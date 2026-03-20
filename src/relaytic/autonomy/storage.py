"""Artifact I/O helpers for Slice 09C autonomy artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from relaytic.core.json_utils import write_json

from .models import AutonomyBundle


AUTONOMY_FILENAMES = {
    "autonomy_loop_state": "autonomy_loop_state.json",
    "autonomy_round_report": "autonomy_round_report.json",
    "challenger_queue": "challenger_queue.json",
    "branch_outcome_matrix": "branch_outcome_matrix.json",
    "retrain_run_request": "retrain_run_request.json",
    "recalibration_run_request": "recalibration_run_request.json",
    "champion_lineage": "champion_lineage.json",
    "loop_budget_report": "loop_budget_report.json",
}


def write_autonomy_bundle(run_dir: str | Path, *, bundle: AutonomyBundle) -> dict[str, Path]:
    """Write all Slice 09C autonomy artifacts for a run."""

    root = Path(run_dir)
    root.mkdir(parents=True, exist_ok=True)
    payload = bundle.to_dict()
    return {
        key: write_json(root / filename, payload[key], indent=2, ensure_ascii=False, sort_keys=True)
        for key, filename in AUTONOMY_FILENAMES.items()
    }


def read_autonomy_bundle(run_dir: str | Path) -> dict[str, Any]:
    """Read autonomy artifacts into plain dictionaries."""

    root = Path(run_dir)
    payload: dict[str, Any] = {}
    for key, filename in AUTONOMY_FILENAMES.items():
        path = root / filename
        if not path.exists():
            continue
        payload[key] = json.loads(path.read_text(encoding="utf-8"))
    return payload
