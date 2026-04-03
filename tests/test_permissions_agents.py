from __future__ import annotations

from pathlib import Path

from relaytic.permissions import apply_permission_decision, evaluate_permission_action, run_permission_review
from relaytic.policies import load_policy
from relaytic.runtime import ensure_runtime_initialized, read_event_stream


def test_permission_modes_and_approval_decisions_are_replayable(tmp_path: Path) -> None:
    run_dir = tmp_path / "permission_run"
    policy = load_policy().policy

    ensure_runtime_initialized(
        run_dir=run_dir,
        policy=policy,
        source_surface="cli",
        source_command="unit_test_bootstrap",
    )

    initial = run_permission_review(run_dir=run_dir, policy=policy).bundle.to_dict()
    assert initial["permission_mode"]["current_mode"] in {"review", "plan", "safe_execute", "bounded_autonomy"}

    review_decision = evaluate_permission_action(
        run_dir=run_dir,
        action_id="relaytic_run_autonomy",
        policy=policy,
        mode_override="review",
        actor_type="operator",
        actor_name="unit-test",
        source_surface="cli",
        source_command="unit_test_permission_check",
    )
    review_bundle = review_decision.bundle.to_dict()
    assert review_decision.decision["decision"] == "approval_requested"
    assert review_decision.decision["request_id"] is not None
    assert review_bundle["approval_policy_report"]["pending_approval_count"] == 1
    assert any(item["event_type"] == "approval_requested" for item in read_event_stream(run_dir))

    bounded = evaluate_permission_action(
        run_dir=run_dir,
        action_id="relaytic_run_autonomy",
        policy=policy,
        mode_override="bounded_autonomy",
        actor_type="agent",
        actor_name="unit-test",
        source_surface="mcp",
        source_command="unit_test_permission_check",
    )
    assert bounded.decision["decision"] == "allowed"
    assert any(item["event_type"] == "permission_allowed" for item in read_event_stream(run_dir))

    request_id = str(review_decision.decision["request_id"])
    approved = apply_permission_decision(
        run_dir=run_dir,
        request_id=request_id,
        decision="approve",
        policy=policy,
        actor_type="operator",
        actor_name="unit-test",
        source_surface="cli",
        source_command="unit_test_permission_decide",
    )
    approved_bundle = approved.bundle.to_dict()
    assert approved.decision["decision"] == "approved"
    assert approved_bundle["approval_policy_report"]["pending_approval_count"] == 0
    assert any(item["event_type"] == "approval_approved" for item in read_event_stream(run_dir))
