from __future__ import annotations

import json
from pathlib import Path

import pytest

pytest.importorskip("sklearn.datasets")

from relaytic.context import (
    build_context_controls_from_policy,
    default_data_origin,
    default_domain_brief,
    default_task_brief,
)
from relaytic.core.json_utils import write_json
from relaytic.investigation import run_investigation
from relaytic.mandate import (
    build_mandate_controls_from_policy,
    build_run_brief,
    build_work_preferences,
    default_lab_mandate,
)
from relaytic.memory import run_memory_retrieval, write_memory_bundle
from relaytic.planning import run_planning
from relaytic.policies import load_policy

from tests.public_datasets import write_public_breast_cancer_dataset
from tests.test_completion_agents import _build_executed_run


def _build_binary_foundation(policy: dict) -> tuple[dict, dict]:
    mandate_controls = build_mandate_controls_from_policy(policy)
    context_controls = build_context_controls_from_policy(policy)
    mandate_bundle = {
        "lab_mandate": default_lab_mandate(mandate_controls).to_dict(),
        "work_preferences": build_work_preferences(
            mandate_controls,
            policy=policy,
            execution_mode_preference="autonomous",
        ).to_dict(),
        "run_brief": build_run_brief(
            mandate_controls,
            policy=policy,
            objective="maximize early detection quality",
            target_column="diagnosis_flag",
            success_criteria=["Preserve strong classification quality with auditable local artifacts."],
            binding_constraints=["Do everything locally."],
        ).to_dict(),
    }
    context_bundle = {
        "data_origin": default_data_origin(
            context_controls,
            source_name="public_breast_cancer_dataset",
            source_type="historical_snapshot",
        ).to_dict(),
        "domain_brief": default_domain_brief(
            context_controls,
            system_name="screening_lab",
            summary="Classify whether a case is malignant from measurement features.",
        ).to_dict(),
        "task_brief": default_task_brief(
            context_controls,
            problem_statement="Classify diagnosis_flag from tabular measurement features.",
            target_column="diagnosis_flag",
            success_criteria=["Maintain strong recall and usable discrimination."],
            failure_costs=["Missed malignancy is costly."],
        ).to_dict(),
    }
    return mandate_bundle, context_bundle


def _write_prior_summary(
    run_dir: Path,
    *,
    run_id: str,
    domain_archetype: str,
    row_count: int,
    column_count: int,
    selected_model_family: str,
    primary_metric: str,
    challenger_family: str | None = None,
) -> None:
    run_dir.mkdir(parents=True, exist_ok=True)
    write_json(
        run_dir / "run_summary.json",
        {
            "schema_version": "relaytic.run_summary.v1",
            "generated_at": "2026-03-20T00:00:00+00:00",
            "product": "Relaytic",
            "run_id": run_id,
            "run_dir": str(run_dir),
            "status": "keep_current_champion",
            "stage_completed": "lifecycle_reviewed",
            "intent": {
                "objective": "maximize early detection quality",
                "domain_archetype": domain_archetype,
                "autonomy_mode": "autonomous",
            },
            "data": {
                "row_count": row_count,
                "column_count": column_count,
                "data_mode": "steady_state",
            },
            "decision": {
                "target_column": "diagnosis_flag",
                "task_type": "binary_classification",
                "selected_route_id": "calibrated_tabular_classifier_route",
                "selected_model_family": selected_model_family,
                "primary_metric": primary_metric,
            },
            "evidence": {
                "challenger_winner": "champion",
                "readiness_level": "strong",
            },
            "completion": {
                "action": "stop_for_now",
                "blocking_layer": "none",
            },
            "lifecycle": {
                "promotion_action": "keep_current_champion",
                "promotion_target": challenger_family,
            },
        },
        indent=2,
        ensure_ascii=False,
        sort_keys=True,
    )
    write_json(
        run_dir / "challenger_report.json",
        {
            "comparison": {
                "challenger_model_family": challenger_family,
            }
        },
        indent=2,
        ensure_ascii=False,
        sort_keys=True,
    )


