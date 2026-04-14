"""Helpers for Slice 11A imported incumbent evaluation."""

from __future__ import annotations

import json
import os
import pickle
from pathlib import Path
from typing import Any

import numpy as np

from relaytic.analytics.task_detection import is_classification_task
from relaytic.ingestion import load_tabular_data
from relaytic.modeling.evaluation import classification_metrics, regression_metrics

from .models import (
    BEAT_TARGET_CONTRACT_SCHEMA_VERSION,
    EXTERNAL_CHALLENGER_EVALUATION_SCHEMA_VERSION,
    EXTERNAL_CHALLENGER_MANIFEST_SCHEMA_VERSION,
    INCUMBENT_PARITY_REPORT_SCHEMA_VERSION,
    BeatTargetContract,
    BenchmarkControls,
    BenchmarkTrace,
    ExternalChallengerEvaluation,
    ExternalChallengerManifest,
    IncumbentParityReport,
)

TRUST_LOCAL_MODELS_ENV = "RELAYTIC_TRUST_LOCAL_MODELS"


class UnsafeIncumbentModelError(ValueError):
    """Raised when executable incumbent model deserialization is blocked."""


def evaluate_incumbent(
    *,
    incumbent_path: str | None,
    incumbent_kind: str | None,
    incumbent_name: str | None,
    trust_model_deserialization: bool = False,
    controls: BenchmarkControls,
    generated_at: str,
    trace: BenchmarkTrace,
    task_type: str,
    comparison_metric: str,
    metric_direction: str,
    threshold_policy: str,
    split_frames: dict[str, Any],
    prepared_frames: dict[str, Any],
    feature_columns: list[str],
    target_column: str,
    relaytic_reference: dict[str, Any],
) -> dict[str, Any]:
    empty = _empty_incumbent_outputs(
        controls=controls,
        generated_at=generated_at,
        trace=trace,
        comparison_metric=comparison_metric,
        metric_direction=metric_direction,
        relaytic_reference=relaytic_reference,
    )
    if not _clean_text(incumbent_path):
        return empty

    path = Path(str(incumbent_path))
    kind = _normalize_incumbent_kind(path=path, requested_kind=incumbent_kind)
    label = _clean_text(incumbent_name) or path.stem
    manifest = ExternalChallengerManifest(
        schema_version=EXTERNAL_CHALLENGER_MANIFEST_SCHEMA_VERSION,
        generated_at=generated_at,
        controls=controls,
        status="configured",
        incumbent_name=label,
        incumbent_kind=kind,
        adapter_family=_adapter_family(kind),
        source_path=str(path),
        executable_locally=kind in {"model", "ruleset"},
        reduced_claim=(kind == "predictions"),
        same_contract_possible=True,
        evaluation_scope="pending",
        summary=f"Relaytic prepared incumbent `{label}` as `{kind}`.",
        trace=trace,
    )
    if not path.exists():
        return _incumbent_error_outputs(
            controls=controls,
            generated_at=generated_at,
            trace=trace,
            manifest=manifest,
            comparison_metric=comparison_metric,
            metric_direction=metric_direction,
            relaytic_reference=relaytic_reference,
            status="unavailable",
            reason_codes=["incumbent_path_missing"],
            summary="Relaytic could not evaluate the incumbent because the configured path does not exist.",
        )

    try:
        if kind == "model":
            evaluation = _evaluate_model_incumbent(
                path=path,
                label=label,
                trust_model_deserialization=trust_model_deserialization,
                controls=controls,
                generated_at=generated_at,
                trace=trace,
                task_type=task_type,
                comparison_metric=comparison_metric,
                metric_direction=metric_direction,
                threshold_policy=threshold_policy,
                prepared_frames=prepared_frames,
                feature_columns=feature_columns,
                target_column=target_column,
            )
        elif kind == "predictions":
            evaluation = _evaluate_predictions_incumbent(
                path=path,
                label=label,
                controls=controls,
                generated_at=generated_at,
                trace=trace,
                task_type=task_type,
                comparison_metric=comparison_metric,
                metric_direction=metric_direction,
                threshold_policy=threshold_policy,
                split_frames=split_frames,
                target_column=target_column,
            )
        else:
            evaluation = _evaluate_ruleset_incumbent(
                path=path,
                label=label,
                controls=controls,
                generated_at=generated_at,
                trace=trace,
                task_type=task_type,
                comparison_metric=comparison_metric,
                metric_direction=metric_direction,
                threshold_policy=threshold_policy,
                prepared_frames=prepared_frames,
                feature_columns=feature_columns,
                target_column=target_column,
            )
    except UnsafeIncumbentModelError:
        return _incumbent_error_outputs(
            controls=controls,
            generated_at=generated_at,
            trace=trace,
            manifest=manifest,
            comparison_metric=comparison_metric,
            metric_direction=metric_direction,
            relaytic_reference=relaytic_reference,
            status="blocked",
            reason_codes=["unsafe_model_deserialization_blocked"],
            summary=(
                "Relaytic refused to deserialize the imported incumbent model because executable pickle and "
                "joblib payloads are blocked by default. Use prediction files or rulesets, or rerun with "
                "`--trust-incumbent-model` only when you trust the file."
            ),
        )
    except Exception as exc:
        return _incumbent_error_outputs(
            controls=controls,
            generated_at=generated_at,
            trace=trace,
            manifest=manifest,
            comparison_metric=comparison_metric,
            metric_direction=metric_direction,
            relaytic_reference=relaytic_reference,
            status="unavailable",
            reason_codes=["incumbent_evaluation_failed", exc.__class__.__name__],
            summary=f"Relaytic could not evaluate incumbent `{label}` because local execution failed.",
        )

    manifest = ExternalChallengerManifest(
        schema_version=manifest.schema_version,
        generated_at=generated_at,
        controls=controls,
        status="ok" if evaluation.status == "ok" else evaluation.status,
        incumbent_name=label,
        incumbent_kind=kind,
        adapter_family=manifest.adapter_family,
        source_path=str(path),
        executable_locally=evaluation.reevaluated_locally,
        reduced_claim=evaluation.reduced_claim,
        same_contract_possible=True,
        evaluation_scope=evaluation.evaluation_scope,
        summary=f"Relaytic prepared incumbent `{label}` as `{kind}` with scope `{evaluation.evaluation_scope}`.",
        trace=trace,
    )
    parity, beat_target = _incumbent_parity_and_contract(
        controls=controls,
        generated_at=generated_at,
        trace=trace,
        evaluation=evaluation,
        comparison_metric=comparison_metric,
        metric_direction=metric_direction,
        relaytic_reference=relaytic_reference,
    )
    benchmark_recommended_action_override = beat_target.recommended_action if beat_target.contract_state == "unmet" else None
    benchmark_summary_override = None
    if beat_target.contract_state == "unmet" and label:
        benchmark_summary_override = (
            f"Relaytic still trails incumbent `{label}` under the current comparison contract and should keep widening challenger pressure."
        )
    return {
        "manifest": manifest,
        "evaluation": evaluation,
        "parity": parity,
        "beat_target": beat_target,
        "incumbent_present": True,
        "incumbent_name": label,
        "beat_target_state": beat_target.contract_state,
        "benchmark_parity_status_override": None,
        "benchmark_recommended_action_override": benchmark_recommended_action_override,
        "benchmark_summary_override": benchmark_summary_override,
    }


