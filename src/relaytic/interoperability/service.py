"""Host-neutral Relaytic operations exposed through interoperability layers."""

from __future__ import annotations

import inspect
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


def relaytic_show_event_bus(*, run_dir: str, config_path: str | None = None) -> dict[str, Any]:
    """Render the current Slice 13B event-bus surface for a Relaytic run."""
    cli = _cli()
    return cli._show_event_bus_surface(run_dir=run_dir, config_path=config_path)


def relaytic_show_permissions(*, run_dir: str, config_path: str | None = None) -> dict[str, Any]:
    """Render the current Slice 13B permission-mode surface for a Relaytic run."""
    cli = _cli()
    return cli._show_permission_surface(run_dir=run_dir, config_path=config_path)


def relaytic_check_permission(
    *,
    run_dir: str,
    action: str,
    config_path: str | None = None,
    mode: str | None = None,
    actor_type: str = "agent",
    actor_name: str | None = None,
) -> dict[str, Any]:
    """Evaluate one action against the current or overridden permission mode and append the decision."""
    cli = _cli()
    return cli._check_permission_surface(
        run_dir=run_dir,
        action_id=action,
        config_path=config_path,
        mode=mode,
        actor_type=_normalize_actor_type(actor_type),
        actor_name=actor_name,
    )


def relaytic_decide_permission(
    *,
    run_dir: str,
    request_id: str,
    decision: str,
    config_path: str | None = None,
    actor_type: str = "agent",
    actor_name: str | None = None,
) -> dict[str, Any]:
    """Approve or deny one pending permission request and append the decision."""
    cli = _cli()
    return cli._decide_permission_surface(
        run_dir=run_dir,
        request_id=request_id,
        decision=decision,
        config_path=config_path,
        actor_type=_normalize_actor_type(actor_type),
        actor_name=actor_name,
    )


def relaytic_show_control(*, run_dir: str) -> dict[str, Any]:
    """Render the current Slice 10C control surface for a Relaytic run."""
    cli = _cli()
    return cli._show_control_surface(run_dir=run_dir)


def relaytic_show_mission_control(*, run_dir: str | None = None, expected_profile: str = "full") -> dict[str, Any]:
    """Render the current Slice 15 mission-control surface for a Relaytic run or onboarding state."""
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


def relaytic_show_search(*, run_dir: str, config_path: str | None = None) -> dict[str, Any]:
    """Render the current Slice 13 search-controller surface for a Relaytic run."""
    cli = _cli()
    return cli._show_search_surface(run_dir=run_dir, config_path=config_path)


def relaytic_show_daemon(*, run_dir: str, config_path: str | None = None) -> dict[str, Any]:
    """Render the current Slice 13C bounded background-job surface for a Relaytic run."""
    cli = _cli()
    return cli._show_daemon_surface(run_dir=run_dir, config_path=config_path)


def relaytic_show_remote_control(*, run_dir: str, config_path: str | None = None) -> dict[str, Any]:
    """Render the current Slice 14A remote-supervision state for a Relaytic run."""
    cli = _cli()
    return cli._show_remote_control_surface(run_dir=run_dir, config_path=config_path)


def relaytic_decide_remote_approval(
    *,
    run_dir: str,
    request_id: str,
    decision: str,
    config_path: str | None = None,
    actor_type: str = "agent",
    actor_name: str | None = None,
) -> dict[str, Any]:
    """Approve or deny one pending request through the Slice 14A remote-supervision surface."""
    cli = _cli()
    return cli._decide_remote_approval_surface(
        run_dir=run_dir,
        request_id=request_id,
        decision=decision,
        config_path=config_path,
        actor_type=_normalize_actor_type(actor_type),
        actor_name=actor_name,
    )


def relaytic_handoff_remote_supervision(
    *,
    run_dir: str,
    to_actor_type: str,
    to_actor_name: str | None = None,
    from_actor_type: str = "agent",
    from_actor_name: str | None = None,
    reason: str | None = None,
    config_path: str | None = None,
) -> dict[str, Any]:
    """Transfer the current remote-supervision role without creating a separate authority path."""
    cli = _cli()
    return cli._handoff_remote_supervision_surface(
        run_dir=run_dir,
        to_actor_type=_normalize_actor_type(to_actor_type),
        to_actor_name=to_actor_name,
        from_actor_type=_normalize_actor_type(from_actor_type),
        from_actor_name=from_actor_name,
        reason=reason,
        config_path=config_path,
    )


