"""Temporal-safe Elliptic graph baseline suite for Paper Track P7."""

from __future__ import annotations

import copy
import csv
from dataclasses import dataclass
from hashlib import sha256
from importlib import metadata as importlib_metadata
import importlib.util
import math
import platform
from pathlib import Path
from time import perf_counter
from typing import Any
import warnings

import numpy as np
import pandas as pd

from relaytic.core.json_utils import write_json

from .elliptic_graph import (
    ELLIPTIC_DATASET_ID,
    ELLIPTIC_DEFAULT_DATA_DIR,
    ELLIPTIC_REQUIRED_FILES,
    ELLIPTIC_SPLIT_CONTRACT_ID,
    ELLIPTIC_TRACK_ID,
    build_elliptic_graph_pack,
)
from .paysim_benchmark import (
    FIXED_FPR_TARGET,
    SELECTED_REVIEW_BUDGET_FRACTION,
    _binary_score_metrics,
    _threshold_for_fpr,
    _threshold_for_review_fraction,
    _threshold_metrics,
)


PAPER_GRAPH_SCHEMA_VERSION = "relaytic.paper_graph_baseline_suite.v1"
PAPER_GRAPH_REPORT_DIR = Path("docs") / "reports"
PAPER_GRAPH_FILENAMES = {
    "paper_graph_baseline_manifest": "paper_graph_baseline_manifest.json",
    "paper_graph_feature_table": "paper_graph_feature_table.json",
    "paper_graph_model_shadow_scorecard": "paper_graph_model_shadow_scorecard.json",
    "paper_graph_baseline_fallback_report": "paper_graph_baseline_fallback_report.json",
    "paper_graph_budget_contract": "paper_graph_budget_contract.json",
    "paper_graph_competitive_search_trace": "paper_graph_competitive_search_trace.json",
    "paper_graph_publishability_gate": "paper_graph_publishability_gate.json",
}
PAPER_GRAPH_ALLOWED_BUDGET_TIERS = {"smoke", "baseline", "competitive"}
PAPER_GRAPH_FEATURE_CONTRACT_ID = "p7_elliptic_same_step_observable_graph_features_v1"
PAPER_GRAPH_RANDOM_SEED = 42
PAPER_GRAPH_STRUCTURAL_FEATURE_COLUMNS = [
    "in_degree_same_step",
    "out_degree_same_step",
    "total_degree_same_step",
    "log1p_in_degree_same_step",
    "log1p_out_degree_same_step",
    "log1p_total_degree_same_step",
    "reciprocal_in_degree_same_step",
    "reciprocal_out_degree_same_step",
    "has_reciprocal_edge_same_step",
    "component_size_same_step",
    "log1p_component_size_same_step",
    "isolated_in_snapshot",
]


@dataclass(frozen=True)
class _GraphData:
    official_features: np.ndarray
    structural_features: np.ndarray
    labels: np.ndarray
    times: np.ndarray
    train_mask: np.ndarray
    validation_mask: np.ndarray
    test_mask: np.ndarray
    labeled_mask: np.ndarray
    edge_index: np.ndarray
    node_count: int
    raw_edge_count: int
    same_step_edge_count: int
    excluded_cross_step_edge_count: int
    feature_value_count: int


def build_paper_graph_baseline_pack(
    project_root: str | Path,
    *,
    data_dir: str | Path | None = None,
    budget_tier: str = "smoke",
    run_optional: bool = False,
) -> dict[str, Any]:
    """Build P7 Elliptic graph baseline artifacts without writing them."""
    if budget_tier not in PAPER_GRAPH_ALLOWED_BUDGET_TIERS:
        raise ValueError("P7 supports `smoke`, `baseline`, or `competitive` graph budget tiers.")
    root = Path(project_root)
    resolved_data_dir = Path(data_dir) if data_dir is not None else root / ELLIPTIC_DEFAULT_DATA_DIR
    if not resolved_data_dir.is_absolute():
        resolved_data_dir = root / resolved_data_dir
    p5_pack = build_elliptic_graph_pack(root, data_dir=resolved_data_dir)
    p5_manifest = dict(p5_pack["elliptic_graph_loader_manifest"])
    if p5_manifest.get("status") != "ok":
        return _blocked_pack(
            root=root,
            data_dir=resolved_data_dir,
            budget_tier=budget_tier,
            reason_code="p7_elliptic_provenance_or_split_not_ready",
            reason="P7 requires a passing P5 Elliptic raw-graph provenance and temporal split pack.",
        )

    try:
        graph_data = _load_graph_data(
            data_dir=resolved_data_dir,
            split_report=dict(p5_pack["elliptic_temporal_split_report"]),
        )
        if not _has_class_coverage(graph_data):
            return _blocked_pack(
                root=root,
                data_dir=resolved_data_dir,
                budget_tier=budget_tier,
                reason_code="p7_labeled_split_class_coverage_failed",
                reason="P7 requires licit and illicit labeled nodes in train, validation, and test windows.",
            )
        effective_budget_tier = "smoke" if graph_data.node_count < 1_000 else budget_tier
        baseline_rows, attempts, selected, view_selected_rows = _execute_tabular_graph_baselines(
            graph_data=graph_data,
            effective_budget_tier=effective_budget_tier,
            run_optional=run_optional,
        )
        shadow_scorecard = _build_graph_model_shadow_scorecard(
            graph_data=graph_data,
            effective_budget_tier=effective_budget_tier,
            run_optional=run_optional,
        )
    except Exception as exc:  # pragma: no cover - defensive command surface
        return _blocked_pack(
            root=root,
            data_dir=resolved_data_dir,
            budget_tier=budget_tier,
            reason_code="p7_graph_baseline_execution_failed",
            reason=f"Elliptic graph baseline suite could not be constructed: {exc}",
        )

    feature_table = _build_feature_table(
        graph_data=graph_data,
        baseline_rows=baseline_rows,
        selected=selected,
        view_selected_rows=view_selected_rows,
        effective_budget_tier=effective_budget_tier,
    )
    budget_contract = _build_budget_contract(
        requested_budget_tier=budget_tier,
        effective_budget_tier=effective_budget_tier,
        run_optional=run_optional,
        attempts=attempts,
        shadow_scorecard=shadow_scorecard,
    )
    fallback_report = _build_fallback_report(
        attempts=attempts,
        shadow_scorecard=shadow_scorecard,
        run_optional=run_optional,
    )
    search_trace = _build_search_trace(
        attempts=attempts,
        selected=selected,
        effective_budget_tier=effective_budget_tier,
        shadow_scorecard=shadow_scorecard,
    )
    gate = _build_publishability_gate(
        graph_data=graph_data,
        feature_table=feature_table,
        shadow_scorecard=shadow_scorecard,
        effective_budget_tier=effective_budget_tier,
    )
    manifest = _build_manifest(
        root=root,
        data_dir=resolved_data_dir,
        graph_data=graph_data,
        feature_table=feature_table,
        shadow_scorecard=shadow_scorecard,
        budget_contract=budget_contract,
        gate=gate,
    )
    return {
        "paper_graph_baseline_manifest": manifest,
        "paper_graph_feature_table": feature_table,
        "paper_graph_model_shadow_scorecard": shadow_scorecard,
        "paper_graph_baseline_fallback_report": fallback_report,
        "paper_graph_budget_contract": budget_contract,
        "paper_graph_competitive_search_trace": search_trace,
        "paper_graph_publishability_gate": gate,
    }


