"""Typed artifact models for Slice 13C bounded background execution."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


DAEMON_CONTROLS_SCHEMA_VERSION = "relaytic.daemon_controls.v1"
DAEMON_STATE_SCHEMA_VERSION = "relaytic.daemon_state.v1"
BACKGROUND_JOB_REGISTRY_SCHEMA_VERSION = "relaytic.background_job_registry.v1"
BACKGROUND_CHECKPOINT_SCHEMA_VERSION = "relaytic.background_checkpoint.v1"
RESUME_SESSION_MANIFEST_SCHEMA_VERSION = "relaytic.resume_session_manifest.v1"
BACKGROUND_APPROVAL_QUEUE_SCHEMA_VERSION = "relaytic.background_approval_queue.v1"
MEMORY_MAINTENANCE_QUEUE_SCHEMA_VERSION = "relaytic.memory_maintenance_queue.v1"
MEMORY_MAINTENANCE_REPORT_SCHEMA_VERSION = "relaytic.memory_maintenance_report.v1"
SEARCH_RESUME_PLAN_SCHEMA_VERSION = "relaytic.search_resume_plan.v1"
STALE_JOB_REPORT_SCHEMA_VERSION = "relaytic.stale_job_report.v1"
BACKGROUND_JOB_LOG_SCHEMA_VERSION = "relaytic.background_job_event.v1"


@dataclass(frozen=True)
class DaemonControls:
    schema_version: str = DAEMON_CONTROLS_SCHEMA_VERSION
    enabled: bool = True
    allow_background_execution: bool = True
    allow_search_campaigns: bool = True
    allow_memory_maintenance: bool = True
    allow_pulse_followup: bool = True
    allow_benchmark_campaigns: bool = False
    stale_after_minutes: int = 180
    max_recent_job_events: int = 60
    checkpoint_resume_enabled: bool = True
    require_approval_for_search_campaigns: bool = True
    require_approval_for_benchmark_campaigns: bool = True

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class DaemonTrace:
    agent: str
    execution_model: str
    authority_model: str
    advisory_notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class DaemonStateArtifact:
    schema_version: str
    generated_at: str
    controls: DaemonControls
    status: str
    workspace_id: str | None
    run_id: str
    background_execution_enabled: bool
    job_count: int
    active_job_count: int
    queued_job_count: int
    paused_job_count: int
    pending_approval_count: int
    stale_job_count: int
    summary: str
    trace: DaemonTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class BackgroundJobRegistryArtifact:
    schema_version: str
    generated_at: str
    controls: DaemonControls
    status: str
    workspace_id: str | None
    run_id: str
    job_count: int
    jobs: list[dict[str, Any]]
    summary: str
    trace: DaemonTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class BackgroundCheckpointArtifact:
    schema_version: str
    generated_at: str
    controls: DaemonControls
    status: str
    checkpoint_count: int
    resume_ready_count: int
    checkpoints: list[dict[str, Any]]
    summary: str
    trace: DaemonTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class ResumeSessionManifestArtifact:
    schema_version: str
    generated_at: str
    controls: DaemonControls
    status: str
    workspace_id: str | None
    run_id: str
    result_contract_status: str | None
    resumable_job_count: int
    pending_approval_count: int
    resumable_jobs: list[dict[str, Any]]
    summary: str
    trace: DaemonTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class BackgroundApprovalQueueArtifact:
    schema_version: str
    generated_at: str
    controls: DaemonControls
    status: str
    pending_approval_count: int
    approvals: list[dict[str, Any]]
    summary: str
    trace: DaemonTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class MemoryMaintenanceQueueArtifact:
    schema_version: str
    generated_at: str
    controls: DaemonControls
    status: str
    queued_task_count: int
    queued_tasks: list[dict[str, Any]]
    summary: str
    trace: DaemonTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class MemoryMaintenanceReportArtifact:
    schema_version: str
    generated_at: str
    controls: DaemonControls
    status: str
    executed: bool
    executed_task_count: int
    before_task_count: int
    after_task_count: int
    before_pin_candidate_count: int
    after_pin_candidate_count: int
    retained_categories: list[str]
    summary: str
    trace: DaemonTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class SearchResumePlanArtifact:
    schema_version: str
    generated_at: str
    controls: DaemonControls
    status: str
    job_id: str | None
    resume_ready: bool
    latest_checkpoint_id: str | None
    planned_trial_count: int
    next_step: str | None
    summary: str
    trace: DaemonTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class StaleJobReportArtifact:
    schema_version: str
    generated_at: str
    controls: DaemonControls
    status: str
    stale_job_count: int
    stale_jobs: list[dict[str, Any]]
    summary: str
    trace: DaemonTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class DaemonBundle:
    daemon_state: DaemonStateArtifact
    background_job_registry: BackgroundJobRegistryArtifact
    background_checkpoint: BackgroundCheckpointArtifact
    resume_session_manifest: ResumeSessionManifestArtifact
    background_approval_queue: BackgroundApprovalQueueArtifact
    memory_maintenance_queue: MemoryMaintenanceQueueArtifact
    memory_maintenance_report: MemoryMaintenanceReportArtifact
    search_resume_plan: SearchResumePlanArtifact
    stale_job_report: StaleJobReportArtifact

    def to_dict(self) -> dict[str, Any]:
        return {
            "daemon_state": self.daemon_state.to_dict(),
            "background_job_registry": self.background_job_registry.to_dict(),
            "background_checkpoint": self.background_checkpoint.to_dict(),
            "resume_session_manifest": self.resume_session_manifest.to_dict(),
            "background_approval_queue": self.background_approval_queue.to_dict(),
            "memory_maintenance_queue": self.memory_maintenance_queue.to_dict(),
            "memory_maintenance_report": self.memory_maintenance_report.to_dict(),
            "search_resume_plan": self.search_resume_plan.to_dict(),
            "stale_job_report": self.stale_job_report.to_dict(),
        }


def build_daemon_controls_from_policy(policy: dict[str, Any] | None) -> DaemonControls:
    payload = dict(policy or {})
    cfg = dict(payload.get("daemon", {}))
    return DaemonControls(
        enabled=bool(cfg.get("enabled", True)),
        allow_background_execution=bool(cfg.get("allow_background_execution", True)),
        allow_search_campaigns=bool(cfg.get("allow_search_campaigns", True)),
        allow_memory_maintenance=bool(cfg.get("allow_memory_maintenance", True)),
        allow_pulse_followup=bool(cfg.get("allow_pulse_followup", True)),
        allow_benchmark_campaigns=bool(cfg.get("allow_benchmark_campaigns", False)),
        stale_after_minutes=max(5, int(cfg.get("stale_after_minutes", 180) or 180)),
        max_recent_job_events=max(10, int(cfg.get("max_recent_job_events", 60) or 60)),
        checkpoint_resume_enabled=bool(cfg.get("checkpoint_resume_enabled", True)),
        require_approval_for_search_campaigns=bool(cfg.get("require_approval_for_search_campaigns", True)),
        require_approval_for_benchmark_campaigns=bool(cfg.get("require_approval_for_benchmark_campaigns", True)),
    )
