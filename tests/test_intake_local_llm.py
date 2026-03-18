import csv
import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from relaytic.context import (
    build_context_controls_from_policy,
    default_data_origin,
    default_domain_brief,
    default_task_brief,
)
from relaytic.intake import run_intake_interpretation
from relaytic.mandate import (
    build_mandate_controls_from_policy,
    build_run_brief,
    build_work_preferences,
    default_lab_mandate,
)
from relaytic.policies import load_policy


class _IntakeLLMHandler(BaseHTTPRequestHandler):
    last_request: dict | None = None

    def log_message(self, format: str, *args) -> None:  # pragma: no cover
        return

    def do_POST(self) -> None:  # noqa: N802
        length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(length).decode("utf-8")
        type(self).last_request = json.loads(body)
        content = {
            "task_brief_updates": {
                "target_column": "failure_flag",
                "problem_statement": "Predict failure_flag before late-stage inspection occurs.",
            },
            "domain_brief_updates": {
                "forbidden_features": ["post_inspection_flag"],
            },
            "clarification_questions": ["What intervention is feasible once a failure is predicted?"],
            "context_constraints": {
                "hard_constraints": ["do not require remote APIs by default"],
                "success_criteria": ["Favor an early warning route with inspectable artifacts."],
            },
        }
        payload = {"choices": [{"message": {"content": json.dumps(content)}}]}
        encoded = json.dumps(payload).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)


class _LocalServer:
    def __init__(self) -> None:
        _IntakeLLMHandler.last_request = None
        self._server = ThreadingHTTPServer(("127.0.0.1", 0), _IntakeLLMHandler)
        self.url = f"http://127.0.0.1:{self._server.server_port}/v1/chat/completions"
        self._thread = threading.Thread(target=self._server.serve_forever, daemon=True)

    def __enter__(self) -> "_LocalServer":
        self._thread.start()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self._server.shutdown()
        self._server.server_close()
        self._thread.join(timeout=2)


def _write_dataset(path: Path) -> Path:
    rows = [
        ["timestamp", "sensor_a", "sensor_b", "failure_flag", "post_inspection_flag"],
        ["2025-01-01T00:00:00", 10.0, 100.0, 0, 0],
        ["2025-01-01T00:01:00", 11.0, 101.0, 1, 1],
        ["2025-01-01T00:02:00", 12.0, 102.0, 0, 0],
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerows(rows)
    return path


def _build_foundation(policy: dict) -> tuple[dict, dict]:
    mandate_controls = build_mandate_controls_from_policy(policy)
    context_controls = build_context_controls_from_policy(policy)
    mandate_bundle = {
        "lab_mandate": default_lab_mandate(mandate_controls).to_dict(),
        "work_preferences": build_work_preferences(mandate_controls, policy=policy).to_dict(),
        "run_brief": build_run_brief(mandate_controls, policy=policy).to_dict(),
    }
    context_bundle = {
        "data_origin": default_data_origin(context_controls).to_dict(),
        "domain_brief": default_domain_brief(context_controls).to_dict(),
        "task_brief": default_task_brief(context_controls).to_dict(),
    }
    return mandate_bundle, context_bundle


def test_run_intake_interpretation_uses_local_llm_advisory_when_enabled(tmp_path: Path) -> None:
    data_path = _write_dataset(tmp_path / "llm_intake.csv")
    policy = load_policy().policy
    policy["intelligence"]["intelligence_mode"] = "advisory_local_llm"
    mandate_bundle, context_bundle = _build_foundation(policy)

    with _LocalServer() as server:
        config_path = tmp_path / "config.yaml"
        config_path.write_text(
            "\n".join(
                [
                    "policy:",
                    "  intelligence:",
                    "    enabled: true",
                    "    intelligence_mode: advisory_local_llm",
                    "    prefer_local_llm: true",
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
                ]
            ),
            encoding="utf-8",
        )

        resolution = run_intake_interpretation(
            message="We need an early warning model for bad batches before inspection.",
            actor_type="user",
            actor_name="ops_user",
            channel="cli",
            policy=policy,
            mandate_bundle=mandate_bundle,
            context_bundle=context_bundle,
            config_path=str(config_path),
            data_path=str(data_path),
        )

    assert resolution.intake_bundle.context_interpretation.llm_advisory is not None
    assert resolution.task_brief.target_column == "failure_flag"
    assert "post_inspection_flag" in resolution.domain_brief.forbidden_features
    assert resolution.intake_bundle.clarification_queue.items
    assert resolution.intake_bundle.clarification_queue.active_count >= 1
    assert resolution.intake_bundle.clarification_queue.suppressed_count == 0
    assert all(item.optional is True for item in resolution.intake_bundle.clarification_queue.items)
    assert all(item.blocking_class == "never" for item in resolution.intake_bundle.clarification_queue.items)
    assert _IntakeLLMHandler.last_request is not None
