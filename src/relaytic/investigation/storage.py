"""Artifact I/O helpers for Slice 03 investigation artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from relaytic.core.json_utils import write_json

from .models import InvestigationBundle


INVESTIGATION_FILENAMES = {
    "dataset_profile": "dataset_profile.json",
    "domain_memo": "domain_memo.json",
    "objective_hypotheses": "objective_hypotheses.json",
    "focus_debate": "focus_debate.json",
    "focus_profile": "focus_profile.json",
    "optimization_profile": "optimization_profile.json",
    "feature_strategy_profile": "feature_strategy_profile.json",
}


def write_investigation_bundle(
    run_dir: str | Path,
    *,
    bundle: InvestigationBundle,
) -> dict[str, Path]:
    """Write all Slice 03 artifacts for a run."""
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
        for key, filename in INVESTIGATION_FILENAMES.items()
    }


def read_investigation_bundle(run_dir: str | Path) -> dict[str, Any]:
    """Read investigation artifacts into plain dictionaries."""
    root = Path(run_dir)
    payload: dict[str, Any] = {}
    for key, filename in INVESTIGATION_FILENAMES.items():
        path = root / filename
        payload[key] = json.loads(path.read_text(encoding="utf-8"))
    return payload
