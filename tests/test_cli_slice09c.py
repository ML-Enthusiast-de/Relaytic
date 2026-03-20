import csv
import json
from pathlib import Path

from relaytic.ui.cli import main


def _write_regression_dataset(path: Path, *, count: int) -> Path:
    rows = [["sensor_a", "sensor_b", "quality_score", "future_quality_score"]]
    for index in range(count):
        sensor_a = 10.0 + index
        sensor_b = 100.0 + index * 1.5
        quality = round(0.4 * sensor_a + 0.015 * sensor_b, 5)
        future_quality = round(quality + 0.25, 5)
        rows.append([sensor_a, sensor_b, quality, future_quality])
    with path.open("w", newline="", encoding="utf-8") as handle:
        csv.writer(handle).writerows(rows)
    return path


def test_cli_autonomy_run_uses_larger_local_dataset_for_retrain_pass(tmp_path: Path, capsys) -> None:
    run_dir = tmp_path / "autonomy_retrain"
    data_path = _write_regression_dataset(tmp_path / "autonomy_retrain.csv", count=40)
    _write_regression_dataset(tmp_path / "autonomy_retrain_more_rows.csv", count=80)

    assert main(
        [
            "run",
            "--run-dir",
            str(run_dir),
            "--data-path",
            str(data_path),
            "--text",
            "Do everything on your own. Estimate quality_score from sensor_a and sensor_b. Do not use future_quality_score.",
            "--format",
            "json",
        ]
    ) == 0
    capsys.readouterr()

    retrain_path = run_dir / "retrain_decision.json"
    retrain_payload = json.loads(retrain_path.read_text(encoding="utf-8"))
    retrain_payload["action"] = "retrain"
    retrain_payload["reason_codes"] = ["test_forced_retrain"]
    retrain_path.write_text(json.dumps(retrain_payload, indent=2), encoding="utf-8")

    assert main(
        [
            "autonomy",
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
    assert payload["autonomy"]["selected_action"] == "run_retrain_pass"
    assert payload["bundle"]["autonomy_round_report"]["local_data_candidates"]
    assert payload["bundle"]["challenger_queue"]["branches"][0]["data_path"].endswith("autonomy_retrain_more_rows.csv")

    for filename in (
        "autonomy_loop_state.json",
        "autonomy_round_report.json",
        "challenger_queue.json",
        "branch_outcome_matrix.json",
        "retrain_run_request.json",
        "recalibration_run_request.json",
        "champion_lineage.json",
        "loop_budget_report.json",
    ):
        assert (run_dir / filename).exists(), filename

    assert main(["autonomy", "show", "--run-dir", str(run_dir), "--format", "json"]) == 0
    show_payload = json.loads(capsys.readouterr().out)
    assert show_payload["status"] == "ok"
    assert show_payload["autonomy"]["selected_action"] == "run_retrain_pass"
