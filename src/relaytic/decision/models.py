"""Typed artifact models for Slice 10A decision-world reasoning."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from relaytic.compiler.models import (
    ArchitectureCandidateRegistry,
    CompiledBenchmarkProtocol,
    CompiledChallengerTemplates,
    CompiledFeatureHypotheses,
    MethodImportReport,
    MethodCompilerReport,
)
from relaytic.data_fabric.models import DataAcquisitionPlan, JoinCandidateReport, SourceGraph


DECISION_CONTROLS_SCHEMA_VERSION = "relaytic.decision_controls.v1"
DECISION_WORLD_MODEL_SCHEMA_VERSION = "relaytic.decision_world_model.v1"
CONTROLLER_POLICY_SCHEMA_VERSION = "relaytic.controller_policy.v1"
HANDOFF_CONTROLLER_REPORT_SCHEMA_VERSION = "relaytic.handoff_controller_report.v1"
INTERVENTION_POLICY_REPORT_SCHEMA_VERSION = "relaytic.intervention_policy_report.v1"
DECISION_USEFULNESS_REPORT_SCHEMA_VERSION = "relaytic.decision_usefulness_report.v1"
TRAJECTORY_CONSTRAINT_REPORT_SCHEMA_VERSION = "relaytic.trajectory_constraint_report.v1"
FEASIBLE_REGION_MAP_SCHEMA_VERSION = "relaytic.feasible_region_map.v1"
EXTRAPOLATION_RISK_REPORT_SCHEMA_VERSION = "relaytic.extrapolation_risk_report.v1"
DECISION_CONSTRAINT_REPORT_SCHEMA_VERSION = "relaytic.decision_constraint_report.v1"
ACTION_BOUNDARY_REPORT_SCHEMA_VERSION = "relaytic.action_boundary_report.v1"
DEPLOYABILITY_ASSESSMENT_SCHEMA_VERSION = "relaytic.deployability_assessment.v1"
REVIEW_GATE_STATE_SCHEMA_VERSION = "relaytic.review_gate_state.v1"
CONSTRAINT_OVERRIDE_REQUEST_SCHEMA_VERSION = "relaytic.constraint_override_request.v1"
COUNTERFACTUAL_REGION_REPORT_SCHEMA_VERSION = "relaytic.counterfactual_region_report.v1"


@dataclass(frozen=True)
class DecisionControls:
    schema_version: str = DECISION_CONTROLS_SCHEMA_VERSION
    enabled: bool = True
    allow_provisional_world_model: bool = True
    allow_local_source_graph: bool = True
    max_join_candidates: int = 5
    max_compiled_templates: int = 6
    default_operator_review_capacity: str = "medium"
    controller_review_threshold: str = "conditional_pass"
    enable_feasibility_reasoning: bool = True
    extrapolation_review_threshold: float = 0.2
    extrapolation_physical_threshold: float = 0.35

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class DecisionTrace:
    agent: str
    operating_mode: str
    llm_used: bool
    llm_status: str
    deterministic_evidence: list[str] = field(default_factory=list)
    advisory_notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class DecisionWorldModel:
    schema_version: str
    generated_at: str
    controls: DecisionControls
    status: str
    task_type: str
    domain_archetype: str
    action_regime: str
    false_positive_cost_band: str
    false_negative_cost_band: str
    defer_cost_band: str
    delay_cost_band: str
    operator_review_capacity: str
    abstention_allowed: bool
    under_specified: bool
    uncertainty_sources: list[str]
    primary_decision_question: str
    threshold_posture: str
    summary: str
    trace: DecisionTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class ControllerPolicy:
    schema_version: str
    generated_at: str
    controls: DecisionControls
    status: str
    next_actor: str
    controller_mode: str
    review_required: bool
    keep_work_local: bool
    branch_depth_budget: int
    selected_next_action: str
    specialist_order: list[str]
    summary: str
    trace: DecisionTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class HandoffControllerReport:
    schema_version: str
    generated_at: str
    controls: DecisionControls
    status: str
    baseline_action: str | None
    baseline_actor: str
    selected_action: str
    selected_actor: str
    changed_controller_path: bool
    reviewer_involvement: str
    reasons: list[str]
    summary: str
    trace: DecisionTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class InterventionPolicyReport:
    schema_version: str
    generated_at: str
    controls: DecisionControls
    status: str
    control_decision: str
    override_posture: str
    checkpoint_required: bool
    skeptical_bias_level: str
    steering_confidence: str
    summary: str
    trace: DecisionTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class DecisionUsefulnessReport:
    schema_version: str
    generated_at: str
    controls: DecisionControls
    status: str
    changed_judgment: bool
    changed_next_action: bool
    changed_controller_path: bool
    usefulness_sources: list[str]
    selected_strategy: str
    summary: str
    trace: DecisionTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class TrajectoryConstraintReport:
    schema_version: str
    generated_at: str
    controls: DecisionControls
    status: str
    trajectory_status: str
    physical_constraint_count: int
    operational_constraint_count: int
    policy_constraint_count: int
    constraint_sources: list[str]
    summary: str
    trace: DecisionTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class FeasibleRegionMap:
    schema_version: str
    generated_at: str
    controls: DecisionControls
    status: str
    region_posture: str
    in_distribution: bool
    deployment_scope: str
    blocked_regions: list[str]
    summary: str
    trace: DecisionTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class ExtrapolationRiskReport:
    schema_version: str
    generated_at: str
    controls: DecisionControls
    status: str
    risk_band: str
    observed_ood_fraction: float | None
    exceeds_review_threshold: bool
    exceeds_physical_threshold: bool
    recommended_direction: str | None
    summary: str
    trace: DecisionTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class DecisionConstraintReport:
    schema_version: str
    generated_at: str
    controls: DecisionControls
    status: str
    controller_selected_action: str | None
    feasible_selected_action: str | None
    recommended_direction: str | None
    recommendation_changed: bool
    primary_constraint_kind: str | None
    blocking_constraints: list[dict[str, Any]]
    summary: str
    trace: DecisionTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class ActionBoundaryReport:
    schema_version: str
    generated_at: str
    controls: DecisionControls
    status: str
    proposal_status: str
    deployability_status: str
    approval_required: bool
    review_required: bool
    override_required: bool
    rerun_recommended: bool
    abstain_recommended: bool
    reason_codes: list[str]
    summary: str
    trace: DecisionTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class DeployabilityAssessment:
    schema_version: str
    generated_at: str
    controls: DecisionControls
    status: str
    deployability: str
    decision_usefulness: str
    operational_readiness: str
    approval_posture: str
    summary: str
    trace: DecisionTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class ReviewGateState:
    schema_version: str
    generated_at: str
    controls: DecisionControls
    status: str
    gate_open: bool
    gate_kind: str | None
    recommended_action: str | None
    review_reason: str | None
    summary: str
    trace: DecisionTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class ConstraintOverrideRequest:
    schema_version: str
    generated_at: str
    controls: DecisionControls
    status: str
    override_required: bool
    requested_action: str | None
    blocked_action: str | None
    constraint_kind: str | None
    reason: str | None
    summary: str
    trace: DecisionTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class CounterfactualRegionReport:
    schema_version: str
    generated_at: str
    controls: DecisionControls
    status: str
    why_not_rerun: str | None
    why_not_same_data: str | None
    why_not_new_dataset: str | None
    alternative_outcomes: list[dict[str, Any]]
    summary: str
    trace: DecisionTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class DecisionBundle:
    decision_world_model: DecisionWorldModel
    controller_policy: ControllerPolicy
    handoff_controller_report: HandoffControllerReport
    intervention_policy_report: InterventionPolicyReport
    decision_usefulness_report: DecisionUsefulnessReport
    trajectory_constraint_report: TrajectoryConstraintReport
    feasible_region_map: FeasibleRegionMap
    extrapolation_risk_report: ExtrapolationRiskReport
    decision_constraint_report: DecisionConstraintReport
    action_boundary_report: ActionBoundaryReport
    deployability_assessment: DeployabilityAssessment
    review_gate_state: ReviewGateState
    constraint_override_request: ConstraintOverrideRequest
    counterfactual_region_report: CounterfactualRegionReport
    value_of_more_data_report: dict[str, Any]
    data_acquisition_plan: DataAcquisitionPlan
    source_graph: SourceGraph
    join_candidate_report: JoinCandidateReport
    method_compiler_report: MethodCompilerReport
    compiled_challenger_templates: CompiledChallengerTemplates
    compiled_feature_hypotheses: CompiledFeatureHypotheses
    compiled_benchmark_protocol: CompiledBenchmarkProtocol
    method_import_report: MethodImportReport
    architecture_candidate_registry: ArchitectureCandidateRegistry

    def to_dict(self) -> dict[str, Any]:
        return {
            "decision_world_model": self.decision_world_model.to_dict(),
            "controller_policy": self.controller_policy.to_dict(),
            "handoff_controller_report": self.handoff_controller_report.to_dict(),
            "intervention_policy_report": self.intervention_policy_report.to_dict(),
            "decision_usefulness_report": self.decision_usefulness_report.to_dict(),
            "trajectory_constraint_report": self.trajectory_constraint_report.to_dict(),
            "feasible_region_map": self.feasible_region_map.to_dict(),
            "extrapolation_risk_report": self.extrapolation_risk_report.to_dict(),
            "decision_constraint_report": self.decision_constraint_report.to_dict(),
            "action_boundary_report": self.action_boundary_report.to_dict(),
            "deployability_assessment": self.deployability_assessment.to_dict(),
            "review_gate_state": self.review_gate_state.to_dict(),
            "constraint_override_request": self.constraint_override_request.to_dict(),
            "counterfactual_region_report": self.counterfactual_region_report.to_dict(),
            "value_of_more_data_report": dict(self.value_of_more_data_report),
            "data_acquisition_plan": self.data_acquisition_plan.to_dict(),
            "source_graph": self.source_graph.to_dict(),
            "join_candidate_report": self.join_candidate_report.to_dict(),
            "method_compiler_report": self.method_compiler_report.to_dict(),
            "compiled_challenger_templates": self.compiled_challenger_templates.to_dict(),
            "compiled_feature_hypotheses": self.compiled_feature_hypotheses.to_dict(),
            "compiled_benchmark_protocol": self.compiled_benchmark_protocol.to_dict(),
            "method_import_report": self.method_import_report.to_dict(),
            "architecture_candidate_registry": self.architecture_candidate_registry.to_dict(),
        }


def build_decision_controls_from_policy(policy: dict[str, Any]) -> DecisionControls:
    decision_cfg = dict(policy.get("decision", {}))
    return DecisionControls(
        enabled=bool(decision_cfg.get("enabled", True)),
        allow_provisional_world_model=bool(decision_cfg.get("allow_provisional_world_model", True)),
        allow_local_source_graph=bool(decision_cfg.get("allow_local_source_graph", True)),
        max_join_candidates=max(1, int(decision_cfg.get("max_join_candidates", 5) or 5)),
        max_compiled_templates=max(1, int(decision_cfg.get("max_compiled_templates", 6) or 6)),
        default_operator_review_capacity=str(
            decision_cfg.get("default_operator_review_capacity", "medium") or "medium"
        ),
        controller_review_threshold=str(
            decision_cfg.get("controller_review_threshold", "conditional_pass") or "conditional_pass"
        ),
        enable_feasibility_reasoning=bool(decision_cfg.get("enable_feasibility_reasoning", True)),
        extrapolation_review_threshold=float(decision_cfg.get("extrapolation_review_threshold", 0.2) or 0.2),
        extrapolation_physical_threshold=float(decision_cfg.get("extrapolation_physical_threshold", 0.35) or 0.35),
    )
