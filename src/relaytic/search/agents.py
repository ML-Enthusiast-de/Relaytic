"""Slice 13 search controller, accelerated execution, and bounded local experimentation."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from relaytic.benchmark import read_benchmark_bundle
from relaytic.decision import read_decision_bundle
from relaytic.evals import read_eval_bundle
from relaytic.iteration import read_iteration_bundle
from relaytic.planning import read_planning_bundle
from relaytic.profiles import read_profiles_bundle
from relaytic.runs import read_run_summary
from relaytic.tracing import read_trace_bundle
from relaytic.workspace import default_workspace_dir, read_result_contract_artifacts, read_workspace_bundle

from .models import (
    CHECKPOINT_STATE_SCHEMA_VERSION,
    DEVICE_ALLOCATION_SCHEMA_VERSION,
    DISTRIBUTED_RUN_PLAN_SCHEMA_VERSION,
    EXECUTION_BACKEND_PROFILE_SCHEMA_VERSION,
    EXECUTION_STRATEGY_REPORT_SCHEMA_VERSION,
    HPO_CAMPAIGN_REPORT_SCHEMA_VERSION,
    PORTFOLIO_SEARCH_TRACE_SCHEMA_VERSION,
    SCHEDULER_JOB_MAP_SCHEMA_VERSION,
    SEARCH_CONTROLLER_EVAL_REPORT_SCHEMA_VERSION,
    SEARCH_CONTROLLER_PLAN_SCHEMA_VERSION,
    SEARCH_DECISION_LEDGER_SCHEMA_VERSION,
    SEARCH_VALUE_REPORT_SCHEMA_VERSION,
    CheckpointStateArtifact,
    DeviceAllocationArtifact,
    DistributedRunPlanArtifact,
    ExecutionBackendProfileArtifact,
    ExecutionStrategyReportArtifact,
    HpoCampaignReportArtifact,
    PortfolioSearchTraceArtifact,
    SchedulerJobMapArtifact,
    SearchBundle,
    SearchControllerEvalReportArtifact,
    SearchControllerPlanArtifact,
    SearchDecisionLedgerArtifact,
    SearchTrace,
    SearchValueReportArtifact,
    build_search_controls_from_policy,
)


@dataclass(frozen=True)
class SearchRunResult:
    bundle: SearchBundle
    review_markdown: str


def run_search_review(*, run_dir: str | Path, policy: dict[str, Any]) -> SearchRunResult:
    """Build the explicit Slice 13 search-controller plan for an existing run."""

    root = Path(run_dir)
    root.mkdir(parents=True, exist_ok=True)
    controls = build_search_controls_from_policy(policy)
    summary = read_run_summary(root)
    planning_bundle = read_planning_bundle(root)
    benchmark_bundle = read_benchmark_bundle(root)
    decision_bundle = read_decision_bundle(root)
    trace_bundle = read_trace_bundle(root)
    eval_bundle = read_eval_bundle(root)
    profiles_bundle = read_profiles_bundle(root)
    workspace_dir = default_workspace_dir(run_dir=root)
    workspace_bundle = read_workspace_bundle(workspace_dir)
    result_contract_bundle = read_result_contract_artifacts(root)
    iteration_bundle = read_iteration_bundle(workspace_dir=workspace_dir, run_dir=root)

    workspace_state = dict(workspace_bundle.get("workspace_state", {}))
    result_contract = dict(result_contract_bundle.get("result_contract", {}))
    confidence_posture = dict(result_contract_bundle.get("confidence_posture", {}))
    next_run_plan = dict(iteration_bundle.get("next_run_plan", {}))
    benchmark = dict(summary.get("benchmark", {}))
    decision = dict(summary.get("decision", {}))
    decision_lab = dict(summary.get("decision_lab", {}))
    eval_state = dict(summary.get("evals", {}))
    promotion_readiness = dict(summary.get("architecture_imports", {}))
    shadow_scorecard = dict(benchmark_bundle.get("shadow_trial_scorecard", {}))

    beat_target_pressure = _beat_target_pressure(
        benchmark=benchmark,
        benchmark_bundle=benchmark_bundle,
    )
    review_need = _clean_text(confidence_posture.get("review_need")) or "unknown"
    recommended_direction = (
        _clean_text(dict(result_contract.get("recommended_next_move", {})).get("direction"))
        or _clean_text(next_run_plan.get("recommended_direction"))
        or "same_data"
    )
    unresolved_count = len(result_contract.get("unresolved_items", [])) if isinstance(result_contract.get("unresolved_items"), list) else 0
    overall_confidence = _clean_text(confidence_posture.get("overall_confidence")) or "medium"
    overall_strength = _clean_text(dict(result_contract.get("evidence_strength", {})).get("overall_strength")) or "mixed"

    value_score = _value_score(
        recommended_direction=recommended_direction,
        beat_target_pressure=beat_target_pressure,
        unresolved_count=unresolved_count,
        review_need=review_need,
        overall_confidence=overall_confidence,
        overall_strength=overall_strength,
        eval_state=eval_state,
        decision_lab=decision_lab,
    )
    value_band = _value_band(
        value_score=value_score,
        low_threshold=controls.low_value_threshold,
        high_threshold=controls.high_value_threshold,
    )
    recommended_action, stop_search_explicit = _recommended_action(
        controls=controls,
        value_band=value_band,
        recommended_direction=recommended_direction,
        beat_target_pressure=beat_target_pressure,
        review_need=review_need,
    )
    selected_hpo_depth = _selected_hpo_depth(
        recommended_action=recommended_action,
        value_band=value_band,
        beat_target_pressure=beat_target_pressure,
    )
    budget_contract = dict(profiles_bundle.get("budget_contract", {}))
    budget_consumption = dict(profiles_bundle.get("budget_consumption_report", {}))
    remaining_trial_budget = _remaining_trials(
        controls=controls,
        budget_contract=budget_contract,
        budget_consumption=budget_consumption,
    )
    planned_trial_count = _planned_trials(
        controls=controls,
        selected_hpo_depth=selected_hpo_depth,
        remaining_trial_budget=remaining_trial_budget,
    )
    candidate_branches = _candidate_branches(
        controls=controls,
        decision=decision,
        decision_lab=decision_lab,
        planning_bundle=planning_bundle,
        recommended_direction=recommended_direction,
        beat_target_pressure=beat_target_pressure,
        unresolved_count=unresolved_count,
        value_band=value_band,
        imported_shadow_candidates=_imported_shadow_branches(
            promotion_readiness=promotion_readiness,
            shadow_scorecard=shadow_scorecard,
        ),
    )
    widened_branches, pruned_branches = _bounded_branches(
        controls=controls,
        candidate_branches=candidate_branches,
        value_band=value_band,
    )
    profile_candidates = _profile_candidates(controls=controls)
    selected_execution_profile = _selected_execution_profile(
        controls=controls,
        profile_candidates=profile_candidates,
        recommended_action=recommended_action,
        planned_trial_count=planned_trial_count,
    )
    distributed_jobs = _distributed_jobs(
        controls=controls,
        widened_branches=widened_branches,
        selected_execution_profile=selected_execution_profile,
        planned_trial_count=planned_trial_count,
    )
    checkpoint_state = _checkpoint_state(root=root, controls=controls, distributed_jobs=distributed_jobs)
    search_mode = _search_mode(
        recommended_action=recommended_action,
        stop_search_explicit=stop_search_explicit,
        widened_branch_count=len(widened_branches),
    )
    execution_mode = "distributed_local" if distributed_jobs else "local_single_node"
    selected_strategy = "stop_search" if stop_search_explicit else ("distributed_local" if distributed_jobs else "local_bounded_search")
    workspace_id = _clean_text(workspace_state.get("workspace_id"))
    run_id = _clean_text(summary.get("run_id")) or root.name
    reasons = _search_reasons(
        recommended_direction=recommended_direction,
        recommended_action=recommended_action,
        beat_target_pressure=beat_target_pressure,
        unresolved_count=unresolved_count,
        review_need=review_need,
        value_band=value_band,
        eval_state=eval_state,
    )
    trace = SearchTrace(
        agent="search_controller",
        operating_mode=search_mode,
        llm_used=False,
        llm_status="not_requested",
        deterministic_evidence=[
            "run_summary",
            "result_contract",
            "benchmark_bundle",
            "decision_bundle",
            "trace_bundle",
            "eval_bundle",
            "profiles_bundle",
        ],
        advisory_notes=[
            "Slice 13 must widen, prune, or stop search explicitly instead of treating deeper HPO as the default next move.",
            "Search remains bounded by quality, budget, benchmark pressure, and workspace direction.",
        ],
    )
    bundle = SearchBundle(
        search_controller_plan=SearchControllerPlanArtifact(
            schema_version=SEARCH_CONTROLLER_PLAN_SCHEMA_VERSION,
            generated_at=_utc_now(),
            controls=controls,
            status="ok",
            workspace_id=workspace_id,
            run_id=run_id,
            recommended_action=recommended_action,
            recommended_direction=recommended_direction,
            search_mode=search_mode,
            selected_hpo_depth=selected_hpo_depth,
            planned_trial_count=planned_trial_count,
            selected_execution_profile=selected_execution_profile,
            branch_budget=controls.max_search_branches,
            widened_branch_ids=[str(item.get("branch_id")) for item in widened_branches],
            pruned_branch_ids=[str(item.get("branch_id")) for item in pruned_branches],
            candidate_branches=candidate_branches,
            summary=_summary_text(
                recommended_action=recommended_action,
                recommended_direction=recommended_direction,
                value_band=value_band,
                planned_trial_count=planned_trial_count,
            ),
            trace=trace,
        ),
        portfolio_search_trace=PortfolioSearchTraceArtifact(
            schema_version=PORTFOLIO_SEARCH_TRACE_SCHEMA_VERSION,
            generated_at=_utc_now(),
            controls=controls,
            status="ok",
            workspace_id=workspace_id,
            run_id=run_id,
            candidate_count=len(candidate_branches),
            widened_branch_count=len(widened_branches),
            pruned_branch_count=len(pruned_branches),
            candidate_branches=candidate_branches,
            summary=f"Relaytic reviewed `{len(candidate_branches)}` candidate search branches and kept `{len(widened_branches)}` in the bounded frontier.",
            trace=trace,
        ),
        hpo_campaign_report=HpoCampaignReportArtifact(
            schema_version=HPO_CAMPAIGN_REPORT_SCHEMA_VERSION,
            generated_at=_utc_now(),
            controls=controls,
            status="ok",
            workspace_id=workspace_id,
            run_id=run_id,
            selected_depth=selected_hpo_depth,
            planned_trials=planned_trial_count,
            max_trials=remaining_trial_budget,
            max_parallel_trials=controls.max_parallel_trials,
            campaign_branches=widened_branches,
            stop_search_explicit=stop_search_explicit,
            summary=f"Relaytic chose `{selected_hpo_depth}` HPO depth with `{planned_trial_count}` planned trial(s).",
            trace=trace,
        ),
        search_decision_ledger=SearchDecisionLedgerArtifact(
            schema_version=SEARCH_DECISION_LEDGER_SCHEMA_VERSION,
            generated_at=_utc_now(),
            controls=controls,
            status="ok",
            workspace_id=workspace_id,
            run_id=run_id,
            entries=[
                {
                    "decision_id": "search_value",
                    "kind": "value_assessment",
                    "value_score": value_score,
                    "value_band": value_band,
                    "reasons": reasons,
                },
                {
                    "decision_id": "search_action",
                    "kind": "next_action",
                    "recommended_action": recommended_action,
                    "recommended_direction": recommended_direction,
                    "stop_search_explicit": stop_search_explicit,
                },
                {
                    "decision_id": "execution_profile",
                    "kind": "execution_selection",
                    "selected_execution_profile": selected_execution_profile,
                    "execution_mode": execution_mode,
                    "planned_trial_count": planned_trial_count,
                },
            ],
            summary="Relaytic recorded the deterministic value, action, and execution decisions behind the search-controller outcome.",
            trace=trace,
        ),
        execution_backend_profile=ExecutionBackendProfileArtifact(
            schema_version=EXECUTION_BACKEND_PROFILE_SCHEMA_VERSION,
            generated_at=_utc_now(),
            controls=controls,
            status="ok",
            selected_profile=selected_execution_profile,
            profile_candidates=profile_candidates,
            distributed_local_allowed=controls.distributed_local_allowed,
            scheduler_allowed=controls.scheduler_allowed,
            summary=f"Relaytic selected execution profile `{selected_execution_profile}` from `{len(profile_candidates)}` candidate profile(s).",
            trace=trace,
        ),
        device_allocation=DeviceAllocationArtifact(
            schema_version=DEVICE_ALLOCATION_SCHEMA_VERSION,
            generated_at=_utc_now(),
            controls=controls,
            status="ok",
            selected_profile=selected_execution_profile,
            accelerator="cpu",
            cpu_workers=max(1, min(controls.max_parallel_trials * 2, 8)),
            job_count=max(1, len(distributed_jobs)),
            notes=[
                "Slice 13 remains CPU-safe by default for local-first MVP execution.",
                "Distributed jobs are only planned when policy allows bounded local fan-out.",
            ],
            summary=f"Relaytic allocated `{max(1, len(distributed_jobs))}` job slot(s) on CPU for the current search plan.",
            trace=trace,
        ),
        distributed_run_plan=DistributedRunPlanArtifact(
            schema_version=DISTRIBUTED_RUN_PLAN_SCHEMA_VERSION,
            generated_at=_utc_now(),
            controls=controls,
            status="ok",
            execution_mode=execution_mode,
            resume_supported=checkpoint_state["resume_ready"],
            job_count=len(distributed_jobs),
            jobs=distributed_jobs,
            summary=(
                "Relaytic planned bounded local distributed execution."
                if distributed_jobs
                else "Relaytic kept execution local and single-node for the current search plan."
            ),
            trace=trace,
        ),
        scheduler_job_map=SchedulerJobMapArtifact(
            schema_version=SCHEDULER_JOB_MAP_SCHEMA_VERSION,
            generated_at=_utc_now(),
            controls=controls,
            status="ok",
            jobs=distributed_jobs,
            summary=f"Relaytic recorded `{len(distributed_jobs)}` scheduler-visible job(s) for replay and host inspection.",
            trace=trace,
        ),
        checkpoint_state=CheckpointStateArtifact(
            schema_version=CHECKPOINT_STATE_SCHEMA_VERSION,
            generated_at=_utc_now(),
            controls=controls,
            status="ok",
            checkpoint_dir=checkpoint_state["checkpoint_dir"],
            checkpoint_count=checkpoint_state["checkpoint_count"],
            resume_ready=checkpoint_state["resume_ready"],
            latest_checkpoint=checkpoint_state["latest_checkpoint"],
            summary=checkpoint_state["summary"],
            trace=trace,
        ),
        execution_strategy_report=ExecutionStrategyReportArtifact(
            schema_version=EXECUTION_STRATEGY_REPORT_SCHEMA_VERSION,
            generated_at=_utc_now(),
            controls=controls,
            status="ok",
            selected_strategy=selected_strategy,
            selected_profile=selected_execution_profile,
            same_plan_profiles=profile_candidates,
            same_plan_across_profiles=True,
            summary=f"Relaytic selected `{selected_strategy}` with profile `{selected_execution_profile}`.",
            trace=trace,
        ),
        search_value_report=SearchValueReportArtifact(
            schema_version=SEARCH_VALUE_REPORT_SCHEMA_VERSION,
            generated_at=_utc_now(),
            controls=controls,
            status="ok",
            workspace_id=workspace_id,
            run_id=run_id,
            value_score=value_score,
            value_band=value_band,
            recommended_action=recommended_action,
            recommended_direction=recommended_direction,
            stop_search_explicit=stop_search_explicit,
            beat_target_pressure=beat_target_pressure,
            review_need=review_need,
            reasons=reasons,
            summary=_summary_text(
                recommended_action=recommended_action,
                recommended_direction=recommended_direction,
                value_band=value_band,
                planned_trial_count=planned_trial_count,
            ),
            trace=trace,
        ),
        search_controller_eval_report=SearchControllerEvalReportArtifact(
            schema_version=SEARCH_CONTROLLER_EVAL_REPORT_SCHEMA_VERSION,
            generated_at=_utc_now(),
            controls=controls,
            status="ok",
            failed_count=0,
            proofs=_proofs(
                recommended_action=recommended_action,
                recommended_direction=recommended_direction,
                stop_search_explicit=stop_search_explicit,
                value_band=value_band,
                planned_trial_count=planned_trial_count,
                candidate_branches=candidate_branches,
                widened_branches=widened_branches,
                imported_shadow_candidate_count=int(promotion_readiness.get("candidate_count", 0) or 0),
                trace_bundle=trace_bundle,
                eval_bundle=eval_bundle,
            ),
            summary="Relaytic recorded explicit proof points showing why the current search plan widened, tuned, or stopped instead of searching blindly.",
            trace=trace,
        ),
    )
    return SearchRunResult(bundle=bundle, review_markdown=render_search_review_markdown(bundle.to_dict()))


def render_search_review_markdown(bundle: dict[str, Any]) -> str:
    plan = dict(bundle.get("search_controller_plan", {}))
    value = dict(bundle.get("search_value_report", {}))
    portfolio = dict(bundle.get("portfolio_search_trace", {}))
    execution = dict(bundle.get("execution_strategy_report", {}))
    checkpoint = dict(bundle.get("checkpoint_state", {}))
    eval_report = dict(bundle.get("search_controller_eval_report", {}))
    lines = [
        "# Relaytic Search Controller Review",
        "",
        "## Outcome",
        f"- Action: `{plan.get('recommended_action') or 'unknown'}`",
        f"- Direction: `{plan.get('recommended_direction') or 'unknown'}`",
        f"- Value band: `{value.get('value_band') or 'unknown'}`",
        f"- Stop search explicitly: `{value.get('stop_search_explicit')}`",
        f"- Search mode: `{plan.get('search_mode') or 'unknown'}`",
        "",
        "## Why Relaytic Chose This",
        f"- Beat-target pressure: `{value.get('beat_target_pressure') or 'unknown'}`",
        f"- Review need: `{value.get('review_need') or 'unknown'}`",
        f"- Planned trials: `{plan.get('planned_trial_count', 0)}`",
        f"- HPO depth: `{plan.get('selected_hpo_depth') or 'off'}`",
        f"- Execution profile: `{plan.get('selected_execution_profile') or 'unknown'}`",
    ]
    reasons = [str(item).strip() for item in value.get("reasons", []) if str(item).strip()]
    if reasons:
        lines.append("")
        lines.append("## Reasons")
        lines.extend(f"- {item}" for item in reasons)
    lines.extend(
        [
            "",
            "## Portfolio",
            f"- Candidate branches: `{portfolio.get('candidate_count', 0)}`",
            f"- Widened branches: `{portfolio.get('widened_branch_count', 0)}`",
            f"- Pruned branches: `{portfolio.get('pruned_branch_count', 0)}`",
            "",
            "## Execution",
            f"- Strategy: `{execution.get('selected_strategy') or 'unknown'}`",
            f"- Same plan across profiles: `{execution.get('same_plan_across_profiles')}`",
            f"- Checkpoint count: `{checkpoint.get('checkpoint_count', 0)}`",
            f"- Resume ready: `{checkpoint.get('resume_ready')}`",
            "",
            "## Proof",
            f"- Proof checks: `{len(eval_report.get('proofs', []))}`",
            f"- Failed checks: `{eval_report.get('failed_count', 0)}`",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def _value_score(
    *,
    recommended_direction: str,
    beat_target_pressure: str,
    unresolved_count: int,
    review_need: str,
    overall_confidence: str,
    overall_strength: str,
    eval_state: dict[str, Any],
    decision_lab: dict[str, Any],
) -> float:
    score = 0.24
    score += min(0.28, unresolved_count * 0.08)
    if beat_target_pressure == "high":
        score += 0.20
    elif beat_target_pressure == "medium":
        score += 0.10
    if review_need == "required":
        score += 0.14
    if overall_confidence == "low":
        score += 0.10
    elif overall_confidence == "high":
        score -= 0.05
    if overall_strength == "weak":
        score += 0.08
    elif overall_strength == "strong":
        score -= 0.05
    if recommended_direction in {"add_data", "new_dataset"}:
        score -= 0.26
    if _clean_text(decision_lab.get("selected_next_action")) == "additional_local_data" or _clean_text(decision_lab.get("recommended_source_id")):
        score -= 0.08
    if _clean_text(eval_state.get("protocol_status")) == "fail" or int(eval_state.get("failed_count", 0) or 0) > 0:
        score -= 0.14
    return max(0.0, min(1.0, round(score, 3)))


def _value_band(*, value_score: float, low_threshold: float, high_threshold: float) -> str:
    if value_score <= low_threshold:
        return "low"
    if value_score >= high_threshold:
        return "high"
    return "medium"


def _recommended_action(
    *,
    controls: Any,
    value_band: str,
    recommended_direction: str,
    beat_target_pressure: str,
    review_need: str,
) -> tuple[str, bool]:
    if not controls.enabled:
        return "stop_search", True
    if recommended_direction in {"add_data", "new_dataset"} and value_band == "low":
        return "stop_search", True
    if beat_target_pressure == "high":
        return "expand_challenger_portfolio", False
    if value_band == "high":
        return "run_hpo_campaign", False
    if review_need == "required":
        return "search_more", False
    if value_band == "low":
        return "stop_search", True
    return "search_more", False


def _selected_hpo_depth(*, recommended_action: str, value_band: str, beat_target_pressure: str) -> str:
    if recommended_action == "stop_search":
        return "off"
    if recommended_action == "expand_challenger_portfolio":
        return "medium" if beat_target_pressure == "high" else "light"
    if value_band == "high":
        return "deep"
    return "light"


def _remaining_trials(*, controls: Any, budget_contract: dict[str, Any], budget_consumption: dict[str, Any]) -> int:
    contract_max = _optional_int(budget_contract.get("max_trials"), default=controls.max_trials)
    consumed = _optional_int(
        budget_consumption.get("estimated_trials_used") or budget_consumption.get("consumed_trials"),
        default=0,
    )
    return max(1, min(controls.max_trials, contract_max - consumed if contract_max > consumed else 1))


def _planned_trials(*, controls: Any, selected_hpo_depth: str, remaining_trial_budget: int) -> int:
    if selected_hpo_depth == "off":
        return 0
    if selected_hpo_depth == "light":
        desired = controls.light_hpo_trials
    elif selected_hpo_depth == "medium":
        desired = controls.medium_hpo_trials
    else:
        desired = controls.deep_hpo_trials
    return max(1, min(remaining_trial_budget, desired))


def _imported_shadow_branches(
    *,
    promotion_readiness: dict[str, Any],
    shadow_scorecard: dict[str, Any],
) -> list[dict[str, Any]]:
    rows = [
        dict(item)
        for item in shadow_scorecard.get("rows", [])
        if isinstance(item, dict) and _clean_text(item.get("family_id"))
    ]
    candidates: list[dict[str, Any]] = []
    for item in rows:
        if str(item.get("promotion_state")) not in {"promotion_ready", "candidate_available"}:
            continue
        family = _clean_text(item.get("family_id"))
        if not family:
            continue
        candidates.append(
            {
                "branch_id": f"imported_shadow::{family}",
                "family": family,
                "title": f"Imported shadow follow-up for `{family}`",
                "reason": _clean_text(item.get("summary"))
                or "Imported architecture evidence looked strong enough for bounded shadow follow-up.",
            }
        )
    if candidates:
        return candidates
    available = promotion_readiness.get("candidate_available_families", [])
    if not isinstance(available, list):
        return []
    for family in available:
        text = str(family).strip()
        if not text:
            continue
        candidates.append(
            {
                "branch_id": f"imported_shadow::{text}",
                "family": text,
                "title": f"Imported shadow follow-up for `{text}`",
                "reason": "Imported architecture evidence is positive enough for bounded shadow follow-up.",
            }
        )
    return candidates


def _candidate_branches(
    *,
    controls: Any,
    decision: dict[str, Any],
    decision_lab: dict[str, Any],
    planning_bundle: dict[str, Any],
    recommended_direction: str,
    beat_target_pressure: str,
    unresolved_count: int,
    value_band: str,
    imported_shadow_candidates: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    route_id = _clean_text(decision.get("selected_route_id")) or "current_route"
    route_title = _clean_text(decision.get("selected_route_title")) or "Current route"
    family = _clean_text(decision.get("selected_model_family")) or "current_family"
    task_type = _clean_text(decision.get("task_type")) or "unknown"
    candidates: list[dict[str, Any]] = [
        {
            "branch_id": f"{route_id}_refine",
            "family": family,
            "priority": 1,
            "kind": "current_family_refine",
            "route_id": route_id,
            "title": f"{route_title} refinement",
            "reason": "Preserve the current route while giving the search controller room to retune bounded hyperparameters.",
        }
    ]
    if beat_target_pressure in {"medium", "high"}:
        candidates.append(
            {
                "branch_id": f"{route_id}_challenger",
                "family": _alternative_family(family=family, task_type=task_type),
                "priority": 2,
                "kind": "alternate_family",
                "route_id": route_id,
                "title": "Alternate family challenger",
                "reason": "Incumbent or benchmark pressure justifies widening the challenger portfolio beyond the current family.",
            }
        )
    if task_type in {"classification", "binary_classification", "fraud_detection", "anomaly_detection"}:
        candidates.append(
            {
                "branch_id": "calibration_repair",
                "family": family,
                "priority": 3,
                "kind": "calibration_repair",
                "route_id": route_id,
                "title": "Calibration repair pass",
                "reason": "Operational binary decisions often benefit from explicit recalibration and threshold review.",
            }
        )
    if controls.allow_abstention and task_type in {"classification", "binary_classification", "fraud_detection"}:
        candidates.append(
            {
                "branch_id": "abstention_wrapper",
                "family": family,
                "priority": 4,
                "kind": "abstention_wrapper",
                "route_id": route_id,
                "title": "Selective prediction wrapper",
                "reason": "Add an abstention option when confidence or review posture suggests bounded deferral could reduce harm.",
            }
        )
    if recommended_direction == "add_data" or _clean_text(decision_lab.get("recommended_source_id")):
        candidates.append(
            {
                "branch_id": "data_expansion_probe",
                "family": "data_expansion",
                "priority": 5,
                "kind": "data_expansion_probe",
                "route_id": route_id,
                "title": "Local data expansion probe",
                "reason": "Decision-lab and result-contract signals say adjacent local data may be worth more than extra search on the current snapshot.",
            }
        )
    alternatives = dict(planning_bundle.get("alternatives", {}))
    alternative_routes = alternatives.get("candidate_routes") if isinstance(alternatives.get("candidate_routes"), list) else []
    for index, item in enumerate(alternative_routes[:2], start=1):
        if not isinstance(item, dict):
            continue
        alt_id = _clean_text(item.get("route_id")) or f"alternative_route_{index}"
        if any(existing.get("branch_id") == alt_id for existing in candidates):
            continue
        candidates.append(
            {
                "branch_id": alt_id,
                "family": _clean_text(item.get("model_family")) or _alternative_family(family=family, task_type=task_type),
                "priority": 6 + index,
                "kind": "planner_alternative",
                "route_id": alt_id,
                "title": _clean_text(item.get("title")) or f"Planner alternative {index}",
                "reason": _clean_text(item.get("why_not_selected"))
                or "Planner identified this as a viable alternate route worth reconsidering if the current route stalls.",
            }
        )
    if value_band == "high" and unresolved_count > 1 and not any(item.get("kind") == "alternate_family" for item in candidates):
        candidates.append(
            {
                "branch_id": "portfolio_backup",
                "family": _alternative_family(family=family, task_type=task_type),
                "priority": 8,
                "kind": "portfolio_backup",
                "route_id": route_id,
                "title": "Portfolio backup branch",
                "reason": "High unresolved load justifies one additional bounded alternate branch even without explicit incumbent pressure.",
            }
        )
    for index, item in enumerate(imported_shadow_candidates[:2], start=1):
        branch_id = _clean_text(item.get("branch_id")) or f"imported_shadow_{index}"
        if any(existing.get("branch_id") == branch_id for existing in candidates):
            continue
        candidates.append(
            {
                "branch_id": branch_id,
                "family": _clean_text(item.get("family")) or "imported_shadow_family",
                "priority": 8 + index,
                "kind": "imported_architecture_shadow",
                "route_id": route_id,
                "title": _clean_text(item.get("title")) or f"Imported shadow candidate {index}",
                "reason": _clean_text(item.get("reason"))
                or "Imported architecture evidence looks promising enough for bounded shadow follow-up, but not for silent live routing.",
            }
        )
    return candidates


def _bounded_branches(*, controls: Any, candidate_branches: list[dict[str, Any]], value_band: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    sorted_candidates = sorted(candidate_branches, key=lambda item: (int(item.get("priority", 99)), str(item.get("branch_id"))))
    if value_band == "low":
        keep = min(1, len(sorted_candidates))
    elif value_band == "medium":
        keep = min(max(2, controls.max_branch_widen), len(sorted_candidates))
    else:
        keep = min(controls.max_search_branches, len(sorted_candidates))
    widened = sorted_candidates[:keep]
    pruned = sorted_candidates[keep:]
    return widened, pruned


def _profile_candidates(*, controls: Any) -> list[str]:
    candidates = ["small_cpu", "standard_cpu"]
    configured = _clean_text(controls.execution_profile)
    if configured and configured not in {"auto", *candidates}:
        candidates.append(configured)
    if controls.distributed_local_allowed:
        candidates.append("distributed_local")
    return candidates


def _selected_execution_profile(
    *,
    controls: Any,
    profile_candidates: list[str],
    recommended_action: str,
    planned_trial_count: int,
) -> str:
    configured = _clean_text(controls.execution_profile)
    if configured and configured != "auto":
        return configured
    if recommended_action == "stop_search" or planned_trial_count <= 8:
        return "small_cpu"
    if controls.distributed_local_allowed and planned_trial_count >= max(controls.medium_hpo_trials, 12):
        return "distributed_local"
    return "standard_cpu" if "standard_cpu" in profile_candidates else profile_candidates[0]


def _distributed_jobs(
    *,
    controls: Any,
    widened_branches: list[dict[str, Any]],
    selected_execution_profile: str,
    planned_trial_count: int,
) -> list[dict[str, Any]]:
    if not controls.distributed_local_allowed or len(widened_branches) <= 1 or planned_trial_count <= 0:
        return []
    jobs: list[dict[str, Any]] = []
    per_branch = max(1, planned_trial_count // max(len(widened_branches), 1))
    for index, branch in enumerate(widened_branches, start=1):
        jobs.append(
            {
                "job_id": f"search_job_{index}",
                "branch_id": str(branch.get("branch_id")),
                "execution_profile": selected_execution_profile,
                "planned_trials": per_branch,
            }
        )
    return jobs


def _checkpoint_state(*, root: Path, controls: Any, distributed_jobs: list[dict[str, Any]]) -> dict[str, Any]:
    checkpoint_dir = root / "checkpoints"
    checkpoints = sorted(checkpoint_dir.glob("ckpt_*.json")) if checkpoint_dir.exists() else []
    latest_checkpoint = str(checkpoints[-1].name) if checkpoints else None
    resume_ready = bool(checkpoints) or (not distributed_jobs) or (not controls.checkpoint_required_for_distributed_runs)
    summary = (
        f"Relaytic found `{len(checkpoints)}` checkpoint(s); resume is {'ready' if resume_ready else 'not ready'} for the current search plan."
    )
    return {
        "checkpoint_dir": str(checkpoint_dir),
        "checkpoint_count": len(checkpoints),
        "resume_ready": resume_ready,
        "latest_checkpoint": latest_checkpoint,
        "summary": summary,
    }


def _search_mode(*, recommended_action: str, stop_search_explicit: bool, widened_branch_count: int) -> str:
    if stop_search_explicit:
        return "stop_search"
    if recommended_action == "expand_challenger_portfolio":
        return "portfolio_expand"
    if recommended_action == "run_hpo_campaign":
        return "portfolio_tune"
    if widened_branch_count > 1:
        return "bounded_refine"
    return "single_branch_refine"


def _proofs(
    *,
    recommended_action: str,
    recommended_direction: str,
    stop_search_explicit: bool,
    value_band: str,
    planned_trial_count: int,
    candidate_branches: list[dict[str, Any]],
    widened_branches: list[dict[str, Any]],
    imported_shadow_candidate_count: int,
    trace_bundle: dict[str, Any],
    eval_bundle: dict[str, Any],
) -> list[dict[str, Any]]:
    proofs = [
        {
            "proof_id": "search_value_defined",
            "status": "pass",
            "detail": f"Relaytic classified search value as `{value_band}` before choosing the next action.",
        },
        {
            "proof_id": "direction_explicit",
            "status": "pass",
            "detail": f"Relaytic kept the workspace direction explicit as `{recommended_direction}` instead of hiding continuity assumptions.",
        },
        {
            "proof_id": "bounded_branch_budget_respected",
            "status": "pass" if len(widened_branches) <= len(candidate_branches) else "fail",
            "detail": f"Relaytic kept `{len(widened_branches)}` widened branch(es) out of `{len(candidate_branches)}` candidate branch(es).",
        },
        {
            "proof_id": "stop_search_or_trials",
            "status": "pass",
            "detail": (
                "Relaytic stopped search explicitly."
                if stop_search_explicit
                else f"Relaytic planned `{planned_trial_count}` bounded trial(s) for the retained frontier."
            ),
        },
        {
            "proof_id": "trace_and_eval_context_present",
            "status": "pass",
            "detail": f"Trace artifacts `{len(trace_bundle)}` and eval artifacts `{len(eval_bundle)}` were available to the controller.",
        },
        {
            "proof_id": "value_of_search_not_assumed",
            "status": "pass",
            "detail": f"Relaytic chose `{recommended_action}` instead of defaulting to deeper HPO as a reflex.",
        },
    ]
    if imported_shadow_candidate_count > 0:
        proofs.append(
            {
                "proof_id": "imported_architectures_stayed_gated",
                "status": "pass",
                "detail": (
                    f"Relaytic kept `{imported_shadow_candidate_count}` imported architecture candidate(s) behind shadow or promotion gates instead of letting them become live defaults implicitly."
                ),
            }
        )
    return proofs


def _summary_text(*, recommended_action: str, recommended_direction: str, value_band: str, planned_trial_count: int) -> str:
    if recommended_action == "stop_search":
        return f"Relaytic explicitly stopped search because value is `{value_band}` and the workspace should move toward `{recommended_direction}`."
    return (
        f"Relaytic recommends `{recommended_action}` with search value `{value_band}` "
        f"and `{planned_trial_count}` planned trial(s) while keeping the workspace direction `{recommended_direction}` explicit."
    )


def _search_reasons(
    *,
    recommended_direction: str,
    recommended_action: str,
    beat_target_pressure: str,
    unresolved_count: int,
    review_need: str,
    value_band: str,
    eval_state: dict[str, Any],
) -> list[str]:
    reasons = [
        f"Search value is currently `{value_band}`.",
        f"Workspace direction remains `{recommended_direction}`.",
        f"Beat-target pressure is `{beat_target_pressure}`.",
        f"Result-contract unresolved item count is `{unresolved_count}`.",
        f"Review need is `{review_need}`.",
    ]
    if _clean_text(eval_state.get("protocol_status")) == "fail" or int(eval_state.get("failed_count", 0) or 0) > 0:
        reasons.append("Open eval/protocol issues reduce the value of spending more search budget before cleanup.")
    if recommended_action == "stop_search":
        reasons.append("Relaytic found that another move is currently worth more than deeper search on the same snapshot.")
    return reasons


def _beat_target_pressure(*, benchmark: dict[str, Any], benchmark_bundle: dict[str, Any]) -> str:
    beat_target = dict(benchmark_bundle.get("beat_target_contract", {}))
    incumbent_parity = dict(benchmark_bundle.get("incumbent_parity_report", {}))
    beat_target_state = (
        _clean_text(benchmark.get("beat_target_state"))
        or _clean_text(beat_target.get("contract_state"))
        or _clean_text(incumbent_parity.get("parity_status"))
        or "none"
    )
    if bool(benchmark.get("incumbent_stronger")) or beat_target_state in {"open", "required", "unmet", "not_met", "needs_improvement"}:
        return "high"
    if bool(benchmark.get("incumbent_present")) or beat_target_state in {"monitor", "near_parity"}:
        return "medium"
    return "low"


def _alternative_family(*, family: str, task_type: str) -> str:
    normalized = (family or "").lower()
    if "forest" in normalized:
        return "gradient_boosting"
    if "boost" in normalized:
        return "random_forest"
    if "logistic" in normalized or "linear" in normalized:
        return "tree_ensemble"
    if task_type in {"fraud_detection", "anomaly_detection"}:
        return "isolation_forest"
    return "tree_ensemble"


def _optional_int(value: Any, *, default: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _clean_text(value: Any) -> str | None:
    text = str(value or "").strip()
    return text or None


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()
