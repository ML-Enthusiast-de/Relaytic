from pathlib import Path

import warnings

import pandas as pd

from relaytic.orchestration.default_tools import build_default_registry
def test_train_surrogate_candidates_tool_runs_split_safe_linear_and_tree(
    monkeypatch, tmp_path: Path
) -> None:
    monkeypatch.chdir(tmp_path)
    csv_path = tmp_path / "train_compare.csv"
    rows = ["time,x1,x2,y"]
    for idx in range(60):
        x1 = idx / 10.0
        x2 = 1.0 if idx % 2 == 0 else 0.0
        y = 1.8 * x1 + 0.6 * x2 + 0.2
        rows.append(f"{idx},{x1:.4f},{x2:.4f},{y:.4f}")
    csv_path.write_text("\n".join(rows), encoding="utf-8")

    registry = build_default_registry()
    result = registry.execute(
        "train_surrogate_candidates",
        {
            "data_path": str(csv_path),
            "target_column": "y",
            "feature_columns": ["x1", "x2"],
            "requested_model_family": "auto",
            "timestamp_column": "time",
            "run_id": "compare_run",
        },
    )
    assert result.status == "ok"
    payload = result.output
    assert payload["status"] == "ok"
    assert payload["split"]["strategy"]
    assert payload["split"]["train_size"] > payload["split"]["validation_size"] >= 2
    assert payload["normalization"]["enabled"] is True
    assert payload["normalization"]["normalizer_path"]
    families = [row["model_family"] for row in payload["comparison"]]
    assert "linear_ridge" in families
    assert "lagged_linear" in families
    assert "bagged_tree_ensemble" in families
    assert "boosted_tree_ensemble" in families
    assert "hist_gradient_boosting_ensemble" in families
    assert "extra_trees_ensemble" in families
    assert payload["selected_model_family"] in {
        "linear_ridge",
        "lagged_linear",
        "bagged_tree_ensemble",
        "boosted_tree_ensemble",
        "hist_gradient_boosting_ensemble",
        "extra_trees_ensemble",
        "catboost_ensemble",
        "xgboost_ensemble",
        "lightgbm_ensemble",
    }
    assert isinstance(payload["selected_hyperparameters"], dict)
    assert payload["selected_hyperparameters"]
    assert payload["checkpoint_id"]
    assert Path(payload["run_dir"]).is_dir()
    assert Path(payload["model_params_path"]).is_file()


def test_train_surrogate_candidates_tool_honors_requested_tree_model(
    monkeypatch, tmp_path: Path
) -> None:
    monkeypatch.chdir(tmp_path)
    csv_path = tmp_path / "train_tree.csv"
    rows = ["x1,x2,y"]
    for idx in range(80):
        x1 = -1.0 + (2.0 * idx / 79.0)
        x2 = 1.0 if idx % 3 == 0 else -1.0
        y = 2.5 if (x1 > 0.2 and x2 > 0) else -1.2
        rows.append(f"{x1:.5f},{x2:.5f},{y:.5f}")
    csv_path.write_text("\n".join(rows), encoding="utf-8")

    registry = build_default_registry()
    result = registry.execute(
        "train_surrogate_candidates",
        {
            "data_path": str(csv_path),
            "target_column": "y",
            "feature_columns": ["x1", "x2"],
            "requested_model_family": "tree_ensemble_candidate",
            "run_id": "tree_run",
        },
    )
    assert result.status == "ok"
    payload = result.output
    assert payload["requested_model_family"] == "bagged_tree_ensemble"
    assert payload["selected_model_family"] == "bagged_tree_ensemble"
    assert payload["selected_metrics"]["test"]["r2"] > 0.0


