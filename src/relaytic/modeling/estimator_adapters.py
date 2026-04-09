"""Sklearn-backed estimator adapters for widened architecture routing."""

from __future__ import annotations

import importlib
import importlib.util
import pickle
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.ensemble import (
    ExtraTreesClassifier,
    ExtraTreesRegressor,
    HistGradientBoostingClassifier,
    HistGradientBoostingRegressor,
)

from relaytic.core.json_utils import write_json

from .evaluation import classification_metrics, regression_metrics


class PickledRegressionEstimatorSurrogate:
    """Persist a fitted sklearn-style regressor beside a small JSON manifest."""

    def __init__(
        self,
        *,
        feature_columns: list[str],
        target_column: str,
        model_name: str,
        estimator: Any,
        hyperparameters: dict[str, Any] | None = None,
    ) -> None:
        if not feature_columns:
            raise ValueError("feature_columns cannot be empty.")
        self.feature_columns = list(feature_columns)
        self.target_column = str(target_column)
        self.model_name = str(model_name)
        self.hyperparameters = dict(hyperparameters or {})
        self._estimator = estimator

    def fit_dataframe(self, frame: pd.DataFrame) -> int:
        x, y = _prepare_xy(frame=frame, feature_columns=self.feature_columns, target_column=self.target_column)
        self._estimator.fit(x, y)
        return int(x.shape[0])

    def predict_dataframe(self, frame: pd.DataFrame, *, context_frame: pd.DataFrame | None = None) -> np.ndarray:
        del context_frame
        x = _prepare_feature_matrix(frame=frame, feature_columns=self.feature_columns)
        return np.asarray(self._estimator.predict(x), dtype=float)

    def evaluate_dataframe(self, frame: pd.DataFrame, *, context_frame: pd.DataFrame | None = None) -> dict[str, float]:
        del context_frame
        y_true = _prepare_target_vector(frame=frame, target_column=self.target_column)
        y_pred = self.predict_dataframe(frame)
        return regression_metrics(y_true=y_true, y_pred=y_pred).to_dict()

    def state_dict(self, *, pickle_filename: str | None = None) -> dict[str, Any]:
        return {
            "model_name": self.model_name,
            "feature_columns": list(self.feature_columns),
            "target_column": self.target_column,
            "hyperparameters": dict(self.hyperparameters),
            "pickle_filename": str(pickle_filename or ""),
            "estimator_backend": "pickle",
        }

    def save(self, path: str | Path) -> Path:
        output = Path(path)
        output.parent.mkdir(parents=True, exist_ok=True)
        pickle_path = output.with_suffix(".pkl")
        with pickle_path.open("wb") as handle:
            pickle.dump(self._estimator, handle, protocol=pickle.HIGHEST_PROTOCOL)
        return write_json(output, self.state_dict(pickle_filename=pickle_path.name), indent=2)

    @classmethod
    def from_state_dict(cls, payload: dict[str, Any], *, state_path: str | Path) -> "PickledRegressionEstimatorSurrogate":
        pickle_path = _resolve_pickle_path(payload=payload, state_path=state_path)
        with pickle_path.open("rb") as handle:
            estimator = pickle.load(handle)
        return cls(
            feature_columns=[str(item) for item in payload.get("feature_columns", []) if str(item).strip()],
            target_column=str(payload.get("target_column", "")),
            model_name=str(payload.get("model_name", "")),
            estimator=estimator,
            hyperparameters=dict(payload.get("hyperparameters") or {}),
        )


