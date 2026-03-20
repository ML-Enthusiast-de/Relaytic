"""Typed artifact models for Slice 09A memory outputs."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


MEMORY_CONTROLS_SCHEMA_VERSION = "relaytic.memory_controls.v1"
MEMORY_RETRIEVAL_SCHEMA_VERSION = "relaytic.memory_retrieval.v1"
ANALOG_RUN_CANDIDATES_SCHEMA_VERSION = "relaytic.analog_run_candidates.v1"
ROUTE_PRIOR_CONTEXT_SCHEMA_VERSION = "relaytic.route_prior_context.v1"
CHALLENGER_PRIOR_SUGGESTIONS_SCHEMA_VERSION = "relaytic.challenger_prior_suggestions.v1"
REFLECTION_MEMORY_SCHEMA_VERSION = "relaytic.reflection_memory.v1"
MEMORY_FLUSH_REPORT_SCHEMA_VERSION = "relaytic.memory_flush_report.v1"


@dataclass(frozen=True)
class MemoryControls:
    """Resolved controls for Slice 09A run memory."""

    schema_version: str = MEMORY_CONTROLS_SCHEMA_VERSION
    enabled: bool = True
    allow_prior_retrieval: bool = True
    feedback_learning_enabled: bool = False
    require_provenance: bool = True
    max_analog_runs: int = 5
    min_similarity_score: float = 0.45
    prefer_summary_level_signals: bool = True

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class MemoryTrace:
    """Execution trace for one memory specialist."""

    agent: str
    operating_mode: str
    llm_used: bool
    llm_status: str
    deterministic_evidence: list[str] = field(default_factory=list)
    advisory_notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class MemoryRetrieval:
    """High-level retrieval report for the current run."""

    schema_version: str
    generated_at: str
    controls: MemoryControls
    status: str
    current_run_id: str
    current_stage: str
    search_roots: list[str]
    candidate_count: int
    selected_analog_count: int
    top_similarity_score: float | None
    query_signature: dict[str, Any]
    analog_run_ids: list[str]
    counterfactual: dict[str, Any]
    summary: str
    trace: MemoryTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class AnalogRunCandidates:
    """Ranked analog candidates with provenance and rationale."""

    schema_version: str
    generated_at: str
    controls: MemoryControls
    current_run_id: str
    candidates: list[dict[str, Any]]
    summary: str
    trace: MemoryTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class RoutePriorContext:
    """Planning-facing priors derived from prior analog runs."""

    schema_version: str
    generated_at: str
    controls: MemoryControls
    status: str
    selected_route_id: str | None
    baseline_candidate_order: list[str]
    adjusted_candidate_order: list[str]
    family_bias: list[dict[str, Any]]
    influencing_analogs: list[str]
    counterfactual: dict[str, Any]
    summary: str
    trace: MemoryTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class ChallengerPriorSuggestions:
    """Evidence-facing challenger priors derived from prior analog runs."""

    schema_version: str
    generated_at: str
    controls: MemoryControls
    status: str
    preferred_challenger_family: str | None
    ranked_families: list[dict[str, Any]]
    influencing_analogs: list[str]
    counterfactual: dict[str, Any]
    summary: str
    trace: MemoryTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class ReflectionMemory:
    """Durable reflection summary written back for the current run."""

    schema_version: str
    generated_at: str
    controls: MemoryControls
    current_run_id: str
    current_stage: str
    analog_count: int
    lessons: list[str]
    reusable_priors: list[str]
    failure_modes: list[str]
    memory_delta: list[str]
    summary: str
    trace: MemoryTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class MemoryFlushReport:
    """Report describing the current memory flush and persisted outputs."""

    schema_version: str
    generated_at: str
    controls: MemoryControls
    flush_stage: str
    flushed: bool
    retrieval_status: str
    analog_count: int
    reflection_stage: str
    written_artifacts: list[str]
    summary: str
    trace: MemoryTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class MemoryBundle:
    """Full Slice 09A memory bundle."""

    memory_retrieval: MemoryRetrieval
    analog_run_candidates: AnalogRunCandidates
    route_prior_context: RoutePriorContext
    challenger_prior_suggestions: ChallengerPriorSuggestions
    reflection_memory: ReflectionMemory
    memory_flush_report: MemoryFlushReport

    def to_dict(self) -> dict[str, Any]:
        return {
            "memory_retrieval": self.memory_retrieval.to_dict(),
            "analog_run_candidates": self.analog_run_candidates.to_dict(),
            "route_prior_context": self.route_prior_context.to_dict(),
            "challenger_prior_suggestions": self.challenger_prior_suggestions.to_dict(),
            "reflection_memory": self.reflection_memory.to_dict(),
            "memory_flush_report": self.memory_flush_report.to_dict(),
        }


def build_memory_controls_from_policy(policy: dict[str, Any]) -> MemoryControls:
    """Derive memory controls from the canonical policy payload."""
    memory_cfg = dict(policy.get("memory", {}))
    compute_cfg = dict(policy.get("compute", {}))
    try:
        max_trials = int(compute_cfg.get("max_parallel_trials", 4) or 4)
    except (TypeError, ValueError):
        max_trials = 4
    try:
        max_analog_runs = int(memory_cfg.get("max_analog_runs", max(4, max_trials)) or max(4, max_trials))
    except (TypeError, ValueError):
        max_analog_runs = max(4, max_trials)
    try:
        min_similarity_score = float(memory_cfg.get("min_similarity_score", 0.45) or 0.45)
    except (TypeError, ValueError):
        min_similarity_score = 0.45
    return MemoryControls(
        enabled=bool(memory_cfg.get("enable_run_memory", True)),
        allow_prior_retrieval=bool(memory_cfg.get("allow_prior_retrieval", True)),
        feedback_learning_enabled=bool(memory_cfg.get("feedback_learning_enabled", False)),
        require_provenance=True,
        max_analog_runs=max(2, min(12, max_analog_runs)),
        min_similarity_score=max(0.0, min(0.95, min_similarity_score)),
        prefer_summary_level_signals=True,
    )