def test_train_surrogate_candidates_tool_supports_lagged_linear_time_series(
    monkeypatch, tmp_path: Path
) -> None:
    monkeypatch.chdir(tmp_path)
    csv_path = tmp_path / "train_lagged.csv"
    rows = ["time,x,y"]
    base = [0.7, -1.4, 1.1, 0.3, -0.9, 1.6, -0.2, 0.8]
    values = [base[idx % len(base)] for idx in range(120)]
    for idx in range(120):
        x = values[idx]
        y = 0.0 if idx < 3 else (1.4 * values[idx - 3] - 0.2)
        rows.append(f"{idx},{x:.5f},{y:.5f}")
    csv_path.write_text("\n".join(rows), encoding="utf-8")

    registry = build_default_registry()
    result = registry.execute(
        "train_surrogate_candidates",
        {
            "data_path": str(csv_path),
            "target_column": "y",
            "feature_columns": ["x"],
            "requested_model_family": "lagged_linear",
            "timestamp_column": "time",
            "lag_horizon_samples": 3,
            "run_id": "lagged_run",
        },
    )
    assert result.status == "ok"
    payload = result.output
    families = [row["model_family"] for row in payload["comparison"]]
    assert "lagged_linear" in families
    assert payload["requested_model_family"] == "lagged_linear"
    assert payload["selected_model_family"] == "lagged_linear"
    assert payload["lag_horizon_samples"] == 3
    assert payload["rows_used"] > 0
    assert payload["selected_metrics"]["test"]["r2"] > 0.8


def test_train_surrogate_candidates_lagged_path_does_not_emit_fragmentation_warning(
    monkeypatch, tmp_path: Path
) -> None:
    monkeypatch.chdir(tmp_path)
    csv_path = tmp_path / "train_lagged_warning_guard.csv"
    rows = ["time,x,y"]
    base = [0.7, -1.4, 1.1, 0.3, -0.9, 1.6, -0.2, 0.8]
    values = [base[idx % len(base)] for idx in range(120)]
    for idx in range(120):
        x = values[idx]
        y = 0.0 if idx < 3 else (1.4 * values[idx - 3] - 0.2)
        rows.append(f"{idx},{x:.5f},{y:.5f}")
    csv_path.write_text("\n".join(rows), encoding="utf-8")

    registry = build_default_registry()
    with warnings.catch_warnings():
        warnings.filterwarnings(
            "error",
            message=r".*DataFrame is highly fragmented.*",
            category=pd.errors.PerformanceWarning,
        )
        result = registry.execute(
            "train_surrogate_candidates",
            {
                "data_path": str(csv_path),
                "target_column": "y",
                "feature_columns": ["x"],
                "requested_model_family": "lagged_linear",
                "timestamp_column": "time",
                "lag_horizon_samples": 3,
                "run_id": "lagged_warning_guard_run",
            },
        )

    assert result.status == "ok"
    assert result.output["status"] == "ok"


def test_train_surrogate_candidates_auto_can_select_temporal_lagged_model_when_best(
    monkeypatch, tmp_path: Path
) -> None:
    monkeypatch.chdir(tmp_path)
    csv_path = tmp_path / "train_auto_lagged.csv"
    rows = ["time,x,y"]
    base = [1.2, -0.6, 0.9, -1.1, 0.4, 1.8, -0.3]
    values = [base[idx % len(base)] for idx in range(140)]
    for idx in range(140):
        x = values[idx]
        y = 0.5 if idx < 2 else (2.0 * values[idx - 2] + 0.1)
        rows.append(f"{idx},{x:.5f},{y:.5f}")
    csv_path.write_text("\n".join(rows), encoding="utf-8")

    registry = build_default_registry()
    result = registry.execute(
        "train_surrogate_candidates",
        {
            "data_path": str(csv_path),
            "target_column": "y",
            "feature_columns": ["x"],
            "requested_model_family": "auto",
            "timestamp_column": "time",
            "lag_horizon_samples": 2,
            "run_id": "auto_lagged_run",
        },
    )
    assert result.status == "ok"
    payload = result.output
    assert payload["best_validation_model_family"] in {
        "lagged_linear",
        "lagged_tree_ensemble",
        "boosted_tree_ensemble",
    }
    assert payload["selected_model_family"] in {
        "lagged_linear",
        "lagged_tree_ensemble",
        "boosted_tree_ensemble",
    }
    assert payload["selected_metrics"]["test"]["r2"] > 0.85


