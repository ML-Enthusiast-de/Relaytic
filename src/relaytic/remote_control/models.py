"""Typed artifact models for Slice 14A remote supervision."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


REMOTE_CONTROL_CONTROLS_SCHEMA_VERSION = "relaytic.remote_control_controls.v1"
REMOTE_SESSION_MANIFEST_SCHEMA_VERSION = "relaytic.remote_session_manifest.v1"
REMOTE_TRANSPORT_REPORT_SCHEMA_VERSION = "relaytic.remote_transport_report.v1"
APPROVAL_REQUEST_QUEUE_SCHEMA_VERSION = "relaytic.approval_request_queue.v1"
APPROVAL_DECISION_LOG_SCHEMA_VERSION = "relaytic.approval_decision_log.v1"
REMOTE_OPERATOR_PRESENCE_SCHEMA_VERSION = "relaytic.remote_operator_presence.v1"
SUPERVISION_HANDOFF_SCHEMA_VERSION = "relaytic.supervision_handoff.v1"
NOTIFICATION_DELIVERY_REPORT_SCHEMA_VERSION = "relaytic.notification_delivery_report.v1"
REMOTE_CONTROL_AUDIT_SCHEMA_VERSION = "relaytic.remote_control_audit.v1"


@dataclass(frozen=True)
class RemoteControlControls:
    schema_version: str = REMOTE_CONTROL_CONTROLS_SCHEMA_VERSION
    enabled: bool = False
    transport_kind: str = "disabled"
    transport_scope: str = "local_only"
    remote_url: str | None = None
    freshness_seconds: int = 120
    allow_remote_approval_decisions: bool = True
    allow_remote_handoffs: bool = True
    read_mostly: bool = True
    max_recent_decisions: int = 40

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class RemoteControlTrace:
    agent: str
    authority_model: str
    transport_model: str
    advisory_notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class RemoteSessionManifestArtifact:
    schema_version: str
    generated_at: str
    controls: RemoteControlControls
    status: str
    run_id: str
    workspace_id: str | None
    current_stage: str | None
    permission_mode: str | None
    transport_enabled: bool
    transport_kind: str
    freshness_status: str
    pending_approval_count: int
    active_job_count: int
    next_recommended_action: str | None
    result_contract_status: str | None
    current_supervisor_type: str | None
    current_supervisor_name: str | None
    write_actions_allowed: bool
    summary: str
    trace: RemoteControlTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class RemoteTransportReportArtifact:
    schema_version: str
    generated_at: str
    controls: RemoteControlControls
    status: str
    transport_enabled: bool
    transport_kind: str
    transport_scope: str
    remote_url: str | None
    freshness_seconds: int
    read_mostly: bool
    write_actions_allowed: bool
    summary: str
    trace: RemoteControlTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class ApprovalRequestQueueArtifact:
    schema_version: str
    generated_at: str
    controls: RemoteControlControls
    status: str
    pending_approval_count: int
    approval_source_count: int
    approvals: list[dict[str, Any]]
    summary: str
    trace: RemoteControlTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class RemoteOperatorPresenceArtifact:
    schema_version: str
    generated_at: str
    controls: RemoteControlControls
    status: str
    current_supervisor_type: str | None
    current_supervisor_name: str | None
    last_seen_at: str | None
    freshness_status: str
    active_presence_count: int
    presences: list[dict[str, Any]]
    summary: str
    trace: RemoteControlTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class SupervisionHandoffArtifact:
    schema_version: str
    generated_at: str
    controls: RemoteControlControls
    status: str
    current_supervisor: dict[str, Any]
    previous_supervisor: dict[str, Any] | None
    handoff_count: int
    blocked_handoff_count: int
    last_handoff_at: str | None
    entries: list[dict[str, Any]]
    summary: str
    trace: RemoteControlTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class NotificationDeliveryReportArtifact:
    schema_version: str
    generated_at: str
    controls: RemoteControlControls
    status: str
    notification_count: int
    undelivered_count: int
    notifications: list[dict[str, Any]]
    summary: str
    trace: RemoteControlTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class RemoteControlAuditArtifact:
    schema_version: str
    generated_at: str
    controls: RemoteControlControls
    status: str
    remote_enabled: bool
    transport_enabled: bool
    applied_decision_count: int
    denied_decision_count: int
    blocked_action_count: int
    handoff_count: int
    last_remote_action_kind: str | None
    last_remote_action_at: str | None
    last_remote_actor_type: str | None
    last_remote_actor_name: str | None
    summary: str
    trace: RemoteControlTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class RemoteControlBundle:
    remote_session_manifest: RemoteSessionManifestArtifact
    remote_transport_report: RemoteTransportReportArtifact
    approval_request_queue: ApprovalRequestQueueArtifact
    remote_operator_presence: RemoteOperatorPresenceArtifact
    supervision_handoff: SupervisionHandoffArtifact
    notification_delivery_report: NotificationDeliveryReportArtifact
    remote_control_audit: RemoteControlAuditArtifact

    def to_dict(self) -> dict[str, Any]:
        return {
            "remote_session_manifest": self.remote_session_manifest.to_dict(),
            "remote_transport_report": self.remote_transport_report.to_dict(),
            "approval_request_queue": self.approval_request_queue.to_dict(),
            "remote_operator_presence": self.remote_operator_presence.to_dict(),
            "supervision_handoff": self.supervision_handoff.to_dict(),
            "notification_delivery_report": self.notification_delivery_report.to_dict(),
            "remote_control_audit": self.remote_control_audit.to_dict(),
        }


def build_remote_control_controls_from_policy(policy: dict[str, Any] | None) -> RemoteControlControls:
    payload = dict(policy or {})
    cfg = dict(payload.get("remote_control", {}))
    freshness_seconds = max(15, int(cfg.get("freshness_seconds", 120) or 120))
    max_recent_decisions = max(10, int(cfg.get("max_recent_decisions", 40) or 40))
    enabled = bool(cfg.get("enabled", False))
    transport_kind = str(cfg.get("transport_kind", "filesystem_sync") or "filesystem_sync").strip().lower()
    if not enabled:
        transport_kind = "disabled"
    return RemoteControlControls(
        enabled=enabled,
        transport_kind=transport_kind,
        transport_scope=str(cfg.get("transport_scope", "local_only") or "local_only").strip().lower(),
        remote_url=str(cfg.get("remote_url", "")).strip() or None,
        freshness_seconds=freshness_seconds,
        allow_remote_approval_decisions=bool(cfg.get("allow_remote_approval_decisions", True)),
        allow_remote_handoffs=bool(cfg.get("allow_remote_handoffs", True)),
        read_mostly=bool(cfg.get("read_mostly", True)),
        max_recent_decisions=max_recent_decisions,
    )
