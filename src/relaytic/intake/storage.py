"""Artifact I/O helpers for Slice 04 intake artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from relaytic.core.json_utils import write_json

from .models import IntakeBundle


INTAKE_FILENAMES = {
    "intake_record": "intake_record.json",
    "autonomy_mode": "autonomy_mode.json",
    "clarification_queue": "clarification_queue.json",
    "assumption_log": "assumption_log.json",
    "context_interpretation": "context_interpretation.json",
    "context_constraints": "context_constraints.json",
    "semantic_mapping": "semantic_mapping.json",
}


def write_intake_bundle(run_dir: str | Path, *, bundle: IntakeBundle) -> dict[str, Path]:
    """Write all Slice 04 intake artifacts for a run."""
    root = Path(run_dir)
    root.mkdir(parents=True, exist_ok=True)
    paths = {
        "intake_record": write_json(
            root / INTAKE_FILENAMES["intake_record"],
            bundle.intake_record.to_dict(),
            indent=2,
            ensure_ascii=False,
            sort_keys=True,
        ),
        "autonomy_mode": write_json(
            root / INTAKE_FILENAMES["autonomy_mode"],
            bundle.autonomy_mode.to_dict(),
            indent=2,
            ensure_ascii=False,
            sort_keys=True,
        ),
        "clarification_queue": write_json(
            root / INTAKE_FILENAMES["clarification_queue"],
            bundle.clarification_queue.to_dict(),
            indent=2,
            ensure_ascii=False,
            sort_keys=True,
        ),
        "assumption_log": write_json(
            root / INTAKE_FILENAMES["assumption_log"],
            bundle.assumption_log.to_dict(),
            indent=2,
            ensure_ascii=False,
            sort_keys=True,
        ),
        "context_interpretation": write_json(
            root / INTAKE_FILENAMES["context_interpretation"],
            bundle.context_interpretation.to_dict(),
            indent=2,
            ensure_ascii=False,
            sort_keys=True,
        ),
        "context_constraints": write_json(
            root / INTAKE_FILENAMES["context_constraints"],
            bundle.context_constraints.to_dict(),
            indent=2,
            ensure_ascii=False,
            sort_keys=True,
        ),
        "semantic_mapping": write_json(
            root / INTAKE_FILENAMES["semantic_mapping"],
            bundle.semantic_mapping.to_dict(),
            indent=2,
            ensure_ascii=False,
            sort_keys=True,
        ),
    }
    return paths


def read_intake_bundle(run_dir: str | Path) -> dict[str, Any]:
    """Read Slice 04 intake artifacts into plain dictionaries."""
    root = Path(run_dir)
    payload: dict[str, Any] = {}
    for key, filename in INTAKE_FILENAMES.items():
        path = root / filename
        if not path.exists():
            continue
        payload[key] = json.loads(path.read_text(encoding="utf-8"))
    return payload