def test_train_surrogate_candidates_tool_supports_lagged_tree_ensemble(
    monkeypatch, tmp_path: Path
) -> None:
    monkeypatch.chdir(tmp_path)
    csv_path = tmp_path / "train_lagged_tree.csv"
    rows = ["time,x,y"]
    base = [0.2, 0.9, -0.4, 1.4, -0.8, 0.6, 1.1, -0.2]
    values = [base[idx % len(base)] for idx in range(150)]
    for idx in range(150):
        x = values[idx]
        if idx < 2:
            y = -1.0
        else:
            y = 2.0 if values[idx - 2] > 0.5 else -1.5
        rows.append(f"{idx},{x:.5f},{y:.5f}")
    csv_path.write_text("\n".join(rows), encoding="utf-8")

    registry = build_default_registry()
    result = registry.execute(
        "train_surrogate_candidates",
        {
            "data_path": str(csv_path),
            "target_column": "y",
            "feature_columns": ["x"],
            "requested_model_family": "lagged_tree_ensemble",
            "timestamp_column": "time",
            "lag_horizon_samples": 2,
            "run_id": "lagged_tree_run",
        },
    )
    assert result.status == "ok"
    payload = result.output
    families = [row["model_family"] for row in payload["comparison"]]
    assert "lagged_tree_ensemble" in families
    assert payload["requested_model_family"] == "lagged_tree_ensemble"
    assert payload["selected_model_family"] == "lagged_tree_ensemble"
    assert payload["selected_metrics"]["test"]["r2"] > 0.75


def test_train_surrogate_candidates_supports_binary_classification_targets(
    monkeypatch, tmp_path: Path
) -> None:
    monkeypatch.chdir(tmp_path)
    csv_path = tmp_path / "classification.csv"
    rows = ["feature_a,feature_b,class_label"]
    for idx in range(80):
        a = idx / 79.0
        b = 1 if idx % 3 == 0 else 0
        label = 1 if (a > 0.55 or b == 1) else 0
        rows.append(f"{a:.5f},{b},{label}")
    csv_path.write_text("\n".join(rows), encoding="utf-8")

    registry = build_default_registry()
    result = registry.execute(
        "train_surrogate_candidates",
        {
            "data_path": str(csv_path),
            "target_column": "class_label",
            "feature_columns": ["feature_a", "feature_b"],
            "requested_model_family": "auto",
            "run_id": "classification_run",
        },
    )
    assert result.status == "ok"
    payload = result.output
    assert payload["task_profile"]["task_type"] == "binary_classification"
    assert payload["split"]["strategy"] == "stratified_deterministic_modulo_70_15_15"
    families = [row["model_family"] for row in payload["comparison"]]
    assert "logistic_regression" in families
    assert "bagged_tree_classifier" in families
    assert "boosted_tree_classifier" in families
    assert "hist_gradient_boosting_classifier" in families
    assert "extra_trees_classifier" in families
    assert payload["selected_model_family"] in {
        "logistic_regression",
        "bagged_tree_classifier",
        "boosted_tree_classifier",
        "hist_gradient_boosting_classifier",
        "extra_trees_classifier",
        "catboost_classifier",
        "xgboost_classifier",
        "lightgbm_classifier",
        "tabpfn_classifier",
    }
    assert payload["selected_metrics"]["test"]["f1"] >= 0.70
    assert "r2" not in payload["selected_metrics"]["test"]
    assert payload["selected_hyperparameters"]["threshold_policy"] == "auto"


