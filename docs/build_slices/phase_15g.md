# Slice 15G - Objective contracts, split correctness, and metric-truth alignment

## Status

Implemented.

Delivered package boundaries:

- extend `src/relaytic/analytics/`
- extend `src/relaytic/planning/`
- extend `src/relaytic/benchmark/`
- extend `src/relaytic/decision/`
- extend `src/relaytic/runs/`
- extend `src/relaytic/assist/`
- extend `tests/`

Intended artifacts:

- `optimization_objective_contract.json`
- `objective_alignment_report.json`
- `split_diagnostics_report.json`
- `temporal_fold_health.json`
- `metric_materialization_audit.json`
- `benchmark_truth_precheck.json`

## Intent

Slice 15G fixes the most dangerous remaining competitiveness failure: Relaytic can still compare, optimize, threshold, and explain using partially different objective assumptions, and temporal benchmarks can still produce degenerate folds or mismatched metrics.

This slice makes objective truth and split truth canonical before we spend more budget on stronger families or deeper search.

## Load-Bearing Improvement

- Relaytic should decide once what it is optimizing, how the split is validated, which metric ranks families, which metric chooses thresholds, which metric is used for benchmark claims, and whether the benchmark is safe to trust at all

## Human Surface

- operators should be able to inspect one explicit objective contract, one split-health report, and one clear answer to why a benchmark result is or is not trustworthy

## Agent Surface

- external agents should be able to consume metric and split truth through stable artifacts rather than inferring intent from mixed reports

## Required Behavior

- Relaytic must write one canonical optimization-objective contract before family racing begins
- the contract must distinguish family-selection, calibration, threshold, benchmark, and deployment objectives explicitly
- temporal classification splits must preserve positive events in validation and test or fail closed with an explicit reason
- benchmark rows must not claim a comparison metric that was not materialized
- assist, run summary, benchmark show, and MCP surfaces must explain the same objective contract

## Acceptance Criteria

Slice 15G is acceptable only if:

1. one benchmark run shows aligned family-selection, calibration, threshold, benchmark, and deployment metrics from one contract
2. one temporal classification dataset avoids zero-positive validation and test folds or is blocked explicitly
3. one benchmark bundle fails closed because its comparison metric is unavailable instead of emitting a misleading ranking
4. one explanation flow answers why Relaytic optimized one metric but reported another without contradiction

## Required Verification

- one optimization-contract schema test
- one split-health regression test for temporal classification
- one benchmark metric-materialization consistency test
- one assist explanation test for objective alignment
