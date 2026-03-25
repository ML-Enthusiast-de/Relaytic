"""Artifact I/O helpers for Slice 10C control artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from relaytic.core.json_utils import write_json

from .models import ControlBundle


CONTROL_FILENAMES = {
    "intervention_request": "intervention_request.json",
    "intervention_contract": "intervention_contract.json",
    "control_challenge_report": "control_challenge_report.json",
    "override_decision": "override_decision.json",
    "intervention_ledger": "intervention_ledger.json",
    "recovery_checkpoint": "recovery_checkpoint.json",
    "control_injection_audit": "control_injection_audit.json",
    "causal_memory_index": "causal_memory_index.json",
    "intervention_memory_log": "intervention_memory_log.json",
    "outcome_memory_graph": "outcome_memory_graph.json",
    "method_memory_index": "method_memory_index.json",
}


def write_control_bundle(run_dir: str | Path, *, bundle: ControlBundle) -> dict[str, Path]:
    root = Path(run_dir)
    root.mkdir(parents=True, exist_ok=True)
    payload = bundle.to_dict()
    return {
        key: write_json(root / filename, payload[key], indent=2, ensure_ascii=False, sort_keys=True)
        for key, filename in CONTROL_FILENAMES.items()
    }


def read_control_bundle(run_dir: str | Path) -> dict[str, Any]:
    root = Path(run_dir)
    payload: dict[str, Any] = {}
    for key, filename in CONTROL_FILENAMES.items():
        path = root / filename
        if not path.exists():
            continue
        try:
            payload[key] = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
    return payload
