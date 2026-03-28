"""Host-specific bundle generation for Relaytic interoperability."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from relaytic.core.json_utils import dumps_json
from relaytic.interoperability.models import HostBundleFile, HostBundleSpec


HOST_BUNDLE_MANIFEST_SCHEMA_VERSION = "relaytic.host_bundle_manifest.v1"
DEFAULT_MCP_COMMAND = "python"
DEFAULT_MCP_ARGS = (
    "-m",
    "relaytic.ui.cli",
    "interoperability",
    "serve-mcp",
    "--transport",
    "stdio",
)


def build_host_bundle_specs(
    *,
    mcp_command: str = DEFAULT_MCP_COMMAND,
    mcp_args: tuple[str, ...] = DEFAULT_MCP_ARGS,
    public_mcp_url: str = "https://example.com/mcp",
) -> list[HostBundleSpec]:
    """Return the canonical Relaytic host-integration bundles."""
    return [
        HostBundleSpec(
            host="claude",
            title="Claude Code project bundle",
            install_mode="project-local",
            description="Project-scoped MCP and subagent surfaces for Claude Code and related Anthropic tools.",
            files=(
                HostBundleFile(
                    relative_path=".mcp.json",
                    content=render_project_mcp_config(mcp_command=mcp_command, mcp_args=mcp_args),
                    description="Project-scoped Claude Code MCP configuration for Relaytic.",
                ),
                HostBundleFile(
                    relative_path=".claude/agents/relaytic.md",
                    content=render_claude_agent_markdown(),
                    description="Claude subagent/skill instructions for Relaytic.",
                ),
            ),
            notes=(
                "Claude Code can use the checked-in `.mcp.json` directly for project-local stdio MCP.",
                "Remote Anthropic MCP connectors should point at a public HTTPS Relaytic `/mcp` endpoint instead of local stdio.",
            ),
            discovery_mode="project_auto",
            discoverable_now=True,
            requires_activation=True,
            next_step="Open this repository in Claude Code and approve the project-local MCP server when prompted.",
        ),
        HostBundleSpec(
            host="codex",
            title="Codex/OpenAI skill bundle",
            install_mode="repo-local or user-skill-dir",
            description="OpenAI/Codex skill wrapper that teaches the host to use Relaytic safely and consistently.",
            files=(
                HostBundleFile(
                    relative_path=".agents/skills/relaytic/SKILL.md",
                    content=render_codex_skill_markdown(),
                    description="Codex/OpenAI skill bundle for Relaytic.",
                ),
            ),
            notes=(
                "The skill assumes `relaytic` is installed and available in the active Python environment.",
                "ChatGPT uses MCP connectors rather than project-local skills; see the ChatGPT bundle for remote setup guidance.",
            ),
            discovery_mode="repo_skill_auto",
            discoverable_now=True,
            requires_activation=False,
            next_step="Use the checked-in Relaytic skill from this repository or copy it into your user skill directory.",
        ),
        HostBundleSpec(
            host="openclaw",
            title="OpenClaw skill bundle",
            install_mode="workspace-skill-dir or ~/.openclaw/skills",
            description="OpenClaw skill wrapper for Relaytic CLI and MCP-backed workflows.",
            files=(
                HostBundleFile(
                    relative_path="skills/relaytic/SKILL.md",
                    content=render_openclaw_skill_markdown(),
                    description="Workspace-local OpenClaw skill for Relaytic auto-discovery.",
                ),
                HostBundleFile(
                    relative_path="openclaw/skills/relaytic/SKILL.md",
                    content=render_openclaw_skill_markdown(),
                    description="Reference OpenClaw skill bundle for Relaytic.",
                ),
            ),
            notes=(
                "OpenClaw workspace discovery should use `skills/relaytic/SKILL.md` when the repo is the current workspace.",
                "The mirrored `openclaw/skills/relaytic/SKILL.md` remains as an explicit export/reference copy.",
            ),
            discovery_mode="workspace_skill_auto",
            discoverable_now=True,
            requires_activation=False,
            next_step="Open this repository as the OpenClaw workspace so the checked-in `skills/relaytic/SKILL.md` can be discovered directly.",
        ),
        HostBundleSpec(
            host="chatgpt",
            title="ChatGPT connector guidance",
            install_mode="export-and-deploy",
            description="Guidance for exposing Relaytic as a public HTTPS MCP endpoint for ChatGPT connectors.",
            files=(
                HostBundleFile(
                    relative_path="connectors/chatgpt/README.md",
                    content=render_chatgpt_connector_markdown(public_mcp_url=public_mcp_url),
                    description="ChatGPT connector setup guide for Relaytic's `/mcp` endpoint.",
                ),
            ),
            notes=(
                "ChatGPT connectors require a public HTTPS `/mcp` endpoint.",
                "Relaytic serves local-only by default; expose it through trusted TLS/auth infrastructure when going public.",
            ),
            discovery_mode="remote_connector_registration",
            discoverable_now=False,
            requires_activation=True,
            requires_public_https=True,
            requires_publication=False,
            next_step="Expose Relaytic at a public HTTPS `/mcp` URL and register that connector inside ChatGPT.",
        ),
    ]


def export_host_bundles(
    *,
    output_dir: str | Path,
    host: str,
    force: bool = False,
    mcp_command: str = DEFAULT_MCP_COMMAND,
    mcp_args: tuple[str, ...] = DEFAULT_MCP_ARGS,
    public_mcp_url: str = "https://example.com/mcp",
) -> dict[str, Any]:
    """Write one or more Relaytic host bundles to disk."""
    root = Path(output_dir)
    root.mkdir(parents=True, exist_ok=True)
    requested = str(host).strip().lower() or "all"
    specs = build_host_bundle_specs(
        mcp_command=mcp_command,
        mcp_args=mcp_args,
        public_mcp_url=public_mcp_url,
    )
    if requested != "all":
        specs = [spec for spec in specs if spec.host == requested]
        if not specs:
            raise ValueError(f"Unsupported host bundle target: {host}")
    written_files: list[str] = []
    for spec in specs:
        for bundle_file in spec.files:
            path = root / bundle_file.relative_path
            if path.exists() and not force:
                raise FileExistsError(f"Refusing to overwrite existing host bundle file without --force: {path}")
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(bundle_file.content, encoding="utf-8")
            written_files.append(str(path))
    manifest = {
        "schema_version": HOST_BUNDLE_MANIFEST_SCHEMA_VERSION,
        "status": "ok",
        "output_dir": str(root),
        "hosts": [
            {
                "host": spec.host,
                "title": spec.title,
                "install_mode": spec.install_mode,
                "description": spec.description,
                "files": [bundle_file.relative_path for bundle_file in spec.files],
                "notes": list(spec.notes),
                "discovery_mode": spec.discovery_mode,
                "discoverable_now": spec.discoverable_now,
                "requires_activation": spec.requires_activation,
                "requires_public_https": spec.requires_public_https,
                "requires_publication": spec.requires_publication,
                "next_step": spec.next_step,
            }
            for spec in specs
        ],
        "written_files": written_files,
    }
    manifest_path = root / "relaytic_host_bundle_manifest.json"
    manifest_path.write_text(dumps_json(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    manifest["manifest_path"] = str(manifest_path)
    return manifest


def render_project_mcp_config(
    *,
    mcp_command: str = DEFAULT_MCP_COMMAND,
    mcp_args: tuple[str, ...] = DEFAULT_MCP_ARGS,
) -> str:
    """Render the project-scoped Claude `.mcp.json` configuration."""
    payload = {
        "mcpServers": {
            "relaytic": {
                "command": mcp_command,
                "args": list(mcp_args),
                "env": {
                    "PYTHONUTF8": "1",
                },
            }
        }
    }
    return json.dumps(payload, indent=2) + "\n"


def render_claude_agent_markdown() -> str:
    """Render the Claude agent guidance for Relaytic."""
    return """---
