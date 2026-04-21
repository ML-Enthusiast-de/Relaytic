"""Canonical task-contract artifacts for modeling, benchmark, and review surfaces."""

from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any

from relaytic.core.benchmark_statuses import benchmark_is_reference_competitive
from relaytic.core.json_utils import write_json
from relaytic.ingestion import load_tabular_data
from relaytic.modeling.splitters import build_train_validation_test_split

from .task_detection import is_classification_task


TASK_PROFILE_CONTRACT_SCHEMA_VERSION = "relaytic.task_profile_contract.v1"
TARGET_SEMANTICS_REPORT_SCHEMA_VERSION = "relaytic.target_semantics_report.v1"
METRIC_CONTRACT_SCHEMA_VERSION = "relaytic.metric_contract.v1"
BENCHMARK_MODE_REPORT_SCHEMA_VERSION = "relaytic.benchmark_mode_report.v1"
DEPLOYMENT_READINESS_REPORT_SCHEMA_VERSION = "relaytic.deployment_readiness_report.v1"
BENCHMARK_VS_DEPLOY_REPORT_SCHEMA_VERSION = "relaytic.benchmark_vs_deploy_report.v1"
DATASET_SEMANTICS_AUDIT_SCHEMA_VERSION = "relaytic.dataset_semantics_audit.v1"
OPTIMIZATION_OBJECTIVE_CONTRACT_SCHEMA_VERSION = "relaytic.optimization_objective_contract.v1"
OBJECTIVE_ALIGNMENT_REPORT_SCHEMA_VERSION = "relaytic.objective_alignment_report.v1"
SPLIT_DIAGNOSTICS_REPORT_SCHEMA_VERSION = "relaytic.split_diagnostics_report.v1"
TEMPORAL_FOLD_HEALTH_SCHEMA_VERSION = "relaytic.temporal_fold_health.v1"
METRIC_MATERIALIZATION_AUDIT_SCHEMA_VERSION = "relaytic.metric_materialization_audit.v1"
BENCHMARK_TRUTH_PRECHECK_SCHEMA_VERSION = "relaytic.benchmark_truth_precheck.v1"
AML_DOMAIN_CONTRACT_SCHEMA_VERSION = "relaytic.aml_domain_contract.v1"
AML_CASE_ONTOLOGY_SCHEMA_VERSION = "relaytic.aml_case_ontology.v1"
AML_REVIEW_BUDGET_CONTRACT_SCHEMA_VERSION = "relaytic.aml_review_budget_contract.v1"
AML_CLAIM_SCOPE_SCHEMA_VERSION = "relaytic.aml_claim_scope.v1"


TASK_CONTRACT_FILENAMES = {
    "task_profile_contract": "task_profile_contract.json",
    "target_semantics_report": "target_semantics_report.json",
    "metric_contract": "metric_contract.json",
    "benchmark_mode_report": "benchmark_mode_report.json",
    "deployment_readiness_report": "deployment_readiness_report.json",
    "benchmark_vs_deploy_report": "benchmark_vs_deploy_report.json",
    "dataset_semantics_audit": "dataset_semantics_audit.json",
    "optimization_objective_contract": "optimization_objective_contract.json",
    "objective_alignment_report": "objective_alignment_report.json",
    "split_diagnostics_report": "split_diagnostics_report.json",
    "temporal_fold_health": "temporal_fold_health.json",
    "metric_materialization_audit": "metric_materialization_audit.json",
    "benchmark_truth_precheck": "benchmark_truth_precheck.json",
    "aml_domain_contract": "aml_domain_contract.json",
    "aml_case_ontology": "aml_case_ontology.json",
    "aml_review_budget_contract": "aml_review_budget_contract.json",
    "aml_claim_scope": "aml_claim_scope.json",
}


def sync_task_contract_artifacts(
    run_dir: str | Path,
    *,
    data_path: str | Path | None = None,
    mandate_bundle: dict[str, Any] | None,
    context_bundle: dict[str, Any] | None,
    investigation_bundle: dict[str, Any] | None,
    planning_bundle: dict[str, Any] | None,
    benchmark_bundle: dict[str, Any] | None = None,
    decision_bundle: dict[str, Any] | None = None,
) -> dict[str, Path]:
    """Build and write the canonical task-contract artifact family."""
    artifacts = build_task_contract_artifacts(
        mandate_bundle=mandate_bundle,
        context_bundle=context_bundle,
        investigation_bundle=investigation_bundle,
        planning_bundle=planning_bundle,
        benchmark_bundle=benchmark_bundle,
        decision_bundle=decision_bundle,
        data_path=data_path,
    )
    root = Path(run_dir)
    root.mkdir(parents=True, exist_ok=True)
    return {
        key: write_json(
            root / filename,
            artifacts[key],
            indent=2,
            ensure_ascii=False,
            sort_keys=True,
        )
        for key, filename in TASK_CONTRACT_FILENAMES.items()
    }


def read_task_contract_artifacts(run_dir: str | Path) -> dict[str, Any]:
    """Read the canonical task-contract artifact family."""
    root = Path(run_dir)
    payload: dict[str, Any] = {}
    for key, filename in TASK_CONTRACT_FILENAMES.items():
        path = root / filename
        if not path.exists():
            continue
        payload[key] = json.loads(path.read_text(encoding="utf-8"))
    return payload


