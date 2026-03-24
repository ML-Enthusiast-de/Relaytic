"""Artifact I/O helpers for Slice 10 feedback artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from relaytic.core.json_utils import write_json

from .models import FeedbackBundle


FEEDBACK_FILENAMES = {
    "feedback_intake": "feedback_intake.json",
    "feedback_validation": "feedback_validation.json",
    "feedback_effect_report": "feedback_effect_report.json",
    "feedback_casebook": "feedback_casebook.json",
    "outcome_observation_report": "outcome_observation_report.json",
    "decision_policy_update_suggestions": "decision_policy_update_suggestions.json",
    "policy_update_suggestions": "policy_update_suggestions.json",
    "route_prior_updates": "route_prior_updates.json",
}


def write_feedback_bundle(run_dir: str | Path, *, bundle: FeedbackBundle) -> dict[str, Path]:
    root = Path(run_dir)
    root.mkdir(parents=True, exist_ok=True)
    payload = bundle.to_dict()
    return {
        key: write_json(root / filename, payload[key], indent=2, ensure_ascii=False, sort_keys=True)
        for key, filename in FEEDBACK_FILENAMES.items()
    }


def read_feedback_bundle(run_dir: str | Path) -> dict[str, Any]:
    root = Path(run_dir)
    payload: dict[str, Any] = {}
    for key, filename in FEEDBACK_FILENAMES.items():
        path = root / filename
        if not path.exists():
            continue
        payload[key] = json.loads(path.read_text(encoding="utf-8"))
    return payload


def write_feedback_intake_artifact(run_dir: str | Path, payload: dict[str, Any]) -> Path:
    root = Path(run_dir)
    root.mkdir(parents=True, exist_ok=True)
    return write_json(
        root / FEEDBACK_FILENAMES["feedback_intake"],
        payload,
        indent=2,
        ensure_ascii=False,
        sort_keys=True,
    )
