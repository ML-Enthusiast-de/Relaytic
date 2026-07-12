from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from relaytic.release_safety import (
    PAPER_NOVELTY_FILENAMES,
    REQUIRED_DISTINCTION_CATEGORIES,
    build_paper_novelty_positioning_pack,
)
from relaytic.ui.cli import main


PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = PROJECT_ROOT / "docs" / "reports"
PAPER_DIR = PROJECT_ROOT / "docs" / "paper"
pytestmark = pytest.mark.prepush


def _load_report(name: str) -> dict[str, Any]:
    return json.loads((REPORT_DIR / name).read_text(encoding="utf-8"))


def test_paper_track_p23_builds_novelty_positioning_pack() -> None:
    pack = build_paper_novelty_positioning_pack(PROJECT_ROOT)

    manifest = pack["paper_novelty_positioning_manifest"]
    audit = pack["paper_novelty_positioning_audit"]
    matrix = pack["paper_adjacent_systems_distinction_matrix"]
    rows = matrix["distinction_rows"]
    categories = {row["adjacent_system_type"] for row in rows}
    serialized = json.dumps(pack, sort_keys=True)

    assert manifest["status"] == "ready_for_final_author_review"
    assert manifest["p23_implemented"] is True
    assert manifest["next_slice"].startswith("Slice 16A")
    assert not manifest["hard_claims_allowed"]
    assert not manifest["headline_claims_allowed"]
    assert not manifest["failed_checks"]

    assert audit["status"] == "pass"
    assert matrix["status"] == "pass"
    assert matrix["covered_category_count"] >= len(REQUIRED_DISTINCTION_CATEGORIES)
    assert set(REQUIRED_DISTINCTION_CATEGORIES) <= categories
    assert not matrix["claim_boundary"]["detector_replacement_claimed"]
    assert not matrix["claim_boundary"]["sar_generation_claimed"]
    assert not matrix["claim_boundary"]["generic_agent_governance_claimed"]
    assert str(PROJECT_ROOT).replace("\\", "/") not in serialized.replace("\\", "/")


def test_paper_track_p23_cli_writes_reports(
    tmp_path: Path,
    capsys: Any,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    output_dir = tmp_path / "reports"
    monkeypatch.chdir(PROJECT_ROOT)

    exit_code = main(
        [
            "release-safety",
            "paper-novelty-positioning",
            "--output-dir",
            str(output_dir),
            "--format",
            "json",
        ]
    )

    assert exit_code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["status"] == "ready_for_final_author_review"
    assert payload["paper_novelty_positioning_audit"]["status"] == "pass"
    assert payload["paper_adjacent_systems_distinction_matrix"]["status"] == "pass"
    for filename in PAPER_NOVELTY_FILENAMES.values():
        assert (output_dir / filename).exists(), filename


def test_paper_track_p23_fails_closed_without_required_inputs(tmp_path: Path) -> None:
    pack = build_paper_novelty_positioning_pack(tmp_path)
    manifest = pack["paper_novelty_positioning_manifest"]
    audit = pack["paper_novelty_positioning_audit"]
    matrix = pack["paper_adjacent_systems_distinction_matrix"]

    assert manifest["status"] == "blocked_pending_p23_repairs"
    assert audit["status"] == "fail"
    assert matrix["status"] == "fail"
    assert any(
        check["check_id"] == "required_p23_inputs_present" and not check["passed"]
        for check in manifest["checks"]
    )
    assert manifest["failed_checks"]


def test_paper_track_p23_committed_artifacts_are_ready() -> None:
    for filename in PAPER_NOVELTY_FILENAMES.values():
        assert (REPORT_DIR / filename).exists(), filename

    manifest = _load_report("paper_novelty_positioning_manifest.json")
    audit = _load_report("paper_novelty_positioning_audit.json")
    matrix = _load_report("paper_adjacent_systems_distinction_matrix.json")
    summary = (REPORT_DIR / "paper_novelty_positioning_summary.md").read_text(encoding="utf-8")
    draft = (PAPER_DIR / "relaytic_aml_arxiv_draft.md").read_text(encoding="utf-8")

    assert manifest["status"] == "ready_for_final_author_review"
    assert audit["status"] == "pass"
    assert matrix["status"] == "pass"
    assert "Paper P23 Novelty And Adjacent-Systems Distinction" in summary
    assert "What is new" in draft
    assert "governance substrate around detectors and agent-assisted workflows" in draft
    assert "wrap detector outputs" in draft
    assert "governance substrate for detector studies rather than a replacement" in draft
    assert "not a SAR drafting system" in draft
