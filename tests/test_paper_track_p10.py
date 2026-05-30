from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from relaytic.release_safety import PAPER_TABLE_FILENAMES, build_paper_table_pack
from relaytic.ui.cli import main


PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = PROJECT_ROOT / "docs" / "reports"
pytestmark = pytest.mark.prepush


def _write_p10_input_reports(root: Path) -> None:
    reports = root / "docs" / "reports"
    reports.mkdir(parents=True, exist_ok=True)
    _write_json(
        reports / "paper_operational_claim_guard.json",
        {
            "schema_version": "relaytic.paper_operational_metrics.v1",
            "slice": "Paper Track P9",
            "status": "supporting_operational_metrics_ready_hard_claims_blocked",
            "paper_can_continue_to_p10": True,
            "supporting_operational_metric_rows_allowed": True,
            "hard_business_value_claim_allowed": False,
            "headline_operational_claim_allowed": False,
            "blocked_reason_codes": ["paper_benchmark_case_packets_missing"],
        },
    )
    _write_json(
        reports / "paper_operational_metric_table.json",
        {
            "schema_version": "relaytic.paper_operational_metrics.v1",
            "slice": "Paper Track P9",
            "status": "operational_metrics_reported_with_claim_guard",
            "command": "relaytic release-safety paper-operational-metrics --format json",
            "rows": [
                {
                    "row_id": "paysim_p6a_competitive_selected_review_budget",
                    "dataset_id": "paysim_temporal_transaction_fraud",
                    "paper_role": "supporting_operational_proxy_only",
                    "model_family": "sklearn_extra_trees",
                    "claim_boundary": "supporting-only",
                    "review_budget_metrics": {
                        "reviewed_count": 100,
                        "true_positive_count": 70,
                        "false_positive_count": 30,
                        "precision_at_k": 0.7,
                        "recall_at_review_budget": 0.5,
                    },
                    "operational_estimates": {
                        "prevalence_matched_baseline_cases_for_same_true_positives": 3500,
                        "false_positive_reduction_vs_prevalence_baseline": 3400,
                        "analyst_hours_saved_estimate": 3400,
                    },
                }
            ],
        },
    )
    _write_json(reports / "paper_review_budget_curve.json", {"status": "review_budget_curves_materialized"})
    _write_json(reports / "paper_case_packet_completeness_report.json", {"status": "case_packets_missing_for_paper_benchmark_rows"})
    _write_json(
        reports / "paper_tabular_baseline_table.json",
        {
            "schema_version": "relaytic.paper_tabular_baseline_suite.v1",
            "slice": "Paper Track P6",
            "status": "ok",
            "split_contract_id": "split_paysim_chronological_step_v1",
            "validation_selected_baseline": {
                "family_id": "sklearn_extra_trees",
                "validation_pr_auc": 0.3,
                "test_pr_auc": 0.33,
            },
        },
    )
    _write_json(reports / "paper_benchmark_budget_contract.json", {"status": "frozen"})
    _write_json(reports / "paper_publishability_gate.json", {"status": "blocked"})
    _write_json(
        reports / "paysim_competitive_benchmark_manifest.json",
        {
            "schema_version": "relaytic.paysim_competitive_benchmark.v1",
            "slice": "Paper Track P6-A",
            "status": "ok",
            "dataset_id": "paysim_temporal_transaction_fraud",
            "effective_budget_tier": "competitive",
            "split_contract_id": "split_paysim_chronological_step_v1",
            "command": "relaytic release-safety paysim-competitive --budget-tier competitive --run-optional --format json",
            "validation_selected_competitive_model": {
                "family_id": "sklearn_extra_trees",
                "validation_pr_auc": 0.56,
                "test_pr_auc": 0.64,
                "test_roc_auc": 0.97,
                "test_operating_point": {
                    "precision_at_k": 0.7,
                    "recall_at_review_budget": 0.5,
                },
                "fixed_fpr": {"test": {"recall_at_review_budget": 0.41}},
            },
        },
    )
    _write_json(reports / "paysim_competitive_budget_contract.json", {"status": "executed"})
    _write_json(reports / "paysim_leakage_safe_feature_report.json", {"status": "pass"})
    _write_json(
        reports / "paysim_publishability_gate.json",
        {
            "status": "pass_supporting_only",
            "claim_boundary_from_taxonomy": "supporting-only",
            "supporting_paper_table_candidate_allowed": True,
            "headline_performance_claim_allowed": False,
            "hard_performance_claims_allowed": False,
            "blocked_reason_codes": ["graph_benchmark_evidence_not_yet_executed_p7_required"],
        },
    )
    _write_json(
        reports / "paper_graph_feature_table.json",
        {
            "schema_version": "relaytic.paper_graph_baseline_suite.v1",
            "slice": "Paper Track P7",
            "status": "ok",
            "track_id": "elliptic_flattened_graph_aml",
            "effective_budget_tier": "competitive",
            "validation_selected_competitive_baseline": {
                "family_id": "lightgbm_classifier",
                "validation_pr_auc": 0.97,
                "test_pr_auc": 0.67,
                "test_roc_auc": 0.89,
                "test_operating_point": {
                    "precision_at_k": 1.0,
                    "recall_at_review_budget": 0.06,
                },
                "fixed_fpr": {"test": {"recall_at_review_budget": 0.58}},
            },
        },
    )
    _write_json(reports / "paper_graph_budget_contract.json", {"status": "ok"})
    _write_json(
        reports / "paper_graph_publishability_gate.json",
        {
            "status": "pass_supporting_only",
            "claim_posture": "supporting-only",
            "supporting_graph_table_candidate_allowed": True,
            "headline_graph_claim_allowed": False,
            "hard_performance_claims_allowed": False,
        },
    )
    _write_json(reports / "elliptic_temporal_split_report.json", {"status": "ok"})
    _write_json(
        reports / "elliptic2_publishability_gate.json",
        {
            "status": "pass_supporting_modern_context_only",
            "supporting_paper_row_allowed": True,
            "headline_or_sota_claim_allowed": False,
            "hard_aml_claim_allowed": False,
            "published_reference_pr_auc": 0.974,
            "official_gap_to_published_revclassify_ds": -0.03,
        },
    )
    _write_json(
        reports / "elliptic2_repeated_seed_scorecard.json",
        {
            "status": "complete",
            "candidate_id": "p8b_pooled_moments_lgbm",
            "official_partition": {"test_pr_auc_mean": 0.943, "test_pr_auc_std": 0.001},
            "robustness_partition": {"test_pr_auc_mean": 0.93},
        },
    )
    _write_json(
        reports / "elliptic2_reference_parity_gate.json",
        {
            "status": "blocked_supporting_only_thesis_narrowing_required",
            "supporting_modern_context_row_allowed": True,
            "headline_or_sota_claim_allowed": False,
            "hard_aml_claim_allowed": False,
        },
    )
    _write_json(
        reports / "elliptic2_entity_disjoint_split_report.json",
        {
            "status": "blocked_degenerate_component_structure",
            "strict_component_protocol": {
                "all_role_entity_components": {"largest_component_row_fraction": 0.999}
            },
        },
    )
    _write_json(
        reports / "elliptic2_evaluable_cohort_reconciliation.json",
        {
            "status": "narrowed_to_revtrack_evaluable_cohort",
            "revtrack_evaluable_row_count": 110902,
            "official_core_subgraph_count": 121810,
        },
    )
    _write_json(reports / "amlsim_generation_manifest.json", {"status": "blocked"})
    _write_json(reports / "amlsim_typology_manifest.json", {"status": "blocked"})
    _write_json(reports / "subgraph_benchmark_blocker_report.json", {"status": "blocked"})


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _load_report(name: str) -> dict[str, Any]:
    return json.loads((REPORT_DIR / name).read_text(encoding="utf-8"))


