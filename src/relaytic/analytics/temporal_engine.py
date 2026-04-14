"""Temporal engine artifacts for time-aware benchmarking and model posture."""

from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from relaytic.core.json_utils import write_json
from relaytic.ingestion import load_tabular_data


TEMPORAL_STRUCTURE_REPORT_SCHEMA_VERSION = "relaytic.temporal_structure_report.v1"
TEMPORAL_FEATURE_LADDER_SCHEMA_VERSION = "relaytic.temporal_feature_ladder.v1"
ROLLING_CV_PLAN_SCHEMA_VERSION = "relaytic.rolling_cv_plan.v1"
TEMPORAL_SPLIT_GUARD_REPORT_SCHEMA_VERSION = "relaytic.temporal_split_guard_report.v1"
SEQUENCE_SHADOW_SCORECARD_SCHEMA_VERSION = "relaytic.sequence_shadow_scorecard.v1"
TEMPORAL_BASELINE_LADDER_SCHEMA_VERSION = "relaytic.temporal_baseline_ladder.v1"
TEMPORAL_METRIC_CONTRACT_SCHEMA_VERSION = "relaytic.temporal_metric_contract.v1"


TEMPORAL_ENGINE_FILENAMES = {
    "temporal_structure_report": "temporal_structure_report.json",
    "temporal_feature_ladder": "temporal_feature_ladder.json",
    "rolling_cv_plan": "rolling_cv_plan.json",
    "temporal_split_guard_report": "temporal_split_guard_report.json",
    "sequence_shadow_scorecard": "sequence_shadow_scorecard.json",
    "temporal_baseline_ladder": "temporal_baseline_ladder.json",
    "temporal_metric_contract": "temporal_metric_contract.json",
}


def sync_temporal_engine_artifacts(
    run_dir: str | Path,
    *,
    data_path: str | Path | None = None,
    investigation_bundle: dict[str, Any] | None = None,
    planning_bundle: dict[str, Any] | None = None,
    benchmark_bundle: dict[str, Any] | None = None,
    architecture_bundle: dict[str, Any] | None = None,
    task_contract_bundle: dict[str, Any] | None = None,
) -> dict[str, Path]:
    artifacts = build_temporal_engine_artifacts(
        data_path=data_path,
        investigation_bundle=investigation_bundle,
        planning_bundle=planning_bundle,
        benchmark_bundle=benchmark_bundle,
        architecture_bundle=architecture_bundle,
        task_contract_bundle=task_contract_bundle,
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
        for key, filename in TEMPORAL_ENGINE_FILENAMES.items()
    }


def read_temporal_engine_artifacts(run_dir: str | Path) -> dict[str, Any]:
    root = Path(run_dir)
    payload: dict[str, Any] = {}
    for key, filename in TEMPORAL_ENGINE_FILENAMES.items():
        path = root / filename
        if not path.exists():
            continue
        payload[key] = json.loads(path.read_text(encoding="utf-8"))
    return payload


