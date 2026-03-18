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


def test_cli_run_now_writes_slice06_evidence_outputs(tmp_path: Path, capsys) -> None:
    run_dir = tmp_path / "run_access_slice06"
    data_path = _write_dataset(tmp_path / "run_access_slice06.csv")

    assert main(
        [
            "run",
            "--run-dir",
            str(run_dir),
            "--data-path",
            str(data_path),
            "--text",
            "Do everything on your own. Predict failure_flag. Do not use future or post-inspection columns.",
            "--format",
            "json",
        ]
    ) == 0

    payload = json.loads(capsys.readouterr().out)
    run_summary = payload["run_summary"]

    assert payload["status"] == "ok"
    assert payload["evidence"]["provisional_recommendation"]
    assert run_summary["evidence"]["provisional_recommendation"]
    assert run_summary["evidence"]["experiment_count"] >= 2
    assert (run_dir / "leaderboard.csv").exists()
    assert (run_dir / "experiment_registry.json").exists()
    assert (run_dir / "challenger_report.json").exists()
    assert (run_dir / "ablation_report.json").exists()
    assert (run_dir / "audit_report.json").exists()
    assert (run_dir / "belief_update.json").exists()
    assert (run_dir / "reports" / "technical_report.md").exists()
    assert (run_dir / "reports" / "decision_memo.md").exists()


def test_cli_evidence_show_renders_decision_memo_and_json_surface(tmp_path: Path, capsys) -> None:
    run_dir = tmp_path / "run_evidence_show"
    data_path = _write_dataset(tmp_path / "run_evidence_show.csv")

    assert main(
        [
            "evidence",
            "run",
            "--run-dir",
            str(run_dir),
            "--data-path",
            str(data_path),
            "--format",
            "json",
        ]
    ) == 0
    capsys.readouterr()

    assert main(["evidence", "show", "--run-dir", str(run_dir), "--format", "human"]) == 0
    human_output = capsys.readouterr().out
    assert "# Relaytic Decision Memo" in human_output
    assert "Provisional recommendation" in human_output

    assert main(["evidence", "show", "--run-dir", str(run_dir), "--format", "json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["status"] == "ok"
    assert payload["evidence"]["recommended_action"]
    assert payload["bundle"]["audit_report"]["provisional_recommendation"]
