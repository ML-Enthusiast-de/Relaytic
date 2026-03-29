"""Slice 11B mission control, onboarding, and static control-center rendering."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from html import escape
from pathlib import Path
from typing import Any

from relaytic.assist import build_assist_bundle
from relaytic.assist.storage import read_assist_bundle, write_assist_bundle
from relaytic.intelligence import build_intelligence_controls_from_policy
from relaytic.intelligence.backends import discover_backend
from relaytic.interoperability.self_check import build_interoperability_inventory
from relaytic.runs.summary import materialize_run_summary, read_run_summary
from relaytic.ui.doctor import build_doctor_report

from .models import (
    ACTION_AFFORDANCES_SCHEMA_VERSION,
    CAPABILITY_MANIFEST_SCHEMA_VERSION,
    CONTROL_CENTER_LAYOUT_SCHEMA_VERSION,
    DEMO_SESSION_MANIFEST_SCHEMA_VERSION,
    INSTALL_EXPERIENCE_REPORT_SCHEMA_VERSION,
    LAUNCH_MANIFEST_SCHEMA_VERSION,
    MODE_OVERVIEW_SCHEMA_VERSION,
    MISSION_CONTROL_STATE_SCHEMA_VERSION,
    ONBOARDING_CHAT_SESSION_STATE_SCHEMA_VERSION,
    ONBOARDING_STATUS_SCHEMA_VERSION,
    QUESTION_STARTERS_SCHEMA_VERSION,
    REVIEW_QUEUE_STATE_SCHEMA_VERSION,
    STAGE_NAVIGATOR_SCHEMA_VERSION,
    UI_PREFERENCES_SCHEMA_VERSION,
    ActionAffordances,
    CapabilityManifest,
    ControlCenterLayout,
    DemoSessionManifest,
    InstallExperienceReport,
    LaunchManifest,
    MissionControlBundle,
    MissionControlControls,
    MissionControlState,
    MissionControlTrace,
    ModeOverview,
    OnboardingChatSessionState,
    OnboardingStatus,
    QuestionStarters,
    ReviewQueueState,
    StageNavigator,
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
    assist_bundle = _materialize_mission_control_assist_bundle(
        run_dir=resolved_run_dir,
        policy=policy or {},
        summary_payload=summary_payload,
        interoperability_inventory=interoperability_inventory,
    )
    trace = _trace(
        note="mission-control state derived from canonical run summary, doctor, interoperability inventory, and assist guidance"
    )
    review_queue = _build_review_queue_state(
        controls=controls,
        summary_payload=summary_payload,
        doctor_report=doctor_report,
        trace=trace,
    )
    onboarding_chat_session_state = _build_onboarding_chat_session_state(
        controls=controls,
        trace=trace,
        root_dir=root,
        run_dir=resolved_run_dir,
        policy=policy or {},
    )
    cards = _build_cards(
        summary_payload=summary_payload,
        doctor_report=doctor_report,
        interoperability_inventory=interoperability_inventory,
        assist_bundle=assist_bundle,
        review_queue=review_queue,
        onboarding_chat_session=onboarding_chat_session_state.to_dict(),
    )
    mode_overview = _build_mode_overview(
        controls=controls,
        trace=trace,
        summary_payload=summary_payload,
        assist_bundle=assist_bundle,
    )
    capability_manifest = _build_capability_manifest(
        controls=controls,
        trace=trace,
        summary_payload=summary_payload,
        assist_bundle=assist_bundle,
        interoperability_inventory=interoperability_inventory,
        doctor_report=doctor_report,
    )
    action_affordances = _build_action_affordances(
        controls=controls,
        trace=trace,
        summary_payload=summary_payload,
        assist_bundle=assist_bundle,
        review_queue=review_queue,
    )
    stage_navigator = _build_stage_navigator(
        controls=controls,
        trace=trace,
        summary_payload=summary_payload,
        assist_bundle=assist_bundle,
    )
    question_starters = _build_question_starters(
        controls=controls,
        trace=trace,
        summary_payload=summary_payload,
        assist_bundle=assist_bundle,
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
        next_actor=_clean_text(dict(summary_payload.get("decision_lab", {})).get("next_actor")) or "operator",
        review_required=bool(dict(summary_payload.get("decision_lab", {})).get("review_required"))
        or review_queue.blocking_count > 0,
        card_count=len(cards),
        review_queue_pending_count=review_queue.pending_count,
        capability_count=capability_manifest.capability_count,
        action_count=action_affordances.action_count,
        question_count=question_starters.question_count,
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
        summary_payload=summary_payload,
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
        mode_overview=mode_overview,
        capability_manifest=capability_manifest,
        action_affordances=action_affordances,
        stage_navigator=stage_navigator,
        question_starters=question_starters,
        onboarding_status=onboarding,
        onboarding_chat_session_state=onboarding_chat_session_state,
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
    modes = dict(payload.get("mode_overview", {}))
    capabilities = dict(payload.get("capability_manifest", {}))
    affordances = dict(payload.get("action_affordances", {}))
    navigator = dict(payload.get("stage_navigator", {}))
    questions = dict(payload.get("question_starters", {}))
    onboarding = dict(payload.get("onboarding_status", {}))
    onboarding_session = dict(payload.get("onboarding_chat_session_state", {}))
    launch = dict(payload.get("launch_manifest", {}))
    cards = [dict(item) for item in state.get("cards", []) if isinstance(item, dict)]
    current_requirements = [str(item).strip() for item in onboarding.get("current_requirements", []) if str(item).strip()]
    first_steps = [str(item).strip() for item in onboarding.get("first_steps", []) if str(item).strip()]
    guided_demo_flow = [str(item).strip() for item in onboarding.get("guided_demo_flow", []) if str(item).strip()]
    stuck_guide = [str(item).strip() for item in onboarding.get("stuck_guide", []) if str(item).strip()]
    mode_explanations = [dict(item) for item in onboarding.get("mode_explanations", []) if isinstance(item, dict)]
    interaction_modes = [dict(item) for item in onboarding.get("interaction_modes", []) if isinstance(item, dict)]
    handbooks = [item for item in interaction_modes if str(dict(item).get("kind", "")).strip().lower() == "guide"]
    detected_data_path = str(onboarding_session.get("detected_data_path") or "").strip()
    detected_objective = str(onboarding_session.get("detected_objective") or "").strip()
    objective_family = str(onboarding_session.get("objective_family") or "").strip()
    last_analysis_summary = str(onboarding_session.get("last_analysis_summary") or "").strip()
    last_analysis_report_path = str(onboarding_session.get("last_analysis_report_path") or "").strip()
    next_expected_input = str(onboarding_session.get("next_expected_input") or "").strip()
    lines = [
        "# Relaytic Mission Control",
        "",
        f"- Status: `{state.get('status') or 'unknown'}`",
        f"- Current stage: `{state.get('current_stage') or 'onboarding'}`",
        f"- Recommended action: `{state.get('recommended_action') or 'none'}`",
        f"- Next actor: `{state.get('next_actor') or 'operator'}`",
        f"- Review queue: `{review_queue.get('pending_count', 0)}` pending / `{review_queue.get('blocking_count', 0)}` blocking",
        f"- Capability count: `{state.get('capability_count', 0)}`",
        f"- Action count: `{state.get('action_count', 0)}`",
        f"- Question starters: `{state.get('question_count', 0)}`",
        f"- Launch ready: `{onboarding.get('launch_ready')}`",
        f"- Doctor status: `{onboarding.get('doctor_status') or 'unknown'}`",
        f"- HTML report: `{launch.get('html_report_path') or 'not written'}`",
        "",
        "## What Relaytic Is",
        str(onboarding.get("what_relaytic_is") or "Relaytic is a local-first structured-data lab."),
        "",
    ]
    if current_requirements:
        lines.extend(["## What Relaytic Needs Right Now"])
        lines.extend(f"- {item}" for item in current_requirements[:4])
        lines.append("")
    if first_steps:
        lines.extend(["## First Steps"])
        lines.extend(f"- {item}" for item in first_steps[:6])
        lines.append("")
    if detected_data_path or detected_objective or next_expected_input:
        lines.extend(["## Captured Onboarding State"])
        if detected_data_path:
            lines.append(f"- Detected data path: `{detected_data_path}`")
        if detected_objective:
            lines.append(f"- Detected objective: `{detected_objective}`")
        if objective_family:
            lines.append(f"- Objective family: `{objective_family}`")
        if next_expected_input:
            lines.append(f"- Next expected input: `{next_expected_input}`")
        if last_analysis_summary:
            lines.append(f"- Last direct analysis: {last_analysis_summary}")
        if last_analysis_report_path:
            lines.append(f"- Direct analysis report: `{last_analysis_report_path}`")
        lines.append("")
    if guided_demo_flow:
        lines.extend(["## Guided Demo Flow"])
        lines.extend(f"- {item}" for item in guided_demo_flow[:8])
        lines.append("")
    if mode_explanations:
        lines.extend(["## What The Modes Mean"])
        for item in mode_explanations[:8]:
            name = str(item.get("name", "Mode")).strip() or "Mode"
            detail = str(item.get("detail", "")).strip()
            lines.append(f"- `{name}`: {detail}")
        lines.append("")
    if stuck_guide:
        lines.extend(["## If You Get Stuck"])
        lines.extend(f"- {item}" for item in stuck_guide[:8])
        lines.append("")
    if interaction_modes:
        lines.extend(["## How To Interact"])
        for item in interaction_modes[:6]:
            command = str(item.get("command", "")).strip()
            detail = str(item.get("detail", "")).strip()
            line = f"- `{item.get('name', 'Mode')}`: {detail}"
            if command:
                line += f" Use `{command}`."
            lines.append(line)
        lines.append("")
    if handbooks:
        lines.extend(["## Handbooks"])
        for item in handbooks[:4]:
            command = str(item.get("command", "")).strip()
            detail = str(item.get("detail", "")).strip()
            lines.append(f"- `{item.get('name', 'Handbook')}`: {detail}" + (f" Path: `{command}`." if command else ""))
        lines.append("")
    lines.extend([
        "## Cards",
    ])
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
    if modes:
        lines.extend(
            [
                "",
                "## Modes",
                f"- Autonomy mode: `{modes.get('autonomy_mode') or 'unknown'}`",
                f"- Intelligence mode: `{modes.get('intelligence_effective_mode') or 'unknown'}`",
                f"- Routed intelligence: `{modes.get('intelligence_routed_mode') or 'unknown'}`",
                f"- Local profile: `{modes.get('local_profile') or 'unknown'}`",
                f"- Takeover available: `{modes.get('takeover_available')}`",
                f"- Skeptical control active: `{modes.get('skeptical_control_active')}`",
            ]
        )
    capability_items = [dict(item) for item in capabilities.get("capabilities", []) if isinstance(item, dict)]
    if capability_items:
        lines.extend(["", "## Capabilities"])
        for item in capability_items[:8]:
            lines.append(
                f"- `{item.get('name', 'capability')}` `{item.get('status', 'unknown')}`: "
                f"{str(item.get('detail', '')).strip()}"
            )
        blocked = [
            item
            for item in capability_items
            if str(dict(item).get("status", "")).strip().lower() not in {"enabled", "ready", "ok"}
        ]
        if blocked:
            lines.extend(["", "## Why Some Capabilities Need Setup"])
            for item in blocked[:8]:
                reason = str(item.get("status_reason", "")).strip()
                hint = str(item.get("activation_hint", "")).strip()
                lines.append(f"- `{item.get('name', 'capability')}`: {reason or 'Needs additional setup or run context.'}")
                if hint:
                    lines.append(f"  Next: {hint}")
    action_items = [dict(item) for item in affordances.get("actions", []) if isinstance(item, dict)]
    if action_items:
        lines.extend(["", "## You Can Do Now"])
        for item in action_items[:8]:
            line = (
                f"- `{item.get('title', 'action')}` "
                f"[challenge `{item.get('challenge_level', 'low')}`]: "
                f"{str(item.get('detail', '')).strip()}"
            )
            command_hint = str(item.get("command_hint", "")).strip()
            if command_hint:
                line += f" Use `{command_hint}`."
            lines.append(line)
    stages = [dict(item) for item in navigator.get("available_stages", []) if isinstance(item, dict)]
    if stages:
        lines.extend(
            [
                "",
                "## Stage Navigation",
                f"- Navigation scope: `{navigator.get('navigation_scope') or 'unknown'}`",
                f"- Jump to any point: `{navigator.get('can_jump_to_any_point')}`",
            ]
        )
        for item in stages[:12]:
            lines.append(
                f"- `{item.get('stage', 'unknown')}`: {str(item.get('detail', '')).strip()}"
            )
    starter_items = [dict(item) for item in questions.get("starters", []) if isinstance(item, dict)]
    if starter_items:
        lines.extend(["", "## Ask Relaytic"])
        for item in starter_items[:8]:
            lines.append(
                f"- `{item.get('question', 'question')}`: {str(item.get('detail', '')).strip()}"
            )
    live_chat_command = str(onboarding.get("live_chat_command", "")).strip()
    if live_chat_command:
        lines.extend(
            [
                "",
                "## Live Terminal Chat",
                "- Mission control is a dashboard, not a chat session.",
                f"- To ask questions in the terminal, run `{live_chat_command}`.",
            ]
        )
    commands = [str(item).strip() for item in onboarding.get("recommended_commands", []) if str(item).strip()]
    if commands:
        lines.extend(["", "## Commands"])
        lines.extend(f"- `{item}`" for item in commands[:8])
    return "\n".join(lines).rstrip() + "\n"


def render_mission_control_html(bundle: MissionControlBundle | dict[str, Any]) -> str:
    payload = bundle.to_dict() if isinstance(bundle, MissionControlBundle) else dict(bundle)
    state = dict(payload.get("mission_control_state", {}))
    review_queue = dict(payload.get("review_queue_state", {}))
    layout = dict(payload.get("control_center_layout", {}))
    modes = dict(payload.get("mode_overview", {}))
    capabilities = dict(payload.get("capability_manifest", {}))
    affordances = dict(payload.get("action_affordances", {}))
    navigator = dict(payload.get("stage_navigator", {}))
    questions = dict(payload.get("question_starters", {}))
    onboarding = dict(payload.get("onboarding_status", {}))
    onboarding_session = dict(payload.get("onboarding_chat_session_state", {}))
    install = dict(payload.get("install_experience_report", {}))
    launch = dict(payload.get("launch_manifest", {}))
    demo = dict(payload.get("demo_session_manifest", {}))
    cards = [dict(item) for item in state.get("cards", []) if isinstance(item, dict)]
    review_items = [dict(item) for item in review_queue.get("items", []) if isinstance(item, dict)]
    commands = [str(item).strip() for item in onboarding.get("recommended_commands", []) if str(item).strip()]
    current_requirements = [str(item).strip() for item in onboarding.get("current_requirements", []) if str(item).strip()]
    first_steps = [str(item).strip() for item in onboarding.get("first_steps", []) if str(item).strip()]
    guided_demo_flow = [str(item).strip() for item in onboarding.get("guided_demo_flow", []) if str(item).strip()]
    stuck_guide = [str(item).strip() for item in onboarding.get("stuck_guide", []) if str(item).strip()]
    mode_explanations = [dict(item) for item in onboarding.get("mode_explanations", []) if isinstance(item, dict)]
    interaction_modes = [dict(item) for item in onboarding.get("interaction_modes", []) if isinstance(item, dict)]
    handbook_modes = [item for item in interaction_modes if str(dict(item).get("kind", "")).strip().lower() == "guide"]
    detected_data_path = str(onboarding_session.get("detected_data_path") or "").strip()
    detected_objective = str(onboarding_session.get("detected_objective") or "").strip()
    objective_family = str(onboarding_session.get("objective_family") or "").strip()
    last_analysis_summary = str(onboarding_session.get("last_analysis_summary") or "").strip()
    last_analysis_report_path = str(onboarding_session.get("last_analysis_report_path") or "").strip()
    next_expected_input = str(onboarding_session.get("next_expected_input") or "").strip()
    panels = [dict(item) for item in layout.get("panels", []) if isinstance(item, dict)]
    capability_items = [dict(item) for item in capabilities.get("capabilities", []) if isinstance(item, dict)]
    blocked_capability_items = [
        item
        for item in capability_items
        if str(dict(item).get("status", "")).strip().lower() not in {"enabled", "ready", "ok"}
    ]
    action_items = [dict(item) for item in affordances.get("actions", []) if isinstance(item, dict)]
    stage_items = [dict(item) for item in navigator.get("available_stages", []) if isinstance(item, dict)]
    question_items = [dict(item) for item in questions.get("starters", []) if isinstance(item, dict)]
    hero_body = (
        str(onboarding.get("what_relaytic_is") or "")
        if bool(onboarding.get("needs_data"))
        else str(state.get("headline") or "Relaytic mission control is ready.")
    )
    live_chat_command = str(onboarding.get("live_chat_command") or "relaytic mission-control chat").strip()
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
    .hero-actions {{ margin-top: 18px; display: flex; flex-wrap: wrap; gap: 12px; }}
    .hero-actions code {{
      display: inline-flex;
      align-items: center;
      padding: 8px 12px;
      background: rgba(255,255,255,0.14);
      color: #f6fbfb;
      border: 1px solid rgba(255,255,255,0.18);
    }}
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
    .note {{
      margin-top: 12px;
      padding: 12px 14px;
      border-radius: 16px;
      background: rgba(0,95,115,0.08);
      color: var(--ink);
    }}
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
      <p>{escape(hero_body)}</p>
      <div class="hero-meta">
        <span class="pill">Stage: {escape(str(state.get("current_stage") or "onboarding"))}</span>
        <span class="pill">Action: {escape(str(state.get("recommended_action") or "none"))}</span>
        <span class="pill">Next actor: {escape(str(state.get("next_actor") or "operator"))}</span>
        <span class="pill">Queue: {escape(str(review_queue.get("pending_count", 0)))} pending</span>
        <span class="pill">Doctor: {escape(str(onboarding.get("doctor_status") or "unknown"))}</span>
        <span class="pill">Intelligence: {escape(str(modes.get("intelligence_effective_mode") or "unknown"))}</span>
        <span class="pill">Demo ready: {escape(str(demo.get("demo_ready")))}</span>
      </div>
      <div class="hero-actions">
        <code>{escape(live_chat_command)}</code>
        <code>{escape(str(install.get("launch_command") or "relaytic mission-control launch"))}</code>
      </div>
    </section>
    <section class="grid">{_render_card_grid(cards)}</section>
    <section class="panels">
      <div class="stack">
        <article class="panel">
          <h2>What Relaytic Needs</h2>
          <ul>{_render_string_items(current_requirements or ["Relaytic can explain itself immediately, but it needs data plus a goal before deeper run capabilities activate."])}</ul>
        </article>
        <article class="panel">
          <h2>First Steps</h2>
          <ul>{_render_string_items(first_steps or ["Start with a dataset and a short goal, then open mission control again on the resulting run."])}</ul>
          <div class="note">Mission control is a dashboard. For natural-language questions in the terminal, use <code>{escape(live_chat_command)}</code>.</div>
        </article>
        <article class="panel">
          <h2>Current Onboarding Capture</h2>
          <div class="meta-list">
            <div class="meta-row"><span class="label">Detected data path</span><span class="value-compact">{escape(detected_data_path or "none yet")}</span></div>
            <div class="meta-row"><span class="label">Detected objective</span><span class="value-compact">{escape(detected_objective or "none yet")}</span></div>
            <div class="meta-row"><span class="label">Objective family</span><span class="value-compact">{escape(objective_family or "none yet")}</span></div>
            <div class="meta-row"><span class="label">Next expected input</span><span class="value-compact">{escape(next_expected_input or "data or objective")}</span></div>
            <div class="meta-row"><span class="label">Last direct analysis</span><span class="value-compact">{escape(last_analysis_summary or "none yet")}</span></div>
            <div class="meta-row"><span class="label">Analysis report</span><span class="value-compact">{escape(last_analysis_report_path or "none yet")}</span></div>
          </div>
        </article>
        <article class="panel">
          <h2>Guided Demo Flow</h2>
          <ul>{_render_string_items(guided_demo_flow or ["Run doctor, point Relaytic at data, inspect mission control, ask what it can do, then review the next recommended action."])}</ul>
        </article>
        <article class="panel">
          <h2>If You Get Stuck</h2>
          <ul>{_render_string_items(stuck_guide or ["Use mission-control chat, read the handbook, rerun doctor, and let Relaytic explain the next safe step."])}</ul>
        </article>
        <article class="panel">
          <h2>How To Interact</h2>
          <ul>{_render_interaction_mode_items(interaction_modes)}</ul>
        </article>
        <article class="panel">
          <h2>What The Modes Mean</h2>
          <ul>{_render_mode_explanations(mode_explanations)}</ul>
        </article>
        <article class="panel">
          <h2>Handbooks</h2>
          <ul>{_render_interaction_mode_items(handbook_modes)}</ul>
        </article>
        <article class="panel">
          <h2>Review Queue</h2>
          {_render_queue(review_items)}
        </article>
        <article class="panel">
          <h2>Capabilities</h2>
          <ul>{_render_capability_items(capability_items)}</ul>
        </article>
        <article class="panel">
          <h2>Why Capabilities Need Setup</h2>
          <ul>{_render_capability_setup_items(blocked_capability_items)}</ul>
        </article>
        <article class="panel">
          <h2>Stage Navigator</h2>
          <p>{escape(str(navigator.get("summary") or "Relaytic exposes bounded stage navigation."))}</p>
          <ul>{_render_stage_items(stage_items)}</ul>
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
          <h2>Modes</h2>
          <div class="meta-list">
            <div class="meta-row"><span class="label">Autonomy</span><span class="value-compact">{escape(str(modes.get("autonomy_mode") or "unknown"))}</span></div>
            <div class="meta-row"><span class="label">Intelligence</span><span class="value-compact">{escape(str(modes.get("intelligence_effective_mode") or "unknown"))}</span></div>
            <div class="meta-row"><span class="label">Routed</span><span class="value-compact">{escape(str(modes.get("intelligence_routed_mode") or "unknown"))}</span></div>
            <div class="meta-row"><span class="label">Takeover</span><span class="value-compact">{escape(str(modes.get("takeover_available")))}</span></div>
            <div class="meta-row"><span class="label">Skeptical control</span><span class="value-compact">{escape(str(modes.get("skeptical_control_active")))}</span></div>
          </div>
        </article>
        <article class="panel">
          <h2>You Can Do Now</h2>
          <ul>{_render_action_items(action_items)}</ul>
        </article>
        <article class="panel">
          <h2>Ask Relaytic</h2>
          <ul>{_render_question_items(question_items)}</ul>
        </article>
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


def _render_capability_items(items: list[dict[str, Any]]) -> str:
    if not items:
        return "<li>No capability summary is available yet.</li>"
    rendered: list[str] = []
    for item in items[:10]:
        name = escape(str(item.get("name", "capability")).strip() or "capability")
        status = escape(str(item.get("status", "unknown")).strip() or "unknown")
        detail = escape(str(item.get("detail", "")).strip() or "No detail available.")
        reason = escape(str(item.get("status_reason", "")).strip())
        hint = escape(str(item.get("activation_hint", "")).strip())
        extra = ""
        if reason:
            extra += f"<div class=\"detail\">Why: {reason}</div>"
        if hint:
            extra += f"<div class=\"detail\">Next: {hint}</div>"
        rendered.append(f"<li><strong>{name}</strong> [{status}]: {detail}{extra}</li>")
    return "".join(rendered)


def _render_capability_setup_items(items: list[dict[str, Any]]) -> str:
    if not items:
        return "<li>Nothing important is blocked right now. Current capabilities are ready.</li>"
    rendered: list[str] = []
    for item in items[:10]:
        name = escape(str(item.get("name", "capability")).strip() or "capability")
        status = escape(str(item.get("status", "unknown")).strip() or "unknown")
        reason = escape(str(item.get("status_reason", "")).strip() or "Needs additional setup or run context.")
        hint = escape(str(item.get("activation_hint", "")).strip())
        suffix = f" Next: {hint}" if hint else ""
        rendered.append(f"<li><strong>{name}</strong> [{status}]: {reason}{suffix}</li>")
    return "".join(rendered)


def _render_action_items(items: list[dict[str, Any]]) -> str:
    if not items:
        return "<li>No action affordances are available yet.</li>"
    rendered: list[str] = []
    for item in items[:10]:
        title = escape(str(item.get("title", "action")).strip() or "action")
        detail = escape(str(item.get("detail", "")).strip() or "No detail available.")
        challenge = escape(str(item.get("challenge_level", "low")).strip() or "low")
        command_hint = escape(str(item.get("command_hint", "")).strip())
        suffix = f" Use <code>{command_hint}</code>." if command_hint else ""
        rendered.append(f"<li><strong>{title}</strong> [challenge {challenge}]: {detail}{suffix}</li>")
    return "".join(rendered)


def _render_stage_items(items: list[dict[str, Any]]) -> str:
    if not items:
        return "<li>No bounded stage reruns are available yet.</li>"
    rendered: list[str] = []
    for item in items[:14]:
        stage = escape(str(item.get("stage", "unknown")).strip() or "unknown")
        detail = escape(str(item.get("detail", "")).strip() or "No detail available.")
        rendered.append(f"<li><strong>{stage}</strong>: {detail}</li>")
    return "".join(rendered)


def _render_question_items(items: list[dict[str, Any]]) -> str:
    if not items:
        return "<li>No starter questions are available yet.</li>"
    rendered: list[str] = []
    for item in items[:10]:
        question = escape(str(item.get("question", "question")).strip() or "question")
        detail = escape(str(item.get("detail", "")).strip() or "No detail available.")
        rendered.append(f"<li><code>{question}</code>: {detail}</li>")
    return "".join(rendered)


def _render_interaction_mode_items(items: list[dict[str, Any]]) -> str:
    if not items:
        return "<li>Mission control can be opened in the browser or used through the terminal.</li>"
    rendered: list[str] = []
    for item in items[:8]:
        name = escape(str(item.get("name", "Mode")).strip() or "Mode")
        detail = escape(str(item.get("detail", "")).strip() or "No detail available.")
        command = escape(str(item.get("command", "")).strip())
        suffix = f" Use <code>{command}</code>." if command else ""
        rendered.append(f"<li><strong>{name}</strong>: {detail}{suffix}</li>")
    return "".join(rendered)


def _render_mode_explanations(items: list[dict[str, Any]]) -> str:
    if not items:
        return "<li>Mode explanations are not available yet.</li>"
    rendered: list[str] = []
    for item in items[:8]:
        name = escape(str(item.get("name", "Mode")).strip() or "Mode")
        detail = escape(str(item.get("detail", "")).strip() or "No detail available.")
        rendered.append(f"<li><strong>{name}</strong>: {detail}</li>")
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
    dojo = dict(summary_payload.get("dojo", {}))
    control = dict(summary_payload.get("control", {}))
    trace_state = dict(summary_payload.get("trace", {}))
    evals = dict(summary_payload.get("evals", {}))
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
    if int(dojo.get("active_promotion_count", 0) or 0) > 0:
        items.append(
            {
                "source": "dojo",
                "severity": "info",
                "title": "Quarantined dojo promotions are available",
                "detail": f"Relaytic has `{dojo.get('active_promotion_count', 0)}` guarded promotions under quarantine.",
                "recommended_action": "review_dojo",
            }
        )
    if _clean_text(dojo.get("control_security_state")) == "fail":
        items.append(
            {
                "source": "dojo",
                "severity": "medium",
                "title": "Dojo promotions are blocked by control-security evidence",
                "detail": "Recent skeptical-control evidence is preventing self-improvement promotions.",
                "recommended_action": "review_control",
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
    if _clean_text(trace_state.get("status")) not in {None, "ok", "empty"}:
        items.append(
            {
                "source": "trace",
                "severity": "medium",
                "title": "Trace truth needs review",
                "detail": f"Trace status is `{trace_state.get('status')}` and winning action is `{trace_state.get('winning_action') or 'unknown'}`.",
                "recommended_action": "trace_show",
            }
        )
    if _clean_text(evals.get("protocol_status")) == "fail":
        items.append(
            {
                "source": "evals",
                "severity": "blocking",
                "title": "Host-surface protocol conformance failed",
                "detail": f"Relaytic detected `{evals.get('protocol_mismatch_count', 0)}` CLI vs MCP mismatches.",
                "recommended_action": "evals_show",
            }
        )
    if int(evals.get("security_open_finding_count", 0) or 0) > 0:
        items.append(
            {
                "source": "evals",
                "severity": "medium",
                "title": "Security evals recorded open findings",
                "detail": f"Relaytic still has `{evals.get('security_open_finding_count', 0)}` open security findings.",
                "recommended_action": "evals_show",
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
    onboarding_chat_session: dict[str, Any],
) -> list[dict[str, Any]]:
    if _is_onboarding_state(summary_payload):
        host_summary = dict(interoperability_inventory.get("host_summary", {}))
        discoverable_hosts = ", ".join(host_summary.get("discoverable_now", [])) or "none"
        detected_data_path = _clean_text(onboarding_chat_session.get("detected_data_path"))
        detected_objective = _clean_text(onboarding_chat_session.get("detected_objective"))
        objective_family = _clean_text(onboarding_chat_session.get("objective_family"))
        last_analysis_summary = _clean_text(onboarding_chat_session.get("last_analysis_summary"))
        next_expected_input = _clean_text(onboarding_chat_session.get("next_expected_input"))
        current_capture_value = "none yet"
        current_capture_detail = "Paste a dataset path, describe the objective, or do both in one messy sentence."
        if detected_data_path and detected_objective:
            current_capture_value = "data + objective"
            current_capture_detail = (
                f"Relaytic has `{detected_data_path}` and objective `{detected_objective}`. "
                + (f"Objective family is `{objective_family}`. " if objective_family else "")
                + ("Next expected input is " + f"`{next_expected_input}`." if next_expected_input else "The next step is confirmation before creating the run.")
            )
        elif detected_data_path:
            current_capture_value = "data captured"
            current_capture_detail = (
                f"Relaytic detected `{detected_data_path}`. "
                + (f"Next expected input is `{next_expected_input}`." if next_expected_input else "It now needs the objective.")
            )
        elif detected_objective:
            current_capture_value = "objective captured"
            current_capture_detail = (
                f"Relaytic detected `{detected_objective}`. "
                + (f"Objective family is `{objective_family}`. " if objective_family else "")
                + (f"Next expected input is `{next_expected_input}`." if next_expected_input else "It now needs a dataset path.")
            )
        if last_analysis_summary:
            current_capture_value = "analysis completed"
            current_capture_detail = last_analysis_summary
        return [
            {
                "card_id": "what_is_relaytic",
                "title": "What Relaytic Is",
                "value": "Local inference lab",
                "detail": "Relaytic is a local-first structured-data research lab. It needs data plus a goal before the deeper modeling and review layers become meaningful.",
                "severity": "normal",
            },
            {
                "card_id": "what_it_needs",
                "title": "What It Needs",
                "value": "data + intent",
                "detail": "Point Relaytic to a dataset or local source and tell it whether you want a quick analysis first or a governed modeling run.",
                "severity": "normal",
            },
            {
                "card_id": "fastest_start",
                "title": "Fastest Start",
                "value": "relaytic run",
                "detail": f"Use `{_example_run_command(run_dir=None)}` to create the first governed run.",
                "severity": "normal",
            },
            {
                "card_id": "terminal_chat",
                "title": "Live Terminal Chat",
                "value": "mission-control chat",
                "detail": "Mission control is a dashboard, not a chat. Use `relaytic mission-control chat` to ask questions in the terminal.",
                "severity": "normal",
            },
            {
                "card_id": "handbooks",
                "title": "Handbooks",
                "value": "human + agent",
                "detail": f"Read `{_human_handbook_path()}` for the human guide or `{_agent_handbook_path()}` for the command-first agent guide.",
                "severity": "normal",
            },
            {
                "card_id": "guided_demo",
                "title": "Guided Demo",
                "value": "5-step flow",
                "detail": "Mission control now exposes a recruiter-friendly demo path, mode explanations, and stuck recovery instead of assuming repo literacy.",
                "severity": "normal",
            },
            {
                "card_id": "current_capture",
                "title": "Current Capture",
                "value": current_capture_value,
                "detail": current_capture_detail,
                "severity": "normal",
            },
            {
                "card_id": "host_readiness",
                "title": "Host Readiness",
                "value": discoverable_hosts,
                "detail": "Relaytic can already be called locally by the discoverable hosts above; others need activation or remote connector setup.",
                "severity": "normal",
            },
            {
                "card_id": "environment",
                "title": "Environment",
                "value": _clean_text(doctor_report.get("status")) or "unknown",
                "detail": "Doctor verifies the local install before you start a run or connect a host.",
                "severity": "medium" if _clean_text(doctor_report.get("status")) == "error" else "normal",
            },
        ]
    decision = dict(summary_payload.get("decision", {}))
    benchmark = dict(summary_payload.get("benchmark", {}))
    decision_lab = dict(summary_payload.get("decision_lab", {}))
    dojo = dict(summary_payload.get("dojo", {}))
    pulse = dict(summary_payload.get("pulse", {}))
    trace_state = dict(summary_payload.get("trace", {}))
    evals = dict(summary_payload.get("evals", {}))
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
            "card_id": "dojo",
            "title": "Dojo",
            "value": _clean_text(dojo.get("status")) or "not_reviewed",
            "detail": f"Promotions `{dojo.get('active_promotion_count', 0)}` | rejected `{dojo.get('rejected_count', 0)}` | benchmark `{dojo.get('benchmark_state') or 'unknown'}`",
            "severity": "medium" if _clean_text(dojo.get("control_security_state")) == "fail" else "normal",
        },
        {
            "card_id": "pulse",
            "title": "Pulse",
            "value": _clean_text(pulse.get("status")) or "not_run",
            "detail": (
                f"Mode `{pulse.get('mode') or 'unknown'}`"
                f" | queued `{pulse.get('queued_action_count', 0)}`"
                f" | leads `{pulse.get('innovation_lead_count', 0)}`"
            ),
            "severity": "medium" if _clean_text(pulse.get("skip_reason")) in {"pulse_disabled_by_policy", "pulse_throttled"} else "normal",
        },
        {
            "card_id": "trace_evals",
            "title": "Trace + Evals",
            "value": _clean_text(trace_state.get("winning_action")) or _clean_text(trace_state.get("status")) or "not_materialized",
            "detail": (
                f"Trace spans `{trace_state.get('span_count', 0)}`"
                f" | protocol `{evals.get('protocol_status') or 'unknown'}`"
                f" | security `{evals.get('security_status') or 'unknown'}`"
            ),
            "severity": "medium" if _clean_text(evals.get("protocol_status")) == "fail" or int(evals.get("failed_count", 0) or 0) > 0 else "normal",
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
            "card_id": "modes",
            "title": "Modes",
            "value": _clean_text(dict(summary_payload.get("intelligence", {})).get("effective_mode")) or "deterministic",
            "detail": (
                f"Autonomy `{dict(summary_payload.get('intent', {})).get('autonomy_mode') or 'unknown'}`"
                f" | next actor `{dict(summary_payload.get('decision_lab', {})).get('next_actor') or 'operator'}`"
            ),
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


def _build_mode_overview(
    *,
    controls: MissionControlControls,
    trace: MissionControlTrace,
    summary_payload: dict[str, Any],
    assist_bundle: dict[str, Any],
) -> ModeOverview:
    intelligence = dict(summary_payload.get("intelligence", {}))
    intent = dict(summary_payload.get("intent", {}))
    decision_lab = dict(summary_payload.get("decision_lab", {}))
    assist_state = dict(assist_bundle.get("assist_session_state", {}))
    control = dict(summary_payload.get("control", {}))
    current_stage = _clean_text(summary_payload.get("stage_completed")) or "onboarding"
    next_actor = _clean_text(decision_lab.get("next_actor")) or "operator"
    return ModeOverview(
        schema_version=MODE_OVERVIEW_SCHEMA_VERSION,
        generated_at=_utc_now(),
        controls=controls,
        status="ok",
        current_stage=current_stage,
        next_actor=next_actor,
        autonomy_mode=_clean_text(intent.get("autonomy_mode")) or ("guided_onboarding" if _is_onboarding_state(summary_payload) else None),
        intelligence_effective_mode=_clean_text(intelligence.get("effective_mode")) or "deterministic",
        intelligence_routed_mode=_clean_text(intelligence.get("routed_mode")) or "deterministic",
        local_profile=_clean_text(intelligence.get("local_profile")) or "not_selected",
        takeover_available=bool(assist_state.get("takeover_available", False)),
        skeptical_control_active=bool(control) or True,
        summary=(
            f"Relaytic is at `{current_stage}` with next actor `{next_actor}`, "
            f"intelligence mode `{_clean_text(intelligence.get('effective_mode')) or 'deterministic'}`, "
            f"and takeover `{assist_state.get('takeover_available')}`."
        ),
        trace=trace,
    )


def _build_capability_manifest(
    *,
    controls: MissionControlControls,
    trace: MissionControlTrace,
    summary_payload: dict[str, Any],
    assist_bundle: dict[str, Any],
    interoperability_inventory: dict[str, Any],
    doctor_report: dict[str, Any],
) -> CapabilityManifest:
    assist_mode = dict(assist_bundle.get("assist_mode", {}))
    assist_state = dict(assist_bundle.get("assist_session_state", {}))
    guide = dict(assist_bundle.get("assistant_connection_guide", {}))
    benchmark = dict(summary_payload.get("benchmark", {}))
    pulse = dict(summary_payload.get("pulse", {}))
    profiles = dict(summary_payload.get("profiles", {}))
    runtime = dict(summary_payload.get("runtime", {}))
    data = dict(summary_payload.get("data", {}))
    host_summary = dict(interoperability_inventory.get("host_summary", {}))
    onboarding = _is_onboarding_state(summary_payload)
    semantic_backend_status = _clean_text(assist_mode.get("semantic_backend_status")) or "unknown"
    discoverable_hosts = ", ".join(host_summary.get("discoverable_now", [])) or "none"
    capabilities = [
        {
            "capability_id": "ask_bounded_questions",
            "name": "Ask Bounded Questions",
            "status": "enabled" if assist_mode.get("enabled") else "disabled",
            "detail": (
                "Relaytic can answer onboarding questions right now."
                if onboarding
                else "Relaytic can explain current state, route choice, benchmark posture, decision posture, and control posture."
            ),
            "status_reason": (
                "No run is loaded yet, so answers are about setup and capabilities rather than model-state details."
                if onboarding
                else "Run context is available, so Relaytic can answer stateful questions about the current lab run."
            ),
            "activation_hint": (
                f"Start a run with `{_example_run_command(run_dir=None)}` for run-specific explanations."
                if onboarding
                else f"Use `{_assist_turn_command(summary_payload, 'what can you do?')}` or `relaytic mission-control chat --run-dir {_display_run_dir(summary_payload)}`."
            ),
        },
        {
            "capability_id": "bounded_stage_navigation",
            "name": "Bounded Stage Navigation",
            "status": "enabled" if assist_state.get("available_stage_targets") else "needs_run_context",
            "detail": "Relaytic supports bounded stage reruns, not arbitrary checkpoint time travel.",
            "status_reason": (
                "Stage reruns only appear after a run exists, because Relaytic needs artifacts to know what can be replayed safely."
                if not assist_state.get("available_stage_targets")
                else "Relaytic can currently rerun named stages and refresh downstream artifacts from there."
            ),
            "activation_hint": (
                f"Create a run first with `{_example_run_command(run_dir=None)}`."
                if not assist_state.get("available_stage_targets")
                else f"Use `{_assist_turn_command(summary_payload, 'go back to planning')}`."
            ),
        },
        {
            "capability_id": "safe_takeover",
            "name": "Safe Takeover",
            "status": "enabled" if assist_state.get("takeover_available") else "needs_run_context",
            "detail": "Relaytic can continue from the next safe bounded stage when the operator stops or is unsure.",
            "status_reason": (
                "Takeover only becomes meaningful after Relaytic has a current run state to continue."
                if not assist_state.get("takeover_available")
                else "Relaytic can take over safely because there is enough run state to continue from a bounded point."
            ),
            "activation_hint": (
                f"Create a run first with `{_example_run_command(run_dir=None)}`."
                if not assist_state.get("takeover_available")
                else "Use `{}`.".format(_assist_turn_command(summary_payload, "i'm not sure, take over"))
            ),
        },
        {
            "capability_id": "skeptical_steering",
            "name": "Skeptical Steering",
            "status": "enabled",
            "detail": "Truth-bearing override requests are challenged instead of blindly obeyed.",
            "status_reason": "This protection stays on by default so Relaytic does not become a compliant shell.",
            "activation_hint": "You can still steer Relaytic, but it will explain accept, modify, defer, or reject decisions explicitly.",
        },
        {
            "capability_id": "imported_incumbent_challenge",
            "name": "Imported Incumbent Challenge",
            "status": (
                "needs_run_context"
                if onboarding
                else ("ready_for_incumbent" if not benchmark.get("incumbent_present") else "enabled")
            ),
            "detail": (
                f"Incumbent parity is `{benchmark.get('incumbent_parity_status') or 'not_configured'}` "
                f"with beat-target `{benchmark.get('beat_target_state') or 'not_configured'}`."
            ),
            "status_reason": (
                "Relaytic needs a run before it can compare itself to an incumbent under the same split and metric contract."
                if onboarding
                else (
                    "No incumbent is attached yet, but the run is ready for one."
                    if not benchmark.get("incumbent_present")
                    else "An incumbent is attached and Relaytic is already tracking parity or beat-target posture."
                )
            ),
            "activation_hint": (
                f"Start a run first with `{_example_run_command(run_dir=None)}`."
                if onboarding
                else f"Use `relaytic benchmark run --run-dir {_display_run_dir(summary_payload)} --data-path <data_path> --incumbent-path <path> --incumbent-kind model`."
            ),
        },
        {
            "capability_id": "host_connections",
            "name": "Host Connections",
            "status": "enabled" if host_summary else "unknown",
            "detail": (
                f"Discoverable now: `{discoverable_hosts}`; "
                f"needs activation: `{', '.join(host_summary.get('requires_activation', [])) or 'none'}`."
            ),
            "status_reason": "Host wrappers are separate from Relaytic's core truth layer, so some hosts are immediately discoverable while others need explicit activation or remote connector setup.",
            "activation_hint": "Run `relaytic interoperability show` to see exact host-specific next steps.",
        },
        {
            "capability_id": "local_semantic_assist",
            "name": "Local Semantic Assist",
            "status": semantic_backend_status,
            "detail": f"Recommended connection path is `{guide.get('recommended_path') or 'unknown'}`.",
            "status_reason": (
                "No local semantic backend is configured yet."
                if semantic_backend_status in {"unknown", "unavailable", "error"}
                else "A semantic backend is available for richer optional phrasing."
            ),
            "activation_hint": (
                "Run `python scripts/install_relaytic.py --profile full --launch-control-center` for the easiest setup, or use `relaytic setup-local-llm --provider llama_cpp --install-provider` if you want to provision the lightweight local semantic helper directly."
                if semantic_backend_status in {"unknown", "unavailable", "error"}
                else "Local semantic help is optional; Relaytic still works without it."
            ),
        },
        {
            "capability_id": "local_first_data_handling",
            "name": "Local-First Data Handling",
            "status": "enabled" if data.get("copy_enforced") else "needs_data",
            "detail": (
                f"Copy-only working data `{data.get('copy_enforced')}`; "
                f"rowless semantic default `{runtime.get('semantic_rowless_default')}`; "
                f"remote intelligence allowed `{profiles.get('remote_intelligence_allowed')}`."
            ),
            "status_reason": (
                "This becomes concrete after Relaytic stages a working copy for a run."
                if not data.get("copy_enforced")
                else "Relaytic is already operating on staged copies instead of the original source."
            ),
            "activation_hint": (
                f"Point Relaytic to data with `{_example_run_command(run_dir=None)}` or inspect a source with `relaytic source inspect --source-path <path>`."
                if not data.get("copy_enforced")
                else "Current data handling is already local-first and copy-only."
            ),
        },
        {
            "capability_id": "environment_health",
            "name": "Environment Health",
            "status": _clean_text(doctor_report.get("status")) or "unknown",
            "detail": "Doctor verifies the install profile and interoperable surfaces before launch.",
            "status_reason": "This is the fastest check for whether the local install is ready before you start a run or connect a host.",
            "activation_hint": f"Run `relaytic doctor --expected-profile {_clean_text(controls.default_expected_profile) or 'full'} --format json` any time you want to verify the local setup.",
        },
    ]
    return CapabilityManifest(
        schema_version=CAPABILITY_MANIFEST_SCHEMA_VERSION,
        generated_at=_utc_now(),
        controls=controls,
        status="ok",
        capability_count=len(capabilities),
        capabilities=capabilities,
        host_summary=host_summary,
        summary="Relaytic exposes what it can do locally, what needs activation, and where it will challenge the operator.",
        trace=trace,
    )


def _build_action_affordances(
    *,
    controls: MissionControlControls,
    trace: MissionControlTrace,
    summary_payload: dict[str, Any],
    assist_bundle: dict[str, Any],
    review_queue: ReviewQueueState,
) -> ActionAffordances:
    run_dir = _clean_text(summary_payload.get("run_dir")) or "<run_dir>"
    assist_state = dict(assist_bundle.get("assist_session_state", {}))
    next_step = dict(summary_payload.get("next_step", {}))
    benchmark = dict(summary_payload.get("benchmark", {}))
    pulse = dict(summary_payload.get("pulse", {}))
    trace_state = dict(summary_payload.get("trace", {}))
    evals = dict(summary_payload.get("evals", {}))
    if _is_onboarding_state(summary_payload):
        actions = [
            {
                "action_id": "start_with_data",
                "title": "Start With Data",
                "challenge_level": "low",
                "detail": "Point Relaytic to a dataset and tell it the goal so it can create the first governed run.",
                "command_hint": _example_run_command(run_dir=None),
            },
            {
                "action_id": "inspect_source",
                "title": "Inspect A Data Source",
                "challenge_level": "low",
                "detail": "Check how Relaytic will treat a file, stream snapshot, or local source before you run anything.",
                "command_hint": "relaytic source inspect --source-path <path>",
            },
            {
                "action_id": "read_human_handbook",
                "title": "Read The Human Handbook",
                "challenge_level": "low",
                "detail": "Open the more narrative operator guide when you want first-step help and onboarding context.",
                "command_hint": f"Get-Content {_human_handbook_path()}",
            },
            {
                "action_id": "read_agent_handbook",
                "title": "Read The Agent Handbook",
                "challenge_level": "low",
                "detail": "Open the terse agent guide when you want commands, artifact truth, and repo-control references fast.",
                "command_hint": f"Get-Content {_agent_handbook_path()}",
            },
            {
                "action_id": "open_terminal_chat",
                "title": "Talk In Terminal",
                "challenge_level": "low",
                "detail": "Open a live terminal conversation where you can paste a dataset path, describe the goal naturally, and let Relaytic guide the startup workflow.",
                "command_hint": "relaytic mission-control chat",
            },
            {
                "action_id": "paste_dataset_path",
                "title": "Paste A Dataset Path",
                "challenge_level": "low",
                "detail": "Paste a local dataset path directly into mission-control chat and Relaytic will confirm it, ask for the objective, and guide the next step.",
                "command_hint": "relaytic mission-control chat",
            },
            {
                "action_id": "analyze_data_first",
                "title": "Analyze Data First",
                "challenge_level": "low",
                "detail": "Ask Relaytic for a quick data analysis, top signals, or correlation review without starting the full governed modeling run yet.",
                "command_hint": "relaytic mission-control chat",
            },
            {
                "action_id": "start_governed_modeling",
                "title": "Start Governed Modeling",
                "challenge_level": "moderate",
                "detail": "Tell Relaytic to build a model, compare against an incumbent, or benchmark the dataset under the full governed run path.",
                "command_hint": _example_run_command(run_dir=None),
            },
            {
                "action_id": "run_guided_demo",
                "title": "Run The Guided Demo",
                "challenge_level": "low",
                "detail": "Follow the short demo path that takes you from install check to a first governed run and review.",
                "command_hint": f"Get-Content {_demo_guide_path()}",
            },
            {
                "action_id": "show_onboarding_state",
                "title": "Show Captured State",
                "challenge_level": "low",
                "detail": "Ask Relaytic what data path and objective it has already captured so you do not have to guess what it understood.",
                "command_hint": "relaytic mission-control chat",
            },
            {
                "action_id": "when_stuck",
                "title": "What To Do When Stuck",
                "challenge_level": "low",
                "detail": "Open the explicit stuck-recovery guide instead of guessing whether something is broken.",
                "command_hint": "relaytic mission-control chat",
            },
            {
                "action_id": "reset_onboarding",
                "title": "Reset Onboarding Capture",
                "challenge_level": "low",
                "detail": "Clear the captured startup state if you pasted the wrong thing or want to start over cleanly.",
                "command_hint": "relaytic mission-control chat",
            },
            {
                "action_id": "review_hosts",
                "title": "Review Host Connections",
                "challenge_level": "low",
                "detail": "See which hosts can already call Relaytic locally and which still need activation.",
                "command_hint": "relaytic interoperability show",
            },
        ]
        return ActionAffordances(
            schema_version=ACTION_AFFORDANCES_SCHEMA_VERSION,
            generated_at=_utc_now(),
            controls=controls,
            status="ok",
            action_count=len(actions),
            actions=actions,
            summary="Relaytic makes the setup and first-run path explicit so new users do not have to infer the workflow.",
            trace=trace,
        )
    actions: list[dict[str, Any]] = [
        {
            "action_id": "ask_question",
            "title": "Ask Why",
            "challenge_level": "low",
            "detail": "Ask Relaytic to explain the current state, route choice, benchmark status, or next step.",
            "command_hint": f"relaytic assist turn --run-dir {run_dir} --message \"why did you choose this route?\"",
        },
        {
            "action_id": "show_capabilities",
            "title": "Show Capabilities",
            "challenge_level": "low",
            "detail": "Ask Relaytic what it can do now, what it expects from you, and how to steer it safely.",
            "command_hint": f"relaytic assist turn --run-dir {run_dir} --message \"what can you do?\"",
        },
    ]
    available_stages = [str(item).strip() for item in assist_state.get("available_stage_targets", []) if str(item).strip()]
    if available_stages:
        suggested_stage = "benchmark" if "benchmark" in available_stages else available_stages[0]
        actions.append(
            {
                "action_id": "rerun_stage",
                "title": "Go Back To A Stage",
                "challenge_level": "low",
                "detail": "Rerun one bounded stage and refresh downstream artifacts from there.",
                "command_hint": f"relaytic assist turn --run-dir {run_dir} --message \"go back to {suggested_stage}\"",
            }
        )
    if assist_state.get("takeover_available"):
        actions.append(
            {
                "action_id": "take_over",
                "title": "Let Relaytic Continue",
                "challenge_level": "moderate",
                "detail": "Relaytic will pick the next safe bounded step and continue, but still challenge unsafe overrides.",
                "command_hint": f"relaytic assist turn --run-dir {run_dir} --message \"i'm not sure, take over\"",
            }
        )
    if review_queue.items:
        top_item = dict(review_queue.items[0])
        actions.append(
            {
                "action_id": "review_queue",
                "title": "Review The Top Queue Item",
                "challenge_level": "low",
                "detail": str(top_item.get("detail", "")).strip() or "Relaytic has a visible review item queued.",
                "command_hint": f"relaytic {str(top_item.get('recommended_action', 'show')).replace('_', ' ')}",
            }
        )
    if not benchmark.get("incumbent_present"):
        actions.append(
            {
                "action_id": "attach_incumbent",
                "title": "Attach An Incumbent",
                "challenge_level": "low",
                "detail": "Import a real incumbent model, ruleset, or prediction file so Relaytic can try to beat it honestly.",
                "command_hint": f"relaytic benchmark run --run-dir {run_dir} --data-path <data_path> --incumbent-path <path> --incumbent-kind model",
            }
        )
    if _clean_text(next_step.get("recommended_action")):
        actions.append(
            {
                "action_id": "inspect_next_action",
                "title": "Inspect The Next Action",
                "challenge_level": "low",
                "detail": str(next_step.get("rationale", "")).strip() or "Relaytic has a bounded next action ready.",
                "command_hint": f"relaytic show --run-dir {run_dir} --format json",
            }
        )
    if pulse:
        actions.append(
            {
                "action_id": "review_pulse",
                "title": "Review The Lab Pulse",
                "challenge_level": "low",
                "detail": "Inspect the latest pulse status, watchlist, innovation leads, and any bounded queued follow-up.",
                "command_hint": f"relaytic pulse show --run-dir {run_dir}",
            }
        )
    if trace_state:
        actions.append(
            {
                "action_id": "review_trace",
                "title": "Review Trace",
                "challenge_level": "low",
                "detail": "Inspect the canonical span log, competing claims, and the deterministic winning action.",
                "command_hint": f"relaytic trace show --run-dir {run_dir}",
            }
        )
    if evals:
        actions.append(
            {
                "action_id": "review_evals",
                "title": "Review Agent Evals",
                "challenge_level": "low",
                "detail": "Inspect protocol conformance, skeptical-control proof, and red-team findings.",
                "command_hint": f"relaytic evals show --run-dir {run_dir}",
            }
        )
    return ActionAffordances(
        schema_version=ACTION_AFFORDANCES_SCHEMA_VERSION,
        generated_at=_utc_now(),
        controls=controls,
        status="ok",
        action_count=len(actions),
        actions=actions[:8],
        summary="Relaytic makes the next safe actions explicit so humans and agents do not have to guess how to interact.",
        trace=trace,
    )


def _build_stage_navigator(
    *,
    controls: MissionControlControls,
    trace: MissionControlTrace,
    summary_payload: dict[str, Any],
    assist_bundle: dict[str, Any],
) -> StageNavigator:
    assist_state = dict(assist_bundle.get("assist_session_state", {}))
    current_stage = _clean_text(summary_payload.get("stage_completed")) or "onboarding"
    stages = [str(item).strip() for item in assist_state.get("available_stage_targets", []) if str(item).strip()]
    details = {
        "intake": "Rebuild intake interpretation and refresh all downstream reasoning.",
        "investigation": "Re-profile the dataset and refresh focus, planning, and later stages.",
        "memory": "Refresh analog retrieval and downstream route/challenger priors.",
        "planning": "Rebuild the plan and rerun downstream build/evidence/governors.",
        "evidence": "Rerun challenger, ablation, and audit without discarding earlier intake and planning.",
        "intelligence": "Refresh semantic debate, verifier output, and later governors.",
        "research": "Refresh redacted research retrieval and downstream autonomy/completion effects.",
        "benchmark": "Refresh reference or incumbent comparison and later follow-up logic.",
        "completion": "Recompute completion state from the current artifacts.",
        "lifecycle": "Recompute lifecycle posture from the current completion/evidence state.",
        "autonomy": "Rerun the bounded follow-up loop from the current governed state.",
    }
    available_stages = [
        {
            "stage": stage,
            "active": stage == current_stage,
            "reruns_downstream": True,
            "detail": details.get(stage, "Relaytic can rerun this bounded stage and refresh downstream artifacts."),
        }
        for stage in stages
    ]
    return StageNavigator(
        schema_version=STAGE_NAVIGATOR_SCHEMA_VERSION,
        generated_at=_utc_now(),
        controls=controls,
        status="ok",
        current_stage=current_stage,
        can_rerun_stage=bool(available_stages),
        can_jump_to_any_point=False,
        navigation_scope="bounded_stage_rerun",
        available_stages=available_stages,
        summary=(
            "Relaytic will expose bounded stage reruns after a run exists."
            if _is_onboarding_state(summary_payload)
            else "Relaytic currently supports bounded stage reruns rather than arbitrary checkpoint time travel."
        ),
        trace=trace,
    )


def _build_question_starters(
    *,
    controls: MissionControlControls,
    trace: MissionControlTrace,
    summary_payload: dict[str, Any],
    assist_bundle: dict[str, Any],
) -> QuestionStarters:
    assist_state = dict(assist_bundle.get("assist_session_state", {}))
    benchmark = dict(summary_payload.get("benchmark", {}))
    decision_lab = dict(summary_payload.get("decision_lab", {}))
    control = dict(summary_payload.get("control", {}))
    if _is_onboarding_state(summary_payload):
        questions = [
            {
                "category": "intro",
                "question": "what is relaytic?",
                "detail": "Explains what Relaytic is and what it is for.",
            },
            {
                "category": "start",
                "question": "how do i start?",
                "detail": "Explains the first steps and the fastest run command.",
            },
            {
                "category": "analysis",
                "question": "can you just analyze the data first?",
                "detail": "Explains the quick analysis-first path for top signals, correlations, and exploratory summaries without a full governed run.",
            },
            {
                "category": "analysis",
                "question": "give me the top 3 signals",
                "detail": "Routes to the direct analysis path when a lightweight exploratory answer is enough.",
            },
            {
                "category": "capture",
                "question": "what have you captured so far?",
                "detail": "Shows which dataset path or objective Relaytic thinks it already understood from the onboarding chat.",
            },
            {
                "category": "data",
                "question": "what data formats do you support?",
                "detail": "Explains supported snapshot and local source formats.",
            },
            {
                "category": "capabilities",
                "question": "why are some capabilities disabled?",
                "detail": "Explains which capabilities need a run, local backend, or host activation.",
            },
            {
                "category": "chat",
                "question": "what can you do?",
                "detail": "Explains current capabilities, limits, and safe steering options.",
            },
            {
                "category": "hosts",
                "question": "how do i use this with claude, codex, or openclaw?",
                "detail": "Explains local host integration paths and activation steps.",
            },
            {
                "category": "demo",
                "question": "show me a demo flow",
                "detail": "Explains the quickest recruiter-safe walkthrough from install check to first reviewed run.",
            },
            {
                "category": "modes",
                "question": "what do the modes mean?",
                "detail": "Explains mission control, terminal chat, assist, and host integration surfaces in plain language.",
            },
            {
                "category": "stuck",
                "question": "i'm stuck, what should i do?",
                "detail": "Explains how to recover when you do not know the next step.",
            },
            {
                "category": "handbook",
                "question": "where is the handbook?",
                "detail": "Points to the human and agent handbooks directly from onboarding.",
            },
            {
                "category": "agent_handbook",
                "question": "what should an agent read first?",
                "detail": "Points to the command-first agent guide and the most important repo contracts.",
            },
        ]
        return QuestionStarters(
            schema_version=QUESTION_STARTERS_SCHEMA_VERSION,
            generated_at=_utc_now(),
            controls=controls,
            status="ok",
            question_count=len(questions),
            starters=questions,
            summary="Relaytic exposes onboarding-first starter questions so the lab is understandable before any run exists.",
            trace=trace,
        )
    questions = [
        {
            "category": "explain",
            "question": "why did you choose this route?",
            "detail": "Explains the current route, metric, and next-step reasoning.",
        },
        {
            "category": "capabilities",
            "question": "what can you do?",
            "detail": "Explains current capabilities, limits, and safe steering options.",
        },
    ]
    if benchmark.get("incumbent_present"):
        questions.append(
            {
                "category": "benchmark",
                "question": "why did you or didn't you beat the incumbent?",
                "detail": "Explains incumbent parity, beat-target state, and the benchmark gap.",
            }
        )
    if decision_lab.get("review_required"):
        questions.append(
            {
                "category": "decision",
                "question": "why does the decision lab want review?",
                "detail": "Explains the selected strategy, next actor, and why Relaytic asked for review.",
            }
        )
    if control.get("decision"):
        questions.append(
            {
                "category": "control",
                "question": "why was my steering request challenged?",
                "detail": "Explains skeptical control, challenge level, and approved scope.",
            }
        )
    stages = [str(item).strip() for item in assist_state.get("available_stage_targets", []) if str(item).strip()]
    if stages:
        target = "research" if "research" in stages else stages[0]
        questions.append(
            {
                "category": "navigation",
                "question": f"go back to {target}",
                "detail": "Reruns one bounded stage and refreshes downstream artifacts from there.",
            }
        )
    if assist_state.get("takeover_available"):
        questions.append(
            {
                "category": "takeover",
                "question": "i'm not sure, take over",
                "detail": "Lets Relaytic continue from the next safe bounded step.",
            }
        )
    return QuestionStarters(
        schema_version=QUESTION_STARTERS_SCHEMA_VERSION,
        generated_at=_utc_now(),
        controls=controls,
        status="ok",
        question_count=len(questions),
        starters=questions[:8],
        summary="Relaytic exposes starter questions so users and external agents know how to interact without guessing the shell vocabulary.",
        trace=trace,
    )


def _build_control_center_layout(
    *,
    controls: MissionControlControls,
    trace: MissionControlTrace,
) -> ControlCenterLayout:
    panels = [
        {"panel_id": "hero", "title": "Run headline, current stage, and launch posture"},
        {"panel_id": "welcome", "title": "What Relaytic is and what it needs before a run exists"},
        {"panel_id": "first_steps", "title": "Fastest path from onboarding into the first governed run"},
        {"panel_id": "captured_onboarding_state", "title": "What Relaytic has already captured from the human and what it still needs next"},
        {"panel_id": "guided_demo", "title": "A recruiter-safe walkthrough from install check to first reviewed run"},
        {"panel_id": "modes_explained", "title": "What each product surface is for and when to use it"},
        {"panel_id": "stuck_help", "title": "Recovery guidance when the next step is unclear"},
        {"panel_id": "interaction_modes", "title": "Dashboard, terminal chat, workflow, and host integration paths"},
        {"panel_id": "handbooks", "title": "Role-specific human and agent guides surfaced directly from onboarding"},
        {"panel_id": "cards", "title": "Operator cards for model, budget, benchmark, decision, and control"},
        {"panel_id": "modes", "title": "Autonomy, intelligence, takeover, and skeptical-control posture"},
        {"panel_id": "capabilities", "title": "What Relaytic can do locally right now and what needs activation"},
        {"panel_id": "capability_reasons", "title": "Why a capability is unavailable and what activates it"},
        {"panel_id": "actions", "title": "What a human or external agent can do next without guessing"},
        {"panel_id": "stage_navigator", "title": "Bounded stage reruns with explicit scope and limitations"},
        {"panel_id": "questions", "title": "Starter questions that make the lab feel immediately explorable"},
        {"panel_id": "trace_evals", "title": "Canonical traces, competing claims, conformance checks, and security proof"},
        {"panel_id": "dojo", "title": "Guarded self-improvement, promotions, and rollback state"},
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
        summary="Relaytic exposes one thin mission-control layout that reuses current artifact truth while making modes, capabilities, actions, stage navigation, trace proof, eval results, questions, and dojo state explicit.",
        trace=trace,
    )


def _build_onboarding_status(
    *,
    controls: MissionControlControls,
    trace: MissionControlTrace,
    expected_profile: str,
    doctor_report: dict[str, Any],
    interoperability_inventory: dict[str, Any],
    summary_payload: dict[str, Any],
    run_dir: Path | None,
    root_dir: Path,
) -> OnboardingStatus:
    doctor_status = str(doctor_report.get("status", "")).strip() or "unknown"
    host_summary = dict(interoperability_inventory.get("host_summary", {}))
    install_verified = doctor_status in {"ok", "warn"}
    launch_ready = install_verified and bool(doctor_report.get("package", {}).get("installed"))
    onboarding = _is_onboarding_state(summary_payload)
    live_chat_command = (
        f"relaytic mission-control chat --run-dir {run_dir}"
        if run_dir is not None
        else "relaytic mission-control chat"
    )
    interaction_modes = [
        {
            "mode_id": "control_center",
            "name": "Mission Control",
            "kind": "dashboard",
            "detail": "Use this to inspect current state, next steps, contracts, benchmark posture, and launch status.",
            "command": (f"relaytic mission-control launch --run-dir {run_dir}" if run_dir is not None else f"relaytic mission-control launch --output-dir {root_dir}"),
        },
        {
            "mode_id": "terminal_chat",
            "name": "Mission Control Chat",
            "kind": "interactive_terminal",
            "detail": "Use this when you want to type natural-language questions in the terminal and get guided help, demo flow, or stuck recovery.",
            "command": live_chat_command,
        },
        {
            "mode_id": "one_shot_run",
            "name": "Create A Run",
            "kind": "workflow",
            "detail": "Use this when you have a dataset and want Relaytic to build and review a run end to end.",
            "command": _example_run_command(run_dir=None),
        },
        {
            "mode_id": "human_handbook",
            "name": "Human Handbook",
            "kind": "guide",
            "detail": "Use this when you want the narrative operator guide, first-step workflow, and mission-control explanation.",
            "command": _human_handbook_path(),
        },
        {
            "mode_id": "agent_handbook",
            "name": "Agent Handbook",
            "kind": "guide",
            "detail": "Use this when you want the command-first agent workflow, artifact contract, and repo-control references.",
            "command": _agent_handbook_path(),
        },
        {
            "mode_id": "host_mode",
            "name": "Agent Host",
            "kind": "integration",
            "detail": "Use this after local setup if you want Claude, Codex, OpenClaw, or another host to call Relaytic.",
            "command": "relaytic interoperability show",
        },
        {
            "mode_id": "guided_demo",
            "name": "Guided Demo",
            "kind": "workflow",
            "detail": "Use this when you want one short recruiter-safe path from install check to first reviewed run.",
            "command": _demo_guide_path(),
        },
    ]
    current_requirements = (
        [
            "A dataset path or local source path.",
            "A short goal in plain language, for example whether you want a quick analysis first or a governed model/benchmark run.",
        ]
        if onboarding
        else [
            "You already have a run context.",
            "You can now inspect, question, rerun bounded stages, attach an incumbent, or let Relaytic continue safely.",
        ]
    )
    first_steps = (
        [
            f"Run `python scripts/install_relaytic.py --profile {expected_profile} --launch-control-center` for the easiest first launch. On the full profile, Relaytic also tries to provision a lightweight local onboarding model for human-friendly chat.",
            "Point Relaytic to data with `relaytic run --run-dir artifacts\\demo --data-path <data.csv> --text \"Describe the goal here.\"` if you already know you want the full governed modeling path.",
            "If you only want a quick analysis first, use mission-control chat and say things like `analyze this data`, `give me the top 3 signals`, or `run a correlation analysis` after you paste the dataset path.",
            "If you want to inspect a source first, run `relaytic source inspect --source-path <path>`.",
            f"Read `{_human_handbook_path()}` for the narrative human guide or `{_agent_handbook_path()}` for the terse agent guide.",
            "Use `relaytic mission-control chat` for terminal questions, direct path pasting, and guided startup or `relaytic mission-control launch` for the browser control center.",
        ]
        if onboarding
        else [
            f"Use `{_assist_turn_command(summary_payload, 'what can you do?')}` for an explanation of the current run posture.",
            f"Use `{_assist_turn_command(summary_payload, 'go back to planning')}` if you want to rerun a bounded stage.",
            "Use `{}` if you want Relaytic to continue safely.".format(
                _assist_turn_command(summary_payload, "i'm not sure, take over")
            ),
        ]
    )
    guided_demo_flow = (
        [
            f"Run `relaytic doctor --expected-profile {expected_profile} --format json` first so you know the local environment is healthy.",
            "If you installed the full profile, let Relaytic keep the lightweight local onboarding helper enabled. It is there to interpret messy first-turn human input, not to replace deterministic run control.",
            "Choose one real local dataset or export one table to a CSV, TSV, Excel, Parquet, Feather, JSON, JSONL, or NDJSON file.",
            "Paste the dataset path directly into mission-control chat, then either ask for a quick analysis-first pass or create the first governed run explicitly with "
            f"`{_example_run_command(run_dir=None)}`.",
            "Open mission control on that run and read the cards, capabilities, next action, and review queue before touching lower-level commands.",
            f"Ask `what can you do?` in `{live_chat_command}` or through `relaytic assist turn --run-dir <run_dir> --message \"what can you do?\"` once the run exists.",
            "If you already have a baseline model, attach it as an incumbent and let Relaytic explain whether it can beat it under the same contract.",
        ]
        if onboarding
        else [
            "Inspect the current stage, next actor, quality posture, and decision-lab state in mission control.",
            "Ask Relaytic why it chose the current route and what it can do now.",
            "Review benchmark or incumbent posture before changing course.",
            "Use one bounded stage rerun if you want a controlled replay.",
            "Use safe takeover only when you want Relaytic to continue from the next bounded step.",
        ]
    )
    mode_explanations = [
        {
            "name": "Mission Control",
            "detail": "The dashboard view. Use it when you want the big picture, current status, next action, capabilities, and queue state.",
        },
        {
            "name": "Mission Control Chat",
            "detail": "The onboarding and navigation chat. Use it for plain-language questions, demo flow help, handbook discovery, and stuck recovery.",
        },
        {
            "name": "Assist",
            "detail": "The run-specific conversational surface. Use it after a run exists when you want explanations, bounded stage reruns, or safe takeover.",
        },
        {
            "name": "Agent Host",
            "detail": "The integration layer for Claude, Codex, OpenClaw, and MCP-style clients. Use it when Relaytic should be driven from another tool.",
        },
    ]
    stuck_guide = (
        [
            "If you are not sure what to do first, run `relaytic doctor --expected-profile full --format json` and then ask `how do i start?` in mission-control chat.",
            "If capabilities look disabled, read the status reason and activation hint in mission control before assuming something is broken.",
            f"If you need a longer explanation, open `{_human_handbook_path()}` or `{_agent_handbook_path()}` depending on who is operating Relaytic.",
            "If you do not have a dataset yet, start with any small local table export. Relaytic needs data plus a goal before deeper behavior becomes meaningful.",
            "If a host integration is confusing, run `relaytic interoperability show` to see what is already discoverable versus what still needs activation.",
        ]
        if onboarding
        else [
            "If you are not sure why Relaytic changed course, ask why in assist before rerunning anything.",
            "If you want to change direction, prefer one bounded stage rerun instead of trying to rebuild the whole run manually.",
            "If you do not know whether to step in or let Relaytic continue, inspect the next action and decision-lab rationale first.",
            "If a capability is blocked, read the activation hint in mission control instead of guessing whether the run is unhealthy.",
            "If you are fully stuck, use safe takeover only after Relaytic has explained the next bounded step.",
        ]
    )
    commands = [
        f"python scripts/install_relaytic.py --profile {expected_profile} --launch-control-center",
        f"relaytic doctor --expected-profile {expected_profile} --format json",
        (f"relaytic mission-control launch --run-dir {run_dir}" if run_dir is not None else f"relaytic mission-control launch --output-dir {root_dir}"),
        live_chat_command,
        f"Get-Content {_demo_guide_path()}",
        (f"relaytic assist show --run-dir {run_dir}" if run_dir is not None else "relaytic assist show --run-dir <run_dir>"),
        (f"relaytic assist turn --run-dir {run_dir} --message \"what can you do?\"" if run_dir is not None else "relaytic assist turn --run-dir <run_dir> --message \"what can you do?\""),
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
        what_relaytic_is="Relaytic is a local-first structured-data research lab. It needs data plus a goal, then it can either run a quick analysis-first pass or build, challenge, judge, and explain a governed run. The full install can also provision a lightweight local onboarding helper so first-contact chat is more forgiving for humans.",
        needs_data=onboarding,
        current_requirements=current_requirements,
        first_steps=first_steps,
        guided_demo_flow=guided_demo_flow,
        mode_explanations=mode_explanations,
        stuck_guide=stuck_guide,
        interaction_modes=interaction_modes,
        live_chat_ready=True,
        live_chat_command=live_chat_command,
        host_summary=host_summary,
        recommended_commands=commands,
        summary=(
            "Relaytic is in onboarding mode and needs data plus a goal before deeper run capabilities activate."
            if onboarding
            else "Relaytic has a run context, so mission control, assist, and bounded stage reruns are now meaningful."
        ),
        trace=trace,
    )


def _build_onboarding_chat_session_state(
    *,
    controls: MissionControlControls,
    trace: MissionControlTrace,
    root_dir: Path,
    run_dir: Path | None,
    policy: dict[str, Any],
) -> OnboardingChatSessionState:
    suggested_run_dir = _suggested_onboarding_run_dir_from_policy(policy)
    if run_dir is not None:
        current_phase = "run_context"
        summary = "Relaytic already has a run context, so onboarding chat state is no longer collecting startup inputs."
        return OnboardingChatSessionState(
            schema_version=ONBOARDING_CHAT_SESSION_STATE_SCHEMA_VERSION,
            generated_at=_utc_now(),
            controls=controls,
            status="inactive",
            current_phase=current_phase,
            detected_data_path=None,
            data_path_exists=None,
            detected_objective=None,
            objective_family=None,
            incumbent_path=None,
            incumbent_path_exists=None,
            suggested_run_dir=str(run_dir),
            ready_to_start_run=False,
            created_run_dir=str(run_dir),
            last_analysis_report_path=None,
            last_analysis_summary=None,
            next_expected_input=None,
            last_user_message=None,
            last_system_question=None,
            semantic_backend_status="run_context",
            semantic_model=None,
            llm_used_last_turn=False,
            turn_count=0,
            notes=["Mission-control onboarding chat switches to run-specific assist behavior once a run exists."],
            summary=summary,
            trace=trace,
        )

    existing = _read_onboarding_chat_session_payload(root_dir)
    if not existing:
        return OnboardingChatSessionState(
            schema_version=ONBOARDING_CHAT_SESSION_STATE_SCHEMA_VERSION,
            generated_at=_utc_now(),
            controls=controls,
            status="ready",
            current_phase="need_data",
            detected_data_path=None,
            data_path_exists=None,
            detected_objective=None,
            objective_family=None,
            incumbent_path=None,
            incumbent_path_exists=None,
            suggested_run_dir=suggested_run_dir,
            ready_to_start_run=False,
            created_run_dir=None,
            last_analysis_report_path=None,
            last_analysis_summary=None,
            next_expected_input="dataset path",
            last_user_message=None,
            last_system_question="Send a dataset path and tell Relaytic whether you want a quick analysis first or a governed model.",
            semantic_backend_status="not_checked",
            semantic_model=None,
            llm_used_last_turn=False,
            turn_count=0,
            notes=[
                "Adaptive onboarding is waiting for a dataset path or a plain-language objective.",
                "Relaytic can branch between direct analysis-first work and the full governed modeling flow once it understands the intent.",
                "Relaytic will confirm before it creates the first run.",
            ],
            summary="Relaytic is waiting for the first useful human input: a dataset path, an objective, or both.",
            trace=trace,
        )

    existing_suggested_run_dir = _clean_text(existing.get("suggested_run_dir"))
    if existing_suggested_run_dir in {None, "artifacts/demo", r"artifacts\demo"}:
        existing["suggested_run_dir"] = suggested_run_dir

    return OnboardingChatSessionState(
        schema_version=str(existing.get("schema_version") or ONBOARDING_CHAT_SESSION_STATE_SCHEMA_VERSION),
        generated_at=str(existing.get("generated_at") or _utc_now()),
        controls=controls,
        status=str(existing.get("status") or "ready"),
        current_phase=str(existing.get("current_phase") or "need_data"),
        detected_data_path=_clean_text(existing.get("detected_data_path")),
        data_path_exists=_maybe_bool(existing.get("data_path_exists")),
        detected_objective=_clean_text(existing.get("detected_objective")),
        objective_family=_clean_text(existing.get("objective_family")),
        incumbent_path=_clean_text(existing.get("incumbent_path")),
        incumbent_path_exists=_maybe_bool(existing.get("incumbent_path_exists")),
        suggested_run_dir=_clean_text(existing.get("suggested_run_dir")) or "artifacts/demo",
        ready_to_start_run=bool(existing.get("ready_to_start_run")),
        created_run_dir=_clean_text(existing.get("created_run_dir")),
        last_analysis_report_path=_clean_text(existing.get("last_analysis_report_path")),
        last_analysis_summary=_clean_text(existing.get("last_analysis_summary")),
        next_expected_input=_clean_text(existing.get("next_expected_input")),
        last_user_message=_clean_text(existing.get("last_user_message")),
        last_system_question=_clean_text(existing.get("last_system_question")),
        semantic_backend_status=_clean_text(existing.get("semantic_backend_status")) or "unknown",
        semantic_model=_clean_text(existing.get("semantic_model")),
        llm_used_last_turn=bool(existing.get("llm_used_last_turn")),
        turn_count=max(0, int(existing.get("turn_count", 0) or 0)),
        notes=[str(item).strip() for item in existing.get("notes", []) if str(item).strip()],
        summary=str(existing.get("summary") or "Relaytic is tracking the onboarding conversation state."),
        trace=trace,
    )


def _suggested_onboarding_run_dir_from_policy(policy: dict[str, Any]) -> str:
    communication_cfg = dict(policy.get("communication", {}))
    configured = _clean_text(communication_cfg.get("adaptive_onboarding_default_run_dir"))
    return str(Path(configured).expanduser()) if configured else str(Path("artifacts") / "demo")


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
        default_panels=["cards", "capabilities", "actions", "review_queue", "onboarding"],
        auto_open_browser=controls.auto_open_browser,
        summary="Relaytic defaults to one comfortable local mission-control layout with explicit modes, capabilities, actions, and stage navigation.",
        trace=trace,
    )


def _materialize_mission_control_assist_bundle(
    *,
    run_dir: Path | None,
    policy: dict[str, Any],
    summary_payload: dict[str, Any],
    interoperability_inventory: dict[str, Any],
) -> dict[str, Any]:
    existing = read_assist_bundle(run_dir) if run_dir is not None else {}
    session_state = dict(existing.get("assist_session_state", {}))
    if session_state.get("available_stage_targets") and session_state.get("available_actions"):
        return existing
    backend_discovery_payload: dict[str, Any]
    try:
        backend_discovery = discover_backend(
            controls=build_intelligence_controls_from_policy(policy),
            config_path=None,
        )
        backend_discovery_payload = backend_discovery.to_dict()
    except Exception as exc:
        backend_discovery_payload = {
            "status": "error",
            "notes": [str(exc)],
        }
    bundle = build_assist_bundle(
        policy=policy,
        run_summary=summary_payload,
        backend_discovery=backend_discovery_payload,
        interoperability_inventory=interoperability_inventory,
        last_user_intent=_clean_text(session_state.get("last_user_intent")),
        last_requested_stage=_clean_text(session_state.get("last_requested_stage")),
        last_action_kind=_clean_text(session_state.get("last_action_kind")),
        turn_count=int(session_state.get("turn_count", 0) or 0),
    )
    if run_dir is not None:
        write_assist_bundle(run_dir, bundle=bundle)
    return bundle.to_dict()


def _mission_control_summary(*, summary_payload: dict[str, Any], doctor_report: dict[str, Any]) -> str:
    if summary_payload:
        return f"Relaytic mission control is tracking `{summary_payload.get('stage_completed') or 'unknown'}` with next action `{dict(summary_payload.get('next_step', {})).get('recommended_action') or 'none'}`."
    return f"Relaytic mission control is in onboarding mode with doctor status `{doctor_report.get('status', 'unknown')}`."


def _normalize_expected_profile(value: str | None, *, controls: MissionControlControls) -> str:
    normalized = str(value or controls.default_expected_profile).strip().lower() or controls.default_expected_profile
    return normalized if normalized in {"core", "full"} else controls.default_expected_profile


def _is_onboarding_state(summary_payload: dict[str, Any]) -> bool:
    if not summary_payload:
        return True
    stage = _clean_text(summary_payload.get("stage_completed")) or _clean_text(dict(summary_payload.get("runtime", {})).get("current_stage"))
    if stage in {None, "onboarding", "foundation"}:
        decision = dict(summary_payload.get("decision", {}))
        data = dict(summary_payload.get("data", {}))
        if not decision and not data:
            return True
    if not _clean_text(summary_payload.get("run_dir")):
        decision = dict(summary_payload.get("decision", {}))
        next_step = dict(summary_payload.get("next_step", {}))
        if not decision and not next_step:
            return True
    return False


def _example_run_command(run_dir: str | None) -> str:
    target_run_dir = _clean_text(run_dir) or r"artifacts\demo"
    return f'relaytic run --run-dir {target_run_dir} --data-path <data.csv> --text "Describe the goal here."'


def _display_run_dir(summary_payload: dict[str, Any]) -> str:
    return _clean_text(summary_payload.get("run_dir")) or "<run_dir>"


def _assist_turn_command(summary_payload: dict[str, Any], message: str) -> str:
    run_dir = _clean_text(summary_payload.get("run_dir"))
    escaped = message.replace('"', '\\"')
    if run_dir:
        return f'relaytic assist turn --run-dir {run_dir} --message "{escaped}"'
    return "relaytic mission-control chat"


def _human_handbook_path() -> str:
    return "docs/handbooks/relaytic_user_handbook.md"


def _agent_handbook_path() -> str:
    return "docs/handbooks/relaytic_agent_handbook.md"


def _demo_guide_path() -> str:
    return "docs/handbooks/relaytic_demo_walkthrough.md"


def _clean_text(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text or text.lower() in {"none", "null"}:
        return None
    return text


def _maybe_bool(value: Any) -> bool | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    text = str(value).strip().lower()
    if text in {"true", "1", "yes", "on"}:
        return True
    if text in {"false", "0", "no", "off"}:
        return False
    return None


def _read_onboarding_chat_session_payload(root_dir: Path) -> dict[str, Any]:
    path = root_dir / "onboarding_chat_session_state.json"
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return payload if isinstance(payload, dict) else {}


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
