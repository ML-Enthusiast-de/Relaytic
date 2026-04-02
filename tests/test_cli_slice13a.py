from __future__ import annotations

import json
from pathlib import Path

from relaytic.ui.cli import main


def test_cli_release_safety_scan_rejects_leaky_bundle_and_show_reads_written_state(tmp_path: Path, capsys) -> None:
    bundle_dir = tmp_path / "bundle"
    state_dir = tmp_path / "release_state"
    bundle_dir.mkdir(parents=True, exist_ok=True)
    (bundle_dir / "README.md").write_text(
        "Leaky bundle path C:\\Users\\build-agent\\Desktop\\debug.txt\n",
        encoding="utf-8",
    )

    assert main(
        [
            "release-safety",
            "scan",
            "--target-path",
            str(bundle_dir),
            "--state-dir",
            str(state_dir),
            "--format",
            "json",
        ]
    ) == 1
    payload = json.loads(capsys.readouterr().out)

    assert payload["status"] == "error"
    assert payload["release_safety"]["finding_count"] >= 1
    assert (state_dir / "release_safety_scan.json").exists()

    assert main(
        [
            "release-safety",
            "show",
            "--state-dir",
            str(state_dir),
            "--format",
            "json",
        ]
    ) == 1
    show_payload = json.loads(capsys.readouterr().out)
    assert show_payload["status"] == "error"
    assert show_payload["bundle"]["sensitive_string_audit"]["finding_count"] >= 1


def test_cli_release_safety_scan_updates_latest_state_consumed_by_doctor(tmp_path: Path, capsys) -> None:
    bundle_dir = tmp_path / "clean_bundle"
    bundle_dir.mkdir(parents=True, exist_ok=True)
    (bundle_dir / "README.md").write_text("Release bundle\n", encoding="utf-8")

    assert main(
        [
            "release-safety",
            "scan",
            "--target-path",
            str(bundle_dir),
            "--state-dir",
            str(tmp_path / "release_state_clean"),
            "--format",
            "json",
        ]
    ) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["status"] == "ok"

    assert main(["doctor", "--expected-profile", "core", "--format", "json"]) == 0
    doctor = json.loads(capsys.readouterr().out)
    assert doctor["release_safety"]["status"] == "ok"
    assert doctor["release_safety"]["ship_readiness"] == "safe_to_ship"


def test_cli_scan_git_safety_uses_release_safety_findings(tmp_path: Path, capsys) -> None:
    leaked = tmp_path / "leaked.md"
    leaked.write_text("Local path C:\\Users\\owner\\Desktop\\demo.txt\n", encoding="utf-8")

    assert main(["scan-git-safety", str(leaked)]) == 1
    output = capsys.readouterr().out
    assert "Potential leak findings:" in output
    assert "[windows_user_path]" in output
