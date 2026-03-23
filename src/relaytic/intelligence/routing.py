"""Routing plans and proof helpers for Slice 09F intelligence."""

from __future__ import annotations

from typing import Any

from .modes import (
    MODE_AMPLIFY,
    MODE_ASSIST,
    MODE_LOCAL_MIN,
    MODE_MAX_REASONING,
    MODE_NONE,
    canonicalize_mode,
    clamp_mode,
    highest_allowed_mode,
    mode_rank,
)
from .models import (
    LLM_ROUTING_PLAN_SCHEMA_VERSION,
    SEMANTIC_PROOF_REPORT_SCHEMA_VERSION,
    VERIFIER_REPORT_SCHEMA_VERSION,
    IntelligenceControls,
    IntelligenceTrace,
    LLMRoutingPlanArtifact,
    SemanticProofReport,
    VerifierReportArtifact,
)


def build_llm_routing_plan_artifact(
    *,
    controls: IntelligenceControls,
    discovery: Any,
    local_profile: Any,
    context_blocks: list[dict[str, Any]],
    grounding_points: list[dict[str, Any]],
    generated_at: str,
    trace: IntelligenceTrace,
) -> LLMRoutingPlanArtifact:
    """Build the explicit runtime routing plan for semantic work."""

    requested_mode = canonicalize_mode(controls.intelligence_mode)
    pressure = _semantic_pressure(context_blocks=context_blocks, grounding_points=grounding_points)
    recommended_mode = _recommended_mode(
        requested_mode=requested_mode,
        pressure=pressure,
        local_profile=local_profile,
        controls=controls,
    )
    maximum_mode = highest_allowed_mode(
        allow_frontier_llm=controls.allow_frontier_llm,
        allow_max_reasoning=controls.allow_max_reasoning,
    )
    planned_mode = clamp_mode(
        requested_mode if not controls.allow_mode_routing else recommended_mode,
        maximum_mode=maximum_mode,
    )
    if discovery.status != "available":
        routed_mode = MODE_NONE
        routing_status = "deterministic_only"
    else:
        routed_mode = planned_mode if planned_mode != MODE_NONE else requested_mode
        routing_status = "routed"
    reason_codes = _reason_codes(
        requested_mode=requested_mode,
        planned_mode=planned_mode,
        routed_mode=routed_mode,
        discovery_status=discovery.status,
        pressure=pressure,
        local_profile=local_profile,
    )
    return LLMRoutingPlanArtifact(
        schema_version=LLM_ROUTING_PLAN_SCHEMA_VERSION,
        generated_at=generated_at,
        controls=controls,
        status=routing_status,
        requested_mode=requested_mode,
        recommended_mode=recommended_mode,
        selected_mode=routed_mode,
        semantic_pressure=pressure,
        reason_codes=reason_codes,
        selected_backend={
            "provider": discovery.resolved_provider,
            "model": discovery.resolved_model,
            "endpoint_scope": discovery.endpoint_scope,
            "status": discovery.status,
        },
        selected_profile={
            "profile_name": local_profile.profile_name,
            "model": local_profile.model,
            "recommended_mode": local_profile.recommended_mode,
        },
        capability_matrix=_capability_matrix(discovery=discovery, local_profile=local_profile),
        phase_assignments=_phase_assignments(selected_mode=routed_mode, requested_mode=requested_mode),
        summary=_routing_summary(
            routed_mode=routed_mode,
            discovery_status=discovery.status,
            local_profile=local_profile,
            pressure=pressure,
        ),
        trace=trace,
    )


def build_verifier_report_artifact(
    *,
    controls: IntelligenceControls,
    debate_payload: dict[str, Any],
    baseline_debate: dict[str, Any],
    llm_used: bool,
    provider_status: str,
    generated_at: str,
    trace: IntelligenceTrace,
) -> VerifierReportArtifact:
    """Persist verifier output as its own first-class artifact."""

    verifier = dict(debate_payload.get("verifier_verdict") or {})
    baseline_verifier = dict(baseline_debate.get("verifier_verdict") or {})
    selected_action = str(verifier.get("action") or debate_payload.get("recommended_followup_action") or "unknown")
    baseline_action = str(
        baseline_verifier.get("action") or baseline_debate.get("recommended_followup_action") or "unknown"
    )
    return VerifierReportArtifact(
        schema_version=VERIFIER_REPORT_SCHEMA_VERSION,
        generated_at=generated_at,
        controls=controls,
        status="ok",
        llm_used=llm_used,
        provider_status=provider_status,
        selected_action=selected_action,
        baseline_action=baseline_action,
        changed_from_deterministic_baseline=selected_action != baseline_action,
        verifier_payload=verifier,
        summary=_verifier_summary(
            selected_action=selected_action,
            baseline_action=baseline_action,
            llm_used=llm_used,
        ),
        trace=trace,
    )


