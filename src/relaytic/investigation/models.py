"""Typed artifact models for Slice 03 investigation outputs."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


INVESTIGATION_CONTROLS_SCHEMA_VERSION = "relaytic.investigation_controls.v1"
DATASET_PROFILE_SCHEMA_VERSION = "relaytic.dataset_profile.v1"
DOMAIN_MEMO_SCHEMA_VERSION = "relaytic.domain_memo.v1"
OBJECTIVE_HYPOTHESES_SCHEMA_VERSION = "relaytic.objective_hypotheses.v1"
FOCUS_DEBATE_SCHEMA_VERSION = "relaytic.focus_debate.v1"
FOCUS_PROFILE_SCHEMA_VERSION = "relaytic.focus_profile.v1"
OPTIMIZATION_PROFILE_SCHEMA_VERSION = "relaytic.optimization_profile.v1"
FEATURE_STRATEGY_PROFILE_SCHEMA_VERSION = "relaytic.feature_strategy_profile.v1"


@dataclass(frozen=True)
class InvestigationControls:
    """Resolved controls that govern investigation behavior."""

    schema_version: str = INVESTIGATION_CONTROLS_SCHEMA_VERSION
    enabled: bool = True
    focus_council_enabled: bool = True
    intelligence_mode: str = "none"
    prefer_local_llm: bool = True
    allow_local_llm_advisory: bool = False
    require_schema_constrained_actions: bool = True
    strict_leakage_checks: bool = True
    strict_time_ordering: bool = True
    reproducibility_required: bool = True

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class SpecialistTrace:
    """Execution trace for one specialist run."""

    agent: str
    operating_mode: str
    llm_used: bool
    llm_status: str
    deterministic_evidence: list[str] = field(default_factory=list)
    advisory_notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class DatasetProfile:
    """Structured Scout artifact for dataset inspection."""

    schema_version: str
    generated_at: str
    controls: InvestigationControls
    source_path: str
    file_type: str
    selected_sheet: str | None
    header_row: int
    data_start_row: int
    row_count: int
    column_count: int
    numeric_columns: list[str]
    categorical_columns: list[str]
    binary_like_columns: list[str]
    candidate_target_columns: list[str]
    hidden_key_candidates: list[str]
    entity_key_candidates: list[str]
    suspicious_columns: list[str]
    leakage_risk_level: str
    leakage_risks: list[dict[str, Any]]
    quality_warnings: list[str]
    completeness_score: float
    missing_fraction_by_column: dict[str, float]
    duplicate_rows: int
    constant_columns: list[str]
    extreme_outlier_columns: list[str]
    data_mode: str
    timestamp_column: str | None
    estimated_sample_period_seconds: float | None
    duplicate_timestamps: int
    monotonic_timestamp: bool | None
    stationarity: dict[str, Any]
    scout_summary: str
    trace: SpecialistTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class DomainMemo:
    """Structured Scientist artifact for domain/task interpretation."""

    schema_version: str
    generated_at: str
    controls: InvestigationControls
    operational_problem_statement: str
    domain_summary: str
    domain_archetype: str
    target_candidates: list[dict[str, Any]]
    expert_priors: dict[str, Any]
    knowledge_sources: list[dict[str, Any]]
    route_hypotheses: list[dict[str, Any]]
    split_hypotheses: list[dict[str, Any]]
    feature_hypotheses: list[dict[str, Any]]
    additional_data_hypotheses: list[dict[str, Any]]
    unresolved_questions: list[str]
    domain_risks: list[str]
    llm_advisory: dict[str, Any] | None
    scientist_summary: str
    trace: SpecialistTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class ObjectiveHypotheses:
    """Structured Focus Council hypothesis artifact."""

    schema_version: str
    generated_at: str
    controls: InvestigationControls
    hypotheses: list[dict[str, Any]]
    summary: str
    trace: SpecialistTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class FocusDebate:
    """Structured debate transcript for objective resolution."""

    schema_version: str
    generated_at: str
    controls: InvestigationControls
    activated_lenses: list[str]
    lens_positions: list[dict[str, Any]]
    mandate_conflicts: list[dict[str, Any]]
    resolution: dict[str, Any]
    llm_advisory: dict[str, Any] | None
    trace: SpecialistTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class FocusProfile:
    """Resolved objective profile for downstream planning."""

    schema_version: str
    generated_at: str
    controls: InvestigationControls
    primary_objective: str
    secondary_objectives: list[str]
    resolution_mode: str
    active_lenses: list[str]
    objective_weights: dict[str, float]
    mandate_alignment: dict[str, Any]
    confidence: float
    summary: str
    trace: SpecialistTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class OptimizationProfile:
    """Derived optimization posture for the next slice."""

    schema_version: str
    generated_at: str
    controls: InvestigationControls
    primary_metric: str
    secondary_metrics: list[str]
    threshold_objective: str
    split_strategy_bias: str
    model_family_bias: list[str]
    search_budget_posture: str
    calibration_required: bool
    uncertainty_required: bool
    reproducibility_required: bool
    notes: list[str]
    trace: SpecialistTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class FeatureStrategyProfile:
    """Derived feature strategy posture for the next slice."""

    schema_version: str
    generated_at: str
    controls: InvestigationControls
    prioritize_lag_features: bool
    prioritize_interactions: bool
    prioritize_missingness_indicators: bool
    prioritize_stability_features: bool
    prioritize_simple_features: bool
    preferred_feature_families: list[str]
    de_emphasized_feature_families: list[str]
    excluded_columns: list[str]
    guardrails: list[str]
    notes: list[str]
    trace: SpecialistTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class InvestigationBundle:
    """Full Slice 03 artifact bundle returned by the investigation pipeline."""

    dataset_profile: DatasetProfile
    domain_memo: DomainMemo
    objective_hypotheses: ObjectiveHypotheses
    focus_debate: FocusDebate
    focus_profile: FocusProfile
    optimization_profile: OptimizationProfile
    feature_strategy_profile: FeatureStrategyProfile

    def to_dict(self) -> dict[str, Any]:
        return {
            "dataset_profile": self.dataset_profile.to_dict(),
            "domain_memo": self.domain_memo.to_dict(),
            "objective_hypotheses": self.objective_hypotheses.to_dict(),
            "focus_debate": self.focus_debate.to_dict(),
            "focus_profile": self.focus_profile.to_dict(),
            "optimization_profile": self.optimization_profile.to_dict(),
            "feature_strategy_profile": self.feature_strategy_profile.to_dict(),
        }


def build_investigation_controls_from_policy(policy: dict[str, Any]) -> InvestigationControls:
    """Derive investigation controls from the canonical policy payload."""
    optimization_cfg = dict(policy.get("optimization", {}))
    intelligence_cfg = dict(policy.get("intelligence", {}))
    safety_cfg = dict(policy.get("safety", {}))
    constraints_cfg = dict(policy.get("constraints", {}))
    intelligence_mode = str(intelligence_cfg.get("intelligence_mode", "none")).strip() or "none"
    normalized_mode = intelligence_mode.lower().replace("-", "_")
    advisory_enabled = normalized_mode not in {"", "none", "off", "disabled", "deterministic"}
    return InvestigationControls(
        enabled=True,
        focus_council_enabled=bool(optimization_cfg.get("focus_council_enabled", True)),
        intelligence_mode=intelligence_mode,
        prefer_local_llm=bool(intelligence_cfg.get("prefer_local_llm", True)),
        allow_local_llm_advisory=bool(intelligence_cfg.get("enabled", True)) and advisory_enabled,
        require_schema_constrained_actions=bool(
            intelligence_cfg.get("require_schema_constrained_actions", True)
        ),
        strict_leakage_checks=bool(safety_cfg.get("strict_leakage_checks", True)),
        strict_time_ordering=bool(safety_cfg.get("strict_time_ordering", True)),
        reproducibility_required=bool(constraints_cfg.get("reproducibility_required", True)),
    )
