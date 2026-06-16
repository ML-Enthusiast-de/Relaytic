"""Paper Track P15 measured system-evaluation proof pack."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
from typing import Any

from relaytic.core.json_utils import write_json


PAPER_SYSTEM_EVAL_SCHEMA_VERSION = "relaytic.paper_system_eval.v1"
PAPER_SYSTEM_EVAL_REPORT_DIR = Path("docs") / "reports"
PAPER_SYSTEM_EVAL_STATE_DIR = Path("artifacts") / "release_safety" / "paper_p15_system_eval"
NEXT_PAPER_SYSTEM_EVAL_SLICE = "Slice 16A - capability registry and capability cards"

PAPER_SYSTEM_EVAL_FILENAMES = {
    "paper_system_behavior_eval": "paper_system_behavior_eval.json",
    "paper_system_task_eval": "paper_system_task_eval.json",
    "paper_agent_handoff_eval": "paper_agent_handoff_eval.json",
    "paper_no_lost_user_eval": "paper_no_lost_user_eval.json",
    "paper_claim_gate_case_studies": "paper_claim_gate_case_studies.json",
    "paper_system_eval_manifest": "paper_system_eval_manifest.json",
    "paper_system_eval_summary": "paper_system_eval_summary.md",
}

REQUIRED_CLAIM_INPUT_REFS = [
    "docs/reports/paper_claim_lint_report.json",
    "docs/reports/paper_external_dry_run_report.json",
    "docs/reports/paper_reproduction_failure_report.json",
    "docs/reports/paper_release_go_no_go.json",
]
REQUIRED_READER_TASK_INPUT_REFS = [
    "README.md",
    "docs/reports/paper_result_table_final.json",
    "docs/reports/paper_metric_cell_audit.json",
    "docs/reports/paper_publishability_matrix.json",
]
OPTIONAL_CLAIM_INPUT_REFS = [
    "docs/reports/paper_public_claims_allowed.json",
    "docs/reports/paper_release_manifest.json",
    "docs/reports/paper_arxiv_source_manifest.json",
]
REQUIRED_SERVER_TOOLS = {
    "relaytic_server_info",
    "relaytic_show_mission_control",
    "relaytic_show_trace",
    "relaytic_show_handoff",
    "relaytic_show_workspace",
    "relaytic_assist_turn",
    "relaytic_check_permission",
    "relaytic_run_agent_evals",
}
SYSTEM_EVAL_STATE_FILENAMES = [
    "guide_state.json",
    "guide_action_menu.json",
    "guide_artifact_shortlist.json",
    "guide_question_starters.json",
    "guide_local_llm_summary.json",
    "external_llm_context_pack.json",
    "external_llm_context_pack.md",
    "external_llm_artifact_index.json",
    "external_llm_redaction_report.json",
    "manifest.json",
]


def build_paper_system_eval_pack(
    project_root: str | Path,
    *,
    state_dir: str | Path | None = None,
) -> dict[str, Any]:
    """Build deterministic P15 evidence for Relaytic's user/agent system behavior."""
    root = Path(project_root)
    state_root = Path(state_dir) if state_dir is not None else root / PAPER_SYSTEM_EVAL_STATE_DIR
    inputs = _collect_inputs(root)
    surfaces = _materialize_system_surfaces(root=root, state_root=state_root)
    no_lost = _build_no_lost_user_eval(root=root, surfaces=surfaces)
    agent_handoff = _build_agent_handoff_eval(root=root, surfaces=surfaces)
    claim_cases = _build_claim_gate_case_studies(inputs=inputs)
    reader_tasks = _build_reader_task_eval(
        inputs=inputs,
        no_lost_user_eval=no_lost,
        agent_handoff_eval=agent_handoff,
        claim_gate_case_studies=claim_cases,
    )
    behavior = _build_system_behavior_eval(
        no_lost_user_eval=no_lost,
        agent_handoff_eval=agent_handoff,
        claim_gate_case_studies=claim_cases,
        reader_task_eval=reader_tasks,
    )
    manifest = _build_manifest(
        root=root,
        state_root=state_root,
        inputs=inputs,
        surfaces=surfaces,
        no_lost_user_eval=no_lost,
        agent_handoff_eval=agent_handoff,
        claim_gate_case_studies=claim_cases,
        reader_task_eval=reader_tasks,
        system_behavior_eval=behavior,
    )
    pack = {
        "paper_system_behavior_eval": behavior,
        "paper_system_task_eval": reader_tasks,
        "paper_agent_handoff_eval": agent_handoff,
        "paper_no_lost_user_eval": no_lost,
        "paper_claim_gate_case_studies": claim_cases,
        "paper_system_eval_manifest": manifest,
    }
    pack["paper_system_eval_summary"] = render_paper_system_eval_markdown(pack)
    return pack


def sync_paper_system_eval_pack(
    project_root: str | Path,
    *,
    output_dir: str | Path | None = None,
    state_dir: str | Path | None = None,
) -> dict[str, Path]:
    """Write P15 measured system-evaluation reports under docs/reports."""
    root = Path(project_root)
    report_dir = Path(output_dir) if output_dir is not None else root / PAPER_SYSTEM_EVAL_REPORT_DIR
    report_dir.mkdir(parents=True, exist_ok=True)
    pack = build_paper_system_eval_pack(root, state_dir=state_dir)
    written: dict[str, Path] = {}
    for key, filename in PAPER_SYSTEM_EVAL_FILENAMES.items():
        path = report_dir / filename
        if filename.endswith(".md"):
            path.write_text(str(pack[key]), encoding="utf-8")
            written[key] = path
        else:
            written[key] = write_json(path, pack[key], indent=2, sort_keys=True)
    return written


