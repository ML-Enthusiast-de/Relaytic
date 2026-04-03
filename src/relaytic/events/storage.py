"""Artifact I/O helpers for Slice 13B event-bus state."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from relaytic.core.json_utils import write_json

from .models import EventBusBundle


EVENT_BUS_FILENAMES = {
    "event_schema": "event_schema.json",
    "event_subscription_registry": "event_subscription_registry.json",
    "hook_registry": "hook_registry.json",
    "hook_dispatch_report": "hook_dispatch_report.json",
}


def write_event_bus_bundle(run_dir: str | Path, *, bundle: EventBusBundle) -> dict[str, Path]:
    root = Path(run_dir)
    root.mkdir(parents=True, exist_ok=True)
    payload = bundle.to_dict()
    return {
        key: write_json(root / filename, payload[key], indent=2, ensure_ascii=False, sort_keys=True)
        for key, filename in EVENT_BUS_FILENAMES.items()
    }


def read_event_bus_bundle(run_dir: str | Path) -> dict[str, Any]:
    root = Path(run_dir)
    payload: dict[str, Any] = {}
    for key, filename in EVENT_BUS_FILENAMES.items():
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
