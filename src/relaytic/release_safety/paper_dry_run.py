"""Paper Track P12 external dry-run and clean-clone proof artifacts."""

from __future__ import annotations

import importlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from typing import Any
import venv

from relaytic.core.json_utils import write_json

from .paper_draft import (
    PAPER_DRAFT_DOC_DIR,
    PAPER_DRAFT_DOC_FILENAME,
    PAPER_DRAFT_FILENAMES,
    PAPER_DRAFT_FIGURE_DIRNAME,
    PAPER_FIGURE_FILENAMES,
    PAPER_FIGURE_MANIFEST_FILENAME,
    build_paper_draft_pack,
)
from .paper_table_generator import PAPER_TABLE_FILENAMES, build_paper_table_pack


PAPER_DRY_RUN_SCHEMA_VERSION = "relaytic.paper_dry_run.v1"
PAPER_DRY_RUN_REPORT_DIR = Path("docs") / "reports"
PAPER_CLEAN_CLONE_CHECKLIST_FILENAME = "paper_clean_clone_checklist.md"
PAPER_DRY_RUN_FILENAMES = {
    "paper_clean_clone_checklist": PAPER_CLEAN_CLONE_CHECKLIST_FILENAME,
    "paper_external_dry_run_report": "paper_external_dry_run_report.json",
    "paper_clean_clone_install_report": "paper_clean_clone_install_report.json",
    "paper_reproduction_failure_report": "paper_reproduction_failure_report.json",
    "paper_release_go_no_go": "paper_release_go_no_go.json",
}

PAPER_SMOKE_COMMANDS = [
    "python -m relaytic.ui.cli release-safety paper-tables --format json",
    "python -m relaytic.ui.cli release-safety paper-draft --format json",
    "python -m relaytic.ui.cli release-safety paper-dry-run --run-isolated-install --format json",
    "python -m relaytic.ui.cli scan-git-safety",
]

FULL_BENCHMARK_COMMANDS_NOT_REPRODUCED_BY_P12_SMOKE = [
    "python -m relaytic.ui.cli release-safety paysim-benchmark --format json",
    "python -m relaytic.ui.cli release-safety elliptic-graph --format json",
    "python -m relaytic.ui.cli release-safety tabular-baselines --budget-tier baseline --run-optional --format json",
    "python -m relaytic.ui.cli release-safety paysim-competitive --budget-tier competitive --run-optional --format json",
    "python -m relaytic.ui.cli release-safety graph-baselines --budget-tier competitive --run-optional --format json",
    "python -m relaytic.ui.cli release-safety elliptic2-recovery --core-data-dir <external-local-core-dir> --revtrack-dir <external-local-revtrack-dir> --prepare-selected-embeddings --run-pilot --hash-large-assets --format json",
    "python -m relaytic.ui.cli release-safety elliptic2-competitive --revtrack-dir <external-local-revtrack-dir> --budget-tier competitive --run-suite --format json",
    "python -m relaytic.ui.cli release-safety elliptic2-reference-parity --revtrack-dir <external-local-revtrack-dir> --run-neural --format json",
]


