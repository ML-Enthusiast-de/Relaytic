# Slice 15R - AML flagship benchmark, demo, and paper pack

## Status

Accepted through Slice 15R-A. The proof-pack implementation is now covered by targeted tests, cross-surface alignment checks, and control-doc status updates.

## Intent

Slice 15R is the proof slice for the AML pivot.

It turns the earlier AML slices into a public-safe, paper-safe, and demo-safe evidence pack.

Current doctrine: do not move into Academy work after the AML proof-pack implementation. The next implementation target is Slice 15S, which turns the accepted proof pack into one public-safe flagship AML demo bundle.

## Load-Bearing Improvement

- Relaytic-AML should have one explicit AML benchmark pack, one holdout claim policy, one flagship demo pack, and one paper-facing result bundle that proves value on a hard AML problem instead of generic benchmark narration

## Human Surface

- operators should be able to inspect which AML claims are safe to make publicly, which demos are healthy, and where Relaytic-AML still loses

## Agent Surface

- external agents should be able to inspect AML benchmark manifests, holdout posture, demo scorecards, and public-claim guards through stable JSON surfaces

## Intelligence Source

- benchmark rigor
- holdout and paper-safe claim gating
- honest failure reporting
- no benchmark-identity shortcuts

## Intended Artifacts

- `aml_benchmark_manifest.json`
- `aml_holdout_claim_report.json`
- `aml_demo_scorecard.json`
- `aml_public_claim_guard.json`
- `aml_failure_report.json`

## Acceptance Criteria

1. one AML benchmark pack can be rerun and rendered as a public-ready table
2. one AML demo pack can be scored as public-safe
3. one real AML miss is surfaced honestly with a concrete next-step recommendation
4. the benchmark pack explicitly covers PaySim-style temporal transaction fraud and Elliptic-style temporal graph AML before broader public claims are made
5. benchmark CLI, benchmark show, run summary, assist, and mission control expose the same AML proof posture
6. docs and status files say clearly whether 15R is partial, shipped, or blocked

## Required Verification

- one AML benchmark manifest test
- one AML holdout-claim test
- one AML flagship-demo regression test
- one PaySim-style workload regression test
- one Elliptic-style workload regression test
