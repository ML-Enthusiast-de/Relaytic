from __future__ import annotations

import json
from pathlib import Path
import re


PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = PROJECT_ROOT / "docs" / "reports"
PAPER_PATH = PROJECT_ROOT / "docs" / "paper" / "relaytic_aml_arxiv_draft.md"
LATEX_PATH = PROJECT_ROOT / "docs" / "paper" / "arxiv_src" / "main.tex"
PROVENANCE_LIMITATION_PATH = REPORT_DIR / "elliptic2_cohort_provenance_limitation.md"
PINNED_DATA_DF_SHA256 = "2baa712b67382aeade8d5e72dd07ddbffb1029b359a048c80a2300a3e3abc220"


def _read_json(filename: str) -> dict[str, object]:
    return json.loads((REPORT_DIR / filename).read_text(encoding="utf-8"))


def test_elliptic2_evaluable_cohort_counts_are_internally_consistent() -> None:
    contract = _read_json("elliptic2_modern_reference_contract.json")
    partition = contract["partition_summary"]
    assert isinstance(partition, dict)
    split_rows = partition["split_rows"]
    assert isinstance(split_rows, dict)

    row_counts = [int(split_rows[name]["row_count"]) for name in ("TRN", "VAL", "TST")]
    positive_counts = [int(split_rows[name]["positive_count"]) for name in ("TRN", "VAL", "TST")]

    assert row_counts == [88_738, 11_059, 11_105]
    assert sum(row_counts) == int(partition["row_count"]) == 110_902
    assert positive_counts == [2_054, 252, 272]
    assert sum(positive_counts) == 2_578


def test_elliptic2_row_level_relationship_remains_explicitly_unproven() -> None:
    reconciliation = _read_json("elliptic2_evaluable_cohort_reconciliation.json")

    assert reconciliation["full_core_equivalence_proven"] is False
    assert reconciliation["official_core_subgraph_count"] == 121_810
    assert reconciliation["official_core_positive_count"] == 2_763
    assert reconciliation["revtrack_evaluable_row_count"] == 110_902
    assert reconciliation["revtrack_evaluable_positive_count"] == 2_578
    assert "full_core_row_mapping_not_proven" in reconciliation["blocked_reason_codes"]
    assert PROVENANCE_LIMITATION_PATH.is_file()
    assert not (PROJECT_ROOT / "ELLIPTIC2_COHORT_BLOCKER.md").exists()

    limitation = PROVENANCE_LIMITATION_PATH.read_text(encoding="utf-8")
    assert "underlying upstream-provenance gap remains unresolved" in limitation
    assert "explicitly non-comparable, pinned-artifact context claim" in limitation
    assert PINNED_DATA_DF_SHA256 in limitation


def test_elliptic2_paper_scope_is_pinned_non_comparable_and_directly_cited() -> None:
    paper = PAPER_PATH.read_text(encoding="utf-8")
    abstract = paper.split("## 1. Introduction", 1)[0]

    assert all(value not in abstract for value in ("Elliptic2", "0.9432", "0.9297", "0.9740"))
    assert "Across the tested system fixtures" in abstract
    assert "0.9740" not in paper
    assert "hard and headline claims blocked" not in paper
    assert "privacy boundary that lets outside agents help" not in paper
    assert paper.count(PINNED_DATA_DF_SHA256) == 1

    protocol_blocks = [
        block
        for block in re.split(r"\n\s*\n", paper)
        if "Three documented count states remain distinct" in block
    ]
    assert len(protocol_blocks) == 1
    protocol = protocol_blocks[0]
    assert "a local audit of the current core records 121,810 subgraphs and 2,763 positives" in protocol
    assert "RevTrack paper reports 121,810 subgraphs and 2,718 positives [@song2024revtrack]" in protocol
    assert "pinned artifact contains 110,902 rows and 2,578 positives" in protocol
    assert "does not explain these count or label differences" in protocol

    assert "neither a blind holdout result nor a reproduction or parity claim" in paper
    assert "No numerical comparison with published RevClassifyDS performance is made" in paper

    for phrase in (
        "after preprocessing",
        "after filtering",
        "filtered subset",
        "derived from the current core",
        "cleaned cohort",
        "matched cohort",
        "cohort parity",
        "reference parity established",
        "full-core equivalence",
    ):
        assert phrase not in paper.lower()


def test_elliptic2_external_value_is_not_repeated_in_paper_figures() -> None:
    figure_dir = PROJECT_ROOT / "docs" / "paper" / "figures"
    for figure in figure_dir.glob("*.svg"):
        content = figure.read_text(encoding="utf-8")
        assert "0.9740" not in content
        assert "RevClassifyDS" not in content
    figure4 = (figure_dir / "figure_3_review_budget.svg").read_text(encoding="utf-8")
    for token in ("Elliptic2", "0.9432", "0.9297"):
        assert token not in figure4


def test_elliptic2_provenance_audit_uses_repository_relative_refs() -> None:
    audit = _read_json("paper_p24_reference_provenance_audit.json")
    checks = audit["checks"]
    assert isinstance(checks, list)
    limitation_check = next(
        check
        for check in checks
        if isinstance(check, dict) and check.get("check") == "durable provenance limitation present"
    )
    assert limitation_check["observed"] == "docs/reports/elliptic2_cohort_provenance_limitation.md"


def test_final_typesetting_corrections_are_present_in_generated_latex() -> None:
    paper = PAPER_PATH.read_text(encoding="utf-8")
    latex = LATEX_PATH.read_text(encoding="utf-8")

    assert "*Table note:*" not in paper
    assert "*Note.* The E2 row" in paper
    assert r"\emph{Note.} The E2 row" in latex
    assert "*Table note:*" not in latex

    json_listings = re.findall(
        r"\\begin\{Verbatim\}\[([^]]*breaksymbolleft=\{\}[^]]*)\](.*?)\\end\{Verbatim\}",
        latex,
        flags=re.DOTALL,
    )
    assert len(json_listings) >= 4
    assert all("\\hookrightarrow" not in body and "↪" not in body for _, body in json_listings)

    assert r"\mbox{\nolinkurl{paper-final-preflight}}" in latex
    assert "0.9740" not in latex
    assert not re.search(r"\b(?:we|our|ours|us)\b", paper, flags=re.IGNORECASE)
