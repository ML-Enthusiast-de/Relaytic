"""Slice 09C bounded autonomy loops and executable second-pass behavior."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
import shutil
from typing import Any

from relaytic.core.json_utils import write_json
from relaytic.ingestion import load_tabular_data
from relaytic.modeling import train_surrogate_candidates

from .models import (
    AUTONOMY_LOOP_STATE_SCHEMA_VERSION,
    AUTONOMY_ROUND_REPORT_SCHEMA_VERSION,
    BRANCH_OUTCOME_MATRIX_SCHEMA_VERSION,
    CHALLENGER_QUEUE_SCHEMA_VERSION,
    CHAMPION_LINEAGE_SCHEMA_VERSION,
    LOOP_BUDGET_REPORT_SCHEMA_VERSION,
    RECALIBRATION_RUN_REQUEST_SCHEMA_VERSION,
    RETRAIN_RUN_REQUEST_SCHEMA_VERSION,
    AutonomyBundle,
    AutonomyControls,
    AutonomyLoopState,
    AutonomyRoundReport,
    AutonomyTrace,
    BranchOutcomeMatrix,
    ChallengerQueue,
    ChampionLineage,
    LoopBudgetReport,
    RecalibrationRunRequest,
    RetrainRunRequest,
    build_autonomy_controls_from_policy,
)


@dataclass(frozen=True)
class AutonomyRunResult:
    bundle: AutonomyBundle
    review_markdown: str
    selected_action: str
    promotion_applied: bool
    winning_branch_id: str | None


def run_autonomy_loop(
    *,
    run_dir: str | Path,
    data_path: str,
    policy: dict[str, Any],
    planning_bundle: dict[str, Any],
    evidence_bundle: dict[str, Any],
    completion_bundle: dict[str, Any],
    lifecycle_bundle: dict[str, Any],
    research_bundle: dict[str, Any] | None = None,
    intelligence_bundle: dict[str, Any] | None = None,
) -> AutonomyRunResult:
    """Execute one bounded second-pass loop for the current Relaytic run."""

    controls = build_autonomy_controls_from_policy(policy)
    root = Path(run_dir)
    research_bundle = research_bundle or {}
    intelligence_bundle = intelligence_bundle or {}
    trace = AutonomyTrace(
        agent="autonomy_controller",
        operating_mode="bounded_followup_loop",
        llm_used=False,
        llm_status="not_requested",
        deterministic_evidence=[
            "completion_signal",
            "lifecycle_signal",
            "semantic_debate_signal",
            "branch_metric_comparison",
            "promotion_guardrail",
        ],
    )

    current_plan = _bundle_item(planning_bundle, "plan")
    execution_summary = dict(current_plan.get("execution_summary") or {})
    research_brief = _bundle_item(research_bundle, "research_brief")
    method_transfer = _bundle_item(research_bundle, "method_transfer_report")
    semantic_debate = _bundle_item(intelligence_bundle, "semantic_debate_report")
    uncertainty = _bundle_item(intelligence_bundle, "semantic_uncertainty_report")
    local_data_candidates = _find_local_data_candidates(
        data_path=data_path,
        target_column=_clean_text(current_plan.get("target_column")),
        feature_columns=[str(item) for item in current_plan.get("feature_columns", []) if str(item).strip()],
    )
    selected_action = _choose_action(
        controls=controls,
        completion_bundle=completion_bundle,
        lifecycle_bundle=lifecycle_bundle,
        research_brief=research_brief,
        semantic_debate=semantic_debate,
        uncertainty=uncertainty,
        local_data_candidates=local_data_candidates,
    )
    queue = _build_branch_queue(
        controls=controls,
        selected_action=selected_action,
        current_plan=current_plan,
        execution_summary=execution_summary,
        research_bundle=research_bundle,
        semantic_debate=semantic_debate,
        local_data_candidates=local_data_candidates,
        data_path=data_path,
    )
    branch_results = _execute_branches(
        root=root,
        controls=controls,
        queue=queue,
        current_plan=current_plan,
        execution_summary=execution_summary,
    )
    winning_branch = _select_winning_branch(
        branches=branch_results,
        primary_metric=_clean_text(current_plan.get("primary_metric")) or "unknown",
        baseline_metric_value=_baseline_metric_value(current_plan=current_plan),
        controls=controls,
    )
    promotion_applied = False
    if winning_branch is not None:
        promotion_applied = _promote_branch(root=root, branch=winning_branch, current_plan=current_plan)
    generated_at = _utc_now()
    lineage = _build_lineage(root=root, branch=winning_branch, promotion_applied=promotion_applied, controls=controls, trace=trace)
    bundle = AutonomyBundle(
        autonomy_loop_state=AutonomyLoopState(
            schema_version=AUTONOMY_LOOP_STATE_SCHEMA_VERSION,
            generated_at=generated_at,
            controls=controls,
            status="completed" if queue else "idle",
            current_round=1 if queue else 0,
            max_rounds=controls.max_followup_rounds,
            selected_action=selected_action,
            promotion_applied=promotion_applied,
            stopped_reason="no_followup_required" if not queue else ("promotion_applied" if promotion_applied else "bounded_round_completed"),
            summary=_loop_state_summary(selected_action=selected_action, promotion_applied=promotion_applied, branch_count=len(branch_results)),
            trace=trace,
        ),
        autonomy_round_report=AutonomyRoundReport(
            schema_version=AUTONOMY_ROUND_REPORT_SCHEMA_VERSION,
            generated_at=generated_at,
            controls=controls,
            round_index=1 if queue else 0,
            selected_action=selected_action,
            promoted_branch_id=winning_branch["branch_id"] if winning_branch and promotion_applied else None,
            local_data_candidates=local_data_candidates,
            summary=_round_summary(selected_action=selected_action, winning_branch=winning_branch, promotion_applied=promotion_applied),
            trace=trace,
        ),
        challenger_queue=ChallengerQueue(
            schema_version=CHALLENGER_QUEUE_SCHEMA_VERSION,
            generated_at=generated_at,
            controls=controls,
            selected_action=selected_action,
            branches=queue,
            summary=f"Relaytic queued {len(queue)} bounded follow-up branch(es) for `{selected_action}`.",
            trace=trace,
        ),
        branch_outcome_matrix=BranchOutcomeMatrix(
            schema_version=BRANCH_OUTCOME_MATRIX_SCHEMA_VERSION,
            generated_at=generated_at,
            controls=controls,
            selected_action=selected_action,
            primary_metric=_clean_text(current_plan.get("primary_metric")) or "unknown",
            baseline_metric_value=_baseline_metric_value(current_plan=current_plan),
            branches=branch_results,
            winning_branch_id=winning_branch["branch_id"] if winning_branch else None,
            promotion_applied=promotion_applied,
            summary=_matrix_summary(branch_results=branch_results, winning_branch=winning_branch, promotion_applied=promotion_applied),
            trace=trace,
        ),
        retrain_run_request=RetrainRunRequest(
            schema_version=RETRAIN_RUN_REQUEST_SCHEMA_VERSION,
            generated_at=generated_at,
            controls=controls,
            requested=selected_action == "run_retrain_pass",
            data_path=(queue[0]["data_path"] if queue else None),
            requested_model_family=(queue[0]["requested_model_family"] if queue else None),
            threshold_policy=(queue[0].get("threshold_policy") if queue else None),
            reason_codes=list(queue[0].get("reason_codes", [])) if queue else [],
            summary="Relaytic opened a bounded retraining request." if selected_action == "run_retrain_pass" else "Relaytic did not request retraining in this autonomy round.",
            trace=trace,
        ),
        recalibration_run_request=RecalibrationRunRequest(
            schema_version=RECALIBRATION_RUN_REQUEST_SCHEMA_VERSION,
            generated_at=generated_at,
            controls=controls,
            requested=selected_action == "run_recalibration_pass",
            requested_model_family=(queue[0]["requested_model_family"] if queue else None),
            threshold_policy=(queue[0].get("threshold_policy") if queue else None),
            reason_codes=list(queue[0].get("reason_codes", [])) if queue else [],
            summary="Relaytic opened a bounded recalibration request." if selected_action == "run_recalibration_pass" else "Relaytic did not request recalibration in this autonomy round.",
            trace=trace,
        ),
        champion_lineage=lineage,
        loop_budget_report=LoopBudgetReport(
            schema_version=LOOP_BUDGET_REPORT_SCHEMA_VERSION,
            generated_at=generated_at,
            controls=controls,
            max_rounds=controls.max_followup_rounds,
            used_rounds=1 if queue else 0,
            max_branches_per_round=controls.max_branches_per_round,
            used_branches=len(branch_results),
            budget_remaining=max(0, controls.max_branches_per_round - len(branch_results)),
            summary=f"Relaytic used {len(branch_results)} of {controls.max_branches_per_round} branch slots in this bounded autonomy round.",
            trace=trace,
        ),
    )
    return AutonomyRunResult(
        bundle=bundle,
        review_markdown=render_autonomy_review_markdown(bundle.to_dict()),
        selected_action=selected_action,
        promotion_applied=promotion_applied,
        winning_branch_id=winning_branch["branch_id"] if winning_branch else None,
    )


def render_autonomy_review_markdown(bundle: AutonomyBundle | dict[str, Any]) -> str:
    """Render a concise human-readable autonomy review."""

    payload = bundle.to_dict() if isinstance(bundle, AutonomyBundle) else dict(bundle)
    loop_state = dict(payload.get("autonomy_loop_state", {}))
    queue = dict(payload.get("challenger_queue", {}))
    matrix = dict(payload.get("branch_outcome_matrix", {}))
    lineage = dict(payload.get("champion_lineage", {}))
    lines = [
        "# Relaytic Autonomy Review",
        "",
        f"- Status: `{loop_state.get('status') or 'unknown'}`",
        f"- Selected action: `{loop_state.get('selected_action') or 'unknown'}`",
        f"- Promotion applied: `{loop_state.get('promotion_applied')}`",
        f"- Branches queued: `{len(queue.get('branches', []))}`",
        f"- Winning branch: `{matrix.get('winning_branch_id') or 'none'}`",
        f"- Current champion: `{lineage.get('current_model_family') or 'unknown'}`",
    ]
    branches = list(matrix.get("branches", []))
    if branches:
        lines.extend(["", "## Branch Outcomes"])
        for item in branches[:4]:
            lines.append(
                f"- `{item.get('branch_id')}` family=`{item.get('selected_model_family')}` "
                f"metric=`{item.get('metric_value')}` promoted=`{item.get('promotion_candidate')}`"
            )
    return "\n".join(lines).rstrip() + "\n"


def _choose_action(
    *,
    controls: AutonomyControls,
    completion_bundle: dict[str, Any],
    lifecycle_bundle: dict[str, Any],
    research_brief: dict[str, Any],
    semantic_debate: dict[str, Any],
    uncertainty: dict[str, Any],
    local_data_candidates: list[dict[str, Any]],
) -> str:
    if not controls.enabled or not controls.allow_auto_run:
        return "hold_current_route"
    completion = _bundle_item(completion_bundle, "completion_decision")
    lifecycle_retrain = _bundle_item(lifecycle_bundle, "retrain_decision")
    lifecycle_recal = _bundle_item(lifecycle_bundle, "recalibration_decision")
    research_action = _clean_text(research_brief.get("recommended_followup_action"))
    semantic_action = _clean_text(semantic_debate.get("recommended_followup_action"))
    completion_action = _clean_text(completion.get("action"))
    if semantic_action == "run_recalibration_pass" or research_action == "run_recalibration_pass":
        return "run_recalibration_pass"
    if _clean_text(lifecycle_recal.get("action")) == "recalibrate":
        return "run_recalibration_pass"
    if _clean_text(lifecycle_retrain.get("action")) == "retrain":
        return "run_retrain_pass"
    if semantic_action in {"run_retrain_pass", "run_recalibration_pass", "expand_challenger_portfolio", "collect_more_data", "benchmark_needed"}:
        if semantic_action == "collect_more_data" and local_data_candidates:
            return "run_retrain_pass"
        return semantic_action
    if research_action in {"run_recalibration_pass", "expand_challenger_portfolio", "collect_more_data", "benchmark_needed"}:
        if research_action == "collect_more_data" and local_data_candidates:
            return "run_retrain_pass"
        return research_action
    if completion_action in {"retrain_candidate"}:
        return "run_retrain_pass"
    if completion_action in {"recalibration_candidate"}:
        return "run_recalibration_pass"
    if completion_action in {"review_challenger", "continue_experimentation", "memory_support_needed"}:
        return "expand_challenger_portfolio"
    if list(uncertainty.get("unresolved_items", [])):
        return "expand_challenger_portfolio"
    return "hold_current_route"


def _build_branch_queue(
    *,
    controls: AutonomyControls,
    selected_action: str,
    current_plan: dict[str, Any],
    execution_summary: dict[str, Any],
    research_bundle: dict[str, Any],
    semantic_debate: dict[str, Any],
    local_data_candidates: list[dict[str, Any]],
    data_path: str,
) -> list[dict[str, Any]]:
    current_family = _clean_text(execution_summary.get("selected_model_family")) or _clean_text(current_plan.get("selected_model_family"))
    task_type = _clean_text(current_plan.get("task_type")) or "unknown"
    candidates = _default_candidate_families(task_type=task_type)
    preferred_family = None
    verifier = dict(semantic_debate.get("verifier_verdict") or {})
    if isinstance(verifier.get("preferred_model_family"), str):
        preferred_family = _clean_text(verifier.get("preferred_model_family"))
    method_transfer = _bundle_item(research_bundle, "method_transfer_report")
    research_families = [
        _clean_text(item.get("value"))
        for item in method_transfer.get("accepted_candidates", [])
        if str(item.get("candidate_kind", "")).strip() == "challenger_family"
    ]
    research_families = [item for item in research_families if item]
    research_evaluation_designs = {
        _clean_text(item.get("value"))
        for item in method_transfer.get("accepted_candidates", [])
        if str(item.get("candidate_kind", "")).strip() == "evaluation_design"
    }
    queue: list[dict[str, Any]] = []
    base_data_path = data_path
    if selected_action == "run_recalibration_pass":
        recalibration_reason_codes = ["lifecycle_recalibration"]
        if "calibration_review" in research_evaluation_designs:
            recalibration_reason_codes.append("research_calibration_review")
        queue.append(
            {
                "branch_id": "round01_recalibration",
                "requested_model_family": current_family,
                "threshold_policy": _preferred_threshold_policy(execution_summary=execution_summary),
                "data_path": base_data_path,
                "reason_codes": recalibration_reason_codes,
                "branch_kind": "recalibration",
                "priority": 1,
            }
        )
    elif selected_action == "run_retrain_pass":
        retrain_data_path = local_data_candidates[0]["data_path"] if local_data_candidates else base_data_path
        queue.append(
            {
                "branch_id": "round01_retrain",
                "requested_model_family": current_family,
                "threshold_policy": None,
                "data_path": retrain_data_path,
                "reason_codes": ["autonomous_retrain"],
                "branch_kind": "retrain",
                "priority": 1,
            }
        )
        if controls.allow_architecture_switch:
            alt = next((item for item in (research_families + [preferred_family] + candidates) if item and item != current_family), None)
            if alt:
                alt_reason_codes = ["autonomous_retrain_alt"]
                if alt in research_families:
                    alt_reason_codes.append("research_transfer_family")
                queue.append(
                    {
                        "branch_id": "round01_retrain_alt",
                        "requested_model_family": alt,
                        "threshold_policy": None,
                        "data_path": retrain_data_path,
                        "reason_codes": alt_reason_codes,
                        "branch_kind": "retrain_alt",
                        "priority": 2,
                    }
                )
    elif selected_action == "expand_challenger_portfolio":
        ordered = [item for item in research_families + [preferred_family] + candidates if item and item != current_family]
        seen: set[str] = set()
        for family in ordered:
            if family in seen:
                continue
            seen.add(family)
            reason_codes = ["challenger_portfolio"]
            if family in research_families:
                reason_codes.append("research_transfer_family")
            if preferred_family and family == preferred_family:
                reason_codes.append("semantic_preferred_family")
            queue.append(
                {
                    "branch_id": f"round01_{family}",
                    "requested_model_family": family,
                    "threshold_policy": None,
                    "data_path": base_data_path,
                    "reason_codes": reason_codes,
                    "branch_kind": "challenger",
                    "priority": len(queue) + 1,
                }
            )
            if len(queue) >= controls.max_branches_per_round:
                break
    return queue[: controls.max_branches_per_round]


def _execute_branches(
    *,
    root: Path,
    controls: AutonomyControls,
    queue: list[dict[str, Any]],
    current_plan: dict[str, Any],
    execution_summary: dict[str, Any],
) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    if not queue:
        return results
    feature_columns = [str(item) for item in current_plan.get("feature_columns", []) if str(item).strip()]
    target_column = _clean_text(current_plan.get("target_column"))
    if not feature_columns or not target_column:
        return results
    timestamp_column = _clean_text(current_plan.get("timestamp_column"))
    task_type = _clean_text(current_plan.get("task_type"))
    primary_metric = _clean_text(current_plan.get("primary_metric")) or "unknown"
    round_root = root / "autonomy_rounds" / "round_01"
    round_root.mkdir(parents=True, exist_ok=True)
    for branch in queue:
        branch_dir = round_root / str(branch["branch_id"])
        branch_dir.mkdir(parents=True, exist_ok=True)
        try:
            frame = load_tabular_data(branch["data_path"]).frame
            training = train_surrogate_candidates(
                frame=frame,
                target_column=target_column,
                feature_columns=feature_columns,
                requested_model_family=str(branch["requested_model_family"] or "auto"),
                timestamp_column=timestamp_column,
                compare_against_baseline=False,
                threshold_policy=branch.get("threshold_policy"),
                task_type=task_type,
                selection_metric=primary_metric,
                preferred_candidate_order=[str(branch["requested_model_family"] or "auto")],
                output_run_dir=branch_dir,
                checkpoint_base_dir=branch_dir / "checkpoints",
            )
            metric_value = _metric_from_training(training, primary_metric=primary_metric)
            baseline_metric = _metric_from_execution_summary(execution_summary, primary_metric=primary_metric)
            improvement = _relative_improvement(primary_metric=primary_metric, baseline=baseline_metric, candidate=metric_value)
            promotion_candidate = _is_improvement(primary_metric=primary_metric, baseline=baseline_metric, candidate=metric_value) and improvement >= controls.min_relative_improvement
            results.append(
                {
                    "branch_id": branch["branch_id"],
                    "branch_kind": branch["branch_kind"],
                    "requested_model_family": branch["requested_model_family"],
                    "selected_model_family": training.get("selected_model_family"),
                    "data_path": branch["data_path"],
                    "threshold_policy": branch.get("threshold_policy"),
                    "metric_value": metric_value,
                    "baseline_metric_value": baseline_metric,
                    "relative_improvement": improvement,
                    "promotion_candidate": promotion_candidate,
                    "status": "ok",
                    "training_result": training,
                    "branch_dir": str(branch_dir),
                }
            )
        except Exception as exc:
            results.append(
                {
                    "branch_id": branch["branch_id"],
                    "branch_kind": branch["branch_kind"],
                    "requested_model_family": branch["requested_model_family"],
                    "data_path": branch["data_path"],
                    "threshold_policy": branch.get("threshold_policy"),
                    "status": "error",
                    "error": str(exc),
                    "promotion_candidate": False,
                    "branch_dir": str(branch_dir),
                }
            )
    return results


def _select_winning_branch(
    *,
    branches: list[dict[str, Any]],
    primary_metric: str,
    baseline_metric_value: float | None,
    controls: AutonomyControls,
) -> dict[str, Any] | None:
    valid = [item for item in branches if item.get("status") == "ok" and item.get("promotion_candidate")]
    if not valid:
        return None
    higher_is_better = _higher_is_better(primary_metric)
    return sorted(
        valid,
        key=lambda item: (
            -float(item.get("relative_improvement", 0.0)),
            (-float(item.get("metric_value", 0.0)) if higher_is_better else float(item.get("metric_value", float("inf")))),
        ),
    )[0]


def _promote_branch(*, root: Path, branch: dict[str, Any], current_plan: dict[str, Any]) -> bool:
    training = dict(branch.get("training_result") or {})
    branch_dir = Path(str(branch.get("branch_dir", "")))
    if not training or not branch_dir.exists():
        return False
    copied_paths: dict[str, str] = {}
    for filename in ("model_params.json", "normalization_state.json"):
        source = branch_dir / filename
        if source.exists():
            target = root / filename
            shutil.copy2(source, target)
            copied_paths[filename] = str(target)
    for source in branch_dir.glob("*_state.json"):
        target = root / source.name
        shutil.copy2(source, target)
        copied_paths[source.name] = str(target)
    source_ckpts = branch_dir / "checkpoints"
    if source_ckpts.exists():
        target_ckpts = root / "checkpoints"
        target_ckpts.mkdir(parents=True, exist_ok=True)
        for source in source_ckpts.glob("*.json"):
            shutil.copy2(source, target_ckpts / source.name)
    updated_plan = dict(current_plan)
    execution_summary = dict(updated_plan.get("execution_summary") or {})
    execution_summary.update(training)
    execution_summary["run_dir"] = str(root)
    execution_summary["model_params_path"] = copied_paths.get("model_params.json", str(root / "model_params.json"))
    state_path = next((path for name, path in copied_paths.items() if name.endswith("_state.json")), None)
    if state_path:
        execution_summary["model_state_path"] = state_path
    execution_summary["autonomy_selected_action"] = branch.get("branch_kind")
    execution_summary["autonomy_branch_id"] = branch.get("branch_id")
    updated_plan["execution_summary"] = execution_summary
    write_json(root / "plan.json", updated_plan, indent=2, ensure_ascii=False, sort_keys=True)
    return True


def _build_lineage(
    *,
    root: Path,
    branch: dict[str, Any] | None,
    promotion_applied: bool,
    controls: AutonomyControls,
    trace: AutonomyTrace,
) -> ChampionLineage:
    existing_path = root / "champion_lineage.json"
    existing = {}
    if existing_path.exists():
        try:
            existing = json.loads(existing_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            existing = {}
    lineage = list(existing.get("lineage", [])) if isinstance(existing.get("lineage"), list) else []
    current_model_family = None
    if promotion_applied and branch is not None:
        training = dict(branch.get("training_result") or {})
        current_model_family = _clean_text(training.get("selected_model_family"))
        lineage.append(
            {
                "occurred_at": _utc_now(),
                "from_model_family": _clean_text(branch.get("requested_model_family")),
                "to_model_family": current_model_family,
                "branch_id": branch.get("branch_id"),
                "reason": "autonomy_promotion",
            }
        )
    else:
        current_model_family = _clean_text(existing.get("current_model_family"))
    return ChampionLineage(
        schema_version=CHAMPION_LINEAGE_SCHEMA_VERSION,
        generated_at=_utc_now(),
        controls=controls,
        current_model_family=current_model_family,
        lineage=lineage,
        summary=f"Relaytic recorded {len(lineage)} champion lineage transition(s).",
        trace=trace,
    )


def _find_local_data_candidates(*, data_path: str, target_column: str | None, feature_columns: list[str]) -> list[dict[str, Any]]:
    current = Path(data_path)
    if not current.exists() or not current.parent.exists():
        return []
    try:
        current_frame = load_tabular_data(current).frame
    except Exception:
        return []
    current_columns = {str(item).strip().casefold() for item in current_frame.columns}
    candidates: list[dict[str, Any]] = []
    for path in sorted(current.parent.iterdir()):
        if path == current or path.suffix.lower() not in {".csv", ".xlsx", ".xls"}:
            continue
        try:
            frame = load_tabular_data(path).frame
        except Exception:
            continue
        columns = {str(item).strip().casefold() for item in frame.columns}
        overlap = len(current_columns.intersection(columns))
        score = overlap / max(len(current_columns), 1)
        if target_column and str(target_column).casefold() not in columns:
            continue
        if score < 0.75 or len(frame) <= len(current_frame):
            continue
        candidates.append(
            {
                "data_path": str(path),
                "row_count": int(len(frame)),
                "column_overlap": round(score, 4),
                "extra_rows": int(len(frame) - len(current_frame)),
            }
        )
    candidates.sort(key=lambda item: (-item["row_count"], -item["column_overlap"], item["data_path"]))
    return candidates[:3]


def _default_candidate_families(*, task_type: str) -> list[str]:
    if task_type in {"binary_classification", "multiclass_classification", "fraud_detection", "anomaly_detection"}:
        return [
            "boosted_tree_classifier",
            "bagged_tree_classifier",
            "logistic_regression",
            "lagged_tree_classifier",
            "lagged_logistic_regression",
        ]
    return [
        "boosted_tree_ensemble",
        "bagged_tree_ensemble",
        "linear_ridge",
        "lagged_tree_ensemble",
        "lagged_linear",
    ]


def _preferred_threshold_policy(*, execution_summary: dict[str, Any]) -> str:
    metrics = dict(execution_summary.get("selected_metrics") or {})
    validation = dict(metrics.get("validation") or {})
    precision = _optional_float(validation.get("precision"))
    recall = _optional_float(validation.get("recall"))
    if precision is not None and recall is not None:
        if precision < recall:
            return "favor_precision"
        if recall < precision:
            return "favor_recall"
    return "favor_f1"


def _metric_from_training(training: dict[str, Any], *, primary_metric: str) -> float | None:
    metrics = dict(training.get("selected_metrics") or {})
    validation = dict(metrics.get("validation") or {})
    if primary_metric in validation:
        return _optional_float(validation.get(primary_metric))
    test = dict(metrics.get("test") or {})
    if primary_metric in test:
        return _optional_float(test.get(primary_metric))
    return None


def _metric_from_execution_summary(execution_summary: dict[str, Any], *, primary_metric: str) -> float | None:
    metrics = dict(execution_summary.get("selected_metrics") or {})
    validation = dict(metrics.get("validation") or {})
    if primary_metric in validation:
        return _optional_float(validation.get(primary_metric))
    test = dict(metrics.get("test") or {})
    if primary_metric in test:
        return _optional_float(test.get(primary_metric))
    return None


def _baseline_metric_value(*, current_plan: dict[str, Any]) -> float | None:
    execution_summary = dict(current_plan.get("execution_summary") or {})
    return _metric_from_execution_summary(execution_summary, primary_metric=_clean_text(current_plan.get("primary_metric")) or "unknown")


def _relative_improvement(*, primary_metric: str, baseline: float | None, candidate: float | None) -> float:
    if candidate is None:
        return 0.0
    if baseline is None:
        return 1.0
    if _higher_is_better(primary_metric):
        return (candidate - baseline) / max(abs(baseline), 1e-6)
    return (baseline - candidate) / max(abs(baseline), 1e-6)


def _is_improvement(*, primary_metric: str, baseline: float | None, candidate: float | None) -> bool:
    if candidate is None:
        return False
    if baseline is None:
        return True
    return candidate > baseline if _higher_is_better(primary_metric) else candidate < baseline


def _higher_is_better(primary_metric: str) -> bool:
    return primary_metric in {"accuracy", "precision", "recall", "f1", "pr_auc", "roc_auc", "r2"}


def _bundle_item(bundle: dict[str, Any], key: str) -> dict[str, Any]:
    value = bundle.get(key)
    return dict(value) if isinstance(value, dict) else {}


def _optional_float(value: Any) -> float | None:
    try:
        if value is None or value == "":
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def _clean_text(value: Any) -> str | None:
    text = str(value or "").strip()
    return text or None


def _loop_state_summary(*, selected_action: str, promotion_applied: bool, branch_count: int) -> str:
    if branch_count == 0:
        return f"Relaytic found no bounded follow-up branch worth executing for `{selected_action}`."
    if promotion_applied:
        return f"Relaytic executed {branch_count} autonomy branch(es) and promoted the winning branch."
    return f"Relaytic executed {branch_count} autonomy branch(es) but kept the current champion."


def _round_summary(*, selected_action: str, winning_branch: dict[str, Any] | None, promotion_applied: bool) -> str:
    if promotion_applied and winning_branch is not None:
        return f"Relaytic used `{selected_action}` and promoted branch `{winning_branch['branch_id']}`."
    return f"Relaytic used `{selected_action}` as a bounded second-pass action."


def _matrix_summary(*, branch_results: list[dict[str, Any]], winning_branch: dict[str, Any] | None, promotion_applied: bool) -> str:
    if not branch_results:
        return "Relaytic did not execute any second-pass branches."
    if winning_branch is not None and promotion_applied:
        return f"Relaytic promoted `{winning_branch['branch_id']}` after bounded branch comparison."
    return f"Relaytic compared {len(branch_results)} bounded branch outcome(s) without promotion."


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()
