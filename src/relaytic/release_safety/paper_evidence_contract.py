"""Typed factual evidence-cell and separate claim-gate contracts."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any


METRIC_EVIDENCE_CELL_TYPE = "metric_evidence_cell"
INVARIANT_EVIDENCE_CELL_TYPE = "invariant_evidence_cell"
PAPER_METRIC_EVIDENCE_CELL_SCHEMA_VERSION = "relaytic.paper_metric_evidence_cell.v1"
PAPER_INVARIANT_EVIDENCE_CELL_SCHEMA_VERSION = "relaytic.paper_invariant_evidence_cell.v1"
PAPER_CLAIM_GATE_SCHEMA_VERSION = "relaytic.paper_claim_gate.v2"
PAPER_EVIDENCE_TYPE_SYSTEM_SCHEMA_VERSION = "relaytic.paper_evidence_type_system.v1"

COMMON_EVIDENCE_CELL_REQUIRED_FIELDS = (
    "cell_schema",
    "cell_id",
    "cell_type",
    "dataset_id",
    "split",
    "command",
    "artifact_ref",
    "artifact_field",
    "budget_tier",
    "leakage_posture",
)

METRIC_EVIDENCE_CELL_EXTENSION_FIELDS = (
    "metric",
    "value",
    "operating_point_applicability",
    "operating_point_ref",
    "calibration_status",
    "exposure_status",
    "model_identifier",
)

INVARIANT_EVIDENCE_CELL_EXTENSION_FIELDS = (
    "invariant_name",
    "invariant_state",
    "observed_value",
    "detector_performance_metric",
    "operating_point_applicability",
    "rowless_export_status",
)

METRIC_EVIDENCE_CELL_REQUIRED_FIELDS = (
    *COMMON_EVIDENCE_CELL_REQUIRED_FIELDS,
    *METRIC_EVIDENCE_CELL_EXTENSION_FIELDS,
)
INVARIANT_EVIDENCE_CELL_REQUIRED_FIELDS = (
    *COMMON_EVIDENCE_CELL_REQUIRED_FIELDS,
    *INVARIANT_EVIDENCE_CELL_EXTENSION_FIELDS,
)

# The disabled-field ablation removes the complete production metric-cell contract.
DISABLED_REQUIRED_FIELD_ABLATION_FIELDS = METRIC_EVIDENCE_CELL_REQUIRED_FIELDS

# The stress fixture preserves type identity, then omits every other required metric field.
MISSING_FIELD_STRESS_FIXTURE_PRESERVED_FIELDS = (
    "cell_schema",
    "cell_id",
    "cell_type",
)
MISSING_FIELD_STRESS_FIXTURE_OMITTED_FIELDS = tuple(
    field
    for field in METRIC_EVIDENCE_CELL_REQUIRED_FIELDS
    if field not in MISSING_FIELD_STRESS_FIXTURE_PRESERVED_FIELDS
)

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

CLAIM_GATE_REQUIRED_FIELDS = (
    "schema_version",
    "gate_id",
    "evidence_cell_ids",
    "admissible_use",
    "stronger_claim_status",
    "gate_reasons",
    "missing_evidence",
)


def evidence_cell_required_fields(cell_type: str) -> tuple[str, ...]:
    """Return the authoritative required fields for one evidence-cell type."""
    if cell_type == METRIC_EVIDENCE_CELL_TYPE:
        return METRIC_EVIDENCE_CELL_REQUIRED_FIELDS
    if cell_type == INVARIANT_EVIDENCE_CELL_TYPE:
        return INVARIANT_EVIDENCE_CELL_REQUIRED_FIELDS
    return ()


def evidence_cell_violations(cell: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Return deterministic type, schema, and factual-field violations."""
    present_interpretive = _interpretive_field_paths(cell)
    cell_type = str(cell.get("cell_type") or "")
    required_fields = evidence_cell_required_fields(cell_type)
    violations: list[dict[str, Any]] = []

    if present_interpretive:
        violations.append(
            {
                "violation": "interpretive_fields_in_evidence_cell",
                "fields": present_interpretive,
            }
        )
    if not required_fields:
        violations.append(
            {
                "violation": "untyped_evidence_cell",
                "observed_cell_type": cell_type or None,
            }
        )
        return violations

    expected_schema = (
        PAPER_METRIC_EVIDENCE_CELL_SCHEMA_VERSION
        if cell_type == METRIC_EVIDENCE_CELL_TYPE
        else PAPER_INVARIANT_EVIDENCE_CELL_SCHEMA_VERSION
    )
    if cell.get("cell_schema") != expected_schema:
        violations.append(
            {
                "violation": "evidence_cell_schema_type_mismatch",
                "expected": expected_schema,
                "observed": cell.get("cell_schema"),
            }
        )

    missing = [field for field in required_fields if not _has_required_value(cell.get(field))]
    if missing:
        violations.append(
            {
                "violation": "required_factual_fields_missing",
                "cell_type": cell_type,
                "fields": missing,
            }
        )

    if cell_type == METRIC_EVIDENCE_CELL_TYPE:
        invariant_fields = sorted(
            field
            for field in ("invariant_name", "invariant_state", "observed_value")
            if field in cell
        )
        if invariant_fields:
            violations.append(
                {
                    "violation": "metric_cell_contains_invariant_observation",
                    "fields": invariant_fields,
                }
            )
    else:
        detector_fields = sorted(field for field in ("metric", "metric_id", "value") if field in cell)
        if detector_fields or cell.get("detector_performance_metric") is not False:
            violations.append(
                {
                    "violation": "invariant_rendered_as_detector_performance",
                    "fields": detector_fields,
                    "detector_performance_metric": cell.get("detector_performance_metric"),
                }
            )
        if cell.get("operating_point_applicability") != "not_applicable":
            violations.append(
                {
                    "violation": "invariant_operating_point_must_be_not_applicable",
                    "observed": cell.get("operating_point_applicability"),
                }
            )
    return violations


