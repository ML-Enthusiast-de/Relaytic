"""Interoperability inventory and self-check surfaces for Relaytic."""

from __future__ import annotations

import os
from pathlib import Path
import socket
import subprocess
import sys
from typing import Any

from relaytic.interoperability.exports import (
    DEFAULT_MCP_ARGS,
    DEFAULT_MCP_COMMAND,
    build_host_bundle_specs,
)
from relaytic.interoperability.server import build_mcp_sdk_status
from relaytic.interoperability.service import (
    INTEROPERABILITY_SCHEMA_VERSION,
    build_interoperability_tool_specs,
)


INTEROPERABILITY_SELF_CHECK_SCHEMA_VERSION = "relaytic.interoperability_self_check.v1"


def build_interoperability_inventory() -> dict[str, Any]:
    """Return the current interoperability inventory for humans and agents."""
    tool_specs = build_interoperability_tool_specs()
    repo_root = _repo_root()
    host_specs = build_host_bundle_specs()
    hosts = []
    for spec in host_specs:
        existing = []
        ready = True
        for bundle_file in spec.files:
            path = repo_root / bundle_file.relative_path
            exists = path.exists()
            matches = exists and path.read_text(encoding="utf-8") == bundle_file.content
            existing.append(
                {
                    "path": bundle_file.relative_path,
                    "exists": exists,
                    "content_match": matches,
                    "description": bundle_file.description,
                }
            )
            ready = ready and matches
        hosts.append(
            {
                "host": spec.host,
                "title": spec.title,
                "install_mode": spec.install_mode,
                "description": spec.description,
                "notes": list(spec.notes),
                "discovery_mode": spec.discovery_mode,
                "discoverable_now": spec.discoverable_now,
                "requires_activation": spec.requires_activation,
                "requires_public_https": spec.requires_public_https,
                "requires_publication": spec.requires_publication,
                "next_step": spec.next_step,
                "status": "ready" if ready else "incomplete",
                "files": existing,
            }
        )
    discoverable_hosts = [host["host"] for host in hosts if host.get("discoverable_now")]
    activation_required_hosts = [host["host"] for host in hosts if host.get("requires_activation")]
    public_https_hosts = [host["host"] for host in hosts if host.get("requires_public_https")]
    return {
        "schema_version": INTEROPERABILITY_SCHEMA_VERSION,
        "status": "ok",
        "product": "Relaytic",
        "mcp_sdk": build_mcp_sdk_status(),
        "server": {
            "command": DEFAULT_MCP_COMMAND,
            "args": list(DEFAULT_MCP_ARGS),
            "mount_path": build_mcp_sdk_status()["mount_path"],
        },
        "tools": [
            {
                "name": spec.name,
                "title": spec.title,
                "category": spec.category,
                "description": spec.description,
                "annotations": dict(spec.annotations),
            }
            for spec in tool_specs
        ],
        "tool_count": len(tool_specs),
        "host_summary": {
            "discoverable_now": discoverable_hosts,
            "requires_activation": activation_required_hosts,
            "requires_public_https": public_https_hosts,
        },
        "hosts": hosts,
    }


def render_interoperability_inventory_markdown(payload: dict[str, Any]) -> str:
    """Render the interoperability inventory in concise human-readable form."""
    mcp_sdk = dict(payload.get("mcp_sdk", {}))
    lines = [
        "# Relaytic Interoperability",
        "",
        f"- Status: `{payload.get('status', 'unknown')}`",
        f"- MCP SDK installed: `{mcp_sdk.get('installed')}`",
        f"- MCP SDK compatible: `{mcp_sdk.get('compatible')}`",
        f"- Default transport: `{mcp_sdk.get('default_transport', 'stdio')}`",
        f"- Remote transport: `{mcp_sdk.get('remote_transport', 'streamable-http')}`",
        f"- Tool count: `{payload.get('tool_count', 0)}`",
        "",
        "## Host Summary",
    ]
    host_summary = dict(payload.get("host_summary", {}))
    lines.extend(
        [
            f"- Discoverable now: `{', '.join(host_summary.get('discoverable_now', [])) or 'none'}`",
            f"- Requires activation: `{', '.join(host_summary.get('requires_activation', [])) or 'none'}`",
            f"- Requires public HTTPS: `{', '.join(host_summary.get('requires_public_https', [])) or 'none'}`",
            "",
            "## Tool Surface",
        ]
    )
    for tool in payload.get("tools", []):
        lines.append(f"- `{tool.get('name')}`: {tool.get('description')}")
    lines.extend(["", "## Host Bundles"])
    for host in payload.get("hosts", []):
        lines.append(
            f"- `{host.get('host')}`: `{host.get('status')}`"
            f" discoverable_now=`{host.get('discoverable_now')}`"
            f" mode=`{host.get('discovery_mode')}`"
        )
        next_step = str(host.get("next_step", "")).strip()
        if next_step:
            lines.append(f"  next: {next_step}")
    return "\n".join(lines).strip() + "\n"


