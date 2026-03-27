"""Typed artifact models for Slice 12 dojo mode and guarded self-improvement."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


DOJO_CONTROLS_SCHEMA_VERSION = "relaytic.dojo_controls.v1"
DOJO_SESSION_SCHEMA_VERSION = "relaytic.dojo_session.v1"
DOJO_HYPOTHESES_SCHEMA_VERSION = "relaytic.dojo_hypotheses.v1"
DOJO_RESULTS_SCHEMA_VERSION = "relaytic.dojo_results.v1"
DOJO_PROMOTIONS_SCHEMA_VERSION = "relaytic.dojo_promotions.v1"
ARCHITECTURE_PROPOSALS_SCHEMA_VERSION = "relaytic.architecture_proposals.v1"


@dataclass(frozen=True)
class DojoControls:
    schema_version: str = DOJO_CONTROLS_SCHEMA_VERSION
    enabled: bool = True
    allow_method_self_improvement: bool = True
    allow_architecture_proposals: bool = True
    require_quarantine_before_promotion: bool = True
    require_benchmark_gate: bool = True
    require_quality_proxy_gate: bool = True
    require_control_security_gate: bool = True
    max_active_promotions: int = 3

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, payload: dict[str, Any] | None) -> "DojoControls":
        payload = dict(payload or {})
        max_active = int(payload.get("max_active_promotions", 3) or 3)
        return cls(
            enabled=bool(payload.get("enabled", True)),
            allow_method_self_improvement=bool(payload.get("allow_method_self_improvement", True)),
            allow_architecture_proposals=bool(payload.get("allow_architecture_proposals", True)),
            require_quarantine_before_promotion=bool(payload.get("require_quarantine_before_promotion", True)),
            require_benchmark_gate=bool(payload.get("require_benchmark_gate", True)),
            require_quality_proxy_gate=bool(payload.get("require_quality_proxy_gate", True)),
            require_control_security_gate=bool(payload.get("require_control_security_gate", True)),
            max_active_promotions=max(1, max_active),
        )


@dataclass(frozen=True)
class DojoTrace:
    agent: str
    operating_mode: str
    llm_used: bool
    llm_status: str
    deterministic_evidence: list[str] = field(default_factory=list)
    advisory_notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, payload: dict[str, Any] | None) -> "DojoTrace":
        payload = dict(payload or {})
        return cls(
            agent=str(payload.get("agent", "dojo_referee") or "dojo_referee"),
            operating_mode=str(payload.get("operating_mode", "deterministic_quarantine") or "deterministic_quarantine"),
            llm_used=bool(payload.get("llm_used", False)),
            llm_status=str(payload.get("llm_status", "not_used") or "not_used"),
            deterministic_evidence=[str(item).strip() for item in payload.get("deterministic_evidence", []) if str(item).strip()],
            advisory_notes=[str(item).strip() for item in payload.get("advisory_notes", []) if str(item).strip()],
        )


@dataclass(frozen=True)
class DojoSession:
    schema_version: str
    generated_at: str
    controls: DojoControls
    status: str
    quarantine_active: bool
    benchmark_state: str
    quality_gate_status: str | None
    control_security_state: str
    incumbent_present: bool
    active_promotion_count: int
    rejected_count: int
    quarantined_count: int
    summary: str
    trace: DojoTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload

    @classmethod
    def from_dict(cls, payload: dict[str, Any] | None) -> "DojoSession":
        payload = dict(payload or {})
        return cls(
            schema_version=str(payload.get("schema_version", DOJO_SESSION_SCHEMA_VERSION) or DOJO_SESSION_SCHEMA_VERSION),
            generated_at=str(payload.get("generated_at", "") or ""),
            controls=DojoControls.from_dict(payload.get("controls")),
            status=str(payload.get("status", "unknown") or "unknown"),
            quarantine_active=bool(payload.get("quarantine_active", True)),
            benchmark_state=str(payload.get("benchmark_state", "not_available") or "not_available"),
            quality_gate_status=_optional_text(payload.get("quality_gate_status")),
            control_security_state=str(payload.get("control_security_state", "unknown") or "unknown"),
            incumbent_present=bool(payload.get("incumbent_present", False)),
            active_promotion_count=int(payload.get("active_promotion_count", 0) or 0),
            rejected_count=int(payload.get("rejected_count", 0) or 0),
            quarantined_count=int(payload.get("quarantined_count", 0) or 0),
            summary=str(payload.get("summary", "") or ""),
            trace=DojoTrace.from_dict(payload.get("trace")),
        )


@dataclass(frozen=True)
class DojoHypotheses:
    schema_version: str
    generated_at: str
    controls: DojoControls
    status: str
    proposal_count: int
    proposals: list[dict[str, Any]]
    summary: str
    trace: DojoTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload

    @classmethod
    def from_dict(cls, payload: dict[str, Any] | None) -> "DojoHypotheses":
        payload = dict(payload or {})
        proposals = [dict(item) for item in payload.get("proposals", []) if isinstance(item, dict)]
        return cls(
            schema_version=str(payload.get("schema_version", DOJO_HYPOTHESES_SCHEMA_VERSION) or DOJO_HYPOTHESES_SCHEMA_VERSION),
            generated_at=str(payload.get("generated_at", "") or ""),
            controls=DojoControls.from_dict(payload.get("controls")),
            status=str(payload.get("status", "unknown") or "unknown"),
            proposal_count=int(payload.get("proposal_count", len(proposals)) or len(proposals)),
            proposals=proposals,
            summary=str(payload.get("summary", "") or ""),
            trace=DojoTrace.from_dict(payload.get("trace")),
        )


@dataclass(frozen=True)
class DojoResults:
    schema_version: str
    generated_at: str
    controls: DojoControls
    status: str
    promoted_count: int
    rejected_count: int
    quarantined_count: int
    results: list[dict[str, Any]]
    summary: str
    trace: DojoTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload

    @classmethod
    def from_dict(cls, payload: dict[str, Any] | None) -> "DojoResults":
        payload = dict(payload or {})
        results = [dict(item) for item in payload.get("results", []) if isinstance(item, dict)]
        return cls(
            schema_version=str(payload.get("schema_version", DOJO_RESULTS_SCHEMA_VERSION) or DOJO_RESULTS_SCHEMA_VERSION),
            generated_at=str(payload.get("generated_at", "") or ""),
            controls=DojoControls.from_dict(payload.get("controls")),
            status=str(payload.get("status", "unknown") or "unknown"),
            promoted_count=int(payload.get("promoted_count", 0) or 0),
            rejected_count=int(payload.get("rejected_count", 0) or 0),
            quarantined_count=int(payload.get("quarantined_count", 0) or 0),
            results=results,
            summary=str(payload.get("summary", "") or ""),
            trace=DojoTrace.from_dict(payload.get("trace")),
        )


@dataclass(frozen=True)
class DojoPromotions:
    schema_version: str
    generated_at: str
    controls: DojoControls
    status: str
    active_promotions: list[dict[str, Any]]
    rejected_proposals: list[dict[str, Any]]
    quarantined_proposals: list[dict[str, Any]]
    rolled_back_promotions: list[dict[str, Any]]
    promotion_ledger: list[dict[str, Any]]
    summary: str
    trace: DojoTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload

    @classmethod
    def from_dict(cls, payload: dict[str, Any] | None) -> "DojoPromotions":
        payload = dict(payload or {})
        return cls(
            schema_version=str(payload.get("schema_version", DOJO_PROMOTIONS_SCHEMA_VERSION) or DOJO_PROMOTIONS_SCHEMA_VERSION),
            generated_at=str(payload.get("generated_at", "") or ""),
            controls=DojoControls.from_dict(payload.get("controls")),
            status=str(payload.get("status", "unknown") or "unknown"),
            active_promotions=[dict(item) for item in payload.get("active_promotions", []) if isinstance(item, dict)],
            rejected_proposals=[dict(item) for item in payload.get("rejected_proposals", []) if isinstance(item, dict)],
            quarantined_proposals=[dict(item) for item in payload.get("quarantined_proposals", []) if isinstance(item, dict)],
            rolled_back_promotions=[dict(item) for item in payload.get("rolled_back_promotions", []) if isinstance(item, dict)],
            promotion_ledger=[dict(item) for item in payload.get("promotion_ledger", []) if isinstance(item, dict)],
            summary=str(payload.get("summary", "") or ""),
            trace=DojoTrace.from_dict(payload.get("trace")),
        )


@dataclass(frozen=True)
class ArchitectureProposals:
    schema_version: str
    generated_at: str
    controls: DojoControls
    status: str
    proposal_count: int
    proposals: list[dict[str, Any]]
    summary: str
    trace: DojoTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload

    @classmethod
    def from_dict(cls, payload: dict[str, Any] | None) -> "ArchitectureProposals":
        payload = dict(payload or {})
        proposals = [dict(item) for item in payload.get("proposals", []) if isinstance(item, dict)]
        return cls(
            schema_version=str(payload.get("schema_version", ARCHITECTURE_PROPOSALS_SCHEMA_VERSION) or ARCHITECTURE_PROPOSALS_SCHEMA_VERSION),
            generated_at=str(payload.get("generated_at", "") or ""),
            controls=DojoControls.from_dict(payload.get("controls")),
            status=str(payload.get("status", "unknown") or "unknown"),
            proposal_count=int(payload.get("proposal_count", len(proposals)) or len(proposals)),
            proposals=proposals,
            summary=str(payload.get("summary", "") or ""),
            trace=DojoTrace.from_dict(payload.get("trace")),
        )


@dataclass(frozen=True)
class DojoBundle:
    dojo_session: DojoSession
    dojo_hypotheses: DojoHypotheses
    dojo_results: DojoResults
    dojo_promotions: DojoPromotions
    architecture_proposals: ArchitectureProposals

    def to_dict(self) -> dict[str, Any]:
        return {
            "dojo_session": self.dojo_session.to_dict(),
            "dojo_hypotheses": self.dojo_hypotheses.to_dict(),
            "dojo_results": self.dojo_results.to_dict(),
            "dojo_promotions": self.dojo_promotions.to_dict(),
            "architecture_proposals": self.architecture_proposals.to_dict(),
        }


def build_dojo_controls_from_policy(policy: dict[str, Any]) -> DojoControls:
    cfg = dict(policy.get("dojo", {}))
    max_active = int(cfg.get("max_active_promotions", 3) or 3)
    return DojoControls(
        enabled=bool(cfg.get("enabled", True)),
        allow_method_self_improvement=bool(cfg.get("allow_method_self_improvement", True)),
        allow_architecture_proposals=bool(cfg.get("allow_architecture_proposals", True)),
        require_quarantine_before_promotion=bool(cfg.get("require_quarantine_before_promotion", True)),
        require_benchmark_gate=bool(cfg.get("require_benchmark_gate", True)),
        require_quality_proxy_gate=bool(cfg.get("require_quality_proxy_gate", True)),
        require_control_security_gate=bool(cfg.get("require_control_security_gate", True)),
        max_active_promotions=max(1, max_active),
    )


def dojo_bundle_from_dict(payload: dict[str, Any]) -> DojoBundle:
    payload = dict(payload or {})
    return DojoBundle(
        dojo_session=DojoSession.from_dict(payload.get("dojo_session")),
        dojo_hypotheses=DojoHypotheses.from_dict(payload.get("dojo_hypotheses")),
        dojo_results=DojoResults.from_dict(payload.get("dojo_results")),
        dojo_promotions=DojoPromotions.from_dict(payload.get("dojo_promotions")),
        architecture_proposals=ArchitectureProposals.from_dict(payload.get("architecture_proposals")),
    )


def _optional_text(value: Any) -> str | None:
    text = str(value or "").strip()
    return text or None
