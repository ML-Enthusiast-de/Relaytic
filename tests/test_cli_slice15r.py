from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

pytest.importorskip("sklearn.datasets")

from relaytic.ui.cli import main
from tests.aml_workload_fixtures import write_elliptic_like_dataset, write_paysim_like_dataset


AML_PROOF_ARTIFACTS = (
    "aml_benchmark_manifest.json",
    "aml_holdout_claim_report.json",
    "aml_demo_scorecard.json",
    "aml_public_claim_guard.json",
    "aml_failure_report.json",
)


def _run_and_benchmark(
    *,
    run_dir: Path,
    data_path: Path,
    timestamp_column: str,
    text: str,
    capsys: pytest.CaptureFixture[str],
) -> dict[str, Any]:
    assert main(
        [
            "run",
            "--run-dir",
            str(run_dir),
            "--data-path",
            str(data_path),
            "--timestamp-column",
            timestamp_column,
            "--text",
            text,
            "--format",
            "json",
        ]
    ) == 0
    run_payload = json.loads(capsys.readouterr().out)
    assert run_payload["status"] == "ok"

    assert main(
        [
            "benchmark",
            "run",
            "--run-dir",
            str(run_dir),
            "--data-path",
            str(data_path),
            "--overwrite",
            "--format",
            "json",
        ]
    ) == 0
    benchmark_payload = json.loads(capsys.readouterr().out)
    assert benchmark_payload["status"] == "ok"
    return benchmark_payload


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def test_cli_slice15r_aligns_aml_proof_pack_across_workload_surfaces(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    paysim_run = tmp_path / "slice15r_paysim"
    paysim_data = write_paysim_like_dataset(tmp_path / "slice15r_paysim.csv")

    paysim_payload = _run_and_benchmark(
        run_dir=paysim_run,
        data_path=paysim_data,
        timestamp_column="step",
        text=(
            "Do everything on your own. This is a PaySim-style AML payment-fraud transaction monitoring workload. "
            "Classify isFraud, optimize analyst review queue value, detect drift, and explain public AML proof posture."
        ),
        capsys=capsys,
    )
    paysim_benchmark = paysim_payload["benchmark"]
    paysim_summary = _read_json(paysim_run / "run_summary.json")

    assert paysim_summary["decision"]["target_column"] == "isFraud"
    assert paysim_benchmark["aml_dataset_family"] == "paysim_style_temporal_transaction_fraud"
    assert paysim_benchmark["aml_required_track_coverage_met"] is False
    assert paysim_benchmark["aml_primary_failure_kind"] == "cross_track_coverage_gap"
    assert "elliptic_style_temporal_graph_aml" in paysim_benchmark["aml_recommended_next_step"]
    assert "aml_cross_track_coverage_missing" in _read_json(paysim_run / "aml_public_claim_guard.json")[
        "blocked_reason_codes"
    ]
    assert paysim_summary["aml_proof"]["dataset_family"] == paysim_benchmark["aml_dataset_family"]
    for artifact_name in AML_PROOF_ARTIFACTS:
        assert (paysim_run / artifact_name).exists(), artifact_name

    elliptic_run = tmp_path / "slice15r_elliptic"
    elliptic_data = write_elliptic_like_dataset(tmp_path / "slice15r_elliptic.csv")
    elliptic_payload = _run_and_benchmark(
        run_dir=elliptic_run,
        data_path=elliptic_data,
        timestamp_column="time_step",
        text=(
            "Do everything on your own. This is a flattened Elliptic-style AML temporal graph workload. "
            "Classify y, use source and destination entity graph evidence, optimize analyst review queue value, "
            "and explain public AML proof posture."
        ),
        capsys=capsys,
    )
    elliptic_benchmark = elliptic_payload["benchmark"]
    elliptic_summary = _read_json(elliptic_run / "run_summary.json")
    elliptic_manifest = _read_json(elliptic_run / "aml_benchmark_manifest.json")
    elliptic_guard = _read_json(elliptic_run / "aml_public_claim_guard.json")

    assert elliptic_summary["decision"]["target_column"] == "y"
    assert elliptic_benchmark["aml_dataset_family"] == "elliptic_style_temporal_graph_aml"
    assert elliptic_manifest["covered_track_families"] == [
        "elliptic_style_temporal_graph_aml",
        "paysim_style_temporal_transaction_fraud",
    ]
    assert elliptic_benchmark["aml_required_track_coverage_met"] is True
    assert elliptic_summary["aml_proof"]["required_track_coverage_met"] is True
    assert "aml_cross_track_coverage_missing" not in elliptic_guard["blocked_reason_codes"]
    assert elliptic_benchmark["aml_broader_flagship_claim_allowed"] is False

    assert main(["benchmark", "show", "--run-dir", str(elliptic_run), "--format", "json"]) == 0
    show_payload = json.loads(capsys.readouterr().out)
    show_benchmark = show_payload["benchmark"]
    assert show_benchmark["aml_dataset_family"] == elliptic_benchmark["aml_dataset_family"]
    assert show_benchmark["aml_required_track_coverage_met"] == elliptic_benchmark["aml_required_track_coverage_met"]
    assert show_benchmark["aml_primary_failure_kind"] == elliptic_benchmark["aml_primary_failure_kind"]

    assert main(
        [
            "assist",
            "turn",
            "--run-dir",
            str(elliptic_run),
            "--message",
            "what AML proof claims are allowed?",
            "--format",
            "json",
        ]
    ) == 0
    assist_payload = json.loads(capsys.readouterr().out)
    assert assist_payload["turn"]["audit_question_type"] == "aml_proof_pack"
    assert set(AML_PROOF_ARTIFACTS).issubset(set(assist_payload["audit"]["evidence_refs"]))

    assert main(["mission-control", "show", "--run-dir", str(elliptic_run), "--format", "json"]) == 0
    mission_payload = json.loads(capsys.readouterr().out)
    mission_bundle = mission_payload["bundle"]
    assert mission_bundle["flagship_demo_scorecard"]["current_run_story"] == elliptic_summary["aml_proof"][
        "current_run_story"
    ]
    assert mission_bundle["demo_pack_manifest"]["demo_count"] == len(elliptic_summary["aml_proof"]["scored_demos"])

    for artifact_name in AML_PROOF_ARTIFACTS:
        assert (elliptic_run / artifact_name).exists(), artifact_name
