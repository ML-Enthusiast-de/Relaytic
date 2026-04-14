"""Shared staged search-budget profiles for portfolio search and HPO."""

from __future__ import annotations

import os
from typing import Any


SEARCH_BUDGET_PROFILE_DEFAULTS: dict[str, dict[str, int | str]] = {
    "operator": {
        "profile": "operator",
        "max_trials": 240,
        "light_hpo_trials": 12,
        "medium_hpo_trials": 36,
        "deep_hpo_trials": 72,
        "probe_trials_per_family": 2,
        "race_trials_per_family": 4,
        "finalist_followup_trials": 8,
        "post_fit_trials": 4,
        "max_search_branches": 4,
        "max_branch_widen": 2,
    },
    "benchmark": {
        "profile": "benchmark",
        "max_trials": 360,
        "light_hpo_trials": 18,
        "medium_hpo_trials": 54,
        "deep_hpo_trials": 108,
        "probe_trials_per_family": 3,
        "race_trials_per_family": 6,
        "finalist_followup_trials": 12,
        "post_fit_trials": 6,
        "max_search_branches": 5,
        "max_branch_widen": 3,
    },
    "low_budget": {
        "profile": "low_budget",
        "max_trials": 48,
        "light_hpo_trials": 6,
        "medium_hpo_trials": 12,
        "deep_hpo_trials": 18,
        "probe_trials_per_family": 1,
        "race_trials_per_family": 2,
        "finalist_followup_trials": 4,
        "post_fit_trials": 2,
        "max_search_branches": 3,
        "max_branch_widen": 2,
    },
    "test": {
        "profile": "test",
        "max_trials": 20,
        "light_hpo_trials": 4,
        "medium_hpo_trials": 8,
        "deep_hpo_trials": 12,
        "probe_trials_per_family": 1,
        "race_trials_per_family": 2,
        "finalist_followup_trials": 3,
        "post_fit_trials": 1,
        "max_search_branches": 3,
        "max_branch_widen": 2,
    },
}


def resolve_search_budget_profile(policy: dict[str, Any] | None, *, default: str = "operator") -> str:
    payload = dict(policy or {})
    search_cfg = dict(payload.get("search", {}))
    benchmark_cfg = dict(payload.get("benchmark", {}))
    configured = str(search_cfg.get("budget_profile", "")).strip().lower()
    if configured in SEARCH_BUDGET_PROFILE_DEFAULTS:
        return configured
    env_profile = str(os.getenv("RELAYTIC_SEARCH_BUDGET_PROFILE", "")).strip().lower()
    if env_profile in SEARCH_BUDGET_PROFILE_DEFAULTS:
        return env_profile
    if bool(search_cfg.get("low_budget_mode")):
        return "low_budget"
    if bool(benchmark_cfg.get("enabled")) or str(search_cfg.get("mode", "")).strip().lower() == "benchmark":
        return "benchmark"
    return default if default in SEARCH_BUDGET_PROFILE_DEFAULTS else "operator"


def get_search_budget_profile(profile: str) -> dict[str, int | str]:
    resolved = str(profile or "operator").strip().lower()
    selected = SEARCH_BUDGET_PROFILE_DEFAULTS.get(resolved) or SEARCH_BUDGET_PROFILE_DEFAULTS["operator"]
    return dict(selected)