def sync_paper_graph_baseline_pack(
    project_root: str | Path,
    *,
    data_dir: str | Path | None = None,
    output_dir: str | Path | None = None,
    budget_tier: str = "smoke",
    run_optional: bool = False,
) -> dict[str, Path]:
    """Write P7 artifacts to ``docs/reports`` by default."""
    root = Path(project_root)
    report_dir = Path(output_dir) if output_dir is not None else root / PAPER_GRAPH_REPORT_DIR
    report_dir.mkdir(parents=True, exist_ok=True)
    artifacts = build_paper_graph_baseline_pack(
        root,
        data_dir=data_dir,
        budget_tier=budget_tier,
        run_optional=run_optional,
    )
    return {
        key: write_json(report_dir / filename, artifacts[key], indent=2, sort_keys=True)
        for key, filename in PAPER_GRAPH_FILENAMES.items()
    }


def render_paper_graph_baseline_markdown(pack: dict[str, Any]) -> str:
    manifest = dict(pack.get("paper_graph_baseline_manifest", {}))
    table = dict(pack.get("paper_graph_feature_table", {}))
    scorecard = dict(pack.get("paper_graph_model_shadow_scorecard", {}))
    gate = dict(pack.get("paper_graph_publishability_gate", {}))
    selected = dict(table.get("validation_selected_competitive_baseline", {}) or {})
    return "\n".join(
        [
            "# Paper Graph Baseline Suite",
            "",
            f"- Status: `{manifest.get('status') or 'unknown'}`",
            f"- Effective budget tier: `{manifest.get('effective_budget_tier') or 'unknown'}`",
            f"- Same-step observable edges: `{manifest.get('same_step_edge_count') or 0}`",
            f"- Validation-selected baseline: `{selected.get('family_id') or 'none'}`",
            f"- Selected feature view: `{selected.get('feature_view_id') or 'none'}`",
            f"- Validation PR-AUC: `{selected.get('validation_pr_auc')}`",
            f"- Fixed test PR-AUC: `{selected.get('test_pr_auc')}`",
            f"- Graph model shadow state: `{scorecard.get('graph_model_execution_state') or 'unknown'}`",
            f"- Supporting graph table candidate: `{gate.get('supporting_graph_table_candidate_allowed')}`",
            f"- Headline graph claim allowed: `{gate.get('headline_graph_claim_allowed')}`",
            f"- Next slice: `{manifest.get('next_slice') or 'unknown'}`",
        ]
    ).rstrip() + "\n"


def _load_graph_data(*, data_dir: Path, split_report: dict[str, Any]) -> _GraphData:
    required_paths = {role: data_dir / filename for role, filename in ELLIPTIC_REQUIRED_FILES.items()}
    features = _read_feature_frame(required_paths["features"])
    labels = _read_label_frame(required_paths["classes"])
    frame = features.merge(labels, on="txid", how="left", validate="one_to_one")
    frame["label"] = frame["label"].map(_numeric_label).fillna(-1).astype("int8")
    times = frame["time_step"].to_numpy(dtype="int16")
    split_rows = {str(row["split"]): row for row in split_report["split_rows"]}
    train_max = int(split_rows["train"]["time_step_max"])
    validation_max = int(split_rows["validation"]["time_step_max"])
    labels_array = frame["label"].to_numpy(dtype="int8")
    labeled_mask = labels_array >= 0
    train_mask = labeled_mask & (times <= train_max)
    validation_mask = labeled_mask & (times > train_max) & (times <= validation_max)
    test_mask = labeled_mask & (times > validation_max)
    edges = _read_edge_frame(required_paths["edges"])
    node_index = pd.Series(np.arange(len(frame), dtype="int64"), index=frame["txid"])
    src = edges["src"].map(node_index)
    dst = edges["dst"].map(node_index)
    present = src.notna() & dst.notna()
    src_idx = src.loc[present].to_numpy(dtype="int64")
    dst_idx = dst.loc[present].to_numpy(dtype="int64")
    same_step = times[src_idx] == times[dst_idx]
    safe_src = src_idx[same_step]
    safe_dst = dst_idx[same_step]
    edge_index = np.asarray([safe_src, safe_dst], dtype="int64")
    structural = _derive_structural_features(
        node_count=len(frame),
        source=safe_src,
        destination=safe_dst,
    )
    official_columns = [column for column in frame.columns if str(column).startswith("feature_")]
    official = frame[official_columns].to_numpy(dtype="float32")
    return _GraphData(
        official_features=official,
        structural_features=structural,
        labels=labels_array,
        times=times,
        train_mask=train_mask,
        validation_mask=validation_mask,
        test_mask=test_mask,
        labeled_mask=labeled_mask,
        edge_index=edge_index,
        node_count=int(len(frame)),
        raw_edge_count=int(len(edges)),
        same_step_edge_count=int(np.sum(same_step)),
        excluded_cross_step_edge_count=int(np.sum(~same_step)),
        feature_value_count=int(len(official_columns)),
    )


def _read_feature_frame(path: Path) -> pd.DataFrame:
    with path.open("r", newline="", encoding="utf-8-sig") as handle:
        first = next(csv.reader(handle))
    width = len(first)
    if width < 3:
        raise ValueError("Elliptic feature file must include transaction ID, time step, and feature values.")
    skiprows = 1 if not _numeric(first[1]) else 0
    dtype: dict[int, str] = {0: "string", 1: "float32"}
    dtype.update({index: "float32" for index in range(2, width)})
    frame = pd.read_csv(path, header=None, skiprows=skiprows, dtype=dtype)
    frame.columns = ["txid", "time_step", *(f"feature_{index:03d}" for index in range(width - 2))]
    frame["time_step"] = frame["time_step"].astype("int16")
    return frame


def _read_label_frame(path: Path) -> pd.DataFrame:
    with path.open("r", newline="", encoding="utf-8-sig") as handle:
        first = next(csv.reader(handle))
    skiprows = 1 if str(first[0]).strip().lower() in {"txid", "tx_id", "id"} else 0
    frame = pd.read_csv(path, header=None, skiprows=skiprows, usecols=[0, 1], dtype="string")
    frame.columns = ["txid", "label"]
    return frame


def _read_edge_frame(path: Path) -> pd.DataFrame:
    with path.open("r", newline="", encoding="utf-8-sig") as handle:
        first = next(csv.reader(handle))
    skiprows = 1 if str(first[0]).strip().lower() in {"txid1", "src", "source"} else 0
    frame = pd.read_csv(path, header=None, skiprows=skiprows, usecols=[0, 1], dtype="string")
    frame.columns = ["src", "dst"]
    return frame


def _numeric_label(value: Any) -> int:
    label = str(value).strip().lower()
    if label in {"1", "illicit", "1_illicit"}:
        return 1
    if label in {"2", "licit", "2_licit"}:
        return 0
    return -1


def _numeric(value: str) -> bool:
    try:
        float(str(value).strip())
        return True
    except ValueError:
        return False


def _derive_structural_features(*, node_count: int, source: np.ndarray, destination: np.ndarray) -> np.ndarray:
    in_degree = np.bincount(destination, minlength=node_count).astype("float32")
    out_degree = np.bincount(source, minlength=node_count).astype("float32")
    total_degree = in_degree + out_degree
    edge_pairs = set(zip(source.tolist(), destination.tolist()))
    reciprocal_mask = np.asarray(
        [(int(dst), int(src)) in edge_pairs for src, dst in zip(source, destination)],
        dtype=bool,
    )
    reciprocal_in = np.bincount(destination[reciprocal_mask], minlength=node_count).astype("float32")
    reciprocal_out = np.bincount(source[reciprocal_mask], minlength=node_count).astype("float32")
    component_size = _component_sizes(node_count=node_count, source=source, destination=destination)
    return np.asarray(
        np.vstack(
            [
                in_degree,
                out_degree,
                total_degree,
                np.log1p(in_degree),
                np.log1p(out_degree),
                np.log1p(total_degree),
                reciprocal_in,
                reciprocal_out,
                ((reciprocal_in + reciprocal_out) > 0).astype("float32"),
                component_size,
                np.log1p(component_size),
                (total_degree == 0).astype("float32"),
            ]
        ).T,
        dtype="float32",
    )


