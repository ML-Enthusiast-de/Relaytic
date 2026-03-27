from __future__ import annotations

import json
from pathlib import Path

from relaytic.interoperability import relaytic_show_mission_control
from relaytic.ui.cli import main
from tests.public_datasets import write_public_breast_cancer_dataset


def test_cli_mission_control_show_exposes_modes_capabilities_actions_and_stage_navigation(
    tmp_path: Path,
    capsys,
) -> None:
    run_dir = tmp_path / "mission_control_clarity"
    data_path = write_public_breast_cancer_dataset(tmp_path / "mission_control_clarity_breast_cancer.csv")

    assert main(
        [
            "run",
            "--run-dir",
            str(run_dir),
            "--data-path",
            str(data_path),
            "--text",
            "Do everything on your own. Classify diagnosis_flag from the provided features and explain what you can do at each step.",
            "--format",
            "json",
        ]
    ) == 0
    capsys.readouterr()

    assert main(
        [
            "mission-control",
            "show",
            "--run-dir",
            str(run_dir),
            "--expected-profile",
            "full",
            "--format",
            "json",
        ]
    ) == 0
    payload = json.loads(capsys.readouterr().out)
    mission_control = dict(payload["mission_control"])
    bundle = dict(payload["bundle"])

    assert payload["status"] == "ok"
    assert mission_control["next_actor"] is not None
    assert mission_control["capability_count"] >= 6
    assert mission_control["action_count"] >= 4
    assert mission_control["question_count"] >= 3
    assert mission_control["intelligence_mode"] is not None
    assert mission_control["can_rerun_stage"] is True
    assert mission_control["navigation_scope"] == "bounded_stage_rerun"

    mode_overview = dict(bundle["mode_overview"])
    capability_manifest = dict(bundle["capability_manifest"])
    action_affordances = dict(bundle["action_affordances"])
    stage_navigator = dict(bundle["stage_navigator"])
    question_starters = dict(bundle["question_starters"])

    assert mode_overview["takeover_available"] is True
    assert capability_manifest["capability_count"] >= 6
    assert any(
        dict(item).get("capability_id") == "skeptical_steering"
        for item in capability_manifest.get("capabilities", [])
    )
    assert action_affordances["action_count"] >= 4
    assert stage_navigator["can_jump_to_any_point"] is False
    assert stage_navigator["navigation_scope"] == "bounded_stage_rerun"
    assert any(
        dict(item).get("stage") in {"research", "benchmark", "planning"}
        for item in stage_navigator.get("available_stages", [])
    )
    assert question_starters["question_count"] >= 3

    for filename in (
        "mode_overview.json",
        "capability_manifest.json",
        "action_affordances.json",
        "stage_navigator.json",
        "question_starters.json",
    ):
        assert (run_dir / filename).exists(), filename

    interop_payload = relaytic_show_mission_control(run_dir=str(run_dir))
    interop_mission_control = dict(interop_payload["surface_payload"]["mission_control"])
    interop_bundle = dict(interop_payload["surface_payload"]["bundle"])
    assert interop_mission_control["next_actor"] == mission_control["next_actor"]
    assert interop_mission_control["capability_count"] == mission_control["capability_count"]
    assert dict(interop_bundle["stage_navigator"])["navigation_scope"] == "bounded_stage_rerun"


def test_cli_assist_show_and_turn_make_capabilities_and_question_starters_visible(
    tmp_path: Path,
    capsys,
) -> None:
    run_dir = tmp_path / "assist_capabilities"
    data_path = write_public_breast_cancer_dataset(tmp_path / "assist_capabilities_breast_cancer.csv")

    assert main(
        [
            "run",
            "--run-dir",
            str(run_dir),
            "--data-path",
            str(data_path),
            "--text",
            "Do everything on your own. Classify diagnosis_flag from the measurement columns and keep me informed.",
            "--format",
            "json",
        ]
    ) == 0
    capsys.readouterr()

    assert main(["assist", "show", "--run-dir", str(run_dir), "--format", "json"]) == 0
    show_payload = json.loads(capsys.readouterr().out)
    state = dict(show_payload["assist"]["assist_session_state"])

    assert show_payload["status"] == "ok"
    assert state["available_actions"]
    assert state["available_stage_targets"]
    assert state["suggested_questions"]
    assert "take_over" in state["available_actions"]
    assert any(stage in {"planning", "research", "benchmark"} for stage in state["available_stage_targets"])
    assert any("what can you do" in question.lower() for question in state["suggested_questions"])

    assert main(
        [
            "assist",
            "turn",
            "--run-dir",
            str(run_dir),
            "--message",
            "what can you do?",
            "--format",
            "json",
        ]
    ) == 0
    turn_payload = json.loads(capsys.readouterr().out)
    turn = dict(turn_payload["turn"])
    response = str(turn.get("response_message", "")).lower()

    assert turn_payload["status"] == "ok"
    assert turn["intent_type"] == "capabilities"
    assert turn["action_kind"] == "respond"
    assert "bounded questions" in response
    assert "bounded stage" in response
    assert "take over" in response or "takeover" in response
    assert "challenge" in response
