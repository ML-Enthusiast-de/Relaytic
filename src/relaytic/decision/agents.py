"""Slice 10A decision-world reasoning, controller logic, and method compilation."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from relaytic.compiler import build_compiler_outputs
from relaytic.data_fabric import build_data_fabric_outputs

from .models import (
    CONTROLLER_POLICY_SCHEMA_VERSION,
    DECISION_USEFULNESS_REPORT_SCHEMA_VERSION,
    DECISION_WORLD_MODEL_SCHEMA_VERSION,
    HANDOFF_CONTROLLER_REPORT_SCHEMA_VERSION,
    INTERVENTION_POLICY_REPORT_SCHEMA_VERSION,
    ControllerPolicy,
    DecisionBundle,
    DecisionControls,
    DecisionTrace,
    DecisionUsefulnessReport,
    DecisionWorldModel,
    HandoffControllerReport,
    InterventionPolicyReport,
    build_decision_controls_from_policy,
)


VALUE_OF_MORE_DATA_REPORT_SCHEMA_VERSION = "relaytic.value_of_more_data_report.v1"


@dataclass(frozen=True)
class DecisionRunResult:
    """Decision bundle plus human-readable output."""

    bundle: DecisionBundle
    review_markdown: str
    selected_strategy: str
    next_actor: str
    selected_next_action: str
    changed_next_action: bool
    changed_controller_path: bool


def run_decision_review(
    *,
    run_dir: str | Path,
    policy: dict[str, Any],
    context_bundle: dict[str, Any] | None = None,
    investigation_bundle: dict[str, Any] | None = None,
    planning_bundle: dict[str, Any] | None = None,
    memory_bundle: dict[str, Any] | None = None,
    intelligence_bundle: dict[str, Any] | None = None,
    research_bundle: dict[str, Any] | None = None,
    benchmark_bundle: dict[str, Any] | None = None,
    profiles_bundle: dict[str, Any] | None = None,
    control_bundle: dict[str, Any] | None = None,
    completion_bundle: dict[str, Any] | None = None,
    lifecycle_bundle: dict[str, Any] | None = None,
    autonomy_bundle: dict[str, Any] | None = None,
) -> DecisionRunResult:
    controls = build_decision_controls_from_policy(policy)
    context_bundle = context_bundle or {}
    investigation_bundle = investigation_bundle or {}
    planning_bundle = planning_bundle or {}
    memory_bundle = memory_bundle or {}
    intelligence_bundle = intelligence_bundle or {}
    research_bundle = research_bundle or {}
    benchmark_bundle = benchmark_bundle or {}
    profiles_bundle = profiles_bundle or {}
    control_bundle = control_bundle or {}
    completion_bundle = completion_bundle or {}
    lifecycle_bundle = lifecycle_bundle or {}
    autonomy_bundle = autonomy_bundle or {}

    dataset_profile = _bundle_item(investigation_bundle, "dataset_profile")
    plan = _bundle_item(planning_bundle, "plan")
    if not plan:
        raise ValueError("Slice 10A decision review requires executed planning artifacts.")

    trace = _trace()
    decision_world_model = _build_decision_world_model(
        controls=controls,
        trace=trace,
        context_bundle=context_bundle,
        investigation_bundle=investigation_bundle,
        planning_bundle=planning_bundle,
        benchmark_bundle=benchmark_bundle,
        profiles_bundle=profiles_bundle,
        intelligence_bundle=intelligence_bundle,
        research_bundle=research_bundle,
        memory_bundle=memory_bundle,
    )
    source_graph, join_candidate_report, data_acquisition_plan = build_data_fabric_outputs(
        run_dir=run_dir,
        current_data_path=_resolve_current_data_path(run_dir=run_dir, planning_bundle=planning_bundle),
        policy=policy,
        dataset_profile=dataset_profile,
    )
    value_of_more_data_report = _build_value_of_more_data_report(
        controls=controls,
        trace=trace,
        decision_world_model=decision_world_model,
        benchmark_bundle=benchmark_bundle,
        research_bundle=research_bundle,
        intelligence_bundle=intelligence_bundle,
        join_candidate_report=join_candidate_report.to_dict(),
        data_acquisition_plan=data_acquisition_plan.to_dict(),
        profiles_bundle=profiles_bundle,
        control_bundle=control_bundle,
    )
    compiler_report, challenger_templates, feature_hypotheses, benchmark_protocol = build_compiler_outputs(
        policy=policy,
        planning_bundle=planning_bundle,
        investigation_bundle=investigation_bundle,
        research_bundle=research_bundle,
        memory_bundle=memory_bundle,
        benchmark_bundle=benchmark_bundle,
        decision_world_model=decision_world_model.to_dict(),
        join_candidate_report=join_candidate_report.to_dict(),
    )
    controller_policy = _build_controller_policy(
        controls=controls,
        trace=trace,
        decision_world_model=decision_world_model,
        value_of_more_data_report=value_of_more_data_report,
        profiles_bundle=profiles_bundle,
        compiled_challenger_templates=challenger_templates.to_dict(),
    )
    handoff_controller_report = _build_handoff_controller_report(
        controls=controls,
        trace=trace,
        controller_policy=controller_policy,
        completion_bundle=completion_bundle,
        lifecycle_bundle=lifecycle_bundle,
        autonomy_bundle=autonomy_bundle,
        benchmark_bundle=benchmark_bundle,
    )
    intervention_policy_report = _build_intervention_policy_report(
        controls=controls,
        trace=trace,
        control_bundle=control_bundle,
        controller_policy=controller_policy,
    )
    decision_usefulness_report = _build_decision_usefulness_report(
        controls=controls,
        trace=trace,
        decision_world_model=decision_world_model,
        value_of_more_data_report=value_of_more_data_report,
        handoff_controller_report=handoff_controller_report,
        method_compiler_report=compiler_report.to_dict(),
        completion_bundle=completion_bundle,
    )
    bundle = DecisionBundle(
        decision_world_model=decision_world_model,
        controller_policy=controller_policy,
        handoff_controller_report=handoff_controller_report,
        intervention_policy_report=intervention_policy_report,
        decision_usefulness_report=decision_usefulness_report,
        value_of_more_data_report=value_of_more_data_report,
        data_acquisition_plan=data_acquisition_plan,
        source_graph=source_graph,
        join_candidate_report=join_candidate_report,
        method_compiler_report=compiler_report,
        compiled_challenger_templates=challenger_templates,
        compiled_feature_hypotheses=feature_hypotheses,
        compiled_benchmark_protocol=benchmark_protocol,
    )
    return DecisionRunResult(
        bundle=bundle,
        review_markdown=render_decision_review_markdown(bundle.to_dict()),
        selected_strategy=str(value_of_more_data_report.get("selected_strategy") or "hold_current_course"),
        next_actor=controller_policy.next_actor,
        selected_next_action=controller_policy.selected_next_action,
        changed_next_action=decision_usefulness_report.changed_next_action,
        changed_controller_path=decision_usefulness_report.changed_controller_path,
    )


def render_decision_review_markdown(bundle: DecisionBundle | dict[str, Any]) -> str:
    """Render the current Slice 10A artifacts for humans."""

    payload = bundle.to_dict() if isinstance(bundle, DecisionBundle) else dict(bundle)
    world = dict(payload.get("decision_world_model", {}))
    controller = dict(payload.get("controller_policy", {}))
    handoff = dict(payload.get("handoff_controller_report", {}))
    usefulness = dict(payload.get("decision_usefulness_report", {}))
    value_report = dict(payload.get("value_of_more_data_report", {}))
    acquisition = dict(payload.get("data_acquisition_plan", {}))
    join_report = dict(payload.get("join_candidate_report", {}))
    compiler = dict(payload.get("method_compiler_report", {}))
    lines = [
        "# Relaytic Decision Lab",
        "",
        f"- Action regime: `{world.get('action_regime') or 'unknown'}`",
        f"- Threshold posture: `{world.get('threshold_posture') or 'unknown'}`",
        f"- Under-specified: `{world.get('under_specified')}`",
        f"- Selected strategy: `{value_report.get('selected_strategy') or 'unknown'}`",
        f"- Next actor: `{controller.get('next_actor') or 'unknown'}`",
        f"- Selected next action: `{controller.get('selected_next_action') or 'unknown'}`",
        f"- Review required: `{controller.get('review_required')}`",
        f"- Changed next action: `{usefulness.get('changed_next_action')}`",
        f"- Changed controller path: `{handoff.get('changed_controller_path')}`",
        f"- Join candidates: `{join_report.get('candidate_count', 0)}`",
        f"- Compiled challengers: `{compiler.get('compiled_challenger_count', 0)}`",
        f"- Compiled features: `{compiler.get('compiled_feature_count', 0)}`",
    ]
    if acquisition.get("recommended_source_id"):
        lines.append(f"- Recommended local source: `{acquisition.get('recommended_source_id')}`")
    uncertainty_sources = [str(item) for item in world.get("uncertainty_sources", []) if str(item).strip()]
    if uncertainty_sources:
        lines.extend(["", "## Uncertainty"] + [f"- {item}" for item in uncertainty_sources[:6]])
    lines.extend(
        [
            "",
            "## Summary",
            "",
            str(
                usefulness.get("summary")
                or controller.get("summary")
                or world.get("summary")
                or "No decision-lab summary available."
            ),
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def _build_decision_world_model(
    *,
    controls: DecisionControls,
    trace: DecisionTrace,
    context_bundle: dict[str, Any],
    investigation_bundle: dict[str, Any],
    planning_bundle: dict[str, Any],
    benchmark_bundle: dict[str, Any],
    profiles_bundle: dict[str, Any],
    intelligence_bundle: dict[str, Any],
    research_bundle: dict[str, Any],
    memory_bundle: dict[str, Any],
) -> DecisionWorldModel:
    task_brief = _bundle_item(context_bundle, "task_brief")
    domain_memo = _bundle_item(investigation_bundle, "domain_memo")
    dataset_profile = _bundle_item(investigation_bundle, "dataset_profile")
    plan = _bundle_item(planning_bundle, "plan")
    quality_contract = _bundle_item(profiles_bundle, "quality_contract")
    operator_profile = _bundle_item(profiles_bundle, "operator_profile")
    semantic_uncertainty = _bundle_item(intelligence_bundle, "semantic_uncertainty_report")
    research_brief = _bundle_item(research_bundle, "research_brief")
    memory_retrieval = _bundle_item(memory_bundle, "memory_retrieval")
    benchmark_parity = _bundle_item(benchmark_bundle, "benchmark_parity_report")

    task_type = _clean_text(plan.get("task_type")) or _clean_text(task_brief.get("task_type_hint")) or "unknown"
    domain_archetype = (
        _clean_text(domain_memo.get("domain_archetype"))
        or _clean_text(task_brief.get("domain_archetype_hint"))
        or "generic_tabular"
    )
    action_regime = _infer_action_regime(task_type=task_type, domain_archetype=domain_archetype, task_brief=task_brief)
    false_positive_cost_band, false_negative_cost_band, defer_cost_band, delay_cost_band = _cost_bands(
        action_regime=action_regime,
        domain_archetype=domain_archetype,
        task_type=task_type,
        task_brief=task_brief,
    )
    operator_review_capacity = (
        _clean_text(operator_profile.get("review_strictness"))
        or _clean_text(controls.default_operator_review_capacity)
        or "medium"
    )
    uncertainty_sources = _world_uncertainty(
        benchmark_parity=benchmark_parity,
        semantic_uncertainty=semantic_uncertainty,
        research_brief=research_brief,
        memory_retrieval=memory_retrieval,
        dataset_profile=dataset_profile,
        controls=controls,
    )
    under_specified = bool(uncertainty_sources)
    threshold_posture = _threshold_posture(
        action_regime=action_regime,
        false_positive_cost_band=false_positive_cost_band,
        false_negative_cost_band=false_negative_cost_band,
    )
    summary = (
        f"Relaytic modeled this run as `{action_regime}` with `{threshold_posture}` threshold posture "
        f"and `{operator_review_capacity}` review capacity."
    )
    return DecisionWorldModel(
        schema_version=DECISION_WORLD_MODEL_SCHEMA_VERSION,
        generated_at=_utc_now(),
        controls=controls,
        status="provisional" if under_specified else "ok",
        task_type=task_type,
        domain_archetype=domain_archetype,
        action_regime=action_regime,
        false_positive_cost_band=false_positive_cost_band,
        false_negative_cost_band=false_negative_cost_band,
        defer_cost_band=defer_cost_band,
        delay_cost_band=delay_cost_band,
        operator_review_capacity=operator_review_capacity,
        abstention_allowed=bool(dict(quality_contract.get("acceptance_criteria", {})) or True),
        under_specified=under_specified,
        uncertainty_sources=uncertainty_sources,
        primary_decision_question=_primary_decision_question(
            action_regime=action_regime,
            task_type=task_type,
            task_brief=task_brief,
        ),
        threshold_posture=threshold_posture,
        summary=summary,
        trace=trace,
    )


def _build_value_of_more_data_report(
    *,
    controls: DecisionControls,
    trace: DecisionTrace,
    decision_world_model: DecisionWorldModel,
    benchmark_bundle: dict[str, Any],
    research_bundle: dict[str, Any],
    intelligence_bundle: dict[str, Any],
    join_candidate_report: dict[str, Any],
    data_acquisition_plan: dict[str, Any],
    profiles_bundle: dict[str, Any],
    control_bundle: dict[str, Any],
) -> dict[str, Any]:
    benchmark_parity = _bundle_item(benchmark_bundle, "benchmark_parity_report")
    benchmark_gap = _bundle_item(benchmark_bundle, "benchmark_gap_report")
    research_brief = _bundle_item(research_bundle, "research_brief")
    semantic_debate = _bundle_item(intelligence_bundle, "semantic_debate_report")
    quality_gate = _bundle_item(profiles_bundle, "quality_gate_report")
    override_decision = _bundle_item(control_bundle, "override_decision")
    candidates = list(join_candidate_report.get("candidates", []))
    recommended_data_path = _clean_text(data_acquisition_plan.get("recommended_data_path"))

    more_data_value_band = "low"
    if candidates and decision_world_model.action_regime in {"human_review_queue", "triage_and_intervention"}:
        more_data_value_band = "high"
    elif candidates or decision_world_model.under_specified:
        more_data_value_band = "medium"

    parity_status = _clean_text(benchmark_parity.get("parity_status"))
    benchmark_action = _clean_text(benchmark_parity.get("recommended_action"))
    more_search_value_band = "low"
    if parity_status not in {"at_parity", "better_than_reference"} or benchmark_action in {
        "broaden_search",
        "continue_experimentation",
        "benchmark_needed",
    }:
        more_search_value_band = "high"
    elif _clean_text(research_brief.get("recommended_followup_action")) in {"expand_challenger_portfolio", "benchmark_needed"}:
        more_search_value_band = "medium"

    more_review_value_band = "low"
    if decision_world_model.action_regime == "human_review_queue":
        more_review_value_band = "high" if decision_world_model.under_specified else "medium"
    if _clean_text(override_decision.get("decision")) in {"defer", "accept_with_modification"}:
        more_review_value_band = "high"
    if _clean_text(quality_gate.get("gate_status")) == "fail":
        more_review_value_band = "high"

    strategy = "hold_current_course"
    if _band_rank(more_data_value_band) > max(_band_rank(more_search_value_band), _band_rank(more_review_value_band)) and recommended_data_path:
        strategy = "additional_local_data"
    elif _band_rank(more_search_value_band) >= max(_band_rank(more_data_value_band), _band_rank(more_review_value_band)) and _band_rank(more_search_value_band) >= 2:
        strategy = "broader_search"
    elif _band_rank(more_review_value_band) >= max(_band_rank(more_data_value_band), _band_rank(more_search_value_band)) and _band_rank(more_review_value_band) >= 2:
        strategy = "operator_review"

    return {
        "schema_version": VALUE_OF_MORE_DATA_REPORT_SCHEMA_VERSION,
        "generated_at": _utc_now(),
        "controls": controls.to_dict(),
        "status": "ok",
        "selected_strategy": strategy,
        "more_data_value_band": more_data_value_band,
        "more_search_value_band": more_search_value_band,
        "more_review_value_band": more_review_value_band,
        "recommended_data_path": recommended_data_path,
        "recommended_join_candidate_id": _clean_text(data_acquisition_plan.get("recommended_join_candidate_id")),
        "benchmark_action": benchmark_action,
        "parity_status": parity_status,
        "reasons": _value_reasons(
            strategy=strategy,
            decision_world_model=decision_world_model,
            benchmark_gap=benchmark_gap,
            semantic_debate=semantic_debate,
            candidates=candidates,
        ),
        "summary": _value_summary(strategy=strategy, recommended_data_path=recommended_data_path),
        "trace": trace.to_dict(),
    }


def _build_controller_policy(
    *,
    controls: DecisionControls,
    trace: DecisionTrace,
    decision_world_model: DecisionWorldModel,
    value_of_more_data_report: dict[str, Any],
    profiles_bundle: dict[str, Any],
    compiled_challenger_templates: dict[str, Any],
) -> ControllerPolicy:
    lab_profile = _bundle_item(profiles_bundle, "lab_operating_profile")
    strategy = _clean_text(value_of_more_data_report.get("selected_strategy")) or "hold_current_course"
    next_actor = {
        "additional_local_data": "relaytic_data_fabric",
        "broader_search": "relaytic_autonomy",
        "operator_review": "operator_review",
        "hold_current_course": "relaytic_completion",
    }.get(strategy, "relaytic_completion")
    selected_next_action = {
        "additional_local_data": "acquire_local_data",
        "broader_search": "expand_challenger_portfolio",
        "operator_review": "request_operator_review",
        "hold_current_course": "hold_current_route",
    }.get(strategy, "hold_current_route")
    review_required = strategy == "operator_review" or decision_world_model.action_regime == "human_review_queue"
    keep_work_local = bool(lab_profile.get("local_truth_required", True)) or strategy == "additional_local_data"
    branch_depth_budget = 2 if strategy == "broader_search" and compiled_challenger_templates.get("templates") else 1
    controller_mode = {
        "additional_local_data": "local_data_expansion",
        "broader_search": "bounded_search_controller",
        "operator_review": "review_gate",
        "hold_current_course": "steady_state",
    }.get(strategy, "steady_state")
    return ControllerPolicy(
        schema_version=CONTROLLER_POLICY_SCHEMA_VERSION,
        generated_at=_utc_now(),
        controls=controls,
        status="ok",
        next_actor=next_actor,
        controller_mode=controller_mode,
        review_required=review_required,
        keep_work_local=keep_work_local,
        branch_depth_budget=branch_depth_budget,
        selected_next_action=selected_next_action,
        specialist_order=_specialist_order(strategy=strategy, review_required=review_required),
        summary=(
            f"Relaytic set controller mode `{controller_mode}` so `{next_actor}` should execute `{selected_next_action}` next."
        ),
        trace=trace,
    )


def _build_handoff_controller_report(
    *,
    controls: DecisionControls,
    trace: DecisionTrace,
    controller_policy: ControllerPolicy,
    completion_bundle: dict[str, Any],
    lifecycle_bundle: dict[str, Any],
    autonomy_bundle: dict[str, Any],
    benchmark_bundle: dict[str, Any],
) -> HandoffControllerReport:
    baseline_action, baseline_actor = _baseline_action(
        completion_bundle=completion_bundle,
        lifecycle_bundle=lifecycle_bundle,
        autonomy_bundle=autonomy_bundle,
        benchmark_bundle=benchmark_bundle,
    )
    selected_action = controller_policy.selected_next_action
    selected_actor = controller_policy.next_actor
    changed_controller_path = (baseline_action or "none") != selected_action or baseline_actor != selected_actor
    return HandoffControllerReport(
        schema_version=HANDOFF_CONTROLLER_REPORT_SCHEMA_VERSION,
        generated_at=_utc_now(),
        controls=controls,
        status="ok",
        baseline_action=baseline_action,
        baseline_actor=baseline_actor,
        selected_action=selected_action,
        selected_actor=selected_actor,
        changed_controller_path=changed_controller_path,
        reviewer_involvement="required" if controller_policy.review_required else "none",
        reasons=_dedupe_strings(
            [
                "controller_selected_different_actor" if baseline_actor != selected_actor else "",
                "controller_selected_different_action" if (baseline_action or "none") != selected_action else "",
                "review_required" if controller_policy.review_required else "",
                "keep_work_local" if controller_policy.keep_work_local else "",
            ]
        ),
        summary=(
            f"Relaytic compared baseline `{baseline_actor}:{baseline_action or 'none'}` against "
            f"`{selected_actor}:{selected_action}` and {'changed' if changed_controller_path else 'kept'} the acting path."
        ),
        trace=trace,
    )


def _build_intervention_policy_report(
    *,
    controls: DecisionControls,
    trace: DecisionTrace,
    control_bundle: dict[str, Any],
    controller_policy: ControllerPolicy,
) -> InterventionPolicyReport:
    override_decision = _bundle_item(control_bundle, "override_decision")
    challenge_report = _bundle_item(control_bundle, "control_challenge_report")
    recovery_checkpoint = _bundle_item(control_bundle, "recovery_checkpoint")
    control_decision = _clean_text(override_decision.get("decision")) or "no_intervention"
    skeptical_bias_level = _clean_text(challenge_report.get("skepticism_level")) or "moderate"
    if control_decision == "rejected":
        override_posture = "reject_override"
        steering_confidence = "high"
    elif control_decision == "accept_with_modification":
        override_posture = "skeptical_accept"
        steering_confidence = "medium"
    elif control_decision == "defer":
        override_posture = "defer_until_review"
        steering_confidence = "medium"
    else:
        override_posture = "steady_state"
        steering_confidence = "medium" if controller_policy.review_required else "high"
    return InterventionPolicyReport(
        schema_version=INTERVENTION_POLICY_REPORT_SCHEMA_VERSION,
        generated_at=_utc_now(),
        controls=controls,
        status="ok",
        control_decision=control_decision,
        override_posture=override_posture,
        checkpoint_required=bool(recovery_checkpoint.get("checkpoint_id")),
        skeptical_bias_level=skeptical_bias_level,
        steering_confidence=steering_confidence,
        summary=(
            f"Relaytic carried forward `{override_posture}` intervention posture with `{skeptical_bias_level}` skepticism."
        ),
        trace=trace,
    )


def _build_decision_usefulness_report(
    *,
    controls: DecisionControls,
    trace: DecisionTrace,
    decision_world_model: DecisionWorldModel,
    value_of_more_data_report: dict[str, Any],
    handoff_controller_report: HandoffControllerReport,
    method_compiler_report: dict[str, Any],
    completion_bundle: dict[str, Any],
) -> DecisionUsefulnessReport:
    completion_decision = _bundle_item(completion_bundle, "completion_decision")
    selected_strategy = _clean_text(value_of_more_data_report.get("selected_strategy")) or "hold_current_course"
    completion_action = _clean_text(completion_decision.get("action"))
    changed_next_action = _normalized_action(completion_action) != _normalized_action(handoff_controller_report.selected_action)
    changed_judgment = decision_world_model.threshold_posture != "balanced_auto_threshold" or selected_strategy != "hold_current_course"
    usefulness_sources = _dedupe_strings(
        [
            "decision_world_model",
            "value_of_more_data" if selected_strategy != "hold_current_course" else "",
            "controller_path_change" if handoff_controller_report.changed_controller_path else "",
            "compiled_methods" if int(method_compiler_report.get("compiled_challenger_count", 0) or 0) > 0 else "",
        ]
    )
    return DecisionUsefulnessReport(
        schema_version=DECISION_USEFULNESS_REPORT_SCHEMA_VERSION,
        generated_at=_utc_now(),
        controls=controls,
        status="ok",
        changed_judgment=changed_judgment,
        changed_next_action=changed_next_action,
        changed_controller_path=handoff_controller_report.changed_controller_path,
        usefulness_sources=usefulness_sources,
        selected_strategy=selected_strategy,
        summary=(
            f"Relaytic {'changed' if changed_next_action else 'retained'} the next-step action and "
            f"{'changed' if handoff_controller_report.changed_controller_path else 'retained'} the acting path."
        ),
        trace=trace,
    )


def _resolve_current_data_path(*, run_dir: str | Path, planning_bundle: dict[str, Any]) -> str | None:
    root = Path(run_dir)
    staged_candidates = sorted((root / "data_copies").glob("primary_*"))
    if staged_candidates:
        return str(staged_candidates[-1])
    plan = _bundle_item(planning_bundle, "plan")
    for value in list(dict(plan.get("builder_handoff") or {}).get("data_references", [])):
        text = _clean_text(value)
        if text:
            return text
    return None


def _infer_action_regime(*, task_type: str, domain_archetype: str, task_brief: dict[str, Any]) -> str:
    text = " ".join(
        item
        for item in (
            task_type,
            domain_archetype,
            _clean_text(task_brief.get("problem_statement")),
            _clean_text(task_brief.get("domain_archetype_hint")),
        )
        if item
    ).lower()
    if any(token in text for token in ("fraud", "risk", "compliance", "bank", "anomaly", "regulated", "legal", "kyc")):
        return "human_review_queue"
    if any(token in text for token in ("maintenance", "monitor", "failure", "outage", "alert", "telemetry", "time_series")):
        return "triage_and_intervention"
    if "regression" in text or task_type == "regression":
        return "decision_support"
    return "assisted_automation"


def _cost_bands(
    *,
    action_regime: str,
    domain_archetype: str,
    task_type: str,
    task_brief: dict[str, Any],
) -> tuple[str, str, str, str]:
    text = " ".join(item for item in (action_regime, domain_archetype, task_type, _clean_text(task_brief.get("problem_statement"))) if item).lower()
    false_positive = "medium"
    false_negative = "medium"
    defer_cost = "medium"
    delay_cost = "medium"
    if any(token in text for token in ("fraud", "anomaly", "maintenance", "safety", "medical", "failure")):
        false_negative = "high"
        delay_cost = "high"
    if any(token in text for token in ("compliance", "legal", "precision", "kyc")):
        false_positive = "high"
    if action_regime == "human_review_queue":
        defer_cost = "low"
        false_positive = "high" if false_positive == "medium" else false_positive
    elif action_regime == "decision_support":
        delay_cost = "low" if delay_cost == "medium" else delay_cost
    return false_positive, false_negative, defer_cost, delay_cost


def _world_uncertainty(
    *,
    benchmark_parity: dict[str, Any],
    semantic_uncertainty: dict[str, Any],
    research_brief: dict[str, Any],
    memory_retrieval: dict[str, Any],
    dataset_profile: dict[str, Any],
    controls: DecisionControls,
) -> list[str]:
    issues: list[str] = []
    if not benchmark_parity:
        issues.append("benchmark parity not yet established")
    elif _clean_text(benchmark_parity.get("parity_status")) not in {"at_parity", "better_than_reference"}:
        issues.append("benchmark parity remains open")
    issues.extend([str(item).strip() for item in semantic_uncertainty.get("unresolved_items", []) if str(item).strip()][:3])
    if not research_brief:
        issues.append("no research brief available")
    if int(memory_retrieval.get("selected_analog_count", 0) or 0) == 0:
        issues.append("no strong analog memory support")
    if int(dataset_profile.get("row_count", 0) or 0) < 150:
        issues.append("small-sample decision environment")
    if not controls.allow_provisional_world_model and issues:
        return issues[:6]
    return _dedupe_strings(issues)[:6]


def _threshold_posture(*, action_regime: str, false_positive_cost_band: str, false_negative_cost_band: str) -> str:
    if action_regime == "human_review_queue":
        if false_positive_cost_band == "high":
            return "favor_precision_with_review"
        return "favor_recall_with_review"
    if false_negative_cost_band == "high":
        return "favor_recall"
    if false_positive_cost_band == "high":
        return "favor_precision"
    if action_regime == "decision_support":
        return "calibrated_decision_support"
    return "balanced_auto_threshold"


def _primary_decision_question(*, action_regime: str, task_type: str, task_brief: dict[str, Any]) -> str:
    if action_regime == "human_review_queue":
        return "Which cases deserve operator review versus automated handling under bounded risk?"
    if action_regime == "triage_and_intervention":
        return "Which cases should be triaged or acted on first under delay-sensitive conditions?"
    if task_type == "regression":
        return "How should this prediction support a downstream decision rather than act as a final rule?"
    return _clean_text(task_brief.get("problem_statement")) or "What is the most useful next decision under the current evidence?"


def _value_reasons(
    *,
    strategy: str,
    decision_world_model: DecisionWorldModel,
    benchmark_gap: dict[str, Any],
    semantic_debate: dict[str, Any],
    candidates: list[dict[str, Any]],
) -> list[str]:
    return _dedupe_strings(
        [
            "decision_world_model" if decision_world_model else "",
            "benchmark_gap_open" if benchmark_gap and benchmark_gap.get("near_parity") is False else "",
            "semantic_followup" if _clean_text(semantic_debate.get("recommended_followup_action")) else "",
            "local_join_candidates" if candidates else "",
            f"selected_{strategy}" if strategy else "",
        ]
    )


def _value_summary(*, strategy: str, recommended_data_path: str | None) -> str:
    if strategy == "additional_local_data":
        return (
            f"Relaytic judged additional local data more valuable than broader search and recommended `{recommended_data_path or 'a nearby local source'}`."
        )
    if strategy == "broader_search":
        return "Relaytic judged broader challenger search more valuable than local data expansion on the current evidence."
    if strategy == "operator_review":
        return "Relaytic judged operator review more valuable than additional search or local data expansion."
    return "Relaytic judged the current route stable enough to hold course unless new evidence arrives."


def _specialist_order(*, strategy: str, review_required: bool) -> list[str]:
    if strategy == "additional_local_data":
        return ["data_fabric_agent", "strategist_agent", "autonomy_controller"]
    if strategy == "broader_search":
        return ["method_compiler_agent", "autonomy_controller", "benchmark_agent"]
    if review_required:
        return ["operator_review", "completion_governor", "lifecycle_governor"]
    return ["completion_governor", "lifecycle_governor"]


def _baseline_action(
    *,
    completion_bundle: dict[str, Any],
    lifecycle_bundle: dict[str, Any],
    autonomy_bundle: dict[str, Any],
    benchmark_bundle: dict[str, Any],
) -> tuple[str | None, str]:
    autonomy_state = _bundle_item(autonomy_bundle, "autonomy_loop_state")
    if autonomy_state:
        return _normalized_action(_clean_text(autonomy_state.get("selected_action"))), "autonomy_controller"
    for key in ("rollback_decision", "retrain_decision", "recalibration_decision", "promotion_decision"):
        action = _clean_text(_bundle_item(lifecycle_bundle, key).get("action"))
        normalized = _normalized_action(action)
        if normalized and normalized not in {"no_rollback", "no_retrain", "no_recalibration", "promote"}:
            return normalized, "lifecycle_governor"
    benchmark_action = _normalized_action(_clean_text(_bundle_item(benchmark_bundle, "benchmark_parity_report").get("recommended_action")))
    if benchmark_action:
        return benchmark_action, "benchmark_agent"
    completion_action = _normalized_action(_clean_text(_bundle_item(completion_bundle, "completion_decision").get("action")))
    return completion_action, "completion_governor"


def _normalized_action(action: str | None) -> str | None:
    mapping = {
        "retrain": "expand_challenger_portfolio",
        "retrain_candidate": "expand_challenger_portfolio",
        "review_challenger": "expand_challenger_portfolio",
        "continue_experimentation": "expand_challenger_portfolio",
        "memory_support_needed": "expand_challenger_portfolio",
        "benchmark_needed": "expand_challenger_portfolio",
        "broaden_search": "expand_challenger_portfolio",
        "recalibrate": "run_recalibration_pass",
        "recalibration_candidate": "run_recalibration_pass",
        "collect_more_data": "acquire_local_data",
        "hold_current_route": "hold_current_route",
    }
    normalized = _clean_text(action)
    if not normalized:
        return None
    return mapping.get(normalized, normalized)


def _band_rank(value: str | None) -> int:
    return {"low": 1, "medium": 2, "high": 3}.get(str(value or "").strip().lower(), 0)


def _trace() -> DecisionTrace:
    return DecisionTrace(
        agent="decision_lab",
        operating_mode="decision_world_model_and_controller_reasoning",
        llm_used=False,
        llm_status="not_requested",
        deterministic_evidence=[
            "benchmark_context",
            "profiles_contracts",
            "control_contracts",
            "memory_priors",
            "research_transfer",
            "local_source_graph",
        ],
    )


def _bundle_item(bundle: dict[str, Any] | None, key: str) -> dict[str, Any]:
    if not isinstance(bundle, dict):
        return {}
    payload = bundle.get(key, {})
    return dict(payload) if isinstance(payload, dict) else {}


def _clean_text(value: Any) -> str | None:
    text = str(value or "").strip()
    return text or None


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


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()
