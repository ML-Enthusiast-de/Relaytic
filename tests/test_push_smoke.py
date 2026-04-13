from __future__ import annotations

import json

from relaytic.interoperability import relaytic_show_handoff, relaytic_show_workspace
from relaytic.ui.cli import main


def test_push_smoke_core_cli_surfaces(push_smoke_run: dict[str, object], capsys) -> None:
    run_dir = push_smoke_run["run_dir"]

    assert main(["show", "--run-dir", str(run_dir), "--format", "json"]) == 0
    summary_payload = json.loads(capsys.readouterr().out)
    assert summary_payload["status"] == "ok"
    assert summary_payload["run_summary"]["decision"]["task_type"] in {
        "binary_classification",
        "rare_event_supervised",
    }

    assert main(["runtime", "show", "--run-dir", str(run_dir), "--format", "json"]) == 0
    runtime_payload = json.loads(capsys.readouterr().out)
    assert runtime_payload["status"] == "ok"
    assert runtime_payload["runtime"]["event_count"] >= 1

    assert main(["benchmark", "show", "--run-dir", str(run_dir), "--format", "json"]) == 0
    benchmark_payload = json.loads(capsys.readouterr().out)
    assert benchmark_payload["status"] == "ok"
    assert benchmark_payload["benchmark"]["reference_count"] >= 2

    workspace_payload = relaytic_show_workspace(run_dir=str(run_dir))
    assert workspace_payload["surface_payload"]["status"] == "ok"
    assert workspace_payload["surface_payload"]["workspace"]["workspace_state"]["workspace_id"] is not None

    handoff_payload = relaytic_show_handoff(run_dir=str(run_dir))
    assert handoff_payload["surface_payload"]["status"] == "ok"
    assert handoff_payload["surface_payload"]["handoff"]["recommended_option_id"] in {
        "same_data",
        "add_data",
        "new_dataset",
    }
