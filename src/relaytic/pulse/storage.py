"""Artifact I/O helpers for Slice 12A pulse artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from relaytic.core.json_utils import write_json

from .models import PulseBundle


PULSE_FILENAMES = {
    "pulse_schedule": "pulse_schedule.json",
    "pulse_run_report": "pulse_run_report.json",
    "pulse_skip_report": "pulse_skip_report.json",
    "pulse_recommendations": "pulse_recommendations.json",
    "innovation_watch_report": "innovation_watch_report.json",
    "challenge_watchlist": "challenge_watchlist.json",
    "pulse_checkpoint": "pulse_checkpoint.json",
    "memory_compaction_plan": "memory_compaction_plan.json",
    "memory_compaction_report": "memory_compaction_report.json",
    "memory_pinning_index": "memory_pinning_index.json",
}


def write_pulse_bundle(run_dir: str | Path, *, bundle: PulseBundle) -> dict[str, Path]:
    root = Path(run_dir)
    root.mkdir(parents=True, exist_ok=True)
    payload = bundle.to_dict()
    return {
        key: write_json(root / filename, payload[key], indent=2, ensure_ascii=False, sort_keys=True)
        for key, filename in PULSE_FILENAMES.items()
    }


def read_pulse_bundle(run_dir: str | Path) -> dict[str, Any]:
    root = Path(run_dir)
    payload: dict[str, Any] = {}
    for key, filename in PULSE_FILENAMES.items():
        path = root / filename
        if not path.exists():
            continue
        try:
            payload[key] = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
    return payload
