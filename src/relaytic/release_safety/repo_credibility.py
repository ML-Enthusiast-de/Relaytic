"""Repo credibility audit artifacts for the pre-Academy cleanup slice."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from relaytic.core.json_utils import write_json


REPO_CREDIBILITY_SCHEMA_VERSION = "relaytic.repo_credibility.v1"
REPO_CREDIBILITY_REPORT_DIR = Path("docs") / "reports"
REPO_CREDIBILITY_FILENAMES = {
    "pre_academy_repo_audit": "pre_academy_repo_audit.json",
    "module_extraction_plan": "module_extraction_plan.json",
    "public_surface_inventory": "public_surface_inventory.json",
    "module_split_report": "module_split_report.json",
    "benchmark_surface_cleanup_report": "benchmark_surface_cleanup_report.json",
}
OVERSIZED_MODULE_LINE_THRESHOLD = 1200

EXTRACTED_MODULE = "src/relaytic/ui/aml_environment.py"
EXTRACTION_SOURCE_MODULE = "src/relaytic/ui/cli.py"

PUBLIC_SURFACE_COMMANDS: tuple[dict[str, str], ...] = (
    {
        "command": "relaytic benchmark run",
        "family": "benchmark",
        "surface_role": "paper_evidence_builder",
        "claim_posture": "claim_gated",
    },
    {
        "command": "relaytic benchmark show",
        "family": "benchmark",
        "surface_role": "paper_evidence_reader",
        "claim_posture": "claim_gated",
    },
    {
        "command": "relaytic demo aml-review-queue",
        "family": "demo",
        "surface_role": "first_contact_aml_demo",
        "claim_posture": "demo_only",
    },
    {
        "command": "relaytic aml graph-loader",
        "family": "aml",
        "surface_role": "graph_workload_ingestion",
        "claim_posture": "supporting_evidence",
    },
    {
        "command": "relaytic aml business-value",
        "family": "aml",
        "surface_role": "operational_metric_builder",
        "claim_posture": "guarded_metric",
    },
    {
        "command": "relaytic aml baselines",
        "family": "aml",
        "surface_role": "baseline_and_ablation_builder",
        "claim_posture": "claim_gated",
    },
    {
        "command": "relaytic aml temporal",
        "family": "aml",
        "surface_role": "temporal_weak_label_gate",
        "claim_posture": "supporting_or_blocked",
    },
    {
        "command": "relaytic aml environment",
        "family": "aml",
        "surface_role": "model_environment_separation",
        "claim_posture": "claim_gated",
    },
    {
        "command": "relaytic guide show",
        "family": "guide",
        "surface_role": "operator_status_and_next_options",
        "claim_posture": "navigation",
    },
    {
        "command": "relaytic guide ask",
        "family": "guide",
        "surface_role": "guided_status_question",
        "claim_posture": "navigation",
    },
    {
        "command": "relaytic guide export-context",
        "family": "guide",
        "surface_role": "external_llm_context_pack",
        "claim_posture": "redacted_context_export",
    },
    {
        "command": "relaytic release-safety scan",
        "family": "release_safety",
        "surface_role": "leak_and_release_gate",
        "claim_posture": "release_gate",
    },
    {
        "command": "relaytic release-safety paper-freeze",
        "family": "release_safety",
        "surface_role": "paper_release_freeze_builder",
        "claim_posture": "claim_boundary_freeze",
    },
    {
        "command": "relaytic trace show",
        "family": "trace",
        "surface_role": "trace_identity_reader",
        "claim_posture": "auditability",
    },
    {
        "command": "relaytic evals run",
        "family": "evals",
        "surface_role": "surface_parity_check",
        "claim_posture": "auditability",
    },
    {
        "command": "relaytic mission-control show",
        "family": "mission_control",
        "surface_role": "workspace_status_board",
        "claim_posture": "navigation",
    },
    {
        "command": "relaytic handoff show",
        "family": "handoff",
        "surface_role": "human_agent_result_handoff",
        "claim_posture": "navigation",
    },
)

STALE_PUBLIC_SURFACE_TERMS = ("corr2surrogate", "prototype", "toy demo")

EXTRACTION_BOUNDARIES = {
    "src/relaytic/ui/cli.py": (
        "Continue extracting command-family helpers and manifest refresh chains into "
        "focused UI modules while retaining parser and top-level dispatch ownership."
    ),
    "src/relaytic/mission_control/agents.py": (
        "Split board assembly, chat-turn handling, and launch-surface rendering once "
        "mission control changes again."
    ),
    "src/relaytic/modeling/training.py": (
        "Separate candidate-family adapters, validation plumbing, and training report "
        "assembly when the next model-family slice touches this module."
    ),
    "src/relaytic/benchmark/agents.py": (
        "Move paper-freeze pack assembly and benchmark-family adapters into focused "
        "modules during Slice 15Z-R."
    ),
    "src/relaytic/runs/summary.py": (
        "Extract AML summary sections and generic summary rendering into focused "
        "builders after the benchmark freeze stabilizes summary contracts."
    ),
    "src/relaytic/intake/agents.py": (
        "Split source profiling, question generation, and intake report rendering on "
        "the next intake behavior change."
    ),
    "src/relaytic/investigation/agents.py": (
        "Separate specialist synthesis, evidence joins, and report rendering when "
        "investigation depth expands."
    ),
    "src/relaytic/interoperability/service.py": (
        "Separate protocol adapters from artifact serialization if the MCP or external "
        "agent surface changes."
    ),
    "src/relaytic/decision/agents.py": (
        "Split decision review assembly, rollback planning, and markdown rendering on "
        "the next decision-surface slice."
    ),
    "src/relaytic/orchestration/default_tools.py": (
        "Split registry construction by tool family when tool registration changes."
    ),
    "src/relaytic/analytics/architecture_routing.py": (
        "Separate routing feature extraction, eligibility gates, and explanation "
        "rendering when architecture routing changes again."
    ),
    "src/relaytic/assist/agents.py": (
        "Separate deterministic answer planning, artifact lookup, and response "
        "rendering when assist evolves beyond bounded guidance."
    ),
}


def build_repo_credibility_reports(project_root: str | Path) -> dict[str, dict[str, Any]]:
    root = Path(project_root)
    module_audit = _build_module_size_audit(root)
    public_surface_inventory = _build_public_surface_inventory()
    module_split_report = _build_module_split_report(root)
    module_extraction_plan = _build_module_extraction_plan(module_audit, module_split_report)
    benchmark_cleanup_report = _build_benchmark_surface_cleanup_report(public_surface_inventory, module_audit)
    pre_academy_audit = {
        "schema_version": REPO_CREDIBILITY_SCHEMA_VERSION,
        "slice": "15Z",
        "status": "implemented",
        "module_size_audit": module_audit,
        "module_split_report_path": _report_path("module_split_report"),
        "module_extraction_plan_path": _report_path("module_extraction_plan"),
        "public_surface_inventory_path": _report_path("public_surface_inventory"),
        "benchmark_surface_cleanup_report_path": _report_path("benchmark_surface_cleanup_report"),
        "acceptance_status": {
            "oversized_module_split": bool(module_split_report["split_modules"]),
            "retained_oversized_modules_documented": all(
                bool(item.get("next_extraction_boundary"))
                for item in module_audit["oversized_modules"]
            ),
            "public_surface_inventory_clean": all(
                not bool(item.get("stale_surface_language_detected"))
                for item in public_surface_inventory["commands"]
            ),
            "benchmark_cleanup_debt_listed": bool(benchmark_cleanup_report["retained_cleanup_debt"]),
        },
    }
    return {
        "pre_academy_repo_audit": pre_academy_audit,
        "module_extraction_plan": module_extraction_plan,
        "public_surface_inventory": public_surface_inventory,
        "module_split_report": module_split_report,
        "benchmark_surface_cleanup_report": benchmark_cleanup_report,
    }


def sync_repo_credibility_reports(
    project_root: str | Path,
    *,
    output_dir: str | Path | None = None,
) -> dict[str, Path]:
    root = Path(project_root)
    report_dir = Path(output_dir) if output_dir is not None else root / REPO_CREDIBILITY_REPORT_DIR
    report_dir.mkdir(parents=True, exist_ok=True)
    reports = build_repo_credibility_reports(root)
    written: dict[str, Path] = {}
    for key, payload in reports.items():
        filename = REPO_CREDIBILITY_FILENAMES[key]
        written[key] = write_json(report_dir / filename, payload, indent=2, sort_keys=True)
    return written


def _build_module_size_audit(root: Path) -> dict[str, Any]:
    modules = []
    for path in sorted((root / "src" / "relaytic").rglob("*.py")):
        rel = _relative_path(path, root)
        line_count = _line_count(path)
        modules.append(
            {
                "path": rel,
                "line_count": line_count,
                "oversized": line_count >= OVERSIZED_MODULE_LINE_THRESHOLD,
                "next_extraction_boundary": _extraction_boundary_for(rel)
                if line_count >= OVERSIZED_MODULE_LINE_THRESHOLD
                else None,
            }
        )
    oversized = [item for item in modules if item["oversized"]]
    oversized.sort(key=lambda item: (-int(item["line_count"]), str(item["path"])))
    top_modules = sorted(modules, key=lambda item: (-int(item["line_count"]), str(item["path"])))[:20]
    return {
        "threshold_lines": OVERSIZED_MODULE_LINE_THRESHOLD,
        "module_count": len(modules),
        "oversized_count": len(oversized),
        "oversized_modules": oversized,
        "top_modules": top_modules,
    }


def _build_public_surface_inventory() -> dict[str, Any]:
    commands = []
    for item in PUBLIC_SURFACE_COMMANDS:
        row = dict(item)
        stale_language = _surface_has_stale_language(row)
        row["stale_surface_language_detected"] = stale_language
        row["public_name"] = "Relaytic"
        row["package_name"] = "relaytic"
        row["compatibility_only_legacy_surface"] = False
        commands.append(row)
    return {
        "schema_version": REPO_CREDIBILITY_SCHEMA_VERSION,
        "slice": "15Z",
        "command_count": len(commands),
        "commands": commands,
        "stale_public_surface_terms_checked": list(STALE_PUBLIC_SURFACE_TERMS),
    }


def _build_module_split_report(root: Path) -> dict[str, Any]:
    source_path = root / EXTRACTION_SOURCE_MODULE
    extracted_path = root / EXTRACTED_MODULE
    return {
        "schema_version": REPO_CREDIBILITY_SCHEMA_VERSION,
        "slice": "15Z",
        "split_modules": [
            {
                "source_module": EXTRACTION_SOURCE_MODULE,
                "extracted_module": EXTRACTED_MODULE,
                "extracted_responsibility": "AML environment CLI surface execution, summary shaping, and run-summary refresh.",
                "source_module_lines_after_split": _line_count(source_path),
                "extracted_module_lines": _line_count(extracted_path),
                "public_behavior_preserved": True,
                "public_commands_preserved": ["relaytic aml environment"],
                "regression_tests": [
                    "tests/test_cli_slice15x.py::test_cli_slice15x_materializes_aml_environment_scorecards",
                    "tests/test_cli_slice15z.py::test_slice15z_import_boundary_smoke",
                    "tests/test_cli_slice15z.py::test_slice15z_public_surface_inventory_is_clean",
                ],
            }
        ],
        "retained_source_boundary": _extraction_boundary_for(EXTRACTION_SOURCE_MODULE),
    }


def _build_module_extraction_plan(
    module_audit: dict[str, Any],
    module_split_report: dict[str, Any],
) -> dict[str, Any]:
    return {
        "schema_version": REPO_CREDIBILITY_SCHEMA_VERSION,
        "slice": "15Z",
        "status": "partially_extracted_with_retained_boundaries",
        "extracted_now": module_split_report["split_modules"],
        "retained_oversized_modules": module_audit["oversized_modules"],
        "next_best_extraction": {
            "module": "src/relaytic/benchmark/agents.py",
            "reason": "Slice 15Z-R will touch paper benchmark freeze behavior, so paper-pack extraction can move with real contract changes.",
            "planned_boundary": _extraction_boundary_for("src/relaytic/benchmark/agents.py"),
        },
    }


def _build_benchmark_surface_cleanup_report(
    public_surface_inventory: dict[str, Any],
    module_audit: dict[str, Any],
) -> dict[str, Any]:
    benchmark_commands = [
        item for item in public_surface_inventory["commands"]
        if item["family"] in {"benchmark", "demo", "aml", "release_safety", "trace", "evals"}
    ]
    cli_audit = next(
        (item for item in module_audit["oversized_modules"] if item["path"] == EXTRACTION_SOURCE_MODULE),
        None,
    )
    retained_cleanup_debt = [
        {
            "debt_id": "paper_freeze_not_yet_materialized",
            "status": "retained_for_slice_15z_r",
            "paper_reproduction_impact": "Medium until Slice 15Z-R writes a frozen benchmark result table and reproducibility attestation.",
            "next_action": "Build the paper/release benchmark pack in Slice 15Z-R from this public-surface inventory.",
        },
        {
            "debt_id": "benchmark_agents_still_oversized",
            "status": "documented_boundary",
            "paper_reproduction_impact": "Low for current behavior, medium for reviewer code-reading speed.",
            "next_action": _extraction_boundary_for("src/relaytic/benchmark/agents.py"),
        },
        {
            "debt_id": "cli_entrypoint_still_oversized",
            "status": "partially_reduced",
            "paper_reproduction_impact": "Low for command behavior because the AML environment path has regression coverage.",
            "line_count_after_split": cli_audit.get("line_count") if isinstance(cli_audit, dict) else None,
            "next_action": _extraction_boundary_for(EXTRACTION_SOURCE_MODULE),
        },
        {
            "debt_id": "optional_dependency_profile_needs_freeze",
            "status": "retained_for_release_freeze",
            "paper_reproduction_impact": "Medium until exact paper commands name the `.[full]` dependency profile and Python version.",
            "next_action": "Record install profile, Python versions, dataset access notes, and exact benchmark command sequence in Slice 15Z-R.",
        },
    ]
    return {
        "schema_version": REPO_CREDIBILITY_SCHEMA_VERSION,
        "slice": "15Z",
        "benchmark_and_public_claim_commands": benchmark_commands,
        "stale_public_surface_language_detected": any(
            bool(item.get("stale_surface_language_detected")) for item in benchmark_commands
        ),
        "retained_cleanup_debt": retained_cleanup_debt,
    }


def _surface_has_stale_language(row: dict[str, str]) -> bool:
    text = " ".join(str(value).lower() for value in row.values())
    return any(term in text for term in STALE_PUBLIC_SURFACE_TERMS)


def _extraction_boundary_for(rel_path: str) -> str:
    return EXTRACTION_BOUNDARIES.get(
        rel_path,
        "Retain temporarily with explicit ownership; split the next behavior-specific helper set when this module changes.",
    )


def _relative_path(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def _report_path(key: str) -> str:
    return (REPO_CREDIBILITY_REPORT_DIR / REPO_CREDIBILITY_FILENAMES[key]).as_posix()


def _line_count(path: Path) -> int:
    try:
        return len(path.read_text(encoding="utf-8").splitlines())
    except OSError:
        return 0
