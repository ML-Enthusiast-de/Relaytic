import json
from pathlib import Path

import pytest

pytest.importorskip("sklearn.datasets")

from relaytic.ui.cli import main

from tests.public_datasets import write_public_breast_cancer_dataset


def test_cli_feedback_add_show_and_rollback_work_on_public_run(tmp_path: Path, capsys) -> None:
    run_dir = tmp_path / "feedback_public_binary"
    data_path = write_public_breast_cancer_dataset(tmp_path / "feedback_public_breast_cancer.csv")

    assert main(
        [
            "run",
            "--run-dir",
            str(run_dir),
            "--data-path",
            str(data_path),
            "--text",
            "Do everything on your own. Classify diagnosis_flag from the measurement columns.",
            "--format",
            "json",
        ]
    ) == 0
    capsys.readouterr()

    assert main(
        [
            "feedback",
            "add",
            "--run-dir",
            str(run_dir),
            "--source-type",
            "human",
            "--feedback-type",
            "route_quality",
            "--message",
            "Boosted_tree_classifier looked stronger in manual review and should be preferred later.",
            "--suggested-route-family",
            "boosted_tree_classifier",
            "--evidence-level",
            "strong",
            "--source-artifact",
            "benchmark_gap_report.json",
            "--format",
            "json",
        ]
    ) == 0
    add_payload = json.loads(capsys.readouterr().out)
    assert add_payload["status"] == "ok"
    assert add_payload["feedback"]["accepted_count"] == 1
    assert (run_dir / "feedback_effect_report.json").exists()
    assert (run_dir / "route_prior_updates.json").exists()

    agent_feedback_path = tmp_path / "agent_feedback.json"
    agent_feedback_path.write_text(
        json.dumps(
            [
                {
                    "feedback_id": "agent_feedback_0001",
                    "source_type": "external_agent",
                    "feedback_type": "route_quality",
                    "message": "Tree ensembles outperformed the linear route on the agent review leaderboard.",
                    "suggested_route_family": "bagged_tree_classifier",
                    "metric_name": "pr_auc",
                    "metric_value": 0.87,
                    "evidence_level": "strong",
                    "source_artifacts": ["leaderboard.csv"],
                },
                {
                    "feedback_id": "outcome_feedback_0001",
                    "source_type": "outcome_observation",
                    "feedback_type": "outcome_evidence",
                    "message": "False positives overloaded the downstream review queue.",
                    "observed_outcome": "false_positive",
                    "evidence_level": "strong",
                    "source_artifacts": ["promotion_decision.json"],
                },
            ],
            indent=2,
        ),
        encoding="utf-8",
    )

    assert main(
        [
            "feedback",
            "add",
            "--run-dir",
            str(run_dir),
            "--input-file",
            str(agent_feedback_path),
            "--format",
            "json",
        ]
    ) == 0
    capsys.readouterr()

    assert main(["feedback", "show", "--run-dir", str(run_dir), "--format", "json"]) == 0
    show_payload = json.loads(capsys.readouterr().out)
    assert show_payload["status"] == "ok"
    assert show_payload["feedback"]["accepted_count"] >= 2
    assert show_payload["feedback"]["decision_policy_suggestion_count"] >= 1
    assert show_payload["bundle"]["feedback_effect_report"]["primary_recommended_action"] == "raise_review_threshold"

    assert main(["show", "--run-dir", str(run_dir), "--format", "json"]) == 0
    summary_payload = json.loads(capsys.readouterr().out)
    assert summary_payload["run_summary"]["feedback"]["accepted_count"] >= 2
    assert summary_payload["run_summary"]["next_step"]["recommended_action"] == "raise_review_threshold"

    assert main(
        [
            "feedback",
            "rollback",
            "--run-dir",
            str(run_dir),
            "--feedback-id",
            "feedback_0001",
            "--format",
            "json",
        ]
    ) == 0
    rollback_payload = json.loads(capsys.readouterr().out)
    assert rollback_payload["feedback"]["reverted_count"] >= 1
    assert "feedback_0001" in rollback_payload["bundle"]["feedback_effect_report"]["reverted_feedback_ids"]
