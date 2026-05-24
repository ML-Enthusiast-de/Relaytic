"""Competitive, claim-gated PaySim rerun for Paper Track P6-A."""

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
    _split_row,
    _threshold_for_fpr,
    _threshold_for_review_fraction,
    _threshold_metrics,
)


PAYSIM_COMPETITIVE_SCHEMA_VERSION = "relaytic.paysim_competitive_benchmark.v1"
PAYSIM_COMPETITIVE_REPORT_DIR = Path("docs") / "reports"
PAYSIM_COMPETITIVE_FILENAMES = {
    "paysim_competitive_benchmark_manifest": "paysim_competitive_benchmark_manifest.json",
    "paysim_competitive_budget_contract": "paysim_competitive_budget_contract.json",
    "paysim_competitive_search_trace": "paysim_competitive_search_trace.json",
    "paysim_leakage_safe_feature_report": "paysim_leakage_safe_feature_report.json",
    "paysim_competitive_baseline_table": "paysim_competitive_baseline_table.json",
    "paysim_publishability_gate": "paysim_publishability_gate.json",
}
PAYSIM_COMPETITIVE_DATASET_ID = "paysim_temporal_transaction_fraud"
PAYSIM_COMPETITIVE_SPLIT_CONTRACT_ID = "split_paysim_chronological_step_v1"
PAYSIM_COMPETITIVE_FEATURE_CONTRACT_ID = "p6a_paysim_point_in_time_destination_history_v1"
PAYSIM_COMPETITIVE_ALLOWED_BUDGET_TIERS = {"smoke", "competitive"}
PAYSIM_COMPETITIVE_REQUIRED_COLUMNS = ["step", "type", "amount", "nameOrig", "nameDest", "isFraud"]
PAYSIM_COMPETITIVE_RANDOM_SEEDS = [42]
PAYSIM_COMPETITIVE_PROBE_MAX_TRAIN_ROWS = 750_000
PAYSIM_COMPETITIVE_FEATURE_COLUMNS = [
    "log1p_amount",
    "sqrt_amount",
    "log1p_amount_squared",
    "step_over_train_horizon",
    "hour_of_day_sin",
    "hour_of_day_cos",
    "day_of_week_sin",
    "day_of_week_cos",
    "type_CASH_IN",
    "type_CASH_OUT",
    "type_DEBIT",
    "type_PAYMENT",
    "type_TRANSFER",
    "risky_transfer_or_cashout",
    "log1p_amount_x_CASH_OUT",
    "log1p_amount_x_TRANSFER",
    "amount_gt_train_p90",
    "amount_gt_train_p99",
    "amount_gt_train_p999",
    "destination_unseen_before_step",
    "log1p_destination_prior_transaction_count",
    "log1p_destination_prior_amount_sum",
    "destination_prior_risky_fraction",
    "destination_prior_transfer_fraction",
    "destination_prior_cashout_fraction",
    "amount_vs_destination_prior_mean",
]
_PAYSIM_TYPES = ["CASH_IN", "CASH_OUT", "DEBIT", "PAYMENT", "TRANSFER"]


@dataclass(frozen=True)
class _CompetitiveFeatureState:
    train_max_step: int
    amount_p90: float
    amount_p99: float
    amount_p999: float


@dataclass(frozen=True)
class _CompetitivePreparedData:
    x_train: np.ndarray
    x_validation: np.ndarray
    x_test: np.ndarray
    y_train: np.ndarray
    y_validation: np.ndarray
    y_test: np.ndarray
    validation_steps: np.ndarray
    feature_state: _CompetitiveFeatureState


def build_paysim_competitive_pack(
    project_root: str | Path,
    *,
    data_path: str | Path | None = None,
    budget_tier: str = "smoke",
    run_optional: bool = False,
) -> dict[str, Any]:
    """Build the P6-A competitive rerun artifacts under one untouched-test contract."""
    if budget_tier not in PAYSIM_COMPETITIVE_ALLOWED_BUDGET_TIERS:
        raise ValueError("P6-A supports only `smoke` or `competitive`; release proof belongs to Paper Track P12.")
    root = Path(project_root)
    resolved_data_path = Path(data_path) if data_path is not None else root / PAYSIM_DEFAULT_DATA_PATH
    if not resolved_data_path.is_absolute():
        resolved_data_path = root / resolved_data_path
    claim_taxonomy = _read_json(root / "docs" / "reports" / "paper_claim_taxonomy.json")
    p4_row = _read_json(root / "docs" / "reports" / "paysim_paper_result_row.json")
    p6_manifest = _read_json(root / "docs" / "reports" / "paper_baseline_suite_manifest.json")
    p6_table = _read_json(root / "docs" / "reports" / "paper_tabular_baseline_table.json")
    if not resolved_data_path.exists():
        return _blocked_pack(
            root=root,
            data_path=resolved_data_path,
            budget_tier=budget_tier,
            reason_code="p6a_paysim_source_file_missing",
            reason=f"PaySim source file is missing at `{_display_path(root, resolved_data_path)}`.",
        )
    try:
        frame, header_columns = _load_competitive_frame(resolved_data_path)
        split = _chronological_split(frame)
        split_audit = _build_split_audit(
            root=root,
            data_path=resolved_data_path,
            frame=frame,
            split=split,
            header_columns=header_columns,
        )
        if split_audit["status"] != "ok":
            return _blocked_pack(
                root=root,
                data_path=resolved_data_path,
                budget_tier=budget_tier,
                reason_code="p6a_split_or_leakage_contract_failed",
                reason=str(split_audit["summary"]),
                split_audit=split_audit,
            )
        effective_budget_tier = "smoke" if len(frame) < 10_000 else budget_tier
        prepared = _prepare_data(split)
        candidate_rows, trace_payload = _run_search(
            prepared=prepared,
            split=split,
            effective_budget_tier=effective_budget_tier,
            run_optional=run_optional,
        )
    except Exception as exc:  # pragma: no cover - defensive command boundary
        return _blocked_pack(
            root=root,
            data_path=resolved_data_path,
            budget_tier=budget_tier,
            reason_code="p6a_competitive_execution_failed",
            reason=f"Competitive PaySim rerun could not be constructed: {exc}",
        )

    source_sha256 = split_audit["source_sha256"]
    baseline_linked = _p6_baseline_matches_source(
        source_sha256=source_sha256,
        p4_row=p4_row,
        p6_manifest=p6_manifest,
    )
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
        trace_payload=trace_payload,
    )
    table = _build_baseline_table(
        candidate_rows=candidate_rows,
        trace_payload=trace_payload,
        effective_budget_tier=effective_budget_tier,
        source_sha256=source_sha256,
        baseline_linked=baseline_linked,
        p4_row=p4_row,
        p6_table=p6_table,
    )
    search_trace = _build_search_trace(
        trace_payload=trace_payload,
        effective_budget_tier=effective_budget_tier,
        run_optional=run_optional,
    )
    gate = _build_publishability_gate(
        table=table,
        feature_report=feature_report,
        budget_contract=budget_contract,
        baseline_linked=baseline_linked,
        claim_taxonomy=claim_taxonomy,
    )
    manifest = _build_manifest(
        root=root,
        data_path=resolved_data_path,
        table=table,
        budget_contract=budget_contract,
        gate=gate,
    )
    return {
        "paysim_competitive_benchmark_manifest": manifest,
        "paysim_competitive_budget_contract": budget_contract,
        "paysim_competitive_search_trace": search_trace,
        "paysim_leakage_safe_feature_report": feature_report,
        "paysim_competitive_baseline_table": table,
        "paysim_publishability_gate": gate,
    }


