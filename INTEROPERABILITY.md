# Relaytic Interoperability

Relaytic exposes a local-first interoperability layer so common agent hosts can drive the same product surface without vendor-specific forks.

## Default model

Relaytic's source of truth is a Relaytic-owned MCP server plus the canonical `relaytic` CLI.

- local agent hosts should use `stdio` MCP when possible
- connector-style clients can use local `streamable-http`
- public HTTPS exposure is optional and never the default

## Host activation truth

- Claude Code: repo-local auto-discovery through `.mcp.json`, plus one approval step for the MCP server
- Codex/OpenAI local skill environments: repo-local discovery through `.agents/skills/relaytic/SKILL.md`
- OpenClaw: workspace-local discovery through `skills/relaytic/SKILL.md`
- ChatGPT: no repository auto-discovery; requires explicit connector registration against a public HTTPS `/mcp` endpoint

All checked-in agent-facing host notes should point new agents to `docs/handbooks/relaytic_agent_handbook.md` before they begin driving Relaytic.

## Quick checks

```bash
relaytic interoperability show
relaytic interoperability self-check
relaytic interoperability self-check --live
```

Use `--format json` when another agent needs machine-readable output, including per-host `discoverable_now`, `requires_activation`, and `next_step` fields.

## Local stdio MCP

This is the safest default for local tools such as Claude Code and similar hosts that can spawn Relaytic directly.

```bash
relaytic interoperability serve-mcp --transport stdio
```

The checked-in [.mcp.json](.mcp.json) uses this mode.

## Local HTTP MCP

Use local HTTP only when a client needs a reachable endpoint instead of a subprocess.

```bash
relaytic interoperability serve-mcp --transport streamable-http --host 127.0.0.1 --port 8000 --mount-path /mcp
```

Default safety rule:

- bind to `127.0.0.1`
- do not expose `/mcp` publicly without trusted TLS and auth controls

## Checked-in host bundles

Relaytic keeps thin wrappers for common hosts:

- Claude Code: [.mcp.json](.mcp.json) and [.claude/agents/relaytic.md](.claude/agents/relaytic.md)
- Codex/OpenAI skills: [.agents/skills/relaytic/SKILL.md](.agents/skills/relaytic/SKILL.md)
- OpenClaw workspace skill: [skills/relaytic/SKILL.md](skills/relaytic/SKILL.md)
- OpenClaw: [openclaw/skills/relaytic/SKILL.md](openclaw/skills/relaytic/SKILL.md)
- ChatGPT connector guidance: [connectors/chatgpt/README.md](connectors/chatgpt/README.md)

For human onboarding and operator-facing explanation, use:

- [docs/handbooks/relaytic_user_handbook.md](docs/handbooks/relaytic_user_handbook.md)
- [docs/handbooks/relaytic_agent_handbook.md](docs/handbooks/relaytic_agent_handbook.md)
- [docs/handbooks/relaytic_demo_walkthrough.md](docs/handbooks/relaytic_demo_walkthrough.md)

Generate fresh copies into another directory with:

```bash
relaytic interoperability export --host all --output-dir artifacts/interop_export --force
```

## Tool surface

The MCP server exposes Relaytic-owned tools over the current MVP and specialist phases, including:

- `relaytic_run`
- `relaytic_show_run`
- `relaytic_show_runtime`
- `relaytic_get_status`
- `relaytic_show_intelligence`
- `relaytic_show_research`
- `relaytic_show_assist`
- `relaytic_predict`
- `relaytic_intake_interpret`
- `relaytic_investigate_dataset`
- `relaytic_generate_plan`
- `relaytic_run_evidence_review`
- `relaytic_run_intelligence`
- `relaytic_gather_research`
- `relaytic_assist_turn`
- `relaytic_review_completion`
- `relaytic_review_lifecycle`
- `relaytic_show_lifecycle`
- `relaytic_run_autonomy`
- `relaytic_show_autonomy`
- `relaytic_doctor`
- `relaytic_integrations_show`

Use `relaytic_server_info` as the compact health and discovery tool before larger operations.

## Safety rules

- keep Relaytic local-first by default
- keep checked-in host bundles free of secrets and machine-specific paths
- prefer Relaytic artifacts over prose when another agent needs the result
- use public HTTPS `/mcp` only behind explicit deployment infrastructure you trust

## Verification

Recommended verification after changing interoperability code:

```bash
relaytic interoperability self-check --live
python -m pytest tests/test_cli_slice08a.py tests/test_interoperability_mcp.py tests/test_cli_slice09b.py -q
```
