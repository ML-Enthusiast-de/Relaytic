from __future__ import annotations

import json
from pathlib import Path

import pytest

pytest.importorskip("sklearn.datasets")

from relaytic.ui.cli import main
from tests.public_datasets import (
    write_public_temporal_energy_dataset,
    write_public_temporal_occupancy_dataset,
)


def test_cli_slice15j_run_materializes_temporal_engine_and_preserves_future_events(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    run_dir = tmp_path / "slice15j_temporal_run"
    data_path = write_public_temporal_occupancy_dataset(tmp_path / "slice15j_occupancy.csv", max_rows=720)

    assert main(
        [
            "run",
            "--run-dir",
            str(run_dir),
            "--data-path",
            str(data_path),
            "--text",
            "Classify occupancy_flag from the room sensor columns over time. Do everything on your own.",
            "--format",
            "json",
        ]
    ) == 0
    payload = json.loads(capsys.readouterr().out)

    assert payload["status"] == "ok"
    assert payload["run_summary"]["split_health"]["temporal_fold_status"] == "ok"
    assert payload["run_summary"]["split_health"]["validation_positive_count"] > 0
    assert payload["run_summary"]["split_health"]["test_positive_count"] > 0
    assert payload["run_summary"]["temporal"]["ordered_temporal_structure"] is True
    assert "lag_windows" in payload["run_summary"]["temporal"]["materialized_feature_families"]

    for filename in (
        "temporal_structure_report.json",
        "temporal_feature_ladder.json",
        "rolling_cv_plan.json",
        "temporal_split_guard_report.json",
        "sequence_shadow_scorecard.json",
        "temporal_baseline_ladder.json",
        "temporal_metric_contract.json",
    ):
        assert (run_dir / filename).exists(), filename


def test_cli_slice15j_temporal_benchmark_materializes_metric_and_lagged_baseline(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    run_dir = tmp_path / "slice15j_temporal_benchmark"
    data_path = write_public_temporal_energy_dataset(tmp_path / "slice15j_energy.csv", max_rows=960)

    assert main(
        [
            "run",
            "--run-dir",
            str(run_dir),
            "--data-path",
            str(data_path),
            "--text",
            "Reliably predict energy_target from the energy signals over time and do everything on your own.",
            "--format",
            "json",
        ]
    ) == 0
    capsys.readouterr()

    assert main(["benchmark", "run", "--run-dir", str(run_dir), "--data-path", str(data_path), "--overwrite", "--format", "json"]) == 0
    payload = json.loads(capsys.readouterr().out)

    metric_contract = payload["bundle"]["temporal_metric_contract"]
    baseline_ladder = payload["bundle"]["temporal_baseline_ladder"]

    assert payload["status"] == "ok"
    assert metric_contract["status"] == "ok"
    assert metric_contract["comparison_metric"]
    assert metric_contract["comparison_metric_materialized_in_benchmark_rows"] is True
    assert baseline_ladder["status"] == "ok"
    assert baseline_ladder["lagged_baseline_family"]
    assert baseline_ladder["ordinary_baseline_family"]
    assert baseline_ladder["lagged_beats_ordinary"] is True


def test_cli_slice15j_sequence_candidates_stay_shadow_only_against_lagged_baseline(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    run_dir = tmp_path / "slice15j_sequence_shadow"
    data_path = write_public_temporal_occupancy_dataset(tmp_path / "slice15j_shadow_occupancy.csv", max_rows=720)

    assert main(
        [
            "run",
            "--run-dir",
            str(run_dir),
            "--data-path",
            str(data_path),
            "--text",
            "Classify occupancy_flag from the room sensor columns over time, benchmark against strong references, and explain the temporal classifier route.",
            "--format",
            "json",
        ]
    ) == 0
    capsys.readouterr()

    assert main(["benchmark", "run", "--run-dir", str(run_dir), "--data-path", str(data_path), "--overwrite", "--format", "json"]) == 0
    payload = json.loads(capsys.readouterr().out)

    scorecard = payload["bundle"]["sequence_shadow_scorecard"]
    row = next(item for item in scorecard["rows"] if item["family_id"] == "sequence_lstm_candidate")

    assert scorecard["status"] == "ok"
    assert row["baseline_family"] in {"sklearn_lagged_logistic_regression", "sklearn_lagged_random_forest_classifier", "sklearn_lagged_gradient_boosting_classifier", "lagged_logistic_regression", "lagged_tree_classifier", "lagged_tree_ensemble"}
    assert row["promotion_state"] == "shadow_only"
    assert row["comparison_outcome"] in {"baseline_unbeaten", "loses_to_lagged_baseline"}
