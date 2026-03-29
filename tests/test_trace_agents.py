from __future__ import annotations

from relaytic.tracing import ClaimPacket, adjudicate_claim_packets


def _claim(*, claim_id: str, specialist: str, action: str, confidence: float) -> ClaimPacket:
    return ClaimPacket(
        schema_version="relaytic.claim_packet.v1",
        claim_id=claim_id,
        generated_at="2026-03-29T00:00:00+00:00",
        stage=specialist,
        specialist=specialist,
        claim_type="next_action",
        proposed_action=action,
        target_scope="current_run",
        objective_frame="unit test",
        confidence=confidence,
        evidence_refs=["run_summary.json"],
        empirical_support={"unit_test": True},
        risk_flags=[],
        assumptions=["unit test"],
        falsifiers=["unit test"],
        policy_constraints=["local_truth_first"],
        trace_ref="span_unit",
    )


def test_adjudication_can_choose_lower_confidence_claim_when_contract_support_is_stronger() -> None:
    scorecard = adjudicate_claim_packets(
        claim_packets=[
            _claim(
                claim_id="claim_decision",
                specialist="decision_lab",
                action="collect_more_data",
                confidence=0.74,
            ),
            _claim(
                claim_id="claim_benchmark",
                specialist="benchmark_referee",
                action="expand_challenger_portfolio",
                confidence=0.91,
            ),
            _claim(
                claim_id="claim_completion",
                specialist="completion_governor",
                action="run_recalibration_pass",
                confidence=0.77,
            ),
        ],
        summary_payload={
            "decision_lab": {
                "selected_next_action": "collect_more_data",
                "review_required": False,
            },
            "benchmark": {
                "beat_target_state": "unmet",
            },
            "control": {
                "suspicious_count": 1,
                "similar_harmful_override_count": 1,
            },
            "intelligence": {
                "uncertainty_band": "medium",
            },
            "next_step": {
                "recommended_action": "collect_more_data",
            },
        },
    )

    assert scorecard.winning_claim_id == "claim_decision"
    assert scorecard.winning_action == "collect_more_data"
    assert scorecard.scorecard[0].claim_id == "claim_decision"
    assert any(
        item["claim_id"] == "claim_benchmark"
        and "higher confidence lost" in item["reason"]
        for item in scorecard.why_not_others
    )
