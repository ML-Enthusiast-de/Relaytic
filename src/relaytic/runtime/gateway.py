"""Local lab gateway, event stream, hooks, and capability enforcement for Slice 09B."""

from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any
from uuid import uuid4

from .models import (
    CAPABILITY_PROFILES_SCHEMA_VERSION,
    CONTEXT_INFLUENCE_REPORT_SCHEMA_VERSION,
    DATA_ACCESS_AUDIT_SCHEMA_VERSION,
    HOOK_EXECUTION_LOG_SCHEMA_VERSION,
    LAB_EVENT_SCHEMA_VERSION,
    RUN_CHECKPOINT_MANIFEST_SCHEMA_VERSION,
    CapabilityProfilesArtifact,
    ContextInfluenceReportArtifact,
    DataAccessAuditArtifact,
    HookExecutionLogArtifact,
    RunCheckpointManifestArtifact,
    RuntimeControls,
    build_default_capability_profiles,
    build_runtime_controls_from_policy,
)
from .storage import EVENT_STREAM_FILENAME, RUNTIME_FILENAMES, append_event, read_event_stream, read_runtime_bundle, write_runtime_artifact


READ_ONLY_HOOK_NAME = "stage_transition_observer"
WRITE_HOOK_NAME = "context_influence_writeback"

_STAGE_PLAN: dict[str, dict[str, Any]] = {
    "intake": {
        "specialists": ["intake_translator"],
        "input_artifacts": ["lab_mandate.json", "work_preferences.json", "run_brief.json", "data_origin.json", "domain_brief.json", "task_brief.json"],
    },
    "investigation": {
        "specialists": ["scout", "scientist", "focus_council"],
        "input_artifacts": ["task_brief.json", "domain_brief.json", "run_brief.json", "data_origin.json"],
    },
    "memory": {
        "specialists": ["memory_retrieval_agent"],
        "input_artifacts": ["run_summary.json", "plan.json", "challenger_report.json", "completion_decision.json", "promotion_decision.json"],
    },
    "planning": {
        "specialists": ["strategist", "builder"],
        "input_artifacts": ["dataset_profile.json", "domain_memo.json", "focus_profile.json", "optimization_profile.json", "feature_strategy_profile.json", "route_prior_context.json"],
    },
    "evidence": {
        "specialists": ["challenger"],
        "input_artifacts": ["plan.json", "memory_retrieval.json", "route_prior_context.json", "challenger_prior_suggestions.json", "model_params.json"],
    },
    "intelligence": {
        "specialists": ["semantic_helper"],
        "input_artifacts": [
            "run_brief.json",
            "task_brief.json",
            "plan.json",
            "audit_report.json",
            "completion_decision.json",
        ],
    },
    "research": {
        "specialists": ["research_librarian"],
        "input_artifacts": [
            "run_brief.json",
            "task_brief.json",
            "dataset_profile.json",
            "plan.json",
            "semantic_debate_report.json",
        ],
    },
    "benchmark": {
        "specialists": ["benchmark_referee"],
        "input_artifacts": [
            "plan.json",
            "model_params.json",
            "task_brief.json",
            "run_brief.json",
        ],
    },
    "completion": {
        "specialists": ["completion_governor"],
        "input_artifacts": ["audit_report.json", "belief_update.json", "route_prior_context.json", "memory_retrieval.json", "benchmark_parity_report.json", "run_summary.json"],
    },
    "lifecycle": {
        "specialists": ["lifecycle_governor"],
        "input_artifacts": ["completion_decision.json", "memory_retrieval.json", "run_summary.json", "champion_vs_candidate.json"],
    },
    "autonomy": {
        "specialists": ["autonomy_controller"],
        "input_artifacts": [
            "plan.json",
            "completion_decision.json",
            "promotion_decision.json",
            "semantic_debate_report.json",
            "semantic_uncertainty_report.json",
        ],
    },
}


