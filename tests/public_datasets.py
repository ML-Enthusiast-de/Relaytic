"""Helpers for stable public dataset fixtures used in end-to-end tests."""

from __future__ import annotations

import re
from pathlib import Path

import numpy as np
import pandas as pd
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


def write_public_temporal_occupancy_dataset(path: Path, *, max_rows: int = 1500) -> Path:
    """Write a deterministic temporal occupancy dataset for offline benchmark tests."""
    timestamps = pd.date_range("2024-01-01 00:00:00", periods=max_rows, freq="5min")
    frame = pd.DataFrame({"timestamp": timestamps})
    minute_of_day = timestamps.hour * 60 + timestamps.minute
    weekday = timestamps.dayofweek
    workday = (weekday < 5).astype(int)
    occupied = (
        (workday == 1)
        & (minute_of_day >= 8 * 60)
        & (minute_of_day < 18 * 60)
    ).astype(int)
    midday_peak = ((minute_of_day >= 11 * 60) & (minute_of_day < 14 * 60)).astype(int)
    evening_decay = ((minute_of_day >= 17 * 60) & (minute_of_day < 19 * 60)).astype(int)

    frame["temperature"] = 20.5 + (minute_of_day / 1440.0) * 2.2 + occupied * 1.6 + midday_peak * 0.9
    frame["humidity"] = 31.0 + ((minute_of_day + 180) % 1440) / 1440.0 * 11.0 + occupied * 2.4
    frame["light"] = occupied * 260.0 + midday_peak * 110.0 + evening_decay * 35.0
    frame["co2"] = 430.0 + occupied * 340.0 + midday_peak * 90.0 + (minute_of_day % 60) * 1.5
    frame["humidity_ratio"] = ((frame["humidity"] / 100.0) * (frame["temperature"] + 273.15) / 273.15).round(6)
    frame["occupancy_flag"] = occupied.astype(int)
    frame["timestamp"] = frame["timestamp"].dt.strftime("%Y-%m-%d %H:%M:%S")
    frame.to_csv(path, index=False)
    return path


def write_public_temporal_energy_dataset(path: Path, *, max_rows: int = 1600) -> Path:
    """Write a deterministic temporal regression dataset with meaningful lag structure."""
    timestamps = pd.date_range("2024-01-01 00:00:00", periods=max_rows, freq="15min")
    minute_of_day = timestamps.hour * 60 + timestamps.minute
    day_index = np.arange(max_rows, dtype=float) / 96.0
    base_load = 42.0 + np.sin(2.0 * np.pi * day_index / 7.0) * 3.2
    occupancy_cycle = ((minute_of_day >= 7 * 60) & (minute_of_day < 20 * 60)).astype(float)
    hvac_signal = 18.0 + np.sin(2.0 * np.pi * minute_of_day / 1440.0) * 4.5 + occupancy_cycle * 2.0
    equipment_signal = 9.0 + np.cos(2.0 * np.pi * minute_of_day / 720.0) * 1.4 + occupancy_cycle * 1.6
    external_temp = 11.0 + np.sin(2.0 * np.pi * (minute_of_day + 180) / 1440.0) * 7.5
    control_signal = ((np.arange(max_rows) // 4) % 2).astype(float)

    lagged_hvac = np.roll(hvac_signal, 1)
    lagged_hvac[0] = hvac_signal[0]
    lagged_equipment = np.roll(equipment_signal, 2)
    lagged_equipment[:2] = equipment_signal[:2]
    lagged_control = np.roll(control_signal, 4)
    lagged_control[:4] = control_signal[:4]

    target = (
        base_load
        + 5.6 * lagged_control
        + 0.38 * lagged_hvac
        + 0.22 * lagged_equipment
        + 0.05 * external_temp
        + occupancy_cycle * 2.8
    )
    target = np.round(target, 6)

    frame = pd.DataFrame(
        {
            "timestamp": timestamps.strftime("%Y-%m-%d %H:%M:%S"),
            "hvac_signal": np.round(hvac_signal, 6),
            "equipment_signal": np.round(equipment_signal, 6),
            "external_temp": np.round(external_temp, 6),
            "control_signal": control_signal.astype(int),
            "occupancy_cycle": occupancy_cycle.astype(int),
            "energy_target": target,
        }
    )
    frame.to_csv(path, index=False)
    return path