def build_temporal_engine_artifacts(
    *,
    data_path: str | Path | None = None,
    investigation_bundle: dict[str, Any] | None = None,
    planning_bundle: dict[str, Any] | None = None,
    benchmark_bundle: dict[str, Any] | None = None,
    architecture_bundle: dict[str, Any] | None = None,
    task_contract_bundle: dict[str, Any] | None = None,
) -> dict[str, dict[str, Any]]:
    generated_at = _utc_now()
    dataset_profile = _bundle_item(investigation_bundle or {}, "dataset_profile")
    plan = _bundle_item(planning_bundle or {}, "plan")
    execution_summary = dict(plan.get("execution_summary") or {})
    builder_handoff = dict(plan.get("builder_handoff") or {})
    task_profile_contract = _bundle_item(task_contract_bundle or {}, "task_profile_contract")
    metric_contract = _bundle_item(task_contract_bundle or {}, "metric_contract")
    split_diagnostics_report = _bundle_item(task_contract_bundle or {}, "split_diagnostics_report")
    temporal_fold_health = _bundle_item(task_contract_bundle or {}, "temporal_fold_health")
    metric_materialization_audit = _bundle_item(task_contract_bundle or {}, "metric_materialization_audit")
    benchmark_truth_precheck = _bundle_item(task_contract_bundle or {}, "benchmark_truth_precheck")
    optimization_objective_contract = _bundle_item(task_contract_bundle or {}, "optimization_objective_contract")
    architecture_router_report = _bundle_item(architecture_bundle or {}, "architecture_router_report")
    architecture_ablation_report = _bundle_item(architecture_bundle or {}, "architecture_ablation_report")
    reference_approach_matrix = _bundle_item(benchmark_bundle or {}, "reference_approach_matrix")
    benchmark_ablation_matrix = _bundle_item(benchmark_bundle or {}, "benchmark_ablation_matrix")
    shadow_trial_scorecard = _bundle_item(benchmark_bundle or {}, "shadow_trial_scorecard")

    data_mode = (
        _clean_text(task_profile_contract.get("data_mode"))
        or _clean_text(plan.get("data_mode"))
        or _clean_text(dataset_profile.get("data_mode"))
        or "steady_state"
    )
    timestamp_column = (
        _clean_text(task_profile_contract.get("timestamp_column"))
        or _clean_text(plan.get("timestamp_column"))
        or _clean_text(dataset_profile.get("timestamp_column"))
    )
    target_column = _clean_text(task_profile_contract.get("target_column")) or _clean_text(plan.get("target_column"))
    task_type = _clean_text(task_profile_contract.get("task_type")) or _clean_text(plan.get("task_type"))
    lag_horizon = _optional_int(builder_handoff.get("lag_horizon_samples"))
    if lag_horizon is None:
        lag_horizon = _optional_int(execution_summary.get("lag_horizon_samples"))

    frame: pd.DataFrame | None = None
    parsed_timestamp: pd.Series | None = None
    data_load_error: str | None = None
    resolved_data_path = str(data_path) if data_path else None
    if resolved_data_path and Path(resolved_data_path).exists():
        try:
            frame = load_tabular_data(resolved_data_path).frame.copy()
            if timestamp_column and timestamp_column in frame.columns:
                parsed_timestamp = pd.to_datetime(frame[timestamp_column], errors="coerce")
        except Exception as exc:  # pragma: no cover - defensive runtime protection
            data_load_error = str(exc)

    temporal_structure_report = _build_temporal_structure_report(
        generated_at=generated_at,
        data_mode=data_mode,
        timestamp_column=timestamp_column,
        frame=frame,
        parsed_timestamp=parsed_timestamp,
        data_load_error=data_load_error,
    )
    temporal_feature_ladder = _build_temporal_feature_ladder(
        generated_at=generated_at,
        data_mode=data_mode,
        lag_horizon=lag_horizon,
        feature_columns=[str(item) for item in plan.get("feature_columns", []) if str(item).strip()],
        structure_report=temporal_structure_report,
    )
    rolling_cv_plan = _build_rolling_cv_plan(
        generated_at=generated_at,
        data_mode=data_mode,
        row_count=_optional_int(task_profile_contract.get("row_count")) or (len(frame) if frame is not None else 0),
        lag_horizon=lag_horizon,
        task_type=task_type,
        split_diagnostics_report=split_diagnostics_report,
    )
    temporal_split_guard_report = _build_temporal_split_guard_report(
        generated_at=generated_at,
        data_mode=data_mode,
        split_diagnostics_report=split_diagnostics_report,
        temporal_fold_health=temporal_fold_health,
        benchmark_truth_precheck=benchmark_truth_precheck,
    )
    temporal_baseline_ladder = _build_temporal_baseline_ladder(
        generated_at=generated_at,
        data_mode=data_mode,
        reference_approach_matrix=reference_approach_matrix,
        benchmark_ablation_matrix=benchmark_ablation_matrix,
    )
    sequence_shadow_scorecard = _build_sequence_shadow_scorecard(
        generated_at=generated_at,
        data_mode=data_mode,
        architecture_router_report=architecture_router_report,
        architecture_ablation_report=architecture_ablation_report,
        temporal_baseline_ladder=temporal_baseline_ladder,
        shadow_trial_scorecard=shadow_trial_scorecard,
    )
    temporal_metric_contract = _build_temporal_metric_contract(
        generated_at=generated_at,
        data_mode=data_mode,
        metric_contract=metric_contract,
        optimization_objective_contract=optimization_objective_contract,
        metric_materialization_audit=metric_materialization_audit,
        reference_approach_matrix=reference_approach_matrix,
        temporal_baseline_ladder=temporal_baseline_ladder,
    )

    if target_column and frame is not None and target_column in frame.columns and data_mode == "time_series":
        temporal_structure_report["target_column"] = target_column
        temporal_feature_ladder["target_column"] = target_column

    return {
        "temporal_structure_report": temporal_structure_report,
        "temporal_feature_ladder": temporal_feature_ladder,
        "rolling_cv_plan": rolling_cv_plan,
        "temporal_split_guard_report": temporal_split_guard_report,
        "sequence_shadow_scorecard": sequence_shadow_scorecard,
        "temporal_baseline_ladder": temporal_baseline_ladder,
        "temporal_metric_contract": temporal_metric_contract,
    }


