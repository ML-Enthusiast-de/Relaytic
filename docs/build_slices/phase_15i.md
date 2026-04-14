# Slice 15I - Portfolio search engine and serious budget doctrine

## Status

Shipped.

Delivered package boundaries:

- extend `src/relaytic/search/`
- extend `src/relaytic/modeling/`
- extend `src/relaytic/planning/`
- extend `src/relaytic/memory/`
- extend `src/relaytic/runs/`
- extend `tests/`

Intended artifacts:

- `search_budget_envelope.json`
- `probe_stage_report.json`
- `family_race_report.json`
- `finalist_search_plan.json`
- `multi_fidelity_pruning_report.json`
- `portfolio_search_scorecard.json`
- `search_stop_reason.json`

## Intent

Slice 15I fixes the remaining shallow-search ceiling.

The goal is not simply "more loops." The goal is to make Relaytic spend search budget in the right order:

1. probe many eligible families cheaply
2. race the plausible families honestly
3. deepen only the finalists
4. spend separate budget on calibration and threshold work

## Load-Bearing Improvement

- Relaytic should allocate serious, profile-aware, dataset-aware search budgets that are deep enough to matter and explicit enough to audit

## Human Surface

- operators should be able to inspect the active budget envelope, how much search was spent at each stage, what deeper search was skipped, and why search stopped

## Agent Surface

- external agents should be able to consume staged search outcomes, pruning reasons, finalist plans, and stop reasons through stable JSON artifacts

## Required Behavior

- portfolio search must have distinct probe, race, finalist, and post-fit decision stages
- default operator and benchmark profiles must not collapse to tiny fixed loops purely because tests need to run quickly
- test profiles must be explicitly separate and visibly smaller
- Relaytic must persist why a family was pruned, promoted to finalist, or stopped
- warm starts may influence search, but must not silently replace stage evidence
- search stopping must record whether it stopped for budget, plateau, dominance, or infeasible remaining value

## Acceptance Criteria

Slice 15I is acceptable only if:

1. one benchmark profile gives multiple materially different families non-trivial probe budgets before finalist selection
2. one finalist receives deeper follow-up budget than losing families under the same run
3. one low-budget profile still runs a staged search and reports which deeper work was skipped
4. one test profile can shrink budgets without mutating the default operator or benchmark profile contracts

## Required Verification

- one staged-search regression test
- one budget-profile separation test
- one pruning-reason test
- one warm-start transparency test
