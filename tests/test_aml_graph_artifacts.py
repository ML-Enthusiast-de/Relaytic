from __future__ import annotations

from pathlib import Path

import pandas as pd

from relaytic.aml import build_aml_graph_artifacts
from relaytic.analytics import build_task_contract_artifacts


def _write_aml_graph_dataset(path: Path) -> Path:
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


def _aml_task_contract_bundle(data_path: Path) -> dict[str, dict]:
    return build_task_contract_artifacts(
        data_path=data_path,
        mandate_bundle={
            "run_brief": {
                "objective": (
                    "Do AML transaction monitoring, detect suspicious subgraphs, and optimize the analyst review queue."
                )
            }
        },
        context_bundle={
            "task_brief": {
                "target_column": "suspicious_activity_flag",
                "problem_statement": "Classify suspicious_activity_flag for AML analyst review.",
            },
            "domain_brief": {
                "summary": "Payment-fraud and financial-crime review workflow with structural risk.",
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


def test_build_aml_graph_artifacts_constructs_entity_graph_and_subgraph(tmp_path: Path) -> None:
    data_path = _write_aml_graph_dataset(tmp_path / "aml_graph.csv")
    task_contract_bundle = _aml_task_contract_bundle(data_path)

    artifacts = build_aml_graph_artifacts(
        data_path=data_path,
        context_bundle={
            "domain_brief": {
                "summary": "AML transaction monitoring with entity and counterparty reasoning."
            }
        },
        task_contract_bundle=task_contract_bundle,
    )

    graph_profile = artifacts["entity_graph_profile"]
    subgraph = artifacts["subgraph_risk_report"]
    case_expansion = artifacts["entity_case_expansion"]
    assert graph_profile["status"] == "active"
    assert graph_profile["node_count"] >= 8
    assert graph_profile["edge_count"] >= 8
    assert graph_profile["high_risk_entities"][0]["entity_id"] == "HUB1"
    assert subgraph["status"] == "active"
    assert subgraph["candidate_comparison"]["winner"] == "structural_baseline"
    assert case_expansion["focal_entity"] == "HUB1"
    assert case_expansion["expanded_entity_count"] >= 3


def test_build_aml_graph_artifacts_detects_typologies(tmp_path: Path) -> None:
    data_path = _write_aml_graph_dataset(tmp_path / "aml_typology.csv")
    task_contract_bundle = _aml_task_contract_bundle(data_path)

    artifacts = build_aml_graph_artifacts(
        data_path=data_path,
        context_bundle={},
        task_contract_bundle=task_contract_bundle,
    )

    typology_report = artifacts["typology_detection_report"]
    typologies = {item["typology"] for item in typology_report["typology_hits"]}
    assert typology_report["status"] == "active"
    assert "smurfing" in typologies
    assert "funnel_accounts" in typologies or "layering" in typologies
