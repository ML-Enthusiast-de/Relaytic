"""Official domain-dataset helpers for optional network-backed Relaytic tests."""

from __future__ import annotations

from functools import lru_cache
import re
from pathlib import Path

import pandas as pd
from ucimlrepo import fetch_ucirepo


def _normalize_name(value: str) -> str:
    normalized = re.sub(r"[^A-Za-z0-9]+", "_", value.strip().lower()).strip("_")
    return normalized or "column"


@lru_cache(maxsize=None)
def _fetch_frame(dataset_id: int) -> tuple[pd.DataFrame, pd.DataFrame]:
    dataset = fetch_ucirepo(id=dataset_id)
    features = dataset.data.features.copy()
    targets = dataset.data.targets.copy()
    return features, targets


def _sample_frame(
    frame: pd.DataFrame,
    *,
    target_column: str,
    max_rows: int | None,
    stratify: bool = True,
) -> pd.DataFrame:
    if max_rows is None or len(frame) <= max_rows:
        return frame.reset_index(drop=True)
    if stratify:
        groups = []
        grouped = frame.groupby(target_column, group_keys=False)
        for _, part in grouped:
            share = len(part) / len(frame)
            take = max(1, int(round(max_rows * share)))
            groups.append(part.sample(n=min(take, len(part)), random_state=42))
        sampled = pd.concat(groups, axis=0).sample(frac=1.0, random_state=42)
        return sampled.head(max_rows).reset_index(drop=True)
    return frame.sample(n=max_rows, random_state=42).reset_index(drop=True)


def write_uci_concrete_strength_dataset(path: Path) -> Path:
    features, targets = _fetch_frame(165)
    frame = pd.concat([features, targets], axis=1).copy()
    frame.columns = [_normalize_name(name) for name in frame.columns]
    frame = frame.rename(columns={"concrete_compressive_strength": "concrete_strength"})
    frame.to_csv(path, index=False)
    return path


def write_uci_iranian_churn_dataset(path: Path, *, max_rows: int = 2500) -> Path:
    features, targets = _fetch_frame(563)
    frame = pd.concat([features, targets], axis=1).copy()
    frame.columns = [_normalize_name(name) for name in frame.columns]
    frame = frame.rename(columns={"churn": "churn_flag"})
    frame = _sample_frame(frame, target_column="churn_flag", max_rows=max_rows, stratify=True)
    frame.to_csv(path, index=False)
    return path


def write_uci_credit_default_dataset(path: Path, *, max_rows: int = 5000) -> Path:
    features, targets = _fetch_frame(350)
    frame = pd.concat([features, targets], axis=1).copy()
    frame.columns = [_normalize_name(name) for name in frame.columns]
    frame = frame.rename(columns={"y": "default_flag"})
    frame = _sample_frame(frame, target_column="default_flag", max_rows=max_rows, stratify=True)
    frame.to_csv(path, index=False)
    return path


def write_uci_ai4i_machine_failure_dataset(path: Path, *, max_rows: int = 3000) -> Path:
    features, targets = _fetch_frame(601)
    frame = features.copy()
    frame.columns = [_normalize_name(name) for name in frame.columns]
    frame["type_code"] = frame["type"].astype("category").cat.codes.astype(int)
    frame = frame.drop(columns=["type"])
    target = targets[["Machine failure"]].copy()
    target.columns = ["machine_failure"]
    frame = pd.concat([frame, target], axis=1)
    frame.columns = [_normalize_name(name) for name in frame.columns]
    frame = _sample_frame(frame, target_column="machine_failure", max_rows=max_rows, stratify=True)
    frame.to_csv(path, index=False)
    return path