def build_task_contract_artifacts(
    *,
    data_path: str | Path | None = None,
    mandate_bundle: dict[str, Any] | None,
    context_bundle: dict[str, Any] | None,
    investigation_bundle: dict[str, Any] | None,
    planning_bundle: dict[str, Any] | None,
    benchmark_bundle: dict[str, Any] | None = None,
    decision_bundle: dict[str, Any] | None = None,
) -> dict[str, dict[str, Any]]:
    """Construct canonical task-contract artifacts from run bundles."""
    generated_at = _utc_now()
    run_brief = _bundle_item(mandate_bundle or {}, "run_brief")
    task_brief = _bundle_item(context_bundle or {}, "task_brief")
    domain_brief = _bundle_item(context_bundle or {}, "domain_brief")
    dataset_profile = _bundle_item(investigation_bundle or {}, "dataset_profile")
    plan = _bundle_item(planning_bundle or {}, "plan")
    builder_handoff = dict(plan.get("builder_handoff") or {})
    task_profile = dict(plan.get("task_profile") or {})
    benchmark_bundle = benchmark_bundle or {}
    decision_bundle = decision_bundle or {}
    benchmark_parity_report = _bundle_item(benchmark_bundle, "benchmark_parity_report")
    reference_approach_matrix = _bundle_item(benchmark_bundle, "reference_approach_matrix")
    decision_constraint_report = _bundle_item(decision_bundle, "decision_constraint_report")
    deployability_assessment = _bundle_item(decision_bundle, "deployability_assessment")
    review_gate_state = _bundle_item(decision_bundle, "review_gate_state")
    execution_summary = dict(plan.get("execution_summary") or {})

    task_type = _clean_text(task_profile.get("task_type")) or _clean_text(plan.get("task_type")) or "unknown"
    task_family = _clean_text(task_profile.get("task_family")) or (
        "classification" if is_classification_task(task_type) else "regression"
    )
    class_count = int(task_profile.get("class_count", 0) or 0)
    minority_fraction = _safe_float(task_profile.get("minority_class_fraction"))
    positive_class_label = _clean_text(task_profile.get("positive_class_label"))
    rare_event_supervised = bool(task_profile.get("rare_event_supervised", False))
    target_semantics = _clean_text(task_profile.get("target_semantics")) or _infer_target_semantics(
        task_family=task_family,
        class_count=class_count,
        rare_event_supervised=rare_event_supervised,
    )
    problem_posture = _clean_text(task_profile.get("problem_posture")) or _infer_problem_posture(
        task_type=task_type,
        task_family=task_family,
        class_count=class_count,
        rare_event_supervised=rare_event_supervised,
    )
    primary_metric = _clean_text(plan.get("primary_metric"))
    selection_metric = _clean_text(builder_handoff.get("selection_metric")) or primary_metric
    secondary_metrics = [
        str(item).strip()
        for item in plan.get("secondary_metrics", [])
        if str(item).strip()
    ]
    threshold_policy = _clean_text(builder_handoff.get("threshold_policy"))
    benchmark_expected = infer_benchmark_expected(run_brief=run_brief, task_brief=task_brief)
    benchmark_comparison_metric = _benchmark_comparison_metric(
        task_type=task_type,
        primary_metric=primary_metric,
        selection_metric=selection_metric,
        rare_event_supervised=rare_event_supervised,
    )
    deployment_primary_metric = _deployment_primary_metric(
        task_type=task_type,
        primary_metric=primary_metric,
        rare_event_supervised=rare_event_supervised,
    )
    benchmark_status = _clean_text(benchmark_parity_report.get("parity_status")) or "not_evaluated_yet"
    deployment_readiness = _deployment_readiness_status(
        deployability_assessment=deployability_assessment,
        review_gate_state=review_gate_state,
        decision_constraint_report=decision_constraint_report,
    )
    split_detected = _benchmark_deploy_split_detected(
        benchmark_status=benchmark_status,
        deployment_readiness=deployment_readiness,
    )

    task_profile_contract = {
        "schema_version": TASK_PROFILE_CONTRACT_SCHEMA_VERSION,
        "generated_at": generated_at,
        "status": "ok" if task_type != "unknown" else "partial",
        "target_column": _clean_text(plan.get("target_column")) or _clean_text(task_profile.get("target_signal")) or _clean_text(task_brief.get("target_column")),
        "task_type": task_type,
        "task_family": task_family,
        "target_semantics": target_semantics,
        "problem_posture": problem_posture,
        "rare_event_supervised": rare_event_supervised,
        "override_applied": bool(task_profile.get("override_applied", False)),
        "row_count": int(task_profile.get("row_count", 0) or dataset_profile.get("row_count", 0) or 0),
        "class_count": class_count,
        "class_balance": dict(task_profile.get("class_balance") or {}),
        "minority_class_fraction": minority_fraction,
        "positive_class_label": positive_class_label,
        "recommended_split_strategy": _clean_text(task_profile.get("recommended_split_strategy")) or _clean_text(plan.get("split_strategy")),
        "data_mode": _clean_text(task_profile.get("data_mode")) or _clean_text(plan.get("data_mode")) or _clean_text(dataset_profile.get("data_mode")),
        "timestamp_column": _clean_text(dataset_profile.get("timestamp_column")) or _clean_text(plan.get("timestamp_column")),
        "rationale": _clean_text(task_profile.get("rationale")),
        "why_not_anomaly_detection": _why_not_anomaly_detection(
            task_type=task_type,
            task_family=task_family,
            class_count=class_count,
            target_semantics=target_semantics,
            rare_event_supervised=rare_event_supervised,
        ),
    }
    target_semantics_report = {
        "schema_version": TARGET_SEMANTICS_REPORT_SCHEMA_VERSION,
        "generated_at": generated_at,
        "status": "ok" if task_type != "unknown" else "partial",
        "target_column": task_profile_contract["target_column"],
        "target_semantics": target_semantics,
        "problem_posture": problem_posture,
        "class_count": class_count,
        "class_balance": dict(task_profile_contract["class_balance"]),
        "minority_class_fraction": minority_fraction,
        "positive_class_label": positive_class_label,
        "labeled_supervision": bool(is_classification_task(task_type) and class_count >= 2),
        "why_not_anomaly_detection": task_profile_contract["why_not_anomaly_detection"],
        "summary": _target_semantics_summary(
            task_type=task_type,
            target_semantics=target_semantics,
            problem_posture=problem_posture,
            class_count=class_count,
        ),
    }
    metric_contract = {
        "schema_version": METRIC_CONTRACT_SCHEMA_VERSION,
        "generated_at": generated_at,
        "status": "ok" if primary_metric or benchmark_comparison_metric else "partial",
        "task_type": task_type,
        "problem_posture": problem_posture,
        "selection_metric": selection_metric,
        "benchmark_comparison_metric": benchmark_comparison_metric,
        "deployment_primary_metric": deployment_primary_metric,
        "secondary_metrics": secondary_metrics,
        "threshold_policy": threshold_policy,
        "summary": (
            f"Relaytic will compare benchmark competitiveness with `{benchmark_comparison_metric}` "
            f"and optimize the active route toward `{deployment_primary_metric or 'unknown'}`."
        ),
    }
    optimization_objective_contract = _build_optimization_objective_contract(
        generated_at=generated_at,
        task_type=task_type,
        task_family=task_family,
        data_mode=_clean_text(task_profile.get("data_mode")) or _clean_text(plan.get("data_mode")) or _clean_text(dataset_profile.get("data_mode")),
        split_strategy=_clean_text(task_profile.get("recommended_split_strategy")) or _clean_text(plan.get("split_strategy")),
        selection_metric=selection_metric,
        primary_metric=primary_metric,
        benchmark_comparison_metric=benchmark_comparison_metric,
        deployment_primary_metric=deployment_primary_metric,
        threshold_policy=threshold_policy,
        rare_event_supervised=rare_event_supervised,
    )
    benchmark_mode_report = {
        "schema_version": BENCHMARK_MODE_REPORT_SCHEMA_VERSION,
        "generated_at": generated_at,
        "status": "ok",
        "benchmark_expected": benchmark_expected,
        "benchmark_assessment_enabled": True,
        "deployment_readiness_enabled": True,
        "posture": "benchmark_and_deploy" if benchmark_expected else "deploy_with_optional_benchmark",
        "deployment_target": _clean_text(run_brief.get("deployment_target")),
        "summary": (
            "Relaytic will keep benchmark competitiveness and deployment readiness as separate judgments."
            if benchmark_expected
            else "Relaytic will still preserve a benchmark-vs-deploy split even when the prompt is not benchmark-first."
        ),
    }
    deployment_readiness_report = {
        "schema_version": DEPLOYMENT_READINESS_REPORT_SCHEMA_VERSION,
        "generated_at": generated_at,
        "status": "ok" if decision_bundle else "not_evaluated_yet",
        "readiness_state": deployment_readiness,
        "deployability": _clean_text(deployability_assessment.get("deployability")),
        "recommended_action": _clean_text(deployability_assessment.get("recommended_action"))
        or _clean_text(decision_constraint_report.get("recommended_action"))
        or _clean_text(review_gate_state.get("recommended_action")),
        "review_gate_open": review_gate_state.get("gate_open"),
        "primary_constraint_kind": _clean_text(decision_constraint_report.get("primary_constraint_kind")),
        "summary": _deployment_summary(
            deployment_readiness=deployment_readiness,
            primary_constraint_kind=_clean_text(decision_constraint_report.get("primary_constraint_kind")),
        ),
    }
    benchmark_vs_deploy_report = {
        "schema_version": BENCHMARK_VS_DEPLOY_REPORT_SCHEMA_VERSION,
        "generated_at": generated_at,
        "status": "ok" if benchmark_bundle or decision_bundle else "not_evaluated_yet",
        "benchmark_status": benchmark_status,
        "benchmark_recommended_action": _clean_text(benchmark_parity_report.get("recommended_action")),
        "deployment_readiness": deployment_readiness,
        "deployment_recommended_action": deployment_readiness_report["recommended_action"],
        "split_detected": split_detected,
        "summary": _benchmark_vs_deploy_summary(
            benchmark_status=benchmark_status,
            deployment_readiness=deployment_readiness,
            split_detected=split_detected,
        ),
    }
    dataset_semantics_audit = {
        "schema_version": DATASET_SEMANTICS_AUDIT_SCHEMA_VERSION,
        "generated_at": generated_at,
        "status": "ok" if dataset_profile else "partial",
        "data_mode": _clean_text(dataset_profile.get("data_mode")) or task_profile_contract["data_mode"],
        "timestamp_column": _clean_text(dataset_profile.get("timestamp_column")),
        "row_count": int(dataset_profile.get("row_count", 0) or task_profile_contract["row_count"] or 0),
        "column_count": int(dataset_profile.get("column_count", 0) or 0),
        "target_column": task_profile_contract["target_column"],
        "multiclass_string_labels_preserved": bool(
            task_type == "multiclass_classification" and _has_non_numeric_labels(task_profile_contract["class_balance"])
        ),
        "labeled_target_detected": bool(is_classification_task(task_type) and class_count >= 2),
        "summary": _dataset_audit_summary(
            data_mode=_clean_text(dataset_profile.get("data_mode")) or task_profile_contract["data_mode"],
            timestamp_column=_clean_text(dataset_profile.get("timestamp_column")),
            task_type=task_type,
        ),
    }
    split_diagnostics_report = _build_split_diagnostics_report(
        generated_at=generated_at,
        data_path=data_path,
        task_profile_contract=task_profile_contract,
        plan=plan,
        dataset_profile=dataset_profile,
    )
    temporal_fold_health = _build_temporal_fold_health(
        generated_at=generated_at,
        split_diagnostics_report=split_diagnostics_report,
        task_profile_contract=task_profile_contract,
    )
    metric_materialization_audit = _build_metric_materialization_audit(
        generated_at=generated_at,
        execution_summary=execution_summary,
        reference_approach_matrix=reference_approach_matrix,
        optimization_objective_contract=optimization_objective_contract,
    )
    objective_alignment_report = _build_objective_alignment_report(
        generated_at=generated_at,
        optimization_objective_contract=optimization_objective_contract,
        metric_materialization_audit=metric_materialization_audit,
        split_diagnostics_report=split_diagnostics_report,
        temporal_fold_health=temporal_fold_health,
    )
    benchmark_truth_precheck = _build_benchmark_truth_precheck(
        generated_at=generated_at,
        metric_materialization_audit=metric_materialization_audit,
        temporal_fold_health=temporal_fold_health,
        objective_alignment_report=objective_alignment_report,
        reference_approach_matrix=reference_approach_matrix,
    )
    aml_domain_contract = _build_aml_domain_contract(
        generated_at=generated_at,
        run_brief=run_brief,
        task_brief=task_brief,
        domain_brief=domain_brief,
        task_profile_contract=task_profile_contract,
        target_semantics_report=target_semantics_report,
    )
    aml_case_ontology = _build_aml_case_ontology(
        generated_at=generated_at,
        aml_domain_contract=aml_domain_contract,
        run_brief=run_brief,
        task_brief=task_brief,
        domain_brief=domain_brief,
    )
    aml_review_budget_contract = _build_aml_review_budget_contract(
        generated_at=generated_at,
        aml_domain_contract=aml_domain_contract,
        metric_contract=metric_contract,
        optimization_objective_contract=optimization_objective_contract,
    )
    aml_claim_scope = _build_aml_claim_scope(
        generated_at=generated_at,
        aml_domain_contract=aml_domain_contract,
        benchmark_mode_report=benchmark_mode_report,
        benchmark_truth_precheck=benchmark_truth_precheck,
    )
    return {
        "task_profile_contract": task_profile_contract,
        "target_semantics_report": target_semantics_report,
        "metric_contract": metric_contract,
        "benchmark_mode_report": benchmark_mode_report,
        "deployment_readiness_report": deployment_readiness_report,
        "benchmark_vs_deploy_report": benchmark_vs_deploy_report,
        "dataset_semantics_audit": dataset_semantics_audit,
        "optimization_objective_contract": optimization_objective_contract,
        "objective_alignment_report": objective_alignment_report,
        "split_diagnostics_report": split_diagnostics_report,
        "temporal_fold_health": temporal_fold_health,
        "metric_materialization_audit": metric_materialization_audit,
        "benchmark_truth_precheck": benchmark_truth_precheck,
        "aml_domain_contract": aml_domain_contract,
        "aml_case_ontology": aml_case_ontology,
        "aml_review_budget_contract": aml_review_budget_contract,
        "aml_claim_scope": aml_claim_scope,
    }


