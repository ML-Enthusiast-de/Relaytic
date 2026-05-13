"""Flagship Relaytic-AML demo-bundle artifacts for Slice 15S."""

from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from relaytic.core.json_utils import write_json


AML_DEMO_BUNDLE_MANIFEST_SCHEMA_VERSION = "relaytic.aml_demo_bundle_manifest.v1"
AML_DEMO_BUSINESS_METRIC_TABLE_SCHEMA_VERSION = "relaytic.aml_demo_business_metric_table.v1"
AML_DEMO_ARTIFACT_INDEX_SCHEMA_VERSION = "relaytic.aml_demo_artifact_index.v1"
AML_DEMO_ID = "relaytic-aml-review-queue"

AML_DEMO_OUTPUT_FILENAMES = {
    "aml_demo_bundle_manifest": "aml_demo_bundle_manifest.json",
    "aml_demo_business_metric_table": "aml_demo_business_metric_table.json",
    "aml_demo_flow_report": "aml_demo_flow_report.md",
    "aml_demo_artifact_index": "aml_demo_artifact_index.json",
}

_SOURCE_ARTIFACTS = (
    ("run_summary", "run_summary.json", "run truth", True),
    ("alert_queue_policy", "alert_queue_policy.json", "review queue policy", True),
    ("alert_queue_rankings", "alert_queue_rankings.json", "ranked alert queue", True),
    ("analyst_review_scorecard", "analyst_review_scorecard.json", "review-budget scorecard", True),
    ("case_packet", "case_packet.json", "top case packet", True),
    ("review_capacity_sensitivity", "review_capacity_sensitivity.json", "review-capacity sensitivity", False),
    ("operating_point_contract", "operating_point_contract.json", "operating point", True),
    ("stream_risk_posture", "stream_risk_posture.json", "stream-risk posture", True),
    ("drift_recalibration_trigger", "drift_recalibration_trigger.json", "drift trigger", True),
    ("rolling_alert_quality_report", "rolling_alert_quality_report.json", "rolling alert quality", False),
    ("aml_benchmark_manifest", "aml_benchmark_manifest.json", "AML benchmark manifest", True),
    ("benchmark_release_gate", "benchmark_release_gate.json", "benchmark guard", True),
    ("aml_public_claim_guard", "aml_public_claim_guard.json", "public-claim guard", True),
    ("aml_failure_report", "aml_failure_report.json", "failure report", True),
    ("trace_model", "trace_model.json", "trace truth", False),
    ("protocol_conformance_report", "protocol_conformance_report.json", "eval protocol conformance", False),
)


def write_aml_review_queue_fixture(path: str | Path) -> Path:
    """Write a small synthetic PaySim-style AML review-queue fixture."""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, object]] = []
    suspicious_origins = [f"CUST_{index:02d}" for index in range(1, 13)]
    benign_origins = [f"CUST_{index:02d}" for index in range(13, 33)]

    step = 1
    for index, origin in enumerate(suspicious_origins, start=1):
        amount = 18.0 + float(index % 4)
        rows.append(
            {
                "step": step,
                "type": "TRANSFER",
                "amount": amount,
                "nameOrig": origin,
                "oldbalanceOrg": 2500.0 - 40.0 * index,
                "newbalanceOrig": 2500.0 - 40.0 * index - amount,
                "nameDest": "MULE_HUB",
                "oldbalanceDest": 75.0,
                "newbalanceDest": 75.0 + amount,
                "device_id": "shared-device-risk",
                "isFraud": 1,
            }
        )
        step += 1

    for destination in ("CASHOUT_1", "CASHOUT_2", "CASHOUT_3", "CASHOUT_4"):
        amount = 165.0 + float(step % 11)
        rows.append(
            {
                "step": step,
                "type": "CASH_OUT",
                "amount": amount,
                "nameOrig": "MULE_HUB",
                "oldbalanceOrg": 5000.0,
                "newbalanceOrig": 5000.0 - amount,
                "nameDest": destination,
                "oldbalanceDest": 120.0,
                "newbalanceDest": 120.0 + amount,
                "device_id": "shared-device-risk",
                "isFraud": 1,
            }
        )
        step += 1

    for origin in benign_origins:
        destination = f"MERCHANT_{(step % 6) + 1}"
        amount = 115.0 + float((step * 3) % 40)
        rows.append(
            {
                "step": step,
                "type": "PAYMENT",
                "amount": amount,
                "nameOrig": origin,
                "oldbalanceOrg": 6200.0 - 25.0 * step,
                "newbalanceOrig": 6200.0 - 25.0 * step - amount,
                "nameDest": destination,
                "oldbalanceDest": 800.0 + 15.0 * (step % 7),
                "newbalanceDest": 800.0 + 15.0 * (step % 7) + amount,
                "device_id": f"benign-device-{step % 5}",
                "isFraud": 0,
            }
        )
        step += 1

    for index in range(20):
        amount = 28.0 + float(index % 6)
        rows.append(
            {
                "step": step,
                "type": "TRANSFER",
                "amount": amount,
                "nameOrig": f"RING_{(index % 5) + 1}",
                "oldbalanceOrg": 1800.0 - 15.0 * index,
                "newbalanceOrig": 1800.0 - 15.0 * index - amount,
                "nameDest": f"RING_HUB_{(index % 2) + 1}",
                "oldbalanceDest": 150.0,
                "newbalanceDest": 150.0 + amount,
                "device_id": "shared-device-ring",
                "isFraud": 1 if index % 3 == 0 else 0,
            }
        )
        step += 1

    with target.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    return target


