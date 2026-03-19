import json
from pathlib import Path

import pytest

pytest.importorskip("sklearn.datasets")

from relaytic.ui.cli import main

from tests.public_datasets import write_public_breast_cancer_dataset


def test_cli_run_and_lifecycle_show_surface_public_dataset(tmp_path: Path, capsys) -> None:
    run_dir = tmp_path / "run_slice08_public"
    data_path = write_public_breast_cancer_dataset(tmp_path / "public_breast_cancer.csv")

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
    assert payload["status"] == "ok"
    assert payload["lifecycle"]["promotion_action"]
    assert payload["run_summary"]["lifecycle"]["promotion_action"]
    assert (run_dir / "champion_vs_candidate.json").exists()
    assert (run_dir / "recalibration_decision.json").exists()
    assert (run_dir / "retrain_decision.json").exists()
    assert (run_dir / "promotion_decision.json").exists()
    assert (run_dir / "rollback_decision.json").exists()

    assert main(["lifecycle", "show", "--run-dir", str(run_dir), "--format", "json"]) == 0
    lifecycle_payload = json.loads(capsys.readouterr().out)
    assert lifecycle_payload["status"] == "ok"
    assert lifecycle_payload["lifecycle"]["promotion_action"]
    assert lifecycle_payload["bundle"]["promotion_decision"]["action"]