def _component_sizes(*, node_count: int, source: np.ndarray, destination: np.ndarray) -> np.ndarray:
    parent = np.arange(node_count, dtype="int64")
    size = np.ones(node_count, dtype="int64")

    def find(index: int) -> int:
        while parent[index] != index:
            parent[index] = parent[parent[index]]
            index = int(parent[index])
        return index

    for src, dst in zip(source.tolist(), destination.tolist()):
        left = find(int(src))
        right = find(int(dst))
        if left == right:
            continue
        if size[left] < size[right]:
            left, right = right, left
        parent[right] = left
        size[left] += size[right]
    roots = np.asarray([find(index) for index in range(node_count)], dtype="int64")
    counts = np.bincount(roots, minlength=node_count)
    return counts[roots].astype("float32")


def _feature_views(graph_data: _GraphData) -> dict[str, np.ndarray]:
    return {
        "structural_same_snapshot_only": graph_data.structural_features,
        "source_provided_flattened_features": graph_data.official_features,
        "source_features_plus_structural_snapshot": np.hstack(
            [graph_data.official_features, graph_data.structural_features]
        ).astype("float32"),
    }


def _execute_tabular_graph_baselines(
    *,
    graph_data: _GraphData,
    effective_budget_tier: str,
    run_optional: bool,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any] | None, list[dict[str, Any]]]:
    views = _feature_views(graph_data)
    train_y = graph_data.labels[graph_data.train_mask].astype(int)
    validation_y = graph_data.labels[graph_data.validation_mask].astype(int)
    test_y = graph_data.labels[graph_data.test_mask].astype(int)
    rows: list[dict[str, Any]] = []
    attempts: list[dict[str, Any]] = []
    fixed_model, fixed_config = _make_tabular_model(
        family_id="sklearn_extra_trees",
        config={"n_estimators": 80 if effective_budget_tier == "smoke" else 240, "max_depth": 18, "min_samples_leaf": 3},
    )
    fixed_x = views["structural_same_snapshot_only"]
    started = perf_counter()
    fixed_model.fit(fixed_x[graph_data.train_mask], train_y)
    fixed_validation_scores = _predict_scores(fixed_model, fixed_x[graph_data.validation_mask])
    fixed_test_scores = _predict_scores(fixed_model, fixed_x[graph_data.test_mask])
    fixed_threshold = _threshold_for_review_fraction(fixed_validation_scores, SELECTED_REVIEW_BUDGET_FRACTION)
    fixed_row = {
        "row_id": "structural_same_snapshot_extra_trees_floor",
        "family_id": "sklearn_extra_trees",
        "feature_view_id": "structural_same_snapshot_only",
        "evidence_type": "deterministic_label_free_structural_graph_features",
        "row_status": "baseline",
        "selection_role": "predeclared_structural_floor",
        "configuration": fixed_config,
        "runtime_seconds": _round_float(perf_counter() - started),
        "validation_metrics": _binary_score_metrics(validation_y, fixed_validation_scores),
        "test_metrics": _binary_score_metrics(test_y, fixed_test_scores),
        "test_evaluated": True,
        "validation_threshold": _round_float(fixed_threshold),
        "validation_operating_point": _threshold_metrics(
            validation_y,
            fixed_validation_scores,
            threshold=fixed_threshold,
            requested_fraction=SELECTED_REVIEW_BUDGET_FRACTION,
        ),
        "threshold_applied_unchanged_to_test": True,
        "test_operating_point": _threshold_metrics(
            test_y,
            fixed_test_scores,
            threshold=fixed_threshold,
            requested_fraction=SELECTED_REVIEW_BUDGET_FRACTION,
        ),
    }
    rows.append(fixed_row)
    attempts.append({**fixed_row, "execution_state": "ran", "stage": "fixed_structural_baseline"})

    fitted: list[dict[str, Any]] = []
    for view_id, family_id, module, config in _tabular_specs(
        effective_budget_tier=effective_budget_tier,
        run_optional=run_optional,
    ):
        trial_id = f"{view_id}::{family_id}::{len(attempts)}"
        if module and not _module_available(module):
            attempts.append(
                {
                    "trial_id": trial_id,
                    "stage": "validation_search",
                    "family_id": family_id,
                    "feature_view_id": view_id,
                    "execution_state": "fallback",
                    "blocked_reason": "optional_adapter_not_installed",
                }
            )
            continue
        if module and not run_optional:
            attempts.append(
                {
                    "trial_id": trial_id,
                    "stage": "validation_search",
                    "family_id": family_id,
                    "feature_view_id": view_id,
                    "execution_state": "eligible_not_run",
                    "blocked_reason": "optional_execution_not_requested",
                }
            )
            continue
        started = perf_counter()
        try:
            model, materialized = _make_tabular_model(family_id=family_id, config=config)
            matrix = views[view_id]
            model.fit(matrix[graph_data.train_mask], train_y)
            scores = _predict_scores(model, matrix[graph_data.validation_mask])
            result = {
                "trial_id": trial_id,
                "stage": "validation_search",
                "family_id": family_id,
                "feature_view_id": view_id,
                "evidence_type": _evidence_type(view_id),
                "row_status": "competitive" if effective_budget_tier == "competitive" else "baseline",
                "execution_state": "ran",
                "runtime_seconds": _round_float(perf_counter() - started),
                "configuration": materialized,
                "adapter_module": module or "scikit-learn",
                "adapter_version": _module_version(module or "scikit-learn"),
                "validation_metrics": _binary_score_metrics(validation_y, scores),
                "test_metrics": None,
                "test_evaluated": False,
                "selection_surface": "validation_pr_auc_only_before_test_evaluation",
            }
            attempts.append(result)
            rows.append({key: value for key, value in result.items() if key != "execution_state"})
            fitted.append({**result, "_model": model, "_matrix": matrix})
        except Exception as exc:
            attempts.append(
                {
                    "trial_id": trial_id,
                    "stage": "validation_search",
                    "family_id": family_id,
                    "feature_view_id": view_id,
                    "execution_state": "fallback",
                    "runtime_seconds": _round_float(perf_counter() - started),
                    "blocked_reason": f"execution_failed: {exc}",
                }
            )
    view_selected_rows: list[dict[str, Any]] = []
    for view_id in views:
        view_winner = max(
            [row for row in fitted if row["feature_view_id"] == view_id],
            key=lambda row: float(row["validation_metrics"]["pr_auc"]),
            default=None,
        )
        if view_winner is None:
            continue
        evaluated = _evaluate_validation_selected_candidate(
            winner=view_winner,
            graph_data=graph_data,
            validation_y=validation_y,
            test_y=test_y,
            effective_budget_tier=effective_budget_tier,
        )
        view_selected_rows.append(evaluated)
        for row in rows:
            if row.get("trial_id") == view_winner.get("trial_id"):
                row["selected_for_view_test_evaluation"] = True
                row["test_evaluated"] = True
                row["test_metrics"] = {
                    "pr_auc": evaluated["test_pr_auc"],
                    "roc_auc": evaluated["test_roc_auc"],
                }
    winner = max(fitted, key=lambda row: float(row["validation_metrics"]["pr_auc"]), default=None)
    selected = next(
        (row for row in view_selected_rows if winner is not None and row["trial_id"] == winner["trial_id"]),
        None,
    )
    if selected is not None:
        selected["global_validation_selected"] = True
    return rows, attempts, selected, view_selected_rows


