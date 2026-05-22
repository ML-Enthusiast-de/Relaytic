"""Elliptic graph provenance and temporal split pack for Paper Track P5."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from hashlib import sha256
import json
import math
from pathlib import Path
from typing import Any

from relaytic.core.json_utils import write_json


ELLIPTIC_GRAPH_SCHEMA_VERSION = "relaytic.elliptic_graph_provenance.v1"
ELLIPTIC_GRAPH_REPORT_DIR = Path("docs") / "reports"
ELLIPTIC_DEFAULT_DATA_DIR = Path("data") / "paper_benchmarks" / "elliptic"
ELLIPTIC_GRAPH_FILENAMES = {
    "elliptic_graph_loader_manifest": "elliptic_graph_loader_manifest.json",
    "elliptic_graph_provenance_report": "elliptic_graph_provenance_report.json",
    "elliptic_temporal_split_report": "elliptic_temporal_split_report.json",
    "elliptic_graph_claim_scope": "elliptic_graph_claim_scope.json",
    "elliptic_paper_result_row": "elliptic_paper_result_row.json",
}

ELLIPTIC_REQUIRED_FILES = {
    "classes": "elliptic_txs_classes.csv",
    "edges": "elliptic_txs_edgelist.csv",
    "features": "elliptic_txs_features.csv",
}
ELLIPTIC_DATASET_ID = "elliptic_bitcoin_flattened_graph_aml"
ELLIPTIC_TRACK_ID = "elliptic_flattened_graph_aml"
ELLIPTIC_CLAIM_ID = "claim_elliptic_flattened_graph_aml"
ELLIPTIC_SPLIT_CONTRACT_ID = "split_elliptic_temporal_step_v1"
ELLIPTIC_RECOVERY_INSTRUCTIONS = [
    "Place the raw Elliptic files in data/paper_benchmarks/elliptic/ with their original file names.",
    "Required files: elliptic_txs_classes.csv, elliptic_txs_edgelist.csv, and elliptic_txs_features.csv.",
    "Regenerate the artifacts with: relaytic release-safety elliptic-graph --format json.",
    "Do not commit the raw CSV files; only commit the generated docs/reports/*.json artifacts.",
]


@dataclass(frozen=True)
class _NodeIndex:
    time_by_txid: dict[str, int]
    label_by_txid: dict[str, str]
    feature_row_count: int
    feature_width: int
    feature_value_count: int
    class_row_count: int


@dataclass(frozen=True)
class _SplitBounds:
    train_max_time_step: int
    validation_max_time_step: int


def build_elliptic_graph_pack(
    project_root: str | Path,
    *,
    data_dir: str | Path | None = None,
) -> dict[str, Any]:
    """Build Paper Track P5 Elliptic graph artifacts without writing them."""
    root = Path(project_root)
    resolved_data_dir = Path(data_dir) if data_dir is not None else root / ELLIPTIC_DEFAULT_DATA_DIR
    if not resolved_data_dir.is_absolute():
        resolved_data_dir = root / resolved_data_dir

    registry = _read_json(root / "docs" / "reports" / "paper_dataset_registry.json")
    split_contracts = _read_json(root / "docs" / "reports" / "paper_split_contracts.json")
    claim_taxonomy = _read_json(root / "docs" / "reports" / "paper_claim_taxonomy.json")
    required_paths = {role: resolved_data_dir / filename for role, filename in ELLIPTIC_REQUIRED_FILES.items()}
    missing_roles = [role for role, path in required_paths.items() if not path.exists()]
    if missing_roles:
        return _blocked_pack(
            root=root,
            data_dir=resolved_data_dir,
            registry=registry,
            split_contracts=split_contracts,
            claim_taxonomy=claim_taxonomy,
            reason_code="elliptic_required_source_files_missing",
            reason=f"Elliptic source is missing required file roles: {missing_roles}.",
            missing_roles=missing_roles,
        )

    try:
        node_index = _load_node_index(
            features_path=required_paths["features"],
            classes_path=required_paths["classes"],
        )
        split_bounds = _split_bounds(sorted(set(node_index.time_by_txid.values())))
        node_split = _build_node_split_report(node_index=node_index, split_bounds=split_bounds)
        edge_report = _build_edge_report(
            edge_path=required_paths["edges"],
            node_index=node_index,
            split_bounds=split_bounds,
        )
    except Exception as exc:  # pragma: no cover - defensive artifact surface
        return _blocked_pack(
            root=root,
            data_dir=resolved_data_dir,
            registry=registry,
            split_contracts=split_contracts,
            claim_taxonomy=claim_taxonomy,
            reason_code="elliptic_source_load_failed",
            reason=f"Elliptic source could not be loaded: {exc}",
            missing_roles=[],
        )

    split_report = _build_temporal_split_report(
        root=root,
        data_dir=resolved_data_dir,
        node_index=node_index,
        node_split=node_split,
        edge_report=edge_report,
        split_bounds=split_bounds,
        split_contracts=split_contracts,
    )
    if split_report["status"] != "ok":
        return _blocked_pack(
            root=root,
            data_dir=resolved_data_dir,
            registry=registry,
            split_contracts=split_contracts,
            claim_taxonomy=claim_taxonomy,
            reason_code="elliptic_temporal_split_blocked",
            reason=str(split_report["summary"]),
            missing_roles=[],
            split_report=split_report,
        )

    provenance = _build_graph_provenance_report(
        root=root,
        data_dir=resolved_data_dir,
        required_paths=required_paths,
        registry=registry,
        node_index=node_index,
        edge_report=edge_report,
    )
    claim_scope = _build_graph_claim_scope(
        claim_taxonomy=claim_taxonomy,
        provenance=provenance,
        split_report=split_report,
    )
    result_row = _build_paper_result_row(
        root=root,
        data_dir=resolved_data_dir,
        provenance=provenance,
        split_report=split_report,
        claim_scope=claim_scope,
    )
    manifest = _build_graph_loader_manifest(
        root=root,
        data_dir=resolved_data_dir,
        registry=registry,
        provenance=provenance,
        split_report=split_report,
        claim_scope=claim_scope,
    )
    return {
        "elliptic_graph_loader_manifest": manifest,
        "elliptic_graph_provenance_report": provenance,
        "elliptic_temporal_split_report": split_report,
        "elliptic_graph_claim_scope": claim_scope,
        "elliptic_paper_result_row": result_row,
    }


def sync_elliptic_graph_pack(
    project_root: str | Path,
    *,
    data_dir: str | Path | None = None,
    output_dir: str | Path | None = None,
) -> dict[str, Path]:
    """Write Paper Track P5 Elliptic graph artifacts to docs/reports by default."""
    root = Path(project_root)
    report_dir = Path(output_dir) if output_dir is not None else root / ELLIPTIC_GRAPH_REPORT_DIR
    report_dir.mkdir(parents=True, exist_ok=True)
    artifacts = build_elliptic_graph_pack(root, data_dir=data_dir)
    return {
        key: write_json(report_dir / filename, artifacts[key], indent=2, sort_keys=True)
        for key, filename in ELLIPTIC_GRAPH_FILENAMES.items()
    }


def render_elliptic_graph_markdown(pack: dict[str, Any]) -> str:
    manifest = dict(pack.get("elliptic_graph_loader_manifest", {}))
    split = dict(pack.get("elliptic_temporal_split_report", {}))
    claim_scope = dict(pack.get("elliptic_graph_claim_scope", {}))
    result = dict(pack.get("elliptic_paper_result_row", {}))
    lines = [
        "# Elliptic Graph Provenance",
        "",
        f"- Status: `{manifest.get('status') or 'unknown'}`",
        f"- Claim posture: `{result.get('claim_posture') or 'unknown'}`",
        f"- Raw graph loader claim allowed: `{claim_scope.get('raw_graph_loader_claim_allowed')}`",
        f"- Graph benchmark performance claim allowed: `{claim_scope.get('graph_benchmark_performance_claim_allowed')}`",
        f"- Graph SOTA claim allowed: `{claim_scope.get('graph_sota_claim_allowed')}`",
        f"- Nodes: `{manifest.get('node_count') or 0}`",
        f"- Edges: `{manifest.get('edge_count') or 0}`",
        f"- Time steps: `{split.get('unique_time_step_count') or 0}`",
        f"- Labeled nodes: `{split.get('known_label_count') or 0}`",
        f"- Unknown-label nodes: `{split.get('unknown_label_count') or 0}`",
        f"- Next slice: `{manifest.get('next_slice') or 'unknown'}`",
    ]
    blockers = [str(item) for item in manifest.get("blocked_reason_codes", []) if str(item).strip()]
    if blockers:
        lines.extend(["", "## Blockers", *(f"- `{item}`" for item in blockers)])
    return "\n".join(lines).rstrip() + "\n"


def _load_node_index(*, features_path: Path, classes_path: Path) -> _NodeIndex:
    time_by_txid: dict[str, int] = {}
    feature_width = 0
    feature_rows = 0
    with features_path.open("r", newline="", encoding="utf-8-sig") as handle:
        reader = csv.reader(handle)
        for row in reader:
            if len(row) < 2:
                continue
            if feature_rows == 0 and _looks_like_header(row):
                continue
            txid = str(row[0]).strip()
            if not txid:
                continue
            try:
                time_step = int(float(str(row[1]).strip()))
            except ValueError:
                continue
            feature_rows += 1
            feature_width = max(feature_width, len(row))
            time_by_txid[txid] = time_step

    label_by_txid: dict[str, str] = {}
    class_rows = 0
    with classes_path.open("r", newline="", encoding="utf-8-sig") as handle:
        sample = handle.readline()
        handle.seek(0)
        has_header = "tx" in sample.lower() and "class" in sample.lower()
        if has_header:
            reader = csv.DictReader(handle)
            for row in reader:
                txid = str(row.get("txId") or row.get("txid") or row.get("id") or "").strip()
                label = str(row.get("class") or row.get("label") or "").strip().lower()
                if txid:
                    label_by_txid[txid] = label or "unknown"
                    class_rows += 1
        else:
            reader = csv.reader(handle)
            for row in reader:
                if len(row) < 2:
                    continue
                txid = str(row[0]).strip()
                if txid:
                    label_by_txid[txid] = str(row[1]).strip().lower() or "unknown"
                    class_rows += 1

    return _NodeIndex(
        time_by_txid=time_by_txid,
        label_by_txid=label_by_txid,
        feature_row_count=feature_rows,
        feature_width=feature_width,
        feature_value_count=max(0, feature_width - 2),
        class_row_count=class_rows,
    )


def _split_bounds(unique_time_steps: list[int]) -> _SplitBounds:
    if len(unique_time_steps) < 3:
        raise ValueError("Elliptic temporal split requires at least three distinct time steps.")
    train_index = max(0, int(math.floor(0.60 * len(unique_time_steps))) - 1)
    validation_index = max(train_index + 1, int(math.floor(0.80 * len(unique_time_steps))) - 1)
    validation_index = min(validation_index, len(unique_time_steps) - 2)
    return _SplitBounds(
        train_max_time_step=int(unique_time_steps[train_index]),
        validation_max_time_step=int(unique_time_steps[validation_index]),
    )


def _build_node_split_report(*, node_index: _NodeIndex, split_bounds: _SplitBounds) -> dict[str, Any]:
    rows = {
        "train": _empty_node_split_row("train"),
        "validation": _empty_node_split_row("validation"),
        "test": _empty_node_split_row("test"),
    }
    for txid, time_step in node_index.time_by_txid.items():
        split = _time_window(time_step, split_bounds=split_bounds)
        row = rows[split]
        row["node_count"] += 1
        row["time_step_min"] = time_step if row["time_step_min"] is None else min(row["time_step_min"], time_step)
        row["time_step_max"] = time_step if row["time_step_max"] is None else max(row["time_step_max"], time_step)
        label = _normalize_elliptic_label(node_index.label_by_txid.get(txid, "unknown"))
        if label == "illicit":
            row["illicit_count"] += 1
            row["known_label_count"] += 1
        elif label == "licit":
            row["licit_count"] += 1
            row["known_label_count"] += 1
        else:
            row["unknown_label_count"] += 1
    for row in rows.values():
        known = int(row["known_label_count"])
        row["positive_rate_labeled"] = _round_float(_safe_divide(float(row["illicit_count"]), float(known)))
        row["unknown_label_rate"] = _round_float(_safe_divide(float(row["unknown_label_count"]), float(row["node_count"])))
        row["class_coverage_ok"] = int(row["illicit_count"]) > 0 and int(row["licit_count"]) > 0
    return {
        "split_rows": [rows["train"], rows["validation"], rows["test"]],
        "class_coverage_ok": all(bool(row["class_coverage_ok"]) for row in rows.values()),
    }


def _build_edge_report(*, edge_path: Path, node_index: _NodeIndex, split_bounds: _SplitBounds) -> dict[str, Any]:
    counts = {
        "within_train": 0,
        "within_validation": 0,
        "within_test": 0,
        "cross_train_validation": 0,
        "cross_train_test": 0,
        "cross_validation_test": 0,
        "missing_time_endpoint": 0,
    }
    edge_count = 0
    with edge_path.open("r", newline="", encoding="utf-8-sig") as handle:
        reader = csv.reader(handle)
        for row in reader:
            if len(row) < 2:
                continue
            if edge_count == 0 and _looks_like_header(row):
                continue
            src = str(row[0]).strip()
            dst = str(row[1]).strip()
            if not src or not dst:
                continue
            edge_count += 1
            src_time = node_index.time_by_txid.get(src)
            dst_time = node_index.time_by_txid.get(dst)
            if src_time is None or dst_time is None:
                counts["missing_time_endpoint"] += 1
                continue
            src_window = _time_window(src_time, split_bounds=split_bounds)
            dst_window = _time_window(dst_time, split_bounds=split_bounds)
            if src_window == dst_window:
                counts[f"within_{src_window}"] += 1
                continue
            pair = sorted([src_window, dst_window], key={"train": 0, "validation": 1, "test": 2}.get)
            counts[f"cross_{pair[0]}_{pair[1]}"] += 1
    cross_window = counts["cross_train_validation"] + counts["cross_train_test"] + counts["cross_validation_test"]
    return {
        "edge_count": edge_count,
        "edge_rows": counts,
        "edge_time_coverage_ok": counts["missing_time_endpoint"] == 0,
        "cross_window_edge_count": cross_window,
        "train_induced_edge_count": counts["within_train"],
        "validation_induced_edge_count": counts["within_validation"],
        "test_induced_edge_count": counts["within_test"],
        "future_to_train_cross_edge_count": counts["cross_train_validation"] + counts["cross_train_test"],
        "future_to_train_leakage_prevented": True,
        "edge_split_policy": (
            "Training graph construction may use only edges whose endpoints are both in the train window. "
            "Cross-window edges are counted for provenance and excluded from train graph evidence."
        ),
    }


def _build_temporal_split_report(
    *,
    root: Path,
    data_dir: Path,
    node_index: _NodeIndex,
    node_split: dict[str, Any],
    edge_report: dict[str, Any],
    split_bounds: _SplitBounds,
    split_contracts: dict[str, Any],
) -> dict[str, Any]:
    time_steps = sorted(set(node_index.time_by_txid.values()))
    rows = list(node_split["split_rows"])
    chronological_order_ok = (
        len(rows) == 3
        and rows[0]["time_step_max"] is not None
        and rows[1]["time_step_min"] is not None
        and rows[1]["time_step_max"] is not None
        and rows[2]["time_step_min"] is not None
        and int(rows[0]["time_step_max"]) < int(rows[1]["time_step_min"])
        and int(rows[1]["time_step_max"]) < int(rows[2]["time_step_min"])
    )
    edge_time_ok = bool(edge_report["edge_time_coverage_ok"])
    status = "ok" if chronological_order_ok and node_split["class_coverage_ok"] and edge_time_ok else "blocked"
    return {
        "schema_version": ELLIPTIC_GRAPH_SCHEMA_VERSION,
        "slice": "Paper Track P5",
        "status": status,
        "dataset_id": ELLIPTIC_DATASET_ID,
        "track_id": ELLIPTIC_TRACK_ID,
        "source_path": _display_path(root, data_dir),
        "split_contract_id": ELLIPTIC_SPLIT_CONTRACT_ID,
        "split_contract": _elliptic_split_contract(split_contracts),
        "split_type": "temporal_graph_by_time_step",
        "train_window": f"time_step <= {split_bounds.train_max_time_step}",
        "validation_window": (
            f"{split_bounds.train_max_time_step} < time_step <= {split_bounds.validation_max_time_step}"
        ),
        "test_window": f"time_step > {split_bounds.validation_max_time_step}",
        "time_step_min": min(time_steps) if time_steps else None,
        "time_step_max": max(time_steps) if time_steps else None,
        "unique_time_step_count": len(time_steps),
        "node_count": len(node_index.time_by_txid),
        "known_label_count": sum(int(row["known_label_count"]) for row in rows),
        "unknown_label_count": sum(int(row["unknown_label_count"]) for row in rows),
        "split_rows": rows,
        "edge_report": edge_report,
        "chronological_order_ok": chronological_order_ok,
        "class_coverage_ok": bool(node_split["class_coverage_ok"]),
        "edge_time_coverage_ok": edge_time_ok,
        "forbidden_split_methods_avoided": [
            "random_node_split_across_time",
            "edge_leaking_future_to_train",
        ],
        "raw_vs_flattened_claim_scope_recorded": True,
        "blocked_reason_codes": []
        if status == "ok"
        else _split_blockers(chronological_order_ok, node_split["class_coverage_ok"], edge_time_ok),
        "summary": (
            "Elliptic raw graph bundle was split by transaction time step with unknown labels excluded from supervised metric scope."
            if status == "ok"
            else "Elliptic temporal split failed chronological, class-coverage, or edge-time checks."
        ),
    }


def _build_graph_provenance_report(
    *,
    root: Path,
    data_dir: Path,
    required_paths: dict[str, Path],
    registry: dict[str, Any],
    node_index: _NodeIndex,
    edge_report: dict[str, Any],
) -> dict[str, Any]:
    file_checks = _registry_file_checks(registry)
    source_files = [
        _source_file_record(
            root=root,
            path=required_paths["classes"],
            role="labels",
            file_checks=file_checks,
            row_count=node_index.class_row_count,
        ),
        _source_file_record(
            root=root,
            path=required_paths["edges"],
            role="edges",
            file_checks=file_checks,
            row_count=edge_report["edge_count"],
        ),
        _source_file_record(
            root=root,
            path=required_paths["features"],
            role="features",
            file_checks=file_checks,
            row_count=node_index.feature_row_count,
        ),
    ]
    return {
        "schema_version": ELLIPTIC_GRAPH_SCHEMA_VERSION,
        "slice": "Paper Track P5",
        "status": "ok",
        "dataset_id": ELLIPTIC_DATASET_ID,
        "track_id": ELLIPTIC_TRACK_ID,
        "source_path": _display_path(root, data_dir),
        "source_file_count": len(source_files),
        "source_files": source_files,
        "graph_input_mode": "raw_graph_bundle",
        "graph_family": "elliptic_bitcoin_transaction_graph",
        "node_id_lineage": {
            "node_id_field": "txId",
            "edge_source_field": "txId1",
            "edge_destination_field": "txId2",
            "join_key": "transaction_id",
        },
        "time_lineage": {
            "time_field": "time_step",
            "source_file": ELLIPTIC_REQUIRED_FILES["features"],
            "time_steps_are_ordered": True,
        },
        "label_lineage": {
            "class_row_count": node_index.class_row_count,
            "label_field": "class",
            "source_file": ELLIPTIC_REQUIRED_FILES["classes"],
            "positive_class": "1_illicit",
            "negative_class": "2_licit",
            "unknown_label_policy": "exclude_unknown_from_supervised_metrics_but_count_in_split_scope",
        },
        "feature_lineage": {
            "feature_file": ELLIPTIC_REQUIRED_FILES["features"],
            "raw_feature_width": node_index.feature_width,
            "feature_value_count_excluding_id_and_time": node_index.feature_value_count,
            "anonymized_feature_policy": "features are source-provided anonymized transaction features; semantic feature names are unavailable",
        },
        "graph_lineage": {
            "edge_file": ELLIPTIC_REQUIRED_FILES["edges"],
            "node_count": len(node_index.time_by_txid),
            "edge_count": edge_report["edge_count"],
            "directed_edge_assumption": "source edgelist is preserved as directed transaction-to-transaction edges for provenance",
        },
        "transformations": [
            {
                "transformation_id": "raw_elliptic_role_detection",
                "operation": "detect classes, edgelist, features, txId, class, time_step, txId1, and txId2 roles",
                "changes_raw_values": False,
            },
            {
                "transformation_id": "temporal_split_projection",
                "operation": "derive train, validation, and test windows from source time_step without random node shuffling",
                "changes_raw_values": False,
            },
        ],
        "privacy_posture": "raw source files remain local and ignored; committed artifacts contain hashes, relative paths, and aggregate counts only",
        "summary": "Relaytic inspected the raw Elliptic classes, edgelist, and features files and preserved ID, edge, time, and label provenance.",
    }


def _build_graph_claim_scope(
    *,
    claim_taxonomy: dict[str, Any],
    provenance: dict[str, Any],
    split_report: dict[str, Any],
) -> dict[str, Any]:
    boundary = _claim_boundary(ELLIPTIC_CLAIM_ID, claim_taxonomy)
    loader_ready = provenance["status"] == "ok" and split_report["status"] == "ok"
    supporting_allowed = bool(loader_ready and boundary == "supporting-only")
    return {
        "schema_version": ELLIPTIC_GRAPH_SCHEMA_VERSION,
        "slice": "Paper Track P5",
        "status": "ok" if loader_ready else "blocked",
        "dataset_id": ELLIPTIC_DATASET_ID,
        "track_id": ELLIPTIC_TRACK_ID,
        "claim_boundary_from_taxonomy": boundary,
        "claim_posture": "supporting-only",
        "raw_graph_loader_claim_allowed": supporting_allowed,
        "flattened_graph_proxy_claim_allowed": supporting_allowed,
        "graph_benchmark_performance_claim_allowed": False,
        "graph_sota_claim_allowed": False,
        "paper_primary_claim_allowed": False,
        "hard_performance_claims_allowed": False,
        "allowed_public_wording": (
            "Relaytic can inspect the raw Elliptic graph bundle, preserve ID/time/label/edge provenance, "
            "and emit a chronological graph split proof. This is supporting graph evidence, not a graph SOTA or "
            "hard AML performance claim."
        )
        if supporting_allowed
        else None,
        "blocked_claims": [
            "graph_sota_or_leaderboard_claim",
            "hard_elliptic_performance_claim",
            "elliptic2_subgraph_claim",
        ],
        "blocked_reason_codes": [
            "graph_benchmark_not_run_yet",
            "graph_sota_claim_not_benchmarked",
            "paper_primary_claim_blocked_until_competitive_budget",
        ],
        "evidence_refs": {
            "provenance": "docs/reports/elliptic_graph_provenance_report.json",
            "split_report": "docs/reports/elliptic_temporal_split_report.json",
            "claim_taxonomy": "docs/reports/paper_claim_taxonomy.json",
        },
    }


def _build_paper_result_row(
    *,
    root: Path,
    data_dir: Path,
    provenance: dict[str, Any],
    split_report: dict[str, Any],
    claim_scope: dict[str, Any],
) -> dict[str, Any]:
    return {
        "schema_version": ELLIPTIC_GRAPH_SCHEMA_VERSION,
        "slice": "Paper Track P5",
        "status": "ok",
        "track_id": ELLIPTIC_TRACK_ID,
        "dataset_id": ELLIPTIC_DATASET_ID,
        "dataset_source_path": _display_path(root, data_dir),
        "claim_posture": "supporting-only",
        "claim_boundary_from_taxonomy": claim_scope["claim_boundary_from_taxonomy"],
        "supporting_public_claim_allowed": bool(claim_scope["raw_graph_loader_claim_allowed"]),
        "paper_primary_claim_allowed": False,
        "hard_performance_claims_allowed": False,
        "numeric_model_metrics_available": False,
        "paper_table_role": "graph_provenance_and_temporal_split_row",
        "publishable_performance_row_allowed": False,
        "evidence_partition": "loader_and_split_provenance",
        "graph_summary": {
            "node_count": provenance["graph_lineage"]["node_count"],
            "edge_count": provenance["graph_lineage"]["edge_count"],
            "feature_value_count": provenance["feature_lineage"]["feature_value_count_excluding_id_and_time"],
            "unique_time_step_count": split_report["unique_time_step_count"],
            "known_label_count": split_report["known_label_count"],
            "unknown_label_count": split_report["unknown_label_count"],
        },
        "metrics": {},
        "artifact_refs": {
            "manifest": "docs/reports/elliptic_graph_loader_manifest.json",
            "provenance": "docs/reports/elliptic_graph_provenance_report.json",
            "split_report": "docs/reports/elliptic_temporal_split_report.json",
            "claim_scope": "docs/reports/elliptic_graph_claim_scope.json",
            "paper_result_row": "docs/reports/elliptic_paper_result_row.json",
        },
        "public_claim_wording": claim_scope["allowed_public_wording"],
        "blocked_claims": claim_scope["blocked_claims"],
        "next_slice": "Paper Track P6",
    }


def _build_graph_loader_manifest(
    *,
    root: Path,
    data_dir: Path,
    registry: dict[str, Any],
    provenance: dict[str, Any],
    split_report: dict[str, Any],
    claim_scope: dict[str, Any],
) -> dict[str, Any]:
    return {
        "schema_version": ELLIPTIC_GRAPH_SCHEMA_VERSION,
        "slice": "Paper Track P5",
        "status": "ok",
        "dataset_id": ELLIPTIC_DATASET_ID,
        "track_id": ELLIPTIC_TRACK_ID,
        "source_path": _display_path(root, data_dir),
        "source_registry_ref": "docs/reports/paper_dataset_registry.json",
        "registry_status": registry.get("status"),
        "graph_input_mode": "raw_graph_bundle",
        "raw_graph_bundle_ready": True,
        "flattened_graph_ready": False,
        "subgraph_pack_ready": False,
        "node_count": provenance["graph_lineage"]["node_count"],
        "edge_count": provenance["graph_lineage"]["edge_count"],
        "feature_value_count": provenance["feature_lineage"]["feature_value_count_excluding_id_and_time"],
        "class_row_count": provenance["label_lineage"]["class_row_count"],
        "unique_time_step_count": split_report["unique_time_step_count"],
        "split_contract_id": ELLIPTIC_SPLIT_CONTRACT_ID,
        "temporal_split_status": split_report["status"],
        "claim_posture": "supporting-only",
        "raw_graph_loader_claim_allowed": claim_scope["raw_graph_loader_claim_allowed"],
        "graph_benchmark_performance_claim_allowed": False,
        "graph_sota_claim_allowed": False,
        "paper_primary_claim_allowed": False,
        "hard_performance_claims_allowed": False,
        "output_files": ELLIPTIC_GRAPH_FILENAMES,
        "command": "relaytic release-safety elliptic-graph --format json",
        "next_slice": "Paper Track P6",
        "blocked_reason_codes": [],
        "summary": "Elliptic raw graph provenance and temporal split proof completed; graph performance claims remain blocked until baseline/competitive graph benchmarks run.",
    }


def _blocked_pack(
    *,
    root: Path,
    data_dir: Path,
    registry: dict[str, Any],
    split_contracts: dict[str, Any],
    claim_taxonomy: dict[str, Any],
    reason_code: str,
    reason: str,
    missing_roles: list[str],
    split_report: dict[str, Any] | None = None,
) -> dict[str, Any]:
    boundary = _claim_boundary(ELLIPTIC_CLAIM_ID, claim_taxonomy)
    manifest = {
        "schema_version": ELLIPTIC_GRAPH_SCHEMA_VERSION,
        "slice": "Paper Track P5",
        "status": "blocked",
        "dataset_id": ELLIPTIC_DATASET_ID,
        "track_id": ELLIPTIC_TRACK_ID,
        "source_path": _display_path(root, data_dir),
        "source_registry_ref": "docs/reports/paper_dataset_registry.json",
        "registry_status": registry.get("status"),
        "graph_input_mode": "raw_graph_bundle",
        "raw_graph_bundle_ready": False,
        "flattened_graph_proxy_claim_allowed": False,
        "raw_graph_loader_claim_allowed": False,
        "graph_benchmark_performance_claim_allowed": False,
        "graph_sota_claim_allowed": False,
        "missing_required_roles": missing_roles,
        "missing_required_files": [
            ELLIPTIC_REQUIRED_FILES[role] for role in missing_roles if role in ELLIPTIC_REQUIRED_FILES
        ],
        "claim_posture": "supporting-only",
        "paper_primary_claim_allowed": False,
        "hard_performance_claims_allowed": False,
        "blocked_reason_codes": [reason_code],
        "recovery_instructions": ELLIPTIC_RECOVERY_INSTRUCTIONS,
        "summary": reason,
        "output_files": ELLIPTIC_GRAPH_FILENAMES,
        "next_slice": "Paper Track P5 repair before Paper Track P6",
    }
    provenance = {
        "schema_version": ELLIPTIC_GRAPH_SCHEMA_VERSION,
        "slice": "Paper Track P5",
        "status": "blocked",
        "dataset_id": ELLIPTIC_DATASET_ID,
        "track_id": ELLIPTIC_TRACK_ID,
        "source_path": _display_path(root, data_dir),
        "source_file_count": 0,
        "blocked_reason_codes": [reason_code],
        "recovery_instructions": ELLIPTIC_RECOVERY_INSTRUCTIONS,
        "summary": reason,
    }
    split_payload = split_report or {
        "schema_version": ELLIPTIC_GRAPH_SCHEMA_VERSION,
        "slice": "Paper Track P5",
        "status": "blocked",
        "dataset_id": ELLIPTIC_DATASET_ID,
        "track_id": ELLIPTIC_TRACK_ID,
        "split_contract_id": ELLIPTIC_SPLIT_CONTRACT_ID,
        "split_contract": _elliptic_split_contract(split_contracts),
        "blocked_reason_codes": [reason_code],
        "recovery_instructions": ELLIPTIC_RECOVERY_INSTRUCTIONS,
        "summary": reason,
    }
    claim_scope = {
        "schema_version": ELLIPTIC_GRAPH_SCHEMA_VERSION,
        "slice": "Paper Track P5",
        "status": "blocked",
        "dataset_id": ELLIPTIC_DATASET_ID,
        "track_id": ELLIPTIC_TRACK_ID,
        "claim_boundary_from_taxonomy": boundary,
        "claim_posture": "supporting-only",
        "raw_graph_loader_claim_allowed": False,
        "flattened_graph_proxy_claim_allowed": False,
        "graph_benchmark_performance_claim_allowed": False,
        "graph_sota_claim_allowed": False,
        "paper_primary_claim_allowed": False,
        "hard_performance_claims_allowed": False,
        "blocked_reason_codes": [reason_code],
        "recovery_instructions": ELLIPTIC_RECOVERY_INSTRUCTIONS,
        "summary": reason,
    }
    result_row = {
        "schema_version": ELLIPTIC_GRAPH_SCHEMA_VERSION,
        "slice": "Paper Track P5",
        "status": "blocked",
        "track_id": ELLIPTIC_TRACK_ID,
        "dataset_id": ELLIPTIC_DATASET_ID,
        "claim_posture": "supporting-only",
        "claim_boundary_from_taxonomy": boundary,
        "supporting_public_claim_allowed": False,
        "paper_primary_claim_allowed": False,
        "hard_performance_claims_allowed": False,
        "numeric_model_metrics_available": False,
        "paper_table_role": "graph_provenance_and_temporal_split_row",
        "publishable_performance_row_allowed": False,
        "blocked_reason_codes": [reason_code],
        "recovery_instructions": ELLIPTIC_RECOVERY_INSTRUCTIONS,
        "summary": reason,
    }
    return {
        "elliptic_graph_loader_manifest": manifest,
        "elliptic_graph_provenance_report": provenance,
        "elliptic_temporal_split_report": split_payload,
        "elliptic_graph_claim_scope": claim_scope,
        "elliptic_paper_result_row": result_row,
    }


def _empty_node_split_row(split: str) -> dict[str, Any]:
    return {
        "split": split,
        "node_count": 0,
        "known_label_count": 0,
        "unknown_label_count": 0,
        "illicit_count": 0,
        "licit_count": 0,
        "positive_rate_labeled": 0.0,
        "unknown_label_rate": 0.0,
        "time_step_min": None,
        "time_step_max": None,
        "class_coverage_ok": False,
    }


def _time_window(time_step: int, *, split_bounds: _SplitBounds) -> str:
    if time_step <= split_bounds.train_max_time_step:
        return "train"
    if time_step <= split_bounds.validation_max_time_step:
        return "validation"
    return "test"


def _normalize_elliptic_label(label: Any) -> str:
    text = str(label or "").strip().lower()
    if text in {"1", "illicit", "fraud", "suspicious", "true"}:
        return "illicit"
    if text in {"2", "licit", "benign", "false", "0"}:
        return "licit"
    return "unknown"


def _looks_like_header(row: list[str]) -> bool:
    joined = " ".join(str(value).lower() for value in row)
    return any(token in joined for token in ("txid", "class", "time", "feature", "source", "target"))


def _split_blockers(chronological_order_ok: bool, class_coverage_ok: bool, edge_time_ok: bool) -> list[str]:
    blocked = []
    if not chronological_order_ok:
        blocked.append("elliptic_chronological_order_failed")
    if not class_coverage_ok:
        blocked.append("elliptic_class_coverage_failed")
    if not edge_time_ok:
        blocked.append("elliptic_edge_time_coverage_failed")
    return blocked


def _source_file_record(
    *,
    root: Path,
    path: Path,
    role: str,
    file_checks: dict[str, dict[str, Any]],
    row_count: int | None = None,
) -> dict[str, Any]:
    display = _display_path(root, path)
    cached = file_checks.get(display, {})
    return {
        "role": role,
        "path": display,
        "exists": path.exists(),
        "size_bytes": cached.get("size_bytes") if cached else path.stat().st_size if path.exists() else None,
        "sha256": cached.get("sha256") if cached else _sha256(path) if path.exists() else None,
        "row_count": row_count,
        "format": path.suffix.lstrip(".") or "unknown",
    }


def _registry_file_checks(registry: dict[str, Any]) -> dict[str, dict[str, Any]]:
    checks: dict[str, dict[str, Any]] = {}
    for dataset in registry.get("datasets", []):
        if not isinstance(dataset, dict) or dataset.get("dataset_id") != ELLIPTIC_DATASET_ID:
            continue
        for item in dataset.get("required_file_checks", []):
            if isinstance(item, dict) and item.get("path"):
                checks[str(item["path"])] = dict(item)
    return checks


def _elliptic_split_contract(split_contracts: dict[str, Any]) -> dict[str, Any]:
    for contract in split_contracts.get("contracts", []):
        if contract.get("split_contract_id") == ELLIPTIC_SPLIT_CONTRACT_ID:
            return dict(contract)
    return {
        "split_contract_id": ELLIPTIC_SPLIT_CONTRACT_ID,
        "split_type": "temporal_graph_by_time_step",
        "forbidden_split_methods": ["random_node_split_across_time", "edge_leaking_future_to_train"],
        "required_order_fields": ["time_step"],
        "label_fields": ["class"],
    }


def _claim_boundary(claim_id: str, claim_taxonomy: dict[str, Any]) -> str | None:
    for claim in claim_taxonomy.get("claims", []):
        if claim.get("claim_id") == claim_id:
            return str(claim.get("boundary"))
    return None


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return value if isinstance(value, dict) else {}


def _sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _display_path(root: Path, path: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.name


def _safe_divide(numerator: float, denominator: float) -> float:
    if abs(denominator) <= 1e-12:
        return 0.0
    return float(numerator / denominator)


def _round_float(value: float | None, digits: int = 6) -> float | None:
    if value is None:
        return None
    return round(float(value), digits)
