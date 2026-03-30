"""Typed artifact models for durable cross-run learnings."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


LEARNING_CONTROLS_SCHEMA_VERSION = "relaytic.learning_controls.v1"
LEARNINGS_STATE_SCHEMA_VERSION = "relaytic.learnings_state.v1"
LAB_LEARNINGS_SNAPSHOT_SCHEMA_VERSION = "relaytic.lab_learnings_snapshot.v1"
LEARNINGS_RESET_SCHEMA_VERSION = "relaytic.learnings_reset.v1"


@dataclass(frozen=True)
class LearningControls:
    """Resolved controls for durable learnings persistence."""

    schema_version: str = LEARNING_CONTROLS_SCHEMA_VERSION
    enabled: bool = True
    max_entries: int = 120
    max_active_entries: int = 6
    track_assumptions: bool = True
    track_feedback: bool = True
    track_control_lessons: bool = True

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class LearningTrace:
    """Execution trace for learnings sync and reset."""

    agent: str
    operating_mode: str
    llm_used: bool
    llm_status: str
    deterministic_evidence: list[str] = field(default_factory=list)
    advisory_notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class LearningsStateArtifact:
    """Workspace-level durable learnings state."""

    schema_version: str
    generated_at: str
    controls: LearningControls
    status: str
    state_dir: str
    entry_count: int
    entries: list[dict[str, Any]]
    summary: str
    trace: LearningTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class LabLearningsSnapshotArtifact:
    """Run-local snapshot of active and harvested learnings."""

    schema_version: str
    generated_at: str
    controls: LearningControls
    status: str
    run_id: str
    state_dir: str
    learnings_state_path: str
    learnings_md_path: str
    state_entry_count: int
    harvested_count: int
    active_count: int
    harvested_learnings: list[dict[str, Any]]
    active_learnings: list[dict[str, Any]]
    summary: str
    trace: LearningTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class LearningsResetArtifact:
    """Summary for an explicit learnings reset."""

    schema_version: str
    generated_at: str
    controls: LearningControls
    status: str
    state_dir: str
    removed_entry_count: int
    summary: str
    trace: LearningTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


def build_learning_controls_from_policy(policy: dict[str, Any] | None) -> LearningControls:
    """Resolve learnings controls from policy with safe defaults."""

    cfg = dict((policy or {}).get("learnings", {}))
    try:
        max_entries = int(cfg.get("max_entries", 120) or 120)
    except (TypeError, ValueError):
        max_entries = 120
    try:
        max_active = int(cfg.get("max_active_entries", 6) or 6)
    except (TypeError, ValueError):
        max_active = 6
    return LearningControls(
        enabled=bool(cfg.get("enabled", True)),
        max_entries=max(20, min(300, max_entries)),
        max_active_entries=max(3, min(12, max_active)),
        track_assumptions=bool(cfg.get("track_assumptions", True)),
        track_feedback=bool(cfg.get("track_feedback", True)),
        track_control_lessons=bool(cfg.get("track_control_lessons", True)),
    )
