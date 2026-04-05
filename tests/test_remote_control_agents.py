from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import pytest

from relaytic.permissions import evaluate_permission_action, run_permission_review
from relaytic.policies import load_policy
from relaytic.remote_control import (
    apply_remote_approval_decision,
    apply_remote_supervision_handoff,
    read_approval_decision_log,
    run_remote_control_review,
)
from relaytic.runtime import ensure_runtime_initialized, read_event_stream


def _remote_policy(*, enabled: bool) -> dict[str, object]:
    policy = deepcopy(load_policy().policy)
    policy["remote_control"] = {
        "enabled": enabled,
        "transport_kind": "filesystem_sync",
        "transport_scope": "local_only",
        "freshness_seconds": 120,
        "allow_remote_approval_decisions": True,
        "allow_remote_handoffs": True,
        "read_mostly": True,
        "max_recent_decisions": 40,
    }
    return policy


def _bootstrap_remote_run(run_dir: Path, *, policy: dict[str, object]) -> str:
    ensure_runtime_initialized(
        run_dir=run_dir,
        policy=policy,
        source_surface="cli",
        source_command="unit_test_bootstrap",
    )
    review = evaluate_permission_action(
        run_dir=run_dir,
        action_id="relaytic_run_autonomy",
        policy=policy,
        mode_override="review",
        actor_type="operator",
        actor_name="unit-test",
        source_surface="cli",
        source_command="unit_test_permission_check",
    )
    request_id = review.decision.get("request_id")
    assert request_id
    return str(request_id)


def test_remote_control_review_surfaces_pending_approvals_and_freshness(tmp_path: Path) -> None:
    run_dir = tmp_path / "remote_review"
    policy = _remote_policy(enabled=True)
    _bootstrap_remote_run(run_dir, policy=policy)

    review = run_remote_control_review(
        run_dir=run_dir,
        policy=policy,
        actor_type="operator",
        actor_name="unit-test",
    )
    bundle = review.bundle.to_dict()

    assert bundle["approval_request_queue"]["pending_approval_count"] == 1
    assert bundle["remote_transport_report"]["transport_enabled"] is True
    assert bundle["remote_operator_presence"]["freshness_status"] == "fresh"
    assert bundle["remote_session_manifest"]["current_supervisor_type"] == "operator"


def test_remote_control_decision_and_handoff_share_local_authority_truth(tmp_path: Path) -> None:
    run_dir = tmp_path / "remote_apply"
    policy = _remote_policy(enabled=True)
    request_id = _bootstrap_remote_run(run_dir, policy=policy)

    decision_result = apply_remote_approval_decision(
        run_dir=run_dir,
        request_id=request_id,
        decision="approve",
        policy=policy,
        actor_type="agent",
        actor_name="codex-smoke",
    )
    permissions_bundle = run_permission_review(run_dir=run_dir, policy=policy).bundle.to_dict()
    assert permissions_bundle["approval_policy_report"]["pending_approval_count"] == 0
    assert decision_result.bundle.to_dict()["remote_control_audit"]["applied_decision_count"] >= 1

    handoff_result = apply_remote_supervision_handoff(
        run_dir=run_dir,
        to_actor_type="agent",
        to_actor_name="codex-smoke",
        from_actor_type="operator",
        from_actor_name="unit-test",
        reason="Continue supervision remotely.",
        policy=policy,
    )
    handoff_bundle = handoff_result.bundle.to_dict()
    assert handoff_bundle["supervision_handoff"]["current_supervisor"]["actor_type"] == "agent"
    assert any(item["event_type"] == "remote_supervision_handoff" for item in read_event_stream(run_dir))


def test_remote_control_fails_closed_when_disabled_and_leaves_audit_trail(tmp_path: Path) -> None:
    run_dir = tmp_path / "remote_disabled"
    policy = _remote_policy(enabled=False)
    request_id = _bootstrap_remote_run(run_dir, policy=policy)

    with pytest.raises(ValueError, match="Remote supervision is disabled"):
        apply_remote_approval_decision(
            run_dir=run_dir,
            request_id=request_id,
            decision="approve",
            policy=policy,
            actor_type="operator",
            actor_name="unit-test",
        )

    log_entries = read_approval_decision_log(run_dir)
    assert log_entries[-1]["status"] == "blocked"
    review = run_remote_control_review(run_dir=run_dir, policy=policy)
    assert review.bundle.to_dict()["remote_control_audit"]["blocked_action_count"] >= 1
    assert any(item["event_type"] == "remote_access_blocked" for item in read_event_stream(run_dir))
