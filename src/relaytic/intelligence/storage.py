"""Artifact I/O helpers for Slice 09 intelligence artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from relaytic.core.json_utils import write_json

from .models import IntelligenceBundle


INTELLIGENCE_FILENAMES = {
    "intelligence_mode": "intelligence_mode.json",
    "llm_routing_plan": "llm_routing_plan.json",
    "local_llm_profile": "local_llm_profile.json",
    "llm_backend_discovery": "llm_backend_discovery.json",
    "llm_health_check": "llm_health_check.json",
    "llm_upgrade_suggestions": "llm_upgrade_suggestions.json",
    "semantic_task_request": "semantic_task_request.json",
    "semantic_task_results": "semantic_task_results.json",
    "intelligence_escalation": "intelligence_escalation.json",
    "verifier_report": "verifier_report.json",
    "context_assembly_report": "context_assembly_report.json",
    "doc_grounding_report": "doc_grounding_report.json",
    "semantic_access_audit": "semantic_access_audit.json",
    "semantic_debate_report": "semantic_debate_report.json",
    "semantic_counterposition_pack": "semantic_counterposition_pack.json",
    "semantic_uncertainty_report": "semantic_uncertainty_report.json",
    "semantic_proof_report": "semantic_proof_report.json",
}


def write_intelligence_bundle(run_dir: str | Path, *, bundle: IntelligenceBundle) -> dict[str, Path]:
    """Write all Slice 09 intelligence artifacts for a run."""

    root = Path(run_dir)
    root.mkdir(parents=True, exist_ok=True)
    payload = bundle.to_dict()
    return {
        key: write_json(root / filename, payload[key], indent=2, ensure_ascii=False, sort_keys=True)
        for key, filename in INTELLIGENCE_FILENAMES.items()
    }


def read_intelligence_bundle(run_dir: str | Path) -> dict[str, Any]:
    """Read intelligence artifacts into plain dictionaries."""

    root = Path(run_dir)
    payload: dict[str, Any] = {}
    for key, filename in INTELLIGENCE_FILENAMES.items():
        path = root / filename
        if not path.exists():
            continue
        payload[key] = json.loads(path.read_text(encoding="utf-8"))
    return payload