def build_paper_dry_run_pack(
    project_root: str | Path,
    *,
    run_live_checks: bool = True,
    run_isolated_install: bool = False,
) -> dict[str, Any]:
    """Build P12 dry-run reports from the current repository checkout."""
    root = Path(project_root)
    install_report = _build_install_report(root, run_isolated_install=run_isolated_install)
    smoke_report = _build_smoke_report(root)
    leak_scan = _run_leak_scan(root, run_live_checks=run_live_checks)
    claim_lint = _read_json(root / PAPER_DRY_RUN_REPORT_DIR / "paper_claim_lint_report.json")
    publishability = _read_json(root / PAPER_DRY_RUN_REPORT_DIR / "paper_publishability_matrix.json")

    dry_run_checks = [
        _check(
            "clean_clone_install_contract_ready",
            install_report.get("status") == "pass_clean_clone_ready",
            "Clean-clone install contract must be documented and importable from the current checkout.",
            source_artifact="docs/reports/paper_clean_clone_install_report.json",
            repair_action="Fix pyproject/package/CLI entrypoint drift and rerun P12.",
        ),
        _check(
            "paper_smoke_tables_regenerated",
            bool(smoke_report.get("paper_table_smoke", {}).get("passed")),
            "P10 table generation must reproduce the expected metric-cell posture.",
            source_artifact="docs/reports/paper_external_dry_run_report.json",
            repair_action="Run `python -m relaytic.ui.cli release-safety paper-tables --format json` and repair table provenance.",
        ),
        _check(
            "paper_smoke_draft_regenerated",
            bool(smoke_report.get("paper_draft_smoke", {}).get("passed")),
            "P11 draft generation must reproduce a passing claim lint and figure manifest.",
            source_artifact="docs/reports/paper_external_dry_run_report.json",
            repair_action="Run `python -m relaytic.ui.cli release-safety paper-draft --format json` and repair draft or lint failures.",
        ),
        _check(
            "live_or_declared_leak_scan_passed",
            bool(leak_scan.get("passed")),
            "P12 requires a live leak scan unless this is an explicitly skipped unit/smoke run.",
            source_artifact="artifacts/release_safety/paper_p12/release_safety_scan.json",
            repair_action="Run `python -m relaytic.ui.cli scan-git-safety` and fix any findings before P13.",
        ),
        _check(
            "committed_claim_lint_passed",
            claim_lint.get("status") == "pass" and bool(claim_lint.get("paper_can_continue_to_p12")),
            "Committed P11 claim lint must pass before release can continue.",
            source_artifact="docs/reports/paper_claim_lint_report.json",
            repair_action="Regenerate the draft and remove unsupported public claims.",
        ),
    ]

    external_report = _build_external_dry_run_report(
        install_report=install_report,
        smoke_report=smoke_report,
        leak_scan=leak_scan,
        claim_lint=claim_lint,
        checks=dry_run_checks,
    )
    failure_report = _build_failure_report(dry_run_checks)
    go_no_go = _build_go_no_go_report(
        external_report=external_report,
        failure_report=failure_report,
        claim_lint=claim_lint,
        publishability=publishability,
    )
    checklist = _render_clean_clone_checklist(go_no_go=go_no_go)
    return {
        "paper_clean_clone_checklist": checklist,
        "paper_external_dry_run_report": external_report,
        "paper_clean_clone_install_report": install_report,
        "paper_reproduction_failure_report": failure_report,
        "paper_release_go_no_go": go_no_go,
    }


def sync_paper_dry_run_pack(
    project_root: str | Path,
    *,
    output_dir: str | Path | None = None,
    run_live_checks: bool = True,
    run_isolated_install: bool = False,
) -> dict[str, Path]:
    """Write the P12 dry-run reports to docs/reports by default."""
    root = Path(project_root)
    report_dir = Path(output_dir) if output_dir is not None else root / PAPER_DRY_RUN_REPORT_DIR
    report_dir.mkdir(parents=True, exist_ok=True)
    pack = build_paper_dry_run_pack(
        root,
        run_live_checks=run_live_checks,
        run_isolated_install=run_isolated_install,
    )
    written: dict[str, Path] = {}
    for key, filename in PAPER_DRY_RUN_FILENAMES.items():
        path = report_dir / filename
        if filename.endswith(".md"):
            path.write_text(str(pack[key]), encoding="utf-8")
            written[key] = path
        else:
            written[key] = write_json(path, pack[key], indent=2, sort_keys=True)
    return written


def render_paper_dry_run_markdown(pack: dict[str, Any]) -> str:
    report = dict(pack.get("paper_external_dry_run_report", {}))
    install = dict(pack.get("paper_clean_clone_install_report", {}))
    failures = dict(pack.get("paper_reproduction_failure_report", {}))
    go_no_go = dict(pack.get("paper_release_go_no_go", {}))
    return "\n".join(
        [
            "# Paper P12 External Dry Run",
            "",
            f"- Dry-run status: `{report.get('status') or 'unknown'}`",
            f"- Install contract: `{install.get('status') or 'unknown'}`",
            f"- Unresolved failures: `{failures.get('unresolved_failure_count', 'unknown')}`",
            f"- P13 allowed: `{go_no_go.get('paper_can_continue_to_p13')}`",
            f"- Release decision: `{go_no_go.get('release_decision') or 'unknown'}`",
            f"- Live leak scan: `{report.get('leak_scan', {}).get('status') or 'unknown'}`",
        ]
    ).rstrip() + "\n"


