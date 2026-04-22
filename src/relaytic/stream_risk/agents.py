"""Deterministic stream-risk, weak-label, and drift artifacts for Relaytic-AML."""

from __future__ import annotations

from datetime import datetime, timezone
import json
import math
from pathlib import Path
from typing import Any

import pandas as pd

from relaytic.core.json_utils import write_json
from relaytic.ingestion import load_tabular_data


STREAM_RISK_POSTURE_SCHEMA_VERSION = "relaytic.stream_risk_posture.v1"
WEAK_LABEL_POSTURE_SCHEMA_VERSION = "relaytic.weak_label_posture.v1"
DELAYED_OUTCOME_ALIGNMENT_SCHEMA_VERSION = "relaytic.delayed_outcome_alignment.v1"
DRIFT_RECALIBRATION_TRIGGER_SCHEMA_VERSION = "relaytic.drift_recalibration_trigger.v1"
ROLLING_ALERT_QUALITY_REPORT_SCHEMA_VERSION = "relaytic.rolling_alert_quality_report.v1"


STREAM_RISK_FILENAMES = {
    "stream_risk_posture": "stream_risk_posture.json",
    "weak_label_posture": "weak_label_posture.json",
    "delayed_outcome_alignment": "delayed_outcome_alignment.json",
    "drift_recalibration_trigger": "drift_recalibration_trigger.json",
    "rolling_alert_quality_report": "rolling_alert_quality_report.json",
}


def sync_stream_risk_artifacts(
    run_dir: str | Path,
    *,
    data_path: str | Path | None,
    context_bundle: dict[str, Any] | None,
    task_contract_bundle: dict[str, Any] | None,
    temporal_bundle: dict[str, Any] | None,
    operating_point_bundle: dict[str, Any] | None,
    lifecycle_bundle: dict[str, Any] | None = None,
) -> dict[str, Path]:
    """Build and write deterministic stream-risk artifacts for the current run."""
    root = Path(run_dir)
    artifacts = build_stream_risk_artifacts(
        data_path=data_path,
        context_bundle=context_bundle,
        task_contract_bundle=task_contract_bundle,
        temporal_bundle=temporal_bundle,
        operating_point_bundle=operating_point_bundle,
        lifecycle_bundle=lifecycle_bundle,
    )
    root.mkdir(parents=True, exist_ok=True)
    return {
        key: write_json(
            root / filename,
            artifacts[key],
            indent=2,
            ensure_ascii=False,
            sort_keys=True,
        )
        for key, filename in STREAM_RISK_FILENAMES.items()
    }


def read_stream_risk_artifacts(run_dir: str | Path) -> dict[str, Any]:
    """Read stream-risk artifacts if present."""
    root = Path(run_dir)
    payload: dict[str, Any] = {}
    for key, filename in STREAM_RISK_FILENAMES.items():
        path = root / filename
        if not path.exists():
            continue
        payload[key] = json.loads(path.read_text(encoding="utf-8"))
    return payload