def _empty_incumbent_outputs(
    *,
    controls: BenchmarkControls,
    generated_at: str,
    trace: BenchmarkTrace,
    comparison_metric: str,
    metric_direction: str,
    relaytic_reference: dict[str, Any],
) -> dict[str, Any]:
    manifest = ExternalChallengerManifest(
        schema_version=EXTERNAL_CHALLENGER_MANIFEST_SCHEMA_VERSION,
        generated_at=generated_at,
        controls=controls,
        status="not_configured",
        incumbent_name=None,
        incumbent_kind=None,
        adapter_family=None,
        source_path=None,
        executable_locally=False,
        reduced_claim=False,
        same_contract_possible=False,
        evaluation_scope="none",
        summary="Relaytic did not receive an imported incumbent for this benchmark run.",
        trace=trace,
    )
    evaluation = ExternalChallengerEvaluation(
        schema_version=EXTERNAL_CHALLENGER_EVALUATION_SCHEMA_VERSION,
        generated_at=generated_at,
        controls=controls,
        status="not_configured",
        incumbent_name=None,
        incumbent_kind=None,
        evaluation_mode="none",
        comparison_metric=comparison_metric,
        metric_direction=metric_direction,
        reevaluated_locally=False,
        reduced_claim=False,
        evaluation_scope="none",
        train_metric={},
        validation_metric={},
        test_metric={},
        decision_threshold=None,
        reason_codes=["no_incumbent_configured"],
        summary="Relaytic did not evaluate an imported incumbent in this benchmark run.",
        trace=trace,
    )
    parity = IncumbentParityReport(
        schema_version=INCUMBENT_PARITY_REPORT_SCHEMA_VERSION,
        generated_at=generated_at,
        controls=controls,
        status="not_configured",
        incumbent_present=False,
        incumbent_name=None,
        incumbent_kind=None,
        parity_status="no_incumbent",
        comparison_metric=comparison_metric,
        recommended_action="continue_experimentation",
        relaytic_beats_incumbent=False,
        incumbent_stronger=False,
        reduced_claim=False,
        test_gap=None,
        summary="Relaytic has no imported incumbent to compare against in this run.",
        trace=trace,
    )
    beat_target = BeatTargetContract(
        schema_version=BEAT_TARGET_CONTRACT_SCHEMA_VERSION,
        generated_at=generated_at,
        controls=controls,
        status="not_configured",
        target_name=None,
        target_kind="none",
        comparison_metric=comparison_metric,
        metric_direction=metric_direction,
        target_metric_value=None,
        relaytic_metric_value=_metric_value(dict(relaytic_reference.get("test_metric", {})), comparison_metric),
        contract_state="not_configured",
        recommended_action="continue_experimentation",
        reduced_claim=False,
        summary="Relaytic did not receive an explicit incumbent beat-target for this run.",
        trace=trace,
    )
    return {
        "manifest": manifest,
        "evaluation": evaluation,
        "parity": parity,
        "beat_target": beat_target,
        "incumbent_present": False,
        "incumbent_name": None,
        "beat_target_state": "not_configured",
        "benchmark_parity_status_override": None,
        "benchmark_recommended_action_override": None,
        "benchmark_summary_override": None,
    }


