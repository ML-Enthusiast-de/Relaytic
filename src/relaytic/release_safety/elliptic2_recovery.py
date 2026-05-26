"""Elliptic2 modern-benchmark recovery and pilot execution for Paper Track P8-A."""

from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import platform
import struct
from time import perf_counter
from typing import Any
from zipfile import ZIP_STORED, ZipFile

import numpy as np
import pandas as pd

from relaytic.core.json_utils import write_json


ELLIPTIC2_RECOVERY_SCHEMA_VERSION = "relaytic.elliptic2_recovery.v1"
ELLIPTIC2_RECOVERY_REPORT_DIR = Path("docs") / "reports"
ELLIPTIC2_RECOVERY_FILENAMES = {
    "elliptic2_recovery_manifest": "elliptic2_recovery_manifest.json",
    "elliptic2_schema_overlap_audit": "elliptic2_schema_overlap_audit.json",
    "elliptic2_protocol_audit": "elliptic2_protocol_audit.json",
    "elliptic2_modern_reference_contract": "elliptic2_modern_reference_contract.json",
    "elliptic2_context_pilot_result": "elliptic2_context_pilot_result.json",
    "elliptic2_recovery_gate": "elliptic2_recovery_gate.json",
}
DEFAULT_ELLIPTIC2_CORE_DIR = Path("data") / "paper_benchmarks" / "elliptic2"
DEFAULT_REVTRACK_DIR = Path("data") / "paper_benchmarks" / "elliptic2_revtrack"
ELLIPTIC2_CORE_REQUIRED_FILES = ["connected_components.csv", "nodes.csv", "edges.csv"]
ELLIPTIC2_BACKGROUND_FILES = ["background_nodes.csv", "background_edges.csv"]
ELLIPTIC2_CORE_COLUMNS = {
    "connected_components.csv": ["ccId", "ccLabel"],
    "nodes.csv": ["clId", "ccId"],
    "edges.csv": ["clId1", "clId2", "txId"],
}
REVTRACK_RAW_RELATIVE_DIR = Path("data") / "elliptic" / "raw"
REVTRACK_REQUIRED_FILES = ["data_df.pkl", "node_idx_map.pt", "raw_emb.pt"]
REVTRACK_SELECTED_CACHE = "selected_emb_numpy.npy"
REVTRACK_SELECTED_PROVENANCE = "selected_emb_provenance.json"
PINNED_ELLIPTIC2_GUIDE_COMMIT = "370f62655e60af63b8fdc0b95bb2191a5f19c9e8"
PINNED_REVTRACK_COMMIT = "f2111c8a1bafd84ebaa5a04e5caca8f1f0ed7ac0"
PINNED_REVTRACK_DATA_DF_SHA256 = "2baa712b67382aeade8d5e72dd07ddbffb1029b359a048c80a2300a3e3abc220"
PINNED_REVTRACK_NODE_INDEX_SHA256 = "dbb87889aa4aa90e0da558035cba27b2371590c2228ce4c2cdc708c35f23eddb"
PILOT_PRIMARY_VIEW_ID = "context_pooled_official_revtrack_embeddings"
PILOT_FEATURE_CONTRACT_ID = "p8a_revtrack_pooled_context_features_v1"
PILOT_MODEL_CONTRACT = {
    "family_id": "lightgbm_classifier",
    "n_estimators": 1200,
    "learning_rate": 0.03,
    "num_leaves": 31,
    "subsample": 0.9,
    "colsample_bytree": 0.8,
    "reg_lambda": 1.0,
    "class_weight": "balanced",
    "early_stopping_rounds": 75,
    "random_seed": 42,
}


