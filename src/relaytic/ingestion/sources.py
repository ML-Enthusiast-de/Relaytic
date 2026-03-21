"""Local source inspection and materialization for snapshot, stream, and lakehouse inputs."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from pathlib import Path
from typing import Any

import pandas as pd

from relaytic.core.json_utils import write_json

from .csv_loader import SUPPORTED_TABULAR_EXTENSIONS, load_tabular_data
from .staging import DATA_COPY_MANIFEST_FILENAME, DataCopyRecord, stage_dataset_copy, stage_materialized_frame


SUPPORTED_SOURCE_TYPES = {"auto", "snapshot", "stream", "lakehouse"}
SUPPORTED_STREAM_FORMATS = {"auto", "csv", "tsv", "jsonl"}
SUPPORTED_MATERIALIZED_FORMATS = {"auto", "parquet", "csv"}
DUCKDB_EXTENSIONS = {".duckdb", ".db"}
STREAM_FILE_EXTENSIONS = {".csv", ".tsv", ".jsonl", ".ndjson"}
LAKEHOUSE_FILE_EXTENSIONS = {".parquet", ".pq", ".csv", ".tsv", ".jsonl", ".ndjson"}


class SourceMaterializationError(RuntimeError):
    """Raised when Relaytic cannot safely materialize a structured source."""


@dataclass(frozen=True)
class SourceSpec:
    """How Relaytic should interpret a structured data source."""

    source_path: Path
    source_type: str = "auto"
    source_table: str | None = None
    sql_query: str | None = None
    stream_window_rows: int = 5000
    stream_format: str = "auto"
    materialized_format: str = "auto"
    delimiter: str | None = None

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["source_path"] = str(self.source_path)
        return payload


@dataclass(frozen=True)
class SourceInspection:
    """Inspectable metadata for a structured source before materialization."""

    source_path: str
    source_name: str
    source_type: str
    path_kind: str
    detected_format: str
    supports_direct_copy: bool
    recommended_materialization: str
    table_names: list[str]
    file_count: int
    notes: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class MaterializedSource:
    """Materialized source snapshot staged inside a Relaytic run directory."""

    source_path: str
    source_name: str
    source_type: str
    detected_format: str
    staged_path: str
    record: DataCopyRecord
    row_count: int | None = None
    column_count: int | None = None
    materialized_format: str | None = None
    notes: list[str] | None = None

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["record"] = self.record.to_dict()
        return payload


def build_source_spec(
    *,
    source_path: str | Path,
    source_type: str = "auto",
    source_table: str | None = None,
    sql_query: str | None = None,
    stream_window_rows: int = 5000,
    stream_format: str = "auto",
    materialized_format: str = "auto",
    delimiter: str | None = None,
) -> SourceSpec:
    normalized_type = str(source_type or "auto").strip().lower()
    if normalized_type not in SUPPORTED_SOURCE_TYPES:
        raise ValueError(f"Unsupported --source-type '{source_type}'.")
    normalized_stream_format = str(stream_format or "auto").strip().lower()
    if normalized_stream_format not in SUPPORTED_STREAM_FORMATS:
        raise ValueError(f"Unsupported --stream-format '{stream_format}'.")
    normalized_materialized_format = str(materialized_format or "auto").strip().lower()
    if normalized_materialized_format not in SUPPORTED_MATERIALIZED_FORMATS:
        raise ValueError(f"Unsupported --materialized-format '{materialized_format}'.")
    resolved_path = Path(source_path).expanduser().resolve()
    if not resolved_path.exists():
        raise FileNotFoundError(f"Structured source does not exist: {source_path}")
    if stream_window_rows <= 0:
        raise ValueError("--stream-window-rows must be positive.")
    spec = SourceSpec(
        source_path=resolved_path,
        source_type=normalized_type,
        source_table=str(source_table).strip() or None if source_table is not None else None,
        sql_query=str(sql_query).strip() or None if sql_query is not None else None,
        stream_window_rows=int(stream_window_rows),
        stream_format=normalized_stream_format,
        materialized_format=normalized_materialized_format,
        delimiter=str(delimiter).strip() or None if delimiter is not None else None,
    )
    _validate_source_spec(spec)
    return spec


def inspect_structured_source(spec: SourceSpec) -> SourceInspection:
    source_type = _resolve_source_type(spec)
    path = spec.source_path
    if path.is_dir():
        files = [item for item in path.rglob("*") if item.is_file()]
        detected_format = _infer_directory_dataset_format(files)
        return SourceInspection(
            source_path=str(path),
            source_name=path.name or "dataset_directory",
            source_type=source_type,
            path_kind="directory",
            detected_format=detected_format,
            supports_direct_copy=False,
            recommended_materialization=_resolve_materialized_format(spec, prefer_parquet=True),
            table_names=[],
            file_count=len(files),
            notes=["Local dataset directories are materialized into immutable run-local snapshots."],
        )
    if path.suffix.lower() in DUCKDB_EXTENSIONS:
        table_names = _list_duckdb_tables(path)
        return SourceInspection(
            source_path=str(path),
            source_name=path.name,
            source_type=source_type,
            path_kind="file",
            detected_format="duckdb",
            supports_direct_copy=False,
            recommended_materialization=_resolve_materialized_format(spec, prefer_parquet=True),
            table_names=table_names,
            file_count=1,
            notes=["DuckDB sources are queried read-only and materialized into immutable run-local snapshots."],
        )
    detected_format = _infer_file_format(path)
    return SourceInspection(
        source_path=str(path),
        source_name=path.name,
        source_type=source_type,
        path_kind="file",
        detected_format=detected_format,
        supports_direct_copy=(source_type == "snapshot"),
        recommended_materialization=_resolve_materialized_format(spec, prefer_parquet=(source_type != "snapshot")),
        table_names=[],
        file_count=1,
        notes=["Snapshot files can be copied directly; stream and lakehouse sources are materialized into immutable run-local snapshots."],
    )


def materialize_structured_source(
    *,
    spec: SourceSpec,
    run_dir: str | Path,
    purpose: str = "primary",
    alias: str | None = None,
) -> MaterializedSource:
    source_type = _resolve_source_type(spec)
    source_name = spec.source_path.name or "source"
    if source_type == "snapshot" and spec.source_path.is_file():
        record = stage_dataset_copy(
            source_path=spec.source_path,
            run_dir=run_dir,
            purpose=purpose,
            alias=alias or spec.source_path.stem,
        )
        return MaterializedSource(
            source_path=str(spec.source_path),
            source_name=source_name,
            source_type=source_type,
            detected_format=_infer_file_format(spec.source_path),
            staged_path=str(Path(run_dir, record.staged_path).resolve()),
            record=record,
            materialized_format=None,
            notes=["Direct immutable file copy staged under the run directory."],
        )

    frame, detected_format, details = _load_materializable_frame(spec=spec, resolved_source_type=source_type)
    selected_format = _resolve_materialized_format(spec, prefer_parquet=True)
    record = stage_materialized_frame(
        frame=frame,
        run_dir=run_dir,
        purpose=purpose,
        alias=alias or _materialized_alias(spec.source_path, source_type=source_type),
        source_name=source_name,
        source_kind=source_type,
        materialized_format=selected_format,
        source_details={
            "detected_format": detected_format,
            **details,
        },
    )
    return MaterializedSource(
        source_path=str(spec.source_path),
        source_name=source_name,
        source_type=source_type,
        detected_format=detected_format,
        staged_path=str(Path(run_dir, record.staged_path).resolve()),
        record=record,
        row_count=int(frame.shape[0]),
        column_count=int(frame.shape[1]),
        materialized_format=selected_format,
        notes=["Materialized into an immutable run-local snapshot before Relaytic touched the data."],
    )


def write_source_inspection(path: str | Path, inspection: SourceInspection) -> Path:
    return write_json(path, inspection.to_dict(), indent=2, ensure_ascii=False, sort_keys=True)


def write_materialized_source_report(path: str | Path, materialized: MaterializedSource) -> Path:
    return write_json(path, materialized.to_dict(), indent=2, ensure_ascii=False, sort_keys=True)


def _resolve_source_type(spec: SourceSpec) -> str:
    if spec.source_type != "auto":
        return spec.source_type
    if spec.source_path.is_dir():
        return "lakehouse"
    suffix = spec.source_path.suffix.lower()
    if suffix in DUCKDB_EXTENSIONS:
        return "lakehouse"
    return "snapshot"


def _validate_source_spec(spec: SourceSpec) -> None:
    path = spec.source_path
    resolved_type = _resolve_source_type(spec)
    suffix = path.suffix.lower()
    if path.is_dir():
        if resolved_type != "lakehouse":
            raise ValueError("Directories are only supported as lakehouse-style sources.")
        return
    if resolved_type == "snapshot":
        if suffix not in SUPPORTED_TABULAR_EXTENSIONS:
            raise ValueError(
                f"Unsupported snapshot format '{suffix or 'unknown'}'. Supported snapshot formats: {sorted(SUPPORTED_TABULAR_EXTENSIONS)}"
            )
        return
    if resolved_type == "stream":
        if suffix not in STREAM_FILE_EXTENSIONS:
            raise ValueError(
                f"Unsupported stream source '{suffix or 'unknown'}'. Supported stream file formats: {sorted(STREAM_FILE_EXTENSIONS)}"
            )
        return
    if resolved_type == "lakehouse":
        if suffix not in DUCKDB_EXTENSIONS and suffix not in {".parquet", ".pq"}:
            raise ValueError(
                "Lakehouse sources must be a local dataset directory, a DuckDB file, or a parquet file."
            )


def _infer_file_format(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix in {".jsonl", ".ndjson"}:
        return "jsonl"
    if suffix == ".tsv":
        return "tsv"
    if suffix in {".parquet", ".pq"}:
        return "parquet"
    if suffix == ".duckdb":
        return "duckdb"
    if suffix == ".db":
        return "sqlite_or_duckdb"
    return suffix.lstrip(".") or "unknown"


def _infer_directory_dataset_format(files: list[Path]) -> str:
    suffixes = {item.suffix.lower() for item in files}
    if {".parquet", ".pq"} & suffixes:
        return "partitioned_parquet"
    if {".csv", ".tsv"} & suffixes:
        return "tabular_directory"
    if {".jsonl", ".ndjson"} & suffixes:
        return "jsonl_directory"
    return "directory_dataset"


def _resolve_materialized_format(spec: SourceSpec, *, prefer_parquet: bool) -> str:
    if spec.materialized_format != "auto":
        return spec.materialized_format
    if prefer_parquet:
        return "parquet"
    return "csv"


def _load_materializable_frame(*, spec: SourceSpec, resolved_source_type: str) -> tuple[pd.DataFrame, str, dict[str, Any]]:
    if resolved_source_type == "stream":
        return _load_stream_window(spec)
    if resolved_source_type == "lakehouse":
        return _load_lakehouse_source(spec)
    loaded = load_tabular_data(
        spec.source_path,
        delimiter=spec.delimiter,
    )
    return loaded.frame, loaded.file_type, {}


def _load_stream_window(spec: SourceSpec) -> tuple[pd.DataFrame, str, dict[str, Any]]:
    path = spec.source_path
    detected_format = spec.stream_format if spec.stream_format != "auto" else _infer_stream_format(path)
    if detected_format == "jsonl":
        frame = pd.read_json(path, lines=True)
    elif detected_format == "tsv":
        frame = pd.read_csv(path, sep="\t")
    else:
        delimiter = spec.delimiter or ("," if detected_format == "csv" else detected_format)
        frame = pd.read_csv(path, sep=delimiter)
    bounded = frame.tail(spec.stream_window_rows).reset_index(drop=True)
    return bounded, detected_format, {"window_rows": int(spec.stream_window_rows)}


def _infer_stream_format(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix in {".jsonl", ".ndjson"}:
        return "jsonl"
    if suffix == ".tsv":
        return "tsv"
    return "csv"


def _load_lakehouse_source(spec: SourceSpec) -> tuple[pd.DataFrame, str, dict[str, Any]]:
    path = spec.source_path
    if path.is_dir():
        files = [item for item in path.rglob("*") if item.is_file() and item.suffix.lower() in LAKEHOUSE_FILE_EXTENSIONS]
        if not files:
            raise SourceMaterializationError(f"No supported structured files found under lakehouse directory: {path}")
        parquet_files = [item for item in files if item.suffix.lower() in {".parquet", ".pq"}]
        if parquet_files:
            try:
                import pyarrow.dataset as ds
            except Exception as exc:  # pragma: no cover - pyarrow is a runtime dependency in full installs
                raise SourceMaterializationError("PyArrow dataset support is required for partitioned parquet directories.") from exc
            dataset = ds.dataset(path, format="parquet", partitioning="hive")
            table = dataset.to_table()
            frame = table.to_pandas()
            return frame.reset_index(drop=True), "partitioned_parquet", {"file_count": len(parquet_files)}
        frames = [
            load_tabular_data(item).frame
            for item in sorted(files)
        ]
        frame = pd.concat(frames, ignore_index=True)
        return frame.reset_index(drop=True), _infer_directory_dataset_format(files), {"file_count": len(files)}

    if path.suffix.lower() in DUCKDB_EXTENSIONS:
        try:
            import duckdb
        except Exception as exc:  # pragma: no cover - duckdb is installed in full/dev profiles
            raise SourceMaterializationError("DuckDB support is required to materialize .duckdb or .db sources.") from exc
        with duckdb.connect(str(path), read_only=True) as connection:
            query = spec.sql_query
            selected_table = spec.source_table
            if not query:
                if not selected_table:
                    tables = _list_duckdb_tables(path)
                    if len(tables) != 1:
                        raise SourceMaterializationError(
                            "DuckDB source requires --source-table or --sql-query when the database contains multiple tables."
                        )
                    selected_table = tables[0]
                query = f'SELECT * FROM "{selected_table}"'
            frame = connection.execute(query).fetchdf()
            return frame.reset_index(drop=True), "duckdb", {"table": selected_table, "query_used": spec.sql_query is not None}

    loaded = load_tabular_data(path)
    return loaded.frame, loaded.file_type, {}


def _list_duckdb_tables(path: Path) -> list[str]:
    try:
        import duckdb
    except Exception:
        return []
    with duckdb.connect(str(path), read_only=True) as connection:
        rows = connection.execute("SHOW TABLES").fetchall()
    return [str(item[0]) for item in rows if item]


def _materialized_alias(path: Path, *, source_type: str) -> str:
    base = path.stem if path.is_file() else path.name
    normalized = "".join(ch if ch.isalnum() else "_" for ch in (base or "source")).strip("_").lower() or "source"
    return f"{normalized}_{source_type}_snapshot"