class PickledClassificationEstimatorSurrogate:
    """Persist a fitted sklearn-style probabilistic classifier beside JSON metadata."""

    def __init__(
        self,
        *,
        feature_columns: list[str],
        target_column: str,
        model_name: str,
        estimator: Any,
        hyperparameters: dict[str, Any] | None = None,
        class_labels: list[str] | None = None,
    ) -> None:
        if not feature_columns:
            raise ValueError("feature_columns cannot be empty.")
        self.feature_columns = list(feature_columns)
        self.target_column = str(target_column)
        self.model_name = str(model_name)
        self.hyperparameters = dict(hyperparameters or {})
        self.class_labels = [str(item) for item in class_labels or [] if str(item).strip()]
        self._estimator = estimator

    def fit_dataframe(self, frame: pd.DataFrame) -> int:
        x, y = _prepare_classification_xy(
            frame=frame,
            feature_columns=self.feature_columns,
            target_column=self.target_column,
        )
        self.class_labels = [str(item) for item in pd.Index(y).unique().tolist()]
        label_to_index = {label: index for index, label in enumerate(self.class_labels)}
        y_encoded = np.asarray([label_to_index[str(item)] for item in y], dtype=int)
        self._estimator.fit(x, y_encoded)
        return int(x.shape[0])

    def predict_proba_dataframe(self, frame: pd.DataFrame, *, context_frame: pd.DataFrame | None = None) -> np.ndarray:
        del context_frame
        x = _prepare_feature_matrix(frame=frame, feature_columns=self.feature_columns)
        probabilities = np.asarray(self._estimator.predict_proba(x), dtype=float)
        estimator_classes = [int(item) for item in np.asarray(getattr(self._estimator, "classes_", []), dtype=int).tolist()]
        if not self.class_labels:
            raise RuntimeError("Classification estimator is missing class labels.")
        aligned = np.zeros((probabilities.shape[0], len(self.class_labels)), dtype=float)
        for source_index, encoded_label in enumerate(estimator_classes):
            if 0 <= int(encoded_label) < len(self.class_labels):
                aligned[:, int(encoded_label)] = probabilities[:, source_index]
        if aligned.shape[1] == 0:
            raise RuntimeError("Classification estimator produced no aligned class probabilities.")
        return aligned

    def predict_dataframe(self, frame: pd.DataFrame, *, context_frame: pd.DataFrame | None = None) -> np.ndarray:
        probabilities = self.predict_proba_dataframe(frame, context_frame=context_frame)
        winner = np.argmax(probabilities, axis=1)
        return np.asarray([self.class_labels[int(index)] for index in winner], dtype=object)

    def evaluate_dataframe(self, frame: pd.DataFrame, *, context_frame: pd.DataFrame | None = None) -> dict[str, float]:
        del context_frame
        y_true = [str(item) for item in frame[self.target_column].tolist()]
        probabilities = self.predict_proba_dataframe(frame)
        positive_label = _minority_label(y_true)
        return classification_metrics(
            y_true=y_true,
            probabilities=probabilities,
            class_labels=list(self.class_labels),
            positive_label=positive_label,
            decision_threshold=0.5 if len(self.class_labels) == 2 else None,
        ).to_dict()

    def state_dict(self, *, pickle_filename: str | None = None) -> dict[str, Any]:
        return {
            "model_name": self.model_name,
            "feature_columns": list(self.feature_columns),
            "target_column": self.target_column,
            "class_labels": list(self.class_labels),
            "hyperparameters": dict(self.hyperparameters),
            "pickle_filename": str(pickle_filename or ""),
            "estimator_backend": "pickle",
        }

    def save(self, path: str | Path) -> Path:
        output = Path(path)
        output.parent.mkdir(parents=True, exist_ok=True)
        pickle_path = output.with_suffix(".pkl")
        with pickle_path.open("wb") as handle:
            pickle.dump(self._estimator, handle, protocol=pickle.HIGHEST_PROTOCOL)
        return write_json(output, self.state_dict(pickle_filename=pickle_path.name), indent=2)

    @classmethod
    def from_state_dict(cls, payload: dict[str, Any], *, state_path: str | Path) -> "PickledClassificationEstimatorSurrogate":
        pickle_path = _resolve_pickle_path(payload=payload, state_path=state_path)
        with pickle_path.open("rb") as handle:
            estimator = pickle.load(handle)
        return cls(
            feature_columns=[str(item) for item in payload.get("feature_columns", []) if str(item).strip()],
            target_column=str(payload.get("target_column", "")),
            model_name=str(payload.get("model_name", "")),
            estimator=estimator,
            hyperparameters=dict(payload.get("hyperparameters") or {}),
            class_labels=[str(item) for item in payload.get("class_labels", []) if str(item).strip()],
        )


