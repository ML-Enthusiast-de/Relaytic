"""Slice 10B quality contracts, visible budgets, and operator/lab profiles."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any

from relaytic.core.benchmark_statuses import benchmark_is_reference_competitive

from .models import (
    BUDGET_CONSUMPTION_REPORT_SCHEMA_VERSION,
    BUDGET_CONTRACT_SCHEMA_VERSION,
    LAB_OPERATING_PROFILE_SCHEMA_VERSION,
    OPERATOR_PROFILE_SCHEMA_VERSION,
    QUALITY_CONTRACT_SCHEMA_VERSION,
    QUALITY_GATE_REPORT_SCHEMA_VERSION,
    BudgetConsumptionReport,
    BudgetContract,
    LabOperatingProfile,
    OperatorProfile,
    ProfilesBundle,
    ProfilesControls,
    ProfilesTrace,
    QualityContract,
    QualityGateReport,
    build_profiles_controls_from_policy,
)


@dataclass(frozen=True)
class ProfilesRunResult:
    """Profiles bundle plus human-readable output."""

    bundle: ProfilesBundle
    review_markdown: str


def run_profiles_review(
    *,
    run_dir: str | Path,
    policy: dict[str, Any],
    mandate_bundle: dict[str, Any] | None = None,
    context_bundle: dict[str, Any] | None = None,
    intake_bundle: dict[str, Any] | None = None,
    investigation_bundle: dict[str, Any] | None = None,
    planning_bundle: dict[str, Any] | None = None,
    evidence_bundle: dict[str, Any] | None = None,
    benchmark_bundle: dict[str, Any] | None = None,
    completion_bundle: dict[str, Any] | None = None,
    lifecycle_bundle: dict[str, Any] | None = None,
    autonomy_bundle: dict[str, Any] | None = None,
) -> ProfilesRunResult:
    controls = build_profiles_controls_from_policy(policy)
    mandate_bundle = mandate_bundle or {}
    context_bundle = context_bundle or {}
    intake_bundle = intake_bundle or {}
    investigation_bundle = investigation_bundle or {}
    planning_bundle = planning_bundle or {}
    evidence_bundle = evidence_bundle or {}
    benchmark_bundle = benchmark_bundle or {}
    completion_bundle = completion_bundle or {}
    lifecycle_bundle = lifecycle_bundle or {}
    autonomy_bundle = autonomy_bundle or {}

    operator_profile = _build_operator_profile(
        controls=controls,
        policy=policy,
        mandate_bundle=mandate_bundle,
        context_bundle=context_bundle,
        investigation_bundle=investigation_bundle,
    )
    lab_profile = _build_lab_operating_profile(
        controls=controls,
        policy=policy,
        mandate_bundle=mandate_bundle,
        context_bundle=context_bundle,
    )
    quality_contract = _build_quality_contract(
        controls=controls,
        policy=policy,
        operator_profile=operator_profile,
        lab_profile=lab_profile,
        mandate_bundle=mandate_bundle,
        context_bundle=context_bundle,
        intake_bundle=intake_bundle,
        investigation_bundle=investigation_bundle,
        planning_bundle=planning_bundle,
    )
    budget_contract = _build_budget_contract(
        controls=controls,
        policy=policy,
        operator_profile=operator_profile,
        lab_profile=lab_profile,
        investigation_bundle=investigation_bundle,
    )
    quality_gate_report = _build_quality_gate_report(
        controls=controls,
        quality_contract=quality_contract,
        planning_bundle=planning_bundle,
        evidence_bundle=evidence_bundle,
        benchmark_bundle=benchmark_bundle,
        completion_bundle=completion_bundle,
        lifecycle_bundle=lifecycle_bundle,
    )
    budget_consumption_report = _build_budget_consumption_report(
        run_dir=run_dir,
        controls=controls,
        budget_contract=budget_contract,
        planning_bundle=planning_bundle,
        evidence_bundle=evidence_bundle,
        benchmark_bundle=benchmark_bundle,
        autonomy_bundle=autonomy_bundle,
    )
    bundle = ProfilesBundle(
        quality_contract=quality_contract,
        quality_gate_report=quality_gate_report,
        budget_contract=budget_contract,
        budget_consumption_report=budget_consumption_report,
        operator_profile=operator_profile,
        lab_operating_profile=lab_profile,
    )
    return ProfilesRunResult(bundle=bundle, review_markdown=render_profiles_review_markdown(bundle.to_dict()))


def render_profiles_review_markdown(bundle: dict[str, Any]) -> str:
    """Render the current Slice 10B artifacts for humans."""
    quality_contract = dict(bundle.get("quality_contract", {}))
    quality_gate = dict(bundle.get("quality_gate_report", {}))
    budget_contract = dict(bundle.get("budget_contract", {}))
    budget_consumption = dict(bundle.get("budget_consumption_report", {}))
    operator_profile = dict(bundle.get("operator_profile", {}))
    lab_profile = dict(bundle.get("lab_operating_profile", {}))
    criteria = dict(quality_contract.get("acceptance_criteria", {}))
    criteria_text = ", ".join(f"{key}>={float(value):.2f}" for key, value in criteria.items()) or "none"
    lines = [
        "# Relaytic Quality And Budget Contracts",
        "",
        f"- Quality status: `{quality_gate.get('gate_status') or quality_gate.get('status') or 'unknown'}`",
        f"- Recommended action: `{quality_gate.get('recommended_action') or 'none'}`",
        f"- Quality state: `{quality_gate.get('quality_state') or 'unknown'}`",
        f"- Acceptance criteria: `{criteria_text}`",
        f"- Budget health: `{budget_consumption.get('budget_health') or 'unknown'}`",
        f"- Elapsed minutes: `{_fmt_float(budget_consumption.get('observed_elapsed_minutes'))}` / `{budget_contract.get('max_wall_clock_minutes', 'n/a')}`",
        f"- Estimated trials: `{budget_consumption.get('estimated_trials_consumed', 0)}` / `{budget_contract.get('max_trials', 'n/a')}`",
        f"- Used branches: `{budget_consumption.get('used_branches', 0)}` / `{budget_contract.get('max_branches_per_round', 'n/a')}`",
        f"- Operator profile: `{operator_profile.get('profile_name') or 'unknown'}`",
        f"- Lab profile: `{lab_profile.get('profile_name') or 'unknown'}`",
        "",
        "## Notes",
        f"- {quality_gate.get('summary') or quality_contract.get('summary') or 'No quality summary available.'}",
        f"- {budget_consumption.get('summary') or budget_contract.get('summary') or 'No budget summary available.'}",
    ]
    return "\n".join(lines).rstrip() + "\n"


def _build_operator_profile(
    *,
    controls: ProfilesControls,
    policy: dict[str, Any],
    mandate_bundle: dict[str, Any],
    context_bundle: dict[str, Any],
    investigation_bundle: dict[str, Any],
) -> OperatorProfile:
    work_preferences = _bundle_item(mandate_bundle, "work_preferences")
    task_brief = _bundle_item(context_bundle, "task_brief")
    focus_profile = _bundle_item(investigation_bundle, "focus_profile")
    optimization_profile = _bundle_item(investigation_bundle, "optimization_profile")
    compute_cfg = dict(policy.get("compute", {}))
    constraints_cfg = dict(policy.get("constraints", {}))
    benchmark_cfg = dict(policy.get("benchmark", {}))

    report_style = _clean_text(work_preferences.get("preferred_report_style")) or "concise"
    explicit_effort_tier = _clean_text(work_preferences.get("preferred_effort_tier"))
    effort_tier = explicit_effort_tier or _clean_text(compute_cfg.get("default_effort_tier")) or "standard"
    domain_text = " ".join(
        item
        for item in (
            _clean_text(task_brief.get("problem_statement")),
            _clean_text(task_brief.get("domain_archetype_hint")),
            _clean_text(focus_profile.get("primary_objective")),
        )
        if item
    ).lower()
    review_strictness = "strict" if any(token in domain_text for token in ("fraud", "risk", "compliance", "bank", "safety", "medical", "legal")) else "standard"
    benchmark_appetite = "required" if bool(benchmark_cfg.get("enabled", True)) and review_strictness == "strict" else "high" if bool(benchmark_cfg.get("enabled", True)) else "low"
    explanation_style = "detailed" if report_style in {"detailed", "full"} else "concise"
    abstention_preference = "review_when_uncertain" if bool(constraints_cfg.get("abstention_allowed", True)) else "force_decision"
    budget_posture = (
        _effort_tier_to_budget_posture(explicit_effort_tier)
        if explicit_effort_tier
        else _clean_text(optimization_profile.get("search_budget_posture")) or _effort_tier_to_budget_posture(effort_tier)
    )
    profile_name = f"operator_{review_strictness}_{budget_posture}_{report_style}".replace("-", "_")
    source = "work_preferences" if work_preferences else "policy_defaults"
    summary = (
        f"Relaytic derived operator posture `{profile_name}` with `{review_strictness}` review strictness, "
        f"`{benchmark_appetite}` benchmark appetite, and `{budget_posture}` budget posture."
    )
    return OperatorProfile(
        schema_version=OPERATOR_PROFILE_SCHEMA_VERSION,
        generated_at=_utc_now(),
        controls=controls,
        status="derived",
        profile_name=profile_name,
        source=source,
        execution_mode_preference=_clean_text(work_preferences.get("execution_mode_preference")),
        operation_mode_preference=_clean_text(work_preferences.get("operation_mode_preference")),
        preferred_report_style=report_style,
        preferred_effort_tier=effort_tier,
        review_strictness=review_strictness,
        benchmark_appetite=benchmark_appetite,
        explanation_style=explanation_style,
        abstention_preference=abstention_preference,
        budget_posture=budget_posture,
        summary=summary,
        trace=_trace(note="operator profile derived from work preferences and policy"),
    )


def _build_lab_operating_profile(
    *,
    controls: ProfilesControls,
    policy: dict[str, Any],
    mandate_bundle: dict[str, Any],
    context_bundle: dict[str, Any],
) -> LabOperatingProfile:
    lab_mandate = _bundle_item(mandate_bundle, "lab_mandate")
    task_brief = _bundle_item(context_bundle, "task_brief")
    privacy_cfg = dict(policy.get("privacy", {}))
    locality_cfg = dict(policy.get("locality", {}))
    benchmark_cfg = dict(policy.get("benchmark", {}))
    hard_constraints = _string_list(lab_mandate.get("hard_constraints"))
    notes = _string_list(lab_mandate.get("values")) + _string_list(lab_mandate.get("soft_preferences"))
    text_blob = " ".join(hard_constraints + notes + _string_list(task_brief.get("success_criteria"))).lower()
    review_strictness = "strict" if any(token in text_blob for token in ("audit", "risk", "fraud", "compliance", "bank", "safety", "regulated")) else "standard"
    benchmark_required = bool(benchmark_cfg.get("enabled", True)) or "benchmark" in text_blob
    budget_posture = "conservative" if bool(privacy_cfg.get("local_only", True)) else "standard"
    risk_posture = "guarded_local_first" if bool(privacy_cfg.get("local_only", True)) else "balanced"
    profile_name = "local_first_guarded_lab" if bool(privacy_cfg.get("local_only", True)) else "mixed_connectivity_lab"
    summary = (
        f"Relaytic derived lab posture `{profile_name}` with `{review_strictness}` review strictness, "
        f"benchmark required `{benchmark_required}`, and `{budget_posture}` budget posture."
    )
    return LabOperatingProfile(
        schema_version=LAB_OPERATING_PROFILE_SCHEMA_VERSION,
        generated_at=_utc_now(),
        controls=controls,
        status="derived",
        profile_name=profile_name,
        source="lab_mandate" if lab_mandate else "policy_defaults",
        local_truth_required=bool(privacy_cfg.get("local_only", True)),
        remote_intelligence_allowed=bool(locality_cfg.get("allow_optional_remote_baselines", False)),
        benchmark_required=benchmark_required,
        review_strictness=review_strictness,
        risk_posture=risk_posture,
        budget_posture=budget_posture,
        notes=notes[:8],
        summary=summary,
        trace=_trace(note="lab operating profile derived from mandate and policy"),
    )


def _build_quality_contract(
    *,
    controls: ProfilesControls,
    policy: dict[str, Any],
    operator_profile: OperatorProfile,
    lab_profile: LabOperatingProfile,
    mandate_bundle: dict[str, Any],
    context_bundle: dict[str, Any],
    intake_bundle: dict[str, Any],
    investigation_bundle: dict[str, Any],
    planning_bundle: dict[str, Any],
) -> QualityContract:
    run_brief = _bundle_item(mandate_bundle, "run_brief")
    task_brief = _bundle_item(context_bundle, "task_brief")
    autonomy_mode = _bundle_item(intake_bundle, "autonomy_mode")
    optimization_profile = _bundle_item(investigation_bundle, "optimization_profile")
    plan = _bundle_item(planning_bundle, "plan")
    builder_handoff = dict(plan.get("builder_handoff") or {})
    task_type = _task_type(plan=plan, task_brief=task_brief)
    primary_metric = _clean_text(plan.get("primary_metric")) or _clean_text(optimization_profile.get("primary_metric")) or _default_primary_metric(task_type)
    split_strategy = _clean_text(plan.get("split_strategy")) or _clean_text(optimization_profile.get("split_strategy_bias")) or "deterministic_modulo_70_15_15"
    acceptance = dict(builder_handoff.get("acceptance_criteria")) if isinstance(builder_handoff.get("acceptance_criteria"), dict) else {}
    if not acceptance:
        acceptance = _default_acceptance_criteria(task_type)
    constraints_cfg = dict(policy.get("constraints", {}))
    uncertainty_required = bool(constraints_cfg.get("uncertainty_required", True))
    abstention_allowed = bool(constraints_cfg.get("abstention_allowed", True))
    operator_review_required = operator_profile.review_strictness == "strict" or task_type in {"fraud_detection", "anomaly_detection"}
    minimum_readiness_level = "strong" if operator_profile.review_strictness == "strict" else "conditional"
    search_budget_posture = _clean_text(optimization_profile.get("search_budget_posture")) or operator_profile.budget_posture
    threshold_policy = _clean_text(builder_handoff.get("threshold_policy")) or _clean_text(optimization_profile.get("threshold_objective"))
    benchmark_required = lab_profile.benchmark_required or operator_profile.benchmark_appetite in {"high", "required"}
    reasoning_requirements = ["metric_contract"]
    if benchmark_required:
        reasoning_requirements.append("benchmark_parity_review")
    if uncertainty_required:
        reasoning_requirements.append("uncertainty_required")
    if operator_review_required:
        reasoning_requirements.append("operator_review_on_ambiguity")
    if _clean_text(autonomy_mode.get("requested_mode")) == "full_auto":
        reasoning_requirements.append("autonomous_default_assumptions_allowed")
    if _string_list(run_brief.get("success_criteria")):
        reasoning_requirements.append("run_brief_success_criteria_present")
    summary = (
        f"Relaytic will judge `{task_type}` quality with `{primary_metric}` and acceptance "
        f"`{', '.join(f'{key}>={value:.2f}' for key, value in acceptance.items())}`; "
        f"minimum readiness is `{minimum_readiness_level}` and benchmark required is `{benchmark_required}`."
    )
    return QualityContract(
        schema_version=QUALITY_CONTRACT_SCHEMA_VERSION,
        generated_at=_utc_now(),
        controls=controls,
        status="contract_materialized",
        contract_origin="task_derived_defaults",
        task_type=task_type,
        primary_metric=primary_metric or "unknown",
        split_strategy=split_strategy,
        acceptance_criteria={str(key): float(value) for key, value in acceptance.items()},
        threshold_policy=threshold_policy,
        benchmark_required=benchmark_required,
        uncertainty_required=uncertainty_required,
        abstention_allowed=abstention_allowed,
        operator_review_required=operator_review_required,
        minimum_readiness_level=minimum_readiness_level,
        search_budget_posture=search_budget_posture,
        operator_profile_name=operator_profile.profile_name,
        lab_profile_name=lab_profile.profile_name,
        reasoning_requirements=reasoning_requirements,
        summary=summary,
        trace=_trace(note="quality contract derived from task, policy, and profile overlays"),
    )


def _build_quality_gate_report(
    *,
    controls: ProfilesControls,
    quality_contract: QualityContract,
    planning_bundle: dict[str, Any],
    evidence_bundle: dict[str, Any],
    benchmark_bundle: dict[str, Any],
    completion_bundle: dict[str, Any],
    lifecycle_bundle: dict[str, Any],
) -> QualityGateReport:
    plan = _bundle_item(planning_bundle, "plan")
    execution_summary = dict(plan.get("execution_summary") or {})
    selected_metrics = dict(execution_summary.get("selected_metrics") or {})
    validation = dict(selected_metrics.get("validation") or {})
    test = dict(selected_metrics.get("test") or {})
    measured = dict(test or validation)
    audit_report = _bundle_item(evidence_bundle, "audit_report")
    benchmark_parity_report = _bundle_item(benchmark_bundle, "benchmark_parity_report")
    benchmark_gap_report = _bundle_item(benchmark_bundle, "benchmark_gap_report")
    completion_decision = _bundle_item(completion_bundle, "completion_decision")
    retrain = _bundle_item(lifecycle_bundle, "retrain_decision")
    recalibration = _bundle_item(lifecycle_bundle, "recalibration_decision")
    readiness_level = _clean_text(audit_report.get("readiness_level")) or "unknown"
    benchmark_status = _clean_text(benchmark_parity_report.get("parity_status")) or "not_run"
    unmet: list[dict[str, Any]] = []
    passed_gates: list[str] = []
    failed_gates: list[str] = []
    if not measured:
        failed_gates.append("metrics_missing")
        status = "pending"
        gate_status = "pending"
        recommended_action = "continue"
        quality_state = "unknown"
        summary = "Relaytic materialized the quality contract before execution; no measured metrics are available yet."
    else:
        for key, threshold in quality_contract.acceptance_criteria.items():
            actual = _optional_float(measured.get(key))
            if actual is None:
                unmet.append({"metric": key, "expected_minimum": threshold, "actual_value": None, "reason": "metric_missing"})
                failed_gates.append(f"metric:{key}")
                continue
            if actual < threshold:
                unmet.append({"metric": key, "expected_minimum": threshold, "actual_value": actual, "reason": "below_threshold"})
                failed_gates.append(f"metric:{key}")
            else:
                passed_gates.append(f"metric:{key}")
        if quality_contract.benchmark_required:
            if benchmark_is_reference_competitive(benchmark_status, include_near=True):
                passed_gates.append("benchmark")
            else:
                failed_gates.append("benchmark")
        if quality_contract.minimum_readiness_level == "strong":
            if readiness_level == "strong":
                passed_gates.append("readiness")
            else:
                failed_gates.append("readiness")
        elif readiness_level in {"strong", "conditional"}:
            passed_gates.append("readiness")
        else:
            failed_gates.append("readiness")
        status = "gated"
        gate_status = "conditional_pass" if failed_gates and not unmet else "fail" if failed_gates else "pass"
        quality_state = _quality_state_from_gates(unmet=unmet, readiness_level=readiness_level, benchmark_status=benchmark_status)
        recommended_action = _quality_gate_action(
            failed_gates=failed_gates,
            completion_action=_clean_text(completion_decision.get("action")),
            benchmark_recommended_action=_clean_text(benchmark_parity_report.get("recommended_action")) or _clean_text(benchmark_gap_report.get("recommended_action")),
            retrain_action=_clean_text(retrain.get("action")),
            recalibration_action=_clean_text(recalibration.get("action")),
        )
        summary = _quality_gate_summary(
            gate_status=gate_status,
            recommended_action=recommended_action,
            failed_gates=failed_gates,
            readiness_level=readiness_level,
            benchmark_status=benchmark_status,
        )
    return QualityGateReport(
        schema_version=QUALITY_GATE_REPORT_SCHEMA_VERSION,
        generated_at=_utc_now(),
        controls=controls,
        status=status,
        gate_status=gate_status,
        recommended_action=recommended_action,
        quality_state=quality_state,
        benchmark_status=benchmark_status,
        readiness_level=readiness_level,
        measured_metrics=measured,
        passed_gates=_dedupe_strings(passed_gates),
        failed_gates=_dedupe_strings(failed_gates),
        unmet_acceptance_criteria=unmet,
        summary=summary,
        trace=_trace(note="quality gate evaluated against explicit contract"),
    )


def _build_budget_contract(
    *,
    controls: ProfilesControls,
    policy: dict[str, Any],
    operator_profile: OperatorProfile,
    lab_profile: LabOperatingProfile,
    investigation_bundle: dict[str, Any],
) -> BudgetContract:
    compute_cfg = dict(policy.get("compute", {}))
    autonomy_cfg = dict(policy.get("autonomy", {}))
    optimization_profile = _bundle_item(investigation_bundle, "optimization_profile")
    execution_profile = _clean_text(compute_cfg.get("execution_profile")) or "auto"
    machine_profile = _clean_text(compute_cfg.get("machine_profile")) or "auto"
    preferred_effort_tier = operator_profile.preferred_effort_tier or _clean_text(compute_cfg.get("default_effort_tier")) or "standard"
    search_budget_posture = _clean_text(optimization_profile.get("search_budget_posture")) or operator_profile.budget_posture
    recommended_trial_utilization_fraction = {
        "conservative": 0.35,
        "standard": 0.60,
        "aggressive": 0.85,
    }.get(search_budget_posture, 0.60)
    max_wall_clock_minutes = _safe_int(compute_cfg.get("max_wall_clock_minutes"), default=120)
    max_trials = _safe_int(compute_cfg.get("max_trials"), default=200)
    max_parallel_trials = _safe_int(compute_cfg.get("max_parallel_trials"), default=4)
    max_memory_gb = _safe_float(compute_cfg.get("max_memory_gb"), default=24.0)
    max_followup_rounds = _safe_int(autonomy_cfg.get("max_followup_rounds"), default=1)
    max_branches_per_round = _safe_int(autonomy_cfg.get("max_branches_per_round"), default=2)
    summary = (
        f"Relaytic budget contract allows `{max_wall_clock_minutes}` wall-clock minute(s), "
        f"`{max_trials}` estimated trial(s), `{max_parallel_trials}` parallel trial(s), and "
        f"`{max_branches_per_round}` branch(es) per round under `{search_budget_posture}` posture."
    )
    return BudgetContract(
        schema_version=BUDGET_CONTRACT_SCHEMA_VERSION,
        generated_at=_utc_now(),
        controls=controls,
        status="contract_materialized",
        contract_origin="policy_defaults_with_profile_overlay",
        execution_profile=execution_profile,
        machine_profile=machine_profile,
        preferred_effort_tier=preferred_effort_tier,
        budget_posture=lab_profile.budget_posture if lab_profile.budget_posture == "conservative" else operator_profile.budget_posture,
        search_budget_posture=search_budget_posture,
        max_wall_clock_minutes=max_wall_clock_minutes,
        max_trials=max_trials,
        max_parallel_trials=max_parallel_trials,
        max_memory_gb=max_memory_gb,
        max_followup_rounds=max_followup_rounds,
        max_branches_per_round=max_branches_per_round,
        recommended_trial_utilization_fraction=recommended_trial_utilization_fraction,
        summary=summary,
        trace=_trace(note="budget contract derived from compute, autonomy, and profile posture"),
    )


def _build_budget_consumption_report(
    *,
    run_dir: str | Path,
    controls: ProfilesControls,
    budget_contract: BudgetContract,
    planning_bundle: dict[str, Any],
    evidence_bundle: dict[str, Any],
    benchmark_bundle: dict[str, Any],
    autonomy_bundle: dict[str, Any],
) -> BudgetConsumptionReport:
    root = Path(run_dir)
    runtime_events = _read_jsonl(root / "lab_event_stream.jsonl")
    observed_elapsed_minutes = _observed_elapsed_minutes(runtime_events)
    plan = _bundle_item(planning_bundle, "plan")
    execution_summary = dict(plan.get("execution_summary") or {})
    experiment_registry = _bundle_item(evidence_bundle, "experiment_registry")
    benchmark_parity_report = _bundle_item(benchmark_bundle, "benchmark_parity_report")
    branch_outcome_matrix = _bundle_item(autonomy_bundle, "branch_outcome_matrix")
    loop_budget_report = _bundle_item(autonomy_bundle, "loop_budget_report")
    experiment_count = len(experiment_registry.get("experiments", [])) if isinstance(experiment_registry.get("experiments"), list) else 0
    reference_count = _safe_int(benchmark_parity_report.get("reference_count"), default=0)
    branch_count = len(branch_outcome_matrix.get("branches", [])) if isinstance(branch_outcome_matrix.get("branches"), list) else 0
    base_trial = 1 if _clean_text(execution_summary.get("selected_model_family")) else 0
    estimated_trials_consumed = max(base_trial, experiment_count + reference_count + branch_count)
    remaining_trials = max(0, int(budget_contract.max_trials) - estimated_trials_consumed)
    used_branches = _safe_int(loop_budget_report.get("used_branch_count"), default=branch_count)
    remaining_branch_budget = _safe_int(loop_budget_report.get("budget_remaining"), default=max(0, budget_contract.max_branches_per_round - used_branches))
    estimated_input_footprint_mb = _estimated_input_footprint_mb(root)
    elapsed_fraction = observed_elapsed_minutes / max(float(budget_contract.max_wall_clock_minutes), 1.0)
    trial_fraction = estimated_trials_consumed / max(float(budget_contract.max_trials), 1.0)
    if elapsed_fraction > 1.0 or trial_fraction > 1.0:
        budget_health = "over_budget"
    elif elapsed_fraction >= 0.80 or trial_fraction >= 0.80 or remaining_branch_budget <= 0:
        budget_health = "near_limit"
    else:
        budget_health = "within_contract"
    summary = (
        f"Relaytic has consumed about `{observed_elapsed_minutes:.2f}` minute(s), "
        f"`{estimated_trials_consumed}` estimated trial(s), and `{used_branches}` branch(es); "
        f"budget health is `{budget_health}`."
    )
    return BudgetConsumptionReport(
        schema_version=BUDGET_CONSUMPTION_REPORT_SCHEMA_VERSION,
        generated_at=_utc_now(),
        controls=controls,
        status="consumption_recorded",
        budget_health=budget_health,
        observed_elapsed_minutes=round(observed_elapsed_minutes, 4),
        estimated_trials_consumed=estimated_trials_consumed,
        remaining_trials=remaining_trials,
        used_branches=used_branches,
        remaining_branch_budget=remaining_branch_budget,
        estimated_input_footprint_mb=estimated_input_footprint_mb,
        observed_event_count=len(runtime_events),
        summary=summary,
        trace=_trace(note="budget consumption estimated from runtime, evidence, benchmark, and autonomy artifacts"),
    )


def _default_acceptance_criteria(task_type: str) -> dict[str, float]:
    normalized = str(task_type or "").strip().lower()
    if normalized in {"binary_classification", "multiclass_classification"}:
        return {"f1": 0.75, "accuracy": 0.75}
    if normalized in {"fraud_detection", "anomaly_detection"}:
        return {"recall": 0.70, "pr_auc": 0.35}
    return {"r2": 0.70}


def _default_primary_metric(task_type: str) -> str:
    normalized = str(task_type or "").strip().lower()
    if normalized in {"fraud_detection", "anomaly_detection"}:
        return "pr_auc"
    if normalized in {"binary_classification", "multiclass_classification"}:
        return "f1"
    return "r2"


def _task_type(*, plan: dict[str, Any], task_brief: dict[str, Any]) -> str:
    return _clean_text(plan.get("task_type")) or _clean_text(task_brief.get("task_type_hint")) or "unknown"


def _quality_state_from_gates(*, unmet: list[dict[str, Any]], readiness_level: str, benchmark_status: str) -> str:
    if unmet:
        return "below_contract"
    if readiness_level == "strong" and benchmark_is_reference_competitive(benchmark_status, include_near=True):
        return "strong"
    if readiness_level in {"strong", "conditional"}:
        return "acceptable"
    return "conditional"


def _quality_gate_action(
    *,
    failed_gates: list[str],
    completion_action: str | None,
    benchmark_recommended_action: str | None,
    retrain_action: str | None,
    recalibration_action: str | None,
) -> str:
    if retrain_action == "retrain":
        return "retrain"
    if recalibration_action == "recalibrate":
        return "recalibrate"
    if completion_action in {"continue_experimentation", "review_challenger", "retrain_candidate"}:
        return completion_action
    if benchmark_recommended_action:
        return benchmark_recommended_action
    if any(item.startswith("metric:") for item in failed_gates):
        return "run_more_search"
    if "benchmark" in failed_gates or "readiness" in failed_gates:
        return "continue"
    return "continue"


def _quality_gate_summary(
    *,
    gate_status: str,
    recommended_action: str,
    failed_gates: list[str],
    readiness_level: str,
    benchmark_status: str,
) -> str:
    if gate_status == "pending":
        return "Relaytic has not executed enough of the run to evaluate the explicit quality contract yet."
    if not failed_gates:
        return (
            f"Relaytic met the explicit quality contract with readiness `{readiness_level}` and benchmark status "
            f"`{benchmark_status}`; it can continue under action `{recommended_action}`."
        )
    return (
        f"Relaytic did not fully satisfy the explicit quality contract because `{', '.join(failed_gates)}` failed; "
        f"recommended action is `{recommended_action}`."
    )


def _effort_tier_to_budget_posture(effort_tier: str) -> str:
    normalized = str(effort_tier or "").strip().lower()
    if normalized in {"minimal", "light", "quick"}:
        return "conservative"
    if normalized in {"max", "heavy", "extensive", "aggressive"}:
        return "aggressive"
    return "standard"


def _observed_elapsed_minutes(runtime_events: list[dict[str, Any]]) -> float:
    timestamps = []
    for item in runtime_events:
        stamp = _parse_timestamp(item.get("recorded_at"))
        if stamp is not None:
            timestamps.append(stamp)
    if len(timestamps) >= 2:
        return max(0.0, (max(timestamps) - min(timestamps)).total_seconds() / 60.0)
    return 0.0


def _estimated_input_footprint_mb(root: Path) -> float | None:
    manifest_path = root / "data_copy_manifest.json"
    if not manifest_path.exists():
        return None
    try:
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    latest = dict(payload.get("latest_by_purpose", {}))
    primary_text = str(latest.get("primary", "")).strip()
    if not primary_text:
        return None
    primary = Path(primary_text)
    if primary.exists() and primary.is_file():
        try:
            return round(primary.stat().st_size / (1024.0 * 1024.0), 4)
        except OSError:
            return None
    return None


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    records: list[dict[str, Any]] = []
    try:
        with path.open("r", encoding="utf-8") as handle:
            for line in handle:
                text = line.strip()
                if not text:
                    continue
                try:
                    payload = json.loads(text)
                except json.JSONDecodeError:
                    continue
                if isinstance(payload, dict):
                    records.append(payload)
    except OSError:
        return []
    return records


def _bundle_item(bundle: dict[str, Any], key: str) -> dict[str, Any]:
    payload = bundle.get(key)
    return dict(payload) if isinstance(payload, dict) else {}


def _parse_timestamp(value: Any) -> datetime | None:
    text = _clean_text(value)
    if not text:
        return None
    try:
        return datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return None


def _clean_text(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text or text.lower() in {"none", "null"}:
        return None
    return text


def _safe_float(value: Any, *, default: float) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _safe_int(value: Any, *, default: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _optional_float(value: Any) -> float | None:
    try:
        if value is None:
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item).strip() for item in value if str(item).strip()]


def _dedupe_strings(items: list[str]) -> list[str]:
    seen: set[str] = set()
    deduped: list[str] = []
    for item in items:
        text = str(item).strip()
        if not text or text in seen:
            continue
        seen.add(text)
        deduped.append(text)
    return deduped


def _trace(*, note: str) -> ProfilesTrace:
    return ProfilesTrace(
        agent="profiles_contract_agent",
        operating_mode="deterministic_only",
        llm_used=False,
        llm_status="not_requested",
        deterministic_evidence=["policy", "artifacts", "runtime_estimation"],
        advisory_notes=[note],
    )


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _fmt_float(value: Any) -> str:
    try:
        return f"{float(value):.2f}"
    except (TypeError, ValueError):
        return "unknown"
