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
    runtime_cfg = dict(config.get("runtime", {}))
    modeling_cfg = dict(config.get("modeling", {}))
    checkpoints_cfg = dict(modeling_cfg.get("checkpoints", {}))

    return {
        "locality": {
            "remote_allowed": not bool(privacy_cfg.get("local_only", True)),
            "local_models_only": bool(runtime_cfg.get("require_local_models", True)),
            "allow_optional_remote_baselines": bool(privacy_cfg.get("api_calls_allowed", False)),
        },
        "autonomy": {
            "execution_mode": "guided",
            "operation_mode": "session",
            "allow_auto_run": bool(modeling_cfg.get("agentic_loops", {}).get("enabled", True)),
            "allow_indefinite_operation": False,
            "approval_required_for_expensive_runs": True,
            "approval_required_for_optional_backends": True,
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
            "enable_run_memory": False,
            "allow_prior_retrieval": False,
            "feedback_learning_enabled": False,
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
        "intelligence": {
            "enabled": True,
            "intelligence_mode": "none",
            "prefer_local_llm": True,
            "allow_frontier_llm": False,
            "allow_max_reasoning": False,
            "minimum_local_llm_enabled": False,
            "minimum_local_llm_profile": "none",
            "enable_backend_discovery": True,
            "allow_upgrade_suggestions": True,
            "allow_automatic_local_upgrade": False,
            "require_schema_constrained_actions": True,
            "require_verifier_for_high_impact_decisions": True,
        },
        "lifecycle": {
            "scheduled_retraining_enabled": False,
            "drift_triggered_retraining_enabled": False,
            "recalibration_only_allowed": True,
            "rollback_allowed": True,
            "champion_candidate_registry_enabled": False,
            "completion_judge_enabled": False,
            "stage_visibility_enabled": False,
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
                modeling_cfg.get("agentic_loops", {}).get("suggest_more_data_when_stalled", True)
            ),
            "create_decision_memo": False,
        },
    }
