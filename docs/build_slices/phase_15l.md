# Slice 15L - Benchmark truth hardening and paper-claim gates

## Status

Planned.

Delivered package boundaries:

- extend `src/relaytic/benchmark/`
- extend `src/relaytic/evals/`
- extend `src/relaytic/tracing/`
- extend `src/relaytic/runtime/`
- extend `src/relaytic/assist/`
- extend `src/relaytic/ui/`
- extend `tests/`

Intended artifacts:

- `trace_identity_conformance.json`
- `benchmark_truth_audit.json`
- `paper_claim_guard_report.json`
- `eval_surface_parity_report.json`
- `benchmark_release_gate.json`
- `dataset_leakage_audit.json`

## Intent

Slice 15L closes the performance recovery track by making benchmark claims trustworthy enough for public use.

This slice is where Relaytic stops saying only "here is a benchmark table" and starts saying "this result is safe to cite publicly" or "this result is blocked and here is why."

## Load-Bearing Improvement

- Relaytic should be able to issue benchmark bundles that are explicitly safe or unsafe for paper-facing claims based on protocol conformance, trace identity, metric truth, split health, and leakage checks

## Human Surface

- operators should be able to inspect whether a benchmark result is safe to mention publicly, what blocked it, and what has to be fixed next

## Agent Surface

- external agents should be able to consume a machine-readable claim gate and know whether benchmark results are publishable, demo-safe, or blocked

## Required Behavior

- CLI, MCP, mission control, and benchmark bundles must agree on trace identity and adjudication winner
- protocol and security eval failures must block paper-safe benchmark status
- degenerate temporal splits, unavailable comparison metrics, and unresolved leakage findings must block paper-safe benchmark status
- benchmark tables must mark safe-to-claim posture explicitly instead of relying on human interpretation
- assist and mission control must answer why a result is blocked from public claim using the same gate artifacts

## Acceptance Criteria

Slice 15L is acceptable only if:

1. one trace-identity drift class is eliminated across CLI and MCP
2. one benchmark bundle is blocked from paper-safe status because benchmark-truth or protocol gates fail
3. one degenerate temporal benchmark is blocked explicitly rather than silently reported
4. one clean benchmark bundle is marked safe to cite publicly

## Required Verification

- one trace-identity parity test
- one benchmark-truth audit regression test
- one temporal claim-blocking test
- one public-claim-gate explanation test
