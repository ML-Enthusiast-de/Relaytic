# Slice 13C - Background daemon, resumable jobs, and memory maintenance

## Status

Implemented.

Intended package boundaries:

- `src/relaytic/daemon/`
- extend `src/relaytic/pulse/`
- extend `src/relaytic/search/`
- extend `src/relaytic/memory/`
- extend `src/relaytic/workspace/`
- extend `src/relaytic/mission_control/`

Intended artifacts:

- `daemon_state.json`
- `background_job_registry.json`
- `background_job_log.jsonl`
- `background_checkpoint.json`
- `resume_session_manifest.json`
- `background_approval_queue.json`
- `memory_maintenance_queue.json`
- `memory_maintenance_report.json`
- `search_resume_plan.json`
- `stale_job_report.json`

## Intent

Slice 13C is where Relaytic becomes reliably resumable over time instead of only interactive in one foreground session.

The goal is not unbounded autonomous background behavior. The goal is visible, stoppable, policy-gated background work for pulse, search, memory maintenance, and longer governed experiments.

This slice must continue obeying:

- `docs/specs/workspace_lifecycle.md`
- `docs/specs/governed_learnings_schema.md`
- `docs/specs/mission_control_flows.md`
- `docs/specs/test_and_proof_matrix.md`

## Load-Bearing Improvement

- Relaytic should be able to run bounded background work, resume interrupted jobs, and maintain workspace memory over time without becoming a hidden daemon that acts outside operator or agent visibility

## Human Surface

- humans should be able to see active jobs, waiting jobs, stuck jobs, resumed jobs, and memory-maintenance jobs from mission control without reading raw logs

## Agent Surface

- external agents should be able to query one background-job registry, one resume manifest, and one approval queue to understand what is running, what is paused, and what needs a decision

## Intelligence Source

- event bus and permission modes from Slice 13B, pulse watchlists, search-controller outputs, workspace state, result contracts, and governed learnings/memory policy

## Fallback Rule

- when background execution is disabled, Relaytic must still produce the same planned job manifests and resume plans so the work can be run interactively without changing truth or dropping state

## Required Behavior

- Slice 13C must consume the event and permission substrate from Slice 13B instead of inventing a parallel daemon-specific authority model
- background work must be bounded, explicit, and stoppable; Relaytic must never create hidden long-running activity that mission control and external agents cannot inspect
- daemon-managed jobs must cover at least:
  - pulse follow-up
  - search-controller campaigns
  - memory compaction or reaffirmation maintenance
  - long-running benchmark or challenger jobs when policy allows
- resumability must be based on explicit checkpoints and job manifests rather than best-effort local process memory
- memory maintenance must become a real queue with visible reasons, not just an occasional side effect inside pulse
- background approval requests must be visible and consumable through mission control and MCP
- workspace resume should restore the current result contract, active jobs, pending approvals, and next-run posture coherently

## Proof Obligation

- Relaytic must prove that background execution increases continuity and operator leverage without reducing inspectability, control clarity, or replayability

## Acceptance Criteria

Slice 13C is acceptable only if:

1. one long-running search or benchmark job resumes from checkpoint after interruption
2. one memory-maintenance task runs in the background and leaves an explicit before/after report
3. one background task is queued, approved, and started through the explicit approval path rather than silently running
4. one workspace resume restores active-job state and pending approvals without losing the current result contract
5. one stale or failed job is surfaced explicitly with a reason and recovery suggestion

## Required Verification

Slice 13C should not be considered complete without targeted tests that cover at least:

- one checkpoint-resume case
- one background approval case
- one memory-maintenance queue case
- one workspace-resume case
- one stale-job recovery case
- one regression guard against hidden background activity