def ensure_runtime_initialized(
    *,
    run_dir: str | Path,
    policy: dict[str, Any],
    source_surface: str,
    source_command: str,
    backfill_if_missing: bool = False,
) -> dict[str, Any]:
    """Ensure runtime artifacts exist and optionally backfill a synthetic event."""
    root = Path(run_dir)
    root.mkdir(parents=True, exist_ok=True)
    controls = build_runtime_controls_from_policy(policy)
    profiles = build_default_capability_profiles()

    capability_payload = _read_json_artifact(root, "capability_profiles")
    if not capability_payload:
        write_runtime_artifact(
            root,
            key="capability_profiles",
            payload=CapabilityProfilesArtifact(
                schema_version=CAPABILITY_PROFILES_SCHEMA_VERSION,
                generated_at=_utc_now(),
                controls=controls,
                profiles=profiles,
                summary=f"Relaytic currently exposes {len(profiles)} capability-scoped specialists in the local lab runtime.",
            ).to_dict(),
        )
    if not _read_json_artifact(root, "hook_execution_log"):
        _write_hook_execution_log(root, controls, executions=[])
    if not _read_json_artifact(root, "run_checkpoint_manifest"):
        _write_checkpoint_manifest(root, controls, checkpoints=[], latest_stage=None)
    if not _read_json_artifact(root, "data_access_audit"):
        _write_data_access_audit(root, controls, decisions=[])
    if not _read_json_artifact(root, "context_influence_report"):
        _write_context_influence_report(root, controls, stage_reports=[])
    existing_events = read_event_stream(root)
    if not existing_events:
        event_type = "runtime_backfilled" if backfill_if_missing else "runtime_initialized"
        stage = _infer_existing_stage(root) if backfill_if_missing else "initialized"
        init_event = _build_event(
            event_type=event_type,
            stage=stage,
            source_surface=source_surface,
            source_command=source_command,
            status="ok",
            summary=(
                f"Relaytic runtime backfilled current artifact state at `{stage}`."
                if backfill_if_missing
                else "Relaytic runtime initialized for local evented coordination."
            ),
            metadata={"event_stream_path": str(root / EVENT_STREAM_FILENAME)},
        )
        append_event(root, event=init_event)
        _record_hook(
            root,
            controls,
            execution={
                "execution_id": _identifier("hook"),
                "occurred_at": _utc_now(),
                "hook_name": READ_ONLY_HOOK_NAME,
                "hook_type": "read_only",
                "status": "observed",
                "trigger_event_type": init_event["event_type"],
                "stage": stage,
                "source_surface": source_surface,
                "writes": [],
                "notes": ["Observed runtime bootstrap transition."],
            },
        )
        checkpoint = _write_checkpoint(
            root,
            controls,
            stage=stage,
            reason="runtime_bootstrap",
            source_surface=source_surface,
            event_id=init_event["event_id"],
            artifact_paths=_existing_artifact_paths(root),
        )
        append_event(
            root,
            event=_build_event(
                event_type="checkpoint_written",
                stage=stage,
                source_surface=source_surface,
                source_command=source_command,
                status="ok",
                summary=f"Runtime checkpoint `{checkpoint['checkpoint_id']}` captured current local state.",
                metadata={"checkpoint_id": checkpoint["checkpoint_id"]},
            ),
        )
    return build_runtime_surface(run_dir=root)