def test_paper_track_p10_generates_provenance_backed_tables(tmp_path: Path) -> None:
    _write_p10_input_reports(tmp_path)

    pack = build_paper_table_pack(tmp_path)
    table = pack["paper_result_table_final"]
    audit = pack["paper_metric_cell_audit"]
    matrix = pack["paper_publishability_matrix"]

    assert set(pack) == set(PAPER_TABLE_FILENAMES)
    assert table["status"] == "tables_generated_claim_guarded"
    assert table["paper_can_continue_to_p11"] is True
    assert audit["status"] == "pass"
    assert audit["paper_can_continue_to_p11"] is True
    assert audit["numeric_cell_count"] > 10
    assert matrix["hard_claims_allowed"] is False
    assert matrix["headline_claims_allowed"] is False
    assert "relaytic release-safety paper-tables --format json" in pack["paper_reproduction_commands"]

    required = {
        "dataset_id",
        "split",
        "command",
        "run_directory_ref",
        "artifact_ref",
        "claim_state",
        "budget_tier",
        "leakage_posture",
        "publishability_gate_ref",
        "publishability_gate_status",
    }
    for cell in audit["numeric_cells"]:
        assert required.issubset(cell), cell["cell_id"]
        assert all(cell[field] not in (None, "", []) for field in required), cell["cell_id"]
    assert any(cell["budget_tier"] == "competitive" for cell in audit["numeric_cells"])
    assert all(not cell["headline_metric_candidate"] for cell in audit["numeric_cells"])
    paysim_gate = next(row for row in matrix["rows"] if row["dataset_id"] == "paysim_temporal_transaction_fraud")
    assert "graph_benchmark_evidence_not_yet_executed_p7_required" not in paysim_gate["blocked_reason_codes"]


