# Slice 16C - Arena evaluation and promotion scorecards

## Status

Planned.

Intended package boundaries:

- `src/relaytic/capability_academy/`
- extend `src/relaytic/evals/`
- extend `src/relaytic/permissions/`
- extend `src/relaytic/tracing/`

Intended artifacts:

- `capability_arena_scorecard.json`
- `promotion_candidate_ranking.json`
- `arena_judge_report.json`
- `promotion_decision_report.json`
- `capability_registry_update.json`
- `trial_scope_contract.json`
- `trial_rollback_checkpoint.json`

## Intent

Slice 16C turns replay and shadow evidence into deterministic promotion or quarantine decisions.

## Load-Bearing Improvement

- Relaytic should be able to compare candidates against incumbents through one deterministic arena and promote only when multi-axis evidence says they are worth the added complexity

## Human Surface

- humans should be able to inspect why a candidate won, why another candidate lost, and what evidence blocked promotion

## Agent Surface

- external agents should be able to consume one ranking and one promotion decision report without screen-scraping or reading long prose

## Intelligence Source

- replay packs, shadow trials, cost and safety budgets, feasibility outcomes, transfer evidence, and deterministic scorecards

## Fallback Rule

- when arena comparison cannot be run, Relaytic must quarantine the candidate and emit an incomplete-proof posture rather than guessing

## Required Behavior

- promotion decisions must be deterministic and scorecard-backed
- one candidate must not self-certify its own promotion
- arena scoring must include performance, cost, safety, feasibility, transfer, and explanation quality
- narrow live trials must remain rollbackable and scope-limited

## Acceptance Criteria

Slice 16C is acceptable only if:

1. one candidate is promoted through an explicit arena win
2. one higher-scoring-on-metric candidate still loses because safety, feasibility, or transfer evidence is worse
3. one candidate enters a narrow live trial with explicit rollback
4. one candidate is quarantined despite promise because the arena proof is incomplete

## Required Verification

- one promotion-scorecard test
- one metric-win-but-no-promotion test
- one rollback-scope test
- one quarantine-on-incomplete-proof test
