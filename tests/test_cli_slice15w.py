from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import pytest

pytest.importorskip("sklearn.datasets")

from relaytic.analytics import sync_task_contract_artifacts
from relaytic.core.json_utils import write_json
from relaytic.ui.cli import main


def _write_temporal_weak_label_dataset(path: Path) -> Path:
    rows: list[dict[str, object]] = []
    for step in range(1, 13):
        rows.append(
            {
                "step": step,
                "type": "PAYMENT",
                "amount": 10.0 + float(step % 3),
                "nameOrig": f"BENIGN_{step:02d}",
                "oldbalanceOrg": 3000.0 - 20.0 * step,
                "newbalanceOrig": 3000.0 - 20.0 * step - (10.0 + float(step % 3)),
                "nameDest": f"MERCHANT_{(step % 4) + 1}",
                "oldbalanceDest": 500.0,
                "newbalanceDest": 500.0 + (10.0 + float(step % 3)),
                "device_id": f"benign-device-{step % 4}",
                "isFraud": 0 if step % 6 else 1,
            }
        )
    for step in range(13, 25):
        rows.append(
            {
                "step": step,
                "type": "TRANSFER",
                "amount": 100.0 + float(step % 5),
                "nameOrig": f"RISK_{step:02d}",
                "oldbalanceOrg": 6000.0 - 40.0 * step,
                "newbalanceOrig": 6000.0 - 40.0 * step - (100.0 + float(step % 5)),
                "nameDest": "MULE_HUB",
                "oldbalanceDest": 100.0,
                "newbalanceDest": 100.0 + (100.0 + float(step % 5)),
                "device_id": "shared-risk-device",
                "isFraud": 1,
            }
        )
    pd.DataFrame(rows).to_csv(path, index=False)
    return path


def _write_minimal_temporal_run_inputs(run_dir: Path, data_path: Path) -> None:
    run_dir.mkdir(parents=True, exist_ok=True)
    run_brief = {
        "schema_version": "test.run_brief.v1",
        "objective": "AML transaction monitoring with weak labels and delayed outcomes.",
        "success_criteria": ["Keep temporal benchmark claims conservative."],
        "target_column": "isFraud",
    }
    task_brief = {
        "schema_version": "test.task_brief.v1",
        "target_column": "isFraud",
        "task_type_hint": "binary_classification",
        "problem_statement": "Classify isFraud for AML analyst review under delayed labels and threshold drift.",
        "success_criteria": ["Use rolling temporal windows and positive-unlabeled posture."],
    }
    domain_brief = {
        "schema_version": "test.domain_brief.v1",
        "summary": "Streaming AML analyst-review monitoring with weak labels, delayed outcomes, and payment fraud drift.",
        "target_meaning": "Whether a transaction should be escalated for AML review.",
    }
    dataset_profile = {
        "schema_version": "test.dataset_profile.v1",
        "row_count": 24,
        "column_count": 11,
        "data_mode": "time_series",
        "timestamp_column": "step",
    }
    plan = {
        "schema_version": "test.plan.v1",
        "target_column": "isFraud",
        "task_type": "binary_classification",
        "data_mode": "time_series",
        "primary_metric": "pr_auc",
        "split_strategy": "blocked_time_order_event_preserving_70_15_15",
        "feature_columns": [
            "step",
            "type",
            "amount",
            "nameOrig",
            "oldbalanceOrg",
            "newbalanceOrig",
            "nameDest",
            "oldbalanceDest",
            "newbalanceDest",
            "device_id",
        ],
        "builder_handoff": {
            "selection_metric": "log_loss",
            "threshold_policy": "favor_pr_auc",
            "timestamp_column": "step",
        },
        "task_profile": {
            "target_signal": "isFraud",
            "task_type": "binary_classification",
            "task_family": "classification",
            "data_mode": "time_series",
            "target_semantics": "rare_event_supervised_label",
            "problem_posture": "rare_event_supervised",
            "rare_event_supervised": True,
            "row_count": 24,
            "class_count": 2,
            "class_balance": {"0": 10, "1": 14},
            "minority_class_fraction": 10 / 24,
            "positive_class_label": "1",
            "recommended_split_strategy": "blocked_time_order_event_preserving_70_15_15",
        },
    }
    write_json(run_dir / "run_brief.json", run_brief, indent=2, sort_keys=True)
    write_json(run_dir / "task_brief.json", task_brief, indent=2, sort_keys=True)
    write_json(run_dir / "domain_brief.json", domain_brief, indent=2, sort_keys=True)
    write_json(run_dir / "dataset_profile.json", dataset_profile, indent=2, sort_keys=True)
    write_json(run_dir / "plan.json", plan, indent=2, sort_keys=True)
    write_json(
        run_dir / "temporal_structure_report.json",
        {
            "schema_version": "test.temporal_structure_report.v1",
            "status": "active",
            "ordered_temporal_structure": True,
            "timestamp_column": "step",
        },
        indent=2,
        sort_keys=True,
    )
    write_json(
        run_dir / "rolling_cv_plan.json",
        {
            "schema_version": "test.rolling_cv_plan.v1",
            "status": "active",
            "recommended_strategy": "rolling_origin_holdout",
        },
        indent=2,
        sort_keys=True,
    )
    write_json(
        run_dir / "operating_point_contract.json",
        {
            "schema_version": "test.operating_point_contract.v1",
            "status": "active",
            "selected_review_fraction": 0.2,
            "threshold_policy": "favor_pr_auc",
        },
        indent=2,
        sort_keys=True,
    )
    sync_task_contract_artifacts(
        run_dir,
        data_path=data_path,
        mandate_bundle={"run_brief": run_brief},
        context_bundle={"task_brief": task_brief, "domain_brief": domain_brief},
        investigation_bundle={"dataset_profile": dataset_profile},
        planning_bundle={"plan": plan},
    )