def _build_temporal_structure_report(
    *,
    generated_at: str,
    data_mode: str,
    timestamp_column: str | None,
    frame: pd.DataFrame | None,
    parsed_timestamp: pd.Series | None,
    data_load_error: str | None,
) -> dict[str, Any]:
    if str(data_mode).strip().lower() != "time_series":
        return _not_applicable_artifact(
            schema_version=TEMPORAL_STRUCTURE_REPORT_SCHEMA_VERSION,
            generated_at=generated_at,
            summary="Temporal structure checks are not applicable for a steady-state table.",
        )
    if frame is None or parsed_timestamp is None:
        return {
            "schema_version": TEMPORAL_STRUCTURE_REPORT_SCHEMA_VERSION,
            "generated_at": generated_at,
            "status": "partial",
            "timestamp_column": timestamp_column,
            "ordered_temporal_structure": False,
            "incidental_timestamp": True,
            "reason_codes": ["data_load_failed"] if data_load_error else ["timestamp_not_materialized"],
            "summary": (
                f"Relaytic could not fully audit temporal structure: {data_load_error}."
                if data_load_error
                else "Relaytic could not audit temporal structure because the timestamp column was not materialized."
            ),
        }
    usable_fraction = float(parsed_timestamp.notna().mean()) if len(parsed_timestamp) else 0.0
    diffs = parsed_timestamp.dropna().diff().dt.total_seconds().dropna()
    if diffs.empty:
        monotonic_fraction = 0.0
        duplicate_fraction = 0.0
        median_cadence_seconds = None
        regular_cadence = False
    else:
        monotonic_fraction = float((diffs > 0).mean())
        duplicate_fraction = float((diffs == 0).mean())
        positive_diffs = diffs[diffs > 0]
        median_cadence_seconds = float(positive_diffs.median()) if not positive_diffs.empty else None
        if median_cadence_seconds and median_cadence_seconds > 0:
            cadence_deviation = (positive_diffs - median_cadence_seconds).abs() / median_cadence_seconds
            regular_cadence = bool(float((cadence_deviation <= 0.15).mean()) >= 0.75)
        else:
            regular_cadence = False
    ordered_temporal_structure = bool(
        usable_fraction >= 0.80
        and monotonic_fraction >= 0.75
        and duplicate_fraction <= 0.10
    )
    reason_codes: list[str] = []
    if usable_fraction < 0.80:
        reason_codes.append("timestamp_parse_rate_low")
    if monotonic_fraction < 0.75:
        reason_codes.append("timestamp_order_incoherent")
    if duplicate_fraction > 0.10:
        reason_codes.append("timestamp_duplicates_high")
    if not regular_cadence:
        reason_codes.append("cadence_irregular")
    summary = (
        "Relaytic confirmed ordered temporal structure with a mostly regular cadence."
        if ordered_temporal_structure
        else "Relaytic found a timestamp column, but the temporal structure is still too weak or irregular for strong time-aware claims."
    )
    return {
        "schema_version": TEMPORAL_STRUCTURE_REPORT_SCHEMA_VERSION,
        "generated_at": generated_at,
        "status": "ok" if ordered_temporal_structure else "partial",
        "timestamp_column": timestamp_column,
        "row_count": int(len(frame)),
        "usable_timestamp_fraction": round(usable_fraction, 4),
        "monotonic_fraction": round(monotonic_fraction, 4),
        "duplicate_fraction": round(duplicate_fraction, 4),
        "median_cadence_seconds": median_cadence_seconds,
        "regular_cadence": regular_cadence,
        "ordered_temporal_structure": ordered_temporal_structure,
        "incidental_timestamp": not ordered_temporal_structure,
        "reason_codes": reason_codes,
        "summary": summary,
    }