def build_semantic_proof_report_artifact(
    *,
    controls: IntelligenceControls,
    debate_payload: dict[str, Any],
    baseline_debate: dict[str, Any],
    llm_used: bool,
    generated_at: str,
    trace: IntelligenceTrace,
) -> SemanticProofReport:
    """Record whether semantic amplification changed bounded semantic outputs visibly."""

    if not controls.enable_semantic_proof:
        return SemanticProofReport(
            schema_version=SEMANTIC_PROOF_REPORT_SCHEMA_VERSION,
            generated_at=generated_at,
            controls=controls,
            status="disabled",
            llm_used=llm_used,
            deterministic_baseline_action=_clean_text(baseline_debate.get("recommended_followup_action")),
            routed_action=_clean_text(debate_payload.get("recommended_followup_action")),
            changed_fields=[],
            measurable_gain_detected=False,
            benchmark_dimensions=[],
            summary="Semantic proof reporting is disabled by policy for this run.",
            trace=trace,
        )

    dimensions: list[dict[str, Any]] = []
    changed_fields: list[str] = []

    if _clean_text(debate_payload.get("recommended_followup_action")) != _clean_text(
        baseline_debate.get("recommended_followup_action")
    ):
        changed_fields.append("recommended_followup_action")
        dimensions.append(
            {
                "dimension": "challenger_usefulness",
                "status": "changed",
                "detail": "Semantic routing changed the preferred bounded follow-up action.",
            }
        )

    if dict(debate_payload.get("domain_interpretation") or {}) != dict(baseline_debate.get("domain_interpretation") or {}):
        changed_fields.append("domain_interpretation")
        dimensions.append(
            {
                "dimension": "domain_context_extraction",
                "status": "changed",
                "detail": "Semantic routing changed the structured domain interpretation packet.",
            }
        )

    if dict(debate_payload.get("counterposition") or {}) != dict(baseline_debate.get("counterposition") or {}):
        changed_fields.append("counterposition")
        dimensions.append(
            {
                "dimension": "counterposition_quality",
                "status": "changed",
                "detail": "Semantic routing changed the rival bounded follow-up path.",
            }
        )

    if _clean_text(debate_payload.get("confidence")) != _clean_text(baseline_debate.get("confidence")):
        changed_fields.append("confidence")
        dimensions.append(
            {
                "dimension": "lifecycle_ambiguity_resolution",
                "status": "changed",
                "detail": "Semantic routing changed the confidence assessment for the current bounded decision.",
            }
        )

    meaningful_gain = bool(llm_used and changed_fields)
    return SemanticProofReport(
        schema_version=SEMANTIC_PROOF_REPORT_SCHEMA_VERSION,
        generated_at=generated_at,
        controls=controls,
        status="measured" if llm_used else "deterministic_only",
        llm_used=llm_used,
        deterministic_baseline_action=_clean_text(baseline_debate.get("recommended_followup_action")),
        routed_action=_clean_text(debate_payload.get("recommended_followup_action")),
        changed_fields=changed_fields,
        measurable_gain_detected=meaningful_gain,
        benchmark_dimensions=dimensions,
        summary=_proof_summary(llm_used=llm_used, changed_fields=changed_fields),
        trace=trace,
    )


def _semantic_pressure(
    *,
    context_blocks: list[dict[str, Any]],
    grounding_points: list[dict[str, Any]],
) -> str:
    score = 0
    if len(context_blocks) >= 8:
        score += 1
    if len(context_blocks) >= 12:
        score += 1
    if len(grounding_points) >= 4:
        score += 1
    if len(grounding_points) >= 8:
        score += 1
    if score >= 3:
        return "high"
    if score >= 1:
        return "moderate"
    return "light"


