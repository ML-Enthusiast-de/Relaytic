"""Temporal, delayed-label, and weak-label proof artifacts for Relaytic-AML."""

from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any

from relaytic.core.json_utils import write_json
from relaytic.stream_risk import read_stream_risk_artifacts, sync_stream_risk_artifacts


AML_DELAYED_LABEL_EVAL_REPORT_SCHEMA_VERSION = "relaytic.aml_delayed_label_eval_report.v1"
AML_POSITIVE_UNLABELED_POSTURE_SCHEMA_VERSION = "relaytic.aml_positive_unlabeled_posture.v1"
AML_THRESHOLD_DRIFT_REPORT_SCHEMA_VERSION = "relaytic.aml_threshold_drift_report.v1"
AML_TIME_WINDOW_SCORECARD_SCHEMA_VERSION = "relaytic.aml_time_window_scorecard.v1"
AML_TEMPORAL_BENCHMARK_CLAIM_REPORT_SCHEMA_VERSION = "relaytic.aml_temporal_benchmark_claim_report.v1"

AML_TEMPORAL_FILENAMES = {
    "aml_delayed_label_eval_report": "aml_delayed_label_eval_report.json",
    "aml_positive_unlabeled_posture": "aml_positive_unlabeled_posture.json",
    "aml_threshold_drift_report": "aml_threshold_drift_report.json",
    "aml_time_window_scorecard": "aml_time_window_scorecard.json",
    "aml_temporal_benchmark_claim_report": "aml_temporal_benchmark_claim_report.json",
}

_ACTIVE_STATUSES = {"active", "ok", "ready", "partial", "supporting_only", "guarded", "warn"}
_BLOCKED_SPLIT_STATES = {"blocked", "fail", "failed", "unsafe", "leakage_detected"}


def sync_aml_temporal_artifacts(
    run_dir: str | Path,
    *,
    data_path: str | Path | None = None,
    context_bundle: dict[str, Any] | None = None,
    task_contract_bundle: dict[str, Any] | None = None,
    temporal_bundle: dict[str, Any] | None = None,
    operating_point_bundle: dict[str, Any] | None = None,
    lifecycle_bundle: dict[str, Any] | None = None,
    benchmark_bundle: dict[str, Any] | None = None,
) -> dict[str, Path]:
    """Build and write Slice 15W AML temporal and weak-label artifacts."""
    root = Path(run_dir)
    stream_risk_bundle = read_stream_risk_artifacts(root)
    if data_path is not None and task_contract_bundle is not None:
        sync_stream_risk_artifacts(
            root,
            data_path=data_path,
            context_bundle=context_bundle,
            task_contract_bundle=task_contract_bundle,
            temporal_bundle=temporal_bundle,
            operating_point_bundle=operating_point_bundle,
            lifecycle_bundle=lifecycle_bundle,
        )
        stream_risk_bundle = read_stream_risk_artifacts(root)
    elif not stream_risk_bundle:
        sync_stream_risk_artifacts(
            root,
            data_path=data_path,
            context_bundle=context_bundle,
            task_contract_bundle=task_contract_bundle,
            temporal_bundle=temporal_bundle,
            operating_point_bundle=operating_point_bundle,
            lifecycle_bundle=lifecycle_bundle,
        )
        stream_risk_bundle = read_stream_risk_artifacts(root)
    artifacts = build_aml_temporal_artifacts(
        run_dir=root,
        stream_risk_bundle=stream_risk_bundle,
        temporal_bundle=temporal_bundle,
        task_contract_bundle=task_contract_bundle,
        operating_point_bundle=operating_point_bundle,
        benchmark_bundle=benchmark_bundle,
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
        for key, filename in AML_TEMPORAL_FILENAMES.items()
    }


def read_aml_temporal_artifacts(run_dir: str | Path) -> dict[str, Any]:
    """Read AML temporal artifacts if present."""
    root = Path(run_dir)
    payload: dict[str, Any] = {}
    for key, filename in AML_TEMPORAL_FILENAMES.items():
        path = root / filename
        if not path.exists():
            continue
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if isinstance(value, dict):
            payload[key] = value
    return payload


