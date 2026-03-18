import csv
import json
from pathlib import Path

from relaytic.ui.cli import main


def _write_dataset(path: Path) -> Path:
    rows = [
        ["timestamp", "line_id", "batch_id", "sensor_a", "sensor_b", "quality_score", "future_quality"],
        ["2025-01-01T00:00:00", "L1", "B001", 10.0, 100.0, 0.50, 0.60],
        ["2025-01-01T00:01:00", "L1", "B002", 11.0, 101.0, 0.52, 0.61],
        ["2025-01-01T00:02:00", "L2", "B003", 12.0, 102.0, 0.55, 0.64],
        ["2025-01-01T00:03:00", "L2", "B004", 13.0, 103.0, 0.57, 0.66],
        ["2025-01-01T00:04:00", "L1", "B005", 14.0, 104.0, 0.60, 0.68],
        ["2025-01-01T00:05:00", "L1", "B006", 15.0, 105.0, 0.62, 0.70],
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerows(rows)
    return path


def test_cli_investigate_writes_slice03_artifacts_and_manifest(tmp_path: Path) -> None:
    run_dir = tmp_path / "run_slice03"
    data_path = _write_dataset(tmp_path / "dataset.csv")

    exit_code = main(
        [
            "investigate",
            "--run-dir",
            str(run_dir),
            "--data-path",
            str(data_path),
            "--run-id",
            "slice03-alpha",
            "--label",
            "stage=slice03",
        ]
    )

    assert exit_code == 0
    for filename in [
        "policy_resolved.yaml",
        "lab_mandate.json",
        "work_preferences.json",
        "run_brief.json",
        "data_origin.json",
        "domain_brief.json",
        "task_brief.json",
        "dataset_profile.json",
        "domain_memo.json",
        "objective_hypotheses.json",
        "focus_debate.json",
        "focus_profile.json",
        "optimization_profile.json",
        "feature_strategy_profile.json",
        "manifest.json",
    ]:
        assert (run_dir / filename).exists(), filename
    manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["run_id"] == "slice03-alpha"
    assert manifest["labels"]["stage"] == "slice03"
    assert any(item["path"] == "dataset_profile.json" and item["required"] is True for item in manifest["entries"])
    focus_profile = json.loads((run_dir / "focus_profile.json").read_text(encoding="utf-8"))
    assert focus_profile["primary_objective"]


def test_cli_investigate_requires_overwrite_for_existing_slice03_outputs(tmp_path: Path) -> None:
    run_dir = tmp_path / "run_slice03_overwrite"
    data_path = _write_dataset(tmp_path / "dataset_overwrite.csv")

    assert main(["investigate", "--run-dir", str(run_dir), "--data-path", str(data_path)]) == 0
    try:
        main(["investigate", "--run-dir", str(run_dir), "--data-path", str(data_path)])
    except SystemExit as exc:
        assert exc.code == 2
        return
    raise AssertionError("Expected parser failure when overwriting Slice 03 artifacts.")
