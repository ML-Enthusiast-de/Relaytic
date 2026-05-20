from __future__ import annotations

import json
from pathlib import Path

from relaytic.analytics import rank_candidate_targets, rank_surrogate_candidates
from relaytic.modeling import train_model_candidates, train_surrogate_candidates
from relaytic.orchestration.default_tools import build_default_registry
from relaytic.release_safety import (
    PAPER_SURFACE_HYGIENE_FILENAMES,
    build_paper_surface_hygiene_reports,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = PROJECT_ROOT / "docs" / "reports"


def _load_report(name: str) -> dict[str, object]:
    return json.loads((REPORT_DIR / name).read_text(encoding="utf-8"))


def test_paper_track_p1_hygiene_reports_are_clean_and_p2_ready() -> None:
    reports = build_paper_surface_hygiene_reports(PROJECT_ROOT)
    assert set(reports) == set(PAPER_SURFACE_HYGIENE_FILENAMES)

    public_surface = reports["paper_public_surface_hygiene_report"]
    retention = reports["legacy_compatibility_retention_report"]
    scorecard = reports["paper_repo_cleanup_scorecard"]

    assert public_surface["status"] == "clean"
    assert public_surface["stale_public_surface_language_detected"] is False
    assert public_surface["unsupported_sota_language_detected"] is False
    assert public_surface["stale_language_findings"] == []
    assert dict(public_surface["cli_public_help_checks"][0])["legacy_alias_visible"] is False  # type: ignore[index]
    assert retention["all_compatibility_files_present"] is True
    assert retention["all_required_aliases_present"] is True
    assert scorecard["status"] == "ready_for_paper_track_p2"
    assert scorecard["next_slice"] == "Paper Track P2"


def test_paper_track_p1_committed_reports_match_generated_contract() -> None:
    generated = build_paper_surface_hygiene_reports(PROJECT_ROOT)
    for key, filename in PAPER_SURFACE_HYGIENE_FILENAMES.items():
        committed = _load_report(filename)
        assert committed == generated[key], filename


def test_paper_track_p1_adds_relaytic_aliases_for_legacy_api_names() -> None:
    assert train_model_candidates is train_surrogate_candidates
    assert rank_candidate_targets is rank_surrogate_candidates

    registry = build_default_registry()
    tool_names = {item["name"] for item in registry.list_tools()}

    assert "train_model_candidates" in tool_names
    assert "train_incremental_linear_model" in tool_names
    assert "resume_incremental_linear_model" in tool_names
    assert "train_surrogate_candidates" in tool_names
    assert "train_incremental_linear_surrogate" in tool_names
    assert "resume_incremental_linear_surrogate" in tool_names