def record_stage_start(
    *,
    run_dir: str | Path,
    policy: dict[str, Any],
    stage: str,
    source_surface: str,
    source_command: str,
    data_path: str | None,
    input_artifacts: list[str] | None = None,
) -> dict[str, Any]:
    """Record the start of one runtime stage."""
    root = Path(run_dir)
    ensure_runtime_initialized(
        run_dir=root,
        policy=policy,
        source_surface=source_surface,
        source_command=source_command,
    )
    controls = build_runtime_controls_from_policy(policy)
    stage_plan = _STAGE_PLAN.get(stage, {})
    active_specialists = _stage_specialists(stage)
    event = _build_event(
        event_type="stage_started",
        stage=stage,
        source_surface=source_surface,
        source_command=source_command,
        status="running",
        summary=f"Relaytic started the `{stage}` stage through `{source_surface}`.",
        metadata={
            "specialists": active_specialists,
            "input_artifacts": list(input_artifacts or stage_plan.get("input_artifacts", [])),
        },
    )
    append_event(root, event=event)
    decisions = _access_decisions_for_stage(
        stage=stage,
        data_path=data_path,
        source_surface=source_surface,
        source_command=source_command,
    )
    _extend_data_access_audit(root, controls, decisions=decisions)
    _append_context_stage_report(
        root,
        controls,
        stage_report={
            "record_id": _identifier("ctx"),
            "recorded_at": _utc_now(),
            "stage": stage,
            "start_event_id": event["event_id"],
            "status": "running",
            "source_surface": source_surface,
            "source_command": source_command,
            "active_specialists": active_specialists,
            "input_artifacts": list(input_artifacts or stage_plan.get("input_artifacts", [])),
            "output_artifacts": [],
            "denied_accesses": [
                {
                    "specialist": item["specialist"],
                    "access_kind": item["access_kind"],
                    "reason": item["reason"],
                }
                for item in decisions
                if item["decision"] == "denied"
            ],
            "semantic_context_mode": "rowless_default" if controls.semantic_rowless_default else "policy_defined",
            "notes": ["Capability profiles were resolved before stage execution."],
        },
    )
    _record_hook(
        root,
        controls,
        execution={
            "execution_id": _identifier("hook"),
            "occurred_at": _utc_now(),
            "hook_name": READ_ONLY_HOOK_NAME,
            "hook_type": "read_only",
            "status": "observed",
            "trigger_event_type": "stage_started",
            "stage": stage,
            "source_surface": source_surface,
            "writes": [],
            "notes": ["Observed stage start without mutating the run outcome."],
        },
    )
    return {
        "stage": stage,
        "start_event_id": event["event_id"],
        "source_surface": source_surface,
        "source_command": source_command,
    }


def record_stage_completion(
    *,
    run_dir: str | Path,
    policy: dict[str, Any],
    stage_token: dict[str, Any],
    output_artifacts: list[str],
    summary: str,
) -> dict[str, Any]:
    """Record the completion of one runtime stage."""
    root = Path(run_dir)
    controls = build_runtime_controls_from_policy(policy)
    stage = str(stage_token.get("stage", "")).strip() or "unknown"
    source_surface = str(stage_token.get("source_surface", "cli")).strip() or "cli"
    source_command = str(stage_token.get("source_command", stage)).strip() or stage
    completed_event = _build_event(
        event_type="stage_completed",
        stage=stage,
        source_surface=source_surface,
        source_command=source_command,
        status="ok",
        summary=summary,
        metadata={
            "output_artifacts": list(output_artifacts),
            "start_event_id": stage_token.get("start_event_id"),
        },
    )
    append_event(root, event=completed_event)
    _update_context_stage_report(
        root,
        controls,
        start_event_id=str(stage_token.get("start_event_id", "")).strip(),
        updates={
            "completed_at": _utc_now(),
            "status": "ok",
            "completion_event_id": completed_event["event_id"],
            "output_artifacts": list(output_artifacts),
            "notes": ["Stage completed through the shared local runtime path."],
        },
    )
    _record_hook(
        root,
        controls,
        execution={
            "execution_id": _identifier("hook"),
            "occurred_at": _utc_now(),
            "hook_name": READ_ONLY_HOOK_NAME,
            "hook_type": "read_only",
            "status": "observed",
            "trigger_event_type": "stage_completed",
            "stage": stage,
            "source_surface": source_surface,
            "writes": [],
            "notes": ["Observed stage completion without mutating the run outcome."],
        },
    )
    checkpoint = _write_checkpoint(
        root,
        controls,
        stage=stage,
        reason="stage_completed",
        source_surface=source_surface,
        event_id=completed_event["event_id"],
        artifact_paths=list(output_artifacts),
    )
    append_event(
        root,
        event=_build_event(
            event_type="checkpoint_written",
            stage=stage,
            source_surface=source_surface,
            source_command=source_command,
            status="ok",
            summary=f"Runtime checkpoint `{checkpoint['checkpoint_id']}` captured stage `{stage}`.",
            metadata={"checkpoint_id": checkpoint["checkpoint_id"]},
        ),
    )
    if controls.write_hooks_enabled:
        _update_context_stage_report(
            root,
            controls,
            start_event_id=str(stage_token.get("start_event_id", "")).strip(),
            updates={"hook_effects": [f"{WRITE_HOOK_NAME}:context_note_written"]},
        )
        _record_hook(
            root,
            controls,
            execution={
                "execution_id": _identifier("hook"),
                "occurred_at": _utc_now(),
                "hook_name": WRITE_HOOK_NAME,
                "hook_type": "write",
                "status": "executed",
                "trigger_event_type": "stage_completed",
                "stage": stage,
                "source_surface": source_surface,
                "writes": ["context_influence_report.json"],
                "notes": ["Policy allowed a bounded write hook to enrich the context-influence report."],
            },
        )
    else:
        _record_hook(
            root,
            controls,
            execution={
                "execution_id": _identifier("hook"),
                "occurred_at": _utc_now(),
                "hook_name": WRITE_HOOK_NAME,
                "hook_type": "write",
                "status": "blocked_by_policy",
                "trigger_event_type": "stage_completed",
                "stage": stage,
                "source_surface": source_surface,
                "writes": [],
                "notes": ["Write-capable runtime hooks are disabled by policy."],
            },
        )
    return checkpoint