def build_stream_risk_artifacts(
    *,
    data_path: str | Path | None,
    context_bundle: dict[str, Any] | None,
    task_contract_bundle: dict[str, Any] | None,
    temporal_bundle: dict[str, Any] | None,
    operating_point_bundle: dict[str, Any] | None,
    lifecycle_bundle: dict[str, Any] | None = None,
) -> dict[str, dict[str, Any]]:
    """Construct stream-risk artifacts from current AML, temporal, and operating-point evidence."""
    generated_at = _utc_now()
    context_bundle = context_bundle or {}
    task_contract_bundle = task_contract_bundle or {}
    temporal_bundle = temporal_bundle or {}
    operating_point_bundle = operating_point_bundle or {}
    lifecycle_bundle = lifecycle_bundle or {}

    aml_domain_contract = _bundle_item(task_contract_bundle, "aml_domain_contract")
    task_profile_contract = _bundle_item(task_contract_bundle, "task_profile_contract")
    temporal_fold_health = _bundle_item(task_contract_bundle, "temporal_fold_health")
    benchmark_truth_precheck = _bundle_item(task_contract_bundle, "benchmark_truth_precheck")
    temporal_structure_report = _bundle_item(temporal_bundle, "temporal_structure_report")
    rolling_cv_plan = _bundle_item(temporal_bundle, "rolling_cv_plan")
    operating_point_contract = _bundle_item(operating_point_bundle, "operating_point_contract")
    review_budget_optimization_report = _bundle_item(operating_point_bundle, "review_budget_optimization_report")
    champion_vs_candidate = _bundle_item(lifecycle_bundle, "champion_vs_candidate")
    recalibration_decision = _bundle_item(lifecycle_bundle, "recalibration_decision")
    retrain_decision = _bundle_item(lifecycle_bundle, "retrain_decision")
    run_brief = _bundle_item(context_bundle, "domain_brief")
    task_brief = _bundle_item(context_bundle, "task_brief")

    if not bool(aml_domain_contract.get("aml_active")):
        return _inactive_stream_risk_artifacts(
            generated_at=generated_at,
            summary="Relaytic-AML stream-risk posture is inactive because the AML domain contract is not active on this run.",
        )

    frame = _load_frame(data_path)
    target_column = _clean_text(task_profile_contract.get("target_column"))
    timestamp_column = _resolve_timestamp_column(
        frame=frame,
        preferred=_clean_text(temporal_structure_report.get("timestamp_column")) or _clean_text(task_profile_contract.get("timestamp_column")),
    )
    ordered_temporal = bool(temporal_structure_report.get("ordered_temporal_structure")) or bool(timestamp_column)
    stream_mode = "batched_temporal_monitoring" if ordered_temporal else "snapshot_only"
    benchmark_safe = bool(benchmark_truth_precheck.get("safe_to_rank", True)) and _clean_text(temporal_fold_health.get("status")) not in {"blocked", "fail"}
    review_fraction = _resolve_review_fraction(
        operating_point_contract=operating_point_contract,
        review_budget_optimization_report=review_budget_optimization_report,
    )

    corpus = " ".join(
        [
            str(aml_domain_contract.get("domain_focus", "")),
            str(aml_domain_contract.get("business_goal", "")),
            str(_bundle_item(context_bundle, "domain_brief").get("summary", "")),
            str(_bundle_item(context_bundle, "domain_brief").get("target_meaning", "")),
            str(_bundle_item(context_bundle, "task_brief").get("problem_statement", "")),
            str(_bundle_item(context_bundle, "task_brief").get("success_criteria", "")),
        ]
    ).lower()
    label_kind = _infer_label_kind(target_column=target_column, corpus=corpus)
    weak_label_risk_level = _infer_weak_label_risk_level(
        ordered_temporal=ordered_temporal,
        label_kind=label_kind,
        corpus=corpus,
    )
    delayed_confirmation_likely = ordered_temporal and weak_label_risk_level in {"moderate", "high"}

    ordered_frame = _sort_frame(frame=frame, timestamp_column=timestamp_column)
    rolling_report = _build_rolling_alert_quality_report(
        generated_at=generated_at,
        frame=ordered_frame,
        target_column=target_column,
        timestamp_column=timestamp_column,
        review_fraction=review_fraction,
        benchmark_safe=benchmark_safe,
        rolling_cv_plan=rolling_cv_plan,
    )
    drift_trigger = _build_drift_recalibration_trigger(
        generated_at=generated_at,
        rolling_report=rolling_report,
        target_column=target_column,
        review_fraction=review_fraction,
        lifecycle_drift_score=_safe_float(((dict(champion_vs_candidate.get("fresh_data_behavior") or {}).get("drift_summary") or {}).get("overall_drift_score"))),
        recalibration_decision=recalibration_decision,
        retrain_decision=retrain_decision,
    )
    weak_label_posture = {
        "schema_version": WEAK_LABEL_POSTURE_SCHEMA_VERSION,
        "generated_at": generated_at,
        "status": "active" if ordered_temporal else "partial",
        "label_kind": label_kind,
        "weak_label_risk_level": weak_label_risk_level,
        "delayed_confirmation_likely": delayed_confirmation_likely,
        "ordered_temporal_structure": ordered_temporal,
        "adaptation_policy": (
            "threshold_and_recalibration_before_retrain"
            if weak_label_risk_level in {"moderate", "high"}
            else "standard_supervised_refresh"
        ),
        "promotion_guard": (
            "require_holdout_and_shadow_confirmation_before_promotion"
            if weak_label_risk_level == "high"
            else "standard_holdout_confirmation"
        ),
        "summary": (
            f"Relaytic-AML treats `{target_column or 'unknown_target'}` as `{label_kind}` with weak-label risk "
            f"`{weak_label_risk_level}` under `{stream_mode}` posture."
        ),
    }
    delayed_outcome_alignment = {
        "schema_version": DELAYED_OUTCOME_ALIGNMENT_SCHEMA_VERSION,
        "generated_at": generated_at,
        "status": "active" if ordered_temporal else "partial",
        "alignment_state": (
            "rolling_shadow_holdout"
            if delayed_confirmation_likely and ordered_temporal
            else "direct_label_evaluation"
        ),
        "delayed_confirmation_likely": delayed_confirmation_likely,
        "expected_feedback_latency": "multi_window" if delayed_confirmation_likely else "same_window",
        "rolling_window_count": int(rolling_report.get("window_count", 0) or 0),
        "benchmark_safe": benchmark_safe,
        "recommended_policy": (
            "prefer rolling holdout comparisons and threshold recalibration before route promotion"
            if delayed_confirmation_likely
            else "standard temporal holdout evaluation is sufficient"
        ),
        "summary": (
            "Relaytic-AML aligns delayed outcomes through rolling temporal windows and explicit recalibration posture."
            if delayed_confirmation_likely
            else "Relaytic-AML did not detect strong delayed-outcome pressure on this run."
        ),
    }
    stream_risk_posture = {
        "schema_version": STREAM_RISK_POSTURE_SCHEMA_VERSION,
        "generated_at": generated_at,
        "status": "active" if ordered_temporal else "partial",
        "stream_mode": stream_mode,
        "ordered_temporal_structure": ordered_temporal,
        "timestamp_column": timestamp_column,
        "target_column": target_column,
        "weak_label_risk_level": weak_label_risk_level,
        "delayed_confirmation_likely": delayed_confirmation_likely,
        "rolling_window_count": int(rolling_report.get("window_count", 0) or 0),
        "latest_alert_rate": rolling_report.get("latest_alert_rate"),
        "recalibration_triggered": drift_trigger.get("trigger_recalibration"),
        "trigger_action": _clean_text(drift_trigger.get("recommended_action")),
        "selected_threshold": operating_point_contract.get("selected_threshold"),
        "benchmark_safe": benchmark_safe,
        "audit_safe": bool(timestamp_column and target_column and rolling_report.get("window_count", 0)),
        "summary": (
            f"Relaytic-AML is running `{stream_mode}` with timestamp column `{timestamp_column or 'none'}`, "
            f"weak-label risk `{weak_label_risk_level}`, and trigger action `{_clean_text(drift_trigger.get('recommended_action')) or 'none'}`."
        ),
    }
    return {
        "stream_risk_posture": stream_risk_posture,
        "weak_label_posture": weak_label_posture,
        "delayed_outcome_alignment": delayed_outcome_alignment,
        "drift_recalibration_trigger": drift_trigger,
        "rolling_alert_quality_report": rolling_report,
    }


