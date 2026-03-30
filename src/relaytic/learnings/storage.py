"""Storage helpers for durable cross-run learnings."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from relaytic.core.json_utils import write_json

from .models import LabLearningsSnapshotArtifact, LearningsStateArtifact


LEARNINGS_STATE_FILENAME = "learnings_state.json"
LEARNINGS_MARKDOWN_FILENAME = "learnings.md"
RUN_LEARNINGS_SNAPSHOT_FILENAME = "lab_learnings_snapshot.json"


def default_learnings_state_dir(*, run_dir: str | Path | None = None) -> Path:
    """Resolve the default durable learnings directory."""

    if run_dir is not None:
        root = Path(run_dir)
        return root.parent / "lab_memory"
    project_root = Path(__file__).resolve().parents[3]
    return project_root / "artifacts" / "lab_memory"


def write_learnings_state(state_dir: str | Path, *, artifact: LearningsStateArtifact) -> Path:
    """Persist the durable learnings state artifact."""

    root = Path(state_dir)
    root.mkdir(parents=True, exist_ok=True)
    return write_json(
        root / LEARNINGS_STATE_FILENAME,
        artifact.to_dict(),
        indent=2,
        ensure_ascii=False,
        sort_keys=True,
    )


def write_learnings_markdown(state_dir: str | Path, *, markdown: str) -> Path:
    """Persist the human-readable learnings markdown."""

    root = Path(state_dir)
    root.mkdir(parents=True, exist_ok=True)
    path = root / LEARNINGS_MARKDOWN_FILENAME
    path.write_text(markdown, encoding="utf-8")
    return path


def write_learnings_snapshot(run_dir: str | Path, *, artifact: LabLearningsSnapshotArtifact) -> Path:
    """Persist the run-local learnings snapshot."""

    root = Path(run_dir)
    root.mkdir(parents=True, exist_ok=True)
    return write_json(
        root / RUN_LEARNINGS_SNAPSHOT_FILENAME,
        artifact.to_dict(),
        indent=2,
        ensure_ascii=False,
        sort_keys=True,
    )


def read_learnings_state(state_dir: str | Path) -> dict[str, Any]:
    """Read the durable learnings state artifact if present."""

    path = Path(state_dir) / LEARNINGS_STATE_FILENAME
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return payload if isinstance(payload, dict) else {}


def read_learnings_snapshot(run_dir: str | Path) -> dict[str, Any]:
    """Read the run-local learnings snapshot if present."""

    path = Path(run_dir) / RUN_LEARNINGS_SNAPSHOT_FILENAME
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return payload if isinstance(payload, dict) else {}
