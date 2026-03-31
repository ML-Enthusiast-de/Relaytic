"""Slice 12D next-run planner and focus-record generation."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .models import (
    DATA_EXPANSION_CANDIDATES_SCHEMA_VERSION,
    FOCUS_DECISION_RECORD_SCHEMA_VERSION,
    NEXT_RUN_PLAN_SCHEMA_VERSION,
    DataExpansionCandidatesArtifact,
    FocusDecisionRecordArtifact,
    IterationTrace,
    NextRunPlanArtifact,
    build_iteration_controls_from_policy,
)
from .storage import write_iteration_bundle


@dataclass(frozen=True)
class IterationSyncResult:
    next_run_plan: NextRunPlanArtifact
    focus_decision_record: FocusDecisionRecordArtifact
    data_expansion_candidates: DataExpansionCandidatesArtifact


def sync_iteration_from_run(
    *,
    run_dir: str | Path,
    workspace_dir: str | Path,
    workspace_state: dict[str, Any],
    result_contract: dict[str, Any],
    belief_revision_triggers: dict[str, Any],
    summary_payload: dict[str, Any],
    handoff_bundle: dict[str, Any] | None = None,
    policy: dict[str, Any] | None = None,
) -> IterationSyncResult:
    """Create the explicit next-run plan for the current workspace."""

    root = Path(run_dir)
    controls = build_iteration_controls_from_policy(policy)
    handoff_payload = (handoff_bundle or {}).get("next_run_focus", {})
    run_handoff_payload = (handoff_bundle or {}).get("run_handoff", {})
    handoff = dict(handoff_payload) if isinstance(handoff_payload, dict) else {}
    run_handoff = dict(run_handoff_payload) if isinstance(run_handoff_payload, dict) else {}
    next_move = dict(result_contract.get("recommended_next_move", {}))
    direction = _clean_text(handoff.get("selection_id")) or _clean_text(next_move.get("direction")) or _clean_text(run_handoff.get("recommended_option_id")) or "same_data"
    action = _clean_text(next_move.get("action")) or "search_more"
    triggers = [dict(item) for item in belief_revision_triggers.get("triggers", []) if isinstance(item, dict)]
    decision_lab = dict(summary_payload.get("decision_lab", {}))
    benchmark = dict(summary_payload.get("benchmark", {}))
    workspace_id = _clean_text(workspace_state.get("workspace_id")) or "workspace_unknown"
    run_id = _clean_text(summary_payload.get("run_id")) or root.name or "run"

    next_run_plan = NextRunPlanArtifact(
        schema_version=NEXT_RUN_PLAN_SCHEMA_VERSION,
        generated_at=_utc_now(),
        controls=controls,
        status="ok",
        workspace_id=workspace_id,
        run_id=run_id,
        recommended_direction=direction,
        primary_reason=_primary_reason(direction=direction, action=action, summary_payload=summary_payload),
        secondary_actions=_secondary_actions(direction=direction, action=action, benchmark=benchmark, decision_lab=decision_lab),
        confidence=_clean_text(next_move.get("confidence")) or "medium",
        why_not_the_other_paths=dict(result_contract.get("why_not_other_moves", {})),
        required_user_inputs=[str(item).strip() for item in next_move.get("required_inputs", []) if str(item).strip()],
        belief_revision_dependency=_clean_text(triggers[0].get("trigger_id")) if triggers else None,
        summary=f"Relaytic recommends `{direction}` with primary action `{action}` for the next workspace step.",
        trace=_trace(),
    )
    focus_decision_record = FocusDecisionRecordArtifact(
        schema_version=FOCUS_DECISION_RECORD_SCHEMA_VERSION,
        generated_at=_utc_now(),
        controls=controls,
        status="ok",
        workspace_id=workspace_id,
        run_id=run_id,
        selected_direction=direction,
        source=_clean_text(handoff.get("source")) or "relaytic_result_contract",
        actor_type=_clean_text(handoff.get("actor_type")) or "relaytic",
        actor_name=_clean_text(handoff.get("actor_name")),
        notes=_clean_text(handoff.get("notes")),
        reset_learnings_requested=bool(handoff.get("reset_learnings_requested", False)),
        summary=f"Relaytic recorded next-run direction `{direction}` for workspace `{workspace_id}`.",
        trace=_trace(),
    )
    candidates = _data_expansion_candidates(summary_payload=summary_payload, controls=controls)
    data_expansion_candidates = DataExpansionCandidatesArtifact(
        schema_version=DATA_EXPANSION_CANDIDATES_SCHEMA_VERSION,
        generated_at=_utc_now(),
        controls=controls,
        status="ok",
        workspace_id=workspace_id,
        run_id=run_id,
        candidate_count=len(candidates),
        candidates=candidates,
        summary=f"Relaytic recorded `{len(candidates)}` possible local data-expansion candidate(s) for later continuation.",
        trace=_trace(),
    )
    write_iteration_bundle(
        workspace_dir=workspace_dir,
        run_dir=root,
        next_run_plan=next_run_plan,
        focus_decision_record=focus_decision_record,
        data_expansion_candidates=data_expansion_candidates,
    )
    return IterationSyncResult(
        next_run_plan=next_run_plan,
        focus_decision_record=focus_decision_record,
        data_expansion_candidates=data_expansion_candidates,
    )


def _primary_reason(*, direction: str, action: str, summary_payload: dict[str, Any]) -> str:
    if direction == "add_data":
        return "Relaytic believes additional local data is more valuable than deeper search on the current snapshot."
    if direction == "new_dataset":
        return "Relaytic believes the current framing should restart instead of compounding continuity debt."
    rationale = _clean_text(summary_payload.get("next_step", {}).get("rationale"))
    if rationale:
        return rationale
    return f"Relaytic believes `{action}` is the highest-value bounded continuation on the current data."


def _secondary_actions(*, direction: str, action: str, benchmark: dict[str, Any], decision_lab: dict[str, Any]) -> list[str]:
    actions = [action]
    if _clean_text(benchmark.get("incumbent_name")):
        actions.append("benchmark_incumbent")
    if direction == "add_data":
        actions.append("add_features")
    if _clean_text(decision_lab.get("recommended_source_id")):
        actions.append("expand_entities")
    deduped: list[str] = []
    for item in actions:
        if item and item not in deduped:
            deduped.append(item)
    return deduped


def _data_expansion_candidates(*, summary_payload: dict[str, Any], controls: Any) -> list[dict[str, Any]]:
    decision_lab = dict(summary_payload.get("decision_lab", {}))
    candidates: list[dict[str, Any]] = []
    source_id = _clean_text(decision_lab.get("recommended_source_id"))
    if source_id:
        candidates.append(
            {
                "candidate_id": source_id,
                "kind": "recommended_local_source",
                "detail": f"Relaytic flagged local source `{source_id}` as the most coherent expansion candidate.",
            }
        )
    join_count = int(decision_lab.get("join_candidate_count", 0) or 0)
    if join_count > 0:
        candidates.append(
            {
                "candidate_id": "join_candidates_present",
                "kind": "join_candidate_pool",
                "detail": f"Relaytic found `{join_count}` local join candidate(s) worth reviewing before spending more search budget.",
            }
        )
    if not candidates and _clean_text(summary_payload.get("data", {}).get("source_type")):
        candidates.append(
            {
                "candidate_id": "no_explicit_expansion_candidate",
                "kind": "manual_review",
                "detail": "Relaytic did not find a concrete local expansion source, so manual review of adjacent data is the safest next step.",
            }
        )
    return candidates[: controls.max_data_expansion_candidates]


def _clean_text(value: Any) -> str | None:
    text = str(value or "").strip()
    return text or None


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _trace() -> IterationTrace:
    return IterationTrace(
        agent="workspace_iteration_planner",
        operating_mode="deterministic_workspace_planning",
        llm_used=False,
        llm_status="not_requested",
        deterministic_evidence=["result_contract", "handoff_bundle", "decision_lab", "benchmark"],
        advisory_notes=["The next-run plan must choose same data, add data, or new dataset explicitly."],
    )
