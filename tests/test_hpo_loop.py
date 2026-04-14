from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from relaytic.modeling import train_surrogate_candidates
from relaytic.modeling.hpo_loop import (
    build_architecture_search_space,
    build_portfolio_search_plan,
    derive_hpo_budget_contract,
)
from relaytic.modeling.training import CandidateMetrics, _fit_hpo_family_candidates


def test_train_surrogate_candidates_materializes_hpo_budget_and_threshold_artifacts(
    tmp_path: Path,
) -> None:
    run_dir = tmp_path / "hpo_binary_run"
    frame = _binary_frame(row_count=180)

    payload = train_surrogate_candidates(
        frame=frame,
        target_column="class_label",
        feature_columns=["feature_a", "feature_b"],
        requested_model_family="logistic_regression",
        threshold_policy="favor_recall",
        run_id="hpo_binary_run",
        output_run_dir=run_dir,
    )

    assert payload["status"] == "ok"
    assert payload["hpo"]["trial_count"] > 0
    assert payload["hpo"]["warm_start_used"] is False
    assert payload["selected_hyperparameters"]["threshold_policy"] == "favor_recall"
    for artifact_name in (
        "hpo_budget_contract.json",
        "architecture_search_space.json",
        "trial_ledger.jsonl",
        "early_stopping_report.json",
        "search_loop_scorecard.json",
        "warm_start_transfer_report.json",
        "threshold_tuning_report.json",
    ):
        assert (run_dir / artifact_name).exists(), artifact_name

    threshold_report = json.loads((run_dir / "threshold_tuning_report.json").read_text(encoding="utf-8"))
    search_scorecard = json.loads((run_dir / "search_loop_scorecard.json").read_text(encoding="utf-8"))
    assert threshold_report["status"] == "ok"
    assert threshold_report["threshold_policy"] == "favor_recall"
    assert threshold_report["selected_threshold"] is not None
    assert len(threshold_report["candidates"]) >= 1
    assert search_scorecard["status"] == "ok"
    assert search_scorecard["total_trials_executed"] > 0


def test_fit_hpo_family_candidates_stops_on_convergence_plateau() -> None:
    trial_plans = [
        {
            "trial_id": f"linear_trial_{index:04d}",
            "family": "linear_ridge",
            "variant_id": f"search_{index:04d}",
            "source": "search_space",
            "hyperparameters": {"ridge": ridge},
        }
        for index, ridge in enumerate((1e-6, 1e-5, 1e-4, 1e-3), start=1)
    ]

    def _build_model(_params: dict[str, float]) -> object:
        return object()

    def _build_candidate(_model: object, trial_plan: dict[str, object]) -> tuple[CandidateMetrics, int]:
        candidate = CandidateMetrics(
            model_family="linear_ridge",
            train_metrics={"mae": 0.25},
            validation_metrics={"mae": 0.25},
            test_metrics={"mae": 0.25},
            notes="plateau test",
            variant_id=str(trial_plan["variant_id"]),
            hyperparameters={"ridge": float(dict(trial_plan["hyperparameters"])["ridge"])},
        )
        return candidate, 24

    records, report, ledger = _fit_hpo_family_candidates(
        family="linear_ridge",
        trial_plans=trial_plans,
        build_model=_build_model,
        build_candidate=_build_candidate,
        task_type="regression",
        selection_metric="mae",
        budget_contract={
            "plateau_patience": 2,
            "min_trials_before_plateau_stop": 3,
        },
        deadline=10**9,
    )

    assert len(records) == 3
    assert len(ledger) == 3
    assert report["executed_trials"] == 3
    assert report["stop_reason"] == "convergence_plateau"


def test_train_surrogate_candidates_warm_starts_from_prior_trial_ledger(tmp_path: Path) -> None:
    run_dir = tmp_path / "warm_start_run"
    frame = _binary_frame(row_count=220)

    first_payload = train_surrogate_candidates(
        frame=frame,
        target_column="class_label",
        feature_columns=["feature_a", "feature_b"],
        requested_model_family="logistic_regression",
        run_id="warm_start_run",
        output_run_dir=run_dir,
    )
    second_payload = train_surrogate_candidates(
        frame=frame,
        target_column="class_label",
        feature_columns=["feature_a", "feature_b"],
        requested_model_family="logistic_regression",
        run_id="warm_start_run",
        output_run_dir=run_dir,
    )

    assert first_payload["status"] == "ok"
    assert second_payload["status"] == "ok"
    assert first_payload["hpo"]["warm_start_used"] is False
    assert second_payload["hpo"]["warm_start_used"] is True

    warm_start_report = json.loads((run_dir / "warm_start_transfer_report.json").read_text(encoding="utf-8"))
    assert warm_start_report["used"] is True
    assert "logistic_regression" in warm_start_report["imported_families"]


