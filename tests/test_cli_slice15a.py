from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from relaytic.runs.summary import materialize_run_summary
from relaytic.ui.cli import main
from tests.public_datasets import write_public_breast_cancer_dataset


def test_cli_slice15a_preserves_multiclass_string_task_contract(tmp_path: Path, capsys) -> None:
    run_dir = tmp_path / "slice15a_multiclass"
    data_path = tmp_path / "slice15a_multiclass.csv"
    pd.DataFrame(
        {
            "length": [1.0, 1.2, 1.3, 1.4, 1.5, 2.0, 2.2, 2.3, 2.4, 2.5, 3.1, 3.2, 3.3, 3.4, 3.5],
            "width": [0.1, 0.2, 0.15, 0.18, 0.19, 0.9, 0.95, 1.0, 0.98, 1.02, 1.8, 1.75, 1.78, 1.9, 1.88],
            "bean_class": [
                "CALI",
                "CALI",
                "CALI",
                "CALI",
                "CALI",
                "SIRA",
                "SIRA",
                "SIRA",
                "SIRA",
                "SIRA",
                "DERMASON",
                "DERMASON",
                "DERMASON",
                "DERMASON",
                "DERMASON",
            ],
        }
    ).to_csv(data_path, index=False)

    assert main(
        [
            "run",
            "--run-dir",
            str(run_dir),
            "--data-path",
            str(data_path),
            "--text",
            "Classify bean_class from the morphology columns. Do everything on your own.",
            "--format",
            "json",
        ]
    ) == 0
    payload = json.loads(capsys.readouterr().out)

    assert payload["status"] == "ok"
    assert payload["run_summary"]["decision"]["task_type"] == "multiclass_classification"
    assert payload["run_summary"]["task_contract"]["target_semantics"] == "multiclass_labeled_class"
    assert payload["run_summary"]["task_contract"]["multiclass_string_labels_preserved"] is True
    for artifact_name in (
        "task_profile_contract.json",
        "target_semantics_report.json",
        "metric_contract.json",
        "benchmark_mode_report.json",
        "deployment_readiness_report.json",
        "benchmark_vs_deploy_report.json",
        "dataset_semantics_audit.json",
    ):
        assert (run_dir / artifact_name).exists(), artifact_name


def test_cli_slice15a_keeps_benchmark_and_deploy_judgments_separate(tmp_path: Path, capsys) -> None:
    run_dir = tmp_path / "slice15a_benchmark_split"
    data_path = write_public_breast_cancer_dataset(tmp_path / "slice15a_breast_cancer.csv")

    assert main(
        [
            "run",
            "--run-dir",
            str(run_dir),
            "--data-path",
            str(data_path),
            "--text",
            "Classify diagnosis_flag from the measurement columns, benchmark against strong references, and explain the route choice.",
            "--format",
            "json",
        ]
    ) == 0
    capsys.readouterr()

    assert main(["benchmark", "run", "--run-dir", str(run_dir), "--overwrite", "--format", "json"]) == 0
    capsys.readouterr()

    (run_dir / "deployability_assessment.json").write_text(
        json.dumps({"deployability": "conditional", "recommended_action": "hold_for_data_refresh"}, indent=2),
        encoding="utf-8",
    )
    (run_dir / "review_gate_state.json").write_text(
        json.dumps({"gate_open": True, "recommended_action": "request_operator_review"}, indent=2),
        encoding="utf-8",
    )
    (run_dir / "decision_constraint_report.json").write_text(
        json.dumps({"primary_constraint_kind": "data_freshness", "recommended_action": "hold_for_data_refresh"}, indent=2),
        encoding="utf-8",
    )

    summary = materialize_run_summary(run_dir=run_dir)["summary"]

    assert summary["benchmark"]["parity_status"] in {"meets_or_beats_reference", "near_parity", "below_reference"}
    assert summary["benchmark_vs_deploy"]["deployment_readiness"] == "conditional"
    if summary["benchmark"]["parity_status"] in {"meets_or_beats_reference", "near_parity"}:
        assert summary["benchmark_vs_deploy"]["split_detected"] is True
    assert "deploy-ready" in (summary["benchmark_vs_deploy"]["summary"] or "")