def _has_required_value(value: Any) -> bool:
    return value not in (None, "", [])


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
    missing = [field for field in CLAIM_GATE_REQUIRED_FIELDS if not _has_required_value(gate.get(field))]
    references = [str(cell_id) for cell_id in gate.get("evidence_cell_ids", []) if cell_id]
    unknown = sorted(set(references).difference(known))
    violations: list[dict[str, Any]] = []
    if missing:
        violations.append({"violation": "required_gate_fields_missing", "fields": missing})
    if gate.get("schema_version") not in (None, PAPER_CLAIM_GATE_SCHEMA_VERSION):
        violations.append(
            {
                "violation": "claim_gate_schema_mismatch",
                "expected": PAPER_CLAIM_GATE_SCHEMA_VERSION,
                "observed": gate.get("schema_version"),
            }
        )
    if unknown:
        violations.append({"violation": "gate_references_missing_evidence_cells", "cell_ids": unknown})
    return violations


def audit_evidence_gate_separation(
    *,
    evidence_cells: Iterable[Mapping[str, Any]],
    claim_gates: Iterable[Mapping[str, Any]],
) -> dict[str, Any]:
    """Audit typed factual cells and bidirectional separate-gate coverage."""
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

    type_counts = {
        cell_type: sum(1 for cell in cells if cell.get("cell_type") == cell_type)
        for cell_type in (METRIC_EVIDENCE_CELL_TYPE, INVARIANT_EVIDENCE_CELL_TYPE)
    }
    return {
        "schema_version": "relaytic.paper_evidence_gate_audit.v2",
        "status": "pass" if not violations and bool(cells) and bool(gates) else "fail",
        "evidence_type_system_schema": PAPER_EVIDENCE_TYPE_SYSTEM_SCHEMA_VERSION,
        "metric_evidence_cell_schema": PAPER_METRIC_EVIDENCE_CELL_SCHEMA_VERSION,
        "invariant_evidence_cell_schema": PAPER_INVARIANT_EVIDENCE_CELL_SCHEMA_VERSION,
        "claim_gate_schema": PAPER_CLAIM_GATE_SCHEMA_VERSION,
        "evidence_cell_count": len(cells),
        "evidence_cell_type_counts": type_counts,
        "claim_gate_count": len(gates),
        "all_public_cells_have_separate_gate": not ungated,
        "violations": violations,
    }


