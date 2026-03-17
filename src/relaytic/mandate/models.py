"""Stable mandate models for the early Relaytic foundation."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


ALLOWED_INFLUENCE_MODES = {
    "off",
    "advisory",
    "weighted",
    "binding",
    "constitutional",
}


@dataclass(frozen=True)
class MandateControl:
    """How the mandate layer influences a run."""

    enabled: bool = True
    influence_mode: str = "weighted"
    allow_agent_challenges: bool = True
    require_disagreement_logging: bool = True
    allow_soft_preference_override_with_evidence: bool = True

    def __post_init__(self) -> None:
        if self.influence_mode not in ALLOWED_INFLUENCE_MODES:
            raise ValueError(
                f"Unsupported influence mode '{self.influence_mode}'. "
                f"Use one of {sorted(ALLOWED_INFLUENCE_MODES)}."
            )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class LabMandate:
    """Durable lab values and hard boundaries."""

    controls: MandateControl
    values: list[str] = field(default_factory=list)
    hard_constraints: list[str] = field(default_factory=list)
    soft_preferences: list[str] = field(default_factory=list)
    prohibited_actions: list[str] = field(default_factory=list)
    notes: str = ""
    schema_version: str = "relaytic.lab_mandate.v1"

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        return payload


@dataclass(frozen=True)
class WorkPreferences:
    """Semi-stable operator working preferences."""

    controls: MandateControl
    execution_mode_preference: str | None = None
    operation_mode_preference: str | None = None
    preferred_report_style: str = "concise"
    preferred_effort_tier: str = "standard"
    notes: str = ""
    schema_version: str = "relaytic.work_preferences.v1"

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        return payload


@dataclass(frozen=True)
class RunBrief:
    """Run-specific intent for one Relaytic execution."""

    controls: MandateControl
    objective: str = "best_robust_pareto_front"
    target_column: str | None = None
    deployment_target: str | None = None
    success_criteria: list[str] = field(default_factory=list)
    binding_constraints: list[str] = field(default_factory=list)
    notes: str = ""
    schema_version: str = "relaytic.run_brief.v1"

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        return payload


def build_mandate_controls_from_policy(policy: dict[str, Any]) -> MandateControl:
    """Derive mandate controls from the resolved Relaytic policy."""
    mandate_cfg = dict(policy.get("mandate", {}))
    return MandateControl(
        enabled=bool(mandate_cfg.get("enabled", True)),
        influence_mode=str(mandate_cfg.get("influence_mode", "weighted")),
        allow_agent_challenges=bool(mandate_cfg.get("allow_agent_challenges", True)),
        require_disagreement_logging=bool(
            mandate_cfg.get("require_disagreement_logging", True)
        ),
        allow_soft_preference_override_with_evidence=bool(
            mandate_cfg.get("allow_soft_preference_override_with_evidence", True)
        ),
    )


def default_lab_mandate(controls: MandateControl) -> LabMandate:
    """Default lab mandate aligned with the Relaytic vision."""
    return LabMandate(
        controls=controls,
        values=[
            "local-first execution",
            "deterministic floor before optional intelligence amplification",
            "evidence over intuition",
            "artifact-rich and auditable decisions",
        ],
        hard_constraints=[
            "do not require remote APIs by default",
            "do not bypass safety, policy, or budget controls",
        ],
        soft_preferences=[
            "favor robust inference over vanity metrics",
            "prefer inspectable behavior over hidden automation",
        ],
        prohibited_actions=[
            "persist raw secrets into artifacts",
            "silently enable non-local backends",
        ],
        notes="Default Relaytic mandate scaffold. Replace with operator-specific intent when available.",
    )


def build_work_preferences(
    controls: MandateControl,
    *,
    policy: dict[str, Any],
    execution_mode_preference: str | None = None,
    operation_mode_preference: str | None = None,
    preferred_report_style: str = "concise",
    preferred_effort_tier: str | None = None,
    notes: str = "",
) -> WorkPreferences:
    """Create work preferences using resolved policy defaults when needed."""
    autonomy_cfg = dict(policy.get("autonomy", {}))
    compute_cfg = dict(policy.get("compute", {}))
    return WorkPreferences(
        controls=controls,
        execution_mode_preference=execution_mode_preference
        or str(autonomy_cfg.get("execution_mode", "guided")),
        operation_mode_preference=operation_mode_preference
        or str(autonomy_cfg.get("operation_mode", "session")),
        preferred_report_style=preferred_report_style,
        preferred_effort_tier=preferred_effort_tier
        or str(compute_cfg.get("default_effort_tier", "standard")),
        notes=notes,
    )


def build_run_brief(
    controls: MandateControl,
    *,
    policy: dict[str, Any],
    objective: str | None = None,
    target_column: str | None = None,
    deployment_target: str | None = None,
    success_criteria: list[str] | None = None,
    binding_constraints: list[str] | None = None,
    notes: str = "",
) -> RunBrief:
    """Create a run brief from policy defaults and explicit operator intent."""
    optimization_cfg = dict(policy.get("optimization", {}))
    constraints_cfg = dict(policy.get("constraints", {}))
    criteria = list(success_criteria or [])
    if not criteria:
        criteria.append("Produce a reproducible recommendation with inspectable artifacts.")
        if bool(constraints_cfg.get("uncertainty_required", True)):
            criteria.append("Include uncertainty-aware reasoning where the route supports it.")
    return RunBrief(
        controls=controls,
        objective=objective or str(optimization_cfg.get("objective", "best_robust_pareto_front")),
        target_column=target_column,
        deployment_target=deployment_target,
        success_criteria=criteria,
        binding_constraints=list(binding_constraints or []),
        notes=notes,
    )
