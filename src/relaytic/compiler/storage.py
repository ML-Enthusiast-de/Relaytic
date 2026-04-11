"""Artifact I/O helpers for Slice 10A method compiler artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from relaytic.core.json_utils import write_json

from .models import (
    ArchitectureCandidateRegistry,
    CompiledBenchmarkProtocol,
    CompiledChallengerTemplates,
    CompiledFeatureHypotheses,
    MethodImportReport,
    MethodCompilerReport,
)


COMPILER_FILENAMES = {
    "method_compiler_report": "method_compiler_report.json",
    "compiled_challenger_templates": "compiled_challenger_templates.json",
    "compiled_feature_hypotheses": "compiled_feature_hypotheses.json",
    "compiled_benchmark_protocol": "compiled_benchmark_protocol.json",
    "method_import_report": "method_import_report.json",
    "architecture_candidate_registry": "architecture_candidate_registry.json",
}


def write_compiler_bundle(
    run_dir: str | Path,
    *,
    method_compiler_report: MethodCompilerReport,
    compiled_challenger_templates: CompiledChallengerTemplates,
    compiled_feature_hypotheses: CompiledFeatureHypotheses,
    compiled_benchmark_protocol: CompiledBenchmarkProtocol,
    method_import_report: MethodImportReport,
    architecture_candidate_registry: ArchitectureCandidateRegistry,
) -> dict[str, Path]:
    root = Path(run_dir)
    root.mkdir(parents=True, exist_ok=True)
    payload = {
        "method_compiler_report": method_compiler_report.to_dict(),
        "compiled_challenger_templates": compiled_challenger_templates.to_dict(),
        "compiled_feature_hypotheses": compiled_feature_hypotheses.to_dict(),
        "compiled_benchmark_protocol": compiled_benchmark_protocol.to_dict(),
        "method_import_report": method_import_report.to_dict(),
        "architecture_candidate_registry": architecture_candidate_registry.to_dict(),
    }
    return {
        key: write_json(root / filename, payload[key], indent=2, ensure_ascii=False, sort_keys=True)
        for key, filename in COMPILER_FILENAMES.items()
    }


def read_compiler_bundle(run_dir: str | Path) -> dict[str, Any]:
    root = Path(run_dir)
    payload: dict[str, Any] = {}
    for key, filename in COMPILER_FILENAMES.items():
        path = root / filename
        if not path.exists():
            continue
        try:
            payload[key] = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
    return payload