def build_regression_estimator_variants(
    *,
    feature_columns: list[str],
    target_column: str,
) -> list[dict[str, Any]]:
    variants: list[dict[str, Any]] = []
    for variant_id, params in [
        (
            "hist_balanced",
            {
                "max_iter": 180,
                "learning_rate": 0.08,
                "max_depth": 6,
                "min_samples_leaf": 20,
                "random_state": 42,
            },
        ),
        (
            "hist_small_data",
            {
                "max_iter": 120,
                "learning_rate": 0.06,
                "max_depth": 5,
                "min_samples_leaf": 12,
                "random_state": 42,
            },
        ),
        (
            "hist_wide",
            {
                "max_iter": 260,
                "learning_rate": 0.05,
                "max_depth": 8,
                "min_samples_leaf": 10,
                "random_state": 42,
            },
        ),
    ]:
        variants.append(
            _regression_variant(
                family="hist_gradient_boosting_ensemble",
                variant_id=variant_id,
                feature_columns=feature_columns,
                target_column=target_column,
                estimator=HistGradientBoostingRegressor(**params),
                hyperparameters=params,
            )
        )
    for variant_id, params in [
        (
            "extra_balanced",
            {
                "n_estimators": 220,
                "max_depth": None,
                "min_samples_leaf": 2,
                "random_state": 42,
                "n_jobs": 1,
            },
        ),
        (
            "extra_regularized",
            {
                "n_estimators": 160,
                "max_depth": 18,
                "min_samples_leaf": 4,
                "random_state": 42,
                "n_jobs": 1,
            },
        ),
        (
            "extra_small_data",
            {
                "n_estimators": 120,
                "max_depth": 10,
                "min_samples_leaf": 6,
                "random_state": 42,
                "n_jobs": 1,
            },
        ),
    ]:
        variants.append(
            _regression_variant(
                family="extra_trees_ensemble",
                variant_id=variant_id,
                feature_columns=feature_columns,
                target_column=target_column,
                estimator=ExtraTreesRegressor(**params),
                hyperparameters=params,
            )
        )
    variants.extend(
        _optional_regression_variants(
            feature_columns=feature_columns,
            target_column=target_column,
        )
    )
    return variants


def build_classification_estimator_variants(
    *,
    feature_columns: list[str],
    target_column: str,
    class_count: int | None = None,
) -> list[dict[str, Any]]:
    variants: list[dict[str, Any]] = []
    for variant_id, params in [
        (
            "hist_classifier_balanced",
            {
                "max_iter": 220,
                "learning_rate": 0.08,
                "max_depth": 6,
                "min_samples_leaf": 18,
                "random_state": 42,
            },
        ),
        (
            "hist_classifier_small_data",
            {
                "max_iter": 140,
                "learning_rate": 0.06,
                "max_depth": 5,
                "min_samples_leaf": 10,
                "random_state": 42,
            },
        ),
        (
            "hist_classifier_wide",
            {
                "max_iter": 280,
                "learning_rate": 0.05,
                "max_depth": 8,
                "min_samples_leaf": 12,
                "random_state": 42,
            },
        ),
    ]:
        variants.append(
            _classification_variant(
                family="hist_gradient_boosting_classifier",
                variant_id=variant_id,
                feature_columns=feature_columns,
                target_column=target_column,
                estimator=HistGradientBoostingClassifier(**params),
                hyperparameters=params,
            )
        )
    for variant_id, params in [
        (
            "extra_classifier_balanced",
            {
                "n_estimators": 220,
                "max_depth": None,
                "min_samples_leaf": 2,
                "random_state": 42,
                "n_jobs": 1,
            },
        ),
        (
            "extra_classifier_regularized",
            {
                "n_estimators": 160,
                "max_depth": 18,
                "min_samples_leaf": 4,
                "random_state": 42,
                "n_jobs": 1,
            },
        ),
        (
            "extra_classifier_small_data",
            {
                "n_estimators": 120,
                "max_depth": 10,
                "min_samples_leaf": 6,
                "random_state": 42,
                "n_jobs": 1,
            },
        ),
    ]:
        variants.append(
            _classification_variant(
                family="extra_trees_classifier",
                variant_id=variant_id,
                feature_columns=feature_columns,
                target_column=target_column,
                estimator=ExtraTreesClassifier(**params),
                hyperparameters=params,
            )
        )
    variants.extend(
        _optional_classification_variants(
            feature_columns=feature_columns,
            target_column=target_column,
            class_count=class_count,
        )
    )
    return variants


