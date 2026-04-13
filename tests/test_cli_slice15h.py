from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from relaytic.ui.cli import main


def test_cli_slice15h_materializes_family_stack_for_mixed_type_run(
    tmp_path: Path,
    capsys,
) -> None:
    run_dir = tmp_path / "slice15h_mixed_type"
    data_path = tmp_path / "slice15h_mixed_type.csv"
    rows: list[dict[str, object]] = []
    for idx in range(180):
        segment = "enterprise" if idx % 3 == 0 else "retail"
        region = "north" if idx % 4 in {0, 1} else "south"
        score = round(idx / 179.0, 5)
        tenure = round((idx % 24) / 24.0, 5)
        accepted = 1 if segment == "enterprise" or score > 0.68 or (region == "north" and tenure > 0.55) else 0
        rows.append(
            {
                "score": score,
                "tenure": tenure,
                "segment": segment,
                "region": region,
                "accepted": accepted,
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
            "Classify accepted from the mixed-type customer columns and explain which model families were considered.",
            "--format",
            "json",
        ]
    ) == 0
    payload = json.loads(capsys.readouterr().out)

    assert payload["status"] == "ok"
    family_stack = dict(payload["run_summary"]["family_stack"])
    assert family_stack["eligible_family_count"] >= 3
    assert family_stack["categorical_strategy"] in {
        "categorical_native_preferred",
        "encoded_numeric_fallback",
        "numeric_or_low_categorical",
    }
    assert len(family_stack["probe_tier_one_families"]) >= 1

    for artifact_name in (
        "family_registry_extension.json",
        "family_readiness_report.json",
        "family_eligibility_matrix.json",
        "family_probe_policy.json",
        "categorical_strategy_report.json",
        "family_specialization_report.json",
    ):
        assert (run_dir / artifact_name).exists(), artifact_name
