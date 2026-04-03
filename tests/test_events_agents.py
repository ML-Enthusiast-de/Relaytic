from __future__ import annotations

from pathlib import Path

from relaytic.events import run_event_bus_review
from relaytic.policies import load_policy
from relaytic.runtime import ensure_runtime_initialized, record_stage_completion, record_stage_start


def test_event_bus_review_projects_dispatches_from_runtime_events(tmp_path: Path) -> None:
    run_dir = tmp_path / "event_bus_run"
    data_path = tmp_path / "data.csv"
    data_path.write_text("feature,target\n1,0\n2,1\n", encoding="utf-8")
    policy = load_policy().policy

    ensure_runtime_initialized(
        run_dir=run_dir,
        policy=policy,
        source_surface="cli",
        source_command="unit_test_bootstrap",
    )
    (run_dir / "dataset_profile.json").write_text("{}", encoding="utf-8")
    token = record_stage_start(
        run_dir=run_dir,
        policy=policy,
        stage="investigation",
        source_surface="cli",
        source_command="unit_test_investigation",
        data_path=str(data_path),
        input_artifacts=["task_brief.json"],
    )
    record_stage_completion(
        run_dir=run_dir,
        policy=policy,
        stage_token=token,
        output_artifacts=[str(run_dir / "dataset_profile.json")],
        summary="Investigation completed for event-bus projection.",
    )

    result = run_event_bus_review(run_dir=run_dir, policy=policy)
    bundle = result.bundle.to_dict()

    assert bundle["event_schema"]["event_type_count"] >= 15
    assert any(item["event_type"] == "stage_started" for item in bundle["event_schema"]["event_types"])
    assert any(item["event_type"] == "stage_failed" for item in bundle["event_schema"]["event_types"])
    assert any(item["event_type"] == "permission_allowed" for item in bundle["event_schema"]["event_types"])
    assert bundle["event_subscription_registry"]["subscription_count"] >= 3
    assert bundle["hook_dispatch_report"]["dispatch_count"] >= 2
    assert all(item["source_of_truth_preserved"] is True for item in bundle["hook_dispatch_report"]["recent_dispatches"])
    assert any(item["hook_kind"] == "event_subscriber" for item in bundle["hook_registry"]["hooks"])
    assert any(item["hook_kind"] == "runtime_hook" for item in bundle["hook_registry"]["hooks"])
