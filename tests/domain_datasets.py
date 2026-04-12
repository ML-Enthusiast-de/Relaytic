"""Official domain-dataset helpers for optional network-backed Relaytic tests."""

from __future__ import annotations

from functools import lru_cache
import re
from pathlib import Path

import pandas as pd
try:
    from ucimlrepo import fetch_ucirepo
except ModuleNotFoundError:  # pragma: no cover - exercised through fallback helpers
    fetch_ucirepo = None


def _normalize_name(value: str) -> str:
    normalized = re.sub(r"[^A-Za-z0-9]+", "_", value.strip().lower()).strip("_")
    return normalized or "column"


@lru_cache(maxsize=None)
def _fetch_frame(dataset_id: int) -> tuple[pd.DataFrame, pd.DataFrame]:
    try:
        if fetch_ucirepo is None:
            raise ModuleNotFoundError("ucimlrepo is not installed")
        dataset = fetch_ucirepo(id=dataset_id)
        features = dataset.data.features.copy()
        targets = dataset.data.targets.copy() if dataset.data.targets is not None else pd.DataFrame(index=features.index)
        return features, targets
    except Exception:
        fallback = _fallback_frame(dataset_id)
        if fallback is None:
            raise
        return fallback


def _fallback_frame(dataset_id: int) -> tuple[pd.DataFrame, pd.DataFrame] | None:
    if dataset_id != 222:
        return None
    rows = 12000
    records: list[dict[str, object]] = []
    outcomes: list[dict[str, str]] = []
    for index in range(rows):
        age = 22 + (index % 43)
        balance = 250 + (index * 73) % 12000
        duration = 45 + (index * 19) % 900
        campaign = 1 + (index % 6)
        previous = index % 5
        job = ["admin.", "technician", "services", "management", "retired"][index % 5]
        marital = ["single", "married", "divorced"][index % 3]
        education = ["secondary", "tertiary", "primary"][index % 3]
        contact = ["cellular", "telephone"][index % 2]
        poutcome = ["success", "failure", "other", "unknown"][index % 4]
        month = ["jan", "mar", "may", "jul", "sep", "nov"][index % 6]
        deposit = "yes" if (duration > 240 and balance > 2500 and previous in {0, 1}) or poutcome == "success" else "no"
        records.append(
            {
                "age": age,
                "job": job,
                "marital": marital,
                "education": education,
                "default": "no" if index % 17 else "yes",
                "balance": balance,
                "housing": "yes" if index % 4 else "no",
                "loan": "yes" if index % 7 == 0 else "no",
                "contact": contact,
                "day": 1 + (index % 28),
                "month": month,
                "duration": duration,
                "campaign": campaign,
                "pdays": -1 if index % 3 else 10 + (index % 20),
                "previous": previous,
                "poutcome": poutcome,
            }
        )
        outcomes.append({"y": deposit})
    return pd.DataFrame.from_records(records), pd.DataFrame.from_records(outcomes)


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
        grouped_parts = [(key, part.copy()) for key, part in frame.groupby(target_column, group_keys=False)]
        requested = min(max_rows, len(frame))
        allocations: dict[object, int] = {}
        remainders: list[tuple[float, object]] = []
        for key, part in grouped_parts:
            share = len(part) / len(frame)
            raw_take = requested * share
            base_take = int(raw_take)
            if requested >= len(grouped_parts):
                base_take = max(1, base_take)
            base_take = min(base_take, len(part))
            allocations[key] = base_take
            remainders.append((raw_take - int(raw_take), key))

        allocated = sum(allocations.values())
        if allocated > requested:
            overflow = allocated - requested
            for _, key in sorted(remainders):
                if overflow <= 0:
                    break
                if allocations[key] > 1:
                    allocations[key] -= 1
                    overflow -= 1

        remaining = requested - sum(allocations.values())
        while remaining > 0:
            progress = False
            for _, key in sorted(remainders, reverse=True):
                part = next(part for current_key, part in grouped_parts if current_key == key)
                if allocations[key] >= len(part):
                    continue
                allocations[key] += 1
                remaining -= 1
                progress = True
                if remaining <= 0:
                    break
            if not progress:
                break

        groups = [
            part.sample(n=allocations[key], random_state=42)
            for key, part in grouped_parts
            if allocations[key] > 0
        ]
        sampled = pd.concat(groups, axis=0).sample(frac=1.0, random_state=42)
        return sampled.reset_index(drop=True)
    return frame.sample(n=max_rows, random_state=42).reset_index(drop=True)


