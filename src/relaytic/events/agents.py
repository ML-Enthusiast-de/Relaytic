"""Slice 13B event-bus materialization and rendering."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from relaytic.runtime import read_event_stream, read_runtime_bundle

from .models import (
    EVENT_SCHEMA_SCHEMA_VERSION,
    EVENT_SUBSCRIPTION_REGISTRY_SCHEMA_VERSION,
    HOOK_DISPATCH_REPORT_SCHEMA_VERSION,
    HOOK_REGISTRY_SCHEMA_VERSION,
    EventBusBundle,
    EventBusControls,
    EventBusTrace,
    EventSchemaArtifact,
    EventSubscriptionRegistryArtifact,
    HookDispatchReportArtifact,
    HookRegistryArtifact,
)
from .storage import write_event_bus_bundle


@dataclass(frozen=True)
class EventBusRunResult:
    bundle: EventBusBundle
    review_markdown: str


_EVENT_TYPE_SPECS: tuple[dict[str, Any], ...] = (
    {"event_type": "session_started", "category": "session", "required_fields": ["event_id", "occurred_at", "source_surface", "source_command", "status"], "replayable": True, "description": "A human or agent session attached to Relaytic."},
    {"event_type": "session_ended", "category": "session", "required_fields": ["event_id", "occurred_at", "source_surface", "source_command", "status"], "replayable": True, "description": "A human or agent session ended cleanly or due to interruption."},
    {"event_type": "prompt_submitted", "category": "interaction", "required_fields": ["event_id", "occurred_at", "source_surface", "source_command", "status"], "replayable": True, "description": "One human or agent prompt was submitted to Relaytic."},
    {"event_type": "tool_pre_use", "category": "tooling", "required_fields": ["event_id", "occurred_at", "source_surface", "source_command", "status"], "replayable": True, "description": "An MCP or host tool is about to run against Relaytic."},
    {"event_type": "tool_post_use", "category": "tooling", "required_fields": ["event_id", "occurred_at", "source_surface", "source_command", "status"], "replayable": True, "description": "An MCP or host tool finished against Relaytic."},
    {"event_type": "stage_started", "category": "runtime", "required_fields": ["event_id", "occurred_at", "stage", "source_surface", "status"], "replayable": True, "description": "A canonical Relaytic stage started through the shared runtime."},
    {"event_type": "stage_completed", "category": "runtime", "required_fields": ["event_id", "occurred_at", "stage", "source_surface", "status"], "replayable": True, "description": "A canonical Relaytic stage completed through the shared runtime."},
    {"event_type": "stage_failed", "category": "runtime", "required_fields": ["event_id", "occurred_at", "stage", "source_surface", "status"], "replayable": True, "description": "A canonical Relaytic stage failed through the shared runtime."},
    {"event_type": "background_job_started", "category": "background", "required_fields": ["event_id", "occurred_at", "source_surface", "status"], "replayable": True, "description": "A bounded background job started under the canonical event contract."},
    {"event_type": "background_job_completed", "category": "background", "required_fields": ["event_id", "occurred_at", "source_surface", "status"], "replayable": True, "description": "A bounded background job completed under the canonical event contract."},
    {"event_type": "workspace_resumed", "category": "workspace", "required_fields": ["event_id", "occurred_at", "source_surface", "status"], "replayable": True, "description": "Relaytic resumed or continued work from an existing workspace."},
    {"event_type": "compaction_started", "category": "memory", "required_fields": ["event_id", "occurred_at", "source_surface", "status"], "replayable": True, "description": "Relaytic started a bounded compaction or maintenance step."},
    {"event_type": "compaction_completed", "category": "memory", "required_fields": ["event_id", "occurred_at", "source_surface", "status"], "replayable": True, "description": "Relaytic completed a bounded compaction or maintenance step."},
    {"event_type": "approval_requested", "category": "authority", "required_fields": ["event_id", "occurred_at", "source_surface", "status"], "replayable": True, "description": "Relaytic requested approval for a workflow action."},
    {"event_type": "approval_approved", "category": "authority", "required_fields": ["event_id", "occurred_at", "source_surface", "status"], "replayable": True, "description": "An earlier approval request was approved."},
    {"event_type": "approval_denied", "category": "authority", "required_fields": ["event_id", "occurred_at", "source_surface", "status"], "replayable": True, "description": "An action was denied immediately or after review."},
    {"event_type": "permission_allowed", "category": "authority", "required_fields": ["event_id", "occurred_at", "source_surface", "status"], "replayable": True, "description": "A permission-gated action was explicitly allowed under the current mode."},
    {"event_type": "runtime_initialized", "category": "runtime", "required_fields": ["event_id", "occurred_at", "source_surface", "status"], "replayable": True, "description": "The shared runtime initialized its canonical artifacts."},
    {"event_type": "runtime_backfilled", "category": "runtime", "required_fields": ["event_id", "occurred_at", "source_surface", "status"], "replayable": True, "description": "The shared runtime backfilled an event stream for an older run."},
    {"event_type": "checkpoint_written", "category": "runtime", "required_fields": ["event_id", "occurred_at", "source_surface", "status"], "replayable": True, "description": "The shared runtime checkpointed the current state."},
)

_SUBSCRIPTION_SPECS: tuple[dict[str, Any], ...] = (
    {"subscription_id": "sub_stage_timeline", "subscriber_name": "stage_timeline_projection", "event_types": ["stage_started", "stage_completed", "stage_failed", "checkpoint_written"], "delivery_mode": "projection_only", "writes": [], "purpose": "Build a truthful recent stage timeline without mutating run outcome."},
    {"subscription_id": "sub_authority_posture", "subscriber_name": "authority_posture_projection", "event_types": ["approval_requested", "approval_approved", "approval_denied", "permission_allowed"], "delivery_mode": "projection_only", "writes": [], "purpose": "Keep approval posture visible from the same canonical event stream."},
    {"subscription_id": "sub_tool_activity", "subscriber_name": "tool_activity_projection", "event_types": ["tool_pre_use", "tool_post_use", "prompt_submitted", "session_started", "session_ended"], "delivery_mode": "projection_only", "writes": [], "purpose": "Summarize host activity without becoming a second source of truth."},
    {"subscription_id": "sub_workspace_continuity", "subscriber_name": "workspace_continuity_projection", "event_types": ["workspace_resumed", "compaction_started", "compaction_completed"], "delivery_mode": "projection_only", "writes": [], "purpose": "Prepare later daemon and resume work to consume the same canonical events."},
)


def build_event_bus_controls_from_policy(policy: dict[str, Any]) -> EventBusControls:
    cfg = dict(policy.get("events", {}))
    return EventBusControls(
        enabled=bool(cfg.get("enabled", True)),
        max_recent_dispatches=max(10, int(cfg.get("max_recent_dispatches", 60) or 60)),
        project_dispatches_without_live_subscribers=bool(cfg.get("project_dispatches_without_live_subscribers", True)),
        read_only_subscribers_only=bool(cfg.get("read_only_subscribers_only", True)),
    )


def run_event_bus_review(
    *,
    run_dir: str | Path,
    policy: dict[str, Any] | None = None,
) -> EventBusRunResult:
    root = Path(run_dir)
    runtime_bundle = read_runtime_bundle(root)
    runtime_events = read_event_stream(root)
    controls = build_event_bus_controls_from_policy(policy or {})
    trace = EventBusTrace(
        agent="event_bus_controller",
        event_source="lab_event_stream.jsonl",
        dispatch_mode="projection_only",
        advisory_notes=[
            "The event bus is a projection over the canonical runtime stream rather than a second mutable activity log.",
            "Subscribers stay read-only so later daemon and remote work inherit one truthful event history.",
        ],
    )
    subscriptions = [dict(item) for item in _SUBSCRIPTION_SPECS]
    bundle = EventBusBundle(
        event_schema=EventSchemaArtifact(
            schema_version=EVENT_SCHEMA_SCHEMA_VERSION,
            generated_at=_utc_now(),
            controls=controls,
            status="ok",
            event_type_count=len(_EVENT_TYPE_SPECS),
            field_names=["schema_version", "event_id", "occurred_at", "event_type", "stage", "source_surface", "source_command", "status", "summary", "metadata"],
            event_types=[dict(item) for item in _EVENT_TYPE_SPECS],
            summary=f"Relaytic exposes {len(_EVENT_TYPE_SPECS)} canonical event types through one typed local event bus.",
            trace=trace,
        ),
        event_subscription_registry=EventSubscriptionRegistryArtifact(
            schema_version=EVENT_SUBSCRIPTION_REGISTRY_SCHEMA_VERSION,
            generated_at=_utc_now(),
            controls=controls,
            status="ok",
            subscription_count=len(subscriptions),
            subscriptions=subscriptions,
            summary=f"Relaytic currently exposes {len(subscriptions)} typed projection subscriber(s) over the runtime event stream.",
            trace=trace,
        ),
        hook_registry=HookRegistryArtifact(
            schema_version=HOOK_REGISTRY_SCHEMA_VERSION,
            generated_at=_utc_now(),
            controls=controls,
            status="ok",
            hook_count=0,
            hooks=[],
            summary="",
            trace=trace,
        ),
        hook_dispatch_report=HookDispatchReportArtifact(
            schema_version=HOOK_DISPATCH_REPORT_SCHEMA_VERSION,
            generated_at=_utc_now(),
            controls=controls,
            status="ok",
            observed_event_count=len(runtime_events),
            subscriber_count=len(subscriptions),
            dispatch_count=0,
            recent_dispatches=[],
            source_of_truth_preserved=True,
            summary="",
            trace=trace,
        ),
    )
    hooks = _build_hook_registry(runtime_bundle=runtime_bundle, subscriptions=subscriptions)
    dispatches = _project_dispatches(events=runtime_events, subscriptions=subscriptions, limit=controls.max_recent_dispatches)
    bundle = EventBusBundle(
        event_schema=bundle.event_schema,
        event_subscription_registry=bundle.event_subscription_registry,
        hook_registry=HookRegistryArtifact(
            schema_version=HOOK_REGISTRY_SCHEMA_VERSION,
            generated_at=_utc_now(),
            controls=controls,
            status="ok",
            hook_count=len(hooks),
            hooks=hooks,
            summary=f"Relaytic currently tracks {len(hooks)} runtime hook or subscriber registry entries.",
            trace=trace,
        ),
        hook_dispatch_report=HookDispatchReportArtifact(
            schema_version=HOOK_DISPATCH_REPORT_SCHEMA_VERSION,
            generated_at=_utc_now(),
            controls=controls,
            status="ok",
            observed_event_count=len(runtime_events),
            subscriber_count=len(subscriptions),
            dispatch_count=len(dispatches),
            recent_dispatches=dispatches,
            source_of_truth_preserved=True,
            summary=f"Relaytic projected {len(dispatches)} read-only dispatch observations from {len(runtime_events)} canonical runtime event(s).",
            trace=trace,
        ),
    )
    write_event_bus_bundle(root, bundle=bundle)
    return EventBusRunResult(bundle=bundle, review_markdown=render_event_bus_markdown(bundle))


def render_event_bus_markdown(bundle: EventBusBundle | dict[str, Any]) -> str:
    payload = bundle.to_dict() if isinstance(bundle, EventBusBundle) else dict(bundle)
    schema = dict(payload.get("event_schema", {}))
    subscriptions = dict(payload.get("event_subscription_registry", {}))
    hooks = dict(payload.get("hook_registry", {}))
    dispatch = dict(payload.get("hook_dispatch_report", {}))
    lines = [
        "# Relaytic Event Bus",
        "",
        f"- Event types: `{schema.get('event_type_count', 0)}`",
        f"- Subscribers: `{subscriptions.get('subscription_count', 0)}`",
        f"- Hook registry entries: `{hooks.get('hook_count', 0)}`",
        f"- Projected dispatches: `{dispatch.get('dispatch_count', 0)}`",
        f"- Source of truth preserved: `{dispatch.get('source_of_truth_preserved')}`",
    ]
    for item in list(dispatch.get("recent_dispatches", []))[:8]:
        lines.append(f"- `{item.get('event_type')}` -> `{item.get('subscriber_name')}` (projection `{item.get('source_of_truth_preserved')}`)")
    return "\n".join(lines).rstrip() + "\n"


def _build_hook_registry(*, runtime_bundle: dict[str, Any], subscriptions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    hook_log = dict(runtime_bundle.get("hook_execution_log", {}))
    executions = list(hook_log.get("executions", [])) if isinstance(hook_log.get("executions"), list) else []
    registry: list[dict[str, Any]] = []
    grouped: dict[str, list[dict[str, Any]]] = {}
    for item in executions:
        hook_name = str(item.get("hook_name", "")).strip()
        if not hook_name:
            continue
        grouped.setdefault(hook_name, []).append(item)
    for hook_name, items in grouped.items():
        trigger_types = sorted({str(item.get("trigger_event_type", "")).strip() for item in items if str(item.get("trigger_event_type", "")).strip()})
        registry.append(
            {
                "hook_name": hook_name,
                "hook_kind": "runtime_hook",
                "delivery_mode": "read_only" if str(items[-1].get("hook_type", "")).strip() == "read_only" else "bounded_write",
                "trigger_event_types": trigger_types,
                "write_targets": sorted({write for item in items for write in list(item.get("writes", [])) if str(write).strip()}),
                "last_status": str(items[-1].get("status", "")).strip() or None,
                "registry_source": "hook_execution_log.json",
            }
        )
    for item in subscriptions:
        registry.append(
            {
                "hook_name": str(item.get("subscriber_name")),
                "hook_kind": "event_subscriber",
                "delivery_mode": str(item.get("delivery_mode", "projection_only")),
                "trigger_event_types": list(item.get("event_types", [])),
                "write_targets": [],
                "last_status": "projected",
                "registry_source": "event_subscription_registry.json",
            }
        )
    return sorted(registry, key=lambda item: (str(item.get("hook_kind", "")), str(item.get("hook_name", ""))))


def _project_dispatches(*, events: list[dict[str, Any]], subscriptions: list[dict[str, Any]], limit: int) -> list[dict[str, Any]]:
    projected: list[dict[str, Any]] = []
    for event in events:
        event_type = str(event.get("event_type", "")).strip()
        if not event_type:
            continue
        for subscription in subscriptions:
            if event_type not in list(subscription.get("event_types", [])):
                continue
            projected.append(
                {
                    "dispatch_id": _identifier("dispatch"),
                    "event_id": str(event.get("event_id", "")).strip() or None,
                    "event_type": event_type,
                    "subscriber_name": str(subscription.get("subscriber_name", "")).strip() or None,
                    "occurred_at": str(event.get("occurred_at", "")).strip() or _utc_now(),
                    "source_surface": str(event.get("source_surface", "")).strip() or None,
                    "dispatch_mode": str(subscription.get("delivery_mode", "projection_only")),
                    "source_of_truth_preserved": True,
                    "writes": [],
                }
            )
    return projected[-limit:] if limit >= 0 else projected


def _identifier(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex[:12]}"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()
