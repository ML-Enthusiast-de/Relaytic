from relaytic.analytics.expert_priors import infer_expert_priors


def test_infer_expert_priors_detects_manufacturing_quality_from_context() -> None:
    priors = infer_expert_priors(
        dataset_profile={
            "data_mode": "time_series",
            "candidate_target_columns": ["quality_score"],
            "numeric_columns": ["sensor_a", "sensor_b", "quality_score"],
            "categorical_columns": ["line_id", "batch_id"],
            "entity_key_candidates": ["batch_id"],
            "suspicious_columns": ["future_quality"],
        },
        primary_target={"target_column": "quality_score", "task_type": "regression"},
        task_brief={
            "problem_statement": "Predict quality score early enough to reduce scrap.",
            "success_criteria": ["Reduce off-spec production."],
            "failure_costs": ["Late detection causes scrap."],
        },
        domain_brief={"summary": "Production line quality monitoring for batches."},
        run_brief={"objective": "best_robust_pareto_front"},
        data_origin={"source_name": "pilot_line"},
    )

    assert priors.domain_archetype == "manufacturing_quality"
    assert priors.recommended_primary_metric == "mae"
    assert "stability_and_drift_features" in priors.feature_priorities


def test_infer_expert_priors_detects_fraud_risk_from_target_and_text() -> None:
    priors = infer_expert_priors(
        dataset_profile={
            "data_mode": "steady_state",
            "candidate_target_columns": ["fraud_flag"],
            "numeric_columns": ["amount_norm", "device_risk", "velocity_score", "fraud_flag"],
            "categorical_columns": [],
            "entity_key_candidates": ["transaction_id"],
            "suspicious_columns": [],
        },
        primary_target={
            "target_column": "fraud_flag",
            "task_type": "fraud_detection",
            "minority_class_fraction": 0.06,
        },
        task_brief={
            "problem_statement": "Detect fraudulent transactions before approval.",
            "task_type_hint": "fraud_detection",
            "domain_archetype_hint": "fraud_risk",
            "success_criteria": ["Catch fraud early."],
            "failure_costs": ["Missed fraud causes financial loss."],
        },
        domain_brief={"summary": "Payment fraud scoring."},
        run_brief={"objective": "best_robust_pareto_front"},
        data_origin={"source_name": "payment_gateway"},
    )

    assert priors.domain_archetype == "fraud_risk"
    assert priors.recommended_primary_metric == "pr_auc"
    assert priors.threshold_policy_hint == "favor_pr_auc"
    assert "rare_event_examples" in priors.additional_data_needs
