"""PyOD-backed anomaly challenger helpers."""

from __future__ import annotations

from collections import Counter
import os
import platform
from typing import Any

import numpy as np
import pandas as pd

from relaytic.analytics import assess_task_profile
from relaytic.modeling import build_train_validation_test_split
from relaytic.modeling.evaluation import classification_metrics

from .runtime import base_integration_result, import_optional_module


def run_pyod_anomaly_challenger(
    *,
    frame: pd.DataFrame,
    feature_columns: list[str],
    target_column: str,
    task_type: str | None,
    surface: str = "evidence.challenger",
) -> dict[str, Any]:
    """Run a PyOD anomaly challenger if available and applicable."""
    if not _pyod_runtime_allowed():
        return base_integration_result(
            integration="pyod",
            package_name="pyod",
            surface=surface,
            status="guarded",
            compatible=False,
            notes=[
                (
                    "PyOD is runtime-guarded on Windows by default because the current "
                    "PyOD/numba/llvmlite stack can destabilize the interpreter. Set "
                    "`RELAYTIC_ALLOW_UNSTABLE_PYOD=1` only if you intentionally want to bypass this guard."
                )
            ],
        )
    pyod_module = import_optional_module("pyod.models.iforest")
    if pyod_module is None:
        return base_integration_result(
            integration="pyod",
            package_name="pyod",
            surface=surface,
            status="not_installed",
            compatible=False,
            notes=["PyOD is not installed locally; anomaly challenger skipped."],
        )
    detector_cls = getattr(pyod_module, "IForest", None)
    if detector_cls is None:
        return base_integration_result(
            integration="pyod",
            package_name="pyod",
            surface=surface,
            status="incompatible",
            compatible=False,
            notes=["PyOD is installed but `pyod.models.iforest.IForest` is unavailable."],
        )
    if not feature_columns or target_column not in frame.columns:
        return base_integration_result(
            integration="pyod",
            package_name="pyod",
            surface=surface,
            status="skipped",
            compatible=True,
            notes=["Anomaly challenger requires a target column and at least one feature column."],
        )
    profile = assess_task_profile(
        frame=frame,
        target_column=target_column,
        data_mode="steady_state",
        task_type_hint=task_type,
    )
    if profile.task_type != "anomaly_detection":
        return base_integration_result(
            integration="pyod",
            package_name="pyod",
            surface=surface,
            status="skipped",
            compatible=True,
            notes=["PyOD challenger is currently reserved for anomaly-detection tasks."],
            details={"task_type": profile.task_type},
        )

    working = frame[list(feature_columns) + [target_column]].copy()
    for column in feature_columns:
        working[column] = pd.to_numeric(working[column], errors="coerce")
    working[target_column] = working[target_column].astype(str)
    working = working.dropna(subset=[target_column]).reset_index(drop=True)
    if working.empty:
        return base_integration_result(
            integration="pyod",
            package_name="pyod",
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
            integration="pyod",
            package_name="pyod",
            surface=surface,
            status="skipped",
            compatible=True,
            notes=[f"PyOD challenger skipped: {exc}"],
            details={"row_count": int(len(working)), "task_type": profile.task_type},
        )
    except Exception as exc:
        return base_integration_result(
            integration="pyod",
            package_name="pyod",
            surface=surface,
            status="error",
            compatible=False,
            notes=[f"Split construction for the PyOD challenger failed: {exc}"],
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
            integration="pyod",
            package_name="pyod",
            surface=surface,
            status="skipped",
            compatible=True,
            notes=["One or more split partitions became empty after preprocessing."],
        )
    train_labels = train[target_column].astype(str).tolist()
    counts = Counter(train_labels)
    if len(counts) < 2:
        return base_integration_result(
            integration="pyod",
            package_name="pyod",
            surface=surface,
            status="skipped",
            compatible=True,
            notes=["Training split contains fewer than two classes."],
        )
    positive_label = min(counts.items(), key=lambda item: (item[1], str(item[0])))[0]
    contamination = float(counts[positive_label] / max(len(train_labels), 1))
    contamination = max(0.01, min(0.40, contamination))
    try:
        detector = detector_cls(contamination=contamination)
        detector.fit(train[feature_columns].to_numpy(dtype=float))
    except Exception as exc:
        return base_integration_result(
            integration="pyod",
            package_name="pyod",
            surface=surface,
            status="error",
            compatible=False,
            notes=[f"PyOD challenger failed: {exc}"],
        )

    class_labels = ["0", "1"]
    metrics = {
        "train": _pyod_metrics(
            detector=detector,
            frame=train,
            feature_columns=feature_columns,
            target_column=target_column,
            class_labels=class_labels,
            positive_label=positive_label,
        ),
        "validation": _pyod_metrics(
            detector=detector,
            frame=validation,
            feature_columns=feature_columns,
            target_column=target_column,
            class_labels=class_labels,
            positive_label=positive_label,
        ),
        "test": _pyod_metrics(
            detector=detector,
            frame=test,
            feature_columns=feature_columns,
            target_column=target_column,
            class_labels=class_labels,
            positive_label=positive_label,
        ),
    }
    primary_metric_value = float(metrics["test"].get("pr_auc", 0.0))
    return base_integration_result(
        integration="pyod",
        package_name="pyod",
        surface=surface,
        status="ok",
        compatible=True,
        notes=["PyOD IForest anomaly challenger completed successfully."],
        details={
            "model_family": "pyod_iforest_anomaly",
            "task_type": profile.task_type,
            "primary_metric": "pr_auc",
            "primary_metric_value": primary_metric_value,
            "selected_metrics": metrics,
            "contamination": contamination,
        },
    )


