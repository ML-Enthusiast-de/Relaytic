"""Split-safe feature preparation with lightweight categorical and engineered features."""

from __future__ import annotations

from itertools import combinations
from typing import Any

import numpy as np
import pandas as pd

from relaytic.analytics.task_detection import is_classification_task


_CATEGORICAL_MISSING_TOKEN = "__missing__"
_CATEGORICAL_OTHER_TOKEN = "__other__"
_MAX_CATEGORICAL_LEVELS = 8
_MAX_INTERACTION_BASES = 3


def prepare_split_safe_feature_frames(
    *,
    split_frames: dict[str, pd.DataFrame],
    raw_feature_columns: list[str],
    target_column: str,
    missing_data_strategy: str,
    fill_constant_value: float | None,
    task_type: str,
) -> dict[str, Any]:
    """Prepare split-safe train/validation/test frames with engineered numeric features."""
    ordered_raw_features = [str(item) for item in raw_feature_columns if str(item).strip()]
    if not ordered_raw_features:
        raise ValueError("raw_feature_columns cannot be empty.")

    train_source = split_frames["train"]
    numeric_raw_features, categorical_raw_features = _infer_raw_feature_types(
        frame=train_source,
        raw_feature_columns=ordered_raw_features,
    )
    indicator_features = _missing_indicator_features(
        frame=train_source,
        raw_feature_columns=ordered_raw_features,
    )
    strategy = str(missing_data_strategy).strip().lower() or "fill_median"
    train_only_numeric_fill = _numeric_fill_values(
        frame=train_source,
        numeric_raw_features=numeric_raw_features,
        strategy=strategy,
        fill_constant_value=fill_constant_value,
    )
    categorical_levels, deferred_categorical_features = _categorical_level_map(
        frame=train_source,
        categorical_raw_features=categorical_raw_features,
    )

    prepared_raw_frames: dict[str, pd.DataFrame] = {}
    for name, frame in split_frames.items():
        prepared_raw_frames[name] = _prepare_raw_frame(
            frame=frame,
            raw_feature_columns=ordered_raw_features,
            target_column=target_column,
            numeric_raw_features=numeric_raw_features,
            categorical_raw_features=categorical_raw_features,
            strategy=strategy,
            numeric_fill_values=train_only_numeric_fill,
            task_type=task_type,
        )

    interaction_pairs = _interaction_pairs(
        train_frame=prepared_raw_frames["train"],
        numeric_raw_features=numeric_raw_features,
        target_column=target_column,
        task_type=task_type,
    )
    transformed_frames = {
        name: _transform_frame(
            frame=frame,
            target_column=target_column,
            numeric_raw_features=numeric_raw_features,
            categorical_levels=categorical_levels,
            indicator_features=indicator_features,
            interaction_pairs=interaction_pairs,
        )
        for name, frame in prepared_raw_frames.items()
    }
    model_feature_columns = _model_feature_columns(
        numeric_raw_features=numeric_raw_features,
        categorical_levels=categorical_levels,
        indicator_features=indicator_features,
        interaction_pairs=interaction_pairs,
    )
    for name, frame in transformed_frames.items():
        transformed_frames[name] = frame.dropna(subset=model_feature_columns).reset_index(drop=True)
    _validate_prepared_frames(
        frames=transformed_frames,
        target_column=target_column,
        task_type=task_type,
    )

    effective_strategy = {
        "fill_median": "fill_median_train_only",
        "median": "fill_median_train_only",
        "fill_constant": "fill_constant_train_policy",
        "constant": "fill_constant_train_policy",
        "keep": "keep_requested_drop_remaining_for_model",
        "drop_rows": "keep_requested_drop_remaining_for_model",
    }.get(strategy, "keep_requested_drop_remaining_for_model")

    return {
        "frames": transformed_frames,
        "raw_frames": prepared_raw_frames,
        "raw_feature_columns": ordered_raw_features,
        "model_feature_columns": model_feature_columns,
        "preprocessing": {
            "missing_data_strategy_requested": strategy,
            "missing_data_strategy_effective": effective_strategy,
            "fill_values": dict(train_only_numeric_fill),
            "categorical_fill_token": _CATEGORICAL_MISSING_TOKEN,
            "rows_after": {name: int(part.shape[0]) for name, part in transformed_frames.items()},
            "raw_feature_columns": list(ordered_raw_features),
            "model_feature_columns": list(model_feature_columns),
            "numeric_raw_features": list(numeric_raw_features),
            "categorical_raw_features": list(categorical_raw_features),
            "categorical_levels": {key: list(value) for key, value in categorical_levels.items()},
            "deferred_categorical_features": list(deferred_categorical_features),
            "missing_indicator_features": list(indicator_features),
            "interaction_pairs": [list(item) for item in interaction_pairs],
            "feature_engineering_summary": {
                "numeric_raw_feature_count": len(numeric_raw_features),
                "categorical_raw_feature_count": len(categorical_levels),
                "deferred_categorical_feature_count": len(deferred_categorical_features),
                "missing_indicator_count": len(indicator_features),
                "interaction_count": len(interaction_pairs),
                "engineered_feature_count": max(0, len(model_feature_columns) - len(ordered_raw_features)),
            },
        },
    }