def build_aml_temporal_artifacts(
    *,
    run_dir: str | Path,
    stream_risk_bundle: dict[str, Any] | None = None,
    temporal_bundle: dict[str, Any] | None = None,
    task_contract_bundle: dict[str, Any] | None = None,
    operating_point_bundle: dict[str, Any] | None = None,
    benchmark_bundle: dict[str, Any] | None = None,
) -> dict[str, dict[str, Any]]:
    """Construct Slice 15W temporal and weak-label proof artifacts without raw rows."""
    root = Path(run_dir)
    generated_at = _utc_now()
    stream_risk_bundle = stream_risk_bundle or read_stream_risk_artifacts(root)
    temporal_bundle = temporal_bundle or _read_payloads(
        root,
        {
            "temporal_structure_report": "temporal_structure_report.json",
            "temporal_split_guard_report": "temporal_split_guard_report.json",
            "rolling_cv_plan": "rolling_cv_plan.json",
            "sequence_shadow_scorecard": "sequence_shadow_scorecard.json",
            "temporal_baseline_ladder": "temporal_baseline_ladder.json",
            "temporal_metric_contract": "temporal_metric_contract.json",
        },
    )
    task_contract_bundle = task_contract_bundle or _read_payloads(
        root,
        {
            "aml_domain_contract": "aml_domain_contract.json",
            "task_profile_contract": "task_profile_contract.json",
            "benchmark_truth_precheck": "benchmark_truth_precheck.json",
            "temporal_fold_health": "temporal_fold_health.json",
        },
    )
    operating_point_bundle = operating_point_bundle or _read_payloads(
        root,
        {
            "operating_point_contract": "operating_point_contract.json",
            "threshold_search_report": "threshold_search_report.json",
            "review_budget_optimization_report": "review_budget_optimization_report.json",
        },
    )
    benchmark_bundle = benchmark_bundle or _read_payloads(
        root,
        {
            "benchmark_release_gate": "benchmark_release_gate.json",
            "benchmark_truth_audit": "benchmark_truth_audit.json",
            "dataset_leakage_audit": "dataset_leakage_audit.json",
            "paper_claim_guard_report": "paper_claim_guard_report.json",
            "aml_public_claim_guard": "aml_public_claim_guard.json",
        },
    )

    source = _source_view(
        stream_risk_bundle=stream_risk_bundle,
        temporal_bundle=temporal_bundle,
        task_contract_bundle=task_contract_bundle,
        operating_point_bundle=operating_point_bundle,
        benchmark_bundle=benchmark_bundle,
    )
    if not source["aml_active"]:
        return _inactive_aml_temporal_artifacts(
            generated_at=generated_at,
            summary="Relaytic-AML temporal posture is not applicable because the AML domain contract is inactive.",
        )

    time_window_scorecard = _build_time_window_scorecard(generated_at=generated_at, source=source)
    delayed_label_eval_report = _build_delayed_label_eval_report(
        generated_at=generated_at,
        source=source,
        time_window_scorecard=time_window_scorecard,
    )
    positive_unlabeled_posture = _build_positive_unlabeled_posture(
        generated_at=generated_at,
        source=source,
        delayed_label_eval_report=delayed_label_eval_report,
    )
    threshold_drift_report = _build_threshold_drift_report(
        generated_at=generated_at,
        source=source,
        time_window_scorecard=time_window_scorecard,
    )
    temporal_benchmark_claim_report = _build_temporal_benchmark_claim_report(
        generated_at=generated_at,
        source=source,
        time_window_scorecard=time_window_scorecard,
        delayed_label_eval_report=delayed_label_eval_report,
        positive_unlabeled_posture=positive_unlabeled_posture,
        threshold_drift_report=threshold_drift_report,
    )
    return {
        "aml_delayed_label_eval_report": delayed_label_eval_report,
        "aml_positive_unlabeled_posture": positive_unlabeled_posture,
        "aml_threshold_drift_report": threshold_drift_report,
        "aml_time_window_scorecard": time_window_scorecard,
        "aml_temporal_benchmark_claim_report": temporal_benchmark_claim_report,
    }


def render_aml_temporal_markdown(bundle: dict[str, Any]) -> str:
    """Render a compact human-facing summary of Slice 15W AML temporal posture."""
    delayed = _as_dict(bundle.get("aml_delayed_label_eval_report"))
    pu = _as_dict(bundle.get("aml_positive_unlabeled_posture"))
    drift = _as_dict(bundle.get("aml_threshold_drift_report"))
    windows = _as_dict(bundle.get("aml_time_window_scorecard"))
    claims = _as_dict(bundle.get("aml_temporal_benchmark_claim_report"))
    blockers = [
        str(item)
        for item in claims.get("claim_blockers", [])
        if str(item).strip()
    ]
    return "\n".join(
        [
            "# Relaytic-AML Temporal Posture",
            "",
            f"- Claim state: `{claims.get('claim_state') or 'unknown'}`",
            f"- Temporal public claim allowed: `{claims.get('temporal_public_claim_allowed')}`",
            f"- Supporting temporal evidence allowed: `{claims.get('supporting_temporal_evidence_allowed')}`",
            f"- Sequence-native claim allowed: `{claims.get('sequence_native_claim_allowed')}`",
            f"- Delayed-label status: `{delayed.get('status') or 'unknown'}`",
            f"- PU risk state: `{pu.get('pu_risk_state') or 'unknown'}`",
            f"- Threshold drift state: `{drift.get('threshold_drift_state') or 'unknown'}`",
            f"- Recommended action: `{drift.get('recommended_action') or claims.get('recommended_next_action') or 'none'}`",
            f"- Time windows: `{windows.get('window_count', 0)}`",
            f"- Zero-positive future folds: `{windows.get('zero_positive_future_fold_count', 0)}`",
            "",
            "## Claim Blockers",
            *(f"- `{item}`" for item in blockers[:8]),
            *(["- none"] if not blockers else []),
        ]
    ).rstrip() + "\n"