def _evaluate_validation_selected_candidate(
    *,
    winner: dict[str, Any],
    graph_data: _GraphData,
    validation_y: np.ndarray,
    test_y: np.ndarray,
    effective_budget_tier: str,
) -> dict[str, Any]:
    matrix = winner["_matrix"]
    raw_validation = _predict_scores(winner["_model"], matrix[graph_data.validation_mask])
    raw_test = _predict_scores(winner["_model"], matrix[graph_data.test_mask])
    calibration, validation_scores, test_scores, operating_indices = _calibrate_scores(
        validation_y=validation_y,
        validation_times=graph_data.times[graph_data.validation_mask],
        validation_scores=raw_validation,
        test_scores=raw_test,
    )
    operating_y = validation_y[operating_indices]
    operating_scores = validation_scores[operating_indices]
    review_threshold = _threshold_for_review_fraction(operating_scores, SELECTED_REVIEW_BUDGET_FRACTION)
    fpr_threshold = _threshold_for_fpr(operating_y, operating_scores, target_fpr=FIXED_FPR_TARGET)
    return {
        "trial_id": winner["trial_id"],
        "family_id": winner["family_id"],
        "feature_view_id": winner["feature_view_id"],
        "evidence_type": winner["evidence_type"],
        "row_status": "competitive" if effective_budget_tier == "competitive" else "baseline",
        "configuration": winner["configuration"],
        "adapter_module": winner["adapter_module"],
        "adapter_version": winner["adapter_version"],
        "selection_surface": "validation_pr_auc_within_predeclared_feature_view_before_test_evaluation",
        "test_evaluation_role": "paired_feature_view_comparison_not_test_driven_model_selection",
        "calibration": calibration,
        "validation_pr_auc": winner["validation_metrics"]["pr_auc"],
        "test_pr_auc": _binary_score_metrics(test_y, test_scores)["pr_auc"],
        "test_roc_auc": _binary_score_metrics(test_y, test_scores)["roc_auc"],
        "raw_test_pr_auc": _binary_score_metrics(test_y, raw_test)["pr_auc"],
        "review_budget_fraction": SELECTED_REVIEW_BUDGET_FRACTION,
        "validation_threshold": _round_float(review_threshold),
        "validation_operating_partition_row_count": int(len(operating_y)),
        "validation_operating_point": _threshold_metrics(
            operating_y,
            operating_scores,
            threshold=review_threshold,
            requested_fraction=SELECTED_REVIEW_BUDGET_FRACTION,
        ),
        "threshold_selection_surface": "validation_operating_partition_only",
        "threshold_applied_unchanged_to_test": True,
        "comparison_operator": ">=",
        "tie_rule": "include_scores_equal_to_threshold",
        "test_operating_point": _threshold_metrics(
            test_y,
            test_scores,
            threshold=review_threshold,
            requested_fraction=SELECTED_REVIEW_BUDGET_FRACTION,
        ),
        "fixed_fpr": {
            "target_fpr": FIXED_FPR_TARGET,
            "test": _threshold_metrics(
                test_y,
                test_scores,
                threshold=fpr_threshold,
                requested_fraction=None,
            ),
        },
    }


def _tabular_specs(*, effective_budget_tier: str, run_optional: bool) -> list[tuple[str, str, str | None, dict[str, Any]]]:
    del run_optional
    if effective_budget_tier == "smoke":
        return [
            ("structural_same_snapshot_only", "sklearn_extra_trees", None, {"n_estimators": 40, "max_depth": 10, "min_samples_leaf": 1}),
            ("source_provided_flattened_features", "sklearn_extra_trees", None, {"n_estimators": 40, "max_depth": 12, "min_samples_leaf": 1}),
            ("source_features_plus_structural_snapshot", "sklearn_extra_trees", None, {"n_estimators": 40, "max_depth": 12, "min_samples_leaf": 1}),
            ("source_features_plus_structural_snapshot", "lightgbm_classifier", "lightgbm", {"n_estimators": 50, "learning_rate": 0.06, "num_leaves": 15, "min_child_samples": 3}),
        ]
    base = [
        ("structural_same_snapshot_only", "sklearn_extra_trees", None, {"n_estimators": 200, "max_depth": 18, "min_samples_leaf": 3}),
        ("structural_same_snapshot_only", "sklearn_extra_trees", None, {"n_estimators": 260, "max_depth": None, "min_samples_leaf": 8}),
        ("source_provided_flattened_features", "sklearn_extra_trees", None, {"n_estimators": 240, "max_depth": 22, "min_samples_leaf": 3}),
        ("source_features_plus_structural_snapshot", "sklearn_extra_trees", None, {"n_estimators": 240, "max_depth": 22, "min_samples_leaf": 3}),
        ("source_provided_flattened_features", "sklearn_hist_gradient_boosting", None, {"max_iter": 180, "learning_rate": 0.06, "max_leaf_nodes": 31, "min_samples_leaf": 20}),
        ("source_features_plus_structural_snapshot", "sklearn_hist_gradient_boosting", None, {"max_iter": 220, "learning_rate": 0.05, "max_leaf_nodes": 63, "min_samples_leaf": 20}),
    ]
    if effective_budget_tier == "competitive":
        base.extend(
            [
                ("source_provided_flattened_features", "sklearn_extra_trees", None, {"n_estimators": 360, "max_depth": None, "min_samples_leaf": 6}),
                ("source_features_plus_structural_snapshot", "sklearn_extra_trees", None, {"n_estimators": 360, "max_depth": None, "min_samples_leaf": 6}),
                ("source_features_plus_structural_snapshot", "sklearn_hist_gradient_boosting", None, {"max_iter": 300, "learning_rate": 0.035, "max_leaf_nodes": 63, "min_samples_leaf": 30}),
            ]
        )
    optional = [
        ("structural_same_snapshot_only", "lightgbm_classifier", "lightgbm", {"n_estimators": 220, "learning_rate": 0.04, "num_leaves": 31, "min_child_samples": 20}),
        ("source_provided_flattened_features", "lightgbm_classifier", "lightgbm", {"n_estimators": 260, "learning_rate": 0.04, "num_leaves": 31, "min_child_samples": 20}),
        ("source_features_plus_structural_snapshot", "lightgbm_classifier", "lightgbm", {"n_estimators": 260, "learning_rate": 0.04, "num_leaves": 31, "min_child_samples": 20}),
        ("source_features_plus_structural_snapshot", "xgboost_classifier", "xgboost", {"n_estimators": 260, "learning_rate": 0.04, "max_depth": 6, "min_child_weight": 3.0}),
    ]
    if effective_budget_tier == "competitive":
        optional.extend(
            [
                ("source_provided_flattened_features", "lightgbm_classifier", "lightgbm", {"n_estimators": 360, "learning_rate": 0.025, "num_leaves": 63, "min_child_samples": 30}),
                ("source_features_plus_structural_snapshot", "lightgbm_classifier", "lightgbm", {"n_estimators": 360, "learning_rate": 0.025, "num_leaves": 63, "min_child_samples": 30}),
                ("source_provided_flattened_features", "xgboost_classifier", "xgboost", {"n_estimators": 340, "learning_rate": 0.03, "max_depth": 7, "min_child_weight": 4.0}),
            ]
        )
    return base + optional


