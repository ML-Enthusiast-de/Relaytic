from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from relaytic.release_safety import (
    PAPER_OPERATIONAL_METRICS_FILENAMES,
    build_paper_operational_metrics_pack,
)
from relaytic.ui.cli import main


PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = PROJECT_ROOT / "docs" / "reports"
pytestmark = pytest.mark.prepush


def _write_p9_input_reports(root: Path) -> None:
    reports = root / "docs" / "reports"
    reports.mkdir(parents=True, exist_ok=True)
    (reports / "paper_p8d_thesis_decision.json").write_text(
        json.dumps(
            {
                "schema_version": "relaytic.paper_p8d_thesis_decision.v1",
                "slice": "Paper Track P8-D",
                "status": "accepted_thesis_narrowing",
                "selected_route": "narrow_first_paper_to_claim_gated_evaluation_environment",
                "p9_allowed": True,
                "elliptic2_performance_contribution_allowed": False,
            }
        ),
        encoding="utf-8",
    )
    (reports / "paper_p8d_evidence_role_matrix.json").write_text(
        json.dumps({"schema_version": "relaytic.paper_p8d_thesis_decision.v1"}),
        encoding="utf-8",
    )
    (reports / "paysim_competitive_benchmark_manifest.json").write_text(
        json.dumps(
            {
                "effective_budget_tier": "competitive",
                "validation_selected_competitive_model": {
                    "family_id": "sklearn_extra_trees",
                    "review_budget_fraction": 0.005,
                    "test_pr_auc": 0.64,
                    "test_roc_auc": 0.97,
                    "test_operating_point": {
                        "requested_review_fraction": 0.005,
                        "review_fraction": 0.009,
                        "reviewed_count": 100,
                        "true_positive_count": 70,
                        "false_positive_count": 30,
                        "precision_at_k": 0.7,
                        "recall_at_review_budget": 0.5,
                        "false_positive_rate": 0.003,
                    },
                    "fixed_fpr": {
                        "target_fpr": 0.001,
                        "test": {
                            "reviewed_count": 80,
                            "true_positive_count": 68,
                            "false_positive_count": 12,
                            "precision_at_k": 0.85,
                            "recall_at_review_budget": 0.486,
                            "false_positive_rate": 0.001,
                        },
                    },
                },
            }
        ),
        encoding="utf-8",
    )
    (reports / "paysim_competitive_baseline_table.json").write_text(
        json.dumps(
            {
                "rows": [
                    {
                        "selected_for_test_evaluation": True,
                        "test_metrics": {
                            "post_calibration": {
                                "n_samples": 10000,
                                "positive_count": 200,
                                "positive_rate": 0.02,
                            }
                        },
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    (reports / "paysim_publishability_gate.json").write_text(
        json.dumps({"blocked_reason_codes": ["paysim_is_supporting_proxy_not_real_bank_holdout"]}),
        encoding="utf-8",
    )
    (reports / "paysim_operating_point_table.json").write_text(
        json.dumps(
            {
                "model_family": "sklearn_sgd_logistic_leakage_safe",
                "review_budget_rows": [
                    {
                        "review_budget_fraction": 0.005,
                        "test": {
                            "reviewed_count": 120,
                            "true_positive_count": 45,
                            "false_positive_count": 75,
                            "precision_at_k": 0.375,
                            "recall_at_review_budget": 0.225,
                            "false_positive_rate": 0.0075,
                        },
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    (reports / "paper_graph_feature_table.json").write_text(
        json.dumps(
            {
                "effective_budget_tier": "competitive",
                "validation_selected_competitive_baseline": {
                    "family_id": "lightgbm_classifier",
                    "trial_id": "graph::lgbm::1",
                    "review_budget_fraction": 0.005,
                    "test_pr_auc": 0.67,
                    "test_roc_auc": 0.89,
                    "test_operating_point": {
                        "requested_review_fraction": 0.005,
                        "review_fraction": 0.003,
                        "reviewed_count": 36,
                        "true_positive_count": 36,
                        "false_positive_count": 0,
                        "precision_at_k": 1.0,
                        "recall_at_review_budget": 0.06,
                        "false_positive_rate": 0.0,
                    },
                    "fixed_fpr": {
                        "target_fpr": 0.001,
                        "test": {
                            "reviewed_count": 388,
                            "true_positive_count": 369,
                            "false_positive_count": 19,
                            "precision_at_k": 0.951,
                            "recall_at_review_budget": 0.58,
                            "false_positive_rate": 0.0018,
                        },
                    },
                },
                "rows": [
                    {
                        "trial_id": "graph::lgbm::1",
                        "global_validation_selected": True,
                        "test_metrics": {
                            "pr_auc": 0.67,
                            "roc_auc": 0.89,
                        },
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    (reports / "elliptic_temporal_split_report.json").write_text(
        json.dumps(
            {
                "split_rows": [
                    {
                        "split": "test",
                        "known_label_count": 1000,
                        "illicit_count": 50,
                        "positive_rate_labeled": 0.05,
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    (reports / "paper_graph_publishability_gate.json").write_text(
        json.dumps({"blocked_reason_codes": ["graph_sota_claim_not_benchmarked"]}),
        encoding="utf-8",
    )
    (reports / "subgraph_benchmark_blocker_report.json").write_text(
        json.dumps({"status": "blocked"}),
        encoding="utf-8",
    )


def _load_report(name: str) -> dict[str, Any]:
    return json.loads((REPORT_DIR / name).read_text(encoding="utf-8"))


def test_paper_track_p9_reports_review_budget_metrics_and_blocks_hard_claims(tmp_path: Path) -> None:
    _write_p9_input_reports(tmp_path)

    pack = build_paper_operational_metrics_pack(tmp_path)
    table = pack["paper_operational_metric_table"]
    curve = pack["paper_review_budget_curve"]
    case_packet = pack["paper_case_packet_completeness_report"]
    guard = pack["paper_operational_claim_guard"]

    assert set(pack) == set(PAPER_OPERATIONAL_METRICS_FILENAMES)
    assert table["status"] == "operational_metrics_reported_with_claim_guard"
    assert table["row_count"] == 2
    assert table["rows_with_review_budget_metrics"] == 2
    assert curve["curve_count"] == 3
    assert case_packet["status"] == "case_packets_missing_for_paper_benchmark_rows"
    assert guard["status"] == "supporting_operational_metrics_ready_hard_claims_blocked"
    assert guard["paper_can_continue_to_p10"] is True
    assert guard["hard_business_value_claim_allowed"] is False
    assert "paper_benchmark_case_packets_missing" in guard["blocked_reason_codes"]

    paysim = table["rows"][0]
    graph = table["rows"][1]
    assert paysim["operational_estimates"]["prevalence_matched_baseline_cases_for_same_true_positives"] == 3500
    assert graph["model_metrics"]["n_samples"] == 1000
    assert graph["model_metrics"]["positive_count"] == 50
    assert graph["operational_estimates"]["prevalence_matched_baseline_cases_for_same_true_positives"] == 720


def test_paper_track_p9_fails_closed_without_p8d_acceptance(tmp_path: Path) -> None:
    pack = build_paper_operational_metrics_pack(tmp_path)

    table = pack["paper_operational_metric_table"]
    guard = pack["paper_operational_claim_guard"]

    assert table["status"] == "blocked_pending_p8d_thesis_decision"
    assert table["row_count"] == 0
    assert guard["status"] == "blocked"
    assert guard["paper_can_continue_to_p10"] is False
    assert "p8d_thesis_decision_not_accepted" in guard["blocked_reason_codes"]


def test_paper_track_p9_cli_writes_machine_readable_reports(
    tmp_path: Path,
    capsys: Any,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _write_p9_input_reports(tmp_path)
    output_dir = tmp_path / "reports"
    monkeypatch.chdir(tmp_path)

    exit_code = main(
        [
            "release-safety",
            "paper-operational-metrics",
            "--output-dir",
            str(output_dir),
            "--format",
            "json",
        ]
    )

    assert exit_code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["status"] == "supporting_operational_metrics_ready_hard_claims_blocked"
    assert payload["paper_operational_claim_guard"]["paper_can_continue_to_p10"] is True
    assert (output_dir / "paper_operational_metric_table.json").exists()
    assert (output_dir / "paper_operational_claim_guard.json").exists()


def test_paper_track_p9_committed_reports_unlock_p10_but_not_business_claims() -> None:
    for filename in PAPER_OPERATIONAL_METRICS_FILENAMES.values():
        assert (REPORT_DIR / filename).exists(), filename

    table = _load_report("paper_operational_metric_table.json")
    curve = _load_report("paper_review_budget_curve.json")
    case_packet = _load_report("paper_case_packet_completeness_report.json")
    guard = _load_report("paper_operational_claim_guard.json")

    assert table["status"] == "operational_metrics_reported_with_claim_guard"
    assert table["rows_with_review_budget_metrics"] >= 1
    assert curve["status"] == "review_budget_curves_materialized"
    assert case_packet["status"] == "case_packets_missing_for_paper_benchmark_rows"
    assert guard["paper_can_continue_to_p10"] is True
    assert guard["hard_business_value_claim_allowed"] is False
    assert guard["headline_operational_claim_allowed"] is False
    assert "elliptic2_excluded_from_operational_performance_contribution_by_p8d" in guard["blocked_reason_codes"]

    paysim = next(row for row in table["rows"] if row["dataset_id"] == "paysim_temporal_transaction_fraud")
    graph = next(row for row in table["rows"] if row["dataset_id"] == "elliptic_flattened_graph_aml")
    assert paysim["review_budget_metrics"]["precision_at_k"] >= 0.7
    assert "graph_benchmark_evidence_not_yet_executed_p7_required" not in paysim["blocked_reason_codes"]
    assert paysim["operational_estimates"]["prevalence_matched_baseline_cases_for_same_true_positives"] is not None
    assert graph["model_metrics"]["positive_count"] is not None
    assert graph["operational_estimates"]["prevalence_matched_baseline_cases_for_same_true_positives"] is not None
