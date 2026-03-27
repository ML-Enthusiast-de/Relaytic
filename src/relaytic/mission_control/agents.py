"""Slice 11B mission control, onboarding, and static control-center rendering."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from html import escape
from pathlib import Path
from typing import Any

from relaytic.assist.storage import read_assist_bundle
from relaytic.interoperability.self_check import build_interoperability_inventory
from relaytic.runs.summary import materialize_run_summary, read_run_summary
from relaytic.ui.doctor import build_doctor_report

from .models import (
    CONTROL_CENTER_LAYOUT_SCHEMA_VERSION,
    DEMO_SESSION_MANIFEST_SCHEMA_VERSION,
    INSTALL_EXPERIENCE_REPORT_SCHEMA_VERSION,
    LAUNCH_MANIFEST_SCHEMA_VERSION,
    MISSION_CONTROL_STATE_SCHEMA_VERSION,
    ONBOARDING_STATUS_SCHEMA_VERSION,
    REVIEW_QUEUE_STATE_SCHEMA_VERSION,
    UI_PREFERENCES_SCHEMA_VERSION,
    ControlCenterLayout,
    DemoSessionManifest,
    InstallExperienceReport,
    LaunchManifest,
    MissionControlBundle,
    MissionControlControls,
    MissionControlState,
    MissionControlTrace,
    OnboardingStatus,
    ReviewQueueState,
    UIPreferences,
    build_mission_control_controls_from_policy,
)


@dataclass(frozen=True)
class MissionControlRunResult:
    bundle: MissionControlBundle
    review_markdown: str
    html_report: str


def run_mission_control_review(
    *,
    root_dir: str | Path,
    run_dir: str | Path | None = None,
    expected_profile: str = "full",
    policy: dict[str, Any] | None = None,
    browser_requested: bool = False,
    browser_opened: bool = False,
) -> MissionControlRunResult:
    root = Path(root_dir)
    root.mkdir(parents=True, exist_ok=True)
    resolved_run_dir = Path(run_dir) if run_dir is not None else None
    controls = build_mission_control_controls_from_policy(policy or {})
    normalized_profile = _normalize_expected_profile(expected_profile, controls=controls)
    doctor_report = build_doctor_report(expected_profile=normalized_profile)
    interoperability_inventory = build_interoperability_inventory()
    assist_bundle = read_assist_bundle(resolved_run_dir) if resolved_run_dir else {}
    summary_payload: dict[str, Any] = {}
    summary_paths: dict[str, str | None] = {"summary_path": None, "report_path": None}
    if resolved_run_dir is not None and resolved_run_dir.exists():
        materialized = materialize_run_summary(run_dir=resolved_run_dir)
        summary_payload = dict(materialized.get("summary", {}))
        summary_paths = {
            "summary_path": str(materialized.get("summary_path")) if materialized.get("summary_path") else None,
            "report_path": str(materialized.get("report_path")) if materialized.get("report_path") else None,
        }
    elif resolved_run_dir is not None:
        summary_payload = read_run_summary(resolved_run_dir)
    trace = _trace(
        note="mission-control state derived from canonical run summary, doctor, interoperability inventory, and assist guidance"
    )
    review_queue = _build_review_queue_state(
        controls=controls,
        summary_payload=summary_payload,
        doctor_report=doctor_report,
        trace=trace,
    )
    cards = _build_cards(
        summary_payload=summary_payload,
        doctor_report=doctor_report,
        interoperability_inventory=interoperability_inventory,
        assist_bundle=assist_bundle,
        review_queue=review_queue,
    )
    mission_control_state = MissionControlState(
        schema_version=MISSION_CONTROL_STATE_SCHEMA_VERSION,
        generated_at=_utc_now(),
        controls=controls,
        status="ok" if doctor_report.get("status") in {"ok", "warn"} else "needs_attention",
        state_dir=str(root),
        run_dir=str(resolved_run_dir) if resolved_run_dir is not None else None,
        headline=str(summary_payload.get("headline") or "Relaytic mission control is ready.")[:280],
        current_stage=_clean_text(summary_payload.get("stage_completed"))
        or _clean_text(dict(summary_payload.get("runtime", {})).get("current_stage"))
        or "onboarding",
        recommended_action=_clean_text(dict(summary_payload.get("next_step", {})).get("recommended_action"))
        or ("fix_environment" if doctor_report.get("status") == "error" else "launch_or_run"),
        review_required=bool(dict(summary_payload.get("decision_lab", {})).get("review_required"))
        or review_queue.blocking_count > 0,
        card_count=len(cards),
        review_queue_pending_count=review_queue.pending_count,
        cards=cards,
        summary=_mission_control_summary(summary_payload=summary_payload, doctor_report=doctor_report),
        trace=trace,
    )
    layout = _build_control_center_layout(controls=controls, trace=trace)
    onboarding = _build_onboarding_status(
        controls=controls,
        trace=trace,
        expected_profile=normalized_profile,
        doctor_report=doctor_report,
        interoperability_inventory=interoperability_inventory,
        run_dir=resolved_run_dir,
        root_dir=root,
    )
    install = _build_install_experience_report(
        controls=controls,
        trace=trace,
        expected_profile=normalized_profile,
        doctor_report=doctor_report,
        run_dir=resolved_run_dir,
        root_dir=root,
    )
    ui_preferences = _build_ui_preferences(controls=controls, trace=trace)
    demo_session = _build_demo_session_manifest(
        controls=controls,
        trace=trace,
        summary_payload=summary_payload,
        review_queue=review_queue,
        cards=cards,
    )
    exported_paths = {
        "run_summary_path": summary_paths["summary_path"] or "",
        "summary_report_path": summary_paths["report_path"] or "",
    }
    launch_manifest = LaunchManifest(
        schema_version=LAUNCH_MANIFEST_SCHEMA_VERSION,
        generated_at=_utc_now(),
        controls=controls,
        status="ready" if onboarding.launch_ready else "needs_attention",
        launch_mode="static_html",
        state_dir=str(root),
        run_dir=str(resolved_run_dir) if resolved_run_dir is not None else None,
        html_report_path=str(root / "reports" / "mission_control.html"),
        browser_requested=browser_requested,
        browser_opened=browser_opened,
        openable_url=(root / "reports" / "mission_control.html").resolve().as_uri(),
        exported_paths=exported_paths,
        summary="Relaytic prepared a static local mission-control report that reuses the canonical artifact truth.",
        trace=trace,
    )
    bundle = MissionControlBundle(
        mission_control_state=mission_control_state,
        review_queue_state=review_queue,
        control_center_layout=layout,
        onboarding_status=onboarding,
        install_experience_report=install,
        launch_manifest=launch_manifest,
        demo_session_manifest=demo_session,
        ui_preferences=ui_preferences,
    )
    return MissionControlRunResult(
        bundle=bundle,
        review_markdown=render_mission_control_markdown(bundle.to_dict()),
        html_report=render_mission_control_html(bundle.to_dict()),
    )


def render_mission_control_markdown(bundle: MissionControlBundle | dict[str, Any]) -> str:
    payload = bundle.to_dict() if isinstance(bundle, MissionControlBundle) else dict(bundle)
    state = dict(payload.get("mission_control_state", {}))
    review_queue = dict(payload.get("review_queue_state", {}))
    onboarding = dict(payload.get("onboarding_status", {}))
    launch = dict(payload.get("launch_manifest", {}))
    cards = [dict(item) for item in state.get("cards", []) if isinstance(item, dict)]
    lines = [
        "# Relaytic Mission Control",
        "",
        f"- Status: `{state.get('status') or 'unknown'}`",
        f"- Current stage: `{state.get('current_stage') or 'onboarding'}`",
        f"- Recommended action: `{state.get('recommended_action') or 'none'}`",
        f"- Review queue: `{review_queue.get('pending_count', 0)}` pending / `{review_queue.get('blocking_count', 0)}` blocking",
        f"- Launch ready: `{onboarding.get('launch_ready')}`",
        f"- Doctor status: `{onboarding.get('doctor_status') or 'unknown'}`",
        f"- HTML report: `{launch.get('html_report_path') or 'not written'}`",
        "",
        "## Cards",
    ]
    for item in cards[:8]:
        title = str(item.get("title", "Card")).strip() or "Card"
        lines.append(f"- `{title}`: {str(item.get('value', 'n/a')).strip() or 'n/a'}")
        detail = str(item.get("detail", "")).strip()
        if detail:
            lines.append(f"  {detail}")
    items = [dict(item) for item in review_queue.get("items", []) if isinstance(item, dict)]
    if items:
        lines.extend(["", "## Review Queue"])
        for item in items[:8]:
            lines.append(
                f"- `{item.get('source', 'unknown')}` `{item.get('severity', 'info')}`: "
                f"{str(item.get('title', 'Queued item')).strip()}"
            )
    commands = [str(item).strip() for item in onboarding.get("recommended_commands", []) if str(item).strip()]
    if commands:
        lines.extend(["", "## Commands"])
        lines.extend(f"- `{item}`" for item in commands[:5])
    return "\n".join(lines).rstrip() + "\n"


def render_mission_control_html(bundle: MissionControlBundle | dict[str, Any]) -> str:
    payload = bundle.to_dict() if isinstance(bundle, MissionControlBundle) else dict(bundle)
    state = dict(payload.get("mission_control_state", {}))
    review_queue = dict(payload.get("review_queue_state", {}))
    layout = dict(payload.get("control_center_layout", {}))
    onboarding = dict(payload.get("onboarding_status", {}))
    install = dict(payload.get("install_experience_report", {}))
    launch = dict(payload.get("launch_manifest", {}))
    demo = dict(payload.get("demo_session_manifest", {}))
    cards = [dict(item) for item in state.get("cards", []) if isinstance(item, dict)]
    review_items = [dict(item) for item in review_queue.get("items", []) if isinstance(item, dict)]
    commands = [str(item).strip() for item in onboarding.get("recommended_commands", []) if str(item).strip()]
    panels = [dict(item) for item in layout.get("panels", []) if isinstance(item, dict)]
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Relaytic Mission Control</title>
  <style>
    :root {{
      --bg: #f4efe7;
      --panel: rgba(255,255,255,0.84);
      --panel-strong: #fffaf2;
      --ink: #17212c;
      --muted: #5c6b73;
      --accent: #005f73;
      --warning: #b85c00;
      --danger: #9b2226;
      --ok: #2d6a4f;
      --shadow: 0 20px 45px rgba(23, 33, 44, 0.12);
      --radius: 22px;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: "Aptos", "Segoe UI Variable", "Trebuchet MS", sans-serif;
      color: var(--ink);
      background:
        radial-gradient(circle at top left, rgba(0, 95, 115, 0.12), transparent 36%),
        radial-gradient(circle at bottom right, rgba(184, 92, 0, 0.12), transparent 32%),
        linear-gradient(160deg, #f7f2eb 0%, var(--bg) 48%, #f1ebe2 100%);
      min-height: 100vh;
      padding: 28px;
    }}
    .shell {{ max-width: 1220px; margin: 0 auto; display: grid; gap: 22px; }}
    .hero {{
      background: linear-gradient(135deg, rgba(0,95,115,0.95), rgba(23,33,44,0.94));
      color: #f6fbfb;
      padding: 28px;
      border-radius: 30px;
      box-shadow: var(--shadow);
    }}
    .hero h1 {{ margin: 0 0 10px; font-size: clamp(2rem, 4vw, 3.3rem); letter-spacing: -0.04em; }}
    .hero p {{ margin: 0; color: rgba(246,251,251,0.84); max-width: 820px; line-height: 1.5; }}
    .hero-meta {{ margin-top: 18px; display: flex; flex-wrap: wrap; gap: 10px; }}
    .pill {{
      display: inline-flex;
      align-items: center;
      padding: 8px 14px;
      border-radius: 999px;
      background: rgba(255,255,255,0.12);
      border: 1px solid rgba(255,255,255,0.18);
      font-size: 0.92rem;
    }}
    .grid {{ display: grid; gap: 18px; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); }}
    .card, .panel {{
      background: var(--panel);
      border-radius: var(--radius);
      box-shadow: var(--shadow);
      padding: 20px;
      border: 1px solid rgba(23,33,44,0.06);
    }}
    .card h2, .panel h2 {{ margin: 0 0 10px; font-size: 1rem; text-transform: uppercase; letter-spacing: 0.08em; color: var(--muted); }}
    .card .value {{ font-size: 1.8rem; font-weight: 700; letter-spacing: -0.04em; margin-bottom: 8px; }}
    .card .detail, .panel p, .panel li {{ color: var(--muted); line-height: 1.5; }}
    .panels {{ display: grid; gap: 18px; grid-template-columns: 1.25fr 0.95fr; }}
    .stack {{ display: grid; gap: 18px; }}
    ul {{ margin: 0; padding-left: 18px; }}
    .queue-item {{
      padding: 12px 14px;
      border-radius: 16px;
      background: var(--panel-strong);
      margin-bottom: 10px;
      border-left: 4px solid var(--accent);
    }}
    .queue-item.blocking {{ border-left-color: var(--danger); }}
    .queue-item.warn {{ border-left-color: var(--warning); }}
    .queue-item.ok {{ border-left-color: var(--ok); }}
    .meta-list {{ display: grid; gap: 10px; }}
    .meta-row {{
      display: flex;
      justify-content: space-between;
      gap: 12px;
      padding-bottom: 10px;
      border-bottom: 1px solid rgba(23,33,44,0.08);
    }}
    .meta-row:last-child {{ border-bottom: none; padding-bottom: 0; }}
    .label {{ color: var(--muted); }}
    .value-compact {{ text-align: right; font-weight: 600; }}
    code {{ font-family: "Cascadia Code", "Consolas", monospace; font-size: 0.9rem; background: rgba(23,33,44,0.06); padding: 2px 6px; border-radius: 8px; }}
    @media (max-width: 900px) {{
      body {{ padding: 18px; }}
      .panels {{ grid-template-columns: 1fr; }}
    }}
  </style>
</head>
<body>
  <div class="shell">
    <section class="hero">
      <h1>Relaytic Mission Control</h1>
      <p>{escape(str(state.get("headline") or "Relaytic mission control is ready."))}</p>
      <div class="hero-meta">
        <span class="pill">Stage: {escape(str(state.get("current_stage") or "onboarding"))}</span>
        <span class="pill">Action: {escape(str(state.get("recommended_action") or "none"))}</span>
        <span class="pill">Queue: {escape(str(review_queue.get("pending_count", 0)))} pending</span>
        <span class="pill">Doctor: {escape(str(onboarding.get("doctor_status") or "unknown"))}</span>
        <span class="pill">Demo ready: {escape(str(demo.get("demo_ready")))}</span>
      </div>
    </section>
    <section class="grid">{_render_card_grid(cards)}</section>
    <section class="panels">
      <div class="stack">
        <article class="panel">
          <h2>Review Queue</h2>
          {_render_queue(review_items)}
        </article>
        <article class="panel">
          <h2>Launch + Install</h2>
          <div class="meta-list">
            <div class="meta-row"><span class="label">Install command</span><span class="value-compact"><code>{escape(str(install.get("install_command") or ""))}</code></span></div>
            <div class="meta-row"><span class="label">Doctor command</span><span class="value-compact"><code>{escape(str(install.get("doctor_command") or ""))}</code></span></div>
            <div class="meta-row"><span class="label">Launch command</span><span class="value-compact"><code>{escape(str(install.get("launch_command") or ""))}</code></span></div>
            <div class="meta-row"><span class="label">HTML report</span><span class="value-compact">{escape(str(launch.get("html_report_path") or "not written"))}</span></div>
          </div>
        </article>
      </div>
      <div class="stack">
        <article class="panel">
          <h2>Onboarding</h2>
          <ul>{_render_string_items(commands or ["Relaytic is ready to install, verify, and launch from one surface."])}</ul>
        </article>
        <article class="panel">
          <h2>Layout</h2>
          <ul>{_render_panel_items(panels)}</ul>
        </article>
      </div>
    </section>
  </div>
</body>
</html>"""


