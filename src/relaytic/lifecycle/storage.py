"""Artifact I/O helpers for Slice 08 lifecycle artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from relaytic.core.json_utils import write_json

from .models import LifecycleBundle


LIFECYCLE_FILENAMES = {
    "champion_vs_candidate": "champion_vs_candidate.json",
    "recalibration_decision": "recalibration_decision.json",
    "retrain_decision": "retrain_decision.json",
    "promotion_decision": "promotion_decision.json",
    "rollback_decision": "rollback_decision.json",
}


def write_lifecycle_bundle(run_dir: str | Path, *, bundle: LifecycleBundle) -> dict[str, Path]:
    """Write all Slice 08 lifecycle artifacts for a run."""
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
        for key, filename in LIFECYCLE_FILENAMES.items()
    }


def read_lifecycle_bundle(run_dir: str | Path) -> dict[str, Any]:
    """Read lifecycle artifacts into plain dictionaries."""
    root = Path(run_dir)
    payload: dict[str, Any] = {}
    for key, filename in LIFECYCLE_FILENAMES.items():
        path = root / filename
        if not path.exists():
            continue
        payload[key] = json.loads(path.read_text(encoding="utf-8"))
    return payload
