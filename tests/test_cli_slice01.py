import json
from pathlib import Path

import yaml

from relaytic.ui.cli import main


def test_cli_policy_resolve_writes_output(tmp_path: Path) -> None:
    config = tmp_path / "policy.yaml"
    config.write_text("project:\n  name: relaytic-cli\n", encoding="utf-8")
    output = tmp_path / "run" / "policy_resolved.yaml"

    exit_code = main(["policy", "resolve", "--config", str(config), "--output", str(output)])

    assert exit_code == 0
    payload = yaml.safe_load(output.read_text(encoding="utf-8"))
    assert payload["policy"]["mandate"]["enabled"] is True
    assert payload["source_format"] == "legacy_top_level"


def test_cli_manifest_init_writes_manifest(tmp_path: Path) -> None:
    run_dir = tmp_path / "run_cli"
    artifact = run_dir / "policy_resolved.yaml"
    run_dir.mkdir()
    artifact.write_text("policy:\n  mode: local\n", encoding="utf-8")

    exit_code = main(
        [
            "manifest",
            "init",
            "--run-dir",
            str(run_dir),
            "--run-id",
            "cli-run",
            "--policy-source",
            str(artifact),
            "--label",
            "stage=slice01",
            "--entry",
            "policy_resolved.yaml",
        ]
    )

    manifest_path = run_dir / "manifest.json"
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert exit_code == 0
    assert payload["run_id"] == "cli-run"
    assert payload["labels"]["stage"] == "slice01"


def test_cli_manifest_init_rejects_invalid_label(tmp_path: Path) -> None:
    try:
        main(["manifest", "init", "--run-dir", str(tmp_path / "bad"), "--label", "badlabel"])
    except SystemExit as exc:
        assert exc.code == 2
        return
    raise AssertionError("Expected parser failure for invalid label syntax.")
