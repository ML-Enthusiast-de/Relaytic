"""Slice 09A run-memory and analog-retrieval pipeline."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import json
import math
import re
from pathlib import Path
from typing import Any

from .models import (
    ANALOG_RUN_CANDIDATES_SCHEMA_VERSION,
    CHALLENGER_PRIOR_SUGGESTIONS_SCHEMA_VERSION,
    MEMORY_FLUSH_REPORT_SCHEMA_VERSION,
    MEMORY_RETRIEVAL_SCHEMA_VERSION,
    REFLECTION_MEMORY_SCHEMA_VERSION,
    ROUTE_PRIOR_CONTEXT_SCHEMA_VERSION,
    AnalogRunCandidates,
    ChallengerPriorSuggestions,
    MemoryBundle,
    MemoryControls,
    MemoryFlushReport,
    MemoryRetrieval,
    MemoryTrace,
    ReflectionMemory,
    RoutePriorContext,
    build_memory_controls_from_policy,
)


@dataclass(frozen=True)
class MemoryRunResult:
    """Memory artifacts plus human-readable review output."""

    bundle: MemoryBundle
    review_markdown: str


def run_memory_retrieval(
    *,
    run_dir: str | Path,
    policy: dict[str, Any],
    mandate_bundle: dict[str, Any],
    context_bundle: dict[str, Any],
    intake_bundle: dict[str, Any] | None = None,
    investigation_bundle: dict[str, Any] | None = None,
    planning_bundle: dict[str, Any] | None = None,
    evidence_bundle: dict[str, Any] | None = None,
    completion_bundle: dict[str, Any] | None = None,
    lifecycle_bundle: dict[str, Any] | None = None,
    autonomy_bundle: dict[str, Any] | None = None,
    search_roots: list[str | Path] | None = None,
) -> MemoryRunResult:
    """Execute Slice 09A memory retrieval and advisory prior generation."""
    controls = build_memory_controls_from_policy(policy)
    root = Path(run_dir)
    intake_bundle = intake_bundle or {}
    investigation_bundle = investigation_bundle or {}
    planning_bundle = planning_bundle or {}
    evidence_bundle = evidence_bundle or {}
    completion_bundle = completion_bundle or {}
    lifecycle_bundle = lifecycle_bundle or {}
    autonomy_bundle = autonomy_bundle or {}

    current = _build_current_run_signature(
        run_dir=root,
        mandate_bundle=mandate_bundle,
        context_bundle=context_bundle,
        intake_bundle=intake_bundle,
        investigation_bundle=investigation_bundle,
        planning_bundle=planning_bundle,
        evidence_bundle=evidence_bundle,
        completion_bundle=completion_bundle,
        lifecycle_bundle=lifecycle_bundle,
        autonomy_bundle=autonomy_bundle,
    )
    roots = _resolve_search_roots(root, search_roots=search_roots)
    candidate_details = (
        _discover_candidate_runs(current_run_dir=root, search_roots=roots)
        if controls.enabled and controls.allow_prior_retrieval
        else []
    )
    scored_candidates = [
        _score_candidate(current=current, candidate=detail)
        for detail in candidate_details
    ]
    scored_candidates = [item for item in scored_candidates if item["similarity_score"] is not None]
    analog_candidates = _select_analog_candidates(
        scored_candidates=scored_candidates,
        controls=controls,
    )
    route_prior = _build_route_prior_context(
        current=current,
        analog_candidates=analog_candidates,
        controls=controls,
    )
    challenger_prior = _build_challenger_prior_suggestions(
        current=current,
        analog_candidates=analog_candidates,
        controls=controls,
    )
    retrieval_status = _retrieval_status(controls=controls, analog_candidates=analog_candidates)
    trace = MemoryTrace(
        agent="memory_retrieval_agent",
        operating_mode="deterministic_only",
        llm_used=False,
        llm_status="not_requested",
        deterministic_evidence=[
            "run_summary_scan",
            "artifact_derived_similarity",
            "route_prior_aggregation",
            "challenger_prior_aggregation",
            "reflection_writeback",
        ],
    )
    reflection = _build_reflection_memory(
        current=current,
        analog_candidates=analog_candidates,
        route_prior=route_prior,
        challenger_prior=challenger_prior,
        retrieval_status=retrieval_status,
        controls=controls,
        trace=trace,
    )
    flush_report = MemoryFlushReport(
        schema_version=MEMORY_FLUSH_REPORT_SCHEMA_VERSION,
        generated_at=_utc_now(),
        controls=controls,
        flush_stage=str(current.get("current_stage", "unknown")).strip() or "unknown",
        flushed=True,
        retrieval_status=retrieval_status,
        analog_count=len(analog_candidates),
        reflection_stage=reflection.current_stage,
        written_artifacts=[
            "memory_retrieval.json",
            "analog_run_candidates.json",
            "route_prior_context.json",
            "challenger_prior_suggestions.json",
            "reflection_memory.json",
            "memory_flush_report.json",
        ],
        summary=_flush_summary(
            retrieval_status=retrieval_status,
            analog_count=len(analog_candidates),
            current_stage=reflection.current_stage,
        ),
        trace=trace,
    )
    bundle = MemoryBundle(
        memory_retrieval=MemoryRetrieval(
            schema_version=MEMORY_RETRIEVAL_SCHEMA_VERSION,
            generated_at=_utc_now(),
            controls=controls,
            status=retrieval_status,
            current_run_id=str(current.get("run_id", root.name or "run")),
            current_stage=str(current.get("current_stage", "unknown")).strip() or "unknown",
            search_roots=[str(item) for item in roots],
            candidate_count=len(scored_candidates),
            selected_analog_count=len(analog_candidates),
            top_similarity_score=_optional_float(analog_candidates[0].get("similarity_score")) if analog_candidates else None,
            query_signature=current,
            analog_run_ids=[
                str(item.get("run_id", "")).strip()
                for item in analog_candidates
                if str(item.get("run_id", "")).strip()
            ],
            counterfactual={
                "without_memory": "Relaytic would continue with deterministic local planning and challenger selection only.",
                "with_memory": _with_memory_counterfactual(route_prior=route_prior, challenger_prior=challenger_prior),
            },
            summary=_retrieval_summary(retrieval_status=retrieval_status, analog_count=len(analog_candidates)),
            trace=trace,
        ),
        analog_run_candidates=AnalogRunCandidates(
            schema_version=ANALOG_RUN_CANDIDATES_SCHEMA_VERSION,
            generated_at=_utc_now(),
            controls=controls,
            current_run_id=str(current.get("run_id", root.name or "run")),
            candidates=analog_candidates,
            summary=_candidate_summary(analog_candidates),
            trace=trace,
        ),
        route_prior_context=RoutePriorContext(
            schema_version=ROUTE_PRIOR_CONTEXT_SCHEMA_VERSION,
            generated_at=_utc_now(),
            controls=controls,
            status=str(route_prior["status"]),
            selected_route_id=_optional_str(current.get("selected_route_id")),
            baseline_candidate_order=list(route_prior["baseline_candidate_order"]),
            adjusted_candidate_order=list(route_prior["adjusted_candidate_order"]),
            family_bias=list(route_prior["family_bias"]),
            influencing_analogs=list(route_prior["influencing_analogs"]),
            counterfactual=dict(route_prior["counterfactual"]),
            summary=str(route_prior["summary"]),
            trace=trace,
        ),
        challenger_prior_suggestions=ChallengerPriorSuggestions(
            schema_version=CHALLENGER_PRIOR_SUGGESTIONS_SCHEMA_VERSION,
            generated_at=_utc_now(),
            controls=controls,
            status=str(challenger_prior["status"]),
            preferred_challenger_family=_optional_str(challenger_prior.get("preferred_challenger_family")),
            ranked_families=list(challenger_prior["ranked_families"]),
            influencing_analogs=list(challenger_prior["influencing_analogs"]),
            counterfactual=dict(challenger_prior["counterfactual"]),
            summary=str(challenger_prior["summary"]),
            trace=trace,
        ),
        reflection_memory=reflection,
        memory_flush_report=flush_report,
    )
    return MemoryRunResult(
        bundle=bundle,
        review_markdown=render_memory_review_markdown(bundle.to_dict()),
    )


def render_memory_review_markdown(bundle: dict[str, Any]) -> str:
    """Render a concise markdown review of the current memory state."""
    retrieval = dict(bundle.get("memory_retrieval", {}))
    analogs = list(dict(bundle.get("analog_run_candidates", {})).get("candidates", []))
    route_prior = dict(bundle.get("route_prior_context", {}))
    challenger_prior = dict(bundle.get("challenger_prior_suggestions", {}))
    reflection = dict(bundle.get("reflection_memory", {}))
    lines = [
        "# Relaytic Memory Review",
        "",
        f"- Status: `{retrieval.get('status') or 'unknown'}`",
        f"- Current stage: `{retrieval.get('current_stage') or 'unknown'}`",
        f"- Analog candidates: `{retrieval.get('selected_analog_count', 0)}`",
        f"- Route prior status: `{route_prior.get('status') or 'unknown'}`",
        f"- Challenger prior status: `{challenger_prior.get('status') or 'unknown'}`",
    ]
    if route_prior.get("baseline_candidate_order") or route_prior.get("adjusted_candidate_order"):
        lines.extend(
            [
                "",
                "## Planning Influence",
                f"- Baseline candidate order: `{', '.join(route_prior.get('baseline_candidate_order', [])) or 'none'}`",
                f"- Memory-adjusted order: `{', '.join(route_prior.get('adjusted_candidate_order', [])) or 'none'}`",
            ]
        )
    preferred = str(challenger_prior.get("preferred_challenger_family", "")).strip()
    if preferred:
        lines.extend(["", "## Challenger Prior", f"- Preferred challenger family: `{preferred}`"])
    if analogs:
        lines.extend(["", "## Top Analogs"])
        for item in analogs[:3]:
            lines.append(
                f"- `{item.get('run_id')}` score `{_format_score(item.get('similarity_score'))}`: {item.get('relevance_reason')}"
            )
    if reflection:
        lessons = [str(item).strip() for item in reflection.get("lessons", []) if str(item).strip()]
        if lessons:
            lines.extend(["", "## Reflection", f"- {lessons[0]}"])
    return "\n".join(lines) + "\n"


def _build_current_run_signature(
    *,
    run_dir: Path,
    mandate_bundle: dict[str, Any],
    context_bundle: dict[str, Any],
    intake_bundle: dict[str, Any],
    investigation_bundle: dict[str, Any],
    planning_bundle: dict[str, Any],
    evidence_bundle: dict[str, Any],
    completion_bundle: dict[str, Any],
    lifecycle_bundle: dict[str, Any],
    autonomy_bundle: dict[str, Any],
) -> dict[str, Any]:
    run_brief = _bundle_item(mandate_bundle, "run_brief")
    task_brief = _bundle_item(context_bundle, "task_brief")
    domain_memo = _bundle_item(investigation_bundle, "domain_memo")
    dataset_profile = _bundle_item(investigation_bundle, "dataset_profile")
    focus_profile = _bundle_item(investigation_bundle, "focus_profile")
    optimization_profile = _bundle_item(investigation_bundle, "optimization_profile")
    plan = _bundle_item(planning_bundle, "plan")
    execution_summary = dict(plan.get("execution_summary") or {})
    audit_report = _bundle_item(evidence_bundle, "audit_report")
    belief_update = _bundle_item(evidence_bundle, "belief_update")
    completion_decision = _bundle_item(completion_bundle, "completion_decision")
    run_state = _bundle_item(completion_bundle, "run_state")
    promotion_decision = _bundle_item(lifecycle_bundle, "promotion_decision")
    autonomy_loop_state = _bundle_item(autonomy_bundle, "autonomy_loop_state")
    autonomy_mode = _bundle_item(intake_bundle, "autonomy_mode")
    current_stage = (
        ("autonomy_reviewed" if any(autonomy_bundle.values()) else None)
        or ("lifecycle_reviewed" if any(lifecycle_bundle.values()) else None)
        or ("completion_reviewed" if any(completion_bundle.values()) else None)
        or ("evidence_reviewed" if any(evidence_bundle.values()) else None)
        or ("planned_and_executed" if execution_summary else None)
        or ("planned" if plan else None)
        or ("investigated" if any(investigation_bundle.values()) else None)
        or _optional_str(run_state.get("current_stage"))
        or ("foundation_ready" if mandate_bundle and context_bundle else None)
        or "initialized"
    )
    task_type = (
        _optional_str(plan.get("task_type"))
        or _optional_str(task_brief.get("task_type_hint"))
        or _investigation_task_type(investigation_bundle=investigation_bundle, task_brief=task_brief)
        or "unknown"
    )
    primary_metric = (
        _optional_str(plan.get("primary_metric"))
        or _optional_str(optimization_profile.get("primary_metric"))
        or _optional_str(focus_profile.get("primary_metric"))
        or "unknown"
    )
    selected_route_id = (
        _optional_str(plan.get("selected_route_id"))
        or _investigation_route_id(investigation_bundle=investigation_bundle, task_type=task_type)
    )
    return {
        "run_id": run_dir.name or "run",
        "current_stage": current_stage,
        "task_type": task_type,
        "domain_archetype": _optional_str(domain_memo.get("domain_archetype")) or _optional_str(task_brief.get("domain_archetype_hint")) or "generic_tabular",
        "objective": _optional_str(run_brief.get("objective")) or "best_robust_pareto_front",
        "primary_metric": primary_metric,
        "selected_route_id": selected_route_id,
        "selected_model_family": _optional_str(execution_summary.get("selected_model_family")),
        "target_column": _optional_str(plan.get("target_column")) or _optional_str(task_brief.get("target_column")),
        "data_mode": _optional_str(dataset_profile.get("data_mode")) or "steady_state",
        "row_count": _coerce_int(dataset_profile.get("row_count")),
        "column_count": _coerce_int(dataset_profile.get("column_count")),
        "readiness_level": _optional_str(audit_report.get("readiness_level")),
        "provisional_recommendation": _optional_str(audit_report.get("provisional_recommendation")),
        "belief_action": _optional_str(belief_update.get("recommended_action")),
        "completion_action": _optional_str(completion_decision.get("action")),
        "blocking_layer": _optional_str(completion_decision.get("blocking_layer")),
        "promotion_action": _optional_str(promotion_decision.get("action")),
        "promotion_target": _optional_str(promotion_decision.get("selected_model_family")),
        "autonomy_action": _optional_str(autonomy_loop_state.get("selected_action")),
        "autonomy_mode": _optional_str(autonomy_mode.get("requested_mode")),
    }


def _investigation_task_type(
    *,
    investigation_bundle: dict[str, Any],
    task_brief: dict[str, Any],
) -> str | None:
    domain_memo = _bundle_item(investigation_bundle, "domain_memo")
    target_candidates = domain_memo.get("target_candidates")
    if not isinstance(target_candidates, list):
        return None
    target_column = _optional_str(task_brief.get("target_column"))
    ranked: list[dict[str, Any]] = []
    for item in target_candidates:
        if not isinstance(item, dict):
            continue
        ranked.append(item)
    if not ranked:
        return None
    if target_column:
        for item in ranked:
            if _optional_str(item.get("target_column")) == target_column:
                return _optional_str(item.get("task_type"))
    ranked.sort(
        key=lambda item: (
            -float(_optional_float(item.get("confidence")) or 0.0),
            str(item.get("target_column", "")),
        )
    )
    return _optional_str(ranked[0].get("task_type"))


def _investigation_route_id(*, investigation_bundle: dict[str, Any], task_type: str) -> str | None:
    domain_memo = _bundle_item(investigation_bundle, "domain_memo")
    route_hypotheses = domain_memo.get("route_hypotheses")
    if not isinstance(route_hypotheses, list):
        return None
    ranked: list[dict[str, Any]] = []
    for item in route_hypotheses:
        if not isinstance(item, dict):
            continue
        route_id = _optional_str(item.get("route_id"))
        if not route_id:
            continue
        ranked.append(item)
    if not ranked:
        return None
    preferred_tokens = _preferred_route_tokens(task_type=task_type)
    if preferred_tokens:
        preferred = [
            item
            for item in ranked
            if any(token in str(item.get("route_id", "")).lower() for token in preferred_tokens)
        ]
        if preferred:
            ranked = preferred
    ranked.sort(
        key=lambda item: (
            -float(_optional_float(item.get("confidence")) or 0.0),
            str(item.get("route_id", "")),
        )
    )
    return _optional_str(ranked[0].get("route_id"))


def _preferred_route_tokens(*, task_type: str) -> tuple[str, ...]:
    if _is_classification_task(task_type):
        return ("classifier", "classification", "threshold", "calibrated")
    return ("regression", "baseline", "steady_state")


def _resolve_search_roots(current_run_dir: Path, *, search_roots: list[str | Path] | None) -> list[Path]:
    if search_roots:
        roots = [Path(item).expanduser().resolve() for item in search_roots]
    else:
        project_root = Path(__file__).resolve().parents[3]
        roots = [current_run_dir.parent.resolve(), (project_root / "artifacts").resolve()]
    deduped: list[Path] = []
    seen: set[str] = set()
    for item in roots:
        text = str(item)
        if text in seen:
            continue
        seen.add(text)
        deduped.append(item)
    return deduped


def _discover_candidate_runs(*, current_run_dir: Path, search_roots: list[Path]) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    seen_run_dirs: set[str] = set()
    for root in search_roots:
        if not root.exists():
            continue
        try:
            summary_paths = list(root.rglob("run_summary.json"))
        except OSError:
            continue
        for summary_path in summary_paths:
            run_dir = summary_path.parent.resolve()
            if run_dir == current_run_dir.resolve():
                continue
            run_dir_text = str(run_dir)
            if run_dir_text in seen_run_dirs:
                continue
            seen_run_dirs.add(run_dir_text)
            summary = _read_json(summary_path)
            if not summary:
                continue
            candidates.append(
                {
                    "run_dir": run_dir,
                    "summary_path": summary_path.resolve(),
                    "summary": summary,
                    "challenger_report": _read_json(run_dir / "challenger_report.json"),
                    "reflection_memory": _read_json(run_dir / "reflection_memory.json"),
                    "memory_pinning_index": _read_json(run_dir / "memory_pinning_index.json"),
                    "route_prior_updates": _read_json(run_dir / "route_prior_updates.json"),
                    "decision_policy_update_suggestions": _read_json(run_dir / "decision_policy_update_suggestions.json"),
                    "feedback_casebook": _read_json(run_dir / "feedback_casebook.json"),
                }
            )
    return candidates


def _score_candidate(*, current: dict[str, Any], candidate: dict[str, Any]) -> dict[str, Any]:
    summary = dict(candidate.get("summary") or {})
    decision = dict(summary.get("decision", {}))
    intent = dict(summary.get("intent", {}))
    data = dict(summary.get("data", {}))
    evidence = dict(summary.get("evidence", {}))
    completion = dict(summary.get("completion", {}))
    lifecycle = dict(summary.get("lifecycle", {}))
    snapshot = {
        "task_type": _optional_str(decision.get("task_type")) or "unknown",
        "domain_archetype": _optional_str(intent.get("domain_archetype")) or "generic_tabular",
        "objective": _optional_str(intent.get("objective")) or "best_robust_pareto_front",
        "primary_metric": _optional_str(decision.get("primary_metric")) or "unknown",
        "selected_route_id": _optional_str(decision.get("selected_route_id")),
        "selected_model_family": _optional_str(decision.get("selected_model_family")),
        "target_column": _optional_str(decision.get("target_column")),
        "data_mode": _optional_str(data.get("data_mode")) or "steady_state",
        "row_count": _coerce_int(data.get("row_count")),
        "column_count": _coerce_int(data.get("column_count")),
        "readiness_level": _optional_str(evidence.get("readiness_level")),
        "challenger_winner": _optional_str(evidence.get("challenger_winner")),
        "completion_action": _optional_str(completion.get("action")),
        "promotion_action": _optional_str(lifecycle.get("promotion_action")),
        "promotion_target": _optional_str(lifecycle.get("promotion_target")),
    }
    score = 0.0
    total_weight = 0.0
    reasons: list[str] = []
    for key, weight, label in [
        ("task_type", 0.24, "same task family"),
        ("domain_archetype", 0.12, "same domain archetype"),
        ("primary_metric", 0.12, "same primary metric"),
        ("selected_route_id", 0.08, "same route history"),
        ("data_mode", 0.06, "same data mode"),
        ("completion_action", 0.08, "similar completion posture"),
        ("promotion_action", 0.06, "similar lifecycle posture"),
    ]:
        current_value = _optional_str(current.get(key))
        candidate_value = _optional_str(snapshot.get(key))
        if not current_value or not candidate_value:
            continue
        total_weight += weight
        if current_value == candidate_value:
            score += weight
            reasons.append(label)
    objective_similarity = _token_overlap_similarity(
        _optional_str(current.get("objective")),
        _optional_str(snapshot.get("objective")),
    )
    if objective_similarity is not None:
        score += objective_similarity * 0.08
        total_weight += 0.08
        if objective_similarity >= 0.5:
            reasons.append("similar objective framing")
    target_similarity = _token_overlap_similarity(
        _optional_str(current.get("target_column")),
        _optional_str(snapshot.get("target_column")),
    )
    if target_similarity is not None:
        score += target_similarity * 0.05
        total_weight += 0.05
        if target_similarity >= 0.5:
            reasons.append("similar target semantics")
    for current_key, candidate_key, weight, label in [
        ("row_count", "row_count", 0.07, "similar dataset size"),
        ("column_count", "column_count", 0.04, "similar feature width"),
    ]:
        similarity = _scaled_size_similarity(
            current=_coerce_int(current.get(current_key)),
            candidate=_coerce_int(snapshot.get(candidate_key)),
        )
        if similarity is None:
            continue
        score += similarity * weight
        total_weight += weight
        if similarity >= 0.7:
            reasons.append(label)
    readiness_bonus = _readiness_bonus(
        readiness_level=_optional_str(snapshot.get("readiness_level")),
        promotion_action=_optional_str(snapshot.get("promotion_action")),
    )
    score += readiness_bonus * 0.10
    total_weight += 0.10
    if readiness_bonus >= 0.8:
        reasons.append("prior run ended with strong evidence")
    pinning_index = dict(candidate.get("memory_pinning_index") or {})
    pin_boost = _pinning_boost(pinning_index)
    if pin_boost is not None:
        score += pin_boost * 0.05
        total_weight += 0.05
        if pin_boost >= 0.5:
            reasons.append("pulse-pinned memory")
    similarity_score = round(score / total_weight, 4) if total_weight > 0.0 else None
    return {
        "run_id": str(summary.get("run_id", "")).strip() or Path(candidate["run_dir"]).name,
        "run_dir": str(candidate["run_dir"]),
        "summary": summary,
        "snapshot": snapshot,
        "similarity_score": similarity_score,
        "relevance_reason": ", ".join(reasons[:4]) if reasons else "artifact-derived partial similarity",
        "match_factors": reasons,
        "provenance": {
            "run_dir": str(candidate["run_dir"]),
            "summary_path": str(candidate["summary_path"]),
            "manifest_path": str(Path(candidate["run_dir"]) / "manifest.json"),
        },
        "challenger_report": dict(candidate.get("challenger_report") or {}),
        "reflection_memory": dict(candidate.get("reflection_memory") or {}),
        "memory_pinning_index": pinning_index,
        "route_prior_updates": dict(candidate.get("route_prior_updates") or {}),
        "decision_policy_update_suggestions": dict(candidate.get("decision_policy_update_suggestions") or {}),
        "feedback_casebook": dict(candidate.get("feedback_casebook") or {}),
    }


def _select_analog_candidates(*, scored_candidates: list[dict[str, Any]], controls: MemoryControls) -> list[dict[str, Any]]:
    eligible = [
        item
        for item in scored_candidates
        if _optional_float(item.get("similarity_score")) is not None
        and float(item["similarity_score"]) >= controls.min_similarity_score
    ]
    ordered = sorted(
        eligible,
        key=lambda item: (-float(item.get("similarity_score", 0.0) or 0.0), str(item.get("run_id", ""))),
    )
    selected = ordered[: controls.max_analog_runs]
    out: list[dict[str, Any]] = []
    for item in selected:
        summary = dict(item.get("summary") or {})
        evidence = dict(summary.get("evidence", {}))
        completion = dict(summary.get("completion", {}))
        lifecycle = dict(summary.get("lifecycle", {}))
        out.append(
            {
                "run_id": str(item.get("run_id", "")),
                "similarity_score": float(item.get("similarity_score", 0.0) or 0.0),
                "relevance_reason": str(item.get("relevance_reason", "analog candidate")).strip(),
                "match_factors": list(item.get("match_factors", [])),
                "snapshot": dict(item.get("snapshot", {})),
                "outcome_summary": {
                    "readiness_level": evidence.get("readiness_level"),
                    "completion_action": completion.get("action"),
                    "promotion_action": lifecycle.get("promotion_action"),
                    "promotion_target": lifecycle.get("promotion_target"),
                    "challenger_winner": evidence.get("challenger_winner"),
                },
                "provenance": dict(item.get("provenance", {})),
                "reflection_excerpt": _optional_str(dict(item.get("reflection_memory", {})).get("summary")),
                "memory_pinning_index": dict(item.get("memory_pinning_index") or {}),
                "challenger_report": dict(item.get("challenger_report") or {}),
                "route_prior_updates": dict(item.get("route_prior_updates") or {}),
                "decision_policy_update_suggestions": dict(item.get("decision_policy_update_suggestions") or {}),
                "feedback_casebook": dict(item.get("feedback_casebook") or {}),
            }
        )
    return out


def _build_route_prior_context(
    *,
    current: dict[str, Any],
    analog_candidates: list[dict[str, Any]],
    controls: MemoryControls,
) -> dict[str, Any]:
    baseline_candidate_order = _default_candidate_order(
        task_type=_optional_str(current.get("task_type")) or "unknown",
        data_mode=_optional_str(current.get("data_mode")) or "steady_state",
    )
    family_scores: dict[str, float] = {}
    analog_ids: list[str] = []
    for item in analog_candidates:
        family = _optional_str(dict(item.get("snapshot", {})).get("selected_model_family"))
        if not family:
            continue
        family_scores[family] = family_scores.get(family, 0.0) + _memory_outcome_weight(item)
        analog_ids.append(str(item.get("run_id", "")))
        for update in dict(item.get("route_prior_updates") or {}).get("updates", []):
            update_family = _optional_str(dict(update).get("model_family"))
            if not update_family:
                continue
            bias = _optional_float(dict(update).get("bias"))
            if bias is None:
                continue
            family_scores[update_family] = family_scores.get(update_family, 0.0) + round(float(bias) * 2.0, 4)
    adjusted = _apply_family_bias(baseline_candidate_order=baseline_candidate_order, family_scores=family_scores)
    changed = adjusted != baseline_candidate_order
    status = "memory_influenced" if changed else ("retrieved_without_change" if analog_candidates else ("disabled" if not controls.enabled else "no_credible_analogs"))
    return {
        "status": status,
        "baseline_candidate_order": baseline_candidate_order,
        "adjusted_candidate_order": adjusted,
        "family_bias": [
            {"model_family": name, "score": round(score, 4), "source": "analog_success_bias"}
            for name, score in sorted(family_scores.items(), key=lambda pair: (-pair[1], pair[0]))
        ],
        "influencing_analogs": _dedupe_strings(analog_ids),
        "counterfactual": {
            "without_memory_candidate_order": baseline_candidate_order,
            "with_memory_candidate_order": adjusted,
            "changed": changed,
        },
        "summary": _route_prior_summary(
            status=status,
            baseline_candidate_order=baseline_candidate_order,
            adjusted_candidate_order=adjusted,
        ),
    }


def _build_challenger_prior_suggestions(
    *,
    current: dict[str, Any],
    analog_candidates: list[dict[str, Any]],
    controls: MemoryControls,
) -> dict[str, Any]:
    champion_family = _optional_str(current.get("selected_model_family"))
    scores: dict[str, float] = {}
    analog_ids: list[str] = []
    for item in analog_candidates:
        challenger_family = _challenger_family_from_candidate(item)
        if not challenger_family or challenger_family == champion_family:
            continue
        scores[challenger_family] = scores.get(challenger_family, 0.0) + _memory_outcome_weight(item)
        analog_ids.append(str(item.get("run_id", "")))
    ranked = [
        {"model_family": name, "score": round(score, 4), "source": "analog_challenger_pressure"}
        for name, score in sorted(scores.items(), key=lambda pair: (-pair[1], pair[0]))
    ]
    preferred = ranked[0]["model_family"] if ranked else None
    status = "memory_influenced" if preferred else ("disabled" if not controls.enabled else "no_credible_analogs")
    return {
        "status": status,
        "preferred_challenger_family": preferred,
        "ranked_families": ranked,
        "influencing_analogs": _dedupe_strings(analog_ids),
        "counterfactual": {
            "without_memory": "bounded challenger fallback order only",
            "with_memory": f"bias toward `{preferred}`" if preferred else "bounded challenger fallback order only",
            "changed": preferred is not None,
        },
        "summary": _challenger_prior_summary(status=status, preferred=preferred),
    }


def _build_reflection_memory(
    *,
    current: dict[str, Any],
    analog_candidates: list[dict[str, Any]],
    route_prior: dict[str, Any],
    challenger_prior: dict[str, Any],
    retrieval_status: str,
    controls: MemoryControls,
    trace: MemoryTrace,
) -> ReflectionMemory:
    memory_delta: list[str] = []
    if dict(route_prior.get("counterfactual", {})).get("changed", False):
        memory_delta.append("planning_candidate_order_changed")
    if dict(challenger_prior.get("counterfactual", {})).get("changed", False):
        memory_delta.append("challenger_bias_changed")
    if not memory_delta:
        memory_delta.append("no_behavior_change_from_memory")
    lessons = []
    if retrieval_status == "no_credible_analogs":
        lessons.append("No credible analog set was available, so Relaytic had to rely on current-run evidence only.")
    if dict(route_prior.get("counterfactual", {})).get("changed", False):
        lessons.append("Analog evidence shifted the first-route model-family order away from the baseline deterministic default.")
    if dict(challenger_prior.get("counterfactual", {})).get("changed", False):
        lessons.append("Analog evidence suggested a more specific challenger family than the bounded fallback order.")
    if analog_candidates:
        lessons.append("Top analog provenance stayed summary-level and artifact-derived rather than relying on raw training rows.")
    blocking_layer = _optional_str(current.get("blocking_layer"))
    if blocking_layer:
        lessons.append(f"Current completion pressure is still concentrated in `{blocking_layer}`.")
    reusable_priors = [
        f"task_type:{current.get('task_type')}",
        f"domain_archetype:{current.get('domain_archetype')}",
    ]
    adjusted = list(route_prior.get("adjusted_candidate_order", []))
    if adjusted:
        reusable_priors.append(f"candidate_order:{' > '.join(adjusted[:3])}")
    preferred = _optional_str(challenger_prior.get("preferred_challenger_family"))
    if preferred:
        reusable_priors.append(f"challenger_bias:{preferred}")
    failure_modes = []
    if retrieval_status == "no_credible_analogs":
        failure_modes.append("No close prior analogs")
    completion_action = _optional_str(current.get("completion_action"))
    if completion_action in {"continue_experimentation", "benchmark_needed", "memory_support_needed"}:
        failure_modes.append(f"completion_action:{completion_action}")
    return ReflectionMemory(
        schema_version=REFLECTION_MEMORY_SCHEMA_VERSION,
        generated_at=_utc_now(),
        controls=controls,
        current_run_id=str(current.get("run_id", "run")),
        current_stage=str(current.get("current_stage", "unknown")).strip() or "unknown",
        analog_count=len(analog_candidates),
        lessons=_dedupe_strings(lessons)[:6],
        reusable_priors=_dedupe_strings(reusable_priors)[:6],
        failure_modes=failure_modes[:5],
        memory_delta=memory_delta,
        summary=_reflection_summary(
            current_stage=str(current.get("current_stage", "unknown")).strip() or "unknown",
            retrieval_status=retrieval_status,
            analog_count=len(analog_candidates),
        ),
        trace=trace,
    )


def _default_candidate_order(*, task_type: str, data_mode: str) -> list[str]:
    if data_mode == "time_series" and _is_classification_task(task_type):
        return ["lagged_logistic_regression", "lagged_tree_classifier", "logistic_regression", "bagged_tree_classifier", "boosted_tree_classifier"]
    if data_mode == "time_series":
        return ["lagged_linear", "lagged_tree_ensemble", "linear_ridge", "bagged_tree_ensemble", "boosted_tree_ensemble"]
    if _is_classification_task(task_type):
        return ["logistic_regression", "bagged_tree_classifier", "boosted_tree_classifier"]
    return ["linear_ridge", "bagged_tree_ensemble", "boosted_tree_ensemble"]


def _apply_family_bias(*, baseline_candidate_order: list[str], family_scores: dict[str, float]) -> list[str]:
    if not family_scores:
        return list(baseline_candidate_order)
    ranked = sorted(
        baseline_candidate_order,
        key=lambda name: (-family_scores.get(name, 0.0), baseline_candidate_order.index(name)),
    )
    unseen = [
        name
        for name, score in sorted(family_scores.items(), key=lambda pair: (-pair[1], pair[0]))
        if name not in ranked and score > 0.0
    ]
    return _dedupe_strings(ranked + unseen)


def _memory_outcome_weight(candidate: dict[str, Any]) -> float:
    base = float(candidate.get("similarity_score", 0.0) or 0.0)
    outcome = dict(candidate.get("outcome_summary", {}))
    multiplier = 1.0
    if _optional_str(outcome.get("readiness_level")) == "strong":
        multiplier += 0.20
    if _optional_str(outcome.get("promotion_action")) == "promote_challenger":
        multiplier += 0.10
    if _optional_str(outcome.get("promotion_action")) == "hold_promotion":
        multiplier -= 0.10
    if _optional_str(outcome.get("completion_action")) in {"benchmark_needed", "memory_support_needed"}:
        multiplier -= 0.15
    return round(max(0.0, base * multiplier), 4)


def _pinning_boost(pinning_index: dict[str, Any]) -> float | None:
    entries = [dict(item) for item in pinning_index.get("entries", []) if isinstance(item, dict)]
    if not entries:
        return None
    boosts: list[float] = []
    for item in entries:
        value = _optional_float(item.get("retrieval_boost"))
        if value is None:
            continue
        boosts.append(max(0.0, min(1.0, value / 0.10)))
    if not boosts:
        return None
    return max(boosts)


def _challenger_family_from_candidate(candidate: dict[str, Any]) -> str | None:
    outcome = dict(candidate.get("outcome_summary", {}))
    promotion_target = _optional_str(outcome.get("promotion_target"))
    if promotion_target:
        return promotion_target
    challenger_report = dict(candidate.get("challenger_report", {}))
    comparison = dict(challenger_report.get("comparison", {}))
    return _optional_str(comparison.get("challenger_model_family")) or _optional_str(comparison.get("selected_model_family"))


def _retrieval_status(*, controls: MemoryControls, analog_candidates: list[dict[str, Any]]) -> str:
    if not controls.enabled or not controls.allow_prior_retrieval:
        return "disabled"
    if analog_candidates:
        return "retrieval_completed"
    return "no_credible_analogs"


def _with_memory_counterfactual(*, route_prior: dict[str, Any], challenger_prior: dict[str, Any]) -> str:
    route_changed = bool(dict(route_prior.get("counterfactual", {})).get("changed", False))
    challenger_changed = bool(dict(challenger_prior.get("counterfactual", {})).get("changed", False))
    if route_changed and challenger_changed:
        return "Relaytic changed both planning candidate order and challenger bias because analogs were available."
    if route_changed:
        return "Relaytic changed planning candidate order because analogs were available."
    if challenger_changed:
        return "Relaytic changed challenger bias because analogs were available."
    return "Relaytic retrieved analogs but kept the same deterministic route and challenger defaults."


def _retrieval_summary(*, retrieval_status: str, analog_count: int) -> str:
    if retrieval_status == "disabled":
        return "Relaytic memory retrieval is disabled by policy."
    if retrieval_status == "no_credible_analogs":
        return "Relaytic searched local prior runs but did not find a credible analog set."
    return f"Relaytic retrieved {analog_count} prior analog run(s) with explicit provenance."


def _candidate_summary(candidates: list[dict[str, Any]]) -> str:
    if not candidates:
        return "No credible analog runs were retrieved."
    return f"Relaytic ranked {len(candidates)} prior run(s) as current analogs."


def _route_prior_summary(*, status: str, baseline_candidate_order: list[str], adjusted_candidate_order: list[str]) -> str:
    if status == "memory_influenced":
        return (
            "Relaytic adjusted the candidate family order from `"
            + ", ".join(baseline_candidate_order)
            + "` to `"
            + ", ".join(adjusted_candidate_order)
            + "` using prior analog evidence."
        )
    if status == "retrieved_without_change":
        return "Relaytic retrieved analogs but kept the original planning candidate order."
    if status == "disabled":
        return "Relaytic memory is disabled, so planning stayed purely current-run local."
    return "Relaytic did not find a credible analog set that should influence planning."


def _challenger_prior_summary(*, status: str, preferred: str | None) -> str:
    if status == "memory_influenced" and preferred:
        return f"Relaytic suggests challenger family `{preferred}` based on prior analog pressure."
    if status == "disabled":
        return "Relaytic memory is disabled, so challenger design stayed purely local."
    return "Relaytic did not find a credible analog set that should influence challenger selection."


def _reflection_summary(*, current_stage: str, retrieval_status: str, analog_count: int) -> str:
    return (
        f"Relaytic flushed reflection memory at `{current_stage}` with retrieval status `{retrieval_status}` "
        f"and {analog_count} analog candidate(s)."
    )


def _flush_summary(*, retrieval_status: str, analog_count: int, current_stage: str) -> str:
    return (
        f"Relaytic flushed memory artifacts at `{current_stage}` with status `{retrieval_status}` "
        f"and {analog_count} analog candidate(s)."
    )


def _token_overlap_similarity(left: str | None, right: str | None) -> float | None:
    left_tokens = _normalized_tokens(left)
    right_tokens = _normalized_tokens(right)
    if not left_tokens or not right_tokens:
        return None
    overlap = len(left_tokens & right_tokens)
    union = len(left_tokens | right_tokens)
    if union <= 0:
        return None
    return overlap / union


def _normalized_tokens(value: str | None) -> set[str]:
    text = str(value or "").strip().lower()
    if not text:
        return set()
    return {token for token in re.split(r"[^a-z0-9]+", text) if token}


def _scaled_size_similarity(*, current: int | None, candidate: int | None) -> float | None:
    if current is None or candidate is None or current <= 0 or candidate <= 0:
        return None
    return min(current, candidate) / max(current, candidate)


def _readiness_bonus(*, readiness_level: str | None, promotion_action: str | None) -> float:
    if readiness_level == "strong":
        return 1.0
    if promotion_action in {"keep_current_champion", "promote_challenger"}:
        return 0.8
    if readiness_level == "conditional":
        return 0.55
    return 0.35


def _is_classification_task(task_type: str) -> bool:
    return task_type in {
        "binary_classification",
        "multiclass_classification",
        "fraud_detection",
        "anomaly_detection",
    } or "classification" in task_type


def _bundle_item(bundle: dict[str, Any], key: str) -> dict[str, Any]:
    payload = bundle.get(key)
    return dict(payload) if isinstance(payload, dict) else {}


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _coerce_int(value: Any) -> int | None:
    try:
        if value is None:
            return None
        return int(value)
    except (TypeError, ValueError):
        return None


def _optional_str(value: Any) -> str | None:
    text = str(value or "").strip()
    return text or None


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


def _format_score(value: Any) -> str:
    parsed = _optional_float(value)
    if parsed is None:
        return "n/a"
    return f"{parsed:.2f}"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()