def infer_benchmark_expected(*, run_brief: dict[str, Any], task_brief: dict[str, Any]) -> bool:
    """Infer whether the operator explicitly asked for benchmark comparison."""
    corpus = " ".join(
        [
            str(run_brief.get("objective", "")),
            str(run_brief.get("success_criteria", "")),
            str(task_brief.get("problem_statement", "")),
            str(task_brief.get("success_criteria", "")),
        ]
    ).lower()
    return any(token in corpus for token in ("benchmark", "baseline", "reference", "parity", "sota", "state of the art"))


def _build_aml_domain_contract(
    *,
    generated_at: str,
    run_brief: dict[str, Any],
    task_brief: dict[str, Any],
    domain_brief: dict[str, Any],
    task_profile_contract: dict[str, Any],
    target_semantics_report: dict[str, Any],
) -> dict[str, Any]:
    corpus = _aml_domain_corpus(
        run_brief=run_brief,
        task_brief=task_brief,
        domain_brief=domain_brief,
        task_profile_contract=task_profile_contract,
    )
    aml_active = _contains_aml_signal(corpus)
    target_level = _infer_aml_target_level(corpus=corpus)
    domain_focus = _infer_aml_domain_focus(corpus=corpus)
    review_budget_relevant = aml_active
    business_goal = _infer_aml_business_goal(corpus=corpus)
    target_column = _clean_text(task_profile_contract.get("target_column"))
    if not aml_active:
        return {
            "schema_version": AML_DOMAIN_CONTRACT_SCHEMA_VERSION,
            "generated_at": generated_at,
            "status": "not_applicable",
            "aml_active": False,
            "domain_family": "generic_structured_data",
            "domain_focus": "not_applicable",
            "target_level": "not_applicable",
            "review_budget_relevant": False,
            "business_goal": "standard_model_quality",
            "target_column": target_column,
            "task_type": _clean_text(task_profile_contract.get("task_type")),
            "problem_posture": _clean_text(task_profile_contract.get("problem_posture")),
            "summary": "AML posture is inactive for this run; Relaytic stays on the generic structured-data contract.",
        }
    return {
        "schema_version": AML_DOMAIN_CONTRACT_SCHEMA_VERSION,
        "generated_at": generated_at,
        "status": "active",
        "aml_active": True,
        "domain_family": "aml_financial_crime",
        "domain_focus": domain_focus,
        "target_level": target_level,
        "review_budget_relevant": review_budget_relevant,
        "business_goal": business_goal,
        "target_column": target_column,
        "task_type": _clean_text(task_profile_contract.get("task_type")),
        "problem_posture": _clean_text(task_profile_contract.get("problem_posture")),
        "target_semantics": _clean_text(target_semantics_report.get("target_semantics")),
        "summary": (
            f"Relaytic-AML activated `{domain_focus}` posture at `{target_level}` level and will favor alert quality, "
            "review burden, and case usefulness over metric-only reporting."
        ),
    }


