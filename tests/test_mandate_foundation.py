from pathlib import Path

from relaytic.mandate import (
    MandateControl,
    build_mandate_controls_from_policy,
    build_run_brief,
    build_work_preferences,
    default_lab_mandate,
    read_mandate_bundle,
    write_mandate_bundle,
)


def test_mandate_control_rejects_invalid_influence_mode() -> None:
    try:
        MandateControl(influence_mode="invalid")
    except ValueError:
        return
    raise AssertionError("Expected ValueError for invalid influence mode.")


def test_build_mandate_controls_from_policy() -> None:
    controls = build_mandate_controls_from_policy(
        {
            "mandate": {
                "enabled": True,
                "influence_mode": "binding",
                "allow_agent_challenges": False,
                "require_disagreement_logging": True,
                "allow_soft_preference_override_with_evidence": False,
            }
        }
    )
    assert controls.enabled is True
    assert controls.influence_mode == "binding"
    assert controls.allow_agent_challenges is False


def test_default_lab_mandate_contains_relaytic_values() -> None:
    mandate = default_lab_mandate(MandateControl())
    assert "local-first execution" in mandate.values
    assert "persist raw secrets into artifacts" in mandate.prohibited_actions


def test_build_work_preferences_and_run_brief_use_policy_defaults() -> None:
    policy = {
        "autonomy": {"execution_mode": "autonomous", "operation_mode": "daemon"},
        "compute": {"default_effort_tier": "deep"},
        "optimization": {"objective": "best_robust_pareto_front"},
        "constraints": {"uncertainty_required": True},
    }
    controls = MandateControl()
    work = build_work_preferences(controls, policy=policy)
    brief = build_run_brief(controls, policy=policy)
    assert work.execution_mode_preference == "autonomous"
    assert work.operation_mode_preference == "daemon"
    assert work.preferred_effort_tier == "deep"
    assert brief.objective == "best_robust_pareto_front"
    assert brief.success_criteria


def test_write_and_read_mandate_bundle(tmp_path: Path) -> None:
    run_dir = tmp_path / "run_mandate"
    controls = MandateControl()
    write_mandate_bundle(
        run_dir,
        lab_mandate=default_lab_mandate(controls),
        work_preferences=build_work_preferences(controls, policy={}),
        run_brief=build_run_brief(controls, policy={}),
    )
    payload = read_mandate_bundle(run_dir)
    assert payload["lab_mandate"]["schema_version"] == "relaytic.lab_mandate.v1"
    assert payload["work_preferences"]["schema_version"] == "relaytic.work_preferences.v1"
    assert payload["run_brief"]["schema_version"] == "relaytic.run_brief.v1"
