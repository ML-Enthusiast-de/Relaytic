from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from relaytic.release_safety import PAPER_DRAFT_FILENAMES, PAPER_FIGURE_FILENAMES, build_paper_draft_pack
from relaytic.ui.cli import main


PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = PROJECT_ROOT / "docs" / "reports"
PAPER_DIR = PROJECT_ROOT / "docs" / "paper"
pytestmark = pytest.mark.prepush


def _write_p11_input_reports(root: Path) -> None:
    reports = root / "docs" / "reports"
    reports.mkdir(parents=True, exist_ok=True)
    _write_json(
        reports / "paper_thesis_contract.json",
        {
            "schema_version": "relaytic.paper_thesis_contract.v1",
            "status": "thesis_contract_frozen",
            "paper_title": "Relaytic-AML: Claim-Gated Evaluation Environments for Temporal Graph Financial-Crime ML",
            "thesis": "Relaytic-AML is a local-first, claim-gated evaluation environment.",
        },
    )
    _write_json(
        reports / "paper_claim_taxonomy.json",
        {
            "schema_version": "relaytic.paper_thesis_contract.v1",
            "status": "claim_taxonomy_frozen",
            "claims": [
                {"claim_id": "claim_release_freeze_pack_exists", "boundary": "hard"},
                {"claim_id": "claim_paysim_temporal_transaction_fraud", "boundary": "supporting-only"},
                {"claim_id": "claim_elliptic_flattened_graph_aml", "boundary": "supporting-only"},
                {"claim_id": "claim_sota_or_hard_aml_superiority", "boundary": "blocked"},
            ],
        },
    )
    _write_json(
        reports / "paper_related_work_seed.json",
        {
            "status": "related_work_seed_frozen",
            "sources": [
                {
                    "title": "Anti-Money Laundering in Bitcoin",
                    "url": "https://arxiv.org/abs/1908.02591",
                    "paper_relevance": "Temporal graph AML benchmark pressure.",
                }
            ],
        },
    )
    _write_json(reports / "paper_dataset_registry.json", {"status": "dataset_registry_frozen"})
    _write_json(reports / "paper_split_contracts.json", {"status": "split_contracts_frozen"})
    _write_json(
        reports / "paper_p8d_thesis_decision.json",
        {
            "status": "accepted_thesis_narrowing",
            "hard_aml_claim_allowed": False,
            "headline_or_sota_claim_allowed": False,
        },
    )
    _write_json(reports / "paper_p8d_evidence_role_matrix.json", {"status": "evidence_roles_frozen"})
    _write_json(
        reports / "paper_result_table_final.json",
        {
            "schema_version": "relaytic.paper_table_generator.v1",
            "status": "tables_generated_claim_guarded",
            "paper_can_continue_to_p11": True,
            "table_groups": [
                {
                    "table_id": "supporting_performance_table",
                    "rows": [
                        {
                            "row_id": "paysim_p6a_competitive_selected",
                            "dataset_id": "paysim_temporal_transaction_fraud",
                            "dataset_display_name": "PaySim synthetic mobile-money transaction fraud",
                            "evidence_role": "supporting_temporal_proxy_numeric_candidate",
                            "budget_tier": "competitive",
                            "claim_state": "supporting-only",
                            "publishability_gate_status": "pass_supporting_only",
                        }
                    ],
                }
            ],
        },
    )
    cells = [
        _cell("paysim_p6_validation_selected_baseline.test_pr_auc", 0.331345),
        _cell("paysim_p6a_competitive_selected.test_pr_auc", 0.638773),
        _cell("paysim_p6a_competitive_selected.precision_at_review_budget", 0.703336),
        _cell("paysim_p6a_competitive_selected.recall_at_review_budget", 0.471584),
        _cell("elliptic_p7_selected_graph_feature_baseline.test_pr_auc", 0.668756),
        _cell("elliptic_p7_selected_graph_feature_baseline.precision_at_review_budget", 1.0),
        _cell("elliptic_p7_selected_graph_feature_baseline.recall_at_review_budget", 0.056604),
        _cell("elliptic2_p8b_modern_context.official_partition_test_pr_auc_mean", 0.94324),
        _cell("elliptic2_p8b_modern_context.published_reference_pr_auc", 0.974),
    ]
    _write_json(
        reports / "paper_metric_cell_audit.json",
        {
            "schema_version": "relaytic.paper_table_generator.v1",
            "status": "pass",
            "paper_can_continue_to_p11": True,
            "numeric_cells": cells,
            "violations": [],
        },
    )
    _write_json(reports / "paper_table_provenance.json", {"status": "provenance_materialized", "cell_provenance": []})
    _write_json(
        reports / "paper_publishability_matrix.json",
        {
            "schema_version": "relaytic.paper_table_generator.v1",
            "status": "supporting_tables_ready_hard_claims_blocked",
            "paper_can_continue_to_p11": True,
            "hard_claims_allowed": False,
            "headline_claims_allowed": False,
            "rows": [
                {
                    "dataset_id": "paysim_temporal_transaction_fraud",
                    "gate_status": "pass_supporting_only",
                    "supporting_table_allowed": True,
                    "headline_claim_allowed": False,
                    "hard_claim_allowed": False,
                    "blocked_reason_codes": ["paysim_is_supporting_proxy_not_real_bank_holdout"],
                },
                {
                    "dataset_id": "elliptic_flattened_graph_aml",
                    "gate_status": "pass_supporting_only",
                    "supporting_table_allowed": True,
                    "headline_claim_allowed": False,
                    "hard_claim_allowed": False,
                    "blocked_reason_codes": ["graph_sota_claim_not_benchmarked"],
                },
                {
                    "dataset_id": "elliptic2_subgraph_aml",
                    "gate_status": "pass_supporting_modern_context_only",
                    "supporting_table_allowed": True,
                    "headline_claim_allowed": False,
                    "hard_claim_allowed": False,
                    "blocked_reason_codes": ["entity_disjoint_generalization_not_yet_proven"],
                },
                {
                    "dataset_id": "paper_operational_layer",
                    "gate_status": "supporting_operational_metrics_ready_hard_claims_blocked",
                    "supporting_table_allowed": True,
                    "headline_claim_allowed": False,
                    "hard_claim_allowed": False,
                    "blocked_reason_codes": ["paper_benchmark_case_packets_missing"],
                },
            ],
        },
    )
    _write_json(
        reports / "paper_operational_claim_guard.json",
        {
            "status": "supporting_operational_metrics_ready_hard_claims_blocked",
            "blocked_reason_codes": ["paper_benchmark_case_packets_missing"],
        },
    )
    _write_json(
        reports / "elliptic2_reference_parity_gate.json",
        {
            "status": "blocked_supporting_only_thesis_narrowing_required",
            "blocked_reason_codes": ["official_revclassify_classification_checkpoints_not_distributed"],
        },
    )
    _write_json(reports / "elliptic2_repeated_seed_scorecard.json", {"status": "complete"})
    (reports / "paper_reproduction_commands.md").write_text(
        "# Commands\n\n```powershell\nrelaytic release-safety paper-tables --format json\n```\n",
        encoding="utf-8",
    )


