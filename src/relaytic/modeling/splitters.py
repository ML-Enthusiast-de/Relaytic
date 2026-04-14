"""Data splitting strategies for modeling workflows."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Sequence

import numpy as np


@dataclass(frozen=True)
class DatasetSplit:
    """Deterministic split indices for train/validation/test."""

    train_indices: np.ndarray
    validation_indices: np.ndarray
    test_indices: np.ndarray
    strategy: str
    data_mode: str

    def to_dict(self) -> dict[str, object]:
        return {
            "train_size": int(self.train_indices.size),
            "validation_size": int(self.validation_indices.size),
            "test_size": int(self.test_indices.size),
            "strategy": self.strategy,
            "data_mode": self.data_mode,
        }


def build_train_validation_test_split(
    *,
    n_rows: int,
    data_mode: str,
    task_type: str = "regression",
    stratify_labels: Sequence[Any] | np.ndarray | None = None,
) -> DatasetSplit:
    """Build deterministic split indices for tabular or time-series data."""
    if n_rows < 12:
        raise ValueError("At least 12 rows are required for train/validation/test split.")
    mode = data_mode.strip().lower()
    if mode == "time_series":
        return _build_time_series_split(n_rows=n_rows, stratify_labels=stratify_labels)
    if str(task_type).strip() in {
        "binary_classification",
        "multiclass_classification",
        "fraud_detection",
        "anomaly_detection",
    }:
        stratified = _build_steady_state_stratified_split(
            n_rows=n_rows,
            stratify_labels=stratify_labels,
        )
        if stratified is not None:
            return stratified
    return _build_steady_state_split(n_rows=n_rows)


def _build_time_series_split(
    *,
    n_rows: int,
    stratify_labels: Sequence[Any] | np.ndarray | None = None,
) -> DatasetSplit:
    train_end, val_end = _default_time_series_boundaries(n_rows=n_rows)
    if stratify_labels is not None:
        adjusted = _event_preserving_time_series_boundaries(
            n_rows=n_rows,
            stratify_labels=stratify_labels,
            default_train_end=train_end,
            default_val_end=val_end,
        )
        if adjusted is not None:
            train_end, val_end = adjusted
            return DatasetSplit(
                train_indices=np.arange(0, train_end, dtype=int),
                validation_indices=np.arange(train_end, val_end, dtype=int),
                test_indices=np.arange(val_end, n_rows, dtype=int),
                strategy="blocked_time_order_event_preserving_70_15_15",
                data_mode="time_series",
            )
    return DatasetSplit(
        train_indices=np.arange(0, train_end, dtype=int),
        validation_indices=np.arange(train_end, val_end, dtype=int),
        test_indices=np.arange(val_end, n_rows, dtype=int),
        strategy="blocked_time_order_70_15_15",
        data_mode="time_series",
    )


def _default_time_series_boundaries(*, n_rows: int) -> tuple[int, int]:
    train_end = max(6, int(round(n_rows * 0.70)))
    val_end = max(train_end + 2, int(round(n_rows * 0.85)))
    train_end = min(train_end, n_rows - 4)
    val_end = min(val_end, n_rows - 2)
    if train_end < 6 or (val_end - train_end) < 2 or (n_rows - val_end) < 2:
        train_end = max(6, n_rows - 4)
        val_end = n_rows - 2
    if train_end < 6 or (val_end - train_end) < 2 or (n_rows - val_end) < 2:
        raise ValueError("Unable to create a valid time-series split with current row count.")
    return train_end, val_end


def _event_preserving_time_series_boundaries(
    *,
    n_rows: int,
    stratify_labels: Sequence[Any] | np.ndarray,
    default_train_end: int,
    default_val_end: int,
) -> tuple[int, int] | None:
    labels = np.asarray(list(stratify_labels), dtype=object)
    if labels.shape[0] != n_rows:
        raise ValueError("stratify_labels length must match n_rows.")
    normalized = np.asarray([str(item) for item in labels.tolist()], dtype=object)
    unique_labels, inverse = np.unique(normalized, return_inverse=True)
    if unique_labels.size < 2:
        return None

    label_totals = np.bincount(inverse, minlength=int(unique_labels.size))
    required_indices = np.where(label_totals >= 3)[0]
    if required_indices.size == 0:
        return None

    prefix = np.zeros((n_rows + 1, int(unique_labels.size)), dtype=int)
    for idx, class_index in enumerate(inverse.tolist(), start=1):
        prefix[idx] = prefix[idx - 1]
        prefix[idx, int(class_index)] += 1

    def _slice_counts(start: int, end: int) -> np.ndarray:
        return prefix[end] - prefix[start]

    def _covers_required_labels(start: int, end: int) -> bool:
        counts = _slice_counts(start, end)
        return bool(np.all(counts[required_indices] > 0))

    search_radius = max(12, min(256, int(round(n_rows * 0.20))))
    train_candidates = range(
        max(6, default_train_end - search_radius),
        min(n_rows - 4, default_train_end + search_radius) + 1,
    )
    val_floor = max(8, default_val_end - search_radius)
    val_ceiling = min(n_rows - 2, default_val_end + search_radius)

    best_candidate: tuple[int, int] | None = None
    best_score: tuple[int, int] | None = None
    for train_end in train_candidates:
        for val_end in range(max(train_end + 2, val_floor), val_ceiling + 1):
            if (val_end - train_end) < 2 or (n_rows - val_end) < 2:
                continue
            if not _covers_required_labels(0, train_end):
                continue
            if not _covers_required_labels(train_end, val_end):
                continue
            if not _covers_required_labels(val_end, n_rows):
                continue
            score = (
                abs(train_end - default_train_end) + abs(val_end - default_val_end),
                abs((val_end - train_end) - max(2, int(round(n_rows * 0.15)))),
            )
            if best_score is None or score < best_score:
                best_score = score
                best_candidate = (train_end, val_end)
    return best_candidate


def _build_steady_state_split(*, n_rows: int) -> DatasetSplit:
    idx = np.arange(n_rows, dtype=int)
    remainder = idx % 20
    test_mask = remainder < 3
    val_mask = (remainder >= 3) & (remainder < 6)
    train_mask = ~(test_mask | val_mask)
    if int(np.sum(test_mask)) < 2 or int(np.sum(val_mask)) < 2 or int(np.sum(train_mask)) < 6:
        split_a = max(6, int(round(n_rows * 0.70)))
        split_b = max(split_a + 2, int(round(n_rows * 0.85)))
        split_a = min(split_a, n_rows - 4)
        split_b = min(split_b, n_rows - 2)
        train_idx = idx[:split_a]
        val_idx = idx[split_a:split_b]
        test_idx = idx[split_b:]
        if train_idx.size < 6 or val_idx.size < 2 or test_idx.size < 2:
            raise ValueError("Unable to create a valid steady-state split with current row count.")
        return DatasetSplit(
            train_indices=train_idx,
            validation_indices=val_idx,
            test_indices=test_idx,
            strategy="deterministic_70_15_15_fallback",
            data_mode="steady_state",
        )
    return DatasetSplit(
        train_indices=idx[train_mask],
        validation_indices=idx[val_mask],
        test_indices=idx[test_mask],
        strategy="deterministic_modulo_70_15_15",
        data_mode="steady_state",
    )


def _build_steady_state_stratified_split(
    *,
    n_rows: int,
    stratify_labels: Sequence[Any] | np.ndarray | None,
) -> DatasetSplit | None:
    if stratify_labels is None:
        return None
    labels = np.asarray(list(stratify_labels), dtype=object)
    if labels.shape[0] != n_rows:
        raise ValueError("stratify_labels length must match n_rows.")
    idx = np.arange(n_rows, dtype=int)
    train_mask = np.zeros(n_rows, dtype=bool)
    val_mask = np.zeros(n_rows, dtype=bool)
    test_mask = np.zeros(n_rows, dtype=bool)

    seen_labels: list[Any] = []
    seen_tokens: set[str] = set()
    for value in labels.tolist():
        token = str(value)
        if token in seen_tokens:
            continue
        seen_tokens.add(token)
        seen_labels.append(value)

    for label in seen_labels:
        class_indices = idx[labels == label]
        if class_indices.size == 0:
            continue
        ordered_class_indices = _deterministic_class_order(class_indices)
        train_count, val_count, test_count = _allocate_class_counts(int(class_indices.size))
        train_end = train_count
        val_end = train_count + val_count
        train_mask[ordered_class_indices[:train_end]] = True
        val_mask[ordered_class_indices[train_end:val_end]] = True
        test_mask[ordered_class_indices[val_end : val_end + test_count]] = True

    if int(np.sum(test_mask)) < 2 or int(np.sum(val_mask)) < 2 or int(np.sum(train_mask)) < 6:
        return None
    return DatasetSplit(
        train_indices=idx[train_mask],
        validation_indices=idx[val_mask],
        test_indices=idx[test_mask],
        strategy="stratified_deterministic_modulo_70_15_15",
        data_mode="steady_state",
    )


def _allocate_class_counts(class_size: int) -> tuple[int, int, int]:
    if class_size <= 0:
        return 0, 0, 0
    if class_size == 1:
        return 1, 0, 0
    if class_size == 2:
        return 1, 0, 1
    if class_size == 3:
        return 1, 1, 1

    train_count = max(1, int(round(class_size * 0.70)))
    val_count = max(1, int(round(class_size * 0.15)))
    test_count = class_size - train_count - val_count
    if test_count < 1:
        test_count = 1
        if train_count >= val_count and train_count > 1:
            train_count -= 1
        elif val_count > 1:
            val_count -= 1
    while train_count + val_count + test_count > class_size:
        if train_count >= val_count and train_count > 1:
            train_count -= 1
        elif val_count > 1:
            val_count -= 1
        else:
            test_count -= 1
    return train_count, val_count, test_count


def _deterministic_class_order(class_indices: np.ndarray) -> np.ndarray:
    if class_indices.size <= 2:
        return class_indices
    positions = np.arange(class_indices.size, dtype=int)
    multiplier = 7 if class_indices.size % 7 else 5
    order = np.argsort((positions * multiplier) % class_indices.size, kind="stable")
    return class_indices[order]