def _recommended_mode(
    *,
    requested_mode: str,
    pressure: str,
    local_profile: Any,
    controls: IntelligenceControls,
) -> str:
    if requested_mode == MODE_NONE and not controls.minimum_local_llm_enabled:
        return MODE_NONE
    if requested_mode == MODE_NONE and controls.minimum_local_llm_enabled:
        return MODE_LOCAL_MIN
    if not controls.hardware_aware_routing:
        return requested_mode if requested_mode != MODE_NONE else (MODE_LOCAL_MIN if controls.minimum_local_llm_enabled else MODE_NONE)
    if pressure == "high":
        return MODE_MAX_REASONING if controls.allow_max_reasoning else MODE_AMPLIFY
    if pressure == "moderate":
        return MODE_AMPLIFY if mode_rank(local_profile.recommended_mode) >= mode_rank(MODE_AMPLIFY) else MODE_ASSIST
    return local_profile.recommended_mode or MODE_ASSIST


def _reason_codes(
    *,
    requested_mode: str,
    planned_mode: str,
    routed_mode: str,
    discovery_status: str,
    pressure: str,
    local_profile: Any,
) -> list[str]:
    codes = [f"requested_mode:{requested_mode}", f"semantic_pressure:{pressure}"]
    if local_profile.profile_name:
        codes.append(f"profile:{local_profile.profile_name}")
    if planned_mode != requested_mode:
        codes.append("mode_adjusted_by_routing")
    if discovery_status != "available":
        codes.append(f"backend:{discovery_status}")
    else:
        codes.append(f"selected_mode:{routed_mode}")
    return codes


def _capability_matrix(*, discovery: Any, local_profile: Any) -> dict[str, Any]:
    provider = str(discovery.resolved_provider or discovery.requested_provider or "none").lower()
    supports_thinking_toggle = provider in {"openai", "openai_compatible"}
    return {
        "json_mode": True,
        "tool_calls": False,
        "thinking_toggle": supports_thinking_toggle,
        "vision": False,
        "context_window": local_profile.max_context,
        "endpoint_scope": discovery.endpoint_scope,
        "provider": provider or None,
    }


def _phase_assignments(*, selected_mode: str, requested_mode: str) -> list[dict[str, str]]:
    active_mode = selected_mode if selected_mode != MODE_NONE else requested_mode
    if active_mode == MODE_NONE:
        active_mode = MODE_NONE
    lifecycle_mode = MODE_AMPLIFY if mode_rank(active_mode) >= mode_rank(MODE_AMPLIFY) else active_mode
    if mode_rank(active_mode) >= mode_rank(MODE_MAX_REASONING):
        lifecycle_mode = MODE_MAX_REASONING
    return [
        {"phase": "assist_explanation", "mode": MODE_LOCAL_MIN if active_mode != MODE_NONE else MODE_NONE},
        {"phase": "target_and_note_interpretation", "mode": active_mode if active_mode != MODE_NONE else MODE_NONE},
        {"phase": "challenger_design", "mode": MODE_AMPLIFY if mode_rank(active_mode) >= mode_rank(MODE_AMPLIFY) else active_mode},
        {"phase": "lifecycle_ambiguity_resolution", "mode": lifecycle_mode},
    ]


def _routing_summary(*, routed_mode: str, discovery_status: str, local_profile: Any, pressure: str) -> str:
    if discovery_status != "available":
        return f"Relaytic stayed on the deterministic floor because semantic routing resolved backend status `{discovery_status}`."
    return (
        f"Relaytic routed semantic work through mode `{routed_mode}` with profile "
        f"`{local_profile.profile_name or 'unknown'}` under `{pressure}` semantic pressure."
    )


def _verifier_summary(*, selected_action: str, baseline_action: str, llm_used: bool) -> str:
    if not llm_used:
        return f"Relaytic kept verifier action `{selected_action}` on the deterministic floor."
    if selected_action == baseline_action:
        return f"Relaytic used semantic amplification, but the verifier still held the deterministic action `{selected_action}`."
    return (
        f"Relaytic's verifier changed the bounded action from `{baseline_action}` "
        f"to `{selected_action}` under routed semantic assistance."
    )


def _proof_summary(*, llm_used: bool, changed_fields: list[str]) -> str:
    if not llm_used:
        return "Relaytic recorded no semantic uplift because the run stayed on the deterministic floor."
    if not changed_fields:
        return "Relaytic used semantic routing, but the bounded outputs matched the deterministic semantic baseline."
    return f"Relaytic recorded measurable semantic output changes in {len(changed_fields)} field(s)."


def _clean_text(value: Any) -> str | None:
    text = str(value).strip() if value is not None else ""
    return text or None
