"""Typed artifact models for Slice 13B event-bus surfaces."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


EVENT_BUS_CONTROLS_SCHEMA_VERSION = "relaytic.event_bus_controls.v1"
EVENT_SCHEMA_SCHEMA_VERSION = "relaytic.event_schema.v1"
EVENT_SUBSCRIPTION_REGISTRY_SCHEMA_VERSION = "relaytic.event_subscription_registry.v1"
HOOK_REGISTRY_SCHEMA_VERSION = "relaytic.hook_registry.v1"
HOOK_DISPATCH_REPORT_SCHEMA_VERSION = "relaytic.hook_dispatch_report.v1"


@dataclass(frozen=True)
class EventBusControls:
    schema_version: str = EVENT_BUS_CONTROLS_SCHEMA_VERSION
    enabled: bool = True
    max_recent_dispatches: int = 60
    project_dispatches_without_live_subscribers: bool = True
    read_only_subscribers_only: bool = True

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class EventBusTrace:
    agent: str
    event_source: str
    dispatch_mode: str
    advisory_notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class EventSchemaArtifact:
    schema_version: str
    generated_at: str
    controls: EventBusControls
    status: str
    event_type_count: int
    field_names: list[str]
    event_types: list[dict[str, Any]]
    summary: str
    trace: EventBusTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class EventSubscriptionRegistryArtifact:
    schema_version: str
    generated_at: str
    controls: EventBusControls
    status: str
    subscription_count: int
    subscriptions: list[dict[str, Any]]
    summary: str
    trace: EventBusTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class HookRegistryArtifact:
    schema_version: str
    generated_at: str
    controls: EventBusControls
    status: str
    hook_count: int
    hooks: list[dict[str, Any]]
    summary: str
    trace: EventBusTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class HookDispatchReportArtifact:
    schema_version: str
    generated_at: str
    controls: EventBusControls
    status: str
    observed_event_count: int
    subscriber_count: int
    dispatch_count: int
    recent_dispatches: list[dict[str, Any]]
    source_of_truth_preserved: bool
    summary: str
    trace: EventBusTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class EventBusBundle:
    event_schema: EventSchemaArtifact
    event_subscription_registry: EventSubscriptionRegistryArtifact
    hook_registry: HookRegistryArtifact
    hook_dispatch_report: HookDispatchReportArtifact

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_schema": self.event_schema.to_dict(),
            "event_subscription_registry": self.event_subscription_registry.to_dict(),
            "hook_registry": self.hook_registry.to_dict(),
            "hook_dispatch_report": self.hook_dispatch_report.to_dict(),
        }
