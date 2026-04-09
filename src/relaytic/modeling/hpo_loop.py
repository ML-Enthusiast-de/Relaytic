"""Bounded HPO planning and artifact helpers for Slice 15C."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import itertools
import json
from pathlib import Path
from typing import Any


HPO_BUDGET_CONTRACT_SCHEMA_VERSION = "relaytic.hpo_budget_contract.v1"
ARCHITECTURE_SEARCH_SPACE_SCHEMA_VERSION = "relaytic.architecture_search_space.v1"
EARLY_STOPPING_REPORT_SCHEMA_VERSION = "relaytic.early_stopping_report.v1"
SEARCH_LOOP_SCORECARD_SCHEMA_VERSION = "relaytic.search_loop_scorecard.v1"
WARM_START_TRANSFER_REPORT_SCHEMA_VERSION = "relaytic.warm_start_transfer_report.v1"
THRESHOLD_TUNING_REPORT_SCHEMA_VERSION = "relaytic.threshold_tuning_report.v1"
TRIAL_LEDGER_RECORD_SCHEMA_VERSION = "relaytic.trial_ledger_record.v1"

HPO_ARTIFACT_FILENAMES = {
    "hpo_budget_contract": "hpo_budget_contract.json",
    "architecture_search_space": "architecture_search_space.json",
    "trial_ledger": "trial_ledger.jsonl",
    "early_stopping_report": "early_stopping_report.json",
    "search_loop_scorecard": "search_loop_scorecard.json",
    "warm_start_transfer_report": "warm_start_transfer_report.json",
    "threshold_tuning_report": "threshold_tuning_report.json",
}

SEARCHABLE_FAMILIES = {
    "linear_ridge",
    "logistic_regression",
    "bagged_tree_ensemble",
    "boosted_tree_ensemble",
    "hist_gradient_boosting_ensemble",
    "extra_trees_ensemble",
    "bagged_tree_classifier",
    "boosted_tree_classifier",
    "hist_gradient_boosting_classifier",
    "extra_trees_classifier",
}


@dataclass(frozen=True)
class TrialPlan:
    trial_id: str
    family: str
    variant_id: str
    source: str
    family_loop_index: int
    hyperparameters: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "trial_id": self.trial_id,
            "family": self.family,
            "variant_id": self.variant_id,
            "source": self.source,
            "family_loop_index": self.family_loop_index,
            "hyperparameters": dict(self.hyperparameters),
        }


def derive_hpo_budget_contract(
    *,
    run_dir: str | Path,
    task_type: str,
    row_count: int,
    requested_family: str,
    preferred_candidate_order: list[str] | None,
    available_families: list[str],
) -> dict[str, Any]:
    root = Path(run_dir)
    preferred = [str(item).strip() for item in preferred_candidate_order or [] if str(item).strip()]
    selected_families = _select_hpo_families(
        requested_family=requested_family,
        preferred_candidate_order=preferred,
        available_families=available_families,
        task_type=task_type,
    )
    budget_cap = _read_budget_max_trials(root)
    if row_count <= 600:
        default_trials = 12
        default_seconds = 40
    elif row_count <= 4000:
        default_trials = 10
        default_seconds = 55
    else:
        default_trials = 8
        default_seconds = 70
    if task_type in {"multiclass_classification", "fraud_detection", "anomaly_detection"}:
        default_trials += 2
    max_trials = min(budget_cap, default_trials)
    family_count = max(1, len(selected_families))
    per_family_trial_cap = max(3, min(6, max_trials // family_count if family_count else max_trials))
    max_family_loops = min(max(1, family_count), 3 if task_type in {"multiclass_classification", "fraud_detection", "anomaly_detection"} else 2)
    payload = {
        "schema_version": HPO_BUDGET_CONTRACT_SCHEMA_VERSION,
        "generated_at": _utc_now(),
        "status": "ok",
        "backend": "deterministic_local_search",
        "seed": 42,
        "task_type": str(task_type),
        "row_count": int(max(row_count, 0)),
        "requested_family": str(requested_family or "auto"),
        "selected_families": selected_families,
        "max_trials": int(max_trials),
        "max_wall_clock_seconds": int(default_seconds),
        "per_family_trial_cap": int(per_family_trial_cap),
        "max_family_loops": int(max_family_loops),
        "plateau_patience": 2,
        "min_trials_before_plateau_stop": 3,
        "min_improvement_delta": 0.0005,
        "warm_start_enabled": True,
        "summary": (
            f"Relaytic will tune `{len(selected_families)}` family(s) with up to `{max_trials}` total trial(s), "
            f"`{per_family_trial_cap}` trial(s) per family, and `{default_seconds}` wall-clock second(s)."
        ),
    }
    return payload


def build_architecture_search_space(
    *,
    task_type: str,
    selected_families: list[str],
) -> dict[str, Any]:
    family_spaces: list[dict[str, Any]] = []
    for family in selected_families:
        space = _family_search_space(family=family)
        if not space:
            continue
        family_spaces.append(
            {
                "family": family,
                "searchable": True,
                "strategy": "seeded_random_without_replacement",
                "parameters": space["parameters"],
                "default_anchor": dict(space["default_anchor"]),
            }
        )
    return {
        "schema_version": ARCHITECTURE_SEARCH_SPACE_SCHEMA_VERSION,
        "generated_at": _utc_now(),
        "status": "ok" if family_spaces else "not_applicable",
        "task_type": str(task_type),
        "family_count": len(family_spaces),
        "families": family_spaces,
        "summary": (
            f"Relaytic materialized `{len(family_spaces)}` bounded architecture search space(s)."
            if family_spaces
            else "No bounded architecture search spaces were materialized for this run."
        ),
    }


def load_warm_start_state(
    *,
    run_dir: str | Path,
    selected_families: list[str],
) -> dict[str, Any]:
    root = Path(run_dir)
    ledger_path = root / HPO_ARTIFACT_FILENAMES["trial_ledger"]
    families = {str(item) for item in selected_families if str(item).strip()}
    imported: dict[str, dict[str, Any]] = {}
    imported_count = 0
    if ledger_path.exists():
        for line in ledger_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                payload = json.loads(line)
            except json.JSONDecodeError:
                continue
            family = str(payload.get("family", "")).strip()
            if family not in families:
                continue
            imported_count += 1
            current_rank = _rank_key(payload.get("validation_metrics"))
            best = imported.get(family)
            if best is None or current_rank < _rank_key(best.get("validation_metrics")):
                imported[family] = {
                    "hyperparameters": dict(payload.get("hyperparameters") or {}),
                    "trial_id": str(payload.get("trial_id", "")).strip(),
                    "validation_metrics": dict(payload.get("validation_metrics") or {}),
                    "source_path": str(ledger_path),
                }
    return {
        "schema_version": WARM_START_TRANSFER_REPORT_SCHEMA_VERSION,
        "generated_at": _utc_now(),
        "status": "warm_start_loaded" if imported else "no_prior_search",
        "enabled": True,
        "used": bool(imported),
        "source_path": str(ledger_path) if ledger_path.exists() else None,
        "imported_trial_count": int(imported_count),
        "imported_families": sorted(imported.keys()),
        "best_priors": imported,
        "summary": (
            f"Relaytic loaded warm-start priors for `{len(imported)}` family(s)."
            if imported
            else "Relaytic found no prior HPO ledger to warm-start from."
        ),
    }


def build_trial_plans(
    *,
    budget_contract: dict[str, Any],
    architecture_search_space: dict[str, Any],
    warm_start_state: dict[str, Any],
) -> dict[str, list[dict[str, Any]]]:
    plans: dict[str, list[dict[str, Any]]] = {}
    total_trial_cap = int(budget_contract.get("max_trials", 0) or 0)
    per_family_cap = int(budget_contract.get("per_family_trial_cap", 0) or 0)
    seed = int(budget_contract.get("seed", 42) or 42)
    used_total = 0
    for family_index, family_payload in enumerate(architecture_search_space.get("families", [])):
        family = str(family_payload.get("family", "")).strip()
        if not family:
            continue
        if used_total >= total_trial_cap:
            break
        search_space = _family_search_space(family=family)
        if not search_space:
            continue
        variant_prefix = _family_variant_prefix(family)
        warm_prior = dict(dict(warm_start_state.get("best_priors") or {}).get(family) or {})
        family_trials: list[TrialPlan] = []
        seen: set[str] = set()
        if warm_prior:
            warm_params = _normalize_hyperparameters(warm_prior.get("hyperparameters"))
            if warm_params:
                family_trials.append(
                    TrialPlan(
                        trial_id=f"{family}_trial_0001",
                        family=family,
                        variant_id=f"{variant_prefix}_warm_start",
                        source="warm_start",
                        family_loop_index=family_index,
                        hyperparameters=warm_params,
                    )
                )
                seen.add(_canonical_hyperparameters(warm_params))
        anchor = dict(search_space["default_anchor"])
        anchor_key = _canonical_hyperparameters(anchor)
        if anchor_key not in seen:
            family_trials.append(
                TrialPlan(
                    trial_id=f"{family}_trial_{len(family_trials) + 1:04d}",
                    family=family,
                    variant_id=f"{variant_prefix}_anchor",
                    source="default_anchor",
                    family_loop_index=family_index,
                    hyperparameters=anchor,
                )
            )
            seen.add(anchor_key)
        combinations = _all_parameter_combinations(search_space["parameters"])
        rng = _stable_rng(seed + family_index * 17)
        rng.shuffle(combinations)
        for params in combinations:
            if len(family_trials) >= per_family_cap or used_total + len(family_trials) >= total_trial_cap:
                break
            normalized = _normalize_hyperparameters(params)
            key = _canonical_hyperparameters(normalized)
            if key in seen:
                continue
            family_trials.append(
                TrialPlan(
                    trial_id=f"{family}_trial_{len(family_trials) + 1:04d}",
                    family=family,
                    variant_id=f"{variant_prefix}_search_{len(family_trials):04d}",
                    source="search_space",
                    family_loop_index=family_index,
                    hyperparameters=normalized,
                )
            )
            seen.add(key)
        plans[family] = [item.to_dict() for item in family_trials[:per_family_cap]]
        used_total += len(plans[family])
    return plans


def artifact_path(run_dir: str | Path, key: str) -> Path:
    return Path(run_dir) / HPO_ARTIFACT_FILENAMES[key]


def _select_hpo_families(
    *,
    requested_family: str,
    preferred_candidate_order: list[str],
    available_families: list[str],
    task_type: str,
) -> list[str]:
    available = [str(item).strip() for item in available_families if str(item).strip() in SEARCHABLE_FAMILIES]
    if requested_family != "auto" and requested_family in available:
        return [requested_family]
    ordered = [family for family in preferred_candidate_order if family in available]
    if not ordered:
        if task_type in {"binary_classification", "fraud_detection", "anomaly_detection"}:
            ordered = [family for family in ["logistic_regression", "hist_gradient_boosting_classifier", "extra_trees_classifier", "boosted_tree_classifier"] if family in available]
        elif task_type == "multiclass_classification":
            ordered = [family for family in ["hist_gradient_boosting_classifier", "extra_trees_classifier", "boosted_tree_classifier", "bagged_tree_classifier"] if family in available]
        else:
            ordered = [family for family in ["hist_gradient_boosting_ensemble", "extra_trees_ensemble", "boosted_tree_ensemble", "linear_ridge"] if family in available]
    return ordered[:3]


def _family_search_space(*, family: str) -> dict[str, Any] | None:
    spaces: dict[str, dict[str, Any]] = {
        "linear_ridge": {
            "default_anchor": {"ridge": 1e-4},
            "parameters": {"ridge": [1e-6, 1e-5, 1e-4, 1e-3, 1e-2]},
        },
        "logistic_regression": {
            "default_anchor": {"learning_rate": 0.25, "epochs": 350, "l2": 1e-4},
            "parameters": {
                "learning_rate": [0.10, 0.15, 0.20, 0.25, 0.32, 0.40],
                "epochs": [220, 300, 380, 500, 650],
                "l2": [1e-5, 5e-5, 1e-4, 1e-3, 1e-2],
            },
        },
        "bagged_tree_ensemble": {
            "default_anchor": {"n_estimators": 12, "max_depth": 4, "min_leaf": 6},
            "parameters": {
                "n_estimators": [8, 12, 16, 20, 28],
                "max_depth": [3, 4, 5, 6, 7],
                "min_leaf": [3, 4, 5, 6, 8, 10],
            },
        },
        "boosted_tree_ensemble": {
            "default_anchor": {"n_estimators": 24, "learning_rate": 0.60, "max_depth": 3, "min_leaf": 5},
            "parameters": {
                "n_estimators": [12, 16, 24, 32, 40],
                "learning_rate": [0.15, 0.25, 0.35, 0.50, 0.65],
                "max_depth": [2, 3, 4, 5],
                "min_leaf": [3, 4, 5, 6, 8],
            },
        },
        "hist_gradient_boosting_ensemble": {
            "default_anchor": {"max_iter": 180, "learning_rate": 0.08, "max_depth": 6, "min_samples_leaf": 20},
            "parameters": {
                "max_iter": [120, 180, 240, 320, 420],
                "learning_rate": [0.03, 0.05, 0.08, 0.10, 0.12],
                "max_depth": [3, 5, 6, 8, 10],
                "min_samples_leaf": [5, 10, 15, 20, 30],
            },
        },
        "extra_trees_ensemble": {
            "default_anchor": {"n_estimators": 220, "max_depth": None, "min_samples_leaf": 2},
            "parameters": {
                "n_estimators": [80, 120, 160, 220, 300],
                "max_depth": [None, 8, 12, 18, 24],
                "min_samples_leaf": [1, 2, 3, 4, 6, 8],
            },
        },
        "bagged_tree_classifier": {
            "default_anchor": {"n_estimators": 12, "max_depth": 4, "min_leaf": 6},
            "parameters": {
                "n_estimators": [8, 12, 16, 20, 28],
                "max_depth": [3, 4, 5, 6, 7],
                "min_leaf": [3, 4, 5, 6, 8, 10],
            },
        },
        "boosted_tree_classifier": {
            "default_anchor": {"n_estimators": 24, "learning_rate": 0.60, "max_depth": 3, "min_leaf": 5},
            "parameters": {
                "n_estimators": [12, 16, 24, 32, 40],
                "learning_rate": [0.15, 0.25, 0.35, 0.50, 0.65],
                "max_depth": [2, 3, 4, 5],
                "min_leaf": [3, 4, 5, 6, 8],
            },
        },
        "hist_gradient_boosting_classifier": {
            "default_anchor": {"max_iter": 220, "learning_rate": 0.08, "max_depth": 6, "min_samples_leaf": 18},
            "parameters": {
                "max_iter": [120, 180, 220, 300, 420],
                "learning_rate": [0.03, 0.05, 0.08, 0.10, 0.12],
                "max_depth": [3, 5, 6, 8, 10],
                "min_samples_leaf": [5, 10, 15, 18, 24, 30],
            },
        },
        "extra_trees_classifier": {
            "default_anchor": {"n_estimators": 220, "max_depth": None, "min_samples_leaf": 2},
            "parameters": {
                "n_estimators": [80, 120, 160, 220, 300],
                "max_depth": [None, 8, 12, 18, 24],
                "min_samples_leaf": [1, 2, 3, 4, 6, 8],
            },
        },
    }
    return spaces.get(family)


def _all_parameter_combinations(parameters: dict[str, list[Any]]) -> list[dict[str, Any]]:
    keys = [str(key) for key in parameters.keys()]
    values = [list(parameters[key]) for key in keys]
    combos: list[dict[str, Any]] = []
    for parts in itertools.product(*values):
        combos.append({key: value for key, value in zip(keys, parts, strict=False)})
    return combos


def _normalize_hyperparameters(payload: dict[str, Any] | None) -> dict[str, Any]:
    normalized: dict[str, Any] = {}
    for key, value in dict(payload or {}).items():
        if key.startswith("training_") or key in {"class_count", "decision_threshold"}:
            continue
        if isinstance(value, float):
            normalized[str(key)] = float(value)
        elif isinstance(value, bool):
            normalized[str(key)] = bool(value)
        elif isinstance(value, int):
            normalized[str(key)] = int(value)
        elif value is None:
            normalized[str(key)] = None
    return normalized


def _canonical_hyperparameters(payload: dict[str, Any]) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _family_variant_prefix(family: str) -> str:
    mapping = {
        "linear_ridge": "linear",
        "logistic_regression": "logistic",
        "bagged_tree_ensemble": "bagged",
        "boosted_tree_ensemble": "boosted",
        "hist_gradient_boosting_ensemble": "hist",
        "extra_trees_ensemble": "extra",
        "bagged_tree_classifier": "bagged_classifier",
        "boosted_tree_classifier": "boosted_classifier",
        "hist_gradient_boosting_classifier": "hist_classifier",
        "extra_trees_classifier": "extra_classifier",
    }
    return mapping.get(family, family.replace("_ensemble", "").replace("_classifier", "_classifier"))


def _read_budget_max_trials(root: Path) -> int:
    budget_path = root / "budget_contract.json"
    if not budget_path.exists():
        return 18
    try:
        payload = json.loads(budget_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return 18
    try:
        return max(6, min(32, int(payload.get("max_trials", 18) or 18)))
    except (TypeError, ValueError):
        return 18


def _rank_key(metrics: Any) -> tuple[float, ...]:
    payload = dict(metrics or {})
    if "mae" in payload:
        return (
            float(payload.get("mae", float("inf"))),
            float(payload.get("rmse", float("inf"))),
        )
    return (
        -float(payload.get("pr_auc", payload.get("f1", 0.0)) or 0.0),
        -float(payload.get("recall", payload.get("f1", 0.0)) or 0.0),
        -float(payload.get("f1", 0.0) or 0.0),
        float(payload.get("log_loss", float("inf"))),
    )


def _stable_rng(seed: int) -> Any:
    import random

    return random.Random(seed)


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()
