"""Raw graph, flattened graph, and subgraph ingestion artifacts for Relaytic-AML."""

from __future__ import annotations

import csv
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from typing import Any

from relaytic.core.json_utils import write_json


AML_GRAPH_LOADER_MANIFEST_SCHEMA_VERSION = "relaytic.aml_graph_loader_manifest.v1"
AML_GRAPH_PROVENANCE_REPORT_SCHEMA_VERSION = "relaytic.aml_graph_provenance_report.v1"
AML_SUBGRAPH_TASK_MANIFEST_SCHEMA_VERSION = "relaytic.aml_subgraph_task_manifest.v1"
AML_GRAPH_CLAIM_SCOPE_SCHEMA_VERSION = "relaytic.aml_graph_claim_scope.v1"
AML_PUBLIC_GRAPH_BENCHMARK_CATALOG_SCHEMA_VERSION = "relaytic.aml_public_graph_benchmark_catalog.v1"

AML_GRAPH_LOADER_FILENAMES = {
    "aml_graph_loader_manifest": "aml_graph_loader_manifest.json",
    "aml_graph_provenance_report": "aml_graph_provenance_report.json",
    "aml_subgraph_task_manifest": "aml_subgraph_task_manifest.json",
    "aml_graph_claim_scope": "aml_graph_claim_scope.json",
    "aml_public_graph_benchmark_catalog": "aml_public_graph_benchmark_catalog.json",
}

_NORMALIZED_EDGE_TABLE_FILENAME = "aml_graph_loader_edge_table.csv"
_SUPPORTED_TABULAR_SUFFIXES = {".csv", ".tsv", ".txt"}
_GRAPH_SUFFIXES = _SUPPORTED_TABULAR_SUFFIXES | {".jsonl", ".ndjson", ".json"}
_ACTIVE_STATUSES = {"active", "ok", "ready", "pass", "warn", "supporting_only", "guarded"}
_INACTIVE_STATUSES = {"", "not_available", "not_applicable", "inactive", "blocked"}


def build_aml_graph_loader_artifacts(
    *,
    run_dir: str | Path,
    graph_path: str | Path | None = None,
    data_path: str | Path | None = None,
) -> dict[str, dict[str, Any]]:
    """Build Slice 15V graph-loader artifacts without writing them."""
    root = Path(run_dir)
    generated_at = _utc_now()
    source_path = _resolve_source_path(root=root, graph_path=graph_path, data_path=data_path)
    source = _inspect_graph_source(root=root, source_path=source_path)
    return _build_artifacts_from_source(
        root=root,
        generated_at=generated_at,
        source=source,
        normalized_edge_table=None,
    )


def sync_aml_graph_loader_artifacts(
    run_dir: str | Path,
    *,
    graph_path: str | Path | None = None,
    data_path: str | Path | None = None,
    context_bundle: dict[str, Any] | None = None,
    task_contract_bundle: dict[str, Any] | None = None,
    sync_entity_graph: bool = True,
    force_aml_active: bool = False,
) -> dict[str, Path]:
    """Build and write Slice 15V graph-loader artifacts for a run."""
    root = Path(run_dir)
    root.mkdir(parents=True, exist_ok=True)
    generated_at = _utc_now()
    source_path = _resolve_source_path(root=root, graph_path=graph_path, data_path=data_path)
    source = _inspect_graph_source(root=root, source_path=source_path)
    normalized_edge_table = None
    if source.get("loader_can_construct_graph"):
        normalized_edge_table = _write_normalized_edge_table(root=root, source=source)
        if sync_entity_graph and normalized_edge_table is not None:
            _sync_existing_entity_graph(
                root=root,
                normalized_edge_table=normalized_edge_table,
                context_bundle=context_bundle,
                task_contract_bundle=task_contract_bundle,
                force_aml_active=force_aml_active,
            )
    artifacts = _build_artifacts_from_source(
        root=root,
        generated_at=generated_at,
        source=source,
        normalized_edge_table=normalized_edge_table,
    )
    return {
        key: write_json(
            root / filename,
            artifacts[key],
            indent=2,
            ensure_ascii=False,
            sort_keys=True,
        )
        for key, filename in AML_GRAPH_LOADER_FILENAMES.items()
    }


def read_aml_graph_loader_artifacts(run_dir: str | Path) -> dict[str, Any]:
    """Read Slice 15V graph-loader artifacts if present."""
    root = Path(run_dir)
    payload: dict[str, Any] = {}
    for key, filename in AML_GRAPH_LOADER_FILENAMES.items():
        path = root / filename
        if not path.exists():
            continue
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if isinstance(value, dict):
            payload[key] = value
    return payload


def render_aml_graph_loader_markdown(bundle: dict[str, Any]) -> str:
    """Render a compact human-facing graph-loader summary."""
    manifest = dict(bundle.get("aml_graph_loader_manifest", {}))
    provenance = dict(bundle.get("aml_graph_provenance_report", {}))
    subgraph = dict(bundle.get("aml_subgraph_task_manifest", {}))
    claim_scope = dict(bundle.get("aml_graph_claim_scope", {}))
    catalog = dict(bundle.get("aml_public_graph_benchmark_catalog", {}))
    rows = [dict(item) for item in catalog.get("rows", []) if isinstance(item, dict)]
    return "\n".join(
        [
            "# Relaytic-AML Graph Loader",
            "",
            f"- Loader status: `{manifest.get('status') or 'unknown'}`",
            f"- Input mode: `{manifest.get('graph_input_mode') or 'unknown'}`",
            f"- Graph family: `{manifest.get('graph_family') or 'unknown'}`",
            f"- Loader can construct graph: `{manifest.get('loader_can_construct_graph')}`",
            f"- Benchmark-ready graph labels: `{manifest.get('benchmark_label_provenance_ready')}`",
            f"- Subgraph task status: `{subgraph.get('status') or 'unknown'}`",
            f"- Source files inspected: `{provenance.get('source_file_count', 0)}`",
            f"- Raw graph benchmark claim allowed: `{claim_scope.get('raw_graph_benchmark_claim_allowed')}`",
            f"- Subgraph benchmark claim allowed: `{claim_scope.get('subgraph_benchmark_claim_allowed')}`",
            f"- Graph SOTA claim allowed: `{claim_scope.get('graph_sota_claim_allowed')}`",
            "",
            "## Benchmark Catalog",
            *(
                f"- `{row.get('benchmark_family')}` support=`{row.get('support_level')}` claim=`{row.get('public_claim_level')}`"
                for row in rows[:8]
            ),
            *(["- none"] if not rows else []),
            "",
        ]
    )


