"""Slice 11 benchmark parity and reference comparison pipeline."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np

from relaytic.analytics.task_detection import assess_task_profile, is_classification_task
from relaytic.ingestion import load_tabular_data
from relaytic.modeling.evaluation import classification_metrics, regression_metrics
from relaytic.modeling.feature_pipeline import prepare_split_safe_feature_frames
from relaytic.modeling.normalization import MinMaxNormalizer
from relaytic.modeling.splitters import build_train_validation_test_split

from .incumbents import evaluate_incumbent
from .models import (
    BENCHMARK_GAP_REPORT_SCHEMA_VERSION,
    BENCHMARK_PARITY_REPORT_SCHEMA_VERSION,
    BEAT_TARGET_CONTRACT_SCHEMA_VERSION,
    EXTERNAL_CHALLENGER_EVALUATION_SCHEMA_VERSION,
    EXTERNAL_CHALLENGER_MANIFEST_SCHEMA_VERSION,
    INCUMBENT_PARITY_REPORT_SCHEMA_VERSION,
    REFERENCE_APPROACH_MATRIX_SCHEMA_VERSION,
    BenchmarkBundle,
    BenchmarkControls,
    BenchmarkGapReport,
    BenchmarkParityReport,
    BenchmarkTrace,
    BeatTargetContract,
    ExternalChallengerEvaluation,
    ExternalChallengerManifest,
    IncumbentParityReport,
    ReferenceApproachMatrix,
    build_benchmark_controls_from_policy,
)


@dataclass(frozen=True)
class BenchmarkRunResult:
    bundle: BenchmarkBundle
    review_markdown: str


def run_benchmark_review(
    *,
    run_dir: str | Path,
    data_path: str,
    policy: dict[str, Any],
    planning_bundle: dict[str, Any],
    mandate_bundle: dict[str, Any] | None = None,
    context_bundle: dict[str, Any] | None = None,
    incumbent_path: str | None = None,
    incumbent_kind: str | None = None,
    incumbent_name: str | None = None,
) -> BenchmarkRunResult:
    controls = build_benchmark_controls_from_policy(policy)
    plan = _bundle_item(planning_bundle, "plan")
    run_brief = _bundle_item(mandate_bundle or {}, "run_brief")
    task_brief = _bundle_item(context_bundle or {}, "task_brief")
    trace = BenchmarkTrace(
        agent="benchmark_referee",
        operating_mode="same_contract_reference_and_incumbent_parity",
        llm_used=False,
        llm_status="not_requested",
        deterministic_evidence=[
            "same_split_contract",
            "same_metric_contract",
            "same_feature_pipeline_contract",
            "public_reference_models",
            "explicit_incumbent_contract",
        ],
    )
    generated_at = _utc_now()
    benchmark_expected = _benchmark_expected(run_brief=run_brief, task_brief=task_brief)
    if not controls.enabled:
        bundle = _unavailable_bundle(
            controls=controls,
            generated_at=generated_at,
            trace=trace,
            benchmark_expected=benchmark_expected,
            summary="Relaytic benchmark parity is disabled by policy for this run.",
        )
        return BenchmarkRunResult(bundle=bundle, review_markdown=render_benchmark_review_markdown(bundle.to_dict()))

    execution_summary = dict(plan.get("execution_summary") or {})
    builder_handoff = dict(plan.get("builder_handoff") or {})
    target_column = _clean_text(plan.get("target_column")) or _clean_text(builder_handoff.get("target_column"))
    feature_columns = [str(item) for item in plan.get("feature_columns", []) if str(item).strip()]
    if not target_column or not feature_columns or not execution_summary:
        bundle = _unavailable_bundle(
            controls=controls,
            generated_at=generated_at,
            trace=trace,
            benchmark_expected=benchmark_expected,
            summary="Relaytic could not benchmark the run because plan or execution artifacts are incomplete.",
        )
        return BenchmarkRunResult(bundle=bundle, review_markdown=render_benchmark_review_markdown(bundle.to_dict()))

    sklearn_status, sklearn_notes = _sklearn_status()
    if sklearn_status != "ok":
        bundle = _unavailable_bundle(
            controls=controls,
            generated_at=generated_at,
            trace=BenchmarkTrace(
                agent=trace.agent,
                operating_mode=trace.operating_mode,
                llm_used=False,
                llm_status="not_requested",
                deterministic_evidence=trace.deterministic_evidence,
                advisory_notes=sklearn_notes,
            ),
            benchmark_expected=benchmark_expected,
            summary="Relaytic could not benchmark the run because scikit-learn references are unavailable.",
        )
        return BenchmarkRunResult(bundle=bundle, review_markdown=render_benchmark_review_markdown(bundle.to_dict()))

    loaded = load_tabular_data(data_path)
    frame = loaded.frame.copy()
    timestamp_column = _clean_text(plan.get("timestamp_column")) or _clean_text(builder_handoff.get("timestamp_column"))
    task_profile = assess_task_profile(
        frame=frame,
        target_column=target_column,
        data_mode=str(plan.get("data_mode", "")).strip() or _infer_data_mode(frame=frame, timestamp_column=timestamp_column),
        task_type_hint=_clean_text(plan.get("task_type")),
    )
    split = build_train_validation_test_split(
        n_rows=len(frame),
        data_mode=str(plan.get("data_mode", "")).strip() or task_profile.data_mode,
        task_type=task_profile.task_type,
        stratify_labels=frame[target_column] if is_classification_task(task_profile.task_type) else None,
    )
    split_frames = {
        "train": frame.iloc[split.train_indices].reset_index(drop=True),
        "validation": frame.iloc[split.validation_indices].reset_index(drop=True),
        "test": frame.iloc[split.test_indices].reset_index(drop=True),
    }
    prepared = prepare_split_safe_feature_frames(
        split_frames=split_frames,
        raw_feature_columns=feature_columns,
        target_column=target_column,
        missing_data_strategy=str(builder_handoff.get("missing_data_strategy", "fill_median")),
        fill_constant_value=None,
        task_type=task_profile.task_type,
    )
    prepared_frames = dict(prepared.get("frames", {}))
    preprocessing = dict(prepared.get("preprocessing", {}))
    model_feature_columns = [str(item) for item in prepared.get("model_feature_columns", []) if str(item).strip()]
    if not model_feature_columns:
        bundle = _unavailable_bundle(
            controls=controls,
            generated_at=generated_at,
            trace=trace,
            benchmark_expected=benchmark_expected,
            summary="Relaytic could not benchmark the run because preprocessing left no usable model features.",
        )
        return BenchmarkRunResult(bundle=bundle, review_markdown=render_benchmark_review_markdown(bundle.to_dict()))

    if bool(builder_handoff.get("normalize", True)):
        normalizer = MinMaxNormalizer()
        normalizer.fit(prepared_frames["train"], feature_columns=model_feature_columns)
        prepared_frames = {
            name: normalizer.transform_features(part)
            for name, part in prepared_frames.items()
        }

    lag_horizon = _optional_int(builder_handoff.get("lag_horizon_samples"))
    use_lagged_references = bool(
        controls.allow_time_series_references
        and lag_horizon
        and lag_horizon > 0
        and (
            str(plan.get("data_mode", "")).strip() == "time_series"
            or str(execution_summary.get("selected_model_family", "")).strip().startswith("lagged_")
        )
    )
    design = _prepare_reference_design(
        prepared_frames=prepared_frames,
        target_column=target_column,
        feature_columns=model_feature_columns,
        lag_horizon=lag_horizon if use_lagged_references else None,
    )
    reference_rows = _run_reference_matrix(
        controls=controls,
        task_type=task_profile.task_type,
        target_column=target_column,
        frames=design["frames"],
        feature_columns=design["feature_columns"],
        threshold_policy=_clean_text(builder_handoff.get("threshold_policy")) or "auto",
        lagged=use_lagged_references,
    )
    comparison_metric = _resolve_comparison_metric(
        primary_metric=_clean_text(plan.get("primary_metric")),
        selection_metric=_clean_text(execution_summary.get("selection_metric")),
        task_type=task_profile.task_type,
    )
    metric_direction = _metric_direction(comparison_metric)
    relaytic_reference = _relaytic_reference_row(
        plan=plan,
        execution_summary=execution_summary,
        comparison_metric=comparison_metric,
        metric_direction=metric_direction,
        preprocessing=preprocessing,
        use_lagged_references=use_lagged_references,
    )
    ranking = _rank_rows(
        comparison_metric=comparison_metric,
        metric_direction=metric_direction,
        relaytic_reference=relaytic_reference,
        references=reference_rows,
    )
    relaytic_rank = next((index + 1 for index, item in enumerate(ranking) if item.get("role") == "relaytic"), None)
    best_reference = next((item for item in ranking if item.get("role") == "reference"), None)
    winning_family = _clean_text(ranking[0].get("model_family")) if ranking else None
    gap = _gap_payload(
        controls=controls,
        comparison_metric=comparison_metric,
        metric_direction=metric_direction,
        relaytic_reference=relaytic_reference,
        best_reference=best_reference,
        relaytic_rank=relaytic_rank,
        total_compared_routes=len(ranking),
    )
    parity_status, recommended_action, parity_summary = _parity_decision(
        gap=gap,
        reference_count=len(reference_rows),
        benchmark_expected=benchmark_expected,
    )
    incumbent_outputs = evaluate_incumbent(
        incumbent_path=incumbent_path,
        incumbent_kind=incumbent_kind,
        incumbent_name=incumbent_name,
        controls=controls,
        generated_at=generated_at,
        trace=trace,
        task_type=task_profile.task_type,
        comparison_metric=comparison_metric,
        metric_direction=metric_direction,
        threshold_policy=_clean_text(builder_handoff.get("threshold_policy")) or "auto",
        split_frames=split_frames,
        prepared_frames=prepared_frames,
        feature_columns=model_feature_columns,
        target_column=target_column,
        relaytic_reference=relaytic_reference,
    )
    parity_status = incumbent_outputs["benchmark_parity_status_override"] or parity_status
    recommended_action = incumbent_outputs["benchmark_recommended_action_override"] or recommended_action
    parity_summary = incumbent_outputs["benchmark_summary_override"] or parity_summary

    matrix = ReferenceApproachMatrix(
        schema_version=REFERENCE_APPROACH_MATRIX_SCHEMA_VERSION,
        generated_at=generated_at,
        controls=controls,
        status="ok",
        task_type=task_profile.task_type,
        data_mode=str(plan.get("data_mode", "")).strip() or task_profile.data_mode,
        primary_metric=_clean_text(plan.get("primary_metric")) or comparison_metric,
        comparison_metric=comparison_metric,
        metric_direction=metric_direction,
        relaytic_reference=relaytic_reference,
        references=reference_rows,
        winning_reference_family=_clean_text(best_reference.get("model_family")) if best_reference else None,
        same_contract_guarantees=[
            "same_target_column",
            "same_train_validation_test_split",
            "same_feature_engineering_pipeline",
            "same_primary_metric_family",
        ],
        summary=(
            f"Relaytic compared the selected route against {len(reference_rows)} same-contract reference approach(es) "
            f"using `{comparison_metric}`."
        ),
        trace=trace,
    )
    gap_report = BenchmarkGapReport(
        schema_version=BENCHMARK_GAP_REPORT_SCHEMA_VERSION,
        generated_at=generated_at,
        controls=controls,
        status="ok",
        comparison_metric=comparison_metric,
        metric_direction=metric_direction,
        relaytic_family=_clean_text(relaytic_reference.get("model_family")),
        best_reference_family=_clean_text(best_reference.get("model_family")) if best_reference else None,
        relaytic_rank=relaytic_rank,
        total_compared_routes=len(ranking),
        validation_gap=gap["validation_gap"],
        test_gap=gap["test_gap"],
        validation_relative_gap=gap["validation_relative_gap"],
        test_relative_gap=gap["test_relative_gap"],
        relaytic_beats_best_reference=bool(gap["relaytic_beats_best_reference"]),
        near_parity=bool(gap["near_parity"]),
        summary=gap["summary"],
        trace=trace,
    )
    parity_report = BenchmarkParityReport(
        schema_version=BENCHMARK_PARITY_REPORT_SCHEMA_VERSION,
        generated_at=generated_at,
        controls=controls,
        status="ok",
        benchmark_expected=benchmark_expected,
        parity_status=parity_status,
        comparison_metric=comparison_metric,
        recommended_action=recommended_action,
        winning_family=winning_family,
        relaytic_family=_clean_text(relaytic_reference.get("model_family")),
        reference_count=len(reference_rows),
        strong_reference_available=bool(reference_rows),
        incumbent_present=bool(incumbent_outputs["incumbent_present"]),
        incumbent_name=incumbent_outputs["incumbent_name"],
        beat_target_state=incumbent_outputs["beat_target_state"],
        summary=parity_summary,
        trace=trace,
    )
    bundle = BenchmarkBundle(
        reference_approach_matrix=matrix,
        benchmark_gap_report=gap_report,
        benchmark_parity_report=parity_report,
        external_challenger_manifest=incumbent_outputs["manifest"],
        external_challenger_evaluation=incumbent_outputs["evaluation"],
        incumbent_parity_report=incumbent_outputs["parity"],
        beat_target_contract=incumbent_outputs["beat_target"],
    )
    return BenchmarkRunResult(bundle=bundle, review_markdown=render_benchmark_review_markdown(bundle.to_dict()))


def render_benchmark_review_markdown(bundle: BenchmarkBundle | dict[str, Any]) -> str:
    payload = bundle.to_dict() if isinstance(bundle, BenchmarkBundle) else dict(bundle)
    matrix = dict(payload.get("reference_approach_matrix", {}))
    gap = dict(payload.get("benchmark_gap_report", {}))
    parity = dict(payload.get("benchmark_parity_report", {}))
    incumbent = dict(payload.get("incumbent_parity_report", {}))
    beat_target = dict(payload.get("beat_target_contract", {}))
    lines = [
        "# Relaytic Benchmark Review",
        "",
        f"- Status: `{parity.get('status') or matrix.get('status') or 'unknown'}`",
        f"- Comparison metric: `{parity.get('comparison_metric') or matrix.get('comparison_metric') or 'unknown'}`",
        f"- Parity status: `{parity.get('parity_status') or 'unknown'}`",
        f"- Recommended action: `{parity.get('recommended_action') or 'unknown'}`",
        f"- Relaytic family: `{parity.get('relaytic_family') or gap.get('relaytic_family') or 'unknown'}`",
        f"- Winning family: `{parity.get('winning_family') or gap.get('best_reference_family') or 'unknown'}`",
        f"- Reference count: `{parity.get('reference_count', 0)}`",
    ]
    if incumbent:
        lines.extend(
            [
                f"- Incumbent present: `{incumbent.get('incumbent_present')}`",
                f"- Incumbent name: `{incumbent.get('incumbent_name') or 'none'}`",
                f"- Incumbent parity: `{incumbent.get('parity_status') or 'unknown'}`",
                f"- Beat-target state: `{beat_target.get('contract_state') or parity.get('beat_target_state') or 'unknown'}`",
            ]
        )
    if gap:
        lines.extend(
            [
                "",
                "## Gap",
                f"- Validation gap: `{gap.get('validation_gap')}`",
                f"- Test gap: `{gap.get('test_gap')}`",
                f"- Near parity: `{gap.get('near_parity')}`",
                f"- Relaytic beats best reference: `{gap.get('relaytic_beats_best_reference')}`",
            ]
        )
    if incumbent:
        lines.extend(
            [
                "",
                "## Incumbent",
                f"- Recommended action: `{incumbent.get('recommended_action') or beat_target.get('recommended_action') or 'unknown'}`",
                f"- Relaytic beats incumbent: `{incumbent.get('relaytic_beats_incumbent')}`",
                f"- Incumbent stronger: `{incumbent.get('incumbent_stronger')}`",
                f"- Reduced claim: `{incumbent.get('reduced_claim')}`",
                f"- Test gap: `{incumbent.get('test_gap')}`",
            ]
        )
    references = list(matrix.get("references", []))
    if references:
        lines.extend(["", "## Reference Approaches"])
        for item in references[:5]:
            lines.append(
                f"- `{item.get('model_family')}` validation=`{item.get('validation_metric')}` "
                f"test=`{item.get('test_metric')}` rank=`{item.get('rank')}`"
            )
    return "\n".join(lines).rstrip() + "\n"


def _sklearn_status() -> tuple[str, list[str]]:
    try:
        import sklearn  # noqa: F401
    except Exception:
        return "not_installed", ["scikit-learn is required for the current benchmark-reference layer."]
    return "ok", []


def _prepare_reference_design(
    *,
    prepared_frames: dict[str, Any],
    target_column: str,
    feature_columns: list[str],
    lag_horizon: int | None,
) -> dict[str, Any]:
    if not lag_horizon or lag_horizon <= 0:
        return {"frames": prepared_frames, "feature_columns": list(feature_columns)}
    train = prepared_frames["train"]
    validation = prepared_frames["validation"]
    test = prepared_frames["test"]
    train_design = _build_lagged_design_frame(
        frame=train,
        feature_columns=feature_columns,
        target_column=target_column,
        lag_horizon=lag_horizon,
    )
    validation_design = _build_lagged_design_frame(
        frame=validation,
        feature_columns=feature_columns,
        target_column=target_column,
        lag_horizon=lag_horizon,
        context_frame=train,
    )
    test_design = _build_lagged_design_frame(
        frame=test,
        feature_columns=feature_columns,
        target_column=target_column,
        lag_horizon=lag_horizon,
        context_frame=_concat_frames(train, validation),
    )
    lagged_feature_columns = [column for column in train_design.columns if column != target_column]
    return {
        "frames": {
            "train": train_design,
            "validation": validation_design,
            "test": test_design,
        },
        "feature_columns": lagged_feature_columns,
    }


def _run_reference_matrix(
    *,
    controls: BenchmarkControls,
    task_type: str,
    target_column: str,
    frames: dict[str, Any],
    feature_columns: list[str],
    threshold_policy: str,
    lagged: bool,
) -> list[dict[str, Any]]:
    specs = _reference_specs(task_type=task_type, lagged=lagged)[: controls.max_reference_models]
    rows: list[dict[str, Any]] = []
    for spec in specs:
        rows.append(
            _fit_reference_candidate(
                spec=spec,
                task_type=task_type,
                target_column=target_column,
                frames=frames,
                feature_columns=feature_columns,
                threshold_policy=threshold_policy,
            )
        )
    return rows


def _fit_reference_candidate(
    *,
    spec: dict[str, Any],
    task_type: str,
    target_column: str,
    frames: dict[str, Any],
    feature_columns: list[str],
    threshold_policy: str,
) -> dict[str, Any]:
    estimator = spec["builder"]()
    train_x = frames["train"][feature_columns].to_numpy(dtype=float)
    validation_x = frames["validation"][feature_columns].to_numpy(dtype=float)
    test_x = frames["test"][feature_columns].to_numpy(dtype=float)
    if is_classification_task(task_type):
        train_y = frames["train"][target_column].astype(str).to_numpy(dtype=object)
        validation_y = frames["validation"][target_column].astype(str).to_numpy(dtype=object)
        test_y = frames["test"][target_column].astype(str).to_numpy(dtype=object)
        estimator.fit(train_x, train_y)
        class_labels = [str(item) for item in getattr(estimator, "classes_", [])]
        train_proba = np.asarray(estimator.predict_proba(train_x), dtype=float)
        validation_proba = np.asarray(estimator.predict_proba(validation_x), dtype=float)
        test_proba = np.asarray(estimator.predict_proba(test_x), dtype=float)
        positive_label = _minority_label(train_y)
        decision_threshold = _select_binary_threshold(
            y_true=validation_y.tolist(),
            probabilities=validation_proba,
            class_labels=class_labels,
            positive_label=positive_label,
            threshold_policy=threshold_policy,
            task_type=task_type,
        )
        train_metrics = classification_metrics(
            y_true=train_y.tolist(),
            probabilities=train_proba,
            class_labels=class_labels,
            positive_label=positive_label,
            decision_threshold=decision_threshold,
        ).to_dict()
        validation_metrics = classification_metrics(
            y_true=validation_y.tolist(),
            probabilities=validation_proba,
            class_labels=class_labels,
            positive_label=positive_label,
            decision_threshold=decision_threshold,
        ).to_dict()
        test_metrics = classification_metrics(
            y_true=test_y.tolist(),
            probabilities=test_proba,
            class_labels=class_labels,
            positive_label=positive_label,
            decision_threshold=decision_threshold,
        ).to_dict()
        return {
            "role": "reference",
            "model_family": spec["name"],
            "library": "scikit-learn",
            "task_type": task_type,
            "train_metric": train_metrics,
            "validation_metric": validation_metrics,
            "test_metric": test_metrics,
            "decision_threshold": decision_threshold,
            "notes": spec["notes"],
        }

    train_y = frames["train"][target_column].to_numpy(dtype=float)
    validation_y = frames["validation"][target_column].to_numpy(dtype=float)
    test_y = frames["test"][target_column].to_numpy(dtype=float)
    estimator.fit(train_x, train_y)
    train_pred = np.asarray(estimator.predict(train_x), dtype=float)
    validation_pred = np.asarray(estimator.predict(validation_x), dtype=float)
    test_pred = np.asarray(estimator.predict(test_x), dtype=float)
    return {
        "role": "reference",
        "model_family": spec["name"],
        "library": "scikit-learn",
        "task_type": task_type,
        "train_metric": regression_metrics(y_true=train_y, y_pred=train_pred).to_dict(),
        "validation_metric": regression_metrics(y_true=validation_y, y_pred=validation_pred).to_dict(),
        "test_metric": regression_metrics(y_true=test_y, y_pred=test_pred).to_dict(),
        "notes": spec["notes"],
    }


def _reference_specs(*, task_type: str, lagged: bool) -> list[dict[str, Any]]:
    from sklearn.ensemble import (
        GradientBoostingClassifier,
        GradientBoostingRegressor,
        RandomForestClassifier,
        RandomForestRegressor,
    )
    from sklearn.linear_model import LogisticRegression, Ridge

    prefix = "lagged_" if lagged else ""
    if is_classification_task(task_type):
        return [
            {
                "name": f"sklearn_{prefix}logistic_regression",
                "builder": lambda: LogisticRegression(max_iter=1000, class_weight="balanced", random_state=42),
                "notes": "Regularized linear classification reference on the same split-safe feature frame.",
            },
            {
                "name": f"sklearn_{prefix}random_forest_classifier",
                "builder": lambda: RandomForestClassifier(
                    n_estimators=200,
                    min_samples_leaf=2,
                    class_weight="balanced",
                    random_state=42,
                ),
                "notes": "Random-forest classifier reference on the same feature contract.",
            },
            {
                "name": f"sklearn_{prefix}gradient_boosting_classifier",
                "builder": lambda: GradientBoostingClassifier(random_state=42),
                "notes": "Gradient-boosting classifier reference on the same feature contract.",
            },
        ]
    return [
        {
            "name": f"sklearn_{prefix}ridge",
            "builder": lambda: Ridge(alpha=1.0, random_state=42),
            "notes": "Linear ridge regression reference on the same split-safe feature frame.",
        },
        {
            "name": f"sklearn_{prefix}random_forest_regressor",
            "builder": lambda: RandomForestRegressor(
                n_estimators=200,
                min_samples_leaf=2,
                random_state=42,
            ),
            "notes": "Random-forest regressor reference on the same feature contract.",
        },
        {
            "name": f"sklearn_{prefix}gradient_boosting_regressor",
            "builder": lambda: GradientBoostingRegressor(random_state=42),
            "notes": "Gradient-boosting regressor reference on the same feature contract.",
        },
    ]


def _relaytic_reference_row(
    *,
    plan: dict[str, Any],
    execution_summary: dict[str, Any],
    comparison_metric: str,
    metric_direction: str,
    preprocessing: dict[str, Any],
    use_lagged_references: bool,
) -> dict[str, Any]:
    selected_metrics = dict(execution_summary.get("selected_metrics") or {})
    return {
        "role": "relaytic",
        "model_family": _clean_text(execution_summary.get("selected_model_family")),
        "comparison_metric": comparison_metric,
        "metric_direction": metric_direction,
        "train_metric": dict(selected_metrics.get("train") or {}),
        "validation_metric": dict(selected_metrics.get("validation") or {}),
        "test_metric": dict(selected_metrics.get("test") or {}),
        "primary_metric": _clean_text(plan.get("primary_metric")),
        "selection_metric": _clean_text(execution_summary.get("selection_metric")),
        "feature_engineering_summary": dict(preprocessing.get("feature_engineering_summary", {})),
        "used_lagged_reference_contract": use_lagged_references,
        "selected_hyperparameters": dict(execution_summary.get("selected_hyperparameters") or {}),
    }


def _rank_rows(
    *,
    comparison_metric: str,
    metric_direction: str,
    relaytic_reference: dict[str, Any],
    references: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    rows = [relaytic_reference, *references]
    ranked = sorted(
        rows,
        key=lambda item: _sort_key(
            metrics=dict(item.get("validation_metric", {})),
            metric=comparison_metric,
            direction=metric_direction,
            model_family=_clean_text(item.get("model_family")) or "unknown",
            role=_clean_text(item.get("role")) or "reference",
        ),
    )
    for index, item in enumerate(ranked, start=1):
        item["rank"] = index
    return ranked


def _gap_payload(
    *,
    controls: BenchmarkControls,
    comparison_metric: str,
    metric_direction: str,
    relaytic_reference: dict[str, Any],
    best_reference: dict[str, Any] | None,
    relaytic_rank: int | None,
    total_compared_routes: int,
) -> dict[str, Any]:
    relaytic_validation = _metric_value(dict(relaytic_reference.get("validation_metric", {})), comparison_metric)
    relaytic_test = _metric_value(dict(relaytic_reference.get("test_metric", {})), comparison_metric)
    if not best_reference:
        return {
            "validation_gap": None,
            "test_gap": None,
            "validation_relative_gap": None,
            "test_relative_gap": None,
            "relaytic_beats_best_reference": True,
            "near_parity": True,
            "summary": "Relaytic did not have any strong reference approaches to compare against in this run.",
        }
    reference_validation = _metric_value(dict(best_reference.get("validation_metric", {})), comparison_metric)
    reference_test = _metric_value(dict(best_reference.get("test_metric", {})), comparison_metric)
    validation_gap = _signed_gap(
        reference_value=reference_validation,
        relaytic_value=relaytic_validation,
        direction=metric_direction,
    )
    test_gap = _signed_gap(
        reference_value=reference_test,
        relaytic_value=relaytic_test,
        direction=metric_direction,
    )
    validation_relative_gap = _relative_gap(validation_gap, reference_validation)
    test_relative_gap = _relative_gap(test_gap, reference_test)
    near_parity = _near_parity(
        controls=controls,
        absolute_gap=test_gap,
        relative_gap=test_relative_gap,
    )
    relaytic_beats = bool(test_gap is not None and test_gap <= 0.0)
    summary = (
        f"Relaytic ranked `{relaytic_rank or 'unknown'}` of `{total_compared_routes}` on `{comparison_metric}`; "
        f"best reference was `{_clean_text(best_reference.get('model_family')) or 'unknown'}`."
    )
    return {
        "validation_gap": validation_gap,
        "test_gap": test_gap,
        "validation_relative_gap": validation_relative_gap,
        "test_relative_gap": test_relative_gap,
        "relaytic_beats_best_reference": relaytic_beats,
        "near_parity": near_parity,
        "summary": summary,
    }


def _parity_decision(
    *,
    gap: dict[str, Any],
    reference_count: int,
    benchmark_expected: bool,
) -> tuple[str, str, str]:
    if reference_count <= 0:
        return (
            "reference_unavailable",
            "continue_experimentation",
            "Relaytic could not compare against a strong reference model in this run.",
        )
    if bool(gap.get("relaytic_beats_best_reference")):
        return (
            "meets_or_exceeds_reference",
            "hold_current_route",
            "Relaytic meets or exceeds the strongest current reference on the comparison metric.",
        )
    if bool(gap.get("near_parity")):
        return (
            "near_parity",
            "continue_experimentation",
            "Relaytic is close to the strongest current reference and should keep iterating honestly.",
        )
    if benchmark_expected:
        return (
            "below_reference",
            "expand_challenger_portfolio",
            "Relaytic is currently below the strongest reference and should widen challenger/search pressure.",
        )
    return (
        "below_reference",
        "continue_experimentation",
        "Relaytic is currently below the strongest reference and should keep iterating before stronger claims.",
    )


def _build_lagged_design_frame(
    *,
    frame: Any,
    feature_columns: list[str],
    target_column: str,
    lag_horizon: int,
    context_frame: Any | None = None,
) -> Any:
    import pandas as pd

    required = list(feature_columns) + [target_column]
    if context_frame is not None:
        combined = pd.concat([context_frame[required], frame[required]], ignore_index=True)
        context_len = int(len(context_frame))
    else:
        combined = frame[required].copy().reset_index(drop=True)
        context_len = 0
    out = pd.DataFrame(index=combined.index)
    for column in feature_columns:
        numeric = combined[column].astype(float)
        out[f"{column}__t"] = numeric
        for lag in range(1, int(lag_horizon) + 1):
            out[f"{column}__lag{lag}"] = numeric.shift(lag)
    out[target_column] = combined[target_column]
    out["_is_current"] = False
    out.loc[context_len:, "_is_current"] = True
    out = out.dropna()
    out = out[out["_is_current"]].drop(columns=["_is_current"]).reset_index(drop=True)
    return out


def _concat_frames(left: Any, right: Any) -> Any:
    import pandas as pd

    return pd.concat([left, right], ignore_index=True)


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


def _minority_label(y_true: np.ndarray) -> str | None:
    labels, counts = np.unique(np.asarray([str(item) for item in y_true], dtype=object), return_counts=True)
    if labels.size != 2:
        return None
    return str(labels[int(np.argmin(counts))])


def _resolve_comparison_metric(*, primary_metric: str | None, selection_metric: str | None, task_type: str) -> str:
    for candidate in (_clean_text(primary_metric), _clean_text(selection_metric)):
        if candidate:
            return candidate
    if is_classification_task(task_type):
        return "pr_auc" if task_type == "binary_classification" else "f1"
    return "mae"


def _metric_direction(metric: str) -> str:
    lowered = str(metric or "").strip().lower()
    if lowered in {"mae", "rmse", "mape", "log_loss", "brier_score", "expected_calibration_error"}:
        return "lower_is_better"
    return "higher_is_better"


def _metric_value(metrics: dict[str, Any], metric: str) -> float | None:
    value = metrics.get(metric)
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _sort_key(*, metrics: dict[str, Any], metric: str, direction: str, model_family: str, role: str) -> tuple[Any, ...]:
    value = _metric_value(metrics, metric)
    missing_rank = 1 if value is None else 0
    if value is None:
        metric_key = float("inf")
    elif direction == "lower_is_better":
        metric_key = float(value)
    else:
        metric_key = -float(value)
    role_key = 1 if role == "relaytic" else 0
    return (missing_rank, metric_key, role_key, model_family)


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


def _benchmark_expected(*, run_brief: dict[str, Any], task_brief: dict[str, Any]) -> bool:
    corpus = " ".join(
        [
            str(run_brief.get("objective", "")),
            str(run_brief.get("success_criteria", "")),
            str(task_brief.get("problem_statement", "")),
            str(task_brief.get("success_criteria", "")),
        ]
    ).lower()
    return any(token in corpus for token in ("benchmark", "baseline", "reference", "parity", "sota", "state of the art"))


def _disabled_bundle(
    *,
    controls: BenchmarkControls,
    generated_at: str,
    trace: BenchmarkTrace,
    benchmark_expected: bool,
    summary: str,
) -> BenchmarkBundle:
    return _unavailable_bundle(
        controls=controls,
        generated_at=generated_at,
        trace=trace,
        benchmark_expected=benchmark_expected,
        summary=summary,
        status="disabled",
        recommended_action="continue_experimentation",
        parity_status="reference_unavailable",
    )


def _unavailable_bundle(
    *,
    controls: BenchmarkControls,
    generated_at: str,
    trace: BenchmarkTrace,
    benchmark_expected: bool,
    summary: str,
    status: str = "unavailable",
    recommended_action: str | None = None,
    parity_status: str = "reference_unavailable",
) -> BenchmarkBundle:
    recommendation = recommended_action or ("benchmark_needed" if benchmark_expected else "continue_experimentation")
    matrix = ReferenceApproachMatrix(
        schema_version=REFERENCE_APPROACH_MATRIX_SCHEMA_VERSION,
        generated_at=generated_at,
        controls=controls,
        status=status,
        task_type="unknown",
        data_mode="unknown",
        primary_metric="unknown",
        comparison_metric="unknown",
        metric_direction="higher_is_better",
        relaytic_reference={},
        references=[],
        winning_reference_family=None,
        same_contract_guarantees=[],
        summary=summary,
        trace=trace,
    )
    gap_report = BenchmarkGapReport(
        schema_version=BENCHMARK_GAP_REPORT_SCHEMA_VERSION,
        generated_at=generated_at,
        controls=controls,
        status=status,
        comparison_metric="unknown",
        metric_direction="higher_is_better",
        relaytic_family=None,
        best_reference_family=None,
        relaytic_rank=None,
        total_compared_routes=0,
        validation_gap=None,
        test_gap=None,
        validation_relative_gap=None,
        test_relative_gap=None,
        relaytic_beats_best_reference=False,
        near_parity=False,
        summary=summary,
        trace=trace,
    )
    parity_report = BenchmarkParityReport(
        schema_version=BENCHMARK_PARITY_REPORT_SCHEMA_VERSION,
        generated_at=generated_at,
        controls=controls,
        status=status,
        benchmark_expected=benchmark_expected,
        parity_status=parity_status,
        comparison_metric="unknown",
        recommended_action=recommendation,
        winning_family=None,
        relaytic_family=None,
        reference_count=0,
        strong_reference_available=False,
        summary=summary,
        trace=trace,
    )
    incumbent_manifest = ExternalChallengerManifest(
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
        summary="Relaytic did not receive an imported incumbent for this benchmark bundle.",
        trace=trace,
    )
    incumbent_evaluation = ExternalChallengerEvaluation(
        schema_version=EXTERNAL_CHALLENGER_EVALUATION_SCHEMA_VERSION,
        generated_at=generated_at,
        controls=controls,
        status="not_configured",
        incumbent_name=None,
        incumbent_kind=None,
        evaluation_mode="none",
        comparison_metric="unknown",
        metric_direction="higher_is_better",
        reevaluated_locally=False,
        reduced_claim=False,
        evaluation_scope="none",
        train_metric={},
        validation_metric={},
        test_metric={},
        decision_threshold=None,
        reason_codes=["no_incumbent_configured"],
        summary="Relaytic did not evaluate an imported incumbent for this benchmark bundle.",
        trace=trace,
    )
    incumbent_parity = IncumbentParityReport(
        schema_version=INCUMBENT_PARITY_REPORT_SCHEMA_VERSION,
        generated_at=generated_at,
        controls=controls,
        status="not_configured",
        incumbent_present=False,
        incumbent_name=None,
        incumbent_kind=None,
        parity_status="no_incumbent",
        comparison_metric="unknown",
        recommended_action=recommendation,
        relaytic_beats_incumbent=False,
        incumbent_stronger=False,
        reduced_claim=False,
        test_gap=None,
        summary="Relaytic has no imported incumbent for this benchmark bundle.",
        trace=trace,
    )
    beat_target = BeatTargetContract(
        schema_version=BEAT_TARGET_CONTRACT_SCHEMA_VERSION,
        generated_at=generated_at,
        controls=controls,
        status="not_configured",
        target_name=None,
        target_kind="none",
        comparison_metric="unknown",
        metric_direction="higher_is_better",
        target_metric_value=None,
        relaytic_metric_value=None,
        contract_state="not_configured",
        recommended_action=recommendation,
        reduced_claim=False,
        summary="Relaytic did not receive an explicit incumbent beat-target for this benchmark bundle.",
        trace=trace,
    )
    return BenchmarkBundle(
        reference_approach_matrix=matrix,
        benchmark_gap_report=gap_report,
        benchmark_parity_report=parity_report,
        external_challenger_manifest=incumbent_manifest,
        external_challenger_evaluation=incumbent_evaluation,
        incumbent_parity_report=incumbent_parity,
        beat_target_contract=beat_target,
    )


def _bundle_item(bundle: dict[str, Any] | None, key: str) -> dict[str, Any]:
    if not isinstance(bundle, dict):
        return {}
    value = bundle.get(key)
    return value if isinstance(value, dict) else {}


def _clean_text(value: Any) -> str | None:
    text = str(value or "").strip()
    return text or None


def _optional_int(value: Any) -> int | None:
    try:
        if value is None or str(value).strip() == "":
            return None
        return int(value)
    except (TypeError, ValueError):
        return None


def _infer_data_mode(*, frame: Any, timestamp_column: str | None) -> str:
    if timestamp_column and timestamp_column in frame.columns:
        return "time_series"
    return "steady_state"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()
