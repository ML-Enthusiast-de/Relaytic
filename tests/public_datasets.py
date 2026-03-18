"""Helpers for stable public dataset fixtures used in end-to-end tests."""

from __future__ import annotations

import re
from pathlib import Path

from sklearn.datasets import load_breast_cancer, load_diabetes, load_wine


def _normalize_name(value: str) -> str:
    normalized = re.sub(r"[^A-Za-z0-9]+", "_", value.strip().lower()).strip("_")
    return normalized or "column"


def write_public_diabetes_dataset(path: Path) -> Path:
    """Write the bundled public diabetes regression dataset to CSV."""
    frame = load_diabetes(as_frame=True).frame.copy()
    frame.columns = [_normalize_name(name) for name in frame.columns]
    frame = frame.rename(columns={"target": "disease_progression"})
    frame.to_csv(path, index=False)
    return path


def write_public_breast_cancer_dataset(path: Path) -> Path:
    """Write the bundled public breast-cancer classification dataset to CSV."""
    frame = load_breast_cancer(as_frame=True).frame.copy()
    frame.columns = [_normalize_name(name) for name in frame.columns]
    frame = frame.rename(columns={"target": "diagnosis_flag"})
    frame.to_csv(path, index=False)
    return path


def write_public_wine_dataset(path: Path) -> Path:
    """Write the bundled public wine multiclass dataset to CSV."""
    frame = load_wine(as_frame=True).frame.copy()
    frame.columns = [_normalize_name(name) for name in frame.columns]
    frame = frame.rename(columns={"target": "wine_class"})
    frame.to_csv(path, index=False)
    return path
