"""Storage helpers for Slice 12D iteration planning artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from relaytic.core.json_utils import write_json

from .models import (
    DataExpansionCandidatesArtifact,
    FocusDecisionRecordArtifact,
    NextRunPlanArtifact,
)


ITERATION_FILENAMES = {
    "next_run_plan": "next_run_plan.json",
    "focus_decision_record": "focus_decision_record.json",
    "data_expansion_candidates": "data_expansion_candidates.json",
}


def write_iteration_bundle(
    *,
    workspace_dir: str | Path,
    run_dir: str | Path,
    next_run_plan: NextRunPlanArtifact,
    focus_decision_record: FocusDecisionRecordArtifact,
    data_expansion_candidates: DataExpansionCandidatesArtifact,
) -> dict[str, Path]:
    """Persist the next-run plan plus per-run iteration support artifacts."""

    workspace_root = Path(workspace_dir)
    run_root = Path(run_dir)
    workspace_root.mkdir(parents=True, exist_ok=True)
    run_root.mkdir(parents=True, exist_ok=True)
    return {
        "next_run_plan": write_json(
            workspace_root / ITERATION_FILENAMES["next_run_plan"],
            next_run_plan.to_dict(),
            indent=2,
            ensure_ascii=False,
            sort_keys=True,
        ),
        "focus_decision_record": write_json(
            run_root / ITERATION_FILENAMES["focus_decision_record"],
            focus_decision_record.to_dict(),
            indent=2,
            ensure_ascii=False,
            sort_keys=True,
        ),
        "data_expansion_candidates": write_json(
            run_root / ITERATION_FILENAMES["data_expansion_candidates"],
            data_expansion_candidates.to_dict(),
            indent=2,
            ensure_ascii=False,
            sort_keys=True,
        ),
    }


def read_iteration_bundle(*, workspace_dir: str | Path, run_dir: str | Path) -> dict[str, Any]:
    """Read the iteration artifacts if present."""

    payload: dict[str, Any] = {}
    for key, path in {
        "next_run_plan": Path(workspace_dir) / ITERATION_FILENAMES["next_run_plan"],
        "focus_decision_record": Path(run_dir) / ITERATION_FILENAMES["focus_decision_record"],
        "data_expansion_candidates": Path(run_dir) / ITERATION_FILENAMES["data_expansion_candidates"],
    }.items():
        if not path.exists():
            continue
        try:
            loaded = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if isinstance(loaded, dict):
            payload[key] = loaded
    return payload
