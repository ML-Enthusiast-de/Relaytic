"""Slice 05 Strategist and Builder handoff pipeline."""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from relaytic.analytics.task_detection import assess_task_profile, is_classification_task
from relaytic.ingestion import load_tabular_data
from relaytic.modeling import train_surrogate_candidates

from .models import (
    ALTERNATIVES_SCHEMA_VERSION,
    EXPERIMENT_PRIORITY_REPORT_SCHEMA_VERSION,
    HYPOTHESES_SCHEMA_VERSION,
    MARGINAL_VALUE_OF_NEXT_EXPERIMENT_SCHEMA_VERSION,
    PLAN_SCHEMA_VERSION,
    Alternatives,
    ExperimentPriorityReport,
    Hypotheses,
    MarginalValueOfNextExperiment,
    Plan,
    PlanningBundle,
    PlanningControls,
    PlanningTrace,
    build_planning_controls_from_policy,
)
from .semantic import PlanningLocalAdvisor, build_local_advisor


@dataclass(frozen=True)
class PlanningExecutionResult:
    """Plan artifacts plus the first Builder execution result."""

    planning_bundle: PlanningBundle
    training_result: dict[str, Any]


class StrategistAgent:
    """Turns investigation artifacts into a concrete Builder handoff."""

    def __init__(
        self,
        *,
        controls: PlanningControls,
        policy: dict[str, Any],
        advisor: PlanningLocalAdvisor | None = None,
    ) -> None:
        self.controls = controls
        self.policy = policy
        self.advisor = advisor

    def run(
        self,
        *,
        frame: Any,
        data_path: str,
        mandate_bundle: dict[str, Any],
        context_bundle: dict[str, Any],
        investigation_bundle: dict[str, Any],
    ) -> PlanningBundle:
        dataset_profile = _bundle_item(investigation_bundle, "dataset_profile")
        domain_memo = _bundle_item(investigation_bundle, "domain_memo")
        focus_profile = _bundle_item(investigation_bundle, "focus_profile")
        optimization_profile = _bundle_item(investigation_bundle, "optimization_profile")
        feature_strategy_profile = _bundle_item(investigation_bundle, "feature_strategy_profile")
        run_brief = _bundle_item(mandate_bundle, "run_brief")
        task_brief = _bundle_item(context_bundle, "task_brief")
        domain_brief = _bundle_item(context_bundle, "domain_brief")

        target_column = _resolve_target_column(
            frame=frame,
            task_brief=task_brief,
            run_brief=run_brief,
            domain_memo=domain_memo,
            dataset_profile=dataset_profile,
        )
        task_profile = assess_task_profile(
            frame=frame,
            target_column=target_column,
            data_mode=str(dataset_profile.get("data_mode", "steady_state")),
            task_type_hint=_task_type_hint_for_target(domain_memo, target_column),
        )
        route = _select_route(
            dataset_profile=dataset_profile,
            task_profile=task_profile.to_dict(),
            focus_profile=focus_profile,
        )
        primary_metric = _resolve_primary_metric(
            optimization_profile=optimization_profile,
            task_type=task_profile.task_type,
        )
        secondary_metrics = _resolve_secondary_metrics(
            optimization_profile=optimization_profile,
            primary_metric=primary_metric,
        )
        candidate_order = _resolve_candidate_order(
            data_mode=str(dataset_profile.get("data_mode", "steady_state")),
            task_type=task_profile.task_type,
            optimization_profile=optimization_profile,
        )
        feature_columns, feature_drop_reasons, feature_risk_flags = _select_feature_columns(
            frame=frame,
            dataset_profile=dataset_profile,
            domain_brief=domain_brief,
            feature_strategy_profile=feature_strategy_profile,
            target_column=target_column,
            timestamp_column=str(dataset_profile.get("timestamp_column") or "").strip() or None,
            controls=self.controls,
        )
        threshold_policy = _resolve_threshold_policy(
            task_type=task_profile.task_type,
            primary_metric=primary_metric,
            focus_profile=focus_profile,
            task_brief=task_brief,
        )
        selection_metric = _selection_metric_for_primary_metric(
            primary_metric=primary_metric,
            task_type=task_profile.task_type,
        )
        lag_horizon = _resolve_lag_horizon(
            dataset_profile=dataset_profile,
            route=route,
            feature_count=len(feature_columns),
        )
        builder_handoff = {
            "route_id": route["route_id"],
            "route_title": route["title"],
            "target_column": target_column,
            "feature_columns": feature_columns,
            "timestamp_column": str(dataset_profile.get("timestamp_column") or "").strip() or None,
            "requested_model_family": "auto",
            "preferred_candidate_order": candidate_order,
            "selection_metric": selection_metric,
            "primary_metric": primary_metric,
            "secondary_metrics": secondary_metrics,
            "split_strategy": str(route["split_strategy"]),
            "normalize": True,
            "missing_data_strategy": "fill_median",
            "compare_against_baseline": True,
            "lag_horizon_samples": lag_horizon,
            "threshold_policy": threshold_policy,
            "decision_threshold": None,
            "task_type": task_profile.task_type,
            "data_references": [str(data_path)],
            "feature_risk_flags": feature_risk_flags,
        }
        guardrails = _dedupe_strings(
            _string_list(feature_strategy_profile.get("guardrails"))
            + _string_list(run_brief.get("binding_constraints"))
            + _string_list(domain_brief.get("binding_constraints"))
            + _string_list(domain_brief.get("forbidden_features"))
        )
        if feature_risk_flags:
            guardrails.append(
                "Retained heuristic-risk features for the first route because no cleaner numeric set was available: "
                + ", ".join(sorted(flag["column"] for flag in feature_risk_flags))
            )
        execution_steps = [
            {
                "step_id": "validate_route_contract",
                "kind": "guardrail",
                "description": "Freeze target, metric, split, and feature exclusions before training.",
            },
            {
                "step_id": "execute_deterministic_builder",
                "kind": "builder",
                "description": "Run the first deterministic local training route inside the Relaytic run directory.",
            },
            {
                "step_id": "compare_candidate_families",
                "kind": "builder",
                "description": "Compare split-safe baseline candidates and persist the winning artifact set.",
            },
        ]

        alternatives = _build_alternatives(
            route=route,
            candidate_order=candidate_order,
            focus_profile=focus_profile,
            optimization_profile=optimization_profile,
            task_profile=task_profile.to_dict(),
            dataset_profile=dataset_profile,
        )
        hypotheses = _build_hypotheses(
            domain_memo=domain_memo,
            feature_strategy_profile=feature_strategy_profile,
            route=route,
            target_column=target_column,
        )
        priority_items = _build_experiment_priorities(
            route=route,
            candidate_order=candidate_order,
            dataset_profile=dataset_profile,
            focus_profile=focus_profile,
            feature_strategy_profile=feature_strategy_profile,
        )
        marginal_value = _build_marginal_value(
            priority_items=priority_items,
            dataset_profile=dataset_profile,
            primary_metric=primary_metric,
            executed=False,
        )

        llm_advisory: dict[str, Any] | None = None
        llm_status = "not_requested"
        advisory_notes: list[str] = []
        if self.advisor is not None:
            advisory = self.advisor.complete_json(
                task_name="strategist",
                system_prompt=(
                    "You are Relaytic's Strategist advisory module. Read the structured route proposal only. "
                    "Return JSON with keys alternative_routes, extra_hypotheses, experiment_clues, and "
                    "marginal_value_hint. alternative_routes must be a list of objects with route_id, title, "
                    "tradeoff, and reason. extra_hypotheses and experiment_clues must be short strings."
                ),
                payload={
                    "dataset_profile": {
                        "data_mode": dataset_profile.get("data_mode"),
                        "timestamp_column": dataset_profile.get("timestamp_column"),
                        "row_count": dataset_profile.get("row_count"),
                        "leakage_risk_level": dataset_profile.get("leakage_risk_level"),
                    },
                    "focus_profile": focus_profile,
                    "optimization_profile": optimization_profile,
                    "feature_strategy_profile": feature_strategy_profile,
                    "selected_route": route,
                    "builder_handoff": builder_handoff,
                },
            )
            llm_status = "advisory_used" if advisory.status == "ok" and advisory.payload else advisory.status
            advisory_notes.extend(advisory.notes)
            if advisory.payload:
                llm_advisory = advisory.payload
                alternatives.extend(_advisory_alternatives(advisory.payload))
                hypotheses.extend(_advisory_hypotheses(advisory.payload))
                priority_items.extend(_advisory_experiments(advisory.payload))
                marginal_value = _merge_marginal_value_hint(
                    marginal_value=marginal_value,
                    advisory_payload=advisory.payload,
                )

        trace = PlanningTrace(
            agent="strategist",
            operating_mode="deterministic_plus_advisory" if self.advisor is not None else "deterministic_only",
            llm_used=llm_advisory is not None,
            llm_status=llm_status,
            deterministic_evidence=[
                "foundation_artifacts",
                "investigation_artifacts",
                "route_and_metric_resolution",
                "builder_handoff_generation",
            ],
            advisory_notes=advisory_notes,
        )
        generated_at = _utc_now()
        plan = Plan(
            schema_version=PLAN_SCHEMA_VERSION,
            generated_at=generated_at,
            controls=self.controls,
            selected_route_id=str(route["route_id"]),
            selected_route_title=str(route["title"]),
            target_column=target_column,
            task_type=task_profile.task_type,
            data_mode=str(dataset_profile.get("data_mode", "steady_state")),
            primary_metric=primary_metric,
            secondary_metrics=secondary_metrics,
            split_strategy=str(route["split_strategy"]),
            timestamp_column=str(dataset_profile.get("timestamp_column") or "").strip() or None,
            feature_columns=feature_columns,
            feature_drop_reasons=feature_drop_reasons,
            guardrails=guardrails,
            builder_handoff=builder_handoff,
            execution_steps=execution_steps,
            execution_summary=None,
            llm_advisory=llm_advisory,
            summary=_plan_summary(route=route, target_column=target_column, primary_metric=primary_metric),
            trace=trace,
        )
        return PlanningBundle(
            plan=plan,
            alternatives=Alternatives(
                schema_version=ALTERNATIVES_SCHEMA_VERSION,
                generated_at=generated_at,
                controls=self.controls,
                selected_route_id=plan.selected_route_id,
                alternatives=_dedupe_dicts(alternatives, key_field="alternative_id"),
                summary=_alternatives_summary(alternatives),
                trace=trace,
            ),
            hypotheses=Hypotheses(
                schema_version=HYPOTHESES_SCHEMA_VERSION,
                generated_at=generated_at,
                controls=self.controls,
                hypotheses=_dedupe_dicts(hypotheses, key_field="hypothesis_id"),
                summary=_hypotheses_summary(hypotheses),
                trace=trace,
            ),
            experiment_priority_report=ExperimentPriorityReport(
                schema_version=EXPERIMENT_PRIORITY_REPORT_SCHEMA_VERSION,
                generated_at=generated_at,
                controls=self.controls,
                prioritized_experiments=priority_items,
                summary=_priority_summary(priority_items),
                trace=trace,
            ),
            marginal_value_of_next_experiment=MarginalValueOfNextExperiment(
                schema_version=MARGINAL_VALUE_OF_NEXT_EXPERIMENT_SCHEMA_VERSION,
                generated_at=generated_at,
                controls=self.controls,
                recommended_experiment_id=str(marginal_value["recommended_experiment_id"]),
                estimated_value_band=str(marginal_value["estimated_value_band"]),
                estimated_gain_metric=str(marginal_value["estimated_gain_metric"]),
                rationale=str(marginal_value["rationale"]),
                blockers_removed=list(marginal_value["blockers_removed"]),
                trace=trace,
            ),
        )


