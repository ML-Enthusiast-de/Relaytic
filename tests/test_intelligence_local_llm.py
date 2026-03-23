from __future__ import annotations

import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest

pytest.importorskip("sklearn.datasets")

from relaytic.ui.cli import main

from tests.public_datasets import write_public_breast_cancer_dataset


class _IntelligenceLLMHandler(BaseHTTPRequestHandler):
    last_request: dict | None = None

    def log_message(self, format: str, *args) -> None:  # pragma: no cover
        return

    def do_POST(self) -> None:  # noqa: N802
        length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(length).decode("utf-8")
        type(self).last_request = json.loads(body)
        content = {
            "proposer_position": {
                "action": "expand_challenger_portfolio",
                "summary": "Semantic review sees value in broader challenger pressure.",
            },
            "counterposition": {
                "action": "run_recalibration_pass",
                "summary": "A cheaper recalibration pass remains a plausible alternative.",
            },
            "verifier_verdict": {
                "action": "expand_challenger_portfolio",
                "summary": "Verifier keeps the broader challenger step because evidence is still conditional.",
                "preferred_model_family": "logistic_regression",
            },
            "recommended_followup_action": "expand_challenger_portfolio",
            "confidence": "conditional",
            "counterpositions": [
                {"action": "expand_challenger_portfolio", "summary": "Primary semantic recommendation."},
                {"action": "run_recalibration_pass", "summary": "Lower-cost fallback."},
            ],
            "unresolved_items": [
                {"item": "operating_threshold", "severity": "medium", "detail": "Threshold preference remains somewhat open."}
            ],
            "reason_codes": ["semantic_portfolio_expansion"],
            "escalation_recommended": False,
            "recommended_path": "continue_with_artifact_grounding",
            "escalation_summary": "No richer escalation is required for this round.",
            "summary": "Local semantic debate recommends a broader challenger portfolio.",
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
        _IntelligenceLLMHandler.last_request = None
        self._server = ThreadingHTTPServer(("127.0.0.1", 0), _IntelligenceLLMHandler)
        self.url = f"http://127.0.0.1:{self._server.server_port}/v1/chat/completions"
        self._thread = threading.Thread(target=self._server.serve_forever, daemon=True)

    def __enter__(self) -> "_LocalServer":
        self._thread.start()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self._server.shutdown()
        self._server.server_close()
        self._thread.join(timeout=2)


def test_cli_intelligence_run_uses_local_llm_when_enabled(tmp_path: Path, capsys) -> None:
    run_dir = tmp_path / "intelligence_llm"
    data_path = write_public_breast_cancer_dataset(tmp_path / "public_breast_cancer.csv")

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
    (run_dir / "policy_resolved.yaml").unlink()

    with _LocalServer() as server:
        config_path = tmp_path / "intelligence_config.yaml"
        config_path.write_text(
            "\n".join(
                [
                    "policy:",
                    "  intelligence:",
                    "    enabled: true",
                    "    intelligence_mode: advisory_local_llm",
                    "    prefer_local_llm: true",
                    "    allow_frontier_llm: false",
                    "    enable_backend_discovery: true",
                    "    require_schema_constrained_actions: true",
                    "    require_verifier_for_high_impact_decisions: true",
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

        assert main(
            [
                "intelligence",
                "run",
                "--run-dir",
                str(run_dir),
                "--config",
                str(config_path),
                "--overwrite",
                "--format",
                "json",
            ]
        ) == 0
        payload = json.loads(capsys.readouterr().out)

    assert payload["status"] == "ok"
    assert payload["intelligence"]["effective_mode"] == "semantic_local_llm"
    assert payload["intelligence"]["routed_mode"] is not None
    assert payload["intelligence"]["local_profile"] is not None
    assert payload["bundle"]["llm_health_check"]["status"] == "ok"
    assert payload["bundle"]["llm_routing_plan"]["status"] == "routed"
    assert payload["bundle"]["local_llm_profile"]["profile_name"] == "small_cpu"
    assert payload["bundle"]["semantic_debate_report"]["recommended_followup_action"] == "expand_challenger_portfolio"
    assert payload["bundle"]["verifier_report"]["changed_from_deterministic_baseline"] is True
    assert _IntelligenceLLMHandler.last_request is not None
