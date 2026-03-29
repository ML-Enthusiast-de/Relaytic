"""Host-neutral Relaytic operations exposed through interoperability layers."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from relaytic.interoperability.models import InteropToolSpec


INTEROPERABILITY_SCHEMA_VERSION = "relaytic.interoperability_inventory.v1"


def relaytic_run(
    *,
    data_path: str,
    run_dir: str | None = None,
    text: str | None = None,
    config_path: str | None = None,
    run_id: str | None = None,
    actor_type: str = "agent",
    actor_name: str | None = None,
    channel: str = "mcp",
    sheet_name: str | None = None,
    header_row: int | None = None,
    data_start_row: int | None = None,
    source_type: str = "auto",
    source_table: str | None = None,
    sql_query: str | None = None,
    stream_window_rows: int = 5000,
    stream_format: str = "auto",
    materialized_format: str = "auto",
    timestamp_column: str | None = None,
    overwrite: bool = False,
    labels: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Execute the current Relaytic MVP path end to end."""
    cli = _cli()
    resolved_run_dir = _resolve_run_dir(run_dir=run_dir, data_path=data_path)
    return cli._run_access_flow(
        run_dir=str(resolved_run_dir),
        data_path=data_path,
        source_type=source_type,
        source_table=source_table,
        sql_query=sql_query,
        stream_window_rows=stream_window_rows,
        stream_format=stream_format,
        materialized_format=materialized_format,
        config_path=config_path,
        run_id=run_id,
        text=text,
        text_file=None,
        actor_type=_normalize_actor_type(actor_type),
        actor_name=actor_name,
        channel=channel,
        sheet_name=sheet_name,
        header_row=header_row,
        data_start_row=data_start_row,
        timestamp_column=timestamp_column,
        overwrite=overwrite,
        labels=_normalize_labels(labels),
    )


def relaytic_show_run(*, run_dir: str) -> dict[str, Any]:
    """Render the current summary surface for a Relaytic run."""
    cli = _cli()
    return cli._show_access_run(run_dir=run_dir)


def relaytic_show_runtime(*, run_dir: str, limit: int = 20) -> dict[str, Any]:
    """Render the current runtime gateway surface for a Relaytic run."""
    cli = _cli()
    return cli._show_runtime_surface(run_dir=run_dir, limit=max(1, int(limit)))


def relaytic_show_control(*, run_dir: str) -> dict[str, Any]:
    """Render the current Slice 10C control surface for a Relaytic run."""
    cli = _cli()
    return cli._show_control_surface(run_dir=run_dir)


def relaytic_show_mission_control(*, run_dir: str | None = None, expected_profile: str = "full") -> dict[str, Any]:
    """Render the current Slice 11B/11C mission-control surface for a Relaytic run or onboarding state."""
    cli = _cli()
    return cli._show_mission_control_surface(
        run_dir=run_dir,
        output_dir=None,
        config_path=None,
        expected_profile=expected_profile,
    )


def relaytic_show_dojo(*, run_dir: str) -> dict[str, Any]:
    """Render the current Slice 12 dojo surface for a Relaytic run."""
    cli = _cli()
    return cli._show_dojo_surface(run_dir=run_dir)


def relaytic_show_pulse(*, run_dir: str) -> dict[str, Any]:
    """Render the current Slice 12A pulse surface for a Relaytic run."""
    cli = _cli()
    return cli._show_pulse_surface(run_dir=run_dir)


def relaytic_show_trace(*, run_dir: str) -> dict[str, Any]:
    """Render the current Slice 12B trace surface for a Relaytic run."""
    cli = _cli()
    return cli._show_trace_surface(run_dir=run_dir)


def relaytic_replay_trace(*, run_dir: str) -> dict[str, Any]:
    """Render the current Slice 12B replay surface for a Relaytic run."""
    cli = _cli()
    return cli._replay_trace_surface(run_dir=run_dir)