def _incumbent_error_outputs(
    *,
    controls: BenchmarkControls,
    generated_at: str,
    trace: BenchmarkTrace,
    manifest: ExternalChallengerManifest,
    comparison_metric: str,
    metric_direction: str,
    relaytic_reference: dict[str, Any],
    status: str,
    reason_codes: list[str],
    summary: str,
) -> dict[str, Any]:
    evaluation = ExternalChallengerEvaluation(
        schema_version=EXTERNAL_CHALLENGER_EVALUATION_SCHEMA_VERSION,
        generated_at=generated_at,
        controls=controls,
        status=status,
        incumbent_name=manifest.incumbent_name,
        incumbent_kind=manifest.incumbent_kind,
        evaluation_mode="failed",
        comparison_metric=comparison_metric,
        metric_direction=metric_direction,
        reevaluated_locally=False,
        reduced_claim=True,
        evaluation_scope="none",
        train_metric={},
        validation_metric={},
        test_metric={},
        decision_threshold=None,
        reason_codes=reason_codes,
        summary=summary,
        trace=trace,
    )
    parity = IncumbentParityReport(
        schema_version=INCUMBENT_PARITY_REPORT_SCHEMA_VERSION,
        generated_at=generated_at,
        controls=controls,
        status=status,
        incumbent_present=True,
        incumbent_name=manifest.incumbent_name,
        incumbent_kind=manifest.incumbent_kind,
        parity_status="incumbent_unavailable",
        comparison_metric=comparison_metric,
        recommended_action="continue_experimentation",
        relaytic_beats_incumbent=False,
        incumbent_stronger=False,
        reduced_claim=True,
        test_gap=None,
        summary=summary,
        trace=trace,
    )
    beat_target = BeatTargetContract(
        schema_version=BEAT_TARGET_CONTRACT_SCHEMA_VERSION,
        generated_at=generated_at,
        controls=controls,
        status=status,
        target_name=manifest.incumbent_name,
        target_kind="incumbent",
        comparison_metric=comparison_metric,
        metric_direction=metric_direction,
        target_metric_value=None,
        relaytic_metric_value=_metric_value(dict(relaytic_reference.get("test_metric", {})), comparison_metric),
        contract_state="unavailable",
        recommended_action="continue_experimentation",
        reduced_claim=True,
        summary=summary,
        trace=trace,
    )
    return {
        "manifest": manifest,
        "evaluation": evaluation,
        "parity": parity,
        "beat_target": beat_target,
        "incumbent_present": True,
        "incumbent_name": manifest.incumbent_name,
        "beat_target_state": "unavailable",
        "benchmark_parity_status_override": None,
        "benchmark_recommended_action_override": None,
        "benchmark_summary_override": None,
    }


def _evaluate_model_incumbent(
    *,
    path: Path,
    label: str,
    trust_model_deserialization: bool,
    controls: BenchmarkControls,
    generated_at: str,
    trace: BenchmarkTrace,
    task_type: str,
    comparison_metric: str,
    metric_direction: str,
    threshold_policy: str,
    prepared_frames: dict[str, Any],
    feature_columns: list[str],
    target_column: str,
) -> ExternalChallengerEvaluation:
    loaded = _load_incumbent_object(path, trust_model_deserialization=trust_model_deserialization)
    estimator = loaded["estimator"]
    incumbent_features = [item for item in loaded.get("feature_columns", feature_columns) if item in feature_columns]
    if not incumbent_features:
        raise ValueError("Incumbent model does not expose any compatible feature columns.")
    train_x = prepared_frames["train"][incumbent_features].to_numpy(dtype=float)
    validation_x = prepared_frames["validation"][incumbent_features].to_numpy(dtype=float)
    test_x = prepared_frames["test"][incumbent_features].to_numpy(dtype=float)
    if is_classification_task(task_type):
        train_y = prepared_frames["train"][target_column].astype(str).to_numpy(dtype=object)
        validation_y = prepared_frames["validation"][target_column].astype(str).to_numpy(dtype=object)
        test_y = prepared_frames["test"][target_column].astype(str).to_numpy(dtype=object)
        class_labels = [str(item) for item in getattr(estimator, "classes_", [])]
        if not class_labels:
            class_labels = sorted({str(item) for item in np.concatenate([train_y, validation_y, test_y])})
        train_proba = _predict_classification_probabilities(estimator, train_x, class_labels)
        validation_proba = _predict_classification_probabilities(estimator, validation_x, class_labels)
        test_proba = _predict_classification_probabilities(estimator, test_x, class_labels)
        positive_label = _minority_label(train_y)
        decision_threshold = _select_binary_threshold(
            y_true=validation_y.tolist(),
            probabilities=validation_proba,
            class_labels=class_labels,
            positive_label=positive_label,
            threshold_policy=threshold_policy,
            task_type=task_type,
        )
        train_metric = classification_metrics(
            y_true=train_y.tolist(),
            probabilities=train_proba,
            class_labels=class_labels,
            positive_label=positive_label,
            decision_threshold=decision_threshold,
        ).to_dict()
        validation_metric = classification_metrics(
            y_true=validation_y.tolist(),
            probabilities=validation_proba,
            class_labels=class_labels,
            positive_label=positive_label,
            decision_threshold=decision_threshold,
        ).to_dict()
        test_metric = classification_metrics(
            y_true=test_y.tolist(),
            probabilities=test_proba,
            class_labels=class_labels,
            positive_label=positive_label,
            decision_threshold=decision_threshold,
        ).to_dict()
        return ExternalChallengerEvaluation(
            schema_version=EXTERNAL_CHALLENGER_EVALUATION_SCHEMA_VERSION,
            generated_at=generated_at,
            controls=controls,
            status="ok",
            incumbent_name=label,
            incumbent_kind="model",
            evaluation_mode="local_model_execution",
            comparison_metric=comparison_metric,
            metric_direction=metric_direction,
            reevaluated_locally=True,
            reduced_claim=False,
            evaluation_scope="same_contract_full",
            train_metric=train_metric,
            validation_metric=validation_metric,
            test_metric=test_metric,
            decision_threshold=decision_threshold,
            reason_codes=["local_model_replayed"],
            summary=f"Relaytic reevaluated incumbent model `{label}` locally under the same split and metric contract.",
            trace=trace,
        )

    train_y = prepared_frames["train"][target_column].to_numpy(dtype=float)
    validation_y = prepared_frames["validation"][target_column].to_numpy(dtype=float)
    test_y = prepared_frames["test"][target_column].to_numpy(dtype=float)
    train_pred = np.asarray(estimator.predict(train_x), dtype=float)
    validation_pred = np.asarray(estimator.predict(validation_x), dtype=float)
    test_pred = np.asarray(estimator.predict(test_x), dtype=float)
    return ExternalChallengerEvaluation(
        schema_version=EXTERNAL_CHALLENGER_EVALUATION_SCHEMA_VERSION,
        generated_at=generated_at,
        controls=controls,
        status="ok",
        incumbent_name=label,
        incumbent_kind="model",
        evaluation_mode="local_model_execution",
        comparison_metric=comparison_metric,
        metric_direction=metric_direction,
        reevaluated_locally=True,
        reduced_claim=False,
        evaluation_scope="same_contract_full",
        train_metric=regression_metrics(y_true=train_y, y_pred=train_pred).to_dict(),
        validation_metric=regression_metrics(y_true=validation_y, y_pred=validation_pred).to_dict(),
        test_metric=regression_metrics(y_true=test_y, y_pred=test_pred).to_dict(),
        decision_threshold=None,
        reason_codes=["local_model_replayed"],
        summary=f"Relaytic reevaluated incumbent model `{label}` locally under the same split and metric contract.",
        trace=trace,
    )


