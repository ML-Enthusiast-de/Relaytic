"""Paper Track P9 operational AML evaluation artifacts."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

from relaytic.core.json_utils import write_json


PAPER_OPERATIONAL_METRICS_SCHEMA_VERSION = "relaytic.paper_operational_metrics.v1"
PAPER_OPERATIONAL_METRICS_REPORT_DIR = Path("docs") / "reports"
PAPER_OPERATIONAL_METRICS_FILENAMES = {
    "paper_operational_metric_table": "paper_operational_metric_table.json",
    "paper_review_budget_curve": "paper_review_budget_curve.json",
    "paper_case_packet_completeness_report": "paper_case_packet_completeness_report.json",
    "paper_operational_claim_guard": "paper_operational_claim_guard.json",
}

DEFAULT_ANALYST_HOURS_PER_CASE = 1.0
CASE_PACKET_REQUIRED_FIELDS = [
    "case_id",
    "focal_entity",
    "review_action",
    "priority_score",
    "top_typologies",
    "linked_entities",
    "counterparty_edges",
    "analyst_questions",
    "recommended_next_steps",
    "evidence_refs",
]


def build_paper_operational_metrics_pack(
    project_root: str | Path,
    *,
    run_dir: str | Path | None = None,
) -> dict[str, Any]:
    """Build P9 operational metric artifacts from paper-track evidence."""
    root = Path(project_root)
    reports = root / PAPER_OPERATIONAL_METRICS_REPORT_DIR
    inputs = _collect_inputs(root=root, reports=reports, run_dir=run_dir)
    case_packet = _build_case_packet_completeness_report(inputs=inputs)
    table = _build_operational_metric_table(inputs=inputs, case_packet=case_packet)
    curve = _build_review_budget_curve(inputs=inputs, table=table)
    guard = _build_operational_claim_guard(inputs=inputs, table=table, case_packet=case_packet)
    return {
        "paper_operational_metric_table": table,
        "paper_review_budget_curve": curve,
        "paper_case_packet_completeness_report": case_packet,
        "paper_operational_claim_guard": guard,
    }


def sync_paper_operational_metrics_pack(
    project_root: str | Path,
    *,
    run_dir: str | Path | None = None,
    output_dir: str | Path | None = None,
) -> dict[str, Path]:
    """Write P9 operational metric artifacts to ``docs/reports`` by default."""
    root = Path(project_root)
    report_dir = Path(output_dir) if output_dir is not None else root / PAPER_OPERATIONAL_METRICS_REPORT_DIR
    report_dir.mkdir(parents=True, exist_ok=True)
    artifacts = build_paper_operational_metrics_pack(root, run_dir=run_dir)
    return {
        key: write_json(report_dir / filename, artifacts[key], indent=2, sort_keys=True)
        for key, filename in PAPER_OPERATIONAL_METRICS_FILENAMES.items()
    }


def render_paper_operational_metrics_markdown(pack: dict[str, Any]) -> str:
    table = dict(pack.get("paper_operational_metric_table", {}))
    guard = dict(pack.get("paper_operational_claim_guard", {}))
    case_packet = dict(pack.get("paper_case_packet_completeness_report", {}))
    return "\n".join(
        [
            "# Paper P9 Operational AML Metrics",
            "",
            f"- Status: `{table.get('status') or 'unknown'}`",
            f"- Operational rows: `{table.get('row_count') or 0}`",
            f"- Rows with review-budget metrics: `{table.get('rows_with_review_budget_metrics') or 0}`",
            f"- Case-packet completeness state: `{case_packet.get('status') or 'unknown'}`",
            f"- Hard business-value claims allowed: `{guard.get('hard_business_value_claim_allowed')}`",
            f"- Paper may continue to P10: `{guard.get('paper_can_continue_to_p10')}`",
            f"- Next slice: `{guard.get('next_slice') or table.get('next_slice') or 'unknown'}`",
        ]
    ).rstrip() + "\n"


def _collect_inputs(*, root: Path, reports: Path, run_dir: str | Path | None) -> dict[str, Any]:
    resolved_run_dir = Path(run_dir) if run_dir is not None else None
    if resolved_run_dir is not None and not resolved_run_dir.is_absolute():
        resolved_run_dir = root / resolved_run_dir
    run_artifacts = _collect_run_artifacts(root=root, run_dir=resolved_run_dir) if resolved_run_dir else {}
    return {
        "root": root,
        "run_dir": resolved_run_dir,
        "p8d_decision": _read_artifact(reports / "paper_p8d_thesis_decision.json"),
        "p8d_matrix": _read_artifact(reports / "paper_p8d_evidence_role_matrix.json"),
        "paysim_manifest": _read_artifact(reports / "paysim_competitive_benchmark_manifest.json"),
        "paysim_table": _read_artifact(reports / "paysim_competitive_baseline_table.json"),
        "paysim_gate": _read_artifact(reports / "paysim_publishability_gate.json"),
        "paysim_p4_operating": _read_artifact(reports / "paysim_operating_point_table.json"),
        "graph_table": _read_artifact(reports / "paper_graph_feature_table.json"),
        "graph_split": _read_artifact(reports / "elliptic_temporal_split_report.json"),
        "graph_gate": _read_artifact(reports / "paper_graph_publishability_gate.json"),
        "elliptic2_p8d": _read_artifact(reports / "paper_p8d_thesis_decision.json"),
        "subgraph_blocker": _read_artifact(reports / "subgraph_benchmark_blocker_report.json"),
        "run_artifacts": run_artifacts,
    }


def _build_operational_metric_table(
    *,
    inputs: dict[str, Any],
    case_packet: dict[str, Any],
) -> dict[str, Any]:
    p8d = _payload(inputs["p8d_decision"])
    p9_dependency_met = _p8d_allows_p9(p8d)
    rows: list[dict[str, Any]] = []
    if p9_dependency_met:
        rows.extend(_build_paysim_rows(inputs=inputs, case_packet=case_packet))
        rows.extend(_build_graph_rows(inputs=inputs, case_packet=case_packet))
    rows_with_review_metrics = sum(1 for row in rows if bool(row.get("review_budget_metrics_available")))
    status = (
        "operational_metrics_reported_with_claim_guard"
        if rows_with_review_metrics
        else "blocked_pending_operational_metric_inputs"
        if p9_dependency_met
        else "blocked_pending_p8d_thesis_decision"
    )
    return {
        "schema_version": PAPER_OPERATIONAL_METRICS_SCHEMA_VERSION,
        "slice": "Paper Track P9",
        "status": status,
        "p8d_dependency": {
            "artifact_ref": "docs/reports/paper_p8d_thesis_decision.json",
            "status": p8d.get("status"),
            "selected_route": p8d.get("selected_route"),
            "p9_allowed": bool(p8d.get("p9_allowed")),
            "elliptic2_performance_contribution_allowed": bool(
                p8d.get("elliptic2_performance_contribution_allowed")
            ),
        },
        "row_count": len(rows),
        "rows_with_review_budget_metrics": rows_with_review_metrics,
        "rows": rows,
        "excluded_or_context_only_tracks": _excluded_tracks(inputs),
        "assumption_policy": {
            "analyst_hours_per_case": DEFAULT_ANALYST_HOURS_PER_CASE,
            "analyst_hours_assumption_defaulted": True,
            "baseline_kind": "prevalence_matched_unranked_review",
            "hard_business_claim_requires_explicit_nondefault_analyst_assumptions": True,
            "hard_business_claim_requires_case_packet_completeness": True,
            "hard_business_claim_requires_same_queue_incumbent_or_human_baseline": True,
        },
        "hard_business_value_claim_allowed": False,
        "supporting_operational_metrics_allowed": bool(rows_with_review_metrics),
        "next_slice": "Paper Track P10 - reproducible paper table generator" if rows_with_review_metrics else "Paper Track P9 follow-up",
        "command": "relaytic release-safety paper-operational-metrics --format json",
    }


def _build_paysim_rows(*, inputs: dict[str, Any], case_packet: dict[str, Any]) -> list[dict[str, Any]]:
    manifest = _payload(inputs["paysim_manifest"])
    baseline_table = _payload(inputs["paysim_table"])
    gate = _payload(inputs["paysim_gate"])
    selected = dict(manifest.get("validation_selected_competitive_model", {}))
    test_metrics = {
        "pr_auc": selected.get("test_pr_auc"),
        "roc_auc": selected.get("test_roc_auc"),
    }
    selected_table_row = _selected_paysim_table_row(baseline_table)
    test_metric_block = _deep_get(selected_table_row, ["test_metrics", "post_calibration"])
    if isinstance(test_metric_block, dict):
        test_metrics.update(
            {
                "n_samples": test_metric_block.get("n_samples"),
                "positive_count": test_metric_block.get("positive_count"),
                "positive_rate": test_metric_block.get("positive_rate"),
            }
        )
    op = dict(selected.get("test_operating_point", {}))
    if not op:
        return []
    completeness = _case_packet_row(case_packet, "paysim_temporal_transaction_fraud")
    row = _operational_row(
        row_id="paysim_p6a_competitive_selected_review_budget",
        dataset_id="paysim_temporal_transaction_fraud",
        evidence_id="paysim_competitive_p6a",
        source_role="supporting_temporal_proxy_numeric_and_operational_seed",
        paper_role="supporting_operational_proxy_only",
        model_family=selected.get("family_id"),
        model_metrics=test_metrics,
        operating_point=op,
        positive_count=test_metrics.get("positive_count"),
        n_samples=test_metrics.get("n_samples"),
        claim_boundary="supporting-only",
        artifact_refs=[
            "docs/reports/paysim_competitive_benchmark_manifest.json",
            "docs/reports/paysim_competitive_baseline_table.json",
            "docs/reports/paysim_publishability_gate.json",
            "docs/reports/paper_p8d_evidence_role_matrix.json",
        ],
        blocked_reason_codes=[
            *_paysim_gate_reason_codes(inputs=inputs, gate=gate),
            "analyst_hour_assumption_defaulted",
            "case_packet_not_materialized_for_aggregate_benchmark",
            "same_queue_incumbent_or_human_baseline_missing",
        ],
        case_packet_completeness=completeness,
    )
    return [row]


def _paysim_gate_reason_codes(*, inputs: dict[str, Any], gate: dict[str, Any]) -> list[Any]:
    codes = _as_list(gate.get("blocked_reason_codes"))
    graph_table = _payload(inputs["graph_table"])
    graph_evidence_available = bool(graph_table.get("validation_selected_competitive_baseline"))
    if graph_evidence_available:
        codes = [code for code in codes if code != "graph_benchmark_evidence_not_yet_executed_p7_required"]
    return codes


def _build_graph_rows(*, inputs: dict[str, Any], case_packet: dict[str, Any]) -> list[dict[str, Any]]:
    table = _payload(inputs["graph_table"])
    split = _payload(inputs["graph_split"])
    gate = _payload(inputs["graph_gate"])
    selected = dict(table.get("validation_selected_competitive_baseline", {}))
    op = dict(selected.get("test_operating_point", {}))
    if not op:
        return []
    test_metrics = {
        "pr_auc": selected.get("test_pr_auc"),
        "roc_auc": selected.get("test_roc_auc"),
    }
    test_split = _split_row(split, "test")
    if test_split:
        test_metrics.update(
            {
                "n_samples": test_split.get("known_label_count"),
                "positive_count": test_split.get("illicit_count"),
                "positive_rate": test_split.get("positive_rate_labeled"),
            }
        )
    for row in table.get("rows", []):
        if not isinstance(row, dict):
            continue
        if row.get("trial_id") == selected.get("trial_id") or bool(row.get("global_validation_selected")):
            metrics = row.get("test_metrics")
            if isinstance(metrics, dict):
                _update_present(
                    test_metrics,
                    {
                        "n_samples": metrics.get("n_samples"),
                        "positive_count": metrics.get("positive_count"),
                        "positive_rate": metrics.get("positive_rate"),
                    },
                )
            break
    completeness = _case_packet_row(case_packet, "elliptic_flattened_graph_aml")
    row = _operational_row(
        row_id="elliptic_p7_selected_graph_feature_review_budget",
        dataset_id="elliptic_flattened_graph_aml",
        evidence_id="elliptic_raw_graph_p7",
        source_role="supporting_temporal_graph_numeric_candidate",
        paper_role="supporting_graph_operational_metric_only",
        model_family=selected.get("family_id"),
        model_metrics=test_metrics,
        operating_point=op,
        positive_count=test_metrics.get("positive_count"),
        n_samples=test_metrics.get("n_samples"),
        claim_boundary="supporting-only",
        artifact_refs=[
            "docs/reports/paper_graph_feature_table.json",
            "docs/reports/paper_graph_publishability_gate.json",
            "docs/reports/paper_p8d_evidence_role_matrix.json",
        ],
        blocked_reason_codes=[
            *_as_list(gate.get("blocked_reason_codes")),
            "analyst_hour_assumption_defaulted",
            "case_packet_not_materialized_for_aggregate_benchmark",
            "same_queue_incumbent_or_human_baseline_missing",
        ],
        case_packet_completeness=completeness,
    )
    return [row]


def _selected_paysim_table_row(table: dict[str, Any]) -> dict[str, Any]:
    for row in table.get("rows", []):
        if isinstance(row, dict) and bool(row.get("selected_for_test_evaluation")):
            return row
    return {}


def _split_row(split: dict[str, Any], split_name: str) -> dict[str, Any]:
    for row in split.get("split_rows", []):
        if isinstance(row, dict) and row.get("split") == split_name:
            return row
    return {}


def _operational_row(
    *,
    row_id: str,
    dataset_id: str,
    evidence_id: str,
    source_role: str,
    paper_role: str,
    model_family: Any,
    model_metrics: dict[str, Any],
    operating_point: dict[str, Any],
    positive_count: Any,
    n_samples: Any,
    claim_boundary: str,
    artifact_refs: list[str],
    blocked_reason_codes: list[str],
    case_packet_completeness: dict[str, Any],
) -> dict[str, Any]:
    estimates = _operational_estimates(
        operating_point=operating_point,
        positive_count=_optional_float(positive_count),
        n_samples=_optional_float(n_samples),
    )
    return {
        "row_id": row_id,
        "dataset_id": dataset_id,
        "evidence_id": evidence_id,
        "source_role": source_role,
        "paper_role": paper_role,
        "model_family": model_family,
        "model_metrics": model_metrics,
        "review_budget_metrics_available": True,
        "review_budget_metrics": {
            "reviewed_count": operating_point.get("reviewed_count"),
            "review_fraction": operating_point.get("review_fraction"),
            "requested_review_fraction": operating_point.get("requested_review_fraction"),
            "true_positive_count": operating_point.get("true_positive_count"),
            "false_positive_count": operating_point.get("false_positive_count"),
            "false_positive_rate": operating_point.get("false_positive_rate"),
            "precision_at_k": operating_point.get("precision_at_k"),
            "recall_at_review_budget": operating_point.get("recall_at_review_budget"),
        },
        "operational_estimates": estimates,
        "case_packet_completeness": case_packet_completeness,
        "assumptions": {
            "analyst_hours_per_case": DEFAULT_ANALYST_HOURS_PER_CASE,
            "analyst_hours_assumption_defaulted": True,
            "baseline_kind": "prevalence_matched_unranked_review",
            "baseline_description": (
                "Estimated cases needed by an unranked review process to recover the same expected true positives "
                "at observed test prevalence; this is an operational burden proxy, not an ROI claim."
            ),
        },
        "claim_boundary": claim_boundary,
        "hard_business_value_claim_allowed": False,
        "supporting_operational_metric_allowed": True,
        "blocked_reason_codes": _dedupe(blocked_reason_codes),
        "artifact_refs": artifact_refs,
    }


def _operational_estimates(*, operating_point: dict[str, Any], positive_count: float | None, n_samples: float | None) -> dict[str, Any]:
    true_positives = _optional_float(operating_point.get("true_positive_count"))
    selected_false_positives = _optional_float(operating_point.get("false_positive_count"))
    selected_reviewed = _optional_float(operating_point.get("reviewed_count"))
    prevalence = positive_count / n_samples if positive_count is not None and n_samples and n_samples > 0 else None
    baseline_cases = math.ceil(true_positives / prevalence) if true_positives and prevalence and prevalence > 0 else None
    baseline_false_positives = (
        max(0.0, float(baseline_cases) - true_positives)
        if baseline_cases is not None and true_positives is not None
        else None
    )
    false_positive_reduction = (
        baseline_false_positives - selected_false_positives
        if baseline_false_positives is not None and selected_false_positives is not None
        else None
    )
    selected_hours = selected_reviewed * DEFAULT_ANALYST_HOURS_PER_CASE if selected_reviewed is not None else None
    baseline_hours = float(baseline_cases) * DEFAULT_ANALYST_HOURS_PER_CASE if baseline_cases is not None else None
    analyst_hours_saved = (
        baseline_hours - selected_hours
        if baseline_hours is not None and selected_hours is not None
        else None
    )
    return {
        "prevalence_matched_baseline_cases_for_same_true_positives": baseline_cases,
        "prevalence_matched_baseline_false_positives": _round(baseline_false_positives),
        "false_positive_reduction_vs_prevalence_baseline": _round(false_positive_reduction),
        "false_positive_reduction_fraction_vs_prevalence_baseline": _round(
            false_positive_reduction / baseline_false_positives
            if baseline_false_positives and false_positive_reduction is not None
            else None
        ),
        "selected_review_hours": _round(selected_hours),
        "baseline_review_hours_for_same_true_positives": _round(baseline_hours),
        "analyst_hours_saved_estimate": _round(analyst_hours_saved),
        "claim_basis": "derived_from_test_operating_point_and_test_prevalence",
        "claim_safety": "supporting_burden_proxy_not_business_value_claim",
    }


def _build_review_budget_curve(*, inputs: dict[str, Any], table: dict[str, Any]) -> dict[str, Any]:
    curves = [
        _paysim_p4_curve(inputs),
        _paysim_p6a_curve(inputs),
        _graph_p7_curve(inputs),
    ]
    curves = [curve for curve in curves if curve.get("points")]
    return {
        "schema_version": PAPER_OPERATIONAL_METRICS_SCHEMA_VERSION,
        "slice": "Paper Track P9",
        "status": "review_budget_curves_materialized" if curves else "blocked_no_review_budget_curves",
        "curve_count": len(curves),
        "curves": curves,
        "source_metric_table_status": table.get("status"),
        "artifact_refs": [
            "docs/reports/paysim_operating_point_table.json",
            "docs/reports/paysim_competitive_benchmark_manifest.json",
            "docs/reports/paper_graph_feature_table.json",
        ],
        "claim_boundary": "Review-budget curves are operational evaluation evidence; they do not authorize hard business-value or SOTA claims.",
    }


def _paysim_p4_curve(inputs: dict[str, Any]) -> dict[str, Any]:
    payload = _payload(inputs["paysim_p4_operating"])
    points = []
    for row in payload.get("review_budget_rows", []):
        if not isinstance(row, dict):
            continue
        test = dict(row.get("test", {}))
        points.append(_curve_point(row_id=f"p4_budget_{row.get('review_budget_fraction')}", source_row=row, test=test))
    return {
        "curve_id": "paysim_p4_leakage_safe_review_budget_curve",
        "dataset_id": "paysim_temporal_transaction_fraud",
        "model_family": payload.get("model_family"),
        "budget_tier": "baseline",
        "artifact_ref": "docs/reports/paysim_operating_point_table.json",
        "points": points,
    }


def _paysim_p6a_curve(inputs: dict[str, Any]) -> dict[str, Any]:
    payload = _payload(inputs["paysim_manifest"])
    selected = dict(payload.get("validation_selected_competitive_model", {}))
    points = []
    if isinstance(selected.get("test_operating_point"), dict):
        points.append(
            _curve_point(
                row_id="p6a_selected_review_budget",
                source_row={"review_budget_fraction": selected.get("review_budget_fraction")},
                test=dict(selected["test_operating_point"]),
            )
        )
    fixed_fpr = dict(selected.get("fixed_fpr", {}))
    if isinstance(fixed_fpr.get("test"), dict):
        points.append(
            _curve_point(
                row_id="p6a_fixed_fpr_0_001",
                source_row={"review_budget_fraction": None, "target_fpr": fixed_fpr.get("target_fpr")},
                test=dict(fixed_fpr["test"]),
            )
        )
    return {
        "curve_id": "paysim_p6a_competitive_selected_operating_points",
        "dataset_id": "paysim_temporal_transaction_fraud",
        "model_family": dict(payload.get("validation_selected_competitive_model", {})).get("family_id"),
        "budget_tier": payload.get("effective_budget_tier"),
        "artifact_ref": "docs/reports/paysim_competitive_benchmark_manifest.json",
        "points": points,
    }


def _graph_p7_curve(inputs: dict[str, Any]) -> dict[str, Any]:
    payload = _payload(inputs["graph_table"])
    selected = dict(payload.get("validation_selected_competitive_baseline", {}))
    points = []
    if isinstance(selected.get("test_operating_point"), dict):
        points.append(
            _curve_point(
                row_id="p7_selected_review_budget",
                source_row={"review_budget_fraction": selected.get("review_budget_fraction")},
                test=dict(selected["test_operating_point"]),
            )
        )
    fixed_fpr = dict(selected.get("fixed_fpr", {}))
    if isinstance(fixed_fpr.get("test"), dict):
        points.append(
            _curve_point(
                row_id="p7_fixed_fpr_0_001",
                source_row={"review_budget_fraction": None, "target_fpr": fixed_fpr.get("target_fpr")},
                test=dict(fixed_fpr["test"]),
            )
        )
    return {
        "curve_id": "elliptic_p7_graph_selected_operating_points",
        "dataset_id": "elliptic_flattened_graph_aml",
        "model_family": selected.get("family_id"),
        "budget_tier": payload.get("effective_budget_tier"),
        "artifact_ref": "docs/reports/paper_graph_feature_table.json",
        "points": points,
    }


def _curve_point(*, row_id: str, source_row: dict[str, Any], test: dict[str, Any]) -> dict[str, Any]:
    return {
        "point_id": row_id,
        "review_budget_fraction": source_row.get("review_budget_fraction"),
        "target_fpr": source_row.get("target_fpr"),
        "reviewed_count": test.get("reviewed_count"),
        "review_fraction": test.get("review_fraction"),
        "precision_at_k": test.get("precision_at_k"),
        "recall_at_review_budget": test.get("recall_at_review_budget"),
        "true_positive_count": test.get("true_positive_count"),
        "false_positive_count": test.get("false_positive_count"),
        "false_positive_rate": test.get("false_positive_rate"),
    }


def _build_case_packet_completeness_report(*, inputs: dict[str, Any]) -> dict[str, Any]:
    run_artifacts = dict(inputs.get("run_artifacts", {}))
    materialized_case_packet = dict(run_artifacts.get("case_packet", {}))
    materialized = bool(materialized_case_packet)
    completeness = _case_packet_completeness(materialized_case_packet) if materialized else None
    rows = [
        _aggregate_case_packet_row("paysim_temporal_transaction_fraud"),
        _aggregate_case_packet_row("elliptic_flattened_graph_aml"),
        _aggregate_case_packet_row("elliptic2_subgraph_aml", role="context_only_after_p8d"),
        _aggregate_case_packet_row("amlsim_synthetic_bank_graph", role="blocked_pending_reproducible_generation"),
    ]
    if materialized:
        rows.append(
            {
                "dataset_id": "optional_run_case_packet",
                "source": "operator_supplied_run_dir",
                "case_packet_artifact_ref": _display_path(inputs["root"], inputs["run_dir"] / "case_packet.json"),
                "case_packet_materialized": True,
                "completeness_score": completeness["score"],
                "present_fields": completeness["present_fields"],
                "missing_fields": completeness["missing_fields"],
                "claim_role": "supporting_demo_or_run_specific_context_only",
                "hard_business_value_claim_allowed": False,
                "blocked_reason_codes": ["run_specific_case_packet_not_same_as_paper_benchmark_rows"],
            }
        )
    aggregate_missing = all(not row["case_packet_materialized"] for row in rows if row["dataset_id"] != "optional_run_case_packet")
    return {
        "schema_version": PAPER_OPERATIONAL_METRICS_SCHEMA_VERSION,
        "slice": "Paper Track P9",
        "status": "case_packets_missing_for_paper_benchmark_rows" if aggregate_missing else "case_packet_completeness_reported",
        "required_fields": CASE_PACKET_REQUIRED_FIELDS,
        "rows": rows,
        "hard_business_value_claim_allowed": False,
        "claim_boundary": "Aggregate paper benchmark rows need materialized case packets before analyst-workflow value can become a hard claim.",
    }


def _aggregate_case_packet_row(dataset_id: str, *, role: str = "aggregate_benchmark_row") -> dict[str, Any]:
    return {
        "dataset_id": dataset_id,
        "source": role,
        "case_packet_artifact_ref": None,
        "case_packet_materialized": False,
        "completeness_score": 0.0,
        "present_fields": [],
        "missing_fields": CASE_PACKET_REQUIRED_FIELDS,
        "claim_role": "blocks_hard_business_value_claims",
        "hard_business_value_claim_allowed": False,
        "blocked_reason_codes": ["case_packet_not_materialized_for_aggregate_benchmark"],
    }


def _build_operational_claim_guard(
    *,
    inputs: dict[str, Any],
    table: dict[str, Any],
    case_packet: dict[str, Any],
) -> dict[str, Any]:
    p8d = _payload(inputs["p8d_decision"])
    rows = [dict(row) for row in table.get("rows", []) if isinstance(row, dict)]
    has_review_metrics = any(bool(row.get("review_budget_metrics_available")) for row in rows)
    reason_codes = []
    if not _p8d_allows_p9(p8d):
        reason_codes.append("p8d_thesis_decision_not_accepted")
    if not has_review_metrics:
        reason_codes.append("review_budget_metrics_missing")
    if case_packet.get("status") == "case_packets_missing_for_paper_benchmark_rows":
        reason_codes.append("paper_benchmark_case_packets_missing")
    if any(bool(_deep_get(row, ["assumptions", "analyst_hours_assumption_defaulted"])) for row in rows):
        reason_codes.append("analyst_hour_assumption_defaulted")
    if any("same_queue_incumbent_or_human_baseline_missing" in row.get("blocked_reason_codes", []) for row in rows):
        reason_codes.append("same_queue_incumbent_or_human_baseline_missing")
    if any(row.get("claim_boundary") != "paper" for row in rows):
        reason_codes.append("operational_metrics_supporting_only_not_hard_claims")
    if not bool(p8d.get("elliptic2_performance_contribution_allowed", False)):
        reason_codes.append("elliptic2_excluded_from_operational_performance_contribution_by_p8d")
    reason_codes = _dedupe(reason_codes)
    paper_can_continue = _p8d_allows_p9(p8d) and has_review_metrics
    hard_business_value_claim_allowed = paper_can_continue and not reason_codes
    status = (
        "operational_metrics_ready"
        if hard_business_value_claim_allowed
        else "supporting_operational_metrics_ready_hard_claims_blocked"
        if paper_can_continue
        else "blocked"
    )
    return {
        "schema_version": PAPER_OPERATIONAL_METRICS_SCHEMA_VERSION,
        "slice": "Paper Track P9",
        "status": status,
        "paper_can_continue_to_p10": paper_can_continue,
        "supporting_operational_metric_rows_allowed": has_review_metrics,
        "hard_business_value_claim_allowed": hard_business_value_claim_allowed,
        "headline_operational_claim_allowed": hard_business_value_claim_allowed,
        "blocked_reason_codes": reason_codes,
        "safe_operational_claims": [
            "review_budget_metrics_reported_for_supporting_paper_rows",
            "false_positive_burden_estimates_reported_as_claim_guarded_operational_proxies",
            "case_packet_completeness_missingness_reported_instead_of_invented",
        ] if has_review_metrics else [],
        "claim_guard_thresholds": {
            "requires_p8d_thesis_boundary": True,
            "requires_review_budget_metrics": True,
            "requires_materialized_case_packets_for_hard_business_value": True,
            "requires_explicit_nondefault_analyst_hour_assumptions": True,
            "requires_same_queue_incumbent_or_human_baseline_for_value_claim": True,
            "elliptic2_must_remain_non_contribution_until_later_parity_gate": True,
        },
        "next_slice": "Paper Track P10 - reproducible paper table generator" if paper_can_continue else "Paper Track P9 follow-up",
        "summary": (
            "P9 reports operational metrics as supporting evidence and deliberately blocks hard business-value claims."
            if paper_can_continue
            else "P9 cannot proceed because review-budget or thesis-boundary evidence is missing."
        ),
    }


def _excluded_tracks(inputs: dict[str, Any]) -> list[dict[str, Any]]:
    p8d = _payload(inputs["p8d_decision"])
    return [
        {
            "dataset_id": "elliptic2_subgraph_aml",
            "role": "supporting_context_and_limitation_only",
            "reason": "P8-D blocks Elliptic2 as a performance contribution in the first paper.",
            "artifact_ref": "docs/reports/paper_p8d_thesis_decision.json",
            "elliptic2_performance_contribution_allowed": bool(
                p8d.get("elliptic2_performance_contribution_allowed")
            ),
        },
        {
            "dataset_id": "amlsim_synthetic_bank_graph",
            "role": "blocked_or_future_proxy",
            "reason": "AMLSim remains blocked until seeded generation, hashes, license, and typology distribution are frozen.",
            "artifact_ref": "docs/reports/subgraph_benchmark_blocker_report.json",
        },
    ]


def _collect_run_artifacts(*, root: Path, run_dir: Path) -> dict[str, Any]:
    filenames = [
        "case_packet.json",
        "review_capacity_metric_report.json",
        "analyst_hour_savings_report.json",
        "operational_metric_guard.json",
    ]
    artifacts: dict[str, Any] = {}
    for filename in filenames:
        path = run_dir / filename
        if path.is_file():
            artifacts[filename.rsplit(".", 1)[0]] = _read_json(path)
    return artifacts


def _case_packet_completeness(case_packet: dict[str, Any]) -> dict[str, Any]:
    present = []
    missing = []
    for field in CASE_PACKET_REQUIRED_FIELDS:
        value = case_packet.get(field)
        if value is None or value == "" or value == [] or value == {}:
            missing.append(field)
        else:
            present.append(field)
    score = len(present) / len(CASE_PACKET_REQUIRED_FIELDS) if CASE_PACKET_REQUIRED_FIELDS else 0.0
    return {"score": _round(score) or 0.0, "present_fields": present, "missing_fields": missing}


def _case_packet_row(case_packet: dict[str, Any], dataset_id: str) -> dict[str, Any]:
    for row in case_packet.get("rows", []):
        if isinstance(row, dict) and row.get("dataset_id") == dataset_id:
            return {
                "completeness_score": row.get("completeness_score"),
                "case_packet_materialized": row.get("case_packet_materialized"),
                "blocked_reason_codes": row.get("blocked_reason_codes", []),
            }
    return {"completeness_score": 0.0, "case_packet_materialized": False, "blocked_reason_codes": []}


def _p8d_allows_p9(p8d: dict[str, Any]) -> bool:
    return (
        p8d.get("slice") == "Paper Track P8-D"
        and p8d.get("status") == "accepted_thesis_narrowing"
        and bool(p8d.get("p9_allowed"))
    )


def _read_artifact(path: Path) -> dict[str, Any]:
    return {"artifact_ref": _artifact_ref(path), "exists": path.is_file(), "payload": _read_json(path) if path.is_file() else {}}


def _read_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return dict(payload) if isinstance(payload, dict) else {}


def _payload(artifact: dict[str, Any]) -> dict[str, Any]:
    payload = artifact.get("payload", {})
    return dict(payload) if isinstance(payload, dict) else {}


def _artifact_ref(path: Path) -> str:
    parts = path.parts
    if "docs" in parts:
        return Path(*parts[parts.index("docs"):]).as_posix()
    return path.as_posix()


def _display_path(root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except (OSError, ValueError):
        return path.as_posix()


def _deep_get(payload: dict[str, Any], path: list[str]) -> Any:
    current: Any = payload
    for part in path:
        if not isinstance(current, dict):
            return None
        current = current.get(part)
    return current


def _update_present(target: dict[str, Any], values: dict[str, Any]) -> None:
    for key, value in values.items():
        if value is not None:
            target[key] = value


def _optional_float(value: Any) -> float | None:
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    return result if math.isfinite(result) else None


def _round(value: float | None) -> float | None:
    return round(float(value), 6) if value is not None and math.isfinite(float(value)) else None


def _dedupe(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        text = str(value).strip()
        if text and text not in seen:
            seen.add(text)
            result.append(text)
    return result


def _as_list(value: Any) -> list[Any]:
    return list(value) if isinstance(value, list) else []
