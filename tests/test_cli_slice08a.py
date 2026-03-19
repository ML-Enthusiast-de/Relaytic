import json
from pathlib import Path

from relaytic.ui.cli import main


def test_cli_interoperability_show_and_export_are_machine_readable(tmp_path: Path, capsys) -> None:
    assert main(["interoperability", "show", "--format", "json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["status"] == "ok"
    assert payload["tool_count"] >= 10
    assert {host["host"] for host in payload["hosts"]} >= {"claude", "codex", "openclaw", "chatgpt"}
    assert all(host["status"] == "ready" for host in payload["hosts"])
    host_map = {host["host"]: host for host in payload["hosts"]}
    assert host_map["claude"]["discoverable_now"] is True
    assert host_map["codex"]["discoverable_now"] is True
    assert host_map["openclaw"]["discoverable_now"] is True
    assert host_map["chatgpt"]["discoverable_now"] is False
    assert host_map["chatgpt"]["requires_public_https"] is True
    assert "openclaw" in payload["host_summary"]["discoverable_now"]
    assert "chatgpt" in payload["host_summary"]["requires_public_https"]

    export_dir = tmp_path / "interop_export"
    assert main(
        [
            "interoperability",
            "export",
            "--host",
            "all",
            "--output-dir",
            str(export_dir),
            "--force",
            "--format",
            "json",
        ]
    ) == 0
    exported = json.loads(capsys.readouterr().out)
    assert exported["status"] == "ok"
    assert (export_dir / "relaytic_host_bundle_manifest.json").exists()
    assert (export_dir / ".mcp.json").exists()
    assert (export_dir / ".claude" / "agents" / "relaytic.md").exists()
    assert (export_dir / ".agents" / "skills" / "relaytic" / "SKILL.md").exists()
    assert (export_dir / "skills" / "relaytic" / "SKILL.md").exists()
    assert (export_dir / "openclaw" / "skills" / "relaytic" / "SKILL.md").exists()
    assert (export_dir / "connectors" / "chatgpt" / "README.md").exists()


def test_cli_interoperability_self_check_live_and_doctor_full_are_ok(capsys) -> None:
    assert main(["interoperability", "self-check", "--live", "--format", "json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["status"] == "ok"
    assert payload["live_stdio_mcp"]["status"] == "ok"
    assert "relaytic_server_info" in payload["live_stdio_mcp"]["tool_names"]

    assert main(["doctor", "--expected-profile", "full", "--format", "json"]) == 0
    doctor = json.loads(capsys.readouterr().out)
    assert doctor["status"] in {"ok", "warn"}
    assert doctor["interoperability_self_check"]["status"] == "ok"
