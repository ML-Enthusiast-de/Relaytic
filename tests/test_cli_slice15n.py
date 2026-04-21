from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import pytest

pytest.importorskip("sklearn.datasets")

from relaytic.ui.cli import main


def test_cli_slice15n_materializes_aml_contract_and_benchmark_scope(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    run_dir = tmp_path / "slice15n_aml_review_queue"
    data_path = tmp_path / "slice15n_aml_review_queue.csv"

    rows = []
    for index in range(360):
        txn_risk = 0.12 + ((index * 7) % 100) / 140.0
        device_overlap = ((index * 5 + 11) % 100) / 100.0
        merchant_pressure = ((index * 3 + 17) % 100) / 120.0
        counterparty_density = ((index * 9 + 23) % 100) / 130.0
        suspicious = 1 if index % 29 == 0 or (txn_risk + merchant_pressure + counterparty_density > 1.65 and index % 5 == 0) else 0
        rows.append(
            {
                "txn_risk": round(txn_risk, 6),
                "device_overlap": round(device_overlap, 6),
                "merchant_pressure": round(merchant_pressure, 6),
                "counterparty_density": round(counterparty_density, 6),
                "review_pressure": round(((index // 9) % 7) / 7.0, 6),
                "suspicious_activity_flag": suspicious,
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
            (
                "Do everything on your own. This is an AML and payment-fraud review-queue problem. "
                "Classify suspicious_activity_flag from the transaction risk features, optimize for analyst review burden, "
                "and benchmark against strong references."
            ),
            "--format",
            "json",
        ]
    ) == 0
    run_payload = json.loads(capsys.readouterr().out)

    assert run_payload["status"] == "ok"
    assert run_payload["run_summary"]["aml"]["status"] == "active"
    assert run_payload["run_summary"]["aml"]["aml_active"] is True
    assert run_payload["run_summary"]["aml"]["review_budget_relevant"] is True
    assert run_payload["run_summary"]["aml"]["decision_objective"] == "maximize_precision_at_review_budget"
    assert run_payload["run_summary"]["aml"]["claim_scope"] == "generic_supporting_only_until_15r"

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
    assert benchmark_payload["benchmark"]["aml_domain_active"] is True
    assert benchmark_payload["benchmark"]["aml_pack_family"] == "aml_flagship_pending"
    assert benchmark_payload["benchmark"]["aml_claim_scope"] == "generic_supporting_only_until_15r"
    assert benchmark_payload["bundle"]["aml_claim_scope"]["public_claim_ready"] is False

    for filename in (
        "aml_domain_contract.json",
        "aml_case_ontology.json",
        "aml_review_budget_contract.json",
        "aml_claim_scope.json",
    ):
        assert (run_dir / filename).exists(), filename