def relaytic_run_agent_evals(
    *,
    run_dir: str,
    config_path: str | None = None,
    run_id: str | None = None,
    overwrite: bool = False,
    labels: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Execute the Slice 12B eval harness for an existing Relaytic run."""
    cli = _cli()
    return cli._run_evals_phase(
        run_dir=run_dir,
        config_path=config_path,
        run_id=run_id,
        overwrite=overwrite,
        labels=_normalize_labels(labels),
        runtime_surface="mcp",
        runtime_command="relaytic_run_agent_evals",
    )


def relaytic_show_agent_evals(*, run_dir: str) -> dict[str, Any]:
    """Render the current Slice 12B eval surface for a Relaytic run."""
    cli = _cli()
    return cli._show_evals_surface(run_dir=run_dir)


def relaytic_get_status(*, run_dir: str) -> dict[str, Any]:
    """Render the completion-governor status for a Relaytic run."""
    cli = _cli()
    return cli._show_completion_status(run_dir=run_dir)


def relaytic_predict(
    *,
    run_dir: str,
    data_path: str,
    source_type: str = "auto",
    source_table: str | None = None,
    sql_query: str | None = None,
    stream_window_rows: int = 5000,
    stream_format: str = "auto",
    materialized_format: str = "auto",
    sheet_name: str | None = None,
    header_row: int | None = None,
    data_start_row: int | None = None,
    delimiter: str | None = None,
    decision_threshold: float | None = None,
    output_path: str | None = None,
) -> dict[str, Any]:
    """Run inference from an existing Relaytic run directory."""
    cli = _cli()
    return cli.run_inference_from_artifacts(
        data_path=data_path,
        run_dir=run_dir,
        source_type=source_type,
        source_table=source_table,
        sql_query=sql_query,
        stream_window_rows=stream_window_rows,
        stream_format=stream_format,
        materialized_format=materialized_format,
        sheet_name=sheet_name,
        header_row=header_row,
        data_start_row=data_start_row,
        delimiter=delimiter,
        decision_threshold=decision_threshold,
        output_path=output_path,
    )


def relaytic_intake_interpret(
    *,
    text: str,
    run_dir: str | None = None,
    data_path: str | None = None,
    config_path: str | None = None,
    run_id: str | None = None,
    actor_type: str = "agent",
    actor_name: str | None = None,
    channel: str = "mcp",
    sheet_name: str | None = None,
    header_row: int | None = None,
    data_start_row: int | None = None,
    overwrite: bool = False,
    labels: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Translate free-form user or agent input into Relaytic foundation artifacts."""
    cli = _cli()
    resolved_run_dir = _resolve_run_dir(run_dir=run_dir, data_path=data_path)
    return cli._run_intake_phase(
        run_dir=str(resolved_run_dir),
        message=text,
        actor_type=_normalize_actor_type(actor_type),
        actor_name=actor_name,
        channel=channel,
        config_path=config_path,
        run_id=run_id,
        data_path=data_path,
        sheet_name=sheet_name,
        header_row=header_row,
        data_start_row=data_start_row,
        overwrite=overwrite,
        labels=_normalize_labels(labels),
        runtime_surface="mcp",
        runtime_command="relaytic_intake_interpret",
    )


def relaytic_investigate_dataset(
    *,
    data_path: str,
    run_dir: str | None = None,
    config_path: str | None = None,
    run_id: str | None = None,
    sheet_name: str | None = None,
    header_row: int | None = None,
    data_start_row: int | None = None,
    timestamp_column: str | None = None,
    overwrite: bool = False,
    labels: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Run the Scout/Scientist/Focus Council investigation path."""
    cli = _cli()
    resolved_run_dir = _resolve_run_dir(run_dir=run_dir, data_path=data_path)
    return cli._run_investigation_phase(
        run_dir=str(resolved_run_dir),
        data_path=data_path,
        config_path=config_path,
        run_id=run_id,
        sheet_name=sheet_name,
        header_row=header_row,
        data_start_row=data_start_row,
        timestamp_column=timestamp_column,
        overwrite=overwrite,
        labels=_normalize_labels(labels),
        runtime_surface="mcp",
        runtime_command="relaytic_investigate_dataset",
    )


def relaytic_generate_plan(
    *,
    data_path: str,
    run_dir: str | None = None,
    config_path: str | None = None,
    run_id: str | None = None,
    sheet_name: str | None = None,
    header_row: int | None = None,
    data_start_row: int | None = None,
    timestamp_column: str | None = None,
    overwrite: bool = False,
    execute_route: bool = True,
    labels: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Build the Strategist plan and optionally execute the selected Builder route."""
    cli = _cli()
    resolved_run_dir = _resolve_run_dir(run_dir=run_dir, data_path=data_path)
    return cli._run_planning_phase(
        run_dir=str(resolved_run_dir),
        data_path=data_path,
        config_path=config_path,
        run_id=run_id,
        sheet_name=sheet_name,
        header_row=header_row,
        data_start_row=data_start_row,
        timestamp_column=timestamp_column,
        overwrite=overwrite,
        labels=_normalize_labels(labels),
        execute_route=execute_route,
        runtime_surface="mcp",
        runtime_command="relaytic_generate_plan",
    )


def relaytic_run_evidence_review(
    *,
    data_path: str,
    run_dir: str,
    config_path: str | None = None,
    run_id: str | None = None,
    sheet_name: str | None = None,
    header_row: int | None = None,
    data_start_row: int | None = None,
    timestamp_column: str | None = None,
    overwrite: bool = False,
    labels: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Challenge, ablate, and audit the current Relaytic route."""
    cli = _cli()
    return cli._run_evidence_phase(
        run_dir=run_dir,
        data_path=data_path,
        config_path=config_path,
        run_id=run_id,
        sheet_name=sheet_name,
        header_row=header_row,
        data_start_row=data_start_row,
        timestamp_column=timestamp_column,
        overwrite=overwrite,
        labels=_normalize_labels(labels),
        planning_state=None,
        runtime_surface="mcp",
        runtime_command="relaytic_run_evidence_review",
    )


def relaytic_review_completion(
    *,
    run_dir: str,
    config_path: str | None = None,
    run_id: str | None = None,
    overwrite: bool = False,
    labels: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Recompute the completion governor for an existing run."""
    cli = _cli()
    return cli._run_completion_phase(
        run_dir=run_dir,
        config_path=config_path,
        run_id=run_id,
        overwrite=overwrite,
        labels=_normalize_labels(labels),
        runtime_surface="mcp",
        runtime_command="relaytic_review_completion",
    )


def relaytic_run_intelligence(
    *,
    run_dir: str,
    config_path: str | None = None,
    run_id: str | None = None,
    overwrite: bool = False,
    labels: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Execute the Slice 09 intelligence review for an existing run."""
    cli = _cli()
    return cli._run_intelligence_phase(
        run_dir=run_dir,
        config_path=config_path,
        run_id=run_id,
        overwrite=overwrite,
        labels=_normalize_labels(labels),
        runtime_surface="mcp",
        runtime_command="relaytic_run_intelligence",
    )


def relaytic_show_intelligence(*, run_dir: str) -> dict[str, Any]:
    """Render the current Slice 09 intelligence surface for a run."""
    cli = _cli()
    return cli._show_intelligence_surface(run_dir=run_dir)


def relaytic_gather_research(
    *,
    run_dir: str,
    config_path: str | None = None,
    run_id: str | None = None,
    overwrite: bool = False,
    labels: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Execute the Slice 09D research retrieval layer for an existing run."""
    cli = _cli()
    return cli._run_research_phase(
        run_dir=run_dir,
        config_path=config_path,
        run_id=run_id,
        overwrite=overwrite,
        labels=_normalize_labels(labels),
        runtime_surface="mcp",
        runtime_command="relaytic_gather_research",
    )


def relaytic_show_research(*, run_dir: str) -> dict[str, Any]:
    """Render the current Slice 09D research surface for a run."""
    cli = _cli()
    return cli._show_research_surface(run_dir=run_dir)


def relaytic_run_benchmark(
    *,
    run_dir: str,
    data_path: str | None = None,
    config_path: str | None = None,
    run_id: str | None = None,
    overwrite: bool = False,
    labels: dict[str, str] | None = None,
    incumbent_path: str | None = None,
    incumbent_kind: str | None = None,
    incumbent_name: str | None = None,
) -> dict[str, Any]:
    """Execute the Slice 11/11A benchmark parity and incumbent-challenge layer for an existing run."""
    cli = _cli()
    return cli._run_benchmark_phase(
        run_dir=run_dir,
        data_path=data_path,
        config_path=config_path,
        run_id=run_id,
        overwrite=overwrite,
        labels=_normalize_labels(labels),
        incumbent_path=incumbent_path,
        incumbent_kind=incumbent_kind,
        incumbent_name=incumbent_name,
        runtime_surface="mcp",
        runtime_command="relaytic_run_benchmark",
    )


def relaytic_show_benchmark(*, run_dir: str) -> dict[str, Any]:
    """Render the current Slice 11/11A benchmark and incumbent-challenge surface for a run."""
    cli = _cli()
    return cli._show_benchmark_surface(run_dir=run_dir)


def relaytic_review_decision(
    *,
    run_dir: str,
    config_path: str | None = None,
    run_id: str | None = None,
    overwrite: bool = False,
    labels: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Execute the Slice 10A decision-lab layer for an existing run."""
    cli = _cli()
    return cli._run_decision_phase(
        run_dir=run_dir,
        config_path=config_path,
        run_id=run_id,
        overwrite=overwrite,
        labels=_normalize_labels(labels),
        runtime_surface="mcp",
        runtime_command="relaytic_review_decision",
    )


def relaytic_review_dojo(
    *,
    run_dir: str,
    config_path: str | None = None,
    run_id: str | None = None,
    overwrite: bool = True,
    labels: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Execute the Slice 12 dojo review for an existing run."""
    cli = _cli()
    return cli._run_dojo_phase(
        run_dir=run_dir,
        config_path=config_path,
        run_id=run_id,
        overwrite=overwrite,
        labels=_normalize_labels(labels),
        runtime_surface="mcp",
        runtime_command="relaytic_review_dojo",
    )


def relaytic_review_pulse(
    *,
    run_dir: str,
    config_path: str | None = None,
    run_id: str | None = None,
    overwrite: bool = True,
    labels: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Execute the Slice 12A pulse review for an existing run."""
    cli = _cli()
    return cli._run_pulse_phase(
        run_dir=run_dir,
        config_path=config_path,
        run_id=run_id,
        overwrite=overwrite,
        labels=_normalize_labels(labels),
        runtime_surface="mcp",
        runtime_command="relaytic_review_pulse",
    )


def relaytic_show_decision(*, run_dir: str) -> dict[str, Any]:
    """Render the current Slice 10A decision-lab surface for a run."""
    cli = _cli()
    return cli._show_decision_surface(run_dir=run_dir)


def relaytic_show_assist(*, run_dir: str, config_path: str | None = None) -> dict[str, Any]:
    """Render the current Slice 09E communicative assist surface for a run."""
    cli = _cli()
    return cli._show_assist_surface(run_dir=run_dir, config_path=config_path)


def relaytic_assist_turn(
    *,
    run_dir: str,
    message: str,
    data_path: str | None = None,
    config_path: str | None = None,
) -> dict[str, Any]:
    """Send one communicative assist turn into Relaytic for explanation, navigation, or takeover."""
    cli = _cli()
    return cli._run_assist_turn(
        run_dir=run_dir,
        message=message,
        config_path=config_path,
        data_path=data_path,
        runtime_surface="mcp",
        runtime_command="relaytic_assist_turn",
        actor_type="agent",
    )


def relaytic_review_lifecycle(
    *,
    run_dir: str,
    data_path: str | None = None,
    config_path: str | None = None,
    run_id: str | None = None,
    overwrite: bool = False,
    labels: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Recompute lifecycle posture for an existing run."""
    cli = _cli()
    return cli._run_lifecycle_phase(
        run_dir=run_dir,
        data_path=data_path,
        config_path=config_path,
        run_id=run_id,
        overwrite=overwrite,
        labels=_normalize_labels(labels),
        runtime_surface="mcp",
        runtime_command="relaytic_review_lifecycle",
    )


def relaytic_run_autonomy(
    *,
    run_dir: str,
    data_path: str | None = None,
    config_path: str | None = None,
    run_id: str | None = None,
    overwrite: bool = False,
    labels: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Execute the Slice 09C autonomy loop for an existing run."""
    cli = _cli()
    return cli._run_autonomy_phase(
        run_dir=run_dir,
        data_path=data_path,
        config_path=config_path,
        run_id=run_id,
        overwrite=overwrite,
        labels=_normalize_labels(labels),
        runtime_surface="mcp",
        runtime_command="relaytic_run_autonomy",
    )


def relaytic_show_autonomy(*, run_dir: str) -> dict[str, Any]:
    """Render the current Slice 09C autonomy surface for a run."""
    cli = _cli()
    return cli._show_autonomy_surface(run_dir=run_dir)


def relaytic_show_lifecycle(*, run_dir: str, data_path: str | None = None) -> dict[str, Any]:
    """Render the current lifecycle surface for a run."""
    cli = _cli()
    return cli._show_lifecycle_surface(run_dir=run_dir, data_path=data_path)


def relaytic_doctor(*, expected_profile: str = "core") -> dict[str, Any]:
    """Return the current Relaytic runtime/install health report."""
    from relaytic.ui.doctor import build_doctor_report

    return build_doctor_report(expected_profile=expected_profile)


def relaytic_server_info() -> dict[str, Any]:
    """Return a compact server-health payload suitable for transport checks."""
    tool_specs = build_interoperability_tool_specs()
    return {
        "status": "ok",
        "product": "Relaytic",
        "tool_count": len(tool_specs),
        "inspection_tools": [
            "relaytic_server_info",
            "relaytic_show_run",
            "relaytic_show_runtime",
            "relaytic_show_control",
            "relaytic_show_mission_control",
            "relaytic_show_pulse",
            "relaytic_show_trace",
            "relaytic_replay_trace",
            "relaytic_show_agent_evals",
            "relaytic_get_status",
            "relaytic_show_intelligence",
            "relaytic_show_research",
            "relaytic_show_benchmark",
            "relaytic_show_decision",
            "relaytic_show_assist",
            "relaytic_show_lifecycle",
            "relaytic_show_autonomy",
            "relaytic_doctor",
            "relaytic_integrations_show",
        ],
        "workflow_tools": [
            "relaytic_run",
            "relaytic_intake_interpret",
            "relaytic_investigate_dataset",
            "relaytic_generate_plan",
            "relaytic_run_evidence_review",
            "relaytic_run_intelligence",
            "relaytic_gather_research",
            "relaytic_run_benchmark",
            "relaytic_review_decision",
            "relaytic_review_pulse",
            "relaytic_run_agent_evals",
            "relaytic_assist_turn",
            "relaytic_review_completion",
            "relaytic_review_lifecycle",
            "relaytic_run_autonomy",
            "relaytic_predict",
        ],
    }


def relaytic_integrations_show() -> dict[str, Any]:
    """Return the wired optional-library inventory."""
    from relaytic.integrations import build_integration_inventory

    return {
        "status": "ok",
        "schema_version": "relaytic.integrations_inventory.v1",
        "integrations": build_integration_inventory(),
    }


def build_interoperability_tool_specs() -> list[InteropToolSpec]:
    """Return the canonical host-neutral tool contract for Relaytic."""
    return [
        InteropToolSpec(
            name="relaytic_server_info",
            title="Relaytic Server Info",
            description="Return a compact health and capability summary for the Relaytic MCP server.",
            category="inspection",
            annotations={"readOnlyHint": True, "idempotentHint": True, "destructiveHint": False, "openWorldHint": False},
            handler=relaytic_server_info,
        ),
        InteropToolSpec(
            name="relaytic_run",
            title="Run Relaytic",
            description="Run the Relaytic MVP flow end to end on a dataset, optionally using free-form intent text.",
            category="workflow",
            annotations={"readOnlyHint": False, "idempotentHint": False, "destructiveHint": False, "openWorldHint": False},
            handler=relaytic_run,
        ),
        InteropToolSpec(
            name="relaytic_show_run",
            title="Show Relaytic Run",
            description="Render the current Relaytic run summary for humans and agents without modifying the run beyond summary materialization.",
            category="inspection",
            annotations={"readOnlyHint": True, "idempotentHint": True, "destructiveHint": False, "openWorldHint": False},
            handler=relaytic_show_run,
        ),
        InteropToolSpec(
            name="relaytic_show_runtime",
            title="Show Relaytic Runtime",
            description="Render the current Relaytic runtime gateway state, including recent events, hook activity, and capability enforcement.",
            category="inspection",
            annotations={"readOnlyHint": True, "idempotentHint": True, "destructiveHint": False, "openWorldHint": False},
            handler=relaytic_show_runtime,
        ),
        InteropToolSpec(
            name="relaytic_show_control",
            title="Show Relaytic Control",
            description="Render the current Slice 10C behavioral control contract, override decision, and causal steering memory for a Relaytic run.",
            category="inspection",
            annotations={"readOnlyHint": True, "idempotentHint": True, "destructiveHint": False, "openWorldHint": False},
            handler=relaytic_show_control,
        ),
        InteropToolSpec(
            name="relaytic_show_mission_control",
            title="Show Relaytic Mission Control",
            description="Render the current Slice 11B/11C operator control-center state, onboarding posture, clarity surfaces, and launch metadata for a Relaytic run.",
            category="inspection",
            annotations={"readOnlyHint": True, "idempotentHint": True, "destructiveHint": False, "openWorldHint": False},
            handler=relaytic_show_mission_control,
        ),
        InteropToolSpec(
            name="relaytic_show_dojo",
            title="Show Relaytic Dojo",
            description="Render the current Slice 12 guarded self-improvement surface, including promotions, rejections, and rollback-ready state for a Relaytic run.",
            category="inspection",
            annotations={"readOnlyHint": True, "idempotentHint": True, "destructiveHint": False, "openWorldHint": False},
            handler=relaytic_show_dojo,
        ),
        InteropToolSpec(
            name="relaytic_show_pulse",
            title="Show Relaytic Pulse",
            description="Render the current Slice 12A lab pulse surface, including skip reasons, watchlists, innovation leads, and bounded follow-up state for a Relaytic run.",
            category="inspection",
            annotations={"readOnlyHint": True, "idempotentHint": True, "destructiveHint": False, "openWorldHint": False},
            handler=relaytic_show_pulse,
        ),
        InteropToolSpec(
            name="relaytic_show_trace",
            title="Show Relaytic Trace",
            description="Render the current Slice 12B canonical trace surface, including competing claims, deterministic adjudication, and winning-action truth for a Relaytic run.",
            category="inspection",
            annotations={"readOnlyHint": True, "idempotentHint": True, "destructiveHint": False, "openWorldHint": False},
            handler=relaytic_show_trace,
        ),
        InteropToolSpec(
            name="relaytic_replay_trace",
            title="Replay Relaytic Trace",
            description="Render the current Slice 12B replay timeline so a host can inspect why Relaytic chose the winning action over competing claims.",
            category="inspection",
            annotations={"readOnlyHint": True, "idempotentHint": True, "destructiveHint": False, "openWorldHint": False},
            handler=relaytic_replay_trace,
        ),
        InteropToolSpec(
            name="relaytic_show_agent_evals",
            title="Show Relaytic Agent Evals",
            description="Render the current Slice 12B protocol, security, and deterministic-debate proof surface for a Relaytic run.",
            category="inspection",
            annotations={"readOnlyHint": True, "idempotentHint": True, "destructiveHint": False, "openWorldHint": False},
            handler=relaytic_show_agent_evals,
        ),
        InteropToolSpec(
            name="relaytic_get_status",
            title="Get Relaytic Status",
            description="Read the Slice 07 completion-governor status for a Relaytic run.",
            category="inspection",
            annotations={"readOnlyHint": True, "idempotentHint": True, "destructiveHint": False, "openWorldHint": False},
            handler=relaytic_get_status,
        ),
        InteropToolSpec(
            name="relaytic_show_intelligence",
            title="Show Relaytic Intelligence",
            description="Render the current Slice 09 semantic debate and uncertainty surface for a Relaytic run.",
            category="inspection",
            annotations={"readOnlyHint": True, "idempotentHint": True, "destructiveHint": False, "openWorldHint": False},
            handler=relaytic_show_intelligence,
        ),
        InteropToolSpec(
            name="relaytic_show_research",
            title="Show Relaytic Research",
            description="Render the current Slice 09D research, method-transfer, and benchmark-reference surface for a Relaytic run.",
            category="inspection",
            annotations={"readOnlyHint": True, "idempotentHint": True, "destructiveHint": False, "openWorldHint": False},
            handler=relaytic_show_research,
        ),
        InteropToolSpec(
            name="relaytic_show_benchmark",
            title="Show Relaytic Benchmark",
            description="Render the current Slice 11/11A benchmark parity, reference comparison, and incumbent-challenge surface for a Relaytic run.",
            category="inspection",
            annotations={"readOnlyHint": True, "idempotentHint": True, "destructiveHint": False, "openWorldHint": False},
            handler=relaytic_show_benchmark,
        ),
        InteropToolSpec(
            name="relaytic_show_decision",
            title="Show Relaytic Decision Lab",
            description="Render the current Slice 10A decision-world model, controller policy, and local data-fabric surface for a Relaytic run.",
            category="inspection",
            annotations={"readOnlyHint": True, "idempotentHint": True, "destructiveHint": False, "openWorldHint": False},
            handler=relaytic_show_decision,
        ),
        InteropToolSpec(
            name="relaytic_show_assist",
            title="Show Relaytic Assist",
            description="Render the current Slice 09E communicative assist state, guidance, and connection options for a Relaytic run.",
            category="inspection",
            annotations={"readOnlyHint": True, "idempotentHint": True, "destructiveHint": False, "openWorldHint": False},
            handler=relaytic_show_assist,
        ),
        InteropToolSpec(
            name="relaytic_predict",
            title="Predict With Relaytic",
            description="Run inference from an existing Relaytic run directory against a new dataset.",
            category="workflow",
            annotations={"readOnlyHint": False, "idempotentHint": False, "destructiveHint": False, "openWorldHint": False},
            handler=relaytic_predict,
        ),
        InteropToolSpec(
            name="relaytic_intake_interpret",
            title="Interpret Relaytic Intake",
            description="Translate free-form human or agent input into Relaytic mandate/context/intake artifacts.",
            category="workflow",
            annotations={"readOnlyHint": False, "idempotentHint": False, "destructiveHint": False, "openWorldHint": False},
            handler=relaytic_intake_interpret,
        ),
        InteropToolSpec(
            name="relaytic_investigate_dataset",
            title="Investigate Dataset",
            description="Run the current Relaytic investigation and focus-selection specialists on a dataset.",
            category="workflow",
            annotations={"readOnlyHint": False, "idempotentHint": False, "destructiveHint": False, "openWorldHint": False},
            handler=relaytic_investigate_dataset,
        ),
        InteropToolSpec(
            name="relaytic_generate_plan",
            title="Generate Relaytic Plan",
            description="Build the Strategist plan and optionally execute the selected Builder route for a dataset.",
            category="workflow",
            annotations={"readOnlyHint": False, "idempotentHint": False, "destructiveHint": False, "openWorldHint": False},
            handler=relaytic_generate_plan,
        ),
        InteropToolSpec(
            name="relaytic_run_evidence_review",
            title="Run Evidence Review",
            description="Execute the challenger, ablation, and audit layer for an existing Relaytic run.",
            category="workflow",
            annotations={"readOnlyHint": False, "idempotentHint": False, "destructiveHint": False, "openWorldHint": False},
            handler=relaytic_run_evidence_review,
        ),
        InteropToolSpec(
            name="relaytic_run_intelligence",
            title="Run Intelligence Review",
            description="Execute the Slice 09 structured semantic debate layer for an existing Relaytic run.",
            category="workflow",
            annotations={"readOnlyHint": False, "idempotentHint": False, "destructiveHint": False, "openWorldHint": False},
            handler=relaytic_run_intelligence,
        ),
        InteropToolSpec(
            name="relaytic_gather_research",
            title="Gather Research",
            description="Execute the Slice 09D privacy-safe external research retrieval layer for an existing Relaytic run.",
            category="workflow",
            annotations={"readOnlyHint": False, "idempotentHint": False, "destructiveHint": False, "openWorldHint": False},
            handler=relaytic_gather_research,
        ),
        InteropToolSpec(
            name="relaytic_run_benchmark",
            title="Run Benchmark Review",
            description="Execute the Slice 11/11A benchmark parity and incumbent-challenge layer for an existing Relaytic run.",
            category="workflow",
            annotations={"readOnlyHint": False, "idempotentHint": False, "destructiveHint": False, "openWorldHint": False},
            handler=relaytic_run_benchmark,
        ),
        InteropToolSpec(
            name="relaytic_review_decision",
            title="Review Decision Lab",
            description="Execute the Slice 10A decision-world model, controller logic, and method-compilation layer for an existing Relaytic run.",
            category="workflow",
            annotations={"readOnlyHint": False, "idempotentHint": False, "destructiveHint": False, "openWorldHint": False},
            handler=relaytic_review_decision,
        ),
        InteropToolSpec(
            name="relaytic_review_dojo",
            title="Review Dojo",
            description="Execute the Slice 12 guarded self-improvement layer for an existing Relaytic run under explicit quarantine gates.",
            category="workflow",
            annotations={"readOnlyHint": False, "idempotentHint": False, "destructiveHint": False, "openWorldHint": False},
            handler=relaytic_review_dojo,
        ),
        InteropToolSpec(
            name="relaytic_review_pulse",
            title="Review Pulse",
            description="Execute the Slice 12A lab pulse review for an existing Relaytic run, writing explicit skip, watchlist, innovation-watch, and bounded follow-up artifacts.",
            category="workflow",
            annotations={"readOnlyHint": False, "idempotentHint": False, "destructiveHint": False, "openWorldHint": False},
            handler=relaytic_review_pulse,
        ),
        InteropToolSpec(
            name="relaytic_run_agent_evals",
            title="Run Agent Evals",
            description="Execute the Slice 12B protocol, security, and deterministic-debate proof harness for an existing Relaytic run.",
            category="workflow",
            annotations={"readOnlyHint": False, "idempotentHint": False, "destructiveHint": False, "openWorldHint": False},
            handler=relaytic_run_agent_evals,
        ),
        InteropToolSpec(
            name="relaytic_assist_turn",
            title="Assist Turn",
            description="Send one communicative turn so Relaytic can explain state, guide connection options, rerun a stage, or take over safely.",
            category="workflow",
            annotations={"readOnlyHint": False, "idempotentHint": False, "destructiveHint": False, "openWorldHint": False},
            handler=relaytic_assist_turn,
        ),
        InteropToolSpec(
            name="relaytic_review_completion",
            title="Review Completion",
            description="Execute the completion-governor review for an existing Relaytic run.",
            category="workflow",
            annotations={"readOnlyHint": False, "idempotentHint": False, "destructiveHint": False, "openWorldHint": False},
            handler=relaytic_review_completion,
        ),
        InteropToolSpec(
            name="relaytic_review_lifecycle",
            title="Review Lifecycle",
            description="Execute the lifecycle-governor review for an existing Relaytic run.",
            category="workflow",
            annotations={"readOnlyHint": False, "idempotentHint": False, "destructiveHint": False, "openWorldHint": False},
            handler=relaytic_review_lifecycle,
        ),
        InteropToolSpec(
            name="relaytic_show_lifecycle",
            title="Show Lifecycle",
            description="Render the current lifecycle posture for a Relaytic run.",
            category="inspection",
            annotations={"readOnlyHint": True, "idempotentHint": True, "destructiveHint": False, "openWorldHint": False},
            handler=relaytic_show_lifecycle,
        ),
        InteropToolSpec(
            name="relaytic_run_autonomy",
            title="Run Autonomy Loop",
            description="Execute the Slice 09C bounded autonomous follow-up loop for an existing Relaytic run.",
            category="workflow",
            annotations={"readOnlyHint": False, "idempotentHint": False, "destructiveHint": False, "openWorldHint": False},
            handler=relaytic_run_autonomy,
        ),
        InteropToolSpec(
            name="relaytic_show_autonomy",
            title="Show Autonomy",
            description="Render the current autonomy-loop posture and branch results for a Relaytic run.",
            category="inspection",
            annotations={"readOnlyHint": True, "idempotentHint": True, "destructiveHint": False, "openWorldHint": False},
            handler=relaytic_show_autonomy,
        ),
        InteropToolSpec(
            name="relaytic_doctor",
            title="Relaytic Doctor",
            description="Return Relaytic install, dependency, interoperability, and adapter health information.",
            category="inspection",
            annotations={"readOnlyHint": True, "idempotentHint": True, "destructiveHint": False, "openWorldHint": False},
            handler=relaytic_doctor,
        ),
        InteropToolSpec(
            name="relaytic_integrations_show",
            title="Show Integrations",
            description="List mature optional libraries and whether Relaytic can use them locally.",
            category="inspection",
            annotations={"readOnlyHint": True, "idempotentHint": True, "destructiveHint": False, "openWorldHint": False},
            handler=relaytic_integrations_show,
        ),
    ]


def _resolve_run_dir(*, run_dir: str | None, data_path: str | None) -> Path:
    if run_dir:
        return Path(run_dir)
    if not data_path:
        raise ValueError("Either `run_dir` or `data_path` is required.")
    cli = _cli()
    return Path(cli._default_access_run_dir(data_path=data_path))


def _normalize_actor_type(actor_type: str) -> str:
    normalized = str(actor_type or "agent").strip().lower()
    if normalized == "human":
        return "operator"
    if normalized not in {"user", "operator", "agent"}:
        return "agent"
    return normalized


def _normalize_labels(labels: dict[str, str] | None) -> dict[str, str] | None:
    if not labels:
        return None
    normalized: dict[str, str] = {}
    for key, value in labels.items():
        key_text = str(key).strip()
        value_text = str(value).strip()
        if key_text:
            normalized[key_text] = value_text
    return normalized or None


def _cli() -> Any:
    from relaytic.ui import cli

    return cli
