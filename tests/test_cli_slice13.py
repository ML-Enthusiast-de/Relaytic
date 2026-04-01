from __future__ import annotations

import json
from pathlib import Path

from relaytic.ui.cli import main
from relaytic.workspace import default_workspace_dir
from tests.public_datasets import write_public_breast_cancer_dataset


def test_cli_search_slice_materializes_and_surfaces_search_controller_artifacts(tmp_path: Path, capsys) -> None:
    run_dir = tmp_path / "search_public_binary"
    data_path = write_public_breast_cancer_dataset(tmp_path / "search_breast_cancer.csv")

    assert main(
        [
            "run",
            "--run-dir",
            str(run_dir),
            "--data-path",
            str(data_path),
            "--text",
            "Do everything on your own. Classify diagnosis_flag from the measurement columns and make search decisions explicit.",
            "--format",
            "json",
        ]
    ) == 0
    capsys.readouterr()

    assert main(
        [
            "search",
            "review",
            "--run-dir",
            str(run_dir),
            "--overwrite",
            "--format",
            "json",
        ]
    ) == 0
    payload = json.loads(capsys.readouterr().out)

    assert payload["status"] == "ok"
    assert payload["search"]["recommended_action"] is not None
    assert payload["run_summary"]["search"]["recommended_action"] is not None

    expected_paths = [
        run_dir / "search_controller_plan.json",
        run_dir / "portfolio_search_trace.json",
        run_dir / "hpo_campaign_report.json",
        run_dir / "search_decision_ledger.json",
        run_dir / "execution_backend_profile.json",
        run_dir / "device_allocation.json",
        run_dir / "distributed_run_plan.json",
        run_dir / "scheduler_job_map.json",
        run_dir / "checkpoint_state.json",
        run_dir / "execution_strategy_report.json",
        run_dir / "search_value_report.json",
        run_dir / "search_controller_eval_report.json",
    ]
    for path in expected_paths:
        assert path.exists(), f"Expected artifact missing: {path}"

    assert main(["search", "show", "--run-dir", str(run_dir), "--format", "json"]) == 0
    show_payload = json.loads(capsys.readouterr().out)
    assert show_payload["status"] == "ok"
    assert show_payload["search"]["value_band"] in {"low", "medium", "high"}
    assert show_payload["search"]["selected_execution_profile"] is not None


def test_cli_search_slice_can_override_iteration_toward_add_data(tmp_path: Path, capsys) -> None:
    run_dir = tmp_path / "search_override_binary"
    data_path = write_public_breast_cancer_dataset(tmp_path / "search_override_breast_cancer.csv")

    assert main(
        [
            "run",
            "--run-dir",
            str(run_dir),
            "--data-path",
            str(data_path),
            "--text",
            "Do everything on your own. Classify diagnosis_flag from the measurement columns and keep the next run focused.",
            "--format",
            "json",
        ]
    ) == 0
    capsys.readouterr()

    result_contract_path = run_dir / "result_contract.json"
    confidence_posture_path = run_dir / "confidence_posture.json"
    contract = json.loads(result_contract_path.read_text(encoding="utf-8"))
    contract["recommended_next_move"] = {"direction": "add_data", "action": "collect_more_data"}
    contract["unresolved_items"] = []
    contract["evidence_strength"] = {"overall_strength": "strong"}
    result_contract_path.write_text(json.dumps(contract, indent=2, sort_keys=True), encoding="utf-8")

    confidence = json.loads(confidence_posture_path.read_text(encoding="utf-8"))
    confidence["overall_confidence"] = "high"
    confidence["review_need"] = "optional"
    confidence_posture_path.write_text(json.dumps(confidence, indent=2, sort_keys=True), encoding="utf-8")

    assert main(
        [
            "search",
            "review",
            "--run-dir",
            str(run_dir),
            "--overwrite",
            "--format",
            "json",
        ]
    ) == 0
    payload = json.loads(capsys.readouterr().out)

    workspace_dir = default_workspace_dir(run_dir=run_dir)
    next_run_plan = json.loads((workspace_dir / "next_run_plan.json").read_text(encoding="utf-8"))
    focus_record = json.loads((run_dir / "focus_decision_record.json").read_text(encoding="utf-8"))

    assert payload["search"]["recommended_direction"] == "add_data"
    assert payload["search"]["stop_search_explicit"] is True
    assert next_run_plan["recommended_direction"] == "add_data"
    assert focus_record["source"] == "relaytic_search_controller"