name: relaytic
description: Use Relaytic when a task involves structured data triage, dataset investigation, model routing, lifecycle review, or prediction from an existing Relaytic run.
---

# Relaytic

Use Relaytic for local-first structured-data modeling, review, and inference.

## Prefer this order

1. Use the project-local Relaytic MCP server when the `relaytic_*` tools are available.
2. Fall back to the `relaytic` CLI if MCP is unavailable.
3. Keep runs local-first and deterministic unless the user explicitly asks for stronger semantic help.

## Read First

- Start with `docs/handbooks/relaytic_agent_handbook.md` when you are new to the Relaytic surface or need the shortest command-first operating guide.

## Fast paths

- End-to-end: `relaytic run --data-path <data.csv> --text "Do everything on your own. Predict <target>."`
- Inspect: `relaytic show --run-dir <run_dir>`
- Status: `relaytic status --run-dir <run_dir>`
- Predict: `relaytic predict --run-dir <run_dir> --data-path <new_data.csv>`
- Lifecycle: `relaytic lifecycle show --run-dir <run_dir>`

## Guardrails

- Do not invent targets or forbidden columns when the dataset or artifacts can answer the question.
- Prefer Relaytic's structured artifacts over narrative summaries when handing results to other tools or agents.
- Keep secrets out of prompts, saved notes, and exported configs.
- For remote MCP exposure, require trusted HTTPS/auth infrastructure instead of exposing a local development server directly.
"""


def render_codex_skill_markdown() -> str:
    """Render the Codex/OpenAI skill guidance for Relaytic."""
    return """---
