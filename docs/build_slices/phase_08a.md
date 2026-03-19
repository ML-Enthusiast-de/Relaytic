# Slice 08A - Interoperability and host adapters

## Goal

Make Relaytic reachable from the most common local agent hosts and developer tools without collapsing the product into vendor-specific shells.

## Load-bearing improvement

After this slice, Relaytic can be driven through a Relaytic-owned MCP server and thin checked-in host bundles instead of CLI-only usage.

## Human surface

- `relaytic interoperability show`
- `relaytic interoperability self-check`
- `relaytic interoperability export`
- `relaytic interoperability serve-mcp`
- checked-in usage surfaces for Claude, Codex/OpenAI, OpenClaw, and ChatGPT connector guidance

## Agent surface

- host-neutral MCP tool contract for the current MVP and phase-level flows
- compact `relaytic_server_info` health tool
- stable JSON payloads for run, status, prediction, lifecycle, doctor, and integration discovery

## Intelligence source

- deterministic host-bundle generation
- deterministic capability inventory
- local live MCP smoke checks
- existing Relaytic judgment stack reused through a transport-safe interface

## Required behavior

- local `stdio` transport must work for agent hosts that spawn Relaytic as a subprocess
- local `streamable-http` transport must work for connector-style clients on `127.0.0.1`
- checked-in host bundles must stay secret-free and machine-path-free
- `relaytic interoperability self-check --live` must verify the live stdio path
- at least one public-dataset flow must pass through the MCP surface end to end

## First implementation moves

- create `src/relaytic/interoperability/`
- expose the current MVP and slice-level surfaces through a Relaytic-owned MCP server
- add checked-in `.mcp.json`, Claude agent instructions, Codex/OpenAI skill bundle, OpenClaw skill bundle, and ChatGPT connector guidance
- add inventory and export helpers so humans and agents can inspect and reproduce the host bundles

## Minimum proof

- live stdio MCP smoke passes
- live local HTTP MCP smoke passes
- one public-dataset Relaytic run succeeds through the MCP client path
- host bundle drift checks pass

## Fallback rule

If the MCP SDK is not installed or a host cannot use MCP, Relaytic must remain fully usable through the canonical `relaytic` CLI.

## Innovation hook

Relaytic should be reachable from multiple popular agent ecosystems through one host-neutral contract, while staying local-first, safe by default, and auditable.
