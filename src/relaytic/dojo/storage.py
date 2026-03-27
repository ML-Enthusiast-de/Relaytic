"""Artifact I/O helpers for Slice 12 dojo artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from relaytic.core.json_utils import write_json

from .models import DojoBundle


DOJO_FILENAMES = {
    "dojo_session": "dojo_session.json",
    "dojo_hypotheses": "dojo_hypotheses.json",
    "dojo_results": "dojo_results.json",
    "dojo_promotions": "dojo_promotions.json",
    "architecture_proposals": "architecture_proposals.json",
}


def write_dojo_bundle(run_dir: str | Path, *, bundle: DojoBundle) -> dict[str, Path]:
    root = Path(run_dir)
    root.mkdir(parents=True, exist_ok=True)
    payload = bundle.to_dict()
    return {
        key: write_json(root / filename, payload[key], indent=2, ensure_ascii=False, sort_keys=True)
        for key, filename in DOJO_FILENAMES.items()
    }


def read_dojo_bundle(run_dir: str | Path) -> dict[str, Any]:
    root = Path(run_dir)
    payload: dict[str, Any] = {}
    for key, filename in DOJO_FILENAMES.items():
        path = root / filename
        if not path.exists():
            continue
        try:
            payload[key] = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
    return payload
