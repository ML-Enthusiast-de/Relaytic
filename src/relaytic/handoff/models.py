"""Typed artifact models for differentiated post-run handoff reporting."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


HANDOFF_CONTROLS_SCHEMA_VERSION = "relaytic.handoff_controls.v1"
RUN_HANDOFF_SCHEMA_VERSION = "relaytic.run_handoff.v1"
NEXT_RUN_OPTIONS_SCHEMA_VERSION = "relaytic.next_run_options.v1"
NEXT_RUN_FOCUS_SCHEMA_VERSION = "relaytic.next_run_focus.v1"


@dataclass(frozen=True)
class HandoffControls:
    """Resolved controls for differentiated end-of-run handoffs."""

    schema_version: str = HANDOFF_CONTROLS_SCHEMA_VERSION
    enabled: bool = True
    max_findings: int = 6
    max_risks: int = 5
    include_commands: bool = True
    include_agent_artifact_paths: bool = True

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class HandoffTrace:
    """Execution trace for handoff/report generation."""

    agent: str
    operating_mode: str
    llm_used: bool
    llm_status: str
    deterministic_evidence: list[str] = field(default_factory=list)
    advisory_notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class RunHandoffArtifact:
    """Canonical machine-readable handoff state for a run."""

    schema_version: str
    generated_at: str
    controls: HandoffControls
    status: str
    run_id: str
    current_stage: str
    headline: str
    user_summary: str
    agent_summary: str
    key_findings: list[dict[str, Any]]
    risks: list[dict[str, Any]]
    open_questions: list[str]
    recommended_option_id: str
    selected_focus_id: str | None
    report_paths: dict[str, str]
    summary: str
    trace: HandoffTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class NextRunOptionsArtifact:
    """Structured follow-up choices for the next run."""

    schema_version: str
    generated_at: str
    controls: HandoffControls
    status: str
    run_id: str
    recommended_option_id: str
    options: list[dict[str, Any]]
    summary: str
    trace: HandoffTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class NextRunFocusArtifact:
    """Persisted operator or agent selection for the next run focus."""

    schema_version: str
    generated_at: str
    controls: HandoffControls
    status: str
    run_id: str
    selection_id: str
    selection_label: str
    source: str
    actor_type: str
    actor_name: str | None
    notes: str | None
    reset_learnings_requested: bool
    summary: str
    trace: HandoffTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class HandoffBundle:
    """Full differentiated handoff bundle."""

    run_handoff: RunHandoffArtifact
    next_run_options: NextRunOptionsArtifact
    next_run_focus: NextRunFocusArtifact | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "run_handoff": self.run_handoff.to_dict(),
            "next_run_options": self.next_run_options.to_dict(),
            "next_run_focus": self.next_run_focus.to_dict() if self.next_run_focus is not None else None,
        }


def build_handoff_controls_from_policy(policy: dict[str, Any] | None) -> HandoffControls:
    """Resolve handoff controls from policy with safe defaults."""

    cfg = dict((policy or {}).get("handoff", {}))
    try:
        max_findings = int(cfg.get("max_findings", 6) or 6)
    except (TypeError, ValueError):
        max_findings = 6
    try:
        max_risks = int(cfg.get("max_risks", 5) or 5)
    except (TypeError, ValueError):
        max_risks = 5
    return HandoffControls(
        enabled=bool(cfg.get("enabled", True)),
        max_findings=max(3, min(10, max_findings)),
        max_risks=max(2, min(8, max_risks)),
        include_commands=bool(cfg.get("include_commands", True)),
        include_agent_artifact_paths=bool(cfg.get("include_agent_artifact_paths", True)),
    )
