import json
from pathlib import Path

import pandas as pd

from relaytic.ui.cli import main

from tests.public_datasets import (
    write_public_breast_cancer_dataset,
    write_public_diabetes_dataset,
)


def test_cli_source_materialize_reports_local_snapshot(tmp_path: Path, capsys) -> None:
    source_path = write_public_breast_cancer_dataset(tmp_path / "breast_cancer.csv")
    run_dir = tmp_path / "materialize_report"

    assert main(
        [
            "source",
            "materialize",
            "--source-path",
            str(source_path),
            "--run-dir",
            str(run_dir),
            "--format",
            "json",
        ]
    ) == 0

    payload = json.loads(capsys.readouterr().out)
    assert payload["source_type"] == "snapshot"
    assert payload["staged_path"]
    assert Path(payload["staged_path"]).exists()


def test_cli_run_supports_public_breast_cancer_parquet_snapshot(tmp_path: Path, capsys) -> None:
    run_dir = tmp_path / "run_public_breast_cancer_parquet"
    csv_path = write_public_breast_cancer_dataset(tmp_path / "public_breast_cancer.csv")
    parquet_path = tmp_path / "public_breast_cancer.parquet"
    pd.read_csv(csv_path).to_parquet(parquet_path, index=False)

    assert main(
        [
            "run",
            "--run-dir",
            str(run_dir),
            "--data-path",
            str(parquet_path),
            "--text",
            "Classify diagnosis_flag from the measurement columns. Do everything on your own.",
            "--format",
            "json",
        ]
    ) == 0

    payload = json.loads(capsys.readouterr().out)
    assert payload["status"] == "ok"
    assert payload["run_summary"]["decision"]["task_type"] == "binary_classification"
    assert payload["run_summary"]["data"]["source_format"] == "parquet"
    assert payload["run_summary"]["data"]["source_type"] == "snapshot"


def test_cli_run_supports_public_diabetes_jsonl_stream_snapshot(tmp_path: Path, capsys) -> None:
    run_dir = tmp_path / "run_public_diabetes_stream"
    csv_path = write_public_diabetes_dataset(tmp_path / "public_diabetes.csv")
    jsonl_path = tmp_path / "public_diabetes_stream.jsonl"
    pd.read_csv(csv_path).to_json(jsonl_path, orient="records", lines=True)

    assert main(
        [
            "run",
            "--run-dir",
            str(run_dir),
            "--data-path",
            str(jsonl_path),
            "--source-type",
            "stream",
            "--stream-format",
            "jsonl",
            "--stream-window-rows",
            "442",
            "--text",
            "Estimate disease_progression from the patient measurements. Do everything on your own.",
            "--format",
            "json",
        ]
    ) == 0

    payload = json.loads(capsys.readouterr().out)
    assert payload["status"] == "ok"
    assert payload["run_summary"]["decision"]["task_type"] == "regression"
    assert payload["run_summary"]["data"]["source_type"] == "stream"
    assert payload["run_summary"]["data"]["row_count"] == 442


def test_cli_run_supports_local_partitioned_parquet_lakehouse(tmp_path: Path, capsys) -> None:
    run_dir = tmp_path / "run_lakehouse"
    csv_path = write_public_breast_cancer_dataset(tmp_path / "public_breast_cancer.csv")
    frame = pd.read_csv(csv_path)
    lake_root = tmp_path / "breast_cancer_lake"
    first_half = lake_root / "split=first"
    second_half = lake_root / "split=second"
    first_half.mkdir(parents=True)
    second_half.mkdir(parents=True)
    frame.iloc[:300].to_parquet(first_half / "part_a.parquet", index=False)
    frame.iloc[300:].to_parquet(second_half / "part_b.parquet", index=False)

    assert main(
        [
            "run",
            "--run-dir",
            str(run_dir),
            "--data-path",
            str(lake_root),
            "--source-type",
            "lakehouse",
            "--text",
            "Classify diagnosis_flag from the measurement columns. Do everything on your own.",
            "--format",
            "json",
        ]
    ) == 0

    payload = json.loads(capsys.readouterr().out)
    assert payload["status"] == "ok"
    assert payload["run_summary"]["decision"]["task_type"] == "binary_classification"
    assert payload["run_summary"]["data"]["source_type"] == "lakehouse"
    assert payload["run_summary"]["data"]["row_count"] == 569
