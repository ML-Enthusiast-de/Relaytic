import json
from pathlib import Path

import pandas as pd

from relaytic.ingestion import (
    build_source_spec,
    inspect_structured_source,
    materialize_structured_source,
)


def test_materialize_stream_jsonl_stages_bounded_window(tmp_path: Path) -> None:
    stream_path = tmp_path / "events.jsonl"
    frame = pd.DataFrame(
        {
            "sensor_a": list(range(12)),
            "sensor_b": [value * 10 for value in range(12)],
            "failure_flag": [value % 2 for value in range(12)],
        }
    )
    frame.to_json(stream_path, orient="records", lines=True)

    run_dir = tmp_path / "run_stream"
    spec = build_source_spec(
        source_path=stream_path,
        source_type="stream",
        stream_window_rows=5,
        stream_format="jsonl",
    )
    materialized = materialize_structured_source(spec=spec, run_dir=run_dir, purpose="primary")

    manifest = json.loads((run_dir / "data_copy_manifest.json").read_text(encoding="utf-8"))
    staged = Path(materialized.staged_path)
    loaded = pd.read_parquet(staged)

    assert materialized.source_type == "stream"
    assert materialized.detected_format == "jsonl"
    assert materialized.row_count == 5
    assert staged.exists()
    assert loaded.shape == (5, 3)
    assert loaded["sensor_a"].tolist() == [7, 8, 9, 10, 11]
    assert manifest["latest_by_purpose"]["primary"] == materialized.record.staged_path


def test_inspect_lakehouse_directory_reports_directory_dataset(tmp_path: Path) -> None:
    lake_root = tmp_path / "lakehouse"
    part_a = lake_root / "day=2025-01-01"
    part_b = lake_root / "day=2025-01-02"
    part_a.mkdir(parents=True)
    part_b.mkdir(parents=True)
    pd.DataFrame({"sensor_a": [1.0, 2.0], "target": [0, 1]}).to_parquet(part_a / "part_a.parquet", index=False)
    pd.DataFrame({"sensor_a": [3.0, 4.0], "target": [1, 0]}).to_parquet(part_b / "part_b.parquet", index=False)

    spec = build_source_spec(source_path=lake_root, source_type="lakehouse")
    inspection = inspect_structured_source(spec)

    assert inspection.source_type == "lakehouse"
    assert inspection.path_kind == "directory"
    assert inspection.detected_format == "partitioned_parquet"
    assert inspection.supports_direct_copy is False
    assert inspection.file_count == 2


def test_materialize_duckdb_source_reads_single_table_read_only(tmp_path: Path) -> None:
    duckdb = __import__("duckdb")

    db_path = tmp_path / "quality.duckdb"
    with duckdb.connect(str(db_path)) as connection:
        connection.execute("CREATE TABLE quality_signals AS SELECT 1 AS sensor_a, 0 AS failure_flag UNION ALL SELECT 2, 1")

    run_dir = tmp_path / "run_duckdb"
    spec = build_source_spec(source_path=db_path, source_type="lakehouse", source_table="quality_signals")
    materialized = materialize_structured_source(spec=spec, run_dir=run_dir, purpose="primary")

    staged = Path(materialized.staged_path)
    loaded = pd.read_parquet(staged)

    assert materialized.source_type == "lakehouse"
    assert materialized.detected_format == "duckdb"
    assert materialized.row_count == 2
    assert loaded["sensor_a"].tolist() == [1, 2]
