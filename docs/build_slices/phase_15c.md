# Slice 15C - Budgeted HPO, early stopping, and deeper portfolio loops

## Status

Planned.

Delivered package boundaries:

- extend `src/relaytic/modeling/`
- extend `src/relaytic/search/`
- extend `src/relaytic/profiles/`
- extend `src/relaytic/workspace/`

Intended artifacts:

- `hpo_budget_contract.json`
- `architecture_search_space.json`
- `trial_ledger.jsonl`
- `early_stopping_report.json`
- `search_loop_scorecard.json`
- `warm_start_transfer_report.json`
- `threshold_tuning_report.json`

## Intent

Slice 15C replaces shallow fixed-variant search with explicit budgeted optimization loops.

The current state uses a few hard-coded variants per family. That is useful as a deterministic floor, but it is not good enough for stronger benchmark performance.

## Load-Bearing Improvement

- Relaytic should spend training budget deliberately through explicit search spaces, trial budgets, early stopping, and warm starts instead of pretending a three-variant family sweep is real HPO

## Human Surface

- operators should be able to inspect how much search budget was allocated, what search space was explored, why Relaytic stopped, and whether tuning was worth the spent time

## Agent Surface

- external agents should be able to inspect HPO contracts, search spaces, trial ledgers, and stop reasons without reading raw logs

## Required Behavior

- Relaytic must wire a real HPO backend instead of leaving the optimizer contract as a stub
- every model family must define an explicit bounded search space
- search budgets must include:
  - maximum trials
  - maximum wall-clock time
  - per-family trial caps
  - early-stopping conditions
  - warm-start eligibility
- threshold tuning and calibration tuning must be first-class for classification and rare-event tasks
- search depth must be allowed to widen through multiple loops when the value-of-search controller says it is worth it
- search must be replayable and seeded
- Relaytic must persist why it stopped:
  - budget exhausted
  - convergence plateau
  - no value in more search
  - protocol or data issue blocked further search

## Acceptance Criteria

Slice 15C is acceptable only if:

1. one family uses a real search space instead of a fixed three-variant sweep
2. one classification route tunes threshold and calibration as part of the bounded search
3. one search loop stops because of explicit plateau or budget logic rather than arbitrary fixed exhaustion
4. one rerun can warm-start from a prior successful family search state

## Required Verification

- one HPO budget test
- one early-stopping test
- one warm-start test
- one threshold-tuning test
