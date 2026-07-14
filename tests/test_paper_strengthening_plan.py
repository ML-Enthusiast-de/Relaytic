from __future__ import annotations

from pathlib import Path

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
pytestmark = pytest.mark.prepush


def _read(relative_path: str) -> str:
    return (PROJECT_ROOT / relative_path).read_text(encoding="utf-8")


def test_paper_strengthening_track_records_stage_9_as_implemented() -> None:
    plan = _read("docs/build_slices/phase_paper_strengthening.md")
    slicing = _read("RELAYTIC_SLICING_PLAN.md")
    build = _read("RELAYTIC_BUILD_MASTER.md")
    status = _read("IMPLEMENTATION_STATUS.md")
    paper_track = _read("docs/build_slices/phase_paper_track.md")
    release_integrity = _read("docs/build_slices/phase_paper_release_integrity.md")

    for slice_id in ("P16", "P17", "P18", "P19", "P20", "P21", "P22", "P23"):
        assert f"Paper Track {slice_id}" in plan
        assert f"Paper Track {slice_id}" in slicing

    assert "Paper Track P19-A" in plan
    assert "Paper Track P19-A" in slicing
    assert "Paper Track P19-B" in plan
    assert "Paper Track P19-B" in slicing
    assert "Paper P19-A" in build
    assert "Paper P19-B" in build
    assert "Paper P22" in build
    assert "Paper P23" in build
    assert "Stage 9/9 is implemented." in plan
    assert "P23 hardens the paper's novelty and adjacent-systems distinction" in plan
    assert "separate planned P24 release-integrity slice" in plan
    assert "Paper Track P24" in release_integrity
    assert "P19-A produces the external score-file governance proof pack" in plan
    assert "P19-B turns that proof into a reader-facing hosted-score case study" in plan
    assert "Paper Track P16 - failure-case evaluation pack** - implemented" in plan
    assert "Paper Track P17 - governance machinery ablation pack** - implemented" in plan
    assert "Paper Track P18 - governance invariants and adjacent-systems positioning** - implemented" in plan
    assert "Paper Track P19-A - external score-file adapter proof pack** - implemented" in plan
    assert "Paper Track P19-B - external score case-study and paper integration** - implemented" in plan
    assert "Paper Track P20 - paper narrative and visual polish** - implemented" in plan
    assert "Paper Track P21 - final source/PDF preflight and changelog** - implemented" in plan
    assert "Paper Track P22 - author-review layout hardening and regression closure** - implemented" in plan
    assert "Paper Track P23 - novelty and adjacent-systems distinction hardening** - implemented" in plan
    assert "Stage 3 Acceptance" in plan
    assert "Stage 4A Acceptance (completed)" in plan
    assert "Stage 4B Acceptance (completed)" in plan
    assert "Stage 5/6 Acceptance (completed)" in plan
    assert "Stage 7 Acceptance (completed)" in plan
    assert "Stage 8 Acceptance (completed)" in plan
    assert "Stage 9 Acceptance (completed)" in plan
    assert "phase_paper_strengthening.md" in build
    assert "phase_paper_strengthening.md" in paper_track
    assert "latest paper-strengthening slice" in status
    assert "Paper Track P22 author-review layout hardening" in status
    assert "latest paper-integrity slice: P24 corrected factual" in status
    assert "next recommended action: commit and push the reviewed P26 source candidate" in status
    assert "latest paper-novelty-positioning slice" in status


def test_paper_strengthening_plan_preserves_evidence_first_scope() -> None:
    plan = _read("docs/build_slices/phase_paper_strengthening.md")

    for required_case in (
        "leakage-column injection",
        "test-set selection violation",
        "over-strong claim attempts",
        "rowless handoff redaction",
        "interrupted-run recovery",
    ):
        assert required_case in plan

    for ablation_metric in (
        "unsupported claims released",
        "leakage features allowed",
        "raw fields exported",
        "missing provenance fields",
        "publishable tables generated",
        "recovery next actions available",
    ):
        assert ablation_metric in plan

    for invariant in (
        "metric-cell provenance",
        "claim-strength monotonicity",
        "leakage and selection firewalls",
        "rowless handoff",
        "interrupted-run recovery",
        "benchmark role separation",
        "local-first release safety",
    ):
        assert invariant in plan

    for blocked_claim in (
        "real-bank AML superiority",
        "RevClassifyDS parity",
        "graph-neural detector novelty",
        "production deployment",
        "analyst-impact claims",
    ):
        assert blocked_claim in plan

    assert "No invented benchmark result" in plan
    assert "Stage work stops at the requested trigger" in plan
    assert "CTO/arXiv quality gate" in plan
    assert "paper_cto_quality_gap_review.md" in plan
    assert "external score-file adapter" in plan
    assert "paper-external-score-proof" in plan
    assert "paper-external-score-integration" in plan
    assert "paper_external_score_manifest.json" in plan
    assert "paper_external_score_evidence_cells.json" in plan
    assert "paper_external_score_case_study.json" in plan
    assert "paper_external_score_paper_panel.json" in plan
    assert "paper_external_score_repro_card.md" in plan
    assert "paper_paysim_selection_story_review.json" in plan
    assert "paper_reader_guidance_audit.json" in plan
    assert "paper_visual_table_polish_audit.json" in plan
    assert "paper_narrative_polish_manifest.json" in plan
    assert "paper_final_preflight_manifest.json" in plan
    assert "paper_final_release_changelog.md" in plan
    assert "rowless handoff report redacts raw rows" in plan
    assert "hosted-score case study" in plan
    assert "hosted detector or score-workflow" in plan
    assert "paper_novelty_positioning_audit.json" in plan
    assert "paper_adjacent_systems_distinction_matrix.json" in plan
    assert "AML LLM triage systems" in plan
    assert "agentic SAR/compliance narrative systems" in plan
    assert "agent-governance/trust layers" in plan
    assert "around detectors and agents" in plan
    assert "not a detector replacement" in plan


def test_paper_strengthening_plan_records_cto_quality_review() -> None:
    review = _read("docs/reports/paper_cto_quality_gap_review.md")

    for source_marker in (
        "PaperBench",
        "MLR-Bench",
        "TransXion",
        "BlazingAML",
        "LineMVGNN",
        "Elliptic2",
    ):
        assert source_marker in review

    assert "Good independent arXiv systems/evaluation paper: yes." in review
    assert "Top visible arXiv paper" in review
    assert "not yet" in review
    assert "Hosted detector or score-stream demonstration" in review
    assert "Preferred route: external score-file adapter." in review
    assert "The paper should not try to compete" in review