def _build_aml_case_ontology(
    *,
    generated_at: str,
    aml_domain_contract: dict[str, Any],
    run_brief: dict[str, Any],
    task_brief: dict[str, Any],
    domain_brief: dict[str, Any],
) -> dict[str, Any]:
    aml_active = bool(aml_domain_contract.get("aml_active"))
    corpus = " ".join(
        [
            str(run_brief.get("objective", "")),
            str(run_brief.get("success_criteria", "")),
            str(task_brief.get("problem_statement", "")),
            str(task_brief.get("success_criteria", "")),
            str(domain_brief.get("summary", "")),
            str(domain_brief.get("target_meaning", "")),
        ]
    ).lower()
    if not aml_active:
        return {
            "schema_version": AML_CASE_ONTOLOGY_SCHEMA_VERSION,
            "generated_at": generated_at,
            "status": "not_applicable",
            "entity_types": [],
            "case_levels": [],
            "typology_candidates": [],
            "reasoning_scope": "generic_structured_data",
            "summary": "No AML case ontology is active on this run.",
        }
    entity_types = _infer_aml_entity_types(corpus=corpus, target_level=_clean_text(aml_domain_contract.get("target_level")))
    case_levels = _infer_aml_case_levels(target_level=_clean_text(aml_domain_contract.get("target_level")))
    typology_candidates = _infer_aml_typology_candidates(corpus=corpus, domain_focus=_clean_text(aml_domain_contract.get("domain_focus")))
    return {
        "schema_version": AML_CASE_ONTOLOGY_SCHEMA_VERSION,
        "generated_at": generated_at,
        "status": "active",
        "entity_types": entity_types,
        "case_levels": case_levels,
        "typology_candidates": typology_candidates,
        "reasoning_scope": "entity_graph_and_casework_ready",
        "summary": (
            f"Relaytic-AML framed this run around entity types `{', '.join(entity_types)}` with typology candidates "
            f"`{', '.join(typology_candidates)}`."
        ),
    }


def _build_aml_review_budget_contract(
    *,
    generated_at: str,
    aml_domain_contract: dict[str, Any],
    metric_contract: dict[str, Any],
    optimization_objective_contract: dict[str, Any],
) -> dict[str, Any]:
    aml_active = bool(aml_domain_contract.get("aml_active"))
    review_budget_relevant = bool(aml_domain_contract.get("review_budget_relevant"))
    if not aml_active:
        return {
            "schema_version": AML_REVIEW_BUDGET_CONTRACT_SCHEMA_VERSION,
            "generated_at": generated_at,
            "status": "not_applicable",
            "review_budget_relevant": False,
            "priority": "not_applicable",
            "decision_objective": "standard_metric_optimization",
            "recommended_metrics": [],
            "analyst_capacity_assumption": "not_applicable",
            "recommended_next_action": None,
            "summary": "Review-budget posture is inactive because this run is not under the AML contract.",
        }
    selection_metric = _clean_text(optimization_objective_contract.get("family_selection_metric")) or _clean_text(metric_contract.get("selection_metric"))
    benchmark_metric = _clean_text(optimization_objective_contract.get("benchmark_comparison_metric")) or _clean_text(metric_contract.get("benchmark_comparison_metric"))
    return {
        "schema_version": AML_REVIEW_BUDGET_CONTRACT_SCHEMA_VERSION,
        "generated_at": generated_at,
        "status": "active",
        "review_budget_relevant": review_budget_relevant,
        "priority": "primary",
        "decision_objective": "maximize_precision_at_review_budget",
        "recommended_metrics": [
            "precision_at_k",
            "recall_at_review_budget",
            "pr_auc",
            benchmark_metric or "pr_auc",
        ],
        "analyst_capacity_assumption": "bounded_manual_review",
        "selection_metric": selection_metric,
        "recommended_next_action": "optimize_review_queue",
        "summary": (
            f"Relaytic-AML keeps `{selection_metric or 'unknown'}` for model selection but elevates review-budget decisions "
            "toward precision-at-k, recall-at-review-budget, and case usefulness."
        ),
    }


def _build_aml_claim_scope(
    *,
    generated_at: str,
    aml_domain_contract: dict[str, Any],
    benchmark_mode_report: dict[str, Any],
    benchmark_truth_precheck: dict[str, Any],
) -> dict[str, Any]:
    aml_active = bool(aml_domain_contract.get("aml_active"))
    if not aml_active:
        return {
            "schema_version": AML_CLAIM_SCOPE_SCHEMA_VERSION,
            "generated_at": generated_at,
            "status": "not_applicable",
            "aml_active": False,
            "benchmark_pack_family": "generic_supporting_pack",
            "claim_scope": "generic_supporting_only",
            "public_claim_ready": bool(benchmark_truth_precheck.get("safe_to_rank")),
            "summary": "AML-specific public claim scope is inactive for this run.",
        }
    benchmark_expected = bool(benchmark_mode_report.get("benchmark_expected"))
    public_claim_ready = False
    return {
        "schema_version": AML_CLAIM_SCOPE_SCHEMA_VERSION,
        "generated_at": generated_at,
        "status": "active",
        "aml_active": True,
        "benchmark_pack_family": "aml_flagship_pending",
        "claim_scope": "generic_supporting_only_until_15r",
        "public_claim_ready": public_claim_ready,
        "benchmark_expected": benchmark_expected,
        "summary": (
            "Relaytic-AML can use generic benchmark packs as supporting evidence, but flagship AML public claims stay "
            "gated until the dedicated AML benchmark and holdout pack are shipped."
        ),
    }


def _aml_domain_corpus(
    *,
    run_brief: dict[str, Any],
    task_brief: dict[str, Any],
    domain_brief: dict[str, Any],
    task_profile_contract: dict[str, Any],
) -> str:
    return " ".join(
        [
            str(run_brief.get("objective", "")),
            str(run_brief.get("success_criteria", "")),
            str(task_brief.get("problem_statement", "")),
            str(task_brief.get("success_criteria", "")),
            str(task_brief.get("target_column", "")),
            str(domain_brief.get("summary", "")),
            str(domain_brief.get("target_meaning", "")),
            str(domain_brief.get("system_name", "")),
            str(task_profile_contract.get("target_column", "")),
            str(task_profile_contract.get("problem_posture", "")),
        ]
    ).lower()


