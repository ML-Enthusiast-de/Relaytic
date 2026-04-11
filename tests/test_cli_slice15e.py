from __future__ import annotations

import json
import os
import time
from pathlib import Path

import pandas as pd

from relaytic.completion.storage import COMPLETION_FILENAMES
from relaytic.ui.cli import main


def _write_binary_dataset(path: Path) -> Path:
    rows: list[dict[str, float | int]] = []
    for idx in range(240):
        feature_a = idx / 239.0
        feature_b = 1 if idx % 5 in {0, 1} else 0
        feature_c = round((idx % 13) / 12.0, 5)
        feature_d = round(((idx * 7) % 17) / 16.0, 5)
        target = 1 if (feature_a > 0.62 or feature_b == 1 or (feature_c + feature_d) > 1.45) else 0
        rows.append(
            {
                "feature_a": round(feature_a, 5),
                "feature_b": feature_b,
                "feature_c": feature_c,
                "feature_d": feature_d,
                "target_flag": target,
            }
        )
    pd.DataFrame(rows).to_csv(path, index=False)
    return path


def _create_base_run(tmp_path: Path, capsys) -> tuple[Path, Path]:
    run_dir = tmp_path / "slice15e_binary"
    data_path = _write_binary_dataset(tmp_path / "slice15e_binary.csv")
    assert main(
        [
            "run",
            "--run-dir",
            str(run_dir),
            "--data-path",
            str(data_path),
            "--text",
            "Classify target_flag from the feature columns. Do everything on your own.",
            "--format",
            "json",
        ]
    ) == 0
    capsys.readouterr()
    return run_dir, data_path


def test_cli_slice15e_runtime_reuse_surface_materializes_dependency_artifacts(tmp_path: Path, capsys) -> None:
    run_dir, data_path = _create_base_run(tmp_path, capsys)

    assert main(["benchmark", "run", "--run-dir", str(run_dir), "--data-path", str(data_path), "--format", "json"]) == 0
    capsys.readouterr()

    assert main(["runtime", "reuse", "--run-dir", str(run_dir), "--format", "json"]) == 0
    payload = json.loads(capsys.readouterr().out)

    assert payload["status"] == "ok"
    assert payload["recompute"]["fresh_stage_count"] >= 1
    assert payload["bundle"]["artifact_dependency_graph"]["node_count"] >= 6
    stages = {item["stage"]: item for item in payload["bundle"]["artifact_dependency_graph"]["nodes"]}
    assert "benchmark" in stages
    assert "completion" in stages
    assert "workspace" in stages
    assert "search" in stages["benchmark"]["depends_on"]
    for filename in (
        "artifact_dependency_graph.json",
        "freshness_contract.json",
        "recompute_plan.json",
        "materialization_cache_index.json",
        "invalidation_report.json",
    ):
        assert (run_dir / filename).exists(), filename


def test_cli_slice15e_invalidation_marks_only_downstream_after_benchmark_change(tmp_path: Path, capsys) -> None:
    run_dir, data_path = _create_base_run(tmp_path, capsys)

    assert main(["benchmark", "run", "--run-dir", str(run_dir), "--data-path", str(data_path), "--format", "json"]) == 0
    capsys.readouterr()
    assert main(["completion", "review", "--run-dir", str(run_dir), "--format", "json"]) == 0
    capsys.readouterr()

    benchmark_path = run_dir / "benchmark_parity_report.json"
    future = time.time() + 5.0
    os.utime(benchmark_path, (future, future))

    assert main(["runtime", "reuse", "--run-dir", str(run_dir), "--format", "json"]) == 0
    payload = json.loads(capsys.readouterr().out)

    stages = {item["stage"]: item for item in payload["bundle"]["freshness_contract"]["stages"]}
    assert stages["search"]["status"] == "fresh"
    assert stages["benchmark"]["status"] == "fresh"
    assert stages["decision"]["status"] == "stale"
    assert stages["completion"]["status"] in {"stale", "upstream_invalidated"}
    assert stages["workspace"]["status"] in {"stale", "upstream_invalidated"}


def test_cli_slice15e_benchmark_run_reuses_existing_fresh_bundle(tmp_path: Path, capsys) -> None:
    run_dir, data_path = _create_base_run(tmp_path, capsys)

    assert main(["benchmark", "run", "--run-dir", str(run_dir), "--data-path", str(data_path), "--format", "json"]) == 0
    capsys.readouterr()
    benchmark_path = run_dir / "benchmark_parity_report.json"
    first_mtime = benchmark_path.stat().st_mtime

    assert main(["benchmark", "run", "--run-dir", str(run_dir), "--data-path", str(data_path), "--format", "json"]) == 0
    payload = json.loads(capsys.readouterr().out)

    assert payload["status"] == "ok"
    assert benchmark_path.stat().st_mtime == first_mtime


def test_cli_slice15e_completion_review_reuses_existing_benchmark_artifacts(tmp_path: Path, capsys) -> None:
    run_dir, data_path = _create_base_run(tmp_path, capsys)

    assert main(["benchmark", "run", "--run-dir", str(run_dir), "--data-path", str(data_path), "--format", "json"]) == 0
    capsys.readouterr()
    benchmark_path = run_dir / "benchmark_parity_report.json"
    benchmark_mtime = benchmark_path.stat().st_mtime

    for filename in COMPLETION_FILENAMES.values():
        path = run_dir / filename
        if path.exists():
            path.unlink()

    assert main(["completion", "review", "--run-dir", str(run_dir), "--format", "json"]) == 0
    payload = json.loads(capsys.readouterr().out)

    assert payload["status"] == "ok"
    assert benchmark_path.stat().st_mtime == benchmark_mtime
    assert payload["completion"]["action"]
    for filename in COMPLETION_FILENAMES.values():
        assert (run_dir / filename).exists(), filename
