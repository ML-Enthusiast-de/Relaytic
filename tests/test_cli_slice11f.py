from __future__ import annotations

import json
from pathlib import Path

from relaytic.ui.cli import main


def test_cli_mission_control_show_exposes_demo_flow_modes_and_stuck_guidance(
    tmp_path: Path,
    capsys,
) -> None:
    output_dir = tmp_path / "mission_control_demo_grade"

    assert main(
        [
            "mission-control",
            "show",
            "--output-dir",
            str(output_dir),
            "--expected-profile",
            "full",
            "--format",
            "json",
        ]
    ) == 0
    payload = json.loads(capsys.readouterr().out)
    bundle = dict(payload["bundle"])
    onboarding = dict(bundle["onboarding_status"])
    actions = dict(bundle["action_affordances"])
    starters = dict(bundle["question_starters"])
    layout = dict(bundle["control_center_layout"])
    mission_control = dict(payload["mission_control"])

    action_ids = {str(dict(item).get("action_id", "")).strip() for item in actions.get("actions", [])}
    starter_questions = {str(dict(item).get("question", "")).strip().lower() for item in starters.get("starters", [])}
    panel_ids = {str(dict(item).get("panel_id", "")).strip() for item in layout.get("panels", [])}
    mode_names = {str(dict(item).get("name", "")).strip() for item in onboarding.get("mode_explanations", [])}

    assert payload["status"] == "ok"
    assert len(onboarding.get("guided_demo_flow", [])) >= 4
    assert len(onboarding.get("stuck_guide", [])) >= 4
    assert len(onboarding.get("mode_explanations", [])) >= 4
    assert "run_guided_demo" in action_ids
    assert "when_stuck" in action_ids
    assert "show me a demo flow" in starter_questions
    assert "what do the modes mean?" in starter_questions
    assert "i'm stuck, what should i do?" in starter_questions
    assert "guided_demo" in panel_ids
    assert "modes_explained" in panel_ids
    assert "stuck_help" in panel_ids
    assert "Mission Control" in mode_names
    assert "Mission Control Chat" in mode_names
    assert "Assist" in mode_names
    assert mission_control["question_count"] >= 10


def test_cli_mission_control_show_human_output_contains_demo_grade_sections(
    tmp_path: Path,
    capsys,
) -> None:
    output_dir = tmp_path / "mission_control_demo_grade_markdown"

    assert main(
        [
            "mission-control",
            "show",
            "--output-dir",
            str(output_dir),
            "--expected-profile",
            "full",
        ]
    ) == 0
    output = capsys.readouterr().out

    assert "## Guided Demo Flow" in output
    assert "## What The Modes Mean" in output
    assert "## If You Get Stuck" in output
    assert "## Handbooks" in output


def test_cli_mission_control_chat_supports_demo_mode_and_stuck_shortcuts(
    tmp_path: Path,
    capsys,
    monkeypatch,
) -> None:
    output_dir = tmp_path / "mission_control_demo_chat"
    prompts = iter(["/demo", "/modes", "/stuck"])
    monkeypatch.setattr("builtins.input", lambda _prompt="": next(prompts))

    assert main(
        [
            "mission-control",
            "chat",
            "--output-dir",
            str(output_dir),
            "--expected-profile",
            "full",
            "--max-turns",
            "3",
        ]
    ) == 0
    output = capsys.readouterr().out

    assert "Here is the shortest useful demo path." in output
    assert "Relaytic exposes different surfaces on purpose." in output
    assert "If you are stuck, do not guess." in output


def test_handbooks_cover_demo_flow_and_stuck_recovery() -> None:
    user_text = Path("docs/handbooks/relaytic_user_handbook.md").read_text(encoding="utf-8")
    agent_text = Path("docs/handbooks/relaytic_agent_handbook.md").read_text(encoding="utf-8")
    demo_text = Path("docs/handbooks/relaytic_demo_walkthrough.md").read_text(encoding="utf-8")

    assert "## The Fastest Start" in user_text
    assert "## Quick Analysis First" in user_text
    assert "## The Main Flow" in user_text
    assert "## What To Do When You Are Stuck" in user_text
    assert "## The Best First Demo" in user_text
    assert "## First Session Workflow" in agent_text
    assert "## The Main Operating Pattern" in agent_text
    assert "analysis-first objectives" in agent_text
    assert "## If You Are Stuck" in agent_text
    assert "## The Five-Step Demo" in demo_text
    assert "## If You Need To Explain Why This Is Different" in demo_text
    assert len(user_text.splitlines()) >= 80
    assert len(agent_text.splitlines()) >= 60
    assert len(demo_text.splitlines()) >= 60
