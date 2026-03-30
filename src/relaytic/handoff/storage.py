"""Artifact I/O helpers for differentiated post-run handoffs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from relaytic.core.json_utils import write_json

from .models import HandoffBundle, NextRunFocusArtifact


HANDOFF_FILENAMES = {
    "run_handoff": "run_handoff.json",
    "next_run_options": "next_run_options.json",
    "next_run_focus": "next_run_focus.json",
}
USER_RESULT_REPORT_RELATIVE_PATH = Path("reports") / "user_result_report.md"
AGENT_RESULT_REPORT_RELATIVE_PATH = Path("reports") / "agent_result_report.md"


def write_handoff_bundle(run_dir: str | Path, *, bundle: HandoffBundle) -> dict[str, Path]:
    """Write all handoff artifacts for a run."""

    root = Path(run_dir)
    root.mkdir(parents=True, exist_ok=True)
    payload = bundle.to_dict()
    written: dict[str, Path] = {}
    for key, filename in HANDOFF_FILENAMES.items():
        item = payload.get(key)
        if not isinstance(item, dict) or not item:
            continue
        written[key] = write_json(
            root / filename,
            item,
            indent=2,
            ensure_ascii=False,
            sort_keys=True,
        )
    return written


def write_next_run_focus(run_dir: str | Path, *, artifact: NextRunFocusArtifact) -> Path:
    """Persist only the next-run focus artifact."""

    root = Path(run_dir)
    root.mkdir(parents=True, exist_ok=True)
    return write_json(
        root / HANDOFF_FILENAMES["next_run_focus"],
        artifact.to_dict(),
        indent=2,
        ensure_ascii=False,
        sort_keys=True,
    )


def read_handoff_bundle(run_dir: str | Path) -> dict[str, Any]:
    """Read handoff artifacts into plain dictionaries."""

    root = Path(run_dir)
    payload: dict[str, Any] = {}
    for key, filename in HANDOFF_FILENAMES.items():
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
