# Relaytic Runtime

Relaytic has a local runtime that acts as the shared control plane for CLI,
MCP, mission control, supervision, and background work.

The runtime is local-first, append-only where ordering matters, and designed to
make specialist behavior inspectable.

## What It Owns

- stage transition events
- checkpoint manifests
- hook execution audit
- specialist capability profiles
- data-access audit
- context-influence tracking
- permission and approval decisions
- resumable background-job state
- workspace and result-contract projections
- supervision handoff and freshness state

Canonical runtime artifacts:

- `lab_event_stream.jsonl`
- `hook_execution_log.json`
- `run_checkpoint_manifest.json`
- `capability_profiles.json`
- `data_access_audit.json`
- `context_influence_report.json`
- `permission_mode.json`
- `permission_decision_log.jsonl`
- `background_job_state.json`
- `workspace_state.json`
- `result_contract.json`

## Safety Model

- local-first by default
- no remote daemon required
- background execution is bounded and explicit
- approval-requiring work cannot silently cross permission modes
- read-only hooks by default
- write hooks blocked unless policy explicitly enables them
- semantic work rowless by default
- specialist capabilities declared up front instead of inferred ad hoc

## CLI Surface

Inspect the runtime for an existing run:

```bash
relaytic runtime show --run-dir artifacts/run_example
relaytic runtime show --run-dir artifacts/run_example --format json
```

Inspect recent events:

```bash
relaytic runtime events --run-dir artifacts/run_example --limit 12
relaytic runtime events --run-dir artifacts/run_example --limit 12 --format json
```

Inspect permission and background state:

```bash
relaytic permissions show --run-dir artifacts/run_example --format json
relaytic daemon show --run-dir artifacts/run_example --format json
relaytic remote show --run-dir artifacts/run_example --format json
```

`relaytic show` also surfaces a compact runtime summary so humans and agents do not need to read the raw event log first.

## What Humans Get

- one visible current stage for the run
- a count of recent events and checkpoints
- visible denied-access counts
- visible hook behavior
- explicit specialist-capability inventory on disk
- visible permission, approval, and resumable-job posture
- one current workspace result and next-run plan

## What Agents Get

- append-only machine-readable events
- stable runtime JSON artifacts
- the same runtime state from CLI and MCP
- a deterministic fallback path when hooks are absent or blocked
- rowless workspace and handoff contracts for safe continuation

## Design Rule

The runtime does not replace Relaytic's artifacts. It coordinates them.

Run artifacts on disk remain the canonical source of truth. The runtime exists to make transitions, capability boundaries, and long-running coordination explicit and inspectable.
