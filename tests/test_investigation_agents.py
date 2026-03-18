import csv
from pathlib import Path

from relaytic.context import (
    build_context_controls_from_policy,
    default_data_origin,
    default_domain_brief,
    default_task_brief,
)
from relaytic.investigation import run_investigation
from relaytic.mandate import (
    build_mandate_controls_from_policy,
    build_run_brief,
    build_work_preferences,
    default_lab_mandate,
)
from relaytic.policies import load_policy


def _write_regression_dataset(path: Path) -> Path:
    rows = [
        ["timestamp", "line_id", "batch_id", "sensor_a", "sensor_b", "quality_score", "future_quality"],
        ["2025-01-01T00:00:00", "L1", "B001", 10.0, 100.0, 0.50, 0.60],
        ["2025-01-01T00:01:00", "L1", "B002", 11.0, 101.0, 0.52, 0.61],
        ["2025-01-01T00:02:00", "L2", "B003", 12.0, 102.0, 0.55, 0.64],
        ["2025-01-01T00:03:00", "L2", "B004", 13.0, "", 0.57, 0.66],
        ["2025-01-01T00:04:00", "L1", "B005", 14.0, 104.0, 0.60, 0.68],
        ["2025-01-01T00:05:00", "L1", "B006", 15.0, 105.0, 0.62, 0.70],
        ["2025-01-01T00:06:00", "L2", "B007", 16.0, 106.0, 0.65, 0.73],
        ["2025-01-01T00:07:00", "L2", "B008", 17.0, 107.0, 0.67, 0.75],
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerows(rows)
    return path


def _write_fraud_dataset(path: Path) -> Path:
    rows = [["transaction_id", "amount_norm", "device_risk", "velocity_score", "fraud_flag"]]
    for index in range(24):
        fraud = 1 if index % 7 == 0 else 0
        amount = 0.9 if fraud else 0.2 + (index % 5) * 0.05
        device_risk = 0.95 if fraud else 0.15 + (index % 4) * 0.04
        velocity = 0.88 if fraud else 0.2 + (index % 3) * 0.06
        rows.append([f"T{index:04d}", round(amount, 5), round(device_risk, 5), round(velocity, 5), fraud])
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerows(rows)
    return path


def _build_foundation(policy: dict, *, target_column: str) -> tuple[dict, dict]:
    mandate_controls = build_mandate_controls_from_policy(policy)
    context_controls = build_context_controls_from_policy(policy)
    mandate_bundle = {
        "lab_mandate": default_lab_mandate(mandate_controls).to_dict(),
        "work_preferences": build_work_preferences(mandate_controls, policy=policy).to_dict(),
        "run_brief": build_run_brief(
            mandate_controls,
            policy=policy,
            objective="best_robust_pareto_front",
            target_column=target_column,
            success_criteria=["Reduce scrap and bad downstream decisions."],
            binding_constraints=["Do not use post-outcome features."],
        ).to_dict(),
    }
    context_bundle = {
        "data_origin": default_data_origin(
            context_controls,
            source_name="pilot_line",
            source_type="historical_snapshot",
        ).to_dict(),
        "domain_brief": default_domain_brief(
            context_controls,
            system_name="distillation_line",
            summary="Predict quality drift early enough to intervene before scrap is created.",
            forbidden_features=["future_quality"],
        ).to_dict(),
        "task_brief": default_task_brief(
            context_controls,
            problem_statement="Predict quality score from upstream sensors.",
            target_column=target_column,
            success_criteria=["Reduce off-spec production."],
            failure_costs=["Late detection causes scrap and wasted operator time."],
        ).to_dict(),
    }
    return mandate_bundle, context_bundle


def test_run_investigation_produces_slice03_bundle(tmp_path: Path) -> None:
    data_path = _write_regression_dataset(tmp_path / "quality.csv")
    policy = load_policy().policy
    mandate_bundle, context_bundle = _build_foundation(policy, target_column="quality_score")

    bundle = run_investigation(
        data_path=str(data_path),
        policy=policy,
        mandate_bundle=mandate_bundle,
        context_bundle=context_bundle,
    )

    assert bundle.dataset_profile.data_mode == "time_series"
    assert "future_quality" in bundle.dataset_profile.suspicious_columns
    assert "batch_id" in bundle.dataset_profile.hidden_key_candidates
    assert bundle.domain_memo.target_candidates[0]["target_column"] == "quality_score"
    assert bundle.focus_profile.primary_objective in {"accuracy", "value", "reliability"}
    assert bundle.optimization_profile.split_strategy_bias == "blocked_time_order_70_15_15"
    assert "future_quality" in bundle.feature_strategy_profile.excluded_columns


def test_run_investigation_activates_value_and_reliability_lenses(tmp_path: Path) -> None:
    data_path = _write_regression_dataset(tmp_path / "value_focus.csv")
    policy = load_policy().policy
    mandate_bundle, context_bundle = _build_foundation(policy, target_column="quality_score")

    bundle = run_investigation(
        data_path=str(data_path),
        policy=policy,
        mandate_bundle=mandate_bundle,
        context_bundle=context_bundle,
    )

    assert "value" in bundle.focus_profile.active_lenses
    assert "reliability" in bundle.focus_profile.active_lenses
    assert bundle.focus_debate.resolution["primary_objective"] == bundle.focus_profile.primary_objective


def test_run_investigation_applies_expert_priors_for_fraud_like_use_cases(tmp_path: Path) -> None:
    data_path = _write_fraud_dataset(tmp_path / "fraud.csv")
    policy = load_policy().policy
    mandate_bundle, context_bundle = _build_foundation(policy, target_column="fraud_flag")
    context_bundle["task_brief"]["problem_statement"] = "Detect fraudulent transactions before approval."
    context_bundle["task_brief"]["task_type_hint"] = "fraud_detection"
    context_bundle["task_brief"]["domain_archetype_hint"] = "fraud_risk"
    context_bundle["domain_brief"]["summary"] = "Score transaction fraud risk for payment review."

    bundle = run_investigation(
        data_path=str(data_path),
        policy=policy,
        mandate_bundle=mandate_bundle,
        context_bundle=context_bundle,
    )

    assert bundle.domain_memo.domain_archetype == "fraud_risk"
    assert bundle.domain_memo.target_candidates[0]["task_type"] == "fraud_detection"
    assert bundle.domain_memo.expert_priors["recommended_primary_metric"] == "pr_auc"
    assert "group_history_features" in bundle.feature_strategy_profile.preferred_feature_families
    assert bundle.optimization_profile.primary_metric == "pr_auc"
