"""Baseline, ablation, and benchmark-relevance artifacts for Relaytic-AML."""

from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any

from relaytic.core.json_utils import write_json


AML_BASELINE_MATRIX_SCHEMA_VERSION = "relaytic.aml_baseline_matrix.v1"
AML_ABLATION_MATRIX_SCHEMA_VERSION = "relaytic.aml_ablation_matrix.v1"
AML_BASELINE_ADAPTER_REPORT_SCHEMA_VERSION = "relaytic.aml_baseline_adapter_report.v1"
AML_CAPABILITY_CONTRIBUTION_REPORT_SCHEMA_VERSION = "relaytic.aml_capability_contribution_report.v1"
AML_BENCHMARK_RELEVANCE_SCORECARD_SCHEMA_VERSION = "relaytic.aml_benchmark_relevance_scorecard.v1"

AML_BASELINE_FILENAMES = {
    "aml_baseline_matrix": "aml_baseline_matrix.json",
    "aml_ablation_matrix": "aml_ablation_matrix.json",
    "aml_baseline_adapter_report": "aml_baseline_adapter_report.json",
    "aml_capability_contribution_report": "aml_capability_contribution_report.json",
    "aml_benchmark_relevance_scorecard": "aml_benchmark_relevance_scorecard.json",
}

_SOURCE_FILENAMES = {
    "reference_approach_matrix": "reference_approach_matrix.json",
    "paper_benchmark_manifest": "paper_benchmark_manifest.json",
    "paper_benchmark_table": "paper_benchmark_table.json",
    "benchmark_ablation_matrix": "benchmark_ablation_matrix.json",
    "benchmark_parity_report": "benchmark_parity_report.json",
    "benchmark_gap_report": "benchmark_gap_report.json",
    "benchmark_release_gate": "benchmark_release_gate.json",
    "paper_claim_guard_report": "paper_claim_guard_report.json",
    "benchmark_truth_audit": "benchmark_truth_audit.json",
    "benchmark_pack_partition": "benchmark_pack_partition.json",
    "holdout_claim_policy": "holdout_claim_policy.json",
    "benchmark_generalization_audit": "benchmark_generalization_audit.json",
    "adapter_activation_report": "adapter_activation_report.json",
    "architecture_router_report": "architecture_router_report.json",
    "aml_benchmark_manifest": "aml_benchmark_manifest.json",
    "aml_public_claim_guard": "aml_public_claim_guard.json",
    "aml_failure_report": "aml_failure_report.json",
    "aml_domain_contract": "aml_domain_contract.json",
    "aml_claim_scope": "aml_claim_scope.json",
    "task_profile_contract": "task_profile_contract.json",
    "metric_contract": "metric_contract.json",
    "temporal_structure_report": "temporal_structure_report.json",
    "temporal_baseline_ladder": "temporal_baseline_ladder.json",
    "temporal_feature_ladder": "temporal_feature_ladder.json",
    "temporal_metric_contract": "temporal_metric_contract.json",
    "calibration_strategy_report": "calibration_strategy_report.json",
    "operating_point_contract": "operating_point_contract.json",
    "threshold_search_report": "threshold_search_report.json",
    "review_budget_optimization_report": "review_budget_optimization_report.json",
    "entity_graph_profile": "entity_graph_profile.json",
    "counterparty_network_report": "counterparty_network_report.json",
    "typology_detection_report": "typology_detection_report.json",
    "subgraph_risk_report": "subgraph_risk_report.json",
    "entity_case_expansion": "entity_case_expansion.json",
    "alert_queue_policy": "alert_queue_policy.json",
    "alert_queue_rankings": "alert_queue_rankings.json",
    "analyst_review_scorecard": "analyst_review_scorecard.json",
    "case_packet": "case_packet.json",
    "review_capacity_sensitivity": "review_capacity_sensitivity.json",
    "stream_risk_posture": "stream_risk_posture.json",
    "weak_label_posture": "weak_label_posture.json",
    "delayed_outcome_alignment": "delayed_outcome_alignment.json",
    "drift_recalibration_trigger": "drift_recalibration_trigger.json",
    "rolling_alert_quality_report": "rolling_alert_quality_report.json",
    "aml_business_value_report": "aml_business_value_report.json",
    "analyst_hour_savings_report": "analyst_hour_savings_report.json",
    "review_capacity_metric_report": "review_capacity_metric_report.json",
    "operational_metric_guard": "operational_metric_guard.json",
}

_RUN_OR_FALLBACK_STATES = {"ran", "fallback", "shadow_only"}
_ACTIVE_STATUSES = {"active", "ok", "ready", "partial", "supporting_only", "guarded", "pass", "warn"}
_INACTIVE_STATUSES = {
    "not_available",
    "not_applicable",
    "data_unavailable",
    "graph_not_available_for_dataset",
    "graph_not_available_for_casework",
    "no_graph",
    "inactive",
}


def sync_aml_baseline_artifacts(run_dir: str | Path) -> dict[str, Path]:
    """Build and write deterministic 15U AML baseline and ablation artifacts."""
    root = Path(run_dir)
    artifacts = build_aml_baseline_artifacts(run_dir=root)
    root.mkdir(parents=True, exist_ok=True)
    return {
        key: write_json(
            root / filename,
            artifacts[key],
            indent=2,
            ensure_ascii=False,
            sort_keys=True,
        )
        for key, filename in AML_BASELINE_FILENAMES.items()
    }


def read_aml_baseline_artifacts(run_dir: str | Path) -> dict[str, Any]:
    """Read AML baseline and ablation artifacts if present."""
    root = Path(run_dir)
    payload: dict[str, Any] = {}
    for key, filename in AML_BASELINE_FILENAMES.items():
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


