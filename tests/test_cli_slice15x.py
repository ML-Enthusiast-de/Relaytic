from __future__ import annotations

import json
from pathlib import Path

import pytest

from relaytic.aml import build_aml_environment_artifacts
from relaytic.core.json_utils import write_json
from relaytic.ui.cli import main


def _write_environment_run(run_dir: Path, *, override_decision: str = "reject") -> None:
    run_dir.mkdir(parents=True, exist_ok=True)
    payloads = {
        "manifest.json": {
            "schema_version": "test.manifest.v1",
            "run_id": run_dir.name,
            "entries": [],
        },
        "run_summary.json": {
            "schema_version": "test.run_summary.v1",
            "run_id": run_dir.name,
            "status": "ok",
        },
        "data_copy_manifest.json": {
            "schema_version": "test.data_copy_manifest.v1",
            "copy_enforced": True,
            "source_path_persisted": False,
        },
        "task_profile_contract.json": {
            "schema_version": "test.task_profile_contract.v1",
            "status": "active",
            "target_signal": "isFraud",
            "task_type": "binary_classification",
            "problem_posture": "rare_event_supervised",
        },
        "aml_domain_contract.json": {
            "schema_version": "test.aml_domain_contract.v1",
            "status": "active",
            "aml_active": True,
            "domain_focus": "transaction_monitoring",
            "business_goal": "prioritize analyst review",
        },
        "aml_claim_scope.json": {
            "schema_version": "test.aml_claim_scope.v1",
            "claim_scope": "supporting_public_claims",
        },
        "benchmark_truth_precheck.json": {
            "schema_version": "test.benchmark_truth_precheck.v1",
            "status": "pass",
            "safe_to_rank": True,
        },
        "benchmark_parity_report.json": {
            "schema_version": "test.benchmark_parity_report.v1",
            "status": "pass",
            "parity_status": "competitive",
            "relaytic_metric_value": 0.82,
        },
        "reference_approach_matrix.json": {
            "schema_version": "test.reference_approach_matrix.v1",
            "status": "active",
            "rows": [{"reference_id": "public_strong_baseline", "metric_value": 0.78}],
        },
        "benchmark_release_gate.json": {
            "schema_version": "test.benchmark_release_gate.v1",
            "status": "pass",
            "safe_to_cite_publicly": True,
        },
        "paper_claim_guard_report.json": {
            "schema_version": "test.paper_claim_guard_report.v1",
            "status": "pass",
            "safe_to_cite_publicly": True,
            "claim_blockers": [],
        },
        "aml_benchmark_manifest.json": {
            "schema_version": "test.aml_benchmark_manifest.v1",
            "status": "active",
            "dataset_family": "paysim_like",
            "benchmark_track": "transaction_monitoring",
        },
        "aml_public_claim_guard.json": {
            "schema_version": "test.aml_public_claim_guard.v1",
            "status": "pass",
            "hard_public_claim_allowed": True,
            "supporting_public_claim_allowed": True,
            "claim_blockers": [],
        },
        "aml_benchmark_relevance_scorecard.json": {
            "schema_version": "test.aml_benchmark_relevance_scorecard.v1",
            "status": "pass",
            "supported_family_count": 1,
            "rows": [{"benchmark_family": "paysim_like", "support_level": "supported"}],
        },
        "incumbent_parity_report.json": {
            "schema_version": "test.incumbent_parity_report.v1",
            "status": "pass",
            "incumbent_present": True,
            "parity_status": "competitive",
        },
        "aml_business_value_report.json": {
            "schema_version": "test.aml_business_value_report.v1",
            "status": "active",
            "incumbent_tradeoff": {"incumbent_present": True, "tradeoff_summary": "competitive at review capacity"},
        },
        "alert_queue_policy.json": {
            "schema_version": "test.alert_queue_policy.v1",
            "status": "active",
            "review_capacity_cases": 3,
        },
        "alert_queue_rankings.json": {
            "schema_version": "test.alert_queue_rankings.v1",
            "status": "active",
            "queue_count": 4,
            "rows": [
                {"case_id": "case_001", "risk_score": 0.94},
                {"case_id": "case_002", "risk_score": 0.86},
            ],
        },
        "analyst_review_scorecard.json": {
            "schema_version": "test.analyst_review_scorecard.v1",
            "status": "active",
            "review_capacity_cases": 3,
        },
        "case_packet.json": {
            "schema_version": "test.case_packet.v1",
            "status": "active",
            "case_id": "case_001",
            "summary": "High-risk transaction bundle for analyst review.",
        },
        "review_capacity_metric_report.json": {
            "schema_version": "test.review_capacity_metric_report.v1",
            "status": "active",
            "review_capacity_cases": 3,
            "case_packet_completeness": 0.9,
        },
        "drift_recalibration_trigger.json": {
            "schema_version": "test.drift_recalibration_trigger.v1",
            "status": "active",
            "trigger_state": "watch",
            "recommended_action": "run_recalibration_pass",
        },
        "aml_threshold_drift_report.json": {
            "schema_version": "test.aml_threshold_drift_report.v1",
            "status": "active",
            "threshold_drift_state": "watch",
            "recommended_action": "run_recalibration_pass",
        },
        "aml_time_window_scorecard.json": {
            "schema_version": "test.aml_time_window_scorecard.v1",
            "status": "active",
            "window_count": 3,
        },
        "aml_temporal_benchmark_claim_report.json": {
            "schema_version": "test.aml_temporal_benchmark_claim_report.v1",
            "status": "supporting_only",
            "supporting_temporal_evidence_allowed": True,
            "temporal_public_claim_allowed": True,
            "claim_blockers": [],
            "recommended_next_action": "run_recalibration_pass",
        },
        "control_challenge_report.json": {
            "schema_version": "test.control_challenge_report.v1",
            "status": "active",
            "unsafe_steering_detected": True,
            "risk_flags": ["policy_bypass"],
            "trace_refs": ["trace_model.json"],
        },
        "override_decision.json": {
            "schema_version": "test.override_decision.v1",
            "status": override_decision,
            "decision": override_decision,
            "allowed": override_decision == "accept",
            "trace_refs": ["trace_model.json"],
        },
        "trace_model.json": {
            "schema_version": "test.trace_model.v1",
            "status": "active",
            "span_count": 2,
        },
        "security_eval_report.json": {
            "schema_version": "test.security_eval_report.v1",
            "status": "pass",
        },
        "red_team_report.json": {
            "schema_version": "test.red_team_report.v1",
            "status": "pass",
        },
    }
    for filename, payload in payloads.items():
        write_json(run_dir / filename, payload, indent=2, sort_keys=True)


