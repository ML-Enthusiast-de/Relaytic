from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from relaytic.aml import build_aml_baseline_artifacts, sync_aml_business_value_artifacts
from relaytic.ui.cli import main


SLICE15U_ARTIFACTS = (
    "aml_baseline_matrix.json",
    "aml_ablation_matrix.json",
    "aml_baseline_adapter_report.json",
    "aml_capability_contribution_report.json",
    "aml_benchmark_relevance_scorecard.json",
)


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _seed_aml_baseline_run(run_dir: Path) -> None:
    run_dir.mkdir(parents=True, exist_ok=True)
    _write_json(
        run_dir / "aml_domain_contract.json",
        {
            "schema_version": "relaytic.aml_domain_contract.v1",
            "status": "active",
            "aml_active": True,
            "domain_focus": "payment fraud and AML transaction monitoring",
            "target_level": "transaction_or_entity_case",
            "business_goal": "prioritize analyst review capacity",
        },
    )
    _write_json(
        run_dir / "task_profile_contract.json",
        {
            "schema_version": "relaytic.task_profile_contract.v1",
            "status": "ok",
            "task_type": "binary_classification",
            "target_column": "isFraud",
            "timestamp_column": "step",
            "rare_event_supervised": True,
        },
    )
    _write_json(
        run_dir / "reference_approach_matrix.json",
        {
            "schema_version": "relaytic.reference_approach_matrix.v1",
            "status": "ok",
            "comparison_metric": "pr_auc",
            "metric_direction": "maximize",
            "relaytic_reference": {
                "role": "relaytic",
                "model_family": "hist_gradient_boosting",
                "test_metric": {"pr_auc": 0.91},
            },
            "references": [
                {"role": "reference", "model_family": "sklearn_logistic_regression", "test_metric": {"pr_auc": 0.77}},
                {"role": "reference", "model_family": "sklearn_random_forest_classifier", "test_metric": {"pr_auc": 0.83}},
                {"role": "reference", "model_family": "sklearn_gradient_boosting_classifier", "test_metric": {"pr_auc": 0.86}},
                {"role": "reference", "model_family": "sklearn_lagged_logistic_regression", "test_metric": {"pr_auc": 0.80}},
            ],
        },
    )
    _write_json(
        run_dir / "paper_benchmark_table.json",
        {
            "schema_version": "relaytic.paper_benchmark_table.v1",
            "status": "ok",
            "comparison_metric": "pr_auc",
            "rows": [
                {"rank": 1, "role": "relaytic", "model_family": "hist_gradient_boosting", "test_metric": 0.91},
                {"rank": 2, "role": "reference", "model_family": "sklearn_gradient_boosting_classifier", "test_metric": 0.86},
            ],
        },
    )
    _write_json(
        run_dir / "benchmark_ablation_matrix.json",
        {
            "schema_version": "relaytic.benchmark_ablation_matrix.v1",
            "status": "ok",
            "comparison_metric": "pr_auc",
            "rows": [
                {"ablation_id": "selected_route", "role": "selected_route", "model_family": "hist_gradient_boosting", "test_metric": 0.91},
                {"ablation_id": "lagged_baseline_reference", "role": "lagged_reference", "model_family": "sklearn_lagged_logistic_regression", "test_metric": 0.80},
            ],
        },
    )
    _write_json(
        run_dir / "adapter_activation_report.json",
        {
            "schema_version": "relaytic.adapter_activation_report.v1",
            "status": "ok",
            "rows": [
                {
                    "family_id": "xgboost_classifier",
                    "adapter_module": "xgboost",
                    "available": False,
                    "activation_state": "unavailable",
                }
            ],
        },
    )
    _write_json(
        run_dir / "aml_benchmark_manifest.json",
        {
            "schema_version": "relaytic.aml_benchmark_manifest.v1",
            "status": "supporting_only",
            "dataset_family": "paysim_style_temporal_transaction_fraud",
            "benchmark_track": "temporal_transaction_fraud",
            "covered_track_families": ["paysim_style_temporal_transaction_fraud"],
            "required_track_coverage_met": False,
        },
    )
    _write_json(
        run_dir / "benchmark_release_gate.json",
        {
            "schema_version": "relaytic.benchmark_release_gate.v1",
            "status": "blocked",
            "safe_to_cite_publicly": False,
            "demo_safe": True,
            "blocked_reason_codes": ["aml_cross_track_coverage_missing"],
        },
    )
    _write_json(
        run_dir / "aml_public_claim_guard.json",
        {
            "schema_version": "relaytic.aml_public_claim_guard.v1",
            "status": "supporting_only",
            "supporting_public_claim_allowed": True,
            "paper_primary_claim_allowed": False,
            "broader_flagship_claim_allowed": False,
            "blocked_reason_codes": ["aml_cross_track_coverage_missing"],
        },
    )
    _write_json(
        run_dir / "entity_graph_profile.json",
        {
            "schema_version": "relaytic.entity_graph_profile.v1",
            "status": "active",
            "node_count": 8,
            "edge_count": 9,
            "high_risk_entities": [
                {"entity_id": "MULE_HUB", "risk_score": 0.88, "tx_count": 8, "neighbor_count": 5, "suspicious_rate": 0.85},
                {"entity_id": "RING_1", "risk_score": 0.66, "tx_count": 5, "neighbor_count": 3, "suspicious_rate": 0.50},
            ],
        },
    )
    _write_json(
        run_dir / "counterparty_network_report.json",
        {
            "schema_version": "relaytic.counterparty_network_report.v1",
            "status": "active",
            "component_count": 2,
            "top_edges": [{"source": "MULE_HUB", "destination": "CASHOUT_1", "risk_score": 0.9}],
        },
    )
    _write_json(
        run_dir / "typology_detection_report.json",
        {
            "schema_version": "relaytic.typology_detection_report.v1",
            "status": "active",
            "typology_hit_count": 2,
            "typology_hits": [
                {"typology": "funnel_accounts", "focal_entity": "MULE_HUB", "risk_score": 0.93},
                {"typology": "smurfing", "focal_entity": "MULE_HUB", "risk_score": 0.74},
            ],
        },
    )
    _write_json(
        run_dir / "subgraph_risk_report.json",
        {
            "schema_version": "relaytic.subgraph_risk_report.v1",
            "status": "active",
            "subgraph_count": 1,
            "selected_subgraphs": [{"subgraph_id": "focal_neighborhood_001", "focal_entity": "MULE_HUB"}],
            "candidate_comparison": {
                "status": "ok",
                "selected_candidate": "structural_baseline",
                "shadow_candidate": "message_passing_shadow_proxy",
                "selected_score": 0.84,
                "shadow_score": 0.71,
                "winner": "structural_baseline",
            },
        },
    )
    _write_json(
        run_dir / "entity_case_expansion.json",
        {
            "schema_version": "relaytic.entity_case_expansion.v1",
            "status": "active",
            "focal_entity": "MULE_HUB",
            "expanded_entity_count": 5,
        },
    )
    _write_json(
        run_dir / "alert_queue_policy.json",
        {
            "schema_version": "relaytic.alert_queue_policy.v1",
            "status": "active",
            "review_capacity_cases": 2,
            "review_budget_fraction": 0.5,
        },
    )
    _write_json(
        run_dir / "alert_queue_rankings.json",
        {
            "schema_version": "relaytic.alert_queue_rankings.v1",
            "status": "active",
            "queue_count": 4,
            "review_capacity_cases": 2,
            "ranking": [
                {"rank": 1, "case_id": "case_mule", "entity_id": "MULE_HUB", "suspicious_rate": 0.90, "priority_score": 0.95, "typologies": ["funnel_accounts"]},
                {"rank": 2, "case_id": "case_ring", "entity_id": "RING_1", "suspicious_rate": 0.75, "priority_score": 0.80, "typologies": ["smurfing"]},
                {"rank": 3, "case_id": "case_benign_a", "entity_id": "A", "suspicious_rate": 0.10, "priority_score": 0.30, "typologies": []},
                {"rank": 4, "case_id": "case_benign_b", "entity_id": "B", "suspicious_rate": 0.05, "priority_score": 0.20, "typologies": []},
            ],
        },
    )
    _write_json(
        run_dir / "analyst_review_scorecard.json",
        {
            "schema_version": "relaytic.analyst_review_scorecard.v1",
            "status": "active",
            "total_case_count": 4,
            "review_capacity_cases": 2,
            "analyst_hours_per_case": 0.75,
        },
    )
    _write_json(
        run_dir / "case_packet.json",
        {
            "schema_version": "relaytic.case_packet.v1",
            "status": "active",
            "case_id": "case_mule",
            "focal_entity": "MULE_HUB",
            "priority_score": 0.95,
            "review_action": "review_now",
            "top_typologies": ["funnel_accounts"],
            "linked_entities": ["CASHOUT_1", "CASHOUT_2"],
            "analyst_questions": ["Why did the hub cash out after inbound transfers?"],
        },
    )
    _write_json(
        run_dir / "stream_risk_posture.json",
        {
            "schema_version": "relaytic.stream_risk_posture.v1",
            "status": "active",
            "stream_mode": "batched_temporal_monitoring",
            "timestamp_column": "step",
            "rolling_window_count": 4,
            "recalibration_triggered": True,
        },
    )
    _write_json(
        run_dir / "rolling_alert_quality_report.json",
        {
            "schema_version": "relaytic.rolling_alert_quality_report.v1",
            "status": "active",
            "window_count": 4,
            "latest_alert_rate": 0.25,
            "benchmark_safe": True,
        },
    )
    _write_json(
        run_dir / "drift_recalibration_trigger.json",
        {
            "schema_version": "relaytic.drift_recalibration_trigger.v1",
            "status": "active",
            "trigger_recalibration": True,
            "recommended_action": "recalibrate_threshold",
            "drift_score": 0.18,
        },
    )
    _write_json(
        run_dir / "temporal_structure_report.json",
        {
            "schema_version": "relaytic.temporal_structure_report.v1",
            "status": "active",
            "ordered_temporal_structure": True,
            "timestamp_column": "step",
        },
    )
    _write_json(
        run_dir / "temporal_baseline_ladder.json",
        {
            "schema_version": "relaytic.temporal_baseline_ladder.v1",
            "status": "active",
            "lagged_beats_ordinary": True,
        },
    )
    _write_json(
        run_dir / "calibration_strategy_report.json",
        {
            "schema_version": "relaytic.calibration_strategy_report.v1",
            "status": "ok",
            "selected_method": "isotonic",
        },
    )
    _write_json(
        run_dir / "operating_point_contract.json",
        {
            "schema_version": "relaytic.operating_point_contract.v1",
            "status": "ok",
            "selected_threshold": 0.23,
        },
    )