def _build_artifacts_from_source(
    *,
    root: Path,
    generated_at: str,
    source: dict[str, Any],
    normalized_edge_table: Path | None,
) -> dict[str, dict[str, Any]]:
    manifest = _build_loader_manifest(
        root=root,
        generated_at=generated_at,
        source=source,
        normalized_edge_table=normalized_edge_table,
    )
    provenance = _build_provenance_report(
        root=root,
        generated_at=generated_at,
        source=source,
        manifest=manifest,
        normalized_edge_table=normalized_edge_table,
    )
    subgraph = _build_subgraph_task_manifest(
        root=root,
        generated_at=generated_at,
        source=source,
        manifest=manifest,
    )
    claim_scope = _build_graph_claim_scope(
        root=root,
        generated_at=generated_at,
        manifest=manifest,
        subgraph=subgraph,
    )
    catalog = _build_public_graph_benchmark_catalog(
        root=root,
        generated_at=generated_at,
        manifest=manifest,
        subgraph=subgraph,
        claim_scope=claim_scope,
    )
    return {
        "aml_graph_loader_manifest": manifest,
        "aml_graph_provenance_report": provenance,
        "aml_subgraph_task_manifest": subgraph,
        "aml_graph_claim_scope": claim_scope,
        "aml_public_graph_benchmark_catalog": catalog,
    }


def _build_loader_manifest(
    *,
    root: Path,
    generated_at: str,
    source: dict[str, Any],
    normalized_edge_table: Path | None,
) -> dict[str, Any]:
    role_counts = {
        role: len(items)
        for role, items in dict(source.get("roles", {})).items()
        if isinstance(items, list) and items
    }
    missing = list(source.get("missing_required_roles", []))
    blocked = list(source.get("blocked_reason_codes", []))
    normalized_path = _display_path(normalized_edge_table, root) if normalized_edge_table else None
    summary = _loader_summary(source=source, missing=missing)
    return {
        "schema_version": AML_GRAPH_LOADER_MANIFEST_SCHEMA_VERSION,
        "generated_at": generated_at,
        "status": source.get("status"),
        "run_dir": str(root),
        "source_kind": source.get("source_kind"),
        "source_path_display": source.get("source_path_display"),
        "graph_input_mode": source.get("graph_input_mode"),
        "graph_family": source.get("graph_family"),
        "loader_can_construct_graph": bool(source.get("loader_can_construct_graph")),
        "benchmark_label_provenance_ready": bool(source.get("benchmark_label_provenance_ready")),
        "raw_graph_bundle_ready": bool(source.get("raw_graph_bundle_ready")),
        "flattened_graph_ready": bool(source.get("flattened_graph_ready")),
        "subgraph_pack_ready": bool(source.get("subgraph_pack_ready")),
        "required_roles": list(source.get("required_roles", [])),
        "present_roles": sorted(role_counts),
        "role_counts": role_counts,
        "missing_required_roles": missing,
        "blocked_reason_codes": blocked,
        "recovery_instructions": _recovery_instructions(missing, blocked),
        "node_id_columns": sorted(_unique(source.get("node_id_columns", []))),
        "edge_source_columns": sorted(_unique(source.get("edge_source_columns", []))),
        "edge_destination_columns": sorted(_unique(source.get("edge_destination_columns", []))),
        "time_columns": sorted(_unique(source.get("time_columns", []))),
        "label_columns": sorted(_unique(source.get("label_columns", []))),
        "subgraph_id_columns": sorted(_unique(source.get("subgraph_id_columns", []))),
        "file_roles": _public_file_roles(source),
        "normalized_edge_table_path": normalized_path,
        "normalization_performed": normalized_path is not None,
        "claim_boundary": (
            "Loader evidence supports ingestion and provenance claims only. Raw graph, subgraph, or graph-SOTA "
            "benchmark claims still require a benchmark run and public claim gate."
        ),
        "summary": summary,
    }


def _build_provenance_report(
    *,
    root: Path,
    generated_at: str,
    source: dict[str, Any],
    manifest: dict[str, Any],
    normalized_edge_table: Path | None,
) -> dict[str, Any]:
    files = [_public_file_info(item) for item in source.get("files", []) if isinstance(item, dict)]
    transformations = [
        {
            "transformation_id": "graph_source_inspection",
            "operation": "header_schema_hash_and_role_detection",
            "changes_raw_values": False,
            "output_artifact": "aml_graph_loader_manifest.json",
        }
    ]
    if normalized_edge_table is not None:
        transformations.append(
            {
                "transformation_id": "normalized_edge_table",
                "operation": "edge_list_to_relaytic_source_destination_table",
                "changes_raw_values": False,
                "output_artifact": _display_path(normalized_edge_table, root),
                "lineage": {
                    "source_role": "edges",
                    "label_join_role": "labels",
                    "time_join_role": "features",
                    "join_key": "node_id_or_transaction_id",
                },
            }
        )
    return {
        "schema_version": AML_GRAPH_PROVENANCE_REPORT_SCHEMA_VERSION,
        "generated_at": generated_at,
        "status": "active" if files else "not_available",
        "run_dir": str(root),
        "source_path_display": source.get("source_path_display"),
        "source_file_count": len(files),
        "source_files": files,
        "id_lineage": {
            "node_id_columns": manifest.get("node_id_columns", []),
            "edge_source_columns": manifest.get("edge_source_columns", []),
            "edge_destination_columns": manifest.get("edge_destination_columns", []),
            "subgraph_id_columns": manifest.get("subgraph_id_columns", []),
        },
        "time_lineage": {
            "time_columns": manifest.get("time_columns", []),
            "time_required_for_public_graph_benchmark": True,
            "time_available": bool(manifest.get("time_columns")),
        },
        "label_lineage": {
            "label_columns": manifest.get("label_columns", []),
            "label_required_for_public_graph_benchmark": True,
            "label_available": bool(manifest.get("label_columns")),
        },
        "transformations": transformations,
        "privacy_posture": "external absolute paths are redacted to file or run-relative displays",
        "summary": (
            f"Relaytic inspected `{len(files)}` graph source file(s) and preserved ID, time, label, and edge-role provenance."
            if files
            else "Relaytic did not find graph source files to inspect."
        ),
    }


