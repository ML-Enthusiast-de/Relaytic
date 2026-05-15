# Slice 15T - Business-value metrics and analyst-hour proof

## Status

Implemented.

## Intent

Slice 15T makes analyst capacity and business value first-class Relaytic-AML evaluation criteria.

## Load-Bearing Improvement

- Relaytic-AML reports analyst-hours saved, false-positive reduction at fixed recall, recall at review capacity, precision at top-k, and case-packet completeness.

## Human Surface

- operators can see whether Relaytic improved the review queue, not only the predictive score.

## Agent Surface

- external agents can consume a stable business-value report and detect when a higher model score fails operational utility.

## Intelligence Source

- review-budget contracts
- threshold search
- casework scorecards
- operating-point contracts
- incumbent comparisons

## Fallback Rule

- if analyst-hour assumptions are missing, Relaytic uses conservative defaults, labels them as assumptions, and blocks hard business-value claims.

## Required Outputs

- `aml_business_value_report.json`
- `analyst_hour_savings_report.json`
- `review_capacity_metric_report.json`
- `operational_metric_guard.json`

## Implemented Notes

- `relaytic aml business-value --run-dir <run_dir>` builds the four Slice 15T artifacts from existing AML casework, operating-point, benchmark, and incumbent artifacts.
- Benchmark runs now materialize the same business-value reports automatically, and `relaytic benchmark show`, `relaytic assist turn`, `relaytic mission-control show`, and the 15S demo bundle surface the guarded operational posture.
- The operational metric guard blocks hard business-value claims when analyst-hour assumptions are defaulted, case packets are incomplete, false-positive reduction is not positive, or model-score wins disagree with review-capacity utility.

## Acceptance Criteria

1. One regression shows AUROC can improve while operational utility worsens.
2. Relaytic refuses to overclaim when review-capacity metrics disagree with model-score metrics.
3. Imported-incumbent comparison includes analyst-capacity tradeoffs.

## Required Verification

- business-value metric unit tests
- operational guard CLI regression
- incumbent review-budget comparison regression