def _build_time_window_scorecard(*, generated_at: str, source: dict[str, Any]) -> dict[str, Any]:
    rows = []
    for raw in source["rolling_rows"]:
        row = dict(raw)
        row_count = _safe_int(row.get("row_count"))
        alert_rate = _safe_float(row.get("alert_rate"))
        positive_count = int(round(alert_rate * row_count)) if row_count > 0 else 0
        zero_positive = row_count > 0 and positive_count == 0
        rows.append(
            {
                "window_id": _clean_text(row.get("window_id")) or f"window_{len(rows) + 1:02d}",
                "window_rank": _safe_int(row.get("window_rank")) or len(rows) + 1,
                "start_value": row.get("start_value"),
                "end_value": row.get("end_value"),
                "row_count": row_count,
                "alert_rate": round(alert_rate, 4),
                "positive_count_estimate": positive_count,
                "zero_positive_window": zero_positive,
                "review_capacity_cases": _safe_int(row.get("review_capacity_cases")),
                "amount_mean": row.get("amount_mean"),
            }
        )
    zero_positive_count = sum(1 for row in rows if bool(row.get("zero_positive_window")))
    zero_positive_future_count = sum(
        1
        for row in rows
        if bool(row.get("zero_positive_window")) and _safe_int(row.get("window_rank")) > 1
    )
    aggregate_alert_rate = source["rolling_report"].get("overall_avg_alert_rate")
    if aggregate_alert_rate is None and rows:
        aggregate_alert_rate = round(sum(_safe_float(row.get("alert_rate")) for row in rows) / len(rows), 4)
    status = "active" if rows and source["timestamp_column"] else "blocked"
    recommendations = []
    if not source["timestamp_column"]:
        recommendations.append("provide_timestamp_column")
    if not rows:
        recommendations.append("materialize_rolling_alert_windows")
    if zero_positive_future_count:
        recommendations.append("collect_or_resplit_future_windows_with_positive_cases")
    return {
        "schema_version": AML_TIME_WINDOW_SCORECARD_SCHEMA_VERSION,
        "generated_at": generated_at,
        "status": status,
        "timestamp_column": source["timestamp_column"],
        "target_column": source["target_column"],
        "window_count": len(rows),
        "time_sliced_metric_count": len(rows),
        "aggregate_alert_rate": aggregate_alert_rate,
        "latest_alert_rate": source["rolling_report"].get("latest_alert_rate"),
        "min_alert_rate": source["rolling_report"].get("min_alert_rate"),
        "max_alert_rate": source["rolling_report"].get("max_alert_rate"),
        "zero_positive_window_count": zero_positive_count,
        "zero_positive_future_fold_count": zero_positive_future_count,
        "future_fold_positive_state": "blocked" if zero_positive_future_count else ("ok" if rows else "not_available"),
        "review_budget_fraction": source["rolling_report"].get("review_budget_fraction"),
        "recommended_strategy": source["rolling_report"].get("recommended_strategy")
        or source["rolling_cv_plan"].get("recommended_strategy"),
        "required_data_recommendations": recommendations,
        "rows": rows,
        "summary": (
            f"Relaytic-AML separated `{len(rows)}` ordered alert-quality window(s) from aggregate metrics."
            if rows
            else "Relaytic-AML could not build ordered time-window scorecards."
        ),
        "trace": _trace(["rolling_alert_quality_report", "temporal_engine"]),
    }


