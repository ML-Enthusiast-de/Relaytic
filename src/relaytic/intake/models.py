"""Typed artifact models for Slice 04 intake and translation."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


INTAKE_CONTROLS_SCHEMA_VERSION = "relaytic.intake_controls.v1"
INTAKE_RECORD_SCHEMA_VERSION = "relaytic.intake_record.v1"
CONTEXT_INTERPRETATION_SCHEMA_VERSION = "relaytic.context_interpretation.v1"
CONTEXT_CONSTRAINTS_SCHEMA_VERSION = "relaytic.context_constraints.v1"
SEMANTIC_MAPPING_SCHEMA_VERSION = "relaytic.semantic_mapping.v1"
AUTONOMY_MODE_SCHEMA_VERSION = "relaytic.autonomy_mode.v1"
CLARIFICATION_QUEUE_SCHEMA_VERSION = "relaytic.clarification_queue.v1"
ASSUMPTION_LOG_SCHEMA_VERSION = "relaytic.assumption_log.v1"


@dataclass(frozen=True)
class IntakeControls:
    """Resolved controls that govern intake interpretation."""

    schema_version: str = INTAKE_CONTROLS_SCHEMA_VERSION
    enabled: bool = True
    allow_free_text: bool = True
    allow_structured_templates: bool = True
    semantic_mapping_enabled: bool = True
    require_provenance: bool = True
    intelligence_mode: str = "none"
    prefer_local_llm: bool = True
    allow_local_llm_advisory: bool = False
    clarification_threshold: float = 0.72

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class InterpretationTrace:
    """Execution trace for one intake specialist."""

    agent: str
    operating_mode: str
    llm_used: bool
    llm_status: str
    deterministic_evidence: list[str] = field(default_factory=list)
    advisory_notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class IntakeRecord:
    """Raw intake event captured before translation."""

    schema_version: str
    captured_at: str
    controls: IntakeControls
    actor_type: str
    actor_name: str | None
    channel: str
    source_format: str
    message: str
    dataset_path: str | None
    selected_sheet: str | None
    header_row: int | None
    data_start_row: int | None
    schema_validation: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        return payload


@dataclass(frozen=True)
class SemanticMatch:
    """One mapping between text and a normalized Relaytic field."""

    field: str
    value: str
    confidence: float
    evidence: str
    source: str = "deterministic"
    matched_column: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class SemanticMapping:
    """How free-form input mapped onto schema columns and artifact fields."""

    schema_version: str
    generated_at: str
    controls: IntakeControls
    schema_columns: list[str]
    field_matches: list[SemanticMatch]
    unmatched_terms: list[str]
    summary: str
    trace: InterpretationTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["field_matches"] = [item.to_dict() for item in self.field_matches]
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class AutonomyMode:
    """How Relaytic should behave when clarification is incomplete."""

    schema_version: str
    generated_at: str
    controls: IntakeControls
    requested_mode: str
    proceed_without_answers: bool
    suppress_noncritical_questions: bool
    question_policy: str
    operator_signal: str | None
    hard_stop_required: bool
    hard_stop_reasons: list[str]
    summary: str
    trace: InterpretationTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class ClarificationItem:
    """One optional clarification question plus its fallback resolution."""

    id: str
    question: str
    optional: bool
    blocking_class: str
    default_resolution: str
    confidence_impact: str
    affected_artifacts: list[str]
    status: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ClarificationQueue:
    """Non-blocking clarification items produced during intake."""

    schema_version: str
    generated_at: str
    controls: IntakeControls
    items: list[ClarificationItem]
    active_count: int
    suppressed_count: int
    summary: str
    trace: InterpretationTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["items"] = [item.to_dict() for item in self.items]
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class AssumptionEntry:
    """One explicit assumption used to keep the run moving."""

    id: str
    category: str
    assumption: str
    rationale: str
    confidence: float
    source: str
    affected_artifacts: list[str]
    derived_from_question_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class AssumptionLog:
    """Explicit assumptions chosen when Relaytic proceeds autonomously."""

    schema_version: str
    generated_at: str
    controls: IntakeControls
    entries: list[AssumptionEntry]
    summary: str
    trace: InterpretationTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["entries"] = [item.to_dict() for item in self.entries]
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class ContextConstraints:
    """Constraint-centric interpretation extracted from intake."""

    schema_version: str
    generated_at: str
    controls: IntakeControls
    binding_constraints: list[str]
    forbidden_features: list[str]
    suspicious_columns: list[str]
    hard_constraints: list[str]
    soft_preferences: list[str]
    prohibited_actions: list[str]
    success_criteria: list[str]
    failure_costs: list[str]
    clarification_questions: list[str]
    assumptions: list[str]
    trace: InterpretationTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class ContextInterpretation:
    """Normalized update candidates for mandate/context/run artifacts."""

    schema_version: str
    generated_at: str
    controls: IntakeControls
    lab_mandate_updates: dict[str, Any]
    work_preference_updates: dict[str, Any]
    run_brief_updates: dict[str, Any]
    data_origin_updates: dict[str, Any]
    domain_brief_updates: dict[str, Any]
    task_brief_updates: dict[str, Any]
    clarification_questions: list[str]
    assumptions: list[str]
    conflicts: list[str]
    llm_advisory: dict[str, Any] | None
    summary: str
    trace: InterpretationTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class IntakeBundle:
    """Full Slice 04 artifact bundle."""

    intake_record: IntakeRecord
    autonomy_mode: AutonomyMode
    clarification_queue: ClarificationQueue
    assumption_log: AssumptionLog
    context_interpretation: ContextInterpretation
    context_constraints: ContextConstraints
    semantic_mapping: SemanticMapping

    def to_dict(self) -> dict[str, Any]:
        return {
            "intake_record": self.intake_record.to_dict(),
            "autonomy_mode": self.autonomy_mode.to_dict(),
            "clarification_queue": self.clarification_queue.to_dict(),
            "assumption_log": self.assumption_log.to_dict(),
            "context_interpretation": self.context_interpretation.to_dict(),
            "context_constraints": self.context_constraints.to_dict(),
            "semantic_mapping": self.semantic_mapping.to_dict(),
        }


def build_intake_controls_from_policy(policy: dict[str, Any]) -> IntakeControls:
    """Derive intake controls from the canonical policy payload."""
    context_cfg = dict(policy.get("context", {}))
    intelligence_cfg = dict(policy.get("intelligence", {}))
    intelligence_mode = str(intelligence_cfg.get("intelligence_mode", "none")).strip() or "none"
    normalized_mode = intelligence_mode.lower().replace("-", "_")
    advisory_enabled = normalized_mode not in {"", "none", "off", "disabled", "deterministic"}
    return IntakeControls(
        enabled=bool(context_cfg.get("enabled", True)),
        allow_free_text=True,
        allow_structured_templates=True,
        semantic_mapping_enabled=True,
        require_provenance=bool(context_cfg.get("require_provenance", True)),
        intelligence_mode=intelligence_mode,
        prefer_local_llm=bool(intelligence_cfg.get("prefer_local_llm", True)),
        allow_local_llm_advisory=bool(intelligence_cfg.get("enabled", True)) and advisory_enabled,
        clarification_threshold=float(context_cfg.get("clarification_threshold", 0.72)),
    )
