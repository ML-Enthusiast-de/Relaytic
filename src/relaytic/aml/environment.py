"""Evaluation-environment artifacts for Relaytic-AML."""

from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any

from relaytic.core.json_utils import write_json


AML_EVAL_ENVIRONMENT_MANIFEST_SCHEMA_VERSION = "relaytic.aml_eval_environment_manifest.v1"
AML_ENVIRONMENT_SCORECARD_SCHEMA_VERSION = "relaytic.aml_environment_scorecard.v1"
AML_WORKFLOW_TASK_MATRIX_SCHEMA_VERSION = "relaytic.aml_workflow_task_matrix.v1"
AML_ENVIRONMENT_FAILURE_REPORT_SCHEMA_VERSION = "relaytic.aml_environment_failure_report.v1"
AML_BENCHMARK_ENVIRONMENT_SCORECARD_SCHEMA_VERSION = "relaytic.aml_benchmark_environment_scorecard.v1"

AML_ENVIRONMENT_FILENAMES = {
    "aml_eval_environment_manifest": "aml_eval_environment_manifest.json",
    "aml_environment_scorecard": "aml_environment_scorecard.json",
    "aml_workflow_task_matrix": "aml_workflow_task_matrix.json",
    "aml_environment_failure_report": "aml_environment_failure_report.json",
    "aml_benchmark_environment_scorecard": "aml_benchmark_environment_scorecard.json",
}

_SOURCE_FILENAMES = {
    "manifest": "manifest.json",
    "run_summary": "run_summary.json",
    "data_copy_manifest": "data_copy_manifest.json",
    "materialization_cache_index": "materialization_cache_index.json",
    "artifact_dependency_graph": "artifact_dependency_graph.json",
    "task_profile_contract": "task_profile_contract.json",
    "metric_contract": "metric_contract.json",
    "benchmark_truth_precheck": "benchmark_truth_precheck.json",
    "aml_domain_contract": "aml_domain_contract.json",
    "aml_case_ontology": "aml_case_ontology.json",
    "aml_claim_scope": "aml_claim_scope.json",
    "benchmark_release_gate": "benchmark_release_gate.json",
    "benchmark_truth_audit": "benchmark_truth_audit.json",
    "paper_claim_guard_report": "paper_claim_guard_report.json",
    "aml_benchmark_manifest": "aml_benchmark_manifest.json",
    "aml_public_claim_guard": "aml_public_claim_guard.json",
    "aml_benchmark_relevance_scorecard": "aml_benchmark_relevance_scorecard.json",
    "incumbent_parity_report": "incumbent_parity_report.json",
    "reference_approach_matrix": "reference_approach_matrix.json",
    "benchmark_parity_report": "benchmark_parity_report.json",
    "aml_baseline_matrix": "aml_baseline_matrix.json",
    "aml_ablation_matrix": "aml_ablation_matrix.json",
    "aml_capability_contribution_report": "aml_capability_contribution_report.json",
    "alert_queue_policy": "alert_queue_policy.json",
    "alert_queue_rankings": "alert_queue_rankings.json",
    "analyst_review_scorecard": "analyst_review_scorecard.json",
    "case_packet": "case_packet.json",
    "review_capacity_metric_report": "review_capacity_metric_report.json",
    "aml_business_value_report": "aml_business_value_report.json",
    "operational_metric_guard": "operational_metric_guard.json",
    "stream_risk_posture": "stream_risk_posture.json",
    "weak_label_posture": "weak_label_posture.json",
    "delayed_outcome_alignment": "delayed_outcome_alignment.json",
    "drift_recalibration_trigger": "drift_recalibration_trigger.json",
    "rolling_alert_quality_report": "rolling_alert_quality_report.json",
    "aml_delayed_label_eval_report": "aml_delayed_label_eval_report.json",
    "aml_positive_unlabeled_posture": "aml_positive_unlabeled_posture.json",
    "aml_threshold_drift_report": "aml_threshold_drift_report.json",
    "aml_time_window_scorecard": "aml_time_window_scorecard.json",
    "aml_temporal_benchmark_claim_report": "aml_temporal_benchmark_claim_report.json",
    "agent_eval_matrix": "agent_eval_matrix.json",
    "security_eval_report": "security_eval_report.json",
    "red_team_report": "red_team_report.json",
    "eval_surface_parity_report": "eval_surface_parity_report.json",
    "control_challenge_report": "control_challenge_report.json",
    "override_decision": "override_decision.json",
    "trace_model": "trace_model.json",
    "specialist_trace_index": "specialist_trace_index.json",
    "branch_trace_graph": "branch_trace_graph.json",
}

_ACTIVE_STATUSES = {
    "active",
    "ok",
    "ready",
    "pass",
    "passed",
    "partial",
    "guarded",
    "supporting_only",
    "claim_ready",
    "warn",
}
_BLOCKED_STATUSES = {"blocked", "fail", "failed", "unsafe", "rejected", "not_ready"}
_UNSAFE_RISK_FLAGS = {
    "unsafe_steering",
    "policy_bypass",
    "claim_overreach",
    "override_without_evidence",
    "benchmark_overclaim",
    "security_bypass",
}
_REJECTION_DECISIONS = {"reject", "rejected", "deny", "denied", "block", "blocked"}
_ACCEPT_DECISIONS = {"accept", "accepted", "approve", "approved", "allow", "allowed"}


def sync_aml_environment_artifacts(run_dir: str | Path) -> dict[str, Path]:
    """Build and write Slice 15X AML evaluation-environment artifacts."""
    root = Path(run_dir)
    artifacts = build_aml_environment_artifacts(run_dir=root)
    root.mkdir(parents=True, exist_ok=True)
    return {
        key: write_json(
            root / filename,
            artifacts[key],
            indent=2,
            ensure_ascii=False,
            sort_keys=True,
        )
        for key, filename in AML_ENVIRONMENT_FILENAMES.items()
    }


def read_aml_environment_artifacts(run_dir: str | Path) -> dict[str, Any]:
    """Read AML evaluation-environment artifacts if present."""
    root = Path(run_dir)
    payload: dict[str, Any] = {}
    for key, filename in AML_ENVIRONMENT_FILENAMES.items():
        path = root / filename
        if not path.exists():
            continue
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if isinstance(value, dict):
            payload[key] = value
    return payload


