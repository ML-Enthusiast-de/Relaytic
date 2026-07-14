from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from relaytic.release_safety import (
    PAPER_EXTERNAL_SCORE_FILENAMES,
    build_paper_external_score_pack,
)
from relaytic.release_safety.paper_evidence_contract import EVIDENCE_CELL_INTERPRETIVE_FIELDS
from relaytic.ui.cli import main


PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = PROJECT_ROOT / "docs" / "reports"
pytestmark = pytest.mark.prepush


def _load_report(name: str) -> dict[str, Any]:
    return json.loads((REPORT_DIR / name).read_text(encoding="utf-8"))


def test_paper_track_p19a_builds_external_score_proof_pack() -> None:
    pack = build_paper_external_score_pack(PROJECT_ROOT)

    manifest = pack["paper_external_score_manifest"]
    schema = pack["paper_external_score_schema"]
    cells = pack["paper_external_score_evidence_cells"]
    gate = pack["paper_external_score_claim_gate"]
    handoff = pack["paper_external_score_handoff_eval"]
    route = pack["paper_external_score_route_decision"]
    serialized = json.dumps(pack, sort_keys=True)

    assert manifest["status"] == "ready_for_hosted_score_governance"
    assert not manifest["failed_checks"]
    assert route["selected_route"] == "external_score_file_adapter"
    assert schema["accepted"] is True
    assert schema["required_metadata_completeness"] == 1.0
    assert schema["rowless_input"] is True
    assert schema["metric"]["detector_performance_metric"] is False
    assert cells["evidence_cell_count"] == 1
    assert cells["evidence_cells"][0]["cell_id"] == "p19a.external_score.hosted_metadata_completeness"
    assert not EVIDENCE_CELL_INTERPRETIVE_FIELDS.intersection(cells["evidence_cells"][0])
    assert cells["evidence_gate_separation"]["status"] == "pass"
    assert gate["gate_id"] == "p19a.external_score.hosted_output_gate"
    assert gate["evidence_cell_ids"] == ["p19a.external_score.hosted_metadata_completeness"]
    assert gate["admissible_use"] == "hosted detector-output governance only"
    assert gate["stronger_claim_status"] == "blocked"
    assert gate["publishable"] is True
    assert gate["allowed_claim_scope"] == "hosted_detector_output_governance_only"
    assert not gate["detector_superiority_claimed"]
    assert not gate["production_aml_readiness_claimed"]
    assert not gate["graph_neural_detector_novelty_claimed"]
    assert not gate["revclassify_parity_claimed"]
    assert not gate["hard_real_bank_aml_superiority_claimed"]
    assert handoff["rowless_handoff_passed"] is True
    assert handoff["raw_rows_exported"] is False
    assert handoff["entity_identifiers_exported"] is False
    assert handoff["private_paths_exported"] is False
    assert handoff["unapproved_score_payload_fields_exported"] is False
    assert str(PROJECT_ROOT).replace("\\", "/") not in serialized.replace("\\", "/")


def test_paper_track_p19a_cli_writes_reports(
    tmp_path: Path,
    capsys: Any,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    output_dir = tmp_path / "reports"
    monkeypatch.chdir(PROJECT_ROOT)

    exit_code = main(
        [
            "release-safety",
            "paper-external-score-proof",
            "--output-dir",
            str(output_dir),
            "--format",
            "json",
        ]
    )

    assert exit_code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["status"] == "ready_for_hosted_score_governance"
    assert payload["paper_external_score_manifest"]["status"] == "ready_for_hosted_score_governance"
    assert payload["paper_external_score_schema"]["accepted"] is True
    assert payload["paper_external_score_claim_gate"]["publishable"] is True
    assert payload["paper_external_score_handoff_eval"]["rowless_handoff_passed"] is True
    for filename in PAPER_EXTERNAL_SCORE_FILENAMES.values():
        assert (output_dir / filename).exists(), filename


def test_paper_track_p19a_fails_closed_without_required_metadata(tmp_path: Path) -> None:
    score_artifact = tmp_path / "bad_score_artifact.json"
    score_artifact.write_text(
        json.dumps(
            {
                "artifact_id": "bad_score_artifact",
                "rows": [{"entity_id": "private-entity", "score": 0.8}],
                "claim_state": "detector_superiority",
            }
        ),
        encoding="utf-8",
    )

    pack = build_paper_external_score_pack(PROJECT_ROOT, score_artifact_path=score_artifact)
    manifest = pack["paper_external_score_manifest"]
    schema = pack["paper_external_score_schema"]
    cells = pack["paper_external_score_evidence_cells"]
    gate = pack["paper_external_score_claim_gate"]
    handoff = pack["paper_external_score_handoff_eval"]
    serialized = json.dumps(pack, sort_keys=True)

    assert manifest["status"] == "blocked_pending_p19a_metadata"
    assert schema["accepted"] is False
    assert "dataset_id" in schema["required_missing"]
    assert "rows" in " ".join(schema["forbidden_fields_detected"])
    assert cells["evidence_cell_count"] == 0
    assert gate["publishable"] is False
    assert "required_metadata_complete" in gate["failed_checks"]
    assert "rowless_input_contract" in gate["failed_checks"]
    assert "factual_input_has_no_interpretive_fields" in gate["failed_checks"]
    assert handoff["rowless_handoff_passed"] is False
    assert "private-entity" not in serialized
    assert str(tmp_path).replace("\\", "/") not in serialized.replace("\\", "/")


def test_paper_track_p19a_committed_external_score_artifacts_are_ready() -> None:
    for filename in PAPER_EXTERNAL_SCORE_FILENAMES.values():
        assert (REPORT_DIR / filename).exists(), filename

    manifest = _load_report("paper_external_score_manifest.json")
    schema = _load_report("paper_external_score_schema.json")
    route = _load_report("paper_external_score_route_decision.json")
    cells = _load_report("paper_external_score_evidence_cells.json")
    gate = _load_report("paper_external_score_claim_gate.json")
    handoff = _load_report("paper_external_score_handoff_eval.json")
    summary = (REPORT_DIR / "paper_external_score_summary.md").read_text(encoding="utf-8")

    assert manifest["status"] == "ready_for_hosted_score_governance"
    assert route["selected_route"] == "external_score_file_adapter"
    assert schema["accepted"] is True
    assert cells["evidence_cell_count"] == 1
    assert not EVIDENCE_CELL_INTERPRETIVE_FIELDS.intersection(cells["evidence_cells"][0])
    assert cells["evidence_gate_separation"]["status"] == "pass"
    assert gate["publishable"] is True
    assert handoff["rowless_handoff_passed"] is True
    assert "Paper P19-A External Score-File Proof Pack" in summary
    assert "hosted detector-output governance" in route["paper_claim_boundary"]
