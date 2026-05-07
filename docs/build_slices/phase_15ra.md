# Slice 15R-A - Finish AML proof pack alignment

## Status

Planned next.

## Intent

Slice 15R-A finishes the partially present Slice 15R implementation.

It prevents Relaytic from treating AML proof-pack artifacts as shipped until the benchmark CLI, benchmark show, run summary, assist, mission control, tests, and control docs all expose the same proof posture.

## Load-Bearing Improvement

- Relaytic-AML can rerun PaySim-style and flattened Elliptic-style workloads, materialize the AML proof pack, and explain which claims are allowed, blocked, or supporting-only.

## Human Surface

- operators can inspect AML dataset family, covered benchmark tracks, holdout status, demo readiness, blocked claims, and the primary remaining failure from benchmark and summary surfaces.

## Agent Surface

- external agents can consume AML proof state from stable JSON fields without scraping markdown.

## Intelligence Source

- deterministic benchmark manifests
- holdout claim policy
- benchmark-generalization guards
- release gates
- demo scorecards
- explicit AML failure reports

## Fallback Rule

- if cross-track coverage, holdout posture, or release gates are incomplete, Relaytic blocks broader AML claims and emits a concrete next-step recommendation.

## Required Outputs

- `aml_benchmark_manifest.json`
- `aml_holdout_claim_report.json`
- `aml_demo_scorecard.json`
- `aml_public_claim_guard.json`
- `aml_failure_report.json`

## Acceptance Criteria

1. PaySim-style workload regression materializes the full AML proof pack.
2. Flattened Elliptic-style workload regression materializes the full AML proof pack.
3. Cross-track claim gating blocks broader AML claims until both required tracks are covered.
4. Benchmark CLI, benchmark show, run summary, assist, and mission control expose consistent AML proof posture.
5. `IMPLEMENTATION_STATUS.md`, `MIGRATION_MAP.md`, `ARCHITECTURE_CONTRACT.md`, `RELAYTIC_BUILD_MASTER.md`, `RELAYTIC_SLICING_PLAN.md`, and README agree on the next target after completion.

## Required Verification

- `tests/test_cli_slice15r.py`
- one PaySim-style workload regression
- one Elliptic-style workload regression
- one assist or mission-control AML proof regression

