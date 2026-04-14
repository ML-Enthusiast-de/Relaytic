from __future__ import annotations

from pathlib import Path

from relaytic.analytics import build_temporal_engine_artifacts
from relaytic.modeling.splitters import build_train_validation_test_split
from tests.public_datasets import write_public_temporal_occupancy_dataset


def test_temporal_engine_detects_ordered_structure_and_richer_feature_ladder(tmp_path: Path) -> None:
    data_path = write_public_temporal_occupancy_dataset(tmp_path / "temporal_engine_occupancy.csv", max_rows=576)

    artifacts = build_temporal_engine_artifacts(
        data_path=data_path,
        investigation_bundle={
            "dataset_profile": {
                "row_count": 576,
                "column_count": 7,
                "data_mode": "time_series",
                "timestamp_column": "timestamp",
            }
        },
        planning_bundle={
            "plan": {
                "data_mode": "time_series",
                "task_type": "binary_classification",
                "target_column": "occupancy_flag",
                "feature_columns": ["temperature", "humidity", "light", "co2", "humidity_ratio"],
                "builder_handoff": {"lag_horizon_samples": 4},
            }
        },
        task_contract_bundle={
            "task_profile_contract": {
                "data_mode": "time_series",
                "task_type": "binary_classification",
                "timestamp_column": "timestamp",
                "target_column": "occupancy_flag",
                "row_count": 576,
            }
        },
        architecture_bundle={
            "architecture_router_report": {
                "sequence_shadow_ready": True,
                "sequence_live_allowed": False,
            },
            "architecture_ablation_report": {
                "shadow_sequence_candidates": ["sequence_lstm_candidate", "temporal_transformer_candidate"],
            },
        },
    )

    structure = artifacts["temporal_structure_report"]
    ladder = artifacts["temporal_feature_ladder"]

    assert structure["status"] == "ok"
    assert structure["ordered_temporal_structure"] is True
    assert structure["regular_cadence"] is True
    assert ladder["status"] == "ok"
    assert "lag_windows" in ladder["materialized_feature_families"]
    assert "delta_features" in ladder["materialized_feature_families"]
    assert any(str(item).startswith("rolling_mean_") for item in ladder["materialized_feature_families"])
    assert any(str(item).startswith("seasonal_delta_") for item in ladder["materialized_feature_families"])


def test_time_series_splitter_preserves_future_binary_events_when_possible() -> None:
    labels = [0] * 96 + [1] * 24 + [0] * 96 + [1] * 24 + [0] * 96 + [1] * 24
    split = build_train_validation_test_split(
        n_rows=len(labels),
        data_mode="time_series",
        task_type="binary_classification",
        stratify_labels=labels,
    )

    validation_labels = [labels[index] for index in split.validation_indices.tolist()]
    test_labels = [labels[index] for index in split.test_indices.tolist()]

    assert split.strategy in {"blocked_time_order_event_preserving_70_15_15", "blocked_time_order_70_15_15"}
    assert any(label == 1 for label in validation_labels)
    assert any(label == 1 for label in test_labels)
