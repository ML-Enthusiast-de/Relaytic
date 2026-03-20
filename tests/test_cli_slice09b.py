import json
from pathlib import Path

import pytest

pytest.importorskip("sklearn.datasets")

from relaytic.ui.cli import main

from tests.public_datasets import (
    write_public_breast_cancer_dataset,
    write_public_diabetes_dataset,
)


def test_cli_runtime_surfaces_materialize_for_public_binary_run(tmp_path: Path, capsys) -> None:
    run_dir = tmp_path / "runtime_public_binary"
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
    assert payload["run_summary"]["decision"]["task_type"] == "binary_classification"
    assert payload["run_summary"]["runtime"]["event_count"] > 0
    assert payload["run_summary"]["runtime"]["denied_access_count"] >= 1
    assert payload["run_summary"]["runtime"]["active_specialist_count"] >= 8

    for filename in (
        "lab_event_stream.jsonl",
        "hook_execution_log.json",
        "run_checkpoint_manifest.json",
        "capability_profiles.json",
        "data_access_audit.json",
        "context_influence_report.json",
    ):
        assert (run_dir / filename).exists(), filename

    assert main(["runtime", "show", "--run-dir", str(run_dir), "--format", "json"]) == 0
    runtime_payload = json.loads(capsys.readouterr().out)
    assert runtime_payload["status"] == "ok"
    assert runtime_payload["runtime"]["current_stage"] == "autonomy"
    assert runtime_payload["runtime"]["event_count"] >= 10
    assert runtime_payload["runtime"]["write_hook_blocked_count"] >= 1

    assert main(["runtime", "events", "--run-dir", str(run_dir), "--limit", "8", "--format", "json"]) == 0
    events_payload = json.loads(capsys.readouterr().out)
    assert events_payload["status"] == "ok"
    assert events_payload["event_count"] >= len(events_payload["recent_events"])
    assert any(item["event_type"] == "stage_completed" for item in events_payload["recent_events"])

    assert main(["show", "--run-dir", str(run_dir), "--format", "json"]) == 0
    show_payload = json.loads(capsys.readouterr().out)
    assert show_payload["run_summary"]["runtime"]["event_count"] == runtime_payload["runtime"]["event_count"]


def test_cli_runtime_surfaces_materialize_for_public_regression_run(tmp_path: Path, capsys) -> None:
    run_dir = tmp_path / "runtime_public_regression"
    data_path = write_public_diabetes_dataset(tmp_path / "public_diabetes.csv")

    assert main(
        [
            "run",
            "--run-dir",
            str(run_dir),
            "--data-path",
            str(data_path),
            "--text",
            "Do everything on your own. Estimate disease_progression from the patient measurements.",
            "--format",
            "json",
        ]
    ) == 0
    payload = json.loads(capsys.readouterr().out)

    assert payload["status"] == "ok"
    assert payload["run_summary"]["decision"]["task_type"] == "regression"

    assert main(["runtime", "show", "--run-dir", str(run_dir), "--format", "json"]) == 0
    runtime_payload = json.loads(capsys.readouterr().out)

    assert runtime_payload["status"] == "ok"
    assert runtime_payload["runtime"]["current_stage"] == "autonomy"
    assert runtime_payload["runtime"]["checkpoint_count"] >= 4
    assert runtime_payload["runtime"]["denied_access_count"] >= 1