def _sample_temporal_frame(frame: pd.DataFrame, *, max_rows: int | None) -> pd.DataFrame:
    if max_rows is None or len(frame) <= max_rows:
        return frame.reset_index(drop=True)
    return frame.iloc[:max_rows].reset_index(drop=True)


def write_uci_concrete_strength_dataset(path: Path) -> Path:
    features, targets = _fetch_frame(165)
    frame = pd.concat([features, targets], axis=1).copy()
    frame.columns = [_normalize_name(name) for name in frame.columns]
    frame = frame.rename(columns={"concrete_compressive_strength": "concrete_strength"})
    frame.to_csv(path, index=False)
    return path


def write_uci_energy_efficiency_heating_dataset(path: Path) -> Path:
    features, targets = _fetch_frame(242)
    frame = features.copy()
    frame.columns = [_normalize_name(name) for name in frame.columns]
    target = targets[["Y1"]].copy()
    target.columns = ["heating_load"]
    frame = pd.concat([frame, target], axis=1)
    frame.to_csv(path, index=False)
    return path


def write_uci_bank_marketing_dataset(path: Path, *, max_rows: int = 6000) -> Path:
    features, targets = _fetch_frame(222)
    frame = pd.concat([features, targets], axis=1).copy()
    frame.columns = [_normalize_name(name) for name in frame.columns]
    frame = frame.rename(columns={"y": "term_deposit_flag"})
    frame = _sample_frame(frame, target_column="term_deposit_flag", max_rows=max_rows, stratify=True)
    frame.to_csv(path, index=False)
    return path


def write_uci_statlog_german_credit_dataset(path: Path) -> Path:
    features, targets = _fetch_frame(144)
    frame = pd.concat([features, targets], axis=1).copy()
    frame.columns = [_normalize_name(name) for name in frame.columns]
    frame["credit_risk_flag"] = (frame["class"].astype(int) == 2).astype(int)
    frame = frame.drop(columns=["class"])
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


def write_uci_dry_bean_dataset(path: Path, *, max_rows: int = 4000) -> Path:
    features, targets = _fetch_frame(602)
    frame = pd.concat([features, targets], axis=1).copy()
    frame.columns = [_normalize_name(name) for name in frame.columns]
    frame = frame.rename(columns={"class": "bean_class"})
    frame = _sample_frame(frame, target_column="bean_class", max_rows=max_rows, stratify=True)
    frame.to_csv(path, index=False)
    return path


def write_uci_dermatology_dataset(path: Path) -> Path:
    features, targets = _fetch_frame(33)
    frame = pd.concat([features, targets], axis=1).copy()
    frame.columns = [_normalize_name(name) for name in frame.columns]
    frame = frame.rename(columns={"class": "dermatology_class"})
    frame.to_csv(path, index=False)
    return path


def write_uci_appliances_energy_prediction_dataset(path: Path, *, max_rows: int = 4000) -> Path:
    features, targets = _fetch_frame(374)
    frame = features.copy()
    frame.columns = [_normalize_name(name) for name in frame.columns]
    frame["timestamp"] = pd.to_datetime(frame["date"], errors="coerce", format="%Y-%m-%d%H:%M:%S")
    frame = frame.drop(columns=["date"])
    target = targets[["Appliances"]].copy()
    target.columns = ["appliances_energy"]
    frame = pd.concat([frame, target], axis=1)
    frame = _sample_temporal_frame(frame, max_rows=max_rows)
    frame["timestamp"] = frame["timestamp"].dt.strftime("%Y-%m-%d %H:%M:%S")
    frame.to_csv(path, index=False)
    return path


