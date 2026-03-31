"""Storage helpers for Slice 12D workspace continuity artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from relaytic.core.json_utils import write_json

from .models import (
    BeliefRevisionTriggersArtifact,
    ConfidencePostureArtifact,
    ResultContractArtifact,
    WorkspaceFocusHistoryArtifact,
    WorkspaceLineageArtifact,
    WorkspaceMemoryPolicyArtifact,
    WorkspaceStateArtifact,
)


WORKSPACE_FILENAMES = {
    "workspace_state": "workspace_state.json",
    "workspace_lineage": "workspace_lineage.json",
    "workspace_focus_history": "workspace_focus_history.json",
    "workspace_memory_policy": "workspace_memory_policy.json",
}
RUN_CONTRACT_FILENAMES = {
    "result_contract": "result_contract.json",
    "confidence_posture": "confidence_posture.json",
    "belief_revision_triggers": "belief_revision_triggers.json",
}


def default_workspace_dir(*, run_dir: str | Path | None = None) -> Path:
    """Resolve the shared workspace directory for a run family."""

    if run_dir is not None:
        root = Path(run_dir)
        return root.parent / "workspace"
    project_root = Path(__file__).resolve().parents[3]
    return project_root / "artifacts" / "workspace"


def write_workspace_bundle(
    workspace_dir: str | Path,
    *,
    workspace_state: WorkspaceStateArtifact,
    workspace_lineage: WorkspaceLineageArtifact,
    workspace_focus_history: WorkspaceFocusHistoryArtifact,
    workspace_memory_policy: WorkspaceMemoryPolicyArtifact,
) -> dict[str, Path]:
    """Persist the shared workspace bundle."""

    root = Path(workspace_dir)
    root.mkdir(parents=True, exist_ok=True)
    payloads = {
        "workspace_state": workspace_state.to_dict(),
        "workspace_lineage": workspace_lineage.to_dict(),
        "workspace_focus_history": workspace_focus_history.to_dict(),
        "workspace_memory_policy": workspace_memory_policy.to_dict(),
    }
    written: dict[str, Path] = {}
    for key, payload in payloads.items():
        written[key] = write_json(
            root / WORKSPACE_FILENAMES[key],
            payload,
            indent=2,
            ensure_ascii=False,
            sort_keys=True,
        )
    return written


def write_result_contract_artifacts(
    run_dir: str | Path,
    *,
    result_contract: ResultContractArtifact,
    confidence_posture: ConfidencePostureArtifact,
    belief_revision_triggers: BeliefRevisionTriggersArtifact,
) -> dict[str, Path]:
    """Persist the per-run result-contract artifacts."""

    root = Path(run_dir)
    root.mkdir(parents=True, exist_ok=True)
    payloads = {
        "result_contract": result_contract.to_dict(),
        "confidence_posture": confidence_posture.to_dict(),
        "belief_revision_triggers": belief_revision_triggers.to_dict(),
    }
    written: dict[str, Path] = {}
    for key, payload in payloads.items():
        written[key] = write_json(
            root / RUN_CONTRACT_FILENAMES[key],
            payload,
            indent=2,
            ensure_ascii=False,
            sort_keys=True,
        )
    return written


def read_workspace_bundle(workspace_dir: str | Path) -> dict[str, Any]:
    """Read the shared workspace artifacts if present."""

    root = Path(workspace_dir)
    payload: dict[str, Any] = {}
    for key, filename in WORKSPACE_FILENAMES.items():
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


def read_workspace_bundle_for_run(run_dir: str | Path) -> dict[str, Any]:
    """Read the workspace bundle for a run's shared workspace."""

    return read_workspace_bundle(default_workspace_dir(run_dir=run_dir))


def read_result_contract_artifacts(run_dir: str | Path) -> dict[str, Any]:
    """Read the per-run result-contract artifacts if present."""

    root = Path(run_dir)
    payload: dict[str, Any] = {}
    for key, filename in RUN_CONTRACT_FILENAMES.items():
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
