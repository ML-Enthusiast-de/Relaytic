"""Typed artifact models for Slice 10B quality and budget contracts."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


PROFILES_CONTROLS_SCHEMA_VERSION = "relaytic.profiles_controls.v1"
QUALITY_CONTRACT_SCHEMA_VERSION = "relaytic.quality_contract.v1"
QUALITY_GATE_REPORT_SCHEMA_VERSION = "relaytic.quality_gate_report.v1"
BUDGET_CONTRACT_SCHEMA_VERSION = "relaytic.budget_contract.v1"
BUDGET_CONSUMPTION_REPORT_SCHEMA_VERSION = "relaytic.budget_consumption_report.v1"
OPERATOR_PROFILE_SCHEMA_VERSION = "relaytic.operator_profile.v1"
LAB_OPERATING_PROFILE_SCHEMA_VERSION = "relaytic.lab_operating_profile.v1"


@dataclass(frozen=True)
class ProfilesControls:
    schema_version: str = PROFILES_CONTROLS_SCHEMA_VERSION
    enabled: bool = True
    allow_operator_profile_overlays: bool = True
    allow_lab_profile_overlays: bool = True
    allow_assumption_defaults: bool = True
    require_visible_quality_gates: bool = True
    require_visible_budget_consumption: bool = True
    quality_review_mode: str = "explicit_contracts"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ProfilesTrace:
    agent: str
    operating_mode: str
    llm_used: bool
    llm_status: str
    deterministic_evidence: list[str] = field(default_factory=list)
    advisory_notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class OperatorProfile:
    schema_version: str
    generated_at: str
    controls: ProfilesControls
    status: str
    profile_name: str
    source: str
    execution_mode_preference: str | None
    operation_mode_preference: str | None
    preferred_report_style: str | None
    preferred_effort_tier: str | None
    review_strictness: str
    benchmark_appetite: str
    explanation_style: str
    abstention_preference: str
    budget_posture: str
    summary: str
    trace: ProfilesTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class LabOperatingProfile:
    schema_version: str
    generated_at: str
    controls: ProfilesControls
    status: str
    profile_name: str
    source: str
    local_truth_required: bool
    remote_intelligence_allowed: bool
    benchmark_required: bool
    review_strictness: str
    risk_posture: str
    budget_posture: str
    notes: list[str]
    summary: str
    trace: ProfilesTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class QualityContract:
    schema_version: str
    generated_at: str
    controls: ProfilesControls
    status: str
    contract_origin: str
    task_type: str
    primary_metric: str
    split_strategy: str
    acceptance_criteria: dict[str, float]
    threshold_policy: str | None
    benchmark_required: bool
    uncertainty_required: bool
    abstention_allowed: bool
    operator_review_required: bool
    minimum_readiness_level: str
    search_budget_posture: str
    operator_profile_name: str
    lab_profile_name: str
    reasoning_requirements: list[str]
    summary: str
    trace: ProfilesTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class QualityGateReport:
    schema_version: str
    generated_at: str
    controls: ProfilesControls
    status: str
    gate_status: str
    recommended_action: str
    quality_state: str
    benchmark_status: str
    readiness_level: str
    measured_metrics: dict[str, Any]
    passed_gates: list[str]
    failed_gates: list[str]
    unmet_acceptance_criteria: list[dict[str, Any]]
    summary: str
    trace: ProfilesTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class BudgetContract:
    schema_version: str
    generated_at: str
    controls: ProfilesControls
    status: str
    contract_origin: str
    execution_profile: str
    machine_profile: str
    preferred_effort_tier: str
    budget_posture: str
    search_budget_posture: str
    max_wall_clock_minutes: int
    max_trials: int
    max_parallel_trials: int
    max_memory_gb: float
    max_followup_rounds: int
    max_branches_per_round: int
    recommended_trial_utilization_fraction: float
    summary: str
    trace: ProfilesTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class BudgetConsumptionReport:
    schema_version: str
    generated_at: str
    controls: ProfilesControls
    status: str
    budget_health: str
    observed_elapsed_minutes: float
    estimated_trials_consumed: int
    remaining_trials: int
    used_branches: int
    remaining_branch_budget: int
    estimated_input_footprint_mb: float | None
    observed_event_count: int
    summary: str
    trace: ProfilesTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class ProfilesBundle:
    quality_contract: QualityContract
    quality_gate_report: QualityGateReport
    budget_contract: BudgetContract
    budget_consumption_report: BudgetConsumptionReport
    operator_profile: OperatorProfile
    lab_operating_profile: LabOperatingProfile

    def to_dict(self) -> dict[str, Any]:
        return {
            "quality_contract": self.quality_contract.to_dict(),
            "quality_gate_report": self.quality_gate_report.to_dict(),
            "budget_contract": self.budget_contract.to_dict(),
            "budget_consumption_report": self.budget_consumption_report.to_dict(),
            "operator_profile": self.operator_profile.to_dict(),
            "lab_operating_profile": self.lab_operating_profile.to_dict(),
        }


def build_profiles_controls_from_policy(policy: dict[str, Any]) -> ProfilesControls:
    profiles_cfg = dict(policy.get("profiles", {}))
    return ProfilesControls(
        enabled=bool(profiles_cfg.get("enabled", True)),
        allow_operator_profile_overlays=bool(profiles_cfg.get("allow_operator_profile_overlays", True)),
        allow_lab_profile_overlays=bool(profiles_cfg.get("allow_lab_profile_overlays", True)),
        allow_assumption_defaults=bool(profiles_cfg.get("allow_assumption_defaults", True)),
        require_visible_quality_gates=bool(profiles_cfg.get("require_visible_quality_gates", True)),
        require_visible_budget_consumption=bool(profiles_cfg.get("require_visible_budget_consumption", True)),
        quality_review_mode=str(profiles_cfg.get("quality_review_mode", "explicit_contracts") or "explicit_contracts"),
    )