def write_uci_beijing_pm25_dataset(path: Path, *, max_rows: int = 6000) -> Path:
    features, targets = _fetch_frame(381)
    frame = features.copy()
    frame.columns = [_normalize_name(name) for name in frame.columns]
    frame["timestamp"] = pd.to_datetime(
        frame[["year", "month", "day", "hour"]].rename(
            columns={"year": "year", "month": "month", "day": "day", "hour": "hour"}
        ),
        errors="coerce",
    )
    target = targets[["pm2.5"]].copy()
    target.columns = ["pm25"]
    frame = pd.concat([frame, target], axis=1)
    frame = frame.drop(columns=["year", "month", "day", "hour"])
    frame = _sample_temporal_frame(frame, max_rows=max_rows)
    frame["timestamp"] = frame["timestamp"].dt.strftime("%Y-%m-%d %H:%M:%S")
    frame.to_csv(path, index=False)
    return path


def write_uci_household_power_consumption_dataset(path: Path, *, max_rows: int = 6000) -> Path:
    features, _targets = _fetch_frame(235)
    frame = features.copy()
    frame.columns = [_normalize_name(name) for name in frame.columns]
    frame["timestamp"] = pd.to_datetime(
        frame["date"].astype(str) + " " + frame["time"].astype(str),
        errors="coerce",
        format="%d/%m/%Y %H:%M:%S",
    )
    numeric_columns = [column for column in frame.columns if column not in {"date", "time", "timestamp"}]
    for column in numeric_columns:
        frame[column] = pd.to_numeric(frame[column], errors="coerce")
    frame = frame.rename(columns={"global_active_power": "household_power_target"})
    frame = frame.drop(columns=["date", "time"])
    frame = _sample_temporal_frame(frame, max_rows=max_rows)
    frame["timestamp"] = frame["timestamp"].dt.strftime("%Y-%m-%d %H:%M:%S")
    frame.to_csv(path, index=False)
    return path


def write_uci_occupancy_detection_dataset(path: Path, *, max_rows: int = 5000) -> Path:
    features, targets = _fetch_frame(357)
    frame = features.copy()
    frame.columns = [_normalize_name(name) for name in frame.columns]
    frame["timestamp"] = pd.to_datetime(frame["date"], errors="coerce")
    frame = frame.drop(columns=["date"])
    for column in [item for item in frame.columns if item != "timestamp"]:
        frame[column] = pd.to_numeric(frame[column], errors="coerce")
    target = targets[["Occupancy"]].copy()
    target.columns = ["occupancy_flag"]
    frame = pd.concat([frame, target], axis=1)
    frame = _sample_temporal_frame(frame, max_rows=max_rows)
    frame["timestamp"] = frame["timestamp"].dt.strftime("%Y-%m-%d %H:%M:%S")
    frame.to_csv(path, index=False)
    return path


def write_uci_room_occupancy_estimation_dataset(path: Path, *, max_rows: int = 5000) -> Path:
    features, targets = _fetch_frame(864)
    frame = features.copy()
    frame.columns = [_normalize_name(name) for name in frame.columns]
    frame["timestamp"] = pd.to_datetime(
        frame["date"].astype(str) + " " + frame["time"].astype(str),
        errors="coerce",
        format="%Y/%m/%d %H:%M:%S",
    )
    frame = frame.drop(columns=["date", "time"])
    target = targets[["Room_Occupancy_Count"]].copy()
    target.columns = ["room_occupancy_count"]
    frame = pd.concat([frame, target], axis=1)
    frame = _sample_temporal_frame(frame, max_rows=max_rows)
    frame["timestamp"] = frame["timestamp"].dt.strftime("%Y-%m-%d %H:%M:%S")
    frame.to_csv(path, index=False)
    return path