def build_interoperability_self_check_report(*, live: bool = False) -> dict[str, Any]:
    """Return a compatibility and drift check for Relaytic interoperability surfaces."""
    inventory = build_interoperability_inventory()
    mcp_sdk = dict(inventory.get("mcp_sdk", {}))
    host_checks = []
    warnings: list[str] = []
    for host in inventory.get("hosts", []):
        status = str(host.get("status", "unknown"))
        host_checks.append(
            {
                "host": host.get("host"),
                "status": "ok" if status == "ready" else "warn",
                "files": host.get("files", []),
            }
        )
        if status != "ready":
            warnings.append(f"{host.get('host')}_bundle")
    live_check = {
        "enabled": live,
        "status": "skipped",
        "tool_count": inventory.get("tool_count", 0),
    }
    if live:
        live_check = run_live_mcp_stdio_smoke_check()
        if live_check.get("status") != "ok":
            warnings.append("live_stdio_mcp")
    status = "ok"
    if not mcp_sdk.get("installed"):
        status = "warn"
        warnings.append("mcp_missing")
    elif not mcp_sdk.get("compatible"):
        status = "warn"
        warnings.append("mcp_version")
    if live and live_check.get("status") != "ok":
        status = "error"
    return {
        "schema_version": INTEROPERABILITY_SELF_CHECK_SCHEMA_VERSION,
        "status": status,
        "inventory": inventory,
        "host_bundle_checks": host_checks,
        "live_stdio_mcp": live_check,
        "warnings": warnings,
    }


def render_interoperability_self_check_markdown(report: dict[str, Any]) -> str:
    """Render the interoperability self-check for humans."""
    live = dict(report.get("live_stdio_mcp", {}))
    lines = [
        "# Relaytic Interoperability Self-Check",
        "",
        f"- Status: `{report.get('status', 'unknown')}`",
    ]
    inventory = dict(report.get("inventory", {}))
    mcp_sdk = dict(inventory.get("mcp_sdk", {}))
    lines.append(f"- MCP SDK installed: `{mcp_sdk.get('installed')}`")
    lines.append(f"- MCP SDK compatible: `{mcp_sdk.get('compatible')}`")
    lines.extend(["", "## Host Bundles"])
    for item in report.get("host_bundle_checks", []):
        lines.append(f"- `{item.get('host')}`: `{item.get('status')}`")
    lines.extend(["", "## Live MCP Smoke"])
    lines.append(f"- Enabled: `{live.get('enabled')}`")
    lines.append(f"- Status: `{live.get('status')}`")
    if live.get("tool_names"):
        lines.append(f"- Tools: `{', '.join(live.get('tool_names', []))}`")
    warnings = [str(item) for item in report.get("warnings", []) if str(item).strip()]
    if warnings:
        lines.extend(["", "## Warnings"])
        for item in warnings:
            lines.append(f"- `{item}`")
    return "\n".join(lines).strip() + "\n"