def _build_delayed_label_eval_report(
    *,
    generated_at: str,
    source: dict[str, Any],
    time_window_scorecard: dict[str, Any],
) -> dict[str, Any]:
    delayed_required = bool(source["delayed_confirmation_likely"]) or source["expected_feedback_latency"] == "multi_window"
    matured_count = _resolve_matured_outcome_window_count(source=source, delayed_required=delayed_required)
    required_data = []
    claim_blockers = []
    if not source["timestamp_column"]:
        required_data.append("timestamp column or ordered event index")
        claim_blockers.append("missing_timestamp")
    if _safe_int(time_window_scorecard.get("window_count")) < 3:
        required_data.append("at least three ordered evaluation windows")
        claim_blockers.append("insufficient_time_windows")
    if delayed_required and matured_count <= 0:
        required_data.append("matured delayed-outcome windows or explicit confirmation lag")
        claim_blockers.append("delayed_label_maturity_unproven")
    if _safe_int(time_window_scorecard.get("zero_positive_future_fold_count")) > 0:
        required_data.append("future evaluation windows with positive outcomes")
        claim_blockers.append("zero_positive_future_fold")
    status = "blocked" if claim_blockers else ("active" if delayed_required else "direct")
    return {
        "schema_version": AML_DELAYED_LABEL_EVAL_REPORT_SCHEMA_VERSION,
        "generated_at": generated_at,
        "status": status,
        "alignment_state": source["delayed_alignment_state"],
        "delayed_confirmation_likely": source["delayed_confirmation_likely"],
        "expected_feedback_latency": source["expected_feedback_latency"],
        "delayed_label_window_count": _safe_int(time_window_scorecard.get("window_count")),
        "matured_outcome_window_count": matured_count,
        "delayed_label_evidence_state": (
            "maturity_missing"
            if delayed_required and matured_count <= 0
            else ("maturity_observed" if delayed_required else "direct_label_evaluation")
        ),
        "evaluation_policy": {
            "primary_policy": "rolling_shadow_holdout" if delayed_required else "direct_temporal_holdout",
            "public_claim_policy": (
                "block_temporal_claims_until_matured_delayed_outcomes_exist"
                if delayed_required and matured_count <= 0
                else "allow_only_time_window_claims_supported_by_observed_outcomes"
            ),
            "raw_rows_included": False,
        },
        "required_data_recommendations": required_data,
        "claim_blockers": list(dict.fromkeys(claim_blockers)),
        "summary": (
            "Relaytic-AML blocks temporal claims until delayed outcomes mature across ordered windows."
            if claim_blockers
            else "Relaytic-AML has enough delayed-label evidence for guarded time-window evaluation."
        ),
        "trace": _trace(["delayed_outcome_alignment", "rolling_alert_quality_report"]),
    }


def _build_positive_unlabeled_posture(
    *,
    generated_at: str,
    source: dict[str, Any],
    delayed_label_eval_report: dict[str, Any],
) -> dict[str, Any]:
    label_kind = source["label_kind"]
    weak_risk = source["weak_label_risk_level"]
    proxy_or_unresolved = (
        label_kind in {"proxy_alert_label", "unknown_label_kind"}
        or weak_risk in {"high", "moderate"}
        or bool(source["delayed_confirmation_likely"])
    )
    if label_kind == "proxy_alert_label" or weak_risk == "high":
        pu_risk_state = "positive_unlabeled_required"
    elif proxy_or_unresolved:
        pu_risk_state = "positive_unlabeled_watch"
    else:
        pu_risk_state = "not_required"
    blockers = []
    if pu_risk_state in {"positive_unlabeled_required", "positive_unlabeled_watch"}:
        blockers.append("positive_unlabeled_truth_unresolved")
    if delayed_label_eval_report.get("status") == "blocked":
        blockers.extend(delayed_label_eval_report.get("claim_blockers", []))
    assume_unlabeled_negative = pu_risk_state == "not_required"
    return {
        "schema_version": AML_POSITIVE_UNLABELED_POSTURE_SCHEMA_VERSION,
        "generated_at": generated_at,
        "status": "active" if proxy_or_unresolved else "low_risk",
        "label_kind": label_kind,
        "weak_label_risk_level": weak_risk,
        "pu_risk_state": pu_risk_state,
        "assume_unlabeled_are_negative_allowed": assume_unlabeled_negative,
        "recommended_training_posture": (
            "treat unlabeled outcomes as unlabeled, not confirmed negatives; require delayed-outcome or analyst-confirmation evidence"
            if not assume_unlabeled_negative
            else "standard supervised evaluation may be used for label posture"
        ),
        "adaptation_policy": source["weak_label_posture"].get("adaptation_policy"),
        "promotion_guard": source["weak_label_posture"].get("promotion_guard"),
        "public_claim_blockers": list(dict.fromkeys(str(item) for item in blockers if str(item).strip())),
        "summary": (
            "Relaytic-AML treats the label stream as positive-unlabeled or proxy-labeled for public temporal claims."
            if not assume_unlabeled_negative
            else "Relaytic-AML did not detect a positive-unlabeled label posture."
        ),
        "trace": _trace(["weak_label_posture", "delayed_label_eval_report"]),
    }