def _evaluate_predictions_incumbent(
    *,
    path: Path,
    label: str,
    controls: BenchmarkControls,
    generated_at: str,
    trace: BenchmarkTrace,
    task_type: str,
    comparison_metric: str,
    metric_direction: str,
    threshold_policy: str,
    split_frames: dict[str, Any],
    target_column: str,
) -> ExternalChallengerEvaluation:
    prediction_frame = load_tabular_data(str(path)).frame.copy()
    split_payload = _split_prediction_frame(prediction_frame=prediction_frame, split_frames=split_frames)
    prediction_column, score_column = _detect_prediction_columns(prediction_frame)
    reduced_claim = split_payload["reduced_claim"] or score_column is None
    if not prediction_column and score_column is None:
        raise ValueError("Prediction incumbent must provide a prediction or score column.")
    if is_classification_task(task_type):
        train_y = split_frames["train"][target_column].astype(str).tolist()
        validation_y = split_frames["validation"][target_column].astype(str).tolist()
        test_y = split_frames["test"][target_column].astype(str).tolist()
        class_labels = sorted({*train_y, *validation_y, *test_y})
        positive_label = _minority_label(np.asarray(train_y, dtype=object))
        parts: dict[str, dict[str, Any]] = {}
        for name, y_true in (("train", train_y), ("validation", validation_y), ("test", test_y)):
            frame = split_payload["frames"].get(name)
            if frame is None:
                parts[name] = {}
                continue
            probabilities = _prediction_frame_to_probabilities(
                frame=frame,
                class_labels=class_labels,
                prediction_column=prediction_column,
                score_column=score_column,
                positive_label=positive_label,
            )
            parts[name] = {"y_true": y_true, "probabilities": probabilities}
        decision_threshold = None
        if parts.get("validation"):
            decision_threshold = _select_binary_threshold(
                y_true=validation_y,
                probabilities=np.asarray(parts["validation"]["probabilities"], dtype=float),
                class_labels=class_labels,
                positive_label=positive_label,
                threshold_policy=threshold_policy,
                task_type=task_type,
            )
        return ExternalChallengerEvaluation(
            schema_version=EXTERNAL_CHALLENGER_EVALUATION_SCHEMA_VERSION,
            generated_at=generated_at,
            controls=controls,
            status="ok",
            incumbent_name=label,
            incumbent_kind="predictions",
            evaluation_mode="prediction_replay",
            comparison_metric=comparison_metric,
            metric_direction=metric_direction,
            reevaluated_locally=False,
            reduced_claim=reduced_claim,
            evaluation_scope=split_payload["scope"],
            train_metric=_classification_metric_or_empty(parts.get("train"), class_labels, positive_label, decision_threshold),
            validation_metric=_classification_metric_or_empty(parts.get("validation"), class_labels, positive_label, decision_threshold),
            test_metric=_classification_metric_or_empty(parts.get("test"), class_labels, positive_label, decision_threshold),
            decision_threshold=decision_threshold,
            reason_codes=split_payload["reason_codes"] + (["score_column_missing"] if score_column is None else []),
            summary=f"Relaytic replayed incumbent predictions `{label}` under `{split_payload['scope']}` scope.",
            trace=trace,
        )

    column = prediction_column or "prediction"
    if column not in prediction_frame.columns:
        raise ValueError("Regression prediction incumbent must expose a prediction column.")
    metrics_by_split: dict[str, dict[str, Any]] = {"train": {}, "validation": {}, "test": {}}
    for name, frame in split_payload["frames"].items():
        if frame is None:
            continue
        y_true = split_frames[name][target_column].to_numpy(dtype=float)
        y_pred = frame[column].to_numpy(dtype=float)
        metrics_by_split[name] = regression_metrics(y_true=y_true, y_pred=y_pred).to_dict()
    return ExternalChallengerEvaluation(
        schema_version=EXTERNAL_CHALLENGER_EVALUATION_SCHEMA_VERSION,
        generated_at=generated_at,
        controls=controls,
        status="ok",
        incumbent_name=label,
        incumbent_kind="predictions",
        evaluation_mode="prediction_replay",
        comparison_metric=comparison_metric,
        metric_direction=metric_direction,
        reevaluated_locally=False,
        reduced_claim=split_payload["reduced_claim"],
        evaluation_scope=split_payload["scope"],
        train_metric=metrics_by_split["train"],
        validation_metric=metrics_by_split["validation"],
        test_metric=metrics_by_split["test"],
        decision_threshold=None,
        reason_codes=split_payload["reason_codes"],
        summary=f"Relaytic replayed incumbent predictions `{label}` under `{split_payload['scope']}` scope.",
        trace=trace,
    )


