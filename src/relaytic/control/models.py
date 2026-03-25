"""Typed artifact models for Slice 10C behavioral control contracts."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


CONTROL_CONTROLS_SCHEMA_VERSION = "relaytic.control_controls.v1"
INTERVENTION_REQUEST_SCHEMA_VERSION = "relaytic.intervention_request.v1"
INTERVENTION_CONTRACT_SCHEMA_VERSION = "relaytic.intervention_contract.v1"
CONTROL_CHALLENGE_REPORT_SCHEMA_VERSION = "relaytic.control_challenge_report.v1"
OVERRIDE_DECISION_SCHEMA_VERSION = "relaytic.override_decision.v1"
INTERVENTION_LEDGER_SCHEMA_VERSION = "relaytic.intervention_ledger.v1"
RECOVERY_CHECKPOINT_SCHEMA_VERSION = "relaytic.recovery_checkpoint.v1"
CONTROL_INJECTION_AUDIT_SCHEMA_VERSION = "relaytic.control_injection_audit.v1"
CAUSAL_MEMORY_INDEX_SCHEMA_VERSION = "relaytic.causal_memory_index.v1"
INTERVENTION_MEMORY_LOG_SCHEMA_VERSION = "relaytic.intervention_memory_log.v1"
OUTCOME_MEMORY_GRAPH_SCHEMA_VERSION = "relaytic.outcome_memory_graph.v1"
METHOD_MEMORY_INDEX_SCHEMA_VERSION = "relaytic.method_memory_index.v1"


@dataclass(frozen=True)
class ControlControls:
    schema_version: str = CONTROL_CONTROLS_SCHEMA_VERSION
    enabled: bool = True
    allow_navigation_without_challenge: bool = True
    challenge_material_requests: bool = True
    checkpoint_before_override: bool = True
    reject_policy_bypass: bool = True
    skeptical_takeover_enabled: bool = True
    causal_memory_enabled: bool = True
    cross_run_memory_enabled: bool = True
    max_prior_runs: int = 12
    max_ledger_entries: int = 40

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ControlTrace:
    agent: str
    operating_mode: str
    llm_used: bool
    llm_status: str
    deterministic_evidence: list[str] = field(default_factory=list)
    advisory_notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class InterventionRequest:
    schema_version: str
    generated_at: str
    controls: ControlControls
    status: str
    request_id: str
    actor_type: str
    actor_name: str | None
    source_surface: str
    source_command: str | None
    raw_message: str
    normalized_message: str
    requested_action_kind: str
    requested_stage: str | None
    request_classification: str
    authority_level: str
    challenge_required: bool
    bypass_patterns: list[str]
    under_specified: bool
    summary: str
    trace: ControlTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class InterventionContract:
    schema_version: str
    generated_at: str
    controls: ControlControls
    status: str
    authority_order: list[str]
    low_friction_actions: list[str]
    challenge_required_actions: list[str]
    blocked_patterns: list[str]
    summary: str
    trace: ControlTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class ControlChallengeReport:
    schema_version: str
    generated_at: str
    controls: ControlControls
    status: str
    challenge_level: str
    skepticism_level: str
    challenge_required: bool
    similar_harmful_override_count: int
    reasons: list[str]
    accepted_scope: str | None
    risk_flags: list[str]
    summary: str
    trace: ControlTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class OverrideDecision:
    schema_version: str
    generated_at: str
    controls: ControlControls
    status: str
    decision: str
    approved_action_kind: str
    approved_stage: str | None
    requires_checkpoint: bool
    challenge_required: bool
    checkpoint_reason: str | None
    skepticism_applied: bool
    execution_blocked: bool
    summary: str
    trace: ControlTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class InterventionLedger:
    schema_version: str
    generated_at: str
    controls: ControlControls
    status: str
    entry_count: int
    entries: list[dict[str, Any]]
    summary: str
    trace: ControlTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class RecoveryCheckpoint:
    schema_version: str
    generated_at: str
    controls: ControlControls
    status: str
    checkpoint_id: str
    stage_before: str
    selected_model_family: str | None
    next_recommended_action: str | None
    preserved_artifacts: list[str]
    summary: str
    trace: ControlTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class ControlInjectionAudit:
    schema_version: str
    generated_at: str
    controls: ControlControls
    status: str
    suspicious_count: int
    rejected_count: int
    detected_patterns: list[str]
    summary: str
    trace: ControlTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class CausalMemoryIndex:
    schema_version: str
    generated_at: str
    controls: ControlControls
    status: str
    current_request_id: str
    prior_run_count: int
    similar_harmful_override_count: int
    skeptical_bias_level: str
    linked_memories: list[dict[str, Any]]
    summary: str
    trace: ControlTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class InterventionMemoryLog:
    schema_version: str
    generated_at: str
    controls: ControlControls
    status: str
    entry_count: int
    entries: list[dict[str, Any]]
    summary: str
    trace: ControlTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class OutcomeMemoryGraph:
    schema_version: str
    generated_at: str
    controls: ControlControls
    status: str
    outcome_link_count: int
    nodes: list[dict[str, Any]]
    edges: list[dict[str, Any]]
    summary: str
    trace: ControlTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class MethodMemoryIndex:
    schema_version: str
    generated_at: str
    controls: ControlControls
    status: str
    positive_method_count: int
    negative_method_count: int
    methods: list[dict[str, Any]]
    summary: str
    trace: ControlTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class ControlBundle:
    intervention_request: InterventionRequest
    intervention_contract: InterventionContract
    control_challenge_report: ControlChallengeReport
    override_decision: OverrideDecision
    intervention_ledger: InterventionLedger
    recovery_checkpoint: RecoveryCheckpoint
    control_injection_audit: ControlInjectionAudit
    causal_memory_index: CausalMemoryIndex
    intervention_memory_log: InterventionMemoryLog
    outcome_memory_graph: OutcomeMemoryGraph
    method_memory_index: MethodMemoryIndex

    def to_dict(self) -> dict[str, Any]:
        return {
            "intervention_request": self.intervention_request.to_dict(),
            "intervention_contract": self.intervention_contract.to_dict(),
            "control_challenge_report": self.control_challenge_report.to_dict(),
            "override_decision": self.override_decision.to_dict(),
            "intervention_ledger": self.intervention_ledger.to_dict(),
            "recovery_checkpoint": self.recovery_checkpoint.to_dict(),
            "control_injection_audit": self.control_injection_audit.to_dict(),
            "causal_memory_index": self.causal_memory_index.to_dict(),
            "intervention_memory_log": self.intervention_memory_log.to_dict(),
            "outcome_memory_graph": self.outcome_memory_graph.to_dict(),
            "method_memory_index": self.method_memory_index.to_dict(),
        }


def build_control_controls_from_policy(policy: dict[str, Any]) -> ControlControls:
    control_cfg = dict(policy.get("control", {}))
    return ControlControls(
        enabled=bool(control_cfg.get("enabled", True)),
        allow_navigation_without_challenge=bool(control_cfg.get("allow_navigation_without_challenge", True)),
        challenge_material_requests=bool(control_cfg.get("challenge_material_requests", True)),
        checkpoint_before_override=bool(control_cfg.get("checkpoint_before_override", True)),
        reject_policy_bypass=bool(control_cfg.get("reject_policy_bypass", True)),
        skeptical_takeover_enabled=bool(control_cfg.get("skeptical_takeover_enabled", True)),
        causal_memory_enabled=bool(control_cfg.get("causal_memory_enabled", True)),
        cross_run_memory_enabled=bool(control_cfg.get("cross_run_memory_enabled", True)),
        max_prior_runs=max(1, int(control_cfg.get("max_prior_runs", 12) or 12)),
        max_ledger_entries=max(1, int(control_cfg.get("max_ledger_entries", 40) or 40)),
    )