def relaytic_run_background_job(
    *,
    run_dir: str,
    job_id: str,
    config_path: str | None = None,
    actor_type: str = "agent",
    actor_name: str | None = None,
) -> dict[str, Any]:
    """Start one bounded background job, requesting approval first when policy requires it."""
    cli = _cli()
    return cli._run_background_job_surface(
        run_dir=run_dir,
        job_id=job_id,
        config_path=config_path,
        actor_type=_normalize_actor_type(actor_type),
        actor_name=actor_name,
    )


def relaytic_resume_background_job(
    *,
    run_dir: str,
    job_id: str,
    config_path: str | None = None,
    actor_type: str = "agent",
    actor_name: str | None = None,
) -> dict[str, Any]:
    """Resume one paused or stale background job from its explicit checkpoint."""
    cli = _cli()
    return cli._resume_background_job_surface(
        run_dir=run_dir,
        job_id=job_id,
        config_path=config_path,
        actor_type=_normalize_actor_type(actor_type),
        actor_name=actor_name,
    )


def relaytic_scan_release_safety(
    *,
    target_path: str | None = None,
    state_dir: str | None = None,
) -> dict[str, Any]:
    """Execute the Slice 13A release-safety scan for a bundle or the tracked workspace."""
    cli = _cli()
    return cli._run_release_safety_scan_surface(target_path=target_path, state_dir=state_dir)


def relaytic_show_release_safety(*, state_dir: str | None = None) -> dict[str, Any]:
    """Render the current Slice 13A release-safety bundle from a state directory."""
    cli = _cli()
    return cli._show_release_safety_surface(state_dir=state_dir)


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


