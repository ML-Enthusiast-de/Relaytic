"""Competitive and robustness evidence for Elliptic2 Paper Track P8-B."""

from __future__ import annotations

from hashlib import sha256
from importlib import metadata as importlib_metadata
import json
from pathlib import Path
import platform
from statistics import mean, pstdev
from time import perf_counter
from typing import Any
import warnings

import numpy as np
import pandas as pd

from relaytic.core.json_utils import write_json

from . import elliptic2_recovery as recovery


ELLIPTIC2_COMPETITIVE_SCHEMA_VERSION = "relaytic.elliptic2_competitive.v1"
ELLIPTIC2_COMPETITIVE_REPORT_DIR = Path("docs") / "reports"
ELLIPTIC2_COMPETITIVE_FILENAMES = {
    "elliptic2_competitive_budget_contract": "elliptic2_competitive_budget_contract.json",
    "elliptic2_revclassify_reference_scorecard": "elliptic2_revclassify_reference_scorecard.json",
    "elliptic2_relaytic_candidate_search_trace": "elliptic2_relaytic_candidate_search_trace.json",
    "elliptic2_repeated_seed_scorecard": "elliptic2_repeated_seed_scorecard.json",
    "elliptic2_split_robustness_report": "elliptic2_split_robustness_report.json",
    "elliptic2_publishability_gate": "elliptic2_publishability_gate.json",
}
ELLIPTIC2_COMPETITIVE_ALLOWED_TIERS = {"smoke", "competitive"}
ELLIPTIC2_PUBLISHED_REFERENCE = {
    "reference_id": "revclassify_icaif_2024_full_shot",
    "metric": "pr_auc",
    "RevClassify_BP": {"pr_auc": 0.972, "f1": 0.954},
    "RevClassify_DS": {"pr_auc": 0.974, "f1": 0.953},
    "source": "Song et al. (2024), Table 1, RevClassifyDS row, full-shot PR-AUC column",
    "paper_url": "https://arxiv.org/abs/2410.08394",
    "versioned_pdf_url": "https://arxiv.org/pdf/2410.08394v1",
    "paper_doi": "10.1145/3677052.3698635",
    "accessed": "2026-07-13",
    "versioned_pdf_sha256": "b253d97531a0da6fd16a46bb54904437d4373984dfb2559e69c2104faaa08728",
    "cohort_scope": "published Elliptic2 full-shot benchmark; not asserted equivalent to Relaytic's pinned RevTrack-evaluable cohort",
}
ELLIPTIC2_ROBUSTNESS_SPLIT_ID = "p8b_label_stratified_content_hash_v1"
ELLIPTIC2_REFERENCE_SPLIT_ID = "p8a_revtrack_official_partition_comparability_v1"
ELLIPTIC2_SEEDS = [11, 42, 73]
ELLIPTIC2_PARITY_MARGIN = 0.01

_BASE_CONFIG = {
    "family_id": "lightgbm_classifier",
    "n_estimators": 1200,
    "learning_rate": 0.03,
    "num_leaves": 31,
    "subsample": 0.9,
    "subsample_freq": 1,
    "colsample_bytree": 0.8,
    "reg_lambda": 1.0,
    "class_weight": "balanced",
    "early_stopping_rounds": 75,
}
ELLIPTIC2_CANDIDATE_SPECS = [
    {
        "candidate_id": "p8a_pooled_mean_max_lgbm",
        "feature_view_id": "pooled_mean_max_counts",
        "feature_contract": "official_embeddings_sender_receiver_mean_max_plus_log_counts",
        "configuration": dict(_BASE_CONFIG),
    },
    {
        "candidate_id": "p8b_pooled_moments_lgbm",
        "feature_view_id": "pooled_moments_counts",
        "feature_contract": "official_embeddings_sender_receiver_mean_max_min_std_plus_log_counts",
        "configuration": {**_BASE_CONFIG, "num_leaves": 63, "learning_rate": 0.025, "n_estimators": 1400},
    },
    {
        "candidate_id": "p8b_pooled_moment_relations_lgbm",
        "feature_view_id": "pooled_moment_relations_counts",
        "feature_contract": "pooled_moments_plus_sender_receiver_relations_from_official_embeddings",
        "configuration": {**_BASE_CONFIG, "num_leaves": 63, "learning_rate": 0.02, "n_estimators": 1500},
    },
]


