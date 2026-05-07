# Slice 15W - Temporal and weak-label upgrade

## Status

Planned.

## Intent

Slice 15W improves production-shaped AML time and label handling.

## Load-Bearing Improvement

- Relaytic-AML evaluates delayed-label windows, positive-unlabeled posture, threshold stability, and recalibration choices under ordered data.

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

## Acceptance Criteria

1. One ordered workload produces a threshold-drift decision.
2. One delayed-label scenario blocks overconfident public claims.
3. Sequence-native candidates remain shadow-only unless they beat strong lagged tabular baselines.

## Required Verification

- delayed-label window tests
- threshold-drift report regression
- public-claim block regression

