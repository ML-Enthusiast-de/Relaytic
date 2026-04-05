"""Slice 14A remote supervision, approvals, and handoff surfaces."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from relaytic.daemon import run_daemon_review
from relaytic.permissions import apply_permission_decision, run_permission_review
from relaytic.runs import materialize_run_summary, read_run_summary
from relaytic.runtime import record_runtime_event
from relaytic.workspace import default_workspace_dir, read_result_contract_artifacts, read_workspace_bundle

from .models import (
    APPROVAL_DECISION_LOG_SCHEMA_VERSION,
    APPROVAL_REQUEST_QUEUE_SCHEMA_VERSION,
    NOTIFICATION_DELIVERY_REPORT_SCHEMA_VERSION,
    REMOTE_CONTROL_AUDIT_SCHEMA_VERSION,
    REMOTE_OPERATOR_PRESENCE_SCHEMA_VERSION,
    REMOTE_SESSION_MANIFEST_SCHEMA_VERSION,
    REMOTE_TRANSPORT_REPORT_SCHEMA_VERSION,
    SUPERVISION_HANDOFF_SCHEMA_VERSION,
    ApprovalRequestQueueArtifact,
    NotificationDeliveryReportArtifact,
    RemoteControlBundle,
    RemoteControlControls,
    RemoteControlTrace,
    RemoteControlAuditArtifact,
    RemoteOperatorPresenceArtifact,
    RemoteSessionManifestArtifact,
    RemoteTransportReportArtifact,
    SupervisionHandoffArtifact,
    build_remote_control_controls_from_policy,
)
from .storage import (
    append_approval_decision_log,
    read_approval_decision_log,
    read_remote_control_bundle,
    write_remote_control_artifact,
    write_remote_control_bundle,
)


@dataclass(frozen=True)
class RemoteControlRunResult:
    bundle: RemoteControlBundle
    review_markdown: str


@dataclass(frozen=True)
class RemoteDecisionResult:
    bundle: RemoteControlBundle
    decision: dict[str, Any]
    review_markdown: str


def run_remote_control_review(
    *,
    run_dir: str | Path,
    policy: dict[str, Any] | None = None,
    actor_type: str | None = None,
    actor_name: str | None = None,
) -> RemoteControlRunResult:
    root = Path(run_dir)
    root.mkdir(parents=True, exist_ok=True)
    effective_policy = dict(policy or {})
    controls = build_remote_control_controls_from_policy(effective_policy)
    trace = _trace()
    permission_review = run_permission_review(run_dir=root, policy=effective_policy)
    daemon_review = run_daemon_review(run_dir=root, policy=effective_policy)
    summary_bundle = materialize_run_summary(run_dir=root, data_path=_resolve_run_data_path(root))
    summary = dict(summary_bundle.get("summary", {}))
    workspace_bundle = read_workspace_bundle(default_workspace_dir(run_dir=root))
    result_contract_bundle = read_result_contract_artifacts(root)
    existing = read_remote_control_bundle(root)
    decision_log = read_approval_decision_log(root, limit=controls.max_recent_decisions)

    transport_enabled = _transport_enabled(controls)
    write_actions_allowed = transport_enabled and (
        controls.allow_remote_approval_decisions or controls.allow_remote_handoffs
    )
    existing_handoff = dict(existing.get("supervision_handoff", {}))
    existing_presence = dict(existing.get("remote_operator_presence", {}))
    handoff_entries = [dict(item) for item in existing_handoff.get("entries", []) if isinstance(item, dict)]
    current_supervisor = (
        dict(existing_handoff.get("current_supervisor", {}))
        if isinstance(existing_handoff.get("current_supervisor"), dict)
        else {}
    )
    previous_supervisor = (
        dict(existing_handoff.get("previous_supervisor", {}))
        if isinstance(existing_handoff.get("previous_supervisor"), dict) and existing_handoff.get("previous_supervisor")
        else None
    )
    if not current_supervisor:
        current_supervisor = {
            "actor_type": _clean_text(actor_type) or "operator",
            "actor_name": _clean_text(actor_name),
            "assigned_at": existing_handoff.get("generated_at") or _utc_now(),
            "source_surface": "local",
            "status": "active",
        }
    presences = [dict(item) for item in existing_presence.get("presences", []) if isinstance(item, dict)]
    if actor_type or actor_name:
        presence_entry = {
            "actor_type": _clean_text(actor_type) or "operator",
            "actor_name": _clean_text(actor_name),
            "last_seen_at": _utc_now(),
            "source_surface": "remote",
            "status": "active" if transport_enabled else "blocked",
        }
        presences = [item for item in presences if not _same_presence(item, presence_entry)]
        presences.append(presence_entry)
    last_seen_at = _latest_presence_time(presences) or _clean_text(existing_presence.get("last_seen_at"))
    freshness_status = _presence_freshness(last_seen_at=last_seen_at, controls=controls, transport_enabled=transport_enabled)
    workspace_state = dict(workspace_bundle.get("workspace_state", {}))
    permission_mode = dict(permission_review.bundle.to_dict().get("permission_mode", {}))
    approval_policy = dict(permission_review.bundle.to_dict().get("approval_policy_report", {}))
    daemon_state = dict(daemon_review.bundle.to_dict().get("daemon_state", {}))
    background_queue = dict(daemon_review.bundle.to_dict().get("background_approval_queue", {}))
    approvals = _merged_approval_queue(approval_policy=approval_policy, background_queue=background_queue)
    notifications = _notification_items(
        approvals=approvals,
        handoff_entries=handoff_entries,
        transport_enabled=transport_enabled,
        current_supervisor=current_supervisor,
    )
    audit = _build_remote_audit(
        controls=controls,
        trace=trace,
        decision_log=decision_log,
        handoff_entries=handoff_entries,
        transport_enabled=transport_enabled,
    )
    bundle = RemoteControlBundle(
        remote_session_manifest=RemoteSessionManifestArtifact(
            schema_version=REMOTE_SESSION_MANIFEST_SCHEMA_VERSION,
            generated_at=_utc_now(),
            controls=controls,
            status="ok" if controls.enabled else "disabled",
            run_id=_clean_text(summary.get("run_id")) or root.name,
            workspace_id=_clean_text(workspace_state.get("workspace_id")),
            current_stage=_clean_text(summary.get("stage_completed")),
            permission_mode=_clean_text(permission_mode.get("current_mode")),
            transport_enabled=transport_enabled,
            transport_kind=controls.transport_kind,
            freshness_status=freshness_status,
            pending_approval_count=len(approvals),
            active_job_count=int(daemon_state.get("active_job_count", 0) or 0),
            next_recommended_action=_clean_text(dict(summary.get("next_step", {})).get("recommended_action")),
            result_contract_status=_clean_text(dict(result_contract_bundle.get("result_contract", {})).get("status")),
            current_supervisor_type=_clean_text(current_supervisor.get("actor_type")),
            current_supervisor_name=_clean_text(current_supervisor.get("actor_name")),
            write_actions_allowed=write_actions_allowed,
            summary=(
                f"Relaytic remote supervision is `{'enabled' if transport_enabled else 'disabled'}` with "
                f"`{len(approvals)}` pending approval(s) and supervisor "
                f"`{_clean_text(current_supervisor.get('actor_type')) or 'operator'}`."
            ),
            trace=trace,
        ),
        remote_transport_report=RemoteTransportReportArtifact(
            schema_version=REMOTE_TRANSPORT_REPORT_SCHEMA_VERSION,
            generated_at=_utc_now(),
            controls=controls,
            status="ok" if controls.enabled else "disabled",
            transport_enabled=transport_enabled,
            transport_kind=controls.transport_kind,
            transport_scope=controls.transport_scope,
            remote_url=controls.remote_url,
            freshness_seconds=controls.freshness_seconds,
            read_mostly=controls.read_mostly,
            write_actions_allowed=write_actions_allowed,
            summary=(
                "Relaytic remote control stays local-first and read-mostly; write actions are only available when "
                "the explicit remote transport is enabled."
            ),
            trace=trace,
        ),
        approval_request_queue=ApprovalRequestQueueArtifact(
            schema_version=APPROVAL_REQUEST_QUEUE_SCHEMA_VERSION,
            generated_at=_utc_now(),
            controls=controls,
            status="ok" if controls.enabled else "disabled",
            pending_approval_count=len(approvals),
            approval_source_count=len({item.get("queue_source") for item in approvals}),
            approvals=approvals,
            summary=f"Relaytic currently exposes `{len(approvals)}` approval request(s) through the remote supervision surface.",
            trace=trace,
        ),
        remote_operator_presence=RemoteOperatorPresenceArtifact(
            schema_version=REMOTE_OPERATOR_PRESENCE_SCHEMA_VERSION,
            generated_at=_utc_now(),
            controls=controls,
            status="ok" if controls.enabled else "disabled",
            current_supervisor_type=_clean_text(current_supervisor.get("actor_type")),
            current_supervisor_name=_clean_text(current_supervisor.get("actor_name")),
            last_seen_at=last_seen_at,
            freshness_status=freshness_status,
            active_presence_count=len(presences),
            presences=presences[-6:],
            summary=(
                f"Relaytic sees supervisor `{_clean_text(current_supervisor.get('actor_type')) or 'operator'}` "
                f"with freshness `{freshness_status}`."
            ),
            trace=trace,
        ),
        supervision_handoff=SupervisionHandoffArtifact(
            schema_version=SUPERVISION_HANDOFF_SCHEMA_VERSION,
            generated_at=_utc_now(),
            controls=controls,
            status="ok" if controls.enabled else "disabled",
            current_supervisor=current_supervisor,
            previous_supervisor=previous_supervisor,
            handoff_count=sum(1 for item in handoff_entries if _clean_text(item.get("status")) == "applied"),
            blocked_handoff_count=sum(1 for item in handoff_entries if _clean_text(item.get("status")) == "blocked"),
            last_handoff_at=_latest_handoff_time(handoff_entries),
            entries=handoff_entries[-12:],
            summary=(
                f"Relaytic remote supervision currently belongs to `{_clean_text(current_supervisor.get('actor_type')) or 'operator'}` "
                f"with `{len(handoff_entries)}` recorded handoff event(s)."
            ),
            trace=trace,
        ),
        notification_delivery_report=NotificationDeliveryReportArtifact(
            schema_version=NOTIFICATION_DELIVERY_REPORT_SCHEMA_VERSION,
            generated_at=_utc_now(),
            controls=controls,
            status="ok" if controls.enabled else "disabled",
            notification_count=len(notifications),
            undelivered_count=sum(1 for item in notifications if not bool(item.get("delivered"))),
            notifications=notifications[-12:],
            summary=f"Relaytic prepared `{len(notifications)}` remote notification item(s) from approvals and supervision state.",
            trace=trace,
        ),
        remote_control_audit=audit,
    )
    write_remote_control_bundle(root, bundle=bundle)
    return RemoteControlRunResult(bundle=bundle, review_markdown=render_remote_control_markdown(bundle))


def apply_remote_approval_decision(
    *,
    run_dir: str | Path,
    request_id: str,
    decision: str,
    policy: dict[str, Any] | None = None,
    actor_type: str = "operator",
    actor_name: str | None = None,
    source_surface: str = "remote",
    source_command: str = "relaytic remote decide",
) -> RemoteDecisionResult:
    root = Path(run_dir)
    controls = build_remote_control_controls_from_policy(policy or {})
    normalized_decision = _clean_text(decision)
    if normalized_decision not in {"approve", "deny"}:
        raise ValueError("Remote approval decision must be `approve` or `deny`.")
    if not _transport_enabled(controls) or not controls.allow_remote_approval_decisions:
        entry = _append_remote_decision_entry(
            root=root,
            request_id=request_id,
            decision=normalized_decision,
            actor_type=actor_type,
            actor_name=actor_name,
            source_surface=source_surface,
            source_command=source_command,
            status="blocked",
            reason_code="remote_transport_disabled",
            summary="Relaytic blocked the remote approval decision because remote supervision is disabled.",
        )
        record_runtime_event(
            run_dir=root,
            policy=policy or {},
            event_type="remote_access_blocked",
            stage="remote_control",
            source_surface=source_surface,
            source_command=source_command,
            status="blocked",
            summary=entry["summary"],
            metadata={"request_id": request_id, "decision": normalized_decision},
        )
        run_remote_control_review(run_dir=root, policy=policy, actor_type=actor_type, actor_name=actor_name)
        raise ValueError("Remote supervision is disabled or the configured transport is unavailable.")
    permission_result = apply_permission_decision(
        run_dir=root,
        request_id=request_id,
        decision=normalized_decision,
        policy=policy or {},
        actor_type=actor_type,
        actor_name=actor_name,
        source_surface=source_surface,
        source_command=source_command,
    )
    entry = _append_remote_decision_entry(
        root=root,
        request_id=request_id,
        decision=normalized_decision,
        actor_type=actor_type,
        actor_name=actor_name,
        source_surface=source_surface,
        source_command=source_command,
        status="applied",
        reason_code="remote_supervision_decision_applied",
        summary=f"Relaytic applied remote decision `{normalized_decision}` to approval request `{request_id}`.",
    )
    record_runtime_event(
        run_dir=root,
        policy=policy or {},
        event_type="remote_approval_decided",
        stage="remote_control",
        source_surface=source_surface,
        source_command=source_command,
        status="ok",
        summary=entry["summary"],
        metadata={"request_id": request_id, "decision": permission_result.decision.get("decision")},
    )
    review = run_remote_control_review(
        run_dir=root,
        policy=policy,
        actor_type=actor_type,
        actor_name=actor_name,
    )
    return RemoteDecisionResult(bundle=review.bundle, decision=entry, review_markdown=review.review_markdown)


def apply_remote_supervision_handoff(
    *,
    run_dir: str | Path,
    to_actor_type: str,
    to_actor_name: str | None = None,
    from_actor_type: str = "operator",
    from_actor_name: str | None = None,
    reason: str | None = None,
    policy: dict[str, Any] | None = None,
    source_surface: str = "remote",
    source_command: str = "relaytic remote handoff",
) -> RemoteDecisionResult:
    root = Path(run_dir)
    controls = build_remote_control_controls_from_policy(policy or {})
    existing = read_remote_control_bundle(root)
    handoff_payload = dict(existing.get("supervision_handoff", {}))
    current_supervisor = (
        dict(handoff_payload.get("current_supervisor", {}))
        if isinstance(handoff_payload.get("current_supervisor"), dict)
        else {}
    )
    entries = [dict(item) for item in handoff_payload.get("entries", []) if isinstance(item, dict)]
    previous_supervisor = current_supervisor or {
        "actor_type": _clean_text(from_actor_type) or "operator",
        "actor_name": _clean_text(from_actor_name),
        "assigned_at": _utc_now(),
        "source_surface": source_surface,
        "status": "active",
    }
    transport_enabled = _transport_enabled(controls) and controls.allow_remote_handoffs
    status = "applied" if transport_enabled else "blocked"
    entry = {
        "handoff_id": _identifier("handoff"),
        "recorded_at": _utc_now(),
        "from_actor_type": _clean_text(previous_supervisor.get("actor_type")) or "operator",
        "from_actor_name": _clean_text(previous_supervisor.get("actor_name")),
        "to_actor_type": _clean_text(to_actor_type) or "operator",
        "to_actor_name": _clean_text(to_actor_name),
        "reason": _clean_text(reason),
        "source_surface": source_surface,
        "source_command": source_command,
        "status": status,
        "summary": (
            f"Relaytic {'applied' if status == 'applied' else 'blocked'} remote supervision handoff to "
            f"`{_clean_text(to_actor_type) or 'operator'}`."
        ),
    }
    entries.append(entry)
    new_current = current_supervisor
    if status == "applied":
        new_current = {
            "actor_type": _clean_text(to_actor_type) or "operator",
            "actor_name": _clean_text(to_actor_name),
            "assigned_at": entry["recorded_at"],
            "source_surface": source_surface,
            "status": "active",
        }
        record_runtime_event(
            run_dir=root,
            policy=policy or {},
            event_type="remote_supervision_handoff",
            stage="remote_control",
            source_surface=source_surface,
            source_command=source_command,
            status="ok",
            summary=entry["summary"],
            metadata={"to_actor_type": new_current["actor_type"], "to_actor_name": new_current.get("actor_name")},
        )
    else:
        record_runtime_event(
            run_dir=root,
            policy=policy or {},
            event_type="remote_access_blocked",
            stage="remote_control",
            source_surface=source_surface,
            source_command=source_command,
            status="blocked",
            summary="Relaytic blocked the remote supervision handoff because remote supervision is disabled.",
            metadata={"to_actor_type": _clean_text(to_actor_type), "to_actor_name": _clean_text(to_actor_name)},
        )
    trace = _trace()
    write_remote_control_artifact(
        root,
        key="supervision_handoff",
        payload=SupervisionHandoffArtifact(
            schema_version=SUPERVISION_HANDOFF_SCHEMA_VERSION,
            generated_at=_utc_now(),
            controls=controls,
            status="ok" if controls.enabled else "disabled",
            current_supervisor=new_current,
            previous_supervisor=previous_supervisor,
            handoff_count=sum(1 for item in entries if _clean_text(item.get("status")) == "applied"),
            blocked_handoff_count=sum(1 for item in entries if _clean_text(item.get("status")) == "blocked"),
            last_handoff_at=_latest_handoff_time(entries),
            entries=entries[-12:],
            summary=entry["summary"],
            trace=trace,
        ).to_dict(),
    )
    write_remote_control_artifact(
        root,
        key="remote_operator_presence",
        payload=RemoteOperatorPresenceArtifact(
            schema_version=REMOTE_OPERATOR_PRESENCE_SCHEMA_VERSION,
            generated_at=_utc_now(),
            controls=controls,
            status="ok" if controls.enabled else "disabled",
            current_supervisor_type=_clean_text(new_current.get("actor_type")),
            current_supervisor_name=_clean_text(new_current.get("actor_name")),
            last_seen_at=entry["recorded_at"],
            freshness_status=_presence_freshness(
                last_seen_at=entry["recorded_at"],
                controls=controls,
                transport_enabled=_transport_enabled(controls),
            ),
            active_presence_count=1,
            presences=[
                {
                    "actor_type": _clean_text(new_current.get("actor_type")),
                    "actor_name": _clean_text(new_current.get("actor_name")),
                    "last_seen_at": entry["recorded_at"],
                    "source_surface": source_surface,
                    "status": "active" if status == "applied" else "blocked",
                }
            ],
            summary=entry["summary"],
            trace=trace,
        ).to_dict(),
    )
    review = run_remote_control_review(
        run_dir=root,
        policy=policy,
        actor_type=to_actor_type if status == "applied" else from_actor_type,
        actor_name=to_actor_name if status == "applied" else from_actor_name,
    )
    return RemoteDecisionResult(bundle=review.bundle, decision=entry, review_markdown=review.review_markdown)


def render_remote_control_markdown(bundle: RemoteControlBundle | dict[str, Any]) -> str:
    payload = bundle.to_dict() if isinstance(bundle, RemoteControlBundle) else dict(bundle)
    session = dict(payload.get("remote_session_manifest", {}))
    transport = dict(payload.get("remote_transport_report", {}))
    queue = dict(payload.get("approval_request_queue", {}))
    presence = dict(payload.get("remote_operator_presence", {}))
    handoff = dict(payload.get("supervision_handoff", {}))
    audit = dict(payload.get("remote_control_audit", {}))
    lines = [
        "# Relaytic Remote Supervision",
        "",
        f"- Status: `{session.get('status', 'unknown')}`",
        f"- Transport: `{transport.get('transport_kind', 'disabled')}`",
        f"- Transport enabled: `{transport.get('transport_enabled')}`",
        f"- Freshness: `{session.get('freshness_status', 'unknown')}`",
        f"- Pending approvals: `{queue.get('pending_approval_count', 0)}`",
        f"- Current supervisor: `{presence.get('current_supervisor_type') or 'operator'}`",
        f"- Next action: `{session.get('next_recommended_action') or 'unknown'}`",
        f"- Last remote action: `{audit.get('last_remote_action_kind') or 'none'}`",
    ]
    for item in list(queue.get("approvals", []))[:6]:
        lines.append(f"- Pending `{item.get('request_id')}` for `{item.get('action_id')}` from `{item.get('queue_source')}`")
    for item in list(handoff.get("entries", []))[-4:]:
        lines.append(
            f"- Handoff `{item.get('status')}`: `{item.get('from_actor_type')}` -> `{item.get('to_actor_type')}`"
        )
    return "\n".join(lines).rstrip() + "\n"


def _append_remote_decision_entry(
    *,
    root: Path,
    request_id: str,
    decision: str,
    actor_type: str,
    actor_name: str | None,
    source_surface: str,
    source_command: str,
    status: str,
    reason_code: str,
    summary: str,
) -> dict[str, Any]:
    entry = {
        "schema_version": APPROVAL_DECISION_LOG_SCHEMA_VERSION,
        "decision_id": _identifier("remote"),
        "recorded_at": _utc_now(),
        "request_id": request_id,
        "decision": decision,
        "actor_type": _clean_text(actor_type) or "operator",
        "actor_name": _clean_text(actor_name),
        "source_surface": source_surface,
        "source_command": source_command,
        "status": status,
        "reason_code": reason_code,
        "summary": summary,
    }
    append_approval_decision_log(root, entry=entry)
    return entry


def _merged_approval_queue(*, approval_policy: dict[str, Any], background_queue: dict[str, Any]) -> list[dict[str, Any]]:
    merged: dict[str, dict[str, Any]] = {}
    for item in approval_policy.get("pending_approvals", []):
        if not isinstance(item, dict):
            continue
        request_id = _clean_text(item.get("request_id"))
        if not request_id:
            continue
        merged[request_id] = {
            "request_id": request_id,
            "action_id": _clean_text(item.get("action_id")),
            "action_label": _clean_text(item.get("action_label")),
            "requested_at": _clean_text(item.get("requested_at")),
            "queue_source": "permissions",
            "summary": _clean_text(item.get("summary")),
        }
    for item in background_queue.get("approvals", []):
        if not isinstance(item, dict):
            continue
        request_id = _clean_text(item.get("request_id"))
        if not request_id:
            continue
        merged[request_id] = {
            "request_id": request_id,
            "action_id": _clean_text(item.get("approval_action_id")) or _clean_text(item.get("action_id")),
            "action_label": _clean_text(item.get("label")) or _clean_text(item.get("job_id")),
            "requested_at": _clean_text(item.get("requested_at")) or _clean_text(item.get("updated_at")),
            "queue_source": "daemon",
            "summary": _clean_text(item.get("summary")),
            "job_id": _clean_text(item.get("job_id")),
        }
    return sorted(
        merged.values(),
        key=lambda item: _parse_dt(item.get("requested_at")) or datetime.min.replace(tzinfo=timezone.utc),
    )


def _notification_items(
    *,
    approvals: list[dict[str, Any]],
    handoff_entries: list[dict[str, Any]],
    transport_enabled: bool,
    current_supervisor: dict[str, Any],
) -> list[dict[str, Any]]:
    notifications: list[dict[str, Any]] = []
    for item in approvals:
        notifications.append(
            {
                "notification_kind": "approval_pending",
                "recorded_at": _clean_text(item.get("requested_at")) or _utc_now(),
                "target_actor_type": _clean_text(current_supervisor.get("actor_type")) or "operator",
                "target_actor_name": _clean_text(current_supervisor.get("actor_name")),
                "delivered": transport_enabled,
                "delivery_mode": "remote_transport" if transport_enabled else "local_artifact_only",
                "summary": _clean_text(item.get("summary"))
                or f"Approval request `{item.get('request_id')}` is waiting.",
            }
        )
    if handoff_entries:
        last = handoff_entries[-1]
        notifications.append(
            {
                "notification_kind": "supervision_handoff",
                "recorded_at": _clean_text(last.get("recorded_at")) or _utc_now(),
                "target_actor_type": _clean_text(last.get("to_actor_type")) or "operator",
                "target_actor_name": _clean_text(last.get("to_actor_name")),
                "delivered": transport_enabled and _clean_text(last.get("status")) == "applied",
                "delivery_mode": "remote_transport" if transport_enabled else "local_artifact_only",
                "summary": _clean_text(last.get("summary")) or "Relaytic recorded a supervision handoff.",
            }
        )
    return notifications


def _build_remote_audit(
    *,
    controls: RemoteControlControls,
    trace: RemoteControlTrace,
    decision_log: list[dict[str, Any]],
    handoff_entries: list[dict[str, Any]],
    transport_enabled: bool,
) -> RemoteControlAuditArtifact:
    applied = [item for item in decision_log if _clean_text(item.get("status")) == "applied"]
    blocked = [item for item in decision_log if _clean_text(item.get("status")) == "blocked"]
    denied = [
        item
        for item in decision_log
        if _clean_text(item.get("decision")) == "deny" and _clean_text(item.get("status")) == "applied"
    ]
    blocked_handoffs = [item for item in handoff_entries if _clean_text(item.get("status")) == "blocked"]
    latest_candidates = [
        {
            "kind": "approval_decision",
            "recorded_at": _clean_text(item.get("recorded_at")),
            "actor_type": _clean_text(item.get("actor_type")),
            "actor_name": _clean_text(item.get("actor_name")),
        }
        for item in decision_log
    ] + [
        {
            "kind": "supervision_handoff",
            "recorded_at": _clean_text(item.get("recorded_at")),
            "actor_type": _clean_text(item.get("to_actor_type")) or _clean_text(item.get("from_actor_type")),
            "actor_name": _clean_text(item.get("to_actor_name")) or _clean_text(item.get("from_actor_name")),
        }
        for item in handoff_entries
    ]
    latest = max(
        latest_candidates,
        key=lambda item: _parse_dt(item.get("recorded_at")) or datetime.min.replace(tzinfo=timezone.utc),
        default={},
    )
    return RemoteControlAuditArtifact(
        schema_version=REMOTE_CONTROL_AUDIT_SCHEMA_VERSION,
        generated_at=_utc_now(),
        controls=controls,
        status="ok" if controls.enabled else "disabled",
        remote_enabled=controls.enabled,
        transport_enabled=transport_enabled,
        applied_decision_count=len(applied),
        denied_decision_count=len(denied),
        blocked_action_count=len(blocked) + len(blocked_handoffs),
        handoff_count=sum(1 for item in handoff_entries if _clean_text(item.get("status")) == "applied"),
        last_remote_action_kind=_clean_text(latest.get("kind")),
        last_remote_action_at=_clean_text(latest.get("recorded_at")),
        last_remote_actor_type=_clean_text(latest.get("actor_type")),
        last_remote_actor_name=_clean_text(latest.get("actor_name")),
        summary=(
            f"Relaytic recorded `{len(applied)}` applied remote decision(s), "
            f"`{len(blocked) + len(blocked_handoffs)}` blocked remote action(s), and "
            f"`{sum(1 for item in handoff_entries if _clean_text(item.get('status')) == 'applied')}` applied handoff(s)."
        ),
        trace=trace,
    )


def _same_presence(left: dict[str, Any], right: dict[str, Any]) -> bool:
    return (
        _clean_text(left.get("actor_type")) == _clean_text(right.get("actor_type"))
        and _clean_text(left.get("actor_name")) == _clean_text(right.get("actor_name"))
    )


def _latest_presence_time(presences: list[dict[str, Any]]) -> str | None:
    latest = max(
        presences,
        key=lambda item: _parse_dt(item.get("last_seen_at")) or datetime.min.replace(tzinfo=timezone.utc),
        default=None,
    )
    return _clean_text(dict(latest or {}).get("last_seen_at"))


def _latest_handoff_time(entries: list[dict[str, Any]]) -> str | None:
    latest = max(
        entries,
        key=lambda item: _parse_dt(item.get("recorded_at")) or datetime.min.replace(tzinfo=timezone.utc),
        default=None,
    )
    return _clean_text(dict(latest or {}).get("recorded_at"))


def _presence_freshness(*, last_seen_at: str | None, controls: RemoteControlControls, transport_enabled: bool) -> str:
    if not transport_enabled:
        return "disabled"
    seen_at = _parse_dt(last_seen_at)
    if seen_at is None:
        return "unknown"
    delta = datetime.now(timezone.utc) - seen_at
    return "fresh" if delta.total_seconds() <= controls.freshness_seconds else "stale"


def _transport_enabled(controls: RemoteControlControls) -> bool:
    return controls.enabled and controls.transport_kind not in {"", "disabled", "none"}


def _resolve_run_data_path(root: Path) -> str | None:
    summary = read_run_summary(root)
    if not isinstance(summary, dict):
        return None
    return _clean_text(dict(summary.get("data", {})).get("data_path"))


def _parse_dt(value: Any) -> datetime | None:
    text = _clean_text(value)
    if not text:
        return None
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed


def _trace() -> RemoteControlTrace:
    return RemoteControlTrace(
        agent="remote_supervision_controller",
        authority_model="permission_and_event_substrate",
        transport_model="explicit_remote_gate",
        advisory_notes=[
            "Remote supervision is a read-mostly projection over the same local artifacts used by CLI and MCP.",
            "Remote approvals and handoffs append to the same authority and runtime substrate rather than inventing remote-only state.",
        ],
    )


def _clean_text(value: Any) -> str | None:
    text = str(value or "").strip()
    return text or None


def _identifier(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex[:12]}"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()
