import csv
import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from relaytic.completion import run_completion_review
from relaytic.context import (
    build_context_controls_from_policy,
    default_data_origin,
    default_domain_brief,
    default_task_brief,
)
from relaytic.evidence import run_evidence_review
from relaytic.investigation import run_investigation
from relaytic.mandate import (
    build_mandate_controls_from_policy,
    build_run_brief,
    build_work_preferences,
    default_lab_mandate,
)
from relaytic.planning import execute_planned_route, run_planning
from relaytic.policies import load_policy


class _CompletionLLMHandler(BaseHTTPRequestHandler):
    last_request: dict | None = None

    def log_message(self, format: str, *args) -> None:  # pragma: no cover
        return

    def do_POST(self) -> None:  # noqa: N802
        length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(length).decode("utf-8")
        type(self).last_request = json.loads(body)
        content = {
            "summary_note": "Keep the run open because the current challenger space is still narrow.",
            "reasoning_highlights": ["Narrow challenger breadth", "Autonomous continuation"],
            "queue_emphasis": "Do not present the current result as final.",
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
        _CompletionLLMHandler.last_request = None
        self._server = ThreadingHTTPServer(("127.0.0.1", 0), _CompletionLLMHandler)
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
        ["timestamp", "sensor_a", "sensor_b", "failure_flag", "future_failure_flag", "post_inspection_flag"],
        ["2025-01-01T00:00:00", 10.0, 100.0, 0, 0, 0],
        ["2025-01-01T00:01:00", 11.0, 102.0, 0, 0, 0],
        ["2025-01-01T00:02:00", 12.0, 101.0, 1, 1, 1],
        ["2025-01-01T00:03:00", 13.0, 103.0, 0, 0, 0],
        ["2025-01-01T00:04:00", 14.0, 105.0, 1, 1, 1],
        ["2025-01-01T00:05:00", 15.0, 104.0, 0, 0, 0],
        ["2025-01-01T00:06:00", 16.0, 106.0, 1, 1, 1],
        ["2025-01-01T00:07:00", 17.0, 108.0, 0, 0, 0],
        ["2025-01-01T00:08:00", 18.0, 107.0, 1, 1, 1],
        ["2025-01-01T00:09:00", 19.0, 109.0, 0, 0, 0],
        ["2025-01-01T00:10:00", 20.0, 110.0, 1, 1, 1],
        ["2025-01-01T00:11:00", 21.0, 111.0, 0, 0, 0],
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        csv.writer(handle).writerows(rows)
    return path


def _build_foundation(policy: dict) -> tuple[dict, dict]:
    mandate_controls = build_mandate_controls_from_policy(policy)
    context_controls = build_context_controls_from_policy(policy)
    mandate_bundle = {
        "lab_mandate": default_lab_mandate(mandate_controls).to_dict(),
        "work_preferences": build_work_preferences(
            mandate_controls,
            policy=policy,
            execution_mode_preference="autonomous",
        ).to_dict(),
        "run_brief": build_run_brief(
            mandate_controls,
            policy=policy,
            objective="best_robust_pareto_front",
            target_column="failure_flag",
            success_criteria=["Catch failures before scrap decisions."],
            binding_constraints=["Do not use future or post-inspection features."],
        ).to_dict(),
    }
    context_bundle = {
        "data_origin": default_data_origin(
            context_controls,
            source_name="line_alarm_history",
            source_type="historical_snapshot",
        ).to_dict(),
        "domain_brief": default_domain_brief(
            context_controls,
            system_name="production_line",
            summary="Predict likely failures early enough to intervene before scrap is created.",
            forbidden_features=["future_failure_flag", "post_inspection_flag"],
        ).to_dict(),
        "task_brief": default_task_brief(
            context_controls,
            problem_statement="Predict failure flags from upstream process sensors.",
            target_column="failure_flag",
            success_criteria=["Maximize useful early warning value."],
            failure_costs=["Missed failures lead to scrap and avoidable downtime."],
        ).to_dict(),
    }
    return mandate_bundle, context_bundle


def test_run_completion_review_uses_local_llm_advisory_without_changing_decision(tmp_path: Path) -> None:
    data_path = _write_dataset(tmp_path / "slice07_llm.csv")
    run_dir = tmp_path / "run_slice07_llm"
    policy = load_policy().policy
    policy["intelligence"]["intelligence_mode"] = "advisory_local_llm"
    mandate_bundle, context_bundle = _build_foundation(policy)
    investigation_bundle = run_investigation(
        data_path=str(data_path),
        policy=policy,
        mandate_bundle=mandate_bundle,
        context_bundle=context_bundle,
    ).to_dict()
    planning_bundle = run_planning(
        data_path=str(data_path),
        policy=policy,
        mandate_bundle=mandate_bundle,
        context_bundle=context_bundle,
        investigation_bundle=investigation_bundle,
    )
    execution = execute_planned_route(
        run_dir=run_dir,
        data_path=str(data_path),
        planning_bundle=planning_bundle,
    )
    evidence_bundle = run_evidence_review(
        run_dir=run_dir,
        data_path=str(data_path),
        policy=policy,
        mandate_bundle=mandate_bundle,
        context_bundle=context_bundle,
        intake_bundle={
            "autonomy_mode": {
                "requested_mode": "autonomous",
                "operator_signal": "do everything on your own",
            },
            "clarification_queue": {"active_count": 0},
            "assumption_log": {"entries": [{"assumption": "autonomous"}]},
        },
        investigation_bundle=investigation_bundle,
        planning_bundle=execution.planning_bundle.to_dict(),
    ).bundle.to_dict()

    baseline = run_completion_review(
        run_dir=run_dir,
        policy=policy,
        mandate_bundle=mandate_bundle,
        context_bundle=context_bundle,
        intake_bundle={
            "autonomy_mode": {
                "requested_mode": "autonomous",
                "operator_signal": "do everything on your own",
            },
            "clarification_queue": {"active_count": 0},
            "assumption_log": {"entries": [{"assumption": "autonomous"}]},
        },
        investigation_bundle=investigation_bundle,
        planning_bundle=execution.planning_bundle.to_dict(),
        evidence_bundle=evidence_bundle,
    )

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

        advised = run_completion_review(
            run_dir=run_dir,
            policy=policy,
            mandate_bundle=mandate_bundle,
            context_bundle=context_bundle,
            intake_bundle={
                "autonomy_mode": {
                    "requested_mode": "autonomous",
                    "operator_signal": "do everything on your own",
                },
                "clarification_queue": {"active_count": 0},
                "assumption_log": {"entries": [{"assumption": "autonomous"}]},
            },
            investigation_bundle=investigation_bundle,
            planning_bundle=execution.planning_bundle.to_dict(),
            evidence_bundle=evidence_bundle,
            config_path=str(config_path),
        )

    assert advised.bundle.completion_decision.llm_advisory is not None
    assert advised.bundle.completion_decision.action == baseline.bundle.completion_decision.action
    assert "Advisory note" in advised.bundle.completion_decision.summary
    assert _CompletionLLMHandler.last_request is not None
