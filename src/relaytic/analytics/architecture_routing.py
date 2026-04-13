"""Canonical architecture registry and router artifacts for Slice 15B."""

from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any

from relaytic.core.json_utils import write_json
from relaytic.modeling.estimator_adapters import (
    family_adapter_available,
    family_adapter_module,
    family_adapter_version,
)

from .task_detection import is_classification_task


ARCHITECTURE_REGISTRY_SCHEMA_VERSION = "relaytic.architecture_registry.v1"
ARCHITECTURE_ROUTER_REPORT_SCHEMA_VERSION = "relaytic.architecture_router_report.v1"
CANDIDATE_FAMILY_MATRIX_SCHEMA_VERSION = "relaytic.candidate_family_matrix.v1"
ARCHITECTURE_FIT_REPORT_SCHEMA_VERSION = "relaytic.architecture_fit_report.v1"
FAMILY_CAPABILITY_MATRIX_SCHEMA_VERSION = "relaytic.family_capability_matrix.v1"
ARCHITECTURE_ABLATION_REPORT_SCHEMA_VERSION = "relaytic.architecture_ablation_report.v1"
FAMILY_REGISTRY_EXTENSION_SCHEMA_VERSION = "relaytic.family_registry_extension.v1"
FAMILY_READINESS_REPORT_SCHEMA_VERSION = "relaytic.family_readiness_report.v1"
FAMILY_ELIGIBILITY_MATRIX_SCHEMA_VERSION = "relaytic.family_eligibility_matrix.v1"
FAMILY_PROBE_POLICY_SCHEMA_VERSION = "relaytic.family_probe_policy.v1"
CATEGORICAL_STRATEGY_REPORT_SCHEMA_VERSION = "relaytic.categorical_strategy_report.v1"
FAMILY_SPECIALIZATION_REPORT_SCHEMA_VERSION = "relaytic.family_specialization_report.v1"


ARCHITECTURE_ROUTING_FILENAMES = {
    "architecture_registry": "architecture_registry.json",
    "architecture_router_report": "architecture_router_report.json",
    "candidate_family_matrix": "candidate_family_matrix.json",
    "architecture_fit_report": "architecture_fit_report.json",
    "family_capability_matrix": "family_capability_matrix.json",
    "architecture_ablation_report": "architecture_ablation_report.json",
    "family_registry_extension": "family_registry_extension.json",
    "family_readiness_report": "family_readiness_report.json",
    "family_eligibility_matrix": "family_eligibility_matrix.json",
    "family_probe_policy": "family_probe_policy.json",
    "categorical_strategy_report": "categorical_strategy_report.json",
    "family_specialization_report": "family_specialization_report.json",
}


SEARCHABLE_FAMILY_STACK = {
    "linear_ridge",
    "logistic_regression",
    "bagged_tree_ensemble",
    "boosted_tree_ensemble",
    "hist_gradient_boosting_ensemble",
    "extra_trees_ensemble",
    "catboost_ensemble",
    "xgboost_ensemble",
    "lightgbm_ensemble",
    "bagged_tree_classifier",
    "boosted_tree_classifier",
    "hist_gradient_boosting_classifier",
    "extra_trees_classifier",
    "catboost_classifier",
    "xgboost_classifier",
    "lightgbm_classifier",
}


def default_architecture_candidate_order(*, task_type: str, data_mode: str) -> list[str]:
    """Return the deterministic baseline candidate ladder before routing adjustments."""
    if data_mode == "time_series" and is_classification_task(task_type):
        return [
            "lagged_logistic_regression",
            "lagged_tree_classifier",
            "logistic_regression",
            "hist_gradient_boosting_classifier",
            "extra_trees_classifier",
            "bagged_tree_classifier",
            "boosted_tree_classifier",
        ]
    if data_mode == "time_series":
        return [
            "lagged_linear",
            "lagged_tree_ensemble",
            "linear_ridge",
            "hist_gradient_boosting_ensemble",
            "extra_trees_ensemble",
            "bagged_tree_ensemble",
            "boosted_tree_ensemble",
        ]
    if is_classification_task(task_type):
        return [
            "logistic_regression",
            "bagged_tree_classifier",
            "boosted_tree_classifier",
            "hist_gradient_boosting_classifier",
            "extra_trees_classifier",
        ]
    return [
        "linear_ridge",
        "bagged_tree_ensemble",
        "boosted_tree_ensemble",
        "hist_gradient_boosting_ensemble",
        "extra_trees_ensemble",
    ]


def sync_architecture_routing_artifacts(
    run_dir: str | Path,
    *,
    investigation_bundle: dict[str, Any] | None,
    planning_bundle: dict[str, Any] | None,
    route_prior_context: dict[str, Any] | None = None,
    benchmark_bundle: dict[str, Any] | None = None,
) -> dict[str, Path]:
    """Build and write the canonical architecture-routing artifact family."""
    artifacts = build_architecture_routing_artifacts(
        investigation_bundle=investigation_bundle,
        planning_bundle=planning_bundle,
        route_prior_context=route_prior_context,
        benchmark_bundle=benchmark_bundle,
    )
    root = Path(run_dir)
    root.mkdir(parents=True, exist_ok=True)
    return {
        key: write_json(
            root / filename,
            artifacts[key],
            indent=2,
            ensure_ascii=False,
            sort_keys=True,
        )
        for key, filename in ARCHITECTURE_ROUTING_FILENAMES.items()
    }


def read_architecture_routing_artifacts(run_dir: str | Path) -> dict[str, Any]:
    """Read the canonical architecture-routing artifact family."""
    root = Path(run_dir)
    payload: dict[str, Any] = {}
    for key, filename in ARCHITECTURE_ROUTING_FILENAMES.items():
        path = root / filename
        if not path.exists():
            continue
        payload[key] = json.loads(path.read_text(encoding="utf-8"))
    return payload


