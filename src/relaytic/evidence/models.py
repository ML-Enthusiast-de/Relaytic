"""Typed artifact models for Slice 06 evidence outputs."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


EVIDENCE_CONTROLS_SCHEMA_VERSION = "relaytic.evidence_controls.v1"
EXPERIMENT_REGISTRY_SCHEMA_VERSION = "relaytic.experiment_registry.v1"
CHALLENGER_REPORT_SCHEMA_VERSION = "relaytic.challenger_report.v1"
ABLATION_REPORT_SCHEMA_VERSION = "relaytic.ablation_report.v1"
AUDIT_REPORT_SCHEMA_VERSION = "relaytic.audit_report.v1"
BELIEF_UPDATE_SCHEMA_VERSION = "relaytic.belief_update.v1"


@dataclass(frozen=True)
class EvidenceControls:
    """Resolved controls that govern Slice 06 evidence collection."""

    schema_version: str = EVIDENCE_CONTROLS_SCHEMA_VERSION
    enabled: bool = True
    challenger_enabled: bool = True
    ablation_enabled: bool = True
    audit_enabled: bool = True
    intelligence_mode: str = "none"
    prefer_local_llm: bool = True
    allow_local_llm_advisory: bool = False
    require_deterministic_floor: bool = True
    max_ablation_features: int = 3

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class EvidenceTrace:
    """Execution trace for the Slice 06 evidence layer."""

    agent: str
    operating_mode: str
    llm_used: bool
    llm_status: str
    deterministic_evidence: list[str] = field(default_factory=list)
    advisory_notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ExperimentRegistry:
    """Registry of champion, challenger, and ablation experiments."""

    schema_version: str
    generated_at: str
    controls: EvidenceControls
    champion_experiment_id: str
    experiments: list[dict[str, Any]]
    summary: str
    trace: EvidenceTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class ChallengerReport:
    """Comparison between the selected route champion and the first challenger."""

    schema_version: str
    generated_at: str
    controls: EvidenceControls
    champion_experiment_id: str
    challenger_experiment_id: str | None
    comparison_metric: str
    comparison_split: str
    winner: str
    delta_to_champion: float | None
    summary: str
    comparison: dict[str, Any]
    memory_context: dict[str, Any] | None
    llm_advisory: dict[str, Any] | None
    trace: EvidenceTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class AblationReport:
    """First-pass feature ablation evidence for the champion family."""

    schema_version: str
    generated_at: str
    controls: EvidenceControls
    baseline_experiment_id: str
    comparison_metric: str
    comparison_split: str
    ablations: list[dict[str, Any]]
    summary: str
    trace: EvidenceTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class AuditReport:
    """Operational audit of the current champion after Slice 06 evidence."""

    schema_version: str
    generated_at: str
    controls: EvidenceControls
    champion_experiment_id: str
    provisional_recommendation: str
    readiness_level: str
    findings: list[dict[str, Any]]
    external_diagnostics: list[dict[str, Any]]
    inference_audit_path: str | None
    llm_advisory: dict[str, Any] | None
    summary: str
    trace: EvidenceTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class BeliefUpdate:
    """Provisional belief update after challenger and audit pressure."""

    schema_version: str
    generated_at: str
    controls: EvidenceControls
    previous_belief: str
    updated_belief: str
    recommended_action: str
    confidence_level: str
    supporting_evidence: list[str]
    open_questions: list[str]
    llm_advisory: dict[str, Any] | None
    summary: str
    trace: EvidenceTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class EvidenceBundle:
    """Full Slice 06 evidence bundle."""

    experiment_registry: ExperimentRegistry
    challenger_report: ChallengerReport
    ablation_report: AblationReport
    audit_report: AuditReport
    belief_update: BeliefUpdate

    def to_dict(self) -> dict[str, Any]:
        return {
            "experiment_registry": self.experiment_registry.to_dict(),
            "challenger_report": self.challenger_report.to_dict(),
            "ablation_report": self.ablation_report.to_dict(),
            "audit_report": self.audit_report.to_dict(),
            "belief_update": self.belief_update.to_dict(),
        }


def build_evidence_controls_from_policy(policy: dict[str, Any]) -> EvidenceControls:
    """Derive evidence controls from the canonical policy payload."""
    intelligence_cfg = dict(policy.get("intelligence", {}))
    compute_cfg = dict(policy.get("compute", {}))
    intelligence_mode = str(intelligence_cfg.get("intelligence_mode", "none")).strip() or "none"
    normalized_mode = intelligence_mode.lower().replace("-", "_")
    advisory_enabled = normalized_mode not in {"", "none", "off", "disabled", "deterministic"}
    try:
        max_trials = max(1, int(compute_cfg.get("max_parallel_trials", 4) or 4))
    except (TypeError, ValueError):
        max_trials = 4
    return EvidenceControls(
        enabled=True,
        challenger_enabled=True,
        ablation_enabled=True,
        audit_enabled=True,
        intelligence_mode=intelligence_mode,
        prefer_local_llm=bool(intelligence_cfg.get("prefer_local_llm", True)),
        allow_local_llm_advisory=bool(intelligence_cfg.get("enabled", True)) and advisory_enabled,
        require_deterministic_floor=True,
        max_ablation_features=max(1, min(3, max_trials)),
    )
