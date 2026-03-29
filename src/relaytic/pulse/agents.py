"""Slice 12A lab pulse, periodic awareness, and bounded proactive follow-up."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from relaytic.benchmark import read_benchmark_bundle
from relaytic.control import read_control_bundle
from relaytic.decision import read_decision_bundle
from relaytic.dojo import read_dojo_bundle
from relaytic.memory import read_memory_bundle
from relaytic.research import read_research_bundle
from relaytic.runs import read_run_summary
from relaytic.runtime import read_runtime_bundle

from .models import (
    CHALLENGE_WATCHLIST_SCHEMA_VERSION,
    INNOVATION_WATCH_REPORT_SCHEMA_VERSION,
    MEMORY_COMPACTION_PLAN_SCHEMA_VERSION,
    MEMORY_COMPACTION_REPORT_SCHEMA_VERSION,
    MEMORY_PINNING_INDEX_SCHEMA_VERSION,
    PULSE_CHECKPOINT_SCHEMA_VERSION,
    PULSE_RECOMMENDATIONS_SCHEMA_VERSION,
    PULSE_RUN_REPORT_SCHEMA_VERSION,
    PULSE_SCHEDULE_SCHEMA_VERSION,
    PULSE_SKIP_REPORT_SCHEMA_VERSION,
    ChallengeWatchlist,
    InnovationWatchReport,
    MemoryCompactionPlan,
    MemoryCompactionReport,
    MemoryPinningIndex,
    PulseBundle,
    PulseCheckpoint,
    PulseControls,
    PulseRecommendations,
    PulseRunReport,
    PulseSchedule,
    PulseSkipReport,
    PulseTrace,
    build_pulse_controls_from_policy,
)
from .storage import read_pulse_bundle


@dataclass(frozen=True)
class PulseRunResult:
    bundle: PulseBundle
    review_markdown: str


def run_pulse_review(
    *,
    run_dir: str | Path,
    policy: dict[str, Any],
    trigger_kind: str = "manual",
) -> PulseRunResult:
    root = Path(run_dir)
    root.mkdir(parents=True, exist_ok=True)
    controls = build_pulse_controls_from_policy(policy)
    trace = PulseTrace(
        agent="lab_pulse",
        operating_mode=controls.mode,
        llm_used=False,
        llm_status="not_requested",
        deterministic_evidence=[
            "run_summary_scan",
            "runtime_state_scan",
            "benchmark_gap_scan",
            "research_freshness_scan",
            "control_memory_scan",
            "memory_compaction_rules",
        ],
    )
    existing = read_pulse_bundle(root)
    summary = read_run_summary(root)
    runtime_bundle = read_runtime_bundle(root)
    memory_bundle = read_memory_bundle(root)
    control_bundle = read_control_bundle(root)
    research_bundle = read_research_bundle(root)
    benchmark_bundle = read_benchmark_bundle(root)
    decision_bundle = read_decision_bundle(root)
    dojo_bundle = read_dojo_bundle(root)

    schedule_state = _build_schedule(
        controls=controls,
        trace=trace,
        trigger_kind=trigger_kind,
        existing_bundle=existing,
    )
    innovation = _build_innovation_watch_report(
        controls=controls,
        trace=trace,
        summary=summary,
        research_bundle=research_bundle,
        benchmark_bundle=benchmark_bundle,
        decision_bundle=decision_bundle,
    )
    compaction_plan = _build_memory_compaction_plan(
        controls=controls,
        trace=trace,
        summary=summary,
        memory_bundle=memory_bundle,
        control_bundle=control_bundle,
    )
    watchlist = _build_challenge_watchlist(
        controls=controls,
        trace=trace,
        summary=summary,
        benchmark_bundle=benchmark_bundle,
        research_bundle=research_bundle,
        dojo_bundle=dojo_bundle,
        runtime_bundle=runtime_bundle,
    )
    recommendations, queued_actions = _build_recommendations(
        controls=controls,
        watchlist=watchlist,
        innovation=innovation,
        compaction_plan=compaction_plan,
    )

    skip_reason = _resolve_skip_reason(
        controls=controls,
        schedule=schedule_state,
        recommendations=recommendations,
        watchlist=watchlist,
        innovation=innovation,
        compaction_plan=compaction_plan,
    )
    pinning_index = _empty_pinning_index(controls=controls, trace=trace)
    compaction_report = _empty_compaction_report(controls=controls, trace=trace)
    executed_actions: list[dict[str, Any]] = []
    run_status = "skipped" if skip_reason else "ok"

    if not skip_reason and controls.mode == "bounded_execute":
        pinning_index = _build_memory_pinning_index(
            controls=controls,
            trace=trace,
            compaction_plan=compaction_plan,
        )
        compaction_report = _build_compaction_report(
            controls=controls,
            trace=trace,
            plan=compaction_plan,
            pinning_index=pinning_index,
            executed=True,
        )
        if pinning_index.pin_count > 0:
            executed_actions.append(
                {
                    "action_id": "memory_compaction_and_pinning",
                    "risk_level": "low",
                    "status": "executed",
                    "detail": "Pulse compacted and pinned memory cues without mutating the source-of-truth modeling artifacts.",
                }
            )
    elif not skip_reason:
        compaction_report = _build_compaction_report(
            controls=controls,
            trace=trace,
            plan=compaction_plan,
            pinning_index=pinning_index,
            executed=False,
        )

    run_report = PulseRunReport(
        schema_version=PULSE_RUN_REPORT_SCHEMA_VERSION,
        generated_at=_utc_now(),
        controls=controls,
        status=run_status,
        mode=controls.mode,
        trigger_kind=trigger_kind,
        executed_actions=executed_actions,
        queued_actions=queued_actions,
        recommendation_count=len(recommendations),
        watchlist_count=len(watchlist.items),
        innovation_lead_count=len(innovation.leads),
        memory_pinned_count=pinning_index.pin_count,
        summary=_run_summary_text(
            status=run_status,
            executed_actions=executed_actions,
            queued_actions=queued_actions,
            leads=len(innovation.leads),
        ),
        trace=trace,
    )
    skip_report = PulseSkipReport(
        schema_version=PULSE_SKIP_REPORT_SCHEMA_VERSION,
        generated_at=_utc_now(),
        controls=controls,
        status="skipped" if skip_reason else "not_skipped",
        trigger_kind=trigger_kind,
        skip_reason=skip_reason,
        due_now=schedule_state.due_now,
        next_due_at=schedule_state.next_due_at,
        summary=(
            f"Pulse skipped: {skip_reason}."
            if skip_reason
            else "Pulse acted or wrote bounded recommendations, so no skip reason applied."
        ),
        trace=trace,
    )
    checkpoint = PulseCheckpoint(
        schema_version=PULSE_CHECKPOINT_SCHEMA_VERSION,
        generated_at=_utc_now(),
        controls=controls,
        status="ok" if not skip_reason else "skip_recorded",
        checkpoint_id=_identifier("pulse"),
        trigger_kind=trigger_kind,
        mode=controls.mode,
        executed_action_count=len(executed_actions),
        artifact_paths=[
            "pulse_schedule.json",
            "pulse_run_report.json",
            "pulse_skip_report.json",
            "pulse_recommendations.json",
            "innovation_watch_report.json",
            "challenge_watchlist.json",
            "pulse_checkpoint.json",
            "memory_compaction_plan.json",
            "memory_compaction_report.json",
            "memory_pinning_index.json",
        ],
        summary="Pulse recorded one bounded awareness checkpoint for later replay and human/agent inspection.",
        trace=trace,
    )
    bundle = PulseBundle(
        pulse_schedule=schedule_state,
        pulse_run_report=run_report,
        pulse_skip_report=skip_report,
        pulse_recommendations=PulseRecommendations(
            schema_version=PULSE_RECOMMENDATIONS_SCHEMA_VERSION,
            generated_at=_utc_now(),
            controls=controls,
            status="ok" if recommendations or queued_actions else "idle",
            mode=controls.mode,
            recommendations=recommendations,
            queued_actions=queued_actions,
            summary=_recommendation_summary(recommendations=recommendations, queued_actions=queued_actions),
            trace=trace,
        ),
        innovation_watch_report=innovation,
        challenge_watchlist=watchlist,
        pulse_checkpoint=checkpoint,
        memory_compaction_plan=compaction_plan,
        memory_compaction_report=compaction_report,
        memory_pinning_index=pinning_index,
    )
    return PulseRunResult(bundle=bundle, review_markdown=render_pulse_review_markdown(bundle.to_dict()))


def render_pulse_review_markdown(bundle: dict[str, Any]) -> str:
    schedule = dict(bundle.get("pulse_schedule", {}))
    run_report = dict(bundle.get("pulse_run_report", {}))
    skip_report = dict(bundle.get("pulse_skip_report", {}))
    recommendations = dict(bundle.get("pulse_recommendations", {}))
    innovation = dict(bundle.get("innovation_watch_report", {}))
    watchlist = dict(bundle.get("challenge_watchlist", {}))
    compaction = dict(bundle.get("memory_compaction_report", {}))
    pinning = dict(bundle.get("memory_pinning_index", {}))
    lines = [
        "# Relaytic Lab Pulse",
        "",
        f"- Mode: `{schedule.get('mode') or 'unknown'}`",
        f"- Due now: `{schedule.get('due_now')}`",
        f"- Throttled: `{schedule.get('throttled')}`",
        f"- Run status: `{run_report.get('status') or 'unknown'}`",
        f"- Skip reason: `{skip_report.get('skip_reason') or 'none'}`",
        f"- Recommendations: `{run_report.get('recommendation_count', 0)}`",
        f"- Watchlist items: `{run_report.get('watchlist_count', 0)}`",
        f"- Innovation leads: `{run_report.get('innovation_lead_count', 0)}`",
        f"- Pinned memory entries: `{run_report.get('memory_pinned_count', 0)}`",
    ]
    queued = [dict(item) for item in recommendations.get("queued_actions", []) if isinstance(item, dict)]
    if queued:
        lines.extend(["", "## Queued Follow-Up"])
        for item in queued[:3]:
            lines.append(f"- `{item.get('action_kind') or 'unknown'}`: {item.get('detail') or 'no detail'}")
    leads = [dict(item) for item in innovation.get("leads", []) if isinstance(item, dict)]
    if leads:
        lines.extend(["", "## Innovation Watch"])
        for item in leads[:3]:
            lines.append(f"- `{item.get('lead_kind') or 'lead'}`: {item.get('title') or 'untitled'}")
    items = [dict(item) for item in watchlist.get("items", []) if isinstance(item, dict)]
    if items:
        lines.extend(["", "## Challenge Watchlist"])
        for item in items[:3]:
            lines.append(f"- `{item.get('watch_kind') or 'watch'}`: {item.get('detail') or 'no detail'}")
    if compaction:
        lines.extend(
            [
                "",
                "## Memory Maintenance",
                f"- Executed: `{compaction.get('executed')}`",
                f"- Retained categories: `{', '.join(compaction.get('retained_categories', [])) or 'none'}`",
                f"- Retrieval hint: `{pinning.get('retrieval_hint') or 'none'}`",
            ]
        )
    return "\n".join(lines) + "\n"


def _build_schedule(
    *,
    controls: PulseControls,
    trace: PulseTrace,
    trigger_kind: str,
    existing_bundle: dict[str, Any],
) -> PulseSchedule:
    last_run = dict(existing_bundle.get("pulse_run_report", {}))
    last_skip = dict(existing_bundle.get("pulse_skip_report", {}))
    last_timestamp = _latest_timestamp(
        _clean_text(last_run.get("generated_at")),
        _clean_text(last_skip.get("generated_at")),
    )
    last_dt = _parse_dt(last_timestamp)
    now = datetime.now(timezone.utc)
    throttled = False
    due_now = True
    next_due_at: str | None = None
    if trigger_kind != "manual" and last_dt is not None:
        due_now = (now - last_dt) >= timedelta(minutes=controls.schedule_minutes)
        throttled = (now - last_dt) < timedelta(minutes=controls.throttle_minutes)
        wait_until = last_dt + timedelta(minutes=max(controls.schedule_minutes, controls.throttle_minutes))
        next_due_at = wait_until.isoformat()
    last_result = _clean_text(last_run.get("status")) or _clean_text(last_skip.get("status"))
    return PulseSchedule(
        schema_version=PULSE_SCHEDULE_SCHEMA_VERSION,
        generated_at=_utc_now(),
        controls=controls,
        status="disabled" if not controls.enabled or controls.mode == "disabled" else "active",
        mode=controls.mode,
        trigger_kind=trigger_kind,
        due_now=due_now,
        throttled=throttled,
        last_run_at=last_timestamp,
        last_result=last_result,
        next_due_at=next_due_at,
        schedule_minutes=controls.schedule_minutes,
        throttle_minutes=controls.throttle_minutes,
        summary="Pulse keeps bounded awareness on an explicit schedule and records when it skipped, recommended, or acted.",
        trace=trace,
    )


def _build_innovation_watch_report(
    *,
    controls: PulseControls,
    trace: PulseTrace,
    summary: dict[str, Any],
    research_bundle: dict[str, Any],
    benchmark_bundle: dict[str, Any],
    decision_bundle: dict[str, Any],
) -> InnovationWatchReport:
    intent = dict(summary.get("intent", {}))
    decision = dict(summary.get("decision", {}))
    query = {
        "task_type": _clean_text(decision.get("task_type")),
        "domain_archetype": _clean_text(intent.get("domain_archetype")),
        "objective": _clean_text(intent.get("objective")),
        "primary_metric": _clean_text(decision.get("primary_metric")),
        "target_semantics": _clean_text(decision.get("target_column")),
        "rowless": True,
    }
    leads: list[dict[str, Any]] = []
    if not controls.allow_innovation_watch:
        return InnovationWatchReport(
            schema_version=INNOVATION_WATCH_REPORT_SCHEMA_VERSION,
            generated_at=_utc_now(),
            controls=controls,
            status="disabled",
            mode=controls.mode,
            rowless_query=query,
            raw_rows_exported=False,
            identifier_leak_detected=False,
            leads=[],
            summary="Innovation watch is disabled by policy.",
            trace=trace,
        )
    method_transfer = dict(research_bundle.get("method_transfer_report", {}))
    accepted = [dict(item) for item in method_transfer.get("accepted_candidates", []) if isinstance(item, dict)]
    for item in accepted[:2]:
        leads.append(
            {
                "lead_kind": str(item.get("candidate_type", "method_transfer") or "method_transfer"),
                "title": _clean_text(item.get("title")) or _clean_text(item.get("reason")) or "Accepted method-transfer lead",
                "source": _clean_text(item.get("source")) or "research_bundle",
                "url": _clean_text(item.get("url")),
                "rowless_query_snapshot": query,
            }
        )
    if not leads:
        benchmark_gap = dict(benchmark_bundle.get("benchmark_gap_report", {}))
        beat_target = dict(benchmark_bundle.get("beat_target_contract", {}))
        if _clean_text(beat_target.get("contract_state")) == "unmet" or benchmark_gap:
            leads.append(
                {
                    "lead_kind": "benchmark_lead",
                    "title": "Benchmark gap suggests a stronger challenger or refreshed external reference set.",
                    "source": "benchmark_gap_report",
                    "url": None,
                    "rowless_query_snapshot": query,
                }
            )
    if not leads:
        method_compiler = dict(decision_bundle.get("method_compiler_report", {}))
        if int(method_compiler.get("compiled_challenger_count", 0) or 0) > 0:
            leads.append(
                {
                    "lead_kind": "compiled_local_lead",
                    "title": "Compiled challenger templates suggest a follow-up benchmark or method-transfer review.",
                    "source": "method_compiler_report",
                    "url": None,
                    "rowless_query_snapshot": query,
                }
            )
    return InnovationWatchReport(
        schema_version=INNOVATION_WATCH_REPORT_SCHEMA_VERSION,
        generated_at=_utc_now(),
        controls=controls,
        status="ok" if controls.allow_innovation_watch else "disabled",
        mode=controls.mode,
        rowless_query=query,
        raw_rows_exported=False,
        identifier_leak_detected=False,
        leads=leads[: controls.max_recommendations],
        summary=(
            "Pulse kept innovation watch rowless and redacted."
            if leads
            else "Pulse did not surface a new innovation lead from current rowless evidence."
        ),
        trace=trace,
    )


def _build_challenge_watchlist(
    *,
    controls: PulseControls,
    trace: PulseTrace,
    summary: dict[str, Any],
    benchmark_bundle: dict[str, Any],
    research_bundle: dict[str, Any],
    dojo_bundle: dict[str, Any],
    runtime_bundle: dict[str, Any],
) -> ChallengeWatchlist:
    items: list[dict[str, Any]] = []
    benchmark = dict(summary.get("benchmark", {}))
    if _clean_text(benchmark.get("beat_target_state")) == "unmet":
        items.append(
            {
                "watch_kind": "benchmark_debt",
                "severity": "medium",
                "detail": "Current incumbent beat-target is unmet, so Relaytic should refresh the challenger or benchmark posture.",
            }
        )
    if int(benchmark.get("reference_count", 0) or 0) == 0 and (summary.get("decision") or summary.get("stage_completed")):
        items.append(
            {
                "watch_kind": "reference_gap",
                "severity": "low",
                "detail": "No benchmark references are visible yet for this run.",
            }
        )
    research_inventory = dict(research_bundle.get("research_source_inventory", {}))
    if not research_inventory and bool(dict(summary.get("research", {})).get("network_allowed")):
        items.append(
            {
                "watch_kind": "research_freshness",
                "severity": "low",
                "detail": "Research is allowed for this run, but no research inventory is currently materialized.",
            }
        )
    dojo_session = dict(dojo_bundle.get("dojo_session", {}))
    if int(dojo_session.get("active_promotion_count", 0) or 0) > 0:
        items.append(
            {
                "watch_kind": "dojo_review",
                "severity": "medium",
                "detail": "There are active dojo promotions that still deserve operator visibility.",
            }
        )
    runtime = dict(runtime_bundle.get("capability_profiles", {}))
    if summary and not runtime:
        items.append(
            {
                "watch_kind": "runtime_visibility",
                "severity": "low",
                "detail": "Runtime capability artifacts are missing, so pulse can only reason from partial local state.",
            }
        )
    return ChallengeWatchlist(
        schema_version=CHALLENGE_WATCHLIST_SCHEMA_VERSION,
        generated_at=_utc_now(),
        controls=controls,
        status="ok" if items else "quiet",
        items=items[: controls.max_watchlist_items],
        summary=(
            f"Pulse wrote {len(items[: controls.max_watchlist_items])} watchlist item(s)."
            if items
            else "Pulse found no stale or weak local state worth watchlisting."
        ),
        trace=trace,
    )


def _build_memory_compaction_plan(
    *,
    controls: PulseControls,
    trace: PulseTrace,
    summary: dict[str, Any],
    memory_bundle: dict[str, Any],
    control_bundle: dict[str, Any],
) -> MemoryCompactionPlan:
    plan_items: list[dict[str, Any]] = []
    if not controls.allow_memory_maintenance:
        return MemoryCompactionPlan(
            schema_version=MEMORY_COMPACTION_PLAN_SCHEMA_VERSION,
            generated_at=_utc_now(),
            controls=controls,
            status="disabled",
            plan_items=[],
            pin_candidate_count=0,
            summary="Memory maintenance is disabled by policy.",
            trace=trace,
        )
    reflection = dict(memory_bundle.get("reflection_memory", {}))
    if reflection:
        plan_items.append(
            {
                "memory_kind": "reflection_memory",
                "action": "retain_summary_lesson",
                "reason": "Prior reflection stays useful for later analog retrieval and operator explanations.",
                "retrieval_boost": 0.04,
            }
        )
    causal_memory = dict(control_bundle.get("causal_memory_index", {}))
    if int(causal_memory.get("similar_harmful_override_count", 0) or 0) > 0:
        plan_items.append(
            {
                "memory_kind": "harmful_override_pattern",
                "action": "pin_harmful_override_memory",
                "reason": "Relaytic should not forget previously harmful override patterns.",
                "retrieval_boost": 0.10,
            }
        )
    method_memory = dict(control_bundle.get("method_memory_index", {}))
    if method_memory:
        plan_items.append(
            {
                "memory_kind": "method_memory",
                "action": "retain_method_outcome_summary",
                "reason": "Method outcomes should remain available for later challenger and research reasoning.",
                "retrieval_boost": 0.03,
            }
        )
    if _clean_text(dict(summary.get("completion", {})).get("blocking_layer")):
        plan_items.append(
            {
                "memory_kind": "blocking_layer_signal",
                "action": "pin_blocking_layer_summary",
                "reason": "Current blocking pressure should remain available for later retrieval and pulse guidance.",
                "retrieval_boost": 0.02,
            }
        )
    return MemoryCompactionPlan(
        schema_version=MEMORY_COMPACTION_PLAN_SCHEMA_VERSION,
        generated_at=_utc_now(),
        controls=controls,
        status="ok" if plan_items else "idle",
        plan_items=plan_items,
        pin_candidate_count=len(plan_items),
        summary=(
            f"Pulse prepared {len(plan_items)} memory maintenance plan item(s)."
            if plan_items
            else "Pulse found no memory items worth compaction or pinning."
        ),
        trace=trace,
    )


def _build_recommendations(
    *,
    controls: PulseControls,
    watchlist: ChallengeWatchlist,
    innovation: InnovationWatchReport,
    compaction_plan: MemoryCompactionPlan,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    recommendations: list[dict[str, Any]] = []
    queued_actions: list[dict[str, Any]] = []
    for item in watchlist.items:
        kind = str(item.get("watch_kind", "")).strip()
        if kind == "benchmark_debt":
            recommendations.append(
                {
                    "recommendation_id": "pulse_refresh_benchmark",
                    "action_kind": "refresh_benchmark_review",
                    "risk_level": "low",
                    "detail": "Refresh benchmark parity and incumbent pressure before widening the search space.",
                }
            )
        elif kind == "research_freshness":
            recommendations.append(
                {
                    "recommendation_id": "pulse_refresh_research",
                    "action_kind": "refresh_research_gather",
                    "risk_level": "low",
                    "detail": "Materialize a fresh rowless research pass because research is allowed but currently missing.",
                }
            )
        elif kind == "dojo_review":
            recommendations.append(
                {
                    "recommendation_id": "pulse_queue_dojo_visibility",
                    "action_kind": "queue_dojo_review",
                    "risk_level": "low",
                    "detail": "Surface active dojo promotions to humans and external agents again.",
                }
            )
    if innovation.leads:
        recommendations.append(
            {
                "recommendation_id": "pulse_innovation_watch",
                "action_kind": "inspect_innovation_lead",
                "risk_level": "low",
                "detail": f"Inspect the top rowless innovation lead: {innovation.leads[0].get('title') or 'untitled lead'}.",
            }
        )
    if compaction_plan.pin_candidate_count > 0:
        recommendations.append(
            {
                "recommendation_id": "pulse_memory_maintenance",
                "action_kind": "memory_compaction",
                "risk_level": "low",
                "detail": "Compact or pin memory cues so later retrieval is less forgetful.",
            }
        )
    recommendations = recommendations[: controls.max_recommendations]
    if controls.allow_queue_refresh and controls.mode in {"propose_only", "bounded_execute"} and recommendations:
        queued_actions = [
            {
                "action_kind": recommendations[0]["action_kind"],
                "detail": recommendations[0]["detail"],
                "queued_by": "lab_pulse",
                "safe_queue": True,
            }
        ][: controls.max_bounded_actions]
    return recommendations, queued_actions


def _resolve_skip_reason(
    *,
    controls: PulseControls,
    schedule: PulseSchedule,
    recommendations: list[dict[str, Any]],
    watchlist: ChallengeWatchlist,
    innovation: InnovationWatchReport,
    compaction_plan: MemoryCompactionPlan,
) -> str | None:
    if not controls.enabled or controls.mode == "disabled":
        return "pulse_disabled_by_policy"
    if schedule.throttled and schedule.trigger_kind != "manual":
        return "pulse_throttled"
    if not recommendations and not watchlist.items and not innovation.leads and compaction_plan.pin_candidate_count == 0:
        return "nothing_useful_pending"
    return None


def _build_memory_pinning_index(
    *,
    controls: PulseControls,
    trace: PulseTrace,
    compaction_plan: MemoryCompactionPlan,
) -> MemoryPinningIndex:
    entries = [
        {
            "pin_id": _identifier("pin"),
            "memory_kind": str(item.get("memory_kind", "memory")).strip() or "memory",
            "pin_reason": str(item.get("reason", "retain high-value memory")).strip(),
            "retrieval_boost": float(item.get("retrieval_boost", 0.03) or 0.03),
            "source_action": str(item.get("action", "retain")).strip() or "retain",
        }
        for item in compaction_plan.plan_items
    ]
    return MemoryPinningIndex(
        schema_version=MEMORY_PINNING_INDEX_SCHEMA_VERSION,
        generated_at=_utc_now(),
        controls=controls,
        status="active" if entries else "idle",
        pin_count=len(entries),
        entries=entries,
        retrieval_hint=(
            "Later analog retrieval may boost or preserve candidates with pinned harmful-override or method-memory cues."
            if entries
            else "No pinning cues are currently active."
        ),
        summary=(
            f"Pulse pinned {len(entries)} memory cue(s) for later retrieval."
            if entries
            else "Pulse did not pin any memory cues."
        ),
        trace=trace,
    )


def _empty_pinning_index(*, controls: PulseControls, trace: PulseTrace) -> MemoryPinningIndex:
    return MemoryPinningIndex(
        schema_version=MEMORY_PINNING_INDEX_SCHEMA_VERSION,
        generated_at=_utc_now(),
        controls=controls,
        status="idle",
        pin_count=0,
        entries=[],
        retrieval_hint="No pinning cues are currently active.",
        summary="Pulse did not pin any memory cues.",
        trace=trace,
    )


def _build_compaction_report(
    *,
    controls: PulseControls,
    trace: PulseTrace,
    plan: MemoryCompactionPlan,
    pinning_index: MemoryPinningIndex,
    executed: bool,
) -> MemoryCompactionReport:
    retained = [
        str(item.get("memory_kind", "")).strip()
        for item in plan.plan_items
        if str(item.get("memory_kind", "")).strip()
    ]
    return MemoryCompactionReport(
        schema_version=MEMORY_COMPACTION_REPORT_SCHEMA_VERSION,
        generated_at=_utc_now(),
        controls=controls,
        status="ok" if plan.plan_items or executed else "idle",
        executed=executed,
        compacted_category_count=len(retained),
        pinned_count=pinning_index.pin_count,
        retained_categories=retained,
        summary=(
            f"Pulse {'executed' if executed else 'prepared'} memory maintenance for {len(retained)} category(s)."
            if retained
            else "Pulse had no memory categories worth compacting."
        ),
        trace=trace,
    )


def _empty_compaction_report(*, controls: PulseControls, trace: PulseTrace) -> MemoryCompactionReport:
    return MemoryCompactionReport(
        schema_version=MEMORY_COMPACTION_REPORT_SCHEMA_VERSION,
        generated_at=_utc_now(),
        controls=controls,
        status="idle",
        executed=False,
        compacted_category_count=0,
        pinned_count=0,
        retained_categories=[],
        summary="Pulse had no memory categories worth compacting.",
        trace=trace,
    )


def _run_summary_text(
    *,
    status: str,
    executed_actions: list[dict[str, Any]],
    queued_actions: list[dict[str, Any]],
    leads: int,
) -> str:
    if status == "skipped":
        return "Pulse skipped after recording why it did not act."
    if executed_actions:
        return f"Pulse executed {len(executed_actions)} bounded low-risk action(s), queued {len(queued_actions)} follow-up action(s), and surfaced {leads} innovation lead(s)."
    return f"Pulse wrote recommendations and watchlists without executing bounded actions; queued {len(queued_actions)} follow-up action(s)."


def _recommendation_summary(*, recommendations: list[dict[str, Any]], queued_actions: list[dict[str, Any]]) -> str:
    if not recommendations and not queued_actions:
        return "Pulse produced no queued follow-up."
    return f"Pulse wrote {len(recommendations)} recommendation(s) and queued {len(queued_actions)} bounded follow-up action(s)."


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _identifier(prefix: str) -> str:
    return f"{prefix}_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')}"


def _clean_text(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _parse_dt(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def _latest_timestamp(*values: str | None) -> str | None:
    parsed = [item for item in (_parse_dt(value) for value in values) if item is not None]
    if not parsed:
        return None
    return max(parsed).isoformat()
