import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from relaytic.orchestration.harness_runner import run_local_agent_once
from relaytic.orchestration.local_provider import LocalLLMResponder, LocalResponderConfig
from relaytic.orchestration.tool_registry import ToolRegistry
from relaytic.ui.cli import main


class _StubLLMHandler(BaseHTTPRequestHandler):
    response_mode = "openai"
    last_request: dict | None = None

    def log_message(self, format: str, *args) -> None:  # pragma: no cover
        return

    def do_POST(self) -> None:  # noqa: N802
        length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(length).decode("utf-8")
        type(self).last_request = json.loads(body)
        if type(self).response_mode == "ollama":
            payload = {
                "message": {
                    "content": json.dumps({"action": "respond", "message": "ollama-local-ok"})
                }
            }
        else:
            payload = {
                "choices": [
                    {
                        "message": {
                            "content": json.dumps({"action": "respond", "message": "local-ok"})
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


class _LocalServer:
    def __init__(self, mode: str) -> None:
        _StubLLMHandler.response_mode = mode
        _StubLLMHandler.last_request = None
        self._server = ThreadingHTTPServer(("127.0.0.1", 0), _StubLLMHandler)
        self.url = f"http://127.0.0.1:{self._server.server_port}/v1/chat/completions"
        self._thread = threading.Thread(target=self._server.serve_forever, daemon=True)

    def __enter__(self) -> "_LocalServer":
        self._thread.start()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self._server.shutdown()
        self._server.server_close()
        self._thread.join(timeout=2)


def test_local_llm_responder_round_trips_against_local_openai_stub() -> None:
    with _LocalServer("openai") as server:
        responder = LocalLLMResponder(
            config=LocalResponderConfig(
                provider="openai_compatible",
                model="relaytic-local",
                endpoint=server.url,
                timeout_seconds=5,
            ),
            system_prompt="You are local.",
            tool_catalog=[],
        )

        result = responder(history=[], context={"workflow_stage": "test"})

    assert result["action"] == "respond"
    assert result["message"] == "local-ok"
    assert _StubLLMHandler.last_request is not None
    assert _StubLLMHandler.last_request["model"] == "relaytic-local"


def test_run_local_agent_once_uses_local_stub_llm(monkeypatch, tmp_path: Path) -> None:
    with _LocalServer("openai") as server:
        config = tmp_path / "config.yaml"
        config.write_text(
            "\n".join(
                [
                    "privacy:",
                    "  local_only: true",
                    "  api_calls_allowed: false",
                    "  telemetry_allowed: false",
                    "runtime:",
                    "  provider: llama_cpp",
                    "  require_local_models: true",
                    "  block_remote_endpoints: true",
                    "  offline_mode: true",
                    "  temperature: 0.0",
                    "  timeout_seconds: 10",
                    "  endpoints:",
                    f"    llama_cpp: {server.url}",
                    "  profiles:",
                    "    small_cpu:",
                    "      model: relaytic-4b",
                    "      cpu_only: true",
                    "      n_gpu_layers: 0",
                    "      max_context: 4096",
                    "  default_profile: small_cpu",
                    "  fallback_order:",
                    "    - small_cpu",
                    "prompts:",
                    "  analyst_system_path: ''",
                    "  modeler_system_path: ''",
                    "  extra_instructions: ''",
                ]
            ),
            encoding="utf-8",
        )
        monkeypatch.setattr(
            "relaytic.orchestration.harness_runner.build_default_registry",
            lambda: ToolRegistry(),
        )

        result = run_local_agent_once(
            agent="analyst",
            user_message="Say hello from the local model.",
            context={"session": "slice01"},
            config_path=str(config),
        )

    assert result["event"]["status"] == "respond"
    assert result["event"]["message"] == "local-ok"


def test_local_llm_can_consume_foundation_artifacts_as_context(monkeypatch, tmp_path: Path) -> None:
    with _LocalServer("openai") as server:
        run_dir = tmp_path / "run_foundation_llm"
        assert main(["foundation", "init", "--run-dir", str(run_dir)]) == 0
        bundle_context = {
            "run_brief": json.loads((run_dir / "run_brief.json").read_text(encoding="utf-8")),
            "task_brief": json.loads((run_dir / "task_brief.json").read_text(encoding="utf-8")),
            "domain_brief": json.loads((run_dir / "domain_brief.json").read_text(encoding="utf-8")),
        }
        config = tmp_path / "config.yaml"
        config.write_text(
            "\n".join(
                [
                    "privacy:",
                    "  local_only: true",
                    "  api_calls_allowed: false",
                    "  telemetry_allowed: false",
                    "runtime:",
                    "  provider: llama_cpp",
                    "  require_local_models: true",
                    "  block_remote_endpoints: true",
                    "  offline_mode: true",
                    "  temperature: 0.0",
                    "  timeout_seconds: 10",
                    "  endpoints:",
                    f"    llama_cpp: {server.url}",
                    "  profiles:",
                    "    small_cpu:",
                    "      model: relaytic-4b",
                    "      cpu_only: true",
                    "      n_gpu_layers: 0",
                    "      max_context: 4096",
                    "  default_profile: small_cpu",
                    "  fallback_order:",
                    "    - small_cpu",
                    "prompts:",
                    "  analyst_system_path: ''",
                    "  modeler_system_path: ''",
                    "  extra_instructions: ''",
                ]
            ),
            encoding="utf-8",
        )
        monkeypatch.setattr(
            "relaytic.orchestration.harness_runner.build_default_registry",
            lambda: ToolRegistry(),
        )

        result = run_local_agent_once(
            agent="analyst",
            user_message="Summarize the supplied foundation context.",
            context=bundle_context,
            config_path=str(config),
        )

    assert result["event"]["status"] == "respond"
    assert result["event"]["message"] == "local-ok"
    assert "context" in _StubLLMHandler.last_request["messages"][1]["content"]
