from __future__ import annotations

from pathlib import Path

import pandas as pd

from relaytic.analytics import build_task_contract_artifacts
from relaytic.stream_risk import build_stream_risk_artifacts


def _write_stream_drift_dataset(path: Path) -> Path:
    rows: list[dict[str, object]] = []
    for step in range(1, 13):
        rows.append(
            {
                "step": step,
                "source_account": f"BENIGN_{step:02d}",
                "destination_account": f"MERCHANT_{(step % 4) + 1}",
                "txn_amount": 12.0 + float(step % 3),
                "device_id": f"dev-benign-{step % 5}",
                "suspicious_activity_flag": 0 if step % 5 else 1,
            }
        )
    for step in range(13, 25):
        rows.append(
            {
                "step": step,
                "source_account": f"RISK_{step:02d}",
                "destination_account": "MULE_HUB",
                "txn_amount": 85.0 + float(step % 6),
                "device_id": "shared-risk-device",
                "suspicious_activity_flag": 1,
            }
        )
    pd.DataFrame(rows).to_csv(path, index=False)
    return path


def _stream_task_contract_bundle(data_path: Path) -> dict[str, dict]:
    return build_task_contract_artifacts(
        data_path=data_path,
        mandate_bundle={
            "run_brief": {
                "objective": (
                    "Do AML transaction monitoring under weak labels and delayed outcomes, "
                    "then decide whether stream drift justifies recalibration."
                )
            }
        },
        context_bundle={
            "task_brief": {
                "target_column": "suspicious_activity_flag",
                "problem_statement": "Classify suspicious_activity_flag for AML analyst review under delayed labels.",
            },
            "domain_brief": {
                "summary": "Streaming payment-fraud triage with delayed confirmation and weak labels.",
                "target_meaning": "Whether a transaction should be escalated into analyst review.",
            },
        },
        investigation_bundle={"dataset_profile": {"row_count": 24, "column_count": 6, "data_mode": "time_series", "timestamp_column": "step"}},
        planning_bundle={
            "plan": {
                "target_column": "suspicious_activity_flag",
                "task_type": "binary_classification",
                "data_mode": "time_series",
                "primary_metric": "pr_auc",
                "split_strategy": "blocked_time_order_event_preserving_70_15_15",
                "builder_handoff": {"selection_metric": "log_loss", "threshold_policy": "favor_pr_auc"},
                "task_profile": {
                    "target_signal": "suspicious_activity_flag",
                    "task_type": "binary_classification",
                    "task_family": "classification",
                    "data_mode": "time_series",
                    "target_semantics": "rare_event_supervised_label",
                    "problem_posture": "rare_event_supervised",
                    "rare_event_supervised": True,
                    "override_applied": False,
                    "row_count": 24,
                    "class_count": 2,
                    "class_balance": {"0": 10, "1": 14},
                    "minority_class_fraction": 10 / 24,
                    "positive_class_label": "1",
                    "recommended_split_strategy": "blocked_time_order_event_preserving_70_15_15",
                    "rationale": "Ordered AML stream with delayed labels and review pressure.",
                },
            }
        },
    )


def test_build_stream_risk_artifacts_persists_weak_label_and_delay_posture(tmp_path: Path) -> None:
    data_path = _write_stream_drift_dataset(tmp_path / "stream_weak_labels.csv")
    task_contract_bundle = _stream_task_contract_bundle(data_path)

    artifacts = build_stream_risk_artifacts(
        data_path=data_path,
        context_bundle={
            "domain_brief": {"summary": "Streaming AML review under weak labels."},
            "task_brief": {"problem_statement": "Delayed labels and analyst review."},
        },
        task_contract_bundle=task_contract_bundle,
        temporal_bundle={
            "temporal_structure_report": {
                "status": "active",
                "ordered_temporal_structure": True,
                "timestamp_column": "step",
            },
            "rolling_cv_plan": {"recommended_strategy": "rolling_origin_holdout"},
        },
        operating_point_bundle={"operating_point_contract": {"selected_review_fraction": 0.2}},
    )

    stream_risk = artifacts["stream_risk_posture"]
    weak_labels = artifacts["weak_label_posture"]
    delayed = artifacts["delayed_outcome_alignment"]
    rolling = artifacts["rolling_alert_quality_report"]

    assert stream_risk["status"] == "active"
    assert stream_risk["stream_mode"] == "batched_temporal_monitoring"
    assert stream_risk["timestamp_column"] == "step"
    assert weak_labels["weak_label_risk_level"] == "high"
    assert weak_labels["delayed_confirmation_likely"] is True
    assert delayed["alignment_state"] == "rolling_shadow_holdout"
    assert rolling["window_count"] >= 3


def test_build_stream_risk_artifacts_triggers_recalibration_under_clear_drift(tmp_path: Path) -> None:
    data_path = _write_stream_drift_dataset(tmp_path / "stream_drift_trigger.csv")
    task_contract_bundle = _stream_task_contract_bundle(data_path)

    artifacts = build_stream_risk_artifacts(
        data_path=data_path,
        context_bundle={
            "domain_brief": {"summary": "Streaming payment fraud with late concept drift."},
            "task_brief": {"problem_statement": "Detect drift and decide whether recalibration is needed."},
        },
        task_contract_bundle=task_contract_bundle,
        temporal_bundle={
            "temporal_structure_report": {
                "status": "active",
                "ordered_temporal_structure": True,
                "timestamp_column": "step",
            },
            "rolling_cv_plan": {"recommended_strategy": "rolling_origin_holdout"},
        },
        operating_point_bundle={"operating_point_contract": {"selected_review_fraction": 0.2}},
    )

    trigger = artifacts["drift_recalibration_trigger"]
    assert trigger["status"] == "active"
    assert trigger["drift_score"] >= 0.55
    assert trigger["trigger_recalibration"] is True
    assert trigger["recommended_action"] == "run_recalibration_pass"
