from __future__ import annotations

import json
from pathlib import Path

from relaytic.learnings import default_learnings_state_dir
from relaytic.ui.cli import main
from tests.public_datasets import write_public_breast_cancer_dataset


def test_cli_workspace_result_contract_and_iteration_surfaces_materialize_for_public_dataset(
    tmp_path: Path,
    capsys,
) -> None:
    run_dir = tmp_path / "workspace_public_binary"
    data_path = write_public_breast_cancer_dataset(tmp_path / "workspace_breast_cancer.csv")

    assert main(
        [
            "run",
            "--run-dir",
            str(run_dir),
            "--data-path",
            str(data_path),
            "--text",
            "Do everything on your own. Classify diagnosis_flag from the measurement columns and make the next-step contract explicit.",
            "--format",
            "json",
        ]
    ) == 0
    run_payload = json.loads(capsys.readouterr().out)
    summary = dict(run_payload["run_summary"])

    workspace = dict(summary["workspace"])
    result_contract = dict(summary["result_contract"])
    iteration = dict(summary["iteration"])

    assert workspace["workspace_id"] is not None
    assert workspace["lineage_run_count"] >= 1
    assert result_contract["recommended_direction"] in {"same_data", "add_data", "new_dataset"}
    assert iteration["recommended_direction"] in {"same_data", "add_data", "new_dataset"}

    workspace_dir = tmp_path / "workspace"
    expected_paths = [
        workspace_dir / "workspace_state.json",
        workspace_dir / "workspace_lineage.json",
        workspace_dir / "workspace_focus_history.json",
        workspace_dir / "workspace_memory_policy.json",
        workspace_dir / "next_run_plan.json",
        run_dir / "result_contract.json",
        run_dir / "confidence_posture.json",
        run_dir / "belief_revision_triggers.json",
        run_dir / "focus_decision_record.json",
        run_dir / "data_expansion_candidates.json",
        run_dir / "reports" / "user_result_report.md",
        run_dir / "reports" / "agent_result_report.md",
    ]
    for path in expected_paths:
        assert path.exists(), f"Expected artifact missing: {path}"

    contract = json.loads((run_dir / "result_contract.json").read_text(encoding="utf-8"))
    user_report = (run_dir / "reports" / "user_result_report.md").read_text(encoding="utf-8")
    agent_report = (run_dir / "reports" / "agent_result_report.md").read_text(encoding="utf-8")
    direction = dict(contract["recommended_next_move"])["direction"]

    assert "# Relaytic User Result Report" in user_report
    assert "# Relaytic Agent Result Report" in agent_report
    assert f"`{direction}`" in user_report
    assert f"`{direction}`" in agent_report
    assert "What Would Change Relaytic's Mind" in user_report
    assert "## Revision Triggers" in agent_report

    assert main(["workspace", "show", "--run-dir", str(run_dir), "--format", "json"]) == 0
    workspace_payload = json.loads(capsys.readouterr().out)
    assert workspace_payload["status"] == "ok"
    assert workspace_payload["workspace"]["workspace_state"]["workspace_id"] == workspace["workspace_id"]
    assert (
        workspace_payload["result_contract"]["result_contract"]["recommended_next_move"]["direction"]
        == direction
    )
    assert workspace_payload["next_run_plan"]["recommended_direction"] == iteration["recommended_direction"]


def test_cli_workspace_lineage_and_new_dataset_continuation_govern_governed_learnings(
    tmp_path: Path,
    capsys,
) -> None:
    data_path = write_public_breast_cancer_dataset(tmp_path / "workspace_lineage_breast_cancer.csv")
    first_run = tmp_path / "workspace_lineage_first"
    second_run = tmp_path / "workspace_lineage_second"

    for run_dir in (first_run, second_run):
        assert main(
            [
                "run",
                "--run-dir",
                str(run_dir),
                "--data-path",
                str(data_path),
                "--text",
                "Do everything on your own. Classify diagnosis_flag from the measurement columns and preserve cross-run continuity.",
                "--format",
                "json",
            ]
        ) == 0
        capsys.readouterr()

    workspace_dir = tmp_path / "workspace"
    lineage = json.loads((workspace_dir / "workspace_lineage.json").read_text(encoding="utf-8"))
    assert lineage["run_count"] >= 2

    assert main(
        [
            "workspace",
            "continue",
            "--run-dir",
            str(second_run),
            "--direction",
            "new_dataset",
            "--notes",
            "restart on a new dataset and expire stale workspace guidance",
            "--format",
            "json",
        ]
    ) == 0
    continuation_payload = json.loads(capsys.readouterr().out)
    assert continuation_payload["status"] == "ok"
    assert continuation_payload["continuation"]["selection_id"] == "new_dataset"
    assert continuation_payload["run_summary"]["handoff"]["selected_focus_id"] == "new_dataset"
    assert continuation_payload["next_run_plan"]["recommended_direction"] in {"same_data", "add_data", "new_dataset"}

    state_dir = default_learnings_state_dir(run_dir=second_run)
    learnings_state = json.loads((state_dir / "learnings_state.json").read_text(encoding="utf-8"))
    statuses = {str(item.get("status")) for item in learnings_state.get("entries", []) if isinstance(item, dict)}
    reasons = {
        str(item.get("invalidation_reason"))
        for item in learnings_state.get("entries", [])
        if isinstance(item, dict) and item.get("status") == "expired"
    }
    assert "expired" in statuses
    assert "new_dataset_restart_selected" in reasons


def test_cli_assist_workspace_review_answers_belief_revision_and_focus_questions(
    tmp_path: Path,
    capsys,
) -> None:
    run_dir = tmp_path / "assist_workspace_review"
    data_path = write_public_breast_cancer_dataset(tmp_path / "assist_workspace_breast_cancer.csv")

    assert main(
        [
            "run",
            "--run-dir",
            str(run_dir),
            "--data-path",
            str(data_path),
            "--text",
            "Do everything on your own. Classify diagnosis_flag from the measurement columns and preserve a clear workspace contract.",
            "--format",
            "json",
        ]
    ) == 0
    capsys.readouterr()

    assert main(
        [
            "assist",
            "turn",
            "--run-dir",
            str(run_dir),
            "--message",
            "show the workspace",
            "--format",
            "json",
        ]
    ) == 0
    workspace_turn = json.loads(capsys.readouterr().out)
    assert workspace_turn["status"] == "ok"
    assert workspace_turn["turn"]["action_kind"] == "show_workspace"

    assert main(
        [
            "assist",
            "turn",
            "--run-dir",
            str(run_dir),
            "--message",
            "what would change your mind?",
        ]
    ) == 0
    revision_output = capsys.readouterr().out
    assert "# Relaytic Workspace Review" in revision_output
    assert "Belief revision triggers" in revision_output
