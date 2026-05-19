"""AML environment CLI surface helpers.

This module keeps the Slice 15X environment surface out of the main CLI file
while preserving the public `relaytic aml environment` behavior.
"""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Any, Optional


OutputPaths = Callable[[Path], dict[str, Path]]
RefreshManifest = Callable[..., Path]
ResolveRunDataPath = Callable[[Path], Optional[str]]


def run_aml_environment_phase(
    *,
    run_dir: str | Path,
    config_path: str | None,
    run_id: str | None,
    overwrite: bool,
    labels: dict[str, str] | None,
    output_paths: OutputPaths,
    ensure_paths_absent: Callable[..., None],
    refresh_manifest: RefreshManifest,
    resolve_run_data_path: ResolveRunDataPath,
) -> dict[str, Any]:
    """Build the AML environment artifacts for the public CLI surface."""
    from relaytic.aml import render_aml_environment_markdown, sync_aml_environment_artifacts

    root = Path(run_dir)
    if not root.exists():
        raise ValueError(f"Run directory does not exist: {root}")
    targets = output_paths(root)
    if not overwrite and all(path.exists() for path in targets.values()):
        return show_aml_environment_surface(
            run_dir=root,
            output_paths=output_paths,
            refresh_manifest=refresh_manifest,
            resolve_run_data_path=resolve_run_data_path,
        )
    ensure_paths_absent(list(targets.values()), overwrite=overwrite)
    written = sync_aml_environment_artifacts(root)
    manifest_path = refresh_manifest(
        root,
        run_id=run_id,
        policy_source=config_path,
        labels=labels,
    )
    summary_materialized = refresh_run_summary_from_current_artifacts(
        root,
        resolve_run_data_path=resolve_run_data_path,
    )
    bundle = read_aml_environment_bundle(root)
    return {
        "surface_payload": {
            "status": "ok",
            "run_dir": str(root),
            "manifest_path": str(manifest_path),
            "paths": {key: str(value) for key, value in written.items()},
            "aml_environment": aml_environment_surface_summary(bundle),
            "bundle": bundle,
            "run_summary": summary_materialized["summary"],
        },
        "human_output": render_aml_environment_markdown(bundle),
    }


def show_aml_environment_surface(
    *,
    run_dir: str | Path,
    output_paths: OutputPaths,
    refresh_manifest: RefreshManifest,
    resolve_run_data_path: ResolveRunDataPath,
) -> dict[str, Any]:
    """Show or lazily materialize the AML environment artifact bundle."""
    from relaytic.aml import render_aml_environment_markdown, sync_aml_environment_artifacts

    root = Path(run_dir)
    if not root.exists():
        raise ValueError(f"Run directory does not exist: {root}")
    bundle = read_aml_environment_bundle(root)
    if not all(path.exists() for path in output_paths(root).values()):
        sync_aml_environment_artifacts(root)
        bundle = read_aml_environment_bundle(root)
    if not bundle:
        raise ValueError(f"No AML environment artifacts could be built in {root}.")
    bundle = read_aml_environment_bundle(root)
    manifest_path = refresh_manifest(root)
    summary_materialized = refresh_run_summary_from_current_artifacts(
        root,
        resolve_run_data_path=resolve_run_data_path,
    )
    return {
        "surface_payload": {
            "status": "ok",
            "run_dir": str(root),
            "manifest_path": str(manifest_path),
            "aml_environment": aml_environment_surface_summary(bundle),
            "bundle": bundle,
            "run_summary": summary_materialized["summary"],
        },
        "human_output": render_aml_environment_markdown(bundle),
    }


def read_aml_environment_bundle(root: Path) -> dict[str, Any]:
    from relaytic.aml import read_aml_environment_artifacts

    return read_aml_environment_artifacts(root)


def aml_environment_surface_summary(bundle: dict[str, Any]) -> dict[str, Any]:
    manifest = dict(bundle.get("aml_eval_environment_manifest", {}))
    scorecard = dict(bundle.get("aml_environment_scorecard", {}))
    matrix = dict(bundle.get("aml_workflow_task_matrix", {}))
    failure = dict(bundle.get("aml_environment_failure_report", {}))
    benchmark = dict(bundle.get("aml_benchmark_environment_scorecard", {}))
    rows = matrix.get("rows", []) if isinstance(matrix.get("rows"), list) else []
    return {
        "status": scorecard.get("overall_environment_status") or manifest.get("status"),
        "environment_score": scorecard.get("environment_score"),
        "model_quality_score": scorecard.get("model_quality_score"),
        "workflow_safety_score": scorecard.get("workflow_safety_score"),
        "model_score_and_environment_score_separate": scorecard.get("model_score_and_environment_score_separate"),
        "model_success_environment_success_disagreement": scorecard.get("model_success_environment_success_disagreement")
        or failure.get("model_success_environment_success_disagreement"),
        "unsafe_steering_status": scorecard.get("unsafe_steering_status"),
        "unsafe_steering_trace_backed": scorecard.get("unsafe_steering_trace_backed"),
        "benchmark_environment_status": benchmark.get("overall_benchmark_environment_status")
        or scorecard.get("benchmark_environment_status"),
        "named_benchmark_family": benchmark.get("named_benchmark_family"),
        "reproducibility_status": benchmark.get("reproducibility_status"),
        "claim_safety_status": benchmark.get("claim_safety_status"),
        "benchmark_relevance_status": benchmark.get("benchmark_relevance_status"),
        "task_count": matrix.get("task_count"),
        "pass_count": matrix.get("pass_count"),
        "fail_count": matrix.get("fail_count"),
        "incomplete_count": matrix.get("incomplete_count"),
        "primary_failure_kind": failure.get("primary_failure_kind"),
        "recommended_next_action": scorecard.get("recommended_next_action") or failure.get("recommended_next_step"),
        "task_statuses": {
            str(item.get("task_id")): item.get("status")
            for item in rows
            if isinstance(item, dict) and item.get("task_id")
        },
        "summary": scorecard.get("summary") or manifest.get("summary"),
    }


def refresh_run_summary_from_current_artifacts(
    root: Path,
    *,
    resolve_run_data_path: ResolveRunDataPath,
) -> dict[str, Any]:
    from relaytic.core.json_utils import write_json
    from relaytic.runs.summary import (
        RUN_REPORT_RELATIVE_PATH,
        RUN_SUMMARY_FILENAME,
        build_run_summary,
        render_run_summary_markdown,
    )

    summary = build_run_summary(run_dir=root, data_path=resolve_run_data_path(root))
    summary_path = write_json(
        root / RUN_SUMMARY_FILENAME,
        summary,
        indent=2,
        ensure_ascii=False,
        sort_keys=True,
    )
    report_path = root / RUN_REPORT_RELATIVE_PATH
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(render_run_summary_markdown(summary), encoding="utf-8")
    return {
        "summary": summary,
        "summary_path": summary_path,
        "report_path": report_path,
    }
