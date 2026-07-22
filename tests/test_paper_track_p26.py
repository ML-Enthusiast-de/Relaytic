from __future__ import annotations

import json
from pathlib import Path

import pytest

from relaytic.release_safety import build_paper_release_integrity_pack
from relaytic.release_safety.paper_evidence_contract import (
    METRIC_EVIDENCE_CELL_TYPE,
    PAPER_CLAIM_GATE_SCHEMA_VERSION,
    PAPER_METRIC_EVIDENCE_CELL_SCHEMA_VERSION,
    audit_evidence_gate_separation,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = PROJECT_ROOT / "docs" / "reports"
PAPER_PATH = PROJECT_ROOT / "docs" / "paper" / "relaytic_aml_arxiv_draft.md"
pytestmark = pytest.mark.prepush


def _factual_cell() -> dict[str, object]:
    return {
        "cell_schema": PAPER_METRIC_EVIDENCE_CELL_SCHEMA_VERSION,
        "cell_id": "fixture.metric",
        "cell_type": METRIC_EVIDENCE_CELL_TYPE,
        "dataset_id": "fixture",
        "split": "test",
        "command": "relaytic fixture",
        "artifact_ref": "fixture.json",
        "artifact_field": "pr_auc",
        "metric": "pr_auc",
        "value": 0.5,
        "budget_tier": "fixture",
        "leakage_posture": "fixture_only",
        "operating_point_applicability": "not_applicable",
        "operating_point_ref": "not_applicable",
        "calibration_status": "not_recorded",
        "exposure_status": "fixture_only",
        "model_identifier": "fixture_model",
    }


def _gate(*, cell_ids: list[str] | None = None) -> dict[str, object]:
    return {
        "schema_version": PAPER_CLAIM_GATE_SCHEMA_VERSION,
        "gate_id": "fixture.publication_gate",
        "evidence_cell_ids": cell_ids or ["fixture.metric"],
        "admissible_use": "schema test only",
        "stronger_claim_status": "blocked",
        "gate_reasons": ["fixture evidence has no detector-performance scope"],
        "missing_evidence": ["benchmark evidence"],
    }


def test_p26_rejects_interpretation_merged_into_evidence_cell() -> None:
    cell = {**_factual_cell(), "claim_state": "supporting_only"}

    audit = audit_evidence_gate_separation(evidence_cells=[cell], claim_gates=[_gate()])

    assert audit["status"] == "fail"
    violation = next(row for row in audit["violations"] if row["violation"] == "interpretive_fields_in_evidence_cell")
    assert violation["fields"] == ["claim_state"]

    nested = {
        **_factual_cell(),
        "release_record": {"admissible_use": "supporting-only"},
    }
    nested_audit = audit_evidence_gate_separation(evidence_cells=[nested], claim_gates=[_gate()])
    nested_violation = next(
        row for row in nested_audit["violations"] if row["violation"] == "interpretive_fields_in_evidence_cell"
    )
    assert nested_violation["fields"] == ["release_record.admissible_use"]


def test_p26_rejects_ungated_public_cell_and_dangling_gate_reference() -> None:
    ungated = audit_evidence_gate_separation(evidence_cells=[_factual_cell()], claim_gates=[])
    dangling = audit_evidence_gate_separation(
        evidence_cells=[_factual_cell()],
        claim_gates=[_gate(cell_ids=["missing.metric"])],
    )

    assert ungated["status"] == "fail"
    assert any(row["violation"] == "public_evidence_cells_without_separate_gate" for row in ungated["violations"])
    assert dangling["status"] == "fail"
    assert any(row["violation"] == "gate_references_missing_evidence_cells" for row in dangling["violations"])


def test_p26_committed_cells_and_gates_are_strictly_separate() -> None:
    audit = json.loads((REPORT_DIR / "paper_p26_evidence_gate_separation_audit.json").read_text(encoding="utf-8"))

    assert audit["status"] == "pass"
    assert audit["metric_evidence_cell_schema"] == PAPER_METRIC_EVIDENCE_CELL_SCHEMA_VERSION
    assert audit["evidence_cell_type_counts"]["metric_evidence_cell"] > 0
    assert audit["evidence_cell_type_counts"]["invariant_evidence_cell"] > 0
    assert audit["interpretive_gate_schema"] == PAPER_CLAIM_GATE_SCHEMA_VERSION
    assert all(audit["checks"].values())
    assert audit["violations"] == []


def test_p26_validation_subsplits_and_reader_disclosure_reconcile() -> None:
    pack = build_paper_release_integrity_pack(PROJECT_ROOT)
    audit = pack["paper_p26_validation_subsplit_audit"]
    paper = PAPER_PATH.read_text(encoding="utf-8")

    assert audit["status"] == "pass"
    assert all(row["passed"] for row in audit["checks"])
    assert audit["datasets"]["PaySim"]["calibration"] == {
        "boundary": "446-540",
        "count": 116502,
        "positive_count": 984,
    }
    assert audit["datasets"]["PaySim"]["threshold_selection"] == {
        "boundary": "541-594",
        "count": 111601,
        "positive_count": 568,
    }
    assert audit["datasets"]["Elliptic"]["calibration"] == {
        "boundary": "30-35",
        "count": 4854,
        "positive_count": 773,
    }
    assert audit["datasets"]["Elliptic"]["threshold_selection"] == {
        "boundary": "36-39",
        "count": 4145,
        "positive_count": 265,
    }
    assert "Threshold-selection queue" in paper
    assert "full validation partition selected" in paper


def test_p26_finalist_release_and_reader_language_are_consistent() -> None:
    pack = build_paper_release_integrity_pack(PROJECT_ROOT)
    release = pack["paper_p26_release_reference_audit"]
    paper = PAPER_PATH.read_text(encoding="utf-8")
    lower = paper.lower()

    assert release["status"] == "pass"
    assert release["paper_claims_release_tag"] is False
    assert release["release_identity_mode"] == "immutable_commit"
    assert "joint XGBoost and Random Forest runner-up rows" in paper
    assert "all finalist scores are distinct" not in lower
    assert "review draft" not in lower
    assert "review build" not in lower
    assert "platt_sigmoid" not in paper
    assert "beside a published RevClassifyDS reference" not in paper
    assert "alongside a published RevClassifyDS reference" in paper
    assert "PaySim test partition was an untouched holdout" not in paper
    assert "fixed but not an untouched holdout" in paper
    assert "confirmatory rather than blind or untouched evidence" in paper
