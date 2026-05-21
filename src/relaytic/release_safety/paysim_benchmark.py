"""PaySim temporal benchmark runner for Paper Track P4."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
import math
from pathlib import Path
import warnings
from typing import Any

import numpy as np
import pandas as pd

from relaytic.core.json_utils import write_json


PAYSIM_BENCHMARK_SCHEMA_VERSION = "relaytic.paysim_temporal_benchmark.v1"
PAYSIM_BENCHMARK_REPORT_DIR = Path("docs") / "reports"
PAYSIM_DEFAULT_DATA_PATH = (
    Path("data")
    / "paper_benchmarks"
    / "paysim"
    / "PS_20174392719_1491204439457_log.csv"
)
PAYSIM_BENCHMARK_FILENAMES = {
    "paysim_benchmark_manifest": "paysim_benchmark_manifest.json",
    "paysim_temporal_split_report": "paysim_temporal_split_report.json",
    "paysim_operating_point_table": "paysim_operating_point_table.json",
    "paysim_paper_result_row": "paysim_paper_result_row.json",
}

MODEL_FEATURE_COLUMNS = [
    "log1p_amount",
    "sqrt_amount",
    "step_fraction",
    "type_CASH_IN",
    "type_CASH_OUT",
    "type_DEBIT",
    "type_PAYMENT",
    "type_TRANSFER",
    "log1p_amount_x_CASH_OUT",
    "log1p_amount_x_TRANSFER",
]
PAYSIM_TYPES = ["CASH_IN", "CASH_OUT", "DEBIT", "PAYMENT", "TRANSFER"]
PAYSIM_REQUIRED_COLUMNS = ["step", "type", "amount", "isFraud"]
PAYSIM_FORBIDDEN_MODEL_COLUMNS = [
    "oldbalanceOrg",
    "newbalanceOrig",
    "oldbalanceDest",
    "newbalanceDest",
    "nameOrig",
    "nameDest",
    "isFlaggedFraud",
]
REVIEW_BUDGET_FRACTIONS = [0.001, 0.002, 0.005, 0.01, 0.02]
SELECTED_REVIEW_BUDGET_FRACTION = 0.005
FIXED_FPR_TARGET = 0.001


@dataclass(frozen=True)
class _SplitFrames:
    train: pd.DataFrame
    validation: pd.DataFrame
    test: pd.DataFrame
    train_max_step: int
    validation_max_step: int


def build_paysim_benchmark_pack(
    project_root: str | Path,
    *,
    data_path: str | Path | None = None,
) -> dict[str, Any]:
    """Run or block the P4 PaySim benchmark and return paper artifacts."""
    root = Path(project_root)
    resolved_data_path = Path(data_path) if data_path is not None else root / PAYSIM_DEFAULT_DATA_PATH
    if not resolved_data_path.is_absolute():
        resolved_data_path = root / resolved_data_path
    registry = _read_json(root / "docs" / "reports" / "paper_dataset_registry.json")
    split_contracts = _read_json(root / "docs" / "reports" / "paper_split_contracts.json")
    claim_taxonomy = _read_json(root / "docs" / "reports" / "paper_claim_taxonomy.json")
    if not resolved_data_path.exists():
        return _blocked_pack(
            data_path=resolved_data_path,
            registry=registry,
            split_contracts=split_contracts,
            claim_taxonomy=claim_taxonomy,
            reason_code="paysim_source_file_missing",
            reason=(
                "PaySim source file is missing. Expected "
                f"`{_display_path(root, resolved_data_path)}`."
            ),
        )

    try:
        frame, header_columns = _load_paysim_frame(resolved_data_path)
    except Exception as exc:  # pragma: no cover - defensive surface
        return _blocked_pack(
            data_path=resolved_data_path,
            registry=registry,
            split_contracts=split_contracts,
            claim_taxonomy=claim_taxonomy,
            reason_code="paysim_source_load_failed",
            reason=f"PaySim source file could not be loaded: {exc}",
        )
    missing_columns = [column for column in PAYSIM_REQUIRED_COLUMNS if column not in frame.columns]
    if missing_columns:
        return _blocked_pack(
            data_path=resolved_data_path,
            registry=registry,
            split_contracts=split_contracts,
            claim_taxonomy=claim_taxonomy,
            reason_code="paysim_required_columns_missing",
            reason=f"PaySim source is missing required columns: {missing_columns}.",
        )
    split = _chronological_split(frame)
    split_report = _build_split_report(
        root=root,
        data_path=resolved_data_path,
        frame=frame,
        header_columns=header_columns,
        split=split,
        split_contracts=split_contracts,
    )
    if split_report["status"] != "ok":
        return _blocked_pack(
            data_path=resolved_data_path,
            registry=registry,
            split_contracts=split_contracts,
            claim_taxonomy=claim_taxonomy,
            reason_code="paysim_temporal_split_blocked",
            reason=str(split_report["summary"]),
            split_report=split_report,
        )
    try:
        model_payload = _fit_and_score_model(split)
    except Exception as exc:
        return _blocked_pack(
            data_path=resolved_data_path,
            registry=registry,
            split_contracts=split_contracts,
            claim_taxonomy=claim_taxonomy,
            reason_code="paysim_model_run_failed",
            reason=f"PaySim model run failed: {exc}",
            split_report=split_report,
        )
    operating_point_table = _build_operating_point_table(model_payload=model_payload)
    selected_row = dict(operating_point_table["selected_operating_point"])
    paper_result_row = _build_paper_result_row(
        root=root,
        data_path=resolved_data_path,
        split_report=split_report,
        operating_point_table=operating_point_table,
        model_payload=model_payload,
        claim_taxonomy=claim_taxonomy,
    )
    manifest = _build_manifest(
        root=root,
        data_path=resolved_data_path,
        registry=registry,
        split_report=split_report,
        operating_point_table=operating_point_table,
        model_payload=model_payload,
        selected_row=selected_row,
    )
    return {
        "paysim_benchmark_manifest": manifest,
        "paysim_temporal_split_report": split_report,
        "paysim_operating_point_table": operating_point_table,
        "paysim_paper_result_row": paper_result_row,
    }


def sync_paysim_benchmark_pack(
    project_root: str | Path,
    *,
    data_path: str | Path | None = None,
    output_dir: str | Path | None = None,
) -> dict[str, Path]:
    """Write the P4 PaySim benchmark artifacts to docs/reports by default."""
    root = Path(project_root)
    report_dir = Path(output_dir) if output_dir is not None else root / PAYSIM_BENCHMARK_REPORT_DIR
    report_dir.mkdir(parents=True, exist_ok=True)
    artifacts = build_paysim_benchmark_pack(root, data_path=data_path)
    return {
        key: write_json(report_dir / filename, artifacts[key], indent=2, sort_keys=True)
        for key, filename in PAYSIM_BENCHMARK_FILENAMES.items()
    }


def render_paysim_benchmark_markdown(pack: dict[str, Any]) -> str:
    manifest = dict(pack.get("paysim_benchmark_manifest", {}))
    split = dict(pack.get("paysim_temporal_split_report", {}))
    ops = dict(pack.get("paysim_operating_point_table", {}))
    row = dict(pack.get("paysim_paper_result_row", {}))
    selected = dict(ops.get("selected_operating_point", {}))
    metrics = dict(row.get("metrics", {}))
    lines = [
        "# PaySim Temporal Benchmark",
        "",
        f"- Status: `{manifest.get('status') or 'unknown'}`",
        f"- Claim posture: `{row.get('claim_posture') or 'unknown'}`",
        f"- Paper primary claim allowed: `{row.get('paper_primary_claim_allowed')}`",
        f"- Dataset rows: `{split.get('row_count') or 0}`",
        f"- Selected model: `{manifest.get('selected_model_family') or 'unknown'}`",
        f"- Selected review budget: `{selected.get('review_budget_fraction')}`",
        f"- Validation-selected threshold: `{selected.get('validation_threshold')}`",
        f"- Test PR-AUC: `{metrics.get('test_pr_auc')}`",
        f"- Test precision@budget: `{metrics.get('test_precision_at_review_budget')}`",
        f"- Test recall@budget: `{metrics.get('test_recall_at_review_budget')}`",
    ]
    blockers = [str(item) for item in manifest.get("blocked_reason_codes", []) if str(item).strip()]
    if blockers:
        lines.extend(["", "## Blockers", *(f"- `{item}`" for item in blockers)])
    return "\n".join(lines).rstrip() + "\n"


def _load_paysim_frame(path: Path) -> tuple[pd.DataFrame, list[str]]:
    header = pd.read_csv(path, nrows=0)
    header_columns = [str(column) for column in header.columns]
    frame = pd.read_csv(
        path,
        usecols=PAYSIM_REQUIRED_COLUMNS,
        dtype={"step": "int32", "type": "category", "amount": "float32", "isFraud": "int8"},
    )
    frame = frame.sort_values(["step"], kind="mergesort").reset_index(drop=True)
    frame["amount"] = frame["amount"].clip(lower=0)
    return frame, header_columns


def _chronological_split(frame: pd.DataFrame) -> _SplitFrames:
    unique_steps = np.sort(frame["step"].unique())
    if len(unique_steps) < 5:
        first_cut = max(1, int(math.floor(0.60 * len(frame))))
        second_cut = max(first_cut + 1, int(math.floor(0.80 * len(frame))))
        train = frame.iloc[:first_cut].reset_index(drop=True)
        validation = frame.iloc[first_cut:second_cut].reset_index(drop=True)
        test = frame.iloc[second_cut:].reset_index(drop=True)
        return _SplitFrames(
            train=train,
            validation=validation,
            test=test,
            train_max_step=int(train["step"].max()) if len(train) else 0,
            validation_max_step=int(validation["step"].max()) if len(validation) else 0,
        )
    train_index = max(0, int(math.floor(0.60 * len(unique_steps))) - 1)
    validation_index = max(train_index + 1, int(math.floor(0.80 * len(unique_steps))) - 1)
    validation_index = min(validation_index, len(unique_steps) - 2)
    train_max_step = int(unique_steps[train_index])
    validation_max_step = int(unique_steps[validation_index])
    train_mask = frame["step"] <= train_max_step
    validation_mask = (frame["step"] > train_max_step) & (frame["step"] <= validation_max_step)
    test_mask = frame["step"] > validation_max_step
    return _SplitFrames(
        train=frame.loc[train_mask].reset_index(drop=True),
        validation=frame.loc[validation_mask].reset_index(drop=True),
        test=frame.loc[test_mask].reset_index(drop=True),
        train_max_step=train_max_step,
        validation_max_step=validation_max_step,
    )


def _fit_and_score_model(split: _SplitFrames) -> dict[str, Any]:
    try:
        from sklearn.exceptions import ConvergenceWarning
        from sklearn.linear_model import SGDClassifier
        from sklearn.preprocessing import StandardScaler
    except Exception as exc:  # pragma: no cover - exercised only without full deps
        raise RuntimeError("scikit-learn is required for the PaySim benchmark runner") from exc

    max_step = max(
        int(split.train["step"].max()),
        int(split.validation["step"].max()),
        int(split.test["step"].max()),
        1,
    )
    x_train = _feature_matrix(split.train, max_step=max_step)
    x_validation = _feature_matrix(split.validation, max_step=max_step)
    x_test = _feature_matrix(split.test, max_step=max_step)
    y_train = split.train["isFraud"].to_numpy(dtype=int)
    y_validation = split.validation["isFraud"].to_numpy(dtype=int)
    y_test = split.test["isFraud"].to_numpy(dtype=int)
    if len(set(y_train.tolist())) < 2:
        raise RuntimeError("PaySim training split contains fewer than two target classes.")
    scaler = StandardScaler()
    x_train = scaler.fit_transform(x_train)
    x_validation = scaler.transform(x_validation)
    x_test = scaler.transform(x_test)
    model = SGDClassifier(
        loss="log_loss",
        penalty="elasticnet",
        alpha=1e-5,
        l1_ratio=0.05,
        class_weight="balanced",
        random_state=42,
        max_iter=20,
        tol=1e-4,
        n_jobs=-1,
    )
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=ConvergenceWarning)
        model.fit(x_train, y_train)
    validation_scores = model.predict_proba(x_validation)[:, 1]
    test_scores = model.predict_proba(x_test)[:, 1]
    return {
        "model_family": "sklearn_sgd_logistic_leakage_safe",
        "model_config": {
            "loss": "log_loss",
            "penalty": "elasticnet",
            "alpha": 1e-5,
            "l1_ratio": 0.05,
            "class_weight": "balanced",
            "random_state": 42,
            "max_iter": 20,
            "feature_policy": "leakage_safe_amount_type_step_only",
        },
        "feature_columns": MODEL_FEATURE_COLUMNS,
        "validation_scores": validation_scores,
        "test_scores": test_scores,
        "y_validation": y_validation,
        "y_test": y_test,
        "validation_metrics": _binary_score_metrics(y_validation, validation_scores),
        "test_metrics": _binary_score_metrics(y_test, test_scores),
    }


def _feature_matrix(frame: pd.DataFrame, *, max_step: int) -> np.ndarray:
    amount = frame["amount"].to_numpy(dtype="float64")
    log_amount = np.log1p(np.maximum(amount, 0.0))
    sqrt_amount = np.sqrt(np.maximum(amount, 0.0))
    step_fraction = frame["step"].to_numpy(dtype="float64") / max(float(max_step), 1.0)
    type_values = frame["type"].astype(str).to_numpy()
    type_features = [(type_values == item).astype(float) for item in PAYSIM_TYPES]
    cash_out = type_features[PAYSIM_TYPES.index("CASH_OUT")]
    transfer = type_features[PAYSIM_TYPES.index("TRANSFER")]
    matrix = [
        log_amount,
        sqrt_amount,
        step_fraction,
        *type_features,
        log_amount * cash_out,
        log_amount * transfer,
    ]
    return np.vstack(matrix).T


def _build_split_report(
    *,
    root: Path,
    data_path: Path,
    frame: pd.DataFrame,
    header_columns: list[str],
    split: _SplitFrames,
    split_contracts: dict[str, Any],
) -> dict[str, Any]:
    split_contract = _paysim_split_contract(split_contracts)
    split_rows = [
        _split_row("train", split.train),
        _split_row("validation", split.validation),
        _split_row("test", split.test),
    ]
    forbidden_present = [column for column in PAYSIM_FORBIDDEN_MODEL_COLUMNS if column in header_columns]
    forbidden_used = [column for column in PAYSIM_FORBIDDEN_MODEL_COLUMNS if column in MODEL_FEATURE_COLUMNS]
    chronological_ok = (
        bool(len(split.train) and len(split.validation) and len(split.test))
        and int(split.train["step"].max()) < int(split.validation["step"].min())
        and int(split.validation["step"].max()) < int(split.test["step"].min())
    )
    class_ok = all(int(row["positive_count"]) > 0 and int(row["negative_count"]) > 0 for row in split_rows)
    status = "ok" if chronological_ok and class_ok and not forbidden_used else "blocked"
    return {
        "schema_version": PAYSIM_BENCHMARK_SCHEMA_VERSION,
        "slice": "Paper Track P4",
        "status": status,
        "dataset_id": "paysim_temporal_transaction_fraud",
        "source_path": _display_path(root, data_path),
        "source_sha256": _sha256(data_path),
        "row_count": int(len(frame)),
        "step_min": int(frame["step"].min()),
        "step_max": int(frame["step"].max()),
        "unique_step_count": int(frame["step"].nunique()),
        "split_contract_id": "split_paysim_chronological_step_v1",
        "split_contract": split_contract,
        "split_rows": split_rows,
        "chronological_order_ok": chronological_ok,
        "class_coverage_ok": class_ok,
        "forbidden_source_columns_present": forbidden_present,
        "forbidden_model_columns_used": forbidden_used,
        "model_feature_columns": MODEL_FEATURE_COLUMNS,
        "forbidden_feature_check_passed": not forbidden_used,
        "rare_event_rate": _safe_divide(float(frame["isFraud"].sum()), float(len(frame))),
        "summary": (
            "PaySim was split chronologically by `step` into train/validation/test windows."
            if status == "ok"
            else "PaySim temporal split failed chronological, class-coverage, or forbidden-feature checks."
        ),
    }


def _build_operating_point_table(*, model_payload: dict[str, Any]) -> dict[str, Any]:
    y_validation = np.asarray(model_payload["y_validation"], dtype=int)
    y_test = np.asarray(model_payload["y_test"], dtype=int)
    validation_scores = np.asarray(model_payload["validation_scores"], dtype=float)
    test_scores = np.asarray(model_payload["test_scores"], dtype=float)
    rows = []
    for fraction in REVIEW_BUDGET_FRACTIONS:
        threshold = _threshold_for_review_fraction(validation_scores, fraction)
        validation_metrics = _threshold_metrics(
            y_validation,
            validation_scores,
            threshold=threshold,
            requested_fraction=fraction,
        )
        test_metrics = _threshold_metrics(
            y_test,
            test_scores,
            threshold=threshold,
            requested_fraction=fraction,
        )
        rows.append(
            {
                "review_budget_fraction": fraction,
                "validation_threshold": _round_float(threshold),
                "selection_surface": "validation_only",
                "test_threshold_policy": "fixed_from_validation",
                "validation": validation_metrics,
                "test": test_metrics,
            }
        )
    selected = next(
        row for row in rows if abs(float(row["review_budget_fraction"]) - SELECTED_REVIEW_BUDGET_FRACTION) < 1e-12
    )
    fixed_fpr_threshold = _threshold_for_fpr(y_validation, validation_scores, target_fpr=FIXED_FPR_TARGET)
    fixed_fpr_validation = _threshold_metrics(
        y_validation,
        validation_scores,
        threshold=fixed_fpr_threshold,
        requested_fraction=None,
    )
    fixed_fpr_test = _threshold_metrics(
        y_test,
        test_scores,
        threshold=fixed_fpr_threshold,
        requested_fraction=None,
    )
    drift = _threshold_drift(
        y_validation=y_validation,
        y_test=y_test,
        validation_scores=validation_scores,
        test_scores=test_scores,
        selected_threshold=float(selected["validation_threshold"]),
        selected_fraction=SELECTED_REVIEW_BUDGET_FRACTION,
    )
    return {
        "schema_version": PAYSIM_BENCHMARK_SCHEMA_VERSION,
        "slice": "Paper Track P4",
        "status": "ok",
        "dataset_id": "paysim_temporal_transaction_fraud",
        "model_family": model_payload["model_family"],
        "threshold_selection_rule": (
            "Choose thresholds on validation only by review-budget fraction; apply the selected threshold unchanged to test."
        ),
        "selected_review_budget_fraction": SELECTED_REVIEW_BUDGET_FRACTION,
        "selected_operating_point": selected,
        "review_budget_rows": rows,
        "fixed_fpr": {
            "target_fpr": FIXED_FPR_TARGET,
            "validation_threshold": _round_float(fixed_fpr_threshold),
            "selection_surface": "validation_only",
            "test_threshold_policy": "fixed_from_validation",
            "validation": fixed_fpr_validation,
            "test": fixed_fpr_test,
        },
        "threshold_drift_report": drift,
        "validation_score_metrics": model_payload["validation_metrics"],
        "test_score_metrics": model_payload["test_metrics"],
    }


def _build_paper_result_row(
    *,
    root: Path,
    data_path: Path,
    split_report: dict[str, Any],
    operating_point_table: dict[str, Any],
    model_payload: dict[str, Any],
    claim_taxonomy: dict[str, Any],
) -> dict[str, Any]:
    selected = dict(operating_point_table["selected_operating_point"])
    selected_validation = dict(selected["validation"])
    selected_test = dict(selected["test"])
    fixed_fpr = dict(operating_point_table["fixed_fpr"])
    fixed_fpr_test = dict(fixed_fpr["test"])
    claim_boundary = _claim_boundary("claim_paysim_temporal_transaction_fraud", claim_taxonomy)
    return {
        "schema_version": PAYSIM_BENCHMARK_SCHEMA_VERSION,
        "slice": "Paper Track P4",
        "status": "ok",
        "track_id": "paysim_temporal_transaction_fraud",
        "dataset_id": "paysim_temporal_transaction_fraud",
        "dataset_source_path": _display_path(root, data_path),
        "dataset_sha256": split_report["source_sha256"],
        "model_family": model_payload["model_family"],
        "claim_posture": "supporting-only",
        "claim_boundary_from_taxonomy": claim_boundary,
        "supporting_public_claim_allowed": claim_boundary == "supporting-only",
        "paper_primary_claim_allowed": False,
        "hard_performance_claims_allowed": False,
        "evidence_partition": "development_proxy",
        "metrics": {
            "validation_pr_auc": model_payload["validation_metrics"]["pr_auc"],
            "test_pr_auc": model_payload["test_metrics"]["pr_auc"],
            "validation_roc_auc": model_payload["validation_metrics"]["roc_auc"],
            "test_roc_auc": model_payload["test_metrics"]["roc_auc"],
            "review_budget_fraction": SELECTED_REVIEW_BUDGET_FRACTION,
            "validation_precision_at_review_budget": selected_validation["precision_at_k"],
            "test_precision_at_review_budget": selected_test["precision_at_k"],
            "validation_recall_at_review_budget": selected_validation["recall_at_review_budget"],
            "test_recall_at_review_budget": selected_test["recall_at_review_budget"],
            "fixed_fpr_target": FIXED_FPR_TARGET,
            "test_recall_at_fixed_fpr_threshold": fixed_fpr_test["recall_at_review_budget"],
            "test_fpr_at_fixed_validation_threshold": fixed_fpr_test["false_positive_rate"],
        },
        "artifact_refs": {
            "manifest": "docs/reports/paysim_benchmark_manifest.json",
            "split_report": "docs/reports/paysim_temporal_split_report.json",
            "operating_point_table": "docs/reports/paysim_operating_point_table.json",
            "paper_result_row": "docs/reports/paysim_paper_result_row.json",
            "claim_taxonomy": "docs/reports/paper_claim_taxonomy.json",
            "split_contracts": "docs/reports/paper_split_contracts.json",
        },
        "public_claim_wording": (
            "Relaytic-AML can run a PaySim-style chronological transaction-fraud benchmark and emit "
            "review-budget, temporal split, and claim-gated paper artifacts. This is supporting proxy evidence, "
            "not a hard real-world AML or SOTA superiority claim."
        ),
        "blocked_claims": [
            "hard_real_world_aml_superiority",
            "sota_aml_benchmark_winner",
            "real_bank_holdout_claim",
        ],
    }


def _build_manifest(
    *,
    root: Path,
    data_path: Path,
    registry: dict[str, Any],
    split_report: dict[str, Any],
    operating_point_table: dict[str, Any],
    model_payload: dict[str, Any],
    selected_row: dict[str, Any],
) -> dict[str, Any]:
    selected_test = dict(selected_row["test"])
    return {
        "schema_version": PAYSIM_BENCHMARK_SCHEMA_VERSION,
        "slice": "Paper Track P4",
        "status": "ok",
        "dataset_id": "paysim_temporal_transaction_fraud",
        "track_id": "paysim_temporal_transaction_fraud",
        "source_path": _display_path(root, data_path),
        "source_sha256": split_report["source_sha256"],
        "source_registry_ref": "docs/reports/paper_dataset_registry.json",
        "registry_status": registry.get("status"),
        "row_count": split_report["row_count"],
        "split_contract_id": split_report["split_contract_id"],
        "selected_model_family": model_payload["model_family"],
        "model_config": model_payload["model_config"],
        "model_feature_columns": model_payload["feature_columns"],
        "forbidden_feature_check_passed": split_report["forbidden_feature_check_passed"],
        "threshold_selection_surface": "validation_only",
        "selected_review_budget_fraction": SELECTED_REVIEW_BUDGET_FRACTION,
        "selected_validation_threshold": selected_row["validation_threshold"],
        "test_precision_at_review_budget": selected_test["precision_at_k"],
        "test_recall_at_review_budget": selected_test["recall_at_review_budget"],
        "test_pr_auc": model_payload["test_metrics"]["pr_auc"],
        "paper_claim_posture": "supporting-only",
        "paper_primary_claim_allowed": False,
        "hard_performance_claims_allowed": False,
        "output_files": PAYSIM_BENCHMARK_FILENAMES,
        "command": "relaytic release-safety paysim-benchmark --format json",
        "next_slice": "Paper Track P5",
        "summary": (
            "PaySim chronological benchmark completed with validation-only threshold tuning and fixed test evaluation."
        ),
        "blocked_reason_codes": [],
        "threshold_drift_state": operating_point_table["threshold_drift_report"]["drift_state"],
    }


def _blocked_pack(
    *,
    data_path: Path,
    registry: dict[str, Any],
    split_contracts: dict[str, Any],
    claim_taxonomy: dict[str, Any],
    reason_code: str,
    reason: str,
    split_report: dict[str, Any] | None = None,
) -> dict[str, Any]:
    manifest = {
        "schema_version": PAYSIM_BENCHMARK_SCHEMA_VERSION,
        "slice": "Paper Track P4",
        "status": "blocked",
        "dataset_id": "paysim_temporal_transaction_fraud",
        "track_id": "paysim_temporal_transaction_fraud",
        "source_path": str(data_path),
        "source_registry_ref": "docs/reports/paper_dataset_registry.json",
        "registry_status": registry.get("status"),
        "paper_claim_posture": "supporting-only",
        "paper_primary_claim_allowed": False,
        "hard_performance_claims_allowed": False,
        "blocked_reason_codes": [reason_code],
        "summary": reason,
        "output_files": PAYSIM_BENCHMARK_FILENAMES,
        "next_slice": "Paper Track P4 repair or Paper Track P5 after PaySim is unblocked",
    }
    split_payload = split_report or {
        "schema_version": PAYSIM_BENCHMARK_SCHEMA_VERSION,
        "slice": "Paper Track P4",
        "status": "blocked",
        "dataset_id": "paysim_temporal_transaction_fraud",
        "split_contract_id": "split_paysim_chronological_step_v1",
        "split_contract": _paysim_split_contract(split_contracts),
        "source_path": str(data_path),
        "blocked_reason_codes": [reason_code],
        "summary": reason,
    }
    operating_point_table = {
        "schema_version": PAYSIM_BENCHMARK_SCHEMA_VERSION,
        "slice": "Paper Track P4",
        "status": "blocked",
        "dataset_id": "paysim_temporal_transaction_fraud",
        "blocked_reason_codes": [reason_code],
        "summary": reason,
        "threshold_selection_rule": "unavailable_until_source_and_split_are_ready",
    }
    paper_result_row = {
        "schema_version": PAYSIM_BENCHMARK_SCHEMA_VERSION,
        "slice": "Paper Track P4",
        "status": "blocked",
        "track_id": "paysim_temporal_transaction_fraud",
        "dataset_id": "paysim_temporal_transaction_fraud",
        "claim_posture": "supporting-only",
        "claim_boundary_from_taxonomy": _claim_boundary("claim_paysim_temporal_transaction_fraud", claim_taxonomy),
        "supporting_public_claim_allowed": False,
        "paper_primary_claim_allowed": False,
        "hard_performance_claims_allowed": False,
        "blocked_reason_codes": [reason_code],
        "summary": reason,
    }
    return {
        "paysim_benchmark_manifest": manifest,
        "paysim_temporal_split_report": split_payload,
        "paysim_operating_point_table": operating_point_table,
        "paysim_paper_result_row": paper_result_row,
    }


def _split_row(split_name: str, frame: pd.DataFrame) -> dict[str, Any]:
    row_count = int(len(frame))
    positive_count = int(frame["isFraud"].sum()) if row_count else 0
    negative_count = row_count - positive_count
    return {
        "split": split_name,
        "row_count": row_count,
        "positive_count": positive_count,
        "negative_count": negative_count,
        "positive_rate": _round_float(_safe_divide(float(positive_count), float(row_count))),
        "step_min": int(frame["step"].min()) if row_count else None,
        "step_max": int(frame["step"].max()) if row_count else None,
    }


def _binary_score_metrics(y_true: np.ndarray, scores: np.ndarray) -> dict[str, Any]:
    try:
        from sklearn.metrics import average_precision_score, log_loss, roc_auc_score
    except Exception as exc:  # pragma: no cover - exercised only without full deps
        raise RuntimeError("scikit-learn is required for PaySim score metrics") from exc
    has_both = len(set(np.asarray(y_true, dtype=int).tolist())) == 2
    return {
        "n_samples": int(len(y_true)),
        "positive_count": int(np.sum(y_true == 1)),
        "positive_rate": _round_float(_safe_divide(float(np.sum(y_true == 1)), float(len(y_true)))),
        "pr_auc": _round_float(float(average_precision_score(y_true, scores))) if has_both else None,
        "roc_auc": _round_float(float(roc_auc_score(y_true, scores))) if has_both else None,
        "log_loss": _round_float(float(log_loss(y_true, scores, labels=[0, 1]))),
    }


def _threshold_metrics(
    y_true: np.ndarray,
    scores: np.ndarray,
    *,
    threshold: float,
    requested_fraction: float | None,
) -> dict[str, Any]:
    y = np.asarray(y_true, dtype=int)
    s = np.asarray(scores, dtype=float)
    selected = s >= float(threshold)
    reviewed = int(np.sum(selected))
    positives = int(np.sum(y == 1))
    negatives = int(np.sum(y == 0))
    true_positive = int(np.sum(selected & (y == 1)))
    false_positive = int(np.sum(selected & (y == 0)))
    precision = _safe_divide(float(true_positive), float(reviewed))
    recall = _safe_divide(float(true_positive), float(positives))
    fpr = _safe_divide(float(false_positive), float(negatives))
    return {
        "requested_review_fraction": requested_fraction,
        "reviewed_count": reviewed,
        "review_fraction": _round_float(_safe_divide(float(reviewed), float(len(y)))),
        "true_positive_count": true_positive,
        "false_positive_count": false_positive,
        "precision_at_k": _round_float(precision),
        "recall_at_review_budget": _round_float(recall),
        "false_positive_rate": _round_float(fpr),
    }


def _threshold_for_review_fraction(scores: np.ndarray, fraction: float) -> float:
    if len(scores) == 0:
        return 1.0
    k = max(1, int(math.ceil(float(fraction) * len(scores))))
    k = min(k, len(scores))
    return float(np.partition(np.asarray(scores, dtype=float), -k)[-k])


def _threshold_for_fpr(y_true: np.ndarray, scores: np.ndarray, *, target_fpr: float) -> float:
    negatives = np.asarray(scores, dtype=float)[np.asarray(y_true, dtype=int) == 0]
    if len(negatives) == 0:
        return 1.0
    false_positive_budget = max(1, int(math.floor(float(target_fpr) * len(negatives))))
    false_positive_budget = min(false_positive_budget, len(negatives))
    return float(np.partition(negatives, -false_positive_budget)[-false_positive_budget])


def _threshold_drift(
    *,
    y_validation: np.ndarray,
    y_test: np.ndarray,
    validation_scores: np.ndarray,
    test_scores: np.ndarray,
    selected_threshold: float,
    selected_fraction: float,
) -> dict[str, Any]:
    test_equivalent_threshold = _threshold_for_review_fraction(test_scores, selected_fraction)
    validation_alert_rate = _safe_divide(
        float(np.sum(validation_scores >= selected_threshold)),
        float(len(validation_scores)),
    )
    test_alert_rate = _safe_divide(float(np.sum(test_scores >= selected_threshold)), float(len(test_scores)))
    validation_positive_rate = _safe_divide(float(np.sum(y_validation == 1)), float(len(y_validation)))
    test_positive_rate = _safe_divide(float(np.sum(y_test == 1)), float(len(y_test)))
    threshold_delta = float(test_equivalent_threshold - selected_threshold)
    alert_delta = float(test_alert_rate - validation_alert_rate)
    drift_level = "low"
    if abs(alert_delta) > 0.01 or abs(threshold_delta) > 0.1:
        drift_level = "watch"
    if abs(alert_delta) > 0.03 or abs(threshold_delta) > 0.25:
        drift_level = "high"
    return {
        "drift_state": drift_level,
        "selected_validation_threshold": _round_float(selected_threshold),
        "test_threshold_for_same_review_fraction": _round_float(test_equivalent_threshold),
        "threshold_delta_test_equivalent_minus_validation": _round_float(threshold_delta),
        "validation_alert_rate_at_selected_threshold": _round_float(validation_alert_rate),
        "test_alert_rate_at_selected_threshold": _round_float(test_alert_rate),
        "alert_rate_delta_test_minus_validation": _round_float(alert_delta),
        "validation_positive_rate": _round_float(validation_positive_rate),
        "test_positive_rate": _round_float(test_positive_rate),
        "positive_rate_delta_test_minus_validation": _round_float(test_positive_rate - validation_positive_rate),
    }


def _paysim_split_contract(split_contracts: dict[str, Any]) -> dict[str, Any]:
    for contract in split_contracts.get("contracts", []):
        if contract.get("split_contract_id") == "split_paysim_chronological_step_v1":
            return dict(contract)
    return {
        "split_contract_id": "split_paysim_chronological_step_v1",
        "split_type": "chronological_by_step",
        "forbidden_split_methods": ["random_row_shuffle", "stratified_random_without_time"],
        "forbidden_feature_fields": PAYSIM_FORBIDDEN_MODEL_COLUMNS[:4],
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
        return str(path)


def _safe_divide(numerator: float, denominator: float) -> float:
    if abs(denominator) <= 1e-12:
        return 0.0
    return float(numerator / denominator)


def _round_float(value: float | None, digits: int = 6) -> float | None:
    if value is None:
        return None
    value = float(value)
    if not math.isfinite(value):
        return None
    return round(value, digits)
