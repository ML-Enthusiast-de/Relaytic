"""Typed artifact models for Slice 12B agent, security, and protocol evals."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


EVAL_CONTROLS_SCHEMA_VERSION = "relaytic.eval_controls.v1"
AGENT_EVAL_MATRIX_SCHEMA_VERSION = "relaytic.agent_eval_matrix.v1"
SECURITY_EVAL_REPORT_SCHEMA_VERSION = "relaytic.security_eval_report.v1"
RED_TEAM_REPORT_SCHEMA_VERSION = "relaytic.red_team_report.v1"
PROTOCOL_CONFORMANCE_REPORT_SCHEMA_VERSION = "relaytic.protocol_conformance_report.v1"
HOST_SURFACE_MATRIX_SCHEMA_VERSION = "relaytic.host_surface_matrix.v1"
TRACE_IDENTITY_CONFORMANCE_SCHEMA_VERSION = "relaytic.trace_identity_conformance.v1"
EVAL_SURFACE_PARITY_REPORT_SCHEMA_VERSION = "relaytic.eval_surface_parity_report.v1"


@dataclass(frozen=True)
class EvalControls:
    schema_version: str = EVAL_CONTROLS_SCHEMA_VERSION
    enabled: bool = True
    require_protocol_conformance: bool = True
    require_security_evals: bool = True
    require_high_confidence_loser_proof: bool = True
    fail_on_protocol_mismatch: bool = True
    tracked_surfaces: list[str] = field(default_factory=lambda: ["cli", "mcp"])
    max_reported_findings: int = 6

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_policy(cls, policy: dict[str, Any] | None) -> "EvalControls":
        payload = dict((policy or {}).get("evals", {}))
        tracked_surfaces = [
            str(item).strip().lower()
            for item in payload.get("tracked_surfaces", ["cli", "mcp"])
            if str(item).strip()
        ]
        return cls(
            enabled=bool(payload.get("enabled", True)),
            require_protocol_conformance=bool(payload.get("require_protocol_conformance", True)),
            require_security_evals=bool(payload.get("require_security_evals", True)),
            require_high_confidence_loser_proof=bool(payload.get("require_high_confidence_loser_proof", True)),
            fail_on_protocol_mismatch=bool(payload.get("fail_on_protocol_mismatch", True)),
            tracked_surfaces=tracked_surfaces or ["cli", "mcp"],
            max_reported_findings=max(1, int(payload.get("max_reported_findings", 6) or 6)),
        )


@dataclass(frozen=True)
class EvalTrace:
    agent: str
    operating_mode: str
    llm_used: bool
    llm_status: str
    deterministic_evidence: list[str] = field(default_factory=list)
    advisory_notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class AgentEvalMatrixArtifact:
    schema_version: str
    generated_at: str
    controls: EvalControls
    status: str
    passed_count: int
    failed_count: int
    not_applicable_count: int
    scenarios: list[dict[str, Any]]
    summary: str
    trace: EvalTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class SecurityEvalReportArtifact:
    schema_version: str
    generated_at: str
    controls: EvalControls
    status: str
    suspicious_count: int
    defended_count: int
    open_finding_count: int
    open_findings: list[dict[str, Any]]
    summary: str
    trace: EvalTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class RedTeamReportArtifact:
    schema_version: str
    generated_at: str
    controls: EvalControls
    status: str
    attempted_scenarios: list[dict[str, Any]]
    passed_count: int
    finding_count: int
    summary: str
    trace: EvalTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class ProtocolConformanceReportArtifact:
    schema_version: str
    generated_at: str
    controls: EvalControls
    status: str
    compared_surfaces: list[str]
    checked_fields: list[str]
    mismatch_count: int
    mismatches: list[dict[str, Any]]
    summary: str
    trace: EvalTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class HostSurfaceMatrixArtifact:
    schema_version: str
    generated_at: str
    controls: EvalControls
    status: str
    aligned_fields: list[str]
    surfaces: list[dict[str, Any]]
    summary: str
    trace: EvalTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class TraceIdentityConformanceArtifact:
    schema_version: str
    generated_at: str
    controls: EvalControls
    status: str
    canonical_winning_claim_id: str | None
    canonical_winning_action: str | None
    compared_surfaces: list[str]
    mismatch_count: int
    mismatches: list[dict[str, Any]]
    summary: str
    trace: EvalTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class EvalSurfaceParityReportArtifact:
    schema_version: str
    generated_at: str
    controls: EvalControls
    status: str
    compared_fields: list[str]
    mismatch_count: int
    mismatches: list[dict[str, Any]]
    summary: str
    trace: EvalTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class EvalBundle:
    agent_eval_matrix: AgentEvalMatrixArtifact
    security_eval_report: SecurityEvalReportArtifact
    red_team_report: RedTeamReportArtifact
    protocol_conformance_report: ProtocolConformanceReportArtifact
    host_surface_matrix: HostSurfaceMatrixArtifact
    trace_identity_conformance: TraceIdentityConformanceArtifact
    eval_surface_parity_report: EvalSurfaceParityReportArtifact

    def to_dict(self) -> dict[str, Any]:
        return {
            "agent_eval_matrix": self.agent_eval_matrix.to_dict(),
            "security_eval_report": self.security_eval_report.to_dict(),
            "red_team_report": self.red_team_report.to_dict(),
            "protocol_conformance_report": self.protocol_conformance_report.to_dict(),
            "host_surface_matrix": self.host_surface_matrix.to_dict(),
            "trace_identity_conformance": self.trace_identity_conformance.to_dict(),
            "eval_surface_parity_report": self.eval_surface_parity_report.to_dict(),
        }
