from __future__ import annotations

import json
from pathlib import Path

import pytest

pytest.importorskip("sklearn.datasets")

from relaytic.interoperability import relaytic_assist_turn
from relaytic.ui.cli import main

from tests.public_datasets import write_public_breast_cancer_dataset


def test_cli_slice14_materializes_feasibility_and_audit_surfaces(tmp_path: Path, capsys) -> None:
    run_dir = tmp_path / "slice14_public_binary"
    data_path = write_public_breast_cancer_dataset(tmp_path / "slice14_public_breast_cancer.csv")
    config_path = tmp_path / "slice14_config.yaml"
    config_path.write_text(
        "\n".join(
            [
                "policy:",
                "  permissions:",
                "    default_mode: review",
            ]
        ),
        encoding="utf-8",
    )

    assert main(
        [
            "run",
            "--run-dir",
            str(run_dir),
            "--data-path",
            str(data_path),
            "--text",
            "Do everything on your own. Predict diagnosis_flag from the provided features.",
            "--format",
            "json",
        ]
    ) == 0
    _ = json.loads(capsys.readouterr().out)

    (run_dir / "champion_vs_candidate.json").write_text(
        json.dumps(
            {
                "fresh_data_behavior": {
                    "ood_summary": {"overall_ood_fraction": 0.41},
                }
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    (run_dir / "permission_mode.json").write_text(
        json.dumps(
            {
                "current_mode": "review",
                "status": "ok",
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    assert main(
        [
            "decision",
            "review",
            "--run-dir",
            str(run_dir),
            "--config",
            str(config_path),
            "--overwrite",
            "--format",
            "json",
        ]
    ) == 0
    decision_payload = json.loads(capsys.readouterr().out)

    assert decision_payload["status"] == "ok"
    assert decision_payload["decision_lab"]["selected_next_action"] == "request_operator_review"
    assert decision_payload["feasibility"]["recommended_direction"] == "add_data"
    assert decision_payload["feasibility"]["deployability"] == "not_deployable"
    assert decision_payload["feasibility"]["gate_open"] is True

    for filename in (
        "trajectory_constraint_report.json",
        "feasible_region_map.json",
        "extrapolation_risk_report.json",
        "decision_constraint_report.json",
        "action_boundary_report.json",
        "deployability_assessment.json",
        "review_gate_state.json",
        "constraint_override_request.json",
        "counterfactual_region_report.json",
    ):
        assert (run_dir / filename).exists(), filename

    assert main(["show", "--run-dir", str(run_dir), "--format", "json"]) == 0
    show_payload = json.loads(capsys.readouterr().out)
    run_summary = dict(show_payload["run_summary"])
    assert run_summary["feasibility"]["recommended_direction"] == "add_data"
    assert run_summary["decision_lab"]["selected_next_action"] == "request_operator_review"
    assert run_summary["result_contract"]["recommended_direction"] == "add_data"

    assert main(
        [
            "assist",
            "turn",
            "--run-dir",
            str(run_dir),
            "--message",
            "why not a rerun?",
            "--format",
            "json",
        ]
    ) == 0
    assist_payload = json.loads(capsys.readouterr().out)
    assert assist_payload["audit"]["question_type"] == "why_not_rerun"
    assert "did not recommend a rerun" in assist_payload["audit"]["answer"].lower()

    agent_payload = relaytic_assist_turn(run_dir=str(run_dir), message="why did you use this model?")
    assert agent_payload["surface_payload"]["audit"]["question_type"] == "model_choice"
    assert agent_payload["surface_payload"]["audit"]["actor_type"] == "agent"
