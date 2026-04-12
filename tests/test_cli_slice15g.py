from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import pytest

pytest.importorskip("sklearn.datasets")

from relaytic.ui.cli import main
from tests.public_datasets import write_public_breast_cancer_dataset


def test_cli_slice15g_materializes_objective_and_split_truth_for_public_binary_run(tmp_path: Path, capsys) -> None:
    run_dir = tmp_path / "slice15g_binary"
    data_path = write_public_breast_cancer_dataset(tmp_path / "slice15g_breast_cancer.csv")

    assert main(
        [
            "run",
            "--run-dir",
            str(run_dir),
            "--data-path",
            str(data_path),
            "--text",
            "Classify diagnosis_flag from the measurement columns, benchmark against strong references, and explain the route choice.",
            "--format",
            "json",
        ]
    ) == 0
    payload = json.loads(capsys.readouterr().out)

    assert payload["status"] == "ok"
    assert payload["run_summary"]["objective_contract"]["status"] == "ok"
    assert payload["run_summary"]["objective_contract"]["benchmark_comparison_metric"] == "pr_auc"
    assert payload["run_summary"]["split_health"]["status"] == "ok"
    assert payload["run_summary"]["objective_contract"]["truth_precheck_status"] == "ok"
    for artifact_name in (
        "optimization_objective_contract.json",
        "objective_alignment_report.json",
        "split_diagnostics_report.json",
        "temporal_fold_health.json",
        "metric_materialization_audit.json",
        "benchmark_truth_precheck.json",
    ):
        assert (run_dir / artifact_name).exists(), artifact_name


def test_cli_slice15g_temporal_benchmark_fails_closed_when_truth_precheck_blocks_it(tmp_path: Path, capsys) -> None:
    run_dir = tmp_path / "slice15g_temporal_block"
    data_path = tmp_path / "slice15g_temporal_block.csv"
    frame = pd.DataFrame(
        {
            "timestamp": pd.date_range("2026-01-01 00:00:00", periods=60, freq="5min"),
            "sensor_a": [float(index % 7) for index in range(60)],
            "sensor_b": [float((index * 5) % 13) for index in range(60)],
            "occupancy_flag": [1 if index < 12 else 0 for index in range(60)],
        }
    )
    frame["timestamp"] = frame["timestamp"].dt.strftime("%Y-%m-%d %H:%M:%S")
    frame.to_csv(data_path, index=False)

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
    run_payload = json.loads(capsys.readouterr().out)
    assert run_payload["run_summary"]["split_health"]["temporal_fold_status"] == "blocked"
    assert run_payload["run_summary"]["split_health"]["safe_for_benchmarking"] is False

    assert main(["benchmark", "run", "--run-dir", str(run_dir), "--data-path", str(data_path), "--overwrite", "--format", "json"]) == 0
    benchmark_payload = json.loads(capsys.readouterr().out)
    assert benchmark_payload["benchmark"]["parity_status"] == "reference_unavailable"
    assert benchmark_payload["benchmark"]["truth_precheck_status"] == "blocked"
    assert benchmark_payload["benchmark"]["safe_to_rank"] is False