def record_stage_failure(
    *,
    run_dir: str | Path,
    policy: dict[str, Any],
    stage_token: dict[str, Any],
    error: Exception,
) -> None:
    """Record a failed runtime stage."""
    root = Path(run_dir)
    controls = build_runtime_controls_from_policy(policy)
    stage = str(stage_token.get("stage", "")).strip() or "unknown"
    source_surface = str(stage_token.get("source_surface", "cli")).strip() or "cli"
    source_command = str(stage_token.get("source_command", stage)).strip() or stage
    failed_event = _build_event(
        event_type="stage_failed",
        stage=stage,
        source_surface=source_surface,
        source_command=source_command,
        status="error",
        summary=f"Relaytic recorded a `{stage}` failure through the local runtime.",
        metadata={
            "start_event_id": stage_token.get("start_event_id"),
            "error": str(error),
        },
    )
    append_event(root, event=failed_event)
    _update_context_stage_report(
        root,
        controls,
        start_event_id=str(stage_token.get("start_event_id", "")).strip(),
        updates={
            "completed_at": _utc_now(),
            "status": "error",
            "completion_event_id": failed_event["event_id"],
            "notes": [f"Runtime captured failure: {error}"],
        },
    )
    _record_hook(
        root,
        controls,
        execution={
            "execution_id": _identifier("hook"),
            "occurred_at": _utc_now(),
            "hook_name": READ_ONLY_HOOK_NAME,
            "hook_type": "read_only",
            "status": "observed",
            "trigger_event_type": "stage_failed",
            "stage": stage,
            "source_surface": source_surface,
            "writes": [],
            "notes": ["Observed failed stage transition."],
        },
    )


