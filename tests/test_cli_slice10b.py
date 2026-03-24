import json
from pathlib import Path

import pytest

pytest.importorskip("sklearn.datasets")

from relaytic.interoperability.service import relaytic_show_run
from relaytic.ui.cli import main

from tests.public_datasets import write_public_breast_cancer_dataset


def test_cli_run_materializes_slice10b_contracts_and_host_surfaces(tmp_path: Path, capsys) -> None:
    run_dir = tmp_path / "profiles_public_binary"
    data_path = write_public_breast_cancer_dataset(tmp_path / "profiles_public_breast_cancer.csv")

    assert main(
        [
            "run",
            "--run-dir",
            str(run_dir),
            "--data-path",
            str(data_path),
            "--text",
            "Do everything on your own. Classify diagnosis_flag from the measurement columns.",
            "--format",
            "json",
        ]
    ) == 0
    payload = json.loads(capsys.readouterr().out)

    contracts = dict(payload["run_summary"].get("contracts", {}))
    profiles = dict(payload["run_summary"].get("profiles", {}))
    assert payload["status"] == "ok"
    assert contracts["quality_gate_status"] in {"pass", "conditional_pass", "fail"}
    assert contracts["max_trials"] >= 1
    assert contracts["estimated_trials_consumed"] >= 1
    assert profiles["operator_profile_name"]
    assert profiles["lab_profile_name"]

    for filename in (
        "quality_contract.json",
        "quality_gate_report.json",
        "budget_contract.json",
        "budget_consumption_report.json",
        "operator_profile.json",
        "lab_operating_profile.json",
    ):
        assert (run_dir / filename).exists(), filename

    assert main(["profiles", "show", "--run-dir", str(run_dir), "--format", "json"]) == 0
    profiles_payload = json.loads(capsys.readouterr().out)
    assert profiles_payload["status"] == "ok"
    assert profiles_payload["profiles"]["quality_gate_status"] == contracts["quality_gate_status"]

    assert main(["assist", "show", "--run-dir", str(run_dir), "--format", "json"]) == 0
    assist_payload = json.loads(capsys.readouterr().out)
    assert assist_payload["run_summary"]["contracts"]["quality_gate_status"] == contracts["quality_gate_status"]
    assert assist_payload["run_summary"]["profiles"]["operator_profile_name"] == profiles["operator_profile_name"]

    interop_payload = relaytic_show_run(run_dir=str(run_dir))
    assert interop_payload["surface_payload"]["run_summary"]["contracts"]["quality_gate_status"] == contracts["quality_gate_status"]
