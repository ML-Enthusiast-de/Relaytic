from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import pytest

pytest.importorskip("sklearn.datasets")

from relaytic.ui.cli import main


def test_cli_slice15o_materializes_graph_typology_and_case_expansion(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    run_dir = tmp_path / "slice15o_aml_graph"
    data_path = tmp_path / "slice15o_aml_graph.csv"
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
                "Classify suspicious_activity_flag, expand suspicious entities and counterparties, detect typology hits, "
                "and explain why the case is structurally suspicious for analyst review."
            ),
            "--format",
            "json",
        ]
    ) == 0
    payload = json.loads(capsys.readouterr().out)

    assert payload["status"] == "ok"
    aml_graph = payload["run_summary"]["aml_graph"]
    assert aml_graph["status"] == "active"
    assert aml_graph["node_count"] >= 8
    assert aml_graph["typology_hit_count"] >= 1
    assert aml_graph["focal_entity"] == "HUB1"
    assert aml_graph["shadow_winner"] == "structural_baseline"

    for filename in (
        "entity_graph_profile.json",
        "counterparty_network_report.json",
        "typology_detection_report.json",
        "subgraph_risk_report.json",
        "entity_case_expansion.json",
    ):
        assert (run_dir / filename).exists(), filename
