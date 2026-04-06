"""Artifact I/O helpers for Slice 11B mission control state."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from relaytic.core.json_utils import write_json

from .models import MissionControlBundle


MISSION_CONTROL_FILENAMES = {
    "mission_control_state": "mission_control_state.json",
    "review_queue_state": "review_queue_state.json",
    "control_center_layout": "control_center_layout.json",
    "mode_overview": "mode_overview.json",
    "capability_manifest": "capability_manifest.json",
    "action_affordances": "action_affordances.json",
    "stage_navigator": "stage_navigator.json",
    "question_starters": "question_starters.json",
    "onboarding_status": "onboarding_status.json",
    "onboarding_chat_session_state": "onboarding_chat_session_state.json",
    "install_experience_report": "install_experience_report.json",
    "launch_manifest": "launch_manifest.json",
    "demo_session_manifest": "demo_session_manifest.json",
    "ui_preferences": "ui_preferences.json",
    "branch_dag": "branch_dag.json",
    "confidence_map": "confidence_map.json",
    "change_attribution_report": "change_attribution_report.json",
    "trace_explorer_state": "trace_explorer_state.json",
    "branch_replay_index": "branch_replay_index.json",
    "approval_timeline": "approval_timeline.json",
    "background_job_view": "background_job_view.json",
    "permission_mode_card": "permission_mode_card.json",
    "release_health_report": "release_health_report.json",
    "demo_pack_manifest": "demo_pack_manifest.json",
    "flagship_demo_scorecard": "flagship_demo_scorecard.json",
    "human_factors_eval_report": "human_factors_eval_report.json",
    "onboarding_success_report": "onboarding_success_report.json",
}
MISSION_CONTROL_REPORT_RELATIVE_PATH = Path("reports") / "mission_control.html"


def write_mission_control_bundle(
    run_dir: str | Path,
    *,
    bundle: MissionControlBundle,
    html_report: str,
) -> dict[str, Path]:
    root = Path(run_dir)
    root.mkdir(parents=True, exist_ok=True)
    payload = bundle.to_dict()
    written = {
        key: write_json(
            root / filename,
            payload[key],
            indent=2,
            ensure_ascii=False,
            sort_keys=True,
        )
        for key, filename in MISSION_CONTROL_FILENAMES.items()
    }
    html_path = root / MISSION_CONTROL_REPORT_RELATIVE_PATH
    html_path.parent.mkdir(parents=True, exist_ok=True)
    html_path.write_text(html_report, encoding="utf-8")
    written["mission_control_report"] = html_path
    return written


def write_mission_control_artifact(run_dir: str | Path, *, key: str, payload: dict[str, Any]) -> Path:
    if key not in MISSION_CONTROL_FILENAMES:
        raise ValueError(f"Unsupported mission-control artifact '{key}'.")
    root = Path(run_dir)
    root.mkdir(parents=True, exist_ok=True)
    return write_json(
        root / MISSION_CONTROL_FILENAMES[key],
        payload,
        indent=2,
        ensure_ascii=False,
        sort_keys=True,
    )


def read_mission_control_bundle(run_dir: str | Path) -> dict[str, Any]:
    root = Path(run_dir)
    payload: dict[str, Any] = {}
    for key, filename in MISSION_CONTROL_FILENAMES.items():
        path = root / filename
        if not path.exists():
            continue
        try:
            artifact = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if isinstance(artifact, dict):
            payload[key] = artifact
    report_path = root / MISSION_CONTROL_REPORT_RELATIVE_PATH
    if report_path.exists():
        payload["mission_control_report_path"] = str(report_path)
    return payload
