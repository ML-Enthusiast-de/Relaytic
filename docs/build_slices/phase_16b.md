# Slice 16B - Offline replay packs and shadow mode

## Status

Planned.

Intended package boundaries:

- `src/relaytic/capability_academy/`
- extend `src/relaytic/evals/`
- extend `src/relaytic/tracing/`
- extend `src/relaytic/runtime/`

Intended artifacts:

- `offline_replay_scorecard.json`
- `replay_trace_index.json`
- `capability_failure_taxonomy.json`
- `shadow_trial_report.json`
- `shadow_disagreement_log.jsonl`
- `shadow_counterfactual_win_report.json`
- `shadow_budget_report.json`

## Intent

Slice 16B gives Relaytic the safe proving ground for new capabilities.

## Load-Bearing Improvement

- Relaytic should be able to evaluate candidate tools or non-core specialists on replayable runs and in live-like shadow mode without letting them change production truth

## Human Surface

- humans should be able to see whether a candidate would have helped, hurt, disagreed, or violated constraints before it gets live authority

## Agent Surface

- external agents should be able to launch replay packs and shadow trials, then consume the disagreement and counterfactual win reports through stable JSON-first surfaces

## Intelligence Source

- historical runs, benchmark packs, shadow disagreements, trace spans, cost envelopes, and constraint or permission outcomes

## Fallback Rule

- when replay packs are unavailable, Relaytic must block promotion and keep the candidate at intake or candidate state rather than skipping directly to live trial

## Required Behavior

- replay mode must be non-authoritative
- shadow mode must be non-authoritative
- shadow mode must record what changed and what would have changed
- replay and shadow must record cost, latency, safety, and feasibility impact in addition to task metrics
- shadow execution must be seeded and replayable

## Acceptance Criteria

Slice 16B is acceptable only if:

1. one candidate runs on a replay pack and produces a comparable scorecard
2. one candidate runs in shadow on a live-like path without altering the authoritative output
3. one candidate shows a measurable counterfactual win
4. one candidate is blocked from advancing because replay or shadow evidence is weak

## Required Verification

- one replay-scorecard test
- one shadow-non-authority regression guard
- one disagreement-log test
- one weak-candidate non-advancement test
