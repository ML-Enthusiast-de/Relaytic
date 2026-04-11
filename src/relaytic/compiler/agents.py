"""Slice 10A method compiler that turns context into executable proposals."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from relaytic.analytics import read_architecture_routing_artifacts

from .models import (
    ARCHITECTURE_CANDIDATE_REGISTRY_SCHEMA_VERSION,
    COMPILED_BENCHMARK_PROTOCOL_SCHEMA_VERSION,
    COMPILED_CHALLENGER_TEMPLATES_SCHEMA_VERSION,
    COMPILED_FEATURE_HYPOTHESES_SCHEMA_VERSION,
    METHOD_IMPORT_REPORT_SCHEMA_VERSION,
    ArchitectureCandidateRegistry,
    METHOD_COMPILER_REPORT_SCHEMA_VERSION,
    CompiledBenchmarkProtocol,
    CompiledChallengerTemplates,
    CompiledFeatureHypotheses,
    CompilerTrace,
    MethodImportReport,
    MethodCompilerReport,
    build_compiler_controls_from_policy,
)


def build_compiler_outputs(
    *,
    run_dir: str | Path,
    policy: dict[str, Any],
    planning_bundle: dict[str, Any],
    investigation_bundle: dict[str, Any],
    research_bundle: dict[str, Any],
    memory_bundle: dict[str, Any],
    benchmark_bundle: dict[str, Any],
    decision_world_model: dict[str, Any],
    join_candidate_report: dict[str, Any],
) -> tuple[
    MethodCompilerReport,
    CompiledChallengerTemplates,
    CompiledFeatureHypotheses,
    CompiledBenchmarkProtocol,
    MethodImportReport,
    ArchitectureCandidateRegistry,
]:
    controls = build_compiler_controls_from_policy(policy)
    plan = dict(planning_bundle.get("plan", {}))
    execution_summary = dict(plan.get("execution_summary") or {})
    current_family = _clean_text(execution_summary.get("selected_model_family")) or _clean_text(plan.get("selected_model_family"))
    task_type = _clean_text(plan.get("task_type")) or "unknown"
    task_profile = dict(plan.get("task_profile") or {})
    data_mode = _clean_text(task_profile.get("data_mode")) or _clean_text(plan.get("data_mode")) or "steady_state"
    research_transfer = dict(research_bundle.get("method_transfer_report", {}))
    accepted_candidates = list(research_transfer.get("accepted_candidates", []))
    advisory_candidates = list(research_transfer.get("advisory_candidates", []))
    rejected_candidates = list(research_transfer.get("rejected_candidates", []))
    route_prior = dict(memory_bundle.get("route_prior_context", {}))
    challenger_prior = dict(memory_bundle.get("challenger_prior_suggestions", {}))
    feature_strategy = dict(investigation_bundle.get("feature_strategy_profile", {}))
    benchmark_gap = dict(benchmark_bundle.get("benchmark_gap_report", {}))
    benchmark_parity = dict(benchmark_bundle.get("benchmark_parity_report", {}))
    join_candidates = list(join_candidate_report.get("candidates", []))
    architecture_bundle = read_architecture_routing_artifacts(run_dir)

    challenger_templates = _compile_challenger_templates(
        controls=controls,
        accepted_candidates=accepted_candidates,
        advisory_candidates=advisory_candidates,
        current_family=current_family,
        task_type=task_type,
        benchmark_gap=benchmark_gap,
        challenger_prior=challenger_prior,
    )
    feature_hypotheses = _compile_feature_hypotheses(
        controls=controls,
        feature_strategy=feature_strategy,
        accepted_candidates=accepted_candidates,
        join_candidates=join_candidates,
        route_prior=route_prior,
        decision_world_model=decision_world_model,
    )
    benchmark_protocol = _compile_benchmark_protocol(
        controls=controls,
        benchmark_gap=benchmark_gap,
        benchmark_parity=benchmark_parity,
        decision_world_model=decision_world_model,
        accepted_candidates=accepted_candidates,
    )
    method_import_report, architecture_candidate_registry = _build_architecture_import_outputs(
        controls=controls,
        accepted_candidates=accepted_candidates,
        advisory_candidates=advisory_candidates,
        rejected_candidates=rejected_candidates,
        current_family=current_family,
        task_type=task_type,
        data_mode=data_mode,
        architecture_bundle=architecture_bundle,
    )
    reasoning_sources = _dedupe_strings(
        [
            "research_transfer" if accepted_candidates or advisory_candidates else "",
            "memory_priors" if route_prior or challenger_prior else "",
            "feature_strategy" if feature_strategy else "",
            "benchmark_gap" if benchmark_gap or benchmark_parity else "",
            "join_candidates" if join_candidates else "",
            "decision_world_model" if decision_world_model else "",
            "architecture_registry" if architecture_bundle else "",
        ]
    )
    report = MethodCompilerReport(
        schema_version=METHOD_COMPILER_REPORT_SCHEMA_VERSION,
        generated_at=_utc_now(),
        controls=controls,
        status="ok" if any([challenger_templates.templates, feature_hypotheses.hypotheses, benchmark_protocol.protocol_updates]) else "no_compilation",
        accepted_transfer_count=len(accepted_candidates),
        compiled_challenger_count=len(challenger_templates.templates),
        compiled_feature_count=len(feature_hypotheses.hypotheses),
        compiled_benchmark_change_count=len(benchmark_protocol.protocol_updates),
        reasoning_sources=reasoning_sources,
        summary=_report_summary(
            challenger_count=len(challenger_templates.templates),
            feature_count=len(feature_hypotheses.hypotheses),
            benchmark_count=len(benchmark_protocol.protocol_updates),
        ),
        trace=_trace(),
    )
    return (
        report,
        challenger_templates,
        feature_hypotheses,
        benchmark_protocol,
        method_import_report,
        architecture_candidate_registry,
    )


def _compile_challenger_templates(
    *,
    controls: Any,
    accepted_candidates: list[dict[str, Any]],
    advisory_candidates: list[dict[str, Any]],
    current_family: str | None,
    task_type: str,
    benchmark_gap: dict[str, Any],
    challenger_prior: dict[str, Any],
) -> CompiledChallengerTemplates:
    templates: list[dict[str, Any]] = []
    seen: set[str] = set()
    for candidate in accepted_candidates + advisory_candidates:
        if str(candidate.get("candidate_kind", "")) != "challenger_family":
            continue
        family = _clean_text(candidate.get("value"))
        if not family or family == current_family or family in seen:
            continue
        seen.add(family)
        templates.append(
            {
                "template_id": f"challenger_{family}",
                "requested_model_family": family,
                "origin": "research_transfer",
                "trigger": "accepted_transfer_candidate",
                "expected_value_band": "medium",
                "task_type": task_type,
                "reason_codes": ["compiled_from_research"],
            }
        )
    preferred_family = _clean_text(challenger_prior.get("preferred_challenger_family"))
    if preferred_family and preferred_family != current_family and preferred_family not in seen:
        seen.add(preferred_family)
        templates.append(
            {
                "template_id": f"challenger_{preferred_family}",
                "requested_model_family": preferred_family,
                "origin": "memory_prior",
                "trigger": "prior_successful_family",
                "expected_value_band": "medium",
                "task_type": task_type,
                "reason_codes": ["compiled_from_memory"],
            }
        )
    winning_family = _clean_text(benchmark_gap.get("winning_family"))
    if winning_family and winning_family != current_family and winning_family not in seen:
        seen.add(winning_family)
        templates.append(
            {
                "template_id": f"challenger_{winning_family}",
                "requested_model_family": winning_family,
                "origin": "benchmark_gap",
                "trigger": "parity_gap",
                "expected_value_band": "high",
                "task_type": task_type,
                "reason_codes": ["compiled_from_benchmark_gap"],
            }
        )
    if not templates:
        fallback = _fallback_family(task_type=task_type, current_family=current_family)
        if fallback:
            templates.append(
                {
                    "template_id": f"challenger_{fallback}",
                    "requested_model_family": fallback,
                    "origin": "task_prior",
                    "trigger": "no_transfer_but_more_pressure_needed",
                    "expected_value_band": "low",
                    "task_type": task_type,
                    "reason_codes": ["compiled_from_task_prior"],
                }
            )
    templates = templates[: controls.max_compiled_templates]
    return CompiledChallengerTemplates(
        schema_version=COMPILED_CHALLENGER_TEMPLATES_SCHEMA_VERSION,
        generated_at=_utc_now(),
        controls=controls,
        status="ok" if templates else "empty",
        templates=templates,
        summary=(
            f"Relaytic compiled {len(templates)} challenger template(s) from research, memory, and benchmark context."
            if templates
            else "Relaytic did not compile challenger templates for this run."
        ),
        trace=_trace(),
    )


def _compile_feature_hypotheses(
    *,
    controls: Any,
    feature_strategy: dict[str, Any],
    accepted_candidates: list[dict[str, Any]],
    join_candidates: list[dict[str, Any]],
    route_prior: dict[str, Any],
    decision_world_model: dict[str, Any],
) -> CompiledFeatureHypotheses:
    hypotheses: list[dict[str, Any]] = []
    if bool(feature_strategy.get("prioritize_missingness_indicators")):
        hypotheses.append(
            {
                "hypothesis_id": "feature_missingness_indicators",
                "feature_family": "missingness_indicators",
                "origin": "feature_strategy",
                "reason": "Investigation already flagged missingness as potentially informative.",
            }
        )
    if bool(feature_strategy.get("prioritize_interactions")):
        hypotheses.append(
            {
                "hypothesis_id": "feature_pairwise_interactions",
                "feature_family": "pairwise_interactions",
                "origin": "feature_strategy",
                "reason": "Investigation flagged interaction features as a bounded next step.",
            }
        )
    if any(str(item.get("candidate_kind", "")) == "evaluation_design" and str(item.get("value", "")) == "calibration_review" for item in accepted_candidates):
        hypotheses.append(
            {
                "hypothesis_id": "feature_calibration_review",
                "feature_family": "calibration_review",
                "origin": "research_transfer",
                "reason": "External references suggested calibration-sensitive evaluation.",
            }
        )
    if join_candidates:
        top = join_candidates[0]
        hypotheses.append(
            {
                "hypothesis_id": "feature_join_context",
                "feature_family": "joined_context",
                "origin": "data_fabric",
                "reason": f"Top local join candidate `{top.get('candidate_id')}` could add context before more search.",
                "source_id": top.get("source_id"),
            }
        )
    if str(route_prior.get("status", "")) == "memory_influenced":
        hypotheses.append(
            {
                "hypothesis_id": "feature_memory_supported_route",
                "feature_family": "route_supporting_features",
                "origin": "memory_prior",
                "reason": "Prior analog evidence suggests reinforcing the currently favored route with explicit support features.",
            }
        )
    if str(decision_world_model.get("action_regime", "")) == "human_review_queue":
        hypotheses.append(
            {
                "hypothesis_id": "feature_review_priority",
                "feature_family": "review_priority_features",
                "origin": "decision_world_model",
                "reason": "Human-review regimes benefit from features that separate obvious from borderline cases.",
            }
        )
    hypotheses = hypotheses[: controls.max_compiled_templates]
    return CompiledFeatureHypotheses(
        schema_version=COMPILED_FEATURE_HYPOTHESES_SCHEMA_VERSION,
        generated_at=_utc_now(),
        controls=controls,
        status="ok" if hypotheses else "empty",
        hypotheses=hypotheses,
        summary=(
            f"Relaytic compiled {len(hypotheses)} executable feature hypothesis/hypotheses."
            if hypotheses
            else "Relaytic did not compile feature hypotheses for this run."
        ),
        trace=_trace(),
    )


def _compile_benchmark_protocol(
    *,
    controls: Any,
    benchmark_gap: dict[str, Any],
    benchmark_parity: dict[str, Any],
    decision_world_model: dict[str, Any],
    accepted_candidates: list[dict[str, Any]],
) -> CompiledBenchmarkProtocol:
    updates: list[dict[str, Any]] = []
    if _clean_text(benchmark_parity.get("parity_status")) not in {"at_parity", "better_than_reference"}:
        updates.append(
            {
                "update_id": "benchmark_gap_followup",
                "change": "retain_same_contract_reference_review",
                "reason": "Relaytic is not yet at parity, so benchmark pressure should remain explicit.",
            }
        )
    if str(decision_world_model.get("action_regime", "")) == "human_review_queue":
        updates.append(
            {
                "update_id": "benchmark_review_regime",
                "change": "add_review_queue_sensitivity",
                "reason": "Review-heavy regimes should compare not only raw score but defer/review usefulness.",
            }
        )
    if any(str(item.get("candidate_kind", "")) == "evaluation_design" for item in accepted_candidates):
        updates.append(
            {
                "update_id": "benchmark_calibration",
                "change": "retain_calibration_specific_checks",
                "reason": "Compiled research transfer said calibration should stay explicit in proof work.",
            }
        )
    return CompiledBenchmarkProtocol(
        schema_version=COMPILED_BENCHMARK_PROTOCOL_SCHEMA_VERSION,
        generated_at=_utc_now(),
        controls=controls,
        status="ok" if updates else "empty",
        protocol_updates=updates[: controls.max_compiled_templates],
        summary=(
            f"Relaytic compiled {len(updates[: controls.max_compiled_templates])} benchmark-protocol update(s)."
            if updates
            else "Relaytic did not compile benchmark-protocol updates for this run."
        ),
        trace=_trace(),
    )


def _report_summary(*, challenger_count: int, feature_count: int, benchmark_count: int) -> str:
    return (
        f"Relaytic compiled {challenger_count} challenger template(s), {feature_count} feature hypothesis/hypotheses, "
        f"and {benchmark_count} benchmark-protocol update(s)."
    )


def _fallback_family(*, task_type: str, current_family: str | None) -> str | None:
    normalized = str(task_type or "").strip().lower()
    candidates = {
        "regression": "boosted_tree_ensemble",
        "binary_classification": "boosted_tree_classifier",
        "multiclass_classification": "boosted_tree_classifier",
        "fraud_detection": "boosted_tree_classifier",
        "anomaly_detection": "bagged_tree_classifier",
    }
    fallback = candidates.get(normalized)
    if fallback == current_family:
        return None
    return fallback


def _build_architecture_import_outputs(
    *,
    controls: Any,
    accepted_candidates: list[dict[str, Any]],
    advisory_candidates: list[dict[str, Any]],
    rejected_candidates: list[dict[str, Any]],
    current_family: str | None,
    task_type: str,
    data_mode: str,
    architecture_bundle: dict[str, Any] | None,
) -> tuple[MethodImportReport, ArchitectureCandidateRegistry]:
    generated_at = _utc_now()
    trace = _trace()
    architecture_bundle = architecture_bundle or {}
    architecture_registry = dict(architecture_bundle.get("architecture_registry", {}))
    candidate_family_matrix = dict(architecture_bundle.get("candidate_family_matrix", {}))
    registry_rows = list(architecture_registry.get("families", [])) if isinstance(architecture_registry.get("families"), list) else []
    live_order = [
        str(item)
        for item in dict(architecture_bundle.get("architecture_router_report", {})).get("candidate_order", [])
        if str(item).strip()
    ]
    candidate_ranks = {
        str(item.get("family_id")): int(item.get("rank", 0) or 0)
        for item in candidate_family_matrix.get("rows", [])
        if isinstance(item, dict) and _clean_text(item.get("family_id"))
    } if isinstance(candidate_family_matrix.get("rows"), list) else {}
    registry_by_family = {
        str(item.get("family_id")): dict(item)
        for item in registry_rows
        if isinstance(item, dict) and _clean_text(item.get("family_id"))
    }
    imported_families: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    imported_sources = [
        ("accepted", accepted_candidates),
        ("advisory", advisory_candidates),
        ("rejected", rejected_candidates),
    ]
    for disposition, rows in imported_sources:
        for candidate in rows:
            if str(candidate.get("candidate_kind", "")).strip() != "challenger_family":
                continue
            family_id = _clean_text(candidate.get("value"))
            if not family_id:
                continue
            key = (disposition, family_id)
            if key in seen:
                continue
            seen.add(key)
            registry_row = dict(registry_by_family.get(family_id, {}))
            availability_status = _clean_text(registry_row.get("availability_status")) or "unknown"
            training_support = bool(registry_row.get("training_support"))
            shadow_policy = _shadow_policy_for_family(
                family_id=family_id,
                availability_status=availability_status,
                training_support=training_support,
                data_mode=data_mode,
            )
            imported_families.append(
                {
                    "candidate_id": f"architecture_candidate::{family_id}",
                    "family_id": family_id,
                    "family_title": _clean_text(registry_row.get("family_title")) or family_id,
                    "research_disposition": disposition,
                    "current_family": current_family,
                    "task_type": task_type,
                    "data_mode": data_mode,
                    "source_title": _clean_text(dict(candidate.get("source") or {}).get("title")),
                    "source_url": _clean_text(dict(candidate.get("source") or {}).get("url")),
                    "source_provider": _clean_text(dict(candidate.get("source") or {}).get("provider")),
                    "source_year": dict(candidate.get("source") or {}).get("year"),
                    "support_reason": _clean_text(candidate.get("support_reason"))
                    or _clean_text(candidate.get("acceptance_reason"))
                    or _clean_text(candidate.get("rejection_reason")),
                    "architecture_known": bool(registry_row),
                    "family_role": _clean_text(registry_row.get("family_role")) or "research_import",
                    "availability_status": availability_status,
                    "training_support": training_support,
                    "live_candidate": bool(registry_row.get("live_candidate")),
                    "candidate_rank": candidate_ranks.get(family_id),
                    "in_live_order": family_id in live_order,
                    "temporal_gate_required": family_id in {"sequence_lstm_candidate", "temporal_transformer_candidate"},
                    "required_proof_steps": ["offline_replay", "shadow_trial", "promotion_readiness_review"],
                    "shadow_policy": shadow_policy,
                    "initial_state": _initial_import_state(
                        disposition=disposition,
                        family_id=family_id,
                        availability_status=availability_status,
                        training_support=training_support,
                        data_mode=data_mode,
                    ),
                    "blocking_reason": _blocking_reason_for_import(
                        disposition=disposition,
                        family_id=family_id,
                        availability_status=availability_status,
                        training_support=training_support,
                        data_mode=data_mode,
                    ),
                }
            )
    imported_families = imported_families[: max(1, controls.max_compiled_templates)]
    shadow_only_count = sum(1 for item in imported_families if str(item.get("shadow_policy")) == "shadow_only")
    unavailable_count = sum(1 for item in imported_families if str(item.get("availability_status")) not in {"available", "shadow_only"})
    report = MethodImportReport(
        schema_version=METHOD_IMPORT_REPORT_SCHEMA_VERSION,
        generated_at=generated_at,
        controls=controls,
        status="ok" if imported_families else "no_imported_architectures",
        imported_family_count=len(imported_families),
        accepted_family_count=sum(1 for item in imported_families if item.get("research_disposition") == "accepted"),
        advisory_family_count=sum(1 for item in imported_families if item.get("research_disposition") == "advisory"),
        rejected_family_count=sum(1 for item in imported_families if item.get("research_disposition") == "rejected"),
        shadow_only_count=shadow_only_count,
        unavailable_count=unavailable_count,
        imported_families=imported_families,
        summary=(
            f"Relaytic registered {len(imported_families)} research-imported architecture candidate(s) for replay or shadow proof."
            if imported_families
            else "Relaytic did not import architecture candidates from the current research signals."
        ),
        trace=trace,
    )
    registry = ArchitectureCandidateRegistry(
        schema_version=ARCHITECTURE_CANDIDATE_REGISTRY_SCHEMA_VERSION,
        generated_at=generated_at,
        controls=controls,
        status="ok" if imported_families else "no_candidates",
        candidate_count=len(imported_families),
        shadow_only_count=shadow_only_count,
        unavailable_count=unavailable_count,
        replay_only_count=sum(1 for item in imported_families if str(item.get("shadow_policy")) == "offline_replay_only"),
        candidates=imported_families,
        summary=(
            f"Relaytic wrote a governed registry for {len(imported_families)} imported architecture candidate(s)."
            if imported_families
            else "Relaytic did not need an imported architecture registry for this run."
        ),
        trace=trace,
    )
    return report, registry


def _shadow_policy_for_family(
    *,
    family_id: str,
    availability_status: str,
    training_support: bool,
    data_mode: str,
) -> str:
    if family_id in {"sequence_lstm_candidate", "temporal_transformer_candidate"}:
        return "offline_replay_only" if data_mode != "time_series" else "shadow_only"
    if availability_status == "available" and training_support:
        return "same_split_shadow_trial"
    if availability_status == "shadow_only":
        return "shadow_only"
    return "offline_replay_only"


def _initial_import_state(
    *,
    disposition: str,
    family_id: str,
    availability_status: str,
    training_support: bool,
    data_mode: str,
) -> str:
    if disposition == "rejected":
        return "rejected"
    if family_id in {"sequence_lstm_candidate", "temporal_transformer_candidate"}:
        return "shadow_only" if data_mode == "time_series" else "replay_only"
    if availability_status == "available" and training_support:
        return "registered"
    if availability_status == "shadow_only":
        return "shadow_only"
    return "quarantined"


def _blocking_reason_for_import(
    *,
    disposition: str,
    family_id: str,
    availability_status: str,
    training_support: bool,
    data_mode: str,
) -> str | None:
    if disposition == "rejected":
        return "Research signals suggested this family, but the current task contract rejected it as incompatible."
    if family_id in {"sequence_lstm_candidate", "temporal_transformer_candidate"} and data_mode != "time_series":
        return "Relaytic kept this temporal sequence family in replay-only mode because the current task is not provably ordered temporal data."
    if family_id in {"sequence_lstm_candidate", "temporal_transformer_candidate"}:
        return "Relaytic requires offline replay and shadow proof against lagged tabular baselines before temporal sequence families can become promotion-ready."
    if availability_status == "unavailable" or not training_support:
        return "Relaytic found research support for this family, but the required local adapter is not available on this machine."
    return None


def _trace() -> CompilerTrace:
    return CompilerTrace(
        agent="method_compiler_agent",
        operating_mode="artifact_to_executable_proposal_compiler",
        llm_used=False,
        llm_status="not_requested",
        deterministic_evidence=[
            "research_transfer_candidates",
            "memory_priors",
            "benchmark_gap_context",
            "feature_strategy_profile",
            "data_fabric_candidates",
        ],
    )


def _dedupe_strings(values: list[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for value in values:
        text = str(value).strip()
        if not text or text in seen:
            continue
        seen.add(text)
        ordered.append(text)
    return ordered


def _clean_text(value: Any) -> str | None:
    text = str(value or "").strip()
    return text or None


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()
