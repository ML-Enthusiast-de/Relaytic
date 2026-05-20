from __future__ import annotations

import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = PROJECT_ROOT / "docs" / "reports"


def _load_report(name: str) -> dict[str, object]:
    return json.loads((REPORT_DIR / name).read_text(encoding="utf-8"))


def test_paper_track_p0_baseline_manifest_freezes_claim_blocked_start() -> None:
    manifest = _load_report("paper_track_baseline_manifest.json")
    freeze = _load_report("paper_release_freeze_manifest.json")
    claim_report = _load_report("paper_claim_boundary_report.json")

    assert manifest["schema_version"] == "relaytic.paper_track_baseline.v1"
    assert manifest["slice"] == "Paper Track P0"
    assert manifest["status"] == "baseline_frozen_for_paper_track"
    assert dict(manifest["baseline"])["next_slice"] == "Paper Track P1"
    assert dict(manifest["claim_gate_snapshot"])["hard_performance_claims_allowed"] is False
    assert freeze["hard_performance_claims_allowed"] is False

    claims = {str(item["claim_id"]): dict(item) for item in claim_report["claims"]}  # type: ignore[index]
    assert claims["claim_sota_or_hard_aml_superiority"]["boundary"] == "blocked"


def test_paper_track_p0_verification_report_records_required_commands() -> None:
    report = _load_report("paper_track_verification_report.json")
    commands = {str(item["command_id"]): dict(item) for item in report["commands"]}  # type: ignore[index]
    summary = dict(report["verification_summary"])

    assert report["schema_version"] == "relaytic.paper_track_verification.v1"
    assert report["slice"] == "Paper Track P0"
    assert summary["paper_freeze_rerun_passed"] is True
    assert summary["release_safety_scan_passed"] is True
    assert summary["hard_performance_claims_allowed"] is False
    assert summary["next_slice"] == "Paper Track P1"

    assert commands["paper_freeze_rerun"]["status"] == "passed"
    assert commands["paper_freeze_rerun"]["observed_hard_performance_claims_allowed"] is False
    assert commands["release_safety_scan"]["status"] == "passed"
    assert "test_paper_track_p0.py" in commands["targeted_p0_regression"]["command"]