def build_elliptic2_competitive_pack(
    project_root: str | Path,
    *,
    revtrack_dir: str | Path | None = None,
    budget_tier: str = "smoke",
    run_suite: bool = False,
) -> dict[str, Any]:
    """Build P8-B artifacts with fail-closed candidate and robustness claims."""
    if budget_tier not in ELLIPTIC2_COMPETITIVE_ALLOWED_TIERS:
        raise ValueError("P8-B supports only `smoke` or `competitive` budget tiers.")
    root = Path(project_root)
    modern_dir = _resolve_dir(root, revtrack_dir, recovery.DEFAULT_REVTRACK_DIR)
    modern = recovery._build_modern_reference_contract(  # noqa: SLF001 - same bounded release-safety package
        root=root,
        revtrack_dir=modern_dir,
        extraction_report=None,
        hash_large_assets=False,
    )
    core_audit = _read_json(root / "docs" / "reports" / "elliptic2_schema_overlap_audit.json")
    reference = _build_reference_scorecard(root=root, revtrack_dir=modern_dir, modern=modern, core_audit=core_audit)
    if not run_suite or not modern.get("pilot_allowed"):
        reason = "p8b_competitive_execution_not_requested" if not run_suite else "p8b_modern_reference_assets_not_ready"
        return _blocked_pack(
            budget_tier=budget_tier,
            reference=reference,
            reason_code=reason,
            reason="P8-B requires verified modern-reference assets and an explicitly requested competitive execution.",
        )

    raw_dir = modern_dir / recovery.REVTRACK_RAW_RELATIVE_DIR
    data = pd.read_pickle(raw_dir / "data_df.pkl")
    embeddings = np.load(raw_dir / recovery.REVTRACK_SELECTED_CACHE, mmap_mode="r")
    effective_tier = "smoke" if len(data) < 1000 else budget_tier
    seeds = [42] if effective_tier == "smoke" else list(ELLIPTIC2_SEEDS)
    specs = ELLIPTIC2_CANDIDATE_SPECS[:1] if effective_tier == "smoke" else ELLIPTIC2_CANDIDATE_SPECS
    started = perf_counter()
    feature_views = _build_feature_views(data=data, embeddings=embeddings, view_ids={spec["feature_view_id"] for spec in specs})
    official_masks = _official_partition_masks(data)
    robust_split = _content_hash_split(data)
    robust_masks = _split_masks(robust_split["assignments"])
    search_trace, selected = _run_candidate_search(
        data=data,
        feature_views=feature_views,
        masks=official_masks,
        specs=specs,
    )
    repeated = _run_repeated_seeds(
        data=data,
        features=feature_views[selected["feature_view_id"]],
        selected=selected,
        official_masks=official_masks,
        robust_masks=robust_masks,
        seeds=seeds,
    )
    split_report = _build_split_robustness_report(
        data=data,
        core_audit=core_audit,
        official_masks=official_masks,
        robust_split=robust_split,
        robust_masks=robust_masks,
        repeated=repeated,
    )
    budget = _build_budget_contract(
        requested_tier=budget_tier,
        effective_tier=effective_tier,
        seeds=seeds,
        specs=specs,
        selected=selected,
        runtime_seconds=perf_counter() - started,
    )
    gate = _build_publishability_gate(
        budget=budget,
        reference=reference,
        search_trace=search_trace,
        repeated=repeated,
        split_report=split_report,
    )
    return {
        "elliptic2_competitive_budget_contract": budget,
        "elliptic2_revclassify_reference_scorecard": reference,
        "elliptic2_relaytic_candidate_search_trace": search_trace,
        "elliptic2_repeated_seed_scorecard": repeated,
        "elliptic2_split_robustness_report": split_report,
        "elliptic2_publishability_gate": gate,
    }


def sync_elliptic2_competitive_pack(
    project_root: str | Path,
    *,
    revtrack_dir: str | Path | None = None,
    output_dir: str | Path | None = None,
    budget_tier: str = "smoke",
    run_suite: bool = False,
) -> dict[str, Path]:
    """Write P8-B artifacts to ``docs/reports`` by default."""
    root = Path(project_root)
    report_dir = Path(output_dir) if output_dir is not None else root / ELLIPTIC2_COMPETITIVE_REPORT_DIR
    report_dir.mkdir(parents=True, exist_ok=True)
    artifacts = build_elliptic2_competitive_pack(
        root,
        revtrack_dir=revtrack_dir,
        budget_tier=budget_tier,
        run_suite=run_suite,
    )
    return {
        key: write_json(report_dir / filename, artifacts[key], indent=2, sort_keys=True)
        for key, filename in ELLIPTIC2_COMPETITIVE_FILENAMES.items()
    }


