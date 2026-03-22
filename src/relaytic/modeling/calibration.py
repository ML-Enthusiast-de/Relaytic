"""Lightweight calibration and uncertainty helpers for local Relaytic models."""

from __future__ import annotations

from typing import Any

import numpy as np


def fit_binary_platt_calibrator(
    *,
    y_true: list[str] | np.ndarray,
    positive_scores: np.ndarray,
    positive_label: str,
    learning_rate: float = 0.05,
    epochs: int = 400,
) -> dict[str, Any]:
    """Fit a small Platt-style calibrator on validation predictions."""
    labels = np.asarray([str(item) for item in y_true], dtype=object)
    scores = np.asarray(positive_scores, dtype=float)
    if labels.size == 0 or scores.size == 0 or labels.size != scores.size:
        return {"status": "identity", "method": "none"}
    binary = (labels == str(positive_label)).astype(float)
    positives = int(np.sum(binary))
    negatives = int(binary.size - positives)
    if positives == 0 or negatives == 0:
        return {"status": "identity", "method": "none"}
    clipped = np.clip(scores, 1e-6, 1.0 - 1e-6)
    logits = np.log(clipped / (1.0 - clipped))
    slope = 1.0
    intercept = 0.0
    for _ in range(max(50, int(epochs))):
        calibrated_logits = (slope * logits) + intercept
        probs = 1.0 / (1.0 + np.exp(-np.clip(calibrated_logits, -40.0, 40.0)))
        error = probs - binary
        slope_grad = float(np.mean(error * logits))
        intercept_grad = float(np.mean(error))
        slope -= float(learning_rate) * slope_grad
        intercept -= float(learning_rate) * intercept_grad
    return {
        "status": "ok",
        "method": "platt_scaling",
        "positive_label": str(positive_label),
        "slope": float(slope),
        "intercept": float(intercept),
        "validation_row_count": int(labels.size),
    }


def apply_binary_platt_calibrator(
    *,
    probabilities: np.ndarray,
    class_labels: list[str],
    calibrator: dict[str, Any] | None,
) -> np.ndarray:
    """Apply a fitted Platt calibrator to binary probabilities."""
    raw = np.asarray(probabilities, dtype=float)
    if raw.ndim != 2 or raw.shape[1] != 2 or not calibrator:
        return raw
    if str(calibrator.get("status", "")).strip() != "ok":
        return raw
    positive_label = str(calibrator.get("positive_label", "")).strip()
    if positive_label not in class_labels:
        return raw
    slope = float(calibrator.get("slope", 1.0))
    intercept = float(calibrator.get("intercept", 0.0))
    pos_idx = class_labels.index(positive_label)
    neg_idx = 1 - pos_idx
    positive_scores = np.clip(raw[:, pos_idx], 1e-6, 1.0 - 1e-6)
    logits = np.log(positive_scores / (1.0 - positive_scores))
    calibrated_logits = (slope * logits) + intercept
    calibrated_positive = 1.0 / (1.0 + np.exp(-np.clip(calibrated_logits, -40.0, 40.0)))
    calibrated = np.zeros_like(raw, dtype=float)
    calibrated[:, pos_idx] = calibrated_positive
    calibrated[:, neg_idx] = 1.0 - calibrated_positive
    return calibrated


def fit_regression_residual_interval(
    *,
    y_true: np.ndarray | list[float],
    y_pred: np.ndarray | list[float],
    coverage: float = 0.90,
) -> dict[str, Any]:
    """Fit a residual-quantile interval from validation residuals."""
    true = np.asarray(y_true, dtype=float)
    pred = np.asarray(y_pred, dtype=float)
    if true.size == 0 or pred.size == 0 or true.size != pred.size:
        return {"status": "unavailable", "method": "none"}
    residual = true - pred
    alpha = max(0.01, min(0.25, (1.0 - float(coverage)) / 2.0))
    lower = float(np.quantile(residual, alpha))
    upper = float(np.quantile(residual, 1.0 - alpha))
    abs_margin = float(np.quantile(np.abs(residual), coverage))
    within = ((residual >= lower) & (residual <= upper)).astype(float)
    return {
        "status": "ok",
        "method": "residual_quantile",
        "coverage_target": float(coverage),
        "coverage_estimate": float(np.mean(within)),
        "residual_lower": lower,
        "residual_upper": upper,
        "absolute_margin": abs_margin,
        "validation_row_count": int(true.size),
    }


def apply_regression_residual_interval(
    *,
    predictions: np.ndarray | list[float],
    interval: dict[str, Any] | None,
) -> dict[str, np.ndarray]:
    """Apply one residual interval payload to regression predictions."""
    pred = np.asarray(predictions, dtype=float)
    if not interval or str(interval.get("status", "")).strip() != "ok":
        return {
            "prediction": pred,
            "lower": pred,
            "upper": pred,
        }
    lower = pred + float(interval.get("residual_lower", 0.0))
    upper = pred + float(interval.get("residual_upper", 0.0))
    return {
        "prediction": pred,
        "lower": lower,
        "upper": upper,
    }