def build_architecture_routing_artifacts(
    *,
    investigation_bundle: dict[str, Any] | None,
    planning_bundle: dict[str, Any] | None,
    route_prior_context: dict[str, Any] | None = None,
    benchmark_bundle: dict[str, Any] | None = None,
) -> dict[str, dict[str, Any]]:
    """Construct canonical architecture-routing artifacts from current run truth."""
    generated_at = _utc_now()
    investigation_bundle = investigation_bundle or {}
    planning_bundle = planning_bundle or {}
    route_prior_context = route_prior_context or {}
    benchmark_bundle = benchmark_bundle or {}

    dataset_profile = _bundle_item(investigation_bundle, "dataset_profile")
    optimization_profile = _bundle_item(investigation_bundle, "optimization_profile")
    plan = _bundle_item(planning_bundle, "plan")
    task_profile = dict(plan.get("task_profile") or {})
    task_type = _clean_text(task_profile.get("task_type")) or _clean_text(plan.get("task_type")) or "unknown"
    data_mode = _clean_text(task_profile.get("data_mode")) or _clean_text(plan.get("data_mode")) or _clean_text(dataset_profile.get("data_mode")) or "steady_state"
    row_count = int(task_profile.get("row_count", 0) or dataset_profile.get("row_count", 0) or 0)
    numeric_columns = _string_list(dataset_profile.get("numeric_columns"))
    categorical_columns = _string_list(dataset_profile.get("categorical_columns"))
    feature_count = max(
        len(_string_list(plan.get("feature_columns"))),
        len(numeric_columns) + len(categorical_columns),
        int(dataset_profile.get("column_count", 0) or 0) - 1,
        0,
    )
    class_count = int(task_profile.get("class_count", 0) or 0)
    minority_fraction = _optional_float(task_profile.get("minority_class_fraction"))
    categorical_ratio = len(categorical_columns) / max(len(numeric_columns) + len(categorical_columns), 1)
    missingness = _mean_missingness(dataset_profile)
    timestamp_column = _clean_text(dataset_profile.get("timestamp_column")) or _clean_text(plan.get("timestamp_column"))
    benchmark_parity_report = _bundle_item(benchmark_bundle, "benchmark_parity_report")
    benchmark_status = _clean_text(benchmark_parity_report.get("parity_status"))
    baseline_order = [
        item
        for item in route_prior_context.get("baseline_candidate_order", [])
        if _clean_text(item)
    ] or default_architecture_candidate_order(task_type=task_type, data_mode=data_mode)
    adjusted_order = [
        item
        for item in route_prior_context.get("adjusted_candidate_order", [])
        if _clean_text(item)
    ] or list(baseline_order)
    preferred_family = adjusted_order[0] if adjusted_order != baseline_order and adjusted_order else None
    adjusted_rank = {name: index for index, name in enumerate(adjusted_order)}
    memory_bias = {
        _clean_text(item.get("model_family")): _optional_float(item.get("score")) or 0.0
        for item in route_prior_context.get("family_bias", [])
        if isinstance(item, dict) and _clean_text(item.get("model_family"))
    }
    explicit_biases = _string_list(optimization_profile.get("model_family_bias"))
    sequence_shadow_ready = (
        data_mode == "time_series"
        and bool(timestamp_column)
        and row_count >= 256
        and feature_count <= 128
    )
    sequence_live_allowed = False
    sequence_rejection_reason = None
    if data_mode != "time_series":
        sequence_rejection_reason = "Relaytic rejected sequence-family routing because the task contract does not prove ordered temporal structure."
    elif not sequence_shadow_ready:
        sequence_rejection_reason = (
            "Relaytic kept sequence families out of the live ladder because the current timestamped task does not yet show enough sequence support for reliable promotion."
        )

    registry_rows: list[dict[str, Any]] = []
    candidate_rows: list[dict[str, Any]] = []
    excluded_rows: list[dict[str, Any]] = []
    fit_rows: list[dict[str, Any]] = []

    for template in _registry_templates():
        row = dict(template)
        family_id = str(row["family_id"])
        availability = _availability_status(family_id=family_id, sequence_shadow_ready=sequence_shadow_ready)
        row.update(availability)
        score, reasons, factor_scores, exclusion_reason = _score_family(
            family_id=family_id,
            row=row,
            task_type=task_type,
            data_mode=data_mode,
            row_count=row_count,
            feature_count=feature_count,
            categorical_ratio=categorical_ratio,
            missingness=missingness,
            class_count=class_count,
            minority_fraction=minority_fraction,
            preferred_family=preferred_family,
            memory_bias=memory_bias,
            benchmark_status=benchmark_status,
            explicit_biases=explicit_biases,
        )
        row["router_score"] = round(score, 6)
        row["router_reasons"] = reasons
        row["factor_scores"] = factor_scores
        registry_rows.append(row)
        fit_rows.append(
            {
                "family_id": family_id,
                "family_title": row["family_title"],
                "router_score": round(score, 6),
                "availability_status": row["availability_status"],
                "training_support": row["training_support"],
                "live_candidate": row["live_candidate"],
                "factor_scores": factor_scores,
                "reasons": reasons,
                "exclusion_reason": exclusion_reason,
            }
        )
        if exclusion_reason or not row["live_candidate"] or row["availability_status"] != "available":
            excluded_rows.append(
                {
                    "family_id": family_id,
                    "family_title": row["family_title"],
                    "availability_status": row["availability_status"],
                    "live_candidate": row["live_candidate"],
                    "reason": exclusion_reason
                    or "Relaytic kept this family out of the live candidate order because it is not currently trainable on this machine.",
                }
            )
            continue
        candidate_rows.append(
            {
                "family_id": family_id,
                "family_title": row["family_title"],
                "router_score": round(score, 6),
                "availability_status": row["availability_status"],
                "task_family": row["task_family"],
                "time_series_level": row["time_series_level"],
                "selection_reason": reasons[0] if reasons else "Router score only.",
            }
        )

    ordered_candidates = sorted(
        candidate_rows,
        key=lambda item: (
            -float(item.get("router_score", 0.0)),
            adjusted_rank.get(item["family_id"], len(adjusted_rank) + _candidate_tiebreak(item["family_id"])),
            _candidate_tiebreak(item["family_id"]),
        ),
    )
    for index, row in enumerate(ordered_candidates, start=1):
        row["rank"] = index
    candidate_order = [str(item["family_id"]) for item in ordered_candidates]
    recommended_primary_family = candidate_order[0] if candidate_order else None
    best_live = next(iter(ordered_candidates), {})
    temporal_ladder = _temporal_ladder(
        task_type=task_type,
        data_mode=data_mode,
        sequence_shadow_ready=sequence_shadow_ready,
    )
    architecture_registry = {
        "schema_version": ARCHITECTURE_REGISTRY_SCHEMA_VERSION,
        "generated_at": generated_at,
        "status": "ok",
        "task_type": task_type,
        "data_mode": data_mode,
        "family_count": len(registry_rows),
        "available_family_count": sum(1 for row in registry_rows if row.get("availability_status") == "available"),
        "optional_unavailable_count": sum(
            1
            for row in registry_rows
            if row.get("family_role") == "optional_adapter" and row.get("availability_status") != "available"
        ),
        "families": registry_rows,
    }
    architecture_router_report = {
        "schema_version": ARCHITECTURE_ROUTER_REPORT_SCHEMA_VERSION,
        "generated_at": generated_at,
        "status": "ok" if candidate_order else "partial",
        "task_type": task_type,
        "data_mode": data_mode,
        "recommended_primary_family": recommended_primary_family,
        "candidate_order": candidate_order,
        "benchmark_evidence_status": benchmark_status or "not_available_yet",
        "workspace_analog_status": _clean_text(route_prior_context.get("status")) or "not_available",
        "workspace_analog_influence": bool(memory_bias) or adjusted_order != baseline_order,
        "explicit_model_family_bias": explicit_biases,
        "baseline_candidate_order": baseline_order,
        "memory_adjusted_candidate_order": adjusted_order,
        "sequence_live_allowed": sequence_live_allowed,
        "sequence_shadow_ready": sequence_shadow_ready,
        "sequence_rejection_reason": sequence_rejection_reason,
        "top_selection_reason": _clean_text(best_live.get("selection_reason")),
        "summary": _router_summary(
            task_type=task_type,
            data_mode=data_mode,
            recommended_primary_family=recommended_primary_family,
            sequence_shadow_ready=sequence_shadow_ready,
            sequence_rejection_reason=sequence_rejection_reason,
        ),
    }
    candidate_family_matrix = {
        "schema_version": CANDIDATE_FAMILY_MATRIX_SCHEMA_VERSION,
        "generated_at": generated_at,
        "status": "ok" if ordered_candidates else "partial",
        "candidate_count": len(ordered_candidates),
        "candidates": ordered_candidates,
        "excluded_families": excluded_rows,
    }
    architecture_fit_report = {
        "schema_version": ARCHITECTURE_FIT_REPORT_SCHEMA_VERSION,
        "generated_at": generated_at,
        "status": "ok",
        "task_type": task_type,
        "data_mode": data_mode,
        "row_count": row_count,
        "feature_count": feature_count,
        "categorical_ratio": round(categorical_ratio, 4),
        "mean_missingness": round(missingness, 4),
        "class_count": class_count,
        "minority_class_fraction": minority_fraction,
        "fit_rows": sorted(
            fit_rows,
            key=lambda item: (-float(item.get("router_score", 0.0)), _candidate_tiebreak(str(item.get("family_id", "")))),
        ),
    }
    family_capability_matrix = {
        "schema_version": FAMILY_CAPABILITY_MATRIX_SCHEMA_VERSION,
        "generated_at": generated_at,
        "status": "ok",
        "families": [
            {
                "family_id": row["family_id"],
                "family_title": row["family_title"],
                "family_role": row["family_role"],
                "task_family": row["task_family"],
                "time_series_level": row["time_series_level"],
                "categorical_affinity": row["categorical_affinity"],
                "small_data_affinity": row["small_data_affinity"],
                "multiclass_affinity": row["multiclass_affinity"],
                "rare_event_affinity": row["rare_event_affinity"],
                "availability_status": row["availability_status"],
                "training_support": row["training_support"],
                "inference_support": row["inference_support"],
            }
            for row in registry_rows
        ],
    }
    architecture_ablation_report = {
        "schema_version": ARCHITECTURE_ABLATION_REPORT_SCHEMA_VERSION,
        "generated_at": generated_at,
        "status": "ok",
        "ordinary_tabular_baseline": "logistic_regression" if is_classification_task(task_type) else "linear_ridge",
        "lagged_tabular_baseline": (
            "lagged_logistic_regression"
            if data_mode == "time_series" and is_classification_task(task_type)
            else "lagged_linear"
            if data_mode == "time_series"
            else None
        ),
        "stronger_tree_or_boosting_candidates": [
            row["family_id"]
            for row in ordered_candidates
            if row["family_id"] not in {"linear_ridge", "logistic_regression", "lagged_linear", "lagged_logistic_regression"}
        ][:4],
        "shadow_sequence_candidates": [
            row["family_id"]
            for row in registry_rows
            if row.get("family_role") == "shadow_candidate"
        ],
        "temporal_ladder": temporal_ladder,
        "summary": _ablation_summary(
            data_mode=data_mode,
            recommended_primary_family=recommended_primary_family,
            sequence_shadow_ready=sequence_shadow_ready,
        ),
    }
    fit_row_by_family = {
        str(item.get("family_id", "")).strip(): dict(item)
        for item in fit_rows
        if str(item.get("family_id", "")).strip()
    }
    categorical_strategy_report = _build_categorical_strategy_report(
        generated_at=generated_at,
        task_type=task_type,
        categorical_columns=categorical_columns,
        categorical_ratio=categorical_ratio,
        candidate_order=candidate_order,
        registry_rows=registry_rows,
        class_count=class_count,
    )
    family_probe_policy = _build_family_probe_policy(
        generated_at=generated_at,
        candidate_order=candidate_order,
        task_type=task_type,
        categorical_strategy=str(categorical_strategy_report.get("selected_strategy") or ""),
        registry_rows=registry_rows,
    )
    family_specialization_report = _build_family_specialization_report(
        generated_at=generated_at,
        task_type=task_type,
        row_count=row_count,
        feature_count=feature_count,
        categorical_ratio=categorical_ratio,
        class_count=class_count,
        minority_fraction=minority_fraction,
        candidate_order=candidate_order,
    )
    family_readiness_report = {
        "schema_version": FAMILY_READINESS_REPORT_SCHEMA_VERSION,
        "generated_at": generated_at,
        "status": "ok",
        "adapter_ready_family_count": sum(
            1
            for row in registry_rows
            if row.get("family_role") == "optional_adapter" and row.get("availability_status") == "available"
        ),
        "rows": [
            {
                "family_id": row["family_id"],
                "family_title": row["family_title"],
                "family_role": row["family_role"],
                "availability_status": row["availability_status"],
                "adapter_module": row.get("adapter_module"),
                "adapter_version": row.get("adapter_version"),
                "training_support": row["training_support"],
                "inference_support": row["inference_support"],
                "live_candidate": row["live_candidate"],
                "readiness_reason": _family_readiness_reason(row=row),
            }
            for row in registry_rows
        ],
    }
    family_eligibility_matrix = {
        "schema_version": FAMILY_ELIGIBILITY_MATRIX_SCHEMA_VERSION,
        "generated_at": generated_at,
        "status": "ok" if registry_rows else "partial",
        "eligible_family_count": len(candidate_order),
        "rows": [
            {
                "family_id": row["family_id"],
                "family_title": row["family_title"],
                "family_role": row["family_role"],
                "availability_status": row["availability_status"],
                "eligible": row["family_id"] in candidate_order,
                "live_candidate": row["live_candidate"],
                "searchable": bool(row["training_support"]) and row["family_id"] in SEARCHABLE_FAMILY_STACK,
                "probe_tier": _family_probe_tier(
                    family_id=row["family_id"],
                    tier_one=[str(item) for item in family_probe_policy.get("tier_one_families", []) if str(item).strip()],
                    tier_two=[str(item) for item in family_probe_policy.get("tier_two_families", []) if str(item).strip()],
                ),
                "categorical_priority": row["family_id"] in {
                    str(item)
                    for item in family_specialization_report.get("categorical_priority_families", [])
                    if str(item).strip()
                },
                "small_data_specialist": row["family_id"] in {
                    str(item)
                    for item in family_specialization_report.get("small_data_specialist_families", [])
                    if str(item).strip()
                },
                "multiclass_specialist": bool(class_count >= 3 and row["family_id"] in {
                    "hist_gradient_boosting_classifier",
                    "extra_trees_classifier",
                    "catboost_classifier",
                    "xgboost_classifier",
                    "lightgbm_classifier",
                    "tabpfn_classifier",
                }),
                "rare_event_specialist": bool(
                    ((minority_fraction is not None and minority_fraction <= 0.20) or task_type in {"fraud_detection", "anomaly_detection"})
                    and row["family_id"] in {
                        "boosted_tree_classifier",
                        "hist_gradient_boosting_classifier",
                        "catboost_classifier",
                        "xgboost_classifier",
                        "lightgbm_classifier",
                        "lagged_tree_classifier",
                    }
                ),
                "block_reason": _clean_text(dict(fit_row_by_family.get(row["family_id"], {})).get("exclusion_reason"))
                or (None if row["family_id"] in candidate_order else _family_readiness_reason(row=row)),
            }
            for row in registry_rows
        ],
    }
    family_registry_extension = {
        "schema_version": FAMILY_REGISTRY_EXTENSION_SCHEMA_VERSION,
        "generated_at": generated_at,
        "status": "ok",
        "task_type": task_type,
        "data_mode": data_mode,
        "first_class_builtin_families": [
            row["family_id"]
            for row in registry_rows
            if row.get("family_role") == "deterministic_builtin" and row.get("training_support")
        ],
        "first_class_optional_adapter_families": [
            row["family_id"]
            for row in registry_rows
            if row.get("family_role") == "optional_adapter" and row.get("availability_status") == "available"
        ],
        "shadow_candidate_families": [
            row["family_id"]
            for row in registry_rows
            if row.get("family_role") == "shadow_candidate"
        ],
        "eligible_family_count": len(candidate_order),
        "adapter_ready_family_count": int(family_readiness_report.get("adapter_ready_family_count", 0) or 0),
        "searchable_family_count": sum(
            1
            for row in registry_rows
            if bool(row.get("training_support")) and row.get("family_id") in SEARCHABLE_FAMILY_STACK
        ),
        "summary": (
            f"Relaytic widened the first-class family stack to `{len(candidate_order)}` eligible live family/families "
            f"with categorical strategy `{categorical_strategy_report.get('selected_strategy')}`."
        ),
    }
    return {
        "architecture_registry": architecture_registry,
        "architecture_router_report": architecture_router_report,
        "candidate_family_matrix": candidate_family_matrix,
        "architecture_fit_report": architecture_fit_report,
        "family_capability_matrix": family_capability_matrix,
        "architecture_ablation_report": architecture_ablation_report,
        "family_registry_extension": family_registry_extension,
        "family_readiness_report": family_readiness_report,
        "family_eligibility_matrix": family_eligibility_matrix,
        "family_probe_policy": family_probe_policy,
        "categorical_strategy_report": categorical_strategy_report,
        "family_specialization_report": family_specialization_report,
    }


