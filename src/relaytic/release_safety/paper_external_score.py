"""Paper Track P19-A external score-file governance proof pack."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from relaytic.core.json_utils import dumps_json, write_json
from relaytic.release_safety.paper_evidence_contract import (
    EVIDENCE_CELL_INTERPRETIVE_FIELDS,
    PAPER_CLAIM_GATE_SCHEMA_VERSION,
    PAPER_EVIDENCE_CELL_SCHEMA_VERSION,
    audit_evidence_gate_separation,
)


PAPER_EXTERNAL_SCORE_SCHEMA_VERSION = "relaytic.paper_external_score.v2"
PAPER_EXTERNAL_SCORE_REPORT_DIR = Path("docs") / "reports"
NEXT_PAPER_EXTERNAL_SCORE_SLICE = "Paper Track P19-B - external score case-study and paper integration"

PAPER_EXTERNAL_SCORE_FILENAMES = {
    "paper_external_score_route_decision": "paper_external_score_route_decision.json",
    "paper_external_score_schema": "paper_external_score_schema.json",
    "paper_external_score_manifest": "paper_external_score_manifest.json",
    "paper_external_score_evidence_cells": "paper_external_score_evidence_cells.json",
    "paper_external_score_claim_gate": "paper_external_score_claim_gate.json",
    "paper_external_score_handoff_eval": "paper_external_score_handoff_eval.json",
    "paper_external_score_summary": "paper_external_score_summary.md",
}

REQUIRED_EXTERNAL_SCORE_FIELDS = [
    "artifact_id",
    "dataset_id",
    "dataset_role",
    "split",
    "split_role",
    "score_artifact_type",
    "schema_fields",
    "metric",
    "leakage_posture",
]

FORBIDDEN_EXTERNAL_SCORE_FIELDS = [
    "raw_rows",
    "rows",
    "records",
    "entity_id",
    "entity_ids",
    "customer_id",
    "account_id",
    "transaction_id",
    "transaction_ids",
    "raw_scores",
    "scores",
    "local_path",
    "local_paths",
    "absolute_path",
    "secret",
    "token",
]

HOSTED_SCORE_ADMISSIBLE_USE = "hosted detector-output governance only"


def build_paper_external_score_pack(
    project_root: str | Path,
    *,
    score_artifact_path: str | Path | None = None,
    metadata_path: str | Path | None = None,
) -> dict[str, Any]:
    """Build the P19-A external-score governance proof pack.

    The default path uses a deterministic rowless fixture. If a local JSON artifact is
    supplied, only hashes, schema, metadata, and aggregate fields are written out.
    """
    root = Path(project_root)
    source = _load_score_source(root, score_artifact_path=score_artifact_path, metadata_path=metadata_path)
    normalized = _normalize_score_artifact(source)
    schema_report = _build_schema_report(source=source, normalized=normalized)
    evidence_cells = _build_evidence_cells(source=source, normalized=normalized, schema_report=schema_report)
    claim_gate = _build_claim_gate(source=source, normalized=normalized, schema_report=schema_report)
    separation_audit = audit_evidence_gate_separation(
        evidence_cells=evidence_cells.get("evidence_cells", []),
        claim_gates=[claim_gate] if claim_gate.get("publishable") else [],
    )
    evidence_cells["evidence_gate_separation"] = separation_audit
    handoff_eval = _build_handoff_eval(source=source, normalized=normalized, schema_report=schema_report)
    route_decision = _build_route_decision(
        source=source,
        normalized=normalized,
        schema_report=schema_report,
        claim_gate=claim_gate,
        handoff_eval=handoff_eval,
    )
    manifest = _build_manifest(
        source=source,
        normalized=normalized,
        schema_report=schema_report,
        evidence_cells=evidence_cells,
        claim_gate=claim_gate,
        handoff_eval=handoff_eval,
        route_decision=route_decision,
    )
    pack = {
        "paper_external_score_route_decision": route_decision,
        "paper_external_score_schema": schema_report,
        "paper_external_score_manifest": manifest,
        "paper_external_score_evidence_cells": evidence_cells,
        "paper_external_score_claim_gate": claim_gate,
        "paper_external_score_handoff_eval": handoff_eval,
    }
    pack["paper_external_score_summary"] = render_paper_external_score_markdown(pack)
    return pack


def sync_paper_external_score_pack(
    project_root: str | Path,
    *,
    score_artifact_path: str | Path | None = None,
    metadata_path: str | Path | None = None,
    output_dir: str | Path | None = None,
) -> dict[str, Path]:
    """Write P19-A external-score reports under docs/reports."""
    root = Path(project_root)
    report_dir = Path(output_dir) if output_dir is not None else root / PAPER_EXTERNAL_SCORE_REPORT_DIR
    report_dir.mkdir(parents=True, exist_ok=True)
    pack = build_paper_external_score_pack(
        root,
        score_artifact_path=score_artifact_path,
        metadata_path=metadata_path,
    )
    written: dict[str, Path] = {}
    for key, filename in PAPER_EXTERNAL_SCORE_FILENAMES.items():
        path = report_dir / filename
        if filename.endswith(".md"):
            path.write_text(str(pack[key]), encoding="utf-8")
            written[key] = path
        else:
            written[key] = write_json(path, pack[key], indent=2, sort_keys=True)
    return written


def render_paper_external_score_markdown(pack: dict[str, Any]) -> str:
    manifest = dict(pack.get("paper_external_score_manifest", {}))
    route = dict(pack.get("paper_external_score_route_decision", {}))
    schema = dict(pack.get("paper_external_score_schema", {}))
    gate = dict(pack.get("paper_external_score_claim_gate", {}))
    handoff = dict(pack.get("paper_external_score_handoff_eval", {}))
    cells = list(dict(pack.get("paper_external_score_evidence_cells", {})).get("evidence_cells", []))
    lines = [
        "# Paper P19-A External Score-File Proof Pack",
        "",
        f"- Status: `{manifest.get('status') or 'unknown'}`",
        f"- Selected route: `{route.get('selected_route') or 'unknown'}`",
        f"- Score artifact accepted: `{schema.get('accepted')}`",
        f"- Required metadata completeness: `{schema.get('required_metadata_completeness')}`",
        f"- Claim gate publishable: `{gate.get('publishable')}`",
        f"- Rowless handoff passed: `{handoff.get('rowless_handoff_passed')}`",
        f"- Next slice: `{manifest.get('next_slice') or 'unknown'}`",
        "",
        "## Evidence Cells",
        "",
        "| Cell | Dataset | Split | Metric | Value | Rowless |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for cell in cells:
        if not isinstance(cell, dict):
            continue
        lines.append(
            "| "
            + " | ".join(
                [
                    _escape_md(str(cell.get("cell_id") or "")),
                    _escape_md(str(cell.get("dataset_id") or "")),
                    _escape_md(str(cell.get("split") or "")),
                    _escape_md(str(cell.get("metric") or "")),
                    _escape_md(str(cell.get("value") or "")),
                    _escape_md(str(cell.get("rowless") or "")),
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            f"- Allowed wording: `{gate.get('allowed_claim_scope') or 'unknown'}`",
            f"- Blocked stronger claims: `{len(gate.get('blocked_claims', []))}`",
            f"- Redacted handoff fields: `{len(handoff.get('redacted_fields', []))}`",
            "",
            "## Reproduction",
            "",
            "- Windows: `py -3.11 -m relaytic.ui.cli release-safety paper-external-score-proof --format json`",
            "- macOS/Linux: `python -m relaytic.ui.cli release-safety paper-external-score-proof --format json`",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def _load_score_source(
    root: Path,
    *,
    score_artifact_path: str | Path | None,
    metadata_path: str | Path | None,
) -> dict[str, Any]:
    if score_artifact_path is None:
        fixture = _default_score_fixture()
        content = _json_canonical(fixture)
        return {
            "source_kind": "deterministic_rowless_fixture",
            "artifact_ref": "fixture:p19a_external_score_rowless_v1",
            "exists": True,
            "parse_error": None,
            "input_filename": "p19a_external_score_rowless_fixture.json",
            "content": fixture,
            "content_hash": _sha256_text(content),
            "content_hash_prefix": _sha256_text(content)[:12],
            "metadata_source": "embedded_fixture",
            "metadata_exists": True,
        }

    score_path = Path(score_artifact_path)
    if not score_path.is_absolute():
        score_path = root / score_path
    source = {
        "source_kind": "local_json_score_artifact",
        "artifact_ref": f"local_json_score_artifact:{score_path.name}",
        "exists": score_path.exists(),
        "parse_error": None,
        "input_filename": score_path.name,
        "content": {},
        "content_hash": None,
        "content_hash_prefix": None,
        "metadata_source": "artifact",
        "metadata_exists": metadata_path is None,
    }
    if not score_path.exists():
        return source
    raw = score_path.read_text(encoding="utf-8")
    source["content_hash"] = _sha256_text(raw)
    source["content_hash_prefix"] = str(source["content_hash"])[:12]
    try:
        content = json.loads(raw)
    except json.JSONDecodeError as exc:
        source["parse_error"] = f"invalid_json:{exc.msg}"
        return source
    if not isinstance(content, dict):
        source["parse_error"] = "json_root_must_be_object"
        return source

    if metadata_path is not None:
        metadata_file = Path(metadata_path)
        if not metadata_file.is_absolute():
            metadata_file = root / metadata_file
        source["metadata_source"] = f"local_json_metadata:{metadata_file.name}"
        source["metadata_exists"] = metadata_file.exists()
        if metadata_file.exists():
            try:
                metadata = json.loads(metadata_file.read_text(encoding="utf-8"))
            except json.JSONDecodeError as exc:
                source["parse_error"] = f"invalid_metadata_json:{exc.msg}"
                metadata = {}
            if isinstance(metadata, dict):
                content = {**content, "metadata": {**dict(content.get("metadata") or {}), **metadata}}
            else:
                source["parse_error"] = "metadata_json_root_must_be_object"

    source["content"] = content
    return source


def _default_score_fixture() -> dict[str, Any]:
    return {
        "artifact_id": "p19a_external_score_rowless_fixture_v1",
        "dataset_id": "p19a_hosted_score_fixture",
        "dataset_role": "deterministic_system_fixture",
        "split": "fixture_holdout",
        "split_role": "fixed_evaluation_surface",
        "score_artifact_type": "rowless_detector_score_summary",
        "producer": {
            "kind": "external_detector_output",
            "training_visibility": "unknown_to_relaytic",
            "relaytic_role": "host_and_govern_output_only",
        },
        "schema_fields": [
            {"name": "risk_score", "dtype": "float", "role": "score_summary", "rowless": True},
            {"name": "score_count", "dtype": "integer", "role": "aggregate_count", "rowless": True},
            {"name": "split_role", "dtype": "string", "role": "evaluation_metadata", "rowless": True},
        ],
        "metric": {
            "name": "hosted_score_metadata_completeness",
            "value": 1.0,
            "unit": "fraction",
            "role": "governance_metric",
            "detector_performance_metric": False,
        },
        "leakage_posture": "rowless_no_training_or_label_data_exported",
        "payload_summary": {
            "score_count": 1200,
            "row_count": 1200,
            "score_min": 0.0,
            "score_max": 1.0,
            "raw_rows_in_artifact": False,
            "entity_identifiers_in_artifact": False,
        },
        "handoff_policy": {
            "rowless": True,
            "allowed_fields": [
                "artifact_id",
                "dataset_id",
                "dataset_role",
                "split",
                "split_role",
                "metric",
                "value",
                "schema_hash",
                "content_hash_prefix",
                "leakage_posture",
                "claim_gate_ref",
            ],
            "redact_fields": FORBIDDEN_EXTERNAL_SCORE_FIELDS,
        },
    }


def _normalize_score_artifact(source: dict[str, Any]) -> dict[str, Any]:
    content = dict(source.get("content") or {})
    metadata = dict(content.get("metadata") or {})
    merged = {**content, **metadata}
    metric = dict(merged.get("metric") or {})
    schema_fields = list(merged.get("schema_fields") or [])
    required_missing = [
        field
        for field in REQUIRED_EXTERNAL_SCORE_FIELDS
        if not _has_required_value(merged.get(field))
    ]
    forbidden_hits = _find_forbidden_fields(merged)
    interpretive_field_hits = _find_named_fields(merged, EVIDENCE_CELL_INTERPRETIVE_FIELDS)
    schema_fingerprint = {
        "artifact_id": merged.get("artifact_id"),
        "score_artifact_type": merged.get("score_artifact_type"),
        "schema_fields": schema_fields,
        "metric_name": metric.get("name"),
        "metric_role": metric.get("role"),
    }
    return {
        "artifact_id": str(merged.get("artifact_id") or ""),
        "dataset_id": str(merged.get("dataset_id") or ""),
        "dataset_role": str(merged.get("dataset_role") or ""),
        "split": str(merged.get("split") or ""),
        "split_role": str(merged.get("split_role") or ""),
        "score_artifact_type": str(merged.get("score_artifact_type") or ""),
        "schema_fields": schema_fields,
        "metric": metric,
        "leakage_posture": str(merged.get("leakage_posture") or ""),
        "payload_summary": dict(merged.get("payload_summary") or {}),
        "handoff_policy": dict(merged.get("handoff_policy") or {}),
        "required_missing": required_missing,
        "required_present_count": len(REQUIRED_EXTERNAL_SCORE_FIELDS) - len(required_missing),
        "forbidden_field_hits": forbidden_hits,
        "interpretive_field_hits": interpretive_field_hits,
        "schema_hash": _sha256_text(_json_canonical(schema_fingerprint)),
        "schema_hash_prefix": _sha256_text(_json_canonical(schema_fingerprint))[:12],
        "metric_name": str(metric.get("name") or ""),
        "metric_value": metric.get("value"),
        "metric_role": str(metric.get("role") or ""),
    }


def _build_schema_report(*, source: dict[str, Any], normalized: dict[str, Any]) -> dict[str, Any]:
    parse_ok = bool(source.get("exists")) and not source.get("parse_error")
    metadata_complete = not normalized["required_missing"]
    rowless_input = not normalized["forbidden_field_hits"]
    factual_input = not normalized["interpretive_field_hits"]
    accepted = parse_ok and metadata_complete and rowless_input and factual_input
    return {
        "schema_version": PAPER_EXTERNAL_SCORE_SCHEMA_VERSION,
        "status": "pass" if accepted else "blocked",
        "accepted": accepted,
        "source_kind": source.get("source_kind"),
        "artifact_ref": source.get("artifact_ref"),
        "input_filename": source.get("input_filename"),
        "input_exists": bool(source.get("exists")),
        "parse_error": source.get("parse_error"),
        "content_hash_prefix": source.get("content_hash_prefix"),
        "schema_hash": normalized["schema_hash"],
        "schema_hash_prefix": normalized["schema_hash_prefix"],
        "required_fields": REQUIRED_EXTERNAL_SCORE_FIELDS,
        "required_missing": normalized["required_missing"],
        "required_present_count": normalized["required_present_count"],
        "required_metadata_completeness": round(
            normalized["required_present_count"] / len(REQUIRED_EXTERNAL_SCORE_FIELDS),
            6,
        ),
        "forbidden_fields_detected": normalized["forbidden_field_hits"],
        "rowless_input": rowless_input,
        "factual_input": factual_input,
        "interpretive_fields_detected": normalized["interpretive_field_hits"],
        "schema_fields": _schema_field_summaries(normalized["schema_fields"]),
        "metric": {
            "name": normalized["metric_name"],
            "value": normalized["metric_value"],
            "role": normalized["metric_role"],
            "detector_performance_metric": bool(normalized["metric"].get("detector_performance_metric")),
        },
        "leakage_posture": normalized["leakage_posture"],
    }


def _build_evidence_cells(
    *,
    source: dict[str, Any],
    normalized: dict[str, Any],
    schema_report: dict[str, Any],
) -> dict[str, Any]:
    accepted = bool(schema_report["accepted"])
    cell = {
        "cell_schema": PAPER_EVIDENCE_CELL_SCHEMA_VERSION,
        "cell_id": "p19a.external_score.hosted_metadata_completeness",
        "dataset_id": normalized["dataset_id"],
        "dataset_role": normalized["dataset_role"],
        "split": normalized["split"],
        "split_role": normalized["split_role"],
        "command": "relaytic release-safety paper-external-score-proof",
        "artifact_ref": source.get("artifact_ref"),
        "artifact_hash_prefix": source.get("content_hash_prefix"),
        "schema_hash_prefix": normalized["schema_hash_prefix"],
        "metric": normalized["metric_name"],
        "value": normalized["metric_value"],
        "metric_role": normalized["metric_role"],
        "detector_performance_metric": bool(normalized["metric"].get("detector_performance_metric")),
        "budget_tier": "deterministic_fixture",
        "leakage_posture": normalized["leakage_posture"],
        "invariant_state": "pass" if accepted else "blocked",
        "rowless": bool(schema_report["rowless_input"]),
        "rowless_export_status": "rowless" if bool(schema_report["rowless_input"]) else "blocked",
        "source_posture": source.get("source_kind"),
    }
    return {
        "schema_version": PAPER_EXTERNAL_SCORE_SCHEMA_VERSION,
        "status": "pass" if accepted else "blocked",
        "evidence_cell_count": 1 if accepted else 0,
        "evidence_cells": [cell] if accepted else [],
        "blocked_cell": None if accepted else cell,
        "required_cell_fields": [
            "cell_id",
            "dataset_id",
            "split",
            "command",
            "artifact_ref",
            "metric",
            "value",
            "leakage_posture",
            "budget_tier",
        ],
    }


def _build_claim_gate(
    *,
    source: dict[str, Any],
    normalized: dict[str, Any],
    schema_report: dict[str, Any],
) -> dict[str, Any]:
    checks = [
        _check(
            "score_artifact_exists",
            bool(source.get("exists")),
            f"exists={bool(source.get('exists'))}",
            "score artifact or deterministic fixture is available",
        ),
        _check(
            "score_artifact_parseable",
            not source.get("parse_error"),
            f"parse_error={source.get('parse_error')}",
            "score artifact parses as JSON object",
        ),
        _check(
            "required_metadata_complete",
            not normalized["required_missing"],
            f"missing={len(normalized['required_missing'])}",
            "artifact carries dataset, split, schema, metric, and leakage metadata",
        ),
        _check(
            "rowless_input_contract",
            not normalized["forbidden_field_hits"],
            f"forbidden_fields={len(normalized['forbidden_field_hits'])}",
            "artifact does not expose raw rows, identifiers, local paths, secrets, or raw score payloads",
        ),
        _check(
            "factual_input_has_no_interpretive_fields",
            not normalized["interpretive_field_hits"],
            f"interpretive_fields={len(normalized['interpretive_field_hits'])}",
            "the factual score record does not carry claim or publication fields",
        ),
        _check(
            "detector_performance_not_promoted",
            not bool(normalized["metric"].get("detector_performance_metric")),
            f"detector_performance_metric={bool(normalized['metric'].get('detector_performance_metric'))}",
            "P19-A does not promote detector-performance metrics",
        ),
    ]
    publishable = all(check["passed"] for check in checks)
    return {
        "schema_version": PAPER_CLAIM_GATE_SCHEMA_VERSION,
        "gate_id": "p19a.external_score.hosted_output_gate",
        "evidence_cell_ids": ["p19a.external_score.hosted_metadata_completeness"] if publishable else [],
        "status": "pass" if publishable else "blocked",
        "publishable": publishable,
        "allowed_claim_scope": "hosted_detector_output_governance_only",
        "admissible_use": HOSTED_SCORE_ADMISSIBLE_USE,
        "stronger_claim_status": "blocked",
        "gate_reasons": [
            "the fixture measures hosted-score metadata completeness rather than detector performance",
            "raw rows and entity identifiers are excluded from the export",
        ],
        "missing_evidence": [
            "independent detector benchmark comparison",
            "production controls and analyst outcome study",
        ],
        "checks": checks,
        "failed_checks": [check["check_id"] for check in checks if not check["passed"]],
        "allowed_public_claims": [
            "Relaytic-AML can convert a rowless external detector-score artifact into a factual evidence cell plus a separate interpretation gate.",
            "Relaytic-AML can produce a rowless handoff summary for hosted detector-output governance.",
        ]
        if publishable
        else [],
        "blocked_claims": [
            {
                "claim": "The imported detector is superior to current AML detectors.",
                "reason": "P19-A validates governance of an external score artifact, not detector performance.",
                "missing_evidence": "independent benchmark comparison under a validated detector budget",
            },
            {
                "claim": "Relaytic-AML is production-ready for bank AML monitoring.",
                "reason": "No production deployment, analyst study, or bank validation exists.",
                "missing_evidence": "production controls, live data validation, and human analyst outcome study",
            },
            {
                "claim": "Relaytic-AML introduces graph-neural detector novelty.",
                "reason": "The route hosts external detector outputs and does not implement a new graph-neural model.",
                "missing_evidence": "new detector architecture plus benchmark and ablation evidence",
            },
            {
                "claim": "Relaytic-AML reaches RevClassifyDS parity.",
                "reason": "No faithful RevClassifyDS parity run is executed in P19-A.",
                "missing_evidence": "faithful reference replay or accepted parity protocol",
            },
            {
                "claim": "Relaytic-AML proves real-bank AML superiority.",
                "reason": "The artifact is rowless governance evidence, not real-bank detector validation.",
                "missing_evidence": "licensed real-bank data, approved evaluation protocol, and independent validation",
            },
        ],
        "detector_superiority_claimed": False,
        "production_aml_readiness_claimed": False,
        "graph_neural_detector_novelty_claimed": False,
        "revclassify_parity_claimed": False,
        "hard_real_bank_aml_superiority_claimed": False,
    }


def _build_handoff_eval(
    *,
    source: dict[str, Any],
    normalized: dict[str, Any],
    schema_report: dict[str, Any],
) -> dict[str, Any]:
    policy = dict(normalized.get("handoff_policy") or {})
    allowed_fields = list(policy.get("allowed_fields") or [])
    if not allowed_fields:
        allowed_fields = [
            "artifact_id",
            "dataset_id",
            "dataset_role",
            "split",
            "split_role",
            "metric",
            "value",
            "schema_hash",
            "content_hash_prefix",
            "leakage_posture",
            "claim_gate_ref",
        ]
    redacted_fields = list(dict.fromkeys(list(policy.get("redact_fields") or []) + FORBIDDEN_EXTERNAL_SCORE_FIELDS))
    exported_payload = {
        "artifact_id": normalized["artifact_id"],
        "dataset_id": normalized["dataset_id"],
        "dataset_role": normalized["dataset_role"],
        "split": normalized["split"],
        "split_role": normalized["split_role"],
        "metric": normalized["metric_name"],
        "value": normalized["metric_value"],
        "schema_hash_prefix": normalized["schema_hash_prefix"],
        "content_hash_prefix": source.get("content_hash_prefix"),
        "leakage_posture": normalized["leakage_posture"],
        "claim_gate_ref": "p19a.external_score.hosted_output_gate",
    }
    rowless_handoff = bool(schema_report["rowless_input"]) and not any(
        field in exported_payload for field in redacted_fields
    )
    return {
        "schema_version": PAPER_EXTERNAL_SCORE_SCHEMA_VERSION,
        "status": "pass" if bool(schema_report["accepted"]) and rowless_handoff else "blocked",
        "rowless_handoff_passed": bool(schema_report["accepted"]) and rowless_handoff,
        "exported_field_count": len(exported_payload),
        "exported_fields": sorted(exported_payload.keys()),
        "redacted_field_count": len(redacted_fields),
        "redacted_fields": sorted(redacted_fields),
        "blocked_fields": sorted(redacted_fields),
        "raw_rows_exported": False,
        "entity_identifiers_exported": False,
        "private_paths_exported": False,
        "secrets_exported": False,
        "unapproved_score_payload_fields_exported": False,
        "handoff_payload_preview": exported_payload if bool(schema_report["accepted"]) else {},
        "source_path_recorded": False,
        "input_filename_recorded": bool(source.get("input_filename")),
        "input_absolute_path_recorded": False,
        "pass_criterion": "only schema, hash prefixes, factual metadata, governance metric, leakage posture, and a gate reference are exported",
    }


def _build_route_decision(
    *,
    source: dict[str, Any],
    normalized: dict[str, Any],
    schema_report: dict[str, Any],
    claim_gate: dict[str, Any],
    handoff_eval: dict[str, Any],
) -> dict[str, Any]:
    selected = bool(schema_report["accepted"]) and bool(claim_gate["publishable"]) and bool(
        handoff_eval["rowless_handoff_passed"]
    )
    return {
        "schema_version": PAPER_EXTERNAL_SCORE_SCHEMA_VERSION,
        "status": "selected" if selected else "blocked",
        "selected_route": "external_score_file_adapter" if selected else None,
        "preferred_route": "external_score_file_adapter",
        "route_reason": (
            "The external score route proves Relaytic-AML can host detector-output evidence without claiming detector novelty."
            if selected
            else "The route remains blocked until required score metadata, rowless posture, and evidence/gate separation pass."
        ),
        "alternatives": [
            {
                "route": "lightweight_graph_native_fixture",
                "decision": "not_selected",
                "reason": "Would shift attention toward detector mechanics rather than hosted-output governance.",
            },
            {
                "route": "revclassifyds_style_scorecard_adapter",
                "decision": "not_selected",
                "reason": "Would invite parity interpretation without faithful reference replay evidence.",
            },
            {
                "route": "skip_hosted_score_workflow",
                "decision": "not_selected" if selected else "available_fallback",
                "reason": "Use only if no safe score artifact can be governed.",
            },
        ],
        "input_artifact_ref": source.get("artifact_ref"),
        "artifact_id": normalized["artifact_id"],
        "dataset_id": normalized["dataset_id"],
        "split": normalized["split"],
        "claim_gate_ref": "p19a.external_score.hosted_output_gate",
        "paper_claim_boundary": "hosted detector-output governance, not detector superiority",
        "next_slice": NEXT_PAPER_EXTERNAL_SCORE_SLICE if selected else "Paper Track P20 - narrative and visual polish",
    }


def _build_manifest(
    *,
    source: dict[str, Any],
    normalized: dict[str, Any],
    schema_report: dict[str, Any],
    evidence_cells: dict[str, Any],
    claim_gate: dict[str, Any],
    handoff_eval: dict[str, Any],
    route_decision: dict[str, Any],
) -> dict[str, Any]:
    checks = [
        _check(
            "route_selected",
            route_decision["status"] == "selected",
            f"status={route_decision['status']}",
            "external score-file adapter route is selected",
        ),
        _check(
            "score_schema_accepted",
            bool(schema_report["accepted"]),
            f"accepted={schema_report['accepted']}",
            "score artifact has required factual schema, metadata, and rowless posture",
        ),
        _check(
            "evidence_cells_created",
            evidence_cells["evidence_cell_count"] >= 1,
            f"count={evidence_cells['evidence_cell_count']}",
            "at least one evidence cell is emitted",
        ),
        _check(
            "evidence_and_claim_gate_separate",
            dict(evidence_cells.get("evidence_gate_separation") or {}).get("status") == "pass",
            f"status={dict(evidence_cells.get('evidence_gate_separation') or {}).get('status')}",
            "factual evidence fields and interpretive gate fields are stored in separate records",
        ),
        _check(
            "claim_gate_publishable",
            bool(claim_gate["publishable"]),
            f"publishable={claim_gate['publishable']}",
            "claim gate allows only hosted-detector-output governance wording",
        ),
        _check(
            "rowless_handoff_redaction_passed",
            bool(handoff_eval["rowless_handoff_passed"]),
            f"redacted={handoff_eval['redacted_field_count']}; exported={handoff_eval['exported_field_count']}",
            "handoff redacts rows, identifiers, private paths, raw scores, and secrets",
        ),
    ]
    status = "ready_for_hosted_score_governance" if all(check["passed"] for check in checks) else "blocked_pending_p19a_metadata"
    return {
        "schema_version": PAPER_EXTERNAL_SCORE_SCHEMA_VERSION,
        "status": status,
        "slice": "Paper Track P19-A",
        "next_slice": NEXT_PAPER_EXTERNAL_SCORE_SLICE if status == "ready_for_hosted_score_governance" else "Paper Track P20 - narrative and visual polish",
        "command": "relaytic release-safety paper-external-score-proof",
        "reports": PAPER_EXTERNAL_SCORE_FILENAMES,
        "checks": checks,
        "failed_checks": [check["check_id"] for check in checks if not check["passed"]],
        "input_summary": {
            "source_kind": source.get("source_kind"),
            "artifact_ref": source.get("artifact_ref"),
            "input_filename": source.get("input_filename"),
            "input_exists": bool(source.get("exists")),
            "metadata_source": source.get("metadata_source"),
            "metadata_exists": bool(source.get("metadata_exists")),
            "content_hash_prefix": source.get("content_hash_prefix"),
            "schema_hash_prefix": normalized["schema_hash_prefix"],
        },
        "claim_boundary": {
            "allowed": "hosted_detector_output_governance_only",
            "detector_superiority_claimed": False,
            "production_aml_readiness_claimed": False,
            "graph_neural_detector_novelty_claimed": False,
            "revclassify_parity_claimed": False,
            "hard_real_bank_aml_superiority_claimed": False,
        },
        "no_private_data_posture": {
            "raw_rows_written": False,
            "entity_identifiers_written": False,
            "absolute_paths_written": False,
            "secrets_written": False,
            "licensed_data_written": False,
        },
    }


def _check(check_id: str, passed: bool, observed: str, requirement: str) -> dict[str, Any]:
    return {
        "check_id": check_id,
        "passed": bool(passed),
        "observed": observed,
        "requirement": requirement,
    }


def _schema_field_summaries(fields: list[Any]) -> list[dict[str, Any]]:
    summaries: list[dict[str, Any]] = []
    for item in fields:
        if isinstance(item, dict):
            summaries.append(
                {
                    "name": str(item.get("name") or ""),
                    "dtype": str(item.get("dtype") or ""),
                    "role": str(item.get("role") or ""),
                    "rowless": bool(item.get("rowless", True)),
                }
            )
        else:
            summaries.append({"name": str(item), "dtype": "unknown", "role": "unknown", "rowless": True})
    return summaries


def _find_forbidden_fields(value: Any, *, prefix: str = "") -> list[str]:
    hits: list[str] = []
    forbidden = {field.lower() for field in FORBIDDEN_EXTERNAL_SCORE_FIELDS}
    if isinstance(value, dict):
        for key, item in value.items():
            key_text = str(key)
            path = f"{prefix}.{key_text}" if prefix else key_text
            if key_text.lower() in forbidden:
                hits.append(path)
            hits.extend(_find_forbidden_fields(item, prefix=path))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            hits.extend(_find_forbidden_fields(item, prefix=f"{prefix}[{index}]"))
    return hits


def _find_named_fields(value: Any, names: set[str] | frozenset[str], *, prefix: str = "") -> list[str]:
    hits: list[str] = []
    normalized_names = {name.lower() for name in names}
    if isinstance(value, dict):
        for key, item in value.items():
            key_text = str(key)
            path = f"{prefix}.{key_text}" if prefix else key_text
            if key_text.lower() in normalized_names:
                hits.append(path)
            hits.extend(_find_named_fields(item, names, prefix=path))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            hits.extend(_find_named_fields(item, names, prefix=f"{prefix}[{index}]"))
    return hits


def _has_required_value(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, dict)):
        return bool(value)
    return True


def _json_canonical(value: Any) -> str:
    return dumps_json(value, sort_keys=True, ensure_ascii=True)


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _escape_md(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")
