"""Artifact I/O helpers for mandate foundation artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from relaytic.core.json_utils import write_json

from .models import LabMandate, RunBrief, WorkPreferences


MANDATE_FILENAMES = {
    "lab_mandate": "lab_mandate.json",
    "work_preferences": "work_preferences.json",
    "run_brief": "run_brief.json",
}


def write_mandate_bundle(
    run_dir: str | Path,
    *,
    lab_mandate: LabMandate,
    work_preferences: WorkPreferences,
    run_brief: RunBrief,
) -> dict[str, Path]:
    """Write all mandate-layer artifacts for a run."""
    root = Path(run_dir)
    root.mkdir(parents=True, exist_ok=True)
    paths = {
        "lab_mandate": write_json(root / MANDATE_FILENAMES["lab_mandate"], lab_mandate.to_dict(), indent=2, ensure_ascii=False, sort_keys=True),
        "work_preferences": write_json(root / MANDATE_FILENAMES["work_preferences"], work_preferences.to_dict(), indent=2, ensure_ascii=False, sort_keys=True),
        "run_brief": write_json(root / MANDATE_FILENAMES["run_brief"], run_brief.to_dict(), indent=2, ensure_ascii=False, sort_keys=True),
    }
    return paths


def read_mandate_bundle(run_dir: str | Path) -> dict[str, Any]:
    """Read mandate artifacts into plain dictionaries."""
    root = Path(run_dir)
    payload: dict[str, Any] = {}
    for key, filename in MANDATE_FILENAMES.items():
        path = root / filename
        payload[key] = json.loads(path.read_text(encoding="utf-8"))
    return payload
