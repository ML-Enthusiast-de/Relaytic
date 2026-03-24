import json
from pathlib import Path

from relaytic.profiles import run_profiles_review

from tests.test_completion_agents import _build_executed_run


def _write_runtime_events(run_dir: Path) -> None:
    (run_dir / "lab_event_stream.jsonl").write_text(
        "\n".join(
            [
                json.dumps({"recorded_at": "2026-03-24T10:00:00+00:00", "stage": "investigation"}),
                json.dumps({"recorded_at": "2026-03-24T10:42:00+00:00", "stage": "autonomy"}),
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def test_run_profiles_review_materializes_quality_and_budget_contracts(tmp_path: Path) -> None:
    _, run_dir, policy, mandate_bundle, context_bundle, payloads = _build_executed_run(tmp_path)
    _write_runtime_events(run_dir)

    result = run_profiles_review(
        run_dir=run_dir,
        policy=policy,
        mandate_bundle=mandate_bundle,
        context_bundle=context_bundle,
        intake_bundle=payloads["intake_bundle"],
        investigation_bundle=payloads["investigation_bundle"],
        planning_bundle=payloads["planning_bundle"],
        evidence_bundle=payloads["evidence_bundle"],
    )

    assert result.bundle.quality_contract.status == "contract_materialized"
    assert result.bundle.quality_contract.acceptance_criteria
    assert result.bundle.quality_gate_report.gate_status in {"pass", "conditional_pass", "fail"}
    assert result.bundle.quality_gate_report.measured_metrics
    assert result.bundle.budget_contract.max_trials >= 1
    assert result.bundle.budget_consumption_report.observed_elapsed_minutes == 42.0
    assert result.bundle.budget_consumption_report.estimated_trials_consumed >= 1


def test_operator_profile_changes_posture_without_changing_metric_contract(tmp_path: Path) -> None:
    _, run_dir, policy, mandate_bundle, context_bundle, payloads = _build_executed_run(tmp_path)
    baseline = run_profiles_review(
        run_dir=run_dir,
        policy=policy,
        mandate_bundle=mandate_bundle,
        context_bundle=context_bundle,
        intake_bundle=payloads["intake_bundle"],
        investigation_bundle=payloads["investigation_bundle"],
        planning_bundle=payloads["planning_bundle"],
        evidence_bundle=payloads["evidence_bundle"],
    )

    tuned_mandate = json.loads(json.dumps(mandate_bundle))
    tuned_mandate["work_preferences"]["preferred_report_style"] = "detailed"
    tuned_mandate["work_preferences"]["preferred_effort_tier"] = "minimal"
    tuned = run_profiles_review(
        run_dir=run_dir,
        policy=policy,
        mandate_bundle=tuned_mandate,
        context_bundle=context_bundle,
        intake_bundle=payloads["intake_bundle"],
        investigation_bundle=payloads["investigation_bundle"],
        planning_bundle=payloads["planning_bundle"],
        evidence_bundle=payloads["evidence_bundle"],
    )

    assert baseline.bundle.quality_contract.acceptance_criteria == tuned.bundle.quality_contract.acceptance_criteria
    assert baseline.bundle.operator_profile.explanation_style != tuned.bundle.operator_profile.explanation_style
    assert baseline.bundle.operator_profile.budget_posture != tuned.bundle.operator_profile.budget_posture


def test_lab_profile_overlay_can_raise_benchmark_and_review_posture(tmp_path: Path) -> None:
    _, run_dir, policy, mandate_bundle, context_bundle, payloads = _build_executed_run(tmp_path)
    tuned_policy = json.loads(json.dumps(policy))
    tuned_policy["privacy"]["local_only"] = False
    tuned_policy["benchmark"]["enabled"] = False
    tuned_mandate = json.loads(json.dumps(mandate_bundle))
    tuned_mandate["lab_mandate"]["hard_constraints"] = [
        "Audit every model decision.",
        "Require benchmark evidence before deployment.",
    ]
    tuned_mandate["lab_mandate"]["soft_preferences"] = ["Operate like a regulated bank risk lab."]

    result = run_profiles_review(
        run_dir=run_dir,
        policy=tuned_policy,
        mandate_bundle=tuned_mandate,
        context_bundle=context_bundle,
        intake_bundle=payloads["intake_bundle"],
        investigation_bundle=payloads["investigation_bundle"],
        planning_bundle=payloads["planning_bundle"],
        evidence_bundle=payloads["evidence_bundle"],
    )

    assert result.bundle.lab_operating_profile.review_strictness == "strict"
    assert result.bundle.lab_operating_profile.benchmark_required is True
    assert result.bundle.quality_contract.benchmark_required is True
