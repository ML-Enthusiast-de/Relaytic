from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from relaytic.release_safety import (
    PAPER_NARRATIVE_POLISH_FILENAMES,
    build_paper_narrative_polish_pack,
)
from relaytic.ui.cli import main


PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = PROJECT_ROOT / "docs" / "reports"
PAPER_DIR = PROJECT_ROOT / "docs" / "paper"
pytestmark = pytest.mark.prepush


def _load_report(name: str) -> dict[str, Any]:
    return json.loads((REPORT_DIR / name).read_text(encoding="utf-8"))


def test_paper_track_p20_builds_polish_readiness_pack() -> None:
    pack = build_paper_narrative_polish_pack(PROJECT_ROOT)

    manifest = pack["paper_narrative_polish_manifest"]
    paysim = pack["paper_paysim_selection_story_review"]
    guidance = pack["paper_reader_guidance_audit"]
    polish = pack["paper_visual_table_polish_audit"]
    story = paysim["selection_story"]

    assert manifest["status"] == "ready_for_final_pdf_preflight"
    assert manifest["paper_content_ready_for_p21_preflight"] is True
    assert manifest["arxiv_upload_ready"] is False
    assert manifest["next_slice"].startswith("Paper Track P21")
    assert not manifest["failed_checks"]

    assert paysim["status"] == "pass"
    assert story["best_probe_family"] == "XGBoost"
    assert story["selected_finalist_family"] == "Extra Trees"
    assert story["best_probe_validation_pr_auc"] == 0.5944
    assert story["selected_finalist_validation_pr_auc"] == 0.5687
    assert story["selected_finalist_test_pr_auc"] == 0.6388
    assert story["test_visibility_policy"] == "nonselected_competitive_finalists_have_no_test_metrics"

    assert guidance["status"] == "pass"
    assert guidance["reader_path_ready"] is True
    assert guidance["paper_avoids_internal_planning_guidance"] is True
    assert any(
        check["check_id"] == "release_snapshot_guidance_visible" and check["passed"]
        for check in guidance["checks"]
    )
    assert polish["status"] == "pass"
    assert polish["figure_count"] == 4
    assert polish["table_count"] >= 11
    assert any(
        check["check_id"] == "ambiguous_referent_lint_passed" and check["passed"]
        for check in polish["checks"]
    )


def test_paper_track_p20_cli_writes_polish_reports(
    tmp_path: Path,
    capsys: Any,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    output_dir = tmp_path / "reports"
    monkeypatch.chdir(PROJECT_ROOT)

    exit_code = main(
        [
            "release-safety",
            "paper-narrative-polish",
            "--output-dir",
            str(output_dir),
            "--format",
            "json",
        ]
    )

    assert exit_code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["status"] == "ready_for_final_pdf_preflight"
    assert payload["paper_narrative_polish_manifest"]["paper_content_ready_for_p21_preflight"] is True
    for filename in PAPER_NARRATIVE_POLISH_FILENAMES.values():
        assert (output_dir / filename).exists(), filename


def test_paper_track_p20_fails_closed_without_paper_inputs(tmp_path: Path) -> None:
    pack = build_paper_narrative_polish_pack(tmp_path)
    manifest = pack["paper_narrative_polish_manifest"]

    assert manifest["status"] == "blocked_pending_paper_polish_repairs"
    assert manifest["paper_content_ready_for_p21_preflight"] is False
    assert any(
        check["check_id"] == "required_p20_inputs_present" and not check["passed"]
        for check in manifest["checks"]
    )
    assert manifest["failed_checks"]


def test_paper_track_p20_committed_artifacts_and_reader_path_are_ready() -> None:
    for filename in PAPER_NARRATIVE_POLISH_FILENAMES.values():
        assert (REPORT_DIR / filename).exists(), filename

    manifest = _load_report("paper_narrative_polish_manifest.json")
    paysim = _load_report("paper_paysim_selection_story_review.json")
    guidance = _load_report("paper_reader_guidance_audit.json")
    polish = _load_report("paper_visual_table_polish_audit.json")
    draft = (PAPER_DIR / "relaytic_aml_arxiv_draft.md").read_text(encoding="utf-8")
    readme = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8")
    paper_readme = (PAPER_DIR / "README.md").read_text(encoding="utf-8")

    assert manifest["status"] == "ready_for_final_pdf_preflight"
    assert paysim["status"] == "pass"
    assert guidance["status"] == "pass"
    assert polish["status"] == "pass"
    assert "Probe screen" in draft
    assert "Full finalist selection" in draft
    assert "A precision-recall area under the curve (PR-AUC) estimate" in draft
    assert "In this setting, the score" not in draft
    assert "the score only becomes useful" not in draft
    assert "realized test queue of 1,109 of 123,580 transactions" in draft
    assert "Elliptic is a different evidence contract" in draft
    assert "That is a useful operating result" not in draft
    assert "small-sample probe identified" in draft
    assert "Competitive search | XGBoost probe" not in draft
    assert "README contains the full regeneration script" in draft
    assert "final release tag or archival snapshot" in draft
    assert "Deep audit, after the first read" in readme
    assert "docs/paper/README.md" in readme
    assert "paper artifact-generation pipeline" in readme
    assert "release tag is the stable paper record" in readme
    assert "paper_narrative_polish_manifest.json" in readme
    assert "Relaytic-AML Paper Artifacts" in paper_readme
    assert "final Git tag, GitHub Release, or archival snapshot" in paper_readme
