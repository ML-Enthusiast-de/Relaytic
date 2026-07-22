from __future__ import annotations

import json
from pathlib import Path

import pytest

from relaytic.release_safety.paper_evidence_contract import (
    INVARIANT_EVIDENCE_CELL_TYPE,
    METRIC_EVIDENCE_CELL_REQUIRED_FIELDS,
    METRIC_EVIDENCE_CELL_TYPE,
    MISSING_FIELD_STRESS_FIXTURE_OMITTED_FIELDS,
    PAPER_INVARIANT_EVIDENCE_CELL_SCHEMA_VERSION,
    PAPER_METRIC_EVIDENCE_CELL_SCHEMA_VERSION,
    build_evidence_schema_contract,
    evidence_cell_violations,
)
from relaytic.release_safety.paper_release import build_paper_release_pack


PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = PROJECT_ROOT / "docs" / "reports"
pytestmark = pytest.mark.prepush


def _metric_cell() -> dict[str, object]:
    return {
        "cell_schema": PAPER_METRIC_EVIDENCE_CELL_SCHEMA_VERSION,
        "cell_id": "fixture.metric",
        "cell_type": METRIC_EVIDENCE_CELL_TYPE,
        "dataset_id": "fixture",
        "split": "test",
        "command": "relaytic fixture",
        "artifact_ref": "fixture.json",
        "artifact_field": "test_pr_auc",
        "budget_tier": "fixture",
        "leakage_posture": "fixture_only",
        "metric": "pr_auc",
        "value": 0.5,
        "operating_point_applicability": "not_applicable",
        "operating_point_ref": "not_applicable",
        "calibration_status": "not_recorded",
        "exposure_status": "fixture_only",
        "model_identifier": "fixture_model",
    }


def _invariant_cell() -> dict[str, object]:
    return {
        "cell_schema": PAPER_INVARIANT_EVIDENCE_CELL_SCHEMA_VERSION,
        "cell_id": "fixture.invariant",
        "cell_type": INVARIANT_EVIDENCE_CELL_TYPE,
        "dataset_id": "fixture",
        "split": "not_applicable",
        "command": "relaytic fixture",
        "artifact_ref": "fixture.json",
        "artifact_field": "accepted",
        "budget_tier": "deterministic_fixture",
        "leakage_posture": "rowless_fixture",
        "invariant_name": "metadata_complete",
        "invariant_state": "pass",
        "observed_value": True,
        "detector_performance_metric": False,
        "operating_point_applicability": "not_applicable",
        "rowless_export_status": "rowless",
    }


def test_p27_typed_evidence_contract_rejects_schema_conflation() -> None:
    assert evidence_cell_violations(_metric_cell()) == []
    assert evidence_cell_violations(_invariant_cell()) == []

    untyped = dict(_metric_cell())
    untyped.pop("cell_type")
    assert any(row["violation"] == "untyped_evidence_cell" for row in evidence_cell_violations(untyped))

    missing_operating_point = dict(_metric_cell())
    missing_operating_point.pop("operating_point_ref")
    assert any(
        row["violation"] == "required_factual_fields_missing"
        and "operating_point_ref" in row["fields"]
        for row in evidence_cell_violations(missing_operating_point)
    )

    detector_invariant = {**_invariant_cell(), "metric": "pr_auc", "value": 1.0}
    assert any(
        row["violation"] == "invariant_rendered_as_detector_performance"
        for row in evidence_cell_violations(detector_invariant)
    )


def test_p27_schema_counts_have_one_authoritative_source() -> None:
    contract = build_evidence_schema_contract()

    assert contract["cell_types"][METRIC_EVIDENCE_CELL_TYPE]["required_field_count"] == len(
        METRIC_EVIDENCE_CELL_REQUIRED_FIELDS
    )
    assert contract["fixtures"]["disabled_required_fields_ablation"]["removed_field_count"] == len(
        METRIC_EVIDENCE_CELL_REQUIRED_FIELDS
    )
    assert contract["fixtures"]["missing_field_stress_fixture"]["omitted_field_count"] == len(
        MISSING_FIELD_STRESS_FIXTURE_OMITTED_FIELDS
    )


def test_p27_paysim_contracts_and_elliptic2_reference_are_truthful() -> None:
    p6 = json.loads((REPORT_DIR / "paper_leakage_safe_feature_report.json").read_text(encoding="utf-8"))
    p6a = json.loads((REPORT_DIR / "paysim_leakage_safe_feature_report.json").read_text(encoding="utf-8"))
    reference = json.loads(
        (REPORT_DIR / "elliptic2_revclassify_reference_scorecard.json").read_text(encoding="utf-8")
    )

    assert p6["dataset_id"] == p6a["dataset_id"]
    assert p6["split_contract_id"] == p6a["split_contract_id"]
    assert p6["feature_contract_id"] != p6a["feature_contract_id"]
    assert set(p6["feature_columns"]) != set(p6a["feature_columns"])
    assert reference["reference"]["RevClassify_DS"]["pr_auc"] == pytest.approx(0.974)
    assert "Table 1" in reference["reference"]["source"]
    assert reference["reference"]["versioned_pdf_url"].endswith("2410.08394v1")


def test_p27_candidate_manuscript_does_not_claim_a_source_revision() -> None:
    draft = build_paper_release_pack(PROJECT_ROOT)["paper_final_draft"]

    assert "This review candidate does not claim an archival revision." in draft
    assert "Source commit:" not in draft
    assert "same dataset, split, feature, and metric contract" not in draft
