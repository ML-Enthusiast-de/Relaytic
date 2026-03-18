"""Typed artifact models for Slice 05 planning outputs."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


PLANNING_CONTROLS_SCHEMA_VERSION = "relaytic.planning_controls.v1"
PLAN_SCHEMA_VERSION = "relaytic.plan.v1"
ALTERNATIVES_SCHEMA_VERSION = "relaytic.alternatives.v1"
HYPOTHESES_SCHEMA_VERSION = "relaytic.hypotheses.v1"
EXPERIMENT_PRIORITY_REPORT_SCHEMA_VERSION = "relaytic.experiment_priority_report.v1"
MARGINAL_VALUE_OF_NEXT_EXPERIMENT_SCHEMA_VERSION = "relaytic.marginal_value_of_next_experiment.v1"


@dataclass(frozen=True)
class PlanningControls:
    """Resolved controls that govern planning and builder handoff behavior."""

    schema_version: str = PLANNING_CONTROLS_SCHEMA_VERSION
    enabled: bool = True
    strategist_enabled: bool = True
    builder_enabled: bool = True
    intelligence_mode: str = "none"
    prefer_local_llm: bool = True
    allow_local_llm_advisory: bool = False
    require_deterministic_floor: bool = True
    require_artifact_handoff: bool = True
    max_primary_features: int = 24

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class PlanningTrace:
    """Execution trace for the Slice 05 Strategist."""

    agent: str
    operating_mode: str
    llm_used: bool
    llm_status: str
    deterministic_evidence: list[str] = field(default_factory=list)
    advisory_notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class Plan:
    """Primary Strategist artifact and Builder handoff contract."""

    schema_version: str
    generated_at: str
    controls: PlanningControls
    selected_route_id: str
    selected_route_title: str
    target_column: str
    task_type: str
    data_mode: str
    primary_metric: str
    secondary_metrics: list[str]
    split_strategy: str
    timestamp_column: str | None
    feature_columns: list[str]
    feature_drop_reasons: list[dict[str, Any]]
    guardrails: list[str]
    builder_handoff: dict[str, Any]
    execution_steps: list[dict[str, Any]]
    execution_summary: dict[str, Any] | None
    llm_advisory: dict[str, Any] | None
    summary: str
    trace: PlanningTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class Alternatives:
    """Route and builder alternatives considered by Strategist."""

    schema_version: str
    generated_at: str
    controls: PlanningControls
    selected_route_id: str
    alternatives: list[dict[str, Any]]
    summary: str
    trace: PlanningTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class Hypotheses:
    """Testable hypotheses carried into the first execution route."""

    schema_version: str
    generated_at: str
    controls: PlanningControls
    hypotheses: list[dict[str, Any]]
    summary: str
    trace: PlanningTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class ExperimentPriorityReport:
    """Prioritized execution and follow-up queue for Slice 05."""

    schema_version: str
    generated_at: str
    controls: PlanningControls
    prioritized_experiments: list[dict[str, Any]]
    summary: str
    trace: PlanningTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class MarginalValueOfNextExperiment:
    """Estimate of the next most valuable experiment after the selected route."""

    schema_version: str
    generated_at: str
    controls: PlanningControls
    recommended_experiment_id: str
    estimated_value_band: str
    estimated_gain_metric: str
    rationale: str
    blockers_removed: list[str]
    trace: PlanningTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class PlanningBundle:
    """Full Slice 05 artifact bundle."""

    plan: Plan
    alternatives: Alternatives
    hypotheses: Hypotheses
    experiment_priority_report: ExperimentPriorityReport
    marginal_value_of_next_experiment: MarginalValueOfNextExperiment

    def to_dict(self) -> dict[str, Any]:
        return {
            "plan": self.plan.to_dict(),
            "alternatives": self.alternatives.to_dict(),
            "hypotheses": self.hypotheses.to_dict(),
            "experiment_priority_report": self.experiment_priority_report.to_dict(),
            "marginal_value_of_next_experiment": self.marginal_value_of_next_experiment.to_dict(),
        }


def build_planning_controls_from_policy(policy: dict[str, Any]) -> PlanningControls:
    """Derive planning controls from the canonical policy payload."""
    autonomy_cfg = dict(policy.get("autonomy", {}))
    intelligence_cfg = dict(policy.get("intelligence", {}))
    compute_cfg = dict(policy.get("compute", {}))
    intelligence_mode = str(intelligence_cfg.get("intelligence_mode", "none")).strip() or "none"
    normalized_mode = intelligence_mode.lower().replace("-", "_")
    advisory_enabled = normalized_mode not in {"", "none", "off", "disabled", "deterministic"}
    return PlanningControls(
        enabled=True,
        strategist_enabled=True,
        builder_enabled=bool(autonomy_cfg.get("allow_auto_run", True)),
        intelligence_mode=intelligence_mode,
        prefer_local_llm=bool(intelligence_cfg.get("prefer_local_llm", True)),
        allow_local_llm_advisory=bool(intelligence_cfg.get("enabled", True)) and advisory_enabled,
        require_deterministic_floor=True,
        require_artifact_handoff=True,
        max_primary_features=max(4, int(compute_cfg.get("max_parallel_trials", 4) or 4) * 4),
    )