def _contains_aml_signal(corpus: str) -> bool:
    tokens = (
        "aml",
        "anti-money laundering",
        "money laundering",
        "laundering",
        "financial crime",
        "payment fraud",
        "payment-fraud",
        "paysim",
        "elliptic",
        "illicit transaction",
        "fraud",
        "chargeback",
        "charge back",
        "suspicious activity",
        "transaction monitoring",
        "analyst review",
        "review queue",
        "case packet",
    )
    return any(token in corpus for token in tokens)


def _infer_aml_domain_focus(*, corpus: str) -> str:
    if any(token in corpus for token in ("chargeback", "charge back", "payment fraud", "payment-fraud", "merchant fraud", "paysim")):
        return "payment_fraud"
    if any(token in corpus for token in ("review queue", "analyst review", "case packet", "triage")):
        return "analyst_review"
    if any(token in corpus for token in ("transaction monitoring", "suspicious transaction", "alert queue", "elliptic", "bitcoin")):
        return "transaction_monitoring"
    if any(token in corpus for token in ("aml", "anti-money laundering", "money laundering", "financial crime", "suspicious activity")):
        return "aml_investigation"
    return "aml_financial_crime"


def _infer_aml_target_level(*, corpus: str) -> str:
    if any(token in corpus for token in ("subgraph", "multi-hop", "network", "community", "typology motif")):
        return "subgraph"
    if any(token in corpus for token in ("entity", "account", "merchant", "customer", "wallet", "counterparty", "device")):
        return "entity"
    if any(token in corpus for token in ("case", "investigation", "review queue", "analyst review", "case packet")):
        return "case"
    return "transaction"


def _infer_aml_business_goal(corpus: str) -> str:
    if any(token in corpus for token in ("review queue", "analyst review", "case packet", "triage")):
        return "analyst_triage"
    if any(token in corpus for token in ("chargeback", "payment fraud", "fraud")):
        return "false_positive_reduction"
    return "suspicious_activity_detection"


def _infer_aml_entity_types(*, corpus: str, target_level: str | None) -> list[str]:
    entity_types: list[str] = []
    for token, label in (
        ("transaction", "transaction"),
        ("account", "account"),
        ("customer", "customer"),
        ("merchant", "merchant"),
        ("device", "device"),
        ("card", "card"),
        ("wallet", "wallet"),
        ("counterparty", "counterparty"),
        ("ip", "ip"),
    ):
        if token in corpus:
            entity_types.append(label)
    if not entity_types:
        if target_level == "entity":
            entity_types = ["account", "counterparty", "transaction"]
        elif target_level == "case":
            entity_types = ["case", "transaction", "account"]
        else:
            entity_types = ["transaction", "account", "counterparty"]
    return entity_types


def _infer_aml_case_levels(*, target_level: str | None) -> list[str]:
    if target_level == "subgraph":
        return ["transaction", "entity", "subgraph", "case"]
    if target_level == "entity":
        return ["transaction", "entity", "case"]
    if target_level == "case":
        return ["alert", "case"]
    return ["transaction", "alert", "case"]


def _infer_aml_typology_candidates(*, corpus: str, domain_focus: str | None) -> list[str]:
    typologies: list[str] = []
    for token, label in (
        ("smurf", "smurfing"),
        ("layer", "layering"),
        ("funnel", "funnel_accounts"),
        ("peel", "peel_chain"),
        ("bitcoin", "peel_chain"),
        ("elliptic", "peel_chain"),
        ("chargeback", "chargeback_abuse"),
        ("account takeover", "account_takeover"),
        ("suspicious activity", "suspicious_activity_pattern"),
    ):
        if token in corpus and label not in typologies:
            typologies.append(label)
    if not typologies:
        if domain_focus == "payment_fraud":
            typologies = ["chargeback_abuse", "account_takeover", "merchant_abuse"]
        else:
            typologies = ["suspicious_activity_pattern", "money_laundering_pattern", "alert_triad_priority"]
    return typologies


def _deployment_readiness_status(
    *,
    deployability_assessment: dict[str, Any],
    review_gate_state: dict[str, Any],
    decision_constraint_report: dict[str, Any],
) -> str:
    deployability = _clean_text(deployability_assessment.get("deployability"))
    if deployability:
        return deployability
    if review_gate_state:
        if review_gate_state.get("gate_open") is True:
            return "conditional"
        if review_gate_state.get("gate_open") is False:
            return "blocked"
    if decision_constraint_report:
        if _clean_text(decision_constraint_report.get("primary_constraint_kind")):
            return "conditional"
    return "not_evaluated_yet"


def _benchmark_deploy_split_detected(*, benchmark_status: str, deployment_readiness: str) -> bool:
    competitive = benchmark_is_reference_competitive(benchmark_status, include_near=True)
    return competitive and deployment_readiness in {"conditional", "blocked", "not_evaluated_yet"}


def _benchmark_comparison_metric(
    *,
    task_type: str,
    primary_metric: str | None,
    selection_metric: str | None,
    rare_event_supervised: bool,
) -> str:
    if task_type == "regression":
        return selection_metric or primary_metric or "mae"
    if task_type == "multiclass_classification":
        return selection_metric or "f1"
    if rare_event_supervised or task_type in {"fraud_detection", "anomaly_detection", "binary_classification"}:
        return "pr_auc"
    return selection_metric or primary_metric or "f1"


def _deployment_primary_metric(*, task_type: str, primary_metric: str | None, rare_event_supervised: bool) -> str:
    if primary_metric:
        return primary_metric
    if task_type == "regression":
        return "mae"
    if rare_event_supervised or task_type in {"fraud_detection", "anomaly_detection"}:
        return "pr_auc"
    if task_type == "multiclass_classification":
        return "f1"
    return "f1"


def _infer_target_semantics(*, task_family: str, class_count: int, rare_event_supervised: bool) -> str:
    if task_family != "classification":
        return "continuous_signal"
    if rare_event_supervised and class_count <= 2:
        return "rare_event_supervised_label"
    if class_count <= 2:
        return "binary_labeled_class"
    return "multiclass_labeled_class"


def _infer_problem_posture(*, task_type: str, task_family: str, class_count: int, rare_event_supervised: bool) -> str:
    if task_type == "anomaly_detection":
        return "anomaly_detection"
    if task_family != "classification":
        return "regression"
    if rare_event_supervised and class_count <= 2:
        return "rare_event_supervised"
    return "standard_classification"


def _why_not_anomaly_detection(
    *,
    task_type: str,
    task_family: str,
    class_count: int,
    target_semantics: str,
    rare_event_supervised: bool,
) -> str | None:
    if task_type == "anomaly_detection":
        return None
    if task_family != "classification" or class_count < 2:
        return "Relaytic did not choose anomaly detection because the target behaves like a continuous supervised signal."
    if rare_event_supervised:
        return (
            "Relaytic kept this as supervised rare-event classification because the dataset contains explicit labeled outcomes. "
            "True anomaly detection is reserved for unlabeled or explicitly forced anomaly workflows."
        )
    if target_semantics in {"binary_labeled_class", "multiclass_labeled_class"}:
        return (
            "Relaytic kept this as supervised classification because the target already exposes labeled outcome states. "
            "Anomaly detection would discard that supervision signal."
        )
    return None


