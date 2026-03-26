"""Artifact I/O helpers for Slice 10A data-fabric artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from relaytic.core.json_utils import write_json

from .models import DataAcquisitionPlan, JoinCandidateReport, SourceGraph


DATA_FABRIC_FILENAMES = {
    "source_graph": "source_graph.json",
    "join_candidate_report": "join_candidate_report.json",
    "data_acquisition_plan": "data_acquisition_plan.json",
}


def write_data_fabric_bundle(
    run_dir: str | Path,
    *,
    source_graph: SourceGraph,
    join_candidate_report: JoinCandidateReport,
    data_acquisition_plan: DataAcquisitionPlan,
) -> dict[str, Path]:
    root = Path(run_dir)
    root.mkdir(parents=True, exist_ok=True)
    payload = {
        "source_graph": source_graph.to_dict(),
        "join_candidate_report": join_candidate_report.to_dict(),
        "data_acquisition_plan": data_acquisition_plan.to_dict(),
    }
    return {
        key: write_json(root / filename, payload[key], indent=2, ensure_ascii=False, sort_keys=True)
        for key, filename in DATA_FABRIC_FILENAMES.items()
    }


def read_data_fabric_bundle(run_dir: str | Path) -> dict[str, Any]:
    root = Path(run_dir)
    payload: dict[str, Any] = {}
    for key, filename in DATA_FABRIC_FILENAMES.items():
        path = root / filename
        if not path.exists():
            continue
        try:
            payload[key] = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
    return payload