def build_aml_baseline_artifacts(run_dir: str | Path) -> dict[str, dict[str, Any]]:
    """Construct AML baseline, ablation, capability, and relevance artifacts from run evidence."""
    root = Path(run_dir)
    generated_at = _utc_now()
    payloads = _read_source_payloads(root)

    adapter_report = _build_baseline_adapter_report(
        generated_at=generated_at,
        run_dir=root,
        payloads=payloads,
    )
    baseline_matrix = _build_baseline_matrix(
        generated_at=generated_at,
        run_dir=root,
        payloads=payloads,
        adapter_report=adapter_report,
    )
    ablation_matrix = _build_ablation_matrix(
        generated_at=generated_at,
        run_dir=root,
        payloads=payloads,
        baseline_matrix=baseline_matrix,
    )
    contribution_report = _build_capability_contribution_report(
        generated_at=generated_at,
        run_dir=root,
        payloads=payloads,
        baseline_matrix=baseline_matrix,
        ablation_matrix=ablation_matrix,
    )
    relevance_scorecard = _build_benchmark_relevance_scorecard(
        generated_at=generated_at,
        run_dir=root,
        payloads=payloads,
        baseline_matrix=baseline_matrix,
        ablation_matrix=ablation_matrix,
        contribution_report=contribution_report,
    )
    return {
        "aml_baseline_adapter_report": adapter_report,
        "aml_baseline_matrix": baseline_matrix,
        "aml_ablation_matrix": ablation_matrix,
        "aml_capability_contribution_report": contribution_report,
        "aml_benchmark_relevance_scorecard": relevance_scorecard,
    }


def render_aml_baseline_markdown(bundle: dict[str, Any]) -> str:
    """Render a compact human-facing 15U AML baseline and ablation summary."""
    baseline = _as_dict(bundle.get("aml_baseline_matrix"))
    adapter = _as_dict(bundle.get("aml_baseline_adapter_report"))
    ablation = _as_dict(bundle.get("aml_ablation_matrix"))
    contribution = _as_dict(bundle.get("aml_capability_contribution_report"))
    relevance = _as_dict(bundle.get("aml_benchmark_relevance_scorecard"))
    baseline_rows = [_as_dict(item) for item in _as_list(baseline.get("rows"))]
    ablation_rows = [_as_dict(item) for item in _as_list(ablation.get("rows"))]
    relevance_rows = [_as_dict(item) for item in _as_list(relevance.get("rows"))]
    top_capabilities = [_as_dict(item) for item in _as_list(contribution.get("top_capabilities"))]
    return "\n".join(
        [
            "# Relaytic-AML Baselines And Ablations",
            "",
            f"- Baseline status: `{baseline.get('status') or 'unknown'}`",
            f"- Run-or-fallback families: `{baseline.get('run_or_fallback_count', 0)}`",
            f"- Adapter status: `{adapter.get('status') or 'unknown'}`",
            f"- Material capability contributions: `{contribution.get('material_contribution_count', 0)}`",
            f"- Public metric changed by capabilities: `{contribution.get('public_metric_changed')}`",
            f"- Hard benchmark claim allowed: `{relevance.get('hard_benchmark_claim_allowed')}`",
            "",
            "## Baseline Families",
            *(
                f"- `{row.get('baseline_id')}` state=`{row.get('availability_state')}` model_metric=`{row.get('model_metric_value')}` operational_metric=`{row.get('operational_metric_value')}`"
                for row in baseline_rows[:8]
            ),
            *(["- none"] if not baseline_rows else []),
            "",
            "## Ablations",
            *(
                f"- `{row.get('ablation_id')}` evidence=`{row.get('evidence_state')}` impact=`{row.get('impact_state')}` delta_proxy=`{row.get('metric_delta_proxy')}`"
                for row in ablation_rows[:8]
            ),
            *(["- none"] if not ablation_rows else []),
            "",
            "## Top Capabilities",
            *(
                f"- `{row.get('capability_id')}` contribution=`{row.get('contribution_state')}` reason=`{row.get('summary')}`"
                for row in top_capabilities[:5]
            ),
            *(["- none"] if not top_capabilities else []),
            "",
            "## Benchmark Relevance",
            *(
                f"- `{row.get('benchmark_family')}` support=`{row.get('support_level')}` claim=`{row.get('public_claim_level')}`"
                for row in relevance_rows[:8]
            ),
            *(["- none"] if not relevance_rows else []),
            "",
        ]
    )


