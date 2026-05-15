"""Business-value and analyst-capacity artifacts for Relaytic-AML."""

from __future__ import annotations

from datetime import datetime, timezone
import json
import math
from pathlib import Path
from typing import Any

from relaytic.core.json_utils import write_json


AML_BUSINESS_VALUE_REPORT_SCHEMA_VERSION = "relaytic.aml_business_value_report.v1"
ANALYST_HOUR_SAVINGS_REPORT_SCHEMA_VERSION = "relaytic.analyst_hour_savings_report.v1"
REVIEW_CAPACITY_METRIC_REPORT_SCHEMA_VERSION = "relaytic.review_capacity_metric_report.v1"
OPERATIONAL_METRIC_GUARD_SCHEMA_VERSION = "relaytic.operational_metric_guard.v1"

CONSERVATIVE_ANALYST_HOURS_PER_CASE = 1.0
MIN_CASE_PACKET_COMPLETENESS_FOR_CLAIM = 0.75

AML_BUSINESS_VALUE_FILENAMES = {
    "aml_business_value_report": "aml_business_value_report.json",
    "analyst_hour_savings_report": "analyst_hour_savings_report.json",
    "review_capacity_metric_report": "review_capacity_metric_report.json",
    "operational_metric_guard": "operational_metric_guard.json",
}


def sync_aml_business_value_artifacts(run_dir: str | Path) -> dict[str, Path]:
    """Build and write deterministic 15T business-value artifacts for an AML run."""
    root = Path(run_dir)
    artifacts = build_aml_business_value_artifacts(run_dir=root)
    root.mkdir(parents=True, exist_ok=True)
    return {
        key: write_json(
            root / filename,
            artifacts[key],
            indent=2,
            ensure_ascii=False,
            sort_keys=True,
        )
        for key, filename in AML_BUSINESS_VALUE_FILENAMES.items()
    }


def read_aml_business_value_artifacts(run_dir: str | Path) -> dict[str, Any]:
    """Read AML business-value artifacts if present."""
    root = Path(run_dir)
    payload: dict[str, Any] = {}
    for key, filename in AML_BUSINESS_VALUE_FILENAMES.items():
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


def build_aml_business_value_artifacts(run_dir: str | Path) -> dict[str, dict[str, Any]]:
    """Construct business-value artifacts from queue, casework, operating-point, and benchmark evidence."""
    root = Path(run_dir)
    generated_at = _utc_now()
    payloads = _read_source_payloads(root)

    review_capacity = _build_review_capacity_metric_report(
        generated_at=generated_at,
        run_dir=root,
        payloads=payloads,
    )
    analyst_hours = _build_analyst_hour_savings_report(
        generated_at=generated_at,
        run_dir=root,
        payloads=payloads,
        review_capacity=review_capacity,
    )
    guard = _build_operational_metric_guard(
        generated_at=generated_at,
        run_dir=root,
        payloads=payloads,
        review_capacity=review_capacity,
        analyst_hours=analyst_hours,
    )
    business_value = _build_business_value_report(
        generated_at=generated_at,
        run_dir=root,
        payloads=payloads,
        review_capacity=review_capacity,
        analyst_hours=analyst_hours,
        guard=guard,
    )
    return {
        "aml_business_value_report": business_value,
        "analyst_hour_savings_report": analyst_hours,
        "review_capacity_metric_report": review_capacity,
        "operational_metric_guard": guard,
    }