def _build_temporal_feature_ladder(
    *,
    generated_at: str,
    data_mode: str,
    lag_horizon: int | None,
    feature_columns: list[str],
    structure_report: dict[str, Any],
) -> dict[str, Any]:
    if str(data_mode).strip().lower() != "time_series":
        return _not_applicable_artifact(
            schema_version=TEMPORAL_FEATURE_LADDER_SCHEMA_VERSION,
            generated_at=generated_at,
            summary="Temporal feature ladders are not applicable for a steady-state table.",
        )
    resolved_horizon = max(1, int(lag_horizon or 3))
    rolling_window = max(2, min(resolved_horizon + 1, 4))
    materialized = [
        "current_value",
        "lag_windows",
        "delta_features",
        f"rolling_mean_{rolling_window}",
        f"rolling_std_{rolling_window}",
        f"rolling_min_{rolling_window}",
        f"rolling_max_{rolling_window}",
    ]
    if resolved_horizon > 1:
        materialized.append(f"seasonal_delta_{resolved_horizon}")
    planned_only = []
    if bool(structure_report.get("ordered_temporal_structure")):
        planned_only.append("calendar_cycle_features")
    return {
        "schema_version": TEMPORAL_FEATURE_LADDER_SCHEMA_VERSION,
        "generated_at": generated_at,
        "status": "ok",
        "lag_horizon_samples": resolved_horizon,
        "rolling_window_samples": rolling_window,
        "base_feature_count": int(len(feature_columns)),
        "materialized_feature_families": materialized,
        "planned_but_not_materialized": planned_only,
        "seasonality_style_enabled": resolved_horizon > 1,
        "calendar_cycle_ready": bool(structure_report.get("ordered_temporal_structure")),
        "summary": (
            f"Relaytic expanded the temporal ladder with lag, delta, rolling, and seasonality-style features at horizon `{resolved_horizon}`."
        ),
    }


def _build_rolling_cv_plan(
    *,
    generated_at: str,
    data_mode: str,
    row_count: int,
    lag_horizon: int | None,
    task_type: str | None,
    split_diagnostics_report: dict[str, Any],
) -> dict[str, Any]:
    if str(data_mode).strip().lower() != "time_series":
        return _not_applicable_artifact(
            schema_version=ROLLING_CV_PLAN_SCHEMA_VERSION,
            generated_at=generated_at,
            summary="Rolling cross-validation plans are not applicable for a steady-state table.",
        )
    holdout_test_size = _optional_int(split_diagnostics_report.get("test_size")) or max(2, int(round(row_count * 0.15)))
    validation_size = _optional_int(split_diagnostics_report.get("validation_size")) or max(2, int(round(row_count * 0.15)))
    recommended_windows = max(2, min(4, int(row_count / max(validation_size, 1))))
    step_size = max(1, validation_size)
    train_window_size = max(6, row_count - holdout_test_size - validation_size)
    return {
        "schema_version": ROLLING_CV_PLAN_SCHEMA_VERSION,
        "generated_at": generated_at,
        "status": "ok",
        "task_type": task_type,
        "current_split_strategy": _clean_text(split_diagnostics_report.get("split_strategy")) or "blocked_time_order_70_15_15",
        "recommended_strategy": "rolling_origin_backtest_plus_holdout",
        "lag_horizon_samples": int(lag_horizon or 0),
        "rolling_window_count": int(recommended_windows),
        "train_window_size": int(train_window_size),
        "validation_window_size": int(validation_size),
        "holdout_test_size": int(holdout_test_size),
        "step_size": int(step_size),
        "summary": "Relaytic recommends rolling-origin backtests plus a final holdout for honest temporal comparisons.",
    }