def _registry_templates() -> list[dict[str, Any]]:
    return [
        _family_template("linear_ridge", "Ridge baseline", "regression", "deterministic_builtin", "static", "low", "high", "n/a", "n/a"),
        _family_template("lagged_linear", "Lagged ridge baseline", "regression", "deterministic_builtin", "lagged", "low", "medium", "n/a", "n/a"),
        _family_template("bagged_tree_ensemble", "Bagged tree ensemble", "regression", "deterministic_builtin", "static", "medium", "medium", "n/a", "n/a"),
        _family_template("boosted_tree_ensemble", "Boosted tree ensemble", "regression", "deterministic_builtin", "static", "medium", "medium", "n/a", "n/a"),
        _family_template("hist_gradient_boosting_ensemble", "Histogram gradient boosting", "regression", "deterministic_builtin", "static", "medium", "medium", "n/a", "n/a"),
        _family_template("extra_trees_ensemble", "Extra-trees ensemble", "regression", "deterministic_builtin", "static", "medium", "medium", "n/a", "n/a"),
        _family_template("catboost_ensemble", "CatBoost regressor", "regression", "optional_adapter", "static", "high", "medium", "n/a", "n/a"),
        _family_template("xgboost_ensemble", "XGBoost regressor", "regression", "optional_adapter", "static", "medium", "medium", "n/a", "n/a"),
        _family_template("lightgbm_ensemble", "LightGBM regressor", "regression", "optional_adapter", "static", "medium", "medium", "n/a", "n/a"),
        _family_template("logistic_regression", "Logistic baseline", "classification", "deterministic_builtin", "static", "low", "high", "medium", "low"),
        _family_template("lagged_logistic_regression", "Lagged logistic baseline", "classification", "deterministic_builtin", "lagged", "low", "medium", "medium", "medium"),
        _family_template("bagged_tree_classifier", "Bagged tree classifier", "classification", "deterministic_builtin", "static", "medium", "medium", "medium", "medium"),
        _family_template("boosted_tree_classifier", "Boosted tree classifier", "classification", "deterministic_builtin", "static", "medium", "medium", "medium", "high"),
        _family_template("hist_gradient_boosting_classifier", "Histogram gradient boosting classifier", "classification", "deterministic_builtin", "static", "medium", "medium", "high", "high"),
        _family_template("extra_trees_classifier", "Extra-trees classifier", "classification", "deterministic_builtin", "static", "medium", "medium", "high", "medium"),
        _family_template("lagged_tree_classifier", "Lagged tree classifier", "classification", "deterministic_builtin", "lagged", "medium", "medium", "medium", "high"),
        _family_template("catboost_classifier", "CatBoost classifier", "classification", "optional_adapter", "static", "high", "medium", "high", "high"),
        _family_template("xgboost_classifier", "XGBoost classifier", "classification", "optional_adapter", "static", "medium", "medium", "high", "high"),
        _family_template("lightgbm_classifier", "LightGBM classifier", "classification", "optional_adapter", "static", "medium", "medium", "high", "high"),
        _family_template("tabpfn_classifier", "TabPFN classifier", "classification", "optional_adapter", "static", "medium", "very_high", "high", "medium"),
        _family_template("sequence_lstm_candidate", "LSTM sequence candidate", "classification_or_regression", "shadow_candidate", "sequence", "medium", "low", "medium", "medium"),
        _family_template("temporal_transformer_candidate", "Temporal transformer candidate", "classification_or_regression", "shadow_candidate", "sequence", "medium", "low", "medium", "medium"),
    ]