def build_runtime_surface(*, run_dir: str | Path, event_limit: int | None = None) -> dict[str, Any]:
    """Build the current runtime surface for humans and agents."""
    root = Path(run_dir)
    bundle = read_runtime_bundle(root)
    recent_events = read_event_stream(root, limit=event_limit or 20)
    all_events = read_event_stream(root)
    hook_log = dict(bundle.get("hook_execution_log", {}))
    checkpoint_manifest = dict(bundle.get("run_checkpoint_manifest", {}))
    data_access_audit = dict(bundle.get("data_access_audit", {}))
    capability_profiles = dict(bundle.get("capability_profiles", {}))
    executions = list(hook_log.get("executions", []))
    write_hook_entries = [item for item in executions if str(item.get("hook_type", "")) == "write"]
    last_event = recent_events[-1] if recent_events else {}
    current_stage = _resolve_runtime_stage_label(
        root,
        latest_stage=str(checkpoint_manifest.get("latest_stage", "")).strip(),
        last_event_stage=str(last_event.get("stage", "")).strip(),
    )
    runtime = {
        "current_stage": current_stage or None,
        "event_count": len(all_events),
        "recent_event_count": len(recent_events),
        "last_event_type": str(last_event.get("event_type", "")).strip() or None,
        "last_surface": str(last_event.get("source_surface", "")).strip() or None,
        "checkpoint_count": len(checkpoint_manifest.get("checkpoints", [])) if isinstance(checkpoint_manifest.get("checkpoints"), list) else 0,
        "denied_access_count": int(data_access_audit.get("denied_count", 0) or 0),
        "active_specialist_count": len(capability_profiles.get("profiles", [])) if isinstance(capability_profiles.get("profiles"), list) else 0,
        "read_only_hook_count": sum(1 for item in executions if str(item.get("hook_type", "")) == "read_only"),
        "write_hook_executed_count": sum(1 for item in write_hook_entries if str(item.get("status", "")) == "executed"),
        "write_hook_blocked_count": sum(1 for item in write_hook_entries if str(item.get("status", "")) == "blocked_by_policy"),
        "semantic_rowless_default": bool(dict(capability_profiles.get("controls", {})).get("semantic_rowless_default", True)),
    }
    return {
        "status": "ok",
        "run_dir": str(root),
        "event_stream_path": str(root / EVENT_STREAM_FILENAME),
        "runtime": runtime,
        "bundle": {key: value for key, value in bundle.items() if key != "lab_event_stream"},
        "recent_events": recent_events,
    }


def build_runtime_events_surface(*, run_dir: str | Path, limit: int = 20) -> dict[str, Any]:
    """Return recent runtime events as a structured surface."""
    root = Path(run_dir)
    all_events = read_event_stream(root)
    recent_events = read_event_stream(root, limit=limit)
    return {
        "status": "ok",
        "run_dir": str(root),
        "event_stream_path": str(root / EVENT_STREAM_FILENAME),
        "event_count": len(all_events),
        "recent_events": recent_events,
    }


def render_runtime_markdown(payload: dict[str, Any]) -> str:
    """Render a compact human-facing runtime report."""
    runtime = dict(payload.get("runtime", {}))
    recent_events = list(payload.get("recent_events", []))
    lines = [
        "# Relaytic Runtime",
        "",
        f"- Current stage: `{runtime.get('current_stage') or 'unknown'}`",
        f"- Events: `{runtime.get('event_count', 0)}` total, `{runtime.get('recent_event_count', 0)}` shown",
        f"- Checkpoints: `{runtime.get('checkpoint_count', 0)}`",
        f"- Denied accesses: `{runtime.get('denied_access_count', 0)}`",
        f"- Specialists: `{runtime.get('active_specialist_count', 0)}` capability profiles",
        f"- Write hooks: `{runtime.get('write_hook_executed_count', 0)}` executed, `{runtime.get('write_hook_blocked_count', 0)}` blocked",
    ]
    if recent_events:
        lines.extend(["", "## Recent Events"])
        for item in recent_events[-8:]:
            lines.append(
                f"- `{item.get('event_type')}` at stage `{item.get('stage')}` via `{item.get('source_surface')}`: {item.get('summary')}"
            )
    return "\n".join(lines) + "\n"


