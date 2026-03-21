"""Typed artifact models for Slice 09D private research retrieval."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


RESEARCH_CONTROLS_SCHEMA_VERSION = "relaytic.research_controls.v1"
RESEARCH_QUERY_PLAN_SCHEMA_VERSION = "relaytic.research_query_plan.v1"
RESEARCH_SOURCE_INVENTORY_SCHEMA_VERSION = "relaytic.research_source_inventory.v1"
RESEARCH_BRIEF_SCHEMA_VERSION = "relaytic.research_brief.v1"
METHOD_TRANSFER_REPORT_SCHEMA_VERSION = "relaytic.method_transfer_report.v1"
BENCHMARK_REFERENCE_REPORT_SCHEMA_VERSION = "relaytic.benchmark_reference_report.v1"
EXTERNAL_RESEARCH_AUDIT_SCHEMA_VERSION = "relaytic.external_research_audit.v1"


@dataclass(frozen=True)
class ResearchControls:
    schema_version: str = RESEARCH_CONTROLS_SCHEMA_VERSION
    enabled: bool = False
    allow_external_research: bool = False
    require_redaction_default: bool = True
    require_rowless_queries: bool = True
    allow_benchmark_reference_retrieval: bool = True
    allow_method_transfer: bool = True
    max_queries: int = 3
    max_results_per_source: int = 5
    timeout_seconds: int = 10
    source_order: list[str] = field(default_factory=lambda: ["semantic_scholar", "crossref"])
    semantic_scholar_endpoint: str = "https://api.semanticscholar.org/graph/v1/paper/search"
    crossref_endpoint: str = "https://api.crossref.org/works"
    contact_email: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ResearchTrace:
    agent: str
    operating_mode: str
    llm_used: bool
    llm_status: str
    deterministic_evidence: list[str] = field(default_factory=list)
    advisory_notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ResearchQueryPlan:
    schema_version: str
    generated_at: str
    controls: ResearchControls
    status: str
    query_signature: dict[str, Any]
    redaction_summary: dict[str, Any]
    exported_fields: list[str]
    queries: list[dict[str, Any]]
    summary: str
    trace: ResearchTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class ResearchSourceInventory:
    schema_version: str
    generated_at: str
    controls: ResearchControls
    status: str
    queries_executed: list[dict[str, Any]]
    sources: list[dict[str, Any]]
    source_counts: dict[str, Any]
    endpoint_status: list[dict[str, Any]]
    summary: str
    trace: ResearchTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class ResearchBrief:
    schema_version: str
    generated_at: str
    controls: ResearchControls
    status: str
    top_findings: list[dict[str, Any]]
    contradictions: list[dict[str, Any]]
    recommended_followup_action: str
    confidence: str
    summary: str
    trace: ResearchTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class MethodTransferReport:
    schema_version: str
    generated_at: str
    controls: ResearchControls
    status: str
    accepted_candidates: list[dict[str, Any]]
    rejected_candidates: list[dict[str, Any]]
    advisory_candidates: list[dict[str, Any]]
    summary: str
    trace: ResearchTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class BenchmarkReferenceReport:
    schema_version: str
    generated_at: str
    controls: ResearchControls
    status: str
    benchmark_expected: bool
    reference_count: int
    references: list[dict[str, Any]]
    summary: str
    trace: ResearchTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class ExternalResearchAudit:
    schema_version: str
    generated_at: str
    controls: ResearchControls
    status: str
    network_attempted: bool
    network_allowed: bool
    raw_rows_exported: bool
    identifier_leak_detected: bool
    exported_fields: list[str]
    redactions: list[str]
    query_texts: list[str]
    endpoints_contacted: list[str]
    source_classes: list[str]
    request_count: int
    summary: str
    trace: ResearchTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class ResearchBundle:
    research_query_plan: ResearchQueryPlan
    research_source_inventory: ResearchSourceInventory
    research_brief: ResearchBrief
    method_transfer_report: MethodTransferReport
    benchmark_reference_report: BenchmarkReferenceReport
    external_research_audit: ExternalResearchAudit

    def to_dict(self) -> dict[str, Any]:
        return {
            "research_query_plan": self.research_query_plan.to_dict(),
            "research_source_inventory": self.research_source_inventory.to_dict(),
            "research_brief": self.research_brief.to_dict(),
            "method_transfer_report": self.method_transfer_report.to_dict(),
            "benchmark_reference_report": self.benchmark_reference_report.to_dict(),
            "external_research_audit": self.external_research_audit.to_dict(),
        }


def build_research_controls_from_policy(policy: dict[str, Any]) -> ResearchControls:
    research_cfg = dict(policy.get("research", {}))
    privacy_cfg = dict(policy.get("privacy", {}))
    runtime_cfg = dict(policy.get("runtime", {}))
    contact_email = research_cfg.get("contact_email", "")
    if contact_email is None:
        contact_email = ""
    source_order = [
        str(item).strip()
        for item in research_cfg.get("source_order", ["semantic_scholar", "crossref"])
        if str(item).strip()
    ]
    if not source_order:
        source_order = ["semantic_scholar", "crossref"]
    try:
        max_queries = int(research_cfg.get("max_queries", 3) or 3)
    except (TypeError, ValueError):
        max_queries = 3
    try:
        max_results = int(research_cfg.get("max_results_per_source", 5) or 5)
    except (TypeError, ValueError):
        max_results = 5
    try:
        timeout_seconds = int(runtime_cfg.get("timeout_seconds", research_cfg.get("timeout_seconds", 10)) or 10)
    except (TypeError, ValueError):
        timeout_seconds = 10
    enabled = bool(research_cfg.get("enabled", False))
    return ResearchControls(
        enabled=enabled,
        allow_external_research=enabled and bool(privacy_cfg.get("api_calls_allowed", False)),
        require_redaction_default=bool(research_cfg.get("require_redaction_default", True)),
        require_rowless_queries=bool(runtime_cfg.get("semantic_rowless_default", True)),
        allow_benchmark_reference_retrieval=bool(
            research_cfg.get("allow_benchmark_reference_retrieval", True)
        ),
        allow_method_transfer=bool(research_cfg.get("allow_method_transfer", True)),
        max_queries=max(1, min(5, max_queries)),
        max_results_per_source=max(1, min(8, max_results)),
        timeout_seconds=max(2, min(30, timeout_seconds)),
        source_order=source_order[:3],
        semantic_scholar_endpoint=str(
            research_cfg.get(
                "semantic_scholar_endpoint",
                "https://api.semanticscholar.org/graph/v1/paper/search",
            )
        ).strip()
        or "https://api.semanticscholar.org/graph/v1/paper/search",
        crossref_endpoint=str(
            research_cfg.get("crossref_endpoint", "https://api.crossref.org/works")
        ).strip()
        or "https://api.crossref.org/works",
        contact_email=str(contact_email).strip() or None,
    )