def _build_subgraph_task_manifest(
    *,
    root: Path,
    generated_at: str,
    source: dict[str, Any],
    manifest: dict[str, Any],
) -> dict[str, Any]:
    existing_subgraph = _read_json(root / "subgraph_risk_report.json")
    existing_proxy = _artifact_active(existing_subgraph) and (
        bool(existing_subgraph.get("selected_subgraphs")) or bool(existing_subgraph.get("candidate_comparison"))
    )
    subgraph_pack_ready = bool(source.get("subgraph_pack_ready"))
    raw_ready = bool(source.get("raw_graph_bundle_ready"))
    if subgraph_pack_ready:
        status = "subgraph_task_ready"
        task_level = "subgraph"
        blocked: list[str] = []
        support_level = "supported"
    elif raw_ready:
        status = "ego_subgraph_proxy_ready"
        task_level = "node_or_ego_subgraph_proxy"
        blocked = ["subgraph_labels_missing"]
        support_level = "proxy"
    elif existing_proxy:
        status = "existing_subgraph_proxy_only"
        task_level = "derived_case_subgraph_proxy"
        blocked = ["raw_subgraph_pack_missing"]
        support_level = "proxy"
    else:
        status = "blocked"
        task_level = "not_available"
        blocked = ["subgraph_pack_or_graph_proxy_missing"]
        support_level = "blocked"
    candidate_files = [
        _public_file_info(item)
        for item in source.get("files", [])
        if isinstance(item, dict) and item.get("role") in {"subgraphs", "labels"}
    ]
    return {
        "schema_version": AML_SUBGRAPH_TASK_MANIFEST_SCHEMA_VERSION,
        "generated_at": generated_at,
        "status": status,
        "run_dir": str(root),
        "task_level": task_level,
        "support_level": support_level,
        "subgraph_pack_ready": subgraph_pack_ready,
        "existing_case_subgraph_proxy": existing_proxy,
        "node_or_ego_subgraph_proxy_ready": raw_ready or existing_proxy,
        "subgraph_id_columns": manifest.get("subgraph_id_columns", []),
        "label_columns": manifest.get("label_columns", []),
        "candidate_files": candidate_files,
        "blocked_reason_codes": blocked,
        "recovery_instructions": _recovery_instructions([], blocked),
        "claim_boundary": (
            "Derived suspicious-neighborhood evidence is a useful proxy. Elliptic2-style subgraph benchmark claims "
            "require explicit subgraph IDs, subgraph labels, and benchmark execution."
        ),
        "summary": (
            "Relaytic can represent a labeled subgraph task from the inspected source."
            if subgraph_pack_ready
            else "Relaytic has only proxy subgraph evidence until a labeled subgraph pack is supplied."
            if raw_ready or existing_proxy
            else "Relaytic cannot represent a subgraph task from the current source."
        ),
    }


def _build_graph_claim_scope(
    *,
    root: Path,
    generated_at: str,
    manifest: dict[str, Any],
    subgraph: dict[str, Any],
) -> dict[str, Any]:
    release_gate = _read_json(root / "benchmark_release_gate.json")
    scorecard = _read_json(root / "aml_benchmark_relevance_scorecard.json")
    raw_loader_claim_allowed = bool(manifest.get("raw_graph_bundle_ready"))
    flattened_proxy_claim_allowed = bool(manifest.get("flattened_graph_ready") or manifest.get("raw_graph_bundle_ready"))
    subgraph_loader_claim_allowed = bool(subgraph.get("status") == "subgraph_task_ready")
    benchmark_safe = bool(release_gate.get("safe_to_cite_publicly"))
    hard_benchmark_claim = bool(scorecard.get("hard_benchmark_claim_allowed"))
    raw_benchmarked = _scorecard_family_supported(scorecard, "elliptic_style_raw_graph_aml")
    subgraph_benchmarked = _scorecard_family_supported(scorecard, "elliptic2_style_subgraph_aml")
    raw_graph_benchmark_claim_allowed = bool(raw_loader_claim_allowed and benchmark_safe and hard_benchmark_claim and raw_benchmarked)
    subgraph_benchmark_claim_allowed = bool(subgraph_loader_claim_allowed and benchmark_safe and hard_benchmark_claim and subgraph_benchmarked)
    graph_sota_claim_allowed = bool(raw_graph_benchmark_claim_allowed and subgraph_benchmark_claim_allowed)
    blocked = []
    if not raw_loader_claim_allowed:
        blocked.append("raw_graph_loader_not_active")
    if raw_loader_claim_allowed and not raw_graph_benchmark_claim_allowed:
        blocked.append("raw_graph_benchmark_not_run_or_not_claim_gated")
    if not subgraph_loader_claim_allowed:
        blocked.append("labeled_subgraph_loader_not_active")
    if subgraph_loader_claim_allowed and not subgraph_benchmark_claim_allowed:
        blocked.append("subgraph_benchmark_not_run_or_not_claim_gated")
    if not graph_sota_claim_allowed:
        blocked.append("graph_sota_claim_not_benchmarked")
    allowed_claims = []
    if raw_loader_claim_allowed:
        allowed_claims.append("Relaytic-AML can ingest a raw graph bundle with explicit edge, feature, label, and time provenance.")
    if flattened_proxy_claim_allowed:
        allowed_claims.append("Relaytic-AML can label flattened graph snapshots as proxy evidence instead of raw graph benchmark evidence.")
    if subgraph_loader_claim_allowed:
        allowed_claims.append("Relaytic-AML can represent a labeled subgraph task from the supplied graph pack.")
    return {
        "schema_version": AML_GRAPH_CLAIM_SCOPE_SCHEMA_VERSION,
        "generated_at": generated_at,
        "status": "active" if allowed_claims else "blocked",
        "run_dir": str(root),
        "graph_input_mode": manifest.get("graph_input_mode"),
        "raw_graph_loader_claim_allowed": raw_loader_claim_allowed,
        "flattened_graph_proxy_claim_allowed": flattened_proxy_claim_allowed,
        "subgraph_loader_claim_allowed": subgraph_loader_claim_allowed,
        "raw_graph_benchmark_claim_allowed": raw_graph_benchmark_claim_allowed,
        "subgraph_benchmark_claim_allowed": subgraph_benchmark_claim_allowed,
        "graph_sota_claim_allowed": graph_sota_claim_allowed,
        "benchmark_release_gate_safe": benchmark_safe,
        "hard_aml_benchmark_claim_allowed": hard_benchmark_claim,
        "allowed_claims": allowed_claims,
        "blocked_claims": [
            "raw Elliptic-style benchmark performance",
            "Elliptic2-style labeled subgraph benchmark performance",
            "graph SOTA or leaderboard claims",
        ] if blocked else [],
        "blocked_reason_codes": sorted(_unique(blocked)),
        "evidence_refs": _existing_refs(
            root,
            [
                "aml_graph_loader_manifest.json",
                "aml_graph_provenance_report.json",
                "aml_subgraph_task_manifest.json",
                "benchmark_release_gate.json",
                "aml_benchmark_relevance_scorecard.json",
            ],
        ),
        "summary": (
            "Relaytic-AML has graph-loader evidence, but public graph benchmark and SOTA claims remain blocked until benchmarked and claim-gated."
            if allowed_claims
            else "Relaytic-AML has no active graph-loader claim scope for the current run."
        ),
    }


