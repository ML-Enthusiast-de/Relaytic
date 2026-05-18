from __future__ import annotations

import re
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _read(rel: str) -> str:
    return (PROJECT_ROOT / rel).read_text(encoding="utf-8")


def test_slice15y_readme_starts_with_aml_demo_path() -> None:
    readme = _read("README.md")

    start = readme.index("## Start Here: Relaytic-AML Demo Path")
    baseline = readme.index("## Current Product Baseline")
    assert start < baseline
    assert "relaytic demo aml-review-queue --run-dir artifacts\\relaytic_aml_demo --format json" in readme
    assert "relaytic aml environment --run-dir artifacts\\relaytic_aml_demo --format json" in readme
    assert "Demo-only" in readme
    assert "Dev-benchmark" in readme
    assert "Holdout-benchmark" in readme
    assert "Paper-ready" in readme
    assert "[Why Relaytic-AML](docs/why_relaytic_aml.md)" in readme
    assert "[Product Story](docs/product_story.md)" in readme
    assert "[Paper Benchmark Runbook](docs/paper_benchmark_runbook.md)" in readme
    assert readme.count("**Slice 15Y** demo-first documentation rewrite") == 1


def test_slice15y_story_docs_exist_and_link_to_proof_artifacts() -> None:
    for rel in (
        "docs/why_relaytic_aml.md",
        "docs/product_story.md",
        "docs/paper_benchmark_runbook.md",
    ):
        assert (PROJECT_ROOT / rel).exists(), rel

    story = _read("docs/product_story.md")
    why = _read("docs/why_relaytic_aml.md")
    combined = story + "\n" + why
    for artifact in (
        "case_packet.json",
        "alert_queue_rankings.json",
        "aml_business_value_report.json",
        "operational_metric_guard.json",
        "aml_temporal_benchmark_claim_report.json",
        "aml_environment_scorecard.json",
        "aml_workflow_task_matrix.json",
        "aml_benchmark_environment_scorecard.json",
        "aml_public_claim_guard.json",
        "benchmark_release_gate.json",
    ):
        assert artifact in combined

    for link in re.findall(r"\[[^\]]+\]\(([^)]+)\)", story):
        if link.startswith(("http://", "https://", "#")):
            continue
        assert (PROJECT_ROOT / "docs" / link).resolve().exists(), link


def test_slice15y_handbooks_expose_command_first_aml_demo() -> None:
    user = _read("docs/handbooks/relaytic_user_handbook.md")
    agent = _read("docs/handbooks/relaytic_agent_handbook.md")
    demo = _read("docs/handbooks/relaytic_demo_walkthrough.md")

    for text in (user, agent, demo):
        assert "relaytic demo aml-review-queue --run-dir artifacts\\relaytic_aml_demo --format json" in text
        assert "relaytic aml environment --run-dir artifacts\\relaytic_aml_demo --format json" in text
        assert "aml_environment_scorecard.json" in text

    assert "## Relaytic-AML Demo Path" in user
    assert "## Flagship AML Demo Path" in agent
    assert "## Fastest AML Demo" in demo
    assert "paper_benchmark_runbook.md" in agent


def test_slice15y_paper_runbook_names_families_blockers_and_repro_sequence() -> None:
    runbook = _read("docs/paper_benchmark_runbook.md")

    for family in (
        "PaySim-style",
        "Elliptic-style",
        "Elliptic2-style",
        "AMLSim-style",
        "Generic structured-data",
    ):
        assert family in runbook

    for label in ("`dev`", "`holdout`", "`paper`", "`proxy`", "`blocked`"):
        assert label in runbook

    for artifact in (
        "aml_benchmark_manifest.json",
        "aml_graph_loader_manifest.json",
        "aml_subgraph_task_manifest.json",
        "aml_temporal_benchmark_claim_report.json",
        "aml_environment_scorecard.json",
        "aml_benchmark_environment_scorecard.json",
        "release_safety_scan.json",
    ):
        assert artifact in runbook

    assert "## Blocked-Claim Conditions" in runbook
    assert "## Reproducibility Record" in runbook
    assert "relaytic benchmark run --run-dir artifacts\\aml_benchmark_run" in runbook
    assert "relaytic release-safety scan --format json" in runbook


def test_slice15y_ui_doc_distinguishes_public_surfaces() -> None:
    ui_doc = _read("docs/relaytic_ui_frontier_review.md")

    assert "## First-Contact UI Contract" in ui_doc
    assert "Static fallback" in ui_doc
    assert "AML investigation board" in ui_doc
    assert "Agent Console" in ui_doc
    assert "Local live UI server" in ui_doc