def _regression_variant(
    *,
    family: str,
    variant_id: str,
    feature_columns: list[str],
    target_column: str,
    estimator: Any,
    hyperparameters: dict[str, Any],
) -> dict[str, Any]:
    return {
        "family": family,
        "variant_id": variant_id,
        "model": PickledRegressionEstimatorSurrogate(
            feature_columns=feature_columns,
            target_column=target_column,
            model_name=family,
            estimator=estimator,
            hyperparameters=hyperparameters,
        ),
        "hyperparameters": dict(hyperparameters),
    }


def _classification_variant(
    *,
    family: str,
    variant_id: str,
    feature_columns: list[str],
    target_column: str,
    estimator: Any,
    hyperparameters: dict[str, Any],
) -> dict[str, Any]:
    return {
        "family": family,
        "variant_id": variant_id,
        "model": PickledClassificationEstimatorSurrogate(
            feature_columns=feature_columns,
            target_column=target_column,
            model_name=family,
            estimator=estimator,
            hyperparameters=hyperparameters,
        ),
        "hyperparameters": dict(hyperparameters),
    }


def _optional_regression_variants(
    *,
    feature_columns: list[str],
    target_column: str,
) -> list[dict[str, Any]]:
    variants: list[dict[str, Any]] = []
    if importlib.util.find_spec("catboost") is not None:
        from catboost import CatBoostRegressor

        params = {"depth": 6, "iterations": 220, "learning_rate": 0.06, "loss_function": "RMSE", "verbose": False}
        variants.append(
            _regression_variant(
                family="catboost_ensemble",
                variant_id="catboost_default",
                feature_columns=feature_columns,
                target_column=target_column,
                estimator=CatBoostRegressor(**params),
                hyperparameters=params,
            )
        )
    if importlib.util.find_spec("xgboost") is not None:
        from xgboost import XGBRegressor

        params = {
            "n_estimators": 240,
            "max_depth": 6,
            "learning_rate": 0.06,
            "subsample": 0.9,
            "colsample_bytree": 0.9,
            "objective": "reg:squarederror",
            "random_state": 42,
            "n_jobs": 1,
        }
        variants.append(
            _regression_variant(
                family="xgboost_ensemble",
                variant_id="xgboost_default",
                feature_columns=feature_columns,
                target_column=target_column,
                estimator=XGBRegressor(**params),
                hyperparameters=params,
            )
        )
    if importlib.util.find_spec("lightgbm") is not None:
        from lightgbm import LGBMRegressor

        params = {"n_estimators": 240, "learning_rate": 0.06, "num_leaves": 31, "random_state": 42, "n_jobs": 1}
        variants.append(
            _regression_variant(
                family="lightgbm_ensemble",
                variant_id="lightgbm_default",
                feature_columns=feature_columns,
                target_column=target_column,
                estimator=LGBMRegressor(**params),
                hyperparameters=params,
            )
        )
    return variants


