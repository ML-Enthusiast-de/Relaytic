# Slice 15U - Strong AML baselines and ablations

## Status

Planned.

## Intent

Slice 15U strengthens AML proof through explicit baselines and ablation science.

## Load-Bearing Improvement

- Relaytic-AML compares rules, calibrated linear models, tree ensembles, optional boosted trees, lagged temporal baselines, structural graph baselines, and graph-shadow candidates under the same contract.

## Human Surface

- operators see one AML ablation matrix explaining which capability changed the outcome.

## Agent Surface

- external agents can inspect baseline availability, adapter versions, ablation outcomes, and blocked claims through stable artifacts.

## Intelligence Source

- model-family registry
- optional adapter readiness
- benchmark truth gates
- temporal ladder
- graph evidence
- casework metrics

## Fallback Rule

- optional baselines may be unavailable, but Relaytic records adapter absence and keeps deterministic baselines alive.

## Required Outputs

- `aml_baseline_matrix.json`
- `aml_ablation_matrix.json`
- `aml_baseline_adapter_report.json`
- `aml_capability_contribution_report.json`

## Acceptance Criteria

1. At least three baseline families run or explicitly fall back on one AML workload.
2. The ablation matrix includes no-graph, no-temporal, no-review-budget, no-calibration, and no-typology-prior rows when evidence exists.
3. Benchmark and demo reports surface ablation outcomes.

## Required Verification

- AML baseline matrix unit tests
- AML ablation matrix regression
- optional-adapter fallback regression

