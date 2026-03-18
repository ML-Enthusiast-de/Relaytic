"""Artifact I/O helpers for Slice 05 planning artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from relaytic.core.json_utils import write_json

from .models import PlanningBundle


PLANNING_FILENAMES = {
    "plan": "plan.json",
    "alternatives": "alternatives.json",
    "hypotheses": "hypotheses.json",
    "experiment_priority_report": "experiment_priority_report.json",
    "marginal_value_of_next_experiment": "marginal_value_of_next_experiment.json",
}


def write_planning_bundle(
    run_dir: str | Path,
    *,
    bundle: PlanningBundle,
) -> dict[str, Path]:
    """Write all Slice 05 planning artifacts for a run."""
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
        for key, filename in PLANNING_FILENAMES.items()
    }


def read_planning_bundle(run_dir: str | Path) -> dict[str, Any]:
    """Read planning artifacts into plain dictionaries."""
    root = Path(run_dir)
    payload: dict[str, Any] = {}
    for key, filename in PLANNING_FILENAMES.items():
        path = root / filename
        if not path.exists():
            continue
        payload[key] = json.loads(path.read_text(encoding="utf-8"))
    return payload
