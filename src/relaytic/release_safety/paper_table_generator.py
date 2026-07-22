"""Paper Track P10 reproducible paper table artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from relaytic.core.json_utils import write_json
from relaytic.release_safety.paper_evidence_contract import (
    METRIC_EVIDENCE_CELL_REQUIRED_FIELDS,
    METRIC_EVIDENCE_CELL_TYPE,
    PAPER_CLAIM_GATE_SCHEMA_VERSION,
    PAPER_METRIC_EVIDENCE_CELL_SCHEMA_VERSION,
    audit_evidence_gate_separation,
    build_evidence_schema_contract,
)


PAPER_TABLE_SCHEMA_VERSION = "relaytic.paper_table_generator.v1"
PAPER_TABLE_REPORT_DIR = Path("docs") / "reports"
PAPER_TABLE_FILENAMES = {
    "paper_result_table_final": "paper_result_table_final.json",
    "paper_table_provenance": "paper_table_provenance.json",
    "paper_reproduction_commands": "paper_reproduction_commands.md",
    "paper_metric_cell_audit": "paper_metric_cell_audit.json",
    "paper_publishability_matrix": "paper_publishability_matrix.json",
    "paper_claim_gate_records": "paper_claim_gate_records.json",
    "paper_evidence_schema_contract": "paper_evidence_schema_contract.json",
}

RUN_DIRECTORY_REF = "docs/reports"


def build_paper_table_pack(project_root: str | Path) -> dict[str, Any]:
    """Build P10 paper tables from committed paper-track artifacts."""
    root = Path(project_root)
    reports = root / PAPER_TABLE_REPORT_DIR
    inputs = _collect_inputs(reports)
    result_table = _build_result_table(inputs)
    cells = _collect_metric_cells(result_table)
    claim_gates = _collect_claim_gate_records(result_table)
    _remove_internal_gate_specs(result_table)
    separation_audit = audit_evidence_gate_separation(evidence_cells=cells, claim_gates=claim_gates)
    schema_contract = build_evidence_schema_contract()
    audit = _build_metric_cell_audit(
        inputs=inputs,
        result_table=result_table,
        cells=cells,
        separation_audit=separation_audit,
    )
    provenance = _build_table_provenance(
        inputs=inputs,
        result_table=result_table,
        cells=cells,
        claim_gates=claim_gates,
    )
    claim_gate_records = {
        "schema_version": PAPER_CLAIM_GATE_SCHEMA_VERSION,
        "slice": "Paper Track P27",
        "status": separation_audit["status"],
        "gate_count": len(claim_gates),
        "claim_gates": claim_gates,
        "separation_audit": separation_audit,
    }
    publishability = _build_publishability_matrix(inputs=inputs, result_table=result_table, audit=audit)
    commands = _build_reproduction_commands(inputs=inputs, result_table=result_table, audit=audit)
    result_table["metric_cell_audit_status"] = audit["status"]
    result_table["paper_can_continue_to_p11"] = bool(audit["paper_can_continue_to_p11"])
    result_table["next_slice"] = (
        "Paper Track P11 - paper draft and figure pack"
        if audit["paper_can_continue_to_p11"]
        else "Paper Track P10 follow-up"
    )
    return {
        "paper_result_table_final": result_table,
        "paper_table_provenance": provenance,
        "paper_reproduction_commands": commands,
        "paper_metric_cell_audit": audit,
        "paper_publishability_matrix": publishability,
        "paper_claim_gate_records": claim_gate_records,
        "paper_evidence_schema_contract": schema_contract,
    }


def sync_paper_table_pack(
    project_root: str | Path,
    *,
    output_dir: str | Path | None = None,
) -> dict[str, Path]:
    """Write P10 table artifacts to ``docs/reports`` by default."""
    root = Path(project_root)
    report_dir = Path(output_dir) if output_dir is not None else root / PAPER_TABLE_REPORT_DIR
    report_dir.mkdir(parents=True, exist_ok=True)
    artifacts = build_paper_table_pack(root)
    written: dict[str, Path] = {}
    for key, filename in PAPER_TABLE_FILENAMES.items():
        path = report_dir / filename
        if filename.endswith(".md"):
            path.write_text(str(artifacts[key]), encoding="utf-8")
            written[key] = path
        else:
            written[key] = write_json(path, artifacts[key], indent=2, sort_keys=True)
    return written


def render_paper_table_markdown(pack: dict[str, Any]) -> str:
    table = dict(pack.get("paper_result_table_final", {}))
    audit = dict(pack.get("paper_metric_cell_audit", {}))
    matrix = dict(pack.get("paper_publishability_matrix", {}))
    return "\n".join(
        [
            "# Paper P10 Reproducible Tables",
            "",
            f"- Status: `{table.get('status') or 'unknown'}`",
            f"- Table groups: `{len(table.get('table_groups') or [])}`",
            f"- Metric cells audited: `{audit.get('numeric_cell_count') or 0}`",
            f"- Cell audit: `{audit.get('status') or 'unknown'}`",
            f"- Hard claims allowed: `{matrix.get('hard_claims_allowed')}`",
            f"- Paper may continue to P11: `{audit.get('paper_can_continue_to_p11')}`",
            f"- Next slice: `{table.get('next_slice') or 'unknown'}`",
        ]
    ).rstrip() + "\n"


def _collect_inputs(reports: Path) -> dict[str, Any]:
    return {
        "dataset_registry": _read_artifact(reports / "paper_dataset_registry.json"),
        "split_contracts": _read_artifact(reports / "paper_split_contracts.json"),
        "p8d_decision": _read_artifact(reports / "paper_p8d_thesis_decision.json"),
        "p8d_matrix": _read_artifact(reports / "paper_p8d_evidence_role_matrix.json"),
        "p9_operational_table": _read_artifact(reports / "paper_operational_metric_table.json"),
        "p9_review_curve": _read_artifact(reports / "paper_review_budget_curve.json"),
        "p9_case_packet": _read_artifact(reports / "paper_case_packet_completeness_report.json"),
        "p9_claim_guard": _read_artifact(reports / "paper_operational_claim_guard.json"),
        "p6_baseline_table": _read_artifact(reports / "paper_tabular_baseline_table.json"),
        "p6_budget_contract": _read_artifact(reports / "paper_benchmark_budget_contract.json"),
        "p6_publishability_gate": _read_artifact(reports / "paper_publishability_gate.json"),
        "paysim_manifest": _read_artifact(reports / "paysim_competitive_benchmark_manifest.json"),
        "paysim_budget_contract": _read_artifact(reports / "paysim_competitive_budget_contract.json"),
        "paysim_gate": _read_artifact(reports / "paysim_publishability_gate.json"),
        "paysim_leakage": _read_artifact(reports / "paysim_leakage_safe_feature_report.json"),
        "graph_table": _read_artifact(reports / "paper_graph_feature_table.json"),
        "graph_budget_contract": _read_artifact(reports / "paper_graph_budget_contract.json"),
        "graph_gate": _read_artifact(reports / "paper_graph_publishability_gate.json"),
        "graph_split": _read_artifact(reports / "elliptic_temporal_split_report.json"),
        "elliptic2_gate": _read_artifact(reports / "elliptic2_publishability_gate.json"),
        "elliptic2_repeated": _read_artifact(reports / "elliptic2_repeated_seed_scorecard.json"),
        "elliptic2_reference_scorecard": _read_artifact(reports / "elliptic2_revclassify_reference_scorecard.json"),
        "elliptic2_parity_gate": _read_artifact(reports / "elliptic2_reference_parity_gate.json"),
        "elliptic2_entity_split": _read_artifact(reports / "elliptic2_entity_disjoint_split_report.json"),
        "elliptic2_cohort": _read_artifact(reports / "elliptic2_evaluable_cohort_reconciliation.json"),
        "amlsim_manifest": _read_artifact(reports / "amlsim_generation_manifest.json"),
        "amlsim_typology": _read_artifact(reports / "amlsim_typology_manifest.json"),
        "subgraph_blocker": _read_artifact(reports / "subgraph_benchmark_blocker_report.json"),
    }


def _build_result_table(inputs: dict[str, Any]) -> dict[str, Any]:
    p9_guard = _payload(inputs["p9_claim_guard"])
    p10_dependency_met = bool(p9_guard.get("paper_can_continue_to_p10"))
    rows = []
    if p10_dependency_met:
        rows.extend(_performance_rows(inputs))
        rows.extend(_operational_rows(inputs))
        rows.extend(_context_rows(inputs))
    status = "tables_generated_claim_guarded" if p10_dependency_met and rows else "blocked_pending_p9_operational_pack"
    return {
        "schema_version": PAPER_TABLE_SCHEMA_VERSION,
        "slice": "Paper Track P10",
        "status": status,
        "p10_dependency": {
            "artifact_ref": "docs/reports/paper_operational_claim_guard.json",
            "exists": inputs["p9_claim_guard"]["exists"],
            "status": p9_guard.get("status"),
            "paper_can_continue_to_p10": p10_dependency_met,
        },
        "table_groups": [
            {
                "table_id": "supporting_performance_table",
                "title": "Supporting AML Benchmark Metrics",
                "headline_table": False,
                "rows": [row for row in rows if row.get("table_group") == "supporting_performance_table"],
            },
            {
                "table_id": "operational_evaluation_table",
                "title": "Review-Budget and Operational Burden Metrics",
                "headline_table": False,
                "rows": [row for row in rows if row.get("table_group") == "operational_evaluation_table"],
            },
            {
                "table_id": "context_and_limitations_table",
                "title": "Modern Context, Blockers, and Limitations",
                "headline_table": False,
                "rows": [row for row in rows if row.get("table_group") == "context_and_limitations_table"],
            },
        ],
        "headline_performance_claim_allowed": False,
        "hard_aml_claim_allowed": False,
        "hard_business_value_claim_allowed": bool(p9_guard.get("hard_business_value_claim_allowed")),
        "claim_boundary": (
            "P10 tables are reproducible paper evidence. They do not convert supporting rows into headline, "
            "SOTA, hard AML, or business-value claims."
        ),
        "command": "relaytic release-safety paper-tables --format json",
    }


def _performance_rows(inputs: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    baseline = _payload(inputs["p6_baseline_table"])
    selected_baseline = dict(baseline.get("validation_selected_baseline", {}))
    if selected_baseline:
        rows.append(
            _table_row(
                row_id="paysim_p6_validation_selected_baseline",
                table_group="supporting_performance_table",
                dataset_id="paysim_temporal_transaction_fraud",
                dataset_display_name="PaySim synthetic mobile-money transaction fraud",
                evidence_role="baseline_reference_appendix",
                model_family=selected_baseline.get("family_id"),
                budget_tier="baseline",
                split_contract_id=baseline.get("split_contract_id") or "split_paysim_chronological_step_v1",
                source_claim_posture="baseline_only_not_headline",
                publishability_gate_ref="docs/reports/paper_publishability_gate.json",
                publishability_gate_status=_payload(inputs["p6_publishability_gate"]).get("status"),
                leakage_posture="train_only_features_validation_only_thresholds",
                command="relaytic release-safety tabular-baselines --budget-tier baseline --run-optional --format json",
                artifact_refs=[
                    "docs/reports/paper_tabular_baseline_table.json",
                    "docs/reports/paper_benchmark_budget_contract.json",
                    "docs/reports/paper_publishability_gate.json",
                ],
                metrics=[
                    _metric_cell(
                        "paysim_p6_validation_selected_baseline",
                        "validation_pr_auc",
                        selected_baseline.get("validation_pr_auc"),
                        dataset_id="paysim_temporal_transaction_fraud",
                        split="validation",
                        artifact_ref="docs/reports/paper_tabular_baseline_table.json",
                        artifact_field="validation_selected_baseline.validation_pr_auc",
                        source_claim_posture="baseline_only_not_headline",
                        budget_tier="baseline",
                        command="relaytic release-safety tabular-baselines --budget-tier baseline --run-optional --format json",
                        leakage_posture="train_only_features_validation_only_thresholds",
                        publishability_gate_ref="docs/reports/paper_publishability_gate.json",
                        publishability_gate_status=_payload(inputs["p6_publishability_gate"]).get("status"),
                    ),
                    _metric_cell(
                        "paysim_p6_validation_selected_baseline",
                        "test_pr_auc",
                        selected_baseline.get("test_pr_auc"),
                        dataset_id="paysim_temporal_transaction_fraud",
                        split="test",
                        artifact_ref="docs/reports/paper_tabular_baseline_table.json",
                        artifact_field="validation_selected_baseline.test_pr_auc",
                        source_claim_posture="baseline_only_not_headline",
                        budget_tier="baseline",
                        command="relaytic release-safety tabular-baselines --budget-tier baseline --run-optional --format json",
                        leakage_posture="train_only_features_validation_only_thresholds",
                        publishability_gate_ref="docs/reports/paper_publishability_gate.json",
                        publishability_gate_status=_payload(inputs["p6_publishability_gate"]).get("status"),
                    ),
                ],
            )
        )
    paysim = _payload(inputs["paysim_manifest"])
    selected = dict(paysim.get("validation_selected_competitive_model", {}))
    if selected:
        gate = _payload(inputs["paysim_gate"])
        command = "relaytic release-safety paysim-competitive --budget-tier competitive --run-optional --require-full-rerun --format json"
        rows.append(
            _table_row(
                row_id="paysim_p6a_competitive_selected",
                table_group="supporting_performance_table",
                dataset_id=paysim.get("dataset_id") or "paysim_temporal_transaction_fraud",
                dataset_display_name="PaySim synthetic mobile-money transaction fraud",
                evidence_role="supporting_temporal_proxy_numeric_candidate",
                model_family=selected.get("family_id"),
                budget_tier=paysim.get("effective_budget_tier") or "competitive",
                split_contract_id=paysim.get("split_contract_id") or "split_paysim_chronological_step_v1",
                source_claim_posture=gate.get("claim_boundary_from_taxonomy") or "supporting-only",
                publishability_gate_ref="docs/reports/paysim_publishability_gate.json",
                publishability_gate_status=gate.get("status"),
                leakage_posture="prior_step_destination_history_forbidden_balance_fields_excluded_validation_only_selection",
                command=command,
                artifact_refs=[
                    "docs/reports/paysim_competitive_benchmark_manifest.json",
                    "docs/reports/paysim_competitive_budget_contract.json",
                    "docs/reports/paysim_leakage_safe_feature_report.json",
                    "docs/reports/paysim_publishability_gate.json",
                ],
                metrics=[
                    _selected_metric("validation_pr_auc", selected, "validation", "validation_pr_auc", command, gate, paysim, inputs),
                    _selected_metric("test_pr_auc", selected, "test", "test_pr_auc", command, gate, paysim, inputs),
                    _selected_metric("test_roc_auc", selected, "test", "test_roc_auc", command, gate, paysim, inputs),
                    _operating_metric("precision_at_review_budget", selected, "precision_at_k", command, gate, paysim, inputs),
                    _operating_metric("recall_at_review_budget", selected, "recall_at_review_budget", command, gate, paysim, inputs),
                    _fixed_fpr_metric("fixed_fpr_recall", selected, "recall_at_review_budget", command, gate, paysim, inputs),
                ],
                protocol_metadata={
                    "test_exposure_contract": paysim.get("test_exposure_contract") or {
                        "test_partition_fixed": True,
                        "test_partition_previously_exposed": True,
                        "prior_test_exposure_roles": ["P4 reference", "P6 baseline"],
                        "competitive_selection_used_test": False,
                        "competitive_finalists_tested_after_freeze": 1,
                        "untouched_holdout_claim_allowed": False,
                    },
                    "operating_point": _operating_point_provenance(selected),
                },
            )
        )
    graph = _payload(inputs["graph_table"])
    selected_graph = dict(graph.get("validation_selected_competitive_baseline", {}))
    if selected_graph:
        gate = _payload(inputs["graph_gate"])
        command = "relaytic release-safety graph-baselines --budget-tier competitive --run-optional --require-full-rerun --format json"
        rows.append(
            _table_row(
                row_id="elliptic_p7_selected_graph_feature_baseline",
                table_group="supporting_performance_table",
                dataset_id=graph.get("track_id") or graph.get("dataset_id") or "elliptic_flattened_graph_aml",
                dataset_display_name="Elliptic Bitcoin temporal graph",
                evidence_role="supporting_temporal_graph_numeric_candidate",
                model_family=selected_graph.get("family_id"),
                budget_tier=graph.get("effective_budget_tier") or "competitive",
                split_contract_id="split_elliptic_temporal_step_v1",
                source_claim_posture=gate.get("claim_posture") or "supporting-only",
                publishability_gate_ref="docs/reports/paper_graph_publishability_gate.json",
                publishability_gate_status=gate.get("status"),
                leakage_posture="same_time_step_graph_snapshot_validation_only_selection",
                command=command,
                artifact_refs=[
                    "docs/reports/paper_graph_feature_table.json",
                    "docs/reports/paper_graph_budget_contract.json",
                    "docs/reports/paper_graph_publishability_gate.json",
                    "docs/reports/elliptic_temporal_split_report.json",
                ],
                metrics=[
                    _graph_metric("validation_pr_auc", selected_graph, "validation", "validation_pr_auc", command, gate, graph),
                    _graph_metric("test_pr_auc", selected_graph, "test", "test_pr_auc", command, gate, graph),
                    _graph_metric("test_roc_auc", selected_graph, "test", "test_roc_auc", command, gate, graph),
                    _graph_operating_metric("precision_at_review_budget", selected_graph, "precision_at_k", command, gate, graph),
                    _graph_operating_metric("recall_at_review_budget", selected_graph, "recall_at_review_budget", command, gate, graph),
                    _graph_fixed_fpr_metric("fixed_fpr_recall", selected_graph, "recall_at_review_budget", command, gate, graph),
                ],
                protocol_metadata={
                    "feature_view_boundary": "source-provided local and one-hop neighbor aggregates remain distinct from Relaytic-derived same-step structural features",
                    "operating_point": _operating_point_provenance(selected_graph),
                },
            )
        )
    return rows


def _operational_rows(inputs: dict[str, Any]) -> list[dict[str, Any]]:
    operational = _payload(inputs["p9_operational_table"])
    guard = _payload(inputs["p9_claim_guard"])
    rows = []
    for source in operational.get("rows", []):
        if not isinstance(source, dict):
            continue
        row_id = f"{source.get('row_id')}_operational"
        command = operational.get("command") or "relaytic release-safety paper-operational-metrics --format json"
        metrics = []
        for metric_id, value in dict(source.get("review_budget_metrics", {})).items():
            metrics.append(
                _metric_cell(
                    row_id,
                    metric_id,
                    value,
                    dataset_id=source.get("dataset_id"),
                    split="test",
                    artifact_ref="docs/reports/paper_operational_metric_table.json",
                    artifact_field=f"rows[{source.get('row_id')}].review_budget_metrics.{metric_id}",
                    source_claim_posture=source.get("claim_boundary") or "supporting-only",
                    budget_tier="operational_evaluation",
                    command=command,
                    leakage_posture="derived_from_validation_selected_test_operating_point",
                    publishability_gate_ref="docs/reports/paper_operational_claim_guard.json",
                    publishability_gate_status=guard.get("status"),
                    headline_metric_candidate=False,
                )
            )
        estimates = dict(source.get("operational_estimates", {}))
        for metric_id in [
            "prevalence_matched_baseline_cases_for_same_true_positives",
            "false_positive_reduction_vs_prevalence_baseline",
            "analyst_hours_saved_estimate",
        ]:
            metrics.append(
                _metric_cell(
                    row_id,
                    metric_id,
                    estimates.get(metric_id),
                    dataset_id=source.get("dataset_id"),
                    split="test",
                    artifact_ref="docs/reports/paper_operational_metric_table.json",
                    artifact_field=f"rows[{source.get('row_id')}].operational_estimates.{metric_id}",
                    source_claim_posture="supporting_burden_proxy_not_business_value_claim",
                    budget_tier="operational_evaluation",
                    command=command,
                    leakage_posture="derived_from_test_operating_point_and_test_prevalence",
                    publishability_gate_ref="docs/reports/paper_operational_claim_guard.json",
                    publishability_gate_status=guard.get("status"),
                    headline_metric_candidate=False,
                )
            )
        rows.append(
            _table_row(
                row_id=row_id,
                table_group="operational_evaluation_table",
                dataset_id=source.get("dataset_id"),
                dataset_display_name=source.get("dataset_id"),
                evidence_role=source.get("paper_role"),
                model_family=source.get("model_family"),
                budget_tier="operational_evaluation",
                split_contract_id=_split_contract_for_dataset(source.get("dataset_id")),
                source_claim_posture=source.get("claim_boundary") or "supporting-only",
                publishability_gate_ref="docs/reports/paper_operational_claim_guard.json",
                publishability_gate_status=guard.get("status"),
                leakage_posture="claim_guarded_operating_point_derived_evidence",
                command=command,
                artifact_refs=[
                    "docs/reports/paper_operational_metric_table.json",
                    "docs/reports/paper_review_budget_curve.json",
                    "docs/reports/paper_case_packet_completeness_report.json",
                    "docs/reports/paper_operational_claim_guard.json",
                ],
                metrics=metrics,
            )
        )
    return rows


def _context_rows(inputs: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    p8b = _payload(inputs["elliptic2_gate"])
    repeated = _payload(inputs["elliptic2_repeated"])
    reference_scorecard = _payload(inputs["elliptic2_reference_scorecard"])
    if p8b or repeated:
        command = "relaytic release-safety elliptic2-competitive --revtrack-dir <external-local-revtrack-dir> --budget-tier competitive --run-suite --require-full-rerun --format json"
        rows.append(
            _table_row(
                row_id="elliptic2_p8b_modern_context",
                table_group="context_and_limitations_table",
                dataset_id="elliptic2_subgraph_aml",
                dataset_display_name="Elliptic2 subgraph AML",
                evidence_role="supporting_modern_context_only",
                model_family=repeated.get("candidate_id") or "p8b_pooled_moments_lgbm",
                budget_tier="competitive_context",
                split_contract_id="provided_revtrack_trn_val_tst_partition_and_content_hash_robustness_partition",
                source_claim_posture="supporting_context_only_not_performance_contribution",
                publishability_gate_ref="docs/reports/elliptic2_publishability_gate.json",
                publishability_gate_status=p8b.get("status"),
                leakage_posture="revtrack_tst_prior_exposure_disclosed_hash_partition_used_as_robustness_check",
                command=command,
                artifact_refs=[
                    "docs/reports/elliptic2_publishability_gate.json",
                    "docs/reports/elliptic2_repeated_seed_scorecard.json",
                    "docs/reports/elliptic2_revclassify_reference_scorecard.json",
                    "docs/reports/elliptic2_split_robustness_report.json",
                    "docs/reports/paper_p8d_evidence_role_matrix.json",
                ],
                metrics=[
                    _context_metric(
                        "official_partition_test_pr_auc_mean",
                        _deep_get(repeated, ["official_partition", "test_pr_auc_mean"]),
                        "provided_revtrack_tst",
                        "docs/reports/elliptic2_repeated_seed_scorecard.json",
                        "official_partition.test_pr_auc_mean",
                        command,
                        p8b,
                    ),
                    _context_metric(
                        "official_partition_test_pr_auc_std",
                        _deep_get(repeated, ["official_partition", "test_pr_auc_std"]),
                        "provided_revtrack_tst",
                        "docs/reports/elliptic2_repeated_seed_scorecard.json",
                        "official_partition.test_pr_auc_std",
                        command,
                        p8b,
                    ),
                    _context_metric(
                        "hash_partition_test_pr_auc_mean",
                        _deep_get(repeated, ["robustness_partition", "test_pr_auc_mean"]),
                        "content_hash_test",
                        "docs/reports/elliptic2_repeated_seed_scorecard.json",
                        "robustness_partition.test_pr_auc_mean",
                        command,
                        p8b,
                    ),
                    _context_metric(
                        "published_reference_pr_auc",
                        _deep_get(reference_scorecard, ["reference", "RevClassify_DS", "pr_auc"]),
                        "reported_reference",
                        "docs/reports/elliptic2_revclassify_reference_scorecard.json",
                        "reference.RevClassify_DS.pr_auc",
                        command,
                        p8b,
                    ),
                    _context_metric(
                        "gap_to_published_reference_pr_auc",
                        p8b.get("official_gap_to_published_revclassify_ds"),
                        "reported_reference_comparison",
                        "docs/reports/elliptic2_publishability_gate.json",
                        "official_gap_to_published_revclassify_ds",
                        command,
                        p8b,
                    ),
                ],
            )
        )
    p8c = _payload(inputs["elliptic2_parity_gate"])
    entity_split = _payload(inputs["elliptic2_entity_split"])
    cohort = _payload(inputs["elliptic2_cohort"])
    if p8c:
        command = "relaytic release-safety elliptic2-reference-parity --revtrack-dir <external-local-revtrack-dir> --run-neural --format json"
        rows.append(
            _table_row(
                row_id="elliptic2_p8c_claim_firewall",
                table_group="context_and_limitations_table",
                dataset_id="elliptic2_subgraph_aml",
                dataset_display_name="Elliptic2 subgraph AML",
                evidence_role="limitation_and_claim_firewall",
                model_family=None,
                budget_tier="reference_parity_gate",
                split_contract_id="component_grouped_entity_disjoint_audit",
                source_claim_posture="blocked_claim_evidence",
                publishability_gate_ref="docs/reports/elliptic2_reference_parity_gate.json",
                publishability_gate_status=p8c.get("status"),
                leakage_posture="faithful_reference_parity_not_executable_current_core_equivalence_not_proven",
                command=command,
                artifact_refs=[
                    "docs/reports/elliptic2_reference_parity_gate.json",
                    "docs/reports/elliptic2_entity_disjoint_split_report.json",
                    "docs/reports/elliptic2_evaluable_cohort_reconciliation.json",
                ],
                metrics=[
                    _limitation_metric(
                        "largest_component_row_fraction",
                        _deep_get(entity_split, ["strict_component_protocol", "all_role_entity_components", "largest_component_row_fraction"]),
                        "component_audit",
                        "docs/reports/elliptic2_entity_disjoint_split_report.json",
                        "strict_component_protocol.all_role_entity_components.largest_component_row_fraction",
                        command,
                        p8c,
                    ),
                    _limitation_metric(
                        "revtrack_evaluable_row_count",
                        cohort.get("revtrack_evaluable_row_count"),
                        "cohort_audit",
                        "docs/reports/elliptic2_evaluable_cohort_reconciliation.json",
                        "revtrack_evaluable_row_count",
                        command,
                        p8c,
                    ),
                    _limitation_metric(
                        "official_core_subgraph_count",
                        cohort.get("official_core_subgraph_count"),
                        "cohort_audit",
                        "docs/reports/elliptic2_evaluable_cohort_reconciliation.json",
                        "official_core_subgraph_count",
                        command,
                        p8c,
                    ),
                ],
            )
        )
    amlsim = _payload(inputs["amlsim_manifest"])
    rows.append(
        _table_row(
            row_id="amlsim_p8_blocked_generation",
            table_group="context_and_limitations_table",
            dataset_id="amlsim_synthetic_bank_graph",
            dataset_display_name="AMLSim synthetic bank graph",
            evidence_role="blocked_pending_reproducible_generation",
            model_family=None,
            budget_tier="blocked",
            split_contract_id="split_amlsim_seeded_temporal_v1",
            source_claim_posture="blocked_or_future_proxy",
            publishability_gate_ref="docs/reports/subgraph_benchmark_blocker_report.json",
            publishability_gate_status=_payload(inputs["subgraph_blocker"]).get("decision_state") or _payload(inputs["subgraph_blocker"]).get("status"),
            leakage_posture="not_evaluated_seeded_generation_not_frozen",
            command="relaytic release-safety hard-graph-tracks --format json",
            artifact_refs=[
                "docs/reports/amlsim_generation_manifest.json",
                "docs/reports/amlsim_typology_manifest.json",
                "docs/reports/subgraph_benchmark_blocker_report.json",
            ],
            metrics=[
                _blocked_metric(
                    "test_pr_auc",
                    "blocked_pending_reproducible_generation",
                    "amlsim_synthetic_bank_graph",
                    "docs/reports/amlsim_generation_manifest.json",
                    "relaytic release-safety hard-graph-tracks --format json",
                    amlsim.get("status"),
                )
            ],
        )
    )
    return rows


def _build_metric_cell_audit(
    *,
    inputs: dict[str, Any],
    result_table: dict[str, Any],
    cells: list[dict[str, Any]],
    separation_audit: dict[str, Any],
) -> dict[str, Any]:
    p9_guard = _payload(inputs["p9_claim_guard"])
    numeric_cells = [cell for cell in cells if cell.get("value") is not None]
    blocked_cells = [cell for cell in cells if cell.get("value") is None]
    violations = []
    for cell in numeric_cells:
        missing = [
            field
            for field in METRIC_EVIDENCE_CELL_REQUIRED_FIELDS
            if cell.get(field) in (None, "", [])
        ]
        if missing:
            violations.append(
                {
                    "cell_id": cell.get("cell_id"),
                    "violation": "numeric_cell_missing_required_provenance",
                    "missing_fields": missing,
                }
            )
    violations.extend(separation_audit.get("violations", []))
    dependency_ready = bool(p9_guard.get("paper_can_continue_to_p10")) and result_table.get("status") == "tables_generated_claim_guarded"
    status = "pass" if dependency_ready and not violations and numeric_cells else "blocked"
    return {
        "schema_version": PAPER_TABLE_SCHEMA_VERSION,
        "slice": "Paper Track P10",
        "status": status,
        "paper_can_continue_to_p11": status == "pass",
        "numeric_cell_count": len(numeric_cells),
        "blocked_or_empty_cell_count": len(blocked_cells),
        "evidence_cell_schema": PAPER_METRIC_EVIDENCE_CELL_SCHEMA_VERSION,
        "metric_required_fields": list(METRIC_EVIDENCE_CELL_REQUIRED_FIELDS),
        "metric_required_field_count": len(METRIC_EVIDENCE_CELL_REQUIRED_FIELDS),
        "claim_gate_schema": PAPER_CLAIM_GATE_SCHEMA_VERSION,
        "evidence_gate_separation": separation_audit,
        "checks": {
            "p9_operational_claim_guard_allows_p10": bool(p9_guard.get("paper_can_continue_to_p10")),
            "all_numeric_cells_have_required_provenance": not any(
                violation.get("violation") == "numeric_cell_missing_required_provenance" for violation in violations
            ),
            "evidence_cells_are_factual_only": separation_audit.get("status") == "pass",
            "all_public_cells_have_separate_gate": bool(separation_audit.get("all_public_cells_have_separate_gate")),
            "hard_claims_remain_blocked_until_gates_pass": not bool(p9_guard.get("hard_business_value_claim_allowed")),
        },
        "violations": violations,
        "numeric_cells": numeric_cells,
        "blocked_or_empty_cells": blocked_cells,
        "next_slice": "Paper Track P11 - paper draft and figure pack" if status == "pass" else "Paper Track P10 follow-up",
    }


def _build_table_provenance(
    *,
    inputs: dict[str, Any],
    result_table: dict[str, Any],
    cells: list[dict[str, Any]],
    claim_gates: list[dict[str, Any]],
) -> dict[str, Any]:
    artifacts = []
    for key, artifact in inputs.items():
        if not isinstance(artifact, dict) or "artifact_ref" not in artifact:
            continue
        payload = _payload(artifact)
        artifacts.append(
            {
                "input_id": key,
                "artifact_ref": artifact.get("artifact_ref"),
                "exists": bool(artifact.get("exists")),
                "slice": payload.get("slice"),
                "status": payload.get("status") or payload.get("decision_state"),
                "schema_version": payload.get("schema_version"),
            }
        )
    return {
        "schema_version": PAPER_TABLE_SCHEMA_VERSION,
        "slice": "Paper Track P10",
        "status": "provenance_materialized" if cells else "blocked_no_cells",
        "run_directory_ref": RUN_DIRECTORY_REF,
        "source_artifacts": artifacts,
        "row_provenance": [
            {
                "row_id": row.get("row_id"),
                "dataset_id": row.get("dataset_id"),
                "table_group": row.get("table_group"),
                "budget_tier": row.get("budget_tier"),
                "claim_gate_id": f"{row.get('row_id')}.publication_gate",
                "command": row.get("command"),
                "artifact_refs": row.get("artifact_refs", []),
            }
            for row in _all_rows(result_table)
        ],
        "cell_provenance": cells,
        "claim_gate_records": claim_gates,
    }


def _build_publishability_matrix(
    *,
    inputs: dict[str, Any],
    result_table: dict[str, Any],
    audit: dict[str, Any],
) -> dict[str, Any]:
    p9_guard = _payload(inputs["p9_claim_guard"])
    rows = [
        _gate_row(
            "paysim_temporal_transaction_fraud",
            "docs/reports/paysim_publishability_gate.json",
            _filter_stale_paysim_gate(_payload(inputs["paysim_gate"]), inputs=inputs),
            supporting_key="supporting_paper_table_candidate_allowed",
            headline_key="headline_performance_claim_allowed",
            hard_key="hard_performance_claims_allowed",
        ),
        _gate_row(
            "elliptic_flattened_graph_aml",
            "docs/reports/paper_graph_publishability_gate.json",
            _payload(inputs["graph_gate"]),
            supporting_key="supporting_graph_table_candidate_allowed",
            headline_key="headline_graph_claim_allowed",
            hard_key="hard_performance_claims_allowed",
        ),
        _gate_row(
            "elliptic2_subgraph_aml",
            "docs/reports/elliptic2_publishability_gate.json",
            _payload(inputs["elliptic2_gate"]),
            supporting_key="supporting_paper_row_allowed",
            headline_key="headline_or_sota_claim_allowed",
            hard_key="hard_aml_claim_allowed",
            role="modern_context_only",
        ),
        _gate_row(
            "elliptic2_subgraph_aml",
            "docs/reports/elliptic2_reference_parity_gate.json",
            _payload(inputs["elliptic2_parity_gate"]),
            supporting_key="supporting_modern_context_row_allowed",
            headline_key="headline_or_sota_claim_allowed",
            hard_key="hard_aml_claim_allowed",
            role="claim_firewall",
        ),
        {
            "dataset_id": "paper_operational_layer",
            "role": "operational_claim_guard",
            "gate_ref": "docs/reports/paper_operational_claim_guard.json",
            "gate_status": p9_guard.get("status"),
            "supporting_table_allowed": bool(p9_guard.get("supporting_operational_metric_rows_allowed")),
            "performance_contribution_allowed": False,
            "headline_claim_allowed": bool(p9_guard.get("headline_operational_claim_allowed")),
            "hard_claim_allowed": bool(p9_guard.get("hard_business_value_claim_allowed")),
            "blocked_reason_codes": p9_guard.get("blocked_reason_codes", []),
        },
    ]
    hard_allowed = any(bool(row.get("hard_claim_allowed")) for row in rows)
    headline_allowed = any(bool(row.get("headline_claim_allowed")) for row in rows)
    return {
        "schema_version": PAPER_TABLE_SCHEMA_VERSION,
        "slice": "Paper Track P10",
        "status": "supporting_tables_ready_hard_claims_blocked" if audit.get("status") == "pass" else "blocked",
        "paper_can_continue_to_p11": bool(audit.get("paper_can_continue_to_p11")),
        "supporting_tables_ready": result_table.get("status") == "tables_generated_claim_guarded",
        "headline_claims_allowed": headline_allowed,
        "hard_claims_allowed": hard_allowed,
        "rows": rows,
        "claim_boundary": "P10 permits reproducible supporting tables only; hard claims require later clean-clone and claim-lint gates.",
    }


def _build_reproduction_commands(
    *,
    inputs: dict[str, Any],
    result_table: dict[str, Any],
    audit: dict[str, Any],
) -> str:
    lines = [
        "# Paper P10 Reproduction Commands",
        "",
        "Run from the repository root. External-local dataset paths are intentionally placeholders when the source is not committed.",
        "",
        "```powershell",
        "relaytic release-safety paysim-benchmark --format json",
        "relaytic release-safety elliptic-graph --format json",
        "relaytic release-safety tabular-baselines --budget-tier baseline --run-optional --format json",
        "relaytic release-safety paysim-competitive --budget-tier competitive --run-optional --require-full-rerun --format json",
        "relaytic release-safety graph-baselines --budget-tier competitive --run-optional --require-full-rerun --format json",
        "relaytic release-safety hard-graph-tracks --format json",
        "relaytic release-safety elliptic2-recovery --core-data-dir <external-local-core-dir> --revtrack-dir <external-local-revtrack-dir> --prepare-selected-embeddings --run-pilot --hash-large-assets --format json",
        "relaytic release-safety elliptic2-competitive --revtrack-dir <external-local-revtrack-dir> --budget-tier competitive --run-suite --require-full-rerun --format json",
        "relaytic release-safety elliptic2-reference-parity --revtrack-dir <external-local-revtrack-dir> --run-neural --format json",
        "relaytic release-safety paper-thesis-decision --format json",
        "relaytic release-safety paper-operational-metrics --format json",
        "relaytic release-safety paper-tables --format json",
        "```",
        "",
        f"- Table status: `{result_table.get('status')}`",
        f"- Metric audit status: `{audit.get('status')}`",
        f"- P9 dependency: `{_payload(inputs['p9_claim_guard']).get('status')}`",
        f"- Paper may continue to P11: `{audit.get('paper_can_continue_to_p11')}`",
    ]
    return "\n".join(lines).rstrip() + "\n"


def _table_row(
    *,
    row_id: str,
    table_group: str,
    dataset_id: Any,
    dataset_display_name: Any,
    evidence_role: Any,
    model_family: Any,
    budget_tier: str,
    split_contract_id: str,
    source_claim_posture: str,
    publishability_gate_ref: str,
    publishability_gate_status: Any,
    leakage_posture: str,
    command: str,
    artifact_refs: list[str],
    metrics: list[dict[str, Any]],
    protocol_metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "row_id": row_id,
        "table_group": table_group,
        "dataset_id": dataset_id,
        "dataset_display_name": dataset_display_name,
        "model_family": model_family,
        "budget_tier": budget_tier,
        "split_contract_id": split_contract_id,
        "claim_gate_id": f"{row_id}.publication_gate",
        "leakage_posture": leakage_posture,
        "command": command,
        "run_directory_ref": RUN_DIRECTORY_REF,
        "artifact_refs": artifact_refs,
        "metrics": metrics,
        "protocol_metadata": protocol_metadata or {},
        "_claim_gate_spec": {
            "publication_role": evidence_role,
            "source_claim_posture": source_claim_posture,
            "source_gate_ref": publishability_gate_ref,
            "source_gate_status": publishability_gate_status,
        },
    }


def _operating_point_provenance(selected: dict[str, Any]) -> dict[str, Any]:
    validation = dict(selected.get("validation_operating_point") or {})
    test = dict(selected.get("test_operating_point") or {})
    threshold = selected.get("validation_threshold")
    if threshold is None:
        threshold = validation.get("threshold")
    return {
        "calibration_method": selected.get("calibration_method")
        or dict(selected.get("calibration") or {}).get("selected_method"),
        "validation_threshold": threshold,
        "requested_review_fraction": selected.get("review_budget_fraction"),
        "validation": validation,
        "test": test,
        "comparison_operator": selected.get("comparison_operator") or validation.get("comparison_operator") or ">=",
        "tie_rule": selected.get("tie_rule") or validation.get("tie_rule") or "include_scores_equal_to_threshold",
        "threshold_applied_unchanged_to_test": bool(selected.get("threshold_applied_unchanged_to_test", True)),
    }


def _selected_metric(
    metric_id: str,
    selected: dict[str, Any],
    split: str,
    field: str,
    command: str,
    gate: dict[str, Any],
    manifest: dict[str, Any],
    inputs: dict[str, Any],
) -> dict[str, Any]:
    cell = _metric_cell(
        "paysim_p6a_competitive_selected",
        metric_id,
        selected.get(field),
        dataset_id=manifest.get("dataset_id") or "paysim_temporal_transaction_fraud",
        split=split,
        artifact_ref="docs/reports/paysim_competitive_benchmark_manifest.json",
        artifact_field=f"validation_selected_competitive_model.{field}",
        source_claim_posture=gate.get("claim_boundary_from_taxonomy") or "supporting-only",
        budget_tier=manifest.get("effective_budget_tier") or "competitive",
        command=command,
        leakage_posture="prior_step_destination_history_forbidden_balance_fields_excluded_validation_only_selection",
        publishability_gate_ref="docs/reports/paysim_publishability_gate.json",
        publishability_gate_status=gate.get("status"),
        headline_metric_candidate=False,
    )
    cell["model_identifier"] = selected.get("family_id") or "not_recorded"
    cell["calibration_status"] = selected.get("calibration_method") or "not_recorded"
    cell["operating_point_applicability"] = "contextual_operating_point_recorded"
    cell["operating_point_ref"] = (
        "docs/reports/paysim_competitive_benchmark_manifest.json#"
        f"validation_selected_competitive_model.{split}_operating_point"
    )
    cell["exposure_status"] = "validation_selection_surface" if split == "validation" else "fixed_test_previously_exposed"
    if split == "test":
        cell["test_exposure_contract"] = manifest.get("test_exposure_contract") or {
            "test_partition_fixed": True,
            "test_partition_previously_exposed": True,
            "prior_test_exposure_roles": ["P4 reference", "P6 baseline"],
            "competitive_selection_used_test": False,
            "competitive_finalists_tested_after_freeze": 1,
            "untouched_holdout_claim_allowed": False,
        }
    return cell


def _operating_metric(
    metric_id: str,
    selected: dict[str, Any],
    field: str,
    command: str,
    gate: dict[str, Any],
    manifest: dict[str, Any],
    inputs: dict[str, Any],
) -> dict[str, Any]:
    op = dict(selected.get("test_operating_point", {}))
    cell = _metric_cell(
        "paysim_p6a_competitive_selected",
        metric_id,
        op.get(field),
        dataset_id=manifest.get("dataset_id") or "paysim_temporal_transaction_fraud",
        split="test",
        artifact_ref="docs/reports/paysim_competitive_benchmark_manifest.json",
        artifact_field=f"validation_selected_competitive_model.test_operating_point.{field}",
        source_claim_posture=gate.get("claim_boundary_from_taxonomy") or "supporting-only",
        budget_tier=manifest.get("effective_budget_tier") or "competitive",
        command=command,
        leakage_posture="validation_selected_review_budget_fixed_on_test",
        publishability_gate_ref="docs/reports/paysim_publishability_gate.json",
        publishability_gate_status=gate.get("status"),
    )
    cell["operating_point_provenance"] = _operating_point_provenance(selected)
    cell["operating_point_applicability"] = "applicable"
    cell["operating_point_ref"] = (
        "docs/reports/paysim_competitive_benchmark_manifest.json#"
        "validation_selected_competitive_model.test_operating_point"
    )
    cell["calibration_status"] = selected.get("calibration_method") or "not_recorded"
    cell["exposure_status"] = "fixed_test_previously_exposed"
    cell["model_identifier"] = selected.get("family_id") or "not_recorded"
    cell["test_exposure_contract"] = manifest.get("test_exposure_contract") or {
        "test_partition_fixed": True,
        "test_partition_previously_exposed": True,
        "prior_test_exposure_roles": ["P4 reference", "P6 baseline"],
        "competitive_selection_used_test": False,
        "competitive_finalists_tested_after_freeze": 1,
        "untouched_holdout_claim_allowed": False,
    }
    return cell


def _fixed_fpr_metric(
    metric_id: str,
    selected: dict[str, Any],
    field: str,
    command: str,
    gate: dict[str, Any],
    manifest: dict[str, Any],
    inputs: dict[str, Any],
) -> dict[str, Any]:
    fixed = _deep_get(selected, ["fixed_fpr", "test"]) or {}
    cell = _metric_cell(
        "paysim_p6a_competitive_selected",
        metric_id,
        fixed.get(field) if isinstance(fixed, dict) else None,
        dataset_id=manifest.get("dataset_id") or "paysim_temporal_transaction_fraud",
        split="test",
        artifact_ref="docs/reports/paysim_competitive_benchmark_manifest.json",
        artifact_field=f"validation_selected_competitive_model.fixed_fpr.test.{field}",
        source_claim_posture=gate.get("claim_boundary_from_taxonomy") or "supporting-only",
        budget_tier=manifest.get("effective_budget_tier") or "competitive",
        command=command,
        leakage_posture="validation_fixed_fpr_threshold_fixed_on_test",
        publishability_gate_ref="docs/reports/paysim_publishability_gate.json",
        publishability_gate_status=gate.get("status"),
    )
    cell["operating_point_applicability"] = "applicable"
    cell["operating_point_ref"] = (
        "docs/reports/paysim_competitive_benchmark_manifest.json#"
        "validation_selected_competitive_model.fixed_fpr"
    )
    cell["calibration_status"] = selected.get("calibration_method") or "not_recorded"
    cell["exposure_status"] = "fixed_test_previously_exposed"
    cell["model_identifier"] = selected.get("family_id") or "not_recorded"
    return cell


def _graph_metric(
    metric_id: str,
    selected: dict[str, Any],
    split: str,
    field: str,
    command: str,
    gate: dict[str, Any],
    graph: dict[str, Any],
) -> dict[str, Any]:
    cell = _metric_cell(
        "elliptic_p7_selected_graph_feature_baseline",
        metric_id,
        selected.get(field),
        dataset_id=graph.get("track_id") or graph.get("dataset_id") or "elliptic_flattened_graph_aml",
        split=split,
        artifact_ref="docs/reports/paper_graph_feature_table.json",
        artifact_field=f"validation_selected_competitive_baseline.{field}",
        source_claim_posture=gate.get("claim_posture") or "supporting-only",
        budget_tier=graph.get("effective_budget_tier") or "competitive",
        command=command,
        leakage_posture="same_time_step_graph_snapshot_validation_only_selection",
        publishability_gate_ref="docs/reports/paper_graph_publishability_gate.json",
        publishability_gate_status=gate.get("status"),
    )
    cell["operating_point_applicability"] = "contextual_operating_point_recorded"
    cell["operating_point_ref"] = (
        "docs/reports/paper_graph_feature_table.json#"
        f"validation_selected_competitive_baseline.{split}_operating_point"
    )
    cell["calibration_status"] = selected.get("calibration_method") or "not_recorded"
    cell["exposure_status"] = "validation_selection_surface" if split == "validation" else "public_temporal_test_surface"
    cell["model_identifier"] = selected.get("family_id") or "not_recorded"
    return cell


def _graph_operating_metric(
    metric_id: str,
    selected: dict[str, Any],
    field: str,
    command: str,
    gate: dict[str, Any],
    graph: dict[str, Any],
) -> dict[str, Any]:
    op = dict(selected.get("test_operating_point", {}))
    cell = _metric_cell(
        "elliptic_p7_selected_graph_feature_baseline",
        metric_id,
        op.get(field),
        dataset_id=graph.get("track_id") or graph.get("dataset_id") or "elliptic_flattened_graph_aml",
        split="test",
        artifact_ref="docs/reports/paper_graph_feature_table.json",
        artifact_field=f"validation_selected_competitive_baseline.test_operating_point.{field}",
        source_claim_posture=gate.get("claim_posture") or "supporting-only",
        budget_tier=graph.get("effective_budget_tier") or "competitive",
        command=command,
        leakage_posture="validation_selected_review_budget_fixed_on_test",
        publishability_gate_ref="docs/reports/paper_graph_publishability_gate.json",
        publishability_gate_status=gate.get("status"),
    )
    cell["operating_point_provenance"] = _operating_point_provenance(selected)
    cell["operating_point_applicability"] = "applicable"
    cell["operating_point_ref"] = (
        "docs/reports/paper_graph_feature_table.json#"
        "validation_selected_competitive_baseline.test_operating_point"
    )
    cell["calibration_status"] = selected.get("calibration_method") or "not_recorded"
    cell["exposure_status"] = "public_temporal_test_surface"
    cell["model_identifier"] = selected.get("family_id") or "not_recorded"
    return cell


def _graph_fixed_fpr_metric(
    metric_id: str,
    selected: dict[str, Any],
    field: str,
    command: str,
    gate: dict[str, Any],
    graph: dict[str, Any],
) -> dict[str, Any]:
    fixed = _deep_get(selected, ["fixed_fpr", "test"]) or {}
    cell = _metric_cell(
        "elliptic_p7_selected_graph_feature_baseline",
        metric_id,
        fixed.get(field) if isinstance(fixed, dict) else None,
        dataset_id=graph.get("track_id") or graph.get("dataset_id") or "elliptic_flattened_graph_aml",
        split="test",
        artifact_ref="docs/reports/paper_graph_feature_table.json",
        artifact_field=f"validation_selected_competitive_baseline.fixed_fpr.test.{field}",
        source_claim_posture=gate.get("claim_posture") or "supporting-only",
        budget_tier=graph.get("effective_budget_tier") or "competitive",
        command=command,
        leakage_posture="validation_fixed_fpr_threshold_fixed_on_test",
        publishability_gate_ref="docs/reports/paper_graph_publishability_gate.json",
        publishability_gate_status=gate.get("status"),
    )
    cell["operating_point_applicability"] = "applicable"
    cell["operating_point_ref"] = (
        "docs/reports/paper_graph_feature_table.json#"
        "validation_selected_competitive_baseline.fixed_fpr"
    )
    cell["calibration_status"] = selected.get("calibration_method") or "not_recorded"
    cell["exposure_status"] = "public_temporal_test_surface"
    cell["model_identifier"] = selected.get("family_id") or "not_recorded"
    return cell


def _context_metric(
    metric_id: str,
    value: Any,
    split: str,
    artifact_ref: str,
    artifact_field: str,
    command: str,
    gate: dict[str, Any],
) -> dict[str, Any]:
    cell = _metric_cell(
        "elliptic2_p8b_modern_context",
        metric_id,
        value,
        dataset_id="elliptic2_subgraph_aml",
        split=split,
        artifact_ref=artifact_ref,
        artifact_field=artifact_field,
        source_claim_posture="supporting_context_only_not_performance_contribution",
        budget_tier="competitive_context",
        command=command,
        leakage_posture="revtrack_tst_prior_exposure_disclosed_hash_partition_used_as_robustness_check",
        publishability_gate_ref="docs/reports/elliptic2_publishability_gate.json",
        publishability_gate_status=gate.get("status"),
    )
    cell["calibration_status"] = "not_recorded"
    cell["operating_point_applicability"] = "not_applicable"
    cell["operating_point_ref"] = "not_applicable"
    if metric_id == "published_reference_pr_auc":
        cell["model_identifier"] = "RevClassify_DS_published_reference"
        cell["exposure_status"] = "external_published_reference_not_locally_generated"
        cell["provenance_role"] = "external_published_reference"
        cell["published_source_ref"] = "Song et al. (2024), Table 1, RevClassifyDS full-shot PR-AUC"
        cell["cohort_equivalence_status"] = "not_established"
    else:
        cell["model_identifier"] = "p8b_pooled_moments_lgbm"
        cell["exposure_status"] = (
            "provided_revtrack_tst_previously_exposed"
            if split == "provided_revtrack_tst"
            else "content_hash_robustness_partition"
        )
    return cell


def _limitation_metric(
    metric_id: str,
    value: Any,
    split: str,
    artifact_ref: str,
    artifact_field: str,
    command: str,
    gate: dict[str, Any],
) -> dict[str, Any]:
    return _metric_cell(
        "elliptic2_p8c_claim_firewall",
        metric_id,
        value,
        dataset_id="elliptic2_subgraph_aml",
        split=split,
        artifact_ref=artifact_ref,
        artifact_field=artifact_field,
        source_claim_posture="blocked_claim_evidence",
        budget_tier="reference_parity_gate",
        command=command,
        leakage_posture="faithful_reference_parity_not_executable_current_core_equivalence_not_proven",
        publishability_gate_ref="docs/reports/elliptic2_reference_parity_gate.json",
        publishability_gate_status=gate.get("status"),
    )


def _blocked_metric(
    metric_id: str,
    missing_reason: str,
    dataset_id: str,
    artifact_ref: str,
    command: str,
    gate_status: Any,
) -> dict[str, Any]:
    cell = _metric_cell(
        "amlsim_p8_blocked_generation",
        metric_id,
        None,
        dataset_id=dataset_id,
        split="blocked",
        artifact_ref=artifact_ref,
        artifact_field="status",
        source_claim_posture="blocked_or_future_proxy",
        budget_tier="blocked",
        command=command,
        leakage_posture="not_evaluated_seeded_generation_not_frozen",
        publishability_gate_ref="docs/reports/subgraph_benchmark_blocker_report.json",
        publishability_gate_status=gate_status or "blocked",
        headline_metric_candidate=False,
    )
    cell["cell_schema"] = "relaytic.paper_metric_placeholder.v1"
    cell["blocked_reason"] = missing_reason
    return cell


def _metric_cell(
    row_id: str,
    metric_id: str,
    value: Any,
    *,
    dataset_id: Any,
    split: str,
    artifact_ref: str,
    artifact_field: str,
    source_claim_posture: str,
    budget_tier: str,
    command: str,
    leakage_posture: str,
    publishability_gate_ref: str,
    publishability_gate_status: Any,
    headline_metric_candidate: bool = False,
) -> dict[str, Any]:
    del source_claim_posture, publishability_gate_ref, publishability_gate_status, headline_metric_candidate
    return {
        "cell_schema": PAPER_METRIC_EVIDENCE_CELL_SCHEMA_VERSION,
        "cell_id": f"{row_id}.{metric_id}",
        "cell_type": METRIC_EVIDENCE_CELL_TYPE,
        "row_id": row_id,
        "metric": metric_id,
        "metric_id": metric_id,
        "value": _json_scalar(value),
        "dataset_id": dataset_id,
        "split": split,
        "command": command,
        "run_directory_ref": RUN_DIRECTORY_REF,
        "artifact_ref": artifact_ref,
        "artifact_field": artifact_field,
        "budget_tier": budget_tier,
        "leakage_posture": leakage_posture,
        "operating_point_applicability": "not_applicable",
        "operating_point_ref": "not_applicable",
        "calibration_status": "not_recorded",
        "exposure_status": "not_recorded",
        "model_identifier": "not_recorded",
    }


def _collect_metric_cells(payload: Any) -> list[dict[str, Any]]:
    cells: list[dict[str, Any]] = []
    if isinstance(payload, dict):
        if (
            payload.get("cell_type") == METRIC_EVIDENCE_CELL_TYPE
            and payload.get("cell_schema") == PAPER_METRIC_EVIDENCE_CELL_SCHEMA_VERSION
        ):
            cells.append(dict(payload))
        for value in payload.values():
            cells.extend(_collect_metric_cells(value))
    elif isinstance(payload, list):
        for item in payload:
            cells.extend(_collect_metric_cells(item))
    return cells


def _collect_claim_gate_records(result_table: dict[str, Any]) -> list[dict[str, Any]]:
    gates: list[dict[str, Any]] = []
    for row in _all_rows(result_table):
        spec = dict(row.get("_claim_gate_spec") or {})
        cell_ids = [
            str(cell.get("cell_id"))
            for cell in row.get("metrics", [])
            if isinstance(cell, dict)
            and cell.get("cell_type") == METRIC_EVIDENCE_CELL_TYPE
            and cell.get("cell_schema") == PAPER_METRIC_EVIDENCE_CELL_SCHEMA_VERSION
            and cell.get("cell_id")
        ]
        if not cell_ids:
            continue
        row_id = str(row.get("row_id") or "")
        gate_reasons, missing_evidence = _gate_explanation(row_id=row_id, spec=spec)
        gates.append(
            {
                "schema_version": PAPER_CLAIM_GATE_SCHEMA_VERSION,
                "gate_id": f"{row_id}.publication_gate",
                "evidence_cell_ids": cell_ids,
                "admissible_use": _admissible_use(str(spec.get("publication_role") or "supporting evidence")),
                "publication_role": str(spec.get("publication_role") or "supporting_evidence"),
                "stronger_claim_status": "blocked",
                "gate_reasons": gate_reasons,
                "missing_evidence": missing_evidence,
                "source_gate_ref": spec.get("source_gate_ref"),
                "source_gate_status": spec.get("source_gate_status"),
            }
        )
    return gates


def _remove_internal_gate_specs(payload: Any) -> None:
    if isinstance(payload, dict):
        payload.pop("_claim_gate_spec", None)
        for value in payload.values():
            _remove_internal_gate_specs(value)
    elif isinstance(payload, list):
        for item in payload:
            _remove_internal_gate_specs(item)


def _admissible_use(publication_role: str) -> str:
    roles = {
        "baseline_reference_appendix": "baseline reference under the recorded dataset and split contract",
        "supporting_temporal_proxy_numeric_candidate": "bounded PaySim temporal-proxy demonstration",
        "supporting_temporal_graph_numeric_candidate": "bounded Elliptic temporal graph-feature demonstration",
        "supporting_burden_proxy_not_business_value_claim": "review-burden proxy under the recorded queue contract",
        "supporting_modern_context_only": "Elliptic2 modern benchmark context",
        "limitation_and_claim_firewall": "cohort and reference-parity limitation evidence",
        "blocked_pending_reproducible_generation": "blocked benchmark placeholder with no numeric claim",
    }
    return roles.get(publication_role, publication_role.replace("_", " "))


def _gate_explanation(*, row_id: str, spec: dict[str, Any]) -> tuple[list[str], list[str]]:
    if row_id == "paysim_p6a_competitive_selected":
        return (
            [
                "the fixed test partition had prior P4 reference and P6 baseline exposure",
                "competitive selection did not use test evidence and one finalist was evaluated after protocol freeze",
            ],
            [
                "genuinely unseen chronological or external holdout",
                "incumbent queue comparison under the same operating contract",
            ],
        )
    if row_id.startswith("paysim_"):
        return (
            ["PaySim is synthetic proxy evidence and the fixed test partition has prior baseline exposure"],
            ["genuinely unseen holdout", "real or partner-approved AML validation"],
        )
    if row_id.startswith("elliptic_p7"):
        return (
            ["the result is a single-seed temporal graph-feature estimate on public blockchain data"],
            ["repeated-seed detector study", "graph-native ablations", "real-bank validation"],
        )
    if row_id.startswith("elliptic2_p8b"):
        return (
            [
                "the RevTrack TST partition had prior exposure",
                "the local cohort is not established as equivalent to the published RevClassifyDS cohort",
            ],
            ["faithful reference replay", "cohort-equivalence proof", "blind or external holdout"],
        )
    if row_id.startswith("elliptic2_p8c"):
        return (
            ["reference parity and cohort equivalence are not established"],
            ["executable reference method", "accepted parity protocol", "resource-complete rerun"],
        )
    if row_id.startswith("amlsim"):
        return (
            ["the seeded AMLSim generation contract is not frozen"],
            ["versioned generator", "configuration hash", "seed manifest", "executed benchmark evidence"],
        )
    status = str(spec.get("source_claim_posture") or spec.get("source_gate_status") or "supporting-only evidence")
    return ([status.replace("_", " ")], ["stronger benchmark or deployment evidence"])


def _all_rows(result_table: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for group in result_table.get("table_groups", []):
        if isinstance(group, dict):
            rows.extend([dict(row) for row in group.get("rows", []) if isinstance(row, dict)])
    return rows


def _gate_row(
    dataset_id: str,
    gate_ref: str,
    gate: dict[str, Any],
    *,
    supporting_key: str,
    headline_key: str,
    hard_key: str,
    role: str = "publishability_gate",
) -> dict[str, Any]:
    return {
        "dataset_id": dataset_id,
        "role": role,
        "gate_ref": gate_ref,
        "gate_status": gate.get("status"),
        "supporting_table_allowed": bool(gate.get(supporting_key)),
        "performance_contribution_allowed": bool(gate.get("paper_primary_claim_allowed")),
        "headline_claim_allowed": bool(gate.get(headline_key)),
        "hard_claim_allowed": bool(gate.get(hard_key)),
        "blocked_reason_codes": gate.get("blocked_reason_codes", []),
    }


def _filter_stale_paysim_gate(gate: dict[str, Any], *, inputs: dict[str, Any]) -> dict[str, Any]:
    graph_table = _payload(inputs["graph_table"])
    if not graph_table.get("validation_selected_competitive_baseline"):
        return gate
    filtered = dict(gate)
    filtered["blocked_reason_codes"] = [
        code
        for code in _as_list(gate.get("blocked_reason_codes"))
        if code != "graph_benchmark_evidence_not_yet_executed_p7_required"
    ]
    return filtered


def _split_contract_for_dataset(dataset_id: Any) -> str:
    if dataset_id == "paysim_temporal_transaction_fraud":
        return "split_paysim_chronological_step_v1"
    if dataset_id in {"elliptic_flattened_graph_aml", "elliptic_bitcoin_flattened_graph_aml"}:
        return "split_elliptic_temporal_step_v1"
    if dataset_id == "elliptic2_subgraph_aml":
        return "split_elliptic2_subgraph_fixed_seed_v1"
    if dataset_id == "amlsim_synthetic_bank_graph":
        return "split_amlsim_seeded_temporal_v1"
    return "unknown"


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


def _deep_get(payload: dict[str, Any], path: list[str]) -> Any:
    current: Any = payload
    for part in path:
        if not isinstance(current, dict):
            return None
        current = current.get(part)
    return current


def _as_list(value: Any) -> list[Any]:
    return list(value) if isinstance(value, list) else []


def _json_scalar(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    return str(value)
