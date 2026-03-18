import csv
import json
from pathlib import Path

from relaytic.ui.cli import main


def _write_dataset(path: Path) -> Path:
    rows = [
        ["timestamp", "sensor_a", "failure_flag", "future_failure_flag", "post_inspection_flag"],
        ["2025-01-01T00:00:00", 10.0, 0, 0, 0],
        ["2025-01-01T00:01:00", 11.0, 1, 1, 1],
        ["2025-01-01T00:02:00", 12.0, 0, 0, 0],
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerows(rows)
    return path


def test_cli_intake_interpret_writes_slice04_artifacts_and_updates_foundation(tmp_path: Path) -> None:
    run_dir = tmp_path / "run_slice04"
    data_path = _write_dataset(tmp_path / "slice04.csv")

    exit_code = main(
        [
            "intake",
            "interpret",
            "--run-dir",
            str(run_dir),
            "--data-path",
            str(data_path),
            "--text",
            "Predict failure_flag. Do not use future_failure_flag or post_inspection_flag. Laptop CPU only.",
            "--run-id",
            "slice04-alpha",
            "--label",
            "stage=slice04",
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
        "intake_record.json",
        "autonomy_mode.json",
        "clarification_queue.json",
        "assumption_log.json",
        "context_interpretation.json",
        "context_constraints.json",
        "semantic_mapping.json",
        "manifest.json",
    ]:
        assert (run_dir / filename).exists(), filename

    task_brief = json.loads((run_dir / "task_brief.json").read_text(encoding="utf-8"))
    manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
    assert task_brief["target_column"] == "failure_flag"
    assert manifest["run_id"] == "slice04-alpha"
    assert manifest["labels"]["stage"] == "slice04"
    assert any(item["path"] == "intake_record.json" and item["required"] is True for item in manifest["entries"])
    assert any(item["path"] == "autonomy_mode.json" and item["required"] is True for item in manifest["entries"])
    assert any(item["path"] == "clarification_queue.json" and item["required"] is True for item in manifest["entries"])
    assert any(item["path"] == "assumption_log.json" and item["required"] is True for item in manifest["entries"])


def test_cli_intake_interpret_requires_overwrite_for_existing_slice04_outputs(tmp_path: Path) -> None:
    run_dir = tmp_path / "run_slice04_overwrite"
    data_path = _write_dataset(tmp_path / "slice04_overwrite.csv")

    assert main(
        [
            "intake",
            "interpret",
            "--run-dir",
            str(run_dir),
            "--data-path",
            str(data_path),
            "--text",
            "Predict failure_flag.",
        ]
    ) == 0
    try:
        main(
            [
                "intake",
                "interpret",
                "--run-dir",
                str(run_dir),
                "--data-path",
                str(data_path),
                "--text",
                "Predict failure_flag.",
            ]
        )
    except SystemExit as exc:
        assert exc.code == 2
        return
    raise AssertionError("Expected parser failure when overwriting Slice 04 intake artifacts.")


def test_cli_intake_show_and_investigate_preserve_intake_manifest_entries(tmp_path: Path, capsys) -> None:
    run_dir = tmp_path / "run_slice04_show"
    data_path = _write_dataset(tmp_path / "slice04_show.csv")

    assert main(
        [
            "intake",
            "interpret",
            "--run-dir",
            str(run_dir),
            "--data-path",
            str(data_path),
            "--text",
            "Predict failure_flag. Do not use future_failure_flag.",
        ]
    ) == 0
    assert main(["intake", "show", "--run-dir", str(run_dir)]) == 0
    output = capsys.readouterr().out
    assert "context_interpretation" in output
    assert main(["investigate", "--run-dir", str(run_dir), "--data-path", str(data_path)]) == 0
    manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
    assert any(item["path"] == "intake_record.json" and item["exists"] is True for item in manifest["entries"])


def test_cli_intake_questions_reports_optional_queue_and_assumptions(tmp_path: Path, capsys) -> None:
    run_dir = tmp_path / "run_slice04_questions"
    data_path = _write_dataset(tmp_path / "slice04_questions.csv")

    assert main(
        [
            "intake",
            "interpret",
            "--run-dir",
            str(run_dir),
            "--data-path",
            str(data_path),
            "--text",
            "Do everything on your own and find out the target from the data. Do not use future columns.",
        ]
    ) == 0
    assert main(["intake", "questions", "--run-dir", str(run_dir)]) == 0
    output = capsys.readouterr().out
    assert "clarification_queue" in output
    assert "assumption_log" in output
    assert "suppressed_by_autonomy" in output


def test_cli_intake_show_tolerates_legacy_slice04_runs_without_new_artifacts(tmp_path: Path, capsys) -> None:
    run_dir = tmp_path / "legacy_slice04"
    run_dir.mkdir(parents=True)
    for filename, payload in {
        "intake_record.json": {"schema_version": "relaytic.intake_record.v1"},
        "context_interpretation.json": {"schema_version": "relaytic.context_interpretation.v1"},
        "context_constraints.json": {"schema_version": "relaytic.context_constraints.v1"},
        "semantic_mapping.json": {"schema_version": "relaytic.semantic_mapping.v1"},
    }.items():
        (run_dir / filename).write_text(json.dumps(payload), encoding="utf-8")

    assert main(["intake", "show", "--run-dir", str(run_dir)]) == 0
    output = capsys.readouterr().out
    assert "intake_record" in output
    assert "context_interpretation" in output
