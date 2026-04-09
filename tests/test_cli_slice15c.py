from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from relaytic.ui.cli import main


def test_cli_slice15c_materializes_hpo_contracts_and_summary(tmp_path: Path, capsys) -> None:
    run_dir = tmp_path / "slice15c_binary"
    data_path = tmp_path / "slice15c_binary.csv"
    rows: list[dict[str, float | int]] = []
    for idx in range(240):
        feature_a = idx / 239.0
        feature_b = 1 if idx % 6 in {0, 1} else 0
        feature_c = round((idx % 11) / 10.0, 5)
        class_label = 1 if (feature_a > 0.60 or feature_b == 1 or feature_c > 0.85) else 0
        rows.append(
            {
                "feature_a": round(feature_a, 5),
                "feature_b": feature_b,
                "feature_c": feature_c,
                "class_label": class_label,
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
            "Classify class_label from the feature columns, use the strongest bounded search you have, and explain the model choice.",
            "--format",
            "json",
        ]
    ) == 0
    payload = json.loads(capsys.readouterr().out)

    assert payload["status"] == "ok"
    run_summary = dict(payload["run_summary"])
    hpo = dict(run_summary["hpo"])
    assert hpo["status"] == "ok"
    assert hpo["executed_trial_count"] > 0
    assert hpo["tuned_family_count"] >= 1
    assert "trial_budget_exhausted" in hpo["stop_reasons"] or "convergence_plateau" in hpo["stop_reasons"]
    assert run_summary["artifacts"]["hpo_budget_contract_path"]
    assert run_summary["artifacts"]["trial_ledger_path"]
    assert run_summary["artifacts"]["threshold_tuning_report_path"]
    for artifact_name in (
        "hpo_budget_contract.json",
        "architecture_search_space.json",
        "trial_ledger.jsonl",
        "early_stopping_report.json",
        "search_loop_scorecard.json",
        "warm_start_transfer_report.json",
        "threshold_tuning_report.json",
    ):
        assert (run_dir / artifact_name).exists(), artifact_name
