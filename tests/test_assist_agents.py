from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

from relaytic.assist import build_assist_audit_explanation, plan_assist_turn
from relaytic.ui.cli import _maybe_enhance_audit_explanation_with_local_advisor


def test_plan_assist_turn_treats_why_not_rerun_as_explanation() -> None:
    plan = plan_assist_turn(
        message="why not a rerun?",
        run_summary={"stage_completed": "decision"},
        assist_bundle={},
    )

    assert plan.intent.intent_type == "explain"
    assert plan.action_kind == "respond"


def test_build_assist_audit_explanation_gives_agent_exact_model_choice_reasoning() -> None:
    audit = build_assist_audit_explanation(
        message="why did you use this model?",
        actor_type="agent",
        run_summary={
            "decision": {
                "selected_model_family": "gradient_boosting",
                "selected_route_title": "Gradient boosting route",
                "primary_metric": "roc_auc",
            },
            "decision_lab": {"selected_next_action": "search_more"},
            "benchmark": {"parity_status": "below_reference"},
            "hpo": {
                "executed_trial_count": 9,
                "tuned_family_count": 2,
                "stop_reasons": ["convergence_plateau"],
            },
        },
    )

    assert audit["question_type"] == "model_choice"
    assert audit["actor_type"] == "agent"
    assert audit["llm_enhanced"] is False
    assert "gradient_boosting" in audit["answer"]
    assert "roc_auc" in audit["answer"]
    assert "9" in audit["answer"]
    assert "benchmark_parity_report.json" in audit["evidence_refs"]
    assert "search_loop_scorecard.json" in audit["evidence_refs"]


def test_build_assist_audit_explanation_answers_task_semantics_questions() -> None:
    audit = build_assist_audit_explanation(
        message="why not anomaly detection?",
        actor_type="user",
        run_summary={
            "decision": {"task_type": "binary_classification"},
            "task_contract": {
                "task_type": "binary_classification",
                "problem_posture": "rare_event_supervised",
                "benchmark_comparison_metric": "pr_auc",
                "why_not_anomaly_detection": (
                    "Relaytic kept this as supervised rare-event classification because the dataset contains explicit labeled outcomes."
                ),
            },
            "benchmark_vs_deploy": {"deployment_readiness": "conditional"},
            "benchmark": {"comparison_metric": "pr_auc"},
        },
    )

    assert audit["question_type"] == "task_semantics"
    assert "rare-event classification" in audit["answer"]
    assert "task_profile_contract.json" in audit["evidence_refs"]


def test_build_assist_audit_explanation_answers_aml_posture_questions() -> None:
    audit = build_assist_audit_explanation(
        message="why is this in aml mode and what is the review queue objective?",
        actor_type="user",
        run_summary={
            "aml": {
                "status": "active",
                "aml_active": True,
                "domain_focus": "transaction_monitoring",
                "target_level": "transaction",
                "business_goal": "analyst_triage",
                "review_budget_relevant": True,
                "decision_objective": "maximize_precision_at_review_budget",
                "claim_scope": "generic_supporting_only_until_15r",
                "benchmark_pack_family": "aml_flagship_pending",
                "public_claim_ready": False,
            }
        },
    )

    assert audit["question_type"] == "aml_posture"
    assert "transaction_monitoring" in audit["answer"]
    assert "maximize_precision_at_review_budget" in audit["answer"]
    assert "aml_review_budget_contract.json" in audit["evidence_refs"]


def test_build_assist_audit_explanation_answers_aml_graph_questions() -> None:
    audit = build_assist_audit_explanation(
        message="why is this structurally suspicious and what did the graph find?",
        actor_type="agent",
        run_summary={
            "aml_graph": {
                "status": "active",
                "node_count": 14,
                "edge_count": 11,
                "component_count": 3,
                "top_entity": "HUB1",
                "typology_hit_count": 3,
                "top_typology": "smurfing",
                "focal_entity": "HUB1",
                "expanded_entity_count": 5,
                "shadow_winner": "structural_baseline",
            }
        },
    )

    assert audit["question_type"] == "aml_graph"
    assert "HUB1" in audit["answer"]
    assert "smurfing" in audit["answer"]
    assert "subgraph_risk_report.json" in audit["evidence_refs"]


