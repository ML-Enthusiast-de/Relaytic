"""Artifact I/O helpers for Slice 13B permission state."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from relaytic.core.json_utils import dumps_json, write_json

from .models import PermissionBundle


PERMISSION_FILENAMES = {
    "permission_mode": "permission_mode.json",
    "tool_permission_matrix": "tool_permission_matrix.json",
    "approval_policy_report": "approval_policy_report.json",
    "session_capability_contract": "session_capability_contract.json",
}
PERMISSION_DECISION_LOG_FILENAME = "permission_decision_log.jsonl"


def write_permission_bundle(run_dir: str | Path, *, bundle: PermissionBundle) -> dict[str, Path]:
    root = Path(run_dir)
    root.mkdir(parents=True, exist_ok=True)
    payload = bundle.to_dict()
    return {
        key: write_json(root / filename, payload[key], indent=2, ensure_ascii=False, sort_keys=True)
        for key, filename in PERMISSION_FILENAMES.items()
    }


def read_permission_bundle(run_dir: str | Path) -> dict[str, Any]:
    root = Path(run_dir)
    payload: dict[str, Any] = {}
    for key, filename in PERMISSION_FILENAMES.items():
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


def append_permission_decision(run_dir: str | Path, *, entry: dict[str, Any]) -> Path:
    root = Path(run_dir)
    root.mkdir(parents=True, exist_ok=True)
    path = root / PERMISSION_DECISION_LOG_FILENAME
    with path.open("a", encoding="utf-8") as handle:
        handle.write(dumps_json(entry, ensure_ascii=False))
        handle.write("\n")
    return path


def read_permission_decision_log(run_dir: str | Path, *, limit: int | None = None) -> list[dict[str, Any]]:
    root = Path(run_dir)
    path = root / PERMISSION_DECISION_LOG_FILENAME
    if not path.exists():
        return []
    entries: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            text = line.strip()
            if not text:
                continue
            try:
                loaded = json.loads(text)
            except json.JSONDecodeError:
                continue
            if isinstance(loaded, dict):
                entries.append(loaded)
    return entries[-limit:] if limit is not None and limit >= 0 else entries
