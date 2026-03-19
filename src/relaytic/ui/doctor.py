"""Runtime health checks for install and dependency verification."""

from __future__ import annotations

from datetime import datetime, timezone
from importlib import metadata, util
import platform
import sys
from typing import Any

from relaytic.integrations import build_integration_self_check_report
from relaytic.interoperability import build_interoperability_self_check_report


DOCTOR_SCHEMA_VERSION = "relaytic.doctor_report.v1"

_CORE_PACKAGES = (
    ("numpy", "numpy"),
    ("pandas", "pandas"),
    ("openpyxl", "openpyxl"),
    ("pyyaml", "yaml"),
)

_FULL_PROFILE_PACKAGES = (
    ("scikit-learn", "sklearn"),
    ("scipy", "scipy"),
    ("matplotlib", "matplotlib"),
    ("pandera", "pandera"),
    ("statsmodels", "statsmodels"),
    ("imbalanced-learn", "imblearn"),
    ("pyod", "pyod"),
    ("mcp", "mcp"),
)


def build_doctor_report(*, expected_profile: str = "core") -> dict[str, Any]:
    """Build a machine-readable install and dependency health report."""
    normalized_profile = str(expected_profile).strip().lower() or "core"
    core = [_package_check(package_name=package_name, import_name=import_name) for package_name, import_name in _CORE_PACKAGES]
    extras: list[dict[str, Any]] = []
    if normalized_profile == "full":
        extras = [_package_check(package_name=package_name, import_name=import_name) for package_name, import_name in _FULL_PROFILE_PACKAGES]
    integration_report = build_integration_self_check_report()
    interoperability_report = build_interoperability_self_check_report(live=False)
    blocking_issues = [
        item["package_name"]
        for item in core + extras
        if item["required"] and item["status"] != "installed"
    ]
    warnings = [
        item.get("integration")
        for item in integration_report.get("checks", [])
        if str(item.get("status", "")).strip() not in {"ok", "not_installed", "guarded"}
    ]
    if str(interoperability_report.get("status", "")).strip() not in {"ok"}:
        warnings.append("interoperability")
    status = "ok"
    if blocking_issues:
        status = "error"
    elif warnings:
        status = "warn"
    try:
        relaytic_version = metadata.version("relaytic")
    except metadata.PackageNotFoundError:
        relaytic_version = None
    return {
        "schema_version": DOCTOR_SCHEMA_VERSION,
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "product": "Relaytic",
        "status": status,
        "expected_profile": normalized_profile,
        "python": {
            "version": platform.python_version(),
            "executable": sys.executable,
            "major": sys.version_info.major,
            "minor": sys.version_info.minor,
            "compatible": sys.version_info >= (3, 10),
        },
        "package": {
            "name": "relaytic",
            "version": relaytic_version,
            "installed": relaytic_version is not None,
        },
        "core_dependencies": core,
        "profile_dependencies": extras,
        "integration_self_check": integration_report,
        "interoperability_self_check": interoperability_report,
        "blocking_issues": blocking_issues,
        "warnings": warnings,
    }


def render_doctor_markdown(report: dict[str, Any]) -> str:
    """Render a concise human-readable doctor report."""
    python_block = dict(report.get("python", {}))
    package_block = dict(report.get("package", {}))
    lines = [
        "# Relaytic Doctor",
        "",
        f"- Status: `{report.get('status', 'unknown')}`",
        f"- Expected profile: `{report.get('expected_profile', 'core')}`",
        f"- Python: `{python_block.get('version', 'unknown')}`",
        f"- Relaytic installed: `{package_block.get('installed')}`",
    ]
    lines.extend(["", "## Core Dependencies"])
    for item in report.get("core_dependencies", []):
        lines.append(_render_dep_line(item))
    profile_dependencies = list(report.get("profile_dependencies", []))
    if profile_dependencies:
        lines.extend(["", "## Profile Dependencies"])
        for item in profile_dependencies:
            lines.append(_render_dep_line(item))
    checks = list(dict(report.get("integration_self_check", {})).get("checks", []))
    if checks:
        lines.extend(["", "## Integration Self-Check"])
        for item in checks:
            lines.append(
                f"- `{item.get('integration', 'unknown')}`: `{item.get('status', 'unknown')}`"
            )
    interop = dict(report.get("interoperability_self_check", {}))
    if interop:
        lines.extend(["", "## Interoperability Self-Check"])
        lines.append(f"- Status: `{interop.get('status', 'unknown')}`")
        inventory = dict(interop.get("inventory", {}))
        mcp_sdk = dict(inventory.get("mcp_sdk", {}))
        if mcp_sdk:
            lines.append(f"- MCP SDK installed: `{mcp_sdk.get('installed')}`")
            lines.append(f"- MCP SDK compatible: `{mcp_sdk.get('compatible')}`")
    blocking = list(report.get("blocking_issues", []))
    warnings = [str(item) for item in report.get("warnings", []) if str(item).strip()]
    if blocking:
        lines.extend(["", "## Blocking Issues"])
        for item in blocking:
            lines.append(f"- `{item}` is required but missing.")
    if warnings:
        lines.extend(["", "## Warnings"])
        for item in warnings:
            lines.append(f"- `{item}` reported a non-ideal self-check result.")
    return "\n".join(lines).strip() + "\n"


def _package_check(*, package_name: str, import_name: str) -> dict[str, Any]:
    installed = util.find_spec(import_name) is not None
    version = None
    if installed:
        try:
            version = metadata.version(package_name)
        except metadata.PackageNotFoundError:
            version = None
    return {
        "package_name": package_name,
        "import_name": import_name,
        "status": "installed" if installed else "missing",
        "version": version,
        "required": True,
    }


def _render_dep_line(item: dict[str, Any]) -> str:
    return (
        f"- `{item.get('package_name', 'unknown')}`: `{item.get('status', 'unknown')}`"
        + (f" (`{item.get('version')}`)" if item.get("version") else "")
    )