def test_paper_track_p10_fails_closed_without_p9_guard(tmp_path: Path) -> None:
    pack = build_paper_table_pack(tmp_path)

    table = pack["paper_result_table_final"]
    audit = pack["paper_metric_cell_audit"]

    assert table["status"] == "blocked_pending_p9_operational_pack"
    assert table["paper_can_continue_to_p11"] is False
    assert audit["status"] == "blocked"
    assert audit["paper_can_continue_to_p11"] is False


def test_paper_track_p10_cli_writes_json_and_markdown(
    tmp_path: Path,
    capsys: Any,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _write_p10_input_reports(tmp_path)
    output_dir = tmp_path / "reports"
    monkeypatch.chdir(tmp_path)

    exit_code = main(
        [
            "release-safety",
            "paper-tables",
            "--output-dir",
            str(output_dir),
            "--format",
            "json",
        ]
    )

    assert exit_code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["status"] == "tables_generated_claim_guarded"
    assert payload["paper_metric_cell_audit"]["status"] == "pass"
    assert (output_dir / "paper_result_table_final.json").exists()
    assert (output_dir / "paper_reproduction_commands.md").exists()


def test_paper_track_p10_committed_reports_are_ready_for_p11() -> None:
    for filename in PAPER_TABLE_FILENAMES.values():
        assert (REPORT_DIR / filename).exists(), filename

    table = _load_report("paper_result_table_final.json")
    audit = _load_report("paper_metric_cell_audit.json")
    matrix = _load_report("paper_publishability_matrix.json")

    assert table["status"] == "tables_generated_claim_guarded"
    assert table["paper_can_continue_to_p11"] is True
    assert audit["status"] == "pass"
    assert audit["violations"] == []
    assert audit["headline_metric_cell_count"] == 0
    assert matrix["status"] == "supporting_tables_ready_hard_claims_blocked"
    assert matrix["hard_claims_allowed"] is False
    assert matrix["headline_claims_allowed"] is False

    paysim = next(row for row in matrix["rows"] if row["dataset_id"] == "paysim_temporal_transaction_fraud")
    assert "graph_benchmark_evidence_not_yet_executed_p7_required" not in paysim["blocked_reason_codes"]
    assert any(cell["metric_id"] == "test_pr_auc" and cell["budget_tier"] == "competitive" for cell in audit["numeric_cells"])
    assert any(cell["dataset_id"] == "elliptic2_subgraph_aml" for cell in audit["numeric_cells"])
