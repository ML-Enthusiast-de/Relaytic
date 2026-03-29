import json
from pathlib import Path

from relaytic.tracing import read_jsonl_records
from relaytic.policies import load_policy
from relaytic.runtime import (
    build_runtime_surface,
    ensure_runtime_initialized,
    read_event_stream,
    read_runtime_bundle,
    record_stage_completion,
    record_stage_start,
)


def test_runtime_gateway_records_events_checkpoints_and_denied_accesses(tmp_path: Path) -> None:
    run_dir = tmp_path / "runtime_run"
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

    stage_token = record_stage_start(
        run_dir=run_dir,
        policy=policy,
        stage="investigation",
        source_surface="cli",
        source_command="unit_test_investigation",
        data_path=str(data_path),
        input_artifacts=["task_brief.json", "domain_brief.json"],
    )
    record_stage_completion(
        run_dir=run_dir,
        policy=policy,
        stage_token=stage_token,
        output_artifacts=[str(run_dir / "dataset_profile.json")],
        summary="Investigation completed in the local runtime.",
    )

    bundle = read_runtime_bundle(run_dir)
    surface = build_runtime_surface(run_dir=run_dir)
    audit = dict(bundle["data_access_audit"])
    denied = [
        item
        for item in audit["decisions"]
        if item["stage"] == "investigation" and item["access_kind"] == "raw_rows" and item["decision"] == "denied"
    ]

    assert surface["status"] == "ok"
    assert surface["runtime"]["checkpoint_count"] >= 1
    assert surface["runtime"]["event_count"] >= 4
    assert surface["runtime"]["denied_access_count"] >= 1
    assert any(item["specialist"] == "scientist" for item in denied)
    assert any(item["specialist"] == "focus_council" for item in denied)

    hook_log = dict(bundle["hook_execution_log"])
    executions = list(hook_log["executions"])
    assert any(item["hook_name"] == "stage_transition_observer" for item in executions)
    assert any(item["hook_name"] == "context_influence_writeback" and item["status"] == "blocked_by_policy" for item in executions)

    events = read_event_stream(run_dir)
    assert any(item["event_type"] == "stage_started" for item in events)
    assert any(item["event_type"] == "stage_completed" for item in events)
    assert any(item["event_type"] == "checkpoint_written" for item in events)
    trace_spans = read_jsonl_records(run_dir / "trace_span_log.jsonl")
    assert any(item["event_type"] == "stage_started" for item in trace_spans)
    assert any(item["event_type"] == "stage_completed" for item in trace_spans)


def test_runtime_gateway_executes_bounded_write_hook_when_policy_allows_it(tmp_path: Path) -> None:
    run_dir = tmp_path / "runtime_write_hook"
    policy = load_policy().policy
    policy["runtime"] = {
        **dict(policy.get("runtime", {})),
        "allow_write_hooks": True,
    }

    ensure_runtime_initialized(
        run_dir=run_dir,
        policy=policy,
        source_surface="cli",
        source_command="unit_test_bootstrap",
    )
    (run_dir / "plan.json").write_text("{}", encoding="utf-8")

    stage_token = record_stage_start(
        run_dir=run_dir,
        policy=policy,
        stage="planning",
        source_surface="cli",
        source_command="unit_test_planning",
        data_path=None,
        input_artifacts=["dataset_profile.json", "focus_profile.json"],
    )
    record_stage_completion(
        run_dir=run_dir,
        policy=policy,
        stage_token=stage_token,
        output_artifacts=[str(run_dir / "plan.json")],
        summary="Planning completed with write hooks enabled.",
    )

    hook_log = json.loads((run_dir / "hook_execution_log.json").read_text(encoding="utf-8"))
    context_report = json.loads((run_dir / "context_influence_report.json").read_text(encoding="utf-8"))

    assert any(
        item["hook_name"] == "context_influence_writeback" and item["status"] == "executed"
        for item in hook_log["executions"]
    )
    assert any(item.get("hook_effects") for item in context_report["stage_reports"])
