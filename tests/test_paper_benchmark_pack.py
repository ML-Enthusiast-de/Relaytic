import json
import os
from pathlib import Path

import pytest

pytest.importorskip("sklearn.datasets")
pytest.importorskip("ucimlrepo")

from relaytic.ui.cli import main

from tests.paper_benchmark_datasets import (
    PAPER_BENCHMARK_DATASETS,
    REPRESENTATIVE_PAPER_BENCHMARK_EVAL_DATASETS,
    PaperBenchmarkDatasetSpec,
)


pytestmark = pytest.mark.skipif(
    os.environ.get("RELAYTIC_ENABLE_PAPER_BENCHMARKS", "").strip() != "1",
    reason="Set RELAYTIC_ENABLE_PAPER_BENCHMARKS=1 to run the optional paper-grade benchmark and eval pack.",
)


def _run_dataset(spec: PaperBenchmarkDatasetSpec, *, tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> tuple[Path, dict[str, object]]:
    run_dir = tmp_path / spec.dataset_key
    data_path = spec.writer(tmp_path / f"{spec.dataset_key}.csv")
    assert main(
        [
            "run",
            "--run-dir",
            str(run_dir),
            "--data-path",
            str(data_path),
            "--text",
            spec.objective_text,
            "--format",
            "json",
        ]
    ) == 0
    payload = json.loads(capsys.readouterr().out)
    return run_dir, payload


@pytest.mark.parametrize("spec", PAPER_BENCHMARK_DATASETS, ids=lambda spec: spec.pytest_id)
def test_cli_run_supports_paper_benchmark_dataset_matrix(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    spec: PaperBenchmarkDatasetSpec,
) -> None:
    _, payload = _run_dataset(spec, tmp_path=tmp_path, capsys=capsys)

    assert payload["status"] == "ok"
    assert payload["run_summary"]["decision"]["task_type"] in spec.expected_task_types
    assert payload["run_summary"]["decision"]["target_column"] == spec.target_column
    assert payload["run_summary"]["data"]["row_count"] == spec.expected_rows


@pytest.mark.parametrize(
    "spec",
    REPRESENTATIVE_PAPER_BENCHMARK_EVAL_DATASETS,
    ids=lambda spec: spec.pytest_id,
)
def test_cli_paper_benchmark_pack_materializes_benchmark_and_eval_surfaces(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    spec: PaperBenchmarkDatasetSpec,
) -> None:
    run_dir, payload = _run_dataset(spec, tmp_path=tmp_path, capsys=capsys)

    assert payload["status"] == "ok"
    assert payload["run_summary"]["decision"]["task_type"] in spec.expected_task_types

    assert main(["benchmark", "run", "--run-dir", str(run_dir), "--overwrite", "--format", "json"]) == 0
    benchmark_payload = json.loads(capsys.readouterr().out)
    assert benchmark_payload["status"] == "ok"
    assert benchmark_payload["benchmark"]["comparison_metric"]
    assert benchmark_payload["bundle"]["benchmark_parity_report"]["parity_status"] == benchmark_payload["benchmark"]["parity_status"]

    assert main(["evals", "run", "--run-dir", str(run_dir), "--overwrite", "--format", "json"]) == 0
    eval_payload = json.loads(capsys.readouterr().out)
    assert eval_payload["status"] == "ok"
    assert eval_payload["evals"]["protocol_status"] == "ok"
    assert eval_payload["evals"]["security_status"] == "ok"
