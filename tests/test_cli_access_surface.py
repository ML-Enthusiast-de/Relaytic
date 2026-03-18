import csv
import json
from pathlib import Path

from relaytic.ui.cli import main


def _write_dataset(path: Path, *, count: int = 15) -> Path:
    rows = [["timestamp", "sensor_a", "sensor_b", "failure_flag", "future_failure_flag", "post_inspection_flag"]]
    for index in range(count):
        failure_flag = index % 2
        rows.append(
            [
                f"2025-01-01T00:{index:02d}:00",
                10.0 + index,
                100.0 + index + (index % 3),
                failure_flag,
                failure_flag,
                failure_flag,
            ]
        )
    with path.open("w", newline="", encoding="utf-8") as handle:
        csv.writer(handle).writerows(rows)
    return path


def _write_regression_dataset(path: Path, *, count: int = 15) -> Path:
    rows = [["sensor_a", "sensor_b", "quality_score", "future_quality_score"]]
    for index in range(count):
        sensor_a = 10.0 + index
        sensor_b = 100.0 + index * 1.5
        quality = round(0.35 * sensor_a + 0.02 * sensor_b, 5)
        future_quality = round(quality + 0.2, 5)
        rows.append([sensor_a, sensor_b, quality, future_quality])
    with path.open("w", newline="", encoding="utf-8") as handle:
        csv.writer(handle).writerows(rows)
    return path


def _write_fraud_dataset(path: Path, *, count: int = 18) -> Path:
    rows = [["transaction_id", "amount_norm", "device_risk", "velocity_score", "fraud_flag"]]
    for index in range(count):
        fraud = 1 if index % 4 == 0 else 0
        amount = 0.92 if fraud else 0.18 + (index % 5) * 0.04
        device = 0.96 if fraud else 0.12 + (index % 4) * 0.05
        velocity = 0.9 if fraud else 0.15 + (index % 3) * 0.05
        rows.append([f"T{index:04d}", round(amount, 5), round(device, 5), round(velocity, 5), fraud])
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


def test_cli_run_overwrite_refreshes_upstream_artifacts(tmp_path: Path, capsys) -> None:
    run_dir = tmp_path / "run_access_overwrite"
    data_path = _write_dataset(tmp_path / "run_access_overwrite.csv", count=15)

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

    _write_dataset(data_path, count=18)
    assert main(
        [
            "run",
            "--run-dir",
            str(run_dir),
            "--data-path",
            str(data_path),
            "--text",
            "Do everything on your own. Predict failure_flag. Do not use future_failure_flag or post_inspection_flag.",
            "--overwrite",
            "--format",
            "json",
        ]
    ) == 0
    payload = json.loads(capsys.readouterr().out)
    dataset_profile = json.loads((run_dir / "dataset_profile.json").read_text(encoding="utf-8"))

    assert dataset_profile["row_count"] == 18
    assert payload["run_summary"]["data"]["row_count"] == 18


def test_cli_run_supports_regression_routes_end_to_end(tmp_path: Path, capsys) -> None:
    run_dir = tmp_path / "run_access_regression"
    data_path = _write_regression_dataset(tmp_path / "run_access_regression.csv")

    assert main(
        [
            "run",
            "--run-dir",
            str(run_dir),
            "--data-path",
            str(data_path),
            "--text",
            "Estimate quality_score from sensor_a and sensor_b. Do everything on your own. Do not use future_quality_score.",
            "--format",
            "json",
        ]
    ) == 0

    payload = json.loads(capsys.readouterr().out)
    plan = json.loads((run_dir / "plan.json").read_text(encoding="utf-8"))

    assert payload["run_summary"]["decision"]["task_type"] == "regression"
    assert plan["selected_route_id"] == "steady_state_tabular_regression_route"
    assert payload["run_summary"]["decision"]["selected_model_family"] in {
        "linear_ridge",
        "bagged_tree_ensemble",
        "boosted_tree_ensemble",
    }


def test_cli_run_supports_fraud_detection_routes_end_to_end(tmp_path: Path, capsys) -> None:
    run_dir = tmp_path / "run_access_fraud"
    data_path = _write_fraud_dataset(tmp_path / "run_access_fraud.csv")

    assert main(
        [
            "run",
            "--run-dir",
            str(run_dir),
            "--data-path",
            str(data_path),
            "--text",
            "Detect fraud_flag from transaction risk features. Do everything on your own.",
            "--format",
            "json",
        ]
    ) == 0

    payload = json.loads(capsys.readouterr().out)
    plan = json.loads((run_dir / "plan.json").read_text(encoding="utf-8"))

    assert payload["run_summary"]["decision"]["task_type"] == "fraud_detection"
    assert payload["run_summary"]["intent"]["domain_archetype"] == "fraud_risk"
    assert plan["primary_metric"] == "pr_auc"