def test_train_surrogate_candidates_supports_fraud_detection_targets(
    monkeypatch, tmp_path: Path
) -> None:
    monkeypatch.chdir(tmp_path)
    csv_path = tmp_path / "fraud.csv"
    rows = ["amount_norm,device_risk,velocity_score,fraud_flag"]
    for idx in range(160):
        fraud = 1 if idx % 10 == 0 else 0
        if fraud == 1:
            amount = 0.88 + ((idx % 3) * 0.03)
            device = 0.92
            velocity = 0.90
        else:
            amount = 0.05 + ((idx % 8) * 0.07)
            device = 0.10 + ((idx % 5) * 0.08)
            velocity = 0.08 + ((idx % 6) * 0.06)
        rows.append(f"{amount:.5f},{device:.5f},{velocity:.5f},{fraud}")
    csv_path.write_text("\n".join(rows), encoding="utf-8")

    registry = build_default_registry()
    result = registry.execute(
        "train_surrogate_candidates",
        {
            "data_path": str(csv_path),
            "target_column": "fraud_flag",
            "feature_columns": ["amount_norm", "device_risk", "velocity_score"],
            "requested_model_family": "auto",
            "run_id": "fraud_run",
        },
    )
    assert result.status == "ok"
    payload = result.output
    assert payload["task_profile"]["task_type"] == "fraud_detection"
    assert payload["split"]["strategy"] == "stratified_deterministic_modulo_70_15_15"
    assert payload["selected_model_family"] in {
        "logistic_regression",
        "bagged_tree_classifier",
        "boosted_tree_classifier",
        "hist_gradient_boosting_classifier",
        "extra_trees_classifier",
        "catboost_classifier",
        "xgboost_classifier",
        "lightgbm_classifier",
        "tabpfn_classifier",
    }
    test_metrics = payload["selected_metrics"]["test"]
    assert test_metrics["recall"] >= 0.70
    assert test_metrics["pr_auc"] >= 0.35


def test_train_surrogate_candidates_supports_lagged_binary_classification(
    monkeypatch, tmp_path: Path
) -> None:
    monkeypatch.chdir(tmp_path)
    csv_path = tmp_path / "classification_lagged.csv"
    rows = ["time,feature_x,class_label"]
    base = [0.9, 0.2, 0.8, 0.1, 0.7, 0.3, 0.85, 0.15]
    values = [base[idx % len(base)] for idx in range(120)]
    for idx in range(120):
        x = values[idx]
        label = 0 if idx < 2 else int(values[idx - 2] > 0.5)
        rows.append(f"{idx},{x:.5f},{label}")
    csv_path.write_text("\n".join(rows), encoding="utf-8")

    registry = build_default_registry()
    result = registry.execute(
        "train_surrogate_candidates",
        {
            "data_path": str(csv_path),
            "target_column": "class_label",
            "feature_columns": ["feature_x"],
            "requested_model_family": "lagged_logistic_regression",
            "timestamp_column": "time",
            "lag_horizon_samples": 2,
            "run_id": "classification_lagged_run",
        },
    )
    assert result.status == "ok"
    payload = result.output
    assert payload["task_profile"]["task_type"] == "binary_classification"
    assert payload["requested_model_family"] == "lagged_logistic_regression"
    assert payload["selected_model_family"] == "lagged_logistic_regression"
    assert payload["lag_horizon_samples"] == 2
    assert payload["selected_hyperparameters"]["threshold_policy"] == "auto"
    assert payload["selected_hyperparameters"]["lag_horizon_samples"] == 2
    assert payload["selected_metrics"]["test"]["f1"] >= 0.75


def test_train_surrogate_candidates_honors_binary_threshold_policy(
    monkeypatch, tmp_path: Path
) -> None:
    monkeypatch.chdir(tmp_path)
    csv_path = tmp_path / "classification_threshold.csv"
    rows = ["feature_a,feature_b,class_label"]
    for idx in range(100):
        a = idx / 99.0
        b = 1 if idx % 4 == 0 else 0
        label = 1 if (a > 0.62 or b == 1) else 0
        rows.append(f"{a:.5f},{b},{label}")
    csv_path.write_text("\n".join(rows), encoding="utf-8")

    registry = build_default_registry()
    result = registry.execute(
        "train_surrogate_candidates",
        {
            "data_path": str(csv_path),
            "target_column": "class_label",
            "feature_columns": ["feature_a", "feature_b"],
            "requested_model_family": "logistic_regression",
            "threshold_policy": "favor_recall",
            "run_id": "classification_threshold_run",
        },
    )
    assert result.status == "ok"
    payload = result.output
    assert payload["selected_model_family"] == "logistic_regression"
    assert payload["selected_hyperparameters"]["threshold_policy"] == "favor_recall"
    assert 0.0 < payload["selected_hyperparameters"]["decision_threshold"] < 1.0


