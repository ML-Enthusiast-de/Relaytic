"""Slice 09 structured semantic-task orchestration and debate pipeline."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .backends import AdvisoryResult, discover_backend
from .models import (
    CONTEXT_ASSEMBLY_REPORT_SCHEMA_VERSION,
    DOC_GROUNDING_REPORT_SCHEMA_VERSION,
    INTELLIGENCE_ESCALATION_SCHEMA_VERSION,
    INTELLIGENCE_MODE_SCHEMA_VERSION,
    LLM_BACKEND_DISCOVERY_SCHEMA_VERSION,
    LLM_HEALTH_CHECK_SCHEMA_VERSION,
    LLM_UPGRADE_SUGGESTIONS_SCHEMA_VERSION,
    SEMANTIC_ACCESS_AUDIT_SCHEMA_VERSION,
    SEMANTIC_COUNTERPOSITION_PACK_SCHEMA_VERSION,
    SEMANTIC_DEBATE_REPORT_SCHEMA_VERSION,
    SEMANTIC_TASK_REQUEST_SCHEMA_VERSION,
    SEMANTIC_TASK_RESULTS_SCHEMA_VERSION,
    SEMANTIC_UNCERTAINTY_REPORT_SCHEMA_VERSION,
    ContextAssemblyReport,
    DocGroundingReport,
    IntelligenceBundle,
    IntelligenceControls,
    IntelligenceEscalationArtifact,
    IntelligenceModeArtifact,
    IntelligenceTrace,
    LLMBackendDiscoveryArtifact,
    LLMHealthCheckArtifact,
    LLMUpgradeSuggestionsArtifact,
    SemanticAccessAudit,
    SemanticCounterpositionPack,
    SemanticDebateReport,
    SemanticTaskRequestArtifact,
    SemanticTaskResultsArtifact,
    SemanticUncertaintyReport,
    build_intelligence_controls_from_policy,
)


@dataclass(frozen=True)
class IntelligenceRunResult:
    bundle: IntelligenceBundle
    review_markdown: str


def run_intelligence_review(
    *,
    run_dir: str | Path,
    policy: dict[str, Any],
    mandate_bundle: dict[str, Any],
    context_bundle: dict[str, Any],
    intake_bundle: dict[str, Any] | None = None,
    investigation_bundle: dict[str, Any] | None = None,
    planning_bundle: dict[str, Any] | None = None,
    evidence_bundle: dict[str, Any] | None = None,
    memory_bundle: dict[str, Any] | None = None,
    completion_bundle: dict[str, Any] | None = None,
    lifecycle_bundle: dict[str, Any] | None = None,
    config_path: str | None = None,
) -> IntelligenceRunResult:
    controls = build_intelligence_controls_from_policy(policy)
    root = Path(run_dir)
    intake_bundle = intake_bundle or {}
    investigation_bundle = investigation_bundle or {}
    planning_bundle = planning_bundle or {}
    evidence_bundle = evidence_bundle or {}
    memory_bundle = memory_bundle or {}
    completion_bundle = completion_bundle or {}
    lifecycle_bundle = lifecycle_bundle or {}

    discovery = discover_backend(controls=controls, config_path=config_path)
    context_blocks, source_artifacts = _assemble_context_blocks(
        controls=controls,
        mandate_bundle=mandate_bundle,
        context_bundle=context_bundle,
        intake_bundle=intake_bundle,
        investigation_bundle=investigation_bundle,
        planning_bundle=planning_bundle,
        evidence_bundle=evidence_bundle,
        memory_bundle=memory_bundle,
        completion_bundle=completion_bundle,
        lifecycle_bundle=lifecycle_bundle,
    )
    doc_sources, grounding_points = _build_doc_grounding(
        root=root,
        mandate_bundle=mandate_bundle,
        context_bundle=context_bundle,
        investigation_bundle=investigation_bundle,
        planning_bundle=planning_bundle,
        evidence_bundle=evidence_bundle,
        memory_bundle=memory_bundle,
        completion_bundle=completion_bundle,
        lifecycle_bundle=lifecycle_bundle,
    )
    task_request = _semantic_task_request(
        context_blocks=context_blocks,
        source_artifacts=source_artifacts,
        grounding_points=grounding_points,
    )
    debate_payload, uncertainty_payload, counterpositions, provider_status, llm_used, llm_notes, latency_ms = _run_semantic_tasks(
        discovery=discovery,
        task_request=task_request,
        context_blocks=context_blocks,
        grounding_points=grounding_points,
        evidence_bundle=evidence_bundle,
        completion_bundle=completion_bundle,
        lifecycle_bundle=lifecycle_bundle,
    )

    trace = IntelligenceTrace(
        agent="semantic_debate_agent",
        operating_mode="structured_semantic_tasks",
        llm_used=llm_used,
        llm_status=provider_status,
        deterministic_evidence=[
            "artifact_context_assembly",
            "doc_grounding_contract",
            "structured_proposer_counter_verifier",
            "rowless_semantic_default",
        ],
        advisory_notes=list(llm_notes),
    )
    generated_at = _utc_now()
    discovery_payload = discovery.to_dict()

    bundle = IntelligenceBundle(
        intelligence_mode=IntelligenceModeArtifact(
            schema_version=INTELLIGENCE_MODE_SCHEMA_VERSION,
            generated_at=generated_at,
            controls=controls,
            configured_mode=controls.intelligence_mode,
            effective_mode=_effective_mode(controls=controls, provider_status=provider_status, llm_used=llm_used),
            backend_status=provider_status,
            llm_used=llm_used,
            rowless_default=controls.semantic_rowless_default,
            summary=_mode_summary(controls=controls, provider_status=provider_status, llm_used=llm_used),
            trace=trace,
        ),
        llm_backend_discovery=LLMBackendDiscoveryArtifact(
            schema_version=LLM_BACKEND_DISCOVERY_SCHEMA_VERSION,
            generated_at=generated_at,
            controls=controls,
            status=discovery.status,
            requested_provider=discovery.requested_provider,
            resolved_provider=discovery.resolved_provider,
            resolved_model=discovery.resolved_model,
            endpoint=discovery.endpoint,
            endpoint_scope=discovery.endpoint_scope,
            profile=discovery.profile,
            notes=list(discovery.notes),
            summary=_backend_summary(discovery_payload),
            trace=trace,
        ),
        llm_health_check=LLMHealthCheckArtifact(
            schema_version=LLM_HEALTH_CHECK_SCHEMA_VERSION,
            generated_at=generated_at,
            controls=controls,
            status=provider_status,
            checked=llm_used or discovery.status == "available",
            provider=discovery.resolved_provider,
            model=discovery.resolved_model,
            endpoint=discovery.endpoint,
            latency_ms=latency_ms,
            notes=list(llm_notes),
            summary=_health_summary(provider_status=provider_status, llm_used=llm_used, latency_ms=latency_ms),
            trace=trace,
        ),
        llm_upgrade_suggestions=LLMUpgradeSuggestionsArtifact(
            schema_version=LLM_UPGRADE_SUGGESTIONS_SCHEMA_VERSION,
            generated_at=generated_at,
            controls=controls,
            status="available" if controls.allow_upgrade_suggestions else "disabled",
            suggestions=_upgrade_suggestions(discovery_payload, controls=controls, provider_status=provider_status),
            summary=_upgrade_summary(discovery_payload, controls=controls, provider_status=provider_status),
            trace=trace,
        ),
        semantic_task_request=SemanticTaskRequestArtifact(
            schema_version=SEMANTIC_TASK_REQUEST_SCHEMA_VERSION,
            generated_at=generated_at,
            controls=controls,
            status="prepared",
            tasks=task_request["tasks"],
            context_digest=task_request["context_digest"],
            summary=task_request["summary"],
            trace=trace,
        ),
        semantic_task_results=SemanticTaskResultsArtifact(
            schema_version=SEMANTIC_TASK_RESULTS_SCHEMA_VERSION,
            generated_at=generated_at,
            controls=controls,
            status="ok",
            provider_status=provider_status,
            tasks=[
                {"task": "proposer", "status": "ok", "result": debate_payload["proposer_position"]},
                {"task": "counterposition", "status": "ok", "result": debate_payload["counterposition"]},
                {"task": "verifier", "status": "ok", "result": debate_payload["verifier_verdict"]},
            ],
            summary="Relaytic completed the proposer, counterposition, and verifier semantic tasks.",
            trace=trace,
        ),
        intelligence_escalation=IntelligenceEscalationArtifact(
            schema_version=INTELLIGENCE_ESCALATION_SCHEMA_VERSION,
            generated_at=generated_at,
            controls=controls,
            status="required" if uncertainty_payload["escalation_recommended"] else "not_required",
            escalation_required=bool(uncertainty_payload["escalation_recommended"]),
            reason_codes=list(uncertainty_payload["reason_codes"]),
            recommended_path=str(uncertainty_payload["recommended_path"]),
            summary=str(uncertainty_payload["escalation_summary"]),
            trace=trace,
        ),
        context_assembly_report=ContextAssemblyReport(
            schema_version=CONTEXT_ASSEMBLY_REPORT_SCHEMA_VERSION,
            generated_at=generated_at,
            controls=controls,
            status="ok",
            rowless_context=controls.semantic_rowless_default,
            context_blocks=context_blocks,
            source_artifacts=source_artifacts,
            summary=f"Relaytic assembled {len(context_blocks)} rowless context block(s) from current-run artifacts.",
            trace=trace,
        ),
        doc_grounding_report=DocGroundingReport(
            schema_version=DOC_GROUNDING_REPORT_SCHEMA_VERSION,
            generated_at=generated_at,
            controls=controls,
            status="ok" if grounding_points else "artifact_only",
            source_documents=doc_sources,
            grounding_points=grounding_points,
            summary=_grounding_summary(doc_sources=doc_sources, grounding_points=grounding_points),
            trace=trace,
        ),
        semantic_access_audit=SemanticAccessAudit(
            schema_version=SEMANTIC_ACCESS_AUDIT_SCHEMA_VERSION,
            generated_at=generated_at,
            controls=controls,
            status="ok",
            row_level_access_requested=False,
            row_level_access_granted=False,
            accessed_artifacts=source_artifacts,
            redactions=["raw_rows", "full_prediction_vectors"] if controls.semantic_rowless_default else [],
            summary="Relaytic kept the semantic layer rowless and artifact-scoped for this run.",
            trace=trace,
        ),
        semantic_debate_report=SemanticDebateReport(
            schema_version=SEMANTIC_DEBATE_REPORT_SCHEMA_VERSION,
            generated_at=generated_at,
            controls=controls,
            status="ok",
            proposer_position=debate_payload["proposer_position"],
            counterposition=debate_payload["counterposition"],
            verifier_verdict=debate_payload["verifier_verdict"],
            recommended_followup_action=str(debate_payload["recommended_followup_action"]),
            confidence=str(debate_payload["confidence"]),
            summary=str(debate_payload["summary"]),
            trace=trace,
        ),
        semantic_counterposition_pack=SemanticCounterpositionPack(
            schema_version=SEMANTIC_COUNTERPOSITION_PACK_SCHEMA_VERSION,
            generated_at=generated_at,
            controls=controls,
            status="ok",
            positions=counterpositions,
            summary=f"Relaytic recorded {len(counterpositions)} counterposition option(s) for the next bounded loop.",
            trace=trace,
        ),
        semantic_uncertainty_report=SemanticUncertaintyReport(
            schema_version=SEMANTIC_UNCERTAINTY_REPORT_SCHEMA_VERSION,
            generated_at=generated_at,
            controls=controls,
            status="ok",
            confidence_band=str(uncertainty_payload["confidence_band"]),
            unresolved_items=list(uncertainty_payload["unresolved_items"]),
            reason_codes=list(uncertainty_payload["reason_codes"]),
            summary=str(uncertainty_payload["summary"]),
            trace=trace,
        ),
    )
    return IntelligenceRunResult(bundle=bundle, review_markdown=render_intelligence_review_markdown(bundle.to_dict()))


def render_intelligence_review_markdown(bundle: IntelligenceBundle | dict[str, Any]) -> str:
    """Render a concise human-readable intelligence review."""

    payload = bundle.to_dict() if isinstance(bundle, IntelligenceBundle) else dict(bundle)
    debate = dict(payload.get("semantic_debate_report", {}))
    uncertainty = dict(payload.get("semantic_uncertainty_report", {}))
    discovery = dict(payload.get("llm_backend_discovery", {}))
    mode = dict(payload.get("intelligence_mode", {}))
    counterpositions = list(dict(payload.get("semantic_counterposition_pack", {})).get("positions", []))
    lines = [
        "# Relaytic Intelligence Review",
        "",
        f"- Configured mode: `{mode.get('configured_mode') or 'unknown'}`",
        f"- Effective mode: `{mode.get('effective_mode') or 'unknown'}`",
        f"- Backend status: `{discovery.get('status') or 'unknown'}`",
        f"- Recommended follow-up: `{debate.get('recommended_followup_action') or 'unknown'}`",
        f"- Debate confidence: `{debate.get('confidence') or 'unknown'}`",
        f"- Uncertainty band: `{uncertainty.get('confidence_band') or 'unknown'}`",
    ]
    proposer = dict(debate.get("proposer_position") or {})
    counter = dict(debate.get("counterposition") or {})
    verifier = dict(debate.get("verifier_verdict") or {})
    if proposer:
        lines.extend(["", "## Proposer", f"- {proposer.get('summary') or 'No proposer summary recorded.'}"])
    if counter:
        lines.extend(["", "## Counterposition", f"- {counter.get('summary') or 'No counterposition summary recorded.'}"])
    if verifier:
        lines.extend(["", "## Verifier", f"- {verifier.get('summary') or 'No verifier summary recorded.'}"])
    if counterpositions:
        lines.extend(["", "## Candidate Follow-Ups"])
        for item in counterpositions[:4]:
            lines.append(f"- `{item.get('action') or 'unknown'}`: {item.get('summary') or 'No summary.'}")
    return "\n".join(lines).rstrip() + "\n"


def _assemble_context_blocks(
    *,
    controls: IntelligenceControls,
    mandate_bundle: dict[str, Any],
    context_bundle: dict[str, Any],
    intake_bundle: dict[str, Any],
    investigation_bundle: dict[str, Any],
    planning_bundle: dict[str, Any],
    evidence_bundle: dict[str, Any],
    memory_bundle: dict[str, Any],
    completion_bundle: dict[str, Any],
    lifecycle_bundle: dict[str, Any],
) -> tuple[list[dict[str, Any]], list[str]]:
    blocks: list[dict[str, Any]] = []
    source_artifacts: list[str] = []
    specs = [
        ("run_brief.json", "Run Brief", _brief_summary(_bundle_item(mandate_bundle, "run_brief"))),
        ("task_brief.json", "Task Brief", _brief_summary(_bundle_item(context_bundle, "task_brief"))),
        ("domain_brief.json", "Domain Brief", _brief_summary(_bundle_item(context_bundle, "domain_brief"))),
        ("intake_record.json", "Operator Intent", _brief_summary(_bundle_item(intake_bundle, "intake_record"))),
        ("dataset_profile.json", "Dataset Profile", _brief_summary(_bundle_item(investigation_bundle, "dataset_profile"))),
        ("domain_memo.json", "Domain Memo", _brief_summary(_bundle_item(investigation_bundle, "domain_memo"))),
        ("focus_profile.json", "Focus Profile", _brief_summary(_bundle_item(investigation_bundle, "focus_profile"))),
        ("plan.json", "Plan", _brief_summary(_bundle_item(planning_bundle, "plan"))),
        ("audit_report.json", "Audit Report", _brief_summary(_bundle_item(evidence_bundle, "audit_report"))),
        ("belief_update.json", "Belief Update", _brief_summary(_bundle_item(evidence_bundle, "belief_update"))),
        ("memory_retrieval.json", "Memory Retrieval", _brief_summary(_bundle_item(memory_bundle, "memory_retrieval"))),
        ("route_prior_context.json", "Route Priors", _brief_summary(_bundle_item(memory_bundle, "route_prior_context"))),
        ("completion_decision.json", "Completion", _brief_summary(_bundle_item(completion_bundle, "completion_decision"))),
        ("promotion_decision.json", "Lifecycle", _brief_summary(_bundle_item(lifecycle_bundle, "promotion_decision"))),
    ]
    for artifact, title, summary in specs:
        if not summary:
            continue
        blocks.append(
            {
                "artifact": artifact,
                "title": title,
                "row_level": False,
                "summary": summary[:600],
            }
        )
        source_artifacts.append(artifact)
    return blocks[: controls.max_context_blocks], source_artifacts[: controls.max_context_blocks]


def _build_doc_grounding(
    *,
    root: Path,
    mandate_bundle: dict[str, Any],
    context_bundle: dict[str, Any],
    investigation_bundle: dict[str, Any],
    planning_bundle: dict[str, Any],
    evidence_bundle: dict[str, Any],
    memory_bundle: dict[str, Any],
    completion_bundle: dict[str, Any],
    lifecycle_bundle: dict[str, Any],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    doc_sources: list[dict[str, Any]] = []
    grounding_points: list[dict[str, Any]] = []
    mapping = [
        ("run_brief.json", _bundle_item(mandate_bundle, "run_brief"), "objective"),
        ("task_brief.json", _bundle_item(context_bundle, "task_brief"), "problem_statement"),
        ("domain_memo.json", _bundle_item(investigation_bundle, "domain_memo"), "domain_summary"),
        ("plan.json", _bundle_item(planning_bundle, "plan"), "summary"),
        ("audit_report.json", _bundle_item(evidence_bundle, "audit_report"), "summary"),
        ("belief_update.json", _bundle_item(evidence_bundle, "belief_update"), "summary"),
        ("memory_retrieval.json", _bundle_item(memory_bundle, "memory_retrieval"), "summary"),
        ("completion_decision.json", _bundle_item(completion_bundle, "completion_decision"), "summary"),
        ("promotion_decision.json", _bundle_item(lifecycle_bundle, "promotion_decision"), "summary"),
    ]
    for filename, payload, key in mapping:
        if not payload:
            continue
        path = root / filename
        doc_sources.append({"artifact": filename, "exists_on_disk": path.exists(), "kind": "run_artifact"})
        text = _clean_text(payload.get(key))
        if text:
            grounding_points.append({"artifact": filename, "field": key, "evidence": text[:240]})
    return doc_sources, grounding_points


def _semantic_task_request(
    *,
    context_blocks: list[dict[str, Any]],
    source_artifacts: list[str],
    grounding_points: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "tasks": [
            {"task": "proposer", "goal": "Argue for the strongest bounded next move from current evidence."},
            {"task": "counterposition", "goal": "Argue for the strongest rival next move or stopping reason."},
            {"task": "verifier", "goal": "Fuse proposer and counterposition into a machine-actionable recommendation."},
        ],
        "context_digest": {
            "context_block_count": len(context_blocks),
            "source_artifact_count": len(source_artifacts),
            "grounding_point_count": len(grounding_points),
        },
        "summary": "Relaytic prepared structured proposer/counterposition/verifier tasks over rowless artifact context.",
    }


def _run_semantic_tasks(
    *,
    discovery: Any,
    task_request: dict[str, Any],
    context_blocks: list[dict[str, Any]],
    grounding_points: list[dict[str, Any]],
    evidence_bundle: dict[str, Any],
    completion_bundle: dict[str, Any],
    lifecycle_bundle: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any], list[dict[str, Any]], str, bool, list[str], float | None]:
    fallback = _deterministic_semantic_debate(
        evidence_bundle=evidence_bundle,
        completion_bundle=completion_bundle,
        lifecycle_bundle=lifecycle_bundle,
        grounding_points=grounding_points,
    )
    if discovery.status != "available" or discovery.advisor is None:
        return (
            fallback["debate"],
            fallback["uncertainty"],
            fallback["counterpositions"],
            discovery.status,
            False,
            list(discovery.notes),
            None,
        )
    prompt = (
        "You are Relaytic's bounded semantic deliberation layer. Use only the provided artifact summaries. "
        "Never assume raw-row access. Return JSON with keys proposer_position, counterposition, verifier_verdict, "
        "recommended_followup_action, confidence, counterpositions, unresolved_items, reason_codes, "
        "escalation_recommended, recommended_path, escalation_summary, summary."
    )
    payload = {
        "task_request": task_request,
        "context_blocks": context_blocks,
        "grounding_points": grounding_points,
        "allowed_followup_actions": [
            "hold_current_route",
            "expand_challenger_portfolio",
            "run_recalibration_pass",
            "run_retrain_pass",
            "collect_more_data",
            "benchmark_needed",
        ],
    }
    result: AdvisoryResult = discovery.advisor.complete_json(
        task_name="semantic_debate",
        system_prompt=prompt,
        payload=payload,
    )
    if result.status != "ok" or not isinstance(result.payload, dict):
        return (
            fallback["debate"],
            fallback["uncertainty"],
            fallback["counterpositions"],
            "fallback_after_backend_error",
            False,
            list(discovery.notes) + list(result.notes),
            result.latency_ms,
        )
    debate = {
        "proposer_position": _dict_or_fallback(result.payload.get("proposer_position"), fallback["debate"]["proposer_position"]),
        "counterposition": _dict_or_fallback(result.payload.get("counterposition"), fallback["debate"]["counterposition"]),
        "verifier_verdict": _dict_or_fallback(result.payload.get("verifier_verdict"), fallback["debate"]["verifier_verdict"]),
        "recommended_followup_action": _clean_text(result.payload.get("recommended_followup_action"))
        or fallback["debate"]["recommended_followup_action"],
        "confidence": _clean_text(result.payload.get("confidence")) or fallback["debate"]["confidence"],
        "summary": _clean_text(result.payload.get("summary")) or fallback["debate"]["summary"],
    }
    unresolved_items = result.payload.get("unresolved_items")
    if not isinstance(unresolved_items, list):
        unresolved_items = fallback["uncertainty"]["unresolved_items"]
    reason_codes = result.payload.get("reason_codes")
    if not isinstance(reason_codes, list):
        reason_codes = fallback["uncertainty"]["reason_codes"]
    counterpositions = result.payload.get("counterpositions")
    if not isinstance(counterpositions, list):
        counterpositions = fallback["counterpositions"]
    uncertainty = {
        "confidence_band": _clean_text(result.payload.get("confidence")) or fallback["uncertainty"]["confidence_band"],
        "unresolved_items": [item for item in unresolved_items if isinstance(item, dict)],
        "reason_codes": [str(item).strip() for item in reason_codes if str(item).strip()],
        "summary": _clean_text(result.payload.get("summary")) or fallback["uncertainty"]["summary"],
        "escalation_recommended": bool(result.payload.get("escalation_recommended", False)),
        "recommended_path": _clean_text(result.payload.get("recommended_path")) or "continue_with_artifact_grounding",
        "escalation_summary": _clean_text(result.payload.get("escalation_summary"))
        or "Relaytic did not require a higher-cost semantic escalation for this round.",
    }
    return debate, uncertainty, counterpositions, "ok", True, list(discovery.notes) + list(result.notes), result.latency_ms


def _deterministic_semantic_debate(
    *,
    evidence_bundle: dict[str, Any],
    completion_bundle: dict[str, Any],
    lifecycle_bundle: dict[str, Any],
    grounding_points: list[dict[str, Any]],
) -> dict[str, Any]:
    audit = _bundle_item(evidence_bundle, "audit_report")
    completion = _bundle_item(completion_bundle, "completion_decision")
    blocking = _bundle_item(completion_bundle, "blocking_analysis")
    lifecycle_retrain = _bundle_item(lifecycle_bundle, "retrain_decision")
    lifecycle_recal = _bundle_item(lifecycle_bundle, "recalibration_decision")
    recommended_action = "expand_challenger_portfolio"
    reason_codes: list[str] = []
    unresolved: list[dict[str, Any]] = []

    completion_action = _clean_text(completion.get("action"))
    lifecycle_retrain_action = _clean_text(lifecycle_retrain.get("action"))
    lifecycle_recal_action = _clean_text(lifecycle_recal.get("action"))
    readiness = _clean_text(audit.get("readiness_level"))
    blocking_layer = _clean_text(completion.get("blocking_layer")) or _clean_text(blocking.get("blocking_layer"))

    if lifecycle_retrain_action == "retrain":
        recommended_action = "run_retrain_pass"
        reason_codes.append("lifecycle_retrain")
    elif lifecycle_recal_action == "recalibrate":
        recommended_action = "run_recalibration_pass"
        reason_codes.append("lifecycle_recalibration")
    elif completion_action in {"benchmark_needed", "collect_more_data"}:
        recommended_action = completion_action
        reason_codes.append(completion_action)
    elif completion_action in {"review_challenger", "continue_experimentation", "memory_support_needed"}:
        recommended_action = "expand_challenger_portfolio"
        reason_codes.append("challenger_breadth_needed")

    if readiness in {"weak", "conditional"}:
        unresolved.append(
            {"item": "evidence_readiness", "severity": "high" if readiness == "weak" else "medium", "detail": f"Audit readiness is `{readiness}`."}
        )
        reason_codes.append(f"readiness_{readiness}")
    if blocking_layer and blocking_layer != "none":
        unresolved.append(
            {"item": "blocking_layer", "severity": "high", "detail": f"Completion still reports blocking layer `{blocking_layer}`."}
        )
        reason_codes.append(f"blocking_{blocking_layer}")

    confidence = "conditional"
    if recommended_action in {"run_retrain_pass", "run_recalibration_pass"}:
        confidence = "strong"
    elif unresolved:
        confidence = "low"

    proposer = {
        "action": recommended_action,
        "summary": (
            "Current run evidence favors an immediate bounded follow-up loop."
            if recommended_action.startswith("run_") or recommended_action == "expand_challenger_portfolio"
            else "Current run evidence favors a conservative operational next step."
        ),
        "reasons": _dedupe_strings(reason_codes or ["semantic_followup"]),
    }
    counter_action = "hold_current_route"
    if recommended_action == "expand_challenger_portfolio":
        counter_action = "run_recalibration_pass"
    elif recommended_action in {"run_recalibration_pass", "run_retrain_pass"}:
        counter_action = "expand_challenger_portfolio"
    counter = {
        "action": counter_action,
        "summary": "A narrower, cheaper alternative still exists and should be kept visible in the debate record.",
        "risks": ["extra_compute_budget", "false_confidence_if_semantic_layer_overstates_evidence"],
    }
    verifier = {
        "action": recommended_action,
        "summary": f"Verifier keeps `{recommended_action}` because it best matches current completion and lifecycle evidence.",
        "grounding_artifacts": [item["artifact"] for item in grounding_points[:5]],
    }
    return {
        "debate": {
            "proposer_position": proposer,
            "counterposition": counter,
            "verifier_verdict": verifier,
            "recommended_followup_action": recommended_action,
            "confidence": confidence,
            "summary": f"Relaytic's semantic debate currently prefers `{recommended_action}`.",
        },
        "uncertainty": {
            "confidence_band": confidence,
            "unresolved_items": unresolved,
            "reason_codes": _dedupe_strings(reason_codes or ["semantic_debate"]),
            "summary": "Relaytic still sees unresolved evidence that should inform the next bounded loop." if unresolved else "Relaytic sees bounded uncertainty but no hidden semantic blocker.",
            "escalation_recommended": bool(unresolved and recommended_action not in {"run_retrain_pass", "run_recalibration_pass"}),
            "recommended_path": "continue_with_artifact_grounding" if unresolved else "no_escalation_required",
            "escalation_summary": "Relaytic should continue with bounded artifact-grounded loops before escalating to richer semantic help." if unresolved else "No semantic escalation is required for the current run.",
        },
        "counterpositions": [
            {"action": recommended_action, "priority": 1, "summary": proposer["summary"]},
            {"action": counter_action, "priority": 2, "summary": counter["summary"]},
        ],
    }


def _bundle_item(bundle: dict[str, Any], key: str) -> dict[str, Any]:
    value = bundle.get(key)
    return dict(value) if isinstance(value, dict) else {}


def _brief_summary(payload: dict[str, Any]) -> str:
    if not payload:
        return ""
    preferred_keys = (
        "summary",
        "problem_statement",
        "objective",
        "domain_summary",
        "notes",
        "status",
        "recommended_action",
        "readiness_level",
        "provisional_recommendation",
    )
    parts: list[str] = []
    for key in preferred_keys:
        text = _clean_text(payload.get(key))
        if text:
            parts.append(f"{key}={text}")
    if parts:
        return "; ".join(parts)
    simple_parts: list[str] = []
    for key, value in payload.items():
        if isinstance(value, (dict, list)):
            continue
        text = _clean_text(value)
        if text:
            simple_parts.append(f"{key}={text}")
        if len(simple_parts) >= 4:
            break
    return "; ".join(simple_parts)


def _clean_text(value: Any) -> str | None:
    text = str(value or "").strip()
    return text or None


def _effective_mode(*, controls: IntelligenceControls, provider_status: str, llm_used: bool) -> str:
    if llm_used:
        return "semantic_local_llm"
    if provider_status in {"deterministic_only", "disabled"}:
        return "deterministic_only"
    return "semantic_fallback_deterministic"


def _mode_summary(*, controls: IntelligenceControls, provider_status: str, llm_used: bool) -> str:
    if llm_used:
        return "Relaytic used a schema-bounded local semantic backend to refine debate outputs without leaving the rowless artifact boundary."
    if provider_status == "blocked_by_policy":
        return "Relaytic stayed deterministic because policy blocked a non-local semantic backend."
    if controls.intelligence_mode.strip().lower() in {"", "none", "off", "disabled", "deterministic"}:
        return "Relaytic stayed deterministic because semantic amplification is disabled for this run."
    return "Relaytic kept the semantic layer deterministic because no healthy local backend was available."


def _backend_summary(discovery: dict[str, Any]) -> str:
    status = str(discovery.get("status", "unknown")).strip() or "unknown"
    provider = _clean_text(discovery.get("resolved_provider")) or _clean_text(discovery.get("requested_provider")) or "none"
    return f"Relaytic backend discovery resolved status `{status}` for provider `{provider}`."


def _health_summary(*, provider_status: str, llm_used: bool, latency_ms: float | None) -> str:
    if llm_used and latency_ms is not None:
        return f"Relaytic completed a live local semantic call in {latency_ms:.1f} ms."
    if provider_status in {"deterministic_only", "disabled"}:
        return "Relaytic did not perform a live semantic backend check because the run stayed deterministic."
    return f"Relaytic recorded backend health status `{provider_status}`."


def _upgrade_suggestions(
    discovery: dict[str, Any],
    *,
    controls: IntelligenceControls,
    provider_status: str,
) -> list[dict[str, Any]]:
    if not controls.allow_upgrade_suggestions:
        return []
    if provider_status in {"deterministic_only", "disabled"}:
        return [
            {
                "kind": "optional_enablement",
                "action": "relaytic setup-local-llm",
                "reason": "Enable a local semantic helper without weakening the deterministic floor.",
            }
        ]
    if provider_status == "blocked_by_policy":
        return [
            {
                "kind": "policy_alignment",
                "action": "use a loopback local backend",
                "reason": "Current semantic endpoint is remote but Relaytic keeps Slice 09 local-first.",
            }
        ]
    if discovery.get("resolved_provider") in {"llama_cpp", "llama.cpp"}:
        return [
            {
                "kind": "local_quality",
                "action": "upgrade the local profile model if semantic verifier quality is weak",
                "reason": "Slice 09 benefits from stronger local schema-following and contradiction handling.",
            }
        ]
    return []


def _upgrade_summary(discovery: dict[str, Any], *, controls: IntelligenceControls, provider_status: str) -> str:
    suggestions = _upgrade_suggestions(discovery, controls=controls, provider_status=provider_status)
    if not suggestions:
        return "Relaytic does not see a necessary semantic-backend upgrade right now."
    return f"Relaytic recorded {len(suggestions)} semantic-backend upgrade suggestion(s)."


def _grounding_summary(*, doc_sources: list[dict[str, Any]], grounding_points: list[dict[str, Any]]) -> str:
    if grounding_points:
        return f"Relaytic grounded the semantic debate on {len(grounding_points)} artifact evidence point(s)."
    if doc_sources:
        return "Relaytic used run artifacts as document-grounding sources but found no strong text evidence fields."
    return "Relaytic ran without extra document grounding beyond current artifact presence."


def _dict_or_fallback(value: Any, fallback: dict[str, Any]) -> dict[str, Any]:
    return dict(value) if isinstance(value, dict) else dict(fallback)


def _dedupe_strings(values: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for value in values:
        stripped = str(value).strip()
        if not stripped:
            continue
        key = stripped.casefold()
        if key in seen:
            continue
        seen.add(key)
        out.append(stripped)
    return out


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()
