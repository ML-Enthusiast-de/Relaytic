from __future__ import annotations

import json
from pathlib import Path
import subprocess
from typing import Any

import pytest

from relaytic.release_safety import (
    PAPER_RELEASE_INTEGRITY_FILENAMES,
    build_exact_revision_release,
    build_paper_release_integrity_pack,
)
from relaytic.ui.cli import main


PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = PROJECT_ROOT / "docs" / "reports"
PAPER_DIR = PROJECT_ROOT / "docs" / "paper"
pytestmark = pytest.mark.prepush


def test_p24_integrity_pack_passes_authoritative_evidence_checks() -> None:
    pack = build_paper_release_integrity_pack(PROJECT_ROOT)
    manifest = pack["paper_p24_release_manifest"]

    assert manifest["status"] == "release_candidate_ready_for_human_upload"
    assert manifest["arxiv_upload_ready"] is False
    assert manifest["benchmark_values_changed"] is False
    assert all(row["passed"] for row in manifest["checks"])
    assert pack["paper_p24_metric_consistency_audit"]["status"] == "pass"
    assert pack["paper_p24_split_consistency_audit"]["status"] == "pass"
    assert pack["paper_p24_semantic_source_audit"]["status"] == "pass"
    bibliography_checks = pack["paper_p24_bibliography_verification"]["corrected_author_checks"]
    governance_check = next(
        row for row in bibliography_checks if row["citation_key"] == "gaurav2025governanceaas"
    )
    assert governance_check["expected_author_field"] == (
        "Pervez, Helen and Gaurav, Suyash and Heikkonen, Jukka and Chaudhary, Jatin"
    )
    assert governance_check["passed"] is True


def test_p24_reader_surfaces_disclose_protocol_and_statistical_boundaries() -> None:
    draft = (PAPER_DIR / "relaytic_aml_arxiv_draft.md").read_text(encoding="utf-8")
    figure = (PAPER_DIR / "figures" / "figure_3_review_budget.svg").read_text(encoding="utf-8")

    for phrase in (
        "single-seed point estimates",
        "same-step events do not see one another",
        "validation PR-AUC 0.9767",
        "confirmatory rather than blind or untouched evidence",
        "scores equal to the threshold are included",
        "Deterministic Artifact and Release-Gate Evaluation",
    ):
        assert phrase in draft
    assert "paper/public claim a..." not in draft
    assert "+/-" not in draft
    assert "rows/nodes" not in draft
    assert "Values across datasets and task contracts are not directly comparable." in figure


def test_p24_cli_writes_all_reports(tmp_path: Path, capsys: Any, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(PROJECT_ROOT)
    output_dir = tmp_path / "reports"

    exit_code = main(
        ["release-safety", "paper-release-integrity", "--output-dir", str(output_dir), "--format", "json"]
    )

    assert exit_code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["status"] == "release_candidate_ready_for_human_upload"
    for filename in PAPER_RELEASE_INTEGRITY_FILENAMES.values():
        assert (output_dir / filename).is_file(), filename


def test_p24_final_mode_refuses_dirty_worktree(tmp_path: Path) -> None:
    subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=tmp_path, check=True)
    marker = tmp_path / "marker.txt"
    marker.write_text("clean\n", encoding="utf-8")
    subprocess.run(["git", "add", "marker.txt"], cwd=tmp_path, check=True)
    subprocess.run(["git", "commit", "-m", "fixture"], cwd=tmp_path, check=True, capture_output=True)
    marker.write_text("dirty\n", encoding="utf-8")
    with pytest.raises(ValueError, match="clean Git worktree"):
        build_exact_revision_release(tmp_path)


def test_p24_committed_reports_pass() -> None:
    for filename in PAPER_RELEASE_INTEGRITY_FILENAMES.values():
        assert (REPORT_DIR / filename).is_file(), filename
    manifest = json.loads((REPORT_DIR / "paper_p24_release_manifest.json").read_text(encoding="utf-8"))
    assert manifest["status"] == "release_candidate_ready_for_human_upload"
    assert all(row["passed"] for row in manifest["checks"])