def run_live_mcp_stdio_smoke_check() -> dict[str, Any]:
    """Start the local stdio MCP server and verify the Relaytic tool contract."""
    mcp_status = build_mcp_sdk_status()
    if not mcp_status.get("installed"):
        return {"enabled": True, "status": "skipped", "reason": "mcp_not_installed"}
    try:
        import anyio
        from mcp import ClientSession
        from mcp.client.stdio import StdioServerParameters, stdio_client
    except ImportError:
        return {"enabled": True, "status": "skipped", "reason": "mcp_import_failed"}

    async def _smoke() -> dict[str, Any]:
        env = os.environ.copy()
        src_dir = str(_repo_root() / "src")
        env["PYTHONPATH"] = src_dir if not env.get("PYTHONPATH") else src_dir + os.pathsep + env["PYTHONPATH"]
        params = StdioServerParameters(
            command=sys.executable,
            args=[
                "-m",
                "relaytic.ui.cli",
                "interoperability",
                "serve-mcp",
                "--transport",
                "stdio",
            ],
            env=env,
        )
        async with stdio_client(params, errlog=sys.__stderr__) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                tools = await session.list_tools()
                result = await session.call_tool("relaytic_server_info", {})
                structured = getattr(result, "structuredContent", None) or getattr(result, "structured_content", None)
                tool_names = [tool.name for tool in tools.tools]
                return {
                    "enabled": True,
                    "status": "ok",
                    "tool_count": len(tool_names),
                    "tool_names": tool_names,
                    "server_status": dict(structured or {}).get("status"),
                }

    try:
        return anyio.run(_smoke)
    except Exception as exc:  # pragma: no cover
        return {
            "enabled": True,
            "status": "error",
            "error": str(exc),
        }


def run_live_streamable_http_smoke_check(*, port: int | None = None) -> dict[str, Any]:
    """Start the local HTTP MCP server and verify the compact Relaytic health tool."""
    mcp_status = build_mcp_sdk_status()
    if not mcp_status.get("installed"):
        return {"enabled": True, "status": "skipped", "reason": "mcp_not_installed"}
    try:
        import anyio
        from mcp import ClientSession
        from mcp.client.streamable_http import streamable_http_client
    except ImportError:
        return {"enabled": True, "status": "skipped", "reason": "mcp_import_failed"}

    selected_port = int(port or find_available_port())
    process = start_streamable_http_server_process(port=selected_port)
    url = f"http://127.0.0.1:{selected_port}/mcp"

    async def _smoke() -> dict[str, Any]:
        last_error: str | None = None
        for _ in range(30):
            try:
                async with streamable_http_client(url) as (read_stream, write_stream, _get_session_id):
                    async with ClientSession(read_stream, write_stream) as session:
                        await session.initialize()
                        tools = await session.list_tools()
                        result = await session.call_tool("relaytic_server_info", {})
                        structured = getattr(result, "structuredContent", None) or getattr(result, "structured_content", None)
                        return {
                            "enabled": True,
                            "status": "ok",
                            "url": url,
                            "tool_count": len(tools.tools),
                            "server_status": dict(structured or {}).get("status"),
                        }
            except Exception as exc:  # pragma: no cover - retried and surfaced below
                last_error = str(exc)
                await anyio.sleep(0.25)
        return {
            "enabled": True,
            "status": "error",
            "url": url,
            "error": last_error or "streamable_http_unavailable",
        }

    try:
        return anyio.run(_smoke)
    finally:
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)


def find_available_port() -> int:
    """Find an available localhost TCP port for integration tests."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def start_streamable_http_server_process(*, port: int) -> subprocess.Popen[str]:
    """Launch the Relaytic MCP server over streamable HTTP for tests and local checks."""
    env = os.environ.copy()
    src_dir = str(_repo_root() / "src")
    env["PYTHONPATH"] = src_dir if not env.get("PYTHONPATH") else src_dir + os.pathsep + env["PYTHONPATH"]
    return subprocess.Popen(
        [
            sys.executable,
            "-m",
            "relaytic.ui.cli",
            "interoperability",
            "serve-mcp",
            "--transport",
            "streamable-http",
            "--host",
            "127.0.0.1",
            "--port",
            str(port),
            "--mount-path",
            "/mcp",
        ],
        cwd=_repo_root(),
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]
