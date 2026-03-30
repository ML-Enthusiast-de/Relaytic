"""Slice 12C differentiated post-run handoff generation and next-run focus."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .models import (
    HandoffBundle,
    HandoffControls,
    HandoffTrace,
    NEXT_RUN_FOCUS_SCHEMA_VERSION,
    NEXT_RUN_OPTIONS_SCHEMA_VERSION,
    RUN_HANDOFF_SCHEMA_VERSION,
    NextRunFocusArtifact,
    NextRunOptionsArtifact,
    RunHandoffArtifact,
    build_handoff_controls_from_policy,
)
from .storage import (
    AGENT_RESULT_REPORT_RELATIVE_PATH,
    USER_RESULT_REPORT_RELATIVE_PATH,
    read_handoff_bundle,
    write_handoff_bundle,
)


NEXT_RUN_OPTION_SPECS: dict[str, dict[str, str]] = {
    "same_data": {
        "label": "Stay on the same dataset",
        "short_detail": "Keep the current dataset and sharpen the focus, thresholds, or route pressure.",
    },
    "add_data": {
        "label": "Add more local data",
        "short_detail": "Expand context with nearby local data or fresh rows before making a stronger claim.",
    },
    "new_dataset": {
        "label": "Start over on a new dataset",
        "short_detail": "Reset the run context and work on a different dataset or problem entirely.",
    },
}


@dataclass(frozen=True)
class HandoffRunResult:
    """Handoff artifacts plus differentiated rendered reports."""

    bundle: HandoffBundle
    user_report_markdown: str
    agent_report_markdown: str
    review_markdown: str
    user_report_path: Path
    agent_report_path: Path


def run_handoff_review(
    *,
    run_dir: str | Path,
    summary_payload: dict[str, Any],
    policy: dict[str, Any] | None = None,
) -> HandoffRunResult:
    """Build a differentiated post-run handoff for humans and agents."""

    root = Path(run_dir)
    controls = build_handoff_controls_from_policy(policy)
    existing = read_handoff_bundle(root)
    existing_focus = dict(existing.get("next_run_focus", {})) if isinstance(existing.get("next_run_focus"), dict) else {}
    selected_focus_id = _clean_text(existing_focus.get("selection_id"))
    generated_at = _utc_now()
    trace = _trace()

    run_id = _clean_text(summary_payload.get("run_id")) or root.name or "run"
    current_stage = _clean_text(summary_payload.get("stage_completed")) or "unknown"
    next_step = dict(summary_payload.get("next_step", {}))
    benchmark = dict(summary_payload.get("benchmark", {}))
    trace_state = dict(summary_payload.get("trace", {}))
    evals = dict(summary_payload.get("evals", {}))
    report_paths = {
        "user": str(root / USER_RESULT_REPORT_RELATIVE_PATH),
        "agent": str(root / AGENT_RESULT_REPORT_RELATIVE_PATH),
    }
    recommended_option_id = _recommended_option_id(summary_payload=summary_payload)
    key_findings = _build_key_findings(summary_payload=summary_payload, controls=controls)
    risks = _build_risks(summary_payload=summary_payload, controls=controls)
    open_questions = _build_open_questions(summary_payload=summary_payload)

    headline = _clean_text(summary_payload.get("headline")) or "Relaytic finished the current governed run."
    user_summary = (
        f"{headline} "
        f"The current recommendation is `{_clean_text(next_step.get('recommended_action')) or 'review the run state'}`. "
        f"Relaytic recommends `{NEXT_RUN_OPTION_SPECS[recommended_option_id]['label']}` as the most coherent next move right now."
    )
    agent_summary = (
        f"run `{run_id}` at stage `{current_stage}` | "
        f"winning_action `{_clean_text(trace_state.get('winning_action')) or _clean_text(next_step.get('recommended_action')) or 'none'}` | "
        f"recommended_option `{recommended_option_id}` | "
        f"protocol `{_clean_text(evals.get('protocol_status')) or 'unknown'}` | "
        f"benchmark `{_clean_text(benchmark.get('parity_status')) or _clean_text(benchmark.get('incumbent_parity_status')) or 'unknown'}`"
    )

    run_handoff = RunHandoffArtifact(
        schema_version=RUN_HANDOFF_SCHEMA_VERSION,
        generated_at=generated_at,
        controls=controls,
        status="ok",
        run_id=run_id,
        current_stage=current_stage,
        headline=headline,
        user_summary=user_summary,
        agent_summary=agent_summary,
        key_findings=key_findings,
        risks=risks,
        open_questions=open_questions,
        recommended_option_id=recommended_option_id,
        selected_focus_id=selected_focus_id,
        report_paths=report_paths,
        summary="Relaytic prepared differentiated user and agent handoffs plus explicit next-run options.",
        trace=trace,
    )
    next_run_options = NextRunOptionsArtifact(
        schema_version=NEXT_RUN_OPTIONS_SCHEMA_VERSION,
        generated_at=generated_at,
        controls=controls,
        status="ok",
        run_id=run_id,
        recommended_option_id=recommended_option_id,
        options=_build_next_run_options(summary_payload=summary_payload, root=root),
        summary="Relaytic prepared bounded next-run options so humans and agents can steer the next iteration explicitly.",
        trace=trace,
    )
    next_run_focus = None
    if selected_focus_id and selected_focus_id in NEXT_RUN_OPTION_SPECS:
        next_run_focus = NextRunFocusArtifact(
            schema_version=NEXT_RUN_FOCUS_SCHEMA_VERSION,
            generated_at=_clean_text(existing_focus.get("generated_at")) or generated_at,
            controls=controls,
            status="selected",
            run_id=run_id,
            selection_id=selected_focus_id,
            selection_label=NEXT_RUN_OPTION_SPECS[selected_focus_id]["label"],
            source=_clean_text(existing_focus.get("source")) or "prior_selection",
            actor_type=_clean_text(existing_focus.get("actor_type")) or "user",
            actor_name=_clean_text(existing_focus.get("actor_name")),
            notes=_clean_text(existing_focus.get("notes")),
            reset_learnings_requested=bool(existing_focus.get("reset_learnings_requested", False)),
            summary=_clean_text(existing_focus.get("summary"))
            or f"Relaytic keeps the previously selected next-run focus `{selected_focus_id}` visible.",
            trace=trace,
        )

    bundle = HandoffBundle(
        run_handoff=run_handoff,
        next_run_options=next_run_options,
        next_run_focus=next_run_focus,
    )
    write_handoff_bundle(root, bundle=bundle)
    user_report_markdown = render_user_result_report(summary_payload=summary_payload, bundle=bundle)
    agent_report_markdown = render_agent_result_report(summary_payload=summary_payload, bundle=bundle)
    user_report_path = root / USER_RESULT_REPORT_RELATIVE_PATH
    agent_report_path = root / AGENT_RESULT_REPORT_RELATIVE_PATH
    user_report_path.parent.mkdir(parents=True, exist_ok=True)
    user_report_path.write_text(user_report_markdown, encoding="utf-8")
    agent_report_path.parent.mkdir(parents=True, exist_ok=True)
    agent_report_path.write_text(agent_report_markdown, encoding="utf-8")
    review_markdown = render_handoff_review_markdown(bundle.to_dict(), audience="both")
    return HandoffRunResult(
        bundle=bundle,
        user_report_markdown=user_report_markdown,
        agent_report_markdown=agent_report_markdown,
        review_markdown=review_markdown,
        user_report_path=user_report_path,
        agent_report_path=agent_report_path,
    )


def apply_next_run_focus(
    *,
    run_dir: str | Path,
    selection_id: str,
    notes: str | None = None,
    source: str = "cli",
    actor_type: str = "user",
    actor_name: str | None = None,
    reset_learnings_requested: bool = False,
    policy: dict[str, Any] | None = None,
) -> NextRunFocusArtifact:
    """Create a persisted next-run focus selection."""

    normalized = _normalize_selection_id(selection_id)
    if normalized not in NEXT_RUN_OPTION_SPECS:
        raise ValueError(
            "Unsupported next-run selection "
            f"`{selection_id}`. Use one of {sorted(NEXT_RUN_OPTION_SPECS)}."
        )
    root = Path(run_dir)
    summary = _read_summary_hint(root)
    run_id = _clean_text(summary.get("run_id")) or root.name or "run"
    controls = build_handoff_controls_from_policy(policy)
    return NextRunFocusArtifact(
        schema_version=NEXT_RUN_FOCUS_SCHEMA_VERSION,
        generated_at=_utc_now(),
        controls=controls,
        status="selected",
        run_id=run_id,
        selection_id=normalized,
        selection_label=NEXT_RUN_OPTION_SPECS[normalized]["label"],
        source=_clean_text(source) or "cli",
        actor_type=_clean_text(actor_type) or "user",
        actor_name=_clean_text(actor_name),
        notes=_clean_text(notes),
        reset_learnings_requested=bool(reset_learnings_requested),
        summary=_focus_summary(
            selection_id=normalized,
            notes=notes,
            reset_learnings_requested=reset_learnings_requested,
        ),
        trace=_trace(),
    )


def render_handoff_review_markdown(bundle: dict[str, Any], *, audience: str = "both") -> str:
    """Render a concise handoff review surface."""

    if audience == "user":
        return _render_user_review_block(bundle)
    if audience == "agent":
        return _render_agent_review_block(bundle)
    return _render_user_review_block(bundle).rstrip() + "\n\n---\n\n" + _render_agent_review_block(bundle)


def render_user_result_report(*, summary_payload: dict[str, Any], bundle: HandoffBundle | dict[str, Any]) -> str:
    """Render the differentiated user-facing result report."""

    payload = bundle.to_dict() if isinstance(bundle, HandoffBundle) else dict(bundle)
    run_handoff = dict(payload.get("run_handoff", {}))
    next_options = dict(payload.get("next_run_options", {}))
    focus = dict(payload.get("next_run_focus") or {})
    findings = [dict(item) for item in run_handoff.get("key_findings", []) if isinstance(item, dict)]
    risks = [dict(item) for item in run_handoff.get("risks", []) if isinstance(item, dict)]
    options = [dict(item) for item in next_options.get("options", []) if isinstance(item, dict)]
    learnings = dict(summary_payload.get("learnings", {}))
    lines = [
        "# Relaytic User Result Report",
        "",
        str(run_handoff.get("user_summary") or run_handoff.get("headline") or "Relaytic completed the requested run."),
        "",
        "## What Relaytic Found",
    ]
    for item in findings[:6]:
        lines.append(f"- {str(item.get('detail') or item.get('title') or 'Finding').strip()}")
    if risks:
        lines.extend(["", "## What Needs Attention"])
        for item in risks[:5]:
            lines.append(f"- {str(item.get('detail') or item.get('title') or 'Risk').strip()}")
    focus_label = _clean_text(focus.get("selection_label"))
    if focus_label:
        lines.extend(
            [
                "",
                "## Current Next-Run Focus",
                f"- Selected focus: `{focus_label}`",
            ]
        )
        if _clean_text(focus.get("notes")):
            lines.append(f"- Notes: {focus.get('notes')}")
        if focus.get("reset_learnings_requested"):
            lines.append("- Learnings reset requested: `True`")
    lines.extend(["", "## Good Next Moves"])
    for item in options[:3]:
        recommended = " (recommended)" if str(item.get("selection_id")) == str(next_options.get("recommended_option_id")) else ""
        lines.append(f"- `{item.get('label')}`{recommended}: {item.get('detail')}")
    lines.extend(
        [
            "",
            "## Where To Look",
            "- Concise run summary: `reports/summary.md`",
            "- Agent handoff: `reports/agent_result_report.md`",
        ]
    )
    if learnings.get("learnings_md_path"):
        lines.append(f"- Durable learnings: `{learnings.get('learnings_md_path')}`")
    lines.extend(
        [
            "",
            "## If You Want To Continue",
            f"- Keep the same data and sharpen the focus: `relaytic handoff focus --run-dir {summary_payload.get('run_dir')} --selection same_data --notes \"focus on recall\"`",
            f"- Add more local data: `relaytic handoff focus --run-dir {summary_payload.get('run_dir')} --selection add_data --notes \"bring in additional local context\"`",
            f"- Start fresh with a new dataset: `relaytic handoff focus --run-dir {summary_payload.get('run_dir')} --selection new_dataset --notes \"start over\"`",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def render_agent_result_report(*, summary_payload: dict[str, Any], bundle: HandoffBundle | dict[str, Any]) -> str:
    """Render the differentiated agent-facing result report."""

    payload = bundle.to_dict() if isinstance(bundle, HandoffBundle) else dict(bundle)
    run_handoff = dict(payload.get("run_handoff", {}))
    next_options = dict(payload.get("next_run_options", {}))
    focus = dict(payload.get("next_run_focus") or {})
    findings = [dict(item) for item in run_handoff.get("key_findings", []) if isinstance(item, dict)]
    risks = [dict(item) for item in run_handoff.get("risks", []) if isinstance(item, dict)]
    options = [dict(item) for item in next_options.get("options", []) if isinstance(item, dict)]
    artifacts = dict(summary_payload.get("artifacts", {}))
    learnings = dict(summary_payload.get("learnings", {}))
    lines = [
        "# Relaytic Agent Result Report",
        "",
        "## Run State",
        f"- Run id: `{summary_payload.get('run_id') or 'unknown'}`",
        f"- Stage completed: `{summary_payload.get('stage_completed') or 'unknown'}`",
        f"- Winning action: `{dict(summary_payload.get('trace', {})).get('winning_action') or dict(summary_payload.get('next_step', {})).get('recommended_action') or 'unknown'}`",
        f"- Recommended option: `{next_options.get('recommended_option_id') or 'same_data'}`",
        f"- Selected focus: `{focus.get('selection_id') or 'none'}`",
        "",
        "## Key Findings",
    ]
    for item in findings[:6]:
        refs = [str(ref).strip() for ref in item.get("artifact_refs", []) if str(ref).strip()]
        ref_text = f" | refs `{', '.join(refs)}`" if refs else ""
        lines.append(f"- `{item.get('finding_id') or 'finding'}` `{item.get('severity') or 'info'}`: {item.get('detail')}{ref_text}")
    if risks:
        lines.extend(["", "## Risks"])
        for item in risks[:5]:
            lines.append(f"- `{item.get('risk_id') or 'risk'}` `{item.get('severity') or 'warning'}`: {item.get('detail')}")
    lines.extend(["", "## Next-Run Options"])
    for item in options[:3]:
        lines.append(f"- `{item.get('selection_id')}`: {item.get('detail')} | command `{item.get('command_hint')}`")
    lines.extend(
        [
            "",
            "## Preferred Artifact Inputs",
            f"- `run_summary.json`: `{artifacts.get('manifest_path') and 'present' or 'available in run dir'}`",
            f"- `run_handoff.json`: `{artifacts.get('run_handoff_path') or 'run_handoff.json'}`",
            f"- `next_run_options.json`: `{artifacts.get('next_run_options_path') or 'next_run_options.json'}`",
            f"- `lab_learnings_snapshot.json`: `{artifacts.get('lab_learnings_snapshot_path') or 'lab_learnings_snapshot.json'}`",
        ]
    )
    if learnings.get("learnings_state_path") or learnings.get("learnings_md_path"):
        lines.extend(
            [
                "",
                "## Durable Learnings",
                f"- State: `{learnings.get('learnings_state_path') or 'lab_memory/learnings_state.json'}`",
                f"- Markdown: `{learnings.get('learnings_md_path') or 'lab_memory/learnings.md'}`",
                f"- Reset: `relaytic learnings reset --run-dir {summary_payload.get('run_dir')}`",
            ]
        )
    lines.extend(
        [
            "",
            "## Recommended Host Actions",
            f"- Show handoff: `relaytic handoff show --run-dir {summary_payload.get('run_dir')} --audience agent --format json`",
            f"- Persist focus: `relaytic handoff focus --run-dir {summary_payload.get('run_dir')} --selection {next_options.get('recommended_option_id') or 'same_data'} --notes \"<focus>\" --format json`",
            f"- Show learnings: `relaytic learnings show --run-dir {summary_payload.get('run_dir')} --format json`",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def _render_user_review_block(bundle: dict[str, Any]) -> str:
    run_handoff = dict(bundle.get("run_handoff", {}))
    next_options = dict(bundle.get("next_run_options", {}))
    focus = dict(bundle.get("next_run_focus") or {})
    lines = [
        "# Relaytic Handoff",
        "",
        f"- Status: `{run_handoff.get('status') or 'unknown'}`",
        f"- Recommended option: `{next_options.get('recommended_option_id') or 'same_data'}`",
        f"- Selected focus: `{focus.get('selection_id') or 'none'}`",
        "",
        str(run_handoff.get("user_summary") or run_handoff.get("summary") or "No user handoff summary available."),
    ]
    return "\n".join(lines).rstrip() + "\n"


def _render_agent_review_block(bundle: dict[str, Any]) -> str:
    run_handoff = dict(bundle.get("run_handoff", {}))
    next_options = dict(bundle.get("next_run_options", {}))
    focus = dict(bundle.get("next_run_focus") or {})
    lines = [
        "# Relaytic Agent Handoff",
        "",
        f"- Status: `{run_handoff.get('status') or 'unknown'}`",
        f"- Recommended option: `{next_options.get('recommended_option_id') or 'same_data'}`",
        f"- Selected focus: `{focus.get('selection_id') or 'none'}`",
        f"- Agent summary: {run_handoff.get('agent_summary') or 'No agent summary available.'}",
    ]
    return "\n".join(lines).rstrip() + "\n"


def _build_key_findings(*, summary_payload: dict[str, Any], controls: HandoffControls) -> list[dict[str, Any]]:
    decision = dict(summary_payload.get("decision", {}))
    benchmark = dict(summary_payload.get("benchmark", {}))
    next_step = dict(summary_payload.get("next_step", {}))
    completion = dict(summary_payload.get("completion", {}))
    trace_state = dict(summary_payload.get("trace", {}))
    evals = dict(summary_payload.get("evals", {}))
    findings: list[dict[str, Any]] = []
    findings.append(
        {
            "finding_id": "route_model",
            "severity": "info",
            "title": "Selected route and model",
            "detail": (
                f"Relaytic selected route `{decision.get('selected_route_title') or decision.get('selected_route_id') or 'unknown'}` "
                f"with model family `{decision.get('selected_model_family') or 'unknown'}`."
            ),
            "artifact_refs": ["run_summary.json", "plan.json", "model_params.json"],
        }
    )
    primary_metric = _clean_text(decision.get("primary_metric")) or "unknown"
    validation_metrics = dict(summary_payload.get("metrics", {})).get("validation", {})
    metric_value = _best_metric_value(validation_metrics, primary_metric=primary_metric)
    findings.append(
        {
            "finding_id": "metric_posture",
            "severity": "info",
            "title": "Metric posture",
            "detail": (
                f"Primary metric is `{primary_metric}`"
                + (f" with current validation value `{metric_value}`." if metric_value is not None else ".")
            ),
            "artifact_refs": ["run_summary.json"],
        }
    )
    findings.append(
        {
            "finding_id": "next_action",
            "severity": "info",
            "title": "Current recommendation",
            "detail": (
                f"Relaytic currently recommends `{_clean_text(next_step.get('recommended_action')) or _clean_text(completion.get('action')) or 'review the run'}` "
                f"because `{_clean_text(next_step.get('rationale')) or 'the current evidence and governors point there'}`."
            ),
            "artifact_refs": ["completion_decision.json", "run_summary.json"],
        }
    )
    if _clean_text(benchmark.get("incumbent_name")):
        findings.append(
            {
                "finding_id": "incumbent",
                "severity": "info",
                "title": "Incumbent parity",
                "detail": (
                    f"Relaytic evaluated incumbent `{benchmark.get('incumbent_name')}` with parity status "
                    f"`{benchmark.get('incumbent_parity_status') or benchmark.get('parity_status') or 'unknown'}`."
                ),
                "artifact_refs": ["incumbent_parity_report.json", "benchmark_parity_report.json"],
            }
        )
    if _clean_text(trace_state.get("winning_action")):
        findings.append(
            {
                "finding_id": "trace_truth",
                "severity": "info",
                "title": "Deterministic adjudication",
                "detail": (
                    f"The canonical trace currently resolves to winning action `{trace_state.get('winning_action')}` "
                    f"with `{trace_state.get('claim_count', 0)}` claim(s) and `{trace_state.get('span_count', 0)}` span(s)."
                ),
                "artifact_refs": ["trace_model.json", "adjudication_scorecard.json", "decision_replay_report.json"],
            }
        )
    if _clean_text(evals.get("protocol_status")):
        findings.append(
            {
                "finding_id": "eval_posture",
                "severity": "info" if int(evals.get("failed_count", 0) or 0) == 0 else "warning",
                "title": "Protocol and security posture",
                "detail": (
                    f"Protocol status is `{evals.get('protocol_status') or 'unknown'}`, "
                    f"security status is `{evals.get('security_status') or 'unknown'}`, "
                    f"and red-team status is `{evals.get('red_team_status') or 'unknown'}`."
                ),
                "artifact_refs": ["agent_eval_matrix.json", "protocol_conformance_report.json", "security_eval_report.json"],
            }
        )
    return findings[: controls.max_findings]


def _build_risks(*, summary_payload: dict[str, Any], controls: HandoffControls) -> list[dict[str, Any]]:
    completion = dict(summary_payload.get("completion", {}))
    benchmark = dict(summary_payload.get("benchmark", {}))
    decision_lab = dict(summary_payload.get("decision_lab", {}))
    contracts = dict(summary_payload.get("contracts", {}))
    evals = dict(summary_payload.get("evals", {}))
    risks: list[dict[str, Any]] = []
    blocking_layer = _clean_text(completion.get("blocking_layer"))
    if blocking_layer and blocking_layer != "none":
        risks.append(
            {
                "risk_id": "blocking_layer",
                "severity": "warning",
                "detail": f"Completion still reports blocking layer `{blocking_layer}`.",
            }
        )
    beat_target_state = _clean_text(benchmark.get("beat_target_state"))
    if beat_target_state and beat_target_state not in {"met", "not_configured"}:
        risks.append(
            {
                "risk_id": "beat_target",
                "severity": "warning",
                "detail": f"Beat-target state is `{beat_target_state}`, so Relaytic should not present this as settled parity yet.",
            }
        )
    if bool(decision_lab.get("review_required")):
        risks.append(
            {
                "risk_id": "review_required",
                "severity": "warning",
                "detail": "Decision lab still wants explicit review before treating the next move as fully settled.",
            }
        )
    quality_gate = _clean_text(contracts.get("quality_gate_status"))
    if quality_gate and quality_gate not in {"pass", "conditional_pass"}:
        risks.append(
            {
                "risk_id": "quality_gate",
                "severity": "warning",
                "detail": f"Quality gate is `{quality_gate}`, so Relaytic still sees material quality risk.",
            }
        )
    if int(evals.get("failed_count", 0) or 0) > 0 or int(evals.get("security_open_finding_count", 0) or 0) > 0:
        risks.append(
            {
                "risk_id": "eval_findings",
                "severity": "warning",
                "detail": (
                    f"Agent/security evals still show `{evals.get('failed_count', 0)}` failed case(s) and "
                    f"`{evals.get('security_open_finding_count', 0)}` open security finding(s)."
                ),
            }
        )
    if not risks:
        risks.append(
            {
                "risk_id": "no_major_blocker",
                "severity": "info",
                "detail": "Relaytic does not currently see a major unresolved blocker in the surfaced governors.",
            }
        )
    return risks[: controls.max_risks]


def _build_open_questions(*, summary_payload: dict[str, Any]) -> list[str]:
    decision_lab = dict(summary_payload.get("decision_lab", {}))
    benchmark = dict(summary_payload.get("benchmark", {}))
    questions: list[str] = []
    if decision_lab.get("recommended_data_path"):
        questions.append("Do you want Relaytic to add the recommended local data source before the next run?")
    if benchmark.get("incumbent_present"):
        questions.append("Should the next run explicitly optimize to beat the incumbent or to improve interpretability/calibration?")
    questions.append("Do you want to keep the same dataset, add more local data, or start over with a new dataset?")
    return questions[:3]


def _build_next_run_options(*, summary_payload: dict[str, Any], root: Path) -> list[dict[str, Any]]:
    decision_lab = dict(summary_payload.get("decision_lab", {}))
    next_step = dict(summary_payload.get("next_step", {}))
    recommended_source = _clean_text(decision_lab.get("recommended_source_id")) or _clean_text(decision_lab.get("recommended_data_path"))
    options: list[dict[str, Any]] = []
    for selection_id, spec in NEXT_RUN_OPTION_SPECS.items():
        detail = spec["short_detail"]
        if selection_id == "same_data":
            detail += (
                f" Relaytic would continue from the current data and push `{_clean_text(next_step.get('recommended_action')) or 'the strongest bounded next action'}`."
            )
        elif selection_id == "add_data":
            if recommended_source:
                detail += f" Relaytic already sees a plausible next local source: `{recommended_source}`."
            else:
                detail += " This is best when you believe the current data is missing context rather than just missing search effort."
        else:
            detail += " This resets the current run framing and tells Relaytic to treat the next dataset as a fresh problem."
        options.append(
            {
                "selection_id": selection_id,
                "label": spec["label"],
                "detail": detail,
                "command_hint": f"relaytic handoff focus --run-dir {root} --selection {selection_id} --notes \"<focus>\"",
            }
        )
    return options


def _recommended_option_id(*, summary_payload: dict[str, Any]) -> str:
    decision_lab = dict(summary_payload.get("decision_lab", {}))
    next_step = dict(summary_payload.get("next_step", {}))
    benchmark = dict(summary_payload.get("benchmark", {}))
    selected_strategy = _clean_text(decision_lab.get("selected_strategy"))
    if selected_strategy in {"collect_additional_local_data", "additional_local_data", "add_data"}:
        return "add_data"
    if _clean_text(decision_lab.get("recommended_data_path")) or _clean_text(decision_lab.get("recommended_source_id")):
        return "add_data"
    if _clean_text(benchmark.get("beat_target_state")) == "unmet":
        return "same_data"
    if _clean_text(next_step.get("recommended_action")) in {
        "run_recalibration_pass",
        "run_retrain_pass",
        "review_challenger",
        "continue_experimentation",
        "promote_challenger",
    }:
        return "same_data"
    return "same_data"


def _focus_summary(*, selection_id: str, notes: str | None, reset_learnings_requested: bool) -> str:
    summary = f"Relaytic persisted next-run focus `{selection_id}`."
    if notes:
        summary += f" Notes: {str(notes).strip()}."
    if reset_learnings_requested:
        summary += " Learnings reset was requested alongside the new focus."
    return summary


def _best_metric_value(metrics: dict[str, Any], *, primary_metric: str) -> str | None:
    if not isinstance(metrics, dict):
        return None
    if primary_metric in metrics:
        try:
            return f"{float(metrics[primary_metric]):.4f}"
        except (TypeError, ValueError):
            return _clean_text(metrics[primary_metric])
    for key in ("f1", "pr_auc", "accuracy", "roc_auc", "r2", "mae"):
        if key in metrics:
            try:
                return f"{float(metrics[key]):.4f}"
            except (TypeError, ValueError):
                return _clean_text(metrics[key])
    return None


def _normalize_selection_id(selection_id: str) -> str:
    normalized = str(selection_id or "").strip().lower().replace("-", "_").replace(" ", "_")
    aliases = {
        "same_dataset": "same_data",
        "same": "same_data",
        "more_data": "add_data",
        "additional_data": "add_data",
        "fresh_start": "new_dataset",
        "start_over": "new_dataset",
    }
    return aliases.get(normalized, normalized)


def _read_summary_hint(run_dir: Path) -> dict[str, Any]:
    path = run_dir / "run_summary.json"
    if not path.exists():
        return {}
    try:
        import json

        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return payload if isinstance(payload, dict) else {}


def _clean_text(value: Any) -> str | None:
    text = str(value or "").strip()
    return text or None


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _trace() -> HandoffTrace:
    return HandoffTrace(
        agent="handoff_coordinator",
        operating_mode="deterministic_post_run_handoff",
        llm_used=False,
        llm_status="not_requested",
        deterministic_evidence=[
            "run_summary",
            "benchmark_posture",
            "decision_lab_posture",
            "trace_truth",
            "agent_evals",
        ],
    )
