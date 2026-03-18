import csv
from pathlib import Path

from relaytic.context import (
    build_context_controls_from_policy,
    default_data_origin,
    default_domain_brief,
    default_task_brief,
)
from relaytic.intake import run_intake_interpretation
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
        ).to_dict(),
        "task_brief": default_task_brief(
            context_controls,
            success_criteria=["Maximize useful early warning value."],
            failure_costs=["Missed failures lead to scrap and avoidable downtime."],
        ).to_dict(),
    }
    return mandate_bundle, context_bundle


def _build_intake_backed_bundles(policy: dict, *, data_path: Path) -> tuple[dict, dict]:
    mandate_bundle, context_bundle = _build_foundation(policy)
    resolution = run_intake_interpretation(
        message=(
            "Predict failure_flag. Do not use future_failure_flag or post_inspection_flag. "
            "Find out the best local-first route and optimize for useful early warning."
        ),
        actor_type="user",
        actor_name="operator_a",
        channel="cli",
        policy=policy,
        mandate_bundle=mandate_bundle,
        context_bundle=context_bundle,
        data_path=str(data_path),
    )
    return (
        {
            "lab_mandate": resolution.lab_mandate.to_dict(),
            "work_preferences": resolution.work_preferences.to_dict(),
            "run_brief": resolution.run_brief.to_dict(),
        },
        {
            "data_origin": resolution.data_origin.to_dict(),
            "domain_brief": resolution.domain_brief.to_dict(),
            "task_brief": resolution.task_brief.to_dict(),
        },
    )


def test_run_planning_creates_real_builder_handoff_from_investigation(tmp_path: Path) -> None:
    data_path = _write_dataset(tmp_path / "slice05.csv")
    policy = load_policy().policy
    mandate_bundle, context_bundle = _build_intake_backed_bundles(policy, data_path=data_path)
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

    assert planning_bundle.plan.selected_route_id == "temporal_calibrated_classifier_route"
    assert planning_bundle.plan.target_column == "failure_flag"
    assert planning_bundle.plan.feature_columns == ["sensor_a", "sensor_b"]
    assert planning_bundle.plan.builder_handoff["selection_metric"] == "log_loss"
    assert planning_bundle.plan.builder_handoff["preferred_candidate_order"][0] == "lagged_logistic_regression"
    assert {item["column"] for item in planning_bundle.plan.builder_handoff["feature_risk_flags"]} == {"sensor_a", "sensor_b"}
    assert any(item["column"] == "future_failure_flag" for item in planning_bundle.plan.feature_drop_reasons)
    assert any(item["experiment_id"] == "execute_selected_route" for item in planning_bundle.experiment_priority_report.prioritized_experiments)
    assert planning_bundle.marginal_value_of_next_experiment.recommended_experiment_id == "execute_selected_route"


def test_execute_planned_route_trains_into_same_run_dir_and_is_inference_ready(tmp_path: Path) -> None:
    data_path = _write_dataset(tmp_path / "slice05_execute.csv")
    run_dir = tmp_path / "run_slice05_execute"
    policy = load_policy().policy
    mandate_bundle, context_bundle = _build_intake_backed_bundles(policy, data_path=data_path)
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

    assert execution.training_result["status"] == "ok"
    assert execution.training_result["run_dir"] == str(run_dir)
    assert (run_dir / "model_params.json").exists()
    assert Path(execution.training_result["model_state_path"]).exists()
    assert execution.planning_bundle.plan.execution_summary is not None
    assert execution.planning_bundle.plan.execution_summary["selected_model_family"] == execution.training_result["selected_model_family"]
    assert any(
        item["experiment_id"] == "execute_selected_route" and item["status"] == "completed"
        for item in execution.planning_bundle.experiment_priority_report.prioritized_experiments
    )

    inference = run_inference_from_artifacts(
        data_path=str(data_path),
        run_dir=str(run_dir),
    )

    assert inference["status"] == "ok"
    assert inference["prediction_count"] == 15
    assert inference["model_name"] == execution.training_result["selected_model_family"]
