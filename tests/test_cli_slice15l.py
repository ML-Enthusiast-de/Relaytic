from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import pytest

pytest.importorskip("sklearn.datasets")

from relaytic.interoperability import relaytic_show_agent_evals
from relaytic.ui.cli import main
from tests.public_datasets import write_public_breast_cancer_dataset


def test_cli_slice15l_clean_public_binary_run_marks_benchmark_safe_to_cite(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    run_dir = tmp_path / "slice15l_public_binary"
    data_path = write_public_breast_cancer_dataset(tmp_path / "slice15l_public_breast_cancer.csv")

    assert main(
        [
            "run",
            "--run-dir",
            str(run_dir),
            "--data-path",
            str(data_path),
            "--text",
            "Classify diagnosis_flag from the measurement columns, benchmark against strong references, and explain whether the result is safe to cite publicly.",
            "--format",
            "json",
        ]
    ) == 0
    capsys.readouterr()

    assert main(["benchmark", "run", "--run-dir", str(run_dir), "--data-path", str(data_path), "--overwrite", "--format", "json"]) == 0
    payload = json.loads(capsys.readouterr().out)

    assert payload["status"] == "ok"
    assert payload["benchmark"]["paper_status"] == "ok"
    assert payload["benchmark"]["claim_gate_status"] == "safe_to_cite_publicly"
    assert payload["benchmark"]["safe_to_cite_publicly"] is True
    assert payload["benchmark"]["truth_audit_status"] == "ok"
    assert payload["bundle"]["benchmark_release_gate"]["status"] == "safe_to_cite_publicly"
    assert payload["bundle"]["paper_claim_guard_report"]["safe_to_cite_publicly"] is True
    assert payload["bundle"]["trace_identity_conformance"]["status"] == "ok"
    assert payload["bundle"]["eval_surface_parity_report"]["status"] == "ok"

    for filename in (
        "trace_identity_conformance.json",
        "eval_surface_parity_report.json",
        "benchmark_truth_audit.json",
        "paper_claim_guard_report.json",
        "benchmark_release_gate.json",
        "dataset_leakage_audit.json",
    ):
        assert (run_dir / filename).exists(), filename


def test_cli_slice15l_temporal_claim_gate_blocks_degenerate_public_claim(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    run_dir = tmp_path / "slice15l_temporal_block"
    data_path = tmp_path / "slice15l_temporal_block.csv"
    frame = pd.DataFrame(
        {
            "timestamp": pd.date_range("2026-01-01 00:00:00", periods=60, freq="5min"),
            "sensor_a": [float(index % 7) for index in range(60)],
            "sensor_b": [float((index * 5) % 13) for index in range(60)],
            "occupancy_flag": [1 if index < 12 else 0 for index in range(60)],
        }
    )
    frame["timestamp"] = frame["timestamp"].dt.strftime("%Y-%m-%d %H:%M:%S")
    frame.to_csv(data_path, index=False)

    assert main(
        [
            "run",
            "--run-dir",
            str(run_dir),
            "--data-path",
            str(data_path),
            "--text",
            "Classify occupancy_flag from the room sensor columns over time, benchmark against strong references, and tell me if the result is safe for a paper.",
            "--format",
            "json",
        ]
    ) == 0
    capsys.readouterr()

    assert main(["benchmark", "run", "--run-dir", str(run_dir), "--data-path", str(data_path), "--overwrite", "--format", "json"]) == 0
    payload = json.loads(capsys.readouterr().out)

    assert payload["status"] == "ok"
    assert payload["benchmark"]["safe_to_cite_publicly"] is False
    assert payload["benchmark"]["truth_audit_status"] == "blocked"
    assert payload["bundle"]["paper_claim_guard_report"]["safe_to_cite_publicly"] is False
    assert "temporal_fold_health_blocked" in payload["bundle"]["paper_claim_guard_report"]["blocked_reason_codes"]
    assert payload["bundle"]["benchmark_release_gate"]["status"] in {"demo_only", "blocked"}


def test_cli_slice15l_evals_surface_materializes_trace_identity_and_surface_parity(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    run_dir = tmp_path / "slice15l_eval_parity"
    data_path = write_public_breast_cancer_dataset(tmp_path / "slice15l_eval_parity.csv")

    assert main(
        [
            "run",
            "--run-dir",
            str(run_dir),
            "--data-path",
            str(data_path),
            "--text",
            "Classify diagnosis_flag from the measurement columns and explain the trace state.",
            "--format",
            "json",
        ]
    ) == 0
    capsys.readouterr()

    assert main(["evals", "show", "--run-dir", str(run_dir), "--format", "json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["status"] == "ok"
    assert payload["evals"]["trace_identity_status"] == "ok"
    assert payload["evals"]["surface_parity_status"] == "ok"
    assert payload["bundle"]["trace_identity_conformance"]["mismatch_count"] == 0
    assert payload["bundle"]["eval_surface_parity_report"]["status"] == "ok"

    interop_payload = relaytic_show_agent_evals(run_dir=str(run_dir))
    assert interop_payload["surface_payload"]["evals"]["trace_identity_status"] == "ok"


def test_cli_slice15l_assist_explains_public_claim_gate(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    run_dir = tmp_path / "slice15l_assist_claim_gate"
    data_path = tmp_path / "slice15l_assist_claim_gate.csv"
    frame = pd.DataFrame(
        {
            "timestamp": pd.date_range("2026-02-01 00:00:00", periods=60, freq="5min"),
            "sensor_a": [float(index % 5) for index in range(60)],
            "sensor_b": [float((index * 3) % 11) for index in range(60)],
            "occupancy_flag": [1 if index < 10 else 0 for index in range(60)],
        }
    )
    frame["timestamp"] = frame["timestamp"].dt.strftime("%Y-%m-%d %H:%M:%S")
    frame.to_csv(data_path, index=False)

    assert main(
        [
            "run",
            "--run-dir",
            str(run_dir),
            "--data-path",
            str(data_path),
            "--text",
            "Classify occupancy_flag from the room sensor columns over time, benchmark against strong references, and explain the route.",
            "--format",
            "json",
        ]
    ) == 0
    capsys.readouterr()
    assert main(["benchmark", "run", "--run-dir", str(run_dir), "--data-path", str(data_path), "--overwrite", "--format", "json"]) == 0
    capsys.readouterr()

    assert main(
        [
            "assist",
            "turn",
            "--run-dir",
            str(run_dir),
            "--message",
            "why is this blocked from public claim?",
            "--format",
            "json",
        ]
    ) == 0
    payload = json.loads(capsys.readouterr().out)

    assert payload["status"] == "ok"
    assert payload["turn"]["intent_type"] == "explain"
    assert payload["turn"]["audit_question_type"] == "paper_claim_gate"
    assert "public" in payload["turn"]["response_message"].lower()
    assert "benchmark_release_gate.json" in payload["audit"]["evidence_refs"]