def build_elliptic2_recovery_pack(
    project_root: str | Path,
    *,
    core_data_dir: str | Path | None = None,
    revtrack_dir: str | Path | None = None,
    prepare_selected_embeddings: bool = False,
    run_pilot: bool = False,
    hash_large_assets: bool = False,
) -> dict[str, Any]:
    """Build P8-A source, protocol, modern-reference, pilot, and claim-gate artifacts."""
    root = Path(project_root)
    core_dir = _resolve_dir(root, core_data_dir, DEFAULT_ELLIPTIC2_CORE_DIR)
    modern_dir = _resolve_dir(root, revtrack_dir, DEFAULT_REVTRACK_DIR)
    extraction_report: dict[str, Any] | None = None
    if prepare_selected_embeddings:
        extraction_report = _prepare_selected_embedding_cache(modern_dir)
    schema_audit = _build_schema_overlap_audit(root=root, core_dir=core_dir)
    modern_contract = _build_modern_reference_contract(
        root=root,
        revtrack_dir=modern_dir,
        extraction_report=extraction_report,
        hash_large_assets=hash_large_assets,
    )
    protocol_audit = _build_protocol_audit(schema_audit=schema_audit, modern_contract=modern_contract)
    pilot = _build_context_pilot_result(
        modern_contract=modern_contract,
        revtrack_dir=modern_dir,
        run_pilot=run_pilot,
    )
    gate = _build_recovery_gate(
        schema_audit=schema_audit,
        modern_contract=modern_contract,
        protocol_audit=protocol_audit,
        pilot=pilot,
    )
    manifest = {
        "schema_version": ELLIPTIC2_RECOVERY_SCHEMA_VERSION,
        "slice": "Paper Track P8-A",
        "status": gate["status"],
        "dataset_id": "elliptic2_subgraph_aml",
        "modern_reference_family": "RevClassify and RevTrack",
        "core_source_state": schema_audit["status"],
        "modern_reference_state": modern_contract["status"],
        "pilot_state": pilot["status"],
        "claim_posture": gate["claim_posture"],
        "headline_or_sota_claim_allowed": False,
        "mandatory_next_slice": gate["mandatory_next_slice"],
        "command_template": "relaytic release-safety elliptic2-recovery --core-data-dir <external-local-core-dir> --revtrack-dir <external-local-revtrack-dir> --run-pilot --hash-large-assets --format json",
        "output_files": ELLIPTIC2_RECOVERY_FILENAMES,
        "evidence_refs": {
            key: f"docs/reports/{filename}" for key, filename in ELLIPTIC2_RECOVERY_FILENAMES.items() if key != "elliptic2_recovery_manifest"
        },
    }
    return {
        "elliptic2_recovery_manifest": manifest,
        "elliptic2_schema_overlap_audit": schema_audit,
        "elliptic2_protocol_audit": protocol_audit,
        "elliptic2_modern_reference_contract": modern_contract,
        "elliptic2_context_pilot_result": pilot,
        "elliptic2_recovery_gate": gate,
    }


def sync_elliptic2_recovery_pack(
    project_root: str | Path,
    *,
    core_data_dir: str | Path | None = None,
    revtrack_dir: str | Path | None = None,
    output_dir: str | Path | None = None,
    prepare_selected_embeddings: bool = False,
    run_pilot: bool = False,
    hash_large_assets: bool = False,
) -> dict[str, Path]:
    """Write P8-A artifacts to ``docs/reports`` by default."""
    root = Path(project_root)
    report_dir = Path(output_dir) if output_dir is not None else root / ELLIPTIC2_RECOVERY_REPORT_DIR
    report_dir.mkdir(parents=True, exist_ok=True)
    artifacts = build_elliptic2_recovery_pack(
        root,
        core_data_dir=core_data_dir,
        revtrack_dir=revtrack_dir,
        prepare_selected_embeddings=prepare_selected_embeddings,
        run_pilot=run_pilot,
        hash_large_assets=hash_large_assets,
    )
    return {
        key: write_json(report_dir / filename, artifacts[key], indent=2, sort_keys=True)
        for key, filename in ELLIPTIC2_RECOVERY_FILENAMES.items()
    }