def _build_install_report(root: Path, *, run_isolated_install: bool) -> dict[str, Any]:
    pyproject = root / "pyproject.toml"
    pyproject_text = _safe_read_text(pyproject)
    import_check = _current_import_check()
    isolated_probe = (
        _run_isolated_clean_clone_probe(root)
        if run_isolated_install
        else {
            "executed": False,
            "status": "not_run",
            "reason": "run_isolated_install_false",
            "operator_command": "python -m relaytic.ui.cli release-safety paper-dry-run --run-isolated-install --format json",
        }
    )
    checks = [
        _check(
            "pyproject_present",
            pyproject.is_file(),
            "pyproject.toml must exist in a clean clone.",
            source_artifact="pyproject.toml",
            repair_action="Restore pyproject.toml before release.",
        ),
        _check(
            "relaytic_package_present",
            (root / "src" / "relaytic" / "__init__.py").is_file(),
            "The canonical relaytic package must be present.",
            source_artifact="src/relaytic/__init__.py",
            repair_action="Restore the canonical package boundary.",
        ),
        _check(
            "console_script_declared",
            'relaytic = "relaytic.ui.cli:main"' in pyproject_text,
            "The public relaytic CLI entry point must be declared.",
            source_artifact="pyproject.toml",
            repair_action="Restore the relaytic console script in pyproject.toml.",
        ),
        _check(
            "full_install_profile_declared",
            "[project.optional-dependencies]" in pyproject_text and "full = [" in pyproject_text,
            "The documented full install profile must be declared.",
            source_artifact="pyproject.toml",
            repair_action="Restore the `full` optional-dependency profile.",
        ),
        _check(
            "current_checkout_importable",
            bool(import_check.get("passed")),
            "The current checkout must import the CLI and release-safety package.",
            source_artifact="src/relaytic/ui/cli.py",
            repair_action="Fix import errors before asking reviewers to install the package.",
            detail=import_check,
        ),
    ]
    checks.append(
        _check(
            "isolated_clean_clone_full_profile_install",
            isolated_probe.get("status") == "pass",
            "The temp clean-clone probe must install the full profile and rerun the paper-smoke commands.",
            source_artifact="docs/reports/paper_clean_clone_install_report.json",
            repair_action="Run `python -m relaytic.ui.cli release-safety paper-dry-run --run-isolated-install --format json`, inspect the isolated probe command statuses, fix install or smoke failures, and rerun P12.",
            detail=isolated_probe,
        )
    )
    status = "pass_clean_clone_ready" if all(check["passed"] for check in checks) else "blocked_install_contract"
    return {
        "schema_version": PAPER_DRY_RUN_SCHEMA_VERSION,
        "slice": "Paper Track P12",
        "status": status,
        "documented_install_profile": "full",
        "install_verification_level": (
            "isolated_clean_clone_full_profile_probe"
            if isolated_probe.get("status") == "pass"
            else "source_contract_plus_current_environment_import_probe"
        ),
        "live_isolated_clean_clone_install_executed": bool(isolated_probe.get("executed")),
        "live_isolated_clean_clone_install_passed": isolated_probe.get("status") == "pass",
        "isolated_clean_clone_probe": isolated_probe,
        "documented_clean_clone_commands": _clean_clone_commands(),
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "checks": checks,
        "clean_clone_install_verified": status == "pass_clean_clone_ready",
        "honesty_note": (
            "P12's committed report proves clean-clone readiness and paper-smoke reproducibility from the current "
            "checkout. External reviewers should still run the checklist in a fresh clone; unresolved failures block P13."
        ),
    }


