# Slice 16A - Capability registry and capability cards

## Status

Planned.

Intended package boundaries:

- `src/relaytic/capability_academy/`
- extend `src/relaytic/workspace/`
- extend `src/relaytic/interoperability/`

Intended artifacts:

- `capability_registry.json`
- `capability_card_log.jsonl`
- `capability_intake_record.json`
- `capability_risk_profile.json`
- `academy_policy_report.json`
- `core_agent_roster.json`
- `non_core_specialist_registry.json`

## Intent

Slice 16A gives Relaytic one canonical registry for candidate and promoted tools or non-core specialists.

It should begin only after the AML pivot slices have made Relaytic's flagship domain thesis real enough that future capability growth has a clear target.

## Load-Bearing Improvement

- Relaytic should be able to represent capabilities explicitly as typed cards with lifecycle state, risk, owner, domain fit, and proof posture instead of scattering those judgments across ad hoc notes or code branches

## Human Surface

- humans should be able to inspect what a capability is, why it exists, whether it is core or non-core, what permissions it needs, and where it currently sits in the academy lifecycle

## Agent Surface

- external agents should be able to submit capability candidates and read the same capability cards through stable JSON-first surfaces

## Intelligence Source

- current workspace gaps, benchmark debt, pulse innovation watch, search/controller blind spots, and external-agent proposals

## Fallback Rule

- when no academy registry exists, Relaytic must continue using only the shipped static capability set and emit an explicit `academy_unavailable` posture instead of inferring candidate state

## Required Behavior

- capability cards must distinguish `tool` and `specialist_agent`
- capability cards must distinguish `core` and `non_core`
- core agents must be immutable from this subsystem
- cards must expose lifecycle state, permissions, intended task families, risk level, and current proof status
- all candidate intake must leave an audit trail

## Acceptance Criteria

Slice 16A is acceptable only if:

1. one tool candidate can be registered with a full capability card
2. one non-core specialist candidate can be registered without affecting the core roster
3. one attempt to mark a core agent as removable is explicitly rejected
4. CLI and MCP expose the same registry truth

## Required Verification

- one tool-card schema test
- one non-core specialist-card schema test
- one core-agent immutability regression test
- one CLI registry test
- one MCP registry test