def refresh_elliptic2_reference_metadata(
    project_root: str | Path,
    *,
    output_dir: str | Path | None = None,
) -> dict[str, Path]:
    """Reconcile versioned-reference provenance without executing the P8-B suite again."""
    root = Path(project_root)
    report_dir = Path(output_dir) if output_dir is not None else root / ELLIPTIC2_COMPETITIVE_REPORT_DIR
    payloads = {
        key: _read_json(report_dir / filename)
        for key, filename in ELLIPTIC2_COMPETITIVE_FILENAMES.items()
    }
    missing = [key for key, payload in payloads.items() if not payload]
    if missing:
        raise ValueError(f"Cannot reconcile P8-B reference metadata; missing artifacts: {', '.join(missing)}.")

    scorecard = payloads["elliptic2_revclassify_reference_scorecard"]
    scorecard["reference"] = dict(ELLIPTIC2_PUBLISHED_REFERENCE)
    scorecard["reference_metadata_refresh"] = {
        "mode": "versioned_reference_provenance_reconciliation",
        "benchmark_reexecuted": False,
        "published_value_changed": False,
    }
    budget = payloads["elliptic2_competitive_budget_contract"]
    budget["test_exposure_disclosure"] = (
        "P8-A exposed the supplied TST metrics from the pinned external artifact before this competitive suite. "
        "The alternate content-hash partition supplies additional robustness evidence, not a pristine benchmark replacement."
    )
    trace = payloads["elliptic2_relaytic_candidate_search_trace"]
    trace["prior_test_exposure_disclosure"] = (
        "The supplied TST partition from the pinned external artifact was exposed during P8-A. "
        "Candidate selection in P8-B remained validation-only."
    )
    gate = payloads["elliptic2_publishability_gate"]
    gate["execution_status"] = {
        "status": "executed",
        "requested_tier": budget.get("requested_budget_tier"),
        "effective_tier": budget.get("effective_budget_tier"),
        "dataset_execution": "recorded_prior_local_revtrack_execution",
        "optional_adapter_execution_requested": False,
        "optional_adapter_skips": [],
        "blocked_reason_codes": [],
    }
    gate["blocked_reason_codes"] = [
        "pinned_external_artifact_and_embeddings_consumed"
        if code == "official_revtrack_preprocessing_and_embeddings_consumed"
        else code
        for code in list(gate.get("blocked_reason_codes", []))
    ]
    gate["allowed_wording"] = str(gate.get("allowed_wording", "")).replace(
        "official preprocessing boundary",
        "pinned external-artifact boundary and unresolved upstream provenance",
    ).replace(
        "provided RevTrack preprocessing boundary",
        "pinned external-artifact boundary and unresolved upstream provenance",
    )

    written = {
        key: write_json(report_dir / filename, payloads[key], indent=2, sort_keys=True)
        for key, filename in ELLIPTIC2_COMPETITIVE_FILENAMES.items()
    }
    metric_audit_path = report_dir / "paper_metric_cell_audit.json"
    metric_audit = _read_json(metric_audit_path)
    if metric_audit:
        for cell in metric_audit.get("numeric_cells", []):
            if not isinstance(cell, dict) or not str(cell.get("cell_id", "")).startswith("elliptic2_p8b_modern_context"):
                continue
            cell["leakage_posture"] = "provided_revtrack_tst_prior_exposure_disclosed_content_hash_partition_used_as_robustness_check"
            if cell.get("split") == "official_test":
                cell["split"] = "provided_revtrack_tst"
        written["paper_metric_cell_audit"] = write_json(metric_audit_path, metric_audit, indent=2, sort_keys=True)
    return written


def render_elliptic2_competitive_markdown(pack: dict[str, Any]) -> str:
    trace = dict(pack.get("elliptic2_relaytic_candidate_search_trace", {}))
    repeated = dict(pack.get("elliptic2_repeated_seed_scorecard", {}))
    gate = dict(pack.get("elliptic2_publishability_gate", {}))
    official = dict(repeated.get("official_partition", {}) or {})
    robust = dict(repeated.get("robustness_partition", {}) or {})
    selected = dict(trace.get("validation_selected_candidate", {}) or {})
    return "\n".join(
        [
            "# Elliptic2 Competitive And Robustness Suite",
            "",
            f"- Gate: `{gate.get('status') or 'unknown'}`",
            f"- Selected candidate: `{selected.get('candidate_id') or 'none'}`",
            f"- Official split mean test PR-AUC: `{official.get('test_pr_auc_mean')}`",
            f"- Hash robustness split mean test PR-AUC: `{robust.get('test_pr_auc_mean')}`",
            f"- Published RevClassifyDS full-shot PR-AUC: `{ELLIPTIC2_PUBLISHED_REFERENCE['RevClassify_DS']['pr_auc']}`",
            f"- Supporting row allowed: `{gate.get('supporting_paper_row_allowed')}`",
            f"- Reference parity claim allowed: `{gate.get('reference_parity_claim_allowed')}`",
            f"- Next slice: `{gate.get('next_slice') or 'unknown'}`",
        ]
    ).rstrip() + "\n"


