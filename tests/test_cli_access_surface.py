import csv
import json
from pathlib import Path

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
        ["2025-01-01T00:12:00", 22.0, 112.0, 1, 1, 1],
        ["2025-01-01T00:13:00", 23.0, 113.0, 0, 0, 0],
        ["2025-01-01T00:14:00", 24.0, 114.0, 1, 1, 1],
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        csv.writer(handle).writerows(rows)
    return path


def test_cli_run_executes_end_to_end_and_writes_access_artifacts(tmp_path: Path, capsys) -> None:
    run_dir = tmp_path / "run_access"
    data_path = _write_dataset(tmp_path / "run_access.csv")

    assert main(
        [
            "run",
            "--run-dir",
            str(run_dir),
            "--data-path",
            str(data_path),
            "--text",
            "Predict failure_flag. Do not use future_failure_flag or post_inspection_flag.",
            "--run-id",
            "access-alpha",
            "--label",
            "stage=access",
            "--format",
            "json",
        ]
    ) == 0

    payload = json.loads(capsys.readouterr().out)
    manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))

    assert payload["status"] == "ok"
    assert payload["run_summary"]["decision"]["selected_model_family"]
    assert payload["run_summary"]["decision"]["selected_route_id"] == "temporal_calibrated_classifier_route"
    assert payload["run_summary"]["request"]["source"] == "inline_text"
    assert payload["run_summary"]["evidence"]["provisional_recommendation"]
    assert (run_dir / "run_summary.json").exists()
    assert (run_dir / "reports" / "summary.md").exists()
    assert (run_dir / "reports" / "decision_memo.md").exists()
    assert manifest["run_id"] == "access-alpha"
    assert manifest["labels"]["stage"] == "access"
    assert any(item["path"] == "run_summary.json" and item["required"] is True for item in manifest["entries"])
    assert any(item["path"] == "reports/summary.md" and item["required"] is True for item in manifest["entries"])
    assert any(item["path"] == "leaderboard.csv" and item["required"] is True for item in manifest["entries"])


def test_cli_run_without_text_uses_autonomous_default_and_show_renders_human_output(tmp_path: Path, capsys) -> None:
    run_dir = tmp_path / "run_access_default"
    data_path = _write_dataset(tmp_path / "run_access_default.csv")

    assert main(
        [
            "run",
            "--run-dir",
            str(run_dir),
            "--data-path",
            str(data_path),
            "--format",
            "json",
        ]
    ) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["run_summary"]["request"]["source"] == "autonomous_default"

    assert main(["show", "--run-dir", str(run_dir), "--format", "human"]) == 0
    output = capsys.readouterr().out
    assert "# Relaytic Run Summary" in output
    assert "Model:" in output
    assert "Recommended next experiment" in output
    assert "Provisional recommendation" in output


def test_cli_predict_surface_runs_inference_from_run_dir(tmp_path: Path, capsys) -> None:
    run_dir = tmp_path / "run_predict"
    data_path = _write_dataset(tmp_path / "run_predict.csv")

    assert main(
        [
            "run",
            "--run-dir",
            str(run_dir),
            "--data-path",
            str(data_path),
            "--text",
            "Predict failure_flag. Do not use future_failure_flag or post_inspection_flag.",
            "--format",
            "json",
        ]
    ) == 0
    capsys.readouterr()

    assert main(
        [
            "predict",
            "--run-dir",
            str(run_dir),
            "--data-path",
            str(data_path),
            "--format",
            "json",
        ]
    ) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["status"] == "ok"
    assert payload["prediction_count"] == 15
    assert payload["model_name"]


def test_cli_show_bootstraps_summary_for_existing_plan_run_dirs(tmp_path: Path, capsys) -> None:
    run_dir = tmp_path / "legacy_plan_run"
    data_path = _write_dataset(tmp_path / "legacy_plan_run.csv")

    assert main(
        [
            "intake",
            "interpret",
            "--run-dir",
            str(run_dir),
            "--data-path",
            str(data_path),
            "--text",
            "Predict failure_flag. Do not use future_failure_flag or post_inspection_flag.",
        ]
    ) == 0
    capsys.readouterr()
    assert main(["plan", "run", "--run-dir", str(run_dir), "--data-path", str(data_path)]) == 0
    capsys.readouterr()

    assert not (run_dir / "run_summary.json").exists()
    assert main(["show", "--run-dir", str(run_dir), "--format", "json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["status"] == "ok"
    assert (run_dir / "run_summary.json").exists()
    assert (run_dir / "reports" / "summary.md").exists()
    assert payload["run_summary"]["decision"]["selected_model_family"]
    assert payload["run_summary"]["evidence"]["experiment_count"] == 0