def _inactive_stream_risk_artifacts(*, generated_at: str, summary: str, status: str = "not_applicable") -> dict[str, dict[str, Any]]:
    base = {
        "generated_at": generated_at,
        "status": status,
        "summary": summary,
    }
    return {
        "stream_risk_posture": {
            "schema_version": STREAM_RISK_POSTURE_SCHEMA_VERSION,
            **base,
            "stream_mode": "not_applicable",
            "ordered_temporal_structure": False,
            "timestamp_column": None,
            "target_column": None,
            "weak_label_risk_level": "not_applicable",
            "delayed_confirmation_likely": False,
            "rolling_window_count": 0,
            "recalibration_triggered": False,
            "trigger_action": None,
            "benchmark_safe": None,
            "audit_safe": False,
        },
        "weak_label_posture": {
            "schema_version": WEAK_LABEL_POSTURE_SCHEMA_VERSION,
            **base,
            "label_kind": "not_applicable",
            "weak_label_risk_level": "not_applicable",
            "delayed_confirmation_likely": False,
        },
        "delayed_outcome_alignment": {
            "schema_version": DELAYED_OUTCOME_ALIGNMENT_SCHEMA_VERSION,
            **base,
            "alignment_state": "not_applicable",
            "delayed_confirmation_likely": False,
            "benchmark_safe": None,
            "rolling_window_count": 0,
        },
        "drift_recalibration_trigger": {
            "schema_version": DRIFT_RECALIBRATION_TRIGGER_SCHEMA_VERSION,
            **base,
            "trigger_recalibration": False,
            "recommended_action": None,
            "drift_score": 0.0,
            "reason_codes": [],
        },
        "rolling_alert_quality_report": {
            "schema_version": ROLLING_ALERT_QUALITY_REPORT_SCHEMA_VERSION,
            **base,
            "window_count": 0,
            "target_column": None,
            "timestamp_column": None,
            "rows": [],
        },
    }