def test_slice15u_builds_aml_baseline_ablation_and_relevance_artifacts(tmp_path: Path) -> None:
    run_dir = tmp_path / "slice15u_unit"
    _seed_aml_baseline_run(run_dir)
    sync_aml_business_value_artifacts(run_dir)

    bundle = build_aml_baseline_artifacts(run_dir=run_dir)

    baseline = bundle["aml_baseline_matrix"]
    ablation = bundle["aml_ablation_matrix"]
    contribution = bundle["aml_capability_contribution_report"]
    relevance = bundle["aml_benchmark_relevance_scorecard"]

    assert baseline["status"] == "active"
    assert baseline["run_or_fallback_count"] >= 3
    assert {"rules_review_queue", "calibrated_linear", "tree_ensemble", "structural_graph_baseline"}.issubset(
        {row["baseline_id"] for row in baseline["rows"]}
    )

    ablation_ids = {row["ablation_id"] for row in ablation["rows"]}
    assert {"no_graph", "no_temporal", "no_review_budget", "no_calibration", "no_typology_prior"}.issubset(ablation_ids)
    assert contribution["material_contribution_count"] >= 1
    assert contribution["public_metric_changed"] is True

    relevance_by_family = {row["benchmark_family"]: row for row in relevance["rows"]}
    assert relevance_by_family["paysim_style_transaction_fraud"]["support_level"] == "supported"
    assert relevance_by_family["elliptic_style_graph_aml"]["support_level"] in {"proxy", "blocked"}
    assert relevance_by_family["elliptic_style_graph_aml"]["blocked_reason_codes"]
    assert relevance["hard_benchmark_claim_allowed"] is False


def test_cli_slice15u_writes_baseline_surface_and_manifest(
    tmp_path: Path,
    capsys: Any,
) -> None:
    run_dir = tmp_path / "slice15u_cli"
    _seed_aml_baseline_run(run_dir)

    assert main(["aml", "baselines", "--run-dir", str(run_dir), "--format", "json"]) == 0
    payload = json.loads(capsys.readouterr().out)

    assert payload["status"] == "ok"
    assert payload["aml_baselines"]["status"] == "active"
    assert payload["aml_baselines"]["run_or_fallback_count"] >= 3
    assert payload["aml_baselines"]["material_contribution_count"] >= 1
    assert payload["aml_baselines"]["benchmark_support_levels"]["paysim_style_transaction_fraud"] == "supported"

    for artifact_name in SLICE15U_ARTIFACTS:
        assert (run_dir / artifact_name).exists(), artifact_name

    manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
    manifest_paths = {item["path"] for item in manifest["entries"]}
    for artifact_name in SLICE15U_ARTIFACTS:
        assert artifact_name in manifest_paths
