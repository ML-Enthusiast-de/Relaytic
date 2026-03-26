"""Slice 10A local source-graph and join-candidate reasoning."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from relaytic.ingestion import load_tabular_data

from .models import (
    DATA_ACQUISITION_PLAN_SCHEMA_VERSION,
    JOIN_CANDIDATE_REPORT_SCHEMA_VERSION,
    SOURCE_GRAPH_SCHEMA_VERSION,
    DataAcquisitionPlan,
    DataFabricControls,
    DataFabricTrace,
    JoinCandidateReport,
    SourceGraph,
    build_data_fabric_controls_from_policy,
)


SUPPORTED_EXTENSIONS = {
    ".csv",
    ".tsv",
    ".xlsx",
    ".xls",
    ".parquet",
    ".pq",
    ".feather",
    ".json",
    ".jsonl",
    ".ndjson",
}


def build_data_fabric_outputs(
    *,
    run_dir: str | Path,
    current_data_path: str | None,
    policy: dict[str, Any],
    dataset_profile: dict[str, Any],
) -> tuple[SourceGraph, JoinCandidateReport, DataAcquisitionPlan]:
    controls = build_data_fabric_controls_from_policy(policy)
    trace = DataFabricTrace(
        agent="data_fabric_agent",
        operating_mode="local_source_graph_and_join_reasoning",
        llm_used=False,
        llm_status="not_requested",
        deterministic_evidence=[
            "copy_only_local_paths",
            "same_directory_source_scan",
            "column_overlap_scoring",
            "bounded_join_candidates",
        ],
    )
    current_path = Path(current_data_path).resolve() if current_data_path else None
    current_columns = _current_columns(dataset_profile=dataset_profile)
    current_targets = _string_list(dataset_profile.get("candidate_target_columns"))
    current_target = current_targets[0] if current_targets else None
    nodes, edges = _build_source_graph(
        current_path=current_path,
        current_columns=current_columns,
        controls=controls,
    )
    generated_at = _utc_now()
    source_graph = SourceGraph(
        schema_version=SOURCE_GRAPH_SCHEMA_VERSION,
        generated_at=generated_at,
        controls=controls,
        status="ok" if nodes else "no_sources",
        current_source_id="current_source",
        source_count=len(nodes),
        edge_count=len(edges),
        nodes=nodes,
        edges=edges,
        summary=_source_graph_summary(nodes=nodes, edges=edges),
        trace=trace,
    )
    join_candidates = _build_join_candidates(
        nodes=nodes,
        current_target=current_target,
        dataset_profile=dataset_profile,
        controls=controls,
    )
    selected_candidate = join_candidates[0] if join_candidates else None
    join_report = JoinCandidateReport(
        schema_version=JOIN_CANDIDATE_REPORT_SCHEMA_VERSION,
        generated_at=generated_at,
        controls=controls,
        status="ok" if join_candidates else "no_candidate",
        selected_candidate_id=_clean_text(selected_candidate.get("candidate_id")) if selected_candidate else None,
        candidate_count=len(join_candidates),
        candidates=join_candidates,
        summary=_join_summary(join_candidates=join_candidates),
        trace=trace,
    )
    selected_strategy = "additional_local_data" if selected_candidate else "no_local_expansion"
    acquisition_plan = DataAcquisitionPlan(
        schema_version=DATA_ACQUISITION_PLAN_SCHEMA_VERSION,
        generated_at=generated_at,
        controls=controls,
        status="planned" if selected_candidate else "idle",
        selected_strategy=selected_strategy,
        recommended_source_id=_clean_text(selected_candidate.get("source_id")) if selected_candidate else None,
        recommended_join_candidate_id=_clean_text(selected_candidate.get("candidate_id")) if selected_candidate else None,
        recommended_data_path=_clean_text(selected_candidate.get("data_path")) if selected_candidate else None,
        bounded_followups=_bounded_followups(selected_candidate),
        summary=_plan_summary(selected_candidate=selected_candidate),
        trace=trace,
    )
    return source_graph, join_report, acquisition_plan


def _build_source_graph(
    *,
    current_path: Path | None,
    current_columns: list[str],
    controls: DataFabricControls,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    nodes: list[dict[str, Any]] = []
    edges: list[dict[str, Any]] = []
    current_dir = current_path.parent if current_path is not None else None
    if current_path is not None:
        nodes.append(
            {
                "source_id": "current_source",
                "path": str(current_path),
                "role": "current",
                "format": current_path.suffix.lower(),
                "column_count": len(current_columns),
                "columns": current_columns[:32],
                "shared_columns": [],
                "readable": current_path.exists(),
            }
        )
    if not controls.enabled or not controls.allow_local_source_graph or current_dir is None or not current_dir.exists():
        return nodes, edges
    candidate_paths = [
        path
        for path in sorted(current_dir.iterdir())
        if path.is_file()
        and path.resolve() != current_path
        and path.suffix.lower() in SUPPORTED_EXTENSIONS
    ][: controls.max_nearby_sources]
    for index, path in enumerate(candidate_paths, start=1):
        columns = _read_columns(path)
        shared = sorted(set(current_columns).intersection(columns))
        source_id = f"candidate_source_{index:02d}"
        nodes.append(
            {
                "source_id": source_id,
                "path": str(path.resolve()),
                "role": "candidate",
                "format": path.suffix.lower(),
                "column_count": len(columns),
                "columns": columns[:32],
                "shared_columns": shared[:16],
                "readable": bool(columns),
            }
        )
        if shared:
            edges.append(
                {
                    "edge_id": f"edge_current_{index:02d}",
                    "source": "current_source",
                    "target": source_id,
                    "relation": "shared_columns",
                    "shared_columns": shared[:16],
                    "shared_column_count": len(shared),
                }
            )
    return nodes, edges


def _build_join_candidates(
    *,
    nodes: list[dict[str, Any]],
    current_target: str | None,
    dataset_profile: dict[str, Any],
    controls: DataFabricControls,
) -> list[dict[str, Any]]:
    entity_candidates = set(_string_list(dataset_profile.get("entity_key_candidates")))
    hidden_candidates = set(_string_list(dataset_profile.get("hidden_key_candidates")))
    suspicious = set(_string_list(dataset_profile.get("suspicious_columns")))
    timestamp_column = _clean_text(dataset_profile.get("timestamp_column"))
    candidates: list[dict[str, Any]] = []
    for node in nodes:
        if node.get("role") != "candidate":
            continue
        shared = [item for item in _string_list(node.get("shared_columns")) if item not in suspicious]
        if not shared:
            continue
        join_keys = [item for item in shared if item in entity_candidates or item in hidden_candidates]
        time_keys = [item for item in shared if timestamp_column and item == timestamp_column]
        score = float(len(shared))
        if join_keys:
            score += 2.0
        if time_keys:
            score += 1.0
        if current_target and current_target in shared:
            score -= 0.75
        join_type = "entity_join" if join_keys else "time_aligned_join" if time_keys else "contextual_join"
        candidates.append(
            {
                "candidate_id": f"join_{node['source_id']}",
                "source_id": node["source_id"],
                "data_path": node.get("path"),
                "join_type": join_type,
                "score": round(score, 4),
                "shared_columns": shared[:12],
                "join_keys": join_keys[:6],
                "time_keys": time_keys[:4],
                "target_overlap": bool(current_target and current_target in shared),
                "reason": _candidate_reason(join_type=join_type, join_keys=join_keys, time_keys=time_keys, shared=shared),
            }
        )
    candidates.sort(key=lambda item: (-float(item.get("score", 0.0)), str(item.get("candidate_id", ""))))
    return candidates[: controls.max_join_candidates]


def _bounded_followups(selected_candidate: dict[str, Any] | None) -> list[dict[str, Any]]:
    if not selected_candidate:
        return []
    return [
        {
            "followup_id": "materialize_join_candidate",
            "action": "materialize_candidate_snapshot",
            "source_id": selected_candidate.get("source_id"),
            "data_path": selected_candidate.get("data_path"),
            "bounded": True,
        },
        {
            "followup_id": "validate_join_utility",
            "action": "compare_joined_vs_current_route",
            "source_id": selected_candidate.get("source_id"),
            "bounded": True,
        },
    ]


def _read_columns(path: Path) -> list[str]:
    try:
        frame = load_tabular_data(str(path)).frame
    except Exception:
        return []
    return [str(column).strip() for column in frame.columns if str(column).strip()]


def _current_columns(*, dataset_profile: dict[str, Any]) -> list[str]:
    current: list[str] = []
    for key in ("numeric_columns", "categorical_columns", "binary_like_columns", "candidate_target_columns"):
        current.extend(_string_list(dataset_profile.get(key)))
    return _dedupe_strings(current)


def _candidate_reason(*, join_type: str, join_keys: list[str], time_keys: list[str], shared: list[str]) -> str:
    if join_type == "entity_join" and join_keys:
        return "Shared entity-like columns suggest this local source could add stable contextual signals."
    if join_type == "time_aligned_join" and time_keys:
        return "Shared time keys suggest this local source could add event history or freshness context."
    return f"Relaytic found {len(shared)} non-suspicious shared column(s) that may reduce uncertainty more than wider search."


def _source_graph_summary(*, nodes: list[dict[str, Any]], edges: list[dict[str, Any]]) -> str:
    if len(nodes) <= 1:
        return "Relaytic did not find nearby local sources to expand the current copy-only working set."
    return f"Relaytic found {len(nodes) - 1} nearby local source(s) and {len(edges)} shared-column edge(s) around the current working copy."


def _join_summary(*, join_candidates: list[dict[str, Any]]) -> str:
    if not join_candidates:
        return "Relaytic did not find a safe local join candidate stronger than the current standalone snapshot."
    top = join_candidates[0]
    return (
        f"Relaytic found {len(join_candidates)} local join candidate(s); top candidate `{top.get('candidate_id')}` "
        f"uses `{top.get('join_type')}` reasoning with score `{top.get('score')}`."
    )


def _plan_summary(*, selected_candidate: dict[str, Any] | None) -> str:
    if not selected_candidate:
        return "Relaytic did not open a local data-acquisition plan because no bounded join candidate was credible."
    return (
        f"Relaytic recommends bounded local data expansion from `{selected_candidate.get('source_id')}` "
        "before widening search on the current snapshot."
    )


def _string_list(raw: Any) -> list[str]:
    if not isinstance(raw, list):
        return []
    return [str(item).strip() for item in raw if str(item).strip()]


def _dedupe_strings(values: list[str]) -> list[str]:
    ordered: list[str] = []
    seen: set[str] = set()
    for value in values:
        text = str(value).strip()
        if not text or text in seen:
            continue
        seen.add(text)
        ordered.append(text)
    return ordered


def _clean_text(value: Any) -> str | None:
    text = str(value or "").strip()
    return text or None


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()