def test_run_memory_retrieval_produces_provenance_and_changes_planning_order(tmp_path: Path) -> None:
    policy = load_policy().policy
    data_path = write_public_breast_cancer_dataset(tmp_path / "breast_cancer.csv")
    mandate_bundle, context_bundle = _build_binary_foundation(policy)
    investigation_bundle = run_investigation(
        data_path=str(data_path),
        policy=policy,
        mandate_bundle=mandate_bundle,
        context_bundle=context_bundle,
    ).to_dict()

    prior_dir = tmp_path / "prior_binary_success"
    _write_prior_summary(
        prior_dir,
        run_id="prior_binary_success",
        domain_archetype=str(
            investigation_bundle["domain_memo"].get("domain_archetype")
            or context_bundle["task_brief"].get("domain_archetype_hint")
            or "generic_tabular"
        ),
        row_count=int(investigation_bundle["dataset_profile"]["row_count"]),
        column_count=int(investigation_bundle["dataset_profile"]["column_count"]),
        selected_model_family="bagged_tree_classifier",
        primary_metric=str(investigation_bundle["optimization_profile"]["primary_metric"]),
        challenger_family="boosted_tree_classifier",
    )

    baseline = run_planning(
        data_path=str(data_path),
        policy=policy,
        mandate_bundle=mandate_bundle,
        context_bundle=context_bundle,
        investigation_bundle=investigation_bundle,
    )
    memory_result = run_memory_retrieval(
        run_dir=tmp_path / "current_binary_run",
        policy=policy,
        mandate_bundle=mandate_bundle,
        context_bundle=context_bundle,
        investigation_bundle=investigation_bundle,
        search_roots=[tmp_path],
    )
    with_memory = run_planning(
        data_path=str(data_path),
        policy=policy,
        mandate_bundle=mandate_bundle,
        context_bundle=context_bundle,
        investigation_bundle=investigation_bundle,
        memory_bundle=memory_result.bundle.to_dict(),
    )

    analogs = memory_result.bundle.analog_run_candidates.candidates
    assert memory_result.bundle.memory_retrieval.status == "retrieval_completed"
    assert analogs[0]["run_id"] == "prior_binary_success"
    assert analogs[0]["provenance"]["summary_path"].endswith("run_summary.json")
    assert baseline.plan.builder_handoff["preferred_candidate_order"][0] == "logistic_regression"
    assert with_memory.plan.builder_handoff["preferred_candidate_order"][0] == "bagged_tree_classifier"
    assert with_memory.plan.memory_context["changed"] is True


def test_run_completion_review_respects_memory_attempt_and_flushes_reflection(tmp_path: Path) -> None:
    data_path, run_dir, policy, mandate_bundle, context_bundle, payloads = _build_executed_run(tmp_path)
    evidence_bundle = dict(payloads["evidence_bundle"])
    evidence_bundle["challenger_report"] = {
        **dict(evidence_bundle["challenger_report"]),
        "winner": "champion",
    }
    evidence_bundle["audit_report"] = {
        **dict(evidence_bundle["audit_report"]),
        "provisional_recommendation": "continue_experimentation",
        "readiness_level": "conditional",
    }
    evidence_bundle["belief_update"] = {
        **dict(evidence_bundle["belief_update"]),
        "recommended_action": "continue_experimentation",
        "open_questions": ["Search breadth is still narrow."],
    }

    memory_result = run_memory_retrieval(
        run_dir=run_dir,
        policy=policy,
        mandate_bundle=mandate_bundle,
        context_bundle=context_bundle,
        intake_bundle=payloads["intake_bundle"],
        investigation_bundle=payloads["investigation_bundle"],
        planning_bundle=payloads["planning_bundle"],
        evidence_bundle=evidence_bundle,
        search_roots=[tmp_path / "isolated_memory_root"],
    )
    written = write_memory_bundle(run_dir, bundle=memory_result.bundle)

    from relaytic.completion import run_completion_review

    result = run_completion_review(
        run_dir=run_dir,
        policy=policy,
        mandate_bundle=mandate_bundle,
        context_bundle=context_bundle,
        intake_bundle=payloads["intake_bundle"],
        investigation_bundle=payloads["investigation_bundle"],
        planning_bundle=payloads["planning_bundle"],
        evidence_bundle=evidence_bundle,
        memory_bundle=memory_result.bundle.to_dict(),
    )

    assert memory_result.bundle.memory_retrieval.status == "no_credible_analogs"
    assert Path(written["reflection_memory"]).exists()
    assert Path(written["memory_flush_report"]).exists()
    assert result.bundle.completion_decision.action == "continue_experimentation"
    assert result.bundle.completion_decision.blocking_layer != "missing_memory_support"