def _cell(cell_id: str, value: float) -> dict[str, Any]:
    row_id, metric_id = cell_id.rsplit(".", 1)
    return {
        "cell_schema": "paper_metric_cell.v1",
        "cell_id": cell_id,
        "row_id": row_id,
        "metric_id": metric_id,
        "value": value,
        "dataset_id": "test_dataset",
        "split": "test",
        "command": "relaytic release-safety paper-tables --format json",
        "run_directory_ref": "docs/reports",
        "artifact_ref": "docs/reports/paper_metric_cell_audit.json",
        "claim_state": "supporting-only",
        "budget_tier": "competitive",
        "leakage_posture": "test",
        "publishability_gate_ref": "docs/reports/paper_publishability_matrix.json",
        "publishability_gate_status": "pass_supporting_only",
        "headline_metric_candidate": False,
    }


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _load_report(name: str) -> dict[str, Any]:
    return json.loads((REPORT_DIR / name).read_text(encoding="utf-8"))


def test_paper_track_p11_builds_claim_linted_draft_and_figures(tmp_path: Path) -> None:
    _write_p11_input_reports(tmp_path)

    pack = build_paper_draft_pack(tmp_path)
    draft = pack["paper_draft"]
    lint = pack["paper_claim_lint_report"]
    limitations = pack["paper_limitations_matrix"]
    manifest = pack["paper_figure_manifest"]

    assert lint["status"] == "pass"
    assert lint["paper_can_continue_to_p12"] is True
    assert lint["hard_claims_allowed"] is False
    assert lint["headline_claims_allowed"] is False
    for section in ["Abstract", "Introduction", "Related Work", "Method", "Benchmarks", "Results", "Limitations", "Reproducibility Appendix"]:
        assert f"## {section}" in draft
    for limitation in limitations["limitations"]:
        assert limitation["limitation_id"] in draft
    assert len(manifest["figures"]) == len(PAPER_FIGURE_FILENAMES)
    assert all(item["source_type"] in {"artifact_generated", "schematic_explicit"} for item in manifest["figures"])
    assert all(svg.startswith("<svg") for svg in pack["figures"].values())
    assert "leaderboard winner" not in draft.lower()


def test_paper_track_p11_cli_writes_draft_reports_and_figures(
    tmp_path: Path,
    capsys: Any,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _write_p11_input_reports(tmp_path)
    paper_dir = tmp_path / "paper"
    output_dir = tmp_path / "reports"
    monkeypatch.chdir(tmp_path)

    exit_code = main(
        [
            "release-safety",
            "paper-draft",
            "--paper-dir",
            str(paper_dir),
            "--output-dir",
            str(output_dir),
            "--format",
            "json",
        ]
    )

    assert exit_code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["status"] == "pass"
    assert payload["paper_claim_lint_report"]["paper_can_continue_to_p12"] is True
    assert (paper_dir / "relaytic_aml_draft.md").exists()
    assert (paper_dir / "figures" / "figure_manifest.json").exists()
    for filename in PAPER_FIGURE_FILENAMES.values():
        assert (paper_dir / "figures" / filename).exists()
    for filename in PAPER_DRAFT_FILENAMES.values():
        assert (output_dir / filename).exists()


def test_paper_track_p11_committed_reports_are_claim_linted() -> None:
    assert (PAPER_DIR / "relaytic_aml_draft.md").exists()
    assert (PAPER_DIR / "figures" / "figure_manifest.json").exists()
    for filename in PAPER_FIGURE_FILENAMES.values():
        assert (PAPER_DIR / "figures" / filename).exists()

    lint = _load_report("paper_claim_lint_report.json")
    limitations = _load_report("paper_limitations_matrix.json")
    draft = (PAPER_DIR / "relaytic_aml_draft.md").read_text(encoding="utf-8")

    assert lint["status"] == "pass"
    assert lint["violations"] == []
    assert lint["paper_can_continue_to_p12"] is True
    assert lint["hard_claims_allowed"] is False
    assert lint["headline_claims_allowed"] is False
    assert limitations["status"] == "limitations_materialized_claims_guarded"
    assert limitations["limitation_count"] >= 5
    assert "paper-cell:paysim_p6a_competitive_selected.test_pr_auc" in draft
    assert "paper-cell:elliptic_p7_selected_graph_feature_baseline.test_pr_auc" in draft
