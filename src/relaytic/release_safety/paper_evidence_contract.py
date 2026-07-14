"""Factual evidence-cell and separate claim-gate contracts for paper artifacts."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any


PAPER_EVIDENCE_CELL_SCHEMA_VERSION = "relaytic.paper_evidence_cell.v2"
PAPER_CLAIM_GATE_SCHEMA_VERSION = "relaytic.paper_claim_gate.v2"

EVIDENCE_CELL_INTERPRETIVE_FIELDS = frozenset(
    {
        "admissible_use",
        "allowed_claim_scope",
        "claim_state",
        "evidence_role",
        "missing_evidence",
        "paper_role",
        "publication_role",
        "publishability_gate_ref",
        "publishability_gate_status",
        "publishable",
        "release_wording",
        "stronger_claim_status",
    }
)

EVIDENCE_CELL_REQUIRED_FIELDS = (
    "cell_id",
    "dataset_id",
    "split",
    "command",
    "artifact_ref",
    "metric",
    "value",
    "budget_tier",
    "leakage_posture",
)

CLAIM_GATE_REQUIRED_FIELDS = (
    "gate_id",
    "evidence_cell_ids",
    "admissible_use",
    "stronger_claim_status",
    "gate_reasons",
    "missing_evidence",
)


def evidence_cell_violations(cell: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Return deterministic schema violations for one factual evidence cell."""
    present_interpretive = _interpretive_field_paths(cell)
    missing = [field for field in EVIDENCE_CELL_REQUIRED_FIELDS if cell.get(field) in (None, "", [])]
    violations: list[dict[str, Any]] = []
    if present_interpretive:
        violations.append(
            {
                "violation": "interpretive_fields_in_evidence_cell",
                "fields": present_interpretive,
            }
        )
    if missing:
        violations.append(
            {
                "violation": "required_factual_fields_missing",
                "fields": missing,
            }
        )
    return violations


def _interpretive_field_paths(payload: Any, *, prefix: str = "") -> list[str]:
    paths: list[str] = []
    if isinstance(payload, Mapping):
        for key, value in payload.items():
            field = str(key)
            path = f"{prefix}.{field}" if prefix else field
            if field in EVIDENCE_CELL_INTERPRETIVE_FIELDS:
                paths.append(path)
            paths.extend(_interpretive_field_paths(value, prefix=path))
    elif isinstance(payload, list):
        for index, value in enumerate(payload):
            path = f"{prefix}[{index}]"
            paths.extend(_interpretive_field_paths(value, prefix=path))
    return sorted(set(paths))


def claim_gate_violations(
    gate: Mapping[str, Any],
    *,
    known_evidence_cell_ids: Iterable[str],
) -> list[dict[str, Any]]:
    """Return deterministic schema and reference violations for one claim gate."""
    known = set(known_evidence_cell_ids)
    missing = [field for field in CLAIM_GATE_REQUIRED_FIELDS if gate.get(field) in (None, "", [])]
    references = [str(cell_id) for cell_id in gate.get("evidence_cell_ids", []) if cell_id]
    unknown = sorted(set(references).difference(known))
    violations: list[dict[str, Any]] = []
    if missing:
        violations.append({"violation": "required_gate_fields_missing", "fields": missing})
    if unknown:
        violations.append({"violation": "gate_references_missing_evidence_cells", "cell_ids": unknown})
    return violations


def audit_evidence_gate_separation(
    *,
    evidence_cells: Iterable[Mapping[str, Any]],
    claim_gates: Iterable[Mapping[str, Any]],
) -> dict[str, Any]:
    """Audit factual/interpretive separation and bidirectional gate coverage."""
    cells = [dict(cell) for cell in evidence_cells]
    gates = [dict(gate) for gate in claim_gates]
    cell_ids = [str(cell.get("cell_id") or "") for cell in cells]
    known_ids = {cell_id for cell_id in cell_ids if cell_id}
    violations: list[dict[str, Any]] = []

    for cell in cells:
        for violation in evidence_cell_violations(cell):
            violations.append({"cell_id": cell.get("cell_id"), **violation})

    referenced_ids: set[str] = set()
    for gate in gates:
        referenced_ids.update(str(cell_id) for cell_id in gate.get("evidence_cell_ids", []) if cell_id)
        for violation in claim_gate_violations(gate, known_evidence_cell_ids=known_ids):
            violations.append({"gate_id": gate.get("gate_id"), **violation})

    ungated = sorted(known_ids.difference(referenced_ids))
    if ungated:
        violations.append(
            {
                "violation": "public_evidence_cells_without_separate_gate",
                "cell_ids": ungated,
            }
        )

    duplicate_cell_ids = sorted({cell_id for cell_id in cell_ids if cell_ids.count(cell_id) > 1})
    if duplicate_cell_ids:
        violations.append({"violation": "duplicate_evidence_cell_ids", "cell_ids": duplicate_cell_ids})

    return {
        "schema_version": "relaytic.paper_evidence_gate_audit.v1",
        "status": "pass" if not violations and bool(cells) and bool(gates) else "fail",
        "evidence_cell_schema": PAPER_EVIDENCE_CELL_SCHEMA_VERSION,
        "claim_gate_schema": PAPER_CLAIM_GATE_SCHEMA_VERSION,
        "evidence_cell_count": len(cells),
        "claim_gate_count": len(gates),
        "all_public_cells_have_separate_gate": not ungated,
        "violations": violations,
    }


__all__ = [
    "CLAIM_GATE_REQUIRED_FIELDS",
    "EVIDENCE_CELL_INTERPRETIVE_FIELDS",
    "EVIDENCE_CELL_REQUIRED_FIELDS",
    "PAPER_CLAIM_GATE_SCHEMA_VERSION",
    "PAPER_EVIDENCE_CELL_SCHEMA_VERSION",
    "audit_evidence_gate_separation",
    "claim_gate_violations",
    "evidence_cell_violations",
]
