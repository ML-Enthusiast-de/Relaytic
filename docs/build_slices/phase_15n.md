# Slice 15N - AML domain contract and flagship pivot

## Status

Planned.

## Intent

Slice 15N is the wedge-setting slice.

It freezes the flagship domain pivot from a broad structured-data platform into **Relaytic-AML**, the AML and financial-crime frontier edition of Relaytic.

This slice does not yet implement graph mining or streaming detection. It establishes the domain truth the later AML slices must obey.

## Load-Bearing Improvement

- Relaytic should gain one canonical AML domain contract with explicit case ontology, analyst-review budget semantics, and AML-safe benchmark doctrine instead of treating fraud or AML as only one more generic rare-event task family

## Human Surface

- operators should be able to see that Relaytic-AML optimizes for alert quality, review burden, and case usefulness rather than raw leaderboard score only

## Agent Surface

- external agents should be able to consume one typed AML domain contract and one review-budget contract through stable JSON artifacts instead of inferring the domain posture from free-form text

## Intelligence Source

- deterministic domain contracts
- deterministic risk taxonomy
- benchmark doctrine and review-budget logic
- optional local semantic help only for ontology mapping, never as the authority path

## Intended Artifacts

- `aml_domain_contract.json`
- `aml_case_ontology.json`
- `aml_review_budget_contract.json`
- `aml_claim_scope.json`

## Acceptance Criteria

1. one AML/fraud run can persist an explicit AML domain contract without reusing generic rare-event defaults blindly
2. one review-budget-aware decision surface changes next-step reasoning compared with a metric-only posture
3. one benchmark bundle records AML pack scope explicitly

## Required Verification

- one AML domain-contract schema test
- one review-budget contract test
- one CLI or assist explanation test proving AML posture is visible
