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
        },
    )

    assert audit["question_type"] == "model_choice"
    assert audit["actor_type"] == "agent"
    assert audit["llm_enhanced"] is False
    assert "gradient_boosting" in audit["answer"]
    assert "roc_auc" in audit["answer"]
    assert "benchmark_parity_report.json" in audit["evidence_refs"]


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
