import json
from pathlib import Path

import pytest

pytest.importorskip("sklearn.datasets")

from relaytic.ui.cli import main

from tests.public_datasets import write_public_breast_cancer_dataset


def test_cli_intelligence_surfaces_materialize_for_public_binary_run(tmp_path: Path, capsys) -> None:
    run_dir = tmp_path / "intelligence_public_binary"
    data_path = write_public_breast_cancer_dataset(tmp_path / "public_breast_cancer.csv")

    assert main(
        [
            "run",
            "--run-dir",
            str(run_dir),
            "--data-path",
            str(data_path),
            "--text",
            "Do everything on your own. Classify diagnosis_flag from the measurement columns.",
            "--format",
            "json",
        ]
    ) == 0
    payload = json.loads(capsys.readouterr().out)

    assert payload["status"] == "ok"
    assert payload["run_summary"]["stage_completed"] == "autonomy_reviewed"
    assert payload["run_summary"]["intelligence"]["effective_mode"] in {
        "deterministic_only",
        "semantic_fallback_deterministic",
        "semantic_local_llm",
    }
    assert payload["run_summary"]["intelligence"]["recommended_followup_action"] is not None
    assert payload["run_summary"]["intelligence"]["domain_archetype"] is not None

    for filename in (
        "intelligence_mode.json",
        "llm_routing_plan.json",
        "local_llm_profile.json",
        "llm_backend_discovery.json",
        "semantic_task_request.json",
        "semantic_task_results.json",
        "verifier_report.json",
        "semantic_debate_report.json",
        "semantic_counterposition_pack.json",
        "semantic_uncertainty_report.json",
        "intelligence_escalation.json",
        "semantic_proof_report.json",
        "context_assembly_report.json",
        "doc_grounding_report.json",
        "semantic_access_audit.json",
    ):
        assert (run_dir / filename).exists(), filename

    assert main(["intelligence", "show", "--run-dir", str(run_dir), "--format", "json"]) == 0
    intelligence_payload = json.loads(capsys.readouterr().out)

    assert intelligence_payload["status"] == "ok"
    assert intelligence_payload["intelligence"]["effective_mode"] in {
        "deterministic_only",
        "semantic_fallback_deterministic",
        "semantic_local_llm",
    }
    assert intelligence_payload["intelligence"]["routed_mode"] is not None
    assert intelligence_payload["intelligence"]["recommended_mode"] is not None
    assert intelligence_payload["bundle"]["semantic_debate_report"]["status"] == "ok"
    assert intelligence_payload["bundle"]["semantic_debate_report"]["domain_interpretation"]["domain_archetype"] is not None
    assert intelligence_payload["bundle"]["semantic_access_audit"]["row_level_access_granted"] is False
    assert intelligence_payload["bundle"]["llm_routing_plan"]["capability_matrix"]["json_mode"] is True
    assert intelligence_payload["bundle"]["verifier_report"]["status"] == "ok"
    assert "measurable_gain_detected" in intelligence_payload["bundle"]["semantic_proof_report"]

    assert main(["show", "--run-dir", str(run_dir), "--format", "json"]) == 0
    show_payload = json.loads(capsys.readouterr().out)

    assert show_payload["run_summary"]["runtime"]["current_stage"] == "autonomy"
    assert show_payload["run_summary"]["intelligence"]["backend_status"] is not None
    assert show_payload["run_summary"]["intelligence"]["routed_mode"] is not None