def run_planning(
    *,
    data_path: str,
    policy: dict[str, Any],
    mandate_bundle: dict[str, Any],
    context_bundle: dict[str, Any],
    investigation_bundle: dict[str, Any],
    config_path: str | None = None,
    sheet_name: str | None = None,
    header_row: int | None = None,
    data_start_row: int | None = None,
) -> PlanningBundle:
    """Run Slice 05 Strategist planning and emit planning artifacts."""
    controls = build_planning_controls_from_policy(policy)
    advisor = build_local_advisor(controls=controls, config_path=config_path)
    strategist = StrategistAgent(controls=controls, policy=policy, advisor=advisor)
    loaded = load_tabular_data(
        data_path,
        sheet_name=sheet_name,
        header_row=header_row,
        data_start_row=data_start_row,
    )
    return strategist.run(
        frame=loaded.frame.copy(),
        data_path=str(Path(data_path)),
        mandate_bundle=mandate_bundle,
        context_bundle=context_bundle,
        investigation_bundle=investigation_bundle,
    )


def execute_planned_route(
    *,
    run_dir: str | Path,
    data_path: str,
    planning_bundle: PlanningBundle,
    sheet_name: str | None = None,
    header_row: int | None = None,
    data_start_row: int | None = None,
) -> PlanningExecutionResult:
    """Execute the first deterministic Builder route from a planning bundle."""
    loaded = load_tabular_data(
        data_path,
        sheet_name=sheet_name,
        header_row=header_row,
        data_start_row=data_start_row,
    )
    handoff = dict(planning_bundle.plan.builder_handoff)
    training_result = train_surrogate_candidates(
        frame=loaded.frame.copy(),
        target_column=str(handoff["target_column"]),
        feature_columns=[str(item) for item in handoff.get("feature_columns", [])],
        requested_model_family=str(handoff.get("requested_model_family", "auto")),
        timestamp_column=_optional_str(handoff.get("timestamp_column")),
        normalize=bool(handoff.get("normalize", True)),
        missing_data_strategy=str(handoff.get("missing_data_strategy", "fill_median")),
        compare_against_baseline=bool(handoff.get("compare_against_baseline", True)),
        lag_horizon_samples=_optional_int(handoff.get("lag_horizon_samples")),
        threshold_policy=_optional_str(handoff.get("threshold_policy")),
        decision_threshold=_optional_float(handoff.get("decision_threshold")),
        task_type=_optional_str(handoff.get("task_type")),
        run_id=Path(run_dir).name,
        checkpoint_tag="relaytic_slice05_builder",
        data_references=[str(item) for item in handoff.get("data_references", [str(Path(data_path))])],
        selection_metric=_optional_str(handoff.get("selection_metric")),
        preferred_candidate_order=[str(item) for item in handoff.get("preferred_candidate_order", [])],
        output_run_dir=run_dir,
        checkpoint_base_dir=Path(run_dir) / "checkpoints",
    )
    execution_summary = {
        "status": training_result.get("status", "error"),
        "selected_model_family": training_result.get("selected_model_family"),
        "best_validation_model_family": training_result.get("best_validation_model_family"),
        "checkpoint_id": training_result.get("checkpoint_id"),
        "model_state_path": training_result.get("model_state_path"),
        "model_params_path": training_result.get("model_params_path"),
        "rows_used": training_result.get("rows_used"),
        "selection_metric": training_result.get("selection_metric"),
        "selected_metrics": training_result.get("selected_metrics"),
    }
    updated_plan = replace(planning_bundle.plan, execution_summary=execution_summary)
    updated_priorities = _mark_priority_completed(
        planning_bundle.experiment_priority_report.prioritized_experiments,
        "execute_selected_route",
    )
    updated_marginal_value = _build_marginal_value(
        priority_items=updated_priorities,
        dataset_profile={"leakage_risk_level": "low"},
        primary_metric=updated_plan.primary_metric,
        executed=True,
    )
    updated_bundle = PlanningBundle(
        plan=updated_plan,
        alternatives=planning_bundle.alternatives,
        hypotheses=planning_bundle.hypotheses,
        experiment_priority_report=replace(
            planning_bundle.experiment_priority_report,
            prioritized_experiments=updated_priorities,
            summary=_priority_summary(updated_priorities),
        ),
        marginal_value_of_next_experiment=replace(
            planning_bundle.marginal_value_of_next_experiment,
            recommended_experiment_id=str(updated_marginal_value["recommended_experiment_id"]),
            estimated_value_band=str(updated_marginal_value["estimated_value_band"]),
            estimated_gain_metric=str(updated_marginal_value["estimated_gain_metric"]),
            rationale=str(updated_marginal_value["rationale"]),
            blockers_removed=list(updated_marginal_value["blockers_removed"]),
        ),
    )
    return PlanningExecutionResult(
        planning_bundle=updated_bundle,
        training_result=training_result,
    )


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _bundle_item(bundle: dict[str, Any], key: str) -> dict[str, Any]:
    payload = bundle.get(key)
    return dict(payload) if isinstance(payload, dict) else {}