def test_run_memory_retrieval_prefers_pulse_pinned_analogs_when_similarity_is_otherwise_equal(tmp_path: Path) -> None:
    policy = load_policy().policy
    data_path = write_public_breast_cancer_dataset(tmp_path / "breast_cancer_for_pinning.csv")
    mandate_bundle, context_bundle = _build_binary_foundation(policy)
    investigation_bundle = run_investigation(
        data_path=str(data_path),
        policy=policy,
        mandate_bundle=mandate_bundle,
        context_bundle=context_bundle,
    ).to_dict()

    unpinned_dir = tmp_path / "analog_unpinned"
    pinned_dir = tmp_path / "analog_pinned"
    for run_dir, run_id in [(unpinned_dir, "analog_unpinned"), (pinned_dir, "analog_pinned")]:
        _write_prior_summary(
            run_dir,
            run_id=run_id,
            domain_archetype=str(
                investigation_bundle["domain_memo"].get("domain_archetype")
                or context_bundle["task_brief"].get("domain_archetype_hint")
                or "generic_tabular"
            ),
            row_count=int(investigation_bundle["dataset_profile"]["row_count"]),
            column_count=int(investigation_bundle["dataset_profile"]["column_count"]),
            selected_model_family="bagged_tree_classifier",
            primary_metric=str(investigation_bundle["optimization_profile"]["primary_metric"]),
            challenger_family="boosted_tree_classifier",
        )
    write_json(
        pinned_dir / "memory_pinning_index.json",
        {
            "schema_version": "relaytic.memory_pinning_index.v1",
            "generated_at": "2026-03-29T00:00:00+00:00",
            "status": "active",
            "pin_count": 1,
            "entries": [
                {
                    "pin_id": "pin_0001",
                    "memory_kind": "harmful_override_pattern",
                    "pin_reason": "Do not forget this harmful override pattern.",
                    "retrieval_boost": 0.9,
                    "source_action": "pin_harmful_override_memory",
                }
            ],
            "retrieval_hint": "Pinned memory should influence later analog ordering.",
        },
        indent=2,
        ensure_ascii=False,
        sort_keys=True,
    )

    memory_result = run_memory_retrieval(
        run_dir=tmp_path / "current_binary_run_for_pinning",
        policy=policy,
        mandate_bundle=mandate_bundle,
        context_bundle=context_bundle,
        investigation_bundle=investigation_bundle,
        search_roots=[tmp_path],
    )

    analogs = memory_result.bundle.analog_run_candidates.candidates
    assert analogs
    assert analogs[0]["run_id"] == "analog_pinned"
    assert analogs[0]["memory_pinning_index"]["pin_count"] == 1


def test_run_memory_retrieval_includes_workspace_learnings_and_focus_priors(tmp_path: Path) -> None:
    policy = load_policy().policy
    data_path = write_public_breast_cancer_dataset(tmp_path / "breast_cancer_with_learnings.csv")
    mandate_bundle, context_bundle = _build_binary_foundation(policy)
    investigation_bundle = run_investigation(
        data_path=str(data_path),
        policy=policy,
        mandate_bundle=mandate_bundle,
        context_bundle=context_bundle,
    ).to_dict()
    current_run_dir = tmp_path / "current_binary_with_learnings"
    learnings_dir = tmp_path / "lab_memory"
    learnings_dir.mkdir(parents=True, exist_ok=True)
    write_json(
        learnings_dir / "learnings_state.json",
        {
            "schema_version": "relaytic.learnings_state.v1",
            "generated_at": "2026-03-30T00:00:00+00:00",
            "status": "ok",
            "state_dir": str(learnings_dir),
            "entry_count": 2,
            "entries": [
                {
                    "entry_id": "learning_focus_same_data",
                    "kind": "focus",
                    "lesson": "The selected next-run focus for this problem is `same_data`.",
                    "source_run_id": "prior_run",
                    "applicability_tags": ["binary_classification", "diagnosis_flag", "same_data"],
                    "last_updated_at": "2026-03-30T00:00:00+00:00",
                },
                {
                    "entry_id": "learning_feedback",
                    "kind": "feedback",
                    "lesson": "Accepted feedback in this run pushed Relaytic toward `review_thresholds`.",
                    "source_run_id": "prior_run",
                    "applicability_tags": ["binary_classification", "diagnosis_flag", "feedback"],
                    "last_updated_at": "2026-03-30T00:00:00+00:00",
                },
            ],
        },
        indent=2,
        ensure_ascii=False,
        sort_keys=True,
    )
    current_run_dir.mkdir(parents=True, exist_ok=True)
    write_json(
        current_run_dir / "lab_learnings_snapshot.json",
        {
            "schema_version": "relaytic.lab_learnings_snapshot.v1",
            "generated_at": "2026-03-30T00:00:00+00:00",
            "status": "ok",
            "run_id": "current_binary_with_learnings",
            "active_count": 1,
            "harvested_count": 0,
            "state_entry_count": 2,
            "active_learnings": [
                {
                    "entry_id": "learning_focus_same_data",
                    "kind": "focus",
                    "lesson": "The selected next-run focus for this problem is `same_data`.",
                    "source_run_id": "prior_run",
                    "applicability_tags": ["binary_classification", "diagnosis_flag", "same_data"],
                    "last_updated_at": "2026-03-30T00:00:00+00:00",
                }
            ],
            "harvested_learnings": [],
        },
        indent=2,
        ensure_ascii=False,
        sort_keys=True,
    )

    memory_result = run_memory_retrieval(
        run_dir=current_run_dir,
        policy=policy,
        mandate_bundle=mandate_bundle,
        context_bundle=context_bundle,
        investigation_bundle=investigation_bundle,
        search_roots=[tmp_path / "isolated_memory_root"],
    )

    query_signature = dict(memory_result.bundle.memory_retrieval.query_signature)
    reflection = memory_result.bundle.reflection_memory

    assert query_signature["workspace_recent_focus"] == "same_data"
    assert "focus" in list(query_signature["workspace_learning_kinds"])
    assert "same_data" in list(query_signature["workspace_learning_tags"])
    assert any(item == "workspace_focus:same_data" for item in reflection.reusable_priors)
    assert any("Workspace learnings still carry" in item for item in reflection.lessons)


