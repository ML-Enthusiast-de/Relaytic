from __future__ import annotations

import json
from pathlib import Path

from relaytic.core.json_utils import write_json
from relaytic.ui.cli import main
from relaytic.workspace import default_workspace_dir
from tests.public_datasets import write_public_breast_cancer_dataset


def test_cli_daemon_slice_materializes_and_resumes_background_search(tmp_path: Path, capsys) -> None:
    run_dir = tmp_path / "daemon_public_binary"
    data_path = write_public_breast_cancer_dataset(tmp_path / "daemon_breast_cancer.csv")

    assert main(
        [
            "run",
            "--run-dir",
            str(run_dir),
            "--data-path",
            str(data_path),
            "--text",
            "Do everything on your own. Classify diagnosis_flag from the measurement columns and make background continuity explicit.",
            "--format",
            "json",
        ]
    ) == 0
    capsys.readouterr()

    assert main(["search", "review", "--run-dir", str(run_dir), "--overwrite", "--format", "json"]) == 0
    capsys.readouterr()
    write_json(
        run_dir / "search_controller_plan.json",
        {
            "status": "ok",
            "recommended_action": "expand_challenger_portfolio",
            "recommended_direction": "same_data",
            "planned_trial_count": 10,
        },
        indent=2,
        ensure_ascii=False,
        sort_keys=True,
    )

    assert main(["daemon", "review", "--run-dir", str(run_dir), "--format", "json"]) == 0
    review_payload = json.loads(capsys.readouterr().out)
    assert review_payload["daemon"]["job_count"] >= 1

    assert main(["daemon", "run-job", "--run-dir", str(run_dir), "--job-id", "job_search_campaign", "--format", "json"]) == 0
    run_payload = json.loads(capsys.readouterr().out)
    assert run_payload["job"]["status"] == "paused"
    assert run_payload["daemon"]["resumable_job_count"] >= 1

    assert main(["daemon", "resume-job", "--run-dir", str(run_dir), "--job-id", "job_search_campaign", "--format", "json"]) == 0
    resume_payload = json.loads(capsys.readouterr().out)
    assert resume_payload["job"]["status"] == "completed"

    assert main(["daemon", "show", "--run-dir", str(run_dir), "--format", "json"]) == 0
    show_payload = json.loads(capsys.readouterr().out)
    assert show_payload["daemon"]["job_count"] >= 1
    assert show_payload["daemon"]["resumable_job_count"] == 0


def test_cli_daemon_background_job_can_go_through_explicit_approval_and_workspace_summary(tmp_path: Path, capsys) -> None:
    run_dir = tmp_path / "daemon_review_mode"
    workspace_dir = default_workspace_dir(run_dir=run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    workspace_dir.mkdir(parents=True, exist_ok=True)

    write_json(run_dir / "run_summary.json", {"run_id": "run_daemon_review_mode"}, indent=2, ensure_ascii=False, sort_keys=True)
    write_json(workspace_dir / "workspace_state.json", {"workspace_id": "workspace_daemon_review_mode", "status": "ok"}, indent=2, ensure_ascii=False, sort_keys=True)
    write_json(run_dir / "result_contract.json", {"status": "needs_review"}, indent=2, ensure_ascii=False, sort_keys=True)
    write_json(run_dir / "confidence_posture.json", {"review_need": "required"}, indent=2, ensure_ascii=False, sort_keys=True)
    write_json(
        run_dir / "search_controller_plan.json",
        {
            "status": "ok",
            "recommended_action": "expand_challenger_portfolio",
            "recommended_direction": "same_data",
            "planned_trial_count": 10,
        },
        indent=2,
        ensure_ascii=False,
        sort_keys=True,
    )

    assert main(["daemon", "run-job", "--run-dir", str(run_dir), "--job-id", "job_search_campaign", "--format", "json"]) == 0
    first_payload = json.loads(capsys.readouterr().out)
    request_id = first_payload["job"]["request_id"]
    assert first_payload["job"]["status"] == "approval_requested"
    assert request_id

    assert main(
        [
            "permissions",
            "decide",
            "--run-dir",
            str(run_dir),
            "--request-id",
            str(request_id),
            "--decision",
            "approve",
            "--format",
            "json",
        ]
    ) == 0
    capsys.readouterr()

    assert main(["daemon", "run-job", "--run-dir", str(run_dir), "--job-id", "job_search_campaign", "--format", "json"]) == 0
    second_payload = json.loads(capsys.readouterr().out)
    assert second_payload["job"]["status"] == "paused"

    assert main(["workspace", "show", "--run-dir", str(run_dir), "--format", "json"]) == 0
    workspace_payload = json.loads(capsys.readouterr().out)
    assert workspace_payload["run_summary"]["daemon"]["resumable_job_count"] >= 1
    assert workspace_payload["result_contract"]["result_contract"]["status"]
    assert workspace_payload["result_contract"]["confidence_posture"]["review_need"] in {"required", "recommended", "none"}