def test_cli_slice15w_materializes_temporal_weak_label_claim_gates(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    run_dir = tmp_path / "slice15w_temporal"
    data_path = _write_temporal_weak_label_dataset(tmp_path / "slice15w_temporal.csv")
    _write_minimal_temporal_run_inputs(run_dir, data_path)

    assert main(
        [
            "aml",
            "temporal",
            "--run-dir",
            str(run_dir),
            "--data-path",
            str(data_path),
            "--overwrite",
            "--format",
            "json",
        ]
    ) == 0
    temporal_payload = json.loads(capsys.readouterr().out)

    temporal = temporal_payload["aml_temporal"]
    assert temporal["claim_state"] == "supporting_only"
    assert temporal["supporting_temporal_evidence_allowed"] is True
    assert temporal["temporal_public_claim_allowed"] is False
    assert temporal_payload["run_summary"]["aml_temporal"]["supporting_temporal_evidence_allowed"] is True
    assert temporal_payload["run_summary"]["aml_temporal"]["temporal_public_claim_allowed"] is False
    assert temporal["window_count"] >= 3
    assert temporal["pu_risk_state"] in {"positive_unlabeled_required", "positive_unlabeled_watch"}
    assert temporal["threshold_reset_recommended"] is True
    assert temporal["recommended_action"] == "run_recalibration_pass"
    assert "delayed_label_maturity_unproven" in temporal["claim_blockers"]
    assert "positive_unlabeled_truth_unresolved" in temporal["claim_blockers"]
    assert "threshold_drift_requires_recalibration" in temporal["claim_blockers"]

    for filename in (
        "aml_delayed_label_eval_report.json",
        "aml_positive_unlabeled_posture.json",
        "aml_threshold_drift_report.json",
        "aml_time_window_scorecard.json",
        "aml_temporal_benchmark_claim_report.json",
    ):
        assert (run_dir / filename).exists(), filename