def _build_smoke_report(root: Path) -> dict[str, Any]:
    required = _required_paper_artifacts(root)
    missing = [item["artifact_ref"] for item in required if not item["exists"]]
    table_smoke = _regenerate_table_smoke(root)
    draft_smoke = _regenerate_draft_smoke(root)
    checks = [
        _check(
            "required_paper_artifacts_present",
            not missing,
            "Committed P10/P11 artifacts must be present for reviewer reproduction.",
            source_artifact="docs/reports",
            repair_action="Regenerate missing paper artifacts before P12.",
            detail={"missing_artifacts": missing},
        ),
        _check(
            "table_pack_regenerated_in_memory",
            bool(table_smoke.get("passed")),
            "P10 table pack must regenerate from committed source artifacts.",
            source_artifact="docs/reports/paper_metric_cell_audit.json",
            repair_action="Repair P10 inputs or table generation.",
            detail=table_smoke,
        ),
        _check(
            "draft_pack_regenerated_in_memory",
            bool(draft_smoke.get("passed")),
            "P11 draft pack must regenerate from committed P10 artifacts.",
            source_artifact="docs/reports/paper_claim_lint_report.json",
            repair_action="Repair P11 draft generation or claim lint.",
            detail=draft_smoke,
        ),
    ]
    return {
        "schema_version": PAPER_DRY_RUN_SCHEMA_VERSION,
        "slice": "Paper Track P12",
        "status": "paper_smoke_reproduced" if all(check["passed"] for check in checks) else "blocked_paper_smoke",
        "paper_smoke_subset": {
            "declared": True,
            "reason": "Full public benchmark reruns are heavier and depend on external-local datasets; P12 reproduces the paper transformation path.",
            "commands": PAPER_SMOKE_COMMANDS,
            "expected_artifacts": [item["artifact_ref"] for item in required],
        },
        "full_benchmark_commands_not_reproduced": FULL_BENCHMARK_COMMANDS_NOT_REPRODUCED_BY_P12_SMOKE,
        "required_artifacts": required,
        "paper_table_smoke": table_smoke,
        "paper_draft_smoke": draft_smoke,
        "checks": checks,
    }


def _build_external_dry_run_report(
    *,
    install_report: dict[str, Any],
    smoke_report: dict[str, Any],
    leak_scan: dict[str, Any],
    claim_lint: dict[str, Any],
    checks: list[dict[str, Any]],
) -> dict[str, Any]:
    failed = [check for check in checks if not check["passed"]]
    status = "pass_paper_smoke_reproduced_claim_linted" if not failed else "blocked_pending_dry_run_repairs"
    return {
        "schema_version": PAPER_DRY_RUN_SCHEMA_VERSION,
        "slice": "Paper Track P12",
        "status": status,
        "paper_can_continue_to_p13": not failed,
        "dry_run_role": "external_reviewer_paper_smoke",
        "install_status": install_report.get("status"),
        "paper_smoke_status": smoke_report.get("status"),
        "claim_lint_status": claim_lint.get("status"),
        "leak_scan": leak_scan,
        "checks": checks,
        "paper_smoke_subset": smoke_report.get("paper_smoke_subset", {}),
        "full_benchmark_commands_not_reproduced": smoke_report.get("full_benchmark_commands_not_reproduced", []),
        "fallback_rule_applied": True,
        "fallback_rule_reason": (
            "P12 does not rerun every heavy benchmark by default. It proves the declared paper-smoke subset and records "
            "the full benchmark commands that remain outside this dry run."
        ),
        "next_slice": "Paper Track P13 - arXiv release and attention pack" if not failed else "Paper Track P12 repair",
    }


def _build_failure_report(checks: list[dict[str, Any]]) -> dict[str, Any]:
    failures = [
        {
            "check_id": check["check_id"],
            "message": check["message"],
            "source_artifact": check.get("source_artifact"),
            "repair_action": check.get("repair_action"),
            "detail": check.get("detail", {}),
        }
        for check in checks
        if not check["passed"]
    ]
    return {
        "schema_version": PAPER_DRY_RUN_SCHEMA_VERSION,
        "slice": "Paper Track P12",
        "status": "no_failures" if not failures else "failures_detected",
        "unresolved_failure_count": len(failures),
        "arxiv_release_blocked": bool(failures),
        "failures": failures,
        "nonblocking_nonreproduced_full_benchmarks": FULL_BENCHMARK_COMMANDS_NOT_REPRODUCED_BY_P12_SMOKE,
        "failure_policy": "Any unresolved P12 failure blocks P13. Heavy full-benchmark reruns are recorded but not required for the P12 smoke pass.",
    }


