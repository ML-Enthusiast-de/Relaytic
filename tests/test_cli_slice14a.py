from __future__ import annotations

import json
from pathlib import Path

from relaytic.ui.cli import main
from tests.public_datasets import write_public_breast_cancer_dataset


def _write_remote_config(path: Path) -> Path:
    path.write_text(
        "\n".join(
            [
                "remote_control:",
                "  enabled: true",
                "  transport_kind: filesystem_sync",
                "  transport_scope: local_only",
                "  freshness_seconds: 120",
                "  allow_remote_approval_decisions: true",
                "  allow_remote_handoffs: true",
                "  read_mostly: true",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    return path


def test_cli_remote_supervision_surfaces_approval_and_handoff_state(tmp_path: Path, capsys) -> None:
    run_dir = tmp_path / "remote_cli"
    data_path = write_public_breast_cancer_dataset(tmp_path / "remote_cli_dataset.csv")
    config_path = _write_remote_config(tmp_path / "remote_config.yaml")

    assert main(
        [
            "run",
            "--run-dir",
            str(run_dir),
            "--data-path",
            str(data_path),
            "--text",
            "Do everything on your own. Classify diagnosis_flag and keep the supervision state explicit.",
            "--config",
            str(config_path),
            "--format",
            "json",
        ]
    ) == 0
    capsys.readouterr()

    assert main(
        [
            "permissions",
            "check",
            "--run-dir",
            str(run_dir),
            "--action",
            "relaytic_run_autonomy",
            "--mode",
            "review",
            "--config",
            str(config_path),
            "--format",
            "json",
        ]
    ) == 0
    check_payload = json.loads(capsys.readouterr().out)
    request_id = check_payload["decision"]["request_id"]
    assert request_id

    assert main(
        ["remote", "show", "--run-dir", str(run_dir), "--config", str(config_path), "--format", "json"]
    ) == 0
    show_payload = json.loads(capsys.readouterr().out)
    assert show_payload["remote"]["pending_approval_count"] >= 1
    assert show_payload["remote"]["transport_enabled"] is True
    assert show_payload["bundle"]["remote_operator_presence"]["freshness_status"] in {"fresh", "unknown"}

    assert main(
        [
            "remote",
            "decide",
            "--run-dir",
            str(run_dir),
            "--request-id",
            str(request_id),
            "--decision",
            "approve",
            "--config",
            str(config_path),
            "--actor-type",
            "agent",
            "--actor-name",
            "codex-smoke",
            "--format",
            "json",
        ]
    ) == 0
    decide_payload = json.loads(capsys.readouterr().out)
    assert decide_payload["decision"]["status"] == "applied"
    assert decide_payload["remote"]["pending_approval_count"] == 0

    assert main(
        ["permissions", "show", "--run-dir", str(run_dir), "--config", str(config_path), "--format", "json"]
    ) == 0
    permissions_payload = json.loads(capsys.readouterr().out)
    assert permissions_payload["permissions"]["pending_approval_count"] == 0

    assert main(
        [
            "remote",
            "handoff",
            "--run-dir",
            str(run_dir),
            "--to-actor-type",
            "agent",
            "--to-actor-name",
            "codex-smoke",
            "--from-actor-type",
            "operator",
            "--from-actor-name",
            "unit-test",
            "--reason",
            "Continue supervision remotely.",
            "--config",
            str(config_path),
            "--format",
            "json",
        ]
    ) == 0
    handoff_payload = json.loads(capsys.readouterr().out)
    assert handoff_payload["remote"]["current_supervisor_type"] == "agent"

    assert main(
        ["mission-control", "show", "--run-dir", str(run_dir), "--config", str(config_path), "--format", "json"]
    ) == 0
    mission_payload = json.loads(capsys.readouterr().out)
    mission = mission_payload["mission_control"]
    assert mission["remote_transport_kind"] == "filesystem_sync"
    assert mission["remote_current_supervisor_type"] == "agent"

    for artifact_name in [
        "remote_session_manifest.json",
        "remote_transport_report.json",
        "approval_request_queue.json",
        "approval_decision_log.jsonl",
        "remote_operator_presence.json",
        "supervision_handoff.json",
        "notification_delivery_report.json",
        "remote_control_audit.json",
    ]:
        assert (run_dir / artifact_name).exists(), artifact_name
