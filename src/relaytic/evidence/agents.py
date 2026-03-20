"""Slice 06 challenger, ablation, audit, and report pipeline."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import math
from pathlib import Path
from typing import Any

import pandas as pd

from relaytic.ingestion import load_tabular_data
from relaytic.integrations import (
    compute_regression_residual_diagnostics,
    run_pyod_anomaly_challenger,
    run_resampled_logistic_challenger,
)
from relaytic.modeling import run_inference_from_artifacts, train_surrogate_candidates
from relaytic.core.json_utils import write_json

from .models import (
    ABLATION_REPORT_SCHEMA_VERSION,
    AUDIT_REPORT_SCHEMA_VERSION,
    BELIEF_UPDATE_SCHEMA_VERSION,
    CHALLENGER_REPORT_SCHEMA_VERSION,
    EXPERIMENT_REGISTRY_SCHEMA_VERSION,
    AblationReport,
    AuditReport,
    BeliefUpdate,
    ChallengerReport,
    EvidenceBundle,
    EvidenceControls,
    EvidenceTrace,
    ExperimentRegistry,
    build_evidence_controls_from_policy,
)
from .semantic import EvidenceLocalAdvisor, build_local_advisor


@dataclass(frozen=True)
class EvidenceRunResult:
    """Evidence artifacts plus leaderboard and report surfaces."""

    bundle: EvidenceBundle
    leaderboard_rows: list[dict[str, Any]]
    technical_report_markdown: str
    decision_memo_markdown: str


class ChallengerAgent:
    """Executes one bounded challenger branch against the current champion."""

    def __init__(self, *, controls: EvidenceControls) -> None:
        self.controls = controls

    def run(
        self,
        *,
        frame: Any,
        data_path: str,
        run_dir: str | Path,
        plan: dict[str, Any],
        champion_experiment: dict[str, Any],
        memory_bundle: dict[str, Any] | None = None,
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        memory_bundle = memory_bundle or {}
        summary = dict(plan.get("execution_summary") or {})
        handoff = dict(plan.get("builder_handoff") or {})
        external = _run_external_challenger(
            frame=frame,
            run_dir=run_dir,
            plan=plan,
            handoff=handoff,
        )
        if external is not None:
            return external
        champion_family = str(summary.get("selected_model_family", "")).strip() or str(
            champion_experiment.get("model_family", "")
        ).strip()
        challenger_family = _choose_challenger_family(
            plan=plan,
            champion_family=champion_family,
            challenger_prior_suggestions=_bundle_item(memory_bundle, "challenger_prior_suggestions"),
        )
        if not challenger_family:
            return (
                {
                    "experiment_id": "",
                    "status": "skipped",
                    "winner": "champion",
                    "comparison_metric": str(plan.get("primary_metric", "")).strip() or "unknown",
                    "comparison_split": "test",
                    "delta_to_champion": None,
                    "summary": "No challenger family was available beyond the selected champion.",
                    "result": {},
                },
                {},
            )

        experiment_id = f"challenger_{_slug(challenger_family)}"
        experiment_root = Path(run_dir) / "experiments" / experiment_id
        try:
            result = train_surrogate_candidates(
                frame=frame.copy(),
                target_column=str(handoff["target_column"]),
                feature_columns=[str(item) for item in handoff.get("feature_columns", [])],
                requested_model_family=challenger_family,
                timestamp_column=_optional_str(handoff.get("timestamp_column")),
                normalize=bool(handoff.get("normalize", True)),
                missing_data_strategy=str(handoff.get("missing_data_strategy", "fill_median")),
                compare_against_baseline=False,
                lag_horizon_samples=_optional_int(handoff.get("lag_horizon_samples")),
                threshold_policy=_optional_str(handoff.get("threshold_policy")),
                decision_threshold=_optional_float(handoff.get("decision_threshold")),
                task_type=_optional_str(handoff.get("task_type")),
                run_id=f"{Path(run_dir).name}_{experiment_id}",
                checkpoint_tag="relaytic_slice06_challenger",
                data_references=[str(item) for item in handoff.get("data_references", [str(Path(data_path))])],
                selection_metric=_optional_str(handoff.get("selection_metric")),
                preferred_candidate_order=[challenger_family],
                output_run_dir=experiment_root,
                checkpoint_base_dir=experiment_root / "checkpoints",
            )
        except Exception as exc:
            return (
                {
                    "experiment_id": experiment_id,
                    "status": "error",
                    "winner": "champion",
                    "comparison_metric": str(plan.get("primary_metric", "")).strip() or "unknown",
                    "comparison_split": "test",
                    "delta_to_champion": None,
                    "summary": f"Challenger execution failed: {exc}",
                    "result": {},
                },
                {
                    "experiment_id": experiment_id,
                    "role": "challenger",
                    "status": "error",
                    "model_family": challenger_family,
                    "primary_metric": str(plan.get("primary_metric", "")).strip() or "unknown",
                    "evaluation_split": "test",
                    "primary_metric_value": None,
                    "delta_from_champion": None,
                    "feature_count": len([str(item) for item in handoff.get("feature_columns", [])]),
                    "artifact_root": str(experiment_root),
                    "note": f"Execution failed: {exc}",
                },
            )

        comparison_metric = str(plan.get("primary_metric", "")).strip() or "unknown"
        comparison_split, champion_value = _primary_metric_snapshot(
            metrics=dict(summary.get("selected_metrics") or {}),
            primary_metric=comparison_metric,
        )
        _, challenger_value = _primary_metric_snapshot(
            metrics=dict(result.get("selected_metrics") or {}),
            primary_metric=comparison_metric,
        )
        delta = _metric_delta(
            metric_name=comparison_metric,
            baseline=champion_value,
            candidate=challenger_value,
        )
        challenger_wins = _candidate_beats_baseline(
            metric_name=comparison_metric,
            baseline=champion_value,
            candidate=challenger_value,
        )
        selected_family = str(result.get("selected_model_family", "")).strip() or challenger_family
        summary_line = (
            f"Challenger `{selected_family}` {'beat' if challenger_wins else 'did not beat'} "
            f"the champion on `{comparison_metric}` ({comparison_split})."
        )
        return (
            {
                "experiment_id": experiment_id,
                "status": str(result.get("status", "error")),
                "winner": "challenger" if challenger_wins else "champion",
                "comparison_metric": comparison_metric,
                "comparison_split": comparison_split,
                "delta_to_champion": delta,
                "summary": summary_line,
                "result": result,
            },
            {
                "experiment_id": experiment_id,
                "role": "challenger",
                "status": str(result.get("status", "error")),
                "model_family": selected_family,
                "primary_metric": comparison_metric,
                "evaluation_split": comparison_split,
                "primary_metric_value": challenger_value,
                "delta_from_champion": delta,
                "feature_count": len([str(item) for item in handoff.get("feature_columns", [])]),
                "artifact_root": str(experiment_root),
                "note": summary_line,
            },
        )


class AblationAgent:
    """Runs bounded feature-drop ablations against the champion family."""

    def __init__(self, *, controls: EvidenceControls) -> None:
        self.controls = controls

    def run(
        self,
        *,
        frame: Any,
        data_path: str,
        run_dir: str | Path,
        plan: dict[str, Any],
        champion_experiment: dict[str, Any],
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        summary = dict(plan.get("execution_summary") or {})
        handoff = dict(plan.get("builder_handoff") or {})
        feature_columns = [str(item) for item in handoff.get("feature_columns", []) if str(item).strip()]
        if len(feature_columns) <= 1:
            return (
                [
                    {
                        "experiment_id": "",
                        "status": "skipped",
                        "removed_feature": None,
                        "delta_to_champion": None,
                        "interpretation": "Ablation skipped because the first route has one or zero usable features.",
                    }
                ],
                [],
            )

        comparison_metric = str(plan.get("primary_metric", "")).strip() or "unknown"
        comparison_split, champion_value = _primary_metric_snapshot(
            metrics=dict(summary.get("selected_metrics") or {}),
            primary_metric=comparison_metric,
        )
        champion_family = str(summary.get("selected_model_family", "")).strip() or str(
            champion_experiment.get("model_family", "")
        ).strip()
        ablation_targets = feature_columns[: min(self.controls.max_ablation_features, len(feature_columns))]
        ablations: list[dict[str, Any]] = []
        registry_entries: list[dict[str, Any]] = []

        for feature_name in ablation_targets:
            ablated_features = [item for item in feature_columns if item != feature_name]
            experiment_id = f"ablation_without_{_slug(feature_name)}"
            experiment_root = Path(run_dir) / "experiments" / "ablations" / f"without_{_slug(feature_name)}"
            if not ablated_features:
                ablations.append(
                    {
                        "experiment_id": experiment_id,
                        "status": "skipped",
                        "removed_feature": feature_name,
                        "delta_to_champion": None,
                        "interpretation": "Feature drop would leave no usable inputs.",
                    }
                )
                continue
            try:
                result = train_surrogate_candidates(
                    frame=frame.copy(),
                    target_column=str(handoff["target_column"]),
                    feature_columns=ablated_features,
                    requested_model_family=champion_family,
                    timestamp_column=_optional_str(handoff.get("timestamp_column")),
                    normalize=bool(handoff.get("normalize", True)),
                    missing_data_strategy=str(handoff.get("missing_data_strategy", "fill_median")),
                    compare_against_baseline=False,
                    lag_horizon_samples=_optional_int(handoff.get("lag_horizon_samples")),
                    threshold_policy=_optional_str(handoff.get("threshold_policy")),
                    decision_threshold=_optional_float(handoff.get("decision_threshold")),
                    task_type=_optional_str(handoff.get("task_type")),
                    run_id=f"{Path(run_dir).name}_{experiment_id}",
                    checkpoint_tag="relaytic_slice06_ablation",
                    data_references=[str(item) for item in handoff.get("data_references", [str(Path(data_path))])],
                    selection_metric=_optional_str(handoff.get("selection_metric")),
                    preferred_candidate_order=[champion_family],
                    output_run_dir=experiment_root,
                    checkpoint_base_dir=experiment_root / "checkpoints",
                )
            except Exception as exc:
                ablations.append(
                    {
                        "experiment_id": experiment_id,
                        "status": "error",
                        "removed_feature": feature_name,
                        "delta_to_champion": None,
                        "interpretation": f"Ablation failed: {exc}",
                    }
                )
                registry_entries.append(
                    {
                        "experiment_id": experiment_id,
                        "role": "ablation",
                        "status": "error",
                        "model_family": champion_family,
                        "primary_metric": comparison_metric,
                        "evaluation_split": comparison_split,
                        "primary_metric_value": None,
                        "delta_from_champion": None,
                        "feature_count": len(ablated_features),
                        "artifact_root": str(experiment_root),
                        "note": f"Dropped `{feature_name}` but execution failed: {exc}",
                    }
                )
                continue

            _, ablation_value = _primary_metric_snapshot(
                metrics=dict(result.get("selected_metrics") or {}),
                primary_metric=comparison_metric,
            )
            delta = _metric_delta(
                metric_name=comparison_metric,
                baseline=champion_value,
                candidate=ablation_value,
            )
            interpretation = _interpret_ablation_delta(metric_name=comparison_metric, delta=delta)
            ablations.append(
                {
                    "experiment_id": experiment_id,
                    "status": str(result.get("status", "error")),
                    "removed_feature": feature_name,
                    "remaining_features": ablated_features,
                    "delta_to_champion": delta,
                    "primary_metric": comparison_metric,
                    "comparison_split": comparison_split,
                    "primary_metric_value": ablation_value,
                    "selected_model_family": str(result.get("selected_model_family", "")).strip() or champion_family,
                    "interpretation": interpretation,
                    "artifact_root": str(experiment_root),
                }
            )
            registry_entries.append(
                {
                    "experiment_id": experiment_id,
                    "role": "ablation",
                    "status": str(result.get("status", "error")),
                    "model_family": str(result.get("selected_model_family", "")).strip() or champion_family,
                    "primary_metric": comparison_metric,
                    "evaluation_split": comparison_split,
                    "primary_metric_value": ablation_value,
                    "delta_from_champion": delta,
                    "feature_count": len(ablated_features),
                    "artifact_root": str(experiment_root),
                    "note": f"Dropped `{feature_name}`. {interpretation}",
                }
            )

        return ablations, registry_entries


class AuditAgent:
    """Builds a provisional audit and belief update from experiment evidence."""

    def __init__(
        self,
        *,
        controls: EvidenceControls,
        advisor: EvidenceLocalAdvisor | None = None,
    ) -> None:
        self.controls = controls
        self.advisor = advisor

    def run(
        self,
        *,
        run_dir: str | Path,
        data_path: str,
        source_frame: Any,
        plan: dict[str, Any],
        intake_bundle: dict[str, Any],
        challenger_result: dict[str, Any],
        ablations: list[dict[str, Any]],
    ) -> tuple[dict[str, Any], dict[str, Any], EvidenceTrace]:
        root = Path(run_dir)
        execution_summary = dict(plan.get("execution_summary") or {})
        selected_metrics = dict(execution_summary.get("selected_metrics") or {})
        comparison_metric = str(plan.get("primary_metric", "")).strip() or "unknown"
        validation_metrics = dict(selected_metrics.get("validation") or {})
        test_metrics = dict(selected_metrics.get("test") or {})
        train_metrics = dict(selected_metrics.get("train") or {})
        validation_value = _metric_value(validation_metrics, comparison_metric)
        test_value = _metric_value(test_metrics, comparison_metric)
        train_value = _metric_value(train_metrics, comparison_metric)
        generalization_gap = _signed_metric_gap(
            metric_name=comparison_metric,
            reference=validation_value,
            observed=test_value,
        )

        inference_path = root / "reports" / "audit_inference.json"
        inference_audit = run_inference_from_artifacts(
            data_path=data_path,
            run_dir=str(root),
            output_path=str(inference_path),
        )
        ood_summary = dict(inference_audit.get("ood_summary") or {})
        drift_summary = dict(inference_audit.get("drift_summary") or {})
        assumptions = list((dict(intake_bundle.get("assumption_log") or {})).get("entries", []))
        feature_risk_flags = list((dict(plan.get("builder_handoff") or {})).get("feature_risk_flags", []))
        external_diagnostics: list[dict[str, Any]] = []
        load_bearing_features = [
            str(item.get("removed_feature", "")).strip()
            for item in ablations
            if str(item.get("interpretation", "")).strip().startswith("Load-bearing")
        ]

        findings: list[dict[str, Any]] = []
        if challenger_result.get("winner") == "challenger":
            findings.append(
                {
                    "severity": "high",
                    "title": "Challenger outperformed the baseline.",
                    "detail": str(challenger_result.get("summary", "")).strip(),
                }
            )
        if generalization_gap is not None and abs(generalization_gap) >= 0.03:
            findings.append(
                {
                    "severity": "medium",
                    "title": "Generalization gap is visible.",
                    "detail": (
                        f"`{comparison_metric}` changed by {generalization_gap:+.4f} between validation and test."
                    ),
                }
            )
        if float(ood_summary.get("overall_ood_fraction", 0.0)) >= 0.05:
            findings.append(
                {
                    "severity": "medium",
                    "title": "Inference data exceeds the training envelope.",
                    "detail": "At least one feature crossed the observed training range on the supplied dataset.",
                }
            )
        if float(drift_summary.get("overall_drift_score", 0.0)) >= 0.50:
            findings.append(
                {
                    "severity": "medium",
                    "title": "Feature drift is material.",
                    "detail": "The inference distribution moved meaningfully away from the training midpoint.",
                }
            )
        if load_bearing_features:
            findings.append(
                {
                    "severity": "medium",
                    "title": "The first route depends on a small set of load-bearing signals.",
                    "detail": "Dropping these features caused a meaningful quality loss: "
                    + ", ".join(load_bearing_features),
                }
            )
        if feature_risk_flags:
            findings.append(
                {
                    "severity": "low",
                    "title": "The baseline retained heuristic-risk signals.",
                    "detail": "These columns were retained to keep the first route viable: "
                    + ", ".join(str(item.get("column", "")).strip() for item in feature_risk_flags if str(item.get("column", "")).strip()),
                }
            )
        if assumptions:
            findings.append(
                {
                    "severity": "low",
                    "title": "The run proceeded with explicit assumptions.",
                    "detail": f"Relaytic logged {len(assumptions)} assumption(s) rather than waiting for clarification.",
                }
            )
        task_type = str(plan.get("task_type", "")).strip()
        target_column = str((dict(plan.get("builder_handoff") or {})).get("target_column", "")).strip()
        statsmodels_report = _statsmodels_audit_report(
            source_frame=source_frame,
            inference_audit=inference_audit,
            target_column=target_column,
            task_type=task_type,
        )
        external_diagnostics.append(statsmodels_report)
        findings.extend(_integration_findings(statsmodels_report))
        if not findings:
            findings.append(
                {
                    "severity": "low",
                    "title": "No material evidence objections were found in the Slice 06 pass.",
                    "detail": "The baseline survived challenger, ablation, and audit checks with no major warning flags.",
                }
            )

        provisional_recommendation, readiness_level = _provisional_recommendation(
            challenger_winner=str(challenger_result.get("winner", "")).strip(),
            ood_fraction=float(ood_summary.get("overall_ood_fraction", 0.0)),
            drift_score=float(drift_summary.get("overall_drift_score", 0.0)),
            load_bearing_count=len(load_bearing_features),
            assumption_count=len(assumptions),
            generalization_gap=generalization_gap,
        )

        llm_advisory: dict[str, Any] | None = None
        llm_status = "not_requested"
        advisory_notes: list[str] = []
        if self.advisor is not None:
            advisory = self.advisor.complete_json(
                task_name="evidence_review",
                system_prompt=(
                    "You are Relaytic's bounded evidence reviewer. Read the structured audit snapshot only. "
                    "Return JSON with keys belief_shift, audit_focus, next_actions, and memo_note. "
                    "belief_shift must be a short sentence. audit_focus and next_actions must be short string lists."
                ),
                payload={
                    "primary_metric": comparison_metric,
                    "selected_model_family": execution_summary.get("selected_model_family"),
                    "challenger_result": challenger_result,
                    "ablation_results": ablations,
                    "ood_summary": ood_summary,
                    "drift_summary": drift_summary,
                    "findings": findings,
                    "provisional_recommendation": provisional_recommendation,
                },
            )
            llm_status = "advisory_used" if advisory.status == "ok" and advisory.payload else advisory.status
            advisory_notes.extend(advisory.notes)
            if advisory.payload:
                llm_advisory = advisory.payload

        trace = EvidenceTrace(
            agent="audit_agent",
            operating_mode="deterministic_plus_advisory" if self.advisor is not None else "deterministic_only",
            llm_used=llm_advisory is not None,
            llm_status=llm_status,
            deterministic_evidence=[
                "planning_execution_summary",
                "challenger_comparison",
                "feature_ablation_runs",
                "inference_shift_diagnostics",
                "optional_external_diagnostics",
            ],
            advisory_notes=advisory_notes,
        )

        updated_belief = _belief_statement(
            recommendation=provisional_recommendation,
            readiness_level=readiness_level,
            challenger_winner=str(challenger_result.get("winner", "")).strip(),
        )
        if llm_advisory is not None and str(llm_advisory.get("belief_shift", "")).strip():
            updated_belief = str(llm_advisory.get("belief_shift", "")).strip()
        supporting_evidence = [
            f"Champion model: {execution_summary.get('selected_model_family') or 'unknown'}",
            str(challenger_result.get("summary", "")).strip(),
            f"OOD fraction={float(ood_summary.get('overall_ood_fraction', 0.0)):.4f}",
            f"Drift score={float(drift_summary.get('overall_drift_score', 0.0)):.4f}",
        ]
        supporting_evidence.extend(
            f"{str(item.get('removed_feature', '')).strip()}: {str(item.get('interpretation', '')).strip()}"
            for item in ablations[:2]
            if str(item.get("removed_feature", "")).strip()
        )
        open_questions = list(inference_audit.get("recommendations", []))[:3]
        if llm_advisory is not None:
            open_questions.extend(
                str(item).strip()
                for item in llm_advisory.get("next_actions", [])
                if str(item).strip()
            )
        open_questions = _dedupe_strings(open_questions)[:5]

        return (
            {
                "champion_experiment_id": "champion_selected_route",
                "provisional_recommendation": provisional_recommendation,
                "readiness_level": readiness_level,
                "findings": findings,
                "external_diagnostics": external_diagnostics,
                "inference_audit_path": str(inference_path),
                "llm_advisory": llm_advisory,
                "summary": _audit_summary(provisional_recommendation, readiness_level, findings),
            },
            {
                "previous_belief": "The first planned route is the best current autonomous baseline.",
                "updated_belief": updated_belief,
                "recommended_action": provisional_recommendation,
                "confidence_level": readiness_level,
                "supporting_evidence": _dedupe_strings(supporting_evidence),
                "open_questions": open_questions,
                "llm_advisory": llm_advisory,
                "summary": _belief_summary(provisional_recommendation, readiness_level, updated_belief),
            },
            trace,
        )


def run_evidence_review(
    *,
    run_dir: str | Path,
    data_path: str,
    policy: dict[str, Any],
    mandate_bundle: dict[str, Any],
    context_bundle: dict[str, Any],
    intake_bundle: dict[str, Any],
    investigation_bundle: dict[str, Any],
    planning_bundle: dict[str, Any],
    memory_bundle: dict[str, Any] | None = None,
    config_path: str | None = None,
    sheet_name: str | None = None,
    header_row: int | None = None,
    data_start_row: int | None = None,
) -> EvidenceRunResult:
    """Execute the Slice 06 evidence stage for an executed Relaytic run."""
    del mandate_bundle, context_bundle, investigation_bundle
    memory_bundle = memory_bundle or {}
    root = Path(run_dir)
    plan = _bundle_item(planning_bundle, "plan")
    if not plan:
        raise ValueError("Slice 06 evidence requires `plan.json`.")
    execution_summary = dict(plan.get("execution_summary") or {})
    if not execution_summary:
        raise ValueError("Slice 06 evidence requires an executed plan with `execution_summary`.")

    controls = build_evidence_controls_from_policy(policy)
    advisor = build_local_advisor(controls=controls, config_path=config_path)
    loaded = load_tabular_data(
        data_path,
        sheet_name=sheet_name,
        header_row=header_row,
        data_start_row=data_start_row,
    )
    frame = loaded.frame.copy()
    champion_experiment = _build_champion_experiment(plan=plan, run_dir=root)

    challenger_agent = ChallengerAgent(controls=controls)
    challenger_result, challenger_registry_entry = challenger_agent.run(
        frame=frame,
        data_path=data_path,
        run_dir=root,
        plan=plan,
        champion_experiment=champion_experiment,
        memory_bundle=memory_bundle,
    )

    ablation_agent = AblationAgent(controls=controls)
    ablations, ablation_registry_entries = ablation_agent.run(
        frame=frame,
        data_path=data_path,
        run_dir=root,
        plan=plan,
        champion_experiment=champion_experiment,
    )

    audit_agent = AuditAgent(controls=controls, advisor=advisor)
    audit_payload, belief_payload, audit_trace = audit_agent.run(
        run_dir=root,
        data_path=data_path,
        source_frame=frame,
        plan=plan,
        intake_bundle=intake_bundle,
        challenger_result=challenger_result,
        ablations=ablations,
    )

    llm_advisory = dict(audit_payload.get("llm_advisory") or {})
    challenger_trace = EvidenceTrace(
        agent="challenger_agent",
        operating_mode="deterministic_only",
        llm_used=False,
        llm_status="not_requested",
        deterministic_evidence=["planning_execution_summary", "bounded_challenger_training"],
    )
    ablation_trace = EvidenceTrace(
        agent="ablation_agent",
        operating_mode="deterministic_only",
        llm_used=False,
        llm_status="not_requested",
        deterministic_evidence=["feature_drop_training_runs", "metric_delta_analysis"],
    )
    registry_trace = EvidenceTrace(
        agent="experiment_registry",
        operating_mode="deterministic_plus_advisory" if llm_advisory else "deterministic_only",
        llm_used=bool(llm_advisory),
        llm_status="advisory_used" if llm_advisory else "not_requested",
        deterministic_evidence=[
            "champion_execution_summary",
            "challenger_report",
            "ablation_report",
            "audit_report",
        ],
        advisory_notes=[
            str(item).strip()
            for item in llm_advisory.get("audit_focus", [])
            if str(item).strip()
        ],
    )

    experiments = [champion_experiment]
    if challenger_registry_entry:
        experiments.append(challenger_registry_entry)
    experiments.extend(ablation_registry_entries)
    leaderboard_rows = _build_leaderboard_rows(
        experiments=experiments,
        primary_metric=str(plan.get("primary_metric", "")).strip() or "unknown",
    )

    generated_at = _utc_now()
    bundle = EvidenceBundle(
        experiment_registry=ExperimentRegistry(
            schema_version=EXPERIMENT_REGISTRY_SCHEMA_VERSION,
            generated_at=generated_at,
            controls=controls,
            champion_experiment_id=str(champion_experiment["experiment_id"]),
            experiments=experiments,
            summary=_registry_summary(experiments),
            trace=registry_trace,
        ),
        challenger_report=ChallengerReport(
            schema_version=CHALLENGER_REPORT_SCHEMA_VERSION,
            generated_at=generated_at,
            controls=controls,
            champion_experiment_id=str(champion_experiment["experiment_id"]),
            challenger_experiment_id=str(challenger_result.get("experiment_id") or "") or None,
            comparison_metric=str(challenger_result.get("comparison_metric", "")).strip() or "unknown",
            comparison_split=str(challenger_result.get("comparison_split", "test")).strip() or "test",
            winner=str(challenger_result.get("winner", "champion")).strip() or "champion",
            delta_to_champion=_optional_float(challenger_result.get("delta_to_champion")),
            summary=str(challenger_result.get("summary", "")).strip() or "No challenger summary recorded.",
            comparison={
                "champion_model_family": champion_experiment.get("model_family"),
                "challenger_model_family": (
                    dict(challenger_result.get("result") or {}).get("selected_model_family")
                    or challenger_registry_entry.get("model_family")
                    if challenger_registry_entry
                    else None
                ),
                "champion_metric_value": champion_experiment.get("primary_metric_value"),
                "challenger_metric_value": challenger_registry_entry.get("primary_metric_value")
                if challenger_registry_entry
                else None,
                "status": challenger_result.get("status"),
                "integration": challenger_registry_entry.get("integration") if challenger_registry_entry else None,
                "integration_version": challenger_registry_entry.get("integration_version")
                if challenger_registry_entry
                else None,
            },
            memory_context={
                "preferred_challenger_family": _optional_str(
                    _bundle_item(memory_bundle, "challenger_prior_suggestions").get("preferred_challenger_family")
                ),
                "memory_influenced": str(
                    _bundle_item(memory_bundle, "challenger_prior_suggestions").get("status", "")
                ).strip()
                == "memory_influenced",
            }
            if memory_bundle
            else None,
            llm_advisory=llm_advisory or None,
            trace=challenger_trace,
        ),
        ablation_report=AblationReport(
            schema_version=ABLATION_REPORT_SCHEMA_VERSION,
            generated_at=generated_at,
            controls=controls,
            baseline_experiment_id=str(champion_experiment["experiment_id"]),
            comparison_metric=str(plan.get("primary_metric", "")).strip() or "unknown",
            comparison_split="test",
            ablations=ablations,
            summary=_ablation_summary(ablations),
            trace=ablation_trace,
        ),
        audit_report=AuditReport(
            schema_version=AUDIT_REPORT_SCHEMA_VERSION,
            generated_at=generated_at,
            controls=controls,
            champion_experiment_id=str(audit_payload["champion_experiment_id"]),
            provisional_recommendation=str(audit_payload["provisional_recommendation"]),
            readiness_level=str(audit_payload["readiness_level"]),
            findings=list(audit_payload["findings"]),
            external_diagnostics=list(audit_payload.get("external_diagnostics", [])),
            inference_audit_path=str(audit_payload["inference_audit_path"]),
            llm_advisory=audit_payload["llm_advisory"],
            summary=str(audit_payload["summary"]),
            trace=audit_trace,
        ),
        belief_update=BeliefUpdate(
            schema_version=BELIEF_UPDATE_SCHEMA_VERSION,
            generated_at=generated_at,
            controls=controls,
            previous_belief=str(belief_payload["previous_belief"]),
            updated_belief=str(belief_payload["updated_belief"]),
            recommended_action=str(belief_payload["recommended_action"]),
            confidence_level=str(belief_payload["confidence_level"]),
            supporting_evidence=list(belief_payload["supporting_evidence"]),
            open_questions=list(belief_payload["open_questions"]),
            llm_advisory=belief_payload["llm_advisory"],
            summary=str(belief_payload["summary"]),
            trace=audit_trace,
        ),
    )

    return EvidenceRunResult(
        bundle=bundle,
        leaderboard_rows=leaderboard_rows,
        technical_report_markdown=_render_technical_report(bundle=bundle, leaderboard_rows=leaderboard_rows),
        decision_memo_markdown=_render_decision_memo(bundle=bundle),
    )


def _build_champion_experiment(*, plan: dict[str, Any], run_dir: Path) -> dict[str, Any]:
    execution_summary = dict(plan.get("execution_summary") or {})
    primary_metric = str(plan.get("primary_metric", "")).strip() or "unknown"
    comparison_split, primary_metric_value = _primary_metric_snapshot(
        metrics=dict(execution_summary.get("selected_metrics") or {}),
        primary_metric=primary_metric,
    )
    feature_columns = [str(item) for item in plan.get("feature_columns", []) if str(item).strip()]
    return {
        "experiment_id": "champion_selected_route",
        "role": "champion",
        "status": str(execution_summary.get("status", "ok")).strip() or "ok",
        "model_family": str(execution_summary.get("selected_model_family", "")).strip() or "unknown",
        "primary_metric": primary_metric,
        "evaluation_split": comparison_split,
        "primary_metric_value": primary_metric_value,
        "delta_from_champion": 0.0,
        "feature_count": len(feature_columns),
        "artifact_root": str(run_dir),
        "note": "Selected Builder route champion.",
    }


def _build_leaderboard_rows(*, experiments: list[dict[str, Any]], primary_metric: str) -> list[dict[str, Any]]:
    scored: list[tuple[float, dict[str, Any]]] = []
    for item in experiments:
        value = _optional_float(item.get("primary_metric_value"))
        score = _ranking_score(metric_name=primary_metric, value=value)
        scored.append((score, item))
    scored.sort(key=lambda pair: pair[0], reverse=True)
    rows: list[dict[str, Any]] = []
    for index, (_, item) in enumerate(scored, start=1):
        rows.append(
            {
                "rank": index,
                "experiment_id": item.get("experiment_id", ""),
                "role": item.get("role", ""),
                "status": item.get("status", ""),
                "model_family": item.get("model_family", ""),
                "primary_metric": item.get("primary_metric", ""),
                "evaluation_split": item.get("evaluation_split", ""),
                "primary_metric_value": _format_optional_float(item.get("primary_metric_value")),
                "delta_from_champion": _format_optional_float(item.get("delta_from_champion")),
                "feature_count": item.get("feature_count", ""),
                "artifact_root": item.get("artifact_root", ""),
                "note": item.get("note", ""),
            }
        )
    return rows


def _render_technical_report(*, bundle: EvidenceBundle, leaderboard_rows: list[dict[str, Any]]) -> str:
    challenger = bundle.challenger_report.to_dict()
    ablation = bundle.ablation_report.to_dict()
    audit = bundle.audit_report.to_dict()
    belief = bundle.belief_update.to_dict()
    lines = [
        "# Relaytic Technical Report",
        "",
        bundle.audit_report.summary,
        "",
        "## Leaderboard",
    ]
    for row in leaderboard_rows[:5]:
        lines.append(
            f"- #{row['rank']} `{row['experiment_id']}` ({row['role']}): "
            f"`{row['model_family']}` on `{row['primary_metric']}`={row['primary_metric_value'] or 'n/a'}"
        )
    lines.extend(
        [
            "",
            "## Challenger",
            f"- Winner: `{challenger.get('winner') or 'unknown'}`",
            f"- Metric: `{challenger.get('comparison_metric') or 'unknown'}` on `{challenger.get('comparison_split') or 'test'}`",
            f"- Delta to champion: `{_format_optional_float(challenger.get('delta_to_champion'))}`",
            f"- Summary: {challenger.get('summary') or 'No challenger summary recorded.'}",
            "",
            "## Ablations",
            f"- Summary: {ablation.get('summary') or 'No ablation summary recorded.'}",
        ]
    )
    for item in list(ablation.get("ablations", []))[:3]:
        lines.append(
            f"- `{item.get('removed_feature') or 'unknown'}`: "
            f"{item.get('interpretation') or 'No interpretation recorded.'}"
        )
    lines.extend(
        [
            "",
            "## Audit",
            f"- Provisional recommendation: `{audit.get('provisional_recommendation') or 'unknown'}`",
            f"- Readiness level: `{audit.get('readiness_level') or 'unknown'}`",
        ]
    )
    for finding in list(audit.get("findings", []))[:5]:
        lines.append(
            f"- [{finding.get('severity') or 'info'}] {finding.get('title') or 'Finding'}: "
            f"{finding.get('detail') or ''}".rstrip()
        )
    lines.extend(
        [
            "",
            "## Belief Update",
            f"- Updated belief: {belief.get('updated_belief') or 'No belief update recorded.'}",
            f"- Recommended action: `{belief.get('recommended_action') or 'unknown'}`",
        ]
    )
    for item in list(belief.get("open_questions", []))[:3]:
        lines.append(f"- Next question: {item}")
    return "\n".join(lines).rstrip() + "\n"


def _render_decision_memo(*, bundle: EvidenceBundle) -> str:
    audit = bundle.audit_report
    belief = bundle.belief_update
    challenger = bundle.challenger_report
    lines = [
        "# Relaytic Decision Memo",
        "",
        f"Provisional recommendation: `{audit.provisional_recommendation}`",
        "",
        belief.updated_belief,
        "",
        "## Why",
        f"- Challenger outcome: {challenger.summary}",
        f"- Ablation stance: {bundle.ablation_report.summary}",
        f"- Audit stance: {audit.summary}",
        "",
        "## Next",
    ]
    if belief.open_questions:
        for item in belief.open_questions[:3]:
            lines.append(f"- {item}")
    else:
        lines.append("- No additional next actions were recorded.")
    return "\n".join(lines).rstrip() + "\n"


def _primary_metric_snapshot(*, metrics: dict[str, Any], primary_metric: str) -> tuple[str, float | None]:
    for split_name in ("test", "validation", "train"):
        split_metrics = metrics.get(split_name)
        if isinstance(split_metrics, dict):
            value = _metric_value(split_metrics, primary_metric)
            if value is not None:
                return split_name, value
    return "unknown", None


def _metric_value(metrics: dict[str, Any], metric_name: str) -> float | None:
    raw = metrics.get(metric_name)
    try:
        if raw is None:
            return None
        value = float(raw)
    except (TypeError, ValueError):
        return None
    if math.isnan(value) or math.isinf(value):
        return None
    return value


def _candidate_beats_baseline(*, metric_name: str, baseline: float | None, candidate: float | None) -> bool:
    if baseline is None or candidate is None:
        return False
    if _lower_is_better(metric_name):
        return candidate < baseline - 1e-9
    return candidate > baseline + 1e-9


def _metric_delta(*, metric_name: str, baseline: float | None, candidate: float | None) -> float | None:
    if baseline is None or candidate is None:
        return None
    if _lower_is_better(metric_name):
        return baseline - candidate
    return candidate - baseline


def _signed_metric_gap(*, metric_name: str, reference: float | None, observed: float | None) -> float | None:
    if reference is None or observed is None:
        return None
    if _lower_is_better(metric_name):
        return reference - observed
    return observed - reference


def _lower_is_better(metric_name: str) -> bool:
    normalized = metric_name.lower().strip()
    return normalized in {"log_loss", "mae", "rmse", "mse", "brier"}


def _ranking_score(*, metric_name: str, value: float | None) -> float:
    if value is None:
        return float("-inf")
    if _lower_is_better(metric_name):
        return -float(value)
    return float(value)


def _interpret_ablation_delta(*, metric_name: str, delta: float | None) -> str:
    if delta is None:
        return "Ablation did not yield a comparable metric."
    magnitude = abs(delta)
    if delta < -0.05:
        return "Load-bearing feature; removing it substantially worsened the objective."
    if delta < -0.01:
        return "Important feature; removing it hurt the objective."
    if magnitude <= 0.01:
        return "Resilient feature set; removing it barely changed the objective."
    if _lower_is_better(metric_name):
        return "Potentially replaceable feature; the ablation did not materially increase loss."
    return "Potentially replaceable feature; the ablation did not materially damage the objective."


def _provisional_recommendation(
    *,
    challenger_winner: str,
    ood_fraction: float,
    drift_score: float,
    load_bearing_count: int,
    assumption_count: int,
    generalization_gap: float | None,
) -> tuple[str, str]:
    if challenger_winner == "challenger":
        return "review_challenger_before_promotion", "conditional"
    if ood_fraction >= 0.05 or drift_score >= 0.50:
        return "hold_for_data_refresh", "conditional"
    if load_bearing_count >= 2 or assumption_count >= 3:
        return "use_with_operator_review", "conditional"
    if generalization_gap is not None and abs(generalization_gap) >= 0.03:
        return "continue_experimentation", "conditional"
    return "promote_baseline_for_mvp", "strong"


def _belief_statement(*, recommendation: str, readiness_level: str, challenger_winner: str) -> str:
    if recommendation == "review_challenger_before_promotion":
        return "The first route is viable, but the challenger produced enough pressure that Relaytic should not auto-promote the baseline without review."
    if recommendation == "hold_for_data_refresh":
        return "The current route is informative but exposed operating-envelope risk; Relaytic should wait for a data refresh or recalibration pass."
    if recommendation == "use_with_operator_review":
        return "The current route is useful as an MVP baseline, but its dependency profile and assumptions justify explicit review."
    if recommendation == "continue_experimentation":
        return "The first route is a workable baseline, but Relaytic should keep searching because the evidence is still fragile."
    if challenger_winner == "champion" and readiness_level == "strong":
        return "The first route survived its initial evidence pressure and is strong enough for MVP-level use."
    return "Relaytic built a valid first route, but the evidence is not yet decisive."


def _registry_summary(experiments: list[dict[str, Any]]) -> str:
    completed = sum(1 for item in experiments if str(item.get("status", "")).strip() == "ok")
    return f"Relaytic registered {len(experiments)} experiment records, with {completed} completed successfully."


def _ablation_summary(ablations: list[dict[str, Any]]) -> str:
    if not ablations:
        return "No ablations were executed."
    load_bearing = sum(
        1 for item in ablations if str(item.get("interpretation", "")).strip().startswith("Load-bearing")
    )
    return (
        f"Relaytic executed {len(ablations)} ablation checks and flagged {load_bearing} load-bearing feature(s)."
    )


def _audit_summary(recommendation: str, readiness_level: str, findings: list[dict[str, Any]]) -> str:
    top_finding = findings[0]["title"] if findings else "No material objections recorded."
    return (
        f"Relaytic's provisional recommendation is `{recommendation}` with `{readiness_level}` confidence. "
        f"Top finding: {top_finding}"
    )


def _belief_summary(recommendation: str, readiness_level: str, updated_belief: str) -> str:
    return (
        f"Belief updated toward `{recommendation}` with `{readiness_level}` confidence. "
        f"{updated_belief}"
    )


def _run_external_challenger(
    *,
    frame: Any,
    run_dir: str | Path,
    plan: dict[str, Any],
    handoff: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]] | None:
    task_type = _optional_str(handoff.get("task_type")) or str(plan.get("task_type", "")).strip()
    feature_columns = [str(item) for item in handoff.get("feature_columns", []) if str(item).strip()]
    target_column = str(handoff.get("target_column", "")).strip()
    if not feature_columns or not target_column:
        return None

    candidate_reports: list[dict[str, Any]] = []
    if task_type in {"fraud_detection", "anomaly_detection"}:
        candidate_reports.append(
            run_resampled_logistic_challenger(
                frame=frame,
                feature_columns=feature_columns,
                target_column=target_column,
                task_type=task_type,
                surface="evidence.challenger",
            )
        )
    if task_type == "anomaly_detection":
        candidate_reports.append(
            run_pyod_anomaly_challenger(
                frame=frame,
                feature_columns=feature_columns,
                target_column=target_column,
                task_type=task_type,
                surface="evidence.challenger",
            )
        )

    chosen = next((item for item in candidate_reports if str(item.get("status", "")).strip() == "ok"), None)
    if chosen is None:
        return None

    details = dict(chosen.get("details") or {})
    experiment_id = f"challenger_{_slug(str(details.get('model_family', chosen.get('integration', 'external'))))}"
    experiment_root = Path(run_dir) / "experiments" / experiment_id
    experiment_root.mkdir(parents=True, exist_ok=True)
    artifact_path = write_json(experiment_root / "external_challenger_result.json", chosen, indent=2)
    comparison_metric = str(plan.get("primary_metric", "")).strip() or str(details.get("primary_metric", "unknown")).strip() or "unknown"
    comparison_split, champion_value = _primary_metric_snapshot(
        metrics=dict(plan.get("execution_summary", {}).get("selected_metrics") or {}),
        primary_metric=comparison_metric,
    )
    selected_metrics = dict(details.get("selected_metrics") or {})
    challenger_value = _metric_value(dict(selected_metrics.get("test") or {}), comparison_metric)
    if challenger_value is None:
        challenger_value = _metric_value(dict(selected_metrics.get("validation") or {}), comparison_metric)
        comparison_split = "validation"
    delta = _metric_delta(
        metric_name=comparison_metric,
        baseline=champion_value,
        candidate=challenger_value,
    )
    challenger_wins = _candidate_beats_baseline(
        metric_name=comparison_metric,
        baseline=champion_value,
        candidate=challenger_value,
    )
    selected_family = str(details.get("model_family", "")).strip() or str(chosen.get("integration", "external_challenger"))
    summary = (
        f"External challenger `{selected_family}` from `{chosen.get('integration')}` "
        f"{'beat' if challenger_wins else 'did not beat'} the champion on `{comparison_metric}` ({comparison_split})."
    )
    return (
        {
            "experiment_id": experiment_id,
            "status": "ok",
            "winner": "challenger" if challenger_wins else "champion",
            "comparison_metric": comparison_metric,
            "comparison_split": comparison_split,
            "delta_to_champion": delta,
            "summary": summary,
            "result": {
                "selected_model_family": selected_family,
                "selected_metrics": selected_metrics,
                "integration": chosen.get("integration"),
                "integration_version": chosen.get("version"),
                "artifact_path": str(artifact_path),
            },
        },
        {
            "experiment_id": experiment_id,
            "role": "challenger",
            "status": "ok",
            "model_family": selected_family,
            "primary_metric": comparison_metric,
            "evaluation_split": comparison_split,
            "primary_metric_value": challenger_value,
            "delta_from_champion": delta,
            "feature_count": len(feature_columns),
            "artifact_root": str(experiment_root),
            "integration": chosen.get("integration"),
            "integration_version": chosen.get("version"),
            "note": summary,
        },
    )


def _statsmodels_audit_report(
    *,
    source_frame: Any,
    inference_audit: dict[str, Any],
    target_column: str,
    task_type: str,
) -> dict[str, Any]:
    if str(task_type).strip() != "regression":
        return {
            "integration": "statsmodels",
            "package_name": "statsmodels",
            "version": None,
            "surface": "evidence.audit",
            "status": "skipped",
            "compatible": True,
            "notes": ["statsmodels audit is currently limited to regression routes."],
            "details": {"task_type": task_type},
        }
    predictions_path = str(inference_audit.get("predictions_path", "")).strip()
    if not predictions_path:
        return {
            "integration": "statsmodels",
            "package_name": "statsmodels",
            "version": None,
            "surface": "evidence.audit",
            "status": "skipped",
            "compatible": True,
            "notes": ["Inference audit did not provide a predictions file for residual diagnostics."],
            "details": {},
        }
    try:
        prediction_frame = load_tabular_data(predictions_path).frame.copy()
    except Exception as exc:
        return {
            "integration": "statsmodels",
            "package_name": "statsmodels",
            "version": None,
            "surface": "evidence.audit",
            "status": "error",
            "compatible": False,
            "notes": [f"Could not load inference predictions for statsmodels audit: {exc}"],
            "details": {},
        }
    if "source_row" not in prediction_frame.columns or "prediction" not in prediction_frame.columns:
        return {
            "integration": "statsmodels",
            "package_name": "statsmodels",
            "version": None,
            "surface": "evidence.audit",
            "status": "skipped",
            "compatible": True,
            "notes": ["Prediction artifact does not expose `source_row` and `prediction` columns."],
            "details": {},
        }
    aligned_source = source_frame.reset_index(drop=True).reset_index().rename(columns={"index": "source_row"})
    merged = prediction_frame.merge(aligned_source, on="source_row", how="inner")
    if target_column not in merged.columns:
        return {
            "integration": "statsmodels",
            "package_name": "statsmodels",
            "version": None,
            "surface": "evidence.audit",
            "status": "skipped",
            "compatible": True,
            "notes": [f"Target column `{target_column}` is unavailable for residual diagnostics."],
            "details": {},
        }
    y_true = [float(item) for item in pd.to_numeric(merged[target_column], errors="coerce").dropna().tolist()]
    prediction_series = pd.to_numeric(merged["prediction"], errors="coerce")
    aligned = merged.loc[prediction_series.notna()].reset_index(drop=True)
    y_true = pd.to_numeric(aligned[target_column], errors="coerce")
    y_pred = pd.to_numeric(aligned["prediction"], errors="coerce")
    valid = y_true.notna() & y_pred.notna()
    return compute_regression_residual_diagnostics(
        y_true=y_true.loc[valid].tolist(),
        y_pred=y_pred.loc[valid].tolist(),
        surface="evidence.audit",
    )


def _integration_findings(report: dict[str, Any]) -> list[dict[str, Any]]:
    details = dict(report.get("details") or {})
    findings = list(details.get("findings") or [])
    if findings:
        return findings
    if str(report.get("status", "")).strip() == "error":
        return [
            {
                "severity": "low",
                "title": f"{report.get('integration')} integration encountered an error.",
                "detail": "; ".join(str(item) for item in report.get("notes", [])) or "No details recorded.",
                "source": str(report.get("integration", "integration")),
            }
        ]
    return []


def _choose_challenger_family(
    *,
    plan: dict[str, Any],
    champion_family: str,
    challenger_prior_suggestions: dict[str, Any],
) -> str | None:
    preferred = str(challenger_prior_suggestions.get("preferred_challenger_family", "")).strip()
    if preferred and preferred != champion_family:
        return preferred
    for item in challenger_prior_suggestions.get("ranked_families", []):
        candidate = str(dict(item).get("model_family", "")).strip()
        if candidate and candidate != champion_family:
            return candidate
    handoff = dict(plan.get("builder_handoff") or {})
    for item in handoff.get("preferred_candidate_order", []):
        candidate = str(item).strip()
        if candidate and candidate != champion_family:
            return candidate
    task_type = str(plan.get("task_type", "")).strip()
    fallback_order = (
        ["boosted_tree_classifier", "bagged_tree_classifier", "logistic_regression"]
        if "classification" in task_type or task_type in {"fraud_detection", "anomaly_detection"}
        else ["boosted_tree_ensemble", "bagged_tree_ensemble", "linear_ridge"]
    )
    for item in fallback_order:
        if item != champion_family:
            return item
    return None


def _bundle_item(bundle: dict[str, Any], key: str) -> dict[str, Any]:
    payload = bundle.get(key)
    return dict(payload) if isinstance(payload, dict) else {}


def _optional_str(value: Any) -> str | None:
    text = str(value or "").strip()
    return text or None


def _optional_int(value: Any) -> int | None:
    try:
        if value is None:
            return None
        parsed = int(value)
    except (TypeError, ValueError):
        return None
    return parsed


def _optional_float(value: Any) -> float | None:
    try:
        if value is None:
            return None
        parsed = float(value)
    except (TypeError, ValueError):
        return None
    if math.isnan(parsed) or math.isinf(parsed):
        return None
    return parsed


def _dedupe_strings(values: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for value in values:
        text = str(value).strip()
        if not text or text in seen:
            continue
        seen.add(text)
        out.append(text)
    return out


def _format_optional_float(value: Any) -> str:
    parsed = _optional_float(value)
    if parsed is None:
        return ""
    return f"{parsed:.6f}"


def _slug(value: str) -> str:
    out = []
    for char in str(value).strip().lower():
        if char.isalnum():
            out.append(char)
        else:
            out.append("_")
    text = "".join(out).strip("_")
    while "__" in text:
        text = text.replace("__", "_")
    return text or "item"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()