def _family_template(
    family_id: str,
    family_title: str,
    task_family: str,
    family_role: str,
    time_series_level: str,
    categorical_affinity: str,
    small_data_affinity: str,
    multiclass_affinity: str,
    rare_event_affinity: str,
) -> dict[str, Any]:
    return {
        "family_id": family_id,
        "family_title": family_title,
        "task_family": task_family,
        "family_role": family_role,
        "time_series_level": time_series_level,
        "categorical_affinity": categorical_affinity,
        "small_data_affinity": small_data_affinity,
        "multiclass_affinity": multiclass_affinity,
        "rare_event_affinity": rare_event_affinity,
    }


def _availability_status(*, family_id: str, sequence_shadow_ready: bool) -> dict[str, Any]:
    if family_id in {"sequence_lstm_candidate", "temporal_transformer_candidate"}:
        return {
            "availability_status": "shadow_only" if sequence_shadow_ready else "not_ready",
            "training_support": False,
            "inference_support": False,
            "live_candidate": False,
            "adapter_module": None,
            "adapter_version": None,
        }
    adapter_module = family_adapter_module(family_id)
    if adapter_module is None:
        return {
            "availability_status": "available",
            "training_support": True,
            "inference_support": True,
            "live_candidate": True,
            "adapter_module": None,
            "adapter_version": None,
        }
    available = family_adapter_available(family_id)
    return {
        "availability_status": "available" if available else "unavailable",
        "training_support": available,
        "inference_support": available,
        "live_candidate": available,
        "adapter_module": adapter_module,
        "adapter_version": family_adapter_version(family_id) if available else None,
    }


