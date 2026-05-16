from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

pytest.importorskip("sklearn.datasets")

from relaytic.ui.cli import main


AML_DEMO_ARTIFACTS = (
    "aml_demo_bundle_manifest.json",
    "aml_demo_business_metric_table.json",
    "aml_demo_flow_report.md",
    "aml_demo_artifact_index.json",
    "aml_business_value_report.json",
    "analyst_hour_savings_report.json",
    "review_capacity_metric_report.json",
    "operational_metric_guard.json",
    "aml_baseline_matrix.json",
    "aml_ablation_matrix.json",
    "aml_baseline_adapter_report.json",
    "aml_capability_contribution_report.json",
    "aml_benchmark_relevance_scorecard.json",
)


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def test_cli_slice15s_creates_public_safe_aml_review_queue_demo_bundle(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    run_dir = tmp_path / "slice15s_aml_demo"

    assert main(
        [
            "demo",
            "aml-review-queue",
            "--run-dir",
            str(run_dir),
            "--overwrite",
            "--format",
            "json",
        ]
    ) == 0
    payload = json.loads(capsys.readouterr().out)

    assert payload["status"] == "ok"
    assert payload["demo_id"] == "relaytic-aml-review-queue"
    assert payload["fixture_written"] is True
    assert payload["artifact_index"]["status"] == "ready"
    assert payload["artifact_index"]["missing_required_artifact_count"] == 0

    for artifact_name in AML_DEMO_ARTIFACTS:
        assert (run_dir / artifact_name).exists(), artifact_name

    manifest = _read_json(run_dir / "aml_demo_bundle_manifest.json")
    index = _read_json(run_dir / "aml_demo_artifact_index.json")
    business_metrics = _read_json(run_dir / "aml_demo_business_metric_table.json")
    public_claim_guard = _read_json(run_dir / "aml_public_claim_guard.json")
    business_value = _read_json(run_dir / "aml_business_value_report.json")
    operational_guard = _read_json(run_dir / "operational_metric_guard.json")
    baseline_matrix = _read_json(run_dir / "aml_baseline_matrix.json")
    contribution_report = _read_json(run_dir / "aml_capability_contribution_report.json")
    flow_report = (run_dir / "aml_demo_flow_report.md").read_text(encoding="utf-8")

    required_by_id = {str(item["artifact_id"]): item for item in index["required_artifacts"]}
    for artifact_id in (
        "case_packet",
        "benchmark_release_gate",
        "aml_public_claim_guard",
        "aml_failure_report",
        "aml_baseline_matrix",
        "aml_ablation_matrix",
        "aml_benchmark_relevance_scorecard",
    ):
        assert required_by_id[artifact_id]["exists"] is True
    for item in index["bundle_artifacts"]:
        assert item["exists"] is True

    assert business_metrics["model_metrics"]
    assert business_metrics["operational_review_metrics"]
    assert business_metrics["hard_business_value_claim_allowed"] is operational_guard["hard_business_value_claim_allowed"]
    assert business_metrics["claim_boundary"].startswith("Model metrics and operational review-budget metrics")
    assert "## Model Metrics" in flow_report
    assert "## Operational Review Metrics" in flow_report
    assert "## Business Value Guard" in flow_report
    assert "## Baselines And Ablations" in flow_report
    assert "## Safe Claims" in flow_report

    assert manifest["artifact_paths"]["case_packet"] == "case_packet.json"
    assert manifest["artifact_paths"]["benchmark_guard"] == "benchmark_release_gate.json"
    assert manifest["artifact_paths"]["public_claim_guard"] == "aml_public_claim_guard.json"
    assert manifest["artifact_paths"]["failure_report"] == "aml_failure_report.json"
    assert manifest["artifact_paths"]["aml_business_value_report"] == "aml_business_value_report.json"
    assert manifest["claim_guard"]["broader_flagship_claim_allowed"] is False
    assert manifest["business_value"]["status"] == business_value["status"]
    assert manifest["business_value"]["hard_business_value_claim_allowed"] is operational_guard["hard_business_value_claim_allowed"]
    assert manifest["baseline_and_ablation"]["status"] == baseline_matrix["status"]
    assert manifest["baseline_and_ablation"]["material_contribution_count"] == contribution_report["material_contribution_count"]
    assert manifest["artifact_paths"]["aml_baseline_matrix"] == "aml_baseline_matrix.json"
    assert manifest["artifact_paths"]["aml_benchmark_relevance_scorecard"] == "aml_benchmark_relevance_scorecard.json"
    assert "aml_cross_track_coverage_missing" in public_claim_guard["blocked_reason_codes"]

    assert main(["mission-control", "show", "--run-dir", str(run_dir), "--format", "json"]) == 0
    mission_payload = json.loads(capsys.readouterr().out)
    mission = mission_payload["mission_control"]
    board = mission_payload["bundle"]["aml_investigation_board"]
    cards = mission_payload["bundle"]["mission_control_state"]["cards"]

    assert mission["aml_demo_bundle_present"] is True
    assert mission["aml_top_case_id"] == board["top_case_packet"]["case_id"]
    assert board["demo_bundle_present"] is True
    assert board["alert_queue"]["queue_count"] > 0
    assert board["top_case_packet"]["case_id"]
    assert board["business_value"]["status"] == business_value["status"]
    assert board["business_value"]["operational_guard_status"] == operational_guard["operational_utility_state"]
    assert board["drift_posture"]["recommended_action"]
    assert board["claim_guard"]["broader_flagship_claim_allowed"] is False
    assert any(item["card_id"] == "aml_investigation_board" for item in cards)