def render_elliptic2_recovery_markdown(pack: dict[str, Any]) -> str:
    schema = dict(pack.get("elliptic2_schema_overlap_audit", {}))
    pilot = dict(pack.get("elliptic2_context_pilot_result", {}))
    gate = dict(pack.get("elliptic2_recovery_gate", {}))
    selected = dict(pilot.get("primary_pilot_result", {}) or {})
    return "\n".join(
        [
            "# Elliptic2 Modern Recovery",
            "",
            f"- Gate: `{gate.get('status') or 'unknown'}`",
            f"- Official labeled core: `{schema.get('status') or 'unknown'}`",
            f"- Labeled subgraphs: `{schema.get('subgraph_count')}`",
            f"- Modern context pilot: `{pilot.get('status') or 'unknown'}`",
            f"- Pilot test PR-AUC: `{selected.get('test_pr_auc')}`",
            f"- Headline/SOTA claim allowed: `{gate.get('headline_or_sota_claim_allowed')}`",
            f"- Mandatory next slice: `{gate.get('mandatory_next_slice') or 'unknown'}`",
        ]
    )


def _build_schema_overlap_audit(*, root: Path, core_dir: Path) -> dict[str, Any]:
    required = _checks(root, core_dir, ELLIPTIC2_CORE_REQUIRED_FILES, include_hash=True)
    background = _checks(root, core_dir, ELLIPTIC2_BACKGROUND_FILES, include_hash=False)
    missing = [item["filename"] for item in required if not item["exists"]]
    blocked_reasons: list[str] = []
    if missing:
        blocked_reasons.append("official_labeled_subgraph_core_missing")
        return {
            "schema_version": ELLIPTIC2_RECOVERY_SCHEMA_VERSION,
            "slice": "Paper Track P8-A",
            "status": "blocked",
            "source_path": _display_path(root, core_dir),
            "required_file_checks": required,
            "background_file_checks": background,
            "blocked_reason_codes": blocked_reasons,
            "subgraph_core_pilot_allowed": False,
            "full_background_model_allowed": False,
        }
    try:
        components = pd.read_csv(core_dir / "connected_components.csv")
        nodes = pd.read_csv(core_dir / "nodes.csv")
        edges = pd.read_csv(core_dir / "edges.csv")
    except Exception:
        return {
            "schema_version": ELLIPTIC2_RECOVERY_SCHEMA_VERSION,
            "slice": "Paper Track P8-A",
            "status": "blocked",
            "source_path": _display_path(root, core_dir),
            "required_file_checks": required,
            "background_file_checks": background,
            "blocked_reason_codes": ["official_labeled_subgraph_core_not_readable_as_csv"],
            "subgraph_core_pilot_allowed": False,
            "full_background_model_allowed": False,
        }
    frames = {
        "connected_components.csv": components,
        "nodes.csv": nodes,
        "edges.csv": edges,
    }
    schema_failures = {
        filename: [column for column in columns if column not in frames[filename].columns]
        for filename, columns in ELLIPTIC2_CORE_COLUMNS.items()
    }
    schema_failures = {key: value for key, value in schema_failures.items() if value}
    if schema_failures:
        blocked_reasons.append("official_labeled_subgraph_schema_mismatch")
    if not schema_failures:
        node_components = nodes.groupby("clId")["ccId"].nunique()
        nodes_in_multiple_components = int((node_components > 1).sum())
        node_to_component = nodes.drop_duplicates("clId").set_index("clId")["ccId"]
        source_component = edges["clId1"].map(node_to_component)
        target_component = edges["clId2"].map(node_to_component)
        unknown_edge_endpoint_count = int((source_component.isna() | target_component.isna()).sum())
        cross_component_edge_count = int(
            (source_component.notna() & target_component.notna() & source_component.ne(target_component)).sum()
        )
        if nodes_in_multiple_components or cross_component_edge_count or unknown_edge_endpoint_count:
            blocked_reasons.append("subgraph_overlap_or_edge_membership_audit_failed")
        label_counts = {str(key): int(value) for key, value in components["ccLabel"].value_counts().items()}
    else:
        nodes_in_multiple_components = None
        unknown_edge_endpoint_count = None
        cross_component_edge_count = None
        label_counts = {}
    core_ready = not blocked_reasons
    background_ready = all(item["exists"] for item in background)
    return {
        "schema_version": ELLIPTIC2_RECOVERY_SCHEMA_VERSION,
        "slice": "Paper Track P8-A",
        "status": "core_ready" if core_ready else "blocked",
        "source_path": _display_path(root, core_dir),
        "required_file_checks": required,
        "background_file_checks": background,
        "schema_failures": schema_failures,
        "subgraph_count": int(len(components)),
        "node_membership_row_count": int(len(nodes)),
        "subgraph_edge_row_count": int(len(edges)),
        "label_counts": label_counts,
        "positive_label": "suspicious",
        "positive_rate": round(label_counts.get("suspicious", 0) / len(components), 8) if len(components) else None,
        "nodes_in_multiple_components": nodes_in_multiple_components,
        "unknown_edge_endpoint_count": unknown_edge_endpoint_count,
        "cross_component_edge_count": cross_component_edge_count,
        "blocked_reason_codes": blocked_reasons,
        "subgraph_core_pilot_allowed": core_ready,
        "full_background_model_allowed": core_ready and background_ready,
        "claim_scope": "official_labeled_subgraph_core_audit_and_pilot_only",
    }


