import csv
from pathlib import Path

from relaytic.completion import read_completion_bundle, run_completion_review, write_completion_bundle
from relaytic.context import (
    build_context_controls_from_policy,
    default_data_origin,
    default_domain_brief,
    default_task_brief,
)
from relaytic.evidence import run_evidence_review
from relaytic.investigation import run_investigation
from relaytic.mandate import (
    build_mandate_controls_from_policy,
    build_run_brief,
    build_work_preferences,
    default_lab_mandate,
)
from relaytic.planning import execute_planned_route, run_planning
from relaytic.policies import load_policy


def _write_dataset(path: Path) -> Path:
    rows = [
        ["timestamp", "sensor_a", "sensor_b", "failure_flag", "future_failure_flag", "post_inspection_flag"],
        ["2025-01-01T00:00:00", 10.0, 100.0, 0, 0, 0],
        ["2025-01-01T00:01:00", 11.0, 102.0, 0, 0, 0],
        ["2025-01-01T00:02:00", 12.0, 101.0, 1, 1, 1],
        ["2025-01-01T00:03:00", 13.0, 103.0, 0, 0, 0],
        ["2025-01-01T00:04:00", 14.0, 105.0, 1, 1, 1],
        ["2025-01-01T00:05:00", 15.0, 104.0, 0, 0, 0],
        ["2025-01-01T00:06:00", 16.0, 106.0, 1, 1, 1],
        ["2025-01-01T00:07:00", 17.0, 108.0, 0, 0, 0],
        ["2025-01-01T00:08:00", 18.0, 107.0, 1, 1, 1],
        ["2025-01-01T00:09:00", 19.0, 109.0, 0, 0, 0],
        ["2025-01-01T00:10:00", 20.0, 110.0, 1, 1, 1],
        ["2025-01-01T00:11:00", 21.0, 111.0, 0, 0, 0],
        ["2025-01-01T00:12:00", 22.0, 112.0, 1, 1, 1],
        ["2025-01-01T00:13:00", 23.0, 113.0, 0, 0, 0],
        ["2025-01-01T00:14:00", 24.0, 114.0, 1, 1, 1],
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        csv.writer(handle).writerows(rows)
    return path


def _build_foundation(policy: dict, *, objective: str = "best_robust_pareto_front") -> tuple[dict, dict]:
    mandate_controls = build_mandate_controls_from_policy(policy)
    context_controls = build_context_controls_from_policy(policy)
    mandate_bundle = {
        "lab_mandate": default_lab_mandate(mandate_controls).to_dict(),
        "work_preferences": build_work_preferences(
            mandate_controls,
            policy=policy,
            execution_mode_preference="autonomous",
        ).to_dict(),
        "run_brief": build_run_brief(
            mandate_controls,
            policy=policy,
            objective=objective,
            target_column="failure_flag",
            success_criteria=["Catch failures before scrap decisions."],
            binding_constraints=["Do not use future or post-inspection features."],
        ).to_dict(),
    }
    context_bundle = {
        "data_origin": default_data_origin(
            context_controls,
            source_name="line_alarm_history",
            source_type="historical_snapshot",
        ).to_dict(),
        "domain_brief": default_domain_brief(
            context_controls,
            system_name="production_line",
            summary="Predict likely failures early enough to intervene before scrap is created.",
            forbidden_features=["future_failure_flag", "post_inspection_flag"],
        ).to_dict(),
        "task_brief": default_task_brief(
            context_controls,
            problem_statement="Predict failure flags from upstream process sensors.",
            target_column="failure_flag",
            success_criteria=["Maximize useful early warning value."],
            failure_costs=["Missed failures lead to scrap and avoidable downtime."],
        ).to_dict(),
    }
    return mandate_bundle, context_bundle


def _build_executed_run(tmp_path: Path, *, objective: str = "best_robust_pareto_front") -> tuple[Path, Path, dict, dict, dict, dict]:
    data_path = _write_dataset(tmp_path / "slice07.csv")
    run_dir = tmp_path / "run_slice07"
    policy = load_policy().policy
    mandate_bundle, context_bundle = _build_foundation(policy, objective=objective)
    investigation_bundle = run_investigation(
        data_path=str(data_path),
        policy=policy,
        mandate_bundle=mandate_bundle,
        context_bundle=context_bundle,
    ).to_dict()
    planning_bundle = run_planning(
        data_path=str(data_path),
        policy=policy,
        mandate_bundle=mandate_bundle,
        context_bundle=context_bundle,
        investigation_bundle=investigation_bundle,
    )
    execution = execute_planned_route(
        run_dir=run_dir,
        data_path=str(data_path),
        planning_bundle=planning_bundle,
    )
    evidence_result = run_evidence_review(
        run_dir=run_dir,
        data_path=str(data_path),
        policy=policy,
        mandate_bundle=mandate_bundle,
        context_bundle=context_bundle,
        intake_bundle={
            "autonomy_mode": {
                "requested_mode": "autonomous",
                "operator_signal": "do everything on your own",
            },
            "clarification_queue": {"active_count": 0},
            "assumption_log": {"entries": [{"assumption": "autonomous default request"}]},
        },
        investigation_bundle=investigation_bundle,
        planning_bundle=execution.planning_bundle.to_dict(),
    )
    return (
        data_path,
        run_dir,
        policy,
        mandate_bundle,
        context_bundle,
        {
            "intake_bundle": {
                "autonomy_mode": {
                    "requested_mode": "autonomous",
                    "operator_signal": "do everything on your own",
                },
                "clarification_queue": {"active_count": 0},
                "assumption_log": {"entries": [{"assumption": "autonomous default request"}]},
            },
            "investigation_bundle": investigation_bundle,
            "planning_bundle": execution.planning_bundle.to_dict(),
            "evidence_bundle": evidence_result.bundle.to_dict(),
        },
    )


def test_run_completion_review_generates_completion_bundle_and_stage_state(tmp_path: Path) -> None:
    _, run_dir, policy, mandate_bundle, context_bundle, payloads = _build_executed_run(tmp_path)

    result = run_completion_review(
        run_dir=run_dir,
        policy=policy,
        mandate_bundle=mandate_bundle,
        context_bundle=context_bundle,
        intake_bundle=payloads["intake_bundle"],
        investigation_bundle=payloads["investigation_bundle"],
        planning_bundle=payloads["planning_bundle"],
        evidence_bundle=payloads["evidence_bundle"],
    )
    written = write_completion_bundle(run_dir, bundle=result.bundle)
    bundle = read_completion_bundle(run_dir)

    assert result.bundle.completion_decision.action
    assert result.bundle.completion_decision.current_stage == "completion_reviewed"
    assert result.bundle.run_state.current_stage == "completion_reviewed"
    assert any(item["stage"] == "evidence_reviewed" for item in result.bundle.stage_timeline.stages)
    assert result.bundle.next_action_queue.actions
    assert Path(written["completion_decision"]).exists()
    assert Path(written["run_state"]).exists()
    assert "completion_decision" in bundle
    assert "next_action_queue" in bundle


def test_run_completion_review_returns_benchmark_needed_when_mandate_requests_benchmark(tmp_path: Path) -> None:
    _, run_dir, policy, mandate_bundle, context_bundle, payloads = _build_executed_run(
        tmp_path,
        objective="benchmark parity against strong reference baselines",
    )
    evidence_bundle = dict(payloads["evidence_bundle"])
    evidence_bundle["challenger_report"] = {
        **dict(evidence_bundle["challenger_report"]),
        "winner": "champion",
    }
    evidence_bundle["audit_report"] = {
        **dict(evidence_bundle["audit_report"]),
        "provisional_recommendation": "promote_baseline_for_mvp",
        "readiness_level": "strong",
        "findings": [],
    }
    evidence_bundle["belief_update"] = {
        **dict(evidence_bundle["belief_update"]),
        "recommended_action": "promote_baseline_for_mvp",
        "open_questions": [],
    }

    result = run_completion_review(
        run_dir=run_dir,
        policy=policy,
        mandate_bundle=mandate_bundle,
        context_bundle=context_bundle,
        intake_bundle=payloads["intake_bundle"],
        investigation_bundle=payloads["investigation_bundle"],
        planning_bundle=payloads["planning_bundle"],
        evidence_bundle=evidence_bundle,
    )

    assert result.bundle.completion_decision.action == "benchmark_needed"
    assert result.bundle.completion_decision.blocking_layer == "missing_benchmark_context"


def test_run_completion_review_returns_memory_support_needed_for_autonomous_fragile_search(tmp_path: Path) -> None:
    _, run_dir, policy, mandate_bundle, context_bundle, payloads = _build_executed_run(tmp_path)
    evidence_bundle = dict(payloads["evidence_bundle"])
    evidence_bundle["challenger_report"] = {
        **dict(evidence_bundle["challenger_report"]),
        "winner": "champion",
    }
    evidence_bundle["audit_report"] = {
        **dict(evidence_bundle["audit_report"]),
        "provisional_recommendation": "continue_experimentation",
        "readiness_level": "conditional",
    }
    evidence_bundle["belief_update"] = {
        **dict(evidence_bundle["belief_update"]),
        "recommended_action": "continue_experimentation",
        "open_questions": ["Search breadth is still narrow."],
    }

    result = run_completion_review(
        run_dir=run_dir,
        policy=policy,
        mandate_bundle=mandate_bundle,
        context_bundle=context_bundle,
        intake_bundle=payloads["intake_bundle"],
        investigation_bundle=payloads["investigation_bundle"],
        planning_bundle=payloads["planning_bundle"],
        evidence_bundle=evidence_bundle,
    )

    assert result.bundle.completion_decision.action == "memory_support_needed"
    assert result.bundle.completion_decision.blocking_layer == "missing_memory_support"


def test_run_completion_review_stops_when_mandate_and_plan_conflict(tmp_path: Path) -> None:
    _, run_dir, policy, mandate_bundle, context_bundle, payloads = _build_executed_run(tmp_path)
    planning_bundle = dict(payloads["planning_bundle"])
    planning_bundle["plan"] = {
        **dict(planning_bundle["plan"]),
        "feature_columns": ["sensor_a", "future_failure_flag"],
    }
    evidence_bundle = dict(payloads["evidence_bundle"])
    evidence_bundle["challenger_report"] = {
        **dict(evidence_bundle["challenger_report"]),
        "winner": "champion",
    }
    evidence_bundle["audit_report"] = {
        **dict(evidence_bundle["audit_report"]),
        "provisional_recommendation": "promote_baseline_for_mvp",
        "readiness_level": "strong",
    }
    evidence_bundle["belief_update"] = {
        **dict(evidence_bundle["belief_update"]),
        "recommended_action": "promote_baseline_for_mvp",
        "open_questions": [],
    }

    result = run_completion_review(
        run_dir=run_dir,
        policy=policy,
        mandate_bundle=mandate_bundle,
        context_bundle=context_bundle,
        intake_bundle=payloads["intake_bundle"],
        investigation_bundle=payloads["investigation_bundle"],
        planning_bundle=planning_bundle,
        evidence_bundle=evidence_bundle,
    )

    assert result.bundle.completion_decision.action == "stop_for_now"
    assert result.bundle.completion_decision.blocking_layer == "policy_or_operator_constraint"
    assert result.bundle.mandate_evidence_review.alignment == "conflict"