def _evaluate_ruleset_incumbent(
    *,
    path: Path,
    label: str,
    controls: BenchmarkControls,
    generated_at: str,
    trace: BenchmarkTrace,
    task_type: str,
    comparison_metric: str,
    metric_direction: str,
    threshold_policy: str,
    prepared_frames: dict[str, Any],
    feature_columns: list[str],
    target_column: str,
) -> ExternalChallengerEvaluation:
    spec = json.loads(path.read_text(encoding="utf-8"))
    kind = _clean_text(spec.get("kind")) or "linear_scorecard"
    if kind != "linear_scorecard":
        raise ValueError("Only `linear_scorecard` rulesets are currently supported.")
    weights = {
        str(key): float(value)
        for key, value in dict(spec.get("weights") or {}).items()
        if str(key).strip() in feature_columns
    }
    if not weights:
        raise ValueError("Ruleset does not expose any compatible feature weights.")
    intercept = float(spec.get("intercept", 0.0) or 0.0)
    if is_classification_task(task_type):
        train_y = prepared_frames["train"][target_column].astype(str).to_numpy(dtype=object)
        validation_y = prepared_frames["validation"][target_column].astype(str).to_numpy(dtype=object)
        test_y = prepared_frames["test"][target_column].astype(str).to_numpy(dtype=object)
        class_labels = sorted({*map(str, train_y), *map(str, validation_y), *map(str, test_y)})
        if len(class_labels) != 2:
            raise ValueError("Linear scorecard incumbent currently supports binary classification only.")
        positive_label = _clean_text(spec.get("positive_label")) or _minority_label(train_y)
        train_proba = _apply_linear_scorecard(prepared_frames["train"], weights, intercept, class_labels, positive_label)
        validation_proba = _apply_linear_scorecard(prepared_frames["validation"], weights, intercept, class_labels, positive_label)
        test_proba = _apply_linear_scorecard(prepared_frames["test"], weights, intercept, class_labels, positive_label)
        threshold = float(spec.get("threshold", 0.0) or 0.0)
        if threshold <= 0.0 or threshold >= 1.0:
            threshold = _select_binary_threshold(
                y_true=validation_y.tolist(),
                probabilities=validation_proba,
                class_labels=class_labels,
                positive_label=positive_label,
                threshold_policy=threshold_policy,
                task_type=task_type,
            )
        return ExternalChallengerEvaluation(
            schema_version=EXTERNAL_CHALLENGER_EVALUATION_SCHEMA_VERSION,
            generated_at=generated_at,
            controls=controls,
            status="ok",
            incumbent_name=label,
            incumbent_kind="ruleset",
            evaluation_mode="ruleset_execution",
            comparison_metric=comparison_metric,
            metric_direction=metric_direction,
            reevaluated_locally=True,
            reduced_claim=False,
            evaluation_scope="same_contract_full",
            train_metric=classification_metrics(y_true=train_y.tolist(), probabilities=train_proba, class_labels=class_labels, positive_label=positive_label, decision_threshold=threshold).to_dict(),
            validation_metric=classification_metrics(y_true=validation_y.tolist(), probabilities=validation_proba, class_labels=class_labels, positive_label=positive_label, decision_threshold=threshold).to_dict(),
            test_metric=classification_metrics(y_true=test_y.tolist(), probabilities=test_proba, class_labels=class_labels, positive_label=positive_label, decision_threshold=threshold).to_dict(),
            decision_threshold=threshold,
            reason_codes=["ruleset_replayed_locally"],
            summary=f"Relaytic reevaluated ruleset incumbent `{label}` locally under the same split and metric contract.",
            trace=trace,
        )

    train_y = prepared_frames["train"][target_column].to_numpy(dtype=float)
    validation_y = prepared_frames["validation"][target_column].to_numpy(dtype=float)
    test_y = prepared_frames["test"][target_column].to_numpy(dtype=float)
    train_pred = _apply_linear_regression_scorecard(prepared_frames["train"], weights, intercept)
    validation_pred = _apply_linear_regression_scorecard(prepared_frames["validation"], weights, intercept)
    test_pred = _apply_linear_regression_scorecard(prepared_frames["test"], weights, intercept)
    return ExternalChallengerEvaluation(
        schema_version=EXTERNAL_CHALLENGER_EVALUATION_SCHEMA_VERSION,
        generated_at=generated_at,
        controls=controls,
        status="ok",
        incumbent_name=label,
        incumbent_kind="ruleset",
        evaluation_mode="ruleset_execution",
        comparison_metric=comparison_metric,
        metric_direction=metric_direction,
        reevaluated_locally=True,
        reduced_claim=False,
        evaluation_scope="same_contract_full",
        train_metric=regression_metrics(y_true=train_y, y_pred=train_pred).to_dict(),
        validation_metric=regression_metrics(y_true=validation_y, y_pred=validation_pred).to_dict(),
        test_metric=regression_metrics(y_true=test_y, y_pred=test_pred).to_dict(),
        decision_threshold=None,
        reason_codes=["ruleset_replayed_locally"],
        summary=f"Relaytic reevaluated ruleset incumbent `{label}` locally under the same split and metric contract.",
        trace=trace,
    )


def _incumbent_parity_and_contract(
    *,
    controls: BenchmarkControls,
    generated_at: str,
    trace: BenchmarkTrace,
    evaluation: ExternalChallengerEvaluation,
    comparison_metric: str,
    metric_direction: str,
    relaytic_reference: dict[str, Any],
) -> tuple[IncumbentParityReport, BeatTargetContract]:
    relaytic_test = _metric_value(dict(relaytic_reference.get("test_metric", {})), comparison_metric)
    incumbent_test = _metric_value(dict(evaluation.test_metric or {}), comparison_metric)
    if evaluation.status != "ok":
        parity_status = "incumbent_unavailable"
        recommended_action = "continue_experimentation"
        contract_state = "unavailable"
        test_gap = None
    elif evaluation.reduced_claim:
        parity_status = "reduced_claim"
        recommended_action = "continue_experimentation"
        contract_state = "reduced_claim"
        test_gap = _signed_gap(reference_value=incumbent_test, relaytic_value=relaytic_test, direction=metric_direction)
    else:
        test_gap = _signed_gap(reference_value=incumbent_test, relaytic_value=relaytic_test, direction=metric_direction)
        relative_gap = _relative_gap(test_gap, incumbent_test)
        near = _near_parity(controls=controls, absolute_gap=test_gap, relative_gap=relative_gap)
        if test_gap is not None and test_gap <= 0.0:
            parity_status = "beats_incumbent"
            recommended_action = "hold_current_route"
            contract_state = "met"
        elif near:
            parity_status = "near_incumbent"
            recommended_action = "continue_experimentation"
            contract_state = "near"
        else:
            parity_status = "below_incumbent"
            recommended_action = "expand_challenger_portfolio"
            contract_state = "unmet"
    parity = IncumbentParityReport(
        schema_version=INCUMBENT_PARITY_REPORT_SCHEMA_VERSION,
        generated_at=generated_at,
        controls=controls,
        status=evaluation.status,
        incumbent_present=True,
        incumbent_name=evaluation.incumbent_name,
        incumbent_kind=evaluation.incumbent_kind,
        parity_status=parity_status,
        comparison_metric=comparison_metric,
        recommended_action=recommended_action,
        relaytic_beats_incumbent=parity_status == "beats_incumbent",
        incumbent_stronger=parity_status == "below_incumbent",
        reduced_claim=evaluation.reduced_claim,
        test_gap=test_gap,
        summary=_incumbent_summary(evaluation.incumbent_name, parity_status, evaluation.reduced_claim),
        trace=trace,
    )
    beat_target = BeatTargetContract(
        schema_version=BEAT_TARGET_CONTRACT_SCHEMA_VERSION,
        generated_at=generated_at,
        controls=controls,
        status=evaluation.status,
        target_name=evaluation.incumbent_name,
        target_kind="incumbent",
        comparison_metric=comparison_metric,
        metric_direction=metric_direction,
        target_metric_value=incumbent_test,
        relaytic_metric_value=relaytic_test,
        contract_state=contract_state,
        recommended_action=recommended_action,
        reduced_claim=evaluation.reduced_claim,
        summary=_beat_target_summary(evaluation.incumbent_name, contract_state),
        trace=trace,
    )
    return parity, beat_target


