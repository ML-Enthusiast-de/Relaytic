"""imbalanced-learn-backed rare-event challenger helpers."""

from __future__ import annotations

from collections import Counter
from typing import Any

import numpy as np
import pandas as pd

from relaytic.analytics import assess_task_profile, is_classification_task
from relaytic.modeling import build_train_validation_test_split
from relaytic.modeling.evaluation import classification_metrics

from .runtime import base_integration_result, import_optional_module


def run_resampled_logistic_challenger(
    *,
    frame: pd.DataFrame,
    feature_columns: list[str],
    target_column: str,
    task_type: str | None,
    surface: str = "evidence.challenger",
) -> dict[str, Any]:
    """Run a stable RandomOverSampler + LogisticRegression challenger if available."""
    imblearn_module = import_optional_module("imblearn.over_sampling")
    linear_model = import_optional_module("sklearn.linear_model")
    if imblearn_module is None:
        return base_integration_result(
            integration="imbalanced_learn",
            package_name="imbalanced-learn",
            surface=surface,
            status="not_installed",
            compatible=False,
            notes=["imbalanced-learn is not installed locally; resampled challenger skipped."],
        )
    if linear_model is None:
        return base_integration_result(
            integration="imbalanced_learn",
            package_name="imbalanced-learn",
            surface=surface,
            status="incompatible",
            compatible=False,
            notes=["scikit-learn logistic regression is unavailable; resampled challenger skipped."],
        )
    sampler_cls = getattr(imblearn_module, "RandomOverSampler", None)
    model_cls = getattr(linear_model, "LogisticRegression", None)
    if sampler_cls is None or model_cls is None:
        return base_integration_result(
            integration="imbalanced_learn",
            package_name="imbalanced-learn",
            surface=surface,
            status="incompatible",
            compatible=False,
            notes=["The expected RandomOverSampler/LogisticRegression API is unavailable."],
        )

    if not feature_columns or target_column not in frame.columns:
        return base_integration_result(
            integration="imbalanced_learn",
            package_name="imbalanced-learn",
            surface=surface,
            status="skipped",
            compatible=True,
            notes=["Challenger requires a target column and at least one feature column."],
        )

    profile = assess_task_profile(
        frame=frame,
        target_column=target_column,
        data_mode="steady_state",
        task_type_hint=task_type,
    )
    if not is_classification_task(profile.task_type):
        return base_integration_result(
            integration="imbalanced_learn",
            package_name="imbalanced-learn",
            surface=surface,
            status="skipped",
            compatible=True,
            notes=["Resampled challenger is only applicable to classification-style targets."],
            details={"task_type": profile.task_type},
        )
    if profile.task_type not in {"fraud_detection", "anomaly_detection", "binary_classification"}:
        return base_integration_result(
            integration="imbalanced_learn",
            package_name="imbalanced-learn",
            surface=surface,
            status="skipped",
            compatible=True,
            notes=["Current resampled challenger is intentionally limited to binary-style tasks."],
            details={"task_type": profile.task_type},
        )

    working = frame[list(feature_columns) + [target_column]].copy()
    for column in feature_columns:
        working[column] = pd.to_numeric(working[column], errors="coerce")
    working[target_column] = working[target_column].astype(str)
    working = working.dropna(subset=[target_column]).reset_index(drop=True)
    if working.empty:
        return base_integration_result(
            integration="imbalanced_learn",
            package_name="imbalanced-learn",
            surface=surface,
            status="skipped",
            compatible=True,
            notes=["No usable target rows remained after preprocessing."],
        )
    try:
        split = build_train_validation_test_split(
            n_rows=len(working),
            data_mode="steady_state",
            task_type=profile.task_type,
            stratify_labels=working[target_column],
        )
    except ValueError as exc:
        return base_integration_result(
            integration="imbalanced_learn",
            package_name="imbalanced-learn",
            surface=surface,
            status="skipped",
            compatible=True,
            notes=[f"Resampled challenger skipped: {exc}"],
            details={"row_count": int(len(working)), "task_type": profile.task_type},
        )
    except Exception as exc:
        return base_integration_result(
            integration="imbalanced_learn",
            package_name="imbalanced-learn",
            surface=surface,
            status="error",
            compatible=False,
            notes=[f"Split construction for the resampled challenger failed: {exc}"],
            details={"row_count": int(len(working)), "task_type": profile.task_type},
        )
    train = working.iloc[split.train_indices].reset_index(drop=True)
    validation = working.iloc[split.validation_indices].reset_index(drop=True)
    test = working.iloc[split.test_indices].reset_index(drop=True)
    fill_values = {column: float(train[column].median(skipna=True)) for column in feature_columns}
    for bundle in (train, validation, test):
        for column in feature_columns:
            bundle[column] = bundle[column].fillna(fill_values[column])
    train = train.dropna(subset=feature_columns).reset_index(drop=True)
    validation = validation.dropna(subset=feature_columns).reset_index(drop=True)
    test = test.dropna(subset=feature_columns).reset_index(drop=True)
    if train.empty or validation.empty or test.empty:
        return base_integration_result(
            integration="imbalanced_learn",
            package_name="imbalanced-learn",
            surface=surface,
            status="skipped",
            compatible=True,
            notes=["One or more split partitions became empty after preprocessing."],
        )
    train_labels = train[target_column].astype(str).tolist()
    class_counts = Counter(train_labels)
    if len(class_counts) < 2:
        return base_integration_result(
            integration="imbalanced_learn",
            package_name="imbalanced-learn",
            surface=surface,
            status="skipped",
            compatible=True,
            notes=["Training split contains fewer than two classes."],
            details={"class_balance_before": dict(class_counts)},
        )

    X_train = train[feature_columns].to_numpy(dtype=float)
    y_train = np.asarray(train_labels)
    sampler = sampler_cls(random_state=0)
    try:
        X_resampled, y_resampled = sampler.fit_resample(X_train, y_train)
        model = model_cls(max_iter=400, solver="liblinear")
        model.fit(X_resampled, y_resampled)
    except Exception as exc:
        return base_integration_result(
            integration="imbalanced_learn",
            package_name="imbalanced-learn",
            surface=surface,
            status="error",
            compatible=False,
            notes=[f"Resampled challenger failed: {exc}"],
        )

    class_labels = [str(item) for item in getattr(model, "classes_", [])]
    positive_label = min(class_counts.items(), key=lambda item: (item[1], str(item[0])))[0]
    metrics = {
        "train": _classification_metrics(
            model=model,
            frame=train,
            feature_columns=feature_columns,
            target_column=target_column,
            class_labels=class_labels,
            positive_label=positive_label,
        ),
        "validation": _classification_metrics(
            model=model,
            frame=validation,
            feature_columns=feature_columns,
            target_column=target_column,
            class_labels=class_labels,
            positive_label=positive_label,
        ),
        "test": _classification_metrics(
            model=model,
            frame=test,
            feature_columns=feature_columns,
            target_column=target_column,
            class_labels=class_labels,
            positive_label=positive_label,
        ),
    }
    primary_metric = "pr_auc" if profile.task_type in {"fraud_detection", "anomaly_detection"} else "f1"
    primary_metric_value = float(metrics["test"].get(primary_metric, 0.0))
    return base_integration_result(
        integration="imbalanced_learn",
        package_name="imbalanced-learn",
        surface=surface,
        status="ok",
        compatible=True,
        notes=["RandomOverSampler + LogisticRegression challenger completed successfully."],
        details={
            "model_family": "imblearn_resampled_logistic",
            "task_type": profile.task_type,
            "primary_metric": primary_metric,
            "primary_metric_value": primary_metric_value,
            "selected_metrics": metrics,
            "class_balance_before": dict(class_counts),
            "class_balance_after": dict(Counter([str(item) for item in y_resampled])),
            "train_rows_before": int(len(train)),
            "train_rows_after_resample": int(len(y_resampled)),
        },
    )


