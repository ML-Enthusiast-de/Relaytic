"""Typed artifact models for Slice 12B tracing and deterministic adjudication."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


TRACE_CONTROLS_SCHEMA_VERSION = "relaytic.trace_controls.v1"
TRACE_SPAN_SCHEMA_VERSION = "relaytic.trace_span.v1"
TRACE_MODEL_SCHEMA_VERSION = "relaytic.trace_model.v1"
SPECIALIST_TRACE_INDEX_SCHEMA_VERSION = "relaytic.specialist_trace_index.v1"
BRANCH_TRACE_GRAPH_SCHEMA_VERSION = "relaytic.branch_trace_graph.v1"
CLAIM_PACKET_SCHEMA_VERSION = "relaytic.claim_packet.v1"
ADJUDICATION_SCORECARD_SCHEMA_VERSION = "relaytic.adjudication_scorecard.v1"
DECISION_REPLAY_REPORT_SCHEMA_VERSION = "relaytic.decision_replay_report.v1"


@dataclass(frozen=True)
class TraceControls:
    schema_version: str = TRACE_CONTROLS_SCHEMA_VERSION
    enabled: bool = True
    backfill_from_runtime_events: bool = True
    direct_runtime_span_writes: bool = True
    max_replay_spans: int = 80
    conformance_surfaces: list[str] = field(default_factory=lambda: ["cli", "mcp"])

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_policy(cls, policy: dict[str, Any] | None) -> "TraceControls":
        payload = dict((policy or {}).get("tracing", {}))
        surfaces = [
            str(item).strip().lower()
            for item in payload.get("conformance_surfaces", ["cli", "mcp"])
            if str(item).strip()
        ]
        return cls(
            enabled=bool(payload.get("enabled", True)),
            backfill_from_runtime_events=bool(payload.get("backfill_from_runtime_events", True)),
            direct_runtime_span_writes=bool(payload.get("direct_runtime_span_writes", True)),
            max_replay_spans=max(10, int(payload.get("max_replay_spans", 80) or 80)),
            conformance_surfaces=surfaces or ["cli", "mcp"],
        )


@dataclass(frozen=True)
class TraceSpan:
    schema_version: str
    span_id: str
    occurred_at: str
    span_kind: str
    event_type: str
    stage: str
    specialist: str | None
    source_surface: str
    source_command: str | None
    status: str
    summary: str
    trace_ref: str | None
    evidence_refs: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ClaimPacket:
    schema_version: str
    claim_id: str
    generated_at: str
    stage: str
    specialist: str
    claim_type: str
    proposed_action: str
    target_scope: str
    objective_frame: str
    confidence: float
    evidence_refs: list[str]
    empirical_support: dict[str, Any]
    risk_flags: list[str]
    assumptions: list[str]
    falsifiers: list[str]
    policy_constraints: list[str]
    trace_ref: str | None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class AdjudicationEntry:
    claim_id: str
    specialist: str
    proposed_action: str
    confidence: float
    empirical_support_score: float
    policy_fit_score: float
    benchmark_fit_score: float
    memory_consistency_score: float
    decision_value_score: float
    uncertainty_penalty: float
    risk_penalty: float
    cost_penalty: float
    reversibility_bonus: float
    final_score: float
    reasons: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class AdjudicationScorecard:
    schema_version: str
    generated_at: str
    controls: TraceControls
    status: str
    decision_id: str
    decision_scope: str
    winning_claim_id: str | None
    winning_action: str | None
    scorecard: list[AdjudicationEntry]
    why_won: list[str]
    why_not_others: list[dict[str, str]]
    summary: str

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["scorecard"] = [item.to_dict() for item in self.scorecard]
        return payload


@dataclass(frozen=True)
class TraceModelArtifact:
    schema_version: str
    generated_at: str
    controls: TraceControls
    status: str
    span_count: int
    claim_count: int
    branch_count: int
    tool_trace_count: int
    intervention_trace_count: int
    conformance_surfaces: list[str]
    direct_runtime_emission_detected: bool
    summary: str

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        return payload


@dataclass(frozen=True)
class SpecialistTraceIndexArtifact:
    schema_version: str
    generated_at: str
    controls: TraceControls
    status: str
    entries: list[dict[str, Any]]
    summary: str

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        return payload


@dataclass(frozen=True)
class BranchTraceGraphArtifact:
    schema_version: str
    generated_at: str
    controls: TraceControls
    status: str
    nodes: list[dict[str, Any]]
    edges: list[dict[str, Any]]
    summary: str

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        return payload


@dataclass(frozen=True)
class DecisionReplayReportArtifact:
    schema_version: str
    generated_at: str
    controls: TraceControls
    status: str
    timeline: list[dict[str, Any]]
    winning_claim_id: str | None
    winning_action: str | None
    competing_claim_count: int
    summary: str

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        return payload


@dataclass(frozen=True)
class TraceBundle:
    trace_model: TraceModelArtifact
    specialist_trace_index: SpecialistTraceIndexArtifact
    branch_trace_graph: BranchTraceGraphArtifact
    adjudication_scorecard: AdjudicationScorecard
    decision_replay_report: DecisionReplayReportArtifact
    trace_span_log: list[TraceSpan]
    tool_trace_log: list[dict[str, Any]]
    intervention_trace_log: list[dict[str, Any]]
    claim_packet_log: list[ClaimPacket]

    def to_dict(self) -> dict[str, Any]:
        return {
            "trace_model": self.trace_model.to_dict(),
            "specialist_trace_index": self.specialist_trace_index.to_dict(),
            "branch_trace_graph": self.branch_trace_graph.to_dict(),
            "adjudication_scorecard": self.adjudication_scorecard.to_dict(),
            "decision_replay_report": self.decision_replay_report.to_dict(),
            "trace_span_log": [item.to_dict() for item in self.trace_span_log],
            "tool_trace_log": list(self.tool_trace_log),
            "intervention_trace_log": list(self.intervention_trace_log),
            "claim_packet_log": [item.to_dict() for item in self.claim_packet_log],
        }
