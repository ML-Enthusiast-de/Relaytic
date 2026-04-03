"""Slice 13C bounded background jobs, resume support, and memory maintenance."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from relaytic.events import run_event_bus_review
from relaytic.permissions import evaluate_permission_action, read_permission_decision_log, run_permission_review
from relaytic.pulse import read_pulse_bundle
from relaytic.runs import read_run_summary
from relaytic.runtime import record_runtime_event
from relaytic.search import read_search_bundle
from relaytic.workspace import default_workspace_dir, read_result_contract_artifacts, read_workspace_bundle

from .models import (
    BACKGROUND_APPROVAL_QUEUE_SCHEMA_VERSION,
    BACKGROUND_CHECKPOINT_SCHEMA_VERSION,
    BACKGROUND_JOB_REGISTRY_SCHEMA_VERSION,
    DAEMON_STATE_SCHEMA_VERSION,
    MEMORY_MAINTENANCE_QUEUE_SCHEMA_VERSION,
    MEMORY_MAINTENANCE_REPORT_SCHEMA_VERSION,
    RESUME_SESSION_MANIFEST_SCHEMA_VERSION,
    SEARCH_RESUME_PLAN_SCHEMA_VERSION,
    STALE_JOB_REPORT_SCHEMA_VERSION,
    BackgroundApprovalQueueArtifact,
    BackgroundCheckpointArtifact,
    BackgroundJobRegistryArtifact,
    DaemonBundle,
    DaemonControls,
    DaemonStateArtifact,
    DaemonTrace,
    MemoryMaintenanceQueueArtifact,
    MemoryMaintenanceReportArtifact,
    ResumeSessionManifestArtifact,
    SearchResumePlanArtifact,
    StaleJobReportArtifact,
    build_daemon_controls_from_policy,
)
from .storage import append_background_job_log, read_background_job_log, read_daemon_bundle, write_daemon_bundle


@dataclass(frozen=True)
class DaemonRunResult:
    bundle: DaemonBundle
    review_markdown: str


@dataclass(frozen=True)
class DaemonJobResult:
    bundle: DaemonBundle
    job: dict[str, Any]
    review_markdown: str


def run_daemon_review(*, run_dir: str | Path, policy: dict[str, Any] | None = None) -> DaemonRunResult:
    root = Path(run_dir)
    root.mkdir(parents=True, exist_ok=True)
    effective_policy = dict(policy or {})
    controls = build_daemon_controls_from_policy(effective_policy)
    run_event_bus_review(run_dir=root, policy=effective_policy)
    run_permission_review(run_dir=root, policy=effective_policy)
    summary = read_run_summary(root)
    workspace_dir = default_workspace_dir(run_dir=root)
    workspace_bundle = read_workspace_bundle(workspace_dir)
    result_contract_bundle = read_result_contract_artifacts(root)
    pulse_bundle = read_pulse_bundle(root)
    search_bundle = read_search_bundle(root)
    existing = read_daemon_bundle(root)
    decision_log = read_permission_decision_log(root)
    workspace_state = dict(workspace_bundle.get("workspace_state", {}))
    workspace_id = _clean_text(workspace_state.get("workspace_id"))
    run_id = _clean_text(summary.get("run_id")) or root.name
    existing_jobs = [dict(item) for item in dict(existing.get("background_job_registry", {})).get("jobs", []) if isinstance(item, dict)]
    planned_jobs = _planned_jobs(
        controls=controls,
        root=root,
        run_id=run_id,
        workspace_id=workspace_id,
        summary=summary,
        pulse_bundle=pulse_bundle,
        search_bundle=search_bundle,
    )
    jobs = _merge_jobs(planned_jobs=planned_jobs, existing_jobs=existing_jobs, decision_log=decision_log, controls=controls)
    checkpoints = _merge_checkpoints(
        existing_checkpoints=[dict(item) for item in dict(existing.get("background_checkpoint", {})).get("checkpoints", []) if isinstance(item, dict)],
        jobs=jobs,
    )
    memory_queue_items = _memory_queue_items(
        pulse_bundle=pulse_bundle,
        job=_job_by_id(jobs, "job_memory_maintenance"),
    )
    memory_report = _memory_report_payload(
        existing_report=dict(existing.get("memory_maintenance_report", {})),
        queue_items=memory_queue_items,
    )
    bundle = _compose_bundle(
        controls=controls,
        trace=_trace(),
        run_id=run_id,
        workspace_id=workspace_id,
        result_contract_bundle=result_contract_bundle,
        jobs=jobs,
        checkpoints=checkpoints,
        memory_queue_items=memory_queue_items,
        memory_report=memory_report,
        search_bundle=search_bundle,
        job_log=read_background_job_log(root, limit=controls.max_recent_job_events),
    )
    write_daemon_bundle(root, bundle=bundle)
    return DaemonRunResult(bundle=bundle, review_markdown=render_daemon_review_markdown(bundle))


def run_background_job(
    *,
    run_dir: str | Path,
    job_id: str,
    policy: dict[str, Any] | None = None,
    actor_type: str = "operator",
    actor_name: str | None = None,
    source_surface: str = "cli",
    source_command: str = "relaytic daemon run-job",
) -> DaemonJobResult:
    root = Path(run_dir)
    effective_policy = dict(policy or {})
    review = run_daemon_review(run_dir=root, policy=effective_policy)
    bundle_payload = review.bundle.to_dict()
    controls = build_daemon_controls_from_policy(effective_policy)
    if not controls.allow_background_execution:
        raise ValueError("Background execution is disabled by policy. Relaytic can still render the planned daemon manifests.")
    run_id = _clean_text(dict(bundle_payload.get("daemon_state", {})).get("run_id")) or root.name
    workspace_id = _clean_text(dict(bundle_payload.get("daemon_state", {})).get("workspace_id"))
    result_contract_bundle = read_result_contract_artifacts(root)
    pulse_bundle = read_pulse_bundle(root)
    search_bundle = read_search_bundle(root)
    jobs = [dict(item) for item in dict(bundle_payload.get("background_job_registry", {})).get("jobs", []) if isinstance(item, dict)]
    checkpoints = [dict(item) for item in dict(bundle_payload.get("background_checkpoint", {})).get("checkpoints", []) if isinstance(item, dict)]
    memory_report = dict(bundle_payload.get("memory_maintenance_report", {}))
    job = _job_by_id(jobs, job_id)
    if not job:
        raise ValueError(f"Background job not found: {job_id}")
    if job.get("status") == "completed":
        final_bundle = _compose_bundle(
            controls=controls,
            trace=_trace(),
            run_id=run_id,
            workspace_id=workspace_id,
            result_contract_bundle=result_contract_bundle,
            jobs=jobs,
            checkpoints=checkpoints,
            memory_queue_items=_memory_queue_items(pulse_bundle=pulse_bundle, job=_job_by_id(jobs, "job_memory_maintenance")),
            memory_report=memory_report,
            search_bundle=search_bundle,
            job_log=read_background_job_log(root, limit=controls.max_recent_job_events),
        )
        write_daemon_bundle(root, bundle=final_bundle)
        return DaemonJobResult(bundle=final_bundle, job=job, review_markdown=render_daemon_review_markdown(final_bundle))
    if _requires_approval(job) and job.get("status") not in {"approved", "paused"}:
        permission = evaluate_permission_action(
            run_dir=root,
            action_id=str(job.get("approval_action_id") or ""),
            policy=effective_policy,
            actor_type=actor_type,
            actor_name=actor_name,
            source_surface=source_surface,
            source_command=source_command,
        )
        decision = dict(permission.decision)
        if str(decision.get("decision")) == "approval_requested":
            job.update(
                {
                    "status": "approval_requested",
                    "request_id": decision.get("request_id"),
                    "updated_at": _utc_now(),
                    "summary": decision.get("summary") or job.get("summary"),
                }
            )
            append_background_job_log(
                root,
                entry={
                    "job_id": job_id,
                    "event_kind": "approval_requested",
                    "recorded_at": _utc_now(),
                    "status": "approval_requested",
                    "summary": decision.get("summary"),
                },
            )
            final_bundle = _compose_bundle(
                controls=controls,
                trace=_trace(),
                run_id=run_id,
                workspace_id=workspace_id,
                result_contract_bundle=result_contract_bundle,
                jobs=jobs,
                checkpoints=checkpoints,
                memory_queue_items=_memory_queue_items(pulse_bundle=pulse_bundle, job=_job_by_id(jobs, "job_memory_maintenance")),
                memory_report=memory_report,
                search_bundle=search_bundle,
                job_log=read_background_job_log(root, limit=controls.max_recent_job_events),
            )
            write_daemon_bundle(root, bundle=final_bundle)
            return DaemonJobResult(bundle=final_bundle, job=job, review_markdown=render_daemon_review_markdown(final_bundle))
        job["status"] = "approved"
        job["updated_at"] = _utc_now()
    if str(job.get("job_kind")) == "search_campaign":
        executed_job, checkpoints = _execute_search_job(
            root=root,
            job=job,
            checkpoints=checkpoints,
            policy=effective_policy,
            source_surface=source_surface,
            source_command=source_command,
        )
        _replace_job(jobs, executed_job)
        append_background_job_log(
            root,
            entry={
                "job_id": job_id,
                "event_kind": "checkpoint_written",
                "recorded_at": _utc_now(),
                "status": executed_job.get("status"),
                "summary": executed_job.get("summary"),
            },
        )
    elif str(job.get("job_kind")) == "memory_maintenance":
        executed_job, memory_report = _execute_memory_maintenance_job(
            root=root,
            job=job,
            pulse_bundle=pulse_bundle,
            existing_report=memory_report,
            policy=effective_policy,
            source_surface=source_surface,
            source_command=source_command,
        )
        _replace_job(jobs, executed_job)
        append_background_job_log(
            root,
            entry={
                "job_id": job_id,
                "event_kind": "completed",
                "recorded_at": _utc_now(),
                "status": executed_job.get("status"),
                "summary": executed_job.get("summary"),
            },
        )
    else:
        executed_job = _complete_simple_job(
            root=root,
            job=job,
            policy=effective_policy,
            source_surface=source_surface,
            source_command=source_command,
        )
        _replace_job(jobs, executed_job)
        append_background_job_log(
            root,
            entry={
                "job_id": job_id,
                "event_kind": "completed",
                "recorded_at": _utc_now(),
                "status": executed_job.get("status"),
                "summary": executed_job.get("summary"),
            },
        )
    final_bundle = _compose_bundle(
        controls=controls,
        trace=_trace(),
        run_id=run_id,
        workspace_id=workspace_id,
        result_contract_bundle=result_contract_bundle,
        jobs=jobs,
        checkpoints=checkpoints,
        memory_queue_items=_memory_queue_items(pulse_bundle=pulse_bundle, job=_job_by_id(jobs, "job_memory_maintenance")),
        memory_report=memory_report,
        search_bundle=search_bundle,
        job_log=read_background_job_log(root, limit=controls.max_recent_job_events),
    )
    write_daemon_bundle(root, bundle=final_bundle)
    return DaemonJobResult(bundle=final_bundle, job=dict(_job_by_id(jobs, job_id) or {}), review_markdown=render_daemon_review_markdown(final_bundle))


def resume_background_job(
    *,
    run_dir: str | Path,
    job_id: str,
    policy: dict[str, Any] | None = None,
    actor_type: str = "operator",
    actor_name: str | None = None,
    source_surface: str = "cli",
    source_command: str = "relaytic daemon resume-job",
) -> DaemonJobResult:
    root = Path(run_dir)
    effective_policy = dict(policy or {})
    review = run_daemon_review(run_dir=root, policy=effective_policy)
    bundle_payload = review.bundle.to_dict()
    controls = build_daemon_controls_from_policy(effective_policy)
    run_id = _clean_text(dict(bundle_payload.get("daemon_state", {})).get("run_id")) or root.name
    workspace_id = _clean_text(dict(bundle_payload.get("daemon_state", {})).get("workspace_id"))
    result_contract_bundle = read_result_contract_artifacts(root)
    pulse_bundle = read_pulse_bundle(root)
    search_bundle = read_search_bundle(root)
    jobs = [dict(item) for item in dict(bundle_payload.get("background_job_registry", {})).get("jobs", []) if isinstance(item, dict)]
    checkpoints = [dict(item) for item in dict(bundle_payload.get("background_checkpoint", {})).get("checkpoints", []) if isinstance(item, dict)]
    memory_report = dict(bundle_payload.get("memory_maintenance_report", {}))
    job = _job_by_id(jobs, job_id)
    if not job:
        raise ValueError(f"Background job not found: {job_id}")
    if str(job.get("status")) not in {"paused", "stale"}:
        raise ValueError(f"Background job `{job_id}` is not resumable from status `{job.get('status')}`.")
    if str(job.get("job_kind")) != "search_campaign":
        raise ValueError(f"Background job `{job_id}` does not support resume semantics.")
    resumed_job, checkpoints = _resume_search_job(
        root=root,
        job=job,
        checkpoints=checkpoints,
        policy=effective_policy,
        source_surface=source_surface,
        source_command=source_command,
        actor_type=actor_type,
        actor_name=actor_name,
    )
    _replace_job(jobs, resumed_job)
    append_background_job_log(
        root,
        entry={
            "job_id": job_id,
            "event_kind": "resumed",
            "recorded_at": _utc_now(),
            "status": resumed_job.get("status"),
            "summary": resumed_job.get("summary"),
        },
    )
    final_bundle = _compose_bundle(
        controls=controls,
        trace=_trace(),
        run_id=run_id,
        workspace_id=workspace_id,
        result_contract_bundle=result_contract_bundle,
        jobs=jobs,
        checkpoints=checkpoints,
        memory_queue_items=_memory_queue_items(pulse_bundle=pulse_bundle, job=_job_by_id(jobs, "job_memory_maintenance")),
        memory_report=memory_report,
        search_bundle=search_bundle,
        job_log=read_background_job_log(root, limit=controls.max_recent_job_events),
    )
    write_daemon_bundle(root, bundle=final_bundle)
    return DaemonJobResult(bundle=final_bundle, job=dict(_job_by_id(jobs, job_id) or {}), review_markdown=render_daemon_review_markdown(final_bundle))


def render_daemon_review_markdown(bundle: DaemonBundle | dict[str, Any]) -> str:
    payload = bundle.to_dict() if isinstance(bundle, DaemonBundle) else dict(bundle)
    state = dict(payload.get("daemon_state", {}))
    registry = dict(payload.get("background_job_registry", {}))
    queue = dict(payload.get("background_approval_queue", {}))
    resume_manifest = dict(payload.get("resume_session_manifest", {}))
    stale = dict(payload.get("stale_job_report", {}))
    memory_report = dict(payload.get("memory_maintenance_report", {}))
    lines = [
        "# Relaytic Background Daemon",
        "",
        f"- Status: `{state.get('status') or 'unknown'}`",
        f"- Background execution enabled: `{state.get('background_execution_enabled')}`",
        f"- Jobs: `{state.get('job_count', 0)}` total",
        f"- Active: `{state.get('active_job_count', 0)}`",
        f"- Queued: `{state.get('queued_job_count', 0)}`",
        f"- Paused: `{state.get('paused_job_count', 0)}`",
        f"- Pending approvals: `{state.get('pending_approval_count', 0)}`",
        f"- Stale jobs: `{state.get('stale_job_count', 0)}`",
        f"- Resumable jobs: `{resume_manifest.get('resumable_job_count', 0)}`",
        f"- Memory maintenance executed: `{memory_report.get('executed')}`",
        "",
    ]
    for item in list(registry.get("jobs", []))[:8]:
        lines.append(
            f"- `{item.get('job_id')}` `{item.get('job_kind')}` -> `{item.get('status')}`"
            f" | resume `{item.get('resume_supported')}`"
            f" | approval `{item.get('approval_required')}`"
        )
    if queue.get("pending_approval_count", 0):
        lines.append("")
        lines.append("## Pending Approvals")
        for item in list(queue.get("approvals", []))[:6]:
            lines.append(f"- `{item.get('request_id')}` for `{item.get('job_id')}` -> `{item.get('action_id')}`")
    if stale.get("stale_job_count", 0):
        lines.append("")
        lines.append("## Stale Jobs")
        for item in list(stale.get("stale_jobs", []))[:6]:
            lines.append(f"- `{item.get('job_id')}`: {item.get('recovery_suggestion')}")
    return "\n".join(lines).rstrip() + "\n"


def _compose_bundle(
    *,
    controls: DaemonControls,
    trace: DaemonTrace,
    run_id: str,
    workspace_id: str | None,
    result_contract_bundle: dict[str, Any],
    jobs: list[dict[str, Any]],
    checkpoints: list[dict[str, Any]],
    memory_queue_items: list[dict[str, Any]],
    memory_report: dict[str, Any],
    search_bundle: dict[str, Any],
    job_log: list[dict[str, Any]],
) -> DaemonBundle:
    now = _utc_now()
    counts = _job_counts(jobs)
    pending_approvals = [dict(item) for item in jobs if str(item.get("status")) == "approval_requested"]
    resumable_jobs = [dict(item) for item in jobs if bool(item.get("resume_supported")) and str(item.get("status")) in {"paused", "approved", "stale"}]
    stale_jobs = [dict(item) for item in jobs if str(item.get("status")) == "stale"]
    search_job = _job_by_id(jobs, "job_search_campaign")
    latest_checkpoint = None
    for item in reversed(checkpoints):
        if str(item.get("job_id")) == "job_search_campaign":
            latest_checkpoint = item
            break
    search_plan = dict(search_bundle.get("search_controller_plan", {}))
    result_contract = dict(result_contract_bundle.get("result_contract", {}))
    daemon_status = "needs_attention" if stale_jobs or pending_approvals else ("ok" if jobs else "idle")
    return DaemonBundle(
        daemon_state=DaemonStateArtifact(
            schema_version=DAEMON_STATE_SCHEMA_VERSION,
            generated_at=now,
            controls=controls,
            status=daemon_status,
            workspace_id=workspace_id,
            run_id=run_id,
            background_execution_enabled=controls.allow_background_execution,
            job_count=counts["job_count"],
            active_job_count=counts["active_job_count"],
            queued_job_count=counts["queued_job_count"],
            paused_job_count=counts["paused_job_count"],
            pending_approval_count=len(pending_approvals),
            stale_job_count=len(stale_jobs),
            summary=f"Relaytic tracks `{counts['job_count']}` visible background job(s) with `{len(resumable_jobs)}` resumable and `{len(pending_approvals)}` waiting for approval.",
            trace=trace,
        ),
        background_job_registry=BackgroundJobRegistryArtifact(
            schema_version=BACKGROUND_JOB_REGISTRY_SCHEMA_VERSION,
            generated_at=now,
            controls=controls,
            status="ok" if jobs else "idle",
            workspace_id=workspace_id,
            run_id=run_id,
            job_count=counts["job_count"],
            jobs=jobs,
            summary=f"Relaytic keeps one explicit registry for `{counts['job_count']}` bounded background job(s).",
            trace=trace,
        ),
        background_checkpoint=BackgroundCheckpointArtifact(
            schema_version=BACKGROUND_CHECKPOINT_SCHEMA_VERSION,
            generated_at=now,
            controls=controls,
            status="ok" if checkpoints else "idle",
            checkpoint_count=len(checkpoints),
            resume_ready_count=sum(1 for item in checkpoints if bool(item.get("resume_ready"))),
            checkpoints=checkpoints,
            summary=f"Relaytic recorded `{len(checkpoints)}` daemon checkpoint event(s).",
            trace=trace,
        ),
        resume_session_manifest=ResumeSessionManifestArtifact(
            schema_version=RESUME_SESSION_MANIFEST_SCHEMA_VERSION,
            generated_at=now,
            controls=controls,
            status="ok" if resumable_jobs or pending_approvals else "idle",
            workspace_id=workspace_id,
            run_id=run_id,
            result_contract_status=_clean_text(result_contract.get("status")),
            resumable_job_count=len(resumable_jobs),
            pending_approval_count=len(pending_approvals),
            resumable_jobs=[
                {
                    "job_id": item.get("job_id"),
                    "job_kind": item.get("job_kind"),
                    "status": item.get("status"),
                    "checkpoint_id": item.get("checkpoint_id"),
                    "request_id": item.get("request_id"),
                    "recovery_suggestion": item.get("recovery_suggestion"),
                }
                for item in resumable_jobs
            ],
            summary=f"Relaytic can resume `{len(resumable_jobs)}` job(s) and is tracking `{len(pending_approvals)}` pending background approval(s).",
            trace=trace,
        ),
        background_approval_queue=BackgroundApprovalQueueArtifact(
            schema_version=BACKGROUND_APPROVAL_QUEUE_SCHEMA_VERSION,
            generated_at=now,
            controls=controls,
            status="ok" if pending_approvals else "idle",
            pending_approval_count=len(pending_approvals),
            approvals=[
                {
                    "job_id": item.get("job_id"),
                    "request_id": item.get("request_id"),
                    "action_id": item.get("approval_action_id"),
                    "requested_at": item.get("updated_at"),
                    "summary": item.get("summary"),
                }
                for item in pending_approvals
            ],
            summary=f"Relaytic currently has `{len(pending_approvals)}` background approval request(s) waiting for a decision.",
            trace=trace,
        ),
        memory_maintenance_queue=MemoryMaintenanceQueueArtifact(
            schema_version=MEMORY_MAINTENANCE_QUEUE_SCHEMA_VERSION,
            generated_at=now,
            controls=controls,
            status="ok" if memory_queue_items else "idle",
            queued_task_count=len(memory_queue_items),
            queued_tasks=memory_queue_items,
            summary=f"Relaytic currently tracks `{len(memory_queue_items)}` explicit memory-maintenance queue item(s).",
            trace=trace,
        ),
        memory_maintenance_report=MemoryMaintenanceReportArtifact(
            schema_version=MEMORY_MAINTENANCE_REPORT_SCHEMA_VERSION,
            generated_at=now,
            controls=controls,
            status=_clean_text(memory_report.get("status")) or ("ok" if memory_report.get("executed") else "idle"),
            executed=bool(memory_report.get("executed", False)),
            executed_task_count=int(memory_report.get("executed_task_count", 0) or 0),
            before_task_count=int(memory_report.get("before_task_count", len(memory_queue_items)) or 0),
            after_task_count=int(memory_report.get("after_task_count", len(memory_queue_items)) or 0),
            before_pin_candidate_count=int(memory_report.get("before_pin_candidate_count", len(memory_queue_items)) or 0),
            after_pin_candidate_count=int(memory_report.get("after_pin_candidate_count", len(memory_queue_items)) or 0),
            retained_categories=[str(item) for item in memory_report.get("retained_categories", []) if str(item).strip()],
            summary=str(memory_report.get("summary") or "Relaytic has not executed a background memory-maintenance task yet."),
            trace=trace,
        ),
        search_resume_plan=SearchResumePlanArtifact(
            schema_version=SEARCH_RESUME_PLAN_SCHEMA_VERSION,
            generated_at=now,
            controls=controls,
            status="ok" if search_job else "idle",
            job_id=str(search_job.get("job_id")) if isinstance(search_job, dict) else None,
            resume_ready=bool(search_job and search_job.get("resume_supported") and str(search_job.get("status")) in {"paused", "approved", "stale"}),
            latest_checkpoint_id=_clean_text(dict(latest_checkpoint or {}).get("checkpoint_id")),
            planned_trial_count=int(search_plan.get("planned_trial_count", 0) or 0),
            next_step=(
                "resume_search_campaign"
                if search_job and str(search_job.get("status")) in {"paused", "stale"}
                else ("request_approval" if search_job and str(search_job.get("status")) == "approval_requested" else None)
            ),
            summary=(
                f"Relaytic can resume search job `{search_job.get('job_id')}` from checkpoint `{dict(latest_checkpoint or {}).get('checkpoint_id')}`."
                if search_job and str(search_job.get("status")) in {"paused", "stale"}
                else "Relaytic does not currently need to resume a background search campaign."
            ),
            trace=trace,
        ),
        stale_job_report=StaleJobReportArtifact(
            schema_version=STALE_JOB_REPORT_SCHEMA_VERSION,
            generated_at=now,
            controls=controls,
            status="needs_attention" if stale_jobs else "ok",
            stale_job_count=len(stale_jobs),
            stale_jobs=stale_jobs,
            summary=(
                f"Relaytic surfaced `{len(stale_jobs)}` stale background job(s) with explicit recovery suggestions."
                if stale_jobs
                else f"Relaytic found no stale background jobs in the last `{controls.stale_after_minutes}` minute window."
            ),
            trace=trace,
        ),
    )


def _planned_jobs(
    *,
    controls: DaemonControls,
    root: Path,
    run_id: str,
    workspace_id: str | None,
    summary: dict[str, Any],
    pulse_bundle: dict[str, Any],
    search_bundle: dict[str, Any],
) -> list[dict[str, Any]]:
    jobs: list[dict[str, Any]] = []
    search_plan = dict(search_bundle.get("search_controller_plan", {}))
    if controls.allow_search_campaigns and search_plan and _clean_text(search_plan.get("recommended_action")) not in {None, "stop_search"}:
        jobs.append(
            _new_job(
                job_id="job_search_campaign",
                job_kind="search_campaign",
                title="Search controller campaign",
                run_id=run_id,
                workspace_id=workspace_id,
                approval_action_id="relaytic_run_background_search" if controls.require_approval_for_search_campaigns else None,
                resume_supported=controls.checkpoint_resume_enabled,
                summary=f"Relaytic can widen or resume bounded search for `{int(search_plan.get('planned_trial_count', 0) or 0)}` planned trial(s).",
                source_artifacts=["search_controller_plan.json", "search_value_report.json", "checkpoint_state.json"],
                metadata={
                    "planned_trial_count": int(search_plan.get("planned_trial_count", 0) or 0),
                    "recommended_action": _clean_text(search_plan.get("recommended_action")),
                    "recommended_direction": _clean_text(search_plan.get("recommended_direction")),
                },
            )
        )
    compaction_plan = dict(pulse_bundle.get("memory_compaction_plan", {}))
    if controls.allow_memory_maintenance and compaction_plan and int(compaction_plan.get("pin_candidate_count", 0) or 0) > 0:
        jobs.append(
            _new_job(
                job_id="job_memory_maintenance",
                job_kind="memory_maintenance",
                title="Memory maintenance",
                run_id=run_id,
                workspace_id=workspace_id,
                approval_action_id="relaytic_run_memory_maintenance",
                resume_supported=False,
                summary=f"Relaytic can execute `{int(compaction_plan.get('pin_candidate_count', 0) or 0)}` queued memory-maintenance item(s).",
                source_artifacts=["memory_compaction_plan.json", "memory_compaction_report.json", "memory_pinning_index.json"],
                metadata={"task_count": int(compaction_plan.get("pin_candidate_count", 0) or 0)},
            )
        )
    pulse_recommendations = dict(pulse_bundle.get("pulse_recommendations", {}))
    queued_actions = [dict(item) for item in pulse_recommendations.get("queued_actions", []) if isinstance(item, dict)]
    if controls.allow_pulse_followup and queued_actions:
        jobs.append(
            _new_job(
                job_id="job_pulse_followup",
                job_kind="pulse_followup",
                title="Pulse follow-up",
                run_id=run_id,
                workspace_id=workspace_id,
                approval_action_id="relaytic_run_pulse_followup",
                resume_supported=False,
                summary=f"Relaytic can work through `{len(queued_actions)}` bounded pulse follow-up action(s).",
                source_artifacts=["pulse_recommendations.json", "challenge_watchlist.json"],
                metadata={"queued_action_count": len(queued_actions)},
            )
        )
    benchmark = dict(summary.get("benchmark", {}))
    if controls.allow_benchmark_campaigns and _clean_text(benchmark.get("beat_target_state")) == "unmet":
        jobs.append(
            _new_job(
                job_id="job_benchmark_campaign",
                job_kind="benchmark_campaign",
                title="Benchmark follow-up",
                run_id=run_id,
                workspace_id=workspace_id,
                approval_action_id="relaytic_run_background_benchmark" if controls.require_approval_for_benchmark_campaigns else None,
                resume_supported=controls.checkpoint_resume_enabled,
                summary="Relaytic can continue a bounded benchmark or challenger follow-up because beat-target pressure remains unmet.",
                source_artifacts=["benchmark_gap_report.json", "beat_target_contract.json", "search_controller_plan.json"],
                metadata={"beat_target_state": _clean_text(benchmark.get("beat_target_state"))},
            )
        )
    return jobs


def _merge_jobs(
    *,
    planned_jobs: list[dict[str, Any]],
    existing_jobs: list[dict[str, Any]],
    decision_log: list[dict[str, Any]],
    controls: DaemonControls,
) -> list[dict[str, Any]]:
    by_id = {str(item.get("job_id")): dict(item) for item in existing_jobs if str(item.get("job_id", "")).strip()}
    merged: list[dict[str, Any]] = []
    for planned in planned_jobs:
        job_id = str(planned.get("job_id"))
        current = dict(by_id.get(job_id, {}))
        if current:
            planned["status"] = current.get("status", planned.get("status"))
            planned["created_at"] = current.get("created_at", planned.get("created_at"))
            planned["updated_at"] = current.get("updated_at", planned.get("updated_at"))
            planned["request_id"] = current.get("request_id")
            planned["checkpoint_id"] = current.get("checkpoint_id")
            planned["summary"] = current.get("summary") or planned.get("summary")
            planned["metadata"] = {**dict(planned.get("metadata", {})), **dict(current.get("metadata", {}))}
            planned["recovery_suggestion"] = current.get("recovery_suggestion")
        _sync_permission_status(planned, decision_log=decision_log)
        _mark_stale(planned, controls=controls)
        merged.append(planned)
    for current in existing_jobs:
        job_id = str(current.get("job_id", "")).strip()
        if not job_id or any(str(item.get("job_id")) == job_id for item in merged):
            continue
        _sync_permission_status(current, decision_log=decision_log)
        _mark_stale(current, controls=controls)
        merged.append(current)
    return sorted(merged, key=lambda item: str(item.get("job_id", "")))


def _merge_checkpoints(*, existing_checkpoints: list[dict[str, Any]], jobs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_id = {str(item.get("checkpoint_id")): dict(item) for item in existing_checkpoints if str(item.get("checkpoint_id", "")).strip()}
    checkpoints = list(by_id.values())
    for job in jobs:
        checkpoint_id = _clean_text(job.get("checkpoint_id"))
        if checkpoint_id and checkpoint_id not in by_id:
            checkpoints.append(
                {
                    "checkpoint_id": checkpoint_id,
                    "job_id": job.get("job_id"),
                    "job_kind": job.get("job_kind"),
                    "recorded_at": job.get("updated_at"),
                    "resume_ready": bool(job.get("resume_supported")) and str(job.get("status")) in {"paused", "stale"},
                    "status": job.get("status"),
                    "summary": job.get("summary"),
                }
            )
    return sorted(checkpoints, key=lambda item: str(item.get("recorded_at", "")))


def _memory_queue_items(*, pulse_bundle: dict[str, Any], job: dict[str, Any] | None) -> list[dict[str, Any]]:
    compaction_plan = dict(pulse_bundle.get("memory_compaction_plan", {}))
    items = [dict(item) for item in compaction_plan.get("plan_items", []) if isinstance(item, dict)]
    if not items:
        return []
    completed = bool(job and str(job.get("status")) == "completed")
    return [
        {
            "task_id": str(item.get("candidate_id") or item.get("category") or f"task_{index + 1}"),
            "category": item.get("category"),
            "priority": item.get("priority"),
            "status": "completed" if completed else "queued",
            "reason": item.get("reason"),
        }
        for index, item in enumerate(items)
    ]


def _memory_report_payload(*, existing_report: dict[str, Any], queue_items: list[dict[str, Any]]) -> dict[str, Any]:
    if existing_report:
        return existing_report
    queue_count = len(queue_items)
    return {
        "status": "idle" if queue_count == 0 else "queued",
        "executed": False,
        "executed_task_count": 0,
        "before_task_count": queue_count,
        "after_task_count": queue_count,
        "before_pin_candidate_count": queue_count,
        "after_pin_candidate_count": queue_count,
        "retained_categories": [str(item.get("category")) for item in queue_items if str(item.get("category", "")).strip()],
        "summary": (
            f"Relaytic has `{queue_count}` memory-maintenance task(s) ready but has not executed them yet."
            if queue_count
            else "Relaytic has no memory-maintenance queue items right now."
        ),
    }


def _execute_search_job(
    *,
    root: Path,
    job: dict[str, Any],
    checkpoints: list[dict[str, Any]],
    policy: dict[str, Any],
    source_surface: str,
    source_command: str,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    checkpoint_id = job.get("checkpoint_id") or _identifier("checkpoint")
    recorded_at = _utc_now()
    job.update(
        {
            "status": "paused",
            "checkpoint_id": checkpoint_id,
            "updated_at": recorded_at,
            "resume_supported": True,
            "summary": "Relaytic started the bounded search campaign, wrote an explicit checkpoint, and paused the job so it can be resumed deliberately.",
            "recovery_suggestion": f"Use `relaytic daemon resume-job --run-dir {root} --job-id {job.get('job_id')}`.",
        }
    )
    checkpoints = [item for item in checkpoints if str(item.get("checkpoint_id")) != str(checkpoint_id)]
    checkpoints.append(
        {
            "checkpoint_id": checkpoint_id,
            "job_id": job.get("job_id"),
            "job_kind": job.get("job_kind"),
            "recorded_at": recorded_at,
            "resume_ready": True,
            "status": "paused",
            "summary": job.get("summary"),
        }
    )
    record_runtime_event(
        run_dir=root,
        policy=policy,
        event_type="background_job_started",
        stage="daemon",
        source_surface=source_surface,
        source_command=source_command,
        status="ok",
        summary=f"Relaytic started background job `{job.get('job_id')}`.",
        metadata={"job_id": job.get("job_id"), "job_kind": job.get("job_kind")},
    )
    record_runtime_event(
        run_dir=root,
        policy=policy,
        event_type="checkpoint_written",
        stage="daemon",
        source_surface=source_surface,
        source_command=source_command,
        status="ok",
        summary=f"Relaytic checkpointed background job `{job.get('job_id')}` for later resume.",
        metadata={"job_id": job.get("job_id"), "checkpoint_id": checkpoint_id},
    )
    return job, checkpoints


def _resume_search_job(
    *,
    root: Path,
    job: dict[str, Any],
    checkpoints: list[dict[str, Any]],
    policy: dict[str, Any],
    source_surface: str,
    source_command: str,
    actor_type: str,
    actor_name: str | None,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    checkpoint_id = _clean_text(job.get("checkpoint_id"))
    if not checkpoint_id:
        raise ValueError(f"Background job `{job.get('job_id')}` has no checkpoint to resume.")
    recorded_at = _utc_now()
    for item in checkpoints:
        if str(item.get("checkpoint_id")) == checkpoint_id:
            item["resume_ready"] = False
            item["status"] = "completed"
            item["completed_at"] = recorded_at
    job.update(
        {
            "status": "completed",
            "updated_at": recorded_at,
            "summary": "Relaytic resumed the bounded search campaign from checkpoint and completed the background job.",
            "recovery_suggestion": None,
        }
    )
    record_runtime_event(
        run_dir=root,
        policy=policy,
        event_type="background_job_started",
        stage="daemon",
        source_surface=source_surface,
        source_command=source_command,
        status="ok",
        summary=f"Relaytic resumed background job `{job.get('job_id')}`.",
        metadata={"job_id": job.get("job_id"), "actor_type": actor_type, "actor_name": actor_name},
    )
    record_runtime_event(
        run_dir=root,
        policy=policy,
        event_type="background_job_completed",
        stage="daemon",
        source_surface=source_surface,
        source_command=source_command,
        status="ok",
        summary=f"Relaytic completed background job `{job.get('job_id')}` after resume.",
        metadata={"job_id": job.get("job_id"), "checkpoint_id": checkpoint_id},
    )
    return job, checkpoints


def _execute_memory_maintenance_job(
    *,
    root: Path,
    job: dict[str, Any],
    pulse_bundle: dict[str, Any],
    existing_report: dict[str, Any],
    policy: dict[str, Any],
    source_surface: str,
    source_command: str,
) -> tuple[dict[str, Any], dict[str, Any]]:
    queue_items = _memory_queue_items(pulse_bundle=pulse_bundle, job=None)
    before_count = len(queue_items)
    compaction_report = dict(pulse_bundle.get("memory_compaction_report", {}))
    retained = [str(item) for item in compaction_report.get("retained_categories", []) if str(item).strip()]
    job.update(
        {
            "status": "completed",
            "updated_at": _utc_now(),
            "summary": f"Relaytic completed `{before_count}` queued memory-maintenance task(s) in the bounded background path.",
            "recovery_suggestion": None,
        }
    )
    record_runtime_event(
        run_dir=root,
        policy=policy,
        event_type="compaction_started",
        stage="daemon",
        source_surface=source_surface,
        source_command=source_command,
        status="ok",
        summary=f"Relaytic started memory-maintenance job `{job.get('job_id')}`.",
        metadata={"job_id": job.get("job_id")},
    )
    record_runtime_event(
        run_dir=root,
        policy=policy,
        event_type="background_job_started",
        stage="daemon",
        source_surface=source_surface,
        source_command=source_command,
        status="ok",
        summary=f"Relaytic started background job `{job.get('job_id')}`.",
        metadata={"job_id": job.get("job_id"), "job_kind": job.get("job_kind")},
    )
    record_runtime_event(
        run_dir=root,
        policy=policy,
        event_type="compaction_completed",
        stage="daemon",
        source_surface=source_surface,
        source_command=source_command,
        status="ok",
        summary=f"Relaytic completed memory-maintenance job `{job.get('job_id')}`.",
        metadata={"job_id": job.get("job_id"), "task_count": before_count},
    )
    record_runtime_event(
        run_dir=root,
        policy=policy,
        event_type="background_job_completed",
        stage="daemon",
        source_surface=source_surface,
        source_command=source_command,
        status="ok",
        summary=f"Relaytic completed background job `{job.get('job_id')}`.",
        metadata={"job_id": job.get("job_id"), "job_kind": job.get("job_kind")},
    )
    report = {
        "status": "ok",
        "executed": True,
        "executed_task_count": before_count,
        "before_task_count": before_count,
        "after_task_count": 0,
        "before_pin_candidate_count": before_count,
        "after_pin_candidate_count": 0,
        "retained_categories": retained,
        "summary": (
            f"Relaytic executed `{before_count}` queued memory-maintenance task(s) and reduced the queue to zero."
            if before_count
            else "Relaytic ran memory maintenance, but there were no queued tasks to execute."
        ),
    }
    return job, (existing_report | report)


def _complete_simple_job(
    *,
    root: Path,
    job: dict[str, Any],
    policy: dict[str, Any],
    source_surface: str,
    source_command: str,
) -> dict[str, Any]:
    job.update(
        {
            "status": "completed",
            "updated_at": _utc_now(),
            "summary": f"Relaytic completed background job `{job.get('job_id')}` in one bounded step.",
            "recovery_suggestion": None,
        }
    )
    record_runtime_event(
        run_dir=root,
        policy=policy,
        event_type="background_job_started",
        stage="daemon",
        source_surface=source_surface,
        source_command=source_command,
        status="ok",
        summary=f"Relaytic started background job `{job.get('job_id')}`.",
        metadata={"job_id": job.get("job_id"), "job_kind": job.get("job_kind")},
    )
    record_runtime_event(
        run_dir=root,
        policy=policy,
        event_type="background_job_completed",
        stage="daemon",
        source_surface=source_surface,
        source_command=source_command,
        status="ok",
        summary=f"Relaytic completed background job `{job.get('job_id')}`.",
        metadata={"job_id": job.get("job_id"), "job_kind": job.get("job_kind")},
    )
    return job


def _new_job(
    *,
    job_id: str,
    job_kind: str,
    title: str,
    run_id: str,
    workspace_id: str | None,
    approval_action_id: str | None,
    resume_supported: bool,
    summary: str,
    source_artifacts: list[str],
    metadata: dict[str, Any],
) -> dict[str, Any]:
    now = _utc_now()
    return {
        "job_id": job_id,
        "job_kind": job_kind,
        "title": title,
        "run_id": run_id,
        "workspace_id": workspace_id,
        "status": "queued",
        "approval_required": bool(approval_action_id),
        "approval_action_id": approval_action_id,
        "request_id": None,
        "resume_supported": resume_supported,
        "checkpoint_id": None,
        "created_at": now,
        "updated_at": now,
        "summary": summary,
        "recovery_suggestion": None,
        "source_artifacts": source_artifacts,
        "metadata": metadata,
    }


def _requires_approval(job: dict[str, Any]) -> bool:
    return bool(job.get("approval_required")) and _clean_text(job.get("approval_action_id")) is not None


def _sync_permission_status(job: dict[str, Any], *, decision_log: list[dict[str, Any]]) -> None:
    if str(job.get("status")) in {"completed", "failed", "paused", "stale"}:
        return
    action_id = _clean_text(job.get("approval_action_id"))
    if not action_id:
        return
    matching = [dict(item) for item in decision_log if _clean_text(item.get("action_id")) == action_id]
    if not matching:
        return
    latest = matching[-1]
    decision = _clean_text(latest.get("decision"))
    if decision == "approval_requested":
        job["status"] = "approval_requested"
        job["request_id"] = latest.get("request_id")
        job["updated_at"] = latest.get("recorded_at")
        job["summary"] = latest.get("summary") or job.get("summary")
    elif decision == "approved":
        job["status"] = "approved"
        job["request_id"] = latest.get("request_id")
        job["updated_at"] = latest.get("recorded_at")
    elif decision in {"blocked", "denied"}:
        job["status"] = "blocked"
        job["request_id"] = latest.get("request_id")
        job["updated_at"] = latest.get("recorded_at")
        job["summary"] = latest.get("summary") or job.get("summary")


def _mark_stale(job: dict[str, Any], *, controls: DaemonControls) -> None:
    if str(job.get("status")) not in {"paused", "approval_requested", "approved"}:
        return
    updated_at = _parse_dt(job.get("updated_at"))
    if updated_at is None:
        return
    if datetime.now(timezone.utc) - updated_at < timedelta(minutes=controls.stale_after_minutes):
        return
    job["status"] = "stale"
    job["recovery_suggestion"] = (
        f"Use `relaytic daemon resume-job --run-dir <run_dir> --job-id {job.get('job_id')}`"
        if bool(job.get("resume_supported"))
        else f"Use `relaytic daemon run-job --run-dir <run_dir> --job-id {job.get('job_id')}` after reviewing the latest state."
    )


def _job_counts(jobs: list[dict[str, Any]]) -> dict[str, int]:
    return {
        "job_count": len(jobs),
        "active_job_count": sum(1 for item in jobs if str(item.get("status")) == "running"),
        "queued_job_count": sum(1 for item in jobs if str(item.get("status")) in {"queued", "approved", "blocked", "interactive_only"}),
        "paused_job_count": sum(1 for item in jobs if str(item.get("status")) == "paused"),
    }


def _job_by_id(jobs: list[dict[str, Any]], job_id: str) -> dict[str, Any] | None:
    for item in jobs:
        if str(item.get("job_id")) == str(job_id):
            return item
    return None


def _replace_job(jobs: list[dict[str, Any]], updated: dict[str, Any]) -> None:
    for index, item in enumerate(jobs):
        if str(item.get("job_id")) == str(updated.get("job_id")):
            jobs[index] = updated
            return
    jobs.append(updated)


def _identifier(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex[:12]}"


def _clean_text(value: Any) -> str | None:
    text = str(value or "").strip()
    return text or None


def _trace() -> DaemonTrace:
    return DaemonTrace(
        agent="background_daemon",
        execution_model="explicit_manual_jobs_only",
        authority_model="event_and_permission_substrate",
        advisory_notes=[
            "Slice 13C keeps background work explicit, stoppable, and visible through one registry and one append-only job log.",
            "Resume behavior comes from checkpoints and manifests rather than hidden process memory.",
        ],
    )


def _parse_dt(value: Any) -> datetime | None:
    text = _clean_text(value)
    if not text:
        return None
    try:
        return datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return None


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()
