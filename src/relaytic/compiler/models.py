"""Typed artifact models for Slice 10A method compilation."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


COMPILER_CONTROLS_SCHEMA_VERSION = "relaytic.compiler_controls.v1"
METHOD_COMPILER_REPORT_SCHEMA_VERSION = "relaytic.method_compiler_report.v1"
COMPILED_CHALLENGER_TEMPLATES_SCHEMA_VERSION = "relaytic.compiled_challenger_templates.v1"
COMPILED_FEATURE_HYPOTHESES_SCHEMA_VERSION = "relaytic.compiled_feature_hypotheses.v1"
COMPILED_BENCHMARK_PROTOCOL_SCHEMA_VERSION = "relaytic.compiled_benchmark_protocol.v1"
METHOD_IMPORT_REPORT_SCHEMA_VERSION = "relaytic.method_import_report.v1"
ARCHITECTURE_CANDIDATE_REGISTRY_SCHEMA_VERSION = "relaytic.architecture_candidate_registry.v1"


@dataclass(frozen=True)
class CompilerControls:
    schema_version: str = COMPILER_CONTROLS_SCHEMA_VERSION
    enabled: bool = True
    max_compiled_templates: int = 6

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class CompilerTrace:
    agent: str
    operating_mode: str
    llm_used: bool
    llm_status: str
    deterministic_evidence: list[str] = field(default_factory=list)
    advisory_notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class MethodCompilerReport:
    schema_version: str
    generated_at: str
    controls: CompilerControls
    status: str
    accepted_transfer_count: int
    compiled_challenger_count: int
    compiled_feature_count: int
    compiled_benchmark_change_count: int
    reasoning_sources: list[str]
    summary: str
    trace: CompilerTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class CompiledChallengerTemplates:
    schema_version: str
    generated_at: str
    controls: CompilerControls
    status: str
    templates: list[dict[str, Any]]
    summary: str
    trace: CompilerTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class CompiledFeatureHypotheses:
    schema_version: str
    generated_at: str
    controls: CompilerControls
    status: str
    hypotheses: list[dict[str, Any]]
    summary: str
    trace: CompilerTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class CompiledBenchmarkProtocol:
    schema_version: str
    generated_at: str
    controls: CompilerControls
    status: str
    protocol_updates: list[dict[str, Any]]
    summary: str
    trace: CompilerTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class MethodImportReport:
    schema_version: str
    generated_at: str
    controls: CompilerControls
    status: str
    imported_family_count: int
    accepted_family_count: int
    advisory_family_count: int
    rejected_family_count: int
    shadow_only_count: int
    unavailable_count: int
    imported_families: list[dict[str, Any]]
    summary: str
    trace: CompilerTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class ArchitectureCandidateRegistry:
    schema_version: str
    generated_at: str
    controls: CompilerControls
    status: str
    candidate_count: int
    shadow_only_count: int
    unavailable_count: int
    replay_only_count: int
    candidates: list[dict[str, Any]]
    summary: str
    trace: CompilerTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


def build_compiler_controls_from_policy(policy: dict[str, Any]) -> CompilerControls:
    decision_cfg = dict(policy.get("decision", {}))
    return CompilerControls(
        enabled=bool(decision_cfg.get("enabled", True)),
        max_compiled_templates=max(1, int(decision_cfg.get("max_compiled_templates", 6) or 6)),
    )
