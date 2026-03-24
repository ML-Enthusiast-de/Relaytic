"""Slice 10 feedback assimilation and outcome learning."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .models import (
    DECISION_POLICY_UPDATE_SUGGESTIONS_SCHEMA_VERSION,
    FEEDBACK_CASEBOOK_SCHEMA_VERSION,
    FEEDBACK_EFFECT_REPORT_SCHEMA_VERSION,
    FEEDBACK_INTAKE_SCHEMA_VERSION,
    FEEDBACK_VALIDATION_SCHEMA_VERSION,
    OUTCOME_OBSERVATION_REPORT_SCHEMA_VERSION,
    POLICY_UPDATE_SUGGESTIONS_SCHEMA_VERSION,
    ROUTE_PRIOR_UPDATES_SCHEMA_VERSION,
    DecisionPolicyUpdateSuggestions,
    FeedbackBundle,
    FeedbackCasebook,
    FeedbackControls,
    FeedbackEffectReport,
    FeedbackIntake,
    FeedbackTrace,
    FeedbackValidation,
    OutcomeObservationReport,
    PolicyUpdateSuggestions,
    RoutePriorUpdates,
    build_feedback_controls_from_policy,
)
from .storage import FEEDBACK_FILENAMES, read_feedback_bundle, write_feedback_bundle, write_feedback_intake_artifact


ADVERSARIAL_PATTERNS = (
    "ignore safeguards",
    "skip validation",
    "disable benchmark",
    "always use",
    "never challenge",
    "trust me",
    "hide this",
)

POSITIVE_ROUTE_PATTERNS = ("prefer", "use", "promote", "better", "won", "stronger", "worked")
NEGATIVE_ROUTE_PATTERNS = ("avoid", "failed", "weaker", "underperform", "regressed", "bad", "worse")

OUTCOME_POSITIVE = {"correct_override", "successful_intervention", "good_deferral", "good_review"}
OUTCOME_NEGATIVE = {"false_positive", "false_negative", "drift", "regime_shift", "harmful_delay", "missed_case"}


@dataclass(frozen=True)
class FeedbackRunResult:
    """Feedback artifacts plus human-readable review output."""

    bundle: FeedbackBundle
    review_markdown: str


def append_feedback_entries(
    run_dir: str | Path,
    *,
    entries: list[dict[str, Any]],
    policy: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Append feedback/outcome entries to the canonical intake artifact."""
    root = Path(run_dir)
    root.mkdir(parents=True, exist_ok=True)
    existing_bundle = read_feedback_bundle(root)
    existing_intake = dict(existing_bundle.get("feedback_intake", {}))
    current_entries = list(existing_intake.get("entries", []))
    controls = build_feedback_controls_from_policy(policy or {})
    for entry in entries:
        normalized = _normalize_feedback_entry(entry, index=len(current_entries) + 1)
        current_entries.append(normalized)
    payload = _build_feedback_intake_payload(entries=current_entries, controls=controls)
    write_feedback_intake_artifact(root, payload)
    return payload


