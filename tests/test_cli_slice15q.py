from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import pytest

pytest.importorskip("sklearn.datasets")

from relaytic.ui.cli import main


def _write_cli_stream_drift_dataset(path: Path) -> Path:
    rows: list[dict[str, object]] = []
    for step in range(1, 13):
        rows.append(
            {
                "step": step,
                "type": "PAYMENT",
                "amount": 14.0 + float(step % 3),
                "nameOrig": f"BENIGN_{step:02d}",
                "oldbalanceOrg": 3000.0 - 20.0 * step,
                "newbalanceOrig": 3000.0 - 20.0 * step - (14.0 + float(step % 3)),
                "nameDest": f"MERCHANT_{(step % 4) + 1}",
                "oldbalanceDest": 500.0,
                "newbalanceDest": 500.0 + (14.0 + float(step % 3)),
                "device_id": f"benign-device-{step % 4}",
                "isFraud": 0 if step % 5 else 1,
            }
        )
    for step in range(13, 25):
        amount = 90.0 + float(step % 5)
        rows.append(
            {
                "step": step,
                "type": "TRANSFER",
                "amount": amount,
                "nameOrig": f"RISK_{step:02d}",
                "oldbalanceOrg": 6000.0 - 40.0 * step,
                "newbalanceOrig": 6000.0 - 40.0 * step - amount,
                "nameDest": "MULE_HUB",
                "oldbalanceDest": 100.0,
                "newbalanceDest": 100.0 + amount,
                "device_id": "shared-risk-device",
                "isFraud": 1,
            }
        )
    pd.DataFrame(rows).to_csv(path, index=False)
    return path


def test_cli_slice15q_materializes_stream_risk_and_benchmark_surfaces(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    run_dir = tmp_path / "slice15q_stream_risk"
    data_path = _write_cli_stream_drift_dataset(tmp_path / "slice15q_stream_risk.csv")

    assert main(
        [
            "run",
            "--run-dir",
            str(run_dir),
            "--data-path",
            str(data_path),
            "--timestamp-column",
            "step",
            "--text",
            (
                "Do everything on your own. This is streaming AML payment-fraud monitoring with weak labels and delayed outcomes. "
                "Classify isFraud, detect drift over time, decide whether recalibration is required, and keep the analyst review queue safe."
            ),
            "--format",
            "json",
        ]
    ) == 0
    run_payload = json.loads(capsys.readouterr().out)

    assert run_payload["status"] == "ok"
    stream_risk = run_payload["run_summary"]["stream_risk"]
    assert stream_risk["status"] == "active"
    assert stream_risk["stream_mode"] == "batched_temporal_monitoring"
    assert stream_risk["weak_label_risk_level"] in {"moderate", "high"}
    assert stream_risk["rolling_window_count"] >= 3
    assert stream_risk["trigger_action"] == "run_recalibration_pass"

    for filename in (
        "stream_risk_posture.json",
        "weak_label_posture.json",
        "delayed_outcome_alignment.json",
        "drift_recalibration_trigger.json",
        "rolling_alert_quality_report.json",
    ):
        assert (run_dir / filename).exists(), filename

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
    assert benchmark_payload["benchmark"]["stream_risk_status"] == "active"
    assert benchmark_payload["benchmark"]["weak_label_risk_level"] in {"moderate", "high"}
    assert benchmark_payload["benchmark"]["drift_trigger_action"] == "run_recalibration_pass"
    assert benchmark_payload["bundle"]["stream_risk_posture"]["status"] == "active"