def relaytic_review_search(
    *,
    run_dir: str,
    config_path: str | None = None,
    run_id: str | None = None,
    overwrite: bool = True,
    labels: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Execute the Slice 13 search-controller review for an existing run."""
    cli = _cli()
    return cli._run_search_phase(
        run_dir=run_dir,
        config_path=config_path,
        run_id=run_id,
        overwrite=overwrite,
        labels=_normalize_labels(labels),
        runtime_surface="mcp",
        runtime_command="relaytic_review_search",
    )


def relaytic_show_decision(*, run_dir: str) -> dict[str, Any]:
    """Render the current Slice 10A decision-lab surface for a run."""
    cli = _cli()
    return cli._show_decision_surface(run_dir=run_dir)


def relaytic_show_assist(*, run_dir: str, config_path: str | None = None) -> dict[str, Any]:
    """Render the current Slice 09E communicative assist surface for a run."""
    cli = _cli()
    return cli._show_assist_surface(run_dir=run_dir, config_path=config_path)


def relaytic_show_handoff(*, run_dir: str, audience: str = "agent") -> dict[str, Any]:
    """Render the current differentiated post-run handoff surface for a run."""
    cli = _cli()
    return cli._show_handoff_surface(run_dir=run_dir, audience=audience)


def relaytic_set_next_run_focus(
    *,
    run_dir: str,
    selection: str,
    notes: str | None = None,
    actor_type: str = "agent",
    actor_name: str | None = None,
    reset_learnings: bool = False,
) -> dict[str, Any]:
    """Persist the preferred next-run focus for a run without immediately rerunning it."""
    cli = _cli()
    return cli._set_next_run_focus_surface(
        run_dir=run_dir,
        selection_id=selection,
        notes=notes,
        source="mcp",
        actor_type=_normalize_actor_type(actor_type),
        actor_name=actor_name,
        reset_requested=reset_learnings,
    )


def relaytic_show_learnings(*, run_dir: str | None = None, state_dir: str | None = None) -> dict[str, Any]:
    """Render the durable learnings state for the current workspace and optional run snapshot."""
    cli = _cli()
    return cli._show_learnings_surface(run_dir=run_dir, state_dir=state_dir)


def relaytic_reset_learnings(*, run_dir: str | None = None, state_dir: str | None = None) -> dict[str, Any]:
    """Reset the durable learnings state for the current workspace."""
    cli = _cli()
    return cli._reset_learnings_surface(run_dir=run_dir, state_dir=state_dir)


def relaytic_show_workspace(*, run_dir: str) -> dict[str, Any]:
    """Render the current workspace continuity surface for a run."""
    cli = _cli()
    return cli._show_workspace_surface(run_dir=run_dir)


def relaytic_continue_workspace(
    *,
    run_dir: str,
    direction: str,
    notes: str | None = None,
    actor_type: str = "agent",
    actor_name: str | None = None,
    reset_learnings: bool = False,
) -> dict[str, Any]:
    """Persist the next workspace continuation direction without starting a fresh run."""
    cli = _cli()
    return cli._continue_workspace_surface(
        run_dir=run_dir,
        direction=direction,
        notes=notes,
        source="mcp",
        actor_type=_normalize_actor_type(actor_type),
        actor_name=actor_name,
        reset_requested=reset_learnings,
    )


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
            "relaytic_show_event_bus",
            "relaytic_show_permissions",
            "relaytic_show_control",
            "relaytic_show_mission_control",
            "relaytic_show_handoff",
            "relaytic_show_learnings",
            "relaytic_show_workspace",
            "relaytic_show_pulse",
            "relaytic_show_search",
            "relaytic_show_daemon",
            "relaytic_show_remote_control",
            "relaytic_show_release_safety",
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
            "relaytic_review_search",
            "relaytic_run_background_job",
            "relaytic_resume_background_job",
            "relaytic_scan_release_safety",
            "relaytic_run_agent_evals",
            "relaytic_assist_turn",
            "relaytic_set_next_run_focus",
            "relaytic_continue_workspace",
            "relaytic_reset_learnings",
            "relaytic_check_permission",
            "relaytic_decide_permission",
            "relaytic_decide_remote_approval",
            "relaytic_handoff_remote_supervision",
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
    specs = [
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
            name="relaytic_show_event_bus",
            title="Show Relaytic Event Bus",
            description="Render the current Slice 13B typed event bus, subscriber registry, and hook-dispatch projection for a Relaytic run.",
            category="inspection",
            annotations={"readOnlyHint": True, "idempotentHint": True, "destructiveHint": False, "openWorldHint": False},
            handler=relaytic_show_event_bus,
        ),
        InteropToolSpec(
            name="relaytic_show_permissions",
            title="Show Relaytic Permissions",
            description="Render the current Slice 13B permission mode, approval posture, and session capability contract for a Relaytic run.",
            category="inspection",
            annotations={"readOnlyHint": True, "idempotentHint": True, "destructiveHint": False, "openWorldHint": False},
            handler=relaytic_show_permissions,
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
            description="Render the current Slice 15 operator surface, including workspace continuity, branches, confidence posture, approvals, background work, demo readiness, and onboarding state for a Relaytic run.",
            category="inspection",
            annotations={"readOnlyHint": True, "idempotentHint": True, "destructiveHint": False, "openWorldHint": False},
            handler=relaytic_show_mission_control,
        ),
        InteropToolSpec(
            name="relaytic_show_handoff",
            title="Show Relaytic Handoff",
            description="Render the differentiated user or agent result handoff for a Relaytic run, including findings, risks, and next-run options.",
            category="inspection",
            annotations={"readOnlyHint": True, "idempotentHint": True, "destructiveHint": False, "openWorldHint": False},
            handler=relaytic_show_handoff,
        ),
        InteropToolSpec(
            name="relaytic_show_learnings",
            title="Show Relaytic Learnings",
            description="Render the durable cross-run learnings state and the current run's active learnings snapshot for a Relaytic workspace.",
            category="inspection",
            annotations={"readOnlyHint": True, "idempotentHint": True, "destructiveHint": False, "openWorldHint": False},
            handler=relaytic_show_learnings,
        ),
        InteropToolSpec(
            name="relaytic_show_workspace",
            title="Show Relaytic Workspace",
            description="Render the current Slice 12D workspace continuity, result-contract posture, and next-run plan for a Relaytic run.",
            category="inspection",
            annotations={"readOnlyHint": True, "idempotentHint": True, "destructiveHint": False, "openWorldHint": False},
            handler=relaytic_show_workspace,
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
            name="relaytic_show_search",
            title="Show Relaytic Search Controller",
            description="Render the current Slice 13 search-controller surface, including value-of-search posture, widened branches, bounded HPO depth, and execution strategy for a Relaytic run.",
            category="inspection",
            annotations={"readOnlyHint": True, "idempotentHint": True, "destructiveHint": False, "openWorldHint": False},
            handler=relaytic_show_search,
        ),
        InteropToolSpec(
            name="relaytic_show_daemon",
            title="Show Relaytic Background Daemon",
            description="Render the current Slice 13C bounded background-job surface, including approvals, checkpoints, resumable jobs, and memory-maintenance posture for a Relaytic run.",
            category="inspection",
            annotations={"readOnlyHint": True, "idempotentHint": True, "destructiveHint": False, "openWorldHint": False},
            handler=relaytic_show_daemon,
        ),
        InteropToolSpec(
            name="relaytic_show_remote_control",
            title="Show Relaytic Remote Supervision",
            description="Render the current Slice 14A remote supervision, approval queue, transport freshness, and supervision-handoff surface for a Relaytic run.",
            category="inspection",
            annotations={"readOnlyHint": True, "idempotentHint": True, "destructiveHint": False, "openWorldHint": False},
            handler=relaytic_show_remote_control,
        ),
        InteropToolSpec(
            name="relaytic_show_release_safety",
            title="Show Relaytic Release Safety",
            description="Render the current Slice 13A release-safety attestation, scanned inventory, and packaging-regression posture from a release-safety state directory.",
            category="inspection",
            annotations={"readOnlyHint": True, "idempotentHint": True, "destructiveHint": False, "openWorldHint": False},
            handler=relaytic_show_release_safety,
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
            name="relaytic_set_next_run_focus",
            title="Set Relaytic Next-Run Focus",
            description="Persist the preferred next-run focus for a Relaytic run so the next iteration can stay on the same data, add data, or start over.",
            category="workflow",
            annotations={"readOnlyHint": False, "idempotentHint": False, "destructiveHint": False, "openWorldHint": False},
            handler=relaytic_set_next_run_focus,
        ),
        InteropToolSpec(
            name="relaytic_reset_learnings",
            title="Reset Relaytic Learnings",
            description="Reset the durable Relaytic learnings state for a workspace when an operator or agent wants to start fresh.",
            category="workflow",
            annotations={"readOnlyHint": False, "idempotentHint": False, "destructiveHint": False, "openWorldHint": False},
            handler=relaytic_reset_learnings,
        ),
        InteropToolSpec(
            name="relaytic_continue_workspace",
            title="Continue Relaytic Workspace",
            description="Persist the current workspace continuation direction so the next run stays on the same data, adds data, or starts over explicitly.",
            category="workflow",
            annotations={"readOnlyHint": False, "idempotentHint": False, "destructiveHint": False, "openWorldHint": False},
            handler=relaytic_continue_workspace,
        ),
        InteropToolSpec(
            name="relaytic_check_permission",
            title="Check Relaytic Permission",
            description="Evaluate one tool or action against the current Relaytic permission mode and append the resulting decision.",
            category="workflow",
            annotations={"readOnlyHint": False, "idempotentHint": False, "destructiveHint": False, "openWorldHint": False},
            handler=relaytic_check_permission,
        ),
        InteropToolSpec(
            name="relaytic_decide_permission",
            title="Decide Relaytic Permission",
            description="Resolve one pending Relaytic approval request by approving or denying it explicitly.",
            category="workflow",
            annotations={"readOnlyHint": False, "idempotentHint": False, "destructiveHint": False, "openWorldHint": False},
            handler=relaytic_decide_permission,
        ),
        InteropToolSpec(
            name="relaytic_decide_remote_approval",
            title="Decide Relaytic Remote Approval",
            description="Approve or deny one pending request through the Slice 14A remote-supervision surface while appending to the same local authority truth.",
            category="workflow",
            annotations={"readOnlyHint": False, "idempotentHint": False, "destructiveHint": False, "openWorldHint": False},
            handler=relaytic_decide_remote_approval,
        ),
        InteropToolSpec(
            name="relaytic_handoff_remote_supervision",
            title="Handoff Relaytic Remote Supervision",
            description="Transfer the current remote-supervision role between a human and an external agent without creating a separate authority path.",
            category="workflow",
            annotations={"readOnlyHint": False, "idempotentHint": False, "destructiveHint": False, "openWorldHint": False},
            handler=relaytic_handoff_remote_supervision,
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
            name="relaytic_review_search",
            title="Review Search Controller",
            description="Execute the Slice 13 search-controller review for an existing Relaytic run, recording value-of-search, widened/pruned branches, HPO depth, and execution strategy artifacts.",
            category="workflow",
            annotations={"readOnlyHint": False, "idempotentHint": False, "destructiveHint": False, "openWorldHint": False},
            handler=relaytic_review_search,
        ),
        InteropToolSpec(
            name="relaytic_run_background_job",
            title="Run Relaytic Background Job",
            description="Start one bounded Slice 13C background job for an existing Relaytic run, requesting approval first when policy requires it.",
            category="workflow",
            annotations={"readOnlyHint": False, "idempotentHint": False, "destructiveHint": False, "openWorldHint": False},
            handler=relaytic_run_background_job,
        ),
        InteropToolSpec(
            name="relaytic_resume_background_job",
            title="Resume Relaytic Background Job",
            description="Resume one paused or stale Slice 13C background job from its explicit checkpoint for an existing Relaytic run.",
            category="workflow",
            annotations={"readOnlyHint": False, "idempotentHint": False, "destructiveHint": False, "openWorldHint": False},
            handler=relaytic_resume_background_job,
        ),
        InteropToolSpec(
            name="relaytic_scan_release_safety",
            title="Scan Relaytic Release Safety",
            description="Execute the Slice 13A release-safety scan for a built bundle or the tracked workspace, writing attestation and packaging-regression artifacts.",
            category="workflow",
            annotations={"readOnlyHint": False, "idempotentHint": False, "destructiveHint": False, "openWorldHint": False},
            handler=relaytic_scan_release_safety,
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
    return [_wrap_tool_spec(spec) for spec in specs]


def _wrap_tool_spec(spec: InteropToolSpec) -> InteropToolSpec:
    if spec.name == "relaytic_server_info":
        return spec

    def _wrapped_handler(**kwargs: Any) -> dict[str, Any]:
        run_dir = _resolve_tool_event_run_dir(tool_name=spec.name, kwargs=kwargs)
        if run_dir is not None:
            _emit_tool_event(
                tool_name=spec.name,
                run_dir=run_dir,
                kwargs=kwargs,
                event_type="tool_pre_use",
                status="running",
                summary=f"Relaytic host tool `{spec.name}` started.",
            )
        try:
            result = spec.handler(**kwargs)
        except Exception:
            if run_dir is not None:
                _emit_tool_event(
                    tool_name=spec.name,
                    run_dir=run_dir,
                    kwargs=kwargs,
                    event_type="tool_post_use",
                    status="error",
                    summary=f"Relaytic host tool `{spec.name}` failed.",
                )
            raise
        if run_dir is not None:
            _emit_tool_event(
                tool_name=spec.name,
                run_dir=run_dir,
                kwargs=kwargs,
                event_type="tool_post_use",
                status="ok",
                summary=f"Relaytic host tool `{spec.name}` completed.",
            )
        return result

    _wrapped_handler.__signature__ = inspect.signature(spec.handler)
    _wrapped_handler.__name__ = getattr(spec.handler, "__name__", spec.name)
    _wrapped_handler.__doc__ = getattr(spec.handler, "__doc__", None)

    return InteropToolSpec(
        name=spec.name,
        title=spec.title,
        description=spec.description,
        category=spec.category,
        annotations=spec.annotations,
        handler=_wrapped_handler,
        structured_output=spec.structured_output,
    )


def _resolve_tool_event_run_dir(*, tool_name: str, kwargs: dict[str, Any]) -> Path | None:
    run_dir = kwargs.get("run_dir")
    if run_dir:
        return Path(str(run_dir))
    data_path = kwargs.get("data_path")
    if tool_name == "relaytic_run" and data_path:
        return _resolve_run_dir(run_dir=None, data_path=str(data_path))
    return None


def _emit_tool_event(
    *,
    tool_name: str,
    run_dir: Path,
    kwargs: dict[str, Any],
    event_type: str,
    status: str,
    summary: str,
) -> None:
    try:
        cli = _cli()
        config_path = kwargs.get("config_path") or kwargs.get("config")
        policy = cli._load_mission_control_policy(run_dir=str(run_dir), config_path=config_path)
        runtime_payload = cli._show_runtime_surface(run_dir=run_dir, limit=1)
        stage = str(dict(runtime_payload.get("surface_payload", {}).get("runtime", {})).get("current_stage", "")).strip() or "runtime"
        cli.record_runtime_event(
            run_dir=run_dir,
            policy=policy,
            event_type=event_type,
            stage=stage,
            source_surface="mcp",
            source_command=tool_name,
            status=status,
            summary=summary,
            metadata={"tool_name": tool_name},
        )
    except Exception:
        return


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