def test_hpo_budget_contract_and_search_space_include_first_class_optional_families(
    tmp_path: Path,
) -> None:
    budget_contract = derive_hpo_budget_contract(
        run_dir=tmp_path,
        task_type="multiclass_classification",
        row_count=900,
        requested_family="auto",
        preferred_candidate_order=[
            "catboost_classifier",
            "hist_gradient_boosting_classifier",
            "xgboost_classifier",
            "lightgbm_classifier",
            "extra_trees_classifier",
        ],
        available_families=[
            "catboost_classifier",
            "hist_gradient_boosting_classifier",
            "xgboost_classifier",
            "lightgbm_classifier",
            "extra_trees_classifier",
        ],
        search_budget_profile="benchmark",
    )
    search_space = build_architecture_search_space(
        task_type="multiclass_classification",
        selected_families=[str(item) for item in budget_contract["selected_families"]],
    )

    assert budget_contract["budget_profile"] == "benchmark"
    assert budget_contract["selected_families"][0] == "catboost_classifier"
    assert set(search_space["families"][0].keys()) >= {"family", "parameters", "default_anchor"}
    assert {
        "catboost_classifier",
        "hist_gradient_boosting_classifier",
        "xgboost_classifier",
    }.issubset({str(item["family"]) for item in search_space["families"]})


def test_hpo_budget_profiles_keep_test_budgets_separate_from_benchmark_contracts(tmp_path: Path) -> None:
    benchmark_contract = derive_hpo_budget_contract(
        run_dir=tmp_path / "benchmark_profile",
        task_type="binary_classification",
        row_count=800,
        requested_family="auto",
        preferred_candidate_order=[
            "catboost_classifier",
            "hist_gradient_boosting_classifier",
            "extra_trees_classifier",
            "lightgbm_classifier",
        ],
        available_families=[
            "catboost_classifier",
            "hist_gradient_boosting_classifier",
            "extra_trees_classifier",
            "lightgbm_classifier",
        ],
        search_budget_profile="benchmark",
    )
    test_contract = derive_hpo_budget_contract(
        run_dir=tmp_path / "test_profile",
        task_type="binary_classification",
        row_count=800,
        requested_family="auto",
        preferred_candidate_order=[
            "catboost_classifier",
            "hist_gradient_boosting_classifier",
            "extra_trees_classifier",
            "lightgbm_classifier",
        ],
        available_families=[
            "catboost_classifier",
            "hist_gradient_boosting_classifier",
            "extra_trees_classifier",
            "lightgbm_classifier",
        ],
        search_budget_profile="test",
    )

    assert benchmark_contract["budget_profile"] == "benchmark"
    assert test_contract["budget_profile"] == "test"
    assert benchmark_contract["max_trials"] > test_contract["max_trials"]
    assert benchmark_contract["probe_trials_per_family"] > test_contract["probe_trials_per_family"]
    assert benchmark_contract["selected_families"] != []
    assert len(benchmark_contract["selected_families"]) >= len(test_contract["selected_families"])


def test_portfolio_search_plan_reports_warm_start_influence_without_hiding_stage_evidence(tmp_path: Path) -> None:
    budget_contract = derive_hpo_budget_contract(
        run_dir=tmp_path,
        task_type="binary_classification",
        row_count=600,
        requested_family="auto",
        preferred_candidate_order=[
            "hist_gradient_boosting_classifier",
            "extra_trees_classifier",
            "logistic_regression",
        ],
        available_families=[
            "hist_gradient_boosting_classifier",
            "extra_trees_classifier",
            "logistic_regression",
        ],
        search_budget_profile="operator",
    )
    search_space = build_architecture_search_space(
        task_type="binary_classification",
        selected_families=[str(item) for item in budget_contract["selected_families"]],
    )
    warm_start_state = {
        "best_priors": {
            "extra_trees_classifier": {
                "hyperparameters": {"n_estimators": 20, "max_depth": 5, "min_leaf": 3},
                "validation_metrics": {"pr_auc": 0.82, "f1": 0.74},
            }
        }
    }

    portfolio_plan = build_portfolio_search_plan(
        budget_contract=budget_contract,
        architecture_search_space=search_space,
        warm_start_state=warm_start_state,
    )

    assert portfolio_plan["status"] == "ok"
    assert "extra_trees_classifier" in portfolio_plan["warm_start_influenced_families"]
    assert len(portfolio_plan["families"]) >= 2
    assert len(portfolio_plan["racing_families"]) >= 1
    assert len(portfolio_plan["finalists"]) >= 1


def _binary_frame(*, row_count: int) -> pd.DataFrame:
    rows: list[dict[str, float | int]] = []
    for idx in range(row_count):
        feature_a = idx / max(1, row_count - 1)
        feature_b = 1 if idx % 5 in {0, 1} else 0
        label = 1 if (feature_a > 0.58 or feature_b == 1) else 0
        rows.append(
            {
                "feature_a": round(feature_a, 5),
                "feature_b": feature_b,
                "class_label": label,
            }
        )
    return pd.DataFrame(rows)