def _build_baseline_adapter_report(
    *,
    generated_at: str,
    run_dir: Path,
    payloads: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    family_evidence = _family_evidence(payloads)
    queue_active = _queue_active(payloads)
    graph_active = _graph_active(payloads)
    temporal_active = _temporal_active(payloads)
    calibration_active = _calibration_active(payloads)
    adapter_rows = _adapter_rows(payloads)
    optional_available = any(
        bool(row.get("available")) or _clean_text(row.get("activation_state")) in {"active", "ready"}
        for row in adapter_rows
        if _contains_any(_clean_text(row.get("family_id")) or "", ["xgboost", "lightgbm", "catboost"])
    )
    candidate_comparison = _as_dict(payloads["subgraph_risk_report"].get("candidate_comparison"))

    rows = [
        _adapter_row(
            baseline_id="rules_review_queue",
            family="rules_and_review_queue",
            availability_state="ran" if queue_active else "blocked",
            adapter_required=False,
            adapter_present=True,
            evidence_refs=_refs(payloads, ["alert_queue_rankings", "alert_queue_policy", "analyst_review_scorecard"]),
            blocked_reason=None if queue_active else "alert_queue_artifacts_missing_or_inactive",
        ),
        _adapter_row(
            baseline_id="calibrated_linear",
            family="linear_or_logistic_reference",
            availability_state="ran" if family_evidence["linear"] else "fallback",
            adapter_required=False,
            adapter_present=True,
            evidence_refs=_refs(payloads, ["reference_approach_matrix", "paper_benchmark_table", "benchmark_ablation_matrix", "calibration_strategy_report"]),
            blocked_reason=None if family_evidence["linear"] else "same_contract_linear_reference_not_materialized",
        ),
        _adapter_row(
            baseline_id="tree_ensemble",
            family="tree_ensemble_reference",
            availability_state="ran" if family_evidence["tree"] else "fallback",
            adapter_required=False,
            adapter_present=True,
            evidence_refs=_refs(payloads, ["reference_approach_matrix", "paper_benchmark_table", "benchmark_ablation_matrix"]),
            blocked_reason=None if family_evidence["tree"] else "same_contract_tree_reference_not_materialized",
        ),
        _adapter_row(
            baseline_id="boosted_tree_adapter",
            family="optional_boosted_tree_adapter",
            availability_state="ran" if family_evidence["boosted"] else "fallback" if optional_available else "optional_adapter_missing",
            adapter_required=True,
            adapter_present=bool(optional_available or family_evidence["boosted"]),
            evidence_refs=_refs(payloads, ["adapter_activation_report", "reference_approach_matrix", "paper_benchmark_table"]),
            blocked_reason=None if family_evidence["boosted"] else "optional_boosted_tree_adapter_unavailable_or_not_activated",
        ),
        _adapter_row(
            baseline_id="lagged_temporal_baseline",
            family="lagged_temporal_reference",
            availability_state="ran" if family_evidence["lagged"] else "fallback" if temporal_active else "blocked",
            adapter_required=False,
            adapter_present=True,
            evidence_refs=_refs(payloads, ["temporal_baseline_ladder", "temporal_structure_report", "stream_risk_posture", "benchmark_ablation_matrix"]),
            blocked_reason=None if family_evidence["lagged"] else "lagged_reference_not_materialized" if temporal_active else "temporal_evidence_missing",
        ),
        _adapter_row(
            baseline_id="structural_graph_baseline",
            family="deterministic_structural_graph_baseline",
            availability_state="ran" if graph_active else "blocked",
            adapter_required=False,
            adapter_present=True,
            evidence_refs=_refs(payloads, ["entity_graph_profile", "subgraph_risk_report", "counterparty_network_report"]),
            blocked_reason=None if graph_active else "graph_artifacts_missing_or_inactive",
        ),
        _adapter_row(
            baseline_id="message_passing_graph_shadow",
            family="message_passing_shadow_proxy",
            availability_state="shadow_only" if candidate_comparison.get("shadow_candidate") else "blocked",
            adapter_required=True,
            adapter_present=bool(candidate_comparison.get("shadow_candidate")),
            evidence_refs=_refs(payloads, ["subgraph_risk_report", "entity_case_expansion"]),
            blocked_reason=None if candidate_comparison.get("shadow_candidate") else "graph_shadow_candidate_not_materialized",
        ),
    ]
    run_or_fallback_count = sum(1 for row in rows if row["availability_state"] in _RUN_OR_FALLBACK_STATES)
    return {
        "schema_version": AML_BASELINE_ADAPTER_REPORT_SCHEMA_VERSION,
        "generated_at": generated_at,
        "status": "ready" if run_or_fallback_count >= 3 else "insufficient_baselines",
        "run_dir": str(run_dir),
        "baseline_family_count": len(rows),
        "run_or_fallback_count": run_or_fallback_count,
        "optional_adapter_present_count": sum(1 for row in rows if row["adapter_required"] and row["adapter_present"]),
        "calibration_evidence_active": calibration_active,
        "rows": rows,
        "summary": (
            f"Relaytic-AML has `{run_or_fallback_count}` AML baseline family/families that ran or have a declared fallback path."
        ),
        "trace": {
            "deterministic_evidence": _existing_source_filenames(payloads),
            "notes": [
                "15U does not promote optional graph-neural or boosted-tree adapters unless the run already materialized them.",
                "Fallback rows are explicit so absent adapters do not silently weaken a benchmark claim.",
            ],
        },
    }


def _build_baseline_matrix(
    *,
    generated_at: str,
    run_dir: Path,
    payloads: dict[str, dict[str, Any]],
    adapter_report: dict[str, Any],
) -> dict[str, Any]:
    metric_name = _comparison_metric(payloads)
    family_evidence = _family_evidence(payloads)
    review_capacity = payloads["review_capacity_metric_report"]
    subgraph = payloads["subgraph_risk_report"]
    candidate_comparison = _as_dict(subgraph.get("candidate_comparison"))
    rows: list[dict[str, Any]] = []
    evidence_by_id = {
        "calibrated_linear": family_evidence["linear"],
        "tree_ensemble": family_evidence["tree"],
        "boosted_tree_adapter": family_evidence["boosted"],
        "lagged_temporal_baseline": family_evidence["lagged"],
    }
    for adapter_row in _as_list(adapter_report.get("rows")):
        row = _as_dict(adapter_row)
        baseline_id = _clean_text(row.get("baseline_id")) or "unknown"
        model_metric_value = None
        model_metric_source = None
        operational_metric_name = None
        operational_metric_value = None
        if baseline_id in evidence_by_id:
            metric_row = evidence_by_id[baseline_id][0] if evidence_by_id[baseline_id] else {}
            model_metric_value = _metric_from_row(metric_row, metric_name)
            model_metric_source = _clean_text(metric_row.get("model_family")) or _clean_text(metric_row.get("family_id"))
        if baseline_id == "rules_review_queue":
            operational_metric_name = "precision_at_top_k"
            operational_metric_value = _round_metric(review_capacity.get("precision_at_top_k"))
        elif baseline_id == "structural_graph_baseline":
            operational_metric_name = "structural_subgraph_score"
            operational_metric_value = _round_metric(candidate_comparison.get("selected_score"))
        elif baseline_id == "message_passing_graph_shadow":
            operational_metric_name = "shadow_graph_score"
            operational_metric_value = _round_metric(candidate_comparison.get("shadow_score"))
        elif baseline_id == "lagged_temporal_baseline":
            operational_metric_name = "rolling_window_count"
            operational_metric_value = _round_metric(payloads["rolling_alert_quality_report"].get("window_count"))
        rows.append(
            {
                "baseline_id": baseline_id,
                "family": row.get("family"),
                "availability_state": row.get("availability_state"),
                "comparison_scope": _baseline_scope(baseline_id),
                "model_metric_name": metric_name,
                "model_metric_value": _round_metric(model_metric_value),
                "model_metric_source": model_metric_source,
                "operational_metric_name": operational_metric_name,
                "operational_metric_value": operational_metric_value,
                "adapter_required": row.get("adapter_required"),
                "adapter_present": row.get("adapter_present"),
                "evidence_refs": row.get("evidence_refs", []),
                "blocked_reason": row.get("blocked_reason"),
            }
        )

    run_or_fallback_count = sum(1 for row in rows if row["availability_state"] in _RUN_OR_FALLBACK_STATES)
    return {
        "schema_version": AML_BASELINE_MATRIX_SCHEMA_VERSION,
        "generated_at": generated_at,
        "status": "active" if run_or_fallback_count >= 3 else "insufficient_baselines",
        "run_dir": str(run_dir),
        "comparison_metric": metric_name,
        "metric_direction": _metric_direction(payloads, metric_name),
        "baseline_family_count": len(rows),
        "run_or_fallback_count": run_or_fallback_count,
        "ran_count": sum(1 for row in rows if row["availability_state"] == "ran"),
        "fallback_count": sum(1 for row in rows if row["availability_state"] == "fallback"),
        "shadow_only_count": sum(1 for row in rows if row["availability_state"] == "shadow_only"),
        "blocked_count": sum(1 for row in rows if row["availability_state"] not in _RUN_OR_FALLBACK_STATES),
        "rows": rows,
        "summary": (
            f"Relaytic-AML materialized or declared fallback paths for `{run_or_fallback_count}` baseline family/families; "
            "model metrics remain separate from operational review-queue utility."
        ),
    }


def _build_ablation_matrix(
    *,
    generated_at: str,
    run_dir: Path,
    payloads: dict[str, dict[str, Any]],
    baseline_matrix: dict[str, Any],
) -> dict[str, Any]:
    rows = [
        _ablation_no_graph(payloads),
        _ablation_no_temporal(payloads),
        _ablation_no_review_budget(payloads),
        _ablation_no_calibration(payloads),
        _ablation_no_typology_prior(payloads),
    ]
    rows = [row for row in rows if row]
    material_count = sum(1 for row in rows if row.get("impact_state") == "material")
    weak_count = sum(1 for row in rows if row.get("impact_state") == "weak")
    blocked_count = sum(1 for row in rows if row.get("evidence_state") == "blocked")
    return {
        "schema_version": AML_ABLATION_MATRIX_SCHEMA_VERSION,
        "generated_at": generated_at,
        "status": "active" if rows else "not_available",
        "run_dir": str(run_dir),
        "comparison_metric": baseline_matrix.get("comparison_metric"),
        "rows": rows,
        "required_ablation_ids": [
            "no_graph",
            "no_temporal",
            "no_review_budget",
            "no_calibration",
            "no_typology_prior",
        ],
        "material_contribution_count": material_count,
        "weak_contribution_count": weak_count,
        "blocked_ablation_count": blocked_count,
        "public_metric_changed": material_count > 0,
        "claim_boundary": (
            "Ablations use measured artifacts when available and otherwise label proxy or blocked evidence; "
            "they do not convert model-score wins into AML system wins."
        ),
        "summary": (
            f"Relaytic-AML recorded `{len(rows)}` AML capability ablation row(s), with `{material_count}` material contribution proxy row(s)."
        ),
    }


def _build_capability_contribution_report(
    *,
    generated_at: str,
    run_dir: Path,
    payloads: dict[str, dict[str, Any]],
    baseline_matrix: dict[str, Any],
    ablation_matrix: dict[str, Any],
) -> dict[str, Any]:
    rows = [_as_dict(item) for item in _as_list(ablation_matrix.get("rows"))]
    ranked = sorted(
        [row for row in rows if row.get("impact_state") in {"material", "weak"}],
        key=lambda item: (_impact_rank(_clean_text(item.get("impact_state"))), _safe_float(item.get("metric_delta_proxy"), 0.0)),
        reverse=True,
    )
    top_capabilities = [
        {
            "capability_id": str(row.get("ablation_id", "")).removeprefix("no_"),
            "removed_in_ablation": row.get("ablation_id"),
            "contribution_state": row.get("impact_state"),
            "evidence_state": row.get("evidence_state"),
            "metric_delta_proxy": row.get("metric_delta_proxy"),
            "evidence_refs": row.get("evidence_refs", []),
            "summary": row.get("summary"),
        }
        for row in ranked[:5]
    ]
    material_count = sum(1 for row in rows if row.get("impact_state") == "material")
    blocked_reasons = [
        {
            "ablation_id": row.get("ablation_id"),
            "blocked_reason": row.get("blocked_reason"),
        }
        for row in rows
        if row.get("evidence_state") == "blocked"
    ]
    guard = payloads["operational_metric_guard"]
    return {
        "schema_version": AML_CAPABILITY_CONTRIBUTION_REPORT_SCHEMA_VERSION,
        "generated_at": generated_at,
        "status": "active" if rows else "not_available",
        "run_dir": str(run_dir),
        "baseline_status": baseline_matrix.get("status"),
        "baseline_run_or_fallback_count": baseline_matrix.get("run_or_fallback_count", 0),
        "material_contribution_count": material_count,
        "weak_contribution_count": sum(1 for row in rows if row.get("impact_state") == "weak"),
        "blocked_capability_count": len(blocked_reasons),
        "public_metric_changed": material_count > 0,
        "hard_business_value_claim_allowed": guard.get("hard_business_value_claim_allowed"),
        "top_capabilities": top_capabilities,
        "blocked_capabilities": blocked_reasons,
        "claim_boundary": (
            "Capability contributions explain why an AML system surface is useful; public benchmark claims still require "
            "the benchmark truth gate, cross-track coverage, and operational guard."
        ),
        "summary": (
            f"Relaytic-AML found `{material_count}` material AML capability contribution(s) and "
            f"`{len(blocked_reasons)}` blocked contribution check(s)."
        ),
    }


def _build_benchmark_relevance_scorecard(
    *,
    generated_at: str,
    run_dir: Path,
    payloads: dict[str, dict[str, Any]],
    baseline_matrix: dict[str, Any],
    ablation_matrix: dict[str, Any],
    contribution_report: dict[str, Any],
) -> dict[str, Any]:
    corpus = _payload_corpus(payloads)
    graph_active = _graph_active(payloads)
    subgraph_active = _subgraph_active(payloads)
    transaction_active = _mentions_any(
        corpus,
        ["paysim", "transaction_fraud", "payment", "cash_out", "transfer", "nameorig", "namedest", "isfraud"],
    )
    elliptic_named = _mentions_any(corpus, ["elliptic"])
    amlsim_named = _mentions_any(corpus, ["amlsim", "synthetic_bank", "synthetic bank"])
    paper_table_ready = bool(_as_list(payloads["paper_benchmark_table"].get("rows"))) or bool(
        _as_list(payloads["reference_approach_matrix"].get("references"))
    )
    rows = [
        {
            "benchmark_family": "paysim_style_transaction_fraud",
            "support_level": "supported" if transaction_active else "proxy" if _aml_active(payloads) else "blocked",
            "covered_by_current_run": bool(transaction_active),
            "proxy_usable": bool(_aml_active(payloads) and not transaction_active),
            "public_claim_level": "current_run_supported" if transaction_active else "supporting_only",
            "blocked_reason_codes": [] if transaction_active else ["paysim_style_transaction_columns_or_manifest_missing"],
            "evidence_refs": _refs(payloads, ["aml_benchmark_manifest", "paper_benchmark_manifest", "task_profile_contract", "stream_risk_posture"]),
            "notes": "PaySim-style relevance requires transaction amount, temporal step, source/destination, and fraud-review label evidence.",
        },
        {
            "benchmark_family": "elliptic_style_graph_aml",
            "support_level": "supported" if elliptic_named and graph_active else "proxy" if graph_active else "blocked",
            "covered_by_current_run": bool(elliptic_named and graph_active),
            "proxy_usable": bool(graph_active and not elliptic_named),
            "public_claim_level": "current_run_supported" if elliptic_named and graph_active else "proxy_only",
            "blocked_reason_codes": [] if elliptic_named and graph_active else ["elliptic_raw_or_named_flattened_workload_missing"],
            "evidence_refs": _refs(payloads, ["aml_benchmark_manifest", "entity_graph_profile", "counterparty_network_report", "subgraph_risk_report"]),
            "notes": "Flattened graph evidence can support an Elliptic-style proxy; raw graph ingestion remains a later 15V boundary unless named evidence is present.",
        },
        {
            "benchmark_family": "elliptic2_style_subgraph_aml",
            "support_level": "proxy" if subgraph_active else "blocked",
            "covered_by_current_run": False,
            "proxy_usable": bool(subgraph_active),
            "public_claim_level": "proxy_only",
            "blocked_reason_codes": [] if subgraph_active else ["subgraph_risk_artifacts_missing"],
            "evidence_refs": _refs(payloads, ["subgraph_risk_report", "entity_case_expansion", "typology_detection_report"]),
            "notes": "Relaytic can explain suspicious subgraphs now; raw Elliptic2-style subgraph loading is reserved for Slice 15V.",
        },
        {
            "benchmark_family": "amlsim_style_synthetic_bank_graph",
            "support_level": "proxy" if graph_active or amlsim_named else "blocked",
            "covered_by_current_run": bool(amlsim_named),
            "proxy_usable": bool(graph_active),
            "public_claim_level": "proxy_only" if graph_active and not amlsim_named else "current_run_supported",
            "blocked_reason_codes": [] if graph_active or amlsim_named else ["bank_graph_or_synthetic_aml_fixture_missing"],
            "evidence_refs": _refs(payloads, ["entity_graph_profile", "typology_detection_report", "aml_benchmark_manifest"]),
            "notes": "Synthetic-bank graph relevance is useful for demo breadth but not a substitute for public raw benchmark coverage.",
        },
        {
            "benchmark_family": "generic_structured_tabular_benchmark",
            "support_level": "supported" if paper_table_ready else "blocked",
            "covered_by_current_run": bool(paper_table_ready),
            "proxy_usable": False,
            "public_claim_level": "supporting_benchmark_table" if paper_table_ready else "not_supported",
            "blocked_reason_codes": [] if paper_table_ready else ["paper_benchmark_table_or_reference_matrix_missing"],
            "evidence_refs": _refs(payloads, ["paper_benchmark_table", "reference_approach_matrix", "benchmark_parity_report"]),
            "notes": "Generic structured-data benchmark rows support method comparison but do not establish AML benchmark relevance by themselves.",
        },
    ]
    supported_count = sum(1 for row in rows if row["support_level"] == "supported")
    proxy_count = sum(1 for row in rows if row["support_level"] == "proxy")
    required_public_families = {"paysim_style_transaction_fraud", "elliptic_style_graph_aml"}
    covered_required = {
        row["benchmark_family"]
        for row in rows
        if row["benchmark_family"] in required_public_families and row["support_level"] == "supported"
    }
    release_gate = payloads["benchmark_release_gate"]
    public_guard = payloads["aml_public_claim_guard"]
    hard_claim_allowed = bool(
        required_public_families.issubset(covered_required)
        and release_gate.get("safe_to_cite_publicly")
        and public_guard.get("paper_primary_claim_allowed")
        and contribution_report.get("material_contribution_count", 0) > 0
        and baseline_matrix.get("run_or_fallback_count", 0) >= 3
    )
    return {
        "schema_version": AML_BENCHMARK_RELEVANCE_SCORECARD_SCHEMA_VERSION,
        "generated_at": generated_at,
        "status": "active" if supported_count or proxy_count else "blocked",
        "run_dir": str(run_dir),
        "supported_family_count": supported_count,
        "proxy_family_count": proxy_count,
        "blocked_family_count": sum(1 for row in rows if row["support_level"] == "blocked"),
        "required_public_families": sorted(required_public_families),
        "covered_required_public_families": sorted(covered_required),
        "hard_benchmark_claim_allowed": hard_claim_allowed,
        "public_claim_boundary": (
            "Use supported/proxy/blocked labels when discussing AML benchmarks; proxy graph evidence is useful for demos "
            "but not a raw Elliptic or Elliptic2 leaderboard claim."
        ),
        "rows": rows,
        "summary": (
            f"Relaytic-AML marks `{supported_count}` benchmark family/families supported and `{proxy_count}` proxy-supported; "
            f"hard public benchmark claims allowed = `{hard_claim_allowed}`."
        ),
    }


def _ablation_no_graph(payloads: dict[str, dict[str, Any]]) -> dict[str, Any]:
    subgraph = payloads["subgraph_risk_report"]
    comparison = _as_dict(subgraph.get("candidate_comparison"))
    selected_score = _optional_float(comparison.get("selected_score"))
    shadow_score = _optional_float(comparison.get("shadow_score"))
    delta = None
    if selected_score is not None:
        if shadow_score is not None:
            delta = max(0.0, selected_score - shadow_score)
        else:
            delta = selected_score
    graph_active = _graph_active(payloads)
    return _ablation_row(
        ablation_id="no_graph",
        removed_capability="counterparty_graph_and_subgraph_scoring",
        evidence_state="proxy" if graph_active else "blocked",
        metric_name="structural_subgraph_score_delta",
        metric_delta_proxy=_round_metric(delta),
        expected_public_metric_direction="lower_case_context_and_weaker_graph_benchmark_relevance",
        impact_state=_impact_state(delta, default_material=graph_active and bool(comparison.get("winner"))),
        evidence_refs=_refs(payloads, ["entity_graph_profile", "counterparty_network_report", "subgraph_risk_report"]),
        blocked_reason=None if graph_active else "graph_artifacts_missing_or_inactive",
        summary=(
            "Removing graph reasoning weakens structural case context and graph-benchmark relevance."
            if graph_active
            else "Graph ablation is blocked because no active graph artifact exists."
        ),
    )


def _ablation_no_temporal(payloads: dict[str, dict[str, Any]]) -> dict[str, Any]:
    stream = payloads["stream_risk_posture"]
    rolling = payloads["rolling_alert_quality_report"]
    drift = payloads["drift_recalibration_trigger"]
    window_count = _safe_float(rolling.get("window_count") or stream.get("rolling_window_count"), 0.0)
    trigger = bool(drift.get("trigger_recalibration") or stream.get("recalibration_triggered"))
    delta = min(0.25, (window_count / 100.0) + (0.05 if trigger else 0.0)) if _temporal_active(payloads) else None
    return _ablation_row(
        ablation_id="no_temporal",
        removed_capability="temporal_stream_risk_and_drift_posture",
        evidence_state="proxy" if _temporal_active(payloads) else "blocked",
        metric_name="temporal_alert_quality_delta_proxy",
        metric_delta_proxy=_round_metric(delta),
        expected_public_metric_direction="lower_temporal_benchmark_relevance_and_weaker_drift_claims",
        impact_state=_impact_state(delta, default_material=trigger),
        evidence_refs=_refs(payloads, ["stream_risk_posture", "rolling_alert_quality_report", "drift_recalibration_trigger", "temporal_structure_report"]),
        blocked_reason=None if _temporal_active(payloads) else "temporal_or_stream_artifacts_missing",
        summary=(
            "Removing temporal posture weakens drift, delayed-outcome, and rolling alert-quality claims."
            if _temporal_active(payloads)
            else "Temporal ablation is blocked because no stream or temporal artifact exists."
        ),
    )


def _ablation_no_review_budget(payloads: dict[str, dict[str, Any]]) -> dict[str, Any]:
    capacity = payloads["review_capacity_metric_report"]
    precision = _optional_float(capacity.get("precision_at_top_k"))
    expected_positive = _optional_float(capacity.get("expected_positive_count"))
    queue_count = _optional_float(capacity.get("queue_count"))
    prevalence = expected_positive / queue_count if expected_positive is not None and queue_count and queue_count > 0 else None
    delta = max(0.0, precision - prevalence) if precision is not None and prevalence is not None else None
    hours = payloads["analyst_hour_savings_report"]
    false_positive_reduction = _optional_float(hours.get("false_positive_reduction_at_fixed_recall"))
    if delta is None and false_positive_reduction is not None:
        delta = min(0.25, max(0.0, false_positive_reduction) / 100.0)
    queue_active = _queue_active(payloads)
    return _ablation_row(
        ablation_id="no_review_budget",
        removed_capability="analyst_review_budget_optimization",
        evidence_state="proxy" if queue_active and capacity else "blocked",
        metric_name="precision_lift_over_queue_prevalence",
        metric_delta_proxy=_round_metric(delta),
        expected_public_metric_direction="lower_precision_at_review_capacity_and_weaker_business_value_claims",
        impact_state=_impact_state(delta, default_material=queue_active),
        evidence_refs=_refs(payloads, ["alert_queue_rankings", "review_capacity_metric_report", "analyst_hour_savings_report", "operational_metric_guard"]),
        blocked_reason=None if queue_active and capacity else "review_queue_or_capacity_metrics_missing",
        summary=(
            "Removing the review budget weakens the evidence that Relaytic is optimizing analyst attention rather than only model score."
            if queue_active and capacity
            else "Review-budget ablation is blocked because queue/capacity evidence is missing."
        ),
    )


def _ablation_no_calibration(payloads: dict[str, dict[str, Any]]) -> dict[str, Any]:
    calibration = payloads["calibration_strategy_report"]
    operating_point = payloads["operating_point_contract"]
    threshold = _optional_float(operating_point.get("selected_threshold"))
    delta = abs(threshold - 0.5) if threshold is not None else None
    return _ablation_row(
        ablation_id="no_calibration",
        removed_capability="calibration_and_operating_point_selection",
        evidence_state="proxy" if _calibration_active(payloads) else "blocked",
        metric_name="threshold_distance_from_default",
        metric_delta_proxy=_round_metric(delta),
        expected_public_metric_direction="less_stable_precision_recall_tradeoff_and_weaker_operating_point_claims",
        impact_state=_impact_state(delta, weak_threshold=0.02, material_threshold=0.15),
        evidence_refs=_refs(payloads, ["calibration_strategy_report", "operating_point_contract", "threshold_search_report", "review_budget_optimization_report"]),
        blocked_reason=None if _calibration_active(payloads) else "calibration_or_operating_point_artifacts_missing",
        summary=(
            "Removing calibration weakens threshold, abstention, and review-budget operating-point evidence."
            if _calibration_active(payloads)
            else "Calibration ablation is blocked because no calibration or operating-point artifact exists."
        ),
    )


def _ablation_no_typology_prior(payloads: dict[str, dict[str, Any]]) -> dict[str, Any]:
    typology = payloads["typology_detection_report"]
    hit_count = int(typology.get("typology_hit_count", 0) or 0)
    delta = min(0.25, hit_count * 0.04) if hit_count else None
    return _ablation_row(
        ablation_id="no_typology_prior",
        removed_capability="aml_typology_prior_and_case_context",
        evidence_state="proxy" if hit_count else "blocked",
        metric_name="typology_case_context_delta_proxy",
        metric_delta_proxy=_round_metric(delta),
        expected_public_metric_direction="less_explainable_case_packets_and_weaker_typology_coverage",
        impact_state=_impact_state(delta, default_material=hit_count > 0),
        evidence_refs=_refs(payloads, ["typology_detection_report", "case_packet", "alert_queue_rankings"]),
        blocked_reason=None if hit_count else "typology_hits_missing",
        summary=(
            f"Removing typology priors would hide `{hit_count}` typology hit(s) from review-queue and case-packet evidence."
            if hit_count
            else "Typology-prior ablation is blocked because no typology hit exists."
        ),
    )


def _ablation_row(
    *,
    ablation_id: str,
    removed_capability: str,
    evidence_state: str,
    metric_name: str,
    metric_delta_proxy: float | None,
    expected_public_metric_direction: str,
    impact_state: str,
    evidence_refs: list[str],
    blocked_reason: str | None,
    summary: str,
) -> dict[str, Any]:
    return {
        "ablation_id": ablation_id,
        "removed_capability": removed_capability,
        "evidence_state": evidence_state,
        "metric_name": metric_name,
        "metric_delta_proxy": metric_delta_proxy,
        "expected_public_metric_direction": expected_public_metric_direction,
        "impact_state": impact_state if evidence_state != "blocked" else "not_available",
        "evidence_refs": evidence_refs,
        "blocked_reason": blocked_reason,
        "public_claim_caution": (
            "Use this ablation as AML capability evidence, not as a standalone public leaderboard claim."
        ),
        "summary": summary,
    }


def _adapter_row(
    *,
    baseline_id: str,
    family: str,
    availability_state: str,
    adapter_required: bool,
    adapter_present: bool,
    evidence_refs: list[str],
    blocked_reason: str | None,
) -> dict[str, Any]:
    return {
        "baseline_id": baseline_id,
        "family": family,
        "availability_state": availability_state,
        "adapter_required": adapter_required,
        "adapter_present": adapter_present,
        "evidence_refs": evidence_refs,
        "blocked_reason": blocked_reason,
    }


def _baseline_scope(baseline_id: str) -> str:
    mapping = {
        "rules_review_queue": "operational_review_queue",
        "calibrated_linear": "same_contract_model",
        "tree_ensemble": "same_contract_model",
        "boosted_tree_adapter": "same_contract_model_or_optional_adapter",
        "lagged_temporal_baseline": "temporal_same_contract_or_stream_proxy",
        "structural_graph_baseline": "structural_graph_case_context",
        "message_passing_graph_shadow": "graph_shadow_proxy",
    }
    return mapping.get(baseline_id, "unknown")


def _family_evidence(payloads: dict[str, dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    rows = _benchmark_family_rows(payloads)
    return {
        "linear": _rows_matching(rows, ["logistic", "linear", "ridge"]),
        "tree": _rows_matching(rows, ["random_forest", "forest", "extra_trees", "gradient_boosting", "hist_gradient"]),
        "boosted": _rows_matching(rows, ["xgboost", "lightgbm", "catboost"]),
        "lagged": _rows_matching(rows, ["lagged"]),
    }


def _benchmark_family_rows(payloads: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    matrix = payloads["reference_approach_matrix"]
    relaytic_reference = _as_dict(matrix.get("relaytic_reference"))
    if relaytic_reference:
        item = dict(relaytic_reference)
        item.setdefault("evidence_ref", "reference_approach_matrix.json")
        rows.append(item)
    for row in _as_list(matrix.get("references")):
        item = _as_dict(row)
        if item:
            item.setdefault("evidence_ref", "reference_approach_matrix.json")
            rows.append(item)
    for row in _as_list(payloads["paper_benchmark_table"].get("rows")):
        item = _as_dict(row)
        if item:
            item.setdefault("evidence_ref", "paper_benchmark_table.json")
            rows.append(item)
    for row in _as_list(payloads["benchmark_ablation_matrix"].get("rows")):
        item = _as_dict(row)
        if item:
            item.setdefault("evidence_ref", "benchmark_ablation_matrix.json")
            rows.append(item)
    for row in _as_list(payloads["adapter_activation_report"].get("rows")):
        item = _as_dict(row)
        if item:
            item.setdefault("model_family", item.get("family_id"))
            item.setdefault("evidence_ref", "adapter_activation_report.json")
            rows.append(item)
    return rows


def _rows_matching(rows: list[dict[str, Any]], tokens: list[str]) -> list[dict[str, Any]]:
    matched: list[dict[str, Any]] = []
    for row in rows:
        family = " ".join(
            [
                str(row.get("model_family", "")),
                str(row.get("family_id", "")),
                str(row.get("label", "")),
                str(row.get("ablation_id", "")),
            ]
        ).lower()
        if _contains_any(family, tokens):
            matched.append(row)
    return matched


def _adapter_rows(payloads: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    return [_as_dict(item) for item in _as_list(payloads["adapter_activation_report"].get("rows"))]


def _metric_from_row(row: dict[str, Any], metric_name: str | None) -> float | None:
    if not row:
        return None
    for key in ("test_metric", "validation_metric", "candidate_metric_value", "metric_value"):
        value = row.get(key)
        if isinstance(value, dict):
            direct = _optional_float(value.get(metric_name)) if metric_name else None
            if direct is not None:
                return direct
            for fallback in ("pr_auc", "roc_auc", "f1", "accuracy", "rmse", "mae", "r2"):
                direct = _optional_float(value.get(fallback))
                if direct is not None:
                    return direct
        else:
            direct = _optional_float(value)
            if direct is not None:
                return direct
    return None


def _comparison_metric(payloads: dict[str, dict[str, Any]]) -> str:
    for payload_key in (
        "reference_approach_matrix",
        "paper_benchmark_table",
        "benchmark_ablation_matrix",
        "benchmark_parity_report",
        "metric_contract",
    ):
        payload = payloads[payload_key]
        for key in ("comparison_metric", "benchmark_comparison_metric", "primary_metric"):
            value = _clean_text(payload.get(key))
            if value:
                return value
    return "pr_auc"


def _metric_direction(payloads: dict[str, dict[str, Any]], metric_name: str | None) -> str:
    for payload_key in ("reference_approach_matrix", "paper_benchmark_table", "benchmark_ablation_matrix"):
        value = _clean_text(payloads[payload_key].get("metric_direction"))
        if value:
            return value
    return "minimize" if _clean_text(metric_name) in {"rmse", "mae", "mse", "log_loss"} else "maximize"


def _impact_state(
    value: float | None,
    *,
    weak_threshold: float = 0.01,
    material_threshold: float = 0.05,
    default_material: bool = False,
) -> str:
    if value is None:
        return "material" if default_material else "not_available"
    if value >= material_threshold or default_material:
        return "material"
    if value >= weak_threshold:
        return "weak"
    return "observed_low_delta"


def _impact_rank(value: str | None) -> int:
    return {"material": 2, "weak": 1}.get(value or "", 0)


def _queue_active(payloads: dict[str, dict[str, Any]]) -> bool:
    rankings = payloads["alert_queue_rankings"]
    return _artifact_active(rankings) and bool(_as_list(rankings.get("ranking")) or int(rankings.get("queue_count", 0) or 0) > 0)


def _graph_active(payloads: dict[str, dict[str, Any]]) -> bool:
    graph = payloads["entity_graph_profile"]
    subgraph = payloads["subgraph_risk_report"]
    return (
        _artifact_active(graph)
        and (int(graph.get("node_count", 0) or 0) > 0 or int(graph.get("edge_count", 0) or 0) > 0)
    ) or _subgraph_active(payloads)


def _subgraph_active(payloads: dict[str, dict[str, Any]]) -> bool:
    subgraph = payloads["subgraph_risk_report"]
    return _artifact_active(subgraph) and (
        bool(_as_list(subgraph.get("selected_subgraphs")))
        or bool(_as_dict(subgraph.get("candidate_comparison")))
    )


def _temporal_active(payloads: dict[str, dict[str, Any]]) -> bool:
    stream = payloads["stream_risk_posture"]
    rolling = payloads["rolling_alert_quality_report"]
    temporal = payloads["temporal_structure_report"]
    return (
        _artifact_active(stream)
        or _artifact_active(rolling)
        or _artifact_active(temporal)
        or bool(payloads["temporal_baseline_ladder"])
    )


def _calibration_active(payloads: dict[str, dict[str, Any]]) -> bool:
    return bool(
        _artifact_active(payloads["calibration_strategy_report"])
        or _artifact_active(payloads["operating_point_contract"])
        or _artifact_active(payloads["threshold_search_report"])
        or _artifact_active(payloads["review_budget_optimization_report"])
    )


def _aml_active(payloads: dict[str, dict[str, Any]]) -> bool:
    domain = payloads["aml_domain_contract"]
    return bool(domain.get("aml_active")) or bool(payloads["aml_benchmark_manifest"]) or _graph_active(payloads) or _queue_active(payloads)


def _artifact_active(payload: dict[str, Any]) -> bool:
    if not payload:
        return False
    status = _clean_text(payload.get("status"))
    if status in _INACTIVE_STATUSES:
        return False
    if status in _ACTIVE_STATUSES:
        return True
    return bool(status or payload)


def _read_source_payloads(root: Path) -> dict[str, dict[str, Any]]:
    return {key: _read_json(root / filename) for key, filename in _SOURCE_FILENAMES.items()}


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return value if isinstance(value, dict) else {}


def _refs(payloads: dict[str, dict[str, Any]], keys: list[str]) -> list[str]:
    refs: list[str] = []
    for key in keys:
        filename = _SOURCE_FILENAMES.get(key)
        if filename and payloads.get(key):
            refs.append(filename)
    return refs


def _existing_source_filenames(payloads: dict[str, dict[str, Any]]) -> list[str]:
    return [
        filename
        for key, filename in _SOURCE_FILENAMES.items()
        if payloads.get(key)
    ]


def _payload_corpus(payloads: dict[str, dict[str, Any]]) -> str:
    try:
        return json.dumps(payloads, sort_keys=True).lower()
    except (TypeError, ValueError):
        return ""


def _mentions_any(corpus: str, tokens: list[str]) -> bool:
    return any(token.lower() in corpus for token in tokens)


def _contains_any(text: str, tokens: list[str]) -> bool:
    lower = text.lower()
    return any(token.lower() in lower for token in tokens)


def _as_dict(value: Any) -> dict[str, Any]:
    return dict(value) if isinstance(value, dict) else {}


def _as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


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


def _safe_float(value: Any, default: float) -> float:
    parsed = _optional_float(value)
    return default if parsed is None else parsed


def _round_metric(value: Any) -> float | None:
    parsed = _optional_float(value)
    if parsed is None:
        return None
    return round(parsed, 6)


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()
