"""Typed artifact models for Slice 12A lab pulse and bounded proactive follow-up."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


PULSE_CONTROLS_SCHEMA_VERSION = "relaytic.pulse_controls.v1"
PULSE_SCHEDULE_SCHEMA_VERSION = "relaytic.pulse_schedule.v1"
PULSE_RUN_REPORT_SCHEMA_VERSION = "relaytic.pulse_run_report.v1"
PULSE_SKIP_REPORT_SCHEMA_VERSION = "relaytic.pulse_skip_report.v1"
PULSE_RECOMMENDATIONS_SCHEMA_VERSION = "relaytic.pulse_recommendations.v1"
INNOVATION_WATCH_REPORT_SCHEMA_VERSION = "relaytic.innovation_watch_report.v1"
CHALLENGE_WATCHLIST_SCHEMA_VERSION = "relaytic.challenge_watchlist.v1"
PULSE_CHECKPOINT_SCHEMA_VERSION = "relaytic.pulse_checkpoint.v1"
MEMORY_COMPACTION_PLAN_SCHEMA_VERSION = "relaytic.memory_compaction_plan.v1"
MEMORY_COMPACTION_REPORT_SCHEMA_VERSION = "relaytic.memory_compaction_report.v1"
MEMORY_PINNING_INDEX_SCHEMA_VERSION = "relaytic.memory_pinning_index.v1"

PULSE_MODES = {"disabled", "observe_only", "propose_only", "bounded_execute"}


@dataclass(frozen=True)
class PulseControls:
    schema_version: str = PULSE_CONTROLS_SCHEMA_VERSION
    enabled: bool = True
    mode: str = "propose_only"
    schedule_minutes: int = 1440
    throttle_minutes: int = 60
    allow_innovation_watch: bool = True
    allow_memory_maintenance: bool = True
    allow_queue_refresh: bool = True
    max_watchlist_items: int = 4
    max_recommendations: int = 4
    max_bounded_actions: int = 1
    require_rowless_innovation: bool = True

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, payload: dict[str, Any] | None) -> "PulseControls":
        payload = dict(payload or {})
        mode = str(payload.get("mode", "propose_only") or "propose_only").strip().lower()
        if mode not in PULSE_MODES:
            mode = "propose_only"
        return cls(
            enabled=bool(payload.get("enabled", True)),
            mode=mode,
            schedule_minutes=max(5, int(payload.get("schedule_minutes", 1440) or 1440)),
            throttle_minutes=max(0, int(payload.get("throttle_minutes", 60) or 60)),
            allow_innovation_watch=bool(payload.get("allow_innovation_watch", True)),
            allow_memory_maintenance=bool(payload.get("allow_memory_maintenance", True)),
            allow_queue_refresh=bool(payload.get("allow_queue_refresh", True)),
            max_watchlist_items=max(1, int(payload.get("max_watchlist_items", 4) or 4)),
            max_recommendations=max(1, int(payload.get("max_recommendations", 4) or 4)),
            max_bounded_actions=max(1, int(payload.get("max_bounded_actions", 1) or 1)),
            require_rowless_innovation=bool(payload.get("require_rowless_innovation", True)),
        )


@dataclass(frozen=True)
class PulseTrace:
    agent: str
    operating_mode: str
    llm_used: bool
    llm_status: str
    deterministic_evidence: list[str] = field(default_factory=list)
    advisory_notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class PulseSchedule:
    schema_version: str
    generated_at: str
    controls: PulseControls
    status: str
    mode: str
    trigger_kind: str
    due_now: bool
    throttled: bool
    last_run_at: str | None
    last_result: str | None
    next_due_at: str | None
    schedule_minutes: int
    throttle_minutes: int
    summary: str
    trace: PulseTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class PulseRunReport:
    schema_version: str
    generated_at: str
    controls: PulseControls
    status: str
    mode: str
    trigger_kind: str
    executed_actions: list[dict[str, Any]]
    queued_actions: list[dict[str, Any]]
    recommendation_count: int
    watchlist_count: int
    innovation_lead_count: int
    memory_pinned_count: int
    summary: str
    trace: PulseTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class PulseSkipReport:
    schema_version: str
    generated_at: str
    controls: PulseControls
    status: str
    trigger_kind: str
    skip_reason: str | None
    due_now: bool
    next_due_at: str | None
    summary: str
    trace: PulseTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class PulseRecommendations:
    schema_version: str
    generated_at: str
    controls: PulseControls
    status: str
    mode: str
    recommendations: list[dict[str, Any]]
    queued_actions: list[dict[str, Any]]
    summary: str
    trace: PulseTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class InnovationWatchReport:
    schema_version: str
    generated_at: str
    controls: PulseControls
    status: str
    mode: str
    rowless_query: dict[str, Any]
    raw_rows_exported: bool
    identifier_leak_detected: bool
    leads: list[dict[str, Any]]
    summary: str
    trace: PulseTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class ChallengeWatchlist:
    schema_version: str
    generated_at: str
    controls: PulseControls
    status: str
    items: list[dict[str, Any]]
    summary: str
    trace: PulseTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class PulseCheckpoint:
    schema_version: str
    generated_at: str
    controls: PulseControls
    status: str
    checkpoint_id: str
    trigger_kind: str
    mode: str
    executed_action_count: int
    artifact_paths: list[str]
    summary: str
    trace: PulseTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class MemoryCompactionPlan:
    schema_version: str
    generated_at: str
    controls: PulseControls
    status: str
    plan_items: list[dict[str, Any]]
    pin_candidate_count: int
    summary: str
    trace: PulseTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class MemoryCompactionReport:
    schema_version: str
    generated_at: str
    controls: PulseControls
    status: str
    executed: bool
    compacted_category_count: int
    pinned_count: int
    retained_categories: list[str]
    summary: str
    trace: PulseTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class MemoryPinningIndex:
    schema_version: str
    generated_at: str
    controls: PulseControls
    status: str
    pin_count: int
    entries: list[dict[str, Any]]
    retrieval_hint: str
    summary: str
    trace: PulseTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class PulseBundle:
    pulse_schedule: PulseSchedule
    pulse_run_report: PulseRunReport
    pulse_skip_report: PulseSkipReport
    pulse_recommendations: PulseRecommendations
    innovation_watch_report: InnovationWatchReport
    challenge_watchlist: ChallengeWatchlist
    pulse_checkpoint: PulseCheckpoint
    memory_compaction_plan: MemoryCompactionPlan
    memory_compaction_report: MemoryCompactionReport
    memory_pinning_index: MemoryPinningIndex

    def to_dict(self) -> dict[str, Any]:
        return {
            "pulse_schedule": self.pulse_schedule.to_dict(),
            "pulse_run_report": self.pulse_run_report.to_dict(),
            "pulse_skip_report": self.pulse_skip_report.to_dict(),
            "pulse_recommendations": self.pulse_recommendations.to_dict(),
            "innovation_watch_report": self.innovation_watch_report.to_dict(),
            "challenge_watchlist": self.challenge_watchlist.to_dict(),
            "pulse_checkpoint": self.pulse_checkpoint.to_dict(),
            "memory_compaction_plan": self.memory_compaction_plan.to_dict(),
            "memory_compaction_report": self.memory_compaction_report.to_dict(),
            "memory_pinning_index": self.memory_pinning_index.to_dict(),
        }


def build_pulse_controls_from_policy(policy: dict[str, Any]) -> PulseControls:
    pulse_cfg = dict(policy.get("pulse", {}))
    return PulseControls.from_dict(pulse_cfg)