def _build_temporal_split_guard_report(
    *,
    generated_at: str,
    data_mode: str,
    split_diagnostics_report: dict[str, Any],
    temporal_fold_health: dict[str, Any],
    benchmark_truth_precheck: dict[str, Any],
) -> dict[str, Any]:
    if str(data_mode).strip().lower() != "time_series":
        return _not_applicable_artifact(
            schema_version=TEMPORAL_SPLIT_GUARD_REPORT_SCHEMA_VERSION,
            generated_at=generated_at,
            summary="Temporal split guards are not applicable for a steady-state table.",
        )
    status = _clean_text(temporal_fold_health.get("status")) or _clean_text(split_diagnostics_report.get("status")) or "partial"
    safe_to_rank = bool(benchmark_truth_precheck.get("safe_to_rank"))
    if status == "not_applicable":
        guard_state = "not_applicable"
    else:
        guard_state = "safe" if safe_to_rank and status == "ok" else "blocked"
    reason_codes = [
        str(item)
        for item in (
            temporal_fold_health.get("reason_codes")
            if isinstance(temporal_fold_health.get("reason_codes"), list)
            else split_diagnostics_report.get("reason_codes", [])
        )
        if str(item).strip()
    ]
    return {
        "schema_version": TEMPORAL_SPLIT_GUARD_REPORT_SCHEMA_VERSION,
        "generated_at": generated_at,
        "status": status,
        "guard_state": guard_state,
        "split_strategy": _clean_text(split_diagnostics_report.get("split_strategy")),
        "validation_positive_count": split_diagnostics_report.get("validation_positive_count"),
        "test_positive_count": split_diagnostics_report.get("test_positive_count"),
        "safe_for_benchmarking": safe_to_rank,
        "reason_codes": reason_codes,
        "summary": (
            "Relaytic confirmed that temporal validation and test folds preserve event truth."
            if guard_state == "safe"
            else _clean_text(temporal_fold_health.get("summary"))
            or _clean_text(split_diagnostics_report.get("summary"))
            or "Relaytic blocked temporal benchmarking because future-fold event integrity is not safe."
        ),
    }


def _build_temporal_baseline_ladder(
    *,
    generated_at: str,
    data_mode: str,
    reference_approach_matrix: dict[str, Any],
    benchmark_ablation_matrix: dict[str, Any],
) -> dict[str, Any]:
    if str(data_mode).strip().lower() != "time_series":
        return _not_applicable_artifact(
            schema_version=TEMPORAL_BASELINE_LADDER_SCHEMA_VERSION,
            generated_at=generated_at,
            summary="Temporal baseline ladders are not applicable for a steady-state table.",
        )
    comparison_metric = _clean_text(reference_approach_matrix.get("comparison_metric"))
    metric_direction = _clean_text(reference_approach_matrix.get("metric_direction")) or _metric_direction(comparison_metric)
    relaytic_reference = dict(reference_approach_matrix.get("relaytic_reference", {}))
    ordinary = _find_ablation_row(benchmark_ablation_matrix, role="baseline_reference")
    lagged = _find_ablation_row(benchmark_ablation_matrix, role="lagged_reference")
    selected = _find_ablation_row(benchmark_ablation_matrix, role="selected_route")
    ordinary_metric = _optional_float(dict(ordinary).get("test_metric"))
    lagged_metric = _optional_float(dict(lagged).get("test_metric"))
    selected_metric = _optional_float(dict(selected).get("test_metric"))
    if selected_metric is None:
        selected_metric = _metric_value(dict(relaytic_reference.get("test_metric", {})), comparison_metric)
    lagged_beats_ordinary = _wins(candidate=lagged_metric, incumbent=ordinary_metric, metric_direction=metric_direction)
    return {
        "schema_version": TEMPORAL_BASELINE_LADDER_SCHEMA_VERSION,
        "generated_at": generated_at,
        "status": "ok" if comparison_metric else "partial",
        "comparison_metric": comparison_metric,
        "metric_direction": metric_direction,
        "ordinary_baseline_family": _clean_text(dict(ordinary).get("model_family")),
        "ordinary_baseline_metric": ordinary_metric,
        "lagged_baseline_family": _clean_text(dict(lagged).get("model_family")),
        "lagged_baseline_metric": lagged_metric,
        "selected_route_family": _clean_text(dict(selected).get("model_family")) or _clean_text(relaytic_reference.get("model_family")),
        "selected_route_metric": selected_metric,
        "lagged_beats_ordinary": lagged_beats_ordinary,
        "summary": (
            "Relaytic confirmed that the stronger lagged baseline beats the ordinary non-temporal baseline."
            if lagged_beats_ordinary is True
            else "Relaytic recorded temporal baseline posture for this run."
        ),
    }