def sync_paysim_competitive_pack(
    project_root: str | Path,
    *,
    data_path: str | Path | None = None,
    output_dir: str | Path | None = None,
    budget_tier: str = "smoke",
    run_optional: bool = False,
) -> dict[str, Path]:
    """Write P6-A artifacts to ``docs/reports`` by default."""
    root = Path(project_root)
    report_dir = Path(output_dir) if output_dir is not None else root / PAYSIM_COMPETITIVE_REPORT_DIR
    report_dir.mkdir(parents=True, exist_ok=True)
    artifacts = build_paysim_competitive_pack(
        root,
        data_path=data_path,
        budget_tier=budget_tier,
        run_optional=run_optional,
    )
    return {
        key: write_json(report_dir / filename, artifacts[key], indent=2, sort_keys=True)
        for key, filename in PAYSIM_COMPETITIVE_FILENAMES.items()
    }


def render_paysim_competitive_markdown(pack: dict[str, Any]) -> str:
    manifest = dict(pack.get("paysim_competitive_benchmark_manifest", {}))
    table = dict(pack.get("paysim_competitive_baseline_table", {}))
    gate = dict(pack.get("paysim_publishability_gate", {}))
    selected = dict(table.get("validation_selected_competitive_model", {}) or {})
    return "\n".join(
        [
            "# PaySim Competitive Rerun",
            "",
            f"- Status: `{manifest.get('status') or 'unknown'}`",
            f"- Effective budget tier: `{manifest.get('effective_budget_tier') or 'unknown'}`",
            f"- Search trials: `{manifest.get('hpo_trial_count') or 0}`",
            f"- Finalist families: `{manifest.get('finalist_family_count') or 0}`",
            f"- Validation-selected model: `{selected.get('family_id') or 'none'}`",
            f"- Validation PR-AUC: `{selected.get('validation_pr_auc')}`",
            f"- Fixed test PR-AUC: `{selected.get('test_pr_auc')}`",
            f"- Supporting paper-table candidate: `{gate.get('supporting_paper_table_candidate_allowed')}`",
            f"- Headline performance allowed: `{gate.get('headline_performance_claim_allowed')}`",
            f"- Next slice: `{manifest.get('next_slice') or 'unknown'}`",
        ]
    ).rstrip() + "\n"


def _load_competitive_frame(path: Path) -> tuple[pd.DataFrame, list[str]]:
    header = pd.read_csv(path, nrows=0)
    header_columns = [str(column) for column in header.columns]
    missing = [column for column in PAYSIM_COMPETITIVE_REQUIRED_COLUMNS if column not in header_columns]
    if missing:
        raise ValueError(f"Required point-in-time feature columns are missing: {missing}.")
    frame = pd.read_csv(
        path,
        usecols=PAYSIM_COMPETITIVE_REQUIRED_COLUMNS,
        dtype={
            "step": "int32",
            "type": "category",
            "amount": "float32",
            "nameOrig": "category",
            "nameDest": "category",
            "isFraud": "int8",
        },
    )
    frame = frame.sort_values(["step"], kind="mergesort").reset_index(drop=True)
    frame["amount"] = frame["amount"].clip(lower=0)
    return _attach_prior_destination_state(frame), header_columns


def _attach_prior_destination_state(frame: pd.DataFrame) -> pd.DataFrame:
    """Attach history available before each time step; same-step rows never see each other."""
    enriched = frame.copy()
    enriched["_row_order"] = np.arange(len(enriched), dtype="int64")
    enriched["_risky_type"] = enriched["type"].isin(["TRANSFER", "CASH_OUT"]).astype("float32")
    enriched["_transfer_type"] = (enriched["type"].astype(str) == "TRANSFER").astype("float32")
    enriched["_cashout_type"] = (enriched["type"].astype(str) == "CASH_OUT").astype("float32")
    step_state = (
        enriched.groupby(["nameDest", "step"], observed=True, sort=False)
        .agg(
            destination_step_count=("amount", "size"),
            destination_step_amount_sum=("amount", "sum"),
            destination_step_risky_count=("_risky_type", "sum"),
            destination_step_transfer_count=("_transfer_type", "sum"),
            destination_step_cashout_count=("_cashout_type", "sum"),
        )
        .reset_index()
        .sort_values(["nameDest", "step"], kind="mergesort")
    )
    grouped = step_state.groupby("nameDest", observed=True, sort=False)
    for source, target in [
        ("destination_step_count", "destination_prior_count"),
        ("destination_step_amount_sum", "destination_prior_amount_sum"),
        ("destination_step_risky_count", "destination_prior_risky_count"),
        ("destination_step_transfer_count", "destination_prior_transfer_count"),
        ("destination_step_cashout_count", "destination_prior_cashout_count"),
    ]:
        step_state[target] = grouped[source].cumsum() - step_state[source]
    prior_columns = [
        "nameDest",
        "step",
        "destination_prior_count",
        "destination_prior_amount_sum",
        "destination_prior_risky_count",
        "destination_prior_transfer_count",
        "destination_prior_cashout_count",
    ]
    enriched = enriched.merge(step_state[prior_columns], on=["nameDest", "step"], how="left", sort=False)
    enriched = enriched.sort_values("_row_order", kind="mergesort").drop(
        columns=["_row_order", "_risky_type", "_transfer_type", "_cashout_type"]
    )
    return enriched.reset_index(drop=True)


def _prepare_data(split: Any) -> _CompetitivePreparedData:
    train_amount = split.train["amount"].to_numpy(dtype="float64")
    state = _CompetitiveFeatureState(
        train_max_step=max(1, int(split.train["step"].max())),
        amount_p90=float(np.quantile(train_amount, 0.90)),
        amount_p99=float(np.quantile(train_amount, 0.99)),
        amount_p999=float(np.quantile(train_amount, 0.999)),
    )
    return _CompetitivePreparedData(
        x_train=_feature_matrix(split.train, state=state),
        x_validation=_feature_matrix(split.validation, state=state),
        x_test=_feature_matrix(split.test, state=state),
        y_train=split.train["isFraud"].to_numpy(dtype=int),
        y_validation=split.validation["isFraud"].to_numpy(dtype=int),
        y_test=split.test["isFraud"].to_numpy(dtype=int),
        validation_steps=split.validation["step"].to_numpy(dtype=int),
        feature_state=state,
    )