def render_runtime_events_markdown(payload: dict[str, Any]) -> str:
    """Render recent runtime events for humans."""
    lines = [
        "# Relaytic Runtime Events",
        "",
        f"- Run directory: `{payload.get('run_dir')}`",
        f"- Event count: `{payload.get('event_count', 0)}`",
    ]
    recent_events = list(payload.get("recent_events", []))
    if recent_events:
        lines.extend(["", "## Event Stream"])
        for item in recent_events:
            lines.append(
                f"- `{item.get('event_type')}` stage=`{item.get('stage')}` surface=`{item.get('source_surface')}` status=`{item.get('status')}`"
            )
    return "\n".join(lines) + "\n"


def _stage_specialists(stage: str) -> list[str]:
    return list(dict(_STAGE_PLAN.get(stage, {})).get("specialists", []))


def _access_decisions_for_stage(
    *,
    stage: str,
    data_path: str | None,
    source_surface: str,
    source_command: str,
) -> list[dict[str, Any]]:
    profiles = {item.specialist: item for item in build_default_capability_profiles()}
    decisions: list[dict[str, Any]] = []
    for specialist in _stage_specialists(stage):
        profile = profiles.get(specialist)
        if profile is None:
            continue
        decisions.append(
            {
                "decision_id": _identifier("access"),
                "recorded_at": _utc_now(),
                "stage": stage,
                "specialist": specialist,
                "access_kind": "artifact_scope",
                "requested_scope": list(profile.artifact_read_scope),
                "effective_scope": list(profile.artifact_read_scope),
                "decision": "granted",
                "reason": "capability_profile_scope",
                "source_surface": source_surface,
                "source_command": source_command,
            }
        )
        if data_path:
            decisions.append(
                {
                    "decision_id": _identifier("access"),
                    "recorded_at": _utc_now(),
                    "stage": stage,
                    "specialist": specialist,
                    "access_kind": "raw_rows",
                    "requested_scope": [str(data_path)],
                    "effective_scope": [str(data_path)] if profile.raw_row_access else [],
                    "decision": "granted" if profile.raw_row_access else "denied",
                    "reason": "capability_profile_allows_raw_rows" if profile.raw_row_access else "rowless_by_default",
                    "source_surface": source_surface,
                    "source_command": source_command,
                }
            )
        decisions.append(
            {
                "decision_id": _identifier("access"),
                "recorded_at": _utc_now(),
                "stage": stage,
                "specialist": specialist,
                "access_kind": "semantic_context",
                "requested_scope": [profile.semantic_access],
                "effective_scope": [profile.semantic_access],
                "decision": "granted",
                "reason": "semantic_context_policy",
                "source_surface": source_surface,
                "source_command": source_command,
            }
        )
    return decisions


def _write_checkpoint(
    root: Path,
    controls: RuntimeControls,
    *,
    stage: str,
    reason: str,
    source_surface: str,
    event_id: str,
    artifact_paths: list[str],
) -> dict[str, Any]:
    existing = _read_json_artifact(root, "run_checkpoint_manifest")
    checkpoints = list(existing.get("checkpoints", [])) if isinstance(existing.get("checkpoints"), list) else []
    reflection_memory = _safe_read_json(root / "reflection_memory.json")
    memory_flush = _safe_read_json(root / "memory_flush_report.json")
    run_state = _safe_read_json(root / "run_state.json")
    checkpoint = {
        "checkpoint_id": _identifier("ckpt"),
        "recorded_at": _utc_now(),
        "stage": stage,
        "reason": reason,
        "source_surface": source_surface,
        "event_id": event_id,
        "artifact_paths": [item for item in artifact_paths if item],
        "reflection_stage": str(reflection_memory.get("current_stage", "")).strip() or None,
        "memory_flush_stage": str(memory_flush.get("flush_stage", "")).strip() or None,
        "run_state_stage": str(run_state.get("current_stage", "")).strip() or None,
        "preserved_memory_state": bool(reflection_memory or memory_flush),
    }
    checkpoints.append(checkpoint)
    _write_checkpoint_manifest(root, controls, checkpoints=checkpoints, latest_stage=stage)
    return checkpoint


