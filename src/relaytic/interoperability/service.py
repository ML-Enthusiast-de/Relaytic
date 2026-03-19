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


def relaytic_get_status(*, run_dir: str) -> dict[str, Any]:
    """Render the completion-governor status for a Relaytic run."""
    cli = _cli()
    return cli._show_completion_status(run_dir=run_dir)


def relaytic_predict(
    *,
    run_dir: str,
    data_path: str,
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
    )


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
            "relaytic_get_status",
            "relaytic_show_lifecycle",
            "relaytic_doctor",
            "relaytic_integrations_show",
        ],
        "workflow_tools": [
            "relaytic_run",
            "relaytic_intake_interpret",
            "relaytic_investigate_dataset",
            "relaytic_generate_plan",
            "relaytic_run_evidence_review",
            "relaytic_review_completion",
            "relaytic_review_lifecycle",
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
            name="relaytic_get_status",
            title="Get Relaytic Status",
            description="Read the Slice 07 completion-governor status for a Relaytic run.",
            category="inspection",
            annotations={"readOnlyHint": True, "idempotentHint": True, "destructiveHint": False, "openWorldHint": False},
            handler=relaytic_get_status,
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