def _build_rolling_alert_quality_report(
    *,
    generated_at: str,
    frame: pd.DataFrame | None,
    target_column: str | None,
    timestamp_column: str | None,
    review_fraction: float,
    benchmark_safe: bool,
    rolling_cv_plan: dict[str, Any],
) -> dict[str, Any]:
    if frame is None or frame.empty or not target_column or target_column not in frame.columns:
        return {
            "schema_version": ROLLING_ALERT_QUALITY_REPORT_SCHEMA_VERSION,
            "generated_at": generated_at,
            "status": "not_available",
            "target_column": target_column,
            "timestamp_column": timestamp_column,
            "window_count": 0,
            "rows": [],
            "summary": "Relaytic-AML could not build rolling alert quality windows because the target column was unavailable.",
        }

    target_values = _coerce_binary_series(frame[target_column])
    if target_values is None:
        return {
            "schema_version": ROLLING_ALERT_QUALITY_REPORT_SCHEMA_VERSION,
            "generated_at": generated_at,
            "status": "not_available",
            "target_column": target_column,
            "timestamp_column": timestamp_column,
            "window_count": 0,
            "rows": [],
            "summary": "Relaytic-AML could not build rolling alert quality windows because the target could not be interpreted as a binary alert series.",
        }

    window_count = min(6, max(3, int(math.ceil(len(frame) / 8))))
    window_size = max(4, int(math.ceil(len(frame) / float(window_count))))
    amount_column = _preferred_amount_column(frame.columns)
    rows: list[dict[str, Any]] = []
    for window_index, start in enumerate(range(0, len(frame), window_size), start=1):
        window = frame.iloc[start : start + window_size].copy()
        labels = target_values.iloc[start : start + window_size]
        if window.empty:
            continue
        review_capacity_cases = max(1, min(len(window), math.ceil(len(window) * review_fraction)))
        amount_mean = None
        if amount_column and amount_column in window.columns:
            numeric = pd.to_numeric(window[amount_column], errors="coerce")
            if not numeric.dropna().empty:
                amount_mean = round(float(numeric.dropna().mean()), 4)
        rows.append(
            {
                "window_id": f"window_{window_index:02d}",
                "window_rank": window_index,
                "start_index": int(start),
                "end_index": int(start + len(window) - 1),
                "start_value": _window_boundary_value(window, timestamp_column, first=True),
                "end_value": _window_boundary_value(window, timestamp_column, first=False),
                "row_count": int(len(window)),
                "alert_rate": round(float(labels.mean()), 4),
                "review_capacity_cases": review_capacity_cases,
                "amount_mean": amount_mean,
            }
        )

    latest_alert_rate = rows[-1]["alert_rate"] if rows else None
    alert_rates = [float(row.get("alert_rate", 0.0) or 0.0) for row in rows]
    return {
        "schema_version": ROLLING_ALERT_QUALITY_REPORT_SCHEMA_VERSION,
        "generated_at": generated_at,
        "status": "active" if rows else "not_available",
        "target_column": target_column,
        "timestamp_column": timestamp_column,
        "window_count": len(rows),
        "review_budget_fraction": review_fraction,
        "benchmark_safe": benchmark_safe,
        "recommended_strategy": _clean_text(rolling_cv_plan.get("recommended_strategy")),
        "overall_avg_alert_rate": round(sum(alert_rates) / max(len(alert_rates), 1), 4) if rows else None,
        "max_alert_rate": round(max(alert_rates), 4) if rows else None,
        "min_alert_rate": round(min(alert_rates), 4) if rows else None,
        "latest_alert_rate": latest_alert_rate,
        "rows": rows,
        "summary": (
            f"Relaytic-AML built `{len(rows)}` rolling alert-quality window(s) to track alert pressure under stream-risk posture."
            if rows
            else "Relaytic-AML could not build rolling alert-quality windows."
        ),
    }