def test_run_memory_retrieval_prefers_explicit_workspace_focus_over_looser_learning_hints(tmp_path: Path) -> None:
    policy = load_policy().policy
    data_path = write_public_breast_cancer_dataset(tmp_path / "breast_cancer_workspace_truth.csv")
    mandate_bundle, context_bundle = _build_binary_foundation(policy)
    investigation_bundle = run_investigation(
        data_path=str(data_path),
        policy=policy,
        mandate_bundle=mandate_bundle,
        context_bundle=context_bundle,
    ).to_dict()
    current_run_dir = tmp_path / "current_binary_workspace_truth"
    learnings_dir = tmp_path / "lab_memory"
    workspace_dir = tmp_path / "workspace"
    learnings_dir.mkdir(parents=True, exist_ok=True)
    workspace_dir.mkdir(parents=True, exist_ok=True)
    current_run_dir.mkdir(parents=True, exist_ok=True)

    write_json(
        learnings_dir / "learnings_state.json",
        {
            "schema_version": "relaytic.learnings_state.v1",
            "generated_at": "2026-03-31T00:00:00+00:00",
            "status": "ok",
            "state_dir": str(learnings_dir),
            "entry_count": 1,
            "entries": [
                {
                    "entry_id": "learning_focus_same_data",
                    "kind": "focus",
                    "lesson": "Older continuity guidance suggested `same_data`.",
                    "source_run_id": "prior_run",
                    "applicability_tags": ["binary_classification", "diagnosis_flag", "same_data"],
                    "last_updated_at": "2026-03-31T00:00:00+00:00",
                }
            ],
        },
        indent=2,
        ensure_ascii=False,
        sort_keys=True,
    )
    write_json(
        workspace_dir / "workspace_state.json",
        {
            "schema_version": "relaytic.workspace_state.v1",
            "generated_at": "2026-03-31T00:00:00+00:00",
            "status": "active",
            "workspace_id": "workspace_test",
            "workspace_label": "Workspace Test",
            "workspace_dir": str(workspace_dir),
            "current_run_id": current_run_dir.name,
            "current_focus": "new_dataset",
            "continuity_mode": "restart",
            "prior_run_count": 1,
            "next_run_plan_path": str(workspace_dir / "next_run_plan.json"),
            "result_contract_path": str(current_run_dir / "result_contract.json"),
            "learnings_state_path": str(learnings_dir / "learnings_state.json"),
            "summary": "Workspace truth points to a new dataset restart.",
            "trace": {
                "agent": "test",
                "operating_mode": "deterministic",
                "llm_used": False,
                "llm_status": "not_requested",
                "deterministic_evidence": ["workspace_state"],
                "advisory_notes": [],
            },
        },
        indent=2,
        ensure_ascii=False,
        sort_keys=True,
    )

    memory_result = run_memory_retrieval(
        run_dir=current_run_dir,
        policy=policy,
        mandate_bundle=mandate_bundle,
        context_bundle=context_bundle,
        investigation_bundle=investigation_bundle,
        search_roots=[tmp_path / "isolated_memory_root"],
    )

    query_signature = dict(memory_result.bundle.memory_retrieval.query_signature)
    reflection = memory_result.bundle.reflection_memory

    assert query_signature["workspace_recent_focus"] == "new_dataset"
    assert any(item == "workspace_focus:new_dataset" for item in reflection.reusable_priors)
