from __future__ import annotations

import numpy as np

from relaytic.modeling.calibration import select_binary_calibration_strategy
from relaytic.modeling.training import _build_binary_operating_point


def test_select_binary_calibration_strategy_prefers_evidence_based_non_identity_method() -> None:
    labels = ["1", "1", "0", "0", "1", "0", "1", "0"]
    probabilities = np.array(
        [
            [0.40, 0.60],
            [0.45, 0.55],
            [0.20, 0.80],
            [0.25, 0.75],
            [0.48, 0.52],
            [0.30, 0.70],
            [0.51, 0.49],
            [0.52, 0.48],
        ],
        dtype=float,
    )

    payload = select_binary_calibration_strategy(
        y_true=labels,
        probabilities=probabilities,
        class_labels=["0", "1"],
        positive_label="1",
    )

    assert payload["selected_method"] == "platt_scaling"
    assert payload["selection_metric"] == "validation_log_loss_then_ece"
    assert len(payload["candidates"]) == 3
    assert "selected `platt_scaling`" in payload["selection_reason"]


def test_build_binary_operating_point_can_choose_review_budget_threshold_over_raw_metric_threshold() -> None:
    labels = ["1", "1", "1", "1", "0", "0", "0", "0", "0", "0", "0", "0"]
    probabilities = np.array(
        [
            [0.40, 0.60],
            [0.45, 0.55],
            [0.46, 0.54],
            [0.48, 0.52],
            [0.49, 0.51],
            [0.50, 0.50],
            [0.52, 0.48],
            [0.60, 0.40],
            [0.65, 0.35],
            [0.70, 0.30],
            [0.75, 0.25],
            [0.80, 0.20],
        ],
        dtype=float,
    )

    payload = _build_binary_operating_point(
        probabilities=probabilities,
        y_true=labels,
        class_labels=["0", "1"],
        positive_label="1",
        task_type="fraud_detection",
        threshold_policy="auto",
        explicit_threshold=None,
    )

    assert payload["status"] == "ok"
    assert payload["raw_best_threshold"] == 0.5
    assert payload["review_budget_threshold"] == 0.6
    assert payload["selected_threshold"] == 0.6
    assert payload["selected_reason_codes"] == ["review_budget_aware_optimum"]
    assert payload["review_budget_fraction"] == 0.16
    assert payload["abstention_state"] == "review_band"
    assert len(payload["threshold_candidates"]) >= 10
