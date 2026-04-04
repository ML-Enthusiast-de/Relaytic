"""Artifact I/O helpers for Slice 10A decision artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from relaytic.core.json_utils import write_json

from relaytic.compiler.storage import COMPILER_FILENAMES
from relaytic.data_fabric.storage import DATA_FABRIC_FILENAMES

from .models import DecisionBundle


DECISION_FILENAMES = {
    "decision_world_model": "decision_world_model.json",
    "controller_policy": "controller_policy.json",
    "handoff_controller_report": "handoff_controller_report.json",
    "intervention_policy_report": "intervention_policy_report.json",
    "decision_usefulness_report": "decision_usefulness_report.json",
    "trajectory_constraint_report": "trajectory_constraint_report.json",
    "feasible_region_map": "feasible_region_map.json",
    "extrapolation_risk_report": "extrapolation_risk_report.json",
    "decision_constraint_report": "decision_constraint_report.json",
    "action_boundary_report": "action_boundary_report.json",
    "deployability_assessment": "deployability_assessment.json",
    "review_gate_state": "review_gate_state.json",
    "constraint_override_request": "constraint_override_request.json",
    "counterfactual_region_report": "counterfactual_region_report.json",
    "value_of_more_data_report": "value_of_more_data_report.json",
    **DATA_FABRIC_FILENAMES,
    **COMPILER_FILENAMES,
}


def write_decision_bundle(run_dir: str | Path, *, bundle: DecisionBundle) -> dict[str, Path]:
    root = Path(run_dir)
    root.mkdir(parents=True, exist_ok=True)
    payload = bundle.to_dict()
    return {
        key: write_json(root / filename, payload[key], indent=2, ensure_ascii=False, sort_keys=True)
        for key, filename in DECISION_FILENAMES.items()
    }


def read_decision_bundle(run_dir: str | Path) -> dict[str, Any]:
    root = Path(run_dir)
    payload: dict[str, Any] = {}
    for key, filename in DECISION_FILENAMES.items():
        path = root / filename
        if not path.exists():
            continue
        try:
            payload[key] = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
    return payload