def test_cli_slice15x_materializes_aml_environment_scorecards(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    run_dir = tmp_path / "slice15x_environment"
    _write_environment_run(run_dir)

    assert main(
        [
            "aml",
            "environment",
            "--run-dir",
            str(run_dir),
            "--overwrite",
            "--format",
            "json",
        ]
    ) == 0
    payload = json.loads(capsys.readouterr().out)

    environment = payload["aml_environment"]
    run_summary_environment = payload["run_summary"]["aml_environment"]
    assert environment["model_score_and_environment_score_separate"] is True
    assert environment["model_quality_score"] == run_summary_environment["model_quality_score"]
    assert environment["environment_score"] == run_summary_environment["environment_score"]
    assert environment["unsafe_steering_status"] == "pass"
    assert environment["unsafe_steering_trace_backed"] is True
    assert environment["benchmark_environment_status"] == "pass"
    assert environment["named_benchmark_family"] == "paysim_like"

    matrix = payload["bundle"]["aml_workflow_task_matrix"]
    task_statuses = {row["task_id"]: row["status"] for row in matrix["rows"]}
    assert task_statuses["model_quality"] == "pass"
    assert task_statuses["unsafe_steering_rejection"] == "pass"
    assert matrix["model_quality_task_count"] == 1
    assert matrix["workflow_safety_task_count"] >= 2

    for filename in (
        "aml_eval_environment_manifest.json",
        "aml_environment_scorecard.json",
        "aml_workflow_task_matrix.json",
        "aml_environment_failure_report.json",
        "aml_benchmark_environment_scorecard.json",
    ):
        assert (run_dir / filename).exists(), filename


def test_slice15x_failure_report_blocks_model_success_as_environment_success(tmp_path: Path) -> None:
    run_dir = tmp_path / "slice15x_unsafe_accept"
    _write_environment_run(run_dir, override_decision="accept")

    artifacts = build_aml_environment_artifacts(run_dir=run_dir)
    scorecard = artifacts["aml_environment_scorecard"]
    failure = artifacts["aml_environment_failure_report"]
    matrix = artifacts["aml_workflow_task_matrix"]
    task_statuses = {row["task_id"]: row["status"] for row in matrix["rows"]}

    assert scorecard["model_quality_status"] == "pass"
    assert task_statuses["unsafe_steering_rejection"] == "fail"
    assert failure["model_success_environment_success_disagreement"] is True
    assert failure["model_success_does_not_imply_environment_success"] is True
    assert failure["primary_failure_kind"] == "workflow_safety_failed"
