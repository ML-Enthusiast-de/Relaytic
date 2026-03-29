"""Slice 12B tracing, deterministic debate packets, and replay helpers."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from relaytic.control import read_control_bundle
from relaytic.runs import materialize_run_summary, read_run_summary
from relaytic.runtime.storage import read_event_stream

from .models import (
    ADJUDICATION_SCORECARD_SCHEMA_VERSION,
    BRANCH_TRACE_GRAPH_SCHEMA_VERSION,
    CLAIM_PACKET_SCHEMA_VERSION,
    DECISION_REPLAY_REPORT_SCHEMA_VERSION,
    SPECIALIST_TRACE_INDEX_SCHEMA_VERSION,
    TRACE_MODEL_SCHEMA_VERSION,
    TRACE_SPAN_SCHEMA_VERSION,
    AdjudicationEntry,
    AdjudicationScorecard,
    BranchTraceGraphArtifact,
    ClaimPacket,
    DecisionReplayReportArtifact,
    SpecialistTraceIndexArtifact,
    TraceBundle,
    TraceControls,
    TraceModelArtifact,
    TraceSpan,
)
from .storage import append_trace_span, read_trace_bundle


@dataclass(frozen=True)
class TraceRunResult:
    bundle: TraceBundle
    review_markdown: str
    replay_markdown: str


def build_trace_controls_from_policy(policy: dict[str, Any] | None) -> TraceControls:
    return TraceControls.from_policy(policy)


def record_runtime_trace_event(
    *,
    run_dir: str | Path,
    policy: dict[str, Any] | None,
    event: dict[str, Any],
) -> None:
    controls = build_trace_controls_from_policy(policy)
    if not controls.enabled or not controls.direct_runtime_span_writes:
        return
    append_trace_span(run_dir, span=_span_from_runtime_event(event))


def run_trace_review(
    *,
    run_dir: str | Path,
    policy: dict[str, Any] | None = None,
) -> TraceRunResult:
    root = Path(run_dir)
    root.mkdir(parents=True, exist_ok=True)
    controls = build_trace_controls_from_policy(policy)
    summary_payload = read_run_summary(root) or materialize_run_summary(run_dir=root)["summary"]
    runtime_events = read_event_stream(root)
    existing = read_trace_bundle(root)
    spans = _merge_spans(
        existing_spans=[dict(item) for item in existing.get("trace_span_log", []) if isinstance(item, dict)],
        runtime_events=runtime_events,
        controls=controls,
    )
    control_bundle = read_control_bundle(root)
    tool_trace_log = _build_tool_trace_log(
        existing=[dict(item) for item in existing.get("tool_trace_log", []) if isinstance(item, dict)],
        runtime_events=runtime_events,
    )
    intervention_trace_log = _build_intervention_trace_log(
        existing=[dict(item) for item in existing.get("intervention_trace_log", []) if isinstance(item, dict)],
        control_bundle=control_bundle,
    )
    claim_packets = _build_claim_packets(summary_payload=summary_payload, spans=spans)
    adjudication = adjudicate_claim_packets(claim_packets=claim_packets, summary_payload=summary_payload, controls=controls)
    specialist_index = _build_specialist_trace_index(spans=spans, controls=controls)
    branch_graph = _build_branch_trace_graph(summary_payload=summary_payload, controls=controls)
    replay_report = _build_decision_replay_report(spans=spans, claim_packets=claim_packets, adjudication=adjudication, controls=controls)
    trace_model = TraceModelArtifact(
        schema_version=TRACE_MODEL_SCHEMA_VERSION,
        generated_at=_utc_now(),
        controls=controls,
        status="ok" if spans else "empty",
        span_count=len(spans),
        claim_count=len(claim_packets),
        branch_count=len(branch_graph.nodes),
        tool_trace_count=len(tool_trace_log),
        intervention_trace_count=len(intervention_trace_log),
        conformance_surfaces=list(controls.conformance_surfaces),
        direct_runtime_emission_detected=bool(existing.get("trace_span_log")),
        summary=f"Relaytic recorded {len(spans)} trace spans, {len(claim_packets)} claim packets, and {len(branch_graph.nodes)} branch nodes.",
    )
    bundle = TraceBundle(
        trace_model=trace_model,
        specialist_trace_index=specialist_index,
        branch_trace_graph=branch_graph,
        adjudication_scorecard=adjudication,
        decision_replay_report=replay_report,
        trace_span_log=[_dict_to_span(item) for item in spans],
        tool_trace_log=tool_trace_log,
        intervention_trace_log=intervention_trace_log,
        claim_packet_log=claim_packets,
    )
    payload = bundle.to_dict()
    return TraceRunResult(
        bundle=bundle,
        review_markdown=render_trace_review_markdown(payload),
        replay_markdown=render_trace_replay_markdown(payload),
    )


def adjudicate_claim_packets(
    *,
    claim_packets: list[ClaimPacket],
    summary_payload: dict[str, Any],
    controls: TraceControls | None = None,
) -> AdjudicationScorecard:
    controls = controls or TraceControls()
    if not claim_packets:
        return AdjudicationScorecard(
            schema_version=ADJUDICATION_SCORECARD_SCHEMA_VERSION,
            generated_at=_utc_now(),
            controls=controls,
            status="empty",
            decision_id=_identifier("decision"),
            decision_scope="next_action",
            winning_claim_id=None,
            winning_action=None,
            scorecard=[],
            why_won=["No competing claims were available."],
            why_not_others=[],
            summary="Relaytic did not have enough structured claims to adjudicate.",
        )

    decision_lab = dict(summary_payload.get("decision_lab", {}))
    benchmark = dict(summary_payload.get("benchmark", {}))
    control = dict(summary_payload.get("control", {}))
    intelligence = dict(summary_payload.get("intelligence", {}))
    target_action = _clean_text(decision_lab.get("selected_next_action")) or _clean_text(dict(summary_payload.get("next_step", {})).get("recommended_action"))
    beat_target_unmet = _clean_text(benchmark.get("beat_target_state")) == "unmet"
    suspicious_count = int(control.get("suspicious_count", 0) or 0)
    harmful_override_count = int(control.get("similar_harmful_override_count", 0) or 0)
    review_required = bool(decision_lab.get("review_required"))
    uncertainty_band = _clean_text(intelligence.get("uncertainty_band"))

    entries: list[AdjudicationEntry] = []
    for claim in claim_packets:
        aggressive = _is_aggressive_action(claim.proposed_action)
        search_heavy = _is_search_heavy_action(claim.proposed_action)
        cautious = _is_cautious_action(claim.proposed_action)
        empirical_support_score = 0.52 + (0.12 if claim.empirical_support else 0.0) + (0.08 if claim.evidence_refs else 0.0)
        if claim.specialist == "completion_governor":
            empirical_support_score += 0.08
        elif claim.specialist == "decision_lab":
            empirical_support_score += 0.04
        policy_fit_score = 0.92
        if aggressive and suspicious_count > 0:
            policy_fit_score = 0.18
        elif aggressive and harmful_override_count > 0:
            policy_fit_score = 0.34
        benchmark_fit_score = 0.55
        if beat_target_unmet:
            benchmark_fit_score = 0.86 if search_heavy or claim.proposed_action in {"run_retrain_pass", "expand_challenger_portfolio"} else 0.44
        elif claim.proposed_action in {"stop_for_now", "operator_review"}:
            benchmark_fit_score = 0.82
        memory_consistency_score = 0.62
        if harmful_override_count > 0:
            memory_consistency_score = 0.84 if cautious else 0.28
        decision_value_score = 0.56
        if target_action:
            decision_value_score = 0.94 if claim.proposed_action == target_action else 0.41
        uncertainty_penalty = 0.18 if review_required and aggressive else 0.11 if uncertainty_band in {"high", "wide"} else 0.04
        risk_penalty = 0.27 if suspicious_count > 0 and aggressive else 0.14 if aggressive else 0.05
        cost_penalty = _cost_penalty(claim.proposed_action)
        reversibility_bonus = _reversibility_bonus(claim.proposed_action)
        final_score = max(
            0.0,
            min(
                1.0,
                (
                    empirical_support_score
                    + policy_fit_score
                    + benchmark_fit_score
                    + memory_consistency_score
                    + decision_value_score
                )
                / 5.0
                + reversibility_bonus
                - uncertainty_penalty
                - risk_penalty
                - cost_penalty,
            ),
        )
        reasons = []
        if claim.proposed_action == target_action and target_action:
            reasons.append("matches current decision-lab next action")
        if beat_target_unmet and (search_heavy or claim.proposed_action == "expand_challenger_portfolio"):
            reasons.append("fits current beat-target pressure")
        if harmful_override_count > 0 and cautious:
            reasons.append("aligns with prior harmful-override memory")
        if aggressive and suspicious_count > 0:
            reasons.append("penalized by suspicious steering history")
        entries.append(
            AdjudicationEntry(
                claim_id=claim.claim_id,
                specialist=claim.specialist,
                proposed_action=claim.proposed_action,
                confidence=claim.confidence,
                empirical_support_score=round(empirical_support_score, 3),
                policy_fit_score=round(policy_fit_score, 3),
                benchmark_fit_score=round(benchmark_fit_score, 3),
                memory_consistency_score=round(memory_consistency_score, 3),
                decision_value_score=round(decision_value_score, 3),
                uncertainty_penalty=round(uncertainty_penalty, 3),
                risk_penalty=round(risk_penalty, 3),
                cost_penalty=round(cost_penalty, 3),
                reversibility_bonus=round(reversibility_bonus, 3),
                final_score=round(final_score, 3),
                reasons=reasons,
            )
        )

    ordered = sorted(entries, key=lambda item: (item.final_score, item.policy_fit_score, item.decision_value_score), reverse=True)
    winner = ordered[0]
    return AdjudicationScorecard(
        schema_version=ADJUDICATION_SCORECARD_SCHEMA_VERSION,
        generated_at=_utc_now(),
        controls=controls,
        status="ok",
        decision_id=_identifier("decision"),
        decision_scope="next_action",
        winning_claim_id=winner.claim_id,
        winning_action=winner.proposed_action,
        scorecard=ordered,
        why_won=list(winner.reasons) or [f"`{winner.proposed_action}` had the strongest deterministic score."],
        why_not_others=[{"claim_id": item.claim_id, "reason": _losing_reason(item=item, winner=winner)} for item in ordered[1:]],
        summary=f"Relaytic adjudicated {len(ordered)} competing claims and selected `{winner.proposed_action}`.",
    )


def render_trace_review_markdown(bundle: dict[str, Any]) -> str:
    model = dict(bundle.get("trace_model", {}))
    adjudication = dict(bundle.get("adjudication_scorecard", {}))
    scorecard = [dict(item) for item in adjudication.get("scorecard", []) if isinstance(item, dict)]
    lines = [
        "# Relaytic Trace Review",
        "",
        f"- Trace status: `{model.get('status') or 'unknown'}`",
        f"- Span count: `{model.get('span_count', 0)}`",
        f"- Claim count: `{model.get('claim_count', 0)}`",
        f"- Branch count: `{model.get('branch_count', 0)}`",
        f"- Winning claim: `{adjudication.get('winning_claim_id') or 'none'}`",
        f"- Winning action: `{adjudication.get('winning_action') or 'none'}`",
    ]
    if scorecard:
        lines.extend(["", "## Competing Claims"])
        for item in scorecard[:5]:
            lines.append(
                f"- `{item.get('specialist') or 'specialist'}` -> `{item.get('proposed_action') or 'none'}`"
                f" | confidence `{item.get('confidence')}` | final score `{item.get('final_score')}`"
            )
    why_won = [str(item).strip() for item in adjudication.get("why_won", []) if str(item).strip()]
    if why_won:
        lines.extend(["", "## Why Relaytic Chose This"])
        lines.extend(f"- {item}" for item in why_won[:5])
    return "\n".join(lines).rstrip() + "\n"


def render_trace_replay_markdown(bundle: dict[str, Any]) -> str:
    replay = dict(bundle.get("decision_replay_report", {}))
    timeline = [dict(item) for item in replay.get("timeline", []) if isinstance(item, dict)]
    lines = [
        "# Relaytic Trace Replay",
        "",
        f"- Winning claim: `{replay.get('winning_claim_id') or 'none'}`",
        f"- Winning action: `{replay.get('winning_action') or 'none'}`",
        f"- Competing claims: `{replay.get('competing_claim_count', 0)}`",
    ]
    if timeline:
        lines.extend(["", "## Timeline"])
        for item in timeline[:12]:
            lines.append(
                f"- `{item.get('occurred_at') or 'unknown'}` | `{item.get('stage') or 'unknown'}` | `{item.get('event_type') or 'event'}` | {item.get('summary') or 'no summary'}"
            )
    return "\n".join(lines).rstrip() + "\n"


def _merge_spans(*, existing_spans: list[dict[str, Any]], runtime_events: list[dict[str, Any]], controls: TraceControls) -> list[dict[str, Any]]:
    seen_refs = {str(item.get("trace_ref", "")).strip() for item in existing_spans if str(item.get("trace_ref", "")).strip()}
    merged = list(existing_spans)
    if controls.backfill_from_runtime_events:
        for event in runtime_events:
            event_id = _clean_text(event.get("event_id"))
            if event_id and event_id in seen_refs:
                continue
            merged.append(_span_from_runtime_event(event).to_dict())
    return sorted(merged, key=lambda item: (str(item.get("occurred_at", "")), str(item.get("span_id", ""))))


def _build_tool_trace_log(*, existing: list[dict[str, Any]], runtime_events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    records = list(existing)
    seen = {str(item.get("trace_ref", "")).strip() for item in records if str(item.get("trace_ref", "")).strip()}
    for event in runtime_events:
        source_surface = _clean_text(event.get("source_surface"))
        event_id = _clean_text(event.get("event_id"))
        if source_surface not in {"cli", "mcp"} or (event_id and event_id in seen):
            continue
        records.append(
            {
                "schema_version": TRACE_SPAN_SCHEMA_VERSION,
                "trace_ref": event_id,
                "occurred_at": _clean_text(event.get("occurred_at")) or _utc_now(),
                "surface": source_surface,
                "command": _clean_text(event.get("source_command")),
                "stage": _clean_text(event.get("stage")),
                "event_type": _clean_text(event.get("event_type")),
                "status": _clean_text(event.get("status")) or "unknown",
                "summary": _clean_text(event.get("summary")) or "Relaytic recorded one tool-facing runtime event.",
            }
        )
        if event_id:
            seen.add(event_id)
    return sorted(records, key=lambda item: (str(item.get("occurred_at", "")), str(item.get("trace_ref", ""))))


def _build_intervention_trace_log(*, existing: list[dict[str, Any]], control_bundle: dict[str, Any]) -> list[dict[str, Any]]:
    if existing:
        return existing
    request = dict(control_bundle.get("intervention_request", {}))
    decision = dict(control_bundle.get("override_decision", {}))
    challenge = dict(control_bundle.get("control_challenge_report", {}))
    if not request and not decision:
        return []
    return [
        {
            "schema_version": TRACE_SPAN_SCHEMA_VERSION,
            "trace_ref": _clean_text(request.get("request_id")) or _identifier("intervention"),
            "occurred_at": _clean_text(request.get("generated_at")) or _utc_now(),
            "request_classification": _clean_text(request.get("request_classification")),
            "requested_action_kind": _clean_text(request.get("requested_action_kind")),
            "decision": _clean_text(decision.get("decision")),
            "approved_action_kind": _clean_text(decision.get("approved_action_kind")),
            "challenge_level": _clean_text(challenge.get("challenge_level")),
            "skepticism_level": _clean_text(challenge.get("skepticism_level")),
            "summary": _clean_text(decision.get("summary")) or _clean_text(challenge.get("summary")) or "Relaytic reviewed one intervention request.",
        }
    ]


def _build_claim_packets(*, summary_payload: dict[str, Any], spans: list[dict[str, Any]]) -> list[ClaimPacket]:
    span_ref = _latest_trace_ref(spans)
    claims: list[ClaimPacket] = []
    claim_specs = [
        ("completion", "completion_governor", _clean_text(dict(summary_payload.get("completion", {})).get("action")), 0.77, ["completion_decision.json", "run_summary.json"], "completion readiness judgment"),
        ("decision", "decision_lab", _clean_text(dict(summary_payload.get("decision_lab", {})).get("selected_next_action")), 0.74, ["decision_world_model.json", "controller_policy.json", "value_of_more_data_report.json"], "decision-world value optimization"),
        ("benchmark", "benchmark_referee", _clean_text(dict(summary_payload.get("benchmark", {})).get("recommended_action")), 0.91 if _clean_text(dict(summary_payload.get("benchmark", {})).get("beat_target_state")) == "unmet" else 0.7, ["benchmark_parity_report.json", "benchmark_gap_report.json", "beat_target_contract.json"], "reference and incumbent parity pressure"),
        ("autonomy", "autonomy_controller", _clean_text(dict(summary_payload.get("autonomy", {})).get("selected_action")), 0.73, ["autonomy_loop_state.json", "branch_outcome_matrix.json", "loop_budget_report.json"], "bounded closed-loop follow-up"),
        ("control", "control_governor", _clean_text(dict(summary_payload.get("control", {})).get("approved_action_kind")) or _clean_text(dict(summary_payload.get("control", {})).get("decision")), 0.83 if _clean_text(dict(summary_payload.get("control", {})).get("decision")) in {"reject", "defer"} else 0.66, ["intervention_request.json", "control_challenge_report.json", "override_decision.json"], "skeptical steering and safety preservation"),
        ("research", "research_librarian", _clean_text(dict(summary_payload.get("research", {})).get("recommended_followup_action")), 0.68, ["research_brief.json", "method_transfer_report.json", "benchmark_reference_report.json"], "external method-transfer pressure"),
    ]
    for stage, specialist, action, confidence, evidence_refs, objective_frame in claim_specs:
        if not action:
            continue
        claims.append(
            ClaimPacket(
                schema_version=CLAIM_PACKET_SCHEMA_VERSION,
                claim_id=_identifier("claim"),
                generated_at=_utc_now(),
                stage=stage,
                specialist=specialist,
                claim_type="next_action",
                proposed_action=action,
                target_scope="current_run",
                objective_frame=objective_frame,
                confidence=confidence,
                evidence_refs=evidence_refs,
                empirical_support={"source_stage": stage},
                risk_flags=[],
                assumptions=["current artifact state is still valid"],
                falsifiers=["later evidence contradicts this proposal"],
                policy_constraints=["local_truth_first"],
                trace_ref=span_ref,
            )
        )
    return claims


def _build_specialist_trace_index(*, spans: list[dict[str, Any]], controls: TraceControls) -> SpecialistTraceIndexArtifact:
    grouped: dict[str, dict[str, Any]] = {}
    for item in spans:
        specialist = _clean_text(item.get("specialist")) or _clean_text(item.get("stage")) or "unknown"
        entry = grouped.setdefault(specialist, {"specialist": specialist, "span_count": 0, "stages": set(), "last_status": None, "latest_span_id": None})
        entry["span_count"] += 1
        if _clean_text(item.get("stage")):
            entry["stages"].add(_clean_text(item.get("stage")))
        entry["last_status"] = _clean_text(item.get("status")) or entry["last_status"]
        entry["latest_span_id"] = _clean_text(item.get("span_id")) or entry["latest_span_id"]
    entries = [
        {
            "specialist": specialist,
            "span_count": payload["span_count"],
            "stages": sorted(payload["stages"]),
            "last_status": payload["last_status"],
            "latest_span_id": payload["latest_span_id"],
        }
        for specialist, payload in grouped.items()
    ]
    return SpecialistTraceIndexArtifact(
        schema_version=SPECIALIST_TRACE_INDEX_SCHEMA_VERSION,
        generated_at=_utc_now(),
        controls=controls,
        status="ok" if entries else "empty",
        entries=sorted(entries, key=lambda item: item["specialist"]),
        summary=f"Relaytic indexed {len(entries)} specialist traces from canonical runtime spans.",
    )


def _build_branch_trace_graph(*, summary_payload: dict[str, Any], controls: TraceControls) -> BranchTraceGraphArtifact:
    autonomy = dict(summary_payload.get("autonomy", {}))
    winning_branch_id = _clean_text(autonomy.get("winning_branch_id")) or "root"
    executed_branch_count = int(autonomy.get("executed_branch_count", 0) or 0)
    nodes = [{"node_id": "root", "kind": "root", "label": "current_run"}]
    edges: list[dict[str, Any]] = []
    for index in range(max(1, executed_branch_count)):
        node_id = winning_branch_id if index == 0 else f"branch_{index:02d}"
        if node_id == "root":
            continue
        nodes.append({"node_id": node_id, "kind": "branch", "label": node_id, "winning": node_id == winning_branch_id})
        edges.append({"from": "root", "to": node_id, "relation": "candidate_branch"})
    return BranchTraceGraphArtifact(
        schema_version=BRANCH_TRACE_GRAPH_SCHEMA_VERSION,
        generated_at=_utc_now(),
        controls=controls,
        status="ok" if nodes else "empty",
        nodes=nodes,
        edges=edges,
        summary=f"Relaytic recorded {len(nodes)} branch nodes for later replay.",
    )


def _build_decision_replay_report(
    *,
    spans: list[dict[str, Any]],
    claim_packets: list[ClaimPacket],
    adjudication: AdjudicationScorecard,
    controls: TraceControls,
) -> DecisionReplayReportArtifact:
    timeline = [
        {
            "occurred_at": item.get("occurred_at"),
            "stage": item.get("stage"),
            "event_type": item.get("event_type"),
            "source_surface": item.get("source_surface"),
            "summary": item.get("summary"),
            "trace_ref": item.get("trace_ref"),
        }
        for item in sorted(spans, key=lambda item: (str(item.get("occurred_at", "")), str(item.get("span_id", ""))))[-controls.max_replay_spans :]
    ]
    return DecisionReplayReportArtifact(
        schema_version=DECISION_REPLAY_REPORT_SCHEMA_VERSION,
        generated_at=_utc_now(),
        controls=controls,
        status="ok" if timeline else "empty",
        timeline=timeline,
        winning_claim_id=adjudication.winning_claim_id,
        winning_action=adjudication.winning_action,
        competing_claim_count=len(claim_packets),
        summary=f"Relaytic replayed {len(timeline)} trace entries and {len(claim_packets)} competing claims." if timeline else "Relaytic did not have enough trace entries for replay.",
    )


def _span_from_runtime_event(event: dict[str, Any]) -> TraceSpan:
    metadata = dict(event.get("metadata", {})) if isinstance(event.get("metadata"), dict) else {}
    specialists = metadata.get("specialists")
    specialist = str(specialists[0]).strip() if isinstance(specialists, list) and specialists and str(specialists[0]).strip() else None
    evidence_refs = [str(item).strip() for item in metadata.get("output_artifacts", []) if str(item).strip()] if isinstance(metadata.get("output_artifacts"), list) else []
    return TraceSpan(
        schema_version=TRACE_SPAN_SCHEMA_VERSION,
        span_id=_identifier("span"),
        occurred_at=_clean_text(event.get("occurred_at")) or _utc_now(),
        span_kind="runtime_event",
        event_type=_clean_text(event.get("event_type")) or "runtime_event",
        stage=_clean_text(event.get("stage")) or "unknown",
        specialist=specialist,
        source_surface=_clean_text(event.get("source_surface")) or "cli",
        source_command=_clean_text(event.get("source_command")),
        status=_clean_text(event.get("status")) or "unknown",
        summary=_clean_text(event.get("summary")) or "Relaytic recorded one runtime event.",
        trace_ref=_clean_text(event.get("event_id")),
        evidence_refs=evidence_refs,
        metadata=metadata,
    )


def _dict_to_span(payload: dict[str, Any]) -> TraceSpan:
    return TraceSpan(
        schema_version=_clean_text(payload.get("schema_version")) or TRACE_SPAN_SCHEMA_VERSION,
        span_id=_clean_text(payload.get("span_id")) or _identifier("span"),
        occurred_at=_clean_text(payload.get("occurred_at")) or _utc_now(),
        span_kind=_clean_text(payload.get("span_kind")) or "runtime_event",
        event_type=_clean_text(payload.get("event_type")) or "runtime_event",
        stage=_clean_text(payload.get("stage")) or "unknown",
        specialist=_clean_text(payload.get("specialist")),
        source_surface=_clean_text(payload.get("source_surface")) or "cli",
        source_command=_clean_text(payload.get("source_command")),
        status=_clean_text(payload.get("status")) or "unknown",
        summary=_clean_text(payload.get("summary")) or "Relaytic recorded one trace span.",
        trace_ref=_clean_text(payload.get("trace_ref")),
        evidence_refs=[str(item).strip() for item in payload.get("evidence_refs", []) if str(item).strip()] if isinstance(payload.get("evidence_refs"), list) else [],
        metadata=dict(payload.get("metadata", {})) if isinstance(payload.get("metadata"), dict) else {},
    )


def _latest_trace_ref(spans: list[dict[str, Any]]) -> str | None:
    ordered = sorted(spans, key=lambda item: (str(item.get("occurred_at", "")), str(item.get("span_id", ""))))
    for item in reversed(ordered):
        trace_ref = _clean_text(item.get("trace_ref"))
        if trace_ref:
            return trace_ref
    return None


def _cost_penalty(action: str) -> float:
    return {
        "run_retrain_pass": 0.15,
        "expand_challenger_portfolio": 0.12,
        "continue_experimentation": 0.11,
        "run_recalibration_pass": 0.07,
        "collect_more_data": 0.05,
        "operator_review": 0.03,
        "stop_for_now": 0.02,
    }.get(action, 0.06)


def _reversibility_bonus(action: str) -> float:
    return {
        "operator_review": 0.12,
        "collect_more_data": 0.09,
        "run_recalibration_pass": 0.07,
        "continue_experimentation": 0.05,
        "expand_challenger_portfolio": 0.04,
        "stop_for_now": 0.03,
    }.get(action, 0.01)


def _is_aggressive_action(action: str) -> bool:
    return action in {"force_promote", "promote_anyway", "run_retrain_pass", "expand_challenger_portfolio", "continue_experimentation", "take_over"}


def _is_search_heavy_action(action: str) -> bool:
    return action in {"expand_challenger_portfolio", "continue_experimentation", "run_retrain_pass"}


def _is_cautious_action(action: str) -> bool:
    return action in {"operator_review", "stop_for_now", "collect_more_data", "run_recalibration_pass"}


def _losing_reason(*, item: AdjudicationEntry, winner: AdjudicationEntry) -> str:
    if item.confidence > winner.confidence and item.final_score < winner.final_score:
        return "higher confidence lost to a stronger deterministic score under the active contract"
    if item.policy_fit_score < winner.policy_fit_score:
        return "policy fit was weaker than the winning claim"
    if item.decision_value_score < winner.decision_value_score:
        return "decision value was weaker than the winning claim"
    if item.risk_penalty > winner.risk_penalty:
        return "risk penalty was higher than the winning claim"
    return "final score remained below the winning claim"


def _identifier(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex[:12]}"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _clean_text(value: Any) -> str | None:
    text = str(value or "").strip()
    return text or None
