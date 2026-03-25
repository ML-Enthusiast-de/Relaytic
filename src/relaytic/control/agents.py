"""Slice 10C behavioral contracts, skeptical steering, and causal memory."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import json
import re
from pathlib import Path
from typing import Any

from .models import (
    CAUSAL_MEMORY_INDEX_SCHEMA_VERSION,
    CONTROL_CHALLENGE_REPORT_SCHEMA_VERSION,
    CONTROL_INJECTION_AUDIT_SCHEMA_VERSION,
    INTERVENTION_CONTRACT_SCHEMA_VERSION,
    INTERVENTION_LEDGER_SCHEMA_VERSION,
    INTERVENTION_MEMORY_LOG_SCHEMA_VERSION,
    INTERVENTION_REQUEST_SCHEMA_VERSION,
    METHOD_MEMORY_INDEX_SCHEMA_VERSION,
    OUTCOME_MEMORY_GRAPH_SCHEMA_VERSION,
    OVERRIDE_DECISION_SCHEMA_VERSION,
    RECOVERY_CHECKPOINT_SCHEMA_VERSION,
    CausalMemoryIndex,
    ControlBundle,
    ControlChallengeReport,
    ControlControls,
    ControlInjectionAudit,
    ControlTrace,
    InterventionContract,
    InterventionLedger,
    InterventionMemoryLog,
    InterventionRequest,
    MethodMemoryIndex,
    OutcomeMemoryGraph,
    OverrideDecision,
    RecoveryCheckpoint,
    build_control_controls_from_policy,
)
from .storage import read_control_bundle


BYPASS_PATTERNS = (
    "ignore safeguards",
    "skip validation",
    "skip benchmark",
    "disable benchmark",
    "disable lifecycle",
    "disable controls",
    "bypass policy",
    "just promote",
    "promote anyway",
    "do not challenge",
    "never challenge",
    "trust me",
    "hide this",
)
UNDER_SPECIFIED_PATTERNS = (
    "make it better",
    "fix it",
    "optimize harder",
    "just improve it",
    "do the best thing",
)


@dataclass(frozen=True)
class ControlRunResult:
    bundle: ControlBundle
    review_markdown: str
    decision: str
    approved_action_kind: str
    approved_stage: str | None


def run_control_review(
    *,
    run_dir: str | Path,
    policy: dict[str, Any],
    message: str,
    action_kind: str,
    requested_stage: str | None,
    stage_before: str,
    run_summary: dict[str, Any] | None = None,
    source_surface: str = "assist",
    source_command: str | None = None,
    actor_type: str = "user",
    actor_name: str | None = None,
) -> ControlRunResult:
    root = Path(run_dir)
    controls = build_control_controls_from_policy(policy)
    run_summary = run_summary or {}
    trace = _trace(note="behavioral control review")
    request_id = f"intervention_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')}"
    normalized_message = _normalize_message(message)
    classification = _classify_request(
        normalized_message=normalized_message,
        action_kind=action_kind,
        requested_stage=requested_stage,
    )
    bypass_patterns = [pattern for pattern in BYPASS_PATTERNS if pattern in normalized_message]
    under_specified = _is_under_specified(
        normalized_message=normalized_message,
        action_kind=action_kind,
        requested_stage=requested_stage,
    )
    challenge_required = _challenge_required(
        controls=controls,
        classification=classification,
        action_kind=action_kind,
        bypass_patterns=bypass_patterns,
    )
    request = InterventionRequest(
        schema_version=INTERVENTION_REQUEST_SCHEMA_VERSION,
        generated_at=_utc_now(),
        controls=controls,
        status="materialized" if controls.enabled else "disabled",
        request_id=request_id,
        actor_type=str(actor_type or "user"),
        actor_name=_clean_text(actor_name),
        source_surface=str(source_surface or "assist"),
        source_command=_clean_text(source_command),
        raw_message=str(message or ""),
        normalized_message=normalized_message,
        requested_action_kind=str(action_kind or "respond"),
        requested_stage=_clean_text(requested_stage),
        request_classification=classification,
        authority_level=_authority_level(actor_type=actor_type, source_surface=source_surface),
        challenge_required=challenge_required,
        bypass_patterns=bypass_patterns,
        under_specified=under_specified,
        summary=_request_summary(classification=classification, action_kind=action_kind, requested_stage=requested_stage),
        trace=trace,
    )
    contract = InterventionContract(
        schema_version=INTERVENTION_CONTRACT_SCHEMA_VERSION,
        generated_at=_utc_now(),
        controls=controls,
        status="active" if controls.enabled else "disabled",
        authority_order=["policy", "mandate", "operator", "external_agent", "tool", "research"],
        low_friction_actions=["respond", "connection_guidance", "rerun_stage"],
        challenge_required_actions=["take_over", "planning_override", "evidence_override", "policy_change"],
        blocked_patterns=list(BYPASS_PATTERNS),
        summary="Relaytic applies skeptical steering: navigation stays easy, truth-bearing requests are challenged, and bypass attempts are rejected.",
        trace=trace,
    )
    causal_memory = _build_causal_memory_index(
        current_run_dir=root,
        controls=controls,
        request=request,
    )
    challenge = _build_challenge_report(
        controls=controls,
        request=request,
        causal_memory=causal_memory,
    )
    decision = _build_override_decision(
        controls=controls,
        request=request,
        challenge=challenge,
        stage_before=stage_before,
    )
    checkpoint = _build_recovery_checkpoint(
        controls=controls,
        request=request,
        decision=decision,
        stage_before=stage_before,
        run_summary=run_summary,
    )
    existing_bundle = read_control_bundle(root)
    ledger = _build_intervention_ledger(
        controls=controls,
        request=request,
        decision=decision,
        challenge=challenge,
        existing_bundle=existing_bundle,
    )
    injection_audit = _build_control_injection_audit(
        controls=controls,
        request=request,
        challenge=challenge,
        decision=decision,
    )
    intervention_memory = _build_intervention_memory_log(
        controls=controls,
        ledger=ledger,
        decision=decision,
    )
    outcome_memory = _build_outcome_memory_graph(
        controls=controls,
        request=request,
        decision=decision,
        run_summary=run_summary,
    )
    method_memory = _build_method_memory_index(
        controls=controls,
        run_summary=run_summary,
    )
    bundle = ControlBundle(
        intervention_request=request,
        intervention_contract=contract,
        control_challenge_report=challenge,
        override_decision=decision,
        intervention_ledger=ledger,
        recovery_checkpoint=checkpoint,
        control_injection_audit=injection_audit,
        causal_memory_index=causal_memory,
        intervention_memory_log=intervention_memory,
        outcome_memory_graph=outcome_memory,
        method_memory_index=method_memory,
    )
    return ControlRunResult(
        bundle=bundle,
        review_markdown=render_control_review_markdown(bundle.to_dict()),
        decision=decision.decision,
        approved_action_kind=decision.approved_action_kind,
        approved_stage=decision.approved_stage,
    )


def render_control_review_markdown(bundle: dict[str, Any]) -> str:
    request = dict(bundle.get("intervention_request", {}))
    challenge = dict(bundle.get("control_challenge_report", {}))
    decision = dict(bundle.get("override_decision", {}))
    causal_memory = dict(bundle.get("causal_memory_index", {}))
    audit = dict(bundle.get("control_injection_audit", {}))
    checkpoint = dict(bundle.get("recovery_checkpoint", {}))
    lines = [
        "# Relaytic Control Review",
        "",
        f"- Request classification: `{request.get('request_classification') or 'unknown'}`",
        f"- Challenge required: `{request.get('challenge_required')}`",
        f"- Decision: `{decision.get('decision') or 'unknown'}`",
        f"- Approved action: `{decision.get('approved_action_kind') or 'none'}`",
        f"- Approved stage: `{decision.get('approved_stage') or 'none'}`",
        f"- Skepticism level: `{challenge.get('skepticism_level') or 'unknown'}`",
        f"- Similar harmful overrides: `{causal_memory.get('similar_harmful_override_count', 0)}`",
        f"- Suspicious patterns: `{audit.get('suspicious_count', 0)}`",
    ]
    if checkpoint.get("checkpoint_id"):
        lines.append(f"- Recovery checkpoint: `{checkpoint.get('checkpoint_id')}`")
    reasons = [str(item) for item in challenge.get("reasons", []) if str(item).strip()]
    if reasons:
        lines.extend(["", "## Challenge Reasons"])
        for item in reasons[:5]:
            lines.append(f"- {item}")
    lines.extend(["", "## Summary", "", str(decision.get("summary") or challenge.get("summary") or "No control summary available.")])
    return "\n".join(lines).rstrip() + "\n"


def _build_causal_memory_index(
    *,
    current_run_dir: Path,
    controls: ControlControls,
    request: InterventionRequest,
) -> CausalMemoryIndex:
    linked_memories: list[dict[str, Any]] = []
    if controls.cross_run_memory_enabled:
        linked_memories.extend(_scan_prior_intervention_memory(current_run_dir=current_run_dir, request=request, controls=controls))
    harmful_count = sum(
        1
        for item in linked_memories
        if str(item.get("outcome_label", "")).strip() in {"harmful_override", "rejected_bypass", "harmful_takeover"}
    )
    skepticism_level = "high" if harmful_count >= 2 else "elevated" if harmful_count == 1 else "standard"
    summary = (
        f"Relaytic found `{harmful_count}` similar harmful prior interventions."
        if linked_memories
        else "Relaytic did not find prior harmful intervention memory for this request."
    )
    return CausalMemoryIndex(
        schema_version=CAUSAL_MEMORY_INDEX_SCHEMA_VERSION,
        generated_at=_utc_now(),
        controls=controls,
        status="derived",
        current_request_id=request.request_id,
        prior_run_count=len({item.get("run_id") for item in linked_memories if item.get("run_id")}),
        similar_harmful_override_count=harmful_count,
        skeptical_bias_level=skepticism_level,
        linked_memories=linked_memories[: controls.max_prior_runs],
        summary=summary,
        trace=_trace(note="causal memory derived from prior intervention logs"),
    )


def _build_challenge_report(
    *,
    controls: ControlControls,
    request: InterventionRequest,
    causal_memory: CausalMemoryIndex,
) -> ControlChallengeReport:
    reasons: list[str] = []
    risk_flags: list[str] = []
    if request.request_classification == "policy_bypass":
        reasons.append("The request attempts to bypass Relaytic safeguards or suppress challenge behavior.")
        risk_flags.append("policy_bypass")
    if request.requested_action_kind == "take_over":
        reasons.append("Takeover changes downstream artifacts, so Relaytic narrows scope to the next safe bounded stage.")
        risk_flags.append("truth_bearing_override")
    if request.under_specified:
        reasons.append("The request is under-specified, so Relaytic continues only with explicit narrowing.")
        risk_flags.append("under_specified")
    if causal_memory.similar_harmful_override_count:
        reasons.append(
            f"Relaytic found `{causal_memory.similar_harmful_override_count}` similar harmful prior interventions and increases skepticism."
        )
        risk_flags.append("causal_memory_skepticism")
    if request.requested_action_kind == "rerun_stage":
        reasons.append("Stage navigation is allowed, but Relaytic checkpoints state before rerunning downstream artifacts.")
    accepted_scope = None
    if request.requested_action_kind == "take_over":
        accepted_scope = "next_safe_stage_only"
    elif request.requested_action_kind == "rerun_stage" and request.requested_stage:
        accepted_scope = f"rerun_from_{request.requested_stage}"
    challenge_level = "high" if request.request_classification == "policy_bypass" else "moderate" if request.challenge_required else "low"
    summary = (
        "Relaytic rejected the intervention because it attempted to bypass control policy."
        if request.request_classification == "policy_bypass"
        else "Relaytic reviewed the intervention skeptically and preserved a bounded accepted scope."
        if request.challenge_required
        else "Relaytic treated the intervention as low-risk navigation or explanation."
    )
    return ControlChallengeReport(
        schema_version=CONTROL_CHALLENGE_REPORT_SCHEMA_VERSION,
        generated_at=_utc_now(),
        controls=controls,
        status="reviewed",
        challenge_level=challenge_level,
        skepticism_level=causal_memory.skeptical_bias_level,
        challenge_required=request.challenge_required,
        similar_harmful_override_count=causal_memory.similar_harmful_override_count,
        reasons=reasons,
        accepted_scope=accepted_scope,
        risk_flags=risk_flags,
        summary=summary,
        trace=_trace(note="challenge report derived from request class and causal memory"),
    )


def _build_override_decision(
    *,
    controls: ControlControls,
    request: InterventionRequest,
    challenge: ControlChallengeReport,
    stage_before: str,
) -> OverrideDecision:
    approved_action_kind = request.requested_action_kind
    approved_stage = request.requested_stage
    decision = "accept"
    execution_blocked = False
    checkpoint_reason = None
    if request.request_classification == "policy_bypass" and controls.reject_policy_bypass:
        decision = "reject"
        approved_action_kind = "respond"
        approved_stage = None
        execution_blocked = True
    elif request.requested_action_kind == "take_over":
        decision = "accept_with_modification"
        checkpoint_reason = "takeover_changes_downstream_artifacts"
    elif request.under_specified and request.requested_action_kind != "respond":
        decision = "accept_with_modification"
        checkpoint_reason = "under_specified_request_narrowed"
    elif request.requested_action_kind == "rerun_stage":
        checkpoint_reason = "stage_rerun_rewrites_downstream_artifacts"
    requires_checkpoint = bool(
        controls.checkpoint_before_override
        and decision in {"accept", "accept_with_modification"}
        and request.requested_action_kind in {"rerun_stage", "take_over"}
    )
    if challenge.similar_harmful_override_count >= 2 and request.requested_action_kind == "take_over":
        decision = "defer"
        execution_blocked = True
        approved_action_kind = "respond"
        approved_stage = None
    return OverrideDecision(
        schema_version=OVERRIDE_DECISION_SCHEMA_VERSION,
        generated_at=_utc_now(),
        controls=controls,
        status="decided",
        decision=decision,
        approved_action_kind=approved_action_kind,
        approved_stage=approved_stage,
        requires_checkpoint=requires_checkpoint,
        challenge_required=request.challenge_required,
        checkpoint_reason=checkpoint_reason,
        skepticism_applied=challenge.similar_harmful_override_count > 0,
        execution_blocked=execution_blocked,
        summary=_decision_summary(decision=decision, action_kind=request.requested_action_kind, requested_stage=request.requested_stage, stage_before=stage_before),
        trace=_trace(note="override decision derived from challenge result"),
    )


def _build_recovery_checkpoint(
    *,
    controls: ControlControls,
    request: InterventionRequest,
    decision: OverrideDecision,
    stage_before: str,
    run_summary: dict[str, Any],
) -> RecoveryCheckpoint:
    checkpoint_id = f"checkpoint_{request.request_id}" if decision.requires_checkpoint else ""
    preserved_artifacts = [
        path
        for path in (
            dict(run_summary.get("artifacts", {})).get("manifest_path"),
            dict(run_summary.get("artifacts", {})).get("plan_path"),
            dict(run_summary.get("artifacts", {})).get("completion_decision_path"),
            dict(run_summary.get("artifacts", {})).get("promotion_decision_path"),
        )
        if str(path or "").strip()
    ]
    if not decision.requires_checkpoint:
        preserved_artifacts = []
    return RecoveryCheckpoint(
        schema_version=RECOVERY_CHECKPOINT_SCHEMA_VERSION,
        generated_at=_utc_now(),
        controls=controls,
        status="checkpointed" if decision.requires_checkpoint else "not_required",
        checkpoint_id=checkpoint_id,
        stage_before=str(stage_before or "unknown"),
        selected_model_family=_clean_text(dict(run_summary.get("decision", {})).get("selected_model_family")),
        next_recommended_action=_clean_text(dict(run_summary.get("next_step", {})).get("recommended_action")),
        preserved_artifacts=preserved_artifacts,
        summary=(
            f"Relaytic checkpointed recoverable run state before `{request.requested_action_kind}` changed downstream artifacts."
            if decision.requires_checkpoint
            else "Relaytic did not need a recovery checkpoint for this low-risk request."
        ),
        trace=_trace(note="recovery checkpoint snapshot"),
    )


def _build_intervention_ledger(
    *,
    controls: ControlControls,
    request: InterventionRequest,
    decision: OverrideDecision,
    challenge: ControlChallengeReport,
    existing_bundle: dict[str, Any],
) -> InterventionLedger:
    prior_entries = list(dict(existing_bundle.get("intervention_ledger", {})).get("entries", []))
    entry = {
        "recorded_at": _utc_now(),
        "request_id": request.request_id,
        "source_surface": request.source_surface,
        "actor_type": request.actor_type,
        "request_classification": request.request_classification,
        "requested_action_kind": request.requested_action_kind,
        "requested_stage": request.requested_stage,
        "decision": decision.decision,
        "approved_action_kind": decision.approved_action_kind,
        "approved_stage": decision.approved_stage,
        "skepticism_level": challenge.skepticism_level,
        "challenge_level": challenge.challenge_level,
        "checkpoint_required": decision.requires_checkpoint,
        "outcome_label": _outcome_label(request=request, decision=decision),
    }
    entries = (prior_entries + [entry])[-controls.max_ledger_entries :]
    return InterventionLedger(
        schema_version=INTERVENTION_LEDGER_SCHEMA_VERSION,
        generated_at=_utc_now(),
        controls=controls,
        status="tracked",
        entry_count=len(entries),
        entries=entries,
        summary=f"Relaytic is tracking `{len(entries)}` intervention decisions for replayable steering history.",
        trace=_trace(note="intervention ledger updated"),
    )


def _build_control_injection_audit(
    *,
    controls: ControlControls,
    request: InterventionRequest,
    challenge: ControlChallengeReport,
    decision: OverrideDecision,
) -> ControlInjectionAudit:
    detected_patterns = list(request.bypass_patterns)
    if "policy_bypass" in challenge.risk_flags and not detected_patterns:
        detected_patterns.append("policy_bypass")
    return ControlInjectionAudit(
        schema_version=CONTROL_INJECTION_AUDIT_SCHEMA_VERSION,
        generated_at=_utc_now(),
        controls=controls,
        status="audited",
        suspicious_count=len(request.bypass_patterns),
        rejected_count=1 if decision.decision == "reject" else 0,
        detected_patterns=detected_patterns,
        summary=f"Relaytic flagged `{len(request.bypass_patterns)}` suspicious control patterns.",
        trace=_trace(note="control injection audit"),
    )


def _build_intervention_memory_log(
    *,
    controls: ControlControls,
    ledger: InterventionLedger,
    decision: OverrideDecision,
) -> InterventionMemoryLog:
    return InterventionMemoryLog(
        schema_version=INTERVENTION_MEMORY_LOG_SCHEMA_VERSION,
        generated_at=_utc_now(),
        controls=controls,
        status="updated",
        entry_count=ledger.entry_count,
        entries=list(ledger.entries),
        summary=(
            "Relaytic preserved intervention history so later runs can become more skeptical when similar overrides proved harmful."
            if decision.skepticism_applied or ledger.entry_count
            else "No intervention memory entries were recorded."
        ),
        trace=_trace(note="intervention memory log updated from ledger"),
    )


def _build_outcome_memory_graph(
    *,
    controls: ControlControls,
    request: InterventionRequest,
    decision: OverrideDecision,
    run_summary: dict[str, Any],
) -> OutcomeMemoryGraph:
    next_action = _clean_text(dict(run_summary.get("next_step", {})).get("recommended_action"))
    nodes = [
        {"id": request.request_id, "kind": "intervention", "label": request.request_classification},
        {"id": "decision", "kind": "decision", "label": decision.decision},
    ]
    edges = [{"source": request.request_id, "target": "decision", "relation": "led_to"}]
    if next_action:
        nodes.append({"id": "next_action", "kind": "recommendation", "label": next_action})
        edges.append({"source": "decision", "target": "next_action", "relation": "influenced"})
    return OutcomeMemoryGraph(
        schema_version=OUTCOME_MEMORY_GRAPH_SCHEMA_VERSION,
        generated_at=_utc_now(),
        controls=controls,
        status="derived",
        outcome_link_count=len(edges),
        nodes=nodes,
        edges=edges,
        summary="Relaytic linked intervention requests to decisions and the current recommended action.",
        trace=_trace(note="outcome memory graph derived from current decision"),
    )


def _build_method_memory_index(*, controls: ControlControls, run_summary: dict[str, Any]) -> MethodMemoryIndex:
    methods: list[dict[str, Any]] = []
    research = dict(run_summary.get("research", {}))
    benchmark = dict(run_summary.get("benchmark", {}))
    selected_family = _clean_text(dict(run_summary.get("decision", {})).get("selected_model_family"))
    if selected_family:
        methods.append({"method_id": selected_family, "outcome": "current_route", "source": "run_summary"})
    for item in (
        _clean_text(research.get("recommended_followup_action")),
        _clean_text(benchmark.get("winning_family")),
    ):
        if item:
            methods.append({"method_id": item, "outcome": "suggested", "source": "derived"})
    positive_count = sum(1 for item in methods if str(item.get("outcome")) in {"current_route", "suggested"})
    return MethodMemoryIndex(
        schema_version=METHOD_MEMORY_INDEX_SCHEMA_VERSION,
        generated_at=_utc_now(),
        controls=controls,
        status="derived",
        positive_method_count=positive_count,
        negative_method_count=0,
        methods=methods[:12],
        summary="Relaytic preserved current route and method suggestions so later intervention reviews can cite method context.",
        trace=_trace(note="method memory index derived from current run summary"),
    )


def _scan_prior_intervention_memory(
    *,
    current_run_dir: Path,
    request: InterventionRequest,
    controls: ControlControls,
) -> list[dict[str, Any]]:
    parent = current_run_dir.parent
    if not parent.exists():
        return []
    linked: list[dict[str, Any]] = []
    for candidate in sorted(parent.iterdir()):
        if candidate == current_run_dir or not candidate.is_dir():
            continue
        path = candidate / "intervention_memory_log.json"
        if not path.exists():
            continue
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        for entry in list(payload.get("entries", [])):
            if not isinstance(entry, dict) or not _memory_entry_matches(request=request, entry=entry):
                continue
            linked.append(
                {
                    "run_id": candidate.name,
                    "request_id": _clean_text(entry.get("request_id")),
                    "requested_action_kind": _clean_text(entry.get("requested_action_kind")),
                    "requested_stage": _clean_text(entry.get("requested_stage")),
                    "decision": _clean_text(entry.get("decision")),
                    "outcome_label": _clean_text(entry.get("outcome_label")),
                    "skepticism_level": _clean_text(entry.get("skepticism_level")),
                }
            )
            if len(linked) >= controls.max_prior_runs:
                return linked
    return linked


def _memory_entry_matches(*, request: InterventionRequest, entry: dict[str, Any]) -> bool:
    entry_action = _clean_text(entry.get("requested_action_kind"))
    entry_stage = _clean_text(entry.get("requested_stage"))
    if entry_action and entry_action == request.requested_action_kind:
        return True
    if entry_stage and request.requested_stage and entry_stage == request.requested_stage:
        return True
    return request.request_classification == _clean_text(entry.get("request_classification"))


def _classify_request(*, normalized_message: str, action_kind: str, requested_stage: str | None) -> str:
    if action_kind == "respond":
        return "policy_bypass" if any(pattern in normalized_message for pattern in BYPASS_PATTERNS) else "explain"
    if action_kind == "rerun_stage":
        return "navigation"
    if any(pattern in normalized_message for pattern in BYPASS_PATTERNS):
        return "policy_bypass"
    if action_kind == "take_over":
        return "proposal" if _is_under_specified(normalized_message=normalized_message, action_kind=action_kind, requested_stage=requested_stage) else "override"
    return "proposal"


def _challenge_required(
    *,
    controls: ControlControls,
    classification: str,
    action_kind: str,
    bypass_patterns: list[str],
) -> bool:
    if not controls.enabled:
        return False
    if classification == "policy_bypass" or bypass_patterns:
        return True
    if action_kind == "rerun_stage":
        return not controls.allow_navigation_without_challenge
    if action_kind == "respond":
        return False
    return controls.challenge_material_requests


def _is_under_specified(*, normalized_message: str, action_kind: str, requested_stage: str | None) -> bool:
    if action_kind == "take_over" and requested_stage is None:
        return True
    return any(pattern in normalized_message for pattern in UNDER_SPECIFIED_PATTERNS)


def _authority_level(*, actor_type: str, source_surface: str) -> str:
    actor = str(actor_type or "user").strip().lower()
    surface = str(source_surface or "assist").strip().lower()
    if actor == "operator":
        return "operator"
    if actor == "agent" or surface == "mcp":
        return "external_agent"
    return "user"


def _request_summary(*, classification: str, action_kind: str, requested_stage: str | None) -> str:
    if action_kind == "rerun_stage" and requested_stage:
        return f"Relaytic normalized the request as navigation to rerun from `{requested_stage}`."
    if action_kind == "take_over":
        return "Relaytic normalized the request as a takeover proposal that can change downstream artifacts."
    if classification == "policy_bypass":
        return "Relaytic normalized the request as a safeguard-bypass attempt."
    return "Relaytic normalized the request as an explanation or low-risk interaction."


def _decision_summary(*, decision: str, action_kind: str, requested_stage: str | None, stage_before: str) -> str:
    if decision == "reject":
        return "Relaytic rejected the request because it tried to bypass safeguards or suppress challenge behavior."
    if decision == "defer":
        return "Relaytic deferred the request because similar prior overrides proved harmful and the current request needs stronger review."
    if decision == "accept_with_modification" and action_kind == "take_over":
        return f"Relaytic accepted the takeover with modification and will continue only from the next safe bounded stage after `{stage_before}`."
    if decision == "accept_with_modification":
        return "Relaytic accepted the request with a narrower scope because the original instruction was under-specified."
    if action_kind == "rerun_stage" and requested_stage:
        return f"Relaytic accepted the navigation request and checkpointed state before rerunning from `{requested_stage}`."
    return "Relaytic accepted the request under the current control contract."


def _outcome_label(*, request: InterventionRequest, decision: OverrideDecision) -> str:
    if request.request_classification == "policy_bypass" or decision.decision == "reject":
        return "rejected_bypass"
    if decision.decision == "defer":
        return "harmful_override"
    if request.requested_action_kind == "take_over" and decision.decision == "accept_with_modification":
        return "harmful_takeover" if request.under_specified else "bounded_takeover"
    return "accepted_navigation" if request.requested_action_kind == "rerun_stage" else "accepted_override"


def _normalize_message(message: str) -> str:
    return re.sub(r"\s+", " ", str(message or "").strip().lower())


def _clean_text(value: Any) -> str | None:
    text = str(value or "").strip()
    return text or None


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _trace(*, note: str) -> ControlTrace:
    return ControlTrace(
        agent="control_governor",
        operating_mode="deterministic_behavioral_contracts",
        llm_used=False,
        llm_status="not_requested",
        deterministic_evidence=[
            "assist_turn_plan",
            "authority_order",
            "control_policy",
            "prior_intervention_memory",
        ],
        advisory_notes=[note],
    )