def test_train_surrogate_candidates_supports_boosted_tree_regression_and_professional_analysis(
    monkeypatch, tmp_path: Path
) -> None:
    monkeypatch.chdir(tmp_path)
    csv_path = tmp_path / "boosted_regression.csv"
    rows = ["x1,x2,y"]
    for idx in range(180):
        x1 = -1.0 + (2.0 * idx / 179.0)
        x2 = (idx % 9) / 8.0
        y = 2.4 if (x1 > 0.35 and x2 > 0.5) else -1.1
        rows.append(f"{x1:.5f},{x2:.5f},{y:.5f}")
    csv_path.write_text("\n".join(rows), encoding="utf-8")

    registry = build_default_registry()
    result = registry.execute(
        "train_surrogate_candidates",
        {
            "data_path": str(csv_path),
            "target_column": "y",
            "feature_columns": ["x1", "x2"],
            "requested_model_family": "boosted_tree_ensemble",
            "run_id": "boosted_regression_run",
        },
    )
    assert result.status == "ok"
    payload = result.output
    assert payload["requested_model_family"] == "boosted_tree_ensemble"
    assert payload["selected_model_family"] == "boosted_tree_ensemble"
    assert payload["selected_hyperparameters"]["n_estimators"] >= 1
    assert payload["selected_hyperparameters"]["learning_rate"] > 0.0
    assert payload["selected_metrics"]["test"]["r2"] > 0.30
    analysis = payload["professional_analysis"]
    assert isinstance(analysis, dict)
    assert analysis.get("summary")
    assert isinstance(analysis.get("suggestions"), list)


def test_train_surrogate_candidates_supports_boosted_tree_classifier(
    monkeypatch, tmp_path: Path
) -> None:
    monkeypatch.chdir(tmp_path)
    csv_path = tmp_path / "boosted_classifier.csv"
    rows = ["feature_a,feature_b,class_label"]
    for idx in range(180):
        a = idx / 179.0
        b = (idx % 10) / 9.0
        label = 1 if (a > 0.55 and b > 0.4) else 0
        rows.append(f"{a:.5f},{b:.5f},{label}")
    csv_path.write_text("\n".join(rows), encoding="utf-8")

    registry = build_default_registry()
    result = registry.execute(
        "train_surrogate_candidates",
        {
            "data_path": str(csv_path),
            "target_column": "class_label",
            "feature_columns": ["feature_a", "feature_b"],
            "requested_model_family": "boosted_tree_classifier",
            "run_id": "boosted_classifier_run",
        },
    )
    assert result.status == "ok"
    payload = result.output
    assert payload["selected_model_family"] == "boosted_tree_classifier"
    assert payload["selected_hyperparameters"]["learning_rate"] > 0.0
    assert payload["selected_metrics"]["test"]["f1"] > 0.75
    analysis = payload["professional_analysis"]
    assert isinstance(analysis.get("high_error_regions"), list)


def test_train_surrogate_candidates_supports_hist_gradient_boosting_regression(
    monkeypatch, tmp_path: Path
) -> None:
    monkeypatch.chdir(tmp_path)
    csv_path = tmp_path / "hist_gradient_regression.csv"
    rows = ["x1,x2,y"]
    for idx in range(220):
        x1 = -1.0 + (2.0 * idx / 219.0)
        x2 = (idx % 12) / 11.0
        y = (x1 * x1) + (2.0 * x2) + (1.8 if x1 > 0.2 else -0.6)
        rows.append(f"{x1:.5f},{x2:.5f},{y:.5f}")
    csv_path.write_text("\n".join(rows), encoding="utf-8")

    registry = build_default_registry()
    result = registry.execute(
        "train_surrogate_candidates",
        {
            "data_path": str(csv_path),
            "target_column": "y",
            "feature_columns": ["x1", "x2"],
            "requested_model_family": "hist_gradient_boosting",
            "run_id": "hist_gradient_regression_run",
        },
    )

    assert result.status == "ok"
    payload = result.output
    assert payload["requested_model_family"] == "hist_gradient_boosting_ensemble"
    assert payload["selected_model_family"] == "hist_gradient_boosting_ensemble"
    assert payload["selected_hyperparameters"]["selected_variant_id"].startswith("hist_")
    assert payload["selected_metrics"]["test"]["r2"] > 0.55
    assert Path(payload["model_state_path"]).is_file()


