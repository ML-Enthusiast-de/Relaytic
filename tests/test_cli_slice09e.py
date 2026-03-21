from __future__ import annotations

import json
from pathlib import Path

from relaytic.ui.cli import main

from tests.public_datasets import write_public_breast_cancer_dataset


def test_cli_assist_show_turn_and_takeover_work_on_public_dataset(tmp_path: Path, capsys) -> None:
    run_dir = tmp_path / "assist_public_binary"
    data_path = write_public_breast_cancer_dataset(tmp_path / "assist_public_breast_cancer.csv")

    assert main(
        [
            "run",
            "--run-dir",
            str(run_dir),
            "--data-path",
            str(data_path),
            "--text",
            "Do everything on your own. Classify diagnosis_flag from the measurement columns.",
            "--format",
            "json",
        ]
    ) == 0
    capsys.readouterr()

    assert main(["assist", "show", "--run-dir", str(run_dir), "--format", "json"]) == 0
    show_payload = json.loads(capsys.readouterr().out)
    assert show_payload["status"] == "ok"
    assert show_payload["assist"]["assist_mode"]["enabled"] is True
    assert show_payload["assist"]["assistant_connection_guide"]["recommended_path"]
    assert (run_dir / "assist_mode.json").exists()
    assert (run_dir / "assist_session_state.json").exists()
    assert (run_dir / "assistant_connection_guide.json").exists()

    assert main(
        [
            "assist",
            "turn",
            "--run-dir",
            str(run_dir),
            "--message",
            "why are you in this state?",
            "--format",
            "json",
        ]
    ) == 0
    explain_payload = json.loads(capsys.readouterr().out)
    assert explain_payload["status"] == "ok"
    assert explain_payload["turn"]["intent_type"] == "explain"
    assert explain_payload["turn"]["action_kind"] == "respond"
    assert (run_dir / "assist_turn_log.jsonl").exists()

    assert main(
        [
            "assist",
            "turn",
            "--run-dir",
            str(run_dir),
            "--message",
            "connect claude or use a local llm",
            "--format",
            "json",
        ]
    ) == 0
    connect_payload = json.loads(capsys.readouterr().out)
    assert connect_payload["turn"]["intent_type"] == "connection_guidance"
    assert "local" in connect_payload["turn"]["response_message"].lower()

    assert main(
        [
            "assist",
            "turn",
            "--run-dir",
            str(run_dir),
            "--message",
            "go back to research",
            "--format",
            "json",
        ]
    ) == 0
    research_payload = json.loads(capsys.readouterr().out)
    assert research_payload["turn"]["action_kind"] == "rerun_stage"
    assert "research" in research_payload["turn"]["executed_stages"]
    assert "autonomy" in research_payload["turn"]["executed_stages"]

    autonomy_loop_path = run_dir / "autonomy_loop_state.json"
    assert autonomy_loop_path.exists()
    autonomy_loop_path.unlink()

    assert main(
        [
            "assist",
            "turn",
            "--run-dir",
            str(run_dir),
            "--message",
            "i'm not sure, take over",
            "--data-path",
            str(data_path),
            "--format",
            "json",
        ]
    ) == 0
    takeover_payload = json.loads(capsys.readouterr().out)
    assert takeover_payload["turn"]["intent_type"] == "take_over"
    assert takeover_payload["turn"]["action_kind"] == "take_over"
    assert "autonomy" in takeover_payload["turn"]["executed_stages"]
    assert (run_dir / "autonomy_loop_state.json").exists()


def test_cli_assist_chat_respects_turn_cap(tmp_path: Path, capsys, monkeypatch) -> None:
    run_dir = tmp_path / "assist_chat"
    data_path = write_public_breast_cancer_dataset(tmp_path / "assist_chat_breast_cancer.csv")

    assert main(
        [
            "run",
            "--run-dir",
            str(run_dir),
            "--data-path",
            str(data_path),
            "--text",
            "Do everything on your own. Classify diagnosis_flag from the measurement columns.",
            "--format",
            "json",
        ]
    ) == 0
    capsys.readouterr()

    inputs = iter(["status"])
    monkeypatch.setattr("builtins.input", lambda _prompt="": next(inputs))

    assert main(
        [
            "assist",
            "chat",
            "--run-dir",
            str(run_dir),
            "--max-turns",
            "1",
        ]
    ) == 0
    output = capsys.readouterr().out
    assert "Communicative assist session started" in output
    assert "Session ended." in output
