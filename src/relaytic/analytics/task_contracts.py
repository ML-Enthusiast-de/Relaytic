"""Canonical task-contract artifacts for modeling, benchmark, and review surfaces."""

from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any

from relaytic.core.json_utils import write_json

from .task_detection import is_classification_task


TASK_PROFILE_CONTRACT_SCHEMA_VERSION = "relaytic.task_profile_contract.v1"
TARGET_SEMANTICS_REPORT_SCHEMA_VERSION = "relaytic.target_semantics_report.v1"
METRIC_CONTRACT_SCHEMA_VERSION = "relaytic.metric_contract.v1"
BENCHMARK_MODE_REPORT_SCHEMA_VERSION = "relaytic.benchmark_mode_report.v1"
DEPLOYMENT_READINESS_REPORT_SCHEMA_VERSION = "relaytic.deployment_readiness_report.v1"
BENCHMARK_VS_DEPLOY_REPORT_SCHEMA_VERSION = "relaytic.benchmark_vs_deploy_report.v1"
DATASET_SEMANTICS_AUDIT_SCHEMA_VERSION = "relaytic.dataset_semantics_audit.v1"


TASK_CONTRACT_FILENAMES = {
    "task_profile_contract": "task_profile_contract.json",
    "target_semantics_report": "target_semantics_report.json",
    "metric_contract": "metric_contract.json",
    "benchmark_mode_report": "benchmark_mode_report.json",
    "deployment_readiness_report": "deployment_readiness_report.json",
    "benchmark_vs_deploy_report": "benchmark_vs_deploy_report.json",
    "dataset_semantics_audit": "dataset_semantics_audit.json",
}


def sync_task_contract_artifacts(
    run_dir: str | Path,
    *,
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
    dataset_profile = _bundle_item(investigation_bundle or {}, "dataset_profile")
    plan = _bundle_item(planning_bundle or {}, "plan")
    builder_handoff = dict(plan.get("builder_handoff") or {})
    task_profile = dict(plan.get("task_profile") or {})
    benchmark_bundle = benchmark_bundle or {}
    decision_bundle = decision_bundle or {}
    benchmark_parity_report = _bundle_item(benchmark_bundle, "benchmark_parity_report")
    decision_constraint_report = _bundle_item(decision_bundle, "decision_constraint_report")
    deployability_assessment = _bundle_item(decision_bundle, "deployability_assessment")
    review_gate_state = _bundle_item(decision_bundle, "review_gate_state")

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
    return {
        "task_profile_contract": task_profile_contract,
        "target_semantics_report": target_semantics_report,
        "metric_contract": metric_contract,
        "benchmark_mode_report": benchmark_mode_report,
        "deployment_readiness_report": deployment_readiness_report,
        "benchmark_vs_deploy_report": benchmark_vs_deploy_report,
        "dataset_semantics_audit": dataset_semantics_audit,
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
    competitive = benchmark_status in {"meets_or_beats_reference", "near_parity", "competitive"}
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
