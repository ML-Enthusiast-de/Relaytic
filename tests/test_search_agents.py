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


def test_search_review_materializes_staged_family_race_and_pruning_reasons(tmp_path: Path) -> None:
    run_dir = tmp_path / "search_staged_family_race"
    workspace_dir = default_workspace_dir(run_dir=run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    workspace_dir.mkdir(parents=True, exist_ok=True)

    _write_json(
        run_dir / "run_summary.json",
        {
            "run_id": "run_staged_family_race",
            "benchmark": {"incumbent_present": True, "beat_target_state": "near_parity"},
            "decision": {
                "task_type": "binary_classification",
                "selected_route_id": "mixed_route",
                "selected_route_title": "Mixed route",
                "selected_model_family": "hist_gradient_boosting_classifier",
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
            "unresolved_items": [{"id": "u1"}],
            "evidence_strength": {"overall_strength": "mixed"},
        },
    )
    _write_json(run_dir / "confidence_posture.json", {"overall_confidence": "medium", "review_need": "optional"})
    _write_json(
        run_dir / "plan.json",
        {
            "builder_handoff": {
                "preferred_candidate_order": [
                    "catboost_classifier",
                    "hist_gradient_boosting_classifier",
                    "extra_trees_classifier",
                    "logistic_regression",
                ]
            }
        },
    )
    _write_json(run_dir / "budget_contract.json", {"max_trials": 48})
    _write_json(run_dir / "budget_consumption_report.json", {"estimated_trials_used": 6})
    _write_json(workspace_dir / "workspace_state.json", {"workspace_id": "workspace_stage", "status": "ok"})
    _write_json(workspace_dir / "next_run_plan.json", {"recommended_direction": "same_data", "status": "ok"})

    result = run_search_review(run_dir=run_dir, policy={"search": {"budget_profile": "benchmark"}})
    bundle = result.bundle.to_dict()

    assert bundle["search_budget_envelope"]["controls"]["budget_profile"] == "benchmark"
    assert len(bundle["probe_stage_report"]["candidate_families"]) >= 3
    assert len(bundle["family_race_report"]["racing_families"]) >= 2
    assert len(bundle["finalist_search_plan"]["finalists"]) >= 1
    assert bundle["multi_fidelity_pruning_report"]["status"] == "ok"
    assert any(
        str(item.get("prune_reason", "")).strip()
        for item in bundle["multi_fidelity_pruning_report"]["pruned_families"]
    )


def test_search_review_low_budget_profile_reports_skipped_deeper_work(tmp_path: Path) -> None:
    run_dir = tmp_path / "search_low_budget"
    workspace_dir = default_workspace_dir(run_dir=run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    workspace_dir.mkdir(parents=True, exist_ok=True)

    _write_json(
        run_dir / "run_summary.json",
        {
            "run_id": "run_low_budget",
            "benchmark": {"incumbent_present": True, "beat_target_state": "monitor"},
            "decision": {
                "task_type": "binary_classification",
                "selected_route_id": "lean_route",
                "selected_route_title": "Lean route",
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
            "unresolved_items": [{"id": "u1"}],
            "evidence_strength": {"overall_strength": "mixed"},
        },
    )
    _write_json(run_dir / "confidence_posture.json", {"overall_confidence": "low", "review_need": "required"})
    _write_json(
        run_dir / "plan.json",
        {
            "builder_handoff": {
                "preferred_candidate_order": [
                    "logistic_regression",
                    "hist_gradient_boosting_classifier",
                    "extra_trees_classifier",
                ]
            }
        },
    )
    _write_json(run_dir / "budget_contract.json", {"max_trials": 10})
    _write_json(run_dir / "budget_consumption_report.json", {"estimated_trials_used": 1})
    _write_json(workspace_dir / "workspace_state.json", {"workspace_id": "workspace_low_budget", "status": "ok"})
    _write_json(workspace_dir / "next_run_plan.json", {"recommended_direction": "same_data", "status": "ok"})

    result = run_search_review(run_dir=run_dir, policy={"search": {"budget_profile": "low_budget"}})
    bundle = result.bundle.to_dict()

    assert bundle["search_budget_envelope"]["controls"]["budget_profile"] == "low_budget"
    assert bundle["portfolio_search_scorecard"]["skipped_deeper_work_count"] >= 1
    assert bundle["search_stop_reason"]["reason_kind"] in {"budget", "plateau", "continue_search"}


def _write_json(path: Path, payload: dict[str, object]) -> None:
    write_json(path, payload, indent=2, ensure_ascii=False, sort_keys=True)