def _build_go_no_go_report(
    *,
    external_report: dict[str, Any],
    failure_report: dict[str, Any],
    claim_lint: dict[str, Any],
    publishability: dict[str, Any],
) -> dict[str, Any]:
    can_continue = bool(external_report.get("paper_can_continue_to_p13")) and failure_report.get("status") == "no_failures"
    hard_allowed = bool(claim_lint.get("hard_claims_allowed")) or bool(publishability.get("hard_claims_allowed"))
    headline_allowed = bool(claim_lint.get("headline_claims_allowed")) or bool(publishability.get("headline_claims_allowed"))
    return {
        "schema_version": PAPER_DRY_RUN_SCHEMA_VERSION,
        "slice": "Paper Track P12",
        "status": "go_for_p13_claim_safe_release_pack" if can_continue else "blocked_pending_p12_repairs",
        "paper_can_continue_to_p13": can_continue,
        "release_decision": "go_for_p13" if can_continue else "no_go",
        "allowed_release_mode": "claim_safe_evaluation_environment_only" if can_continue else "none_until_repairs_complete",
        "hard_claims_allowed": hard_allowed,
        "headline_claims_allowed": headline_allowed,
        "blocked_public_claims": [
            "hard real-world AML superiority",
            "SOTA or leaderboard-winner claim",
            "RevClassify parity or Elliptic2 performance contribution",
            "graph-neural superiority",
            "hard business-value or analyst-hour savings claim",
        ],
        "required_p13_inputs": [
            "docs/reports/paper_result_table_final.json",
            "docs/reports/paper_metric_cell_audit.json",
            "docs/reports/paper_claim_lint_report.json",
            "docs/reports/paper_external_dry_run_report.json",
            "docs/reports/paper_release_go_no_go.json",
            "docs/paper/relaytic_aml_draft.md",
        ],
        "gate_refs": [
            "docs/reports/paper_publishability_matrix.json",
            "docs/reports/paper_claim_lint_report.json",
            "docs/reports/paper_external_dry_run_report.json",
            "docs/reports/paper_reproduction_failure_report.json",
        ],
        "unresolved_failure_count": failure_report.get("unresolved_failure_count", 0),
        "next_slice": "Paper Track P13 - arXiv release and attention pack" if can_continue else "Paper Track P12 repair",
    }


