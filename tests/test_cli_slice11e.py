from __future__ import annotations

import json
from pathlib import Path

from relaytic.ui.cli import main


def test_cli_mission_control_show_exposes_role_specific_handbooks(
    tmp_path: Path,
    capsys,
) -> None:
    output_dir = tmp_path / "mission_control_handbooks"

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

    interaction_modes = [dict(item) for item in onboarding.get("interaction_modes", [])]
    guide_names = {str(item.get("name", "")).strip() for item in interaction_modes if str(item.get("kind", "")).strip().lower() == "guide"}
    commands = {str(item.get("command", "")).strip() for item in interaction_modes}
    action_ids = {str(dict(item).get("action_id", "")).strip() for item in actions.get("actions", [])}
    starter_questions = {str(dict(item).get("question", "")).strip().lower() for item in starters.get("starters", [])}
    panel_ids = {str(dict(item).get("panel_id", "")).strip() for item in layout.get("panels", [])}

    assert payload["status"] == "ok"
    assert "Human Handbook" in guide_names
    assert "Agent Handbook" in guide_names
    assert "docs/handbooks/relaytic_user_handbook.md" in commands
    assert "docs/handbooks/relaytic_agent_handbook.md" in commands
    assert "read_human_handbook" in action_ids
    assert "read_agent_handbook" in action_ids
    assert "where is the handbook?" in starter_questions
    assert "what should an agent read first?" in starter_questions
    assert "handbooks" in panel_ids
    assert any("relaytic_user_handbook.md" in str(step) for step in onboarding.get("first_steps", []))
    assert any("relaytic_agent_handbook.md" in str(step) for step in onboarding.get("first_steps", []))


def test_cli_mission_control_chat_answers_handbook_question(
    tmp_path: Path,
    capsys,
    monkeypatch,
) -> None:
    output_dir = tmp_path / "mission_control_handbook_chat"
    prompts = iter(["where is the handbook?"])
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
            "1",
        ]
    ) == 0
    output = capsys.readouterr().out

    assert "docs/handbooks/relaytic_user_handbook.md" in output
    assert "docs/handbooks/relaytic_agent_handbook.md" in output
    assert "Human operators should start" in output
    assert "External agents should start" in output


def test_cli_mission_control_chat_supports_handbook_shortcut(
    tmp_path: Path,
    capsys,
    monkeypatch,
) -> None:
    output_dir = tmp_path / "mission_control_handbook_shortcut"
    prompts = iter(["/handbook"])
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
            "1",
        ]
    ) == 0
    output = capsys.readouterr().out

    assert "docs/handbooks/relaytic_user_handbook.md" in output
    assert "docs/handbooks/relaytic_agent_handbook.md" in output
    assert "Relaytic ships with two handbook paths" in output


def test_checked_in_host_notes_point_to_agent_handbook() -> None:
    repo_files = [
        Path(".claude/agents/relaytic.md"),
        Path(".agents/skills/relaytic/SKILL.md"),
        Path("skills/relaytic/SKILL.md"),
        Path("openclaw/skills/relaytic/SKILL.md"),
    ]

    for path in repo_files:
        text = path.read_text(encoding="utf-8")
        assert "docs/handbooks/relaytic_agent_handbook.md" in text, str(path)
