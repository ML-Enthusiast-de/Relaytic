"""Artifact I/O helpers for Slice 12B eval artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from relaytic.core.json_utils import write_json

from .models import EvalBundle


EVAL_FILENAMES = {
    "agent_eval_matrix": "agent_eval_matrix.json",
    "security_eval_report": "security_eval_report.json",
    "red_team_report": "red_team_report.json",
    "protocol_conformance_report": "protocol_conformance_report.json",
    "host_surface_matrix": "host_surface_matrix.json",
    "trace_identity_conformance": "trace_identity_conformance.json",
    "eval_surface_parity_report": "eval_surface_parity_report.json",
}


def write_eval_bundle(run_dir: str | Path, *, bundle: EvalBundle) -> dict[str, Path]:
    root = Path(run_dir)
    root.mkdir(parents=True, exist_ok=True)
    payload = bundle.to_dict()
    return {
        key: write_json(root / filename, payload[key], indent=2, ensure_ascii=False, sort_keys=True)
        for key, filename in EVAL_FILENAMES.items()
    }


def read_eval_bundle(run_dir: str | Path) -> dict[str, Any]:
    root = Path(run_dir)
    payload: dict[str, Any] = {}
    for key, filename in EVAL_FILENAMES.items():
        path = root / filename
        if not path.exists():
            continue
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if isinstance(value, dict) and value:
            payload[key] = value
    return payload
