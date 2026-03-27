from __future__ import annotations

import json
from pathlib import Path

from relaytic.ui.cli import main
from tests.public_datasets import write_public_breast_cancer_dataset


def test_cli_mission_control_show_onboarding_explains_what_relaytic_is_and_first_steps(
    tmp_path: Path,
    capsys,
) -> None:
    output_dir = tmp_path / "mission_control_onboarding"

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
    capabilities = dict(bundle["capability_manifest"])
    starters = dict(bundle["question_starters"])
    mission_control = dict(payload["mission_control"])

    assert payload["status"] == "ok"
    assert onboarding["what_relaytic_is"]
    assert onboarding["needs_data"] is True
    assert len(onboarding["first_steps"]) >= 2
    assert "mission-control chat" in onboarding["live_chat_command"]
    assert mission_control["live_chat_command"] == onboarding["live_chat_command"]
    assert mission_control["needs_data"] is True
    assert any(dict(item).get("status_reason") for item in capabilities.get("capabilities", []))
    assert any(dict(item).get("activation_hint") for item in capabilities.get("capabilities", []))
    starter_questions = [str(dict(item).get("question", "")).strip().lower() for item in starters.get("starters", [])]
    assert "what is relaytic?" in starter_questions
    assert "how do i start?" in starter_questions
    assert "why are some capabilities disabled?" in starter_questions


def test_cli_mission_control_chat_handles_onboarding_questions(
    tmp_path: Path,
    capsys,
    monkeypatch,
) -> None:
    output_dir = tmp_path / "mission_control_chat"
    prompts = iter(["what can you do?"])
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
    output = capsys.readouterr().out.lower()

    assert "mission-control chat is the terminal onboarding surface" in output
    assert "local-first structured-data lab" in output or "local-first structured-data research lab" in output
    assert "data plus a goal" in output or "dataset" in output
    assert "mission-control launch" in output or "mission-control chat" in output


def test_cli_mission_control_launch_interactive_routes_into_chat(
    tmp_path: Path,
    capsys,
    monkeypatch,
) -> None:
    output_dir = tmp_path / "mission_control_launch"
    prompts = iter(["what is relaytic?"])
    monkeypatch.setattr("builtins.input", lambda _prompt="": next(prompts))

    assert main(
        [
            "mission-control",
            "launch",
            "--output-dir",
            str(output_dir),
            "--expected-profile",
            "full",
            "--no-browser",
            "--interactive",
            "--max-turns",
            "1",
        ]
    ) == 0
    output = capsys.readouterr().out.lower()

    assert "relaytic mission control" in output
    assert "mission-control chat is the terminal onboarding surface" in output
    assert "local-first structured-data" in output


def test_cli_assist_chat_help_and_capabilities_shortcuts_are_clear(
    tmp_path: Path,
    capsys,
    monkeypatch,
) -> None:
    run_dir = tmp_path / "assist_chat_clarity"
    data_path = write_public_breast_cancer_dataset(tmp_path / "assist_chat_clarity_breast_cancer.csv")

    assert main(
        [
            "run",
            "--run-dir",
            str(run_dir),
            "--data-path",
            str(data_path),
            "--text",
            "Do everything on your own. Classify diagnosis_flag from the provided features and keep the operator informed.",
            "--format",
            "json",
        ]
    ) == 0
    capsys.readouterr()

    prompts = iter(["/capabilities", "/stages", "/exit"])
    monkeypatch.setattr("builtins.input", lambda _prompt="": next(prompts))

    assert main(
        [
            "assist",
            "chat",
            "--run-dir",
            str(run_dir),
            "--max-turns",
            "0",
        ]
    ) == 0
    output = capsys.readouterr().out.lower()

    assert "assist chat is the live terminal conversation for an existing run" in output
    assert "bounded questions" in output
    assert "bounded stage reruns" in output
    assert "not arbitrary checkpoint time travel" in output
