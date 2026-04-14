"""Split-safe training and model comparison helpers for Agent 2."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import json
import math
from pathlib import Path
import time
from typing import Any

import numpy as np
import pandas as pd

from relaytic.analytics.task_detection import assess_task_profile, is_classification_task
from relaytic.core.json_utils import write_json
from relaytic.persistence.artifact_store import ArtifactStore
from .baselines import IncrementalLinearSurrogate
from .calibration import (
    apply_binary_platt_calibrator,
    fit_binary_platt_calibrator,
    fit_regression_residual_interval,
)
from .checkpoints import ModelCheckpointStore
from .classifiers import (
    BaggedTreeClassifierSurrogate,
    BoostedTreeClassifierSurrogate,
    LogisticClassificationSurrogate,
)
from .estimator_adapters import (
    build_classification_estimator_surrogate,
    build_classification_estimator_variants,
    build_regression_estimator_surrogate,
    build_regression_estimator_variants,
    family_adapter_available,
)
from .evaluation import classification_metrics, regression_metrics
from .feature_pipeline import prepare_split_safe_feature_frames
from .hpo_loop import (
    EARLY_STOPPING_REPORT_SCHEMA_VERSION,
    SEARCH_LOOP_SCORECARD_SCHEMA_VERSION,
    THRESHOLD_TUNING_REPORT_SCHEMA_VERSION,
    TRIAL_LEDGER_RECORD_SCHEMA_VERSION,
    WARM_START_TRANSFER_REPORT_SCHEMA_VERSION,
    artifact_path as hpo_artifact_path,
    build_architecture_search_space,
    build_portfolio_search_plan,
    build_trial_plans,
    derive_hpo_budget_contract,
    load_warm_start_state,
)
from .normalization import MinMaxNormalizer
from .performance_feedback import analyze_model_performance
from .splitters import DatasetSplit, build_train_validation_test_split


@dataclass(frozen=True)
class CandidateMetrics:
    """Train/validation/test metrics for one candidate model."""

    model_family: str
    train_metrics: dict[str, float]
    validation_metrics: dict[str, float]
    test_metrics: dict[str, float]
    notes: str
    variant_id: str | None = None
    hyperparameters: dict[str, Any] | None = None
    calibration: dict[str, Any] | None = None
    uncertainty: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


_MODEL_TIEBREAK = {
    "linear_ridge": 0,
    "lagged_linear": 1,
    "bagged_tree_ensemble": 2,
    "boosted_tree_ensemble": 3,
    "hist_gradient_boosting_ensemble": 4,
    "extra_trees_ensemble": 5,
    "catboost_ensemble": 6,
    "xgboost_ensemble": 7,
    "lightgbm_ensemble": 8,
    "lagged_tree_ensemble": 9,
    "logistic_regression": 0,
    "lagged_logistic_regression": 1,
    "bagged_tree_classifier": 2,
    "boosted_tree_classifier": 3,
    "hist_gradient_boosting_classifier": 4,
    "extra_trees_classifier": 5,
    "catboost_classifier": 6,
    "xgboost_classifier": 7,
    "lightgbm_classifier": 8,
    "tabpfn_classifier": 9,
    "lagged_tree_classifier": 10,
}


_REGRESSION_ADAPTER_FAMILIES = {
    "hist_gradient_boosting_ensemble",
    "extra_trees_ensemble",
    "catboost_ensemble",
    "xgboost_ensemble",
    "lightgbm_ensemble",
}

_CLASSIFICATION_ADAPTER_FAMILIES = {
    "hist_gradient_boosting_classifier",
    "extra_trees_classifier",
    "catboost_classifier",
    "xgboost_classifier",
    "lightgbm_classifier",
    "tabpfn_classifier",
}


def _ordered_available_hpo_families(
    *,
    preferred_candidate_order: list[str] | None,
    candidate_pool: list[str],
) -> list[str]:
    ordered: list[str] = []
    for family in list(preferred_candidate_order or []) + list(candidate_pool):
        normalized = str(family).strip()
        if not normalized or normalized in ordered:
            continue
        if normalized not in candidate_pool:
            continue
        if not family_adapter_available(normalized):
            continue
        ordered.append(normalized)
    return ordered


def normalize_candidate_model_family(requested_model_family: str) -> str | None:
    """Normalize user-facing model names to implemented candidate identifiers."""
    normalized = requested_model_family.strip().lower().replace("-", "_")
    aliases = {
        "": "auto",
        "auto": "auto",
        "recommended": "auto",
        "linear_ridge": "linear_ridge",
        "ridge": "linear_ridge",
        "linear": "linear_ridge",
        "incremental_linear_surrogate": "linear_ridge",
        "logistic_regression": "logistic_regression",
        "logistic": "logistic_regression",
        "logit": "logistic_regression",
        "linear_classifier": "logistic_regression",
        "classifier": "logistic_regression",
        "lagged_logistic_regression": "lagged_logistic_regression",
        "lagged_logistic": "lagged_logistic_regression",
        "lagged_logit": "lagged_logistic_regression",
        "temporal_logistic": "lagged_logistic_regression",
        "temporal_classifier": "lagged_logistic_regression",
        "lagged_classifier": "lagged_logistic_regression",
        "lagged_linear": "lagged_linear",
        "lagged": "lagged_linear",
        "temporal_linear": "lagged_linear",
        "arx": "lagged_linear",
        "bagged_tree_classifier": "bagged_tree_classifier",
        "tree_classifier": "bagged_tree_classifier",
        "classifier_tree": "bagged_tree_classifier",
        "fraud_tree": "bagged_tree_classifier",
        "lagged_tree_classifier": "lagged_tree_classifier",
        "temporal_tree_classifier": "lagged_tree_classifier",
        "lag_window_tree_classifier": "lagged_tree_classifier",
        "temporal_fraud_tree": "lagged_tree_classifier",
        "lagged_tree_ensemble": "lagged_tree_ensemble",
        "lagged_tree": "lagged_tree_ensemble",
        "lag_window_tree": "lagged_tree_ensemble",
        "temporal_tree": "lagged_tree_ensemble",
        "temporal_tree_ensemble": "lagged_tree_ensemble",
        "bagged_tree_ensemble": "bagged_tree_ensemble",
        "tree_ensemble": "bagged_tree_ensemble",
        "tree_ensemble_candidate": "bagged_tree_ensemble",
        "tree": "bagged_tree_ensemble",
        "extra_trees": "extra_trees_ensemble",
        "extra_trees_ensemble": "extra_trees_ensemble",
        "boosted_tree_ensemble": "boosted_tree_ensemble",
        "boosted_tree": "boosted_tree_ensemble",
        "gradient_boosting": "boosted_tree_ensemble",
        "hist_gradient_boosting": "hist_gradient_boosting_ensemble",
        "hist_gradient_boosting_ensemble": "hist_gradient_boosting_ensemble",
        "gbdt": "boosted_tree_ensemble",
        "catboost": "catboost_ensemble",
        "catboost_ensemble": "catboost_ensemble",
        "xgboost": "xgboost_ensemble",
        "xgboost_ensemble": "xgboost_ensemble",
        "lightgbm": "lightgbm_ensemble",
        "lightgbm_ensemble": "lightgbm_ensemble",
        "boosted_tree_classifier": "boosted_tree_classifier",
        "gradient_boosting_classifier": "boosted_tree_classifier",
        "hist_gradient_boosting_classifier": "hist_gradient_boosting_classifier",
        "extra_trees_classifier": "extra_trees_classifier",
        "catboost_classifier": "catboost_classifier",
        "xgboost_classifier": "xgboost_classifier",
        "lightgbm_classifier": "lightgbm_classifier",
        "tabpfn": "tabpfn_classifier",
        "tabpfn_classifier": "tabpfn_classifier",
        "gbdt_classifier": "boosted_tree_classifier",
    }
    return aliases.get(normalized)


def train_surrogate_candidates(
    *,
    frame: pd.DataFrame,
    target_column: str,
    feature_columns: list[str],
    requested_model_family: str,
    timestamp_column: str | None = None,
    normalize: bool = True,
    missing_data_strategy: str = "fill_median",
    fill_constant_value: float | None = None,
    compare_against_baseline: bool = True,
    lag_horizon_samples: int | None = None,
    threshold_policy: str | None = None,
    decision_threshold: float | None = None,
    task_type: str | None = None,
    run_id: str | None = None,
    checkpoint_tag: str | None = None,
    data_references: list[str] | None = None,
    selection_metric: str | None = None,
    preferred_candidate_order: list[str] | None = None,
    output_run_dir: str | Path | None = None,
    checkpoint_base_dir: str | Path | None = None,
) -> dict[str, Any]:
    """Train a split-safe linear baseline and optional nonlinear comparator."""
    if not feature_columns:
        raise ValueError("feature_columns cannot be empty.")
    _require_columns(frame, list(feature_columns) + [target_column])

    data_mode = _infer_data_mode(frame=frame, timestamp_column=timestamp_column)
    task_profile = assess_task_profile(
        frame=frame,
        target_column=target_column,
        data_mode=data_mode,
        task_type_hint=task_type,
    )
    split = build_train_validation_test_split(
        n_rows=len(frame),
        data_mode=data_mode,
        task_type=task_profile.task_type,
        stratify_labels=frame[target_column] if is_classification_task(task_profile.task_type) else None,
    )
    requested = normalize_candidate_model_family(requested_model_family)
    if requested is None:
        raise ValueError(
            "Requested model is not implemented. "
            "Supported: auto, linear_ridge/ridge/linear, logistic_regression/logistic/linear_classifier, "
            "lagged_logistic_regression/lagged_logistic/temporal_classifier, "
            "lagged_linear/lagged/temporal_linear/arx, "
            "lagged_tree_classifier/temporal_tree_classifier, "
            "lagged_tree_ensemble/lagged_tree/lag_window_tree/temporal_tree, "
            "bagged_tree_ensemble/tree/tree_ensemble, extra_trees/extra_trees_ensemble, "
            "boosted_tree_ensemble/gradient_boosting, hist_gradient_boosting/hist_gradient_boosting_ensemble, "
            "bagged_tree_classifier/tree_classifier/classifier_tree, "
            "boosted_tree_classifier/gradient_boosting_classifier, "
            "hist_gradient_boosting_classifier, extra_trees_classifier, "
            "catboost/catboost_classifier, xgboost/xgboost_classifier, lightgbm/lightgbm_classifier, "
            "tabpfn/tabpfn_classifier."
        )
    requested = _resolve_requested_for_task(
        requested=requested,
        task_type=task_profile.task_type,
    )
    if is_classification_task(task_profile.task_type):
        return _train_classification_candidates(
            frame=frame,
            target_column=target_column,
            feature_columns=feature_columns,
            requested=requested,
            normalize=normalize,
            missing_data_strategy=missing_data_strategy,
            fill_constant_value=fill_constant_value,
            compare_against_baseline=compare_against_baseline,
            lag_horizon_samples=lag_horizon_samples,
            split=split,
            task_profile=task_profile,
            threshold_policy=threshold_policy,
            decision_threshold=decision_threshold,
            run_id=run_id,
            checkpoint_tag=checkpoint_tag,
            data_references=data_references,
            selection_metric=selection_metric,
            preferred_candidate_order=preferred_candidate_order,
            output_run_dir=output_run_dir,
            checkpoint_base_dir=checkpoint_base_dir,
        )
    split_frames = {
        "train": frame.iloc[split.train_indices].reset_index(drop=True),
        "validation": frame.iloc[split.validation_indices].reset_index(drop=True),
        "test": frame.iloc[split.test_indices].reset_index(drop=True),
    }
    prepared = _prepare_split_safe_frames(
        split_frames=split_frames,
        feature_columns=feature_columns,
        target_column=target_column,
        missing_data_strategy=missing_data_strategy,
        fill_constant_value=fill_constant_value,
        task_type=task_profile.task_type,
    )
    prepared_frames = prepared["frames"]
    preprocessing = prepared["preprocessing"]
    model_feature_columns = [str(item) for item in prepared.get("model_feature_columns", []) if str(item).strip()]
    if not model_feature_columns:
        model_feature_columns = list(feature_columns)

    normalizer: MinMaxNormalizer | None = None
    if normalize:
        normalizer = MinMaxNormalizer()
        normalizer.fit(prepared_frames["train"], feature_columns=model_feature_columns)
        prepared_frames = {
            name: normalizer.transform_features(part)
            for name, part in prepared_frames.items()
        }

    artifact_store = ArtifactStore()
    if output_run_dir is not None:
        run_dir = Path(output_run_dir)
        run_dir.mkdir(parents=True, exist_ok=True)
    else:
        run_dir = artifact_store.create_run_dir(run_id=run_id)

    regression_hpo_family_pool: list[str] = ["linear_ridge"]
    if compare_against_baseline or requested == "bagged_tree_ensemble":
        regression_hpo_family_pool.append("bagged_tree_ensemble")
    if compare_against_baseline or requested == "boosted_tree_ensemble":
        regression_hpo_family_pool.append("boosted_tree_ensemble")
    if compare_against_baseline or requested in _REGRESSION_ADAPTER_FAMILIES:
        regression_hpo_family_pool.extend(
            [
                family
                for family in [
                    "hist_gradient_boosting_ensemble",
                    "extra_trees_ensemble",
                    "catboost_ensemble",
                    "xgboost_ensemble",
                    "lightgbm_ensemble",
                ]
                if compare_against_baseline or requested == family
            ]
        )
    regression_hpo_families = _ordered_available_hpo_families(
        preferred_candidate_order=preferred_candidate_order,
        candidate_pool=regression_hpo_family_pool,
    )
    hpo_context = _prepare_hpo_context(
        run_dir=run_dir,
        task_type=task_profile.task_type,
        row_count=len(frame),
        requested_family=requested,
        preferred_candidate_order=preferred_candidate_order,
        available_families=regression_hpo_families,
    )

    rows_used_by_model: dict[str, int] = {}
    candidate_records: list[dict[str, Any]] = []
    linear_candidates = _fit_regression_linear_candidates(
        frames=prepared_frames,
        model_feature_columns=model_feature_columns,
        target_column=target_column,
        hpo_context=hpo_context,
        task_type=task_profile.task_type,
        selection_metric=selection_metric,
    )
    for record in linear_candidates:
        rows_used_by_model["linear_ridge"] = int(record["rows_used"])
        candidate_records.append(record)
    lagged_model: LaggedLinearSurrogate | None = None
    lagged_horizon = _resolve_lag_horizon(
        data_mode=data_mode,
        requested=requested,
        lag_horizon_samples=lag_horizon_samples,
        split=split,
    )
    if requested in {"lagged_linear", "lagged_tree_ensemble"} and lagged_horizon is None:
        raise ValueError(
            "Lagged model families require time-series structure and a usable timestamp column."
        )
    if lagged_horizon is not None and (compare_against_baseline or requested == "lagged_linear"):
        lagged_model = LaggedLinearSurrogate(
            feature_columns=model_feature_columns,
            target_column=target_column,
            lag_horizon=lagged_horizon,
        )
        lagged_rows_used = lagged_model.fit_dataframe(prepared_frames["train"])
        rows_used_by_model["lagged_linear"] = int(lagged_rows_used)
        candidate_records.append(
            {
                "candidate": _candidate_metrics_with_context(
                    model_family="lagged_linear",
                    model=lagged_model,
                    frames=prepared_frames,
                    notes=(
                        "Lagged tabular ridge baseline with current and historical predictor windows. "
                        f"Lag horizon={lagged_horizon} samples. Train rows used={lagged_rows_used}."
                    ),
                    hyperparameters={
                        "ridge": float(lagged_model.ridge),
                        "lag_horizon_samples": int(lagged_model.lag_horizon),
                        "training_feature_count": int(len(lagged_model._lagged_feature_columns)),
                        "training_rows_used": int(lagged_rows_used),
                    },
                ),
                "model": lagged_model,
                "rows_used": int(lagged_rows_used),
            }
        )

    lagged_tree_model: LaggedTreeEnsembleSurrogate | None = None
    if lagged_horizon is not None and (compare_against_baseline or requested == "lagged_tree_ensemble"):
        lagged_tree_model = LaggedTreeEnsembleSurrogate(
            feature_columns=model_feature_columns,
            target_column=target_column,
            lag_horizon=lagged_horizon,
        )
        lagged_tree_rows_used = lagged_tree_model.fit_dataframe(prepared_frames["train"])
        rows_used_by_model["lagged_tree_ensemble"] = int(lagged_tree_rows_used)
        candidate_records.append(
            {
                "candidate": _candidate_metrics_with_context(
                    model_family="lagged_tree_ensemble",
                    model=lagged_tree_model,
                    frames=prepared_frames,
                    notes=(
                        "Lag-window bagged depth-limited regression trees over current and historical "
                        f"predictor windows. Lag horizon={lagged_horizon} samples. "
                        f"Train rows used={lagged_tree_rows_used}."
                    ),
                    hyperparameters={
                        "lag_horizon_samples": int(lagged_tree_model.lag_horizon),
                        "n_estimators": int(lagged_tree_model.n_estimators),
                        "max_depth": int(lagged_tree_model.max_depth),
                        "min_leaf": int(lagged_tree_model.min_leaf),
                        "training_feature_count": int(len(lagged_tree_model._lagged_feature_columns)),
                        "training_rows_used": int(lagged_tree_rows_used),
                    },
                ),
                "model": lagged_tree_model,
                "rows_used": int(lagged_tree_rows_used),
            }
        )

    if compare_against_baseline or requested == "bagged_tree_ensemble":
        for record in _fit_regression_tree_candidates(
            family="bagged_tree_ensemble",
            frames=prepared_frames,
            model_feature_columns=model_feature_columns,
            target_column=target_column,
            hpo_context=hpo_context,
            task_type=task_profile.task_type,
            selection_metric=selection_metric,
        ):
            rows_used_by_model["bagged_tree_ensemble"] = int(record["rows_used"])
            candidate_records.append(record)

    if compare_against_baseline or requested == "boosted_tree_ensemble":
        for record in _fit_regression_tree_candidates(
            family="boosted_tree_ensemble",
            frames=prepared_frames,
            model_feature_columns=model_feature_columns,
            target_column=target_column,
            hpo_context=hpo_context,
            task_type=task_profile.task_type,
            selection_metric=selection_metric,
        ):
            rows_used_by_model["boosted_tree_ensemble"] = int(record["rows_used"])
            candidate_records.append(record)

    if compare_against_baseline or requested in _REGRESSION_ADAPTER_FAMILIES:
        for record in _fit_regression_estimator_candidates(
            frames=prepared_frames,
            model_feature_columns=model_feature_columns,
            target_column=target_column,
            requested_family=None if compare_against_baseline else requested,
            hpo_context=hpo_context,
            task_type=task_profile.task_type,
            selection_metric=selection_metric,
        ):
            rows_used_by_model[str(record["candidate"].model_family)] = int(record["rows_used"])
            candidate_records.append(record)

    candidates = [dict(record).get("candidate") for record in candidate_records]
    if requested in _REGRESSION_ADAPTER_FAMILIES and not any(
        item.model_family == requested for item in candidates
    ):
        raise ValueError(f"Requested model family `{requested}` is not available on this machine.")

    best_by_validation = _select_best_candidate(
        candidates,
        task_type=task_profile.task_type,
        selection_metric=selection_metric,
        preferred_candidate_order=preferred_candidate_order,
    )
    selected_candidate = _resolve_selected_candidate(
        requested=requested,
        candidates=candidates,
        task_type=task_profile.task_type,
        selection_metric=selection_metric,
        preferred_candidate_order=preferred_candidate_order,
    )
    selected_model_name = selected_candidate.model_family
    selected_record = next((record for record in candidate_records if record["candidate"] is selected_candidate), None)
    if selected_record is None:
        raise RuntimeError("Selected model object is unavailable.")
    selected_model_obj: Any = selected_record["model"]

    normalizer_path: str | None = None
    if normalizer is not None:
        normalizer_path = str(artifact_store.save_normalizer(run_dir=run_dir, normalizer=normalizer))

    model_state_path = _save_selected_model_state(
        model=selected_model_obj,
        run_dir=run_dir,
        model_name=selected_model_name,
    )
    regression_uncertainty = _regression_uncertainty_payload(
        selected_model_name=selected_model_name,
        selected_model_obj=selected_model_obj,
        prepared_frames=prepared_frames,
        feature_columns=model_feature_columns,
        target_column=target_column,
    )
    selected_hyperparameters = {"requested_model_family": requested}
    if selected_candidate.variant_id:
        selected_hyperparameters["selected_variant_id"] = selected_candidate.variant_id
    if isinstance(selected_candidate.hyperparameters, dict):
        selected_hyperparameters.update(selected_candidate.hyperparameters)
    professional_analysis = _build_regression_professional_analysis(
        selected_model_name=selected_model_name,
        selected_model_obj=selected_model_obj,
        selected_candidate=selected_candidate,
        prepared_frames=prepared_frames,
        feature_columns=model_feature_columns,
        target_column=target_column,
        lag_horizon_samples=lagged_horizon,
    )
    params_path = artifact_store.save_model_params(
        run_dir=run_dir,
        model_name=selected_model_name,
        best_params=selected_hyperparameters,
        metrics=selected_candidate.test_metrics,
        feature_columns=feature_columns,
        target_column=target_column,
        split_strategy=split.strategy,
        normalizer_path=normalizer_path,
        extra={
            "requested_model_family": requested,
            "selected_model_family": selected_candidate.model_family,
            "best_validation_model_family": best_by_validation.model_family,
            "data_mode": data_mode,
            "lag_horizon_samples": int(lagged_horizon) if lagged_horizon is not None else 0,
            "split": split.to_dict(),
            "preprocessing": preprocessing,
            "comparison": [item.to_dict() for item in candidates],
            "professional_analysis": professional_analysis,
            "uncertainty": regression_uncertainty,
            "selection_metric": str(selection_metric or "").strip() or "auto",
            "preferred_candidate_order": list(preferred_candidate_order or []),
        },
    )
    checkpoint_store = ModelCheckpointStore(base_dir=checkpoint_base_dir or "artifacts/checkpoints")
    checkpoint = checkpoint_store.create_checkpoint(
        model_name=selected_model_name,
        run_dir=run_dir,
        model_state_path=model_state_path,
        target_column=target_column,
        feature_columns=feature_columns,
        metrics=selected_candidate.test_metrics,
        data_references=list(data_references or []),
        notes=checkpoint_tag or "",
        tags=[checkpoint_tag] if checkpoint_tag else [],
    )
    hpo_artifacts = _write_hpo_artifacts(
        run_dir=run_dir,
        hpo_context=hpo_context,
        candidates=candidates,
        selected_candidate=selected_candidate,
        best_by_validation=best_by_validation,
        task_type=task_profile.task_type,
        threshold_policy=threshold_policy,
    )

    return {
        "status": "ok",
        "data_mode": data_mode,
        "task_profile": task_profile.to_dict(),
        "requested_model_family": requested,
        "selected_model_family": selected_candidate.model_family,
        "best_validation_model_family": best_by_validation.model_family,
        "comparison": [item.to_dict() for item in candidates],
        "split": split.to_dict(),
        "preprocessing": preprocessing,
        "normalization": {
            "enabled": bool(normalizer is not None),
            "method": "minmax" if normalizer is not None else "none",
            "normalizer_path": normalizer_path,
        },
        "checkpoint_id": checkpoint.checkpoint_id,
        "run_dir": str(run_dir),
        "model_state_path": str(model_state_path),
        "model_params_path": str(params_path),
        "selected_hyperparameters": selected_hyperparameters,
        "feature_columns": list(feature_columns),
        "model_feature_columns": list(model_feature_columns),
        "lag_horizon_samples": int(lagged_horizon) if lagged_horizon is not None else 0,
        "rows_used": int(rows_used_by_model.get(selected_model_name, prepared_frames["train"].shape[0])),
        "rows_used_by_model": rows_used_by_model,
        "professional_analysis": professional_analysis,
        "uncertainty": regression_uncertainty,
        "selected_metrics": {
            "train": _materialize_temporal_metric_aliases(
                metrics=selected_candidate.train_metrics,
                data_mode=data_mode,
            ),
            "validation": _materialize_temporal_metric_aliases(
                metrics=selected_candidate.validation_metrics,
                data_mode=data_mode,
            ),
            "test": _materialize_temporal_metric_aliases(
                metrics=selected_candidate.test_metrics,
                data_mode=data_mode,
            ),
        },
        "hpo": {
            "budget_contract": dict(hpo_context.get("budget_contract") or {}),
            "family_reports": list(hpo_context.get("family_reports") or []),
            "trial_count": len(hpo_context.get("trial_ledger") or []),
            "warm_start_used": bool(dict(hpo_context.get("warm_start_state") or {}).get("used")),
        },
        "hpo_artifacts": hpo_artifacts,
        "selection_metric": str(selection_metric or "").strip() or "auto",
        "preferred_candidate_order": list(preferred_candidate_order or []),
    }


def _resolve_requested_for_task(*, requested: str, task_type: str) -> str:
    if not is_classification_task(task_type):
        return requested
    if requested in {
        "auto",
        "logistic_regression",
        "lagged_logistic_regression",
        "bagged_tree_classifier",
        "boosted_tree_classifier",
        "hist_gradient_boosting_classifier",
        "extra_trees_classifier",
        "catboost_classifier",
        "xgboost_classifier",
        "lightgbm_classifier",
        "tabpfn_classifier",
        "lagged_tree_classifier",
    }:
        return requested
    if requested == "linear_ridge":
        return "logistic_regression"
    if requested == "lagged_linear":
        return "lagged_logistic_regression"
    if requested == "bagged_tree_ensemble":
        return "bagged_tree_classifier"
    if requested == "boosted_tree_ensemble":
        return "boosted_tree_classifier"
    if requested == "hist_gradient_boosting_ensemble":
        return "hist_gradient_boosting_classifier"
    if requested == "extra_trees_ensemble":
        return "extra_trees_classifier"
    if requested == "catboost_ensemble":
        return "catboost_classifier"
    if requested == "xgboost_ensemble":
        return "xgboost_classifier"
    if requested == "lightgbm_ensemble":
        return "lightgbm_classifier"
    if requested == "lagged_tree_ensemble":
        return "lagged_tree_classifier"
    return requested


def _train_classification_candidates(
    *,
    frame: pd.DataFrame,
    target_column: str,
    feature_columns: list[str],
    requested: str,
    normalize: bool,
    missing_data_strategy: str,
    fill_constant_value: float | None,
    compare_against_baseline: bool,
    lag_horizon_samples: int | None,
    split: DatasetSplit,
    task_profile: Any,
    threshold_policy: str | None,
    decision_threshold: float | None,
    run_id: str | None,
    checkpoint_tag: str | None,
    data_references: list[str] | None,
    selection_metric: str | None,
    preferred_candidate_order: list[str] | None,
    output_run_dir: str | Path | None,
    checkpoint_base_dir: str | Path | None,
) -> dict[str, Any]:
    split_frames = {
        "train": frame.iloc[split.train_indices].reset_index(drop=True),
        "validation": frame.iloc[split.validation_indices].reset_index(drop=True),
        "test": frame.iloc[split.test_indices].reset_index(drop=True),
    }
    prepared = _prepare_split_safe_frames_classification(
        split_frames=split_frames,
        feature_columns=feature_columns,
        target_column=target_column,
        missing_data_strategy=missing_data_strategy,
        fill_constant_value=fill_constant_value,
        task_type=str(task_profile.task_type),
    )
    prepared_frames = prepared["frames"]
    preprocessing = prepared["preprocessing"]
    model_feature_columns = [str(item) for item in prepared.get("model_feature_columns", []) if str(item).strip()]
    if not model_feature_columns:
        model_feature_columns = list(feature_columns)

    normalizer: MinMaxNormalizer | None = None
    if normalize:
        normalizer = MinMaxNormalizer()
        normalizer.fit(prepared_frames["train"], feature_columns=model_feature_columns)
        prepared_frames = {
            name: normalizer.transform_features(part)
            for name, part in prepared_frames.items()
        }

    artifact_store = ArtifactStore()
    if output_run_dir is not None:
        run_dir = Path(output_run_dir)
        run_dir.mkdir(parents=True, exist_ok=True)
    else:
        run_dir = artifact_store.create_run_dir(run_id=run_id)

    classification_hpo_family_pool: list[str] = ["logistic_regression"]
    if compare_against_baseline or requested == "bagged_tree_classifier":
        classification_hpo_family_pool.append("bagged_tree_classifier")
    if compare_against_baseline or requested == "boosted_tree_classifier":
        classification_hpo_family_pool.append("boosted_tree_classifier")
    if compare_against_baseline or requested in _CLASSIFICATION_ADAPTER_FAMILIES:
        classification_hpo_family_pool.extend(
            [
                family
                for family in [
                    "hist_gradient_boosting_classifier",
                    "extra_trees_classifier",
                    "catboost_classifier",
                    "xgboost_classifier",
                    "lightgbm_classifier",
                    "tabpfn_classifier",
                ]
                if compare_against_baseline or requested == family
            ]
        )
    classification_hpo_families = _ordered_available_hpo_families(
        preferred_candidate_order=preferred_candidate_order,
        candidate_pool=classification_hpo_family_pool,
    )
    hpo_context = _prepare_hpo_context(
        run_dir=run_dir,
        task_type=str(task_profile.task_type),
        row_count=len(frame),
        requested_family=requested,
        preferred_candidate_order=preferred_candidate_order,
        available_families=classification_hpo_families,
    )

    lagged_horizon = _resolve_lag_horizon(
        data_mode="time_series" if split.data_mode == "time_series" else "steady_state",
        requested=requested,
        lag_horizon_samples=lag_horizon_samples,
        split=split,
    )
    if requested in {"lagged_logistic_regression", "lagged_tree_classifier"} and lagged_horizon is None:
        raise ValueError(
            "Lagged classifier families require time-series structure and a usable timestamp column."
        )

    rows_used_by_model: dict[str, int] = {}
    classifier_thresholds: dict[str, float] = {}
    candidate_records: list[dict[str, Any]] = []
    for record in _fit_logistic_candidates(
        frames=prepared_frames,
        model_feature_columns=model_feature_columns,
        target_column=target_column,
        task_type=str(task_profile.task_type),
        threshold_policy=threshold_policy,
        decision_threshold=decision_threshold,
        hpo_context=hpo_context,
        selection_metric=selection_metric,
    ):
        rows_used_by_model["logistic_regression"] = int(record["rows_used"])
        classifier_thresholds["logistic_regression"] = float(
            record["candidate"].train_metrics.get("decision_threshold", 0.5)
        )
        candidate_records.append(record)
    lagged_logistic_model: LaggedLogisticClassificationSurrogate | None = None
    if lagged_horizon is not None and (compare_against_baseline or requested == "lagged_logistic_regression"):
        lagged_logistic_model = LaggedLogisticClassificationSurrogate(
            feature_columns=model_feature_columns,
            target_column=target_column,
            lag_horizon=lagged_horizon,
        )
        lagged_logistic_rows = lagged_logistic_model.fit_dataframe(prepared_frames["train"])
        rows_used_by_model["lagged_logistic_regression"] = int(lagged_logistic_rows)
        lagged_logistic_candidate = _classification_candidate_metrics_with_context(
            model_family="lagged_logistic_regression",
            model=lagged_logistic_model,
            frames=prepared_frames,
            task_type=str(task_profile.task_type),
            threshold_policy=threshold_policy,
            decision_threshold=decision_threshold,
            notes=(
                "Lagged logistic classifier over current and historical predictor windows. "
                f"Lag horizon={lagged_horizon} samples. Train rows used={lagged_logistic_rows}."
            ),
            hyperparameters={
                "learning_rate": float(lagged_logistic_model.learning_rate),
                "epochs": int(lagged_logistic_model.epochs),
                "l2": float(lagged_logistic_model.l2),
                "lag_horizon_samples": int(lagged_logistic_model.lag_horizon),
                "training_rows_used": int(lagged_logistic_rows),
                "class_count": int(len(lagged_logistic_model.class_labels)),
                "training_feature_count": int(len(lagged_logistic_model._lagged_feature_columns)),
            },
        )
        candidate_records.append(
            {
                "candidate": lagged_logistic_candidate,
                "model": lagged_logistic_model,
                "rows_used": int(lagged_logistic_rows),
            }
        )
        classifier_thresholds["lagged_logistic_regression"] = float(
            lagged_logistic_candidate.train_metrics.get("decision_threshold", 0.5)
        )

    if compare_against_baseline or requested == "bagged_tree_classifier":
        for record in _fit_classifier_tree_candidates(
            family="bagged_tree_classifier",
            frames=prepared_frames,
            model_feature_columns=model_feature_columns,
            target_column=target_column,
            task_type=str(task_profile.task_type),
            threshold_policy=threshold_policy,
            decision_threshold=decision_threshold,
            hpo_context=hpo_context,
            selection_metric=selection_metric,
        ):
            rows_used_by_model["bagged_tree_classifier"] = int(record["rows_used"])
            classifier_thresholds["bagged_tree_classifier"] = float(
                record["candidate"].train_metrics.get("decision_threshold", 0.5)
            )
            candidate_records.append(record)

    if compare_against_baseline or requested == "boosted_tree_classifier":
        for record in _fit_classifier_tree_candidates(
            family="boosted_tree_classifier",
            frames=prepared_frames,
            model_feature_columns=model_feature_columns,
            target_column=target_column,
            task_type=str(task_profile.task_type),
            threshold_policy=threshold_policy,
            decision_threshold=decision_threshold,
            hpo_context=hpo_context,
            selection_metric=selection_metric,
        ):
            rows_used_by_model["boosted_tree_classifier"] = int(record["rows_used"])
            classifier_thresholds["boosted_tree_classifier"] = float(
                record["candidate"].train_metrics.get("decision_threshold", 0.5)
            )
            candidate_records.append(record)

    class_count = int(task_profile.class_count or 0)
    if compare_against_baseline or requested in _CLASSIFICATION_ADAPTER_FAMILIES:
        for record in _fit_classification_estimator_candidates(
            frames=prepared_frames,
            model_feature_columns=model_feature_columns,
            target_column=target_column,
            task_type=str(task_profile.task_type),
            threshold_policy=threshold_policy,
            decision_threshold=decision_threshold,
            class_count=class_count,
            requested_family=None if compare_against_baseline else requested,
            hpo_context=hpo_context,
            selection_metric=selection_metric,
        ):
            rows_used_by_model[str(record["candidate"].model_family)] = int(record["rows_used"])
            classifier_thresholds[str(record["candidate"].model_family)] = float(
                record["candidate"].train_metrics.get("decision_threshold", 0.5)
            )
            candidate_records.append(record)

    lagged_tree_classifier: LaggedTreeClassifierSurrogate | None = None
    if lagged_horizon is not None and (compare_against_baseline or requested == "lagged_tree_classifier"):
        lagged_tree_classifier = LaggedTreeClassifierSurrogate(
            feature_columns=model_feature_columns,
            target_column=target_column,
            lag_horizon=lagged_horizon,
        )
        lagged_tree_rows = lagged_tree_classifier.fit_dataframe(prepared_frames["train"])
        rows_used_by_model["lagged_tree_classifier"] = int(lagged_tree_rows)
        lagged_tree_candidate = _classification_candidate_metrics_with_context(
            model_family="lagged_tree_classifier",
            model=lagged_tree_classifier,
            frames=prepared_frames,
            task_type=str(task_profile.task_type),
            threshold_policy=threshold_policy,
            decision_threshold=decision_threshold,
            notes=(
                "Lag-window bagged tree classifier over current and historical predictor windows. "
                f"Lag horizon={lagged_horizon} samples. Train rows used={lagged_tree_rows}."
            ),
            hyperparameters={
                "n_estimators": int(lagged_tree_classifier.n_estimators),
                "max_depth": int(lagged_tree_classifier.max_depth),
                "min_leaf": int(lagged_tree_classifier.min_leaf),
                "lag_horizon_samples": int(lagged_tree_classifier.lag_horizon),
                "training_rows_used": int(lagged_tree_rows),
                "class_count": int(len(lagged_tree_classifier.class_labels)),
                "training_feature_count": int(len(lagged_tree_classifier._lagged_feature_columns)),
            },
        )
        candidate_records.append(
            {
                "candidate": lagged_tree_candidate,
                "model": lagged_tree_classifier,
                "rows_used": int(lagged_tree_rows),
            }
        )
        classifier_thresholds["lagged_tree_classifier"] = float(
            lagged_tree_candidate.train_metrics.get("decision_threshold", 0.5)
        )

    candidates = [dict(record).get("candidate") for record in candidate_records]
    if requested in _CLASSIFICATION_ADAPTER_FAMILIES and not any(
        item.model_family == requested for item in candidates
    ):
        raise ValueError(f"Requested model family `{requested}` is not available on this machine.")

    best_by_validation = _select_best_candidate(
        candidates,
        task_type=str(task_profile.task_type),
        selection_metric=selection_metric,
        preferred_candidate_order=preferred_candidate_order,
    )
    selected_candidate = _resolve_selected_candidate(
        requested=requested,
        candidates=candidates,
        task_type=str(task_profile.task_type),
        selection_metric=selection_metric,
        preferred_candidate_order=preferred_candidate_order,
    )
    selected_model_name = selected_candidate.model_family
    selected_record = next((record for record in candidate_records if record["candidate"] is selected_candidate), None)
    if selected_record is None:
        raise RuntimeError("Selected classifier model object is unavailable.")
    selected_model_obj: Any = selected_record["model"]

    normalizer_path: str | None = None
    if normalizer is not None:
        normalizer_path = str(artifact_store.save_normalizer(run_dir=run_dir, normalizer=normalizer))

    model_state_path = _save_selected_model_state(
        model=selected_model_obj,
        run_dir=run_dir,
        model_name=selected_model_name,
    )
    selected_hyperparameters = {
        "requested_model_family": requested,
        "task_type": str(task_profile.task_type),
        "threshold_policy": str(threshold_policy or "").strip() or "auto",
    }
    if selected_candidate.variant_id:
        selected_hyperparameters["selected_variant_id"] = selected_candidate.variant_id
    if isinstance(selected_candidate.hyperparameters, dict):
        selected_hyperparameters.update(selected_candidate.hyperparameters)
    if _is_number(selected_candidate.test_metrics.get("decision_threshold")):
        selected_hyperparameters["decision_threshold"] = float(selected_candidate.test_metrics["decision_threshold"])

    professional_analysis = _build_classification_professional_analysis(
        selected_model_name=selected_model_name,
        selected_model_obj=selected_model_obj,
        selected_candidate=selected_candidate,
        prepared_frames=prepared_frames,
        feature_columns=model_feature_columns,
        target_column=target_column,
        task_type=str(task_profile.task_type),
    )

    params_path = artifact_store.save_model_params(
        run_dir=run_dir,
        model_name=selected_model_name,
        best_params=selected_hyperparameters,
        metrics=selected_candidate.test_metrics,
        feature_columns=feature_columns,
        target_column=target_column,
        split_strategy=split.strategy,
        normalizer_path=normalizer_path,
        extra={
            "requested_model_family": requested,
            "selected_model_family": selected_candidate.model_family,
            "best_validation_model_family": best_by_validation.model_family,
            "data_mode": "time_series" if split.data_mode == "time_series" else "steady_state",
            "split": split.to_dict(),
            "preprocessing": preprocessing,
            "comparison": [item.to_dict() for item in candidates],
            "task_profile": task_profile.to_dict(),
            "decision_thresholds": classifier_thresholds,
            "threshold_policy": str(threshold_policy or "").strip() or "auto",
            "calibration": dict(selected_candidate.calibration or {}),
            "uncertainty": dict(selected_candidate.uncertainty or {}),
            "lag_horizon_samples": int(lagged_horizon) if lagged_horizon is not None else 0,
            "professional_analysis": professional_analysis,
            "selection_metric": str(selection_metric or "").strip() or "auto",
            "preferred_candidate_order": list(preferred_candidate_order or []),
        },
    )
    checkpoint_store = ModelCheckpointStore(base_dir=checkpoint_base_dir or "artifacts/checkpoints")
    checkpoint = checkpoint_store.create_checkpoint(
        model_name=selected_model_name,
        run_dir=run_dir,
        model_state_path=model_state_path,
        target_column=target_column,
        feature_columns=feature_columns,
        metrics=selected_candidate.test_metrics,
        data_references=list(data_references or []),
        notes=checkpoint_tag or "",
        tags=[checkpoint_tag] if checkpoint_tag else [],
    )
    hpo_artifacts = _write_hpo_artifacts(
        run_dir=run_dir,
        hpo_context=hpo_context,
        candidates=candidates,
        selected_candidate=selected_candidate,
        best_by_validation=best_by_validation,
        task_type=str(task_profile.task_type),
        threshold_policy=threshold_policy,
    )
    return {
        "status": "ok",
        "data_mode": "time_series" if split.data_mode == "time_series" else "steady_state",
        "task_profile": task_profile.to_dict(),
        "requested_model_family": requested,
        "selected_model_family": selected_candidate.model_family,
        "best_validation_model_family": best_by_validation.model_family,
        "comparison": [item.to_dict() for item in candidates],
        "split": split.to_dict(),
        "preprocessing": preprocessing,
        "normalization": {
            "enabled": bool(normalizer is not None),
            "method": "minmax" if normalizer is not None else "none",
            "normalizer_path": normalizer_path,
        },
        "checkpoint_id": checkpoint.checkpoint_id,
        "run_dir": str(run_dir),
        "model_state_path": str(model_state_path),
        "model_params_path": str(params_path),
        "selected_hyperparameters": selected_hyperparameters,
        "feature_columns": list(feature_columns),
        "model_feature_columns": list(model_feature_columns),
        "lag_horizon_samples": int(lagged_horizon) if lagged_horizon is not None else 0,
        "rows_used": int(rows_used_by_model.get(selected_model_name, prepared_frames["train"].shape[0])),
        "rows_used_by_model": rows_used_by_model,
        "professional_analysis": professional_analysis,
        "calibration": dict(selected_candidate.calibration or {}),
        "uncertainty": dict(selected_candidate.uncertainty or {}),
        "selected_metrics": {
            "train": _materialize_temporal_metric_aliases(
                metrics=selected_candidate.train_metrics,
                data_mode="time_series" if split.data_mode == "time_series" else "steady_state",
            ),
            "validation": _materialize_temporal_metric_aliases(
                metrics=selected_candidate.validation_metrics,
                data_mode="time_series" if split.data_mode == "time_series" else "steady_state",
            ),
            "test": _materialize_temporal_metric_aliases(
                metrics=selected_candidate.test_metrics,
                data_mode="time_series" if split.data_mode == "time_series" else "steady_state",
            ),
        },
        "hpo": {
            "budget_contract": dict(hpo_context.get("budget_contract") or {}),
            "family_reports": list(hpo_context.get("family_reports") or []),
            "trial_count": len(hpo_context.get("trial_ledger") or []),
            "warm_start_used": bool(dict(hpo_context.get("warm_start_state") or {}).get("used")),
        },
        "hpo_artifacts": hpo_artifacts,
        "selection_metric": str(selection_metric or "").strip() or "auto",
        "preferred_candidate_order": list(preferred_candidate_order or []),
    }


class BaggedTreeEnsembleSurrogate:
    """Small local regression tree ensemble without external dependencies."""

    def __init__(
        self,
        *,
        feature_columns: list[str],
        target_column: str,
        n_estimators: int = 12,
        max_depth: int = 4,
        min_leaf: int = 6,
    ) -> None:
        if not feature_columns:
            raise ValueError("feature_columns cannot be empty.")
        self.feature_columns = list(feature_columns)
        self.target_column = target_column
        self.n_estimators = int(n_estimators)
        self.max_depth = int(max_depth)
        self.min_leaf = int(min_leaf)
        self._estimators: list[dict[str, Any]] = []

    def fit_dataframe(self, frame: pd.DataFrame) -> int:
        x, y = _prepare_xy(frame=frame, feature_columns=self.feature_columns, target_column=self.target_column)
        if x.shape[0] == 0:
            raise ValueError("No valid numeric rows available for tree training.")
        self._estimators = []
        feature_count = x.shape[1]
        feature_subsample = max(1, int(feature_count))
        for seed in range(self.n_estimators):
            rng = np.random.default_rng(100 + seed)
            row_idx = rng.integers(0, x.shape[0], size=x.shape[0])
            feat_idx = np.sort(
                rng.choice(feature_count, size=feature_subsample, replace=False)
            ).astype(int)
            tree = _fit_regression_tree(
                x_train=x[row_idx][:, feat_idx],
                y_train=y[row_idx],
                depth=0,
                max_depth=self.max_depth,
                min_leaf=min(self.min_leaf, max(2, x.shape[0] // 8)),
            )
            self._estimators.append(
                {
                    "feature_indices": feat_idx.tolist(),
                    "tree": tree,
                }
            )
        return int(x.shape[0])

    def predict_dataframe(self, frame: pd.DataFrame) -> np.ndarray:
        if not self._estimators:
            raise RuntimeError("Tree ensemble has not been fitted yet.")
        x = _prepare_feature_matrix(frame=frame, feature_columns=self.feature_columns)
        preds = []
        for estimator in self._estimators:
            feat_idx = np.asarray(estimator["feature_indices"], dtype=int)
            pred = _predict_regression_tree_batch(
                tree=estimator["tree"],
                x=x[:, feat_idx],
            )
            preds.append(pred)
        return np.mean(np.vstack(preds), axis=0).astype(float)

    def evaluate_dataframe(self, frame: pd.DataFrame) -> dict[str, float]:
        y_true = _prepare_target_vector(frame=frame, target_column=self.target_column)
        y_pred = self.predict_dataframe(frame)
        return regression_metrics(y_true=y_true, y_pred=y_pred).to_dict()

    def state_dict(self) -> dict[str, Any]:
        if not self._estimators:
            raise RuntimeError("Tree ensemble has not been fitted yet.")
        return {
            "model_name": "bagged_tree_ensemble",
            "feature_columns": list(self.feature_columns),
            "target_column": self.target_column,
            "n_estimators": self.n_estimators,
            "max_depth": self.max_depth,
            "min_leaf": self.min_leaf,
            "estimators": self._estimators,
        }

    def save(self, path: str | Path) -> Path:
        output = Path(path)
        output.parent.mkdir(parents=True, exist_ok=True)
        return write_json(output, self.state_dict(), indent=2)


class BoostedTreeEnsembleSurrogate:
    """Simple gradient-boosted regression trees with local weak learners."""

    def __init__(
        self,
        *,
        feature_columns: list[str],
        target_column: str,
        n_estimators: int = 28,
        learning_rate: float = 0.25,
        max_depth: int = 3,
        min_leaf: int = 5,
    ) -> None:
        if not feature_columns:
            raise ValueError("feature_columns cannot be empty.")
        self.feature_columns = list(feature_columns)
        self.target_column = target_column
        self.n_estimators = int(n_estimators)
        self.learning_rate = float(learning_rate)
        self.max_depth = int(max_depth)
        self.min_leaf = int(min_leaf)
        self._bias: float = 0.0
        self._estimators: list[dict[str, Any]] = []

    def fit_dataframe(self, frame: pd.DataFrame) -> int:
        x, y = _prepare_xy(frame=frame, feature_columns=self.feature_columns, target_column=self.target_column)
        if x.shape[0] == 0:
            raise ValueError("No valid numeric rows available for boosted tree training.")
        self._bias = float(np.mean(y))
        residual = y - self._bias
        self._estimators = []
        feature_count = x.shape[1]
        feature_subsample = max(1, int(math.sqrt(feature_count)))
        for step in range(self.n_estimators):
            rng = np.random.default_rng(300 + step)
            feat_idx = np.sort(
                rng.choice(feature_count, size=feature_subsample, replace=False)
            ).astype(int)
            tree = _fit_regression_tree(
                x_train=x[:, feat_idx],
                y_train=residual,
                depth=0,
                max_depth=self.max_depth,
                min_leaf=min(self.min_leaf, max(2, x.shape[0] // 10)),
            )
            update = _predict_regression_tree_batch(tree=tree, x=x[:, feat_idx])
            residual = residual - (self.learning_rate * update)
            self._estimators.append(
                {
                    "feature_indices": feat_idx.tolist(),
                    "tree": tree,
                }
            )
            if float(np.std(residual)) <= 1e-7:
                break
        if not self._estimators:
            raise RuntimeError("Boosted tree ensemble failed to produce any weak learner.")
        return int(x.shape[0])

    def predict_dataframe(self, frame: pd.DataFrame) -> np.ndarray:
        if not self._estimators:
            raise RuntimeError("Boosted tree ensemble has not been fitted yet.")
        x = _prepare_feature_matrix(frame=frame, feature_columns=self.feature_columns)
        pred = np.full(x.shape[0], self._bias, dtype=float)
        for estimator in self._estimators:
            feat_idx = np.asarray(estimator["feature_indices"], dtype=int)
            pred += self.learning_rate * _predict_regression_tree_batch(
                tree=estimator["tree"],
                x=x[:, feat_idx],
            )
        return pred.astype(float)

    def evaluate_dataframe(self, frame: pd.DataFrame) -> dict[str, float]:
        y_true = _prepare_target_vector(frame=frame, target_column=self.target_column)
        y_pred = self.predict_dataframe(frame)
        return regression_metrics(y_true=y_true, y_pred=y_pred).to_dict()

    def state_dict(self) -> dict[str, Any]:
        if not self._estimators:
            raise RuntimeError("Boosted tree ensemble has not been fitted yet.")
        return {
            "model_name": "boosted_tree_ensemble",
            "feature_columns": list(self.feature_columns),
            "target_column": self.target_column,
            "n_estimators": int(self.n_estimators),
            "learning_rate": float(self.learning_rate),
            "max_depth": int(self.max_depth),
            "min_leaf": int(self.min_leaf),
            "bias": float(self._bias),
            "estimators": self._estimators,
        }

    def save(self, path: str | Path) -> Path:
        output = Path(path)
        output.parent.mkdir(parents=True, exist_ok=True)
        return write_json(output, self.state_dict(), indent=2)


class LaggedLinearSurrogate:
    """Linear surrogate over current and lagged predictor windows."""

    def __init__(
        self,
        *,
        feature_columns: list[str],
        target_column: str,
        lag_horizon: int = 3,
        ridge: float = 1e-8,
    ) -> None:
        if not feature_columns:
            raise ValueError("feature_columns cannot be empty.")
        if int(lag_horizon) <= 0:
            raise ValueError("lag_horizon must be > 0.")
        self.feature_columns = list(feature_columns)
        self.target_column = target_column
        self.lag_horizon = int(lag_horizon)
        self.ridge = float(ridge)
        self._lagged_feature_columns = _lagged_feature_names(
            feature_columns=self.feature_columns,
            lag_horizon=self.lag_horizon,
        )
        self._delegate: IncrementalLinearSurrogate | None = None

    def fit_dataframe(self, frame: pd.DataFrame) -> int:
        lagged = _build_lagged_design_frame(
            frame=frame,
            feature_columns=self.feature_columns,
            target_column=self.target_column,
            lag_horizon=self.lag_horizon,
            expected_feature_columns=self._lagged_feature_columns,
        )
        if lagged.shape[0] == 0:
            raise ValueError("No valid rows available after lagged feature construction.")
        self._delegate = IncrementalLinearSurrogate(
            feature_columns=list(self._lagged_feature_columns),
            target_column=self.target_column,
            ridge=self.ridge,
        )
        return self._delegate.fit_dataframe(lagged)

    def predict_dataframe(
        self,
        frame: pd.DataFrame,
        *,
        context_frame: pd.DataFrame | None = None,
    ) -> np.ndarray:
        lagged = self._lagged_frame(frame=frame, context_frame=context_frame)
        if lagged.shape[0] == 0:
            raise ValueError("Lagged prediction frame is empty for the requested split.")
        return self._require_delegate().predict_dataframe(lagged)

    def evaluate_dataframe(
        self,
        frame: pd.DataFrame,
        *,
        context_frame: pd.DataFrame | None = None,
    ) -> dict[str, float]:
        lagged = self._lagged_frame(frame=frame, context_frame=context_frame)
        if lagged.shape[0] == 0:
            raise ValueError("Lagged evaluation frame is empty for the requested split.")
        return self._require_delegate().evaluate_dataframe(lagged)

    def state_dict(self) -> dict[str, Any]:
        delegate = self._require_delegate()
        return {
            "model_name": "lagged_linear",
            "feature_columns": list(self.feature_columns),
            "target_column": self.target_column,
            "lag_horizon": int(self.lag_horizon),
            "ridge": float(self.ridge),
            "lagged_feature_columns": list(self._lagged_feature_columns),
            "linear_state": delegate.state_dict(),
        }

    def save(self, path: str | Path) -> Path:
        output = Path(path)
        output.parent.mkdir(parents=True, exist_ok=True)
        return write_json(output, self.state_dict(), indent=2)

    def _lagged_frame(
        self,
        *,
        frame: pd.DataFrame,
        context_frame: pd.DataFrame | None = None,
    ) -> pd.DataFrame:
        return _build_lagged_design_frame(
            frame=frame,
            feature_columns=self.feature_columns,
            target_column=self.target_column,
            lag_horizon=self.lag_horizon,
            context_frame=context_frame,
            expected_feature_columns=self._lagged_feature_columns,
        )

    def _require_delegate(self) -> IncrementalLinearSurrogate:
        if self._delegate is None:
            raise RuntimeError("Lagged linear surrogate has not been fitted yet.")
        return self._delegate


class LaggedTreeEnsembleSurrogate:
    """Tree ensemble over current and lagged predictor windows."""

    def __init__(
        self,
        *,
        feature_columns: list[str],
        target_column: str,
        lag_horizon: int = 3,
        n_estimators: int = 12,
        max_depth: int = 4,
        min_leaf: int = 6,
    ) -> None:
        if not feature_columns:
            raise ValueError("feature_columns cannot be empty.")
        if int(lag_horizon) <= 0:
            raise ValueError("lag_horizon must be > 0.")
        self.feature_columns = list(feature_columns)
        self.target_column = target_column
        self.lag_horizon = int(lag_horizon)
        self.n_estimators = int(n_estimators)
        self.max_depth = int(max_depth)
        self.min_leaf = int(min_leaf)
        self._lagged_feature_columns = _lagged_feature_names(
            feature_columns=self.feature_columns,
            lag_horizon=self.lag_horizon,
        )
        self._delegate: BaggedTreeEnsembleSurrogate | None = None

    def fit_dataframe(self, frame: pd.DataFrame) -> int:
        lagged = _build_lagged_design_frame(
            frame=frame,
            feature_columns=self.feature_columns,
            target_column=self.target_column,
            lag_horizon=self.lag_horizon,
            expected_feature_columns=self._lagged_feature_columns,
        )
        if lagged.shape[0] == 0:
            raise ValueError("No valid rows available after lagged feature construction.")
        self._delegate = BaggedTreeEnsembleSurrogate(
            feature_columns=list(self._lagged_feature_columns),
            target_column=self.target_column,
            n_estimators=self.n_estimators,
            max_depth=self.max_depth,
            min_leaf=self.min_leaf,
        )
        return self._delegate.fit_dataframe(lagged)

    def predict_dataframe(
        self,
        frame: pd.DataFrame,
        *,
        context_frame: pd.DataFrame | None = None,
    ) -> np.ndarray:
        lagged = self._lagged_frame(frame=frame, context_frame=context_frame)
        if lagged.shape[0] == 0:
            raise ValueError("Lagged prediction frame is empty for the requested split.")
        return self._require_delegate().predict_dataframe(lagged)

    def evaluate_dataframe(
        self,
        frame: pd.DataFrame,
        *,
        context_frame: pd.DataFrame | None = None,
    ) -> dict[str, float]:
        lagged = self._lagged_frame(frame=frame, context_frame=context_frame)
        if lagged.shape[0] == 0:
            raise ValueError("Lagged evaluation frame is empty for the requested split.")
        return self._require_delegate().evaluate_dataframe(lagged)

    def state_dict(self) -> dict[str, Any]:
        delegate = self._require_delegate()
        return {
            "model_name": "lagged_tree_ensemble",
            "feature_columns": list(self.feature_columns),
            "target_column": self.target_column,
            "lag_horizon": int(self.lag_horizon),
            "n_estimators": int(self.n_estimators),
            "max_depth": int(self.max_depth),
            "min_leaf": int(self.min_leaf),
            "lagged_feature_columns": list(self._lagged_feature_columns),
            "tree_state": delegate.state_dict(),
        }

    def save(self, path: str | Path) -> Path:
        output = Path(path)
        output.parent.mkdir(parents=True, exist_ok=True)
        return write_json(output, self.state_dict(), indent=2)

    def _lagged_frame(
        self,
        *,
        frame: pd.DataFrame,
        context_frame: pd.DataFrame | None = None,
    ) -> pd.DataFrame:
        return _build_lagged_design_frame(
            frame=frame,
            feature_columns=self.feature_columns,
            target_column=self.target_column,
            lag_horizon=self.lag_horizon,
            context_frame=context_frame,
            expected_feature_columns=self._lagged_feature_columns,
        )

    def _require_delegate(self) -> BaggedTreeEnsembleSurrogate:
        if self._delegate is None:
            raise RuntimeError("Lagged tree ensemble has not been fitted yet.")
        return self._delegate


class LaggedLogisticClassificationSurrogate:
    """Logistic classifier over current and lagged predictor windows."""

    def __init__(
        self,
        *,
        feature_columns: list[str],
        target_column: str,
        lag_horizon: int = 3,
        learning_rate: float = 0.25,
        epochs: int = 350,
        l2: float = 1e-4,
    ) -> None:
        if not feature_columns:
            raise ValueError("feature_columns cannot be empty.")
        if int(lag_horizon) <= 0:
            raise ValueError("lag_horizon must be > 0.")
        self.feature_columns = list(feature_columns)
        self.target_column = target_column
        self.lag_horizon = int(lag_horizon)
        self.learning_rate = float(learning_rate)
        self.epochs = int(epochs)
        self.l2 = float(l2)
        self._lagged_feature_columns = _lagged_feature_names(
            feature_columns=self.feature_columns,
            lag_horizon=self.lag_horizon,
        )
        self._delegate: LogisticClassificationSurrogate | None = None

    @property
    def class_labels(self) -> list[str]:
        return list(self._require_delegate().class_labels)

    def fit_dataframe(self, frame: pd.DataFrame) -> int:
        lagged = self._lagged_frame(frame=frame)
        if lagged.shape[0] == 0:
            raise ValueError("No valid rows available after lagged feature construction.")
        self._delegate = LogisticClassificationSurrogate(
            feature_columns=list(self._lagged_feature_columns),
            target_column=self.target_column,
            learning_rate=self.learning_rate,
            epochs=self.epochs,
            l2=self.l2,
        )
        return self._delegate.fit_dataframe(lagged)

    def predict_proba_dataframe(
        self,
        frame: pd.DataFrame,
        *,
        context_frame: pd.DataFrame | None = None,
    ) -> np.ndarray:
        lagged = self._lagged_frame(frame=frame, context_frame=context_frame)
        if lagged.shape[0] == 0:
            raise ValueError("Lagged prediction frame is empty for the requested split.")
        return self._require_delegate().predict_proba_dataframe(lagged)

    def predict_dataframe(
        self,
        frame: pd.DataFrame,
        *,
        context_frame: pd.DataFrame | None = None,
    ) -> np.ndarray:
        lagged = self._lagged_frame(frame=frame, context_frame=context_frame)
        if lagged.shape[0] == 0:
            raise ValueError("Lagged prediction frame is empty for the requested split.")
        return self._require_delegate().predict_dataframe(lagged)

    def state_dict(self) -> dict[str, Any]:
        delegate = self._require_delegate()
        return {
            "model_name": "lagged_logistic_regression",
            "feature_columns": list(self.feature_columns),
            "target_column": self.target_column,
            "lag_horizon": int(self.lag_horizon),
            "learning_rate": float(self.learning_rate),
            "epochs": int(self.epochs),
            "l2": float(self.l2),
            "lagged_feature_columns": list(self._lagged_feature_columns),
            "logistic_state": delegate.state_dict(),
        }

    def save(self, path: str | Path) -> Path:
        output = Path(path)
        output.parent.mkdir(parents=True, exist_ok=True)
        return write_json(output, self.state_dict(), indent=2)

    def _lagged_frame(
        self,
        *,
        frame: pd.DataFrame,
        context_frame: pd.DataFrame | None = None,
    ) -> pd.DataFrame:
        return _build_lagged_design_frame(
            frame=frame,
            feature_columns=self.feature_columns,
            target_column=self.target_column,
            lag_horizon=self.lag_horizon,
            context_frame=context_frame,
            expected_feature_columns=self._lagged_feature_columns,
        )

    def _require_delegate(self) -> LogisticClassificationSurrogate:
        if self._delegate is None:
            raise RuntimeError("Lagged logistic classifier has not been fitted yet.")
        return self._delegate


class LaggedTreeClassifierSurrogate:
    """Bagged tree classifier over current and lagged predictor windows."""

    def __init__(
        self,
        *,
        feature_columns: list[str],
        target_column: str,
        lag_horizon: int = 3,
        n_estimators: int = 12,
        max_depth: int = 4,
        min_leaf: int = 6,
    ) -> None:
        if not feature_columns:
            raise ValueError("feature_columns cannot be empty.")
        if int(lag_horizon) <= 0:
            raise ValueError("lag_horizon must be > 0.")
        self.feature_columns = list(feature_columns)
        self.target_column = target_column
        self.lag_horizon = int(lag_horizon)
        self.n_estimators = int(n_estimators)
        self.max_depth = int(max_depth)
        self.min_leaf = int(min_leaf)
        self._lagged_feature_columns = _lagged_feature_names(
            feature_columns=self.feature_columns,
            lag_horizon=self.lag_horizon,
        )
        self._delegate: BaggedTreeClassifierSurrogate | None = None

    @property
    def class_labels(self) -> list[str]:
        return list(self._require_delegate().class_labels)

    def fit_dataframe(self, frame: pd.DataFrame) -> int:
        lagged = self._lagged_frame(frame=frame)
        if lagged.shape[0] == 0:
            raise ValueError("No valid rows available after lagged feature construction.")
        self._delegate = BaggedTreeClassifierSurrogate(
            feature_columns=list(self._lagged_feature_columns),
            target_column=self.target_column,
            n_estimators=self.n_estimators,
            max_depth=self.max_depth,
            min_leaf=self.min_leaf,
        )
        return self._delegate.fit_dataframe(lagged)

    def predict_proba_dataframe(
        self,
        frame: pd.DataFrame,
        *,
        context_frame: pd.DataFrame | None = None,
    ) -> np.ndarray:
        lagged = self._lagged_frame(frame=frame, context_frame=context_frame)
        if lagged.shape[0] == 0:
            raise ValueError("Lagged prediction frame is empty for the requested split.")
        return self._require_delegate().predict_proba_dataframe(lagged)

    def predict_dataframe(
        self,
        frame: pd.DataFrame,
        *,
        context_frame: pd.DataFrame | None = None,
    ) -> np.ndarray:
        lagged = self._lagged_frame(frame=frame, context_frame=context_frame)
        if lagged.shape[0] == 0:
            raise ValueError("Lagged prediction frame is empty for the requested split.")
        return self._require_delegate().predict_dataframe(lagged)

    def state_dict(self) -> dict[str, Any]:
        delegate = self._require_delegate()
        return {
            "model_name": "lagged_tree_classifier",
            "feature_columns": list(self.feature_columns),
            "target_column": self.target_column,
            "lag_horizon": int(self.lag_horizon),
            "n_estimators": int(self.n_estimators),
            "max_depth": int(self.max_depth),
            "min_leaf": int(self.min_leaf),
            "lagged_feature_columns": list(self._lagged_feature_columns),
            "tree_state": delegate.state_dict(),
        }

    def save(self, path: str | Path) -> Path:
        output = Path(path)
        output.parent.mkdir(parents=True, exist_ok=True)
        return write_json(output, self.state_dict(), indent=2)

    def _lagged_frame(
        self,
        *,
        frame: pd.DataFrame,
        context_frame: pd.DataFrame | None = None,
    ) -> pd.DataFrame:
        return _build_lagged_design_frame(
            frame=frame,
            feature_columns=self.feature_columns,
            target_column=self.target_column,
            lag_horizon=self.lag_horizon,
            context_frame=context_frame,
            expected_feature_columns=self._lagged_feature_columns,
        )

    def _require_delegate(self) -> BaggedTreeClassifierSurrogate:
        if self._delegate is None:
            raise RuntimeError("Lagged tree classifier has not been fitted yet.")
        return self._delegate


def _candidate_metrics_from_model(
    *,
    model_family: str,
    model: Any,
    frames: dict[str, pd.DataFrame],
    notes: str,
    variant_id: str | None = None,
    hyperparameters: dict[str, Any] | None = None,
    uncertainty: dict[str, Any] | None = None,
) -> CandidateMetrics:
    return CandidateMetrics(
        model_family=model_family,
        train_metrics={k: float(v) for k, v in model.evaluate_dataframe(frames["train"]).items()},
        validation_metrics={
            k: float(v) for k, v in model.evaluate_dataframe(frames["validation"]).items()
        },
        test_metrics={k: float(v) for k, v in model.evaluate_dataframe(frames["test"]).items()},
        notes=notes,
        variant_id=variant_id,
        hyperparameters=hyperparameters,
        uncertainty=uncertainty,
    )


def _classification_candidate_metrics_from_model(
    *,
    model_family: str,
    model: Any,
    frames: dict[str, pd.DataFrame],
    task_type: str,
    threshold_policy: str | None,
    decision_threshold: float | None,
    notes: str,
    variant_id: str | None = None,
    hyperparameters: dict[str, Any] | None = None,
) -> CandidateMetrics:
    class_labels = [str(item) for item in getattr(model, "class_labels", [])]
    target_column = str(getattr(model, "target_column", "")).strip()
    if not class_labels or not target_column:
        raise RuntimeError("Classification candidate is missing class labels or target column.")
    positive_label = _minority_label_token(
        frame=frames["train"],
        target_column=target_column,
    )
    train_true = [str(item) for item in frames["train"][target_column].tolist()]
    validation_true = [str(item) for item in frames["validation"][target_column].tolist()]
    test_true = [str(item) for item in frames["test"][target_column].tolist()]
    raw_train_probabilities = model.predict_proba_dataframe(frames["train"])
    raw_validation_probabilities = model.predict_proba_dataframe(frames["validation"])
    raw_test_probabilities = model.predict_proba_dataframe(frames["test"])
    calibration = _fit_candidate_calibration(
        y_true=validation_true,
        probabilities=raw_validation_probabilities,
        class_labels=class_labels,
        positive_label=positive_label,
    )
    train_probabilities = _apply_candidate_calibration(
        probabilities=raw_train_probabilities,
        class_labels=class_labels,
        calibration=calibration,
    )
    validation_probabilities = _apply_candidate_calibration(
        probabilities=raw_validation_probabilities,
        class_labels=class_labels,
        calibration=calibration,
    )
    test_probabilities = _apply_candidate_calibration(
        probabilities=raw_test_probabilities,
        class_labels=class_labels,
        calibration=calibration,
    )
    decision_threshold = _select_binary_decision_threshold(
        probabilities=validation_probabilities,
        y_true=validation_true,
        class_labels=class_labels,
        positive_label=positive_label,
        task_type=task_type,
        threshold_policy=threshold_policy,
        explicit_threshold=decision_threshold,
    )
    train_metrics = _classification_metrics_from_probabilities(
        y_true=train_true,
        probabilities=train_probabilities,
        class_labels=class_labels,
        positive_label=positive_label,
        decision_threshold=decision_threshold,
    )
    validation_metrics = _classification_metrics_from_probabilities(
        y_true=validation_true,
        probabilities=validation_probabilities,
        class_labels=class_labels,
        positive_label=positive_label,
        decision_threshold=decision_threshold,
    )
    test_metrics = _classification_metrics_from_probabilities(
        y_true=test_true,
        probabilities=test_probabilities,
        class_labels=class_labels,
        positive_label=positive_label,
        decision_threshold=decision_threshold,
    )
    for bundle in (train_metrics, validation_metrics, test_metrics):
        bundle["decision_threshold"] = float(decision_threshold)
    return CandidateMetrics(
        model_family=model_family,
        train_metrics=train_metrics,
        validation_metrics=validation_metrics,
        test_metrics=test_metrics,
        notes=notes,
        variant_id=variant_id,
        hyperparameters=hyperparameters,
        calibration=calibration,
        uncertainty=_classification_uncertainty_payload(
            probabilities=validation_probabilities,
            class_labels=class_labels,
            positive_label=positive_label,
            y_true=validation_true,
        ),
    )


def _classification_candidate_metrics_with_context(
    *,
    model_family: str,
    model: Any,
    frames: dict[str, pd.DataFrame],
    task_type: str,
    threshold_policy: str | None,
    decision_threshold: float | None,
    notes: str,
    variant_id: str | None = None,
    hyperparameters: dict[str, Any] | None = None,
) -> CandidateMetrics:
    train_design = model._lagged_frame(frame=frames["train"])
    validation_design = model._lagged_frame(
        frame=frames["validation"],
        context_frame=frames["train"],
    )
    test_design = model._lagged_frame(
        frame=frames["test"],
        context_frame=pd.concat([frames["train"], frames["validation"]], ignore_index=True),
    )
    if train_design.shape[0] == 0 or validation_design.shape[0] == 0 or test_design.shape[0] == 0:
        raise ValueError("Lagged classification design frame is empty for one or more splits.")

    delegate_model = model._require_delegate()
    class_labels = [str(item) for item in getattr(model, "class_labels", [])]
    target_column = str(getattr(model, "target_column", "")).strip()
    if not class_labels or not target_column:
        raise RuntimeError("Lagged classification candidate is missing class labels or target column.")
    positive_label = _minority_label_token(
        frame=train_design,
        target_column=target_column,
    )
    train_true = [str(item) for item in train_design[target_column].tolist()]
    validation_true = [str(item) for item in validation_design[target_column].tolist()]
    test_true = [str(item) for item in test_design[target_column].tolist()]
    raw_train_probabilities = delegate_model.predict_proba_dataframe(train_design)
    raw_validation_probabilities = delegate_model.predict_proba_dataframe(validation_design)
    raw_test_probabilities = delegate_model.predict_proba_dataframe(test_design)
    calibration = _fit_candidate_calibration(
        y_true=validation_true,
        probabilities=raw_validation_probabilities,
        class_labels=class_labels,
        positive_label=positive_label,
    )
    train_probabilities = _apply_candidate_calibration(
        probabilities=raw_train_probabilities,
        class_labels=class_labels,
        calibration=calibration,
    )
    validation_probabilities = _apply_candidate_calibration(
        probabilities=raw_validation_probabilities,
        class_labels=class_labels,
        calibration=calibration,
    )
    test_probabilities = _apply_candidate_calibration(
        probabilities=raw_test_probabilities,
        class_labels=class_labels,
        calibration=calibration,
    )
    resolved_threshold = _select_binary_decision_threshold(
        probabilities=validation_probabilities,
        y_true=validation_true,
        class_labels=class_labels,
        positive_label=positive_label,
        task_type=task_type,
        threshold_policy=threshold_policy,
        explicit_threshold=decision_threshold,
    )
    train_metrics = _classification_metrics_from_probabilities(
        y_true=train_true,
        probabilities=train_probabilities,
        class_labels=class_labels,
        positive_label=positive_label,
        decision_threshold=resolved_threshold,
    )
    validation_metrics = _classification_metrics_from_probabilities(
        y_true=validation_true,
        probabilities=validation_probabilities,
        class_labels=class_labels,
        positive_label=positive_label,
        decision_threshold=resolved_threshold,
    )
    test_metrics = _classification_metrics_from_probabilities(
        y_true=test_true,
        probabilities=test_probabilities,
        class_labels=class_labels,
        positive_label=positive_label,
        decision_threshold=resolved_threshold,
    )
    for bundle in (train_metrics, validation_metrics, test_metrics):
        bundle["decision_threshold"] = float(resolved_threshold)
    return CandidateMetrics(
        model_family=model_family,
        train_metrics=train_metrics,
        validation_metrics=validation_metrics,
        test_metrics=test_metrics,
        notes=notes,
        variant_id=variant_id,
        hyperparameters=hyperparameters,
        calibration=calibration,
        uncertainty=_classification_uncertainty_payload(
            probabilities=validation_probabilities,
            class_labels=class_labels,
            positive_label=positive_label,
            y_true=validation_true,
        ),
    )


def _candidate_metrics_with_context(
    *,
    model_family: str,
    model: Any,
    frames: dict[str, pd.DataFrame],
    notes: str,
    variant_id: str | None = None,
    hyperparameters: dict[str, Any] | None = None,
) -> CandidateMetrics:
    train_metrics = model.evaluate_dataframe(frames["train"])
    validation_metrics = model.evaluate_dataframe(
        frames["validation"],
        context_frame=frames["train"],
    )
    test_metrics = model.evaluate_dataframe(
        frames["test"],
        context_frame=pd.concat([frames["train"], frames["validation"]], ignore_index=True),
    )
    return CandidateMetrics(
        model_family=model_family,
        train_metrics={k: float(v) for k, v in train_metrics.items()},
        validation_metrics={k: float(v) for k, v in validation_metrics.items()},
        test_metrics={k: float(v) for k, v in test_metrics.items()},
        notes=notes,
        variant_id=variant_id,
        hyperparameters=hyperparameters,
    )


def _classification_metrics_for_frame(
    *,
    model: Any,
    frame: pd.DataFrame,
    class_labels: list[str],
    positive_label: str | None,
    decision_threshold: float,
    calibration: dict[str, Any] | None = None,
) -> dict[str, float]:
    y_true = [str(item) for item in frame[str(getattr(model, "target_column", ""))].tolist()]
    probabilities = model.predict_proba_dataframe(frame)
    probabilities = _apply_candidate_calibration(
        probabilities=probabilities,
        class_labels=class_labels,
        calibration=calibration,
    )
    metrics = classification_metrics(
        y_true=y_true,
        probabilities=probabilities,
        class_labels=class_labels,
        positive_label=positive_label,
        decision_threshold=decision_threshold if len(class_labels) == 2 else None,
    ).to_dict()
    return {str(key): float(value) for key, value in metrics.items()}


def _minority_label_token(*, frame: pd.DataFrame, target_column: str) -> str | None:
    if target_column not in frame.columns:
        return None
    counts = frame[target_column].astype(str).value_counts()
    if counts.empty:
        return None
    return str(counts.sort_values(kind="stable").index[0])


def _select_binary_decision_threshold(
    *,
    probabilities: np.ndarray,
    y_true: list[str],
    class_labels: list[str],
    positive_label: str | None,
    task_type: str,
    threshold_policy: str | None,
    explicit_threshold: float | None,
) -> float:
    if len(class_labels) != 2 or not positive_label:
        return 0.5
    if explicit_threshold is not None:
        return float(max(0.01, min(0.99, explicit_threshold)))
    thresholds = [0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.45, 0.50]
    best_threshold = 0.5
    best_rank: tuple[float, ...] | None = None
    normalized_policy = str(threshold_policy or "").strip().lower() or "auto"
    for threshold in thresholds:
        metrics = classification_metrics(
            y_true=y_true,
            probabilities=probabilities,
            class_labels=class_labels,
            positive_label=positive_label,
            decision_threshold=threshold,
        ).to_dict()
        if normalized_policy == "favor_recall":
            rank = (
                -float(metrics.get("recall", 0.0)),
                -float(metrics.get("f1", 0.0)),
                -float(metrics.get("pr_auc", 0.0)),
                -float(metrics.get("precision", 0.0)),
                float(metrics.get("log_loss", float("inf"))),
            )
        elif normalized_policy == "favor_precision":
            rank = (
                -float(metrics.get("precision", 0.0)),
                -float(metrics.get("f1", 0.0)),
                -float(metrics.get("recall", 0.0)),
                -float(metrics.get("pr_auc", 0.0)),
                float(metrics.get("log_loss", float("inf"))),
            )
        elif normalized_policy == "favor_pr_auc":
            rank = (
                -float(metrics.get("pr_auc", 0.0)),
                -float(metrics.get("recall", 0.0)),
                -float(metrics.get("f1", 0.0)),
                -float(metrics.get("precision", 0.0)),
                float(metrics.get("log_loss", float("inf"))),
            )
        elif normalized_policy == "favor_f1":
            rank = (
                -float(metrics.get("f1", 0.0)),
                -float(metrics.get("recall", 0.0)),
                -float(metrics.get("precision", 0.0)),
                -float(metrics.get("pr_auc", 0.0)),
                float(metrics.get("log_loss", float("inf"))),
            )
        elif task_type in {"fraud_detection", "anomaly_detection"}:
            rank = (
                -float(metrics.get("recall", 0.0)),
                -float(metrics.get("pr_auc", 0.0)),
                -float(metrics.get("f1", 0.0)),
                -float(metrics.get("precision", 0.0)),
                float(metrics.get("log_loss", float("inf"))),
            )
        else:
            rank = (
                -float(metrics.get("f1", 0.0)),
                -float(metrics.get("accuracy", 0.0)),
                -float(metrics.get("precision", 0.0)),
                -float(metrics.get("recall", 0.0)),
                float(metrics.get("log_loss", float("inf"))),
            )
        if best_rank is None or rank < best_rank:
            best_rank = rank
            best_threshold = float(threshold)
    return best_threshold


def _classification_metrics_from_probabilities(
    *,
    y_true: list[str],
    probabilities: np.ndarray,
    class_labels: list[str],
    positive_label: str | None,
    decision_threshold: float,
) -> dict[str, float]:
    metrics = classification_metrics(
        y_true=y_true,
        probabilities=probabilities,
        class_labels=class_labels,
        positive_label=positive_label,
        decision_threshold=decision_threshold if len(class_labels) == 2 else None,
    ).to_dict()
    return {str(key): float(value) for key, value in metrics.items()}


def _select_best_candidate(
    candidates: list[CandidateMetrics],
    *,
    task_type: str,
    selection_metric: str | None = None,
    preferred_candidate_order: list[str] | None = None,
) -> CandidateMetrics:
    preferred_order = {
        str(model_family).strip(): index
        for index, model_family in enumerate(preferred_candidate_order or [])
        if str(model_family).strip()
    }
    ranked = sorted(
        candidates,
        key=lambda item: (
            _candidate_validation_rank(
                item=item,
                task_type=task_type,
                selection_metric=selection_metric,
            ),
            preferred_order.get(item.model_family, len(preferred_order) + _MODEL_TIEBREAK.get(item.model_family, 9)),
            _MODEL_TIEBREAK.get(item.model_family, 9),
        ),
    )
    return ranked[0]


def _resolve_selected_candidate(
    *,
    requested: str,
    candidates: list[CandidateMetrics],
    task_type: str,
    selection_metric: str | None = None,
    preferred_candidate_order: list[str] | None = None,
) -> CandidateMetrics:
    if requested == "auto":
        return _select_best_candidate(
            candidates,
            task_type=task_type,
            selection_metric=selection_metric,
            preferred_candidate_order=preferred_candidate_order,
        )
    matching = [item for item in candidates if item.model_family == requested]
    if matching:
        return _select_best_candidate(
            matching,
            task_type=task_type,
            selection_metric=selection_metric,
            preferred_candidate_order=preferred_candidate_order,
        )
    return _select_best_candidate(
        candidates,
        task_type=task_type,
        selection_metric=selection_metric,
        preferred_candidate_order=preferred_candidate_order,
    )


def _candidate_validation_rank(
    *,
    item: CandidateMetrics,
    task_type: str,
    selection_metric: str | None = None,
) -> tuple[float, ...]:
    metrics = item.validation_metrics
    explicit_metric_rank = _explicit_selection_metric_rank(
        metrics=metrics,
        task_type=task_type,
        selection_metric=selection_metric,
    )
    if explicit_metric_rank is not None:
        return explicit_metric_rank
    if is_classification_task(task_type):
        if task_type in {"fraud_detection", "anomaly_detection"}:
            return (
                -float(metrics.get("pr_auc", 0.0)),
                -float(metrics.get("recall", 0.0)),
                -float(metrics.get("f1", 0.0)),
                float(metrics.get("expected_calibration_error", float("inf"))),
                -float(metrics.get("accuracy", 0.0)),
                float(metrics.get("log_loss", float("inf"))),
            )
        return (
            -float(metrics.get("f1", 0.0)),
            -float(metrics.get("accuracy", 0.0)),
            -float(metrics.get("precision", 0.0)),
            -float(metrics.get("recall", 0.0)),
            float(metrics.get("expected_calibration_error", float("inf"))),
            float(metrics.get("log_loss", float("inf"))),
        )
    return (
        float(metrics.get("mae", float("inf"))),
        float(metrics.get("rmse", float("inf"))),
    )


def _explicit_selection_metric_rank(
    *,
    metrics: dict[str, float],
    task_type: str,
    selection_metric: str | None,
) -> tuple[float, ...] | None:
    normalized = str(selection_metric or "").strip().lower().replace("-", "_")
    aliases = {
        "": None,
        "auto": None,
        "stability_adjusted_mae": "mae",
        "mae_per_latency": "mae",
        "latency_weighted_f1": "f1",
    }
    resolved = aliases.get(normalized, normalized)
    if resolved is None:
        return None
    higher_is_better = {"accuracy", "precision", "recall", "f1", "pr_auc", "roc_auc", "r2"}
    lower_is_better = {"log_loss", "mae", "rmse"}
    if is_classification_task(task_type) and resolved in higher_is_better:
        return (
            -float(metrics.get(resolved, 0.0)),
            -float(metrics.get("f1", 0.0)),
            -float(metrics.get("accuracy", 0.0)),
            float(metrics.get("log_loss", float("inf"))),
        )
    if is_classification_task(task_type) and resolved in lower_is_better:
        return (
            float(metrics.get(resolved, float("inf"))),
            -float(metrics.get("f1", 0.0)),
            -float(metrics.get("accuracy", 0.0)),
        )
    if not is_classification_task(task_type) and resolved in lower_is_better:
        return (
            float(metrics.get(resolved, float("inf"))),
            float(metrics.get("mae", float("inf"))),
            float(metrics.get("rmse", float("inf"))),
        )
    if not is_classification_task(task_type) and resolved in higher_is_better:
        return (
            -float(metrics.get(resolved, 0.0)),
            float(metrics.get("mae", float("inf"))),
            float(metrics.get("rmse", float("inf"))),
        )
    return None


def _prepare_hpo_context(
    *,
    run_dir: Path,
    task_type: str,
    row_count: int,
    requested_family: str,
    preferred_candidate_order: list[str] | None,
    available_families: list[str],
) -> dict[str, Any]:
    budget_contract = derive_hpo_budget_contract(
        run_dir=run_dir,
        task_type=task_type,
        row_count=row_count,
        requested_family=requested_family,
        preferred_candidate_order=preferred_candidate_order,
        available_families=available_families,
    )
    architecture_search_space = build_architecture_search_space(
        task_type=task_type,
        selected_families=[str(item) for item in budget_contract.get("selected_families", [])],
    )
    warm_start_state = load_warm_start_state(
        run_dir=run_dir,
        selected_families=[str(item) for item in budget_contract.get("selected_families", [])],
    )
    portfolio_plan = build_portfolio_search_plan(
        budget_contract=budget_contract,
        architecture_search_space=architecture_search_space,
        warm_start_state=warm_start_state,
    )
    trial_plans = build_trial_plans(
        budget_contract=budget_contract,
        architecture_search_space=architecture_search_space,
        warm_start_state=warm_start_state,
        portfolio_plan=portfolio_plan,
    )
    deadline = time.monotonic() + float(budget_contract.get("max_wall_clock_seconds", 45) or 45)
    return {
        "budget_contract": budget_contract,
        "architecture_search_space": architecture_search_space,
        "warm_start_state": warm_start_state,
        "portfolio_plan": portfolio_plan,
        "trial_plans": trial_plans,
        "deadline": deadline,
        "family_reports": [],
        "trial_ledger": [],
    }


def _fit_hpo_family_candidates(
    *,
    family: str,
    trial_plans: list[dict[str, Any]],
    build_model: Any,
    build_candidate: Any,
    task_type: str,
    selection_metric: str | None,
    budget_contract: dict[str, Any],
    deadline: float,
) -> tuple[list[dict[str, Any]], dict[str, Any], list[dict[str, Any]]]:
    if not trial_plans:
        return (
            [],
            {
                "family": family,
                "status": "not_selected",
                "planned_trials": 0,
                "executed_trials": 0,
                "stop_reason": "not_selected_for_hpo",
            },
            [],
        )

    records: list[dict[str, Any]] = []
    ledger: list[dict[str, Any]] = []
    best_rank: tuple[float, ...] | None = None
    best_trial_id: str | None = None
    best_record: dict[str, Any] | None = None
    plateau_count = 0
    stop_reason = "trial_budget_exhausted"
    min_trials_before_stop = int(budget_contract.get("min_trials_before_plateau_stop", 3) or 3)
    plateau_patience = int(budget_contract.get("plateau_patience", 2) or 2)

    for index, trial_plan in enumerate(trial_plans, start=1):
        if time.monotonic() >= deadline:
            stop_reason = "wall_clock_exhausted"
            break
        model = build_model(dict(trial_plan.get("hyperparameters") or {}))
        candidate, rows_used = build_candidate(model, trial_plan)
        rank = _candidate_validation_rank(
            item=candidate,
            task_type=task_type,
            selection_metric=selection_metric,
        )
        improved_best = best_rank is None or rank < best_rank
        if improved_best:
            best_rank = rank
            best_trial_id = str(trial_plan.get("trial_id", "")).strip() or None
            best_record = {"candidate": candidate, "model": model, "rows_used": int(rows_used)}
            plateau_count = 0
        else:
            plateau_count += 1
        records.append({"candidate": candidate, "model": model, "rows_used": int(rows_used)})
        ledger.append(
            {
                "schema_version": TRIAL_LEDGER_RECORD_SCHEMA_VERSION,
                "trial_id": str(trial_plan.get("trial_id", "")).strip() or f"{family}_trial_{index:04d}",
                "family": family,
                "variant_id": str(trial_plan.get("variant_id", "")).strip() or f"{family}_variant_{index:04d}",
                "stage": str(trial_plan.get("stage", "probe")),
                "source": str(trial_plan.get("source", "search_space")),
                "hyperparameters": dict(candidate.hyperparameters or {}),
                "validation_metrics": dict(candidate.validation_metrics),
                "test_metrics": dict(candidate.test_metrics),
                "decision_threshold": candidate.validation_metrics.get("decision_threshold"),
                "improved_best": bool(improved_best),
            }
        )
        if plateau_count >= plateau_patience and len(records) >= min_trials_before_stop:
            stop_reason = "convergence_plateau"
            break

    if records and stop_reason == "trial_budget_exhausted" and len(records) < len(trial_plans):
        stop_reason = "wall_clock_exhausted"

    if best_record is None and records:
        best_record = records[0]
    return (
        records,
        {
            "family": family,
            "status": "ok" if records else "not_run",
            "planned_trials": len(trial_plans),
            "executed_trials": len(records),
            "stop_reason": stop_reason,
            "best_trial_id": best_trial_id,
            "warm_start_used": any(str(item.get("source", "")) == "warm_start" for item in trial_plans[: max(len(records), 1)]),
            "stages_planned": [
                str(item.get("stage", "probe"))
                for item in trial_plans
                if str(item.get("stage", "probe")).strip()
            ],
            "stages_executed": [
                str(item.get("stage", "probe"))
                for item in trial_plans[: len(records)]
                if str(item.get("stage", "probe")).strip()
            ],
            "best_validation_metrics": dict(best_record["candidate"].validation_metrics) if best_record else {},
        },
        ledger,
    )


def _write_hpo_artifacts(
    *,
    run_dir: Path,
    hpo_context: dict[str, Any],
    candidates: list[CandidateMetrics],
    selected_candidate: CandidateMetrics,
    best_by_validation: CandidateMetrics,
    task_type: str,
    threshold_policy: str | None,
) -> dict[str, str]:
    budget_contract = dict(hpo_context.get("budget_contract") or {})
    architecture_search_space = dict(hpo_context.get("architecture_search_space") or {})
    warm_start_state = dict(hpo_context.get("warm_start_state") or {})
    portfolio_plan = dict(hpo_context.get("portfolio_plan") or {})
    family_reports = list(hpo_context.get("family_reports") or [])
    trial_ledger = list(hpo_context.get("trial_ledger") or [])

    early_stopping_report = {
        "schema_version": EARLY_STOPPING_REPORT_SCHEMA_VERSION,
        "generated_at": _utc_now(),
        "status": "ok" if family_reports else "not_applicable",
        "family_count": len(family_reports),
        "plateau_triggered_count": sum(1 for item in family_reports if str(item.get("stop_reason")) == "convergence_plateau"),
        "wall_clock_exhausted_count": sum(1 for item in family_reports if str(item.get("stop_reason")) == "wall_clock_exhausted"),
        "families": family_reports,
        "summary": (
            f"Relaytic stopped `{sum(1 for item in family_reports if str(item.get('stop_reason')) == 'convergence_plateau')}` family search loop(s) on convergence plateau."
            if family_reports
            else "No HPO families were selected for this run."
        ),
    }
    search_loop_scorecard = {
        "schema_version": SEARCH_LOOP_SCORECARD_SCHEMA_VERSION,
        "generated_at": _utc_now(),
        "status": "ok" if trial_ledger else "not_applicable",
        "backend": str(budget_contract.get("backend", "deterministic_local_search")),
        "selected_model_family": selected_candidate.model_family,
        "selected_variant_id": selected_candidate.variant_id,
        "best_validation_model_family": best_by_validation.model_family,
        "best_validation_variant_id": best_by_validation.variant_id,
        "budget_profile": str(budget_contract.get("budget_profile", "operator")),
        "total_trials_executed": len(trial_ledger),
        "tuned_family_count": len(family_reports),
        "probe_family_count": len(portfolio_plan.get("families", [])) if isinstance(portfolio_plan.get("families"), list) else 0,
        "race_family_count": len(portfolio_plan.get("racing_families", [])) if isinstance(portfolio_plan.get("racing_families"), list) else 0,
        "finalist_count": len(portfolio_plan.get("finalists", [])) if isinstance(portfolio_plan.get("finalists"), list) else 0,
        "family_reports": family_reports,
        "warm_start_used": bool(warm_start_state.get("used")),
        "warm_start_influenced_families": [
            str(item)
            for item in portfolio_plan.get("warm_start_influenced_families", [])
            if str(item).strip()
        ],
        "skipped_deeper_work": [
            str(item)
            for item in portfolio_plan.get("skipped_deeper_work", [])
            if str(item).strip()
        ],
        "stop_reasons": sorted({str(item.get("stop_reason", "")).strip() for item in family_reports if str(item.get("stop_reason", "")).strip()}),
        "summary": (
            f"Relaytic executed `{len(trial_ledger)}` bounded HPO trial(s) across `{len(family_reports)}` family loop(s) and selected `{selected_candidate.model_family}`."
            if trial_ledger
            else "Relaytic did not execute bounded HPO trials for this run."
        ),
    }
    if is_classification_task(task_type):
        threshold_tuning_report = {
            "schema_version": THRESHOLD_TUNING_REPORT_SCHEMA_VERSION,
            "generated_at": _utc_now(),
            "status": "ok",
            "task_type": task_type,
            "threshold_policy": str(threshold_policy or "").strip() or "auto",
            "selected_model_family": selected_candidate.model_family,
            "selected_threshold": float(selected_candidate.test_metrics.get("decision_threshold", 0.5)),
            "candidates": [
                {
                    "model_family": item.model_family,
                    "variant_id": item.variant_id,
                    "decision_threshold": float(item.validation_metrics.get("decision_threshold", item.test_metrics.get("decision_threshold", 0.5))),
                    "calibration_status": str(dict(item.calibration or {}).get("status", "unknown")),
                    "validation_pr_auc": item.validation_metrics.get("pr_auc"),
                    "validation_f1": item.validation_metrics.get("f1"),
                }
                for item in candidates
            ],
            "summary": (
                f"Relaytic tuned binary decision thresholds and calibration across `{len(candidates)}` candidate(s) and selected `{selected_candidate.model_family}` at threshold `{float(selected_candidate.test_metrics.get('decision_threshold', 0.5)):.2f}`."
            ),
        }
    else:
        threshold_tuning_report = {
            "schema_version": THRESHOLD_TUNING_REPORT_SCHEMA_VERSION,
            "generated_at": _utc_now(),
            "status": "not_applicable",
            "task_type": task_type,
            "summary": "Threshold tuning is only applicable to classification and rare-event tasks.",
        }

    budget_path = write_json(hpo_artifact_path(run_dir, "hpo_budget_contract"), budget_contract, indent=2)
    search_space_path = write_json(hpo_artifact_path(run_dir, "architecture_search_space"), architecture_search_space, indent=2)
    warm_start_payload = {
        "schema_version": WARM_START_TRANSFER_REPORT_SCHEMA_VERSION,
        **warm_start_state,
    }
    warm_start_path = write_json(hpo_artifact_path(run_dir, "warm_start_transfer_report"), warm_start_payload, indent=2)
    early_stop_path = write_json(hpo_artifact_path(run_dir, "early_stopping_report"), early_stopping_report, indent=2)
    scorecard_path = write_json(hpo_artifact_path(run_dir, "search_loop_scorecard"), search_loop_scorecard, indent=2)
    threshold_path = write_json(hpo_artifact_path(run_dir, "threshold_tuning_report"), threshold_tuning_report, indent=2)
    ledger_path = _write_jsonl_records(hpo_artifact_path(run_dir, "trial_ledger"), trial_ledger)
    return {
        "hpo_budget_contract_path": str(budget_path),
        "architecture_search_space_path": str(search_space_path),
        "warm_start_transfer_report_path": str(warm_start_path),
        "early_stopping_report_path": str(early_stop_path),
        "search_loop_scorecard_path": str(scorecard_path),
        "threshold_tuning_report_path": str(threshold_path),
        "trial_ledger_path": str(ledger_path),
    }


def _write_jsonl_records(path: Path, records: list[dict[str, Any]]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True))
            handle.write("\n")
    return path


def _save_selected_model_state(*, model: Any, run_dir: Path, model_name: str) -> Path:
    filename = "model_state.json" if model_name == "linear_ridge" else f"{model_name}_state.json"
    path = Path(run_dir) / filename
    return model.save(path)


def _best_params_payload(
    *,
    selected_model_name: str,
    linear_rows_used: int,
    lagged_model: LaggedLinearSurrogate | None,
    lagged_tree_model: LaggedTreeEnsembleSurrogate | None,
    tree_model: BaggedTreeEnsembleSurrogate | None,
    boosted_tree_model: BoostedTreeEnsembleSurrogate | None,
    requested: str,
) -> dict[str, Any]:
    if selected_model_name == "linear_ridge":
        return {
            "requested_model_family": requested,
            "ridge": 1e-8,
            "training_rows_used": int(linear_rows_used),
        }
    if selected_model_name == "lagged_linear" and lagged_model is not None:
        return {
            "requested_model_family": requested,
            "ridge": float(lagged_model.ridge),
            "lag_horizon_samples": int(lagged_model.lag_horizon),
            "training_feature_count": int(len(lagged_model._lagged_feature_columns)),
        }
    if selected_model_name == "lagged_tree_ensemble" and lagged_tree_model is not None:
        return {
            "requested_model_family": requested,
            "lag_horizon_samples": int(lagged_tree_model.lag_horizon),
            "n_estimators": int(lagged_tree_model.n_estimators),
            "max_depth": int(lagged_tree_model.max_depth),
            "min_leaf": int(lagged_tree_model.min_leaf),
            "training_feature_count": int(len(lagged_tree_model._lagged_feature_columns)),
        }
    if selected_model_name == "boosted_tree_ensemble" and boosted_tree_model is not None:
        return {
            "requested_model_family": requested,
            "n_estimators": int(boosted_tree_model.n_estimators),
            "learning_rate": float(boosted_tree_model.learning_rate),
            "max_depth": int(boosted_tree_model.max_depth),
            "min_leaf": int(boosted_tree_model.min_leaf),
        }
    if tree_model is not None:
        return {
            "requested_model_family": requested,
            "n_estimators": int(tree_model.n_estimators),
            "max_depth": int(tree_model.max_depth),
            "min_leaf": int(tree_model.min_leaf),
        }
    return {"requested_model_family": requested}


def _build_regression_professional_analysis(
    *,
    selected_model_name: str,
    selected_model_obj: Any,
    selected_candidate: CandidateMetrics,
    prepared_frames: dict[str, pd.DataFrame],
    feature_columns: list[str],
    target_column: str,
    lag_horizon_samples: int | None,
) -> dict[str, Any]:
    train = selected_candidate.train_metrics
    validation = selected_candidate.validation_metrics
    test = selected_candidate.test_metrics
    train_mae = _metric_or_none(train, "mae")
    val_mae = _metric_or_none(validation, "mae")
    train_r2 = _metric_or_none(train, "r2")
    val_r2 = _metric_or_none(validation, "r2")
    test_r2 = _metric_or_none(test, "r2")

    diagnostics: list[str] = []
    risk_flags: list[str] = []
    if train_mae is not None and val_mae is not None:
        ratio = val_mae / max(train_mae, 1e-9)
        diagnostics.append(
            f"Generalization gap (MAE): train={train_mae:.4f}, val={val_mae:.4f}, ratio={ratio:.3f}."
        )
        if ratio > 1.25:
            risk_flags.append("overfitting_risk_high")
    if train_r2 is not None and val_r2 is not None:
        diagnostics.append(
            f"Generalization gap (R2): train={train_r2:.4f}, val={val_r2:.4f}, delta={train_r2 - val_r2:.4f}."
        )
    if test_r2 is not None and test_r2 < 0.50:
        risk_flags.append("underfitting_or_coverage_gap")

    feature_eval, y_true, y_pred = _extract_regression_eval_payload(
        selected_model_name=selected_model_name,
        selected_model_obj=selected_model_obj,
        prepared_frames=prepared_frames,
        feature_columns=feature_columns,
        target_column=target_column,
    )
    feedback = analyze_model_performance(
        y_true=y_true,
        y_pred=y_pred,
        feature_frame=feature_eval,
        top_k_regions=3,
        trajectory_budget=3,
    )
    feedback_payload = feedback.to_dict()
    residual = np.asarray(y_pred, dtype=float) - np.asarray(y_true, dtype=float)
    diagnostics.append(
        f"Residual check: mean={float(np.mean(residual)):.4f}, std={float(np.std(residual)):.4f}, abs_max={float(np.max(np.abs(residual))):.4f}."
    )
    uncertainty = fit_regression_residual_interval(y_true=y_true, y_pred=y_pred)
    if str(uncertainty.get("status", "")).strip() == "ok":
        diagnostics.append(
            "Validation interval fit: "
            f"target_coverage={float(uncertainty.get('coverage_target', 0.0)):.2f}, "
            f"estimated_coverage={float(uncertainty.get('coverage_estimate', 0.0)):.2f}, "
            f"margin={float(uncertainty.get('absolute_margin', 0.0)):.4f}."
        )

    suggestions = [
        str(item.get("rationale", "")).strip()
        for item in feedback_payload.get("trajectory_suggestions", [])
        if isinstance(item, dict) and str(item.get("rationale", "")).strip()
    ]
    summary = (
        f"{feedback_payload.get('summary', 'Regression evaluation complete.')} "
        f"Selected model `{selected_model_name}` with lag_horizon={int(lag_horizon_samples or 0)}."
    )
    return {
        "summary": summary.strip(),
        "diagnostics": diagnostics,
        "risk_flags": risk_flags,
        "high_error_regions": feedback_payload.get("bad_regions", []),
        "suggestions": suggestions[:3],
    }


def _build_classification_professional_analysis(
    *,
    selected_model_name: str,
    selected_model_obj: Any,
    selected_candidate: CandidateMetrics,
    prepared_frames: dict[str, pd.DataFrame],
    feature_columns: list[str],
    target_column: str,
    task_type: str,
) -> dict[str, Any]:
    train = selected_candidate.train_metrics
    validation = selected_candidate.validation_metrics
    test = selected_candidate.test_metrics
    train_f1 = _metric_or_none(train, "f1")
    val_f1 = _metric_or_none(validation, "f1")
    train_recall = _metric_or_none(train, "recall")
    val_recall = _metric_or_none(validation, "recall")
    test_recall = _metric_or_none(test, "recall")
    test_pr_auc = _metric_or_none(test, "pr_auc")
    test_brier = _metric_or_none(test, "brier_score")
    test_ece = _metric_or_none(test, "expected_calibration_error")

    diagnostics: list[str] = []
    risk_flags: list[str] = []
    if train_f1 is not None and val_f1 is not None:
        diagnostics.append(
            f"Generalization gap (F1): train={train_f1:.4f}, val={val_f1:.4f}, delta={train_f1 - val_f1:.4f}."
        )
        if train_f1 > max(val_f1 + 0.10, val_f1 * 1.10):
            risk_flags.append("overfitting_risk_high")
    if train_recall is not None and val_recall is not None:
        diagnostics.append(
            f"Minority recall stability: train={train_recall:.4f}, val={val_recall:.4f}."
        )
    if test_brier is not None or test_ece is not None:
        diagnostics.append(
            f"Calibration quality: brier={test_brier if test_brier is not None else float('nan'):.4f}, "
            f"ece={test_ece if test_ece is not None else float('nan'):.4f}."
        )
        if test_ece is not None and test_ece > 0.10:
            risk_flags.append("calibration_drift_risk")

    feature_eval, y_true, y_pred, probs, class_labels, decision_threshold = _extract_classification_eval_payload(
        selected_model_name=selected_model_name,
        selected_model_obj=selected_model_obj,
        selected_candidate=selected_candidate,
        prepared_frames=prepared_frames,
        feature_columns=feature_columns,
        target_column=target_column,
    )
    regions = _analyze_classification_error_regions(
        feature_frame=feature_eval,
        y_true=y_true,
        y_pred=y_pred,
        max_regions=3,
    )
    suggestions: list[str] = []
    for region in regions:
        suggestions.append(
            f"Increase labeled coverage in {region['feature']} range "
            f"[{region['lower_bound']:.3g}, {region['upper_bound']:.3g}] where error rate is "
            f"{region['error_rate']:.3f} (lift {region['error_lift']:.3f})."
        )
    if task_type in {"fraud_detection", "anomaly_detection"}:
        if test_recall is not None and test_recall < 0.70:
            risk_flags.append("minority_recall_below_target")
            suggestions.append("Collect more positive-event sequences and hard negatives near the decision boundary.")
        if test_pr_auc is not None and test_pr_auc < 0.35:
            risk_flags.append("precision_recall_separation_weak")
            suggestions.append("Add discriminative predictors and targeted event windows to improve PR-AUC.")

    if not suggestions:
        suggestions.append(
            "Collect additional boundary-crossing examples in underrepresented operating regions before increasing model complexity."
        )

    avg_conf = float(np.mean(np.max(probs, axis=1))) if probs.size else float("nan")
    diagnostics.append(
        f"Prediction confidence: mean_max_probability={avg_conf:.4f}, classes={len(class_labels)}, decision_threshold={decision_threshold:.2f}."
    )
    summary = (
        f"Classification evaluation complete for `{selected_model_name}`: "
        f"test_f1={_metric_or_none(test, 'f1') if _metric_or_none(test, 'f1') is not None else float('nan'):.4f}, "
        f"test_accuracy={_metric_or_none(test, 'accuracy') if _metric_or_none(test, 'accuracy') is not None else float('nan'):.4f}, "
        f"test_recall={_metric_or_none(test, 'recall') if _metric_or_none(test, 'recall') is not None else float('nan'):.4f}."
    )
    return {
        "summary": summary,
        "diagnostics": diagnostics,
        "risk_flags": risk_flags,
        "high_error_regions": regions,
        "suggestions": suggestions[:3],
    }


def _extract_regression_eval_payload(
    *,
    selected_model_name: str,
    selected_model_obj: Any,
    prepared_frames: dict[str, pd.DataFrame],
    feature_columns: list[str],
    target_column: str,
) -> tuple[pd.DataFrame, np.ndarray, np.ndarray]:
    if selected_model_name in {"lagged_linear", "lagged_tree_ensemble"} and hasattr(selected_model_obj, "_lagged_frame"):
        context = pd.concat([prepared_frames["train"], prepared_frames["validation"]], ignore_index=True)
        eval_frame = selected_model_obj._lagged_frame(
            frame=prepared_frames["test"],
            context_frame=context,
        )
        delegate = selected_model_obj._require_delegate()
        model_features = list(getattr(selected_model_obj, "_lagged_feature_columns", []))
        y_true = eval_frame[target_column].to_numpy(dtype=float)
        y_pred = delegate.predict_dataframe(eval_frame)
        return eval_frame[model_features].copy(), y_true, np.asarray(y_pred, dtype=float)

    eval_frame = prepared_frames["test"]
    y_true = eval_frame[target_column].to_numpy(dtype=float)
    y_pred = selected_model_obj.predict_dataframe(eval_frame)
    return eval_frame[feature_columns].copy(), y_true, np.asarray(y_pred, dtype=float)


def _extract_classification_eval_payload(
    *,
    selected_model_name: str,
    selected_model_obj: Any,
    selected_candidate: CandidateMetrics,
    prepared_frames: dict[str, pd.DataFrame],
    feature_columns: list[str],
    target_column: str,
) -> tuple[pd.DataFrame, list[str], list[str], np.ndarray, list[str], float]:
    if selected_model_name in {"lagged_logistic_regression", "lagged_tree_classifier"} and hasattr(selected_model_obj, "_lagged_frame"):
        context = pd.concat([prepared_frames["train"], prepared_frames["validation"]], ignore_index=True)
        eval_frame = selected_model_obj._lagged_frame(
            frame=prepared_frames["test"],
            context_frame=context,
        )
        delegate = selected_model_obj._require_delegate()
        model_features = list(getattr(selected_model_obj, "_lagged_feature_columns", []))
        probabilities = delegate.predict_proba_dataframe(eval_frame)
    else:
        eval_frame = prepared_frames["test"]
        model_features = list(feature_columns)
        probabilities = selected_model_obj.predict_proba_dataframe(eval_frame)
    probabilities = _apply_candidate_calibration(
        probabilities=probabilities,
        class_labels=[str(item) for item in getattr(selected_model_obj, "class_labels", [])],
        calibration=selected_candidate.calibration,
    )
    class_labels = [str(item) for item in getattr(selected_model_obj, "class_labels", [])]
    y_true = [str(item) for item in eval_frame[target_column].tolist()]
    positive_label = _minority_label_token(frame=prepared_frames["train"], target_column=target_column)
    decision_threshold = float(selected_candidate.test_metrics.get("decision_threshold", 0.5))
    y_pred = _predict_labels_from_probabilities(
        probabilities=probabilities,
        class_labels=class_labels,
        positive_label=positive_label,
        decision_threshold=decision_threshold,
    )
    return eval_frame[model_features].copy(), y_true, y_pred, probabilities, class_labels, decision_threshold


def _predict_labels_from_probabilities(
    *,
    probabilities: np.ndarray,
    class_labels: list[str],
    positive_label: str | None,
    decision_threshold: float,
) -> list[str]:
    if probabilities.size == 0 or not class_labels:
        return []
    if len(class_labels) == 2 and positive_label in class_labels:
        pos_idx = class_labels.index(str(positive_label))
        neg_idx = 1 - pos_idx
        out: list[str] = []
        for row in probabilities:
            if float(row[pos_idx]) >= float(decision_threshold):
                out.append(class_labels[pos_idx])
            else:
                out.append(class_labels[neg_idx])
        return out
    labels = np.asarray(class_labels, dtype=object)
    return [str(item) for item in labels[np.argmax(probabilities, axis=1)]]


def _analyze_classification_error_regions(
    *,
    feature_frame: pd.DataFrame,
    y_true: list[str],
    y_pred: list[str],
    max_regions: int = 3,
) -> list[dict[str, Any]]:
    if feature_frame.empty or not y_true or len(y_true) != len(y_pred):
        return []
    error = np.asarray([1.0 if truth != pred else 0.0 for truth, pred in zip(y_true, y_pred)], dtype=float)
    overall_error = float(np.mean(error))
    minimum_region_size = max(8, int(0.05 * len(error)))
    regions: list[dict[str, Any]] = []
    for feature in feature_frame.columns:
        numeric = pd.to_numeric(feature_frame[feature], errors="coerce")
        valid = numeric.notna()
        if int(valid.sum()) < minimum_region_size:
            continue
        values = numeric[valid].to_numpy(dtype=float)
        errors = error[valid.to_numpy()]
        boundaries = np.unique(np.quantile(values, [0.0, 0.25, 0.5, 0.75, 1.0]))
        if len(boundaries) < 2:
            continue
        for idx in range(len(boundaries) - 1):
            low = float(boundaries[idx])
            high = float(boundaries[idx + 1])
            if idx == len(boundaries) - 2:
                mask = (values >= low) & (values <= high)
            else:
                mask = (values >= low) & (values < high)
            count = int(np.sum(mask))
            if count < minimum_region_size:
                continue
            region_error = float(np.mean(errors[mask]))
            lift = region_error - overall_error
            if lift <= 0.01:
                continue
            regions.append(
                {
                    "feature": str(feature),
                    "lower_bound": low,
                    "upper_bound": high,
                    "sample_count": count,
                    "error_rate": region_error,
                    "error_lift": lift,
                }
            )
    regions.sort(key=lambda item: float(item.get("error_lift", 0.0)), reverse=True)
    return regions[: max(int(max_regions), 1)]


def _metric_or_none(metrics: dict[str, float], key: str) -> float | None:
    try:
        if key not in metrics:
            return None
        return float(metrics[key])
    except (TypeError, ValueError):
        return None


def _resolve_lag_horizon(
    *,
    data_mode: str,
    requested: str,
    lag_horizon_samples: int | None,
    split: DatasetSplit,
) -> int | None:
    if data_mode != "time_series":
        return None
    max_safe = max(1, min(12, int(split.train_indices.size) - 2))
    if max_safe <= 0:
        return None
    if lag_horizon_samples is not None:
        return max(1, min(int(lag_horizon_samples), max_safe))
    if requested in {"lagged_linear", "lagged_logistic_regression"}:
        return min(4, max_safe)
    return min(3, max_safe)


def _infer_data_mode(*, frame: pd.DataFrame, timestamp_column: str | None) -> str:
    if not timestamp_column or timestamp_column not in frame.columns:
        return "steady_state"
    numeric = pd.to_numeric(frame[timestamp_column], errors="coerce")
    valid = numeric.dropna()
    if len(valid) >= 8:
        diffs = valid.diff().dropna()
        if int((diffs > 0).sum()) >= max(5, int(len(diffs) * 0.7)):
            return "time_series"
    parsed = pd.to_datetime(frame[timestamp_column], errors="coerce")
    if float(parsed.notna().mean()) >= 0.8:
        diffs_dt = parsed.dropna().diff().dt.total_seconds().dropna()
        if int((diffs_dt > 0).sum()) >= max(5, int(len(diffs_dt) * 0.7)):
            return "time_series"
    return "steady_state"


def _fit_regression_linear_candidates(
    *,
    frames: dict[str, pd.DataFrame],
    model_feature_columns: list[str],
    target_column: str,
    hpo_context: dict[str, Any],
    task_type: str,
    selection_metric: str | None,
) -> list[dict[str, Any]]:
    trial_plans = list(dict(hpo_context.get("trial_plans") or {}).get("linear_ridge") or [])
    if trial_plans:
        def _build_model(params: dict[str, Any]) -> IncrementalLinearSurrogate:
            return IncrementalLinearSurrogate(
                feature_columns=model_feature_columns,
                target_column=target_column,
                ridge=float(params.get("ridge", 1e-4)),
            )

        def _build_candidate(model: Any, trial_plan: dict[str, Any]) -> tuple[CandidateMetrics, int]:
            rows_used = int(model.fit_dataframe(frames["train"]))
            hyperparameters = dict(trial_plan.get("hyperparameters") or {})
            hyperparameters.update(
                {
                    "training_rows_used": int(rows_used),
                    "training_feature_count": int(len(model_feature_columns)),
                }
            )
            candidate = _candidate_metrics_from_model(
                model_family="linear_ridge",
                model=model,
                frames=frames,
                notes=(
                    "Budgeted HPO ridge baseline with explicit search-space trial "
                    f"`{trial_plan.get('trial_id', '')}`. Train rows used={rows_used}."
                ),
                variant_id=str(trial_plan.get("variant_id", "hpo_linear_ridge")),
                hyperparameters=hyperparameters,
            )
            return candidate, rows_used

        records, report, ledger = _fit_hpo_family_candidates(
            family="linear_ridge",
            trial_plans=trial_plans,
            build_model=_build_model,
            build_candidate=_build_candidate,
            task_type=task_type,
            selection_metric=selection_metric,
            budget_contract=dict(hpo_context.get("budget_contract") or {}),
            deadline=float(hpo_context.get("deadline", time.monotonic() + 30.0)),
        )
        hpo_context.setdefault("family_reports", []).append(report)
        hpo_context.setdefault("trial_ledger", []).extend(ledger)
        return records

    variants = [
        ("ridge_default", {"ridge": 1e-8}),
        ("ridge_regularized", {"ridge": 1e-4}),
        ("ridge_strong", {"ridge": 1e-2}),
    ]
    records: list[dict[str, Any]] = []
    for variant_id, params in variants:
        model = IncrementalLinearSurrogate(
            feature_columns=model_feature_columns,
            target_column=target_column,
            ridge=float(params["ridge"]),
        )
        rows_used = model.fit_dataframe(frames["train"])
        candidate = _candidate_metrics_from_model(
            model_family="linear_ridge",
            model=model,
            frames=frames,
            notes=(
                "Split-safe ridge baseline with executed feature engineering and "
                f"variant `{variant_id}`. Train rows used={rows_used}."
            ),
            variant_id=variant_id,
            hyperparameters={
                "ridge": float(params["ridge"]),
                "training_rows_used": int(rows_used),
                "training_feature_count": int(len(model_feature_columns)),
            },
        )
        records.append({"candidate": candidate, "model": model, "rows_used": int(rows_used)})
    return records


def _fit_regression_tree_candidates(
    *,
    family: str,
    frames: dict[str, pd.DataFrame],
    model_feature_columns: list[str],
    target_column: str,
    hpo_context: dict[str, Any],
    task_type: str,
    selection_metric: str | None,
) -> list[dict[str, Any]]:
    trial_plans = list(dict(hpo_context.get("trial_plans") or {}).get(family) or [])
    if trial_plans:
        def _build_model(params: dict[str, Any]) -> Any:
            model_class = BoostedTreeEnsembleSurrogate if family == "boosted_tree_ensemble" else BaggedTreeEnsembleSurrogate
            return model_class(
                feature_columns=model_feature_columns,
                target_column=target_column,
                n_estimators=int(params.get("n_estimators", 12)),
                max_depth=int(params.get("max_depth", 4)),
                min_leaf=int(params.get("min_leaf", 6)),
                **({"learning_rate": float(params.get("learning_rate", 0.6))} if family == "boosted_tree_ensemble" else {}),
            )

        def _build_candidate(model: Any, trial_plan: dict[str, Any]) -> tuple[CandidateMetrics, int]:
            rows_used = int(model.fit_dataframe(frames["train"]))
            hyperparameters = dict(trial_plan.get("hyperparameters") or {})
            hyperparameters.update(
                {
                    "training_rows_used": int(rows_used),
                    "training_feature_count": int(len(model_feature_columns)),
                }
            )
            candidate = _candidate_metrics_from_model(
                model_family=family,
                model=model,
                frames=frames,
                notes=(
                    "Budgeted regression-tree HPO trial with explicit search-space exploration "
                    f"`{trial_plan.get('trial_id', '')}`. Train rows used={rows_used}."
                ),
                variant_id=str(trial_plan.get("variant_id", f"hpo_{family}")),
                hyperparameters=hyperparameters,
            )
            return candidate, rows_used

        records, report, ledger = _fit_hpo_family_candidates(
            family=family,
            trial_plans=trial_plans,
            build_model=_build_model,
            build_candidate=_build_candidate,
            task_type=task_type,
            selection_metric=selection_metric,
            budget_contract=dict(hpo_context.get("budget_contract") or {}),
            deadline=float(hpo_context.get("deadline", time.monotonic() + 30.0)),
        )
        hpo_context.setdefault("family_reports", []).append(report)
        hpo_context.setdefault("trial_ledger", []).extend(ledger)
        return records

    if family == "boosted_tree_ensemble":
        variants = [
            ("boosted_fast", {"n_estimators": 16, "learning_rate": 0.45, "max_depth": 3, "min_leaf": 6}),
            ("boosted_balanced", {"n_estimators": 24, "learning_rate": 0.60, "max_depth": 3, "min_leaf": 5}),
            ("boosted_wide", {"n_estimators": 32, "learning_rate": 0.35, "max_depth": 4, "min_leaf": 4}),
        ]
        model_class = BoostedTreeEnsembleSurrogate
    else:
        variants = [
            ("bagged_fast", {"n_estimators": 8, "max_depth": 3, "min_leaf": 8}),
            ("bagged_balanced", {"n_estimators": 12, "max_depth": 4, "min_leaf": 6}),
            ("bagged_wide", {"n_estimators": 20, "max_depth": 5, "min_leaf": 4}),
        ]
        model_class = BaggedTreeEnsembleSurrogate
    records: list[dict[str, Any]] = []
    for variant_id, params in variants:
        model = model_class(
            feature_columns=model_feature_columns,
            target_column=target_column,
            **params,
        )
        rows_used = model.fit_dataframe(frames["train"])
        candidate = _candidate_metrics_from_model(
            model_family=family,
            model=model,
            frames=frames,
            notes=(
                "Bounded tree-search candidate with executed feature engineering and "
                f"variant `{variant_id}`. Train rows used={rows_used}."
            ),
            variant_id=variant_id,
            hyperparameters={
                **{key: (float(value) if isinstance(value, float) else int(value)) for key, value in params.items()},
                "training_rows_used": int(rows_used),
                "training_feature_count": int(len(model_feature_columns)),
            },
        )
        records.append({"candidate": candidate, "model": model, "rows_used": int(rows_used)})
    return records


def _fit_logistic_candidates(
    *,
    frames: dict[str, pd.DataFrame],
    model_feature_columns: list[str],
    target_column: str,
    task_type: str,
    threshold_policy: str | None,
    decision_threshold: float | None,
    hpo_context: dict[str, Any],
    selection_metric: str | None,
) -> list[dict[str, Any]]:
    trial_plans = list(dict(hpo_context.get("trial_plans") or {}).get("logistic_regression") or [])
    if trial_plans:
        def _build_model(params: dict[str, Any]) -> LogisticClassificationSurrogate:
            return LogisticClassificationSurrogate(
                feature_columns=model_feature_columns,
                target_column=target_column,
                learning_rate=float(params.get("learning_rate", 0.25)),
                epochs=int(params.get("epochs", 350)),
                l2=float(params.get("l2", 1e-4)),
            )

        def _build_candidate(model: Any, trial_plan: dict[str, Any]) -> tuple[CandidateMetrics, int]:
            rows_used = int(model.fit_dataframe(frames["train"]))
            hyperparameters = dict(trial_plan.get("hyperparameters") or {})
            hyperparameters.update(
                {
                    "training_rows_used": int(rows_used),
                    "class_count": int(len(model.class_labels)),
                    "training_feature_count": int(len(model_feature_columns)),
                }
            )
            candidate = _classification_candidate_metrics_from_model(
                model_family="logistic_regression",
                model=model,
                frames=frames,
                task_type=task_type,
                threshold_policy=threshold_policy,
                decision_threshold=decision_threshold,
                notes=(
                    "Budgeted logistic HPO trial with validation threshold tuning and calibration "
                    f"`{trial_plan.get('trial_id', '')}`. Train rows used={rows_used}."
                ),
                variant_id=str(trial_plan.get("variant_id", "hpo_logistic_regression")),
                hyperparameters=hyperparameters,
            )
            return candidate, rows_used

        records, report, ledger = _fit_hpo_family_candidates(
            family="logistic_regression",
            trial_plans=trial_plans,
            build_model=_build_model,
            build_candidate=_build_candidate,
            task_type=task_type,
            selection_metric=selection_metric,
            budget_contract=dict(hpo_context.get("budget_contract") or {}),
            deadline=float(hpo_context.get("deadline", time.monotonic() + 30.0)),
        )
        hpo_context.setdefault("family_reports", []).append(report)
        hpo_context.setdefault("trial_ledger", []).extend(ledger)
        return records

    variants = [
        ("logistic_default", {"learning_rate": 0.25, "epochs": 350, "l2": 1e-4}),
        ("logistic_stable", {"learning_rate": 0.15, "epochs": 500, "l2": 1e-3}),
        ("logistic_sharp", {"learning_rate": 0.35, "epochs": 260, "l2": 5e-5}),
    ]
    records: list[dict[str, Any]] = []
    for variant_id, params in variants:
        model = LogisticClassificationSurrogate(
            feature_columns=model_feature_columns,
            target_column=target_column,
            **params,
        )
        rows_used = model.fit_dataframe(frames["train"])
        candidate = _classification_candidate_metrics_from_model(
            model_family="logistic_regression",
            model=model,
            frames=frames,
            task_type=task_type,
            threshold_policy=threshold_policy,
            decision_threshold=decision_threshold,
            notes=(
                "One-vs-rest logistic classifier with executed feature engineering and "
                f"variant `{variant_id}`. Train rows used={rows_used}."
            ),
            variant_id=variant_id,
            hyperparameters={
                "learning_rate": float(params["learning_rate"]),
                "epochs": int(params["epochs"]),
                "l2": float(params["l2"]),
                "training_rows_used": int(rows_used),
                "class_count": int(len(model.class_labels)),
                "training_feature_count": int(len(model_feature_columns)),
            },
        )
        records.append({"candidate": candidate, "model": model, "rows_used": int(rows_used)})
    return records


def _fit_classifier_tree_candidates(
    *,
    family: str,
    frames: dict[str, pd.DataFrame],
    model_feature_columns: list[str],
    target_column: str,
    task_type: str,
    threshold_policy: str | None,
    decision_threshold: float | None,
    hpo_context: dict[str, Any],
    selection_metric: str | None,
) -> list[dict[str, Any]]:
    trial_plans = list(dict(hpo_context.get("trial_plans") or {}).get(family) or [])
    if trial_plans:
        def _build_model(params: dict[str, Any]) -> Any:
            model_class = BoostedTreeClassifierSurrogate if family == "boosted_tree_classifier" else BaggedTreeClassifierSurrogate
            return model_class(
                feature_columns=model_feature_columns,
                target_column=target_column,
                n_estimators=int(params.get("n_estimators", 12)),
                max_depth=int(params.get("max_depth", 4)),
                min_leaf=int(params.get("min_leaf", 6)),
                **({"learning_rate": float(params.get("learning_rate", 0.6))} if family == "boosted_tree_classifier" else {}),
            )

        def _build_candidate(model: Any, trial_plan: dict[str, Any]) -> tuple[CandidateMetrics, int]:
            rows_used = int(model.fit_dataframe(frames["train"]))
            hyperparameters = dict(trial_plan.get("hyperparameters") or {})
            hyperparameters.update(
                {
                    "training_rows_used": int(rows_used),
                    "class_count": int(len(model.class_labels)),
                    "training_feature_count": int(len(model_feature_columns)),
                }
            )
            candidate = _classification_candidate_metrics_from_model(
                model_family=family,
                model=model,
                frames=frames,
                task_type=task_type,
                threshold_policy=threshold_policy,
                decision_threshold=decision_threshold,
                notes=(
                    "Budgeted classifier-tree HPO trial with explicit threshold tuning "
                    f"`{trial_plan.get('trial_id', '')}`. Train rows used={rows_used}."
                ),
                variant_id=str(trial_plan.get("variant_id", f"hpo_{family}")),
                hyperparameters=hyperparameters,
            )
            return candidate, rows_used

        records, report, ledger = _fit_hpo_family_candidates(
            family=family,
            trial_plans=trial_plans,
            build_model=_build_model,
            build_candidate=_build_candidate,
            task_type=task_type,
            selection_metric=selection_metric,
            budget_contract=dict(hpo_context.get("budget_contract") or {}),
            deadline=float(hpo_context.get("deadline", time.monotonic() + 30.0)),
        )
        hpo_context.setdefault("family_reports", []).append(report)
        hpo_context.setdefault("trial_ledger", []).extend(ledger)
        return records

    if family == "boosted_tree_classifier":
        variants = [
            ("boosted_classifier_fast", {"n_estimators": 16, "learning_rate": 0.45, "max_depth": 3, "min_leaf": 6}),
            ("boosted_classifier_balanced", {"n_estimators": 24, "learning_rate": 0.60, "max_depth": 3, "min_leaf": 5}),
            ("boosted_classifier_wide", {"n_estimators": 32, "learning_rate": 0.35, "max_depth": 4, "min_leaf": 4}),
        ]
        model_class = BoostedTreeClassifierSurrogate
    else:
        variants = [
            ("bagged_classifier_fast", {"n_estimators": 8, "max_depth": 3, "min_leaf": 8}),
            ("bagged_classifier_balanced", {"n_estimators": 12, "max_depth": 4, "min_leaf": 6}),
            ("bagged_classifier_wide", {"n_estimators": 20, "max_depth": 5, "min_leaf": 4}),
        ]
        model_class = BaggedTreeClassifierSurrogate
    records: list[dict[str, Any]] = []
    for variant_id, params in variants:
        model = model_class(
            feature_columns=model_feature_columns,
            target_column=target_column,
            **params,
        )
        rows_used = model.fit_dataframe(frames["train"])
        candidate = _classification_candidate_metrics_from_model(
            model_family=family,
            model=model,
            frames=frames,
            task_type=task_type,
            threshold_policy=threshold_policy,
            decision_threshold=decision_threshold,
            notes=(
                "Bounded classifier-search candidate with executed feature engineering and "
                f"variant `{variant_id}`. Train rows used={rows_used}."
            ),
            variant_id=variant_id,
            hyperparameters={
                **{key: (float(value) if isinstance(value, float) else int(value)) for key, value in params.items()},
                "training_rows_used": int(rows_used),
                "class_count": int(len(model.class_labels)),
                "training_feature_count": int(len(model_feature_columns)),
            },
        )
        records.append({"candidate": candidate, "model": model, "rows_used": int(rows_used)})
    return records


def _fit_regression_estimator_candidates(
    *,
    frames: dict[str, pd.DataFrame],
    model_feature_columns: list[str],
    target_column: str,
    requested_family: str | None,
    hpo_context: dict[str, Any],
    task_type: str,
    selection_metric: str | None,
) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    planned_families = {
        str(key).strip()
        for key in dict(hpo_context.get("trial_plans") or {}).keys()
        if str(key).strip()
    }
    hpo_families = [
        family
        for family in [str(item).strip() for item in dict(hpo_context.get("budget_contract") or {}).get("selected_families", [])]
        if family in _REGRESSION_ADAPTER_FAMILIES
    ]
    for family in hpo_families:
        if requested_family and family != requested_family:
            continue
        trial_plans = list(dict(hpo_context.get("trial_plans") or {}).get(family) or [])
        if not trial_plans:
            continue

        def _build_model(params: dict[str, Any], *, selected_family: str = family) -> Any:
            return build_regression_estimator_surrogate(
                family=selected_family,
                feature_columns=model_feature_columns,
                target_column=target_column,
                hyperparameters=dict(params),
            )

        def _build_candidate(model: Any, trial_plan: dict[str, Any], *, selected_family: str = family) -> tuple[CandidateMetrics, int]:
            rows_used = int(model.fit_dataframe(frames["train"]))
            hyperparameters = dict(trial_plan.get("hyperparameters") or {})
            hyperparameters.update(
                {
                    "training_rows_used": int(rows_used),
                    "training_feature_count": int(len(model_feature_columns)),
                }
            )
            candidate = _candidate_metrics_from_model(
                model_family=selected_family,
                model=model,
                frames=frames,
                notes=(
                    "Budgeted estimator-family HPO trial from the Slice 15C search space "
                    f"`{trial_plan.get('trial_id', '')}`. Train rows used={rows_used}."
                ),
                variant_id=str(trial_plan.get("variant_id", f"hpo_{selected_family}")),
                hyperparameters=hyperparameters,
            )
            return candidate, rows_used

        family_records, report, ledger = _fit_hpo_family_candidates(
            family=family,
            trial_plans=trial_plans,
            build_model=_build_model,
            build_candidate=_build_candidate,
            task_type=task_type,
            selection_metric=selection_metric,
            budget_contract=dict(hpo_context.get("budget_contract") or {}),
            deadline=float(hpo_context.get("deadline", time.monotonic() + 30.0)),
        )
        hpo_context.setdefault("family_reports", []).append(report)
        hpo_context.setdefault("trial_ledger", []).extend(ledger)
        records.extend(family_records)

    for variant in build_regression_estimator_variants(
        feature_columns=model_feature_columns,
        target_column=target_column,
    ):
        family = str(variant["family"])
        if family in planned_families:
            continue
        if requested_family and family != requested_family:
            continue
        model = variant["model"]
        rows_used = model.fit_dataframe(frames["train"])
        hyperparameters = dict(variant.get("hyperparameters") or {})
        hyperparameters.update(
            {
                "training_rows_used": int(rows_used),
                "training_feature_count": int(len(model_feature_columns)),
            }
        )
        candidate = _candidate_metrics_from_model(
            model_family=family,
            model=model,
            frames=frames,
            notes=(
                "Expanded architecture candidate routed through the Slice 15B estimator registry with "
                f"variant `{variant['variant_id']}`. Train rows used={rows_used}."
            ),
            variant_id=str(variant["variant_id"]),
            hyperparameters=hyperparameters,
        )
        records.append({"candidate": candidate, "model": model, "rows_used": int(rows_used)})
    return records


def _fit_classification_estimator_candidates(
    *,
    frames: dict[str, pd.DataFrame],
    model_feature_columns: list[str],
    target_column: str,
    task_type: str,
    threshold_policy: str | None,
    decision_threshold: float | None,
    class_count: int,
    requested_family: str | None,
    hpo_context: dict[str, Any],
    selection_metric: str | None,
) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    planned_families = {
        str(key).strip()
        for key in dict(hpo_context.get("trial_plans") or {}).keys()
        if str(key).strip()
    }
    hpo_families = [
        family
        for family in [str(item).strip() for item in dict(hpo_context.get("budget_contract") or {}).get("selected_families", [])]
        if family in _CLASSIFICATION_ADAPTER_FAMILIES
    ]
    for family in hpo_families:
        if requested_family and family != requested_family:
            continue
        trial_plans = list(dict(hpo_context.get("trial_plans") or {}).get(family) or [])
        if not trial_plans:
            continue

        def _build_model(params: dict[str, Any], *, selected_family: str = family) -> Any:
            return build_classification_estimator_surrogate(
                family=selected_family,
                feature_columns=model_feature_columns,
                target_column=target_column,
                hyperparameters=dict(params),
                class_count=class_count,
            )

        def _build_candidate(model: Any, trial_plan: dict[str, Any], *, selected_family: str = family) -> tuple[CandidateMetrics, int]:
            rows_used = int(model.fit_dataframe(frames["train"]))
            hyperparameters = dict(trial_plan.get("hyperparameters") or {})
            hyperparameters.update(
                {
                    "training_rows_used": int(rows_used),
                    "class_count": int(len(model.class_labels)),
                    "training_feature_count": int(len(model_feature_columns)),
                }
            )
            candidate = _classification_candidate_metrics_from_model(
                model_family=selected_family,
                model=model,
                frames=frames,
                task_type=task_type,
                threshold_policy=threshold_policy,
                decision_threshold=decision_threshold,
                notes=(
                    "Budgeted estimator-family HPO trial with threshold tuning and calibration "
                    f"`{trial_plan.get('trial_id', '')}`. Train rows used={rows_used}."
                ),
                variant_id=str(trial_plan.get("variant_id", f"hpo_{selected_family}")),
                hyperparameters=hyperparameters,
            )
            return candidate, rows_used

        family_records, report, ledger = _fit_hpo_family_candidates(
            family=family,
            trial_plans=trial_plans,
            build_model=_build_model,
            build_candidate=_build_candidate,
            task_type=task_type,
            selection_metric=selection_metric,
            budget_contract=dict(hpo_context.get("budget_contract") or {}),
            deadline=float(hpo_context.get("deadline", time.monotonic() + 30.0)),
        )
        hpo_context.setdefault("family_reports", []).append(report)
        hpo_context.setdefault("trial_ledger", []).extend(ledger)
        records.extend(family_records)

    for variant in build_classification_estimator_variants(
        feature_columns=model_feature_columns,
        target_column=target_column,
        class_count=class_count,
    ):
        family = str(variant["family"])
        if family in planned_families:
            continue
        if requested_family and family != requested_family:
            continue
        model = variant["model"]
        rows_used = model.fit_dataframe(frames["train"])
        hyperparameters = dict(variant.get("hyperparameters") or {})
        hyperparameters.update(
            {
                "training_rows_used": int(rows_used),
                "class_count": int(len(model.class_labels)),
                "training_feature_count": int(len(model_feature_columns)),
            }
        )
        candidate = _classification_candidate_metrics_from_model(
            model_family=family,
            model=model,
            frames=frames,
            task_type=task_type,
            threshold_policy=threshold_policy,
            decision_threshold=decision_threshold,
            notes=(
                "Expanded architecture candidate routed through the Slice 15B estimator registry with "
                f"variant `{variant['variant_id']}`. Train rows used={rows_used}."
            ),
            variant_id=str(variant["variant_id"]),
            hyperparameters=hyperparameters,
        )
        records.append({"candidate": candidate, "model": model, "rows_used": int(rows_used)})
    return records


def _fit_candidate_calibration(
    *,
    y_true: list[str],
    probabilities: np.ndarray,
    class_labels: list[str],
    positive_label: str | None,
) -> dict[str, Any]:
    if len(class_labels) != 2 or not positive_label or positive_label not in class_labels:
        return {"status": "identity", "method": "none"}
    pos_idx = class_labels.index(str(positive_label))
    return fit_binary_platt_calibrator(
        y_true=y_true,
        positive_scores=np.asarray(probabilities, dtype=float)[:, pos_idx],
        positive_label=str(positive_label),
    )


def _apply_candidate_calibration(
    *,
    probabilities: np.ndarray,
    class_labels: list[str],
    calibration: dict[str, Any] | None,
) -> np.ndarray:
    return apply_binary_platt_calibrator(
        probabilities=np.asarray(probabilities, dtype=float),
        class_labels=list(class_labels),
        calibrator=calibration,
    )


def _classification_uncertainty_payload(
    *,
    probabilities: np.ndarray,
    class_labels: list[str],
    positive_label: str | None,
    y_true: list[str],
) -> dict[str, Any]:
    normalized = np.asarray(probabilities, dtype=float)
    if normalized.size == 0:
        return {"status": "unavailable", "kind": "classification"}
    max_conf = np.max(normalized, axis=1)
    payload: dict[str, Any] = {
        "status": "ok",
        "kind": "classification",
        "mean_max_confidence": float(np.mean(max_conf)),
        "low_confidence_fraction": float(np.mean(max_conf < 0.60)),
    }
    if len(class_labels) == 2 and positive_label and positive_label in class_labels:
        pos_idx = class_labels.index(str(positive_label))
        positive_scores = normalized[:, pos_idx]
        payload["mean_positive_probability"] = float(np.mean(positive_scores))
        payload["positive_probability_std"] = float(np.std(positive_scores))
    return payload


def _regression_uncertainty_payload(
    *,
    selected_model_name: str,
    selected_model_obj: Any,
    prepared_frames: dict[str, pd.DataFrame],
    feature_columns: list[str],
    target_column: str,
) -> dict[str, Any]:
    if selected_model_name in {"lagged_linear", "lagged_tree_ensemble"} and hasattr(selected_model_obj, "_lagged_frame"):
        validation_design = selected_model_obj._lagged_frame(
            frame=prepared_frames["validation"],
            context_frame=prepared_frames["train"],
        )
        if validation_design.empty:
            return {"status": "unavailable", "kind": "regression"}
        delegate = selected_model_obj._require_delegate()
        y_true = validation_design[target_column].to_numpy(dtype=float)
        y_pred = delegate.predict_dataframe(validation_design)
        return fit_regression_residual_interval(y_true=y_true, y_pred=y_pred)
    validation = prepared_frames["validation"]
    if validation.empty:
        return {"status": "unavailable", "kind": "regression"}
    y_true = validation[target_column].to_numpy(dtype=float)
    y_pred = selected_model_obj.predict_dataframe(validation)
    return fit_regression_residual_interval(y_true=y_true, y_pred=y_pred)


def _prepare_split_safe_frames(
    *,
    split_frames: dict[str, pd.DataFrame],
    feature_columns: list[str],
    target_column: str,
    missing_data_strategy: str,
    fill_constant_value: float | None,
    task_type: str,
) -> dict[str, Any]:
    return prepare_split_safe_feature_frames(
        split_frames=split_frames,
        raw_feature_columns=feature_columns,
        target_column=target_column,
        missing_data_strategy=missing_data_strategy,
        fill_constant_value=fill_constant_value,
        task_type=task_type,
    )


def _prepare_split_safe_frames_classification(
    *,
    split_frames: dict[str, pd.DataFrame],
    feature_columns: list[str],
    target_column: str,
    missing_data_strategy: str,
    fill_constant_value: float | None,
    task_type: str,
) -> dict[str, Any]:
    return prepare_split_safe_feature_frames(
        split_frames=split_frames,
        raw_feature_columns=feature_columns,
        target_column=target_column,
        missing_data_strategy=missing_data_strategy,
        fill_constant_value=fill_constant_value,
        task_type=task_type,
    )


def _prepare_xy(
    *,
    frame: pd.DataFrame,
    feature_columns: list[str],
    target_column: str,
) -> tuple[np.ndarray, np.ndarray]:
    _require_columns(frame, feature_columns + [target_column])
    subset = frame[feature_columns + [target_column]].copy().dropna()
    x = subset[feature_columns].to_numpy(dtype=float)
    y = subset[target_column].to_numpy(dtype=float)
    return x, y


def _lagged_feature_names(*, feature_columns: list[str], lag_horizon: int) -> list[str]:
    names: list[str] = []
    rolling_window = _temporal_rolling_window(lag_horizon=lag_horizon)
    for col in feature_columns:
        names.append(f"{col}__t")
        for lag in range(1, int(lag_horizon) + 1):
            names.append(f"{col}__lag{lag}")
        names.append(f"{col}__delta1")
        names.append(f"{col}__rolling_mean{rolling_window}")
        names.append(f"{col}__rolling_std{rolling_window}")
        names.append(f"{col}__rolling_min{rolling_window}")
        names.append(f"{col}__rolling_max{rolling_window}")
        if int(lag_horizon) > 1:
            names.append(f"{col}__seasonal_delta{int(lag_horizon)}")
    return names


def _build_lagged_design_frame(
    *,
    frame: pd.DataFrame,
    feature_columns: list[str],
    target_column: str,
    lag_horizon: int,
    context_frame: pd.DataFrame | None = None,
    expected_feature_columns: list[str] | None = None,
) -> pd.DataFrame:
    required = list(feature_columns) + [target_column]
    _require_columns(frame, required)
    if context_frame is not None:
        _require_columns(context_frame, required)
    context_len = int(len(context_frame)) if context_frame is not None else 0
    if context_frame is not None and context_len > 0:
        combined = pd.concat(
            [context_frame[required], frame[required]],
            ignore_index=True,
        )
    else:
        combined = frame[required].copy().reset_index(drop=True)

    out_columns: dict[str, pd.Series] = {}
    rolling_window = _temporal_rolling_window(lag_horizon=lag_horizon)
    for col in feature_columns:
        numeric = pd.to_numeric(combined[col], errors="coerce")
        out_columns[f"{col}__t"] = numeric
        for lag in range(1, int(lag_horizon) + 1):
            out_columns[f"{col}__lag{lag}"] = numeric.shift(lag)
        out_columns[f"{col}__delta1"] = numeric.diff(1)
        rolling = numeric.rolling(window=rolling_window, min_periods=rolling_window)
        out_columns[f"{col}__rolling_mean{rolling_window}"] = rolling.mean()
        out_columns[f"{col}__rolling_std{rolling_window}"] = rolling.std()
        out_columns[f"{col}__rolling_min{rolling_window}"] = rolling.min()
        out_columns[f"{col}__rolling_max{rolling_window}"] = rolling.max()
        if int(lag_horizon) > 1:
            out_columns[f"{col}__seasonal_delta{int(lag_horizon)}"] = numeric - numeric.shift(int(lag_horizon))
    out_columns[target_column] = pd.to_numeric(combined[target_column], errors="coerce")
    out_columns["_is_current"] = pd.Series(False, index=combined.index)
    out = pd.DataFrame(out_columns, index=combined.index)
    out.loc[context_len:, "_is_current"] = True
    out = out.dropna()
    out = out[out["_is_current"]].drop(columns=["_is_current"]).reset_index(drop=True)
    if expected_feature_columns:
        ordered = [column for column in expected_feature_columns if column in out.columns]
        out = out[ordered + [target_column]]
    return out


def _temporal_rolling_window(*, lag_horizon: int) -> int:
    return max(2, min(int(lag_horizon) + 1, 4))


def _materialize_temporal_metric_aliases(*, metrics: dict[str, float], data_mode: str) -> dict[str, float]:
    payload = {str(key): float(value) for key, value in dict(metrics).items()}
    if str(data_mode).strip().lower() == "time_series" and "mae" in payload:
        payload.setdefault("stability_adjusted_mae", float(payload["mae"]))
        payload.setdefault("mae_per_latency", float(payload["mae"]))
    return payload


def _prepare_feature_matrix(*, frame: pd.DataFrame, feature_columns: list[str]) -> np.ndarray:
    _require_columns(frame, feature_columns)
    subset = frame[feature_columns].copy()
    if subset.isna().any().any():
        raise ValueError("Feature frame contains missing values after preprocessing.")
    return subset.to_numpy(dtype=float)


def _prepare_target_vector(*, frame: pd.DataFrame, target_column: str) -> np.ndarray:
    _require_columns(frame, [target_column])
    target = frame[target_column].copy()
    if target.isna().any():
        raise ValueError("Target column contains missing values after preprocessing.")
    return target.to_numpy(dtype=float)


def _require_columns(frame: pd.DataFrame, columns: list[str]) -> None:
    missing = [column for column in columns if column not in frame.columns]
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(missing)}")


def _fit_regression_tree(
    *,
    x_train: np.ndarray,
    y_train: np.ndarray,
    depth: int,
    max_depth: int,
    min_leaf: int,
) -> dict[str, Any]:
    leaf_value = float(np.mean(y_train)) if y_train.size > 0 else 0.0
    if (
        depth >= max_depth
        or y_train.size < max(2 * int(min_leaf), 8)
        or float(np.var(y_train)) <= 1e-12
    ):
        return {"leaf": True, "value": leaf_value}

    best_feature = -1
    best_threshold = float("nan")
    best_score = float("inf")
    n_features = int(x_train.shape[1]) if x_train.ndim == 2 else 0
    for feature_idx in range(n_features):
        values = x_train[:, feature_idx]
        finite_values = values[np.isfinite(values)]
        if finite_values.size < max(2 * int(min_leaf), 8):
            continue
        thresholds = _candidate_thresholds(finite_values)
        for threshold in thresholds:
            left_mask = values <= threshold
            right_mask = ~left_mask
            left_count = int(np.sum(left_mask))
            right_count = int(np.sum(right_mask))
            if left_count < min_leaf or right_count < min_leaf:
                continue
            score = _sum_squared_error(y_train[left_mask]) + _sum_squared_error(y_train[right_mask])
            if score < best_score:
                best_score = score
                best_feature = feature_idx
                best_threshold = float(threshold)

    if best_feature < 0 or not math.isfinite(best_threshold):
        return {"leaf": True, "value": leaf_value}

    values = x_train[:, best_feature]
    left_mask = values <= best_threshold
    right_mask = ~left_mask
    return {
        "leaf": False,
        "value": leaf_value,
        "feature_index": int(best_feature),
        "threshold": float(best_threshold),
        "left": _fit_regression_tree(
            x_train=x_train[left_mask],
            y_train=y_train[left_mask],
            depth=depth + 1,
            max_depth=max_depth,
            min_leaf=min_leaf,
        ),
        "right": _fit_regression_tree(
            x_train=x_train[right_mask],
            y_train=y_train[right_mask],
            depth=depth + 1,
            max_depth=max_depth,
            min_leaf=min_leaf,
        ),
    }


def _predict_regression_tree_batch(*, tree: dict[str, Any], x: np.ndarray) -> np.ndarray:
    pred = np.empty(x.shape[0], dtype=float)
    for idx in range(x.shape[0]):
        pred[idx] = _predict_regression_tree_row(tree=tree, row=x[idx])
    return pred


def _predict_regression_tree_row(*, tree: dict[str, Any], row: np.ndarray) -> float:
    node = tree
    while not bool(node.get("leaf", False)):
        feature_index = int(node["feature_index"])
        threshold = float(node["threshold"])
        node = node["left"] if float(row[feature_index]) <= threshold else node["right"]
    return float(node.get("value", 0.0))


def _candidate_thresholds(values: np.ndarray) -> np.ndarray:
    unique = np.unique(values)
    if unique.size <= 1:
        return np.array([], dtype=float)
    if unique.size <= 12:
        return ((unique[:-1] + unique[1:]) / 2.0).astype(float)
    quantiles = np.linspace(0.1, 0.9, 9)
    candidates = np.unique(np.quantile(values, quantiles))
    lower = float(np.min(values))
    upper = float(np.max(values))
    candidates = candidates[(candidates > lower) & (candidates < upper)]
    return candidates.astype(float)


def _sum_squared_error(values: np.ndarray) -> float:
    if values.size == 0:
        return 0.0
    centered = values - float(np.mean(values))
    return float(np.sum(np.square(centered)))


def _is_number(value: Any) -> bool:
    try:
        float(value)
    except (TypeError, ValueError):
        return False
    return True