def _build_public_graph_benchmark_catalog(
    *,
    root: Path,
    generated_at: str,
    manifest: dict[str, Any],
    subgraph: dict[str, Any],
    claim_scope: dict[str, Any],
) -> dict[str, Any]:
    raw_ready = bool(manifest.get("raw_graph_bundle_ready"))
    flattened_ready = bool(manifest.get("flattened_graph_ready"))
    graph_construct = bool(manifest.get("loader_can_construct_graph"))
    subgraph_ready = bool(subgraph.get("status") == "subgraph_task_ready")
    graph_family = str(manifest.get("graph_family") or "")
    rows = [
        {
            "benchmark_family": "elliptic_style_raw_graph_aml",
            "support_level": "supported" if raw_ready else "blocked",
            "covered_by_current_run": raw_ready,
            "proxy_usable": False,
            "public_claim_level": "loader_supported_benchmark_not_run" if raw_ready else "not_supported",
            "blocked_reason_codes": [] if raw_ready else ["raw_elliptic_edge_feature_label_time_bundle_missing"],
            "evidence_refs": _existing_refs(root, ["aml_graph_loader_manifest.json", "aml_graph_provenance_report.json"]),
            "notes": "Raw Elliptic-style support requires edge, feature, label, and time provenance from a multi-file graph bundle.",
        },
        {
            "benchmark_family": "elliptic_style_flattened_graph_aml",
            "support_level": "supported" if flattened_ready else "proxy" if raw_ready else "blocked",
            "covered_by_current_run": flattened_ready,
            "proxy_usable": raw_ready,
            "public_claim_level": "current_run_supported" if flattened_ready else "derived_proxy" if raw_ready else "not_supported",
            "blocked_reason_codes": [] if flattened_ready or raw_ready else ["flattened_edge_table_missing"],
            "evidence_refs": _existing_refs(root, ["aml_graph_loader_manifest.json", "entity_graph_profile.json"]),
            "notes": "Flattened Elliptic-style graph support is proxy-compatible but not equivalent to raw graph leaderboard evidence.",
        },
        {
            "benchmark_family": "elliptic2_style_subgraph_aml",
            "support_level": "supported" if subgraph_ready else "proxy" if subgraph.get("support_level") == "proxy" else "blocked",
            "covered_by_current_run": subgraph_ready,
            "proxy_usable": subgraph.get("support_level") == "proxy",
            "public_claim_level": "loader_supported_benchmark_not_run" if subgraph_ready else "proxy_only" if subgraph.get("support_level") == "proxy" else "not_supported",
            "blocked_reason_codes": list(subgraph.get("blocked_reason_codes", [])),
            "evidence_refs": _existing_refs(root, ["aml_subgraph_task_manifest.json", "subgraph_risk_report.json"]),
            "notes": "Elliptic2-style claims require labeled subgraph task provenance and benchmark execution.",
        },
        {
            "benchmark_family": "amlsim_style_synthetic_bank_graph",
            "support_level": "supported" if graph_construct and "amlsim" in graph_family else "proxy" if graph_construct else "blocked",
            "covered_by_current_run": graph_construct and "amlsim" in graph_family,
            "proxy_usable": graph_construct,
            "public_claim_level": "current_run_supported" if graph_construct and "amlsim" in graph_family else "proxy_only" if graph_construct else "not_supported",
            "blocked_reason_codes": [] if graph_construct else ["bank_graph_edge_source_missing"],
            "evidence_refs": _existing_refs(root, ["aml_graph_loader_manifest.json", "counterparty_network_report.json"]),
            "notes": "AMLSim-style synthetic bank graph support is useful for reproducible demos but remains separate from public raw graph benchmarks.",
        },
    ]
    supported_count = sum(1 for row in rows if row["support_level"] == "supported")
    proxy_count = sum(1 for row in rows if row["support_level"] == "proxy")
    return {
        "schema_version": AML_PUBLIC_GRAPH_BENCHMARK_CATALOG_SCHEMA_VERSION,
        "generated_at": generated_at,
        "status": "active" if supported_count or proxy_count else "blocked",
        "run_dir": str(root),
        "supported_family_count": supported_count,
        "proxy_family_count": proxy_count,
        "blocked_family_count": sum(1 for row in rows if row["support_level"] == "blocked"),
        "raw_graph_benchmark_claim_allowed": claim_scope.get("raw_graph_benchmark_claim_allowed"),
        "subgraph_benchmark_claim_allowed": claim_scope.get("subgraph_benchmark_claim_allowed"),
        "graph_sota_claim_allowed": claim_scope.get("graph_sota_claim_allowed"),
        "rows": rows,
        "summary": (
            f"Relaytic-AML graph catalog marks `{supported_count}` family/families supported and `{proxy_count}` proxy-supported."
        ),
    }


def _inspect_graph_source(*, root: Path, source_path: Path | None) -> dict[str, Any]:
    if source_path is None:
        return _empty_source("not_available", "No graph path or run dataset was available.")
    path = source_path if source_path.is_absolute() else root / source_path
    if not path.exists():
        return _empty_source("not_available", f"Graph source was not found: {path.name}")
    if path.is_dir():
        files = [
            _inspect_graph_file(file_path=file_path, root=root)
            for file_path in sorted(path.rglob("*"))
            if file_path.is_file() and file_path.suffix.lower() in _GRAPH_SUFFIXES
        ]
        source_kind = "directory"
    else:
        files = [_inspect_graph_file(file_path=path, root=root)]
        source_kind = "file"
    roles: dict[str, list[dict[str, Any]]] = {}
    for file_info in files:
        roles.setdefault(str(file_info.get("role") or "unknown"), []).append(file_info)
    return _classify_source(
        root=root,
        source_path=path,
        source_kind=source_kind,
        files=files,
        roles=roles,
    )


