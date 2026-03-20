import json
import os
from pathlib import Path

import pytest

pytest.importorskip("ucimlrepo")

from relaytic.ui.cli import main

from tests.domain_datasets import (
    write_uci_ai4i_machine_failure_dataset,
    write_uci_concrete_strength_dataset,
    write_uci_credit_default_dataset,
    write_uci_iranian_churn_dataset,
)


pytestmark = pytest.mark.skipif(
    os.environ.get("RELAYTIC_ENABLE_NETWORK_DATASETS", "").strip() != "1",
    reason="Set RELAYTIC_ENABLE_NETWORK_DATASETS=1 to run official network-backed domain dataset tests.",
)


def test_cli_run_supports_uci_concrete_strength_regression_dataset(tmp_path: Path, capsys) -> None:
    run_dir = tmp_path / "run_uci_concrete"
    data_path = write_uci_concrete_strength_dataset(tmp_path / "uci_concrete_strength.csv")

    assert main(
        [
            "run",
            "--run-dir",
            str(run_dir),
            "--data-path",
            str(data_path),
            "--text",
            "Predict concrete_strength from the process and material mix columns. Do everything on your own.",
            "--format",
            "json",
        ]
    ) == 0

    payload = json.loads(capsys.readouterr().out)
    assert payload["status"] == "ok"
    assert payload["run_summary"]["decision"]["task_type"] == "regression"
    assert payload["run_summary"]["data"]["row_count"] == 1030


def test_cli_run_supports_uci_iranian_churn_dataset(tmp_path: Path, capsys) -> None:
    run_dir = tmp_path / "run_uci_churn"
    data_path = write_uci_iranian_churn_dataset(tmp_path / "uci_iranian_churn.csv")

    assert main(
        [
            "run",
            "--run-dir",
            str(run_dir),
            "--data-path",
            str(data_path),
            "--text",
            "Predict churn_flag from the telecom behavior columns. Do everything on your own.",
            "--format",
            "json",
        ]
    ) == 0

    payload = json.loads(capsys.readouterr().out)
    assert payload["status"] == "ok"
    assert payload["run_summary"]["decision"]["task_type"] == "binary_classification"
    assert payload["run_summary"]["data"]["row_count"] == 2500


def test_cli_run_supports_uci_credit_default_dataset(tmp_path: Path, capsys) -> None:
    run_dir = tmp_path / "run_uci_credit_default"
    data_path = write_uci_credit_default_dataset(tmp_path / "uci_credit_default.csv")

    assert main(
        [
            "run",
            "--run-dir",
            str(run_dir),
            "--data-path",
            str(data_path),
            "--text",
            "Predict default_flag from the credit history and billing columns. Do everything on your own.",
            "--format",
            "json",
        ]
    ) == 0

    payload = json.loads(capsys.readouterr().out)
    assert payload["status"] == "ok"
    assert payload["run_summary"]["decision"]["task_type"] in {
        "binary_classification",
        "fraud_detection",
        "anomaly_detection",
    }
    assert payload["run_summary"]["data"]["row_count"] == 5000


def test_cli_run_supports_uci_ai4i_predictive_maintenance_dataset(tmp_path: Path, capsys) -> None:
    run_dir = tmp_path / "run_uci_ai4i"
    data_path = write_uci_ai4i_machine_failure_dataset(tmp_path / "uci_ai4i_machine_failure.csv")

    assert main(
        [
            "run",
            "--run-dir",
            str(run_dir),
            "--data-path",
            str(data_path),
            "--text",
            "Predict machine_failure from the maintenance sensor columns. Do everything on your own.",
            "--format",
            "json",
        ]
    ) == 0

    payload = json.loads(capsys.readouterr().out)
    assert payload["status"] == "ok"
    assert payload["run_summary"]["decision"]["task_type"] == "binary_classification"
    assert payload["run_summary"]["data"]["row_count"] == 3000