def _feature_matrix(frame: pd.DataFrame, *, state: _CompetitiveFeatureState) -> np.ndarray:
    amount = frame["amount"].to_numpy(dtype="float32")
    log_amount = np.log1p(amount)
    step = frame["step"].to_numpy(dtype="float32")
    hour = np.remainder(step - 1.0, 24.0)
    weekday = np.remainder(np.floor((step - 1.0) / 24.0), 7.0)
    typed_values = frame["type"].astype(str).to_numpy()
    typed = [(typed_values == item).astype("float32") for item in _PAYSIM_TYPES]
    cashout = typed[_PAYSIM_TYPES.index("CASH_OUT")]
    transfer = typed[_PAYSIM_TYPES.index("TRANSFER")]
    prior_count = frame["destination_prior_count"].to_numpy(dtype="float32")
    prior_amount = frame["destination_prior_amount_sum"].to_numpy(dtype="float32")
    prior_risky = frame["destination_prior_risky_count"].to_numpy(dtype="float32")
    prior_transfer = frame["destination_prior_transfer_count"].to_numpy(dtype="float32")
    prior_cashout = frame["destination_prior_cashout_count"].to_numpy(dtype="float32")
    prior_denominator = np.maximum(prior_count, 1.0)
    prior_mean_amount = prior_amount / prior_denominator
    matrix = [
        log_amount,
        np.sqrt(amount),
        np.square(log_amount),
        step / float(state.train_max_step),
        np.sin(2.0 * np.pi * hour / 24.0),
        np.cos(2.0 * np.pi * hour / 24.0),
        np.sin(2.0 * np.pi * weekday / 7.0),
        np.cos(2.0 * np.pi * weekday / 7.0),
        *typed,
        np.maximum(cashout, transfer),
        log_amount * cashout,
        log_amount * transfer,
        (amount > state.amount_p90).astype("float32"),
        (amount > state.amount_p99).astype("float32"),
        (amount > state.amount_p999).astype("float32"),
        (prior_count == 0).astype("float32"),
        np.log1p(prior_count),
        np.log1p(prior_amount),
        prior_risky / prior_denominator,
        prior_transfer / prior_denominator,
        prior_cashout / prior_denominator,
        log_amount - np.log1p(prior_mean_amount),
    ]
    return np.asarray(np.vstack(matrix).T, dtype="float32")


