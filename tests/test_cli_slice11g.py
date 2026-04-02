from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from types import SimpleNamespace

from relaytic.ui.cli import main
from tests.public_datasets import write_public_breast_cancer_dataset


class _OnboardingLLMHandler(BaseHTTPRequestHandler):
    def log_message(self, format: str, *args) -> None:  # pragma: no cover
        return

    def do_POST(self) -> None:  # noqa: N802
        length = int(self.headers.get("Content-Length", "0"))
        _ = self.rfile.read(length).decode("utf-8")
        payload = {
            "choices": [
                {
                    "message": {
                        "content": json.dumps(
                            {
                                "intent": "provide_data_and_objective",
                                "data_path": None,
                                "objective": "identify malignant cases",
                                "incumbent_path": None,
                                "confirm_start": False,
                                "wants_reset": False,
                                "question_focus": None,
                                "confidence": "high",
                            }
                        )
                    }
                }
            ]
        }
        encoded = json.dumps(payload).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)


class _OnboardingLocalServer:
    def __init__(self) -> None:
        self._server = ThreadingHTTPServer(("127.0.0.1", 0), _OnboardingLLMHandler)
        self.url = f"http://127.0.0.1:{self._server.server_port}/v1/chat/completions"
        self._thread = threading.Thread(target=self._server.serve_forever, daemon=True)

    def __enter__(self) -> "_OnboardingLocalServer":
        self._thread.start()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self._server.shutdown()
        self._server.server_close()
        self._thread.join(timeout=2)


def _write_small_fraud_dataset(path: Path) -> Path:
    rows = ["transaction_id,amount_norm,device_risk,velocity_score,fraud_flag"]
    for index in range(20):
        fraud = 1 if index % 4 == 0 else 0
        amount = 0.93 if fraud else 0.18 + (index % 5) * 0.04
        device = 0.97 if fraud else 0.12 + (index % 4) * 0.05
        velocity = 0.9 if fraud else 0.15 + (index % 3) * 0.05
        rows.append(f"T{index:04d},{amount:.5f},{device:.5f},{velocity:.5f},{fraud}")
    path.write_text("\n".join(rows) + "\n", encoding="utf-8")
    return path


def test_cli_mission_control_chat_captures_dataset_path_and_requests_objective(
    tmp_path: Path,
    capsys,
    monkeypatch,
) -> None:
    output_dir = tmp_path / "adaptive_onboarding"
    data_path = write_public_breast_cancer_dataset(tmp_path / "onboarding_data.csv")
    prompts = iter([str(data_path)])
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
    session = json.loads((output_dir / "onboarding_chat_session_state.json").read_text(encoding="utf-8"))

    assert "You can paste a dataset path directly" in output
    assert "I found a dataset path" in output
    assert "Do you want a quick analysis first" in output
    assert session["detected_data_path"] == str(data_path)
    assert session["data_path_exists"] is True
    assert session["current_phase"] == "need_objective"
    assert session["next_expected_input"] == "objective"