def test_build_assist_audit_explanation_answers_aml_casework_questions() -> None:
    audit = build_assist_audit_explanation(
        message="why is this the top case in the review queue and what is in the case packet?",
        actor_type="user",
        run_summary={
            "aml": {
                "decision_objective": "maximize_precision_at_review_budget",
            },
            "casework": {
                "status": "active",
                "queue_count": 6,
                "review_capacity_cases": 2,
                "decision_objective": "maximize_precision_at_review_budget",
                "top_case_id": "case_hub1",
                "top_case_entity": "HUB1",
                "top_case_action": "review_now",
                "estimated_review_hours": 1.5,
                "review_typology_coverage": 3,
                "selected_review_fraction": 0.2,
            },
        },
    )

    assert audit["question_type"] == "aml_casework"
    assert "case_hub1" in audit["answer"]
    assert "HUB1" in audit["answer"]
    assert "maximize_precision_at_review_budget" in audit["answer"]
    assert "case_packet.json" in audit["evidence_refs"]


def test_build_assist_audit_explanation_answers_aml_stream_risk_questions() -> None:
    audit = build_assist_audit_explanation(
        message="why did drift trigger recalibration and how weak are these labels?",
        actor_type="agent",
        run_summary={
            "stream_risk": {
                "status": "active",
                "stream_mode": "batched_temporal_monitoring",
                "timestamp_column": "step",
                "weak_label_risk_level": "high",
                "label_kind": "proxy_alert_label",
                "delayed_confirmation_likely": True,
                "rolling_window_count": 4,
                "drift_score": 0.72,
                "trigger_action": "run_recalibration_pass",
            }
        },
    )

    assert audit["question_type"] == "aml_stream_risk"
    assert "run_recalibration_pass" in audit["answer"]
    assert "proxy_alert_label" in audit["answer"]
    assert "stream_risk_posture.json" in audit["evidence_refs"]


def test_build_assist_audit_explanation_answers_objective_alignment_questions() -> None:
    audit = build_assist_audit_explanation(
        message="why did you optimize one metric but benchmark another?",
        actor_type="agent",
        run_summary={
            "objective_contract": {
                "selection_metric": "log_loss",
                "calibration_metric": "log_loss",
                "threshold_metric": "pr_auc",
                "benchmark_comparison_metric": "pr_auc",
                "deployment_decision_metric": "roc_auc",
                "explicit_metric_split": True,
                "truth_precheck_status": "ok",
                "safe_to_rank": True,
            },
            "split_health": {
                "status": "ok",
                "temporal_fold_status": "not_applicable",
            },
            "benchmark": {"comparison_metric": "pr_auc"},
            "decision": {"primary_metric": "roc_auc"},
        },
    )

    assert audit["question_type"] == "objective_alignment"
    assert "log_loss" in audit["answer"]
    assert "pr_auc" in audit["answer"]
    assert "roc_auc" in audit["answer"]
    assert "optimization_objective_contract.json" in audit["evidence_refs"]


def test_build_assist_audit_explanation_answers_operating_point_questions() -> None:
    audit = build_assist_audit_explanation(
        message="why this threshold and calibration?",
        actor_type="user",
        run_summary={
            "hpo": {
                "threshold_policy": "favor_pr_auc",
                "selected_calibration_method": "platt_scaling",
            },
            "operating_point": {
                "selected_threshold": 0.6,
                "threshold_policy": "favor_pr_auc",
                "raw_best_threshold": 0.5,
                "review_budget_threshold": 0.6,
                "selected_calibration_method": "platt_scaling",
                "decision_cost_profile_kind": "rare_event_review_queue",
                "review_budget_changed_threshold": True,
                "selection_reason": "Relaytic selected the review-budget-aware threshold to cut operator overload.",
                "abstention_state": "review_band",
                "abstain_low": 0.52,
                "abstain_high": 0.68,
            },
        },
    )

    assert audit["question_type"] == "operating_point"
    assert "0.6" in audit["answer"]
    assert "platt_scaling" in audit["answer"]
    assert "review-budget-aware threshold" in audit["answer"]
    assert "operating_point_contract.json" in audit["evidence_refs"]