def _render_clean_clone_checklist(*, go_no_go: dict[str, Any]) -> str:
    lines = [
        "# Paper P12 Clean-Clone Checklist",
        "",
        "Run these commands from a fresh clone before arXiv or public attention release.",
        "",
        "## Install",
        "",
        "```powershell",
        "git clone <repo-url> Relaytic",
        "cd Relaytic",
        "python -m venv .venv",
        ".\\.venv\\Scripts\\python.exe -m pip install --upgrade pip",
        ".\\.venv\\Scripts\\python.exe -m pip install -e \".[full]\"",
        ".\\.venv\\Scripts\\python.exe -m relaytic.ui.cli doctor --expected-profile full --format json",
        "```",
        "",
        "## Paper-Smoke Reproduction",
        "",
        "```powershell",
        ".\\.venv\\Scripts\\python.exe -m relaytic.ui.cli release-safety paper-tables --format json",
        ".\\.venv\\Scripts\\python.exe -m relaytic.ui.cli release-safety paper-draft --format json",
        ".\\.venv\\Scripts\\python.exe -m relaytic.ui.cli release-safety paper-dry-run --run-isolated-install --format json",
        ".\\.venv\\Scripts\\python.exe -m relaytic.ui.cli scan-git-safety",
        "```",
        "",
        "## Pass Criteria",
        "",
        "- `paper_clean_clone_install_report.json` status is `pass_clean_clone_ready`.",
        "- `paper_external_dry_run_report.json` status is `pass_paper_smoke_reproduced_claim_linted`.",
        "- `paper_reproduction_failure_report.json` status is `no_failures`.",
        "- `paper_release_go_no_go.json` has `paper_can_continue_to_p13: true`.",
        "- Public wording remains limited to the claim-safe evaluation-environment story.",
        "",
        "## Heavy Reruns Outside P12 Smoke",
        "",
    ]
    lines.extend(f"- `{command}`" for command in FULL_BENCHMARK_COMMANDS_NOT_REPRODUCED_BY_P12_SMOKE)
    lines.extend(
        [
            "",
            "## Current Go/No-Go",
            "",
            f"- Release decision: `{go_no_go.get('release_decision')}`",
            f"- P13 allowed: `{go_no_go.get('paper_can_continue_to_p13')}`",
            f"- Allowed release mode: `{go_no_go.get('allowed_release_mode')}`",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def _required_paper_artifacts(root: Path) -> list[dict[str, Any]]:
    reports = root / PAPER_DRY_RUN_REPORT_DIR
    paper_dir = root / PAPER_DRAFT_DOC_DIR
    figure_dir = paper_dir / PAPER_DRAFT_FIGURE_DIRNAME
    artifact_refs = [
        *(f"docs/reports/{filename}" for filename in PAPER_TABLE_FILENAMES.values()),
        *(f"docs/reports/{filename}" for filename in PAPER_DRAFT_FILENAMES.values()),
        f"docs/paper/{PAPER_DRAFT_DOC_FILENAME}",
        f"docs/paper/{PAPER_DRAFT_FIGURE_DIRNAME}/{PAPER_FIGURE_MANIFEST_FILENAME}",
        *(f"docs/paper/{PAPER_DRAFT_FIGURE_DIRNAME}/{filename}" for filename in PAPER_FIGURE_FILENAMES.values()),
    ]
    entries = []
    for ref in artifact_refs:
        path = root / Path(ref)
        entries.append(
            {
                "artifact_ref": ref,
                "exists": path.is_file(),
                "required_for": "paper_smoke",
            }
        )
    if not reports.exists() or not figure_dir.exists():
        return entries
    return entries


def _regenerate_table_smoke(root: Path) -> dict[str, Any]:
    committed = _read_json(root / PAPER_DRY_RUN_REPORT_DIR / "paper_metric_cell_audit.json")
    try:
        pack = build_paper_table_pack(root)
    except Exception as exc:
        return {"passed": False, "error": str(exc), "status": "exception"}
    audit = dict(pack.get("paper_metric_cell_audit", {}))
    generated_ids = _cell_ids(audit)
    committed_ids = _cell_ids(committed)
    passed = (
        audit.get("status") == "pass"
        and bool(audit.get("paper_can_continue_to_p11"))
        and bool(generated_ids)
        and generated_ids == committed_ids
    )
    return {
        "passed": passed,
        "status": audit.get("status"),
        "paper_can_continue_to_p11": audit.get("paper_can_continue_to_p11"),
        "generated_numeric_cell_count": len(generated_ids),
        "committed_numeric_cell_count": len(committed_ids),
        "cell_id_sets_match": generated_ids == committed_ids,
        "missing_generated_cell_ids": sorted(committed_ids - generated_ids),
        "unexpected_generated_cell_ids": sorted(generated_ids - committed_ids),
    }


def _regenerate_draft_smoke(root: Path) -> dict[str, Any]:
    try:
        pack = build_paper_draft_pack(root)
    except Exception as exc:
        return {"passed": False, "error": str(exc), "status": "exception"}
    lint = dict(pack.get("paper_claim_lint_report", {}))
    manifest = dict(pack.get("paper_figure_manifest", {}))
    draft = str(pack.get("paper_draft", ""))
    required_sections = ["Abstract", "Introduction", "Related Work", "Method", "Benchmarks", "Results", "Limitations", "Reproducibility Appendix"]
    missing_sections = [section for section in required_sections if f"## {section}" not in draft]
    passed = (
        lint.get("status") == "pass"
        and bool(lint.get("paper_can_continue_to_p12"))
        and not missing_sections
        and len(manifest.get("figures") or []) == len(PAPER_FIGURE_FILENAMES)
    )
    return {
        "passed": passed,
        "status": lint.get("status"),
        "paper_can_continue_to_p12": lint.get("paper_can_continue_to_p12"),
        "figure_count": len(manifest.get("figures") or []),
        "missing_sections": missing_sections,
        "violation_count": len(lint.get("violations") or []),
    }


def _run_leak_scan(root: Path, *, run_live_checks: bool) -> dict[str, Any]:
    if not run_live_checks:
        return {
            "status": "skipped",
            "passed": False,
            "skip_reason": "live_checks_disabled",
            "command": "python -m relaytic.ui.cli scan-git-safety",
        }
    try:
        from .agents import run_release_safety_scan
    except Exception as exc:
        return {"status": "error", "passed": False, "error": str(exc), "command": "python -m relaytic.ui.cli scan-git-safety"}
    state_dir = Path("artifacts") / "release_safety" / "paper_p12"
    previous_cwd = Path.cwd()
    try:
        os.chdir(root)
        result = run_release_safety_scan(
            target_path=None,
            state_dir=state_dir,
            tracked_only=True,
        )
    except Exception as exc:
        return {"status": "error", "passed": False, "error": str(exc), "command": "python -m relaytic.ui.cli scan-git-safety"}
    finally:
        os.chdir(previous_cwd)
    bundle = result.bundle.to_dict()
    scan = dict(bundle.get("release_safety_scan", {}))
    passed = scan.get("status") in {"workspace_only", "ok"} and int(scan.get("finding_count") or 0) == 0
    return {
        "status": scan.get("status"),
        "passed": passed,
        "command": "python -m relaytic.ui.cli scan-git-safety",
        "state_dir_ref": state_dir.as_posix(),
        "scanned_file_count": scan.get("scanned_file_count"),
        "finding_count": scan.get("finding_count"),
        "failed_check_count": scan.get("failed_check_count"),
        "ship_readiness": scan.get("ship_readiness"),
    }


def _run_isolated_clean_clone_probe(root: Path) -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="relaytic_p12_clean_clone_") as raw_temp:
        temp_root = Path(raw_temp)
        clone_root = temp_root / "Relaytic"
        try:
            copied_files = _copy_clean_workspace(root=root, clone_root=clone_root)
        except Exception as exc:
            return {"executed": True, "status": "error", "phase": "copy_workspace", "error": str(exc)}
        venv_dir = clone_root / ".venv"
        try:
            venv.EnvBuilder(with_pip=True).create(venv_dir)
        except Exception as exc:
            return {
                "executed": True,
                "status": "error",
                "phase": "create_venv",
                "error": _redact_probe_text(str(exc), clone_root=clone_root, temp_root=temp_root),
                "workspace_file_count": len(copied_files),
            }
        venv_python = _venv_python(venv_dir)
        command_specs = [
            ("git_init", ["git", "init"]),
            ("git_add", ["git", "add", "-A"]),
            ("install_full_profile", [str(venv_python), "-m", "pip", "install", "-e", ".[full]"]),
            ("doctor_full_profile", [str(venv_python), "-m", "relaytic.ui.cli", "doctor", "--expected-profile", "full", "--format", "json"]),
            ("paper_tables", [str(venv_python), "-m", "relaytic.ui.cli", "release-safety", "paper-tables", "--format", "json"]),
            ("paper_draft", [str(venv_python), "-m", "relaytic.ui.cli", "release-safety", "paper-draft", "--format", "json"]),
            ("scan_git_safety", [str(venv_python), "-m", "relaytic.ui.cli", "scan-git-safety"]),
        ]
        commands = [
            _run_probe_command(step_id=step_id, command=command, cwd=clone_root, temp_root=temp_root)
            for step_id, command in command_specs
        ]
        passed = all(command["passed"] for command in commands)
        return {
            "executed": True,
            "status": "pass" if passed else "fail",
            "workspace_file_count": len(copied_files),
            "install_profile": "full",
            "commands": commands,
        }


def _copy_clean_workspace(*, root: Path, clone_root: Path) -> list[Path]:
    completed = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard"],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(f"git ls-files failed with code {completed.returncode}: {completed.stderr.strip()}")
    clone_root.mkdir(parents=True, exist_ok=True)
    copied: list[Path] = []
    for line in completed.stdout.splitlines():
        rel = Path(line.strip())
        if not line.strip() or _skip_clean_clone_file(rel):
            continue
        source = root / rel
        if not source.is_file():
            continue
        target = clone_root / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        copied.append(rel)
    return copied


def _skip_clean_clone_file(path: Path) -> bool:
    skip_parts = {
        ".git",
        ".venv",
        ".pytest_cache",
        "__pycache__",
        "artifacts",
        "local_notes",
        "htmlcov",
        "data",
        "external_data",
    }
    return any(part in skip_parts for part in path.parts)


def _run_probe_command(
    *,
    step_id: str,
    command: list[str],
    cwd: Path,
    temp_root: Path,
) -> dict[str, Any]:
    try:
        completed = subprocess.run(
            command,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=False,
            timeout=600,
        )
    except subprocess.TimeoutExpired as exc:
        return {
            "step_id": step_id,
            "command": _display_probe_command(command),
            "passed": False,
            "returncode": None,
            "error": "timeout",
            "stderr_tail": _redact_probe_text(str(exc), clone_root=cwd, temp_root=temp_root),
        }
    passed = completed.returncode == 0
    return {
        "step_id": step_id,
        "command": _display_probe_command(command),
        "passed": passed,
        "returncode": completed.returncode,
        "stdout_tail": "" if passed else _tail_for_probe(completed.stdout, clone_root=cwd, temp_root=temp_root),
        "stderr_tail": "" if passed else _tail_for_probe(completed.stderr, clone_root=cwd, temp_root=temp_root),
    }


def _venv_python(venv_dir: Path) -> Path:
    if os.name == "nt":
        return venv_dir / "Scripts" / "python.exe"
    return venv_dir / "bin" / "python"


def _display_probe_command(command: list[str]) -> str:
    display = []
    for part in command:
        if part.endswith("python.exe") or part.endswith("/python"):
            display.append("<venv-python>")
        else:
            display.append(part)
    return " ".join(display)


def _tail_for_probe(text: str, *, clone_root: Path, temp_root: Path) -> str:
    if not text:
        return ""
    lines = text.splitlines()[-12:]
    return _redact_probe_text("\n".join(lines), clone_root=clone_root, temp_root=temp_root)


def _redact_probe_text(text: str, *, clone_root: Path, temp_root: Path) -> str:
    redacted = text.replace(str(clone_root), "<clean-clone>")
    redacted = redacted.replace(str(temp_root), "<temp>")
    redacted = redacted.replace(clone_root.as_posix(), "<clean-clone>")
    redacted = redacted.replace(temp_root.as_posix(), "<temp>")
    return redacted


def _current_import_check() -> dict[str, Any]:
    modules = ["relaytic", "relaytic.ui.cli", "relaytic.release_safety"]
    loaded = []
    for module in modules:
        try:
            importlib.import_module(module)
        except Exception as exc:
            return {"passed": False, "failed_module": module, "error": str(exc), "loaded_modules": loaded}
        loaded.append(module)
    try:
        cli = importlib.import_module("relaytic.ui.cli")
        main = getattr(cli, "main", None)
    except Exception as exc:
        return {"passed": False, "failed_module": "relaytic.ui.cli", "error": str(exc), "loaded_modules": loaded}
    return {"passed": callable(main), "loaded_modules": loaded, "cli_main_callable": callable(main)}


def _clean_clone_commands() -> list[str]:
    return [
        "git clone <repo-url> Relaytic",
        "cd Relaytic",
        "python -m venv .venv",
        "python -m pip install --upgrade pip",
        "python -m pip install -e \".[full]\"",
        "python -m relaytic.ui.cli doctor --expected-profile full --format json",
        *PAPER_SMOKE_COMMANDS,
    ]


def _check(
    check_id: str,
    passed: bool,
    message: str,
    *,
    source_artifact: str,
    repair_action: str,
    detail: dict[str, Any] | None = None,
) -> dict[str, Any]:
    payload = {
        "check_id": check_id,
        "passed": bool(passed),
        "message": message,
        "source_artifact": source_artifact,
        "repair_action": repair_action,
    }
    if detail is not None:
        payload["detail"] = detail
    return payload


def _cell_ids(audit: dict[str, Any]) -> set[str]:
    cells = audit.get("numeric_cells", [])
    return {str(cell.get("cell_id")) for cell in cells if isinstance(cell, dict) and cell.get("cell_id")}


def _safe_read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return ""


def _read_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return dict(payload) if isinstance(payload, dict) else {}
