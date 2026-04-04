from __future__ import annotations

import csv
from pathlib import Path

from relaytic.decision import run_decision_review
from relaytic.policies import load_policy


def test_decision_review_prefers_additional_local_data_when_safe_join_candidate_exists(tmp_path: Path) -> None:
    run_dir = tmp_path / "decision_unit"
    data_dir = run_dir / "data_copies"
    data_dir.mkdir(parents=True)
    current_path = data_dir / "primary_sample.csv"
    nearby_path = data_dir / "nearby_context.csv"
    _write_dataset(current_path)
    _write_dataset(nearby_path)

    result = run_decision_review(
        run_dir=run_dir,
        policy=load_policy().policy,
        context_bundle={
            "task_brief": {
                "problem_statement": "Fraud review queue for high-risk cases.",
                "task_type_hint": "binary_classification",
                "domain_archetype_hint": "fraud_risk",
            }
        },
        investigation_bundle={
            "dataset_profile": {
                "row_count": 220,
                "candidate_target_columns": ["target_flag"],
                "numeric_columns": ["amount", "balance", "velocity"],
                "categorical_columns": ["segment_id"],
                "entity_key_candidates": ["entity_id"],
                "hidden_key_candidates": [],
                "suspicious_columns": [],
                "timestamp_column": "event_time",
            },
            "domain_memo": {"domain_archetype": "fraud_risk"},
            "feature_strategy_profile": {
                "prioritize_missingness_indicators": True,
                "prioritize_interactions": True,
            },
        },
        planning_bundle={
            "plan": {
                "task_type": "binary_classification",
                "target_column": "target_flag",
                "feature_columns": ["amount", "balance", "velocity", "segment_id"],
                "selected_model_family": "logistic_regression",
                "execution_summary": {"selected_model_family": "logistic_regression"},
                "builder_handoff": {"data_references": [str(current_path)]},
            }
        },
        memory_bundle={
            "memory_retrieval": {"selected_analog_count": 2},
            "route_prior_context": {"status": "memory_influenced"},
            "challenger_prior_suggestions": {"preferred_challenger_family": "boosted_tree_classifier"},
        },
        intelligence_bundle={
            "semantic_debate_report": {"recommended_followup_action": "collect_more_data"},
            "semantic_uncertainty_report": {"unresolved_items": []},
        },
        research_bundle={
            "research_brief": {"recommended_followup_action": "collect_more_data"},
            "method_transfer_report": {
                "accepted_candidates": [
                    {"candidate_kind": "challenger_family", "value": "boosted_tree_classifier"},
                    {"candidate_kind": "evaluation_design", "value": "calibration_review"},
                ],
                "advisory_candidates": [],
            },
        },
        benchmark_bundle={
            "benchmark_parity_report": {"parity_status": "at_parity", "recommended_action": "hold_current_route"},
            "benchmark_gap_report": {"near_parity": True, "winning_family": "boosted_tree_classifier"},
        },
        profiles_bundle={
            "quality_contract": {"acceptance_criteria": {"f1": 0.75}},
            "quality_gate_report": {"gate_status": "conditional_pass"},
            "operator_profile": {"review_strictness": "strict"},
            "lab_operating_profile": {"local_truth_required": True},
        },
        control_bundle={},
        completion_bundle={"completion_decision": {"action": "hold_current_route"}},
    )

    bundle = result.bundle.to_dict()
    assert result.selected_strategy == "additional_local_data"
    assert result.next_actor == "relaytic_data_fabric"
    assert result.selected_next_action == "acquire_local_data"
    assert bundle["decision_world_model"]["action_regime"] == "human_review_queue"
    assert bundle["decision_usefulness_report"]["selected_strategy"] == "additional_local_data"
    assert bundle["join_candidate_report"]["candidate_count"] >= 1
    assert bundle["compiled_challenger_templates"]["templates"]
    assert bundle["compiled_feature_hypotheses"]["hypotheses"]


