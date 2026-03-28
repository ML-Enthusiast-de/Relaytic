import csv
from pathlib import Path

from relaytic.context import (
    build_context_controls_from_policy,
    default_data_origin,
    default_domain_brief,
    default_task_brief,
)
from relaytic.intake import run_intake_interpretation
from relaytic.mandate import (
    build_mandate_controls_from_policy,
    build_run_brief,
    build_work_preferences,
    default_lab_mandate,
)
from relaytic.policies import load_policy


def _write_dataset(path: Path) -> Path:
    rows = [
        ["timestamp", "sensor_a", "sensor_b", "failure_flag", "future_failure_flag", "post_inspection_flag"],
        ["2025-01-01T00:00:00", 10.0, 100.0, 0, 0, 0],
        ["2025-01-01T00:01:00", 11.0, 101.0, 0, 0, 0],
        ["2025-01-01T00:02:00", 12.0, 102.0, 1, 1, 1],
        ["2025-01-01T00:03:00", 13.0, 103.0, 0, 0, 0],
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerows(rows)
    return path


def _write_multiclass_dataset(path: Path) -> Path:
    rows = [
        ["feature_a", "feature_b", "wine_class"],
        [0.1, 1.2, 0],
        [0.2, 1.1, 0],
        [0.3, 1.0, 0],
        [1.1, 2.2, 1],
        [1.2, 2.1, 1],
        [1.3, 2.0, 1],
        [2.1, 3.2, 2],
        [2.2, 3.1, 2],
        [2.3, 3.0, 2],
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerows(rows)
    return path


def _build_foundation(policy: dict) -> tuple[dict, dict]:
    mandate_controls = build_mandate_controls_from_policy(policy)
    context_controls = build_context_controls_from_policy(policy)
    mandate_bundle = {
        "lab_mandate": default_lab_mandate(mandate_controls).to_dict(),
        "work_preferences": build_work_preferences(mandate_controls, policy=policy).to_dict(),
        "run_brief": build_run_brief(mandate_controls, policy=policy).to_dict(),
    }
    context_bundle = {
        "data_origin": default_data_origin(context_controls).to_dict(),
        "domain_brief": default_domain_brief(context_controls).to_dict(),
        "task_brief": default_task_brief(context_controls).to_dict(),
    }
    return mandate_bundle, context_bundle


def test_run_intake_interpretation_deterministically_updates_foundation(tmp_path: Path) -> None:
    data_path = _write_dataset(tmp_path / "intake.csv")
    policy = load_policy().policy
    mandate_bundle, context_bundle = _build_foundation(policy)

    resolution = run_intake_interpretation(
        message=(
            "Predict failure_flag from sensor_a. Do not use future_failure_flag or post_inspection_flag. "
            "Laptop CPU only. Must stay local. Success means catch failures before scrap. "
            "If we miss failures, scrap increases."
        ),
        actor_type="user",
        actor_name="operator_a",
        channel="cli",
        policy=policy,
        mandate_bundle=mandate_bundle,
        context_bundle=context_bundle,
        data_path=str(data_path),
    )

    assert resolution.task_brief.target_column == "failure_flag"
    assert "future_failure_flag" in resolution.domain_brief.forbidden_features
    assert "post_inspection_flag" in resolution.domain_brief.forbidden_features
    assert resolution.run_brief.deployment_target is not None
    assert "laptop" in resolution.run_brief.deployment_target
    assert "do not require remote APIs by default" in resolution.lab_mandate.hard_constraints
    assert resolution.intake_bundle.intake_record.schema_validation
    assert resolution.intake_bundle.intake_record.schema_validation[0]["integration"] == "pandera"
    assert any(match.field == "task_brief.target_column" for match in resolution.intake_bundle.semantic_mapping.field_matches)


def test_run_intake_interpretation_accepts_human_actor_alias(tmp_path: Path) -> None:
    data_path = _write_dataset(tmp_path / "human_alias.csv")
    policy = load_policy().policy
    mandate_bundle, context_bundle = _build_foundation(policy)

    resolution = run_intake_interpretation(
        message="Predict failure_flag from sensor_a.",
        actor_type="human",
        actor_name="operator_alias",
        channel="mission_control_chat",
        policy=policy,
        mandate_bundle=mandate_bundle,
        context_bundle=context_bundle,
        data_path=str(data_path),
    )

    assert resolution.intake_bundle.intake_record.actor_type == "operator"
    assert resolution.task_brief.target_column == "failure_flag"


def test_run_intake_interpretation_parses_structured_template_fields(tmp_path: Path) -> None:
    data_path = _write_dataset(tmp_path / "template.csv")
    policy = load_policy().policy
    mandate_bundle, context_bundle = _build_foundation(policy)

    resolution = run_intake_interpretation(
        message="\n".join(
            [
                "target_column: failure_flag",
                "source_name: line_alarm_history",
                "system_name: production_line",
                "primary_stakeholder: operations team",
                "report_style: detailed",
                "effort_tier: deep",
                "lab_values: protect local-first defaults, favor inspectable behavior",
                "forbidden_features: future_failure_flag, post_inspection_flag",
            ]
        ),
        actor_type="agent",
        actor_name="planner_bot",
        channel="tool",
        policy=policy,
        mandate_bundle=mandate_bundle,
        context_bundle=context_bundle,
        data_path=str(data_path),
    )

    assert resolution.task_brief.target_column == "failure_flag"
    assert resolution.data_origin.source_name == "line_alarm_history"
    assert resolution.domain_brief.system_name == "production_line"
    assert resolution.task_brief.primary_stakeholder == "operations team"
    assert resolution.work_preferences.preferred_report_style == "detailed"
    assert resolution.work_preferences.preferred_effort_tier == "deep"
    assert "protect local-first defaults" in resolution.lab_mandate.values


def test_run_intake_interpretation_infers_task_type_and_domain_archetype_hints(tmp_path: Path) -> None:
    data_path = _write_dataset(tmp_path / "fraud_intake.csv")
    policy = load_policy().policy
    mandate_bundle, context_bundle = _build_foundation(policy)

    resolution = run_intake_interpretation(
        message=(
            "Detect fraud_flag from transaction risk signals. "
            "Fraud review capacity is limited, but missed fraud is expensive."
        ),
        actor_type="user",
        actor_name="risk_lead",
        channel="cli",
        policy=policy,
        mandate_bundle=mandate_bundle,
        context_bundle=context_bundle,
        data_path=str(data_path),
    )

    assert resolution.task_brief.task_type_hint == "fraud_detection"
    assert resolution.task_brief.domain_archetype_hint == "fraud_risk"


def test_run_intake_interpretation_uses_dataset_evidence_for_multiclass_targets(tmp_path: Path) -> None:
    data_path = _write_multiclass_dataset(tmp_path / "multiclass_intake.csv")
    policy = load_policy().policy
    mandate_bundle, context_bundle = _build_foundation(policy)

    resolution = run_intake_interpretation(
        message="Classify wine_class from the available measurements. Do everything on your own.",
        actor_type="user",
        actor_name="operator_multi",
        channel="cli",
        policy=policy,
        mandate_bundle=mandate_bundle,
        context_bundle=context_bundle,
        data_path=str(data_path),
    )

    assert resolution.task_brief.target_column == "wine_class"
    assert resolution.task_brief.task_type_hint == "multiclass_classification"


def test_run_intake_interpretation_logs_conflict_instead_of_overwriting_existing_target(tmp_path: Path) -> None:
    data_path = _write_dataset(tmp_path / "conflict.csv")
    policy = load_policy().policy
    mandate_bundle, context_bundle = _build_foundation(policy)
    context_bundle["task_brief"]["target_column"] = "post_inspection_flag"

    resolution = run_intake_interpretation(
        message="Predict failure_flag from sensor_a.",
        actor_type="user",
        actor_name=None,
        channel="cli",
        policy=policy,
        mandate_bundle=mandate_bundle,
        context_bundle=context_bundle,
        data_path=str(data_path),
    )

    assert resolution.task_brief.target_column == "post_inspection_flag"
    assert any("task_brief.target_column" in item for item in resolution.intake_bundle.context_interpretation.conflicts)


def test_run_intake_interpretation_enters_autonomous_mode_and_logs_assumptions(tmp_path: Path) -> None:
    data_path = tmp_path / "autonomy.csv"
    rows = [
        ["timestamp", "sensor_a", "failure_flag", "quality_score", "future_failure_flag", "post_inspection_flag"],
        ["2025-01-01T00:00:00", 10.0, 0, 0.1, 0, 0],
        ["2025-01-01T00:01:00", 11.0, 1, 0.9, 1, 1],
    ]
    with data_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerows(rows)

    policy = load_policy().policy
    mandate_bundle, context_bundle = _build_foundation(policy)

    resolution = run_intake_interpretation(
        message=(
            "Do everything on your own and find out the target from the data. "
            "Do not use future or post inspection columns."
        ),
        actor_type="user",
        actor_name="operator_autonomy",
        channel="cli",
        policy=policy,
        mandate_bundle=mandate_bundle,
        context_bundle=context_bundle,
        data_path=str(data_path),
    )

    autonomy_mode = resolution.intake_bundle.autonomy_mode
    clarification_queue = resolution.intake_bundle.clarification_queue
    assumption_log = resolution.intake_bundle.assumption_log

    assert autonomy_mode.requested_mode == "autonomous"
    assert autonomy_mode.proceed_without_answers is True
    assert autonomy_mode.suppress_noncritical_questions is True
    assert autonomy_mode.operator_signal == "do everything on your own"
    assert clarification_queue.items
    assert all(item.optional is True for item in clarification_queue.items)
    assert all(item.blocking_class == "never" for item in clarification_queue.items)
    assert all(item.status == "suppressed_by_autonomy" for item in clarification_queue.items)
    assert assumption_log.entries
    assert any(entry.category == "operating_mode" for entry in assumption_log.entries)
    assert resolution.intake_bundle.context_interpretation.assumptions
    assert resolution.intake_bundle.context_constraints.assumptions
