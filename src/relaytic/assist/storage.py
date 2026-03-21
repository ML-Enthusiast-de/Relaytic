"""Artifact I/O helpers for Slice 09E assist artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from relaytic.core.json_utils import dumps_json, write_json

from .models import AssistBundle


ASSIST_FILENAMES = {
    "assist_mode": "assist_mode.json",
    "assist_session_state": "assist_session_state.json",
    "assistant_connection_guide": "assistant_connection_guide.json",
    "assist_turn_log": "assist_turn_log.jsonl",
}


def write_assist_bundle(run_dir: str | Path, *, bundle: AssistBundle) -> dict[str, Path]:
    root = Path(run_dir)
    root.mkdir(parents=True, exist_ok=True)
    payload = bundle.to_dict()
    return {
        key: write_json(
            root / filename,
            payload[key],
            indent=2,
            ensure_ascii=False,
            sort_keys=True,
        )
        for key, filename in ASSIST_FILENAMES.items()
        if key != "assist_turn_log"
    }


def read_assist_bundle(run_dir: str | Path) -> dict[str, Any]:
    root = Path(run_dir)
    payload: dict[str, Any] = {}
    for key, filename in ASSIST_FILENAMES.items():
        if key == "assist_turn_log":
            continue
        path = root / filename
        if not path.exists():
            continue
        payload[key] = json.loads(path.read_text(encoding="utf-8"))
    return payload


def append_assist_turn_log(run_dir: str | Path, *, entry: dict[str, Any]) -> Path:
    root = Path(run_dir)
    root.mkdir(parents=True, exist_ok=True)
    path = root / ASSIST_FILENAMES["assist_turn_log"]
    with path.open("a", encoding="utf-8") as handle:
        handle.write(dumps_json(entry, ensure_ascii=False))
        handle.write("\n")
    return path