def build_aml_demo_bundle_artifacts(
    *,
    run_dir: str | Path,
    data_path: str | Path | None,
    command: str,
) -> dict[str, Any]:
    """Build and persist the Slice 15S AML review-queue demo bundle."""
    root = Path(run_dir)
    root.mkdir(parents=True, exist_ok=True)
    generated_at = _utc_now()
    payloads = _read_demo_source_payloads(root)

    business_metric_table = _build_business_metric_table(
        generated_at=generated_at,
        run_dir=root,
        payloads=payloads,
    )
    flow_report = _render_flow_report(
        run_dir=root,
        data_path=data_path,
        payloads=payloads,
        business_metric_table=business_metric_table,
    )

    business_path = write_json(
        root / AML_DEMO_OUTPUT_FILENAMES["aml_demo_business_metric_table"],
        business_metric_table,
        indent=2,
        ensure_ascii=False,
        sort_keys=True,
    )
    flow_path = root / AML_DEMO_OUTPUT_FILENAMES["aml_demo_flow_report"]
    flow_path.write_text(flow_report, encoding="utf-8")

    artifact_index = _build_artifact_index(root=root, generated_at=generated_at)
    index_path = write_json(
        root / AML_DEMO_OUTPUT_FILENAMES["aml_demo_artifact_index"],
        artifact_index,
        indent=2,
        ensure_ascii=False,
        sort_keys=True,
    )

    manifest = _build_bundle_manifest(
        generated_at=generated_at,
        run_dir=root,
        data_path=data_path,
        command=command,
        payloads=payloads,
        artifact_index=artifact_index,
        business_metric_table=business_metric_table,
    )
    manifest_path = write_json(
        root / AML_DEMO_OUTPUT_FILENAMES["aml_demo_bundle_manifest"],
        manifest,
        indent=2,
        ensure_ascii=False,
        sort_keys=True,
    )

    artifact_index = _build_artifact_index(root=root, generated_at=generated_at)
    index_path = write_json(
        root / AML_DEMO_OUTPUT_FILENAMES["aml_demo_artifact_index"],
        artifact_index,
        indent=2,
        ensure_ascii=False,
        sort_keys=True,
    )
    manifest["artifact_index_status"] = artifact_index["status"]
    manifest["missing_required_artifact_count"] = artifact_index["missing_required_artifact_count"]
    manifest["artifact_paths"]["aml_demo_bundle_manifest"] = AML_DEMO_OUTPUT_FILENAMES["aml_demo_bundle_manifest"]
    manifest_path = write_json(
        root / AML_DEMO_OUTPUT_FILENAMES["aml_demo_bundle_manifest"],
        manifest,
        indent=2,
        ensure_ascii=False,
        sort_keys=True,
    )

    return {
        "manifest": manifest,
        "business_metric_table": business_metric_table,
        "artifact_index": artifact_index,
        "flow_report": flow_report,
        "paths": {
            "aml_demo_bundle_manifest": str(manifest_path),
            "aml_demo_business_metric_table": str(business_path),
            "aml_demo_flow_report": str(flow_path),
            "aml_demo_artifact_index": str(index_path),
        },
    }