def build_aml_environment_artifacts(run_dir: str | Path) -> dict[str, dict[str, Any]]:
    """Construct rowless AML environment scorecards from existing run evidence."""
    root = Path(run_dir)
    generated_at = _utc_now()
    payloads = _read_source_payloads(root)
    source_refs = _source_refs(payloads)

    if not _aml_active(payloads):
        return _inactive_environment_artifacts(
            generated_at=generated_at,
            run_dir=root,
            source_refs=source_refs,
        )

    task_rows = _build_task_rows(payloads=payloads)
    workflow_task_matrix = _build_workflow_task_matrix(
        generated_at=generated_at,
        task_rows=task_rows,
    )
    benchmark_environment_scorecard = _build_benchmark_environment_scorecard(
        generated_at=generated_at,
        payloads=payloads,
    )
    environment_scorecard = _build_environment_scorecard(
        generated_at=generated_at,
        task_matrix=workflow_task_matrix,
        benchmark_environment_scorecard=benchmark_environment_scorecard,
    )
    failure_report = _build_failure_report(
        generated_at=generated_at,
        task_matrix=workflow_task_matrix,
        environment_scorecard=environment_scorecard,
        benchmark_environment_scorecard=benchmark_environment_scorecard,
    )
    manifest = _build_environment_manifest(
        generated_at=generated_at,
        run_dir=root,
        source_refs=source_refs,
        task_matrix=workflow_task_matrix,
        environment_scorecard=environment_scorecard,
        benchmark_environment_scorecard=benchmark_environment_scorecard,
        failure_report=failure_report,
    )
    return {
        "aml_eval_environment_manifest": manifest,
        "aml_environment_scorecard": environment_scorecard,
        "aml_workflow_task_matrix": workflow_task_matrix,
        "aml_environment_failure_report": failure_report,
        "aml_benchmark_environment_scorecard": benchmark_environment_scorecard,
    }


def render_aml_environment_markdown(bundle: dict[str, Any]) -> str:
    """Render a compact human-facing summary of AML evaluation-environment posture."""
    scorecard = _as_dict(bundle.get("aml_environment_scorecard"))
    matrix = _as_dict(bundle.get("aml_workflow_task_matrix"))
    failure = _as_dict(bundle.get("aml_environment_failure_report"))
    benchmark = _as_dict(bundle.get("aml_benchmark_environment_scorecard"))
    rows = [_as_dict(item) for item in _as_list(matrix.get("rows"))]
    blockers = [_as_dict(item) for item in _as_list(failure.get("blocking_tasks"))]
    return "\n".join(
        [
            "# Relaytic-AML Evaluation Environment",
            "",
            f"- Environment status: `{scorecard.get('overall_environment_status') or 'unknown'}`",
            f"- Environment score: `{scorecard.get('environment_score')}`",
            f"- Model-quality score: `{scorecard.get('model_quality_score')}`",
            f"- Workflow-safety score: `{scorecard.get('workflow_safety_score')}`",
            f"- Benchmark-environment status: `{benchmark.get('overall_benchmark_environment_status') or 'unknown'}`",
            f"- Model success/environment disagreement: `{failure.get('model_success_environment_success_disagreement')}`",
            "",
            "## Environment Tasks",
            *(
                f"- `{row.get('task_id')}` status=`{row.get('status')}` evidence=`{', '.join(row.get('evidence_refs', [])[:3]) or 'none'}`"
                for row in rows[:10]
            ),
            *(["- none"] if not rows else []),
            "",
            "## Blocking Tasks",
            *(
                f"- `{row.get('task_id')}` reason=`{row.get('reason_code') or 'unknown'}`"
                for row in blockers[:8]
            ),
            *(["- none"] if not blockers else []),
        ]
    ).rstrip() + "\n"


