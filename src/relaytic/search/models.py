"""Typed artifact models for Slice 13 search-controller artifacts."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from relaytic.core.search_budget_profiles import get_search_budget_profile, resolve_search_budget_profile


SEARCH_CONTROLS_SCHEMA_VERSION = "relaytic.search_controls.v1"
SEARCH_CONTROLLER_PLAN_SCHEMA_VERSION = "relaytic.search_controller_plan.v1"
PORTFOLIO_SEARCH_TRACE_SCHEMA_VERSION = "relaytic.portfolio_search_trace.v1"
HPO_CAMPAIGN_REPORT_SCHEMA_VERSION = "relaytic.hpo_campaign_report.v1"
SEARCH_DECISION_LEDGER_SCHEMA_VERSION = "relaytic.search_decision_ledger.v1"
EXECUTION_BACKEND_PROFILE_SCHEMA_VERSION = "relaytic.execution_backend_profile.v1"
DEVICE_ALLOCATION_SCHEMA_VERSION = "relaytic.device_allocation.v1"
DISTRIBUTED_RUN_PLAN_SCHEMA_VERSION = "relaytic.distributed_run_plan.v1"
SCHEDULER_JOB_MAP_SCHEMA_VERSION = "relaytic.scheduler_job_map.v1"
CHECKPOINT_STATE_SCHEMA_VERSION = "relaytic.checkpoint_state.v1"
EXECUTION_STRATEGY_REPORT_SCHEMA_VERSION = "relaytic.execution_strategy_report.v1"
SEARCH_VALUE_REPORT_SCHEMA_VERSION = "relaytic.search_value_report.v1"
SEARCH_CONTROLLER_EVAL_REPORT_SCHEMA_VERSION = "relaytic.search_controller_eval_report.v1"
SEARCH_BUDGET_ENVELOPE_SCHEMA_VERSION = "relaytic.search_budget_envelope.v1"
PROBE_STAGE_REPORT_SCHEMA_VERSION = "relaytic.probe_stage_report.v1"
FAMILY_RACE_REPORT_SCHEMA_VERSION = "relaytic.family_race_report.v1"
FINALIST_SEARCH_PLAN_SCHEMA_VERSION = "relaytic.finalist_search_plan.v1"
MULTI_FIDELITY_PRUNING_REPORT_SCHEMA_VERSION = "relaytic.multi_fidelity_pruning_report.v1"
PORTFOLIO_SEARCH_SCORECARD_SCHEMA_VERSION = "relaytic.portfolio_search_scorecard.v1"
SEARCH_STOP_REASON_SCHEMA_VERSION = "relaytic.search_stop_reason.v1"


@dataclass(frozen=True)
class SearchControls:
    schema_version: str = SEARCH_CONTROLS_SCHEMA_VERSION
    enabled: bool = True
    budget_profile: str = "operator"
    max_search_branches: int = 4
    max_branch_widen: int = 2
    low_value_threshold: float = 0.38
    high_value_threshold: float = 0.62
    light_hpo_trials: int = 8
    medium_hpo_trials: int = 24
    deep_hpo_trials: int = 48
    probe_trials_per_family: int = 2
    race_trials_per_family: int = 4
    finalist_followup_trials: int = 8
    post_fit_trials: int = 4
    max_trials: int = 200
    max_parallel_trials: int = 4
    execution_profile: str = "auto"
    distributed_local_allowed: bool = False
    scheduler_allowed: bool = False
    checkpoint_required_for_distributed_runs: bool = True
    allow_abstention: bool = True

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class SearchTrace:
    agent: str
    operating_mode: str
    llm_used: bool
    llm_status: str
    deterministic_evidence: list[str] = field(default_factory=list)
    advisory_notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class SearchControllerPlanArtifact:
    schema_version: str
    generated_at: str
    controls: SearchControls
    status: str
    workspace_id: str | None
    run_id: str
    recommended_action: str
    recommended_direction: str
    search_mode: str
    selected_hpo_depth: str
    planned_trial_count: int
    selected_execution_profile: str
    branch_budget: int
    widened_branch_ids: list[str]
    pruned_branch_ids: list[str]
    candidate_branches: list[dict[str, Any]]
    summary: str
    trace: SearchTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class PortfolioSearchTraceArtifact:
    schema_version: str
    generated_at: str
    controls: SearchControls
    status: str
    workspace_id: str | None
    run_id: str
    candidate_count: int
    widened_branch_count: int
    pruned_branch_count: int
    candidate_branches: list[dict[str, Any]]
    summary: str
    trace: SearchTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class HpoCampaignReportArtifact:
    schema_version: str
    generated_at: str
    controls: SearchControls
    status: str
    workspace_id: str | None
    run_id: str
    selected_depth: str
    planned_trials: int
    max_trials: int
    max_parallel_trials: int
    campaign_branches: list[dict[str, Any]]
    stop_search_explicit: bool
    summary: str
    trace: SearchTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class SearchDecisionLedgerArtifact:
    schema_version: str
    generated_at: str
    controls: SearchControls
    status: str
    workspace_id: str | None
    run_id: str
    entries: list[dict[str, Any]]
    summary: str
    trace: SearchTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class ExecutionBackendProfileArtifact:
    schema_version: str
    generated_at: str
    controls: SearchControls
    status: str
    selected_profile: str
    profile_candidates: list[str]
    distributed_local_allowed: bool
    scheduler_allowed: bool
    summary: str
    trace: SearchTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class DeviceAllocationArtifact:
    schema_version: str
    generated_at: str
    controls: SearchControls
    status: str
    selected_profile: str
    accelerator: str
    cpu_workers: int
    job_count: int
    notes: list[str]
    summary: str
    trace: SearchTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class DistributedRunPlanArtifact:
    schema_version: str
    generated_at: str
    controls: SearchControls
    status: str
    execution_mode: str
    resume_supported: bool
    job_count: int
    jobs: list[dict[str, Any]]
    summary: str
    trace: SearchTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class SchedulerJobMapArtifact:
    schema_version: str
    generated_at: str
    controls: SearchControls
    status: str
    jobs: list[dict[str, Any]]
    summary: str
    trace: SearchTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class CheckpointStateArtifact:
    schema_version: str
    generated_at: str
    controls: SearchControls
    status: str
    checkpoint_dir: str
    checkpoint_count: int
    resume_ready: bool
    latest_checkpoint: str | None
    summary: str
    trace: SearchTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class ExecutionStrategyReportArtifact:
    schema_version: str
    generated_at: str
    controls: SearchControls
    status: str
    selected_strategy: str
    selected_profile: str
    same_plan_profiles: list[str]
    same_plan_across_profiles: bool
    summary: str
    trace: SearchTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class SearchValueReportArtifact:
    schema_version: str
    generated_at: str
    controls: SearchControls
    status: str
    workspace_id: str | None
    run_id: str
    value_score: float
    value_band: str
    recommended_action: str
    recommended_direction: str
    stop_search_explicit: bool
    beat_target_pressure: str
    review_need: str
    reasons: list[str]
    summary: str
    trace: SearchTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class SearchControllerEvalReportArtifact:
    schema_version: str
    generated_at: str
    controls: SearchControls
    status: str
    failed_count: int
    proofs: list[dict[str, Any]]
    summary: str
    trace: SearchTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class SearchBudgetEnvelopeArtifact:
    schema_version: str
    generated_at: str
    controls: SearchControls
    status: str
    workspace_id: str | None
    run_id: str
    selected_hpo_depth: str
    remaining_trial_budget: int
    planned_trial_count: int
    probe_trials_per_family: int
    race_trials_per_family: int
    finalist_followup_trials: int
    post_fit_trials: int
    skipped_deeper_work: list[str]
    summary: str
    trace: SearchTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class ProbeStageReportArtifact:
    schema_version: str
    generated_at: str
    controls: SearchControls
    status: str
    workspace_id: str | None
    run_id: str
    candidate_families: list[dict[str, Any]]
    promoted_families: list[str]
    skipped_families: list[str]
    summary: str
    trace: SearchTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class FamilyRaceReportArtifact:
    schema_version: str
    generated_at: str
    controls: SearchControls
    status: str
    workspace_id: str | None
    run_id: str
    racing_families: list[dict[str, Any]]
    finalists: list[str]
    summary: str
    trace: SearchTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class FinalistSearchPlanArtifact:
    schema_version: str
    generated_at: str
    controls: SearchControls
    status: str
    workspace_id: str | None
    run_id: str
    finalists: list[dict[str, Any]]
    calibration_budget: int
    skipped_work: list[str]
    summary: str
    trace: SearchTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class MultiFidelityPruningReportArtifact:
    schema_version: str
    generated_at: str
    controls: SearchControls
    status: str
    workspace_id: str | None
    run_id: str
    pruned_families: list[dict[str, Any]]
    summary: str
    trace: SearchTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class PortfolioSearchScorecardArtifact:
    schema_version: str
    generated_at: str
    controls: SearchControls
    status: str
    workspace_id: str | None
    run_id: str
    probe_family_count: int
    race_family_count: int
    finalist_count: int
    skipped_deeper_work_count: int
    summary: str
    trace: SearchTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class SearchStopReasonArtifact:
    schema_version: str
    generated_at: str
    controls: SearchControls
    status: str
    workspace_id: str | None
    run_id: str
    stop_reason: str
    reason_kind: str
    search_stopped: bool
    detail: str
    summary: str
    trace: SearchTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class SearchBundle:
    search_controller_plan: SearchControllerPlanArtifact
    portfolio_search_trace: PortfolioSearchTraceArtifact
    hpo_campaign_report: HpoCampaignReportArtifact
    search_decision_ledger: SearchDecisionLedgerArtifact
    execution_backend_profile: ExecutionBackendProfileArtifact
    device_allocation: DeviceAllocationArtifact
    distributed_run_plan: DistributedRunPlanArtifact
    scheduler_job_map: SchedulerJobMapArtifact
    checkpoint_state: CheckpointStateArtifact
    execution_strategy_report: ExecutionStrategyReportArtifact
    search_value_report: SearchValueReportArtifact
    search_controller_eval_report: SearchControllerEvalReportArtifact
    search_budget_envelope: SearchBudgetEnvelopeArtifact
    probe_stage_report: ProbeStageReportArtifact
    family_race_report: FamilyRaceReportArtifact
    finalist_search_plan: FinalistSearchPlanArtifact
    multi_fidelity_pruning_report: MultiFidelityPruningReportArtifact
    portfolio_search_scorecard: PortfolioSearchScorecardArtifact
    search_stop_reason: SearchStopReasonArtifact

    def to_dict(self) -> dict[str, Any]:
        return {
            "search_controller_plan": self.search_controller_plan.to_dict(),
            "portfolio_search_trace": self.portfolio_search_trace.to_dict(),
            "hpo_campaign_report": self.hpo_campaign_report.to_dict(),
            "search_decision_ledger": self.search_decision_ledger.to_dict(),
            "execution_backend_profile": self.execution_backend_profile.to_dict(),
            "device_allocation": self.device_allocation.to_dict(),
            "distributed_run_plan": self.distributed_run_plan.to_dict(),
            "scheduler_job_map": self.scheduler_job_map.to_dict(),
            "checkpoint_state": self.checkpoint_state.to_dict(),
            "execution_strategy_report": self.execution_strategy_report.to_dict(),
            "search_value_report": self.search_value_report.to_dict(),
            "search_controller_eval_report": self.search_controller_eval_report.to_dict(),
            "search_budget_envelope": self.search_budget_envelope.to_dict(),
            "probe_stage_report": self.probe_stage_report.to_dict(),
            "family_race_report": self.family_race_report.to_dict(),
            "finalist_search_plan": self.finalist_search_plan.to_dict(),
            "multi_fidelity_pruning_report": self.multi_fidelity_pruning_report.to_dict(),
            "portfolio_search_scorecard": self.portfolio_search_scorecard.to_dict(),
            "search_stop_reason": self.search_stop_reason.to_dict(),
        }


def build_search_controls_from_policy(policy: dict[str, Any] | None) -> SearchControls:
    payload = dict(policy or {})
    search_cfg = dict(payload.get("search", {}))
    compute_cfg = dict(payload.get("compute", {}))
    autonomy_cfg = dict(payload.get("autonomy", {}))
    constraints_cfg = dict(payload.get("constraints", {}))
    budget_profile = resolve_search_budget_profile(payload)
    profile_defaults = get_search_budget_profile(budget_profile)
    max_search_branches = _bounded_int(
        search_cfg.get(
            "max_search_branches",
            max(int(profile_defaults["max_search_branches"]), int(autonomy_cfg.get("max_branches_per_round", 2) or 2) + 1),
        ),
        default=4,
        minimum=2,
        maximum=8,
    )
    max_branch_widen = _bounded_int(
        search_cfg.get("max_branch_widen", profile_defaults["max_branch_widen"]),
        default=2,
        minimum=1,
        maximum=max_search_branches,
    )
    max_trials = _bounded_int(
        compute_cfg.get("max_trials", profile_defaults["max_trials"]),
        default=int(profile_defaults["max_trials"]),
        minimum=4,
        maximum=2000,
    )
    light_trials = min(
        max_trials,
        _bounded_int(
            search_cfg.get("light_hpo_trials", profile_defaults["light_hpo_trials"]),
            default=int(profile_defaults["light_hpo_trials"]),
            minimum=2,
            maximum=max_trials,
        ),
    )
    medium_trials = min(
        max_trials,
        _bounded_int(
            search_cfg.get("medium_hpo_trials", profile_defaults["medium_hpo_trials"]),
            default=int(profile_defaults["medium_hpo_trials"]),
            minimum=light_trials,
            maximum=max_trials,
        ),
    )
    deep_trials = min(
        max_trials,
        _bounded_int(
            search_cfg.get("deep_hpo_trials", profile_defaults["deep_hpo_trials"]),
            default=int(profile_defaults["deep_hpo_trials"]),
            minimum=medium_trials,
            maximum=max_trials,
        ),
    )
    return SearchControls(
        enabled=bool(search_cfg.get("enabled", True)),
        budget_profile=budget_profile,
        max_search_branches=max_search_branches,
        max_branch_widen=max_branch_widen,
        low_value_threshold=_bounded_float(search_cfg.get("low_value_threshold", 0.38), default=0.38),
        high_value_threshold=_bounded_float(search_cfg.get("high_value_threshold", 0.62), default=0.62),
        light_hpo_trials=light_trials,
        medium_hpo_trials=medium_trials,
        deep_hpo_trials=deep_trials,
        probe_trials_per_family=_bounded_int(
            search_cfg.get("probe_trials_per_family", profile_defaults["probe_trials_per_family"]),
            default=int(profile_defaults["probe_trials_per_family"]),
            minimum=1,
            maximum=max(1, light_trials),
        ),
        race_trials_per_family=_bounded_int(
            search_cfg.get("race_trials_per_family", profile_defaults["race_trials_per_family"]),
            default=int(profile_defaults["race_trials_per_family"]),
            minimum=1,
            maximum=max(1, medium_trials),
        ),
        finalist_followup_trials=_bounded_int(
            search_cfg.get("finalist_followup_trials", profile_defaults["finalist_followup_trials"]),
            default=int(profile_defaults["finalist_followup_trials"]),
            minimum=1,
            maximum=max(1, deep_trials),
        ),
        post_fit_trials=_bounded_int(
            search_cfg.get("post_fit_trials", profile_defaults["post_fit_trials"]),
            default=int(profile_defaults["post_fit_trials"]),
            minimum=1,
            maximum=max(1, deep_trials),
        ),
        max_trials=max_trials,
        max_parallel_trials=_bounded_int(compute_cfg.get("max_parallel_trials", 4), default=4, minimum=1, maximum=32),
        execution_profile=str(compute_cfg.get("execution_profile", "auto") or "auto"),
        distributed_local_allowed=bool(compute_cfg.get("distributed_local_allowed", False)),
        scheduler_allowed=bool(compute_cfg.get("scheduler_allowed", False)),
        checkpoint_required_for_distributed_runs=bool(compute_cfg.get("checkpoint_required_for_distributed_runs", True)),
        allow_abstention=bool(constraints_cfg.get("abstention_allowed", True)),
    )


def _bounded_int(value: Any, *, default: int, minimum: int, maximum: int) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        parsed = default
    return max(minimum, min(maximum, parsed))


def _bounded_float(value: Any, *, default: float) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        parsed = default
    return max(0.0, min(1.0, parsed))