def render_aml_business_value_markdown(bundle: dict[str, Any]) -> str:
    """Render a short human-facing summary of AML business-value posture."""
    report = _as_dict(bundle.get("aml_business_value_report"))
    hours = _as_dict(bundle.get("analyst_hour_savings_report"))
    capacity = _as_dict(bundle.get("review_capacity_metric_report"))
    guard = _as_dict(bundle.get("operational_metric_guard"))
    safe_claims = [
        str(item)
        for item in guard.get("safe_operational_claims", [])
        if str(item).strip()
    ]
    blocked = [
        str(item)
        for item in guard.get("blocked_reason_codes", [])
        if str(item).strip()
    ]
    return "\n".join(
        [
            "# Relaytic-AML Business Value",
            "",
            f"- Status: `{report.get('status') or 'unknown'}`",
            f"- Operational guard: `{guard.get('operational_utility_state') or guard.get('status') or 'unknown'}`",
            f"- Hard business-value claim allowed: `{guard.get('hard_business_value_claim_allowed')}`",
            f"- Analyst-hours saved at fixed recall: `{hours.get('analyst_hours_saved_at_fixed_recall')}`",
            f"- False-positive reduction at fixed recall: `{hours.get('false_positive_reduction_at_fixed_recall')}`",
            f"- Recall at review capacity: `{capacity.get('recall_at_review_capacity')}`",
            f"- Precision at top-k: `{capacity.get('precision_at_top_k')}`",
            f"- Case-packet completeness: `{capacity.get('case_packet_completeness')}`",
            f"- Incumbent tradeoff: `{dict(report.get('incumbent_tradeoff', {})).get('tradeoff_summary') or 'none'}`",
            "",
            "## Safe Operational Claims",
            *(f"- {item}" for item in safe_claims[:5]),
            *(["- none"] if not safe_claims else []),
            "",
            "## Blocking Reasons",
            *(f"- `{item}`" for item in blocked[:8]),
            *(["- none"] if not blocked else []),
            "",
        ]
    )