def _score_family(
    *,
    family_id: str,
    row: dict[str, Any],
    task_type: str,
    data_mode: str,
    row_count: int,
    feature_count: int,
    categorical_ratio: float,
    missingness: float,
    class_count: int,
    minority_fraction: float | None,
    preferred_family: str | None,
    memory_bias: dict[str, float],
    benchmark_status: str,
    explicit_biases: list[str],
) -> tuple[float, list[str], dict[str, float], str | None]:
    reasons: list[str] = []
    factor_scores: dict[str, float] = {}
    task_family = "classification" if is_classification_task(task_type) else "regression"
    preferred_family_bonus, memory_bias_scale, memory_bias_cap = _memory_route_bonus_profile(task_type=task_type)
    if row["task_family"] not in {task_family, "classification_or_regression"}:
        return -999.0, ["Task-family mismatch."], {"task_family_mismatch": -999.0}, "Task family mismatch."
    if data_mode != "time_series" and row["time_series_level"] == "lagged":
        return -250.0, ["Lagged family excluded for a static table."], {"static_table_penalty": -250.0}, (
            "Relaytic excluded this lagged family because the task contract does not prove ordered temporal structure."
        )
    if data_mode != "time_series" and row["time_series_level"] == "sequence":
        return -500.0, ["Sequence family rejected for a static table."], {"sequence_static_penalty": -500.0}, (
            "Relaytic rejected this sequence family because the task contract does not prove ordered temporal structure."
        )
    if family_id == "tabpfn_classifier" and (
        data_mode == "time_series" or row_count > 3000 or feature_count > 128 or (class_count and class_count > 10)
    ):
        return -220.0, ["TabPFN live routing deferred to a better small-data fit window."], {"tabpfn_fit_window_penalty": -220.0}, (
            "Relaytic kept TabPFN out of the live candidate set because the current task is outside the preferred small-data static classification window."
        )
    score = _factor(factor_scores, "task_base", _base_score(family_id=family_id, task_type=task_type, data_mode=data_mode))
    if row_count <= 400 and family_id in {"linear_ridge", "logistic_regression"}:
        score += _factor(factor_scores, "small_data_linear_bonus", 0.12)
        reasons.append("Small-to-medium data still justifies a strong linear baseline.")
    if task_type == "binary_classification" and data_mode != "time_series" and family_id == "logistic_regression":
        score += _factor(factor_scores, "binary_linear_baseline_bonus", 0.34)
        reasons.append("Standard binary classification keeps a calibrated linear baseline in front until stronger evidence appears.")
    if row_count >= 250 and family_id in {
        "hist_gradient_boosting_ensemble",
        "hist_gradient_boosting_classifier",
        "boosted_tree_ensemble",
        "boosted_tree_classifier",
        "xgboost_ensemble",
        "xgboost_classifier",
        "lightgbm_ensemble",
        "lightgbm_classifier",
        "catboost_ensemble",
        "catboost_classifier",
    }:
        score += _factor(factor_scores, "row_count_boosting_bonus", 0.12)
        reasons.append("Row count is large enough for a stronger boosting family to be worthwhile.")
    if row_count <= 2000 and feature_count <= 100 and family_id == "tabpfn_classifier":
        score += _factor(factor_scores, "small_data_specialist_bonus", 0.34)
        reasons.append("Problem size is compatible with a small-data specialist classifier.")
    if feature_count >= 14 and family_id in {"extra_trees_ensemble", "extra_trees_classifier"}:
        score += _factor(factor_scores, "feature_count_extra_trees_bonus", 0.10)
        reasons.append("Feature count favors a broader randomized tree ensemble.")
    if missingness >= 0.05 and family_id in {
        "hist_gradient_boosting_ensemble",
        "hist_gradient_boosting_classifier",
        "extra_trees_ensemble",
        "extra_trees_classifier",
        "catboost_ensemble",
        "catboost_classifier",
        "lightgbm_ensemble",
        "lightgbm_classifier",
    }:
        score += _factor(factor_scores, "missingness_tree_bonus", 0.08)
        reasons.append("Missingness pattern favors robust tree or boosting families.")
    if categorical_ratio >= 0.22 and family_id in {"catboost_ensemble", "catboost_classifier"}:
        score += _factor(factor_scores, "categorical_native_bonus", 0.30)
        reasons.append("Categorical ratio is high enough to prefer a categorical-aware boosting family when available.")
    elif categorical_ratio >= 0.22 and family_id in {
        "extra_trees_ensemble",
        "extra_trees_classifier",
        "hist_gradient_boosting_ensemble",
        "hist_gradient_boosting_classifier",
    }:
        score += _factor(factor_scores, "categorical_general_bonus", 0.07)
        reasons.append("Mixed feature types favor a strong non-linear family over a purely linear route.")
    if class_count >= 3 and family_id in {
        "hist_gradient_boosting_classifier",
        "extra_trees_classifier",
        "tabpfn_classifier",
        "catboost_classifier",
        "xgboost_classifier",
        "lightgbm_classifier",
    }:
        score += _factor(factor_scores, "multiclass_bonus", 0.16)
        reasons.append("Multiclass structure widens the router beyond binary-default families.")
    if (minority_fraction is not None and minority_fraction <= 0.20) or task_type in {"fraud_detection", "anomaly_detection"}:
        if family_id in {
            "boosted_tree_classifier",
            "hist_gradient_boosting_classifier",
            "catboost_classifier",
            "xgboost_classifier",
            "lightgbm_classifier",
            "lagged_tree_classifier",
        }:
            score += _factor(factor_scores, "rare_event_bonus", 0.13)
            reasons.append("Rare-event posture favors stronger non-linear probability-ranking families.")
        if family_id == "logistic_regression":
            score += _factor(factor_scores, "rare_event_linear_penalty", -0.05)
    if data_mode == "time_series":
        if family_id in {"lagged_linear", "lagged_logistic_regression"}:
            score += _factor(factor_scores, "temporal_lagged_baseline_bonus", 0.16)
            reasons.append("Time-aware routing keeps a lagged baseline near the front of the ladder.")
        if is_classification_task(task_type) and family_id == "lagged_logistic_regression":
            score += _factor(factor_scores, "temporal_calibrated_classifier_bonus", 0.18)
            reasons.append("Temporal classification keeps a calibrated lagged logistic route ahead of heavier candidates until stronger evidence arrives.")
        if family_id in {"lagged_tree_ensemble", "lagged_tree_classifier"}:
            score += _factor(factor_scores, "temporal_lagged_tree_bonus", 0.14)
            reasons.append("Timestamped data supports lagged non-linear routes before sequence promotion.")
        if row["time_series_level"] == "static":
            score += _factor(factor_scores, "temporal_static_baseline_penalty", -0.04)
    if preferred_family and family_id == preferred_family:
        score += _factor(factor_scores, "preferred_family_bonus", preferred_family_bonus)
        reasons.append("Workspace analog evidence strongly preferred this family for the current run shape.")
    memory_bonus = float(memory_bias.get(family_id, 0.0) or 0.0)
    if abs(memory_bonus) > 1e-12:
        bounded = max(-memory_bias_cap, min(memory_bias_cap, memory_bonus * memory_bias_scale))
        score += _factor(factor_scores, "workspace_analog_bias", bounded)
        reasons.append("Workspace analog evidence shifted this family's priority.")
    explicit_bonus = _explicit_bias_bonus(family_id=family_id, explicit_biases=explicit_biases)
    if explicit_bonus:
        score += _factor(factor_scores, "explicit_bias_bonus", explicit_bonus)
        reasons.append("Operator or domain priors explicitly favored this family.")
    if benchmark_status == "below_reference" and family_id in {"hist_gradient_boosting_classifier", "hist_gradient_boosting_ensemble", "extra_trees_classifier", "extra_trees_ensemble"}:
        score += _factor(factor_scores, "benchmark_pressure_bonus", 0.05)
    if not reasons:
        reasons.append("Router score came mostly from the default family prior and current task structure.")
    return score, reasons, factor_scores, None


