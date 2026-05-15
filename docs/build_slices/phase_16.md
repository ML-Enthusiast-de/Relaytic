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

It should start only after the full performance-recovery track in Slices 15A through 15M, the AML foundation track in Slices 15N through 15Q, the AML proof alignment in Slice 15R-A, the flagship demo packaging in Slice 15S, the business-value guard in Slice 15T, and the remaining AML productization plus paper-freeze track in Slices 15U through 15Z-R have landed.

This is not a single coding pass. It is a governed program delivered through:

- Slice 16A capability registry and capability cards
- Slice 16B offline replay packs and shadow mode
- Slice 16C arena evaluation and promotion scorecards
- Slice 16D hunt campaigns, seeded exploration, and provider feedback
- Slice 16E non-core specialist recruitment and retirement
- Slice 16F academy mission control and explainability surfaces

The academy is intentionally not the next move anymore.
Relaytic first needs to become genuinely interesting as **Relaytic-AML**, with domain contracts, graph-aware reasoning, analyst-review optimization, streaming AML posture, and hard AML proof packs.
After Slice 15Z-R, academy work must treat the frozen relevant benchmark catalog as a target and guardrail: new capabilities can attack benchmark gaps, but they must not redefine the benchmark story or bypass paper-claim gates.

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
- Slice 16 must consume frozen benchmark gaps and claim boundaries from Slice 15Z-R when capability candidates are justified by public benchmark relevance

## Proof Obligation

- Relaytic must prove that academy growth increases search power and specialization depth without weakening authority, auditability, or rollback safety
- Relaytic must also prove that academy growth improves or honestly fails against the frozen benchmark catalog rather than inventing easier post-hoc proof tasks

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