def _classify_source(
    *,
    root: Path,
    source_path: Path,
    source_kind: str,
    files: list[dict[str, Any]],
    roles: dict[str, list[dict[str, Any]]],
) -> dict[str, Any]:
    has_edges = bool(roles.get("edges"))
    has_features = bool(roles.get("features"))
    has_labels = bool(roles.get("labels"))
    has_subgraphs = bool(roles.get("subgraphs"))
    time_columns = _role_columns(files, "time_columns")
    label_columns = _role_columns(files, "label_columns")
    subgraph_id_columns = _role_columns(files, "subgraph_id_columns")
    node_id_columns = _role_columns(files, "id_columns")
    edge_source_columns = [col for item in roles.get("edges", []) for col in item.get("edge_source_columns", [])]
    edge_destination_columns = [col for item in roles.get("edges", []) for col in item.get("edge_destination_columns", [])]
    raw_missing = []
    if not has_edges:
        raw_missing.append("edges")
    if not has_features:
        raw_missing.append("features")
    if not has_labels:
        raw_missing.append("labels")
    if not time_columns:
        raw_missing.append("time")
    blocked: list[str] = []
    flattened_ready = source_kind == "file" and has_edges and not has_features and not has_labels and bool(label_columns or time_columns)
    if has_subgraphs and (label_columns or has_labels) and subgraph_id_columns:
        status = "subgraph_pack_ready"
        input_mode = "subgraph_pack"
        graph_family = _infer_graph_family(source_path, mode=input_mode)
        required_roles = ["subgraphs", "labels"]
        missing_required_roles: list[str] = []
        loader_can_construct_graph = has_edges
        raw_ready = False
        subgraph_ready = True
    elif has_edges and not raw_missing:
        status = "raw_graph_ready" if source_kind == "directory" else "flattened_graph_ready"
        input_mode = "raw_graph_bundle" if source_kind == "directory" else "flattened_graph_snapshot"
        graph_family = _infer_graph_family(source_path, mode=input_mode)
        required_roles = ["edges", "features", "labels", "time"]
        missing_required_roles = []
        loader_can_construct_graph = True
        raw_ready = source_kind == "directory"
        subgraph_ready = False
        flattened_ready = source_kind == "file"
    elif has_edges and source_kind == "file":
        status = "flattened_graph_ready"
        input_mode = "flattened_graph_snapshot"
        graph_family = _infer_graph_family(source_path, mode=input_mode)
        required_roles = ["edges"]
        missing_required_roles = []
        loader_can_construct_graph = True
        raw_ready = False
        subgraph_ready = False
        flattened_ready = True
    elif has_edges:
        status = "incomplete_graph_bundle"
        input_mode = "incomplete_raw_graph_bundle"
        graph_family = _infer_graph_family(source_path, mode=input_mode)
        required_roles = ["edges", "features", "labels", "time"]
        missing_required_roles = raw_missing
        loader_can_construct_graph = False
        raw_ready = False
        subgraph_ready = False
        blocked.extend(f"{role}_missing" for role in raw_missing)
    elif files:
        status = "unrecognized_graph_source"
        input_mode = "unrecognized"
        graph_family = _infer_graph_family(source_path, mode=input_mode)
        required_roles = ["edges"]
        missing_required_roles = ["edges"]
        loader_can_construct_graph = False
        raw_ready = False
        subgraph_ready = False
        blocked.append("edge_source_destination_columns_missing")
    else:
        status = "not_available"
        input_mode = "not_available"
        graph_family = "unknown"
        required_roles = ["edges"]
        missing_required_roles = ["edges"]
        loader_can_construct_graph = False
        raw_ready = False
        subgraph_ready = False
        blocked.append("graph_source_files_missing")
    return {
        "status": status,
        "source_path": source_path,
        "source_path_display": _display_path(source_path, root),
        "source_kind": source_kind,
        "files": files,
        "roles": roles,
        "graph_input_mode": input_mode,
        "graph_family": graph_family,
        "required_roles": required_roles,
        "missing_required_roles": missing_required_roles,
        "blocked_reason_codes": sorted(_unique(blocked)),
        "loader_can_construct_graph": loader_can_construct_graph,
        "benchmark_label_provenance_ready": bool(label_columns and time_columns),
        "raw_graph_bundle_ready": raw_ready,
        "flattened_graph_ready": flattened_ready,
        "subgraph_pack_ready": subgraph_ready,
        "node_id_columns": sorted(_unique(node_id_columns)),
        "edge_source_columns": sorted(_unique(edge_source_columns)),
        "edge_destination_columns": sorted(_unique(edge_destination_columns)),
        "time_columns": sorted(_unique(time_columns)),
        "label_columns": sorted(_unique(label_columns)),
        "subgraph_id_columns": sorted(_unique(subgraph_id_columns)),
    }


def _inspect_graph_file(*, file_path: Path, root: Path) -> dict[str, Any]:
    suffix = file_path.suffix.lower()
    if suffix in _SUPPORTED_TABULAR_SUFFIXES:
        inspection = _inspect_delimited_file(file_path)
    else:
        inspection = _inspect_jsonish_file(file_path)
    role = _infer_file_role(file_path=file_path, inspection=inspection)
    edge_pair = _resolve_edge_columns(inspection.get("columns", []), role=role)
    id_columns = _resolve_id_columns(inspection.get("columns", []), role=role)
    time_columns = _resolve_named_columns(inspection.get("columns", []), {"time", "timestamp", "time_step", "timestep", "step", "date", "period"})
    label_columns = _resolve_named_columns(inspection.get("columns", []), {"class", "label", "labels", "target", "y", "isfraud", "is_fraud", "fraud"})
    subgraph_id_columns = _resolve_named_columns(inspection.get("columns", []), {"subgraph_id", "graph_id", "community_id", "case_id", "component_id"})
    if role == "labels" and not label_columns and len(inspection.get("columns", [])) >= 2:
        label_columns = [inspection["columns"][1]]
    if role == "features" and not time_columns and len(inspection.get("columns", [])) >= 2:
        time_columns = [inspection["columns"][1]]
    if role == "subgraphs" and not subgraph_id_columns and inspection.get("columns"):
        subgraph_id_columns = [inspection["columns"][0]]
    return {
        "filename": file_path.name,
        "path_display": _display_path(file_path, root),
        "path_obj": file_path,
        "role": role,
        "format": suffix.lstrip(".") or "unknown",
        "size_bytes": file_path.stat().st_size if file_path.exists() else None,
        "sha256": _sha256_file(file_path),
        "row_count": inspection.get("row_count"),
        "delimiter": inspection.get("delimiter"),
        "has_header": inspection.get("has_header"),
        "columns": inspection.get("columns", []),
        "sample_row_count": inspection.get("sample_row_count", 0),
        "schema_hash": _schema_hash(inspection.get("columns", [])),
        "id_columns": id_columns,
        "edge_source_columns": [edge_pair[0]] if edge_pair[0] else [],
        "edge_destination_columns": [edge_pair[1]] if edge_pair[1] else [],
        "time_columns": time_columns,
        "label_columns": label_columns,
        "subgraph_id_columns": subgraph_id_columns,
    }


