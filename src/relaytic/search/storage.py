"""Artifact I/O helpers for Slice 13 search-controller artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from relaytic.core.json_utils import write_json

from .models import SearchBundle


SEARCH_FILENAMES = {
    "search_controller_plan": "search_controller_plan.json",
    "portfolio_search_trace": "portfolio_search_trace.json",
    "hpo_campaign_report": "hpo_campaign_report.json",
    "search_decision_ledger": "search_decision_ledger.json",
    "execution_backend_profile": "execution_backend_profile.json",
    "device_allocation": "device_allocation.json",
    "distributed_run_plan": "distributed_run_plan.json",
    "scheduler_job_map": "scheduler_job_map.json",
    "checkpoint_state": "checkpoint_state.json",
    "execution_strategy_report": "execution_strategy_report.json",
    "search_value_report": "search_value_report.json",
    "search_controller_eval_report": "search_controller_eval_report.json",
}


def write_search_bundle(run_dir: str | Path, *, bundle: SearchBundle) -> dict[str, Path]:
    root = Path(run_dir)
    root.mkdir(parents=True, exist_ok=True)
    payload = bundle.to_dict()
    return {
        key: write_json(root / filename, payload[key], indent=2, ensure_ascii=False, sort_keys=True)
        for key, filename in SEARCH_FILENAMES.items()
    }


def read_search_bundle(run_dir: str | Path) -> dict[str, Any]:
    root = Path(run_dir)
    payload: dict[str, Any] = {}
    for key, filename in SEARCH_FILENAMES.items():
        path = root / filename
        if not path.exists():
            continue
        try:
            loaded = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if isinstance(loaded, dict):
            payload[key] = loaded
    return payload