def render_paper_system_eval_markdown(pack: dict[str, Any]) -> str:
    manifest = dict(pack.get("paper_system_eval_manifest", {}))
    behavior = dict(pack.get("paper_system_behavior_eval", {}))
    reader_tasks = dict(pack.get("paper_system_task_eval", {}))
    rows = list(behavior.get("evaluation_rows", []))
    task_rows = list(reader_tasks.get("tasks", []))
    lines = [
        "# Paper P15 System-Evaluation Proof Pack",
        "",
        f"- Status: `{manifest.get('status') or 'unknown'}`",
        f"- System pass rate: `{behavior.get('pass_rate')}`",
        f"- Required task count: `{behavior.get('required_task_count')}`",
        f"- Raw rows exposed: `{behavior.get('raw_rows_exposed')}`",
        f"- Private paths exposed: `{behavior.get('private_paths_exposed')}`",
        f"- Next slice: `{manifest.get('next_slice') or 'unknown'}`",
        "",
        "## Reader And Agent Task Evaluation",
        "",
        (
            f"The reader-task suite checks `{reader_tasks.get('passed_task_count')}`/"
            f"`{reader_tasks.get('task_count')}` concrete navigation, provenance, privacy, and claim-boundary tasks."
        ),
        "",
        "| Task | Measured Signal | Source | Result |",
        "| --- | --- | --- | --- |",
    ]
    for row in task_rows:
        result = "pass" if row.get("passed") else "fail"
        lines.append(
            "| "
            + " | ".join(
                [
                    _escape_md(str(row.get("task_id") or "unknown")),
                    _escape_md(str(row.get("measured_signal") or "")),
                    _escape_md(str(row.get("source_artifact") or "")),
                    f"`{result}`",
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## Aggregate Protocol Checks",
            "",
        "| Track | Task | Measured Signal | Result |",
        "| --- | --- | --- | --- |",
        ]
    )
    for row in rows:
        required = bool(row.get("required", True))
        passed = bool(row.get("passed"))
        result = "pass" if passed else "observed" if not required else "fail"
        lines.append(
            "| "
            + " | ".join(
                [
                    _escape_md(str(row.get("track") or "system")),
                    _escape_md(str(row.get("task") or "unknown")),
                    _escape_md(str(row.get("measured_signal") or "")),
                    f"`{result}`",
                ]
            )
            + " |"
        )
    return "\n".join(lines).rstrip() + "\n"


def _collect_inputs(root: Path) -> dict[str, Any]:
    reports = root / PAPER_SYSTEM_EVAL_REPORT_DIR
    return {
        "root": root,
        "paper_claim_lint_report": _read_artifact(reports / "paper_claim_lint_report.json", root=root),
        "paper_external_dry_run_report": _read_artifact(reports / "paper_external_dry_run_report.json", root=root),
        "paper_reproduction_failure_report": _read_artifact(reports / "paper_reproduction_failure_report.json", root=root),
        "paper_release_go_no_go": _read_artifact(reports / "paper_release_go_no_go.json", root=root),
        "readme": _read_text_artifact(root / "README.md", root=root),
        "paper_result_table_final": _read_artifact(reports / "paper_result_table_final.json", root=root),
        "paper_metric_cell_audit": _read_artifact(reports / "paper_metric_cell_audit.json", root=root),
        "paper_publishability_matrix": _read_artifact(reports / "paper_publishability_matrix.json", root=root),
        "paper_public_claims_allowed": _read_artifact(reports / "paper_public_claims_allowed.json", root=root),
        "paper_release_manifest": _read_artifact(reports / "paper_release_manifest.json", root=root),
        "paper_arxiv_source_manifest": _read_artifact(reports / "paper_arxiv_source_manifest.json", root=root),
    }


def _materialize_system_surfaces(*, root: Path, state_root: Path) -> dict[str, Any]:
    partial_run = state_root / "partial_run"
    onboarding_dir = state_root / "onboarding"
    partial_run.mkdir(parents=True, exist_ok=True)
    onboarding_dir.mkdir(parents=True, exist_ok=True)
    _reset_system_eval_state_dirs(partial_run, onboarding_dir)
    _write_partial_run_summary(partial_run)

    try:
        from relaytic.guide.agents import export_external_context_pack, run_guide_review
    except Exception as exc:  # pragma: no cover - defensive import guard
        sanitized = _sanitize_text(str(exc))
        return {
            "status": "error",
            "error": sanitized,
            "state_tree": _state_tree(root=root, state_root=state_root, partial_run=partial_run, onboarding_dir=onboarding_dir),
            "onboarding_payload": {"status": "error", "error": sanitized},
            "partial_payload": {"status": "error", "error": sanitized},
            "external_context_payload": {"status": "error", "error": sanitized},
            "server_info": {"status": "error", "error": sanitized},
        }

    onboarding_payload = _call_surface(lambda: run_guide_review(output_dir=onboarding_dir))
    partial_payload = _call_surface(lambda: run_guide_review(run_dir=partial_run))
    external_context_payload = _call_surface(
        lambda: export_external_context_pack(run_dir=partial_run, audience="external-llm")
    )
    try:
        from relaytic.interoperability import relaytic_server_info

        server_info = relaytic_server_info()
    except Exception as exc:  # pragma: no cover - defensive import guard
        server_info = {"status": "error", "error": _sanitize_text(str(exc))}

    return {
        "status": "ok",
        "state_tree": _state_tree(root=root, state_root=state_root, partial_run=partial_run, onboarding_dir=onboarding_dir),
        "onboarding_payload": onboarding_payload,
        "partial_payload": partial_payload,
        "external_context_payload": external_context_payload,
        "server_info": _safe_server_info(server_info),
    }


def _build_no_lost_user_eval(*, root: Path, surfaces: dict[str, Any]) -> dict[str, Any]:
    onboarding = dict(surfaces.get("onboarding_payload", {}))
    partial = dict(surfaces.get("partial_payload", {}))
    context = dict(surfaces.get("external_context_payload", {}))
    onboarding_guide = dict(onboarding.get("guide", {}))
    onboarding_bundle = dict(onboarding.get("bundle", {}))
    partial_guide = dict(partial.get("guide", {}))
    partial_bundle = dict(partial.get("bundle", {}))
    context_pack = dict(context.get("external_context_pack", {}))

    onboarding_actions = _actions(onboarding_bundle)
    partial_actions = _actions(partial_bundle)
    onboarding_artifacts = _artifacts(onboarding_bundle)
    context_artifacts = list(context_pack.get("artifact_index", []))
    context_artifact_paths = {
        str(item.get("path") or "")
        for item in context_artifacts
        if isinstance(item, dict)
    }
    tasks = [
        _task(
            "no_lost_user",
            "onboarding_guide_available",
            onboarding_guide.get("current_state") == "onboarding"
            and int(onboarding_guide.get("safe_command_count") or 0) >= 3
            and int(onboarding_guide.get("question_count") or 0) >= 4
            and "mission_control_chat" in {str(item.get("action_id")) for item in onboarding_actions}
            and {"docs/handbooks/relaytic_user_handbook.md", "docs/handbooks/relaytic_agent_handbook.md"}.issubset(
                {str(item.get("path")) for item in onboarding_artifacts}
            ),
            "A new user should see onboarding state, safe commands, starter questions, and human/agent handbooks.",
            "state="
            f"{onboarding_guide.get('current_state')}; commands={onboarding_guide.get('safe_command_count')}; "
            f"questions={onboarding_guide.get('question_count')}",
            "artifacts/release_safety/paper_p15_system_eval/onboarding/guide_state.json",
        ),
        _task(
            "no_lost_user",
            "partial_run_state_recovery",
            partial_guide.get("current_state") == "partial_run"
            and int(partial_guide.get("missing_evidence_count") or 0) >= 1
            and "export_external_context" in {str(item.get("action_id")) for item in partial_actions},
            "A partial run should explain where it is, what evidence is missing, and how to export safe context.",
            "state="
            f"{partial_guide.get('current_state')}; missing={partial_guide.get('missing_evidence_count')}; "
            f"actions={len(partial_actions)}",
            "artifacts/release_safety/paper_p15_system_eval/partial_run/guide_state.json",
        ),
        _task(
            "no_lost_user",
            "artifact_shortlist_points_to_canonical_state",
            "run_summary.json" in context_artifact_paths
            and all(not bool(item.get("contains_raw_rows")) for item in context_artifacts if isinstance(item, dict)),
            "The handoff should name canonical state artifacts without exposing raw rows.",
            f"artifact_count={len(context_artifacts)}; includes_run_summary={'run_summary.json' in context_artifact_paths}",
            "artifacts/release_safety/paper_p15_system_eval/partial_run/external_llm_artifact_index.json",
        ),
    ]
    return {
        "schema_version": PAPER_SYSTEM_EVAL_SCHEMA_VERSION,
        "slice": "Paper Track P15",
        "status": "pass" if all(item["passed"] for item in tasks) else "fail",
        "task_count": len(tasks),
        "passed_task_count": sum(1 for item in tasks if item["passed"]),
        "tasks": tasks,
        "state_tree": surfaces.get("state_tree", {}),
        "summary": "Relaytic guide surfaces were evaluated for onboarding, partial-run recovery, and artifact shortlisting.",
    }


def _build_agent_handoff_eval(*, root: Path, surfaces: dict[str, Any]) -> dict[str, Any]:
    context = dict(surfaces.get("external_context_payload", {}))
    context_pack = dict(context.get("external_context_pack", {}))
    redaction = dict(context.get("external_llm_redaction_report", {}))
    partial = dict(surfaces.get("partial_payload", {}))
    partial_bundle = dict(partial.get("bundle", {}))
    local_llm = dict(partial_bundle.get("guide_local_llm_summary", {}))
    server_info = dict(surfaces.get("server_info", {}))
    inspection_tools = set(server_info.get("inspection_tools", []) or [])
    workflow_tools = set(server_info.get("workflow_tools", []) or [])
    tools = inspection_tools | workflow_tools
    available_actions = [
        item
        for item in list(context_pack.get("available_actions", []))
        if isinstance(item, dict)
    ]
    required_tools_present = REQUIRED_SERVER_TOOLS.issubset(tools)
    tasks = [
        _task(
            "agent_handoff",
            "server_tool_contract_available",
            server_info.get("status") == "ok"
            and int(server_info.get("tool_count") or 0) >= 20
            and required_tools_present,
            "External agents should be able to discover inspection, workflow, trace, and permission tools.",
            f"tool_count={server_info.get('tool_count')}; required_present={required_tools_present}",
            "relaytic.interoperability.relaytic_server_info",
        ),
        _task(
            "agent_handoff",
            "external_context_rowless_and_redacted",
            context_pack.get("raw_rows_included") is False
            and context_pack.get("local_only") is True
            and int(redaction.get("redaction_count") or 0) >= 1
            and {"raw_rows", "absolute_source_paths"}.issubset(set(redaction.get("blocked_fields", []) or []))
            and not _contains_private_path(json.dumps(context_pack, sort_keys=True)),
            "External context should carry artifact-derived state, not raw rows or private paths.",
            "raw_rows="
            f"{context_pack.get('raw_rows_included')}; redactions={redaction.get('redaction_count')}; "
            f"blocked_fields={len(redaction.get('blocked_fields', []) or [])}",
            "artifacts/release_safety/paper_p15_system_eval/partial_run/external_llm_context_pack.json",
        ),
        _task(
            "agent_handoff",
            "safe_next_action_exported",
            bool(dict(context_pack.get("guide", {})).get("recommended_next_action"))
            and bool([item for item in available_actions if item.get("command")])
            and len(context_pack.get("starter_questions", []) or []) >= 4,
            "Another model should receive next-action options and starter questions without guessing artifact names.",
            "actions="
            f"{len(available_actions)}; starter_questions={len(context_pack.get('starter_questions', []) or [])}",
            "artifacts/release_safety/paper_p15_system_eval/partial_run/external_llm_context_pack.json",
        ),
        _task(
            "agent_handoff",
            "local_llm_option_is_advisory",
            local_llm.get("status") in {"not_requested", "ok", "available", "unavailable", "error"}
            and local_llm.get("llm_used") is False
            and dict(local_llm.get("trace", {})).get("operating_mode") == "deterministic_no_lost_guide",
            "The local-LLM path should be optional phrasing help over deterministic artifact guidance.",
            f"llm_status={local_llm.get('status')}; llm_used={local_llm.get('llm_used')}",
            "artifacts/release_safety/paper_p15_system_eval/partial_run/guide_local_llm_summary.json",
        ),
    ]
    return {
        "schema_version": PAPER_SYSTEM_EVAL_SCHEMA_VERSION,
        "slice": "Paper Track P15",
        "status": "pass" if all(item["passed"] for item in tasks) else "fail",
        "task_count": len(tasks),
        "passed_task_count": sum(1 for item in tasks if item["passed"]),
        "tool_contract": {
            "tool_count": server_info.get("tool_count"),
            "required_tools": sorted(REQUIRED_SERVER_TOOLS),
            "missing_required_tools": sorted(REQUIRED_SERVER_TOOLS - tools),
        },
        "tasks": tasks,
        "summary": "Relaytic external-agent handoff was evaluated for discoverability, redaction, next actions, and local-LLM boundaries.",
    }


def _build_claim_gate_case_studies(*, inputs: dict[str, Any]) -> dict[str, Any]:
    claim_lint = _payload(inputs["paper_claim_lint_report"])
    dry_run = _payload(inputs["paper_external_dry_run_report"])
    failures = _payload(inputs["paper_reproduction_failure_report"])
    go_no_go = _payload(inputs["paper_release_go_no_go"])
    p13_claims = _payload(inputs["paper_public_claims_allowed"])
    p13_release = _payload(inputs["paper_release_manifest"])
    p14_source = _payload(inputs["paper_arxiv_source_manifest"])

    cases = [
        _case(
            "claim_gate",
            "p11_claim_lint_passed",
            claim_lint.get("status") == "pass"
            and claim_lint.get("hard_claims_allowed") is False
            and claim_lint.get("headline_claims_allowed") is False,
            "P11 should keep blocked claim language out of the generated draft.",
            f"status={claim_lint.get('status')}; hard={claim_lint.get('hard_claims_allowed')}; headline={claim_lint.get('headline_claims_allowed')}",
            "docs/reports/paper_claim_lint_report.json",
        ),
        _case(
            "claim_gate",
            "p12_go_no_go_blocks_hard_and_headline_claims",
            go_no_go.get("status") == "go_for_p13_claim_safe_release_pack"
            and go_no_go.get("hard_claims_allowed") is False
            and go_no_go.get("headline_claims_allowed") is False
            and bool(go_no_go.get("blocked_public_claims")),
            "P12 should allow only a claim-safe paper release mode.",
            f"status={go_no_go.get('status')}; blocked={len(go_no_go.get('blocked_public_claims', []) or [])}",
            "docs/reports/paper_release_go_no_go.json",
        ),
        _case(
            "claim_gate",
            "p12_full_benchmark_rerun_scope_disclosed",
            dry_run.get("status") == "pass_paper_smoke_reproduced_claim_linted"
            and dry_run.get("fallback_rule_applied") is True
            and bool(dry_run.get("full_benchmark_commands_not_reproduced")),
            "P12 should disclose which heavy benchmark reruns remain outside the paper-smoke proof.",
            "fallback="
            f"{dry_run.get('fallback_rule_applied')}; withheld_commands={len(dry_run.get('full_benchmark_commands_not_reproduced', []) or [])}",
            "docs/reports/paper_external_dry_run_report.json",
        ),
        _case(
            "claim_gate",
            "p12_reproduction_failures_clear",
            failures.get("status") == "no_failures" and int(failures.get("unresolved_failure_count") or 0) == 0,
            "P12 should have no unresolved paper-smoke reproduction failures.",
            f"status={failures.get('status')}; unresolved={failures.get('unresolved_failure_count')}",
            "docs/reports/paper_reproduction_failure_report.json",
        ),
        _case(
            "claim_gate",
            "p13_public_wording_lint_passed",
            p13_claims.get("status") == "claim_safe_public_wording_allowed"
            and p13_claims.get("hard_claims_allowed") is False
            and p13_claims.get("headline_claims_allowed") is False,
            "P13 public wording should remain claim-safe if present.",
            f"status={p13_claims.get('status')}; lint={dict(p13_claims.get('wording_lint', {})).get('status')}",
            "docs/reports/paper_public_claims_allowed.json",
            required=False,
            observed=bool(inputs["paper_public_claims_allowed"].get("exists")),
        ),
        _case(
            "claim_gate",
            "p14_source_bundle_requires_human_upload_gate",
            p14_source.get("source_release_candidate_ready") is True
            and p14_source.get("arxiv_upload_ready") is False,
            "P14 source packaging should stay release-candidate only until human metadata and PDF checks are complete.",
            f"source_ready={p14_source.get('source_release_candidate_ready')}; upload_ready={p14_source.get('arxiv_upload_ready')}",
            "docs/reports/paper_arxiv_source_manifest.json",
            required=False,
            observed=bool(inputs["paper_arxiv_source_manifest"].get("exists")),
        ),
        _case(
            "claim_gate",
            "p13_release_manifest_claim_safe",
            p13_release.get("status") == "ready_for_claim_safe_arxiv_release"
            and p13_release.get("claim_safe_public_release_allowed") is True,
            "P13 release manifest should authorize only claim-safe public release if present.",
            f"status={p13_release.get('status')}; release_allowed={p13_release.get('claim_safe_public_release_allowed')}",
            "docs/reports/paper_release_manifest.json",
            required=False,
            observed=bool(inputs["paper_release_manifest"].get("exists")),
        ),
    ]
    required_cases = [item for item in cases if item.get("required")]
    return {
        "schema_version": PAPER_SYSTEM_EVAL_SCHEMA_VERSION,
        "slice": "Paper Track P15",
        "status": "pass" if all(item["passed"] for item in required_cases) else "fail",
        "case_count": len(cases),
        "required_case_count": len(required_cases),
        "passed_required_case_count": sum(1 for item in required_cases if item["passed"]),
        "cases": cases,
        "summary": "Claim-gate cases verify that public paper claims remain bounded by P11/P12 evidence, with P13/P14 observed when present.",
    }


def _build_reader_task_eval(
    *,
    inputs: dict[str, Any],
    no_lost_user_eval: dict[str, Any],
    agent_handoff_eval: dict[str, Any],
    claim_gate_case_studies: dict[str, Any],
) -> dict[str, Any]:
    readme_text = _text_payload(inputs["readme"])
    readme_lower = readme_text.lower()
    result_table = _payload(inputs["paper_result_table_final"])
    metric_audit = _payload(inputs["paper_metric_cell_audit"])
    publishability = _payload(inputs["paper_publishability_matrix"])
    pay_base_cell = _find_metric_cell(metric_audit, "paysim_p6_validation_selected_baseline.test_pr_auc")
    pay_comp_cell = _find_metric_cell(metric_audit, "paysim_p6a_competitive_selected.test_pr_auc")
    pay_row = _find_publishability_row(publishability, dataset_id="paysim_temporal_transaction_fraud")
    elliptic2_context = _find_publishability_row(
        publishability,
        dataset_id="elliptic2_subgraph_aml",
        role="modern_context_only",
    )
    elliptic2_firewall = _find_publishability_row(
        publishability,
        dataset_id="elliptic2_subgraph_aml",
        role="claim_firewall",
    )
    paysim_result_row = _find_result_row(result_table, "paysim_p6a_competitive_selected")
    required_metric_fields = {
        "artifact_ref",
        "artifact_field",
        "budget_tier",
        "claim_state",
        "command",
        "dataset_id",
        "leakage_posture",
        "metric_id",
        "publishability_gate_ref",
        "publishability_gate_status",
        "row_id",
        "split",
        "value",
    }
    no_lost_tasks = _task_pass_map(no_lost_user_eval.get("tasks", []))
    handoff_tasks = _task_pass_map(agent_handoff_eval.get("tasks", []))
    claim_cases = _case_pass_map(claim_gate_case_studies.get("cases", []))
    publishability_rows = [
        item
        for item in list(publishability.get("rows", []))
        if isinstance(item, dict)
    ]
    all_rows_block_hard = bool(publishability_rows) and all(
        item.get("hard_claim_allowed") is False and item.get("headline_claim_allowed") is False
        for item in publishability_rows
    )
    pay_base_value = pay_base_cell.get("value")
    pay_comp_value = pay_comp_cell.get("value")
    try:
        pay_improved = float(pay_comp_value) > float(pay_base_value)
    except (TypeError, ValueError):
        pay_improved = False
    tasks = [
        _task(
            "reader_task",
            "repo_navigation_separates_relaytic_from_aml_paper",
            inputs["readme"].get("exists") is True
            and "this repository is larger than the aml paper" in readme_lower
            and "relaytic is the general local-first inference lab" in readme_lower
            and "relaytic-aml is the current flagship edition" in readme_lower
            and "docs/paper/relaytic_aml_arxiv_draft.pdf" in readme_lower,
            "A reviewer should learn from the README that Relaytic is the general lab and Relaytic-AML is the current paper focus.",
            "readme_present="
            f"{inputs['readme'].get('exists')}; mentions_pdf={'docs/paper/relaytic_aml_arxiv_draft.pdf' in readme_lower}",
            "README.md",
        ),
        _task(
            "reader_task",
            "cross_platform_reproduction_path_visible",
            "windows powershell" in readme_lower
            and "macos/linux" in readme_lower
            and "release-safety paper-system-eval" in readme_lower
            and "release-safety paper-release" in readme_lower
            and "release-safety paper-arxiv-source" in readme_lower,
            "A reviewer should see compact Windows and macOS/Linux commands for the paper and system-evaluation artifacts.",
            "windows_path="
            f"{'windows powershell' in readme_lower}; unix_path={'macos/linux' in readme_lower}",
            "README.md",
        ),
        _task(
            "reader_task",
            "metric_cell_provenance_available",
            metric_audit.get("status") == "pass"
            and required_metric_fields.issubset(set(pay_comp_cell.keys())),
            "A reviewer should be able to trace the PaySim competitive PR-AUC cell to dataset, split, command, artifact field, budget, leakage posture, and claim state.",
            "audit_status="
            f"{metric_audit.get('status')}; required_fields_present={len(required_metric_fields & set(pay_comp_cell.keys()))}/{len(required_metric_fields)}",
            "docs/reports/paper_metric_cell_audit.json",
        ),
        _task(
            "reader_task",
            "paysim_baseline_and_competitive_budget_comparable",
            pay_improved
            and pay_base_cell.get("dataset_id") == pay_comp_cell.get("dataset_id")
            and pay_base_cell.get("metric_id") == pay_comp_cell.get("metric_id") == "test_pr_auc"
            and pay_base_cell.get("budget_tier") == "baseline"
            and pay_comp_cell.get("budget_tier") == "competitive",
            "A reviewer should be able to compare the PaySim baseline and competitive budgets under the same metric and dataset contract.",
            f"baseline={pay_base_value}; competitive={pay_comp_value}; improved={pay_improved}",
            "docs/reports/paper_metric_cell_audit.json",
        ),
        _task(
            "reader_task",
            "paysim_claim_boundary_machine_readable",
            pay_row.get("supporting_table_allowed") is True
            and pay_row.get("hard_claim_allowed") is False
            and pay_row.get("headline_claim_allowed") is False
            and pay_row.get("performance_contribution_allowed") is False
            and bool(pay_row.get("blocked_reason_codes")),
            "The PaySim row should be usable as supporting evidence while staying blocked from real-bank or headline claims.",
            "supporting="
            f"{pay_row.get('supporting_table_allowed')}; hard={pay_row.get('hard_claim_allowed')}; "
            f"reasons={len(pay_row.get('blocked_reason_codes', []) or [])}",
            "docs/reports/paper_publishability_matrix.json",
        ),
        _task(
            "reader_task",
            "elliptic2_supporting_context_and_firewall_visible",
            elliptic2_context.get("supporting_table_allowed") is True
            and elliptic2_context.get("performance_contribution_allowed") is False
            and elliptic2_firewall.get("gate_status") == "blocked_supporting_only_thesis_narrowing_required",
            "Elliptic2 should be visible as modern context plus a claim firewall, not as a Relaytic performance contribution.",
            "context_role="
            f"{elliptic2_context.get('role')}; firewall_status={elliptic2_firewall.get('gate_status')}",
            "docs/reports/paper_publishability_matrix.json",
        ),
        _task(
            "reader_task",
            "rowless_external_agent_handoff_recoverable",
            handoff_tasks.get("external_context_rowless_and_redacted") is True
            and handoff_tasks.get("safe_next_action_exported") is True
            and handoff_tasks.get("server_tool_contract_available") is True,
            "An external model or agent should receive redacted state, action choices, and tool discovery without raw rows.",
            "rowless="
            f"{handoff_tasks.get('external_context_rowless_and_redacted')}; next_action={handoff_tasks.get('safe_next_action_exported')}; "
            f"tools={handoff_tasks.get('server_tool_contract_available')}",
            "docs/reports/paper_agent_handoff_eval.json",
        ),
        _task(
            "reader_task",
            "partial_run_recovery_without_artifact_literacy",
            no_lost_tasks.get("onboarding_guide_available") is True
            and no_lost_tasks.get("partial_run_state_recovery") is True
            and no_lost_tasks.get("artifact_shortlist_points_to_canonical_state") is True,
            "A new or interrupted user should see onboarding, partial-run state, and a canonical artifact shortlist.",
            "onboarding="
            f"{no_lost_tasks.get('onboarding_guide_available')}; partial={no_lost_tasks.get('partial_run_state_recovery')}; "
            f"shortlist={no_lost_tasks.get('artifact_shortlist_points_to_canonical_state')}",
            "docs/reports/paper_no_lost_user_eval.json",
        ),
        _task(
            "reader_task",
            "claim_gate_fails_closed_for_public_interpretation",
            claim_gate_case_studies.get("status") == "pass"
            and claim_cases.get("p12_go_no_go_blocks_hard_and_headline_claims") is True
            and claim_cases.get("p11_claim_lint_passed") is True,
            "Public paper interpretation should stay below the claim lint and go/no-go gates.",
            "claim_cases_status="
            f"{claim_gate_case_studies.get('status')}; go_no_go={claim_cases.get('p12_go_no_go_blocks_hard_and_headline_claims')}",
            "docs/reports/paper_claim_gate_case_studies.json",
        ),
        _task(
            "reader_task",
            "all_publishability_rows_block_hard_and_headline_claims",
            all_rows_block_hard and len(publishability_rows) >= 5,
            "Every current paper row should keep hard and headline claims blocked until stronger evidence gates pass.",
            f"rows={len(publishability_rows)}; all_blocked={all_rows_block_hard}",
            "docs/reports/paper_publishability_matrix.json",
        ),
        _task(
            "reader_task",
            "result_row_links_metric_cells_and_source_artifacts",
            bool(paysim_result_row)
            and any(
                item.get("cell_id") == "paysim_p6a_competitive_selected.test_pr_auc"
                for item in list(paysim_result_row.get("metrics", []))
                if isinstance(item, dict)
            )
            and "docs/reports/paysim_competitive_benchmark_manifest.json"
            in set(paysim_result_row.get("artifact_refs", []) or []),
            "The result table should connect the reader-facing row to metric cells and source artifacts.",
            "row_present="
            f"{bool(paysim_result_row)}; artifact_refs={len(paysim_result_row.get('artifact_refs', []) or [])}",
            "docs/reports/paper_result_table_final.json",
        ),
    ]
    passed = sum(1 for item in tasks if item["passed"])
    return {
        "schema_version": PAPER_SYSTEM_EVAL_SCHEMA_VERSION,
        "slice": "Paper Track P15",
        "status": "pass" if passed == len(tasks) else "fail",
        "deterministic": True,
        "task_count": len(tasks),
        "passed_task_count": passed,
        "required_task_count": len(tasks),
        "failed_tasks": [item for item in tasks if not item["passed"]],
        "tasks": tasks,
        "interpretation": (
            "This is a deterministic reader/agent task suite. It verifies that the current repo surfaces let a reviewer "
            "navigate the AML paper, trace numeric evidence, understand blocked claims, recover run state, and export "
            "rowless context. It is not a substitute for a controlled human-subject study."
        ),
    }


def _build_system_behavior_eval(
    *,
    no_lost_user_eval: dict[str, Any],
    agent_handoff_eval: dict[str, Any],
    claim_gate_case_studies: dict[str, Any],
    reader_task_eval: dict[str, Any],
) -> dict[str, Any]:
    tasks = [
        *list(no_lost_user_eval.get("tasks", [])),
        *list(agent_handoff_eval.get("tasks", [])),
        *list(claim_gate_case_studies.get("cases", [])),
        *list(reader_task_eval.get("tasks", [])),
    ]
    required_tasks = [item for item in tasks if item.get("required", True)]
    passed_required = [item for item in required_tasks if item.get("passed")]
    evaluation_rows = [
        {
            "track": item.get("track"),
            "task": item.get("task_id") or item.get("case_id"),
            "expected_behavior": item.get("expected_behavior"),
            "measured_signal": item.get("measured_signal"),
            "passed": bool(item.get("passed")),
            "required": bool(item.get("required", True)),
            "source_artifact": item.get("source_artifact"),
        }
        for item in tasks
    ]
    serialized = json.dumps(evaluation_rows, sort_keys=True)
    raw_rows_exposed = "raw_rows_included\": true" in serialized.lower()
    private_paths_exposed = _contains_private_path(serialized)
    status = (
        "pass"
        if required_tasks
        and len(passed_required) == len(required_tasks)
        and not raw_rows_exposed
        and not private_paths_exposed
        else "fail"
    )
    return {
        "schema_version": PAPER_SYSTEM_EVAL_SCHEMA_VERSION,
        "slice": "Paper Track P15",
        "status": status,
        "deterministic": True,
        "task_count": len(tasks),
        "required_task_count": len(required_tasks),
        "passed_required_task_count": len(passed_required),
        "pass_rate": round(len(passed_required) / len(required_tasks), 4) if required_tasks else 0.0,
        "raw_rows_exposed": raw_rows_exposed,
        "private_paths_exposed": private_paths_exposed,
        "surface_count": 6,
        "evaluation_rows": evaluation_rows,
        "interpretation": (
            "These checks are deterministic system-behavior and reader-task evidence. They support the paper's "
            "navigation, provenance, recovery, privacy, agent-handoff, and claim-boundary claims, but they are "
            "not a controlled human-subject study."
        ),
    }


def _build_manifest(
    *,
    root: Path,
    state_root: Path,
    inputs: dict[str, Any],
    surfaces: dict[str, Any],
    no_lost_user_eval: dict[str, Any],
    agent_handoff_eval: dict[str, Any],
    claim_gate_case_studies: dict[str, Any],
    reader_task_eval: dict[str, Any],
    system_behavior_eval: dict[str, Any],
) -> dict[str, Any]:
    required_presence = _required_input_presence(inputs)
    artifact_refs = [
        f"docs/reports/{filename}"
        for filename in PAPER_SYSTEM_EVAL_FILENAMES.values()
    ]
    checks = [
        _check(
            "required_claim_gate_inputs_present",
            not required_presence["missing_artifact_refs"],
            "P15 requires claim-gate artifacts plus README, table, metric-provenance, and publishability inputs.",
            source_artifact="docs/reports",
            detail=required_presence,
        ),
        _check(
            "no_lost_user_eval_passed",
            no_lost_user_eval.get("status") == "pass",
            "Guide and status-like surfaces must prove onboarding and partial-run recovery.",
            source_artifact="docs/reports/paper_no_lost_user_eval.json",
        ),
        _check(
            "agent_handoff_eval_passed",
            agent_handoff_eval.get("status") == "pass",
            "External-agent handoff must be rowless, redacted, discoverable, and action-oriented.",
            source_artifact="docs/reports/paper_agent_handoff_eval.json",
        ),
        _check(
            "claim_gate_case_studies_passed",
            claim_gate_case_studies.get("status") == "pass",
            "Required claim-gate case studies must pass.",
            source_artifact="docs/reports/paper_claim_gate_case_studies.json",
        ),
        _check(
            "reader_task_eval_passed",
            reader_task_eval.get("status") == "pass",
            "Reader and external-agent task evaluation must prove navigation, provenance, handoff, and claim-boundary tasks.",
            source_artifact="docs/reports/paper_system_task_eval.json",
        ),
        _check(
            "system_behavior_eval_passed",
            system_behavior_eval.get("status") == "pass",
            "Aggregate system-behavior evaluation must pass.",
            source_artifact="docs/reports/paper_system_behavior_eval.json",
        ),
        _check(
            "no_raw_rows_or_private_paths_exposed",
            system_behavior_eval.get("raw_rows_exposed") is False
            and system_behavior_eval.get("private_paths_exposed") is False,
            "Committed P15 reports must not expose raw rows or private machine paths.",
            source_artifact="docs/reports/paper_system_behavior_eval.json",
        ),
    ]
    ready = all(check["passed"] for check in checks)
    return {
        "schema_version": PAPER_SYSTEM_EVAL_SCHEMA_VERSION,
        "slice": "Paper Track P15",
        "status": "ready_for_system_evaluation_evidence" if ready else "blocked_pending_system_evaluation_repairs",
        "release_mode": "claim_safe_evaluation_environment_only" if ready else "blocked",
        "system_evaluation_claim_allowed": bool(ready),
        "hard_claims_allowed": False,
        "headline_claims_allowed": False,
        "human_study_claim_allowed": False,
        "state_tree": _state_tree(
            root=root,
            state_root=state_root,
            partial_run=state_root / "partial_run",
            onboarding_dir=state_root / "onboarding",
        ),
        "surface_refs": [
            "relaytic guide --format json",
            "relaytic guide --run-dir <run_dir> --format json",
            "relaytic guide export-context --run-dir <run_dir> --format json",
            "relaytic status --run-dir <run_dir> --format json",
            "relaytic interoperability relaytic_server_info",
        ],
        "artifact_refs": artifact_refs,
        "source_input_refs": REQUIRED_CLAIM_INPUT_REFS + REQUIRED_READER_TASK_INPUT_REFS + OPTIONAL_CLAIM_INPUT_REFS,
        "artifact_hashes": _artifact_hashes(inputs),
        "checks": checks,
        "failed_checks": [check for check in checks if not check["passed"]],
        "next_slice": NEXT_PAPER_SYSTEM_EVAL_SLICE if ready else "Paper Track P15 repair",
        "summary": "P15 turns Relaytic's guide, reader navigation, redacted handoff, interoperability, and claim-gate surfaces into measured paper evidence.",
    }


def _write_partial_run_summary(run_dir: Path) -> None:
    write_json(
        run_dir / "run_summary.json",
        {
            "schema_version": "relaytic.run_summary.v1",
            "run_id": "paper_p15_partial_run",
            "status": "initialized",
            "stage_completed": "profiles_reviewed",
            "headline": "Relaytic prepared a partial AML run and is waiting for more evidence.",
            "request": {
                "actor_type": "user",
                "channel": "paper-system-eval",
                "text_preview": "Review /private/local/data.csv without exposing raw rows.",
            },
            "intent": {
                "objective": "classify suspicious transactions",
                "domain_archetype": "aml",
                "problem_statement": "Find a safe next modeling step for a local AML table.",
                "autonomy_mode": "assisted",
            },
            "decision": {
                "task_type": "classification",
                "target_column": "label",
                "selected_model_family": None,
                "primary_metric": "pr_auc",
                "split_strategy": "temporal",
            },
            "completion": {},
            "handoff": {},
            "lifecycle": {},
            "result_contract": {
                "status": "provisional",
                "recommended_direction": "same_data",
                "overall_confidence": "low",
            },
            "benchmark": {},
            "data": {
                "row_count": 12,
                "column_count": 5,
                "source_format": "csv",
                "source_type": "local_private",
                "copy_enforced": True,
                "immutable_working_copies": True,
            },
        },
        indent=2,
        sort_keys=True,
    )


def _reset_system_eval_state_dirs(*directories: Path) -> None:
    for directory in directories:
        for filename in SYSTEM_EVAL_STATE_FILENAMES:
            path = directory / filename
            if path.is_file():
                path.unlink()


def _call_surface(callable_obj: Any) -> dict[str, Any]:
    try:
        result = callable_obj()
    except Exception as exc:  # pragma: no cover - defensive runtime guard
        return {"status": "error", "error": _sanitize_text(str(exc))}
    payload = dict(result.get("surface_payload", {})) if isinstance(result, dict) else {}
    return _sanitize_surface_payload(payload)


def _sanitize_surface_payload(payload: dict[str, Any]) -> dict[str, Any]:
    allowed = {
        "status",
        "guide",
        "bundle",
        "external_context_pack",
        "external_llm_artifact_index",
        "external_llm_redaction_report",
        "audience",
    }
    return {key: payload[key] for key in allowed if key in payload}


def _safe_server_info(server_info: Any) -> dict[str, Any]:
    payload = dict(server_info) if isinstance(server_info, dict) else {}
    return {
        "status": payload.get("status"),
        "product": payload.get("product"),
        "tool_count": payload.get("tool_count"),
        "inspection_tools": sorted(str(item) for item in list(payload.get("inspection_tools", []) or [])),
        "workflow_tools": sorted(str(item) for item in list(payload.get("workflow_tools", []) or [])),
    }


def _state_tree(*, root: Path, state_root: Path, partial_run: Path, onboarding_dir: Path) -> dict[str, Any]:
    return {
        "state_root": _repo_relative(state_root, root=root, fallback="<external_state_dir>"),
        "partial_run": _repo_relative(partial_run, root=root, fallback="<external_state_dir>/partial_run"),
        "onboarding": _repo_relative(onboarding_dir, root=root, fallback="<external_state_dir>/onboarding"),
        "committed": False,
        "purpose": "temporary deterministic proof fixtures; committed reports contain only rowless summaries",
    }


def _actions(bundle: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        dict(item)
        for item in list(dict(bundle.get("guide_action_menu", {})).get("actions", []))
        if isinstance(item, dict)
    ]


def _artifacts(bundle: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        dict(item)
        for item in list(dict(bundle.get("guide_artifact_shortlist", {})).get("artifacts", []))
        if isinstance(item, dict)
    ]


def _task(
    track: str,
    task_id: str,
    passed: bool,
    expected_behavior: str,
    measured_signal: str,
    source_artifact: str,
) -> dict[str, Any]:
    return {
        "track": track,
        "task_id": task_id,
        "required": True,
        "passed": bool(passed),
        "expected_behavior": expected_behavior,
        "measured_signal": _sanitize_text(measured_signal),
        "source_artifact": source_artifact,
    }


def _case(
    track: str,
    case_id: str,
    passed: bool,
    expected_behavior: str,
    measured_signal: str,
    source_artifact: str,
    *,
    required: bool = True,
    observed: bool = True,
) -> dict[str, Any]:
    effective_passed = bool(passed) if observed else False
    return {
        "track": track,
        "case_id": case_id,
        "required": bool(required),
        "observed": bool(observed),
        "passed": effective_passed,
        "expected_behavior": expected_behavior,
        "measured_signal": _sanitize_text(measured_signal if observed else "optional artifact not present"),
        "source_artifact": source_artifact,
    }


def _task_pass_map(tasks: Any) -> dict[str, bool]:
    return {
        str(item.get("task_id")): bool(item.get("passed"))
        for item in list(tasks or [])
        if isinstance(item, dict) and item.get("task_id")
    }


def _case_pass_map(cases: Any) -> dict[str, bool]:
    return {
        str(item.get("case_id")): bool(item.get("passed"))
        for item in list(cases or [])
        if isinstance(item, dict) and item.get("case_id")
    }


def _find_metric_cell(metric_audit: dict[str, Any], cell_id: str) -> dict[str, Any]:
    for cell in list(metric_audit.get("numeric_cells", [])) + list(metric_audit.get("blocked_or_empty_cells", [])):
        if isinstance(cell, dict) and cell.get("cell_id") == cell_id:
            return dict(cell)
    return {}


def _find_result_row(result_table: dict[str, Any], row_id: str) -> dict[str, Any]:
    for group in list(result_table.get("table_groups", [])):
        if not isinstance(group, dict):
            continue
        for row in list(group.get("rows", [])):
            if isinstance(row, dict) and row.get("row_id") == row_id:
                return dict(row)
    return {}


def _find_publishability_row(
    publishability: dict[str, Any],
    *,
    dataset_id: str,
    role: str | None = None,
) -> dict[str, Any]:
    for row in list(publishability.get("rows", [])):
        if not isinstance(row, dict) or row.get("dataset_id") != dataset_id:
            continue
        if role is not None and row.get("role") != role:
            continue
        return dict(row)
    return {}


def _required_input_presence(inputs: dict[str, Any]) -> dict[str, Any]:
    artifacts_by_ref = {
        str(value.get("artifact_ref")): value
        for value in inputs.values()
        if isinstance(value, dict) and value.get("artifact_ref")
    }
    present = []
    missing = []
    for ref in REQUIRED_CLAIM_INPUT_REFS + REQUIRED_READER_TASK_INPUT_REFS:
        artifact = artifacts_by_ref.get(ref)
        if artifact and artifact.get("exists"):
            present.append(ref)
        else:
            missing.append(ref)
    return {"present_artifact_refs": present, "missing_artifact_refs": missing}


def _artifact_hashes(inputs: dict[str, Any]) -> dict[str, str]:
    hashes = {}
    for value in inputs.values():
        if not isinstance(value, dict) or not value.get("exists") or not value.get("sha256"):
            continue
        if value.get("artifact_ref") not in REQUIRED_CLAIM_INPUT_REFS + REQUIRED_READER_TASK_INPUT_REFS:
            continue
        hashes[str(value["artifact_ref"])] = str(value["sha256"])
    return hashes


def _read_artifact(path: Path, *, root: Path) -> dict[str, Any]:
    artifact_ref = _repo_relative(path, root=root)
    if not path.is_file():
        return {"artifact_ref": artifact_ref, "exists": False, "payload": {}}
    text = path.read_text(encoding="utf-8")
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        payload = {"error": _sanitize_text(str(exc))}
    return {
        "artifact_ref": artifact_ref,
        "exists": True,
        "sha256": _sha256_text(text),
        "payload": payload if isinstance(payload, dict) else {},
    }


def _read_text_artifact(path: Path, *, root: Path) -> dict[str, Any]:
    artifact_ref = _repo_relative(path, root=root)
    if not path.is_file():
        return {"artifact_ref": artifact_ref, "exists": False, "payload": ""}
    text = path.read_text(encoding="utf-8")
    return {
        "artifact_ref": artifact_ref,
        "exists": True,
        "sha256": _sha256_text(text),
        "payload": text,
    }


def _payload(artifact: dict[str, Any]) -> dict[str, Any]:
    payload = artifact.get("payload", {})
    return dict(payload) if isinstance(payload, dict) else {}


def _text_payload(artifact: dict[str, Any]) -> str:
    payload = artifact.get("payload", "")
    return str(payload) if isinstance(payload, str) else ""


def _check(
    check_id: str,
    passed: bool,
    message: str,
    *,
    source_artifact: str,
    detail: dict[str, Any] | None = None,
) -> dict[str, Any]:
    result: dict[str, Any] = {
        "check_id": check_id,
        "passed": bool(passed),
        "message": message,
        "source_artifact": source_artifact,
    }
    if detail is not None:
        result["detail"] = detail
    return result


def _repo_relative(path: Path, *, root: Path, fallback: str | None = None) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except (OSError, ValueError):
        if fallback is not None:
            return fallback
    parts = path.parts
    for marker in ("docs", "artifacts", "src", "tests", ".github"):
        if marker in parts:
            return Path(*parts[parts.index(marker) :]).as_posix()
    return fallback or path.name


def _contains_private_path(text: str) -> bool:
    return bool(
        re.search(r"[A-Za-z]:[\\/]", text)
        or re.search(r"(?<![A-Za-z0-9])/(?:Users|home|private|tmp|var/folders)/", text)
        or re.search(r"C:/Users|C:\\Users|\\Users\\", text, re.IGNORECASE)
    )


def _sanitize_text(text: Any) -> str:
    cleaned = str(text)
    cleaned = re.sub(r"[A-Za-z]:[\\/][^\s`\"']+", _path_redaction, cleaned)
    cleaned = re.sub(r"/(?:Users|home|private|tmp|var/folders)/[^\s`\"']+", _path_redaction, cleaned)
    cleaned = re.sub(r"(?i)(api[_-]?key|token|secret)\s*[:=]\s*[A-Za-z0-9_\-]{8,}", r"\1=<redacted_secret>", cleaned)
    return cleaned


def _path_redaction(match: re.Match[str]) -> str:
    raw = match.group(0).replace("\\", "/")
    name = Path(raw).name
    return f"<redacted_path:{name or 'local'}>"


def _escape_md(text: str) -> str:
    return text.replace("|", "\\|").replace("\n", " ")


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


__all__ = [
    "NEXT_PAPER_SYSTEM_EVAL_SLICE",
    "PAPER_SYSTEM_EVAL_FILENAMES",
    "PAPER_SYSTEM_EVAL_REPORT_DIR",
    "PAPER_SYSTEM_EVAL_SCHEMA_VERSION",
    "PAPER_SYSTEM_EVAL_STATE_DIR",
    "build_paper_system_eval_pack",
    "render_paper_system_eval_markdown",
    "sync_paper_system_eval_pack",
]