def read_aml_demo_bundle_artifacts(run_dir: str | Path) -> dict[str, Any]:
    root = Path(run_dir)
    payload: dict[str, Any] = {}
    for key, filename in AML_DEMO_OUTPUT_FILENAMES.items():
        path = root / filename
        if not path.exists():
            continue
        if path.suffix.lower() == ".json":
            try:
                payload[key] = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
        else:
            try:
                payload[key] = path.read_text(encoding="utf-8")
            except OSError:
                continue
    return payload


def _read_demo_source_payloads(root: Path) -> dict[str, dict[str, Any]]:
    return {
        "run_summary": _read_json(root / "run_summary.json"),
        "alert_queue_policy": _read_json(root / "alert_queue_policy.json"),
        "alert_queue_rankings": _read_json(root / "alert_queue_rankings.json"),
        "analyst_review_scorecard": _read_json(root / "analyst_review_scorecard.json"),
        "case_packet": _read_json(root / "case_packet.json"),
        "review_capacity_sensitivity": _read_json(root / "review_capacity_sensitivity.json"),
        "operating_point_contract": _read_json(root / "operating_point_contract.json"),
        "stream_risk_posture": _read_json(root / "stream_risk_posture.json"),
        "drift_recalibration_trigger": _read_json(root / "drift_recalibration_trigger.json"),
        "rolling_alert_quality_report": _read_json(root / "rolling_alert_quality_report.json"),
        "aml_benchmark_manifest": _read_json(root / "aml_benchmark_manifest.json"),
        "benchmark_release_gate": _read_json(root / "benchmark_release_gate.json"),
        "aml_public_claim_guard": _read_json(root / "aml_public_claim_guard.json"),
        "aml_failure_report": _read_json(root / "aml_failure_report.json"),
    }


def _build_bundle_manifest(
    *,
    generated_at: str,
    run_dir: Path,
    data_path: str | Path | None,
    command: str,
    payloads: dict[str, dict[str, Any]],
    artifact_index: dict[str, Any],
    business_metric_table: dict[str, Any],
) -> dict[str, Any]:
    summary = payloads["run_summary"]
    case_packet = payloads["case_packet"]
    public_claim_guard = payloads["aml_public_claim_guard"]
    failure_report = payloads["aml_failure_report"]
    benchmark_manifest = payloads["aml_benchmark_manifest"]
    stream_risk = payloads["stream_risk_posture"]
    drift_trigger = payloads["drift_recalibration_trigger"]
    alert_queue = payloads["alert_queue_rankings"]
    claim_posture = _claim_posture(public_claim_guard)
    status = "ready" if artifact_index["missing_required_artifact_count"] == 0 else "partial"
    if claim_posture == "blocked":
        status = "supporting_only"
    return {
        "schema_version": AML_DEMO_BUNDLE_MANIFEST_SCHEMA_VERSION,
        "generated_at": generated_at,
        "demo_id": AML_DEMO_ID,
        "status": status,
        "run_dir": str(run_dir),
        "data_path": str(data_path) if data_path is not None else None,
        "source": "demo_fixture_or_supplied_dataset" if data_path is not None else "existing_run",
        "command": command,
        "target_column": _get_nested(summary, "decision", "target_column"),
        "selected_model_family": _get_nested(summary, "decision", "selected_model_family"),
        "dataset_family": _clean_text(benchmark_manifest.get("dataset_family")),
        "benchmark_track": _clean_text(benchmark_manifest.get("benchmark_track")),
        "alert_queue": {
            "status": _clean_text(payloads["alert_queue_policy"].get("status"))
            or _clean_text(alert_queue.get("status")),
            "queue_count": int(alert_queue.get("queue_count", 0) or 0),
            "review_capacity_cases": int(payloads["alert_queue_policy"].get("review_capacity_cases", 0) or 0),
            "top_case_id": _clean_text(case_packet.get("case_id")),
            "top_case_entity": _clean_text(case_packet.get("focal_entity")),
        },
        "top_case_packet": {
            "case_id": _clean_text(case_packet.get("case_id")),
            "focal_entity": _clean_text(case_packet.get("focal_entity")),
            "priority_score": case_packet.get("priority_score"),
            "review_action": _clean_text(case_packet.get("review_action")),
            "path": "case_packet.json",
        },
        "drift_posture": {
            "status": _clean_text(stream_risk.get("status")),
            "stream_mode": _clean_text(stream_risk.get("stream_mode")),
            "trigger_recalibration": drift_trigger.get("trigger_recalibration"),
            "recommended_action": _clean_text(drift_trigger.get("recommended_action")),
            "path": "drift_recalibration_trigger.json",
        },
        "claim_guard": {
            "claim_posture": claim_posture,
            "supporting_public_claim_allowed": public_claim_guard.get("supporting_public_claim_allowed"),
            "paper_primary_claim_allowed": public_claim_guard.get("paper_primary_claim_allowed"),
            "broader_flagship_claim_allowed": public_claim_guard.get("broader_flagship_claim_allowed"),
            "blocked_reason_codes": list(public_claim_guard.get("blocked_reason_codes", []))
            if isinstance(public_claim_guard.get("blocked_reason_codes"), list)
            else [],
            "allowed_claims": list(public_claim_guard.get("allowed_claims", []))
            if isinstance(public_claim_guard.get("allowed_claims"), list)
            else [],
            "path": "aml_public_claim_guard.json",
        },
        "failure_report": {
            "primary_failure_kind": _clean_text(failure_report.get("primary_failure_kind")),
            "severity": _clean_text(failure_report.get("severity")),
            "public_safe_to_discuss": failure_report.get("public_safe_to_discuss"),
            "recommended_next_step": _clean_text(failure_report.get("recommended_next_step")),
            "path": "aml_failure_report.json",
        },
        "business_metric_table_status": business_metric_table.get("status"),
        "artifact_index_status": artifact_index.get("status"),
        "missing_required_artifact_count": artifact_index.get("missing_required_artifact_count"),
        "artifact_paths": {
            "aml_demo_bundle_manifest": "aml_demo_bundle_manifest.json",
            "aml_demo_business_metric_table": "aml_demo_business_metric_table.json",
            "aml_demo_flow_report": "aml_demo_flow_report.md",
            "aml_demo_artifact_index": "aml_demo_artifact_index.json",
            "case_packet": "case_packet.json",
            "benchmark_guard": "benchmark_release_gate.json",
            "public_claim_guard": "aml_public_claim_guard.json",
            "failure_report": "aml_failure_report.json",
        },
        "recommended_next_command": f"relaytic mission-control show --run-dir {run_dir} --format json",
        "summary": (
            "Relaytic-AML packaged one public-safe review-queue demo bundle with casework, drift, benchmark, "
            "public-claim guard, and failure-posture evidence."
        ),
    }


