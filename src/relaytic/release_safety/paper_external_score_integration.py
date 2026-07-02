"""Paper Track P19-B hosted-score case-study integration pack."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from relaytic.core.json_utils import write_json


PAPER_EXTERNAL_SCORE_INTEGRATION_SCHEMA_VERSION = "relaytic.paper_external_score_integration.v1"
PAPER_EXTERNAL_SCORE_INTEGRATION_REPORT_DIR = Path("docs") / "reports"
NEXT_PAPER_EXTERNAL_SCORE_INTEGRATION_SLICE = (
    "Paper Track P20 - PaySim selection-story cleanup and paper visual/narrative polish"
)

PAPER_EXTERNAL_SCORE_INTEGRATION_FILENAMES = {
    "paper_external_score_case_study": "paper_external_score_case_study.json",
    "paper_external_score_paper_panel": "paper_external_score_paper_panel.json",
    "paper_external_score_claim_map": "paper_external_score_claim_map.json",
    "paper_external_score_repro_card": "paper_external_score_repro_card.md",
    "paper_external_score_integration_manifest": "paper_external_score_integration_manifest.json",
}

REQUIRED_PAPER_EXTERNAL_SCORE_INPUT_REFS = [
    "docs/reports/paper_external_score_route_decision.json",
    "docs/reports/paper_external_score_schema.json",
    "docs/reports/paper_external_score_manifest.json",
    "docs/reports/paper_external_score_evidence_cells.json",
    "docs/reports/paper_external_score_claim_gate.json",
    "docs/reports/paper_external_score_handoff_eval.json",
]


def build_paper_external_score_integration_pack(
    project_root: str | Path,
    *,
    source_report_dir: str | Path | None = None,
) -> dict[str, Any]:
    """Build the P19-B paper-facing hosted-score case-study pack."""
    root = Path(project_root)
    report_dir = (
        Path(source_report_dir)
        if source_report_dir is not None
        else root / PAPER_EXTERNAL_SCORE_INTEGRATION_REPORT_DIR
    )
    inputs = _load_p19a_inputs(report_dir)
    case_study = _build_case_study(inputs)
    paper_panel = _build_paper_panel(case_study)
    claim_map = _build_claim_map(case_study)
    repro_card = render_paper_external_score_repro_card(case_study)
    manifest = _build_manifest(
        inputs=inputs,
        case_study=case_study,
        paper_panel=paper_panel,
        claim_map=claim_map,
        repro_card=repro_card,
    )
    pack = {
        "paper_external_score_case_study": case_study,
        "paper_external_score_paper_panel": paper_panel,
        "paper_external_score_claim_map": claim_map,
        "paper_external_score_repro_card": repro_card,
        "paper_external_score_integration_manifest": manifest,
    }
    return pack


def sync_paper_external_score_integration_pack(
    project_root: str | Path,
    *,
    source_report_dir: str | Path | None = None,
    output_dir: str | Path | None = None,
) -> dict[str, Path]:
    """Write P19-B case-study reports under docs/reports."""
    root = Path(project_root)
    report_dir = Path(output_dir) if output_dir is not None else root / PAPER_EXTERNAL_SCORE_INTEGRATION_REPORT_DIR
    report_dir.mkdir(parents=True, exist_ok=True)
    pack = build_paper_external_score_integration_pack(root, source_report_dir=source_report_dir)
    written: dict[str, Path] = {}
    for key, filename in PAPER_EXTERNAL_SCORE_INTEGRATION_FILENAMES.items():
        path = report_dir / filename
        if filename.endswith(".md"):
            path.write_text(str(pack[key]), encoding="utf-8")
            written[key] = path
        else:
            written[key] = write_json(path, pack[key], indent=2, sort_keys=True)
    return written


def render_paper_external_score_integration_markdown(pack: dict[str, Any]) -> str:
    manifest = dict(pack.get("paper_external_score_integration_manifest", {}))
    case_study = dict(pack.get("paper_external_score_case_study", {}))
    panel = dict(pack.get("paper_external_score_paper_panel", {}))
    claim_map = dict(pack.get("paper_external_score_claim_map", {}))
    rows = [row for row in panel.get("rows", []) if isinstance(row, dict)]
    lines = [
        "# Paper P19-B Hosted-Score Case Study Integration",
        "",
        f"- Status: `{manifest.get('status') or 'unknown'}`",
        f"- Case study: `{case_study.get('case_id') or 'unknown'}`",
        f"- Paper integration allowed: `{manifest.get('paper_integration_allowed')}`",
        f"- Evidence cells cited: `{len(case_study.get('evidence_cell_ids', []))}`",
        f"- Blocked stronger claims: `{len(case_study.get('blocked_stronger_claims', []))}`",
        f"- Next slice: `{manifest.get('next_slice') or 'unknown'}`",
        "",
        "## Paper Panel",
        "",
        "| Component | Observed evidence | Reader takeaway |",
        "| --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            "| "
            + " | ".join(
                [
                    _escape_md(str(row.get("component") or "")),
                    _escape_md(str(row.get("observed") or "")),
                    _escape_md(str(row.get("reader_takeaway") or "")),
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            f"- Allowed scope: `{claim_map.get('allowed_claim_scope') or 'unknown'}`",
            f"- Detector superiority allowed: `{claim_map.get('detector_superiority_allowed')}`",
            f"- Production AML readiness allowed: `{claim_map.get('production_aml_readiness_allowed')}`",
            f"- RevClassifyDS parity allowed: `{claim_map.get('revclassifyds_parity_allowed')}`",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def render_paper_external_score_repro_card(case_study: dict[str, Any]) -> str:
    snippet = dict(case_study.get("auditable_record_snippet", {}))
    adapter = dict(case_study.get("adapter_input_contract", {}))
    lines = [
        "# Paper P19-B Hosted-Score Reproducibility Card",
        "",
        (
            "This card regenerates the hosted external-score governance proof and the paper-facing case-study "
            "artifacts. It uses the repo-local rowless fixture by default and does not require PaySim, Elliptic, "
            "or Elliptic2 data."
        ),
        "",
        "Windows PowerShell:",
        "",
        "```powershell",
        "py -3.11 -m relaytic.ui.cli release-safety paper-external-score-proof --format json",
        "py -3.11 -m relaytic.ui.cli release-safety paper-external-score-integration --format json",
        "py -3.11 -m relaytic.ui.cli release-safety paper-release --format json",
        "```",
        "",
        "macOS/Linux:",
        "",
        "```bash",
        "python3 -m relaytic.ui.cli release-safety paper-external-score-proof --format json",
        "python3 -m relaytic.ui.cli release-safety paper-external-score-integration --format json",
        "python3 -m relaytic.ui.cli release-safety paper-release --format json",
        "```",
        "",
        "Expected outputs:",
        "",
    ]
    for filename in PAPER_EXTERNAL_SCORE_INTEGRATION_FILENAMES.values():
        lines.append(f"- `docs/reports/{filename}`")
    lines.extend(
        [
            "",
            "Data and privacy boundary:",
            "",
            "- The default fixture is rowless and contains no raw transactions, identifiers, secrets, licensed data, or private machine paths.",
            (
                "- Optional local score artifacts remain local. Relaytic records only schema fields, hash prefixes, "
                "metric policy, leakage posture, claim state, and redaction evidence."
            ),
            "",
            "Evidence identifiers:",
            "",
            f"- Evidence cell: `{snippet.get('cell_id') or 'not_available'}`",
            f"- Dataset: `{snippet.get('dataset_id') or 'not_available'}`",
            f"- Split: `{snippet.get('split') or 'not_available'}`",
            f"- Schema hash prefix: `{adapter.get('schema_hash_prefix') or 'not_available'}`",
            f"- Content hash prefix: `{adapter.get('content_hash_prefix') or 'not_available'}`",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def _load_p19a_inputs(report_dir: Path) -> dict[str, Any]:
    return {
        "route_decision": _read_artifact(report_dir / "paper_external_score_route_decision.json"),
        "schema": _read_artifact(report_dir / "paper_external_score_schema.json"),
        "manifest": _read_artifact(report_dir / "paper_external_score_manifest.json"),
        "evidence_cells": _read_artifact(report_dir / "paper_external_score_evidence_cells.json"),
        "claim_gate": _read_artifact(report_dir / "paper_external_score_claim_gate.json"),
        "handoff_eval": _read_artifact(report_dir / "paper_external_score_handoff_eval.json"),
    }


def _build_case_study(inputs: dict[str, Any]) -> dict[str, Any]:
    route = _payload(inputs["route_decision"])
    schema = _payload(inputs["schema"])
    manifest = _payload(inputs["manifest"])
    cells_report = _payload(inputs["evidence_cells"])
    gate = _payload(inputs["claim_gate"])
    handoff = _payload(inputs["handoff_eval"])
    cells = [cell for cell in cells_report.get("evidence_cells", []) if isinstance(cell, dict)]
    first_cell = dict(cells[0]) if cells else {}
    checks = _case_study_checks(
        inputs=inputs,
        manifest=manifest,
        schema=schema,
        cells=cells,
        gate=gate,
        handoff=handoff,
    )
    passed = all(bool(check.get("passed")) for check in checks)
    adapter_input_contract = {
        "selected_route": route.get("selected_route") or "not_available",
        "input_artifact_ref": route.get("input_artifact_ref") or schema.get("artifact_ref") or "not_available",
        "source_kind": manifest.get("input_summary", {}).get("source_kind") or schema.get("source_kind") or "not_available",
        "dataset_id": first_cell.get("dataset_id") or route.get("dataset_id") or "not_available",
        "dataset_role": first_cell.get("dataset_role") or "not_available",
        "split": first_cell.get("split") or route.get("split") or "not_available",
        "split_role": first_cell.get("split_role") or "not_available",
        "schema_field_count": len(schema.get("schema_fields", [])),
        "schema_hash_prefix": schema.get("schema_hash_prefix") or "not_available",
        "content_hash_prefix": manifest.get("input_summary", {}).get("content_hash_prefix")
        or schema.get("content_hash_prefix")
        or "not_available",
    }
    metric_policy = {
        "metric": first_cell.get("metric") or schema.get("metric", {}).get("name") or "not_available",
        "metric_role": first_cell.get("metric_role") or schema.get("metric", {}).get("role") or "not_available",
        "value": first_cell.get("value") if "value" in first_cell else schema.get("metric", {}).get("value"),
        "detector_performance_metric": bool(schema.get("metric", {}).get("detector_performance_metric")),
        "paper_role": first_cell.get("paper_role") or "hosted_detector_output_governance_evidence",
        "publishable": bool(first_cell.get("publishable")) if first_cell else False,
    }
    rowless_redaction = {
        "rowless_handoff_passed": bool(handoff.get("rowless_handoff_passed")),
        "exported_field_count": int(handoff.get("exported_field_count") or 0),
        "redacted_field_count": int(handoff.get("redacted_field_count") or 0),
        "exported_fields": list(handoff.get("exported_fields", [])),
        "redacted_field_categories": [
            "raw rows and records",
            "entity, account, customer, and transaction identifiers",
            "private local paths",
            "raw score payloads",
            "secrets and tokens",
        ],
        "raw_rows_exported": bool(handoff.get("raw_rows_exported")),
        "entity_identifiers_exported": bool(handoff.get("entity_identifiers_exported")),
        "private_paths_exported": bool(handoff.get("private_paths_exported")),
        "secrets_exported": bool(handoff.get("secrets_exported")),
    }
    return {
        "schema_version": PAPER_EXTERNAL_SCORE_INTEGRATION_SCHEMA_VERSION,
        "slice": "Paper Track P19-B",
        "case_id": "p19b_hosted_external_score_case_study",
        "status": "pass" if passed else "blocked_pending_p19a_evidence",
        "title": "Hosted external-score governance case study",
        "source_reports": REQUIRED_PAPER_EXTERNAL_SCORE_INPUT_REFS,
        "checks": checks,
        "adapter_input_contract": adapter_input_contract,
        "relaytic_checks": _compact_checks(manifest.get("checks", [])) + _compact_checks(gate.get("checks", [])),
        "metric_policy": metric_policy,
        "rowless_redaction": rowless_redaction,
        "evidence_cell_ids": [str(cell.get("cell_id")) for cell in cells if cell.get("cell_id")],
        "auditable_record_snippet": _auditable_record_snippet(first_cell),
        "allowed_claim_state": gate.get("allowed_claim_scope") or "not_available",
        "allowed_public_claims": list(gate.get("allowed_public_claims", [])),
        "blocked_stronger_claims": [
            {
                "claim": blocked.get("claim"),
                "gate_reason": blocked.get("reason"),
                "missing_evidence": blocked.get("missing_evidence"),
            }
            for blocked in gate.get("blocked_claims", [])
            if isinstance(blocked, dict)
        ],
        "interpretation": (
            "This case study shows that Relaytic-AML can host a rowless detector-score artifact as governed evidence: "
            "the adapter records schema and content hashes, creates evidence cells, redacts unsafe handoff fields, "
            "and blocks stronger detector or production claims. It is not a detector-performance result."
        ),
    }


def _build_paper_panel(case_study: dict[str, Any]) -> dict[str, Any]:
    adapter = dict(case_study.get("adapter_input_contract", {}))
    metric = dict(case_study.get("metric_policy", {}))
    redaction = dict(case_study.get("rowless_redaction", {}))
    blocked = list(case_study.get("blocked_stronger_claims", []))
    rows = [
        {
            "component": "Adapter input",
            "observed": (
                f"external-score adapter over a rowless fixture; "
                f"schema hash {adapter.get('schema_hash_prefix')}; content hash {adapter.get('content_hash_prefix')}"
            ),
            "evidence_ref": "docs/reports/paper_external_score_schema.json",
            "reader_takeaway": "The score artifact is described by schema and hash posture, not by raw rows.",
        },
        {
            "component": "Evidence emitted",
            "observed": (
                f"{len(case_study.get('evidence_cell_ids', []))} evidence cell; "
                f"metadata-completeness metric; value {_format_panel_value(metric.get('value'))}"
            ),
            "evidence_ref": "docs/reports/paper_external_score_evidence_cells.json",
            "reader_takeaway": "Relaytic records the governance metric as auditable evidence, not as detector novelty.",
        },
        {
            "component": "Rowless handoff",
            "observed": (
                f"{redaction.get('exported_field_count')} exported fields; "
                f"{redaction.get('redacted_field_count')} blocked fields; no raw rows exported"
            ),
            "evidence_ref": "docs/reports/paper_external_score_handoff_eval.json",
            "reader_takeaway": "A downstream agent can inspect state without receiving rows, identifiers, paths, or secrets.",
        },
        {
            "component": "Claim state",
            "observed": f"hosted detector-output governance only; {len(blocked)} stronger claims blocked",
            "evidence_ref": "docs/reports/paper_external_score_claim_gate.json",
            "reader_takeaway": "The public use is hosted detector-output governance only.",
        },
    ]
    return {
        "schema_version": PAPER_EXTERNAL_SCORE_INTEGRATION_SCHEMA_VERSION,
        "status": "pass" if case_study.get("status") == "pass" else "blocked",
        "panel_id": "p19b_hosted_score_panel",
        "title": "Hosted external-score case study",
        "rows": rows,
        "interpretation": case_study.get("interpretation"),
    }


def _build_claim_map(case_study: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": PAPER_EXTERNAL_SCORE_INTEGRATION_SCHEMA_VERSION,
        "status": "pass" if case_study.get("status") == "pass" else "blocked",
        "allowed_claim_scope": case_study.get("allowed_claim_state"),
        "paper_safe_sentence": (
            "Relaytic-AML can wrap a rowless external detector-score artifact in schema, hash, redaction, "
            "evidence-cell, and claim-state controls."
        ),
        "allowed_claims": list(case_study.get("allowed_public_claims", [])),
        "blocked_claims": list(case_study.get("blocked_stronger_claims", [])),
        "detector_superiority_allowed": False,
        "graph_neural_detector_novelty_allowed": False,
        "production_aml_readiness_allowed": False,
        "revclassifyds_parity_allowed": False,
        "real_bank_validation_allowed": False,
        "headline_performance_claim_allowed": False,
    }


def _build_manifest(
    *,
    inputs: dict[str, Any],
    case_study: dict[str, Any],
    paper_panel: dict[str, Any],
    claim_map: dict[str, Any],
    repro_card: str,
) -> dict[str, Any]:
    checks = list(case_study.get("checks", []))
    checks.extend(
        [
            {
                "check_id": "paper_panel_ready",
                "requirement": "paper panel has compact reader-facing rows",
                "observed": f"rows={len(paper_panel.get('rows', []))}; status={paper_panel.get('status')}",
                "passed": paper_panel.get("status") == "pass" and len(paper_panel.get("rows", [])) >= 4,
            },
            {
                "check_id": "claim_map_bounded",
                "requirement": "hosted-score integration does not permit stronger detector or production claims",
                "observed": (
                    f"detector_superiority_allowed={claim_map.get('detector_superiority_allowed')}; "
                    f"revclassifyds_parity_allowed={claim_map.get('revclassifyds_parity_allowed')}"
                ),
                "passed": not any(
                    bool(claim_map.get(flag))
                    for flag in (
                        "detector_superiority_allowed",
                        "graph_neural_detector_novelty_allowed",
                        "production_aml_readiness_allowed",
                        "revclassifyds_parity_allowed",
                        "real_bank_validation_allowed",
                        "headline_performance_claim_allowed",
                    )
                ),
            },
            {
                "check_id": "repro_card_cross_platform",
                "requirement": "repro card includes Windows and macOS/Linux commands for P19-A and P19-B",
                "observed": "windows=py -3.11; posix=python3; p19b_command=paper-external-score-integration",
                "passed": all(
                    token in repro_card
                    for token in (
                        "py -3.11 -m relaytic.ui.cli release-safety paper-external-score-proof",
                        "py -3.11 -m relaytic.ui.cli release-safety paper-external-score-integration",
                        "python3 -m relaytic.ui.cli release-safety paper-external-score-proof",
                        "python3 -m relaytic.ui.cli release-safety paper-external-score-integration",
                    )
                ),
            },
        ]
    )
    failed = [str(check.get("check_id")) for check in checks if not bool(check.get("passed"))]
    missing = _missing_input_refs(inputs)
    return {
        "schema_version": PAPER_EXTERNAL_SCORE_INTEGRATION_SCHEMA_VERSION,
        "slice": "Paper Track P19-B",
        "status": "ready_for_hosted_score_case_study" if not failed else "blocked_pending_hosted_score_case_study",
        "command": "relaytic release-safety paper-external-score-integration",
        "paper_integration_allowed": not failed,
        "failed_checks": failed,
        "checks": checks,
        "required_p19a_artifacts": REQUIRED_PAPER_EXTERNAL_SCORE_INPUT_REFS,
        "missing_p19a_artifacts": missing,
        "source_evidence_cell_ids": list(case_study.get("evidence_cell_ids", [])),
        "reports": dict(PAPER_EXTERNAL_SCORE_INTEGRATION_FILENAMES),
        "claim_boundary": {
            "allowed": claim_map.get("allowed_claim_scope"),
            "detector_superiority_claimed": False,
            "graph_neural_detector_novelty_claimed": False,
            "production_aml_readiness_claimed": False,
            "revclassify_parity_claimed": False,
            "real_bank_validation_claimed": False,
        },
        "no_private_data_posture": {
            "raw_rows_written": False,
            "entity_identifiers_written": False,
            "private_paths_written": False,
            "licensed_data_written": False,
            "secrets_written": False,
        },
        "next_slice": NEXT_PAPER_EXTERNAL_SCORE_INTEGRATION_SLICE,
    }


def _case_study_checks(
    *,
    inputs: dict[str, Any],
    manifest: dict[str, Any],
    schema: dict[str, Any],
    cells: list[dict[str, Any]],
    gate: dict[str, Any],
    handoff: dict[str, Any],
) -> list[dict[str, Any]]:
    missing = _missing_input_refs(inputs)
    cell_ids = [str(cell.get("cell_id")) for cell in cells if cell.get("cell_id")]
    return [
        {
            "check_id": "p19a_inputs_present",
            "requirement": "P19-B consumes the complete P19-A report family",
            "observed": f"missing={len(missing)}",
            "passed": not missing,
        },
        {
            "check_id": "p19a_manifest_ready",
            "requirement": "P19-A manifest is ready for hosted-score governance",
            "observed": f"status={manifest.get('status') or 'missing'}",
            "passed": manifest.get("status") == "ready_for_hosted_score_governance",
        },
        {
            "check_id": "adapter_contract_hashes_available",
            "requirement": "adapter input has schema and content hash prefixes",
            "observed": (
                f"schema_hash={schema.get('schema_hash_prefix') or 'missing'}; "
                f"content_hash={manifest.get('input_summary', {}).get('content_hash_prefix') or schema.get('content_hash_prefix') or 'missing'}"
            ),
            "passed": bool(schema.get("schema_hash_prefix"))
            and bool(manifest.get("input_summary", {}).get("content_hash_prefix") or schema.get("content_hash_prefix")),
        },
        {
            "check_id": "evidence_cell_ids_present",
            "requirement": "case study cites evidence-cell IDs",
            "observed": f"cell_ids={','.join(cell_ids) if cell_ids else 'missing'}",
            "passed": bool(cell_ids),
        },
        {
            "check_id": "rowless_handoff_passed",
            "requirement": "handoff report redacts rows, identifiers, paths, raw scores, and secrets",
            "observed": f"passed={handoff.get('rowless_handoff_passed')}; redacted={handoff.get('redacted_field_count')}",
            "passed": bool(handoff.get("rowless_handoff_passed"))
            and not bool(handoff.get("raw_rows_exported"))
            and not bool(handoff.get("private_paths_exported"))
            and not bool(handoff.get("secrets_exported")),
        },
        {
            "check_id": "claim_gate_bounded",
            "requirement": "claim gate permits hosted-score governance only and blocks stronger claims",
            "observed": f"publishable={gate.get('publishable')}; blocked={len(gate.get('blocked_claims', []))}",
            "passed": bool(gate.get("publishable"))
            and gate.get("allowed_claim_scope") == "hosted_detector_output_governance_only"
            and len(gate.get("blocked_claims", [])) >= 4
            and not bool(gate.get("detector_superiority_claimed"))
            and not bool(gate.get("production_aml_readiness_claimed"))
            and not bool(gate.get("revclassify_parity_claimed")),
        },
    ]


def _compact_checks(checks: Any) -> list[dict[str, Any]]:
    compact = []
    for check in checks if isinstance(checks, list) else []:
        if not isinstance(check, dict):
            continue
        compact.append(
            {
                "check_id": check.get("check_id"),
                "requirement": check.get("requirement"),
                "observed": check.get("observed"),
                "passed": bool(check.get("passed")),
            }
        )
    return compact


def _format_panel_value(value: Any) -> str:
    if isinstance(value, (int, float)):
        return f"{float(value):.4f}"
    return str(value)


def _auditable_record_snippet(cell: dict[str, Any]) -> dict[str, Any]:
    return {
        "cell_id": cell.get("cell_id") or "not_available",
        "dataset_id": cell.get("dataset_id") or "not_available",
        "split": cell.get("split") or "not_available",
        "command": cell.get("command") or "relaytic release-safety paper-external-score-proof",
        "artifact_ref": cell.get("artifact_ref") or "not_available",
        "metric": cell.get("metric") or "not_available",
        "value": cell.get("value") if "value" in cell else "not_available",
        "leakage_posture": cell.get("leakage_posture") or "not_available",
        "claim_state": cell.get("claim_state") or "not_available",
    }


def _missing_input_refs(inputs: dict[str, Any]) -> list[str]:
    missing = []
    for artifact in inputs.values():
        if isinstance(artifact, dict) and artifact.get("artifact_ref") and not artifact.get("exists"):
            missing.append(str(artifact.get("artifact_ref")))
    return sorted(missing)


def _read_artifact(path: Path) -> dict[str, Any]:
    payload: dict[str, Any] = {}
    parse_error = None
    if path.is_file():
        try:
            loaded = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            parse_error = type(exc).__name__
        else:
            payload = dict(loaded) if isinstance(loaded, dict) else {}
    return {
        "artifact_ref": f"docs/reports/{path.name}",
        "exists": path.is_file(),
        "parse_error": parse_error,
        "payload": payload,
    }


def _payload(artifact: dict[str, Any]) -> dict[str, Any]:
    payload = artifact.get("payload", {})
    return dict(payload) if isinstance(payload, dict) else {}


def _escape_md(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")