def _target_semantics_summary(*, task_type: str, target_semantics: str, problem_posture: str, class_count: int) -> str:
    if task_type == "regression":
        return "Relaytic treated the target as a continuous supervised signal."
    return (
        f"Relaytic treated the target as `{target_semantics}` with posture `{problem_posture}` "
        f"across {class_count} observed target states."
    )


def _deployment_summary(*, deployment_readiness: str, primary_constraint_kind: str | None) -> str:
    if deployment_readiness == "not_evaluated_yet":
        return "Deployment readiness has not been evaluated yet for this run."
    if primary_constraint_kind:
        return (
            f"Deployment readiness is `{deployment_readiness}` because the current primary constraint is "
            f"`{primary_constraint_kind}`."
        )
    return f"Deployment readiness is currently `{deployment_readiness}`."


def _benchmark_vs_deploy_summary(*, benchmark_status: str, deployment_readiness: str, split_detected: bool) -> str:
    if split_detected:
        return (
            f"Relaytic keeps benchmark competitiveness `{benchmark_status}` separate from deployment readiness "
            f"`{deployment_readiness}` so offline benchmark wins do not masquerade as deploy-ready decisions."
        )
    return (
        f"Benchmark status is `{benchmark_status}` and deployment readiness is `{deployment_readiness}` under the "
        "same canonical task contract."
    )


def _dataset_audit_summary(*, data_mode: str | None, timestamp_column: str | None, task_type: str) -> str:
    if data_mode == "time_series":
        return (
            f"Relaytic preserved time-aware semantics with timestamp column `{timestamp_column or 'unknown'}` "
            f"for task type `{task_type}`."
        )
    return f"Relaytic audited the dataset as `{data_mode or 'unknown'}` for task type `{task_type}`."


def _build_optimization_objective_contract(
    *,
    generated_at: str,
    task_type: str,
    task_family: str,
    data_mode: str | None,
    split_strategy: str | None,
    selection_metric: str | None,
    primary_metric: str | None,
    benchmark_comparison_metric: str | None,
    deployment_primary_metric: str | None,
    threshold_policy: str | None,
    rare_event_supervised: bool,
) -> dict[str, Any]:
    calibration_metric = _calibration_metric(
        task_type=task_type,
        task_family=task_family,
        selection_metric=selection_metric,
        primary_metric=primary_metric,
    )
    threshold_metric = _threshold_metric(
        task_type=task_type,
        primary_metric=primary_metric,
        benchmark_comparison_metric=benchmark_comparison_metric,
        rare_event_supervised=rare_event_supervised,
    )
    distinct_metrics = {
        item
        for item in (
            _clean_text(selection_metric),
            _clean_text(calibration_metric),
            _clean_text(threshold_metric),
            _clean_text(benchmark_comparison_metric),
            _clean_text(deployment_primary_metric),
        )
        if item
    }
    explicit_metric_split = len(distinct_metrics) > 1
    summary = (
        f"Relaytic will select families on `{selection_metric or 'unknown'}`, "
        f"calibrate on `{calibration_metric or 'not_applicable'}`, "
        f"tune thresholds on `{threshold_metric or 'not_applicable'}`, "
        f"compare benchmarks on `{benchmark_comparison_metric or 'unknown'}`, "
        f"and judge deployment on `{deployment_primary_metric or 'unknown'}`."
    )
    if explicit_metric_split:
        summary += " These metrics are intentionally separated rather than silently conflated."
    return {
        "schema_version": OPTIMIZATION_OBJECTIVE_CONTRACT_SCHEMA_VERSION,
        "generated_at": generated_at,
        "status": "ok" if selection_metric or benchmark_comparison_metric or deployment_primary_metric else "partial",
        "task_type": task_type,
        "task_family": task_family,
        "data_mode": data_mode,
        "split_strategy": split_strategy,
        "family_selection_metric": selection_metric,
        "calibration_metric": calibration_metric,
        "threshold_metric": threshold_metric,
        "benchmark_comparison_metric": benchmark_comparison_metric,
        "deployment_decision_metric": deployment_primary_metric,
        "threshold_policy": threshold_policy,
        "explicit_metric_split": explicit_metric_split,
        "summary": summary,
    }