def _make_tabular_model(*, family_id: str, config: dict[str, Any]) -> tuple[Any, dict[str, Any]]:
    params = dict(config)
    if family_id == "sklearn_extra_trees":
        from sklearn.ensemble import ExtraTreesClassifier

        params.update({"class_weight": "balanced_subsample", "random_state": PAPER_GRAPH_RANDOM_SEED, "n_jobs": -1})
        return ExtraTreesClassifier(**params), {**params, "imbalance_fit_surface": "train_labels_only"}
    if family_id == "sklearn_hist_gradient_boosting":
        from sklearn.ensemble import HistGradientBoostingClassifier

        params.update({"class_weight": "balanced", "random_state": PAPER_GRAPH_RANDOM_SEED})
        return HistGradientBoostingClassifier(**params), {**params, "imbalance_fit_surface": "train_labels_only"}
    if family_id == "lightgbm_classifier":
        from lightgbm import LGBMClassifier

        params.update(
            {
                "class_weight": "balanced",
                "random_state": PAPER_GRAPH_RANDOM_SEED,
                "n_jobs": -1,
                "verbosity": -1,
                "subsample": 0.9,
                "colsample_bytree": 0.9,
            }
        )
        return LGBMClassifier(**params), {**params, "imbalance_fit_surface": "train_labels_only"}
    if family_id == "xgboost_classifier":
        from xgboost import XGBClassifier

        params.update(
            {
                "scale_pos_weight": 3.0,
                "random_state": PAPER_GRAPH_RANDOM_SEED,
                "n_jobs": -1,
                "tree_method": "hist",
                "eval_metric": "logloss",
                "objective": "binary:logistic",
                "subsample": 0.9,
                "colsample_bytree": 0.9,
            }
        )
        return XGBClassifier(**params), {**params, "imbalance_fit_surface": "train_labels_only"}
    raise ValueError(f"Unsupported P7 family: {family_id}")


def _predict_scores(model: Any, matrix: np.ndarray) -> np.ndarray:
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", message="X does not have valid feature names.*")
        return np.asarray(model.predict_proba(matrix)[:, 1], dtype=float)


def _calibrate_scores(
    *,
    validation_y: np.ndarray,
    validation_times: np.ndarray,
    validation_scores: np.ndarray,
    test_scores: np.ndarray,
) -> tuple[dict[str, Any], np.ndarray, np.ndarray, np.ndarray]:
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import log_loss

    midpoint = float(np.median(validation_times))
    calibration = np.flatnonzero(validation_times <= midpoint)
    operating = np.flatnonzero(validation_times > midpoint)
    if not (_has_two_classes(validation_y[calibration]) and _has_two_classes(validation_y[operating])):
        return (
            {
                "selected_method": "identity",
                "partition_policy": "identity_fallback_insufficient_temporal_validation_class_coverage",
                "test_used_for_selection": False,
                "model_selection_subset": _graph_validation_subset_summary(
                    validation_y,
                    validation_times,
                    np.arange(len(validation_y)),
                    purpose="full_validation_model_and_feature_view_selection",
                ),
                "calibration_subset": _graph_validation_subset_summary(
                    validation_y,
                    validation_times,
                    np.asarray([], dtype=int),
                    purpose="calibration_not_fitted",
                ),
                "threshold_selection_subset": _graph_validation_subset_summary(
                    validation_y,
                    validation_times,
                    np.arange(len(validation_y)),
                    purpose="identity_fallback_and_review_threshold_selection",
                ),
                "calibration_threshold_overlap_count": int(len(validation_y)),
            },
            validation_scores,
            test_scores,
            np.arange(len(validation_y)),
        )
    model = LogisticRegression(C=1.0, random_state=PAPER_GRAPH_RANDOM_SEED, solver="lbfgs")
    model.fit(_logit(validation_scores[calibration]).reshape(-1, 1), validation_y[calibration])
    identity_loss = log_loss(validation_y[operating], validation_scores[operating], labels=[0, 1])
    calibrated_validation = model.predict_proba(_logit(validation_scores).reshape(-1, 1))[:, 1]
    calibrated_test = model.predict_proba(_logit(test_scores).reshape(-1, 1))[:, 1]
    calibrated_loss = log_loss(validation_y[operating], calibrated_validation[operating], labels=[0, 1])
    use_calibrated = float(model.coef_[0][0]) > 0 and calibrated_loss < identity_loss
    return (
        {
            "selected_method": "platt_sigmoid" if use_calibrated else "identity",
            "partition_policy": "chronological_validation_calibration_then_operating_subwindows",
            "identity_operating_log_loss": _round_float(identity_loss),
            "platt_operating_log_loss": _round_float(calibrated_loss),
            "test_used_for_selection": False,
            "model_selection_subset": _graph_validation_subset_summary(
                validation_y,
                validation_times,
                np.arange(len(validation_y)),
                purpose="full_validation_model_and_feature_view_selection",
            ),
            "calibration_subset": _graph_validation_subset_summary(
                validation_y,
                validation_times,
                calibration,
                purpose="platt_calibration_fit",
            ),
            "threshold_selection_subset": _graph_validation_subset_summary(
                validation_y,
                validation_times,
                operating,
                purpose="calibration_comparison_and_review_threshold_selection",
            ),
            "calibration_threshold_overlap_count": int(len(np.intersect1d(calibration, operating))),
        },
        calibrated_validation if use_calibrated else validation_scores,
        calibrated_test if use_calibrated else test_scores,
        operating,
    )


def _graph_validation_subset_summary(
    labels: np.ndarray,
    time_steps: np.ndarray,
    indices: np.ndarray,
    *,
    purpose: str,
) -> dict[str, Any]:
    selected_times = time_steps[indices] if len(indices) else np.asarray([], dtype=time_steps.dtype)
    selected_labels = labels[indices] if len(indices) else np.asarray([], dtype=labels.dtype)
    return {
        "purpose": purpose,
        "node_count": int(len(indices)),
        "positive_count": int(selected_labels.sum()) if len(indices) else 0,
        "time_step_min": int(selected_times.min()) if len(indices) else None,
        "time_step_max": int(selected_times.max()) if len(indices) else None,
    }


def _build_graph_model_shadow_scorecard(
    *,
    graph_data: _GraphData,
    effective_budget_tier: str,
    run_optional: bool,
) -> dict[str, Any]:
    available = _module_available("torch") and _module_available("torch_geometric")
    base = {
        "schema_version": PAPER_GRAPH_SCHEMA_VERSION,
        "slice": "Paper Track P7",
        "status": "ok",
        "dataset_id": ELLIPTIC_DATASET_ID,
        "model_family": "pyg_graphsage",
        "model_claim_scope": "shadow_only_not_promoted_to_public_graph_model_claim",
        "protocol": "inductive_same_time_step_snapshot_edges_with_train_label_loss_only",
        "unknown_label_policy": "unknown_nodes_may_contribute_observable_features_and_topology_but_never_loss_or_metrics",
        "graph_neural_claim_allowed": False,
        "adapter_versions": {
            "torch": _module_version("torch"),
            "torch_geometric": _module_version("torch-geometric"),
        },
    }
    if not available:
        return {
            **base,
            "graph_model_execution_state": "fallback",
            "blocked_reason": "torch_or_torch_geometric_not_installed",
            "rows": [],
        }
    if not run_optional:
        return {
            **base,
            "graph_model_execution_state": "eligible_not_run",
            "blocked_reason": "optional_execution_not_requested",
            "rows": [],
        }
    started = perf_counter()
    try:
        row = _run_graphsage_shadow(graph_data=graph_data, effective_budget_tier=effective_budget_tier)
        return {
            **base,
            "graph_model_execution_state": "ran_shadow_only",
            "runtime_seconds": _round_float(perf_counter() - started),
            "rows": [row],
            "blocked_reason": "shadow_result_requires_repeated_seed_and_release_claim_gate_before_promotion",
        }
    except Exception as exc:
        return {
            **base,
            "graph_model_execution_state": "fallback",
            "runtime_seconds": _round_float(perf_counter() - started),
            "blocked_reason": f"graph_model_execution_failed: {exc}",
            "rows": [],
        }