def _render_card_grid(cards: list[dict[str, Any]]) -> str:
    chunks: list[str] = []
    for item in cards:
        title = escape(str(item.get("title", "Card")).strip() or "Card")
        value = escape(str(item.get("value", "n/a")).strip() or "n/a")
        detail = escape(str(item.get("detail", "")).strip())
        severity = escape(str(item.get("severity", "normal")).strip() or "normal")
        chunks.append(
            f"<article class=\"card\"><h2>{title}</h2><div class=\"value\">{value}</div><div class=\"detail\">{detail}</div><div class=\"detail\">Severity: {severity}</div></article>"
        )
    return "".join(chunks)


def _render_queue(items: list[dict[str, Any]]) -> str:
    if not items:
        return "<p>No blocking or follow-up items are queued right now.</p>"
    chunks: list[str] = []
    for item in items:
        severity = str(item.get("severity", "info")).strip().lower()
        css = "queue-item"
        if severity in {"blocking", "high"}:
            css += " blocking"
        elif severity in {"warn", "medium"}:
            css += " warn"
        else:
            css += " ok"
        title = escape(str(item.get("title", "Queued item")).strip() or "Queued item")
        detail = escape(str(item.get("detail", "")).strip())
        source = escape(str(item.get("source", "unknown")).strip() or "unknown")
        action = escape(str(item.get("recommended_action", "none")).strip() or "none")
        chunks.append(
            f"<div class=\"{css}\"><strong>{title}</strong><div class=\"detail\">{detail}</div><div class=\"detail\">Source: {source} | Action: {action}</div></div>"
        )
    return "".join(chunks)


