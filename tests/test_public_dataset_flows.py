import json
from pathlib import Path

import pytest

pytest.importorskip("sklearn.datasets")

from relaytic.ui.cli import main

from tests.public_datasets import (
    write_public_breast_cancer_dataset,
    write_public_diabetes_dataset,
    write_public_wine_dataset,
)


def test_cli_run_supports_public_diabetes_regression_dataset(tmp_path: Path, capsys) -> None:
    run_dir = tmp_path / "run_public_diabetes"
    data_path = write_public_diabetes_dataset(tmp_path / "public_diabetes.csv")

    assert main(
        [
            "run",
            "--run-dir",
            str(run_dir),
            "--data-path",
            str(data_path),
            "--text",
            "Estimate disease_progression from the patient measurements. Do everything on your own.",
            "--format",
            "json",
        ]
    ) == 0

    payload = json.loads(capsys.readouterr().out)
    plan = json.loads((run_dir / "plan.json").read_text(encoding="utf-8"))

    assert payload["status"] == "ok"
    assert payload["run_summary"]["decision"]["task_type"] == "regression"
    assert payload["run_summary"]["data"]["row_count"] == 442
    assert plan["selected_route_id"] == "steady_state_tabular_regression_route"


def test_cli_run_supports_public_breast_cancer_binary_dataset(tmp_path: Path, capsys) -> None:
    run_dir = tmp_path / "run_public_breast_cancer"
    data_path = write_public_breast_cancer_dataset(tmp_path / "public_breast_cancer.csv")

    assert main(
        [
            "run",
            "--run-dir",
            str(run_dir),
            "--data-path",
            str(data_path),
            "--text",
            "Classify diagnosis_flag from the measurement columns. Do everything on your own.",
            "--format",
            "json",
        ]
    ) == 0

    payload = json.loads(capsys.readouterr().out)
    plan = json.loads((run_dir / "plan.json").read_text(encoding="utf-8"))

    assert payload["status"] == "ok"
    assert payload["run_summary"]["decision"]["task_type"] == "binary_classification"
    assert payload["run_summary"]["data"]["row_count"] == 569
    assert plan["selected_route_id"] == "calibrated_tabular_classifier_route"


def test_cli_run_supports_public_wine_multiclass_dataset(tmp_path: Path, capsys) -> None:
    run_dir = tmp_path / "run_public_wine"
    data_path = write_public_wine_dataset(tmp_path / "public_wine.csv")

    assert main(
        [
            "run",
            "--run-dir",
            str(run_dir),
            "--data-path",
            str(data_path),
            "--text",
            "Classify wine_class from the lab measurements. Do everything on your own.",
            "--format",
            "json",
        ]
    ) == 0

    payload = json.loads(capsys.readouterr().out)
    plan = json.loads((run_dir / "plan.json").read_text(encoding="utf-8"))

    assert payload["status"] == "ok"
    assert payload["run_summary"]["decision"]["task_type"] == "multiclass_classification"
    assert payload["run_summary"]["data"]["row_count"] == 178
    assert plan["selected_route_id"] == "calibrated_tabular_classifier_route"