def test_train_surrogate_candidates_supports_extra_trees_multiclass_strings(
    monkeypatch, tmp_path: Path
) -> None:
    monkeypatch.chdir(tmp_path)
    csv_path = tmp_path / "extra_trees_multiclass.csv"
    rows = ["length,width,color_score,bean_class"]
    for idx in range(210):
        if idx < 70:
            length = 1.0 + (idx / 140.0)
            width = 0.2 + ((idx % 7) / 100.0)
            color = 0.1 + ((idx % 5) / 25.0)
            label = "CALI"
        elif idx < 140:
            local = idx - 70
            length = 2.0 + (local / 140.0)
            width = 0.8 + ((local % 7) / 80.0)
            color = 0.5 + ((local % 5) / 25.0)
            label = "SIRA"
        else:
            local = idx - 140
            length = 3.0 + (local / 140.0)
            width = 1.5 + ((local % 7) / 60.0)
            color = 0.9 + ((local % 5) / 20.0)
            label = "DERMASON"
        rows.append(f"{length:.5f},{width:.5f},{color:.5f},{label}")
    csv_path.write_text("\n".join(rows), encoding="utf-8")

    registry = build_default_registry()
    result = registry.execute(
        "train_surrogate_candidates",
        {
            "data_path": str(csv_path),
            "target_column": "bean_class",
            "feature_columns": ["length", "width", "color_score"],
            "requested_model_family": "extra_trees_classifier",
            "run_id": "extra_trees_multiclass_run",
        },
    )

    assert result.status == "ok"
    payload = result.output
    assert payload["task_profile"]["task_type"] == "multiclass_classification"
    assert payload["requested_model_family"] == "extra_trees_classifier"
    assert payload["selected_model_family"] == "extra_trees_classifier"
    assert payload["selected_hyperparameters"]["selected_variant_id"].startswith("extra_classifier_")
    assert payload["selected_metrics"]["test"]["accuracy"] >= 0.80


def test_train_surrogate_candidates_executes_categorical_features_missingness_and_calibration(
    monkeypatch, tmp_path: Path
) -> None:
    monkeypatch.chdir(tmp_path)
    csv_path = tmp_path / "categorical_missing_classification.csv"
    rows = ["amount,velocity,device_type,region_code,fraud_flag"]
    device_cycle = ["mobile", "desktop", "tablet", ""]
    region_cycle = ["north", "south", "west", "east"]
    for idx in range(220):
        amount = 0.1 + ((idx % 17) / 20.0)
        velocity = "" if idx % 11 == 0 else f"{0.05 + ((idx % 9) / 10.0):.4f}"
        device = device_cycle[idx % len(device_cycle)]
        region = region_cycle[idx % len(region_cycle)]
        fraud = 1 if ((amount > 0.65 and device in {"mobile", "tablet"}) or region == "west" or idx % 19 == 0) else 0
        rows.append(f"{amount:.4f},{velocity},{device},{region},{fraud}")
    csv_path.write_text("\n".join(rows), encoding="utf-8")

    registry = build_default_registry()
    result = registry.execute(
        "train_surrogate_candidates",
        {
            "data_path": str(csv_path),
            "target_column": "fraud_flag",
            "feature_columns": ["amount", "velocity", "device_type", "region_code"],
            "requested_model_family": "auto",
            "run_id": "categorical_missing_classification_run",
        },
    )
    assert result.status == "ok"
    payload = result.output
    summary = dict(payload["preprocessing"].get("feature_engineering_summary", {}))

    assert summary["categorical_raw_feature_count"] >= 2
    assert summary["missing_indicator_count"] >= 1
    assert summary["interaction_count"] >= 1
    assert summary["engineered_feature_count"] >= 3
    assert any(column.startswith("cat__") for column in payload["model_feature_columns"])
    assert any(column.startswith("miss__") for column in payload["model_feature_columns"])
    assert any("__x__" in column for column in payload["model_feature_columns"])
    assert "brier_score" in payload["selected_metrics"]["test"]
    assert "expected_calibration_error" in payload["selected_metrics"]["test"]
    assert payload["selected_hyperparameters"]["selected_variant_id"]

