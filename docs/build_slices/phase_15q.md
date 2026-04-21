# Slice 15Q - Streaming drift, weak labels, and continual AML learning

## Status

Planned.

## Intent

Slice 15Q turns Relaytic-AML into a serious temporal risk system.

It should handle delayed feedback, weak labels, streaming posture, and recalibration under drift instead of assuming static supervised tables.

## Load-Bearing Improvement

- Relaytic-AML should be able to reason about streaming risk, delayed outcomes, weak labels, and recalibration triggers with explicit artifacts and bounded adaptation logic

## Human Surface

- operators should be able to see whether drift or label delay is the reason for recalibration, retraining, or threshold changes

## Agent Surface

- external agents should be able to inspect stream posture, weak-label posture, and recalibration triggers without re-deriving them

## Intelligence Source

- deterministic drift diagnostics
- temporal performance tracking
- explicit weak-label contracts
- bounded continual-learning and recalibration policies

## Intended Artifacts

- `stream_risk_posture.json`
- `weak_label_posture.json`
- `delayed_outcome_alignment.json`
- `drift_recalibration_trigger.json`
- `rolling_alert_quality_report.json`

## Acceptance Criteria

1. one AML temporal task persists a weak-label or delayed-outcome contract explicitly
2. one drift trigger changes recalibration or threshold posture visibly
3. one streaming or rolling evaluation path stays audit-safe and benchmark-safe

## Required Verification

- one weak-label posture test
- one drift-trigger regression test
- one rolling temporal AML evaluation test
