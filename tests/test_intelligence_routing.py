from __future__ import annotations

from pathlib import Path

from relaytic.intelligence.local_baseline import build_local_llm_profile_artifact
from relaytic.intelligence.modes import canonicalize_mode
from relaytic.intelligence.models import IntelligenceControls, IntelligenceTrace
from relaytic.intelligence.routing import (
    build_llm_routing_plan_artifact,
    build_semantic_proof_report_artifact,
    build_verifier_report_artifact,
)


class _Discovery:
    def __init__(self, *, status: str = "available") -> None:
        self.status = status
        self.requested_provider = "llama_cpp"
        self.resolved_provider = "llama_cpp"
        self.resolved_model = "relaytic-4b"
        self.endpoint = "http://127.0.0.1:8000/v1/chat/completions"
        self.endpoint_scope = "local"
        self.profile = "small_cpu"


def _trace() -> IntelligenceTrace:
    return IntelligenceTrace(
        agent="test_agent",
        operating_mode="structured_semantic_tasks",
        llm_used=False,
        llm_status="deterministic_only",
        deterministic_evidence=["artifact_context_assembly"],
        advisory_notes=[],
    )


def test_canonicalize_mode_maps_legacy_labels() -> None:
    assert canonicalize_mode("deterministic") == "none"
    assert canonicalize_mode("advisory_local_llm") == "assist"
    assert canonicalize_mode("frontier_assisted") == "max_reasoning"


def test_local_profile_and_routing_plan_use_minimum_local_profile(tmp_path: Path) -> None:
    config_path = tmp_path / "routing_config.yaml"
    config_path.write_text(
        "\n".join(
            [
                "policy:",
                "  intelligence:",
                "    enabled: true",
                "    intelligence_mode: advisory_local_llm",
                "    minimum_local_llm_enabled: true",
                "    minimum_local_llm_profile: small_cpu",
                "runtime:",
                "  provider: llama_cpp",
                "  require_local_models: true",
                "  block_remote_endpoints: true",
                "  offline_mode: true",
                "  profiles:",
                "    small_cpu:",
                "      model: relaytic-4b",
                "      cpu_only: true",
                "      n_gpu_layers: 0",
                "      max_context: 4096",
                "    balanced:",
                "      model: relaytic-8b",
                "      cpu_only: false",
                "      n_gpu_layers: auto",
                "      max_context: 8192",
                "  default_profile: balanced",
                "  fallback_order:",
                "    - small_cpu",
            ]
        ),
        encoding="utf-8",
    )
    controls = IntelligenceControls(
        intelligence_mode="advisory_local_llm",
        minimum_local_llm_enabled=True,
        minimum_local_llm_profile="small_cpu",
    )
    profile = build_local_llm_profile_artifact(
        controls=controls,
        config_path=str(config_path),
        generated_at="2026-03-23T00:00:00+00:00",
        trace=_trace(),
    )

    assert profile.status == "ok"
    assert profile.profile_name == "small_cpu"
    assert profile.profile_origin == "minimum_local_llm_profile"
    assert profile.recommended_mode == "local_min"

    routing = build_llm_routing_plan_artifact(
        controls=controls,
        discovery=_Discovery(),
        local_profile=profile,
        context_blocks=[{"artifact": "run_brief.json"}] * 9,
        grounding_points=[{"artifact": "plan.json"}] * 5,
        generated_at="2026-03-23T00:00:00+00:00",
        trace=_trace(),
    )

    assert routing.requested_mode == "assist"
    assert routing.selected_profile["profile_name"] == "small_cpu"
    assert routing.capability_matrix["json_mode"] is True
    assert routing.capability_matrix["context_window"] == 4096
    assert routing.selected_mode in {"assist", "amplify"}


def test_verifier_and_semantic_proof_capture_deltas() -> None:
    controls = IntelligenceControls(intelligence_mode="assist")
    baseline = {
        "recommended_followup_action": "run_recalibration_pass",
        "verifier_verdict": {"action": "run_recalibration_pass", "summary": "Cheaper path."},
        "domain_interpretation": {"domain_archetype": "fraud_risk"},
        "counterposition": {"action": "run_retrain_pass"},
        "confidence": "conditional",
    }
    routed = {
        "recommended_followup_action": "expand_challenger_portfolio",
        "verifier_verdict": {"action": "expand_challenger_portfolio", "summary": "Need more challenge."},
        "domain_interpretation": {"domain_archetype": "fraud_risk", "modeling_bias": "rare_event_precision"},
        "counterposition": {"action": "run_recalibration_pass"},
        "confidence": "medium",
    }

    verifier = build_verifier_report_artifact(
        controls=controls,
        debate_payload=routed,
        baseline_debate=baseline,
        llm_used=True,
        provider_status="ok",
        generated_at="2026-03-23T00:00:00+00:00",
        trace=_trace(),
    )
    proof = build_semantic_proof_report_artifact(
        controls=controls,
        debate_payload=routed,
        baseline_debate=baseline,
        llm_used=True,
        generated_at="2026-03-23T00:00:00+00:00",
        trace=_trace(),
    )

    assert verifier.changed_from_deterministic_baseline is True
    assert verifier.selected_action == "expand_challenger_portfolio"
    assert proof.measurable_gain_detected is True
    assert "recommended_followup_action" in proof.changed_fields
    assert proof.benchmark_dimensions