def _run_search(
    *,
    prepared: _CompetitivePreparedData,
    split: Any,
    effective_budget_tier: str,
    run_optional: bool,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    probe_indices, probe_policy = _probe_training_indices(prepared, effective_budget_tier)
    x_probe = prepared.x_train[probe_indices]
    y_probe = prepared.y_train[probe_indices]
    imbalance_ratio = _safe_divide(float(np.sum(y_probe == 0)), float(np.sum(y_probe == 1)))
    full_imbalance_ratio = _safe_divide(
        float(np.sum(prepared.y_train == 0)),
        float(np.sum(prepared.y_train == 1)),
    )
    attempts: list[dict[str, Any]] = []
    family_probe_results: dict[str, list[dict[str, Any]]] = {}
    unavailable: list[dict[str, Any]] = []
    specs = _search_specs(
        budget_tier=effective_budget_tier,
        run_optional=run_optional,
        imbalance_ratio=imbalance_ratio,
    )
    for family_id, role, module, configurations in specs:
        if module and not _module_available(module):
            unavailable.append(
                {
                    "family_id": family_id,
                    "adapter_module": module,
                    "execution_state": "fallback",
                    "blocked_reason": "optional_adapter_not_installed",
                }
            )
            continue
        if module and not run_optional:
            unavailable.append(
                {
                    "family_id": family_id,
                    "adapter_module": module,
                    "execution_state": "eligible_not_run",
                    "blocked_reason": "optional_execution_not_requested",
                }
            )
            continue
        family_probe_results[family_id] = []
        for trial_index, config in enumerate(configurations, start=1):
            result = _fit_and_validate(
                family_id=family_id,
                module=module,
                configuration=config,
                x_train=x_probe,
                y_train=y_probe,
                x_validation=prepared.x_validation,
                y_validation=prepared.y_validation,
                random_state=PAYSIM_COMPETITIVE_RANDOM_SEEDS[0],
            )
            trial = {
                **result,
                "stage": "probe",
                "family_id": family_id,
                "family_role": role,
                "adapter_module": module or "scikit-learn",
                "adapter_version": _module_version(module or "scikit-learn"),
                "trial_id": f"{family_id}_probe_{trial_index}",
                "training_row_count": int(len(y_probe)),
                "selection_surface": "validation_pr_auc_only",
            }
            attempts.append(trial)
            if trial["execution_state"] == "ran":
                family_probe_results[family_id].append(trial)

    finalist_rows: list[dict[str, Any]] = []
    fitted_finalists: list[dict[str, Any]] = []
    for family_id, probe_rows in family_probe_results.items():
        if not probe_rows:
            continue
        probe_winner = max(probe_rows, key=lambda row: float(row["validation_metrics"]["pr_auc"]))
        role = str(probe_winner["family_role"])
        module_value = str(probe_winner["adapter_module"])
        module = None if module_value == "scikit-learn" else module_value
        config = _materialize_full_train_config(
            family_id=family_id,
            configuration=dict(probe_winner["configuration"]),
            full_imbalance_ratio=full_imbalance_ratio,
        )
        finalist = _fit_and_validate(
            family_id=family_id,
            module=module,
            configuration=config,
            x_train=prepared.x_train,
            y_train=prepared.y_train,
            x_validation=prepared.x_validation,
            y_validation=prepared.y_validation,
            random_state=PAYSIM_COMPETITIVE_RANDOM_SEEDS[0],
            return_model=True,
        )
        finalist_row = {
            **{key: value for key, value in finalist.items() if key != "_model"},
            "stage": "full_train_finalist",
            "family_id": family_id,
            "family_role": role,
            "adapter_module": module_value,
            "adapter_version": _module_version(module or "scikit-learn"),
            "source_probe_trial_id": probe_winner["trial_id"],
            "training_row_count": int(len(prepared.y_train)),
            "selection_surface": "validation_pr_auc_only",
            "test_metrics": None,
            "test_evaluated": False,
        }
        attempts.append(finalist_row)
        if finalist_row["execution_state"] == "ran":
            finalist_rows.append(finalist_row)
            fitted_finalists.append({**finalist_row, "_model": finalist["_model"]})

    rule_scores = _rule_scores(split.validation)
    candidate_rows: list[dict[str, Any]] = [
        {
            "family_id": "deterministic_transfer_cashout_rule",
            "family_role": "rules_reference",
            "stage": "fixed_reference",
            "execution_state": "ran",
            "budget_tier": effective_budget_tier,
            "eligible_for_model_selection": False,
            "validation_metrics": _binary_score_metrics(prepared.y_validation, rule_scores),
            "test_metrics": None,
            "test_evaluated": False,
            "selection_surface": "reference_only_not_a_search_candidate",
            "configuration": {
                "rule": "fixed_sigmoid_log_amount_plus_transfer_cashout_flags",
                "fit_surface": "none",
            },
        }
    ]
    candidate_rows.extend({**row, "budget_tier": effective_budget_tier, "eligible_for_model_selection": True} for row in finalist_rows)
    selected = max(
        fitted_finalists,
        key=lambda row: float(row["validation_metrics"]["pr_auc"]),
        default=None,
    )
    calibration_trace: dict[str, Any] = {"status": "blocked", "reason": "no_finalist_completed"}
    selected_summary: dict[str, Any] | None = None
    if selected is not None:
        model = selected["_model"]
        raw_validation_scores = _predict_scores(model, prepared.x_validation)
        raw_test_scores = _predict_scores(model, prepared.x_test)
        calibration_trace, final_validation_scores, final_test_scores, threshold_indices = _calibrate_selected_scores(
            y_validation=prepared.y_validation,
            validation_steps=prepared.validation_steps,
            raw_validation_scores=raw_validation_scores,
            raw_test_scores=raw_test_scores,
        )
        operating_validation_scores = final_validation_scores[threshold_indices]
        operating_validation_y = prepared.y_validation[threshold_indices]
        threshold = _threshold_for_review_fraction(operating_validation_scores, SELECTED_REVIEW_BUDGET_FRACTION)
        fpr_threshold = _threshold_for_fpr(
            operating_validation_y,
            operating_validation_scores,
            target_fpr=FIXED_FPR_TARGET,
        )
        selected_summary = {
            "family_id": selected["family_id"],
            "configuration": selected["configuration"],
            "selection_surface": "validation_pr_auc_only_before_test_evaluation",
            "validation_pr_auc": selected["validation_metrics"]["pr_auc"],
            "raw_test_pr_auc": _binary_score_metrics(prepared.y_test, raw_test_scores)["pr_auc"],
            "test_pr_auc": _binary_score_metrics(prepared.y_test, final_test_scores)["pr_auc"],
            "test_roc_auc": _binary_score_metrics(prepared.y_test, final_test_scores)["roc_auc"],
            "calibration_method": calibration_trace["selected_method"],
            "threshold_selection_surface": "validation_operating_partition_only",
            "review_budget_fraction": SELECTED_REVIEW_BUDGET_FRACTION,
            "validation_threshold": _round_float(threshold),
            "validation_operating_point": _threshold_metrics(
                operating_validation_y,
                operating_validation_scores,
                threshold=threshold,
                requested_fraction=SELECTED_REVIEW_BUDGET_FRACTION,
            ),
            "test_operating_point": _threshold_metrics(
                prepared.y_test,
                final_test_scores,
                threshold=threshold,
                requested_fraction=SELECTED_REVIEW_BUDGET_FRACTION,
            ),
            "fixed_fpr": {
                "target_fpr": FIXED_FPR_TARGET,
                "validation_threshold": _round_float(fpr_threshold),
                "test": _threshold_metrics(
                    prepared.y_test,
                    final_test_scores,
                    threshold=fpr_threshold,
                    requested_fraction=None,
                ),
            },
        }
        for row in candidate_rows:
            if row["family_id"] == selected["family_id"]:
                row["test_evaluated"] = True
                row["test_metrics"] = {
                    "raw": _binary_score_metrics(prepared.y_test, raw_test_scores),
                    "post_calibration": _binary_score_metrics(prepared.y_test, final_test_scores),
                }
                row["selected_for_test_evaluation"] = True
                row["calibration_method"] = calibration_trace["selected_method"]
                row["selected_review_budget"] = selected_summary["test_operating_point"]
    trace = {
        "probe_policy": probe_policy,
        "attempts": attempts,
        "fallback_or_not_run": unavailable,
        "finalist_rows": finalist_rows,
        "selected_summary": selected_summary,
        "calibration_trace": calibration_trace,
        "probe_trial_count": sum(1 for row in attempts if row["stage"] == "probe"),
        "finalist_fit_count": sum(1 for row in attempts if row["stage"] == "full_train_finalist"),
    }
    return candidate_rows, trace


def _search_specs(
    *,
    budget_tier: str,
    run_optional: bool,
    imbalance_ratio: float,
) -> list[tuple[str, str, str | None, list[dict[str, Any]]]]:
    del run_optional
    if budget_tier == "smoke":
        return [
            ("sklearn_hist_gradient_boosting", "strong_boosted_tree", None, [{"max_iter": 30, "learning_rate": 0.08, "max_leaf_nodes": 15, "min_samples_leaf": 5, "l2_regularization": 1.0, "class_weight": "balanced"}]),
            ("sklearn_extra_trees", "strong_tree_ensemble", None, [{"n_estimators": 32, "max_depth": 12, "min_samples_leaf": 2, "class_weight": "balanced_subsample", "bootstrap": False, "max_samples": None}]),
            ("sklearn_random_forest", "strong_tree_ensemble", None, [{"n_estimators": 32, "max_depth": 12, "min_samples_leaf": 2, "class_weight": "balanced_subsample", "bootstrap": True, "max_samples": None}]),
            ("lightgbm_classifier", "optional_boosted_tree_adapter", "lightgbm", [{"n_estimators": 40, "learning_rate": 0.08, "num_leaves": 15, "min_child_samples": 5, "scale_pos_weight": 1.0}]),
            ("xgboost_classifier", "optional_boosted_tree_adapter", "xgboost", [{"n_estimators": 40, "learning_rate": 0.08, "max_depth": 4, "min_child_weight": 1.0, "scale_pos_weight": max(1.0, np.sqrt(imbalance_ratio))}]),
        ]
    return [
        (
            "sklearn_hist_gradient_boosting",
            "strong_boosted_tree",
            None,
            [
                {"max_iter": 180, "learning_rate": 0.06, "max_leaf_nodes": 31, "min_samples_leaf": 30, "l2_regularization": 1.0, "class_weight": "balanced"},
                {"max_iter": 250, "learning_rate": 0.04, "max_leaf_nodes": 63, "min_samples_leaf": 20, "l2_regularization": 2.0, "class_weight": "balanced"},
                {"max_iter": 160, "learning_rate": 0.08, "max_leaf_nodes": 63, "min_samples_leaf": 50, "l2_regularization": 0.5, "class_weight": "balanced"},
            ],
        ),
        (
            "sklearn_extra_trees",
            "strong_tree_ensemble",
            None,
            [
                {"n_estimators": 160, "max_depth": 18, "min_samples_leaf": 4, "class_weight": "balanced_subsample", "bootstrap": True, "max_samples": 0.35},
                {"n_estimators": 220, "max_depth": 24, "min_samples_leaf": 8, "class_weight": "balanced_subsample", "bootstrap": True, "max_samples": 0.45},
                {"n_estimators": 180, "max_depth": None, "min_samples_leaf": 12, "class_weight": "balanced", "bootstrap": False, "max_samples": None},
            ],
        ),
        (
            "sklearn_random_forest",
            "strong_tree_ensemble",
            None,
            [
                {"n_estimators": 120, "max_depth": 18, "min_samples_leaf": 5, "class_weight": "balanced_subsample", "bootstrap": True, "max_samples": 0.35},
                {"n_estimators": 160, "max_depth": 24, "min_samples_leaf": 10, "class_weight": "balanced_subsample", "bootstrap": True, "max_samples": 0.45},
            ],
        ),
        (
            "lightgbm_classifier",
            "optional_boosted_tree_adapter",
            "lightgbm",
            [
                {"n_estimators": 240, "learning_rate": 0.04, "num_leaves": 31, "min_child_samples": 40, "scale_pos_weight": 1.0},
                {"n_estimators": 300, "learning_rate": 0.03, "num_leaves": 63, "min_child_samples": 30, "scale_pos_weight": max(1.0, np.sqrt(imbalance_ratio))},
                {"n_estimators": 200, "learning_rate": 0.06, "num_leaves": 31, "min_child_samples": 60, "scale_pos_weight": max(1.0, np.sqrt(imbalance_ratio) / 2.0)},
            ],
        ),
        (
            "xgboost_classifier",
            "optional_boosted_tree_adapter",
            "xgboost",
            [
                {"n_estimators": 240, "learning_rate": 0.05, "max_depth": 5, "min_child_weight": 3.0, "scale_pos_weight": max(1.0, np.sqrt(imbalance_ratio))},
                {"n_estimators": 320, "learning_rate": 0.03, "max_depth": 7, "min_child_weight": 5.0, "scale_pos_weight": max(1.0, np.sqrt(imbalance_ratio) / 2.0)},
                {"n_estimators": 220, "learning_rate": 0.06, "max_depth": 4, "min_child_weight": 2.0, "scale_pos_weight": 1.0},
            ],
        ),
    ]


def _probe_training_indices(prepared: _CompetitivePreparedData, budget_tier: str) -> tuple[np.ndarray, dict[str, Any]]:
    row_count = len(prepared.y_train)
    if budget_tier == "smoke" or row_count <= PAYSIM_COMPETITIVE_PROBE_MAX_TRAIN_ROWS:
        return np.arange(row_count), {
            "sampling_policy": "all_training_rows",
            "probe_training_row_count": row_count,
            "full_training_row_count": row_count,
        }
    rng = np.random.default_rng(PAYSIM_COMPETITIVE_RANDOM_SEEDS[0])
    positive = np.flatnonzero(prepared.y_train == 1)
    negative = np.flatnonzero(prepared.y_train == 0)
    negative_budget = max(0, PAYSIM_COMPETITIVE_PROBE_MAX_TRAIN_ROWS - len(positive))
    selected_negative = rng.choice(negative, size=min(negative_budget, len(negative)), replace=False)
    indices = np.sort(np.concatenate([positive, selected_negative]))
    return indices, {
        "sampling_policy": "train_only_all_positives_plus_seeded_negative_subsample_for_probe",
        "probe_training_row_count": int(len(indices)),
        "full_training_row_count": int(row_count),
        "positive_rows_retained": int(len(positive)),
        "random_seed": PAYSIM_COMPETITIVE_RANDOM_SEEDS[0],
        "finalist_refit_policy": "full_training_rows_only",
    }


def _fit_and_validate(
    *,
    family_id: str,
    module: str | None,
    configuration: dict[str, Any],
    x_train: np.ndarray,
    y_train: np.ndarray,
    x_validation: np.ndarray,
    y_validation: np.ndarray,
    random_state: int,
    return_model: bool = False,
) -> dict[str, Any]:
    started = perf_counter()
    try:
        model, materialized = _make_model(
            family_id=family_id,
            configuration=configuration,
            random_state=random_state,
        )
        model.fit(x_train, y_train)
        validation_scores = _predict_scores(model, x_validation)
        result = {
            "execution_state": "ran",
            "runtime_seconds": _round_float(perf_counter() - started),
            "random_seed": random_state,
            "configuration": materialized,
            "validation_metrics": _binary_score_metrics(y_validation, validation_scores),
        }
        if return_model:
            result["_model"] = model
        return result
    except Exception as exc:
        return {
            "execution_state": "fallback",
            "runtime_seconds": _round_float(perf_counter() - started),
            "random_seed": random_state,
            "configuration": configuration,
            "blocked_reason": f"execution_failed: {exc}",
        }


def _make_model(
    *,
    family_id: str,
    configuration: dict[str, Any],
    random_state: int,
) -> tuple[Any, dict[str, Any]]:
    params = dict(configuration)
    if family_id == "sklearn_hist_gradient_boosting":
        from sklearn.ensemble import HistGradientBoostingClassifier

        params["random_state"] = random_state
        return HistGradientBoostingClassifier(**params), {**params, "imbalance_fit_surface": "train_only"}
    if family_id == "sklearn_extra_trees":
        from sklearn.ensemble import ExtraTreesClassifier

        params.update({"random_state": random_state, "n_jobs": -1})
        return ExtraTreesClassifier(**params), {**params, "imbalance_fit_surface": "train_only"}
    if family_id == "sklearn_random_forest":
        from sklearn.ensemble import RandomForestClassifier

        params.update({"random_state": random_state, "n_jobs": -1})
        return RandomForestClassifier(**params), {**params, "imbalance_fit_surface": "train_only"}
    if family_id == "lightgbm_classifier":
        from lightgbm import LGBMClassifier

        params.update(
            {
                "random_state": random_state,
                "n_jobs": -1,
                "verbosity": -1,
                "subsample": 0.9,
                "colsample_bytree": 0.9,
            }
        )
        return LGBMClassifier(**params), {**params, "imbalance_fit_surface": "train_only"}
    if family_id == "xgboost_classifier":
        from xgboost import XGBClassifier

        params.update(
            {
                "random_state": random_state,
                "n_jobs": -1,
                "tree_method": "hist",
                "eval_metric": "logloss",
                "objective": "binary:logistic",
                "subsample": 0.9,
                "colsample_bytree": 0.9,
            }
        )
        return XGBClassifier(**params), {**params, "imbalance_fit_surface": "train_only"}
    raise ValueError(f"Unsupported competitive family: {family_id}")


def _materialize_full_train_config(
    *,
    family_id: str,
    configuration: dict[str, Any],
    full_imbalance_ratio: float,
) -> dict[str, Any]:
    config = {key: value for key, value in configuration.items() if key not in {"random_state", "n_jobs", "verbosity", "subsample", "colsample_bytree", "tree_method", "eval_metric", "objective", "imbalance_fit_surface"}}
    if family_id in {"lightgbm_classifier", "xgboost_classifier"}:
        probe_weight = float(config.get("scale_pos_weight", 1.0))
        if probe_weight > 1.0:
            config["scale_pos_weight"] = min(probe_weight, max(1.0, np.sqrt(full_imbalance_ratio)))
    return config


def _predict_scores(model: Any, values: np.ndarray) -> np.ndarray:
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", message="X does not have valid feature names.*")
        return np.asarray(model.predict_proba(values)[:, 1], dtype=float)


def _calibrate_selected_scores(
    *,
    y_validation: np.ndarray,
    validation_steps: np.ndarray,
    raw_validation_scores: np.ndarray,
    raw_test_scores: np.ndarray,
) -> tuple[dict[str, Any], np.ndarray, np.ndarray, np.ndarray]:
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import log_loss

    calibration_indices, operating_indices, partition_policy = _calibration_partitions(
        y_validation=y_validation,
        validation_steps=validation_steps,
    )
    candidates = [
        {
            "method": "identity",
            "operating_scores": raw_validation_scores[operating_indices],
            "full_validation_scores": raw_validation_scores,
            "test_scores": raw_test_scores,
        }
    ]
    if calibration_indices is not None and operating_indices is not None:
        calibrator = LogisticRegression(C=1.0, random_state=42, solver="lbfgs")
        fit_x = _logit(raw_validation_scores[calibration_indices]).reshape(-1, 1)
        calibrator.fit(fit_x, y_validation[calibration_indices])
        if float(calibrator.coef_[0][0]) > 0:
            candidates.append(
                {
                    "method": "platt_sigmoid",
                    "operating_scores": calibrator.predict_proba(
                        _logit(raw_validation_scores[operating_indices]).reshape(-1, 1)
                    )[:, 1],
                    "full_validation_scores": calibrator.predict_proba(
                        _logit(raw_validation_scores).reshape(-1, 1)
                    )[:, 1],
                    "test_scores": calibrator.predict_proba(_logit(raw_test_scores).reshape(-1, 1))[:, 1],
                }
            )
    else:
        operating_indices = np.arange(len(y_validation))
    scored = []
    for candidate in candidates:
        scored.append(
            {
                **candidate,
                "operating_log_loss": _round_float(
                    log_loss(y_validation[operating_indices], candidate["operating_scores"], labels=[0, 1])
                ),
            }
        )
    selected = min(scored, key=lambda row: float(row["operating_log_loss"]))
    report_rows = [
        {"method": row["method"], "operating_log_loss": row["operating_log_loss"]}
        for row in scored
    ]
    return (
        {
            "status": "ok",
            "selection_metric": "validation_operating_partition_log_loss",
            "partition_policy": partition_policy,
            "calibration_row_count": int(len(calibration_indices)) if calibration_indices is not None else 0,
            "operating_point_row_count": int(len(operating_indices)),
            "candidates": report_rows,
            "selected_method": selected["method"],
            "test_used_for_calibration_or_selection": False,
        },
        np.asarray(selected["full_validation_scores"], dtype=float),
        np.asarray(selected["test_scores"], dtype=float),
        operating_indices,
    )


def _calibration_partitions(
    *,
    y_validation: np.ndarray,
    validation_steps: np.ndarray,
) -> tuple[np.ndarray | None, np.ndarray, str]:
    midpoint = float(np.median(validation_steps))
    calibration = np.flatnonzero(validation_steps <= midpoint)
    operating = np.flatnonzero(validation_steps > midpoint)
    if _has_two_classes(y_validation[calibration]) and _has_two_classes(y_validation[operating]):
        return calibration, operating, "chronological_validation_calibration_then_operating_subwindows"
    calibration = np.arange(0, len(y_validation), 2)
    operating = np.arange(1, len(y_validation), 2)
    if _has_two_classes(y_validation[calibration]) and _has_two_classes(y_validation[operating]):
        return calibration, operating, "validation_only_deterministic_alternating_fallback_for_class_coverage"
    return None, np.arange(len(y_validation)), "identity_calibration_fallback_insufficient_validation_class_coverage"


def _rule_scores(frame: pd.DataFrame) -> np.ndarray:
    log_amount = np.log1p(frame["amount"].to_numpy(dtype="float64"))
    typed = frame["type"].astype(str).to_numpy()
    raw_score = log_amount + (2.0 * (typed == "TRANSFER")) + (typed == "CASH_OUT")
    return 1.0 / (1.0 + np.exp(-np.clip((raw_score - 8.0) / 2.0, -30.0, 30.0)))


def _build_split_audit(
    *,
    root: Path,
    data_path: Path,
    frame: pd.DataFrame,
    split: Any,
    header_columns: list[str],
) -> dict[str, Any]:
    split_rows = [
        _split_row("train", split.train),
        _split_row("validation", split.validation),
        _split_row("test", split.test),
    ]
    forbidden_present = [column for column in PAYSIM_FORBIDDEN_MODEL_COLUMNS if column in header_columns]
    balance_columns = [column for column in PAYSIM_FORBIDDEN_MODEL_COLUMNS if "balance" in column.lower()]
    forbidden_used = [column for column in balance_columns if column in PAYSIM_COMPETITIVE_FEATURE_COLUMNS]
    chronological_ok = (
        bool(len(split.train) and len(split.validation) and len(split.test))
        and int(split.train["step"].max()) < int(split.validation["step"].min())
        and int(split.validation["step"].max()) < int(split.test["step"].min())
    )
    class_ok = all(int(row["positive_count"]) > 0 and int(row["negative_count"]) > 0 for row in split_rows)
    status = "ok" if chronological_ok and class_ok and not forbidden_used else "blocked"
    return {
        "status": status,
        "dataset_id": PAYSIM_COMPETITIVE_DATASET_ID,
        "source_path": _display_path(root, data_path),
        "source_sha256": _sha256(data_path),
        "row_count": int(len(frame)),
        "split_contract_id": PAYSIM_COMPETITIVE_SPLIT_CONTRACT_ID,
        "split_rows": split_rows,
        "chronological_order_ok": chronological_ok,
        "class_coverage_ok": class_ok,
        "forbidden_source_columns_present_but_excluded": forbidden_present,
        "forbidden_balance_columns_used": forbidden_used,
        "identifier_policy": "nameDest_is_used_only_as_a_prior_step_grouping_key_never_as_a_raw_model_feature",
        "summary": (
            "P6-A uses the frozen chronological PaySim split, excludes balance fields, and derives destination history only from earlier steps."
            if status == "ok"
            else "P6-A cannot run until chronological, class-coverage, and forbidden-feature checks pass."
        ),
    }


def _build_feature_report(
    *,
    root: Path,
    data_path: Path,
    split_audit: dict[str, Any],
    prepared: _CompetitivePreparedData,
) -> dict[str, Any]:
    return {
        "schema_version": PAYSIM_COMPETITIVE_SCHEMA_VERSION,
        "slice": "Paper Track P6-A",
        "status": "pass" if split_audit["status"] == "ok" else "blocked",
        "dataset_id": PAYSIM_COMPETITIVE_DATASET_ID,
        "source_path": _display_path(root, data_path),
        "source_sha256": split_audit["source_sha256"],
        "split_contract_id": PAYSIM_COMPETITIVE_SPLIT_CONTRACT_ID,
        "feature_contract_id": PAYSIM_COMPETITIVE_FEATURE_CONTRACT_ID,
        "feature_columns": PAYSIM_COMPETITIVE_FEATURE_COLUMNS,
        "raw_modeled_source_fields": ["step", "type", "amount"],
        "state_key_source_fields": ["nameDest"],
        "identifier_policy": split_audit["identifier_policy"],
        "nameOrig_used": False,
        "raw_identifier_encoding_used": False,
        "balance_fields_used": False,
        "forbidden_source_columns_present_but_excluded": split_audit["forbidden_source_columns_present_but_excluded"],
        "forbidden_balance_columns_used": split_audit["forbidden_balance_columns_used"],
        "feature_derivation_policy": (
            "row_local_amount_type_time_features_plus_train_only_amount_thresholds_plus_destination_aggregates_shifted_before_each_step"
        ),
        "same_step_entity_information_used": False,
        "label_derived_history_used": False,
        "validation_or_test_labels_used_for_features": False,
        "train_only_fit_state": {
            "train_max_step": prepared.feature_state.train_max_step,
            "amount_p90": _round_float(prepared.feature_state.amount_p90),
            "amount_p99": _round_float(prepared.feature_state.amount_p99),
            "amount_p999": _round_float(prepared.feature_state.amount_p999),
        },
        "threshold_and_calibration_policy": (
            "candidate selection uses validation PR-AUC; calibration and thresholds use validation-only partitions; test is evaluated once after winner selection"
        ),
        "summary": "P6-A adds auditable prior-step destination behavior without balance leakage, raw account encoding, or test-driven selection.",
    }


def _build_budget_contract(
    *,
    requested_budget_tier: str,
    effective_budget_tier: str,
    run_optional: bool,
    split_audit: dict[str, Any],
    trace_payload: dict[str, Any],
) -> dict[str, Any]:
    return {
        "schema_version": PAYSIM_COMPETITIVE_SCHEMA_VERSION,
        "slice": "Paper Track P6-A",
        "status": "executed",
        "requested_budget_tier": requested_budget_tier,
        "effective_budget_tier": effective_budget_tier,
        "effective_budget_reason": (
            "fixture_or_small_source_is_smoke_only"
            if effective_budget_tier != requested_budget_tier
            else "requested_budget_executed"
        ),
        "dataset_row_count": split_audit["row_count"],
        "random_seeds": PAYSIM_COMPETITIVE_RANDOM_SEEDS,
        "optional_adapter_execution_requested": run_optional,
        "probe_policy": trace_payload["probe_policy"],
        "probe_trial_count": trace_payload["probe_trial_count"],
        "finalist_fit_count": trace_payload["finalist_fit_count"],
        "test_evaluation_policy": "only_validation_selected_finalist_is_evaluated_on_test",
        "calibration_policy": "validation_only_partitioned_platt_or_identity_selection",
        "threshold_policy": "validation_operating_partition_only_then_fixed_test_application",
        "release_proof_required": True,
        "summary": "P6-A records a multi-fidelity competitive budget with validation-only selection and one deferred test evaluation.",
    }


def _build_baseline_table(
    *,
    candidate_rows: list[dict[str, Any]],
    trace_payload: dict[str, Any],
    effective_budget_tier: str,
    source_sha256: str,
    baseline_linked: bool,
    p4_row: dict[str, Any],
    p6_table: dict[str, Any],
) -> dict[str, Any]:
    p6_selected = p6_table.get("validation_selected_baseline") if baseline_linked else None
    return {
        "schema_version": PAYSIM_COMPETITIVE_SCHEMA_VERSION,
        "slice": "Paper Track P6-A",
        "status": "ok" if trace_payload["selected_summary"] else "no_competitive_finalist_completed",
        "dataset_id": PAYSIM_COMPETITIVE_DATASET_ID,
        "source_sha256": source_sha256,
        "split_contract_id": PAYSIM_COMPETITIVE_SPLIT_CONTRACT_ID,
        "feature_contract_id": PAYSIM_COMPETITIVE_FEATURE_CONTRACT_ID,
        "effective_budget_tier": effective_budget_tier,
        "comparison_metric": "validation_pr_auc",
        "selection_rule": "rank_full_train_finalists_on_validation_pr_auc_then_evaluate_only_the_selected_finalist_on_test",
        "rows": candidate_rows,
        "validation_selected_competitive_model": trace_payload["selected_summary"],
        "same_source_baseline_linked": baseline_linked,
        "p4_reference_row": {
            "model_family": p4_row.get("model_family"),
            "test_pr_auc": dict(p4_row.get("metrics", {})).get("test_pr_auc"),
            "artifact_ref": "docs/reports/paysim_paper_result_row.json",
        }
        if baseline_linked
        else None,
        "p6_validation_selected_baseline": p6_selected,
        "test_visibility_policy": "nonselected_competitive_finalists_have_no_test_metrics",
        "summary": "P6-A places prior baseline evidence beside a validation-selected competitive finalist without searching over test outcomes.",
    }


def _build_search_trace(
    *,
    trace_payload: dict[str, Any],
    effective_budget_tier: str,
    run_optional: bool,
) -> dict[str, Any]:
    return {
        "schema_version": PAYSIM_COMPETITIVE_SCHEMA_VERSION,
        "slice": "Paper Track P6-A",
        "status": "competitive_executed" if trace_payload["selected_summary"] else "blocked",
        "effective_budget_tier": effective_budget_tier,
        "optional_execution_requested": run_optional,
        "random_seeds": PAYSIM_COMPETITIVE_RANDOM_SEEDS,
        "probe_policy": trace_payload["probe_policy"],
        "hpo_trial_count": trace_payload["probe_trial_count"],
        "full_train_finalist_fit_count": trace_payload["finalist_fit_count"],
        "attempts": trace_payload["attempts"],
        "fallback_or_not_run": trace_payload["fallback_or_not_run"],
        "calibration_trace": trace_payload["calibration_trace"],
        "selected_finalist": trace_payload["selected_summary"],
        "test_visibility_policy": "test_scores_are_materialized_for_the_validation_selected_finalist_only",
        "summary": "P6-A executes bounded competitive search, full-training finalist refits, validation-only calibration and threshold choice, then one fixed test evaluation.",
    }


def _build_publishability_gate(
    *,
    table: dict[str, Any],
    feature_report: dict[str, Any],
    budget_contract: dict[str, Any],
    baseline_linked: bool,
    claim_taxonomy: dict[str, Any],
) -> dict[str, Any]:
    selected = dict(table.get("validation_selected_competitive_model", {}) or {})
    p6_selected = dict(table.get("p6_validation_selected_baseline", {}) or {})
    protocol_checks = {
        "chronological_split_passed": feature_report["status"] == "pass",
        "forbidden_balance_fields_excluded": not feature_report["forbidden_balance_columns_used"],
        "prior_step_only_entity_history": not feature_report["same_step_entity_information_used"],
        "test_not_used_for_model_or_calibration_selection": True,
        "competitive_budget_executed": budget_contract["effective_budget_tier"] == "competitive",
        "same_source_baseline_linked": baseline_linked,
        "strong_finalist_selected": bool(selected),
        "validation_improves_on_p6_baseline": (
            bool(selected)
            and bool(p6_selected)
            and float(selected["validation_pr_auc"]) > float(p6_selected["validation_pr_auc"])
        ),
    }
    supporting_candidate_allowed = all(protocol_checks.values())
    blocked_reasons = [
        code
        for code, passed in [
            ("competitive_budget_not_executed", protocol_checks["competitive_budget_executed"]),
            ("same_source_baseline_not_linked", protocol_checks["same_source_baseline_linked"]),
            ("competitive_model_did_not_improve_validation_floor", protocol_checks["validation_improves_on_p6_baseline"]),
        ]
        if not passed
    ]
    blocked_reasons.extend(
        [
            "paysim_is_supporting_proxy_not_real_bank_holdout",
            "release_budget_and_clean_clone_proof_not_executed",
            "graph_benchmark_evidence_not_yet_executed_p7_required",
        ]
    )
    return {
        "schema_version": PAYSIM_COMPETITIVE_SCHEMA_VERSION,
        "slice": "Paper Track P6-A",
        "status": "pass_supporting_only" if supporting_candidate_allowed else "blocked",
        "dataset_id": PAYSIM_COMPETITIVE_DATASET_ID,
        "claim_boundary_from_taxonomy": _claim_boundary("claim_paysim_temporal_transaction_fraud", claim_taxonomy),
        "protocol_checks": protocol_checks,
        "supporting_paper_table_candidate_allowed": supporting_candidate_allowed,
        "headline_performance_claim_allowed": False,
        "paper_primary_claim_allowed": False,
        "hard_performance_claims_allowed": False,
        "blocked_reason_codes": blocked_reasons,
        "public_claim_wording": (
            "Relaytic completed a leakage-audited competitive PaySim rerun with prior-step destination features, "
            "recorded search budget, and validation-only selection. PaySim remains supporting synthetic evidence, "
            "not a real-world AML or SOTA headline."
        ),
        "next_slice": "Paper Track P7",
        "summary": (
            "P6-A admits a supporting PaySim paper-table candidate while keeping headline and hard AML claims blocked for graph and release proof."
            if supporting_candidate_allowed
            else "P6-A remains non-publishable as a table candidate until its competitive protocol and validation-improvement conditions pass."
        ),
    }


def _build_manifest(
    *,
    root: Path,
    data_path: Path,
    table: dict[str, Any],
    budget_contract: dict[str, Any],
    gate: dict[str, Any],
) -> dict[str, Any]:
    selected = dict(table.get("validation_selected_competitive_model", {}) or {})
    return {
        "schema_version": PAYSIM_COMPETITIVE_SCHEMA_VERSION,
        "slice": "Paper Track P6-A",
        "status": "ok" if selected else "blocked",
        "dataset_id": PAYSIM_COMPETITIVE_DATASET_ID,
        "source_path": _display_path(root, data_path),
        "source_sha256": table["source_sha256"],
        "split_contract_id": PAYSIM_COMPETITIVE_SPLIT_CONTRACT_ID,
        "feature_contract_id": PAYSIM_COMPETITIVE_FEATURE_CONTRACT_ID,
        "requested_budget_tier": budget_contract["requested_budget_tier"],
        "effective_budget_tier": budget_contract["effective_budget_tier"],
        "hpo_trial_count": budget_contract["probe_trial_count"],
        "finalist_family_count": budget_contract["finalist_fit_count"],
        "validation_selected_competitive_model": selected or None,
        "supporting_paper_table_candidate_allowed": gate["supporting_paper_table_candidate_allowed"],
        "headline_performance_claim_allowed": False,
        "paper_primary_claim_allowed": False,
        "hard_performance_claims_allowed": False,
        "output_files": PAYSIM_COMPETITIVE_FILENAMES,
        "command": "relaytic release-safety paysim-competitive --budget-tier competitive --run-optional --format json",
        "next_slice": "Paper Track P7",
        "summary": "P6-A competitive PaySim evaluation completed under an untouched-test, leakage-audited, supporting-only paper contract.",
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
        "Run relaytic release-safety paysim-competitive --budget-tier competitive --run-optional --format json.",
        "Keep raw benchmark files out of git; commit only aggregate paper artifacts.",
    ]
    common = {
        "schema_version": PAYSIM_COMPETITIVE_SCHEMA_VERSION,
        "slice": "Paper Track P6-A",
        "status": "blocked",
        "dataset_id": PAYSIM_COMPETITIVE_DATASET_ID,
        "source_path": _display_path(root, data_path),
        "blocked_reason_codes": [reason_code],
        "recovery_instructions": recovery,
        "summary": reason,
    }
    return {
        "paysim_competitive_benchmark_manifest": {
            **common,
            "requested_budget_tier": budget_tier,
            "supporting_paper_table_candidate_allowed": False,
            "headline_performance_claim_allowed": False,
            "paper_primary_claim_allowed": False,
            "hard_performance_claims_allowed": False,
            "output_files": PAYSIM_COMPETITIVE_FILENAMES,
            "next_slice": "Paper Track P6-A repair before Paper Track P7",
        },
        "paysim_competitive_budget_contract": {**common, "requested_budget_tier": budget_tier},
        "paysim_competitive_search_trace": {**common, "attempts": [], "hpo_trial_count": 0},
        "paysim_leakage_safe_feature_report": {
            **common,
            "split_audit": split_audit,
            "balance_fields_used": False,
            "forbidden_balance_columns_used": [],
        },
        "paysim_competitive_baseline_table": {**common, "rows": [], "validation_selected_competitive_model": None},
        "paysim_publishability_gate": {
            **common,
            "supporting_paper_table_candidate_allowed": False,
            "headline_performance_claim_allowed": False,
            "paper_primary_claim_allowed": False,
            "hard_performance_claims_allowed": False,
        },
    }


def _p6_baseline_matches_source(
    *,
    source_sha256: str,
    p4_row: dict[str, Any],
    p6_manifest: dict[str, Any],
) -> bool:
    return (
        p4_row.get("dataset_sha256") == source_sha256
        and p6_manifest.get("dataset_id") == PAYSIM_COMPETITIVE_DATASET_ID
        and p6_manifest.get("effective_budget_tier") == "baseline"
    )


def _claim_boundary(claim_id: str, claim_taxonomy: dict[str, Any]) -> str | None:
    for claim in claim_taxonomy.get("claims", []):
        if claim.get("claim_id") == claim_id:
            return str(claim.get("boundary"))
    return None


def _module_available(module_name: str) -> bool:
    return importlib.util.find_spec(module_name) is not None


def _module_version(module_name: str) -> str | None:
    distribution = "scikit-learn" if module_name == "scikit-learn" else module_name
    try:
        return importlib_metadata.version(distribution)
    except importlib_metadata.PackageNotFoundError:
        return None


def _has_two_classes(values: np.ndarray) -> bool:
    return len(values) > 1 and len(np.unique(values)) == 2


def _logit(scores: np.ndarray) -> np.ndarray:
    clipped = np.clip(scores, 1e-8, 1.0 - 1e-8)
    return np.log(clipped / (1.0 - clipped))


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
