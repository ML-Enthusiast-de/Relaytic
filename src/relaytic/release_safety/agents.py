"""Slice 13A release-safety scanning and attestation logic."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
from pathlib import Path
import re
import subprocess
from typing import Any, Iterable

from relaytic.security.git_guard import scan_files_for_leaks

from .models import (
    ARTIFACT_ATTESTATION_SCHEMA_VERSION,
    ARTIFACT_INVENTORY_SCHEMA_VERSION,
    DISTRIBUTION_MANIFEST_SCHEMA_VERSION,
    PACKAGING_REGRESSION_REPORT_SCHEMA_VERSION,
    RELEASE_BUNDLE_REPORT_SCHEMA_VERSION,
    RELEASE_SAFETY_SCAN_SCHEMA_VERSION,
    SENSITIVE_STRING_AUDIT_SCHEMA_VERSION,
    SOURCE_MAP_AUDIT_SCHEMA_VERSION,
    ArtifactAttestationArtifact,
    ArtifactInventoryArtifact,
    DistributionManifestArtifact,
    PackagingRegressionReportArtifact,
    ReleaseBundleReportArtifact,
    ReleaseSafetyBundle,
    ReleaseSafetyControls,
    ReleaseSafetyFinding,
    ReleaseSafetyScanArtifact,
    ReleaseSafetyTrace,
    SensitiveStringAuditArtifact,
    SourceMapAuditArtifact,
)
from .storage import write_release_safety_bundle


DEFAULT_RELEASE_SAFETY_ROOT = Path("artifacts") / "release_safety"
LATEST_RELEASE_SAFETY_STATE_DIR = DEFAULT_RELEASE_SAFETY_ROOT / "latest"
_SOURCE_MAPPING_PATTERN = re.compile(r"sourceMappingURL=", re.IGNORECASE)
_INTERNAL_URL_PATTERN = re.compile(
    r"https?://(?:localhost|127\.0\.0\.1|\[::1\]|10\.\d+\.\d+\.\d+|192\.168\.\d+\.\d+|172\.(?:1[6-9]|2\d|3[01])\.\d+\.\d+)(?::\d+)?",
    re.IGNORECASE,
)
_DISALLOWED_BUNDLE_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("roadmap_internal", re.compile(r"(^|/)(RELAYTIC_(VISION_MASTER|BUILD_MASTER|SLICING_PLAN)\.md|IMPLEMENTATION_STATUS\.md|MIGRATION_MAP\.md|AGENTS\.md)$", re.IGNORECASE)),
    ("slice_plan_internal", re.compile(r"(^|/)docs/build_slices/phase_[^/]+\.md$", re.IGNORECASE)),
    ("product_spec_internal", re.compile(r"(^|/)docs/specs/[^/]+\.md$", re.IGNORECASE)),
    ("debug_manifest", re.compile(r"(^|/)[^/]*(debug|internal_manifest|roadmap|scratch)[^/]*$", re.IGNORECASE)),
)
_TEXT_SCAN_IGNORE_SUFFIXES = {
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".pdf",
    ".zip",
    ".gz",
    ".pkl",
    ".pt",
    ".pth",
    ".parquet",
    ".feather",
    ".npy",
    ".npz",
}
_SKIP_DIR_NAMES = {".git", ".venv", "__pycache__", ".pytest_cache", ".mypy_cache"}


@dataclass(frozen=True)
class ReleaseSafetyRunResult:
    bundle: ReleaseSafetyBundle
    review_markdown: str
    state_dir: Path


def default_release_safety_state_dir(*, target_path: str | Path | None = None) -> Path:
    if target_path is None:
        return DEFAULT_RELEASE_SAFETY_ROOT / "workspace"
    target = Path(target_path)
    base = target.name or "bundle"
    safe = "".join(ch if ch.isalnum() or ch in {"-", "_"} else "_" for ch in base).strip("_") or "bundle"
    return DEFAULT_RELEASE_SAFETY_ROOT / safe


def latest_release_safety_state_dir() -> Path:
    return LATEST_RELEASE_SAFETY_STATE_DIR


def build_release_safety_controls_from_policy(policy: dict[str, Any]) -> ReleaseSafetyControls:
    block = dict(policy.get("release_safety", {}))
    return ReleaseSafetyControls(
        oversized_file_threshold_bytes=max(
            1_000_000,
            int(block.get("oversized_file_threshold_bytes", 5_000_000) or 5_000_000),
        ),
        preview_finding_limit=max(5, int(block.get("preview_finding_limit", 20) or 20)),
        scan_hidden_internal_urls=bool(block.get("scan_hidden_internal_urls", True)),
        scan_source_mapping_comments=bool(block.get("scan_source_mapping_comments", True)),
        workspace_mode_tracks_attestation_only=bool(block.get("workspace_mode_tracks_attestation_only", True)),
    )


def run_release_safety_scan(
    *,
    target_path: str | Path | None,
    state_dir: str | Path | None = None,
    explicit_paths: Iterable[str | Path] | None = None,
    tracked_only: bool = False,
    policy: dict[str, Any] | None = None,
) -> ReleaseSafetyRunResult:
    controls = build_release_safety_controls_from_policy(policy or {})
    mode = "workspace_only" if target_path is None else "distribution_bundle"
    scan_root = Path(target_path).expanduser() if target_path is not None else None
    resolved_state_dir = Path(state_dir) if state_dir is not None else default_release_safety_state_dir(target_path=scan_root)
    scan_paths = _resolve_scan_paths(target_path=scan_root, explicit_paths=explicit_paths, tracked_only=tracked_only)
    inventory_entries = [_inventory_entry(path=path, root=scan_root) for path in scan_paths]
    total_bytes = sum(int(entry["size_bytes"]) for entry in inventory_entries)
    extension_counts = _count_extensions(scan_paths)
    host_bundle_paths = [entry["relative_path"] for entry in inventory_entries if entry["category"] == "host_bundle"]
    docs_paths = [entry["relative_path"] for entry in inventory_entries if entry["category"] == "docs"]

    sensitive_findings = _collect_sensitive_findings(
        scan_paths,
        root=scan_root,
        controls=controls,
        mode=mode,
    )
    source_map_findings = _collect_source_map_findings(scan_paths, root=scan_root, controls=controls)
    packaging_findings = _collect_packaging_findings(
        scan_paths,
        root=scan_root,
        controls=controls,
        mode=mode,
    )
    all_findings = [*sensitive_findings, *source_map_findings, *packaging_findings]

    safe_to_ship = mode == "distribution_bundle" and not all_findings
    if mode == "workspace_only" and not all_findings:
        status = "workspace_only"
        ship_readiness = "pre_release_only"
    elif all_findings:
        status = "error"
        ship_readiness = "blocked"
    else:
        status = "ok"
        ship_readiness = "safe_to_ship"

    checks_run = _checks_run(
        sensitive_findings=sensitive_findings,
        source_map_findings=source_map_findings,
        packaging_findings=packaging_findings,
        host_bundle_count=len(host_bundle_paths),
        docs_count=len(docs_paths),
    )
    trace = ReleaseSafetyTrace(
        agent="release_safety_controller",
        scan_mode=mode,
        target_label=str(scan_root) if scan_root is not None else "workspace_tracked_files",
        advisory_notes=[
            "Release safety stays local-first and never uploads scanned bundle contents.",
            "Workspace-only scans are pre-release checks rather than clean bundle attestations.",
        ],
    )
    findings_by_rule = _count_findings_by_rule(all_findings)
    summary = _release_summary(
        status=status,
        mode=mode,
        target_path=scan_root,
        finding_count=len(all_findings),
        file_count=len(scan_paths),
    )
    preview = [finding.to_dict() for finding in all_findings[: controls.preview_finding_limit]]

    bundle = ReleaseSafetyBundle(
        release_safety_scan=ReleaseSafetyScanArtifact(
            schema_version=RELEASE_SAFETY_SCAN_SCHEMA_VERSION,
            generated_at=_utc_now(),
            controls=controls,
            status=status,
            target_path=str(scan_root) if scan_root is not None else None,
            state_dir=str(resolved_state_dir),
            scan_mode=mode,
            ship_readiness=ship_readiness,
            safe_to_ship=safe_to_ship,
            scanned_file_count=len(scan_paths),
            finding_count=len(all_findings),
            failed_check_count=sum(1 for check in checks_run if not bool(check["passed"])),
            findings_by_rule=findings_by_rule,
            host_bundle_count=len(host_bundle_paths),
            docs_file_count=len(docs_paths),
            summary=summary,
            recommendation=_release_recommendation(status=status, mode=mode),
            trace=trace,
        ),
        distribution_manifest=DistributionManifestArtifact(
            schema_version=DISTRIBUTION_MANIFEST_SCHEMA_VERSION,
            generated_at=_utc_now(),
            status="ok",
            scan_mode=mode,
            target_path=str(scan_root) if scan_root is not None else None,
            included_roots=[str(scan_root)] if scan_root is not None else ["git_tracked_workspace"],
            workspace_only=mode == "workspace_only",
            host_bundle_paths=host_bundle_paths,
            docs_paths=docs_paths,
            total_file_count=len(scan_paths),
            total_bytes=total_bytes,
        ),
        artifact_inventory=ArtifactInventoryArtifact(
            schema_version=ARTIFACT_INVENTORY_SCHEMA_VERSION,
            generated_at=_utc_now(),
            status="ok",
            total_file_count=len(scan_paths),
            total_bytes=total_bytes,
            host_bundle_count=len(host_bundle_paths),
            docs_file_count=len(docs_paths),
            extension_counts=extension_counts,
            files=inventory_entries,
        ),
        artifact_attestation=ArtifactAttestationArtifact(
            schema_version=ARTIFACT_ATTESTATION_SCHEMA_VERSION,
            generated_at=_utc_now(),
            status=status,
            scan_mode=mode,
            target_path=str(scan_root) if scan_root is not None else None,
            workspace_only=mode == "workspace_only",
            safe_to_ship=safe_to_ship,
            checks_run=checks_run,
            failed_checks=[check["check_id"] for check in checks_run if not bool(check["passed"])],
            scanned_file_count=len(scan_paths),
            manifest_file_count=len(scan_paths),
            attested_paths_preview=[entry["relative_path"] for entry in inventory_entries[: controls.preview_finding_limit]],
        ),
        source_map_audit=SourceMapAuditArtifact(
            schema_version=SOURCE_MAP_AUDIT_SCHEMA_VERSION,
            generated_at=_utc_now(),
            status="error" if source_map_findings else "ok",
            finding_count=len(source_map_findings),
            findings=[finding.to_dict() for finding in source_map_findings],
        ),
        sensitive_string_audit=SensitiveStringAuditArtifact(
            schema_version=SENSITIVE_STRING_AUDIT_SCHEMA_VERSION,
            generated_at=_utc_now(),
            status="error" if sensitive_findings else "ok",
            finding_count=len(sensitive_findings),
            findings=[finding.to_dict() for finding in sensitive_findings],
        ),
        release_bundle_report=ReleaseBundleReportArtifact(
            schema_version=RELEASE_BUNDLE_REPORT_SCHEMA_VERSION,
            generated_at=_utc_now(),
            status=status,
            ship_readiness=ship_readiness,
            safe_to_ship=safe_to_ship,
            findings_preview=preview,
            required_actions=_required_actions(status=status, mode=mode, findings=all_findings),
            summary=summary,
        ),
        packaging_regression_report=PackagingRegressionReportArtifact(
            schema_version=PACKAGING_REGRESSION_REPORT_SCHEMA_VERSION,
            generated_at=_utc_now(),
            status="error" if packaging_findings else "ok",
            finding_count=len(packaging_findings),
            oversized_payload_count=sum(1 for finding in packaging_findings if finding.rule_id == "oversized_payload"),
            disallowed_internal_count=sum(1 for finding in packaging_findings if finding.rule_id != "oversized_payload"),
            findings=[finding.to_dict() for finding in packaging_findings],
        ),
    )

    write_release_safety_bundle(resolved_state_dir, bundle=bundle)
    if resolved_state_dir.resolve(strict=False) != LATEST_RELEASE_SAFETY_STATE_DIR.resolve(strict=False):
        write_release_safety_bundle(LATEST_RELEASE_SAFETY_STATE_DIR, bundle=bundle)
    return ReleaseSafetyRunResult(
        bundle=bundle,
        review_markdown=render_release_safety_markdown(bundle.to_dict()),
        state_dir=resolved_state_dir,
    )


def render_release_safety_markdown(bundle: ReleaseSafetyBundle | dict[str, Any]) -> str:
    payload = bundle.to_dict() if isinstance(bundle, ReleaseSafetyBundle) else dict(bundle)
    scan = dict(payload.get("release_safety_scan", {}))
    report = dict(payload.get("release_bundle_report", {}))
    inventory = dict(payload.get("artifact_inventory", {}))
    attestation = dict(payload.get("artifact_attestation", {}))
    lines = [
        "# Relaytic Release Safety",
        "",
        f"- Status: `{scan.get('status', 'unknown')}`",
        f"- Ship readiness: `{scan.get('ship_readiness', 'unknown')}`",
        f"- Scan mode: `{scan.get('scan_mode', 'unknown')}`",
        f"- Target: `{scan.get('target_path') or 'git_tracked_workspace'}`",
        f"- State directory: `{scan.get('state_dir', '')}`",
        f"- Scanned files: `{scan.get('scanned_file_count', 0)}`",
        f"- Findings: `{scan.get('finding_count', 0)}`",
        f"- Host bundle files scanned: `{scan.get('host_bundle_count', 0)}`",
        f"- Docs files scanned: `{scan.get('docs_file_count', 0)}`",
        "",
        "## Summary",
        report.get("summary", "No summary available."),
        "",
        "## Required Actions",
    ]
    required_actions = list(report.get("required_actions", []))
    if required_actions:
        lines.extend(f"- {item}" for item in required_actions)
    else:
        lines.append("- No blocking actions recorded.")
    lines.extend(
        [
            "",
            "## Attestation",
            f"- Safe to ship: `{attestation.get('safe_to_ship')}`",
            f"- Failed checks: `{len(list(attestation.get('failed_checks', [])))}`",
            f"- Inventory bytes: `{inventory.get('total_bytes', 0)}`",
        ]
    )
    findings_preview = list(report.get("findings_preview", []))
    if findings_preview:
        lines.extend(["", "## Findings Preview"])
        for item in findings_preview[:10]:
            lines.append(
                f"- `{item.get('path', 'unknown')}` [{item.get('rule_id', 'unknown')}] {item.get('reason', 'Finding detected.')}"
            )
    return "\n".join(lines).strip() + "\n"


def _resolve_scan_paths(
    *,
    target_path: Path | None,
    explicit_paths: Iterable[str | Path] | None,
    tracked_only: bool,
) -> list[Path]:
    if explicit_paths:
        return _expand_paths(explicit_paths)
    if target_path is not None:
        return _expand_paths([target_path])
    if tracked_only or target_path is None:
        return _tracked_files()
    return []


def _expand_paths(paths: Iterable[str | Path]) -> list[Path]:
    expanded: list[Path] = []
    for raw in paths:
        path = Path(raw)
        if path.is_dir():
            for child in path.rglob("*"):
                if child.is_file() and not _skip_path(child):
                    expanded.append(child)
        elif path.is_file():
            expanded.append(path)
    deduped: dict[str, Path] = {}
    for path in expanded:
        deduped[str(path.resolve(strict=False))] = path
    return sorted(deduped.values(), key=lambda item: str(item).lower())


def _tracked_files() -> list[Path]:
    completed = subprocess.run(["git", "ls-files"], capture_output=True, text=True, check=False)
    if completed.returncode != 0:
        raise RuntimeError(f"git ls-files failed with code {completed.returncode}: {completed.stderr.strip()}")
    files = [Path(line.strip()) for line in completed.stdout.splitlines() if line.strip()]
    return [path for path in files if path.is_file() and not _skip_path(path)]


def _skip_path(path: Path) -> bool:
    return any(part in _SKIP_DIR_NAMES for part in path.parts)


def _inventory_entry(*, path: Path, root: Path | None) -> dict[str, Any]:
    return {
        "path": str(path),
        "relative_path": _relative_path(path, root=root),
        "size_bytes": path.stat().st_size,
        "sha256": _sha256(path),
        "extension": path.suffix.lower(),
        "category": _categorize_path(path, root=root),
        "text_scanned": path.suffix.lower() not in _TEXT_SCAN_IGNORE_SUFFIXES,
    }


def _collect_sensitive_findings(
    scan_paths: list[Path],
    *,
    root: Path | None,
    controls: ReleaseSafetyControls,
    mode: str,
) -> list[ReleaseSafetyFinding]:
    findings: list[ReleaseSafetyFinding] = []
    for finding in scan_files_for_leaks(scan_paths):
        findings.append(
            ReleaseSafetyFinding(
                path=_relative_path(Path(finding.path), root=root),
                rule_id=finding.pattern_name,
                severity="high",
                reason="Potential secret or machine-specific path detected in release-scanned content.",
                line_number=finding.line_number,
                excerpt=finding.excerpt,
            )
        )
    if controls.scan_hidden_internal_urls and mode == "distribution_bundle":
        for path in scan_paths:
            text = _safe_read_text(path)
            if text is None:
                continue
            for line_number, line in enumerate(text.splitlines(), start=1):
                if _INTERNAL_URL_PATTERN.search(line):
                    findings.append(
                        ReleaseSafetyFinding(
                            path=_relative_path(path, root=root),
                            rule_id="internal_url",
                            severity="high",
                            reason="Hidden local or internal URL detected in a release-scanned file.",
                            line_number=line_number,
                            excerpt=line[:220],
                        )
                    )
    return findings


def _collect_source_map_findings(
    scan_paths: list[Path],
    *,
    root: Path | None,
    controls: ReleaseSafetyControls,
) -> list[ReleaseSafetyFinding]:
    findings: list[ReleaseSafetyFinding] = []
    for path in scan_paths:
        relative = _relative_path(path, root=root)
        if path.suffix.lower() == ".map":
            findings.append(
                ReleaseSafetyFinding(
                    path=relative,
                    rule_id="source_map_file",
                    severity="high",
                    reason="Source map files should not ship in a Relaytic release bundle.",
                )
            )
            continue
        if not controls.scan_source_mapping_comments:
            continue
        text = _safe_read_text(path)
        if text is None:
            continue
        for line_number, line in enumerate(text.splitlines(), start=1):
            if _SOURCE_MAPPING_PATTERN.search(line):
                findings.append(
                    ReleaseSafetyFinding(
                        path=relative,
                        rule_id="source_mapping_comment",
                        severity="high",
                        reason="A sourceMappingURL comment points to shipping source maps or debug references.",
                        line_number=line_number,
                        excerpt=line[:220],
                    )
                )
    return findings


def _collect_packaging_findings(
    scan_paths: list[Path],
    *,
    root: Path | None,
    controls: ReleaseSafetyControls,
    mode: str,
) -> list[ReleaseSafetyFinding]:
    if mode != "distribution_bundle":
        return []
    findings: list[ReleaseSafetyFinding] = []
    for path in scan_paths:
        relative = _relative_path(path, root=root)
        if path.stat().st_size > controls.oversized_file_threshold_bytes:
            findings.append(
                ReleaseSafetyFinding(
                    path=relative,
                    rule_id="oversized_payload",
                    severity="medium",
                    reason=f"File exceeds the release-safety size threshold of {controls.oversized_file_threshold_bytes} bytes.",
                )
            )
        normalized = relative.replace("\\", "/")
        for rule_id, pattern in _DISALLOWED_BUNDLE_PATTERNS:
            if pattern.search(normalized):
                findings.append(
                    ReleaseSafetyFinding(
                        path=relative,
                        rule_id=rule_id,
                        severity="high",
                        reason="Bundle contains internal planning or debug material that should not ship in a distribution.",
                    )
                )
                break
    return findings


def _checks_run(
    *,
    sensitive_findings: list[ReleaseSafetyFinding],
    source_map_findings: list[ReleaseSafetyFinding],
    packaging_findings: list[ReleaseSafetyFinding],
    host_bundle_count: int,
    docs_count: int,
) -> list[dict[str, Any]]:
    return [
        {"check_id": "sensitive_string_and_machine_path_audit", "passed": not sensitive_findings, "finding_count": len(sensitive_findings)},
        {"check_id": "source_map_audit", "passed": not source_map_findings, "finding_count": len(source_map_findings)},
        {"check_id": "packaging_regression_audit", "passed": not packaging_findings, "finding_count": len(packaging_findings)},
        {
            "check_id": "host_and_docs_inventory",
            "passed": True,
            "finding_count": 0,
            "host_bundle_count": host_bundle_count,
            "docs_count": docs_count,
        },
    ]


def _count_findings_by_rule(findings: list[ReleaseSafetyFinding]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for finding in findings:
        counts[finding.rule_id] = counts.get(finding.rule_id, 0) + 1
    return counts


def _required_actions(*, status: str, mode: str, findings: list[ReleaseSafetyFinding]) -> list[str]:
    if status == "ok":
        return ["Bundle passed the defined release-safety checks and has a machine-readable attestation."]
    if status == "workspace_only":
        return [
            "No blocking leak findings were detected in the workspace scan.",
            "Run the same scan against a built bundle before calling the release safe to ship.",
        ]
    unique_rules: list[str] = []
    seen: set[str] = set()
    for finding in findings:
        if finding.rule_id not in seen:
            unique_rules.append(finding.rule_id)
            seen.add(finding.rule_id)
    actions = [f"Remove or fix findings for `{rule_id}` before shipping." for rule_id in unique_rules[:5]]
    if mode == "distribution_bundle":
        actions.append("Rebuild the distribution and rerun `relaytic release-safety scan` until the bundle is attested cleanly.")
    return actions


def _release_summary(*, status: str, mode: str, target_path: Path | None, finding_count: int, file_count: int) -> str:
    target_label = str(target_path) if target_path is not None else "git-tracked workspace"
    if status == "ok":
        return f"Relaytic scanned {file_count} files in `{target_label}` and attested the bundle as safe to ship."
    if status == "workspace_only":
        return (
            f"Relaytic scanned {file_count} tracked files in `{target_label}` with no blocking findings, "
            "but this remains a workspace-only pre-release check rather than a clean bundle attestation."
        )
    return f"Relaytic scanned {file_count} files in `{target_label}` and found {finding_count} blocking release-safety issue(s)."


def _release_recommendation(*, status: str, mode: str) -> str:
    if status == "ok":
        return "Safe to ship under the current release-safety contract."
    if status == "workspace_only":
        return "Good workspace hygiene, but run the same scan against a built bundle before releasing."
    if mode == "distribution_bundle":
        return "Do not ship this bundle until the blocking findings are removed and the attestation passes."
    return "Fix the workspace findings before packaging a release bundle."


def _relative_path(path: Path, *, root: Path | None) -> str:
    if root is not None:
        try:
            return str(path.relative_to(root)).replace("\\", "/")
        except ValueError:
            pass
    try:
        return str(path.relative_to(Path.cwd())).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")


def _categorize_path(path: Path, *, root: Path | None) -> str:
    relative = _relative_path(path, root=root).replace("\\", "/")
    if relative.startswith(".claude/") or relative.startswith(".agents/") or relative.startswith("skills/") or relative.startswith("openclaw/"):
        return "host_bundle"
    if relative.startswith("docs/") or path.suffix.lower() == ".md":
        return "docs"
    if path.suffix.lower() == ".map":
        return "source_map"
    return "bundle_file"


def _count_extensions(paths: list[Path]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for path in paths:
        key = path.suffix.lower() or "<no_suffix>"
        counts[key] = counts.get(key, 0) + 1
    return counts


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1_048_576), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _safe_read_text(path: Path) -> str | None:
    if path.suffix.lower() in _TEXT_SCAN_IGNORE_SUFFIXES:
        return None
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        try:
            return path.read_text(encoding="latin-1")
        except UnicodeDecodeError:
            return None
    except OSError:
        return None


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()
