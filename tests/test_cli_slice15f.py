from __future__ import annotations

import json
from pathlib import Path

from relaytic.ui.cli import main
from tests.public_datasets import write_public_breast_cancer_dataset


def test_cli_slice15f_materializes_imported_architecture_artifacts_and_explanation(
    tmp_path: Path, capsys
) -> None:
    run_dir = tmp_path / "slice15f_public_binary"
    data_path = write_public_breast_cancer_dataset(tmp_path / "slice15f_breast_cancer.csv")

    assert main(
        [
            "run",
            "--run-dir",
            str(run_dir),
            "--data-path",
            str(data_path),
            "--text",
            "Classify diagnosis_flag from the measurement columns. Do everything on your own.",
            "--format",
            "json",
        ]
    ) == 0
    capsys.readouterr()

    (run_dir / "method_transfer_report.json").write_text(
        json.dumps(
            {
                "status": "ok",
                "accepted_candidates": [
                    {
                        "candidate_kind": "challenger_family",
                        "value": "tabpfn_classifier",
                        "support_reason": "A recent paper suggested TabPFN as a strong small-data classifier.",
                        "source": {
                            "provider": "semantic_scholar",
                            "title": "TabPFN for tabular classification",
                            "url": "https://example.com/tabpfn",
                            "year": 2025,
                        },
                    }
                ],
                "advisory_candidates": [],
                "rejected_candidates": [],
                "summary": "Synthetic research signal for Slice 15F regression coverage.",
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    assert main(["decision", "review", "--run-dir", str(run_dir), "--overwrite", "--format", "json"]) == 0
    decision_payload = json.loads(capsys.readouterr().out)
    assert decision_payload["decision_lab"]["imported_candidate_count"] >= 1

    assert main(
        ["benchmark", "run", "--run-dir", str(run_dir), "--data-path", str(data_path), "--overwrite", "--format", "json"]
    ) == 0
    benchmark_payload = json.loads(capsys.readouterr().out)

    assert benchmark_payload["benchmark"]["imported_candidate_count"] >= 1
    assert benchmark_payload["benchmark"]["quarantined_candidate_count"] >= 1
    for filename in (
        "method_import_report.json",
        "architecture_candidate_registry.json",
        "shadow_trial_manifest.json",
        "shadow_trial_scorecard.json",
        "candidate_quarantine.json",
        "promotion_readiness_report.json",
    ):
        assert (run_dir / filename).exists(), filename

    assert main(
        [
            "assist",
            "turn",
            "--run-dir",
            str(run_dir),
            "--message",
            "why not tabpfn here?",
            "--format",
            "json",
        ]
    ) == 0
    assist_payload = json.loads(capsys.readouterr().out)

    assert assist_payload["audit"]["question_type"] == "why_not_imported_architecture"
    assert "tabpfn" in assist_payload["audit"]["answer"].lower()
    assert "promotion_readiness_report.json" in assist_payload["audit"]["evidence_refs"]