def prepare_inference_feature_frame(
    *,
    frame: pd.DataFrame,
    target_column: str,
    preprocessing: dict[str, Any],
    task_type: str,
) -> dict[str, Any]:
    """Prepare one inference frame using saved preprocessing metadata."""
    raw_feature_columns = _string_list(preprocessing.get("raw_feature_columns"))
    numeric_raw_features = _string_list(preprocessing.get("numeric_raw_features"))
    categorical_raw_features = _string_list(preprocessing.get("categorical_raw_features"))
    categorical_levels = {
        str(key): _string_list(value)
        for key, value in dict(preprocessing.get("categorical_levels", {})).items()
    }
    indicator_features = _string_list(preprocessing.get("missing_indicator_features"))
    interaction_pairs = [
        tuple(str(item) for item in pair[:2])
        for pair in list(preprocessing.get("interaction_pairs", []))
        if isinstance(pair, list) and len(pair) >= 2
    ]
    strategy = str(preprocessing.get("missing_data_strategy_requested", "keep")).strip().lower() or "keep"
    fill_values = {
        str(key): float(value)
        for key, value in dict(preprocessing.get("fill_values", {})).items()
        if _is_number(value)
    }
    working = frame.copy()
    working["__source_row"] = np.arange(len(working), dtype=int)
    prepared_raw = _prepare_raw_frame(
        frame=working,
        raw_feature_columns=raw_feature_columns,
        target_column=target_column,
        numeric_raw_features=numeric_raw_features,
        categorical_raw_features=categorical_raw_features,
        strategy=strategy,
        numeric_fill_values=fill_values,
        task_type=task_type,
        keep_source_row=True,
    )
    transformed = _transform_frame(
        frame=prepared_raw,
        target_column=target_column,
        numeric_raw_features=numeric_raw_features,
        categorical_levels=categorical_levels,
        indicator_features=indicator_features,
        interaction_pairs=interaction_pairs,
        keep_source_row=True,
    )
    model_feature_columns = _string_list(preprocessing.get("model_feature_columns"))
    before = int(len(transformed))
    transformed = transformed.dropna(subset=model_feature_columns).reset_index(drop=True)
    prepared_raw = (
        prepared_raw.set_index("__source_row")
        .loc[transformed["__source_row"].tolist()]
        .reset_index()
    )
    dropped_rows = before - int(len(transformed))
    if transformed.empty:
        raise ValueError("No usable rows left for inference after preprocessing and feature engineering.")
    return {
        "frame": transformed,
        "raw_frame": prepared_raw,
        "model_feature_columns": model_feature_columns,
        "dropped_rows": dropped_rows,
    }


def _infer_raw_feature_types(*, frame: pd.DataFrame, raw_feature_columns: list[str]) -> tuple[list[str], list[str]]:
    numeric_raw_features: list[str] = []
    categorical_raw_features: list[str] = []
    for column in raw_feature_columns:
        series = frame[column] if column in frame.columns else pd.Series(dtype=object)
        numeric = pd.to_numeric(series, errors="coerce")
        numeric_ratio = float(numeric.notna().mean()) if len(series) else 0.0
        lowered = {str(item).strip().lower() for item in series.dropna().tolist()}
        bool_like = bool(lowered) and lowered.issubset({"0", "1", "true", "false", "yes", "no", "y", "n"})
        if bool_like or numeric_ratio >= 0.90:
            numeric_raw_features.append(column)
        else:
            categorical_raw_features.append(column)
    return numeric_raw_features, categorical_raw_features


def _missing_indicator_features(*, frame: pd.DataFrame, raw_feature_columns: list[str]) -> list[str]:
    selected: list[str] = []
    for column in raw_feature_columns:
        if column not in frame.columns:
            continue
        missing_fraction = float(frame[column].isna().mean()) if len(frame) else 0.0
        if missing_fraction > 0.0:
            selected.append(column)
    return selected


def _numeric_fill_values(
    *,
    frame: pd.DataFrame,
    numeric_raw_features: list[str],
    strategy: str,
    fill_constant_value: float | None,
) -> dict[str, float]:
    fill_values: dict[str, float] = {}
    if strategy in {"fill_constant", "constant"}:
        constant = 0.0 if fill_constant_value is None else float(fill_constant_value)
        for column in numeric_raw_features:
            fill_values[column] = constant
        return fill_values
    for column in numeric_raw_features:
        numeric = pd.to_numeric(frame[column], errors="coerce")
        fill_values[column] = float(numeric.median()) if numeric.notna().any() else 0.0
    return fill_values


