"""Immutable local data-copy staging for Relaytic run execution."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
import hashlib
from pathlib import Path
import shutil
import stat
from typing import Any

import pandas as pd

from relaytic.core.json_utils import write_json


DATA_COPY_MANIFEST_FILENAME = "data_copy_manifest.json"
DATA_COPY_MANIFEST_SCHEMA_VERSION = "relaytic.data_copy_manifest.v1"


@dataclass(frozen=True)
class DataCopyRecord:
    """One staged immutable dataset copy inside a Relaytic run."""

    copy_id: str
    purpose: str
    source_basename: str
    source_extension: str
    source_size_bytes: int
    source_sha256: str
    staged_path: str
    staged_size_bytes: int
    immutable: bool
    original_path_persisted: bool
    copied_at: str
    source_kind: str = "snapshot"
    materialized_format: str | None = None
    row_count: int | None = None
    column_count: int | None = None
    source_details: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class DataCopyManifest:
    """Persisted copy-only boundary for run data."""

    schema_version: str
    generated_at: str
    copy_only: bool
    immutable_working_copies: bool
    original_paths_persisted: bool
    latest_by_purpose: dict[str, str] = field(default_factory=dict)
    copies: list[DataCopyRecord] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "generated_at": self.generated_at,
            "copy_only": self.copy_only,
            "immutable_working_copies": self.immutable_working_copies,
            "original_paths_persisted": self.original_paths_persisted,
            "latest_by_purpose": dict(self.latest_by_purpose),
            "copies": [item.to_dict() for item in self.copies],
        }


def stage_dataset_copy(
    *,
    source_path: str | Path,
    run_dir: str | Path,
    purpose: str = "primary",
    alias: str | None = None,
) -> DataCopyRecord:
    """Stage a local immutable copy of a dataset into a Relaytic run directory."""
    root = Path(run_dir)
    root.mkdir(parents=True, exist_ok=True)
    source = Path(source_path).expanduser().resolve()
    if not source.is_file():
        raise FileNotFoundError(f"Dataset path does not exist: {source_path}")

    manifest_payload = read_data_copy_manifest(root)
    existing_records = [
        _record_from_dict(item)
        for item in manifest_payload.get("copies", [])
        if isinstance(item, dict)
    ]

    direct_match = _find_existing_by_staged_path(
        root=root,
        source=source,
        records=existing_records,
    )
    if direct_match is not None:
        _mark_read_only(root / direct_match.staged_path)
        return direct_match

    source_sha256 = _sha256_file(source)
    purpose_key = _normalize_purpose(purpose)
    reusable = _find_existing_copy(
        root=root,
        purpose=purpose_key,
        source=source,
        source_sha256=source_sha256,
        records=existing_records,
    )
    if reusable is not None:
        _mark_read_only(root / reusable.staged_path)
        _write_manifest(
            root=root,
            records=existing_records,
            latest_by_purpose=_latest_map(existing_records, previous=dict(manifest_payload.get("latest_by_purpose", {}))),
        )
        return reusable

    target_dir = root / "data_copies" / purpose_key
    target_dir.mkdir(parents=True, exist_ok=True)
    safe_name = _slugify(alias or source.stem or source.name)
    target_path = target_dir / f"{safe_name}_{source_sha256[:12]}{source.suffix.lower()}"
    shutil.copy2(source, target_path)
    _mark_read_only(target_path)

    record = DataCopyRecord(
        copy_id=f"copy_{source_sha256[:12]}",
        purpose=purpose_key,
        source_basename=source.name,
        source_extension=source.suffix.lower(),
        source_size_bytes=int(source.stat().st_size),
        source_sha256=source_sha256,
        staged_path=str(target_path.relative_to(root).as_posix()),
        staged_size_bytes=int(target_path.stat().st_size),
        immutable=True,
        original_path_persisted=False,
        copied_at=_utc_now(),
    )
    updated_records = [*existing_records, record]
    _write_manifest(
        root=root,
        records=updated_records,
        latest_by_purpose=_latest_map(updated_records, previous=dict(manifest_payload.get("latest_by_purpose", {}))),
    )
    return record


def stage_materialized_frame(
    *,
    frame: pd.DataFrame,
    run_dir: str | Path,
    purpose: str = "primary",
    alias: str | None = None,
    source_name: str = "materialized_source",
    source_kind: str = "materialized",
    materialized_format: str = "parquet",
    source_details: dict[str, Any] | None = None,
) -> DataCopyRecord:
    """Persist a materialized dataframe as an immutable run-local snapshot."""
    root = Path(run_dir)
    root.mkdir(parents=True, exist_ok=True)
    purpose_key = _normalize_purpose(purpose)
    manifest_payload = read_data_copy_manifest(root)
    existing_records = [
        _record_from_dict(item)
        for item in manifest_payload.get("copies", [])
        if isinstance(item, dict)
    ]
    target_dir = root / "data_copies" / purpose_key
    target_dir.mkdir(parents=True, exist_ok=True)
    safe_name = _slugify(alias or Path(source_name).stem or source_name)
    selected_format = str(materialized_format or "parquet").strip().lower() or "parquet"
    if selected_format not in {"parquet", "csv"}:
        raise ValueError(f"Unsupported materialized snapshot format: {materialized_format}")
    token = hashlib.sha256(f"{_utc_now()}::{purpose_key}::{safe_name}".encode("utf-8")).hexdigest()[:12]
    suffix = ".parquet" if selected_format == "parquet" else ".csv"
    target_path = target_dir / f"{safe_name}_{token}{suffix}"
    normalized = frame.reset_index(drop=True).copy()
    if selected_format == "parquet":
        normalized.to_parquet(target_path, index=False)
    else:
        normalized.to_csv(target_path, index=False)
    _mark_read_only(target_path)
    record = DataCopyRecord(
        copy_id=f"copy_{token}",
        purpose=purpose_key,
        source_basename=str(source_name).strip() or "materialized_source",
        source_extension=suffix,
        source_size_bytes=int(target_path.stat().st_size),
        source_sha256=_sha256_file(target_path),
        staged_path=str(target_path.relative_to(root).as_posix()),
        staged_size_bytes=int(target_path.stat().st_size),
        source_kind=str(source_kind or "materialized").strip() or "materialized",
        materialized_format=selected_format,
        row_count=int(normalized.shape[0]),
        column_count=int(normalized.shape[1]),
        source_details=dict(source_details or {}),
        immutable=True,
        original_path_persisted=False,
        copied_at=_utc_now(),
    )
    updated_records = [*existing_records, record]
    _write_manifest(
        root=root,
        records=updated_records,
        latest_by_purpose=_latest_map(updated_records, previous=dict(manifest_payload.get("latest_by_purpose", {}))),
    )
    return record


def read_data_copy_manifest(run_dir: str | Path) -> dict[str, Any]:
    """Read the staged-data manifest if present."""
    path = Path(run_dir) / DATA_COPY_MANIFEST_FILENAME
    if not path.exists():
        return {}
    try:
        payload = path.read_text(encoding="utf-8")
    except OSError:
        return {}
    import json

    try:
        decoded = json.loads(payload)
    except json.JSONDecodeError:
        return {}
    return decoded if isinstance(decoded, dict) else {}


def resolve_staged_data_path(
    run_dir: str | Path,
    *,
    purpose: str = "primary",
) -> str | None:
    """Resolve the preferred staged copy for one purpose."""
    root = Path(run_dir)
    payload = read_data_copy_manifest(root)
    latest = str(dict(payload.get("latest_by_purpose", {})).get(_normalize_purpose(purpose), "")).strip()
    if not latest:
        return None
    candidate = root / latest
    if not candidate.exists():
        return None
    return str(candidate)


def _write_manifest(
    *,
    root: Path,
    records: list[DataCopyRecord],
    latest_by_purpose: dict[str, str],
) -> None:
    manifest = DataCopyManifest(
        schema_version=DATA_COPY_MANIFEST_SCHEMA_VERSION,
        generated_at=_utc_now(),
        copy_only=True,
        immutable_working_copies=True,
        original_paths_persisted=False,
        latest_by_purpose=latest_by_purpose,
        copies=records,
    )
    write_json(
        root / DATA_COPY_MANIFEST_FILENAME,
        manifest.to_dict(),
        indent=2,
        ensure_ascii=False,
        sort_keys=True,
    )


def _find_existing_by_staged_path(
    *,
    root: Path,
    source: Path,
    records: list[DataCopyRecord],
) -> DataCopyRecord | None:
    for record in records:
        candidate = (root / record.staged_path).resolve()
        if candidate == source and candidate.exists():
            return record
    return None


def _find_existing_copy(
    *,
    root: Path,
    purpose: str,
    source: Path,
    source_sha256: str,
    records: list[DataCopyRecord],
) -> DataCopyRecord | None:
    for record in records:
        if record.purpose != purpose:
            continue
        if record.source_sha256 != source_sha256:
            continue
        if record.source_basename != source.name:
            continue
        staged = root / record.staged_path
        if staged.exists():
            return record
    return None


def _latest_map(
    records: list[DataCopyRecord],
    *,
    previous: dict[str, str],
) -> dict[str, str]:
    latest = dict(previous)
    ordered = sorted(records, key=lambda item: item.copied_at)
    for record in ordered:
        latest[record.purpose] = record.staged_path
    return latest


def _record_from_dict(payload: dict[str, Any]) -> DataCopyRecord:
    return DataCopyRecord(
        copy_id=str(payload.get("copy_id", "")).strip(),
        purpose=_normalize_purpose(payload.get("purpose", "primary")),
        source_basename=str(payload.get("source_basename", "")).strip(),
        source_extension=str(payload.get("source_extension", "")).strip(),
        source_size_bytes=int(payload.get("source_size_bytes", 0) or 0),
        source_sha256=str(payload.get("source_sha256", "")).strip(),
        staged_path=str(payload.get("staged_path", "")).strip(),
        staged_size_bytes=int(payload.get("staged_size_bytes", 0) or 0),
        source_kind=str(payload.get("source_kind", "snapshot")).strip() or "snapshot",
        materialized_format=str(payload.get("materialized_format", "")).strip() or None,
        row_count=int(payload.get("row_count")) if payload.get("row_count") is not None else None,
        column_count=int(payload.get("column_count")) if payload.get("column_count") is not None else None,
        source_details=dict(payload.get("source_details", {})) if isinstance(payload.get("source_details"), dict) else {},
        immutable=bool(payload.get("immutable", True)),
        original_path_persisted=bool(payload.get("original_path_persisted", False)),
        copied_at=str(payload.get("copied_at", "")).strip() or _utc_now(),
    )


def _mark_read_only(path: Path) -> None:
    if not path.exists():
        return
    try:
        current = path.stat().st_mode
        path.chmod(current & ~stat.S_IWUSR & ~stat.S_IWGRP & ~stat.S_IWOTH)
    except OSError:
        return


def _normalize_purpose(value: str | None) -> str:
    text = str(value or "").strip().lower()
    return text or "primary"


def _slugify(value: str) -> str:
    text = "".join(ch if ch.isalnum() else "_" for ch in str(value).strip().lower())
    text = "_".join(part for part in text.split("_") if part)
    return text or "dataset"


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()
