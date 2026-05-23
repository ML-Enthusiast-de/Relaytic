"""Strong tabular baseline suite and publishability gate for Paper Track P6."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from importlib import metadata as importlib_metadata
import importlib.util
import json
from pathlib import Path
from time import perf_counter
from typing import Any, Callable
import warnings

import numpy as np
import pandas as pd

from relaytic.core.json_utils import write_json

from .paysim_benchmark import (
    FIXED_FPR_TARGET,
    PAYSIM_DEFAULT_DATA_PATH,
    PAYSIM_FORBIDDEN_MODEL_COLUMNS,
    SELECTED_REVIEW_BUDGET_FRACTION,
    _binary_score_metrics,
    _chronological_split,
    _load_paysim_frame,
    _split_row,
    _threshold_for_fpr,
    _threshold_for_review_fraction,
    _threshold_metrics,
)


PAPER_BASELINE_SCHEMA_VERSION = "relaytic.paper_tabular_baseline_suite.v1"
PAPER_BASELINE_REPORT_DIR = Path("docs") / "reports"
PAPER_BASELINE_FILENAMES = {
    "paper_baseline_suite_manifest": "paper_baseline_suite_manifest.json",
    "paper_baseline_version_matrix": "paper_baseline_version_matrix.json",
    "paper_tabular_baseline_table": "paper_tabular_baseline_table.json",
    "paper_baseline_fallback_report": "paper_baseline_fallback_report.json",
    "paper_benchmark_budget_contract": "paper_benchmark_budget_contract.json",
    "paper_competitive_search_trace": "paper_competitive_search_trace.json",
    "paper_leakage_safe_feature_report": "paper_leakage_safe_feature_report.json",
    "paper_publishability_gate": "paper_publishability_gate.json",
}
PAPER_BASELINE_DATASET_ID = "paysim_temporal_transaction_fraud"
PAPER_BASELINE_SPLIT_CONTRACT_ID = "split_paysim_chronological_step_v1"
PAPER_BASELINE_FEATURE_CONTRACT_ID = "p6_paysim_train_only_row_features_v1"
PAPER_BASELINE_ALLOWED_BUDGET_TIERS = {"smoke", "baseline"}

PAPER_BASELINE_FEATURE_COLUMNS = [
    "log1p_amount",
    "sqrt_amount",
    "log1p_amount_squared",
    "step_over_train_horizon",
    "type_CASH_IN",
    "type_CASH_OUT",
    "type_DEBIT",
    "type_PAYMENT",
    "type_TRANSFER",
    "risky_transfer_or_cashout",
    "log1p_amount_x_CASH_OUT",
    "log1p_amount_x_TRANSFER",
    "log1p_amount_x_PAYMENT",
    "amount_gt_train_p90",
    "amount_gt_train_p99",
    "amount_gt_train_p999",
]
PAYSIM_TYPES = ["CASH_IN", "CASH_OUT", "DEBIT", "PAYMENT", "TRANSFER"]


@dataclass(frozen=True)
class _FeatureState:
    train_max_step: int
    amount_p90: float
    amount_p99: float
    amount_p999: float


@dataclass(frozen=True)
class _PreparedData:
    x_train: np.ndarray
    x_validation: np.ndarray
    x_test: np.ndarray
    y_train: np.ndarray
    y_validation: np.ndarray
    y_test: np.ndarray
    feature_state: _FeatureState


def build_paper_baseline_suite_pack(
    project_root: str | Path,
    *,
    data_path: str | Path | None = None,
    budget_tier: str = "smoke",
    run_optional: bool = False,
) -> dict[str, Any]:
    """Build P6 baseline artifacts against one PaySim chronological split."""
    if budget_tier not in PAPER_BASELINE_ALLOWED_BUDGET_TIERS:
        raise ValueError("P6 supports only `smoke` or `baseline`; competitive execution belongs to Paper Track P6-A.")
    root = Path(project_root)
    resolved_data_path = Path(data_path) if data_path is not None else root / PAYSIM_DEFAULT_DATA_PATH
    if not resolved_data_path.is_absolute():
        resolved_data_path = root / resolved_data_path
    split_contracts = _read_json(root / "docs" / "reports" / "paper_split_contracts.json")
    claim_taxonomy = _read_json(root / "docs" / "reports" / "paper_claim_taxonomy.json")
    p4_result = _read_json(root / "docs" / "reports" / "paysim_paper_result_row.json")
    if not resolved_data_path.exists():
        return _blocked_pack(
            root=root,
            data_path=resolved_data_path,
            budget_tier=budget_tier,
            reason_code="p6_paysim_source_file_missing",
            reason=f"PaySim source file is missing at `{_display_path(root, resolved_data_path)}`.",
        )
    try:
        frame, header_columns = _load_paysim_frame(resolved_data_path)
        split = _chronological_split(frame)
        split_audit = _build_split_audit(
            root=root,
            data_path=resolved_data_path,
            header_columns=header_columns,
            split=split,
            frame=frame,
            split_contracts=split_contracts,
        )
        if split_audit["status"] != "ok":
            return _blocked_pack(
                root=root,
                data_path=resolved_data_path,
                budget_tier=budget_tier,
                reason_code="p6_split_or_leakage_contract_failed",
                reason=str(split_audit["summary"]),
                split_audit=split_audit,
            )
        effective_budget_tier = "smoke" if len(frame) < 10_000 else budget_tier
        prepared = _prepare_data(split)
        rows, attempts = _execute_baselines(
            prepared=prepared,
            split=split,
            effective_budget_tier=effective_budget_tier,
            run_optional=run_optional,
        )
    except Exception as exc:  # pragma: no cover - defensive CLI surface
        return _blocked_pack(
            root=root,
            data_path=resolved_data_path,
            budget_tier=budget_tier,
            reason_code="p6_baseline_suite_execution_failed",
            reason=f"Tabular baseline suite could not be constructed: {exc}",
        )

    version_matrix = _build_version_matrix(rows=rows, attempts=attempts)
    feature_report = _build_feature_report(
        root=root,
        data_path=resolved_data_path,
        split_audit=split_audit,
        prepared=prepared,
    )
    budget_contract = _build_budget_contract(
        requested_budget_tier=budget_tier,
        effective_budget_tier=effective_budget_tier,
        run_optional=run_optional,
        split_audit=split_audit,
    )
    baseline_table = _build_baseline_table(
        rows=rows,
        split_audit=split_audit,
        effective_budget_tier=effective_budget_tier,
        p4_result=p4_result,
    )
    fallback_report = _build_fallback_report(rows=rows, attempts=attempts, run_optional=run_optional)
    search_trace = _build_search_trace(
        rows=rows,
        attempts=attempts,
        effective_budget_tier=effective_budget_tier,
        run_optional=run_optional,
    )
    publishability_gate = _build_publishability_gate(
        baseline_table=baseline_table,
        feature_report=feature_report,
        effective_budget_tier=effective_budget_tier,
        claim_taxonomy=claim_taxonomy,
    )
    manifest = _build_manifest(
        root=root,
        data_path=resolved_data_path,
        budget_contract=budget_contract,
        baseline_table=baseline_table,
        fallback_report=fallback_report,
        feature_report=feature_report,
        publishability_gate=publishability_gate,
    )
    return {
        "paper_baseline_suite_manifest": manifest,
        "paper_baseline_version_matrix": version_matrix,
        "paper_tabular_baseline_table": baseline_table,
        "paper_baseline_fallback_report": fallback_report,
        "paper_benchmark_budget_contract": budget_contract,
        "paper_competitive_search_trace": search_trace,
        "paper_leakage_safe_feature_report": feature_report,
        "paper_publishability_gate": publishability_gate,
    }


def sync_paper_baseline_suite_pack(
    project_root: str | Path,
    *,
    data_path: str | Path | None = None,
    output_dir: str | Path | None = None,
    budget_tier: str = "smoke",
    run_optional: bool = False,
) -> dict[str, Path]:
    """Write P6 baseline-suite artifacts to docs/reports by default."""
    root = Path(project_root)
    report_dir = Path(output_dir) if output_dir is not None else root / PAPER_BASELINE_REPORT_DIR
    report_dir.mkdir(parents=True, exist_ok=True)
    artifacts = build_paper_baseline_suite_pack(
        root,
        data_path=data_path,
        budget_tier=budget_tier,
        run_optional=run_optional,
    )
    return {
        key: write_json(report_dir / filename, artifacts[key], indent=2, sort_keys=True)
        for key, filename in PAPER_BASELINE_FILENAMES.items()
    }


def render_paper_baseline_suite_markdown(pack: dict[str, Any]) -> str:
    manifest = dict(pack.get("paper_baseline_suite_manifest", {}))
    table = dict(pack.get("paper_tabular_baseline_table", {}))
    gate = dict(pack.get("paper_publishability_gate", {}))
    selected = dict(table.get("validation_selected_baseline", {}) or {})
    lines = [
        "# Paper Tabular Baseline Suite",
        "",
        f"- Status: `{manifest.get('status') or 'unknown'}`",
        f"- Effective budget tier: `{manifest.get('effective_budget_tier') or 'unknown'}`",
        f"- Executed families: `{manifest.get('executed_family_count') or 0}`",
        f"- Validation-selected baseline: `{selected.get('family_id') or 'none'}`",
        f"- Validation PR-AUC: `{selected.get('validation_pr_auc')}`",
        f"- Fixed test PR-AUC: `{selected.get('test_pr_auc')}`",
        f"- Headline performance allowed: `{gate.get('headline_performance_claim_allowed')}`",
        f"- Next slice: `{manifest.get('next_slice') or 'unknown'}`",
    ]
    blockers = [str(item) for item in gate.get("blocked_reason_codes", []) if str(item).strip()]
    if blockers:
        lines.extend(["", "## Publishability Blockers", *(f"- `{item}`" for item in blockers)])
    return "\n".join(lines).rstrip() + "\n"


def _prepare_data(split: Any) -> _PreparedData:
    train_amount = split.train["amount"].to_numpy(dtype="float64")
    feature_state = _FeatureState(
        train_max_step=max(1, int(split.train["step"].max())),
        amount_p90=float(np.quantile(train_amount, 0.90)),
        amount_p99=float(np.quantile(train_amount, 0.99)),
        amount_p999=float(np.quantile(train_amount, 0.999)),
    )
    return _PreparedData(
        x_train=_feature_matrix(split.train, feature_state=feature_state),
        x_validation=_feature_matrix(split.validation, feature_state=feature_state),
        x_test=_feature_matrix(split.test, feature_state=feature_state),
        y_train=split.train["isFraud"].to_numpy(dtype=int),
        y_validation=split.validation["isFraud"].to_numpy(dtype=int),
        y_test=split.test["isFraud"].to_numpy(dtype=int),
        feature_state=feature_state,
    )


def _feature_matrix(frame: pd.DataFrame, *, feature_state: _FeatureState) -> np.ndarray:
    amount = frame["amount"].to_numpy(dtype="float32")
    log_amount = np.log1p(np.maximum(amount, 0.0))
    sqrt_amount = np.sqrt(np.maximum(amount, 0.0))
    step_fraction = frame["step"].to_numpy(dtype="float32") / float(feature_state.train_max_step)
    type_values = frame["type"].astype(str).to_numpy()
    typed = [(type_values == item).astype("float32") for item in PAYSIM_TYPES]
    cash_out = typed[PAYSIM_TYPES.index("CASH_OUT")]
    transfer = typed[PAYSIM_TYPES.index("TRANSFER")]
    payment = typed[PAYSIM_TYPES.index("PAYMENT")]
    matrix = [
        log_amount,
        sqrt_amount,
        np.square(log_amount),
        step_fraction,
        *typed,
        np.maximum(cash_out, transfer),
        log_amount * cash_out,
        log_amount * transfer,
        log_amount * payment,
        (amount > feature_state.amount_p90).astype("float32"),
        (amount > feature_state.amount_p99).astype("float32"),
        (amount > feature_state.amount_p999).astype("float32"),
    ]
    return np.asarray(np.vstack(matrix).T, dtype="float32")


def _execute_baselines(
    *,
    prepared: _PreparedData,
    split: Any,
    effective_budget_tier: str,
    run_optional: bool,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    rows: list[dict[str, Any]] = []
    attempts: list[dict[str, Any]] = []
    imbalance_ratio = _safe_divide(float(np.sum(prepared.y_train == 0)), float(np.sum(prepared.y_train == 1)))

    def execute(
        family_id: str,
        role: str,
        fit_score: Callable[[], tuple[np.ndarray, np.ndarray, dict[str, Any]]],
        *,
        adapter_module: str | None = None,
    ) -> None:
        started = perf_counter()
        try:
            validation_scores, test_scores, config = fit_score()
            runtime = perf_counter() - started
            row = _build_metric_row(
                family_id=family_id,
                family_role=role,
                configuration=config,
                prepared=prepared,
                validation_scores=validation_scores,
                test_scores=test_scores,
                runtime_seconds=runtime,
                budget_tier=effective_budget_tier,
                adapter_module=adapter_module,
            )
            rows.append(row)
            attempts.append(
                {
                    "family_id": family_id,
                    "execution_state": "ran",
                    "runtime_seconds": _round_float(runtime),
                    "candidate_budget_tier": effective_budget_tier,
                    "configuration": config,
                }
            )
        except Exception as exc:
            attempts.append(
                {
                    "family_id": family_id,
                    "execution_state": "fallback",
                    "candidate_budget_tier": effective_budget_tier,
                    "blocked_reason": f"execution_failed: {exc}",
                }
            )

    execute(
        "deterministic_transfer_cashout_rule",
        "rules_reference",
        lambda: _score_rules(split=split, prepared=prepared),
    )
    execute(
        "sklearn_sgd_logistic",
        "linear_probability_reference",
        lambda: _score_sgd(prepared=prepared),
        adapter_module="scikit-learn",
    )
    execute(
        "sklearn_hist_gradient_boosting",
        "boosted_tree_reference",
        lambda: _score_hist_gradient_boosting(prepared=prepared, budget_tier=effective_budget_tier),
        adapter_module="scikit-learn",
    )
    execute(
        "sklearn_extra_trees",
        "tree_ensemble_reference",
        lambda: _score_extra_trees(prepared=prepared, budget_tier=effective_budget_tier),
        adapter_module="scikit-learn",
    )
    for family_id, module, role, scorer in [
        ("lightgbm_classifier", "lightgbm", "optional_boosted_tree_adapter", _score_lightgbm),
        ("xgboost_classifier", "xgboost", "optional_boosted_tree_adapter", _score_xgboost),
    ]:
        if not _module_available(module):
            attempts.append(
                {
                    "family_id": family_id,
                    "execution_state": "fallback",
                    "candidate_budget_tier": effective_budget_tier,
                    "blocked_reason": "optional_adapter_not_installed",
                }
            )
        elif not run_optional:
            attempts.append(
                {
                    "family_id": family_id,
                    "execution_state": "eligible_not_run",
                    "candidate_budget_tier": effective_budget_tier,
                    "blocked_reason": "optional_execution_not_requested",
                }
            )
        else:
            execute(
                family_id,
                role,
                lambda scorer=scorer: scorer(
                    prepared=prepared,
                    budget_tier=effective_budget_tier,
                    imbalance_ratio=imbalance_ratio,
                ),
                adapter_module=module,
            )
    for family_id, module in [("catboost_classifier", "catboost"), ("tabpfn_classifier", "tabpfn")]:
        attempts.append(
            {
                "family_id": family_id,
                "execution_state": "reserved" if _module_available(module) else "fallback",
                "candidate_budget_tier": "competitive",
                "blocked_reason": (
                    "reserved_for_p6_a_scale_and_budget_review"
                    if _module_available(module)
                    else "optional_adapter_not_installed"
                ),
            }
        )
    return rows, attempts


def _score_rules(*, split: Any, prepared: _PreparedData) -> tuple[np.ndarray, np.ndarray, dict[str, Any]]:
    del prepared

    def scores(frame: pd.DataFrame) -> np.ndarray:
        amount = frame["amount"].to_numpy(dtype="float64")
        log_amount = np.log1p(np.maximum(amount, 0.0))
        transfer = (frame["type"].astype(str).to_numpy() == "TRANSFER").astype(float)
        cash_out = (frame["type"].astype(str).to_numpy() == "CASH_OUT").astype(float)
        raw_score = log_amount + (2.0 * transfer) + cash_out
        return 1.0 / (1.0 + np.exp(-np.clip((raw_score - 8.0) / 2.0, -30.0, 30.0)))

    return scores(split.validation), scores(split.test), {
        "rule": "rank_by_fixed_sigmoid_of_log_amount_plus_transfer_cashout_flags",
        "fit_surface": "none",
        "threshold_surface": "validation_only",
    }


def _score_sgd(*, prepared: _PreparedData) -> tuple[np.ndarray, np.ndarray, dict[str, Any]]:
    from sklearn.linear_model import SGDClassifier
    from sklearn.preprocessing import StandardScaler

    scaler = StandardScaler()
    x_train = scaler.fit_transform(prepared.x_train)
    x_validation = scaler.transform(prepared.x_validation)
    x_test = scaler.transform(prepared.x_test)
    model = SGDClassifier(
        loss="log_loss",
        penalty="elasticnet",
        alpha=1e-5,
        l1_ratio=0.05,
        class_weight="balanced",
        random_state=42,
        max_iter=25,
        tol=1e-4,
        n_jobs=-1,
    )
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        model.fit(x_train, prepared.y_train)
    return model.predict_proba(x_validation)[:, 1], model.predict_proba(x_test)[:, 1], {
        "loss": "log_loss",
        "class_weight": "balanced_train_only",
        "scaling_fit_surface": "train_only",
        "random_state": 42,
        "max_iter": 25,
    }


def _score_hist_gradient_boosting(
    *,
    prepared: _PreparedData,
    budget_tier: str,
) -> tuple[np.ndarray, np.ndarray, dict[str, Any]]:
    from sklearn.ensemble import HistGradientBoostingClassifier

    params = {
        "max_iter": 100 if budget_tier == "baseline" else 30,
        "learning_rate": 0.08,
        "max_leaf_nodes": 31,
        "min_samples_leaf": 40 if budget_tier == "baseline" else 5,
        "l2_regularization": 1.0,
        "class_weight": "balanced",
        "random_state": 42,
    }
    model = HistGradientBoostingClassifier(**params)
    model.fit(prepared.x_train, prepared.y_train)
    return model.predict_proba(prepared.x_validation)[:, 1], model.predict_proba(prepared.x_test)[:, 1], {
        **params,
        "class_weight_fit_surface": "train_only",
    }


def _score_extra_trees(
    *,
    prepared: _PreparedData,
    budget_tier: str,
) -> tuple[np.ndarray, np.ndarray, dict[str, Any]]:
    from sklearn.ensemble import ExtraTreesClassifier

    params: dict[str, Any] = {
        "n_estimators": 96 if budget_tier == "baseline" else 32,
        "max_depth": 18 if budget_tier == "baseline" else 10,
        "min_samples_leaf": 8 if budget_tier == "baseline" else 2,
        "class_weight": "balanced_subsample",
        "max_samples": 0.25 if budget_tier == "baseline" else None,
        "bootstrap": budget_tier == "baseline",
        "random_state": 42,
        "n_jobs": -1,
    }
    model = ExtraTreesClassifier(**params)
    model.fit(prepared.x_train, prepared.y_train)
    return model.predict_proba(prepared.x_validation)[:, 1], model.predict_proba(prepared.x_test)[:, 1], {
        **params,
        "class_weight_fit_surface": "train_only",
        "sample_surface": "train_only",
    }


def _score_lightgbm(
    *,
    prepared: _PreparedData,
    budget_tier: str,
    imbalance_ratio: float,
) -> tuple[np.ndarray, np.ndarray, dict[str, Any]]:
    from lightgbm import LGBMClassifier

    params = {
        "n_estimators": 160 if budget_tier == "baseline" else 40,
        "learning_rate": 0.06,
        "num_leaves": 31,
        "min_child_samples": 40,
        "scale_pos_weight": float(imbalance_ratio),
        "random_state": 42,
        "n_jobs": -1,
        "verbosity": -1,
    }
    model = LGBMClassifier(**params)
    model.fit(prepared.x_train, prepared.y_train)
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", message="X does not have valid feature names.*")
        validation_scores = model.predict_proba(prepared.x_validation)[:, 1]
        test_scores = model.predict_proba(prepared.x_test)[:, 1]
    return validation_scores, test_scores, {
        **params,
        "scale_pos_weight_fit_surface": "train_only",
    }


def _score_xgboost(
    *,
    prepared: _PreparedData,
    budget_tier: str,
    imbalance_ratio: float,
) -> tuple[np.ndarray, np.ndarray, dict[str, Any]]:
    from xgboost import XGBClassifier

    params = {
        "n_estimators": 160 if budget_tier == "baseline" else 40,
        "max_depth": 6,
        "learning_rate": 0.06,
        "subsample": 0.9,
        "colsample_bytree": 0.9,
        "scale_pos_weight": float(imbalance_ratio),
        "tree_method": "hist",
        "eval_metric": "logloss",
        "objective": "binary:logistic",
        "random_state": 42,
        "n_jobs": -1,
    }
    model = XGBClassifier(**params)
    model.fit(prepared.x_train, prepared.y_train)
    return model.predict_proba(prepared.x_validation)[:, 1], model.predict_proba(prepared.x_test)[:, 1], {
        **params,
        "scale_pos_weight_fit_surface": "train_only",
    }


def _build_metric_row(
    *,
    family_id: str,
    family_role: str,
    configuration: dict[str, Any],
    prepared: _PreparedData,
    validation_scores: np.ndarray,
    test_scores: np.ndarray,
    runtime_seconds: float,
    budget_tier: str,
    adapter_module: str | None,
) -> dict[str, Any]:
    validation_metrics = _binary_score_metrics(prepared.y_validation, validation_scores)
    test_metrics = _binary_score_metrics(prepared.y_test, test_scores)
    threshold = _threshold_for_review_fraction(validation_scores, SELECTED_REVIEW_BUDGET_FRACTION)
    selected_validation = _threshold_metrics(
        prepared.y_validation,
        validation_scores,
        threshold=threshold,
        requested_fraction=SELECTED_REVIEW_BUDGET_FRACTION,
    )
    selected_test = _threshold_metrics(
        prepared.y_test,
        test_scores,
        threshold=threshold,
        requested_fraction=SELECTED_REVIEW_BUDGET_FRACTION,
    )
    fixed_fpr_threshold = _threshold_for_fpr(prepared.y_validation, validation_scores, target_fpr=FIXED_FPR_TARGET)
    fixed_fpr_test = _threshold_metrics(
        prepared.y_test,
        test_scores,
        threshold=fixed_fpr_threshold,
        requested_fraction=None,
    )
    return {
        "family_id": family_id,
        "family_role": family_role,
        "execution_state": "ran",
        "budget_tier": budget_tier,
        "adapter_module": adapter_module,
        "adapter_version": _module_version(adapter_module),
        "split_contract_id": PAPER_BASELINE_SPLIT_CONTRACT_ID,
        "feature_contract_id": PAPER_BASELINE_FEATURE_CONTRACT_ID,
        "threshold_selection_surface": "validation_only",
        "test_threshold_policy": "fixed_from_validation",
        "runtime_seconds": _round_float(runtime_seconds),
        "configuration": configuration,
        "validation_metrics": validation_metrics,
        "test_metrics": test_metrics,
        "selected_review_budget": {
            "review_budget_fraction": SELECTED_REVIEW_BUDGET_FRACTION,
            "validation_threshold": _round_float(threshold),
            "validation": selected_validation,
            "test": selected_test,
        },
        "fixed_fpr": {
            "target_fpr": FIXED_FPR_TARGET,
            "validation_threshold": _round_float(fixed_fpr_threshold),
            "test": fixed_fpr_test,
        },
        "paper_use": "baseline_only",
    }


def _build_split_audit(
    *,
    root: Path,
    data_path: Path,
    header_columns: list[str],
    split: Any,
    frame: pd.DataFrame,
    split_contracts: dict[str, Any],
) -> dict[str, Any]:
    split_rows = [_split_row("train", split.train), _split_row("validation", split.validation), _split_row("test", split.test)]
    forbidden_present = [column for column in PAYSIM_FORBIDDEN_MODEL_COLUMNS if column in header_columns]
    forbidden_used = [column for column in PAYSIM_FORBIDDEN_MODEL_COLUMNS if column in PAPER_BASELINE_FEATURE_COLUMNS]
    chronological_ok = (
        bool(len(split.train) and len(split.validation) and len(split.test))
        and int(split.train["step"].max()) < int(split.validation["step"].min())
        and int(split.validation["step"].max()) < int(split.test["step"].min())
    )
    class_ok = all(int(row["positive_count"]) > 0 and int(row["negative_count"]) > 0 for row in split_rows)
    status = "ok" if chronological_ok and class_ok and not forbidden_used else "blocked"
    return {
        "status": status,
        "dataset_id": PAPER_BASELINE_DATASET_ID,
        "source_path": _display_path(root, data_path),
        "source_sha256": _sha256(data_path),
        "row_count": int(len(frame)),
        "split_contract_id": PAPER_BASELINE_SPLIT_CONTRACT_ID,
        "split_contract": _find_split_contract(split_contracts),
        "split_rows": split_rows,
        "chronological_order_ok": chronological_ok,
        "class_coverage_ok": class_ok,
        "forbidden_source_columns_present_but_excluded": forbidden_present,
        "forbidden_model_columns_used": forbidden_used,
        "summary": (
            "P6 shares the frozen chronological PaySim split and excludes forbidden source fields from every model."
            if status == "ok"
            else "P6 cannot run until chronological, class-coverage, and forbidden-feature checks pass."
        ),
    }


def _build_version_matrix(*, rows: list[dict[str, Any]], attempts: list[dict[str, Any]]) -> dict[str, Any]:
    attempt_by_family = {str(row["family_id"]): row for row in attempts}
    executed_by_family = {str(row["family_id"]): row for row in rows}
    specs = [
        ("deterministic_transfer_cashout_rule", "in_core", False),
        ("sklearn_sgd_logistic", "scikit-learn", False),
        ("sklearn_hist_gradient_boosting", "scikit-learn", False),
        ("sklearn_extra_trees", "scikit-learn", False),
        ("lightgbm_classifier", "lightgbm", True),
        ("xgboost_classifier", "xgboost", True),
        ("catboost_classifier", "catboost", True),
        ("tabpfn_classifier", "tabpfn", True),
    ]
    matrix_rows = []
    for family_id, module, optional in specs:
        attempt = attempt_by_family.get(family_id, {})
        executed = executed_by_family.get(family_id, {})
        matrix_rows.append(
            {
                "family_id": family_id,
                "adapter_module": module,
                "optional_adapter": optional,
                "adapter_available": True if module == "in_core" else _module_available(module),
                "adapter_version": _module_version(module),
                "execution_state": executed.get("execution_state") or attempt.get("execution_state") or "not_attempted",
                "budget_tier": executed.get("budget_tier") or attempt.get("candidate_budget_tier"),
                "blocked_reason": attempt.get("blocked_reason"),
            }
        )
    return {
        "schema_version": PAPER_BASELINE_SCHEMA_VERSION,
        "slice": "Paper Track P6",
        "status": "ok",
        "rows": matrix_rows,
        "optional_available_count": sum(1 for row in matrix_rows if row["optional_adapter"] and row["adapter_available"]),
        "executed_family_count": len(rows),
        "summary": "Versions, adapter availability, execution state, and fallback state are explicit for each P6 baseline family.",
    }


def _build_feature_report(
    *,
    root: Path,
    data_path: Path,
    split_audit: dict[str, Any],
    prepared: _PreparedData,
) -> dict[str, Any]:
    return {
        "schema_version": PAPER_BASELINE_SCHEMA_VERSION,
        "slice": "Paper Track P6",
        "status": "pass" if split_audit["status"] == "ok" else "blocked",
        "dataset_id": PAPER_BASELINE_DATASET_ID,
        "source_path": _display_path(root, data_path),
        "split_contract_id": PAPER_BASELINE_SPLIT_CONTRACT_ID,
        "feature_contract_id": PAPER_BASELINE_FEATURE_CONTRACT_ID,
        "feature_columns": PAPER_BASELINE_FEATURE_COLUMNS,
        "allowed_source_fields": ["step", "type", "amount"],
        "forbidden_source_columns_present_but_excluded": split_audit["forbidden_source_columns_present_but_excluded"],
        "forbidden_model_columns_used": split_audit["forbidden_model_columns_used"],
        "feature_derivation_policy": "row_local_features_plus_train_only_amount_quantiles_and_train_only_time_scaling",
        "train_only_fit_state": {
            "train_max_step": prepared.feature_state.train_max_step,
            "amount_p90": _round_float(prepared.feature_state.amount_p90),
            "amount_p99": _round_float(prepared.feature_state.amount_p99),
            "amount_p999": _round_float(prepared.feature_state.amount_p999),
        },
        "entity_history_features_used": False,
        "balance_fields_used": False,
        "validation_or_test_fit_state_used": False,
        "imbalance_handling_policy": "class weights or scale_pos_weight are calculated from train labels only",
        "threshold_policy": "each model selects review and fixed-FPR thresholds on validation only and applies them unchanged to test",
        "competitive_expansion_reserved_for_p6_a": [
            "point_in_time_entity_history_features_if_audited",
            "calibration_and_threshold_search",
            "budgeted_hyperparameter_optimization",
        ],
        "summary": "P6 improves the conservative PaySim feature floor using train-only transforms while excluding forbidden balance and identifier fields.",
    }


def _build_budget_contract(
    *,
    requested_budget_tier: str,
    effective_budget_tier: str,
    run_optional: bool,
    split_audit: dict[str, Any],
) -> dict[str, Any]:
    return {
        "schema_version": PAPER_BASELINE_SCHEMA_VERSION,
        "slice": "Paper Track P6",
        "status": "frozen",
        "requested_budget_tier": requested_budget_tier,
        "effective_budget_tier": effective_budget_tier,
        "effective_budget_reason": (
            "small_dataset_is_smoke_only"
            if effective_budget_tier != requested_budget_tier
            else "requested_budget_supported_for_dataset_scope"
        ),
        "dataset_row_count": split_audit.get("row_count"),
        "optional_adapter_execution_requested": run_optional,
        "tiers": [
            {
                "budget_tier": "smoke",
                "purpose": "verify commands, artifacts, and gates on fixture-sized data",
                "publishable_performance_candidate": False,
            },
            {
                "budget_tier": "baseline",
                "purpose": "run clean conservative full-data reference families under one protocol",
                "publishable_performance_candidate": False,
            },
            {
                "budget_tier": "competitive",
                "purpose": "P6-A leakage-safe feature expansion, strong adapters, calibration, and recorded HPO",
                "publishable_performance_candidate": True,
                "execution_state": "reserved_for_p6_a",
            },
            {
                "budget_tier": "release",
                "purpose": "clean-clone reproduction, frozen configs, variance and claim lint before arXiv",
                "publishable_performance_candidate": True,
                "execution_state": "future_gate",
            },
        ],
        "summary": "P6 runs only smoke and baseline evidence; competitive promotion must be executed and audited in P6-A.",
    }


def _build_baseline_table(
    *,
    rows: list[dict[str, Any]],
    split_audit: dict[str, Any],
    effective_budget_tier: str,
    p4_result: dict[str, Any],
) -> dict[str, Any]:
    ran_rows = [row for row in rows if row.get("execution_state") == "ran"]
    selected = max(
        ran_rows,
        key=lambda row: float(row.get("validation_metrics", {}).get("pr_auc") or -1.0),
        default=None,
    )
    selected_summary = None
    if selected:
        selected_summary = {
            "family_id": selected["family_id"],
            "selection_surface": "validation_pr_auc_only",
            "validation_pr_auc": selected["validation_metrics"]["pr_auc"],
            "test_pr_auc": selected["test_metrics"]["pr_auc"],
            "test_precision_at_review_budget": selected["selected_review_budget"]["test"]["precision_at_k"],
            "test_recall_at_review_budget": selected["selected_review_budget"]["test"]["recall_at_review_budget"],
            "paper_use": "baseline_only",
        }
    return {
        "schema_version": PAPER_BASELINE_SCHEMA_VERSION,
        "slice": "Paper Track P6",
        "status": "ok" if len(ran_rows) >= 3 else "insufficient_executed_baselines",
        "dataset_id": PAPER_BASELINE_DATASET_ID,
        "split_contract_id": PAPER_BASELINE_SPLIT_CONTRACT_ID,
        "feature_contract_id": PAPER_BASELINE_FEATURE_CONTRACT_ID,
        "effective_budget_tier": effective_budget_tier,
        "comparison_metric": "pr_auc",
        "metric_contract": ["pr_auc", "precision_at_review_budget", "recall_at_review_budget", "fixed_fpr_recall"],
        "executed_family_count": len(ran_rows),
        "rows": rows,
        "validation_selected_baseline": selected_summary,
        "p4_reference_row": {
            "model_family": p4_result.get("model_family"),
            "test_pr_auc": dict(p4_result.get("metrics", {})).get("test_pr_auc"),
            "artifact_ref": "docs/reports/paysim_paper_result_row.json",
            "relationship": "same_split_contract_prior_conservative_feature_floor",
        }
        if p4_result
        else None,
        "headline_table_eligible": False,
        "headline_blocked_reason": "baseline_tier_is_not_a_competitive_or_release_budget",
        "summary": "P6 records clean comparable baseline rows; the validation-selected row remains baseline-only until P6-A executes competitive gates.",
    }


def _build_fallback_report(
    *,
    rows: list[dict[str, Any]],
    attempts: list[dict[str, Any]],
    run_optional: bool,
) -> dict[str, Any]:
    fallback_rows = [row for row in attempts if row.get("execution_state") != "ran"]
    return {
        "schema_version": PAPER_BASELINE_SCHEMA_VERSION,
        "slice": "Paper Track P6",
        "status": "ok",
        "optional_execution_requested": run_optional,
        "executed_family_ids": [row["family_id"] for row in rows],
        "fallback_rows": fallback_rows,
        "fallback_count": len(fallback_rows),
        "policy": "Optional adapters never disappear silently; unavailable, unrequested, failed, or P6-A-reserved candidates remain explicit.",
        "summary": f"P6 executed `{len(rows)}` family/families and recorded `{len(fallback_rows)}` explicit fallback or reservation state(s).",
    }


def _build_search_trace(
    *,
    rows: list[dict[str, Any]],
    attempts: list[dict[str, Any]],
    effective_budget_tier: str,
    run_optional: bool,
) -> dict[str, Any]:
    return {
        "schema_version": PAPER_BASELINE_SCHEMA_VERSION,
        "slice": "Paper Track P6",
        "status": "baseline_executed_competitive_reserved",
        "effective_budget_tier": effective_budget_tier,
        "optional_execution_requested": run_optional,
        "candidate_attempt_count": len(attempts),
        "executed_candidate_count": len(rows),
        "hpo_trial_count": 0,
        "random_seeds": [42],
        "attempts": attempts,
        "competitive_next_actions": [
            "Run P6-A on full PaySim with explicitly bounded HPO/search budgets.",
            "Audit additional point-in-time features before use; keep prohibited future/post-event fields excluded.",
            "Select calibration, model, and operating points on validation only before fixed test evaluation.",
        ],
        "summary": "P6 executes fixed baseline configurations only; competitive HPO/search is intentionally reserved for P6-A.",
    }


def _build_publishability_gate(
    *,
    baseline_table: dict[str, Any],
    feature_report: dict[str, Any],
    effective_budget_tier: str,
    claim_taxonomy: dict[str, Any],
) -> dict[str, Any]:
    split_clean = feature_report.get("status") == "pass"
    return {
        "schema_version": PAPER_BASELINE_SCHEMA_VERSION,
        "slice": "Paper Track P6",
        "status": "blocked",
        "dataset_id": PAPER_BASELINE_DATASET_ID,
        "claim_boundary_from_taxonomy": _claim_boundary("claim_paysim_temporal_transaction_fraud", claim_taxonomy),
        "effective_budget_tier": effective_budget_tier,
        "baseline_protocol_clean": split_clean,
        "baseline_family_minimum_met": int(baseline_table.get("executed_family_count", 0)) >= 3,
        "headline_performance_claim_allowed": False,
        "paper_primary_claim_allowed": False,
        "hard_performance_claims_allowed": False,
        "blocked_reason_codes": [
            "competitive_budget_not_executed_p6_a_required",
            "paysim_is_supporting_proxy_not_real_bank_holdout",
            "release_budget_and_clean_clone_proof_not_executed",
        ],
        "public_claim_wording": (
            "Relaytic runs a leakage-audited, chronological PaySim baseline suite with explicit budgets, "
            "adapter states, and validation-only threshold selection. These are supporting baseline results, "
            "not a headline AML or SOTA claim."
        ),
        "next_slice": "Paper Track P6-A",
        "summary": "P6 baseline evidence is useful and auditable, but promotion is blocked until a clean competitive rerun and later release proof pass.",
    }


def _build_manifest(
    *,
    root: Path,
    data_path: Path,
    budget_contract: dict[str, Any],
    baseline_table: dict[str, Any],
    fallback_report: dict[str, Any],
    feature_report: dict[str, Any],
    publishability_gate: dict[str, Any],
) -> dict[str, Any]:
    status = "ok" if baseline_table.get("status") == "ok" and feature_report.get("status") == "pass" else "blocked"
    return {
        "schema_version": PAPER_BASELINE_SCHEMA_VERSION,
        "slice": "Paper Track P6",
        "status": status,
        "dataset_id": PAPER_BASELINE_DATASET_ID,
        "source_path": _display_path(root, data_path),
        "split_contract_id": PAPER_BASELINE_SPLIT_CONTRACT_ID,
        "feature_contract_id": PAPER_BASELINE_FEATURE_CONTRACT_ID,
        "requested_budget_tier": budget_contract["requested_budget_tier"],
        "effective_budget_tier": budget_contract["effective_budget_tier"],
        "executed_family_count": baseline_table["executed_family_count"],
        "fallback_or_reservation_count": fallback_report["fallback_count"],
        "validation_selected_baseline": baseline_table.get("validation_selected_baseline"),
        "paper_primary_claim_allowed": False,
        "hard_performance_claims_allowed": False,
        "headline_performance_claim_allowed": publishability_gate["headline_performance_claim_allowed"],
        "output_files": PAPER_BASELINE_FILENAMES,
        "command": "relaytic release-safety tabular-baselines --budget-tier baseline --run-optional --format json",
        "next_slice": "Paper Track P6-A",
        "summary": "P6 tabular baseline suite completed under a shared chronological, leakage-audited metric contract; competitive promotion remains blocked for P6-A.",
    }


def _blocked_pack(
    *,
    root: Path,
    data_path: Path,
    budget_tier: str,
    reason_code: str,
    reason: str,
    split_audit: dict[str, Any] | None = None,
) -> dict[str, Any]:
    recovery = [
        "Materialize PaySim at data/paper_benchmarks/paysim/PS_20174392719_1491204439457_log.csv.",
        "Run relaytic release-safety tabular-baselines --budget-tier baseline --format json.",
        "Keep raw benchmark files out of git; commit only aggregate paper artifacts.",
    ]
    common = {
        "schema_version": PAPER_BASELINE_SCHEMA_VERSION,
        "slice": "Paper Track P6",
        "status": "blocked",
        "dataset_id": PAPER_BASELINE_DATASET_ID,
        "source_path": _display_path(root, data_path),
        "blocked_reason_codes": [reason_code],
        "recovery_instructions": recovery,
        "summary": reason,
    }
    return {
        "paper_baseline_suite_manifest": {
            **common,
            "requested_budget_tier": budget_tier,
            "paper_primary_claim_allowed": False,
            "hard_performance_claims_allowed": False,
            "headline_performance_claim_allowed": False,
            "output_files": PAPER_BASELINE_FILENAMES,
            "next_slice": "Paper Track P6 repair before Paper Track P6-A",
        },
        "paper_baseline_version_matrix": {**common, "rows": []},
        "paper_tabular_baseline_table": {
            **common,
            "split_audit": split_audit,
            "rows": [],
            "headline_table_eligible": False,
        },
        "paper_baseline_fallback_report": {**common, "fallback_rows": []},
        "paper_benchmark_budget_contract": {**common, "requested_budget_tier": budget_tier, "tiers": []},
        "paper_competitive_search_trace": {**common, "attempts": [], "hpo_trial_count": 0},
        "paper_leakage_safe_feature_report": {**common, "split_audit": split_audit, "forbidden_model_columns_used": []},
        "paper_publishability_gate": {
            **common,
            "headline_performance_claim_allowed": False,
            "paper_primary_claim_allowed": False,
            "hard_performance_claims_allowed": False,
        },
    }


def _module_available(module_name: str) -> bool:
    if module_name in {"in_core", "scikit-learn"}:
        return True
    return importlib.util.find_spec(module_name) is not None


def _module_version(module_name: str | None) -> str | None:
    if not module_name or module_name == "in_core":
        return None
    distribution = "scikit-learn" if module_name == "scikit-learn" else module_name
    try:
        return importlib_metadata.version(distribution)
    except importlib_metadata.PackageNotFoundError:
        return None


def _find_split_contract(split_contracts: dict[str, Any]) -> dict[str, Any]:
    for contract in split_contracts.get("contracts", []):
        if contract.get("split_contract_id") == PAPER_BASELINE_SPLIT_CONTRACT_ID:
            return dict(contract)
    return {"split_contract_id": PAPER_BASELINE_SPLIT_CONTRACT_ID, "split_type": "chronological_by_step"}


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
