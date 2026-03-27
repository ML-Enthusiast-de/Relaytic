"""Slice 12 dojo mode and guarded self-improvement."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .models import (
    ARCHITECTURE_PROPOSALS_SCHEMA_VERSION,
    DOJO_HYPOTHESES_SCHEMA_VERSION,
    DOJO_PROMOTIONS_SCHEMA_VERSION,
    DOJO_RESULTS_SCHEMA_VERSION,
    DOJO_SESSION_SCHEMA_VERSION,
    ArchitectureProposals,
    DojoBundle,
    DojoControls,
    DojoHypotheses,
    DojoPromotions,
    DojoResults,
    DojoSession,
    DojoTrace,
    build_dojo_controls_from_policy,
    dojo_bundle_from_dict,
)
from .storage import read_dojo_bundle


@dataclass(frozen=True)
class DojoRunResult:
    bundle: DojoBundle
    review_markdown: str


def run_dojo_review(
    *,
    run_dir: str | Path,
    policy: dict[str, Any],
    planning_bundle: dict[str, Any] | None = None,
    research_bundle: dict[str, Any] | None = None,
    benchmark_bundle: dict[str, Any] | None = None,
    decision_bundle: dict[str, Any] | None = None,
    profiles_bundle: dict[str, Any] | None = None,
    control_bundle: dict[str, Any] | None = None,
) -> DojoRunResult:
    controls = build_dojo_controls_from_policy(policy)
    planning_bundle = planning_bundle or {}
    research_bundle = research_bundle or {}
    benchmark_bundle = benchmark_bundle or {}
    decision_bundle = decision_bundle or {}
    profiles_bundle = profiles_bundle or {}
    control_bundle = control_bundle or {}

    plan = _bundle_item(planning_bundle, "plan")
    execution_summary = dict(plan.get("execution_summary") or {})
    benchmark_parity = _bundle_item(benchmark_bundle, "benchmark_parity_report")
    beat_target = _bundle_item(benchmark_bundle, "beat_target_contract")
    method_transfer = _bundle_item(research_bundle, "method_transfer_report")
    method_compiler = _bundle_item(decision_bundle, "method_compiler_report")
    quality_gate = _bundle_item(profiles_bundle, "quality_gate_report")
    control_audit = _bundle_item(control_bundle, "control_injection_audit")
    override_decision = _bundle_item(control_bundle, "override_decision")

    benchmark_state = _clean_text(beat_target.get("contract_state")) or _clean_text(benchmark_parity.get("parity_status")) or "not_available"
    quality_gate_status = _clean_text(quality_gate.get("gate_status")) or _clean_text(quality_gate.get("status"))
    quality_proxy_state = _quality_proxy_state(quality_gate_status)
    control_security_state = _control_security_state(control_audit=control_audit, override_decision=override_decision)
    selected_family = (
        _clean_text(execution_summary.get("selected_model_family"))
        or _clean_text(benchmark_parity.get("relaytic_family"))
        or _clean_text(benchmark_parity.get("winning_family"))
        or "current_route"
    )
    proposed_challenger_family = (
        _clean_text(method_compiler.get("top_compiled_challenger_family"))
        or _clean_text(benchmark_parity.get("winning_family"))
        or selected_family
    )
    transfer_count = len(method_transfer.get("accepted_candidates", [])) if isinstance(method_transfer.get("accepted_candidates"), list) else 0
    compiled_challenger_count = int(method_compiler.get("compiled_challenger_count", 0) or 0)
    compiled_feature_count = int(method_compiler.get("compiled_feature_count", 0) or 0)
    incumbent_present = bool(benchmark_parity.get("incumbent_present"))

    proposals = [
        {
            "proposal_id": f"route_prior_upgrade::{selected_family}",
            "category": "route_priors",
            "proposal_kind": "route_prior_upgrade",
            "title": f"Promote `{selected_family}` in future route priors",
            "rationale": "Recent benchmark and quality signals suggest this selected family is a good first-pass route candidate.",
            "expected_benefit": "Improve first-pass route ordering without changing current authoritative behavior.",
            "risk_level": "low",
            "quarantine_only": False,
            "source_artifacts": ["plan.json", "benchmark_parity_report.json", "quality_gate_report.json"],
            "proposed_change": {
                "preferred_family": selected_family,
                "change_scope": "planning_route_priors",
            },
        },
        {
            "proposal_id": f"challenger_design_upgrade::{proposed_challenger_family}",
            "category": "challenger_design",
            "proposal_kind": "challenger_design_upgrade",
            "title": f"Strengthen challenger design around `{proposed_challenger_family}`",
            "rationale": "Decision-lab and benchmark artifacts expose a reusable challenger pattern worth carrying forward under quarantine.",
            "expected_benefit": "Increase challenger usefulness in later bounded follow-up rounds.",
            "risk_level": "medium",
            "quarantine_only": False,
            "source_artifacts": ["benchmark_gap_report.json", "compiled_challenger_templates.json", "beat_target_contract.json"],
            "proposed_change": {
                "preferred_challenger_family": proposed_challenger_family,
                "change_scope": "challenger_design",
                "compiled_candidate_count": compiled_challenger_count,
            },
        },
        {
            "proposal_id": f"method_compiler_upgrade::{max(transfer_count, compiled_feature_count)}",
            "category": "method_compiler",
            "proposal_kind": "method_compiler_upgrade",
            "title": "Carry forward validated method-compiler heuristics",
            "rationale": "Accepted research transfer ideas and compiled feature/challenger outputs can become reusable heuristics if benchmark and quality gates hold.",
            "expected_benefit": "Improve future compiled challenger and feature suggestions without directly mutating execution logic.",
            "risk_level": "medium",
            "quarantine_only": False,
            "source_artifacts": ["method_transfer_report.json", "method_compiler_report.json", "decision_world_model.json"],
            "proposed_change": {
                "accepted_transfer_count": transfer_count,
                "compiled_challenger_count": compiled_challenger_count,
                "compiled_feature_count": compiled_feature_count,
                "change_scope": "method_compiler_heuristics",
            },
        },
    ]
    architecture_items = (
        [
            {
                "proposal_id": "architecture_proposal::controller_refactor",
                "category": "architecture",
                "proposal_kind": "architecture_proposal",
                "title": "Evaluate a deeper controller/search refactor under later dojo phases",
                "rationale": "Architecture proposals stay explicitly quarantined until later slices provide stronger trace and security-eval proof.",
                "expected_benefit": "Reserve high-impact architecture ideas without letting them drift into current default behavior.",
                "risk_level": "high",
                "quarantine_only": True,
                "source_artifacts": ["handoff_controller_report.json", "control_challenge_report.json", "semantic_proof_report.json"],
                "proposed_change": {
                    "change_scope": "architecture",
                    "default_behavior_changed": False,
                },
            }
        ]
        if controls.allow_architecture_proposals
        else []
    )

    evaluation = _evaluate_proposals(
        controls=controls,
        proposals=proposals,
        architecture_items=architecture_items,
        benchmark_state=benchmark_state,
        quality_proxy_state=quality_proxy_state,
        control_security_state=control_security_state,
    )

    trace = _trace(
        note="dojo review derived quarantined self-improvement proposals from benchmark, profile, control, and decision artifacts",
        evidence=[
            "benchmark_parity_report.json",
            "beat_target_contract.json",
            "quality_gate_report.json",
            "control_injection_audit.json",
            "method_compiler_report.json",
        ],
    )
    session = DojoSession(
        schema_version=DOJO_SESSION_SCHEMA_VERSION,
        generated_at=_utc_now(),
        controls=controls,
        status="ok" if controls.enabled else "disabled",
        quarantine_active=True,
        benchmark_state=benchmark_state,
        quality_gate_status=quality_gate_status,
        control_security_state=control_security_state,
        incumbent_present=incumbent_present,
        active_promotion_count=len(evaluation["active_promotions"]),
        rejected_count=len(evaluation["rejected"]),
        quarantined_count=len(evaluation["quarantined"]),
        summary=(
            f"Relaytic reviewed {len(proposals) + len(architecture_items)} dojo proposals under quarantine and "
            f"kept `{len(evaluation['active_promotions'])}` active promotions, `{len(evaluation['rejected'])}` rejections, "
            f"and `{len(evaluation['quarantined'])}` quarantined proposals."
        ),
        trace=trace,
    )
    hypotheses = DojoHypotheses(
        schema_version=DOJO_HYPOTHESES_SCHEMA_VERSION,
        generated_at=_utc_now(),
        controls=controls,
        status="materialized" if controls.enabled else "disabled",
        proposal_count=len(proposals),
        proposals=proposals,
        summary="Relaytic materialized deterministic self-improvement hypotheses and kept them non-authoritative until validation passed.",
        trace=trace,
    )
    results = DojoResults(
        schema_version=DOJO_RESULTS_SCHEMA_VERSION,
        generated_at=_utc_now(),
        controls=controls,
        status="validated" if controls.enabled else "disabled",
        promoted_count=sum(1 for item in evaluation["results"] if item.get("decision") == "promoted"),
        rejected_count=sum(1 for item in evaluation["results"] if item.get("decision") == "rejected"),
        quarantined_count=sum(1 for item in evaluation["results"] if item.get("decision") == "quarantined"),
        results=evaluation["results"],
        summary="Relaytic evaluated dojo proposals against benchmark, quality-proxy, and control-security gates before any promotion.",
        trace=trace,
    )
    promotions = DojoPromotions(
        schema_version=DOJO_PROMOTIONS_SCHEMA_VERSION,
        generated_at=_utc_now(),
        controls=controls,
        status="active" if evaluation["active_promotions"] else "quarantined_only",
        active_promotions=evaluation["active_promotions"],
        rejected_proposals=evaluation["rejected"],
        quarantined_proposals=evaluation["quarantined"],
        rolled_back_promotions=[],
        promotion_ledger=evaluation["ledger"],
        summary="Relaytic writes explicit promotion, rejection, quarantine, and rollback-ready dojo state instead of mutating defaults silently.",
        trace=trace,
    )
    architecture = ArchitectureProposals(
        schema_version=ARCHITECTURE_PROPOSALS_SCHEMA_VERSION,
        generated_at=_utc_now(),
        controls=controls,
        status="quarantined",
        proposal_count=len(architecture_items),
        proposals=architecture_items,
        summary="Architecture proposals remain quarantined in early dojo scope and cannot become default behavior here.",
        trace=trace,
    )
    bundle = DojoBundle(
        dojo_session=session,
        dojo_hypotheses=hypotheses,
        dojo_results=results,
        dojo_promotions=promotions,
        architecture_proposals=architecture,
    )
    return DojoRunResult(bundle=bundle, review_markdown=render_dojo_review_markdown(bundle.to_dict()))


def rollback_dojo_promotion(
    *,
    run_dir: str | Path,
    policy: dict[str, Any],
    proposal_id: str,
    reason: str | None = None,
) -> DojoRunResult:
    root = Path(run_dir)
    payload = read_dojo_bundle(root)
    if not payload:
        raise ValueError(f"No Slice 12 dojo artifacts found in {root}.")
    bundle = dojo_bundle_from_dict(payload)
    promotions_payload = bundle.dojo_promotions.to_dict()
    results_payload = bundle.dojo_results.to_dict()
    session_payload = bundle.dojo_session.to_dict()

    active = [dict(item) for item in promotions_payload.get("active_promotions", []) if isinstance(item, dict)]
    match = None
    remaining: list[dict[str, Any]] = []
    for item in active:
        if str(item.get("proposal_id", "")).strip() == proposal_id and match is None:
            match = dict(item)
            continue
        remaining.append(item)
    if match is None:
        raise ValueError(f"No active dojo promotion found for proposal id `{proposal_id}`.")

    rolled_back = [dict(item) for item in promotions_payload.get("rolled_back_promotions", []) if isinstance(item, dict)]
    ledger = [dict(item) for item in promotions_payload.get("promotion_ledger", []) if isinstance(item, dict)]
    rollback_record = {
        **match,
        "status": "rolled_back",
        "rolled_back_at": _utc_now(),
        "rollback_reason": _clean_text(reason) or "manual_rollback",
    }
    rolled_back.append(rollback_record)
    ledger.append(
        {
            "entry_type": "rollback",
            "proposal_id": proposal_id,
            "proposal_kind": match.get("proposal_kind"),
            "recorded_at": rollback_record["rolled_back_at"],
            "reason": rollback_record["rollback_reason"],
        }
    )
    promotions_payload["active_promotions"] = remaining
    promotions_payload["rolled_back_promotions"] = rolled_back
    promotions_payload["promotion_ledger"] = ledger
    promotions_payload["status"] = "active" if remaining else "quarantined_only"
    promotions_payload["summary"] = (
        f"Relaytic now tracks `{len(remaining)}` active dojo promotions and `{len(rolled_back)}` rolled-back promotions."
    )

    results_entries = [dict(item) for item in results_payload.get("results", []) if isinstance(item, dict)]
    for item in results_entries:
        if str(item.get("proposal_id", "")).strip() != proposal_id:
            continue
        item["decision"] = "rolled_back"
        item["rolled_back"] = True
        reasons = [str(reason_item) for reason_item in item.get("reasons", []) if str(reason_item).strip()]
        reasons.append(f"Rolled back: {rollback_record['rollback_reason']}")
        item["reasons"] = reasons
        break
    results_payload["results"] = results_entries
    results_payload["promoted_count"] = len(remaining)
    results_payload["summary"] = (
        f"Relaytic rollback left `{len(remaining)}` active dojo promotions and preserved the full decision ledger."
    )

    session_payload["active_promotion_count"] = len(remaining)
    session_payload["summary"] = (
        f"Relaytic rolled back dojo proposal `{proposal_id}` and now has `{len(remaining)}` active promotions remaining."
    )

    updated_bundle = dojo_bundle_from_dict(
        {
            "dojo_session": session_payload,
            "dojo_hypotheses": bundle.dojo_hypotheses.to_dict(),
            "dojo_results": results_payload,
            "dojo_promotions": promotions_payload,
            "architecture_proposals": bundle.architecture_proposals.to_dict(),
        }
    )
    return DojoRunResult(bundle=updated_bundle, review_markdown=render_dojo_review_markdown(updated_bundle.to_dict()))


def render_dojo_review_markdown(bundle: DojoBundle | dict[str, Any]) -> str:
    payload = bundle.to_dict() if isinstance(bundle, DojoBundle) else dict(bundle)
    session = dict(payload.get("dojo_session", {}))
    results = dict(payload.get("dojo_results", {}))
    promotions = dict(payload.get("dojo_promotions", {}))
    lines = [
        "# Relaytic Dojo Review",
        "",
        f"- Status: `{session.get('status') or 'unknown'}`",
        f"- Benchmark state: `{session.get('benchmark_state') or 'unknown'}`",
        f"- Quality gate: `{session.get('quality_gate_status') or 'unknown'}`",
        f"- Control security: `{session.get('control_security_state') or 'unknown'}`",
        f"- Active promotions: `{session.get('active_promotion_count', 0)}`",
        f"- Rejected proposals: `{session.get('rejected_count', 0)}`",
        f"- Quarantined proposals: `{session.get('quarantined_count', 0)}`",
        "",
        "## Promotions",
    ]
    active = [dict(item) for item in promotions.get("active_promotions", []) if isinstance(item, dict)]
    if not active:
        lines.append("- No active dojo promotions.")
    else:
        for item in active[:6]:
            lines.append(
                f"- `{item.get('proposal_id')}` `{item.get('proposal_kind')}`: "
                f"{str(item.get('promotion_reason') or 'promoted under quarantine').strip()}"
            )
    result_rows = [dict(item) for item in results.get("results", []) if isinstance(item, dict)]
    if result_rows:
        lines.extend(["", "## Decisions"])
        for item in result_rows[:8]:
            lines.append(f"- `{item.get('proposal_id')}` -> `{item.get('decision')}`")
    return "\n".join(lines).rstrip() + "\n"


def _evaluate_proposals(
    *,
    controls: DojoControls,
    proposals: list[dict[str, Any]],
    architecture_items: list[dict[str, Any]],
    benchmark_state: str,
    quality_proxy_state: str,
    control_security_state: str,
) -> dict[str, Any]:
    results: list[dict[str, Any]] = []
    active_promotions: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []
    quarantined: list[dict[str, Any]] = []
    ledger: list[dict[str, Any]] = []
    promotion_slots_remaining = controls.max_active_promotions

    benchmark_pass = benchmark_state == "met" if controls.require_benchmark_gate else True
    quality_pass = quality_proxy_state == "pass" if controls.require_quality_proxy_gate else True
    control_pass = control_security_state == "pass" if controls.require_control_security_gate else True

    for proposal in proposals:
        reasons: list[str] = []
        if not controls.enabled:
            decision = "quarantined"
            reasons.append("Dojo is disabled by policy.")
        elif proposal["category"] == "method_compiler" and not controls.allow_method_self_improvement:
            decision = "quarantined"
            reasons.append("Method self-improvement is disabled by policy for this dojo review.")
        elif not benchmark_pass:
            decision = "rejected"
            reasons.append(f"Benchmark gate failed because beat-target state is `{benchmark_state}`.")
        elif not quality_pass:
            decision = "rejected"
            reasons.append(f"Quality-proxy gate failed because visible quality gate is `{quality_proxy_state}`.")
        elif not control_pass:
            decision = "rejected"
            reasons.append(f"Control-security gate failed because skeptical-control state is `{control_security_state}`.")
        elif promotion_slots_remaining <= 0:
            decision = "quarantined"
            reasons.append("Promotion budget is exhausted for this dojo session.")
        else:
            decision = "promoted"
            reasons.append("Proposal passed benchmark, quality-proxy, and control-security gates under quarantine.")
            promotion_slots_remaining -= 1

        result = {
            "proposal_id": proposal["proposal_id"],
            "proposal_kind": proposal["proposal_kind"],
            "category": proposal["category"],
            "decision": decision,
            "benchmark_gate": {"status": "pass" if benchmark_pass else "fail", "state": benchmark_state},
            "golden_case_gate": {
                "status": "pass" if quality_pass else "fail",
                "state": quality_proxy_state,
                "validation_basis": "quality_contract_proxy",
            },
            "control_security_gate": {"status": "pass" if control_pass else "fail", "state": control_security_state},
            "reasons": reasons,
            "quarantine_only": False,
        }
        results.append(result)
        if decision == "promoted":
            active_promotions.append(
                {
                    "proposal_id": proposal["proposal_id"],
                    "proposal_kind": proposal["proposal_kind"],
                    "category": proposal["category"],
                    "promoted_at": _utc_now(),
                    "promotion_reason": reasons[0],
                    "quarantine_scope": "advisory_only",
                    "default_behavior_changed": False,
                }
            )
        elif decision == "rejected":
            rejected.append(
                {
                    "proposal_id": proposal["proposal_id"],
                    "proposal_kind": proposal["proposal_kind"],
                    "category": proposal["category"],
                    "reasons": reasons,
                }
            )
        else:
            quarantined.append(
                {
                    "proposal_id": proposal["proposal_id"],
                    "proposal_kind": proposal["proposal_kind"],
                    "category": proposal["category"],
                    "reasons": reasons,
                }
            )
        ledger.append(
            {
                "entry_type": decision,
                "proposal_id": proposal["proposal_id"],
                "proposal_kind": proposal["proposal_kind"],
                "recorded_at": _utc_now(),
                "reason": reasons[0],
            }
        )

    for proposal in architecture_items:
        reasons = ["Architecture proposals stay quarantined in early dojo scope until later trace and security-eval slices exist."]
        results.append(
            {
                "proposal_id": proposal["proposal_id"],
                "proposal_kind": proposal["proposal_kind"],
                "category": proposal["category"],
                "decision": "quarantined",
                "benchmark_gate": {"status": "not_applied", "state": benchmark_state},
                "golden_case_gate": {"status": "not_applied", "state": quality_proxy_state, "validation_basis": "quality_contract_proxy"},
                "control_security_gate": {"status": "not_applied", "state": control_security_state},
                "reasons": reasons,
                "quarantine_only": True,
            }
        )
        quarantined.append(
            {
                "proposal_id": proposal["proposal_id"],
                "proposal_kind": proposal["proposal_kind"],
                "category": proposal["category"],
                "reasons": reasons,
            }
        )
        ledger.append(
            {
                "entry_type": "quarantined",
                "proposal_id": proposal["proposal_id"],
                "proposal_kind": proposal["proposal_kind"],
                "recorded_at": _utc_now(),
                "reason": reasons[0],
            }
        )
    return {
        "results": results,
        "active_promotions": active_promotions,
        "rejected": rejected,
        "quarantined": quarantined,
        "ledger": ledger,
    }


def _control_security_state(*, control_audit: dict[str, Any], override_decision: dict[str, Any]) -> str:
    suspicious_count = int(control_audit.get("suspicious_count", 0) or 0)
    rejected_count = int(control_audit.get("rejected_count", 0) or 0)
    decision = _clean_text(override_decision.get("decision"))
    if suspicious_count > 0 or rejected_count > 0 or decision == "reject":
        return "fail"
    return "pass"


def _quality_proxy_state(quality_gate_status: str | None) -> str:
    if quality_gate_status in {"pass", "conditional_pass"}:
        return "pass"
    if quality_gate_status:
        return "fail"
    return "not_available"


def _bundle_item(bundle: dict[str, Any], key: str) -> dict[str, Any]:
    value = bundle.get(key, {})
    return dict(value) if isinstance(value, dict) else {}


def _trace(*, note: str, evidence: list[str]) -> DojoTrace:
    return DojoTrace(
        agent="dojo_referee",
        operating_mode="deterministic_quarantine",
        llm_used=False,
        llm_status="not_used",
        deterministic_evidence=evidence,
        advisory_notes=[note],
    )


def _clean_text(value: Any) -> str | None:
    text = str(value or "").strip()
    return text or None


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()