name: relaytic
description: Use Relaytic for local-first structured-data investigation, model planning, execution, lifecycle review, and inference.
---

# Relaytic

Relaytic is the local inference-engineering system in this workspace.

## When to use

- The user wants to model a structured dataset.
- A previous Relaytic run needs to be inspected, challenged, reviewed, or used for prediction.
- A downstream agent needs stable JSON artifacts instead of ad hoc prose.

## Preferred execution order

1. If Relaytic MCP tools are available, call them directly.
2. Otherwise use the `relaytic` CLI.
3. Prefer `relaytic run` for the main path unless the user explicitly asks for lower-level phase control.

## Read First

- If you are new to this repo, read `docs/handbooks/relaytic_agent_handbook.md` before using the CLI. It is the terse agent-oriented map of commands, artifacts, and supporting contracts.

## Core commands

- `relaytic run --data-path <data.csv> --text "<intent>"`
- `relaytic show --run-dir <run_dir> --format json`
- `relaytic status --run-dir <run_dir> --format json`
- `relaytic assist show --run-dir <run_dir> --format json`
- `relaytic assist turn --run-dir <run_dir> --message "<message>" --format json`
- `relaytic predict --run-dir <run_dir> --data-path <new_data.csv> --format json`
- `relaytic doctor --expected-profile full --format json`

## Safety rules

- Keep Relaytic local-first by default.
- Do not expose `/mcp` publicly without trusted HTTPS and auth controls.
- Treat `run_summary.json`, `completion_decision.json`, and lifecycle artifacts as the machine-facing source of truth.
- Use the assist surface when a human or external agent needs explanations, stage navigation, or safe takeover rather than inventing ad hoc chat behavior.
"""


def render_openclaw_skill_markdown() -> str:
    """Render the OpenClaw skill guidance for Relaytic."""
    return """---
name: relaytic
description: Structured-data investigation, modeling, evidence review, lifecycle decisions, and prediction through Relaytic.
---

# Relaytic

Use Relaytic when the task involves structured datasets, model generation, or reviewing an existing Relaytic run.

## Default workflow

1. Run `relaytic run --data-path <data.csv> --text "<intent>"`.
2. Inspect with `relaytic show --run-dir <run_dir>`.
3. Use `relaytic status --run-dir <run_dir>` for the governed state.
4. Use `relaytic predict --run-dir <run_dir> --data-path <new_data.csv>` for inference.

## Read First

- Start with `docs/handbooks/relaytic_agent_handbook.md` when you are new to the Relaytic surface or need the shortest command-first operating guide.

## Notes

- Relaytic is autonomous by default and will proceed with explicit assumptions when non-critical answers are missing.
- Prefer Relaytic JSON outputs when passing results to other tools or agents.
- Keep remote exposure behind trusted HTTPS/auth layers when using the MCP server outside local development.
"""


def render_chatgpt_connector_markdown(*, public_mcp_url: str) -> str:
    """Render the ChatGPT connector setup guidance."""
    return f"""# Relaytic ChatGPT Connector

Relaytic exposes a host-neutral MCP surface. For ChatGPT, expose that surface as a public HTTPS MCP endpoint.

This is not auto-discovered from the repository. You must register the connector explicitly in ChatGPT once you have a reachable HTTPS `/mcp` URL.

## Local server command

```bash
relaytic interoperability serve-mcp --transport streamable-http --host 127.0.0.1 --port 8000 --mount-path /mcp
```

## Public connector requirement

ChatGPT connectors expect a public HTTPS MCP endpoint. A typical production shape is:

1. Run the Relaytic MCP server locally or in your deployment environment.
2. Put it behind trusted TLS/auth infrastructure.
3. Expose the final endpoint at `/mcp`.
4. Register that public HTTPS URL inside ChatGPT.

Example public MCP URL:

```text
{public_mcp_url}
```

## Safety notes

- Do not commit tokens, headers, or private URLs.
- Relaytic binds to `127.0.0.1` by default; only widen exposure deliberately.
- Keep the remote boundary thin: MCP transport outside, Relaytic artifacts inside.
"""