def _base_score(*, family_id: str, task_type: str, data_mode: str) -> float:
    task_family = "classification" if is_classification_task(task_type) else "regression"
    if task_family == "classification":
        base = {
            "logistic_regression": 0.38,
            "lagged_logistic_regression": 0.42,
            "bagged_tree_classifier": 0.48,
            "boosted_tree_classifier": 0.56,
            "hist_gradient_boosting_classifier": 0.61,
            "extra_trees_classifier": 0.58,
            "lagged_tree_classifier": 0.57,
            "catboost_classifier": 0.63,
            "xgboost_classifier": 0.60,
            "lightgbm_classifier": 0.60,
            "tabpfn_classifier": 0.62,
            "sequence_lstm_candidate": 0.45,
            "temporal_transformer_candidate": 0.47,
        }
    else:
        base = {
            "linear_ridge": 0.38,
            "lagged_linear": 0.44,
            "bagged_tree_ensemble": 0.50,
            "boosted_tree_ensemble": 0.57,
            "hist_gradient_boosting_ensemble": 0.60,
            "extra_trees_ensemble": 0.58,
            "lagged_tree_ensemble": 0.56,
            "catboost_ensemble": 0.62,
            "xgboost_ensemble": 0.60,
            "lightgbm_ensemble": 0.60,
            "sequence_lstm_candidate": 0.45,
            "temporal_transformer_candidate": 0.47,
        }
    score = base.get(family_id, 0.0)
    if data_mode == "time_series" and family_id in {"sequence_lstm_candidate", "temporal_transformer_candidate"}:
        score += 0.05
    return score


