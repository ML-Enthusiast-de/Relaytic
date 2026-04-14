from __future__ import annotations

import json
from pathlib import Path

from relaytic.ui.cli import main
from tests.public_datasets import write_public_review_queue_dataset


def test_cli_slice15k_run_materializes_operating_point_artifacts_and_explains_threshold(
    tmp_path: Path,
    capsys,
) -> None:
    run_dir = tmp_path / "slice15k_review_queue"
    data_path = write_public_review_queue_dataset(tmp_path / "slice15k_review_queue.csv", max_rows=420)

    assert main(
        [
            "run",
            "--run-dir",
            str(run_dir),
            "--data-path",
            str(data_path),
            "--text",
            "Predict default_flag from the account risk features, keep false negatives low, and keep operator review load manageable. Do everything on your own.",
            "--format",
            "json",
        ]
    ) == 0
    payload = json.loads(capsys.readouterr().out)

    assert payload["status"] == "ok"
    assert payload["run_summary"]["operating_point"]["status"] == "ok"
    assert payload["run_summary"]["operating_point"]["selected_threshold"] is not None
    assert payload["run_summary"]["operating_point"]["selected_calibration_method"] is not None
    assert payload["run_summary"]["operating_point"]["decision_cost_profile_kind"] in {
        "binary_review_queue",
        "rare_event_review_queue",
    }

    for filename in (
        "calibration_strategy_report.json",
        "operating_point_contract.json",
        "threshold_search_report.json",
        "decision_cost_profile.json",
        "review_budget_optimization_report.json",
        "abstention_policy_report.json",
    ):
        assert (run_dir / filename).exists(), filename

    assert main(
        [
            "assist",
            "turn",
            "--run-dir",
            str(run_dir),
            "--message",
            "why this threshold and calibration?",
            "--format",
            "json",
        ]
    ) == 0
    assist_payload = json.loads(capsys.readouterr().out)

    assert assist_payload["status"] == "ok"
    assert assist_payload["turn"]["intent_type"] == "explain"
    assert assist_payload["audit"]["question_type"] == "operating_point"
    assert "operating_point_contract.json" in assist_payload["audit"]["evidence_refs"]

    assert main(["benchmark", "run", "--run-dir", str(run_dir), "--data-path", str(data_path), "--overwrite", "--format", "json"]) == 0
    benchmark_payload = json.loads(capsys.readouterr().out)

    assert benchmark_payload["status"] == "ok"
    assert benchmark_payload["benchmark"]["selected_threshold"] is not None
    assert benchmark_payload["benchmark"]["selected_calibration_method"] is not None
    assert benchmark_payload["bundle"]["operating_point_contract"]["status"] == "ok"
    assert benchmark_payload["bundle"]["calibration_strategy_report"]["status"] == "ok"
