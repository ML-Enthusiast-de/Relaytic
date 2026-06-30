from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from relaytic.release_safety import (
    PAPER_FAILURE_EVAL_FILENAMES,
    build_paper_failure_eval_pack,
)
from relaytic.ui.cli import main


PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = PROJECT_ROOT / "docs" / "reports"
PAPER_DIR = PROJECT_ROOT / "docs" / "paper"
pytestmark = pytest.mark.prepush


def _load_report(name: str) -> dict[str, Any]:
    return json.loads((REPORT_DIR / name).read_text(encoding="utf-8"))


def test_paper_track_p16_builds_failure_case_eval_pack() -> None:
    pack = build_paper_failure_eval_pack(PROJECT_ROOT)

    manifest = pack["paper_failure_case_manifest"]
    evaluation = pack["paper_failure_case_eval"]
    table = pack["paper_failure_case_table"]
    case_ids = {case["case_id"] for case in evaluation["cases"]}
    serialized = json.dumps(pack, sort_keys=True)

    assert manifest["status"] == "ready_for_failure_case_evidence"
    assert manifest["failure_case_evidence_allowed"] is True
    assert manifest["hard_claims_allowed"] is False
    assert manifest["headline_claims_allowed"] is False
    assert manifest["detector_superiority_claim_allowed"] is False
    assert evaluation["status"] == "pass"
    assert evaluation["case_count"] == 5
    assert evaluation["passed_case_count"] == 5
    assert table["status"] == "pass"
    assert len(table["rows"]) == 5
    assert {
        "leakage_column_injection",
        "test_set_selection_violation",
        "overstrong_claim_attempt",
        "rowless_handoff_redaction",
        "interrupted_run_recovery",
    } <= case_ids
    assert "offered=4; excluded=4; used=0" in serialized
    assert "test_used_for_selection=False" in serialized
    assert "hard_allowed=False" in serialized
    assert "raw_rows=False; redactions=8; blocked_fields=6" in serialized
    assert "state=partial_run; missing=8; actions=6" in serialized
    assert "not detector benchmarks" in evaluation["interpretation"]
    assert str(PROJECT_ROOT).replace("\\", "/") not in serialized.replace("\\", "/")


def test_paper_track_p16_cli_writes_reports(
    tmp_path: Path,
    capsys: Any,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    output_dir = tmp_path / "reports"
    monkeypatch.chdir(PROJECT_ROOT)

    exit_code = main(
        [
            "release-safety",
            "paper-failure-eval",
            "--output-dir",
            str(output_dir),
            "--format",
            "json",
        ]
    )

    assert exit_code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["status"] == "ready_for_failure_case_evidence"
    assert payload["paper_failure_case_eval"]["status"] == "pass"
    assert payload["paper_failure_case_table"]["status"] == "pass"
    for filename in PAPER_FAILURE_EVAL_FILENAMES.values():
        assert (output_dir / filename).exists(), filename


def test_paper_track_p16_fails_closed_without_required_inputs(tmp_path: Path) -> None:
    pack = build_paper_failure_eval_pack(tmp_path)
    manifest = pack["paper_failure_case_manifest"]
    evaluation = pack["paper_failure_case_eval"]

    assert manifest["status"] == "blocked_missing_failure_case_evidence"
    assert manifest["failure_case_evidence_allowed"] is False
    assert evaluation["status"] == "fail"
    assert evaluation["passed_case_count"] < evaluation["case_count"]
    assert any(
        check["check_id"] == "required_failure_case_inputs_present" and not check["passed"]
        for check in manifest["checks"]
    )
    assert manifest["failed_checks"]


def test_paper_track_p16_committed_failure_case_artifacts_are_ready() -> None:
    for filename in PAPER_FAILURE_EVAL_FILENAMES.values():
        assert (REPORT_DIR / filename).exists(), filename

    manifest = _load_report("paper_failure_case_manifest.json")
    evaluation = _load_report("paper_failure_case_eval.json")
    table = _load_report("paper_failure_case_table.json")
    summary = (REPORT_DIR / "paper_failure_case_summary.md").read_text(encoding="utf-8")
    draft = (PAPER_DIR / "relaytic_aml_arxiv_draft.md").read_text(encoding="utf-8")

    assert manifest["status"] == "ready_for_failure_case_evidence"
    assert not manifest["failed_checks"]
    assert evaluation["status"] == "pass"
    assert evaluation["case_count"] == 5
    assert evaluation["passed_case_count"] == 5
    assert evaluation["raw_rows_exposed"] is False
    assert evaluation["private_paths_exposed"] is False
    assert table["status"] == "pass"
    assert "Paper P16 Failure-Case Evaluation Pack" in summary
    assert "Table 6. Failure-case evaluation" in draft
    assert "Leakage-column injection" in draft
    assert "Table 10 gives the practical external-agent story" in draft