def _inspect_delimited_file(file_path: Path) -> dict[str, Any]:
    delimiter = "\t" if file_path.suffix.lower() == ".tsv" else _guess_delimiter(file_path)
    sample_rows: list[list[str]] = []
    row_count = 0
    try:
        with file_path.open("r", newline="", encoding="utf-8-sig") as handle:
            reader = csv.reader(handle, delimiter=delimiter)
            for row in reader:
                if not row:
                    continue
                row_count += 1
                if len(sample_rows) < 6:
                    sample_rows.append([str(item).strip() for item in row])
    except UnicodeDecodeError:
        with file_path.open("r", newline="", encoding="latin-1") as handle:
            reader = csv.reader(handle, delimiter=delimiter)
            for row in reader:
                if not row:
                    continue
                row_count += 1
                if len(sample_rows) < 6:
                    sample_rows.append([str(item).strip() for item in row])
    if not sample_rows:
        return {"columns": [], "row_count": 0, "sample_row_count": 0, "has_header": False, "delimiter": delimiter}
    has_header = _looks_like_header(sample_rows[0])
    columns = list(sample_rows[0]) if has_header else _default_columns_for_file(file_path, len(sample_rows[0]))
    data_rows = max(0, row_count - 1) if has_header else row_count
    return {
        "columns": columns,
        "row_count": data_rows,
        "sample_row_count": max(0, len(sample_rows) - 1) if has_header else len(sample_rows),
        "has_header": has_header,
        "delimiter": delimiter,
    }


def _inspect_jsonish_file(file_path: Path) -> dict[str, Any]:
    columns: list[str] = []
    row_count = 0
    try:
        with file_path.open("r", encoding="utf-8") as handle:
            for line in handle:
                text = line.strip()
                if not text:
                    continue
                row_count += 1
                if columns:
                    continue
                try:
                    value = json.loads(text)
                except json.JSONDecodeError:
                    continue
                if isinstance(value, dict):
                    columns = sorted(str(key) for key in value)
    except OSError:
        pass
    return {
        "columns": columns,
        "row_count": row_count,
        "sample_row_count": min(row_count, 1),
        "has_header": True,
        "delimiter": None,
    }


def _write_normalized_edge_table(*, root: Path, source: dict[str, Any]) -> Path | None:
    edge_files = list(dict(source.get("roles", {})).get("edges", []))
    if not edge_files:
        return None
    edge_file = edge_files[0]
    edge_path = edge_file.get("path_obj")
    if not isinstance(edge_path, Path) or edge_path.suffix.lower() not in _SUPPORTED_TABULAR_SUFFIXES:
        return None
    label_map = _load_node_value_map(source=source, role="labels", value_columns_key="label_columns")
    time_map = _load_node_value_map(source=source, role="features", value_columns_key="time_columns")
    source_col = _first(edge_file.get("edge_source_columns"))
    dest_col = _first(edge_file.get("edge_destination_columns"))
    if not source_col or not dest_col:
        return None
    output_path = root / _NORMALIZED_EDGE_TABLE_FILENAME
    delimiter = str(edge_file.get("delimiter") or _guess_delimiter(edge_path))
    has_header = bool(edge_file.get("has_header"))
    columns = list(edge_file.get("columns", []))
    with edge_path.open("r", newline="", encoding="utf-8-sig") as in_handle, output_path.open("w", newline="", encoding="utf-8") as out_handle:
        writer = csv.DictWriter(out_handle, fieldnames=["src", "dst", "label", "time_step", "amount"])
        writer.writeheader()
        if has_header:
            reader = csv.DictReader(in_handle, delimiter=delimiter)
            for row in reader:
                src = str(row.get(source_col, "")).strip()
                dst = str(row.get(dest_col, "")).strip()
                if not src or not dst:
                    continue
                writer.writerow(
                    {
                        "src": src,
                        "dst": dst,
                        "label": _normalize_label(label_map.get(src, 0)),
                        "time_step": time_map.get(src, ""),
                        "amount": 1.0,
                    }
                )
        else:
            reader = csv.reader(in_handle, delimiter=delimiter)
            source_index = columns.index(source_col) if source_col in columns else 0
            dest_index = columns.index(dest_col) if dest_col in columns else 1
            for row in reader:
                if len(row) <= max(source_index, dest_index):
                    continue
                src = str(row[source_index]).strip()
                dst = str(row[dest_index]).strip()
                if not src or not dst:
                    continue
                writer.writerow(
                    {
                        "src": src,
                        "dst": dst,
                        "label": _normalize_label(label_map.get(src, 0)),
                        "time_step": time_map.get(src, ""),
                        "amount": 1.0,
                    }
                )
    return output_path


def _sync_existing_entity_graph(
    *,
    root: Path,
    normalized_edge_table: Path,
    context_bundle: dict[str, Any] | None,
    task_contract_bundle: dict[str, Any] | None,
    force_aml_active: bool,
) -> None:
    try:
        from relaytic.aml.agents import sync_aml_graph_artifacts

        sync_aml_graph_artifacts(
            root,
            data_path=normalized_edge_table,
            context_bundle=context_bundle or {},
            task_contract_bundle=_entity_graph_task_contract(task_contract_bundle, force_aml_active=force_aml_active),
        )
    except Exception:
        return


def _entity_graph_task_contract(bundle: dict[str, Any] | None, *, force_aml_active: bool) -> dict[str, Any]:
    payload = dict(bundle or {})
    domain = dict(payload.get("aml_domain_contract", {})) if isinstance(payload.get("aml_domain_contract"), dict) else {}
    task = dict(payload.get("task_profile_contract", {})) if isinstance(payload.get("task_profile_contract"), dict) else {}
    if force_aml_active or domain.get("aml_active") is True:
        domain.setdefault("status", "active")
        domain["aml_active"] = True
        domain.setdefault("domain_focus", "graph_aml")
        domain.setdefault("target_level", "entity_or_transaction_graph")
        task.setdefault("target_column", "label")
        task.setdefault("timestamp_column", "time_step")
    payload["aml_domain_contract"] = domain
    payload["task_profile_contract"] = task
    return payload