def _build_split_diagnostics_report(
    *,
    generated_at: str,
    data_path: str | Path | None,
    task_profile_contract: dict[str, Any],
    plan: dict[str, Any],
    dataset_profile: dict[str, Any],
) -> dict[str, Any]:
    target_column = _clean_text(task_profile_contract.get("target_column")) or _clean_text(plan.get("target_column"))
    task_type = _clean_text(task_profile_contract.get("task_type")) or _clean_text(plan.get("task_type")) or "unknown"
    data_mode = _clean_text(task_profile_contract.get("data_mode")) or _clean_text(plan.get("data_mode")) or _clean_text(dataset_profile.get("data_mode"))
    timestamp_column = _clean_text(task_profile_contract.get("timestamp_column")) or _clean_text(plan.get("timestamp_column")) or _clean_text(dataset_profile.get("timestamp_column"))
    fallback = {
        "schema_version": SPLIT_DIAGNOSTICS_REPORT_SCHEMA_VERSION,
        "generated_at": generated_at,
        "status": "partial",
        "task_type": task_type,
        "data_mode": data_mode,
        "timestamp_column": timestamp_column,
        "split_strategy": _clean_text(task_profile_contract.get("recommended_split_strategy")) or _clean_text(plan.get("split_strategy")),
        "target_column": target_column,
        "train_size": None,
        "validation_size": None,
        "test_size": None,
        "train_class_count": None,
        "validation_class_count": None,
        "test_class_count": None,
        "positive_label": _clean_text(task_profile_contract.get("positive_class_label")),
        "train_positive_count": None,
        "validation_positive_count": None,
        "test_positive_count": None,
        "zero_positive_validation": None,
        "zero_positive_test": None,
        "reason_codes": [],
        "summary": "Relaytic could not compute split diagnostics because the dataset path or target column is unavailable.",
    }
    if not data_path or not target_column:
        return fallback
    try:
        frame = load_tabular_data(str(data_path)).frame.copy()
    except Exception as exc:
        fallback["summary"] = f"Relaytic could not load the dataset for split diagnostics: {exc}."
        fallback["reason_codes"] = ["data_load_failed"]
        return fallback
    if target_column not in frame.columns:
        fallback["summary"] = f"Relaytic could not compute split diagnostics because target `{target_column}` was not found."
        fallback["reason_codes"] = ["target_missing"]
        return fallback
    try:
        split = build_train_validation_test_split(
            n_rows=len(frame),
            data_mode=data_mode or "steady_state",
            task_type=task_type,
            stratify_labels=frame[target_column] if is_classification_task(task_type) else None,
        )
    except Exception as exc:
        fallback["status"] = "blocked"
        fallback["summary"] = f"Relaytic blocked split diagnostics because it could not build a safe split: {exc}."
        fallback["reason_codes"] = ["split_build_failed"]
        return fallback

    train = frame.iloc[split.train_indices].reset_index(drop=True)
    validation = frame.iloc[split.validation_indices].reset_index(drop=True)
    test = frame.iloc[split.test_indices].reset_index(drop=True)
    reason_codes: list[str] = []
    positive_label = _clean_text(task_profile_contract.get("positive_class_label")) or _infer_positive_label(frame[target_column])
    train_class_count = validation_class_count = test_class_count = None
    train_positive_count = validation_positive_count = test_positive_count = None
    zero_positive_validation = zero_positive_test = None
    if is_classification_task(task_type):
        train_class_count = int(train[target_column].astype(str).nunique(dropna=False))
        validation_class_count = int(validation[target_column].astype(str).nunique(dropna=False))
        test_class_count = int(test[target_column].astype(str).nunique(dropna=False))
        if positive_label:
            train_positive_count = int((train[target_column].astype(str) == str(positive_label)).sum())
            validation_positive_count = int((validation[target_column].astype(str) == str(positive_label)).sum())
            test_positive_count = int((test[target_column].astype(str) == str(positive_label)).sum())
            zero_positive_validation = validation_positive_count == 0
            zero_positive_test = test_positive_count == 0
            if data_mode == "time_series" and zero_positive_validation:
                reason_codes.append("temporal_validation_missing_positive")
            if data_mode == "time_series" and zero_positive_test:
                reason_codes.append("temporal_test_missing_positive")
    status = "ok" if not reason_codes else "blocked"
    summary = (
        f"Relaytic built `{split.strategy}` with train/validation/test sizes "
        f"`{len(train)}/{len(validation)}/{len(test)}`."
    )
    if reason_codes:
        summary += " Split truth is blocked because " + ", ".join(reason_codes).replace("_", " ") + "."
    elif data_mode == "time_series" and is_classification_task(task_type):
        summary += (
            f" Temporal validation/test positive counts are "
            f"`{validation_positive_count if validation_positive_count is not None else 'n/a'}` and "
            f"`{test_positive_count if test_positive_count is not None else 'n/a'}`."
        )
    return {
        "schema_version": SPLIT_DIAGNOSTICS_REPORT_SCHEMA_VERSION,
        "generated_at": generated_at,
        "status": status,
        "task_type": task_type,
        "data_mode": data_mode,
        "timestamp_column": timestamp_column,
        "split_strategy": split.strategy,
        "target_column": target_column,
        "train_size": int(len(train)),
        "validation_size": int(len(validation)),
        "test_size": int(len(test)),
        "train_class_count": train_class_count,
        "validation_class_count": validation_class_count,
        "test_class_count": test_class_count,
        "positive_label": positive_label,
        "train_positive_count": train_positive_count,
        "validation_positive_count": validation_positive_count,
        "test_positive_count": test_positive_count,
        "zero_positive_validation": zero_positive_validation,
        "zero_positive_test": zero_positive_test,
        "reason_codes": reason_codes,
        "summary": summary,
    }


def _build_temporal_fold_health(
    *,
    generated_at: str,
    split_diagnostics_report: dict[str, Any],
    task_profile_contract: dict[str, Any],
) -> dict[str, Any]:
    data_mode = _clean_text(split_diagnostics_report.get("data_mode")) or _clean_text(task_profile_contract.get("data_mode"))
    task_type = _clean_text(task_profile_contract.get("task_type"))
    if data_mode != "time_series" or not is_classification_task(task_type or ""):
        return {
            "schema_version": TEMPORAL_FOLD_HEALTH_SCHEMA_VERSION,
            "generated_at": generated_at,
            "status": "not_applicable",
            "reason_codes": [],
            "validation_positive_count": split_diagnostics_report.get("validation_positive_count"),
            "test_positive_count": split_diagnostics_report.get("test_positive_count"),
            "safe_for_benchmarking": True,
            "summary": "Temporal fold-health checks are not applicable for this run.",
        }
    validation_positive = split_diagnostics_report.get("validation_positive_count")
    test_positive = split_diagnostics_report.get("test_positive_count")
    reason_codes = [
        str(item)
        for item in split_diagnostics_report.get("reason_codes", [])
        if str(item).startswith("temporal_")
    ]
    safe = not reason_codes and validation_positive not in {None, 0} and test_positive not in {None, 0}
    return {
        "schema_version": TEMPORAL_FOLD_HEALTH_SCHEMA_VERSION,
        "generated_at": generated_at,
        "status": "ok" if safe else "blocked",
        "reason_codes": reason_codes or ([] if safe else ["temporal_fold_health_unavailable"]),
        "validation_positive_count": validation_positive,
        "test_positive_count": test_positive,
        "safe_for_benchmarking": safe,
        "summary": (
            "Temporal classification folds preserve positive events in validation and test."
            if safe
            else "Relaytic blocked temporal benchmark trust because validation or test lost positive events."
        ),
    }


def _build_metric_materialization_audit(
    *,
    generated_at: str,
    execution_summary: dict[str, Any],
    reference_approach_matrix: dict[str, Any],
    optimization_objective_contract: dict[str, Any],
) -> dict[str, Any]:
    execution_metrics = _collect_execution_metric_names(execution_summary)
    selection_metric = _clean_text(optimization_objective_contract.get("family_selection_metric"))
    calibration_metric = _clean_text(optimization_objective_contract.get("calibration_metric"))
    threshold_metric = _clean_text(optimization_objective_contract.get("threshold_metric"))
    benchmark_metric = _clean_text(optimization_objective_contract.get("benchmark_comparison_metric"))
    deployment_metric = _clean_text(optimization_objective_contract.get("deployment_decision_metric"))
    benchmark_rows_present = _benchmark_rows_materialize_metric(reference_approach_matrix, benchmark_metric)
    selection_present = selection_metric in execution_metrics if selection_metric else True
    calibration_present = calibration_metric in execution_metrics if calibration_metric else True
    threshold_present = threshold_metric in execution_metrics if threshold_metric else True
    benchmark_present = benchmark_metric in execution_metrics if benchmark_metric else False
    deployment_present = deployment_metric in execution_metrics if deployment_metric else False
    missing_metrics = [
        name
        for name, present in (
            (selection_metric, selection_present),
            (calibration_metric, calibration_present),
            (threshold_metric, threshold_present),
            (benchmark_metric, benchmark_present),
            (deployment_metric, deployment_present),
        )
        if name and not present
    ]
    status = "ok"
    if not benchmark_present:
        status = "fail"
    elif reference_approach_matrix and benchmark_rows_present is False:
        status = "fail"
    elif missing_metrics:
        status = "warning"
    return {
        "schema_version": METRIC_MATERIALIZATION_AUDIT_SCHEMA_VERSION,
        "generated_at": generated_at,
        "status": status,
        "available_execution_metrics": sorted(execution_metrics),
        "selection_metric_materialized": selection_present,
        "calibration_metric_materialized": calibration_present,
        "threshold_metric_materialized": threshold_present,
        "benchmark_metric_materialized_in_execution": benchmark_present,
        "benchmark_metric_materialized_in_benchmark_rows": benchmark_rows_present,
        "deployment_metric_materialized": deployment_present,
        "missing_metrics": missing_metrics,
        "summary": (
            f"Relaytic audited execution metrics against benchmark metric `{benchmark_metric or 'unknown'}`."
            if status == "ok"
            else f"Relaytic found objective/metric materialization gaps for `{benchmark_metric or 'unknown'}`."
        ),
    }