def _run_graphsage_shadow(*, graph_data: _GraphData, effective_budget_tier: str) -> dict[str, Any]:
    import torch
    import torch.nn.functional as functional
    from torch_geometric.nn import SAGEConv

    torch.manual_seed(PAPER_GRAPH_RANDOM_SEED)
    combined = _feature_views(graph_data)["source_features_plus_structural_snapshot"]
    observed_train = combined[graph_data.times <= int(np.max(graph_data.times[graph_data.train_mask]))]
    mean = observed_train.mean(axis=0, keepdims=True)
    scale = observed_train.std(axis=0, keepdims=True)
    scale[scale < 1e-6] = 1.0
    values = (combined - mean) / scale
    features = torch.as_tensor(values, dtype=torch.float32)
    labels = torch.as_tensor(np.maximum(graph_data.labels, 0), dtype=torch.long)
    train_mask = torch.as_tensor(graph_data.train_mask, dtype=torch.bool)
    validation_mask = torch.as_tensor(graph_data.validation_mask, dtype=torch.bool)
    test_mask = torch.as_tensor(graph_data.test_mask, dtype=torch.bool)
    directed = graph_data.edge_index
    edge_index = torch.as_tensor(
        np.hstack([directed, directed[::-1]]),
        dtype=torch.long,
    )
    hidden_channels = 24 if effective_budget_tier == "smoke" else 64
    max_epochs = {"smoke": 8, "baseline": 45, "competitive": 90}[effective_budget_tier]
    patience = {"smoke": 3, "baseline": 10, "competitive": 16}[effective_budget_tier]

    class GraphSage(torch.nn.Module):
        def __init__(self) -> None:
            super().__init__()
            self.first = SAGEConv(features.shape[1], hidden_channels)
            self.second = SAGEConv(hidden_channels, hidden_channels)
            self.output = torch.nn.Linear(hidden_channels, 1)

        def forward(self) -> Any:
            hidden = functional.relu(self.first(features, edge_index))
            hidden = functional.dropout(hidden, p=0.2, training=self.training)
            hidden = functional.relu(self.second(hidden, edge_index))
            return self.output(hidden).squeeze(-1)

    model = GraphSage()
    positive_count = float(torch.sum(labels[train_mask] == 1).item())
    negative_count = float(torch.sum(labels[train_mask] == 0).item())
    weight = torch.tensor(max(1.0, negative_count / max(positive_count, 1.0)), dtype=torch.float32)
    optimizer = torch.optim.Adam(model.parameters(), lr=0.008, weight_decay=1e-4)
    best_state: dict[str, Any] | None = None
    best_pr_auc = -math.inf
    best_epoch = 0
    without_improvement = 0
    for epoch in range(1, max_epochs + 1):
        model.train()
        optimizer.zero_grad()
        logits = model()
        loss = functional.binary_cross_entropy_with_logits(
            logits[train_mask],
            labels[train_mask].float(),
            pos_weight=weight,
        )
        loss.backward()
        optimizer.step()
        model.eval()
        with torch.no_grad():
            validation_scores = torch.sigmoid(model()[validation_mask]).cpu().numpy()
        pr_auc = float(_binary_score_metrics(graph_data.labels[graph_data.validation_mask], validation_scores)["pr_auc"])
        if pr_auc > best_pr_auc + 1e-8:
            best_pr_auc = pr_auc
            best_epoch = epoch
            best_state = copy.deepcopy(model.state_dict())
            without_improvement = 0
        else:
            without_improvement += 1
        if without_improvement >= patience:
            break
    if best_state is None:
        raise RuntimeError("GraphSAGE did not complete one validation-scored epoch.")
    model.load_state_dict(best_state)
    model.eval()
    with torch.no_grad():
        scores = torch.sigmoid(model()).cpu().numpy()
    return {
        "family_id": "pyg_graphsage",
        "feature_view_id": "source_features_plus_structural_snapshot",
        "row_status": "blocked",
        "claim_role": "graph_model_shadow_only",
        "configuration": {
            "hidden_channels": hidden_channels,
            "max_epochs": max_epochs,
            "early_stopping_patience": patience,
            "selected_epoch": best_epoch,
            "optimizer": "adam",
            "learning_rate": 0.008,
            "weight_decay": 1e-4,
            "random_seed": PAPER_GRAPH_RANDOM_SEED,
            "class_weight_policy": "train_labeled_nodes_only",
        },
        "validation_metrics": _binary_score_metrics(
            graph_data.labels[graph_data.validation_mask],
            scores[graph_data.validation_mask],
        ),
        "test_metrics": _binary_score_metrics(
            graph_data.labels[graph_data.test_mask],
            scores[graph_data.test_mask],
        ),
        "test_evaluation_policy": "one_evaluation_after_validation_selected_epoch",
    }


def _build_feature_table(
    *,
    graph_data: _GraphData,
    baseline_rows: list[dict[str, Any]],
    selected: dict[str, Any] | None,
    view_selected_rows: list[dict[str, Any]],
    effective_budget_tier: str,
) -> dict[str, Any]:
    floor = baseline_rows[0]
    paired = {row["feature_view_id"]: row for row in view_selected_rows}
    flattened = paired.get("source_provided_flattened_features")
    augmented = paired.get("source_features_plus_structural_snapshot")
    incremental_test_delta = (
        float(augmented["test_pr_auc"]) - float(flattened["test_pr_auc"])
        if flattened is not None and augmented is not None
        else None
    )
    candidate_ready = bool(
        selected
        and effective_budget_tier == "competitive"
        and selected["feature_view_id"] == "source_features_plus_structural_snapshot"
        and float(selected["validation_pr_auc"]) > float(floor["validation_metrics"]["pr_auc"])
        and float(selected["test_pr_auc"]) > _positive_rate(graph_data.labels[graph_data.test_mask])
    )
    if selected is not None and candidate_ready:
        selected["row_status"] = "release-candidate"
    return {
        "schema_version": PAPER_GRAPH_SCHEMA_VERSION,
        "slice": "Paper Track P7",
        "status": "ok",
        "dataset_id": ELLIPTIC_DATASET_ID,
        "track_id": ELLIPTIC_TRACK_ID,
        "split_contract_id": ELLIPTIC_SPLIT_CONTRACT_ID,
        "feature_contract_id": PAPER_GRAPH_FEATURE_CONTRACT_ID,
        "effective_budget_tier": effective_budget_tier,
        "evaluation_protocol": "time_step_batch_snapshot_inductive_evaluation",
        "feature_views": [
            {
                "feature_view_id": "structural_same_snapshot_only",
                "feature_count": len(PAPER_GRAPH_STRUCTURAL_FEATURE_COLUMNS),
                "feature_columns": PAPER_GRAPH_STRUCTURAL_FEATURE_COLUMNS,
                "claim_scope": "relaytic_derived_label_free_graph_structure",
            },
            {
                "feature_view_id": "source_provided_flattened_features",
                "feature_count": graph_data.feature_value_count,
                "claim_scope": "source_provided_anonymized_local_and_one_hop_neighbor_aggregate_features_not_relabelled_as_relaytic_graph_engineering",
                "source_feature_boundary": "supplied_by_elliptic_not_reconstructed_by_relaytic",
            },
            {
                "feature_view_id": "source_features_plus_structural_snapshot",
                "feature_count": graph_data.feature_value_count + len(PAPER_GRAPH_STRUCTURAL_FEATURE_COLUMNS),
                "claim_scope": "source_features_augmented_with_relaytic_label_free_graph_structure",
            },
        ],
        "rows": baseline_rows,
        "predeclared_structural_floor": floor,
        "validation_selected_view_rows": view_selected_rows,
        "validation_selected_competitive_baseline": selected,
        "supporting_candidate_quality_check_passed": candidate_ready,
        "structural_incremental_test_pr_auc_delta_vs_source_features": _round_float(incremental_test_delta),
        "structural_incremental_test_lift_observed": bool(incremental_test_delta is not None and incremental_test_delta > 0),
        "incremental_claim_policy": "paired_test_rows_are_descriptive_only_and_never_override_validation_selected_promotion",
        "test_label_prevalence": _round_float(_positive_rate(graph_data.labels[graph_data.test_mask])),
    }


