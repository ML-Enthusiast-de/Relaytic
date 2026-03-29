"""Artifact I/O helpers for Slice 12B trace artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from relaytic.core.json_utils import dumps_json, write_json

from .models import TraceBundle, TraceSpan


TRACE_FILENAMES = {
    "trace_model": "trace_model.json",
    "specialist_trace_index": "specialist_trace_index.json",
    "branch_trace_graph": "branch_trace_graph.json",
    "adjudication_scorecard": "adjudication_scorecard.json",
    "decision_replay_report": "decision_replay_report.json",
}

TRACE_JSONL_FILENAMES = {
    "trace_span_log": "trace_span_log.jsonl",
    "tool_trace_log": "tool_trace_log.jsonl",
    "intervention_trace_log": "intervention_trace_log.jsonl",
    "claim_packet_log": "claim_packet_log.jsonl",
}


def append_trace_span(run_dir: str | Path, *, span: TraceSpan | dict[str, Any]) -> Path:
    payload = span.to_dict() if isinstance(span, TraceSpan) else dict(span)
    return append_jsonl_record(Path(run_dir) / TRACE_JSONL_FILENAMES["trace_span_log"], payload)


def append_jsonl_record(path: str | Path, payload: dict[str, Any]) -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("a", encoding="utf-8") as handle:
        handle.write(dumps_json(payload, indent=None, ensure_ascii=False, sort_keys=True))
        handle.write("\n")
    return target


def write_trace_bundle(run_dir: str | Path, *, bundle: TraceBundle) -> dict[str, Path]:
    root = Path(run_dir)
    root.mkdir(parents=True, exist_ok=True)
    payload = bundle.to_dict()
    written = {
        key: write_json(root / filename, payload[key], indent=2, ensure_ascii=False, sort_keys=True)
        for key, filename in TRACE_FILENAMES.items()
    }
    for key, filename in TRACE_JSONL_FILENAMES.items():
        written[key] = _write_jsonl(root / filename, payload.get(key, []))
    return written


def read_trace_bundle(run_dir: str | Path) -> dict[str, Any]:
    root = Path(run_dir)
    payload: dict[str, Any] = {}
    for key, filename in TRACE_FILENAMES.items():
        path = root / filename
        if not path.exists():
            continue
        try:
            payload[key] = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
    for key, filename in TRACE_JSONL_FILENAMES.items():
        path = root / filename
        if path.exists():
            payload[key] = read_jsonl_records(path)
    return payload


def read_jsonl_records(path: str | Path) -> list[dict[str, Any]]:
    target = Path(path)
    if not target.exists():
        return []
    records: list[dict[str, Any]] = []
    try:
        for raw_line in target.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line:
                continue
            try:
                value = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(value, dict):
                records.append(value)
    except OSError:
        return []
    return records


def _write_jsonl(path: Path, records: list[dict[str, Any]]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [dumps_json(record, indent=None, ensure_ascii=False, sort_keys=True) for record in records]
    path.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")
    return path
