from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from relaytic.release_safety import (
    PAPER_GOVERNANCE_ABLATION_FILENAMES,
    build_paper_governance_ablation_pack,
)
from relaytic.ui.cli import main


PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = PROJECT_ROOT / "docs" / "reports"
PAPER_DIR = PROJECT_ROOT / "docs" / "paper"
pytestmark = pytest.mark.prepush


def _load_report(name: str) -> dict[str, Any]:
    return json.loads((REPORT_DIR / name).read_text(encoding="utf-8"))


def test_paper_track_p17_builds_governance_ablation_pack() -> None:
    pack = build_paper_governance_ablation_pack(PROJECT_ROOT)

    manifest = pack["paper_governance_ablation_manifest"]
    evaluation = pack["paper_governance_ablation_eval"]
    matrix = pack["paper_governance_ablation_matrix"]
    rows = {row["condition_id"]: row for row in evaluation["ablation_rows"]}
    serialized = json.dumps(pack, sort_keys=True)

    assert manifest["status"] == "ready_for_governance_ablation_evidence"
    assert manifest["governance_ablation_evidence_allowed"] is True
    assert manifest["hard_claims_allowed"] is False
    assert manifest["headline_claims_allowed"] is False
    assert manifest["detector_superiority_claim_allowed"] is False
    assert evaluation["status"] == "pass"
    assert evaluation["full_path_safe"] is True
    assert evaluation["disabled_fixture_count"] >= 5
    assert evaluation["raw_rows_exposed"] is False
    assert evaluation["private_paths_exposed"] is False
    assert matrix["status"] == "pass"

    assert rows["full_governance_path"]["unsupported_claims_released"] == 0
    assert rows["full_governance_path"]["leakage_features_allowed"] == 0
    assert rows["full_governance_path"]["raw_fields_exported"] == 0
    assert rows["full_governance_path"]["missing_provenance_fields"] == 0
    assert rows["full_governance_path"]["recovery_next_actions_available"] > 0
    assert rows["no_claim_gate"]["unsupported_claims_released"] >= 1
    assert rows["no_leakage_policy"]["leakage_features_allowed"] >= 1
    assert rows["no_rowless_redaction"]["raw_fields_exported"] >= 1
    assert rows["no_evidence_cell_required_fields"]["missing_provenance_fields"] >= 1
    assert rows["no_recovery_guide"]["recovery_next_actions_available"] == 0
    assert "do not add detector benchmark" in evaluation["interpretation"]
    assert str(PROJECT_ROOT).replace("\\", "/") not in serialized.replace("\\", "/")


def test_paper_track_p17_cli_writes_reports(
    tmp_path: Path,
    capsys: Any,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    output_dir = tmp_path / "reports"
    monkeypatch.chdir(PROJECT_ROOT)

    exit_code = main(
        [
            "release-safety",
            "paper-governance-ablation",
            "--output-dir",
            str(output_dir),
            "--format",
            "json",
        ]
    )

    assert exit_code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["status"] == "ready_for_governance_ablation_evidence"
    assert payload["paper_governance_ablation_eval"]["status"] == "pass"
    assert payload["paper_governance_ablation_matrix"]["status"] == "pass"
    for filename in PAPER_GOVERNANCE_ABLATION_FILENAMES.values():
        assert (output_dir / filename).exists(), filename


def test_paper_track_p17_fails_closed_without_required_inputs(tmp_path: Path) -> None:
    pack = build_paper_governance_ablation_pack(tmp_path)
    manifest = pack["paper_governance_ablation_manifest"]
    evaluation = pack["paper_governance_ablation_eval"]

    assert manifest["status"] == "blocked_missing_governance_ablation_evidence"
    assert manifest["governance_ablation_evidence_allowed"] is False
    assert evaluation["status"] == "fail"
    assert evaluation["full_path_safe"] is False
    assert any(
        check["check_id"] == "required_governance_ablation_inputs_present" and not check["passed"]
        for check in manifest["checks"]
    )
    assert manifest["failed_checks"]


def test_paper_track_p17_committed_governance_ablation_artifacts_are_ready() -> None:
    for filename in PAPER_GOVERNANCE_ABLATION_FILENAMES.values():
        assert (REPORT_DIR / filename).exists(), filename

    manifest = _load_report("paper_governance_ablation_manifest.json")
    evaluation = _load_report("paper_governance_ablation_eval.json")
    matrix = _load_report("paper_governance_ablation_matrix.json")
    summary = (REPORT_DIR / "paper_governance_ablation_summary.md").read_text(encoding="utf-8")
    draft = (PAPER_DIR / "relaytic_aml_arxiv_draft.md").read_text(encoding="utf-8")

    assert manifest["status"] == "ready_for_governance_ablation_evidence"
    assert not manifest["failed_checks"]
    assert evaluation["status"] == "pass"
    assert evaluation["full_path_safe"] is True
    assert evaluation["disabled_fixture_count"] >= 5
    assert matrix["status"] == "pass"
    assert "Paper P17 Governance-Ablation Pack" in summary
    assert "Table 7. Governance machinery ablation" in draft
    assert "No claim gate" in draft
    assert "Table 11 gives the practical external-agent story" in draft
