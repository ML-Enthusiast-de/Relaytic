"""Artifact I/O helpers for Slice 06 evidence artifacts."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from relaytic.core.json_utils import write_json

from .models import EvidenceBundle


EVIDENCE_FILENAMES = {
    "experiment_registry": "experiment_registry.json",
    "challenger_report": "challenger_report.json",
    "ablation_report": "ablation_report.json",
    "audit_report": "audit_report.json",
    "belief_update": "belief_update.json",
}
LEADERBOARD_FILENAME = "leaderboard.csv"
TECHNICAL_REPORT_RELATIVE_PATH = Path("reports") / "technical_report.md"
DECISION_MEMO_RELATIVE_PATH = Path("reports") / "decision_memo.md"


def write_evidence_bundle(
    run_dir: str | Path,
    *,
    bundle: EvidenceBundle,
    leaderboard_rows: list[dict[str, Any]],
    technical_report_markdown: str,
    decision_memo_markdown: str,
) -> dict[str, Path]:
    """Write all Slice 06 evidence artifacts for a run."""
    root = Path(run_dir)
    root.mkdir(parents=True, exist_ok=True)
    payload = bundle.to_dict()
    written = {
        key: write_json(
            root / filename,
            payload[key],
            indent=2,
            ensure_ascii=False,
            sort_keys=True,
        )
        for key, filename in EVIDENCE_FILENAMES.items()
    }
    written["leaderboard"] = _write_leaderboard(root / LEADERBOARD_FILENAME, rows=leaderboard_rows)
    written["technical_report"] = _write_text(root / TECHNICAL_REPORT_RELATIVE_PATH, technical_report_markdown)
    written["decision_memo"] = _write_text(root / DECISION_MEMO_RELATIVE_PATH, decision_memo_markdown)
    return written


def read_evidence_bundle(run_dir: str | Path) -> dict[str, Any]:
    """Read evidence artifacts into plain dictionaries."""
    root = Path(run_dir)
    payload: dict[str, Any] = {}
    for key, filename in EVIDENCE_FILENAMES.items():
        path = root / filename
        if not path.exists():
            continue
        payload[key] = json.loads(path.read_text(encoding="utf-8"))
    leaderboard_path = root / LEADERBOARD_FILENAME
    if leaderboard_path.exists():
        with leaderboard_path.open("r", encoding="utf-8", newline="") as handle:
            payload["leaderboard_rows"] = list(csv.DictReader(handle))
    technical_report_path = root / TECHNICAL_REPORT_RELATIVE_PATH
    if technical_report_path.exists():
        payload["technical_report_path"] = str(technical_report_path)
    decision_memo_path = root / DECISION_MEMO_RELATIVE_PATH
    if decision_memo_path.exists():
        payload["decision_memo_path"] = str(decision_memo_path)
    return payload


def _write_leaderboard(path: Path, *, rows: list[dict[str, Any]]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "rank",
        "experiment_id",
        "role",
        "status",
        "model_family",
        "primary_metric",
        "evaluation_split",
        "primary_metric_value",
        "delta_from_champion",
        "feature_count",
        "artifact_root",
        "note",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({name: row.get(name, "") for name in fieldnames})
    return path


def _write_text(path: Path, content: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path
