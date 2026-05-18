"""Slice 15V-A no-lost guidance and external context-pack synthesis."""

from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timezone
import json
from pathlib import Path
import re
from typing import Any

from relaytic.core.config import load_config
from relaytic.runs.summary import build_run_summary, read_run_summary

from .storage import default_guide_state_dir, write_external_context_pack, write_guide_bundle


GUIDE_STATE_SCHEMA_VERSION = "relaytic.guide_state.v1"
GUIDE_ACTION_MENU_SCHEMA_VERSION = "relaytic.guide_action_menu.v1"
GUIDE_ARTIFACT_SHORTLIST_SCHEMA_VERSION = "relaytic.guide_artifact_shortlist.v1"
GUIDE_QUESTION_STARTERS_SCHEMA_VERSION = "relaytic.guide_question_starters.v1"
GUIDE_LOCAL_LLM_SUMMARY_SCHEMA_VERSION = "relaytic.guide_local_llm_summary.v1"
EXTERNAL_LLM_CONTEXT_PACK_SCHEMA_VERSION = "relaytic.external_llm_context_pack.v1"
EXTERNAL_LLM_ARTIFACT_INDEX_SCHEMA_VERSION = "relaytic.external_llm_artifact_index.v1"
EXTERNAL_LLM_REDACTION_REPORT_SCHEMA_VERSION = "relaytic.external_llm_redaction_report.v1"


def run_guide_review(
    *,
    run_dir: str | Path | None = None,
    output_dir: str | Path | None = None,
    config_path: str | None = None,
    message: str | None = None,
    use_local_llm: bool = False,
) -> dict[str, Any]:
    """Build, persist, and render the no-lost guide surface."""

    context = _load_context(run_dir=run_dir, output_dir=output_dir)
    bundle = build_guide_bundle(
        context=context,
        config_path=config_path,
        message=message,
        use_local_llm=use_local_llm,
    )
    written = write_guide_bundle(context["state_dir"], bundle=bundle)
    _attach_existing_context_paths(bundle=bundle, state_dir=Path(context["state_dir"]))
    human_output = render_guide_markdown(bundle, message=message)
    return {
        "surface_payload": {
            "status": "ok",
            "run_dir": str(context["run_dir"]) if context.get("run_dir") is not None else None,
            "state_dir": str(context["state_dir"]),
            "paths": {key: str(value) for key, value in written.items()},
            "guide": _guide_surface_summary(bundle),
            "bundle": bundle,
        },
        "human_output": human_output,
    }


def export_external_context_pack(
    *,
    run_dir: str | Path,
    audience: str = "external-llm",
    config_path: str | None = None,
    use_local_llm: bool = False,
) -> dict[str, Any]:
    """Write a redacted context pack that can be given to an external LLM or agent."""

    context = _load_context(run_dir=run_dir, output_dir=None)
    bundle = build_guide_bundle(
        context=context,
        config_path=config_path,
        message="export context for an external llm",
        use_local_llm=use_local_llm,
    )
    guide_paths = write_guide_bundle(context["state_dir"], bundle=bundle)
    context_pack, artifact_index, redaction_report = build_external_context_pack(
        bundle=bundle,
        context=context,
        audience=audience,
    )
    context_markdown = render_external_context_markdown(context_pack)
    export_paths = write_external_context_pack(
        context["state_dir"],
        context_pack=context_pack,
        context_markdown=context_markdown,
        artifact_index=artifact_index,
        redaction_report=redaction_report,
    )
    bundle["guide_state"]["external_context_pack"] = {
        "status": "ready",
        "audience": audience,
        "context_pack_path": str(export_paths["external_llm_context_pack"]),
        "context_pack_markdown_path": str(export_paths["external_llm_context_pack_md"]),
        "artifact_index_path": str(export_paths["external_llm_artifact_index"]),
        "redaction_report_path": str(export_paths["external_llm_redaction_report"]),
    }
    write_guide_bundle(context["state_dir"], bundle=bundle)
    human_output = render_external_context_markdown(context_pack)
    return {
        "surface_payload": {
            "status": "ok",
            "run_dir": str(context["run_dir"]) if context.get("run_dir") is not None else None,
            "state_dir": str(context["state_dir"]),
            "audience": audience,
            "paths": {key: str(value) for key, value in {**guide_paths, **export_paths}.items()},
            "guide": _guide_surface_summary(bundle),
            "external_context_pack": context_pack,
            "external_llm_artifact_index": artifact_index,
            "external_llm_redaction_report": redaction_report,
            "bundle": bundle,
        },
        "human_output": human_output,
    }