def _render_string_items(items: list[str]) -> str:
    return "".join(f"<li>{escape(item)}</li>" for item in items)


def _render_panel_items(items: list[dict[str, Any]]) -> str:
    if not items:
        return "<li>Panel layout is not available.</li>"
    rendered: list[str] = []
    for item in items:
        title = escape(str(item.get("panel_id", "panel")).strip() or "panel")
        detail = escape(str(item.get("title", "")).strip() or "Mission-control panel")
        rendered.append(f"<li><strong>{title}</strong>: {detail}</li>")
    return "".join(rendered)


def _build_review_queue_state(
    *,
    controls: MissionControlControls,
    summary_payload: dict[str, Any],
    doctor_report: dict[str, Any],
    trace: MissionControlTrace,
) -> ReviewQueueState:
    items: list[dict[str, Any]] = []
    contracts = dict(summary_payload.get("contracts", {}))
    benchmark = dict(summary_payload.get("benchmark", {}))
    decision_lab = dict(summary_payload.get("decision_lab", {}))
    control = dict(summary_payload.get("control", {}))
    next_step = dict(summary_payload.get("next_step", {}))

    doctor_status = str(doctor_report.get("status", "")).strip()
    if doctor_status == "error":
        items.append(
            {
                "source": "doctor",
                "severity": "blocking",
                "title": "Environment verification failed",
                "detail": "Required dependencies are missing for the requested install profile.",
                "recommended_action": "fix_environment",
            }
        )
    quality_gate = _clean_text(contracts.get("quality_gate_status"))
    if quality_gate not in {None, "pass", "conditional_pass"}:
        items.append(
            {
                "source": "quality_gate",
                "severity": "blocking",
                "title": "Quality gate is not passing",
                "detail": f"Current quality gate status is `{quality_gate}`.",
                "recommended_action": _clean_text(contracts.get("quality_recommended_action")) or "review_quality",
            }
        )
    beat_target_state = _clean_text(benchmark.get("beat_target_state"))
    if beat_target_state == "unmet":
        items.append(
            {
                "source": "benchmark",
                "severity": "medium",
                "title": "Imported incumbent is still stronger",
                "detail": f"Relaytic is still trailing `{benchmark.get('incumbent_name') or 'the incumbent'}`.",
                "recommended_action": _clean_text(benchmark.get("recommended_action")) or "expand_challenger_portfolio",
            }
        )
    if bool(decision_lab.get("review_required")):
        items.append(
            {
                "source": "decision_lab",
                "severity": "medium",
                "title": "Decision world model requests review",
                "detail": f"Decision strategy is `{decision_lab.get('selected_strategy') or 'unknown'}`.",
                "recommended_action": _clean_text(decision_lab.get("selected_next_action")) or "operator_review",
            }
        )
    if _clean_text(control.get("decision")) in {"accept_with_modification", "defer", "reject"}:
        items.append(
            {
                "source": "control",
                "severity": "medium",
                "title": "Recent steering request was challenged",
                "detail": f"Control decision is `{control.get('decision')}` with challenge level `{control.get('challenge_level') or 'unknown'}`.",
                "recommended_action": _clean_text(control.get("approved_action_kind")) or "review_override",
            }
        )
    if not items and _clean_text(next_step.get("recommended_action")):
        items.append(
            {
                "source": "next_step",
                "severity": "info",
                "title": "Bounded next step is ready",
                "detail": _clean_text(next_step.get("rationale")) or "Relaytic has a visible next step queued.",
                "recommended_action": _clean_text(next_step.get("recommended_action")),
            }
        )
    blocking_count = sum(1 for item in items if item.get("severity") == "blocking")
    status = "ready" if not items else "needs_attention"
    summary = (
        "Relaytic has no blocking review items queued."
        if not items
        else f"Relaytic queued {len(items)} review items, including {blocking_count} blocking items."
    )
    return ReviewQueueState(
        schema_version=REVIEW_QUEUE_STATE_SCHEMA_VERSION,
        generated_at=_utc_now(),
        controls=controls,
        status=status,
        pending_count=len(items),
        blocking_count=blocking_count,
        items=items,
        summary=summary,
        trace=trace,
    )


