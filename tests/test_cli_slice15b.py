from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from relaytic.ui.cli import main


def test_cli_slice15b_materializes_architecture_routing_for_multiclass_run(
    tmp_path: Path, capsys
) -> None:
    run_dir = tmp_path / "slice15b_multiclass"
    data_path = tmp_path / "slice15b_multiclass.csv"
    rows: list[dict[str, object]] = []
    for idx in range(240):
        if idx < 80:
            rows.append(
                {
                    "length": 1.0 + (idx / 200.0),
                    "width": 0.20 + ((idx % 8) / 120.0),
                    "color_score": 0.15 + ((idx % 6) / 40.0),
                    "bean_class": "CALI",
                }
            )
        elif idx < 160:
            local = idx - 80
            rows.append(
                {
                    "length": 2.0 + (local / 200.0),
                    "width": 0.85 + ((local % 8) / 90.0),
                    "color_score": 0.50 + ((local % 6) / 30.0),
                    "bean_class": "SIRA",
                }
            )
        else:
            local = idx - 160
            rows.append(
                {
                    "length": 3.0 + (local / 200.0),
                    "width": 1.55 + ((local % 8) / 70.0),
                    "color_score": 0.95 + ((local % 6) / 20.0),
                    "bean_class": "DERMASON",
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
            "Classify bean_class from the morphology columns, explain the architecture choice, and do everything on your own.",
            "--format",
            "json",
        ]
    ) == 0
    payload = json.loads(capsys.readouterr().out)

    assert payload["status"] == "ok"
    architecture = dict(payload["run_summary"]["architecture"])
    assert payload["run_summary"]["decision"]["selected_model_family"] in {
        "hist_gradient_boosting_classifier",
        "extra_trees_classifier",
        "catboost_classifier",
        "xgboost_classifier",
        "lightgbm_classifier",
        "tabpfn_classifier",
    }
    assert any(
        family in {
            "hist_gradient_boosting_classifier",
            "extra_trees_classifier",
            "catboost_classifier",
            "xgboost_classifier",
            "lightgbm_classifier",
            "tabpfn_classifier",
        }
        for family in architecture["candidate_order"][:4]
    )
    assert architecture["candidate_count"] >= 5
    assert architecture["sequence_live_allowed"] is False
    for artifact_name in (
        "architecture_registry.json",
        "architecture_router_report.json",
        "candidate_family_matrix.json",
        "architecture_fit_report.json",
        "family_capability_matrix.json",
        "architecture_ablation_report.json",
    ):
        assert (run_dir / artifact_name).exists(), artifact_name
