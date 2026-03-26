"""Typed artifact models for Slice 10A local data-fabric reasoning."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


DATA_FABRIC_CONTROLS_SCHEMA_VERSION = "relaytic.data_fabric_controls.v1"
SOURCE_GRAPH_SCHEMA_VERSION = "relaytic.source_graph.v1"
JOIN_CANDIDATE_REPORT_SCHEMA_VERSION = "relaytic.join_candidate_report.v1"
DATA_ACQUISITION_PLAN_SCHEMA_VERSION = "relaytic.data_acquisition_plan.v1"


@dataclass(frozen=True)
class DataFabricControls:
    schema_version: str = DATA_FABRIC_CONTROLS_SCHEMA_VERSION
    enabled: bool = True
    allow_local_source_graph: bool = True
    same_directory_only: bool = True
    max_nearby_sources: int = 6
    max_join_candidates: int = 5

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class DataFabricTrace:
    agent: str
    operating_mode: str
    llm_used: bool
    llm_status: str
    deterministic_evidence: list[str] = field(default_factory=list)
    advisory_notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class SourceGraph:
    schema_version: str
    generated_at: str
    controls: DataFabricControls
    status: str
    current_source_id: str
    source_count: int
    edge_count: int
    nodes: list[dict[str, Any]]
    edges: list[dict[str, Any]]
    summary: str
    trace: DataFabricTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class JoinCandidateReport:
    schema_version: str
    generated_at: str
    controls: DataFabricControls
    status: str
    selected_candidate_id: str | None
    candidate_count: int
    candidates: list[dict[str, Any]]
    summary: str
    trace: DataFabricTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class DataAcquisitionPlan:
    schema_version: str
    generated_at: str
    controls: DataFabricControls
    status: str
    selected_strategy: str
    recommended_source_id: str | None
    recommended_join_candidate_id: str | None
    recommended_data_path: str | None
    bounded_followups: list[dict[str, Any]]
    summary: str
    trace: DataFabricTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


def build_data_fabric_controls_from_policy(policy: dict[str, Any]) -> DataFabricControls:
    decision_cfg = dict(policy.get("decision", {}))
    return DataFabricControls(
        enabled=bool(decision_cfg.get("enabled", True)),
        allow_local_source_graph=bool(decision_cfg.get("allow_local_source_graph", True)),
        same_directory_only=bool(decision_cfg.get("same_directory_only", True)),
        max_nearby_sources=max(1, int(decision_cfg.get("max_nearby_sources", 6) or 6)),
        max_join_candidates=max(1, int(decision_cfg.get("max_join_candidates", 5) or 5)),
    )