def _build_business_metric_table(
    *,
    generated_at: str,
    run_dir: Path,
    payloads: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    summary = payloads["run_summary"]
    benchmark = dict(summary.get("benchmark", {})) if isinstance(summary.get("benchmark"), dict) else {}
    decision = dict(summary.get("decision", {})) if isinstance(summary.get("decision"), dict) else {}
    casework = dict(summary.get("casework", {})) if isinstance(summary.get("casework"), dict) else {}
    stream_risk = dict(summary.get("stream_risk", {})) if isinstance(summary.get("stream_risk"), dict) else {}
    operating_point = dict(summary.get("operating_point", {})) if isinstance(summary.get("operating_point"), dict) else {}
    analyst_review_scorecard = payloads["analyst_review_scorecard"]
    review_capacity = payloads["review_capacity_sensitivity"]

    model_metrics = [
        _metric_row("selected_model_family", decision.get("selected_model_family"), "Model family selected by the run."),
        _metric_row("primary_metric", decision.get("primary_metric"), "Model-selection metric from the run contract."),
        _metric_row("comparison_metric", benchmark.get("comparison_metric"), "Benchmark comparison metric."),
        _metric_row("relaytic_rank", benchmark.get("relaytic_rank"), "Relaytic position in the local benchmark table."),
        _metric_row("selected_threshold", operating_point.get("selected_threshold"), "Decision threshold selected for the operating point."),
    ]
    operational_metrics = [
        _metric_row("queue_count", casework.get("queue_count"), "Entity cases in the review queue."),
        _metric_row("review_capacity_cases", casework.get("review_capacity_cases"), "Cases recommended for immediate review."),
        _metric_row("estimated_review_hours", casework.get("estimated_review_hours"), "Estimated hours for the selected review queue."),
        _metric_row("top_case_priority_score", casework.get("top_case_priority_score"), "Priority score for the top case packet."),
        _metric_row("review_typology_coverage", casework.get("review_typology_coverage"), "Typology coverage among immediate-review cases."),
        _metric_row("drift_trigger_action", stream_risk.get("trigger_action"), "Current drift or threshold action."),
    ]
    return {
        "schema_version": AML_DEMO_BUSINESS_METRIC_TABLE_SCHEMA_VERSION,
        "generated_at": generated_at,
        "demo_id": AML_DEMO_ID,
        "status": "ready" if casework.get("queue_count") else "partial",
        "run_dir": str(run_dir),
        "model_metrics": model_metrics,
        "operational_review_metrics": operational_metrics,
        "review_capacity_scenarios": list(review_capacity.get("rows", []))
        if isinstance(review_capacity.get("rows"), list)
        else [],
        "assumptions": [
            {
                "assumption_id": "analyst_hours_per_case",
                "value": analyst_review_scorecard.get("analyst_hours_per_case"),
                "source": "analyst_review_scorecard.json",
            },
            {
                "assumption_id": "slice_boundary",
                "value": "15S packages demo metrics; 15T owns stronger business-value proof and operational guards.",
                "source": "docs/build_slices/phase_15t.md",
            },
        ],
        "claim_boundary": "Model metrics and operational review-budget metrics are separate; this demo does not claim analyst-hour ROI.",
        "summary": "Relaytic-AML separates model-score posture from review-queue operating metrics for the flagship demo.",
    }


def _build_artifact_index(*, root: Path, generated_at: str) -> dict[str, Any]:
    required_entries = [_artifact_entry(root, artifact_id, filename, role, required) for artifact_id, filename, role, required in _SOURCE_ARTIFACTS]
    bundle_entries = [
        _artifact_entry(root, artifact_id, filename, "15S demo bundle output", True)
        for artifact_id, filename in AML_DEMO_OUTPUT_FILENAMES.items()
    ]
    all_entries = [*required_entries, *bundle_entries]
    missing_required = [
        str(item["artifact_id"])
        for item in all_entries
        if bool(item.get("required")) and not bool(item.get("exists"))
    ]
    return {
        "schema_version": AML_DEMO_ARTIFACT_INDEX_SCHEMA_VERSION,
        "generated_at": generated_at,
        "demo_id": AML_DEMO_ID,
        "status": "ready" if not missing_required else "incomplete",
        "run_dir": str(root),
        "required_artifacts": [item for item in required_entries if bool(item.get("required"))],
        "supporting_artifacts": [item for item in required_entries if not bool(item.get("required"))],
        "bundle_artifacts": bundle_entries,
        "missing_required_artifacts": missing_required,
        "missing_required_artifact_count": len(missing_required),
        "summary": (
            "All required AML demo-bundle artifacts are present."
            if not missing_required
            else f"Missing required AML demo-bundle artifacts: {', '.join(missing_required)}."
        ),
    }


def _render_flow_report(
    *,
    run_dir: Path,
    data_path: str | Path | None,
    payloads: dict[str, dict[str, Any]],
    business_metric_table: dict[str, Any],
) -> str:
    summary = payloads["run_summary"]
    case_packet = payloads["case_packet"]
    public_claim_guard = payloads["aml_public_claim_guard"]
    failure_report = payloads["aml_failure_report"]
    benchmark_manifest = payloads["aml_benchmark_manifest"]
    alert_queue = payloads["alert_queue_rankings"]
    drift_trigger = payloads["drift_recalibration_trigger"]
    allowed_claims = [
        str(item).strip()
        for item in public_claim_guard.get("allowed_claims", [])
        if str(item).strip()
    ] if isinstance(public_claim_guard.get("allowed_claims"), list) else []
    blocked_reason_codes = [
        str(item).strip()
        for item in public_claim_guard.get("blocked_reason_codes", [])
        if str(item).strip()
    ] if isinstance(public_claim_guard.get("blocked_reason_codes"), list) else []
    model_rows = [
        f"| `{row.get('metric_id')}` | `{_display_value(row.get('value'))}` | {row.get('detail') or ''} |"
        for row in business_metric_table.get("model_metrics", [])
        if isinstance(row, dict)
    ]
    operational_rows = [
        f"| `{row.get('metric_id')}` | `{_display_value(row.get('value'))}` | {row.get('detail') or ''} |"
        for row in business_metric_table.get("operational_review_metrics", [])
        if isinstance(row, dict)
    ]
    return "\n".join(
        [
            "# Relaytic-AML Review Queue Demo",
            "",
            f"- Demo id: `{AML_DEMO_ID}`",
            f"- Run directory: `{run_dir}`",
            f"- Fixture/data: `{data_path or 'existing run data'}`",
            f"- Dataset family: `{benchmark_manifest.get('dataset_family') or 'unknown'}`",
            f"- Target: `{_get_nested(summary, 'decision', 'target_column') or 'unknown'}`",
            "",
            "## Run Flow",
            "",
            "```text",
            "fixture data -> governed run -> entity graph -> alert queue -> case packet",
            "            -> operating point -> drift posture -> benchmark guard -> public-claim guard",
            "```",
            "",
            "## Model Metrics",
            "",
            "| Metric | Value | Detail |",
            "| --- | --- | --- |",
            *(model_rows or ["| `not_available` | `unknown` | No model metrics were materialized. |"]),
            "",
            "## Operational Review Metrics",
            "",
            "| Metric | Value | Detail |",
            "| --- | --- | --- |",
            *(operational_rows or ["| `not_available` | `unknown` | No review-budget metrics were materialized. |"]),
            "",
            "## Alert Queue",
            "",
            f"- Queue count: `{alert_queue.get('queue_count', 0)}`",
            f"- Review capacity: `{alert_queue.get('review_capacity_cases', 0)}`",
            f"- Top case: `{case_packet.get('case_id') or 'unknown'}`",
            f"- Focal entity: `{case_packet.get('focal_entity') or 'unknown'}`",
            f"- Review action: `{case_packet.get('review_action') or 'unknown'}`",
            f"- Case packet path: `case_packet.json`",
            "",
            "## Drift Posture",
            "",
            f"- Trigger recalibration: `{drift_trigger.get('trigger_recalibration')}`",
            f"- Recommended action: `{drift_trigger.get('recommended_action') or 'unknown'}`",
            f"- Drift posture path: `drift_recalibration_trigger.json`",
            "",
            "## Safe Claims",
            "",
            f"- Supporting public claim allowed: `{public_claim_guard.get('supporting_public_claim_allowed')}`",
            f"- Paper-primary claim allowed: `{public_claim_guard.get('paper_primary_claim_allowed')}`",
            f"- Broader flagship claim allowed: `{public_claim_guard.get('broader_flagship_claim_allowed')}`",
            f"- Allowed claims: `{'; '.join(allowed_claims) if allowed_claims else 'none'}`",
            f"- Blocked reason codes: `{', '.join(blocked_reason_codes) if blocked_reason_codes else 'none'}`",
            f"- Public-claim guard path: `aml_public_claim_guard.json`",
            "",
            "## Failure Posture",
            "",
            f"- Primary failure kind: `{failure_report.get('primary_failure_kind') or 'none'}`",
            f"- Severity: `{failure_report.get('severity') or 'unknown'}`",
            f"- Recommended next step: `{failure_report.get('recommended_next_step') or 'none'}`",
            f"- Failure report path: `aml_failure_report.json`",
            "",
        ]
    )


def _artifact_entry(root: Path, artifact_id: str, filename: str, role: str, required: bool) -> dict[str, Any]:
    path = root / filename
    return {
        "artifact_id": artifact_id,
        "path": filename,
        "role": role,
        "required": required,
        "exists": path.exists(),
        "size_bytes": path.stat().st_size if path.exists() and path.is_file() else None,
    }


def _metric_row(metric_id: str, value: Any, detail: str) -> dict[str, Any]:
    return {
        "metric_id": metric_id,
        "value": value,
        "detail": detail,
    }


def _claim_posture(public_claim_guard: dict[str, Any]) -> str:
    if bool(public_claim_guard.get("broader_flagship_claim_allowed")):
        return "broader_flagship_allowed"
    if bool(public_claim_guard.get("paper_primary_claim_allowed")):
        return "paper_primary_allowed"
    if bool(public_claim_guard.get("supporting_public_claim_allowed")):
        return "supporting_only"
    return "blocked"


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return payload if isinstance(payload, dict) else {}


def _get_nested(payload: dict[str, Any], *keys: str) -> Any:
    cursor: Any = payload
    for key in keys:
        if not isinstance(cursor, dict):
            return None
        cursor = cursor.get(key)
    return cursor


def _display_value(value: Any) -> str:
    if value is None:
        return "unknown"
    if isinstance(value, float):
        return f"{value:.6g}"
    return str(value)


def _clean_text(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text or text.lower() in {"none", "null"}:
        return None
    return text


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()
