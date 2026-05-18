"""Storage helpers for Slice 15V-A guide artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from relaytic.core.json_utils import write_json


GUIDE_FILENAMES = {
    "guide_state": "guide_state.json",
    "guide_action_menu": "guide_action_menu.json",
    "guide_artifact_shortlist": "guide_artifact_shortlist.json",
    "guide_question_starters": "guide_question_starters.json",
    "guide_local_llm_summary": "guide_local_llm_summary.json",
}

EXTERNAL_CONTEXT_FILENAMES = {
    "external_llm_context_pack": "external_llm_context_pack.json",
    "external_llm_context_pack_md": "external_llm_context_pack.md",
    "external_llm_artifact_index": "external_llm_artifact_index.json",
    "external_llm_redaction_report": "external_llm_redaction_report.json",
}


def default_guide_state_dir() -> Path:
    project_root = Path(__file__).resolve().parents[3]
    return project_root / "artifacts" / "guide_onboarding"


def write_guide_bundle(state_dir: str | Path, *, bundle: dict[str, Any]) -> dict[str, Path]:
    root = Path(state_dir)
    root.mkdir(parents=True, exist_ok=True)
    written: dict[str, Path] = {}
    for key, filename in GUIDE_FILENAMES.items():
        payload = bundle.get(key)
        if isinstance(payload, dict):
            written[key] = write_json(
                root / filename,
                payload,
                indent=2,
                ensure_ascii=False,
                sort_keys=True,
            )
    return written


def write_external_context_pack(
    state_dir: str | Path,
    *,
    context_pack: dict[str, Any],
    context_markdown: str,
    artifact_index: dict[str, Any],
    redaction_report: dict[str, Any],
) -> dict[str, Path]:
    root = Path(state_dir)
    root.mkdir(parents=True, exist_ok=True)
    paths = {
        "external_llm_context_pack": write_json(
            root / EXTERNAL_CONTEXT_FILENAMES["external_llm_context_pack"],
            context_pack,
            indent=2,
            ensure_ascii=False,
            sort_keys=True,
        ),
        "external_llm_artifact_index": write_json(
            root / EXTERNAL_CONTEXT_FILENAMES["external_llm_artifact_index"],
            artifact_index,
            indent=2,
            ensure_ascii=False,
            sort_keys=True,
        ),
        "external_llm_redaction_report": write_json(
            root / EXTERNAL_CONTEXT_FILENAMES["external_llm_redaction_report"],
            redaction_report,
            indent=2,
            ensure_ascii=False,
            sort_keys=True,
        ),
    }
    markdown_path = root / EXTERNAL_CONTEXT_FILENAMES["external_llm_context_pack_md"]
    markdown_path.write_text(context_markdown, encoding="utf-8")
    paths["external_llm_context_pack_md"] = markdown_path
    return paths


def read_guide_bundle(state_dir: str | Path) -> dict[str, Any]:
    root = Path(state_dir)
    payload: dict[str, Any] = {}
    for key, filename in GUIDE_FILENAMES.items():
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
