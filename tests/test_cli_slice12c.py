from __future__ import annotations

import json
from pathlib import Path

from relaytic.learnings import default_learnings_state_dir
from relaytic.ui.cli import main
from tests.public_datasets import write_public_breast_cancer_dataset


def test_cli_handoff_and_learnings_surfaces_materialize_for_public_dataset(tmp_path: Path, capsys) -> None:
    run_dir = tmp_path / "handoff_learnings_public_binary"
    data_path = write_public_breast_cancer_dataset(tmp_path / "handoff_learnings_breast_cancer.csv")

    assert main(
        [
            "run",
            "--run-dir",
            str(run_dir),
            "--data-path",
            str(data_path),
            "--text",
            "Do everything on your own. Classify diagnosis_flag from the measurement columns and keep the result easy to hand off.",
            "--format",
            "json",
        ]
    ) == 0
    run_payload = json.loads(capsys.readouterr().out)
    summary = dict(run_payload["run_summary"])
    handoff = dict(summary["handoff"])
    learnings = dict(summary["learnings"])

    user_report_path = Path(str(handoff["user_report_path"]))
    agent_report_path = Path(str(handoff["agent_report_path"]))
    assert user_report_path.exists()
    assert agent_report_path.exists()
    user_report = user_report_path.read_text(encoding="utf-8")
    agent_report = agent_report_path.read_text(encoding="utf-8")
    assert "# Relaytic User Result Report" in user_report
    assert "# Relaytic Agent Result Report" in agent_report
    assert user_report != agent_report
    assert handoff["recommended_option_id"] in {"same_data", "add_data", "new_dataset"}
    assert learnings["state_entry_count"] >= 1
    assert Path(str(learnings["learnings_state_path"])).exists()
    assert Path(str(learnings["learnings_md_path"])).exists()

    assert main(
        [
            "handoff",
            "show",
            "--run-dir",
            str(run_dir),
            "--audience",
            "agent",
            "--format",
            "json",
        ]
    ) == 0
    handoff_payload = json.loads(capsys.readouterr().out)
    assert handoff_payload["status"] == "ok"
    assert handoff_payload["handoff"]["recommended_option_id"] == handoff["recommended_option_id"]

    assert main(
        [
            "handoff",
            "focus",
            "--run-dir",
            str(run_dir),
            "--selection",
            "same_data",
            "--notes",
            "focus on recall and threshold review",
            "--format",
            "json",
        ]
    ) == 0
    focus_payload = json.loads(capsys.readouterr().out)
    assert focus_payload["status"] == "ok"
    assert focus_payload["next_run_focus"]["selection_id"] == "same_data"
    assert focus_payload["run_summary"]["handoff"]["selected_focus_id"] == "same_data"
    assert focus_payload["run_summary"]["handoff"]["focus_notes"] == "focus on recall and threshold review"
    assert (run_dir / "next_run_focus.json").exists()

    assert main(
        [
            "learnings",
            "show",
            "--run-dir",
            str(run_dir),
            "--format",
            "json",
        ]
    ) == 0
    learnings_payload = json.loads(capsys.readouterr().out)
    assert learnings_payload["status"] == "ok"
    assert learnings_payload["snapshot"]["active_count"] >= 1
    assert learnings_payload["learnings_state"]["entry_count"] >= 1

    assert main(
        [
            "learnings",
            "reset",
            "--run-dir",
            str(run_dir),
            "--format",
            "json",
        ]
    ) == 0
    reset_payload = json.loads(capsys.readouterr().out)
    assert reset_payload["status"] == "ok"
    assert reset_payload["reset"]["status"] == "ok"
    assert reset_payload["run_summary"]["learnings"]["status"] == "reset"
    state_dir = default_learnings_state_dir(run_dir=run_dir)
    learnings_state = json.loads((state_dir / "learnings_state.json").read_text(encoding="utf-8"))
    assert learnings_state["status"] == "reset"
    assert learnings_state["entry_count"] == 0


def test_cli_mission_control_run_chat_supports_report_focus_and_learnings_flow_with_human_detour(
    tmp_path: Path,
    capsys,
    monkeypatch,
) -> None:
    run_dir = tmp_path / "handoff_chat_run"
    data_path = write_public_breast_cancer_dataset(tmp_path / "handoff_chat_breast_cancer.csv")

    assert main(
        [
            "run",
            "--run-dir",
            str(run_dir),
            "--data-path",
            str(data_path),
            "--text",
            "Do everything on your own. Classify diagnosis_flag from the measurement columns and keep the operator informed.",
            "--format",
            "json",
        ]
    ) == 0
    capsys.readouterr()

    prompts = iter(
        [
            "what did you find?",
            "what's the weather like in berlin?",
            "use the same data next time but focus on recall",
            "show learnings",
            "reset the learnings",
        ]
    )
    monkeypatch.setattr("builtins.input", lambda _prompt="": next(prompts))

    assert main(
        [
            "mission-control",
            "chat",
            "--run-dir",
            str(run_dir),
            "--expected-profile",
            "full",
            "--max-turns",
            "5",
        ]
    ) == 0
    output = capsys.readouterr().out
    state_dir = default_learnings_state_dir(run_dir=run_dir)
    next_run_focus = json.loads((run_dir / "next_run_focus.json").read_text(encoding="utf-8"))
    learnings_state = json.loads((state_dir / "learnings_state.json").read_text(encoding="utf-8"))

    assert "Mission-control chat is the terminal companion to the dashboard" in output
    assert "# Relaytic User Result Report" in output
    assert "focus `same_data`" in output
    assert "# Relaytic Learnings" in output
    assert "# Relaytic Learnings Reset" in output
    assert next_run_focus["selection_id"] == "same_data"
    assert learnings_state["status"] == "reset"
    assert learnings_state["entry_count"] == 0
