import csv
import json
from pathlib import Path

from relaytic.modeling import run_inference_from_artifacts
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


def test_cli_plan_create_writes_slice05_artifacts_and_preserves_upstream_manifest_entries(tmp_path: Path) -> None:
    run_dir = tmp_path / "run_slice05_cli"
    data_path = _write_dataset(tmp_path / "slice05_cli.csv")

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
            "--run-id",
            "slice05-cli-alpha",
            "--label",
            "stage=slice05",
        ]
    ) == 0
    assert main(["plan", "create", "--run-dir", str(run_dir), "--data-path", str(data_path)]) == 0

    manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
    plan = json.loads((run_dir / "plan.json").read_text(encoding="utf-8"))

    for filename in [
        "plan.json",
        "alternatives.json",
        "hypotheses.json",
        "experiment_priority_report.json",
        "marginal_value_of_next_experiment.json",
    ]:
        assert (run_dir / filename).exists(), filename

    assert manifest["run_id"] == "slice05-cli-alpha"
    assert manifest["labels"]["stage"] == "slice05"
    assert any(item["path"] == "intake_record.json" and item["exists"] is True for item in manifest["entries"])
    assert any(item["path"] == "dataset_profile.json" and item["exists"] is True for item in manifest["entries"])
    assert any(item["path"] == "plan.json" and item["required"] is True for item in manifest["entries"])
    assert not any(item["path"] == "model_params.json" and item["exists"] is True for item in manifest["entries"])
    assert plan["selected_route_id"] == "temporal_calibrated_classifier_route"
    assert plan["builder_handoff"]["feature_columns"] == ["sensor_a", "sensor_b"]


def test_cli_plan_run_builds_model_artifacts_and_supports_inference(tmp_path: Path) -> None:
    run_dir = tmp_path / "run_slice05_execute"
    data_path = _write_dataset(tmp_path / "slice05_execute.csv")

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
    assert main(["plan", "run", "--run-dir", str(run_dir), "--data-path", str(data_path)]) == 0

    manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
    plan = json.loads((run_dir / "plan.json").read_text(encoding="utf-8"))

    assert (run_dir / "model_params.json").exists()
    assert plan["execution_summary"]["status"] == "ok"
    assert plan["execution_summary"]["selected_model_family"]
    assert any(item["path"] == "model_params.json" and item["required"] is True for item in manifest["entries"])
    assert any(item["path"] == "checkpoints" and item["exists"] is True for item in manifest["entries"])
    assert any("ckpt_" in item["path"] for item in manifest["entries"])

    inference = run_inference_from_artifacts(
        data_path=str(data_path),
        run_dir=str(run_dir),
    )

    assert inference["status"] == "ok"
    assert inference["prediction_count"] == 15


def test_cli_plan_run_requires_overwrite_when_slice05_or_model_artifacts_exist(tmp_path: Path) -> None:
    run_dir = tmp_path / "run_slice05_overwrite"
    data_path = _write_dataset(tmp_path / "slice05_overwrite.csv")

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
    assert main(["plan", "run", "--run-dir", str(run_dir), "--data-path", str(data_path)]) == 0
    try:
        main(["plan", "run", "--run-dir", str(run_dir), "--data-path", str(data_path)])
    except SystemExit as exc:
        assert exc.code == 2
        return
    raise AssertionError("Expected parser failure when overwriting Slice 05 artifacts without --overwrite.")
