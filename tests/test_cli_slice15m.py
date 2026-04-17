from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import pytest

pytest.importorskip("sklearn.datasets")

from relaytic.ui.cli import main
from tests.public_datasets import (
    write_public_temporal_occupancy_dataset,
)


def test_cli_slice15m_benchmark_records_partition_and_generalization_guard(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    run_dir = tmp_path / "slice15m_review_queue"
    data_path = tmp_path / "slice15m_rare_event.csv"
    rows = []
    for index in range(480):
        risk = 0.15 + ((index * 7) % 100) / 140.0
        utilization = 0.10 + ((index * 5 + 11) % 100) / 155.0
        gap = 0.12 + ((index * 9 + 3) % 100) / 180.0
        tenure = 1.0 - (((index * 4 + 17) % 100) / 140.0)
        review_pressure = ((index // 7) % 5) / 5.0
        rare_spike = 1 if index % 37 == 0 or (risk + gap > 1.1 and index % 9 == 0) else 0
        rows.append(
            {
                "risk_score": round(risk, 6),
                "utilization_norm": round(utilization, 6),
                "payment_gap_ratio": round(gap, 6),
                "tenure_norm": round(tenure, 6),
                "review_pressure": round(review_pressure, 6),
                "default_flag": rare_spike,
            }
        )
    pd.DataFrame(rows).to_csv(data_path, index=False)

    assert main(
        [
            "run",
            "--run-dir",
            str(run_dir),
            "--data-path",
            str(data_path),
            "--text",
            "Predict default_flag from the account risk features, benchmark against strong references, and explain whether this claim should stay dev-only or holdout-primary.",
            "--format",
            "json",
        ]
    ) == 0
    capsys.readouterr()

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
    payload = json.loads(capsys.readouterr().out)

    assert payload["status"] == "ok"
    assert payload["benchmark"]["pack_partition"] in {"dev", "holdout"}
    assert payload["benchmark"]["benchmark_generalization_status"] == "ok"
    assert payload["bundle"]["benchmark_generalization_audit"]["identity_branching_detected"] is False
    assert payload["bundle"]["holdout_claim_policy"]["requires_holdout_for_paper_primary"] is True
    assert payload["bundle"]["rare_event_search_profile"]["status"] == "active"
    assert payload["bundle"]["adapter_activation_report"]["status"] == "ok"
    assert payload["benchmark"]["paper_primary_claim_allowed"] == (
        bool(payload["benchmark"]["safe_to_cite_publicly"]) and payload["benchmark"]["pack_partition"] == "holdout"
    )

    for filename in (
        "family_specialization_matrix.json",
        "multiclass_search_profile.json",
        "rare_event_search_profile.json",
        "adapter_activation_report.json",
        "benchmark_pack_partition.json",
        "holdout_claim_policy.json",
        "benchmark_generalization_audit.json",
    ):
        assert (run_dir / filename).exists(), filename


def test_cli_slice15m_temporal_benchmark_recovery_is_honest(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    run_dir = tmp_path / "slice15m_temporal_recovery"
    data_path = write_public_temporal_occupancy_dataset(tmp_path / "slice15m_temporal_occupancy.csv", max_rows=720)

    assert main(
        [
            "run",
            "--run-dir",
            str(run_dir),
            "--data-path",
            str(data_path),
            "--text",
            "Classify occupancy_flag from the room sensor columns over time and benchmark it honestly for paper use.",
            "--format",
            "json",
        ]
    ) == 0
    capsys.readouterr()

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
    payload = json.loads(capsys.readouterr().out)

    recovery = payload["bundle"]["temporal_benchmark_recovery_report"]
    assert payload["status"] == "ok"
    assert recovery["applies_to_temporal_classification"] is True
    assert recovery["recovery_state"] in {"recovered", "blocked"}
    if recovery["recovery_state"] == "recovered":
        assert recovery["comparison_contract_ready"] is True
        assert recovery["fold_health_status"] == "ok"
    else:
        assert set(recovery["blocked_reason_codes"]).issubset(
            {
                "temporal_fold_health_blocked",
                "benchmark_metric_missing_in_execution",
                "benchmark_metric_missing_in_reference_rows",
            }
        )