def _build_threshold_drift_report(
    *,
    generated_at: str,
    source: dict[str, Any],
    time_window_scorecard: dict[str, Any],
) -> dict[str, Any]:
    drift = source["drift_recalibration_trigger"]
    trigger_state = _clean_text(drift.get("trigger_state")) or "not_available"
    recommended_action = _clean_text(drift.get("recommended_action")) or "observe_more_temporal_evidence"
    threshold_reset_recommended = trigger_state in {"triggered", "watch"} or recommended_action in {
        "run_recalibration_pass",
        "tighten_threshold_and_monitor",
    }
    decision_options = ["hold_current_threshold", "tighten_threshold_and_monitor", "observe_more_delayed_outcomes"]
    if threshold_reset_recommended:
        decision_options.insert(0, "run_recalibration_pass")
    reason_codes = [
        str(item)
        for item in drift.get("reason_codes", [])
        if str(item).strip()
    ]
    if _safe_int(time_window_scorecard.get("zero_positive_future_fold_count")) > 0:
        reason_codes.append("zero_positive_future_fold")
    status = "active" if _clean_text(drift.get("status")) in _ACTIVE_STATUSES else "not_available"
    return {
        "schema_version": AML_THRESHOLD_DRIFT_REPORT_SCHEMA_VERSION,
        "generated_at": generated_at,
        "status": status,
        "threshold_drift_state": trigger_state,
        "drift_score": drift.get("drift_score"),
        "alert_rate_shift": drift.get("alert_rate_shift"),
        "amount_mean_shift": drift.get("amount_mean_shift"),
        "review_budget_fraction": drift.get("review_budget_fraction")
        or time_window_scorecard.get("review_budget_fraction"),
        "selected_threshold": source["operating_point_contract"].get("selected_threshold"),
        "threshold_policy": source["threshold_search_report"].get("threshold_policy")
        or source["operating_point_contract"].get("threshold_policy"),
        "threshold_reset_recommended": threshold_reset_recommended,
        "recalibration_recommended": bool(drift.get("trigger_recalibration")),
        "recommended_action": recommended_action,
        "decision_options": list(dict.fromkeys(decision_options)),
        "reason_codes": list(dict.fromkeys(reason_codes)),
        "summary": (
            f"Relaytic-AML threshold drift is `{trigger_state}` and recommends `{recommended_action}`."
            if status == "active"
            else "Relaytic-AML did not have enough temporal evidence to evaluate threshold drift."
        ),
        "trace": _trace(["drift_recalibration_trigger", "threshold_search_report", "rolling_alert_quality_report"]),
    }


