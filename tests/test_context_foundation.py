from pathlib import Path

from relaytic.context import (
    build_context_controls_from_policy,
    default_data_origin,
    default_domain_brief,
    default_task_brief,
    read_context_bundle,
    write_context_bundle,
)


def test_build_context_controls_from_policy() -> None:
    controls = build_context_controls_from_policy(
        {
            "context": {
                "enabled": True,
                "external_retrieval_allowed": True,
                "allow_uploaded_docs": False,
                "require_provenance": True,
                "semantic_task_enabled": False,
            }
        }
    )
    assert controls.enabled is True
    assert controls.external_retrieval_allowed is True
    assert controls.allow_uploaded_docs is False
    assert controls.semantic_task_enabled is False


def test_default_context_objects_are_usable_without_grounding() -> None:
    controls = build_context_controls_from_policy({"context": {}})
    origin = default_data_origin(controls)
    domain = default_domain_brief(controls)
    task = default_task_brief(controls)
    assert origin.source_type == "snapshot"
    assert "ungrounded mode" in domain.summary
    assert task.success_criteria


def test_write_and_read_context_bundle(tmp_path: Path) -> None:
    run_dir = tmp_path / "run_context"
    controls = build_context_controls_from_policy({"context": {}})
    write_context_bundle(
        run_dir,
        data_origin=default_data_origin(controls, source_name="ops-db"),
        domain_brief=default_domain_brief(controls, system_name="reactor"),
        task_brief=default_task_brief(controls, problem_statement="Predict quality drift."),
    )
    payload = read_context_bundle(run_dir)
    assert payload["data_origin"]["source_name"] == "ops-db"
    assert payload["domain_brief"]["system_name"] == "reactor"
    assert payload["task_brief"]["problem_statement"] == "Predict quality drift."
