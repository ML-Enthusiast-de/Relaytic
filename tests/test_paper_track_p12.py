from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from relaytic.release_safety import PAPER_DRY_RUN_FILENAMES, build_paper_dry_run_pack
from relaytic.ui.cli import main


PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = PROJECT_ROOT / "docs" / "reports"
pytestmark = pytest.mark.prepush


def _load_report(name: str) -> dict[str, Any]:
    return json.loads((REPORT_DIR / name).read_text(encoding="utf-8"))


def test_paper_track_p12_reproduces_paper_smoke_from_committed_artifacts() -> None:
    pack = build_paper_dry_run_pack(PROJECT_ROOT, run_live_checks=False)

    install = pack["paper_clean_clone_install_report"]
    report = pack["paper_external_dry_run_report"]
    failures = pack["paper_reproduction_failure_report"]
    go_no_go = pack["paper_release_go_no_go"]

    assert install["status"] == "blocked_install_contract"
    assert install["isolated_clean_clone_probe"]["status"] == "not_run"
    assert report["paper_smoke_status"] == "paper_smoke_reproduced"
    assert report["leak_scan"]["status"] == "skipped"
    assert report["paper_can_continue_to_p13"] is False
    assert failures["unresolved_failure_count"] == 2
    assert {failure["check_id"] for failure in failures["failures"]} == {
        "clean_clone_install_contract_ready",
        "live_or_declared_leak_scan_passed",
    }
    assert go_no_go["paper_can_continue_to_p13"] is False
    assert "python -m relaytic.ui.cli release-safety paper-dry-run --run-isolated-install --format json" in report["paper_smoke_subset"]["commands"]


def test_paper_track_p12_cli_writes_reports(
    tmp_path: Path,
    capsys: Any,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    output_dir = tmp_path / "reports"
    monkeypatch.chdir(PROJECT_ROOT)

    exit_code = main(
        [
            "release-safety",
            "paper-dry-run",
            "--skip-live-checks",
            "--output-dir",
            str(output_dir),
            "--format",
            "json",
        ]
    )

    assert exit_code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["status"] == "blocked_pending_dry_run_repairs"
    assert payload["paper_reproduction_failure_report"]["unresolved_failure_count"] == 2
    for filename in PAPER_DRY_RUN_FILENAMES.values():
        assert (output_dir / filename).exists(), filename


def test_paper_track_p12_fails_closed_without_paper_inputs(tmp_path: Path) -> None:
    pack = build_paper_dry_run_pack(tmp_path, run_live_checks=False)

    report = pack["paper_external_dry_run_report"]
    failures = pack["paper_reproduction_failure_report"]
    go_no_go = pack["paper_release_go_no_go"]

    assert report["status"] == "blocked_pending_dry_run_repairs"
    assert failures["unresolved_failure_count"] >= 3
    assert failures["arxiv_release_blocked"] is True
    assert go_no_go["paper_can_continue_to_p13"] is False
    assert any(check["check_id"] == "committed_claim_lint_passed" and not check["passed"] for check in report["checks"])


def test_paper_track_p12_committed_reports_allow_p13_claim_safe_mode() -> None:
    for filename in PAPER_DRY_RUN_FILENAMES.values():
        assert (REPORT_DIR / filename).exists(), filename

    report = _load_report("paper_external_dry_run_report.json")
    install = _load_report("paper_clean_clone_install_report.json")
    failures = _load_report("paper_reproduction_failure_report.json")
    go_no_go = _load_report("paper_release_go_no_go.json")
    checklist = (REPORT_DIR / "paper_clean_clone_checklist.md").read_text(encoding="utf-8")

    assert report["status"] == "pass_paper_smoke_reproduced_claim_linted"
    assert report["paper_can_continue_to_p13"] is True
    assert report["leak_scan"]["passed"] is True
    assert install["status"] == "pass_clean_clone_ready"
    assert failures["status"] == "no_failures"
    assert failures["arxiv_release_blocked"] is False
    assert go_no_go["status"] == "go_for_p13_claim_safe_release_pack"
    assert go_no_go["paper_can_continue_to_p13"] is True
    assert go_no_go["hard_claims_allowed"] is False
    assert go_no_go["headline_claims_allowed"] is False
    assert "scan-git-safety" in checklist
