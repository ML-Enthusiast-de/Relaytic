# Slice 15K - Calibration, thresholds, and decision optimization

## Status

Shipped.

Delivered package boundaries:

- extend `src/relaytic/modeling/`
- extend `src/relaytic/decision/`
- extend `src/relaytic/benchmark/`
- extend `src/relaytic/runs/`
- extend `src/relaytic/assist/`
- extend `tests/`

Intended artifacts:

- `calibration_strategy_report.json`
- `operating_point_contract.json`
- `threshold_search_report.json`
- `decision_cost_profile.json`
- `review_budget_optimization_report.json`
- `abstention_policy_report.json`

## Intent

Slice 15K turns calibration and operating-point choice into first-class performance work.

This is where Relaytic should start winning on the decisions that matter in review-queue, risk, fraud, churn, and abstention-sensitive workflows.

## Load-Bearing Improvement

- Relaytic should be able to improve real downstream decision quality through evidence-based calibration, threshold search, abstention posture, and review-budget optimization instead of treating those as minor post-processing

## Human Surface

- operators should be able to inspect which calibration strategy won, which threshold or operating point Relaytic chose, what review budget assumptions were applied, and why a rerun was not the better next move

## Agent Surface

- external agents should be able to consume calibration and operating-point artifacts directly and ask why Relaytic chose one threshold or abstention posture over another

## Required Behavior

- Relaytic must support multiple calibration strategies and select among them explicitly
- threshold search must be objective-family aware instead of one generic metric sweep
- rare-event and review-queue tasks must be able to optimize for review capacity and downstream cost, not only score metrics
- abstention or operator-review posture must become an explicit candidate when the decision profile justifies it
- run summary, assist, and benchmark surfaces must explain the chosen operating point from the same canonical contract

## Acceptance Criteria

Slice 15K is acceptable only if:

1. one rare-event task improves decision posture through threshold or calibration choice without changing the winning family
2. one calibration strategy wins for explicit evidence-based reasons instead of fixed defaults
3. one review-budget-aware operating point differs from the best raw-score threshold
4. one explanation surface can answer why Relaytic chose this threshold and why not a rerun instead

## Required Verification

- one calibration-strategy selection test
- one threshold-search regression test
- one review-budget optimization test
- one assist explanation test for operating-point choice