def _build_temporal_benchmark_claim_report(
    *,
    generated_at: str,
    source: dict[str, Any],
    time_window_scorecard: dict[str, Any],
    delayed_label_eval_report: dict[str, Any],
    positive_unlabeled_posture: dict[str, Any],
    threshold_drift_report: dict[str, Any],
) -> dict[str, Any]:
    blockers = []
    blockers.extend(delayed_label_eval_report.get("claim_blockers", []))
    blockers.extend(positive_unlabeled_posture.get("public_claim_blockers", []))
    if _clean_text(source["temporal_split_guard_report"].get("guard_state")) in _BLOCKED_SPLIT_STATES:
        blockers.append("future_leakage_or_split_guard_blocked")
    if _clean_text(source["benchmark_truth_precheck"].get("status")) == "blocked" or source["benchmark_truth_precheck"].get("safe_to_rank") is False:
        blockers.append("benchmark_truth_precheck_blocked")
    if _clean_text(source["dataset_leakage_audit"].get("status")) == "blocked":
        blockers.append("dataset_leakage_audit_blocked")
    if threshold_drift_report.get("threshold_drift_state") == "triggered":
        blockers.append("threshold_drift_requires_recalibration")
    blockers = list(dict.fromkeys(str(item) for item in blockers if str(item).strip()))

    supporting_allowed = bool(source["timestamp_column"]) and _safe_int(time_window_scorecard.get("window_count")) >= 2
    temporal_public_claim_allowed = supporting_allowed and not blockers
    sequence_state = _sequence_candidate_state(source=source)
    sequence_native_claim_allowed = sequence_state["sequence_native_claim_allowed"] and temporal_public_claim_allowed
    if temporal_public_claim_allowed:
        claim_state = "claim_ready"
    elif supporting_allowed:
        claim_state = "supporting_only"
    else:
        claim_state = "blocked"
    allowed_claims = []
    if supporting_allowed:
        allowed_claims.append("ordered_time_window_scorecard")
    if temporal_public_claim_allowed:
        allowed_claims.append("guarded_temporal_benchmark_claim")
    if sequence_native_claim_allowed:
        allowed_claims.append("sequence_native_model_claim")
    return {
        "schema_version": AML_TEMPORAL_BENCHMARK_CLAIM_REPORT_SCHEMA_VERSION,
        "generated_at": generated_at,
        "status": claim_state,
        "claim_state": claim_state,
        "temporal_public_claim_allowed": temporal_public_claim_allowed,
        "supporting_temporal_evidence_allowed": supporting_allowed,
        "sequence_native_claim_allowed": sequence_native_claim_allowed,
        "sequence_candidate_status": sequence_state["sequence_candidate_status"],
        "timestamp_column": source["timestamp_column"],
        "window_count": time_window_scorecard.get("window_count"),
        "zero_positive_future_fold_count": time_window_scorecard.get("zero_positive_future_fold_count"),
        "delayed_label_evidence_state": delayed_label_eval_report.get("delayed_label_evidence_state"),
        "pu_risk_state": positive_unlabeled_posture.get("pu_risk_state"),
        "threshold_drift_state": threshold_drift_report.get("threshold_drift_state"),
        "claim_blockers": blockers,
        "sequence_claim_blockers": sequence_state["sequence_claim_blockers"],
        "allowed_claims": allowed_claims,
        "required_fixes": [_required_fix_for_blocker(item) for item in blockers],
        "recommended_next_action": _recommended_next_action(
            blockers=blockers,
            threshold_drift_report=threshold_drift_report,
            delayed_label_eval_report=delayed_label_eval_report,
        ),
        "claim_boundaries": [
            "Time-window scorecards are not raw rows and may support diagnosis before public claims are ready.",
            "Delayed-label AML workloads need matured outcome evidence before paper-grade temporal claims.",
            "Proxy alert labels require positive-unlabeled posture unless confirmed outcomes are available.",
            "Sequence-native claims remain shadow-only until they beat strong lagged baselines under the same contract.",
        ],
        "summary": (
            "Relaytic-AML allows guarded temporal public claims for this workload."
            if temporal_public_claim_allowed
            else "Relaytic-AML keeps temporal claims supporting-only or blocked until weak-label, delayed-outcome, split, and drift gates are resolved."
        ),
        "trace": _trace(
            [
                "aml_delayed_label_eval_report",
                "aml_positive_unlabeled_posture",
                "aml_threshold_drift_report",
                "aml_time_window_scorecard",
            ]
        ),
    }