def _build_drift_recalibration_trigger(
    *,
    generated_at: str,
    rolling_report: dict[str, Any],
    target_column: str | None,
    review_fraction: float,
    lifecycle_drift_score: float,
    recalibration_decision: dict[str, Any],
    retrain_decision: dict[str, Any],
) -> dict[str, Any]:
    rows = list(rolling_report.get("rows", [])) if isinstance(rolling_report.get("rows"), list) else []
    first_row = dict(rows[0]) if rows else {}
    last_row = dict(rows[-1]) if rows else {}
    alert_rate_shift = abs(_safe_float(last_row.get("alert_rate")) - _safe_float(first_row.get("alert_rate")))
    amount_shift = 0.0
    if first_row.get("amount_mean") is not None and last_row.get("amount_mean") is not None:
        first_amount = _safe_float(first_row.get("amount_mean"))
        last_amount = _safe_float(last_row.get("amount_mean"))
        denominator = max(abs(first_amount), 1.0)
        amount_shift = min(1.0, abs(last_amount - first_amount) / denominator)
    drift_score = round(max(alert_rate_shift, amount_shift, lifecycle_drift_score), 4)

    reason_codes: list[str] = []
    if alert_rate_shift >= 0.15:
        reason_codes.append("alert_rate_shift")
    if amount_shift >= 0.25:
        reason_codes.append("amount_mean_shift")
    if lifecycle_drift_score >= 0.30:
        reason_codes.append("lifecycle_drift_signal")
    if _clean_text(recalibration_decision.get("action")) in {"recalibrate", "recalibrate_and_review"}:
        reason_codes.append("lifecycle_recalibration_request")
    if _clean_text(retrain_decision.get("action")) in {"retrain", "retrain_and_review"}:
        reason_codes.append("lifecycle_retrain_request")

    if drift_score >= 0.55:
        trigger_state = "triggered"
        trigger_recalibration = True
        recommended_action = "run_recalibration_pass"
        threshold_posture = "tighten_review_threshold"
    elif drift_score >= 0.30:
        trigger_state = "watch"
        trigger_recalibration = False
        recommended_action = "tighten_threshold_and_monitor"
        threshold_posture = "monitor_with_tighter_threshold"
    else:
        trigger_state = "stable"
        trigger_recalibration = False
        recommended_action = "hold_current_threshold"
        threshold_posture = "hold"

    return {
        "schema_version": DRIFT_RECALIBRATION_TRIGGER_SCHEMA_VERSION,
        "generated_at": generated_at,
        "status": "active" if rows else "not_available",
        "trigger_state": trigger_state,
        "trigger_recalibration": trigger_recalibration,
        "recommended_action": recommended_action,
        "threshold_posture": threshold_posture,
        "drift_score": drift_score,
        "alert_rate_shift": round(alert_rate_shift, 4),
        "amount_mean_shift": round(amount_shift, 4),
        "review_budget_fraction": review_fraction,
        "target_column": target_column,
        "reason_codes": reason_codes,
        "summary": (
            f"Relaytic-AML computed drift score `{drift_score:.4f}` and recommends `{recommended_action}` under review fraction `{review_fraction:.2f}`."
            if rows
            else "Relaytic-AML did not have enough rolling evidence to build a drift-trigger decision."
        ),
    }


