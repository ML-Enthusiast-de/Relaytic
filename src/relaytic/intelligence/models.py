"""Typed artifact models for Slice 09 structured semantic intelligence."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


INTELLIGENCE_CONTROLS_SCHEMA_VERSION = "relaytic.intelligence_controls.v1"
INTELLIGENCE_MODE_SCHEMA_VERSION = "relaytic.intelligence_mode.v1"
LLM_ROUTING_PLAN_SCHEMA_VERSION = "relaytic.llm_routing_plan.v1"
LOCAL_LLM_PROFILE_SCHEMA_VERSION = "relaytic.local_llm_profile.v1"
LLM_BACKEND_DISCOVERY_SCHEMA_VERSION = "relaytic.llm_backend_discovery.v1"
LLM_HEALTH_CHECK_SCHEMA_VERSION = "relaytic.llm_health_check.v1"
LLM_UPGRADE_SUGGESTIONS_SCHEMA_VERSION = "relaytic.llm_upgrade_suggestions.v1"
SEMANTIC_TASK_REQUEST_SCHEMA_VERSION = "relaytic.semantic_task_request.v1"
SEMANTIC_TASK_RESULTS_SCHEMA_VERSION = "relaytic.semantic_task_results.v1"
INTELLIGENCE_ESCALATION_SCHEMA_VERSION = "relaytic.intelligence_escalation.v1"
VERIFIER_REPORT_SCHEMA_VERSION = "relaytic.verifier_report.v1"
SEMANTIC_DEBATE_REPORT_SCHEMA_VERSION = "relaytic.semantic_debate_report.v1"
SEMANTIC_COUNTERPOSITION_PACK_SCHEMA_VERSION = "relaytic.semantic_counterposition_pack.v1"
SEMANTIC_UNCERTAINTY_REPORT_SCHEMA_VERSION = "relaytic.semantic_uncertainty_report.v1"
CONTEXT_ASSEMBLY_REPORT_SCHEMA_VERSION = "relaytic.context_assembly_report.v1"
DOC_GROUNDING_REPORT_SCHEMA_VERSION = "relaytic.doc_grounding_report.v1"
SEMANTIC_ACCESS_AUDIT_SCHEMA_VERSION = "relaytic.semantic_access_audit.v1"
SEMANTIC_PROOF_REPORT_SCHEMA_VERSION = "relaytic.semantic_proof_report.v1"


@dataclass(frozen=True)
class IntelligenceControls:
    """Resolved controls for Slice 09 intelligence work."""

    schema_version: str = INTELLIGENCE_CONTROLS_SCHEMA_VERSION
    enabled: bool = True
    intelligence_mode: str = "none"
    allow_structured_semantic_tasks: bool = True
    prefer_local_llm: bool = True
    allow_frontier_llm: bool = False
    allow_max_reasoning: bool = False
    minimum_local_llm_enabled: bool = False
    minimum_local_llm_profile: str = "none"
    require_schema_constrained_actions: bool = True
    require_verifier_for_high_impact_decisions: bool = True
    enable_backend_discovery: bool = True
    allow_upgrade_suggestions: bool = True
    allow_mode_routing: bool = True
    hardware_aware_routing: bool = True
    enable_semantic_proof: bool = True
    semantic_rowless_default: bool = True
    max_context_blocks: int = 14

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class IntelligenceTrace:
    """Execution trace for one intelligence artifact."""

    agent: str
    operating_mode: str
    llm_used: bool
    llm_status: str
    deterministic_evidence: list[str] = field(default_factory=list)
    advisory_notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class IntelligenceModeArtifact:
    schema_version: str
    generated_at: str
    controls: IntelligenceControls
    configured_mode: str
    effective_mode: str
    backend_status: str
    llm_used: bool
    rowless_default: bool
    summary: str
    trace: IntelligenceTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class LLMRoutingPlanArtifact:
    schema_version: str
    generated_at: str
    controls: IntelligenceControls
    status: str
    requested_mode: str
    recommended_mode: str
    selected_mode: str
    semantic_pressure: str
    reason_codes: list[str]
    selected_backend: dict[str, Any]
    selected_profile: dict[str, Any]
    capability_matrix: dict[str, Any]
    phase_assignments: list[dict[str, Any]]
    summary: str
    trace: IntelligenceTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class LocalLLMProfileArtifact:
    schema_version: str
    generated_at: str
    controls: IntelligenceControls
    status: str
    provider: str | None
    profile_name: str | None
    model: str | None
    cpu_only: bool | None
    n_gpu_layers: str | None
    max_context: int | None
    recommended_mode: str
    profile_origin: str
    hardware_snapshot: dict[str, Any]
    notes: list[str]
    summary: str
    trace: IntelligenceTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class LLMBackendDiscoveryArtifact:
    schema_version: str
    generated_at: str
    controls: IntelligenceControls
    status: str
    requested_provider: str | None
    resolved_provider: str | None
    resolved_model: str | None
    endpoint: str | None
    endpoint_scope: str
    profile: str | None
    notes: list[str]
    summary: str
    trace: IntelligenceTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class LLMHealthCheckArtifact:
    schema_version: str
    generated_at: str
    controls: IntelligenceControls
    status: str
    checked: bool
    provider: str | None
    model: str | None
    endpoint: str | None
    latency_ms: float | None
    notes: list[str]
    summary: str
    trace: IntelligenceTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class LLMUpgradeSuggestionsArtifact:
    schema_version: str
    generated_at: str
    controls: IntelligenceControls
    status: str
    suggestions: list[dict[str, Any]]
    summary: str
    trace: IntelligenceTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class ContextAssemblyReport:
    schema_version: str
    generated_at: str
    controls: IntelligenceControls
    status: str
    rowless_context: bool
    context_blocks: list[dict[str, Any]]
    source_artifacts: list[str]
    summary: str
    trace: IntelligenceTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class DocGroundingReport:
    schema_version: str
    generated_at: str
    controls: IntelligenceControls
    status: str
    source_documents: list[dict[str, Any]]
    grounding_points: list[dict[str, Any]]
    summary: str
    trace: IntelligenceTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class SemanticTaskRequestArtifact:
    schema_version: str
    generated_at: str
    controls: IntelligenceControls
    status: str
    tasks: list[dict[str, Any]]
    context_digest: dict[str, Any]
    summary: str
    trace: IntelligenceTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class SemanticTaskResultsArtifact:
    schema_version: str
    generated_at: str
    controls: IntelligenceControls
    status: str
    provider_status: str
    tasks: list[dict[str, Any]]
    summary: str
    trace: IntelligenceTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class IntelligenceEscalationArtifact:
    schema_version: str
    generated_at: str
    controls: IntelligenceControls
    status: str
    escalation_required: bool
    reason_codes: list[str]
    recommended_path: str
    summary: str
    trace: IntelligenceTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class VerifierReportArtifact:
    schema_version: str
    generated_at: str
    controls: IntelligenceControls
    status: str
    llm_used: bool
    provider_status: str
    selected_action: str
    baseline_action: str
    changed_from_deterministic_baseline: bool
    verifier_payload: dict[str, Any]
    summary: str
    trace: IntelligenceTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class SemanticDebateReport:
    schema_version: str
    generated_at: str
    controls: IntelligenceControls
    status: str
    proposer_position: dict[str, Any]
    counterposition: dict[str, Any]
    verifier_verdict: dict[str, Any]
    domain_interpretation: dict[str, Any]
    recommended_followup_action: str
    confidence: str
    summary: str
    trace: IntelligenceTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class SemanticCounterpositionPack:
    schema_version: str
    generated_at: str
    controls: IntelligenceControls
    status: str
    positions: list[dict[str, Any]]
    summary: str
    trace: IntelligenceTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class SemanticUncertaintyReport:
    schema_version: str
    generated_at: str
    controls: IntelligenceControls
    status: str
    confidence_band: str
    unresolved_items: list[dict[str, Any]]
    reason_codes: list[str]
    summary: str
    trace: IntelligenceTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class SemanticAccessAudit:
    schema_version: str
    generated_at: str
    controls: IntelligenceControls
    status: str
    row_level_access_requested: bool
    row_level_access_granted: bool
    accessed_artifacts: list[str]
    redactions: list[str]
    summary: str
    trace: IntelligenceTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class SemanticProofReport:
    schema_version: str
    generated_at: str
    controls: IntelligenceControls
    status: str
    llm_used: bool
    deterministic_baseline_action: str | None
    routed_action: str | None
    changed_fields: list[str]
    measurable_gain_detected: bool
    benchmark_dimensions: list[dict[str, Any]]
    summary: str
    trace: IntelligenceTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class IntelligenceBundle:
    intelligence_mode: IntelligenceModeArtifact
    llm_routing_plan: LLMRoutingPlanArtifact
    local_llm_profile: LocalLLMProfileArtifact
    llm_backend_discovery: LLMBackendDiscoveryArtifact
    llm_health_check: LLMHealthCheckArtifact
    llm_upgrade_suggestions: LLMUpgradeSuggestionsArtifact
    semantic_task_request: SemanticTaskRequestArtifact
    semantic_task_results: SemanticTaskResultsArtifact
    intelligence_escalation: IntelligenceEscalationArtifact
    verifier_report: VerifierReportArtifact
    context_assembly_report: ContextAssemblyReport
    doc_grounding_report: DocGroundingReport
    semantic_access_audit: SemanticAccessAudit
    semantic_debate_report: SemanticDebateReport
    semantic_counterposition_pack: SemanticCounterpositionPack
    semantic_uncertainty_report: SemanticUncertaintyReport
    semantic_proof_report: SemanticProofReport

    def to_dict(self) -> dict[str, Any]:
        return {
            "intelligence_mode": self.intelligence_mode.to_dict(),
            "llm_routing_plan": self.llm_routing_plan.to_dict(),
            "local_llm_profile": self.local_llm_profile.to_dict(),
            "llm_backend_discovery": self.llm_backend_discovery.to_dict(),
            "llm_health_check": self.llm_health_check.to_dict(),
            "llm_upgrade_suggestions": self.llm_upgrade_suggestions.to_dict(),
            "semantic_task_request": self.semantic_task_request.to_dict(),
            "semantic_task_results": self.semantic_task_results.to_dict(),
            "intelligence_escalation": self.intelligence_escalation.to_dict(),
            "verifier_report": self.verifier_report.to_dict(),
            "context_assembly_report": self.context_assembly_report.to_dict(),
            "doc_grounding_report": self.doc_grounding_report.to_dict(),
            "semantic_access_audit": self.semantic_access_audit.to_dict(),
            "semantic_debate_report": self.semantic_debate_report.to_dict(),
            "semantic_counterposition_pack": self.semantic_counterposition_pack.to_dict(),
            "semantic_uncertainty_report": self.semantic_uncertainty_report.to_dict(),
            "semantic_proof_report": self.semantic_proof_report.to_dict(),
        }


def build_intelligence_controls_from_policy(policy: dict[str, Any]) -> IntelligenceControls:
    """Derive intelligence controls from the canonical policy payload."""

    intelligence_cfg = dict(policy.get("intelligence", {}))
    runtime_cfg = dict(policy.get("runtime", {}))
    intelligence_mode = str(intelligence_cfg.get("intelligence_mode", "none")).strip() or "none"
    try:
        max_context_blocks = int(runtime_cfg.get("max_recent_events", 50) or 50) // 4
    except (TypeError, ValueError):
        max_context_blocks = 12
    return IntelligenceControls(
        enabled=bool(intelligence_cfg.get("enabled", True)),
        intelligence_mode=intelligence_mode,
        allow_structured_semantic_tasks=True,
        prefer_local_llm=bool(intelligence_cfg.get("prefer_local_llm", True)),
        allow_frontier_llm=bool(intelligence_cfg.get("allow_frontier_llm", False)),
        allow_max_reasoning=bool(intelligence_cfg.get("allow_max_reasoning", False)),
        minimum_local_llm_enabled=bool(intelligence_cfg.get("minimum_local_llm_enabled", False)),
        minimum_local_llm_profile=str(intelligence_cfg.get("minimum_local_llm_profile", "none")),
        require_schema_constrained_actions=bool(intelligence_cfg.get("require_schema_constrained_actions", True)),
        require_verifier_for_high_impact_decisions=bool(
            intelligence_cfg.get("require_verifier_for_high_impact_decisions", True)
        ),
        enable_backend_discovery=bool(intelligence_cfg.get("enable_backend_discovery", True)),
        allow_upgrade_suggestions=bool(intelligence_cfg.get("allow_upgrade_suggestions", True)),
        allow_mode_routing=bool(intelligence_cfg.get("allow_mode_routing", True)),
        hardware_aware_routing=bool(intelligence_cfg.get("hardware_aware_routing", True)),
        enable_semantic_proof=bool(intelligence_cfg.get("enable_semantic_proof", True)),
        semantic_rowless_default=bool(runtime_cfg.get("semantic_rowless_default", True)),
        max_context_blocks=max(6, min(20, max_context_blocks)),
    )
