"""MVP run-summary and report helpers for human and agent access surfaces."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from relaytic.core.json_utils import write_json


RUN_SUMMARY_SCHEMA_VERSION = "relaytic.run_summary.v1"
RUN_SUMMARY_FILENAME = "run_summary.json"
RUN_REPORT_RELATIVE_PATH = Path("reports") / "summary.md"


def read_run_summary(run_dir: str | Path) -> dict[str, Any]:
    """Read a persisted run summary if present."""
    path = Path(run_dir) / RUN_SUMMARY_FILENAME
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def build_run_summary(
    *,
    run_dir: str | Path,
    data_path: str | Path | None = None,
    request_source: str | None = None,
    request_text: str | None = None,
) -> dict[str, Any]:
    """Build a machine-readable summary for a Relaytic run directory."""
    root = Path(run_dir)
    from relaytic.handoff import (
        AGENT_RESULT_REPORT_RELATIVE_PATH,
        USER_RESULT_REPORT_RELATIVE_PATH,
        read_handoff_bundle,
    )
    from relaytic.iteration import read_iteration_bundle
    from relaytic.search import read_search_bundle
    from relaytic.learnings import (
        default_learnings_state_dir,
        read_learnings_snapshot,
        read_learnings_state,
    )
    from relaytic.workspace import (
        default_workspace_dir,
        read_result_contract_artifacts,
        read_workspace_bundle,
    )
    mandate_bundle = _read_bundle(
        root,
        {
            "lab_mandate": "lab_mandate.json",
            "work_preferences": "work_preferences.json",
            "run_brief": "run_brief.json",
        },
    )
    context_bundle = _read_bundle(
        root,
        {
            "data_origin": "data_origin.json",
            "domain_brief": "domain_brief.json",
            "task_brief": "task_brief.json",
        },
    )
    intake_bundle = _read_bundle(
        root,
        {
            "intake_record": "intake_record.json",
            "autonomy_mode": "autonomy_mode.json",
            "clarification_queue": "clarification_queue.json",
            "assumption_log": "assumption_log.json",
            "context_interpretation": "context_interpretation.json",
        },
    )
    investigation_bundle = _read_bundle(
        root,
        {
            "dataset_profile": "dataset_profile.json",
            "domain_memo": "domain_memo.json",
            "focus_profile": "focus_profile.json",
            "optimization_profile": "optimization_profile.json",
        },
    )
    planning_bundle = _read_bundle(
        root,
        {
            "plan": "plan.json",
            "alternatives": "alternatives.json",
            "hypotheses": "hypotheses.json",
            "experiment_priority_report": "experiment_priority_report.json",
            "marginal_value_of_next_experiment": "marginal_value_of_next_experiment.json",
        },
    )
    evidence_bundle = _read_bundle(
        root,
        {
            "experiment_registry": "experiment_registry.json",
            "challenger_report": "challenger_report.json",
            "ablation_report": "ablation_report.json",
            "audit_report": "audit_report.json",
            "belief_update": "belief_update.json",
        },
    )
    completion_bundle = _read_bundle(
        root,
        {
            "completion_decision": "completion_decision.json",
            "run_state": "run_state.json",
            "stage_timeline": "stage_timeline.json",
            "mandate_evidence_review": "mandate_evidence_review.json",
            "blocking_analysis": "blocking_analysis.json",
            "next_action_queue": "next_action_queue.json",
        },
    )
    memory_bundle = _read_bundle(
        root,
        {
            "memory_retrieval": "memory_retrieval.json",
            "analog_run_candidates": "analog_run_candidates.json",
            "route_prior_context": "route_prior_context.json",
            "challenger_prior_suggestions": "challenger_prior_suggestions.json",
            "reflection_memory": "reflection_memory.json",
            "memory_flush_report": "memory_flush_report.json",
        },
    )
    intelligence_bundle = _read_bundle(
        root,
        {
            "intelligence_mode": "intelligence_mode.json",
            "llm_routing_plan": "llm_routing_plan.json",
            "local_llm_profile": "local_llm_profile.json",
            "llm_backend_discovery": "llm_backend_discovery.json",
            "verifier_report": "verifier_report.json",
            "semantic_debate_report": "semantic_debate_report.json",
            "semantic_counterposition_pack": "semantic_counterposition_pack.json",
            "semantic_uncertainty_report": "semantic_uncertainty_report.json",
            "intelligence_escalation": "intelligence_escalation.json",
            "semantic_proof_report": "semantic_proof_report.json",
        },
    )
    research_bundle = _read_bundle(
        root,
        {
            "research_query_plan": "research_query_plan.json",
            "research_source_inventory": "research_source_inventory.json",
            "research_brief": "research_brief.json",
            "method_transfer_report": "method_transfer_report.json",
            "benchmark_reference_report": "benchmark_reference_report.json",
            "external_research_audit": "external_research_audit.json",
        },
    )
    benchmark_bundle = _read_bundle(
        root,
        {
            "reference_approach_matrix": "reference_approach_matrix.json",
            "benchmark_gap_report": "benchmark_gap_report.json",
            "benchmark_parity_report": "benchmark_parity_report.json",
            "external_challenger_manifest": "external_challenger_manifest.json",
            "external_challenger_evaluation": "external_challenger_evaluation.json",
            "incumbent_parity_report": "incumbent_parity_report.json",
            "beat_target_contract": "beat_target_contract.json",
        },
    )
    decision_bundle = _read_bundle(
        root,
        {
            "decision_world_model": "decision_world_model.json",
            "controller_policy": "controller_policy.json",
            "handoff_controller_report": "handoff_controller_report.json",
            "intervention_policy_report": "intervention_policy_report.json",
            "decision_usefulness_report": "decision_usefulness_report.json",
            "value_of_more_data_report": "value_of_more_data_report.json",
            "data_acquisition_plan": "data_acquisition_plan.json",
            "source_graph": "source_graph.json",
            "join_candidate_report": "join_candidate_report.json",
            "method_compiler_report": "method_compiler_report.json",
            "compiled_challenger_templates": "compiled_challenger_templates.json",
            "compiled_feature_hypotheses": "compiled_feature_hypotheses.json",
            "compiled_benchmark_protocol": "compiled_benchmark_protocol.json",
        },
    )
    dojo_bundle = _read_bundle(
        root,
        {
            "dojo_session": "dojo_session.json",
            "dojo_hypotheses": "dojo_hypotheses.json",
            "dojo_results": "dojo_results.json",
            "dojo_promotions": "dojo_promotions.json",
            "architecture_proposals": "architecture_proposals.json",
        },
    )
    pulse_bundle = _read_bundle(
        root,
        {
            "pulse_schedule": "pulse_schedule.json",
            "pulse_run_report": "pulse_run_report.json",
            "pulse_skip_report": "pulse_skip_report.json",
            "pulse_recommendations": "pulse_recommendations.json",
            "innovation_watch_report": "innovation_watch_report.json",
            "challenge_watchlist": "challenge_watchlist.json",
            "pulse_checkpoint": "pulse_checkpoint.json",
            "memory_compaction_plan": "memory_compaction_plan.json",
            "memory_compaction_report": "memory_compaction_report.json",
            "memory_pinning_index": "memory_pinning_index.json",
        },
    )
    trace_bundle = _read_bundle(
        root,
        {
            "trace_model": "trace_model.json",
            "specialist_trace_index": "specialist_trace_index.json",
            "branch_trace_graph": "branch_trace_graph.json",
            "adjudication_scorecard": "adjudication_scorecard.json",
            "decision_replay_report": "decision_replay_report.json",
        },
    )
    evals_bundle = _read_bundle(
        root,
        {
            "agent_eval_matrix": "agent_eval_matrix.json",
            "security_eval_report": "security_eval_report.json",
            "red_team_report": "red_team_report.json",
            "protocol_conformance_report": "protocol_conformance_report.json",
            "host_surface_matrix": "host_surface_matrix.json",
        },
    )
    search_bundle = read_search_bundle(root)
    handoff_bundle = read_handoff_bundle(root)
    learnings_state_dir = default_learnings_state_dir(run_dir=root)
    learnings_state = read_learnings_state(learnings_state_dir)
    learnings_snapshot = read_learnings_snapshot(root)
    workspace_dir = default_workspace_dir(run_dir=root)
    workspace_bundle = read_workspace_bundle(workspace_dir)
    result_contract_bundle = read_result_contract_artifacts(root)
    iteration_bundle = read_iteration_bundle(workspace_dir=workspace_dir, run_dir=root)
    feedback_bundle = _read_bundle(
        root,
        {
            "feedback_intake": "feedback_intake.json",
            "feedback_validation": "feedback_validation.json",
            "feedback_effect_report": "feedback_effect_report.json",
            "feedback_casebook": "feedback_casebook.json",
            "outcome_observation_report": "outcome_observation_report.json",
            "decision_policy_update_suggestions": "decision_policy_update_suggestions.json",
            "policy_update_suggestions": "policy_update_suggestions.json",
            "route_prior_updates": "route_prior_updates.json",
        },
    )
    profiles_bundle = _read_bundle(
        root,
        {
            "quality_contract": "quality_contract.json",
            "quality_gate_report": "quality_gate_report.json",
            "budget_contract": "budget_contract.json",
            "budget_consumption_report": "budget_consumption_report.json",
            "operator_profile": "operator_profile.json",
            "lab_operating_profile": "lab_operating_profile.json",
        },
    )
    control_bundle = _read_bundle(
        root,
        {
            "intervention_request": "intervention_request.json",
            "intervention_contract": "intervention_contract.json",
            "control_challenge_report": "control_challenge_report.json",
            "override_decision": "override_decision.json",
            "intervention_ledger": "intervention_ledger.json",
            "recovery_checkpoint": "recovery_checkpoint.json",
            "control_injection_audit": "control_injection_audit.json",
            "causal_memory_index": "causal_memory_index.json",
            "intervention_memory_log": "intervention_memory_log.json",
            "outcome_memory_graph": "outcome_memory_graph.json",
            "method_memory_index": "method_memory_index.json",
        },
    )
    runtime_bundle = _read_bundle(
        root,
        {
            "hook_execution_log": "hook_execution_log.json",
            "run_checkpoint_manifest": "run_checkpoint_manifest.json",
            "capability_profiles": "capability_profiles.json",
            "data_access_audit": "data_access_audit.json",
            "context_influence_report": "context_influence_report.json",
        },
    )
    lifecycle_bundle = _read_bundle(
        root,
        {
            "champion_vs_candidate": "champion_vs_candidate.json",
            "recalibration_decision": "recalibration_decision.json",
            "retrain_decision": "retrain_decision.json",
            "promotion_decision": "promotion_decision.json",
            "rollback_decision": "rollback_decision.json",
        },
    )
    autonomy_bundle = _read_bundle(
        root,
        {
            "autonomy_loop_state": "autonomy_loop_state.json",
            "autonomy_round_report": "autonomy_round_report.json",
            "branch_outcome_matrix": "branch_outcome_matrix.json",
            "champion_lineage": "champion_lineage.json",
            "loop_budget_report": "loop_budget_report.json",
        },
    )
    model_params = _read_json(root / "model_params.json")
    manifest = _read_json(root / "manifest.json")
    data_copy_manifest = _read_json(root / "data_copy_manifest.json")

    run_brief = _bundle_item(mandate_bundle, "run_brief")
    data_origin = _bundle_item(context_bundle, "data_origin")
    task_brief = _bundle_item(context_bundle, "task_brief")
    domain_brief = _bundle_item(context_bundle, "domain_brief")
    autonomy_mode = _bundle_item(intake_bundle, "autonomy_mode")
    intake_record = _bundle_item(intake_bundle, "intake_record")
    assumption_entries = list(_bundle_item(intake_bundle, "assumption_log").get("entries", []))
    focus_profile = _bundle_item(investigation_bundle, "focus_profile")
    dataset_profile = _bundle_item(investigation_bundle, "dataset_profile")
    plan = _bundle_item(planning_bundle, "plan")
    experiment_registry = _bundle_item(evidence_bundle, "experiment_registry")
    challenger_report = _bundle_item(evidence_bundle, "challenger_report")
    ablation_report = _bundle_item(evidence_bundle, "ablation_report")
    audit_report = _bundle_item(evidence_bundle, "audit_report")
    belief_update = _bundle_item(evidence_bundle, "belief_update")
    completion_decision = _bundle_item(completion_bundle, "completion_decision")
    run_state = _bundle_item(completion_bundle, "run_state")
    mandate_evidence_review = _bundle_item(completion_bundle, "mandate_evidence_review")
    blocking_analysis = _bundle_item(completion_bundle, "blocking_analysis")
    next_action_queue = _bundle_item(completion_bundle, "next_action_queue")
    memory_retrieval = _bundle_item(memory_bundle, "memory_retrieval")
    analog_run_candidates = _bundle_item(memory_bundle, "analog_run_candidates")
    route_prior_context = _bundle_item(memory_bundle, "route_prior_context")
    challenger_prior_suggestions = _bundle_item(memory_bundle, "challenger_prior_suggestions")
    reflection_memory = _bundle_item(memory_bundle, "reflection_memory")
    memory_flush_report = _bundle_item(memory_bundle, "memory_flush_report")
    intelligence_mode = _bundle_item(intelligence_bundle, "intelligence_mode")
    llm_routing_plan = _bundle_item(intelligence_bundle, "llm_routing_plan")
    local_llm_profile = _bundle_item(intelligence_bundle, "local_llm_profile")
    semantic_debate_report = _bundle_item(intelligence_bundle, "semantic_debate_report")
    semantic_uncertainty_report = _bundle_item(intelligence_bundle, "semantic_uncertainty_report")
    intelligence_escalation = _bundle_item(intelligence_bundle, "intelligence_escalation")
    semantic_proof_report = _bundle_item(intelligence_bundle, "semantic_proof_report")
    research_query_plan = _bundle_item(research_bundle, "research_query_plan")
    research_source_inventory = _bundle_item(research_bundle, "research_source_inventory")
    research_brief = _bundle_item(research_bundle, "research_brief")
    method_transfer_report = _bundle_item(research_bundle, "method_transfer_report")
    benchmark_reference_report = _bundle_item(research_bundle, "benchmark_reference_report")
    external_research_audit = _bundle_item(research_bundle, "external_research_audit")
    reference_approach_matrix = _bundle_item(benchmark_bundle, "reference_approach_matrix")
    benchmark_gap_report = _bundle_item(benchmark_bundle, "benchmark_gap_report")
    benchmark_parity_report = _bundle_item(benchmark_bundle, "benchmark_parity_report")
    external_challenger_manifest = _bundle_item(benchmark_bundle, "external_challenger_manifest")
    external_challenger_evaluation = _bundle_item(benchmark_bundle, "external_challenger_evaluation")
    incumbent_parity_report = _bundle_item(benchmark_bundle, "incumbent_parity_report")
    beat_target_contract = _bundle_item(benchmark_bundle, "beat_target_contract")
    decision_world_model = _bundle_item(decision_bundle, "decision_world_model")
    controller_policy = _bundle_item(decision_bundle, "controller_policy")
    handoff_controller_report = _bundle_item(decision_bundle, "handoff_controller_report")
    decision_usefulness_report = _bundle_item(decision_bundle, "decision_usefulness_report")
    value_of_more_data_report = _bundle_item(decision_bundle, "value_of_more_data_report")
    data_acquisition_plan = _bundle_item(decision_bundle, "data_acquisition_plan")
    source_graph = _bundle_item(decision_bundle, "source_graph")
    join_candidate_report = _bundle_item(decision_bundle, "join_candidate_report")
    method_compiler_report = _bundle_item(decision_bundle, "method_compiler_report")
    compiled_challenger_templates = _bundle_item(decision_bundle, "compiled_challenger_templates")
    compiled_feature_hypotheses = _bundle_item(decision_bundle, "compiled_feature_hypotheses")
    compiled_benchmark_protocol = _bundle_item(decision_bundle, "compiled_benchmark_protocol")
    dojo_session = _bundle_item(dojo_bundle, "dojo_session")
    dojo_hypotheses = _bundle_item(dojo_bundle, "dojo_hypotheses")
    dojo_results = _bundle_item(dojo_bundle, "dojo_results")
    dojo_promotions = _bundle_item(dojo_bundle, "dojo_promotions")
    architecture_proposals = _bundle_item(dojo_bundle, "architecture_proposals")
    pulse_schedule = _bundle_item(pulse_bundle, "pulse_schedule")
    pulse_run_report = _bundle_item(pulse_bundle, "pulse_run_report")
    pulse_skip_report = _bundle_item(pulse_bundle, "pulse_skip_report")
    pulse_recommendations = _bundle_item(pulse_bundle, "pulse_recommendations")
    innovation_watch_report = _bundle_item(pulse_bundle, "innovation_watch_report")
    challenge_watchlist = _bundle_item(pulse_bundle, "challenge_watchlist")
    memory_compaction_report = _bundle_item(pulse_bundle, "memory_compaction_report")
    memory_pinning_index = _bundle_item(pulse_bundle, "memory_pinning_index")
    trace_model = _bundle_item(trace_bundle, "trace_model")
    adjudication_scorecard = _bundle_item(trace_bundle, "adjudication_scorecard")
    decision_replay_report = _bundle_item(trace_bundle, "decision_replay_report")
    agent_eval_matrix = _bundle_item(evals_bundle, "agent_eval_matrix")
    security_eval_report = _bundle_item(evals_bundle, "security_eval_report")
    red_team_report = _bundle_item(evals_bundle, "red_team_report")
    protocol_conformance_report = _bundle_item(evals_bundle, "protocol_conformance_report")
    host_surface_matrix = _bundle_item(evals_bundle, "host_surface_matrix")
    search_controller_plan = _bundle_item(search_bundle, "search_controller_plan")
    portfolio_search_trace = _bundle_item(search_bundle, "portfolio_search_trace")
    hpo_campaign_report = _bundle_item(search_bundle, "hpo_campaign_report")
    execution_backend_profile = _bundle_item(search_bundle, "execution_backend_profile")
    distributed_run_plan = _bundle_item(search_bundle, "distributed_run_plan")
    execution_strategy_report = _bundle_item(search_bundle, "execution_strategy_report")
    search_value_report = _bundle_item(search_bundle, "search_value_report")
    run_handoff = dict(handoff_bundle.get("run_handoff", {})) if isinstance(handoff_bundle.get("run_handoff"), dict) else {}
    next_run_options = dict(handoff_bundle.get("next_run_options", {})) if isinstance(handoff_bundle.get("next_run_options"), dict) else {}
    next_run_focus = dict(handoff_bundle.get("next_run_focus", {})) if isinstance(handoff_bundle.get("next_run_focus"), dict) else {}
    workspace_state = dict(workspace_bundle.get("workspace_state", {})) if isinstance(workspace_bundle.get("workspace_state"), dict) else {}
    workspace_lineage = dict(workspace_bundle.get("workspace_lineage", {})) if isinstance(workspace_bundle.get("workspace_lineage"), dict) else {}
    workspace_focus_history = dict(workspace_bundle.get("workspace_focus_history", {})) if isinstance(workspace_bundle.get("workspace_focus_history"), dict) else {}
    workspace_memory_policy = dict(workspace_bundle.get("workspace_memory_policy", {})) if isinstance(workspace_bundle.get("workspace_memory_policy"), dict) else {}
    result_contract = dict(result_contract_bundle.get("result_contract", {})) if isinstance(result_contract_bundle.get("result_contract"), dict) else {}
    confidence_posture = dict(result_contract_bundle.get("confidence_posture", {})) if isinstance(result_contract_bundle.get("confidence_posture"), dict) else {}
    belief_revision_triggers = dict(result_contract_bundle.get("belief_revision_triggers", {})) if isinstance(result_contract_bundle.get("belief_revision_triggers"), dict) else {}
    next_run_plan = dict(iteration_bundle.get("next_run_plan", {})) if isinstance(iteration_bundle.get("next_run_plan"), dict) else {}
    focus_decision_record = dict(iteration_bundle.get("focus_decision_record", {})) if isinstance(iteration_bundle.get("focus_decision_record"), dict) else {}
    data_expansion_candidates = dict(iteration_bundle.get("data_expansion_candidates", {})) if isinstance(iteration_bundle.get("data_expansion_candidates"), dict) else {}
    feedback_intake = _bundle_item(feedback_bundle, "feedback_intake")
    feedback_validation = _bundle_item(feedback_bundle, "feedback_validation")
    feedback_effect_report = _bundle_item(feedback_bundle, "feedback_effect_report")
    feedback_casebook = _bundle_item(feedback_bundle, "feedback_casebook")
    outcome_observation_report = _bundle_item(feedback_bundle, "outcome_observation_report")
    decision_policy_update_suggestions = _bundle_item(feedback_bundle, "decision_policy_update_suggestions")
    policy_update_suggestions = _bundle_item(feedback_bundle, "policy_update_suggestions")
    route_prior_updates = _bundle_item(feedback_bundle, "route_prior_updates")
    quality_contract = _bundle_item(profiles_bundle, "quality_contract")
    quality_gate_report = _bundle_item(profiles_bundle, "quality_gate_report")
    budget_contract = _bundle_item(profiles_bundle, "budget_contract")
    budget_consumption_report = _bundle_item(profiles_bundle, "budget_consumption_report")
    operator_profile = _bundle_item(profiles_bundle, "operator_profile")
    lab_operating_profile = _bundle_item(profiles_bundle, "lab_operating_profile")
    intervention_request = _bundle_item(control_bundle, "intervention_request")
    control_challenge_report = _bundle_item(control_bundle, "control_challenge_report")
    override_decision = _bundle_item(control_bundle, "override_decision")
    intervention_ledger = _bundle_item(control_bundle, "intervention_ledger")
    recovery_checkpoint = _bundle_item(control_bundle, "recovery_checkpoint")
    control_injection_audit = _bundle_item(control_bundle, "control_injection_audit")
    causal_memory_index = _bundle_item(control_bundle, "causal_memory_index")
    hook_execution_log = _bundle_item(runtime_bundle, "hook_execution_log")
    run_checkpoint_manifest = _bundle_item(runtime_bundle, "run_checkpoint_manifest")
    capability_profiles = _bundle_item(runtime_bundle, "capability_profiles")
    data_access_audit = _bundle_item(runtime_bundle, "data_access_audit")
    context_influence_report = _bundle_item(runtime_bundle, "context_influence_report")
    champion_vs_candidate = _bundle_item(lifecycle_bundle, "champion_vs_candidate")
    recalibration_decision = _bundle_item(lifecycle_bundle, "recalibration_decision")
    retrain_decision = _bundle_item(lifecycle_bundle, "retrain_decision")
    promotion_decision = _bundle_item(lifecycle_bundle, "promotion_decision")
    rollback_decision = _bundle_item(lifecycle_bundle, "rollback_decision")
    autonomy_loop_state = _bundle_item(autonomy_bundle, "autonomy_loop_state")
    autonomy_round_report = _bundle_item(autonomy_bundle, "autonomy_round_report")
    branch_outcome_matrix = _bundle_item(autonomy_bundle, "branch_outcome_matrix")
    champion_lineage = _bundle_item(autonomy_bundle, "champion_lineage")
    loop_budget_report = _bundle_item(autonomy_bundle, "loop_budget_report")
    runtime_events = _read_jsonl(root / "lab_event_stream.jsonl")
    execution_summary = dict(plan.get("execution_summary") or {})
    builder_handoff = dict(plan.get("builder_handoff") or {})
    marginal_value = _bundle_item(planning_bundle, "marginal_value_of_next_experiment")
    hook_executions = list(hook_execution_log.get("executions", [])) if isinstance(hook_execution_log.get("executions"), list) else []
    runtime_last_event = runtime_events[-1] if runtime_events else {}

    resolved_data_path = (
        str(Path(data_path))
        if data_path is not None
        else _first_data_reference(builder_handoff)
        or ""
    )
    latest_copy_paths = dict(data_copy_manifest.get("latest_by_purpose", {}))
    primary_copy_path = _clean_text(latest_copy_paths.get("primary"))
    inference_copy_path = _clean_text(latest_copy_paths.get("inference"))
    primary_copy_record = _find_copy_record(
        data_copy_manifest,
        staged_path=primary_copy_path,
        purpose="primary",
    )
    resolved_data_path = primary_copy_path or resolved_data_path
    selected_metrics = execution_summary.get("selected_metrics")
    if not isinstance(selected_metrics, dict):
        selected_metrics = {}
    summary = {
        "schema_version": RUN_SUMMARY_SCHEMA_VERSION,
        "generated_at": _utc_now(),
        "product": "Relaytic",
        "run_id": str(manifest.get("run_id", root.name or "run")),
        "run_dir": str(root),
        "status": _resolve_run_status(
            plan=plan,
            execution_summary=execution_summary,
            audit_report=audit_report,
            completion_decision=completion_decision,
            lifecycle_bundle=lifecycle_bundle,
        ),
        "stage_completed": _resolve_stage(
            plan=plan,
            execution_summary=execution_summary,
            investigation_bundle=investigation_bundle,
            intake_bundle=intake_bundle,
            evidence_bundle=evidence_bundle,
            intelligence_bundle=intelligence_bundle,
            research_bundle=research_bundle,
            benchmark_bundle=benchmark_bundle,
            decision_bundle=decision_bundle,
            dojo_bundle=dojo_bundle,
            pulse_bundle=pulse_bundle,
            search_bundle=search_bundle,
            handoff_bundle=handoff_bundle,
            learnings_state=learnings_state,
            learnings_snapshot=learnings_snapshot,
            profiles_bundle=profiles_bundle,
            feedback_bundle=feedback_bundle,
            control_bundle=control_bundle,
            completion_bundle=completion_bundle,
            lifecycle_bundle=lifecycle_bundle,
            autonomy_bundle=autonomy_bundle,
        ),
        "request": {
            "source": _clean_text(request_source) or _clean_text(intake_record.get("message_source")) or "unknown",
            "text_preview": _preview_text(request_text) or _preview_text(intake_record.get("message")),
            "actor_type": _clean_text(intake_record.get("actor_type")),
            "actor_name": _clean_text(intake_record.get("actor_name")),
            "channel": _clean_text(intake_record.get("channel")),
        },
        "data": {
            "data_path": resolved_data_path,
            "working_copy_path": primary_copy_path or resolved_data_path,
            "latest_inference_copy_path": inference_copy_path,
            "copy_enforced": bool(data_copy_manifest.get("copy_only", False)),
            "immutable_working_copies": bool(data_copy_manifest.get("immutable_working_copies", False)),
            "original_paths_persisted": bool(data_copy_manifest.get("original_paths_persisted", False)),
            "staged_copy_count": len(data_copy_manifest.get("copies", [])) if isinstance(data_copy_manifest.get("copies"), list) else 0,
            "source_format": _clean_text(_infer_data_format(resolved_data_path)),
            "source_type": _clean_text(primary_copy_record.get("source_kind")) or _clean_text(data_origin.get("source_type")),
            "materialized_input_format": _clean_text(primary_copy_record.get("materialized_format")),
            "row_count": int(dataset_profile.get("row_count", 0) or 0),
            "column_count": int(dataset_profile.get("column_count", 0) or 0),
            "data_mode": _clean_text(dataset_profile.get("data_mode")),
            "timestamp_column": _clean_text(dataset_profile.get("timestamp_column")),
        },
        "intent": {
            "objective": _clean_text(run_brief.get("objective")),
            "deployment_target": _clean_text(run_brief.get("deployment_target")),
            "problem_statement": _clean_text(task_brief.get("problem_statement")),
            "domain_archetype": _clean_text(_bundle_item(investigation_bundle, "domain_memo").get("domain_archetype"))
            or _clean_text(task_brief.get("domain_archetype_hint")),
            "autonomy_mode": _clean_text(autonomy_mode.get("requested_mode")),
            "operator_signal": _clean_text(autonomy_mode.get("operator_signal")),
        },
        "decision": {
            "target_column": _clean_text(plan.get("target_column") or task_brief.get("target_column")),
            "task_type": _clean_text(plan.get("task_type")) or _clean_text(task_brief.get("task_type_hint")),
            "primary_objective": _clean_text(focus_profile.get("primary_objective")),
            "selected_route_id": _clean_text(plan.get("selected_route_id")),
            "selected_route_title": _clean_text(plan.get("selected_route_title")),
            "selected_model_family": _clean_text(execution_summary.get("selected_model_family"))
            or _clean_text(model_params.get("model_name")),
            "best_validation_model_family": _clean_text(execution_summary.get("best_validation_model_family")),
            "primary_metric": _clean_text(plan.get("primary_metric"))
            or _clean_text(_bundle_item(investigation_bundle, "optimization_profile").get("primary_metric")),
            "split_strategy": _clean_text(plan.get("split_strategy")),
            "feature_columns": [str(item) for item in plan.get("feature_columns", []) if str(item).strip()],
            "guardrails": [str(item) for item in plan.get("guardrails", []) if str(item).strip()],
            "feature_risk_flags": list(builder_handoff.get("feature_risk_flags", [])),
        },
        "metrics": {
            "validation": dict(selected_metrics.get("validation", {})) if isinstance(selected_metrics.get("validation"), dict) else {},
            "test": dict(selected_metrics.get("test", {})) if isinstance(selected_metrics.get("test"), dict) else {},
        },
        "evidence": {
            "experiment_count": len(experiment_registry.get("experiments", [])) if isinstance(experiment_registry.get("experiments"), list) else 0,
            "challenger_winner": _clean_text(challenger_report.get("winner")),
            "challenger_delta_to_champion": challenger_report.get("delta_to_champion"),
            "provisional_recommendation": _clean_text(audit_report.get("provisional_recommendation")),
            "readiness_level": _clean_text(audit_report.get("readiness_level")),
            "recommended_action": _clean_text(belief_update.get("recommended_action")),
            "updated_belief": _clean_text(belief_update.get("updated_belief")),
            "load_bearing_features": [
                str(item.get("removed_feature", "")).strip()
                for item in ablation_report.get("ablations", [])
                if str(item.get("interpretation", "")).strip().startswith("Load-bearing")
            ][:5],
        },
        "completion": {
            "action": _clean_text(completion_decision.get("action")),
            "confidence": _clean_text(completion_decision.get("confidence")),
            "current_stage": _clean_text(run_state.get("current_stage")),
            "blocking_layer": _clean_text(completion_decision.get("blocking_layer"))
            or _clean_text(blocking_analysis.get("blocking_layer")),
            "mandate_alignment": _clean_text(completion_decision.get("mandate_alignment"))
            or _clean_text(mandate_evidence_review.get("alignment")),
            "evidence_state": _clean_text(completion_decision.get("evidence_state")),
            "complete_for_mode": completion_decision.get("complete_for_mode"),
            "next_action_count": len(next_action_queue.get("actions", [])) if isinstance(next_action_queue.get("actions"), list) else 0,
        },
        "memory": {
            "status": _clean_text(memory_retrieval.get("status")),
            "analog_count": int(memory_retrieval.get("selected_analog_count", 0) or 0),
            "top_analog_run_ids": [
                str(item)
                for item in memory_retrieval.get("analog_run_ids", [])
                if str(item).strip()
            ][:5],
            "route_prior_applied": str(route_prior_context.get("status", "")).strip() == "memory_influenced",
            "challenger_prior_family": _clean_text(challenger_prior_suggestions.get("preferred_challenger_family")),
            "reflection_stage": _clean_text(reflection_memory.get("current_stage")),
            "flush_stage": _clean_text(memory_flush_report.get("flush_stage")),
            "memory_delta": [
                str(item)
                for item in reflection_memory.get("memory_delta", [])
                if str(item).strip()
            ][:5],
            "top_relevance_reason": (
                _clean_text(dict((analog_run_candidates.get("candidates") or [{}])[0]).get("relevance_reason"))
                if isinstance(analog_run_candidates.get("candidates"), list) and analog_run_candidates.get("candidates")
                else None
            ),
        },
        "intelligence": {
            "configured_mode": _clean_literal_text(intelligence_mode.get("configured_mode")),
            "effective_mode": _clean_literal_text(intelligence_mode.get("effective_mode")),
            "routed_mode": _clean_literal_text(llm_routing_plan.get("selected_mode")),
            "recommended_mode": _clean_literal_text(llm_routing_plan.get("recommended_mode")),
            "local_profile": _clean_literal_text(local_llm_profile.get("profile_name")),
            "backend_status": _clean_text(intelligence_mode.get("backend_status")),
            "recommended_followup_action": _clean_text(semantic_debate_report.get("recommended_followup_action")),
            "debate_confidence": _clean_text(semantic_debate_report.get("confidence")),
            "domain_archetype": _clean_text(dict(semantic_debate_report.get("domain_interpretation") or {}).get("domain_archetype")),
            "modeling_bias": _clean_text(dict(semantic_debate_report.get("domain_interpretation") or {}).get("modeling_bias")),
            "uncertainty_band": _clean_text(semantic_uncertainty_report.get("confidence_band")),
            "escalation_required": bool(intelligence_escalation.get("escalation_required", False)),
            "semantic_gain_detected": bool(semantic_proof_report.get("measurable_gain_detected", False)),
        },
        "research": {
            "status": _clean_text(research_source_inventory.get("status")) or _clean_text(research_query_plan.get("status")),
            "source_count": int(dict(research_source_inventory.get("source_counts", {})).get("total_sources", 0) or 0),
            "provider_count": len(
                {
                    str(item.get("provider", "")).strip()
                    for item in research_source_inventory.get("sources", [])
                    if str(item.get("provider", "")).strip()
                }
            ),
            "recommended_followup_action": _clean_text(research_brief.get("recommended_followup_action")),
            "confidence": _clean_text(research_brief.get("confidence")),
            "accepted_transfer_count": len(method_transfer_report.get("accepted_candidates", [])),
            "rejected_transfer_count": len(method_transfer_report.get("rejected_candidates", [])),
            "benchmark_reference_count": int(benchmark_reference_report.get("reference_count", 0) or 0),
            "network_allowed": external_research_audit.get("network_allowed"),
        },
        "benchmark": {
            "status": _clean_text(benchmark_parity_report.get("status")) or _clean_text(reference_approach_matrix.get("status")),
            "parity_status": _clean_text(benchmark_parity_report.get("parity_status")),
            "recommended_action": _clean_text(benchmark_parity_report.get("recommended_action")),
            "comparison_metric": _clean_text(benchmark_parity_report.get("comparison_metric")) or _clean_text(reference_approach_matrix.get("comparison_metric")),
            "reference_count": int(benchmark_parity_report.get("reference_count", 0) or 0),
            "winning_family": _clean_text(benchmark_parity_report.get("winning_family")),
            "relaytic_family": _clean_text(benchmark_parity_report.get("relaytic_family")) or _clean_text(benchmark_gap_report.get("relaytic_family")),
            "test_gap": benchmark_gap_report.get("test_gap"),
            "validation_gap": benchmark_gap_report.get("validation_gap"),
            "near_parity": benchmark_gap_report.get("near_parity"),
            "incumbent_present": benchmark_parity_report.get("incumbent_present"),
            "incumbent_name": _clean_text(benchmark_parity_report.get("incumbent_name"))
            or _clean_text(incumbent_parity_report.get("incumbent_name"))
            or _clean_text(external_challenger_manifest.get("incumbent_name")),
            "incumbent_kind": _clean_text(incumbent_parity_report.get("incumbent_kind"))
            or _clean_text(external_challenger_manifest.get("incumbent_kind")),
            "incumbent_parity_status": _clean_text(incumbent_parity_report.get("parity_status")),
            "beat_target_state": _clean_text(beat_target_contract.get("contract_state"))
            or _clean_text(benchmark_parity_report.get("beat_target_state")),
            "relaytic_beats_incumbent": incumbent_parity_report.get("relaytic_beats_incumbent"),
            "incumbent_stronger": incumbent_parity_report.get("incumbent_stronger"),
            "incumbent_test_gap": incumbent_parity_report.get("test_gap"),
            "incumbent_reduced_claim": incumbent_parity_report.get("reduced_claim"),
            "incumbent_evaluation_mode": _clean_text(external_challenger_evaluation.get("evaluation_mode")),
        },
        "decision_lab": {
            "status": _clean_text(decision_world_model.get("status")),
            "action_regime": _clean_text(decision_world_model.get("action_regime")),
            "threshold_posture": _clean_text(decision_world_model.get("threshold_posture")),
            "under_specified": decision_world_model.get("under_specified"),
            "next_actor": _clean_text(controller_policy.get("next_actor")),
            "selected_next_action": _clean_text(controller_policy.get("selected_next_action")),
            "controller_mode": _clean_text(controller_policy.get("controller_mode")),
            "review_required": controller_policy.get("review_required"),
            "selected_strategy": _clean_text(value_of_more_data_report.get("selected_strategy")),
            "recommended_data_path": _clean_text(value_of_more_data_report.get("recommended_data_path"))
            or _clean_text(data_acquisition_plan.get("recommended_data_path")),
            "recommended_source_id": _clean_text(data_acquisition_plan.get("recommended_source_id")),
            "join_candidate_count": int(join_candidate_report.get("candidate_count", 0) or 0),
            "source_count": int(source_graph.get("source_count", 0) or 0),
            "compiled_challenger_count": int(method_compiler_report.get("compiled_challenger_count", 0) or 0),
            "compiled_feature_count": int(method_compiler_report.get("compiled_feature_count", 0) or 0),
            "compiled_benchmark_change_count": int(method_compiler_report.get("compiled_benchmark_change_count", 0) or 0),
            "changed_next_action": decision_usefulness_report.get("changed_next_action"),
            "changed_controller_path": decision_usefulness_report.get("changed_controller_path"),
            "baseline_action": _clean_text(handoff_controller_report.get("baseline_action")),
            "primary_decision_question": _clean_text(decision_world_model.get("primary_decision_question")),
        },
        "dojo": {
            "status": _clean_text(dojo_session.get("status")),
            "benchmark_state": _clean_text(dojo_session.get("benchmark_state")),
            "quality_gate_status": _clean_text(dojo_session.get("quality_gate_status")),
            "control_security_state": _clean_text(dojo_session.get("control_security_state")),
            "active_promotion_count": int(dojo_session.get("active_promotion_count", 0) or 0),
            "proposal_count": int(dojo_hypotheses.get("proposal_count", 0) or 0),
            "promoted_count": int(dojo_results.get("promoted_count", 0) or 0),
            "rejected_count": int(dojo_results.get("rejected_count", 0) or 0),
            "quarantined_count": int(dojo_results.get("quarantined_count", 0) or 0),
            "rolled_back_count": len(dojo_promotions.get("rolled_back_promotions", []))
            if isinstance(dojo_promotions.get("rolled_back_promotions"), list)
            else 0,
            "active_categories": [
                str(item.get("category", "")).strip()
                for item in dojo_promotions.get("active_promotions", [])
                if isinstance(item, dict) and str(item.get("category", "")).strip()
            ][:5],
            "architecture_proposal_count": int(architecture_proposals.get("proposal_count", 0) or 0),
        },
        "pulse": {
            "status": _clean_text(pulse_run_report.get("status")),
            "mode": _clean_text(pulse_schedule.get("mode")),
            "skip_reason": _clean_text(pulse_skip_report.get("skip_reason")),
            "due_now": pulse_schedule.get("due_now"),
            "throttled": pulse_schedule.get("throttled"),
            "queued_action_count": len(pulse_recommendations.get("queued_actions", []))
            if isinstance(pulse_recommendations.get("queued_actions"), list)
            else 0,
            "recommendation_count": int(pulse_run_report.get("recommendation_count", 0) or 0),
            "watchlist_count": int(pulse_run_report.get("watchlist_count", 0) or 0),
            "innovation_lead_count": int(pulse_run_report.get("innovation_lead_count", 0) or 0),
            "memory_pinned_count": int(memory_pinning_index.get("pin_count", 0) or 0),
            "compaction_executed": memory_compaction_report.get("executed"),
            "redacted_innovation": not bool(innovation_watch_report.get("raw_rows_exported"))
            and not bool(innovation_watch_report.get("identifier_leak_detected")),
            "top_watch_kind": (
                challenge_watchlist.get("items", [])[0].get("watch_kind")
                if isinstance(challenge_watchlist.get("items"), list) and challenge_watchlist.get("items")
                and isinstance(challenge_watchlist.get("items")[0], dict)
                else None
            ),
        },
        "trace": {
            "status": _clean_text(trace_model.get("status")),
            "span_count": int(trace_model.get("span_count", 0) or 0),
            "claim_count": int(trace_model.get("claim_count", 0) or 0),
            "branch_count": int(trace_model.get("branch_count", 0) or 0),
            "winning_claim_id": _clean_text(adjudication_scorecard.get("winning_claim_id")),
            "winning_action": _clean_text(adjudication_scorecard.get("winning_action")),
            "competing_claim_count": int(decision_replay_report.get("competing_claim_count", 0) or 0),
            "timeline_count": len(decision_replay_report.get("timeline", []))
            if isinstance(decision_replay_report.get("timeline"), list)
            else 0,
            "direct_runtime_emission_detected": trace_model.get("direct_runtime_emission_detected"),
        },
        "evals": {
            "status": _clean_text(agent_eval_matrix.get("status")),
            "passed_count": int(agent_eval_matrix.get("passed_count", 0) or 0),
            "failed_count": int(agent_eval_matrix.get("failed_count", 0) or 0),
            "not_applicable_count": int(agent_eval_matrix.get("not_applicable_count", 0) or 0),
            "protocol_status": _clean_text(protocol_conformance_report.get("status")),
            "protocol_mismatch_count": int(protocol_conformance_report.get("mismatch_count", 0) or 0),
            "security_status": _clean_text(security_eval_report.get("status")),
            "security_open_finding_count": int(security_eval_report.get("open_finding_count", 0) or 0),
            "red_team_status": _clean_text(red_team_report.get("status")),
            "red_team_finding_count": int(red_team_report.get("finding_count", 0) or 0),
            "surface_count": len(host_surface_matrix.get("surfaces", []))
            if isinstance(host_surface_matrix.get("surfaces"), list)
            else 0,
        },
        "search": {
            "status": _clean_text(search_controller_plan.get("status")),
            "recommended_action": _clean_text(search_controller_plan.get("recommended_action")),
            "recommended_direction": _clean_text(search_controller_plan.get("recommended_direction"))
            or _clean_text(search_value_report.get("recommended_direction")),
            "search_mode": _clean_text(search_controller_plan.get("search_mode")),
            "selected_hpo_depth": _clean_text(search_controller_plan.get("selected_hpo_depth")),
            "planned_trial_count": int(search_controller_plan.get("planned_trial_count", 0) or 0),
            "selected_execution_profile": _clean_text(search_controller_plan.get("selected_execution_profile"))
            or _clean_text(execution_backend_profile.get("selected_profile")),
            "value_band": _clean_text(search_value_report.get("value_band")),
            "value_score": search_value_report.get("value_score"),
            "stop_search_explicit": search_value_report.get("stop_search_explicit"),
            "beat_target_pressure": _clean_text(search_value_report.get("beat_target_pressure")),
            "review_need": _clean_text(search_value_report.get("review_need")),
            "widened_branch_count": int(portfolio_search_trace.get("widened_branch_count", 0) or 0),
            "pruned_branch_count": int(portfolio_search_trace.get("pruned_branch_count", 0) or 0),
            "candidate_branch_count": int(portfolio_search_trace.get("candidate_count", 0) or 0),
            "execution_strategy": _clean_text(execution_strategy_report.get("selected_strategy")),
            "execution_mode": _clean_text(distributed_run_plan.get("execution_mode")),
            "same_plan_across_profiles": execution_strategy_report.get("same_plan_across_profiles"),
            "max_trials": int(hpo_campaign_report.get("max_trials", 0) or 0),
        },
        "handoff": {
            "status": _clean_text(run_handoff.get("status")),
            "headline": _clean_text(run_handoff.get("headline")),
            "recommended_option_id": _clean_text(run_handoff.get("recommended_option_id")),
            "selected_focus_id": _clean_text(run_handoff.get("selected_focus_id"))
            or _clean_text(next_run_focus.get("selection_id")),
            "selected_focus_label": _clean_text(next_run_focus.get("selection_label")),
            "focus_notes": _clean_text(next_run_focus.get("notes")),
            "focus_reset_learnings_requested": next_run_focus.get("reset_learnings_requested"),
            "key_finding_count": len(run_handoff.get("key_findings", []))
            if isinstance(run_handoff.get("key_findings"), list)
            else 0,
            "risk_count": len(run_handoff.get("risks", []))
            if isinstance(run_handoff.get("risks"), list)
            else 0,
            "open_question_count": len(run_handoff.get("open_questions", []))
            if isinstance(run_handoff.get("open_questions"), list)
            else 0,
            "option_count": len(next_run_options.get("options", []))
            if isinstance(next_run_options.get("options"), list)
            else 0,
            "user_report_path": _path_if_exists(root / USER_RESULT_REPORT_RELATIVE_PATH),
            "agent_report_path": _path_if_exists(root / AGENT_RESULT_REPORT_RELATIVE_PATH),
        },
        "learnings": {
            "status": _clean_text(learnings_snapshot.get("status")) or _clean_text(learnings_state.get("status")),
            "state_dir": str(learnings_state_dir) if learnings_state_dir else None,
            "state_entry_count": int(learnings_snapshot.get("state_entry_count", 0) or learnings_state.get("entry_count", 0) or 0),
            "active_count": int(learnings_snapshot.get("active_count", 0) or 0),
            "harvested_count": int(learnings_snapshot.get("harvested_count", 0) or 0),
            "learnings_state_path": _path_if_exists(learnings_state_dir / "learnings_state.json"),
            "learnings_md_path": _path_if_exists(learnings_state_dir / "learnings.md"),
            "snapshot_path": _path_if_exists(root / "lab_learnings_snapshot.json"),
            "most_recent_lesson": _first_learning_lesson(learnings_snapshot=learnings_snapshot, learnings_state=learnings_state),
        },
        "workspace": {
            "status": _clean_text(workspace_state.get("status")),
            "workspace_id": _clean_text(workspace_state.get("workspace_id")),
            "workspace_label": _clean_text(workspace_state.get("workspace_label")),
            "workspace_dir": _clean_text(workspace_state.get("workspace_dir")) or str(workspace_dir),
            "current_run_id": _clean_text(workspace_state.get("current_run_id")),
            "current_focus": _clean_text(workspace_state.get("current_focus")),
            "continuity_mode": _clean_text(workspace_state.get("continuity_mode")),
            "prior_run_count": int(workspace_state.get("prior_run_count", 0) or 0),
            "lineage_run_count": int(workspace_lineage.get("run_count", 0) or 0),
            "focus_event_count": int(workspace_focus_history.get("event_count", 0) or 0),
            "active_learning_count": int(workspace_memory_policy.get("active_learning_count", 0) or 0),
            "reset_scope_count": len(workspace_memory_policy.get("reset_scopes", []))
            if isinstance(workspace_memory_policy.get("reset_scopes"), list)
            else 0,
        },
        "result_contract": {
            "status": _clean_text(result_contract.get("status")),
            "task_type": _clean_text(dict(result_contract.get("objective_summary", {})).get("task_type")),
            "target_summary": _clean_text(dict(result_contract.get("objective_summary", {})).get("target_summary")),
            "belief_count": len(result_contract.get("current_beliefs", []))
            if isinstance(result_contract.get("current_beliefs"), list)
            else 0,
            "unresolved_count": len(result_contract.get("unresolved_items", []))
            if isinstance(result_contract.get("unresolved_items"), list)
            else 0,
            "overall_strength": _clean_text(dict(result_contract.get("evidence_strength", {})).get("overall_strength")),
            "overall_confidence": _clean_text(confidence_posture.get("overall_confidence")),
            "review_need": _clean_text(confidence_posture.get("review_need")),
            "recommended_direction": _clean_text(dict(result_contract.get("recommended_next_move", {})).get("direction")),
            "recommended_action": _clean_text(dict(result_contract.get("recommended_next_move", {})).get("action")),
            "belief_revision_trigger_count": len(belief_revision_triggers.get("triggers", []))
            if isinstance(belief_revision_triggers.get("triggers"), list)
            else 0,
        },
        "iteration": {
            "status": _clean_text(next_run_plan.get("status")),
            "recommended_direction": _clean_text(next_run_plan.get("recommended_direction")),
            "primary_reason": _clean_text(next_run_plan.get("primary_reason")),
            "secondary_action_count": len(next_run_plan.get("secondary_actions", []))
            if isinstance(next_run_plan.get("secondary_actions"), list)
            else 0,
            "required_input_count": len(next_run_plan.get("required_user_inputs", []))
            if isinstance(next_run_plan.get("required_user_inputs"), list)
            else 0,
            "belief_revision_dependency": _clean_text(next_run_plan.get("belief_revision_dependency")),
            "focus_record_direction": _clean_text(focus_decision_record.get("selected_direction")),
            "data_expansion_candidate_count": int(data_expansion_candidates.get("candidate_count", 0) or 0),
        },
        "feedback": {
            "status": _clean_text(feedback_effect_report.get("status")) or _clean_text(feedback_validation.get("status")) or _clean_text(feedback_intake.get("status")),
            "accepted_count": int(feedback_validation.get("accepted_count", 0) or 0),
            "rejected_count": int(feedback_validation.get("rejected_count", 0) or 0),
            "reverted_count": int(feedback_validation.get("reverted_count", 0) or 0),
            "route_prior_update_count": len(route_prior_updates.get("updates", [])) if isinstance(route_prior_updates.get("updates"), list) else 0,
            "decision_policy_suggestion_count": len(decision_policy_update_suggestions.get("suggestions", []))
            if isinstance(decision_policy_update_suggestions.get("suggestions"), list)
            else 0,
            "policy_suggestion_count": len(policy_update_suggestions.get("suggestions", []))
            if isinstance(policy_update_suggestions.get("suggestions"), list)
            else 0,
            "primary_recommended_action": _clean_text(feedback_effect_report.get("primary_recommended_action"))
            or _clean_text(decision_policy_update_suggestions.get("primary_recommended_action")),
            "outcome_contradiction_count": int(outcome_observation_report.get("contradiction_count", 0) or 0),
            "casebook_accepted_count": len(feedback_casebook.get("accepted_cases", []))
            if isinstance(feedback_casebook.get("accepted_cases"), list)
            else 0,
        },
        "contracts": {
            "quality_contract_status": _clean_text(quality_contract.get("status")),
            "quality_gate_status": _clean_text(quality_gate_report.get("gate_status")) or _clean_text(quality_gate_report.get("status")),
            "quality_recommended_action": _clean_text(quality_gate_report.get("recommended_action")),
            "quality_state": _clean_text(quality_gate_report.get("quality_state")),
            "primary_metric": _clean_text(quality_contract.get("primary_metric")),
            "acceptance_criteria": dict(quality_contract.get("acceptance_criteria") or {}),
            "benchmark_required": quality_contract.get("benchmark_required"),
            "minimum_readiness_level": _clean_text(quality_contract.get("minimum_readiness_level")),
            "budget_posture": _clean_text(budget_contract.get("budget_posture")),
            "search_budget_posture": _clean_text(budget_contract.get("search_budget_posture")),
            "max_wall_clock_minutes": budget_contract.get("max_wall_clock_minutes"),
            "observed_elapsed_minutes": budget_consumption_report.get("observed_elapsed_minutes"),
            "max_trials": budget_contract.get("max_trials"),
            "estimated_trials_consumed": budget_consumption_report.get("estimated_trials_consumed"),
            "remaining_trials": budget_consumption_report.get("remaining_trials"),
            "max_branches_per_round": budget_contract.get("max_branches_per_round"),
            "used_branches": budget_consumption_report.get("used_branches"),
            "remaining_branch_budget": budget_consumption_report.get("remaining_branch_budget"),
            "budget_health": _clean_text(budget_consumption_report.get("budget_health")),
        },
        "profiles": {
            "operator_profile_name": _clean_text(operator_profile.get("profile_name")),
            "operator_review_strictness": _clean_text(operator_profile.get("review_strictness")),
            "operator_benchmark_appetite": _clean_text(operator_profile.get("benchmark_appetite")),
            "operator_budget_posture": _clean_text(operator_profile.get("budget_posture")),
            "operator_explanation_style": _clean_text(operator_profile.get("explanation_style")),
            "lab_profile_name": _clean_text(lab_operating_profile.get("profile_name")),
            "lab_review_strictness": _clean_text(lab_operating_profile.get("review_strictness")),
            "lab_risk_posture": _clean_text(lab_operating_profile.get("risk_posture")),
            "lab_budget_posture": _clean_text(lab_operating_profile.get("budget_posture")),
            "local_truth_required": lab_operating_profile.get("local_truth_required"),
            "remote_intelligence_allowed": lab_operating_profile.get("remote_intelligence_allowed"),
        },
        "control": {
            "request_classification": _clean_text(intervention_request.get("request_classification")),
            "requested_action_kind": _clean_text(intervention_request.get("requested_action_kind")),
            "decision": _clean_text(override_decision.get("decision")),
            "approved_action_kind": _clean_text(override_decision.get("approved_action_kind")),
            "approved_stage": _clean_text(override_decision.get("approved_stage")),
            "challenge_level": _clean_text(control_challenge_report.get("challenge_level")),
            "skepticism_level": _clean_text(control_challenge_report.get("skepticism_level")),
            "similar_harmful_override_count": int(control_challenge_report.get("similar_harmful_override_count", 0) or 0),
            "suspicious_count": int(control_injection_audit.get("suspicious_count", 0) or 0),
            "rejected_count": int(control_injection_audit.get("rejected_count", 0) or 0),
            "checkpoint_id": _clean_text(recovery_checkpoint.get("checkpoint_id")),
            "ledger_entry_count": int(intervention_ledger.get("entry_count", 0) or 0),
            "prior_run_count": int(causal_memory_index.get("prior_run_count", 0) or 0),
        },
        "runtime": {
            "current_stage": _resolve_runtime_stage(
                root,
                latest_stage=str(run_checkpoint_manifest.get("latest_stage", "")).strip(),
                last_event_stage=str(runtime_last_event.get("stage", "")).strip(),
            ),
            "event_count": len(runtime_events),
            "checkpoint_count": len(run_checkpoint_manifest.get("checkpoints", []))
            if isinstance(run_checkpoint_manifest.get("checkpoints"), list)
            else 0,
            "denied_access_count": int(data_access_audit.get("denied_count", 0) or 0),
            "active_specialist_count": len(capability_profiles.get("profiles", []))
            if isinstance(capability_profiles.get("profiles"), list)
            else 0,
            "read_only_hook_count": sum(1 for item in hook_executions if str(item.get("hook_type", "")).strip() == "read_only"),
            "write_hook_executed_count": sum(
                1
                for item in hook_executions
                if str(item.get("hook_type", "")).strip() == "write"
                and str(item.get("status", "")).strip() == "executed"
            ),
            "write_hook_blocked_count": sum(
                1
                for item in hook_executions
                if str(item.get("hook_type", "")).strip() == "write"
                and str(item.get("status", "")).strip() == "blocked_by_policy"
            ),
            "semantic_rowless_default": bool(dict(capability_profiles.get("controls", {})).get("semantic_rowless_default", True))
            if capability_profiles
            else None,
            "last_surface": _clean_text(runtime_last_event.get("source_surface")),
            "last_event_type": _clean_text(runtime_last_event.get("event_type")),
            "context_record_count": len(context_influence_report.get("stage_reports", []))
            if isinstance(context_influence_report.get("stage_reports"), list)
            else 0,
        },
        "lifecycle": {
            "promotion_action": _clean_text(promotion_decision.get("action")),
            "promotion_target": _clean_text(promotion_decision.get("selected_model_family")),
            "recalibration_action": _clean_text(recalibration_decision.get("action")),
            "retrain_action": _clean_text(retrain_decision.get("action")),
            "rollback_action": _clean_text(rollback_decision.get("action")),
            "challenger_winner": _clean_text(champion_vs_candidate.get("challenger_winner")),
            "drift_score": (dict(champion_vs_candidate.get("fresh_data_behavior") or {}).get("drift_summary") or {}).get("overall_drift_score"),
            "ood_fraction": (dict(champion_vs_candidate.get("fresh_data_behavior") or {}).get("ood_summary") or {}).get("overall_ood_fraction"),
        },
        "autonomy": {
            "status": _clean_text(autonomy_loop_state.get("status")),
            "selected_action": _clean_text(autonomy_loop_state.get("selected_action")),
            "promotion_applied": bool(autonomy_loop_state.get("promotion_applied", False)),
            "winning_branch_id": _clean_text(branch_outcome_matrix.get("winning_branch_id")),
            "executed_branch_count": len(branch_outcome_matrix.get("branches", [])) if isinstance(branch_outcome_matrix.get("branches"), list) else 0,
            "current_champion": _clean_text(champion_lineage.get("current_model_family")),
            "budget_remaining": loop_budget_report.get("budget_remaining"),
            "local_data_candidate_count": len(autonomy_round_report.get("local_data_candidates", [])) if isinstance(autonomy_round_report.get("local_data_candidates"), list) else 0,
        },
        "assumptions": {
            "count": len(assumption_entries),
            "items": [str(item.get("assumption", "")).strip() for item in assumption_entries if str(item.get("assumption", "")).strip()][:5],
        },
        "next_step": {
            "recommended_experiment_id": _clean_text(marginal_value.get("recommended_experiment_id")),
            "estimated_value_band": _clean_text(marginal_value.get("estimated_value_band")),
            "rationale": _clean_text(
                feedback_effect_report.get("summary", "")
                or decision_usefulness_report.get("summary", "")
                or value_of_more_data_report.get("summary", "")
                or decision_policy_update_suggestions.get("summary", "")
                or route_prior_updates.get("summary", "")
                or policy_update_suggestions.get("summary", "")
                or outcome_observation_report.get("summary", "")
                or
                completion_decision.get("summary", "")
                or belief_update.get("summary", "")
                or marginal_value.get("rationale", "")
            ),
            "recommended_action": _clean_text(feedback_effect_report.get("primary_recommended_action"))
            or _clean_text(decision_policy_update_suggestions.get("primary_recommended_action"))
            or (
                _clean_text(controller_policy.get("selected_next_action"))
                if _clean_text(value_of_more_data_report.get("selected_strategy")) not in {None, "hold_current_course"}
                else None
            )
            or _lifecycle_primary_action(lifecycle_bundle)
            or _clean_text(completion_decision.get("action"))
            or _clean_text(belief_update.get("recommended_action")),
        },
        "artifacts": {
            "manifest_path": _path_if_exists(root / "manifest.json"),
            "plan_path": _path_if_exists(root / "plan.json"),
            "model_params_path": _path_if_exists(root / "model_params.json"),
            "model_state_path": _resolve_model_state_path(root, execution_summary=execution_summary),
            "report_path": _path_if_exists(root / RUN_REPORT_RELATIVE_PATH),
            "leaderboard_path": _path_if_exists(root / "leaderboard.csv"),
            "technical_report_path": _path_if_exists(root / "reports" / "technical_report.md"),
            "decision_memo_path": _path_if_exists(root / "reports" / "decision_memo.md"),
            "completion_decision_path": _path_if_exists(root / "completion_decision.json"),
            "promotion_decision_path": _path_if_exists(root / "promotion_decision.json"),
            "research_brief_path": _path_if_exists(root / "research_brief.json"),
            "method_transfer_report_path": _path_if_exists(root / "method_transfer_report.json"),
            "external_research_audit_path": _path_if_exists(root / "external_research_audit.json"),
            "benchmark_parity_report_path": _path_if_exists(root / "benchmark_parity_report.json"),
            "benchmark_gap_report_path": _path_if_exists(root / "benchmark_gap_report.json"),
            "external_challenger_manifest_path": _path_if_exists(root / "external_challenger_manifest.json"),
            "external_challenger_evaluation_path": _path_if_exists(root / "external_challenger_evaluation.json"),
            "incumbent_parity_report_path": _path_if_exists(root / "incumbent_parity_report.json"),
            "beat_target_contract_path": _path_if_exists(root / "beat_target_contract.json"),
            "decision_world_model_path": _path_if_exists(root / "decision_world_model.json"),
            "controller_policy_path": _path_if_exists(root / "controller_policy.json"),
            "value_of_more_data_report_path": _path_if_exists(root / "value_of_more_data_report.json"),
            "method_compiler_report_path": _path_if_exists(root / "method_compiler_report.json"),
            "source_graph_path": _path_if_exists(root / "source_graph.json"),
            "join_candidate_report_path": _path_if_exists(root / "join_candidate_report.json"),
            "dojo_session_path": _path_if_exists(root / "dojo_session.json"),
            "dojo_hypotheses_path": _path_if_exists(root / "dojo_hypotheses.json"),
            "dojo_results_path": _path_if_exists(root / "dojo_results.json"),
            "dojo_promotions_path": _path_if_exists(root / "dojo_promotions.json"),
            "architecture_proposals_path": _path_if_exists(root / "architecture_proposals.json"),
            "pulse_schedule_path": _path_if_exists(root / "pulse_schedule.json"),
            "pulse_run_report_path": _path_if_exists(root / "pulse_run_report.json"),
            "pulse_skip_report_path": _path_if_exists(root / "pulse_skip_report.json"),
            "pulse_recommendations_path": _path_if_exists(root / "pulse_recommendations.json"),
            "innovation_watch_report_path": _path_if_exists(root / "innovation_watch_report.json"),
            "challenge_watchlist_path": _path_if_exists(root / "challenge_watchlist.json"),
            "memory_compaction_report_path": _path_if_exists(root / "memory_compaction_report.json"),
            "memory_pinning_index_path": _path_if_exists(root / "memory_pinning_index.json"),
            "trace_model_path": _path_if_exists(root / "trace_model.json"),
            "specialist_trace_index_path": _path_if_exists(root / "specialist_trace_index.json"),
            "branch_trace_graph_path": _path_if_exists(root / "branch_trace_graph.json"),
            "adjudication_scorecard_path": _path_if_exists(root / "adjudication_scorecard.json"),
            "decision_replay_report_path": _path_if_exists(root / "decision_replay_report.json"),
            "trace_span_log_path": _path_if_exists(root / "trace_span_log.jsonl"),
            "claim_packet_log_path": _path_if_exists(root / "claim_packet_log.jsonl"),
            "agent_eval_matrix_path": _path_if_exists(root / "agent_eval_matrix.json"),
            "security_eval_report_path": _path_if_exists(root / "security_eval_report.json"),
            "red_team_report_path": _path_if_exists(root / "red_team_report.json"),
            "protocol_conformance_report_path": _path_if_exists(root / "protocol_conformance_report.json"),
            "host_surface_matrix_path": _path_if_exists(root / "host_surface_matrix.json"),
            "search_controller_plan_path": _path_if_exists(root / "search_controller_plan.json"),
            "portfolio_search_trace_path": _path_if_exists(root / "portfolio_search_trace.json"),
            "hpo_campaign_report_path": _path_if_exists(root / "hpo_campaign_report.json"),
            "search_decision_ledger_path": _path_if_exists(root / "search_decision_ledger.json"),
            "execution_backend_profile_path": _path_if_exists(root / "execution_backend_profile.json"),
            "device_allocation_path": _path_if_exists(root / "device_allocation.json"),
            "distributed_run_plan_path": _path_if_exists(root / "distributed_run_plan.json"),
            "scheduler_job_map_path": _path_if_exists(root / "scheduler_job_map.json"),
            "checkpoint_state_path": _path_if_exists(root / "checkpoint_state.json"),
            "execution_strategy_report_path": _path_if_exists(root / "execution_strategy_report.json"),
            "search_value_report_path": _path_if_exists(root / "search_value_report.json"),
            "search_controller_eval_report_path": _path_if_exists(root / "search_controller_eval_report.json"),
            "run_handoff_path": _path_if_exists(root / "run_handoff.json"),
            "next_run_options_path": _path_if_exists(root / "next_run_options.json"),
            "next_run_focus_path": _path_if_exists(root / "next_run_focus.json"),
            "user_result_report_path": _path_if_exists(root / USER_RESULT_REPORT_RELATIVE_PATH),
            "agent_result_report_path": _path_if_exists(root / AGENT_RESULT_REPORT_RELATIVE_PATH),
            "lab_learnings_snapshot_path": _path_if_exists(root / "lab_learnings_snapshot.json"),
            "learnings_state_path": _path_if_exists(learnings_state_dir / "learnings_state.json"),
            "learnings_md_path": _path_if_exists(learnings_state_dir / "learnings.md"),
            "workspace_state_path": _path_if_exists(workspace_dir / "workspace_state.json"),
            "workspace_lineage_path": _path_if_exists(workspace_dir / "workspace_lineage.json"),
            "workspace_focus_history_path": _path_if_exists(workspace_dir / "workspace_focus_history.json"),
            "workspace_memory_policy_path": _path_if_exists(workspace_dir / "workspace_memory_policy.json"),
            "result_contract_path": _path_if_exists(root / "result_contract.json"),
            "confidence_posture_path": _path_if_exists(root / "confidence_posture.json"),
            "belief_revision_triggers_path": _path_if_exists(root / "belief_revision_triggers.json"),
            "next_run_plan_path": _path_if_exists(workspace_dir / "next_run_plan.json"),
            "focus_decision_record_path": _path_if_exists(root / "focus_decision_record.json"),
            "data_expansion_candidates_path": _path_if_exists(root / "data_expansion_candidates.json"),
            "feedback_effect_report_path": _path_if_exists(root / "feedback_effect_report.json"),
            "feedback_casebook_path": _path_if_exists(root / "feedback_casebook.json"),
            "quality_contract_path": _path_if_exists(root / "quality_contract.json"),
            "quality_gate_report_path": _path_if_exists(root / "quality_gate_report.json"),
            "budget_contract_path": _path_if_exists(root / "budget_contract.json"),
            "budget_consumption_report_path": _path_if_exists(root / "budget_consumption_report.json"),
            "override_decision_path": _path_if_exists(root / "override_decision.json"),
            "control_challenge_report_path": _path_if_exists(root / "control_challenge_report.json"),
            "intervention_memory_log_path": _path_if_exists(root / "intervention_memory_log.json"),
            "event_stream_path": _path_if_exists(root / "lab_event_stream.jsonl"),
            "capability_profiles_path": _path_if_exists(root / "capability_profiles.json"),
        },
    }
    summary["headline"] = _build_headline(summary)
    return summary


def render_run_summary_markdown(summary: dict[str, Any]) -> str:
    """Render a concise markdown summary for humans."""
    decision = dict(summary.get("decision", {}))
    data = dict(summary.get("data", {}))
    intent = dict(summary.get("intent", {}))
    metrics = dict(summary.get("metrics", {}))
    evidence = dict(summary.get("evidence", {}))
    completion = dict(summary.get("completion", {}))
    memory = dict(summary.get("memory", {}))
    intelligence = dict(summary.get("intelligence", {}))
    research = dict(summary.get("research", {}))
    benchmark = dict(summary.get("benchmark", {}))
    decision_lab = dict(summary.get("decision_lab", {}))
    dojo = dict(summary.get("dojo", {}))
    pulse = dict(summary.get("pulse", {}))
    trace = dict(summary.get("trace", {}))
    evals = dict(summary.get("evals", {}))
    search = dict(summary.get("search", {}))
    handoff = dict(summary.get("handoff", {}))
    learnings = dict(summary.get("learnings", {}))
    workspace = dict(summary.get("workspace", {}))
    result_contract = dict(summary.get("result_contract", {}))
    iteration = dict(summary.get("iteration", {}))
    feedback = dict(summary.get("feedback", {}))
    contracts = dict(summary.get("contracts", {}))
    profiles = dict(summary.get("profiles", {}))
    control = dict(summary.get("control", {}))
    runtime = dict(summary.get("runtime", {}))
    lifecycle = dict(summary.get("lifecycle", {}))
    autonomy = dict(summary.get("autonomy", {}))
    assumptions = dict(summary.get("assumptions", {}))
    next_step = dict(summary.get("next_step", {}))
    lines = [
        "# Relaytic Run Summary",
        "",
        summary.get("headline", "Relaytic completed the requested run."),
        "",
        "## Result",
        f"- Status: `{summary.get('status', 'unknown')}`",
        f"- Target: `{decision.get('target_column') or 'unknown'}`",
        f"- Task type: `{decision.get('task_type') or 'unknown'}`",
        f"- Route: `{decision.get('selected_route_title') or decision.get('selected_route_id') or 'not planned'}`",
        f"- Model: `{decision.get('selected_model_family') or 'not executed'}`",
        f"- Primary metric: `{decision.get('primary_metric') or 'unknown'}`",
        "",
        "## Intent",
        f"- Objective: `{intent.get('objective') or 'unspecified'}`",
        f"- Autonomy mode: `{intent.get('autonomy_mode') or 'unknown'}`",
        f"- Deployment target: `{intent.get('deployment_target') or 'unspecified'}`",
        f"- Domain archetype: `{intent.get('domain_archetype') or 'generic_tabular'}`",
        "",
        "## Data",
        f"- Rows: `{data.get('row_count', 0)}`",
        f"- Columns: `{data.get('column_count', 0)}`",
        f"- Data mode: `{data.get('data_mode') or 'unknown'}`",
        f"- Format: `{data.get('source_format') or 'unknown'}`",
        f"- Source type: `{data.get('source_type') or 'unknown'}`",
        f"- Copy enforced: `{data.get('copy_enforced')}`",
    ]
    if data.get("working_copy_path"):
        lines.append(f"- Working copy: `{data.get('working_copy_path')}`")
    feature_columns = list(decision.get("feature_columns", []))
    if feature_columns:
        lines.append(f"- First-route features: `{', '.join(feature_columns)}`")
    validation_metrics = dict(metrics.get("validation", {}))
    test_metrics = dict(metrics.get("test", {}))
    if validation_metrics or test_metrics:
        lines.extend(
            [
                "",
                "## Metrics",
                f"- Validation: {_format_metric_block(validation_metrics)}",
                f"- Test: {_format_metric_block(test_metrics)}",
            ]
        )
    if decision.get("guardrails"):
        lines.extend(
            [
                "",
                "## Guardrails",
                f"- {str(decision['guardrails'][0])}",
            ]
        )
    feature_risk_flags = list(decision.get("feature_risk_flags", []))
    if feature_risk_flags:
        lines.append(
            "- Retained risk-flagged features: `"
            + ", ".join(str(item.get("column", "")).strip() for item in feature_risk_flags if str(item.get("column", "")).strip())
            + "`"
        )
    if evidence:
        lines.extend(
            [
                "",
                "## Evidence",
                f"- Experiments logged: `{evidence.get('experiment_count', 0)}`",
                f"- Challenger winner: `{evidence.get('challenger_winner') or 'unknown'}`",
                f"- Provisional recommendation: `{evidence.get('provisional_recommendation') or 'unknown'}`",
                f"- Readiness: `{evidence.get('readiness_level') or 'unknown'}`",
            ]
        )
        if evidence.get("updated_belief"):
            lines.append(f"- Belief update: {evidence['updated_belief']}")
        load_bearing = list(evidence.get("load_bearing_features", []))
        if load_bearing:
            lines.append(f"- Load-bearing features: `{', '.join(load_bearing)}`")
    if completion:
        lines.extend(
            [
                "",
                "## Completion",
                f"- Current stage: `{completion.get('current_stage') or summary.get('stage_completed') or 'unknown'}`",
                f"- Recommended action: `{completion.get('action') or next_step.get('recommended_action') or 'unknown'}`",
                f"- Blocking layer: `{completion.get('blocking_layer') or 'none'}`",
                f"- Mandate alignment: `{completion.get('mandate_alignment') or 'unknown'}`",
                f"- Complete for mode: `{completion.get('complete_for_mode')}`",
            ]
        )
    if memory and (memory.get("status") or memory.get("analog_count", 0)):
        lines.extend(
            [
                "",
                "## Memory",
                f"- Retrieval status: `{memory.get('status') or 'unknown'}`",
                f"- Analog candidates: `{memory.get('analog_count', 0)}`",
                f"- Route prior applied: `{memory.get('route_prior_applied')}`",
                f"- Challenger prior: `{memory.get('challenger_prior_family') or 'none'}`",
            ]
        )
        if memory.get("top_relevance_reason"):
            lines.append(f"- Top analog rationale: {memory['top_relevance_reason']}")
        if memory.get("top_analog_run_ids"):
            lines.append(f"- Top analog runs: `{', '.join(memory['top_analog_run_ids'])}`")
    if intelligence and any(value is not None for value in intelligence.values()):
        lines.extend(
            [
                "",
                "## Intelligence",
                f"- Effective mode: `{intelligence.get('effective_mode') or 'unknown'}`",
                f"- Routed mode: `{intelligence.get('routed_mode') or 'unknown'}`",
                f"- Recommended mode: `{intelligence.get('recommended_mode') or 'unknown'}`",
                f"- Local profile: `{intelligence.get('local_profile') or 'unknown'}`",
                f"- Backend status: `{intelligence.get('backend_status') or 'unknown'}`",
                f"- Semantic follow-up: `{intelligence.get('recommended_followup_action') or 'none'}`",
                f"- Debate confidence: `{intelligence.get('debate_confidence') or 'unknown'}`",
                f"- Domain archetype: `{intelligence.get('domain_archetype') or 'unknown'}`",
                f"- Modeling bias: `{intelligence.get('modeling_bias') or 'unknown'}`",
                f"- Uncertainty band: `{intelligence.get('uncertainty_band') or 'unknown'}`",
                f"- Semantic gain detected: `{intelligence.get('semantic_gain_detected')}`",
            ]
        )
        if intelligence.get("escalation_required") is not None:
            lines.append(f"- Escalation required: `{intelligence.get('escalation_required')}`")
    if research and any(value is not None for value in research.values()):
        lines.extend(
            [
                "",
                "## Research",
                f"- Status: `{research.get('status') or 'unknown'}`",
                f"- Sources: `{research.get('source_count', 0)}`",
                f"- Providers: `{research.get('provider_count', 0)}`",
                f"- Follow-up: `{research.get('recommended_followup_action') or 'none'}`",
                f"- Confidence: `{research.get('confidence') or 'unknown'}`",
                f"- Accepted transfers: `{research.get('accepted_transfer_count', 0)}`",
                f"- Benchmark references: `{research.get('benchmark_reference_count', 0)}`",
            ]
        )
    if benchmark and any(value is not None for value in benchmark.values()):
        lines.extend(
            [
                "",
                "## Benchmark",
                f"- Status: `{benchmark.get('status') or 'unknown'}`",
                f"- Parity status: `{benchmark.get('parity_status') or 'unknown'}`",
                f"- Recommended action: `{benchmark.get('recommended_action') or 'none'}`",
                f"- Comparison metric: `{benchmark.get('comparison_metric') or 'unknown'}`",
                f"- Reference count: `{benchmark.get('reference_count', 0)}`",
                f"- Winning family: `{benchmark.get('winning_family') or 'unknown'}`",
                f"- Test gap: `{benchmark.get('test_gap')}`",
                f"- Near parity: `{benchmark.get('near_parity')}`",
                f"- Incumbent: `{benchmark.get('incumbent_name') or 'none'}`",
                f"- Incumbent parity: `{benchmark.get('incumbent_parity_status') or 'unknown'}`",
                f"- Beat-target state: `{benchmark.get('beat_target_state') or 'unknown'}`",
            ]
        )
    if decision_lab and any(value is not None for value in decision_lab.values()):
        lines.extend(
            [
                "",
                "## Decision Lab",
                f"- Action regime: `{decision_lab.get('action_regime') or 'unknown'}`",
                f"- Threshold posture: `{decision_lab.get('threshold_posture') or 'unknown'}`",
                f"- Under-specified: `{decision_lab.get('under_specified')}`",
                f"- Selected strategy: `{decision_lab.get('selected_strategy') or 'unknown'}`",
                f"- Next actor: `{decision_lab.get('next_actor') or 'unknown'}`",
                f"- Selected next action: `{decision_lab.get('selected_next_action') or 'unknown'}`",
                f"- Review required: `{decision_lab.get('review_required')}`",
                f"- Join candidates: `{decision_lab.get('join_candidate_count', 0)}`",
                f"- Compiled challengers: `{decision_lab.get('compiled_challenger_count', 0)}`",
                f"- Changed controller path: `{decision_lab.get('changed_controller_path')}`",
            ]
        )
        if decision_lab.get("recommended_source_id"):
            lines.append(f"- Recommended local source: `{decision_lab.get('recommended_source_id')}`")
    if dojo and any(value not in (None, 0, False, "", []) for value in dojo.values()):
        lines.extend(
            [
                "",
                "## Dojo",
                f"- Status: `{dojo.get('status') or 'unknown'}`",
                f"- Benchmark state: `{dojo.get('benchmark_state') or 'unknown'}`",
                f"- Quality gate: `{dojo.get('quality_gate_status') or 'unknown'}`",
                f"- Control security: `{dojo.get('control_security_state') or 'unknown'}`",
                f"- Active promotions: `{dojo.get('active_promotion_count', 0)}`",
                f"- Rejected proposals: `{dojo.get('rejected_count', 0)}`",
                f"- Quarantined proposals: `{dojo.get('quarantined_count', 0)}`",
                f"- Rolled back promotions: `{dojo.get('rolled_back_count', 0)}`",
            ]
        )
        categories = [str(item).strip() for item in dojo.get("active_categories", []) if str(item).strip()]
        if categories:
            lines.append(f"- Active categories: `{', '.join(categories)}`")
    if pulse and any(value not in (None, 0, False, "", []) for value in pulse.values()):
        lines.extend(
            [
                "",
                "## Pulse",
                f"- Status: `{pulse.get('status') or 'unknown'}`",
                f"- Mode: `{pulse.get('mode') or 'unknown'}`",
                f"- Skip reason: `{pulse.get('skip_reason') or 'none'}`",
                f"- Due now: `{pulse.get('due_now')}`",
                f"- Throttled: `{pulse.get('throttled')}`",
                f"- Recommendations: `{pulse.get('recommendation_count', 0)}`",
                f"- Watchlist items: `{pulse.get('watchlist_count', 0)}`",
                f"- Innovation leads: `{pulse.get('innovation_lead_count', 0)}`",
                f"- Queued actions: `{pulse.get('queued_action_count', 0)}`",
                f"- Memory pinned: `{pulse.get('memory_pinned_count', 0)}`",
                f"- Compaction executed: `{pulse.get('compaction_executed')}`",
                f"- Redacted innovation: `{pulse.get('redacted_innovation')}`",
            ]
        )
        if pulse.get("top_watch_kind"):
            lines.append(f"- Top watch kind: `{pulse.get('top_watch_kind')}`")
    if trace and any(value not in (None, 0, False, "", []) for value in trace.values()):
        lines.extend(
            [
                "",
                "## Trace",
                f"- Status: `{trace.get('status') or 'unknown'}`",
                f"- Spans: `{trace.get('span_count', 0)}`",
                f"- Claims: `{trace.get('claim_count', 0)}`",
                f"- Winning claim: `{trace.get('winning_claim_id') or 'unknown'}`",
                f"- Winning action: `{trace.get('winning_action') or 'unknown'}`",
                f"- Replay timeline: `{trace.get('timeline_count', 0)}`",
                f"- Direct runtime emission: `{trace.get('direct_runtime_emission_detected')}`",
            ]
        )
    if evals and any(value not in (None, 0, False, "", []) for value in evals.values()):
        lines.extend(
            [
                "",
                "## Evals",
                f"- Status: `{evals.get('status') or 'unknown'}`",
                f"- Passed: `{evals.get('passed_count', 0)}`",
                f"- Failed: `{evals.get('failed_count', 0)}`",
                f"- Protocol status: `{evals.get('protocol_status') or 'unknown'}`",
                f"- Security status: `{evals.get('security_status') or 'unknown'}`",
                f"- Red-team status: `{evals.get('red_team_status') or 'unknown'}`",
            ]
        )
        if evals.get("protocol_mismatch_count"):
            lines.append(f"- Protocol mismatches: `{evals.get('protocol_mismatch_count')}`")
        if evals.get("security_open_finding_count"):
            lines.append(f"- Open security findings: `{evals.get('security_open_finding_count')}`")
    if search and any(value not in (None, 0, False, "", []) for value in search.values()):
        lines.extend(
            [
                "",
                "## Search Controller",
                f"- Status: `{search.get('status') or 'unknown'}`",
                f"- Action: `{search.get('recommended_action') or 'unknown'}`",
                f"- Direction: `{search.get('recommended_direction') or 'unknown'}`",
                f"- Value band: `{search.get('value_band') or 'unknown'}`",
                f"- Search mode: `{search.get('search_mode') or 'unknown'}`",
                f"- Planned trials: `{search.get('planned_trial_count', 0)}`",
                f"- Execution profile: `{search.get('selected_execution_profile') or 'unknown'}`",
                f"- Widened branches: `{search.get('widened_branch_count', 0)}`",
                f"- Pruned branches: `{search.get('pruned_branch_count', 0)}`",
                f"- Stop search explicitly: `{search.get('stop_search_explicit')}`",
            ]
        )
    if handoff and any(value not in (None, 0, False, "", []) for value in handoff.values()):
        lines.extend(
            [
                "",
                "## Handoff",
                f"- Status: `{handoff.get('status') or 'unknown'}`",
                f"- Recommended next-run option: `{handoff.get('recommended_option_id') or 'unknown'}`",
                f"- Selected focus: `{handoff.get('selected_focus_id') or 'none'}`",
                f"- Selected focus label: `{handoff.get('selected_focus_label') or 'none'}`",
                f"- Findings: `{handoff.get('key_finding_count', 0)}`",
                f"- Risks: `{handoff.get('risk_count', 0)}`",
                f"- Open questions: `{handoff.get('open_question_count', 0)}`",
            ]
        )
        if handoff.get("focus_notes"):
            lines.append(f"- Focus notes: {handoff.get('focus_notes')}")
        if handoff.get("user_report_path"):
            lines.append(f"- User report: `{handoff.get('user_report_path')}`")
        if handoff.get("agent_report_path"):
            lines.append(f"- Agent report: `{handoff.get('agent_report_path')}`")
        if handoff.get("focus_reset_learnings_requested") is not None:
            lines.append(f"- Reset learnings requested: `{handoff.get('focus_reset_learnings_requested')}`")
    if learnings and any(value not in (None, 0, False, "", []) for value in learnings.values()):
        lines.extend(
            [
                "",
                "## Learnings",
                f"- Status: `{learnings.get('status') or 'unknown'}`",
                f"- Stored learnings: `{learnings.get('state_entry_count', 0)}`",
                f"- Active this run: `{learnings.get('active_count', 0)}`",
                f"- Harvested this run: `{learnings.get('harvested_count', 0)}`",
            ]
        )
        if learnings.get("most_recent_lesson"):
            lines.append(f"- Most recent lesson: {learnings.get('most_recent_lesson')}")
        if learnings.get("learnings_md_path"):
            lines.append(f"- Learnings handbook: `{learnings.get('learnings_md_path')}`")
    if workspace and any(value not in (None, 0, False, "", []) for value in workspace.values()):
        lines.extend(
            [
                "",
                "## Workspace",
                f"- Workspace: `{workspace.get('workspace_label') or workspace.get('workspace_id') or 'unknown'}`",
                f"- Continuity mode: `{workspace.get('continuity_mode') or 'unknown'}`",
                f"- Current focus: `{workspace.get('current_focus') or 'none'}`",
                f"- Prior runs: `{workspace.get('prior_run_count', 0)}`",
                f"- Focus events: `{workspace.get('focus_event_count', 0)}`",
            ]
        )
    if result_contract and any(value not in (None, 0, False, "", []) for value in result_contract.values()):
        lines.extend(
            [
                "",
                "## Result Contract",
                f"- Status: `{result_contract.get('status') or 'unknown'}`",
                f"- Task type: `{result_contract.get('task_type') or 'unknown'}`",
                f"- Target summary: `{result_contract.get('target_summary') or 'unknown'}`",
                f"- Beliefs: `{result_contract.get('belief_count', 0)}`",
                f"- Unresolved items: `{result_contract.get('unresolved_count', 0)}`",
                f"- Overall strength: `{result_contract.get('overall_strength') or 'unknown'}`",
                f"- Overall confidence: `{result_contract.get('overall_confidence') or 'unknown'}`",
                f"- Review need: `{result_contract.get('review_need') or 'unknown'}`",
                f"- Recommended direction: `{result_contract.get('recommended_direction') or 'unknown'}`",
                f"- Recommended action: `{result_contract.get('recommended_action') or 'unknown'}`",
                f"- Belief revision triggers: `{result_contract.get('belief_revision_trigger_count', 0)}`",
            ]
        )
    if iteration and any(value not in (None, 0, False, "", []) for value in iteration.values()):
        lines.extend(
            [
                "",
                "## Next-Run Plan",
                f"- Recommended direction: `{iteration.get('recommended_direction') or 'unknown'}`",
                f"- Primary reason: {iteration.get('primary_reason') or 'unknown'}",
                f"- Secondary actions: `{iteration.get('secondary_action_count', 0)}`",
                f"- Required inputs: `{iteration.get('required_input_count', 0)}`",
                f"- Focus record: `{iteration.get('focus_record_direction') or 'none'}`",
                f"- Data expansion candidates: `{iteration.get('data_expansion_candidate_count', 0)}`",
            ]
        )
    if feedback and any(value not in (None, 0, False, "", []) for value in feedback.values()):
        lines.extend(
            [
                "",
                "## Feedback",
                f"- Status: `{feedback.get('status') or 'unknown'}`",
                f"- Accepted feedback: `{feedback.get('accepted_count', 0)}`",
                f"- Rejected feedback: `{feedback.get('rejected_count', 0)}`",
                f"- Reverted feedback: `{feedback.get('reverted_count', 0)}`",
                f"- Route prior updates: `{feedback.get('route_prior_update_count', 0)}`",
                f"- Decision-policy suggestions: `{feedback.get('decision_policy_suggestion_count', 0)}`",
                f"- Outcome contradictions: `{feedback.get('outcome_contradiction_count', 0)}`",
            ]
        )
        if feedback.get("primary_recommended_action"):
            lines.append(f"- Primary feedback action: `{feedback.get('primary_recommended_action')}`")
    if contracts and any(value not in (None, 0, False, "", []) for value in contracts.values()):
        criteria = dict(contracts.get("acceptance_criteria", {}))
        criteria_text = ", ".join(f"{key}>={float(value):.2f}" for key, value in criteria.items()) if criteria else "none"
        lines.extend(
            [
                "",
                "## Contracts",
                f"- Quality gate: `{contracts.get('quality_gate_status') or 'unknown'}`",
                f"- Quality action: `{contracts.get('quality_recommended_action') or 'none'}`",
                f"- Quality state: `{contracts.get('quality_state') or 'unknown'}`",
                f"- Acceptance criteria: `{criteria_text}`",
                f"- Benchmark required: `{contracts.get('benchmark_required')}`",
                f"- Readiness floor: `{contracts.get('minimum_readiness_level') or 'unknown'}`",
                f"- Budget health: `{contracts.get('budget_health') or 'unknown'}`",
                f"- Elapsed minutes: `{contracts.get('observed_elapsed_minutes')}` / `{contracts.get('max_wall_clock_minutes')}`",
                f"- Estimated trials: `{contracts.get('estimated_trials_consumed')}` / `{contracts.get('max_trials')}`",
                f"- Branches: `{contracts.get('used_branches')}` / `{contracts.get('max_branches_per_round')}`",
            ]
        )
    if profiles and any(value not in (None, 0, False, "", []) for value in profiles.values()):
        lines.extend(
            [
                "",
                "## Profiles",
                f"- Operator profile: `{profiles.get('operator_profile_name') or 'unknown'}`",
                f"- Operator strictness: `{profiles.get('operator_review_strictness') or 'unknown'}`",
                f"- Operator benchmark appetite: `{profiles.get('operator_benchmark_appetite') or 'unknown'}`",
                f"- Operator explanation style: `{profiles.get('operator_explanation_style') or 'unknown'}`",
                f"- Lab profile: `{profiles.get('lab_profile_name') or 'unknown'}`",
                f"- Lab risk posture: `{profiles.get('lab_risk_posture') or 'unknown'}`",
                f"- Local truth required: `{profiles.get('local_truth_required')}`",
                f"- Remote intelligence allowed: `{profiles.get('remote_intelligence_allowed')}`",
            ]
        )
    if control and any(value not in (None, 0, False, "", []) for value in control.values()):
        lines.extend(
            [
                "",
                "## Control",
                "",
                f"- Request classification: `{control.get('request_classification') or 'unknown'}`",
                f"- Requested action: `{control.get('requested_action_kind') or 'none'}`",
                f"- Decision: `{control.get('decision') or 'unknown'}`",
                f"- Approved action: `{control.get('approved_action_kind') or 'none'}`",
                f"- Approved stage: `{control.get('approved_stage') or 'none'}`",
                f"- Challenge level: `{control.get('challenge_level') or 'unknown'}`",
                f"- Skepticism level: `{control.get('skepticism_level') or 'unknown'}`",
                f"- Similar harmful overrides: `{control.get('similar_harmful_override_count', 0)}`",
                f"- Suspicious requests: `{control.get('suspicious_count', 0)}`",
            ]
        )
        if control.get("checkpoint_id"):
            lines.append(f"- Recovery checkpoint: `{control.get('checkpoint_id')}`")
    if lifecycle and any(value is not None for value in lifecycle.values()):
        lines.extend(
            [
                "",
                "## Lifecycle",
                f"- Promotion: `{lifecycle.get('promotion_action') or 'unknown'}`",
                f"- Recalibration: `{lifecycle.get('recalibration_action') or 'unknown'}`",
                f"- Retrain: `{lifecycle.get('retrain_action') or 'unknown'}`",
                f"- Rollback: `{lifecycle.get('rollback_action') or 'unknown'}`",
            ]
        )
        if lifecycle.get("promotion_target"):
            lines.append(f"- Promotion target: `{lifecycle.get('promotion_target')}`")
        if lifecycle.get("drift_score") is not None:
            lines.append(f"- Drift score: `{float(lifecycle.get('drift_score', 0.0)):.4f}`")
        if lifecycle.get("ood_fraction") is not None:
            lines.append(f"- OOD fraction: `{float(lifecycle.get('ood_fraction', 0.0)):.4f}`")
    if autonomy and any(value is not None for value in autonomy.values()):
        lines.extend(
            [
                "",
                "## Autonomy",
                f"- Status: `{autonomy.get('status') or 'unknown'}`",
                f"- Selected action: `{autonomy.get('selected_action') or 'none'}`",
                f"- Promotion applied: `{autonomy.get('promotion_applied')}`",
                f"- Executed branches: `{autonomy.get('executed_branch_count', 0)}`",
                f"- Winning branch: `{autonomy.get('winning_branch_id') or 'none'}`",
            ]
        )
        if autonomy.get("current_champion"):
            lines.append(f"- Current champion: `{autonomy.get('current_champion')}`")
        if autonomy.get("budget_remaining") is not None:
            lines.append(f"- Branch budget remaining: `{autonomy.get('budget_remaining')}`")
    if runtime and (runtime.get("event_count", 0) or runtime.get("checkpoint_count", 0)):
        lines.extend(
            [
                "",
                "## Runtime",
                f"- Current runtime stage: `{runtime.get('current_stage') or 'unknown'}`",
                f"- Event count: `{runtime.get('event_count', 0)}`",
                f"- Checkpoints: `{runtime.get('checkpoint_count', 0)}`",
                f"- Denied accesses: `{runtime.get('denied_access_count', 0)}`",
                f"- Specialists tracked: `{runtime.get('active_specialist_count', 0)}`",
                f"- Write hooks: `{runtime.get('write_hook_executed_count', 0)}` executed, `{runtime.get('write_hook_blocked_count', 0)}` blocked",
            ]
        )
        if runtime.get("last_event_type"):
            lines.append(f"- Last event: `{runtime.get('last_event_type')}` via `{runtime.get('last_surface') or 'unknown'}`")
        if runtime.get("semantic_rowless_default") is not None:
            lines.append(f"- Rowless semantic default: `{runtime.get('semantic_rowless_default')}`")
    lines.extend(
        [
            "",
            "## Assumptions",
            f"- Logged assumptions: `{assumptions.get('count', 0)}`",
        ]
    )
    if assumptions.get("items"):
        lines.append(f"- First assumption: {assumptions['items'][0]}")
    lines.extend(
        [
            "",
            "## Next",
            f"- Recommended next experiment: `{next_step.get('recommended_experiment_id') or 'none'}`",
            f"- Recommended action: `{next_step.get('recommended_action') or 'unspecified'}`",
            f"- Why: {next_step.get('rationale') or 'No follow-up rationale recorded.'}",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def materialize_run_summary(
    *,
    run_dir: str | Path,
    data_path: str | Path | None = None,
    request_source: str | None = None,
    request_text: str | None = None,
) -> dict[str, Any]:
    """Build and write the machine and human summary artifacts for a run."""
    root = Path(run_dir)
    from relaytic.handoff import (
        AGENT_RESULT_REPORT_RELATIVE_PATH,
        USER_RESULT_REPORT_RELATIVE_PATH,
        run_handoff_review,
    )
    from relaytic.iteration import sync_iteration_from_run
    from relaytic.learnings import (
        default_learnings_state_dir,
        read_learnings_snapshot,
        read_learnings_state,
        reset_learnings,
        sync_learnings_from_run,
    )
    from relaytic.policies import load_policy
    from relaytic.search import read_search_bundle
    from relaytic.workspace import (
        render_agent_result_report_from_contract,
        render_user_result_report_from_contract,
        sync_workspace_from_run,
    )

    base_summary = build_run_summary(
        run_dir=root,
        data_path=data_path,
        request_source=request_source,
        request_text=request_text,
    )
    try:
        policy_path = root / "policy_resolved.yaml"
        policy = load_policy(policy_path if policy_path.exists() else None).policy
    except Exception:
        policy = {}
    handoff_result = run_handoff_review(
        run_dir=root,
        summary_payload=base_summary,
        policy=policy,
    )
    handoff_bundle = handoff_result.bundle.to_dict()
    next_focus = dict(handoff_bundle.get("next_run_focus", {})) if isinstance(handoff_bundle.get("next_run_focus"), dict) else {}
    if bool(next_focus.get("reset_learnings_requested")):
        reset_learnings(run_dir=root, policy=policy)
    else:
        state_dir = default_learnings_state_dir(run_dir=root)
        existing_state = read_learnings_state(state_dir)
        existing_snapshot = read_learnings_snapshot(root)
        reset_active_for_current_run = (
            str(existing_state.get("status", "")).strip() == "reset"
            and str(existing_snapshot.get("status", "")).strip() == "reset"
            and str(existing_snapshot.get("run_id", "")).strip() == str(base_summary.get("run_id", "")).strip()
        )
        if not reset_active_for_current_run:
            sync_learnings_from_run(
                run_dir=root,
                summary_payload=base_summary,
                handoff_bundle=handoff_bundle,
                policy=policy,
            )
    intermediate_summary = build_run_summary(
        run_dir=root,
        data_path=data_path,
        request_source=request_source,
        request_text=request_text,
    )
    state_dir = default_learnings_state_dir(run_dir=root)
    workspace_sync = sync_workspace_from_run(
        run_dir=root,
        summary_payload=intermediate_summary,
        handoff_bundle=handoff_bundle,
        learnings_state=read_learnings_state(state_dir),
        learnings_snapshot=read_learnings_snapshot(root),
        policy=policy,
    )
    search_bundle = read_search_bundle(root)
    iteration_sync = sync_iteration_from_run(
        run_dir=root,
        workspace_dir=workspace_sync.workspace_dir,
        workspace_state=workspace_sync.workspace_state.to_dict(),
        result_contract=workspace_sync.result_contract.to_dict(),
        belief_revision_triggers=workspace_sync.belief_revision_triggers.to_dict(),
        summary_payload=intermediate_summary,
        handoff_bundle=handoff_bundle,
        search_bundle=search_bundle,
        policy=policy,
    )
    user_report_path = root / USER_RESULT_REPORT_RELATIVE_PATH
    agent_report_path = root / AGENT_RESULT_REPORT_RELATIVE_PATH
    user_report_path.parent.mkdir(parents=True, exist_ok=True)
    agent_report_path.parent.mkdir(parents=True, exist_ok=True)
    user_report_path.write_text(
        render_user_result_report_from_contract(
            result_contract=workspace_sync.result_contract.to_dict(),
            confidence_posture=workspace_sync.confidence_posture.to_dict(),
            belief_revision_triggers=workspace_sync.belief_revision_triggers.to_dict(),
            next_run_plan=iteration_sync.next_run_plan.to_dict(),
            workspace_state=workspace_sync.workspace_state.to_dict(),
        ),
        encoding="utf-8",
    )
    agent_report_path.write_text(
        render_agent_result_report_from_contract(
            result_contract=workspace_sync.result_contract.to_dict(),
            confidence_posture=workspace_sync.confidence_posture.to_dict(),
            belief_revision_triggers=workspace_sync.belief_revision_triggers.to_dict(),
            next_run_plan=iteration_sync.next_run_plan.to_dict(),
            workspace_state=workspace_sync.workspace_state.to_dict(),
        ),
        encoding="utf-8",
    )
    summary = build_run_summary(
        run_dir=root,
        data_path=data_path,
        request_source=request_source,
        request_text=request_text,
    )
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
        "report_markdown": report_path.read_text(encoding="utf-8"),
    }


def _read_bundle(root: Path, mapping: dict[str, str]) -> dict[str, Any]:
    return {
        key: payload
        for key, filename in mapping.items()
        if isinstance((payload := _read_json(root / filename)), dict) and payload
    }


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return payload if isinstance(payload, dict) else {}


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    records: list[dict[str, Any]] = []
    try:
        with path.open("r", encoding="utf-8") as handle:
            for line in handle:
                text = line.strip()
                if not text:
                    continue
                try:
                    payload = json.loads(text)
                except json.JSONDecodeError:
                    continue
                if isinstance(payload, dict):
                    records.append(payload)
    except OSError:
        return []
    return records


def _clean_text(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    if text.lower() in {"none", "null"}:
        return None
    return text


def _first_learning_lesson(*, learnings_snapshot: dict[str, Any], learnings_state: dict[str, Any]) -> str | None:
    for key, source in (
        ("active_learnings", learnings_snapshot),
        ("harvested_learnings", learnings_snapshot),
        ("entries", learnings_state),
    ):
        items = source.get(key)
        if not isinstance(items, list):
            continue
        for item in items:
            if not isinstance(item, dict):
                continue
            lesson = _clean_text(item.get("lesson"))
            if lesson:
                return lesson
    return None


def _clean_literal_text(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _bundle_item(bundle: dict[str, Any], key: str) -> dict[str, Any]:
    payload = bundle.get(key)
    return dict(payload) if isinstance(payload, dict) else {}


def _first_data_reference(builder_handoff: dict[str, Any]) -> str:
    for value in builder_handoff.get("data_references", []):
        text = str(value).strip()
        if text:
            return text
    return ""


def _resolve_stage(
    *,
    plan: dict[str, Any],
    execution_summary: dict[str, Any],
    investigation_bundle: dict[str, Any],
    intake_bundle: dict[str, Any],
    evidence_bundle: dict[str, Any],
    intelligence_bundle: dict[str, Any],
    research_bundle: dict[str, Any],
    benchmark_bundle: dict[str, Any],
    decision_bundle: dict[str, Any],
    dojo_bundle: dict[str, Any],
    pulse_bundle: dict[str, Any],
    search_bundle: dict[str, Any],
    handoff_bundle: dict[str, Any],
    learnings_state: dict[str, Any],
    learnings_snapshot: dict[str, Any],
    profiles_bundle: dict[str, Any],
    feedback_bundle: dict[str, Any],
    control_bundle: dict[str, Any],
    completion_bundle: dict[str, Any],
    lifecycle_bundle: dict[str, Any],
    autonomy_bundle: dict[str, Any],
) -> str:
    if search_bundle:
        return "search_reviewed"
    if pulse_bundle:
        return "pulse_reviewed"
    if dojo_bundle:
        return "dojo_reviewed"
    if any(isinstance(value, dict) and value for value in feedback_bundle.values()):
        return "feedback_reviewed"
    if any(isinstance(value, dict) and value for value in control_bundle.values()):
        return "control_reviewed"
    if autonomy_bundle:
        return "autonomy_reviewed"
    if lifecycle_bundle:
        return "lifecycle_reviewed"
    if completion_bundle:
        run_state = _bundle_item(completion_bundle, "run_state")
        return str(run_state.get("current_stage", "")).strip() or "completion_reviewed"
    if decision_bundle:
        return "decision_reviewed"
    if profiles_bundle:
        return "profiles_reviewed"
    if benchmark_bundle:
        return "benchmark_reviewed"
    if research_bundle:
        return "research_reviewed"
    if intelligence_bundle:
        return "intelligence_reviewed"
    if evidence_bundle:
        return "evidence_reviewed"
    if execution_summary:
        return "planned_and_executed"
    if plan:
        return "planned"
    if investigation_bundle:
        return "investigated"
    if intake_bundle:
        return "interpreted"
    return "foundation_only"


def _resolve_runtime_stage(root: Path, *, latest_stage: str, last_event_stage: str) -> str | None:
    if any(
        (root / filename).exists()
        for filename in (
            "search_controller_plan.json",
            "search_value_report.json",
            "search_controller_eval_report.json",
        )
    ):
        return "search"
    if any(
        (root / filename).exists()
        for filename in (
            "pulse_run_report.json",
            "pulse_schedule.json",
            "challenge_watchlist.json",
        )
    ):
        return "pulse"
    if any(
        (root / filename).exists()
        for filename in (
            "dojo_session.json",
            "dojo_results.json",
            "dojo_promotions.json",
        )
    ):
        return "dojo"
    if (root / "feedback_effect_report.json").exists():
        return "feedback"
    if latest_stage == "control" or last_event_stage == "control":
        return "control"
    if any(
        (root / filename).exists()
        for filename in (
            "autonomy_loop_state.json",
            "autonomy_round_report.json",
            "branch_outcome_matrix.json",
            "champion_lineage.json",
            "loop_budget_report.json",
        )
    ):
        return "autonomy"
    if (root / "promotion_decision.json").exists():
        return "lifecycle"
    if (root / "completion_decision.json").exists():
        return "completion"
    if (root / "override_decision.json").exists():
        return "control"
    if (root / "quality_gate_report.json").exists():
        return "profiles"
    if (root / "benchmark_parity_report.json").exists():
        return "benchmark"
    if (root / "decision_world_model.json").exists():
        return "decision"
    if (root / "research_brief.json").exists():
        return "research"
    if (root / "semantic_debate_report.json").exists():
        return "intelligence"
    if (root / "audit_report.json").exists():
        return "evidence"
    if (root / "plan.json").exists():
        return "planning"
    if (root / "dataset_profile.json").exists():
        return "investigation"
    if (root / "intake_record.json").exists():
        return "intake"
    if latest_stage and latest_stage != "memory":
        return latest_stage
    if latest_stage:
        return latest_stage
    if last_event_stage:
        return last_event_stage
    return None


def _resolve_run_status(
    *,
    plan: dict[str, Any],
    execution_summary: dict[str, Any],
    audit_report: dict[str, Any],
    completion_decision: dict[str, Any],
    lifecycle_bundle: dict[str, Any],
) -> str:
    if lifecycle_bundle:
        rollback = _bundle_item(lifecycle_bundle, "rollback_decision")
        if str(rollback.get("action", "")).strip() == "rollback_required":
            return "rollback_required"
        retrain = _bundle_item(lifecycle_bundle, "retrain_decision")
        if str(retrain.get("action", "")).strip() == "retrain":
            return "retrain"
        recalibration = _bundle_item(lifecycle_bundle, "recalibration_decision")
        if str(recalibration.get("action", "")).strip() == "recalibrate":
            return "recalibrate"
        promotion = _bundle_item(lifecycle_bundle, "promotion_decision")
        action = str(promotion.get("action", "")).strip()
        if action:
            return action
    if completion_decision:
        action = str(completion_decision.get("action", "")).strip()
        if action:
            return action
    if audit_report:
        recommendation = str(audit_report.get("provisional_recommendation", "")).strip()
        if recommendation:
            return recommendation
    if execution_summary:
        status = str(execution_summary.get("status", "")).strip()
        return status or "executed"
    if plan:
        return "planned"
    return "initialized"


def _path_if_exists(path: Path) -> str | None:
    return str(path) if path.exists() else None


def _lifecycle_primary_action(lifecycle_bundle: dict[str, Any]) -> str | None:
    if not lifecycle_bundle:
        return None
    for key in (
        "rollback_decision",
        "retrain_decision",
        "recalibration_decision",
        "promotion_decision",
    ):
        action = str(_bundle_item(lifecycle_bundle, key).get("action", "")).strip()
        if action and action not in {"no_rollback", "no_retrain", "no_recalibration"}:
            return action
    return None


def _resolve_model_state_path(root: Path, *, execution_summary: dict[str, Any]) -> str | None:
    text = str(execution_summary.get("model_state_path", "")).strip()
    if text:
        return text
    direct = root / "model_state.json"
    if direct.exists():
        return str(direct)
    for candidate in sorted(root.glob("*_state.json")):
        if candidate.name != "normalization_state.json":
            return str(candidate)
    return None


def _preview_text(value: Any, *, limit: int = 160) -> str | None:
    text = str(value or "").strip()
    if not text:
        return None
    if len(text) <= limit:
        return text
    return text[: limit - 3].rstrip() + "..."


def _build_headline(summary: dict[str, Any]) -> str:
    decision = dict(summary.get("decision", {}))
    evidence = dict(summary.get("evidence", {}))
    completion = dict(summary.get("completion", {}))
    lifecycle = dict(summary.get("lifecycle", {}))
    target = decision.get("target_column") or "unknown target"
    route = decision.get("selected_route_title") or decision.get("selected_route_id") or "no selected route"
    model = decision.get("selected_model_family")
    if model:
        promotion_action = lifecycle.get("promotion_action")
        retrain_action = lifecycle.get("retrain_action")
        recalibration_action = lifecycle.get("recalibration_action")
        rollback_action = lifecycle.get("rollback_action")
        if rollback_action == "rollback_required":
            return (
                f"Relaytic built `{model}` for `{target}` using the `{route}` route and "
                "now recommends rollback because the current route is no longer trustworthy."
            )
        if retrain_action == "retrain":
            return (
                f"Relaytic built `{model}` for `{target}` using the `{route}` route and "
                "now recommends retraining under lifecycle review."
            )
        if recalibration_action == "recalibrate":
            return (
                f"Relaytic built `{model}` for `{target}` using the `{route}` route and "
                "now recommends recalibration rather than a full route reset."
            )
        if promotion_action:
            return (
                f"Relaytic built `{model}` for `{target}` using the `{route}` route and "
                f"currently applies the lifecycle decision `{promotion_action}`."
            )
        completion_action = completion.get("action")
        if completion_action:
            return (
                f"Relaytic built `{model}` for `{target}` using the `{route}` route and "
                f"currently judges the run as `{completion_action}`."
            )
        recommendation = evidence.get("provisional_recommendation")
        if recommendation:
            return (
                f"Relaytic built `{model}` for `{target}` using the `{route}` route and "
                f"currently recommends `{recommendation}` after challenger and audit review."
            )
        return f"Relaytic built `{model}` for `{target}` using the `{route}` route."
    return f"Relaytic prepared `{route}` for `{target}` but has not executed a model build yet."


def _infer_data_format(path_text: str | None) -> str | None:
    text = str(path_text or "").strip()
    if not text:
        return None
    suffix = Path(text).suffix.lower().strip()
    if not suffix:
        return None
    return suffix.lstrip(".")


def _find_copy_record(
    manifest: dict[str, Any],
    *,
    staged_path: str | None,
    purpose: str,
) -> dict[str, Any]:
    copies = manifest.get("copies", [])
    if not isinstance(copies, list):
        return {}
    normalized_path = str(staged_path or "").strip().replace("\\", "/")
    for item in copies:
        if not isinstance(item, dict):
            continue
        if normalized_path and str(item.get("staged_path", "")).strip().replace("\\", "/") == normalized_path:
            return item
    for item in reversed(copies):
        if isinstance(item, dict) and str(item.get("purpose", "")).strip() == str(purpose).strip():
            return item
    return {}


def _format_metric_block(metrics: dict[str, Any]) -> str:
    if not metrics:
        return "not available"
    preferred_order = ["log_loss", "mae", "rmse", "accuracy", "precision", "recall", "f1", "pr_auc", "roc_auc"]
    parts: list[str] = []
    for key in preferred_order:
        if key in metrics:
            value = metrics[key]
            if isinstance(value, (int, float)):
                parts.append(f"{key}={value:.4f}")
    if not parts:
        for key, value in metrics.items():
            if isinstance(value, (int, float)):
                parts.append(f"{key}={value:.4f}")
    return ", ".join(parts) if parts else "not available"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()