def _build_sequence_shadow_scorecard(
    *,
    generated_at: str,
    data_mode: str,
    architecture_router_report: dict[str, Any],
    architecture_ablation_report: dict[str, Any],
    temporal_baseline_ladder: dict[str, Any],
    shadow_trial_scorecard: dict[str, Any],
) -> dict[str, Any]:
    if str(data_mode).strip().lower() != "time_series":
        return _not_applicable_artifact(
            schema_version=SEQUENCE_SHADOW_SCORECARD_SCHEMA_VERSION,
            generated_at=generated_at,
            summary="Sequence shadow scoring is not applicable for a steady-state table.",
        )
    baseline_family = _clean_text(temporal_baseline_ladder.get("lagged_baseline_family"))
    baseline_metric = _optional_float(temporal_baseline_ladder.get("lagged_baseline_metric"))
    metric_direction = _clean_text(temporal_baseline_ladder.get("metric_direction")) or "lower_is_better"
    imported_rows = {
        _clean_text(item.get("family_id")): dict(item)
        for item in shadow_trial_scorecard.get("rows", [])
        if isinstance(item, dict) and _clean_text(item.get("family_id"))
    }
    candidates = [
        str(item)
        for item in architecture_ablation_report.get("shadow_sequence_candidates", [])
        if str(item).strip()
    ] or ["sequence_lstm_candidate", "temporal_transformer_candidate"]
    rows: list[dict[str, Any]] = []
    for family_id in candidates:
        imported = imported_rows.get(family_id, {})
        candidate_metric = _optional_float(imported.get("test_metric"))
        if candidate_metric is None:
            candidate_metric = _optional_float(imported.get("validation_metric"))
        if candidate_metric is not None and baseline_metric is not None:
            comparison_outcome = "beats_lagged_baseline" if _wins(candidate=candidate_metric, incumbent=baseline_metric, metric_direction=metric_direction) else "loses_to_lagged_baseline"
        else:
            comparison_outcome = "baseline_unbeaten"
        rows.append(
            {
                "family_id": family_id,
                "shadow_mode": _clean_text(imported.get("shadow_mode")) or "baseline_gate_shadow_only",
                "baseline_family": baseline_family,
                "baseline_metric": baseline_metric,
                "candidate_metric": candidate_metric,
                "comparison_outcome": comparison_outcome,
                "promotion_state": _clean_text(imported.get("promotion_state")) or "shadow_only",
                "sequence_live_allowed": bool(architecture_router_report.get("sequence_live_allowed")),
                "sequence_shadow_ready": bool(architecture_router_report.get("sequence_shadow_ready")),
                "reason_codes": list(imported.get("reason_codes", [])) + ["lagged_baseline_required", "sequence_live_not_allowed"],
            }
        )
    return {
        "schema_version": SEQUENCE_SHADOW_SCORECARD_SCHEMA_VERSION,
        "generated_at": generated_at,
        "status": "ok" if rows else "partial",
        "baseline_family": baseline_family,
        "baseline_metric": baseline_metric,
        "rows": rows,
        "summary": (
            "Relaytic kept sequence-native candidates in shadow-only posture until they beat the stronger lagged baseline."
        ),
    }