def _pyod_metrics(
    *,
    detector: Any,
    frame: pd.DataFrame,
    feature_columns: list[str],
    target_column: str,
    class_labels: list[str],
    positive_label: str,
) -> dict[str, float]:
    scores = np.asarray(detector.decision_function(frame[feature_columns].to_numpy(dtype=float)), dtype=float)
    probabilities = _score_probabilities(scores)
    metrics = classification_metrics(
        y_true=[str(item) for item in frame[target_column].astype(str).tolist()],
        probabilities=probabilities,
        class_labels=class_labels,
        positive_label=str(positive_label),
        decision_threshold=0.5,
    ).to_dict()
    return {str(key): float(value) for key, value in metrics.items()}


def _score_probabilities(scores: np.ndarray) -> np.ndarray:
    if scores.size == 0:
        return np.zeros((0, 2), dtype=float)
    low = float(np.min(scores))
    high = float(np.max(scores))
    if abs(high - low) < 1e-12:
        positive = np.full(scores.shape[0], 0.5, dtype=float)
    else:
        positive = (scores - low) / (high - low)
    negative = 1.0 - positive
    return np.column_stack([negative, positive])


def self_check_pyod() -> dict[str, Any]:
    """Run a tiny self-check against PyOD's IForest surface."""
    frame = pd.DataFrame(
        {
            "signal_a": [
                0.1,
                0.12,
                0.15,
                0.18,
                0.19,
                0.2,
                0.82,
                0.85,
                0.88,
                0.91,
                0.13,
                0.14,
                0.16,
                0.17,
                0.89,
                0.93,
            ],
            "signal_b": [
                1.1,
                1.0,
                1.2,
                1.15,
                1.18,
                1.22,
                2.8,
                2.9,
                3.0,
                3.1,
                1.05,
                1.1,
                1.2,
                1.25,
                3.2,
                3.3,
            ],
            "fault_flag": [0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 1, 1],
        }
    )
    return run_pyod_anomaly_challenger(
        frame=frame,
        feature_columns=["signal_a", "signal_b"],
        target_column="fault_flag",
        task_type="anomaly_detection",
        surface="integrations.self_check",
    )


def _pyod_runtime_allowed() -> bool:
    if platform.system().lower() != "windows":
        return True
    override = os.environ.get("RELAYTIC_ALLOW_UNSTABLE_PYOD", "").strip().lower()
    return override in {"1", "true", "yes", "on"}