def _write_checkpoint_manifest(
    root: Path,
    controls: RuntimeControls,
    *,
    checkpoints: list[dict[str, Any]],
    latest_stage: str | None,
) -> None:
    write_runtime_artifact(
        root,
        key="run_checkpoint_manifest",
        payload=RunCheckpointManifestArtifact(
            schema_version=RUN_CHECKPOINT_MANIFEST_SCHEMA_VERSION,
            generated_at=_utc_now(),
            controls=controls,
            latest_stage=latest_stage,
            checkpoints=checkpoints,
            summary=(
                f"Relaytic currently tracks {len(checkpoints)} runtime checkpoint(s); "
                f"latest stage is `{latest_stage or 'unknown'}`."
            ),
        ).to_dict(),
    )


def _write_hook_execution_log(root: Path, controls: RuntimeControls, *, executions: list[dict[str, Any]]) -> None:
    write_runtime_artifact(
        root,
        key="hook_execution_log",
        payload=HookExecutionLogArtifact(
            schema_version=HOOK_EXECUTION_LOG_SCHEMA_VERSION,
            generated_at=_utc_now(),
            controls=controls,
            executions=executions,
            summary=f"Relaytic recorded {len(executions)} hook execution(s) in the local runtime.",
        ).to_dict(),
    )


def _write_data_access_audit(root: Path, controls: RuntimeControls, *, decisions: list[dict[str, Any]]) -> None:
    denied_count = sum(1 for item in decisions if str(item.get("decision", "")) == "denied")
    write_runtime_artifact(
        root,
        key="data_access_audit",
        payload=DataAccessAuditArtifact(
            schema_version=DATA_ACCESS_AUDIT_SCHEMA_VERSION,
            generated_at=_utc_now(),
            controls=controls,
            decisions=decisions,
            denied_count=denied_count,
            summary=f"Relaytic recorded {len(decisions)} data-access decision(s), including {denied_count} denial(s).",
        ).to_dict(),
    )


def _write_context_influence_report(root: Path, controls: RuntimeControls, *, stage_reports: list[dict[str, Any]]) -> None:
    write_runtime_artifact(
        root,
        key="context_influence_report",
        payload=ContextInfluenceReportArtifact(
            schema_version=CONTEXT_INFLUENCE_REPORT_SCHEMA_VERSION,
            generated_at=_utc_now(),
            controls=controls,
            stage_reports=stage_reports,
            summary=f"Relaytic recorded {len(stage_reports)} runtime context-influence record(s).",
        ).to_dict(),
    )


def _extend_data_access_audit(root: Path, controls: RuntimeControls, *, decisions: list[dict[str, Any]]) -> None:
    existing = _read_json_artifact(root, "data_access_audit")
    current = list(existing.get("decisions", [])) if isinstance(existing.get("decisions"), list) else []
    current.extend(decisions)
    _write_data_access_audit(root, controls, decisions=current)


def _append_context_stage_report(root: Path, controls: RuntimeControls, *, stage_report: dict[str, Any]) -> None:
    existing = _read_json_artifact(root, "context_influence_report")
    current = list(existing.get("stage_reports", [])) if isinstance(existing.get("stage_reports"), list) else []
    current.append(stage_report)
    _write_context_influence_report(root, controls, stage_reports=current)


def _update_context_stage_report(root: Path, controls: RuntimeControls, *, start_event_id: str, updates: dict[str, Any]) -> None:
    existing = _read_json_artifact(root, "context_influence_report")
    current = list(existing.get("stage_reports", [])) if isinstance(existing.get("stage_reports"), list) else []
    for item in reversed(current):
        if str(item.get("start_event_id", "")).strip() == start_event_id:
            for key, value in updates.items():
                if key == "notes":
                    existing_notes = list(item.get("notes", [])) if isinstance(item.get("notes"), list) else []
                    new_notes = [str(note).strip() for note in value if str(note).strip()]
                    item["notes"] = existing_notes + new_notes
                elif key == "hook_effects":
                    existing_effects = list(item.get("hook_effects", [])) if isinstance(item.get("hook_effects"), list) else []
                    new_effects = [str(effect).strip() for effect in value if str(effect).strip()]
                    item["hook_effects"] = existing_effects + new_effects
                else:
                    item[key] = value
            break
    _write_context_influence_report(root, controls, stage_reports=current)


