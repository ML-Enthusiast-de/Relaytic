from __future__ import annotations

import json
from pathlib import Path

from relaytic.interoperability import relaytic_show_permissions
from relaytic.policies import load_policy
from relaytic.runtime import ensure_runtime_initialized, record_stage_completion, record_stage_start
from relaytic.ui.cli import main


def test_cli_events_permissions_and_mission_control_surface_stay_aligned(tmp_path: Path, capsys) -> None:
    run_dir = tmp_path / "slice13b_runtime"
    data_path = tmp_path / "runtime_data.csv"
    data_path.write_text("feature,target\n1,0\n2,1\n", encoding="utf-8")
    policy = load_policy().policy

    ensure_runtime_initialized(
        run_dir=run_dir,
        policy=policy,
        source_surface="cli",
        source_command="unit_test_bootstrap",
    )
    (run_dir / "dataset_profile.json").write_text("{}", encoding="utf-8")
    token = record_stage_start(
        run_dir=run_dir,
        policy=policy,
        stage="investigation",
        source_surface="cli",
        source_command="unit_test_investigation",
        data_path=str(data_path),
        input_artifacts=["task_brief.json"],
    )
    record_stage_completion(
        run_dir=run_dir,
        policy=policy,
        stage_token=token,
        output_artifacts=[str(run_dir / "dataset_profile.json")],
        summary="Investigation completed for CLI permission tests.",
    )

    assert main(["events", "show", "--run-dir", str(run_dir), "--format", "json"]) == 0
    events_payload = json.loads(capsys.readouterr().out)
    assert events_payload["events"]["subscription_count"] >= 1
    assert events_payload["events"]["dispatch_count"] >= 1

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
            "--format",
            "json",
        ]
    ) == 0
    check_payload = json.loads(capsys.readouterr().out)
    assert check_payload["decision"]["decision"] == "approval_requested"
    request_id = check_payload["decision"]["request_id"]
    assert request_id

    assert main(["permissions", "show", "--run-dir", str(run_dir), "--format", "json"]) == 0
    permissions_payload = json.loads(capsys.readouterr().out)
    interop_payload = relaytic_show_permissions(run_dir=str(run_dir))
    assert permissions_payload["permissions"]["current_mode"] == interop_payload["surface_payload"]["permissions"]["current_mode"]
    assert permissions_payload["permissions"]["pending_approval_count"] == interop_payload["surface_payload"]["permissions"]["pending_approval_count"]

    assert main(["mission-control", "show", "--run-dir", str(run_dir), "--format", "json"]) == 0
    mission_payload = json.loads(capsys.readouterr().out)
    assert mission_payload["mission_control"]["permission_mode"] is not None
    assert mission_payload["mission_control"]["pending_approval_count"] >= 1

    assert main(
        [
            "permissions",
            "decide",
            "--run-dir",
            str(run_dir),
            "--request-id",
            str(request_id),
            "--decision",
            "approve",
            "--format",
            "json",
        ]
    ) == 0
    decide_payload = json.loads(capsys.readouterr().out)
    assert decide_payload["decision"]["decision"] == "approved"
