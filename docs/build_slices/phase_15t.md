# Slice 15T - Business-value metrics and analyst-hour proof

## Status

Planned.

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

## Acceptance Criteria

1. One regression shows AUROC can improve while operational utility worsens.
2. Relaytic refuses to overclaim when review-capacity metrics disagree with model-score metrics.
3. Imported-incumbent comparison includes analyst-capacity tradeoffs.

## Required Verification

- business-value metric unit tests
- operational guard CLI regression
- incumbent review-budget comparison regression

