"""Typed artifact models for Slice 09C bounded autonomy loops."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


AUTONOMY_CONTROLS_SCHEMA_VERSION = "relaytic.autonomy_controls.v1"
AUTONOMY_LOOP_STATE_SCHEMA_VERSION = "relaytic.autonomy_loop_state.v1"
AUTONOMY_ROUND_REPORT_SCHEMA_VERSION = "relaytic.autonomy_round_report.v1"
CHALLENGER_QUEUE_SCHEMA_VERSION = "relaytic.challenger_queue.v1"
BRANCH_OUTCOME_MATRIX_SCHEMA_VERSION = "relaytic.branch_outcome_matrix.v1"
RETRAIN_RUN_REQUEST_SCHEMA_VERSION = "relaytic.retrain_run_request.v1"
RECALIBRATION_RUN_REQUEST_SCHEMA_VERSION = "relaytic.recalibration_run_request.v1"
CHAMPION_LINEAGE_SCHEMA_VERSION = "relaytic.champion_lineage.v1"
LOOP_BUDGET_REPORT_SCHEMA_VERSION = "relaytic.loop_budget_report.v1"


@dataclass(frozen=True)
class AutonomyControls:
    schema_version: str = AUTONOMY_CONTROLS_SCHEMA_VERSION
    enabled: bool = True
    allow_auto_run: bool = True
    max_followup_rounds: int = 1
    max_branches_per_round: int = 2
    min_relative_improvement: float = 0.02
    allow_architecture_switch: bool = True
    allow_feature_set_expansion: bool = True
    suggest_more_data_when_stalled: bool = True

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class AutonomyTrace:
    agent: str
    operating_mode: str
    llm_used: bool
    llm_status: str
    deterministic_evidence: list[str] = field(default_factory=list)
    advisory_notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class AutonomyLoopState:
    schema_version: str
    generated_at: str
    controls: AutonomyControls
    status: str
    current_round: int
    max_rounds: int
    selected_action: str
    promotion_applied: bool
    stopped_reason: str
    summary: str
    trace: AutonomyTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class AutonomyRoundReport:
    schema_version: str
    generated_at: str
    controls: AutonomyControls
    round_index: int
    selected_action: str
    promoted_branch_id: str | None
    local_data_candidates: list[dict[str, Any]]
    summary: str
    trace: AutonomyTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class ChallengerQueue:
    schema_version: str
    generated_at: str
    controls: AutonomyControls
    selected_action: str
    branches: list[dict[str, Any]]
    summary: str
    trace: AutonomyTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class BranchOutcomeMatrix:
    schema_version: str
    generated_at: str
    controls: AutonomyControls
    selected_action: str
    primary_metric: str
    baseline_metric_value: float | None
    branches: list[dict[str, Any]]
    winning_branch_id: str | None
    promotion_applied: bool
    summary: str
    trace: AutonomyTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class RetrainRunRequest:
    schema_version: str
    generated_at: str
    controls: AutonomyControls
    requested: bool
    data_path: str | None
    requested_model_family: str | None
    threshold_policy: str | None
    reason_codes: list[str]
    summary: str
    trace: AutonomyTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class RecalibrationRunRequest:
    schema_version: str
    generated_at: str
    controls: AutonomyControls
    requested: bool
    requested_model_family: str | None
    threshold_policy: str | None
    reason_codes: list[str]
    summary: str
    trace: AutonomyTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class ChampionLineage:
    schema_version: str
    generated_at: str
    controls: AutonomyControls
    current_model_family: str | None
    lineage: list[dict[str, Any]]
    summary: str
    trace: AutonomyTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class LoopBudgetReport:
    schema_version: str
    generated_at: str
    controls: AutonomyControls
    max_rounds: int
    used_rounds: int
    max_branches_per_round: int
    used_branches: int
    budget_remaining: int
    summary: str
    trace: AutonomyTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class AutonomyBundle:
    autonomy_loop_state: AutonomyLoopState
    autonomy_round_report: AutonomyRoundReport
    challenger_queue: ChallengerQueue
    branch_outcome_matrix: BranchOutcomeMatrix
    retrain_run_request: RetrainRunRequest
    recalibration_run_request: RecalibrationRunRequest
    champion_lineage: ChampionLineage
    loop_budget_report: LoopBudgetReport

    def to_dict(self) -> dict[str, Any]:
        return {
            "autonomy_loop_state": self.autonomy_loop_state.to_dict(),
            "autonomy_round_report": self.autonomy_round_report.to_dict(),
            "challenger_queue": self.challenger_queue.to_dict(),
            "branch_outcome_matrix": self.branch_outcome_matrix.to_dict(),
            "retrain_run_request": self.retrain_run_request.to_dict(),
            "recalibration_run_request": self.recalibration_run_request.to_dict(),
            "champion_lineage": self.champion_lineage.to_dict(),
            "loop_budget_report": self.loop_budget_report.to_dict(),
        }


def build_autonomy_controls_from_policy(policy: dict[str, Any]) -> AutonomyControls:
    """Derive autonomy-loop controls from the canonical policy payload."""

    autonomy_cfg = dict(policy.get("autonomy", {}))
    try:
        max_followup_rounds = int(autonomy_cfg.get("max_followup_rounds", 1) or 1)
    except (TypeError, ValueError):
        max_followup_rounds = 1
    try:
        min_relative_improvement = float(autonomy_cfg.get("min_relative_improvement", 0.02) or 0.02)
    except (TypeError, ValueError):
        min_relative_improvement = 0.02
    return AutonomyControls(
        enabled=bool(autonomy_cfg.get("allow_auto_run", True)),
        allow_auto_run=bool(autonomy_cfg.get("allow_auto_run", True)),
        max_followup_rounds=max(1, min(3, max_followup_rounds)),
        max_branches_per_round=max(1, min(4, int(autonomy_cfg.get("max_branches_per_round", 2) or 2))),
        min_relative_improvement=max(0.0, min(0.50, min_relative_improvement)),
        allow_architecture_switch=bool(autonomy_cfg.get("allow_architecture_switch", True)),
        allow_feature_set_expansion=bool(autonomy_cfg.get("allow_feature_set_expansion", True)),
        suggest_more_data_when_stalled=bool(autonomy_cfg.get("suggest_more_data_when_stalled", True)),
    )
