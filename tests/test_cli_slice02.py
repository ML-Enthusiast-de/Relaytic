import json
from pathlib import Path

from relaytic.ui.cli import main


def test_cli_mandate_init_writes_artifacts_and_manifest(tmp_path: Path) -> None:
    run_dir = tmp_path / "run_mandate"
    exit_code = main(
        [
            "mandate",
            "init",
            "--run-dir",
            str(run_dir),
            "--lab-value",
            "protect local-first defaults",
            "--hard-constraint",
            "never use remote APIs by default",
            "--target-column",
            "yield",
        ]
    )
    assert exit_code == 0
    assert (run_dir / "lab_mandate.json").exists()
    assert (run_dir / "work_preferences.json").exists()
    assert (run_dir / "run_brief.json").exists()
    manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
    assert any(item["path"] == "lab_mandate.json" and item["exists"] is True for item in manifest["entries"])


def test_cli_context_init_writes_artifacts_and_manifest(tmp_path: Path) -> None:
    run_dir = tmp_path / "run_context"
    exit_code = main(
        [
            "context",
            "init",
            "--run-dir",
            str(run_dir),
            "--source-name",
            "pilot-batch",
            "--system-name",
            "distillation-column",
            "--problem-statement",
            "Predict off-spec batches early.",
            "--task-success-criterion",
            "Reduce late-stage scrap decisions.",
        ]
    )
    assert exit_code == 0
    assert (run_dir / "data_origin.json").exists()
    assert (run_dir / "domain_brief.json").exists()
    assert (run_dir / "task_brief.json").exists()
    manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
    assert any(item["path"] == "task_brief.json" and item["exists"] is True for item in manifest["entries"])


def test_cli_foundation_init_writes_all_slice02_outputs(tmp_path: Path) -> None:
    run_dir = tmp_path / "run_foundation"
    exit_code = main(
        [
            "foundation",
            "init",
            "--run-dir",
            str(run_dir),
            "--run-id",
            "foundation-alpha",
            "--label",
            "stage=slice02",
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
        "manifest.json",
    ]:
        assert (run_dir / filename).exists(), filename
    manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["run_id"] == "foundation-alpha"
    assert manifest["labels"]["stage"] == "slice02"


def test_cli_mandate_show_prints_bundle(tmp_path: Path, capsys) -> None:
    run_dir = tmp_path / "run_show"
    assert main(["foundation", "init", "--run-dir", str(run_dir)]) == 0
    exit_code = main(["mandate", "show", "--run-dir", str(run_dir)])
    output = capsys.readouterr().out
    assert exit_code == 0
    assert "lab_mandate" in output
    assert "run_brief" in output


def test_cli_context_init_requires_overwrite_for_existing_artifacts(tmp_path: Path) -> None:
    run_dir = tmp_path / "run_overwrite"
    assert main(["context", "init", "--run-dir", str(run_dir)]) == 0
    try:
        main(["context", "init", "--run-dir", str(run_dir)])
    except SystemExit as exc:
        assert exc.code == 2
        return
    raise AssertionError("Expected parser failure when overwriting existing context artifacts.")


def test_cli_context_init_reuses_existing_policy_resolved(tmp_path: Path) -> None:
    run_dir = tmp_path / "run_reuse_policy"
    canonical = tmp_path / "canonical.yaml"
    canonical.write_text(
        "policy:\n  context:\n    enabled: false\n    require_provenance: false\n",
        encoding="utf-8",
    )
    legacy = tmp_path / "legacy.yaml"
    legacy.write_text("project:\n  name: relaytic-legacy\n", encoding="utf-8")

    assert main(["policy", "resolve", "--config", str(canonical), "--output", str(run_dir / "policy_resolved.yaml")]) == 0
    assert main(["context", "init", "--run-dir", str(run_dir), "--config", str(legacy)]) == 0

    payload = json.loads((run_dir / "data_origin.json").read_text(encoding="utf-8"))
    assert payload["controls"]["enabled"] is False
    assert payload["controls"]["require_provenance"] is False