def _predict_classification_probabilities(estimator: Any, features: np.ndarray, class_labels: list[str]) -> np.ndarray:
    if hasattr(estimator, "predict_proba"):
        probabilities = np.asarray(estimator.predict_proba(features), dtype=float)
        estimator_labels = [str(item) for item in getattr(estimator, "classes_", class_labels)]
        if probabilities.ndim == 1:
            probabilities = probabilities.reshape(-1, 1)
        if probabilities.shape[1] == len(class_labels) and estimator_labels == class_labels:
            return probabilities
        aligned = np.zeros((probabilities.shape[0], len(class_labels)), dtype=float)
        label_to_index = {str(label): idx for idx, label in enumerate(estimator_labels)}
        for output_index, label in enumerate(class_labels):
            if label in label_to_index and label_to_index[label] < probabilities.shape[1]:
                aligned[:, output_index] = probabilities[:, label_to_index[label]]
        if len(class_labels) == 2 and np.allclose(np.sum(aligned, axis=1), 0.0):
            positive_scores = probabilities[:, min(probabilities.shape[1] - 1, 0)]
            aligned[:, 1] = positive_scores
            aligned[:, 0] = 1.0 - positive_scores
        return aligned
    if hasattr(estimator, "decision_function"):
        decision = np.asarray(estimator.decision_function(features), dtype=float)
        if decision.ndim == 1 and len(class_labels) == 2:
            positive_scores = _sigmoid(decision)
            return np.column_stack([1.0 - positive_scores, positive_scores])
        if decision.ndim == 2 and decision.shape[1] == len(class_labels):
            shifted = decision - np.max(decision, axis=1, keepdims=True)
            exp_scores = np.exp(shifted)
            denom = np.sum(exp_scores, axis=1, keepdims=True)
            denom[denom <= 1e-12] = 1.0
            return exp_scores / denom
    predictions = np.asarray(estimator.predict(features), dtype=object)
    if predictions.shape[0] != features.shape[0]:
        raise ValueError("Incumbent prediction count does not match feature rows.")
    probabilities = np.zeros((predictions.shape[0], len(class_labels)), dtype=float)
    label_to_index = {str(label): idx for idx, label in enumerate(class_labels)}
    for row_index, prediction in enumerate(predictions):
        mapped = label_to_index.get(str(prediction))
        if mapped is not None:
            probabilities[row_index, mapped] = 1.0
    return probabilities


def _load_incumbent_object(path: Path, *, trust_model_deserialization: bool) -> dict[str, Any]:
    if not _trust_local_models_enabled(trust_model_deserialization):
        raise UnsafeIncumbentModelError("Relaytic blocks executable incumbent model deserialization by default.")
    suffix = path.suffix.lower()
    if suffix == ".joblib":
        try:
            import joblib  # type: ignore
        except Exception as exc:  # pragma: no cover - depends on optional dependency
            raise ValueError("Joblib is required to load `.joblib` incumbents.") from exc
        loaded = joblib.load(path)
    else:
        with path.open("rb") as handle:
            loaded = pickle.load(handle)
    if isinstance(loaded, dict):
        estimator = loaded.get("estimator") or loaded.get("model") or loaded.get("predictor")
        if estimator is None:
            raise ValueError("Incumbent adapter dict must contain `estimator`, `model`, or `predictor`.")
        feature_columns = loaded.get("feature_columns") or loaded.get("features")
        columns = [str(item) for item in feature_columns] if isinstance(feature_columns, (list, tuple)) else None
        return {"estimator": estimator, "feature_columns": columns}
    return {"estimator": loaded, "feature_columns": None}


def _trust_local_models_enabled(trust_model_deserialization: bool) -> bool:
    if trust_model_deserialization:
        return True
    value = str(os.environ.get(TRUST_LOCAL_MODELS_ENV, "")).strip().lower()
    return value in {"1", "true", "yes", "on"}


