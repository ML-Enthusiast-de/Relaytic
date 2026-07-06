from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from relaytic.release_safety import (
    PAPER_INVARIANT_FILENAMES,
    build_paper_invariant_pack,
)
from relaytic.ui.cli import main


PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = PROJECT_ROOT / "docs" / "reports"
PAPER_DIR = PROJECT_ROOT / "docs" / "paper"
pytestmark = pytest.mark.prepush


def _load_report(name: str) -> dict[str, Any]:
    return json.loads((REPORT_DIR / name).read_text(encoding="utf-8"))


def test_paper_track_p18_builds_governance_invariant_pack() -> None:
    pack = build_paper_invariant_pack(PROJECT_ROOT)

    manifest = pack["paper_invariant_manifest"]
    invariants = pack["paper_governance_invariants"]
    adjacent = pack["paper_adjacent_systems_comparison"]
    serialized = json.dumps(pack, sort_keys=True)

    assert manifest["status"] == "ready_for_governance_invariant_evidence"
    assert not manifest["failed_checks"]
    assert invariants["status"] == "pass"
    assert invariants["proof_obligation_passed"] is True
    assert invariants["current_invariant_count"] >= 7
    assert adjacent["status"] == "pass"
    assert adjacent["family_count"] >= 6
    assert not adjacent["missing_required_families"]
    assert not invariants["claim_boundary"]["detector_superiority_claimed"]
    assert not invariants["claim_boundary"]["hard_real_bank_aml_superiority_claimed"]
    assert not invariants["claim_boundary"]["graph_neural_detector_novelty_claimed"]
    assert not invariants["claim_boundary"]["revclassify_parity_claimed"]

    for row in invariants["invariants"]:
        assert row["current_status"] == "current_checked"
        assert row["evidence_refs"], row["invariant_id"]
        assert row["failure_or_ablation_refs"], row["invariant_id"]
        assert row["limitation_or_boundary"], row["invariant_id"]

    families = {row["adjacent_family"] for row in adjacent["comparison_rows"]}
    assert {
        "Model cards and model reporting",
        "Datasheets and dataset documentation",
        "ML reproducibility checklists",
        "MLOps experiment tracking",
        "Agent benchmarks and research-agent evaluations",
        "AML detector and benchmark papers",
    } <= families
    assert str(PROJECT_ROOT).replace("\\", "/") not in serialized.replace("\\", "/")


def test_paper_track_p18_cli_writes_reports(
    tmp_path: Path,
    capsys: Any,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    output_dir = tmp_path / "reports"
    monkeypatch.chdir(PROJECT_ROOT)

    exit_code = main(
        [
            "release-safety",
            "paper-invariants",
            "--output-dir",
            str(output_dir),
            "--format",
            "json",
        ]
    )

    assert exit_code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["status"] == "ready_for_governance_invariant_evidence"
    assert payload["paper_governance_invariants"]["status"] == "pass"
    assert payload["paper_adjacent_systems_comparison"]["status"] == "pass"
    for filename in PAPER_INVARIANT_FILENAMES.values():
        assert (output_dir / filename).exists(), filename


def test_paper_track_p18_fails_closed_without_required_inputs(tmp_path: Path) -> None:
    pack = build_paper_invariant_pack(tmp_path)
    manifest = pack["paper_invariant_manifest"]
    invariants = pack["paper_governance_invariants"]
    adjacent = pack["paper_adjacent_systems_comparison"]

    assert manifest["status"] == "blocked_pending_p18_repairs"
    assert invariants["status"] == "blocked"
    assert adjacent["status"] == "blocked"
    assert any(
        check["check_id"] == "required_inputs_present" and not check["passed"]
        for check in manifest["checks"]
    )
    assert manifest["failed_checks"]


def test_paper_track_p18_committed_invariant_artifacts_are_ready() -> None:
    for filename in PAPER_INVARIANT_FILENAMES.values():
        assert (REPORT_DIR / filename).exists(), filename

    manifest = _load_report("paper_invariant_manifest.json")
    invariants = _load_report("paper_governance_invariants.json")
    adjacent = _load_report("paper_adjacent_systems_comparison.json")
    summary = (REPORT_DIR / "paper_invariant_summary.md").read_text(encoding="utf-8")
    draft = (PAPER_DIR / "relaytic_aml_arxiv_draft.md").read_text(encoding="utf-8")

    assert manifest["status"] == "ready_for_governance_invariant_evidence"
    assert not manifest["failed_checks"]
    assert invariants["status"] == "pass"
    assert invariants["proof_obligation_passed"] is True
    assert adjacent["status"] == "pass"
    assert "Paper P18 Governance-Invariant Pack" in summary
    assert "Adjacent systems comparison" in draft
    assert "Appendix table. Governance invariants and evidence map" in draft
    assert "Claim-strength monotonicity" in draft
    assert "The handoff and recovery rows give the practical external-agent story." in draft