def _build_temporal_metric_contract(
    *,
    generated_at: str,
    data_mode: str,
    metric_contract: dict[str, Any],
    optimization_objective_contract: dict[str, Any],
    metric_materialization_audit: dict[str, Any],
    reference_approach_matrix: dict[str, Any],
    temporal_baseline_ladder: dict[str, Any],
) -> dict[str, Any]:
    if str(data_mode).strip().lower() != "time_series":
        return _not_applicable_artifact(
            schema_version=TEMPORAL_METRIC_CONTRACT_SCHEMA_VERSION,
            generated_at=generated_at,
            summary="Temporal metric contracts are not applicable for a steady-state table.",
        )
    comparison_metric = (
        _clean_text(optimization_objective_contract.get("benchmark_comparison_metric"))
        or _clean_text(metric_contract.get("benchmark_comparison_metric"))
        or _clean_text(temporal_baseline_ladder.get("comparison_metric"))
    )
    resolved_metric = _metric_alias(comparison_metric)
    relaytic_reference = dict(reference_approach_matrix.get("relaytic_reference", {}))
    benchmark_rows_materialized = bool(metric_materialization_audit.get("benchmark_metric_materialized_in_benchmark_rows"))
    execution_materialized = bool(metric_materialization_audit.get("benchmark_metric_materialized_in_execution"))
    if comparison_metric and not benchmark_rows_materialized:
        benchmark_rows_materialized = _metric_value(dict(relaytic_reference.get("test_metric", {})), comparison_metric) is not None
    return {
        "schema_version": TEMPORAL_METRIC_CONTRACT_SCHEMA_VERSION,
        "generated_at": generated_at,
        "status": "ok" if comparison_metric and benchmark_rows_materialized else "partial",
        "comparison_metric": comparison_metric,
        "resolved_metric": resolved_metric,
        "metric_direction": _clean_text(temporal_baseline_ladder.get("metric_direction")) or _metric_direction(comparison_metric),
        "comparison_metric_materialized_in_execution": execution_materialized,
        "comparison_metric_materialized_in_benchmark_rows": benchmark_rows_materialized,
        "summary": (
            f"Relaytic confirmed that temporal comparison metric `{comparison_metric}` is materially available in benchmark outputs."
            if comparison_metric and benchmark_rows_materialized
            else f"Relaytic could not confirm full temporal metric materialization for `{comparison_metric or 'unknown'}`."
        ),
    }


def _not_applicable_artifact(*, schema_version: str, generated_at: str, summary: str) -> dict[str, Any]:
    return {
        "schema_version": schema_version,
        "generated_at": generated_at,
        "status": "not_applicable",
        "summary": summary,
    }


def _find_ablation_row(benchmark_ablation_matrix: dict[str, Any], *, role: str) -> dict[str, Any]:
    for row in benchmark_ablation_matrix.get("rows", []):
        if isinstance(row, dict) and _clean_text(row.get("role")) == role:
            return row
    return {}


def _metric_value(metrics: dict[str, Any], metric_name: str | None) -> float | None:
    metric = _clean_text(metric_name)
    if not metric:
        return None
    if metric in metrics:
        return _optional_float(metrics.get(metric))
    alias = _metric_alias(metric)
    if alias != metric and alias in metrics:
        return _optional_float(metrics.get(alias))
    return None


def _metric_alias(metric_name: str | None) -> str | None:
    metric = _clean_text(metric_name)
    aliases = {
        "stability_adjusted_mae": "mae",
        "mae_per_latency": "mae",
    }
    return aliases.get(metric, metric)


def _metric_direction(metric_name: str | None) -> str:
    metric = _clean_text(metric_name) or ""
    if metric in {"mae", "rmse", "mape", "log_loss", "brier_score", "expected_calibration_error", "stability_adjusted_mae", "mae_per_latency"}:
        return "lower_is_better"
    return "higher_is_better"


def _wins(*, candidate: float | None, incumbent: float | None, metric_direction: str) -> bool | None:
    if candidate is None or incumbent is None:
        return None
    if metric_direction == "lower_is_better":
        return float(candidate) < float(incumbent)
    return float(candidate) > float(incumbent)


def _bundle_item(bundle: dict[str, Any], key: str) -> dict[str, Any]:
    value = bundle.get(key)
    return dict(value) if isinstance(value, dict) else {}


def _clean_text(value: Any) -> str | None:
    text = str(value).strip() if value is not None else ""
    return text or None


def _optional_int(value: Any) -> int | None:
    try:
        if value in {None, ""}:
            return None
        return int(value)
    except (TypeError, ValueError):
        return None


def _optional_float(value: Any) -> float | None:
    try:
        if value in {None, ""}:
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()
