"""Artifact I/O helpers for Slice 13A release-safety state."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from relaytic.core.json_utils import write_json

from .models import ReleaseSafetyBundle


RELEASE_SAFETY_FILENAMES = {
    "release_safety_scan": "release_safety_scan.json",
    "distribution_manifest": "distribution_manifest.json",
    "artifact_inventory": "artifact_inventory.json",
    "artifact_attestation": "artifact_attestation.json",
    "source_map_audit": "source_map_audit.json",
    "sensitive_string_audit": "sensitive_string_audit.json",
    "release_bundle_report": "release_bundle_report.json",
    "packaging_regression_report": "packaging_regression_report.json",
}


def write_release_safety_bundle(state_dir: str | Path, *, bundle: ReleaseSafetyBundle) -> dict[str, Path]:
    root = Path(state_dir)
    root.mkdir(parents=True, exist_ok=True)
    payload = bundle.to_dict()
    return {
        key: write_json(root / filename, payload[key], indent=2, ensure_ascii=False, sort_keys=True)
        for key, filename in RELEASE_SAFETY_FILENAMES.items()
    }


def read_release_safety_bundle(state_dir: str | Path) -> dict[str, Any]:
    root = Path(state_dir)
    payload: dict[str, Any] = {}
    for key, filename in RELEASE_SAFETY_FILENAMES.items():
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