def _build_objective_alignment_report(
    *,
    generated_at: str,
    optimization_objective_contract: dict[str, Any],
    metric_materialization_audit: dict[str, Any],
    split_diagnostics_report: dict[str, Any],
    temporal_fold_health: dict[str, Any],
) -> dict[str, Any]:
    benchmark_metric = _clean_text(optimization_objective_contract.get("benchmark_comparison_metric"))
    selection_metric = _clean_text(optimization_objective_contract.get("family_selection_metric"))
    deployment_metric = _clean_text(optimization_objective_contract.get("deployment_decision_metric"))
    explicit_split = bool(optimization_objective_contract.get("explicit_metric_split"))
    blocked = metric_materialization_audit.get("status") == "fail" or temporal_fold_health.get("status") == "blocked"
    status = "blocked" if blocked else "ok"
    summary = (
        f"Relaytic selects families on `{selection_metric or 'unknown'}`, compares benchmark claims on `{benchmark_metric or 'unknown'}`, "
        f"and makes deployment decisions on `{deployment_metric or 'unknown'}`."
    )
    if explicit_split:
        summary += " The metric split is explicit rather than implicit."
    if split_diagnostics_report.get("status") == "blocked":
        summary += " Split diagnostics currently block trustworthy benchmark interpretation."
    return {
        "schema_version": OBJECTIVE_ALIGNMENT_REPORT_SCHEMA_VERSION,
        "generated_at": generated_at,
        "status": status,
        "selection_metric": selection_metric,
        "calibration_metric": _clean_text(optimization_objective_contract.get("calibration_metric")),
        "threshold_metric": _clean_text(optimization_objective_contract.get("threshold_metric")),
        "benchmark_comparison_metric": benchmark_metric,
        "deployment_decision_metric": deployment_metric,
        "explicit_metric_split": explicit_split,
        "benchmark_metric_materialized_in_execution": metric_materialization_audit.get("benchmark_metric_materialized_in_execution"),
        "benchmark_metric_materialized_in_benchmark_rows": metric_materialization_audit.get("benchmark_metric_materialized_in_benchmark_rows"),
        "split_status": _clean_text(split_diagnostics_report.get("status")),
        "temporal_fold_status": _clean_text(temporal_fold_health.get("status")),
        "summary": summary,
    }


def _build_benchmark_truth_precheck(
    *,
    generated_at: str,
    metric_materialization_audit: dict[str, Any],
    temporal_fold_health: dict[str, Any],
    objective_alignment_report: dict[str, Any],
    reference_approach_matrix: dict[str, Any],
) -> dict[str, Any]:
    reason_codes: list[str] = []
    if metric_materialization_audit.get("benchmark_metric_materialized_in_execution") is False:
        reason_codes.append("benchmark_metric_missing_in_execution")
    if reference_approach_matrix and metric_materialization_audit.get("benchmark_metric_materialized_in_benchmark_rows") is False:
        reason_codes.append("benchmark_metric_missing_in_reference_rows")
    if _clean_text(temporal_fold_health.get("status")) == "blocked":
        reason_codes.append("temporal_fold_health_blocked")
    safe_to_rank = not reason_codes
    return {
        "schema_version": BENCHMARK_TRUTH_PRECHECK_SCHEMA_VERSION,
        "generated_at": generated_at,
        "status": "ok" if safe_to_rank else "blocked",
        "safe_to_rank": safe_to_rank,
        "reason_codes": reason_codes,
        "objective_alignment_status": _clean_text(objective_alignment_report.get("status")),
        "summary": (
            "Relaytic considers the current benchmark objective and split truth safe to rank."
            if safe_to_rank
            else "Relaytic blocked benchmark ranking because the objective contract or split truth is not safe enough."
        ),
    }


def _calibration_metric(*, task_type: str, task_family: str, selection_metric: str | None, primary_metric: str | None) -> str | None:
    if task_family != "classification":
        return None
    if task_type == "multiclass_classification":
        return "log_loss"
    return "log_loss" if selection_metric not in {"log_loss", "brier_loss"} else selection_metric or primary_metric


def _threshold_metric(
    *,
    task_type: str,
    primary_metric: str | None,
    benchmark_comparison_metric: str | None,
    rare_event_supervised: bool,
) -> str | None:
    if task_type == "regression":
        return None
    if rare_event_supervised or task_type in {"fraud_detection", "anomaly_detection", "binary_classification"}:
        return benchmark_comparison_metric or primary_metric or "pr_auc"
    return primary_metric or benchmark_comparison_metric or "f1"


def _collect_execution_metric_names(execution_summary: dict[str, Any]) -> set[str]:
    names: set[str] = set()
    selected_metrics = execution_summary.get("selected_metrics", {})
    if isinstance(selected_metrics, dict):
        for split_metrics in selected_metrics.values():
            if isinstance(split_metrics, dict):
                for key, value in split_metrics.items():
                    if value is not None and str(key).strip():
                        names.add(str(key).strip())
    return names


def _benchmark_rows_materialize_metric(reference_approach_matrix: dict[str, Any], metric_name: str | None) -> bool | None:
    metric = _clean_text(metric_name)
    if not metric:
        return False
    if not reference_approach_matrix:
        return None
    relaytic_reference = dict(reference_approach_matrix.get("relaytic_reference", {}))
    if _metric_value_present(dict(relaytic_reference.get("test_metric", {})), metric):
        return True
    for row in reference_approach_matrix.get("references", []):
        if isinstance(row, dict) and _metric_value_present(dict(row.get("test_metric", {})), metric):
            return True
    return False


def _metric_value_present(metrics: dict[str, Any], metric_name: str) -> bool:
    if not isinstance(metrics, dict):
        return False
    value = metrics.get(metric_name)
    if value is None:
        alias = {
            "stability_adjusted_mae": "mae",
            "mae_per_latency": "mae",
        }.get(str(metric_name or "").strip().lower())
        if alias:
            value = metrics.get(alias)
    return value is not None


def _infer_positive_label(series: Any) -> str | None:
    try:
        counts = series.astype(str).value_counts(dropna=False)
    except Exception:
        return None
    if counts.empty:
        return None
    lowered = {str(index).strip().lower(): str(index) for index in counts.index}
    for candidate in ("1", "true", "yes", "positive", "fraud", "default", "failure", "occupied"):
        if candidate in lowered:
            return lowered[candidate]
    return str(counts.idxmin())


def _bundle_item(bundle: dict[str, Any], key: str) -> dict[str, Any]:
    value = bundle.get(key)
    return dict(value) if isinstance(value, dict) else {}


def _clean_text(value: Any) -> str | None:
    text = str(value).strip() if value is not None else ""
    return text or None


def _safe_float(value: Any) -> float | None:
    try:
        if value is None or value == "":
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def _has_non_numeric_labels(class_balance: dict[str, Any]) -> bool:
    for label in class_balance:
        try:
            float(label)
        except (TypeError, ValueError):
            return True
    return False


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()