def _build_cards(
    *,
    summary_payload: dict[str, Any],
    doctor_report: dict[str, Any],
    interoperability_inventory: dict[str, Any],
    assist_bundle: dict[str, Any],
    review_queue: ReviewQueueState,
) -> list[dict[str, Any]]:
    decision = dict(summary_payload.get("decision", {}))
    benchmark = dict(summary_payload.get("benchmark", {}))
    decision_lab = dict(summary_payload.get("decision_lab", {}))
    contracts = dict(summary_payload.get("contracts", {}))
    runtime = dict(summary_payload.get("runtime", {}))
    next_step = dict(summary_payload.get("next_step", {}))
    assist_mode = dict(assist_bundle.get("assist_mode", {}))
    assist_session = dict(assist_bundle.get("assist_session_state", {}))
    host_summary = dict(interoperability_inventory.get("host_summary", {}))
    cards: list[dict[str, Any]] = [
        {
            "card_id": "stage",
            "title": "Current Stage",
            "value": _clean_text(summary_payload.get("stage_completed")) or _clean_text(runtime.get("current_stage")) or "onboarding",
            "detail": str(summary_payload.get("headline") or "No run summary is available yet."),
            "severity": "normal",
        },
        {
            "card_id": "next_action",
            "title": "Next Action",
            "value": _clean_text(next_step.get("recommended_action")) or "launch_or_run",
            "detail": _clean_text(next_step.get("rationale")) or "Relaytic will stay local-first and expose the next bounded step here.",
            "severity": "normal",
        },
        {
            "card_id": "quality_budget",
            "title": "Quality + Budget",
            "value": _clean_text(contracts.get("quality_gate_status")) or "not_materialized",
            "detail": f"Budget `{_clean_text(contracts.get('budget_health')) or 'unknown'}` | trials left `{contracts.get('remaining_trials', 'n/a')}`",
            "severity": "medium" if _clean_text(contracts.get("quality_gate_status")) not in {None, "pass", "conditional_pass"} else "normal",
        },
        {
            "card_id": "incumbent",
            "title": "Incumbent Parity",
            "value": _clean_text(benchmark.get("incumbent_parity_status")) or "no_incumbent",
            "detail": f"Incumbent `{benchmark.get('incumbent_name') or 'none'}` | beat-target `{benchmark.get('beat_target_state') or 'not_configured'}`",
            "severity": "medium" if _clean_text(benchmark.get("beat_target_state")) == "unmet" else "normal",
        },
        {
            "card_id": "decision_lab",
            "title": "Decision Lab",
            "value": _clean_text(decision_lab.get("selected_strategy")) or "hold_current_course",
            "detail": f"Action regime `{decision_lab.get('action_regime') or 'unknown'}` | next actor `{decision_lab.get('next_actor') or 'unknown'}`",
            "severity": "medium" if bool(decision_lab.get("review_required")) else "normal",
        },
        {
            "card_id": "assist_control",
            "title": "Assist + Control",
            "value": _clean_text(assist_session.get("next_recommended_action"))
            or _clean_text(dict(summary_payload.get("next_step", {})).get("recommended_action"))
            or "ready",
            "detail": f"Interactive assist `{assist_mode.get('enabled')}` | takeover `{assist_session.get('takeover_available')}`",
            "severity": "normal",
        },
        {
            "card_id": "environment",
            "title": "Environment",
            "value": _clean_text(doctor_report.get("status")) or "unknown",
            "detail": f"Discoverable hosts `{', '.join(host_summary.get('discoverable_now', [])) or 'none'}` | review queue `{review_queue.pending_count}`",
            "severity": "medium" if _clean_text(doctor_report.get("status")) == "error" else "normal",
        },
    ]
    if decision:
        cards.insert(
            1,
            {
                "card_id": "model",
                "title": "Route + Model",
                "value": _clean_text(decision.get("selected_model_family")) or "not_executed",
                "detail": f"Target `{decision.get('target_column') or 'unknown'}` | metric `{decision.get('primary_metric') or 'unknown'}`",
                "severity": "normal",
            },
        )
    return cards