def _string_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    text = str(value).strip()
    return [text] if text else []


def _dedupe_strings(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        stripped = str(value).strip()
        if not stripped:
            continue
        normalized = stripped.casefold()
        if normalized in seen:
            continue
        seen.add(normalized)
        result.append(stripped)
    return result


def _task_type_hint_for_target(domain_memo: dict[str, Any], target_column: str) -> str | None:
    for item in domain_memo.get("target_candidates", []):
        if not isinstance(item, dict):
            continue
        if str(item.get("target_column", "")).strip() == target_column:
            hint = str(item.get("task_type", "")).strip()
            return hint or None
    return None


def _resolve_target_column(
    *,
    frame: Any,
    task_brief: dict[str, Any],
    run_brief: dict[str, Any],
    domain_memo: dict[str, Any],
    dataset_profile: dict[str, Any],
) -> str:
    for candidate in (
        str(task_brief.get("target_column", "")).strip(),
        str(run_brief.get("target_column", "")).strip(),
    ):
        if candidate and candidate in frame.columns:
            return candidate
    for item in domain_memo.get("target_candidates", []):
        if not isinstance(item, dict):
            continue
        candidate = str(item.get("target_column", "")).strip()
        if candidate and candidate in frame.columns:
            return candidate
    for candidate in _string_list(dataset_profile.get("candidate_target_columns")):
        if candidate in frame.columns:
            return candidate
    raise ValueError("Slice 05 planning could not resolve a usable target column.")


def _select_route(
    *,
    dataset_profile: dict[str, Any],
    task_profile: dict[str, Any],
    focus_profile: dict[str, Any],
) -> dict[str, Any]:
    data_mode = str(dataset_profile.get("data_mode", "steady_state")).strip()
    task_type = str(task_profile.get("task_type", "")).strip()
    primary_objective = str(focus_profile.get("primary_objective", "accuracy")).strip()
    if data_mode == "time_series" and is_classification_task(task_type):
        return {
            "route_id": "temporal_calibrated_classifier_route",
            "title": "Temporal calibrated classifier route",
            "split_strategy": "blocked_time_order_70_15_15",
            "rationale": (
                "Timestamped classification data requires blocked splits and benefits from lag-aware "
                "comparators plus explicit threshold control."
            ),
            "priority_signal": primary_objective,
        }
    if data_mode == "time_series":
        return {
            "route_id": "temporal_lagged_regression_route",
            "title": "Temporal lagged regression route",
            "split_strategy": "blocked_time_order_70_15_15",
            "rationale": "Timestamped data supports lagged deterministic routes before any wider search.",
            "priority_signal": primary_objective,
        }
    if is_classification_task(task_type):
        return {
            "route_id": "calibrated_tabular_classifier_route",
            "title": "Calibrated tabular classifier route",
            "split_strategy": "stratified_deterministic_modulo_70_15_15",
            "rationale": "Classification data benefits from deterministic stratified splits and threshold-aware evaluation.",
            "priority_signal": primary_objective,
        }
    return {
        "route_id": "steady_state_tabular_regression_route",
        "title": "Steady-state tabular regression route",
        "split_strategy": "deterministic_modulo_70_15_15",
        "rationale": "The safest first builder route is a split-safe deterministic tabular regression baseline.",
        "priority_signal": primary_objective,
    }


def _resolve_primary_metric(
    *,
    optimization_profile: dict[str, Any],
    task_type: str,
) -> str:
    candidate = str(optimization_profile.get("primary_metric", "auto")).strip().lower().replace("-", "_")
    if candidate and candidate != "auto":
        return candidate
    if is_classification_task(task_type):
        if task_type in {"fraud_detection", "anomaly_detection"}:
            return "pr_auc"
        return "f1"
    return "mae"


def _resolve_secondary_metrics(
    *,
    optimization_profile: dict[str, Any],
    primary_metric: str,
) -> list[str]:
    secondary = [str(item).strip().lower().replace("-", "_") for item in optimization_profile.get("secondary_metrics", [])]
    secondary = [item for item in secondary if item and item != primary_metric]
    if secondary:
        return _dedupe_strings(secondary)
    if primary_metric == "mae":
        return ["rmse", "stability"]
    return ["log_loss", "reliability"]


def _selection_metric_for_primary_metric(*, primary_metric: str, task_type: str) -> str:
    aliases = {
        "stability": "mae",
        "calibration": "log_loss",
        "reliability": "log_loss" if is_classification_task(task_type) else "mae",
        "efficiency": "mae" if not is_classification_task(task_type) else "accuracy",
        "interpretability": "mae" if not is_classification_task(task_type) else "f1",
    }
    return aliases.get(primary_metric, primary_metric)


def _resolve_candidate_order(
    *,
    data_mode: str,
    task_type: str,
    optimization_profile: dict[str, Any],
) -> list[str]:
    bias_names = _string_list(optimization_profile.get("model_family_bias"))
    ordered: list[str] = []
    for bias_name in bias_names:
        ordered.extend(_bias_to_models(bias_name=bias_name, task_type=task_type, data_mode=data_mode))
    if data_mode == "time_series" and is_classification_task(task_type):
        ordered.extend(
            [
                "lagged_logistic_regression",
                "lagged_tree_classifier",
                "logistic_regression",
                "bagged_tree_classifier",
                "boosted_tree_classifier",
            ]
        )
    elif data_mode == "time_series":
        ordered.extend(
            [
                "lagged_linear",
                "lagged_tree_ensemble",
                "linear_ridge",
                "bagged_tree_ensemble",
                "boosted_tree_ensemble",
            ]
        )
    elif is_classification_task(task_type):
        ordered.extend(
            [
                "logistic_regression",
                "bagged_tree_classifier",
                "boosted_tree_classifier",
            ]
        )
    else:
        ordered.extend(
            [
                "linear_ridge",
                "bagged_tree_ensemble",
                "boosted_tree_ensemble",
            ]
        )
    return _dedupe_strings(ordered)


def _bias_to_models(*, bias_name: str, task_type: str, data_mode: str) -> list[str]:
    normalized = str(bias_name).strip().lower().replace("-", "_")
    if normalized == "linear_ridge":
        return ["logistic_regression"] if is_classification_task(task_type) else ["linear_ridge"]
    if normalized == "logistic":
        return ["lagged_logistic_regression", "logistic_regression"] if data_mode == "time_series" else ["logistic_regression"]
    if normalized in {"tree_small", "tree_classifier"}:
        return ["bagged_tree_classifier"] if is_classification_task(task_type) else ["bagged_tree_ensemble"]
    if normalized in {"tree_ensemble", "boosted_tree"}:
        return ["boosted_tree_classifier"] if is_classification_task(task_type) else ["boosted_tree_ensemble"]
    if normalized == "boosted_tree_classifier":
        return ["boosted_tree_classifier"]
    if normalized == "lagged_linear":
        return ["lagged_logistic_regression"] if is_classification_task(task_type) else ["lagged_linear"]
    if normalized == "lagged_tree":
        return ["lagged_tree_classifier"] if is_classification_task(task_type) else ["lagged_tree_ensemble"]
    return []


def _select_feature_columns(
    *,
    frame: Any,
    dataset_profile: dict[str, Any],
    domain_brief: dict[str, Any],
    feature_strategy_profile: dict[str, Any],
    target_column: str,
    timestamp_column: str | None,
    controls: PlanningControls,
) -> tuple[list[str], list[dict[str, Any]], list[dict[str, Any]]]:
    hard_excluded = set(_string_list(domain_brief.get("forbidden_features")))
    hard_excluded.update(_string_list(domain_brief.get("suspicious_columns")))
    hard_excluded.add(target_column)
    if timestamp_column:
        hard_excluded.add(timestamp_column)
    soft_warning_columns = set(_string_list(feature_strategy_profile.get("excluded_columns")))
    soft_warning_columns.update(_string_list(dataset_profile.get("suspicious_columns")))
    soft_warning_columns.update(_string_list(dataset_profile.get("hidden_key_candidates")))
    soft_warning_columns.update(_string_list(dataset_profile.get("entity_key_candidates")))

    numeric_candidates = _dedupe_strings(
        _string_list(dataset_profile.get("numeric_columns")) + _string_list(dataset_profile.get("binary_like_columns"))
    )
    scores: list[tuple[float, str]] = []
    for column in numeric_candidates:
        if column not in frame.columns or column in hard_excluded:
            continue
        missing_fraction = float(dict(dataset_profile.get("missing_fraction_by_column", {})).get(column, 0.0) or 0.0)
        score = 1.0 - min(0.95, missing_fraction)
        if bool(feature_strategy_profile.get("prioritize_simple_features", False)) and len(column) <= 18:
            score += 0.05
        if bool(feature_strategy_profile.get("prioritize_stability_features", False)):
            score += 0.03
        if column.lower().startswith(("sensor", "signal", "measure")):
            score += 0.04
        if column in soft_warning_columns:
            score -= 0.3
        if any(token in column.lower() for token in ("id", "key", "uuid", "guid")):
            score -= 0.15
        scores.append((score, column))
    scores.sort(key=lambda item: (-item[0], item[1]))
    feature_budget = min(
        controls.max_primary_features,
        max(4, min(len(scores), max(4, int(len(frame) // 5) if len(frame) else 4))),
    )
    selected = [column for _, column in scores[:feature_budget]]
    if not selected:
        fallback_scores: list[tuple[float, str]] = []
        for column in numeric_candidates:
            if column not in frame.columns or column in {target_column, timestamp_column}:
                continue
            if column in _string_list(domain_brief.get("forbidden_features")):
                continue
            missing_fraction = float(dict(dataset_profile.get("missing_fraction_by_column", {})).get(column, 0.0) or 0.0)
            fallback_score = 1.0 - min(0.95, missing_fraction)
            if column in soft_warning_columns:
                fallback_score -= 0.1
            fallback_scores.append((fallback_score, column))
        fallback_scores.sort(key=lambda item: (-item[0], item[1]))
        selected = [column for _, column in fallback_scores[: max(1, min(controls.max_primary_features, len(fallback_scores)))]]
    if not selected:
        raise ValueError("Slice 05 planning could not identify usable feature columns after deterministic fallback.")

    drop_reasons: list[dict[str, Any]] = []
    feature_risk_flags: list[dict[str, Any]] = []
    for column in sorted(hard_excluded):
        if column in frame.columns:
            drop_reasons.append({"column": column, "reason": "excluded_by_guardrail"})
    for column in sorted(soft_warning_columns):
        if column in frame.columns and column not in selected and column not in hard_excluded:
            drop_reasons.append(
                {
                    "column": column,
                    "reason": "deferred_due_to_heuristic_risk_signal",
                }
            )
    for column in selected:
        if column in soft_warning_columns:
            feature_risk_flags.append(
                {
                    "column": column,
                    "risk_type": "heuristic_warning",
                    "reason": "Retained despite heuristic risk because it remained one of the strongest usable numeric features.",
                }
            )
    for _, column in scores[feature_budget:]:
        if column not in selected:
            drop_reasons.append(
                {
                    "column": column,
                    "reason": "deferred_to_keep_the_first_route_compact_and_auditable",
                }
            )
    for column in _string_list(dataset_profile.get("categorical_columns")):
        if column != target_column and column in frame.columns:
            drop_reasons.append(
                {
                    "column": column,
                    "reason": "current_builder_route_is_numeric_first; categorical expansion remains a follow-up experiment",
                }
            )
    return selected, drop_reasons, feature_risk_flags


def _resolve_threshold_policy(
    *,
    task_type: str,
    primary_metric: str,
    focus_profile: dict[str, Any],
    task_brief: dict[str, Any],
) -> str | None:
    if not is_classification_task(task_type):
        return None
    if primary_metric == "pr_auc":
        return "favor_pr_auc"
    if primary_metric == "recall":
        return "favor_recall"
    if primary_metric == "precision":
        return "favor_precision"
    if primary_metric == "log_loss":
        return "auto"
    text = " ".join(
        _string_list(task_brief.get("success_criteria")) + _string_list(task_brief.get("failure_costs"))
    ).lower()
    if any(token in text for token in ("miss", "early warning", "catch failures", "scrap")):
        return "favor_recall"
    if str(focus_profile.get("primary_objective", "")).strip() == "value":
        return "favor_recall"
    return "favor_f1"


def _resolve_lag_horizon(*, dataset_profile: dict[str, Any], route: dict[str, Any], feature_count: int) -> int | None:
    if "temporal" not in str(route.get("route_id", "")):
        return None
    row_count = int(dataset_profile.get("row_count", 0) or 0)
    if row_count >= 120:
        return 8
    if row_count >= 48:
        return 5
    return max(3, min(4, feature_count))


def _build_alternatives(
    *,
    route: dict[str, Any],
    candidate_order: list[str],
    focus_profile: dict[str, Any],
    optimization_profile: dict[str, Any],
    task_profile: dict[str, Any],
    dataset_profile: dict[str, Any],
) -> list[dict[str, Any]]:
    alternatives: list[dict[str, Any]] = []
    for index, model_family in enumerate(candidate_order[:4], start=1):
        alternatives.append(
            {
                "alternative_id": f"alt_model_{index:02d}",
                "kind": "model_family",
                "model_family": model_family,
                "tradeoff": "primary_comparator" if index == 1 else "follow_up_comparator",
                "rationale": (
                    f"Focus profile emphasizes `{focus_profile.get('primary_objective', 'accuracy')}`, "
                    f"and optimization bias includes `{model_family}` as a credible local comparator."
                ),
            }
        )
    if _string_list(dataset_profile.get("entity_key_candidates")):
        alternatives.append(
            {
                "alternative_id": "alt_group_holdout",
                "kind": "evaluation",
                "strategy": "group_aware_holdout_candidate",
                "tradeoff": "higher_reliability_lower_data_efficiency",
                "rationale": "Entity-like keys were detected, so group-aware holdout remains a high-value reliability check.",
            }
        )
    if str(task_profile.get("task_type", "")).strip() != "regression":
        alternatives.append(
            {
                "alternative_id": "alt_threshold_stress_test",
                "kind": "decision_policy",
                "strategy": "threshold_sweep",
                "tradeoff": "value_vs_precision_frontier",
                "rationale": "Classification routes benefit from explicit threshold stress testing after the first baseline run.",
            }
        )
    return _dedupe_dicts(alternatives, key_field="alternative_id")


def _build_hypotheses(
    *,
    domain_memo: dict[str, Any],
    feature_strategy_profile: dict[str, Any],
    route: dict[str, Any],
    target_column: str,
) -> list[dict[str, Any]]:
    hypotheses: list[dict[str, Any]] = [
        {
            "hypothesis_id": "baseline_route_is_viable",
            "category": "route",
            "priority": "high",
            "title": f"{route['title']} should produce a stable first benchmark for `{target_column}`.",
            "expected_effect": "establishes the first trustworthy local baseline",
        }
    ]
    for index, item in enumerate(domain_memo.get("feature_hypotheses", [])[:4], start=1):
        if not isinstance(item, dict):
            continue
        rationale = str(item.get("rationale", "")).strip()
        if not rationale:
            continue
        hypotheses.append(
            {
                "hypothesis_id": f"feature_hypothesis_{index:02d}",
                "category": "feature",
                "priority": str(item.get("priority", "medium")),
                "title": rationale,
                "expected_effect": "may improve representation quality or route robustness",
            }
        )
    for index, item in enumerate(domain_memo.get("additional_data_hypotheses", [])[:3], start=1):
        if not isinstance(item, dict):
            continue
        hypotheses.append(
            {
                "hypothesis_id": f"data_hypothesis_{index:02d}",
                "category": "data",
                "priority": str(item.get("priority", "medium")),
                "title": str(item.get("need", "additional_data")).replace("_", " "),
                "expected_effect": str(item.get("rationale", "additional data may reduce route ambiguity")),
            }
        )
    for family in _string_list(feature_strategy_profile.get("preferred_feature_families"))[:3]:
        hypotheses.append(
            {
                "hypothesis_id": f"feature_family_{family}",
                "category": "feature_family",
                "priority": "medium",
                "title": f"Expanding into `{family}` may improve the next route revision.",
                "expected_effect": "targeted feature engineering beyond the first deterministic floor",
            }
        )
    return _dedupe_dicts(hypotheses, key_field="hypothesis_id")


def _build_experiment_priorities(
    *,
    route: dict[str, Any],
    candidate_order: list[str],
    dataset_profile: dict[str, Any],
    focus_profile: dict[str, Any],
    feature_strategy_profile: dict[str, Any],
) -> list[dict[str, Any]]:
    priorities: list[dict[str, Any]] = [
        {
            "experiment_id": "execute_selected_route",
            "priority": 1,
            "status": "queued",
            "title": route["title"],
            "expected_information_gain": "high",
            "rationale": "A first deterministic builder run is required before richer challenger logic becomes meaningful.",
        }
    ]
    if len(candidate_order) > 1:
        priorities.append(
            {
                "experiment_id": "compare_top_alternative_family",
                "priority": 2,
                "status": "queued",
                "title": f"Stress the route against `{candidate_order[1]}` as the first challenger family.",
                "expected_information_gain": "medium",
                "rationale": "A nearby model-family comparison reveals whether the selected route is robust or fragile.",
            }
        )
    if str(dataset_profile.get("leakage_risk_level", "low")) != "low":
        priorities.append(
            {
                "experiment_id": "leakage_guardrail_ablation",
                "priority": 3,
                "status": "queued",
                "title": "Re-run with strict leakage guardrails and explicit forbidden-feature ablation.",
                "expected_information_gain": "high",
                "rationale": "Leakage warnings mean route quality must survive stricter exclusions.",
            }
        )
    if _string_list(dataset_profile.get("entity_key_candidates")):
        priorities.append(
            {
                "experiment_id": "group_holdout_probe",
                "priority": 4,
                "status": "queued",
                "title": "Probe a group-aware holdout variant.",
                "expected_information_gain": "medium",
                "rationale": "Entity-like keys suggest that naive splits may overstate generalization.",
            }
        )
    if "missingness_indicators" in _string_list(feature_strategy_profile.get("preferred_feature_families")):
        priorities.append(
            {
                "experiment_id": "missingness_feature_expansion",
                "priority": 5,
                "status": "queued",
                "title": "Add missingness indicators in the next builder revision.",
                "expected_information_gain": "medium",
                "rationale": "Feature strategy already suggests missingness carries signal worth testing.",
            }
        )
    return priorities


def _build_marginal_value(
    *,
    priority_items: list[dict[str, Any]],
    dataset_profile: dict[str, Any],
    primary_metric: str,
    executed: bool,
) -> dict[str, Any]:
    recommended = next(
        (
            item
            for item in priority_items
            if str(item.get("status", "queued")) != "completed"
        ),
        priority_items[0] if priority_items else {"experiment_id": "none", "title": "none"},
    )
    leakage = str(dataset_profile.get("leakage_risk_level", "low")).strip().lower()
    value_band = "high" if not executed or leakage != "low" else "medium"
    blockers = ["route_quality_baseline"] if not executed else ["next_challenger_signal"]
    return {
        "recommended_experiment_id": str(recommended.get("experiment_id", "none")),
        "estimated_value_band": value_band,
        "estimated_gain_metric": primary_metric,
        "rationale": (
            "The next experiment is still likely to change the current judgment materially."
            if not executed
            else "The next experiment is less about basic viability and more about robustness or challenger pressure."
        ),
        "blockers_removed": blockers,
    }


def _advisory_alternatives(payload: dict[str, Any]) -> list[dict[str, Any]]:
    alternatives: list[dict[str, Any]] = []
    for index, item in enumerate(payload.get("alternative_routes", []), start=1):
        if not isinstance(item, dict):
            continue
        route_id = str(item.get("route_id", f"advisory_alt_{index:02d}")).strip()
        title = str(item.get("title", route_id)).strip()
        reason = str(item.get("reason", "")).strip()
        tradeoff = str(item.get("tradeoff", "advisory_tradeoff")).strip()
        if title:
            alternatives.append(
                {
                    "alternative_id": route_id,
                    "kind": "advisory_route",
                    "title": title,
                    "tradeoff": tradeoff,
                    "rationale": reason or "Optional local advisory proposed an additional route.",
                }
            )
    return alternatives


def _advisory_hypotheses(payload: dict[str, Any]) -> list[dict[str, Any]]:
    hypotheses: list[dict[str, Any]] = []
    for index, item in enumerate(_string_list(payload.get("extra_hypotheses")), start=1):
        hypotheses.append(
            {
                "hypothesis_id": f"advisory_hypothesis_{index:02d}",
                "category": "advisory",
                "priority": "medium",
                "title": item,
                "expected_effect": "optional local advisory expects this to change route quality or interpretation",
            }
        )
    return hypotheses


def _advisory_experiments(payload: dict[str, Any]) -> list[dict[str, Any]]:
    experiments: list[dict[str, Any]] = []
    for index, item in enumerate(_string_list(payload.get("experiment_clues")), start=1):
        experiments.append(
            {
                "experiment_id": f"advisory_experiment_{index:02d}",
                "priority": 10 + index,
                "status": "queued",
                "title": item,
                "expected_information_gain": "medium",
                "rationale": "Optional local advisory highlighted this as a useful follow-up experiment.",
            }
        )
    return experiments


def _merge_marginal_value_hint(
    *,
    marginal_value: dict[str, Any],
    advisory_payload: dict[str, Any],
) -> dict[str, Any]:
    hint = str(advisory_payload.get("marginal_value_hint", "")).strip()
    if not hint:
        return marginal_value
    merged = dict(marginal_value)
    merged["rationale"] = f"{marginal_value['rationale']} Advisory note: {hint}"
    return merged


def _plan_summary(*, route: dict[str, Any], target_column: str, primary_metric: str) -> str:
    return (
        f"Strategist selected `{route['title']}` for target `{target_column}` with `{primary_metric}` "
        "as the first execution metric and a deterministic Builder handoff."
    )


def _alternatives_summary(alternatives: list[dict[str, Any]]) -> str:
    return f"Recorded {len(alternatives)} route or comparator alternative(s) around the selected Slice 05 plan."


def _hypotheses_summary(hypotheses: list[dict[str, Any]]) -> str:
    return f"Promoted {len(hypotheses)} testable hypothesis item(s) into the first execution cycle."


def _priority_summary(items: list[dict[str, Any]]) -> str:
    return f"Queued {len(items)} prioritized experiment(s) around the first Builder route."


def _mark_priority_completed(items: list[dict[str, Any]], experiment_id: str) -> list[dict[str, Any]]:
    updated: list[dict[str, Any]] = []
    for item in items:
        payload = dict(item)
        if str(payload.get("experiment_id", "")) == experiment_id:
            payload["status"] = "completed"
        updated.append(payload)
    return updated


def _dedupe_dicts(items: list[dict[str, Any]], *, key_field: str) -> list[dict[str, Any]]:
    seen: set[str] = set()
    result: list[dict[str, Any]] = []
    for item in items:
        key = str(item.get(key_field, "")).strip()
        if not key or key in seen:
            continue
        seen.add(key)
        result.append(item)
    return result


def _optional_str(value: Any) -> str | None:
    text = str(value).strip() if value is not None else ""
    return text or None


def _optional_int(value: Any) -> int | None:
    if value in (None, "", 0):
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _optional_float(value: Any) -> float | None:
    if value in (None, ""):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None