def _source_view(
    *,
    stream_risk_bundle: dict[str, Any],
    temporal_bundle: dict[str, Any],
    task_contract_bundle: dict[str, Any],
    operating_point_bundle: dict[str, Any],
    benchmark_bundle: dict[str, Any],
) -> dict[str, Any]:
    stream_risk_posture = _as_dict(stream_risk_bundle.get("stream_risk_posture"))
    weak_label_posture = _as_dict(stream_risk_bundle.get("weak_label_posture"))
    delayed_outcome_alignment = _as_dict(stream_risk_bundle.get("delayed_outcome_alignment"))
    drift_recalibration_trigger = _as_dict(stream_risk_bundle.get("drift_recalibration_trigger"))
    rolling_alert_quality_report = _as_dict(stream_risk_bundle.get("rolling_alert_quality_report"))
    temporal_structure_report = _as_dict(temporal_bundle.get("temporal_structure_report"))
    temporal_split_guard_report = _as_dict(temporal_bundle.get("temporal_split_guard_report"))
    rolling_cv_plan = _as_dict(temporal_bundle.get("rolling_cv_plan"))
    sequence_shadow_scorecard = _as_dict(temporal_bundle.get("sequence_shadow_scorecard"))
    temporal_baseline_ladder = _as_dict(temporal_bundle.get("temporal_baseline_ladder"))
    benchmark_truth_precheck = _as_dict(task_contract_bundle.get("benchmark_truth_precheck"))
    aml_domain_contract = _as_dict(task_contract_bundle.get("aml_domain_contract"))
    task_profile_contract = _as_dict(task_contract_bundle.get("task_profile_contract"))
    operating_point_contract = _as_dict(operating_point_bundle.get("operating_point_contract"))
    threshold_search_report = _as_dict(operating_point_bundle.get("threshold_search_report"))
    dataset_leakage_audit = _as_dict(benchmark_bundle.get("dataset_leakage_audit"))
    stream_status = _clean_text(stream_risk_posture.get("status"))
    aml_active = bool(aml_domain_contract.get("aml_active")) or stream_status in _ACTIVE_STATUSES
    timestamp_column = (
        _clean_text(stream_risk_posture.get("timestamp_column"))
        or _clean_text(rolling_alert_quality_report.get("timestamp_column"))
        or _clean_text(temporal_structure_report.get("timestamp_column"))
        or _clean_text(task_profile_contract.get("timestamp_column"))
    )
    target_column = (
        _clean_text(stream_risk_posture.get("target_column"))
        or _clean_text(rolling_alert_quality_report.get("target_column"))
        or _clean_text(task_profile_contract.get("target_column"))
    )
    rows = rolling_alert_quality_report.get("rows", [])
    return {
        "aml_active": aml_active,
        "stream_risk_posture": stream_risk_posture,
        "weak_label_posture": weak_label_posture,
        "delayed_outcome_alignment": delayed_outcome_alignment,
        "drift_recalibration_trigger": drift_recalibration_trigger,
        "rolling_report": rolling_alert_quality_report,
        "rolling_rows": rows if isinstance(rows, list) else [],
        "temporal_structure_report": temporal_structure_report,
        "temporal_split_guard_report": temporal_split_guard_report,
        "rolling_cv_plan": rolling_cv_plan,
        "sequence_shadow_scorecard": sequence_shadow_scorecard,
        "temporal_baseline_ladder": temporal_baseline_ladder,
        "benchmark_truth_precheck": benchmark_truth_precheck,
        "dataset_leakage_audit": dataset_leakage_audit,
        "operating_point_contract": operating_point_contract,
        "threshold_search_report": threshold_search_report,
        "timestamp_column": timestamp_column,
        "target_column": target_column,
        "label_kind": _clean_text(weak_label_posture.get("label_kind")) or "unknown_label_kind",
        "weak_label_risk_level": _clean_text(weak_label_posture.get("weak_label_risk_level")) or "unknown",
        "delayed_confirmation_likely": bool(
            weak_label_posture.get("delayed_confirmation_likely")
            or delayed_outcome_alignment.get("delayed_confirmation_likely")
            or stream_risk_posture.get("delayed_confirmation_likely")
        ),
        "expected_feedback_latency": _clean_text(delayed_outcome_alignment.get("expected_feedback_latency")) or "unknown",
        "delayed_alignment_state": _clean_text(delayed_outcome_alignment.get("alignment_state")) or "unknown",
    }


def _inactive_aml_temporal_artifacts(*, generated_at: str, summary: str) -> dict[str, dict[str, Any]]:
    base = {
        "generated_at": generated_at,
        "status": "not_applicable",
        "summary": summary,
        "trace": _trace(["aml_domain_contract"]),
    }
    return {
        "aml_delayed_label_eval_report": {
            "schema_version": AML_DELAYED_LABEL_EVAL_REPORT_SCHEMA_VERSION,
            **base,
            "claim_blockers": ["aml_domain_not_active"],
            "required_data_recommendations": [],
        },
        "aml_positive_unlabeled_posture": {
            "schema_version": AML_POSITIVE_UNLABELED_POSTURE_SCHEMA_VERSION,
            **base,
            "pu_risk_state": "not_applicable",
            "assume_unlabeled_are_negative_allowed": None,
            "public_claim_blockers": ["aml_domain_not_active"],
        },
        "aml_threshold_drift_report": {
            "schema_version": AML_THRESHOLD_DRIFT_REPORT_SCHEMA_VERSION,
            **base,
            "threshold_drift_state": "not_applicable",
            "threshold_reset_recommended": False,
            "recommended_action": None,
        },
        "aml_time_window_scorecard": {
            "schema_version": AML_TIME_WINDOW_SCORECARD_SCHEMA_VERSION,
            **base,
            "window_count": 0,
            "rows": [],
            "zero_positive_future_fold_count": 0,
        },
        "aml_temporal_benchmark_claim_report": {
            "schema_version": AML_TEMPORAL_BENCHMARK_CLAIM_REPORT_SCHEMA_VERSION,
            **base,
            "claim_state": "not_applicable",
            "temporal_public_claim_allowed": False,
            "supporting_temporal_evidence_allowed": False,
            "sequence_native_claim_allowed": False,
            "claim_blockers": ["aml_domain_not_active"],
            "allowed_claims": [],
        },
    }