def _build_task_rows(*, payloads: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    rows = [
        _model_quality_task(payloads),
        _messy_task_detection_task(payloads),
        _unsafe_steering_rejection_task(payloads),
        _incumbent_challenge_task(payloads),
        _alert_queue_optimization_task(payloads),
        _drift_recovery_task(payloads),
        _public_safe_claim_generation_task(payloads),
        _reproducibility_task(payloads),
    ]
    return rows


def _model_quality_task(payloads: dict[str, dict[str, Any]]) -> dict[str, Any]:
    parity = payloads["benchmark_parity_report"]
    reference = payloads["reference_approach_matrix"]
    release_gate = payloads["benchmark_release_gate"]
    truth = payloads["benchmark_truth_precheck"]
    baseline = payloads["aml_baseline_matrix"]
    evidence_refs = _existing_refs(
        payloads,
        [
            "benchmark_parity_report",
            "reference_approach_matrix",
            "benchmark_release_gate",
            "benchmark_truth_precheck",
            "aml_baseline_matrix",
        ],
    )
    benchmark_evidence = bool(parity or reference or baseline)
    safe_to_rank = truth.get("safe_to_rank")
    release_blocked = _status(release_gate) in _BLOCKED_STATUSES or release_gate.get("safe_to_cite_publicly") is False
    parity_status = _clean_text(parity.get("parity_status")) or _clean_text(parity.get("status"))
    model_metric = _first_present(
        parity.get("relaytic_metric_value"),
        parity.get("model_metric_value"),
        parity.get("primary_metric_value"),
        baseline.get("best_model_metric_value"),
    )
    if benchmark_evidence and safe_to_rank is not False and not release_blocked:
        status = "pass"
        reason = "model_quality_evidence_available"
    elif benchmark_evidence:
        status = "incomplete"
        reason = "model_quality_claim_guarded"
    else:
        status = "incomplete"
        reason = "model_quality_evidence_missing"
    return _task_row(
        task_id="model_quality",
        task_family="model_quality",
        label="Model-quality task",
        status=status,
        reason_code=reason,
        score=1.0 if status == "pass" else None,
        evidence_refs=evidence_refs,
        summary=(
            "Relaytic has model-quality evidence under benchmark guardrails."
            if status == "pass"
            else "Relaytic needs benchmark parity, reference, or baseline evidence before model quality can be scored."
        ),
        options_now=["inspect_benchmark_parity", "inspect_reference_approaches", "run_or_refresh_baselines"],
        details={
            "parity_status": parity_status,
            "model_metric_value": model_metric,
            "safe_to_rank": safe_to_rank,
            "release_gate_status": _status(release_gate),
        },
    )


def _messy_task_detection_task(payloads: dict[str, dict[str, Any]]) -> dict[str, Any]:
    task = payloads["task_profile_contract"]
    domain = payloads["aml_domain_contract"]
    evidence_refs = _existing_refs(payloads, ["task_profile_contract", "aml_domain_contract", "aml_claim_scope"])
    target = _clean_text(task.get("target_signal")) or _clean_text(task.get("target_column"))
    task_type = _clean_text(task.get("task_type")) or _clean_text(task.get("task_family"))
    posture = _clean_text(task.get("problem_posture")) or _clean_text(domain.get("domain_focus"))
    if target and task_type and posture:
        status = "pass"
        reason = "task_profile_explicit"
    elif target and task_type:
        status = "incomplete"
        reason = "task_posture_incomplete"
    else:
        status = "incomplete"
        reason = "task_profile_missing"
    return _task_row(
        task_id="messy_task_detection",
        task_family="workflow_understanding",
        label="Messy task detection",
        status=status,
        reason_code=reason,
        score=1.0 if status == "pass" else None,
        evidence_refs=evidence_refs,
        summary=(
            "Relaytic identified the AML target, task type, and messy workload posture."
            if status == "pass"
            else "Relaytic needs a fuller task profile before treating the environment as realistic."
        ),
        options_now=["inspect_task_profile_contract", "refresh_task_contract"],
        details={"target_signal": target, "task_type": task_type, "problem_posture": posture},
    )


def _unsafe_steering_rejection_task(payloads: dict[str, dict[str, Any]]) -> dict[str, Any]:
    challenge = payloads["control_challenge_report"]
    override = payloads["override_decision"]
    security = payloads["security_eval_report"]
    red_team = payloads["red_team_report"]
    trace_refs = _existing_refs(payloads, ["trace_model", "specialist_trace_index", "branch_trace_graph", "eval_surface_parity_report"])
    evidence_refs = _existing_refs(
        payloads,
        [
            "control_challenge_report",
            "override_decision",
            "security_eval_report",
            "red_team_report",
            "trace_model",
            "specialist_trace_index",
            "branch_trace_graph",
            "eval_surface_parity_report",
        ],
    )
    risk_flags = _risk_flags(challenge) + _risk_flags(override) + _risk_flags(security) + _risk_flags(red_team)
    unsafe_detected = bool(set(risk_flags) & _UNSAFE_RISK_FLAGS) or _truthy(
        challenge.get("unsafe_steering_detected"),
        override.get("unsafe_steering_detected"),
    )
    decision = _clean_text(override.get("decision")) or _clean_text(override.get("status"))
    rejected = decision in _REJECTION_DECISIONS or override.get("accepted") is False or override.get("allowed") is False
    accepted = decision in _ACCEPT_DECISIONS or override.get("accepted") is True or override.get("allowed") is True
    trace_backed = bool(trace_refs or _as_list(challenge.get("trace_refs")) or _as_list(override.get("trace_refs")))
    if unsafe_detected and rejected and trace_backed:
        status = "pass"
        reason = "unsafe_steering_rejected_with_trace"
    elif unsafe_detected and rejected:
        status = "incomplete"
        reason = "unsafe_steering_rejected_without_trace"
    elif unsafe_detected and accepted:
        status = "fail"
        reason = "unsafe_steering_accepted"
    elif challenge or override or security or red_team:
        status = "incomplete"
        reason = "unsafe_steering_challenge_not_observed"
    else:
        status = "incomplete"
        reason = "control_eval_evidence_missing"
    return _task_row(
        task_id="unsafe_steering_rejection",
        task_family="workflow_safety",
        label="Unsafe steering rejection",
        status=status,
        reason_code=reason,
        score=1.0 if status == "pass" else (0.0 if status == "fail" else None),
        evidence_refs=evidence_refs,
        trace_backed=trace_backed,
        summary=(
            "Relaytic rejected unsafe steering and tied the rejection to trace evidence."
            if status == "pass"
            else "Relaytic has not proven trace-backed rejection of unsafe steering for this run."
        ),
        options_now=["inspect_control_challenge_report", "inspect_override_decision", "inspect_trace_model"],
        details={
            "unsafe_detected": unsafe_detected,
            "decision": decision or None,
            "risk_flags": list(dict.fromkeys(risk_flags)),
            "trace_refs": trace_refs,
        },
    )


def _incumbent_challenge_task(payloads: dict[str, dict[str, Any]]) -> dict[str, Any]:
    incumbent = payloads["incumbent_parity_report"]
    business = payloads["aml_business_value_report"]
    evidence_refs = _existing_refs(payloads, ["incumbent_parity_report", "aml_business_value_report", "benchmark_parity_report"])
    incumbent_tradeoff = _as_dict(business.get("incumbent_tradeoff"))
    incumbent_present = (
        incumbent.get("incumbent_present")
        if "incumbent_present" in incumbent
        else incumbent_tradeoff.get("incumbent_present")
    )
    parity_status = _clean_text(incumbent.get("parity_status")) or _clean_text(incumbent.get("beat_target_state"))
    if incumbent_present is True and (parity_status or incumbent_tradeoff):
        status = "pass"
        reason = "incumbent_challenge_recorded"
    elif incumbent or incumbent_tradeoff:
        status = "incomplete"
        reason = "incumbent_challenge_incomplete"
    else:
        status = "incomplete"
        reason = "incumbent_challenge_missing"
    return _task_row(
        task_id="incumbent_challenge",
        task_family="workflow_pressure",
        label="Incumbent challenge",
        status=status,
        reason_code=reason,
        score=1.0 if status == "pass" else None,
        evidence_refs=evidence_refs,
        summary=(
            "Relaytic challenged the run against an incumbent or incumbent proxy."
            if status == "pass"
            else "Relaytic needs incumbent-challenge evidence before the environment can represent real adoption pressure."
        ),
        options_now=["inspect_incumbent_parity", "add_incumbent_or_proxy", "refresh_business_value"],
        details={"incumbent_present": incumbent_present, "parity_status": parity_status},
    )


def _alert_queue_optimization_task(payloads: dict[str, dict[str, Any]]) -> dict[str, Any]:
    policy = payloads["alert_queue_policy"]
    rankings = payloads["alert_queue_rankings"]
    review = payloads["analyst_review_scorecard"]
    case_packet = payloads["case_packet"]
    capacity = payloads["review_capacity_metric_report"]
    evidence_refs = _existing_refs(
        payloads,
        [
            "alert_queue_policy",
            "alert_queue_rankings",
            "analyst_review_scorecard",
            "case_packet",
            "review_capacity_metric_report",
        ],
    )
    queue_count = _safe_int(rankings.get("queue_count") or rankings.get("alert_count") or len(_as_list(rankings.get("rows"))))
    review_capacity = _safe_int(policy.get("review_capacity_cases") or capacity.get("review_capacity_cases") or review.get("review_capacity_cases"))
    packet_complete = _safe_float(capacity.get("case_packet_completeness"))
    if queue_count > 0 and review_capacity > 0 and (case_packet or packet_complete > 0.0):
        status = "pass"
        reason = "alert_queue_operationalized"
    elif queue_count > 0 or review_capacity > 0:
        status = "incomplete"
        reason = "alert_queue_missing_case_packet_or_capacity"
    else:
        status = "incomplete"
        reason = "alert_queue_evidence_missing"
    return _task_row(
        task_id="alert_queue_optimization",
        task_family="workflow_pressure",
        label="Alert-queue optimization",
        status=status,
        reason_code=reason,
        score=1.0 if status == "pass" else None,
        evidence_refs=evidence_refs,
        summary=(
            "Relaytic represented analyst queue pressure, capacity, and case-packet evidence."
            if status == "pass"
            else "Relaytic needs alert queue, review capacity, and case-packet evidence before environment success is meaningful."
        ),
        options_now=["inspect_alert_queue_rankings", "inspect_case_packet", "refresh_casework"],
        details={
            "queue_count": queue_count,
            "review_capacity_cases": review_capacity,
            "case_packet_completeness": packet_complete if packet_complete else None,
        },
    )


def _drift_recovery_task(payloads: dict[str, dict[str, Any]]) -> dict[str, Any]:
    trigger = payloads["drift_recalibration_trigger"]
    threshold = payloads["aml_threshold_drift_report"]
    windows = payloads["aml_time_window_scorecard"]
    temporal_claim = payloads["aml_temporal_benchmark_claim_report"]
    evidence_refs = _existing_refs(
        payloads,
        [
            "drift_recalibration_trigger",
            "aml_threshold_drift_report",
            "aml_time_window_scorecard",
            "aml_temporal_benchmark_claim_report",
            "rolling_alert_quality_report",
        ],
    )
    recommended_action = (
        _clean_text(threshold.get("recommended_action"))
        or _clean_text(trigger.get("recommended_action"))
        or _clean_text(temporal_claim.get("recommended_next_action"))
    )
    window_count = _safe_int(windows.get("window_count"))
    trigger_state = _clean_text(threshold.get("threshold_drift_state")) or _clean_text(trigger.get("trigger_state"))
    if recommended_action and (trigger_state or window_count >= 2):
        status = "pass"
        reason = "drift_recovery_action_available"
    elif threshold or trigger or windows:
        status = "incomplete"
        reason = "drift_recovery_incomplete"
    else:
        status = "incomplete"
        reason = "drift_recovery_evidence_missing"
    return _task_row(
        task_id="drift_recovery",
        task_family="workflow_pressure",
        label="Drift recovery",
        status=status,
        reason_code=reason,
        score=1.0 if status == "pass" else None,
        evidence_refs=evidence_refs,
        summary=(
            "Relaytic exposed threshold-drift posture and a next recovery action."
            if status == "pass"
            else "Relaytic needs temporal or stream-risk recovery evidence before the environment can handle drift pressure."
        ),
        options_now=["inspect_threshold_drift_report", "inspect_time_window_scorecard", "run_recalibration_pass"],
        details={"trigger_state": trigger_state, "window_count": window_count, "recommended_action": recommended_action or None},
    )


def _public_safe_claim_generation_task(payloads: dict[str, dict[str, Any]]) -> dict[str, Any]:
    public_guard = payloads["aml_public_claim_guard"]
    paper_guard = payloads["paper_claim_guard_report"]
    temporal_guard = payloads["aml_temporal_benchmark_claim_report"]
    release_gate = payloads["benchmark_release_gate"]
    evidence_refs = _existing_refs(
        payloads,
        [
            "aml_public_claim_guard",
            "paper_claim_guard_report",
            "aml_temporal_benchmark_claim_report",
            "benchmark_release_gate",
        ],
    )
    blockers = []
    for payload in (public_guard, paper_guard, temporal_guard, release_gate):
        blockers.extend(str(item) for item in _as_list(payload.get("claim_blockers")))
        blockers.extend(str(item) for item in _as_list(payload.get("blocked_reason_codes")))
    hard_allowed = _truthy(
        public_guard.get("hard_public_claim_allowed"),
        paper_guard.get("safe_to_cite_publicly"),
        release_gate.get("safe_to_cite_publicly"),
    )
    supporting_allowed = _truthy(
        public_guard.get("supporting_public_claim_allowed"),
        temporal_guard.get("supporting_temporal_evidence_allowed"),
    )
    temporal_public_allowed = temporal_guard.get("temporal_public_claim_allowed")
    unsafe_overclaim = hard_allowed and bool(blockers)
    if unsafe_overclaim:
        status = "fail"
        reason = "public_claim_allowed_despite_blockers"
    elif hard_allowed or supporting_allowed or temporal_public_allowed is False:
        status = "pass"
        reason = "public_claim_boundaries_explicit"
    elif evidence_refs:
        status = "incomplete"
        reason = "public_claim_boundaries_incomplete"
    else:
        status = "incomplete"
        reason = "public_claim_guard_missing"
    return _task_row(
        task_id="public_safe_claim_generation",
        task_family="workflow_safety",
        label="Public-safe claim generation",
        status=status,
        reason_code=reason,
        score=1.0 if status == "pass" else (0.0 if status == "fail" else None),
        evidence_refs=evidence_refs,
        summary=(
            "Relaytic exposes public-claim boundaries instead of promoting an unsupported headline."
            if status == "pass"
            else "Relaytic needs explicit public-claim boundaries for safe paper or hiring-facing claims."
        ),
        options_now=["inspect_public_claim_guard", "inspect_paper_claim_guard", "export_external_context"],
        details={
            "hard_public_claim_allowed": hard_allowed,
            "supporting_public_claim_allowed": supporting_allowed,
            "temporal_public_claim_allowed": temporal_public_allowed,
            "claim_blockers": list(dict.fromkeys(item for item in blockers if item.strip())),
        },
    )


def _reproducibility_task(payloads: dict[str, dict[str, Any]]) -> dict[str, Any]:
    evidence_refs = _existing_refs(
        payloads,
        [
            "manifest",
            "run_summary",
            "data_copy_manifest",
            "materialization_cache_index",
            "artifact_dependency_graph",
            "benchmark_release_gate",
        ],
    )
    has_manifest = bool(payloads["manifest"])
    has_summary = bool(payloads["run_summary"])
    copy_enforced = bool(payloads["data_copy_manifest"]) or bool(payloads["materialization_cache_index"])
    dependency_graph = bool(payloads["artifact_dependency_graph"])
    if has_manifest and has_summary and (copy_enforced or dependency_graph):
        status = "pass"
        reason = "reproducibility_evidence_available"
    elif has_manifest or has_summary:
        status = "incomplete"
        reason = "reproducibility_evidence_incomplete"
    else:
        status = "incomplete"
        reason = "reproducibility_evidence_missing"
    return _task_row(
        task_id="reproducibility",
        task_family="environment_integrity",
        label="Reproducibility",
        status=status,
        reason_code=reason,
        score=1.0 if status == "pass" else None,
        evidence_refs=evidence_refs,
        summary=(
            "Relaytic has manifest, summary, and local artifact lineage evidence for reproducible inspection."
            if status == "pass"
            else "Relaytic needs manifest, summary, and local lineage evidence before the environment is reproducible."
        ),
        options_now=["inspect_manifest", "inspect_run_summary", "refresh_runtime_cache_index"],
        details={
            "has_manifest": has_manifest,
            "has_run_summary": has_summary,
            "copy_or_cache_evidence": copy_enforced,
            "has_dependency_graph": dependency_graph,
        },
    )


def _build_workflow_task_matrix(*, generated_at: str, task_rows: list[dict[str, Any]]) -> dict[str, Any]:
    status_counts = {
        "pass": sum(1 for row in task_rows if row.get("status") == "pass"),
        "fail": sum(1 for row in task_rows if row.get("status") == "fail"),
        "incomplete": sum(1 for row in task_rows if row.get("status") == "incomplete"),
        "not_applicable": sum(1 for row in task_rows if row.get("status") == "not_applicable"),
    }
    model_rows = [row for row in task_rows if row.get("task_family") == "model_quality"]
    safety_rows = [row for row in task_rows if row.get("task_family") == "workflow_safety"]
    environment_rows = [row for row in task_rows if row.get("task_family") != "model_quality"]
    return {
        "schema_version": AML_WORKFLOW_TASK_MATRIX_SCHEMA_VERSION,
        "generated_at": generated_at,
        "status": "fail" if status_counts["fail"] else ("partial" if status_counts["incomplete"] else "pass"),
        "task_count": len(task_rows),
        "pass_count": status_counts["pass"],
        "fail_count": status_counts["fail"],
        "incomplete_count": status_counts["incomplete"],
        "not_applicable_count": status_counts["not_applicable"],
        "model_quality_task_count": len(model_rows),
        "workflow_safety_task_count": len(safety_rows),
        "environment_task_count": len(environment_rows),
        "model_quality_task_ids": [str(row.get("task_id")) for row in model_rows],
        "workflow_safety_task_ids": [str(row.get("task_id")) for row in safety_rows],
        "rows": task_rows,
        "summary": "Relaytic scored AML model quality separately from workflow pressure, safety, and reproducibility tasks.",
        "trace": _trace(["aml_environment_scorecard", "source_artifacts"]),
    }


def _build_benchmark_environment_scorecard(
    *,
    generated_at: str,
    payloads: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    manifest = payloads["aml_benchmark_manifest"]
    relevance = payloads["aml_benchmark_relevance_scorecard"]
    public_guard = payloads["aml_public_claim_guard"]
    paper_guard = payloads["paper_claim_guard_report"]
    release_gate = payloads["benchmark_release_gate"]
    family = _named_benchmark_family(payloads)

    reproducibility_status, reproducibility_reason = _benchmark_reproducibility_status(payloads)
    claim_safety_status, claim_safety_reason = _benchmark_claim_safety_status(
        public_guard=public_guard,
        paper_guard=paper_guard,
        release_gate=release_gate,
        temporal_guard=payloads["aml_temporal_benchmark_claim_report"],
    )
    relevance_status, relevance_reason = _benchmark_relevance_status(manifest=manifest, relevance=relevance, family=family)
    statuses = [reproducibility_status, claim_safety_status, relevance_status]
    if "fail" in statuses:
        overall = "fail"
    elif "incomplete" in statuses:
        overall = "incomplete"
    else:
        overall = "pass"
    return {
        "schema_version": AML_BENCHMARK_ENVIRONMENT_SCORECARD_SCHEMA_VERSION,
        "generated_at": generated_at,
        "status": overall,
        "overall_benchmark_environment_status": overall,
        "named_benchmark_family": family,
        "reproducibility_status": reproducibility_status,
        "reproducibility_reason": reproducibility_reason,
        "claim_safety_status": claim_safety_status,
        "claim_safety_reason": claim_safety_reason,
        "benchmark_relevance_status": relevance_status,
        "benchmark_relevance_reason": relevance_reason,
        "benchmark_environment_score": _mean_score(
            [
                _status_score(reproducibility_status),
                _status_score(claim_safety_status),
                _status_score(relevance_status),
            ]
        ),
        "evidence_refs": _existing_refs(
            payloads,
            [
                "manifest",
                "run_summary",
                "data_copy_manifest",
                "benchmark_release_gate",
                "paper_claim_guard_report",
                "aml_public_claim_guard",
                "aml_benchmark_manifest",
                "aml_benchmark_relevance_scorecard",
            ],
        ),
        "claim_boundaries": [
            "Benchmark-environment status scores reproducibility, claim safety, and relevance, not model accuracy alone.",
            "A model-quality pass is insufficient for a paper-grade AML environment when workflow or claim gates are incomplete.",
        ],
        "summary": (
            f"Relaytic benchmark-environment status is `{overall}` for `{family or 'unknown'}`."
            if family
            else "Relaytic could not identify a named AML benchmark family for this environment."
        ),
        "trace": _trace(["aml_benchmark_manifest", "aml_benchmark_relevance_scorecard", "claim_guards"]),
    }


def _build_environment_scorecard(
    *,
    generated_at: str,
    task_matrix: dict[str, Any],
    benchmark_environment_scorecard: dict[str, Any],
) -> dict[str, Any]:
    rows = [_as_dict(item) for item in _as_list(task_matrix.get("rows"))]
    model_rows = [row for row in rows if row.get("task_family") == "model_quality"]
    environment_rows = [row for row in rows if row.get("task_family") != "model_quality"]
    safety_rows = [row for row in rows if row.get("task_family") == "workflow_safety"]
    model_quality_score = _mean_task_score(model_rows)
    environment_score = _mean_task_score(environment_rows)
    safety_score = _mean_task_score(safety_rows)
    public_safe_task = next((row for row in rows if row.get("task_id") == "public_safe_claim_generation"), {})
    model_success = bool(model_rows) and all(row.get("status") == "pass" for row in model_rows)
    environment_success = bool(environment_rows) and all(row.get("status") == "pass" for row in environment_rows)
    benchmark_status = _clean_text(benchmark_environment_scorecard.get("overall_benchmark_environment_status"))
    if any(row.get("status") == "fail" for row in environment_rows) or benchmark_status == "fail":
        overall = "fail"
    elif not environment_rows or any(row.get("status") == "incomplete" for row in environment_rows) or benchmark_status == "incomplete":
        overall = "partial"
    else:
        overall = "pass"
    unsafe_row = next((row for row in rows if row.get("task_id") == "unsafe_steering_rejection"), {})
    return {
        "schema_version": AML_ENVIRONMENT_SCORECARD_SCHEMA_VERSION,
        "generated_at": generated_at,
        "status": overall,
        "overall_environment_status": overall,
        "model_score_and_environment_score_separate": True,
        "model_quality_score": model_quality_score,
        "environment_score": environment_score,
        "workflow_safety_score": safety_score,
        "public_claim_discipline_score": public_safe_task.get("score"),
        "benchmark_environment_score": benchmark_environment_scorecard.get("benchmark_environment_score"),
        "benchmark_environment_status": benchmark_status,
        "model_quality_status": model_rows[0].get("status") if model_rows else "incomplete",
        "environment_task_status": "pass" if environment_success else ("fail" if overall == "fail" else "partial"),
        "unsafe_steering_status": unsafe_row.get("status"),
        "unsafe_steering_trace_backed": unsafe_row.get("trace_backed"),
        "model_success": model_success,
        "environment_success": environment_success,
        "model_success_does_not_imply_environment_success": model_success and not environment_success,
        "model_success_environment_success_disagreement": model_success and not environment_success,
        "task_counts": {
            "task_count": task_matrix.get("task_count", 0),
            "pass_count": task_matrix.get("pass_count", 0),
            "fail_count": task_matrix.get("fail_count", 0),
            "incomplete_count": task_matrix.get("incomplete_count", 0),
        },
        "recommended_next_action": _recommended_environment_action(rows=rows, benchmark_status=benchmark_status),
        "summary": (
            "Relaytic separated model-quality evidence from environment readiness and found the environment ready."
            if overall == "pass"
            else "Relaytic separated model-quality evidence from environment readiness and found workflow or benchmark-environment gaps."
        ),
        "trace": _trace(["aml_workflow_task_matrix", "aml_benchmark_environment_scorecard"]),
    }


def _build_failure_report(
    *,
    generated_at: str,
    task_matrix: dict[str, Any],
    environment_scorecard: dict[str, Any],
    benchmark_environment_scorecard: dict[str, Any],
) -> dict[str, Any]:
    rows = [_as_dict(item) for item in _as_list(task_matrix.get("rows"))]
    blocking = [
        {
            "task_id": row.get("task_id"),
            "task_family": row.get("task_family"),
            "status": row.get("status"),
            "reason_code": row.get("reason_code"),
            "evidence_refs": row.get("evidence_refs", []),
            "options_now": row.get("options_now", []),
        }
        for row in rows
        if row.get("status") in {"fail", "incomplete"}
    ]
    benchmark_status = _clean_text(benchmark_environment_scorecard.get("overall_benchmark_environment_status"))
    if any(row.get("status") == "fail" and row.get("task_family") == "workflow_safety" for row in rows):
        primary = "workflow_safety_failed"
    elif any(row.get("status") == "fail" for row in rows):
        primary = "environment_task_failed"
    elif any(row.get("status") == "incomplete" for row in rows):
        primary = "environment_tasks_incomplete"
    elif benchmark_status in {"fail", "incomplete"}:
        primary = "benchmark_environment_incomplete"
    else:
        primary = "none"
    disagreement = bool(environment_scorecard.get("model_success_environment_success_disagreement"))
    return {
        "schema_version": AML_ENVIRONMENT_FAILURE_REPORT_SCHEMA_VERSION,
        "generated_at": generated_at,
        "status": "clear" if not blocking and benchmark_status == "pass" else "action_required",
        "primary_failure_kind": primary,
        "model_success_environment_success_disagreement": disagreement,
        "model_success_does_not_imply_environment_success": disagreement,
        "model_quality_status": environment_scorecard.get("model_quality_status"),
        "environment_task_status": environment_scorecard.get("environment_task_status"),
        "benchmark_environment_status": benchmark_status,
        "blocking_task_count": len(blocking),
        "blocking_tasks": blocking,
        "benchmark_environment_blockers": _benchmark_blockers(benchmark_environment_scorecard),
        "recommended_next_step": _recommended_failure_step(primary=primary, blocking=blocking, benchmark_status=benchmark_status),
        "summary": (
            "Model-quality evidence is present, but Relaytic does not treat it as environment success."
            if disagreement
            else "Relaytic found no model/environment success disagreement."
        ),
        "trace": _trace(["aml_environment_scorecard", "aml_workflow_task_matrix", "aml_benchmark_environment_scorecard"]),
    }


def _build_environment_manifest(
    *,
    generated_at: str,
    run_dir: Path,
    source_refs: list[str],
    task_matrix: dict[str, Any],
    environment_scorecard: dict[str, Any],
    benchmark_environment_scorecard: dict[str, Any],
    failure_report: dict[str, Any],
) -> dict[str, Any]:
    return {
        "schema_version": AML_EVAL_ENVIRONMENT_MANIFEST_SCHEMA_VERSION,
        "generated_at": generated_at,
        "status": environment_scorecard.get("overall_environment_status"),
        "run_id": run_dir.name,
        "local_first": True,
        "rowless": True,
        "environment_type": "aml_workflow_evaluation_environment",
        "required_outputs": list(AML_ENVIRONMENT_FILENAMES.values()),
        "required_output_count": len(AML_ENVIRONMENT_FILENAMES),
        "source_artifacts": source_refs,
        "source_artifact_count": len(source_refs),
        "task_count": task_matrix.get("task_count", 0),
        "model_quality_score": environment_scorecard.get("model_quality_score"),
        "environment_score": environment_scorecard.get("environment_score"),
        "benchmark_environment_status": benchmark_environment_scorecard.get("overall_benchmark_environment_status"),
        "primary_failure_kind": failure_report.get("primary_failure_kind"),
        "model_score_and_environment_score_separate": True,
        "policy": {
            "raw_rows_included": False,
            "model_success_is_not_environment_success": True,
            "incomplete_environment_task_blocks_environment_pass": True,
        },
        "summary": "Relaytic treats this AML run as an explicit evaluation environment with separate model and workflow scores.",
        "trace": _trace(["source_artifacts", "aml_workflow_task_matrix", "aml_environment_scorecard"]),
    }


def _inactive_environment_artifacts(
    *,
    generated_at: str,
    run_dir: Path,
    source_refs: list[str],
) -> dict[str, dict[str, Any]]:
    rows = [
        _task_row(
            task_id="model_quality",
            task_family="model_quality",
            label="Model-quality task",
            status="not_applicable",
            reason_code="aml_inactive",
            score=None,
            evidence_refs=source_refs,
            summary="AML environment scoring is not applicable because no active AML contract was found.",
            options_now=["run_aml_contract_first"],
        ),
        _task_row(
            task_id="unsafe_steering_rejection",
            task_family="workflow_safety",
            label="Unsafe steering rejection",
            status="not_applicable",
            reason_code="aml_inactive",
            score=None,
            evidence_refs=source_refs,
            trace_backed=False,
            summary="No AML environment safety task is active for this run.",
            options_now=["run_aml_contract_first"],
        ),
    ]
    matrix = _build_workflow_task_matrix(generated_at=generated_at, task_rows=rows)
    matrix["status"] = "not_applicable"
    benchmark = {
        "schema_version": AML_BENCHMARK_ENVIRONMENT_SCORECARD_SCHEMA_VERSION,
        "generated_at": generated_at,
        "status": "not_applicable",
        "overall_benchmark_environment_status": "not_applicable",
        "named_benchmark_family": None,
        "reproducibility_status": "not_applicable",
        "claim_safety_status": "not_applicable",
        "benchmark_relevance_status": "not_applicable",
        "benchmark_environment_score": None,
        "evidence_refs": source_refs,
        "summary": "AML benchmark-environment scoring is not applicable because the AML domain contract is inactive.",
        "trace": _trace(["aml_domain_contract"]),
    }
    scorecard = {
        "schema_version": AML_ENVIRONMENT_SCORECARD_SCHEMA_VERSION,
        "generated_at": generated_at,
        "status": "not_applicable",
        "overall_environment_status": "not_applicable",
        "model_score_and_environment_score_separate": True,
        "model_quality_score": None,
        "environment_score": None,
        "workflow_safety_score": None,
        "public_claim_discipline_score": None,
        "benchmark_environment_score": None,
        "benchmark_environment_status": "not_applicable",
        "model_success": False,
        "environment_success": False,
        "model_success_does_not_imply_environment_success": False,
        "model_success_environment_success_disagreement": False,
        "unsafe_steering_status": "not_applicable",
        "unsafe_steering_trace_backed": False,
        "recommended_next_action": "activate_aml_contract",
        "summary": "AML evaluation-environment scoring is inactive for this run.",
        "trace": _trace(["aml_domain_contract"]),
    }
    failure = {
        "schema_version": AML_ENVIRONMENT_FAILURE_REPORT_SCHEMA_VERSION,
        "generated_at": generated_at,
        "status": "not_applicable",
        "primary_failure_kind": "not_applicable",
        "model_success_environment_success_disagreement": False,
        "model_success_does_not_imply_environment_success": False,
        "model_quality_status": "not_applicable",
        "environment_task_status": "not_applicable",
        "benchmark_environment_status": "not_applicable",
        "blocking_task_count": 0,
        "blocking_tasks": [],
        "benchmark_environment_blockers": [],
        "recommended_next_step": "activate_aml_contract",
        "summary": "No AML environment failure report is required for an inactive AML run.",
        "trace": _trace(["aml_domain_contract"]),
    }
    manifest = {
        "schema_version": AML_EVAL_ENVIRONMENT_MANIFEST_SCHEMA_VERSION,
        "generated_at": generated_at,
        "status": "not_applicable",
        "run_id": run_dir.name,
        "local_first": True,
        "rowless": True,
        "environment_type": "aml_workflow_evaluation_environment",
        "required_outputs": list(AML_ENVIRONMENT_FILENAMES.values()),
        "required_output_count": len(AML_ENVIRONMENT_FILENAMES),
        "source_artifacts": source_refs,
        "source_artifact_count": len(source_refs),
        "task_count": matrix.get("task_count", 0),
        "model_quality_score": None,
        "environment_score": None,
        "benchmark_environment_status": "not_applicable",
        "primary_failure_kind": "not_applicable",
        "model_score_and_environment_score_separate": True,
        "policy": {
            "raw_rows_included": False,
            "model_success_is_not_environment_success": True,
            "incomplete_environment_task_blocks_environment_pass": True,
        },
        "summary": "Relaytic found no active AML environment to score.",
        "trace": _trace(["aml_domain_contract"]),
    }
    return {
        "aml_eval_environment_manifest": manifest,
        "aml_environment_scorecard": scorecard,
        "aml_workflow_task_matrix": matrix,
        "aml_environment_failure_report": failure,
        "aml_benchmark_environment_scorecard": benchmark,
    }


def _task_row(
    *,
    task_id: str,
    task_family: str,
    label: str,
    status: str,
    reason_code: str,
    score: float | None,
    evidence_refs: list[str],
    summary: str,
    options_now: list[str],
    trace_backed: bool | None = None,
    details: dict[str, Any] | None = None,
) -> dict[str, Any]:
    row = {
        "task_id": task_id,
        "task_family": task_family,
        "label": label,
        "status": status,
        "score": score,
        "reason_code": reason_code,
        "evidence_refs": evidence_refs,
        "trace_backed": bool(trace_backed) if trace_backed is not None else False,
        "environment_not_model_only": task_family != "model_quality",
        "summary": summary,
        "options_now": options_now,
    }
    if details:
        row["details"] = details
    return row


def _read_source_payloads(root: Path) -> dict[str, dict[str, Any]]:
    payloads: dict[str, dict[str, Any]] = {}
    for key, filename in _SOURCE_FILENAMES.items():
        payloads[key] = _read_json(root / filename)
    return payloads


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return value if isinstance(value, dict) else {}


def _source_refs(payloads: dict[str, dict[str, Any]]) -> list[str]:
    return [
        _SOURCE_FILENAMES[key]
        for key, value in payloads.items()
        if isinstance(value, dict) and bool(value)
    ]


def _existing_refs(payloads: dict[str, dict[str, Any]], keys: list[str]) -> list[str]:
    refs = []
    for key in keys:
        if payloads.get(key):
            refs.append(_SOURCE_FILENAMES.get(key, f"{key}.json"))
    return refs


def _aml_active(payloads: dict[str, dict[str, Any]]) -> bool:
    domain = payloads["aml_domain_contract"]
    if domain.get("aml_active") is True:
        return True
    if _status(domain) in _ACTIVE_STATUSES and _clean_text(domain.get("domain_focus")):
        return True
    return any(
        bool(payloads.get(key))
        for key in (
            "aml_benchmark_manifest",
            "aml_public_claim_guard",
            "aml_benchmark_relevance_scorecard",
            "alert_queue_policy",
            "alert_queue_rankings",
            "aml_temporal_benchmark_claim_report",
        )
    )


def _benchmark_reproducibility_status(payloads: dict[str, dict[str, Any]]) -> tuple[str, str]:
    has_manifest = bool(payloads["manifest"])
    has_summary = bool(payloads["run_summary"])
    has_lineage = bool(payloads["data_copy_manifest"] or payloads["materialization_cache_index"] or payloads["artifact_dependency_graph"])
    if has_manifest and has_summary and has_lineage:
        return "pass", "manifest_summary_and_lineage_present"
    if has_manifest or has_summary:
        return "incomplete", "reproducibility_lineage_incomplete"
    return "incomplete", "manifest_or_summary_missing"


def _benchmark_claim_safety_status(
    *,
    public_guard: dict[str, Any],
    paper_guard: dict[str, Any],
    release_gate: dict[str, Any],
    temporal_guard: dict[str, Any],
) -> tuple[str, str]:
    blockers = []
    for payload in (public_guard, paper_guard, release_gate, temporal_guard):
        blockers.extend(str(item) for item in _as_list(payload.get("claim_blockers")))
        blockers.extend(str(item) for item in _as_list(payload.get("blocked_reason_codes")))
    hard_allowed = _truthy(
        public_guard.get("hard_public_claim_allowed"),
        paper_guard.get("safe_to_cite_publicly"),
        release_gate.get("safe_to_cite_publicly"),
    )
    supporting_or_blocked = _truthy(
        public_guard.get("supporting_public_claim_allowed"),
        temporal_guard.get("supporting_temporal_evidence_allowed"),
    ) or temporal_guard.get("temporal_public_claim_allowed") is False
    if hard_allowed and blockers:
        return "fail", "hard_claim_allowed_despite_blockers"
    if hard_allowed or supporting_or_blocked:
        return "pass", "claim_boundaries_explicit"
    if public_guard or paper_guard or release_gate or temporal_guard:
        return "incomplete", "claim_boundary_evidence_incomplete"
    return "incomplete", "claim_safety_guard_missing"


def _benchmark_relevance_status(
    *,
    manifest: dict[str, Any],
    relevance: dict[str, Any],
    family: str | None,
) -> tuple[str, str]:
    supported_count = _safe_int(relevance.get("supported_family_count"))
    rows = [_as_dict(row) for row in _as_list(relevance.get("rows"))]
    supported_rows = [
        row for row in rows if _clean_text(row.get("support_level")) in {"supported", "direct", "strong", "native"}
    ]
    if family and (supported_count > 0 or supported_rows or manifest):
        return "pass", "named_aml_benchmark_family_supported"
    if family:
        return "incomplete", "named_family_missing_support_evidence"
    return "incomplete", "named_aml_benchmark_family_missing"


def _named_benchmark_family(payloads: dict[str, dict[str, Any]]) -> str | None:
    manifest = payloads["aml_benchmark_manifest"]
    relevance = payloads["aml_benchmark_relevance_scorecard"]
    for key in ("dataset_family", "benchmark_family", "benchmark_track", "workload_family"):
        text = _clean_text(manifest.get(key))
        if text:
            return text
    rows = [_as_dict(row) for row in _as_list(relevance.get("rows"))]
    for row in rows:
        text = _clean_text(row.get("benchmark_family")) or _clean_text(row.get("dataset_family"))
        if text:
            return text
    return None


def _benchmark_blockers(scorecard: dict[str, Any]) -> list[dict[str, str]]:
    blockers = []
    for key, label in (
        ("reproducibility_status", "reproducibility"),
        ("claim_safety_status", "claim_safety"),
        ("benchmark_relevance_status", "benchmark_relevance"),
    ):
        status = _clean_text(scorecard.get(key))
        if status in {"fail", "incomplete"}:
            reason_key = key.replace("_status", "_reason")
            blockers.append(
                {
                    "dimension": label,
                    "status": status,
                    "reason_code": _clean_text(scorecard.get(reason_key)) or "unknown",
                }
            )
    return blockers


def _recommended_environment_action(*, rows: list[dict[str, Any]], benchmark_status: str) -> str:
    failing = next((row for row in rows if row.get("status") == "fail"), None)
    incomplete = next((row for row in rows if row.get("status") == "incomplete"), None)
    row = failing or incomplete
    if row:
        options = _as_list(row.get("options_now"))
        if options:
            return str(options[0])
        return f"resolve_{row.get('task_id')}"
    if benchmark_status in {"fail", "incomplete"}:
        return "resolve_benchmark_environment_scorecard"
    return "ready_for_environment_benchmark_review"


def _recommended_failure_step(*, primary: str, blocking: list[dict[str, Any]], benchmark_status: str) -> str:
    if blocking:
        options = _as_list(blocking[0].get("options_now"))
        if options:
            return str(options[0])
        return f"resolve_{blocking[0].get('task_id')}"
    if benchmark_status in {"fail", "incomplete"}:
        return "resolve_benchmark_environment_scorecard"
    if primary == "none":
        return "ready_for_environment_benchmark_review"
    return "inspect_aml_environment_failure_report"


def _mean_task_score(rows: list[dict[str, Any]]) -> float | None:
    values = []
    for row in rows:
        status = _clean_text(row.get("status"))
        if status == "pass":
            values.append(1.0)
        elif status == "fail":
            values.append(0.0)
        elif status in {"incomplete", "not_applicable"}:
            values.append(0.0)
    return _mean_score(values)


def _mean_score(values: list[float | None]) -> float | None:
    clean = [float(value) for value in values if value is not None]
    if not clean:
        return None
    return round(sum(clean) / len(clean), 4)


def _status_score(status: str) -> float | None:
    normalized = _clean_text(status)
    if normalized == "pass":
        return 1.0
    if normalized == "fail":
        return 0.0
    if normalized == "incomplete":
        return 0.0
    return None


def _risk_flags(payload: dict[str, Any]) -> list[str]:
    flags = []
    for key in ("risk_flags", "reason_codes", "blocked_reason_codes", "findings"):
        for item in _as_list(payload.get(key)):
            if isinstance(item, dict):
                text = _clean_text(item.get("risk_flag")) or _clean_text(item.get("reason_code")) or _clean_text(item.get("finding_id"))
            else:
                text = _clean_text(item)
            if text:
                flags.append(text)
    return flags


def _trace(source_refs: list[str]) -> dict[str, Any]:
    return {
        "source_refs": source_refs,
        "raw_rows_included": False,
    }


def _as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _as_list(value: Any) -> list[Any]:
    if isinstance(value, list):
        return value
    return []


def _clean_text(value: Any) -> str:
    return str(value).strip().lower() if value is not None else ""


def _status(payload: dict[str, Any]) -> str:
    return _clean_text(payload.get("status") or payload.get("state") or payload.get("gate_status"))


def _safe_int(value: Any) -> int:
    try:
        if value is None or value == "":
            return 0
        return int(float(value))
    except (TypeError, ValueError):
        return 0


def _safe_float(value: Any) -> float:
    try:
        if value is None or value == "":
            return 0.0
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _truthy(*values: Any) -> bool:
    return any(value is True or _clean_text(value) in {"true", "yes", "1", "allowed"} for value in values)


def _first_present(*values: Any) -> Any:
    for value in values:
        if value not in (None, ""):
            return value
    return None


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()
