import csv
from pathlib import Path

from relaytic.context import (
    build_context_controls_from_policy,
    default_data_origin,
    default_domain_brief,
    default_task_brief,
)
from relaytic.evidence import read_evidence_bundle, run_evidence_review, write_evidence_bundle
from relaytic.investigation import run_investigation
from relaytic.mandate import (
    build_mandate_controls_from_policy,
    build_run_brief,
    build_work_preferences,
    default_lab_mandate,
)
from relaytic.modeling import run_inference_from_artifacts
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


def _build_foundation(policy: dict) -> tuple[dict, dict]:
    mandate_controls = build_mandate_controls_from_policy(policy)
    context_controls = build_context_controls_from_policy(policy)
    mandate_bundle = {
        "lab_mandate": default_lab_mandate(mandate_controls).to_dict(),
        "work_preferences": build_work_preferences(mandate_controls, policy=policy).to_dict(),
        "run_brief": build_run_brief(
            mandate_controls,
            policy=policy,
            objective="best_robust_pareto_front",
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


def test_run_evidence_review_generates_registry_challenger_ablation_and_reports(tmp_path: Path) -> None:
    data_path = _write_dataset(tmp_path / "slice06.csv")
    run_dir = tmp_path / "run_slice06"
    policy = load_policy().policy
    mandate_bundle, context_bundle = _build_foundation(policy)
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

    result = run_evidence_review(
        run_dir=run_dir,
        data_path=str(data_path),
        policy=policy,
        mandate_bundle=mandate_bundle,
        context_bundle=context_bundle,
        intake_bundle={"assumption_log": {"entries": []}},
        investigation_bundle=investigation_bundle,
        planning_bundle=execution.planning_bundle.to_dict(),
    )
    written = write_evidence_bundle(
        run_dir,
        bundle=result.bundle,
        leaderboard_rows=result.leaderboard_rows,
        technical_report_markdown=result.technical_report_markdown,
        decision_memo_markdown=result.decision_memo_markdown,
    )
    bundle = read_evidence_bundle(run_dir)

    assert result.bundle.experiment_registry.experiments
    assert result.bundle.challenger_report.winner in {"champion", "challenger"}
    assert result.bundle.audit_report.provisional_recommendation
    assert result.bundle.belief_update.recommended_action
    assert len(result.leaderboard_rows) >= 2
    assert "Relaytic Technical Report" in result.technical_report_markdown
    assert "Relaytic Decision Memo" in result.decision_memo_markdown
    assert Path(written["leaderboard"]).exists()
    assert Path(written["technical_report"]).exists()
    assert Path(written["decision_memo"]).exists()
    assert "experiment_registry" in bundle
    assert "challenger_report" in bundle
    assert "leaderboard_rows" in bundle


def test_run_evidence_review_keeps_inference_ready_run_intact(tmp_path: Path) -> None:
    data_path = _write_dataset(tmp_path / "slice06_inference.csv")
    run_dir = tmp_path / "run_slice06_inference"
    policy = load_policy().policy
    mandate_bundle, context_bundle = _build_foundation(policy)
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

    result = run_evidence_review(
        run_dir=run_dir,
        data_path=str(data_path),
        policy=policy,
        mandate_bundle=mandate_bundle,
        context_bundle=context_bundle,
        intake_bundle={"assumption_log": {"entries": [{"assumption": "autonomous"}]}},
        investigation_bundle=investigation_bundle,
        planning_bundle=execution.planning_bundle.to_dict(),
    )
    write_evidence_bundle(
        run_dir,
        bundle=result.bundle,
        leaderboard_rows=result.leaderboard_rows,
        technical_report_markdown=result.technical_report_markdown,
        decision_memo_markdown=result.decision_memo_markdown,
    )

    inference = run_inference_from_artifacts(
        data_path=str(data_path),
        run_dir=str(run_dir),
    )

    assert inference["status"] == "ok"
    assert inference["prediction_count"] == 15
    assert result.bundle.audit_report.readiness_level in {"strong", "conditional"}
