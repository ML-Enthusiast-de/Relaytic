"""Artifact I/O helpers for Slice 09A memory artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from relaytic.core.json_utils import write_json

from .models import MemoryBundle


MEMORY_FILENAMES = {
    "memory_retrieval": "memory_retrieval.json",
    "analog_run_candidates": "analog_run_candidates.json",
    "route_prior_context": "route_prior_context.json",
    "challenger_prior_suggestions": "challenger_prior_suggestions.json",
    "reflection_memory": "reflection_memory.json",
    "memory_flush_report": "memory_flush_report.json",
}


def write_memory_bundle(run_dir: str | Path, *, bundle: MemoryBundle) -> dict[str, Path]:
    """Write all Slice 09A memory artifacts for a run."""
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
        for key, filename in MEMORY_FILENAMES.items()
    }


def read_memory_bundle(run_dir: str | Path) -> dict[str, Any]:
    """Read memory artifacts into plain dictionaries."""
    root = Path(run_dir)
    payload: dict[str, Any] = {}
    for key, filename in MEMORY_FILENAMES.items():
        path = root / filename
        if not path.exists():
            continue
        payload[key] = json.loads(path.read_text(encoding="utf-8"))
    return payload

