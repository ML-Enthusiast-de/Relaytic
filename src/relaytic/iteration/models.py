"""Typed artifact models for Slice 12D next-run iteration planning."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


ITERATION_CONTROLS_SCHEMA_VERSION = "relaytic.iteration_controls.v1"
NEXT_RUN_PLAN_SCHEMA_VERSION = "relaytic.next_run_plan.v1"
FOCUS_DECISION_RECORD_SCHEMA_VERSION = "relaytic.focus_decision_record.v1"
DATA_EXPANSION_CANDIDATES_SCHEMA_VERSION = "relaytic.data_expansion_candidates.v1"


@dataclass(frozen=True)
class IterationControls:
    schema_version: str = ITERATION_CONTROLS_SCHEMA_VERSION
    enabled: bool = True
    max_data_expansion_candidates: int = 5

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class IterationTrace:
    agent: str
    operating_mode: str
    llm_used: bool
    llm_status: str
    deterministic_evidence: list[str] = field(default_factory=list)
    advisory_notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class NextRunPlanArtifact:
    schema_version: str
    generated_at: str
    controls: IterationControls
    status: str
    workspace_id: str
    run_id: str
    recommended_direction: str
    primary_reason: str
    secondary_actions: list[str]
    confidence: str
    why_not_the_other_paths: dict[str, Any]
    required_user_inputs: list[str]
    belief_revision_dependency: str | None
    summary: str
    trace: IterationTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class FocusDecisionRecordArtifact:
    schema_version: str
    generated_at: str
    controls: IterationControls
    status: str
    workspace_id: str
    run_id: str
    selected_direction: str
    source: str
    actor_type: str
    actor_name: str | None
    notes: str | None
    reset_learnings_requested: bool
    summary: str
    trace: IterationTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class DataExpansionCandidatesArtifact:
    schema_version: str
    generated_at: str
    controls: IterationControls
    status: str
    workspace_id: str
    run_id: str
    candidate_count: int
    candidates: list[dict[str, Any]]
    summary: str
    trace: IterationTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


def build_iteration_controls_from_policy(policy: dict[str, Any] | None) -> IterationControls:
    """Resolve iteration controls from policy with safe defaults."""

    cfg = dict((policy or {}).get("iteration", {}))
    try:
        max_candidates = int(cfg.get("max_data_expansion_candidates", 5) or 5)
    except (TypeError, ValueError):
        max_candidates = 5
    return IterationControls(
        enabled=bool(cfg.get("enabled", True)),
        max_data_expansion_candidates=max(1, min(20, max_candidates)),
    )
