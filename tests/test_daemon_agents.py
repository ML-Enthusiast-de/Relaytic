from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

from relaytic.core.json_utils import write_json
from relaytic.daemon import resume_background_job, run_background_job, run_daemon_review
from relaytic.permissions import apply_permission_decision
from relaytic.workspace import default_workspace_dir


def test_daemon_review_materializes_search_memory_and_pulse_jobs(tmp_path: Path) -> None:
    run_dir = tmp_path / "daemon_review"
    workspace_dir = default_workspace_dir(run_dir=run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    workspace_dir.mkdir(parents=True, exist_ok=True)

    _write_json(run_dir / "run_summary.json", {"run_id": "run_daemon_review", "benchmark": {"beat_target_state": None}})
    _write_json(workspace_dir / "workspace_state.json", {"workspace_id": "workspace_daemon_review", "status": "ok"})
    _write_json(
        run_dir / "search_controller_plan.json",
        {
            "status": "ok",
            "recommended_action": "expand_challenger_portfolio",
            "recommended_direction": "same_data",
            "planned_trial_count": 12,
        },
    )
    _write_json(
        run_dir / "memory_compaction_plan.json",
        {
            "status": "ok",
            "pin_candidate_count": 2,
            "plan_items": [
                {"candidate_id": "memory_1", "category": "benchmark_gap", "priority": "high", "reason": "benchmark gap remains open"},
                {"candidate_id": "memory_2", "category": "calibration", "priority": "medium", "reason": "calibration lesson should be pinned"},
            ],
        },
    )
    _write_json(
        run_dir / "pulse_recommendations.json",
        {
            "status": "ok",
            "queued_actions": [{"action_id": "pulse_1", "kind": "follow_up"}],
        },
    )

    result = run_daemon_review(run_dir=run_dir, policy={})
    bundle = result.bundle.to_dict()
    jobs = {item["job_id"]: item for item in bundle["background_job_registry"]["jobs"]}

    assert {"job_search_campaign", "job_memory_maintenance", "job_pulse_followup"}.issubset(jobs)
    assert bundle["daemon_state"]["job_count"] >= 3
    assert bundle["memory_maintenance_queue"]["queued_task_count"] == 2


def test_daemon_background_search_requires_approval_then_resumes_from_checkpoint(tmp_path: Path) -> None:
    run_dir = tmp_path / "daemon_search_resume"
    workspace_dir = default_workspace_dir(run_dir=run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    workspace_dir.mkdir(parents=True, exist_ok=True)

    _write_json(run_dir / "run_summary.json", {"run_id": "run_daemon_search_resume"})
    _write_json(workspace_dir / "workspace_state.json", {"workspace_id": "workspace_daemon_search_resume", "status": "ok"})
    _write_json(run_dir / "result_contract.json", {"status": "needs_review"})
    _write_json(run_dir / "confidence_posture.json", {"review_need": "required"})
    _write_json(
        run_dir / "search_controller_plan.json",
        {
            "status": "ok",
            "recommended_action": "expand_challenger_portfolio",
            "recommended_direction": "same_data",
            "planned_trial_count": 18,
        },
    )

    first = run_background_job(run_dir=run_dir, job_id="job_search_campaign", policy={})
    first_bundle = first.bundle.to_dict()
    first_job = _job(first_bundle, "job_search_campaign")

    assert first_job["status"] == "approval_requested"
    request_id = first_job["request_id"]
    assert request_id
    assert first_bundle["background_approval_queue"]["pending_approval_count"] == 1

    apply_permission_decision(run_dir=run_dir, request_id=str(request_id), decision="approve", policy={})

    second = run_background_job(run_dir=run_dir, job_id="job_search_campaign", policy={})
    second_bundle = second.bundle.to_dict()
    second_job = _job(second_bundle, "job_search_campaign")

    assert second_job["status"] == "paused"
    assert second_job["checkpoint_id"] is not None
    assert second_bundle["background_checkpoint"]["resume_ready_count"] >= 1

    resumed = resume_background_job(run_dir=run_dir, job_id="job_search_campaign", policy={})
    resumed_bundle = resumed.bundle.to_dict()
    resumed_job = _job(resumed_bundle, "job_search_campaign")

    assert resumed_job["status"] == "completed"
    assert resumed_bundle["search_resume_plan"]["resume_ready"] is False
    assert resumed_bundle["stale_job_report"]["stale_job_count"] == 0


def test_daemon_memory_maintenance_writes_before_after_report(tmp_path: Path) -> None:
    run_dir = tmp_path / "daemon_memory"
    workspace_dir = default_workspace_dir(run_dir=run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    workspace_dir.mkdir(parents=True, exist_ok=True)

    _write_json(run_dir / "run_summary.json", {"run_id": "run_daemon_memory"})
    _write_json(workspace_dir / "workspace_state.json", {"workspace_id": "workspace_daemon_memory", "status": "ok"})
    _write_json(run_dir / "completion_decision.json", {"status": "done", "action": "complete"})
    _write_json(
        run_dir / "memory_compaction_plan.json",
        {
            "status": "ok",
            "pin_candidate_count": 3,
            "plan_items": [
                {"candidate_id": "memory_1", "category": "benchmark_gap", "priority": "high", "reason": "retain benchmark memory"},
                {"candidate_id": "memory_2", "category": "calibration", "priority": "medium", "reason": "retain calibration memory"},
                {"candidate_id": "memory_3", "category": "operator_feedback", "priority": "medium", "reason": "retain operator feedback"},
            ],
        },
    )
    _write_json(
        run_dir / "memory_compaction_report.json",
        {"retained_categories": ["benchmark_gap", "calibration", "operator_feedback"]},
    )

    result = run_background_job(run_dir=run_dir, job_id="job_memory_maintenance", policy={})
    report = result.bundle.to_dict()["memory_maintenance_report"]

    assert report["executed"] is True
    assert report["executed_task_count"] == 3
    assert report["before_task_count"] == 3
    assert report["after_task_count"] == 0
    assert "benchmark_gap" in report["retained_categories"]


def test_daemon_review_surfaces_stale_jobs_with_recovery_suggestion(tmp_path: Path) -> None:
    run_dir = tmp_path / "daemon_stale"
    workspace_dir = default_workspace_dir(run_dir=run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    workspace_dir.mkdir(parents=True, exist_ok=True)

    stale_time = (datetime.now(timezone.utc) - timedelta(days=2)).isoformat()
    _write_json(run_dir / "run_summary.json", {"run_id": "run_daemon_stale"})
    _write_json(workspace_dir / "workspace_state.json", {"workspace_id": "workspace_daemon_stale", "status": "ok"})
    _write_json(
        run_dir / "search_controller_plan.json",
        {
            "status": "ok",
            "recommended_action": "expand_challenger_portfolio",
            "recommended_direction": "same_data",
            "planned_trial_count": 9,
        },
    )
    _write_json(
        run_dir / "background_job_registry.json",
        {
            "jobs": [
                {
                    "job_id": "job_search_campaign",
                    "job_kind": "search_campaign",
                    "status": "paused",
                    "approval_required": True,
                    "approval_action_id": "relaytic_run_background_search",
                    "resume_supported": True,
                    "checkpoint_id": "checkpoint_old",
                    "created_at": stale_time,
                    "updated_at": stale_time,
                    "summary": "Paused earlier",
                    "metadata": {"planned_trial_count": 9},
                }
            ]
        },
    )
    _write_json(
        run_dir / "background_checkpoint.json",
        {
            "checkpoints": [
                {
                    "checkpoint_id": "checkpoint_old",
                    "job_id": "job_search_campaign",
                    "job_kind": "search_campaign",
                    "recorded_at": stale_time,
                    "resume_ready": True,
                    "status": "paused",
                    "summary": "Old checkpoint",
                }
            ]
        },
    )

    result = run_daemon_review(run_dir=run_dir, policy={"daemon": {"stale_after_minutes": 5}})
    stale = result.bundle.to_dict()["stale_job_report"]
    job = _job(result.bundle.to_dict(), "job_search_campaign")

    assert stale["stale_job_count"] == 1
    assert job["status"] == "stale"
    assert "resume-job" in str(job["recovery_suggestion"])


def _write_json(path: Path, payload: dict[str, object]) -> None:
    write_json(path, payload, indent=2, ensure_ascii=False, sort_keys=True)


def _job(bundle: dict[str, object], job_id: str) -> dict[str, object]:
    registry = dict(bundle["background_job_registry"])
    for item in registry["jobs"]:
        candidate = dict(item)
        if candidate["job_id"] == job_id:
            return candidate
    raise AssertionError(f"Job not found: {job_id}")
