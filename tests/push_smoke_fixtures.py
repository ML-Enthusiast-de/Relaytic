from __future__ import annotations

import shutil
from pathlib import Path

import pandas as pd
import pytest

from relaytic.core.json_utils import write_json
from relaytic.policies import load_policy
from relaytic.runs.summary import materialize_run_summary
from relaytic.runtime import ensure_runtime_initialized, record_stage_completion, record_stage_start


def _write_push_smoke_binary_dataset(path: Path) -> Path:
    rows: list[dict[str, float | int]] = []
    for idx in range(48):
        feature_a = round(idx / 47.0, 5)
        feature_b = idx % 4
        feature_c = round(((idx * 3) % 11) / 10.0, 5)
        feature_d = round(((idx * 5) % 13) / 12.0, 5)
        target = int(feature_a > 0.57 or feature_b in {0, 1} or (feature_c + feature_d) > 1.4)
        rows.append(
            {
                "feature_a": feature_a,
                "feature_b": feature_b,
                "feature_c": feature_c,
                "feature_d": feature_d,
                "target_flag": target,
            }
        )
    pd.DataFrame(rows).to_csv(path, index=False)
    return path


def _write_seed_artifacts(run_dir: Path, data_path: Path) -> None:
    reports_dir = run_dir / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)

    write_json(run_dir / "manifest.json", {"run_id": "push_smoke_run"}, indent=2, ensure_ascii=False, sort_keys=True)
    write_json(
        run_dir / "dataset_profile.json",
        {
            "row_count": 48,
            "column_count": 5,
            "target_column": "target_flag",
            "data_mode": "steady_state",
            "source_type": "snapshot",
        },
        indent=2,
        ensure_ascii=False,
        sort_keys=True,
    )
    write_json(
        run_dir / "focus_profile.json",
        {
            "primary_objective": "accuracy",
            "secondary_objectives": ["reliability", "calibration"],
            "resolution_mode": "multi_objective_blend",
        },
        indent=2,
        ensure_ascii=False,
        sort_keys=True,
    )
    write_json(
        run_dir / "optimization_profile.json",
        {
            "primary_metric": "f1",
            "split_strategy_bias": "stratified_deterministic_modulo_70_15_15",
            "search_budget_posture": "standard",
        },
        indent=2,
        ensure_ascii=False,
        sort_keys=True,
    )
    write_json(
        run_dir / "plan.json",
        {
            "selected_route_id": "calibrated_tabular_classifier_route",
            "selected_route_title": "Calibrated tabular classifier route",
            "target_column": "target_flag",
            "task_type": "binary_classification",
            "primary_metric": "f1",
            "split_strategy": "stratified_deterministic_modulo_70_15_15",
            "builder_handoff": {
                "selected_model_family": "boosted_tree_classifier",
                "data_references": [str(data_path)],
                "feature_columns": ["feature_a", "feature_b", "feature_c", "feature_d"],
            },
        },
        indent=2,
        ensure_ascii=False,
        sort_keys=True,
    )
    write_json(
        run_dir / "model_metrics.json",
        {
            "selected_model_family": "boosted_tree_classifier",
            "best_validation_model_family": "boosted_tree_classifier",
            "selected_metrics": {
                "validation": {
                    "f1": 0.78,
                    "pr_auc": 0.91,
                    "log_loss": 0.24,
                },
                "test": {
                    "f1": 0.74,
                    "pr_auc": 0.89,
                    "log_loss": 0.27,
                },
            },
        },
        indent=2,
        ensure_ascii=False,
        sort_keys=True,
    )
    write_json(
        run_dir / "belief_update.json",
        {
            "provisional_recommendation": "hold_current_route",
            "readiness_level": "conditional",
            "challenger_winner": "champion",
            "updated_belief": "The current route is competitive, but operator review remains appropriate.",
        },
        indent=2,
        ensure_ascii=False,
        sort_keys=True,
    )
    write_json(
        run_dir / "completion_decision.json",
        {
            "action": "request_operator_review",
            "confidence": "medium",
            "current_stage": "completion_reviewed",
            "blocking_layer": "review_gate",
            "mandate_alignment": "resolved",
            "complete_for_mode": False,
        },
        indent=2,
        ensure_ascii=False,
        sort_keys=True,
    )
    write_json(
        run_dir / "next_action_queue.json",
        {
            "actions": [
                {"action_id": "request_operator_review", "summary": "Confirm the current route."},
                {"action_id": "same_data", "summary": "Continue on the same data if approved."},
            ]
        },
        indent=2,
        ensure_ascii=False,
        sort_keys=True,
    )
    write_json(
        run_dir / "memory_retrieval.json",
        {
            "status": "retrieval_completed",
            "analog_count": 2,
            "top_analog_run_ids": ["analog_a", "analog_b"],
        },
        indent=2,
        ensure_ascii=False,
        sort_keys=True,
    )
    write_json(
        run_dir / "route_prior_context.json",
        {
            "route_prior_applied": True,
            "preferred_challenger_family": "extra_trees_classifier",
        },
        indent=2,
        ensure_ascii=False,
        sort_keys=True,
    )
    write_json(
        run_dir / "benchmark_parity_report.json",
        {
            "parity_status": "meets_or_exceeds_reference",
            "recommended_action": "hold_current_route",
            "comparison_metric": "pr_auc",
            "winning_family": "hist_gradient_boosting_classifier",
            "reference_count": 2,
            "incumbent_present": False,
            "incumbent_name": None,
            "beat_target_state": "not_configured",
            "paper_status": "ok",
        },
        indent=2,
        ensure_ascii=False,
        sort_keys=True,
    )
    write_json(
        run_dir / "benchmark_gap_report.json",
        {
            "test_gap": 0.01,
            "validation_gap": 0.02,
            "near_parity": True,
        },
        indent=2,
        ensure_ascii=False,
        sort_keys=True,
    )
    write_json(
        run_dir / "reference_approach_matrix.json",
        {
            "rows": [
                {"family": "relaytic_boosted_tree", "role": "relaytic", "pr_auc": 0.89},
                {"family": "hist_gradient_boosting_classifier", "role": "reference", "pr_auc": 0.90},
            ]
        },
        indent=2,
        ensure_ascii=False,
        sort_keys=True,
    )
    write_json(
        run_dir / "paper_benchmark_manifest.json",
        {"status": "ok", "claim_boundary_count": 2},
        indent=2,
        ensure_ascii=False,
        sort_keys=True,
    )
    write_json(
        run_dir / "rerun_variance_report.json",
        {"matching_run_count": 1, "stability_band": "single_run_only"},
        indent=2,
        ensure_ascii=False,
        sort_keys=True,
    )
    write_json(
        run_dir / "benchmark_claims_report.json",
        {
            "competitiveness_claim": "competitive_against_current_same_contract_reference_set",
            "deployment_claim": "not_evaluated_yet",
            "below_reference": False,
        },
        indent=2,
        ensure_ascii=False,
        sort_keys=True,
    )
    write_json(
        run_dir / "shadow_trial_manifest.json",
        {"candidate_count": 0},
        indent=2,
        ensure_ascii=False,
        sort_keys=True,
    )
    write_json(
        run_dir / "promotion_readiness_report.json",
        {"promotion_ready_count": 0, "candidate_available_count": 0},
        indent=2,
        ensure_ascii=False,
        sort_keys=True,
    )
    write_json(
        run_dir / "candidate_quarantine.json",
        {"quarantined_count": 0},
        indent=2,
        ensure_ascii=False,
        sort_keys=True,
    )
    write_json(
        run_dir / "decision_constraint_report.json",
        {
            "generated_at": "2026-04-13T07:30:00+00:00",
            "feasible_selected_action": "request_operator_review",
            "summary": "The route is usable but still needs explicit operator review.",
        },
        indent=2,
        ensure_ascii=False,
        sort_keys=True,
    )
    write_json(
        run_dir / "deployability_assessment.json",
        {
            "deployability": "review_only",
            "operational_readiness": "review_needed",
            "recommended_direction": "same_data",
        },
        indent=2,
        ensure_ascii=False,
        sort_keys=True,
    )
    write_json(
        run_dir / "review_gate_state.json",
        {"status": "open", "review_required": True, "gate_kind": "operator_review"},
        indent=2,
        ensure_ascii=False,
        sort_keys=True,
    )
    write_json(
        run_dir / "search_controller_plan.json",
        {
            "recommended_action": "expand_challenger_portfolio",
            "recommended_direction": "same_data",
            "search_mode": "bounded_review",
            "selected_hpo_depth": "light",
            "planned_trial_count": 4,
        },
        indent=2,
        ensure_ascii=False,
        sort_keys=True,
    )
    write_json(
        run_dir / "search_value_report.json",
        {
            "value_band": "medium",
            "value_score": 0.61,
            "review_need": "low",
        },
        indent=2,
        ensure_ascii=False,
        sort_keys=True,
    )
    write_json(
        run_dir / "search_controller_eval_report.json",
        {"status": "ok", "same_plan_across_profiles": True},
        indent=2,
        ensure_ascii=False,
        sort_keys=True,
    )
    write_json(
        run_dir / "portfolio_search_trace.json",
        {"candidate_branch_count": 2, "widened_branch_count": 1, "pruned_branch_count": 1},
        indent=2,
        ensure_ascii=False,
        sort_keys=True,
    )
    write_json(
        run_dir / "hpo_campaign_report.json",
        {"backend": "deterministic_local_search", "max_trials": 12, "executed_trial_count": 6},
        indent=2,
        ensure_ascii=False,
        sort_keys=True,
    )
    write_json(
        run_dir / "execution_backend_profile.json",
        {"selected_execution_profile": "cpu_local", "execution_mode": "local"},
        indent=2,
        ensure_ascii=False,
        sort_keys=True,
    )
    write_json(
        run_dir / "execution_strategy_report.json",
        {"execution_strategy": "serial_finalists"},
        indent=2,
        ensure_ascii=False,
        sort_keys=True,
    )
    write_json(
        run_dir / "trace_model.json",
        {
            "status": "ok",
            "span_count": 4,
            "claim_count": 2,
            "direct_runtime_emission_detected": True,
        },
        indent=2,
        ensure_ascii=False,
        sort_keys=True,
    )
    write_json(
        run_dir / "adjudication_scorecard.json",
        {
            "winning_claim_id": "claim_route_current",
            "winning_action": "hold_current_route",
        },
        indent=2,
        ensure_ascii=False,
        sort_keys=True,
    )
    write_json(
        run_dir / "decision_replay_report.json",
        {
            "status": "ok",
            "competing_claim_count": 2,
            "timeline": [{"event": "claim_compared"}, {"event": "winner_selected"}],
        },
        indent=2,
        ensure_ascii=False,
        sort_keys=True,
    )
    write_json(
        run_dir / "agent_eval_matrix.json",
        {
            "status": "ok",
            "passed_count": 4,
            "failed_count": 0,
            "not_applicable_count": 0,
        },
        indent=2,
        ensure_ascii=False,
        sort_keys=True,
    )
    write_json(
        run_dir / "protocol_conformance_report.json",
        {"status": "ok", "mismatch_count": 0},
        indent=2,
        ensure_ascii=False,
        sort_keys=True,
    )
    write_json(
        run_dir / "security_eval_report.json",
        {"status": "ok", "open_finding_count": 0},
        indent=2,
        ensure_ascii=False,
        sort_keys=True,
    )
    write_json(
        run_dir / "red_team_report.json",
        {"status": "ok", "finding_count": 0},
        indent=2,
        ensure_ascii=False,
        sort_keys=True,
    )
    write_json(
        run_dir / "host_surface_matrix.json",
        {"surface_count": 4},
        indent=2,
        ensure_ascii=False,
        sort_keys=True,
    )
    write_json(
        run_dir / "feedback_intake.json",
        {"entries": []},
        indent=2,
        ensure_ascii=False,
        sort_keys=True,
    )


