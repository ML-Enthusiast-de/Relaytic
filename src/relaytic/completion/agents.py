"""Slice 07 completion-governor pipeline."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any

from .models import (
    BLOCKING_ANALYSIS_SCHEMA_VERSION,
    COMPLETION_DECISION_SCHEMA_VERSION,
    MANDATE_EVIDENCE_REVIEW_SCHEMA_VERSION,
    NEXT_ACTION_QUEUE_SCHEMA_VERSION,
    RUN_STATE_SCHEMA_VERSION,
    STAGE_TIMELINE_SCHEMA_VERSION,
    BlockingAnalysis,
    CompletionBundle,
    CompletionControls,
    CompletionDecision,
    CompletionTrace,
    MandateEvidenceReview,
    NextActionQueue,
    RunState,
    StageTimeline,
    build_completion_controls_from_policy,
)
from .semantic import CompletionLocalAdvisor, build_local_advisor


@dataclass(frozen=True)
class CompletionRunResult:
    """Completion artifacts plus human-readable status output."""

    bundle: CompletionBundle
    review_markdown: str


@dataclass(frozen=True)
class _StateFrame:
    """Internal state snapshot used by the governor."""

    current_stage: str
    previous_stage: str | None
    executed_stages: list[str]
    artifact_presence: dict[str, bool]
    stages: list[dict[str, Any]]


class StateTrackerAgent:
    """Builds visible run-state and stage-timeline artifacts."""

    def __init__(self, *, controls: CompletionControls) -> None:
        self.controls = controls

    def run(
        self,
        *,
        run_dir: str | Path,
        mandate_bundle: dict[str, Any],
        context_bundle: dict[str, Any],
        intake_bundle: dict[str, Any],
        investigation_bundle: dict[str, Any],
        planning_bundle: dict[str, Any],
        evidence_bundle: dict[str, Any],
        memory_bundle: dict[str, Any] | None = None,
        intelligence_bundle: dict[str, Any] | None = None,
        completion_bundle: dict[str, Any] | None = None,
    ) -> tuple[_StateFrame, CompletionTrace]:
        memory_bundle = memory_bundle or {}
        intelligence_bundle = intelligence_bundle or {}
        root = Path(run_dir)
        artifact_presence = {
            "foundation": bool(mandate_bundle) and bool(context_bundle),
            "intake": bool(intake_bundle),
            "investigation": bool(investigation_bundle),
            "planning": bool(_bundle_item(planning_bundle, "plan")),
            "execution": bool(dict(_bundle_item(planning_bundle, "plan").get("execution_summary") or {})),
            "memory": bool(memory_bundle),
            "evidence": bool(evidence_bundle),
            "intelligence": bool(intelligence_bundle),
            "completion": True,
        }
        stage_specs = [
            ("foundation_ready", artifact_presence["foundation"], "run_brief.json", _artifact_time(root / "run_brief.json", mandate_bundle.get("run_brief"))),
            ("intake_interpreted", artifact_presence["intake"], "intake_record.json", _artifact_time(root / "intake_record.json", intake_bundle.get("intake_record"))),
            ("investigation_ready", artifact_presence["investigation"], "focus_profile.json", _artifact_time(root / "focus_profile.json", investigation_bundle.get("focus_profile"))),
            ("planning_ready", artifact_presence["planning"], "plan.json", _artifact_time(root / "plan.json", planning_bundle.get("plan"))),
            ("route_executed", artifact_presence["execution"], "model_params.json", _artifact_time(root / "model_params.json", _read_json(root / "model_params.json"))),
            ("memory_retrieved", artifact_presence["memory"], "memory_retrieval.json", _artifact_time(root / "memory_retrieval.json", memory_bundle.get("memory_retrieval"))),
            ("evidence_reviewed", artifact_presence["evidence"], "audit_report.json", _artifact_time(root / "audit_report.json", evidence_bundle.get("audit_report"))),
            ("intelligence_reviewed", artifact_presence["intelligence"], "semantic_debate_report.json", _artifact_time(root / "semantic_debate_report.json", intelligence_bundle.get("semantic_debate_report"))),
        ]
        stages = [
            {
                "stage": name,
                "status": "completed",
                "source_artifact": artifact,
                "generated_at": stamp,
            }
            for name, present, artifact, stamp in stage_specs
            if present
        ]
        previous_stage = stages[-1]["stage"] if stages else None
        current_stage = "completion_reviewed"
        stages.append(
            {
                "stage": current_stage,
                "status": "completed",
                "source_artifact": "completion_decision.json",
                "generated_at": _utc_now(),
            }
        )
        trace = CompletionTrace(
            agent="state_tracker_agent",
            operating_mode="deterministic_only",
            llm_used=False,
            llm_status="not_requested",
            deterministic_evidence=[
                "artifact_presence_scan",
                "generated_at_resolution",
                "stage_order_contract",
            ],
        )
        return (
            _StateFrame(
                current_stage=current_stage,
                previous_stage=previous_stage,
                executed_stages=[item["stage"] for item in stages],
                artifact_presence=artifact_presence,
                stages=stages,
            ),
            trace,
        )


class MandateReviewAgent:
    """Checks alignment between mandate/context intent and current run evidence."""

    def __init__(self, *, controls: CompletionControls) -> None:
        self.controls = controls

    def run(
        self,
        *,
        mandate_bundle: dict[str, Any],
        context_bundle: dict[str, Any],
        intake_bundle: dict[str, Any],
        planning_bundle: dict[str, Any],
        evidence_bundle: dict[str, Any],
    ) -> tuple[dict[str, Any], CompletionTrace]:
        run_brief = _bundle_item(mandate_bundle, "run_brief")
        lab_mandate = _bundle_item(mandate_bundle, "lab_mandate")
        task_brief = _bundle_item(context_bundle, "task_brief")
        domain_brief = _bundle_item(context_bundle, "domain_brief")
        plan = _bundle_item(planning_bundle, "plan")
        audit_report = _bundle_item(evidence_bundle, "audit_report")
        clarification_queue = _bundle_item(intake_bundle, "clarification_queue")
        assumption_log = _bundle_item(intake_bundle, "assumption_log")

        expected_target = (
            str(task_brief.get("target_column", "")).strip()
            or str(run_brief.get("target_column", "")).strip()
        )
        selected_target = str(plan.get("target_column", "")).strip()
        target_alignment = "agree"
        if expected_target and selected_target and expected_target != selected_target:
            target_alignment = "conflict"
        elif expected_target and not selected_target:
            target_alignment = "unresolved"

        feature_columns = [str(item).strip() for item in plan.get("feature_columns", []) if str(item).strip()]
        forbidden_features = _dedupe_strings(
            _string_list(domain_brief.get("forbidden_features"))
            + _extract_forbidden_hints(run_brief)
            + _extract_forbidden_hints(lab_mandate)
        )
        binding_checks: list[dict[str, Any]] = []
        for name in forbidden_features:
            violated = name in feature_columns or _constraint_matches_columns(name, feature_columns)
            binding_checks.append(
                {
                    "constraint": name,
                    "status": "violated" if violated else "satisfied",
                    "source": "forbidden_feature",
                }
            )
        for constraint in _string_list(lab_mandate.get("hard_constraints")) + _string_list(run_brief.get("binding_constraints")):
            if "local" in constraint.lower() or "remote" in constraint.lower() or "cloud" in constraint.lower():
                binding_checks.append(
                    {
                        "constraint": constraint,
                        "status": "satisfied",
                        "source": "operating_constraint",
                    }
                )

        objective_alignment = "agree" if str(plan.get("primary_metric", "")).strip() else "unresolved"
        if audit_report and str(audit_report.get("provisional_recommendation", "")).strip() in {
            "review_challenger_before_promotion",
            "hold_for_data_refresh",
            "continue_experimentation",
        }:
            objective_alignment = "unresolved"

        violated_checks = [item for item in binding_checks if item["status"] == "violated"]
        assumption_count = len(list(assumption_log.get("entries", [])))
        active_clarifications = int(clarification_queue.get("active_count", 0) or 0)
        caveats: list[str] = []
        if active_clarifications > 0:
            caveats.append("Unresolved optional clarifications are still present.")
        if assumption_count >= 3:
            caveats.append("The run still depends on several explicit assumptions.")
        if violated_checks:
            caveats.append("At least one binding or forbidden-feature constraint was violated.")

        if violated_checks or target_alignment == "conflict":
            alignment = "conflict"
        elif target_alignment == "unresolved" or objective_alignment == "unresolved" or caveats:
            alignment = "unresolved"
        else:
            alignment = "agree"

        trace = CompletionTrace(
            agent="mandate_review_agent",
            operating_mode="deterministic_only",
            llm_used=False,
            llm_status="not_requested",
            deterministic_evidence=[
                "run_brief",
                "task_brief",
                "domain_brief",
                "plan_feature_columns",
                "audit_report",
            ],
        )
        return (
            {
                "alignment": alignment,
                "target_alignment": target_alignment,
                "objective_alignment": objective_alignment,
                "binding_checks": binding_checks,
                "caveats": caveats,
                "summary": _mandate_summary(alignment=alignment, target_alignment=target_alignment, caveats=caveats),
            },
            trace,
        )


class CompletionJudgeAgent:
    """Fuses full-artifact evidence into one machine-actionable governor decision."""

    def __init__(
        self,
        *,
        controls: CompletionControls,
        advisor: CompletionLocalAdvisor | None = None,
    ) -> None:
        self.controls = controls
        self.advisor = advisor

    def run(
        self,
        *,
        run_dir: str | Path,
        mandate_bundle: dict[str, Any],
        context_bundle: dict[str, Any],
        intake_bundle: dict[str, Any],
        investigation_bundle: dict[str, Any],
        planning_bundle: dict[str, Any],
        evidence_bundle: dict[str, Any],
        memory_bundle: dict[str, Any] | None,
        intelligence_bundle: dict[str, Any] | None,
        state_frame: _StateFrame,
        mandate_review: dict[str, Any],
    ) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], CompletionTrace]:
        memory_bundle = memory_bundle or {}
        intelligence_bundle = intelligence_bundle or {}
        run_brief = _bundle_item(mandate_bundle, "run_brief")
        task_brief = _bundle_item(context_bundle, "task_brief")
        plan = _bundle_item(planning_bundle, "plan")
        alternatives = list(_bundle_item(planning_bundle, "alternatives").get("alternatives", []))
        experiment_registry = _bundle_item(evidence_bundle, "experiment_registry")
        challenger_report = _bundle_item(evidence_bundle, "challenger_report")
        ablation_report = _bundle_item(evidence_bundle, "ablation_report")
        audit_report = _bundle_item(evidence_bundle, "audit_report")
        belief_update = _bundle_item(evidence_bundle, "belief_update")
        semantic_debate = _bundle_item(intelligence_bundle, "semantic_debate_report")
        semantic_uncertainty = _bundle_item(intelligence_bundle, "semantic_uncertainty_report")
        intelligence_escalation = _bundle_item(intelligence_bundle, "intelligence_escalation")
        clarification_queue = _bundle_item(intake_bundle, "clarification_queue")
        assumption_log = _bundle_item(intake_bundle, "assumption_log")
        focus_profile = _bundle_item(investigation_bundle, "focus_profile")

        assumption_count = len(list(assumption_log.get("entries", [])))
        clarification_count = int(clarification_queue.get("active_count", 0) or 0)
        experiments = list(experiment_registry.get("experiments", []))
        family_count = len(
            {
                str(item.get("model_family", "")).strip()
                for item in experiments
                if str(item.get("role", "")).strip() in {"champion", "challenger"}
                and str(item.get("model_family", "")).strip()
            }
        )
        challenger_winner = str(challenger_report.get("winner", "")).strip() or "unknown"
        provisional_recommendation = str(audit_report.get("provisional_recommendation", "")).strip()
        readiness_level = str(audit_report.get("readiness_level", "")).strip() or "unknown"
        belief_action = str(belief_update.get("recommended_action", "")).strip()
        open_questions = [str(item).strip() for item in belief_update.get("open_questions", []) if str(item).strip()]
        load_bearing_count = sum(
            1
            for item in ablation_report.get("ablations", [])
            if str(item.get("interpretation", "")).strip().startswith("Load-bearing")
        )
        benchmark_expected = _benchmark_expected(run_brief=run_brief, task_brief=task_brief)
        benchmark_present = any((Path(run_dir) / name).exists() for name in [
            "benchmark_gap_report.json",
            "reference_approach_matrix.json",
            "benchmark_parity_report.json",
            "gold_standard_comparison.json",
        ])
        memory_retrieval = _bundle_item(memory_bundle, "memory_retrieval")
        route_prior_context = _bundle_item(memory_bundle, "route_prior_context")
        challenger_prior = _bundle_item(memory_bundle, "challenger_prior_suggestions")
        memory_present = bool(memory_retrieval)
        memory_attempted = memory_present and str(memory_retrieval.get("status", "")).strip() in {
            "retrieval_completed",
            "no_credible_analogs",
            "disabled",
        }
        memory_helpful = bool(
            int(memory_retrieval.get("selected_analog_count", 0) or 0) > 0
            or str(route_prior_context.get("status", "")).strip() == "memory_influenced"
            or str(challenger_prior.get("status", "")).strip() == "memory_influenced"
        )
        autonomous_mode = _is_autonomous_mode(intake_bundle=intake_bundle, mandate_bundle=mandate_bundle)
        semantic_followup = str(semantic_debate.get("recommended_followup_action", "")).strip()
        semantic_confidence = str(semantic_debate.get("confidence", "")).strip()
        semantic_unresolved_items = [
            item for item in semantic_uncertainty.get("unresolved_items", []) if isinstance(item, dict)
        ]
        route_narrowness = bool(
            challenger_winner == "challenger"
            or (
                family_count <= 2
                and len(alternatives) >= 1
                and provisional_recommendation in {"review_challenger_before_promotion", "continue_experimentation"}
            )
            or semantic_followup == "expand_challenger_portfolio"
        )
        semantic_ambiguity = bool(
            clarification_count > 0
            or assumption_count >= 3
            or not str(plan.get("target_column", "")).strip()
            or semantic_unresolved_items
            or bool(intelligence_escalation.get("escalation_required", False))
            or semantic_confidence == "low"
        )
        evidence_insufficiency = bool(
            readiness_level != "strong"
            or provisional_recommendation in {"hold_for_data_refresh", "continue_experimentation", "use_with_operator_review"}
            or load_bearing_count >= 2
            or open_questions
        )
        memory_support_missing = bool(
            autonomous_mode
            and not memory_attempted
            and route_narrowness
            and provisional_recommendation in {"review_challenger_before_promotion", "continue_experimentation"}
        )
        benchmark_missing = bool(benchmark_expected and not benchmark_present)
        policy_constraint = mandate_review.get("alignment") == "conflict"

        diagnoses = [
            _diagnosis(layer="policy_or_operator_constraint", triggered=policy_constraint, severity="high", reason_code="mandate_conflict", evidence="Mandate or forbidden-feature alignment is conflicting with the executed route."),
            _diagnosis(layer="semantic_ambiguity", triggered=semantic_ambiguity, severity="medium", reason_code="semantic_ambiguity", evidence="Optional clarification items or assumption load are still visible in the run."),
            _diagnosis(layer="route_narrowness", triggered=route_narrowness, severity="high" if challenger_winner == "challenger" else "medium", reason_code="route_narrowness", evidence="The current search breadth is still narrow relative to the observed challenger pressure."),
            _diagnosis(layer="evidence_insufficiency", triggered=evidence_insufficiency, severity="medium", reason_code="evidence_insufficiency", evidence="Readiness remains conditional or the evidence bundle still carries open questions."),
            _diagnosis(layer="missing_memory_support", triggered=memory_support_missing, severity="medium", reason_code="missing_memory_support", evidence="Autonomous continuation would benefit from prior analog retrieval, but no memory retrieval attempt has been recorded."),
            _diagnosis(layer="missing_benchmark_context", triggered=benchmark_missing, severity="medium", reason_code="missing_benchmark_context", evidence="The mandate asks for benchmark or reference proof, but no benchmark artifacts are present."),
        ]

        blocking_layer = "none"
        action = "stop_for_now"
        reason_codes: list[str] = []
        if policy_constraint:
            blocking_layer = "policy_or_operator_constraint"
            reason_codes.append("mandate_conflict")
        elif challenger_winner == "challenger":
            blocking_layer = "route_narrowness"
            action = "review_challenger"
            reason_codes.append("challenger_won")
        elif benchmark_missing:
            blocking_layer = "missing_benchmark_context"
            action = "benchmark_needed"
            reason_codes.append("benchmark_requested_by_mandate")
        elif memory_support_missing:
            blocking_layer = "missing_memory_support"
            action = "memory_support_needed"
            reason_codes.append("memory_not_available")
        elif provisional_recommendation == "hold_for_data_refresh":
            blocking_layer = "evidence_insufficiency"
            action = "collect_more_data"
            reason_codes.append("operating_envelope_risk")
        elif semantic_followup == "collect_more_data":
            blocking_layer = "evidence_insufficiency"
            action = "collect_more_data"
            reason_codes.append("semantic_data_gap")
        elif provisional_recommendation == "continue_experimentation" or belief_action == "continue_experimentation":
            blocking_layer = "route_narrowness" if route_narrowness else "evidence_insufficiency"
            action = "continue_experimentation"
            reason_codes.append("evidence_still_fragile")
        elif provisional_recommendation == "use_with_operator_review":
            if autonomous_mode:
                blocking_layer = "evidence_insufficiency"
                action = "continue_experimentation"
                reason_codes.append("operator_review_not_required_in_autonomous_mode")
            else:
                blocking_layer = "policy_or_operator_constraint"
                action = "stop_for_now"
                reason_codes.append("operator_review_expected")
        elif readiness_level == "strong":
            reason_codes.append("mvp_complete")
        else:
            blocking_layer = "evidence_insufficiency"
            action = "continue_experimentation"
            reason_codes.append("evidence_still_fragile")

        if semantic_ambiguity:
            reason_codes.append("semantic_ambiguity")
        if semantic_followup:
            reason_codes.append(f"semantic_followup_{semantic_followup}")
        if load_bearing_count >= 2:
            reason_codes.append("feature_dependency_high")
        if memory_helpful:
            reason_codes.append("memory_support_available")
        if not str(plan.get("primary_metric", "")).strip():
            reason_codes.append("missing_primary_metric")
        if not str(focus_profile.get("primary_objective", "")).strip():
            reason_codes.append("focus_not_explicit")
        reason_codes = _dedupe_strings(reason_codes)

        evidence_state = _evidence_state(
            readiness_level=readiness_level,
            challenger_winner=challenger_winner,
            open_questions=open_questions,
        )
        confidence = _decision_confidence(
            action=action,
            blocking_layer=blocking_layer,
            evidence_state=evidence_state,
            semantic_ambiguity=semantic_ambiguity,
            mandate_alignment=str(mandate_review.get("alignment", "unresolved")),
        )
        complete_for_mode = action == "stop_for_now" and blocking_layer == "none"

        llm_advisory: dict[str, Any] | None = None
        llm_used = False
        llm_status = "not_requested"
        advisory_notes: list[str] = []
        if self.advisor is not None:
            advisory = self.advisor.complete_json(
                task_name="completion_governor",
                system_prompt="You are Relaytic's Completion Governor advisory module. Do not change the decision. Return JSON with keys summary_note, reasoning_highlights, and queue_emphasis. Keep every value short.",
                payload={
                    "decision": {"action": action, "blocking_layer": blocking_layer, "confidence": confidence, "reason_codes": reason_codes},
                    "mandate_review": mandate_review,
                    "state": {"current_stage": state_frame.current_stage, "previous_stage": state_frame.previous_stage, "executed_stages": state_frame.executed_stages},
                    "evidence": {"provisional_recommendation": provisional_recommendation, "readiness_level": readiness_level, "challenger_winner": challenger_winner, "open_questions": open_questions},
                },
            )
            llm_status = "advisory_used" if advisory.status == "ok" and advisory.payload else advisory.status
            advisory_notes.extend(advisory.notes)
            if advisory.payload:
                llm_advisory = advisory.payload
                llm_used = True

        trace = CompletionTrace(
            agent="completion_judge_agent",
            operating_mode="deterministic_plus_advisory" if self.advisor is not None else "deterministic_only",
            llm_used=llm_used,
            llm_status=llm_status,
            deterministic_evidence=[
                "mandate_bundle",
                "context_bundle",
                "intake_bundle",
                "investigation_bundle",
                "planning_bundle",
                "evidence_bundle",
                "intelligence_bundle",
            ],
            advisory_notes=advisory_notes,
        )
        next_actions = _build_next_actions(
            action=action,
            blocking_layer=blocking_layer,
            reason_codes=reason_codes,
            open_questions=open_questions,
            benchmark_missing=benchmark_missing,
            memory_support_missing=memory_support_missing,
        )
        return (
            {
                "action": action,
                "confidence": confidence,
                "current_stage": state_frame.current_stage,
                "blocking_layer": blocking_layer,
                "mandate_alignment": str(mandate_review.get("alignment", "unresolved")),
                "evidence_state": evidence_state,
                "complete_for_mode": complete_for_mode,
                "reason_codes": reason_codes,
                "summary": _decision_summary(action=action, blocking_layer=blocking_layer, complete_for_mode=complete_for_mode, llm_advisory=llm_advisory),
                "llm_advisory": llm_advisory,
            },
            {
                "blocking_layer": blocking_layer,
                "diagnoses": diagnoses,
                "summary": _blocking_summary(blocking_layer=blocking_layer, diagnoses=diagnoses),
            },
            {
                "actions": next_actions,
                "summary": _queue_summary(next_actions),
            },
            trace,
        )


def run_completion_review(
    *,
    run_dir: str | Path,
    policy: dict[str, Any],
    mandate_bundle: dict[str, Any],
    context_bundle: dict[str, Any],
    intake_bundle: dict[str, Any],
    investigation_bundle: dict[str, Any],
    planning_bundle: dict[str, Any],
    evidence_bundle: dict[str, Any],
    memory_bundle: dict[str, Any] | None = None,
    intelligence_bundle: dict[str, Any] | None = None,
    config_path: str | None = None,
) -> CompletionRunResult:
    """Execute the Slice 07 completion-governor stage for a Relaytic run."""
    controls = build_completion_controls_from_policy(policy)
    advisor = build_local_advisor(controls=controls, config_path=config_path)
    state_tracker = StateTrackerAgent(controls=controls)
    mandate_reviewer = MandateReviewAgent(controls=controls)
    judge = CompletionJudgeAgent(controls=controls, advisor=advisor)

    generated_at = _utc_now()
    state_frame, state_trace = state_tracker.run(
        run_dir=run_dir,
        mandate_bundle=mandate_bundle,
        context_bundle=context_bundle,
        intake_bundle=intake_bundle,
        investigation_bundle=investigation_bundle,
        planning_bundle=planning_bundle,
        evidence_bundle=evidence_bundle,
        memory_bundle=memory_bundle,
        intelligence_bundle=intelligence_bundle,
    )
    mandate_payload, mandate_trace = mandate_reviewer.run(
        mandate_bundle=mandate_bundle,
        context_bundle=context_bundle,
        intake_bundle=intake_bundle,
        planning_bundle=planning_bundle,
        evidence_bundle=evidence_bundle,
    )
    decision_payload, blocking_payload, queue_payload, judge_trace = judge.run(
        run_dir=run_dir,
        mandate_bundle=mandate_bundle,
        context_bundle=context_bundle,
        intake_bundle=intake_bundle,
        investigation_bundle=investigation_bundle,
        planning_bundle=planning_bundle,
        evidence_bundle=evidence_bundle,
        memory_bundle=memory_bundle,
        intelligence_bundle=intelligence_bundle,
        state_frame=state_frame,
        mandate_review=mandate_payload,
    )

    bundle = CompletionBundle(
        completion_decision=CompletionDecision(
            schema_version=COMPLETION_DECISION_SCHEMA_VERSION,
            generated_at=generated_at,
            controls=controls,
            action=str(decision_payload["action"]),
            confidence=str(decision_payload["confidence"]),
            current_stage=str(decision_payload["current_stage"]),
            blocking_layer=str(decision_payload["blocking_layer"]),
            mandate_alignment=str(decision_payload["mandate_alignment"]),
            evidence_state=str(decision_payload["evidence_state"]),
            complete_for_mode=bool(decision_payload["complete_for_mode"]),
            reason_codes=list(decision_payload["reason_codes"]),
            summary=str(decision_payload["summary"]),
            llm_advisory=decision_payload["llm_advisory"],
            trace=judge_trace,
        ),
        run_state=RunState(
            schema_version=RUN_STATE_SCHEMA_VERSION,
            generated_at=generated_at,
            controls=controls,
            current_stage=state_frame.current_stage,
            previous_stage=state_frame.previous_stage,
            state="complete" if bool(decision_payload["complete_for_mode"]) else "in_progress",
            executed_stages=list(state_frame.executed_stages),
            artifact_presence=dict(state_frame.artifact_presence),
            summary=_run_state_summary(
                current_stage=state_frame.current_stage,
                previous_stage=state_frame.previous_stage,
                complete_for_mode=bool(decision_payload["complete_for_mode"]),
            ),
            trace=state_trace,
        ),
        stage_timeline=StageTimeline(
            schema_version=STAGE_TIMELINE_SCHEMA_VERSION,
            generated_at=generated_at,
            controls=controls,
            stages=list(state_frame.stages),
            summary=_timeline_summary(state_frame.stages),
            trace=state_trace,
        ),
        mandate_evidence_review=MandateEvidenceReview(
            schema_version=MANDATE_EVIDENCE_REVIEW_SCHEMA_VERSION,
            generated_at=generated_at,
            controls=controls,
            alignment=str(mandate_payload["alignment"]),
            target_alignment=str(mandate_payload["target_alignment"]),
            objective_alignment=str(mandate_payload["objective_alignment"]),
            binding_checks=list(mandate_payload["binding_checks"]),
            caveats=list(mandate_payload["caveats"]),
            summary=str(mandate_payload["summary"]),
            trace=mandate_trace,
        ),
        blocking_analysis=BlockingAnalysis(
            schema_version=BLOCKING_ANALYSIS_SCHEMA_VERSION,
            generated_at=generated_at,
            controls=controls,
            blocking_layer=str(blocking_payload["blocking_layer"]),
            diagnoses=list(blocking_payload["diagnoses"]),
            summary=str(blocking_payload["summary"]),
            trace=judge_trace,
        ),
        next_action_queue=NextActionQueue(
            schema_version=NEXT_ACTION_QUEUE_SCHEMA_VERSION,
            generated_at=generated_at,
            controls=controls,
            actions=list(queue_payload["actions"]),
            summary=str(queue_payload["summary"]),
            trace=judge_trace,
        ),
    )
    return CompletionRunResult(
        bundle=bundle,
        review_markdown=render_completion_review_markdown(bundle.to_dict()),
    )


def render_completion_review_markdown(bundle: CompletionBundle | dict[str, Any]) -> str:
    """Render a concise human-readable completion review."""
    payload = bundle.to_dict() if isinstance(bundle, CompletionBundle) else dict(bundle)
    decision = _bundle_item(payload, "completion_decision")
    run_state = _bundle_item(payload, "run_state")
    mandate_review = _bundle_item(payload, "mandate_evidence_review")
    queue = _bundle_item(payload, "next_action_queue")
    lines = [
        "# Relaytic Completion Review",
        "",
        decision.get("summary", "Relaytic reviewed the current run state."),
        "",
        "## Decision",
        f"- Action: `{decision.get('action') or 'unknown'}`",
        f"- Confidence: `{decision.get('confidence') or 'unknown'}`",
        f"- Blocking layer: `{decision.get('blocking_layer') or 'none'}`",
        f"- Complete for mode: `{decision.get('complete_for_mode')}`",
        "",
        "## State",
        f"- Current stage: `{run_state.get('current_stage') or 'unknown'}`",
        f"- Previous stage: `{run_state.get('previous_stage') or 'none'}`",
        f"- State: `{run_state.get('state') or 'unknown'}`",
        "",
        "## Mandate Review",
        f"- Alignment: `{mandate_review.get('alignment') or 'unknown'}`",
        f"- Target alignment: `{mandate_review.get('target_alignment') or 'unknown'}`",
        f"- Objective alignment: `{mandate_review.get('objective_alignment') or 'unknown'}`",
        "",
        "## Next Actions",
    ]
    caveats = list(mandate_review.get("caveats", []))
    if caveats:
        lines.insert(-2, f"- Caveat: {caveats[0]}")
    actions = list(queue.get("actions", []))
    if actions:
        for item in actions[:5]:
            lines.append(
                f"- `{item.get('action') or 'unknown'}` (priority `{item.get('priority', 'n/a')}`): "
                f"{item.get('reason_code') or 'no reason code'}"
            )
    else:
            lines.append("- No next actions recorded.")
    return "\n".join(lines).rstrip() + "\n"


def _artifact_time(path: Path, payload: dict[str, Any] | None) -> str | None:
    if isinstance(payload, dict):
        generated = str(payload.get("generated_at", "")).strip()
        if generated:
            return generated
    if path.exists():
        return datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc).isoformat()
    return None


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return payload if isinstance(payload, dict) else {}


def _bundle_item(bundle: dict[str, Any], key: str) -> dict[str, Any]:
    payload = bundle.get(key)
    return dict(payload) if isinstance(payload, dict) else {}


def _string_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    text = str(value).strip()
    return [text] if text else []


def _dedupe_strings(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        stripped = str(value).strip()
        if not stripped:
            continue
        normalized = stripped.casefold()
        if normalized in seen:
            continue
        seen.add(normalized)
        result.append(stripped)
    return result


def _extract_forbidden_hints(payload: dict[str, Any]) -> list[str]:
    values = _string_list(payload.get("binding_constraints")) + _string_list(payload.get("hard_constraints"))
    hints: list[str] = []
    for value in values:
        lowered = value.lower()
        if "future" in lowered:
            hints.append("future")
        if "post-inspection" in lowered or "post inspection" in lowered:
            hints.append("post_inspection")
    return hints


def _constraint_matches_columns(constraint: str, columns: list[str]) -> bool:
    lowered = constraint.casefold()
    if lowered in {column.casefold() for column in columns}:
        return True
    if lowered == "future":
        return any("future" in column.casefold() for column in columns)
    if lowered == "post_inspection":
        return any("post" in column.casefold() and "inspection" in column.casefold() for column in columns)
    return False


def _mandate_summary(*, alignment: str, target_alignment: str, caveats: list[str]) -> str:
    if alignment == "conflict":
        return "Relaytic found a conflict between mandate/context constraints and the executed route."
    if alignment == "agree":
        return "Relaytic found the current route broadly aligned with the recorded mandate and context."
    if target_alignment == "unresolved":
        return "Relaytic can continue, but target intent is still not fully resolved."
    if caveats:
        return f"Relaytic found provisional alignment with caveats: {caveats[0]}"
    return "Relaytic found provisional alignment that still needs more evidence."


def _benchmark_expected(*, run_brief: dict[str, Any], task_brief: dict[str, Any]) -> bool:
    text = " ".join(
        _string_list(run_brief.get("objective"))
        + _string_list(run_brief.get("success_criteria"))
        + _string_list(task_brief.get("success_criteria"))
        + _string_list(task_brief.get("problem_statement"))
    ).lower()
    return any(keyword in text for keyword in ("benchmark", "parity", "reference", "gold standard", "beat baseline", "sota"))


def _is_autonomous_mode(*, intake_bundle: dict[str, Any], mandate_bundle: dict[str, Any]) -> bool:
    autonomy_mode = _bundle_item(intake_bundle, "autonomy_mode")
    requested_mode = str(autonomy_mode.get("requested_mode", "")).strip().lower()
    if requested_mode == "autonomous":
        return True
    operator_signal = str(autonomy_mode.get("operator_signal", "")).strip().lower()
    if any(phrase in operator_signal for phrase in ("autonomous", "on your own", "find out", "figure it out")):
        return True
    work_preferences = _bundle_item(mandate_bundle, "work_preferences")
    execution_mode = str(work_preferences.get("execution_mode_preference", "")).strip().lower()
    return execution_mode == "autonomous"


def _diagnosis(*, layer: str, triggered: bool, severity: str, reason_code: str, evidence: str) -> dict[str, Any]:
    return {
        "layer": layer,
        "triggered": bool(triggered),
        "severity": severity if triggered else "none",
        "reason_code": reason_code,
        "evidence": evidence,
    }


def _evidence_state(*, readiness_level: str, challenger_winner: str, open_questions: list[str]) -> str:
    if challenger_winner == "challenger":
        return "fragile"
    if readiness_level == "strong" and not open_questions:
        return "strong"
    if readiness_level == "conditional":
        return "conditional"
    return "fragile"


def _decision_confidence(
    *,
    action: str,
    blocking_layer: str,
    evidence_state: str,
    semantic_ambiguity: bool,
    mandate_alignment: str,
) -> str:
    del action
    if mandate_alignment == "conflict":
        return "low"
    if blocking_layer == "none" and evidence_state == "strong":
        return "strong"
    if semantic_ambiguity or evidence_state == "fragile":
        return "low"
    return "conditional"


def _decision_summary(
    *,
    action: str,
    blocking_layer: str,
    complete_for_mode: bool,
    llm_advisory: dict[str, Any] | None,
) -> str:
    if blocking_layer != "none":
        base = f"Relaytic recommends `{action}` with primary blocking layer `{blocking_layer}`."
    else:
        base = f"Relaytic recommends `{action}` and considers the run complete enough for the current mode."
    if complete_for_mode:
        base += " The current MVP bar is met."
    note = str((llm_advisory or {}).get("summary_note", "")).strip()
    if note:
        base += f" Advisory note: {note}"
    return base


def _build_next_actions(
    *,
    action: str,
    blocking_layer: str,
    reason_codes: list[str],
    open_questions: list[str],
    benchmark_missing: bool,
    memory_support_missing: bool,
) -> list[dict[str, Any]]:
    actions = [
        {
            "action": action,
            "priority": 1,
            "reason_code": reason_codes[0] if reason_codes else "completion_action",
            "source_artifact": "completion_decision.json",
            "blocking": blocking_layer != "none",
        }
    ]
    if memory_support_missing and action != "memory_support_needed":
        actions.append(
            {
                "action": "memory_support_needed",
                "priority": 2,
                "reason_code": "missing_memory_support",
                "source_artifact": "blocking_analysis.json",
                "blocking": False,
            }
        )
    if benchmark_missing and action != "benchmark_needed":
        actions.append(
            {
                "action": "benchmark_needed",
                "priority": 3,
                "reason_code": "missing_benchmark_context",
                "source_artifact": "blocking_analysis.json",
                "blocking": False,
            }
        )
    for index, item in enumerate(open_questions[:2], start=4):
        actions.append(
            {
                "action": "continue_experimentation",
                "priority": index,
                "reason_code": item,
                "source_artifact": "belief_update.json",
                "blocking": False,
            }
        )
    return actions


def _blocking_summary(*, blocking_layer: str, diagnoses: list[dict[str, Any]]) -> str:
    if blocking_layer == "none":
        return "Relaytic did not detect a blocking layer that should keep the current MVP run open."
    diagnosis = next((item for item in diagnoses if item.get("layer") == blocking_layer), {})
    return (
        f"Relaytic's primary blocking layer is `{blocking_layer}`. "
        f"{diagnosis.get('evidence') or 'No diagnosis detail recorded.'}"
    )


def _queue_summary(actions: list[dict[str, Any]]) -> str:
    if not actions:
        return "No next actions were recorded."
    primary = actions[0]
    return (
        f"Relaytic queued `{primary.get('action')}` as the next action "
        f"with reason `{primary.get('reason_code')}`."
    )


def _run_state_summary(*, current_stage: str, previous_stage: str | None, complete_for_mode: bool) -> str:
    if complete_for_mode:
        return f"Relaytic has reached `{current_stage}` and currently considers the run complete enough for the active mode."
    if previous_stage:
        return f"Relaytic advanced from `{previous_stage}` to `{current_stage}` and still recommends further action."
    return f"Relaytic is at `{current_stage}` and still recommends further action."


def _timeline_summary(stages: list[dict[str, Any]]) -> str:
    if not stages:
        return "No stages were recorded."
    return f"Relaytic recorded {len(stages)} stage transition(s) up to `{stages[-1]['stage']}`."


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()
