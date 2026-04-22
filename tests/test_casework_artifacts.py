from __future__ import annotations

from pathlib import Path

import pandas as pd

from relaytic.aml import build_aml_graph_artifacts
from relaytic.analytics import build_task_contract_artifacts
from relaytic.casework import build_casework_artifacts


def _write_casework_dataset(path: Path) -> Path:
    rows = [
        {"source_account": "A1", "destination_account": "HUB1", "txn_amount": 12.0, "device_id": "dev-1", "suspicious_activity_flag": 1},
        {"source_account": "A2", "destination_account": "HUB1", "txn_amount": 14.0, "device_id": "dev-2", "suspicious_activity_flag": 1},
        {"source_account": "A3", "destination_account": "HUB1", "txn_amount": 11.0, "device_id": "dev-3", "suspicious_activity_flag": 1},
        {"source_account": "HUB1", "destination_account": "L1", "txn_amount": 55.0, "device_id": "dev-1", "suspicious_activity_flag": 1},
        {"source_account": "HUB1", "destination_account": "L2", "txn_amount": 48.0, "device_id": "dev-1", "suspicious_activity_flag": 1},
        {"source_account": "C1", "destination_account": "B1", "txn_amount": 31.0, "device_id": "dev-9", "suspicious_activity_flag": 0},
        {"source_account": "B1", "destination_account": "B2", "txn_amount": 28.0, "device_id": "dev-9", "suspicious_activity_flag": 1},
        {"source_account": "B2", "destination_account": "B3", "txn_amount": 26.0, "device_id": "dev-9", "suspicious_activity_flag": 1},
        {"source_account": "B3", "destination_account": "B4", "txn_amount": 25.0, "device_id": "dev-9", "suspicious_activity_flag": 1},
        {"source_account": "X1", "destination_account": "M1", "txn_amount": 80.0, "device_id": "shared-merchant", "suspicious_activity_flag": 0},
        {"source_account": "X2", "destination_account": "M1", "txn_amount": 82.0, "device_id": "shared-merchant", "suspicious_activity_flag": 0},
        {"source_account": "X3", "destination_account": "M1", "txn_amount": 81.0, "device_id": "shared-merchant", "suspicious_activity_flag": 1},
    ]
    pd.DataFrame(rows).to_csv(path, index=False)
    return path


def _casework_task_contract_bundle(data_path: Path) -> dict[str, dict]:
    return build_task_contract_artifacts(
        data_path=data_path,
        mandate_bundle={
            "run_brief": {
                "objective": "Do AML transaction monitoring, detect suspicious graph structure, and optimize the analyst review queue."
            }
        },
        context_bundle={
            "task_brief": {
                "target_column": "suspicious_activity_flag",
                "problem_statement": "Classify suspicious_activity_flag for AML analyst review prioritization.",
            },
            "domain_brief": {
                "summary": "Payment-fraud and financial-crime review workflow with structural risk and bounded analyst capacity.",
                "target_meaning": "Whether a transaction should be escalated into analyst review.",
            },
        },
        investigation_bundle={"dataset_profile": {"row_count": 12, "column_count": 5, "data_mode": "steady_state"}},
        planning_bundle={
            "plan": {
                "target_column": "suspicious_activity_flag",
                "task_type": "binary_classification",
                "data_mode": "steady_state",
                "primary_metric": "pr_auc",
                "split_strategy": "stratified_deterministic_modulo_70_15_15",
                "builder_handoff": {"selection_metric": "log_loss", "threshold_policy": "favor_pr_auc"},
                "task_profile": {
                    "target_signal": "suspicious_activity_flag",
                    "task_type": "binary_classification",
                    "task_family": "classification",
                    "data_mode": "steady_state",
                    "target_semantics": "rare_event_supervised_label",
                    "problem_posture": "rare_event_supervised",
                    "rare_event_supervised": True,
                    "override_applied": False,
                    "row_count": 12,
                    "class_count": 2,
                    "class_balance": {"0": 5, "1": 7},
                    "minority_class_fraction": 5 / 12,
                    "positive_class_label": "1",
                    "recommended_split_strategy": "stratified_deterministic_modulo_70_15_15",
                    "rationale": "Explicit suspicious-activity labels with AML review pressure.",
                },
            }
        },
    )


def test_build_casework_artifacts_materializes_review_queue_and_case_packet(tmp_path: Path) -> None:
    data_path = _write_casework_dataset(tmp_path / "aml_casework.csv")
    task_contract_bundle = _casework_task_contract_bundle(data_path)
    aml_graph_bundle = build_aml_graph_artifacts(
        data_path=data_path,
        context_bundle={
            "domain_brief": {
                "summary": "AML transaction monitoring with entity and counterparty reasoning."
            }
        },
        task_contract_bundle=task_contract_bundle,
    )

    artifacts = build_casework_artifacts(
        context_bundle={
            "domain_brief": {"summary": "AML analyst queue optimization."},
            "task_brief": {"target_column": "suspicious_activity_flag"},
        },
        task_contract_bundle=task_contract_bundle,
        aml_graph_bundle=aml_graph_bundle,
        operating_point_bundle={
            "operating_point_contract": {"selected_review_fraction": 0.2},
            "review_budget_optimization_report": {"selected_review_fraction": 0.2},
        },
    )

    policy = artifacts["alert_queue_policy"]
    rankings = artifacts["alert_queue_rankings"]
    scorecard = artifacts["analyst_review_scorecard"]
    case_packet = artifacts["case_packet"]
    sensitivity = artifacts["review_capacity_sensitivity"]

    assert policy["status"] == "active"
    assert rankings["status"] == "active"
    assert scorecard["status"] == "active"
    assert case_packet["status"] == "active"
    assert rankings["queue_count"] >= 2
    assert policy["review_capacity_cases"] >= 1
    assert rankings["ranking"][0]["entity_id"] == "HUB1"
    assert rankings["ranking"][0]["review_action"] == "review_now"
    assert case_packet["focal_entity"] == "HUB1"
    assert "smurfing" in case_packet["top_typologies"]
    assert case_packet["counterparty_edges"]
    assert case_packet["analyst_questions"]
    assert scorecard["estimated_review_hours"] > 0
    assert sensitivity["rows"]


def test_build_casework_artifacts_respects_review_budget_fraction(tmp_path: Path) -> None:
    data_path = _write_casework_dataset(tmp_path / "aml_casework_budget.csv")
    task_contract_bundle = _casework_task_contract_bundle(data_path)
    aml_graph_bundle = build_aml_graph_artifacts(
        data_path=data_path,
        context_bundle={},
        task_contract_bundle=task_contract_bundle,
    )

    low_budget = build_casework_artifacts(
        context_bundle={},
        task_contract_bundle=task_contract_bundle,
        aml_graph_bundle=aml_graph_bundle,
        operating_point_bundle={"operating_point_contract": {"selected_review_fraction": 0.1}},
    )
    high_budget = build_casework_artifacts(
        context_bundle={},
        task_contract_bundle=task_contract_bundle,
        aml_graph_bundle=aml_graph_bundle,
        operating_point_bundle={"operating_point_contract": {"selected_review_fraction": 0.3}},
    )

    assert low_budget["alert_queue_policy"]["review_capacity_cases"] < high_budget["alert_queue_policy"]["review_capacity_cases"]
    assert low_budget["analyst_review_scorecard"]["estimated_review_hours"] < high_budget["analyst_review_scorecard"]["estimated_review_hours"]
