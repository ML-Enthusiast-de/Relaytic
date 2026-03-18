"""Typed artifact models for Slice 07 completion-governor outputs."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


COMPLETION_CONTROLS_SCHEMA_VERSION = "relaytic.completion_controls.v1"
COMPLETION_DECISION_SCHEMA_VERSION = "relaytic.completion_decision.v1"
RUN_STATE_SCHEMA_VERSION = "relaytic.run_state.v1"
STAGE_TIMELINE_SCHEMA_VERSION = "relaytic.stage_timeline.v1"
MANDATE_EVIDENCE_REVIEW_SCHEMA_VERSION = "relaytic.mandate_evidence_review.v1"
BLOCKING_ANALYSIS_SCHEMA_VERSION = "relaytic.blocking_analysis.v1"
NEXT_ACTION_QUEUE_SCHEMA_VERSION = "relaytic.next_action_queue.v1"

COMPLETION_ACTIONS = {
    "stop_for_now",
    "continue_experimentation",
    "review_challenger",
    "collect_more_data",
    "benchmark_needed",
    "memory_support_needed",
    "recalibration_candidate",
    "retrain_candidate",
}


@dataclass(frozen=True)
class CompletionControls:
    """Resolved controls for Slice 07 completion judgment."""

    schema_version: str = COMPLETION_CONTROLS_SCHEMA_VERSION
    enabled: bool = True
    stage_visibility_enabled: bool = True
    intelligence_mode: str = "none"
    prefer_local_llm: bool = True
    allow_local_llm_advisory: bool = False
    require_deterministic_floor: bool = True

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class CompletionTrace:
    """Execution trace for one completion specialist."""

    agent: str
    operating_mode: str
    llm_used: bool
    llm_status: str
    deterministic_evidence: list[str] = field(default_factory=list)
    advisory_notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class CompletionDecision:
    """Machine-actionable completion decision for the current run."""

    schema_version: str
    generated_at: str
    controls: CompletionControls
    action: str
    confidence: str
    current_stage: str
    blocking_layer: str
    mandate_alignment: str
    evidence_state: str
    complete_for_mode: bool
    reason_codes: list[str]
    summary: str
    llm_advisory: dict[str, Any] | None
    trace: CompletionTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class RunState:
    """Visible workflow state for humans and external agents."""

    schema_version: str
    generated_at: str
    controls: CompletionControls
    current_stage: str
    previous_stage: str | None
    state: str
    executed_stages: list[str]
    artifact_presence: dict[str, bool]
    summary: str
    trace: CompletionTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class StageTimeline:
    """Recorded timeline of the current run stages."""

    schema_version: str
    generated_at: str
    controls: CompletionControls
    stages: list[dict[str, Any]]
    summary: str
    trace: CompletionTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class MandateEvidenceReview:
    """Alignment review between operator intent and current evidence."""

    schema_version: str
    generated_at: str
    controls: CompletionControls
    alignment: str
    target_alignment: str
    objective_alignment: str
    binding_checks: list[dict[str, Any]]
    caveats: list[str]
    summary: str
    trace: CompletionTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class BlockingAnalysis:
    """Primary blocking-layer diagnosis for the current run."""

    schema_version: str
    generated_at: str
    controls: CompletionControls
    blocking_layer: str
    diagnoses: list[dict[str, Any]]
    summary: str
    trace: CompletionTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class NextActionQueue:
    """Ordered queue of next actions for humans and agents."""

    schema_version: str
    generated_at: str
    controls: CompletionControls
    actions: list[dict[str, Any]]
    summary: str
    trace: CompletionTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class CompletionBundle:
    """Full Slice 07 completion bundle."""

    completion_decision: CompletionDecision
    run_state: RunState
    stage_timeline: StageTimeline
    mandate_evidence_review: MandateEvidenceReview
    blocking_analysis: BlockingAnalysis
    next_action_queue: NextActionQueue

    def to_dict(self) -> dict[str, Any]:
        return {
            "completion_decision": self.completion_decision.to_dict(),
            "run_state": self.run_state.to_dict(),
            "stage_timeline": self.stage_timeline.to_dict(),
            "mandate_evidence_review": self.mandate_evidence_review.to_dict(),
            "blocking_analysis": self.blocking_analysis.to_dict(),
            "next_action_queue": self.next_action_queue.to_dict(),
        }


def build_completion_controls_from_policy(policy: dict[str, Any]) -> CompletionControls:
    """Derive completion controls from the canonical policy payload."""
    intelligence_cfg = dict(policy.get("intelligence", {}))
    lifecycle_cfg = dict(policy.get("lifecycle", {}))
    intelligence_mode = str(intelligence_cfg.get("intelligence_mode", "none")).strip() or "none"
    normalized_mode = intelligence_mode.lower().replace("-", "_")
    advisory_enabled = normalized_mode not in {"", "none", "off", "disabled", "deterministic"}
    enabled = bool(lifecycle_cfg.get("completion_judge_enabled", True))
    stage_visibility = bool(lifecycle_cfg.get("stage_visibility_enabled", True))
    return CompletionControls(
        enabled=enabled,
        stage_visibility_enabled=stage_visibility,
        intelligence_mode=intelligence_mode,
        prefer_local_llm=bool(intelligence_cfg.get("prefer_local_llm", True)),
        allow_local_llm_advisory=bool(intelligence_cfg.get("enabled", True)) and advisory_enabled,
        require_deterministic_floor=True,
    )
