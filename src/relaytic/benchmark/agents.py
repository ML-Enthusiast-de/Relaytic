"""Slice 11 benchmark parity and reference comparison pipeline."""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime, timezone
import json
from pathlib import Path
from statistics import fmean, pstdev
from typing import Any

import numpy as np

from relaytic.analytics import (
    infer_benchmark_expected,
    read_architecture_routing_artifacts,
    read_task_contract_artifacts,
)
from relaytic.analytics.task_detection import assess_task_profile, is_classification_task
from relaytic.decision import read_decision_bundle
from relaytic.evals import read_eval_bundle, run_agent_evals, write_eval_bundle
from relaytic.ingestion import load_tabular_data
from relaytic.modeling.evaluation import classification_metrics, regression_metrics
from relaytic.modeling.feature_pipeline import prepare_split_safe_feature_frames
from relaytic.modeling.normalization import MinMaxNormalizer
from relaytic.modeling.splitters import build_train_validation_test_split
from relaytic.modeling.training import train_surrogate_candidates
from relaytic.tracing import read_trace_bundle

from .incumbents import evaluate_incumbent
from .models import (
    BENCHMARK_ABLATION_MATRIX_SCHEMA_VERSION,
    BENCHMARK_CLAIMS_REPORT_SCHEMA_VERSION,
    BENCHMARK_GAP_REPORT_SCHEMA_VERSION,
    BENCHMARK_PARITY_REPORT_SCHEMA_VERSION,
    BEAT_TARGET_CONTRACT_SCHEMA_VERSION,
    CANDIDATE_QUARANTINE_SCHEMA_VERSION,
    DATASET_LEAKAGE_AUDIT_SCHEMA_VERSION,
    EXTERNAL_CHALLENGER_EVALUATION_SCHEMA_VERSION,
    EXTERNAL_CHALLENGER_MANIFEST_SCHEMA_VERSION,
    INCUMBENT_PARITY_REPORT_SCHEMA_VERSION,
    BENCHMARK_RELEASE_GATE_SCHEMA_VERSION,
    BENCHMARK_TRUTH_AUDIT_SCHEMA_VERSION,
    PAPER_CLAIM_GUARD_REPORT_SCHEMA_VERSION,
    PAPER_BENCHMARK_MANIFEST_SCHEMA_VERSION,
    PAPER_BENCHMARK_TABLE_SCHEMA_VERSION,
    PROMOTION_READINESS_REPORT_SCHEMA_VERSION,
    REFERENCE_APPROACH_MATRIX_SCHEMA_VERSION,
    RERUN_VARIANCE_REPORT_SCHEMA_VERSION,
    SHADOW_TRIAL_MANIFEST_SCHEMA_VERSION,
    SHADOW_TRIAL_SCORECARD_SCHEMA_VERSION,
    BenchmarkAblationMatrix,
    BenchmarkBundle,
    BenchmarkClaimsReport,
    BenchmarkReleaseGate,
    BenchmarkTruthAudit,
    CandidateQuarantine,
    BenchmarkControls,
    BenchmarkGapReport,
    BenchmarkParityReport,
    BenchmarkTrace,
    BeatTargetContract,
    DatasetLeakageAudit,
    ExternalChallengerEvaluation,
    ExternalChallengerManifest,
    IncumbentParityReport,
    PaperClaimGuardReport,
    PaperBenchmarkManifest,
    PaperBenchmarkTable,
    PromotionReadinessReport,
    ReferenceApproachMatrix,
    RerunVarianceReport,
    ShadowTrialManifest,
    ShadowTrialScorecard,
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
    trust_model_deserialization: bool = False,
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
    task_contract_bundle = read_task_contract_artifacts(run_dir)
    decision_bundle = read_decision_bundle(run_dir)
    architecture_bundle = read_architecture_routing_artifacts(run_dir)
    eval_bundle = _ensure_eval_bundle(run_dir=run_dir, policy=policy)
    trace_bundle = read_trace_bundle(run_dir)
    task_profile_contract = dict(task_contract_bundle.get("task_profile_contract", {}))
    metric_contract = dict(task_contract_bundle.get("metric_contract", {}))
    benchmark_mode_report = dict(task_contract_bundle.get("benchmark_mode_report", {}))
    benchmark_truth_precheck = dict(task_contract_bundle.get("benchmark_truth_precheck", {}))
    benchmark_expected = (
        bool(benchmark_mode_report.get("benchmark_expected"))
        if benchmark_mode_report
        else infer_benchmark_expected(run_brief=run_brief, task_brief=task_brief)
    )
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
    if benchmark_truth_precheck and benchmark_truth_precheck.get("safe_to_rank") is False:
        bundle = _unavailable_bundle(
            controls=controls,
            generated_at=generated_at,
            trace=BenchmarkTrace(
                agent=trace.agent,
                operating_mode=trace.operating_mode,
                llm_used=False,
                llm_status="not_requested",
                deterministic_evidence=trace.deterministic_evidence,
                advisory_notes=[
                    str(item)
                    for item in benchmark_truth_precheck.get("reason_codes", [])
                    if str(item).strip()
                ],
            ),
            benchmark_expected=benchmark_expected,
            summary=str(benchmark_truth_precheck.get("summary") or "Relaytic blocked benchmark ranking because truth prechecks failed."),
            blocked_reason_codes=[
                str(item)
                for item in benchmark_truth_precheck.get("reason_codes", [])
                if str(item).strip()
            ],
        )
        return BenchmarkRunResult(bundle=bundle, review_markdown=render_benchmark_review_markdown(bundle.to_dict()))

    loaded = load_tabular_data(data_path)
    frame = loaded.frame.copy()
    timestamp_column = _clean_text(plan.get("timestamp_column")) or _clean_text(builder_handoff.get("timestamp_column"))
    task_profile = assess_task_profile(
        frame=frame,
        target_column=target_column,
        data_mode=str(plan.get("data_mode", "")).strip() or _infer_data_mode(frame=frame, timestamp_column=timestamp_column),
        task_type_hint=_clean_text(task_profile_contract.get("task_type")) or _clean_text(plan.get("task_type")),
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
    if lag_horizon is None:
        lag_horizon = _optional_int(execution_summary.get("lag_horizon_samples"))
    if lag_horizon is None and task_profile.data_mode == "time_series":
        lag_horizon = 3
    use_lagged_references = bool(
        controls.allow_time_series_references
        and lag_horizon
        and lag_horizon > 0
        and task_profile.data_mode == "time_series"
    )
    ordinary_design = _prepare_reference_design(
        prepared_frames=prepared_frames,
        target_column=target_column,
        feature_columns=model_feature_columns,
        lag_horizon=None,
    )
    reference_rows = _run_reference_matrix(
        controls=controls,
        task_type=task_profile.task_type,
        data_mode=task_profile.data_mode,
        target_column=target_column,
        frames=ordinary_design["frames"],
        feature_columns=ordinary_design["feature_columns"],
        threshold_policy=_clean_text(builder_handoff.get("threshold_policy")) or "auto",
        lagged=False,
    )
    if use_lagged_references:
        lagged_design = _prepare_reference_design(
            prepared_frames=prepared_frames,
            target_column=target_column,
            feature_columns=model_feature_columns,
            lag_horizon=lag_horizon,
        )
        reference_rows.extend(
            _run_reference_matrix(
                controls=controls,
                task_type=task_profile.task_type,
                data_mode=task_profile.data_mode,
                target_column=target_column,
                frames=lagged_design["frames"],
                feature_columns=lagged_design["feature_columns"],
                threshold_policy=_clean_text(builder_handoff.get("threshold_policy")) or "auto",
                lagged=True,
            )
        )
    comparison_metric = _resolve_comparison_metric(
        primary_metric=_clean_text(metric_contract.get("benchmark_comparison_metric")) or _clean_text(plan.get("primary_metric")),
        selection_metric=_clean_text(metric_contract.get("selection_metric")) or _clean_text(execution_summary.get("selection_metric")),
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
        data_mode=task_profile.data_mode,
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
        trust_model_deserialization=trust_model_deserialization,
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
    paper_manifest = _build_paper_benchmark_manifest(
        run_dir=run_dir,
        data_path=data_path,
        generated_at=generated_at,
        controls=controls,
        trace=trace,
        context_bundle=context_bundle or {},
        planning_bundle=planning_bundle,
        task_profile=task_profile,
        comparison_metric=comparison_metric,
        metric_direction=metric_direction,
        relaytic_reference=relaytic_reference,
        reference_rows=reference_rows,
        execution_summary=execution_summary,
        benchmark_expected=benchmark_expected,
    )
    paper_table = _build_paper_benchmark_table(
        generated_at=generated_at,
        controls=controls,
        trace=trace,
        ranking=ranking,
        comparison_metric=comparison_metric,
        metric_direction=metric_direction,
        relaytic_rank=relaytic_rank,
    )
    ablation_matrix = _build_benchmark_ablation_matrix(
        run_dir=run_dir,
        generated_at=generated_at,
        controls=controls,
        trace=trace,
        comparison_metric=comparison_metric,
        metric_direction=metric_direction,
        relaytic_reference=relaytic_reference,
        reference_rows=reference_rows,
        task_type=task_profile.task_type,
        selected_model_family=_clean_text(relaytic_reference.get("model_family")),
        data_mode=task_profile.data_mode,
    )
    rerun_variance_report = _build_rerun_variance_report(
        run_dir=run_dir,
        generated_at=generated_at,
        controls=controls,
        trace=trace,
        comparison_metric=comparison_metric,
        metric_direction=metric_direction,
        relaytic_reference=relaytic_reference,
        task_type=task_profile.task_type,
        target_column=target_column,
        data_mode=task_profile.data_mode,
        row_count=len(frame),
        column_count=len(frame.columns),
    )
    benchmark_claims_report = _build_benchmark_claims_report(
        run_dir=run_dir,
        generated_at=generated_at,
        controls=controls,
        trace=trace,
        parity_report=parity_report,
        gap_report=gap_report,
        incumbent_parity=incumbent_outputs["parity"],
        benchmark_expected=benchmark_expected,
        paper_manifest=paper_manifest,
        rerun_variance_report=rerun_variance_report,
    )
    dataset_leakage_audit = _build_dataset_leakage_audit(
        run_dir=run_dir,
        generated_at=generated_at,
        controls=controls,
        trace=trace,
    )
    benchmark_truth_audit = _build_benchmark_truth_audit(
        generated_at=generated_at,
        controls=controls,
        trace=trace,
        task_contract_bundle=task_contract_bundle,
        eval_bundle=eval_bundle,
        trace_bundle=trace_bundle,
        dataset_leakage_audit=dataset_leakage_audit,
        paper_table=paper_table,
    )
    paper_claim_guard_report = _build_paper_claim_guard_report(
        generated_at=generated_at,
        controls=controls,
        trace=trace,
        benchmark_truth_audit=benchmark_truth_audit,
        claims_report=benchmark_claims_report,
        paper_table=paper_table,
    )
    benchmark_release_gate = _build_benchmark_release_gate(
        generated_at=generated_at,
        controls=controls,
        trace=trace,
        benchmark_truth_audit=benchmark_truth_audit,
        paper_claim_guard_report=paper_claim_guard_report,
    )
    paper_manifest = replace(
        paper_manifest,
        status="ok" if benchmark_release_gate.safe_to_cite_publicly else "blocked",
        claim_gate_status=benchmark_release_gate.status,
        safe_to_cite_publicly=benchmark_release_gate.safe_to_cite_publicly,
        claim_gate_reason_codes=list(benchmark_release_gate.blocked_reason_codes),
    )
    paper_table = replace(
        paper_table,
        status=("ok" if benchmark_release_gate.safe_to_cite_publicly else "blocked") if paper_table.rows else "not_available",
        claim_gate_status=benchmark_release_gate.status,
        safe_to_cite_publicly=benchmark_release_gate.safe_to_cite_publicly,
        claim_gate_reason_codes=list(benchmark_release_gate.blocked_reason_codes),
    )
    shadow_trial_manifest, shadow_trial_scorecard, candidate_quarantine, promotion_readiness_report = (
        _build_shadow_trial_outputs(
            run_dir=run_dir,
            generated_at=generated_at,
            controls=controls,
            trace=trace,
            frame=frame,
            target_column=target_column,
            feature_columns=feature_columns,
            task_type=task_profile.task_type,
            data_mode=task_profile.data_mode,
            timestamp_column=timestamp_column,
            builder_handoff=builder_handoff,
            comparison_metric=comparison_metric,
            metric_direction=metric_direction,
            relaytic_reference=relaytic_reference,
            best_reference=best_reference,
            paper_manifest=paper_manifest,
            decision_bundle=decision_bundle,
            architecture_bundle=architecture_bundle,
        )
    )
    bundle = BenchmarkBundle(
        reference_approach_matrix=matrix,
        benchmark_gap_report=gap_report,
        benchmark_parity_report=parity_report,
        external_challenger_manifest=incumbent_outputs["manifest"],
        external_challenger_evaluation=incumbent_outputs["evaluation"],
        incumbent_parity_report=incumbent_outputs["parity"],
        beat_target_contract=incumbent_outputs["beat_target"],
        paper_benchmark_manifest=paper_manifest,
        paper_benchmark_table=paper_table,
        benchmark_ablation_matrix=ablation_matrix,
        rerun_variance_report=rerun_variance_report,
        benchmark_claims_report=benchmark_claims_report,
        shadow_trial_manifest=shadow_trial_manifest,
        shadow_trial_scorecard=shadow_trial_scorecard,
        candidate_quarantine=candidate_quarantine,
        promotion_readiness_report=promotion_readiness_report,
        benchmark_truth_audit=benchmark_truth_audit,
        paper_claim_guard_report=paper_claim_guard_report,
        benchmark_release_gate=benchmark_release_gate,
        dataset_leakage_audit=dataset_leakage_audit,
    )
    return BenchmarkRunResult(bundle=bundle, review_markdown=render_benchmark_review_markdown(bundle.to_dict()))


def _build_shadow_trial_outputs(
    *,
    run_dir: str | Path,
    generated_at: str,
    controls: BenchmarkControls,
    trace: BenchmarkTrace,
    frame: Any,
    target_column: str,
    feature_columns: list[str],
    task_type: str,
    data_mode: str,
    timestamp_column: str | None,
    builder_handoff: dict[str, Any],
    comparison_metric: str,
    metric_direction: str,
    relaytic_reference: dict[str, Any],
    best_reference: dict[str, Any] | None,
    paper_manifest: PaperBenchmarkManifest,
    decision_bundle: dict[str, Any],
    architecture_bundle: dict[str, Any],
) -> tuple[ShadowTrialManifest, ShadowTrialScorecard, CandidateQuarantine, PromotionReadinessReport]:
    method_import_report = dict(decision_bundle.get("method_import_report", {}))
    candidate_registry = dict(decision_bundle.get("architecture_candidate_registry", {}))
    imported_candidates = [
        dict(item)
        for item in candidate_registry.get("candidates", [])
        if isinstance(item, dict) and _clean_text(item.get("family_id"))
    ]
    baseline_family = _clean_text(relaytic_reference.get("model_family")) or _clean_text(paper_manifest.selected_model_family)
    baseline_metric_value = _metric_value(relaytic_reference.get("test_metric"), comparison_metric)
    best_reference_family = _clean_text(best_reference.get("model_family")) if isinstance(best_reference, dict) else None
    best_reference_metric_value = (
        _metric_value(best_reference.get("test_metric"), comparison_metric)
        if isinstance(best_reference, dict)
        else None
    )
    max_candidates = max(1, min(len(imported_candidates), controls.max_reference_models + 1))
    candidate_rows: list[dict[str, Any]] = []
    quarantined_rows: list[dict[str, Any]] = []
    promotion_rows: list[dict[str, Any]] = []
    for candidate in imported_candidates[:max_candidates]:
        family_id = _clean_text(candidate.get("family_id")) or "unknown"
        shadow_row = _run_imported_family_shadow_trial(
            run_dir=run_dir,
            frame=frame,
            target_column=target_column,
            feature_columns=feature_columns,
            task_type=task_type,
            data_mode=data_mode,
            timestamp_column=timestamp_column,
            builder_handoff=builder_handoff,
            comparison_metric=comparison_metric,
            metric_direction=metric_direction,
            baseline_family=baseline_family,
            baseline_metric_value=baseline_metric_value,
            best_reference_family=best_reference_family,
            best_reference_metric_value=best_reference_metric_value,
            paper_manifest=paper_manifest,
            method_import_report=method_import_report,
            architecture_bundle=architecture_bundle,
            candidate=candidate,
        )
        candidate_rows.append(shadow_row)
        promotion_rows.append(
            {
                "candidate_id": shadow_row["candidate_id"],
                "family_id": family_id,
                "promotion_state": shadow_row["promotion_state"],
                "shadow_outcome": shadow_row["shadow_outcome"],
                "candidate_metric_value": shadow_row.get("candidate_metric_value"),
                "baseline_metric_value": shadow_row.get("baseline_metric_value"),
                "reason_codes": list(shadow_row.get("reason_codes", [])),
                "summary": shadow_row.get("summary"),
            }
        )
        if shadow_row["promotion_state"] == "quarantined":
            quarantined_rows.append(
                {
                    "candidate_id": shadow_row["candidate_id"],
                    "family_id": family_id,
                    "reason_codes": list(shadow_row.get("reason_codes", [])),
                    "shadow_mode": shadow_row["shadow_mode"],
                    "summary": shadow_row.get("summary"),
                }
            )
    manifest = ShadowTrialManifest(
        schema_version=SHADOW_TRIAL_MANIFEST_SCHEMA_VERSION,
        generated_at=generated_at,
        controls=controls,
        status="ok" if candidate_rows else "no_candidates",
        candidate_count=len(imported_candidates),
        runnable_candidate_count=sum(1 for item in candidate_rows if bool(item.get("training_executed"))),
        replay_only_count=sum(1 for item in candidate_rows if str(item.get("shadow_mode")) == "offline_replay_only"),
        temporal_candidate_count=sum(
            1 for item in candidate_rows if bool(item.get("temporal_gate_required"))
        ),
        comparison_metric=comparison_metric,
        baseline_family=baseline_family,
        summary=(
            f"Relaytic reviewed {len(candidate_rows)} imported architecture candidate(s) under replay or shadow proof."
            if candidate_rows
            else "Relaytic had no imported architecture candidates to shadow-test."
        ),
        trace=trace,
    )
    scorecard = ShadowTrialScorecard(
        schema_version=SHADOW_TRIAL_SCORECARD_SCHEMA_VERSION,
        generated_at=generated_at,
        controls=controls,
        status="ok" if candidate_rows else "no_candidates",
        comparison_metric=comparison_metric,
        metric_direction=metric_direction,
        rows=candidate_rows,
        summary=(
            f"Relaytic recorded shadow-trial outcomes for {len(candidate_rows)} imported architecture candidate(s)."
            if candidate_rows
            else "Relaytic did not record shadow-trial scorecards because no imported architecture candidates were available."
        ),
        trace=trace,
    )
    quarantine = CandidateQuarantine(
        schema_version=CANDIDATE_QUARANTINE_SCHEMA_VERSION,
        generated_at=generated_at,
        controls=controls,
        status="ok" if candidate_rows else "no_candidates",
        quarantined_count=len(quarantined_rows),
        quarantined_candidates=quarantined_rows,
        summary=(
            f"Relaytic quarantined {len(quarantined_rows)} imported architecture candidate(s) after replay or shadow review."
            if candidate_rows
            else "Relaytic had no imported architecture candidates to quarantine."
        ),
        trace=trace,
    )
    promotion = PromotionReadinessReport(
        schema_version=PROMOTION_READINESS_REPORT_SCHEMA_VERSION,
        generated_at=generated_at,
        controls=controls,
        status="ok" if candidate_rows else "no_candidates",
        promotion_ready_count=sum(1 for item in promotion_rows if item.get("promotion_state") == "promotion_ready"),
        candidate_available_count=sum(1 for item in promotion_rows if item.get("promotion_state") == "candidate_available"),
        quarantined_count=len(quarantined_rows),
        rows=promotion_rows,
        summary=(
            f"Relaytic marked {sum(1 for item in promotion_rows if item.get('promotion_state') == 'promotion_ready')} imported family candidate(s) as promotion-ready."
            if candidate_rows
            else "Relaytic had no imported architecture candidates to review for promotion readiness."
        ),
        trace=trace,
    )
    return manifest, scorecard, quarantine, promotion


def _run_imported_family_shadow_trial(
    *,
    run_dir: str | Path,
    frame: Any,
    target_column: str,
    feature_columns: list[str],
    task_type: str,
    data_mode: str,
    timestamp_column: str | None,
    builder_handoff: dict[str, Any],
    comparison_metric: str,
    metric_direction: str,
    baseline_family: str | None,
    baseline_metric_value: float | None,
    best_reference_family: str | None,
    best_reference_metric_value: float | None,
    paper_manifest: PaperBenchmarkManifest,
    method_import_report: dict[str, Any],
    architecture_bundle: dict[str, Any],
    candidate: dict[str, Any],
) -> dict[str, Any]:
    family_id = _clean_text(candidate.get("family_id")) or "unknown"
    candidate_id = _clean_text(candidate.get("candidate_id")) or f"architecture_candidate::{family_id}"
    reason_codes: list[str] = []
    architecture_report = dict(architecture_bundle.get("architecture_router_report", {}))
    family_title = _clean_text(candidate.get("family_title")) or family_id
    if candidate.get("research_disposition") == "rejected":
        reason_codes.append("rejected_by_task_contract")
        return {
            "candidate_id": candidate_id,
            "family_id": family_id,
            "family_title": family_title,
            "shadow_mode": "task_contract_rejected",
            "training_executed": False,
            "temporal_gate_required": bool(candidate.get("temporal_gate_required")),
            "comparison_metric": comparison_metric,
            "metric_direction": metric_direction,
            "baseline_family": baseline_family,
            "baseline_metric_value": baseline_metric_value,
            "best_reference_family": best_reference_family,
            "best_reference_metric_value": best_reference_metric_value,
            "candidate_metric_value": None,
            "delta_vs_selected": None,
            "delta_vs_best_reference": None,
            "shadow_outcome": "rejected",
            "promotion_state": "quarantined",
            "reason_codes": reason_codes,
            "summary": "Relaytic kept this imported family quarantined because the current task contract already rejected it.",
        }
    if family_id in {"sequence_lstm_candidate", "temporal_transformer_candidate"}:
        reason_codes.extend(
            [
                "temporal_sequence_candidate",
                "lagged_baseline_required",
                "shadow_first_before_live",
            ]
        )
        if data_mode != "time_series":
            reason_codes.append("not_time_series")
        return {
            "candidate_id": candidate_id,
            "family_id": family_id,
            "family_title": family_title,
            "shadow_mode": "offline_replay_only",
            "training_executed": False,
            "temporal_gate_required": True,
            "comparison_metric": comparison_metric,
            "metric_direction": metric_direction,
            "baseline_family": _normalize_shadow_baseline_family(_clean_text(paper_manifest.lagged_baseline_family) or baseline_family),
            "baseline_metric_value": paper_manifest.lagged_baseline_metric,
            "best_reference_family": best_reference_family,
            "best_reference_metric_value": best_reference_metric_value,
            "candidate_metric_value": None,
            "delta_vs_selected": None,
            "delta_vs_best_reference": None,
            "shadow_outcome": "replay_only",
            "promotion_state": "quarantined",
            "reason_codes": reason_codes,
            "summary": (
                "Relaytic kept this temporal sequence candidate shadow-only until it proves value over lagged tabular baselines."
            ),
        }
    if not bool(candidate.get("training_support")) or _clean_text(candidate.get("availability_status")) != "available":
        reason_codes.append("adapter_unavailable")
        return {
            "candidate_id": candidate_id,
            "family_id": family_id,
            "family_title": family_title,
            "shadow_mode": "offline_replay_only",
            "training_executed": False,
            "temporal_gate_required": bool(candidate.get("temporal_gate_required")),
            "comparison_metric": comparison_metric,
            "metric_direction": metric_direction,
            "baseline_family": baseline_family,
            "baseline_metric_value": baseline_metric_value,
            "best_reference_family": best_reference_family,
            "best_reference_metric_value": best_reference_metric_value,
            "candidate_metric_value": None,
            "delta_vs_selected": None,
            "delta_vs_best_reference": None,
            "shadow_outcome": "blocked_unavailable",
            "promotion_state": "quarantined",
            "reason_codes": reason_codes,
            "summary": "Relaytic found research support for this family, but the required local adapter is not available.",
        }
    if family_id == baseline_family:
        reason_codes.append("already_live_family")
        return {
            "candidate_id": candidate_id,
            "family_id": family_id,
            "family_title": family_title,
            "shadow_mode": "current_route_replay",
            "training_executed": False,
            "temporal_gate_required": False,
            "comparison_metric": comparison_metric,
            "metric_direction": metric_direction,
            "baseline_family": baseline_family,
            "baseline_metric_value": baseline_metric_value,
            "best_reference_family": best_reference_family,
            "best_reference_metric_value": best_reference_metric_value,
            "candidate_metric_value": baseline_metric_value,
            "delta_vs_selected": 0.0,
            "delta_vs_best_reference": _metric_delta(
                candidate_value=baseline_metric_value,
                baseline_value=best_reference_metric_value,
                metric_direction=metric_direction,
            ),
            "shadow_outcome": "already_live",
            "promotion_state": "candidate_available",
            "reason_codes": reason_codes,
            "summary": "Relaytic already used this imported family live, so its current benchmark evidence makes it candidate-available.",
        }

    try:
        shadow_output_dir = Path(run_dir) / "shadow_trials" / _shadow_slug(family_id)
        training = train_surrogate_candidates(
            frame=frame,
            target_column=target_column,
            feature_columns=feature_columns,
            requested_model_family=family_id,
            timestamp_column=timestamp_column,
            normalize=bool(builder_handoff.get("normalize", True)),
            missing_data_strategy=str(builder_handoff.get("missing_data_strategy", "fill_median")),
            fill_constant_value=None,
            compare_against_baseline=False,
            lag_horizon_samples=_optional_int(builder_handoff.get("lag_horizon_samples")),
            threshold_policy=_clean_text(builder_handoff.get("threshold_policy")),
            decision_threshold=_optional_float(builder_handoff.get("decision_threshold")),
            task_type=task_type,
            selection_metric=comparison_metric,
            preferred_candidate_order=[family_id],
            output_run_dir=shadow_output_dir,
        )
    except Exception as exc:
        reason_codes.append("shadow_trial_failed")
        return {
            "candidate_id": candidate_id,
            "family_id": family_id,
            "family_title": family_title,
            "shadow_mode": "shadow_trial_failed",
            "training_executed": False,
            "temporal_gate_required": False,
            "comparison_metric": comparison_metric,
            "metric_direction": metric_direction,
            "baseline_family": baseline_family,
            "baseline_metric_value": baseline_metric_value,
            "best_reference_family": best_reference_family,
            "best_reference_metric_value": best_reference_metric_value,
            "candidate_metric_value": None,
            "delta_vs_selected": None,
            "delta_vs_best_reference": None,
            "shadow_outcome": "failed",
            "promotion_state": "quarantined",
            "reason_codes": reason_codes,
            "summary": f"Relaytic could not complete a same-split shadow trial for `{family_id}`: {type(exc).__name__}.",
        }

    candidate_metric_value = _metric_value(dict(training.get("selected_metrics", {})).get("test"), comparison_metric)
    delta_vs_selected = _metric_delta(
        candidate_value=candidate_metric_value,
        baseline_value=baseline_metric_value,
        metric_direction=metric_direction,
    )
    delta_vs_best_reference = _metric_delta(
        candidate_value=candidate_metric_value,
        baseline_value=best_reference_metric_value,
        metric_direction=metric_direction,
    )
    in_router_top = family_id in [
        str(item)
        for item in architecture_report.get("candidate_order", [])[:3]
        if str(item).strip()
    ]
    improved_selected = _metric_better(
        candidate_value=candidate_metric_value,
        baseline_value=baseline_metric_value,
        metric_direction=metric_direction,
        minimum_delta=0.0,
    )
    near_selected = _metric_near(
        candidate_value=candidate_metric_value,
        baseline_value=baseline_metric_value,
        metric_direction=metric_direction,
    )
    competitive_to_reference = (
        best_reference_metric_value is None
        or _metric_better(
            candidate_value=candidate_metric_value,
            baseline_value=best_reference_metric_value,
            metric_direction=metric_direction,
            minimum_delta=0.0,
        )
        or _metric_near(
            candidate_value=candidate_metric_value,
            baseline_value=best_reference_metric_value,
            metric_direction=metric_direction,
        )
    )
    if improved_selected and competitive_to_reference and candidate.get("research_disposition") == "accepted":
        promotion_state = "promotion_ready"
        shadow_outcome = "stronger_than_current"
        reason_codes.extend(["beats_selected_route", "research_supported", "same_split_shadow_pass"])
    elif (improved_selected or near_selected or in_router_top) and candidate.get("research_disposition") in {"accepted", "advisory"}:
        promotion_state = "candidate_available"
        shadow_outcome = "promising"
        reason_codes.extend(["near_selected_route", "shadow_signal_positive"])
    else:
        promotion_state = "quarantined"
        shadow_outcome = "underperforming"
        reason_codes.extend(["shadow_signal_weak"])
    return {
        "candidate_id": candidate_id,
        "family_id": family_id,
        "family_title": family_title,
        "shadow_mode": "same_split_shadow_trial",
        "training_executed": True,
        "temporal_gate_required": False,
        "comparison_metric": comparison_metric,
        "metric_direction": metric_direction,
        "baseline_family": baseline_family,
        "baseline_metric_value": baseline_metric_value,
        "best_reference_family": best_reference_family,
        "best_reference_metric_value": best_reference_metric_value,
        "candidate_metric_value": candidate_metric_value,
        "delta_vs_selected": delta_vs_selected,
        "delta_vs_best_reference": delta_vs_best_reference,
        "shadow_outcome": shadow_outcome,
        "promotion_state": promotion_state,
        "reason_codes": reason_codes,
        "summary": (
            f"Relaytic shadow-tested `{family_id}` against `{baseline_family or 'current_route'}` under the same split and metric contract."
        ),
    }


def _build_paper_benchmark_manifest(
    *,
    run_dir: str | Path,
    data_path: str,
    generated_at: str,
    controls: BenchmarkControls,
    trace: BenchmarkTrace,
    context_bundle: dict[str, Any],
    planning_bundle: dict[str, Any],
    task_profile: Any,
    comparison_metric: str,
    metric_direction: str,
    relaytic_reference: dict[str, Any],
    reference_rows: list[dict[str, Any]],
    execution_summary: dict[str, Any],
    benchmark_expected: bool,
) -> PaperBenchmarkManifest:
    root = Path(run_dir)
    data_origin = _bundle_item(context_bundle, "data_origin")
    dataset_profile = _read_json_artifact(root / "dataset_profile.json")
    architecture_router_report = _read_json_artifact(root / "architecture_router_report.json")
    lagged_reference = _find_lagged_reference(reference_rows=reference_rows)
    frame = _read_frame_or_empty(data_path)
    horizon_type = _temporal_horizon_type(task_type=task_profile.task_type, data_mode=task_profile.data_mode)
    timestamp_cadence_quality = None
    if task_profile.data_mode == "time_series":
        timestamp_cadence_quality = (
            "timestamp_column_present"
            if _clean_text(dataset_profile.get("timestamp_column"))
            else "timestamp_not_materialized"
        )
    selected_hyperparameters = dict(execution_summary.get("selected_hyperparameters") or {})
    if task_profile.data_mode == "time_series":
        if architecture_router_report.get("sequence_shadow_ready"):
            sequence_candidate_status = "shadow_ready"
            sequence_candidate_reason = (
                "Relaytic detected ordered temporal structure and keeps sequence-native families in shadow-only posture "
                "until later promotion slices prove they beat lagged/tabular baselines."
            )
        else:
            sequence_candidate_status = "not_live"
            sequence_candidate_reason = (
                _clean_text(architecture_router_report.get("sequence_rejection_reason"))
                or "Relaytic did not find enough temporal evidence to justify sequence-family evaluation."
            )
    else:
        sequence_candidate_status = "not_applicable"
        sequence_candidate_reason = "Relaytic kept sequence-native families out of static-table benchmark claims."

    return PaperBenchmarkManifest(
        schema_version=PAPER_BENCHMARK_MANIFEST_SCHEMA_VERSION,
        generated_at=generated_at,
        controls=controls,
        status="ok",
        dataset_label=Path(data_path).stem,
        dataset_source_name=_clean_text(data_origin.get("source_name")) or Path(data_path).name,
        dataset_source_type=_clean_text(data_origin.get("source_type")) or "local_snapshot",
        source_url=_clean_text(data_origin.get("source_url")),
        data_path=str(data_path),
        task_type=task_profile.task_type,
        data_mode=task_profile.data_mode,
        target_column=str(planning_bundle.get("plan", {}).get("target_column") or ""),
        row_count=int(len(frame)),
        column_count=int(len(frame.columns)),
        comparison_metric=comparison_metric,
        metric_direction=metric_direction,
        selected_model_family=_clean_text(relaytic_reference.get("model_family")),
        selected_hyperparameters=selected_hyperparameters,
        benchmark_expected=benchmark_expected,
        horizon_type=horizon_type,
        timestamp_cadence_quality=timestamp_cadence_quality,
        lagged_baseline_family=_clean_text(lagged_reference.get("model_family")) if lagged_reference else None,
        lagged_baseline_metric=_metric_value(lagged_reference.get("test_metric"), comparison_metric) if lagged_reference else None,
        sequence_candidate_status=sequence_candidate_status,
        sequence_candidate_reason=sequence_candidate_reason,
        summary=(
            f"Relaytic recorded a paper-facing benchmark manifest for `{Path(data_path).stem}` with selected family "
            f"`{_clean_text(relaytic_reference.get('model_family')) or 'unknown'}` on `{comparison_metric}`."
        ),
        trace=trace,
    )


def _build_paper_benchmark_table(
    *,
    generated_at: str,
    controls: BenchmarkControls,
    trace: BenchmarkTrace,
    ranking: list[dict[str, Any]],
    comparison_metric: str,
    metric_direction: str,
    relaytic_rank: int | None,
) -> PaperBenchmarkTable:
    rows = [
        {
            "rank": index + 1,
            "role": _clean_text(item.get("role")) or "unknown",
            "model_family": _clean_text(item.get("model_family")) or "unknown",
            "validation_metric": item.get("validation_metric"),
            "test_metric": item.get("test_metric"),
            "selected": bool(item.get("role") == "relaytic"),
        }
        for index, item in enumerate(ranking)
    ]
    return PaperBenchmarkTable(
        schema_version=PAPER_BENCHMARK_TABLE_SCHEMA_VERSION,
        generated_at=generated_at,
        controls=controls,
        status="ok" if rows else "not_available",
        comparison_metric=comparison_metric,
        metric_direction=metric_direction,
        relaytic_rank=relaytic_rank,
        reference_count=sum(1 for row in rows if row["role"] == "reference"),
        rows=rows,
        summary=(
            f"Relaytic rendered a benchmark table with `{len(rows)}` ranked rows and current relaytic rank `{relaytic_rank}`."
            if rows
            else "Relaytic could not build a paper benchmark table because no ranked rows were available."
        ),
        trace=trace,
    )


def _build_benchmark_ablation_matrix(
    *,
    run_dir: str | Path,
    generated_at: str,
    controls: BenchmarkControls,
    trace: BenchmarkTrace,
    comparison_metric: str,
    metric_direction: str,
    relaytic_reference: dict[str, Any],
    reference_rows: list[dict[str, Any]],
    task_type: str,
    selected_model_family: str | None,
    data_mode: str,
) -> BenchmarkAblationMatrix:
    root = Path(run_dir)
    ledger = _read_jsonl_artifact(root / "trial_ledger.jsonl")
    rows: list[dict[str, Any]] = []
    selected_metric = _metric_value(relaytic_reference.get("test_metric"), comparison_metric)
    if selected_model_family:
        selected_trial = next(
            (
                item for item in ledger
                if _clean_text(item.get("family")) == selected_model_family
                and _clean_text(item.get("variant_id")) == _clean_text(relaytic_reference.get("variant_id"))
            ),
            None,
        )
        if selected_trial is None:
            selected_trial = _best_trial_for_family(ledger=ledger, family=selected_model_family, comparison_metric=comparison_metric, metric_direction=metric_direction)
        if selected_trial:
            rows.append(
                _ablation_row(
                    ablation_id="selected_route",
                    label="Selected Relaytic route",
                    role="selected_route",
                    comparison_metric=comparison_metric,
                    test_metric=_metric_value(selected_trial.get("test_metrics"), comparison_metric),
                    validation_metric=_metric_value(selected_trial.get("validation_metrics"), comparison_metric),
                    model_family=selected_model_family,
                    variant_id=_clean_text(selected_trial.get("variant_id")),
                    selected_metric=selected_metric,
                )
            )
        anchor_trial = next(
            (
                item for item in ledger
                if _clean_text(item.get("family")) == selected_model_family
                and "anchor" in str(item.get("variant_id", ""))
            ),
            None,
        )
        if anchor_trial:
            rows.append(
                _ablation_row(
                    ablation_id="selected_anchor",
                    label="Default anchor for selected family",
                    role="default_anchor",
                    comparison_metric=comparison_metric,
                    test_metric=_metric_value(anchor_trial.get("test_metrics"), comparison_metric),
                    validation_metric=_metric_value(anchor_trial.get("validation_metrics"), comparison_metric),
                    model_family=selected_model_family,
                    variant_id=_clean_text(anchor_trial.get("variant_id")),
                    selected_metric=selected_metric,
                )
            )
    baseline_family = "sklearn_logistic_regression" if is_classification_task(task_type) else "sklearn_ridge"
    baseline_reference = next((item for item in reference_rows if _clean_text(item.get("model_family")) == baseline_family), None)
    if baseline_reference:
        rows.append(
            _ablation_row(
                ablation_id="ordinary_baseline_reference",
                label="Ordinary baseline reference",
                role="baseline_reference",
                comparison_metric=comparison_metric,
                test_metric=_metric_value(baseline_reference.get("test_metric"), comparison_metric),
                validation_metric=_metric_value(baseline_reference.get("validation_metric"), comparison_metric),
                model_family=_clean_text(baseline_reference.get("model_family")),
                variant_id=None,
                selected_metric=selected_metric,
            )
        )
    best_reference = _best_reference_row(reference_rows=reference_rows, comparison_metric=comparison_metric, metric_direction=metric_direction)
    if best_reference:
        rows.append(
            _ablation_row(
                ablation_id="best_reference",
                label="Best same-contract reference",
                role="best_reference",
                comparison_metric=comparison_metric,
                test_metric=_metric_value(best_reference.get("test_metric"), comparison_metric),
                validation_metric=_metric_value(best_reference.get("validation_metric"), comparison_metric),
                model_family=_clean_text(best_reference.get("model_family")),
                variant_id=None,
                selected_metric=selected_metric,
            )
        )
    if data_mode == "time_series":
        lagged_reference = _find_lagged_reference(reference_rows=reference_rows)
        if lagged_reference:
            rows.append(
                _ablation_row(
                    ablation_id="lagged_baseline_reference",
                    label="Lagged temporal baseline",
                    role="lagged_reference",
                    comparison_metric=comparison_metric,
                    test_metric=_metric_value(lagged_reference.get("test_metric"), comparison_metric),
                    validation_metric=_metric_value(lagged_reference.get("validation_metric"), comparison_metric),
                    model_family=_clean_text(lagged_reference.get("model_family")),
                    variant_id=None,
                    selected_metric=selected_metric,
                )
            )
    return BenchmarkAblationMatrix(
        schema_version=BENCHMARK_ABLATION_MATRIX_SCHEMA_VERSION,
        generated_at=generated_at,
        controls=controls,
        status="ok" if rows else "not_available",
        comparison_metric=comparison_metric,
        metric_direction=metric_direction,
        rows=rows,
        summary=(
            f"Relaytic materialized `{len(rows)}` benchmark ablation row(s), including the selected route, baseline references, and available HPO anchor comparisons."
            if rows
            else "Relaytic could not build a benchmark ablation matrix for this run."
        ),
        trace=trace,
    )


def _build_rerun_variance_report(
    *,
    run_dir: str | Path,
    generated_at: str,
    controls: BenchmarkControls,
    trace: BenchmarkTrace,
    comparison_metric: str,
    metric_direction: str,
    relaytic_reference: dict[str, Any],
    task_type: str,
    target_column: str,
    data_mode: str,
    row_count: int,
    column_count: int,
) -> RerunVarianceReport:
    current_metric = _metric_value(relaytic_reference.get("test_metric"), comparison_metric)
    current_run_id = Path(run_dir).name
    rows = [(current_run_id, current_metric)] if current_metric is not None else []
    rows.extend(
        _discover_matching_benchmark_runs(
            current_run_dir=Path(run_dir),
            comparison_metric=comparison_metric,
            task_type=task_type,
            target_column=target_column,
            data_mode=data_mode,
            row_count=row_count,
            column_count=column_count,
        )
    )
    deduped: list[tuple[str, float]] = []
    seen_ids: set[str] = set()
    for run_id, metric_value in rows:
        if run_id in seen_ids:
            continue
        seen_ids.add(run_id)
        deduped.append((run_id, metric_value))
    values = [float(value) for _, value in deduped]
    if len(values) <= 1:
        stability_band = "single_run_only"
        status = "single_run_only"
        stddev_value = None
        mean_value = values[0] if values else None
        min_value = values[0] if values else None
        max_value = values[0] if values else None
        cv = None
    else:
        mean_value = float(fmean(values))
        stddev_value = float(pstdev(values))
        min_value = min(values)
        max_value = max(values)
        cv = abs(stddev_value / mean_value) if abs(mean_value) > 1e-12 else None
        spread = abs(max_value - min_value)
        if spread <= 0.01 or (cv is not None and cv <= 0.01):
            stability_band = "stable"
        elif spread <= 0.03 or (cv is not None and cv <= 0.05):
            stability_band = "moderate_variance"
        else:
            stability_band = "volatile"
        status = "ok"
    return RerunVarianceReport(
        schema_version=RERUN_VARIANCE_REPORT_SCHEMA_VERSION,
        generated_at=generated_at,
        controls=controls,
        status=status,
        comparison_metric=comparison_metric,
        metric_direction=metric_direction,
        matching_run_count=len(deduped),
        run_ids=[run_id for run_id, _ in deduped],
        metric_values=values,
        mean_metric_value=mean_value,
        min_metric_value=min_value,
        max_metric_value=max_value,
        stddev_metric_value=stddev_value,
        coefficient_of_variation=cv,
        stability_band=stability_band,
        summary=(
            f"Relaytic compared `{len(deduped)}` matching benchmarked run(s) and classified rerun stability as `{stability_band}`."
            if deduped
            else "Relaytic could not find any benchmarked runs to measure rerun variance."
        ),
        trace=trace,
    )


def _build_benchmark_claims_report(
    *,
    run_dir: str | Path,
    generated_at: str,
    controls: BenchmarkControls,
    trace: BenchmarkTrace,
    parity_report: BenchmarkParityReport,
    gap_report: BenchmarkGapReport,
    incumbent_parity: IncumbentParityReport,
    benchmark_expected: bool,
    paper_manifest: PaperBenchmarkManifest,
    rerun_variance_report: RerunVarianceReport,
) -> BenchmarkClaimsReport:
    root = Path(run_dir)
    benchmark_vs_deploy_report = _read_json_artifact(root / "benchmark_vs_deploy_report.json")
    deployment_readiness_report = _read_json_artifact(root / "deployment_readiness_report.json")
    parity_status = _clean_text(parity_report.parity_status) or "unknown"
    if parity_status == "meets_or_exceeds_reference":
        competitiveness_claim = "competitive_against_current_same_contract_reference_set"
    elif parity_status == "near_parity":
        competitiveness_claim = "near_parity_against_current_same_contract_reference_set"
    elif parity_status == "below_reference":
        competitiveness_claim = "below_reference_on_current_same_contract_reference_set"
    else:
        competitiveness_claim = "reference_claim_not_available"
    deployment_claim = (
        _clean_text(benchmark_vs_deploy_report.get("deployment_readiness"))
        or _clean_text(deployment_readiness_report.get("readiness_state"))
        or "unknown"
    )
    below_reference = parity_status == "below_reference"
    split_detected = bool(benchmark_vs_deploy_report.get("split_detected"))
    claim_boundaries = [
        "same-contract local benchmark comparison only",
        "benchmark competitiveness and deployment readiness are reported separately",
        "results reflect the current local reference set rather than a universal leaderboard",
    ]
    if benchmark_expected:
        claim_boundaries.append("benchmarking was explicitly requested or inferred for this run posture")
    if paper_manifest.data_mode == "time_series":
        claim_boundaries.append("sequence-native families remain shadow-only unless temporal evidence justifies promotion")
    weak_spots: list[str] = []
    if below_reference:
        weak_spots.append(gap_report.summary)
    if rerun_variance_report.stability_band == "volatile":
        weak_spots.append("rerun variance is still volatile across matching benchmarked runs")
    if incumbent_parity.incumbent_stronger:
        weak_spots.append("an incumbent or external challenger is currently stronger than Relaytic on the comparison metric")
    not_claiming = [
        "global state-of-the-art performance across tabular machine learning",
        "automatic deployment readiness from benchmark wins alone",
    ]
    if paper_manifest.data_mode == "time_series":
        not_claiming.append("live sequence-model superiority over lagged tabular baselines")
    summary = (
        f"Relaytic currently claims `{competitiveness_claim}` with deployment claim `{deployment_claim}`."
    )
    return BenchmarkClaimsReport(
        schema_version=BENCHMARK_CLAIMS_REPORT_SCHEMA_VERSION,
        generated_at=generated_at,
        controls=controls,
        status="ok",
        competitiveness_claim=competitiveness_claim,
        deployment_claim=deployment_claim,
        below_reference=below_reference,
        benchmark_vs_deploy_split=split_detected,
        claim_boundaries=claim_boundaries,
        weak_spots=weak_spots,
        not_claiming=not_claiming,
        why_below_reference=gap_report.summary if below_reference else None,
        temporal_posture={
            "horizon_type": paper_manifest.horizon_type,
            "lagged_baseline_family": paper_manifest.lagged_baseline_family,
            "sequence_candidate_status": paper_manifest.sequence_candidate_status,
            "sequence_candidate_reason": paper_manifest.sequence_candidate_reason,
        },
        summary=summary,
        trace=trace,
    )


def _ensure_eval_bundle(*, run_dir: str | Path, policy: dict[str, Any] | None) -> dict[str, Any]:
    root = Path(run_dir)
    bundle = read_eval_bundle(root)
    if bundle and isinstance(bundle.get("agent_eval_matrix"), dict) and bundle.get("agent_eval_matrix"):
        return bundle
    eval_result = run_agent_evals(run_dir=root, policy=policy)
    write_eval_bundle(root, bundle=eval_result.bundle)
    return eval_result.bundle.to_dict()


def _build_dataset_leakage_audit(
    *,
    run_dir: str | Path,
    generated_at: str,
    controls: BenchmarkControls,
    trace: BenchmarkTrace,
) -> DatasetLeakageAudit:
    dataset_profile = _read_json_artifact(Path(run_dir) / "dataset_profile.json")
    leakage_risk_level = _clean_text(dataset_profile.get("leakage_risk_level")) or "unknown"
    raw_findings = [
        dict(item)
        for item in dataset_profile.get("leakage_risks", [])
        if isinstance(item, dict)
    ]
    findings = [
        {
            "kind": _clean_text(item.get("kind")) or "unknown",
            "column": _clean_text(item.get("column")),
            "severity": _clean_text(item.get("severity")) or "unknown",
            "reason": _clean_text(item.get("reason")) or "no detail",
        }
        for item in raw_findings[:8]
    ]
    blocked_findings = [item for item in findings if _clean_text(item.get("severity")) == "high"]
    warning_findings = [item for item in findings if _clean_text(item.get("severity")) == "medium"]
    blocked_reason_codes = sorted(
        {
            f"dataset_leakage_{_clean_text(item.get('kind')) or 'risk'}"
            for item in blocked_findings
        }
    )
    if leakage_risk_level == "high" and "dataset_leakage_high_risk_profile" not in blocked_reason_codes:
        blocked_reason_codes.append("dataset_leakage_high_risk_profile")
    if blocked_reason_codes:
        status = "blocked"
    elif warning_findings or leakage_risk_level == "medium":
        status = "warning"
    else:
        status = "ok"
    return DatasetLeakageAudit(
        schema_version=DATASET_LEAKAGE_AUDIT_SCHEMA_VERSION,
        generated_at=generated_at,
        controls=controls,
        status=status,
        leakage_risk_level=leakage_risk_level,
        blocked_finding_count=len(blocked_findings),
        warning_finding_count=len(warning_findings),
        blocked_reason_codes=blocked_reason_codes,
        findings=findings,
        summary=(
            "Relaytic did not detect blocking leakage findings for paper-facing benchmark claims."
            if status == "ok"
            else (
                "Relaytic found medium-severity leakage warnings that should stay visible in benchmark interpretation."
                if status == "warning"
                else "Relaytic blocked paper-facing benchmark claims because unresolved leakage findings remain."
            )
        ),
        trace=trace,
    )


def _build_benchmark_truth_audit(
    *,
    generated_at: str,
    controls: BenchmarkControls,
    trace: BenchmarkTrace,
    task_contract_bundle: dict[str, Any],
    eval_bundle: dict[str, Any],
    trace_bundle: dict[str, Any],
    dataset_leakage_audit: DatasetLeakageAudit,
    paper_table: PaperBenchmarkTable,
) -> BenchmarkTruthAudit:
    benchmark_truth_precheck = dict(task_contract_bundle.get("benchmark_truth_precheck", {}))
    trace_identity_conformance = dict(eval_bundle.get("trace_identity_conformance", {}))
    eval_surface_parity_report = dict(eval_bundle.get("eval_surface_parity_report", {}))
    protocol_conformance_report = dict(eval_bundle.get("protocol_conformance_report", {}))
    security_eval_report = dict(eval_bundle.get("security_eval_report", {}))
    blocked_reason_codes = [
        str(item).strip()
        for item in benchmark_truth_precheck.get("reason_codes", [])
        if str(item).strip()
    ]
    if _clean_text(protocol_conformance_report.get("status")) == "fail":
        blocked_reason_codes.append("protocol_conformance_failed")
    if _clean_text(security_eval_report.get("status")) == "fail":
        blocked_reason_codes.append("security_eval_failed")
    if _clean_text(trace_identity_conformance.get("status")) == "fail":
        blocked_reason_codes.append("trace_identity_drift")
    if _clean_text(eval_surface_parity_report.get("status")) == "fail":
        blocked_reason_codes.append("eval_surface_parity_failed")
    if dataset_leakage_audit.status == "blocked":
        blocked_reason_codes.extend(dataset_leakage_audit.blocked_reason_codes)
    adjudication = dict(trace_bundle.get("adjudication_scorecard", {}))
    if not _clean_text(adjudication.get("winning_claim_id")):
        blocked_reason_codes.append("trace_winner_missing")
    if not list(paper_table.rows):
        blocked_reason_codes.append("paper_benchmark_rows_unavailable")
    deduped_reason_codes = list(dict.fromkeys(blocked_reason_codes))
    safe_to_cite_publicly = not deduped_reason_codes
    return BenchmarkTruthAudit(
        schema_version=BENCHMARK_TRUTH_AUDIT_SCHEMA_VERSION,
        generated_at=generated_at,
        controls=controls,
        status="ok" if safe_to_cite_publicly else "blocked",
        safe_to_cite_publicly=safe_to_cite_publicly,
        truth_precheck_status=_clean_text(benchmark_truth_precheck.get("status")),
        protocol_status=_clean_text(protocol_conformance_report.get("status")),
        security_status=_clean_text(security_eval_report.get("status")),
        trace_identity_status=_clean_text(trace_identity_conformance.get("status")),
        eval_surface_parity_status=_clean_text(eval_surface_parity_report.get("status")),
        leakage_status=dataset_leakage_audit.status,
        blocked_reason_codes=deduped_reason_codes,
        summary=(
            "Relaytic considers the current benchmark bundle truthful enough for paper-facing claims."
            if safe_to_cite_publicly
            else "Relaytic blocked paper-facing claims because one or more benchmark-truth gates failed."
        ),
        trace=trace,
    )


def _build_paper_claim_guard_report(
    *,
    generated_at: str,
    controls: BenchmarkControls,
    trace: BenchmarkTrace,
    benchmark_truth_audit: BenchmarkTruthAudit,
    claims_report: BenchmarkClaimsReport,
    paper_table: PaperBenchmarkTable,
) -> PaperClaimGuardReport:
    blocked_reason_codes = list(benchmark_truth_audit.blocked_reason_codes)
    if not paper_table.rows and "paper_benchmark_rows_unavailable" not in blocked_reason_codes:
        blocked_reason_codes.append("paper_benchmark_rows_unavailable")
    required_fixes = [_required_fix_for_reason(code) for code in blocked_reason_codes]
    safe_to_cite_publicly = benchmark_truth_audit.safe_to_cite_publicly and bool(paper_table.rows)
    return PaperClaimGuardReport(
        schema_version=PAPER_CLAIM_GUARD_REPORT_SCHEMA_VERSION,
        generated_at=generated_at,
        controls=controls,
        status="safe_to_cite_publicly" if safe_to_cite_publicly else "blocked",
        safe_to_cite_publicly=safe_to_cite_publicly,
        blocked_reason_codes=blocked_reason_codes,
        claim_boundaries=list(claims_report.claim_boundaries),
        required_fixes=required_fixes,
        summary=(
            "Relaytic marked this benchmark bundle safe to cite publicly within the stated claim boundaries."
            if safe_to_cite_publicly
            else "Relaytic blocked public benchmark claims and recorded the concrete fixes required before citation."
        ),
        trace=trace,
    )


def _build_benchmark_release_gate(
    *,
    generated_at: str,
    controls: BenchmarkControls,
    trace: BenchmarkTrace,
    benchmark_truth_audit: BenchmarkTruthAudit,
    paper_claim_guard_report: PaperClaimGuardReport,
) -> BenchmarkReleaseGate:
    demo_safe = (
        _clean_text(benchmark_truth_audit.protocol_status) != "fail"
        and _clean_text(benchmark_truth_audit.security_status) != "fail"
        and _clean_text(benchmark_truth_audit.trace_identity_status) != "fail"
    )
    safe_to_cite_publicly = paper_claim_guard_report.safe_to_cite_publicly
    if safe_to_cite_publicly:
        status = "safe_to_cite_publicly"
    elif demo_safe:
        status = "demo_only"
    else:
        status = "blocked"
    return BenchmarkReleaseGate(
        schema_version=BENCHMARK_RELEASE_GATE_SCHEMA_VERSION,
        generated_at=generated_at,
        controls=controls,
        status=status,
        safe_to_cite_publicly=safe_to_cite_publicly,
        demo_safe=demo_safe,
        blocked_reason_codes=list(paper_claim_guard_report.blocked_reason_codes),
        required_fixes=list(paper_claim_guard_report.required_fixes),
        summary=(
            "Relaytic marked this benchmark bundle safe to cite publicly."
            if safe_to_cite_publicly
            else (
                "Relaytic marked this benchmark bundle demo-safe but not paper-safe."
                if demo_safe
                else "Relaytic blocked this benchmark bundle from public claim and demo release."
            )
        ),
        trace=trace,
    )


def _required_fix_for_reason(reason_code: str) -> str:
    mapping = {
        "benchmark_metric_missing_in_execution": "materialize the benchmark comparison metric in the executed model metrics",
        "benchmark_metric_missing_in_reference_rows": "materialize the benchmark comparison metric in the benchmark reference rows",
        "temporal_fold_health_blocked": "fix temporal split degeneracy before benchmarking",
        "protocol_conformance_failed": "repair CLI/MCP protocol drift and rerun evals",
        "security_eval_failed": "resolve open security findings before public claims",
        "trace_identity_drift": "repair adjudication winner drift across trace surfaces",
        "eval_surface_parity_failed": "realign eval surface parity before citing results",
        "dataset_leakage_high_risk_profile": "remove or neutralize high-risk leakage features",
        "trace_winner_missing": "materialize a valid adjudication winner before citing benchmark results",
        "paper_benchmark_rows_unavailable": "rerun benchmark review until paper table rows are available",
    }
    if reason_code.startswith("dataset_leakage_"):
        return "remove or neutralize unresolved leakage findings before public claim"
    return mapping.get(reason_code, "resolve the blocking benchmark-truth finding")


def render_benchmark_review_markdown(bundle: BenchmarkBundle | dict[str, Any]) -> str:
    payload = bundle.to_dict() if isinstance(bundle, BenchmarkBundle) else dict(bundle)
    matrix = dict(payload.get("reference_approach_matrix", {}))
    gap = dict(payload.get("benchmark_gap_report", {}))
    parity = dict(payload.get("benchmark_parity_report", {}))
    incumbent = dict(payload.get("incumbent_parity_report", {}))
    beat_target = dict(payload.get("beat_target_contract", {}))
    paper_manifest = dict(payload.get("paper_benchmark_manifest", {}))
    rerun_variance = dict(payload.get("rerun_variance_report", {}))
    claims = dict(payload.get("benchmark_claims_report", {}))
    truth_audit = dict(payload.get("benchmark_truth_audit", {}))
    claim_guard = dict(payload.get("paper_claim_guard_report", {}))
    release_gate = dict(payload.get("benchmark_release_gate", {}))
    leakage_audit = dict(payload.get("dataset_leakage_audit", {}))
    shadow_manifest = dict(payload.get("shadow_trial_manifest", {}))
    shadow_scorecard = dict(payload.get("shadow_trial_scorecard", {}))
    promotion = dict(payload.get("promotion_readiness_report", {}))
    quarantine = dict(payload.get("candidate_quarantine", {}))
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
    if paper_manifest:
        lines.extend(
            [
                "",
                "## Paper Surface",
                f"- Dataset: `{paper_manifest.get('dataset_label') or 'unknown'}`",
                f"- Task type: `{paper_manifest.get('task_type') or 'unknown'}`",
                f"- Selected family: `{paper_manifest.get('selected_model_family') or 'unknown'}`",
                f"- Horizon type: `{paper_manifest.get('horizon_type') or 'n/a'}`",
                f"- Sequence candidate status: `{paper_manifest.get('sequence_candidate_status') or 'n/a'}`",
                f"- Claim gate status: `{paper_manifest.get('claim_gate_status') or release_gate.get('status') or 'unknown'}`",
                f"- Safe to cite publicly: `{paper_manifest.get('safe_to_cite_publicly')}`",
            ]
        )
    if truth_audit or claim_guard or release_gate:
        lines.extend(
            [
                "",
                "## Claim Gate",
                f"- Truth audit: `{truth_audit.get('status') or 'unknown'}`",
                f"- Release gate: `{release_gate.get('status') or claim_guard.get('status') or 'unknown'}`",
                f"- Demo safe: `{release_gate.get('demo_safe')}`",
                f"- Safe to cite publicly: `{claim_guard.get('safe_to_cite_publicly')}`",
            ]
        )
        blocked_reasons = [
            str(item)
            for item in claim_guard.get("blocked_reason_codes", [])
            if str(item).strip()
        ]
        if blocked_reasons:
            lines.append(f"- Blocked reasons: `{', '.join(blocked_reasons[:6])}`")
    if leakage_audit:
        lines.extend(
            [
                "",
                "## Leakage",
                f"- Leakage status: `{leakage_audit.get('status') or 'unknown'}`",
                f"- Leakage risk level: `{leakage_audit.get('leakage_risk_level') or 'unknown'}`",
            ]
        )
    if rerun_variance:
        lines.extend(
            [
                "",
                "## Rerun Variance",
                f"- Matching run count: `{rerun_variance.get('matching_run_count')}`",
                f"- Stability band: `{rerun_variance.get('stability_band')}`",
                f"- Mean metric value: `{rerun_variance.get('mean_metric_value')}`",
            ]
        )
    if claims:
        lines.extend(
            [
                "",
                "## Claim Boundary",
                f"- Competitiveness claim: `{claims.get('competitiveness_claim')}`",
                f"- Deployment claim: `{claims.get('deployment_claim')}`",
                f"- Below reference: `{claims.get('below_reference')}`",
            ]
        )
    if shadow_manifest or promotion:
        lines.extend(
            [
                "",
                "## Imported Architecture Trials",
                f"- Imported candidates: `{shadow_manifest.get('candidate_count', 0)}`",
                f"- Runnable shadow trials: `{shadow_manifest.get('runnable_candidate_count', 0)}`",
                f"- Promotion-ready: `{promotion.get('promotion_ready_count', 0)}`",
                f"- Candidate-available: `{promotion.get('candidate_available_count', 0)}`",
                f"- Quarantined: `{quarantine.get('quarantined_count', 0)}`",
            ]
        )
    shadow_rows = list(shadow_scorecard.get("rows", []))
    if shadow_rows:
        lines.extend(["", "## Shadow Scorecard"])
        for item in shadow_rows[:4]:
            lines.append(
                f"- `{item.get('family_id')}` outcome=`{item.get('shadow_outcome')}` "
                f"promotion=`{item.get('promotion_state')}` metric=`{item.get('candidate_metric_value')}`"
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
    data_mode: str,
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
                data_mode=data_mode,
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
    data_mode: str,
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
        "train_metric": _materialize_temporal_metric_aliases(
            metrics=regression_metrics(y_true=train_y, y_pred=train_pred).to_dict(),
            data_mode=data_mode,
        ),
        "validation_metric": _materialize_temporal_metric_aliases(
            metrics=regression_metrics(y_true=validation_y, y_pred=validation_pred).to_dict(),
            data_mode=data_mode,
        ),
        "test_metric": _materialize_temporal_metric_aliases(
            metrics=regression_metrics(y_true=test_y, y_pred=test_pred).to_dict(),
            data_mode=data_mode,
        ),
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
    data_mode: str,
) -> dict[str, Any]:
    selected_metrics = dict(execution_summary.get("selected_metrics") or {})
    return {
        "role": "relaytic",
        "model_family": _clean_text(execution_summary.get("selected_model_family")),
        "comparison_metric": comparison_metric,
        "metric_direction": metric_direction,
        "train_metric": _materialize_temporal_metric_aliases(
            metrics=dict(selected_metrics.get("train") or {}),
            data_mode=data_mode,
        ),
        "validation_metric": _materialize_temporal_metric_aliases(
            metrics=dict(selected_metrics.get("validation") or {}),
            data_mode=data_mode,
        ),
        "test_metric": _materialize_temporal_metric_aliases(
            metrics=dict(selected_metrics.get("test") or {}),
            data_mode=data_mode,
        ),
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
    if lowered in {
        "mae",
        "rmse",
        "mape",
        "log_loss",
        "brier_score",
        "expected_calibration_error",
        "stability_adjusted_mae",
        "mae_per_latency",
    }:
        return "lower_is_better"
    return "higher_is_better"


def _metric_value(metrics: dict[str, Any], metric: str) -> float | None:
    value = metrics.get(metric)
    if value is None:
        alias = _metric_alias(metric)
        value = metrics.get(alias)
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _metric_alias(metric: str) -> str:
    normalized = str(metric or "").strip().lower()
    return {
        "stability_adjusted_mae": "mae",
        "mae_per_latency": "mae",
    }.get(normalized, normalized)


def _materialize_temporal_metric_aliases(*, metrics: dict[str, Any], data_mode: str) -> dict[str, Any]:
    payload = dict(metrics)
    if str(data_mode).strip().lower() == "time_series" and "mae" in payload:
        payload.setdefault("stability_adjusted_mae", payload["mae"])
        payload.setdefault("mae_per_latency", payload["mae"])
    return payload


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
        blocked_reason_codes=["benchmark_disabled"],
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
    blocked_reason_codes: list[str] | None = None,
) -> BenchmarkBundle:
    recommendation = recommended_action or ("benchmark_needed" if benchmark_expected else "continue_experimentation")
    reason_codes = [str(item).strip() for item in (blocked_reason_codes or []) if str(item).strip()] or ["benchmark_evidence_unavailable"]
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
        incumbent_present=False,
        incumbent_name=None,
        beat_target_state=None,
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
    paper_manifest = PaperBenchmarkManifest(
        schema_version=PAPER_BENCHMARK_MANIFEST_SCHEMA_VERSION,
        generated_at=generated_at,
        controls=controls,
        status="not_available",
        dataset_label="unknown",
        dataset_source_name=None,
        dataset_source_type=None,
        source_url=None,
        data_path="",
        task_type="unknown",
        data_mode="unknown",
        target_column="",
        row_count=0,
        column_count=0,
        comparison_metric="unknown",
        metric_direction="higher_is_better",
        selected_model_family=None,
        selected_hyperparameters={},
        benchmark_expected=benchmark_expected,
        horizon_type=None,
        timestamp_cadence_quality=None,
        lagged_baseline_family=None,
        lagged_baseline_metric=None,
        sequence_candidate_status=None,
        sequence_candidate_reason=None,
        summary=summary,
        trace=trace,
    )
    paper_table = PaperBenchmarkTable(
        schema_version=PAPER_BENCHMARK_TABLE_SCHEMA_VERSION,
        generated_at=generated_at,
        controls=controls,
        status="not_available",
        comparison_metric="unknown",
        metric_direction="higher_is_better",
        relaytic_rank=None,
        reference_count=0,
        rows=[],
        summary=summary,
        trace=trace,
    )
    ablation_matrix = BenchmarkAblationMatrix(
        schema_version=BENCHMARK_ABLATION_MATRIX_SCHEMA_VERSION,
        generated_at=generated_at,
        controls=controls,
        status="not_available",
        comparison_metric="unknown",
        metric_direction="higher_is_better",
        rows=[],
        summary=summary,
        trace=trace,
    )
    rerun_variance = RerunVarianceReport(
        schema_version=RERUN_VARIANCE_REPORT_SCHEMA_VERSION,
        generated_at=generated_at,
        controls=controls,
        status="single_run_only",
        comparison_metric="unknown",
        metric_direction="higher_is_better",
        matching_run_count=0,
        run_ids=[],
        metric_values=[],
        mean_metric_value=None,
        min_metric_value=None,
        max_metric_value=None,
        stddev_metric_value=None,
        coefficient_of_variation=None,
        stability_band="single_run_only",
        summary=summary,
        trace=trace,
    )
    claims = BenchmarkClaimsReport(
        schema_version=BENCHMARK_CLAIMS_REPORT_SCHEMA_VERSION,
        generated_at=generated_at,
        controls=controls,
        status="not_available",
        competitiveness_claim="reference_claim_not_available",
        deployment_claim="unknown",
        below_reference=False,
        benchmark_vs_deploy_split=False,
        claim_boundaries=["benchmark evidence unavailable"],
        weak_spots=[summary],
        not_claiming=["global state-of-the-art performance"],
        why_below_reference=None,
        temporal_posture={},
        summary=summary,
        trace=trace,
    )
    shadow_manifest = ShadowTrialManifest(
        schema_version=SHADOW_TRIAL_MANIFEST_SCHEMA_VERSION,
        generated_at=generated_at,
        controls=controls,
        status="no_candidates",
        candidate_count=0,
        runnable_candidate_count=0,
        replay_only_count=0,
        temporal_candidate_count=0,
        comparison_metric="unknown",
        baseline_family=None,
        summary=summary,
        trace=trace,
    )
    shadow_scorecard = ShadowTrialScorecard(
        schema_version=SHADOW_TRIAL_SCORECARD_SCHEMA_VERSION,
        generated_at=generated_at,
        controls=controls,
        status="no_candidates",
        comparison_metric="unknown",
        metric_direction="higher_is_better",
        rows=[],
        summary=summary,
        trace=trace,
    )
    candidate_quarantine = CandidateQuarantine(
        schema_version=CANDIDATE_QUARANTINE_SCHEMA_VERSION,
        generated_at=generated_at,
        controls=controls,
        status="no_candidates",
        quarantined_count=0,
        quarantined_candidates=[],
        summary=summary,
        trace=trace,
    )
    promotion_report = PromotionReadinessReport(
        schema_version=PROMOTION_READINESS_REPORT_SCHEMA_VERSION,
        generated_at=generated_at,
        controls=controls,
        status="no_candidates",
        promotion_ready_count=0,
        candidate_available_count=0,
        quarantined_count=0,
        rows=[],
        summary=summary,
        trace=trace,
    )
    truth_audit = BenchmarkTruthAudit(
        schema_version=BENCHMARK_TRUTH_AUDIT_SCHEMA_VERSION,
        generated_at=generated_at,
        controls=controls,
        status="blocked",
        safe_to_cite_publicly=False,
        truth_precheck_status="blocked",
        protocol_status="unknown",
        security_status="unknown",
        trace_identity_status="unknown",
        eval_surface_parity_status="unknown",
        leakage_status="unknown",
        blocked_reason_codes=reason_codes,
        summary=summary,
        trace=trace,
    )
    claim_guard = PaperClaimGuardReport(
        schema_version=PAPER_CLAIM_GUARD_REPORT_SCHEMA_VERSION,
        generated_at=generated_at,
        controls=controls,
        status="blocked",
        safe_to_cite_publicly=False,
        blocked_reason_codes=reason_codes,
        claim_boundaries=["benchmark evidence unavailable"],
        required_fixes=[_required_fix_for_reason(code) for code in reason_codes],
        summary=summary,
        trace=trace,
    )
    release_gate = BenchmarkReleaseGate(
        schema_version=BENCHMARK_RELEASE_GATE_SCHEMA_VERSION,
        generated_at=generated_at,
        controls=controls,
        status="blocked",
        safe_to_cite_publicly=False,
        demo_safe=False,
        blocked_reason_codes=reason_codes,
        required_fixes=[_required_fix_for_reason(code) for code in reason_codes],
        summary=summary,
        trace=trace,
    )
    leakage_audit = DatasetLeakageAudit(
        schema_version=DATASET_LEAKAGE_AUDIT_SCHEMA_VERSION,
        generated_at=generated_at,
        controls=controls,
        status="unknown",
        leakage_risk_level="unknown",
        blocked_finding_count=0,
        warning_finding_count=0,
        blocked_reason_codes=[],
        findings=[],
        summary=summary,
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
        paper_benchmark_manifest=paper_manifest,
        paper_benchmark_table=paper_table,
        benchmark_ablation_matrix=ablation_matrix,
        rerun_variance_report=rerun_variance,
        benchmark_claims_report=claims,
        shadow_trial_manifest=shadow_manifest,
        shadow_trial_scorecard=shadow_scorecard,
        candidate_quarantine=candidate_quarantine,
        promotion_readiness_report=promotion_report,
        benchmark_truth_audit=truth_audit,
        paper_claim_guard_report=claim_guard,
        benchmark_release_gate=release_gate,
        dataset_leakage_audit=leakage_audit,
    )


def _read_json_artifact(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def _read_jsonl_artifact(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        text = line.strip()
        if not text:
            continue
        try:
            payload = json.loads(text)
        except json.JSONDecodeError:
            continue
        if isinstance(payload, dict):
            rows.append(payload)
    return rows


def _read_frame_or_empty(data_path: str) -> Any:
    try:
        return load_tabular_data(data_path).frame.copy()
    except Exception:
        import pandas as pd

        return pd.DataFrame()


def _best_trial_for_family(
    *,
    ledger: list[dict[str, Any]],
    family: str,
    comparison_metric: str,
    metric_direction: str,
) -> dict[str, Any] | None:
    candidates = [item for item in ledger if _clean_text(item.get("family")) == family]
    if not candidates:
        return None
    ordered = sorted(
        candidates,
        key=lambda item: _benchmark_metric_rank_key(
            _metric_value(item.get("validation_metrics"), comparison_metric),
            metric_direction=metric_direction,
        ),
    )
    return ordered[0]


def _ablation_row(
    *,
    ablation_id: str,
    label: str,
    role: str,
    comparison_metric: str,
    test_metric: float | None,
    validation_metric: float | None,
    model_family: str | None,
    variant_id: str | None,
    selected_metric: float | None,
) -> dict[str, Any]:
    delta_to_selected = None
    if selected_metric is not None and test_metric is not None:
        delta_to_selected = round(float(selected_metric) - float(test_metric), 6)
    return {
        "ablation_id": ablation_id,
        "label": label,
        "role": role,
        "comparison_metric": comparison_metric,
        "model_family": model_family,
        "variant_id": variant_id,
        "validation_metric": validation_metric,
        "test_metric": test_metric,
        "delta_to_selected": delta_to_selected,
    }


def _best_reference_row(
    *,
    reference_rows: list[dict[str, Any]],
    comparison_metric: str,
    metric_direction: str,
) -> dict[str, Any] | None:
    if not reference_rows:
        return None
    ordered = sorted(
        reference_rows,
        key=lambda item: _benchmark_metric_rank_key(
            _metric_value(item.get("test_metric"), comparison_metric),
            metric_direction=metric_direction,
        ),
    )
    return ordered[0]


def _benchmark_metric_rank_key(value: float | None, *, metric_direction: str) -> tuple[float, int]:
    if value is None:
        return (float("inf"), 1)
    if metric_direction == "lower_is_better":
        return (float(value), 0)
    return (-float(value), 0)


def _find_lagged_reference(*, reference_rows: list[dict[str, Any]]) -> dict[str, Any] | None:
    return next(
        (
            item
            for item in reference_rows
            if str(item.get("model_family", "")).strip().startswith("sklearn_lagged_")
            or "lagged" in str(item.get("model_family", "")).strip()
        ),
        None,
    )


def _find_lagged_baseline_reference(*, root: Path) -> dict[str, Any] | None:
    matrix = _read_json_artifact(root / "reference_approach_matrix.json")
    return _find_lagged_reference(reference_rows=list(matrix.get("references", [])))


def _temporal_horizon_type(*, task_type: str, data_mode: str) -> str | None:
    if data_mode != "time_series":
        return None
    if is_classification_task(task_type):
        return "same_step_temporal_classification"
    return "one_step_temporal_regression"


def _discover_matching_benchmark_runs(
    *,
    current_run_dir: Path,
    comparison_metric: str,
    task_type: str,
    target_column: str,
    data_mode: str,
    row_count: int,
    column_count: int,
) -> list[tuple[str, float]]:
    parent = current_run_dir.parent
    if not parent.exists():
        return []
    rows: list[tuple[str, float]] = []
    for child in parent.iterdir():
        if not child.is_dir() or child == current_run_dir:
            continue
        summary = _read_json_artifact(child / "run_summary.json")
        matrix = _read_json_artifact(child / "reference_approach_matrix.json")
        if not summary or not matrix:
            continue
        decision = dict(summary.get("decision", {}))
        data = dict(summary.get("data", {}))
        if _clean_text(decision.get("task_type")) != task_type:
            continue
        if _clean_text(decision.get("target_column")) != target_column:
            continue
        if _clean_text(data.get("data_mode")) != data_mode:
            continue
        if int(data.get("row_count", -1) or -1) != int(row_count):
            continue
        if int(data.get("column_count", -1) or -1) != int(column_count):
            continue
        relaytic_reference = dict(matrix.get("relaytic_reference", {}))
        if _clean_text(matrix.get("comparison_metric")) != comparison_metric:
            continue
        metric_value = _metric_value(relaytic_reference.get("test_metric"), comparison_metric)
        if metric_value is None:
            continue
        rows.append((str(summary.get("run_id") or child.name), float(metric_value)))
    return rows


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


def _optional_float(value: Any) -> float | None:
    try:
        if value is None or str(value).strip() == "":
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def _metric_delta(*, candidate_value: float | None, baseline_value: float | None, metric_direction: str) -> float | None:
    if candidate_value is None or baseline_value is None:
        return None
    if metric_direction == "lower_is_better":
        return float(baseline_value) - float(candidate_value)
    return float(candidate_value) - float(baseline_value)


def _metric_better(
    *,
    candidate_value: float | None,
    baseline_value: float | None,
    metric_direction: str,
    minimum_delta: float,
) -> bool:
    delta = _metric_delta(
        candidate_value=candidate_value,
        baseline_value=baseline_value,
        metric_direction=metric_direction,
    )
    return bool(delta is not None and delta > float(minimum_delta))


def _metric_near(*, candidate_value: float | None, baseline_value: float | None, metric_direction: str) -> bool:
    delta = _metric_delta(
        candidate_value=candidate_value,
        baseline_value=baseline_value,
        metric_direction=metric_direction,
    )
    return bool(delta is not None and delta >= -0.02)


def _shadow_slug(value: str) -> str:
    cleaned = "".join(char if char.isalnum() else "_" for char in str(value or "").strip().lower())
    return cleaned.strip("_") or "shadow_candidate"


def _normalize_shadow_baseline_family(value: str | None) -> str | None:
    family = _clean_text(value)
    if not family:
        return None
    if family.startswith("sklearn_"):
        family = family[len("sklearn_") :]
    return family


def _infer_data_mode(*, frame: Any, timestamp_column: str | None) -> str:
    if timestamp_column and timestamp_column in frame.columns:
        return "time_series"
    return "steady_state"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()
