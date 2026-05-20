"""Paper-track public-surface hygiene reports."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from relaytic.core.json_utils import write_json


PAPER_SURFACE_HYGIENE_SCHEMA_VERSION = "relaytic.paper_surface_hygiene.v1"
PAPER_SURFACE_HYGIENE_REPORT_DIR = Path("docs") / "reports"
PAPER_SURFACE_HYGIENE_FILENAMES = {
    "paper_public_surface_hygiene_report": "paper_public_surface_hygiene_report.json",
    "legacy_compatibility_retention_report": "legacy_compatibility_retention_report.json",
    "paper_repo_cleanup_scorecard": "paper_repo_cleanup_scorecard.json",
}

PUBLIC_SURFACE_FILES = (
    "README.md",
    "docs/why_relaytic_aml.md",
    "docs/product_story.md",
    "docs/paper_benchmark_runbook.md",
    "docs/handbooks/relaytic_user_handbook.md",
    "docs/handbooks/relaytic_agent_handbook.md",
    "docs/handbooks/relaytic_demo_walkthrough.md",
    ".agents/skills/relaytic/SKILL.md",
)

AGENT_PROMPT_FILES = (
    "src/relaytic/agents/prompts/modeler_system.txt",
)

PUBLIC_STALE_TERMS = (
    "corr2surrogate",
    "Corr2Surrogate",
    "toy demo",
    "prototype",
)

COMPATIBILITY_FILES = (
    "src/corr2surrogate/__init__.py",
    "src/corr2surrogate/ui/__init__.py",
    "src/corr2surrogate/ui/cli.py",
    "src/corr2surrogate/security/__init__.py",
    "src/corr2surrogate/security/git_guard.py",
)

API_ALIAS_CHECKS = (
    {
        "alias": "train_model_candidates",
        "legacy_name": "train_surrogate_candidates",
        "module": "src/relaytic/modeling/training.py",
        "export_module": "src/relaytic/modeling/__init__.py",
        "surface": "modeling_python_api",
    },
    {
        "alias": "rank_candidate_targets",
        "legacy_name": "rank_surrogate_candidates",
        "module": "src/relaytic/analytics/ranking.py",
        "export_module": "src/relaytic/analytics/__init__.py",
        "surface": "analytics_python_api",
    },
    {
        "alias": "train_model_candidates",
        "legacy_name": "train_surrogate_candidates",
        "module": "src/relaytic/orchestration/default_tools.py",
        "export_module": "src/relaytic/orchestration/default_tools.py",
        "surface": "agent_tool_registry",
    },
    {
        "alias": "train_incremental_linear_model",
        "legacy_name": "train_incremental_linear_surrogate",
        "module": "src/relaytic/orchestration/default_tools.py",
        "export_module": "src/relaytic/orchestration/default_tools.py",
        "surface": "agent_tool_registry",
    },
    {
        "alias": "resume_incremental_linear_model",
        "legacy_name": "resume_incremental_linear_surrogate",
        "module": "src/relaytic/orchestration/default_tools.py",
        "export_module": "src/relaytic/orchestration/default_tools.py",
        "surface": "agent_tool_registry",
    },
)


def build_paper_surface_hygiene_reports(project_root: str | Path) -> dict[str, dict[str, Any]]:
    root = Path(project_root)
    public_surface = _build_public_surface_hygiene_report(root)
    retention = _build_compatibility_retention_report(root)
    scorecard = _build_cleanup_scorecard(public_surface, retention)
    return {
        "paper_public_surface_hygiene_report": public_surface,
        "legacy_compatibility_retention_report": retention,
        "paper_repo_cleanup_scorecard": scorecard,
    }


def sync_paper_surface_hygiene_reports(
    project_root: str | Path,
    *,
    output_dir: str | Path | None = None,
) -> dict[str, Path]:
    root = Path(project_root)
    report_dir = Path(output_dir) if output_dir is not None else root / PAPER_SURFACE_HYGIENE_REPORT_DIR
    report_dir.mkdir(parents=True, exist_ok=True)
    reports = build_paper_surface_hygiene_reports(root)
    written: dict[str, Path] = {}
    for key, payload in reports.items():
        written[key] = write_json(
            report_dir / PAPER_SURFACE_HYGIENE_FILENAMES[key],
            payload,
            indent=2,
            sort_keys=True,
        )
    return written


def _build_public_surface_hygiene_report(root: Path) -> dict[str, Any]:
    doc_findings = _scan_files_for_stale_terms(root, PUBLIC_SURFACE_FILES)
    prompt_findings = _scan_files_for_stale_terms(root, AGENT_PROMPT_FILES)
    cli_text = _read_text(root / "src" / "relaytic" / "ui" / "cli.py")
    cli_old_alias_visible = "incremental_linear_surrogate" in cli_text
    unsupported_sota_findings = _scan_unsupported_sota_language(root, PUBLIC_SURFACE_FILES)
    findings = doc_findings + prompt_findings + unsupported_sota_findings
    if cli_old_alias_visible:
        findings.append(
            {
                "path": "src/relaytic/ui/cli.py",
                "term": "incremental_linear_surrogate",
                "reason": "Legacy model-family alias is visible in CLI model help text.",
            }
        )
    return {
        "schema_version": PAPER_SURFACE_HYGIENE_SCHEMA_VERSION,
        "slice": "Paper Track P1",
        "status": "clean" if not findings else "needs_cleanup",
        "public_surface_files_scanned": list(PUBLIC_SURFACE_FILES),
        "agent_prompt_files_scanned": list(AGENT_PROMPT_FILES),
        "stale_public_surface_language_detected": bool(findings),
        "stale_language_findings": findings,
        "cli_public_help_checks": [
            {
                "surface": "model_family_help",
                "legacy_alias_visible": cli_old_alias_visible,
                "replacement_public_aliases": ["linear_ridge", "ridge", "linear"],
            }
        ],
        "unsupported_sota_language_detected": bool(unsupported_sota_findings),
        "allowed_claim_discipline_language": [
            "SOTA may appear only when explicitly blocking or limiting unsupported claims.",
            "Compatibility terms may appear only in migration, compatibility, history, or generated retention reports.",
        ],
    }


def _build_compatibility_retention_report(root: Path) -> dict[str, Any]:
    retained_files = []
    for rel in COMPATIBILITY_FILES:
        path = root / rel
        retained_files.append(
            {
                "path": rel,
                "exists": path.exists(),
                "retention_reason": "Legacy import forwarding only; new code and docs must target relaytic.",
                "public_expansion_allowed": False,
                "removal_condition": (
                    "Remove after downstream compatibility promises expire and tests no longer need "
                    "legacy import smoke coverage."
                ),
            }
        )
    alias_checks = [_alias_check(root, item) for item in API_ALIAS_CHECKS]
    return {
        "schema_version": PAPER_SURFACE_HYGIENE_SCHEMA_VERSION,
        "slice": "Paper Track P1",
        "status": "compatibility_retained_without_public_expansion",
        "retained_compatibility_files": retained_files,
        "all_compatibility_files_present": all(bool(item["exists"]) for item in retained_files),
        "legacy_import_boundary": "src/corr2surrogate is retained only as a compatibility shim.",
        "new_code_target": "relaytic",
        "legacy_api_aliases": alias_checks,
        "all_required_aliases_present": all(bool(item["alias_present"]) for item in alias_checks),
        "legacy_names_still_accepted": all(bool(item["legacy_name_present"]) for item in alias_checks),
    }


def _build_cleanup_scorecard(
    public_surface: dict[str, Any],
    retention: dict[str, Any],
) -> dict[str, Any]:
    public_clean = not bool(public_surface["stale_public_surface_language_detected"])
    aliases_present = bool(retention["all_required_aliases_present"])
    compatibility_present = bool(retention["all_compatibility_files_present"])
    p2_ready = public_clean and aliases_present and compatibility_present
    return {
        "schema_version": PAPER_SURFACE_HYGIENE_SCHEMA_VERSION,
        "slice": "Paper Track P1",
        "status": "ready_for_paper_track_p2" if p2_ready else "needs_cleanup",
        "scorecard": {
            "public_surface_clean": public_clean,
            "compatibility_boundary_retained": compatibility_present,
            "relaytic_aliases_available_for_legacy_api_names": aliases_present,
            "academy_still_blocked": True,
            "hard_performance_claims_still_blocked": True,
        },
        "next_slice": "Paper Track P2" if p2_ready else "Paper Track P1",
        "blocked_claim_posture": "Hard AML and SOTA performance claims remain blocked until later paper-track gates pass.",
    }


def _scan_files_for_stale_terms(root: Path, rel_paths: tuple[str, ...]) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    for rel in rel_paths:
        path = root / rel
        text = _read_text(path)
        if not text:
            continue
        for term in PUBLIC_STALE_TERMS:
            if term in text:
                findings.append(
                    {
                        "path": rel,
                        "term": term,
                        "reason": "Stale public-surface term appears in a paper-facing surface.",
                    }
                )
    return findings


def _scan_unsupported_sota_language(root: Path, rel_paths: tuple[str, ...]) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    unsupported_patterns = (
        "is sota",
        "is state of the art",
        "state of the art across",
        "beats sota",
        "sota winner",
        "benchmark winner",
    )
    allowed_context_patterns = (
        "blocked",
        "not claiming",
        "without",
        "before",
        "until",
        "guard",
        "claim",
    )
    for rel in rel_paths:
        text = _read_text(root / rel)
        if not text:
            continue
        for line_no, line in enumerate(text.splitlines(), start=1):
            lowered = line.lower()
            if not any(pattern in lowered for pattern in unsupported_patterns):
                continue
            if any(pattern in lowered for pattern in allowed_context_patterns):
                continue
            findings.append(
                {
                    "path": rel,
                    "line": line_no,
                    "term": "unsupported_sota_language",
                    "reason": "SOTA language is not framed as a blocked or guarded claim.",
                }
            )
    return findings


def _alias_check(root: Path, spec: dict[str, str]) -> dict[str, Any]:
    module_text = _read_text(root / spec["module"])
    export_text = _read_text(root / spec["export_module"])
    alias = spec["alias"]
    legacy = spec["legacy_name"]
    return {
        "surface": spec["surface"],
        "alias": alias,
        "legacy_name": legacy,
        "module": spec["module"],
        "export_module": spec["export_module"],
        "alias_present": alias in module_text and alias in export_text,
        "legacy_name_present": legacy in module_text,
        "compatibility_posture": "modern_alias_added_legacy_name_retained",
    }


def _read_text(path: Path) -> str:
    if not path.exists() or not path.is_file():
        return ""
    return path.read_text(encoding="utf-8", errors="ignore")
