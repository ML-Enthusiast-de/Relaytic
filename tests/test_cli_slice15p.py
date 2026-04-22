from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import pytest

pytest.importorskip("sklearn.datasets")

from relaytic.ui.cli import main


def test_cli_slice15p_materializes_casework_queue_and_packet(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    run_dir = tmp_path / "slice15p_casework"
    data_path = tmp_path / "slice15p_casework.csv"
    rows = [
        {"source_account": "A1", "destination_account": "HUB1", "txn_amount": 12.0, "device_id": "dev-1", "suspicious_activity_flag": 1},
        {"source_account": "A2", "destination_account": "HUB1", "txn_amount": 14.0, "device_id": "dev-2", "suspicious_activity_flag": 1},
        {"source_account": "A3", "destination_account": "HUB1", "txn_amount": 11.0, "device_id": "dev-3", "suspicious_activity_flag": 1},
        {"source_account": "HUB1", "destination_account": "L1", "txn_amount": 55.0, "device_id": "dev-1", "suspicious_activity_flag": 1},
        {"source_account": "HUB1", "destination_account": "L2", "txn_amount": 48.0, "device_id": "dev-1", "suspicious_activity_flag": 1},
        {"source_account": "C1", "destination_account": "B1", "txn_amount": 31.0, "device_id": "dev-9", "suspicious_activity_flag": 0},
        {"source_account": "B1", "destination_account": "B2", "txn_amount": 28.0, "device_id": "dev-9", "suspicious_activity_flag": 1},
        {"source_account": "B2", "destination_account": "B3", "txn_amount": 26.0, "device_id": "dev-9", "suspicious_activity_flag": 1},
        {"source_account": "B3", "destination_account": "B4", "txn_amount": 24.0, "device_id": "dev-9", "suspicious_activity_flag": 1},
        {"source_account": "X1", "destination_account": "M1", "txn_amount": 80.0, "device_id": "shared-merchant", "suspicious_activity_flag": 0},
        {"source_account": "X2", "destination_account": "M1", "txn_amount": 82.0, "device_id": "shared-merchant", "suspicious_activity_flag": 0},
        {"source_account": "X3", "destination_account": "M1", "txn_amount": 81.0, "device_id": "shared-merchant", "suspicious_activity_flag": 1},
    ]
    pd.DataFrame(rows).to_csv(data_path, index=False)

    assert main(
        [
            "run",
            "--run-dir",
            str(run_dir),
            "--data-path",
            str(data_path),
            "--text",
            (
                "Do everything on your own. This is an AML payment-fraud case. "
                "Classify suspicious_activity_flag, build the analyst review queue, rank which entity-case should be reviewed first, "
                "and generate a case packet explaining the evidence."
            ),
            "--format",
            "json",
        ]
    ) == 0
    payload = json.loads(capsys.readouterr().out)

    assert payload["status"] == "ok"
    casework = payload["run_summary"]["casework"]
    assert casework["status"] == "active"
    assert casework["queue_count"] >= 2
    assert casework["review_capacity_cases"] >= 1
    assert casework["top_case_id"] == "case_hub1"
    assert casework["top_case_entity"] == "HUB1"
    assert casework["top_case_action"] == "review_now"
    assert casework["estimated_review_hours"] > 0

    for filename in (
        "alert_queue_policy.json",
        "alert_queue_rankings.json",
        "analyst_review_scorecard.json",
        "case_packet.json",
        "review_capacity_sensitivity.json",
    ):
        assert (run_dir / filename).exists(), filename
