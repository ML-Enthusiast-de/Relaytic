"""Typed artifact models for Slice 13B permission-mode surfaces."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


PERMISSION_CONTROLS_SCHEMA_VERSION = "relaytic.permission_controls.v1"
PERMISSION_MODE_SCHEMA_VERSION = "relaytic.permission_mode.v1"
TOOL_PERMISSION_MATRIX_SCHEMA_VERSION = "relaytic.tool_permission_matrix.v1"
APPROVAL_POLICY_REPORT_SCHEMA_VERSION = "relaytic.approval_policy_report.v1"
SESSION_CAPABILITY_CONTRACT_SCHEMA_VERSION = "relaytic.session_capability_contract.v1"
PERMISSION_DECISION_LOG_SCHEMA_VERSION = "relaytic.permission_decision.v1"


@dataclass(frozen=True)
class PermissionControls:
    schema_version: str = PERMISSION_CONTROLS_SCHEMA_VERSION
    enabled: bool = True
    default_mode: str = "bounded_autonomy"
    require_review_for_high_impact_actions: bool = True
    allow_remote_actions: bool = False
    max_recent_decisions: int = 40

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class PermissionTrace:
    agent: str
    mode_source: str
    authority_model: str
    advisory_notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class PermissionModeArtifact:
    schema_version: str
    generated_at: str
    controls: PermissionControls
    status: str
    current_mode: str
    mode_source: str
    pending_approval_count: int
    pending_request_ids: list[str]
    review_reason: str | None
    summary: str
    trace: PermissionTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class ToolPermissionMatrixArtifact:
    schema_version: str
    generated_at: str
    controls: PermissionControls
    status: str
    current_mode: str
    tool_count: int
    tools: list[dict[str, Any]]
    summary: str
    trace: PermissionTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class ApprovalPolicyReportArtifact:
    schema_version: str
    generated_at: str
    controls: PermissionControls
    status: str
    current_mode: str
    pending_approval_count: int
    approval_requested_count: int
    denied_count: int
    recent_decisions: list[dict[str, Any]]
    pending_approvals: list[dict[str, Any]]
    summary: str
    trace: PermissionTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class SessionCapabilityContractArtifact:
    schema_version: str
    generated_at: str
    controls: PermissionControls
    status: str
    current_mode: str
    active_specialist_count: int
    allowed_action_count: int
    approval_gated_action_count: int
    blocked_action_count: int
    actions_by_status: dict[str, list[str]]
    paths: dict[str, str]
    summary: str
    trace: PermissionTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class PermissionBundle:
    permission_mode: PermissionModeArtifact
    tool_permission_matrix: ToolPermissionMatrixArtifact
    approval_policy_report: ApprovalPolicyReportArtifact
    session_capability_contract: SessionCapabilityContractArtifact

    def to_dict(self) -> dict[str, Any]:
        return {
            "permission_mode": self.permission_mode.to_dict(),
            "tool_permission_matrix": self.tool_permission_matrix.to_dict(),
            "approval_policy_report": self.approval_policy_report.to_dict(),
            "session_capability_contract": self.session_capability_contract.to_dict(),
        }
