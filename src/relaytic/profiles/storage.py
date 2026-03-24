"""Artifact I/O helpers for Slice 10B profile and contract artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from relaytic.core.json_utils import write_json

from .models import ProfilesBundle


PROFILES_FILENAMES = {
    "quality_contract": "quality_contract.json",
    "quality_gate_report": "quality_gate_report.json",
    "budget_contract": "budget_contract.json",
    "budget_consumption_report": "budget_consumption_report.json",
    "operator_profile": "operator_profile.json",
    "lab_operating_profile": "lab_operating_profile.json",
}


def write_profiles_bundle(run_dir: str | Path, *, bundle: ProfilesBundle) -> dict[str, Path]:
    root = Path(run_dir)
    root.mkdir(parents=True, exist_ok=True)
    payload = bundle.to_dict()
    return {
        key: write_json(root / filename, payload[key], indent=2, ensure_ascii=False, sort_keys=True)
        for key, filename in PROFILES_FILENAMES.items()
    }


def read_profiles_bundle(run_dir: str | Path) -> dict[str, Any]:
    root = Path(run_dir)
    payload: dict[str, Any] = {}
    for key, filename in PROFILES_FILENAMES.items():
        path = root / filename
        if not path.exists():
            continue
        try:
            payload[key] = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
    return payload