def _build_review_capacity_metric_report(
    *,
    generated_at: str,
    run_dir: Path,
    payloads: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    alert_queue = payloads["alert_queue_rankings"]
    alert_policy = payloads["alert_queue_policy"]
    case_packet = payloads["case_packet"]
    sensitivity = payloads["review_capacity_sensitivity"]
    rows = _queue_rows(alert_queue)
    total_cases = len(rows)
    capacity = _resolve_capacity(alert_policy=alert_policy, alert_queue=alert_queue, total_cases=total_cases)
    top_rows = rows[:capacity]
    selected_expected_true = _sum_expected_true(top_rows)
    total_expected_true = _sum_expected_true(rows)
    selected_false_positives = max(0.0, float(capacity) - selected_expected_true)
    analyst_hours_per_case, analyst_defaulted = _resolve_analyst_hours(payloads["analyst_review_scorecard"])
    review_hours = round(float(capacity) * analyst_hours_per_case, 4)
    case_packet_completeness, completeness_fields = _case_packet_completeness(case_packet)
    precision = selected_expected_true / float(capacity) if capacity > 0 else None
    recall = selected_expected_true / total_expected_true if total_expected_true > 0 else None
    fp_per_hour = selected_false_positives / review_hours if review_hours > 0 else None
    scenarios = _capacity_scenarios(
        queue_rows=rows,
        sensitivity=sensitivity,
        selected_capacity=capacity,
        analyst_hours_per_case=analyst_hours_per_case,
    )
    evidence_quality = "explicit_expected_positive_rates" if _has_expected_positive_rates(rows) else "missing_positive_rates"
    status = "active" if rows and capacity > 0 else "not_available"
    return {
        "schema_version": REVIEW_CAPACITY_METRIC_REPORT_SCHEMA_VERSION,
        "generated_at": generated_at,
        "status": status,
        "run_dir": str(run_dir),
        "queue_count": total_cases,
        "review_capacity_cases": capacity,
        "review_capacity_fraction": round(float(capacity) / float(total_cases), 6) if total_cases else None,
        "expected_positive_count": _round_metric(total_expected_true),
        "expected_true_positives_at_capacity": _round_metric(selected_expected_true),
        "expected_false_positives_at_capacity": _round_metric(selected_false_positives),
        "precision_at_top_k": _round_metric(precision),
        "recall_at_review_capacity": _round_metric(recall),
        "false_positives_per_analyst_hour": _round_metric(fp_per_hour),
        "analyst_hours_at_capacity": _round_metric(review_hours),
        "analyst_hours_per_case": analyst_hours_per_case,
        "analyst_hours_assumption_defaulted": analyst_defaulted,
        "case_packet_completeness": _round_metric(case_packet_completeness),
        "case_packet_completeness_fields": completeness_fields,
        "evidence_quality": evidence_quality,
        "scenarios": scenarios,
        "summary": (
            f"Relaytic-AML expects recall `{_round_metric(recall)}` and precision@{capacity} "
            f"`{_round_metric(precision)}` for the selected review queue."
            if status == "active"
            else "Relaytic-AML could not calculate review-capacity metrics because no active alert queue was available."
        ),
    }


def _build_analyst_hour_savings_report(
    *,
    generated_at: str,
    run_dir: Path,
    payloads: dict[str, dict[str, Any]],
    review_capacity: dict[str, Any],
) -> dict[str, Any]:
    alert_queue = payloads["alert_queue_rankings"]
    rows = _queue_rows(alert_queue)
    analyst_hours_per_case = _safe_float(review_capacity.get("analyst_hours_per_case"), CONSERVATIVE_ANALYST_HOURS_PER_CASE)
    capacity = int(review_capacity.get("review_capacity_cases", 0) or 0)
    selected_expected_true = _safe_float(review_capacity.get("expected_true_positives_at_capacity"), 0.0)
    selected_false_positives = _safe_float(review_capacity.get("expected_false_positives_at_capacity"), 0.0)
    total_expected_true = _safe_float(review_capacity.get("expected_positive_count"), 0.0)
    queue_count = int(review_capacity.get("queue_count", 0) or 0)
    prevalence = total_expected_true / float(queue_count) if queue_count > 0 else 0.0
    baseline_cases = min(queue_count, math.ceil(selected_expected_true / prevalence)) if prevalence > 0.0 and selected_expected_true > 0.0 else None
    baseline_expected_false_positives = (
        max(0.0, float(baseline_cases) - selected_expected_true)
        if baseline_cases is not None
        else None
    )
    false_positive_reduction = (
        baseline_expected_false_positives - selected_false_positives
        if baseline_expected_false_positives is not None
        else None
    )
    false_positive_reduction_fraction = (
        false_positive_reduction / baseline_expected_false_positives
        if baseline_expected_false_positives and baseline_expected_false_positives > 0.0 and false_positive_reduction is not None
        else None
    )
    baseline_hours = float(baseline_cases) * analyst_hours_per_case if baseline_cases is not None else None
    selected_hours = float(capacity) * analyst_hours_per_case if capacity > 0 else None
    analyst_hours_saved = (
        baseline_hours - selected_hours
        if baseline_hours is not None and selected_hours is not None
        else None
    )
    status = "active" if rows and capacity > 0 and baseline_cases is not None else "not_available"
    return {
        "schema_version": ANALYST_HOUR_SAVINGS_REPORT_SCHEMA_VERSION,
        "generated_at": generated_at,
        "status": status,
        "run_dir": str(run_dir),
        "baseline_kind": "prevalence_matched_ungoverned_review",
        "baseline_review_cases_for_fixed_recall": baseline_cases,
        "selected_review_capacity_cases": capacity,
        "baseline_review_hours_for_fixed_recall": _round_metric(baseline_hours),
        "selected_review_hours": _round_metric(selected_hours),
        "analyst_hours_per_case": analyst_hours_per_case,
        "analyst_hours_assumption_defaulted": bool(review_capacity.get("analyst_hours_assumption_defaulted")),
        "analyst_hours_saved_at_fixed_recall": _round_metric(analyst_hours_saved),
        "selected_expected_false_positives": _round_metric(selected_false_positives),
        "baseline_expected_false_positives": _round_metric(baseline_expected_false_positives),
        "false_positive_reduction_at_fixed_recall": _round_metric(false_positive_reduction),
        "false_positive_reduction_fraction_at_fixed_recall": _round_metric(false_positive_reduction_fraction),
        "claim_basis": "expected_positive_rates_from_casework",
        "assumptions": _assumptions(
            analyst_hours_per_case=analyst_hours_per_case,
            analyst_defaulted=bool(review_capacity.get("analyst_hours_assumption_defaulted")),
        ),
        "summary": (
            f"Relaytic-AML estimates `{_round_metric(analyst_hours_saved)}` analyst hour(s) saved at fixed recall "
            f"against a prevalence-matched ungoverned review baseline."
            if status == "active"
            else "Relaytic-AML could not estimate analyst-hour savings because queue prevalence or capacity evidence was missing."
        ),
    }


def _build_operational_metric_guard(
    *,
    generated_at: str,
    run_dir: Path,
    payloads: dict[str, dict[str, Any]],
    review_capacity: dict[str, Any],
    analyst_hours: dict[str, Any],
) -> dict[str, Any]:
    model_score_posture = _model_score_posture(payloads)
    precision = _safe_optional_float(review_capacity.get("precision_at_top_k"))
    recall = _safe_optional_float(review_capacity.get("recall_at_review_capacity"))
    false_positive_reduction = _safe_optional_float(analyst_hours.get("false_positive_reduction_at_fixed_recall"))
    analyst_hours_saved = _safe_optional_float(analyst_hours.get("analyst_hours_saved_at_fixed_recall"))
    case_completeness = _safe_optional_float(review_capacity.get("case_packet_completeness"))
    capacity_status = _clean_text(review_capacity.get("status"))
    evidence_quality = _clean_text(review_capacity.get("evidence_quality"))

    reason_codes: list[str] = []
    if capacity_status != "active":
        reason_codes.append("review_capacity_metrics_missing")
    if evidence_quality != "explicit_expected_positive_rates":
        reason_codes.append("expected_positive_rate_missing")
    if bool(review_capacity.get("analyst_hours_assumption_defaulted")):
        reason_codes.append("analyst_hour_assumption_defaulted")
    if case_completeness is None or case_completeness < MIN_CASE_PACKET_COMPLETENESS_FOR_CLAIM:
        reason_codes.append("case_packet_incomplete")
    if false_positive_reduction is None or false_positive_reduction <= 0.0:
        reason_codes.append("false_positive_reduction_not_positive")
    if analyst_hours_saved is None or analyst_hours_saved <= 0.0:
        reason_codes.append("analyst_hours_saved_not_positive")
    if precision is None or recall is None:
        reason_codes.append("precision_or_recall_missing")
    incumbent_tradeoff = _incumbent_tradeoff(payloads=payloads, review_capacity=review_capacity, analyst_hours=analyst_hours)
    if incumbent_tradeoff["incumbent_present"] and incumbent_tradeoff["operational_comparison_scope"] != "same_queue_evidence":
        reason_codes.append("incumbent_queue_operational_evidence_missing")

    model_operational_disagreement = (
        model_score_posture["score_state"] in {"meets_or_exceeds_reference", "beats_incumbent", "model_score_improved"}
        and bool(reason_codes)
    )
    if model_operational_disagreement:
        reason_codes.append("model_score_operational_utility_disagree")
    reason_codes = _dedupe(reason_codes)
    hard_claim_allowed = not reason_codes
    state = "passed" if hard_claim_allowed else ("not_applicable" if capacity_status != "active" else "blocked")
    safe_claims = []
    if capacity_status == "active":
        safe_claims.append("review_capacity_metrics_reported")
    if precision is not None and recall is not None:
        safe_claims.append("precision_and_recall_at_review_capacity_reported")
    if false_positive_reduction is not None:
        safe_claims.append("false_positive_reduction_estimated_with_claim_guard")
    return {
        "schema_version": OPERATIONAL_METRIC_GUARD_SCHEMA_VERSION,
        "generated_at": generated_at,
        "status": state,
        "run_dir": str(run_dir),
        "operational_utility_state": state,
        "hard_business_value_claim_allowed": hard_claim_allowed,
        "model_score_posture": model_score_posture,
        "incumbent_tradeoff": incumbent_tradeoff,
        "model_operational_disagreement": model_operational_disagreement,
        "blocked_reason_codes": reason_codes,
        "safe_operational_claims": safe_claims,
        "guard_thresholds": {
            "min_case_packet_completeness_for_claim": MIN_CASE_PACKET_COMPLETENESS_FOR_CLAIM,
            "requires_positive_false_positive_reduction": True,
            "requires_positive_analyst_hours_saved": True,
            "blocks_when_analyst_hour_assumptions_default": True,
            "requires_incumbent_queue_evidence_for_incumbent_utility_claim": True,
        },
        "summary": (
            "Relaytic-AML permits hard business-value claims for this run."
            if hard_claim_allowed
            else (
                "Relaytic-AML blocks hard business-value claims because model-score posture and operational utility evidence disagree."
                if model_operational_disagreement
                else "Relaytic-AML reports operational metrics but blocks hard business-value claims until the guard reasons are resolved."
            )
        ),
    }


def _build_business_value_report(
    *,
    generated_at: str,
    run_dir: Path,
    payloads: dict[str, dict[str, Any]],
    review_capacity: dict[str, Any],
    analyst_hours: dict[str, Any],
    guard: dict[str, Any],
) -> dict[str, Any]:
    incumbent_tradeoff = dict(guard.get("incumbent_tradeoff", {}))
    status = "ready" if review_capacity.get("status") == "active" else "partial"
    if guard.get("operational_utility_state") == "blocked":
        status = "guarded"
    return {
        "schema_version": AML_BUSINESS_VALUE_REPORT_SCHEMA_VERSION,
        "generated_at": generated_at,
        "status": status,
        "run_dir": str(run_dir),
        "business_value_ready": guard.get("hard_business_value_claim_allowed"),
        "hard_business_value_claim_allowed": guard.get("hard_business_value_claim_allowed"),
        "model_operational_disagreement": guard.get("model_operational_disagreement"),
        "model_score_posture": guard.get("model_score_posture"),
        "operational_guard_status": guard.get("operational_utility_state"),
        "review_capacity_metrics": {
            "queue_count": review_capacity.get("queue_count"),
            "review_capacity_cases": review_capacity.get("review_capacity_cases"),
            "precision_at_top_k": review_capacity.get("precision_at_top_k"),
            "recall_at_review_capacity": review_capacity.get("recall_at_review_capacity"),
            "false_positives_per_analyst_hour": review_capacity.get("false_positives_per_analyst_hour"),
            "case_packet_completeness": review_capacity.get("case_packet_completeness"),
        },
        "analyst_hour_metrics": {
            "analyst_hours_saved_at_fixed_recall": analyst_hours.get("analyst_hours_saved_at_fixed_recall"),
            "false_positive_reduction_at_fixed_recall": analyst_hours.get("false_positive_reduction_at_fixed_recall"),
            "false_positive_reduction_fraction_at_fixed_recall": analyst_hours.get("false_positive_reduction_fraction_at_fixed_recall"),
            "analyst_hours_assumption_defaulted": analyst_hours.get("analyst_hours_assumption_defaulted"),
        },
        "incumbent_tradeoff": incumbent_tradeoff,
        "claim_boundary": (
            "Business-value metrics are operational evidence, not public ROI claims. Hard business-value claims require "
            "positive analyst-hour and false-positive reduction, complete case-packet evidence, explicit analyst assumptions, "
            "and same-queue incumbent evidence when an incumbent is cited."
        ),
        "blocked_reason_codes": list(guard.get("blocked_reason_codes", []))
        if isinstance(guard.get("blocked_reason_codes"), list)
        else [],
        "required_artifacts": list(AML_BUSINESS_VALUE_FILENAMES.values()),
        "evidence_refs": [
            "alert_queue_rankings.json",
            "analyst_review_scorecard.json",
            "case_packet.json",
            "review_capacity_sensitivity.json",
            "operating_point_contract.json",
            "benchmark_parity_report.json",
            "incumbent_parity_report.json",
            "external_challenger_evaluation.json",
        ],
        "summary": (
            "Relaytic-AML business-value evidence is ready for hard operational claims."
            if guard.get("hard_business_value_claim_allowed")
            else "Relaytic-AML separates reported operational metrics from hard business-value claims until the operational guard passes."
        ),
    }


def _read_source_payloads(root: Path) -> dict[str, dict[str, Any]]:
    return {
        "alert_queue_policy": _read_json(root / "alert_queue_policy.json"),
        "alert_queue_rankings": _read_json(root / "alert_queue_rankings.json"),
        "analyst_review_scorecard": _read_json(root / "analyst_review_scorecard.json"),
        "case_packet": _read_json(root / "case_packet.json"),
        "review_capacity_sensitivity": _read_json(root / "review_capacity_sensitivity.json"),
        "operating_point_contract": _read_json(root / "operating_point_contract.json"),
        "benchmark_parity_report": _read_json(root / "benchmark_parity_report.json"),
        "benchmark_gap_report": _read_json(root / "benchmark_gap_report.json"),
        "reference_approach_matrix": _read_json(root / "reference_approach_matrix.json"),
        "incumbent_parity_report": _read_json(root / "incumbent_parity_report.json"),
        "external_challenger_evaluation": _read_json(root / "external_challenger_evaluation.json"),
        "external_challenger_manifest": _read_json(root / "external_challenger_manifest.json"),
    }


def _queue_rows(alert_queue: dict[str, Any]) -> list[dict[str, Any]]:
    rows = alert_queue.get("ranking")
    if not isinstance(rows, list):
        return []
    clean_rows = [dict(item) for item in rows if isinstance(item, dict)]
    return sorted(clean_rows, key=_row_rank)


def _resolve_capacity(*, alert_policy: dict[str, Any], alert_queue: dict[str, Any], total_cases: int) -> int:
    for value in (
        alert_policy.get("review_capacity_cases"),
        alert_queue.get("review_capacity_cases"),
    ):
        try:
            capacity = int(value)
        except (TypeError, ValueError):
            continue
        if capacity > 0:
            return min(total_cases, capacity) if total_cases > 0 else capacity
    return min(total_cases, max(1, math.ceil(total_cases * 0.15))) if total_cases > 0 else 0


def _capacity_scenarios(
    *,
    queue_rows: list[dict[str, Any]],
    sensitivity: dict[str, Any],
    selected_capacity: int,
    analyst_hours_per_case: float,
) -> list[dict[str, Any]]:
    raw_rows = sensitivity.get("rows")
    capacities: set[int] = {selected_capacity} if selected_capacity > 0 else set()
    if isinstance(raw_rows, list):
        for item in raw_rows:
            if not isinstance(item, dict):
                continue
            capacity = item.get("review_capacity_cases")
            try:
                resolved = int(capacity)
            except (TypeError, ValueError):
                continue
            if resolved > 0:
                capacities.add(min(len(queue_rows), resolved))
    if not capacities and queue_rows:
        capacities = {max(1, math.ceil(len(queue_rows) * fraction)) for fraction in (0.05, 0.1, 0.2)}
    total_expected_true = _sum_expected_true(queue_rows)
    rows: list[dict[str, Any]] = []
    for capacity in sorted(capacities):
        top_rows = queue_rows[:capacity]
        expected_true = _sum_expected_true(top_rows)
        false_positives = max(0.0, float(capacity) - expected_true)
        hours = float(capacity) * analyst_hours_per_case
        rows.append(
            {
                "review_capacity_cases": capacity,
                "review_capacity_fraction": _round_metric(float(capacity) / float(len(queue_rows))) if queue_rows else None,
                "expected_true_positives": _round_metric(expected_true),
                "expected_false_positives": _round_metric(false_positives),
                "precision_at_k": _round_metric(expected_true / float(capacity)) if capacity > 0 else None,
                "recall_at_capacity": _round_metric(expected_true / total_expected_true) if total_expected_true > 0 else None,
                "analyst_hours": _round_metric(hours),
                "false_positives_per_analyst_hour": _round_metric(false_positives / hours) if hours > 0 else None,
                "top_case_ids": [str(row.get("case_id")) for row in top_rows[:3] if str(row.get("case_id", "")).strip()],
            }
        )
    return rows


def _incumbent_tradeoff(
    *,
    payloads: dict[str, dict[str, Any]],
    review_capacity: dict[str, Any],
    analyst_hours: dict[str, Any],
) -> dict[str, Any]:
    incumbent = payloads["incumbent_parity_report"]
    evaluation = payloads["external_challenger_evaluation"]
    manifest = payloads["external_challenger_manifest"]
    incumbent_present = bool(incumbent.get("incumbent_present")) or _clean_text(manifest.get("incumbent_name")) is not None
    comparison_metric = _clean_text(incumbent.get("comparison_metric")) or _clean_text(evaluation.get("comparison_metric"))
    evaluation_test_metric = _as_dict(evaluation.get("test_metric"))
    relaytic_metric = _safe_optional_float(evaluation_test_metric.get("relaytic_metric_value"))
    incumbent_metric = _metric_value(evaluation_test_metric, comparison_metric)
    if relaytic_metric is None:
        relaytic_reference = dict(payloads["reference_approach_matrix"].get("relaytic_reference", {}))
        relaytic_test_metric = relaytic_reference.get("test_metric")
        if isinstance(relaytic_test_metric, dict) and comparison_metric:
            relaytic_metric = _safe_optional_float(relaytic_test_metric.get(comparison_metric))
    if incumbent_metric is None:
        incumbent_metric = _safe_optional_float(_as_dict(incumbent.get("test_metric")).get(comparison_metric))
    operational_claim_allowed = False
    if not incumbent_present:
        tradeoff_summary = "No imported incumbent is attached; Relaytic compares business value against the ungoverned review baseline only."
        scope = "no_incumbent"
    else:
        scope = "metric_only_incumbent_queue_missing"
        tradeoff_summary = (
            "An imported incumbent is present, but Relaytic has no same-queue incumbent ranking, so analyst-capacity tradeoffs are reported for Relaytic and hard incumbent utility claims are blocked."
        )
    return {
        "incumbent_present": incumbent_present,
        "incumbent_name": _clean_text(incumbent.get("incumbent_name")) or _clean_text(manifest.get("incumbent_name")),
        "comparison_metric": comparison_metric,
        "relaytic_metric_value": _round_metric(relaytic_metric),
        "incumbent_metric_value": _round_metric(incumbent_metric),
        "incumbent_parity_status": _clean_text(incumbent.get("parity_status")),
        "relaytic_beats_incumbent_on_model_metric": incumbent.get("relaytic_beats_incumbent"),
        "incumbent_stronger_on_model_metric": incumbent.get("incumbent_stronger"),
        "operational_comparison_scope": scope,
        "operational_claim_allowed": operational_claim_allowed,
        "analyst_capacity_tradeoff": {
            "relaytic_review_capacity_cases": review_capacity.get("review_capacity_cases"),
            "relaytic_precision_at_top_k": review_capacity.get("precision_at_top_k"),
            "relaytic_recall_at_review_capacity": review_capacity.get("recall_at_review_capacity"),
            "relaytic_analyst_hours_saved_at_fixed_recall": analyst_hours.get("analyst_hours_saved_at_fixed_recall"),
            "incumbent_review_capacity_cases": None,
            "incumbent_precision_at_top_k": None,
            "incumbent_recall_at_review_capacity": None,
        },
        "tradeoff_summary": tradeoff_summary,
    }


def _model_score_posture(payloads: dict[str, dict[str, Any]]) -> dict[str, Any]:
    parity = payloads["benchmark_parity_report"]
    gap = payloads["benchmark_gap_report"]
    incumbent = payloads["incumbent_parity_report"]
    score_state = _clean_text(parity.get("parity_status")) or "unknown"
    if bool(incumbent.get("relaytic_beats_incumbent")):
        score_state = "beats_incumbent"
    elif bool(gap.get("relaytic_beats_best_reference")):
        score_state = "meets_or_exceeds_reference"
    return {
        "score_state": score_state,
        "comparison_metric": _clean_text(parity.get("comparison_metric")) or _clean_text(gap.get("comparison_metric")),
        "relaytic_beats_best_reference": gap.get("relaytic_beats_best_reference"),
        "near_parity": gap.get("near_parity"),
        "relaytic_beats_incumbent": incumbent.get("relaytic_beats_incumbent"),
        "incumbent_stronger": incumbent.get("incumbent_stronger"),
        "test_gap": gap.get("test_gap") if "test_gap" in gap else incumbent.get("test_gap"),
    }


def _case_packet_completeness(case_packet: dict[str, Any]) -> tuple[float, list[dict[str, Any]]]:
    expected = {
        "case_id": case_packet.get("case_id"),
        "focal_entity": case_packet.get("focal_entity"),
        "priority_score": case_packet.get("priority_score"),
        "review_action": case_packet.get("review_action"),
        "top_typologies": case_packet.get("top_typologies"),
        "linked_entities": case_packet.get("linked_entities"),
        "counterparty_edges": case_packet.get("counterparty_edges"),
        "analyst_questions": case_packet.get("analyst_questions"),
        "recommended_next_steps": case_packet.get("recommended_next_steps"),
        "evidence_refs": case_packet.get("evidence_refs"),
    }
    fields = [{"field": key, "present": _present(value)} for key, value in expected.items()]
    score = sum(1 for item in fields if item["present"]) / float(len(fields)) if fields else 0.0
    return score, fields


def _resolve_analyst_hours(scorecard: dict[str, Any]) -> tuple[float, bool]:
    value = _safe_optional_float(scorecard.get("analyst_hours_per_case"))
    if value is None or value <= 0.0:
        return CONSERVATIVE_ANALYST_HOURS_PER_CASE, True
    return value, False


def _assumptions(*, analyst_hours_per_case: float, analyst_defaulted: bool) -> list[dict[str, Any]]:
    source = "conservative_default" if analyst_defaulted else "analyst_review_scorecard.json"
    return [
        {
            "assumption_id": "analyst_hours_per_case",
            "value": analyst_hours_per_case,
            "source": source,
            "claim_effect": "hard business-value claims are blocked when this default is used"
            if analyst_defaulted
            else "explicit run artifact",
        },
        {
            "assumption_id": "baseline_kind",
            "value": "prevalence_matched_ungoverned_review",
            "source": "deterministic_15t_business_value_contract",
            "claim_effect": "used only for bounded analyst-hour and false-positive reduction estimates",
        },
    ]


def _sum_expected_true(rows: list[dict[str, Any]]) -> float:
    return sum(_expected_positive_rate(row) for row in rows)


def _expected_positive_rate(row: dict[str, Any]) -> float:
    for key in ("expected_positive_rate", "suspicious_rate", "positive_rate", "label_rate"):
        value = _safe_optional_float(row.get(key))
        if value is not None:
            return min(1.0, max(0.0, value))
    value = _safe_optional_float(row.get("risk_score"))
    if value is not None:
        return min(1.0, max(0.0, value))
    return 0.0


def _has_expected_positive_rates(rows: list[dict[str, Any]]) -> bool:
    if not rows:
        return False
    for row in rows:
        if not any(_safe_optional_float(row.get(key)) is not None for key in ("expected_positive_rate", "suspicious_rate", "positive_rate", "label_rate")):
            return False
    return True


def _metric_value(metric_payload: dict[str, Any], metric_name: str | None) -> float | None:
    if not metric_name:
        return None
    if metric_name in metric_payload:
        return _safe_optional_float(metric_payload.get(metric_name))
    nested = metric_payload.get("metric")
    if isinstance(nested, dict):
        return _safe_optional_float(nested.get(metric_name))
    return None


def _present(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, tuple, set, dict)):
        return bool(value)
    return True


def _safe_optional_float(value: Any) -> float | None:
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    if math.isnan(result) or math.isinf(result):
        return None
    return result


def _safe_float(value: Any, default: float) -> float:
    result = _safe_optional_float(value)
    return default if result is None else result


def _round_metric(value: Any) -> float | int | None:
    numeric = _safe_optional_float(value)
    if numeric is None:
        return None
    rounded = round(numeric, 6)
    if abs(rounded - int(rounded)) < 1e-12:
        return int(rounded)
    return rounded


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return payload if isinstance(payload, dict) else {}


def _as_dict(value: Any) -> dict[str, Any]:
    return dict(value) if isinstance(value, dict) else {}


def _row_rank(row: dict[str, Any]) -> int:
    try:
        rank = int(row.get("rank", 0) or 0)
    except (TypeError, ValueError):
        return 10**9
    return rank if rank > 0 else 10**9


def _clean_text(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text or text.lower() in {"none", "null"}:
        return None
    return text


def _dedupe(values: list[str]) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for value in values:
        text = str(value).strip()
        if not text or text in seen:
            continue
        seen.add(text)
        result.append(text)
    return result


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()