def _build_control_center_layout(
    *,
    controls: MissionControlControls,
    trace: MissionControlTrace,
) -> ControlCenterLayout:
    panels = [
        {"panel_id": "hero", "title": "Run headline, current stage, and launch posture"},
        {"panel_id": "cards", "title": "Operator cards for model, budget, benchmark, decision, and control"},
        {"panel_id": "review_queue", "title": "Queued blocking and follow-up items"},
        {"panel_id": "onboarding", "title": "Install, doctor, and host-readiness guidance"},
        {"panel_id": "layout", "title": "Panel ownership and expansion path for later slices"},
    ]
    return ControlCenterLayout(
        schema_version=CONTROL_CENTER_LAYOUT_SCHEMA_VERSION,
        generated_at=_utc_now(),
        controls=controls,
        status="ok",
        layout_name="mission_control_mvp",
        default_focus_panel="cards",
        panels=panels,
        summary="Relaytic exposes one thin mission-control layout that reuses the current artifact truth and leaves later slices room to extend the same surface.",
        trace=trace,
    )


def _build_onboarding_status(
    *,
    controls: MissionControlControls,
    trace: MissionControlTrace,
    expected_profile: str,
    doctor_report: dict[str, Any],
    interoperability_inventory: dict[str, Any],
    run_dir: Path | None,
    root_dir: Path,
) -> OnboardingStatus:
    doctor_status = str(doctor_report.get("status", "")).strip() or "unknown"
    host_summary = dict(interoperability_inventory.get("host_summary", {}))
    install_verified = doctor_status in {"ok", "warn"}
    launch_ready = install_verified and bool(doctor_report.get("package", {}).get("installed"))
    commands = [
        f"python scripts/install_relaytic.py --profile {expected_profile} --launch-control-center",
        f"relaytic doctor --expected-profile {expected_profile} --format json",
        (f"relaytic mission-control launch --run-dir {run_dir}" if run_dir is not None else f"relaytic mission-control launch --output-dir {root_dir}"),
    ]
    return OnboardingStatus(
        schema_version=ONBOARDING_STATUS_SCHEMA_VERSION,
        generated_at=_utc_now(),
        controls=controls,
        status="ready" if launch_ready else "needs_attention",
        expected_profile=expected_profile,
        install_verified=install_verified,
        launch_ready=launch_ready,
        package_installed=bool(doctor_report.get("package", {}).get("installed")),
        doctor_status=doctor_status,
        host_summary=host_summary,
        recommended_commands=commands,
        summary="Relaytic install and launch posture is visible from one surface and remains host-neutral.",
        trace=trace,
    )