def _resolve_timestamp_column(*, frame: pd.DataFrame | None, preferred: str | None) -> str | None:
    if preferred and frame is not None and preferred in frame.columns:
        return preferred
    if frame is None:
        return preferred
    for candidate in ("timestamp", "event_time", "time_step", "step", "ts", "date"):
        if candidate in frame.columns:
            return candidate
    return preferred


def _sort_frame(*, frame: pd.DataFrame | None, timestamp_column: str | None) -> pd.DataFrame:
    if frame is None:
        return pd.DataFrame()
    if timestamp_column and timestamp_column in frame.columns:
        try:
            return frame.sort_values(by=timestamp_column, kind="stable").reset_index(drop=True)
        except Exception:
            return frame.reset_index(drop=True)
    return frame.reset_index(drop=True)


def _preferred_amount_column(columns: Any) -> str | None:
    names = [str(column) for column in columns]
    for candidate in ("amount", "txn_amount"):
        if candidate in names:
            return candidate
    return None


def _infer_label_kind(*, target_column: str | None, corpus: str) -> str:
    target = (target_column or "").lower()
    if any(token in target for token in ("suspicious", "flag", "alert", "queue", "review")):
        return "proxy_alert_label"
    if any(token in target for token in ("fraud", "chargeback", "confirmed", "loss")):
        return "confirmed_outcome_label"
    if "weak label" in corpus or "weak labels" in corpus:
        return "proxy_alert_label"
    return "unknown_label_kind"


def _infer_weak_label_risk_level(*, ordered_temporal: bool, label_kind: str, corpus: str) -> str:
    if not ordered_temporal and label_kind == "confirmed_outcome_label":
        return "low"
    if label_kind == "proxy_alert_label":
        return "high" if ordered_temporal else "moderate"
    if label_kind == "confirmed_outcome_label":
        return "moderate" if ordered_temporal else "low"
    if any(token in corpus for token in ("delayed", "weak", "review", "triage", "analyst")):
        return "moderate" if ordered_temporal else "low"
    return "moderate" if ordered_temporal else "low"


def _coerce_binary_series(series: pd.Series) -> pd.Series | None:
    numeric = pd.to_numeric(series, errors="coerce")
    if numeric.notna().sum() == len(series):
        unique = sorted({int(value) for value in numeric.dropna().tolist()})
        if set(unique).issubset({0, 1}):
            return numeric.astype(float)
    normalized = series.astype(str).str.strip().str.lower()
    mapping = {"false": 0.0, "true": 1.0, "no": 0.0, "yes": 1.0}
    if normalized.isin(mapping.keys()).all():
        return normalized.map(mapping).astype(float)
    return None


def _window_boundary_value(window: pd.DataFrame, timestamp_column: str | None, *, first: bool) -> Any:
    if timestamp_column and timestamp_column in window.columns:
        value = window.iloc[0 if first else -1][timestamp_column]
        if isinstance(value, (int, float, str)):
            return value
        return str(value)
    return int(window.index[0 if first else -1])


def _load_frame(data_path: str | Path | None) -> pd.DataFrame | None:
    if not data_path:
        return None
    path = Path(data_path)
    if not path.exists():
        return None
    try:
        return load_tabular_data(path).frame.copy()
    except Exception:
        return None


def _bundle_item(bundle: dict[str, Any], key: str) -> dict[str, Any]:
    value = bundle.get(key)
    return dict(value) if isinstance(value, dict) else {}


def _clean_text(value: Any) -> str | None:
    text = str(value).strip()
    return text or None


def _safe_float(value: Any) -> float:
    try:
        if value is None or value == "":
            return 0.0
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _resolve_review_fraction(
    *,
    operating_point_contract: dict[str, Any],
    review_budget_optimization_report: dict[str, Any],
) -> float:
    for source in (
        operating_point_contract.get("selected_review_fraction"),
        operating_point_contract.get("review_budget_fraction"),
        review_budget_optimization_report.get("selected_review_fraction"),
        review_budget_optimization_report.get("review_budget_fraction"),
    ):
        value = _safe_float(source)
        if value > 0.0:
            return min(0.95, max(0.05, value))
    return 0.15


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()
