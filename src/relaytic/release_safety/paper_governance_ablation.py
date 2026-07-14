"""Paper Track P17 deterministic governance-ablation pack."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
from typing import Any

from relaytic.core.json_utils import write_json


PAPER_GOVERNANCE_ABLATION_SCHEMA_VERSION = "relaytic.paper_governance_ablation.v1"
PAPER_GOVERNANCE_ABLATION_REPORT_DIR = Path("docs") / "reports"
NEXT_PAPER_GOVERNANCE_ABLATION_SLICE = "Paper Track P18 - governance invariants and adjacent-systems positioning"

PAPER_GOVERNANCE_ABLATION_FILENAMES = {
    "paper_governance_ablation_eval": "paper_governance_ablation_eval.json",
    "paper_governance_ablation_matrix": "paper_governance_ablation_matrix.json",
    "paper_governance_ablation_manifest": "paper_governance_ablation_manifest.json",
    "paper_governance_ablation_summary": "paper_governance_ablation_summary.md",
}

REQUIRED_GOVERNANCE_ABLATION_INPUT_REFS = [
    "docs/reports/paper_public_claims_allowed.json",
    "docs/reports/paysim_leakage_safe_feature_report.json",
    "docs/reports/paper_agent_handoff_eval.json",
    "docs/reports/paper_no_lost_user_eval.json",
    "docs/reports/paper_metric_cell_audit.json",
    "docs/reports/paper_publishability_matrix.json",
    "docs/reports/paper_result_table_final.json",
    "docs/reports/paper_failure_case_manifest.json",
    "docs/reports/paper_failure_case_eval.json",
]

REQUIRED_METRIC_CELL_FIELDS = [
    "cell_id",
    "dataset_id",
    "split",
    "command",
    "artifact_ref",
    "artifact_field",
    "metric",
    "value",
    "budget_tier",
    "leakage_posture",
]

FORBIDDEN_PAYSIM_BALANCE_COLUMNS = [
    "oldbalanceOrg",
    "newbalanceOrig",
    "oldbalanceDest",
    "newbalanceDest",
]


def build_paper_governance_ablation_pack(project_root: str | Path) -> dict[str, Any]:
    """Build deterministic P17 governance ablations from committed evidence artifacts."""
    root = Path(project_root)
    inputs = _collect_inputs(root)
    full_metrics = _full_path_metrics(inputs)
    rows = _build_ablation_rows(full_metrics)
    evaluation = _build_ablation_eval(inputs=inputs, rows=rows, full_metrics=full_metrics)
    matrix = _build_ablation_matrix(rows)
    manifest = _build_manifest(inputs=inputs, evaluation=evaluation, matrix=matrix, rows=rows)
    pack = {
        "paper_governance_ablation_eval": evaluation,
        "paper_governance_ablation_matrix": matrix,
        "paper_governance_ablation_manifest": manifest,
    }
    pack["paper_governance_ablation_summary"] = render_paper_governance_ablation_markdown(pack)
    return pack


def sync_paper_governance_ablation_pack(
    project_root: str | Path,
    *,
    output_dir: str | Path | None = None,
) -> dict[str, Path]:
    """Write P17 governance-ablation reports under docs/reports."""
    root = Path(project_root)
    report_dir = Path(output_dir) if output_dir is not None else root / PAPER_GOVERNANCE_ABLATION_REPORT_DIR
    report_dir.mkdir(parents=True, exist_ok=True)
    pack = build_paper_governance_ablation_pack(root)
    written: dict[str, Path] = {}
    for key, filename in PAPER_GOVERNANCE_ABLATION_FILENAMES.items():
        path = report_dir / filename
        if filename.endswith(".md"):
            path.write_text(str(pack[key]), encoding="utf-8")
            written[key] = path
        else:
            written[key] = write_json(path, pack[key], indent=2, sort_keys=True)
    return written


def render_paper_governance_ablation_markdown(pack: dict[str, Any]) -> str:
    manifest = dict(pack.get("paper_governance_ablation_manifest", {}))
    evaluation = dict(pack.get("paper_governance_ablation_eval", {}))
    rows = list(evaluation.get("ablation_rows", []))
    lines = [
        "# Paper P17 Governance-Ablation Pack",
        "",
        f"- Status: `{manifest.get('status') or 'unknown'}`",
        f"- Full path safe: `{evaluation.get('full_path_safe')}`",
        f"- Disabled fixture count: `{evaluation.get('disabled_fixture_count')}`",
        f"- Fixture scope: `{evaluation.get('fixture_scope') or 'unknown'}`",
        f"- Raw rows exposed: `{evaluation.get('raw_rows_exposed')}`",
        f"- Private paths exposed: `{evaluation.get('private_paths_exposed')}`",
        f"- Next slice: `{manifest.get('next_slice') or 'unknown'}`",
        "",
        "## Governance Ablation Matrix",
        "",
        "| Path | Disabled Machinery | Unsafe Claims | Leakage Inputs | Raw Fields | Missing Provenance | Publishable Tables | Recovery Actions | Result |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        result = "safe" if row.get("safe_to_publish") else "unsafe"
        lines.append(
            "| "
            + " | ".join(
                [
                    _escape_md(str(row.get("path") or row.get("condition_id") or "unknown")),
                    _escape_md(str(row.get("disabled_machinery") or "")),
                    str(row.get("unsupported_claims_released") or 0),
                    str(row.get("leakage_features_allowed") or 0),
                    str(row.get("raw_fields_exported") or 0),
                    str(row.get("missing_provenance_fields") or 0),
                    str(row.get("publishable_tables_generated") or 0),
                    str(row.get("recovery_next_actions_available") or 0),
                    f"`{result}`",
                ]
            )
            + " |"
        )
    return "\n".join(lines).rstrip() + "\n"


def _collect_inputs(root: Path) -> dict[str, Any]:
    reports = root / PAPER_GOVERNANCE_ABLATION_REPORT_DIR
    return {
        "root": root,
        "public_claims_allowed": _read_artifact(reports / "paper_public_claims_allowed.json", root=root),
        "paysim_feature_report": _read_artifact(reports / "paysim_leakage_safe_feature_report.json", root=root),
        "agent_handoff_eval": _read_artifact(reports / "paper_agent_handoff_eval.json", root=root),
        "no_lost_user_eval": _read_artifact(reports / "paper_no_lost_user_eval.json", root=root),
        "metric_cell_audit": _read_artifact(reports / "paper_metric_cell_audit.json", root=root),
        "publishability_matrix": _read_artifact(reports / "paper_publishability_matrix.json", root=root),
        "result_table": _read_artifact(reports / "paper_result_table_final.json", root=root),
        "failure_case_manifest": _read_artifact(reports / "paper_failure_case_manifest.json", root=root),
        "failure_case_eval": _read_artifact(reports / "paper_failure_case_eval.json", root=root),
    }


def _full_path_metrics(inputs: dict[str, Any]) -> dict[str, Any]:
    claims = _payload(inputs["public_claims_allowed"])
    feature_report = _payload(inputs["paysim_feature_report"])
    handoff = _payload(inputs["agent_handoff_eval"])
    recovery = _payload(inputs["no_lost_user_eval"])
    metric_audit = _payload(inputs["metric_cell_audit"])
    publishability = _payload(inputs["publishability_matrix"])
    result_table = _payload(inputs["result_table"])
    blocked_claims = [str(item) for item in claims.get("blocked_public_claims", []) if item is not None]

    feature_columns = {str(item) for item in feature_report.get("feature_columns", []) if item is not None}
    forbidden_used = {str(item) for item in feature_report.get("forbidden_balance_columns_used", []) if item is not None}
    forbidden_allowed = set(FORBIDDEN_PAYSIM_BALANCE_COLUMNS) & feature_columns
    labels_used = bool(feature_report.get("validation_or_test_labels_used_for_features"))

    handoff_task = _task_by_id(handoff).get("external_context_rowless_and_redacted", {})
    handoff_signal = str(handoff_task.get("measured_signal") or "")
    raw_rows_exposed = "raw_rows=False" not in handoff_signal
    blocked_fields = _signal_int(handoff_signal, "blocked_fields")
    redactions = _signal_int(handoff_signal, "redactions")

    recovery_task = _task_by_id(recovery).get("partial_run_state_recovery", {})
    recovery_signal = str(recovery_task.get("measured_signal") or "")
    recovery_actions = _signal_int(recovery_signal, "actions")

    numeric_cells = [item for item in metric_audit.get("numeric_cells", []) if isinstance(item, dict)]
    sample_cell = _select_metric_cell(numeric_cells)
    missing_fields = _missing_required_fields(sample_cell)
    audit_checks = dict(metric_audit.get("checks") or {})
    all_numeric_have_provenance = bool(audit_checks.get("all_numeric_cells_have_required_provenance"))

    publishability_rows = [item for item in publishability.get("rows", []) if isinstance(item, dict)]
    supporting_rows = [row for row in publishability_rows if bool(row.get("supporting_table_allowed"))]
    table_groups = [item for item in result_table.get("table_groups", []) if isinstance(item, dict)]
    publishable_tables_generated = len(table_groups) if result_table.get("status") == "tables_generated_claim_guarded" else 0

    unsupported_claims_released = 0 if not bool(claims.get("hard_claims_allowed")) and not bool(claims.get("headline_claims_allowed")) else len(blocked_claims)
    leakage_features_allowed = len(forbidden_used | forbidden_allowed) + int(labels_used)
    raw_fields_exported = 0 if bool(handoff_task.get("passed")) and not raw_rows_exposed else blocked_fields
    missing_provenance_fields = 0 if all_numeric_have_provenance and not missing_fields else len(missing_fields)
    safe = (
        bool(claims.get("claim_safe_public_wording_allowed"))
        and unsupported_claims_released == 0
        and leakage_features_allowed == 0
        and raw_fields_exported == 0
        and missing_provenance_fields == 0
        and publishable_tables_generated > 0
        and recovery_actions > 0
    )
    return {
        "blocked_public_claim_count": len(blocked_claims),
        "forbidden_feature_count": len(FORBIDDEN_PAYSIM_BALANCE_COLUMNS),
        "redaction_count": redactions,
        "blocked_field_count": blocked_fields,
        "required_metric_field_count": len(REQUIRED_METRIC_CELL_FIELDS),
        "numeric_cell_count": int(metric_audit.get("numeric_cell_count") or len(numeric_cells)),
        "supporting_table_allowed_count": len(supporting_rows),
        "unsupported_claims_released": unsupported_claims_released,
        "leakage_features_allowed": leakage_features_allowed,
        "raw_fields_exported": raw_fields_exported,
        "missing_provenance_fields": missing_provenance_fields,
        "publishable_tables_generated": publishable_tables_generated,
        "unsafe_publishable_tables_generated": 0,
        "recovery_next_actions_available": recovery_actions,
        "raw_rows_exposed": raw_rows_exposed,
        "private_paths_exposed": False,
        "safe_to_publish": safe,
        "sample_metric_cell_id": str(sample_cell.get("cell_id") or ""),
        "missing_metric_fields": missing_fields,
        "source_signals": {
            "claim_gate": f"blocked_claims={len(blocked_claims)}; hard={bool(claims.get('hard_claims_allowed'))}; headline={bool(claims.get('headline_claims_allowed'))}",
            "leakage_policy": f"forbidden={len(FORBIDDEN_PAYSIM_BALANCE_COLUMNS)}; used={len(forbidden_used)}; labels={labels_used}",
            "handoff_redaction": handoff_signal,
            "metric_provenance": f"numeric_cells={len(numeric_cells)}; missing_required={len(missing_fields)}",
            "recovery": recovery_signal,
        },
    }


def _build_ablation_rows(full: dict[str, Any]) -> list[dict[str, Any]]:
    rows = [
        _row(
            condition_id="full_governance_path",
            path="Full governance path",
            disabled_machinery="none",
            metrics=full,
            observed_failure="No unsafe release signal in the current evidence pack.",
            interpretation="Claim gate, leakage policy, redaction, provenance, and recovery guide are all active.",
            safe_to_publish=bool(full.get("safe_to_publish")),
        )
    ]
    disabled_specs = [
        (
            "no_claim_gate",
            "No claim gate",
            "public claim gate",
            {
                "unsupported_claims_released": int(full.get("blocked_public_claim_count") or 0),
            },
            "Blocked claims would move into public wording.",
            "The claim gate is what keeps proxy evidence below hard AML, SOTA, RevClassifyDS parity, production, and business-value claims.",
        ),
        (
            "no_leakage_policy",
            "No leakage policy",
            "PaySim feature leakage policy",
            {
                "leakage_features_allowed": int(full.get("forbidden_feature_count") or 0),
                "unsafe_publishable_tables_generated": 1,
            },
            "Forbidden PaySim balance fields would be eligible for a paper row.",
            "The leakage policy prevents post-event simulator fields from becoming apparently strong evidence.",
        ),
        (
            "no_rowless_redaction",
            "No rowless handoff redaction",
            "external-agent redaction",
            {
                "raw_fields_exported": int(full.get("blocked_field_count") or 0),
                "raw_rows_exposed": True,
                "private_paths_exposed": True,
            },
            "Blocked fields would be exported to the external-agent packet.",
            "Rowless handoff is the privacy boundary that lets outside agents help without receiving raw data or local paths.",
        ),
        (
            "no_evidence_cell_required_fields",
            "No evidence-cell required fields",
            "evidence-cell required-field gate",
            {
                "missing_provenance_fields": int(full.get("required_metric_field_count") or 0),
                "unsafe_publishable_tables_generated": 1,
            },
            "A metric row could enter a table with required provenance missing.",
            "Required fields connect a reader-facing measurement to its dataset, split, command, artifact, leakage posture, budget, operating-point provenance, and exposure status. Interpretation remains in a separate gate record.",
        ),
        (
            "no_recovery_guide",
            "No interrupted-run recovery guide",
            "no-lost-user guide",
            {
                "recovery_next_actions_available": 0,
            },
            "An interrupted user or agent would receive no safe next actions.",
            "The recovery guide is what keeps state navigation from depending on repo literacy.",
        ),
    ]
    for condition_id, path, disabled_machinery, overrides, failure, interpretation in disabled_specs:
        metrics = dict(full)
        metrics.update(overrides)
        metrics["safe_to_publish"] = False
        rows.append(
            _row(
                condition_id=condition_id,
                path=path,
                disabled_machinery=disabled_machinery,
                metrics=metrics,
                observed_failure=failure,
                interpretation=interpretation,
                safe_to_publish=False,
            )
        )
    return rows


def _row(
    *,
    condition_id: str,
    path: str,
    disabled_machinery: str,
    metrics: dict[str, Any],
    observed_failure: str,
    interpretation: str,
    safe_to_publish: bool,
) -> dict[str, Any]:
    return {
        "condition_id": condition_id,
        "path": path,
        "disabled_machinery": disabled_machinery,
        "unsupported_claims_released": int(metrics.get("unsupported_claims_released") or 0),
        "leakage_features_allowed": int(metrics.get("leakage_features_allowed") or 0),
        "raw_fields_exported": int(metrics.get("raw_fields_exported") or 0),
        "missing_provenance_fields": int(metrics.get("missing_provenance_fields") or 0),
        "publishable_tables_generated": int(metrics.get("publishable_tables_generated") or 0),
        "unsafe_publishable_tables_generated": int(metrics.get("unsafe_publishable_tables_generated") or 0),
        "recovery_next_actions_available": int(metrics.get("recovery_next_actions_available") or 0),
        "raw_rows_would_be_exposed": bool(metrics.get("raw_rows_exposed")),
        "private_paths_would_be_exposed": bool(metrics.get("private_paths_exposed")),
        "observed_failure": _sanitize_text(observed_failure),
        "interpretation": _sanitize_text(interpretation),
        "safe_to_publish": bool(safe_to_publish),
        "fixture_scope": "deterministic disabled-component ablation fixture" if condition_id != "full_governance_path" else "observed full-path control",
    }


def _build_ablation_eval(
    *,
    inputs: dict[str, Any],
    rows: list[dict[str, Any]],
    full_metrics: dict[str, Any],
) -> dict[str, Any]:
    serialized_rows = json.dumps(rows, sort_keys=True)
    raw_rows_exposed = _contains_raw_data_signal(serialized_rows)
    private_paths_exposed = _contains_private_path(serialized_rows)
    full_row = _row_by_id(rows).get("full_governance_path", {})
    disabled = [row for row in rows if row.get("condition_id") != "full_governance_path"]
    disabled_failures_visible = all(not row.get("safe_to_publish") for row in disabled) and all(
        _row_has_expected_failure(row) for row in disabled
    )
    required = _required_artifact_presence(inputs)
    status = (
        "pass"
        if not required["missing_artifact_refs"]
        and bool(full_row.get("safe_to_publish"))
        and disabled_failures_visible
        and not raw_rows_exposed
        and not private_paths_exposed
        else "fail"
    )
    return {
        "schema_version": PAPER_GOVERNANCE_ABLATION_SCHEMA_VERSION,
        "slice": "Paper Track P17",
        "status": status,
        "fixture_scope": "deterministic system-level governance ablation over current paper evidence artifacts",
        "full_path_safe": bool(full_row.get("safe_to_publish")),
        "disabled_fixture_count": len(disabled),
        "ablation_row_count": len(rows),
        "raw_rows_exposed": raw_rows_exposed,
        "private_paths_exposed": private_paths_exposed,
        "required_inputs": required,
        "full_path_metrics": full_metrics,
        "ablation_rows": rows,
        "guardrail_delta": {
            "unsupported_claims_prevented": int(full_metrics.get("blocked_public_claim_count") or 0),
            "leakage_features_prevented": int(full_metrics.get("forbidden_feature_count") or 0),
            "handoff_fields_redacted_or_blocked": int(full_metrics.get("blocked_field_count") or 0),
            "metric_fields_required": int(full_metrics.get("required_metric_field_count") or 0),
            "recovery_actions_preserved": int(full_metrics.get("recovery_next_actions_available") or 0),
        },
        "interpretation": (
            "These are deterministic governance ablations. They show which release-safety mechanisms change the "
            "paper/evidence path and do not add detector benchmark, real-bank AML superiority, RevClassifyDS parity, "
            "production deployment, or analyst-impact claims."
        ),
    }


def _build_ablation_matrix(rows: list[dict[str, Any]]) -> dict[str, Any]:
    table_rows = []
    for row in rows:
        table_rows.append(
            {
                "path": row["path"],
                "disabled_machinery": row["disabled_machinery"],
                "unsafe_signal": _unsafe_signal(row),
                "artifact_integrity": _artifact_integrity_signal(row),
                "handoff_recovery": _handoff_recovery_signal(row),
                "interpretation": row["interpretation"],
                "condition_id": row["condition_id"],
                "safe_to_publish": bool(row["safe_to_publish"]),
                "metrics": {
                    "unsupported_claims_released": row["unsupported_claims_released"],
                    "leakage_features_allowed": row["leakage_features_allowed"],
                    "raw_fields_exported": row["raw_fields_exported"],
                    "missing_provenance_fields": row["missing_provenance_fields"],
                    "publishable_tables_generated": row["publishable_tables_generated"],
                    "unsafe_publishable_tables_generated": row["unsafe_publishable_tables_generated"],
                    "recovery_next_actions_available": row["recovery_next_actions_available"],
                },
            }
        )
    return {
        "schema_version": PAPER_GOVERNANCE_ABLATION_SCHEMA_VERSION,
        "slice": "Paper Track P17",
        "status": "pass" if table_rows and table_rows[0]["safe_to_publish"] and all(not row["safe_to_publish"] for row in table_rows[1:]) else "fail",
        "table_id": "governance_machinery_ablation",
        "columns": [
            "Path",
            "Disabled machinery",
            "Unsafe signal",
            "Artifact integrity",
            "Handoff / recovery",
            "Interpretation",
        ],
        "rows": table_rows,
    }


def _build_manifest(
    *,
    inputs: dict[str, Any],
    evaluation: dict[str, Any],
    matrix: dict[str, Any],
    rows: list[dict[str, Any]],
) -> dict[str, Any]:
    required = _required_artifact_presence(inputs)
    row_by_id = _row_by_id(rows)
    full = row_by_id.get("full_governance_path", {})
    disabled = [row for row in rows if row.get("condition_id") != "full_governance_path"]
    serialized = json.dumps({"evaluation": evaluation, "matrix": matrix}, sort_keys=True)
    checks = [
        _check(
            "required_governance_ablation_inputs_present",
            not required["missing_artifact_refs"],
            "All P17 source evidence artifacts must be present.",
            source_artifact="docs/reports",
            detail=required,
        ),
        _check(
            "full_path_blocks_unsafe_claims",
            bool(full.get("safe_to_publish")) and int(full.get("unsupported_claims_released") or 0) == 0,
            "The full path must release zero unsupported public claims.",
            source_artifact="docs/reports/paper_public_claims_allowed.json",
        ),
        _check(
            "full_path_blocks_leakage_features",
            bool(full.get("safe_to_publish")) and int(full.get("leakage_features_allowed") or 0) == 0,
            "The full path must allow zero forbidden PaySim leakage inputs.",
            source_artifact="docs/reports/paysim_leakage_safe_feature_report.json",
        ),
        _check(
            "full_path_redacts_handoff",
            bool(full.get("safe_to_publish")) and int(full.get("raw_fields_exported") or 0) == 0,
            "The full path must export no raw fields in the external-agent handoff.",
            source_artifact="docs/reports/paper_agent_handoff_eval.json",
        ),
        _check(
            "full_path_metric_provenance_complete",
            bool(full.get("safe_to_publish")) and int(full.get("missing_provenance_fields") or 0) == 0,
            "The full path must retain required evidence-cell provenance fields.",
            source_artifact="docs/reports/paper_metric_cell_audit.json",
        ),
        _check(
            "full_path_generates_publishable_tables",
            bool(full.get("safe_to_publish")) and int(full.get("publishable_tables_generated") or 0) > 0,
            "The full path must generate the claim-safe paper tables.",
            source_artifact="docs/reports/paper_result_table_final.json",
        ),
        _check(
            "full_path_recovery_actions_available",
            bool(full.get("safe_to_publish")) and int(full.get("recovery_next_actions_available") or 0) > 0,
            "The full path must expose next actions for interrupted-run recovery.",
            source_artifact="docs/reports/paper_no_lost_user_eval.json",
        ),
        _check(
            "disabled_fixtures_expose_expected_failures",
            bool(disabled) and all(not row.get("safe_to_publish") and _row_has_expected_failure(row) for row in disabled),
            "Each disabled-component fixture must expose the expected governance failure.",
            source_artifact="docs/reports/paper_governance_ablation_eval.json",
            detail={"condition_ids": [row.get("condition_id") for row in disabled]},
        ),
        _check(
            "rowless_and_path_safe",
            not evaluation.get("raw_rows_exposed") and not evaluation.get("private_paths_exposed") and not _contains_private_path(serialized),
            "The P17 reports must not expose raw rows or private machine paths.",
            source_artifact="docs/reports/paper_governance_ablation_eval.json",
        ),
        _check(
            "claim_boundary_preserved",
            not evaluation.get("detector_superiority_claim_allowed", False)
            and "do not add detector benchmark" in str(evaluation.get("interpretation") or "").lower(),
            "P17 may support governance-ablation claims only, not detector-superiority claims.",
            source_artifact="docs/reports/paper_governance_ablation_eval.json",
        ),
    ]
    status = "ready_for_governance_ablation_evidence" if all(check["passed"] for check in checks) else "blocked_missing_governance_ablation_evidence"
    return {
        "schema_version": PAPER_GOVERNANCE_ABLATION_SCHEMA_VERSION,
        "slice": "Paper Track P17",
        "status": status,
        "governance_ablation_evidence_allowed": status.startswith("ready"),
        "hard_claims_allowed": False,
        "headline_claims_allowed": False,
        "detector_superiority_claim_allowed": False,
        "fixture_scope": evaluation.get("fixture_scope"),
        "required_source_artifacts": REQUIRED_GOVERNANCE_ABLATION_INPUT_REFS,
        "checks": checks,
        "failed_checks": [check for check in checks if not check["passed"]],
        "artifact_hashes": _artifact_hashes(inputs),
        "report_refs": {
            key: f"docs/reports/{filename}"
            for key, filename in PAPER_GOVERNANCE_ABLATION_FILENAMES.items()
        },
        "next_slice": NEXT_PAPER_GOVERNANCE_ABLATION_SLICE if status.startswith("ready") else "Paper Track P17 repair",
    }


def _unsafe_signal(row: dict[str, Any]) -> str:
    claims = int(row.get("unsupported_claims_released") or 0)
    leakage = int(row.get("leakage_features_allowed") or 0)
    raw_fields = int(row.get("raw_fields_exported") or 0)
    missing_fields = int(row.get("missing_provenance_fields") or 0)
    actions = int(row.get("recovery_next_actions_available") or 0)
    if row.get("safe_to_publish"):
        return "0 unsupported claims, leakage inputs, or raw fields"
    parts = []
    if claims:
        parts.append(f"{claims} unsupported claims")
    if leakage:
        parts.append(f"{leakage} leakage inputs")
    if raw_fields:
        parts.append(f"{raw_fields} raw fields")
    if missing_fields:
        parts.append(f"{missing_fields} missing provenance fields")
    if str(row.get("condition_id") or "") == "no_recovery_guide" and actions == 0:
        parts.append("0 recovery actions")
    return "; ".join(parts) if parts else "unsafe governance state"


def _artifact_integrity_signal(row: dict[str, Any]) -> str:
    missing = int(row.get("missing_provenance_fields") or 0)
    unsafe_tables = int(row.get("unsafe_publishable_tables_generated") or 0)
    tables = int(row.get("publishable_tables_generated") or 0)
    if row.get("safe_to_publish"):
        return f"{missing} missing fields; {tables} table groups"
    if missing or unsafe_tables:
        return f"{missing} missing fields; {unsafe_tables} unsafe table path"
    return f"{tables} table groups unchanged"


def _handoff_recovery_signal(row: dict[str, Any]) -> str:
    actions = int(row.get("recovery_next_actions_available") or 0)
    raw_fields = int(row.get("raw_fields_exported") or 0)
    if raw_fields:
        return f"{raw_fields} raw fields; actions={actions}"
    return f"actions={actions}"


def _row_by_id(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {str(row.get("condition_id")): row for row in rows if row.get("condition_id")}


def _row_has_expected_failure(row: dict[str, Any]) -> bool:
    condition_id = str(row.get("condition_id") or "")
    checks = {
        "no_claim_gate": int(row.get("unsupported_claims_released") or 0) > 0,
        "no_leakage_policy": int(row.get("leakage_features_allowed") or 0) > 0,
        "no_rowless_redaction": int(row.get("raw_fields_exported") or 0) > 0,
        "no_evidence_cell_required_fields": int(row.get("missing_provenance_fields") or 0) > 0,
        "no_recovery_guide": int(row.get("recovery_next_actions_available") or 0) == 0,
    }
    return bool(checks.get(condition_id, False))


def _select_metric_cell(cells: list[dict[str, Any]]) -> dict[str, Any]:
    for cell in cells:
        if cell.get("cell_id") == "paysim_p6a_competitive_selected.test_pr_auc":
            return cell
    return cells[0] if cells else {}


def _missing_required_fields(cell: dict[str, Any]) -> list[str]:
    return [field for field in REQUIRED_METRIC_CELL_FIELDS if field not in cell or cell.get(field) in (None, "")]


def _task_by_id(report: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(task.get("task_id")): task
        for task in report.get("tasks", [])
        if isinstance(task, dict) and task.get("task_id")
    }


def _signal_int(signal: str, key: str) -> int:
    match = re.search(rf"{re.escape(key)}=([0-9]+)", signal)
    return int(match.group(1)) if match else 0


def _required_artifact_presence(inputs: dict[str, Any]) -> dict[str, Any]:
    missing = []
    present = []
    artifact_by_ref = {
        value.get("artifact_ref"): value
        for value in inputs.values()
        if isinstance(value, dict) and value.get("artifact_ref")
    }
    for ref in REQUIRED_GOVERNANCE_ABLATION_INPUT_REFS:
        artifact = artifact_by_ref.get(ref)
        if artifact and artifact.get("exists"):
            present.append(ref)
        else:
            missing.append(ref)
    return {"present_artifact_refs": present, "missing_artifact_refs": missing}


def _artifact_hashes(inputs: dict[str, Any]) -> dict[str, str]:
    hashes = {}
    for value in inputs.values():
        if not isinstance(value, dict) or not value.get("exists") or not value.get("sha256"):
            continue
        ref = str(value.get("artifact_ref") or "")
        if ref in REQUIRED_GOVERNANCE_ABLATION_INPUT_REFS:
            hashes[ref] = str(value["sha256"])
    return hashes


def _read_artifact(path: Path, *, root: Path) -> dict[str, Any]:
    artifact_ref = _repo_relative(path, root=root)
    if not path.is_file():
        return {"artifact_ref": artifact_ref, "exists": False, "payload": {}}
    text = path.read_text(encoding="utf-8")
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        payload = {"error": _sanitize_text(str(exc))}
    return {
        "artifact_ref": artifact_ref,
        "exists": True,
        "sha256": _sha256_text(text),
        "payload": payload if isinstance(payload, dict) else {},
    }


def _payload(artifact: dict[str, Any]) -> dict[str, Any]:
    payload = artifact.get("payload", {})
    return dict(payload) if isinstance(payload, dict) else {}


def _check(
    check_id: str,
    passed: bool,
    message: str,
    *,
    source_artifact: str,
    detail: dict[str, Any] | None = None,
) -> dict[str, Any]:
    result: dict[str, Any] = {
        "check_id": check_id,
        "passed": bool(passed),
        "message": message,
        "source_artifact": source_artifact,
    }
    if detail is not None:
        result["detail"] = detail
    return result


def _repo_relative(path: Path, *, root: Path, fallback: str | None = None) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except (OSError, ValueError):
        if fallback is not None:
            return fallback
    parts = path.parts
    for marker in ("docs", "artifacts", "src", "tests", ".github"):
        if marker in parts:
            return Path(*parts[parts.index(marker) :]).as_posix()
    return fallback or path.name


def _contains_private_path(text: str) -> bool:
    return bool(
        re.search(r"[A-Za-z]:[\\/]", text)
        or re.search(r"(?<![A-Za-z0-9])/(?:Users|home|private|tmp|var/folders)/", text)
        or re.search(r"C:/Users|C:\\Users|\\Users\\", text, re.IGNORECASE)
    )


def _contains_raw_data_signal(text: str) -> bool:
    lowered = text.lower()
    return bool("raw transaction row value" in lowered or "account_number" in lowered or "ssn" in lowered)


def _sanitize_text(text: Any) -> str:
    cleaned = str(text)
    cleaned = re.sub(r"[A-Za-z]:[\\/][^\s`\"']+", _path_redaction, cleaned)
    cleaned = re.sub(r"/(?:Users|home|private|tmp|var/folders)/[^\s`\"']+", _path_redaction, cleaned)
    cleaned = re.sub(r"(?i)(api[_-]?key|token|secret)\s*[:=]\s*[A-Za-z0-9_\-]{8,}", r"\1=<redacted_secret>", cleaned)
    return cleaned


def _path_redaction(match: re.Match[str]) -> str:
    raw = match.group(0).replace("\\", "/")
    name = Path(raw).name
    return f"<redacted_path:{name or 'local'}>"


def _escape_md(text: str) -> str:
    return text.replace("|", "\\|").replace("\n", " ")


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


__all__ = [
    "NEXT_PAPER_GOVERNANCE_ABLATION_SLICE",
    "PAPER_GOVERNANCE_ABLATION_FILENAMES",
    "PAPER_GOVERNANCE_ABLATION_REPORT_DIR",
    "PAPER_GOVERNANCE_ABLATION_SCHEMA_VERSION",
    "REQUIRED_GOVERNANCE_ABLATION_INPUT_REFS",
    "build_paper_governance_ablation_pack",
    "render_paper_governance_ablation_markdown",
    "sync_paper_governance_ablation_pack",
]