def _build_budget_contract(
    *,
    requested_budget_tier: str,
    effective_budget_tier: str,
    run_optional: bool,
    attempts: list[dict[str, Any]],
    shadow_scorecard: dict[str, Any],
) -> dict[str, Any]:
    return {
        "schema_version": PAPER_GRAPH_SCHEMA_VERSION,
        "slice": "Paper Track P7",
        "status": "ok",
        "requested_budget_tier": requested_budget_tier,
        "effective_budget_tier": effective_budget_tier,
        "budget_ladder": ["smoke", "baseline", "competitive", "release"],
        "optional_adapters_requested": run_optional,
        "validation_search_trial_count": sum(1 for row in attempts if row.get("stage") == "validation_search"),
        "successful_validation_trial_count": sum(
            1 for row in attempts if row.get("stage") == "validation_search" and row.get("execution_state") == "ran"
        ),
        "random_seeds": [PAPER_GRAPH_RANDOM_SEED],
        "split_policy": "chronological_time_step_windows_frozen_by_p5",
        "graph_observation_policy": "same_time_step_topology_observable_at_batch_snapshot_scoring_only",
        "test_evaluation_policy": "predeclared_structural_floor_plus_one_validation_selected_winner_per_predeclared_feature_view",
        "threshold_policy": "validation_operating_partition_only_then_fixed_test_application",
        "graph_model_shadow_policy": shadow_scorecard["model_claim_scope"],
        "release_budget_required_for_headline_claims": True,
    }


def _build_fallback_report(
    *,
    attempts: list[dict[str, Any]],
    shadow_scorecard: dict[str, Any],
    run_optional: bool,
) -> dict[str, Any]:
    fallback_rows = [
        {key: value for key, value in row.items() if key != "_model"}
        for row in attempts
        if row.get("execution_state") in {"fallback", "eligible_not_run"}
    ]
    return {
        "schema_version": PAPER_GRAPH_SCHEMA_VERSION,
        "slice": "Paper Track P7",
        "status": "ok",
        "optional_execution_requested": run_optional,
        "fallback_rows": fallback_rows,
        "graph_model_execution_state": shadow_scorecard["graph_model_execution_state"],
        "graph_model_blocked_reason": shadow_scorecard.get("blocked_reason"),
        "structural_floor_available_even_if_optional_models_fail": True,
    }


def _build_search_trace(
    *,
    attempts: list[dict[str, Any]],
    selected: dict[str, Any] | None,
    effective_budget_tier: str,
    shadow_scorecard: dict[str, Any],
) -> dict[str, Any]:
    public_attempts = [{key: value for key, value in row.items() if key not in {"_model", "_matrix"}} for row in attempts]
    return {
        "schema_version": PAPER_GRAPH_SCHEMA_VERSION,
        "slice": "Paper Track P7",
        "status": "ok",
        "effective_budget_tier": effective_budget_tier,
        "selection_metric": "validation_pr_auc",
        "attempts": public_attempts,
        "validation_selected_baseline": selected,
        "test_used_for_search_or_selection": False,
        "graph_model_shadow_execution_state": shadow_scorecard["graph_model_execution_state"],
        "graph_model_shadow_not_eligible_for_tabular_selection": True,
    }


def _build_publishability_gate(
    *,
    graph_data: _GraphData,
    feature_table: dict[str, Any],
    shadow_scorecard: dict[str, Any],
    effective_budget_tier: str,
) -> dict[str, Any]:
    candidate_allowed = bool(
        effective_budget_tier == "competitive"
        and graph_data.excluded_cross_step_edge_count == 0
        and feature_table["supporting_candidate_quality_check_passed"]
    )
    blocked = [
        "headline_graph_claim_requires_release_budget_and_repeated_seed_proof",
        "graph_sota_claim_not_benchmarked",
        "hard_aml_claim_requires_broader_holdout_and_operational_proof",
    ]
    if shadow_scorecard["graph_model_execution_state"] != "ran_shadow_only":
        blocked.append("graph_neural_shadow_candidate_not_run")
    else:
        blocked.append("graph_neural_shadow_candidate_not_promoted")
    if not candidate_allowed:
        blocked.append("supporting_graph_table_candidate_gate_not_passed")
    return {
        "schema_version": PAPER_GRAPH_SCHEMA_VERSION,
        "slice": "Paper Track P7",
        "status": "pass_supporting_only" if candidate_allowed else "blocked",
        "dataset_id": ELLIPTIC_DATASET_ID,
        "claim_posture": "supporting-only",
        "supporting_graph_table_candidate_allowed": candidate_allowed,
        "graph_benchmark_performance_claim_allowed": candidate_allowed,
        "structural_incremental_lift_claim_allowed": bool(
            candidate_allowed and feature_table["structural_incremental_test_lift_observed"]
        ),
        "graph_neural_model_claim_allowed": False,
        "headline_graph_claim_allowed": False,
        "graph_sota_claim_allowed": False,
        "paper_primary_claim_allowed": False,
        "hard_performance_claims_allowed": False,
        "same_time_step_topology_gate_passed": graph_data.excluded_cross_step_edge_count == 0,
        "blocked_reason_codes": blocked,
        "allowed_public_wording": (
            "Under the frozen chronological Elliptic split and same-time-step snapshot protocol, Relaytic produced "
            "a supporting source-feature-plus-structural baseline row. Its paired feature-view comparison does not "
            "establish an incremental structural-feature lift. This is not a graph-neural, SOTA, or real-world AML "
            "superiority claim."
            if candidate_allowed and not feature_table["structural_incremental_test_lift_observed"]
            else (
                "Under the frozen chronological Elliptic split and same-time-step snapshot protocol, Relaytic produced "
                "a supporting graph-feature baseline row with descriptive paired structural lift. This is not a "
                "graph-neural, SOTA, or real-world AML superiority claim."
                if candidate_allowed
                else None
            )
        ),
    }