def _prediction_frame_to_probabilities(
    *,
    frame: Any,
    class_labels: list[str],
    prediction_column: str | None,
    score_column: str | None,
    positive_label: str | None,
) -> np.ndarray:
    if not class_labels:
        raise ValueError("Prediction replay requires at least one class label.")
    positive = positive_label if positive_label in class_labels else (class_labels[-1] if class_labels else None)
    positive_index = class_labels.index(positive) if positive in class_labels else max(0, len(class_labels) - 1)
    if score_column and score_column in frame.columns and len(class_labels) == 2:
        scores = frame[score_column].to_numpy(dtype=float)
        if np.any((scores < 0.0) | (scores > 1.0)):
            scores = _sigmoid(scores)
        scores = np.clip(scores, 1e-6, 1.0 - 1e-6)
        probabilities = np.zeros((scores.shape[0], 2), dtype=float)
        negative_index = 1 - positive_index
        probabilities[:, positive_index] = scores
        probabilities[:, negative_index] = 1.0 - scores
        return probabilities
    if not prediction_column or prediction_column not in frame.columns:
        raise ValueError("Prediction replay requires a prediction column when no binary score column is available.")
    probabilities = np.zeros((len(frame), len(class_labels)), dtype=float)
    label_to_index = {str(label): idx for idx, label in enumerate(class_labels)}
    predictions = frame[prediction_column].astype(str).tolist()
    for row_index, prediction in enumerate(predictions):
        mapped = label_to_index.get(str(prediction))
        if mapped is not None:
            probabilities[row_index, mapped] = 1.0
    if len(class_labels) == 2 and np.allclose(np.sum(probabilities, axis=1), 0.0):
        probabilities[:, positive_index] = 0.5
        probabilities[:, 1 - positive_index] = 0.5
    return probabilities


def _classification_metric_or_empty(
    part: dict[str, Any] | None,
    class_labels: list[str],
    positive_label: str | None,
    decision_threshold: float | None,
) -> dict[str, Any]:
    if not part:
        return {}
    y_true = list(part.get("y_true") or [])
    probabilities = np.asarray(part.get("probabilities"), dtype=float)
    if not y_true or probabilities.size == 0:
        return {}
    return classification_metrics(
        y_true=y_true,
        probabilities=probabilities,
        class_labels=class_labels,
        positive_label=positive_label,
        decision_threshold=decision_threshold,
    ).to_dict()


def _split_prediction_frame(*, prediction_frame: Any, split_frames: dict[str, Any]) -> dict[str, Any]:
    total_rows = sum(len(frame) for frame in split_frames.values())
    validation_rows = len(split_frames["validation"])
    test_rows = len(split_frames["test"])
    split_column = next((column for column in prediction_frame.columns if str(column).strip().lower() == "split"), None)
    if split_column:
        alias_map = {
            "train": "train",
            "training": "train",
            "validation": "validation",
            "valid": "validation",
            "val": "validation",
            "test": "test",
        }
        subsets: dict[str, Any] = {"train": None, "validation": None, "test": None}
        reason_codes: list[str] = ["split_column_present"]
        reduced_claim = False
        for raw_name, subset in prediction_frame.groupby(prediction_frame[split_column].astype(str).str.strip().str.lower()):
            mapped = alias_map.get(str(raw_name))
            if not mapped:
                continue
            candidate = subset.reset_index(drop=True)
            expected_rows = len(split_frames[mapped])
            if len(candidate) != expected_rows:
                reduced_claim = True
                reason_codes.append(f"split_row_mismatch_{mapped}")
                continue
            subsets[mapped] = candidate
        available = [name for name, frame in subsets.items() if frame is not None]
        if not available:
            raise ValueError("Prediction incumbent split mapping did not match any Relaytic split.")
        scope = "same_contract_full" if len(available) == 3 else "same_contract_partial"
        return {
            "frames": subsets,
            "scope": scope,
            "reduced_claim": reduced_claim or len(available) != 3,
            "reason_codes": reason_codes,
        }
    if len(prediction_frame) == total_rows:
        train_rows = len(split_frames["train"])
        validation_start = train_rows
        test_start = train_rows + validation_rows
        return {
            "frames": {
                "train": prediction_frame.iloc[:train_rows].reset_index(drop=True),
                "validation": prediction_frame.iloc[validation_start:test_start].reset_index(drop=True),
                "test": prediction_frame.iloc[test_start:].reset_index(drop=True),
            },
            "scope": "same_contract_full",
            "reduced_claim": False,
            "reason_codes": ["row_order_alignment"],
        }
    if len(prediction_frame) == validation_rows + test_rows:
        return {
            "frames": {
                "train": None,
                "validation": prediction_frame.iloc[:validation_rows].reset_index(drop=True),
                "test": prediction_frame.iloc[validation_rows:].reset_index(drop=True),
            },
            "scope": "validation_test_only",
            "reduced_claim": True,
            "reason_codes": ["partial_row_alignment"],
        }
    if len(prediction_frame) == test_rows:
        return {
            "frames": {
                "train": None,
                "validation": None,
                "test": prediction_frame.reset_index(drop=True),
            },
            "scope": "test_only",
            "reduced_claim": True,
            "reason_codes": ["test_only_predictions"],
        }
    raise ValueError("Prediction incumbent row count does not match Relaytic split sizes.")


def _detect_prediction_columns(prediction_frame: Any) -> tuple[str | None, str | None]:
    columns = {str(column).strip().lower(): str(column) for column in prediction_frame.columns}
    prediction_candidates = (
        "prediction",
        "predicted_label",
        "predicted_class",
        "pred",
        "label",
        "class",
        "y_pred",
    )
    score_candidates = (
        "score",
        "probability",
        "positive_probability",
        "positive_score",
        "prediction_score",
        "y_score",
        "prob",
        "p_positive",
    )
    prediction_column = next((columns[name] for name in prediction_candidates if name in columns), None)
    score_column = next((columns[name] for name in score_candidates if name in columns), None)
    return prediction_column, score_column


def _apply_linear_scorecard(
    frame: Any,
    weights: dict[str, float],
    intercept: float,
    class_labels: list[str],
    positive_label: str | None,
) -> np.ndarray:
    score = np.full(len(frame), float(intercept), dtype=float)
    for feature_name, weight in weights.items():
        score += frame[feature_name].to_numpy(dtype=float) * float(weight)
    positive_scores = _sigmoid(score)
    positive = positive_label if positive_label in class_labels else (class_labels[-1] if class_labels else None)
    positive_index = class_labels.index(positive) if positive in class_labels else max(0, len(class_labels) - 1)
    negative_index = 1 - positive_index
    probabilities = np.zeros((len(frame), len(class_labels)), dtype=float)
    probabilities[:, positive_index] = positive_scores
    probabilities[:, negative_index] = 1.0 - positive_scores
    return probabilities


