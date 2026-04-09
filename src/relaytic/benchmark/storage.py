"""Artifact I/O helpers for Slice 11 benchmark artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from relaytic.core.json_utils import write_json

from .models import BenchmarkBundle


BENCHMARK_FILENAMES = {
    "reference_approach_matrix": "reference_approach_matrix.json",
    "benchmark_gap_report": "benchmark_gap_report.json",
    "benchmark_parity_report": "benchmark_parity_report.json",
    "external_challenger_manifest": "external_challenger_manifest.json",
    "external_challenger_evaluation": "external_challenger_evaluation.json",
    "incumbent_parity_report": "incumbent_parity_report.json",
    "beat_target_contract": "beat_target_contract.json",
    "paper_benchmark_manifest": "paper_benchmark_manifest.json",
    "paper_benchmark_table": "paper_benchmark_table.json",
    "benchmark_ablation_matrix": "benchmark_ablation_matrix.json",
    "rerun_variance_report": "rerun_variance_report.json",
    "benchmark_claims_report": "benchmark_claims_report.json",
}


def write_benchmark_bundle(run_dir: str | Path, *, bundle: BenchmarkBundle) -> dict[str, Path]:
    root = Path(run_dir)
    root.mkdir(parents=True, exist_ok=True)
    payload = bundle.to_dict()
    return {
        key: write_json(root / filename, payload[key], indent=2, ensure_ascii=False, sort_keys=True)
        for key, filename in BENCHMARK_FILENAMES.items()
    }


def read_benchmark_bundle(run_dir: str | Path) -> dict[str, Any]:
    root = Path(run_dir)
    payload: dict[str, Any] = {}
    for key, filename in BENCHMARK_FILENAMES.items():
        path = root / filename
        if not path.exists():
            continue
        payload[key] = json.loads(path.read_text(encoding="utf-8"))
    return payload