def test_cli_mission_control_chat_starts_run_after_human_confirmation(
    tmp_path: Path,
    capsys,
    monkeypatch,
) -> None:
    output_dir = tmp_path / "adaptive_onboarding_start"
    data_path = write_public_breast_cancer_dataset(tmp_path / "onboarding_data.csv")
    run_dir = tmp_path / "created_run"
    config_path = tmp_path / "onboarding_config.yaml"
    config_path.write_text(
        "\n".join(
            [
                "communication:",
                f"  adaptive_onboarding_default_run_dir: {run_dir.as_posix()}",
            ]
        ),
        encoding="utf-8",
    )
    prompts = iter(
        [
            str(data_path),
            "Classify diagnosis_flag from the measurement columns.",
            "yes",
        ]
    )
    monkeypatch.setattr("builtins.input", lambda _prompt="": next(prompts))

    captured: dict[str, str] = {}
    original_show = __import__("relaytic.ui.cli", fromlist=["_show_mission_control_surface"])._show_mission_control_surface

    def fake_run_access_flow(**kwargs):
        captured.update(
            {
                "run_dir": str(kwargs["run_dir"]),
                "data_path": str(kwargs["data_path"]),
                "text": str(kwargs["text"]),
                "actor_type": str(kwargs["actor_type"]),
            }
        )
        Path(kwargs["run_dir"]).mkdir(parents=True, exist_ok=True)
        return {
            "surface_payload": {
                "status": "ok",
                "run_dir": str(kwargs["run_dir"]),
                "run_summary": {
                    "stage_completed": "autonomy_reviewed",
                    "next_step": {"recommended_action": "operator_review"},
                },
            },
            "human_output": "fake run created",
        }

    def fake_show(*, run_dir: str | None, output_dir: str | None, config_path: str | None, expected_profile: str):
        if run_dir and Path(run_dir) == run_dir_path:
            return {
                "surface_payload": {
                    "status": "ok",
                    "run_dir": str(run_dir_path),
                    "mission_control": {
                        "current_stage": "autonomy_reviewed",
                        "recommended_action": "operator_review",
                        "next_actor": "operator",
                    },
                    "bundle": {
                        "stage_navigator": {"available_stages": []},
                        "onboarding_status": {"live_chat_command": "relaytic mission-control chat"},
                    },
                },
                "human_output": "# Relaytic Mission Control\n",
            }
        return original_show(run_dir=run_dir, output_dir=output_dir, config_path=config_path, expected_profile=expected_profile)

    run_dir_path = run_dir
    monkeypatch.setattr("relaytic.ui.cli._run_access_flow", fake_run_access_flow)
    monkeypatch.setattr("relaytic.ui.cli._show_mission_control_surface", fake_show)

    assert main(
        [
            "mission-control",
            "chat",
            "--output-dir",
            str(output_dir),
            "--config",
            str(config_path),
            "--expected-profile",
            "full",
            "--max-turns",
            "3",
        ]
    ) == 0
    output = capsys.readouterr().out
    session = json.loads((output_dir / "onboarding_chat_session_state.json").read_text(encoding="utf-8"))

    assert "I have both the data and the objective." in output
    assert "I've started a governed run" in output
    assert "Relaytic is now in run-specific mode." in output
    assert captured["run_dir"] == str(run_dir)
    assert captured["data_path"] == str(data_path)
    assert captured["text"] == "Classify diagnosis_flag from the measurement columns."
    assert captured["actor_type"] == "operator"
    assert session["created_run_dir"] == str(run_dir)
    assert session["current_phase"] == "run_started"


def test_cli_mission_control_chat_starts_fresh_even_if_previous_onboarding_state_exists(
    tmp_path: Path,
    capsys,
    monkeypatch,
) -> None:
    output_dir = tmp_path / "adaptive_onboarding_fresh_start"
    output_dir.mkdir(parents=True, exist_ok=True)
    stale_state = {
        "schema_version": "relaytic.onboarding_chat_session_state.v1",
        "generated_at": "2026-04-02T00:00:00+00:00",
        "status": "ready",
        "current_phase": "analysis_completed",
        "detected_data_path": "C:/stale/data.csv",
        "data_path_exists": True,
        "detected_objective": "give me the top 3 signals",
        "objective_family": "analysis",
        "incumbent_path": None,
        "incumbent_path_exists": None,
        "suggested_run_dir": "artifacts/demo",
        "suggested_run_dir_reason": None,
        "ready_to_start_run": False,
        "created_run_dir": None,
        "last_analysis_report_path": "reports/stale.md",
        "last_analysis_summary": "stale analysis",
        "next_expected_input": "analysis request or model request",
        "last_user_message": "old message",
        "last_system_question": "old question",
        "semantic_backend_status": "available",
        "semantic_model": "relaytic-4b",
        "llm_used_last_turn": True,
        "turn_count": 9,
        "notes": ["stale note"],
        "summary": "stale summary",
    }
    (output_dir / "onboarding_chat_session_state.json").write_text(
        json.dumps(stale_state),
        encoding="utf-8",
    )
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
    output = capsys.readouterr().out
    session = json.loads((output_dir / "onboarding_chat_session_state.json").read_text(encoding="utf-8"))

    assert "local-first structured-data" in output.lower()
    assert "I ran a direct analysis-first pass" not in output
    assert session["detected_data_path"] is None
    assert session["detected_objective"] is None
    assert session["turn_count"] == 1