def _build_install_experience_report(
    *,
    controls: MissionControlControls,
    trace: MissionControlTrace,
    expected_profile: str,
    doctor_report: dict[str, Any],
    run_dir: Path | None,
    root_dir: Path,
) -> InstallExperienceReport:
    install_command = f"python scripts/install_relaytic.py --profile {expected_profile} --launch-control-center"
    doctor_command = f"relaytic doctor --expected-profile {expected_profile} --format json"
    launch_command = f"relaytic mission-control launch --run-dir {run_dir}" if run_dir is not None else f"relaytic mission-control launch --output-dir {root_dir}"
    return InstallExperienceReport(
        schema_version=INSTALL_EXPERIENCE_REPORT_SCHEMA_VERSION,
        generated_at=_utc_now(),
        controls=controls,
        status="ok" if doctor_report.get("status") in {"ok", "warn"} else "needs_attention",
        expected_profile=expected_profile,
        install_mode="one_command_bootstrap",
        install_command=install_command,
        doctor_command=doctor_command,
        launch_command=launch_command,
        doctor_status=str(doctor_report.get("status", "")).strip() or "unknown",
        package_installed=bool(doctor_report.get("package", {}).get("installed")),
        next_steps=[
            "Verify dependency health with Relaytic doctor.",
            "Launch the local control center from one command.",
            "Use the same mission-control state through UI, CLI, or MCP.",
        ],
        summary="Relaytic now has one documented bootstrap path that ends in verification plus a launchable local control center.",
        trace=trace,
    )