def _memory_route_bonus_profile(*, task_type: str) -> tuple[float, float, float]:
    if task_type == "multiclass_classification":
        return 0.08, 0.08, 0.10
    if task_type in {"binary_classification", "fraud_detection", "anomaly_detection"}:
        return 0.26, 0.40, 0.30
    return 0.12, 0.16, 0.16


def _explicit_bias_bonus(*, family_id: str, explicit_biases: list[str]) -> float:
    normalized_biases = {str(item).strip().lower().replace("-", "_") for item in explicit_biases if str(item).strip()}
    mapping = {
        "linear_ridge": {"linear_ridge", "linear"},
        "logistic_regression": {"logistic", "linear_classifier"},
        "boosted_tree_ensemble": {"boosted_tree", "tree_ensemble"},
        "boosted_tree_classifier": {"boosted_tree", "boosted_tree_classifier"},
        "bagged_tree_ensemble": {"tree_small", "tree_ensemble_candidate"},
        "bagged_tree_classifier": {"tree_small", "tree_classifier"},
        "lagged_linear": {"lagged_linear", "temporal_linear"},
        "lagged_logistic_regression": {"lagged_linear", "temporal_classifier"},
        "lagged_tree_ensemble": {"lagged_tree"},
        "lagged_tree_classifier": {"lagged_tree"},
        "hist_gradient_boosting_ensemble": {"hist_gradient_boosting"},
        "hist_gradient_boosting_classifier": {"hist_gradient_boosting_classifier"},
        "extra_trees_ensemble": {"extra_trees"},
        "extra_trees_classifier": {"extra_trees_classifier"},
        "catboost_ensemble": {"catboost", "categorical_native"},
        "catboost_classifier": {"catboost", "categorical_native"},
        "tabpfn_classifier": {"tabpfn", "small_data_specialist"},
    }
    aliases = mapping.get(family_id, set())
    return 0.10 if normalized_biases & aliases else 0.0


def _temporal_ladder(*, task_type: str, data_mode: str, sequence_shadow_ready: bool) -> list[str]:
    if data_mode != "time_series":
        return ["ordinary_tabular_baseline", "non_temporal_non_linear_route"]
    baseline = "ordinary_tabular_baseline"
    lagged = "lagged_tabular_baseline"
    stronger = "stronger_temporal_tree_or_boosting_route"
    sequence = "sequence_shadow_candidates_ready" if sequence_shadow_ready else "sequence_shadow_candidates_deferred"
    return [baseline, lagged, stronger, sequence]


def _router_summary(
    *,
    task_type: str,
    data_mode: str,
    recommended_primary_family: str | None,
    sequence_shadow_ready: bool,
    sequence_rejection_reason: str | None,
) -> str:
    if recommended_primary_family:
        primary = f"Relaytic currently recommends `{recommended_primary_family}` as the lead family for this run."
    else:
        primary = "Relaytic could not produce a live architecture candidate order."
    if data_mode == "time_series":
        if sequence_shadow_ready:
            return primary + " The task is time-aware, so the router kept the lagged baseline ladder live and marked sequence families as shadow-ready rather than live by default."
        return primary + " The task is time-aware, but Relaytic kept sequence families out of the live ladder and stayed with tabular or lagged candidates first."
    if sequence_rejection_reason:
        return primary + " " + sequence_rejection_reason
    return primary


def _ablation_summary(
    *,
    data_mode: str,
    recommended_primary_family: str | None,
    sequence_shadow_ready: bool,
) -> str:
    if data_mode == "time_series":
        if sequence_shadow_ready:
            return (
                "Relaytic kept the ordinary baseline, lagged baseline, and stronger temporal non-linear families live, "
                "while leaving sequence-native candidates in shadow-ready posture."
            )
        return (
            "Relaytic kept the temporal ladder focused on ordinary and lagged tabular routes because sequence promotion is not yet justified."
        )
    return (
        f"Relaytic widened the static-table family set beyond the old tree defaults and currently leans toward `{recommended_primary_family or 'no live family'}`."
    )


def _build_categorical_strategy_report(
    *,
    generated_at: str,
    task_type: str,
    categorical_columns: list[str],
    categorical_ratio: float,
    candidate_order: list[str],
    registry_rows: list[dict[str, Any]],
    class_count: int,
) -> dict[str, Any]:
    relevant_catboost_family = "catboost_classifier" if is_classification_task(task_type) else "catboost_ensemble"
    relevant_hist_family = "hist_gradient_boosting_classifier" if is_classification_task(task_type) else "hist_gradient_boosting_ensemble"
    relevant_extra_family = "extra_trees_classifier" if is_classification_task(task_type) else "extra_trees_ensemble"
    available_families = {str(row.get("family_id")) for row in registry_rows if row.get("availability_status") == "available"}
    if categorical_ratio >= 0.22 and relevant_catboost_family in available_families:
        selected_strategy = "categorical_native_preferred"
        summary = "Relaytic prefers a categorical-native family because the dataset is materially mixed-type and the adapter is available."
    elif categorical_columns:
        selected_strategy = "encoded_numeric_fallback"
        summary = "Relaytic detected categorical structure but is falling back to generic non-linear families because no categorical-native live family is available."
    else:
        selected_strategy = "numeric_or_low_categorical"
        summary = "Relaytic sees a mostly numeric table, so it stays with the general tabular family ladder."
    return {
        "schema_version": CATEGORICAL_STRATEGY_REPORT_SCHEMA_VERSION,
        "generated_at": generated_at,
        "status": "ok",
        "selected_strategy": selected_strategy,
        "categorical_column_count": len(categorical_columns),
        "categorical_ratio": round(categorical_ratio, 4),
        "categorical_native_family": relevant_catboost_family if relevant_catboost_family in available_families else None,
        "general_fallback_families": [
            family
            for family in [relevant_hist_family, relevant_extra_family]
            if family in candidate_order or family in available_families
        ],
        "multiclass_context": bool(class_count >= 3),
        "summary": summary,
    }


