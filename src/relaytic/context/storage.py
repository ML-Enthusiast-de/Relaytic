"""Artifact I/O helpers for context foundation artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from relaytic.core.json_utils import write_json

from .models import DataOrigin, DomainBrief, TaskBrief


CONTEXT_FILENAMES = {
    "data_origin": "data_origin.json",
    "domain_brief": "domain_brief.json",
    "task_brief": "task_brief.json",
}


def write_context_bundle(
    run_dir: str | Path,
    *,
    data_origin: DataOrigin,
    domain_brief: DomainBrief,
    task_brief: TaskBrief,
) -> dict[str, Path]:
    """Write all context-layer artifacts for a run."""
    root = Path(run_dir)
    root.mkdir(parents=True, exist_ok=True)
    paths = {
        "data_origin": write_json(root / CONTEXT_FILENAMES["data_origin"], data_origin.to_dict(), indent=2, ensure_ascii=False, sort_keys=True),
        "domain_brief": write_json(root / CONTEXT_FILENAMES["domain_brief"], domain_brief.to_dict(), indent=2, ensure_ascii=False, sort_keys=True),
        "task_brief": write_json(root / CONTEXT_FILENAMES["task_brief"], task_brief.to_dict(), indent=2, ensure_ascii=False, sort_keys=True),
    }
    return paths


def read_context_bundle(run_dir: str | Path) -> dict[str, Any]:
    """Read context artifacts into plain dictionaries."""
    root = Path(run_dir)
    payload: dict[str, Any] = {}
    for key, filename in CONTEXT_FILENAMES.items():
        path = root / filename
        payload[key] = json.loads(path.read_text(encoding="utf-8"))
    return payload
