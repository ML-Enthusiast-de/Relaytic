"""Runtime helpers for optional third-party integrations."""

from __future__ import annotations

from importlib import import_module, metadata
from types import ModuleType
from typing import Any


def integration_version(package_name: str) -> str | None:
    """Return the installed version for an optional package if available."""
    try:
        return metadata.version(package_name)
    except metadata.PackageNotFoundError:
        return None


def import_optional_module(module_name: str) -> ModuleType | None:
    """Import an optional module without raising on absence."""
    try:
        return import_module(module_name)
    except Exception:
        return None


def base_integration_result(
    *,
    integration: str,
    package_name: str,
    surface: str,
    status: str,
    compatible: bool,
    notes: list[str] | None = None,
    details: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Return a stable machine-readable integration result payload."""
    return {
        "integration": integration,
        "package_name": package_name,
        "version": integration_version(package_name),
        "surface": surface,
        "status": status,
        "compatible": bool(compatible),
        "notes": list(notes or []),
        "details": dict(details or {}),
    }