def _build_family_probe_policy(
    *,
    generated_at: str,
    candidate_order: list[str],
    task_type: str,
    categorical_strategy: str,
    registry_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    tier_one = [str(item) for item in candidate_order[:4] if str(item).strip()]
    tier_two = [str(item) for item in candidate_order[4:7] if str(item).strip()]
    deterministic_floor = [
        row["family_id"]
        for row in registry_rows
        if row.get("family_role") == "deterministic_builtin" and row.get("training_support")
    ]
    return {
        "schema_version": FAMILY_PROBE_POLICY_SCHEMA_VERSION,
        "generated_at": generated_at,
        "status": "ok" if candidate_order else "partial",
        "task_type": task_type,
        "categorical_strategy": categorical_strategy,
        "tier_one_families": tier_one,
        "tier_two_families": tier_two,
        "deterministic_floor_families": deterministic_floor[:6],
        "searchable_probe_families": [
            family
            for family in candidate_order
            if family in SEARCHABLE_FAMILY_STACK
        ][:6],
        "summary": (
            f"Relaytic will probe `{len(tier_one)}` tier-one family/families first and keep `{len(deterministic_floor[:6])}` deterministic floor family/families available for fallback."
        ),
    }


def _build_family_specialization_report(
    *,
    generated_at: str,
    task_type: str,
    row_count: int,
    feature_count: int,
    categorical_ratio: float,
    class_count: int,
    minority_fraction: float | None,
    candidate_order: list[str],
) -> dict[str, Any]:
    categorical_priority_families = [
        family
        for family in candidate_order
        if family in {"catboost_classifier", "catboost_ensemble"}
    ][:2] if categorical_ratio >= 0.22 else []
    small_data_specialist_families = [
        family
        for family in candidate_order
        if family == "tabpfn_classifier"
    ][:1] if is_classification_task(task_type) and row_count <= 3000 and feature_count <= 128 else []
    rare_event_policy_active = bool(
        (minority_fraction is not None and minority_fraction <= 0.20)
        or task_type in {"fraud_detection", "anomaly_detection"}
    )
    return {
        "schema_version": FAMILY_SPECIALIZATION_REPORT_SCHEMA_VERSION,
        "generated_at": generated_at,
        "status": "ok",
        "multiclass_widening_active": bool(is_classification_task(task_type) and class_count >= 3),
        "rare_event_policy_active": rare_event_policy_active,
        "categorical_priority_families": categorical_priority_families,
        "small_data_specialist_families": small_data_specialist_families,
        "eligible_family_count": len(candidate_order),
        "summary": (
            f"Relaytic specialization flags: multiclass widening={is_classification_task(task_type) and class_count >= 3}, "
            f"rare-event policy={rare_event_policy_active}, categorical-priority={bool(categorical_priority_families)}, "
            f"small-data specialist={bool(small_data_specialist_families)}."
        ),
    }


def _family_readiness_reason(*, row: dict[str, Any]) -> str:
    family_id = str(row.get("family_id", "")).strip()
    availability_status = str(row.get("availability_status", "")).strip()
    if family_id in {"sequence_lstm_candidate", "temporal_transformer_candidate"}:
        if availability_status == "shadow_only":
            return "Sequence-native family is shadow-ready but intentionally excluded from the live router."
        return "Sequence-native family is not ready for live routing on this task."
    if row.get("family_role") == "optional_adapter":
        module_name = _clean_text(row.get("adapter_module")) or "unknown_adapter"
        if availability_status == "available":
            version = _clean_text(row.get("adapter_version"))
            return f"Optional adapter `{module_name}` is available{f' at version `{version}`' if version else ''}."
        return f"Optional adapter `{module_name}` is unavailable on this machine, so Relaytic will fall back cleanly."
    return "Deterministic local family is available without an external adapter."


def _family_probe_tier(*, family_id: str, tier_one: list[str], tier_two: list[str]) -> str:
    if family_id in tier_one:
        return "tier_one"
    if family_id in tier_two:
        return "tier_two"
    return "excluded"


def _mean_missingness(dataset_profile: dict[str, Any]) -> float:
    values = [
        _optional_float(value)
        for value in dict(dataset_profile.get("missing_fraction_by_column", {})).values()
    ]
    clean = [float(value) for value in values if value is not None]
    if not clean:
        return 0.0
    return sum(clean) / max(len(clean), 1)


def _bundle_item(bundle: dict[str, Any], key: str) -> dict[str, Any]:
    payload = bundle.get(key)
    return dict(payload) if isinstance(payload, dict) else {}


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item).strip() for item in value if str(item).strip()]


def _clean_text(value: Any) -> str | None:
    text = str(value or "").strip()
    return text or None


def _optional_float(value: Any) -> float | None:
    try:
        if value is None:
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def _factor(store: dict[str, float], key: str, value: float) -> float:
    store[key] = round(float(value), 6)
    return float(value)


def _candidate_tiebreak(family_id: str) -> int:
    order = {
        "linear_ridge": 0,
        "logistic_regression": 0,
        "lagged_linear": 1,
        "lagged_logistic_regression": 1,
        "hist_gradient_boosting_ensemble": 2,
        "hist_gradient_boosting_classifier": 2,
        "extra_trees_ensemble": 3,
        "extra_trees_classifier": 3,
        "bagged_tree_ensemble": 4,
        "bagged_tree_classifier": 4,
        "boosted_tree_ensemble": 5,
        "boosted_tree_classifier": 5,
        "lagged_tree_ensemble": 6,
        "lagged_tree_classifier": 6,
        "catboost_ensemble": 7,
        "catboost_classifier": 7,
        "xgboost_ensemble": 8,
        "xgboost_classifier": 8,
        "lightgbm_ensemble": 9,
        "lightgbm_classifier": 9,
        "tabpfn_classifier": 10,
    }
    return order.get(family_id, 50)
