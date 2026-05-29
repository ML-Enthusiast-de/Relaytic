from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from relaytic.release_safety import (
    PAPER_THESIS_DECISION_FILENAMES,
    build_paper_hard_graph_track_pack,
    build_paper_p8d_thesis_pack,
)
from relaytic.ui.cli import main


PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = PROJECT_ROOT / "docs" / "reports"
pytestmark = pytest.mark.prepush


def _write_minimal_p8bc_reports(root: Path) -> None:
    reports = root / "docs" / "reports"
    reports.mkdir(parents=True, exist_ok=True)
    (reports / "elliptic2_publishability_gate.json").write_text(
        json.dumps(
            {
                "schema_version": "relaytic.elliptic2_competitive.v1",
                "slice": "Paper Track P8-B",
                "status": "pass_supporting_modern_context_only",
                "supporting_paper_row_allowed": True,
                "reference_parity_claim_allowed": False,
                "headline_or_sota_claim_allowed": False,
                "selected_official_test_pr_auc_mean": 0.94324,
                "published_reference_pr_auc": 0.974,
                "official_gap_to_published_revclassify_ds": -0.03076,
            }
        ),
        encoding="utf-8",
    )
    (reports / "elliptic2_reference_parity_gate.json").write_text(
        json.dumps(
            {
                "schema_version": "relaytic.elliptic2_reference_parity.v1",
                "slice": "Paper Track P8-C",
                "status": "blocked_supporting_only_thesis_narrowing_required",
                "supporting_modern_context_row_allowed": True,
                "reference_parity_claim_allowed": False,
                "headline_or_sota_claim_allowed": False,
                "full_core_modern_subgraph_claim_allowed": False,
                "p9_allowed": False,
                "paper_strategy_decision": "narrow_or_reprovision_before_p9",
                "blocked_reason_codes": ["faithful_revclassify_execution_preconditions_met"],
            }
        ),
        encoding="utf-8",
    )
    (reports / "elliptic2_entity_disjoint_split_report.json").write_text(
        json.dumps(
            {
                "slice": "Paper Track P8-C",
                "status": "blocked_degenerate_component_structure",
                "strict_entity_disjoint_split_viable": False,
                "strict_component_protocol": {
                    "all_role_entity_components": {
                        "largest_component_row_count": 110889,
                        "largest_component_row_fraction": 0.99988278,
                    }
                },
            }
        ),
        encoding="utf-8",
    )
    (reports / "elliptic2_evaluable_cohort_reconciliation.json").write_text(
        json.dumps(
            {
                "slice": "Paper Track P8-C",
                "status": "blocked_full_core_equivalence_not_proven",
                "revtrack_evaluable_row_count": 110902,
                "official_core_subgraph_count": 121810,
                "full_core_equivalence_proven": False,
            }
        ),
        encoding="utf-8",
    )
    (reports / "elliptic2_neural_candidate_scorecard.json").write_text(
        json.dumps(
            {
                "slice": "Paper Track P8-C",
                "status": "blocked_no_faithful_neural_scorecard",
                "run_neural_requested": True,
                "neural_reference_parity_met": False,
                "best_local_neural_pr_auc_mean": None,
            }
        ),
        encoding="utf-8",
    )


def _load_report(name: str) -> dict[str, Any]:
    return json.loads((REPORT_DIR / name).read_text(encoding="utf-8"))


def test_paper_track_p8d_accepts_narrowing_from_direct_p8b_p8c_gates(tmp_path: Path) -> None:
    _write_minimal_p8bc_reports(tmp_path)

    pack = build_paper_p8d_thesis_pack(tmp_path)
    decision = pack["paper_p8d_thesis_decision"]
    matrix = pack["paper_p8d_evidence_role_matrix"]
    reprovision = pack["paper_p8d_reprovisioning_decision"]
    claims = pack["paper_p8d_claim_rewrite_plan"]

    assert set(pack) == set(PAPER_THESIS_DECISION_FILENAMES)
    assert decision["status"] == "accepted_thesis_narrowing"
    assert decision["p9_allowed"] is True
    assert decision["elliptic2_performance_contribution_allowed"] is False
    assert decision["gate_summary"]["p8b"]["supporting_paper_row_allowed"] is True
    assert decision["gate_summary"]["p8c"]["reference_parity_claim_allowed"] is False
    assert decision["gate_summary"]["entity_split"]["largest_component_row_fraction"] == pytest.approx(0.99988278)
    assert matrix["table_rules"]["primary_performance_table_can_include_elliptic2"] is False
    assert reprovision["selected_strategy"] == "defer_faithful_revclassify_reprovisioning_for_first_paper"
    assert claims["claim_language_updated"] is True
    assert "Relaytic-AML is state of the art on Elliptic2." in claims["blocked_claim_language"]


def test_paper_track_p8d_fails_closed_when_p8c_gate_is_missing(tmp_path: Path) -> None:
    pack = build_paper_p8d_thesis_pack(tmp_path)

    decision = pack["paper_p8d_thesis_decision"]
    matrix = pack["paper_p8d_evidence_role_matrix"]

    assert decision["status"] == "blocked_pending_p8b_p8c_gate_truth"
    assert decision["p9_allowed"] is False
    assert decision["selected_route"] == "no_accepted_thesis_route"
    assert matrix["status"] == "blocked_pending_accepted_route"


def test_paper_track_p8d_cli_writes_machine_readable_reports(
    tmp_path: Path,
    capsys: Any,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _write_minimal_p8bc_reports(tmp_path)
    output_dir = tmp_path / "reports"
    monkeypatch.chdir(tmp_path)

    exit_code = main(
        [
            "release-safety",
            "paper-thesis-decision",
            "--output-dir",
            str(output_dir),
            "--format",
            "json",
        ]
    )

    assert exit_code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["status"] == "accepted_thesis_narrowing"
    assert payload["paper_p8d_thesis_decision"]["p9_allowed"] is True
    assert (output_dir / "paper_p8d_thesis_decision.json").exists()


def test_paper_track_p8d_committed_reports_unblock_p9_without_elliptic2_contribution() -> None:
    for filename in PAPER_THESIS_DECISION_FILENAMES.values():
        assert (REPORT_DIR / filename).exists(), filename

    decision = _load_report("paper_p8d_thesis_decision.json")
    matrix = _load_report("paper_p8d_evidence_role_matrix.json")
    claims = _load_report("paper_p8d_claim_rewrite_plan.json")
    blocker_pack = build_paper_hard_graph_track_pack(
        PROJECT_ROOT,
        elliptic2_dir=PROJECT_ROOT / "data" / "paper_benchmarks" / "missing_elliptic2_for_test",
        amlsim_dir=PROJECT_ROOT / "data" / "paper_benchmarks" / "missing_amlsim_for_test",
    )
    blocker = blocker_pack["subgraph_benchmark_blocker_report"]

    assert decision["status"] == "accepted_thesis_narrowing"
    assert decision["p9_allowed"] is True
    assert decision["elliptic2_performance_contribution_allowed"] is False
    assert matrix["table_rules"]["primary_performance_table_can_include_elliptic2"] is False
    assert claims["claim_language_updated"] is True
    assert blocker["decision_state"] == "hard_tracks_blocked_with_p8d_thesis_narrowing_accepted"
    assert blocker["paper_can_continue_to_p9"] is True
    assert blocker["next_slice"].startswith("Paper Track P9")
