"""Policy loading shell for early Relaytic slices."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from relaytic.core.config import load_config


POLICY_SCHEMA_VERSION = "relaytic.policy.v1"


@dataclass(frozen=True)
class ResolvedPolicy:
    """Resolved policy/config payload with source metadata."""

    schema_version: str
    resolved_at: str
    source_path: str
    source_format: str
    policy: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def load_policy(path: str | Path | None = None) -> ResolvedPolicy:
    """Resolve policy/config into a stable shell structure."""
    requested = path if path is not None else "configs/default.yaml"
    source_path = _resolve_source_path(requested)
    payload = load_config(source_path)
    resolved_policy, source_format = _normalize_policy_payload(payload)
    return ResolvedPolicy(
        schema_version=POLICY_SCHEMA_VERSION,
        resolved_at=datetime.now(timezone.utc).isoformat(),
        source_path=str(source_path),
        source_format=source_format,
        policy=resolved_policy,
    )


def write_resolved_policy(
    output_path: str | Path,
    *,
    path: str | Path | None = None,
) -> Path:
    """Write `policy_resolved.yaml` and return the output path."""
    resolved = load_policy(path)
    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        yaml.safe_dump(
            resolved.to_dict(),
            sort_keys=False,
            allow_unicode=True,
        ),
        encoding="utf-8",
    )
    return destination


def _resolve_source_path(path: str | Path) -> Path:
    candidate = Path(path).expanduser()
    if candidate.is_file():
        return candidate.resolve()
    if not candidate.is_absolute():
        project_root = Path(__file__).resolve().parents[3]
        alt = (project_root / candidate).resolve()
        if alt.is_file():
            return alt
    raise FileNotFoundError(f"Policy file not found: {path}")


def _normalize_policy_payload(payload: dict[str, Any]) -> tuple[dict[str, Any], str]:
    if "policy" in payload and isinstance(payload["policy"], dict):
        return dict(payload["policy"]), "canonical"
    return _map_legacy_config_to_policy(payload), "legacy_top_level"


def _map_legacy_config_to_policy(config: dict[str, Any]) -> dict[str, Any]:
    privacy_cfg = dict(config.get("privacy", {}))
    data_cfg = dict(config.get("data", {}))
    runtime_cfg = dict(config.get("runtime", {}))
    modeling_cfg = dict(config.get("modeling", {}))
    checkpoints_cfg = dict(modeling_cfg.get("checkpoints", {}))
    autonomy_cfg = dict(config.get("autonomy", {}))
    communication_cfg = dict(config.get("communication", {}))
    intelligence_cfg = dict(config.get("intelligence", {}))
    research_cfg = dict(config.get("research", {}))
    feedback_cfg = dict(config.get("feedback", {}))
    profiles_cfg = dict(config.get("profiles", {}))
    agentic_loops_cfg = dict(modeling_cfg.get("agentic_loops", {}))
    contact_email = research_cfg.get("contact_email", "")
    if contact_email is None:
        contact_email = ""

    return {
        "locality": {
            "remote_allowed": not bool(privacy_cfg.get("local_only", True)),
            "local_models_only": bool(runtime_cfg.get("require_local_models", True)),
            "allow_optional_remote_baselines": bool(privacy_cfg.get("api_calls_allowed", False)),
        },
        "privacy": {
            "local_only": bool(privacy_cfg.get("local_only", True)),
            "api_calls_allowed": bool(privacy_cfg.get("api_calls_allowed", False)),
            "telemetry_allowed": bool(privacy_cfg.get("telemetry_allowed", False)),
        },
        "data_handling": {
            "copy_inputs_to_run_dir": bool(data_cfg.get("copy_inputs_to_run_dir", True)),
            "immutable_working_copies": bool(data_cfg.get("immutable_working_copies", True)),
            "never_modify_source_data": bool(data_cfg.get("never_modify_source_data", True)),
            "persist_original_paths": bool(data_cfg.get("persist_original_paths", False)),
            "allow_streaming_sources": bool(data_cfg.get("allow_streaming_sources", True)),
            "allow_lakehouse_connectors": bool(data_cfg.get("allow_lakehouse_connectors", True)),
            "default_stream_window_rows": int(data_cfg.get("default_stream_window_rows", 5000) or 5000),
            "default_materialized_format": str(data_cfg.get("default_materialized_format", "parquet") or "parquet"),
            "allowed_extensions": [str(item).strip() for item in data_cfg.get("allowed_extensions", []) if str(item).strip()],
        },
        "autonomy": {
            "execution_mode": str(autonomy_cfg.get("execution_mode", "guided")),
            "operation_mode": str(autonomy_cfg.get("operation_mode", "session")),
            "allow_auto_run": bool(autonomy_cfg.get("allow_auto_run", agentic_loops_cfg.get("enabled", True))),
            "allow_indefinite_operation": False,
            "approval_required_for_expensive_runs": True,
            "approval_required_for_optional_backends": True,
            "max_followup_rounds": int(autonomy_cfg.get("max_followup_rounds", agentic_loops_cfg.get("max_attempts", 1)) or 1),
            "max_branches_per_round": int(autonomy_cfg.get("max_branches_per_round", 2) or 2),
            "min_relative_improvement": float(
                autonomy_cfg.get("min_relative_improvement", agentic_loops_cfg.get("min_relative_improvement", 0.02)) or 0.02
            ),
            "allow_architecture_switch": bool(
                autonomy_cfg.get("allow_architecture_switch", agentic_loops_cfg.get("allow_architecture_switch", True))
            ),
            "allow_feature_set_expansion": bool(
                autonomy_cfg.get("allow_feature_set_expansion", agentic_loops_cfg.get("allow_feature_set_expansion", True))
            ),
            "suggest_more_data_when_stalled": bool(
                autonomy_cfg.get("suggest_more_data_when_stalled", agentic_loops_cfg.get("suggest_more_data_when_stalled", True))
            ),
        },
        "compute": {
            "autodetect_hardware_if_unspecified": True,
            "machine_profile": "auto",
            "default_effort_tier": "standard",
            "max_wall_clock_minutes": 120,
            "max_trials": 200,
            "max_parallel_trials": 4,
            "max_memory_gb": 24,
            "multi_fidelity_enabled": True,
            "execution_profile": str(runtime_cfg.get("default_profile", "auto")),
            "gpu_allowed": True,
            "distributed_local_allowed": False,
            "scheduler_allowed": False,
            "checkpoint_required_for_distributed_runs": bool(checkpoints_cfg.get("enabled", True)),
        },
        "optimization": {
            "objective": "best_robust_pareto_front",
            "primary_metric": "auto",
            "secondary_metrics": ["calibration", "stability", "latency"],
            "pareto_selection": True,
            "focus_council_enabled": True,
            "focus_profile": "auto",
        },
        "constraints": {
            "latency_ms_max": None,
            "interpretability": "medium",
            "uncertainty_required": True,
            "reproducibility_required": True,
            "abstention_allowed": True,
        },
        "safety": {
            "strict_leakage_checks": True,
            "strict_time_ordering": True,
            "reject_unstable_models": True,
            "require_disagreement_resolution": True,
            "require_challenger_science": True,
        },
        "memory": {
            "enable_run_memory": True,
            "allow_prior_retrieval": True,
            "feedback_learning_enabled": False,
            "max_analog_runs": 5,
            "min_similarity_score": 0.45,
        },
        "mandate": {
            "enabled": True,
            "influence_mode": "weighted",
            "allow_agent_challenges": True,
            "require_disagreement_logging": True,
            "allow_soft_preference_override_with_evidence": True,
        },
        "context": {
            "enabled": True,
            "external_retrieval_allowed": False,
            "allow_uploaded_docs": True,
            "require_provenance": True,
            "semantic_task_enabled": True,
        },
        "communication": {
            "enabled": bool(communication_cfg.get("enabled", True)),
            "allow_interactive_assist": bool(communication_cfg.get("allow_interactive_assist", True)),
            "allow_stage_navigation": bool(communication_cfg.get("allow_stage_navigation", True)),
            "allow_assistant_takeover": bool(communication_cfg.get("allow_assistant_takeover", True)),
            "prefer_local_semantic_assist": bool(communication_cfg.get("prefer_local_semantic_assist", True)),
            "allow_host_connection_guidance": bool(communication_cfg.get("allow_host_connection_guidance", True)),
            "max_turn_history": int(communication_cfg.get("max_turn_history", 20) or 20),
        },
        "research": {
            "enabled": bool(research_cfg.get("enabled", False)),
            "require_redaction_default": bool(research_cfg.get("require_redaction_default", True)),
            "allow_benchmark_reference_retrieval": bool(
                research_cfg.get("allow_benchmark_reference_retrieval", True)
            ),
            "allow_method_transfer": bool(research_cfg.get("allow_method_transfer", True)),
            "max_queries": int(research_cfg.get("max_queries", 3) or 3),
            "max_results_per_source": int(research_cfg.get("max_results_per_source", 5) or 5),
            "source_order": list(research_cfg.get("source_order", ["semantic_scholar", "crossref"])),
            "contact_email": str(contact_email).strip() or None,
            "semantic_scholar_endpoint": str(
                research_cfg.get("semantic_scholar_endpoint", "https://api.semanticscholar.org/graph/v1/paper/search")
            ).strip()
            or "https://api.semanticscholar.org/graph/v1/paper/search",
            "crossref_endpoint": str(research_cfg.get("crossref_endpoint", "https://api.crossref.org/works")).strip()
            or "https://api.crossref.org/works",
        },
        "benchmark": {
            "enabled": bool(config.get("benchmark", {}).get("enabled", True)),
            "require_same_split_contract": bool(config.get("benchmark", {}).get("require_same_split_contract", True)),
            "require_same_metric_contract": bool(config.get("benchmark", {}).get("require_same_metric_contract", True)),
            "use_optional_flaml_reference": bool(config.get("benchmark", {}).get("use_optional_flaml_reference", False)),
            "allow_time_series_references": bool(config.get("benchmark", {}).get("allow_time_series_references", True)),
            "max_reference_models": int(config.get("benchmark", {}).get("max_reference_models", 3) or 3),
            "near_parity_absolute_delta": float(config.get("benchmark", {}).get("near_parity_absolute_delta", 0.03) or 0.03),
            "near_parity_relative_delta": float(config.get("benchmark", {}).get("near_parity_relative_delta", 0.08) or 0.08),
        },
        "feedback": {
            "enabled": bool(feedback_cfg.get("enabled", True)),
            "accept_human_feedback": bool(feedback_cfg.get("accept_human_feedback", True)),
            "accept_external_agent_feedback": bool(feedback_cfg.get("accept_external_agent_feedback", True)),
            "accept_runtime_failure_feedback": bool(feedback_cfg.get("accept_runtime_failure_feedback", True)),
            "accept_benchmark_review_feedback": bool(feedback_cfg.get("accept_benchmark_review_feedback", True)),
            "accept_outcome_observations": bool(feedback_cfg.get("accept_outcome_observations", True)),
            "min_acceptance_score": float(feedback_cfg.get("min_acceptance_score", 0.68) or 0.68),
            "downgrade_threshold": float(feedback_cfg.get("downgrade_threshold", 0.40) or 0.40),
            "allow_route_prior_updates": bool(feedback_cfg.get("allow_route_prior_updates", True)),
            "allow_policy_update_suggestions": bool(feedback_cfg.get("allow_policy_update_suggestions", True)),
            "allow_decision_policy_update_suggestions": bool(
                feedback_cfg.get("allow_decision_policy_update_suggestions", True)
            ),
            "max_casebook_entries": int(feedback_cfg.get("max_casebook_entries", 50) or 50),
        },
        "profiles": {
            "enabled": bool(profiles_cfg.get("enabled", True)),
            "allow_operator_profile_overlays": bool(profiles_cfg.get("allow_operator_profile_overlays", True)),
            "allow_lab_profile_overlays": bool(profiles_cfg.get("allow_lab_profile_overlays", True)),
            "allow_assumption_defaults": bool(profiles_cfg.get("allow_assumption_defaults", True)),
            "require_visible_quality_gates": bool(profiles_cfg.get("require_visible_quality_gates", True)),
            "require_visible_budget_consumption": bool(profiles_cfg.get("require_visible_budget_consumption", True)),
            "quality_review_mode": str(profiles_cfg.get("quality_review_mode", "explicit_contracts") or "explicit_contracts"),
        },
        "runtime": {
            "gateway_enabled": bool(runtime_cfg.get("gateway_enabled", True)),
            "read_only_hooks_enabled": bool(runtime_cfg.get("read_only_hooks_enabled", True)),
            "allow_write_hooks": bool(runtime_cfg.get("allow_write_hooks", False)),
            "checkpoint_on_stage_complete": bool(runtime_cfg.get("checkpoint_on_stage_complete", True)),
            "capability_enforcement_enabled": bool(runtime_cfg.get("capability_enforcement_enabled", True)),
            "semantic_rowless_default": bool(runtime_cfg.get("semantic_rowless_default", True)),
            "max_recent_events": int(runtime_cfg.get("max_recent_events", 50) or 50),
        },
        "intelligence": {
            "enabled": bool(intelligence_cfg.get("enabled", True)),
            "intelligence_mode": str(intelligence_cfg.get("intelligence_mode", "none")),
            "prefer_local_llm": bool(intelligence_cfg.get("prefer_local_llm", True)),
            "allow_frontier_llm": bool(intelligence_cfg.get("allow_frontier_llm", False)),
            "allow_max_reasoning": bool(intelligence_cfg.get("allow_max_reasoning", False)),
            "minimum_local_llm_enabled": bool(intelligence_cfg.get("minimum_local_llm_enabled", False)),
            "minimum_local_llm_profile": str(intelligence_cfg.get("minimum_local_llm_profile", "none")),
            "enable_backend_discovery": bool(intelligence_cfg.get("enable_backend_discovery", True)),
            "allow_upgrade_suggestions": bool(intelligence_cfg.get("allow_upgrade_suggestions", True)),
            "allow_mode_routing": bool(intelligence_cfg.get("allow_mode_routing", True)),
            "hardware_aware_routing": bool(intelligence_cfg.get("hardware_aware_routing", True)),
            "enable_semantic_proof": bool(intelligence_cfg.get("enable_semantic_proof", True)),
            "allow_automatic_local_upgrade": bool(intelligence_cfg.get("allow_automatic_local_upgrade", False)),
            "require_schema_constrained_actions": bool(intelligence_cfg.get("require_schema_constrained_actions", True)),
            "require_verifier_for_high_impact_decisions": bool(intelligence_cfg.get("require_verifier_for_high_impact_decisions", True)),
        },
        "lifecycle": {
            "scheduled_retraining_enabled": False,
            "drift_triggered_retraining_enabled": False,
            "recalibration_only_allowed": True,
            "rollback_allowed": True,
            "champion_candidate_registry_enabled": False,
            "completion_judge_enabled": True,
            "stage_visibility_enabled": True,
        },
        "dojo": {
            "enabled": False,
            "allow_method_self_improvement": True,
            "allow_architecture_proposals": True,
            "require_quarantine_before_promotion": True,
        },
        "hpo": {
            "backend": str(modeling_cfg.get("optimizer", "optuna_or_flaml")),
            "enable_multi_objective": True,
            "enable_threshold_tuning": True,
            "enable_transfer_from_prior_runs": False,
        },
        "interoperability": {
            "enable_mcp_server": False,
            "expose_tool_contracts": False,
            "workflow_specs_enabled": False,
        },
        "integrations": {
            "engine_slots_enabled": False,
            "trust_mode_default": "advisory_only",
            "dry_run_for_side_effecting_backends": True,
        },
        "reporting": {
            "create_model_card": False,
            "create_risk_report": False,
            "create_experiment_graph": False,
            "create_handoff_graph": False,
            "create_data_recommendations": bool(
                autonomy_cfg.get("suggest_more_data_when_stalled", agentic_loops_cfg.get("suggest_more_data_when_stalled", True))
            ),
            "create_decision_memo": False,
        },
    }
