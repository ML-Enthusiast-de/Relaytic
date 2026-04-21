from __future__ import annotations

from pathlib import Path

from relaytic.aml import build_aml_graph_artifacts
from relaytic.analytics import build_task_contract_artifacts

from tests.aml_workload_fixtures import write_elliptic_like_dataset, write_paysim_like_dataset


def _aml_contract_bundle(
    *,
    data_path: Path,
    objective: str,
    target_column: str,
    timestamp_column: str,
    data_mode: str,
) -> dict[str, dict]:
    return build_task_contract_artifacts(
        data_path=data_path,
        mandate_bundle={
            "run_brief": {
                "objective": objective,
            }
        },
        context_bundle={
            "task_brief": {
                "target_column": target_column,
                "problem_statement": objective,
            },
            "domain_brief": {
                "summary": objective,
                "target_meaning": "Whether the event should be escalated into analyst review.",
            },
        },
        investigation_bundle={
            "dataset_profile": {
                "row_count": 0,
                "column_count": 0,
                "data_mode": data_mode,
                "timestamp_column": timestamp_column,
            }
        },
        planning_bundle={
            "plan": {
                "target_column": target_column,
                "task_type": "binary_classification",
                "data_mode": data_mode,
                "timestamp_column": timestamp_column,
                "primary_metric": "pr_auc",
                "split_strategy": "blocked_time_order_70_15_15",
                "builder_handoff": {
                    "selection_metric": "log_loss",
                    "threshold_policy": "favor_pr_auc",
                },
                "task_profile": {
                    "target_signal": target_column,
                    "task_type": "binary_classification",
                    "task_family": "classification",
                    "data_mode": data_mode,
                    "target_semantics": "rare_event_supervised_label",
                    "problem_posture": "rare_event_supervised",
                    "rare_event_supervised": True,
                    "override_applied": False,
                    "recommended_split_strategy": "blocked_time_order_70_15_15",
                    "timestamp_column": timestamp_column,
                    "rationale": objective,
                },
            }
        },
    )


def test_build_aml_graph_artifacts_supports_paysim_like_columns(tmp_path: Path) -> None:
    data_path = write_paysim_like_dataset(tmp_path / "paysim_like.csv")
    task_contract_bundle = _aml_contract_bundle(
        data_path=data_path,
        objective=(
            "PaySim-style payment-fraud review queue. Classify isFraud, expand suspicious counterparties, "
            "and explain structurally suspicious subgraphs."
        ),
        target_column="isFraud",
        timestamp_column="step",
        data_mode="time_series",
    )

    artifacts = build_aml_graph_artifacts(
        data_path=data_path,
        context_bundle={"domain_brief": {"summary": "PaySim-style payment-fraud graph reasoning."}},
        task_contract_bundle=task_contract_bundle,
    )

    graph_profile = artifacts["entity_graph_profile"]
    typology_report = artifacts["typology_detection_report"]
    case_expansion = artifacts["entity_case_expansion"]

    assert graph_profile["status"] == "active"
    assert graph_profile["source_column"] == "nameOrig"
    assert graph_profile["destination_column"] == "nameDest"
    assert graph_profile["timestamp_column"] == "step"
    assert graph_profile["node_count"] >= 20
    assert typology_report["typology_hit_count"] >= 1
    assert any(hit["typology"] == "chargeback_abuse" for hit in typology_report["typology_hits"])
    assert case_expansion["focal_entity"]


def test_build_aml_graph_artifacts_supports_elliptic_like_columns(tmp_path: Path) -> None:
    data_path = write_elliptic_like_dataset(tmp_path / "elliptic_like.csv")
    task_contract_bundle = _aml_contract_bundle(
        data_path=data_path,
        objective=(
            "Elliptic-style temporal AML graph. Classify y, detect suspicious subgraphs, and preserve time_step stability "
            "for analyst escalation."
        ),
        target_column="y",
        timestamp_column="time_step",
        data_mode="time_series",
    )

    artifacts = build_aml_graph_artifacts(
        data_path=data_path,
        context_bundle={"domain_brief": {"summary": "Elliptic-style temporal graph AML reasoning."}},
        task_contract_bundle=task_contract_bundle,
    )

    graph_profile = artifacts["entity_graph_profile"]
    subgraph_report = artifacts["subgraph_risk_report"]
    typology_report = artifacts["typology_detection_report"]

    assert graph_profile["status"] == "active"
    assert graph_profile["source_column"] == "src"
    assert graph_profile["destination_column"] == "dst"
    assert graph_profile["timestamp_column"] == "time_step"
    assert graph_profile["node_count"] >= 15
    assert subgraph_report["status"] == "active"
    assert subgraph_report["candidate_comparison"]["winner"] == "structural_baseline"
    assert typology_report["typology_hit_count"] >= 1
