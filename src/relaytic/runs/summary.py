"""MVP run-summary and report helpers for human and agent access surfaces."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from relaytic.core.json_utils import write_json


RUN_SUMMARY_SCHEMA_VERSION = "relaytic.run_summary.v1"
RUN_SUMMARY_FILENAME = "run_summary.json"
RUN_REPORT_RELATIVE_PATH = Path("reports") / "summary.md"


def read_run_summary(run_dir: str | Path) -> dict[str, Any]:
    """Read a persisted run summary if present."""
    path = Path(run_dir) / RUN_SUMMARY_FILENAME
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def build_run_summary(
    *,
    run_dir: str | Path,
    data_path: str | Path | None = None,
    request_source: str | None = None,
    request_text: str | None = None,
) -> dict[str, Any]:
    """Build a machine-readable summary for a Relaytic run directory."""
    root = Path(run_dir)
    mandate_bundle = _read_bundle(
        root,
        {
            "lab_mandate": "lab_mandate.json",
            "work_preferences": "work_preferences.json",
            "run_brief": "run_brief.json",
        },
    )
    context_bundle = _read_bundle(
        root,
        {
            "data_origin": "data_origin.json",
            "domain_brief": "domain_brief.json",
            "task_brief": "task_brief.json",
        },
    )
    intake_bundle = _read_bundle(
        root,
        {
            "intake_record": "intake_record.json",
            "autonomy_mode": "autonomy_mode.json",
            "clarification_queue": "clarification_queue.json",
            "assumption_log": "assumption_log.json",
            "context_interpretation": "context_interpretation.json",
        },
    )
    investigation_bundle = _read_bundle(
        root,
        {
            "dataset_profile": "dataset_profile.json",
            "domain_memo": "domain_memo.json",
            "focus_profile": "focus_profile.json",
            "optimization_profile": "optimization_profile.json",
        },
    )
    planning_bundle = _read_bundle(
        root,
        {
            "plan": "plan.json",
            "alternatives": "alternatives.json",
            "hypotheses": "hypotheses.json",
            "experiment_priority_report": "experiment_priority_report.json",
            "marginal_value_of_next_experiment": "marginal_value_of_next_experiment.json",
        },
    )
    evidence_bundle = _read_bundle(
        root,
        {
            "experiment_registry": "experiment_registry.json",
            "challenger_report": "challenger_report.json",
            "ablation_report": "ablation_report.json",
            "audit_report": "audit_report.json",
            "belief_update": "belief_update.json",
        },
    )
    model_params = _read_json(root / "model_params.json")
    manifest = _read_json(root / "manifest.json")

    run_brief = _bundle_item(mandate_bundle, "run_brief")
    task_brief = _bundle_item(context_bundle, "task_brief")
    domain_brief = _bundle_item(context_bundle, "domain_brief")
    autonomy_mode = _bundle_item(intake_bundle, "autonomy_mode")
    intake_record = _bundle_item(intake_bundle, "intake_record")
    assumption_entries = list(_bundle_item(intake_bundle, "assumption_log").get("entries", []))
    focus_profile = _bundle_item(investigation_bundle, "focus_profile")
    dataset_profile = _bundle_item(investigation_bundle, "dataset_profile")
    plan = _bundle_item(planning_bundle, "plan")
    experiment_registry = _bundle_item(evidence_bundle, "experiment_registry")
    challenger_report = _bundle_item(evidence_bundle, "challenger_report")
    ablation_report = _bundle_item(evidence_bundle, "ablation_report")
    audit_report = _bundle_item(evidence_bundle, "audit_report")
    belief_update = _bundle_item(evidence_bundle, "belief_update")
    execution_summary = dict(plan.get("execution_summary") or {})
    builder_handoff = dict(plan.get("builder_handoff") or {})
    marginal_value = _bundle_item(planning_bundle, "marginal_value_of_next_experiment")

    resolved_data_path = (
        str(Path(data_path))
        if data_path is not None
        else _first_data_reference(builder_handoff)
        or ""
    )
    selected_metrics = execution_summary.get("selected_metrics")
    if not isinstance(selected_metrics, dict):
        selected_metrics = {}
    summary = {
        "schema_version": RUN_SUMMARY_SCHEMA_VERSION,
        "generated_at": _utc_now(),
        "product": "Relaytic",
        "run_id": str(manifest.get("run_id", root.name or "run")),
        "run_dir": str(root),
        "status": _resolve_run_status(
            plan=plan,
            execution_summary=execution_summary,
            audit_report=audit_report,
        ),
        "stage_completed": _resolve_stage(
            plan=plan,
            execution_summary=execution_summary,
            investigation_bundle=investigation_bundle,
            intake_bundle=intake_bundle,
            evidence_bundle=evidence_bundle,
        ),
        "request": {
            "source": request_source or str(intake_record.get("message_source", "")).strip() or "unknown",
            "text_preview": _preview_text(request_text) or _preview_text(intake_record.get("message")),
            "actor_type": str(intake_record.get("actor_type", "")).strip() or None,
            "actor_name": str(intake_record.get("actor_name", "")).strip() or None,
            "channel": str(intake_record.get("channel", "")).strip() or None,
        },
        "data": {
            "data_path": resolved_data_path,
            "row_count": int(dataset_profile.get("row_count", 0) or 0),
            "column_count": int(dataset_profile.get("column_count", 0) or 0),
            "data_mode": str(dataset_profile.get("data_mode", "")).strip() or None,
            "timestamp_column": str(dataset_profile.get("timestamp_column", "")).strip() or None,
        },
        "intent": {
            "objective": str(run_brief.get("objective", "")).strip() or None,
            "deployment_target": str(run_brief.get("deployment_target", "")).strip() or None,
            "problem_statement": str(task_brief.get("problem_statement", "")).strip() or None,
            "autonomy_mode": str(autonomy_mode.get("requested_mode", "")).strip() or None,
            "operator_signal": str(autonomy_mode.get("operator_signal", "")).strip() or None,
        },
        "decision": {
            "target_column": str(plan.get("target_column") or task_brief.get("target_column") or "").strip() or None,
            "primary_objective": str(focus_profile.get("primary_objective", "")).strip() or None,
            "selected_route_id": str(plan.get("selected_route_id", "")).strip() or None,
            "selected_route_title": str(plan.get("selected_route_title", "")).strip() or None,
            "selected_model_family": str(execution_summary.get("selected_model_family", "")).strip() or str(model_params.get("model_name", "")).strip() or None,
            "best_validation_model_family": str(execution_summary.get("best_validation_model_family", "")).strip() or None,
            "primary_metric": str(plan.get("primary_metric", "")).strip() or str(_bundle_item(investigation_bundle, "optimization_profile").get("primary_metric", "")).strip() or None,
            "split_strategy": str(plan.get("split_strategy", "")).strip() or None,
            "feature_columns": [str(item) for item in plan.get("feature_columns", []) if str(item).strip()],
            "guardrails": [str(item) for item in plan.get("guardrails", []) if str(item).strip()],
            "feature_risk_flags": list(builder_handoff.get("feature_risk_flags", [])),
        },
        "metrics": {
            "validation": dict(selected_metrics.get("validation", {})) if isinstance(selected_metrics.get("validation"), dict) else {},
            "test": dict(selected_metrics.get("test", {})) if isinstance(selected_metrics.get("test"), dict) else {},
        },
        "evidence": {
            "experiment_count": len(experiment_registry.get("experiments", [])) if isinstance(experiment_registry.get("experiments"), list) else 0,
            "challenger_winner": str(challenger_report.get("winner", "")).strip() or None,
            "challenger_delta_to_champion": challenger_report.get("delta_to_champion"),
            "provisional_recommendation": str(audit_report.get("provisional_recommendation", "")).strip() or None,
            "readiness_level": str(audit_report.get("readiness_level", "")).strip() or None,
            "recommended_action": str(belief_update.get("recommended_action", "")).strip() or None,
            "updated_belief": str(belief_update.get("updated_belief", "")).strip() or None,
            "load_bearing_features": [
                str(item.get("removed_feature", "")).strip()
                for item in ablation_report.get("ablations", [])
                if str(item.get("interpretation", "")).strip().startswith("Load-bearing")
            ][:5],
        },
        "assumptions": {
            "count": len(assumption_entries),
            "items": [str(item.get("assumption", "")).strip() for item in assumption_entries if str(item.get("assumption", "")).strip()][:5],
        },
        "next_step": {
            "recommended_experiment_id": str(marginal_value.get("recommended_experiment_id", "")).strip() or None,
            "estimated_value_band": str(marginal_value.get("estimated_value_band", "")).strip() or None,
            "rationale": str(
                belief_update.get("summary", "")
                or marginal_value.get("rationale", "")
            ).strip()
            or None,
            "recommended_action": str(belief_update.get("recommended_action", "")).strip() or None,
        },
        "artifacts": {
            "manifest_path": _path_if_exists(root / "manifest.json"),
            "plan_path": _path_if_exists(root / "plan.json"),
            "model_params_path": _path_if_exists(root / "model_params.json"),
            "model_state_path": _resolve_model_state_path(root, execution_summary=execution_summary),
            "report_path": _path_if_exists(root / RUN_REPORT_RELATIVE_PATH),
            "leaderboard_path": _path_if_exists(root / "leaderboard.csv"),
            "technical_report_path": _path_if_exists(root / "reports" / "technical_report.md"),
            "decision_memo_path": _path_if_exists(root / "reports" / "decision_memo.md"),
        },
    }
    summary["headline"] = _build_headline(summary)
    return summary


def render_run_summary_markdown(summary: dict[str, Any]) -> str:
    """Render a concise markdown summary for humans."""
    decision = dict(summary.get("decision", {}))
    data = dict(summary.get("data", {}))
    intent = dict(summary.get("intent", {}))
    metrics = dict(summary.get("metrics", {}))
    evidence = dict(summary.get("evidence", {}))
    assumptions = dict(summary.get("assumptions", {}))
    next_step = dict(summary.get("next_step", {}))
    lines = [
        "# Relaytic Run Summary",
        "",
        summary.get("headline", "Relaytic completed the requested run."),
        "",
        "## Result",
        f"- Status: `{summary.get('status', 'unknown')}`",
        f"- Target: `{decision.get('target_column') or 'unknown'}`",
        f"- Route: `{decision.get('selected_route_title') or decision.get('selected_route_id') or 'not planned'}`",
        f"- Model: `{decision.get('selected_model_family') or 'not executed'}`",
        f"- Primary metric: `{decision.get('primary_metric') or 'unknown'}`",
        "",
        "## Intent",
        f"- Objective: `{intent.get('objective') or 'unspecified'}`",
        f"- Autonomy mode: `{intent.get('autonomy_mode') or 'unknown'}`",
        f"- Deployment target: `{intent.get('deployment_target') or 'unspecified'}`",
        "",
        "## Data",
        f"- Rows: `{data.get('row_count', 0)}`",
        f"- Columns: `{data.get('column_count', 0)}`",
        f"- Data mode: `{data.get('data_mode') or 'unknown'}`",
    ]
    feature_columns = list(decision.get("feature_columns", []))
    if feature_columns:
        lines.append(f"- First-route features: `{', '.join(feature_columns)}`")
    validation_metrics = dict(metrics.get("validation", {}))
    test_metrics = dict(metrics.get("test", {}))
    if validation_metrics or test_metrics:
        lines.extend(
            [
                "",
                "## Metrics",
                f"- Validation: {_format_metric_block(validation_metrics)}",
                f"- Test: {_format_metric_block(test_metrics)}",
            ]
        )
    if decision.get("guardrails"):
        lines.extend(
            [
                "",
                "## Guardrails",
                f"- {str(decision['guardrails'][0])}",
            ]
        )
    feature_risk_flags = list(decision.get("feature_risk_flags", []))
    if feature_risk_flags:
        lines.append(
            "- Retained risk-flagged features: `"
            + ", ".join(str(item.get("column", "")).strip() for item in feature_risk_flags if str(item.get("column", "")).strip())
            + "`"
        )
    if evidence:
        lines.extend(
            [
                "",
                "## Evidence",
                f"- Experiments logged: `{evidence.get('experiment_count', 0)}`",
                f"- Challenger winner: `{evidence.get('challenger_winner') or 'unknown'}`",
                f"- Provisional recommendation: `{evidence.get('provisional_recommendation') or 'unknown'}`",
                f"- Readiness: `{evidence.get('readiness_level') or 'unknown'}`",
            ]
        )
        if evidence.get("updated_belief"):
            lines.append(f"- Belief update: {evidence['updated_belief']}")
        load_bearing = list(evidence.get("load_bearing_features", []))
        if load_bearing:
            lines.append(f"- Load-bearing features: `{', '.join(load_bearing)}`")
    lines.extend(
        [
            "",
            "## Assumptions",
            f"- Logged assumptions: `{assumptions.get('count', 0)}`",
        ]
    )
    if assumptions.get("items"):
        lines.append(f"- First assumption: {assumptions['items'][0]}")
    lines.extend(
        [
            "",
            "## Next",
            f"- Recommended next experiment: `{next_step.get('recommended_experiment_id') or 'none'}`",
            f"- Recommended action: `{next_step.get('recommended_action') or 'unspecified'}`",
            f"- Why: {next_step.get('rationale') or 'No follow-up rationale recorded.'}",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def materialize_run_summary(
    *,
    run_dir: str | Path,
    data_path: str | Path | None = None,
    request_source: str | None = None,
    request_text: str | None = None,
) -> dict[str, Any]:
    """Build and write the machine and human summary artifacts for a run."""
    root = Path(run_dir)
    summary = build_run_summary(
        run_dir=root,
        data_path=data_path,
        request_source=request_source,
        request_text=request_text,
    )
    summary_path = write_json(
        root / RUN_SUMMARY_FILENAME,
        summary,
        indent=2,
        ensure_ascii=False,
        sort_keys=True,
    )
    report_path = root / RUN_REPORT_RELATIVE_PATH
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(render_run_summary_markdown(summary), encoding="utf-8")
    return {
        "summary": summary,
        "summary_path": summary_path,
        "report_path": report_path,
        "report_markdown": report_path.read_text(encoding="utf-8"),
    }


def _read_bundle(root: Path, mapping: dict[str, str]) -> dict[str, Any]:
    return {
        key: payload
        for key, filename in mapping.items()
        if isinstance((payload := _read_json(root / filename)), dict)
    }


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return payload if isinstance(payload, dict) else {}


def _bundle_item(bundle: dict[str, Any], key: str) -> dict[str, Any]:
    payload = bundle.get(key)
    return dict(payload) if isinstance(payload, dict) else {}


def _first_data_reference(builder_handoff: dict[str, Any]) -> str:
    for value in builder_handoff.get("data_references", []):
        text = str(value).strip()
        if text:
            return text
    return ""


def _resolve_stage(
    *,
    plan: dict[str, Any],
    execution_summary: dict[str, Any],
    investigation_bundle: dict[str, Any],
    intake_bundle: dict[str, Any],
    evidence_bundle: dict[str, Any],
) -> str:
    if evidence_bundle:
        return "evidence_reviewed"
    if execution_summary:
        return "planned_and_executed"
    if plan:
        return "planned"
    if investigation_bundle:
        return "investigated"
    if intake_bundle:
        return "interpreted"
    return "foundation_only"


def _resolve_run_status(
    *,
    plan: dict[str, Any],
    execution_summary: dict[str, Any],
    audit_report: dict[str, Any],
) -> str:
    if audit_report:
        recommendation = str(audit_report.get("provisional_recommendation", "")).strip()
        if recommendation:
            return recommendation
    if execution_summary:
        status = str(execution_summary.get("status", "")).strip()
        return status or "executed"
    if plan:
        return "planned"
    return "initialized"


def _path_if_exists(path: Path) -> str | None:
    return str(path) if path.exists() else None


def _resolve_model_state_path(root: Path, *, execution_summary: dict[str, Any]) -> str | None:
    text = str(execution_summary.get("model_state_path", "")).strip()
    if text:
        return text
    direct = root / "model_state.json"
    if direct.exists():
        return str(direct)
    for candidate in sorted(root.glob("*_state.json")):
        if candidate.name != "normalization_state.json":
            return str(candidate)
    return None


def _preview_text(value: Any, *, limit: int = 160) -> str | None:
    text = str(value or "").strip()
    if not text:
        return None
    if len(text) <= limit:
        return text
    return text[: limit - 3].rstrip() + "..."


def _build_headline(summary: dict[str, Any]) -> str:
    decision = dict(summary.get("decision", {}))
    evidence = dict(summary.get("evidence", {}))
    target = decision.get("target_column") or "unknown target"
    route = decision.get("selected_route_title") or decision.get("selected_route_id") or "no selected route"
    model = decision.get("selected_model_family")
    if model:
        recommendation = evidence.get("provisional_recommendation")
        if recommendation:
            return (
                f"Relaytic built `{model}` for `{target}` using the `{route}` route and "
                f"currently recommends `{recommendation}` after challenger and audit review."
            )
        return f"Relaytic built `{model}` for `{target}` using the `{route}` route."
    return f"Relaytic prepared `{route}` for `{target}` but has not executed a model build yet."


def _format_metric_block(metrics: dict[str, Any]) -> str:
    if not metrics:
        return "not available"
    preferred_order = ["log_loss", "mae", "rmse", "accuracy", "precision", "recall", "f1", "pr_auc", "roc_auc"]
    parts: list[str] = []
    for key in preferred_order:
        if key in metrics:
            value = metrics[key]
            if isinstance(value, (int, float)):
                parts.append(f"{key}={value:.4f}")
    if not parts:
        for key, value in metrics.items():
            if isinstance(value, (int, float)):
                parts.append(f"{key}={value:.4f}")
    return ", ".join(parts) if parts else "not available"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()