def _categorical_level_map(
    *,
    frame: pd.DataFrame,
    categorical_raw_features: list[str],
) -> tuple[dict[str, list[str]], list[str]]:
    levels: dict[str, list[str]] = {}
    deferred: list[str] = []
    for column in categorical_raw_features:
        tokens = frame[column].where(frame[column].notna(), _CATEGORICAL_MISSING_TOKEN).map(_normalize_token)
        counts = tokens.value_counts(dropna=False)
        unique_count = int(counts.shape[0])
        if unique_count <= 1:
            continue
        if unique_count <= _MAX_CATEGORICAL_LEVELS:
            levels[column] = sorted(str(index) for index in counts.index.tolist())
            continue
        top_levels = [str(index) for index in counts.index.tolist()[: _MAX_CATEGORICAL_LEVELS - 1]]
        if not top_levels:
            deferred.append(column)
            continue
        levels[column] = sorted(top_levels + [_CATEGORICAL_OTHER_TOKEN])
        deferred.append(column)
    return levels, deferred


def _prepare_raw_frame(
    *,
    frame: pd.DataFrame,
    raw_feature_columns: list[str],
    target_column: str,
    numeric_raw_features: list[str],
    categorical_raw_features: list[str],
    strategy: str,
    numeric_fill_values: dict[str, float],
    task_type: str,
    keep_source_row: bool = False,
) -> pd.DataFrame:
    required = list(raw_feature_columns)
    if target_column in frame.columns:
        required.append(target_column)
    if keep_source_row and "__source_row" in frame.columns:
        required.append("__source_row")
    subset = frame[required].copy()
    for column in raw_feature_columns:
        subset[_raw_missing_flag_name(column)] = subset[column].isna().astype(float)
    if target_column in subset.columns:
        if is_classification_task(task_type):
            target = subset[target_column].where(subset[target_column].notna(), None)
            subset[target_column] = target.map(lambda value: None if value is None else str(value).strip())
            subset = subset[(subset[target_column].notna()) & (subset[target_column] != "")].reset_index(drop=True)
        else:
            subset[target_column] = pd.to_numeric(subset[target_column], errors="coerce")
            subset = subset.dropna(subset=[target_column]).reset_index(drop=True)
    for column in numeric_raw_features:
        subset[column] = pd.to_numeric(subset[column], errors="coerce")
    for column in categorical_raw_features:
        subset[column] = subset[column].where(subset[column].notna(), _CATEGORICAL_MISSING_TOKEN).map(_normalize_token)

    if strategy in {"fill_median", "median", "fill_constant", "constant"}:
        for column in numeric_raw_features:
            subset[column] = subset[column].fillna(float(numeric_fill_values.get(column, 0.0)))
        for column in categorical_raw_features:
            subset[column] = subset[column].fillna(_CATEGORICAL_MISSING_TOKEN)
    else:
        subset = subset.dropna(subset=numeric_raw_features).reset_index(drop=True)
        for column in categorical_raw_features:
            subset = subset[subset[column].notna()].reset_index(drop=True)
    return subset


def _interaction_pairs(
    *,
    train_frame: pd.DataFrame,
    numeric_raw_features: list[str],
    target_column: str,
    task_type: str,
) -> list[tuple[str, str]]:
    if len(numeric_raw_features) < 2 or len(train_frame) < 20:
        return []
    scored: list[tuple[float, str]] = []
    for column in numeric_raw_features:
        values = pd.to_numeric(train_frame[column], errors="coerce")
        if not values.notna().any():
            continue
        score = _association_score(
            values=values.to_numpy(dtype=float),
            target=train_frame[target_column],
            task_type=task_type,
        )
        scored.append((score, column))
    scored.sort(key=lambda item: (-item[0], item[1]))
    base = [column for _, column in scored[:_MAX_INTERACTION_BASES]]
    return [tuple(pair) for pair in combinations(base, 2)]


def _association_score(*, values: np.ndarray, target: pd.Series, task_type: str) -> float:
    if values.size == 0:
        return 0.0
    if is_classification_task(task_type):
        labels = target.astype(str)
        global_mean = float(np.mean(values))
        score = 0.0
        for token in sorted(labels.unique().tolist()):
            mask = labels == token
            if not bool(mask.any()):
                continue
            weight = float(mask.mean())
            score += weight * abs(float(np.mean(values[mask.to_numpy()])) - global_mean)
        return score
    numeric_target = pd.to_numeric(target, errors="coerce").to_numpy(dtype=float)
    if numeric_target.size != values.size:
        return 0.0
    if np.std(values) <= 1e-12 or np.std(numeric_target) <= 1e-12:
        return 0.0
    corr = np.corrcoef(values, numeric_target)[0, 1]
    if not np.isfinite(corr):
        return 0.0
    return abs(float(corr))