def _optional_classification_variants(
    *,
    feature_columns: list[str],
    target_column: str,
    class_count: int | None,
) -> list[dict[str, Any]]:
    variants: list[dict[str, Any]] = []
    if importlib.util.find_spec("catboost") is not None:
        from catboost import CatBoostClassifier

        params = {"depth": 6, "iterations": 220, "learning_rate": 0.06, "loss_function": "MultiClass" if (class_count or 2) > 2 else "Logloss", "verbose": False}
        variants.append(
            _classification_variant(
                family="catboost_classifier",
                variant_id="catboost_default",
                feature_columns=feature_columns,
                target_column=target_column,
                estimator=CatBoostClassifier(**params),
                hyperparameters=params,
            )
        )
    if importlib.util.find_spec("xgboost") is not None:
        from xgboost import XGBClassifier

        params = {
            "n_estimators": 240,
            "max_depth": 6,
            "learning_rate": 0.06,
            "subsample": 0.9,
            "colsample_bytree": 0.9,
            "random_state": 42,
            "n_jobs": 1,
            "eval_metric": "mlogloss" if (class_count or 2) > 2 else "logloss",
        }
        variants.append(
            _classification_variant(
                family="xgboost_classifier",
                variant_id="xgboost_default",
                feature_columns=feature_columns,
                target_column=target_column,
                estimator=XGBClassifier(**params),
                hyperparameters=params,
            )
        )
    if importlib.util.find_spec("lightgbm") is not None:
        from lightgbm import LGBMClassifier

        params = {"n_estimators": 240, "learning_rate": 0.06, "num_leaves": 31, "random_state": 42, "n_jobs": 1}
        variants.append(
            _classification_variant(
                family="lightgbm_classifier",
                variant_id="lightgbm_default",
                feature_columns=feature_columns,
                target_column=target_column,
                estimator=LGBMClassifier(**params),
                hyperparameters=params,
            )
        )
    tabpfn = _optional_tabpfn_classifier(
        feature_columns=feature_columns,
        target_column=target_column,
    )
    if tabpfn is not None:
        variants.append(tabpfn)
    return variants


def _optional_tabpfn_classifier(
    *,
    feature_columns: list[str],
    target_column: str,
) -> dict[str, Any] | None:
    if importlib.util.find_spec("tabpfn") is None:
        return None
    try:
        module = importlib.import_module("tabpfn")
        classifier_cls = getattr(module, "TabPFNClassifier", None)
        if classifier_cls is None:
            return None
        params = {"device": "cpu"}
        estimator = classifier_cls(**params)
        return _classification_variant(
            family="tabpfn_classifier",
            variant_id="tabpfn_cpu_default",
            feature_columns=feature_columns,
            target_column=target_column,
            estimator=estimator,
            hyperparameters=params,
        )
    except Exception:
        return None


def _resolve_pickle_path(*, payload: dict[str, Any], state_path: str | Path) -> Path:
    state_file = Path(state_path)
    pickle_name = str(payload.get("pickle_filename", "")).strip()
    if pickle_name:
        return state_file.parent / pickle_name
    return state_file.with_suffix(".pkl")


def _prepare_feature_matrix(*, frame: pd.DataFrame, feature_columns: list[str]) -> np.ndarray:
    data = frame.loc[:, list(feature_columns)].apply(pd.to_numeric, errors="coerce")
    if data.empty:
        raise ValueError("No feature columns available for estimator training.")
    if data.isna().any().any():
        raise ValueError("Prepared feature matrix still contains missing values.")
    return np.asarray(data.to_numpy(dtype=float), dtype=float)


def _prepare_target_vector(*, frame: pd.DataFrame, target_column: str) -> np.ndarray:
    target = pd.to_numeric(frame[target_column], errors="coerce")
    if target.isna().any():
        raise ValueError("Prepared regression target contains non-numeric values.")
    return np.asarray(target.to_numpy(dtype=float), dtype=float)


def _prepare_xy(*, frame: pd.DataFrame, feature_columns: list[str], target_column: str) -> tuple[np.ndarray, np.ndarray]:
    x = _prepare_feature_matrix(frame=frame, feature_columns=feature_columns)
    y = _prepare_target_vector(frame=frame, target_column=target_column)
    return x, y


def _prepare_classification_xy(
    *,
    frame: pd.DataFrame,
    feature_columns: list[str],
    target_column: str,
) -> tuple[np.ndarray, np.ndarray]:
    x = _prepare_feature_matrix(frame=frame, feature_columns=feature_columns)
    y = np.asarray([str(item) for item in frame[target_column].tolist()], dtype=object)
    if y.size == 0:
        raise ValueError("Prepared classification target is empty.")
    return x, y


def _minority_label(values: list[str]) -> str | None:
    series = pd.Series(values, dtype=object)
    counts = series.value_counts()
    if counts.empty:
        return None
    return str(counts.sort_values(kind="stable").index[0])

