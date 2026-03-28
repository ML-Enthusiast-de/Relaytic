# Slice 12 - Dojo mode and guarded self-improvement

## Status

Implemented.

Implemented package boundaries:

- `src/relaytic/dojo/`
- extended `src/relaytic/ui/`
- extended `src/relaytic/runs/`
- extended `src/relaytic/mission_control/`
- extended `src/relaytic/interoperability/`

Implemented artifacts:

- `dojo_session.json`
- `dojo_hypotheses.json`
- `dojo_results.json`
- `dojo_promotions.json`
- `architecture_proposals.json`

Implemented public surfaces:

- `relaytic dojo review`
- `relaytic dojo show`
- `relaytic dojo rollback`
- `relaytic_show_dojo`
- `relaytic_review_dojo`

## Intent

Slice 12 is where Relaytic improves itself like a lab rather than mutating like an unstable agent demo.

The slice is successful only if Relaytic can:

- propose changes to priors, challenger design, controller heuristics, and method-compiler behavior
- validate those proposals under quarantine against benchmark cases, the visible quality-gate proxy, and incumbent behavior
- promote or reject proposals with explicit evidence and rollback support
- keep self-improvement separate from the authoritative product behavior until validation passes

## Load-Bearing Improvement

- Relaytic should be able to improve route priors, controller heuristics, challenger design, and method-compilation behavior under hard quarantine and validation gates instead of freezing all learning outside manual code edits

## Human Surface

- humans should be able to inspect which self-improvement proposals targeted route search, controller logic, method compilation, or benchmark behavior and why each proposal was promoted, rejected, or rolled back

## Agent Surface

- external agents should be able to consume dojo proposals, validation outcomes, promotion ledgers, and rollback state as explicit artifacts rather than inferring them from branch history

## Intelligence Source

- benchmark gaps, validated feedback, outcome evidence, trace/eval artifacts, prior failure cases, gold decision cases, and quarantined experimental proposals

## Fallback Rule

- if dojo validation data or benchmark proof is unavailable, current incumbent behavior remains authoritative and dojo outputs stay quarantined

## Required Behavior

- dojo outputs must remain quarantined until they beat the incumbent on benchmark and pass the visible quality-gate proxy used by the current implementation
- no dojo promotion may become default behavior without an explicit promotion artifact
- dojo must improve strategies, priors, challenger design, route search, decision-world-model heuristics, and method-compilation logic before it is allowed to touch deeper architecture proposals
- dojo must not weaken intervention contracts, override skepticism, trace integrity, or agent-security guarantees without explicit regression evidence
- every dojo promotion must preserve rollback, provenance, and benchmark comparability
- dojo proposals, promotions, rejections, and rollbacks must extend the mission-control surface introduced in Slice 11B and expanded through Slices 11C, 11D, 11E, 11F, and 11G instead of remaining CLI-only state
- early architecture proposals remain explicitly quarantined and non-authoritative even when method-level dojo proposals can be promoted
- current promoted dojo changes are advisory and ledgered; Slice 12 does not silently mutate authoritative runtime defaults outside the explicit promotion surface

## Proof Obligation

- Relaytic must prove that dojo can improve itself without hidden drift, that failed proposals stay quarantined, and that promoted proposals preserve the control and security guarantees already earned

## Acceptance Criteria

Slice 12 is acceptable only if:

1. one dojo proposal is rejected with clear reasons
2. one dojo proposal is promoted only after beating the incumbent on required validations
3. one previously promoted dojo artifact is rolled back cleanly
4. one promoted dojo change preserves skeptical-control and security-eval guarantees rather than only improving score

## Required Verification

Slice 12 should not be considered complete without targeted tests that cover at least:

- one quarantine-only proposal case
- one promotion case
- one rollback case
- one benchmark-regression gate
- one control/security-regression gate