def test_build_assist_audit_explanation_answers_why_not_lstm() -> None:
    audit = build_assist_audit_explanation(
        message="why not an lstm here?",
        actor_type="user",
        run_summary={
            "decision": {"selected_model_family": "hist_gradient_boosting_classifier"},
            "architecture": {
                "recommended_primary_family": "hist_gradient_boosting_classifier",
                "candidate_order": [
                    "hist_gradient_boosting_classifier",
                    "extra_trees_classifier",
                    "bagged_tree_classifier",
                ],
                "sequence_live_allowed": False,
                "sequence_shadow_ready": False,
                "sequence_rejection_reason": (
                    "Relaytic rejected sequence-family routing because the task contract does not prove ordered temporal structure."
                ),
            },
        },
    )

    assert audit["question_type"] == "why_not_sequence_model"
    assert "ordered temporal structure" in audit["answer"]
    assert "architecture_router_report.json" in audit["evidence_refs"]


def test_build_assist_audit_explanation_answers_why_not_imported_architecture() -> None:
    audit = build_assist_audit_explanation(
        message="why not tabpfn here?",
        actor_type="user",
        run_summary={
            "decision": {"selected_model_family": "hist_gradient_boosting_classifier"},
            "architecture": {"recommended_primary_family": "hist_gradient_boosting_classifier"},
            "architecture_imports": {
                "candidate_available_count": 1,
                "candidate_available_families": ["tabpfn_classifier"],
                "quarantined_count": 0,
                "promotion_ready_count": 0,
            },
        },
    )

    assert audit["question_type"] == "why_not_imported_architecture"
    assert "candidate-available" in audit["answer"]
    assert "promotion_readiness_report.json" in audit["evidence_refs"]


def test_build_assist_audit_explanation_answers_family_eligibility_questions() -> None:
    audit = build_assist_audit_explanation(
        message="why not catboost here and what families were eligible?",
        actor_type="agent",
        run_summary={
            "family_stack": {
                "eligible_family_count": 5,
                "adapter_ready_family_count": 2,
                "categorical_strategy": "encoded_numeric_fallback",
                "probe_tier_one_families": [
                    "hist_gradient_boosting_classifier",
                    "extra_trees_classifier",
                    "boosted_tree_classifier",
                ],
                "eligible_families": [
                    "hist_gradient_boosting_classifier",
                    "extra_trees_classifier",
                    "boosted_tree_classifier",
                    "logistic_regression",
                    "xgboost_classifier",
                ],
                "blocked_reasons_by_family": {
                    "catboost_classifier": "Optional adapter `catboost` is unavailable on this machine, so Relaytic will fall back cleanly."
                },
            }
        },
    )

    assert audit["question_type"] == "family_eligibility"
    assert "encoded_numeric_fallback" in audit["answer"]
    assert "catboost_classifier" in audit["answer"]
    assert "family_eligibility_matrix.json" in audit["evidence_refs"]


def test_local_advisor_can_rewrite_human_audit_answer(monkeypatch, tmp_path: Path) -> None:
    import relaytic.intelligence as intelligence_pkg
    import relaytic.intelligence.backends as backends_pkg
    import relaytic.ui.cli as cli_module

    class _FakeAdvisor:
        def complete_json(self, **_kwargs: object) -> SimpleNamespace:
            return SimpleNamespace(
                status="ok",
                payload={
                    "answer": "Relaytic held off on a rerun because new data would change the answer more than another immediate retry.",
                    "bullets": [
                        "The current feasibility posture is outside the safe region for a simple rerun.",
                        "The recommended next move is to add local data first.",
                    ],
                },
            )

    monkeypatch.setattr(
        cli_module,
        "_ensure_run_foundation_present",
        lambda **_kwargs: {"resolved": SimpleNamespace(policy={})},
    )
    monkeypatch.setattr(intelligence_pkg, "build_intelligence_controls_from_policy", lambda _policy: object())
    monkeypatch.setattr(
        backends_pkg,
        "discover_backend",
        lambda **_kwargs: SimpleNamespace(status="available", advisor=_FakeAdvisor()),
    )

    audit = _maybe_enhance_audit_explanation_with_local_advisor(
        run_dir=tmp_path,
        config_path=None,
        actor_type="user",
        message="why not a rerun?",
        audit_payload={
            "question_type": "why_not_rerun",
            "answer": "Relaytic did not recommend a rerun.",
            "reasons": ["Deterministic baseline reason."],
            "evidence_refs": ["decision_constraint_report.json"],
            "actor_type": "user",
            "llm_enhanced": False,
        },
    )

    assert audit["llm_enhanced"] is True
    assert "new data would change the answer more" in audit["answer"]
    assert audit["reasons"] == [
        "The current feasibility posture is outside the safe region for a simple rerun.",
        "The recommended next move is to add local data first.",
    ]
