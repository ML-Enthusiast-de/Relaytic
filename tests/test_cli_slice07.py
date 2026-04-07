import csv
import json
from pathlib import Path

import relaytic.ui.cli as cli_module
from relaytic.ui.cli import main


def _write_dataset(path: Path) -> Path:
    rows = [
        ["timestamp", "sensor_a", "sensor_b", "failure_flag", "future_failure_flag", "post_inspection_flag"],
        ["2025-01-01T00:00:00", 10.0, 100.0, 0, 0, 0],
        ["2025-01-01T00:01:00", 11.0, 102.0, 0, 0, 0],
        ["2025-01-01T00:02:00", 12.0, 101.0, 1, 1, 1],
        ["2025-01-01T00:03:00", 13.0, 103.0, 0, 0, 0],
        ["2025-01-01T00:04:00", 14.0, 105.0, 1, 1, 1],
        ["2025-01-01T00:05:00", 15.0, 104.0, 0, 0, 0],
        ["2025-01-01T00:06:00", 16.0, 106.0, 1, 1, 1],
        ["2025-01-01T00:07:00", 17.0, 108.0, 0, 0, 0],
        ["2025-01-01T00:08:00", 18.0, 107.0, 1, 1, 1],
        ["2025-01-01T00:09:00", 19.0, 109.0, 0, 0, 0],
        ["2025-01-01T00:10:00", 20.0, 110.0, 1, 1, 1],
        ["2025-01-01T00:11:00", 21.0, 111.0, 0, 0, 0],
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        csv.writer(handle).writerows(rows)
    return path


def test_cli_run_writes_completion_artifacts_and_summary_surface(tmp_path: Path, capsys) -> None:
    run_dir = tmp_path / "run_slice07_access"
    data_path = _write_dataset(tmp_path / "slice07_access.csv")

    assert main(
        [
            "run",
            "--run-dir",
            str(run_dir),
            "--data-path",
            str(data_path),
            "--text",
            "Do everything on your own. Predict failure_flag. Do not use future_failure_flag or post_inspection_flag.",
            "--format",
            "json",
        ]
    ) == 0

    payload = json.loads(capsys.readouterr().out)
    assert payload["status"] == "ok"
    assert payload["completion"]["action"]
    assert payload["run_summary"]["completion"]["action"] == payload["completion"]["action"]
    assert (run_dir / "completion_decision.json").exists()
    assert (run_dir / "run_state.json").exists()
    assert (run_dir / "blocking_analysis.json").exists()
    assert (run_dir / "next_action_queue.json").exists()


def test_cli_status_and_completion_review_surfaces_are_machine_readable(tmp_path: Path, capsys) -> None:
    run_dir = tmp_path / "run_slice07_status"
    data_path = _write_dataset(tmp_path / "slice07_status.csv")

    assert main(
        [
            "run",
            "--run-dir",
            str(run_dir),
            "--data-path",
            str(data_path),
            "--text",
            "Do everything on your own. Predict failure_flag. Do not use future_failure_flag or post_inspection_flag.",
            "--format",
            "json",
        ]
    ) == 0
    capsys.readouterr()

    assert main(["status", "--run-dir", str(run_dir), "--format", "json"]) == 0
    status_payload = json.loads(capsys.readouterr().out)
    assert status_payload["status"] == "ok"
    assert status_payload["completion"]["current_stage"] == "completion_reviewed"
    assert status_payload["completion"]["action"]
    assert status_payload["completion"]["blocking_layer"] is not None

    assert main(
        [
            "completion",
            "review",
            "--run-dir",
            str(run_dir),
            "--overwrite",
            "--format",
            "json",
        ]
    ) == 0
    review_payload = json.loads(capsys.readouterr().out)
    assert review_payload["status"] == "ok"
    assert review_payload["completion"]["action"]
    assert review_payload["bundle"]["next_action_queue"]["actions"]


def test_cli_completion_review_reuses_existing_stage_artifacts(tmp_path: Path, capsys, monkeypatch) -> None:
    run_dir = tmp_path / "run_slice07_cached_completion"
    data_path = _write_dataset(tmp_path / "slice07_cached_completion.csv")

    assert main(
        [
            "run",
            "--run-dir",
            str(run_dir),
            "--data-path",
            str(data_path),
            "--text",
            "Do everything on your own. Predict failure_flag. Do not use future_failure_flag or post_inspection_flag.",
            "--format",
            "json",
        ]
    ) == 0
    capsys.readouterr()

    def _unexpected_rerun(*args: object, **kwargs: object) -> None:
        raise AssertionError("completion review should reuse existing stage artifacts for completed runs")

    monkeypatch.setattr(cli_module, "_run_memory_phase", _unexpected_rerun)
    monkeypatch.setattr(cli_module, "_run_intelligence_phase", _unexpected_rerun)
    monkeypatch.setattr(cli_module, "_run_research_phase", _unexpected_rerun)
    monkeypatch.setattr(cli_module, "_run_benchmark_phase", _unexpected_rerun)
    monkeypatch.setattr(cli_module, "_run_profiles_phase", _unexpected_rerun)
    monkeypatch.setattr(cli_module, "_run_decision_phase", _unexpected_rerun)

    assert main(
        [
            "completion",
            "review",
            "--run-dir",
            str(run_dir),
            "--overwrite",
            "--format",
            "json",
        ]
    ) == 0
    review_payload = json.loads(capsys.readouterr().out)
    assert review_payload["status"] == "ok"
    assert review_payload["completion"]["current_stage"] == "completion_reviewed"


def test_cli_show_human_output_includes_completion_section(tmp_path: Path, capsys) -> None:
    run_dir = tmp_path / "run_slice07_show"
    data_path = _write_dataset(tmp_path / "slice07_show.csv")

    assert main(
        [
            "run",
            "--run-dir",
            str(run_dir),
            "--data-path",
            str(data_path),
            "--text",
            "Do everything on your own. Predict failure_flag. Do not use future_failure_flag or post_inspection_flag.",
            "--format",
            "json",
        ]
    ) == 0
    capsys.readouterr()

    assert main(["show", "--run-dir", str(run_dir), "--format", "human"]) == 0
    output = capsys.readouterr().out
    assert "## Completion" in output
    assert "Blocking layer" in output
    assert "Current stage" in output