def _build_modern_reference_contract(
    *,
    root: Path,
    revtrack_dir: Path,
    extraction_report: dict[str, Any] | None,
    hash_large_assets: bool,
) -> dict[str, Any]:
    raw_dir = revtrack_dir / REVTRACK_RAW_RELATIVE_DIR
    checks = _checks(root, raw_dir, REVTRACK_REQUIRED_FILES, include_hash=True, hash_large_assets=hash_large_assets)
    cache_checks = _checks(root, raw_dir, [REVTRACK_SELECTED_CACHE, REVTRACK_SELECTED_PROVENANCE], include_hash=True)
    files = {item["filename"]: item for item in checks + cache_checks}
    blockers: list[str] = []
    if not all(files[name]["exists"] for name in REVTRACK_REQUIRED_FILES):
        blockers.append("revtrack_official_runtime_assets_missing")
    if files["data_df.pkl"].get("sha256") != PINNED_REVTRACK_DATA_DF_SHA256:
        blockers.append("revtrack_preprocessed_table_not_pinned_official_asset")
    if files["node_idx_map.pt"].get("sha256") != PINNED_REVTRACK_NODE_INDEX_SHA256:
        blockers.append("revtrack_node_index_not_pinned_official_asset")
    if not files[REVTRACK_SELECTED_CACHE]["exists"]:
        blockers.append("low_memory_selected_embedding_cache_missing")
    provenance_validation = _validate_selected_cache_provenance(raw_dir=raw_dir, files=files)
    blockers.extend(provenance_validation["blocked_reason_codes"])
    modern_ready = not blockers
    partition: dict[str, Any] | None = None
    if modern_ready:
        data = pd.read_pickle(raw_dir / "data_df.pkl")
        partition = _partition_summary(data)
    return {
        "schema_version": ELLIPTIC2_RECOVERY_SCHEMA_VERSION,
        "slice": "Paper Track P8-A",
        "status": "ready_for_context_pilot" if modern_ready else "blocked",
        "reference_id": "revtrack_revclassify_icaif_2024",
        "reference_title": "Identifying Money Laundering Subgraphs on the Blockchain",
        "reference_code_url": "https://github.com/MITIBMxGraph/RevTrack",
        "reference_paper_url": "https://arxiv.org/abs/2410.08394",
        "reference_commit": PINNED_REVTRACK_COMMIT,
        "source_path": _display_path(root, revtrack_dir),
        "asset_checks": checks + cache_checks,
        "raw_embedding_hash_policy": (
            "sha256_recorded_for_this_recovery_run" if files["raw_emb.pt"].get("sha256") else "large_asset_hash_deferred_unless_requested"
        ),
        "selected_embedding_cache_derivation": {
            "status": "available" if files[REVTRACK_SELECTED_CACHE]["exists"] else "missing",
            "algorithm": "read the uncompressed float32 `archive/data/0` tensor payload in `raw_emb.pt` by memory map and select rows from pinned `node_idx_map.pt`",
            "purpose": "CPU/RAM-bounded execution cache; it does not alter official features or labels.",
            "extraction_report": extraction_report,
            "provenance_validation": provenance_validation,
        },
        "partition_summary": partition,
        "metric_contract": ["pr_auc", "roc_auc"],
        "official_model_targets": ["RevClassify_BP", "RevClassify_DS"],
        "blocked_reason_codes": blockers,
        "pilot_allowed": modern_ready,
        "claim_scope": "modern_official_reference_execution_input_not_relaytic_superiority",
    }


