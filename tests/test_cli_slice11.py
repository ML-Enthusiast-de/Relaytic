import json
from pathlib import Path

import pytest

pytest.importorskip("sklearn.datasets")

from relaytic.ui.cli import main

from tests.public_datasets import (
    write_public_breast_cancer_dataset,
    write_public_diabetes_dataset,
)


def test_cli_run_and_benchmark_show_materialize_reference_parity_for_public_binary_run(
    tmp_path: Path, capsys
) -> None:
    run_dir = tmp_path / "benchmark_public_binary"
    data_path = write_public_breast_cancer_dataset(tmp_path / "public_breast_cancer.csv")

    assert main(
        [
            "run",
            "--run-dir",
            str(run_dir),
            "--data-path",
            str(data_path),
            "--text",
            "Do everything on your own. Classify diagnosis_flag and benchmark against strong references.",
            "--format",
            "json",
        ]
    ) == 0
    payload = json.loads(capsys.readouterr().out)

    benchmark = dict(payload["run_summary"].get("benchmark", {}))
    assert payload["status"] == "ok"
    assert benchmark["reference_count"] >= 2
    assert benchmark["parity_status"] in {
        "meets_or_exceeds_reference",
        "near_parity",
        "below_reference",
        "reference_unavailable",
    }

    for filename in (
        "reference_approach_matrix.json",
        "benchmark_gap_report.json",
        "benchmark_parity_report.json",
    ):
        assert (run_dir / filename).exists(), filename

    assert main(
        [
            "benchmark",
            "show",
            "--run-dir",
            str(run_dir),
            "--format",
            "json",
        ]
    ) == 0
    show_payload = json.loads(capsys.readouterr().out)

    assert show_payload["status"] == "ok"
    assert show_payload["benchmark"]["reference_count"] >= 2
    assert show_payload["bundle"]["benchmark_parity_report"]["status"] == "ok"


def test_cli_benchmark_run_supports_public_regression_run(tmp_path: Path, capsys) -> None:
    run_dir = tmp_path / "benchmark_public_regression"
    data_path = write_public_diabetes_dataset(tmp_path / "public_diabetes.csv")

    assert main(
        [
            "run",
            "--run-dir",
            str(run_dir),
            "--data-path",
            str(data_path),
            "--text",
            "Estimate disease_progression and benchmark against strong reference baselines.",
            "--format",
            "json",
        ]
    ) == 0
    capsys.readouterr()

    assert main(
        [
            "benchmark",
            "run",
            "--run-dir",
            str(run_dir),
            "--data-path",
            str(data_path),
            "--overwrite",
            "--format",
            "json",
        ]
    ) == 0
    payload = json.loads(capsys.readouterr().out)

    assert payload["status"] == "ok"
    assert payload["benchmark"]["comparison_metric"] in {"mae", "rmse", "r2", "mape"}
    assert payload["benchmark"]["reference_count"] >= 2
    assert payload["bundle"]["reference_approach_matrix"]["status"] == "ok"