def _build_reference_scorecard(
    *,
    root: Path,
    revtrack_dir: Path,
    modern: dict[str, Any],
    core_audit: dict[str, Any],
) -> dict[str, Any]:
    official_rows = int(core_audit.get("subgraph_count") or 0)
    official_positives = int(dict(core_audit.get("label_counts", {})).get("suspicious") or 0)
    partition = dict(modern.get("partition_summary", {}) or {})
    split_rows = dict(partition.get("split_rows", {}) or {})
    reference_rows = int(partition.get("row_count") or 0)
    reference_positives = sum(int(dict(row).get("positive_count") or 0) for row in split_rows.values())
    checkpoint_dir = revtrack_dir / "checkpoints"
    classification_checkpoints = list(checkpoint_dir.glob("RevClassify*/*.ckpt")) if checkpoint_dir.is_dir() else []
    reproduction_blockers = [
        "official_revclassify_classification_checkpoints_not_distributed_in_pinned_repository",
        "published_reference_used_single_v100_while_local_execution_is_cpu_only",
        "exact_official_training_sweep_not_executed_locally",
    ]
    if modern.get("status") != "ready_for_context_pilot":
        reproduction_blockers.append("pinned_modern_reference_assets_not_ready")
    return {
        "schema_version": ELLIPTIC2_COMPETITIVE_SCHEMA_VERSION,
        "slice": "Paper Track P8-B",
        "status": "reported_reference_with_local_path_audit",
        "reference": ELLIPTIC2_PUBLISHED_REFERENCE,
        "reference_repository": {
            "url": "https://github.com/MITIBMxGraph/RevTrack",
            "commit": recovery.PINNED_REVTRACK_COMMIT,
            "source_path": _display_path(root, revtrack_dir),
            "classification_checkpoint_count": len(classification_checkpoints),
            "published_training_resource": "single V100 GPU for paper experiments",
            "local_runtime_posture": "CPU-only verification and Relaytic candidate execution",
        },
        "official_reproduction_status": "not_locally_reproduced",
        "official_reproduction_blocked_reason_codes": reproduction_blockers,
        "cohort_coverage": {
            "official_core_subgraph_count": official_rows or None,
            "official_core_positive_count": official_positives or None,
            "revtrack_evaluable_row_count": reference_rows or None,
            "revtrack_evaluable_positive_count": reference_positives or None,
            "row_coverage_fraction": _ratio(reference_rows, official_rows),
            "positive_coverage_fraction": _ratio(reference_positives, official_positives),
            "cohort_equivalence_proven": False,
            "finding": "The pinned RevTrack evaluation table is smaller than the audited official Elliptic2 labeled core; modern-context results describe the RevTrack-evaluable cohort only.",
        },
        "claim_scope": "reported_modern_reference_and_evaluable_cohort_comparison_not_official_reference_reproduction",
    }


def _build_feature_views(
    *,
    data: pd.DataFrame,
    embeddings: np.ndarray,
    view_ids: set[str],
) -> dict[str, np.ndarray]:
    features: dict[str, list[np.ndarray]] = {view_id: [] for view_id in view_ids}
    for row in data.itertuples(index=False):
        senders = embeddings[np.asarray(row.senders_mapped, dtype=np.int64)]
        receivers = embeddings[np.asarray(row.receivers_mapped, dtype=np.int64)]
        counts = np.log1p(
            np.asarray([row.senders_len, row.source_len, row.sink_len, row.receivers_len], dtype=np.float32)
        )
        sender_mean, receiver_mean = senders.mean(axis=0), receivers.mean(axis=0)
        sender_max, receiver_max = senders.max(axis=0), receivers.max(axis=0)
        basic = np.concatenate([sender_mean, sender_max, receiver_mean, receiver_max, counts])
        if "pooled_mean_max_counts" in features:
            features["pooled_mean_max_counts"].append(basic)
        if "pooled_moments_counts" in features or "pooled_moment_relations_counts" in features:
            moments = np.concatenate(
                [
                    sender_mean,
                    sender_max,
                    senders.min(axis=0),
                    senders.std(axis=0),
                    receiver_mean,
                    receiver_max,
                    receivers.min(axis=0),
                    receivers.std(axis=0),
                    counts,
                ]
            )
            if "pooled_moments_counts" in features:
                features["pooled_moments_counts"].append(moments)
            if "pooled_moment_relations_counts" in features:
                relation = np.concatenate(
                    [
                        moments,
                        sender_mean - receiver_mean,
                        np.abs(sender_mean - receiver_mean),
                        sender_mean * receiver_mean,
                        sender_max - receiver_max,
                        np.abs(sender_max - receiver_max),
                        sender_max * receiver_max,
                    ]
                )
                features["pooled_moment_relations_counts"].append(relation)
    return {key: np.asarray(rows, dtype=np.float32) for key, rows in features.items()}


