"""Typed artifact models for Slice 10 feedback assimilation and outcome learning."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


FEEDBACK_CONTROLS_SCHEMA_VERSION = "relaytic.feedback_controls.v1"
FEEDBACK_INTAKE_SCHEMA_VERSION = "relaytic.feedback_intake.v1"
FEEDBACK_VALIDATION_SCHEMA_VERSION = "relaytic.feedback_validation.v1"
FEEDBACK_EFFECT_REPORT_SCHEMA_VERSION = "relaytic.feedback_effect_report.v1"
FEEDBACK_CASEBOOK_SCHEMA_VERSION = "relaytic.feedback_casebook.v1"
OUTCOME_OBSERVATION_REPORT_SCHEMA_VERSION = "relaytic.outcome_observation_report.v1"
DECISION_POLICY_UPDATE_SUGGESTIONS_SCHEMA_VERSION = "relaytic.decision_policy_update_suggestions.v1"
POLICY_UPDATE_SUGGESTIONS_SCHEMA_VERSION = "relaytic.policy_update_suggestions.v1"
ROUTE_PRIOR_UPDATES_SCHEMA_VERSION = "relaytic.route_prior_updates.v1"


@dataclass(frozen=True)
class FeedbackControls:
    schema_version: str = FEEDBACK_CONTROLS_SCHEMA_VERSION
    enabled: bool = True
    accept_human_feedback: bool = True
    accept_external_agent_feedback: bool = True
    accept_runtime_failure_feedback: bool = True
    accept_benchmark_review_feedback: bool = True
    accept_outcome_observations: bool = True
    min_acceptance_score: float = 0.68
    downgrade_threshold: float = 0.40
    allow_route_prior_updates: bool = True
    allow_policy_update_suggestions: bool = True
    allow_decision_policy_update_suggestions: bool = True
    max_casebook_entries: int = 50

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class FeedbackTrace:
    agent: str
    operating_mode: str
    llm_used: bool
    llm_status: str
    deterministic_evidence: list[str] = field(default_factory=list)
    advisory_notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class FeedbackIntake:
    schema_version: str
    generated_at: str
    controls: FeedbackControls
    status: str
    total_count: int
    active_count: int
    reverted_count: int
    source_types: list[str]
    entries: list[dict[str, Any]]
    summary: str
    trace: FeedbackTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class FeedbackValidation:
    schema_version: str
    generated_at: str
    controls: FeedbackControls
    status: str
    accepted_count: int
    downgraded_count: int
    rejected_count: int
    reverted_count: int
    accepted_entries: list[dict[str, Any]]
    downgraded_entries: list[dict[str, Any]]
    rejected_entries: list[dict[str, Any]]
    reverted_entries: list[dict[str, Any]]
    trust_summary: dict[str, Any]
    summary: str
    trace: FeedbackTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class RoutePriorUpdates:
    schema_version: str
    generated_at: str
    controls: FeedbackControls
    status: str
    updates: list[dict[str, Any]]
    summary: str
    trace: FeedbackTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class PolicyUpdateSuggestions:
    schema_version: str
    generated_at: str
    controls: FeedbackControls
    status: str
    suggestions: list[dict[str, Any]]
    summary: str
    trace: FeedbackTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class DecisionPolicyUpdateSuggestions:
    schema_version: str
    generated_at: str
    controls: FeedbackControls
    status: str
    suggestions: list[dict[str, Any]]
    primary_recommended_action: str | None
    summary: str
    trace: FeedbackTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class OutcomeObservationReport:
    schema_version: str
    generated_at: str
    controls: FeedbackControls
    status: str
    accepted_outcome_count: int
    contradiction_count: int
    positive_outcome_count: int
    negative_outcome_count: int
    observed_entries: list[dict[str, Any]]
    summary: str
    trace: FeedbackTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class FeedbackEffectReport:
    schema_version: str
    generated_at: str
    controls: FeedbackControls
    status: str
    active_feedback_count: int
    accepted_feedback_count: int
    downgraded_feedback_count: int
    rejected_feedback_count: int
    reverted_feedback_count: int
    changed_future_route_recommendations: bool
    changed_policy_suggestions: bool
    changed_decision_policy_recommendations: bool
    primary_recommended_action: str | None
    accepted_feedback_ids: list[str]
    reverted_feedback_ids: list[str]
    changed_artifacts: list[str]
    summary: str
    trace: FeedbackTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class FeedbackCasebook:
    schema_version: str
    generated_at: str
    controls: FeedbackControls
    status: str
    accepted_cases: list[dict[str, Any]]
    rejected_cases: list[dict[str, Any]]
    reverted_cases: list[dict[str, Any]]
    source_counts: dict[str, int]
    effect_counts: dict[str, int]
    summary: str
    trace: FeedbackTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class FeedbackBundle:
    feedback_intake: FeedbackIntake
    feedback_validation: FeedbackValidation
    feedback_effect_report: FeedbackEffectReport
    feedback_casebook: FeedbackCasebook
    outcome_observation_report: OutcomeObservationReport
    decision_policy_update_suggestions: DecisionPolicyUpdateSuggestions
    policy_update_suggestions: PolicyUpdateSuggestions
    route_prior_updates: RoutePriorUpdates

    def to_dict(self) -> dict[str, Any]:
        return {
            "feedback_intake": self.feedback_intake.to_dict(),
            "feedback_validation": self.feedback_validation.to_dict(),
            "feedback_effect_report": self.feedback_effect_report.to_dict(),
            "feedback_casebook": self.feedback_casebook.to_dict(),
            "outcome_observation_report": self.outcome_observation_report.to_dict(),
            "decision_policy_update_suggestions": self.decision_policy_update_suggestions.to_dict(),
            "policy_update_suggestions": self.policy_update_suggestions.to_dict(),
            "route_prior_updates": self.route_prior_updates.to_dict(),
        }


def build_feedback_controls_from_policy(policy: dict[str, Any]) -> FeedbackControls:
    feedback_cfg = dict(policy.get("feedback", {}))
    try:
        min_acceptance_score = float(feedback_cfg.get("min_acceptance_score", 0.68) or 0.68)
    except (TypeError, ValueError):
        min_acceptance_score = 0.68
    try:
        downgrade_threshold = float(feedback_cfg.get("downgrade_threshold", 0.40) or 0.40)
    except (TypeError, ValueError):
        downgrade_threshold = 0.40
    try:
        max_casebook_entries = int(feedback_cfg.get("max_casebook_entries", 50) or 50)
    except (TypeError, ValueError):
        max_casebook_entries = 50
    return FeedbackControls(
        enabled=bool(feedback_cfg.get("enabled", True)),
        accept_human_feedback=bool(feedback_cfg.get("accept_human_feedback", True)),
        accept_external_agent_feedback=bool(feedback_cfg.get("accept_external_agent_feedback", True)),
        accept_runtime_failure_feedback=bool(feedback_cfg.get("accept_runtime_failure_feedback", True)),
        accept_benchmark_review_feedback=bool(feedback_cfg.get("accept_benchmark_review_feedback", True)),
        accept_outcome_observations=bool(feedback_cfg.get("accept_outcome_observations", True)),
        min_acceptance_score=max(0.0, min(1.0, min_acceptance_score)),
        downgrade_threshold=max(0.0, min(1.0, downgrade_threshold)),
        allow_route_prior_updates=bool(feedback_cfg.get("allow_route_prior_updates", True)),
        allow_policy_update_suggestions=bool(feedback_cfg.get("allow_policy_update_suggestions", True)),
        allow_decision_policy_update_suggestions=bool(feedback_cfg.get("allow_decision_policy_update_suggestions", True)),
        max_casebook_entries=max(10, min(500, max_casebook_entries)),
    )
