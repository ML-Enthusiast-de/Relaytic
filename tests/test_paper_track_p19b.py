from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from relaytic.release_safety import (
    PAPER_EXTERNAL_SCORE_INTEGRATION_FILENAMES,
    build_paper_external_score_integration_pack,
)
from relaytic.ui.cli import main


PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = PROJECT_ROOT / "docs" / "reports"
PAPER_DRAFT = PROJECT_ROOT / "docs" / "paper" / "relaytic_aml_arxiv_draft.md"
pytestmark = pytest.mark.prepush


def _load_report(name: str) -> dict[str, Any]:
    return json.loads((REPORT_DIR / name).read_text(encoding="utf-8"))


def test_paper_track_p19b_builds_hosted_score_case_study() -> None:
    pack = build_paper_external_score_integration_pack(PROJECT_ROOT)

    manifest = pack["paper_external_score_integration_manifest"]
    case_study = pack["paper_external_score_case_study"]
    panel = pack["paper_external_score_paper_panel"]
    claim_map = pack["paper_external_score_claim_map"]
    repro_card = pack["paper_external_score_repro_card"]
    adapter = case_study["adapter_input_contract"]
    metric = case_study["metric_policy"]
    redaction = case_study["rowless_redaction"]
    serialized = json.dumps(pack, sort_keys=True)

    assert manifest["status"] == "ready_for_hosted_score_case_study"
    assert manifest["paper_integration_allowed"] is True
    assert not manifest["failed_checks"]
    assert case_study["status"] == "pass"
    assert panel["status"] == "pass"
    assert len(panel["rows"]) >= 4
    assert "p19a.external_score.hosted_metadata_completeness" in case_study["evidence_cell_ids"]
    assert adapter["selected_route"] == "external_score_file_adapter"
    assert adapter["schema_hash_prefix"] == "4b2b70a58b0c"
    assert adapter["content_hash_prefix"] == "dac68c3801f5"
    assert metric["detector_performance_metric"] is False
    assert metric["metric_role"] == "governance_metric"
    assert redaction["rowless_handoff_passed"] is True
    assert redaction["raw_rows_exported"] is False
    assert redaction["private_paths_exported"] is False
    assert redaction["secrets_exported"] is False
    assert case_study["allowed_claim_state"] == "hosted_detector_output_governance_only"
    assert len(case_study["blocked_stronger_claims"]) >= 5
    assert claim_map["detector_superiority_allowed"] is False
    assert claim_map["production_aml_readiness_allowed"] is False
    assert claim_map["revclassifyds_parity_allowed"] is False
    assert "paper-external-score-proof" in repro_card
    assert "paper-external-score-integration" in repro_card
    assert "py -3.11" in repro_card
    assert "python3" in repro_card
    assert str(PROJECT_ROOT).replace("\\", "/") not in serialized.replace("\\", "/")


def test_paper_track_p19b_cli_writes_reports(
    tmp_path: Path,
    capsys: Any,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    output_dir = tmp_path / "reports"
    monkeypatch.chdir(PROJECT_ROOT)

    exit_code = main(
        [
            "release-safety",
            "paper-external-score-integration",
            "--output-dir",
            str(output_dir),
            "--format",
            "json",
        ]
    )

    assert exit_code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["status"] == "ready_for_hosted_score_case_study"
    assert payload["paper_external_score_integration_manifest"]["paper_integration_allowed"] is True
    assert payload["paper_external_score_case_study"]["status"] == "pass"
    assert payload["paper_external_score_paper_panel"]["status"] == "pass"
    assert payload["paper_external_score_claim_map"]["detector_superiority_allowed"] is False
    for filename in PAPER_EXTERNAL_SCORE_INTEGRATION_FILENAMES.values():
        assert (output_dir / filename).exists(), filename


def test_paper_track_p19b_fails_closed_without_p19a_artifacts(tmp_path: Path) -> None:
    pack = build_paper_external_score_integration_pack(PROJECT_ROOT, source_report_dir=tmp_path)

    manifest = pack["paper_external_score_integration_manifest"]
    case_study = pack["paper_external_score_case_study"]
    panel = pack["paper_external_score_paper_panel"]
    claim_map = pack["paper_external_score_claim_map"]

    assert manifest["status"] == "blocked_pending_hosted_score_case_study"
    assert manifest["paper_integration_allowed"] is False
    assert len(manifest["missing_p19a_artifacts"]) == 6
    assert "p19a_inputs_present" in manifest["failed_checks"]
    assert case_study["status"] == "blocked_pending_p19a_evidence"
    assert panel["status"] == "blocked"
    assert claim_map["status"] == "blocked"
    assert claim_map["detector_superiority_allowed"] is False
    assert claim_map["production_aml_readiness_allowed"] is False


def test_paper_track_p19b_committed_artifacts_and_paper_are_ready() -> None:
    for filename in PAPER_EXTERNAL_SCORE_INTEGRATION_FILENAMES.values():
        assert (REPORT_DIR / filename).exists(), filename

    manifest = _load_report("paper_external_score_integration_manifest.json")
    case_study = _load_report("paper_external_score_case_study.json")
    panel = _load_report("paper_external_score_paper_panel.json")
    claim_map = _load_report("paper_external_score_claim_map.json")
    repro_card = (REPORT_DIR / "paper_external_score_repro_card.md").read_text(encoding="utf-8")
    paper = PAPER_DRAFT.read_text(encoding="utf-8")

    assert manifest["status"] == "ready_for_hosted_score_case_study"
    assert manifest["paper_integration_allowed"] is True
    assert case_study["status"] == "pass"
    assert "p19a.external_score.hosted_metadata_completeness" in case_study["evidence_cell_ids"]
    assert panel["status"] == "pass"
    assert claim_map["allowed_claim_scope"] == "hosted_detector_output_governance_only"
    assert "paper-external-score-integration" in repro_card
    assert "Hosted external-score case study" in paper
    assert "governed context" in paper
