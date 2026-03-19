"""Typed artifact models for Slice 08 lifecycle-governor outputs."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


LIFECYCLE_CONTROLS_SCHEMA_VERSION = "relaytic.lifecycle_controls.v1"
CHAMPION_VS_CANDIDATE_SCHEMA_VERSION = "relaytic.champion_vs_candidate.v1"
RECALIBRATION_DECISION_SCHEMA_VERSION = "relaytic.recalibration_decision.v1"
RETRAIN_DECISION_SCHEMA_VERSION = "relaytic.retrain_decision.v1"
PROMOTION_DECISION_SCHEMA_VERSION = "relaytic.promotion_decision.v1"
ROLLBACK_DECISION_SCHEMA_VERSION = "relaytic.rollback_decision.v1"

PROMOTION_ACTIONS = {
    "keep_current_champion",
    "promote_challenger",
    "hold_promotion",
}
RECALIBRATION_ACTIONS = {
    "recalibrate",
    "no_recalibration",
}
RETRAIN_ACTIONS = {
    "retrain",
    "no_retrain",
}
ROLLBACK_ACTIONS = {
    "rollback_required",
    "no_rollback",
}


@dataclass(frozen=True)
class LifecycleControls:
    """Resolved controls for Slice 08 lifecycle decisions."""

    schema_version: str = LIFECYCLE_CONTROLS_SCHEMA_VERSION
    enabled: bool = True
    recalibration_only_allowed: bool = True
    rollback_allowed: bool = True
    champion_candidate_registry_enabled: bool = False
    prefer_current_batch_behavior: bool = True
    allow_uncertainty_adapter: bool = True
    allow_monitoring_adapter: bool = True
    allow_registry_export: bool = False
    allow_observability_export: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class LifecycleTrace:
    """Execution trace for one lifecycle specialist."""

    agent: str
    operating_mode: str
    llm_used: bool
    llm_status: str
    deterministic_evidence: list[str] = field(default_factory=list)
    advisory_notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ChampionVsCandidate:
    """Comparison between the current champion and the first bounded candidate."""

    schema_version: str
    generated_at: str
    controls: LifecycleControls
    task_type: str
    primary_metric: str
    champion_model_family: str | None
    challenger_model_family: str | None
    champion_metric_value: float | None
    challenger_metric_value: float | None
    challenger_delta_to_champion: float | None
    challenger_winner: str
    fresh_data_behavior: dict[str, Any]
    completion_signal: dict[str, Any]
    evidence_signal: dict[str, Any]
    adapter_slots: list[dict[str, Any]]
    summary: str
    trace: LifecycleTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class RecalibrationDecision:
    """Decision on whether recalibration is preferable to full retraining."""

    schema_version: str
    generated_at: str
    controls: LifecycleControls
    action: str
    confidence: str
    reason_codes: list[str]
    stale_calibration_signals: list[str]
    next_step: str
    summary: str
    trace: LifecycleTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class RetrainDecision:
    """Decision on whether the route should be retrained now."""

    schema_version: str
    generated_at: str
    controls: LifecycleControls
    action: str
    confidence: str
    reason_codes: list[str]
    urgency: str
    next_step: str
    summary: str
    trace: LifecycleTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class PromotionDecision:
    """Decision on whether a challenger should replace the champion."""

    schema_version: str
    generated_at: str
    controls: LifecycleControls
    action: str
    confidence: str
    reason_codes: list[str]
    selected_model_family: str | None
    selected_source: str
    next_step: str
    summary: str
    trace: LifecycleTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class RollbackDecision:
    """Decision on whether rollback should be prepared or executed."""

    schema_version: str
    generated_at: str
    controls: LifecycleControls
    action: str
    confidence: str
    reason_codes: list[str]
    rollback_target: str | None
    target_available: bool
    next_step: str
    summary: str
    trace: LifecycleTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class LifecycleBundle:
    """Full Slice 08 lifecycle bundle."""

    champion_vs_candidate: ChampionVsCandidate
    recalibration_decision: RecalibrationDecision
    retrain_decision: RetrainDecision
    promotion_decision: PromotionDecision
    rollback_decision: RollbackDecision

    def to_dict(self) -> dict[str, Any]:
        return {
            "champion_vs_candidate": self.champion_vs_candidate.to_dict(),
            "recalibration_decision": self.recalibration_decision.to_dict(),
            "retrain_decision": self.retrain_decision.to_dict(),
            "promotion_decision": self.promotion_decision.to_dict(),
            "rollback_decision": self.rollback_decision.to_dict(),
        }


def build_lifecycle_controls_from_policy(policy: dict[str, Any]) -> LifecycleControls:
    """Derive lifecycle controls from the canonical policy payload."""
    lifecycle_cfg = dict(policy.get("lifecycle", {}))
    intelligence_cfg = dict(policy.get("intelligence", {}))
    return LifecycleControls(
        enabled=True,
        recalibration_only_allowed=bool(lifecycle_cfg.get("recalibration_only_allowed", True)),
        rollback_allowed=bool(lifecycle_cfg.get("rollback_allowed", True)),
        champion_candidate_registry_enabled=bool(lifecycle_cfg.get("champion_candidate_registry_enabled", False)),
        prefer_current_batch_behavior=True,
        allow_uncertainty_adapter=bool(intelligence_cfg.get("enabled", True)),
        allow_monitoring_adapter=True,
        allow_registry_export=False,
        allow_observability_export=False,
    )
