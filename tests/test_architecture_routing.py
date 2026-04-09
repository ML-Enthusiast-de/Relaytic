from __future__ import annotations

from relaytic.analytics import build_architecture_routing_artifacts


def test_architecture_registry_includes_expanded_families_for_multiclass() -> None:
    artifacts = build_architecture_routing_artifacts(
        investigation_bundle={
            "dataset_profile": {
                "row_count": 900,
                "column_count": 9,
                "data_mode": "steady_state",
                "numeric_columns": ["length", "width", "density", "roundness"],
                "categorical_columns": [],
                "missingness_by_column": {"length": 0.0, "width": 0.0},
            },
            "optimization_profile": {},
        },
        planning_bundle={
            "plan": {
                "task_profile": {
                    "task_type": "multiclass_classification",
                    "data_mode": "steady_state",
                    "row_count": 900,
                    "class_count": 7,
                    "minority_class_fraction": 0.12,
                },
                "feature_columns": ["length", "width", "density", "roundness"],
                "target_column": "bean_class",
            }
        },
    )

    families = {
        row["family_id"]
        for row in artifacts["architecture_registry"]["families"]
    }
    assert "hist_gradient_boosting_classifier" in families
    assert "extra_trees_classifier" in families
    assert "catboost_classifier" in families
    assert "sequence_lstm_candidate" in families
    assert artifacts["architecture_router_report"]["recommended_primary_family"] in {
        "hist_gradient_boosting_classifier",
        "extra_trees_classifier",
        "catboost_classifier",
        "xgboost_classifier",
        "lightgbm_classifier",
        "tabpfn_classifier",
    }


def test_architecture_router_rejects_sequence_models_for_static_tables() -> None:
    artifacts = build_architecture_routing_artifacts(
        investigation_bundle={
            "dataset_profile": {
                "row_count": 400,
                "column_count": 12,
                "data_mode": "steady_state",
                "numeric_columns": ["f1", "f2", "f3"],
                "categorical_columns": ["segment"],
            },
            "optimization_profile": {},
        },
        planning_bundle={
            "plan": {
                "task_profile": {
                    "task_type": "binary_classification",
                    "data_mode": "steady_state",
                    "row_count": 400,
                    "class_count": 2,
                    "minority_class_fraction": 0.18,
                },
                "feature_columns": ["f1", "f2", "f3", "segment"],
                "target_column": "label",
            }
        },
    )

    report = artifacts["architecture_router_report"]
    assert report["sequence_live_allowed"] is False
    assert report["sequence_shadow_ready"] is False
    assert "ordered temporal structure" in report["sequence_rejection_reason"]
    assert all(
        "sequence" not in family
        for family in report["candidate_order"]
    )


def test_architecture_router_marks_time_series_sequence_as_shadow_only() -> None:
    artifacts = build_architecture_routing_artifacts(
        investigation_bundle={
            "dataset_profile": {
                "row_count": 640,
                "column_count": 7,
                "data_mode": "time_series",
                "timestamp_column": "ts",
                "numeric_columns": ["sensor_a", "sensor_b", "sensor_c"],
                "categorical_columns": [],
            },
            "optimization_profile": {},
        },
        planning_bundle={
            "plan": {
                "task_profile": {
                    "task_type": "regression",
                    "data_mode": "time_series",
                    "row_count": 640,
                },
                "feature_columns": ["sensor_a", "sensor_b", "sensor_c"],
                "target_column": "target",
                "timestamp_column": "ts",
            }
        },
    )

    report = artifacts["architecture_router_report"]
    ablation = artifacts["architecture_ablation_report"]
    assert report["sequence_live_allowed"] is False
    assert report["sequence_shadow_ready"] is True
    assert "sequence_lstm_candidate" in ablation["shadow_sequence_candidates"]
    assert report["recommended_primary_family"] in {
        "lagged_linear",
        "lagged_tree_ensemble",
        "hist_gradient_boosting_ensemble",
        "extra_trees_ensemble",
    }


def test_architecture_router_respects_memory_bias_for_binary_tasks() -> None:
    artifacts = build_architecture_routing_artifacts(
        investigation_bundle={
            "dataset_profile": {
                "row_count": 240,
                "column_count": 5,
                "data_mode": "steady_state",
                "numeric_columns": ["a", "b", "c"],
                "categorical_columns": [],
            },
            "optimization_profile": {},
        },
        planning_bundle={
            "plan": {
                "task_profile": {
                    "task_type": "binary_classification",
                    "data_mode": "steady_state",
                    "row_count": 240,
                    "class_count": 2,
                    "minority_class_fraction": 0.22,
                },
                "feature_columns": ["a", "b", "c"],
                "target_column": "label",
            }
        },
        route_prior_context={
            "status": "memory_influenced",
            "baseline_candidate_order": [
                "logistic_regression",
                "bagged_tree_classifier",
                "boosted_tree_classifier",
            ],
            "adjusted_candidate_order": [
                "bagged_tree_classifier",
                "logistic_regression",
                "boosted_tree_classifier",
            ],
            "family_bias": [
                {"model_family": "bagged_tree_classifier", "score": 0.40},
            ],
        },
    )

    report = artifacts["architecture_router_report"]
    assert report["workspace_analog_influence"] is True
    assert report["memory_adjusted_candidate_order"][0] == "bagged_tree_classifier"
    assert report["candidate_order"][0] == "bagged_tree_classifier"


def test_architecture_router_keeps_multiclass_task_fit_ahead_of_memory_bias() -> None:
    artifacts = build_architecture_routing_artifacts(
        investigation_bundle={
            "dataset_profile": {
                "row_count": 240,
                "column_count": 4,
                "data_mode": "steady_state",
                "numeric_columns": ["length", "width", "color_score"],
                "categorical_columns": [],
            },
            "optimization_profile": {},
        },
        planning_bundle={
            "plan": {
                "task_profile": {
                    "task_type": "multiclass_classification",
                    "data_mode": "steady_state",
                    "row_count": 240,
                    "class_count": 3,
                    "minority_class_fraction": 0.33,
                },
                "feature_columns": ["length", "width", "color_score"],
                "target_column": "bean_class",
            }
        },
        route_prior_context={
            "status": "memory_influenced",
            "baseline_candidate_order": [
                "logistic_regression",
                "bagged_tree_classifier",
                "boosted_tree_classifier",
                "hist_gradient_boosting_classifier",
                "extra_trees_classifier",
            ],
            "adjusted_candidate_order": [
                "boosted_tree_classifier",
                "logistic_regression",
                "bagged_tree_classifier",
                "hist_gradient_boosting_classifier",
                "extra_trees_classifier",
            ],
            "family_bias": [
                {"model_family": "boosted_tree_classifier", "score": 1.2},
            ],
        },
    )

    report = artifacts["architecture_router_report"]
    assert report["workspace_analog_influence"] is True
    assert report["memory_adjusted_candidate_order"][0] == "boosted_tree_classifier"
    assert report["candidate_order"][0] in {
        "hist_gradient_boosting_classifier",
        "extra_trees_classifier",
        "catboost_classifier",
        "xgboost_classifier",
        "lightgbm_classifier",
        "tabpfn_classifier",
    }
