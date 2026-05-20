from __future__ import annotations

import json
from pathlib import Path

from relaytic.release_safety import (
    PAPER_THESIS_DOC_FILENAME,
    PAPER_THESIS_FILENAMES,
    build_paper_thesis_pack,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = PROJECT_ROOT / "docs" / "reports"
PAPER_DIR = PROJECT_ROOT / "docs" / "paper"


def _load_report(name: str) -> dict[str, object]:
    return json.loads((REPORT_DIR / name).read_text(encoding="utf-8"))


def test_paper_track_p2_freezes_thesis_contract_before_benchmarks() -> None:
    generated = build_paper_thesis_pack(PROJECT_ROOT)
    contract = generated["paper_thesis_contract"]
    taxonomy = generated["paper_claim_taxonomy"]
    related_work = generated["paper_related_work_seed"]

    assert contract["schema_version"] == "relaytic.paper_thesis_contract.v1"
    assert contract["slice"] == "Paper Track P2"
    assert contract["status"] == "thesis_contract_frozen"
    assert contract["paper_title"].startswith("Relaytic-AML:")
    assert contract["paper_type"] == "systems_and_benchmark_evaluation"
    assert contract["next_slice"] == "Paper Track P3"
    assert contract["claim_taxonomy_agrees_with_release_freeze"] is True

    assert len(contract["research_questions"]) >= 4
    assert len(contract["contributions"]) >= 4
    assert "pr_auc" in contract["metric_doctrine"]["primary_metrics"]
    assert "precision_at_k" in contract["metric_doctrine"]["primary_metrics"]
    assert "case_packet_completeness" in contract["metric_doctrine"]["operational_metrics"]

    claim_ids = {claim["claim_id"]: claim for claim in taxonomy["claims"]}
    assert claim_ids["claim_sota_or_hard_aml_superiority"]["boundary"] == "blocked"
    assert claim_ids["claim_subgraph_or_synthetic_bank_graph"]["boundary"] == "blocked"
    assert taxonomy["hard_performance_claims_allowed"] is False

    source_ids = {source["source_id"] for source in related_work["sources"]}
    assert {
        "elliptic_bitcoin_aml_2019",
        "elliptic2_subgraph_2024",
        "amlsim_amlworld_neurips_2023",
        "paysim_2016",
        "tabpfn_nature_2025",
        "dgraph_finance_graph_2022",
        "paperbench_2025",
        "mlr_bench_2025",
    } <= source_ids


def test_paper_track_p2_claim_taxonomy_matches_claim_boundary_report() -> None:
    claim_boundary = _load_report("paper_claim_boundary_report.json")
    generated = build_paper_thesis_pack(PROJECT_ROOT)
    taxonomy = generated["paper_claim_taxonomy"]

    source_boundaries = {
        claim["claim_id"]: claim["boundary"] for claim in claim_boundary["claims"]  # type: ignore[index]
    }
    taxonomy_boundaries = {
        claim["claim_id"]: claim["boundary"] for claim in taxonomy["claims"]
    }

    assert taxonomy["taxonomy_agrees_with_claim_boundary_report"] is True
    assert taxonomy["source_claim_boundary_status"] == "claim_boundaries_frozen"
    assert taxonomy_boundaries == source_boundaries


def test_paper_track_p2_committed_artifacts_match_generated_contract() -> None:
    generated = build_paper_thesis_pack(PROJECT_ROOT)
    for key, filename in PAPER_THESIS_FILENAMES.items():
        committed = _load_report(filename)
        assert committed == generated[key], filename

    committed_markdown = (PAPER_DIR / PAPER_THESIS_DOC_FILENAME).read_text(encoding="utf-8")
    assert committed_markdown == generated["paper_thesis_markdown"]
    assert "# Relaytic-AML:" in committed_markdown
    assert "## Claim Boundaries" in committed_markdown
