"""Typed artifact models for Slice 09B runtime outputs."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


RUNTIME_CONTROLS_SCHEMA_VERSION = "relaytic.runtime_controls.v1"
CAPABILITY_PROFILES_SCHEMA_VERSION = "relaytic.capability_profiles.v1"
HOOK_EXECUTION_LOG_SCHEMA_VERSION = "relaytic.hook_execution_log.v1"
RUN_CHECKPOINT_MANIFEST_SCHEMA_VERSION = "relaytic.run_checkpoint_manifest.v1"
DATA_ACCESS_AUDIT_SCHEMA_VERSION = "relaytic.data_access_audit.v1"
CONTEXT_INFLUENCE_REPORT_SCHEMA_VERSION = "relaytic.context_influence_report.v1"
LAB_EVENT_SCHEMA_VERSION = "relaytic.lab_event.v1"


@dataclass(frozen=True)
class RuntimeControls:
    """Resolved controls for Slice 09B runtime behavior."""

    schema_version: str = RUNTIME_CONTROLS_SCHEMA_VERSION
    enabled: bool = True
    append_only_events: bool = True
    read_only_hooks_enabled: bool = True
    write_hooks_enabled: bool = False
    checkpoint_on_stage_complete: bool = True
    capability_enforcement_enabled: bool = True
    semantic_rowless_default: bool = True
    local_only: bool = True
    max_recent_events: int = 50

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class CapabilityProfile:
    """Capability profile for one Relaytic specialist."""

    specialist: str
    phase: str
    artifact_read_scope: list[str]
    artifact_write_scope: list[str]
    raw_row_access: bool
    semantic_access: str
    external_adapter_access: list[str]
    network_access: bool
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class CapabilityProfilesArtifact:
    """Persisted capability profiles for the local runtime."""

    schema_version: str
    generated_at: str
    controls: RuntimeControls
    profiles: list[CapabilityProfile]
    summary: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "generated_at": self.generated_at,
            "controls": self.controls.to_dict(),
            "profiles": [item.to_dict() for item in self.profiles],
            "summary": self.summary,
        }


@dataclass(frozen=True)
class HookExecutionLogArtifact:
    """Persisted hook-execution ledger."""

    schema_version: str
    generated_at: str
    controls: RuntimeControls
    executions: list[dict[str, Any]]
    summary: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "generated_at": self.generated_at,
            "controls": self.controls.to_dict(),
            "executions": list(self.executions),
            "summary": self.summary,
        }


@dataclass(frozen=True)
class RunCheckpointManifestArtifact:
    """Persisted checkpoint manifest for the local runtime."""

    schema_version: str
    generated_at: str
    controls: RuntimeControls
    latest_stage: str | None
    checkpoints: list[dict[str, Any]]
    summary: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "generated_at": self.generated_at,
            "controls": self.controls.to_dict(),
            "latest_stage": self.latest_stage,
            "checkpoints": list(self.checkpoints),
            "summary": self.summary,
        }


@dataclass(frozen=True)
class DataAccessAuditArtifact:
    """Persisted data-access audit for specialist capability enforcement."""

    schema_version: str
    generated_at: str
    controls: RuntimeControls
    decisions: list[dict[str, Any]]
    denied_count: int
    summary: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "generated_at": self.generated_at,
            "controls": self.controls.to_dict(),
            "decisions": list(self.decisions),
            "denied_count": self.denied_count,
            "summary": self.summary,
        }


@dataclass(frozen=True)
class ContextInfluenceReportArtifact:
    """Persisted context-assembly and influence summary."""

    schema_version: str
    generated_at: str
    controls: RuntimeControls
    stage_reports: list[dict[str, Any]]
    summary: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "generated_at": self.generated_at,
            "controls": self.controls.to_dict(),
            "stage_reports": list(self.stage_reports),
            "summary": self.summary,
        }


@dataclass(frozen=True)
class RuntimeBundle:
    """Full Slice 09B runtime bundle excluding the JSONL event stream."""

    capability_profiles: CapabilityProfilesArtifact
    hook_execution_log: HookExecutionLogArtifact
    run_checkpoint_manifest: RunCheckpointManifestArtifact
    data_access_audit: DataAccessAuditArtifact
    context_influence_report: ContextInfluenceReportArtifact

    def to_dict(self) -> dict[str, Any]:
        return {
            "capability_profiles": self.capability_profiles.to_dict(),
            "hook_execution_log": self.hook_execution_log.to_dict(),
            "run_checkpoint_manifest": self.run_checkpoint_manifest.to_dict(),
            "data_access_audit": self.data_access_audit.to_dict(),
            "context_influence_report": self.context_influence_report.to_dict(),
        }


def build_runtime_controls_from_policy(policy: dict[str, Any]) -> RuntimeControls:
    """Derive runtime controls from the canonical policy payload."""
    runtime_cfg = dict(policy.get("runtime", {}))
    try:
        max_recent_events = int(runtime_cfg.get("max_recent_events", 50) or 50)
    except (TypeError, ValueError):
        max_recent_events = 50
    privacy_cfg = dict(policy.get("privacy", {}))
    local_only_default = bool(privacy_cfg.get("local_only", True))
    return RuntimeControls(
        enabled=bool(runtime_cfg.get("gateway_enabled", True)),
        append_only_events=True,
        read_only_hooks_enabled=bool(runtime_cfg.get("read_only_hooks_enabled", True)),
        write_hooks_enabled=bool(runtime_cfg.get("allow_write_hooks", False)),
        checkpoint_on_stage_complete=bool(runtime_cfg.get("checkpoint_on_stage_complete", True)),
        capability_enforcement_enabled=bool(runtime_cfg.get("capability_enforcement_enabled", True)),
        semantic_rowless_default=bool(runtime_cfg.get("semantic_rowless_default", True)),
        local_only=local_only_default,
        max_recent_events=max(10, min(200, max_recent_events)),
    )


def build_default_capability_profiles() -> list[CapabilityProfile]:
    """Return the canonical specialist capability profiles for the local lab runtime."""
    return [
        CapabilityProfile(
            specialist="intake_translator",
            phase="intake",
            artifact_read_scope=["lab_mandate.json", "work_preferences.json", "run_brief.json", "data_origin.json", "domain_brief.json", "task_brief.json"],
            artifact_write_scope=["intake_record.json", "autonomy_mode.json", "clarification_queue.json", "assumption_log.json", "context_interpretation.json", "context_constraints.json", "semantic_mapping.json"],
            raw_row_access=True,
            semantic_access="rowless_only",
            external_adapter_access=["pandera"],
            network_access=False,
            notes=["May inspect local rows for target/type grounding, but semantic work remains summary-first."],
        ),
        CapabilityProfile(
            specialist="scout",
            phase="investigation",
            artifact_read_scope=["task_brief.json", "domain_brief.json", "data_origin.json"],
            artifact_write_scope=["dataset_profile.json"],
            raw_row_access=True,
            semantic_access="not_allowed",
            external_adapter_access=[],
            network_access=False,
            notes=["Scout owns deterministic dataset profiling and may read raw rows locally."],
        ),
        CapabilityProfile(
            specialist="scientist",
            phase="investigation",
            artifact_read_scope=["dataset_profile.json", "task_brief.json", "domain_brief.json", "run_brief.json"],
            artifact_write_scope=["domain_memo.json", "objective_hypotheses.json"],
            raw_row_access=False,
            semantic_access="rowless_only",
            external_adapter_access=[],
            network_access=False,
            notes=["Scientist reasons from profiles and summaries, not unrestricted raw rows."],
        ),
        CapabilityProfile(
            specialist="focus_council",
            phase="investigation",
            artifact_read_scope=["dataset_profile.json", "domain_memo.json", "run_brief.json", "task_brief.json"],
            artifact_write_scope=["focus_debate.json", "focus_profile.json", "optimization_profile.json", "feature_strategy_profile.json"],
            raw_row_access=False,
            semantic_access="rowless_only",
            external_adapter_access=[],
            network_access=False,
            notes=["Focus Council resolves objective pressure from structured evidence only."],
        ),
        CapabilityProfile(
            specialist="memory_retrieval_agent",
            phase="memory",
            artifact_read_scope=["run_summary.json", "challenger_report.json", "completion_decision.json", "promotion_decision.json", "reflection_memory.json"],
            artifact_write_scope=["memory_retrieval.json", "analog_run_candidates.json", "route_prior_context.json", "challenger_prior_suggestions.json", "reflection_memory.json", "memory_flush_report.json"],
            raw_row_access=False,
            semantic_access="rowless_only",
            external_adapter_access=[],
            network_access=False,
            notes=["Run memory is artifact-first and should not pull raw historical rows by default."],
        ),
        CapabilityProfile(
            specialist="strategist",
            phase="planning",
            artifact_read_scope=["dataset_profile.json", "domain_memo.json", "focus_profile.json", "optimization_profile.json", "feature_strategy_profile.json", "route_prior_context.json"],
            artifact_write_scope=["plan.json", "alternatives.json", "hypotheses.json", "experiment_priority_report.json", "marginal_value_of_next_experiment.json"],
            raw_row_access=False,
            semantic_access="rowless_only",
            external_adapter_access=[],
            network_access=False,
            notes=["Strategist should plan from artifacts and priors rather than browsing rows directly."],
        ),
        CapabilityProfile(
            specialist="builder",
            phase="planning",
            artifact_read_scope=["plan.json", "policy_resolved.yaml"],
            artifact_write_scope=["model_params.json", "normalization_state.json", "model_state.json", "checkpoints/"],
            raw_row_access=True,
            semantic_access="not_allowed",
            external_adapter_access=[],
            network_access=False,
            notes=["Builder may read local rows to train or score the selected deterministic route."],
        ),
        CapabilityProfile(
            specialist="challenger",
            phase="evidence",
            artifact_read_scope=["plan.json", "model_params.json", "route_prior_context.json", "challenger_prior_suggestions.json"],
            artifact_write_scope=["experiment_registry.json", "challenger_report.json", "ablation_report.json", "audit_report.json", "belief_update.json", "leaderboard.csv"],
            raw_row_access=True,
            semantic_access="rowless_only",
            external_adapter_access=["statsmodels", "imbalanced_learn", "pyod"],
            network_access=False,
            notes=["Evidence work may read local rows but semantic help still defaults to rowless summaries."],
        ),
        CapabilityProfile(
            specialist="research_librarian",
            phase="research",
            artifact_read_scope=["run_brief.json", "task_brief.json", "dataset_profile.json", "plan.json", "semantic_debate_report.json"],
            artifact_write_scope=["research_query_plan.json", "research_source_inventory.json", "research_brief.json", "method_transfer_report.json", "benchmark_reference_report.json", "external_research_audit.json"],
            raw_row_access=False,
            semantic_access="rowless_only",
            external_adapter_access=["semantic_scholar", "crossref"],
            network_access=True,
            notes=["Research retrieval is redacted, rowless, and policy-gated even when external sources are enabled."],
        ),
        CapabilityProfile(
            specialist="benchmark_referee",
            phase="benchmark",
            artifact_read_scope=["plan.json", "model_params.json", "task_brief.json", "run_brief.json"],
            artifact_write_scope=["reference_approach_matrix.json", "benchmark_gap_report.json", "benchmark_parity_report.json"],
            raw_row_access=True,
            semantic_access="not_allowed",
            external_adapter_access=["scikit_learn", "flaml"],
            network_access=False,
            notes=["Benchmark parity uses the same local split and feature contract as the active Relaytic route."],
        ),
        CapabilityProfile(
            specialist="completion_governor",
            phase="completion",
            artifact_read_scope=["run_summary.json", "belief_update.json", "audit_report.json", "route_prior_context.json", "memory_retrieval.json"],
            artifact_write_scope=["completion_decision.json", "run_state.json", "stage_timeline.json", "mandate_evidence_review.json", "blocking_analysis.json", "next_action_queue.json"],
            raw_row_access=False,
            semantic_access="rowless_only",
            external_adapter_access=[],
            network_access=False,
            notes=["Completion should judge from artifacts and evidence, not unrestricted data access."],
        ),
        CapabilityProfile(
            specialist="lifecycle_governor",
            phase="lifecycle",
            artifact_read_scope=["champion_vs_candidate.json", "completion_decision.json", "memory_retrieval.json", "run_summary.json"],
            artifact_write_scope=["champion_vs_candidate.json", "recalibration_decision.json", "retrain_decision.json", "promotion_decision.json", "rollback_decision.json"],
            raw_row_access=False,
            semantic_access="rowless_only",
            external_adapter_access=["mapie", "evidently", "mlflow"],
            network_access=False,
            notes=["Lifecycle decisions stay artifact-driven even when richer adapters exist."],
        ),
        CapabilityProfile(
            specialist="semantic_helper",
            phase="intelligence",
            artifact_read_scope=["context_assembly_report.json", "doc_grounding_report.json", "semantic_task_request.json"],
            artifact_write_scope=[
                "semantic_task_results.json",
                "semantic_access_audit.json",
                "semantic_debate_report.json",
                "semantic_counterposition_pack.json",
                "semantic_uncertainty_report.json",
                "intelligence_escalation.json",
            ],
            raw_row_access=False,
            semantic_access="rowless_only",
            external_adapter_access=["local_llm"],
            network_access=False,
            notes=["Semantic helpers are rowless by default and require explicit policy for richer access."],
        ),
        CapabilityProfile(
            specialist="autonomy_controller",
            phase="autonomy",
            artifact_read_scope=[
                "plan.json",
                "audit_report.json",
                "completion_decision.json",
                "promotion_decision.json",
                "semantic_debate_report.json",
                "semantic_uncertainty_report.json",
            ],
            artifact_write_scope=[
                "autonomy_loop_state.json",
                "autonomy_round_report.json",
                "challenger_queue.json",
                "branch_outcome_matrix.json",
                "retrain_run_request.json",
                "recalibration_run_request.json",
                "champion_lineage.json",
                "loop_budget_report.json",
            ],
            raw_row_access=False,
            semantic_access="rowless_only",
            external_adapter_access=[],
            network_access=False,
            notes=["Autonomy stays bounded and coordinates only one follow-up round per review pass."],
        ),
    ]