def _load_node_value_map(*, source: dict[str, Any], role: str, value_columns_key: str) -> dict[str, Any]:
    files = list(dict(source.get("roles", {})).get(role, []))
    if not files:
        return {}
    file_info = files[0]
    path = file_info.get("path_obj")
    if not isinstance(path, Path) or path.suffix.lower() not in _SUPPORTED_TABULAR_SUFFIXES:
        return {}
    id_col = _first(file_info.get("id_columns")) or _first(file_info.get("columns"))
    value_col = _first(file_info.get(value_columns_key))
    if not id_col or not value_col:
        return {}
    delimiter = str(file_info.get("delimiter") or _guess_delimiter(path))
    has_header = bool(file_info.get("has_header"))
    columns = list(file_info.get("columns", []))
    mapping: dict[str, Any] = {}
    with path.open("r", newline="", encoding="utf-8-sig") as handle:
        if has_header:
            reader = csv.DictReader(handle, delimiter=delimiter)
            for row in reader:
                node_id = str(row.get(id_col, "")).strip()
                if node_id:
                    mapping[node_id] = row.get(value_col, "")
        else:
            reader = csv.reader(handle, delimiter=delimiter)
            id_index = columns.index(id_col) if id_col in columns else 0
            value_index = columns.index(value_col) if value_col in columns else 1
            for row in reader:
                if len(row) <= max(id_index, value_index):
                    continue
                node_id = str(row[id_index]).strip()
                if node_id:
                    mapping[node_id] = row[value_index]
    return mapping


def _resolve_source_path(*, root: Path, graph_path: str | Path | None, data_path: str | Path | None) -> Path | None:
    for candidate in (graph_path, data_path):
        if candidate:
            return Path(candidate)
    staged = _resolve_staged_data_path(root)
    if staged:
        return Path(staged)
    summary = _read_json(root / "run_summary.json")
    data = summary.get("data") if isinstance(summary.get("data"), dict) else {}
    for key in ("working_copy_path", "data_path"):
        value = _clean_text(data.get(key))
        if value:
            return Path(value)
    return None


def _resolve_staged_data_path(root: Path) -> str | None:
    try:
        from relaytic.ingestion import resolve_staged_data_path

        return resolve_staged_data_path(root, purpose="primary")
    except Exception:
        return None


def _infer_file_role(*, file_path: Path, inspection: dict[str, Any]) -> str:
    name = file_path.name.lower()
    columns = [str(item).lower() for item in inspection.get("columns", [])]
    if any(token in name for token in ("subgraph", "community", "graph_labels")) or any(
        column in {"subgraph_id", "graph_id", "community_id"} for column in columns
    ):
        return "subgraphs"
    if any(token in name for token in ("edge", "edgelist", "link", "links", "adjacency")):
        return "edges"
    if _resolve_edge_columns(inspection.get("columns", []), role=None) != (None, None):
        return "edges"
    if any(token in name for token in ("class", "classes", "label", "labels", "target")):
        return "labels"
    if any(token in name for token in ("feature", "features", "embedding", "node")):
        return "features"
    if len(columns) >= 6:
        return "features"
    return "unknown"


def _infer_graph_family(source_path: Path, *, mode: str) -> str:
    corpus = f"{source_path.name} {mode}".lower()
    if "elliptic2" in corpus or "subgraph" in corpus:
        return "elliptic2_style_subgraph"
    if "elliptic" in corpus:
        return "elliptic_style_raw_graph" if "raw" in mode or "bundle" in mode else "elliptic_style_flattened_graph"
    if "amlsim" in corpus or "bank" in corpus:
        return "amlsim_style_bank_graph"
    if "paysim" in corpus:
        return "paysim_style_transaction_graph_proxy"
    if mode == "raw_graph_bundle":
        return "generic_raw_graph_bundle"
    if mode == "flattened_graph_snapshot":
        return "generic_flattened_graph_snapshot"
    return "unknown"


def _resolve_edge_columns(columns: list[str], *, role: str | None) -> tuple[str | None, str | None]:
    if role == "edges" and columns and all(column.startswith("column_") for column in columns):
        return columns[0], columns[1] if len(columns) > 1 else None
    normalized = {_normalize_column(column): column for column in columns}
    pairs = [
        ("txid1", "txid2"),
        ("tx_id_1", "tx_id_2"),
        ("source", "target"),
        ("source", "destination"),
        ("source_id", "target_id"),
        ("source_id", "destination_id"),
        ("src", "dst"),
        ("from", "to"),
        ("sender", "receiver"),
        ("nameorig", "namedest"),
        ("account_id", "counterparty_id"),
    ]
    for left, right in pairs:
        if left in normalized and right in normalized:
            return normalized[left], normalized[right]
    source = _first_matching_column(columns, ["source", "src", "from", "sender", "origin", "orig", "payer", "txid1"])
    dest = _first_matching_column(columns, ["target", "destination", "dest", "dst", "to", "receiver", "counterparty", "merchant", "txid2"])
    return source, dest


def _resolve_id_columns(columns: list[str], *, role: str) -> list[str]:
    if role in {"features", "labels", "subgraphs"} and columns:
        first = columns[0]
        if _normalize_column(first).startswith("column_") or _normalize_column(first) in {
            "id",
            "node_id",
            "txid",
            "tx_id",
            "account_id",
            "subgraph_id",
            "graph_id",
        }:
            return [first]
    exact = {"id", "node_id", "txid", "tx_id", "transaction_id", "account_id", "entity_id"}
    return [column for column in columns if _normalize_column(column) in exact]


def _resolve_named_columns(columns: list[str], names: set[str]) -> list[str]:
    normalized_names = {_normalize_column(name) for name in names}
    found = [column for column in columns if _normalize_column(column) in normalized_names]
    if found:
        return found
    return [
        column
        for column in columns
        if any(token in _normalize_column(column) for token in normalized_names if len(token) >= 4)
    ]


def _default_columns_for_file(file_path: Path, width: int) -> list[str]:
    name = file_path.name.lower()
    if "edge" in name and width >= 2:
        return ["txId1", "txId2", *[f"column_{idx}" for idx in range(3, width + 1)]]
    if ("class" in name or "label" in name) and width >= 2:
        return ["txId", "class", *[f"column_{idx}" for idx in range(3, width + 1)]]
    if "feature" in name and width >= 2:
        return ["txId", "time_step", *[f"feature_{idx}" for idx in range(1, max(1, width - 1))]]
    return [f"column_{idx}" for idx in range(1, width + 1)]


