"""Dependency graph, freshness contracts, and recompute planning for Slice 15E."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from relaytic.completion.storage import COMPLETION_FILENAMES
from relaytic.iteration.storage import ITERATION_FILENAMES
from relaytic.workspace.storage import RUN_CONTRACT_FILENAMES, WORKSPACE_FILENAMES, default_workspace_dir

from .storage import write_runtime_artifact


ARTIFACT_DEPENDENCY_GRAPH_SCHEMA_VERSION = "relaytic.runtime.artifact_dependency_graph.v1"
FRESHNESS_CONTRACT_SCHEMA_VERSION = "relaytic.runtime.freshness_contract.v1"
RECOMPUTE_PLAN_SCHEMA_VERSION = "relaytic.runtime.recompute_plan.v1"
MATERIALIZATION_CACHE_INDEX_SCHEMA_VERSION = "relaytic.runtime.materialization_cache_index.v1"
INVALIDATION_REPORT_SCHEMA_VERSION = "relaytic.runtime.invalidation_report.v1"

_SEARCH_STAGE_FILENAMES = [
    "hpo_budget_contract.json",
    "architecture_search_space.json",
    "trial_ledger.jsonl",
    "early_stopping_report.json",
    "search_loop_scorecard.json",
    "warm_start_transfer_report.json",
    "threshold_tuning_report.json",
]
_WORKSPACE_STAGE_FILENAMES = [
    "run_summary.json",
    "reports/summary.md",
    *RUN_CONTRACT_FILENAMES.values(),
    *(f"workspace/{name}" for name in WORKSPACE_FILENAMES.values()),
    f"workspace/{ITERATION_FILENAMES['next_run_plan']}",
]


@dataclass(frozen=True)
class StageContract:
    stage: str
    label: str
    outputs: tuple[str, ...]
    inputs: tuple[str, ...]
    depends_on: tuple[str, ...] = ()
    reuse_value: str = "medium"


_STAGE_CONTRACTS: tuple[StageContract, ...] = (
    StageContract(
        stage="search",
        label="Search and HPO",
        outputs=tuple(dict.fromkeys(_SEARCH_STAGE_FILENAMES)),
        inputs=(),
        reuse_value="high",
    ),
    StageContract(
        stage="benchmark",
        label="Benchmark Review",
        outputs=(
            "benchmark_gap_report.json",
            "benchmark_parity_report.json",
            "incumbent_parity_report.json",
            "paper_benchmark_manifest.json",
            "paper_benchmark_table.json",
            "benchmark_ablation_matrix.json",
            "rerun_variance_report.json",
            "benchmark_claims_report.json",
        ),
        inputs=("model_params.json",),
        depends_on=("search",),
        reuse_value="high",
    ),
    StageContract(
        stage="decision",
        label="Decision Lab",
        outputs=(
            "decision_world_model.json",
            "controller_policy.json",
            "decision_constraint_report.json",
            "action_boundary_report.json",
            "deployability_assessment.json",
            "review_gate_state.json",
            "value_of_more_data_report.json",
        ),
        inputs=("benchmark_parity_report.json", "benchmark_gap_report.json"),
        depends_on=("benchmark",),
        reuse_value="medium",
    ),
    StageContract(
        stage="completion",
        label="Completion Review",
        outputs=tuple(COMPLETION_FILENAMES.values()),
        inputs=(
            "benchmark_parity_report.json",
            "benchmark_gap_report.json",
            "decision_world_model.json",
            "controller_policy.json",
            "value_of_more_data_report.json",
        ),
        depends_on=("benchmark", "decision"),
        reuse_value="medium",
    ),
    StageContract(
        stage="trace",
        label="Trace Replay",
        outputs=(
            "trace_model.json",
            "adjudication_scorecard.json",
            "decision_replay_report.json",
        ),
        inputs=(
            "completion_decision.json",
            "lab_event_stream.jsonl",
            "control_injection_audit.json",
            "override_decision.json",
            "benchmark_parity_report.json",
        ),
        depends_on=("completion",),
        reuse_value="medium",
    ),
    StageContract(
        stage="workspace",
        label="Summary and Workspace",
        outputs=tuple(_WORKSPACE_STAGE_FILENAMES),
        inputs=(
            "completion_decision.json",
            "benchmark_parity_report.json",
            "search_loop_scorecard.json",
        ),
        depends_on=("search", "benchmark", "completion"),
        reuse_value="high",
    ),
)

_STAGE_INDEX = {contract.stage: contract for contract in _STAGE_CONTRACTS}


def sync_materialization_runtime_artifacts(run_dir: str | Path) -> dict[str, Any]:
    """Build and persist the Slice 15E runtime artifacts for one run."""

    root = Path(run_dir)
    graph = _build_artifact_dependency_graph(root)
    cache_index = _build_materialization_cache_index(root)
    freshness = _build_freshness_contract(root)
    invalidation = _build_invalidation_report(freshness)
    recompute = _build_recompute_plan(freshness)
    write_runtime_artifact(root, key="artifact_dependency_graph", payload=graph)
    write_runtime_artifact(root, key="materialization_cache_index", payload=cache_index)
    write_runtime_artifact(root, key="freshness_contract", payload=freshness)
    write_runtime_artifact(root, key="invalidation_report", payload=invalidation)
    write_runtime_artifact(root, key="recompute_plan", payload=recompute)
    return {
        "artifact_dependency_graph": graph,
        "materialization_cache_index": cache_index,
        "freshness_contract": freshness,
        "invalidation_report": invalidation,
        "recompute_plan": recompute,
    }


def stage_recompute_entry(run_dir: str | Path, *, stage: str) -> dict[str, Any]:
    """Return the latest recompute-planning entry for a stage."""

    bundle = sync_materialization_runtime_artifacts(run_dir)
    for item in bundle["recompute_plan"].get("stages", []):
        if str(item.get("stage", "")).strip() == stage:
            return dict(item)
    return {}


def build_materialization_surface(run_dir: str | Path) -> dict[str, Any]:
    """Build the human/agent-facing materialization surface."""

    root = Path(run_dir)
    bundle = sync_materialization_runtime_artifacts(root)
    recompute = bundle["recompute_plan"]
    invalidation = bundle["invalidation_report"]
    freshness = bundle["freshness_contract"]
    next_stage = dict(recompute.get("next_recommended_stage", {}))
    return {
        "status": "ok",
        "run_dir": str(root),
        "recompute": {
            "fresh_stage_count": int(freshness.get("fresh_stage_count", 0) or 0),
            "recompute_stage_count": int(recompute.get("recompute_stage_count", 0) or 0),
            "reusable_stage_count": int(recompute.get("reusable_stage_count", 0) or 0),
            "invalidated_stage_count": int(invalidation.get("invalidated_stage_count", 0) or 0),
            "next_stage": next_stage.get("stage"),
            "next_action": next_stage.get("recommended_action"),
            "next_reason": next_stage.get("reason"),
        },
        "bundle": bundle,
    }


def render_materialization_markdown(payload: dict[str, Any]) -> str:
    """Render a compact human-facing recompute plan."""

    recompute = dict(payload.get("recompute", {}))
    plan = dict(dict(payload.get("bundle", {})).get("recompute_plan", {}))
    lines = [
        "# Relaytic Recompute Plan",
        "",
        f"- Run directory: `{payload.get('run_dir')}`",
        f"- Fresh stages: `{recompute.get('fresh_stage_count', 0)}`",
        f"- Reusable stages: `{recompute.get('reusable_stage_count', 0)}`",
        f"- Recompute stages: `{recompute.get('recompute_stage_count', 0)}`",
        f"- Invalidated stages: `{recompute.get('invalidated_stage_count', 0)}`",
        f"- Next recommended stage: `{recompute.get('next_stage') or 'none'}`",
        f"- Why: {recompute.get('next_reason') or 'Nothing requires recomputation.'}",
    ]
    stages = list(plan.get("stages", []))
    if stages:
        lines.extend(["", "## Stage Decisions"])
        for item in stages:
            lines.append(
                f"- `{item.get('stage')}` status=`{item.get('status')}` action=`{item.get('recommended_action')}`: {item.get('reason')}"
            )
    return "\n".join(lines) + "\n"


def _build_artifact_dependency_graph(root: Path) -> dict[str, Any]:
    downstream: dict[str, list[str]] = {contract.stage: [] for contract in _STAGE_CONTRACTS}
    for contract in _STAGE_CONTRACTS:
        for upstream in contract.depends_on:
            downstream.setdefault(upstream, []).append(contract.stage)
    nodes = [
        {
            "stage": contract.stage,
            "label": contract.label,
            "depends_on": list(contract.depends_on),
            "downstream": sorted(downstream.get(contract.stage, [])),
            "output_artifacts": list(contract.outputs),
            "input_artifacts": list(contract.inputs),
            "reuse_value": contract.reuse_value,
        }
        for contract in _STAGE_CONTRACTS
    ]
    return {
        "schema_version": ARTIFACT_DEPENDENCY_GRAPH_SCHEMA_VERSION,
        "generated_at": _utc_now(),
        "run_dir": str(root),
        "node_count": len(nodes),
        "edge_count": sum(len(node["depends_on"]) for node in nodes),
        "nodes": nodes,
    }


def _build_materialization_cache_index(root: Path) -> dict[str, Any]:
    artifacts: list[dict[str, Any]] = []
    seen: set[str] = set()
    for contract in _STAGE_CONTRACTS:
        for rel_path in contract.outputs:
            if rel_path in seen:
                continue
            seen.add(rel_path)
            path = _resolve_artifact_path(root, rel_path)
            metadata = _artifact_metadata(path)
            artifacts.append(
                {
                    "path": rel_path,
                    "stage": contract.stage,
                    "scope": "workspace" if rel_path.startswith("workspace/") else "run",
                    **metadata,
                }
            )
    return {
        "schema_version": MATERIALIZATION_CACHE_INDEX_SCHEMA_VERSION,
        "generated_at": _utc_now(),
        "run_dir": str(root),
        "artifact_count": len(artifacts),
        "artifacts": artifacts,
    }


def _build_freshness_contract(root: Path) -> dict[str, Any]:
    stage_reports: list[dict[str, Any]] = []
    upstream_status: dict[str, str] = {}
    for contract in _STAGE_CONTRACTS:
        report = _build_stage_freshness_report(root, contract=contract, upstream_status=upstream_status)
        upstream_status[contract.stage] = report["status"]
        stage_reports.append(report)
    fresh_count = sum(1 for item in stage_reports if item["status"] == "fresh")
    return {
        "schema_version": FRESHNESS_CONTRACT_SCHEMA_VERSION,
        "generated_at": _utc_now(),
        "run_dir": str(root),
        "stage_count": len(stage_reports),
        "fresh_stage_count": fresh_count,
        "stages": stage_reports,
    }


def _build_invalidation_report(freshness_contract: dict[str, Any]) -> dict[str, Any]:
    invalidated = []
    for item in freshness_contract.get("stages", []):
        if str(item.get("status", "")) == "fresh":
            continue
        invalidated.append(
            {
                "stage": item.get("stage"),
                "status": item.get("status"),
                "reason": item.get("reason"),
                "upstream_blockers": list(item.get("upstream_blockers", [])),
                "newer_dependencies": list(item.get("newer_dependency_artifacts", [])),
                "missing_outputs": list(item.get("missing_outputs", [])),
                "missing_dependencies": list(item.get("missing_dependencies", [])),
            }
        )
    return {
        "schema_version": INVALIDATION_REPORT_SCHEMA_VERSION,
        "generated_at": _utc_now(),
        "invalidated_stage_count": len(invalidated),
        "stages": invalidated,
    }


def _build_recompute_plan(freshness_contract: dict[str, Any]) -> dict[str, Any]:
    stage_actions = []
    for item in freshness_contract.get("stages", []):
        stage_actions.append(
            {
                "stage": item.get("stage"),
                "label": item.get("label"),
                "status": item.get("status"),
                "recommended_action": item.get("recommended_action"),
                "reason": item.get("reason"),
                "reusable": bool(item.get("reusable", False)),
                "upstream_blockers": list(item.get("upstream_blockers", [])),
                "newer_dependency_artifacts": list(item.get("newer_dependency_artifacts", [])),
            }
        )
    next_stage = next((item for item in stage_actions if not item["reusable"]), None)
    return {
        "schema_version": RECOMPUTE_PLAN_SCHEMA_VERSION,
        "generated_at": _utc_now(),
        "stage_count": len(stage_actions),
        "reusable_stage_count": sum(1 for item in stage_actions if item["reusable"]),
        "recompute_stage_count": sum(1 for item in stage_actions if item["recommended_action"] != "reuse_existing"),
        "next_recommended_stage": next_stage or {},
        "stages": stage_actions,
    }


def _build_stage_freshness_report(
    root: Path,
    *,
    contract: StageContract,
    upstream_status: dict[str, str],
) -> dict[str, Any]:
    output_paths = [_resolve_artifact_path(root, rel_path) for rel_path in contract.outputs]
    input_paths = [_resolve_artifact_path(root, rel_path) for rel_path in dict.fromkeys(contract.inputs)]
    existing_output_paths = [path for path in output_paths if path.exists()]
    missing_outputs = [rel for rel, path in zip(contract.outputs, output_paths) if not path.exists()]
    missing_dependencies = [rel for rel, path in zip(contract.inputs, input_paths) if not path.exists()]
    upstream_blockers = [
        stage for stage in contract.depends_on if str(upstream_status.get(stage, "")).strip() not in {"", "fresh"}
    ]
    oldest_output_mtime = min((path.stat().st_mtime for path in existing_output_paths), default=None)
    dependency_mtms: list[tuple[str, float]] = [
        (rel, path.stat().st_mtime)
        for rel, path in zip(contract.inputs, input_paths)
        if path.exists()
    ]
    newer_dependency_artifacts = [
        rel
        for rel, mtime in dependency_mtms
        if oldest_output_mtime is not None and mtime > oldest_output_mtime + 1e-9
    ]

    status = "fresh"
    reason = "All declared outputs are present and newer than their dependencies."
    if missing_outputs:
        status = "missing_outputs"
        reason = "Required stage outputs are missing and must be materialized."
    elif missing_dependencies:
        status = "blocked_missing_dependency"
        reason = "Upstream dependency artifacts are missing, so this stage cannot be trusted yet."
    elif newer_dependency_artifacts:
        status = "stale"
        reason = "One or more dependency artifacts are newer than the current stage outputs."
    elif upstream_blockers:
        status = "upstream_invalidated"
        reason = "An upstream stage is stale or incomplete, so this stage should be recomputed after its blockers."

    if status == "fresh":
        recommended_action = "reuse_existing"
    elif status == "blocked_missing_dependency":
        recommended_action = "materialize_upstream_first"
    elif status == "upstream_invalidated":
        recommended_action = "recompute_after_upstream"
    else:
        recommended_action = "recompute_stage"

    return {
        "stage": contract.stage,
        "label": contract.label,
        "depends_on": list(contract.depends_on),
        "status": status,
        "recommended_action": recommended_action,
        "reason": reason,
        "reusable": status == "fresh",
        "output_artifact_count": len(contract.outputs),
        "existing_output_count": len(existing_output_paths),
        "dependency_artifact_count": len(contract.inputs),
        "missing_outputs": missing_outputs,
        "missing_dependencies": missing_dependencies,
        "upstream_blockers": upstream_blockers,
        "newer_dependency_artifacts": newer_dependency_artifacts,
        "oldest_output_modified_at": _format_mtime(oldest_output_mtime),
        "newest_dependency_modified_at": _format_mtime(max((mtime for _, mtime in dependency_mtms), default=None)),
    }


def _artifact_metadata(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {
            "exists": False,
            "size_bytes": 0,
            "modified_at": None,
        }
    stat = path.stat()
    return {
        "exists": True,
        "size_bytes": int(stat.st_size),
        "modified_at": _format_mtime(stat.st_mtime),
    }


def _resolve_artifact_path(root: Path, rel_path: str) -> Path:
    if rel_path.startswith("workspace/"):
        return default_workspace_dir(run_dir=root) / rel_path.removeprefix("workspace/")
    return root / rel_path


def _format_mtime(value: float | None) -> str | None:
    if value is None:
        return None
    return datetime.fromtimestamp(value, tz=timezone.utc).isoformat()


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()