def _build_demo_session_manifest(
    *,
    controls: MissionControlControls,
    trace: MissionControlTrace,
    summary_payload: dict[str, Any],
    review_queue: ReviewQueueState,
    cards: list[dict[str, Any]],
) -> DemoSessionManifest:
    benchmark = dict(summary_payload.get("benchmark", {}))
    scenario = "full_run_with_incumbent" if benchmark.get("incumbent_present") else "control_center_mvp"
    return DemoSessionManifest(
        schema_version=DEMO_SESSION_MANIFEST_SCHEMA_VERSION,
        generated_at=_utc_now(),
        controls=controls,
        status="ready",
        demo_ready=bool(cards),
        scenario=scenario,
        highlight_cards=cards[:4],
        incumbent_visible=bool(benchmark.get("incumbent_present")),
        review_queue_pending_count=review_queue.pending_count,
        summary="Relaytic demo sessions can now start from one control-center surface with visible run, benchmark, and next-action posture.",
        trace=trace,
    )


def _build_ui_preferences(
    *,
    controls: MissionControlControls,
    trace: MissionControlTrace,
) -> UIPreferences:
    return UIPreferences(
        schema_version=UI_PREFERENCES_SCHEMA_VERSION,
        generated_at=_utc_now(),
        controls=controls,
        status="defaulted",
        theme=controls.default_theme,
        density="comfortable",
        default_panels=["cards", "review_queue", "onboarding"],
        auto_open_browser=controls.auto_open_browser,
        summary="Relaytic defaults to one comfortable local mission-control layout and can keep extending the same surface in later slices.",
        trace=trace,
    )


def _mission_control_summary(*, summary_payload: dict[str, Any], doctor_report: dict[str, Any]) -> str:
    if summary_payload:
        return f"Relaytic mission control is tracking `{summary_payload.get('stage_completed') or 'unknown'}` with next action `{dict(summary_payload.get('next_step', {})).get('recommended_action') or 'none'}`."
    return f"Relaytic mission control is in onboarding mode with doctor status `{doctor_report.get('status', 'unknown')}`."


def _normalize_expected_profile(value: str | None, *, controls: MissionControlControls) -> str:
    normalized = str(value or controls.default_expected_profile).strip().lower() or controls.default_expected_profile
    return normalized if normalized in {"core", "full"} else controls.default_expected_profile


def _clean_text(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text or text.lower() in {"none", "null"}:
        return None
    return text


def _trace(*, note: str) -> MissionControlTrace:
    return MissionControlTrace(
        agent="mission_control",
        operating_mode="deterministic",
        llm_used=False,
        llm_status="not_used",
        deterministic_evidence=[note],
        advisory_notes=["Mission control is a thin presentation layer over existing Relaytic truth."],
    )


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()