def test_cli_mission_control_chat_answers_information_question_without_rerunning_analysis(
    tmp_path: Path,
    capsys,
    monkeypatch,
) -> None:
    output_dir = tmp_path / "adaptive_onboarding_info_priority"
    data_path = write_public_breast_cancer_dataset(tmp_path / "info_priority_data.csv")
    prompts = iter(
        [
            str(data_path),
            "analyze this data first and give me the top signals",
            "what can you do?",
        ]
    )
    monkeypatch.setattr("builtins.input", lambda _prompt="": next(prompts))

    calls: list[dict[str, object]] = []

    class _FakeRegistry:
        def execute(self, tool_name: str, arguments: dict[str, object]):
            calls.append({"tool_name": tool_name, "arguments": dict(arguments)})
            return SimpleNamespace(
                status="ok",
                output={
                    "status": "ok",
                    "report_path": str(tmp_path / "reports" / "info_priority.md"),
                    "ranking": [
                        {"target_signal": "diagnosis_flag"},
                        {"target_signal": "mean_radius"},
                        {"target_signal": "mean_texture"},
                    ],
                    "correlations": {
                        "target_analyses": [
                            {
                                "target_signal": "diagnosis_flag",
                                "top_predictors": ["mean_radius", "mean_texture", "mean_perimeter"],
                            }
                        ]
                    },
                },
            )

    monkeypatch.setattr("relaytic.ui.cli.build_default_registry", lambda: _FakeRegistry())

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
    session = json.loads((output_dir / "onboarding_chat_session_state.json").read_text(encoding="utf-8"))

    assert output.count("I ran a direct analysis-first pass") == 1
    assert "Right now I can explain what Relaytic is" in output
    assert len(calls) == 1
    assert calls[0]["tool_name"] == "run_agent1_analysis"
    assert session["detected_data_path"] == str(data_path)
    assert session["objective_family"] == "analysis"
    assert session["last_analysis_summary"] is not None


def test_cli_mission_control_chat_uses_local_semantic_assist_for_messy_startup(
    tmp_path: Path,
    capsys,
    monkeypatch,
) -> None:
    output_dir = tmp_path / "adaptive_onboarding_llm"
    data_path = write_public_breast_cancer_dataset(tmp_path / "onboarding_data.csv")
    prompts = iter([f'maybe use "{data_path}" because I mostly care about malignant cases'])
    monkeypatch.setattr("builtins.input", lambda _prompt="": next(prompts))

    with _OnboardingLocalServer() as server:
        config_path = tmp_path / "onboarding_llm_config.yaml"
        config_path.write_text(
            "\n".join(
                [
                    "policy:",
                    "  communication:",
                    "    adaptive_onboarding_semantic_assist: true",
                    "  intelligence:",
                    "    enabled: true",
                    "    intelligence_mode: deterministic",
                    "    prefer_local_llm: true",
                    "    allow_frontier_llm: false",
                    "    enable_backend_discovery: true",
                    "  privacy:",
                    "    api_calls_allowed: false",
                    "  runtime:",
                    "    provider: llama_cpp",
                    "    require_local_models: true",
                    "    block_remote_endpoints: true",
                    "    offline_mode: true",
                    "    temperature: 0.0",
                    "    timeout_seconds: 10",
                    "    endpoints:",
                    f"      llama_cpp: {server.url}",
                    "    profiles:",
                    "      small_cpu:",
                    "        model: relaytic-4b",
                    "        cpu_only: true",
                    "        n_gpu_layers: 0",
                    "        max_context: 4096",
                    "    default_profile: small_cpu",
                    "    fallback_order:",
                    "      - small_cpu",
                ]
            ),
            encoding="utf-8",
        )

        assert main(
            [
                "mission-control",
                "chat",
                "--output-dir",
                str(output_dir),
                "--config",
                str(config_path),
                "--expected-profile",
                "full",
                "--max-turns",
                "1",
            ]
        ) == 0
    output = capsys.readouterr().out
    session = json.loads((output_dir / "onboarding_chat_session_state.json").read_text(encoding="utf-8"))

    assert "I have both the data and the objective." in output
    assert session["detected_data_path"] == str(data_path)
    assert session["llm_used_last_turn"] is True
    assert session["semantic_backend_status"] == "available"


