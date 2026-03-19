# Slice 08B - Host activation and discovery

## Goal

Make host reachability explicit and improve automatic discovery where the host platform allows it.

## Load-bearing improvement

After this slice, Relaytic can say which hosts can call it immediately from the repository, which still need one approval step, and which require a registered remote connector.

## Human surface

- `relaytic interoperability show` now reports host discovery state and next-step guidance
- repo-local OpenClaw discovery through `skills/relaytic/SKILL.md`
- clearer ChatGPT connector guidance that distinguishes private registration from public discoverability

## Agent surface

- machine-readable `discoverable_now`, `requires_activation`, `requires_public_https`, and `next_step` fields per host
- top-level host summary for agents deciding whether Relaytic can be invoked immediately

## Intelligence source

- deterministic host-readiness metadata
- deterministic bundle drift checks
- explicit host-activation doctrine instead of guesswork

## Required behavior

- Claude readiness must reflect project-local auto-discovery with one approval step
- Codex/OpenAI skill readiness must reflect repo-local skill discovery
- OpenClaw readiness must reflect workspace-level `skills/relaytic/SKILL.md` discovery
- ChatGPT readiness must remain explicit about needing a registered public HTTPS `/mcp` connector

## First implementation moves

- extend host bundle metadata with discovery and activation fields
- add a root `skills/relaytic/SKILL.md` mirror for workspace-level OpenClaw discovery
- surface activation state in `relaytic interoperability show`
- align docs so the host-specific truth is clear

## Minimum proof

- interoperability inventory exposes correct host readiness states
- exported host bundles include the workspace-level OpenClaw skill path
- ChatGPT host metadata remains non-auto-discoverable and HTTPS-gated

## Fallback rule

If a host cannot auto-discover Relaytic, the canonical CLI and MCP surfaces still remain the source of truth.

## Innovation hook

Relaytic should not only be interoperable in theory; it should be legible to other agents about exactly how it becomes callable in each ecosystem.