def _build_protocol_audit(
    *,
    schema_audit: dict[str, Any],
    modern_contract: dict[str, Any],
) -> dict[str, Any]:
    return {
        "schema_version": ELLIPTIC2_RECOVERY_SCHEMA_VERSION,
        "slice": "Paper Track P8-A",
        "status": "protocol_recovery_required_and_frozen",
        "original_elliptic2_reference": {
            "paper_url": "https://arxiv.org/abs/2404.19109",
            "official_guide_url": "https://github.com/MITIBMxGraph/Elliptic2",
            "official_guide_commit": PINNED_ELLIPTIC2_GUIDE_COMMIT,
            "reported_paper_split": "random 80:10:10 train/validation/test partition",
            "observed_public_preprocessor_split": "subgraph insertion-order modulo-10 assignment in `preprocess_glass.py`",
            "audit_finding": "paper prose and public preprocessing code do not define the same split construction; direct comparison must identify which protocol is reproduced.",
        },
        "modern_reference": {
            "reference_id": modern_contract["reference_id"],
            "reference_commit": modern_contract["reference_commit"],
            "partition_state": "pinned_official_TRN_VAL_TST_available" if modern_contract["partition_summary"] else "blocked",
            "metrics": ["pr_auc", "roc_auc"],
        },
        "source_core_ready": schema_audit.get("subgraph_core_pilot_allowed", False),
        "publication_protocols_required": [
            {
                "protocol_id": "p8a_revtrack_official_partition_comparability_v1",
                "role": "modern reference comparability",
                "split": "official RevTrack `TRN`/`VAL`/`TST` labels from pinned preprocessed artifact",
                "selection_rule": "model configuration and early stopping selected on validation only; test evaluated after selection",
            },
            {
                "protocol_id": "p8b_label_stratified_hash_robustness_v1",
                "role": "Relaytic robustness check independent of original row order",
                "split": "predeclared label-stratified deterministic hash split with frozen seeds and overlap audit",
                "selection_rule": "all budget and HPO decisions validation-only; report repeated-seed uncertainty",
            },
        ],
        "claim_rule": "A single official-partition pilot may establish feasibility, but modern paper claims require P8-B competitive and robustness proof.",
    }


