"""Slice 09D privacy-safe research retrieval and method transfer."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
import re
from typing import Any

from .models import (
    BENCHMARK_REFERENCE_REPORT_SCHEMA_VERSION,
    EXTERNAL_RESEARCH_AUDIT_SCHEMA_VERSION,
    METHOD_TRANSFER_REPORT_SCHEMA_VERSION,
    RESEARCH_BRIEF_SCHEMA_VERSION,
    RESEARCH_QUERY_PLAN_SCHEMA_VERSION,
    RESEARCH_SOURCE_INVENTORY_SCHEMA_VERSION,
    BenchmarkReferenceReport,
    ExternalResearchAudit,
    MethodTransferReport,
    ResearchBrief,
    ResearchBundle,
    ResearchControls,
    ResearchQueryPlan,
    ResearchSourceInventory,
    ResearchTrace,
    build_research_controls_from_policy,
)
from .sources import gather_external_sources


@dataclass(frozen=True)
class ResearchRunResult:
    bundle: ResearchBundle
    review_markdown: str


def run_research_review(
    *,
    run_dir: str | Path,
    policy: dict[str, Any],
    mandate_bundle: dict[str, Any],
    context_bundle: dict[str, Any],
    intake_bundle: dict[str, Any] | None = None,
    investigation_bundle: dict[str, Any] | None = None,
    planning_bundle: dict[str, Any] | None = None,
    evidence_bundle: dict[str, Any] | None = None,
    memory_bundle: dict[str, Any] | None = None,
    intelligence_bundle: dict[str, Any] | None = None,
) -> ResearchRunResult:
    controls = build_research_controls_from_policy(policy)
    intake_bundle = intake_bundle or {}
    investigation_bundle = investigation_bundle or {}
    planning_bundle = planning_bundle or {}
    evidence_bundle = evidence_bundle or {}
    memory_bundle = memory_bundle or {}
    intelligence_bundle = intelligence_bundle or {}

    signature = _build_query_signature(
        run_dir=run_dir,
        mandate_bundle=mandate_bundle,
        context_bundle=context_bundle,
        intake_bundle=intake_bundle,
        investigation_bundle=investigation_bundle,
        planning_bundle=planning_bundle,
        evidence_bundle=evidence_bundle,
        memory_bundle=memory_bundle,
        intelligence_bundle=intelligence_bundle,
    )
    trace = ResearchTrace(
        agent="research_retrieval_agent",
        operating_mode="policy_gated_redacted_external_retrieval",
        llm_used=False,
        llm_status="not_requested",
        deterministic_evidence=[
            "redacted_run_signature",
            "rowless_query_builder",
            "typed_source_inventory",
            "method_transfer_distillation",
            "explicit_research_audit",
        ],
    )
    query_plan_payload = _build_query_plan(signature=signature, controls=controls)
    source_inventory_payload = gather_external_sources(
        controls=controls,
        queries=list(query_plan_payload["queries"]),
    )
    method_transfer_payload = _build_method_transfer_report(
        signature=signature,
        controls=controls,
        sources=list(source_inventory_payload.get("sources", [])),
        planning_bundle=planning_bundle,
        investigation_bundle=investigation_bundle,
        evidence_bundle=evidence_bundle,
    )
    benchmark_payload = _build_benchmark_reference_report(
        signature=signature,
        controls=controls,
        sources=list(source_inventory_payload.get("sources", [])),
    )
    brief_payload = _build_research_brief(
        controls=controls,
        query_plan=query_plan_payload,
        source_inventory=source_inventory_payload,
        method_transfer=method_transfer_payload,
        benchmark_report=benchmark_payload,
    )
    audit_payload = _build_external_research_audit(
        controls=controls,
        query_plan=query_plan_payload,
        source_inventory=source_inventory_payload,
    )
    generated_at = _utc_now()

    bundle = ResearchBundle(
        research_query_plan=ResearchQueryPlan(
            schema_version=RESEARCH_QUERY_PLAN_SCHEMA_VERSION,
            generated_at=generated_at,
            controls=controls,
            status=str(query_plan_payload["status"]),
            query_signature=dict(query_plan_payload["query_signature"]),
            redaction_summary=dict(query_plan_payload["redaction_summary"]),
            exported_fields=list(query_plan_payload["exported_fields"]),
            queries=list(query_plan_payload["queries"]),
            summary=str(query_plan_payload["summary"]),
            trace=trace,
        ),
        research_source_inventory=ResearchSourceInventory(
            schema_version=RESEARCH_SOURCE_INVENTORY_SCHEMA_VERSION,
            generated_at=generated_at,
            controls=controls,
            status=str(source_inventory_payload["status"]),
            queries_executed=list(source_inventory_payload.get("queries_executed", [])),
            sources=list(source_inventory_payload.get("sources", [])),
            source_counts=dict(source_inventory_payload["source_counts"]),
            endpoint_status=list(source_inventory_payload.get("endpoint_status", [])),
            summary=str(source_inventory_payload["summary"]),
            trace=trace,
        ),
        research_brief=ResearchBrief(
            schema_version=RESEARCH_BRIEF_SCHEMA_VERSION,
            generated_at=generated_at,
            controls=controls,
            status=str(brief_payload["status"]),
            top_findings=list(brief_payload["top_findings"]),
            contradictions=list(brief_payload["contradictions"]),
            recommended_followup_action=str(brief_payload["recommended_followup_action"]),
            confidence=str(brief_payload["confidence"]),
            summary=str(brief_payload["summary"]),
            trace=trace,
        ),
        method_transfer_report=MethodTransferReport(
            schema_version=METHOD_TRANSFER_REPORT_SCHEMA_VERSION,
            generated_at=generated_at,
            controls=controls,
            status=str(method_transfer_payload["status"]),
            accepted_candidates=list(method_transfer_payload["accepted_candidates"]),
            rejected_candidates=list(method_transfer_payload["rejected_candidates"]),
            advisory_candidates=list(method_transfer_payload["advisory_candidates"]),
            summary=str(method_transfer_payload["summary"]),
            trace=trace,
        ),
        benchmark_reference_report=BenchmarkReferenceReport(
            schema_version=BENCHMARK_REFERENCE_REPORT_SCHEMA_VERSION,
            generated_at=generated_at,
            controls=controls,
            status=str(benchmark_payload["status"]),
            benchmark_expected=bool(benchmark_payload["benchmark_expected"]),
            reference_count=int(benchmark_payload["reference_count"]),
            references=list(benchmark_payload["references"]),
            summary=str(benchmark_payload["summary"]),
            trace=trace,
        ),
        external_research_audit=ExternalResearchAudit(
            schema_version=EXTERNAL_RESEARCH_AUDIT_SCHEMA_VERSION,
            generated_at=generated_at,
            controls=controls,
            status=str(audit_payload["status"]),
            network_attempted=bool(audit_payload["network_attempted"]),
            network_allowed=bool(audit_payload["network_allowed"]),
            raw_rows_exported=bool(audit_payload["raw_rows_exported"]),
            identifier_leak_detected=bool(audit_payload["identifier_leak_detected"]),
            exported_fields=list(audit_payload["exported_fields"]),
            redactions=list(audit_payload["redactions"]),
            query_texts=list(audit_payload["query_texts"]),
            endpoints_contacted=list(audit_payload["endpoints_contacted"]),
            source_classes=list(audit_payload["source_classes"]),
            request_count=int(audit_payload["request_count"]),
            summary=str(audit_payload["summary"]),
            trace=trace,
        ),
    )
    return ResearchRunResult(
        bundle=bundle,
        review_markdown=render_research_review_markdown(bundle.to_dict()),
    )


def render_research_review_markdown(bundle: dict[str, Any]) -> str:
    query_plan = dict(bundle.get("research_query_plan", {}))
    inventory = dict(bundle.get("research_source_inventory", {}))
    brief = dict(bundle.get("research_brief", {}))
    transfer = dict(bundle.get("method_transfer_report", {}))
    benchmark = dict(bundle.get("benchmark_reference_report", {}))
    audit = dict(bundle.get("external_research_audit", {}))
    lines = [
        "# Relaytic Research Review",
        "",
        f"- Query status: `{query_plan.get('status') or 'unknown'}`",
        f"- Source inventory status: `{inventory.get('status') or 'unknown'}`",
        f"- Recommended follow-up: `{brief.get('recommended_followup_action') or 'none'}`",
        f"- Confidence: `{brief.get('confidence') or 'unknown'}`",
        f"- Accepted transfers: `{len(transfer.get('accepted_candidates', []))}`",
        f"- Benchmark references: `{benchmark.get('reference_count', 0)}`",
        f"- Network allowed: `{audit.get('network_allowed')}`",
    ]
    findings = list(brief.get("top_findings", []))
    if findings:
        lines.extend(["", "## Top Findings"])
        for item in findings[:4]:
            lines.append(f"- `{item.get('finding_type') or 'finding'}`: {item.get('summary') or 'No summary provided.'}")
    accepted = list(transfer.get("accepted_candidates", []))
    if accepted:
        lines.extend(["", "## Accepted Transfers"])
        for item in accepted[:4]:
            lines.append(
                f"- `{item.get('candidate_kind')}` -> `{item.get('value')}`: {item.get('acceptance_reason')}"
            )
    rejected = list(transfer.get("rejected_candidates", []))
    if rejected:
        lines.extend(["", "## Rejected Suggestions"])
        for item in rejected[:3]:
            lines.append(
                f"- `{item.get('candidate_kind')}` -> `{item.get('value')}` rejected: {item.get('rejection_reason')}"
            )
    return "\n".join(lines).rstrip() + "\n"


def _build_query_signature(
    *,
    run_dir: str | Path,
    mandate_bundle: dict[str, Any],
    context_bundle: dict[str, Any],
    intake_bundle: dict[str, Any],
    investigation_bundle: dict[str, Any],
    planning_bundle: dict[str, Any],
    evidence_bundle: dict[str, Any],
    memory_bundle: dict[str, Any],
    intelligence_bundle: dict[str, Any],
) -> dict[str, Any]:
    del intake_bundle
    run_brief = _bundle_item(mandate_bundle, "run_brief")
    task_brief = _bundle_item(context_bundle, "task_brief")
    dataset_profile = _bundle_item(investigation_bundle, "dataset_profile")
    domain_memo = _bundle_item(investigation_bundle, "domain_memo")
    optimization_profile = _bundle_item(investigation_bundle, "optimization_profile")
    plan = _bundle_item(planning_bundle, "plan")
    audit_report = _bundle_item(evidence_bundle, "audit_report")
    belief_update = _bundle_item(evidence_bundle, "belief_update")
    semantic_debate = _bundle_item(intelligence_bundle, "semantic_debate_report")
    memory_retrieval = _bundle_item(memory_bundle, "memory_retrieval")
    target_column = str(plan.get("target_column") or task_brief.get("target_column") or "").strip()
    positive_rate = dataset_profile.get("positive_fraction")
    if positive_rate is None:
        positive_rate = dataset_profile.get("minority_fraction")
    benchmark_expected = _benchmark_expected(run_brief=run_brief, task_brief=task_brief)
    return {
        "run_id": str(Path(run_dir).name),
        "task_type": _clean_text(plan.get("task_type")) or _clean_text(task_brief.get("task_type_hint")) or "unknown",
        "domain_archetype": _clean_text(domain_memo.get("domain_archetype"))
        or _clean_text(task_brief.get("domain_archetype_hint"))
        or "general_tabular",
        "target_semantics": _generalize_target_name(target_column),
        "data_mode": _clean_text(dataset_profile.get("data_mode")) or "steady_state",
        "time_aware": bool(
            str(dataset_profile.get("timestamp_column", "")).strip()
            or str(plan.get("split_strategy", "")).strip().startswith("time")
        ),
        "row_count_bucket": _row_count_bucket(dataset_profile.get("row_count")),
        "primary_metric": _clean_text(plan.get("primary_metric"))
        or _clean_text(optimization_profile.get("primary_metric"))
        or "unknown",
        "split_strategy": _clean_text(plan.get("split_strategy")) or "unknown",
        "positive_rate_band": _positive_rate_band(positive_rate),
        "benchmark_expected": benchmark_expected,
        "readiness_level": _clean_text(audit_report.get("readiness_level")) or "unknown",
        "provisional_recommendation": _clean_text(audit_report.get("provisional_recommendation")) or "unknown",
        "semantic_followup": _clean_text(semantic_debate.get("recommended_followup_action")) or "none",
        "memory_analog_count": int(memory_retrieval.get("selected_analog_count", 0) or 0),
        "deployment_target": _clean_text(run_brief.get("deployment_target")) or "unspecified",
        "research_needs": _dedupe_strings(
            [
                _clean_text(semantic_debate.get("recommended_followup_action")) or "",
                _clean_text(belief_update.get("recommended_action")) or "",
                "benchmark_reference" if benchmark_expected else "",
                "rare_event_evaluation" if _positive_rate_band(positive_rate) in {"rare", "very_rare"} else "",
                "temporal_split" if bool(str(dataset_profile.get("timestamp_column", "")).strip()) else "",
            ]
        ),
    }


def _build_query_plan(*, signature: dict[str, Any], controls: ResearchControls) -> dict[str, Any]:
    task_type = str(signature.get("task_type", "unknown"))
    domain_archetype = str(signature.get("domain_archetype", "general_tabular"))
    target_semantics = str(signature.get("target_semantics", "generic_target"))
    primary_metric = str(signature.get("primary_metric", "unknown"))
    rare_event = str(signature.get("positive_rate_band", "unknown")) in {"rare", "very_rare"}
    data_mode = str(signature.get("data_mode", "steady_state"))
    benchmark_expected = bool(signature.get("benchmark_expected", False))
    query_terms = [
        (
            "methods",
            " ".join(
                part
                for part in [
                    _domain_phrase(domain_archetype),
                    _task_phrase(task_type, target_semantics),
                    "tabular machine learning",
                    "class imbalance" if rare_event else "",
                    primary_metric if primary_metric != "unknown" else "",
                ]
                if part
            ),
            ["paper", "implementation_doc"],
        ),
        (
            "evaluation",
            " ".join(
                part
                for part in [
                    _domain_phrase(domain_archetype),
                    _task_phrase(task_type, target_semantics),
                    "temporal split" if data_mode == "time_aware" or bool(signature.get("time_aware")) else "evaluation calibration",
                    primary_metric if primary_metric != "unknown" else "",
                ]
                if part
            ),
            ["paper", "benchmark_reference"],
        ),
    ]
    if benchmark_expected:
        query_terms.append(
            (
                "benchmark",
                " ".join(
                    part
                    for part in [
                        _domain_phrase(domain_archetype),
                        _task_phrase(task_type, target_semantics),
                        "benchmark baseline comparison",
                    ]
                    if part
                ),
                ["benchmark_reference", "paper"],
            )
        )
    queries = [
        {
            "query_id": f"research_{index + 1:02d}_{intent}",
            "intent": intent,
            "query_text": query_text,
            "source_classes": source_classes,
            "redacted": True,
            "rowless": True,
        }
        for index, (intent, query_text, source_classes) in enumerate(query_terms[: controls.max_queries])
    ]
    exported_fields = [
        "task_type",
        "domain_archetype",
        "target_semantics",
        "data_mode",
        "row_count_bucket",
        "primary_metric",
        "split_strategy",
        "positive_rate_band",
        "benchmark_expected",
        "deployment_target",
        "research_needs",
    ]
    redaction_summary = {
        "raw_rows_removed": True,
        "column_names_removed": True,
        "data_path_removed": True,
        "private_identifiers_removed": True,
        "redactions": [
            "raw_rows",
            "feature_columns",
            "full_target_name",
            "machine_paths",
            "operator_identifiers",
        ],
    }
    return {
        "status": "planned" if controls.enabled else "disabled",
        "query_signature": {key: signature[key] for key in exported_fields if key in signature},
        "redaction_summary": redaction_summary,
        "exported_fields": exported_fields,
        "queries": queries,
        "summary": f"Relaytic prepared {len(queries)} redacted external research querie(s) without exposing rows or private identifiers.",
    }


def _build_method_transfer_report(
    *,
    signature: dict[str, Any],
    controls: ResearchControls,
    sources: list[dict[str, Any]],
    planning_bundle: dict[str, Any],
    investigation_bundle: dict[str, Any],
    evidence_bundle: dict[str, Any],
) -> dict[str, Any]:
    del investigation_bundle, evidence_bundle
    if not controls.enabled:
        return {
            "status": "disabled",
            "accepted_candidates": [],
            "rejected_candidates": [],
            "advisory_candidates": [],
            "summary": "Research-driven method transfer is disabled by policy.",
        }
    plan = _bundle_item(planning_bundle, "plan")
    current_family = _clean_text(dict(plan.get("execution_summary") or {}).get("selected_model_family"))
    task_type = str(signature.get("task_type", "unknown"))
    positive_rate_band = str(signature.get("positive_rate_band", "unknown"))
    time_aware = bool(signature.get("time_aware", False))
    candidates: list[dict[str, Any]] = []
    for source in sources:
        text = " ".join(
            [
                str(source.get("title", "")),
                str(source.get("abstract_snippet", "")),
                str(source.get("query_text", "")),
            ]
        ).lower()
        source_ref = {
            "provider": source.get("provider"),
            "title": source.get("title"),
            "url": source.get("url"),
            "year": source.get("year"),
        }
        family = _suggest_model_family(text=text, task_type=task_type, time_aware=time_aware)
        if family:
            candidates.append(
                {
                    "candidate_kind": "challenger_family",
                    "value": family,
                    "source": source_ref,
                    "support_reason": "External paper or method reference suggested this model family.",
                }
            )
        if any(token in text for token in ("calibration", "threshold", "isotonic", "platt")) and task_type in {
            "binary_classification",
            "fraud_detection",
            "anomaly_detection",
            "multiclass_classification",
        }:
            candidates.append(
                {
                    "candidate_kind": "evaluation_design",
                    "value": "calibration_review",
                    "source": source_ref,
                    "support_reason": "External references emphasized calibration or thresholding.",
                }
            )
        if "accuracy" in text and positive_rate_band in {"rare", "very_rare"}:
            candidates.append(
                {
                    "candidate_kind": "metric_proposal",
                    "value": "accuracy",
                    "source": source_ref,
                    "support_reason": "External references mentioned accuracy as a possible evaluation metric.",
                }
            )
        if any(token in text for token in ("temporal split", "time split", "walk-forward", "chronological")):
            candidates.append(
                {
                    "candidate_kind": "split_strategy",
                    "value": "time_ordered_holdout",
                    "source": source_ref,
                    "support_reason": "External references emphasized temporal validation.",
                }
            )
        if any(token in text for token in ("more data", "additional data", "collect data", "hard negative")):
            candidates.append(
                {
                    "candidate_kind": "data_collection",
                    "value": "collect_targeted_examples",
                    "source": source_ref,
                    "support_reason": "External references suggested targeted additional data collection.",
                }
            )
    accepted: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []
    advisory: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    for candidate in candidates:
        key = (str(candidate["candidate_kind"]), str(candidate["value"]))
        if key in seen:
            continue
        seen.add(key)
        kind = str(candidate["candidate_kind"])
        value = str(candidate["value"])
        if kind == "challenger_family":
            if current_family and value == current_family:
                advisory.append(
                    {
                        **candidate,
                        "acceptance_reason": "The current route already uses this family; keep it as a benchmarkable reference, not a new challenger.",
                    }
                )
            elif _family_matches_task(value=value, task_type=task_type):
                accepted.append(
                    {
                        **candidate,
                        "acceptance_reason": "The suggested family is compatible with the current task and can widen challenger pressure.",
                    }
                )
            else:
                rejected.append(
                    {
                        **candidate,
                        "rejection_reason": "The suggested family does not match the current task type.",
                    }
                )
        elif kind == "metric_proposal" and value == "accuracy":
            rejected.append(
                {
                    **candidate,
                    "rejection_reason": "Local evidence shows a rare-event regime, so accuracy is too weak as the primary evaluation metric.",
                }
            )
        elif kind == "split_strategy":
            if time_aware:
                accepted.append(
                    {
                        **candidate,
                        "acceptance_reason": "Local evidence already shows time-aware structure, so temporal validation should stay explicit.",
                    }
                )
            else:
                rejected.append(
                    {
                        **candidate,
                        "rejection_reason": "Local evidence does not show a time-aware regime for this run.",
                    }
                )
        elif kind == "evaluation_design":
            accepted.append(
                {
                    **candidate,
                    "acceptance_reason": "Classification quality here can benefit from explicit calibration review.",
                }
            )
        elif kind == "data_collection":
            advisory.append(
                {
                    **candidate,
                    "acceptance_reason": "Additional targeted data is relevant but should remain advisory until the current bounded loop completes.",
                }
            )
    status = "ok" if accepted or rejected or advisory else ("no_results" if not sources else "no_transfer")
    return {
        "status": status,
        "accepted_candidates": accepted,
        "rejected_candidates": rejected,
        "advisory_candidates": advisory,
        "summary": _method_transfer_summary(accepted=accepted, rejected=rejected, advisory=advisory),
    }


def _build_benchmark_reference_report(
    *,
    signature: dict[str, Any],
    controls: ResearchControls,
    sources: list[dict[str, Any]],
) -> dict[str, Any]:
    benchmark_expected = bool(signature.get("benchmark_expected", False))
    references = [
        {
            "title": source.get("title"),
            "url": source.get("url"),
            "provider": source.get("provider"),
            "year": source.get("year"),
            "matched_query_id": source.get("query_id"),
            "benchmark_role": "reference_method_or_dataset",
        }
        for source in sources
        if str(source.get("source_type", "")) == "benchmark_reference"
    ]
    status = "disabled" if not controls.enabled else ("ok" if references else ("not_required" if not benchmark_expected else "needed"))
    return {
        "status": status,
        "benchmark_expected": benchmark_expected,
        "reference_count": len(references),
        "references": references[:8],
        "summary": _benchmark_summary(benchmark_expected=benchmark_expected, reference_count=len(references)),
    }


def _build_research_brief(
    *,
    controls: ResearchControls,
    query_plan: dict[str, Any],
    source_inventory: dict[str, Any],
    method_transfer: dict[str, Any],
    benchmark_report: dict[str, Any],
) -> dict[str, Any]:
    sources = list(source_inventory.get("sources", []))
    accepted = list(method_transfer.get("accepted_candidates", []))
    rejected = list(method_transfer.get("rejected_candidates", []))
    advisory = list(method_transfer.get("advisory_candidates", []))
    findings: list[dict[str, Any]] = []
    if accepted:
        first = accepted[0]
        findings.append(
            {
                "finding_type": str(first.get("candidate_kind")),
                "summary": f"Retrieved sources support `{first.get('value')}` as a plausible transfer candidate.",
            }
        )
    if benchmark_report.get("reference_count", 0):
        findings.append(
            {
                "finding_type": "benchmark_reference",
                "summary": f"Relaytic found {benchmark_report['reference_count']} benchmark or dataset reference(s) for later proof work.",
            }
        )
    if rejected:
        first_rejected = rejected[0]
        findings.append(
            {
                "finding_type": "local_override",
                "summary": f"Relaytic rejected `{first_rejected.get('value')}` because local evidence is stronger.",
            }
        )
    contradictions = [
        {
            "candidate_kind": item.get("candidate_kind"),
            "value": item.get("value"),
            "rejection_reason": item.get("rejection_reason"),
        }
        for item in rejected[:3]
    ]
    if accepted and any(item.get("candidate_kind") == "challenger_family" for item in accepted):
        followup = "expand_challenger_portfolio"
    elif accepted and any(item.get("candidate_kind") == "evaluation_design" for item in accepted):
        followup = "run_recalibration_pass"
    elif benchmark_report.get("reference_count", 0):
        followup = "benchmark_needed"
    elif advisory:
        followup = "collect_more_data"
    else:
        followup = "continue_with_local_evidence"
    provider_count = len({str(item.get("provider", "")).strip() for item in sources if str(item.get("provider", "")).strip()})
    confidence = "high" if len(sources) >= 4 and provider_count >= 2 else ("medium" if sources else "low")
    return {
        "status": "disabled" if not controls.enabled else source_inventory.get("status", "unknown"),
        "top_findings": findings,
        "contradictions": contradictions,
        "recommended_followup_action": followup,
        "confidence": confidence,
        "summary": _brief_summary(
            query_count=len(query_plan.get("queries", [])),
            source_count=len(sources),
            followup=followup,
            confidence=confidence,
        ),
    }


def _build_external_research_audit(
    *,
    controls: ResearchControls,
    query_plan: dict[str, Any],
    source_inventory: dict[str, Any],
) -> dict[str, Any]:
    endpoint_status = list(source_inventory.get("endpoint_status", []))
    query_texts = [
        str(item.get("query_text", "")).strip()
        for item in query_plan.get("queries", [])
        if str(item.get("query_text", "")).strip()
    ]
    identifier_leak = any(_looks_identifier_like(text) for text in query_texts)
    return {
        "status": "ok" if not identifier_leak else "privacy_violation",
        "network_attempted": bool(endpoint_status),
        "network_allowed": controls.allow_external_research,
        "raw_rows_exported": False,
        "identifier_leak_detected": identifier_leak,
        "exported_fields": list(query_plan.get("exported_fields", [])),
        "redactions": list(dict(query_plan.get("redaction_summary", {})).get("redactions", [])),
        "query_texts": query_texts,
        "endpoints_contacted": [
            str(item.get("endpoint", "")).strip()
            for item in endpoint_status
            if str(item.get("endpoint", "")).strip()
        ],
        "source_classes": sorted(
            {
                str(item.get("source_type", "")).strip()
                for item in source_inventory.get("sources", [])
                if str(item.get("source_type", "")).strip()
            }
        ),
        "request_count": len(endpoint_status),
        "summary": _audit_summary(
            network_allowed=controls.allow_external_research,
            request_count=len(endpoint_status),
            identifier_leak=identifier_leak,
        ),
    }


def _domain_phrase(domain_archetype: str) -> str:
    mapping = {
        "manufacturing_quality": "manufacturing quality",
        "predictive_maintenance": "predictive maintenance",
        "fraud_risk": "fraud detection",
        "anomaly_monitoring": "anomaly detection",
        "customer_churn": "customer churn",
        "pricing": "pricing optimization",
        "demand_forecasting": "demand forecasting",
        "general_tabular": "tabular machine learning",
    }
    return mapping.get(domain_archetype, domain_archetype.replace("_", " "))


def _task_phrase(task_type: str, target_semantics: str) -> str:
    mapping = {
        "regression": "regression",
        "binary_classification": "binary classification",
        "multiclass_classification": "multiclass classification",
        "fraud_detection": "fraud detection",
        "anomaly_detection": "anomaly detection",
    }
    task_phrase = mapping.get(task_type, task_type.replace("_", " "))
    return task_phrase if target_semantics == "generic_target" else f"{task_phrase} {target_semantics.replace('_', ' ')}"


def _generalize_target_name(name: str) -> str:
    lowered = str(name or "").strip().lower()
    if not lowered:
        return "generic_target"
    keyword_map = {
        "fraud": "fraud_target",
        "default": "credit_default_target",
        "churn": "churn_target",
        "failure": "failure_target",
        "fault": "failure_target",
        "maintenance": "maintenance_target",
        "defect": "defect_target",
        "quality": "quality_target",
        "scrap": "quality_target",
        "price": "pricing_target",
        "demand": "demand_target",
        "progression": "progression_target",
        "diagnosis": "diagnosis_target",
        "cancer": "diagnosis_target",
    }
    for token, value in keyword_map.items():
        if token in lowered:
            return value
    return "generic_target"


def _row_count_bucket(value: Any) -> str:
    try:
        count = int(value or 0)
    except (TypeError, ValueError):
        return "unknown"
    if count < 500:
        return "small"
    if count < 10000:
        return "medium"
    return "large"


def _positive_rate_band(value: Any) -> str:
    try:
        rate = float(value)
    except (TypeError, ValueError):
        return "unknown"
    if rate <= 0.01:
        return "very_rare"
    if rate <= 0.10:
        return "rare"
    if rate <= 0.40:
        return "moderate"
    return "balanced"


def _suggest_model_family(*, text: str, task_type: str, time_aware: bool) -> str | None:
    normalized = text.lower()
    if time_aware and any(token in normalized for token in ("lstm", "recurrent neural network", "gru", "sequence model")):
        return "sequence_lstm_candidate"
    if time_aware and any(token in normalized for token in ("temporal transformer", "time series transformer", "tcn", "temporal convolution")):
        return "temporal_transformer_candidate"
    if task_type == "regression":
        if "catboost" in normalized:
            return "catboost_ensemble"
        if "xgboost" in normalized:
            return "xgboost_ensemble"
        if "lightgbm" in normalized:
            return "lightgbm_ensemble"
        if any(token in normalized for token in ("histogram gradient", "hist gradient", "histgradient")):
            return "hist_gradient_boosting_ensemble"
        if any(token in normalized for token in ("extra trees", "extremely randomized")):
            return "extra_trees_ensemble"
        if any(token in normalized for token in ("gradient boosting", "xgboost", "lightgbm", "boosted tree")):
            return "boosted_tree_ensemble"
        if any(token in normalized for token in ("ridge", "linear regression", "elastic net")):
            return "linear_ridge"
        return None
    if "tabpfn" in normalized and task_type in {"binary_classification", "multiclass_classification", "fraud_detection", "anomaly_detection"}:
        return "tabpfn_classifier"
    if "catboost" in normalized:
        return "catboost_classifier"
    if "xgboost" in normalized:
        return "xgboost_classifier"
    if "lightgbm" in normalized:
        return "lightgbm_classifier"
    if any(token in normalized for token in ("histogram gradient", "hist gradient", "histgradient")):
        return "hist_gradient_boosting_classifier"
    if any(token in normalized for token in ("extra trees", "extremely randomized")):
        return "extra_trees_classifier"
    if any(token in normalized for token in ("gradient boosting", "xgboost", "lightgbm", "boosted tree")):
        return "boosted_tree_classifier"
    if any(token in normalized for token in ("logistic regression", "logit", "linear classifier")):
        return "logistic_regression"
    if any(token in normalized for token in ("random forest", "bagging", "tree ensemble")):
        return "bagged_tree_classifier"
    return None


def _family_matches_task(*, value: str, task_type: str) -> bool:
    if task_type == "regression":
        return value in {
            "linear_ridge",
            "boosted_tree_ensemble",
            "hist_gradient_boosting_ensemble",
            "extra_trees_ensemble",
            "catboost_ensemble",
            "xgboost_ensemble",
            "lightgbm_ensemble",
            "sequence_lstm_candidate",
            "temporal_transformer_candidate",
        }
    return value in {
        "boosted_tree_classifier",
        "logistic_regression",
        "bagged_tree_classifier",
        "hist_gradient_boosting_classifier",
        "extra_trees_classifier",
        "catboost_classifier",
        "xgboost_classifier",
        "lightgbm_classifier",
        "tabpfn_classifier",
        "sequence_lstm_candidate",
        "temporal_transformer_candidate",
    }


def _benchmark_expected(*, run_brief: dict[str, Any], task_brief: dict[str, Any]) -> bool:
    corpus = " ".join(
        [
            str(run_brief.get("objective", "")),
            str(run_brief.get("problem_statement", "")),
            str(task_brief.get("problem_statement", "")),
            str(task_brief.get("success_criteria", "")),
        ]
    ).lower()
    return any(token in corpus for token in ("benchmark", "baseline", "sota", "state of the art", "literature"))


def _method_transfer_summary(*, accepted: list[dict[str, Any]], rejected: list[dict[str, Any]], advisory: list[dict[str, Any]]) -> str:
    return (
        "Relaytic turned external references into "
        f"{len(accepted)} accepted, {len(rejected)} rejected, and {len(advisory)} advisory transfer candidate(s)."
    )


def _benchmark_summary(*, benchmark_expected: bool, reference_count: int) -> str:
    if reference_count:
        return f"Relaytic recorded {reference_count} benchmark-oriented reference(s) for later proof work."
    if benchmark_expected:
        return "Relaytic did not find benchmark references yet even though the run appears benchmark-sensitive."
    return "Relaytic did not require benchmark references for this run."


def _brief_summary(*, query_count: int, source_count: int, followup: str, confidence: str) -> str:
    return (
        f"Relaytic planned {query_count} redacted research query(ies), harvested {source_count} external source(s), "
        f"and recommends `{followup}` with `{confidence}` confidence."
    )


def _audit_summary(*, network_allowed: bool, request_count: int, identifier_leak: bool) -> str:
    if identifier_leak:
        return "Relaytic detected identifier-like content in the research query text and marked the audit as a privacy violation."
    if not network_allowed:
        return "Relaytic kept private research retrieval disabled and exported nothing."
    return f"Relaytic executed {request_count} external research request(s) without exporting rows or direct identifiers."


def _bundle_item(bundle: dict[str, Any] | None, key: str) -> dict[str, Any]:
    if not isinstance(bundle, dict):
        return {}
    value = bundle.get(key)
    return value if isinstance(value, dict) else {}


def _dedupe_strings(values: list[str]) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for value in values:
        text = str(value or "").strip()
        if not text or text in seen:
            continue
        seen.add(text)
        result.append(text)
    return result


def _clean_text(value: Any) -> str | None:
    text = str(value or "").strip()
    return text or None


def _looks_identifier_like(text: str) -> bool:
    lowered = text.lower()
    if any(token in lowered for token in ("c:\\", "/users/", "ssn", "customer_id", "order_id", "@")):
        return True
    if re.search(r"\b\d{6,}\b", text):
        return True
    return False


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()
