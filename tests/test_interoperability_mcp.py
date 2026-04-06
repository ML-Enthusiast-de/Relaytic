import csv
from pathlib import Path

import anyio
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client

from relaytic.core.json_utils import write_json
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
        "relaytic_show_search",
        "relaytic_show_daemon",
        "relaytic_show_remote_control",
        "relaytic_show_release_safety",
        "relaytic_show_event_bus",
        "relaytic_show_permissions",
        "relaytic_review_search",
        "relaytic_run_background_job",
        "relaytic_resume_background_job",
        "relaytic_scan_release_safety",
        "relaytic_check_permission",
        "relaytic_decide_permission",
        "relaytic_decide_remote_approval",
        "relaytic_handoff_remote_supervision",
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
    config_path = tmp_path / "mcp_remote.yaml"
    config_path.write_text(
        "\n".join(
            [
                "remote_control:",
                "  enabled: true",
                "  transport_kind: filesystem_sync",
                "  transport_scope: local_only",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
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
                                "config_path": str(config_path),
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

                        mission_result = await session.call_tool(
                            "relaytic_show_mission_control",
                            {"run_dir": str(run_dir), "expected_profile": "full"},
                        )
                        mission_payload = _structured_payload(mission_result)
                        mission_control = dict(mission_payload["surface_payload"]["mission_control"])
                        mission_bundle = dict(mission_payload["surface_payload"]["bundle"])
                        assert mission_control["overall_confidence"] is not None
                        assert mission_control["branch_count"] >= 1
                        assert mission_control["background_job_count"] is not None
                        assert dict(mission_bundle["trace_explorer_state"])["span_count"] > 0
                        assert dict(mission_bundle["demo_pack_manifest"])["demo_count"] >= 4

                        search_review_result = await session.call_tool(
                            "relaytic_review_search",
                            {"run_dir": str(run_dir), "overwrite": True},
                        )
                        search_review_payload = _structured_payload(search_review_result)
                        assert search_review_payload["surface_payload"]["status"] == "ok"
                        assert search_review_payload["surface_payload"]["search"]["recommended_action"] is not None
                        write_json(
                            run_dir / "search_controller_plan.json",
                            {
                                "status": "ok",
                                "recommended_action": "expand_challenger_portfolio",
                                "recommended_direction": "same_data",
                                "planned_trial_count": 10,
                            },
                            indent=2,
                            ensure_ascii=False,
                            sort_keys=True,
                        )

                        search_show_result = await session.call_tool(
                            "relaytic_show_search",
                            {"run_dir": str(run_dir)},
                        )
                        search_show_payload = _structured_payload(search_show_result)
                        assert search_show_payload["surface_payload"]["status"] == "ok"
                        assert search_show_payload["surface_payload"]["search"]["value_band"] in {
                            "low",
                            "medium",
                            "high",
                        }

                        daemon_show_result = await session.call_tool(
                            "relaytic_show_daemon",
                            {"run_dir": str(run_dir)},
                        )
                        daemon_show_payload = _structured_payload(daemon_show_result)
                        assert daemon_show_payload["surface_payload"]["status"] == "ok"
                        assert daemon_show_payload["surface_payload"]["daemon"]["job_count"] >= 1

                        daemon_run_result = await session.call_tool(
                            "relaytic_run_background_job",
                            {"run_dir": str(run_dir), "job_id": "job_search_campaign"},
                        )
                        daemon_run_payload = _structured_payload(daemon_run_result)
                        assert daemon_run_payload["surface_payload"]["status"] == "ok"
                        daemon_job = dict(daemon_run_payload["surface_payload"]["job"])
                        if daemon_job["status"] == "approval_requested":
                            request_id = daemon_job["request_id"]
                            assert request_id is not None
                            daemon_approve_result = await session.call_tool(
                                "relaytic_decide_permission",
                                {
                                    "run_dir": str(run_dir),
                                    "request_id": request_id,
                                    "decision": "approve",
                                },
                            )
                            daemon_approve_payload = _structured_payload(daemon_approve_result)
                            assert daemon_approve_payload["surface_payload"]["decision"]["decision"] == "approved"
                            daemon_run_result = await session.call_tool(
                                "relaytic_run_background_job",
                                {"run_dir": str(run_dir), "job_id": "job_search_campaign"},
                            )
                            daemon_run_payload = _structured_payload(daemon_run_result)
                            daemon_job = dict(daemon_run_payload["surface_payload"]["job"])
                        assert daemon_job["status"] == "paused"

                        daemon_resume_result = await session.call_tool(
                            "relaytic_resume_background_job",
                            {"run_dir": str(run_dir), "job_id": "job_search_campaign"},
                        )
                        daemon_resume_payload = _structured_payload(daemon_resume_result)
                        assert daemon_resume_payload["surface_payload"]["status"] == "ok"
                        assert daemon_resume_payload["surface_payload"]["job"]["status"] == "completed"

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

                        event_bus_result = await session.call_tool(
                            "relaytic_show_event_bus",
                            {"run_dir": str(run_dir)},
                        )
                        event_bus_payload = _structured_payload(event_bus_result)
                        assert event_bus_payload["surface_payload"]["status"] == "ok"
                        assert event_bus_payload["surface_payload"]["events"]["subscription_count"] >= 1

                        permissions_result = await session.call_tool(
                            "relaytic_show_permissions",
                            {"run_dir": str(run_dir)},
                        )
                        permissions_payload = _structured_payload(permissions_result)
                        assert permissions_payload["surface_payload"]["status"] == "ok"
                        assert permissions_payload["surface_payload"]["permissions"]["current_mode"] is not None

                        permission_check_result = await session.call_tool(
                            "relaytic_check_permission",
                            {"run_dir": str(run_dir), "action": "relaytic_run_autonomy", "mode": "review"},
                        )
                        permission_check_payload = _structured_payload(permission_check_result)
                        assert permission_check_payload["surface_payload"]["decision"]["decision"] == "approval_requested"
                        assert permission_check_payload["surface_payload"]["decision"]["request_id"] is not None

                        remote_show_result = await session.call_tool(
                            "relaytic_show_remote_control",
                            {"run_dir": str(run_dir), "config_path": str(config_path)},
                        )
                        remote_show_payload = _structured_payload(remote_show_result)
                        assert remote_show_payload["surface_payload"]["status"] == "ok"
                        assert remote_show_payload["surface_payload"]["remote"]["pending_approval_count"] >= 1

                        permission_decide_result = await session.call_tool(
                            "relaytic_decide_remote_approval",
                            {
                                "run_dir": str(run_dir),
                                "request_id": permission_check_payload["surface_payload"]["decision"]["request_id"],
                                "decision": "approve",
                                "config_path": str(config_path),
                                "actor_type": "agent",
                                "actor_name": "mcp-test",
                            },
                        )
                        permission_decide_payload = _structured_payload(permission_decide_result)
                        assert permission_decide_payload["surface_payload"]["decision"]["status"] == "applied"

                        remote_handoff_result = await session.call_tool(
                            "relaytic_handoff_remote_supervision",
                            {
                                "run_dir": str(run_dir),
                                "to_actor_type": "agent",
                                "to_actor_name": "mcp-test",
                                "from_actor_type": "operator",
                                "from_actor_name": "unit-test",
                                "reason": "Continue from the MCP host.",
                                "config_path": str(config_path),
                            },
                        )
                        remote_handoff_payload = _structured_payload(remote_handoff_result)
                        assert remote_handoff_payload["surface_payload"]["remote"]["current_supervisor_type"] == "agent"

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
