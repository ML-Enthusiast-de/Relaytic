import json
from pathlib import Path

import pytest

pytest.importorskip("sklearn.datasets")

from relaytic.ui.cli import main

from tests.public_datasets import write_public_breast_cancer_dataset


def test_cli_memory_retrieve_enriches_public_dataset_run_with_analogs(tmp_path: Path, capsys) -> None:
    data_path = write_public_breast_cancer_dataset(tmp_path / "public_breast_cancer.csv")
    prior_run_dir = tmp_path / "prior_public_breast"
    current_run_dir = tmp_path / "current_public_breast"

    assert main(
        [
            "run",
            "--run-dir",
            str(prior_run_dir),
            "--data-path",
            str(data_path),
            "--text",
            "Classify diagnosis_flag from the measurement columns. Do everything on your own.",
            "--format",
            "json",
        ]
    ) == 0
    capsys.readouterr()

    assert main(
        [
            "run",
            "--run-dir",
            str(current_run_dir),
            "--data-path",
            str(data_path),
            "--text",
            "Classify diagnosis_flag from the measurement columns. Do everything on your own.",
            "--format",
            "json",
        ]
    ) == 0
    capsys.readouterr()

    assert main(
        [
            "memory",
            "retrieve",
            "--run-dir",
            str(current_run_dir),
            "--search-root",
            str(tmp_path),
            "--format",
            "json",
        ]
    ) == 0
    memory_payload = json.loads(capsys.readouterr().out)

    assert memory_payload["status"] == "ok"
    assert memory_payload["memory"]["analog_count"] >= 1
    assert (current_run_dir / "reflection_memory.json").exists()
    assert (current_run_dir / "memory_flush_report.json").exists()

    assert main(["memory", "show", "--run-dir", str(current_run_dir), "--format", "json"]) == 0
    memory_show_payload = json.loads(capsys.readouterr().out)
    assert memory_show_payload["status"] == "ok"
    assert memory_show_payload["bundle"]["memory_retrieval"]["status"] == "retrieval_completed"

    assert main(["show", "--run-dir", str(current_run_dir), "--format", "json"]) == 0
    show_payload = json.loads(capsys.readouterr().out)
    memory = show_payload["run_summary"]["memory"]

    assert memory["analog_count"] >= 1
    assert "prior_public_breast" in memory["top_analog_run_ids"]
    assert memory["flush_stage"] == "autonomy_reviewed"
