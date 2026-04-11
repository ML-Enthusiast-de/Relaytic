from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from relaytic.analytics import sync_architecture_routing_artifacts
from relaytic.benchmark import run_benchmark_review
from relaytic.modeling.training import train_surrogate_candidates


def _write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _build_planning_bundle(
    *,
    run_dir: Path,
    frame: pd.DataFrame,
    target_column: str,
    feature_columns: list[str],
    requested_model_family: str,
    timestamp_column: str | None = None,
    lag_horizon_samples: int | None = None,
) -> dict[str, dict]:
    training = train_surrogate_candidates(
        frame=frame,
        target_column=target_column,
        feature_columns=feature_columns,
        requested_model_family=requested_model_family,
        timestamp_column=timestamp_column,
        compare_against_baseline=False,
        lag_horizon_samples=lag_horizon_samples,
        task_type="binary_classification",
        output_run_dir=run_dir / "selected_route_train",
    )
    return {
        "plan": {
            "task_type": str(training["task_profile"]["task_type"]),
            "data_mode": str(training["data_mode"]),
            "target_column": target_column,
            "feature_columns": feature_columns,
            "timestamp_column": timestamp_column,
            "primary_metric": "log_loss",
            "task_profile": dict(training["task_profile"]),
            "builder_handoff": {
                "target_column": target_column,
                "normalize": True,
                "missing_data_strategy": "fill_median",
                "threshold_policy": "auto",
                "lag_horizon_samples": int(lag_horizon_samples or 0),
            },
            "execution_summary": {
                "selected_model_family": str(training["selected_model_family"]),
                "selected_metrics": dict(training["selected_metrics"]),
                "selected_hyperparameters": dict(training["selected_hyperparameters"]),
                "selection_metric": str(training.get("selection_metric") or "auto"),
            },
        }
    }


def test_benchmark_shadow_trials_can_mark_imported_family_promotion_ready(tmp_path: Path) -> None:
    run_dir = tmp_path / "imported_shadow_ready"
    rows: list[dict[str, int | float]] = []
    for x1 in (0, 1):
        for x2 in (0, 1):
            for repeat in range(120):
                rows.append(
                    {
                        "feature_a": float(x1),
                        "feature_b": float(x2),
                        "feature_noise": float((repeat % 5) / 10.0),
                        "label": int(x1 ^ x2),
                    }
                )
    frame = pd.DataFrame(rows)
    data_path = tmp_path / "xor_binary.csv"
    frame.to_csv(data_path, index=False)
    feature_columns = ["feature_a", "feature_b", "feature_noise"]
    planning_bundle = _build_planning_bundle(
        run_dir=run_dir,
        frame=frame,
        target_column="label",
        feature_columns=feature_columns,
        requested_model_family="logistic_regression",
    )
    sync_architecture_routing_artifacts(
        run_dir,
        investigation_bundle={
            "dataset_profile": {
                "row_count": len(frame),
                "column_count": len(frame.columns),
                "numeric_columns": feature_columns,
                "categorical_columns": [],
            },
            "optimization_profile": {},
        },
        planning_bundle=planning_bundle,
        route_prior_context={},
        benchmark_bundle={},
    )
    _write_json(
        run_dir / "method_import_report.json",
        {
            "status": "ok",
            "imported_family_count": 1,
            "imported_families": [{"family_id": "hist_gradient_boosting_classifier"}],
        },
    )
    _write_json(
        run_dir / "architecture_candidate_registry.json",
        {
            "status": "ok",
            "candidate_count": 1,
            "candidates": [
                {
                    "candidate_id": "architecture_candidate::hist_gradient_boosting_classifier",
                    "family_id": "hist_gradient_boosting_classifier",
                    "family_title": "Histogram gradient boosting classifier",
                    "research_disposition": "accepted",
                    "training_support": True,
                    "availability_status": "available",
                    "temporal_gate_required": False,
                }
            ],
        },
    )

    result = run_benchmark_review(
        run_dir=run_dir,
        data_path=str(data_path),
        policy={},
        planning_bundle=planning_bundle,
        mandate_bundle={},
        context_bundle={},
    )

    score_rows = result.bundle.shadow_trial_scorecard.rows
    assert score_rows
    row = next(item for item in score_rows if item["family_id"] == "hist_gradient_boosting_classifier")
    assert row["training_executed"] is True
    assert row["shadow_mode"] == "same_split_shadow_trial"
    assert row["promotion_state"] == "promotion_ready"
    assert result.bundle.promotion_readiness_report.promotion_ready_count >= 1


def test_benchmark_temporal_imported_family_stays_quarantined_until_baseline_proof(tmp_path: Path) -> None:
    run_dir = tmp_path / "imported_temporal_quarantine"
    rows: list[dict[str, object]] = []
    for idx in range(180):
        rows.append(
            {
                "timestamp": f"2026-01-{(idx // 24) + 1:02d}T{idx % 24:02d}:00:00",
                "sensor_a": round((idx % 12) / 11.0, 5),
                "sensor_b": round(((idx + 3) % 7) / 6.0, 5),
                "occupancy_flag": 1 if (idx % 9 in {0, 1, 2} or idx % 12 > 8) else 0,
            }
        )
    frame = pd.DataFrame(rows)
    data_path = tmp_path / "temporal_binary.csv"
    frame.to_csv(data_path, index=False)
    feature_columns = ["sensor_a", "sensor_b"]
    planning_bundle = _build_planning_bundle(
        run_dir=run_dir,
        frame=frame,
        target_column="occupancy_flag",
        feature_columns=feature_columns,
        requested_model_family="lagged_logistic_regression",
        timestamp_column="timestamp",
        lag_horizon_samples=3,
    )
    sync_architecture_routing_artifacts(
        run_dir,
        investigation_bundle={
            "dataset_profile": {
                "row_count": len(frame),
                "column_count": len(frame.columns),
                "numeric_columns": feature_columns,
                "categorical_columns": [],
                "timestamp_column": "timestamp",
            },
            "optimization_profile": {},
        },
        planning_bundle=planning_bundle,
        route_prior_context={},
        benchmark_bundle={},
    )
    _write_json(
        run_dir / "method_import_report.json",
        {
            "status": "ok",
            "imported_family_count": 1,
            "imported_families": [{"family_id": "sequence_lstm_candidate"}],
        },
    )
    _write_json(
        run_dir / "architecture_candidate_registry.json",
        {
            "status": "ok",
            "candidate_count": 1,
            "candidates": [
                {
                    "candidate_id": "architecture_candidate::sequence_lstm_candidate",
                    "family_id": "sequence_lstm_candidate",
                    "family_title": "LSTM sequence candidate",
                    "research_disposition": "accepted",
                    "training_support": False,
                    "availability_status": "shadow_only",
                    "temporal_gate_required": True,
                }
            ],
        },
    )

    result = run_benchmark_review(
        run_dir=run_dir,
        data_path=str(data_path),
        policy={},
        planning_bundle=planning_bundle,
        mandate_bundle={},
        context_bundle={},
    )

    row = next(item for item in result.bundle.shadow_trial_scorecard.rows if item["family_id"] == "sequence_lstm_candidate")
    assert row["shadow_mode"] == "offline_replay_only"
    assert row["promotion_state"] == "quarantined"
    assert row["baseline_family"] in {"lagged_logistic_regression", "lagged_tree_classifier", "lagged_tree_ensemble"}
    assert "lagged_baseline_required" in row["reason_codes"]
