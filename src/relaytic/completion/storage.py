"""Artifact I/O helpers for Slice 07 completion artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from relaytic.core.json_utils import write_json

from .models import CompletionBundle


COMPLETION_FILENAMES = {
    "completion_decision": "completion_decision.json",
    "run_state": "run_state.json",
    "stage_timeline": "stage_timeline.json",
    "mandate_evidence_review": "mandate_evidence_review.json",
    "blocking_analysis": "blocking_analysis.json",
    "next_action_queue": "next_action_queue.json",
}


def write_completion_bundle(run_dir: str | Path, *, bundle: CompletionBundle) -> dict[str, Path]:
    """Write all Slice 07 completion artifacts for a run."""
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
        for key, filename in COMPLETION_FILENAMES.items()
    }


def read_completion_bundle(run_dir: str | Path) -> dict[str, Any]:
    """Read completion artifacts into plain dictionaries."""
    root = Path(run_dir)
    payload: dict[str, Any] = {}
    for key, filename in COMPLETION_FILENAMES.items():
        path = root / filename
        if not path.exists():
            continue
        payload[key] = json.loads(path.read_text(encoding="utf-8"))
    return payload
