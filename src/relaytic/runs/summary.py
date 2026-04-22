"""MVP run-summary and report helpers for human and agent access surfaces."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from relaytic.core.benchmark_statuses import benchmark_is_reference_competitive, normalize_benchmark_parity_status
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
    from relaytic.analytics import (
        read_architecture_routing_artifacts,
        read_task_contract_artifacts,
        read_temporal_engine_artifacts,
    )
    from relaytic.aml import read_aml_graph_artifacts
    from relaytic.iteration import read_iteration_bundle
    from relaytic.casework import read_casework_artifacts
    from relaytic.stream_risk import read_stream_risk_artifacts
    from relaytic.events import read_event_bus_bundle
    from relaytic.permissions import read_permission_bundle
    from relaytic.search import read_search_bundle
    from relaytic.daemon import read_daemon_bundle
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
    from relaytic.remote_control import read_remote_control_bundle
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
            "paper_benchmark_manifest": "paper_benchmark_manifest.json",
            "paper_benchmark_table": "paper_benchmark_table.json",
            "benchmark_ablation_matrix": "benchmark_ablation_matrix.json",
            "rerun_variance_report": "rerun_variance_report.json",
            "benchmark_claims_report": "benchmark_claims_report.json",
            "benchmark_truth_audit": "benchmark_truth_audit.json",
            "paper_claim_guard_report": "paper_claim_guard_report.json",
            "benchmark_release_gate": "benchmark_release_gate.json",
            "dataset_leakage_audit": "dataset_leakage_audit.json",
            "temporal_benchmark_recovery_report": "temporal_benchmark_recovery_report.json",
            "benchmark_pack_partition": "benchmark_pack_partition.json",
            "holdout_claim_policy": "holdout_claim_policy.json",
            "benchmark_generalization_audit": "benchmark_generalization_audit.json",
            "aml_benchmark_manifest": "aml_benchmark_manifest.json",
            "aml_holdout_claim_report": "aml_holdout_claim_report.json",
            "aml_demo_scorecard": "aml_demo_scorecard.json",
            "aml_public_claim_guard": "aml_public_claim_guard.json",
            "aml_failure_report": "aml_failure_report.json",
            "shadow_trial_manifest": "shadow_trial_manifest.json",
            "shadow_trial_scorecard": "shadow_trial_scorecard.json",
            "candidate_quarantine": "candidate_quarantine.json",
            "promotion_readiness_report": "promotion_readiness_report.json",
        },
    )
    task_contract_bundle = read_task_contract_artifacts(root)
    aml_graph_bundle = read_aml_graph_artifacts(root)
    casework_bundle = read_casework_artifacts(root)
    stream_risk_bundle = read_stream_risk_artifacts(root)
    decision_bundle = _read_bundle(
        root,
        {
            "decision_world_model": "decision_world_model.json",
            "controller_policy": "controller_policy.json",
            "handoff_controller_report": "handoff_controller_report.json",
            "intervention_policy_report": "intervention_policy_report.json",
            "decision_usefulness_report": "decision_usefulness_report.json",
            "trajectory_constraint_report": "trajectory_constraint_report.json",
            "feasible_region_map": "feasible_region_map.json",
            "extrapolation_risk_report": "extrapolation_risk_report.json",
            "decision_constraint_report": "decision_constraint_report.json",
            "action_boundary_report": "action_boundary_report.json",
            "deployability_assessment": "deployability_assessment.json",
            "review_gate_state": "review_gate_state.json",
            "constraint_override_request": "constraint_override_request.json",
            "counterfactual_region_report": "counterfactual_region_report.json",
            "value_of_more_data_report": "value_of_more_data_report.json",
            "data_acquisition_plan": "data_acquisition_plan.json",
            "source_graph": "source_graph.json",
            "join_candidate_report": "join_candidate_report.json",
            "method_compiler_report": "method_compiler_report.json",
            "compiled_challenger_templates": "compiled_challenger_templates.json",
            "compiled_feature_hypotheses": "compiled_feature_hypotheses.json",
            "compiled_benchmark_protocol": "compiled_benchmark_protocol.json",
            "method_import_report": "method_import_report.json",
            "architecture_candidate_registry": "architecture_candidate_registry.json",
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
            "trace_identity_conformance": "trace_identity_conformance.json",
            "eval_surface_parity_report": "eval_surface_parity_report.json",
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
            "artifact_dependency_graph": "artifact_dependency_graph.json",
            "freshness_contract": "freshness_contract.json",
            "recompute_plan": "recompute_plan.json",
            "materialization_cache_index": "materialization_cache_index.json",
            "invalidation_report": "invalidation_report.json",
        },
    )
    event_bus_bundle = read_event_bus_bundle(root)
    permission_bundle = read_permission_bundle(root)
    daemon_bundle = read_daemon_bundle(root)
    remote_control_bundle = read_remote_control_bundle(root)
    architecture_bundle = read_architecture_routing_artifacts(root)
    temporal_bundle = read_temporal_engine_artifacts(root)
    hpo_bundle = _read_bundle(
        root,
        {
            "hpo_budget_contract": "hpo_budget_contract.json",
            "architecture_search_space": "architecture_search_space.json",
            "early_stopping_report": "early_stopping_report.json",
            "search_loop_scorecard": "search_loop_scorecard.json",
            "warm_start_transfer_report": "warm_start_transfer_report.json",
            "threshold_tuning_report": "threshold_tuning_report.json",
        },
    )
    operating_point_bundle = _read_bundle(
        root,
        {
            "calibration_strategy_report": "calibration_strategy_report.json",
            "operating_point_contract": "operating_point_contract.json",
            "threshold_search_report": "threshold_search_report.json",
            "decision_cost_profile": "decision_cost_profile.json",
            "review_budget_optimization_report": "review_budget_optimization_report.json",
            "abstention_policy_report": "abstention_policy_report.json",
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
    task_profile_contract = dict(task_contract_bundle.get("task_profile_contract", {})) if isinstance(task_contract_bundle.get("task_profile_contract"), dict) else {}
    target_semantics_report = dict(task_contract_bundle.get("target_semantics_report", {})) if isinstance(task_contract_bundle.get("target_semantics_report"), dict) else {}
    metric_contract = dict(task_contract_bundle.get("metric_contract", {})) if isinstance(task_contract_bundle.get("metric_contract"), dict) else {}
    benchmark_mode_report = dict(task_contract_bundle.get("benchmark_mode_report", {})) if isinstance(task_contract_bundle.get("benchmark_mode_report"), dict) else {}
    deployment_readiness_report = dict(task_contract_bundle.get("deployment_readiness_report", {})) if isinstance(task_contract_bundle.get("deployment_readiness_report"), dict) else {}
    benchmark_vs_deploy_report = dict(task_contract_bundle.get("benchmark_vs_deploy_report", {})) if isinstance(task_contract_bundle.get("benchmark_vs_deploy_report"), dict) else {}
    dataset_semantics_audit = dict(task_contract_bundle.get("dataset_semantics_audit", {})) if isinstance(task_contract_bundle.get("dataset_semantics_audit"), dict) else {}
    optimization_objective_contract = dict(task_contract_bundle.get("optimization_objective_contract", {})) if isinstance(task_contract_bundle.get("optimization_objective_contract"), dict) else {}
    objective_alignment_report = dict(task_contract_bundle.get("objective_alignment_report", {})) if isinstance(task_contract_bundle.get("objective_alignment_report"), dict) else {}
    split_diagnostics_report = dict(task_contract_bundle.get("split_diagnostics_report", {})) if isinstance(task_contract_bundle.get("split_diagnostics_report"), dict) else {}
    temporal_fold_health = dict(task_contract_bundle.get("temporal_fold_health", {})) if isinstance(task_contract_bundle.get("temporal_fold_health"), dict) else {}
    metric_materialization_audit = dict(task_contract_bundle.get("metric_materialization_audit", {})) if isinstance(task_contract_bundle.get("metric_materialization_audit"), dict) else {}
    benchmark_truth_precheck = dict(task_contract_bundle.get("benchmark_truth_precheck", {})) if isinstance(task_contract_bundle.get("benchmark_truth_precheck"), dict) else {}
    aml_domain_contract = dict(task_contract_bundle.get("aml_domain_contract", {})) if isinstance(task_contract_bundle.get("aml_domain_contract"), dict) else {}
    aml_case_ontology = dict(task_contract_bundle.get("aml_case_ontology", {})) if isinstance(task_contract_bundle.get("aml_case_ontology"), dict) else {}
    aml_review_budget_contract = dict(task_contract_bundle.get("aml_review_budget_contract", {})) if isinstance(task_contract_bundle.get("aml_review_budget_contract"), dict) else {}
    aml_claim_scope = dict(task_contract_bundle.get("aml_claim_scope", {})) if isinstance(task_contract_bundle.get("aml_claim_scope"), dict) else {}
    entity_graph_profile = dict(aml_graph_bundle.get("entity_graph_profile", {})) if isinstance(aml_graph_bundle.get("entity_graph_profile"), dict) else {}
    counterparty_network_report = dict(aml_graph_bundle.get("counterparty_network_report", {})) if isinstance(aml_graph_bundle.get("counterparty_network_report"), dict) else {}
    typology_detection_report = dict(aml_graph_bundle.get("typology_detection_report", {})) if isinstance(aml_graph_bundle.get("typology_detection_report"), dict) else {}
    subgraph_risk_report = dict(aml_graph_bundle.get("subgraph_risk_report", {})) if isinstance(aml_graph_bundle.get("subgraph_risk_report"), dict) else {}
    entity_case_expansion = dict(aml_graph_bundle.get("entity_case_expansion", {})) if isinstance(aml_graph_bundle.get("entity_case_expansion"), dict) else {}
    alert_queue_policy = dict(casework_bundle.get("alert_queue_policy", {})) if isinstance(casework_bundle.get("alert_queue_policy"), dict) else {}
    alert_queue_rankings = dict(casework_bundle.get("alert_queue_rankings", {})) if isinstance(casework_bundle.get("alert_queue_rankings"), dict) else {}
    analyst_review_scorecard = dict(casework_bundle.get("analyst_review_scorecard", {})) if isinstance(casework_bundle.get("analyst_review_scorecard"), dict) else {}
    case_packet = dict(casework_bundle.get("case_packet", {})) if isinstance(casework_bundle.get("case_packet"), dict) else {}
    review_capacity_sensitivity = dict(casework_bundle.get("review_capacity_sensitivity", {})) if isinstance(casework_bundle.get("review_capacity_sensitivity"), dict) else {}
    stream_risk_posture = dict(stream_risk_bundle.get("stream_risk_posture", {})) if isinstance(stream_risk_bundle.get("stream_risk_posture"), dict) else {}
    weak_label_posture = dict(stream_risk_bundle.get("weak_label_posture", {})) if isinstance(stream_risk_bundle.get("weak_label_posture"), dict) else {}
    delayed_outcome_alignment = dict(stream_risk_bundle.get("delayed_outcome_alignment", {})) if isinstance(stream_risk_bundle.get("delayed_outcome_alignment"), dict) else {}
    drift_recalibration_trigger = dict(stream_risk_bundle.get("drift_recalibration_trigger", {})) if isinstance(stream_risk_bundle.get("drift_recalibration_trigger"), dict) else {}
    rolling_alert_quality_report = dict(stream_risk_bundle.get("rolling_alert_quality_report", {})) if isinstance(stream_risk_bundle.get("rolling_alert_quality_report"), dict) else {}
    temporal_structure_report = dict(temporal_bundle.get("temporal_structure_report", {})) if isinstance(temporal_bundle.get("temporal_structure_report"), dict) else {}
    temporal_feature_ladder = dict(temporal_bundle.get("temporal_feature_ladder", {})) if isinstance(temporal_bundle.get("temporal_feature_ladder"), dict) else {}
    rolling_cv_plan = dict(temporal_bundle.get("rolling_cv_plan", {})) if isinstance(temporal_bundle.get("rolling_cv_plan"), dict) else {}
    temporal_split_guard_report = dict(temporal_bundle.get("temporal_split_guard_report", {})) if isinstance(temporal_bundle.get("temporal_split_guard_report"), dict) else {}
    sequence_shadow_scorecard = dict(temporal_bundle.get("sequence_shadow_scorecard", {})) if isinstance(temporal_bundle.get("sequence_shadow_scorecard"), dict) else {}
    temporal_baseline_ladder = dict(temporal_bundle.get("temporal_baseline_ladder", {})) if isinstance(temporal_bundle.get("temporal_baseline_ladder"), dict) else {}
    temporal_metric_contract = dict(temporal_bundle.get("temporal_metric_contract", {})) if isinstance(temporal_bundle.get("temporal_metric_contract"), dict) else {}
    architecture_registry = dict(architecture_bundle.get("architecture_registry", {})) if isinstance(architecture_bundle.get("architecture_registry"), dict) else {}
    architecture_router_report = dict(architecture_bundle.get("architecture_router_report", {})) if isinstance(architecture_bundle.get("architecture_router_report"), dict) else {}
    candidate_family_matrix = dict(architecture_bundle.get("candidate_family_matrix", {})) if isinstance(architecture_bundle.get("candidate_family_matrix"), dict) else {}
    architecture_fit_report = dict(architecture_bundle.get("architecture_fit_report", {})) if isinstance(architecture_bundle.get("architecture_fit_report"), dict) else {}
    family_capability_matrix = dict(architecture_bundle.get("family_capability_matrix", {})) if isinstance(architecture_bundle.get("family_capability_matrix"), dict) else {}
    architecture_ablation_report = dict(architecture_bundle.get("architecture_ablation_report", {})) if isinstance(architecture_bundle.get("architecture_ablation_report"), dict) else {}
    family_registry_extension = dict(architecture_bundle.get("family_registry_extension", {})) if isinstance(architecture_bundle.get("family_registry_extension"), dict) else {}
    family_readiness_report = dict(architecture_bundle.get("family_readiness_report", {})) if isinstance(architecture_bundle.get("family_readiness_report"), dict) else {}
    family_eligibility_matrix = dict(architecture_bundle.get("family_eligibility_matrix", {})) if isinstance(architecture_bundle.get("family_eligibility_matrix"), dict) else {}
    family_probe_policy = dict(architecture_bundle.get("family_probe_policy", {})) if isinstance(architecture_bundle.get("family_probe_policy"), dict) else {}
    categorical_strategy_report = dict(architecture_bundle.get("categorical_strategy_report", {})) if isinstance(architecture_bundle.get("categorical_strategy_report"), dict) else {}
    family_specialization_report = dict(architecture_bundle.get("family_specialization_report", {})) if isinstance(architecture_bundle.get("family_specialization_report"), dict) else {}
    family_specialization_matrix = dict(architecture_bundle.get("family_specialization_matrix", {})) if isinstance(architecture_bundle.get("family_specialization_matrix"), dict) else {}
    multiclass_search_profile = dict(architecture_bundle.get("multiclass_search_profile", {})) if isinstance(architecture_bundle.get("multiclass_search_profile"), dict) else {}
    rare_event_search_profile = dict(architecture_bundle.get("rare_event_search_profile", {})) if isinstance(architecture_bundle.get("rare_event_search_profile"), dict) else {}
    adapter_activation_report = dict(architecture_bundle.get("adapter_activation_report", {})) if isinstance(architecture_bundle.get("adapter_activation_report"), dict) else {}
    hpo_budget_contract = dict(hpo_bundle.get("hpo_budget_contract", {})) if isinstance(hpo_bundle.get("hpo_budget_contract"), dict) else {}
    architecture_search_space = dict(hpo_bundle.get("architecture_search_space", {})) if isinstance(hpo_bundle.get("architecture_search_space"), dict) else {}
    early_stopping_report = dict(hpo_bundle.get("early_stopping_report", {})) if isinstance(hpo_bundle.get("early_stopping_report"), dict) else {}
    search_loop_scorecard = dict(hpo_bundle.get("search_loop_scorecard", {})) if isinstance(hpo_bundle.get("search_loop_scorecard"), dict) else {}
    warm_start_transfer_report = dict(hpo_bundle.get("warm_start_transfer_report", {})) if isinstance(hpo_bundle.get("warm_start_transfer_report"), dict) else {}
    threshold_tuning_report = dict(hpo_bundle.get("threshold_tuning_report", {})) if isinstance(hpo_bundle.get("threshold_tuning_report"), dict) else {}
    calibration_strategy_report = dict(operating_point_bundle.get("calibration_strategy_report", {})) if isinstance(operating_point_bundle.get("calibration_strategy_report"), dict) else {}
    operating_point_contract = dict(operating_point_bundle.get("operating_point_contract", {})) if isinstance(operating_point_bundle.get("operating_point_contract"), dict) else {}
    threshold_search_report = dict(operating_point_bundle.get("threshold_search_report", {})) if isinstance(operating_point_bundle.get("threshold_search_report"), dict) else {}
    decision_cost_profile = dict(operating_point_bundle.get("decision_cost_profile", {})) if isinstance(operating_point_bundle.get("decision_cost_profile"), dict) else {}
    review_budget_optimization_report = dict(operating_point_bundle.get("review_budget_optimization_report", {})) if isinstance(operating_point_bundle.get("review_budget_optimization_report"), dict) else {}
    abstention_policy_report = dict(operating_point_bundle.get("abstention_policy_report", {})) if isinstance(operating_point_bundle.get("abstention_policy_report"), dict) else {}
    trial_ledger = _read_jsonl(root / "trial_ledger.jsonl")
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
    paper_benchmark_manifest = _bundle_item(benchmark_bundle, "paper_benchmark_manifest")
    paper_benchmark_table = _bundle_item(benchmark_bundle, "paper_benchmark_table")
    benchmark_ablation_matrix = _bundle_item(benchmark_bundle, "benchmark_ablation_matrix")
    rerun_variance_report = _bundle_item(benchmark_bundle, "rerun_variance_report")
    benchmark_claims_report = _bundle_item(benchmark_bundle, "benchmark_claims_report")
    benchmark_truth_audit = _bundle_item(benchmark_bundle, "benchmark_truth_audit")
    paper_claim_guard_report = _bundle_item(benchmark_bundle, "paper_claim_guard_report")
    benchmark_release_gate = _bundle_item(benchmark_bundle, "benchmark_release_gate")
    dataset_leakage_audit = _bundle_item(benchmark_bundle, "dataset_leakage_audit")
    temporal_benchmark_recovery_report = _bundle_item(benchmark_bundle, "temporal_benchmark_recovery_report")
    benchmark_pack_partition = _bundle_item(benchmark_bundle, "benchmark_pack_partition")
    holdout_claim_policy = _bundle_item(benchmark_bundle, "holdout_claim_policy")
    benchmark_generalization_audit = _bundle_item(benchmark_bundle, "benchmark_generalization_audit")
    aml_benchmark_manifest = _bundle_item(benchmark_bundle, "aml_benchmark_manifest")
    aml_holdout_claim_report = _bundle_item(benchmark_bundle, "aml_holdout_claim_report")
    aml_demo_scorecard = _bundle_item(benchmark_bundle, "aml_demo_scorecard")
    aml_public_claim_guard = _bundle_item(benchmark_bundle, "aml_public_claim_guard")
    aml_failure_report = _bundle_item(benchmark_bundle, "aml_failure_report")
    shadow_trial_manifest = _bundle_item(benchmark_bundle, "shadow_trial_manifest")
    shadow_trial_scorecard = _bundle_item(benchmark_bundle, "shadow_trial_scorecard")
    candidate_quarantine = _bundle_item(benchmark_bundle, "candidate_quarantine")
    promotion_readiness_report = _bundle_item(benchmark_bundle, "promotion_readiness_report")
    decision_world_model = _bundle_item(decision_bundle, "decision_world_model")
    controller_policy = _bundle_item(decision_bundle, "controller_policy")
    handoff_controller_report = _bundle_item(decision_bundle, "handoff_controller_report")
    decision_usefulness_report = _bundle_item(decision_bundle, "decision_usefulness_report")
    trajectory_constraint_report = _bundle_item(decision_bundle, "trajectory_constraint_report")
    feasible_region_map = _bundle_item(decision_bundle, "feasible_region_map")
    extrapolation_risk_report = _bundle_item(decision_bundle, "extrapolation_risk_report")
    decision_constraint_report = _bundle_item(decision_bundle, "decision_constraint_report")
    action_boundary_report = _bundle_item(decision_bundle, "action_boundary_report")
    deployability_assessment = _bundle_item(decision_bundle, "deployability_assessment")
    review_gate_state = _bundle_item(decision_bundle, "review_gate_state")
    constraint_override_request = _bundle_item(decision_bundle, "constraint_override_request")
    counterfactual_region_report = _bundle_item(decision_bundle, "counterfactual_region_report")
    value_of_more_data_report = _bundle_item(decision_bundle, "value_of_more_data_report")
    data_acquisition_plan = _bundle_item(decision_bundle, "data_acquisition_plan")
    source_graph = _bundle_item(decision_bundle, "source_graph")
    join_candidate_report = _bundle_item(decision_bundle, "join_candidate_report")
    method_compiler_report = _bundle_item(decision_bundle, "method_compiler_report")
    compiled_challenger_templates = _bundle_item(decision_bundle, "compiled_challenger_templates")
    compiled_feature_hypotheses = _bundle_item(decision_bundle, "compiled_feature_hypotheses")
    compiled_benchmark_protocol = _bundle_item(decision_bundle, "compiled_benchmark_protocol")
    method_import_report = _bundle_item(decision_bundle, "method_import_report")
    architecture_candidate_registry = _bundle_item(decision_bundle, "architecture_candidate_registry")
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
    trace_identity_conformance = _bundle_item(evals_bundle, "trace_identity_conformance")
    eval_surface_parity_report = _bundle_item(evals_bundle, "eval_surface_parity_report")
    search_controller_plan = _bundle_item(search_bundle, "search_controller_plan")
    portfolio_search_trace = _bundle_item(search_bundle, "portfolio_search_trace")
    hpo_campaign_report = _bundle_item(search_bundle, "hpo_campaign_report")
    execution_backend_profile = _bundle_item(search_bundle, "execution_backend_profile")
    distributed_run_plan = _bundle_item(search_bundle, "distributed_run_plan")
    execution_strategy_report = _bundle_item(search_bundle, "execution_strategy_report")
    search_value_report = _bundle_item(search_bundle, "search_value_report")
    search_budget_envelope = _bundle_item(search_bundle, "search_budget_envelope")
    probe_stage_report = _bundle_item(search_bundle, "probe_stage_report")
    family_race_report = _bundle_item(search_bundle, "family_race_report")
    finalist_search_plan = _bundle_item(search_bundle, "finalist_search_plan")
    portfolio_search_scorecard = _bundle_item(search_bundle, "portfolio_search_scorecard")
    search_stop_reason = _bundle_item(search_bundle, "search_stop_reason")
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
    artifact_dependency_graph = _bundle_item(runtime_bundle, "artifact_dependency_graph")
    freshness_contract = _bundle_item(runtime_bundle, "freshness_contract")
    recompute_plan = _bundle_item(runtime_bundle, "recompute_plan")
    invalidation_report = _bundle_item(runtime_bundle, "invalidation_report")
    event_schema = dict(event_bus_bundle.get("event_schema", {})) if isinstance(event_bus_bundle.get("event_schema"), dict) else {}
    event_subscription_registry = dict(event_bus_bundle.get("event_subscription_registry", {})) if isinstance(event_bus_bundle.get("event_subscription_registry"), dict) else {}
    hook_registry = dict(event_bus_bundle.get("hook_registry", {})) if isinstance(event_bus_bundle.get("hook_registry"), dict) else {}
    hook_dispatch_report = dict(event_bus_bundle.get("hook_dispatch_report", {})) if isinstance(event_bus_bundle.get("hook_dispatch_report"), dict) else {}
    permission_mode = dict(permission_bundle.get("permission_mode", {})) if isinstance(permission_bundle.get("permission_mode"), dict) else {}
    tool_permission_matrix = dict(permission_bundle.get("tool_permission_matrix", {})) if isinstance(permission_bundle.get("tool_permission_matrix"), dict) else {}
    approval_policy_report = dict(permission_bundle.get("approval_policy_report", {})) if isinstance(permission_bundle.get("approval_policy_report"), dict) else {}
    session_capability_contract = dict(permission_bundle.get("session_capability_contract", {})) if isinstance(permission_bundle.get("session_capability_contract"), dict) else {}
    daemon_state = dict(daemon_bundle.get("daemon_state", {})) if isinstance(daemon_bundle.get("daemon_state"), dict) else {}
    background_job_registry = dict(daemon_bundle.get("background_job_registry", {})) if isinstance(daemon_bundle.get("background_job_registry"), dict) else {}
    background_checkpoint = dict(daemon_bundle.get("background_checkpoint", {})) if isinstance(daemon_bundle.get("background_checkpoint"), dict) else {}
    resume_session_manifest = dict(daemon_bundle.get("resume_session_manifest", {})) if isinstance(daemon_bundle.get("resume_session_manifest"), dict) else {}
    background_approval_queue = dict(daemon_bundle.get("background_approval_queue", {})) if isinstance(daemon_bundle.get("background_approval_queue"), dict) else {}
    memory_maintenance_queue = dict(daemon_bundle.get("memory_maintenance_queue", {})) if isinstance(daemon_bundle.get("memory_maintenance_queue"), dict) else {}
    memory_maintenance_report_v2 = dict(daemon_bundle.get("memory_maintenance_report", {})) if isinstance(daemon_bundle.get("memory_maintenance_report"), dict) else {}
    search_resume_plan = dict(daemon_bundle.get("search_resume_plan", {})) if isinstance(daemon_bundle.get("search_resume_plan"), dict) else {}
    stale_job_report = dict(daemon_bundle.get("stale_job_report", {})) if isinstance(daemon_bundle.get("stale_job_report"), dict) else {}
    remote_session_manifest = dict(remote_control_bundle.get("remote_session_manifest", {})) if isinstance(remote_control_bundle.get("remote_session_manifest"), dict) else {}
    remote_transport_report = dict(remote_control_bundle.get("remote_transport_report", {})) if isinstance(remote_control_bundle.get("remote_transport_report"), dict) else {}
    approval_request_queue = dict(remote_control_bundle.get("approval_request_queue", {})) if isinstance(remote_control_bundle.get("approval_request_queue"), dict) else {}
    remote_operator_presence = dict(remote_control_bundle.get("remote_operator_presence", {})) if isinstance(remote_control_bundle.get("remote_operator_presence"), dict) else {}
    supervision_handoff = dict(remote_control_bundle.get("supervision_handoff", {})) if isinstance(remote_control_bundle.get("supervision_handoff"), dict) else {}
    notification_delivery_report = dict(remote_control_bundle.get("notification_delivery_report", {})) if isinstance(remote_control_bundle.get("notification_delivery_report"), dict) else {}
    remote_control_audit = dict(remote_control_bundle.get("remote_control_audit", {})) if isinstance(remote_control_bundle.get("remote_control_audit"), dict) else {}
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
    next_step_resolution = _resolve_next_step_resolution(
        decision_constraint_report=decision_constraint_report,
        review_gate_state=review_gate_state,
        deployability_assessment=deployability_assessment,
        feedback_effect_report=feedback_effect_report,
        decision_usefulness_report=decision_usefulness_report,
        value_of_more_data_report=value_of_more_data_report,
        decision_policy_update_suggestions=decision_policy_update_suggestions,
        route_prior_updates=route_prior_updates,
        policy_update_suggestions=policy_update_suggestions,
        outcome_observation_report=outcome_observation_report,
        controller_policy=controller_policy,
        lifecycle_bundle=lifecycle_bundle,
        completion_decision=completion_decision,
        belief_update=belief_update,
        marginal_value=marginal_value,
    )
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
            daemon_bundle=daemon_bundle,
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
            "task_type": _clean_text(task_profile_contract.get("task_type"))
            or _clean_text(plan.get("task_type"))
            or _clean_text(task_brief.get("task_type_hint")),
            "primary_objective": _clean_text(focus_profile.get("primary_objective")),
            "selected_route_id": _clean_text(plan.get("selected_route_id")),
            "selected_route_title": _clean_text(plan.get("selected_route_title")),
            "selected_model_family": _clean_text(execution_summary.get("selected_model_family"))
            or _clean_text(model_params.get("model_name")),
            "best_validation_model_family": _clean_text(execution_summary.get("best_validation_model_family")),
            "primary_metric": _clean_text(metric_contract.get("deployment_primary_metric"))
            or _clean_text(plan.get("primary_metric"))
            or _clean_text(_bundle_item(investigation_bundle, "optimization_profile").get("primary_metric")),
            "selection_metric": _clean_text(metric_contract.get("selection_metric"))
            or _clean_text(dict(plan.get("builder_handoff") or {}).get("selection_metric")),
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
            "parity_status": _normalize_benchmark_parity_status(
                _clean_text(benchmark_parity_report.get("parity_status"))
            ),
            "recommended_action": _clean_text(benchmark_parity_report.get("recommended_action")),
            "comparison_metric": _clean_text(metric_contract.get("benchmark_comparison_metric"))
            or _clean_text(benchmark_parity_report.get("comparison_metric"))
            or _clean_text(reference_approach_matrix.get("comparison_metric")),
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
            "paper_status": _clean_text(paper_benchmark_manifest.get("status")) or _clean_text(paper_benchmark_table.get("status")),
            "claim_gate_status": _clean_text(benchmark_release_gate.get("status")) or _clean_text(paper_claim_guard_report.get("status")),
            "safe_to_cite_publicly": benchmark_release_gate.get("safe_to_cite_publicly"),
            "demo_safe": benchmark_release_gate.get("demo_safe"),
            "pack_partition": _clean_text(benchmark_pack_partition.get("partition_name")),
            "claim_origin": _clean_text(holdout_claim_policy.get("claim_origin")) or _clean_text(benchmark_pack_partition.get("claim_origin")),
            "paper_primary_claim_allowed": holdout_claim_policy.get("paper_primary_claim_allowed"),
            "competitiveness_claim": _clean_text(benchmark_claims_report.get("competitiveness_claim")),
            "deployment_claim": _clean_text(benchmark_claims_report.get("deployment_claim")),
            "below_reference": benchmark_claims_report.get("below_reference"),
            "claim_boundary_count": len(benchmark_claims_report.get("claim_boundaries", []))
            if isinstance(benchmark_claims_report.get("claim_boundaries"), list)
            else 0,
            "blocked_reason_count": len(benchmark_release_gate.get("blocked_reason_codes", []))
            if isinstance(benchmark_release_gate.get("blocked_reason_codes"), list)
            else 0,
            "ablation_row_count": len(benchmark_ablation_matrix.get("rows", []))
            if isinstance(benchmark_ablation_matrix.get("rows"), list)
            else 0,
            "rerun_match_count": int(rerun_variance_report.get("matching_run_count", 0) or 0),
            "rerun_stability_band": _clean_text(rerun_variance_report.get("stability_band")),
            "temporal_horizon_type": _clean_text(paper_benchmark_manifest.get("horizon_type")),
            "sequence_candidate_status": _clean_text(paper_benchmark_manifest.get("sequence_candidate_status")),
            "truth_audit_status": _clean_text(benchmark_truth_audit.get("status")),
            "leakage_status": _clean_text(dataset_leakage_audit.get("status")),
            "temporal_recovery_status": _clean_text(temporal_benchmark_recovery_report.get("recovery_state")) or _clean_text(temporal_benchmark_recovery_report.get("status")),
            "benchmark_generalization_status": _clean_text(benchmark_generalization_audit.get("status")),
            "identity_branching_detected": benchmark_generalization_audit.get("identity_branching_detected"),
            "aml_domain_active": aml_domain_contract.get("aml_active"),
            "aml_pack_family": _clean_text(aml_claim_scope.get("benchmark_pack_family")),
            "aml_claim_scope": _clean_text(aml_claim_scope.get("claim_scope")),
            "aml_public_claim_ready": aml_claim_scope.get("public_claim_ready"),
            "aml_dataset_family": _clean_text(aml_benchmark_manifest.get("dataset_family")),
            "aml_supporting_public_claim_allowed": aml_public_claim_guard.get("supporting_public_claim_allowed"),
            "aml_paper_primary_claim_allowed": aml_public_claim_guard.get("paper_primary_claim_allowed"),
            "aml_broader_flagship_claim_allowed": aml_public_claim_guard.get("broader_flagship_claim_allowed"),
            "aml_required_track_coverage_met": aml_benchmark_manifest.get("required_track_coverage_met"),
            "aml_current_run_story": _clean_text(aml_demo_scorecard.get("current_run_story")),
            "aml_ready_demo_count": int(aml_demo_scorecard.get("ready_demo_count", 0) or 0),
            "aml_demo_safe": aml_demo_scorecard.get("demo_safe"),
            "aml_primary_failure_kind": _clean_text(aml_failure_report.get("primary_failure_kind")),
            "aml_recommended_next_step": _clean_text(aml_failure_report.get("recommended_next_step")),
            "imported_candidate_count": int(shadow_trial_manifest.get("candidate_count", 0) or 0),
            "promotion_ready_count": int(promotion_readiness_report.get("promotion_ready_count", 0) or 0),
            "candidate_available_count": int(promotion_readiness_report.get("candidate_available_count", 0) or 0),
            "quarantined_candidate_count": int(candidate_quarantine.get("quarantined_count", 0) or 0),
        },
        "decision_lab": {
            "status": _clean_text(decision_world_model.get("status")),
            "action_regime": _clean_text(decision_world_model.get("action_regime")),
            "threshold_posture": _clean_text(decision_world_model.get("threshold_posture")),
            "under_specified": decision_world_model.get("under_specified"),
            "next_actor": _clean_text(controller_policy.get("next_actor")),
            "selected_next_action": _clean_text(decision_constraint_report.get("feasible_selected_action"))
            or _clean_text(controller_policy.get("selected_next_action")),
            "controller_selected_action": _clean_text(controller_policy.get("selected_next_action")),
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
            "imported_candidate_count": int(method_import_report.get("imported_family_count", 0) or 0),
            "changed_next_action": decision_usefulness_report.get("changed_next_action"),
            "changed_controller_path": decision_usefulness_report.get("changed_controller_path"),
            "baseline_action": _clean_text(handoff_controller_report.get("baseline_action")),
            "primary_decision_question": _clean_text(decision_world_model.get("primary_decision_question")),
        },
        "feasibility": {
            "trajectory_status": _clean_text(trajectory_constraint_report.get("trajectory_status")),
            "region_posture": _clean_text(feasible_region_map.get("region_posture")),
            "in_distribution": feasible_region_map.get("in_distribution"),
            "deployability": _clean_text(deployability_assessment.get("deployability")),
            "operational_readiness": _clean_text(deployability_assessment.get("operational_readiness")),
            "risk_band": _clean_text(extrapolation_risk_report.get("risk_band")),
            "observed_ood_fraction": extrapolation_risk_report.get("observed_ood_fraction"),
            "recommended_direction": _clean_text(decision_constraint_report.get("recommended_direction")),
            "selected_action": _clean_text(decision_constraint_report.get("feasible_selected_action"))
            or _clean_text(controller_policy.get("selected_next_action")),
            "controller_selected_action": _clean_text(decision_constraint_report.get("controller_selected_action"))
            or _clean_text(controller_policy.get("selected_next_action")),
            "recommendation_changed": decision_constraint_report.get("recommendation_changed"),
            "primary_constraint_kind": _clean_text(decision_constraint_report.get("primary_constraint_kind")),
            "blocking_constraint_count": len(decision_constraint_report.get("blocking_constraints", []))
            if isinstance(decision_constraint_report.get("blocking_constraints"), list)
            else 0,
            "gate_open": review_gate_state.get("gate_open"),
            "gate_kind": _clean_text(review_gate_state.get("gate_kind")),
            "override_required": constraint_override_request.get("override_required"),
            "why_not_rerun": _clean_text(counterfactual_region_report.get("why_not_rerun")),
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
            "trace_identity_status": _clean_text(trace_identity_conformance.get("status")),
            "trace_identity_mismatch_count": int(trace_identity_conformance.get("mismatch_count", 0) or 0),
            "surface_parity_status": _clean_text(eval_surface_parity_report.get("status")),
            "surface_parity_mismatch_count": int(eval_surface_parity_report.get("mismatch_count", 0) or 0),
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
            "budget_profile": _clean_text(dict(search_budget_envelope.get("controls", {})).get("budget_profile")),
            "probe_family_count": int(portfolio_search_scorecard.get("probe_family_count", 0) or 0),
            "race_family_count": int(portfolio_search_scorecard.get("race_family_count", 0) or 0),
            "finalist_count": int(portfolio_search_scorecard.get("finalist_count", 0) or 0),
            "calibration_budget": int(finalist_search_plan.get("calibration_budget", 0) or 0),
            "stop_reason_kind": _clean_text(search_stop_reason.get("reason_kind")),
            "skipped_deeper_work_count": int(portfolio_search_scorecard.get("skipped_deeper_work_count", 0) or 0),
            "probe_promoted_family_count": len(probe_stage_report.get("promoted_families", []))
            if isinstance(probe_stage_report.get("promoted_families"), list)
            else 0,
            "race_finalist_count": len(family_race_report.get("finalists", []))
            if isinstance(family_race_report.get("finalists"), list)
            else 0,
        },
        "hpo": {
            "status": _clean_text(search_loop_scorecard.get("status")) or _clean_text(hpo_budget_contract.get("status")),
            "backend": _clean_text(search_loop_scorecard.get("backend")) or _clean_text(hpo_budget_contract.get("backend")),
            "selected_families": [
                str(item)
                for item in hpo_budget_contract.get("selected_families", [])
                if str(item).strip()
            ],
            "planned_family_count": len(hpo_budget_contract.get("selected_families", []))
            if isinstance(hpo_budget_contract.get("selected_families"), list)
            else 0,
            "search_space_family_count": int(architecture_search_space.get("family_count", 0) or 0),
            "max_trials": int(hpo_budget_contract.get("max_trials", 0) or 0),
            "executed_trial_count": int(search_loop_scorecard.get("total_trials_executed", 0) or len(trial_ledger)),
            "tuned_family_count": int(
                search_loop_scorecard.get("tuned_family_count", 0)
                or early_stopping_report.get("family_count", 0)
                or 0
            ),
            "warm_start_used": bool(warm_start_transfer_report.get("used")),
            "imported_family_count": len(warm_start_transfer_report.get("imported_families", []))
            if isinstance(warm_start_transfer_report.get("imported_families"), list)
            else 0,
            "plateau_triggered_count": int(early_stopping_report.get("plateau_triggered_count", 0) or 0),
            "wall_clock_exhausted_count": int(early_stopping_report.get("wall_clock_exhausted_count", 0) or 0),
            "threshold_policy": _clean_text(threshold_tuning_report.get("threshold_policy")),
            "selected_threshold": threshold_tuning_report.get("selected_threshold"),
            "selected_calibration_method": _clean_text(calibration_strategy_report.get("selected_method")),
            "stop_reasons": [
                str(item)
                for item in search_loop_scorecard.get("stop_reasons", [])
                if str(item).strip()
            ],
            "summary": _clean_text(search_loop_scorecard.get("summary"))
            or _clean_text(early_stopping_report.get("summary"))
            or _clean_text(hpo_budget_contract.get("summary")),
        },
        "operating_point": {
            "status": _clean_text(operating_point_contract.get("status")) or _clean_text(calibration_strategy_report.get("status")),
            "selected_threshold": operating_point_contract.get("selected_threshold"),
            "threshold_policy": _clean_text(operating_point_contract.get("threshold_policy"))
            or _clean_text(threshold_tuning_report.get("threshold_policy")),
            "raw_best_threshold": operating_point_contract.get("raw_best_threshold")
            or threshold_search_report.get("raw_best_threshold"),
            "review_budget_threshold": operating_point_contract.get("review_budget_threshold")
            or review_budget_optimization_report.get("review_budget_threshold"),
            "review_budget_fraction": operating_point_contract.get("review_budget_fraction")
            or review_budget_optimization_report.get("review_budget_fraction"),
            "selected_review_fraction": operating_point_contract.get("selected_review_fraction")
            or review_budget_optimization_report.get("selected_review_fraction"),
            "selected_reason_codes": [
                str(item)
                for item in operating_point_contract.get("selected_reason_codes", [])
                if str(item).strip()
            ],
            "selection_reason": _clean_text(operating_point_contract.get("selection_reason"))
            or _clean_text(review_budget_optimization_report.get("summary")),
            "selected_calibration_method": _clean_text(calibration_strategy_report.get("selected_method")),
            "calibration_selection_metric": _clean_text(calibration_strategy_report.get("selection_metric")),
            "calibration_selection_reason": _clean_text(calibration_strategy_report.get("selection_reason")),
            "decision_cost_profile_kind": _clean_text(decision_cost_profile.get("profile_kind"))
            or _clean_text(dict(operating_point_contract.get("decision_cost_profile", {})).get("profile_kind")),
            "review_budget_changed_threshold": review_budget_optimization_report.get("review_budget_changed_threshold"),
            "abstention_state": _clean_text(abstention_policy_report.get("abstention_state"))
            or _clean_text(operating_point_contract.get("abstention_state")),
            "abstain_low": abstention_policy_report.get("abstain_low"),
            "abstain_high": abstention_policy_report.get("abstain_high"),
            "threshold_candidate_count": len(threshold_search_report.get("threshold_candidates", []))
            if isinstance(threshold_search_report.get("threshold_candidates"), list)
            else 0,
            "summary": _clean_text(operating_point_contract.get("summary"))
            or _clean_text(calibration_strategy_report.get("summary")),
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
        "task_contract": {
            "status": _clean_text(task_profile_contract.get("status")),
            "task_type": _clean_text(task_profile_contract.get("task_type")),
            "task_family": _clean_text(task_profile_contract.get("task_family")),
            "problem_posture": _clean_text(task_profile_contract.get("problem_posture")),
            "target_semantics": _clean_text(target_semantics_report.get("target_semantics"))
            or _clean_text(task_profile_contract.get("target_semantics")),
            "rare_event_supervised": bool(task_profile_contract.get("rare_event_supervised", False)),
            "benchmark_expected": benchmark_mode_report.get("benchmark_expected"),
            "benchmark_comparison_metric": _clean_text(metric_contract.get("benchmark_comparison_metric")),
            "deployment_primary_metric": _clean_text(metric_contract.get("deployment_primary_metric")),
            "why_not_anomaly_detection": _clean_text(target_semantics_report.get("why_not_anomaly_detection"))
            or _clean_text(task_profile_contract.get("why_not_anomaly_detection")),
            "multiclass_string_labels_preserved": dataset_semantics_audit.get("multiclass_string_labels_preserved"),
        },
        "aml": {
            "status": _clean_text(aml_domain_contract.get("status")) or _clean_text(aml_review_budget_contract.get("status")),
            "aml_active": aml_domain_contract.get("aml_active"),
            "domain_focus": _clean_text(aml_domain_contract.get("domain_focus")),
            "target_level": _clean_text(aml_domain_contract.get("target_level")),
            "business_goal": _clean_text(aml_domain_contract.get("business_goal")),
            "review_budget_relevant": aml_domain_contract.get("review_budget_relevant"),
            "review_priority": _clean_text(aml_review_budget_contract.get("priority")),
            "decision_objective": _clean_text(aml_review_budget_contract.get("decision_objective")),
            "recommended_next_action": _clean_text(aml_review_budget_contract.get("recommended_next_action")),
            "entity_type_count": len(aml_case_ontology.get("entity_types", []))
            if isinstance(aml_case_ontology.get("entity_types"), list)
            else 0,
            "typology_candidate_count": len(aml_case_ontology.get("typology_candidates", []))
            if isinstance(aml_case_ontology.get("typology_candidates"), list)
            else 0,
            "claim_scope": _clean_text(aml_claim_scope.get("claim_scope")),
            "benchmark_pack_family": _clean_text(aml_claim_scope.get("benchmark_pack_family")),
            "public_claim_ready": aml_claim_scope.get("public_claim_ready"),
            "summary": _clean_text(aml_review_budget_contract.get("summary"))
            or _clean_text(aml_domain_contract.get("summary"))
            or _clean_text(aml_claim_scope.get("summary")),
        },
        "aml_graph": {
            "status": _clean_text(entity_graph_profile.get("status")) or _clean_text(subgraph_risk_report.get("status")),
            "node_count": int(entity_graph_profile.get("node_count", 0) or 0),
            "edge_count": int(entity_graph_profile.get("edge_count", 0) or 0),
            "component_count": int(counterparty_network_report.get("component_count", 0) or 0),
            "high_risk_entity_count": len(entity_graph_profile.get("high_risk_entities", []))
            if isinstance(entity_graph_profile.get("high_risk_entities"), list)
            else 0,
            "top_entity": _clean_text(dict(entity_graph_profile.get("high_risk_entities", [{}])[0]).get("entity_id"))
            if isinstance(entity_graph_profile.get("high_risk_entities"), list) and entity_graph_profile.get("high_risk_entities")
            else None,
            "typology_hit_count": int(typology_detection_report.get("typology_hit_count", 0) or 0),
            "top_typology": _clean_text(dict(typology_detection_report.get("typology_hits", [{}])[0]).get("typology"))
            if isinstance(typology_detection_report.get("typology_hits"), list) and typology_detection_report.get("typology_hits")
            else None,
            "focal_entity": _clean_text(entity_case_expansion.get("focal_entity")),
            "expanded_entity_count": int(entity_case_expansion.get("expanded_entity_count", 0) or 0),
            "shadow_winner": _clean_text(dict(subgraph_risk_report.get("candidate_comparison", {})).get("winner")),
            "summary": _clean_text(entity_case_expansion.get("summary"))
            or _clean_text(subgraph_risk_report.get("summary"))
            or _clean_text(entity_graph_profile.get("summary")),
        },
        "casework": {
            "status": _clean_text(alert_queue_policy.get("status"))
            or _clean_text(alert_queue_rankings.get("status"))
            or _clean_text(case_packet.get("status")),
            "queue_count": int(alert_queue_rankings.get("queue_count", 0) or 0),
            "review_capacity_cases": int(alert_queue_policy.get("review_capacity_cases", 0) or 0),
            "review_budget_fraction": alert_queue_policy.get("review_budget_fraction"),
            "decision_objective": _clean_text(alert_queue_policy.get("decision_objective")),
            "top_case_id": _clean_text(case_packet.get("case_id"))
            or _clean_text(analyst_review_scorecard.get("top_case_id")),
            "top_case_entity": _clean_text(case_packet.get("focal_entity")),
            "top_case_priority_score": case_packet.get("priority_score")
            or analyst_review_scorecard.get("top_priority_score"),
            "top_case_action": _clean_text(case_packet.get("review_action")),
            "estimated_review_hours": analyst_review_scorecard.get("estimated_review_hours"),
            "review_typology_coverage": analyst_review_scorecard.get("review_typology_coverage"),
            "selected_review_fraction": review_capacity_sensitivity.get("selected_review_fraction")
            or alert_queue_policy.get("review_budget_fraction"),
            "summary": _clean_text(case_packet.get("summary"))
            or _clean_text(analyst_review_scorecard.get("summary"))
            or _clean_text(alert_queue_policy.get("summary")),
        },
        "stream_risk": {
            "status": _clean_text(stream_risk_posture.get("status"))
            or _clean_text(weak_label_posture.get("status"))
            or _clean_text(drift_recalibration_trigger.get("status")),
            "stream_mode": _clean_text(stream_risk_posture.get("stream_mode")),
            "timestamp_column": _clean_text(stream_risk_posture.get("timestamp_column"))
            or _clean_text(rolling_alert_quality_report.get("timestamp_column")),
            "weak_label_risk_level": _clean_text(weak_label_posture.get("weak_label_risk_level")),
            "label_kind": _clean_text(weak_label_posture.get("label_kind")),
            "delayed_confirmation_likely": delayed_outcome_alignment.get("delayed_confirmation_likely"),
            "alignment_state": _clean_text(delayed_outcome_alignment.get("alignment_state")),
            "rolling_window_count": int(rolling_alert_quality_report.get("window_count", 0) or 0),
            "latest_alert_rate": rolling_alert_quality_report.get("latest_alert_rate"),
            "drift_score": drift_recalibration_trigger.get("drift_score"),
            "trigger_recalibration": drift_recalibration_trigger.get("trigger_recalibration"),
            "trigger_action": _clean_text(drift_recalibration_trigger.get("recommended_action")),
            "threshold_posture": _clean_text(drift_recalibration_trigger.get("threshold_posture")),
            "benchmark_safe": rolling_alert_quality_report.get("benchmark_safe")
            if "benchmark_safe" in rolling_alert_quality_report
            else stream_risk_posture.get("benchmark_safe"),
            "audit_safe": stream_risk_posture.get("audit_safe"),
            "summary": _clean_text(stream_risk_posture.get("summary"))
            or _clean_text(drift_recalibration_trigger.get("summary"))
            or _clean_text(weak_label_posture.get("summary")),
        },
        "aml_proof": {
            "status": _clean_text(aml_benchmark_manifest.get("status"))
            or _clean_text(aml_demo_scorecard.get("status"))
            or _clean_text(aml_public_claim_guard.get("status")),
            "dataset_family": _clean_text(aml_benchmark_manifest.get("dataset_family")),
            "benchmark_track": _clean_text(aml_benchmark_manifest.get("benchmark_track")),
            "current_partition": _clean_text(aml_benchmark_manifest.get("current_partition")),
            "supporting_public_claim_allowed": aml_public_claim_guard.get("supporting_public_claim_allowed"),
            "paper_primary_claim_allowed": aml_public_claim_guard.get("paper_primary_claim_allowed"),
            "broader_flagship_claim_allowed": aml_public_claim_guard.get("broader_flagship_claim_allowed"),
            "required_track_coverage_met": aml_benchmark_manifest.get("required_track_coverage_met"),
            "covered_track_families": list(aml_benchmark_manifest.get("covered_track_families", []))
            if isinstance(aml_benchmark_manifest.get("covered_track_families"), list)
            else [],
            "current_run_story": _clean_text(aml_demo_scorecard.get("current_run_story")),
            "ready_demo_count": int(aml_demo_scorecard.get("ready_demo_count", 0) or 0),
            "demo_safe": aml_demo_scorecard.get("demo_safe"),
            "primary_failure_kind": _clean_text(aml_failure_report.get("primary_failure_kind")),
            "recommended_next_step": _clean_text(aml_failure_report.get("recommended_next_step")),
            "summary": _clean_text(aml_failure_report.get("summary"))
            or _clean_text(aml_public_claim_guard.get("summary"))
            or _clean_text(aml_benchmark_manifest.get("summary")),
            "scored_demos": list(aml_demo_scorecard.get("scored_demos", []))
            if isinstance(aml_demo_scorecard.get("scored_demos"), list)
            else [],
        },
        "objective_contract": {
            "status": _clean_text(objective_alignment_report.get("status")) or _clean_text(optimization_objective_contract.get("status")),
            "selection_metric": _clean_text(optimization_objective_contract.get("family_selection_metric")),
            "calibration_metric": _clean_text(optimization_objective_contract.get("calibration_metric")),
            "threshold_metric": _clean_text(optimization_objective_contract.get("threshold_metric")),
            "benchmark_comparison_metric": _clean_text(optimization_objective_contract.get("benchmark_comparison_metric")),
            "deployment_decision_metric": _clean_text(optimization_objective_contract.get("deployment_decision_metric")),
            "explicit_metric_split": optimization_objective_contract.get("explicit_metric_split"),
            "benchmark_metric_materialized_in_execution": metric_materialization_audit.get("benchmark_metric_materialized_in_execution"),
            "benchmark_metric_materialized_in_benchmark_rows": metric_materialization_audit.get("benchmark_metric_materialized_in_benchmark_rows"),
            "truth_precheck_status": _clean_text(benchmark_truth_precheck.get("status")),
            "safe_to_rank": benchmark_truth_precheck.get("safe_to_rank"),
            "summary": _clean_text(objective_alignment_report.get("summary")) or _clean_text(optimization_objective_contract.get("summary")),
        },
        "split_health": {
            "status": _clean_text(split_diagnostics_report.get("status")),
            "split_strategy": _clean_text(split_diagnostics_report.get("split_strategy")),
            "data_mode": _clean_text(split_diagnostics_report.get("data_mode")),
            "train_size": split_diagnostics_report.get("train_size"),
            "validation_size": split_diagnostics_report.get("validation_size"),
            "test_size": split_diagnostics_report.get("test_size"),
            "validation_positive_count": split_diagnostics_report.get("validation_positive_count"),
            "test_positive_count": split_diagnostics_report.get("test_positive_count"),
            "zero_positive_validation": split_diagnostics_report.get("zero_positive_validation"),
            "zero_positive_test": split_diagnostics_report.get("zero_positive_test"),
            "temporal_fold_status": _clean_text(temporal_fold_health.get("status")),
            "safe_for_benchmarking": benchmark_truth_precheck.get("safe_to_rank"),
            "summary": _clean_text(temporal_fold_health.get("summary")) or _clean_text(split_diagnostics_report.get("summary")),
        },
        "temporal": {
            "status": _clean_text(temporal_structure_report.get("status")),
            "ordered_temporal_structure": temporal_structure_report.get("ordered_temporal_structure"),
            "timestamp_column": _clean_text(temporal_structure_report.get("timestamp_column")) or _clean_text(task_profile_contract.get("timestamp_column")),
            "regular_cadence": temporal_structure_report.get("regular_cadence"),
            "lag_horizon_samples": temporal_feature_ladder.get("lag_horizon_samples"),
            "rolling_window_samples": temporal_feature_ladder.get("rolling_window_samples"),
            "materialized_feature_families": [
                str(item) for item in temporal_feature_ladder.get("materialized_feature_families", []) if str(item).strip()
            ],
            "split_guard_state": _clean_text(temporal_split_guard_report.get("guard_state")),
            "rolling_cv_strategy": _clean_text(rolling_cv_plan.get("recommended_strategy")),
            "lagged_beats_ordinary": temporal_baseline_ladder.get("lagged_beats_ordinary"),
            "baseline_comparison_metric": _clean_text(temporal_baseline_ladder.get("comparison_metric")),
            "sequence_shadow_rows": len(sequence_shadow_scorecard.get("rows", []))
            if isinstance(sequence_shadow_scorecard.get("rows"), list)
            else 0,
            "temporal_metric_status": _clean_text(temporal_metric_contract.get("status")),
            "summary": _clean_text(temporal_split_guard_report.get("summary"))
            or _clean_text(temporal_structure_report.get("summary")),
        },
        "benchmark_vs_deploy": {
            "status": _clean_text(benchmark_vs_deploy_report.get("status")),
            "benchmark_status": _clean_text(benchmark_vs_deploy_report.get("benchmark_status")),
            "deployment_readiness": _clean_text(benchmark_vs_deploy_report.get("deployment_readiness"))
            or _clean_text(deployment_readiness_report.get("readiness_state")),
            "split_detected": bool(benchmark_vs_deploy_report.get("split_detected"))
            or _infer_benchmark_deploy_split(
                parity_status=_clean_text(benchmark_parity_report.get("parity_status")),
                deployment_readiness=_clean_text(benchmark_vs_deploy_report.get("deployment_readiness"))
                or _clean_text(deployment_readiness_report.get("readiness_state")),
            ),
            "summary": _benchmark_vs_deploy_summary(
                summary=_clean_text(benchmark_vs_deploy_report.get("summary")),
                parity_status=_clean_text(benchmark_parity_report.get("parity_status")),
                deployment_readiness=_clean_text(benchmark_vs_deploy_report.get("deployment_readiness"))
                or _clean_text(deployment_readiness_report.get("readiness_state")),
            ),
            "benchmark_expected": benchmark_mode_report.get("benchmark_expected"),
        },
        "architecture": {
            "status": _clean_text(architecture_router_report.get("status")) or _clean_text(architecture_registry.get("status")),
            "recommended_primary_family": _clean_text(architecture_router_report.get("recommended_primary_family")),
            "candidate_order": [str(item) for item in architecture_router_report.get("candidate_order", []) if str(item).strip()],
            "baseline_candidate_order": [str(item) for item in architecture_router_report.get("baseline_candidate_order", []) if str(item).strip()],
            "memory_adjusted_candidate_order": [str(item) for item in architecture_router_report.get("memory_adjusted_candidate_order", []) if str(item).strip()],
            "benchmark_evidence_status": _clean_text(architecture_router_report.get("benchmark_evidence_status")),
            "workspace_analog_status": _clean_text(architecture_router_report.get("workspace_analog_status")),
            "workspace_analog_influence": architecture_router_report.get("workspace_analog_influence"),
            "sequence_live_allowed": architecture_router_report.get("sequence_live_allowed"),
            "sequence_shadow_ready": architecture_router_report.get("sequence_shadow_ready"),
            "sequence_rejection_reason": _clean_text(architecture_router_report.get("sequence_rejection_reason")),
            "top_selection_reason": _clean_text(architecture_router_report.get("top_selection_reason")),
            "candidate_count": int(candidate_family_matrix.get("candidate_count", 0) or 0),
            "available_family_count": int(architecture_registry.get("available_family_count", 0) or 0),
            "fit_top_family": _clean_text(dict(architecture_fit_report.get("fit_rows", [{}])[0]).get("family_id"))
            if isinstance(architecture_fit_report.get("fit_rows"), list) and architecture_fit_report.get("fit_rows")
            else None,
            "live_family_count": len([item for item in family_capability_matrix.get("families", []) if bool(dict(item).get("training_support"))])
            if isinstance(family_capability_matrix.get("families"), list)
            else 0,
            "shadow_sequence_candidates": [
                str(item)
                for item in architecture_ablation_report.get("shadow_sequence_candidates", [])
                if str(item).strip()
            ],
        },
        "family_stack": {
            "status": _clean_text(family_registry_extension.get("status")) or _clean_text(family_eligibility_matrix.get("status")),
            "eligible_family_count": int(family_registry_extension.get("eligible_family_count", 0) or family_eligibility_matrix.get("eligible_family_count", 0) or 0),
            "adapter_ready_family_count": int(family_registry_extension.get("adapter_ready_family_count", 0) or family_readiness_report.get("adapter_ready_family_count", 0) or 0),
            "categorical_strategy": _clean_text(categorical_strategy_report.get("selected_strategy")),
            "categorical_priority_families": [
                str(item)
                for item in family_specialization_report.get("categorical_priority_families", [])
                if str(item).strip()
            ],
            "small_data_specialist_families": [
                str(item)
                for item in family_specialization_report.get("small_data_specialist_families", [])
                if str(item).strip()
            ],
            "multiclass_widening_active": family_specialization_report.get("multiclass_widening_active"),
            "rare_event_policy_active": family_specialization_report.get("rare_event_policy_active"),
            "multiclass_profile_status": _clean_text(multiclass_search_profile.get("status")),
            "rare_event_profile_status": _clean_text(rare_event_search_profile.get("status")),
            "activated_adapter_family_count": int(adapter_activation_report.get("activated_family_count", 0) or 0),
            "activated_adapter_families": [
                str(item.get("family_id"))
                for item in adapter_activation_report.get("rows", [])
                if isinstance(item, dict) and str(item.get("activation_state")) == "active" and str(item.get("family_id", "")).strip()
            ],
            "probe_tier_one_families": [
                str(item)
                for item in family_probe_policy.get("tier_one_families", [])
                if str(item).strip()
            ],
            "eligible_families": [
                str(item.get("family_id"))
                for item in family_eligibility_matrix.get("rows", [])
                if isinstance(item, dict) and item.get("eligible") and str(item.get("family_id", "")).strip()
            ],
            "blocked_reasons_by_family": {
                str(item.get("family_id")): _clean_text(item.get("block_reason"))
                for item in family_eligibility_matrix.get("rows", [])
                if isinstance(item, dict)
                and str(item.get("family_id", "")).strip()
                and _clean_text(item.get("block_reason"))
            },
        },
        "architecture_imports": {
            "status": _clean_text(method_import_report.get("status")) or _clean_text(promotion_readiness_report.get("status")),
            "imported_family_count": int(method_import_report.get("imported_family_count", 0) or 0),
            "candidate_count": int(architecture_candidate_registry.get("candidate_count", 0) or 0),
            "shadow_trial_count": len(shadow_trial_scorecard.get("rows", []))
            if isinstance(shadow_trial_scorecard.get("rows"), list)
            else 0,
            "promotion_ready_count": int(promotion_readiness_report.get("promotion_ready_count", 0) or 0),
            "candidate_available_count": int(promotion_readiness_report.get("candidate_available_count", 0) or 0),
            "quarantined_count": int(candidate_quarantine.get("quarantined_count", 0) or 0),
            "top_candidate_family": (
                _clean_text(dict(architecture_candidate_registry.get("candidates", [{}])[0]).get("family_id"))
                if isinstance(architecture_candidate_registry.get("candidates"), list)
                and architecture_candidate_registry.get("candidates")
                else None
            ),
            "top_promotion_state": (
                _clean_text(dict(promotion_readiness_report.get("rows", [{}])[0]).get("promotion_state"))
                if isinstance(promotion_readiness_report.get("rows"), list)
                and promotion_readiness_report.get("rows")
                else None
            ),
            "promotion_ready_families": [
                str(item.get("family_id"))
                for item in promotion_readiness_report.get("rows", [])
                if isinstance(item, dict) and str(item.get("promotion_state")) == "promotion_ready" and str(item.get("family_id", "")).strip()
            ][:5],
            "candidate_available_families": [
                str(item.get("family_id"))
                for item in promotion_readiness_report.get("rows", [])
                if isinstance(item, dict) and str(item.get("promotion_state")) == "candidate_available" and str(item.get("family_id", "")).strip()
            ][:5],
            "quarantined_families": [
                str(item.get("family_id"))
                for item in promotion_readiness_report.get("rows", [])
                if isinstance(item, dict) and str(item.get("promotion_state")) == "quarantined" and str(item.get("family_id", "")).strip()
            ][:5],
            "shadow_only_families": [
                str(item.get("family_id"))
                for item in architecture_candidate_registry.get("candidates", [])
                if isinstance(item, dict) and str(item.get("shadow_policy")) in {"shadow_only", "offline_replay_only"} and str(item.get("family_id", "")).strip()
            ][:5],
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
            "fresh_stage_count": int(freshness_contract.get("fresh_stage_count", 0) or 0),
            "recompute_stage_count": int(recompute_plan.get("recompute_stage_count", 0) or 0),
            "invalidated_stage_count": int(invalidation_report.get("invalidated_stage_count", 0) or 0),
            "next_recompute_stage": _clean_text(dict(recompute_plan.get("next_recommended_stage", {})).get("stage")),
            "dependency_graph_node_count": int(artifact_dependency_graph.get("node_count", 0) or 0),
        },
        "event_bus": {
            "event_type_count": int(event_schema.get("event_type_count", 0) or 0),
            "subscription_count": int(event_subscription_registry.get("subscription_count", 0) or 0),
            "hook_registry_count": int(hook_registry.get("hook_count", 0) or 0),
            "dispatch_count": int(hook_dispatch_report.get("dispatch_count", 0) or 0),
            "observed_event_count": int(hook_dispatch_report.get("observed_event_count", 0) or 0),
            "source_of_truth_preserved": bool(hook_dispatch_report.get("source_of_truth_preserved", False)) if hook_dispatch_report else None,
        },
        "permissions": {
            "current_mode": _clean_text(permission_mode.get("current_mode")),
            "mode_source": _clean_text(permission_mode.get("mode_source")),
            "pending_approval_count": int(approval_policy_report.get("pending_approval_count", 0) or 0),
            "approval_requested_count": int(approval_policy_report.get("approval_requested_count", 0) or 0),
            "denied_count": int(approval_policy_report.get("denied_count", 0) or 0),
            "allowed_action_count": int(session_capability_contract.get("allowed_action_count", 0) or 0),
            "approval_gated_action_count": int(session_capability_contract.get("approval_gated_action_count", 0) or 0),
            "blocked_action_count": int(session_capability_contract.get("blocked_action_count", 0) or 0),
        },
        "daemon": {
            "status": _clean_text(daemon_state.get("status")),
            "background_execution_enabled": daemon_state.get("background_execution_enabled"),
            "job_count": int(daemon_state.get("job_count", 0) or 0),
            "active_job_count": int(daemon_state.get("active_job_count", 0) or 0),
            "queued_job_count": int(daemon_state.get("queued_job_count", 0) or 0),
            "paused_job_count": int(daemon_state.get("paused_job_count", 0) or 0),
            "pending_approval_count": int(background_approval_queue.get("pending_approval_count", 0) or 0),
            "resumable_job_count": int(resume_session_manifest.get("resumable_job_count", 0) or 0),
            "checkpoint_count": int(background_checkpoint.get("checkpoint_count", 0) or 0),
            "stale_job_count": int(stale_job_report.get("stale_job_count", 0) or 0),
            "memory_task_count": int(memory_maintenance_queue.get("queued_task_count", 0) or 0),
            "memory_maintenance_executed": memory_maintenance_report_v2.get("executed"),
            "search_resume_ready": search_resume_plan.get("resume_ready"),
            "next_resume_step": _clean_text(search_resume_plan.get("next_step")),
        },
        "remote": {
            "status": _clean_text(remote_session_manifest.get("status"))
            or _clean_text(remote_control_audit.get("status"))
            or ("disabled" if remote_transport_report or remote_control_audit else None),
            "remote_enabled": bool(remote_control_audit.get("remote_enabled", False))
            if remote_control_audit
            else bool(remote_session_manifest.get("transport_enabled", False)),
            "transport_enabled": bool(remote_transport_report.get("transport_enabled", False))
            if remote_transport_report
            else None,
            "transport_kind": _clean_text(remote_transport_report.get("transport_kind"))
            or _clean_text(remote_session_manifest.get("transport_kind")),
            "transport_scope": _clean_text(remote_transport_report.get("transport_scope")),
            "freshness_status": _clean_text(remote_operator_presence.get("freshness_status"))
            or _clean_text(remote_session_manifest.get("freshness_status")),
            "current_supervisor_type": _clean_text(remote_operator_presence.get("current_supervisor_type"))
            or _clean_text((dict(supervision_handoff.get("current_supervisor", {}))).get("actor_type")),
            "current_supervisor_name": _clean_text(remote_operator_presence.get("current_supervisor_name"))
            or _clean_text((dict(supervision_handoff.get("current_supervisor", {}))).get("actor_name")),
            "pending_approval_count": int(approval_request_queue.get("pending_approval_count", 0) or 0),
            "approval_source_count": int(approval_request_queue.get("approval_source_count", 0) or 0),
            "write_actions_allowed": remote_session_manifest.get("write_actions_allowed"),
            "notification_count": int(notification_delivery_report.get("notification_count", 0) or 0),
            "undelivered_count": int(notification_delivery_report.get("undelivered_count", 0) or 0),
            "handoff_count": int(supervision_handoff.get("handoff_count", 0) or 0),
            "blocked_handoff_count": int(supervision_handoff.get("blocked_handoff_count", 0) or 0),
            "blocked_action_count": int(remote_control_audit.get("blocked_action_count", 0) or 0),
            "last_remote_action_kind": _clean_text(remote_control_audit.get("last_remote_action_kind")),
            "last_remote_action_at": _clean_text(remote_control_audit.get("last_remote_action_at")),
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
            "rationale": next_step_resolution["rationale"],
            "recommended_action": next_step_resolution["recommended_action"],
            "recommended_action_source": next_step_resolution["source"],
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
            "task_profile_contract_path": _path_if_exists(root / "task_profile_contract.json"),
            "target_semantics_report_path": _path_if_exists(root / "target_semantics_report.json"),
            "metric_contract_path": _path_if_exists(root / "metric_contract.json"),
            "benchmark_mode_report_path": _path_if_exists(root / "benchmark_mode_report.json"),
            "deployment_readiness_report_path": _path_if_exists(root / "deployment_readiness_report.json"),
            "benchmark_vs_deploy_report_path": _path_if_exists(root / "benchmark_vs_deploy_report.json"),
                "dataset_semantics_audit_path": _path_if_exists(root / "dataset_semantics_audit.json"),
                "optimization_objective_contract_path": _path_if_exists(root / "optimization_objective_contract.json"),
                "objective_alignment_report_path": _path_if_exists(root / "objective_alignment_report.json"),
                "split_diagnostics_report_path": _path_if_exists(root / "split_diagnostics_report.json"),
                "temporal_fold_health_path": _path_if_exists(root / "temporal_fold_health.json"),
            "metric_materialization_audit_path": _path_if_exists(root / "metric_materialization_audit.json"),
            "benchmark_truth_precheck_path": _path_if_exists(root / "benchmark_truth_precheck.json"),
            "aml_domain_contract_path": _path_if_exists(root / "aml_domain_contract.json"),
            "aml_case_ontology_path": _path_if_exists(root / "aml_case_ontology.json"),
            "aml_review_budget_contract_path": _path_if_exists(root / "aml_review_budget_contract.json"),
            "aml_claim_scope_path": _path_if_exists(root / "aml_claim_scope.json"),
            "entity_graph_profile_path": _path_if_exists(root / "entity_graph_profile.json"),
            "counterparty_network_report_path": _path_if_exists(root / "counterparty_network_report.json"),
            "typology_detection_report_path": _path_if_exists(root / "typology_detection_report.json"),
            "subgraph_risk_report_path": _path_if_exists(root / "subgraph_risk_report.json"),
            "entity_case_expansion_path": _path_if_exists(root / "entity_case_expansion.json"),
            "alert_queue_policy_path": _path_if_exists(root / "alert_queue_policy.json"),
            "alert_queue_rankings_path": _path_if_exists(root / "alert_queue_rankings.json"),
            "analyst_review_scorecard_path": _path_if_exists(root / "analyst_review_scorecard.json"),
            "case_packet_path": _path_if_exists(root / "case_packet.json"),
            "review_capacity_sensitivity_path": _path_if_exists(root / "review_capacity_sensitivity.json"),
            "stream_risk_posture_path": _path_if_exists(root / "stream_risk_posture.json"),
            "weak_label_posture_path": _path_if_exists(root / "weak_label_posture.json"),
            "delayed_outcome_alignment_path": _path_if_exists(root / "delayed_outcome_alignment.json"),
            "drift_recalibration_trigger_path": _path_if_exists(root / "drift_recalibration_trigger.json"),
            "rolling_alert_quality_report_path": _path_if_exists(root / "rolling_alert_quality_report.json"),
            "temporal_structure_report_path": _path_if_exists(root / "temporal_structure_report.json"),
                "temporal_feature_ladder_path": _path_if_exists(root / "temporal_feature_ladder.json"),
                "rolling_cv_plan_path": _path_if_exists(root / "rolling_cv_plan.json"),
                "temporal_split_guard_report_path": _path_if_exists(root / "temporal_split_guard_report.json"),
                "sequence_shadow_scorecard_path": _path_if_exists(root / "sequence_shadow_scorecard.json"),
                "temporal_baseline_ladder_path": _path_if_exists(root / "temporal_baseline_ladder.json"),
                "temporal_metric_contract_path": _path_if_exists(root / "temporal_metric_contract.json"),
                "architecture_registry_path": _path_if_exists(root / "architecture_registry.json"),
            "architecture_router_report_path": _path_if_exists(root / "architecture_router_report.json"),
            "candidate_family_matrix_path": _path_if_exists(root / "candidate_family_matrix.json"),
            "architecture_fit_report_path": _path_if_exists(root / "architecture_fit_report.json"),
            "family_capability_matrix_path": _path_if_exists(root / "family_capability_matrix.json"),
            "architecture_ablation_report_path": _path_if_exists(root / "architecture_ablation_report.json"),
            "family_registry_extension_path": _path_if_exists(root / "family_registry_extension.json"),
            "family_readiness_report_path": _path_if_exists(root / "family_readiness_report.json"),
            "family_eligibility_matrix_path": _path_if_exists(root / "family_eligibility_matrix.json"),
            "family_probe_policy_path": _path_if_exists(root / "family_probe_policy.json"),
            "categorical_strategy_report_path": _path_if_exists(root / "categorical_strategy_report.json"),
            "family_specialization_report_path": _path_if_exists(root / "family_specialization_report.json"),
            "family_specialization_matrix_path": _path_if_exists(root / "family_specialization_matrix.json"),
            "multiclass_search_profile_path": _path_if_exists(root / "multiclass_search_profile.json"),
            "rare_event_search_profile_path": _path_if_exists(root / "rare_event_search_profile.json"),
            "adapter_activation_report_path": _path_if_exists(root / "adapter_activation_report.json"),
            "hpo_budget_contract_path": _path_if_exists(root / "hpo_budget_contract.json"),
            "architecture_search_space_path": _path_if_exists(root / "architecture_search_space.json"),
            "trial_ledger_path": _path_if_exists(root / "trial_ledger.jsonl"),
            "early_stopping_report_path": _path_if_exists(root / "early_stopping_report.json"),
            "search_loop_scorecard_path": _path_if_exists(root / "search_loop_scorecard.json"),
            "warm_start_transfer_report_path": _path_if_exists(root / "warm_start_transfer_report.json"),
            "threshold_tuning_report_path": _path_if_exists(root / "threshold_tuning_report.json"),
            "calibration_strategy_report_path": _path_if_exists(root / "calibration_strategy_report.json"),
            "operating_point_contract_path": _path_if_exists(root / "operating_point_contract.json"),
            "threshold_search_report_path": _path_if_exists(root / "threshold_search_report.json"),
            "decision_cost_profile_path": _path_if_exists(root / "decision_cost_profile.json"),
            "review_budget_optimization_report_path": _path_if_exists(root / "review_budget_optimization_report.json"),
            "abstention_policy_report_path": _path_if_exists(root / "abstention_policy_report.json"),
            "trajectory_constraint_report_path": _path_if_exists(root / "trajectory_constraint_report.json"),
            "feasible_region_map_path": _path_if_exists(root / "feasible_region_map.json"),
            "extrapolation_risk_report_path": _path_if_exists(root / "extrapolation_risk_report.json"),
            "decision_constraint_report_path": _path_if_exists(root / "decision_constraint_report.json"),
            "action_boundary_report_path": _path_if_exists(root / "action_boundary_report.json"),
            "deployability_assessment_path": _path_if_exists(root / "deployability_assessment.json"),
            "review_gate_state_path": _path_if_exists(root / "review_gate_state.json"),
            "constraint_override_request_path": _path_if_exists(root / "constraint_override_request.json"),
            "counterfactual_region_report_path": _path_if_exists(root / "counterfactual_region_report.json"),
            "benchmark_gap_report_path": _path_if_exists(root / "benchmark_gap_report.json"),
            "external_challenger_manifest_path": _path_if_exists(root / "external_challenger_manifest.json"),
            "external_challenger_evaluation_path": _path_if_exists(root / "external_challenger_evaluation.json"),
            "incumbent_parity_report_path": _path_if_exists(root / "incumbent_parity_report.json"),
            "beat_target_contract_path": _path_if_exists(root / "beat_target_contract.json"),
            "paper_benchmark_manifest_path": _path_if_exists(root / "paper_benchmark_manifest.json"),
            "paper_benchmark_table_path": _path_if_exists(root / "paper_benchmark_table.json"),
            "benchmark_ablation_matrix_path": _path_if_exists(root / "benchmark_ablation_matrix.json"),
            "rerun_variance_report_path": _path_if_exists(root / "rerun_variance_report.json"),
            "benchmark_claims_report_path": _path_if_exists(root / "benchmark_claims_report.json"),
            "benchmark_truth_audit_path": _path_if_exists(root / "benchmark_truth_audit.json"),
            "paper_claim_guard_report_path": _path_if_exists(root / "paper_claim_guard_report.json"),
            "benchmark_release_gate_path": _path_if_exists(root / "benchmark_release_gate.json"),
            "dataset_leakage_audit_path": _path_if_exists(root / "dataset_leakage_audit.json"),
            "temporal_benchmark_recovery_report_path": _path_if_exists(root / "temporal_benchmark_recovery_report.json"),
            "benchmark_pack_partition_path": _path_if_exists(root / "benchmark_pack_partition.json"),
            "holdout_claim_policy_path": _path_if_exists(root / "holdout_claim_policy.json"),
            "benchmark_generalization_audit_path": _path_if_exists(root / "benchmark_generalization_audit.json"),
            "aml_benchmark_manifest_path": _path_if_exists(root / "aml_benchmark_manifest.json"),
            "aml_holdout_claim_report_path": _path_if_exists(root / "aml_holdout_claim_report.json"),
            "aml_demo_scorecard_path": _path_if_exists(root / "aml_demo_scorecard.json"),
            "aml_public_claim_guard_path": _path_if_exists(root / "aml_public_claim_guard.json"),
            "aml_failure_report_path": _path_if_exists(root / "aml_failure_report.json"),
            "shadow_trial_manifest_path": _path_if_exists(root / "shadow_trial_manifest.json"),
            "shadow_trial_scorecard_path": _path_if_exists(root / "shadow_trial_scorecard.json"),
            "candidate_quarantine_path": _path_if_exists(root / "candidate_quarantine.json"),
            "promotion_readiness_report_path": _path_if_exists(root / "promotion_readiness_report.json"),
            "decision_world_model_path": _path_if_exists(root / "decision_world_model.json"),
            "controller_policy_path": _path_if_exists(root / "controller_policy.json"),
            "value_of_more_data_report_path": _path_if_exists(root / "value_of_more_data_report.json"),
            "method_compiler_report_path": _path_if_exists(root / "method_compiler_report.json"),
            "method_import_report_path": _path_if_exists(root / "method_import_report.json"),
            "architecture_candidate_registry_path": _path_if_exists(root / "architecture_candidate_registry.json"),
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
            "trace_identity_conformance_path": _path_if_exists(root / "trace_identity_conformance.json"),
            "eval_surface_parity_report_path": _path_if_exists(root / "eval_surface_parity_report.json"),
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
            "artifact_dependency_graph_path": _path_if_exists(root / "artifact_dependency_graph.json"),
            "freshness_contract_path": _path_if_exists(root / "freshness_contract.json"),
            "recompute_plan_path": _path_if_exists(root / "recompute_plan.json"),
            "materialization_cache_index_path": _path_if_exists(root / "materialization_cache_index.json"),
            "invalidation_report_path": _path_if_exists(root / "invalidation_report.json"),
            "event_schema_path": _path_if_exists(root / "event_schema.json"),
            "event_subscription_registry_path": _path_if_exists(root / "event_subscription_registry.json"),
            "hook_registry_path": _path_if_exists(root / "hook_registry.json"),
            "hook_dispatch_report_path": _path_if_exists(root / "hook_dispatch_report.json"),
            "permission_mode_path": _path_if_exists(root / "permission_mode.json"),
            "tool_permission_matrix_path": _path_if_exists(root / "tool_permission_matrix.json"),
            "approval_policy_report_path": _path_if_exists(root / "approval_policy_report.json"),
            "permission_decision_log_path": _path_if_exists(root / "permission_decision_log.jsonl"),
            "session_capability_contract_path": _path_if_exists(root / "session_capability_contract.json"),
            "daemon_state_path": _path_if_exists(root / "daemon_state.json"),
            "background_job_registry_path": _path_if_exists(root / "background_job_registry.json"),
            "background_checkpoint_path": _path_if_exists(root / "background_checkpoint.json"),
            "resume_session_manifest_path": _path_if_exists(root / "resume_session_manifest.json"),
            "background_approval_queue_path": _path_if_exists(root / "background_approval_queue.json"),
            "memory_maintenance_queue_path": _path_if_exists(root / "memory_maintenance_queue.json"),
            "memory_maintenance_report_path": _path_if_exists(root / "memory_maintenance_report.json"),
            "search_resume_plan_path": _path_if_exists(root / "search_resume_plan.json"),
            "stale_job_report_path": _path_if_exists(root / "stale_job_report.json"),
            "background_job_log_path": _path_if_exists(root / "background_job_log.jsonl"),
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
    aml = dict(summary.get("aml", {}))
    aml_graph = dict(summary.get("aml_graph", {}))
    casework = dict(summary.get("casework", {}))
    stream_risk = dict(summary.get("stream_risk", {}))
    aml_proof = dict(summary.get("aml_proof", {}))
    decision_lab = dict(summary.get("decision_lab", {}))
    dojo = dict(summary.get("dojo", {}))
    pulse = dict(summary.get("pulse", {}))
    trace = dict(summary.get("trace", {}))
    evals = dict(summary.get("evals", {}))
    search = dict(summary.get("search", {}))
    daemon = dict(summary.get("daemon", {}))
    handoff = dict(summary.get("handoff", {}))
    learnings = dict(summary.get("learnings", {}))
    workspace = dict(summary.get("workspace", {}))
    result_contract = dict(summary.get("result_contract", {}))
    iteration = dict(summary.get("iteration", {}))
    feasibility = dict(summary.get("feasibility", {}))
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
                f"- Claim gate: `{benchmark.get('claim_gate_status') or 'unknown'}`",
                f"- Safe to cite publicly: `{benchmark.get('safe_to_cite_publicly')}`",
                f"- Demo safe: `{benchmark.get('demo_safe')}`",
                f"- Incumbent: `{benchmark.get('incumbent_name') or 'none'}`",
                f"- Incumbent parity: `{benchmark.get('incumbent_parity_status') or 'unknown'}`",
                f"- Beat-target state: `{benchmark.get('beat_target_state') or 'unknown'}`",
            ]
        )
        if benchmark.get("blocked_reason_count"):
            lines.append(f"- Claim-blocking reasons: `{benchmark.get('blocked_reason_count')}`")
    if aml and (aml.get("aml_active") is True or _clean_text(aml.get("status")) == "active"):
        lines.extend(
            [
                "",
                "## Relaytic-AML",
                f"- Status: `{aml.get('status') or 'unknown'}`",
                f"- AML active: `{aml.get('aml_active')}`",
                f"- Domain focus: `{aml.get('domain_focus') or 'unknown'}`",
                f"- Target level: `{aml.get('target_level') or 'unknown'}`",
                f"- Business goal: `{aml.get('business_goal') or 'unknown'}`",
                f"- Review budget relevant: `{aml.get('review_budget_relevant')}`",
                f"- Decision objective: `{aml.get('decision_objective') or 'unknown'}`",
                f"- Recommended next action: `{aml.get('recommended_next_action') or 'none'}`",
                f"- Claim scope: `{aml.get('claim_scope') or 'unknown'}`",
            ]
        )
    if aml_graph and any(value not in (None, 0, False, "", []) for value in aml_graph.values()):
        lines.extend(
            [
                "",
                "## AML Graph",
                f"- Status: `{aml_graph.get('status') or 'unknown'}`",
                f"- Nodes: `{aml_graph.get('node_count', 0)}`",
                f"- Edges: `{aml_graph.get('edge_count', 0)}`",
                f"- Components: `{aml_graph.get('component_count', 0)}`",
                f"- Top entity: `{aml_graph.get('top_entity') or 'none'}`",
                f"- Typology hits: `{aml_graph.get('typology_hit_count', 0)}`",
                f"- Focal entity: `{aml_graph.get('focal_entity') or 'none'}`",
                f"- Shadow winner: `{aml_graph.get('shadow_winner') or 'unknown'}`",
            ]
        )
    if casework and any(value not in (None, 0, False, "", []) for value in casework.values()):
        lines.extend(
            [
                "",
                "## AML Casework",
                f"- Status: `{casework.get('status') or 'unknown'}`",
                f"- Queue count: `{casework.get('queue_count', 0)}`",
                f"- Review capacity: `{casework.get('review_capacity_cases', 0)}`",
                f"- Review budget fraction: `{casework.get('review_budget_fraction')}`",
                f"- Decision objective: `{casework.get('decision_objective') or 'unknown'}`",
                f"- Top case: `{casework.get('top_case_id') or 'none'}`",
                f"- Top entity: `{casework.get('top_case_entity') or 'none'}`",
                f"- Top action: `{casework.get('top_case_action') or 'unknown'}`",
                f"- Estimated review hours: `{casework.get('estimated_review_hours')}`",
            ]
        )
    if stream_risk and any(value not in (None, 0, False, "", []) for value in stream_risk.values()):
        lines.extend(
            [
                "",
                "## AML Stream Risk",
                f"- Status: `{stream_risk.get('status') or 'unknown'}`",
                f"- Stream mode: `{stream_risk.get('stream_mode') or 'unknown'}`",
                f"- Timestamp column: `{stream_risk.get('timestamp_column') or 'none'}`",
                f"- Weak-label risk: `{stream_risk.get('weak_label_risk_level') or 'unknown'}`",
                f"- Delayed confirmation likely: `{stream_risk.get('delayed_confirmation_likely')}`",
                f"- Rolling windows: `{stream_risk.get('rolling_window_count', 0)}`",
                f"- Drift score: `{stream_risk.get('drift_score')}`",
                f"- Trigger action: `{stream_risk.get('trigger_action') or 'none'}`",
                f"- Benchmark safe: `{stream_risk.get('benchmark_safe')}`",
            ]
        )
    if aml_proof and any(value not in (None, 0, False, "", []) for value in aml_proof.values()):
        lines.extend(
            [
                "",
                "## AML Proof Pack",
                f"- Status: `{aml_proof.get('status') or 'unknown'}`",
                f"- Dataset family: `{aml_proof.get('dataset_family') or 'unknown'}`",
                f"- Benchmark track: `{aml_proof.get('benchmark_track') or 'unknown'}`",
                f"- Current partition: `{aml_proof.get('current_partition') or 'unknown'}`",
                f"- Supporting public claim allowed: `{aml_proof.get('supporting_public_claim_allowed')}`",
                f"- Paper primary claim allowed: `{aml_proof.get('paper_primary_claim_allowed')}`",
                f"- Broader flagship claim allowed: `{aml_proof.get('broader_flagship_claim_allowed')}`",
                f"- Cross-track coverage met: `{aml_proof.get('required_track_coverage_met')}`",
                f"- Current demo story: `{aml_proof.get('current_run_story') or 'none'}`",
                f"- Ready demo count: `{aml_proof.get('ready_demo_count', 0)}`",
                f"- Demo safe: `{aml_proof.get('demo_safe')}`",
                f"- Primary remaining gap: `{aml_proof.get('primary_failure_kind') or 'none'}`",
                f"- Recommended next step: `{aml_proof.get('recommended_next_step') or 'none'}`",
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
    if feasibility and any(value not in (None, 0, False, "", []) for value in feasibility.values()):
        lines.extend(
            [
                "",
                "## Feasibility",
                f"- Trajectory status: `{feasibility.get('trajectory_status') or 'unknown'}`",
                f"- Region posture: `{feasibility.get('region_posture') or 'unknown'}`",
                f"- Extrapolation risk: `{feasibility.get('risk_band') or 'unknown'}`",
                f"- OOD fraction: `{float(feasibility.get('observed_ood_fraction', 0.0) or 0.0):.4f}`",
                f"- Recommended direction: `{feasibility.get('recommended_direction') or 'unknown'}`",
                f"- Selected action: `{feasibility.get('selected_action') or 'unknown'}`",
                f"- Constraint kind: `{feasibility.get('primary_constraint_kind') or 'none'}`",
                f"- Deployability: `{feasibility.get('deployability') or 'unknown'}`",
                f"- Gate open: `{feasibility.get('gate_open')}`",
                f"- Override required: `{feasibility.get('override_required')}`",
            ]
        )
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
                f"- Trace identity: `{evals.get('trace_identity_status') or 'unknown'}`",
                f"- Surface parity: `{evals.get('surface_parity_status') or 'unknown'}`",
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
    if daemon and any(value not in (None, 0, False, "", []) for value in daemon.values()):
        lines.extend(
            [
                "",
                "## Background Daemon",
                f"- Status: `{daemon.get('status') or 'unknown'}`",
                f"- Background execution enabled: `{daemon.get('background_execution_enabled')}`",
                f"- Jobs: `{daemon.get('job_count', 0)}`",
                f"- Pending approvals: `{daemon.get('pending_approval_count', 0)}`",
                f"- Resumable jobs: `{daemon.get('resumable_job_count', 0)}`",
                f"- Checkpoints: `{daemon.get('checkpoint_count', 0)}`",
                f"- Memory tasks: `{daemon.get('memory_task_count', 0)}`",
                f"- Memory maintenance executed: `{daemon.get('memory_maintenance_executed')}`",
                f"- Stale jobs: `{daemon.get('stale_job_count', 0)}`",
            ]
        )
        if daemon.get("next_resume_step"):
            lines.append(f"- Next resume step: `{daemon.get('next_resume_step')}`")
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
                f"- Fresh stages: `{runtime.get('fresh_stage_count', 0)}`, recompute needed: `{runtime.get('recompute_stage_count', 0)}`",
            ]
        )
        if runtime.get("last_event_type"):
            lines.append(f"- Last event: `{runtime.get('last_event_type')}` via `{runtime.get('last_surface') or 'unknown'}`")
        if runtime.get("semantic_rowless_default") is not None:
            lines.append(f"- Rowless semantic default: `{runtime.get('semantic_rowless_default')}`")
        if runtime.get("next_recompute_stage"):
            lines.append(f"- Next recompute target: `{runtime.get('next_recompute_stage')}`")
    event_bus = dict(summary.get("event_bus", {}))
    if event_bus and any(value is not None for value in event_bus.values()):
        lines.extend(
            [
                "",
                "## Event Bus",
                f"- Event types: `{event_bus.get('event_type_count', 0)}`",
                f"- Subscribers: `{event_bus.get('subscription_count', 0)}`",
                f"- Hook registry entries: `{event_bus.get('hook_registry_count', 0)}`",
                f"- Projected dispatches: `{event_bus.get('dispatch_count', 0)}`",
            ]
        )
        if event_bus.get("source_of_truth_preserved") is not None:
            lines.append(f"- Source of truth preserved: `{event_bus.get('source_of_truth_preserved')}`")
    permissions = dict(summary.get("permissions", {}))
    if permissions and any(value is not None for value in permissions.values()):
        lines.extend(
            [
                "",
                "## Permissions",
                f"- Current mode: `{permissions.get('current_mode') or 'unknown'}`",
                f"- Pending approvals: `{permissions.get('pending_approval_count', 0)}`",
                f"- Approval-gated actions: `{permissions.get('approval_gated_action_count', 0)}`",
                f"- Blocked actions: `{permissions.get('blocked_action_count', 0)}`",
            ]
        )
        if permissions.get("mode_source"):
            lines.append(f"- Mode source: `{permissions.get('mode_source')}`")
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
    from relaytic.analytics import (
        read_task_contract_artifacts,
        sync_architecture_routing_artifacts,
        sync_task_contract_artifacts,
        sync_temporal_engine_artifacts,
    )
    from relaytic.aml import sync_aml_graph_artifacts
    from relaytic.casework import sync_casework_artifacts
    from relaytic.stream_risk import sync_stream_risk_artifacts
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
    sync_task_contract_artifacts(
        root,
        data_path=data_path or _path_if_exists(root / "data.csv") or _clean_text(dict(base_summary.get("data", {})).get("data_path")),
        mandate_bundle=_read_bundle(root, {"run_brief": "run_brief.json"}),
        context_bundle=_read_bundle(root, {"task_brief": "task_brief.json"}),
        investigation_bundle=_read_bundle(root, {"dataset_profile": "dataset_profile.json"}),
        planning_bundle=_read_bundle(root, {"plan": "plan.json"}),
        benchmark_bundle=_read_bundle(
            root,
            {
                "benchmark_parity_report": "benchmark_parity_report.json",
                "reference_approach_matrix": "reference_approach_matrix.json",
            },
        ),
        decision_bundle=_read_bundle(
            root,
            {
                "decision_constraint_report": "decision_constraint_report.json",
                "deployability_assessment": "deployability_assessment.json",
                "review_gate_state": "review_gate_state.json",
            },
        ),
    )
    sync_aml_graph_artifacts(
        root,
        data_path=data_path or _path_if_exists(root / "data.csv") or _clean_text(dict(base_summary.get("data", {})).get("data_path")),
        context_bundle=_read_bundle(root, {"domain_brief": "domain_brief.json", "task_brief": "task_brief.json"}),
        task_contract_bundle=read_task_contract_artifacts(root),
    )
    sync_architecture_routing_artifacts(
        root,
        investigation_bundle=_read_bundle(
            root,
            {
                "dataset_profile": "dataset_profile.json",
                "optimization_profile": "optimization_profile.json",
            },
        ),
        planning_bundle=_read_bundle(root, {"plan": "plan.json"}),
        route_prior_context=_read_bundle(root, {"route_prior_context": "route_prior_context.json"}).get("route_prior_context", {}),
        benchmark_bundle=_read_bundle(root, {"benchmark_parity_report": "benchmark_parity_report.json"}),
    )
    sync_temporal_engine_artifacts(
        root,
        data_path=data_path or _path_if_exists(root / "data.csv") or _clean_text(dict(base_summary.get("data", {})).get("data_path")),
        investigation_bundle=_read_bundle(root, {"dataset_profile": "dataset_profile.json"}),
        planning_bundle=_read_bundle(root, {"plan": "plan.json"}),
        benchmark_bundle=_read_bundle(
            root,
            {
                "reference_approach_matrix": "reference_approach_matrix.json",
                "benchmark_ablation_matrix": "benchmark_ablation_matrix.json",
                "shadow_trial_scorecard": "shadow_trial_scorecard.json",
            },
        ),
        architecture_bundle=_read_bundle(
            root,
            {
                "architecture_router_report": "architecture_router_report.json",
                "architecture_ablation_report": "architecture_ablation_report.json",
            },
        ),
        task_contract_bundle=read_task_contract_artifacts(root),
    )
    sync_casework_artifacts(
        root,
        context_bundle=_read_bundle(root, {"domain_brief": "domain_brief.json", "task_brief": "task_brief.json"}),
        task_contract_bundle=read_task_contract_artifacts(root),
        aml_graph_bundle=_read_bundle(
            root,
            {
                "entity_graph_profile": "entity_graph_profile.json",
                "counterparty_network_report": "counterparty_network_report.json",
                "typology_detection_report": "typology_detection_report.json",
                "subgraph_risk_report": "subgraph_risk_report.json",
                "entity_case_expansion": "entity_case_expansion.json",
            },
        ),
        operating_point_bundle=_read_bundle(
            root,
            {
                "operating_point_contract": "operating_point_contract.json",
                "review_budget_optimization_report": "review_budget_optimization_report.json",
            },
        ),
    )
    sync_stream_risk_artifacts(
        root,
        data_path=data_path or _path_if_exists(root / "data.csv") or _clean_text(dict(base_summary.get("data", {})).get("data_path")),
        context_bundle=_read_bundle(root, {"domain_brief": "domain_brief.json", "task_brief": "task_brief.json"}),
        task_contract_bundle=read_task_contract_artifacts(root),
        temporal_bundle=_read_bundle(
            root,
            {
                "temporal_structure_report": "temporal_structure_report.json",
                "rolling_cv_plan": "rolling_cv_plan.json",
            },
        ),
        operating_point_bundle=_read_bundle(
            root,
            {
                "operating_point_contract": "operating_point_contract.json",
                "review_budget_optimization_report": "review_budget_optimization_report.json",
            },
        ),
        lifecycle_bundle=_read_bundle(
            root,
            {
                "champion_vs_candidate": "champion_vs_candidate.json",
                "recalibration_decision": "recalibration_decision.json",
                "retrain_decision": "retrain_decision.json",
            },
        ),
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
    from relaytic.runtime import sync_materialization_runtime_artifacts

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
    sync_materialization_runtime_artifacts(root)
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


def _normalize_benchmark_parity_status(value: str | None) -> str | None:
    return normalize_benchmark_parity_status(value)


def _infer_benchmark_deploy_split(*, parity_status: str | None, deployment_readiness: str | None) -> bool:
    readiness = _clean_text(deployment_readiness)
    if not benchmark_is_reference_competitive(parity_status, include_near=True):
        return False
    return readiness not in {None, "ready", "deploy_ready", "ready_now"}


def _benchmark_vs_deploy_summary(
    *,
    summary: str | None,
    parity_status: str | None,
    deployment_readiness: str | None,
) -> str | None:
    text = _clean_text(summary)
    if not _infer_benchmark_deploy_split(
        parity_status=parity_status,
        deployment_readiness=deployment_readiness,
    ):
        return text
    reminder = "Offline benchmark wins do not masquerade as deploy-ready decisions."
    if not text:
        return reminder
    if "deploy-ready" in text:
        return text
    return f"{text} {reminder}"


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
    daemon_bundle: dict[str, Any],
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
    if daemon_bundle:
        return "daemon_reviewed"
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


def _resolve_next_step_resolution(
    *,
    decision_constraint_report: dict[str, Any],
    review_gate_state: dict[str, Any],
    deployability_assessment: dict[str, Any],
    feedback_effect_report: dict[str, Any],
    decision_usefulness_report: dict[str, Any],
    value_of_more_data_report: dict[str, Any],
    decision_policy_update_suggestions: dict[str, Any],
    route_prior_updates: dict[str, Any],
    policy_update_suggestions: dict[str, Any],
    outcome_observation_report: dict[str, Any],
    controller_policy: dict[str, Any],
    lifecycle_bundle: dict[str, Any],
    completion_decision: dict[str, Any],
    belief_update: dict[str, Any],
    marginal_value: dict[str, Any],
) -> dict[str, Any]:
    feedback_action = _clean_text(feedback_effect_report.get("primary_recommended_action"))
    if feedback_action and int(feedback_effect_report.get("accepted_feedback_count", 0) or 0) > 0:
        return {
            "recommended_action": feedback_action,
            "rationale": _clean_text(feedback_effect_report.get("summary")) or _clean_text(marginal_value.get("rationale")),
            "source": "feedback_effect_report",
        }
    latest_candidates = [
        {
            "source": "feedback_effect_report",
            "generated_at": _parse_generated_at(feedback_effect_report),
            "action": feedback_action,
            "rationale": _clean_text(feedback_effect_report.get("summary")),
        },
        {
            "source": "decision_policy_update_suggestions",
            "generated_at": _parse_generated_at(decision_policy_update_suggestions),
            "action": _clean_text(decision_policy_update_suggestions.get("primary_recommended_action")),
            "rationale": _clean_text(decision_policy_update_suggestions.get("summary")),
        },
        {
            "source": "decision_constraint_report",
            "generated_at": _parse_generated_at(decision_constraint_report),
            "action": _clean_text(decision_constraint_report.get("feasible_selected_action")),
            "rationale": _clean_text(
                decision_constraint_report.get("summary")
                or review_gate_state.get("summary")
                or deployability_assessment.get("summary")
            ),
        },
        {
            "source": "controller_policy",
            "generated_at": _parse_generated_at(controller_policy),
            "action": (
                _clean_text(controller_policy.get("selected_next_action"))
                if _clean_text(value_of_more_data_report.get("selected_strategy")) not in {None, "hold_current_course"}
                else None
            ),
            "rationale": _clean_text(
                decision_usefulness_report.get("summary") or value_of_more_data_report.get("summary")
            ),
        },
        {
            "source": "completion_decision",
            "generated_at": _parse_generated_at(completion_decision),
            "action": _clean_text(completion_decision.get("action")),
            "rationale": _clean_text(completion_decision.get("summary")),
        },
        {
            "source": "belief_update",
            "generated_at": _parse_generated_at(belief_update),
            "action": _clean_text(belief_update.get("recommended_action")),
            "rationale": _clean_text(belief_update.get("summary")),
        },
    ]
    latest_candidates = [item for item in latest_candidates if item["action"]]
    if latest_candidates:
        with_timestamp = [item for item in latest_candidates if item["generated_at"] is not None]
        if with_timestamp:
            latest_candidates = with_timestamp
        selected = max(
            enumerate(latest_candidates),
            key=lambda pair: (
                pair[1]["generated_at"] or datetime.min.replace(tzinfo=timezone.utc),
                -pair[0],
            ),
        )[1]
        return {
            "recommended_action": selected["action"],
            "rationale": selected["rationale"] or _clean_text(marginal_value.get("rationale")),
            "source": selected["source"],
        }
    return {
        "recommended_action": _lifecycle_primary_action(lifecycle_bundle)
        or _clean_text(completion_decision.get("action"))
        or _clean_text(belief_update.get("recommended_action")),
        "rationale": _clean_text(
            decision_constraint_report.get("summary")
            or review_gate_state.get("summary")
            or deployability_assessment.get("summary")
            or feedback_effect_report.get("summary")
            or decision_usefulness_report.get("summary")
            or value_of_more_data_report.get("summary")
            or decision_policy_update_suggestions.get("summary")
            or route_prior_updates.get("summary")
            or policy_update_suggestions.get("summary")
            or outcome_observation_report.get("summary")
            or completion_decision.get("summary")
            or belief_update.get("summary")
            or marginal_value.get("rationale")
        ),
        "source": "fallback",
    }


def _parse_generated_at(payload: dict[str, Any]) -> datetime | None:
    value = _clean_text(payload.get("generated_at"))
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed


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
