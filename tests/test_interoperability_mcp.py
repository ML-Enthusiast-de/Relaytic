import csv
from pathlib import Path

import anyio
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client

from relaytic.interoperability import (
    build_interoperability_tool_specs,
    find_available_port,
    run_live_streamable_http_smoke_check,
    start_streamable_http_server_process,
)
from tests.public_datasets import write_public_breast_cancer_dataset


def test_streamable_http_mcp_smoke_is_ok() -> None:
    report = run_live_streamable_http_smoke_check()
    assert report["status"] == "ok"
    assert report["server_status"] == "ok"
    assert report["tool_count"] >= 10


def test_interoperability_specs_include_trace_eval_handoff_and_learnings_tools() -> None:
    names = {spec.name for spec in build_interoperability_tool_specs()}
    assert {
        "relaytic_show_trace",
        "relaytic_replay_trace",
        "relaytic_run_agent_evals",
        "relaytic_show_agent_evals",
        "relaytic_show_handoff",
        "relaytic_show_workspace",
        "relaytic_set_next_run_focus",
        "relaytic_continue_workspace",
        "relaytic_show_learnings",
        "relaytic_reset_learnings",
    }.issubset(names)


def test_streamable_http_mcp_can_run_relaytic_end_to_end_on_public_dataset(tmp_path: Path) -> None:
    data_path = _write_small_public_breast_cancer_dataset(tmp_path / "breast_cancer_small.csv")
    run_dir = tmp_path / "mcp_run"
    port = find_available_port()
    process = start_streamable_http_server_process(port=port)
    url = f"http://127.0.0.1:{port}/mcp"

    async def _flow() -> None:
        last_error: str | None = None
        for _ in range(30):
            try:
                async with streamable_http_client(url) as (read_stream, write_stream, _get_session_id):
                    async with ClientSession(read_stream, write_stream) as session:
                        await session.initialize()
                        tool_result = await session.call_tool(
                            "relaytic_run",
                            {
                                "run_dir": str(run_dir),
                                "data_path": str(data_path),
                                "text": "Do everything on your own. Predict diagnosis_flag from the provided features.",
                                "actor_type": "agent",
                                "channel": "mcp-test",
                                "overwrite": True,
                            },
                        )
                        run_payload = _structured_payload(tool_result)
                        assert run_payload["surface_payload"]["status"] == "ok"
                        assert run_payload["surface_payload"]["run_summary"]["decision"]["task_type"] in {
                            "classification",
                            "binary_classification",
                            "fraud_detection",
                        }

                        status_result = await session.call_tool("relaytic_get_status", {"run_dir": str(run_dir)})
                        status_payload = _structured_payload(status_result)
                        assert status_payload["surface_payload"]["status"] == "ok"
                        assert status_payload["surface_payload"]["completion"]["action"] is not None

                        intelligence_result = await session.call_tool(
                            "relaytic_show_intelligence",
                            {"run_dir": str(run_dir)},
                        )
                        intelligence_payload = _structured_payload(intelligence_result)
                        assert intelligence_payload["surface_payload"]["status"] == "ok"
                        assert (
                            intelligence_payload["surface_payload"]["intelligence"]["recommended_followup_action"]
                            is not None
                        )

                        benchmark_result = await session.call_tool(
                            "relaytic_show_benchmark",
                            {"run_dir": str(run_dir)},
                        )
                        benchmark_payload = _structured_payload(benchmark_result)
                        assert benchmark_payload["surface_payload"]["status"] == "ok"
                        assert "incumbent_present" in benchmark_payload["surface_payload"]["benchmark"]

                        handoff_result = await session.call_tool(
                            "relaytic_show_handoff",
                            {"run_dir": str(run_dir), "audience": "agent"},
                        )
                        handoff_payload = _structured_payload(handoff_result)
                        assert handoff_payload["surface_payload"]["status"] == "ok"
                        assert handoff_payload["surface_payload"]["handoff"]["recommended_option_id"] in {
                            "same_data",
                            "add_data",
                            "new_dataset",
                        }

                        focus_result = await session.call_tool(
                            "relaytic_set_next_run_focus",
                            {
                                "run_dir": str(run_dir),
                                "selection": "same_data",
                                "notes": "focus on recall",
                                "actor_type": "agent",
                                "actor_name": "mcp-test",
                            },
                        )
                        focus_payload = _structured_payload(focus_result)
                        assert focus_payload["surface_payload"]["status"] == "ok"
                        assert focus_payload["surface_payload"]["next_run_focus"]["selection_id"] == "same_data"

                        learnings_result = await session.call_tool(
                            "relaytic_show_learnings",
                            {"run_dir": str(run_dir)},
                        )
                        learnings_payload = _structured_payload(learnings_result)
                        assert learnings_payload["surface_payload"]["status"] == "ok"
                        assert learnings_payload["surface_payload"]["learnings_state"]["entry_count"] >= 1

                        workspace_result = await session.call_tool(
                            "relaytic_show_workspace",
                            {"run_dir": str(run_dir)},
                        )
                        workspace_payload = _structured_payload(workspace_result)
                        assert workspace_payload["surface_payload"]["status"] == "ok"
                        assert workspace_payload["surface_payload"]["workspace"]["workspace_state"]["workspace_id"] is not None

                        continue_result = await session.call_tool(
                            "relaytic_continue_workspace",
                            {
                                "run_dir": str(run_dir),
                                "direction": "same_data",
                                "notes": "continue on the same dataset but focus on recall",
                                "actor_type": "agent",
                                "actor_name": "mcp-test",
                            },
                        )
                        continue_payload = _structured_payload(continue_result)
                        assert continue_payload["surface_payload"]["status"] == "ok"
                        assert continue_payload["surface_payload"]["continuation"]["selection_id"] == "same_data"

                        runtime_result = await session.call_tool(
                            "relaytic_show_runtime",
                            {"run_dir": str(run_dir), "limit": 12},
                        )
                        runtime_payload = _structured_payload(runtime_result)
                        assert runtime_payload["surface_payload"]["status"] == "ok"
                        assert runtime_payload["surface_payload"]["runtime"]["event_count"] >= 10
                        assert runtime_payload["surface_payload"]["runtime"]["last_surface"] == "mcp"

                        assist_result = await session.call_tool(
                            "relaytic_assist_turn",
                            {"run_dir": str(run_dir), "message": "take over"},
                        )
                        assist_payload = _structured_payload(assist_result)
                        assert assist_payload["surface_payload"]["status"] == "ok"
                        assert assist_payload["surface_payload"]["control"]["decision"] in {"accept_with_modification", "defer"}

                        control_result = await session.call_tool(
                            "relaytic_show_control",
                            {"run_dir": str(run_dir)},
                        )
                        control_payload = _structured_payload(control_result)
                        assert control_payload["surface_payload"]["status"] == "ok"
                        assert control_payload["surface_payload"]["control"]["decision"] is not None

                        decision_result = await session.call_tool(
                            "relaytic_show_decision",
                            {"run_dir": str(run_dir)},
                        )
                        decision_payload = _structured_payload(decision_result)
                        assert decision_payload["surface_payload"]["status"] == "ok"
                        assert decision_payload["surface_payload"]["decision_lab"]["selected_next_action"] is not None

                        pulse_review_result = await session.call_tool(
                            "relaytic_review_pulse",
                            {"run_dir": str(run_dir), "overwrite": True},
                        )
                        pulse_review_payload = _structured_payload(pulse_review_result)
                        assert pulse_review_payload["surface_payload"]["status"] == "ok"
                        assert pulse_review_payload["surface_payload"]["pulse"]["status"] in {"ok", "skipped"}

                        pulse_show_result = await session.call_tool(
                            "relaytic_show_pulse",
                            {"run_dir": str(run_dir)},
                        )
                        pulse_show_payload = _structured_payload(pulse_show_result)
                        assert pulse_show_payload["surface_payload"]["status"] == "ok"
                        assert pulse_show_payload["surface_payload"]["pulse"]["mode"] is not None

                        autonomy_result = await session.call_tool(
                            "relaytic_show_autonomy",
                            {"run_dir": str(run_dir)},
                        )
                        autonomy_payload = _structured_payload(autonomy_result)
                        assert autonomy_payload["surface_payload"]["status"] == "ok"
                        assert autonomy_payload["surface_payload"]["autonomy"]["selected_action"] is not None

                        predict_result = await session.call_tool(
                            "relaytic_predict",
                            {
                                "run_dir": str(run_dir),
                                "data_path": str(data_path),
                            },
                        )
                        predict_payload = _structured_payload(predict_result)
                        assert predict_payload["status"] == "ok"
                        assert predict_payload["prediction_count"] > 0
                        return
            except Exception as exc:  # pragma: no cover - retried below
                last_error = str(exc)
                await anyio.sleep(0.25)
        raise AssertionError(f"Failed to complete streamable HTTP Relaytic flow: {last_error}")

    try:
        anyio.run(_flow)
    finally:
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=5)
            except Exception:
                process.kill()
                process.wait(timeout=5)


def _structured_payload(result: object) -> dict:
    structured = getattr(result, "structuredContent", None) or getattr(result, "structured_content", None)
    assert isinstance(structured, dict)
    return structured


def _write_small_public_breast_cancer_dataset(path: Path, *, row_limit: int = 80) -> Path:
    full_path = write_public_breast_cancer_dataset(path.with_name(path.stem + "_full.csv"))
    with full_path.open("r", encoding="utf-8", newline="") as source, path.open(
        "w", encoding="utf-8", newline=""
    ) as destination:
        reader = csv.reader(source)
        writer = csv.writer(destination)
        for index, row in enumerate(reader):
            if index == 0 or index <= row_limit:
                writer.writerow(row)
            else:
                break
    return path
