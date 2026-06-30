from __future__ import annotations

from pathlib import Path

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
pytestmark = pytest.mark.prepush


def _read(relative_path: str) -> str:
    return (PROJECT_ROOT / relative_path).read_text(encoding="utf-8")


def test_paper_strengthening_track_records_stage_3_and_remaining_followons() -> None:
    plan = _read("docs/build_slices/phase_paper_strengthening.md")
    slicing = _read("RELAYTIC_SLICING_PLAN.md")
    build = _read("RELAYTIC_BUILD_MASTER.md")
    status = _read("IMPLEMENTATION_STATUS.md")
    paper_track = _read("docs/build_slices/phase_paper_track.md")

    for slice_id in ("P16", "P17", "P18", "P19", "P20", "P21"):
        assert f"Paper Track {slice_id}" in plan
        assert f"Paper Track {slice_id}" in slicing

    assert "Stage 3 is implemented." in plan
    assert "P19 is the next triggerable stage" in plan
    assert "Paper Track P16 - failure-case evaluation pack** - implemented" in plan
    assert "Paper Track P17 - governance machinery ablation pack** - implemented" in plan
    assert "Paper Track P18 - governance invariants and adjacent-systems positioning** - implemented" in plan
    assert "Stage 3 Acceptance" in plan
    assert "phase_paper_strengthening.md" in build
    assert "phase_paper_strengthening.md" in paper_track
    assert "latest paper-strengthening slice" in status


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
