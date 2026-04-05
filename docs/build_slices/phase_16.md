# Slice 16 - Relaytic Academy, governed capability evolution, and shadow-tested growth

## Status

Planned.

Intended package boundaries:

- `src/relaytic/capability_academy/`
- extend `src/relaytic/daemon/`
- extend `src/relaytic/evals/`
- extend `src/relaytic/mission_control/`
- extend `src/relaytic/tracing/`
- extend `src/relaytic/interoperability/`

## Intent

Slice 16 is the future umbrella track where Relaytic learns new non-core capabilities without turning into an uncontrolled self-modifying system.

This is not a single coding pass. It is a governed program delivered through:

- Slice 16A capability registry and capability cards
- Slice 16B offline replay packs and shadow mode
- Slice 16C arena evaluation and promotion scorecards
- Slice 16D hunt campaigns, seeded exploration, and provider feedback
- Slice 16E non-core specialist recruitment and retirement
- Slice 16F academy mission control and explainability surfaces

This slice family must continue obeying:

- `docs/specs/capability_academy_contract.md`
- `docs/specs/workspace_lifecycle.md`
- `docs/specs/result_contract_schema.md`
- `docs/specs/mission_control_flows.md`
- `docs/specs/test_and_proof_matrix.md`

## Load-Bearing Improvement

- Relaytic should be able to discover, trial, evaluate, promote, demote, and retire new tools and non-core specialist agents through a shadow-tested, audit-backed academy instead of relying only on fixed manually-coded capability growth

## Human Surface

- humans should be able to inspect candidate capabilities, shadow-trial outcomes, promotion decisions, hunt campaigns, retirement reasons, and academy safety posture from one coherent control surface

## Agent Surface

- external agents should be able to propose new capabilities, run replay or shadow evaluations, review promotion scorecards, and inspect academy state through stable JSON-first surfaces instead of prompt-only negotiation

## Intelligence Source

- pulse watchlists, search-controller gaps, benchmark debt, workspace memory, external-agent proposals, seeded exploration, offline replay packs, shadow disagreement data, and deterministic promotion scorecards

## Fallback Rule

- when the academy is disabled, Relaytic must continue using only the currently promoted static capability set and should not silently trial or route candidate tools or non-core specialists

## Required Behavior

- Slice 16 must keep core agents immutable and non-deletable
- Slice 16 must treat new tools and non-core specialists as candidates that move through explicit lifecycle states rather than silently becoming available
- Slice 16 must require offline replay and shadow proof before any candidate receives live authority
- Slice 16 must keep all exploration seeded, budgeted, and replayable
- Slice 16 must record provider feedback on both successful and failed candidates
- Slice 16 must integrate with the same permission, daemon, trace, and remote-supervision truth already used elsewhere in Relaytic

## Proof Obligation

- Relaytic must prove that academy growth increases search power and specialization depth without weakening authority, auditability, or rollback safety

## Acceptance Criteria

Slice 16 is acceptable only if:

1. one candidate capability progresses from intake to shadow mode without changing production truth
2. one candidate is promoted through explicit replay, shadow, and arena evidence
3. one candidate is quarantined or retired despite promise because safety, policy, or transfer proof fails
4. one non-core specialist can be recruited or retired without affecting core-agent integrity
5. one seeded hunt campaign can be replayed exactly

## Required Verification

Slice 16 should not be considered complete without targeted tests that cover at least:

- one replay-only candidate path
- one shadow-mode non-authority proof case
- one arena-promotion case
- one quarantine or retirement case
- one no-core-deletion guard
- one seeded-hunt replay case

Slice 16 should be treated as complete only when Slices 16A through 16F are complete.
