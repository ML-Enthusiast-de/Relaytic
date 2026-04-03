"""Slice 13B visible permission modes and approval posture."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any
from uuid import uuid4

from relaytic.events import run_event_bus_review
from relaytic.runtime import build_runtime_surface, read_runtime_bundle, record_runtime_event

from .models import (
    APPROVAL_POLICY_REPORT_SCHEMA_VERSION,
    PERMISSION_DECISION_LOG_SCHEMA_VERSION,
    PERMISSION_MODE_SCHEMA_VERSION,
    SESSION_CAPABILITY_CONTRACT_SCHEMA_VERSION,
    TOOL_PERMISSION_MATRIX_SCHEMA_VERSION,
    ApprovalPolicyReportArtifact,
    PermissionBundle,
    PermissionControls,
    PermissionModeArtifact,
    PermissionTrace,
    SessionCapabilityContractArtifact,
    ToolPermissionMatrixArtifact,
)
from .storage import (
    PERMISSION_DECISION_LOG_FILENAME,
    append_permission_decision,
    read_permission_decision_log,
    write_permission_bundle,
)


@dataclass(frozen=True)
class PermissionRunResult:
    bundle: PermissionBundle
    review_markdown: str


@dataclass(frozen=True)
class PermissionDecisionResult:
    bundle: PermissionBundle
    decision: dict[str, Any]
    review_markdown: str


_ACTION_CATALOG: tuple[dict[str, Any], ...] = (
    {
        "tool_id": "relaytic_show_run",
        "label": "Inspect run summary",
        "category": "inspection",
        "cli_hint": "relaytic show --run-dir <run_dir>",
        "mcp_tool": "relaytic_show_run",
        "statuses_by_mode": {"review": "allowed", "plan": "allowed", "safe_execute": "allowed", "bounded_autonomy": "allowed"},
        "reason_codes": {"allowed": "read_only_surface"},
    },
    {
        "tool_id": "relaytic_show_runtime",
        "label": "Inspect runtime state",
        "category": "inspection",
        "cli_hint": "relaytic runtime show --run-dir <run_dir>",
        "mcp_tool": "relaytic_show_runtime",
        "statuses_by_mode": {"review": "allowed", "plan": "allowed", "safe_execute": "allowed", "bounded_autonomy": "allowed"},
        "reason_codes": {"allowed": "read_only_surface"},
    },
    {
        "tool_id": "relaytic_run",
        "label": "Start governed run",
        "category": "workflow",
        "cli_hint": "relaytic run --run-dir <run_dir> --data-path <path> --text <objective>",
        "mcp_tool": "relaytic_run",
        "statuses_by_mode": {"review": "approval_required", "plan": "approval_required", "safe_execute": "allowed", "bounded_autonomy": "allowed"},
        "reason_codes": {
            "approval_required": "governed_run_requires_explicit_confirmation_in_review",
            "allowed": "governed_run_allowed_in_execution_modes",
        },
    },
    {
        "tool_id": "relaytic_review_search",
        "label": "Run search controller",
        "category": "workflow",
        "cli_hint": "relaytic search review --run-dir <run_dir>",
        "mcp_tool": "relaytic_review_search",
        "statuses_by_mode": {"review": "approval_required", "plan": "approval_required", "safe_execute": "allowed", "bounded_autonomy": "allowed"},
        "reason_codes": {
            "approval_required": "search_expansion_is_review_gated",
            "allowed": "search_review_is_allowed_in_execution_modes",
        },
    },
    {
        "tool_id": "relaytic_run_background_search",
        "label": "Run background search campaign",
        "category": "background",
        "cli_hint": "relaytic daemon run-job --run-dir <run_dir> --job-id job_search_campaign",
        "mcp_tool": "relaytic_run_background_job",
        "statuses_by_mode": {"review": "approval_required", "plan": "approval_required", "safe_execute": "allowed", "bounded_autonomy": "allowed"},
        "reason_codes": {
            "approval_required": "background_search_requires_explicit_review_in_non_execution_modes",
            "allowed": "background_search_is_allowed_in_execution_modes",
        },
    },
    {
        "tool_id": "relaytic_run_memory_maintenance",
        "label": "Run memory maintenance",
        "category": "background",
        "cli_hint": "relaytic daemon run-job --run-dir <run_dir> --job-id job_memory_maintenance",
        "mcp_tool": "relaytic_run_background_job",
        "statuses_by_mode": {"review": "approval_required", "plan": "approval_required", "safe_execute": "allowed", "bounded_autonomy": "allowed"},
        "reason_codes": {
            "approval_required": "background_memory_maintenance_stays_review_gated_outside_execution_modes",
            "allowed": "background_memory_maintenance_is_allowed_in_execution_modes",
        },
    },
    {
        "tool_id": "relaytic_run_pulse_followup",
        "label": "Run pulse follow-up",
        "category": "background",
        "cli_hint": "relaytic daemon run-job --run-dir <run_dir> --job-id job_pulse_followup",
        "mcp_tool": "relaytic_run_background_job",
        "statuses_by_mode": {"review": "approval_required", "plan": "approval_required", "safe_execute": "allowed", "bounded_autonomy": "allowed"},
        "reason_codes": {
            "approval_required": "background_pulse_followup_requires_review_outside_execution_modes",
            "allowed": "background_pulse_followup_is_allowed_in_execution_modes",
        },
    },
    {
        "tool_id": "relaytic_run_background_benchmark",
        "label": "Run background benchmark campaign",
        "category": "background",
        "cli_hint": "relaytic daemon run-job --run-dir <run_dir> --job-id job_benchmark_campaign",
        "mcp_tool": "relaytic_run_background_job",
        "statuses_by_mode": {"review": "approval_required", "plan": "approval_required", "safe_execute": "allowed", "bounded_autonomy": "allowed"},
        "reason_codes": {
            "approval_required": "background_benchmark_requires_review_outside_execution_modes",
            "allowed": "background_benchmark_is_allowed_in_execution_modes",
        },
    },
    {
        "tool_id": "relaytic_run_autonomy",
        "label": "Run autonomy follow-up",
        "category": "workflow",
        "cli_hint": "relaytic autonomy run --run-dir <run_dir>",
        "mcp_tool": "relaytic_run_autonomy",
        "statuses_by_mode": {"review": "approval_required", "plan": "blocked", "safe_execute": "approval_required", "bounded_autonomy": "allowed"},
        "reason_codes": {
            "approval_required": "autonomy_requires_approval_outside_bounded_autonomy",
            "blocked": "autonomy_not_available_during_plan_only_mode",
            "allowed": "bounded_autonomy_allows_followup_loop",
        },
    },
    {
        "tool_id": "relaytic_continue_workspace",
        "label": "Continue workspace",
        "category": "workflow",
        "cli_hint": "relaytic workspace continue --run-dir <run_dir> --direction same_data",
        "mcp_tool": "relaytic_continue_workspace",
        "statuses_by_mode": {"review": "allowed", "plan": "allowed", "safe_execute": "allowed", "bounded_autonomy": "allowed"},
        "reason_codes": {"allowed": "workspace_continuity_is_always_visible"},
    },
    {
        "tool_id": "relaytic_reset_learnings",
        "label": "Reset learnings",
        "category": "workflow",
        "cli_hint": "relaytic learnings reset --run-dir <run_dir>",
        "mcp_tool": "relaytic_reset_learnings",
        "statuses_by_mode": {"review": "approval_required", "plan": "approval_required", "safe_execute": "allowed", "bounded_autonomy": "allowed"},
        "reason_codes": {
            "approval_required": "state_reset_is_review_gated",
            "allowed": "state_reset_is_explicit_in_execution_modes",
        },
    },
    {
        "tool_id": "runtime_write_hook",
        "label": "Enable write-capable runtime hook",
        "category": "runtime",
        "cli_hint": "policy runtime.allow_write_hooks=true",
        "mcp_tool": "runtime_write_hook",
        "statuses_by_mode": {"review": "blocked", "plan": "blocked", "safe_execute": "approval_required", "bounded_autonomy": "approval_required"},
        "reason_codes": {
            "blocked": "write_hooks_stay_disabled_in_review_or_plan",
            "approval_required": "write_hooks_require_explicit_policy_confirmation",
        },
    },
    {
        "tool_id": "remote_supervision",
        "label": "Open remote supervision channel",
        "category": "remote",
        "cli_hint": "reserved for Slice 14A",
        "mcp_tool": "remote_supervision",
        "statuses_by_mode": {"review": "blocked", "plan": "blocked", "safe_execute": "blocked", "bounded_autonomy": "blocked"},
        "reason_codes": {"blocked": "remote_supervision_not_shipped_yet"},
    },
)

_ACTION_ALIASES = {
    "show_run": "relaytic_show_run",
    "show_runtime": "relaytic_show_runtime",
    "run": "relaytic_run",
    "review_search": "relaytic_review_search",
    "search_review": "relaytic_review_search",
    "run_background_search": "relaytic_run_background_search",
    "run_memory_maintenance": "relaytic_run_memory_maintenance",
    "run_pulse_followup": "relaytic_run_pulse_followup",
    "run_background_benchmark": "relaytic_run_background_benchmark",
    "run_autonomy_followup": "relaytic_run_autonomy",
    "autonomy": "relaytic_run_autonomy",
    "continue_workspace": "relaytic_continue_workspace",
    "reset_learnings": "relaytic_reset_learnings",
}


def build_permission_controls_from_policy(policy: dict[str, Any]) -> PermissionControls:
    cfg = dict(policy.get("permissions", {}))
    default_mode = str(cfg.get("default_mode", "bounded_autonomy") or "bounded_autonomy").strip().lower()
    if default_mode not in {"review", "plan", "safe_execute", "bounded_autonomy"}:
        default_mode = "bounded_autonomy"
    return PermissionControls(
        enabled=bool(cfg.get("enabled", True)),
        default_mode=default_mode,
        require_review_for_high_impact_actions=bool(cfg.get("require_review_for_high_impact_actions", True)),
        allow_remote_actions=bool(cfg.get("allow_remote_actions", False)),
        max_recent_decisions=max(10, int(cfg.get("max_recent_decisions", 40) or 40)),
    )


def run_permission_review(
    *,
    run_dir: str | Path,
    policy: dict[str, Any] | None = None,
) -> PermissionRunResult:
    root = Path(run_dir)
    run_event_bus_review(run_dir=root, policy=policy or {})
    runtime_bundle = read_runtime_bundle(root)
    capability_profiles = dict(runtime_bundle.get("capability_profiles", {}))
    controls = build_permission_controls_from_policy(policy or {})
    current_mode, mode_source, review_reason = _resolve_current_mode(root=root, policy=policy or {})
    decision_log = read_permission_decision_log(root)
    pending = _pending_requests(decision_log)
    trace = PermissionTrace(
        agent="permission_controller",
        mode_source=mode_source,
        authority_model="explicit_mode_matrix",
        advisory_notes=[
            "Permission posture stays visible from one mode artifact, one matrix, and one append-only decision log.",
            "Approval requests and denials are replayable from the permission log plus the canonical runtime event stream.",
        ],
    )
    tools = _materialize_tool_matrix(
        current_mode=current_mode,
        pending_requests=pending,
        allow_remote_actions=controls.allow_remote_actions,
    )
    recent_decisions = decision_log[-controls.max_recent_decisions :]
    pending_payload = [
        {
            "request_id": request_id,
            "action_id": item.get("action_id"),
            "action_label": item.get("action_label"),
            "requested_at": item.get("recorded_at"),
            "evaluated_mode": item.get("evaluated_mode"),
            "source_surface": item.get("source_surface"),
            "summary": item.get("summary"),
        }
        for request_id, item in pending.items()
    ]
    allowed = [item["tool_id"] for item in tools if item.get("current_status") == "allowed"]
    approval_gated = [item["tool_id"] for item in tools if item.get("current_status") == "approval_required"]
    blocked = [item["tool_id"] for item in tools if item.get("current_status") == "blocked"]
    bundle = PermissionBundle(
        permission_mode=PermissionModeArtifact(
            schema_version=PERMISSION_MODE_SCHEMA_VERSION,
            generated_at=_utc_now(),
            controls=controls,
            status="ok",
            current_mode=current_mode,
            mode_source=mode_source,
            pending_approval_count=len(pending_payload),
            pending_request_ids=list(pending.keys()),
            review_reason=review_reason,
            summary=f"Relaytic is operating in `{current_mode}` with `{len(pending_payload)}` pending approval request(s).",
            trace=trace,
        ),
        tool_permission_matrix=ToolPermissionMatrixArtifact(
            schema_version=TOOL_PERMISSION_MATRIX_SCHEMA_VERSION,
            generated_at=_utc_now(),
            controls=controls,
            status="ok",
            current_mode=current_mode,
            tool_count=len(tools),
            tools=tools,
            summary=f"Relaytic currently exposes {len(tools)} tool or action permission rows for mode `{current_mode}`.",
            trace=trace,
        ),
        approval_policy_report=ApprovalPolicyReportArtifact(
            schema_version=APPROVAL_POLICY_REPORT_SCHEMA_VERSION,
            generated_at=_utc_now(),
            controls=controls,
            status="ok",
            current_mode=current_mode,
            pending_approval_count=len(pending_payload),
            approval_requested_count=sum(1 for item in decision_log if str(item.get('decision', '')) == "approval_requested"),
            denied_count=sum(1 for item in decision_log if str(item.get('decision', '')) in {"blocked", "denied"}),
            recent_decisions=recent_decisions,
            pending_approvals=pending_payload,
            summary=f"Relaytic has `{len(pending_payload)}` pending approval(s) and `{sum(1 for item in decision_log if str(item.get('decision', '')) in {'blocked', 'denied'})}` blocked or denied action(s).",
            trace=trace,
        ),
        session_capability_contract=SessionCapabilityContractArtifact(
            schema_version=SESSION_CAPABILITY_CONTRACT_SCHEMA_VERSION,
            generated_at=_utc_now(),
            controls=controls,
            status="ok",
            current_mode=current_mode,
            active_specialist_count=len(capability_profiles.get("profiles", []))
            if isinstance(capability_profiles.get("profiles"), list)
            else 0,
            allowed_action_count=len(allowed),
            approval_gated_action_count=len(approval_gated),
            blocked_action_count=len(blocked),
            actions_by_status={"allowed": allowed, "approval_required": approval_gated, "blocked": blocked},
            paths={
                "event_schema": str(root / "event_schema.json"),
                "event_subscription_registry": str(root / "event_subscription_registry.json"),
                "hook_registry": str(root / "hook_registry.json"),
                "permission_decision_log": str(root / PERMISSION_DECISION_LOG_FILENAME),
                "session_capability_contract": str(root / "session_capability_contract.json"),
            },
            summary=f"Relaytic session capability contract exposes `{len(allowed)}` allowed, `{len(approval_gated)}` approval-gated, and `{len(blocked)}` blocked action(s) in mode `{current_mode}`.",
            trace=trace,
        ),
    )
    write_permission_bundle(root, bundle=bundle)
    return PermissionRunResult(bundle=bundle, review_markdown=render_permission_markdown(bundle))


def evaluate_permission_action(
    *,
    run_dir: str | Path,
    action_id: str,
    policy: dict[str, Any] | None = None,
    mode_override: str | None = None,
    actor_type: str = "operator",
    actor_name: str | None = None,
    source_surface: str = "cli",
    source_command: str = "relaytic permissions check",
) -> PermissionDecisionResult:
    root = Path(run_dir)
    review = run_permission_review(run_dir=root, policy=policy or {})
    permission_mode = dict(review.bundle.to_dict().get("permission_mode", {}))
    normalized_action = _normalize_action_id(action_id)
    evaluated_mode = _normalize_mode(mode_override) or str(permission_mode.get("current_mode", "review")).strip() or "review"
    entry = _catalog_entry(normalized_action)
    current_status = str(dict(entry.get("statuses_by_mode", {})).get(evaluated_mode, "blocked"))
    decision = "allowed" if current_status == "allowed" else ("approval_requested" if current_status == "approval_required" else "blocked")
    request_id = _identifier("approval") if decision == "approval_requested" else None
    log_entry = {
        "schema_version": PERMISSION_DECISION_LOG_SCHEMA_VERSION,
        "decision_id": _identifier("perm"),
        "recorded_at": _utc_now(),
        "request_id": request_id,
        "action_id": normalized_action,
        "action_label": entry.get("label"),
        "evaluated_mode": evaluated_mode,
        "decision": decision,
        "source_surface": source_surface,
        "source_command": source_command,
        "actor_type": str(actor_type or "operator").strip().lower() or "operator",
        "actor_name": actor_name,
        "reason_code": dict(entry.get("reason_codes", {})).get(current_status, "permission_matrix_rule"),
        "summary": _decision_summary(label=str(entry.get("label", normalized_action)), decision=decision, evaluated_mode=evaluated_mode),
    }
    append_permission_decision(root, entry=log_entry)
    runtime = build_runtime_surface(run_dir=root)
    stage = str(dict(runtime.get("runtime", {})).get("current_stage", "")).strip() or "runtime"
    record_runtime_event(
        run_dir=root,
        policy=policy or {},
        event_type="approval_requested" if decision == "approval_requested" else ("approval_denied" if decision == "blocked" else "permission_allowed"),
        stage=stage,
        source_surface=source_surface,
        source_command=source_command,
        status="pending_approval" if decision == "approval_requested" else ("blocked" if decision == "blocked" else "ok"),
        summary=log_entry["summary"],
        metadata={"action_id": normalized_action, "evaluated_mode": evaluated_mode, "request_id": request_id},
    )
    refreshed = run_permission_review(run_dir=root, policy=policy or {})
    return PermissionDecisionResult(bundle=refreshed.bundle, decision=log_entry, review_markdown=render_permission_markdown(refreshed.bundle))


def apply_permission_decision(
    *,
    run_dir: str | Path,
    request_id: str,
    decision: str,
    policy: dict[str, Any] | None = None,
    actor_type: str = "operator",
    actor_name: str | None = None,
    source_surface: str = "cli",
    source_command: str = "relaytic permissions decide",
) -> PermissionDecisionResult:
    root = Path(run_dir)
    normalized_decision = str(decision or "").strip().lower()
    if normalized_decision not in {"approve", "deny"}:
        raise ValueError("Permission decision must be `approve` or `deny`.")
    pending = _pending_requests(read_permission_decision_log(root))
    if request_id not in pending:
        raise ValueError(f"Pending approval request not found: {request_id}")
    requested = pending[request_id]
    log_entry = {
        "schema_version": PERMISSION_DECISION_LOG_SCHEMA_VERSION,
        "decision_id": _identifier("perm"),
        "recorded_at": _utc_now(),
        "request_id": request_id,
        "action_id": requested.get("action_id"),
        "action_label": requested.get("action_label"),
        "evaluated_mode": requested.get("evaluated_mode"),
        "decision": "approved" if normalized_decision == "approve" else "denied",
        "source_surface": source_surface,
        "source_command": source_command,
        "actor_type": str(actor_type or "operator").strip().lower() or "operator",
        "actor_name": actor_name,
        "reason_code": "explicit_approval" if normalized_decision == "approve" else "explicit_denial",
        "summary": f"Relaytic marked approval request `{request_id}` as `{'approved' if normalized_decision == 'approve' else 'denied'}`.",
    }
    append_permission_decision(root, entry=log_entry)
    runtime = build_runtime_surface(run_dir=root)
    stage = str(dict(runtime.get("runtime", {})).get("current_stage", "")).strip() or "runtime"
    record_runtime_event(
        run_dir=root,
        policy=policy or {},
        event_type="approval_approved" if normalized_decision == "approve" else "approval_denied",
        stage=stage,
        source_surface=source_surface,
        source_command=source_command,
        status="ok" if normalized_decision == "approve" else "blocked",
        summary=log_entry["summary"],
        metadata={"action_id": requested.get("action_id"), "request_id": request_id},
    )
    refreshed = run_permission_review(run_dir=root, policy=policy or {})
    return PermissionDecisionResult(bundle=refreshed.bundle, decision=log_entry, review_markdown=render_permission_markdown(refreshed.bundle))


def render_permission_markdown(bundle: PermissionBundle | dict[str, Any]) -> str:
    payload = bundle.to_dict() if isinstance(bundle, PermissionBundle) else dict(bundle)
    mode = dict(payload.get("permission_mode", {}))
    matrix = dict(payload.get("tool_permission_matrix", {}))
    approval = dict(payload.get("approval_policy_report", {}))
    contract = dict(payload.get("session_capability_contract", {}))
    lines = [
        "# Relaytic Permission Modes",
        "",
        f"- Current mode: `{mode.get('current_mode', 'unknown')}`",
        f"- Mode source: `{mode.get('mode_source', 'unknown')}`",
        f"- Pending approvals: `{approval.get('pending_approval_count', 0)}`",
        f"- Allowed actions: `{contract.get('allowed_action_count', 0)}`",
        f"- Approval-gated actions: `{contract.get('approval_gated_action_count', 0)}`",
        f"- Blocked actions: `{contract.get('blocked_action_count', 0)}`",
    ]
    for item in list(approval.get("pending_approvals", []))[:6]:
        lines.append(f"- Pending `{item.get('request_id')}` for `{item.get('action_id')}` at mode `{item.get('evaluated_mode')}`")
    for item in list(matrix.get("tools", []))[:8]:
        lines.append(f"- `{item.get('tool_id')}` -> `{item.get('current_status')}` in mode `{mode.get('current_mode')}`")
    return "\n".join(lines).rstrip() + "\n"


def _resolve_current_mode(*, root: Path, policy: dict[str, Any]) -> tuple[str, str, str | None]:
    if not root.exists():
        return "review", "missing_run_directory", "No run directory exists yet, so Relaytic stays in review mode."
    result_contract = _safe_read_json(root / "result_contract.json")
    confidence_posture = _safe_read_json(root / "confidence_posture.json")
    runtime = build_runtime_surface(run_dir=root)
    stage = str(dict(runtime.get("runtime", {})).get("current_stage", "")).strip()
    review_need = str(result_contract.get("review_need", "")).strip().lower() or str(confidence_posture.get("review_need", "")).strip().lower()
    if review_need == "required" or str(result_contract.get("status", "")).strip().lower() in {"blocked", "needs_review"}:
        return "review", "result_contract_review_need", "Result contract currently requires review."
    if stage in {"initialized", "intake", "investigation", "memory", "planning"} or ((root / "plan.json").exists() and not (root / "completion_decision.json").exists()):
        return "plan", "runtime_stage", "Relaytic is still in an early planning or investigation phase."
    if bool(dict(policy.get("autonomy", {})).get("allow_auto_run", True)):
        return "bounded_autonomy", "autonomy_policy_default", None
    return "safe_execute", "policy_default", None


def _materialize_tool_matrix(*, current_mode: str, pending_requests: dict[str, dict[str, Any]], allow_remote_actions: bool) -> list[dict[str, Any]]:
    pending_by_action = {str(item.get("action_id")): item for item in pending_requests.values()}
    tools: list[dict[str, Any]] = []
    for entry in _ACTION_CATALOG:
        tool_id = str(entry.get("tool_id"))
        statuses = dict(entry.get("statuses_by_mode", {}))
        if not allow_remote_actions and tool_id == "remote_supervision":
            statuses = {mode: "blocked" for mode in statuses}
        current_status = str(statuses.get(current_mode, "blocked"))
        pending = pending_by_action.get(tool_id)
        tools.append(
            {
                "tool_id": tool_id,
                "label": entry.get("label"),
                "category": entry.get("category"),
                "cli_hint": entry.get("cli_hint"),
                "mcp_tool": entry.get("mcp_tool"),
                "statuses_by_mode": statuses,
                "current_status": current_status,
                "current_reason_code": dict(entry.get("reason_codes", {})).get(current_status, "permission_matrix_rule"),
                "pending_request_id": pending.get("request_id") if pending else None,
            }
        )
    return tools


def _pending_requests(entries: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    pending: dict[str, dict[str, Any]] = {}
    for item in entries:
        request_id = str(item.get("request_id", "")).strip()
        if not request_id:
            continue
        decision = str(item.get("decision", "")).strip()
        if decision == "approval_requested":
            pending[request_id] = item
        elif decision in {"approved", "denied"} and request_id in pending:
            pending.pop(request_id, None)
    return pending


def _normalize_action_id(action_id: str) -> str:
    normalized = str(action_id or "").strip()
    if not normalized:
        raise ValueError("Action id is required.")
    return _ACTION_ALIASES.get(normalized, normalized)


def _normalize_mode(mode: str | None) -> str | None:
    if mode is None:
        return None
    normalized = str(mode).strip().lower()
    if normalized not in {"review", "plan", "safe_execute", "bounded_autonomy"}:
        raise ValueError("Mode must be one of `review`, `plan`, `safe_execute`, or `bounded_autonomy`.")
    return normalized


def _catalog_entry(action_id: str) -> dict[str, Any]:
    for entry in _ACTION_CATALOG:
        if str(entry.get("tool_id")) == action_id:
            return dict(entry)
    supported = ", ".join(sorted(str(item.get("tool_id")) for item in _ACTION_CATALOG))
    raise ValueError(f"Unsupported action `{action_id}`. Supported actions: {supported}")


def _decision_summary(*, label: str, decision: str, evaluated_mode: str) -> str:
    if decision == "approval_requested":
        return f"Relaytic requested approval for `{label}` while operating in `{evaluated_mode}`."
    if decision == "blocked":
        return f"Relaytic blocked `{label}` while operating in `{evaluated_mode}`."
    return f"Relaytic allowed `{label}` while operating in `{evaluated_mode}`."


def _safe_read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return loaded if isinstance(loaded, dict) else {}


def _identifier(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex[:12]}"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()
