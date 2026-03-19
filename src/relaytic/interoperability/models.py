"""Typed interoperability metadata for Relaytic host adapters."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable


InteropHandler = Callable[..., dict[str, Any]]


@dataclass(frozen=True)
class InteropToolSpec:
    """Host-neutral MCP/tool contract for one Relaytic operation."""

    name: str
    title: str
    description: str
    category: str
    annotations: dict[str, Any]
    handler: InteropHandler
    structured_output: bool = True


@dataclass(frozen=True)
class HostBundleFile:
    """One generated host-integration file."""

    relative_path: str
    content: str
    description: str


@dataclass(frozen=True)
class HostBundleSpec:
    """Host-specific integration bundle composed of one or more files."""

    host: str
    title: str
    install_mode: str
    description: str
    files: tuple[HostBundleFile, ...]
    notes: tuple[str, ...] = ()
    discovery_mode: str = "manual"
    discoverable_now: bool = False
    requires_activation: bool = True
    requires_public_https: bool = False
    requires_publication: bool = False
    next_step: str = ""
