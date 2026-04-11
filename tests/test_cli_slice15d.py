from __future__ import annotations

import json
from pathlib import Path

import pytest

pytest.importorskip("sklearn.datasets")

from relaytic.ui.cli import main
from tests.public_datasets import write_public_breast_cancer_dataset, write_public_temporal_occupancy_dataset


def test_cli_slice15d_benchmark_run_materializes_paper_artifacts_for_public_binary_run(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    run_dir = tmp_path / "slice15d_public_binary"
    data_path = write_public_breast_cancer_dataset(tmp_path / "slice15d_public_breast_cancer.csv")

    assert main(
        [
            "run",
            "--run-dir",
            str(run_dir),
            "--data-path",
            str(data_path),
            "--text",
            "Classify diagnosis_flag from the measurement columns. Do everything on your own.",
            "--format",
            "json",
        ]
    ) == 0
    capsys.readouterr()

    assert main(["benchmark", "run", "--run-dir", str(run_dir), "--data-path", str(data_path), "--overwrite", "--format", "json"]) == 0
    payload = json.loads(capsys.readouterr().out)

    assert payload["status"] == "ok"
    assert payload["benchmark"]["paper_status"] == "ok"
    assert payload["benchmark"]["competitiveness_claim"]
    assert payload["benchmark"]["deployment_claim"]
    assert payload["bundle"]["paper_benchmark_table"]["rows"]
    assert payload["bundle"]["benchmark_claims_report"]["not_claiming"]
    assert payload["bundle"]["benchmark_vs_deploy_report"]["status"] == "ok"
    ablation_rows = list(payload["bundle"]["benchmark_ablation_matrix"]["rows"])
    assert any(row["role"] == "selected_route" for row in ablation_rows)
    assert any(row["role"] == "baseline_reference" for row in ablation_rows)

    for filename in (
        "paper_benchmark_manifest.json",
        "paper_benchmark_table.json",
        "benchmark_ablation_matrix.json",
        "rerun_variance_report.json",
        "benchmark_claims_report.json",
    ):
        assert (run_dir / filename).exists(), filename

    assert main(["benchmark", "show", "--run-dir", str(run_dir), "--format", "json"]) == 0
    show_payload = json.loads(capsys.readouterr().out)
    assert show_payload["status"] == "ok"
    assert show_payload["benchmark"]["paper_status"] == "ok"
    assert show_payload["benchmark"]["rerun_match_count"] >= 1


def test_cli_slice15d_rerun_variance_uses_matching_benchmarked_runs(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    data_path = write_public_breast_cancer_dataset(tmp_path / "slice15d_variance_breast_cancer.csv")

    for name in ("variance_a", "variance_b", "variance_c"):
        run_dir = tmp_path / name
        assert main(
            [
                "run",
                "--run-dir",
                str(run_dir),
                "--data-path",
                str(data_path),
                "--text",
                "Classify diagnosis_flag from the measurement columns. Do everything on your own.",
                "--format",
                "json",
            ]
        ) == 0
        capsys.readouterr()
        assert main(
            ["benchmark", "run", "--run-dir", str(run_dir), "--data-path", str(data_path), "--overwrite", "--format", "json"]
        ) == 0
        payload = json.loads(capsys.readouterr().out)

    variance = payload["bundle"]["rerun_variance_report"]
    assert variance["matching_run_count"] >= 3
    assert variance["stability_band"] in {"stable", "moderate_variance"}
    assert len(variance["metric_values"]) >= 3


def test_cli_slice15d_temporal_benchmark_manifest_records_temporal_posture(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    run_dir = tmp_path / "slice15d_temporal"
    data_path = write_public_temporal_occupancy_dataset(tmp_path / "slice15d_occupancy.csv", max_rows=1200)

    assert main(
        [
            "run",
            "--run-dir",
            str(run_dir),
            "--data-path",
            str(data_path),
            "--text",
            "Classify occupancy_flag from the room sensor columns over time. Do everything on your own.",
            "--format",
            "json",
        ]
    ) == 0
    capsys.readouterr()

    assert main(["benchmark", "run", "--run-dir", str(run_dir), "--data-path", str(data_path), "--overwrite", "--format", "json"]) == 0
    payload = json.loads(capsys.readouterr().out)

    manifest = payload["bundle"]["paper_benchmark_manifest"]
    claims = payload["bundle"]["benchmark_claims_report"]
    assert manifest["data_mode"] == "time_series"
    assert manifest["horizon_type"]
    assert manifest["sequence_candidate_status"] in {"shadow_ready", "not_live"}
    assert manifest["sequence_candidate_reason"]
    assert claims["temporal_posture"]["horizon_type"] == manifest["horizon_type"]
    assert claims["temporal_posture"]["sequence_candidate_status"] == manifest["sequence_candidate_status"]