def _run_candidate_search(
    *,
    data: pd.DataFrame,
    feature_views: dict[str, np.ndarray],
    masks: dict[str, np.ndarray],
    specs: list[dict[str, Any]],
) -> tuple[dict[str, Any], dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    fitted: list[tuple[dict[str, Any], Any]] = []
    for spec in specs:
        model, result = _fit_model(
            features=feature_views[spec["feature_view_id"]],
            y=data["labels"].to_numpy(dtype=np.int64),
            masks=masks,
            configuration=spec["configuration"],
            seed=42,
            evaluate_test=False,
        )
        row = {**spec, **result, "selection_surface": "official_validation_pr_auc_only"}
        rows.append(row)
        fitted.append((row, model))
    winner_row, winner_model = max(fitted, key=lambda item: float(item[0]["validation_pr_auc"]))
    features = feature_views[winner_row["feature_view_id"]]
    y = data["labels"].to_numpy(dtype=np.int64)
    test_probability = _predict_probability(winner_model, features[masks["test"]])
    selected = {
        **winner_row,
        "test_evaluated": True,
        "test_pr_auc": _pr_auc(y[masks["test"]], test_probability),
        "test_roc_auc": _roc_auc(y[masks["test"]], test_probability),
        "test_count": int(masks["test"].sum()),
        "test_positive_count": int(y[masks["test"]].sum()),
        "test_exposure_disclosure": "P8-A already evaluated this official test partition; P8-B is confirmatory rather than an untouched final holdout.",
    }
    return {
        "schema_version": ELLIPTIC2_COMPETITIVE_SCHEMA_VERSION,
        "slice": "Paper Track P8-B",
        "status": "candidate_search_complete",
        "selection_metric": "official_validation_pr_auc",
        "selection_policy": "candidate view and configuration selected using official validation only; only selected candidate evaluated on official test",
        "prior_test_exposure_disclosed": True,
        "candidates": rows,
        "validation_selected_candidate": selected,
    }, selected


def _run_repeated_seeds(
    *,
    data: pd.DataFrame,
    features: np.ndarray,
    selected: dict[str, Any],
    official_masks: dict[str, np.ndarray],
    robust_masks: dict[str, np.ndarray],
    seeds: list[int],
) -> dict[str, Any]:
    y = data["labels"].to_numpy(dtype=np.int64)
    rows_by_partition: dict[str, list[dict[str, Any]]] = {}
    for partition_id, masks in [
        ("official_partition", official_masks),
        ("robustness_partition", robust_masks),
    ]:
        rows = []
        for seed in seeds:
            _, result = _fit_model(
                features=features,
                y=y,
                masks=masks,
                configuration=dict(selected["configuration"]),
                seed=seed,
                evaluate_test=True,
            )
            rows.append({"seed": seed, **result})
        rows_by_partition[partition_id] = rows
    return {
        "schema_version": ELLIPTIC2_COMPETITIVE_SCHEMA_VERSION,
        "slice": "Paper Track P8-B",
        "status": "complete",
        "candidate_id": selected["candidate_id"],
        "feature_view_id": selected["feature_view_id"],
        "seeds": seeds,
        "official_partition": _summarize_seed_rows(rows_by_partition["official_partition"]),
        "robustness_partition": _summarize_seed_rows(rows_by_partition["robustness_partition"]),
        "test_exposure_disclosure": "The official RevTrack test split was previously observed in P8-A; repeated official-partition scoring is confirmatory. The content-hash partition is the newly predeclared robustness check.",
    }


def _fit_model(
    *,
    features: np.ndarray,
    y: np.ndarray,
    masks: dict[str, np.ndarray],
    configuration: dict[str, Any],
    seed: int,
    evaluate_test: bool,
) -> tuple[Any, dict[str, Any]]:
    from lightgbm import LGBMClassifier, early_stopping, log_evaluation

    started = perf_counter()
    model = LGBMClassifier(
        objective="binary",
        n_estimators=int(configuration["n_estimators"]),
        learning_rate=float(configuration["learning_rate"]),
        num_leaves=int(configuration["num_leaves"]),
        subsample=float(configuration["subsample"]),
        subsample_freq=int(configuration["subsample_freq"]),
        colsample_bytree=float(configuration["colsample_bytree"]),
        reg_lambda=float(configuration["reg_lambda"]),
        class_weight=configuration["class_weight"],
        random_state=seed,
        n_jobs=-1,
        verbosity=-1,
    )
    model.fit(
        features[masks["train"]],
        y[masks["train"]],
        eval_set=[(features[masks["validation"]], y[masks["validation"]])],
        eval_metric="average_precision",
        callbacks=[early_stopping(int(configuration["early_stopping_rounds"]), verbose=False), log_evaluation(0)],
    )
    validation_probability = _predict_probability(model, features[masks["validation"]])
    result: dict[str, Any] = {
        "seed": seed,
        "feature_count": int(features.shape[1]),
        "best_iteration": int(model.best_iteration_),
        "validation_pr_auc": _pr_auc(y[masks["validation"]], validation_probability),
        "validation_roc_auc": _roc_auc(y[masks["validation"]], validation_probability),
        "validation_count": int(masks["validation"].sum()),
        "validation_positive_count": int(y[masks["validation"]].sum()),
        "runtime_seconds": round(perf_counter() - started, 6),
    }
    if evaluate_test:
        test_probability = _predict_probability(model, features[masks["test"]])
        result.update(
            {
                "test_pr_auc": _pr_auc(y[masks["test"]], test_probability),
                "test_roc_auc": _roc_auc(y[masks["test"]], test_probability),
                "test_count": int(masks["test"].sum()),
                "test_positive_count": int(y[masks["test"]].sum()),
            }
        )
    else:
        result.update({"test_evaluated": False, "test_pr_auc": None, "test_roc_auc": None})
    return model, result


def _content_hash_split(data: pd.DataFrame) -> dict[str, Any]:
    keys = [_content_key(row) for row in data.itertuples(index=False)]
    duplicate_key_count = len(keys) - len(set(keys))
    labels = data["labels"].to_numpy(dtype=np.int64)
    assignments = np.empty(len(data), dtype=object)
    for label in sorted(set(labels.tolist())):
        indices = np.flatnonzero(labels == label).tolist()
        indices.sort(key=lambda index: keys[index])
        train_end = int(len(indices) * 0.8)
        validation_end = train_end + int(len(indices) * 0.1)
        for rank, index in enumerate(indices):
            assignments[index] = "TRN" if rank < train_end else ("VAL" if rank < validation_end else "TST")
    return {
        "split_contract_id": ELLIPTIC2_ROBUSTNESS_SPLIT_ID,
        "assignments": assignments,
        "duplicate_content_key_count": int(duplicate_key_count),
        "row_order_independent": duplicate_key_count == 0,
        "identity_basis": "sha256 over sorted original sender, source, sink, receiver, node, and edge identifiers; label used only for strata allocation",
    }


def _content_key(row: Any) -> str:
    payload = {
        "senders": sorted(int(value) for value in row.senders),
        "source": sorted(int(value) for value in row.source),
        "sink": sorted(int(value) for value in row.sink),
        "receivers": sorted(int(value) for value in row.receivers),
        "node_ids": sorted(int(value) for value in row.node_ids),
        "edge_index": sorted([list(map(int, edge)) for edge in row.edge_index]),
    }
    return sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


def _build_split_robustness_report(
    *,
    data: pd.DataFrame,
    core_audit: dict[str, Any],
    official_masks: dict[str, np.ndarray],
    robust_split: dict[str, Any],
    robust_masks: dict[str, np.ndarray],
    repeated: dict[str, Any],
) -> dict[str, Any]:
    official_overlap = _identity_overlap_report(data=data, masks=official_masks)
    robust_overlap = _identity_overlap_report(data=data, masks=robust_masks)
    official_test = dict(repeated["official_partition"])
    robust_test = dict(repeated["robustness_partition"])
    drop = (
        float(official_test["test_pr_auc_mean"]) - float(robust_test["test_pr_auc_mean"])
        if official_test.get("test_pr_auc_mean") is not None and robust_test.get("test_pr_auc_mean") is not None
        else None
    )
    return {
        "schema_version": ELLIPTIC2_COMPETITIVE_SCHEMA_VERSION,
        "slice": "Paper Track P8-B",
        "status": "pass" if robust_split["row_order_independent"] else "blocked",
        "official_partition": {
            "split_contract_id": ELLIPTIC2_REFERENCE_SPLIT_ID,
            "row_summary": _mask_summary(data, official_masks),
            "sender_receiver_identity_overlap": official_overlap,
            "test_previously_exposed_in_p8a": True,
        },
        "robustness_partition": {
            "split_contract_id": ELLIPTIC2_ROBUSTNESS_SPLIT_ID,
            "row_summary": _mask_summary(data, robust_masks),
            "row_order_independent": robust_split["row_order_independent"],
            "duplicate_content_key_count": robust_split["duplicate_content_key_count"],
            "identity_basis": robust_split["identity_basis"],
            "sender_receiver_identity_overlap": robust_overlap,
            "protocol_repair_note": "A provisional boundary-only hash omitted source/sink identifiers and failed uniqueness; the accepted predeclared content key includes all available subgraph role and edge identifiers and passes with zero duplicate keys.",
        },
        "cohort_scope": {
            "official_core_subgraph_count": core_audit.get("subgraph_count"),
            "revtrack_evaluable_row_count": int(len(data)),
            "claim_boundary": "All P8-B metrics are measured on the pinned RevTrack-evaluable cohort, not proven equivalent to the full current Elliptic2 core.",
        },
        "official_minus_robust_test_pr_auc_mean": round(drop, 6) if drop is not None else None,
        "generalization_interpretation": "Hash splitting removes row-order dependence but does not eliminate sender/receiver identity overlap; entity-disjoint and newly curated cohort proof remains a stronger future requirement.",
    }


def _build_budget_contract(
    *,
    requested_tier: str,
    effective_tier: str,
    seeds: list[int],
    specs: list[dict[str, Any]],
    selected: dict[str, Any],
    runtime_seconds: float,
) -> dict[str, Any]:
    return {
        "schema_version": ELLIPTIC2_COMPETITIVE_SCHEMA_VERSION,
        "slice": "Paper Track P8-B",
        "status": "executed",
        "requested_budget_tier": requested_tier,
        "effective_budget_tier": effective_tier,
        "candidate_count": len(specs),
        "repeated_seed_count": len(seeds),
        "seeds": seeds,
        "candidate_family": "LightGBM over explicitly pooled official RevTrack node embeddings",
        "candidate_specs": specs,
        "validation_selected_candidate_id": selected["candidate_id"],
        "selection_rule": "choose the candidate with highest official-validation PR-AUC; evaluate official test only for that candidate; freeze it for repeated and robustness runs",
        "test_exposure_disclosure": "P8-A exposed the official test metrics before this competitive suite; the alternate content-hash partition supplies new robustness evidence, not a pristine benchmark replacement.",
        "runtime_seconds": round(runtime_seconds, 6),
        "runtime_environment": {
            "python": platform.python_version(),
            "lightgbm": _package_version("lightgbm"),
            "execution_posture": "local_cpu_bounded",
        },
    }


def _build_publishability_gate(
    *,
    budget: dict[str, Any],
    reference: dict[str, Any],
    search_trace: dict[str, Any],
    repeated: dict[str, Any],
    split_report: dict[str, Any],
) -> dict[str, Any]:
    official = dict(repeated.get("official_partition", {}))
    robust = dict(repeated.get("robustness_partition", {}))
    official_pr = official.get("test_pr_auc_mean")
    robust_pr = robust.get("test_pr_auc_mean")
    reference_pr = ELLIPTIC2_PUBLISHED_REFERENCE["RevClassify_DS"]["pr_auc"]
    checks = {
        "competitive_budget_executed": budget.get("effective_budget_tier") == "competitive",
        "validation_only_candidate_selection_recorded": search_trace.get("selection_metric") == "official_validation_pr_auc",
        "official_test_prior_exposure_disclosed": bool(search_trace.get("prior_test_exposure_disclosed")),
        "repeated_seed_evidence_available": int(budget.get("repeated_seed_count") or 0) >= 3,
        "row_order_independent_robustness_partition_passed": split_report.get("status") == "pass",
        "modern_context_quality_survives_official_partition": official_pr is not None and float(official_pr) >= 0.90,
        "modern_context_quality_survives_hash_partition": robust_pr is not None and float(robust_pr) >= 0.90,
        "within_declared_reference_parity_margin": official_pr is not None
        and float(official_pr) >= float(reference_pr) - ELLIPTIC2_PARITY_MARGIN,
        "official_reference_locally_reproduced": reference.get("official_reproduction_status") == "locally_reproduced",
        "full_official_core_cohort_equivalence_proven": bool(
            dict(reference.get("cohort_coverage", {})).get("cohort_equivalence_proven")
        ),
    }
    supporting = all(
        checks[key]
        for key in [
            "competitive_budget_executed",
            "validation_only_candidate_selection_recorded",
            "official_test_prior_exposure_disclosed",
            "repeated_seed_evidence_available",
            "row_order_independent_robustness_partition_passed",
            "modern_context_quality_survives_official_partition",
            "modern_context_quality_survives_hash_partition",
        ]
    )
    parity = supporting and checks["within_declared_reference_parity_margin"]
    blockers = [key for key, value in checks.items() if not value]
    next_slice = (
        "Paper Track P9 - operational AML evaluation layer"
        if parity
        else "Paper Track P8-C - modern subgraph reference parity and leakage-resistant cohort protocol"
    )
    return {
        "schema_version": ELLIPTIC2_COMPETITIVE_SCHEMA_VERSION,
        "slice": "Paper Track P8-B",
        "status": "pass_supporting_modern_context_only" if supporting else "blocked",
        "execution_status": {
            "status": "executed",
            "requested_tier": budget.get("requested_budget_tier"),
            "effective_tier": budget.get("effective_budget_tier"),
            "dataset_execution": "completed_from_local_revtrack_assets",
            "optional_adapter_execution_requested": False,
            "optional_adapter_skips": [],
            "blocked_reason_codes": [],
        },
        "protocol_checks": checks,
        "supporting_paper_row_allowed": supporting,
        "reference_parity_claim_allowed": parity,
        "headline_or_sota_claim_allowed": False,
        "end_to_end_relaytic_superiority_claim_allowed": False,
        "hard_aml_claim_allowed": False,
        "blocked_reason_codes": blockers
        + [
            "pinned_external_artifact_and_embeddings_consumed",
            "official_test_partition_was_exposed_during_p8a",
            "entity_disjoint_generalization_not_yet_proven",
        ],
        "allowed_wording": (
            "Relaytic executed a repeated-seed, alternate-split context workflow on a pinned external RevTrack-format artifact. Results may be reported only as non-comparable context with the artifact boundary, prior test exposure, and unresolved upstream provenance explicit. No SOTA, full-core, parity, or end-to-end superiority claim is allowed."
            if supporting
            else "Relaytic recovered modern Elliptic2 execution, but the competitive and robustness gate did not support a paper performance row."
        ),
        "published_reference_pr_auc": reference_pr,
        "selected_official_test_pr_auc_mean": official_pr,
        "official_gap_to_published_revclassify_ds": (
            round(float(official_pr) - float(reference_pr), 6) if official_pr is not None else None
        ),
        "next_slice": next_slice,
        "p9_allowed": parity,
        "summary": "P8-B separates executable modern-context evidence from modern reference parity and rejects broad claims unless both protocol and performance requirements pass.",
    }


def _blocked_pack(
    *,
    budget_tier: str,
    reference: dict[str, Any],
    reason_code: str,
    reason: str,
) -> dict[str, Any]:
    common = {
        "schema_version": ELLIPTIC2_COMPETITIVE_SCHEMA_VERSION,
        "slice": "Paper Track P8-B",
        "status": "blocked",
        "blocked_reason_codes": [reason_code],
        "summary": reason,
    }
    return {
        "elliptic2_competitive_budget_contract": {**common, "requested_budget_tier": budget_tier},
        "elliptic2_revclassify_reference_scorecard": reference,
        "elliptic2_relaytic_candidate_search_trace": {**common, "candidates": [], "validation_selected_candidate": None},
        "elliptic2_repeated_seed_scorecard": {**common, "official_partition": None, "robustness_partition": None},
        "elliptic2_split_robustness_report": {**common, "robustness_partition": None},
        "elliptic2_publishability_gate": {
            **common,
            "supporting_paper_row_allowed": False,
            "reference_parity_claim_allowed": False,
            "headline_or_sota_claim_allowed": False,
            "end_to_end_relaytic_superiority_claim_allowed": False,
            "hard_aml_claim_allowed": False,
            "execution_status": {
                "status": "blocked",
                "dataset_execution": "not_completed",
                "optional_adapter_execution_requested": False,
                "optional_adapter_skips": [],
                "blocked_reason_codes": [reason_code],
            },
            "next_slice": "Paper Track P8-B repair before Paper Track P9",
            "p9_allowed": False,
        },
    }


def _official_partition_masks(data: pd.DataFrame) -> dict[str, np.ndarray]:
    return {
        "train": data["split"].eq("TRN").to_numpy(),
        "validation": data["split"].eq("VAL").to_numpy(),
        "test": data["split"].eq("TST").to_numpy(),
    }


def _split_masks(assignments: np.ndarray) -> dict[str, np.ndarray]:
    return {
        "train": assignments == "TRN",
        "validation": assignments == "VAL",
        "test": assignments == "TST",
    }


def _mask_summary(data: pd.DataFrame, masks: dict[str, np.ndarray]) -> dict[str, Any]:
    y = data["labels"].to_numpy(dtype=np.int64)
    return {
        split: {
            "row_count": int(mask.sum()),
            "positive_count": int(y[mask].sum()),
            "positive_rate": round(float(y[mask].mean()), 8) if mask.any() else None,
        }
        for split, mask in masks.items()
    }


def _identity_overlap_report(*, data: pd.DataFrame, masks: dict[str, np.ndarray]) -> dict[str, Any]:
    split_entities: dict[str, set[int]] = {}
    for split, mask in masks.items():
        subset = data.loc[mask]
        split_entities[split] = {
            int(value)
            for column in ["senders", "receivers"]
            for values in subset[column]
            for value in values
        }
    train_entities = split_entities["train"]
    output: dict[str, Any] = {}
    for split in ["validation", "test"]:
        entities = split_entities[split]
        overlap = train_entities & entities
        output[f"train_to_{split}"] = {
            "evaluation_entity_count": len(entities),
            "overlap_entity_count": len(overlap),
            "overlap_fraction": _ratio(len(overlap), len(entities)),
        }
    return output


def _summarize_seed_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    test_values = [float(row["test_pr_auc"]) for row in rows]
    validation_values = [float(row["validation_pr_auc"]) for row in rows]
    return {
        "rows": rows,
        "seed_count": len(rows),
        "validation_pr_auc_mean": round(mean(validation_values), 6),
        "validation_pr_auc_std": round(pstdev(validation_values), 6),
        "test_pr_auc_mean": round(mean(test_values), 6),
        "test_pr_auc_std": round(pstdev(test_values), 6),
        "test_pr_auc_min": round(min(test_values), 6),
        "test_pr_auc_max": round(max(test_values), 6),
        "failure_case_count": sum(value < 0.90 for value in test_values),
    }


def _pr_auc(y: np.ndarray, probability: np.ndarray) -> float:
    from sklearn.metrics import average_precision_score

    return round(float(average_precision_score(y, probability)), 6)


def _predict_probability(model: Any, features: np.ndarray) -> np.ndarray:
    with warnings.catch_warnings():
        warnings.filterwarnings(
            "ignore",
            message="X does not have valid feature names, but LGBMClassifier was fitted with feature names",
            category=UserWarning,
        )
        return model.predict_proba(features)[:, 1]


def _roc_auc(y: np.ndarray, probability: np.ndarray) -> float:
    from sklearn.metrics import roc_auc_score

    return round(float(roc_auc_score(y, probability)), 6)


def _package_version(package_name: str) -> str | None:
    try:
        return importlib_metadata.version(package_name)
    except importlib_metadata.PackageNotFoundError:
        return None


def _read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return value if isinstance(value, dict) else {}


def _resolve_dir(root: Path, supplied: str | Path | None, default: Path) -> Path:
    value = Path(supplied) if supplied is not None else root / default
    return value if value.is_absolute() else root / value


def _display_path(root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return f"<external-local-source>/{path.name}"


def _ratio(numerator: int, denominator: int) -> float | None:
    return round(float(numerator / denominator), 8) if denominator else None