def _build_manifest(
    *,
    root: Path,
    data_dir: Path,
    graph_data: _GraphData,
    feature_table: dict[str, Any],
    shadow_scorecard: dict[str, Any],
    budget_contract: dict[str, Any],
    gate: dict[str, Any],
) -> dict[str, Any]:
    selected = dict(feature_table.get("validation_selected_competitive_baseline", {}) or {})
    graph_shadow_state = str(shadow_scorecard.get("graph_model_execution_state") or "unknown")
    optional_skips = [] if graph_shadow_state == "ran_shadow_only" else [f"graph_shadow:{graph_shadow_state}"]
    source_files = [
        {
            "role": role,
            "path": _display_path(root, data_dir / filename),
            "size_bytes": (data_dir / filename).stat().st_size,
            "sha256": _sha256(data_dir / filename),
        }
        for role, filename in ELLIPTIC_REQUIRED_FILES.items()
    ]
    return {
        "schema_version": PAPER_GRAPH_SCHEMA_VERSION,
        "slice": "Paper Track P7",
        "status": "ok",
        "dataset_id": ELLIPTIC_DATASET_ID,
        "track_id": ELLIPTIC_TRACK_ID,
        "source_path": _display_path(root, data_dir),
        "source_files": source_files,
        "split_contract_id": ELLIPTIC_SPLIT_CONTRACT_ID,
        "feature_contract_id": PAPER_GRAPH_FEATURE_CONTRACT_ID,
        "node_count": graph_data.node_count,
        "raw_edge_count": graph_data.raw_edge_count,
        "same_step_edge_count": graph_data.same_step_edge_count,
        "excluded_cross_step_edge_count": graph_data.excluded_cross_step_edge_count,
        "official_feature_count": graph_data.feature_value_count,
        "structural_feature_count": len(PAPER_GRAPH_STRUCTURAL_FEATURE_COLUMNS),
        "effective_budget_tier": budget_contract["effective_budget_tier"],
        "selected_family_id": selected.get("family_id"),
        "selected_feature_view_id": selected.get("feature_view_id"),
        "selected_test_pr_auc": selected.get("test_pr_auc"),
        "graph_model_execution_state": shadow_scorecard["graph_model_execution_state"],
        "execution_status": {
            "status": "executed_with_optional_skips" if optional_skips else "executed",
            "requested_tier": budget_contract["requested_budget_tier"],
            "effective_tier": budget_contract["effective_budget_tier"],
            "dataset_execution": "completed_from_local_elliptic_bundle",
            "optional_adapter_execution_requested": budget_contract["optional_adapters_requested"],
            "optional_adapter_skips": optional_skips,
            "blocked_reason_codes": [],
        },
        "runtime_environment": {
            "python": platform.python_version(),
            "numpy": _module_version("numpy"),
            "pandas": _module_version("pandas"),
            "scikit_learn": _module_version("scikit-learn"),
        },
        "supporting_graph_table_candidate_allowed": gate["supporting_graph_table_candidate_allowed"],
        "headline_graph_claim_allowed": False,
        "hard_performance_claims_allowed": False,
        "output_files": PAPER_GRAPH_FILENAMES,
        "evidence_refs": {
            "p5_provenance": "docs/reports/elliptic_graph_provenance_report.json",
            "p5_temporal_split": "docs/reports/elliptic_temporal_split_report.json",
            "feature_table": "docs/reports/paper_graph_feature_table.json",
            "graph_model_shadow_scorecard": "docs/reports/paper_graph_model_shadow_scorecard.json",
            "publishability_gate": "docs/reports/paper_graph_publishability_gate.json",
        },
        "command": "relaytic release-safety graph-baselines --budget-tier competitive --run-optional --format json",
        "next_slice": "Paper Track P8",
        "summary": (
            "P7 evaluated source-provided Elliptic snapshot features and Relaytic-derived same-step structural graph "
            "features under a chronological protocol, with graph-neural candidates kept in a separate shadow scorecard."
        ),
    }


def _blocked_pack(
    *,
    root: Path,
    data_dir: Path,
    budget_tier: str,
    reason_code: str,
    reason: str,
) -> dict[str, Any]:
    base = {
        "schema_version": PAPER_GRAPH_SCHEMA_VERSION,
        "slice": "Paper Track P7",
        "status": "blocked",
        "dataset_id": ELLIPTIC_DATASET_ID,
        "source_path": _display_path(root, data_dir),
        "blocked_reason_codes": [reason_code],
        "summary": reason,
    }
    manifest = {
        **base,
        "requested_budget_tier": budget_tier,
        "execution_status": {
            "status": "blocked",
            "dataset_execution": "not_completed",
            "optional_adapter_execution_requested": False,
            "optional_adapter_skips": [],
            "blocked_reason_codes": [reason_code],
        },
        "supporting_graph_table_candidate_allowed": False,
        "headline_graph_claim_allowed": False,
        "hard_performance_claims_allowed": False,
        "recovery_instructions": [
            "Place the raw Elliptic classes, edge-list, and feature CSVs in data/paper_benchmarks/elliptic/.",
            "Run `relaytic release-safety elliptic-graph --format json` until P5 provenance and split checks pass.",
            "Regenerate P7 with `relaytic release-safety graph-baselines --budget-tier competitive --run-optional --format json`.",
        ],
        "next_slice": "Paper Track P7",
    }
    gate = {
        **base,
        "claim_posture": "blocked",
        "supporting_graph_table_candidate_allowed": False,
        "graph_benchmark_performance_claim_allowed": False,
        "graph_neural_model_claim_allowed": False,
        "headline_graph_claim_allowed": False,
        "graph_sota_claim_allowed": False,
        "paper_primary_claim_allowed": False,
        "hard_performance_claims_allowed": False,
    }
    return {
        "paper_graph_baseline_manifest": manifest,
        "paper_graph_feature_table": {**base, "rows": [], "validation_selected_competitive_baseline": None},
        "paper_graph_model_shadow_scorecard": {**base, "graph_model_execution_state": "blocked", "rows": []},
        "paper_graph_baseline_fallback_report": {**base, "fallback_rows": []},
        "paper_graph_budget_contract": {**base, "requested_budget_tier": budget_tier},
        "paper_graph_competitive_search_trace": {**base, "attempts": []},
        "paper_graph_publishability_gate": gate,
    }


def _evidence_type(feature_view_id: str) -> str:
    return {
        "structural_same_snapshot_only": "deterministic_label_free_structural_graph_features",
        "source_provided_flattened_features": "source_provided_anonymized_feature_snapshot",
        "source_features_plus_structural_snapshot": "source_features_augmented_with_structural_graph_features",
    }[feature_view_id]


def _has_class_coverage(graph_data: _GraphData) -> bool:
    return all(
        _has_two_classes(graph_data.labels[mask])
        for mask in [graph_data.train_mask, graph_data.validation_mask, graph_data.test_mask]
    )


def _has_two_classes(values: np.ndarray) -> bool:
    return len(set(np.asarray(values, dtype=int).tolist())) >= 2


def _positive_rate(values: np.ndarray) -> float:
    return float(np.mean(np.asarray(values, dtype=float))) if len(values) else 0.0


def _logit(values: np.ndarray) -> np.ndarray:
    clipped = np.clip(np.asarray(values, dtype=float), 1e-6, 1.0 - 1e-6)
    return np.log(clipped / (1.0 - clipped))


def _module_available(module: str) -> bool:
    return importlib.util.find_spec(module) is not None


def _module_version(package: str) -> str | None:
    try:
        return importlib_metadata.version(package)
    except importlib_metadata.PackageNotFoundError:
        return None


def _display_path(root: Path, path: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return str(path)


def _sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _round_float(value: float | None, digits: int = 6) -> float | None:
    if value is None or not math.isfinite(float(value)):
        return None
    return round(float(value), digits)
