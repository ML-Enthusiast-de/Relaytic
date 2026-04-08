# Slice 15D - Paper-grade benchmark harness and benchmark rigor

## Status

Planned.

Delivered package boundaries:

- extend `src/relaytic/benchmark/`
- extend `src/relaytic/evals/`
- extend `src/relaytic/runs/`
- extend `src/relaytic/ui/`

Intended artifacts:

- `paper_benchmark_manifest.json`
- `paper_benchmark_table.json`
- `benchmark_ablation_matrix.json`
- `rerun_variance_report.json`
- `benchmark_claims_report.json`
- `benchmark_vs_deploy_report.json`

## Intent

Slice 15D turns benchmark work from an ad hoc test pack into a reproducible paper-facing evaluation surface.

## Load-Bearing Improvement

- Relaytic should be able to produce benchmark tables, ablations, rerun variance, and claim boundaries that are honest enough for papers and strong enough for serious external scrutiny

## Human Surface

- operators should be able to inspect paper-grade benchmark tables and see exactly what claim Relaytic is making, what it is not claiming, and where the weak spots remain

## Agent Surface

- external agents should be able to consume benchmark tables, variance reports, and ablation matrices directly from artifacts

## Required Behavior

- Relaytic must keep the current public benchmark pack as a reproducible local-first base
- Relaytic must add a dedicated temporal benchmark pack for timestamped tabular data and later sequence-native challengers
- Relaytic should add a second-tier optional benchmark expansion path for broader benchmark suites where licensing and runtime remain acceptable
- benchmark reporting must separate:
  - competitiveness claim
  - deployment-readiness claim
  - explanation of why the two differ
- benchmark mode must record:
  - dataset source
  - task contract
  - selected family
  - selected hyperparameters
  - comparison metric
  - rank among references
  - rerun variance
  - ablation impact
- temporal benchmark mode must additionally record:
  - horizon type
  - timestamp cadence quality
  - lagged-baseline result
  - sequence-candidate result when present
  - explanation of why a sequence family was or was not used

## Acceptance Criteria

Slice 15D is acceptable only if:

1. one full benchmark table can be rendered from artifacts without manual spreadsheet cleanup
2. one rerun-variance report shows stability across repeated runs
3. one ablation matrix shows which Relaytic capabilities materially change benchmark outcomes
4. one benchmark claim report states clearly where Relaytic is below reference and why
5. one temporal benchmark report shows whether lagged tabular or sequence-native modeling was actually justified

## Required Verification

- one benchmark-pack smoke test
- one rerun-variance test
- one benchmark-ablation test
- one benchmark-vs-deploy consistency test
