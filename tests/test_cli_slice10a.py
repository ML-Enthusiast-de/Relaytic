from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

pytest.importorskip("sklearn.datasets")

from relaytic.interoperability import relaytic_show_decision, relaytic_show_run
from relaytic.ui.cli import main

from tests.public_datasets import write_public_breast_cancer_dataset


def test_cli_run_materializes_slice10a_decision_lab_and_show_surface(tmp_path: Path, capsys) -> None:
    run_dir = tmp_path / "decision_public_binary"
    data_path = write_public_breast_cancer_dataset(tmp_path / "decision_public_breast_cancer.csv")

    assert main(
        [
            "run",
            "--run-dir",
            str(run_dir),
            "--data-path",
            str(data_path),
            "--text",
            "Do everything on your own. Predict diagnosis_flag from the provided features.",
            "--format",
            "json",
        ]
    ) == 0
    payload = json.loads(capsys.readouterr().out)

    data_copies = run_dir / "data_copies"
    primary_copy = Path(payload["run_summary"]["data"]["working_copy_path"])
    if not primary_copy.is_absolute():
        primary_copy = run_dir / primary_copy
    candidate_copy = data_copies / "nearby_context.csv"
    shutil.copyfile(primary_copy, candidate_copy)

    assert main(
        [
            "decision",
            "review",
            "--run-dir",
            str(run_dir),
            "--overwrite",
            "--format",
            "json",
        ]
    ) == 0
    decision_payload = json.loads(capsys.readouterr().out)

    decision_lab = dict(decision_payload["decision_lab"])
    assert decision_payload["status"] == "ok"
    assert decision_lab["action_regime"] is not None
    assert decision_lab["selected_strategy"] in {
        "additional_local_data",
        "broader_search",
        "operator_review",
        "hold_current_course",
    }
    assert decision_lab["next_actor"] is not None
    assert decision_lab["selected_next_action"] is not None
    assert decision_lab["compiled_challenger_count"] >= 1
    assert decision_lab["compiled_feature_count"] >= 1

    for filename in (
        "decision_world_model.json",
        "controller_policy.json",
        "handoff_controller_report.json",
        "intervention_policy_report.json",
        "decision_usefulness_report.json",
        "value_of_more_data_report.json",
        "data_acquisition_plan.json",
        "source_graph.json",
        "join_candidate_report.json",
        "method_compiler_report.json",
        "compiled_challenger_templates.json",
        "compiled_feature_hypotheses.json",
        "compiled_benchmark_protocol.json",
    ):
        assert (run_dir / filename).exists(), filename

    assert main(["decision", "show", "--run-dir", str(run_dir), "--format", "json"]) == 0
    show_payload = json.loads(capsys.readouterr().out)
    assert show_payload["decision_lab"]["selected_next_action"] == decision_lab["selected_next_action"]

    assert main(["show", "--run-dir", str(run_dir), "--format", "json"]) == 0
    show_run_payload = json.loads(capsys.readouterr().out)
    run_summary = dict(show_run_payload["run_summary"])
    assert dict(run_summary.get("decision_lab", {}))["selected_next_action"] == decision_lab["selected_next_action"]
    assert run_summary["next_step"]["recommended_action"] is not None

    interop_decision = relaytic_show_decision(run_dir=str(run_dir))
    assert interop_decision["surface_payload"]["decision_lab"]["selected_next_action"] == decision_lab["selected_next_action"]

    interop_summary = relaytic_show_run(run_dir=str(run_dir))
    assert interop_summary["surface_payload"]["run_summary"]["decision_lab"]["selected_next_action"] == decision_lab["selected_next_action"]