def build_evidence_schema_contract() -> dict[str, Any]:
    """Materialize the authoritative fields and fixture-specific counts."""
    return {
        "schema_version": PAPER_EVIDENCE_TYPE_SYSTEM_SCHEMA_VERSION,
        "status": "pass",
        "cell_types": {
            METRIC_EVIDENCE_CELL_TYPE: {
                "cell_schema": PAPER_METRIC_EVIDENCE_CELL_SCHEMA_VERSION,
                "required_fields": list(METRIC_EVIDENCE_CELL_REQUIRED_FIELDS),
                "required_field_count": len(METRIC_EVIDENCE_CELL_REQUIRED_FIELDS),
            },
            INVARIANT_EVIDENCE_CELL_TYPE: {
                "cell_schema": PAPER_INVARIANT_EVIDENCE_CELL_SCHEMA_VERSION,
                "required_fields": list(INVARIANT_EVIDENCE_CELL_REQUIRED_FIELDS),
                "required_field_count": len(INVARIANT_EVIDENCE_CELL_REQUIRED_FIELDS),
            },
        },
        "claim_gate": {
            "schema_version": PAPER_CLAIM_GATE_SCHEMA_VERSION,
            "required_fields": list(CLAIM_GATE_REQUIRED_FIELDS),
            "required_field_count": len(CLAIM_GATE_REQUIRED_FIELDS),
        },
        "fixtures": {
            "disabled_required_fields_ablation": {
                "cell_type": METRIC_EVIDENCE_CELL_TYPE,
                "removed_fields": list(DISABLED_REQUIRED_FIELD_ABLATION_FIELDS),
                "removed_field_count": len(DISABLED_REQUIRED_FIELD_ABLATION_FIELDS),
            },
            "missing_field_stress_fixture": {
                "cell_type": METRIC_EVIDENCE_CELL_TYPE,
                "preserved_fields": list(MISSING_FIELD_STRESS_FIXTURE_PRESERVED_FIELDS),
                "omitted_fields": list(MISSING_FIELD_STRESS_FIXTURE_OMITTED_FIELDS),
                "omitted_field_count": len(MISSING_FIELD_STRESS_FIXTURE_OMITTED_FIELDS),
            },
        },
    }


__all__ = [
    "CLAIM_GATE_REQUIRED_FIELDS",
    "COMMON_EVIDENCE_CELL_REQUIRED_FIELDS",
    "DISABLED_REQUIRED_FIELD_ABLATION_FIELDS",
    "EVIDENCE_CELL_INTERPRETIVE_FIELDS",
    "INVARIANT_EVIDENCE_CELL_EXTENSION_FIELDS",
    "INVARIANT_EVIDENCE_CELL_REQUIRED_FIELDS",
    "INVARIANT_EVIDENCE_CELL_TYPE",
    "METRIC_EVIDENCE_CELL_EXTENSION_FIELDS",
    "METRIC_EVIDENCE_CELL_REQUIRED_FIELDS",
    "METRIC_EVIDENCE_CELL_TYPE",
    "MISSING_FIELD_STRESS_FIXTURE_OMITTED_FIELDS",
    "MISSING_FIELD_STRESS_FIXTURE_PRESERVED_FIELDS",
    "PAPER_CLAIM_GATE_SCHEMA_VERSION",
    "PAPER_EVIDENCE_TYPE_SYSTEM_SCHEMA_VERSION",
    "PAPER_INVARIANT_EVIDENCE_CELL_SCHEMA_VERSION",
    "PAPER_METRIC_EVIDENCE_CELL_SCHEMA_VERSION",
    "audit_evidence_gate_separation",
    "build_evidence_schema_contract",
    "claim_gate_violations",
    "evidence_cell_required_fields",
    "evidence_cell_violations",
]
