from __future__ import annotations

from pathlib import Path

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
pytestmark = pytest.mark.prepush


def _read(relative_path: str) -> str:
    return (PROJECT_ROOT / relative_path).read_text(encoding="utf-8")


def test_p24_release_integrity_slice_is_planned_before_academy() -> None:
    plan = _read("docs/build_slices/phase_paper_release_integrity.md")
    slicing = _read("RELAYTIC_SLICING_PLAN.md")
    build = _read("RELAYTIC_BUILD_MASTER.md")
    status = _read("IMPLEMENTATION_STATUS.md")

    assert "Paper Track P24" in plan
    assert "Status: implemented" in plan
    assert "Trigger: `implement P24`" in plan
    assert "Paper Track P24" in slicing
    assert "Paper P24" in build
    assert "next execution target: human review, clean commit, and P24 exact-revision final build" in slicing
    assert "latest paper-integrity slice: P24" in status
    assert "Slice 16A" in slicing and "paper release decision" in slicing


def test_p24_plan_preserves_factual_and_claim_boundaries() -> None:
    plan = _read("docs/build_slices/phase_paper_release_integrity.md")

    for required in (
        "paper/public claim a...",
        "6,362,620 transactions",
        "pre-transaction and post-transaction balances",
        "validation PR-AUC `0.976654`",
        "test PR-AUC `0.668756`",
        "`1109/123580`",
        "`36/11184`",
        "`121810` subgraphs",
        "`110902` rows",
        "single-seed point estimates",
        "Values across datasets and task contracts are not directly comparable.",
        "must not change benchmark values silently",
        "not a new detector",
        "RevClassifyDS-parity result",
    ):
        assert required in plan


def test_p24_plan_requires_primary_sources_and_exact_revision_release() -> None:
    plan = _read("docs/build_slices/phase_paper_release_integrity.md")

    for required in (
        "Saito-Rehmsmeier",
        "Kleppmann et al.",
        "Extra Trees",
        "XGBoost",
        "LightGBM",
        "Platt-scaling",
        "paper_p24_bibliography_verification.json",
        "paper_p24_metric_consistency_audit.json",
        "paper_p24_split_consistency_audit.json",
        "git status --short",
        "git rev-parse HEAD",
        "out-of-tree release build",
        "must refuse to run in final mode on a dirty worktree",
        "no Type 3 fonts",
        "Metric mismatch: block release even if the PDF compiles.",
    ):
        assert required in plan
