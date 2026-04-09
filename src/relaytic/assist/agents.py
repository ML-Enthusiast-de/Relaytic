"""Slice 09E communicative assist planning and rendering."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from .models import (
    ASSISTANT_CONNECTION_GUIDE_SCHEMA_VERSION,
    ASSIST_MODE_SCHEMA_VERSION,
    ASSIST_SESSION_STATE_SCHEMA_VERSION,
    AssistBundle,
    AssistControls,
    AssistModeArtifact,
    AssistSessionStateArtifact,
    AssistTrace,
    AssistantConnectionGuideArtifact,
    build_assist_controls_from_policy,
)


STAGE_ALIASES = {
    "foundation": "foundation",
    "setup": "foundation",
    "intake": "intake",
    "context": "intake",
    "mandate": "intake",
    "investigate": "investigation",
    "investigation": "investigation",
    "scout": "investigation",
    "scientist": "investigation",
    "focus": "investigation",
    "memory": "memory",
    "plan": "planning",
    "planning": "planning",
    "strategist": "planning",
    "builder": "planning",
    "evidence": "evidence",
    "audit": "evidence",
    "challenger": "evidence",
    "ablation": "evidence",
    "intelligence": "intelligence",
    "semantic": "intelligence",
    "debate": "intelligence",
    "research": "research",
    "papers": "research",
    "literature": "research",
    "sota": "research",
    "benchmark": "benchmark",
    "baseline": "benchmark",
    "parity": "benchmark",
    "reference": "benchmark",
    "completion": "completion",
    "status": "completion",
    "lifecycle": "lifecycle",
    "autonomy": "autonomy",
    "runtime": "runtime",
}

NAVIGABLE_STAGES = [
    "intake",
    "investigation",
    "memory",
    "planning",
    "evidence",
    "intelligence",
    "research",
    "benchmark",
    "completion",
    "lifecycle",
    "autonomy",
]


@dataclass(frozen=True)
class AssistIntent:
    intent_type: str
    requested_stage: str | None = None
    wants_takeover: bool = False
    wants_connection_guidance: bool = False
    wants_explanation: bool = False
    next_run_selection: str | None = None
    focus_notes: str | None = None
    reset_learnings_requested: bool = False


@dataclass(frozen=True)
class AssistTurnPlan:
    intent: AssistIntent
    action_kind: str
    requested_stage: str | None
    response_message: str


def build_assist_bundle(
    *,
    policy: dict[str, Any],
    run_summary: dict[str, Any],
    backend_discovery: dict[str, Any] | None,
    interoperability_inventory: dict[str, Any] | None,
    last_user_intent: str | None = None,
    last_requested_stage: str | None = None,
    last_action_kind: str | None = None,
    turn_count: int = 0,
) -> AssistBundle:
    controls = build_assist_controls_from_policy(policy)
    backend_discovery = backend_discovery or {}
    interoperability_inventory = interoperability_inventory or {}
    trace = AssistTrace(
        agent="assist_coordinator",
        operating_mode="deterministic_communicative_surface",
        llm_used=False,
        llm_status="not_requested",
        deterministic_evidence=[
            "run_summary",
            "stage_navigation_rules",
            "backend_discovery_status",
            "host_inventory",
        ],
    )
    current_stage = _clean_text(run_summary.get("stage_completed")) or "unknown"
    next_action = _clean_text(dict(run_summary.get("next_step", {})).get("recommended_action"))
    backend_status = _clean_text(backend_discovery.get("status")) or "unknown"
    backend_provider = _clean_text(backend_discovery.get("resolved_provider"))
    backend_model = _clean_text(backend_discovery.get("resolved_model"))
    host_options = _build_host_options(interoperability_inventory=interoperability_inventory)
    local_options = _build_local_options(
        controls=controls,
        backend_discovery=backend_discovery,
    )
    recommended_path = _recommended_path(
        controls=controls,
        backend_discovery=backend_discovery,
        host_options=host_options,
    )
    generated_at = _utc_now()
    available_actions = _available_actions(controls=controls)
    available_stage_targets = _available_stage_targets(controls=controls)
    suggested_questions = _suggested_questions(
        run_summary=run_summary,
        controls=controls,
        available_stage_targets=available_stage_targets,
    )
    return AssistBundle(
        assist_mode=AssistModeArtifact(
            schema_version=ASSIST_MODE_SCHEMA_VERSION,
            generated_at=generated_at,
            controls=controls,
            enabled=controls.enabled,
            semantic_backend_status=backend_status,
            semantic_backend_provider=backend_provider,
            semantic_backend_model=backend_model,
            takeover_enabled=controls.allow_assistant_takeover,
            host_guidance_available=controls.allow_host_connection_guidance,
            summary=_assist_mode_summary(
                controls=controls,
                backend_status=backend_status,
                backend_provider=backend_provider,
            ),
            trace=trace,
        ),
        assist_session_state=AssistSessionStateArtifact(
            schema_version=ASSIST_SESSION_STATE_SCHEMA_VERSION,
            generated_at=generated_at,
            controls=controls,
            current_stage=current_stage,
            next_recommended_action=next_action,
            takeover_available=controls.allow_assistant_takeover,
            last_user_intent=last_user_intent,
            last_requested_stage=last_requested_stage,
            last_action_kind=last_action_kind,
            turn_count=max(0, int(turn_count or 0)),
            available_actions=available_actions,
            available_stage_targets=available_stage_targets,
            suggested_questions=suggested_questions,
            summary=_session_state_summary(
                current_stage=current_stage,
                next_action=next_action,
                last_action_kind=last_action_kind,
                available_actions=available_actions,
                available_stage_targets=available_stage_targets,
            ),
            trace=trace,
        ),
        assistant_connection_guide=AssistantConnectionGuideArtifact(
            schema_version=ASSISTANT_CONNECTION_GUIDE_SCHEMA_VERSION,
            generated_at=generated_at,
            controls=controls,
            local_options=local_options,
            host_options=host_options,
            recommended_path=recommended_path,
            summary=_connection_guide_summary(recommended_path=recommended_path, host_options=host_options),
            trace=trace,
        ),
    )


def plan_assist_turn(
    *,
    message: str,
    run_summary: dict[str, Any],
    assist_bundle: dict[str, Any] | None = None,
) -> AssistTurnPlan:
    normalized = " ".join(str(message).strip().lower().split())
    requested_stage = _extract_requested_stage(normalized)
    next_run_selection = _extract_next_run_selection(normalized)
    reset_learnings_requested = _looks_like_learnings_reset(normalized)
    intent = AssistIntent(
        intent_type=_intent_type(
            normalized,
            requested_stage=requested_stage,
            next_run_selection=next_run_selection,
        ),
        requested_stage=requested_stage,
        wants_takeover=_looks_like_takeover(normalized),
        wants_connection_guidance=_looks_like_connection_request(normalized),
        wants_explanation=_looks_like_explanation_request(normalized),
        next_run_selection=next_run_selection,
        focus_notes=_clean_text(message) if next_run_selection else None,
        reset_learnings_requested=reset_learnings_requested,
    )
    bundle = assist_bundle or {}
    if intent.intent_type == "connection_guidance":
        response = _build_connection_response(bundle=bundle)
        return AssistTurnPlan(intent=intent, action_kind="respond", requested_stage=requested_stage, response_message=response)
    if intent.intent_type == "capabilities":
        response = _build_capabilities_response(bundle=bundle, run_summary=run_summary)
        return AssistTurnPlan(intent=intent, action_kind="respond", requested_stage=requested_stage, response_message=response)
    if intent.intent_type == "show_workspace":
        return AssistTurnPlan(
            intent=intent,
            action_kind="show_workspace",
            requested_stage=None,
            response_message="Relaytic will show the current workspace continuity, result contract, and next-run plan.",
        )
    if intent.intent_type == "show_handoff":
        return AssistTurnPlan(
            intent=intent,
            action_kind="show_handoff",
            requested_stage=None,
            response_message="Relaytic will show the differentiated result report, the key findings, and the explicit next-run options.",
        )
    if intent.intent_type == "show_learnings":
        return AssistTurnPlan(
            intent=intent,
            action_kind="show_learnings",
            requested_stage=None,
            response_message="Relaytic will show the durable learnings state and the active learnings for this run.",
        )
    if intent.intent_type == "reset_learnings":
        return AssistTurnPlan(
            intent=intent,
            action_kind="reset_learnings",
            requested_stage=None,
            response_message="Relaytic will reset the durable learnings state for this workspace.",
        )
    if intent.intent_type == "focus_next_run":
        if not intent.next_run_selection:
            return AssistTurnPlan(
                intent=intent,
                action_kind="respond",
                requested_stage=None,
                response_message=(
                    "Relaytic can set the next-run focus to `same_data`, `add_data`, or `new_dataset`. "
                    "Say for example `use the same data next time but focus on recall`."
                ),
            )
        return AssistTurnPlan(
            intent=intent,
            action_kind="focus_next_run",
            requested_stage=None,
            response_message=(
                f"Relaytic will save the next-run focus `{intent.next_run_selection}`"
                + (" and reset durable learnings." if intent.reset_learnings_requested else ".")
            ),
        )
    if intent.intent_type == "rerun_stage":
        if requested_stage is None:
            return AssistTurnPlan(
                intent=intent,
                action_kind="respond",
                requested_stage=None,
                response_message=(
                    "Relaytic can jump back to `intake`, `investigation`, `memory`, `planning`, `evidence`, "
                    "`intelligence`, `research`, `benchmark`, `completion`, `lifecycle`, or `autonomy`. "
                    "Say for example `go back to benchmark`."
                ),
            )
        return AssistTurnPlan(
            intent=intent,
            action_kind="rerun_stage",
            requested_stage=requested_stage,
            response_message=f"Relaytic will rerun from `{requested_stage}` and refresh downstream artifacts.",
        )
    if intent.intent_type == "take_over":
        return AssistTurnPlan(
            intent=intent,
            action_kind="take_over",
            requested_stage=None,
            response_message="Relaytic will pick the next safe step and continue from the current run state.",
        )
    if requested_stage:
        response = _build_stage_explanation(stage=requested_stage, run_summary=run_summary)
    else:
        response = _build_general_explanation(run_summary=run_summary)
    return AssistTurnPlan(intent=intent, action_kind="respond", requested_stage=requested_stage, response_message=response)


def render_assist_markdown(bundle: AssistBundle | dict[str, Any]) -> str:
    payload = bundle.to_dict() if isinstance(bundle, AssistBundle) else dict(bundle)
    mode = dict(payload.get("assist_mode", {}))
    state = dict(payload.get("assist_session_state", {}))
    guide = dict(payload.get("assistant_connection_guide", {}))
    lines = [
        "# Relaytic Assist",
        "",
        f"- Current stage: `{state.get('current_stage') or 'unknown'}`",
        f"- Next recommended action: `{state.get('next_recommended_action') or 'none'}`",
        f"- Semantic backend: `{mode.get('semantic_backend_status') or 'unknown'}`",
        f"- Takeover enabled: `{mode.get('takeover_enabled')}`",
        f"- Recommended connection path: `{guide.get('recommended_path') or 'unknown'}`",
    ]
    available_actions = [str(item).strip() for item in state.get("available_actions", []) if str(item).strip()]
    if available_actions:
        lines.extend(["", "## Available Actions"])
        lines.extend(f"- `{item}`" for item in available_actions[:6])
    available_stages = [str(item).strip() for item in state.get("available_stage_targets", []) if str(item).strip()]
    if available_stages:
        lines.extend(["", "## Stage Navigation"])
        lines.append(
            "- Relaytic supports bounded stage reruns, not arbitrary checkpoint time travel yet."
        )
        lines.append(f"- Available stages: `{', '.join(available_stages)}`")
    suggested_questions = [str(item).strip() for item in state.get("suggested_questions", []) if str(item).strip()]
    if suggested_questions:
        lines.extend(["", "## Suggested Questions"])
        lines.extend(f"- `{item}`" for item in suggested_questions[:6])
    local_options = list(guide.get("local_options", []))
    if local_options:
        lines.extend(["", "## Local Options"])
        for item in local_options[:3]:
            lines.append(f"- `{item.get('name')}`: {item.get('summary')}")
    host_options = list(guide.get("host_options", []))
    if host_options:
        lines.extend(["", "## Host Options"])
        for item in host_options[:4]:
            lines.append(
                f"- `{item.get('host')}` ready=`{item.get('discoverable_now')}` activation=`{item.get('requires_activation')}`: {item.get('next_step')}"
            )
    return "\n".join(lines).rstrip() + "\n"


def _intent_type(normalized: str, *, requested_stage: str | None, next_run_selection: str | None) -> str:
    if _looks_like_connection_request(normalized):
        return "connection_guidance"
    if _looks_like_learnings_reset(normalized):
        return "reset_learnings"
    if next_run_selection is not None and _looks_like_next_run_focus_request(normalized, selection_id=next_run_selection):
        return "focus_next_run"
    if _looks_like_workspace_request(normalized) or _looks_like_belief_revision_request(normalized):
        return "show_workspace"
    if _looks_like_handoff_request(normalized):
        return "show_handoff"
    if _looks_like_learnings_request(normalized):
        return "show_learnings"
    if _looks_like_capability_request(normalized):
        return "capabilities"
    if ("why" in normalized or "explain" in normalized) and not (
        normalized.startswith("go back")
        or normalized.startswith("rerun")
        or normalized.startswith("redo")
        or normalized.startswith("restart from")
    ):
        return "explain"
    if _looks_like_stage_rerun(normalized):
        return "rerun_stage"
    if _looks_like_takeover(normalized):
        return "take_over"
    if requested_stage or _looks_like_explanation_request(normalized):
        return "explain"
    return "explain"


def _extract_requested_stage(normalized: str) -> str | None:
    for token, stage in STAGE_ALIASES.items():
        if token in normalized:
            return stage
    return None


def _looks_like_connection_request(normalized: str) -> bool:
    return any(
        token in normalized
        for token in (
            "connect",
            "chatgpt",
            "claude",
            "openclaw",
            "codex",
            "mcp",
            "llm",
            "ollama",
            "llama.cpp",
            "llama_cpp",
            "openai",
        )
    )


def _looks_like_takeover(normalized: str) -> bool:
    return any(
        token in normalized
        for token in (
            "take over",
            "takeover",
            "you decide",
            "do it",
            "continue",
            "proceed",
            "i'm not sure",
            "im not sure",
            "not sure",
            "just do it",
            "handle it",
        )
    )


def _looks_like_stage_rerun(normalized: str) -> bool:
    return any(token in normalized for token in ("go back", "rerun", "redo", "revisit", "restart from"))


def _looks_like_capability_request(normalized: str) -> bool:
    return any(
        token in normalized
        for token in (
            "what can you do",
            "what can i do",
            "capabilities",
            "what are my options",
            "what are the options",
            "what can i ask",
            "how can i steer",
            "help me navigate",
            "help options",
        )
    )


def _looks_like_handoff_request(normalized: str) -> bool:
    return any(
        token in normalized
        for token in (
            "what did you find",
            "what did you find out",
            "show the result report",
            "show the report",
            "show the handoff",
            "result report",
            "handoff",
            "next run options",
            "summarize the findings",
        )
    )


def _looks_like_workspace_request(normalized: str) -> bool:
    return any(
        token in normalized
        for token in (
            "show workspace",
            "show the workspace",
            "workspace",
            "continuity",
            "lineage",
            "next run plan",
            "result contract",
        )
    )


def _looks_like_belief_revision_request(normalized: str) -> bool:
    return any(
        token in normalized
        for token in (
            "what would change your mind",
            "change your mind",
            "belief revision",
            "revision trigger",
            "revision triggers",
            "what could change your mind",
        )
    )


def _looks_like_learnings_request(normalized: str) -> bool:
    return any(
        token in normalized
        for token in (
            "show learnings",
            "what have you learned",
            "what did you learn",
            "durable learnings",
            "learnings.md",
        )
    )


def _looks_like_learnings_reset(normalized: str) -> bool:
    return any(
        token in normalized
        for token in (
            "reset learnings",
            "reset the learnings",
            "clear learnings",
            "clear the learnings",
            "wipe learnings",
            "wipe the learnings",
            "forget the learnings",
            "reset the memory",
            "clear the memory",
            "start from zero next time",
        )
    )


def _extract_next_run_selection(normalized: str) -> str | None:
    if any(token in normalized for token in ("same data", "same dataset", "keep the same data", "use the same data")):
        return "same_data"
    if any(token in normalized for token in ("add data", "more data", "add more data", "bring in more data", "add local data")):
        return "add_data"
    if any(token in normalized for token in ("new dataset", "different dataset", "start over", "new data set")):
        return "new_dataset"
    return None


def _looks_like_next_run_focus_request(normalized: str, *, selection_id: str) -> bool:
    if selection_id in {"same_data", "add_data", "new_dataset"}:
        return True
    return any(token in normalized for token in ("next run", "next time", "focus on", "for the next run"))


def _looks_like_explanation_request(normalized: str) -> bool:
    return any(token in normalized for token in ("why", "explain", "what happened", "status", "show", "summary"))


def _build_general_explanation(*, run_summary: dict[str, Any]) -> str:
    decision = dict(run_summary.get("decision", {}))
    contracts = dict(run_summary.get("contracts", {}))
    model = _clean_text(decision.get("selected_model_family")) or "none"
    metric = _clean_text(decision.get("primary_metric")) or "unknown"
    stage = _clean_text(run_summary.get("stage_completed")) or "unknown"
    next_step = dict(run_summary.get("next_step", {}))
    completion = dict(run_summary.get("completion", {}))
    lifecycle = dict(run_summary.get("lifecycle", {}))
    research = dict(run_summary.get("research", {}))
    benchmark = dict(run_summary.get("benchmark", {}))
    quality_gate = _clean_text(contracts.get("quality_gate_status")) or "unknown"
    budget_health = _clean_text(contracts.get("budget_health")) or "unknown"
    return (
        f"Relaytic is currently at `{stage}`. "
        f"The active model family is `{model}` with primary metric `{metric}`. "
        f"Completion currently points to `{_clean_text(completion.get('action')) or 'none'}`, "
        f"lifecycle currently points to `{_lifecycle_rollup(lifecycle)}`, "
        f"and the next recommended action is `{_clean_text(next_step.get('recommended_action')) or 'none'}`. "
        f"Research follow-up is `{_clean_text(research.get('recommended_followup_action')) or 'none'}` "
        f"benchmark parity is `{_clean_text(benchmark.get('parity_status')) or 'unknown'}`, "
        f"quality gate is `{quality_gate}`, and budget health is `{budget_health}`."
    )


def _build_stage_explanation(*, stage: str, run_summary: dict[str, Any]) -> str:
    if stage == "research":
        research = dict(run_summary.get("research", {}))
        return (
            f"Research currently has status `{_clean_text(research.get('status')) or 'unknown'}` with "
            f"{int(research.get('source_count', 0) or 0)} retrieved sources, "
            f"{int(research.get('accepted_transfer_count', 0) or 0)} accepted transfer candidates, and "
            f"follow-up `{_clean_text(research.get('recommended_followup_action')) or 'none'}`."
        )
    if stage == "benchmark":
        benchmark = dict(run_summary.get("benchmark", {}))
        return (
            f"Benchmark currently has parity status `{_clean_text(benchmark.get('parity_status')) or 'unknown'}` with "
            f"{int(benchmark.get('reference_count', 0) or 0)} reference approach(es), "
            f"comparison metric `{_clean_text(benchmark.get('comparison_metric')) or 'unknown'}`, and "
            f"recommended action `{_clean_text(benchmark.get('recommended_action')) or 'none'}`."
        )
    if stage == "intelligence":
        intelligence = dict(run_summary.get("intelligence", {}))
        return (
            f"Intelligence currently has backend status `{_clean_text(intelligence.get('backend_status')) or 'unknown'}` and "
            f"recommended follow-up `{_clean_text(intelligence.get('recommended_followup_action')) or 'none'}`."
        )
    if stage == "profiles":
        contracts = dict(run_summary.get("contracts", {}))
        profiles = dict(run_summary.get("profiles", {}))
        return (
            f"Profiles currently report quality gate `{_clean_text(contracts.get('quality_gate_status')) or 'unknown'}`, "
            f"recommended action `{_clean_text(contracts.get('quality_recommended_action')) or 'none'}`, "
            f"budget health `{_clean_text(contracts.get('budget_health')) or 'unknown'}`, "
            f"operator profile `{_clean_text(profiles.get('operator_profile_name')) or 'unknown'}`, and "
            f"lab profile `{_clean_text(profiles.get('lab_profile_name')) or 'unknown'}`."
        )
    if stage == "autonomy":
        autonomy = dict(run_summary.get("autonomy", {}))
        return (
            f"Autonomy currently has selected action `{_clean_text(autonomy.get('selected_action')) or 'none'}`, "
            f"promotion applied `{autonomy.get('promotion_applied')}`, and "
            f"{int(autonomy.get('branch_count', 0) or 0)} branch result(s)."
        )
    if stage == "lifecycle":
        lifecycle = dict(run_summary.get("lifecycle", {}))
        return (
            f"Lifecycle currently recommends `{_lifecycle_rollup(lifecycle)}` with "
            f"promotion `{_clean_text(lifecycle.get('promotion_action')) or 'none'}`, "
            f"recalibration `{_clean_text(lifecycle.get('recalibration_action')) or 'none'}`, and "
            f"retrain `{_clean_text(lifecycle.get('retrain_action')) or 'none'}`."
        )
    if stage == "completion":
        completion = dict(run_summary.get("completion", {}))
        return (
            f"Completion currently reports action `{_clean_text(completion.get('action')) or 'none'}`, "
            f"blocking layer `{_clean_text(completion.get('blocking_layer')) or 'none'}`, and "
            f"mandate alignment `{_clean_text(completion.get('mandate_alignment')) or 'unknown'}`."
        )
    return _build_general_explanation(run_summary=run_summary)


def build_assist_audit_explanation(
    *,
    message: str,
    run_summary: dict[str, Any],
    actor_type: str,
) -> dict[str, Any]:
    normalized = " ".join(str(message).strip().lower().split())
    decision = dict(run_summary.get("decision", {}))
    decision_lab = dict(run_summary.get("decision_lab", {}))
    feasibility = dict(run_summary.get("feasibility", {}))
    completion = dict(run_summary.get("completion", {}))
    benchmark = dict(run_summary.get("benchmark", {}))
    result_contract = dict(run_summary.get("result_contract", {}))
    task_contract = dict(run_summary.get("task_contract", {}))
    benchmark_vs_deploy = dict(run_summary.get("benchmark_vs_deploy", {}))
    architecture = dict(run_summary.get("architecture", {}))
    hpo = dict(run_summary.get("hpo", {}))
    next_step = dict(run_summary.get("next_step", {}))
    iteration = dict(run_summary.get("iteration", {}))

    question_type = "general"
    reasons: list[str] = []
    evidence_refs: list[str] = []

    if "what would change your mind" in normalized or "change your mind" in normalized:
        question_type = "belief_revision"
        reasons = [
            "Relaytic will revise its current posture if benchmark parity changes, fresh local data materially changes the error pattern, or review pressure opens a new high-severity issue.",
            f"Current recommended direction is `{_clean_text(result_contract.get('recommended_direction')) or _clean_text(result_contract.get('recommended_action')) or _clean_text(dict(result_contract.get('recommended_next_move', {})).get('direction')) or 'unknown'}` under the workspace contract.",
        ]
        evidence_refs = ["belief_revision_triggers.json", "result_contract.json", "next_run_plan.json"]
    elif "task type" in normalized or ("why not" in normalized and "anomaly" in normalized):
        question_type = "task_semantics"
        reasons = [
            f"Relaytic classified this target as `{_clean_text(task_contract.get('task_type')) or _clean_text(decision.get('task_type')) or 'unknown'}` with posture `{_clean_text(task_contract.get('problem_posture')) or 'unknown'}`.",
            _clean_text(task_contract.get("why_not_anomaly_detection"))
            or "Relaytic did not pick anomaly detection because this run has labeled target states and therefore keeps the problem in a supervised posture.",
            f"Benchmark comparison uses `{_clean_text(task_contract.get('benchmark_comparison_metric')) or _clean_text(benchmark.get('comparison_metric')) or 'unknown'}` while deployment readiness is `{_clean_text(benchmark_vs_deploy.get('deployment_readiness')) or 'unknown'}`.",
        ]
        evidence_refs = [
            "task_profile_contract.json",
            "target_semantics_report.json",
            "metric_contract.json",
            "benchmark_vs_deploy_report.json",
        ]
    elif "why not" in normalized and "rerun" in normalized:
        question_type = "why_not_rerun"
        reasons = [
            _clean_text(feasibility.get("why_not_rerun"))
            or "Relaytic did not pick a rerun because the current feasibility or review posture points to a different bounded next step.",
            f"The selected next action is `{_clean_text(feasibility.get('selected_action')) or _clean_text(next_step.get('recommended_action')) or 'unknown'}`.",
            f"The current constraint kind is `{_clean_text(feasibility.get('primary_constraint_kind')) or 'none'}` and review gate open = `{feasibility.get('gate_open')}`.",
        ]
        evidence_refs = ["counterfactual_region_report.json", "decision_constraint_report.json", "run_summary.json"]
    elif "why not" in normalized and any(token in normalized for token in ("lstm", "transformer", "sequence")):
        question_type = "why_not_sequence_model"
        reasons = [
            _clean_text(architecture.get("sequence_rejection_reason"))
            or "Relaytic kept sequence-native families out of this live run because the task contract does not justify them yet.",
            f"Recommended primary family is `{_clean_text(architecture.get('recommended_primary_family')) or _clean_text(decision.get('selected_model_family')) or 'unknown'}` with candidate order `{', '.join(architecture.get('candidate_order', [])[:4]) or 'unknown'}`.",
            f"Sequence live allowed = `{architecture.get('sequence_live_allowed')}` and shadow ready = `{architecture.get('sequence_shadow_ready')}`.",
        ]
        evidence_refs = [
            "architecture_router_report.json",
            "candidate_family_matrix.json",
            "architecture_fit_report.json",
        ]
    elif "why not" in normalized:
        question_type = "why_not"
        reasons = [
            "Relaytic rejected at least one alternative because the current contract, benchmark posture, or feasibility posture favored the selected action instead.",
            f"Recommended next action is `{_clean_text(feasibility.get('selected_action')) or _clean_text(next_step.get('recommended_action')) or 'unknown'}`.",
        ]
        evidence_refs = ["result_contract.json", "decision_constraint_report.json", "run_summary.json"]
    elif "why" in normalized and "model" in normalized:
        question_type = "model_choice"
        reasons = [
            f"Relaytic selected model family `{_clean_text(decision.get('selected_model_family')) or 'unknown'}` for the active route.",
            f"The route posture is `{_clean_text(decision.get('selected_route_title')) or _clean_text(decision.get('selected_route_id')) or 'unknown'}` with primary metric `{_clean_text(decision.get('primary_metric')) or 'unknown'}`.",
            f"Architecture routing recommended `{_clean_text(architecture.get('recommended_primary_family')) or 'unknown'}` and benchmark parity is `{_clean_text(benchmark.get('parity_status')) or 'unknown'}`.",
        ]
        if int(hpo.get("executed_trial_count", 0) or 0) > 0:
            reasons.append(
                f"Bounded HPO executed `{int(hpo.get('executed_trial_count', 0) or 0)}` trial(s) across `{int(hpo.get('tuned_family_count', 0) or 0)}` tuned family loop(s), with stop reasons `{', '.join(str(item) for item in hpo.get('stop_reasons', []) if str(item).strip()) or 'not recorded'}`."
            )
        evidence_refs = [
            "plan.json",
            "architecture_router_report.json",
            "candidate_family_matrix.json",
            "benchmark_parity_report.json",
        ]
        if int(hpo.get("executed_trial_count", 0) or 0) > 0:
            evidence_refs.extend(
                [
                    "hpo_budget_contract.json",
                    "search_loop_scorecard.json",
                    "threshold_tuning_report.json",
                ]
            )
    elif "why" in normalized and any(token in normalized for token in ("route", "choose", "happen", "selected")):
        question_type = "why_this_happened"
        reasons = [
            f"Relaytic selected next action `{_clean_text(feasibility.get('selected_action')) or _clean_text(decision_lab.get('selected_next_action')) or 'unknown'}` after considering the decision lab, completion, and feasibility layers.",
            f"Completion posture is `{_clean_text(completion.get('action')) or 'unknown'}`, benchmark parity is `{_clean_text(benchmark.get('parity_status')) or 'unknown'}`, and deployability is `{_clean_text(feasibility.get('deployability')) or 'unknown'}`.",
            f"Recommended workspace direction is `{_clean_text(feasibility.get('recommended_direction')) or _clean_text(result_contract.get('recommended_direction')) or _clean_text(dict(result_contract.get('recommended_next_move', {})).get('direction')) or 'unknown'}`.",
        ]
        evidence_refs = ["run_summary.json", "completion_decision.json", "benchmark_parity_report.json", "decision_constraint_report.json"]
    else:
        question_type = "general"
        reasons = [
            _build_general_explanation(run_summary=run_summary),
        ]
        evidence_refs = ["run_summary.json"]

    reasons = [item for item in reasons if _clean_text(item)]
    if actor_type.strip().lower() == "agent":
        answer = " ".join(reasons)
    else:
        answer = " ".join(reasons[:2]) if reasons else _build_general_explanation(run_summary=run_summary)

    return {
        "question_type": question_type,
        "answer": answer,
        "reasons": reasons,
        "evidence_refs": evidence_refs,
        "actor_type": actor_type,
        "llm_enhanced": False,
    }


def _build_connection_response(*, bundle: dict[str, Any]) -> str:
    guide = dict(bundle.get("assistant_connection_guide", {}))
    local_options = list(guide.get("local_options", []))
    host_options = list(guide.get("host_options", []))
    local_bits = "; ".join(
        f"{item.get('name')}: {item.get('summary')}" for item in local_options[:2]
    ) or "No local options recorded."
    host_bits = "; ".join(
        f"{item.get('host')}: {item.get('next_step')}" for item in host_options[:3]
    ) or "No host options recorded."
    return (
        f"Relaytic can stay fully local or plug into host tools. "
        f"Local path: {local_bits}. "
        f"Host path: {host_bits}."
    )


def _build_capabilities_response(*, bundle: dict[str, Any], run_summary: dict[str, Any]) -> str:
    state = dict(bundle.get("assist_session_state", {}))
    available_actions = [str(item).strip() for item in state.get("available_actions", []) if str(item).strip()]
    available_stages = [str(item).strip() for item in state.get("available_stage_targets", []) if str(item).strip()]
    suggested_questions = [str(item).strip() for item in state.get("suggested_questions", []) if str(item).strip()]
    current_stage = _clean_text(state.get("current_stage")) or _clean_text(run_summary.get("stage_completed")) or "unknown"
    action_bits = ", ".join(f"`{item}`" for item in available_actions[:4]) or "`respond`"
    stage_bits = ", ".join(f"`{item}`" for item in available_stages[:6]) or "`none`"
    question_bits = "; ".join(suggested_questions[:3]) or "why did you choose this route?"
    return (
        f"Relaytic is currently at `{current_stage}`. "
        f"You can ask bounded questions, request connection guidance, rerun from bounded stages, or let Relaytic take over safely. "
        f"You can also ask what Relaytic found, inspect the differentiated result reports, inspect the workspace/result contract, choose the next-run focus, or manage durable learnings. "
        f"Available actions now: {action_bits}. "
        f"Bounded stage navigation currently supports: {stage_bits}. "
        f"Relaytic will challenge truth-bearing steering rather than blindly obeying it. "
        f"Good starter questions are: {question_bits}."
    )


def _build_host_options(*, interoperability_inventory: dict[str, Any]) -> list[dict[str, Any]]:
    hosts = interoperability_inventory.get("hosts", [])
    if not isinstance(hosts, list):
        return []
    options: list[dict[str, Any]] = []
    for item in hosts:
        if not isinstance(item, dict):
            continue
        options.append(
            {
                "host": _clean_text(item.get("host")) or "unknown",
                "discoverable_now": bool(item.get("discoverable_now", False)),
                "requires_activation": bool(item.get("requires_activation", False)),
                "requires_public_https": bool(item.get("requires_public_https", False)),
                "next_step": _clean_text(item.get("next_step")) or "No next step provided.",
                "status": _clean_text(item.get("status")) or "unknown",
            }
        )
    return options


def _build_local_options(
    *,
    controls: AssistControls,
    backend_discovery: dict[str, Any],
) -> list[dict[str, Any]]:
    options = [
        {
            "name": "deterministic_local_only",
            "available": True,
            "summary": "No LLM is required. Relaytic can still explain, navigate stages, and take over using local artifacts only.",
            "command": None,
        },
        {
            "name": "ollama_lightweight_local",
            "available": True,
            "summary": "Use a small local chat model through Ollama for more natural assist phrasing while keeping the data local.",
            "command": "relaytic setup-local-llm --provider ollama --install-provider",
        },
        {
            "name": "llama_cpp_lightweight_local",
            "available": True,
            "summary": "Use llama.cpp for a local lightweight assistant endpoint when you want explicit local control.",
            "command": "relaytic setup-local-llm --provider llama_cpp",
        },
    ]
    status = _clean_text(backend_discovery.get("status")) or "unknown"
    provider = _clean_text(backend_discovery.get("resolved_provider"))
    model = _clean_text(backend_discovery.get("resolved_model"))
    endpoint_scope = _clean_text(backend_discovery.get("endpoint_scope")) or "unknown"
    options.insert(
        0,
        {
            "name": "configured_semantic_backend",
            "available": status == "available",
            "summary": (
                f"Current backend status is `{status}`"
                + (f" via `{provider}`" if provider else "")
                + (f" with `{model}`" if model else "")
                + (f" on `{endpoint_scope}` scope." if endpoint_scope else ".")
            ),
            "command": None,
        }
    )
    if not controls.prefer_local_semantic_assist:
        options.append(
            {
                "name": "remote_semantic_optional",
                "available": False,
                "summary": "Remote semantic phrasing is not preferred by the current assist controls.",
                "command": None,
            }
        )
    return options


def _recommended_path(
    *,
    controls: AssistControls,
    backend_discovery: dict[str, Any],
    host_options: list[dict[str, Any]],
) -> str:
    if controls.prefer_local_semantic_assist and _clean_text(backend_discovery.get("status")) == "available":
        if _clean_text(backend_discovery.get("endpoint_scope")) == "local":
            return "local_semantic_backend"
    if any(item.get("discoverable_now") for item in host_options):
        return "host_connected_local_mcp"
    return "deterministic_local_only"


def _assist_mode_summary(*, controls: AssistControls, backend_status: str, backend_provider: str | None) -> str:
    if not controls.enabled:
        return "Relaytic communicative assist is disabled."
    provider_text = f" via `{backend_provider}`" if backend_provider else ""
    return (
        "Relaytic communicative assist is enabled with deterministic explanation and navigation, "
        f"semantic backend status `{backend_status}`{provider_text}, and bounded takeover support."
    )


def _session_state_summary(
    *,
    current_stage: str,
    next_action: str | None,
    last_action_kind: str | None,
    available_actions: list[str],
    available_stage_targets: list[str],
) -> str:
    action_text = ", ".join(available_actions[:4]) if available_actions else "none"
    stage_text = ", ".join(available_stage_targets[:5]) if available_stage_targets else "none"
    return (
        f"Relaytic assist is currently anchored at `{current_stage}` with next action "
        f"`{next_action or 'none'}` and last assist action `{last_action_kind or 'none'}`. "
        f"Available actions: `{action_text}`. Stage navigation: `{stage_text}`."
    )


def _available_actions(*, controls: AssistControls) -> list[str]:
    actions = ["ask_question", "show_workspace"]
    if controls.allow_host_connection_guidance:
        actions.append("connection_guidance")
    if controls.allow_stage_navigation:
        actions.append("rerun_stage")
    if controls.allow_assistant_takeover:
        actions.append("take_over")
    return actions


def _available_stage_targets(*, controls: AssistControls) -> list[str]:
    if not controls.allow_stage_navigation:
        return []
    return list(NAVIGABLE_STAGES)


def _suggested_questions(
    *,
    run_summary: dict[str, Any],
    controls: AssistControls,
    available_stage_targets: list[str],
) -> list[str]:
    questions = [
        "why did you choose this route?",
        "what can you do right now?",
    ]
    benchmark = dict(run_summary.get("benchmark", {}))
    decision_lab = dict(run_summary.get("decision_lab", {}))
    control = dict(run_summary.get("control", {}))
    next_step = dict(run_summary.get("next_step", {}))
    if benchmark.get("incumbent_present"):
        questions.append("why did you or didn't you beat the incumbent?")
    if decision_lab.get("review_required"):
        questions.append("why does the decision lab want review?")
    if control.get("decision"):
        questions.append("why was my steering request challenged?")
    if available_stage_targets:
        default_stage = "benchmark" if "benchmark" in available_stage_targets else available_stage_targets[0]
        questions.append(f"go back to {default_stage}")
    if controls.allow_assistant_takeover:
        questions.append("i'm not sure, take over")
    if _clean_text(next_step.get("recommended_action")):
        questions.append("what should happen next?")
    if dict(run_summary.get("handoff", {})):
        questions.append("what did you find?")
        questions.append("use the same data next time but focus on recall")
    if dict(run_summary.get("learnings", {})):
        questions.append("show learnings")
    if dict(run_summary.get("workspace", {})) or dict(run_summary.get("result_contract", {})):
        questions.append("show the workspace")
        questions.append("what would change your mind?")
    return questions[:6]


def _connection_guide_summary(*, recommended_path: str, host_options: list[dict[str, Any]]) -> str:
    ready_hosts = [str(item.get("host")) for item in host_options if item.get("discoverable_now")]
    if ready_hosts:
        return (
            f"Relaytic recommends `{recommended_path}` and already has host-ready integration for "
            + ", ".join(ready_hosts)
            + "."
        )
    return f"Relaytic recommends `{recommended_path}` and can still operate fully locally without a host connector."


def _lifecycle_rollup(lifecycle: dict[str, Any]) -> str:
    for key in ("promotion_action", "retrain_action", "recalibration_action", "rollback_action"):
        value = _clean_text(lifecycle.get(key))
        if value and value != "none":
            return value
    return "none"


def _clean_text(value: Any) -> str | None:
    text = str(value or "").strip()
    return text or None


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()