def test_decision_review_applies_feasibility_constraints_and_changes_next_move(tmp_path: Path) -> None:
    run_dir = tmp_path / "decision_feasibility"
    data_dir = run_dir / "data_copies"
    data_dir.mkdir(parents=True)
    current_path = data_dir / "primary_sample.csv"
    nearby_path = data_dir / "nearby_context.csv"
    _write_dataset(current_path)
    _write_dataset(nearby_path)

    result = run_decision_review(
        run_dir=run_dir,
        policy=load_policy().policy,
        context_bundle={
            "task_brief": {
                "problem_statement": "Fraud screening with strict reviewability and physical/safety bounds on extrapolation.",
                "task_type_hint": "binary_classification",
                "domain_archetype_hint": "fraud_risk",
            }
        },
        investigation_bundle={
            "dataset_profile": {
                "row_count": 220,
                "candidate_target_columns": ["target_flag"],
                "numeric_columns": ["amount", "balance", "velocity"],
                "categorical_columns": ["segment_id"],
                "entity_key_candidates": ["entity_id"],
                "hidden_key_candidates": [],
                "suspicious_columns": [],
                "timestamp_column": "event_time",
            },
            "domain_memo": {
                "domain_archetype": "fraud_risk",
                "physical_constraints": ["Do not extrapolate outside observed score bands without review."],
                "policy_constraints": ["Human review is required when feasibility is uncertain."],
            },
        },
        planning_bundle={
            "plan": {
                "task_type": "binary_classification",
                "target_column": "target_flag",
                "feature_columns": ["amount", "balance", "velocity", "segment_id"],
                "selected_model_family": "logistic_regression",
                "execution_summary": {"selected_model_family": "logistic_regression"},
                "builder_handoff": {"data_references": [str(current_path)]},
            }
        },
        memory_bundle={"memory_retrieval": {"selected_analog_count": 2}},
        intelligence_bundle={"semantic_uncertainty_report": {"unresolved_items": []}},
        research_bundle={"research_brief": {"recommended_followup_action": "hold_current_route"}},
        benchmark_bundle={
            "benchmark_parity_report": {"parity_status": "at_parity", "recommended_action": "hold_current_route"},
            "benchmark_gap_report": {"near_parity": True},
        },
        profiles_bundle={
            "quality_contract": {"acceptance_criteria": {"f1": 0.75}},
            "quality_gate_report": {"gate_status": "conditional_pass"},
            "operator_profile": {"review_strictness": "strict"},
            "lab_operating_profile": {"local_truth_required": True},
        },
        control_bundle={},
        completion_bundle={"completion_decision": {"action": "hold_current_route"}},
        lifecycle_bundle={
            "champion_vs_candidate": {
                "fresh_data_behavior": {
                    "ood_summary": {"overall_ood_fraction": 0.42},
                }
            }
        },
        permission_bundle={"permission_mode": {"current_mode": "review"}},
    )

    bundle = result.bundle.to_dict()
    assert bundle["trajectory_constraint_report"]["physical_constraint_count"] >= 1
    assert bundle["extrapolation_risk_report"]["risk_band"] == "high"
    assert bundle["decision_constraint_report"]["primary_constraint_kind"] == "physical"
    assert bundle["decision_constraint_report"]["feasible_selected_action"] == "acquire_local_data"
    assert bundle["decision_constraint_report"]["recommended_direction"] == "add_data"
    assert bundle["action_boundary_report"]["deployability_status"] == "not_deployable"
    assert bundle["review_gate_state"]["gate_open"] is True
    assert bundle["counterfactual_region_report"]["why_not_rerun"]
    assert result.selected_next_action == "acquire_local_data"


def _write_dataset(path: Path) -> None:
    rows = [
        ["entity_id", "event_time", "amount", "balance", "velocity", "segment_id", "target_flag"],
        ["a1", "2026-01-01", "10.0", "100.0", "1.0", "retail", "0"],
        ["a2", "2026-01-02", "11.0", "110.0", "2.0", "retail", "1"],
        ["a3", "2026-01-03", "12.0", "120.0", "1.5", "business", "0"],
        ["a4", "2026-01-04", "13.0", "130.0", "2.5", "business", "1"],
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerows(rows)
