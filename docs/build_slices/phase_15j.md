# Slice 15J - Temporal engine and time-aware competitiveness

## Status

Shipped.

Delivered package boundaries:

- extend `src/relaytic/analytics/`
- extend `src/relaytic/modeling/`
- extend `src/relaytic/benchmark/`
- extend `src/relaytic/decision/`
- extend `src/relaytic/runs/`
- extend `tests/`

Intended artifacts:

- `temporal_structure_report.json`
- `temporal_feature_ladder.json`
- `rolling_cv_plan.json`
- `temporal_split_guard_report.json`
- `sequence_shadow_scorecard.json`
- `temporal_baseline_ladder.json`
- `temporal_metric_contract.json`

## Intent

Slice 15J makes time-aware data a first-class modeling problem instead of a timestamp-aware variant of the tabular path.

This slice should recover temporal credibility for sensor, occupancy, maintenance, and energy-style datasets.

## Load-Bearing Improvement

- Relaytic should be able to detect real temporal structure, build stronger temporal baselines, preserve temporal event integrity in evaluation, and test sequence candidates honestly against strong lagged baselines

## Human Surface

- operators should be able to inspect whether Relaytic judged the data as truly temporal, what temporal feature ladder it built, how rolling evaluation was configured, and why a sequence candidate did or did not advance

## Agent Surface

- external agents should be able to consume temporal structure, split-health, feature-ladder, and sequence-shadow artifacts through stable JSON outputs

## Required Behavior

- Relaytic must distinguish incidental timestamps from real ordered temporal structure
- temporal classification and rare-event benchmarks must use split logic that preserves positive events or fail closed
- temporal feature generation must include vectorized lag, rolling, delta, and seasonality-style features where appropriate
- lagged baseline families must be strong enough to act as honest sequence challengers
- sequence families must remain replay-first or shadow-first until they beat strong lagged baselines under explicit proof
- temporal benchmark comparison metrics must be fully materialized in the benchmark rows

## Acceptance Criteria

Slice 15J is acceptable only if:

1. one occupancy-style temporal classification benchmark retains positives in validation and test or is blocked explicitly
2. one temporal regression benchmark materializes its claimed comparison metric correctly
3. one temporal dataset shows a lagged baseline beating a naive non-temporal baseline
4. one sequence candidate is compared against a strong lagged baseline and remains shadow-only when it loses

## Required Verification

- one temporal-structure detection test
- one temporal split-health regression test
- one temporal metric-materialization test
- one sequence-shadow comparison test
