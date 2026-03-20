# Slice 09B - Local lab gateway, hook bus, and capability-scoped specialists

## Implementation Status

Implemented in the current baseline.

The current Slice 09B delivery includes:

- `src/relaytic/runtime/` as the canonical local runtime boundary
- `relaytic runtime show` and `relaytic runtime events`
- append-only `lab_event_stream.jsonl` traces plus checkpoint and hook ledgers
- explicit capability profiles and data-access audit for specialists
- shared runtime coordination across CLI, MCP, summaries, and public-dataset end-to-end flows

## Goal

Turn Relaytic from a sequence of strong commands into a secure local lab runtime with one control plane for CLI, MCP, later UI work, and long-running automation.

## Load-bearing improvement

After this slice, Relaytic should have a local-first runtime that owns run-state transitions, append-only event emission, hook dispatch, checkpointing, and specialist capability enforcement.

## Human surface

- humans can inspect the evented run state rather than inferring progress from scattered files
- humans can see what each specialist was allowed to read and write
- humans can see whether hooks observed or changed a run transition

## Agent surface

- external agents can consume one machine-readable event stream
- external agents can inspect capability profiles and hook execution without scraping prose
- CLI and MCP consumers can rely on the same runtime state rather than parallel control paths

## Intelligence source

- deterministic runtime coordination
- deterministic capability profiles
- deterministic hook policy
- artifact-backed checkpointing and reflection flush

## Required outputs

- `lab_event_stream.jsonl`
- `hook_execution_log.json`
- `run_checkpoint_manifest.json`
- `capability_profiles.json`
- `data_access_audit.json`
- `context_influence_report.json`

## Required behavior

- the runtime must stay local-first and must not require a remote daemon
- the event stream must be append-only and machine-readable
- hooks must default to read-only, local-only, and run-dir-scoped
- broader write scope must be explicit and auditable
- every specialist must declare a capability profile covering artifact read scope, write scope, raw-row access, semantic access, and external-adapter access
- semantic helpers and optional LLM-backed specialists must consume rowless summaries by default unless policy explicitly grants richer context
- the runtime must be able to checkpoint and flush reflection/memory state before retry, compaction, or final completion/lifecycle transitions

## First implementation moves

1. Add `src/relaytic/runtime/` for event emission, checkpointing, hook dispatch, and capability resolution.
2. Freeze the event schema for stage transitions, fallback events, hook calls, approvals, and capability overrides.
3. Add capability profiles for Scout, Scientist, Strategist, Builder, Challenger, Completion, Lifecycle, and semantic helpers.
4. Route `relaytic run` and the MCP server through the same runtime event path.
5. Add one deterministic read-only hook surface and one policy-gated write hook surface.
6. Add tests for capability enforcement, rowless semantic defaults, and pre-close flush behavior.

## Minimum proof

- one run where CLI and MCP views agree because they read the same evented runtime state
- one case where a specialist is denied over-broad access and Relaytic still proceeds safely
- one case where a read-only hook observes a transition without changing outcome
- one case where checkpoint and flush behavior preserves reflection/memory state across retry or completion boundaries

## Fallback rule

If hooks are absent or rejected, Relaytic still runs through the deterministic path and records the fallback in the event stream.

## Innovation hook

Relaytic should stop looking like a pipeline with agent labels and start behaving like a secure local inference lab runtime with explicit specialist capabilities and evented coordination.