def _build_context_pilot_result(
    *,
    modern_contract: dict[str, Any],
    revtrack_dir: Path,
    run_pilot: bool,
) -> dict[str, Any]:
    blocked_base = {
        "schema_version": ELLIPTIC2_RECOVERY_SCHEMA_VERSION,
        "slice": "Paper Track P8-A",
        "dataset_id": "elliptic2_subgraph_aml",
        "protocol_id": "p8a_revtrack_official_partition_comparability_v1",
        "feature_contract_id": PILOT_FEATURE_CONTRACT_ID,
        "primary_pilot_view_id": PILOT_PRIMARY_VIEW_ID,
        "model_contract": PILOT_MODEL_CONTRACT,
        "paper_table_candidate_allowed": False,
        "headline_or_sota_claim_allowed": False,
        "claim_scope": "exploratory_modern_context_pilot_not_paper_table",
    }
    if not run_pilot:
        return {
            **blocked_base,
            "status": "not_run",
            "blocked_reason_codes": ["context_pilot_not_requested"],
            "rows": [],
        }
    if not modern_contract["pilot_allowed"]:
        return {
            **blocked_base,
            "status": "blocked",
            "blocked_reason_codes": ["modern_reference_assets_not_ready_for_pilot"],
            "rows": [],
        }
    from lightgbm import LGBMClassifier, early_stopping, log_evaluation
    from sklearn.metrics import average_precision_score, roc_auc_score

    raw_dir = revtrack_dir / REVTRACK_RAW_RELATIVE_DIR
    started = perf_counter()
    embeddings = np.load(raw_dir / REVTRACK_SELECTED_CACHE, mmap_mode="r")
    data = pd.read_pickle(raw_dir / "data_df.pkl")
    shape_features = np.log1p(
        data[["senders_len", "source_len", "sink_len", "receivers_len"]].to_numpy(dtype=np.float32)
    )
    context_features = _pool_revtrack_features(data=data, embeddings=embeddings)
    masks = {
        "train": data["split"].eq("TRN").to_numpy(),
        "validation": data["split"].eq("VAL").to_numpy(),
        "test": data["split"].eq("TST").to_numpy(),
    }
    y = data["labels"].to_numpy(dtype=np.int64)
    rows: list[dict[str, Any]] = []
    for view_id, features in [
        ("structure_only_revtrack_roles", shape_features),
        (PILOT_PRIMARY_VIEW_ID, context_features),
    ]:
        model = LGBMClassifier(
            objective="binary",
            n_estimators=PILOT_MODEL_CONTRACT["n_estimators"],
            learning_rate=PILOT_MODEL_CONTRACT["learning_rate"],
            num_leaves=PILOT_MODEL_CONTRACT["num_leaves"],
            subsample=PILOT_MODEL_CONTRACT["subsample"],
            colsample_bytree=PILOT_MODEL_CONTRACT["colsample_bytree"],
            reg_lambda=PILOT_MODEL_CONTRACT["reg_lambda"],
            class_weight=PILOT_MODEL_CONTRACT["class_weight"],
            random_state=PILOT_MODEL_CONTRACT["random_seed"],
            n_jobs=-1,
            verbosity=-1,
        )
        model.fit(
            features[masks["train"]],
            y[masks["train"]],
            eval_set=[(features[masks["validation"]], y[masks["validation"]])],
            eval_metric="average_precision",
            callbacks=[early_stopping(PILOT_MODEL_CONTRACT["early_stopping_rounds"], verbose=False), log_evaluation(0)],
        )
        row: dict[str, Any] = {
            "feature_view_id": view_id,
            "feature_count": int(features.shape[1]),
            "best_iteration": int(model.best_iteration_),
            "selection_scope": "predeclared_view_with_validation_only_early_stopping",
        }
        for split in ["validation", "test"]:
            probability = model.predict_proba(features[masks[split]])[:, 1]
            row[f"{split}_pr_auc"] = round(float(average_precision_score(y[masks[split]], probability)), 6)
            row[f"{split}_roc_auc"] = round(float(roc_auc_score(y[masks[split]], probability)), 6)
            row[f"{split}_count"] = int(masks[split].sum())
            row[f"{split}_positive_count"] = int(y[masks[split]].sum())
        rows.append(row)
    primary = next(row for row in rows if row["feature_view_id"] == PILOT_PRIMARY_VIEW_ID)
    structural = next(row for row in rows if row["feature_view_id"] == "structure_only_revtrack_roles")
    return {
        **blocked_base,
        "status": "pilot_complete",
        "rows": rows,
        "primary_pilot_result": primary,
        "context_minus_structure_test_pr_auc": round(primary["test_pr_auc"] - structural["test_pr_auc"], 6),
        "runtime_seconds": round(perf_counter() - started, 6),
        "runtime_environment": {
            "python": platform.python_version(),
            "execution_posture": "cpu_bounded_selected_embedding_cache",
        },
        "blocked_reason_codes": [
            "single_pilot_configuration_not_release_budget",
            "official_revtrack_preprocessing_consumed_not_recomputed_by_relaytic",
            "robustness_partition_not_yet_executed",
        ],
    }


