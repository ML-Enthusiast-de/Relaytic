"""Relaytic-owned MCP server boundary."""

from __future__ import annotations

import functools
from importlib import metadata
import inspect
from typing import Any

from relaytic.core.json_utils import dumps_json
from relaytic.interoperability.service import build_interoperability_tool_specs


SUPPORTED_TRANSPORTS = ("stdio", "streamable-http")
DEFAULT_MCP_HOST = "127.0.0.1"
DEFAULT_MCP_PORT = 8000
DEFAULT_MOUNT_PATH = "/mcp"
MIN_RECOMMENDED_MCP_VERSION = (1, 26, 0)


def serve_relaytic_mcp(
    *,
    transport: str = "stdio",
    host: str = DEFAULT_MCP_HOST,
    port: int = DEFAULT_MCP_PORT,
    mount_path: str = DEFAULT_MOUNT_PATH,
) -> None:
    """Run the Relaytic MCP server over the requested transport."""
    normalized_transport = str(transport).strip().lower() or "stdio"
    if normalized_transport not in SUPPORTED_TRANSPORTS:
        raise ValueError(f"Unsupported Relaytic MCP transport: {transport}")
    server = create_relaytic_mcp_server(host=host, port=port, mount_path=mount_path)
    server.run("streamable-http" if normalized_transport == "streamable-http" else "stdio")


def create_relaytic_mcp_server(
    *,
    host: str = DEFAULT_MCP_HOST,
    port: int = DEFAULT_MCP_PORT,
    mount_path: str = DEFAULT_MOUNT_PATH,
) -> Any:
    """Build the current Relaytic MCP server with the canonical tool contract."""
    fastmcp_cls, tool_annotations, call_tool_result_cls, text_content_cls = _load_mcp_types()
    version = _safe_package_version("relaytic")
    instructions = (
        "Relaytic is a local-first inference-engineering system for structured data. "
        "Prefer deterministic evidence-backed runs, keep `/mcp` local by default, and "
        "use the stable tool surfaces rather than inventing ad hoc workflows."
    )
    server = fastmcp_cls(
        name="Relaytic",
        instructions=instructions,
        host=host,
        port=port,
        streamable_http_path=mount_path,
        dependencies=("relaytic",),
        website_url="https://github.com/gehra/Relaytic",
        log_level="ERROR",
    )
    for spec in build_interoperability_tool_specs():
        server.tool(
            name=spec.name,
            title=spec.title,
            description=spec.description,
            annotations=tool_annotations(**spec.annotations),
            structured_output=False,
            meta={
                "relaytic/category": spec.category,
                "relaytic/version": version,
            },
        )(_wrap_tool_handler(spec.handler, call_tool_result_cls=call_tool_result_cls, text_content_cls=text_content_cls))
    return server


def build_mcp_sdk_status() -> dict[str, Any]:
    """Return a machine-readable status block for the MCP SDK."""
    version = _safe_package_version("mcp")
    compatible = False
    if version:
        compatible = _version_at_least(version, MIN_RECOMMENDED_MCP_VERSION)
    return {
        "package_name": "mcp",
        "installed": version is not None,
        "version": version,
        "compatible": compatible if version is not None else False,
        "minimum_tested_version": ".".join(str(part) for part in MIN_RECOMMENDED_MCP_VERSION),
        "supported_transports": list(SUPPORTED_TRANSPORTS),
        "default_transport": "stdio",
        "remote_transport": "streamable-http",
        "mount_path": DEFAULT_MOUNT_PATH,
        "default_host": DEFAULT_MCP_HOST,
        "default_port": DEFAULT_MCP_PORT,
    }


def _load_mcp_types() -> tuple[Any, Any, Any, Any]:
    try:
        from mcp.server.fastmcp import FastMCP  # type: ignore
        from mcp.types import CallToolResult  # type: ignore
        from mcp.types import TextContent  # type: ignore
        from mcp.types import ToolAnnotations  # type: ignore
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError(
            "Relaytic MCP support requires the `mcp` package. Install `relaytic[interop]` or `relaytic[full]`."
        ) from exc
    return FastMCP, ToolAnnotations, CallToolResult, TextContent


def _wrap_tool_handler(handler: Any, *, call_tool_result_cls: Any, text_content_cls: Any) -> Any:
    @functools.wraps(handler)
    def _wrapped(*args: Any, **kwargs: Any) -> Any:
        payload = handler(*args, **kwargs)
        return call_tool_result_cls(
            content=[text_content_cls(type="text", text=dumps_json(payload, indent=2, ensure_ascii=False))],
            structuredContent=payload,
        )

    _wrapped.__signature__ = inspect.signature(handler)
    return _wrapped


def _safe_package_version(package_name: str) -> str | None:
    try:
        return metadata.version(package_name)
    except metadata.PackageNotFoundError:
        return None


def _version_at_least(version_text: str, minimum: tuple[int, ...]) -> bool:
    parts = []
    for chunk in str(version_text).split("."):
        digits = "".join(character for character in chunk if character.isdigit())
        if not digits:
            break
        parts.append(int(digits))
    if not parts:
        return False
    if len(parts) < len(minimum):
        parts.extend([0] * (len(minimum) - len(parts)))
    return tuple(parts[: len(minimum)]) >= minimum
