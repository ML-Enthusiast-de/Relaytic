"""Artifact I/O helpers for Slice 13C daemon state."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from relaytic.core.json_utils import write_json

from .models import BACKGROUND_JOB_LOG_SCHEMA_VERSION, DaemonBundle


DAEMON_FILENAMES = {
    "daemon_state": "daemon_state.json",
    "background_job_registry": "background_job_registry.json",
    "background_checkpoint": "background_checkpoint.json",
    "resume_session_manifest": "resume_session_manifest.json",
    "background_approval_queue": "background_approval_queue.json",
    "memory_maintenance_queue": "memory_maintenance_queue.json",
    "memory_maintenance_report": "memory_maintenance_report.json",
    "search_resume_plan": "search_resume_plan.json",
    "stale_job_report": "stale_job_report.json",
}
BACKGROUND_JOB_LOG_FILENAME = "background_job_log.jsonl"


def write_daemon_bundle(run_dir: str | Path, *, bundle: DaemonBundle) -> dict[str, Path]:
    root = Path(run_dir)
    root.mkdir(parents=True, exist_ok=True)
    payload = bundle.to_dict()
    return {
        key: write_json(root / filename, payload[key], indent=2, ensure_ascii=False, sort_keys=True)
        for key, filename in DAEMON_FILENAMES.items()
    }


def read_daemon_bundle(run_dir: str | Path) -> dict[str, Any]:
    root = Path(run_dir)
    payload: dict[str, Any] = {}
    for key, filename in DAEMON_FILENAMES.items():
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


def append_background_job_log(run_dir: str | Path, *, entry: dict[str, Any]) -> Path:
    root = Path(run_dir)
    root.mkdir(parents=True, exist_ok=True)
    payload = dict(entry)
    payload.setdefault("schema_version", BACKGROUND_JOB_LOG_SCHEMA_VERSION)
    path = root / BACKGROUND_JOB_LOG_FILENAME
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False, sort_keys=True))
        handle.write("\n")
    return path


def read_background_job_log(run_dir: str | Path, *, limit: int | None = None) -> list[dict[str, Any]]:
    path = Path(run_dir) / BACKGROUND_JOB_LOG_FILENAME
    if not path.exists():
        return []
    entries: list[dict[str, Any]] = []
    try:
        for raw_line in path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line:
                continue
            try:
                loaded = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(loaded, dict):
                entries.append(loaded)
    except OSError:
        return []
    if limit is not None and limit >= 0:
        return entries[-limit:]
    return entries