def _classification_metrics(
    *,
    model: Any,
    frame: pd.DataFrame,
    feature_columns: list[str],
    target_column: str,
    class_labels: list[str],
    positive_label: str | None,
) -> dict[str, float]:
    probabilities = np.asarray(model.predict_proba(frame[feature_columns].to_numpy(dtype=float)), dtype=float)
    metrics = classification_metrics(
        y_true=[str(item) for item in frame[target_column].astype(str).tolist()],
        probabilities=probabilities,
        class_labels=class_labels,
        positive_label=str(positive_label) if positive_label is not None else None,
        decision_threshold=0.5 if len(class_labels) == 2 else None,
    ).to_dict()
    return {str(key): float(value) for key, value in metrics.items()}


def self_check_imbalanced_learn() -> dict[str, Any]:
    """Run a tiny self-check against imbalanced-learn's resampling API."""
    frame = pd.DataFrame(
        {
            "score_a": [0.1, 0.2, 0.15, 0.18, 0.82, 0.88, 0.84, 0.9, 0.12, 0.22, 0.19, 0.92],
            "score_b": [0.2, 0.1, 0.11, 0.09, 0.86, 0.9, 0.83, 0.88, 0.18, 0.14, 0.1, 0.91],
            "fraud_flag": [0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 1],
        }
    )
    return run_resampled_logistic_challenger(
        frame=frame,
        feature_columns=["score_a", "score_b"],
        target_column="fraud_flag",
        task_type="fraud_detection",
        surface="integrations.self_check",
    )
