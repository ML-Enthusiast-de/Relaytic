from __future__ import annotations

from relaytic.analytics import build_task_contract_artifacts


def test_task_contract_marks_labeled_anomaly_like_target_as_supervised() -> None:
    artifacts = build_task_contract_artifacts(
        mandate_bundle={"run_brief": {"objective": "Predict anomaly_flag from the sensor columns."}},
        context_bundle={"task_brief": {"target_column": "anomaly_flag", "problem_statement": "Predict anomaly_flag."}},
        investigation_bundle={"dataset_profile": {"row_count": 120, "column_count": 8, "data_mode": "steady_state"}},
        planning_bundle={
            "plan": {
                "target_column": "anomaly_flag",
                "task_type": "binary_classification",
                "data_mode": "steady_state",
                "primary_metric": "pr_auc",
                "split_strategy": "stratified_deterministic_modulo_70_15_15",
                "builder_handoff": {"selection_metric": "pr_auc", "threshold_policy": "favor_pr_auc"},
                "task_profile": {
                    "target_signal": "anomaly_flag",
                    "task_type": "binary_classification",
                    "task_family": "classification",
                    "data_mode": "steady_state",
                    "target_semantics": "rare_event_supervised_label",
                    "problem_posture": "rare_event_supervised",
                    "rare_event_supervised": True,
                    "override_applied": False,
                    "row_count": 120,
                    "class_count": 2,
                    "class_balance": {"0": 110, "1": 10},
                    "minority_class_fraction": 10 / 120,
                    "positive_class_label": "1",
                    "recommended_split_strategy": "stratified_deterministic_modulo_70_15_15",
                    "rationale": "Detected explicit labeled rare-event states.",
                },
            }
        },
    )

    task_contract = artifacts["task_profile_contract"]
    assert task_contract["task_type"] == "binary_classification"
    assert task_contract["problem_posture"] == "rare_event_supervised"
    assert "True anomaly detection is reserved" in task_contract["why_not_anomaly_detection"]


def test_task_contract_separates_benchmark_competitiveness_from_deployment_readiness() -> None:
    artifacts = build_task_contract_artifacts(
        mandate_bundle={"run_brief": {"objective": "Benchmark this model against strong references."}},
        context_bundle={"task_brief": {"target_column": "default_flag", "problem_statement": "Predict default_flag."}},
        investigation_bundle={"dataset_profile": {"row_count": 5000, "column_count": 20, "data_mode": "steady_state"}},
        planning_bundle={
            "plan": {
                "target_column": "default_flag",
                "task_type": "binary_classification",
                "data_mode": "steady_state",
                "primary_metric": "pr_auc",
                "split_strategy": "stratified_deterministic_modulo_70_15_15",
                "builder_handoff": {"selection_metric": "pr_auc", "threshold_policy": "favor_pr_auc"},
                "task_profile": {
                    "target_signal": "default_flag",
                    "task_type": "binary_classification",
                    "task_family": "classification",
                    "data_mode": "steady_state",
                    "target_semantics": "rare_event_supervised_label",
                    "problem_posture": "rare_event_supervised",
                    "rare_event_supervised": True,
                    "override_applied": False,
                    "row_count": 5000,
                    "class_count": 2,
                    "class_balance": {"0": 3900, "1": 1100},
                    "minority_class_fraction": 0.22,
                    "positive_class_label": "1",
                    "recommended_split_strategy": "stratified_deterministic_modulo_70_15_15",
                    "rationale": "Detected labeled credit-default states.",
                },
            }
        },
        benchmark_bundle={"benchmark_parity_report": {"parity_status": "near_parity", "recommended_action": "hold_route"}},
        decision_bundle={
            "deployability_assessment": {"deployability": "conditional", "recommended_action": "hold_for_data_refresh"},
            "review_gate_state": {"gate_open": True},
            "decision_constraint_report": {"primary_constraint_kind": "data_freshness"},
        },
    )

    report = artifacts["benchmark_vs_deploy_report"]
    assert report["benchmark_status"] == "near_parity"
    assert report["deployment_readiness"] == "conditional"
    assert report["split_detected"] is True
    assert "offline benchmark wins do not masquerade as deploy-ready decisions" in report["summary"]