def _apply_linear_regression_scorecard(frame: Any, weights: dict[str, float], intercept: float) -> np.ndarray:
    prediction = np.full(len(frame), float(intercept), dtype=float)
    for feature_name, weight in weights.items():
        prediction += frame[feature_name].to_numpy(dtype=float) * float(weight)
    return prediction


def _sigmoid(value: np.ndarray | float) -> np.ndarray:
    arr = np.asarray(value, dtype=float)
    clipped = np.clip(arr, -50.0, 50.0)
    return 1.0 / (1.0 + np.exp(-clipped))


def _normalize_incumbent_kind(*, path: Path, requested_kind: str | None) -> str:
    requested = _clean_text(requested_kind)
    if requested and requested != "auto":
        return requested
    suffix = path.suffix.lower()
    if suffix in {".pkl", ".pickle", ".joblib"}:
        return "model"
    if suffix in {".csv", ".tsv", ".xlsx", ".xls", ".parquet", ".pq", ".feather", ".jsonl", ".ndjson"}:
        return "predictions"
    if suffix == ".json":
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return "predictions"
        if isinstance(payload, dict) and (payload.get("weights") or payload.get("kind") == "linear_scorecard"):
            return "ruleset"
        return "predictions"
    return "predictions"


def _adapter_family(kind: str | None) -> str | None:
    mapping = {
        "model": "pickle_or_joblib_estimator",
        "predictions": "prediction_replay",
        "ruleset": "linear_scorecard",
    }
    return mapping.get(str(kind or "").strip())


def _incumbent_summary(incumbent_name: str | None, parity_status: str, reduced_claim: bool) -> str:
    label = incumbent_name or "configured incumbent"
    if parity_status == "beats_incumbent":
        return f"Relaytic beat incumbent `{label}` under the current comparison contract."
    if parity_status == "below_incumbent":
        return f"Relaytic still trails incumbent `{label}` under the current comparison contract."
    if parity_status == "near_incumbent":
        return f"Relaytic is near incumbent `{label}` but has not clearly beaten it yet."
    if reduced_claim:
        return f"Relaytic compared against incumbent `{label}` with reduced-claim confidence because only partial evidence was available."
    return f"Relaytic could not make a full incumbent-parity claim for `{label}`."


def _beat_target_summary(incumbent_name: str | None, contract_state: str) -> str:
    label = incumbent_name or "configured incumbent"
    if contract_state == "met":
        return f"Relaytic met the explicit beat-target contract against `{label}`."
    if contract_state == "unmet":
        return f"Relaytic did not yet meet the explicit beat-target contract against `{label}`."
    if contract_state == "near":
        return f"Relaytic is close to the beat-target contract against `{label}` but has not cleared it."
    if contract_state == "reduced_claim":
        return f"Relaytic only has reduced-claim beat-target evidence for `{label}`."
    return f"Relaytic does not yet have a stable beat-target contract state for `{label}`."


def _minority_label(y_true: np.ndarray) -> str | None:
    labels, counts = np.unique(np.asarray([str(item) for item in y_true], dtype=object), return_counts=True)
    if labels.size != 2:
        return None
    return str(labels[int(np.argmin(counts))])


def _select_binary_threshold(
    *,
    y_true: list[Any],
    probabilities: np.ndarray,
    class_labels: list[str],
    positive_label: str | None,
    threshold_policy: str,
    task_type: str,
) -> float | None:
    if task_type != "binary_classification" or len(class_labels) != 2:
        return None
    if positive_label is None or positive_label not in class_labels:
        positive_label = class_labels[int(np.argmin([sum(str(item) == label for item in y_true) for label in class_labels]))]
    if str(threshold_policy or "").strip().lower() in {"fixed_0_5", "default", "none"}:
        return 0.5
    candidates = np.linspace(0.15, 0.85, 15, dtype=float)
    best_threshold = 0.5
    best_score = float("-inf")
    for candidate in candidates:
        metrics = classification_metrics(
            y_true=y_true,
            probabilities=probabilities,
            class_labels=class_labels,
            positive_label=positive_label,
            decision_threshold=float(candidate),
        ).to_dict()
        score = float(metrics.get("f1", 0.0))
        if score > best_score + 1e-12:
            best_score = score
            best_threshold = float(candidate)
    return best_threshold


def _metric_value(metrics: dict[str, Any], metric: str) -> float | None:
    value = metrics.get(metric)
    if value is None:
        alias = {
            "stability_adjusted_mae": "mae",
            "mae_per_latency": "mae",
        }.get(str(metric or "").strip().lower())
        if alias:
            value = metrics.get(alias)
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _signed_gap(*, reference_value: float | None, relaytic_value: float | None, direction: str) -> float | None:
    if reference_value is None or relaytic_value is None:
        return None
    if direction == "lower_is_better":
        return float(relaytic_value - reference_value)
    return float(reference_value - relaytic_value)


def _relative_gap(absolute_gap: float | None, reference_value: float | None) -> float | None:
    if absolute_gap is None or reference_value is None:
        return None
    denom = abs(float(reference_value))
    if denom <= 1e-12:
        return None
    return float(abs(absolute_gap) / denom)


def _near_parity(*, controls: BenchmarkControls, absolute_gap: float | None, relative_gap: float | None) -> bool:
    if absolute_gap is None:
        return False
    if abs(float(absolute_gap)) <= float(controls.near_parity_absolute_delta):
        return True
    if relative_gap is not None and float(relative_gap) <= float(controls.near_parity_relative_delta):
        return True
    return False


def _clean_text(value: Any) -> str | None:
    text = str(value or "").strip()
    return text or None
