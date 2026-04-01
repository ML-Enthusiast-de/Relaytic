from __future__ import annotations

from pathlib import Path

from relaytic.core.json_utils import write_json
from relaytic.search import run_search_review
from relaytic.workspace import default_workspace_dir


def test_search_review_stops_search_when_additional_data_is_clearly_more_valuable(tmp_path: Path) -> None:
    run_dir = tmp_path / "search_add_data"
    workspace_dir = default_workspace_dir(run_dir=run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    workspace_dir.mkdir(parents=True, exist_ok=True)

    _write_json(
        run_dir / "run_summary.json",
        {
            "run_id": "run_add_data",
            "benchmark": {"incumbent_present": False, "beat_target_state": None},
            "decision": {
                "task_type": "binary_classification",
                "selected_route_id": "tabular_route",
                "selected_route_title": "Tabular route",
                "selected_model_family": "random_forest",
            },
            "decision_lab": {
                "selected_next_action": "additional_local_data",
                "recommended_source_id": "adjacent_source",
            },
            "evals": {"status": "ok", "failed_count": 0, "protocol_status": "ok"},
        },
    )
    _write_json(
        run_dir / "result_contract.json",
        {
            "status": "ok",
            "recommended_next_move": {"direction": "add_data", "action": "collect_more_data"},
            "unresolved_items": [],
            "evidence_strength": {"overall_strength": "strong"},
        },
    )
    _write_json(
        run_dir / "confidence_posture.json",
        {"overall_confidence": "high", "review_need": "optional"},
    )
    _write_json(
        workspace_dir / "workspace_state.json",
        {"workspace_id": "workspace_add_data", "status": "ok"},
    )
    _write_json(
        workspace_dir / "next_run_plan.json",
        {"recommended_direction": "add_data", "status": "ok"},
    )

    result = run_search_review(run_dir=run_dir, policy={})
    bundle = result.bundle.to_dict()
    search_value = bundle["search_value_report"]
    plan = bundle["search_controller_plan"]

    assert search_value["recommended_direction"] == "add_data"
    assert search_value["stop_search_explicit"] is True
    assert plan["recommended_action"] == "stop_search"
    assert plan["planned_trial_count"] == 0


def test_search_review_widens_portfolio_under_real_benchmark_pressure(tmp_path: Path) -> None:
    run_dir = tmp_path / "search_benchmark_pressure"
    workspace_dir = default_workspace_dir(run_dir=run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    workspace_dir.mkdir(parents=True, exist_ok=True)

    _write_json(
        run_dir / "run_summary.json",
        {
            "run_id": "run_benchmark_pressure",
            "benchmark": {
                "incumbent_present": True,
                "incumbent_stronger": True,
                "beat_target_state": "unmet",
            },
            "decision": {
                "task_type": "binary_classification",
                "selected_route_id": "tabular_route",
                "selected_route_title": "Tabular route",
                "selected_model_family": "logistic_regression",
            },
            "decision_lab": {"selected_next_action": "search_more"},
            "evals": {"status": "ok", "failed_count": 0, "protocol_status": "ok"},
        },
    )
    _write_json(
        run_dir / "result_contract.json",
        {
            "status": "ok",
            "recommended_next_move": {"direction": "same_data", "action": "search_more"},
            "unresolved_items": [{"id": "u1"}, {"id": "u2"}],
            "evidence_strength": {"overall_strength": "mixed"},
        },
    )
    _write_json(
        run_dir / "confidence_posture.json",
        {"overall_confidence": "low", "review_need": "required"},
    )
    _write_json(
        run_dir / "alternatives.json",
        {
            "candidate_routes": [
                {"route_id": "gbm_route", "title": "Gradient boosting route", "model_family": "gradient_boosting"},
            ]
        },
    )
    _write_json(
        run_dir / "beat_target_contract.json",
        {"contract_state": "unmet"},
    )
    _write_json(
        run_dir / "budget_contract.json",
        {"max_trials": 64},
    )
    _write_json(
        run_dir / "budget_consumption_report.json",
        {"estimated_trials_used": 4},
    )
    _write_json(
        workspace_dir / "workspace_state.json",
        {"workspace_id": "workspace_pressure", "status": "ok"},
    )
    _write_json(
        workspace_dir / "next_run_plan.json",
        {"recommended_direction": "same_data", "status": "ok"},
    )

    result = run_search_review(run_dir=run_dir, policy={})
    bundle = result.bundle.to_dict()
    plan = bundle["search_controller_plan"]
    portfolio = bundle["portfolio_search_trace"]
    value = bundle["search_value_report"]

    assert value["beat_target_pressure"] == "high"
    assert plan["recommended_action"] == "expand_challenger_portfolio"
    assert portfolio["widened_branch_count"] >= 2
    assert plan["planned_trial_count"] > 0
    assert plan["selected_hpo_depth"] in {"medium", "deep"}


def _write_json(path: Path, payload: dict[str, object]) -> None:
    write_json(path, payload, indent=2, ensure_ascii=False, sort_keys=True)