def rollback_feedback_entry(
    run_dir: str | Path,
    *,
    feedback_id: str,
    policy: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Mark one feedback entry as reverted in the canonical intake artifact."""
    root = Path(run_dir)
    bundle = read_feedback_bundle(root)
    intake = dict(bundle.get("feedback_intake", {}))
    entries = list(intake.get("entries", []))
    target_id = str(feedback_id).strip()
    found = False
    for item in entries:
        if str(item.get("feedback_id", "")).strip() != target_id:
            continue
        item["entry_state"] = "reverted"
        item["reverted_at"] = _utc_now()
        found = True
        break
    if not found:
        raise ValueError(f"Feedback entry not found: {feedback_id}")
    controls = build_feedback_controls_from_policy(policy or {})
    payload = _build_feedback_intake_payload(entries=entries, controls=controls)
    write_feedback_intake_artifact(root, payload)
    return payload


def run_feedback_review(
    *,
    run_dir: str | Path,
    policy: dict[str, Any],
    planning_bundle: dict[str, Any] | None = None,
    evidence_bundle: dict[str, Any] | None = None,
    completion_bundle: dict[str, Any] | None = None,
    lifecycle_bundle: dict[str, Any] | None = None,
    autonomy_bundle: dict[str, Any] | None = None,
    benchmark_bundle: dict[str, Any] | None = None,
    memory_bundle: dict[str, Any] | None = None,
) -> FeedbackRunResult:
    """Validate current feedback/outcome evidence and synthesize reversible effects."""
    root = Path(run_dir)
    controls = build_feedback_controls_from_policy(policy)
    if not controls.enabled:
        bundle = _build_empty_feedback_bundle(controls=controls, status="disabled")
        return FeedbackRunResult(bundle=bundle, review_markdown=render_feedback_review_markdown(bundle.to_dict()))

    existing_bundle = read_feedback_bundle(root)
    intake_payload = dict(existing_bundle.get("feedback_intake", {}))
    entries = list(intake_payload.get("entries", []))
    intake_artifact = _feedback_intake_from_entries(entries=entries, controls=controls)

    current_context = _current_context_snapshot(
        planning_bundle=planning_bundle or {},
        evidence_bundle=evidence_bundle or {},
        completion_bundle=completion_bundle or {},
        lifecycle_bundle=lifecycle_bundle or {},
        benchmark_bundle=benchmark_bundle or {},
    )
    validated = [_validate_feedback_entry(entry, controls=controls, current_context=current_context) for entry in entries]
    validation_artifact = _build_feedback_validation_artifact(validated=validated, controls=controls)
    route_updates_artifact = _build_route_prior_updates_artifact(validated=validated, controls=controls)
    policy_updates_artifact = _build_policy_update_suggestions_artifact(validated=validated, controls=controls)
    decision_updates_artifact = _build_decision_policy_update_suggestions_artifact(validated=validated, controls=controls)
    outcome_report_artifact = _build_outcome_observation_report_artifact(validated=validated, controls=controls)
    effect_report_artifact = _build_feedback_effect_report_artifact(
        validated=validated,
        controls=controls,
        route_updates=route_updates_artifact,
        policy_updates=policy_updates_artifact,
        decision_updates=decision_updates_artifact,
    )
    casebook_artifact = _build_feedback_casebook_artifact(
        validated=validated,
        controls=controls,
        route_updates=route_updates_artifact,
        policy_updates=policy_updates_artifact,
        decision_updates=decision_updates_artifact,
    )
    bundle = FeedbackBundle(
        feedback_intake=intake_artifact,
        feedback_validation=validation_artifact,
        feedback_effect_report=effect_report_artifact,
        feedback_casebook=casebook_artifact,
        outcome_observation_report=outcome_report_artifact,
        decision_policy_update_suggestions=decision_updates_artifact,
        policy_update_suggestions=policy_updates_artifact,
        route_prior_updates=route_updates_artifact,
    )
    write_feedback_bundle(root, bundle=bundle)
    return FeedbackRunResult(bundle=bundle, review_markdown=render_feedback_review_markdown(bundle.to_dict()))


def render_feedback_review_markdown(bundle: dict[str, Any]) -> str:
    """Render the current feedback bundle for humans."""
    intake = dict(bundle.get("feedback_intake", {}))
    validation = dict(bundle.get("feedback_validation", {}))
    effect = dict(bundle.get("feedback_effect_report", {}))
    route_updates = dict(bundle.get("route_prior_updates", {}))
    decision_updates = dict(bundle.get("decision_policy_update_suggestions", {}))
    policy_updates = dict(bundle.get("policy_update_suggestions", {}))
    outcome = dict(bundle.get("outcome_observation_report", {}))
    lines = [
        "# Relaytic Feedback Review",
        "",
        f"- Intake status: `{intake.get('status', 'unknown')}`",
        f"- Total feedback count: `{int(intake.get('total_count', 0) or 0)}`",
        f"- Accepted feedback count: `{int(validation.get('accepted_count', 0) or 0)}`",
        f"- Rejected feedback count: `{int(validation.get('rejected_count', 0) or 0)}`",
        f"- Reverted feedback count: `{int(validation.get('reverted_count', 0) or 0)}`",
        f"- Primary recommended action: `{effect.get('primary_recommended_action') or 'none'}`",
        f"- Route prior updates: `{len(route_updates.get('updates', []))}`",
        f"- Decision-policy suggestions: `{len(decision_updates.get('suggestions', []))}`",
        f"- Policy suggestions: `{len(policy_updates.get('suggestions', []))}`",
        f"- Outcome contradictions: `{int(outcome.get('contradiction_count', 0) or 0)}`",
    ]
    top_route = dict((route_updates.get("updates") or [{}])[0])
    if top_route.get("model_family"):
        lines.append(f"- Top route prior update: `{top_route.get('model_family')}` with bias `{top_route.get('bias')}`")
    top_decision = dict((decision_updates.get("suggestions") or [{}])[0])
    if top_decision.get("suggestion"):
        lines.append(f"- Top decision-policy suggestion: `{top_decision.get('suggestion')}`")
    lines.extend(["", "## Summary", "", str(effect.get("summary", "No feedback effect summary available."))])
    return "\n".join(lines).rstrip() + "\n"


def _build_empty_feedback_bundle(*, controls: FeedbackControls, status: str) -> FeedbackBundle:
    trace = _trace(note="feedback controls disabled")
    now = _utc_now()
    empty_validation = FeedbackValidation(
        schema_version=FEEDBACK_VALIDATION_SCHEMA_VERSION,
        generated_at=now,
        controls=controls,
        status=status,
        accepted_count=0,
        downgraded_count=0,
        rejected_count=0,
        reverted_count=0,
        accepted_entries=[],
        downgraded_entries=[],
        rejected_entries=[],
        reverted_entries=[],
        trust_summary={"accepted_average": None, "rejected_average": None},
        summary="Feedback review is disabled by policy.",
        trace=trace,
    )
    empty_intake = FeedbackIntake(
        schema_version=FEEDBACK_INTAKE_SCHEMA_VERSION,
        generated_at=now,
        controls=controls,
        status=status,
        total_count=0,
        active_count=0,
        reverted_count=0,
        source_types=[],
        entries=[],
        summary="Feedback intake is disabled by policy.",
        trace=trace,
    )
    empty_route = RoutePriorUpdates(
        schema_version=ROUTE_PRIOR_UPDATES_SCHEMA_VERSION,
        generated_at=now,
        controls=controls,
        status=status,
        updates=[],
        summary="Feedback-derived route updates are disabled by policy.",
        trace=trace,
    )
    empty_policy = PolicyUpdateSuggestions(
        schema_version=POLICY_UPDATE_SUGGESTIONS_SCHEMA_VERSION,
        generated_at=now,
        controls=controls,
        status=status,
        suggestions=[],
        summary="Feedback-derived policy suggestions are disabled by policy.",
        trace=trace,
    )
    empty_decision = DecisionPolicyUpdateSuggestions(
        schema_version=DECISION_POLICY_UPDATE_SUGGESTIONS_SCHEMA_VERSION,
        generated_at=now,
        controls=controls,
        status=status,
        suggestions=[],
        primary_recommended_action=None,
        summary="Feedback-derived decision-policy suggestions are disabled by policy.",
        trace=trace,
    )
    empty_outcome = OutcomeObservationReport(
        schema_version=OUTCOME_OBSERVATION_REPORT_SCHEMA_VERSION,
        generated_at=now,
        controls=controls,
        status=status,
        accepted_outcome_count=0,
        contradiction_count=0,
        positive_outcome_count=0,
        negative_outcome_count=0,
        observed_entries=[],
        summary="No outcome observations were processed.",
        trace=trace,
    )
    empty_effect = FeedbackEffectReport(
        schema_version=FEEDBACK_EFFECT_REPORT_SCHEMA_VERSION,
        generated_at=now,
        controls=controls,
        status=status,
        active_feedback_count=0,
        accepted_feedback_count=0,
        downgraded_feedback_count=0,
        rejected_feedback_count=0,
        reverted_feedback_count=0,
        changed_future_route_recommendations=False,
        changed_policy_suggestions=False,
        changed_decision_policy_recommendations=False,
        primary_recommended_action=None,
        accepted_feedback_ids=[],
        reverted_feedback_ids=[],
        changed_artifacts=[],
        summary="Feedback review is disabled by policy.",
        trace=trace,
    )
    empty_casebook = FeedbackCasebook(
        schema_version=FEEDBACK_CASEBOOK_SCHEMA_VERSION,
        generated_at=now,
        controls=controls,
        status=status,
        accepted_cases=[],
        rejected_cases=[],
        reverted_cases=[],
        source_counts={},
        effect_counts={"route_prior_updates": 0, "policy_suggestions": 0, "decision_policy_suggestions": 0},
        summary="Feedback casebook is disabled by policy.",
        trace=trace,
    )
    return FeedbackBundle(
        feedback_intake=empty_intake,
        feedback_validation=empty_validation,
        feedback_effect_report=empty_effect,
        feedback_casebook=empty_casebook,
        outcome_observation_report=empty_outcome,
        decision_policy_update_suggestions=empty_decision,
        policy_update_suggestions=empty_policy,
        route_prior_updates=empty_route,
    )


def _build_feedback_intake_payload(*, entries: list[dict[str, Any]], controls: FeedbackControls) -> dict[str, Any]:
    artifact = _feedback_intake_from_entries(entries=entries, controls=controls)
    return artifact.to_dict()


def _feedback_intake_from_entries(*, entries: list[dict[str, Any]], controls: FeedbackControls) -> FeedbackIntake:
    normalized_entries = [_normalize_feedback_entry(entry, index=index + 1) for index, entry in enumerate(entries)]
    reverted_count = sum(1 for entry in normalized_entries if str(entry.get("entry_state", "")).strip() == "reverted")
    active_count = len(normalized_entries) - reverted_count
    source_types = sorted(
        {
            str(entry.get("source_type", "")).strip()
            for entry in normalized_entries
            if str(entry.get("source_type", "")).strip()
        }
    )
    status = "intake_recorded" if normalized_entries else "no_feedback"
    summary = (
        f"Relaytic recorded {len(normalized_entries)} feedback/outcome packet(s), with {active_count} still active."
        if normalized_entries
        else "Relaytic has not recorded any feedback or outcome packets yet."
    )
    return FeedbackIntake(
        schema_version=FEEDBACK_INTAKE_SCHEMA_VERSION,
        generated_at=_utc_now(),
        controls=controls,
        status=status,
        total_count=len(normalized_entries),
        active_count=active_count,
        reverted_count=reverted_count,
        source_types=source_types,
        entries=normalized_entries,
        summary=summary,
        trace=_trace(note="feedback intake refreshed"),
    )


def _normalize_feedback_entry(entry: dict[str, Any], *, index: int) -> dict[str, Any]:
    payload = dict(entry or {})
    feedback_id = _clean_text(payload.get("feedback_id")) or f"feedback_{index:04d}"
    source_type = _normalize_source_type(payload.get("source_type"))
    feedback_type = _normalize_feedback_type(payload.get("feedback_type"), source_type=source_type)
    message = str(payload.get("message", "")).strip()
    return {
        "feedback_id": feedback_id,
        "received_at": str(payload.get("received_at", "")).strip() or _utc_now(),
        "source_type": source_type,
        "feedback_type": feedback_type,
        "actor_type": str(payload.get("actor_type", "")).strip() or ("user" if source_type == "human" else "agent"),
        "actor_name": str(payload.get("actor_name", "")).strip() or None,
        "message": message,
        "suggested_route_family": _clean_text(payload.get("suggested_route_family")),
        "suggested_action": _clean_text(payload.get("suggested_action")),
        "observed_outcome": _normalize_observed_outcome(payload.get("observed_outcome")),
        "evidence_level": _normalize_evidence_level(payload.get("evidence_level"), source_type=source_type),
        "metric_name": _clean_text(payload.get("metric_name")),
        "metric_value": _coerce_float(payload.get("metric_value")),
        "source_artifacts": [str(item).strip() for item in payload.get("source_artifacts", []) if str(item).strip()],
        "effect_direction": _normalize_effect_direction(payload.get("effect_direction"), message=message),
        "entry_state": "reverted" if str(payload.get("entry_state", "")).strip() == "reverted" else "active",
        "reverted_at": _clean_text(payload.get("reverted_at")),
        "channel": _clean_text(payload.get("channel")),
        "notes": _clean_text(payload.get("notes")),
    }


def _current_context_snapshot(
    *,
    planning_bundle: dict[str, Any],
    evidence_bundle: dict[str, Any],
    completion_bundle: dict[str, Any],
    lifecycle_bundle: dict[str, Any],
    benchmark_bundle: dict[str, Any],
) -> dict[str, Any]:
    plan = dict(planning_bundle.get("plan", {}))
    execution = dict(plan.get("execution_summary", {}))
    audit = dict(evidence_bundle.get("audit_report", {}))
    completion = dict(completion_bundle.get("completion_decision", {}))
    promotion = dict(lifecycle_bundle.get("promotion_decision", {}))
    benchmark = dict(benchmark_bundle.get("benchmark_parity_report", {}))
    return {
        "selected_model_family": _clean_text(execution.get("selected_model_family")) or _clean_text(plan.get("selected_model_family")),
        "task_type": _clean_text(plan.get("task_type")),
        "primary_metric": _clean_text(plan.get("primary_metric")),
        "readiness_level": _clean_text(audit.get("readiness_level")),
        "benchmark_recommended_action": _clean_text(benchmark.get("recommended_action")),
        "completion_action": _clean_text(completion.get("action")),
        "promotion_action": _clean_text(promotion.get("action")),
    }


def _validate_feedback_entry(entry: dict[str, Any], *, controls: FeedbackControls, current_context: dict[str, Any]) -> dict[str, Any]:
    normalized = _normalize_feedback_entry(entry, index=1)
    reasons: list[str] = []
    trust_score = _base_trust_for_source(normalized["source_type"])
    if normalized["entry_state"] == "reverted":
        return {
            **normalized,
            "validation_status": "reverted",
            "trust_score": 1.0,
            "validation_reasons": ["entry was explicitly reverted"],
        }
    if not _source_allowed(source_type=normalized["source_type"], controls=controls):
        return {
            **normalized,
            "validation_status": "rejected",
            "trust_score": 0.0,
            "validation_reasons": ["feedback source type is disabled by policy"],
        }
    if normalized["message"]:
        if len(normalized["message"]) >= 24:
            trust_score += 0.05
            reasons.append("message includes non-trivial rationale")
        else:
            trust_score -= 0.06
            reasons.append("message is too short to carry much reusable signal")
    else:
        trust_score -= 0.08
        reasons.append("message is empty")
    evidence_level = normalized["evidence_level"]
    if evidence_level == "strong":
        trust_score += 0.12
        reasons.append("entry carries strong evidence level")
    elif evidence_level == "medium":
        trust_score += 0.05
        reasons.append("entry carries moderate evidence level")
    else:
        trust_score -= 0.04
        reasons.append("entry only carries weak evidence level")
    if normalized["metric_name"] and normalized["metric_value"] is not None:
        trust_score += 0.05
        reasons.append("entry includes structured metric evidence")
    if normalized["source_artifacts"]:
        trust_score += 0.05
        reasons.append("entry cites concrete artifact provenance")
    lowered_message = normalized["message"].lower()
    if any(pattern in lowered_message for pattern in ADVERSARIAL_PATTERNS):
        trust_score -= 0.45
        reasons.append("entry contains adversarial or policy-bypassing language")
    if normalized["source_type"] == "external_agent" and not normalized["source_artifacts"] and normalized["metric_value"] is None:
        trust_score -= 0.15
        reasons.append("external-agent feedback lacks concrete evidence")
    if normalized["source_type"] == "outcome_observation" and not normalized["observed_outcome"]:
        trust_score -= 0.25
        reasons.append("outcome observation is missing a concrete observed outcome")
    suggested_family = normalized["suggested_route_family"]
    if suggested_family and current_context.get("selected_model_family") and suggested_family == current_context["selected_model_family"]:
        trust_score -= 0.04
        reasons.append("suggested family does not differ from the current selected family")
    if suggested_family and not _known_model_family(suggested_family):
        trust_score -= 0.10
        reasons.append("suggested model family is unknown to Relaytic")
    trust_score = round(max(0.0, min(1.0, trust_score)), 4)
    if trust_score >= controls.min_acceptance_score:
        status = "accepted"
    elif trust_score >= controls.downgrade_threshold:
        status = "downgraded"
    else:
        status = "rejected"
    return {
        **normalized,
        "validation_status": status,
        "trust_score": trust_score,
        "validation_reasons": reasons[:6],
    }


def _build_feedback_validation_artifact(*, validated: list[dict[str, Any]], controls: FeedbackControls) -> FeedbackValidation:
    accepted = [item for item in validated if item["validation_status"] == "accepted"]
    downgraded = [item for item in validated if item["validation_status"] == "downgraded"]
    rejected = [item for item in validated if item["validation_status"] == "rejected"]
    reverted = [item for item in validated if item["validation_status"] == "reverted"]
    accepted_scores = [float(item["trust_score"]) for item in accepted]
    rejected_scores = [float(item["trust_score"]) for item in rejected]
    status = "validated" if validated else "no_feedback"
    summary = (
        f"Relaytic accepted {len(accepted)} feedback packet(s), downgraded {len(downgraded)}, rejected {len(rejected)}, and marked {len(reverted)} as reverted."
        if validated
        else "Relaytic had no feedback or outcome packets to validate."
    )
    return FeedbackValidation(
        schema_version=FEEDBACK_VALIDATION_SCHEMA_VERSION,
        generated_at=_utc_now(),
        controls=controls,
        status=status,
        accepted_count=len(accepted),
        downgraded_count=len(downgraded),
        rejected_count=len(rejected),
        reverted_count=len(reverted),
        accepted_entries=accepted,
        downgraded_entries=downgraded,
        rejected_entries=rejected,
        reverted_entries=reverted,
        trust_summary={
            "accepted_average": round(sum(accepted_scores) / len(accepted_scores), 4) if accepted_scores else None,
            "rejected_average": round(sum(rejected_scores) / len(rejected_scores), 4) if rejected_scores else None,
        },
        summary=summary,
        trace=_trace(note="feedback validation complete"),
    )


def _build_route_prior_updates_artifact(*, validated: list[dict[str, Any]], controls: FeedbackControls) -> RoutePriorUpdates:
    updates_by_family: dict[str, dict[str, Any]] = {}
    if controls.allow_route_prior_updates:
        for item in validated:
            if item["validation_status"] != "accepted":
                continue
            if item["feedback_type"] not in {"route_quality", "outcome_evidence"} and item["source_type"] != "benchmark_review":
                continue
            family = _clean_text(item.get("suggested_route_family"))
            if not family or not _known_model_family(family):
                continue
            direction = _normalize_effect_direction(item.get("effect_direction"), message=str(item.get("message", "")))
            bias = float(item.get("trust_score", 0.0) or 0.0)
            signed_bias = bias if direction == "increase" else -bias
            existing = updates_by_family.setdefault(
                family,
                {
                    "model_family": family,
                    "bias": 0.0,
                    "confidence": 0.0,
                    "source_feedback_ids": [],
                    "source_types": set(),
                    "rationale": [],
                },
            )
            existing["bias"] += signed_bias
            existing["confidence"] = max(existing["confidence"], bias)
            existing["source_feedback_ids"].append(str(item["feedback_id"]))
            existing["source_types"].add(str(item["source_type"]))
            rationale = _clean_text(item.get("message")) or f"accepted {item['source_type']} feedback"
            existing["rationale"].append(rationale)
    updates = [
        {
            "model_family": family,
            "bias": round(payload["bias"], 4),
            "direction": "increase" if payload["bias"] >= 0.0 else "decrease",
            "confidence": round(payload["confidence"], 4),
            "source_feedback_ids": _dedupe_strings(payload["source_feedback_ids"]),
            "source_types": sorted(payload["source_types"]),
            "rationale": "; ".join(_dedupe_strings(payload["rationale"])[:3]),
        }
        for family, payload in sorted(updates_by_family.items(), key=lambda item: (-abs(float(item[1]["bias"])), item[0]))
        if abs(float(payload["bias"])) > 0.0
    ]
    status = "suggested_updates" if updates else ("disabled" if not controls.allow_route_prior_updates else "no_updates")
    summary = (
        f"Relaytic derived {len(updates)} feedback-backed route-prior update(s)."
        if updates
        else "Relaytic did not derive any feedback-backed route-prior updates."
    )
    return RoutePriorUpdates(
        schema_version=ROUTE_PRIOR_UPDATES_SCHEMA_VERSION,
        generated_at=_utc_now(),
        controls=controls,
        status=status,
        updates=updates,
        summary=summary,
        trace=_trace(note="route-prior update suggestions built"),
    )


def _build_policy_update_suggestions_artifact(*, validated: list[dict[str, Any]], controls: FeedbackControls) -> PolicyUpdateSuggestions:
    suggestions: list[dict[str, Any]] = []
    if controls.allow_policy_update_suggestions:
        for item in validated:
            if item["validation_status"] != "accepted":
                continue
            suggestion = None
            message = str(item.get("message", "")).lower()
            if item["feedback_type"] == "data_quality":
                suggestion = "tighten_data_quality_gate"
            elif "missing" in message:
                suggestion = "raise_missingness_alert_sensitivity"
            elif "label" in message:
                suggestion = "schedule_label_audit"
            elif item["observed_outcome"] in {"drift", "regime_shift"}:
                suggestion = "collect_fresh_local_snapshot"
            if not suggestion:
                continue
            suggestions.append(
                {
                    "suggestion": suggestion,
                    "confidence": float(item.get("trust_score", 0.0) or 0.0),
                    "source_feedback_ids": [str(item["feedback_id"])],
                    "source_type": str(item["source_type"]),
                    "rationale": _clean_text(item.get("message")) or f"accepted {item['source_type']} evidence",
                }
            )
    suggestions = sorted(suggestions, key=lambda item: (-float(item["confidence"]), item["suggestion"]))
    status = "suggested_updates" if suggestions else ("disabled" if not controls.allow_policy_update_suggestions else "no_updates")
    summary = (
        f"Relaytic derived {len(suggestions)} feedback-backed policy suggestion(s)."
        if suggestions
        else "Relaytic did not derive any feedback-backed policy suggestions."
    )
    return PolicyUpdateSuggestions(
        schema_version=POLICY_UPDATE_SUGGESTIONS_SCHEMA_VERSION,
        generated_at=_utc_now(),
        controls=controls,
        status=status,
        suggestions=suggestions,
        summary=summary,
        trace=_trace(note="policy update suggestions built"),
    )


def _build_decision_policy_update_suggestions_artifact(
    *,
    validated: list[dict[str, Any]],
    controls: FeedbackControls,
) -> DecisionPolicyUpdateSuggestions:
    suggestions: list[dict[str, Any]] = []
    if controls.allow_decision_policy_update_suggestions:
        for item in validated:
            if item["validation_status"] != "accepted":
                continue
            derived = _decision_policy_suggestion_from_entry(item)
            if not derived:
                continue
            suggestions.append(
                {
                    "suggestion": derived,
                    "confidence": float(item.get("trust_score", 0.0) or 0.0),
                    "source_feedback_ids": [str(item["feedback_id"])],
                    "source_type": str(item["source_type"]),
                    "rationale": _clean_text(item.get("message")) or f"accepted {item['source_type']} evidence",
                }
            )
    suggestions = sorted(suggestions, key=lambda item: (-float(item["confidence"]), item["suggestion"]))
    primary = suggestions[0]["suggestion"] if suggestions else None
    status = "suggested_updates" if suggestions else ("disabled" if not controls.allow_decision_policy_update_suggestions else "no_updates")
    summary = (
        f"Relaytic derived {len(suggestions)} feedback-backed decision-policy suggestion(s)."
        if suggestions
        else "Relaytic did not derive any feedback-backed decision-policy suggestions."
    )
    return DecisionPolicyUpdateSuggestions(
        schema_version=DECISION_POLICY_UPDATE_SUGGESTIONS_SCHEMA_VERSION,
        generated_at=_utc_now(),
        controls=controls,
        status=status,
        suggestions=suggestions,
        primary_recommended_action=primary,
        summary=summary,
        trace=_trace(note="decision-policy suggestions built"),
    )


def _build_outcome_observation_report_artifact(*, validated: list[dict[str, Any]], controls: FeedbackControls) -> OutcomeObservationReport:
    observed_entries = [item for item in validated if item["validation_status"] == "accepted" and item["source_type"] == "outcome_observation"]
    positive = sum(1 for item in observed_entries if item.get("observed_outcome") in OUTCOME_POSITIVE)
    negative = sum(1 for item in observed_entries if item.get("observed_outcome") in OUTCOME_NEGATIVE)
    contradiction_count = sum(1 for item in observed_entries if item.get("observed_outcome") in {"false_positive", "false_negative", "drift", "regime_shift"})
    status = "observations_recorded" if observed_entries else ("disabled" if not controls.accept_outcome_observations else "no_observations")
    summary = (
        f"Relaytic accepted {len(observed_entries)} downstream outcome observation(s), including {contradiction_count} that challenge prior offline confidence."
        if observed_entries
        else "Relaytic did not accept any downstream outcome observations."
    )
    return OutcomeObservationReport(
        schema_version=OUTCOME_OBSERVATION_REPORT_SCHEMA_VERSION,
        generated_at=_utc_now(),
        controls=controls,
        status=status,
        accepted_outcome_count=len(observed_entries),
        contradiction_count=contradiction_count,
        positive_outcome_count=positive,
        negative_outcome_count=negative,
        observed_entries=observed_entries,
        summary=summary,
        trace=_trace(note="outcome observations summarized"),
    )


def _build_feedback_effect_report_artifact(
    *,
    validated: list[dict[str, Any]],
    controls: FeedbackControls,
    route_updates: RoutePriorUpdates,
    policy_updates: PolicyUpdateSuggestions,
    decision_updates: DecisionPolicyUpdateSuggestions,
) -> FeedbackEffectReport:
    active = [item for item in validated if item["validation_status"] != "reverted"]
    accepted = [item for item in validated if item["validation_status"] == "accepted"]
    downgraded = [item for item in validated if item["validation_status"] == "downgraded"]
    rejected = [item for item in validated if item["validation_status"] == "rejected"]
    reverted = [item for item in validated if item["validation_status"] == "reverted"]
    changed_artifacts: list[str] = []
    if route_updates.updates:
        changed_artifacts.append(FEEDBACK_FILENAMES["route_prior_updates"])
    if policy_updates.suggestions:
        changed_artifacts.append(FEEDBACK_FILENAMES["policy_update_suggestions"])
    if decision_updates.suggestions:
        changed_artifacts.append(FEEDBACK_FILENAMES["decision_policy_update_suggestions"])
    status = "effects_recorded" if active else "no_feedback"
    summary = (
        "Relaytic translated accepted feedback into explicit, reversible future-default suggestions."
        if changed_artifacts
        else "Relaytic recorded feedback validation results without changing future-default suggestions."
    )
    return FeedbackEffectReport(
        schema_version=FEEDBACK_EFFECT_REPORT_SCHEMA_VERSION,
        generated_at=_utc_now(),
        controls=controls,
        status=status,
        active_feedback_count=len(active),
        accepted_feedback_count=len(accepted),
        downgraded_feedback_count=len(downgraded),
        rejected_feedback_count=len(rejected),
        reverted_feedback_count=len(reverted),
        changed_future_route_recommendations=bool(route_updates.updates),
        changed_policy_suggestions=bool(policy_updates.suggestions),
        changed_decision_policy_recommendations=bool(decision_updates.suggestions),
        primary_recommended_action=decision_updates.primary_recommended_action,
        accepted_feedback_ids=[str(item["feedback_id"]) for item in accepted],
        reverted_feedback_ids=[str(item["feedback_id"]) for item in reverted],
        changed_artifacts=changed_artifacts,
        summary=summary,
        trace=_trace(note="feedback effects summarized"),
    )


def _build_feedback_casebook_artifact(
    *,
    validated: list[dict[str, Any]],
    controls: FeedbackControls,
    route_updates: RoutePriorUpdates,
    policy_updates: PolicyUpdateSuggestions,
    decision_updates: DecisionPolicyUpdateSuggestions,
) -> FeedbackCasebook:
    accepted = [item for item in validated if item["validation_status"] == "accepted"][: controls.max_casebook_entries]
    rejected = [item for item in validated if item["validation_status"] == "rejected"][: controls.max_casebook_entries]
    reverted = [item for item in validated if item["validation_status"] == "reverted"][: controls.max_casebook_entries]
    source_counts: dict[str, int] = {}
    for item in validated:
        source = str(item.get("source_type", "")).strip()
        if not source:
            continue
        source_counts[source] = source_counts.get(source, 0) + 1
    status = "casebook_recorded" if validated else "no_feedback"
    summary = (
        f"Relaytic casebook now tracks {len(accepted)} accepted, {len(rejected)} rejected, and {len(reverted)} reverted feedback cases."
        if validated
        else "Relaytic has no feedback cases recorded yet."
    )
    return FeedbackCasebook(
        schema_version=FEEDBACK_CASEBOOK_SCHEMA_VERSION,
        generated_at=_utc_now(),
        controls=controls,
        status=status,
        accepted_cases=accepted,
        rejected_cases=rejected,
        reverted_cases=reverted,
        source_counts=source_counts,
        effect_counts={
            "route_prior_updates": len(route_updates.updates),
            "policy_suggestions": len(policy_updates.suggestions),
            "decision_policy_suggestions": len(decision_updates.suggestions),
        },
        summary=summary,
        trace=_trace(note="feedback casebook refreshed"),
    )


def _trace(*, note: str) -> FeedbackTrace:
    return FeedbackTrace(
        agent="feedback_assimilation_agent",
        operating_mode="deterministic_review",
        llm_used=False,
        llm_status="not_used",
        deterministic_evidence=["feedback_intake", "artifact_grounding", "trust_scoring"],
        advisory_notes=[note],
    )


def _base_trust_for_source(source_type: str) -> float:
    return {
        "human": 0.72,
        "external_agent": 0.60,
        "runtime_failure": 0.82,
        "benchmark_review": 0.78,
        "outcome_observation": 0.88,
    }.get(source_type, 0.50)


def _source_allowed(*, source_type: str, controls: FeedbackControls) -> bool:
    if source_type == "human":
        return controls.accept_human_feedback
    if source_type == "external_agent":
        return controls.accept_external_agent_feedback
    if source_type == "runtime_failure":
        return controls.accept_runtime_failure_feedback
    if source_type == "benchmark_review":
        return controls.accept_benchmark_review_feedback
    if source_type == "outcome_observation":
        return controls.accept_outcome_observations
    return False


def _decision_policy_suggestion_from_entry(entry: dict[str, Any]) -> str | None:
    observed = entry.get("observed_outcome")
    message = str(entry.get("message", "")).lower()
    explicit = _clean_text(entry.get("suggested_action"))
    if explicit:
        return explicit
    if observed == "false_positive":
        return "raise_review_threshold"
    if observed == "false_negative":
        return "recalibration_candidate"
    if observed in {"drift", "regime_shift"}:
        return "retrain_candidate"
    if "recalibr" in message:
        return "recalibration_candidate"
    if "retrain" in message:
        return "retrain_candidate"
    if "review" in message or "defer" in message:
        return "increase_operator_review"
    if "more data" in message or "collect" in message:
        return "collect_more_data"
    return None


def _normalize_source_type(value: Any) -> str:
    normalized = str(value or "human").strip().lower().replace("-", "_")
    aliases = {
        "user": "human",
        "operator": "human",
        "agent": "external_agent",
        "runtime": "runtime_failure",
        "benchmark": "benchmark_review",
        "outcome": "outcome_observation",
    }
    normalized = aliases.get(normalized, normalized)
    if normalized not in {"human", "external_agent", "runtime_failure", "benchmark_review", "outcome_observation"}:
        return "human"
    return normalized


def _normalize_feedback_type(value: Any, *, source_type: str) -> str:
    normalized = str(value or "").strip().lower().replace("-", "_")
    if normalized in {"route_quality", "decision_policy", "data_quality", "outcome_evidence"}:
        return normalized
    if source_type == "outcome_observation":
        return "outcome_evidence"
    if source_type == "benchmark_review":
        return "route_quality"
    return "decision_policy"


def _normalize_evidence_level(value: Any, *, source_type: str) -> str:
    normalized = str(value or "").strip().lower()
    if normalized in {"weak", "medium", "strong"}:
        return normalized
    if source_type in {"runtime_failure", "benchmark_review", "outcome_observation"}:
        return "strong"
    return "medium"


def _normalize_observed_outcome(value: Any) -> str | None:
    normalized = str(value or "").strip().lower().replace("-", "_")
    if not normalized:
        return None
    return normalized


def _normalize_effect_direction(value: Any, *, message: str) -> str:
    normalized = str(value or "").strip().lower()
    if normalized in {"increase", "decrease"}:
        return normalized
    lowered = str(message or "").lower()
    if any(token in lowered for token in NEGATIVE_ROUTE_PATTERNS):
        return "decrease"
    if any(token in lowered for token in POSITIVE_ROUTE_PATTERNS):
        return "increase"
    return "increase"


def _known_model_family(value: str) -> bool:
    normalized = str(value or "").strip()
    if not normalized:
        return False
    return re.fullmatch(r"[a-z0-9_]+", normalized) is not None


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


def _clean_text(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text or text.lower() == "none":
        return None
    return text


def _coerce_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()
