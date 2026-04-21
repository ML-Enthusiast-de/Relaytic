# Slice 15P - Analyst review optimization and casework

## Status

Planned.

## Intent

Slice 15P makes analyst economics first-class.

Relaytic-AML should optimize not only for suspiciousness but for which alerts deserve scarce investigation time.

## Load-Bearing Improvement

- Relaytic-AML should be able to rank alerts and cases under explicit review budgets, emit case packets, and compare operating points by analyst burden instead of by model score only

## Human Surface

- operators should be able to ask what changed the queue, why one case is above another, and how many alerts a team can safely review under the current policy

## Agent Surface

- external agents should be able to inspect queue policy, case-packet evidence, and analyst-scorecard metrics through JSON-first outputs

## Intelligence Source

- deterministic review-budget logic
- cost-aware operating-point optimization
- case-packet synthesis from existing evidence
- optional semantic help only for summary wording, not ranking authority

## Intended Artifacts

- `alert_queue_policy.json`
- `alert_queue_rankings.json`
- `analyst_review_scorecard.json`
- `case_packet.json`
- `review_capacity_sensitivity.json`

## Acceptance Criteria

1. one AML run can produce a top-k or review-budget-aware ranking instead of only a flat score file
2. one case packet surfaces enough evidence for a human review handoff
3. one operating-point change can be justified by analyst burden, not just model fit

## Required Verification

- one review-budget ranking test
- one case-packet generation test
- one burden-aware operating-point regression test
