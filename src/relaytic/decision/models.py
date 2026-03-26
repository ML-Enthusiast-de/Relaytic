"""Typed artifact models for Slice 10A decision-world reasoning."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from relaytic.compiler.models import (
    CompiledBenchmarkProtocol,
    CompiledChallengerTemplates,
    CompiledFeatureHypotheses,
    MethodCompilerReport,
)
from relaytic.data_fabric.models import DataAcquisitionPlan, JoinCandidateReport, SourceGraph


DECISION_CONTROLS_SCHEMA_VERSION = "relaytic.decision_controls.v1"
DECISION_WORLD_MODEL_SCHEMA_VERSION = "relaytic.decision_world_model.v1"
CONTROLLER_POLICY_SCHEMA_VERSION = "relaytic.controller_policy.v1"
HANDOFF_CONTROLLER_REPORT_SCHEMA_VERSION = "relaytic.handoff_controller_report.v1"
INTERVENTION_POLICY_REPORT_SCHEMA_VERSION = "relaytic.intervention_policy_report.v1"
DECISION_USEFULNESS_REPORT_SCHEMA_VERSION = "relaytic.decision_usefulness_report.v1"


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
class DecisionBundle:
    decision_world_model: DecisionWorldModel
    controller_policy: ControllerPolicy
    handoff_controller_report: HandoffControllerReport
    intervention_policy_report: InterventionPolicyReport
    decision_usefulness_report: DecisionUsefulnessReport
    value_of_more_data_report: dict[str, Any]
    data_acquisition_plan: DataAcquisitionPlan
    source_graph: SourceGraph
    join_candidate_report: JoinCandidateReport
    method_compiler_report: MethodCompilerReport
    compiled_challenger_templates: CompiledChallengerTemplates
    compiled_feature_hypotheses: CompiledFeatureHypotheses
    compiled_benchmark_protocol: CompiledBenchmarkProtocol

    def to_dict(self) -> dict[str, Any]:
        return {
            "decision_world_model": self.decision_world_model.to_dict(),
            "controller_policy": self.controller_policy.to_dict(),
            "handoff_controller_report": self.handoff_controller_report.to_dict(),
            "intervention_policy_report": self.intervention_policy_report.to_dict(),
            "decision_usefulness_report": self.decision_usefulness_report.to_dict(),
            "value_of_more_data_report": dict(self.value_of_more_data_report),
            "data_acquisition_plan": self.data_acquisition_plan.to_dict(),
            "source_graph": self.source_graph.to_dict(),
            "join_candidate_report": self.join_candidate_report.to_dict(),
            "method_compiler_report": self.method_compiler_report.to_dict(),
            "compiled_challenger_templates": self.compiled_challenger_templates.to_dict(),
            "compiled_feature_hypotheses": self.compiled_feature_hypotheses.to_dict(),
            "compiled_benchmark_protocol": self.compiled_benchmark_protocol.to_dict(),
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
    )
