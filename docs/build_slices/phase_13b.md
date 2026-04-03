# Slice 13B - Event bus, runtime hooks, and visible permission modes

## Status

Implemented.

Intended package boundaries:

- `src/relaytic/events/`
- `src/relaytic/permissions/`
- extend `src/relaytic/runtime/`
- extend `src/relaytic/mission_control/`
- extend `src/relaytic/interoperability/`

Intended artifacts:

- `event_schema.json`
- `event_subscription_registry.json`
- `hook_registry.json`
- `hook_dispatch_report.json`
- `permission_mode.json`
- `tool_permission_matrix.json`
- `approval_policy_report.json`
- `permission_decision_log.jsonl`
- `session_capability_contract.json`

## Intent

Slice 13B is where Relaytic turns the existing runtime event stream and hook audit from a mostly internal trace aid into a first-class product substrate.

This slice should also make permission posture legible. Humans and external agents should always know what Relaytic may do on its own, what requires approval, and what is blocked entirely.

This slice must continue obeying:

- `docs/specs/workspace_lifecycle.md`
- `docs/specs/mission_control_flows.md`
- `docs/specs/external_agent_continuation_contract.md`
- `docs/specs/test_and_proof_matrix.md`

## Load-Bearing Improvement

- Relaytic should expose a canonical event bus plus visible permission modes so later daemon, remote-control, and richer UI work can subscribe to one truthful runtime and one explicit authority model instead of reconstructing state from artifacts after the fact

## Human Surface

- humans should be able to see the current permission mode, pending approvals, recent event timeline, and which tools or actions are allowed, approval-gated, or denied

## Agent Surface

- external agents should be able to query one session capability contract, one permission-mode artifact, and one machine-readable event/hook registry without inferring authority from prose or trial-and-error tool calls

## Intelligence Source

- the shared runtime gateway, control contracts, capability profiles, workspace continuity state, and explicit operator/agent policy overlays

## Fallback Rule

- when subscriptions or richer hook handlers are unavailable, Relaytic must still emit the canonical event stream and permission decisions through stable artifacts rather than silently degrading into hidden local state

## Required Behavior

- Slice 13B must upgrade the existing `lab_event_stream.jsonl`, `hook_execution_log.json`, and `capability_profiles.json` rather than replacing them with a second incompatible runtime history
- event emission must cover at least:
  - session start/end
  - prompt submit
  - tool pre-use/post-use
  - stage start/complete
  - background job start/complete
  - workspace resume
  - compaction start/complete
  - approval requested/approved/denied
- permission modes must be explicit and user-visible, with at least:
  - review
  - plan
  - safe_execute
  - bounded_autonomy
- permission posture must not be hidden in policy files alone; mission control, CLI, MCP, and later remote surfaces must expose the same current mode and the same tool/action matrix
- hooks must be typed and replayable, not arbitrary callback side effects
- control decisions, approval requests, and denied actions must be recorded in one permission-decision log rather than scattered across unrelated artifacts
- later daemon and remote-control slices must consume this event and permission substrate rather than inventing independent activity feeds or approval logic

## Proof Obligation

- Relaytic must prove that runtime authority is explicit, inspectable, and surface-consistent instead of being implied by which host or CLI entrypoint happened to start the session

## Acceptance Criteria

Slice 13B is acceptable only if:

1. one action that is allowed in `bounded_autonomy` is blocked or approval-gated in `review`
2. one event-driven hook subscriber reacts to a real runtime event without changing the canonical source of truth
3. one CLI and one MCP surface report the same permission mode and pending-approval posture
4. one denied or approval-gated action is replayable from the event and permission logs alone

## Required Verification

Slice 13B should not be considered complete without targeted tests that cover at least:

- one event emission and subscription case
- one hook dispatch case
- one permission-mode transition case
- one denied-action or approval-gated case
- one CLI-versus-MCP parity case
- one regression guard against hidden authority drift

## Implementation Notes

Shipped public surfaces:

- `relaytic events show`
- `relaytic permissions show`
- `relaytic permissions check`
- `relaytic permissions decide`
- MCP parity through:
  - `relaytic_show_event_bus`
  - `relaytic_show_permissions`
  - `relaytic_check_permission`
  - `relaytic_decide_permission`

Shipped artifact set:

- `event_schema.json`
- `event_subscription_registry.json`
- `hook_registry.json`
- `hook_dispatch_report.json`
- `permission_mode.json`
- `tool_permission_matrix.json`
- `approval_policy_report.json`
- `permission_decision_log.jsonl`
- `session_capability_contract.json`