def build_guide_bundle(
    *,
    context: dict[str, Any],
    config_path: str | None,
    message: str | None,
    use_local_llm: bool,
) -> dict[str, Any]:
    generated_at = _utc_now()
    summary = dict(context.get("run_summary", {}))
    state = _infer_current_state(context=context)
    missing = _missing_evidence(context=context)
    claim_boundaries = _claim_boundaries(summary=summary, context=context)
    blocking_items = _blocking_items(context=context, missing=missing, claim_boundaries=claim_boundaries)
    recommended = _recommended_next_action(context=context, state=state, missing=missing, blocking_items=blocking_items)
    action_menu = _action_menu(context=context, state=state, recommended_action=recommended)
    artifact_shortlist = _artifact_shortlist(context=context)
    question_starters = _question_starters(context=context, state=state)
    answer = _answer_message(
        message=message,
        state=state,
        recommended_action=recommended,
        action_menu=action_menu,
        claim_boundaries=claim_boundaries,
        artifact_shortlist=artifact_shortlist,
    )
    local_llm_summary = _local_llm_summary(
        config_path=config_path,
        use_local_llm=use_local_llm,
        state=state,
        recommended_action=recommended,
        claim_boundaries=claim_boundaries,
        answer=answer,
    )
    if _clean_text(local_llm_summary.get("friendly_answer")):
        answer = str(local_llm_summary["friendly_answer"]).strip()
    trace = _trace(local_llm_summary=local_llm_summary)
    guide_state = {
        "schema_version": GUIDE_STATE_SCHEMA_VERSION,
        "generated_at": generated_at,
        "status": "ok",
        "current_state": state["current_state"],
        "state_confidence": state["state_confidence"],
        "headline": state["headline"],
        "best_next_move": recommended["label"],
        "recommended_next_action": recommended,
        "blocking_items": blocking_items,
        "missing_evidence": missing,
        "claim_boundaries": claim_boundaries,
        "state_sources": state["state_sources"],
        "answer": answer,
        "question": _clean_text(message),
        "run_dir": _safe_display_path(context.get("run_dir"), base=context.get("state_dir")),
        "state_dir": _safe_display_path(context.get("state_dir"), base=context.get("state_dir")),
        "external_context_pack": _existing_context_pack_paths(Path(context["state_dir"])),
        "summary": _state_summary(state=state, recommended=recommended, blocking_items=blocking_items),
        "trace": trace,
    }
    return {
        "guide_state": guide_state,
        "guide_action_menu": {
            "schema_version": GUIDE_ACTION_MENU_SCHEMA_VERSION,
            "generated_at": generated_at,
            "status": "ok",
            "recommended_action_id": recommended["action_id"],
            "actions": action_menu,
            "safe_command_count": len([item for item in action_menu if item.get("command")]),
            "summary": "Relaytic prepared a safe action menu from registered CLI affordances.",
            "trace": trace,
        },
        "guide_artifact_shortlist": {
            "schema_version": GUIDE_ARTIFACT_SHORTLIST_SCHEMA_VERSION,
            "generated_at": generated_at,
            "status": "ok",
            "artifacts": artifact_shortlist,
            "summary": "Relaytic selected the smallest useful artifact set for humans and external agents.",
            "trace": trace,
        },
        "guide_question_starters": {
            "schema_version": GUIDE_QUESTION_STARTERS_SCHEMA_VERSION,
            "generated_at": generated_at,
            "status": "ok",
            "questions": question_starters,
            "summary": "Relaytic prepared starter questions so users and agents do not need to know artifact names.",
            "trace": trace,
        },
        "guide_local_llm_summary": local_llm_summary,
    }


