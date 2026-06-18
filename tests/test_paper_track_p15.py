from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from relaytic.release_safety import (
    PAPER_SYSTEM_EVAL_FILENAMES,
    build_paper_system_eval_pack,
)
from relaytic.ui.cli import main


PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = PROJECT_ROOT / "docs" / "reports"
PAPER_DIR = PROJECT_ROOT / "docs" / "paper"
pytestmark = pytest.mark.prepush


def _load_report(name: str) -> dict[str, Any]:
    return json.loads((REPORT_DIR / name).read_text(encoding="utf-8"))


def test_paper_track_p15_builds_measured_system_eval_pack(tmp_path: Path) -> None:
    pack = build_paper_system_eval_pack(PROJECT_ROOT, state_dir=tmp_path / "state")

    manifest = pack["paper_system_eval_manifest"]
    behavior = pack["paper_system_behavior_eval"]
    task_eval = pack["paper_system_task_eval"]
    no_lost = pack["paper_no_lost_user_eval"]
    handoff = pack["paper_agent_handoff_eval"]
    cases = pack["paper_claim_gate_case_studies"]
    serialized = json.dumps(pack, sort_keys=True)

    assert manifest["status"] == "ready_for_system_evaluation_evidence"
    assert manifest["system_evaluation_claim_allowed"] is True
    assert manifest["human_study_claim_allowed"] is False
    assert not manifest["failed_checks"]
    assert behavior["status"] == "pass"
    assert behavior["pass_rate"] == 1.0
    assert behavior["raw_rows_exposed"] is False
    assert behavior["private_paths_exposed"] is False
    assert task_eval["status"] == "pass"
    assert task_eval["task_count"] >= 10
    assert task_eval["passed_task_count"] == task_eval["task_count"]
    assert not task_eval["failed_tasks"]
    assert no_lost["status"] == "pass"
    assert handoff["status"] == "pass"
    assert cases["status"] == "pass"
    task_ids = {
        str(row.get("task"))
        for row in behavior["evaluation_rows"]
    }
    assert {
        "onboarding_guide_available",
        "partial_run_state_recovery",
        "external_context_rowless_and_redacted",
        "server_tool_contract_available",
        "repo_navigation_separates_relaytic_from_aml_paper",
        "metric_cell_provenance_available",
        "paysim_baseline_and_competitive_budget_comparable",
        "elliptic2_supporting_context_and_firewall_visible",
        "rowless_external_agent_handoff_recoverable",
        "p12_go_no_go_blocks_hard_and_headline_claims",
    }.issubset(task_ids)
    assert "/private/local/data.csv" not in serialized
    assert str(tmp_path).replace("\\", "/") not in serialized.replace("\\", "/")


def test_paper_track_p15_cli_writes_reports(tmp_path: Path, capsys: Any, monkeypatch: pytest.MonkeyPatch) -> None:
    output_dir = tmp_path / "reports"
    state_dir = tmp_path / "state"
    monkeypatch.chdir(PROJECT_ROOT)

    exit_code = main(
        [
            "release-safety",
            "paper-system-eval",
            "--state-dir",
            str(state_dir),
            "--output-dir",
            str(output_dir),
            "--format",
            "json",
        ]
    )

    assert exit_code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["status"] == "ready_for_system_evaluation_evidence"
    assert payload["paper_system_behavior_eval"]["status"] == "pass"
    assert payload["paper_system_task_eval"]["status"] == "pass"
    for filename in PAPER_SYSTEM_EVAL_FILENAMES.values():
        assert (output_dir / filename).exists(), filename


def test_paper_track_p15_fails_closed_without_claim_gate_inputs(tmp_path: Path) -> None:
    pack = build_paper_system_eval_pack(tmp_path, state_dir=tmp_path / "state")
    manifest = pack["paper_system_eval_manifest"]
    behavior = pack["paper_system_behavior_eval"]
    task_eval = pack["paper_system_task_eval"]
    cases = pack["paper_claim_gate_case_studies"]

    assert manifest["status"] == "blocked_pending_system_evaluation_repairs"
    assert manifest["system_evaluation_claim_allowed"] is False
    assert behavior["status"] == "fail"
    assert task_eval["status"] == "fail"
    assert cases["status"] == "fail"
    assert any(
        check["check_id"] == "required_claim_gate_inputs_present" and not check["passed"]
        for check in manifest["checks"]
    )


def test_paper_track_p15_committed_system_eval_artifacts_are_ready() -> None:
    for filename in PAPER_SYSTEM_EVAL_FILENAMES.values():
        assert (REPORT_DIR / filename).exists(), filename

    manifest = _load_report("paper_system_eval_manifest.json")
    behavior = _load_report("paper_system_behavior_eval.json")
    task_eval = _load_report("paper_system_task_eval.json")
    handoff = _load_report("paper_agent_handoff_eval.json")
    no_lost = _load_report("paper_no_lost_user_eval.json")
    summary = (REPORT_DIR / "paper_system_eval_summary.md").read_text(encoding="utf-8")
    draft = (PAPER_DIR / "relaytic_aml_arxiv_draft.md").read_text(encoding="utf-8")

    assert manifest["status"] == "ready_for_system_evaluation_evidence"
    assert behavior["status"] == "pass"
    assert behavior["pass_rate"] == 1.0
    assert task_eval["status"] == "pass"
    assert task_eval["task_count"] >= 10
    assert not task_eval["failed_tasks"]
    assert handoff["status"] == "pass"
    assert no_lost["status"] == "pass"
    assert "Paper P15 System-Evaluation Proof Pack" in summary
    assert "The system claim is evaluated through deterministic reader and agent tasks." in draft
    assert "rowless external-agent handoff works" in draft
    assert "Table 5 summarizes the protocol audit" in draft
    assert "current deterministic suite reports no raw-row exposure and no private-path exposure" in draft
