"""Bounded HPO planning and artifact helpers for Slice 15C."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import itertools
import json
from pathlib import Path
from typing import Any

from relaytic.core.search_budget_profiles import get_search_budget_profile, resolve_search_budget_profile


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
    "catboost_ensemble",
    "xgboost_ensemble",
    "lightgbm_ensemble",
    "bagged_tree_classifier",
    "boosted_tree_classifier",
    "hist_gradient_boosting_classifier",
    "extra_trees_classifier",
    "catboost_classifier",
    "xgboost_classifier",
    "lightgbm_classifier",
}


@dataclass(frozen=True)
class TrialPlan:
    trial_id: str
    family: str
    variant_id: str
    stage: str
    source: str
    family_loop_index: int
    hyperparameters: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "trial_id": self.trial_id,
            "family": self.family,
            "variant_id": self.variant_id,
            "stage": self.stage,
            "source": self.source,
            "family_loop_index": self.family_loop_index,
            "hyperparameters": dict(self.hyperparameters),
        }


def derive_hpo_budget_contract(
    *,
    run_dir: str | Path,
    task_type: str,
    row_count: int,
    class_count: int | None = None,
    minority_fraction: float | None = None,
    requested_family: str,
    preferred_candidate_order: list[str] | None,
    available_families: list[str],
    search_budget_profile: str | None = None,
) -> dict[str, Any]:
    root = Path(run_dir)
    preferred = [str(item).strip() for item in preferred_candidate_order or [] if str(item).strip()]
    budget_profile = _resolve_hpo_budget_profile(search_budget_profile)
    selected_families = _select_hpo_families(
        requested_family=requested_family,
        preferred_candidate_order=preferred,
        available_families=available_families,
        task_type=task_type,
        budget_profile=budget_profile,
        class_count=class_count,
        minority_fraction=minority_fraction,
    )
    profile_contract = get_search_budget_profile(budget_profile)
    family_count = max(1, len(selected_families))
    multiclass_active = bool(task_type == "multiclass_classification" and int(class_count or 0) >= 3)
    rare_event_profile_active = _rare_event_profile_active(task_type=task_type, minority_fraction=minority_fraction)
    specialization_profile = (
        "multiclass_broadened"
        if multiclass_active
        else "rare_event_imbalance_aware"
        if rare_event_profile_active
        else "generic"
    )
    race_family_count = _race_family_count(
        profile=budget_profile,
        family_count=family_count,
        multiclass_active=multiclass_active,
        rare_event_profile_active=rare_event_profile_active,
    )
    finalist_family_count = _finalist_family_count(
        profile=budget_profile,
        family_count=family_count,
        multiclass_active=multiclass_active,
        rare_event_profile_active=rare_event_profile_active,
    )
    probe_trials_per_family = int(profile_contract["probe_trials_per_family"])
    race_trials_per_family = int(profile_contract["race_trials_per_family"])
    finalist_followup_trials = int(profile_contract["finalist_followup_trials"])
    post_fit_trials = int(profile_contract["post_fit_trials"])
    stage_target_trials = (
        family_count * probe_trials_per_family
        + race_family_count * race_trials_per_family
        + finalist_family_count * finalist_followup_trials
    )
    profile_max_trials = int(profile_contract["max_trials"])
    budget_cap = _read_budget_max_trials(root, fallback=profile_max_trials)
    max_trials = min(budget_cap, profile_max_trials, stage_target_trials)
    if max_trials < family_count:
        max_trials = family_count
    default_seconds = _max_wall_clock_seconds(
        profile=budget_profile,
        row_count=row_count,
        task_type=task_type,
        multiclass_active=multiclass_active,
        rare_event_profile_active=rare_event_profile_active,
    )
    family_count = max(1, len(selected_families))
    per_family_trial_cap = max(
        1,
        min(
            probe_trials_per_family + race_trials_per_family + finalist_followup_trials,
            max_trials,
        ),
    )
    max_family_loops = max(2, min(family_count, 4))
    payload = {
        "schema_version": HPO_BUDGET_CONTRACT_SCHEMA_VERSION,
        "generated_at": _utc_now(),
        "status": "ok",
        "backend": "deterministic_local_search",
        "seed": 42,
        "budget_profile": budget_profile,
        "task_type": str(task_type),
        "class_count": int(class_count or 0),
        "minority_class_fraction": minority_fraction,
        "specialization_profile": specialization_profile,
        "multiclass_widening_active": multiclass_active,
        "rare_event_profile_active": rare_event_profile_active,
        "row_count": int(max(row_count, 0)),
        "requested_family": str(requested_family or "auto"),
        "selected_families": selected_families,
        "max_trials": int(max_trials),
        "max_wall_clock_seconds": int(default_seconds),
        "per_family_trial_cap": int(per_family_trial_cap),
        "max_family_loops": int(max_family_loops),
        "probe_trials_per_family": probe_trials_per_family,
        "race_trials_per_family": race_trials_per_family,
        "finalist_followup_trials": finalist_followup_trials,
        "post_fit_trials": post_fit_trials,
        "probe_family_count": family_count,
        "race_family_count": race_family_count,
        "finalist_family_count": finalist_family_count,
        "stage_trial_target": int(stage_target_trials),
        "plateau_patience": 1 if budget_profile == "test" else 2,
        "min_trials_before_plateau_stop": 3,
        "min_improvement_delta": 0.0005,
        "warm_start_enabled": True,
        "summary": (
            f"Relaytic will run staged portfolio search with `{budget_profile}` budget: probe `{family_count}` family(s), "
            f"race `{race_family_count}`, deepen `{finalist_family_count}`, and spend up to `{max_trials}` total model trial(s) "
            f"under `{specialization_profile}` specialization."
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
    portfolio_plan: dict[str, Any] | None = None,
) -> dict[str, list[dict[str, Any]]]:
    plans: dict[str, list[dict[str, Any]]] = {}
    seed = int(budget_contract.get("seed", 42) or 42)
    effective_portfolio_plan = portfolio_plan or build_portfolio_search_plan(
        budget_contract=budget_contract,
        architecture_search_space=architecture_search_space,
        warm_start_state=warm_start_state,
    )
    for family_index, family_row in enumerate(effective_portfolio_plan.get("families", [])):
        family = str(family_row.get("family", "")).strip()
        stage_slots = [str(item) for item in family_row.get("stage_slots", []) if str(item).strip()]
        if not family or not stage_slots:
            continue
        search_space = _family_search_space(family=family)
        if not search_space:
            continue
        variant_prefix = _family_variant_prefix(family)
        warm_prior = dict(dict(warm_start_state.get("best_priors") or {}).get(family) or {})
        family_trials: list[TrialPlan] = []
        seen: set[str] = set()
        if warm_prior and stage_slots:
            warm_params = _normalize_hyperparameters(warm_prior.get("hyperparameters"))
            if warm_params:
                current_stage = stage_slots.pop(0)
                family_trials.append(
                    TrialPlan(
                        trial_id=f"{family}_trial_0001",
                        family=family,
                        variant_id=f"{variant_prefix}_warm_start",
                        stage=current_stage,
                        source="warm_start",
                        family_loop_index=family_index,
                        hyperparameters=warm_params,
                    )
                )
                seen.add(_canonical_hyperparameters(warm_params))
        if not stage_slots:
            plans[family] = [item.to_dict() for item in family_trials]
            continue
        anchor = dict(search_space["default_anchor"])
        anchor_key = _canonical_hyperparameters(anchor)
        if anchor_key not in seen:
            current_stage = stage_slots.pop(0)
            family_trials.append(
                TrialPlan(
                    trial_id=f"{family}_trial_{len(family_trials) + 1:04d}",
                    family=family,
                    variant_id=f"{variant_prefix}_anchor",
                    stage=current_stage,
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
            if not stage_slots:
                break
            normalized = _normalize_hyperparameters(params)
            key = _canonical_hyperparameters(normalized)
            if key in seen:
                continue
            current_stage = stage_slots.pop(0)
            family_trials.append(
                TrialPlan(
                    trial_id=f"{family}_trial_{len(family_trials) + 1:04d}",
                    family=family,
                    variant_id=f"{variant_prefix}_search_{len(family_trials):04d}",
                    stage=current_stage,
                    source="search_space",
                    family_loop_index=family_index,
                    hyperparameters=normalized,
                )
            )
            seen.add(key)
        plans[family] = [item.to_dict() for item in family_trials]
    return plans


def build_portfolio_search_plan(
    *,
    budget_contract: dict[str, Any],
    architecture_search_space: dict[str, Any],
    warm_start_state: dict[str, Any],
) -> dict[str, Any]:
    selected_families = [
        str(item.get("family", "")).strip()
        for item in architecture_search_space.get("families", [])
        if isinstance(item, dict) and str(item.get("family", "")).strip()
    ]
    warm_priors = dict(warm_start_state.get("best_priors") or {})
    ranked = sorted(
        (
            (
                index - (0.25 if family in warm_priors else 0.0),
                family,
            )
            for index, family in enumerate(selected_families)
        ),
        key=lambda item: (item[0], item[1]),
    )
    ordered_families = [family for _, family in ranked]
    race_family_count = min(len(ordered_families), int(budget_contract.get("race_family_count", 0) or 0))
    finalist_family_count = min(race_family_count, int(budget_contract.get("finalist_family_count", 0) or 0))
    racing_families = ordered_families[:race_family_count]
    finalists = racing_families[:finalist_family_count]
    probe_trials_per_family = int(budget_contract.get("probe_trials_per_family", 1) or 1)
    race_trials_per_family = int(budget_contract.get("race_trials_per_family", 0) or 0)
    finalist_followup_trials = int(budget_contract.get("finalist_followup_trials", 0) or 0)
    post_fit_trials = int(budget_contract.get("post_fit_trials", 0) or 0)
    budget_profile = str(budget_contract.get("budget_profile", "operator") or "operator")

    families: list[dict[str, Any]] = []
    skipped_deeper_work: list[str] = []
    for index, family in enumerate(ordered_families, start=1):
        stage_slots = ["probe"] * probe_trials_per_family
        promotion_reason = "selected_by_probe_order"
        prune_reason = None
        if family in racing_families:
            stage_slots.extend(["race"] * race_trials_per_family)
            promotion_reason = "probe_survivor"
        else:
            prune_reason = "probe_budget_priority"
            skipped_deeper_work.append(f"`{family}` stopped after probe because deeper budget was reserved for higher-priority families.")
        if family in finalists:
            stage_slots.extend(["finalist"] * finalist_followup_trials)
            promotion_reason = "race_survivor"
        elif family in racing_families:
            prune_reason = "outscored_by_finalist_priority"
            skipped_deeper_work.append(f"`{family}` raced but did not receive finalist follow-up budget.")
        if budget_profile in {"test", "low_budget"} and family not in finalists:
            skipped_deeper_work.append(f"`{family}` stayed on the lean `{budget_profile}` profile and skipped deeper finalist work.")
        families.append(
            {
                "family": family,
                "rank": index,
                "warm_start_hint": family in warm_priors,
                "probe_trials": probe_trials_per_family,
                "race_trials": race_trials_per_family if family in racing_families else 0,
                "finalist_followup_trials": finalist_followup_trials if family in finalists else 0,
                "post_fit_trials": post_fit_trials if family in finalists else 0,
                "promotion_reason": promotion_reason,
                "prune_reason": prune_reason,
                "stage_slots": stage_slots,
                "stage_trial_count": len(stage_slots),
            }
        )

    return {
        "status": "ok" if families else "not_applicable",
        "budget_profile": budget_profile,
        "families": families,
        "racing_families": racing_families,
        "finalists": finalists,
        "warm_start_influenced_families": [family for family in ordered_families if family in warm_priors],
        "skipped_deeper_work": skipped_deeper_work,
        "summary": (
            f"Relaytic staged search across `{len(families)}` family(s), raced `{len(racing_families)}`, and kept `{len(finalists)}` finalist(s)."
            if families
            else "Relaytic found no staged portfolio search work to plan."
        ),
    }


def artifact_path(run_dir: str | Path, key: str) -> Path:
    return Path(run_dir) / HPO_ARTIFACT_FILENAMES[key]


def _select_hpo_families(
    *,
    requested_family: str,
    preferred_candidate_order: list[str],
    available_families: list[str],
    task_type: str,
    budget_profile: str,
    class_count: int | None = None,
    minority_fraction: float | None = None,
) -> list[str]:
    available = [str(item).strip() for item in available_families if str(item).strip() in SEARCHABLE_FAMILIES]
    if requested_family != "auto" and requested_family in available:
        return [requested_family]
    ordered = [family for family in preferred_candidate_order if family in available]
    multiclass_active = bool(task_type == "multiclass_classification" and int(class_count or 0) >= 3)
    rare_event_profile_active = _rare_event_profile_active(task_type=task_type, minority_fraction=minority_fraction)
    if not ordered:
        if multiclass_active:
            ordered = [
                family
                for family in [
                    "catboost_classifier",
                    "hist_gradient_boosting_classifier",
                    "extra_trees_classifier",
                    "xgboost_classifier",
                    "lightgbm_classifier",
                    "tabpfn_classifier",
                    "boosted_tree_classifier",
                    "bagged_tree_classifier",
                ]
                if family in available
            ]
        elif rare_event_profile_active or task_type in {"binary_classification", "fraud_detection", "anomaly_detection"}:
            ordered = [
                family
                for family in [
                    "catboost_classifier",
                    "hist_gradient_boosting_classifier",
                    "xgboost_classifier",
                    "lightgbm_classifier",
                    "extra_trees_classifier",
                    "boosted_tree_classifier",
                    "bagged_tree_classifier",
                    "logistic_regression",
                ]
                if family in available
            ]
        else:
            ordered = [
                family
                for family in [
                    "catboost_ensemble",
                    "hist_gradient_boosting_ensemble",
                    "extra_trees_ensemble",
                    "xgboost_ensemble",
                    "lightgbm_ensemble",
                    "boosted_tree_ensemble",
                    "linear_ridge",
                ]
                if family in available
            ]
    family_cap = 2 if budget_profile == "test" else (3 if budget_profile == "low_budget" else 4)
    if budget_profile in {"operator", "benchmark"} and (multiclass_active or rare_event_profile_active):
        family_cap += 1
    return ordered[:family_cap]


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
        "catboost_ensemble": {
            "default_anchor": {"depth": 6, "iterations": 220, "learning_rate": 0.06},
            "parameters": {
                "depth": [4, 6, 8],
                "iterations": [160, 220, 320],
                "learning_rate": [0.03, 0.06, 0.10],
            },
        },
        "xgboost_ensemble": {
            "default_anchor": {
                "n_estimators": 240,
                "max_depth": 6,
                "learning_rate": 0.06,
                "subsample": 0.9,
                "colsample_bytree": 0.9,
            },
            "parameters": {
                "n_estimators": [160, 240, 320],
                "max_depth": [4, 6, 8],
                "learning_rate": [0.03, 0.06, 0.10],
                "subsample": [0.8, 0.9, 1.0],
                "colsample_bytree": [0.8, 0.9, 1.0],
            },
        },
        "lightgbm_ensemble": {
            "default_anchor": {
                "n_estimators": 240,
                "learning_rate": 0.06,
                "num_leaves": 31,
                "min_child_samples": 20,
            },
            "parameters": {
                "n_estimators": [160, 240, 320],
                "learning_rate": [0.03, 0.06, 0.10],
                "num_leaves": [31, 63, 127],
                "min_child_samples": [10, 20, 30],
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
        "catboost_classifier": {
            "default_anchor": {"depth": 6, "iterations": 220, "learning_rate": 0.06},
            "parameters": {
                "depth": [4, 6, 8],
                "iterations": [160, 220, 320],
                "learning_rate": [0.03, 0.06, 0.10],
            },
        },
        "xgboost_classifier": {
            "default_anchor": {
                "n_estimators": 240,
                "max_depth": 6,
                "learning_rate": 0.06,
                "subsample": 0.9,
                "colsample_bytree": 0.9,
            },
            "parameters": {
                "n_estimators": [160, 240, 320],
                "max_depth": [4, 6, 8],
                "learning_rate": [0.03, 0.06, 0.10],
                "subsample": [0.8, 0.9, 1.0],
                "colsample_bytree": [0.8, 0.9, 1.0],
            },
        },
        "lightgbm_classifier": {
            "default_anchor": {
                "n_estimators": 240,
                "learning_rate": 0.06,
                "num_leaves": 31,
                "min_child_samples": 20,
            },
            "parameters": {
                "n_estimators": [160, 240, 320],
                "learning_rate": [0.03, 0.06, 0.10],
                "num_leaves": [31, 63, 127],
                "min_child_samples": [10, 20, 30],
            },
        },
    }
    return spaces.get(family)


def _all_parameter_combinations(parameters: dict[str, list[Any]]) -> list[dict[str, Any]]:
    keys = [str(key) for key in parameters.keys()]
    values = [list(parameters[key]) for key in keys]
    combos: list[dict[str, Any]] = []
    for parts in itertools.product(*values):
        combos.append({key: value for key, value in zip(keys, parts)})
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
        "catboost_ensemble": "catboost",
        "xgboost_ensemble": "xgboost",
        "lightgbm_ensemble": "lightgbm",
        "bagged_tree_classifier": "bagged_classifier",
        "boosted_tree_classifier": "boosted_classifier",
        "hist_gradient_boosting_classifier": "hist_classifier",
        "extra_trees_classifier": "extra_classifier",
        "catboost_classifier": "catboost_classifier",
        "xgboost_classifier": "xgboost_classifier",
        "lightgbm_classifier": "lightgbm_classifier",
    }
    return mapping.get(family, family.replace("_ensemble", "").replace("_classifier", "_classifier"))


def _read_budget_max_trials(root: Path, *, fallback: int) -> int:
    budget_path = root / "budget_contract.json"
    if not budget_path.exists():
        return fallback
    try:
        payload = json.loads(budget_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return fallback
    try:
        return max(6, min(2000, int(payload.get("max_trials", fallback) or fallback)))
    except (TypeError, ValueError):
        return fallback


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


def _resolve_hpo_budget_profile(search_budget_profile: str | None) -> str:
    if search_budget_profile:
        configured = str(search_budget_profile).strip().lower()
        if configured in {"operator", "benchmark", "low_budget", "test"}:
            return configured
    return resolve_search_budget_profile({}, default="operator")


def _race_family_count(
    *,
    profile: str,
    family_count: int,
    multiclass_active: bool = False,
    rare_event_profile_active: bool = False,
) -> int:
    if family_count <= 1:
        return family_count
    if profile == "test":
        return min(family_count, 2)
    if profile == "low_budget":
        return min(family_count, 2)
    cap = 3
    if profile == "benchmark":
        cap = 4 if (multiclass_active or rare_event_profile_active) else 3
    elif multiclass_active or rare_event_profile_active:
        cap = 4
    return min(family_count, cap)


def _finalist_family_count(
    *,
    profile: str,
    family_count: int,
    multiclass_active: bool = False,
    rare_event_profile_active: bool = False,
) -> int:
    if family_count <= 1:
        return family_count
    if profile in {"test", "low_budget"}:
        return 1
    cap = 3 if (multiclass_active or rare_event_profile_active) else 2
    return min(family_count, cap)


def _max_wall_clock_seconds(
    *,
    profile: str,
    row_count: int,
    task_type: str,
    multiclass_active: bool = False,
    rare_event_profile_active: bool = False,
) -> int:
    base = {
        "test": 25,
        "low_budget": 50,
        "operator": 110,
        "benchmark": 180,
    }.get(profile, 110)
    if row_count > 5000:
        base += 25
    if task_type in {"multiclass_classification", "fraud_detection", "anomaly_detection"}:
        base += 10
    if multiclass_active:
        base += 10
    if rare_event_profile_active:
        base += 10
    return base


def _rare_event_profile_active(*, task_type: str, minority_fraction: float | None) -> bool:
    return bool(
        task_type in {"fraud_detection", "anomaly_detection"}
        or (minority_fraction is not None and float(minority_fraction) <= 0.20)
    )


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()
