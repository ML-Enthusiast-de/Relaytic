# Slice 14A - Remote mission control, approvals, and supervision handoff

## Status

Planned.

Intended package boundaries:

- `src/relaytic/remote_control/`
- extend `src/relaytic/interoperability/`
- extend `src/relaytic/mission_control/`
- extend `src/relaytic/permissions/`
- extend `src/relaytic/workspace/`

Intended artifacts:

- `remote_session_manifest.json`
- `remote_transport_report.json`
- `approval_request_queue.json`
- `approval_decision_log.jsonl`
- `remote_operator_presence.json`
- `supervision_handoff.json`
- `notification_delivery_report.json`
- `remote_control_audit.json`

## Intent

Slice 14A is where Relaytic gains a professional remote supervision surface without abandoning its local-first posture.

The goal is not public cloud orchestration by default. The goal is a trusted, explicit, read-mostly remote control layer for inspection, approval, denial, and resumption of already-governed workspaces and background jobs.

This slice must continue obeying:

- `docs/specs/workspace_lifecycle.md`
- `docs/specs/result_contract_schema.md`
- `docs/specs/mission_control_flows.md`
- `docs/specs/external_agent_continuation_contract.md`
- `docs/specs/test_and_proof_matrix.md`

## Load-Bearing Improvement

- Relaytic should allow humans and external agents to supervise a workspace remotely through the same truth used locally, including approvals, denials, resume actions, and handoff between operators or agents

## Human Surface

- humans should be able to inspect remote session status, pending approvals, supervision handoff state, and remote presence without guessing whether the remote surface is stale or authoritative

## Agent Surface

- external agents should be able to read and act on approval queues, supervision handoffs, and remote workspace truth through stable JSON-first surfaces rather than screen-scraping a UI shell

## Intelligence Source

- mission-control truth, event bus and permission modes from Slice 13B, daemon state from Slice 13C, workspace/result-contract state, and interoperability transport configuration

## Fallback Rule

- when remote transport is disabled or unavailable, Relaytic must still preserve the same approval and supervision artifacts locally so the same decisions can be made through CLI or MCP without remote drift

## Required Behavior

- Slice 14A must remain local-first by default; remote access should be explicitly enabled and clearly marked
- remote mission control must be read-mostly unless an action is explicitly approval-scoped or policy-allowed
- approvals, denials, and handoffs must use the same permission and event substrate as local sessions instead of inventing remote-only authority logic
- Relaytic must support explicit supervision handoff between:
  - human to human
  - human to external agent
  - external agent to human
  - external agent to external agent
- remote session state must expose freshness and transport posture so operators and agents know whether they are looking at live or stale state
- mission control, CLI, MCP, and remote supervision must remain semantically aligned on result contract, active jobs, pending approvals, and next-run posture

## Proof Obligation

- Relaytic must prove that remote supervision increases usability without creating a second, drift-prone source of truth or an invisible write path

## Acceptance Criteria

Slice 14A is acceptable only if:

1. one remote approval or denial changes the same local workspace truth that CLI and MCP later read
2. one supervision handoff transfers control cleanly between a human and an external agent
3. one remote session shows freshness and transport status explicitly
4. one locally disabled remote surface fails closed and leaves a clear audit trail rather than silently weakening policy

## Required Verification

Slice 14A should not be considered complete without targeted tests that cover at least:

- one remote approval case
- one remote denial case
- one supervision-handoff case
- one local-versus-remote truth-parity case
- one disabled-remote fail-closed case
- one audit-log regression guard
