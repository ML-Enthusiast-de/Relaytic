"""Typed artifact models for Slice 09E communicative assist surfaces."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


ASSIST_CONTROLS_SCHEMA_VERSION = "relaytic.assist_controls.v1"
ASSIST_MODE_SCHEMA_VERSION = "relaytic.assist_mode.v1"
ASSIST_SESSION_STATE_SCHEMA_VERSION = "relaytic.assist_session_state.v1"
ASSISTANT_CONNECTION_GUIDE_SCHEMA_VERSION = "relaytic.assistant_connection_guide.v1"


@dataclass(frozen=True)
class AssistControls:
    schema_version: str = ASSIST_CONTROLS_SCHEMA_VERSION
    enabled: bool = True
    allow_interactive_assist: bool = True
    allow_stage_navigation: bool = True
    allow_assistant_takeover: bool = True
    prefer_local_semantic_assist: bool = True
    allow_host_connection_guidance: bool = True
    max_turn_history: int = 20

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class AssistTrace:
    agent: str
    operating_mode: str
    llm_used: bool
    llm_status: str
    deterministic_evidence: list[str] = field(default_factory=list)
    advisory_notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class AssistModeArtifact:
    schema_version: str
    generated_at: str
    controls: AssistControls
    enabled: bool
    semantic_backend_status: str
    semantic_backend_provider: str | None
    semantic_backend_model: str | None
    takeover_enabled: bool
    host_guidance_available: bool
    summary: str
    trace: AssistTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class AssistSessionStateArtifact:
    schema_version: str
    generated_at: str
    controls: AssistControls
    current_stage: str
    next_recommended_action: str | None
    takeover_available: bool
    last_user_intent: str | None
    last_requested_stage: str | None
    last_action_kind: str | None
    turn_count: int
    summary: str
    trace: AssistTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class AssistantConnectionGuideArtifact:
    schema_version: str
    generated_at: str
    controls: AssistControls
    local_options: list[dict[str, Any]]
    host_options: list[dict[str, Any]]
    recommended_path: str
    summary: str
    trace: AssistTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class AssistBundle:
    assist_mode: AssistModeArtifact
    assist_session_state: AssistSessionStateArtifact
    assistant_connection_guide: AssistantConnectionGuideArtifact

    def to_dict(self) -> dict[str, Any]:
        return {
            "assist_mode": self.assist_mode.to_dict(),
            "assist_session_state": self.assist_session_state.to_dict(),
            "assistant_connection_guide": self.assistant_connection_guide.to_dict(),
        }


def build_assist_controls_from_policy(policy: dict[str, Any]) -> AssistControls:
    cfg = dict(policy.get("communication", {}))
    try:
        max_turn_history = int(cfg.get("max_turn_history", 20) or 20)
    except (TypeError, ValueError):
        max_turn_history = 20
    return AssistControls(
        enabled=bool(cfg.get("enabled", True)),
        allow_interactive_assist=bool(cfg.get("allow_interactive_assist", True)),
        allow_stage_navigation=bool(cfg.get("allow_stage_navigation", True)),
        allow_assistant_takeover=bool(cfg.get("allow_assistant_takeover", True)),
        prefer_local_semantic_assist=bool(cfg.get("prefer_local_semantic_assist", True)),
        allow_host_connection_guidance=bool(cfg.get("allow_host_connection_guidance", True)),
        max_turn_history=max(4, min(40, max_turn_history)),
    )