def _build_recovery_gate(
    *,
    schema_audit: dict[str, Any],
    modern_contract: dict[str, Any],
    protocol_audit: dict[str, Any],
    pilot: dict[str, Any],
) -> dict[str, Any]:
    pilot_complete = pilot["status"] == "pilot_complete"
    blockers = list(pilot.get("blocked_reason_codes", []))
    if schema_audit["status"] != "core_ready":
        blockers.append("official_core_source_not_audited")
    if modern_contract["status"] != "ready_for_context_pilot":
        blockers.extend(modern_contract["blocked_reason_codes"])
    return {
        "schema_version": ELLIPTIC2_RECOVERY_SCHEMA_VERSION,
        "slice": "Paper Track P8-A",
        "status": "pass_pilot_only" if pilot_complete else "blocked",
        "claim_posture": "modern_context_pilot_only" if pilot_complete else "blocked",
        "official_core_source_ready": schema_audit["status"] == "core_ready",
        "modern_reference_assets_ready": modern_contract["status"] == "ready_for_context_pilot",
        "modern_context_pilot_available": pilot_complete,
        "protocol_discrepancy_recorded": protocol_audit["status"] == "protocol_recovery_required_and_frozen",
        "paper_performance_row_allowed": False,
        "headline_or_sota_claim_allowed": False,
        "hard_aml_claim_allowed": False,
        "blocked_reason_codes": sorted(set(blockers)),
        "allowed_wording": (
            "Relaytic recovered executable Elliptic2 modern-context evidence and completed a strong exploratory pilot on the pinned RevTrack partition; competitive repeated-seed and robustness proof remain required before paper-table or superiority claims."
            if pilot_complete
            else "Elliptic2 remains blocked until official core, modern-reference assets, and a context pilot are auditable."
        ),
        "mandatory_next_slice": "Paper Track P8-B - Elliptic2 competitive and robustness suite",
        "p9_blocked_until_p8b_decision": True,
    }


def _prepare_selected_embedding_cache(revtrack_dir: Path) -> dict[str, Any]:
    import torch

    raw_dir = revtrack_dir / REVTRACK_RAW_RELATIVE_DIR
    raw_path = raw_dir / "raw_emb.pt"
    index_path = raw_dir / "node_idx_map.pt"
    output_path = raw_dir / REVTRACK_SELECTED_CACHE
    provenance_path = raw_dir / REVTRACK_SELECTED_PROVENANCE
    if not raw_path.is_file() or not index_path.is_file():
        return {"status": "blocked", "reason": "raw_emb.pt and node_idx_map.pt are required"}
    started = perf_counter()
    tensor = torch.load(raw_path, map_location="cpu", mmap=True, weights_only=True)
    if tensor.dtype != torch.float32 or tensor.ndim != 2:
        return {"status": "blocked", "reason": "raw_emb.pt must expose a two-dimensional float32 tensor"}
    index = torch.load(index_path, map_location="cpu", weights_only=True).numpy().astype(np.int64, copy=False)
    with ZipFile(raw_path) as archive:
        payload = next((entry for entry in archive.infolist() if entry.filename.endswith("/data/0")), None)
        if payload is None or payload.compress_type != ZIP_STORED:
            return {"status": "blocked", "reason": "raw_emb.pt payload is not available as an uncompressed tensor block"}
        offset = _zip_entry_data_offset(raw_path, payload.header_offset)
    memory = np.memmap(raw_path, dtype=np.float32, mode="r", offset=offset, shape=tuple(tensor.shape))
    selected = np.asarray(memory[index]).copy()
    np.save(output_path, selected)
    report = {
        "status": "ok",
        "raw_tensor_shape": [int(value) for value in tensor.shape],
        "selected_tensor_shape": [int(value) for value in selected.shape],
        "runtime_seconds": round(perf_counter() - started, 6),
        "output_filename": REVTRACK_SELECTED_CACHE,
        "raw_source_size_bytes": raw_path.stat().st_size,
        "node_idx_sha256": _sha256(index_path),
        "output_sha256": _sha256(output_path),
    }
    write_json(provenance_path, report, indent=2, sort_keys=True)
    return report


