"""Slice 08 lifecycle-governor pipeline."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from importlib import metadata, util
from pathlib import Path
from typing import Any

from relaytic.modeling import run_inference_from_artifacts

from .models import (
    CHAMPION_VS_CANDIDATE_SCHEMA_VERSION,
    PROMOTION_DECISION_SCHEMA_VERSION,
    RECALIBRATION_DECISION_SCHEMA_VERSION,
    RETRAIN_DECISION_SCHEMA_VERSION,
    ROLLBACK_DECISION_SCHEMA_VERSION,
    ChampionVsCandidate,
    LifecycleBundle,
    LifecycleControls,
    LifecycleTrace,
    PromotionDecision,
    RecalibrationDecision,
    RetrainDecision,
    RollbackDecision,
    build_lifecycle_controls_from_policy,
)


@dataclass(frozen=True)
class LifecycleRunResult:
    """Lifecycle artifacts plus human-readable review output."""

    bundle: LifecycleBundle
    review_markdown: str


class ChampionCandidateAgent:
    """Build the core lifecycle comparison frame."""

    def __init__(self, *, controls: LifecycleControls) -> None:
        self.controls = controls

    def run(
        self,
        *,
        run_dir: str | Path,
        data_path: str | None,
        context_bundle: dict[str, Any],
        planning_bundle: dict[str, Any],
        evidence_bundle: dict[str, Any],
        completion_bundle: dict[str, Any],
    ) -> ChampionVsCandidate:
        plan = _bundle_item(planning_bundle, "plan")
        execution_summary = dict(plan.get("execution_summary") or {})
        challenger_report = _bundle_item(evidence_bundle, "challenger_report")
        audit_report = _bundle_item(evidence_bundle, "audit_report")
        belief_update = _bundle_item(evidence_bundle, "belief_update")
        completion_decision = _bundle_item(completion_bundle, "completion_decision")
        task_brief = _bundle_item(context_bundle, "task_brief")

        primary_metric = (
            str(plan.get("primary_metric", "")).strip()
            or str(challenger_report.get("comparison_metric", "")).strip()
            or "unknown"
        )
        comparison = dict(challenger_report.get("comparison") or {})
        champion_model_family = str(execution_summary.get("selected_model_family", "")).strip() or None
        challenger_model_family = (
            str(comparison.get("challenger_model_family", "")).strip()
            or str(comparison.get("selected_model_family", "")).strip()
            or None
        )
        fresh_data_behavior = _fresh_data_behavior(run_dir=run_dir, data_path=data_path)

        return ChampionVsCandidate(
            schema_version=CHAMPION_VS_CANDIDATE_SCHEMA_VERSION,
            generated_at=_utc_now(),
            controls=self.controls,
            task_type=(
                str(plan.get("task_type", "")).strip()
                or str(task_brief.get("task_type_hint", "")).strip()
                or "unknown"
            ),
            primary_metric=primary_metric,
            champion_model_family=champion_model_family,
            challenger_model_family=challenger_model_family,
            champion_metric_value=_primary_metric_value(execution_summary=execution_summary, primary_metric=primary_metric),
            challenger_metric_value=_optional_float(comparison.get("challenger_metric_value")),
            challenger_delta_to_champion=_optional_float(challenger_report.get("delta_to_champion")),
            challenger_winner=str(challenger_report.get("winner", "champion")).strip() or "champion",
            fresh_data_behavior=fresh_data_behavior,
            completion_signal={
                "action": str(completion_decision.get("action", "")).strip() or None,
                "blocking_layer": str(completion_decision.get("blocking_layer", "")).strip() or None,
                "mandate_alignment": str(completion_decision.get("mandate_alignment", "")).strip() or None,
                "complete_for_mode": bool(completion_decision.get("complete_for_mode", False)),
            },
            evidence_signal={
                "provisional_recommendation": str(audit_report.get("provisional_recommendation", "")).strip() or None,
                "readiness_level": str(audit_report.get("readiness_level", "")).strip() or None,
                "recommended_action": str(belief_update.get("recommended_action", "")).strip() or None,
            },
            adapter_slots=_adapter_slots(),
            summary=_comparison_summary(
                champion_model_family=champion_model_family,
                challenger_model_family=challenger_model_family,
                primary_metric=primary_metric,
                challenger_winner=str(challenger_report.get("winner", "champion")).strip() or "champion",
                drift_score=float(((fresh_data_behavior.get("drift_summary") or {}).get("overall_drift_score", 0.0)) or 0.0),
            ),
            trace=LifecycleTrace(
                agent="champion_candidate_agent",
                operating_mode="deterministic_only",
                llm_used=False,
                llm_status="not_requested",
                deterministic_evidence=[
                    "planning.execution_summary",
                    "evidence.challenger_report",
                    "evidence.audit_report",
                    "completion.completion_decision",
                    "fresh_data_behavior",
                ],
            ),
        )


class LifecycleGovernorAgent:
    """Emit distinct recalibration, retraining, promotion, and rollback decisions."""

    def __init__(self, *, controls: LifecycleControls) -> None:
        self.controls = controls

    def run(
        self,
        *,
        comparison: ChampionVsCandidate,
    ) -> tuple[RecalibrationDecision, RetrainDecision, PromotionDecision, RollbackDecision]:
        fresh = dict(comparison.fresh_data_behavior or {})
        evaluation = dict(fresh.get("evaluation") or {})
        metrics = dict(evaluation.get("metrics") or {})
        drift_summary = dict(fresh.get("drift_summary") or {})
        ood_summary = dict(fresh.get("ood_summary") or {})
        completion_signal = dict(comparison.completion_signal or {})
        evidence_signal = dict(comparison.evidence_signal or {})

        drift_score = float(drift_summary.get("overall_drift_score", 0.0) or 0.0)
        ood_fraction = float(ood_summary.get("overall_ood_fraction", 0.0) or 0.0)
        evaluation_available = bool(evaluation.get("available", False))
        challenger_superior = comparison.challenger_winner == "challenger" and (comparison.challenger_delta_to_champion or 0.0) > 0.0
        mandate_alignment = str(completion_signal.get("mandate_alignment", "")).strip() or "unknown"
        completion_action = str(completion_signal.get("action", "")).strip()
        readiness = str(evidence_signal.get("readiness_level", "")).strip() or "unknown"

        severe_shift = drift_score >= 0.50 or ood_fraction >= 0.05
        moderate_shift = drift_score >= 0.30 or ood_fraction >= 0.02
        quality_state, quality_reasons = _quality_state(
            task_type=str(comparison.task_type),
            metrics=metrics,
            champion_metric_value=comparison.champion_metric_value,
            primary_metric=comparison.primary_metric,
            evaluation_available=evaluation_available,
        )

        recalibration_reasons: list[str] = []
        if (
            self.controls.recalibration_only_allowed
            and str(comparison.task_type) in {"binary_classification", "multiclass_classification", "fraud_detection", "anomaly_detection"}
            and quality_state in {"acceptable", "strong"}
            and not severe_shift
            and (
                moderate_shift
                or (
                    metrics.get("log_loss") is not None
                    and float(metrics.get("log_loss", 0.0)) >= 0.55
                )
            )
        ):
            recalibration_reasons.append("calibration_or_threshold_stale")
            if moderate_shift:
                recalibration_reasons.append("moderate_shift_without_route_failure")
            if metrics.get("log_loss") is not None and float(metrics.get("log_loss", 0.0)) >= 0.55:
                recalibration_reasons.append("log_loss_high_relative_to_discrimination")

        retrain_reasons: list[str] = []
        if severe_shift:
            retrain_reasons.append("fresh_data_shift_severe")
        if quality_state == "poor":
            retrain_reasons.append("fresh_data_quality_degraded")
        if completion_action == "retrain_candidate":
            retrain_reasons.append("completion_requested_retrain")
        if readiness == "weak":
            retrain_reasons.append("evidence_readiness_weak")
        if mandate_alignment == "conflict":
            retrain_reasons.append("mandate_alignment_conflict")

        promotion_reasons: list[str] = []
        if challenger_superior:
            promotion_reasons.append("challenger_outperformed_champion")
        if readiness == "weak":
            promotion_reasons.append("evidence_readiness_weak")
        if severe_shift:
            promotion_reasons.append("fresh_data_shift_severe")
        if mandate_alignment == "conflict":
            promotion_reasons.append("mandate_alignment_conflict")
        if completion_action in {"review_challenger", "continue_experimentation"}:
            promotion_reasons.append(f"completion_signal_{completion_action}")

        rollback_reasons: list[str] = []
        if self.controls.rollback_allowed and severe_shift and quality_state == "poor":
            rollback_reasons.extend(["current_route_not_trustworthy", "fresh_data_shift_severe"])
        if self.controls.rollback_allowed and mandate_alignment == "conflict":
            rollback_reasons.append("mandate_alignment_conflict")

        recalibration = RecalibrationDecision(
            schema_version=RECALIBRATION_DECISION_SCHEMA_VERSION,
            generated_at=_utc_now(),
            controls=self.controls,
            action="recalibrate" if recalibration_reasons else "no_recalibration",
            confidence=_confidence_band(reasons=recalibration_reasons, positive=bool(recalibration_reasons)),
            reason_codes=recalibration_reasons or ["calibration_hold_stable"],
            stale_calibration_signals=_calibration_signals(metrics=metrics, moderate_shift=moderate_shift),
            next_step="run_recalibration_pass" if recalibration_reasons else "keep_current_thresholds",
            summary=_recalibration_summary(action="recalibrate" if recalibration_reasons else "no_recalibration"),
            trace=LifecycleTrace(
                agent="recalibration_agent",
                operating_mode="deterministic_only",
                llm_used=False,
                llm_status="not_requested",
                deterministic_evidence=["fresh_data_evaluation", "fresh_data_shift", "completion_signal"],
            ),
        )

        retrain = RetrainDecision(
            schema_version=RETRAIN_DECISION_SCHEMA_VERSION,
            generated_at=_utc_now(),
            controls=self.controls,
            action="retrain" if retrain_reasons else "no_retrain",
            confidence=_confidence_band(reasons=retrain_reasons, positive=bool(retrain_reasons)),
            reason_codes=retrain_reasons or ["current_route_within_expected_envelope"],
            urgency="high" if severe_shift or mandate_alignment == "conflict" else "medium" if retrain_reasons else "low",
            next_step="schedule_refresh_training" if retrain_reasons else "continue_monitoring",
            summary=_retrain_summary(action="retrain" if retrain_reasons else "no_retrain", reasons=retrain_reasons),
            trace=LifecycleTrace(
                agent="retrain_agent",
                operating_mode="deterministic_only",
                llm_used=False,
                llm_status="not_requested",
                deterministic_evidence=["fresh_data_evaluation", "fresh_data_shift", "completion_signal", "evidence_readiness"],
                advisory_notes=quality_reasons,
            ),
        )

        if challenger_superior and not severe_shift and mandate_alignment != "conflict" and readiness in {"strong", "conditional"}:
            promotion_action = "promote_challenger"
            selected_model_family = comparison.challenger_model_family
            selected_source = "challenger"
            next_step = "promote_candidate_and_record_promotion"
        elif challenger_superior:
            promotion_action = "hold_promotion"
            selected_model_family = comparison.champion_model_family
            selected_source = "champion"
            next_step = "retest_candidate_under_fresh_conditions"
        else:
            promotion_action = "keep_current_champion"
            selected_model_family = comparison.champion_model_family
            selected_source = "champion"
            next_step = "keep_current_champion"

        promotion = PromotionDecision(
            schema_version=PROMOTION_DECISION_SCHEMA_VERSION,
            generated_at=_utc_now(),
            controls=self.controls,
            action=promotion_action,
            confidence=_confidence_band(reasons=promotion_reasons, positive=promotion_action == "promote_challenger"),
            reason_codes=promotion_reasons or ["challenger_not_superior"],
            selected_model_family=selected_model_family,
            selected_source=selected_source,
            next_step=next_step,
            summary=_promotion_summary(action=promotion_action, selected_model_family=selected_model_family),
            trace=LifecycleTrace(
                agent="promotion_agent",
                operating_mode="deterministic_only",
                llm_used=False,
                llm_status="not_requested",
                deterministic_evidence=["challenger_report", "completion_signal", "fresh_data_shift"],
            ),
        )

        rollback_target = comparison.champion_model_family if promotion_action == "promote_challenger" else None
        rollback = RollbackDecision(
            schema_version=ROLLBACK_DECISION_SCHEMA_VERSION,
            generated_at=_utc_now(),
            controls=self.controls,
            action="rollback_required" if rollback_reasons else "no_rollback",
            confidence=_confidence_band(reasons=rollback_reasons, positive=bool(rollback_reasons)),
            reason_codes=rollback_reasons or ["rollback_not_required"],
            rollback_target=rollback_target or "prior_stable_checkpoint",
            target_available=bool(rollback_target),
            next_step="prepare_rollback_to_last_stable_checkpoint" if rollback_reasons else "no_rollback_action",
            summary=_rollback_summary(action="rollback_required" if rollback_reasons else "no_rollback", target_available=bool(rollback_target)),
            trace=LifecycleTrace(
                agent="rollback_agent",
                operating_mode="deterministic_only",
                llm_used=False,
                llm_status="not_requested",
                deterministic_evidence=["fresh_data_shift", "fresh_data_evaluation", "promotion_decision", "completion_signal"],
            ),
        )
        return recalibration, retrain, promotion, rollback


def run_lifecycle_review(
    *,
    run_dir: str | Path,
    data_path: str | None,
    policy: dict[str, Any],
    mandate_bundle: dict[str, Any],
    context_bundle: dict[str, Any],
    investigation_bundle: dict[str, Any],
    planning_bundle: dict[str, Any],
    evidence_bundle: dict[str, Any],
    completion_bundle: dict[str, Any],
    config_path: str | None = None,
) -> LifecycleRunResult:
    """Run Slice 08 lifecycle review against the current run."""
    del mandate_bundle, investigation_bundle, config_path
    controls = build_lifecycle_controls_from_policy(policy)
    comparison_agent = ChampionCandidateAgent(controls=controls)
    governor = LifecycleGovernorAgent(controls=controls)
    comparison = comparison_agent.run(
        run_dir=run_dir,
        data_path=data_path,
        context_bundle=context_bundle,
        planning_bundle=planning_bundle,
        evidence_bundle=evidence_bundle,
        completion_bundle=completion_bundle,
    )
    recalibration, retrain, promotion, rollback = governor.run(comparison=comparison)
    bundle = LifecycleBundle(
        champion_vs_candidate=comparison,
        recalibration_decision=recalibration,
        retrain_decision=retrain,
        promotion_decision=promotion,
        rollback_decision=rollback,
    )
    return LifecycleRunResult(
        bundle=bundle,
        review_markdown=render_lifecycle_review_markdown(bundle.to_dict()),
    )


def render_lifecycle_review_markdown(bundle: dict[str, Any]) -> str:
    """Render a concise human-readable lifecycle review."""
    comparison = dict(bundle.get("champion_vs_candidate", {}))
    recalibration = dict(bundle.get("recalibration_decision", {}))
    retrain = dict(bundle.get("retrain_decision", {}))
    promotion = dict(bundle.get("promotion_decision", {}))
    rollback = dict(bundle.get("rollback_decision", {}))
    fresh = dict(comparison.get("fresh_data_behavior") or {})
    evaluation = dict(fresh.get("evaluation") or {})
    drift = dict(fresh.get("drift_summary") or {})
    ood = dict(fresh.get("ood_summary") or {})
    lines = [
        "# Relaytic Lifecycle Review",
        "",
        "## Comparison",
        f"- Task type: `{comparison.get('task_type') or 'unknown'}`",
        f"- Primary metric: `{comparison.get('primary_metric') or 'unknown'}`",
        f"- Champion: `{comparison.get('champion_model_family') or 'unknown'}`",
        f"- Challenger: `{comparison.get('challenger_model_family') or 'none'}`",
        f"- Challenger winner: `{comparison.get('challenger_winner') or 'unknown'}`",
        f"- Drift score: `{float(drift.get('overall_drift_score', 0.0)):.4f}`",
        f"- OOD fraction: `{float(ood.get('overall_ood_fraction', 0.0)):.4f}`",
    ]
    if evaluation:
        lines.extend(
            [
                "",
                "## Fresh Data Behavior",
                f"- Evaluation available: `{evaluation.get('available')}`",
                f"- Metrics: {_format_metric_block(dict(evaluation.get('metrics') or {}))}",
            ]
        )
    lines.extend(
        [
            "",
            "## Decisions",
            f"- Promotion: `{promotion.get('action') or 'unknown'}`",
            f"- Recalibration: `{recalibration.get('action') or 'unknown'}`",
            f"- Retrain: `{retrain.get('action') or 'unknown'}`",
            f"- Rollback: `{rollback.get('action') or 'unknown'}`",
            "",
            "## Summary",
            f"- {promotion.get('summary') or 'No promotion summary recorded.'}",
            f"- {recalibration.get('summary') or 'No recalibration summary recorded.'}",
            f"- {retrain.get('summary') or 'No retrain summary recorded.'}",
            f"- {rollback.get('summary') or 'No rollback summary recorded.'}",
        ]
    )
    return "\n".join(lines).strip() + "\n"


def _bundle_item(bundle: dict[str, Any], key: str) -> dict[str, Any]:
    value = bundle.get(key, {})
    return value if isinstance(value, dict) else {}


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _optional_float(value: Any) -> float | None:
    try:
        if value is None or value == "":
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def _primary_metric_value(*, execution_summary: dict[str, Any], primary_metric: str) -> float | None:
    metrics = dict(execution_summary.get("selected_metrics") or {})
    for split in ("test", "validation", "train"):
        split_metrics = dict(metrics.get(split) or {})
        value = _optional_float(split_metrics.get(primary_metric))
        if value is not None:
            return value
    return None


def _fresh_data_behavior(*, run_dir: str | Path, data_path: str | None) -> dict[str, Any]:
    if not data_path:
        return {
            "available": False,
            "status": "not_available",
            "reason": "No data path was available for lifecycle fresh-data review.",
            "evaluation": {"available": False, "reason": "No lifecycle data path resolved."},
            "drift_summary": {"overall_drift_score": 0.0},
            "ood_summary": {"overall_ood_fraction": 0.0},
        }
    try:
        payload = run_inference_from_artifacts(
            run_dir=str(Path(run_dir)),
            data_path=str(Path(data_path)),
        )
    except Exception as exc:
        return {
            "available": False,
            "status": "error",
            "reason": str(exc),
            "evaluation": {"available": False, "reason": str(exc)},
            "drift_summary": {"overall_drift_score": 0.0},
            "ood_summary": {"overall_ood_fraction": 0.0},
        }
    return {
        "available": True,
        "status": str(payload.get("status", "ok")).strip() or "ok",
        "reason": "",
        "data_path": str(payload.get("data_path", "")).strip() or None,
        "evaluation": dict(payload.get("evaluation") or {}),
        "drift_summary": dict(payload.get("drift_summary") or {}),
        "ood_summary": dict(payload.get("ood_summary") or {}),
        "recommendations": list(payload.get("recommendations") or []),
    }


def _adapter_slots() -> list[dict[str, Any]]:
    slots = [
        ("mapie", "mapie", "conformal uncertainty"),
        ("evidently", "evidently", "monitoring and drift reports"),
        ("mlflow", "mlflow", "registry export"),
        ("opentelemetry", "opentelemetry", "run observability"),
        ("openlineage", "openlineage", "lineage export"),
    ]
    out: list[dict[str, Any]] = []
    for key, import_name, purpose in slots:
        installed = util.find_spec(import_name) is not None
        package_name = "opentelemetry-api" if key == "opentelemetry" else key
        version = None
        if installed:
            try:
                version = metadata.version(package_name)
            except metadata.PackageNotFoundError:
                version = None
        out.append(
            {
                "key": key,
                "purpose": purpose,
                "status": "available" if installed else "not_installed",
                "version": version,
                "adoption_mode": "adapter_slot_only",
            }
        )
    return out


def _quality_state(
    *,
    task_type: str,
    metrics: dict[str, Any],
    champion_metric_value: float | None,
    primary_metric: str,
    evaluation_available: bool,
) -> tuple[str, list[str]]:
    reasons: list[str] = []
    if not evaluation_available:
        return "unknown", ["fresh_evaluation_unavailable"]
    if task_type == "regression":
        fresh_mae = _optional_float(metrics.get("mae"))
        fresh_r2 = _optional_float(metrics.get("r2"))
        if fresh_r2 is not None and fresh_r2 < 0.20:
            return "poor", ["fresh_r2_low"]
        if primary_metric == "mae" and champion_metric_value is not None and fresh_mae is not None and fresh_mae > champion_metric_value * 1.40:
            return "poor", ["fresh_mae_degraded_vs_champion"]
        if fresh_r2 is not None and fresh_r2 >= 0.70:
            return "strong", ["fresh_regression_quality_strong"]
        return "acceptable", ["fresh_regression_quality_acceptable"]
    fresh_f1 = _optional_float(metrics.get("f1"))
    fresh_accuracy = _optional_float(metrics.get("accuracy"))
    fresh_log_loss = _optional_float(metrics.get("log_loss"))
    fresh_pr_auc = _optional_float(metrics.get("pr_auc"))
    fresh_recall = _optional_float(metrics.get("recall"))
    if task_type in {"fraud_detection", "anomaly_detection"}:
        if (fresh_recall is not None and fresh_recall < 0.70) or (fresh_pr_auc is not None and fresh_pr_auc < 0.35):
            return "poor", ["rare_event_quality_below_target"]
        if (fresh_recall is not None and fresh_recall >= 0.85) and (fresh_pr_auc is not None and fresh_pr_auc >= 0.55):
            return "strong", ["rare_event_quality_strong"]
        return "acceptable", ["rare_event_quality_acceptable"]
    if (fresh_f1 is not None and fresh_f1 < 0.65) or (fresh_accuracy is not None and fresh_accuracy < 0.70):
        return "poor", ["classification_quality_below_target"]
    if fresh_f1 is not None and fresh_f1 >= 0.85 and (fresh_log_loss is None or fresh_log_loss < 0.40):
        return "strong", ["classification_quality_strong"]
    return "acceptable", ["classification_quality_acceptable"]


def _calibration_signals(*, metrics: dict[str, Any], moderate_shift: bool) -> list[str]:
    out: list[str] = []
    log_loss = _optional_float(metrics.get("log_loss"))
    if log_loss is not None and log_loss >= 0.55:
        out.append("log_loss_high")
    if moderate_shift:
        out.append("moderate_feature_shift")
    return out or ["calibration_stable"]


def _confidence_band(*, reasons: list[str], positive: bool) -> str:
    if positive:
        if len(reasons) >= 3:
            return "high"
        if len(reasons) == 2:
            return "medium"
        return "low"
    if len(reasons) >= 2:
        return "medium"
    return "high"


def _comparison_summary(
    *,
    champion_model_family: str | None,
    challenger_model_family: str | None,
    primary_metric: str,
    challenger_winner: str,
    drift_score: float,
) -> str:
    return (
        f"Lifecycle compared champion `{champion_model_family or 'unknown champion'}` against "
        f"`{challenger_model_family or 'no challenger'}` on `{primary_metric}`; "
        f"challenger winner=`{challenger_winner}`, drift_score={drift_score:.4f}."
    )


def _recalibration_summary(*, action: str) -> str:
    if action == "recalibrate":
        return "Relaytic prefers recalibration because the route still looks useful but calibration or threshold behavior appears stale."
    return "Relaytic does not see a strong recalibration-only case right now."


def _retrain_summary(*, action: str, reasons: list[str]) -> str:
    if action == "retrain":
        return f"Relaytic recommends retraining because: {', '.join(reasons)}."
    return "Relaytic does not see enough evidence to force retraining yet."


def _promotion_summary(*, action: str, selected_model_family: str | None) -> str:
    family = selected_model_family or "unknown model"
    if action == "promote_challenger":
        return f"Relaytic recommends promoting challenger `{family}` because it survived evidence pressure and fresh-data checks."
    if action == "hold_promotion":
        return f"Relaytic sees challenger pressure but is holding promotion for `{family}` until lifecycle risk is reduced."
    return f"Relaytic recommends keeping the current champion `{family}`."


def _rollback_summary(*, action: str, target_available: bool) -> str:
    if action == "rollback_required":
        if target_available:
            return "Relaytic recommends rollback to the last stable champion because the current route is no longer trustworthy."
        return "Relaytic recommends rollback, but no local prior stable checkpoint is attached to this run yet."
    return "Relaytic does not see a rollback trigger right now."


def _format_metric_block(metrics: dict[str, Any]) -> str:
    if not metrics:
        return "not available"
    parts: list[str] = []
    for key in ("log_loss", "mae", "rmse", "accuracy", "precision", "recall", "f1", "pr_auc", "roc_auc", "r2"):
        value = metrics.get(key)
        if isinstance(value, (int, float)):
            parts.append(f"{key}={float(value):.4f}")
    return ", ".join(parts) if parts else "not available"
