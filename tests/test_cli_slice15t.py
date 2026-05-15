from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from relaytic.aml import build_aml_business_value_artifacts
from relaytic.ui.cli import main


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _seed_operational_disagreement_run(run_dir: Path) -> None:
    run_dir.mkdir(parents=True, exist_ok=True)
    _write_json(
        run_dir / "alert_queue_policy.json",
        {
            "schema_version": "relaytic.alert_queue_policy.v1",
            "status": "active",
            "review_capacity_cases": 2,
            "review_budget_fraction": 0.4,
        },
    )
    _write_json(
        run_dir / "alert_queue_rankings.json",
        {
            "schema_version": "relaytic.alert_queue_rankings.v1",
            "status": "active",
            "queue_count": 5,
            "review_capacity_cases": 2,
            "ranking": [
                {"rank": 1, "case_id": "case_a", "entity_id": "A", "suspicious_rate": 0.05, "priority_score": 0.91},
                {"rank": 2, "case_id": "case_b", "entity_id": "B", "suspicious_rate": 0.05, "priority_score": 0.88},
                {"rank": 3, "case_id": "case_c", "entity_id": "C", "suspicious_rate": 0.80, "priority_score": 0.50},
                {"rank": 4, "case_id": "case_d", "entity_id": "D", "suspicious_rate": 0.70, "priority_score": 0.42},
                {"rank": 5, "case_id": "case_e", "entity_id": "E", "suspicious_rate": 0.60, "priority_score": 0.30},
            ],
        },
    )
    _write_json(
        run_dir / "analyst_review_scorecard.json",
        {
            "schema_version": "relaytic.analyst_review_scorecard.v1",
            "status": "active",
            "total_case_count": 5,
            "review_capacity_cases": 2,
        },
    )
    _write_json(
        run_dir / "case_packet.json",
        {
            "schema_version": "relaytic.case_packet.v1",
            "status": "active",
            "case_id": "case_a",
            "focal_entity": "A",
            "priority_score": 0.91,
            "review_action": "review_now",
        },
    )
    _write_json(
        run_dir / "review_capacity_sensitivity.json",
        {
            "schema_version": "relaytic.review_capacity_sensitivity.v1",
            "status": "active",
            "rows": [
                {"review_fraction": 0.2, "review_capacity_cases": 1},
                {"review_fraction": 0.4, "review_capacity_cases": 2},
                {"review_fraction": 0.8, "review_capacity_cases": 4},
            ],
        },
    )
    _write_json(
        run_dir / "benchmark_parity_report.json",
        {
            "schema_version": "relaytic.benchmark_parity_report.v1",
            "status": "ok",
            "parity_status": "meets_or_exceeds_reference",
            "comparison_metric": "roc_auc",
        },
    )
    _write_json(
        run_dir / "benchmark_gap_report.json",
        {
            "schema_version": "relaytic.benchmark_gap_report.v1",
            "status": "ok",
            "comparison_metric": "roc_auc",
            "relaytic_beats_best_reference": True,
            "near_parity": True,
            "test_gap": 0.04,
        },
    )
    _write_json(
        run_dir / "reference_approach_matrix.json",
        {
            "schema_version": "relaytic.reference_approach_matrix.v1",
            "status": "ok",
            "comparison_metric": "roc_auc",
            "relaytic_reference": {"model_family": "relaytic_candidate", "test_metric": {"roc_auc": 0.93}},
            "references": [{"model_family": "strong_reference", "test_metric": {"roc_auc": 0.89}}],
        },
    )
    _write_json(
        run_dir / "external_challenger_manifest.json",
        {
            "schema_version": "relaytic.external_challenger_manifest.v1",
            "status": "ok",
            "incumbent_name": "legacy_alert_engine",
            "incumbent_kind": "predictions",
        },
    )
    _write_json(
        run_dir / "external_challenger_evaluation.json",
        {
            "schema_version": "relaytic.external_challenger_evaluation.v1",
            "status": "ok",
            "incumbent_name": "legacy_alert_engine",
            "comparison_metric": "roc_auc",
            "test_metric": {"roc_auc": 0.87, "relaytic_metric_value": 0.93},
        },
    )
    _write_json(
        run_dir / "incumbent_parity_report.json",
        {
            "schema_version": "relaytic.incumbent_parity_report.v1",
            "status": "ok",
            "incumbent_present": True,
            "incumbent_name": "legacy_alert_engine",
            "parity_status": "relaytic_beats_incumbent",
            "comparison_metric": "roc_auc",
            "relaytic_beats_incumbent": True,
            "incumbent_stronger": False,
            "test_gap": 0.06,
        },
    )


def test_slice15t_business_value_unit_blocks_model_score_overclaim(tmp_path: Path) -> None:
    run_dir = tmp_path / "slice15t_unit"
    _seed_operational_disagreement_run(run_dir)

    bundle = build_aml_business_value_artifacts(run_dir=run_dir)
    guard = bundle["operational_metric_guard"]
    hours = bundle["analyst_hour_savings_report"]
    capacity = bundle["review_capacity_metric_report"]

    assert capacity["precision_at_top_k"] < 0.1
    assert hours["analyst_hours_saved_at_fixed_recall"] < 0
    assert guard["hard_business_value_claim_allowed"] is False
    assert guard["model_operational_disagreement"] is True
    assert "model_score_operational_utility_disagree" in guard["blocked_reason_codes"]
    assert "analyst_hour_assumption_defaulted" in guard["blocked_reason_codes"]


def test_cli_slice15t_writes_guarded_business_value_and_incumbent_tradeoff(
    tmp_path: Path,
    capsys: Any,
) -> None:
    run_dir = tmp_path / "slice15t_cli"
    _seed_operational_disagreement_run(run_dir)

    assert main(["aml", "business-value", "--run-dir", str(run_dir), "--format", "json"]) == 0
    payload = json.loads(capsys.readouterr().out)

    assert payload["status"] == "ok"
    assert payload["aml_business_value"]["operational_guard_status"] == "blocked"
    assert payload["aml_business_value"]["model_operational_disagreement"] is True
    assert payload["aml_business_value"]["incumbent_present"] is True
    assert payload["aml_business_value"]["incumbent_operational_comparison_scope"] == "metric_only_incumbent_queue_missing"

    for artifact_name in (
        "aml_business_value_report.json",
        "analyst_hour_savings_report.json",
        "review_capacity_metric_report.json",
        "operational_metric_guard.json",
    ):
        assert (run_dir / artifact_name).exists(), artifact_name

    report = json.loads((run_dir / "aml_business_value_report.json").read_text(encoding="utf-8"))
    guard = json.loads((run_dir / "operational_metric_guard.json").read_text(encoding="utf-8"))
    assert report["incumbent_tradeoff"]["analyst_capacity_tradeoff"]["relaytic_review_capacity_cases"] == 2
    assert report["incumbent_tradeoff"]["operational_claim_allowed"] is False
    assert "incumbent_queue_operational_evidence_missing" in guard["blocked_reason_codes"]
