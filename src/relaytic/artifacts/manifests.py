"""Manifest helpers for early Relaytic artifact scaffolding."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from relaytic.core.json_utils import write_json


MANIFEST_SCHEMA_VERSION = "relaytic.manifest.v1"


@dataclass(frozen=True)
class ManifestEntry:
    """One declared artifact in a run scaffold."""

    path: str
    kind: str = "artifact"
    required: bool = False
    exists: bool = False
    size_bytes: int | None = None


@dataclass(frozen=True)
class ArtifactManifest:
    """Structured manifest for a Relaytic run directory."""

    schema_version: str
    product: str
    descriptor: str
    run_id: str
    created_at: str
    artifact_root: str
    policy_source: str | None
    labels: dict[str, str] = field(default_factory=dict)
    entries: list[ManifestEntry] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["entry_count"] = len(self.entries)
        return payload


def artifact_entry(
    path: str | Path,
    *,
    run_dir: str | Path | None = None,
    kind: str = "artifact",
    required: bool = False,
) -> ManifestEntry:
    """Create one manifest entry, resolving existence and size on disk."""
    raw_path = Path(path)
    display_path = _relative_path(raw_path, run_dir=run_dir)
    resolved = raw_path if raw_path.is_absolute() else _resolve_entry_path(raw_path, run_dir=run_dir)
    exists = resolved.exists()
    size_bytes = resolved.stat().st_size if exists and resolved.is_file() else None
    return ManifestEntry(
        path=display_path,
        kind=kind,
        required=required,
        exists=exists,
        size_bytes=size_bytes,
    )


def build_manifest(
    *,
    run_dir: str | Path,
    run_id: str | None = None,
    policy_source: str | Path | None = None,
    labels: dict[str, str] | None = None,
    entries: list[ManifestEntry] | None = None,
    created_at: datetime | None = None,
) -> ArtifactManifest:
    """Build an artifact manifest without writing it to disk."""
    root = Path(run_dir)
    stamp = (created_at or datetime.now(timezone.utc)).isoformat()
    resolved_run_id = run_id or root.name or "run"
    resolved_policy_source = str(Path(policy_source)) if policy_source is not None else None

    manifest_entries = list(entries or [])
    manifest_path = root / "manifest.json"
    manifest_entries = [
        item for item in manifest_entries if item.path != "manifest.json"
    ] + [
        artifact_entry(manifest_path, run_dir=root, kind="manifest", required=True)
    ]

    return ArtifactManifest(
        schema_version=MANIFEST_SCHEMA_VERSION,
        product="Relaytic",
        descriptor="The Relay Inference Lab",
        run_id=resolved_run_id,
        created_at=stamp,
        artifact_root=str(root),
        policy_source=resolved_policy_source,
        labels=dict(labels or {}),
        entries=manifest_entries,
    )


def write_manifest(
    *,
    run_dir: str | Path,
    run_id: str | None = None,
    policy_source: str | Path | None = None,
    labels: dict[str, str] | None = None,
    entries: list[ManifestEntry] | None = None,
    created_at: datetime | None = None,
) -> Path:
    """Write `manifest.json` into a run directory and return the path."""
    root = Path(run_dir)
    root.mkdir(parents=True, exist_ok=True)
    manifest = build_manifest(
        run_dir=root,
        run_id=run_id,
        policy_source=policy_source,
        labels=labels,
        entries=entries,
        created_at=created_at,
    )
    path = root / "manifest.json"
    write_json(path, manifest.to_dict(), indent=2, ensure_ascii=False, sort_keys=True)
    manifest = build_manifest(
        run_dir=root,
        run_id=run_id,
        policy_source=policy_source,
        labels=labels,
        entries=entries,
        created_at=created_at,
    )
    write_json(path, manifest.to_dict(), indent=2, ensure_ascii=False, sort_keys=True)
    return path


def _relative_path(path: Path, *, run_dir: str | Path | None) -> str:
    if run_dir is None:
        return str(path)
    root = Path(run_dir)
    if path.is_absolute():
        try:
            return str(path.relative_to(root))
        except ValueError:
            return str(path)
    return str(path)


def _resolve_entry_path(path: Path, *, run_dir: str | Path | None) -> Path:
    if path.is_absolute() or run_dir is None:
        return path
    return Path(run_dir) / path
