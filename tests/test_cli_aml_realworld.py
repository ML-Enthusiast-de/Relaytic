from __future__ import annotations

import json
from pathlib import Path

import pytest

pytest.importorskip("sklearn.datasets")

from relaytic.ui.cli import main

from tests.aml_workload_fixtures import write_elliptic_like_dataset, write_paysim_like_dataset


def test_cli_relaytic_aml_paysim_like_run_and_benchmark_work(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    run_dir = tmp_path / "paysim_like_run"
    data_path = write_paysim_like_dataset(tmp_path / "paysim_like.csv")

    assert main(
        [
            "run",
            "--run-dir",
            str(run_dir),
            "--data-path",
            str(data_path),
            "--timestamp-column",
            "step",
                "--text",
                (
                    "Do everything on your own. This is a PaySim style payment fraud investigation. "
                    "Classify isFraud, optimize alerts at fixed false-positive budgets, expand suspicious counterparties, "
                    "and explain why the case is structurally suspicious for analyst review."
                ),
            "--format",
            "json",
        ]
    ) == 0
    run_payload = json.loads(capsys.readouterr().out)

    assert run_payload["status"] == "ok"
    assert run_payload["run_summary"]["aml"]["aml_active"] is True
    assert run_payload["run_summary"]["aml"]["domain_focus"] in {"payment_fraud", "analyst_review"}
    assert run_payload["run_summary"]["aml_graph"]["status"] == "active"
    assert run_payload["run_summary"]["aml_graph"]["node_count"] >= 20
    assert run_payload["run_summary"]["aml_graph"]["typology_hit_count"] >= 1
    assert run_payload["run_summary"]["aml_graph"]["focal_entity"]

    assert main(
        [
            "benchmark",
            "run",
            "--run-dir",
            str(run_dir),
            "--data-path",
            str(data_path),
            "--overwrite",
            "--format",
            "json",
        ]
    ) == 0
    benchmark_payload = json.loads(capsys.readouterr().out)

    assert benchmark_payload["status"] == "ok"
    assert benchmark_payload["benchmark"]["aml_domain_active"] is True
    assert benchmark_payload["benchmark"]["aml_pack_family"] == "aml_flagship_pending"
    assert benchmark_payload["bundle"]["entity_graph_profile"]["source_column"] == "nameOrig"
    assert benchmark_payload["bundle"]["entity_graph_profile"]["destination_column"] == "nameDest"


def test_cli_relaytic_aml_elliptic_like_run_activates_graph_and_temporal_posture(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    run_dir = tmp_path / "elliptic_like_run"
    data_path = write_elliptic_like_dataset(tmp_path / "elliptic_like.csv")

    assert main(
        [
            "run",
            "--run-dir",
            str(run_dir),
            "--data-path",
            str(data_path),
            "--timestamp-column",
            "time_step",
            "--text",
            (
                "Do everything on your own. This is an Elliptic-style temporal AML graph benchmark. "
                "Classify y, preserve time_step order, expand suspicious subgraphs, and explain which entities should be "
                "escalated for analyst review."
            ),
            "--format",
            "json",
        ]
    ) == 0
    payload = json.loads(capsys.readouterr().out)

    assert payload["status"] == "ok"
    assert payload["run_summary"]["aml"]["aml_active"] is True
    assert payload["run_summary"]["aml"]["target_level"] == "subgraph"
    assert payload["run_summary"]["aml_graph"]["status"] == "active"
    assert payload["run_summary"]["aml_graph"]["node_count"] >= 15
    assert payload["run_summary"]["aml_graph"]["typology_hit_count"] >= 1
    assert payload["run_summary"]["aml_graph"]["shadow_winner"] == "structural_baseline"
