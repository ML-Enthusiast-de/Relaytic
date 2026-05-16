# Slice 15U - Strong AML baselines and ablations

## Status

Implemented.

## Intent

Slice 15U strengthens AML proof through explicit baselines and ablation science.

This slice must make the benchmark story causal, not just comparative: a reviewer should be able to see which AML-specific capability changed which metric on which workload family.

## Load-Bearing Improvement

- Relaytic-AML compares rules, calibrated linear models, tree ensembles, optional boosted trees, lagged temporal baselines, structural graph baselines, and graph-shadow candidates under the same contract.
- The baseline and ablation pack must be valid for PaySim-style temporal transaction fraud, flattened Elliptic-style graph AML, and any raw/subgraph track that later becomes available.

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
- `aml_benchmark_relevance_scorecard.json`

## Acceptance Criteria

1. At least three baseline families run or explicitly fall back on one AML workload.
2. The ablation matrix includes no-graph, no-temporal, no-review-budget, no-calibration, and no-typology-prior rows when evidence exists.
3. At least one PaySim-style or transaction-fraud workload and one Elliptic-style graph workload are either covered by the baseline matrix or explicitly blocked with a precise missing-data reason.
4. The relevance scorecard states which public benchmark families the current evidence supports, supports only as a proxy, or does not support.
5. Benchmark and demo reports surface ablation outcomes without implying that a model-score win is an AML system win.

## Required Verification

- AML baseline matrix unit tests
- AML ablation matrix regression
- optional-adapter fallback regression
- benchmark relevance scorecard regression

## Implemented Notes

- Added deterministic 15U artifact generation in `src/relaytic/aml/baselines.py`.
- Added `relaytic aml baselines --run-dir <run_dir>` for rebuilding and inspecting baseline, ablation, capability-contribution, adapter, and relevance artifacts.
- Benchmark run/show, run summary, and the 15S demo bundle now surface AML baseline and ablation outcomes with explicit supported/proxy/blocked benchmark-family language.
- Optional boosted-tree and graph-shadow paths remain guarded: missing adapters are recorded as fallback or blocked evidence, and proxy graph relevance is not promoted into a hard Elliptic/Elliptic2 public claim.