def _resolve_matured_outcome_window_count(*, source: dict[str, Any], delayed_required: bool) -> int:
    alignment = source["delayed_outcome_alignment"]
    for key in (
        "matured_outcome_window_count",
        "confirmed_outcome_window_count",
        "observed_delayed_window_count",
        "label_maturity_window_count",
    ):
        value = _safe_int(alignment.get(key))
        if value > 0:
            return value
    if not delayed_required:
        return _safe_int(source["rolling_report"].get("window_count"))
    return 0


def _sequence_candidate_state(*, source: dict[str, Any]) -> dict[str, Any]:
    scorecard = source["sequence_shadow_scorecard"]
    rows = scorecard.get("rows", []) if isinstance(scorecard.get("rows"), list) else []
    baseline_ladder = source["temporal_baseline_ladder"]
    lagged_beats_ordinary = bool(baseline_ladder.get("lagged_beats_ordinary"))
    promotion_ready = False
    for item in rows:
        if not isinstance(item, dict):
            continue
        state = _clean_text(item.get("promotion_state")) or _clean_text(item.get("sequence_candidate_status"))
        if state == "promotion_ready":
            promotion_ready = True
            break
    sequence_present = bool(rows)
    sequence_allowed = sequence_present and promotion_ready and lagged_beats_ordinary
    blockers = []
    if sequence_present and not promotion_ready:
        blockers.append("sequence_candidate_shadow_only")
    if sequence_present and not lagged_beats_ordinary:
        blockers.append("lagged_baseline_not_beaten")
    return {
        "sequence_candidate_status": (
            "promotion_ready" if sequence_allowed else ("shadow_only" if sequence_present else "not_present")
        ),
        "sequence_native_claim_allowed": sequence_allowed,
        "sequence_claim_blockers": blockers,
    }


def _recommended_next_action(
    *,
    blockers: list[str],
    threshold_drift_report: dict[str, Any],
    delayed_label_eval_report: dict[str, Any],
) -> str:
    if "threshold_drift_requires_recalibration" in blockers:
        return _clean_text(threshold_drift_report.get("recommended_action")) or "run_recalibration_pass"
    if "delayed_label_maturity_unproven" in blockers:
        return "observe_more_delayed_outcomes"
    if "zero_positive_future_fold" in blockers:
        return "rebuild_temporal_folds_with_future_positive_coverage"
    if "positive_unlabeled_truth_unresolved" in blockers:
        return "collect_confirmed_outcome_labels_or_use_pu_evaluation"
    if delayed_label_eval_report.get("status") == "active":
        return "run_guarded_temporal_benchmark"
    return "inspect_temporal_scorecard"


def _required_fix_for_blocker(code: str) -> str:
    mapping = {
        "missing_timestamp": "provide or infer an ordered timestamp/event index",
        "insufficient_time_windows": "materialize at least three ordered evaluation windows",
        "delayed_label_maturity_unproven": "wait for or import matured delayed outcomes",
        "zero_positive_future_fold": "resplit or collect data so future folds contain positives",
        "positive_unlabeled_truth_unresolved": "use PU-aware evaluation or confirmed outcome labels",
        "future_leakage_or_split_guard_blocked": "repair temporal split leakage before claims",
        "benchmark_truth_precheck_blocked": "repair benchmark truth precheck blockers",
        "dataset_leakage_audit_blocked": "remove benchmark identity leakage",
        "threshold_drift_requires_recalibration": "run recalibration or threshold reset before production temporal claims",
    }
    return mapping.get(code, f"resolve `{code}`")


def _read_payloads(root: Path, mapping: dict[str, str]) -> dict[str, Any]:
    payload: dict[str, Any] = {}
    for key, filename in mapping.items():
        value = _read_json(root / filename)
        if value:
            payload[key] = value
    return payload


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return dict(value) if isinstance(value, dict) else {}


def _as_dict(value: Any) -> dict[str, Any]:
    return dict(value) if isinstance(value, dict) else {}


def _trace(evidence: list[str]) -> dict[str, Any]:
    return {
        "agent": "aml_temporal",
        "operating_mode": "deterministic_temporal_weak_label_upgrade",
        "llm_used": False,
        "llm_status": "not_requested",
        "deterministic_evidence": evidence,
        "advisory_notes": [],
    }


def _clean_text(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text or text.lower() in {"none", "null"}:
        return None
    return text


def _safe_float(value: Any) -> float:
    try:
        if value is None or value == "":
            return 0.0
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _safe_int(value: Any) -> int:
    try:
        if value is None or value == "":
            return 0
        return int(float(value))
    except (TypeError, ValueError):
        return 0


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()
