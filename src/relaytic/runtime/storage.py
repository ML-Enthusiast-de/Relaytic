"""Artifact I/O helpers for Slice 09B runtime outputs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from relaytic.core.json_utils import dumps_json, write_json


RUNTIME_FILENAMES = {
    "hook_execution_log": "hook_execution_log.json",
    "run_checkpoint_manifest": "run_checkpoint_manifest.json",
    "capability_profiles": "capability_profiles.json",
    "data_access_audit": "data_access_audit.json",
    "context_influence_report": "context_influence_report.json",
}
EVENT_STREAM_FILENAME = "lab_event_stream.jsonl"


def write_runtime_artifact(run_dir: str | Path, *, key: str, payload: dict[str, Any]) -> Path:
    """Write one runtime JSON artifact."""
    root = Path(run_dir)
    root.mkdir(parents=True, exist_ok=True)
    filename = RUNTIME_FILENAMES[key]
    return write_json(root / filename, payload, indent=2, ensure_ascii=False, sort_keys=True)


def read_runtime_bundle(run_dir: str | Path) -> dict[str, Any]:
    """Read runtime JSON artifacts and recent events into plain dictionaries."""
    root = Path(run_dir)
    payload: dict[str, Any] = {}
    for key, filename in RUNTIME_FILENAMES.items():
        path = root / filename
        if not path.exists():
            continue
        payload[key] = json.loads(path.read_text(encoding="utf-8"))
    events = read_event_stream(root)
    if events:
        payload["lab_event_stream"] = events
    return payload


def append_event(run_dir: str | Path, *, event: dict[str, Any]) -> Path:
    """Append one JSONL runtime event."""
    root = Path(run_dir)
    root.mkdir(parents=True, exist_ok=True)
    path = root / EVENT_STREAM_FILENAME
    with path.open("a", encoding="utf-8") as handle:
        handle.write(dumps_json(event, ensure_ascii=False))
        handle.write("\n")
    return path


def read_event_stream(run_dir: str | Path, *, limit: int | None = None) -> list[dict[str, Any]]:
    """Read the append-only runtime event stream."""
    root = Path(run_dir)
    path = root / EVENT_STREAM_FILENAME
    if not path.exists():
        return []
    events: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            text = line.strip()
            if not text:
                continue
            try:
                events.append(json.loads(text))
            except json.JSONDecodeError:
                continue
    if limit is not None and limit >= 0:
        return events[-limit:]
    return events
