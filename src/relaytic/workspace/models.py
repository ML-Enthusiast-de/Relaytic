"""Typed artifact models for Slice 12D workspace continuity and result contracts."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


WORKSPACE_CONTROLS_SCHEMA_VERSION = "relaytic.workspace_controls.v1"
WORKSPACE_STATE_SCHEMA_VERSION = "relaytic.workspace_state.v1"
WORKSPACE_LINEAGE_SCHEMA_VERSION = "relaytic.workspace_lineage.v1"
WORKSPACE_FOCUS_HISTORY_SCHEMA_VERSION = "relaytic.workspace_focus_history.v1"
WORKSPACE_MEMORY_POLICY_SCHEMA_VERSION = "relaytic.workspace_memory_policy.v1"
RESULT_CONTRACT_SCHEMA_VERSION = "relaytic.result_contract.v1"
CONFIDENCE_POSTURE_SCHEMA_VERSION = "relaytic.confidence_posture.v1"
BELIEF_REVISION_TRIGGERS_SCHEMA_VERSION = "relaytic.belief_revision_triggers.v1"


@dataclass(frozen=True)
class WorkspaceControls:
    schema_version: str = WORKSPACE_CONTROLS_SCHEMA_VERSION
    enabled: bool = True
    max_lineage_runs: int = 40
    max_focus_events: int = 60
    keep_history_on_reset: bool = True

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class WorkspaceTrace:
    agent: str
    operating_mode: str
    llm_used: bool
    llm_status: str
    deterministic_evidence: list[str] = field(default_factory=list)
    advisory_notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class WorkspaceStateArtifact:
    schema_version: str
    generated_at: str
    controls: WorkspaceControls
    status: str
    workspace_id: str
    workspace_label: str
    workspace_dir: str
    current_run_id: str
    current_focus: str | None
    continuity_mode: str
    prior_run_count: int
    next_run_plan_path: str | None
    result_contract_path: str | None
    learnings_state_path: str | None
    summary: str
    trace: WorkspaceTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class WorkspaceLineageArtifact:
    schema_version: str
    generated_at: str
    controls: WorkspaceControls
    status: str
    workspace_id: str
    current_run_id: str
    run_count: int
    runs: list[dict[str, Any]]
    summary: str
    trace: WorkspaceTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class WorkspaceFocusHistoryArtifact:
    schema_version: str
    generated_at: str
    controls: WorkspaceControls
    status: str
    workspace_id: str
    current_focus: str | None
    event_count: int
    events: list[dict[str, Any]]
    summary: str
    trace: WorkspaceTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class WorkspaceMemoryPolicyArtifact:
    schema_version: str
    generated_at: str
    controls: WorkspaceControls
    status: str
    workspace_id: str
    preferred_focus: str | None
    active_learning_count: int
    tentative_learning_count: int
    invalidated_learning_count: int
    expired_learning_count: int
    reset_scopes: list[str]
    summary: str
    trace: WorkspaceTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class ResultContractArtifact:
    schema_version: str
    run_id: str
    workspace_id: str
    generated_at: str
    status: str
    objective_summary: dict[str, Any]
    current_beliefs: list[dict[str, Any]]
    evidence_strength: dict[str, Any]
    unresolved_items: list[dict[str, Any]]
    recommended_next_move: dict[str, Any]
    why_this_move: list[dict[str, Any]]
    why_not_other_moves: dict[str, Any]
    confidence_posture_ref: str
    belief_revision_triggers_ref: str
    source_artifacts: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ConfidencePostureArtifact:
    schema_version: str
    run_id: str
    workspace_id: str
    generated_at: str
    overall_confidence: str
    known_fragility: list[str]
    abstention_readiness: str
    review_need: str
    confidence_explanation: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class BeliefRevisionTriggersArtifact:
    schema_version: str
    run_id: str
    workspace_id: str
    generated_at: str
    triggers: list[dict[str, Any]]
    summary: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def build_workspace_controls_from_policy(policy: dict[str, Any] | None) -> WorkspaceControls:
    """Resolve workspace controls from policy with safe defaults."""

    cfg = dict((policy or {}).get("workspace", {}))
    try:
        max_lineage_runs = int(cfg.get("max_lineage_runs", 40) or 40)
    except (TypeError, ValueError):
        max_lineage_runs = 40
    try:
        max_focus_events = int(cfg.get("max_focus_events", 60) or 60)
    except (TypeError, ValueError):
        max_focus_events = 60
    return WorkspaceControls(
        enabled=bool(cfg.get("enabled", True)),
        max_lineage_runs=max(5, min(200, max_lineage_runs)),
        max_focus_events=max(5, min(200, max_focus_events)),
        keep_history_on_reset=bool(cfg.get("keep_history_on_reset", True)),
    )