def test_install_script_full_profile_requests_onboarding_local_llm(
    monkeypatch,
    capsys,
) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    script_path = repo_root / "scripts" / "install_relaytic.py"
    spec = importlib.util.spec_from_file_location("relaytic_install_script", script_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    calls: list[list[str]] = []

    def fake_run(cmd, **kwargs):
        calls.append(list(cmd))
        if "doctor" in cmd:
            return subprocess.CompletedProcess(cmd, 0, stdout=json.dumps({"status": "ok", "package": {"installed": True}}), stderr="")
        if "setup-local-llm" in cmd:
            return subprocess.CompletedProcess(cmd, 0, stdout=json.dumps({"ready": True, "provider": "llama_cpp", "model": "relaytic-4b"}), stderr="")
        return subprocess.CompletedProcess(cmd, 0, stdout="", stderr="")

    monkeypatch.setattr(module.subprocess, "run", fake_run)

    assert module.main(["--skip-install", "--profile", "full", "--format", "json"]) == 0
    payload = json.loads(capsys.readouterr().out)

    assert any("setup-local-llm" in part for cmd in calls for part in cmd)
    assert payload["install"]["onboarding_llm_requested"] is True
    assert payload["onboarding_local_llm"]["ready"] is True


def test_cli_mission_control_show_exposes_analysis_first_objective_guidance(
    tmp_path: Path,
    capsys,
) -> None:
    output_dir = tmp_path / "analysis_first_guidance"

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

    action_ids = {str(dict(item).get("action_id", "")).strip() for item in actions.get("actions", [])}
    starter_questions = {str(dict(item).get("question", "")).strip().lower() for item in starters.get("starters", [])}
    first_steps = [str(item).strip().lower() for item in onboarding.get("first_steps", [])]

    assert "analyze_data_first" in action_ids
    assert "start_governed_modeling" in action_ids
    assert "can you just analyze the data first?" in starter_questions
    assert "give me the top 3 signals" in starter_questions
    assert any("quick analysis first" in step for step in first_steps)


def test_cli_mission_control_chat_starts_real_run_from_single_message_without_mocked_access_flow(
    tmp_path: Path,
    capsys,
    monkeypatch,
) -> None:
    output_dir = tmp_path / "adaptive_onboarding_real_run"
    run_dir = tmp_path / "real_started_run"
    data_path = _write_small_fraud_dataset(tmp_path / "fraud_onboarding.csv")
    config_path = tmp_path / "real_onboarding_config.yaml"
    config_path.write_text(
        "\n".join(
            [
                "communication:",
                "  adaptive_onboarding_confirmation_required: false",
                "  adaptive_onboarding_semantic_assist: false",
                f"  adaptive_onboarding_default_run_dir: {run_dir.as_posix()}",
            ]
        ),
        encoding="utf-8",
    )
    prompts = iter([f"{data_path} build a fraud model"])
    monkeypatch.setattr("builtins.input", lambda _prompt="": next(prompts))

    assert main(
        [
            "mission-control",
            "chat",
            "--output-dir",
            str(output_dir),
            "--config",
            str(config_path),
            "--expected-profile",
            "full",
            "--max-turns",
            "1",
        ]
    ) == 0
    output = capsys.readouterr().out
    session = json.loads((output_dir / "onboarding_chat_session_state.json").read_text(encoding="utf-8"))
    summary = json.loads((run_dir / "run_summary.json").read_text(encoding="utf-8"))
    intake_record = json.loads((run_dir / "intake_record.json").read_text(encoding="utf-8"))

    assert "I've started a governed run" in output
    assert run_dir.exists()
    assert session["created_run_dir"] == str(run_dir)
    assert session["current_phase"] == "run_started"
    assert summary["stage_completed"] is not None
    assert summary["decision"]["target_column"] == "fraud_flag"
    assert intake_record["actor_type"] == "operator"


def test_cli_mission_control_chat_runs_direct_analysis_for_analysis_first_objective(
    tmp_path: Path,
    capsys,
    monkeypatch,
) -> None:
    output_dir = tmp_path / "adaptive_onboarding_analysis"
    data_path = _write_small_fraud_dataset(tmp_path / "analysis_input.csv")
    config_path = tmp_path / "analysis_onboarding_config.yaml"
    config_path.write_text(
        "\n".join(
            [
                "communication:",
                "  adaptive_onboarding_confirmation_required: true",
                "  adaptive_onboarding_semantic_assist: false",
            ]
        ),
        encoding="utf-8",
    )
    prompts = iter([f"{data_path} analyze this fraud data and give me the top 3 signals"])
    monkeypatch.setattr("builtins.input", lambda _prompt="": next(prompts))

    captured: dict[str, object] = {}

    class _FakeRegistry:
        def execute(self, tool_name: str, arguments: dict[str, object]):
            captured["tool_name"] = tool_name
            captured["arguments"] = dict(arguments)
            return SimpleNamespace(
                status="ok",
                output={
                    "status": "ok",
                    "report_path": str(tmp_path / "reports" / "agent1_analysis.md"),
                    "ranking": [
                        {"target_signal": "fraud_flag"},
                        {"target_signal": "velocity_score"},
                        {"target_signal": "device_risk"},
                    ],
                    "correlations": {
                        "target_analyses": [
                            {
                                "target_signal": "fraud_flag",
                                "top_predictors": ["velocity_score", "device_risk", "amount_norm"],
                            }
                        ]
                    },
                },
            )

    monkeypatch.setattr("relaytic.ui.cli.build_default_registry", lambda: _FakeRegistry())

    assert main(
        [
            "mission-control",
            "chat",
            "--output-dir",
            str(output_dir),
            "--config",
            str(config_path),
            "--expected-profile",
            "full",
            "--max-turns",
            "1",
        ]
    ) == 0
    output = capsys.readouterr().out
    session = json.loads((output_dir / "onboarding_chat_session_state.json").read_text(encoding="utf-8"))

    assert "I ran a direct analysis-first pass" in output
    assert "`fraud_flag`" in output
    assert captured["tool_name"] == "run_agent1_analysis"
    assert dict(captured["arguments"])["data_path"] == str(data_path)
    assert dict(captured["arguments"])["task_type_hint"] == "fraud_detection"
    assert session["objective_family"] == "analysis"
    assert session["current_phase"] == "analysis_completed"
    assert session["created_run_dir"] is None
    assert session["last_analysis_report_path"] == str(tmp_path / "reports" / "agent1_analysis.md")
    assert "Top candidate signals" in str(session["last_analysis_summary"])


def test_cli_mission_control_chat_switches_from_analysis_to_governed_run_without_reusing_onboarding_root(
    tmp_path: Path,
    capsys,
    monkeypatch,
) -> None:
    shared_root = tmp_path / "shared_demo"
    data_path = _write_small_fraud_dataset(tmp_path / "analysis_then_model.csv")
    config_path = tmp_path / "analysis_then_model_config.yaml"
    config_path.write_text(
        "\n".join(
            [
                "communication:",
                f"  adaptive_onboarding_default_run_dir: {shared_root.as_posix()}",
            ]
        ),
        encoding="utf-8",
    )
    prompts = iter(
        [
            str(data_path),
            "quick analysis",
            "I want you to build a model for the output fraud_flag",
            "go",
        ]
    )
    monkeypatch.setattr("builtins.input", lambda _prompt="": next(prompts))

    assert main(
        [
            "mission-control",
            "chat",
            "--output-dir",
            str(shared_root),
            "--config",
            str(config_path),
            "--expected-profile",
            "full",
            "--max-turns",
            "4",
        ]
    ) == 0
    output = capsys.readouterr().out
    session = json.loads((shared_root / "onboarding_chat_session_state.json").read_text(encoding="utf-8"))
    created_run_dir = Path(str(session["created_run_dir"]))
    summary = json.loads((created_run_dir / "run_summary.json").read_text(encoding="utf-8"))

    assert "I ran a direct analysis-first pass" in output
    assert "The default run folder was already in use because" in output
    assert "I've started a governed run" in output
    assert created_run_dir != shared_root
    assert created_run_dir.exists()
    assert summary["decision"]["target_column"] == "fraud_flag"
    assert (shared_root / "mission_control_state.json").exists()
    assert (created_run_dir / "intake_record.json").exists()
