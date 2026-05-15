# Slice 15W - Temporal and weak-label upgrade

## Status

Planned.

## Intent

Slice 15W improves production-shaped AML time and label handling.

This slice must make time-aware benchmark claims defensible under forward-only evaluation, not merely under randomly shuffled supervised splits.

## Load-Bearing Improvement

- Relaytic-AML evaluates delayed-label windows, positive-unlabeled posture, threshold stability, and recalibration choices under ordered data.
- PaySim-style `step` fields, Elliptic-style `time_step` fields, and later AMLSim or subgraph time windows must all flow into the same temporal claim discipline.

## Human Surface

- operators can see whether Relaytic recommends retraining, recalibration, threshold reset, or more delayed-outcome observation.

## Agent Surface

- external agents can consume time-window scorecards and weak-label guards without reinterpreting raw rows.

## Intelligence Source

- temporal engine
- stream-risk posture
- weak-label posture
- delayed-outcome alignment
- rolling alert-quality reports
- threshold-search artifacts

## Fallback Rule

- if timestamp or delayed-label evidence is missing, Relaytic blocks temporal claims and emits required-data recommendations.

## Required Outputs

- `aml_delayed_label_eval_report.json`
- `aml_positive_unlabeled_posture.json`
- `aml_threshold_drift_report.json`
- `aml_time_window_scorecard.json`
- `aml_temporal_benchmark_claim_report.json`

## Acceptance Criteria

1. One ordered workload produces a threshold-drift decision.
2. One delayed-label scenario blocks overconfident public claims.
3. Sequence-native candidates remain shadow-only unless they beat strong lagged tabular baselines.
4. Time-sliced metrics are reported separately from aggregate metrics, and public temporal claims are blocked when future leakage, zero-positive future folds, or missing delayed-outcome evidence remain unresolved.
5. One PaySim-style or Elliptic-style ordered workload produces a forward-evaluation artifact suitable for the later paper benchmark freeze.

## Required Verification

- delayed-label window tests
- threshold-drift report regression
- public-claim block regression
- temporal benchmark claim regression
