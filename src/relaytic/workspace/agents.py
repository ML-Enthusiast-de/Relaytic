"""Slice 12D workspace continuity and result-contract generation."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
from pathlib import Path
from typing import Any

from relaytic.core.benchmark_statuses import benchmark_is_reference_competitive

from .models import (
    BELIEF_REVISION_TRIGGERS_SCHEMA_VERSION,
    CONFIDENCE_POSTURE_SCHEMA_VERSION,
    RESULT_CONTRACT_SCHEMA_VERSION,
    WORKSPACE_FOCUS_HISTORY_SCHEMA_VERSION,
    WORKSPACE_LINEAGE_SCHEMA_VERSION,
    WORKSPACE_MEMORY_POLICY_SCHEMA_VERSION,
    WORKSPACE_STATE_SCHEMA_VERSION,
    BeliefRevisionTriggersArtifact,
    ConfidencePostureArtifact,
    ResultContractArtifact,
    WorkspaceFocusHistoryArtifact,
    WorkspaceLineageArtifact,
    WorkspaceMemoryPolicyArtifact,
    WorkspaceStateArtifact,
    WorkspaceTrace,
    build_workspace_controls_from_policy,
)
from .storage import (
    RUN_CONTRACT_FILENAMES,
    default_workspace_dir,
    read_result_contract_artifacts,
    read_workspace_bundle,
    write_result_contract_artifacts,
    write_workspace_bundle,
)


@dataclass(frozen=True)
class WorkspaceSyncResult:
    workspace_state: WorkspaceStateArtifact
    workspace_lineage: WorkspaceLineageArtifact
    workspace_focus_history: WorkspaceFocusHistoryArtifact
    workspace_memory_policy: WorkspaceMemoryPolicyArtifact
    result_contract: ResultContractArtifact
    confidence_posture: ConfidencePostureArtifact
    belief_revision_triggers: BeliefRevisionTriggersArtifact
    workspace_dir: Path


def sync_workspace_from_run(
    *,
    run_dir: str | Path,
    summary_payload: dict[str, Any],
    handoff_bundle: dict[str, Any] | None = None,
    learnings_state: dict[str, Any] | None = None,
    learnings_snapshot: dict[str, Any] | None = None,
    policy: dict[str, Any] | None = None,
) -> WorkspaceSyncResult:
    """Create or refresh the explicit workspace continuity bundle for a run."""

    root = Path(run_dir)
    workspace_dir = default_workspace_dir(run_dir=root)
    controls = build_workspace_controls_from_policy(policy)
    existing_bundle = read_workspace_bundle(workspace_dir)
    existing_state = dict(existing_bundle.get("workspace_state", {}))
    existing_lineage = dict(existing_bundle.get("workspace_lineage", {}))
    existing_focus_history = dict(existing_bundle.get("workspace_focus_history", {}))

    run_id = _clean_text(summary_payload.get("run_id")) or root.name or "run"
    workspace_id = _clean_text(existing_state.get("workspace_id")) or _workspace_id_for_dir(workspace_dir)
    workspace_label = _clean_text(existing_state.get("workspace_label")) or f"Relaytic Workspace {workspace_id[-6:]}"
    handoff_payload = handoff_bundle or {}

    result_contract = _build_result_contract(
        run_id=run_id,
        workspace_id=workspace_id,
        summary_payload=summary_payload,
        handoff_bundle=handoff_payload,
    )
    confidence_posture = _build_confidence_posture(
        run_id=run_id,
        workspace_id=workspace_id,
        result_contract=result_contract,
    )
    belief_revision_triggers = _build_belief_revision_triggers(
        run_id=run_id,
        workspace_id=workspace_id,
        summary_payload=summary_payload,
        result_contract=result_contract,
    )
    write_result_contract_artifacts(
        root,
        result_contract=result_contract,
        confidence_posture=confidence_posture,
        belief_revision_triggers=belief_revision_triggers,
    )

    current_focus = _current_focus(summary_payload=summary_payload, handoff_bundle=handoff_payload, result_contract=result_contract)
    continuity_mode = _continuity_mode(current_focus)
    trace = _trace()
    lineage_runs = _update_lineage_runs(
        existing_runs=[dict(item) for item in existing_lineage.get("runs", []) if isinstance(item, dict)],
        summary_payload=summary_payload,
        run_id=run_id,
        workspace_id=workspace_id,
        current_focus=current_focus,
    )[: controls.max_lineage_runs]
    focus_events = _update_focus_events(
        existing_events=[dict(item) for item in existing_focus_history.get("events", []) if isinstance(item, dict)],
        summary_payload=summary_payload,
        run_id=run_id,
        workspace_id=workspace_id,
        current_focus=current_focus,
    )[: controls.max_focus_events]

    workspace_state = WorkspaceStateArtifact(
        schema_version=WORKSPACE_STATE_SCHEMA_VERSION,
        generated_at=_utc_now(),
        controls=controls,
        status="active",
        workspace_id=workspace_id,
        workspace_label=workspace_label,
        workspace_dir=str(workspace_dir),
        current_run_id=run_id,
        current_focus=current_focus,
        continuity_mode=continuity_mode,
        prior_run_count=max(0, len(lineage_runs) - 1),
        next_run_plan_path=str(workspace_dir / "next_run_plan.json"),
        result_contract_path=str(root / RUN_CONTRACT_FILENAMES["result_contract"]),
        learnings_state_path=_clean_text(summary_payload.get("artifacts", {}).get("learnings_state_path")),
        summary=(
            f"Relaytic keeps workspace `{workspace_label}` active with current focus "
            f"`{current_focus or 'not_selected'}` across `{len(lineage_runs)}` run(s)."
        ),
        trace=trace,
    )
    workspace_lineage = WorkspaceLineageArtifact(
        schema_version=WORKSPACE_LINEAGE_SCHEMA_VERSION,
        generated_at=_utc_now(),
        controls=controls,
        status="ok",
        workspace_id=workspace_id,
        current_run_id=run_id,
        run_count=len(lineage_runs),
        runs=lineage_runs,
        summary=f"Relaytic tracks `{len(lineage_runs)}` run(s) inside workspace `{workspace_label}`.",
        trace=trace,
    )
    workspace_focus_history = WorkspaceFocusHistoryArtifact(
        schema_version=WORKSPACE_FOCUS_HISTORY_SCHEMA_VERSION,
        generated_at=_utc_now(),
        controls=controls,
        status="ok",
        workspace_id=workspace_id,
        current_focus=current_focus,
        event_count=len(focus_events),
        events=focus_events,
        summary=f"Relaytic recorded `{len(focus_events)}` focus event(s) for this workspace.",
        trace=trace,
    )
    workspace_memory_policy = WorkspaceMemoryPolicyArtifact(
        schema_version=WORKSPACE_MEMORY_POLICY_SCHEMA_VERSION,
        generated_at=_utc_now(),
        controls=controls,
        status="ok",
        workspace_id=workspace_id,
        preferred_focus=current_focus,
        active_learning_count=_count_learnings(learnings_state, learnings_snapshot, status_values={"active"}),
        tentative_learning_count=_count_learnings(learnings_state, learnings_snapshot, status_values={"tentative"}),
        invalidated_learning_count=_count_learnings(learnings_state, learnings_snapshot, status_values={"invalidated"}),
        expired_learning_count=_count_learnings(learnings_state, learnings_snapshot, status_values={"expired", "reset"}),
        reset_scopes=[
            "learnings_only",
            "focus_only",
            "next_run_plan_only",
            "workspace_soft_reset",
            "workspace_archive_and_restart",
        ],
        summary="Relaytic keeps workspace memory policy explicit so resets, focus, and learnings remain governed.",
        trace=trace,
    )
    write_workspace_bundle(
        workspace_dir,
        workspace_state=workspace_state,
        workspace_lineage=workspace_lineage,
        workspace_focus_history=workspace_focus_history,
        workspace_memory_policy=workspace_memory_policy,
    )
    return WorkspaceSyncResult(
        workspace_state=workspace_state,
        workspace_lineage=workspace_lineage,
        workspace_focus_history=workspace_focus_history,
        workspace_memory_policy=workspace_memory_policy,
        result_contract=result_contract,
        confidence_posture=confidence_posture,
        belief_revision_triggers=belief_revision_triggers,
        workspace_dir=workspace_dir,
    )


def render_user_result_report_from_contract(
    *,
    result_contract: dict[str, Any],
    confidence_posture: dict[str, Any],
    belief_revision_triggers: dict[str, Any],
    next_run_plan: dict[str, Any] | None,
    workspace_state: dict[str, Any] | None,
) -> str:
    """Render the human-facing report directly from the result contract."""

    evidence = dict(result_contract.get("evidence_strength", {}))
    next_move = dict(result_contract.get("recommended_next_move", {}))
    beliefs = [dict(item) for item in result_contract.get("current_beliefs", []) if isinstance(item, dict)]
    unresolved = [dict(item) for item in result_contract.get("unresolved_items", []) if isinstance(item, dict)]
    why_this_move = [dict(item) for item in result_contract.get("why_this_move", []) if isinstance(item, dict)]
    triggers = [dict(item) for item in belief_revision_triggers.get("triggers", []) if isinstance(item, dict)]
    plan = dict(next_run_plan or {})
    workspace = dict(workspace_state or {})
    lines = [
        "# Relaytic User Result Report",
        "",
        f"Relaytic finished this run with status `{result_contract.get('status') or 'unknown'}` inside workspace `{workspace.get('workspace_label') or result_contract.get('workspace_id') or 'unknown'}`.",
        "",
        "## What Relaytic Believes",
    ]
    for belief in beliefs[:4]:
        lines.append(f"- {belief.get('statement')}")
    lines.extend(
        [
            "",
            "## Evidence Posture",
            f"- Overall strength: `{evidence.get('overall_strength') or 'unknown'}`",
            f"- Primary metric: `{dict(evidence.get('metric_posture', {})).get('primary_metric') or 'unknown'}` = `{dict(evidence.get('metric_posture', {})).get('primary_value')}`",
            f"- Benchmark posture: `{evidence.get('benchmark_posture') or 'unknown'}`",
            f"- Review need: `{confidence_posture.get('review_need') or 'unknown'}`",
            f"- Confidence: `{confidence_posture.get('overall_confidence') or 'unknown'}`",
        ]
    )
    if unresolved:
        lines.extend(["", "## What Remains Unresolved"])
        for item in unresolved[:5]:
            lines.append(f"- `{item.get('severity')}` {item.get('statement')}")
    lines.extend(
        [
            "",
            "## Recommended Next Move",
            f"- Direction: `{next_move.get('direction') or plan.get('recommended_direction') or 'unknown'}`",
            f"- Action: `{next_move.get('action') or 'unknown'}`",
            f"- Why: {', '.join(str(item.get('statement')).strip() for item in why_this_move[:3] if str(item.get('statement')).strip()) or 'Relaytic recorded no structured reason.'}",
        ]
    )
    if plan.get("required_user_inputs"):
        lines.append("- What Relaytic still needs from you: " + ", ".join(f"`{item}`" for item in plan.get("required_user_inputs", [])))
    if triggers:
        lines.extend(["", "## What Would Change Relaytic's Mind"])
        for item in triggers[:4]:
            lines.append(f"- {item.get('condition')}")
    lines.extend(
        [
            "",
            "## Next Commands",
            "- Inspect the workspace: `relaytic workspace show --run-dir <run_dir>`",
            "- Continue on the same data: `relaytic workspace continue --run-dir <run_dir> --direction same_data --notes \"focus on the most important risk\"`",
            "- Add more local data: `relaytic workspace continue --run-dir <run_dir> --direction add_data --notes \"bring more local context\"`",
            "- Start over: `relaytic workspace continue --run-dir <run_dir> --direction new_dataset --notes \"start fresh\"`",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def render_agent_result_report_from_contract(
    *,
    result_contract: dict[str, Any],
    confidence_posture: dict[str, Any],
    belief_revision_triggers: dict[str, Any],
    next_run_plan: dict[str, Any] | None,
    workspace_state: dict[str, Any] | None,
) -> str:
    """Render the agent-facing report directly from the result contract."""

    objective = dict(result_contract.get("objective_summary", {}))
    evidence = dict(result_contract.get("evidence_strength", {}))
    next_move = dict(result_contract.get("recommended_next_move", {}))
    beliefs = [dict(item) for item in result_contract.get("current_beliefs", []) if isinstance(item, dict)]
    unresolved = [dict(item) for item in result_contract.get("unresolved_items", []) if isinstance(item, dict)]
    triggers = [dict(item) for item in belief_revision_triggers.get("triggers", []) if isinstance(item, dict)]
    plan = dict(next_run_plan or {})
    workspace = dict(workspace_state or {})
    lines = [
        "# Relaytic Agent Result Report",
        "",
        "## Contract",
        f"- Run id: `{result_contract.get('run_id') or 'unknown'}`",
        f"- Workspace id: `{result_contract.get('workspace_id') or workspace.get('workspace_id') or 'unknown'}`",
        f"- Status: `{result_contract.get('status') or 'unknown'}`",
        f"- Task type: `{objective.get('task_type') or 'unknown'}`",
        f"- Target summary: `{objective.get('target_summary') or 'unknown'}`",
        f"- Recommended direction: `{next_move.get('direction') or plan.get('recommended_direction') or 'unknown'}`",
        f"- Recommended action: `{next_move.get('action') or 'unknown'}`",
        f"- Confidence: `{confidence_posture.get('overall_confidence') or 'unknown'}`",
        f"- Review need: `{confidence_posture.get('review_need') or 'unknown'}`",
        "",
        "## Beliefs",
    ]
    for belief in beliefs[:4]:
        lines.append(f"- `{belief.get('belief_id')}` `{belief.get('support_level')}`: {belief.get('statement')}")
    lines.extend(
        [
            "",
            "## Evidence",
            f"- Overall strength: `{evidence.get('overall_strength') or 'unknown'}`",
            f"- Metric posture: `{dict(evidence.get('metric_posture', {})).get('primary_metric') or 'unknown'}` / `{dict(evidence.get('metric_posture', {})).get('primary_value')}`",
            f"- Benchmark posture: `{evidence.get('benchmark_posture') or 'unknown'}`",
            f"- Trace posture: `{evidence.get('trace_posture') or 'unknown'}`",
            f"- Risk posture: `{evidence.get('risk_posture') or 'unknown'}`",
            "",
            "## Unresolved",
            f"- Count: `{len(unresolved)}`",
        ]
    )
    for item in unresolved[:5]:
        lines.append(f"- `{item.get('kind')}` `{item.get('severity')}`: {item.get('statement')}")
    lines.extend(["", "## Revision Triggers", f"- Count: `{len(triggers)}`"])
    for item in triggers[:4]:
        lines.append(f"- `{item.get('expected_effect')}`: {item.get('condition')}")
    lines.extend(
        [
            "",
            "## Artifact Refs",
            f"- Result contract: `{RUN_CONTRACT_FILENAMES['result_contract']}`",
            f"- Confidence posture: `{RUN_CONTRACT_FILENAMES['confidence_posture']}`",
            f"- Belief revision triggers: `{RUN_CONTRACT_FILENAMES['belief_revision_triggers']}`",
            f"- Next-run plan: `{workspace.get('next_run_plan_path') or 'workspace/next_run_plan.json'}`",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def render_workspace_review_markdown(
    *,
    workspace_bundle: dict[str, Any],
    result_contract_bundle: dict[str, Any],
    next_run_plan: dict[str, Any] | None = None,
) -> str:
    """Render a concise workspace review surface."""

    state = dict(workspace_bundle.get("workspace_state", {}))
    lineage = dict(workspace_bundle.get("workspace_lineage", {}))
    result_contract = dict(result_contract_bundle.get("result_contract", {}))
    confidence = dict(result_contract_bundle.get("confidence_posture", {}))
    triggers = dict(result_contract_bundle.get("belief_revision_triggers", {}))
    plan = dict(next_run_plan or {})
    lines = [
        "# Relaytic Workspace Review",
        "",
        f"- Workspace: `{state.get('workspace_label') or state.get('workspace_id') or 'unknown'}`",
        f"- Current run: `{state.get('current_run_id') or 'unknown'}`",
        f"- Continuity mode: `{state.get('continuity_mode') or 'unknown'}`",
        f"- Prior runs: `{state.get('prior_run_count', 0)}`",
        f"- Current focus: `{state.get('current_focus') or 'none'}`",
        f"- Result contract status: `{result_contract.get('status') or 'unknown'}`",
        f"- Confidence: `{confidence.get('overall_confidence') or 'unknown'}`",
        f"- Recommended direction: `{dict(result_contract.get('recommended_next_move', {})).get('direction') or plan.get('recommended_direction') or 'unknown'}`",
        f"- Recommended action: `{dict(result_contract.get('recommended_next_move', {})).get('action') or 'unknown'}`",
        f"- Belief revision triggers: `{len(triggers.get('triggers', [])) if isinstance(triggers.get('triggers'), list) else 0}`",
        f"- Lineage entries: `{lineage.get('run_count', 0)}`",
    ]
    return "\n".join(lines).rstrip() + "\n"


def read_workspace_review_bundle(run_dir: str | Path) -> dict[str, Any]:
    """Read the workspace + result-contract bundle for a run."""

    root = Path(run_dir)
    workspace_dir = default_workspace_dir(run_dir=root)
    return {
        "workspace_dir": str(workspace_dir),
        "workspace_bundle": read_workspace_bundle(workspace_dir),
        "result_contract_bundle": read_result_contract_artifacts(root),
    }


def _build_result_contract(
    *,
    run_id: str,
    workspace_id: str,
    summary_payload: dict[str, Any],
    handoff_bundle: dict[str, Any],
) -> ResultContractArtifact:
    decision = dict(summary_payload.get("decision", {}))
    benchmark = dict(summary_payload.get("benchmark", {}))
    trace = dict(summary_payload.get("trace", {}))
    next_step = dict(summary_payload.get("next_step", {}))
    decision_lab = dict(summary_payload.get("decision_lab", {}))
    feasibility = dict(summary_payload.get("feasibility", {}))
    run_handoff_payload = handoff_bundle.get("run_handoff", {})
    next_run_focus_payload = handoff_bundle.get("next_run_focus", {})
    run_handoff = dict(run_handoff_payload) if isinstance(run_handoff_payload, dict) else {}
    next_run_focus = dict(next_run_focus_payload) if isinstance(next_run_focus_payload, dict) else {}
    focus_id = (
        _clean_text(next_run_focus.get("selection_id"))
        or _clean_text(feasibility.get("recommended_direction"))
        or _clean_text(run_handoff.get("recommended_option_id"))
        or "same_data"
    )
    action = _normalize_action(direction=focus_id, action_hint=_clean_text(next_step.get("recommended_action")))
    unresolved_items = _unresolved_items(summary_payload=summary_payload, handoff_bundle=handoff_bundle, action=action)
    confidence = _overall_confidence(summary_payload=summary_payload, unresolved_items=unresolved_items)
    return ResultContractArtifact(
        schema_version=RESULT_CONTRACT_SCHEMA_VERSION,
        run_id=run_id,
        workspace_id=workspace_id,
        generated_at=_utc_now(),
        status=_result_status(confidence=confidence, unresolved_items=unresolved_items, direction=focus_id),
        objective_summary={
            "task_type": _normalize_task_type(_clean_text(decision.get("task_type"))),
            "target_summary": _clean_text(decision.get("target_column")) or "analysis_or_decision_target_not_explicit",
            "focus_profile": _clean_text(next_run_focus.get("selection_label")) or _clean_text(run_handoff.get("headline")) or "governed_run",
            "decision_context": _clean_text(decision_lab.get("action_regime")) or "governed_structured_data_decision",
            "active_constraints": _active_constraints(summary_payload),
        },
        current_beliefs=_current_beliefs(summary_payload=summary_payload, handoff_bundle=handoff_bundle, focus_id=focus_id),
        evidence_strength={
            "overall_strength": _overall_strength(summary_payload=summary_payload, unresolved_items=unresolved_items),
            "metric_posture": {
                "primary_metric": _clean_text(decision.get("primary_metric")) or "unknown",
                "primary_value": _primary_metric_value(summary_payload),
                "minimum_contract_met": bool(summary_payload.get("completion", {}).get("complete_for_mode")),
                "calibration_ok": summary_payload.get("decision", {}).get("calibration_applied"),
                "uncertainty_ok": summary_payload.get("decision", {}).get("uncertainty_available"),
            },
            "benchmark_posture": _clean_text(benchmark.get("incumbent_parity_status")) or _clean_text(benchmark.get("parity_status")) or "unknown",
            "trace_posture": _clean_text(trace.get("status")) or "unknown",
            "data_posture": _clean_text(summary_payload.get("data", {}).get("data_mode")) or "unknown",
            "risk_posture": "high" if unresolved_items else ("medium" if int(summary_payload.get("handoff", {}).get("risk_count", 0) or 0) > 0 else "low"),
        },
        unresolved_items=unresolved_items,
        recommended_next_move={
            "direction": focus_id,
            "action": action,
            "confidence": confidence,
            "required_inputs": _required_inputs(direction=focus_id),
            "estimated_cost_posture": "medium" if action in {"retrain", "collect_more_data"} else "low",
            "estimated_value_posture": "high" if focus_id in {"add_data", "same_data"} else "medium",
        },
        why_this_move=_why_this_move(summary_payload=summary_payload, focus_id=focus_id, action=action),
        why_not_other_moves=_why_not_other_moves(selected_direction=focus_id),
        confidence_posture_ref=RUN_CONTRACT_FILENAMES["confidence_posture"],
        belief_revision_triggers_ref=RUN_CONTRACT_FILENAMES["belief_revision_triggers"],
        source_artifacts=_source_artifacts(summary_payload),
    )


def _build_confidence_posture(*, run_id: str, workspace_id: str, result_contract: ResultContractArtifact) -> ConfidencePostureArtifact:
    unresolved = [dict(item) for item in result_contract.unresolved_items if isinstance(item, dict)]
    overall_confidence = str(result_contract.recommended_next_move.get("confidence") or "medium")
    review_need = "required" if result_contract.status in {"needs_review", "blocked"} else ("recommended" if unresolved else "none")
    fragility = [str(item.get("statement")).strip() for item in unresolved[:3] if str(item.get("statement")).strip()]
    if not fragility:
        fragility.append("Current beliefs are stable under the active contract, but future data or benchmark changes can still revise them.")
    return ConfidencePostureArtifact(
        schema_version=CONFIDENCE_POSTURE_SCHEMA_VERSION,
        run_id=run_id,
        workspace_id=workspace_id,
        generated_at=_utc_now(),
        overall_confidence=overall_confidence,
        known_fragility=fragility,
        abstention_readiness="ready" if review_need in {"required", "recommended"} else "not_needed",
        review_need=review_need,
        confidence_explanation=(
            f"Relaytic marks this run `{overall_confidence}` confidence because unresolved items = `{len(unresolved)}` "
            f"and next direction = `{result_contract.recommended_next_move.get('direction')}`."
        ),
    )


def _build_belief_revision_triggers(
    *,
    run_id: str,
    workspace_id: str,
    summary_payload: dict[str, Any],
    result_contract: ResultContractArtifact,
) -> BeliefRevisionTriggersArtifact:
    benchmark = dict(summary_payload.get("benchmark", {}))
    triggers = [
        {
            "trigger_id": "trigger_more_local_data",
            "condition": "Fresh local data materially changes the current split, benchmark parity, or error distribution.",
            "expected_effect": "change_next_move",
            "priority": "high",
        },
        {
            "trigger_id": "trigger_incumbent_shift",
            "condition": "A real incumbent or benchmark reference beats the current route under the same contract.",
            "expected_effect": "weaken_current_belief",
            "priority": "high",
        },
        {
            "trigger_id": "trigger_review_pressure",
            "condition": "Operator review, skeptical control, or runtime security opens a new high-severity issue.",
            "expected_effect": "require_review",
            "priority": "medium",
        },
    ]
    if str(result_contract.recommended_next_move.get("direction")) == "new_dataset":
        triggers.append(
            {
                "trigger_id": "trigger_restart_confirmed",
                "condition": "A replacement dataset or materially different objective is confirmed.",
                "expected_effect": "require_restart",
                "priority": "high",
            }
        )
    if _clean_text(benchmark.get("incumbent_name")):
        triggers.append(
            {
                "trigger_id": "trigger_incumbent_recheck",
                "condition": "Updated incumbent parity changes from the current benchmark state.",
                "expected_effect": "change_next_move",
                "priority": "medium",
            }
        )
    return BeliefRevisionTriggersArtifact(
        schema_version=BELIEF_REVISION_TRIGGERS_SCHEMA_VERSION,
        run_id=run_id,
        workspace_id=workspace_id,
        generated_at=_utc_now(),
        triggers=triggers,
        summary=f"Relaytic recorded `{len(triggers)}` explicit belief-revision trigger(s) for this run.",
    )


def _current_beliefs(*, summary_payload: dict[str, Any], handoff_bundle: dict[str, Any], focus_id: str) -> list[dict[str, Any]]:
    decision = dict(summary_payload.get("decision", {}))
    benchmark = dict(summary_payload.get("benchmark", {}))
    route_label = _clean_text(decision.get("selected_route_title")) or _clean_text(decision.get("selected_route_id")) or "current selected route"
    model_family = _clean_text(decision.get("selected_model_family")) or "current selected model"
    beliefs = [
        {
            "belief_id": "belief_route_current_best",
            "statement": f"Relaytic currently believes `{route_label}` with model family `{model_family}` is the best governed answer under the active contract.",
            "scope": "current_run",
            "support_level": _support_level(summary_payload),
            "supporting_evidence_refs": ["run_summary.json", "completion_decision.json", "audit_report.json"],
            "counterevidence_refs": (
                []
                if benchmark_is_reference_competitive(_clean_text(benchmark.get("parity_status")), include_near=True)
                else ["benchmark_gap_report.json"]
            ),
            "applies_if": ["the current objective and dataset relation remain materially the same"],
        },
        {
            "belief_id": "belief_next_direction",
            "statement": f"Relaytic currently believes the best next direction is `{focus_id}` rather than silently continuing without a continuity choice.",
            "scope": "workspace_continuation",
            "support_level": "strong" if focus_id != "same_data" else "moderate",
            "supporting_evidence_refs": ["run_handoff.json", "next_run_options.json", "result_contract.json"],
            "counterevidence_refs": [],
            "applies_if": ["the active continuity framing remains valid"],
        },
    ]
    if _clean_text(benchmark.get("incumbent_name")):
        beliefs.append(
            {
                "belief_id": "belief_incumbent_posture",
                "statement": (
                    f"Relaytic currently believes incumbent posture is `{_clean_text(benchmark.get('incumbent_parity_status')) or 'unknown'}` "
                    f"against `{_clean_text(benchmark.get('incumbent_name'))}`."
                ),
                "scope": "benchmark_challenge",
                "support_level": "moderate",
                "supporting_evidence_refs": ["incumbent_parity_report.json", "beat_target_contract.json"],
                "counterevidence_refs": [],
                "applies_if": ["the incumbent contract remains comparable to the current run"],
            }
        )
    return beliefs


def _unresolved_items(*, summary_payload: dict[str, Any], handoff_bundle: dict[str, Any], action: str) -> list[dict[str, Any]]:
    run_handoff_payload = handoff_bundle.get("run_handoff", {})
    run_handoff = dict(run_handoff_payload) if isinstance(run_handoff_payload, dict) else {}
    unresolved: list[dict[str, Any]] = []
    for idx, statement in enumerate(run_handoff.get("open_questions", []) or [], start=1):
        text = _clean_text(statement)
        if not text:
            continue
        unresolved.append(
            {
                "item_id": f"unresolved_{idx}",
                "statement": text,
                "severity": "medium",
                "kind": "review_gap",
                "resolution_hint": "Review the differentiated result report and choose the next run direction explicitly.",
                "blocking_next_moves": ["pause_for_review"] if action == "pause_for_review" else [],
            }
        )
    if not unresolved and str(summary_payload.get("completion", {}).get("blocking_layer")).strip():
        unresolved.append(
            {
                "item_id": "unresolved_completion_block",
                "statement": f"Relaytic still sees blocking layer `{summary_payload.get('completion', {}).get('blocking_layer')}`.",
                "severity": "high",
                "kind": "decision_gap",
                "resolution_hint": "Inspect completion, control, and benchmark posture before continuing.",
                "blocking_next_moves": ["search_more"],
            }
        )
    return unresolved


def _why_this_move(*, summary_payload: dict[str, Any], focus_id: str, action: str) -> list[dict[str, Any]]:
    evidence = dict(summary_payload.get("evidence", {}))
    benchmark = dict(summary_payload.get("benchmark", {}))
    feasibility = dict(summary_payload.get("feasibility", {}))
    reasons = [
        {
            "reason_type": "continuity",
            "statement": f"Relaytic recommends `{focus_id}` as the next direction under the current continuity contract.",
            "evidence_refs": ["run_handoff.json", "next_run_options.json"],
        },
        {
            "reason_type": "evidence",
            "statement": f"Current readiness is `{evidence.get('readiness_level') or 'unknown'}` and the next bounded action is `{action}`.",
            "evidence_refs": ["audit_report.json", "completion_decision.json"],
        },
    ]
    if _clean_text(feasibility.get("primary_constraint_kind")):
        reasons.append(
            {
                "reason_type": "feasibility",
                "statement": (
                    f"Relaytic also applied feasibility constraint `{_clean_text(feasibility.get('primary_constraint_kind'))}` "
                    f"with deployability `{_clean_text(feasibility.get('deployability')) or 'unknown'}`."
                ),
                "evidence_refs": ["decision_constraint_report.json", "deployability_assessment.json"],
            }
        )
    incumbent = _clean_text(benchmark.get("incumbent_name"))
    if incumbent:
        reasons.append(
            {
                "reason_type": "benchmark",
                "statement": f"Relaytic kept benchmark pressure from incumbent `{incumbent}` visible in the next-step recommendation.",
                "evidence_refs": ["incumbent_parity_report.json", "beat_target_contract.json"],
            }
        )
    return reasons


def _why_not_other_moves(*, selected_direction: str) -> dict[str, Any]:
    payload: dict[str, Any] = {}
    for direction, reason in {
        "same_data": "Relaytic did not choose same-data continuation because the current continuity posture points elsewhere.",
        "add_data": "Relaytic did not choose add-data continuation because the current run can still move without additional local data.",
        "new_dataset": "Relaytic did not recommend a full restart because current beliefs are still useful enough to continue.",
    }.items():
        payload[direction] = {
            "rejected": direction != selected_direction,
            "reason": reason if direction != selected_direction else "This is the current recommended direction.",
            "reconsider_if": (
                "new evidence, benchmark pressure, or user intent changes the continuity posture."
                if direction != selected_direction
                else "already selected"
            ),
        }
    return payload


def _source_artifacts(summary_payload: dict[str, Any]) -> list[str]:
    artifacts = dict(summary_payload.get("artifacts", {}))
    refs: list[str] = []
    for key in (
        "run_summary_path",
        "completion_decision_path",
        "benchmark_parity_report_path",
        "incumbent_parity_report_path",
        "adjudication_scorecard_path",
        "run_handoff_path",
        "next_run_options_path",
        "learnings_state_path",
    ):
        value = _clean_text(artifacts.get(key))
        if value:
            refs.append(Path(value).name if ":" in value or "\\" in value or "/" in value else value)
    return refs


def _update_lineage_runs(
    *,
    existing_runs: list[dict[str, Any]],
    summary_payload: dict[str, Any],
    run_id: str,
    workspace_id: str,
    current_focus: str | None,
) -> list[dict[str, Any]]:
    current = {
        "run_id": run_id,
        "workspace_id": workspace_id,
        "run_dir": str(summary_payload.get("run_dir") or ""),
        "parent_run_id": _parent_run_id(existing_runs),
        "dataset_relation": _dataset_relation(summary_payload=summary_payload, current_focus=current_focus),
        "continuation_reason": _continuation_reason(current_focus),
        "focus": current_focus,
        "status": _clean_text(summary_payload.get("status")) or "ok",
        "stage_completed": _clean_text(summary_payload.get("stage_completed")) or "unknown",
        "added_at": _utc_now(),
    }
    filtered = [item for item in existing_runs if _clean_text(item.get("run_id")) != run_id]
    filtered.append(current)
    return filtered


def _update_focus_events(
    *,
    existing_events: list[dict[str, Any]],
    summary_payload: dict[str, Any],
    run_id: str,
    workspace_id: str,
    current_focus: str | None,
) -> list[dict[str, Any]]:
    if not current_focus:
        return existing_events
    handoff = dict(summary_payload.get("handoff", {}))
    focus_notes = _clean_text(handoff.get("focus_notes"))
    event = {
        "focus_event_id": f"focus_{hashlib.sha1(f'{workspace_id}|{run_id}|{current_focus}'.encode('utf-8')).hexdigest()[:12]}",
        "workspace_id": workspace_id,
        "run_id": run_id,
        "focus": current_focus,
        "selected_by": _clean_text(handoff.get("selected_focus_id")) and "human_or_agent" or "relaytic_recommendation",
        "reason": focus_notes or f"Relaytic kept focus `{current_focus}` visible for the next run contract.",
        "evidence_refs": ["result_contract.json", "next_run_plan.json"],
        "superseded_by_result_contract": run_id,
        "created_at": _utc_now(),
    }
    filtered = [item for item in existing_events if _clean_text(item.get("focus_event_id")) != event["focus_event_id"]]
    filtered.append(event)
    return filtered


def _count_learnings(
    learnings_state: dict[str, Any] | None,
    learnings_snapshot: dict[str, Any] | None,
    *,
    status_values: set[str],
) -> int:
    count = 0
    for payload, key in ((learnings_snapshot or {}, "active_learnings"), (learnings_snapshot or {}, "harvested_learnings"), (learnings_state or {}, "entries")):
        items = payload.get(key, [])
        if not isinstance(items, list):
            continue
        for item in items:
            if not isinstance(item, dict):
                continue
            status = _clean_text(item.get("status")) or "active"
            if status in status_values:
                count += 1
    return count


def _workspace_id_for_dir(workspace_dir: Path) -> str:
    digest = hashlib.sha1(str(workspace_dir).replace("\\", "/").encode("utf-8")).hexdigest()[:12]
    return f"workspace_{digest}"


def _parent_run_id(runs: list[dict[str, Any]]) -> str | None:
    if not runs:
        return None
    return _clean_text(runs[-1].get("run_id"))


def _current_focus(*, summary_payload: dict[str, Any], handoff_bundle: dict[str, Any], result_contract: ResultContractArtifact) -> str | None:
    handoff_payload = handoff_bundle.get("next_run_focus", {})
    run_handoff_payload = handoff_bundle.get("run_handoff", {})
    handoff = dict(handoff_payload) if isinstance(handoff_payload, dict) else {}
    run_handoff = dict(run_handoff_payload) if isinstance(run_handoff_payload, dict) else {}
    return _clean_text(handoff.get("selection_id")) or _clean_text(run_handoff.get("recommended_option_id")) or _clean_text(result_contract.recommended_next_move.get("direction"))


def _continuity_mode(current_focus: str | None) -> str:
    if current_focus == "add_data":
        return "data_expansion"
    if current_focus == "new_dataset":
        return "new_dataset_restart"
    if current_focus == "same_data":
        return "same_data_continuation"
    return "single_run"


def _continuation_reason(current_focus: str | None) -> str:
    return {
        "same_data": "continue_same_data",
        "add_data": "add_data",
        "new_dataset": "start_over",
    }.get(str(current_focus), "continue_same_data")


def _dataset_relation(*, summary_payload: dict[str, Any], current_focus: str | None) -> str:
    if current_focus == "add_data":
        return "same_dataset_with_more_rows"
    if current_focus == "new_dataset":
        objective = _clean_text(summary_payload.get("intent", {}).get("objective")) or ""
        return "new_dataset_same_problem" if objective else "new_dataset_new_problem"
    return "same_primary_dataset"


def _normalize_task_type(task_type: str | None) -> str:
    allowed = {
        "classification",
        "regression",
        "ranking",
        "forecasting",
        "anomaly_detection",
        "data_analysis",
        "benchmark_challenge",
        "mixed",
    }
    return task_type if task_type in allowed else "mixed"


def _active_constraints(summary_payload: dict[str, Any]) -> list[str]:
    constraints = ["local_first", "deterministic_floor", "skeptical_control"]
    if bool(summary_payload.get("runtime", {}).get("semantic_rowless_default")):
        constraints.append("rowless_semantic_default")
    if not bool(summary_payload.get("profiles", {}).get("remote_intelligence_allowed", False)):
        constraints.append("no_remote_truth")
    feasibility = dict(summary_payload.get("feasibility", {}))
    primary_constraint = _clean_text(feasibility.get("primary_constraint_kind"))
    if primary_constraint:
        constraints.append(f"feasibility:{primary_constraint}")
    if bool(feasibility.get("gate_open")):
        constraints.append("review_gate_open")
    budget_posture = _clean_text(summary_payload.get("contracts", {}).get("budget_posture"))
    if budget_posture:
        constraints.append(f"budget:{budget_posture}")
    return constraints


def _support_level(summary_payload: dict[str, Any]) -> str:
    readiness = _clean_text(summary_payload.get("evidence", {}).get("readiness_level"))
    if readiness in {"production_candidate", "high"}:
        return "strong"
    if readiness in {"moderate", "review"}:
        return "moderate"
    if readiness in {"weak", "low"}:
        return "weak"
    return "tentative"


def _overall_strength(*, summary_payload: dict[str, Any], unresolved_items: list[dict[str, Any]]) -> str:
    if any(str(item.get("severity")) == "high" for item in unresolved_items):
        return "low"
    if _support_level(summary_payload) == "strong":
        return "high"
    if _support_level(summary_payload) == "moderate":
        return "medium"
    return "low"


def _overall_confidence(*, summary_payload: dict[str, Any], unresolved_items: list[dict[str, Any]]) -> str:
    if any(str(item.get("severity")) == "high" for item in unresolved_items):
        return "low"
    if _support_level(summary_payload) == "strong":
        return "high"
    return "medium"


def _result_status(*, confidence: str, unresolved_items: list[dict[str, Any]], direction: str) -> str:
    if direction == "new_dataset":
        return "restart_recommended"
    if any(str(item.get("severity")) == "high" for item in unresolved_items):
        return "needs_review"
    if confidence == "high":
        return "actionable"
    if unresolved_items:
        return "provisional"
    return "actionable"


def _primary_metric_value(summary_payload: dict[str, Any]) -> float | None:
    decision = dict(summary_payload.get("decision", {}))
    metric_name = _clean_text(decision.get("primary_metric"))
    if not metric_name:
        return None
    for section_name in ("test", "validation"):
        section = dict(summary_payload.get("metrics", {}).get(section_name, {}))
        value = section.get(metric_name)
        if isinstance(value, (int, float)):
            return float(value)
    return None


def _required_inputs(*, direction: str) -> list[str]:
    if direction == "add_data":
        return ["local_data_path"]
    if direction == "new_dataset":
        return ["new_dataset_path", "fresh_objective_confirmation"]
    return []


def _normalize_action(*, direction: str, action_hint: str | None) -> str:
    mapping = {
        "run_recalibration_pass": "recalibrate",
        "run_retrain_pass": "retrain",
        "refresh_benchmark": "benchmark_incumbent",
        "request_additional_local_data": "collect_more_data",
        "operator_review": "pause_for_review",
        "start_over": "start_fresh",
    }
    if direction == "new_dataset":
        return "start_fresh"
    if direction == "add_data":
        return "collect_more_data"
    normalized = mapping.get(str(action_hint), str(action_hint))
    return normalized or "search_more"


def _clean_text(value: Any) -> str | None:
    text = str(value or "").strip()
    return text or None


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _trace() -> WorkspaceTrace:
    return WorkspaceTrace(
        agent="workspace_continuity_governor",
        operating_mode="deterministic_workspace_continuity",
        llm_used=False,
        llm_status="not_requested",
        deterministic_evidence=["run_summary", "handoff_bundle", "durable_learnings", "trace_evals", "workspace_spec"],
        advisory_notes=[
            "Workspace continuity stays local and explicit.",
            "Human and agent reports are renderings of the same result contract.",
        ],
    )
