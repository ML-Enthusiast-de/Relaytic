from relaytic.dojo import run_dojo_review


def test_run_dojo_review_promotes_only_when_visible_gates_pass(tmp_path) -> None:
    result = run_dojo_review(
        run_dir=tmp_path / "dojo_unit",
        policy={
            "dojo": {
                "enabled": True,
                "max_active_promotions": 2,
            }
        },
        planning_bundle={
            "plan": {
                "execution_summary": {
                    "selected_model_family": "boosted_tree_classifier",
                }
            }
        },
        benchmark_bundle={
            "benchmark_parity_report": {
                "relaytic_family": "boosted_tree_classifier",
                "incumbent_present": True,
            },
            "beat_target_contract": {
                "contract_state": "met",
            },
        },
        decision_bundle={
            "method_compiler_report": {
                "compiled_challenger_count": 2,
                "compiled_feature_count": 3,
                "top_compiled_challenger_family": "random_forest_classifier",
            }
        },
        research_bundle={
            "method_transfer_report": {
                "accepted_candidates": [{"title": "RF calibration transfer"}],
            }
        },
        profiles_bundle={
            "quality_gate_report": {
                "gate_status": "conditional_pass",
            }
        },
        control_bundle={
            "control_injection_audit": {
                "suspicious_count": 0,
                "rejected_count": 0,
            },
            "override_decision": {
                "decision": "accept",
            },
        },
    )

    bundle = result.bundle.to_dict()
    assert bundle["dojo_results"]["promoted_count"] >= 1
    assert bundle["dojo_session"]["active_promotion_count"] >= 1
    assert any(
        item["proposal_kind"] == "architecture_proposal" and item["decision"] == "quarantined"
        for item in bundle["dojo_results"]["results"]
    )
