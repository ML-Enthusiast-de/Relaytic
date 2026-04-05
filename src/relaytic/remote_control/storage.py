"""Artifact I/O helpers for Slice 14A remote supervision."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from relaytic.core.json_utils import write_json

from .models import RemoteControlBundle


REMOTE_CONTROL_FILENAMES = {
    "remote_session_manifest": "remote_session_manifest.json",
    "remote_transport_report": "remote_transport_report.json",
    "approval_request_queue": "approval_request_queue.json",
    "remote_operator_presence": "remote_operator_presence.json",
    "supervision_handoff": "supervision_handoff.json",
    "notification_delivery_report": "notification_delivery_report.json",
    "remote_control_audit": "remote_control_audit.json",
}

APPROVAL_DECISION_LOG_FILENAME = "approval_decision_log.jsonl"


def write_remote_control_bundle(run_dir: str | Path, *, bundle: RemoteControlBundle) -> dict[str, Path]:
    root = Path(run_dir)
    root.mkdir(parents=True, exist_ok=True)
    payload = bundle.to_dict()
    return {
        key: write_json(root / filename, payload[key], indent=2, ensure_ascii=False, sort_keys=True)
        for key, filename in REMOTE_CONTROL_FILENAMES.items()
    }


def write_remote_control_artifact(run_dir: str | Path, *, key: str, payload: dict[str, Any]) -> Path:
    root = Path(run_dir)
    root.mkdir(parents=True, exist_ok=True)
    filename = REMOTE_CONTROL_FILENAMES[key]
    return write_json(root / filename, payload, indent=2, ensure_ascii=False, sort_keys=True)


def read_remote_control_bundle(run_dir: str | Path) -> dict[str, Any]:
    root = Path(run_dir)
    payload: dict[str, Any] = {}
    for key, filename in REMOTE_CONTROL_FILENAMES.items():
        path = root / filename
        if not path.exists():
            continue
        try:
            loaded = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if isinstance(loaded, dict):
            payload[key] = loaded
    return payload


def append_approval_decision_log(run_dir: str | Path, *, entry: dict[str, Any]) -> Path:
    root = Path(run_dir)
    root.mkdir(parents=True, exist_ok=True)
    path = root / APPROVAL_DECISION_LOG_FILENAME
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(entry, ensure_ascii=False, sort_keys=True))
        handle.write("\n")
    return path


def read_approval_decision_log(run_dir: str | Path, *, limit: int | None = None) -> list[dict[str, Any]]:
    path = Path(run_dir) / APPROVAL_DECISION_LOG_FILENAME
    if not path.exists():
        return []
    entries: list[dict[str, Any]] = []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return []
    for line in lines:
        text = line.strip()
        if not text:
            continue
        try:
            loaded = json.loads(text)
        except json.JSONDecodeError:
            continue
        if isinstance(loaded, dict):
            entries.append(loaded)
    if limit is not None and limit >= 0:
        return entries[-limit:]
    return entries
