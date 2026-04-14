"""Lightweight calibration and uncertainty helpers for local Relaytic models."""

from __future__ import annotations

from typing import Any

import numpy as np

from .evaluation import classification_metrics


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


def fit_binary_temperature_calibrator(
    *,
    y_true: list[str] | np.ndarray,
    positive_scores: np.ndarray,
    positive_label: str,
    learning_rate: float = 0.05,
    epochs: int = 250,
) -> dict[str, Any]:
    """Fit a one-parameter temperature scaler on validation predictions."""
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
    log_temperature = 0.0
    for _ in range(max(50, int(epochs))):
        temperature = float(np.exp(log_temperature))
        calibrated_logits = logits / max(temperature, 1e-6)
        probs = 1.0 / (1.0 + np.exp(-np.clip(calibrated_logits, -40.0, 40.0)))
        error = probs - binary
        gradient = float(np.mean(error * (-logits / max(temperature, 1e-6))))
        log_temperature -= float(learning_rate) * gradient
        log_temperature = float(np.clip(log_temperature, -2.5, 2.5))
    return {
        "status": "ok",
        "method": "temperature_scaling",
        "positive_label": str(positive_label),
        "temperature": float(np.exp(log_temperature)),
        "validation_row_count": int(labels.size),
    }


def apply_binary_temperature_calibrator(
    *,
    probabilities: np.ndarray,
    class_labels: list[str],
    calibrator: dict[str, Any] | None,
) -> np.ndarray:
    """Apply a fitted temperature calibrator to binary probabilities."""
    raw = np.asarray(probabilities, dtype=float)
    if raw.ndim != 2 or raw.shape[1] != 2 or not calibrator:
        return raw
    if str(calibrator.get("status", "")).strip() != "ok":
        return raw
    positive_label = str(calibrator.get("positive_label", "")).strip()
    if positive_label not in class_labels:
        return raw
    temperature = float(calibrator.get("temperature", 1.0) or 1.0)
    if temperature <= 0.0:
        return raw
    pos_idx = class_labels.index(positive_label)
    neg_idx = 1 - pos_idx
    positive_scores = np.clip(raw[:, pos_idx], 1e-6, 1.0 - 1e-6)
    logits = np.log(positive_scores / (1.0 - positive_scores))
    calibrated_logits = logits / temperature
    calibrated_positive = 1.0 / (1.0 + np.exp(-np.clip(calibrated_logits, -40.0, 40.0)))
    calibrated = np.zeros_like(raw, dtype=float)
    calibrated[:, pos_idx] = calibrated_positive
    calibrated[:, neg_idx] = 1.0 - calibrated_positive
    return calibrated


def apply_binary_calibrator(
    *,
    probabilities: np.ndarray,
    class_labels: list[str],
    calibrator: dict[str, Any] | None,
) -> np.ndarray:
    """Apply one supported binary calibration payload."""
    payload = dict(calibrator or {})
    method = str(payload.get("method", "")).strip().lower()
    if method == "temperature_scaling":
        return apply_binary_temperature_calibrator(
            probabilities=probabilities,
            class_labels=class_labels,
            calibrator=payload,
        )
    return apply_binary_platt_calibrator(
        probabilities=probabilities,
        class_labels=class_labels,
        calibrator=payload,
    )


def select_binary_calibration_strategy(
    *,
    y_true: list[str] | np.ndarray,
    probabilities: np.ndarray,
    class_labels: list[str],
    positive_label: str,
) -> dict[str, Any]:
    """Select the best supported binary calibration strategy on validation data."""
    labels = [str(item) for item in y_true]
    raw = np.asarray(probabilities, dtype=float)
    identity = {
        "status": "identity",
        "method": "none",
        "positive_label": str(positive_label),
        "validation_row_count": int(len(labels)),
    }
    candidates = [
        identity,
        fit_binary_platt_calibrator(
            y_true=labels,
            positive_scores=raw[:, class_labels.index(str(positive_label))],
            positive_label=str(positive_label),
        ),
        fit_binary_temperature_calibrator(
            y_true=labels,
            positive_scores=raw[:, class_labels.index(str(positive_label))],
            positive_label=str(positive_label),
        ),
    ]
    scored_rows: list[dict[str, Any]] = []
    selected_payload = identity
    best_rank: tuple[float, float, float, float] | None = None
    for candidate in candidates:
        calibrated = apply_binary_calibrator(
            probabilities=raw,
            class_labels=class_labels,
            calibrator=candidate,
        )
        metrics = classification_metrics(
            y_true=labels,
            probabilities=calibrated,
            class_labels=class_labels,
            positive_label=positive_label,
            decision_threshold=0.5,
        ).to_dict()
        row = {
            "method": str(candidate.get("method", "none")),
            "status": str(candidate.get("status", "identity")),
            "validation_log_loss": float(metrics.get("log_loss", float("inf"))),
            "validation_expected_calibration_error": float(
                metrics.get("expected_calibration_error", float("inf"))
            ),
            "validation_pr_auc": float(metrics.get("pr_auc", 0.0) or 0.0),
            "validation_f1": float(metrics.get("f1", 0.0) or 0.0),
        }
        rank = (
            row["validation_log_loss"],
            row["validation_expected_calibration_error"],
            -row["validation_pr_auc"],
            -row["validation_f1"],
        )
        scored_rows.append(row)
        if best_rank is None or rank < best_rank:
            best_rank = rank
            selected_payload = dict(candidate)
    selected_method = str(selected_payload.get("method", "none")).strip() or "none"
    selected_metrics = next(
        (row for row in scored_rows if str(row.get("method", "")).strip() == selected_method),
        scored_rows[0],
    )
    selected_payload["selection_metric"] = "validation_log_loss_then_ece"
    selected_payload["selected_method"] = selected_method
    selected_payload["candidates"] = scored_rows
    selected_payload["selected_validation_metrics"] = selected_metrics
    selected_payload["selection_reason"] = (
        f"Relaytic compared identity, Platt scaling, and temperature scaling on validation log loss and calibration error, "
        f"then selected `{selected_method}`."
    )
    return selected_payload


def apply_binary_platt_calibrator(
    *,
    probabilities: np.ndarray,
    class_labels: list[str],
    calibrator: dict[str, Any] | None,
) -> np.ndarray:
    """Apply a fitted Platt-style calibrator payload to binary probabilities."""
    raw = np.asarray(probabilities, dtype=float)
    if raw.ndim != 2 or raw.shape[1] != 2 or not calibrator:
        return raw
    method = str(calibrator.get("method", "")).strip().lower()
    if method in {"none", ""} or str(calibrator.get("status", "")).strip() != "ok":
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