def _record_hook(root: Path, controls: RuntimeControls, *, execution: dict[str, Any]) -> None:
    existing = _read_json_artifact(root, "hook_execution_log")
    current = list(existing.get("executions", [])) if isinstance(existing.get("executions"), list) else []
    current.append(execution)
    _write_hook_execution_log(root, controls, executions=current)


def _existing_artifact_paths(root: Path) -> list[str]:
    artifact_paths: list[str] = []
    for filename in [
        "manifest.json",
        "intake_record.json",
        "dataset_profile.json",
        "plan.json",
        "challenger_report.json",
        "completion_decision.json",
        "promotion_decision.json",
        "run_summary.json",
        *RUNTIME_FILENAMES.values(),
    ]:
        path = root / filename
        if path.exists():
            artifact_paths.append(str(path))
    return artifact_paths


def _infer_existing_stage(root: Path) -> str:
    if any(
        (root / filename).exists()
        for filename in (
            "autonomy_loop_state.json",
            "autonomy_round_report.json",
            "branch_outcome_matrix.json",
            "champion_lineage.json",
            "loop_budget_report.json",
        )
    ):
        return "autonomy_reviewed"
    if (root / "promotion_decision.json").exists():
        return "lifecycle_reviewed"
    if (root / "benchmark_parity_report.json").exists():
        return "benchmark_reviewed"
    if (root / "research_brief.json").exists():
        return "research_reviewed"
    if (root / "semantic_debate_report.json").exists():
        return "intelligence_reviewed"
    if (root / "completion_decision.json").exists():
        return "completion_reviewed"
    if (root / "audit_report.json").exists():
        return "evidence_reviewed"
    if (root / "plan.json").exists():
        return "planned"
    if (root / "dataset_profile.json").exists():
        return "investigated"
    if (root / "intake_record.json").exists():
        return "intake_interpreted"
    return "initialized"


def _resolve_runtime_stage_label(root: Path, *, latest_stage: str, last_event_stage: str) -> str:
    inferred = _infer_existing_stage(root)
    if inferred == "autonomy_reviewed":
        return "autonomy"
    if inferred == "lifecycle_reviewed":
        return "lifecycle"
    if inferred == "benchmark_reviewed":
        return "benchmark"
    if inferred == "research_reviewed":
        return "research"
    if inferred == "intelligence_reviewed":
        return "intelligence"
    if inferred == "completion_reviewed":
        return "completion"
    if inferred == "evidence_reviewed":
        return "evidence"
    if inferred == "planned":
        return "planning"
    if inferred == "investigated":
        return "investigation"
    if inferred == "intake_interpreted":
        return "intake"
    if latest_stage and latest_stage != "memory":
        return latest_stage
    if latest_stage:
        return latest_stage
    if last_event_stage:
        return last_event_stage
    return inferred


def _build_event(
    *,
    event_type: str,
    stage: str,
    source_surface: str,
    source_command: str,
    status: str,
    summary: str,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "schema_version": LAB_EVENT_SCHEMA_VERSION,
        "event_id": _identifier("evt"),
        "occurred_at": _utc_now(),
        "event_type": event_type,
        "stage": stage,
        "source_surface": source_surface,
        "source_command": source_command,
        "status": status,
        "summary": summary,
        "metadata": dict(metadata or {}),
    }


def _read_json_artifact(root: Path, key: str) -> dict[str, Any]:
    filename = RUNTIME_FILENAMES[key]
    return _safe_read_json(root / filename)


def _safe_read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _identifier(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex[:12]}"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()
