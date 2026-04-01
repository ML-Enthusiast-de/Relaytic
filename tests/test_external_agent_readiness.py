from __future__ import annotations

from pathlib import Path

from relaytic.interoperability import (
    relaytic_assist_turn,
    relaytic_continue_workspace,
    relaytic_reset_learnings,
    relaytic_run,
    relaytic_run_agent_evals,
    relaytic_review_search,
    relaytic_server_info,
    relaytic_show_agent_evals,
    relaytic_show_handoff,
    relaytic_show_learnings,
    relaytic_show_mission_control,
    relaytic_show_search,
    relaytic_show_trace,
    relaytic_show_workspace,
    relaytic_set_next_run_focus,
)
from tests.public_datasets import write_public_breast_cancer_dataset


def test_external_agent_wrappers_support_a_real_run_and_proof_flow(tmp_path: Path) -> None:
    onboarding_payload = relaytic_show_mission_control(expected_profile="full")
    onboarding_bundle = dict(onboarding_payload["surface_payload"]["bundle"])
    onboarding_status = dict(onboarding_bundle["onboarding_status"])
    host_summary = dict(onboarding_status.get("host_summary", {}))

    assert {"claude", "codex", "openclaw"}.issubset(set(host_summary.get("discoverable_now", [])))
    assert "relaytic_agent_handbook.md" in " ".join(str(item) for item in onboarding_status.get("first_steps", []))

    run_dir = tmp_path / "external_agent_run"
    data_path = write_public_breast_cancer_dataset(tmp_path / "external_agent_breast_cancer.csv")

    run_payload = relaytic_run(
        data_path=str(data_path),
        run_dir=str(run_dir),
        text="Do everything on your own. Classify diagnosis_flag from the provided features and keep the operator informed.",
        actor_type="agent",
        channel="codex-smoke",
        overwrite=True,
    )
    assert run_payload["surface_payload"]["status"] == "ok"
    assert run_payload["surface_payload"]["run_summary"]["stage_completed"] is not None

    mission_payload = relaytic_show_mission_control(run_dir=str(run_dir), expected_profile="full")
    mission_control = dict(mission_payload["surface_payload"]["mission_control"])
    assert mission_control["current_stage"] is not None
    assert mission_control["recommended_action"] is not None

    capabilities_payload = relaytic_assist_turn(run_dir=str(run_dir), message="what can you do?")
    assert capabilities_payload["surface_payload"]["status"] == "ok"
    assert capabilities_payload["surface_payload"]["turn"]["intent_type"] == "capabilities"

    handoff_payload = relaytic_show_handoff(run_dir=str(run_dir))
    assert handoff_payload["surface_payload"]["status"] == "ok"
    assert handoff_payload["surface_payload"]["handoff"]["recommended_option_id"] in {"same_data", "add_data", "new_dataset"}

    focus_payload = relaytic_set_next_run_focus(
        run_dir=str(run_dir),
        selection="same_data",
        notes="focus on recall",
        actor_name="codex-smoke",
    )
    assert focus_payload["surface_payload"]["status"] == "ok"
    assert focus_payload["surface_payload"]["next_run_focus"]["selection_id"] == "same_data"

    learnings_payload = relaytic_show_learnings(run_dir=str(run_dir))
    assert learnings_payload["surface_payload"]["status"] == "ok"
    assert learnings_payload["surface_payload"]["learnings_state"]["entry_count"] >= 1

    workspace_payload = relaytic_show_workspace(run_dir=str(run_dir))
    assert workspace_payload["surface_payload"]["status"] == "ok"
    assert workspace_payload["surface_payload"]["workspace"]["workspace_state"]["workspace_id"] is not None
    assert workspace_payload["surface_payload"]["result_contract"]["result_contract"]["status"] is not None

    search_review_payload = relaytic_review_search(run_dir=str(run_dir), overwrite=True)
    assert search_review_payload["surface_payload"]["status"] == "ok"
    assert search_review_payload["surface_payload"]["search"]["recommended_action"] is not None

    search_show_payload = relaytic_show_search(run_dir=str(run_dir))
    assert search_show_payload["surface_payload"]["status"] == "ok"
    assert search_show_payload["surface_payload"]["search"]["value_band"] in {"low", "medium", "high"}

    continue_payload = relaytic_continue_workspace(
        run_dir=str(run_dir),
        direction="same_data",
        notes="continue with the current dataset but focus on recall risk",
        actor_name="codex-smoke",
    )
    assert continue_payload["surface_payload"]["status"] == "ok"
    assert continue_payload["surface_payload"]["continuation"]["selection_id"] == "same_data"
    assert continue_payload["surface_payload"]["run_summary"]["workspace"]["workspace_id"] is not None

    rerun_payload = relaytic_assist_turn(run_dir=str(run_dir), message="go back to planning")
    assert rerun_payload["surface_payload"]["turn"]["action_kind"] == "rerun_stage"
    assert "planning" in list(rerun_payload["surface_payload"]["turn"]["executed_stages"])

    trace_payload = relaytic_show_trace(run_dir=str(run_dir))
    assert trace_payload["surface_payload"]["trace"]["span_count"] > 0
    assert trace_payload["surface_payload"]["trace"]["winning_action"] is not None

    eval_payload = relaytic_run_agent_evals(run_dir=str(run_dir), overwrite=True)
    assert eval_payload["surface_payload"]["evals"]["protocol_status"] == "ok"
    assert eval_payload["surface_payload"]["evals"]["security_status"] == "ok"

    eval_show_payload = relaytic_show_agent_evals(run_dir=str(run_dir))
    assert eval_show_payload["surface_payload"]["evals"]["status"] == "ok"
    assert eval_show_payload["surface_payload"]["evals"]["failed_count"] == 0

    reset_payload = relaytic_reset_learnings(run_dir=str(run_dir))
    assert reset_payload["surface_payload"]["status"] == "ok"
    assert reset_payload["surface_payload"]["reset"]["status"] == "ok"
    assert reset_payload["surface_payload"]["run_summary"]["learnings"]["status"] == "reset"

    server_info = relaytic_server_info()
    assert server_info["status"] == "ok"
    assert "relaytic_show_trace" in server_info["inspection_tools"]
    assert "relaytic_show_handoff" in server_info["inspection_tools"]
    assert "relaytic_show_learnings" in server_info["inspection_tools"]
    assert "relaytic_show_workspace" in server_info["inspection_tools"]
    assert "relaytic_run_agent_evals" in server_info["workflow_tools"]
    assert "relaytic_set_next_run_focus" in server_info["workflow_tools"]
    assert "relaytic_reset_learnings" in server_info["workflow_tools"]
    assert "relaytic_continue_workspace" in server_info["workflow_tools"]
    assert server_info["tool_count"] >= 26
