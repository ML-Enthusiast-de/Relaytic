from __future__ import annotations

import json
from pathlib import Path

from relaytic.ui.cli import main
from tests.public_datasets import write_public_breast_cancer_dataset


def test_cli_slice15i_materializes_staged_search_artifacts(tmp_path: Path, capsys) -> None:
    run_dir = tmp_path / "slice15i_search_binary"
    data_path = write_public_breast_cancer_dataset(tmp_path / "slice15i_breast_cancer.csv")

    assert main(
        [
            "run",
            "--run-dir",
            str(run_dir),
            "--data-path",
            str(data_path),
            "--text",
            "Classify diagnosis_flag from the measurement columns and make the staged search budget explicit.",
            "--format",
            "json",
        ]
    ) == 0
    capsys.readouterr()

    result_contract_path = run_dir / "result_contract.json"
    confidence_posture_path = run_dir / "confidence_posture.json"
    beat_target_contract_path = run_dir / "beat_target_contract.json"

    result_contract = json.loads(result_contract_path.read_text(encoding="utf-8"))
    result_contract["recommended_next_move"] = {"direction": "same_data", "action": "search_more"}
    result_contract["unresolved_items"] = [{"id": "u1"}, {"id": "u2"}]
    result_contract["evidence_strength"] = {"overall_strength": "mixed"}
    result_contract_path.write_text(json.dumps(result_contract, indent=2, sort_keys=True), encoding="utf-8")

    confidence_posture = json.loads(confidence_posture_path.read_text(encoding="utf-8"))
    confidence_posture["overall_confidence"] = "low"
    confidence_posture["review_need"] = "required"
    confidence_posture_path.write_text(json.dumps(confidence_posture, indent=2, sort_keys=True), encoding="utf-8")

    beat_target_contract_path.write_text(
        json.dumps({"contract_state": "unmet"}, indent=2, sort_keys=True),
        encoding="utf-8",
    )

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
    search_summary = dict(payload["run_summary"]["search"])
    assert search_summary["budget_profile"] == "test"
    assert search_summary["probe_family_count"] >= 1
    assert search_summary["race_family_count"] >= 1
    assert search_summary["finalist_count"] >= 1

    for artifact_name in (
        "search_budget_envelope.json",
        "probe_stage_report.json",
        "family_race_report.json",
        "finalist_search_plan.json",
        "multi_fidelity_pruning_report.json",
        "portfolio_search_scorecard.json",
        "search_stop_reason.json",
    ):
        assert (run_dir / artifact_name).exists(), artifact_name