def _looks_like_header(row: list[str]) -> bool:
    if not row:
        return False
    joined = " ".join(row).lower()
    known_tokens = (
        "source",
        "target",
        "src",
        "dst",
        "txid",
        "class",
        "label",
        "feature",
        "time",
        "subgraph",
        "nameorig",
        "namedest",
    )
    if any(token in joined for token in known_tokens):
        return True
    numeric_like = 0
    for value in row:
        try:
            float(str(value).strip())
            numeric_like += 1
        except ValueError:
            continue
    return numeric_like < max(1, len(row) // 2)


def _guess_delimiter(path: Path) -> str:
    try:
        first_line = path.read_text(encoding="utf-8-sig", errors="ignore").splitlines()[0]
    except (OSError, IndexError):
        return ","
    candidates = [(",", first_line.count(",")), ("\t", first_line.count("\t")), (";", first_line.count(";"))]
    return max(candidates, key=lambda item: item[1])[0] or ","


def _public_file_roles(source: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    roles: dict[str, list[dict[str, Any]]] = {}
    for role, items in dict(source.get("roles", {})).items():
        if not isinstance(items, list) or not items:
            continue
        roles[str(role)] = [_public_file_info(item) for item in items if isinstance(item, dict)]
    return roles


def _public_file_info(item: dict[str, Any]) -> dict[str, Any]:
    return {
        key: value
        for key, value in item.items()
        if key != "path_obj" and not isinstance(value, Path)
    }


def _role_columns(files: list[dict[str, Any]], key: str) -> list[str]:
    return sorted(_unique(column for item in files for column in item.get(key, [])))


def _loader_summary(*, source: dict[str, Any], missing: list[str]) -> str:
    status = source.get("status")
    if status == "raw_graph_ready":
        return "Relaytic-AML loaded a raw graph bundle with edge, feature, label, and time provenance."
    if status == "flattened_graph_ready":
        return "Relaytic-AML recognized a flattened graph snapshot and labeled it as proxy-compatible graph evidence."
    if status == "subgraph_pack_ready":
        return "Relaytic-AML recognized a labeled subgraph pack for subgraph-centric AML task framing."
    if status == "incomplete_graph_bundle":
        return f"Relaytic-AML found an incomplete graph bundle; missing roles: {', '.join(missing)}."
    return "Relaytic-AML did not find a usable graph loader source."


def _recovery_instructions(missing: list[str], blocked: list[str]) -> list[str]:
    instructions: list[str] = []
    if "edges" in missing or "edge_source_destination_columns_missing" in blocked:
        instructions.append("Provide an edge list with source and destination transaction/entity IDs, for example `txId1,txId2` or `src,dst`.")
    if "features" in missing:
        instructions.append("Provide a node/transaction feature file keyed by the same ID used in the edge list.")
    if "labels" in missing or "subgraph_labels_missing" in blocked:
        instructions.append("Provide a class or label file keyed by node, transaction, graph, or subgraph ID.")
    if "time" in missing:
        instructions.append("Provide a `time_step`, timestamp, or documented temporal index so graph benchmark splits remain auditable.")
    if "raw_subgraph_pack_missing" in blocked or "subgraph_pack_or_graph_proxy_missing" in blocked:
        instructions.append("Provide explicit subgraph IDs and labels for Elliptic2-style subgraph benchmark framing.")
    if not instructions and blocked:
        instructions.append("Resolve the graph-loader blocked reason codes before making public graph benchmark claims.")
    return instructions


def _scorecard_family_supported(scorecard: dict[str, Any], family: str) -> bool:
    rows = scorecard.get("rows", [])
    if not isinstance(rows, list):
        return False
    for row in rows:
        if not isinstance(row, dict):
            continue
        if row.get("benchmark_family") == family and row.get("support_level") == "supported":
            return True
    return False


def _artifact_active(payload: dict[str, Any]) -> bool:
    if not payload:
        return False
    status = _clean_text(payload.get("status"))
    if status in _INACTIVE_STATUSES:
        return False
    if status in _ACTIVE_STATUSES:
        return True
    return bool(status or payload)


def _existing_refs(root: Path, filenames: list[str]) -> list[str]:
    return [filename for filename in filenames if (root / filename).exists()]


def _empty_source(status: str, summary: str) -> dict[str, Any]:
    return {
        "status": status,
        "summary": summary,
        "source_path": None,
        "source_path_display": None,
        "source_kind": "not_available",
        "files": [],
        "roles": {},
        "graph_input_mode": "not_available",
        "graph_family": "unknown",
        "required_roles": ["edges"],
        "missing_required_roles": ["edges"],
        "blocked_reason_codes": ["graph_source_missing"],
        "loader_can_construct_graph": False,
        "benchmark_label_provenance_ready": False,
        "raw_graph_bundle_ready": False,
        "flattened_graph_ready": False,
        "subgraph_pack_ready": False,
        "node_id_columns": [],
        "edge_source_columns": [],
        "edge_destination_columns": [],
        "time_columns": [],
        "label_columns": [],
        "subgraph_id_columns": [],
    }


def _display_path(path: Path | None, root: Path) -> str | None:
    if path is None:
        return None
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.name


def _sha256_file(path: Path) -> str | None:
    if not path.exists() or not path.is_file():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _schema_hash(columns: list[str]) -> str:
    payload = json.dumps([str(item) for item in columns], sort_keys=True).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()[:16]


def _normalize_column(value: Any) -> str:
    return str(value or "").strip().lower().replace(" ", "_").replace("-", "_")


def _normalize_label(value: Any) -> Any:
    text = str(value).strip().lower()
    if text in {"1", "illicit", "fraud", "true", "yes", "suspicious"}:
        return 1
    if text in {"2", "licit", "0", "false", "no", "benign", "unknown"}:
        return 0
    try:
        return int(float(text))
    except ValueError:
        return 0


def _first_matching_column(columns: list[str], tokens: list[str]) -> str | None:
    for column in columns:
        normalized = _normalize_column(column)
        if any(token in normalized for token in tokens):
            return column
    return None


def _first(values: Any) -> Any:
    if isinstance(values, list) and values:
        return values[0]
    return None


def _unique(values: Any) -> list[Any]:
    seen: set[str] = set()
    output: list[Any] = []
    for value in values or []:
        text = str(value).strip()
        if not text or text in seen:
            continue
        seen.add(text)
        output.append(value)
    return output


def _clean_text(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return payload if isinstance(payload, dict) else {}


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()