def _transform_frame(
    *,
    frame: pd.DataFrame,
    target_column: str,
    numeric_raw_features: list[str],
    categorical_levels: dict[str, list[str]],
    indicator_features: list[str],
    interaction_pairs: list[tuple[str, str]],
    keep_source_row: bool = False,
) -> pd.DataFrame:
    transformed = pd.DataFrame(index=frame.index)
    if keep_source_row and "__source_row" in frame.columns:
        transformed["__source_row"] = frame["__source_row"].astype(int)
    if target_column in frame.columns:
        transformed[target_column] = frame[target_column]
    for column in numeric_raw_features:
        transformed[column] = pd.to_numeric(frame[column], errors="coerce").astype(float)
    for column in indicator_features:
        raw_flag = _raw_missing_flag_name(column)
        if raw_flag in frame.columns:
            transformed[_missing_indicator_name(column)] = pd.to_numeric(
                frame[raw_flag], errors="coerce"
            ).fillna(0.0).astype(float)
        else:
            transformed[_missing_indicator_name(column)] = (
                frame[column].isna() | (frame[column].astype(str) == _CATEGORICAL_MISSING_TOKEN)
            ).astype(float)
    for column, levels in categorical_levels.items():
        mapped = frame[column].map(_normalize_token)
        if _CATEGORICAL_OTHER_TOKEN in levels:
            allowed = {level for level in levels if level != _CATEGORICAL_OTHER_TOKEN}
            mapped = mapped.where(mapped.isin(allowed), _CATEGORICAL_OTHER_TOKEN)
        for level in levels:
            transformed[_categorical_feature_name(column, level)] = (mapped == level).astype(float)
    for left, right in interaction_pairs:
        transformed[_interaction_feature_name(left, right)] = (
            pd.to_numeric(frame[left], errors="coerce").astype(float)
            * pd.to_numeric(frame[right], errors="coerce").astype(float)
        )
    return transformed


def _model_feature_columns(
    *,
    numeric_raw_features: list[str],
    categorical_levels: dict[str, list[str]],
    indicator_features: list[str],
    interaction_pairs: list[tuple[str, str]],
) -> list[str]:
    columns: list[str] = list(numeric_raw_features)
    columns.extend(_missing_indicator_name(column) for column in indicator_features)
    for column in sorted(categorical_levels):
        for level in categorical_levels[column]:
            columns.append(_categorical_feature_name(column, level))
    for left, right in interaction_pairs:
        columns.append(_interaction_feature_name(left, right))
    return columns


def _validate_prepared_frames(
    *,
    frames: dict[str, pd.DataFrame],
    target_column: str,
    task_type: str,
) -> None:
    if frames["train"].shape[0] < 6 or frames["validation"].shape[0] < 2 or frames["test"].shape[0] < 2:
        raise ValueError(
            "Split-safe preprocessing left too few rows in one or more splits. Reduce missingness, change strategy, or use more data."
        )
    if is_classification_task(task_type):
        train_labels = {str(item) for item in frames["train"][target_column]}
        unseen = set()
        for part_name in ("validation", "test"):
            unseen |= {
                str(item)
                for item in frames[part_name][target_column]
                if str(item) not in train_labels
            }
        if unseen:
            raise ValueError(
                "Split-safe classification preprocessing produced labels in validation/test that were not present in the training split. Collect more examples per class."
            )


def _categorical_feature_name(column: str, level: str) -> str:
    return f"cat__{_slug(column)}__{_slug(level)}"


def _missing_indicator_name(column: str) -> str:
    return f"miss__{_slug(column)}"


def _raw_missing_flag_name(column: str) -> str:
    return f"__raw_missing__{_slug(column)}"


def _interaction_feature_name(left: str, right: str) -> str:
    return f"int__{_slug(left)}__x__{_slug(right)}"


def _normalize_token(value: Any) -> str:
    text = str(value if value is not None else _CATEGORICAL_MISSING_TOKEN).strip()
    return text if text else _CATEGORICAL_MISSING_TOKEN


def _slug(value: str) -> str:
    normalized = []
    for char in str(value):
        if char.isalnum():
            normalized.append(char.lower())
        else:
            normalized.append("_")
    out = "".join(normalized).strip("_")
    while "__" in out:
        out = out.replace("__", "_")
    return out or "feature"


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item).strip() for item in value if str(item).strip()]


def _is_number(value: Any) -> bool:
    try:
        float(value)
    except (TypeError, ValueError):
        return False
    return True