def _validate_selected_cache_provenance(*, raw_dir: Path, files: dict[str, dict[str, Any]]) -> dict[str, Any]:
    path = raw_dir / REVTRACK_SELECTED_PROVENANCE
    blockers: list[str] = []
    provenance: dict[str, Any] = {}
    if not path.is_file():
        blockers.append("low_memory_selected_embedding_provenance_missing")
    else:
        try:
            provenance = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            blockers.append("low_memory_selected_embedding_provenance_invalid")
    if provenance:
        if provenance.get("status") != "ok":
            blockers.append("low_memory_selected_embedding_provenance_invalid")
        if provenance.get("output_sha256") != files[REVTRACK_SELECTED_CACHE].get("sha256"):
            blockers.append("low_memory_selected_embedding_cache_hash_mismatch")
        if provenance.get("node_idx_sha256") != files["node_idx_map.pt"].get("sha256"):
            blockers.append("low_memory_selected_embedding_node_index_mismatch")
        if provenance.get("raw_source_size_bytes") != files["raw_emb.pt"].get("size_bytes"):
            blockers.append("low_memory_selected_embedding_raw_source_size_mismatch")
    return {
        "status": "verified" if not blockers else "blocked",
        "provenance_filename": REVTRACK_SELECTED_PROVENANCE,
        "provenance": provenance,
        "blocked_reason_codes": blockers,
    }


def _pool_revtrack_features(*, data: pd.DataFrame, embeddings: np.ndarray) -> np.ndarray:
    features = np.empty((len(data), embeddings.shape[1] * 4 + 4), dtype=np.float32)
    for index, row in enumerate(data.itertuples(index=False)):
        senders = embeddings[np.asarray(row.senders_mapped, dtype=np.int64)]
        receivers = embeddings[np.asarray(row.receivers_mapped, dtype=np.int64)]
        features[index] = np.concatenate(
            [
                senders.mean(axis=0),
                senders.max(axis=0),
                receivers.mean(axis=0),
                receivers.max(axis=0),
                np.log1p(np.asarray([row.senders_len, row.source_len, row.sink_len, row.receivers_len], dtype=np.float32)),
            ]
        )
    return features


def _partition_summary(data: pd.DataFrame) -> dict[str, Any]:
    rows: dict[str, Any] = {}
    for split in ["TRN", "VAL", "TST"]:
        subset = data[data["split"] == split]
        rows[split] = {
            "row_count": int(len(subset)),
            "positive_count": int(subset["labels"].sum()),
            "positive_rate": round(float(subset["labels"].mean()), 8),
        }
    return {"row_count": int(len(data)), "split_rows": rows}


def _checks(
    root: Path,
    directory: Path,
    filenames: list[str],
    *,
    include_hash: bool,
    hash_large_assets: bool = True,
) -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    for filename in filenames:
        path = directory / filename
        exists = path.is_file()
        is_large = exists and path.stat().st_size >= 1024 * 1024 * 1024
        should_hash = exists and include_hash and (hash_large_assets or not is_large)
        checks.append(
            {
                "filename": filename,
                "path": _display_path(root, path),
                "exists": exists,
                "size_bytes": path.stat().st_size if exists else None,
                "sha256": _sha256(path) if should_hash else None,
                "hash_status": "recorded" if should_hash else ("deferred_large_asset" if exists and include_hash else "not_requested"),
            }
        )
    return checks


def _zip_entry_data_offset(path: Path, header_offset: int) -> int:
    with path.open("rb") as handle:
        handle.seek(header_offset)
        header = handle.read(30)
    signature, _, _, _, _, _, _, _, _, filename_length, extra_length = struct.unpack("<IHHHHHIIIHH", header)
    if signature != 0x04034B50:
        raise ValueError("Invalid ZIP local file header in raw embedding asset.")
    return header_offset + 30 + filename_length + extra_length


def _resolve_dir(root: Path, supplied: str | Path | None, default: Path) -> Path:
    value = Path(supplied) if supplied is not None else root / default
    return value if value.is_absolute() else root / value


def _display_path(root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return f"<external-local-source>/{path.name}"


def _sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()
