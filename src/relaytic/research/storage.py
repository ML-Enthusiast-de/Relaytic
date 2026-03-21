"""Artifact I/O helpers for Slice 09D research artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from relaytic.core.json_utils import write_json

from .models import ResearchBundle


RESEARCH_FILENAMES = {
    "research_query_plan": "research_query_plan.json",
    "research_source_inventory": "research_source_inventory.json",
    "research_brief": "research_brief.json",
    "method_transfer_report": "method_transfer_report.json",
    "benchmark_reference_report": "benchmark_reference_report.json",
    "external_research_audit": "external_research_audit.json",
}


def write_research_bundle(run_dir: str | Path, *, bundle: ResearchBundle) -> dict[str, Path]:
    root = Path(run_dir)
    root.mkdir(parents=True, exist_ok=True)
    payload = bundle.to_dict()
    return {
        key: write_json(root / filename, payload[key], indent=2, ensure_ascii=False, sort_keys=True)
        for key, filename in RESEARCH_FILENAMES.items()
    }


def read_research_bundle(run_dir: str | Path) -> dict[str, Any]:
    root = Path(run_dir)
    payload: dict[str, Any] = {}
    for key, filename in RESEARCH_FILENAMES.items():
        path = root / filename
        if not path.exists():
            continue
        payload[key] = json.loads(path.read_text(encoding="utf-8"))
    return payload
