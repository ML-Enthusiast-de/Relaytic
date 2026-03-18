"""Stable context models for the early Relaytic foundation."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class ContextControl:
    """How optional context is permitted to influence a run."""

    enabled: bool = True
    external_retrieval_allowed: bool = False
    allow_uploaded_docs: bool = True
    require_provenance: bool = True
    semantic_task_enabled: bool = True

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class DataOrigin:
    """Where the dataset came from and how it should be treated."""

    controls: ContextControl
    source_name: str = "unspecified"
    source_type: str = "snapshot"
    acquisition_notes: str = "No data-origin notes provided."
    owner: str | None = None
    contains_pii: bool | None = None
    access_constraints: list[str] = field(default_factory=list)
    refresh_cadence: str | None = None
    schema_version: str = "relaytic.data_origin.v1"

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        return payload


@dataclass(frozen=True)
class DomainBrief:
    """Domain framing, caveats, and forbidden-feature notes."""

    controls: ContextControl
    system_name: str = "unspecified"
    summary: str = "No domain brief provided. Relaytic should proceed in ungrounded mode until more context is available."
    target_meaning: str | None = None
    known_caveats: list[str] = field(default_factory=list)
    suspicious_columns: list[str] = field(default_factory=list)
    forbidden_features: list[str] = field(default_factory=list)
    binding_constraints: list[str] = field(default_factory=list)
    assumptions: list[str] = field(default_factory=list)
    schema_version: str = "relaytic.domain_brief.v1"

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        return payload


@dataclass(frozen=True)
class TaskBrief:
    """What the operator actually wants solved."""

    controls: ContextControl
    problem_statement: str = "No task brief provided. Relaytic should infer a working task from dataset evidence and explicit operator instructions."
    target_column: str | None = None
    prediction_horizon: str | None = None
    decision_type: str | None = None
    task_type_hint: str | None = None
    domain_archetype_hint: str | None = None
    primary_stakeholder: str | None = None
    success_criteria: list[str] = field(default_factory=list)
    failure_costs: list[str] = field(default_factory=list)
    notes: str = ""
    schema_version: str = "relaytic.task_brief.v1"

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        return payload


def build_context_controls_from_policy(policy: dict[str, Any]) -> ContextControl:
    """Derive context controls from the resolved Relaytic policy."""
    context_cfg = dict(policy.get("context", {}))
    return ContextControl(
        enabled=bool(context_cfg.get("enabled", True)),
        external_retrieval_allowed=bool(context_cfg.get("external_retrieval_allowed", False)),
        allow_uploaded_docs=bool(context_cfg.get("allow_uploaded_docs", True)),
        require_provenance=bool(context_cfg.get("require_provenance", True)),
        semantic_task_enabled=bool(context_cfg.get("semantic_task_enabled", True)),
    )


def default_data_origin(
    controls: ContextControl,
    *,
    source_name: str | None = None,
    source_type: str | None = None,
    acquisition_notes: str | None = None,
    owner: str | None = None,
    contains_pii: bool | None = None,
    access_constraints: list[str] | None = None,
    refresh_cadence: str | None = None,
) -> DataOrigin:
    return DataOrigin(
        controls=controls,
        source_name=source_name or "unspecified",
        source_type=source_type or "snapshot",
        acquisition_notes=acquisition_notes or "No data-origin notes provided.",
        owner=owner,
        contains_pii=contains_pii,
        access_constraints=list(access_constraints or []),
        refresh_cadence=refresh_cadence,
    )


def default_domain_brief(
    controls: ContextControl,
    *,
    system_name: str | None = None,
    summary: str | None = None,
    target_meaning: str | None = None,
    known_caveats: list[str] | None = None,
    suspicious_columns: list[str] | None = None,
    forbidden_features: list[str] | None = None,
    binding_constraints: list[str] | None = None,
    assumptions: list[str] | None = None,
) -> DomainBrief:
    return DomainBrief(
        controls=controls,
        system_name=system_name or "unspecified",
        summary=summary
        or "No domain brief provided. Relaytic should proceed in ungrounded mode until more context is available.",
        target_meaning=target_meaning,
        known_caveats=list(known_caveats or []),
        suspicious_columns=list(suspicious_columns or []),
        forbidden_features=list(forbidden_features or []),
        binding_constraints=list(binding_constraints or []),
        assumptions=list(assumptions or []),
    )


def default_task_brief(
    controls: ContextControl,
    *,
    problem_statement: str | None = None,
    target_column: str | None = None,
    prediction_horizon: str | None = None,
    decision_type: str | None = None,
    task_type_hint: str | None = None,
    domain_archetype_hint: str | None = None,
    primary_stakeholder: str | None = None,
    success_criteria: list[str] | None = None,
    failure_costs: list[str] | None = None,
    notes: str = "",
) -> TaskBrief:
    criteria = list(success_criteria or [])
    if not criteria:
        criteria.append("Clarify what should be optimized before expensive search begins.")
        criteria.append("Proceed safely when context is missing or ambiguous.")
    return TaskBrief(
        controls=controls,
        problem_statement=problem_statement
        or "No task brief provided. Relaytic should infer a working task from dataset evidence and explicit operator instructions.",
        target_column=target_column,
        prediction_horizon=prediction_horizon,
        decision_type=decision_type,
        task_type_hint=task_type_hint,
        domain_archetype_hint=domain_archetype_hint,
        primary_stakeholder=primary_stakeholder,
        success_criteria=criteria,
        failure_costs=list(failure_costs or []),
        notes=notes,
    )