def _initialize_runtime(run_dir: Path, data_path: Path) -> None:
    policy = load_policy().policy
    ensure_runtime_initialized(
        run_dir=run_dir,
        policy=policy,
        source_surface="cli",
        source_command="push_smoke_fixture",
    )
    stage_token = record_stage_start(
        run_dir=run_dir,
        policy=policy,
        stage="planning",
        source_surface="cli",
        source_command="push_smoke_fixture",
        data_path=str(data_path),
        input_artifacts=["dataset_profile.json", "plan.json"],
    )
    record_stage_completion(
        run_dir=run_dir,
        policy=policy,
        stage_token=stage_token,
        output_artifacts=[
            str(run_dir / "benchmark_parity_report.json"),
            str(run_dir / "decision_constraint_report.json"),
        ],
        summary="Push smoke fixture materialized a minimal seeded run for fast surface validation.",
    )


@pytest.fixture(scope="session")
def push_smoke_seed_run(tmp_path_factory: pytest.TempPathFactory) -> dict[str, Path]:
    root = tmp_path_factory.mktemp("push_smoke_seed")
    run_dir = root / "seed_run"
    run_dir.mkdir(parents=True, exist_ok=True)
    data_path = _write_push_smoke_binary_dataset(run_dir / "data.csv")
    _write_seed_artifacts(run_dir, data_path)
    _initialize_runtime(run_dir, data_path)
    materialize_run_summary(
        run_dir=run_dir,
        data_path=data_path,
        request_source="fixture",
        request_text="Classify target_flag from the provided features and keep the operator informed.",
    )
    return {"root": root, "run_dir": run_dir, "data_path": data_path}


@pytest.fixture
def push_smoke_run(tmp_path: Path, push_smoke_seed_run: dict[str, Path]) -> dict[str, Path]:
    source_root = Path(push_smoke_seed_run["root"])
    root = tmp_path / "seed_copy"
    shutil.copytree(source_root, root)
    run_dir = root / "seed_run"
    return {
        "run_dir": run_dir,
        "data_path": run_dir / "data.csv",
    }