def build_external_context_pack(
    *,
    bundle: dict[str, Any],
    context: dict[str, Any],
    audience: str,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    summary = dict(context.get("run_summary", {}))
    redactions: list[dict[str, Any]] = []
    data = dict(summary.get("data", {}))
    request = dict(summary.get("request", {}))
    safe_data = {
        "row_count": data.get("row_count"),
        "column_count": data.get("column_count"),
        "source_format": data.get("source_format"),
        "source_type": data.get("source_type"),
        "data_mode": data.get("data_mode"),
        "timestamp_column": data.get("timestamp_column"),
        "copy_enforced": data.get("copy_enforced"),
        "immutable_working_copies": data.get("immutable_working_copies"),
    }
    safe_request = {
        "actor_type": request.get("actor_type"),
        "channel": request.get("channel"),
        "text_preview": request.get("text_preview"),
    }
    artifact_index = _external_artifact_index(bundle=bundle, context=context)
    pack = {
        "schema_version": EXTERNAL_LLM_CONTEXT_PACK_SCHEMA_VERSION,
        "generated_at": _utc_now(),
        "status": "ready",
        "audience": audience,
        "local_only": True,
        "raw_rows_included": False,
        "run": {
            "run_id": summary.get("run_id"),
            "status": summary.get("status"),
            "stage_completed": summary.get("stage_completed"),
            "headline": summary.get("headline"),
        },
        "guide": {
            "current_state": bundle["guide_state"].get("current_state"),
            "state_confidence": bundle["guide_state"].get("state_confidence"),
            "best_next_move": bundle["guide_state"].get("best_next_move"),
            "recommended_next_action": bundle["guide_state"].get("recommended_next_action"),
            "blocking_items": bundle["guide_state"].get("blocking_items", []),
            "missing_evidence": bundle["guide_state"].get("missing_evidence", []),
            "claim_boundaries": bundle["guide_state"].get("claim_boundaries", {}),
        },
        "objective": {
            "intent": _safe_subset(summary.get("intent"), keys=["objective", "domain_archetype", "problem_statement", "autonomy_mode"]),
            "request": safe_request,
            "decision": _safe_subset(
                summary.get("decision"),
                keys=["task_type", "target_column", "selected_model_family", "primary_metric", "split_strategy"],
            ),
            "result_contract": _safe_subset(
                summary.get("result_contract"),
                keys=["status", "overall_confidence", "overall_strength", "recommended_direction", "review_need", "unresolved_count"],
            ),
        },
        "data_summary": safe_data,
        "available_actions": bundle["guide_action_menu"].get("actions", []),
        "artifact_index": artifact_index["artifacts"],
        "starter_questions": bundle["guide_question_starters"].get("questions", []),
        "external_llm_prompt": _external_prompt(bundle),
    }
    redaction_report = {
        "schema_version": EXTERNAL_LLM_REDACTION_REPORT_SCHEMA_VERSION,
        "generated_at": pack["generated_at"],
        "status": "ok",
        "raw_rows_included": False,
        "redactions": redactions,
        "blocked_fields": [
            "raw_rows",
            "row_samples",
            "absolute_source_paths",
            "tokens",
            "api_keys",
            "environment_variables",
        ],
        "summary": "Relaytic exported artifact-derived context only. Raw rows and private machine paths are excluded by default.",
    }
    pack = _sanitize_for_external_pack(pack, redactions=redactions)
    artifact_index = _sanitize_for_external_pack(artifact_index, redactions=redactions)
    redaction_report["redaction_count"] = len(redactions)
    return pack, artifact_index, redaction_report


def render_guide_markdown(bundle: dict[str, Any], *, message: str | None = None) -> str:
    state = dict(bundle.get("guide_state", {}))
    actions = list(dict(bundle.get("guide_action_menu", {})).get("actions", []))
    artifacts = list(dict(bundle.get("guide_artifact_shortlist", {})).get("artifacts", []))
    questions = list(dict(bundle.get("guide_question_starters", {})).get("questions", []))
    local_llm = dict(bundle.get("guide_local_llm_summary", {}))
    lines = [
        "# Relaytic Guide",
        "",
        f"- Current state: `{state.get('current_state') or 'unknown'}`",
        f"- Confidence: `{state.get('state_confidence') or 'unknown'}`",
        f"- Best next move: `{state.get('best_next_move') or 'review_state'}`",
        f"- Local LLM: `{local_llm.get('status') or 'not_requested'}`",
        "",
        str(state.get("answer") or state.get("summary") or "Relaytic prepared guidance from local artifacts.").strip(),
        "",
        "## Do Now",
    ]
    for item in actions[:5]:
        if not isinstance(item, dict):
            continue
        command = _clean_text(item.get("command"))
        reason = _clean_text(item.get("reason")) or _clean_text(item.get("description"))
        if command:
            lines.append(f"- {item.get('label') or item.get('action_id')}: `{command}`")
        else:
            lines.append(f"- {item.get('label') or item.get('action_id')}: {reason or 'available from current guide state'}")
    lines.extend(["", "## Useful Files"])
    visible_artifacts = [item for item in artifacts if isinstance(item, dict) and item.get("exists")]
    if visible_artifacts:
        for item in visible_artifacts[:7]:
            lines.append(f"- `{item.get('path')}` - {item.get('purpose') or 'useful context'}")
    else:
        lines.append("- No run artifacts exist yet. Start with mission-control chat or a governed run.")
    lines.extend(["", "## Ask Next"])
    for question in questions[:4]:
        lines.append(f"- {question}")
    if message:
        lines.extend(["", f"Question handled: `{message}`"])
    return "\n".join(lines).rstrip() + "\n"


def render_external_context_markdown(context_pack: dict[str, Any]) -> str:
    guide = dict(context_pack.get("guide", {}))
    run = dict(context_pack.get("run", {}))
    actions = list(context_pack.get("available_actions", []))
    artifacts = list(context_pack.get("artifact_index", []))
    prompt = str(context_pack.get("external_llm_prompt") or "").strip()
    lines = [
        "# Relaytic External LLM Context Pack",
        "",
        f"- Status: `{context_pack.get('status') or 'unknown'}`",
        f"- Run: `{run.get('run_id') or 'none'}`",
        f"- Current state: `{guide.get('current_state') or 'unknown'}`",
        f"- Best next move: `{guide.get('best_next_move') or 'review_state'}`",
        f"- Raw rows included: `{context_pack.get('raw_rows_included')}`",
        "",
        "## Prompt",
        "",
        prompt,
        "",
        "## Safe Commands",
    ]
    for item in actions[:6]:
        if isinstance(item, dict) and item.get("command"):
            lines.append(f"- `{item.get('command')}`")
    lines.extend(["", "## Artifact Index"])
    for item in artifacts[:8]:
        if isinstance(item, dict):
            lines.append(f"- `{item.get('path')}` - {item.get('purpose') or 'context'}")
    return "\n".join(lines).rstrip() + "\n"


def _load_context(*, run_dir: str | Path | None, output_dir: str | Path | None) -> dict[str, Any]:
    root = Path(run_dir) if run_dir is not None else None
    root_exists = bool(root is not None and root.exists())
    state_dir = Path(output_dir) if output_dir is not None else (root if root_exists else default_guide_state_dir())
    summary: dict[str, Any] = {}
    if root_exists and root is not None:
        try:
            summary = read_run_summary(root) or build_run_summary(run_dir=root)
        except Exception:
            summary = {}
    return {
        "run_dir": root,
        "run_exists": root_exists,
        "state_dir": state_dir,
        "run_summary": summary,
        "mission_control": _read_bundle_from_dir(root if root_exists else Path("artifacts") / "mission_control_onboarding"),
        "handoff": _read_run_files(root, ["run_handoff.json", "next_run_options.json", "next_run_focus.json"]) if root_exists else {},
        "workspace": _read_workspace_files(root) if root_exists and root is not None else {},
    }


def _infer_current_state(*, context: dict[str, Any]) -> dict[str, Any]:
    root = context.get("run_dir")
    if root is None:
        return {
            "current_state": "onboarding",
            "state_confidence": "high",
            "headline": "Relaytic is ready to guide the first step.",
            "state_sources": ["guide_default_onboarding"],
        }
    if not context.get("run_exists"):
        return {
            "current_state": "run_missing",
            "state_confidence": "high",
            "headline": f"Relaytic cannot find run directory `{root}`.",
            "state_sources": ["filesystem"],
        }
    summary = dict(context.get("run_summary", {}))
    if not summary:
        return {
            "current_state": "artifact_shell",
            "state_confidence": "medium",
            "headline": "Relaytic found a run directory but no run summary yet.",
            "state_sources": ["filesystem"],
        }
    stage = _clean_text(summary.get("stage_completed"))
    decision = dict(summary.get("decision", {}))
    completion = dict(summary.get("completion", {}))
    handoff = dict(summary.get("handoff", {}))
    lifecycle = dict(summary.get("lifecycle", {}))
    selected_model = _clean_text(decision.get("selected_model_family"))
    if _clean_text(lifecycle.get("promotion_action")) or _clean_text(lifecycle.get("retrain_action")):
        state = "lifecycle_reviewed"
    elif _clean_text(completion.get("action")):
        state = "completion_reviewed"
    elif _clean_text(handoff.get("status")) == "ok":
        state = "handoff_ready"
    elif selected_model:
        state = "model_built"
    elif stage:
        state = "partial_run"
    else:
        state = "run_started"
    return {
        "current_state": state,
        "state_confidence": "high",
        "headline": _clean_text(summary.get("headline")) or f"Relaytic is at `{stage or state}`.",
        "state_sources": ["run_summary.json"],
    }


def _missing_evidence(*, context: dict[str, Any]) -> list[dict[str, Any]]:
    root = context.get("run_dir")
    if root is None or not context.get("run_exists"):
        return []
    root = Path(root)
    expected = [
        ("completion_decision.json", "completion", "Completion judgment is not available yet."),
        ("run_handoff.json", "handoff", "Differentiated post-run handoff is not available yet."),
        ("result_contract.json", "workspace", "Machine-stable result contract is not available yet."),
        ("benchmark_release_gate.json", "benchmark", "Paper/public benchmark claim gate is not available yet."),
        ("aml_public_claim_guard.json", "aml", "AML public-claim guard is not available yet."),
    ]
    missing = []
    for filename, family, reason in expected:
        if not (root / filename).exists():
            missing.append(
                {
                    "artifact": filename,
                    "family": family,
                    "severity": "info" if family in {"benchmark", "aml"} else "warning",
                    "reason": reason,
                }
            )
    return missing


def _claim_boundaries(*, summary: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    benchmark = dict(summary.get("benchmark", {}))
    aml_proof = dict(summary.get("aml_proof", {}))
    objective = dict(summary.get("objective_contract", {}))
    split = dict(summary.get("split_health", {}))
    hard_allowed = bool(
        benchmark.get("safe_to_cite_publicly")
        or aml_proof.get("paper_primary_claim_allowed")
        or aml_proof.get("broader_flagship_claim_allowed")
    )
    supporting_allowed = bool(aml_proof.get("supporting_public_claim_allowed"))
    if hard_allowed:
        posture = "hard_claim_allowed"
    elif supporting_allowed:
        posture = "supporting_only"
    elif summary:
        posture = "blocked_or_unproven"
    else:
        posture = "no_run"
    do_not_claim = []
    if posture != "hard_claim_allowed":
        do_not_claim.append("Do not claim paper-grade or SOTA benchmark superiority from this run yet.")
    if objective.get("status") == "blocked":
        do_not_claim.append("Do not rank model families as final winners while objective truth is blocked.")
    if split.get("safe_for_benchmarking") is False:
        do_not_claim.append("Do not treat the current split as benchmark-safe.")
    return {
        "posture": posture,
        "hard_public_claim_allowed": hard_allowed,
        "supporting_public_claim_allowed": supporting_allowed,
        "benchmark_safe_to_cite_publicly": benchmark.get("safe_to_cite_publicly"),
        "objective_contract_status": objective.get("status"),
        "split_safe_for_benchmarking": split.get("safe_for_benchmarking"),
        "do_not_claim": do_not_claim,
    }


def _blocking_items(
    *,
    context: dict[str, Any],
    missing: list[dict[str, Any]],
    claim_boundaries: dict[str, Any],
) -> list[dict[str, Any]]:
    blocks: list[dict[str, Any]] = []
    if context.get("run_dir") is not None and not context.get("run_exists"):
        blocks.append(
            {
                "source": "filesystem",
                "severity": "blocking",
                "title": "Run directory was not found",
                "detail": "Choose an existing run directory or start a new run.",
                "recommended_action": "choose_run_or_start_new",
            }
        )
    for item in missing:
        if item.get("artifact") == "completion_decision.json":
            blocks.append(
                {
                    "source": "completion",
                    "severity": "medium",
                    "title": "Completion judgment missing",
                    "detail": item.get("reason"),
                    "recommended_action": "review_partial_run",
                }
            )
    if claim_boundaries.get("posture") == "blocked_or_unproven":
        blocks.append(
            {
                "source": "claim_boundary",
                "severity": "info",
                "title": "Public claims are not proven yet",
                "detail": "Relaytic has not found enough claim-gate evidence for paper-grade claims.",
                "recommended_action": "export_context_or_continue_proof",
            }
        )
    return blocks


def _recommended_next_action(
    *,
    context: dict[str, Any],
    state: dict[str, Any],
    missing: list[dict[str, Any]],
    blocking_items: list[dict[str, Any]],
) -> dict[str, Any]:
    current_state = state["current_state"]
    summary = dict(context.get("run_summary", {}))
    if current_state == "onboarding":
        return _action("start_with_mission_control", "Start with Mission Control Chat", "relaytic mission-control chat")
    if current_state == "run_missing":
        return _action("choose_run_or_start_new", "Choose an existing run or start a new one", "relaytic guide --format json")
    if any(item.get("artifact") == "completion_decision.json" for item in missing):
        return _action(
            "review_partial_run",
            "Review the partial run before continuing",
            f"relaytic guide ask --run-dir {context['run_dir']} --message \"what should I do now?\" --format json",
        )
    completion_action = _clean_text(dict(summary.get("completion", {})).get("action"))
    if completion_action:
        return _action(
            completion_action,
            f"Follow completion action {completion_action}",
            f"relaytic completion review --run-dir {context['run_dir']} --format json",
        )
    handoff = dict(summary.get("handoff", {}))
    option = _clean_text(handoff.get("recommended_option_id"))
    if option:
        return _action(
            f"continue_{option}",
            f"Continue with {option}",
            f"relaytic handoff show --run-dir {context['run_dir']} --audience both --format json",
        )
    if blocking_items:
        return _action(str(blocking_items[0].get("recommended_action") or "review_state"), "Review the blocking item", None)
    return _action(
        "inspect_run_summary",
        "Inspect the run summary",
        f"relaytic show --run-dir {context['run_dir']} --format json" if context.get("run_dir") is not None else "relaytic guide",
    )


def _action(action_id: str, label: str, command: str | None) -> dict[str, Any]:
    return {
        "action_id": action_id,
        "label": label,
        "command": command,
        "description": label,
        "reason": label,
        "enabled": True,
    }


def _action_menu(*, context: dict[str, Any], state: dict[str, Any], recommended_action: dict[str, Any]) -> list[dict[str, Any]]:
    root = context.get("run_dir")
    actions = [dict(recommended_action)]
    if root is None or not context.get("run_exists"):
        actions.extend(
            [
                _action("doctor", "Check install health", "relaytic doctor --expected-profile full --format json"),
                _action("mission_control_chat", "Open guided terminal onboarding", "relaytic mission-control chat"),
                _action(
                    "start_governed_run",
                    "Start a governed run",
                    'relaytic run --run-dir artifacts/demo --data-path <data.csv> --text "<goal>"',
                ),
            ]
        )
    else:
        root_text = str(root)
        actions.extend(
            [
                _action("show_summary", "Show canonical run summary", f"relaytic show --run-dir {root_text} --format json"),
                _action("mission_control", "Show mission control", f"relaytic mission-control show --run-dir {root_text} --format json"),
                _action(
                    "ask_guide",
                    "Ask what to do next",
                    f"relaytic guide ask --run-dir {root_text} --message \"what should I do now?\" --format json",
                ),
                _action(
                    "export_external_context",
                    "Export safe context for another LLM",
                    f"relaytic guide export-context --run-dir {root_text} --audience external-llm --format json",
                ),
            ]
        )
        if Path(root_text, "run_handoff.json").exists():
            actions.append(
                _action("show_handoff", "Show result handoff", f"relaytic handoff show --run-dir {root_text} --audience both --format json")
            )
        if Path(root_text, "result_contract.json").exists():
            actions.append(_action("show_workspace", "Show workspace contract", f"relaytic workspace show --run-dir {root_text} --format json"))
    return _dedupe_actions(actions)


def _artifact_shortlist(*, context: dict[str, Any]) -> list[dict[str, Any]]:
    root = context.get("run_dir")
    if root is None or not context.get("run_exists"):
        return [
            _artifact(
                "docs/handbooks/relaytic_user_handbook.md",
                "Human starter guide",
                Path("docs/handbooks/relaytic_user_handbook.md").exists(),
                "human",
                True,
            ),
            _artifact(
                "docs/handbooks/relaytic_agent_handbook.md",
                "Agent command guide",
                Path("docs/handbooks/relaytic_agent_handbook.md").exists(),
                "agent",
                True,
            ),
        ]
    root = Path(root)
    candidates = [
        ("reports/user_result_report.md", "Plain-language human result report", "human", True),
        ("reports/agent_result_report.md", "Machine-facing result report", "agent", True),
        ("run_summary.json", "Canonical run summary", "both", True),
        ("result_contract.json", "Machine-stable current beliefs and next move", "agent", True),
        ("run_handoff.json", "Differentiated post-run handoff", "both", True),
        ("next_run_options.json", "Same-data, add-data, or new-dataset continuation options", "both", True),
        ("completion_decision.json", "Completion-governor judgment", "agent", True),
        ("next_action_queue.json", "Completion next-action queue", "agent", True),
        ("benchmark_release_gate.json", "Paper/public benchmark claim gate", "agent", True),
        ("aml_public_claim_guard.json", "AML public-claim guard", "agent", True),
        ("external_llm_context_pack.json", "Redacted external LLM context pack", "both", True),
    ]
    return [
        _artifact(rel, purpose, (root / rel).exists(), audience, upload_safe)
        for rel, purpose, audience, upload_safe in candidates
    ]


def _artifact(path: str, purpose: str, exists: bool, audience: str, upload_safe: bool) -> dict[str, Any]:
    return {
        "path": path,
        "purpose": purpose,
        "exists": exists,
        "audience": audience,
        "safe_for_external_llm": upload_safe,
        "contains_raw_rows": False,
    }


def _question_starters(*, context: dict[str, Any], state: dict[str, Any]) -> list[str]:
    if context.get("run_dir") is None or not context.get("run_exists"):
        return [
            "how do i start?",
            "what kind of data do you need?",
            "show me the fastest demo path",
            "how do i use this with another agent?",
        ]
    return [
        "where are we right now?",
        "what should i do next?",
        "what can i safely claim?",
        "what should i give to another llm?",
        "which artifact matters most?",
        "what is blocked?",
    ]


def _answer_message(
    *,
    message: str | None,
    state: dict[str, Any],
    recommended_action: dict[str, Any],
    action_menu: list[dict[str, Any]],
    claim_boundaries: dict[str, Any],
    artifact_shortlist: list[dict[str, Any]],
) -> str:
    normalized = " ".join(str(message or "").strip().lower().split())
    if not normalized:
        return _state_summary(state=state, recommended=recommended_action, blocking_items=[])
    if any(word in normalized for word in ("claim", "paper", "benchmark", "sota", "public")):
        blocked = "; ".join(claim_boundaries.get("do_not_claim", [])[:2])
        return f"Claim posture is `{claim_boundaries.get('posture')}`. {blocked or 'Current claim boundaries are available in the guide payload.'}"
    if any(word in normalized for word in ("external", "llm", "export", "context")):
        command = next((item.get("command") for item in action_menu if item.get("action_id") == "export_external_context"), None)
        return f"Use the external context export. Command: `{command or 'relaytic guide export-context --run-dir <run_dir> --audience external-llm --format json'}`."
    if any(word in normalized for word in ("artifact", "file", "report")):
        useful = [item for item in artifact_shortlist if item.get("exists")]
        if useful:
            names = ", ".join(f"`{item.get('path')}`" for item in useful[:4])
            return f"Start with these files: {names}."
        return "No run artifacts exist yet. Start with mission-control chat or create a governed run."
    if any(word in normalized for word in ("option", "can i", "can you", "available", "do now")):
        commands = [item.get("command") for item in action_menu if item.get("command")]
        return "Available safe commands: " + "; ".join(f"`{cmd}`" for cmd in commands[:4]) + "."
    return f"Relaytic is at `{state.get('current_state')}`. Best next move: `{recommended_action.get('label')}`."


def _local_llm_summary(
    *,
    config_path: str | None,
    use_local_llm: bool,
    state: dict[str, Any],
    recommended_action: dict[str, Any],
    claim_boundaries: dict[str, Any],
    answer: str,
) -> dict[str, Any]:
    generated_at = _utc_now()
    base = {
        "schema_version": GUIDE_LOCAL_LLM_SUMMARY_SCHEMA_VERSION,
        "generated_at": generated_at,
        "status": "not_requested",
        "llm_used": False,
        "recommended_action_preserved": True,
        "friendly_answer": None,
        "backend": {},
        "summary": "Local LLM guide phrasing was not requested.",
        "trace": {
            "agent": "guide",
            "operating_mode": "deterministic_no_lost_guide",
            "llm_used": False,
            "llm_status": "not_requested",
            "deterministic_evidence": ["guide_state", "action_menu", "artifact_shortlist"],
            "advisory_notes": [],
        },
    }
    if not use_local_llm:
        return base
    try:
        from relaytic.intelligence.backends import StructuredLocalAdvisor, discover_backend
        from relaytic.intelligence.models import build_intelligence_controls_from_policy

        policy = load_config(config_path)
        controls = build_intelligence_controls_from_policy(policy)
        if controls.intelligence_mode.strip().lower() in {"", "none", "off", "disabled", "deterministic"}:
            controls = replace(controls, intelligence_mode="advisory_local_llm", minimum_local_llm_enabled=True)
        discovery = discover_backend(controls=controls, config_path=config_path)
        backend = discovery.to_dict()
        if discovery.status != "available" or discovery.advisor is None:
            base.update(
                {
                    "status": discovery.status,
                    "backend": backend,
                    "summary": "Local LLM guide phrasing is unavailable, so Relaytic used deterministic guidance.",
                }
            )
            base["trace"]["llm_status"] = discovery.status
            return base
        advisor = StructuredLocalAdvisor(replace(discovery.advisor.config, timeout_seconds=min(discovery.advisor.config.timeout_seconds, 5)))
        advisory = advisor.complete_json(
            task_name="guide_summary",
            system_prompt=(
                "You rewrite Relaytic guide text for clarity. Return JSON only with keys "
                "friendly_answer and caveats. Do not invent commands, claims, metrics, or actions."
            ),
            payload={
                "current_state": state.get("current_state"),
                "recommended_action": recommended_action,
                "claim_boundaries": claim_boundaries,
                "deterministic_answer": answer,
            },
        )
        if advisory.status != "ok" or not isinstance(advisory.payload, dict):
            base.update(
                {
                    "status": advisory.status,
                    "backend": backend,
                    "summary": "Local LLM guide phrasing failed, so Relaytic used deterministic guidance.",
                }
            )
            base["trace"]["llm_status"] = advisory.status
            base["trace"]["advisory_notes"] = list(advisory.notes)
            return base
        friendly = _clean_text(advisory.payload.get("friendly_answer"))
        base.update(
            {
                "status": "ok",
                "llm_used": True,
                "backend": backend,
                "friendly_answer": friendly or answer,
                "summary": "Local LLM phrasing was used without changing the deterministic recommended action.",
            }
        )
        base["trace"]["llm_used"] = True
        base["trace"]["llm_status"] = "ok"
        return base
    except Exception as exc:
        base.update(
            {
                "status": "error",
                "summary": "Local LLM guide phrasing failed, so Relaytic used deterministic guidance.",
                "error": str(exc),
            }
        )
        base["trace"]["llm_status"] = "error"
        base["trace"]["advisory_notes"] = [str(exc)]
        return base


def _external_artifact_index(*, bundle: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    artifacts = [
        item
        for item in list(bundle.get("guide_artifact_shortlist", {}).get("artifacts", []))
        if isinstance(item, dict) and bool(item.get("exists")) and bool(item.get("safe_for_external_llm"))
    ]
    return {
        "schema_version": EXTERNAL_LLM_ARTIFACT_INDEX_SCHEMA_VERSION,
        "generated_at": _utc_now(),
        "status": "ok",
        "artifacts": artifacts,
        "summary": "All listed artifacts are local files selected for rowless external context. Raw data files are excluded.",
    }


def _external_prompt(bundle: dict[str, Any]) -> str:
    state = dict(bundle.get("guide_state", {}))
    return (
        "Use this Relaytic context pack as artifact-derived local evidence. "
        "Do not assume raw rows are present. Respect the claim boundaries. "
        f"Current state is `{state.get('current_state')}` and the recommended next action is "
        f"`{dict(state.get('recommended_next_action') or {}).get('action_id')}`."
    )


def _sanitize_for_external_pack(value: Any, *, redactions: list[dict[str, Any]], field: str = "root") -> Any:
    if isinstance(value, dict):
        return {str(key): _sanitize_for_external_pack(item, redactions=redactions, field=f"{field}.{key}") for key, item in value.items()}
    if isinstance(value, list):
        return [_sanitize_for_external_pack(item, redactions=redactions, field=f"{field}[]") for item in value]
    if isinstance(value, str):
        sanitized = _sanitize_string(value)
        if sanitized != value:
            redactions.append({"field": field, "reason": "private_path_or_secret_pattern", "replacement": sanitized})
        return sanitized
    return value


def _sanitize_string(text: str) -> str:
    sanitized = re.sub(r"[A-Za-z]:[\\/][^\s`\"']+", _path_redaction, text)
    sanitized = re.sub(r"/(?:Users|home)/[^\s`\"']+", _path_redaction, sanitized)
    sanitized = re.sub(r"(?<![:/])/(?:[^\s`\"'/]+/)+[^\s`\"']+", _path_redaction, sanitized)
    sanitized = re.sub(
        r"(?i)(api[_-]?key|token|secret)\s*[:=]\s*[A-Za-z0-9_\-]{8,}",
        r"\1=<redacted_secret>",
        sanitized,
    )
    return sanitized


def _path_redaction(match: re.Match[str]) -> str:
    raw = match.group(0)
    name = Path(raw.replace("\\", "/")).name
    return f"<redacted_path:{name or 'local'}>"


def _safe_subset(value: Any, *, keys: list[str]) -> dict[str, Any]:
    payload = dict(value) if isinstance(value, dict) else {}
    return {key: payload.get(key) for key in keys}


def _state_summary(*, state: dict[str, Any], recommended: dict[str, Any], blocking_items: list[dict[str, Any]]) -> str:
    block_text = ""
    if blocking_items:
        block_text = f" It sees {len(blocking_items)} item(s) needing attention."
    return (
        f"Relaytic is in `{state.get('current_state')}` with `{state.get('state_confidence')}` confidence. "
        f"Best next move: `{recommended.get('label')}`.{block_text}"
    )


def _guide_surface_summary(bundle: dict[str, Any]) -> dict[str, Any]:
    state = dict(bundle.get("guide_state", {}))
    menu = dict(bundle.get("guide_action_menu", {}))
    artifacts = dict(bundle.get("guide_artifact_shortlist", {}))
    questions = dict(bundle.get("guide_question_starters", {}))
    local_llm = dict(bundle.get("guide_local_llm_summary", {}))
    return {
        "current_state": state.get("current_state"),
        "state_confidence": state.get("state_confidence"),
        "recommended_next_action": state.get("recommended_next_action"),
        "blocking_count": len(state.get("blocking_items", []) or []),
        "missing_evidence_count": len(state.get("missing_evidence", []) or []),
        "safe_command_count": menu.get("safe_command_count"),
        "artifact_count": len(artifacts.get("artifacts", []) or []),
        "question_count": len(questions.get("questions", []) or []),
        "claim_posture": dict(state.get("claim_boundaries", {})).get("posture"),
        "local_llm_status": local_llm.get("status"),
    }


def _trace(*, local_llm_summary: dict[str, Any]) -> dict[str, Any]:
    return {
        "agent": "guide",
        "operating_mode": "deterministic_no_lost_guide",
        "llm_used": bool(local_llm_summary.get("llm_used")),
        "llm_status": local_llm_summary.get("status") or "not_requested",
        "deterministic_evidence": [
            "run_summary",
            "mission_control",
            "handoff",
            "workspace",
            "benchmark_claim_boundaries",
        ],
        "advisory_notes": [
            "Guide is an orientation layer over existing artifacts, not a second source of truth.",
        ],
    }


def _read_bundle_from_dir(path: Path | None) -> dict[str, Any]:
    if path is None or not path.exists():
        return {}
    bundle: dict[str, Any] = {}
    for filename in (
        "mission_control_state.json",
        "review_queue_state.json",
        "capability_manifest.json",
        "action_affordances.json",
        "release_health_report.json",
        "onboarding_success_report.json",
    ):
        loaded = _read_json(path / filename)
        if loaded:
            bundle[Path(filename).stem] = loaded
    return bundle


def _read_run_files(root: Path | None, filenames: list[str]) -> dict[str, Any]:
    if root is None:
        return {}
    bundle: dict[str, Any] = {}
    for filename in filenames:
        loaded = _read_json(root / filename)
        if loaded:
            bundle[Path(filename).stem] = loaded
    return bundle


def _read_workspace_files(root: Path | None) -> dict[str, Any]:
    if root is None:
        return {}
    workspace_dir = root.parent / "workspace"
    return _read_run_files(
        workspace_dir,
        ["workspace_state.json", "workspace_lineage.json", "workspace_focus_history.json", "workspace_memory_policy.json", "next_run_plan.json"],
    )


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return dict(payload) if isinstance(payload, dict) else {}


def _dedupe_actions(actions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    deduped: list[dict[str, Any]] = []
    for item in actions:
        action_id = str(item.get("action_id") or "").strip()
        command = str(item.get("command") or "").strip()
        key = action_id or command
        if not key or key in seen:
            continue
        seen.add(key)
        deduped.append(item)
    return deduped


def _attach_existing_context_paths(*, bundle: dict[str, Any], state_dir: Path) -> None:
    existing = _existing_context_pack_paths(state_dir)
    if existing.get("status") == "ready":
        bundle["guide_state"]["external_context_pack"] = existing


def _existing_context_pack_paths(state_dir: Path) -> dict[str, Any]:
    json_path = state_dir / "external_llm_context_pack.json"
    md_path = state_dir / "external_llm_context_pack.md"
    index_path = state_dir / "external_llm_artifact_index.json"
    redaction_path = state_dir / "external_llm_redaction_report.json"
    if not json_path.exists():
        return {"status": "not_exported"}
    return {
        "status": "ready",
        "context_pack_path": str(json_path),
        "context_pack_markdown_path": str(md_path) if md_path.exists() else None,
        "artifact_index_path": str(index_path) if index_path.exists() else None,
        "redaction_report_path": str(redaction_path) if redaction_path.exists() else None,
    }


def _safe_display_path(value: Any, *, base: Any) -> str | None:
    if value is None:
        return None
    path = Path(value)
    try:
        return str(path.relative_to(Path(base)))
    except (ValueError, TypeError):
        return str(path)


def _clean_text(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text or text.lower() in {"none", "null"}:
        return None
    return text


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()
