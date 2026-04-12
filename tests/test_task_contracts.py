from __future__ import annotations

import pandas as pd

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


def test_task_contract_builds_canonical_optimization_objective_contract() -> None:
    artifacts = build_task_contract_artifacts(
        mandate_bundle={"run_brief": {"objective": "Benchmark this classifier against strong references."}},
        context_bundle={"task_brief": {"target_column": "diagnosis_flag", "problem_statement": "Predict diagnosis_flag."}},
        investigation_bundle={"dataset_profile": {"row_count": 569, "column_count": 31, "data_mode": "steady_state"}},
        planning_bundle={
            "plan": {
                "target_column": "diagnosis_flag",
                "task_type": "binary_classification",
                "data_mode": "steady_state",
                "primary_metric": "roc_auc",
                "split_strategy": "stratified_deterministic_modulo_70_15_15",
                "builder_handoff": {"selection_metric": "log_loss", "threshold_policy": "favor_recall"},
                "execution_summary": {
                    "selected_metrics": {
                        "validation": {"log_loss": 0.18, "roc_auc": 0.96, "pr_auc": 0.94},
                        "test": {"log_loss": 0.19, "roc_auc": 0.95, "pr_auc": 0.93},
                    }
                },
                "task_profile": {
                    "target_signal": "diagnosis_flag",
                    "task_type": "binary_classification",
                    "task_family": "classification",
                    "data_mode": "steady_state",
                    "target_semantics": "binary_labeled_class",
                    "problem_posture": "standard_classification",
                    "rare_event_supervised": False,
                    "override_applied": False,
                    "row_count": 569,
                    "class_count": 2,
                    "class_balance": {"0": 212, "1": 357},
                    "minority_class_fraction": 212 / 569,
                    "positive_class_label": "1",
                    "recommended_split_strategy": "stratified_deterministic_modulo_70_15_15",
                    "rationale": "Detected explicit labeled diagnosis outcomes.",
                },
            }
        },
    )

    objective = artifacts["optimization_objective_contract"]
    alignment = artifacts["objective_alignment_report"]
    assert objective["family_selection_metric"] == "log_loss"
    assert objective["benchmark_comparison_metric"] == "pr_auc"
    assert objective["deployment_decision_metric"] == "roc_auc"
    assert objective["explicit_metric_split"] is True
    assert alignment["status"] == "ok"
    assert "selects families on `log_loss`" in alignment["summary"]


def test_task_contract_blocks_temporal_benchmark_truth_when_future_folds_lose_positives(tmp_path) -> None:
    data_path = tmp_path / "temporal_blocked.csv"
    frame = pd.DataFrame(
        {
            "timestamp": pd.date_range("2026-01-01 00:00:00", periods=60, freq="5min"),
            "sensor_a": [float(index % 7) for index in range(60)],
            "sensor_b": [float((index * 3) % 11) for index in range(60)],
            "occupancy_flag": [1 if index < 12 else 0 for index in range(60)],
        }
    )
    frame["timestamp"] = frame["timestamp"].dt.strftime("%Y-%m-%d %H:%M:%S")
    frame.to_csv(data_path, index=False)

    artifacts = build_task_contract_artifacts(
        data_path=data_path,
        mandate_bundle={"run_brief": {"objective": "Benchmark this temporal occupancy classifier."}},
        context_bundle={"task_brief": {"target_column": "occupancy_flag", "problem_statement": "Predict occupancy_flag over time."}},
        investigation_bundle={"dataset_profile": {"row_count": 60, "column_count": 4, "data_mode": "time_series", "timestamp_column": "timestamp"}},
        planning_bundle={
            "plan": {
                "target_column": "occupancy_flag",
                "task_type": "binary_classification",
                "data_mode": "time_series",
                "timestamp_column": "timestamp",
                "primary_metric": "pr_auc",
                "split_strategy": "blocked_time_order_70_15_15",
                "builder_handoff": {"selection_metric": "pr_auc", "threshold_policy": "favor_pr_auc"},
                "execution_summary": {
                    "selected_metrics": {
                        "validation": {"pr_auc": 0.2, "log_loss": 0.7},
                        "test": {"pr_auc": 0.1, "log_loss": 0.8},
                    }
                },
                "task_profile": {
                    "target_signal": "occupancy_flag",
                    "task_type": "binary_classification",
                    "task_family": "classification",
                    "data_mode": "time_series",
                    "target_semantics": "rare_event_supervised_label",
                    "problem_posture": "rare_event_supervised",
                    "rare_event_supervised": True,
                    "override_applied": False,
                    "row_count": 60,
                    "class_count": 2,
                    "class_balance": {"0": 48, "1": 12},
                    "minority_class_fraction": 0.2,
                    "positive_class_label": "1",
                    "recommended_split_strategy": "blocked_time_order_70_15_15",
                    "rationale": "Temporal occupancy target with explicit labels.",
                },
            }
        },
    )

    split_report = artifacts["split_diagnostics_report"]
    temporal_health = artifacts["temporal_fold_health"]
    precheck = artifacts["benchmark_truth_precheck"]
    assert split_report["status"] == "blocked"
    assert split_report["zero_positive_validation"] is True
    assert split_report["zero_positive_test"] is True
    assert temporal_health["status"] == "blocked"
    assert precheck["safe_to_rank"] is False


def test_task_contract_audit_fails_when_benchmark_metric_is_not_materialized() -> None:
    artifacts = build_task_contract_artifacts(
        mandate_bundle={"run_brief": {"objective": "Benchmark the temporal regression route honestly."}},
        context_bundle={"task_brief": {"target_column": "energy_target", "problem_statement": "Predict energy_target."}},
        investigation_bundle={"dataset_profile": {"row_count": 512, "column_count": 14, "data_mode": "time_series", "timestamp_column": "timestamp"}},
        planning_bundle={
            "plan": {
                "target_column": "energy_target",
                "task_type": "regression",
                "data_mode": "time_series",
                "timestamp_column": "timestamp",
                "primary_metric": "mae",
                "split_strategy": "blocked_time_order_70_15_15",
                "builder_handoff": {"selection_metric": "stability_adjusted_mae", "threshold_policy": "auto"},
                "execution_summary": {
                    "selected_metrics": {
                        "validation": {"mae": 0.42, "rmse": 0.61, "r2": 0.74},
                        "test": {"mae": 0.45, "rmse": 0.63, "r2": 0.72},
                    }
                },
                "task_profile": {
                    "target_signal": "energy_target",
                    "task_type": "regression",
                    "task_family": "regression",
                    "data_mode": "time_series",
                    "target_semantics": "continuous_signal",
                    "problem_posture": "regression",
                    "rare_event_supervised": False,
                    "override_applied": False,
                    "row_count": 512,
                    "class_count": 0,
                    "class_balance": {},
                    "minority_class_fraction": None,
                    "positive_class_label": None,
                    "recommended_split_strategy": "blocked_time_order_70_15_15",
                    "rationale": "Time-aware continuous target.",
                },
            }
        },
    )

    audit = artifacts["metric_materialization_audit"]
    precheck = artifacts["benchmark_truth_precheck"]
    assert audit["status"] == "fail"
    assert "stability_adjusted_mae" in audit["missing_metrics"]
    assert precheck["status"] == "blocked"
    assert precheck["safe_to_rank"] is False
