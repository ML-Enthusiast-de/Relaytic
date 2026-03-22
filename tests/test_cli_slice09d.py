from __future__ import annotations

import json
from pathlib import Path

import pytest

pytest.importorskip("sklearn.datasets")

from relaytic.ui.cli import main

from tests.public_datasets import write_public_breast_cancer_dataset
from tests.research_test_server import ResearchTestServer


def test_cli_research_slice_materializes_and_influences_autonomy_on_public_dataset(tmp_path: Path, capsys) -> None:
    run_dir = tmp_path / "research_public_binary"
    data_path = write_public_breast_cancer_dataset(tmp_path / "public_breast_cancer.csv")
    semantic_payload = {
        "data": [
            {
                "title": "Random forest benchmark for customer churn classification",
                "abstract": "Random forest baselines remain strong challengers for tabular churn and diagnosis tasks.",
                "year": 2025,
                "url": "https://example.org/rf-benchmark",
                "citationCount": 14,
                "publicationTypes": ["JournalArticle"],
            },
            {
                "title": "Probability calibration for binary classification",
                "abstract": "Calibration and threshold review improve operational binary decision quality.",
                "year": 2024,
                "url": "https://example.org/calibration",
                "citationCount": 9,
                "publicationTypes": ["JournalArticle"],
            },
        ]
    }
    crossref_payload = {
        "message": {
            "items": [
                {
                    "title": ["Binary classification benchmark baselines"],
                    "URL": "https://example.org/binary-benchmark",
                    "type": "journal-article",
                    "container-title": ["Benchmark Letters"],
                    "issued": {"date-parts": [[2024]]},
                    "is-referenced-by-count": 5,
                }
            ]
        }
    }

    with ResearchTestServer(semantic_payload=semantic_payload, crossref_payload=crossref_payload) as server:
        config_path = tmp_path / "research_config.yaml"
        config_path.write_text(
            "\n".join(
                [
                    "privacy:",
                    "  api_calls_allowed: true",
                    "runtime:",
                    "  semantic_rowless_default: true",
                    "  timeout_seconds: 5",
                    "research:",
                    "  enabled: true",
                    f"  semantic_scholar_endpoint: {server.semantic_url}",
                    f"  crossref_endpoint: {server.crossref_url}",
                ]
            ),
            encoding="utf-8",
        )

        assert main(
            [
                "run",
                "--run-dir",
                str(run_dir),
                "--data-path",
                str(data_path),
                "--config",
                str(config_path),
                "--text",
                "Do everything on your own. Classify diagnosis_flag from the measurement columns and benchmark against strong references.",
                "--format",
                "json",
            ]
        ) == 0
        payload = json.loads(capsys.readouterr().out)

    assert payload["status"] == "ok"
    assert payload["run_summary"]["stage_completed"] == "autonomy_reviewed"
    assert payload["run_summary"]["research"]["source_count"] >= 2
    assert payload["run_summary"]["research"]["accepted_transfer_count"] >= 1
    assert payload["run_summary"]["research"]["network_allowed"] is True

    audit = json.loads((run_dir / "external_research_audit.json").read_text(encoding="utf-8"))
    assert audit["raw_rows_exported"] is False
    assert audit["identifier_leak_detected"] is False

    queue = json.loads((run_dir / "challenger_queue.json").read_text(encoding="utf-8"))
    branches = list(queue.get("branches", []))
    assert branches
    assert queue["selected_action"] == "run_recalibration_pass"
    assert branches[0]["requested_model_family"] in {
        "boosted_tree_classifier",
        "bagged_tree_classifier",
    }
    assert "research_calibration_review" in branches[0]["reason_codes"]

    transfer = json.loads((run_dir / "method_transfer_report.json").read_text(encoding="utf-8"))
    accepted = list(transfer.get("accepted_candidates", []))
    assert accepted
    assert any(str(item.get("candidate_kind", "")).strip() for item in accepted)

    assert main(["research", "show", "--run-dir", str(run_dir), "--format", "json"]) == 0
    research_payload = json.loads(capsys.readouterr().out)
    assert research_payload["research"]["accepted_transfer_count"] >= 1

    assert main(["research", "sources", "--run-dir", str(run_dir), "--format", "json"]) == 0
    sources_payload = json.loads(capsys.readouterr().out)
    assert sources_payload["source_count"] >= 2
