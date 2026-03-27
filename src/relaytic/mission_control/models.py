"""Typed artifact models for Slice 11B mission control and onboarding."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


MISSION_CONTROL_CONTROLS_SCHEMA_VERSION = "relaytic.mission_control_controls.v1"
MISSION_CONTROL_STATE_SCHEMA_VERSION = "relaytic.mission_control_state.v1"
REVIEW_QUEUE_STATE_SCHEMA_VERSION = "relaytic.review_queue_state.v1"
CONTROL_CENTER_LAYOUT_SCHEMA_VERSION = "relaytic.control_center_layout.v1"
ONBOARDING_STATUS_SCHEMA_VERSION = "relaytic.onboarding_status.v1"
INSTALL_EXPERIENCE_REPORT_SCHEMA_VERSION = "relaytic.install_experience_report.v1"
LAUNCH_MANIFEST_SCHEMA_VERSION = "relaytic.launch_manifest.v1"
DEMO_SESSION_MANIFEST_SCHEMA_VERSION = "relaytic.demo_session_manifest.v1"
UI_PREFERENCES_SCHEMA_VERSION = "relaytic.ui_preferences.v1"


@dataclass(frozen=True)
class MissionControlControls:
    schema_version: str = MISSION_CONTROL_CONTROLS_SCHEMA_VERSION
    enabled: bool = True
    allow_onboarding_without_run: bool = True
    allow_browser_launch: bool = True
    prefer_static_html: bool = True
    require_shared_truth: bool = True
    expose_agent_surface: bool = True
    default_expected_profile: str = "full"
    default_theme: str = "signal"
    auto_open_browser: bool = True

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class MissionControlTrace:
    agent: str
    operating_mode: str
    llm_used: bool
    llm_status: str
    deterministic_evidence: list[str] = field(default_factory=list)
    advisory_notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class MissionControlState:
    schema_version: str
    generated_at: str
    controls: MissionControlControls
    status: str
    state_dir: str
    run_dir: str | None
    headline: str
    current_stage: str | None
    recommended_action: str | None
    review_required: bool
    card_count: int
    review_queue_pending_count: int
    cards: list[dict[str, Any]]
    summary: str
    trace: MissionControlTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class ReviewQueueState:
    schema_version: str
    generated_at: str
    controls: MissionControlControls
    status: str
    pending_count: int
    blocking_count: int
    items: list[dict[str, Any]]
    summary: str
    trace: MissionControlTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class ControlCenterLayout:
    schema_version: str
    generated_at: str
    controls: MissionControlControls
    status: str
    layout_name: str
    default_focus_panel: str
    panels: list[dict[str, Any]]
    summary: str
    trace: MissionControlTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class OnboardingStatus:
    schema_version: str
    generated_at: str
    controls: MissionControlControls
    status: str
    expected_profile: str
    install_verified: bool
    launch_ready: bool
    package_installed: bool
    doctor_status: str
    host_summary: dict[str, Any]
    recommended_commands: list[str]
    summary: str
    trace: MissionControlTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class InstallExperienceReport:
    schema_version: str
    generated_at: str
    controls: MissionControlControls
    status: str
    expected_profile: str
    install_mode: str
    install_command: str
    doctor_command: str
    launch_command: str
    doctor_status: str
    package_installed: bool
    next_steps: list[str]
    summary: str
    trace: MissionControlTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class LaunchManifest:
    schema_version: str
    generated_at: str
    controls: MissionControlControls
    status: str
    launch_mode: str
    state_dir: str
    run_dir: str | None
    html_report_path: str
    browser_requested: bool
    browser_opened: bool
    openable_url: str | None
    exported_paths: dict[str, str]
    summary: str
    trace: MissionControlTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class DemoSessionManifest:
    schema_version: str
    generated_at: str
    controls: MissionControlControls
    status: str
    demo_ready: bool
    scenario: str
    highlight_cards: list[dict[str, Any]]
    incumbent_visible: bool
    review_queue_pending_count: int
    summary: str
    trace: MissionControlTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class UIPreferences:
    schema_version: str
    generated_at: str
    controls: MissionControlControls
    status: str
    theme: str
    density: str
    default_panels: list[str]
    auto_open_browser: bool
    summary: str
    trace: MissionControlTrace

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["controls"] = self.controls.to_dict()
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class MissionControlBundle:
    mission_control_state: MissionControlState
    review_queue_state: ReviewQueueState
    control_center_layout: ControlCenterLayout
    onboarding_status: OnboardingStatus
    install_experience_report: InstallExperienceReport
    launch_manifest: LaunchManifest
    demo_session_manifest: DemoSessionManifest
    ui_preferences: UIPreferences

    def to_dict(self) -> dict[str, Any]:
        return {
            "mission_control_state": self.mission_control_state.to_dict(),
            "review_queue_state": self.review_queue_state.to_dict(),
            "control_center_layout": self.control_center_layout.to_dict(),
            "onboarding_status": self.onboarding_status.to_dict(),
            "install_experience_report": self.install_experience_report.to_dict(),
            "launch_manifest": self.launch_manifest.to_dict(),
            "demo_session_manifest": self.demo_session_manifest.to_dict(),
            "ui_preferences": self.ui_preferences.to_dict(),
        }


def build_mission_control_controls_from_policy(policy: dict[str, Any]) -> MissionControlControls:
    cfg = dict(policy.get("mission_control", {}))
    default_profile = str(cfg.get("default_expected_profile", "full") or "full").strip().lower() or "full"
    if default_profile not in {"core", "full"}:
        default_profile = "full"
    default_theme = str(cfg.get("default_theme", "signal") or "signal").strip() or "signal"
    return MissionControlControls(
        enabled=bool(cfg.get("enabled", True)),
        allow_onboarding_without_run=bool(cfg.get("allow_onboarding_without_run", True)),
        allow_browser_launch=bool(cfg.get("allow_browser_launch", True)),
        prefer_static_html=bool(cfg.get("prefer_static_html", True)),
        require_shared_truth=bool(cfg.get("require_shared_truth", True)),
        expose_agent_surface=bool(cfg.get("expose_agent_surface", True)),
        default_expected_profile=default_profile,
        default_theme=default_theme,
        auto_open_browser=bool(cfg.get("auto_open_browser", True)),
    )
