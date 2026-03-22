# Slice 11 - Benchmark parity and reference approaches

## Status

Implemented in the current baseline.

Shipped surface:

- package boundary: `src/relaytic/benchmark/`
- public commands: `relaytic benchmark run` and `relaytic benchmark show`
- current artifacts: `reference_approach_matrix.json`, `benchmark_gap_report.json`, and `benchmark_parity_report.json`

## Intent

Slice 11 is where Relaytic stops claiming strength only through architecture and starts proving it against explicit reference approaches under the same evaluation contract.

This slice is successful only if Relaytic can:

- compare its selected route against explicit deterministic references on the same split and primary metric contract
- report parity, near parity, or clear gaps honestly instead of inventing superiority claims
- surface whether a gap came more from route quality, challenger breadth, calibration policy, uncertainty handling, or bounded-loop policy
- make those results visible to humans and external agents without requiring full artifact-tree inspection

## Required Behavior

- benchmark comparison must remain same-contract by default: same split, same comparison metric, same staged data copy, and same target semantics
- deterministic reference comparisons must remain available even when optional stronger baselines such as FLAML are unavailable
- benchmark reports must remain explicit artifacts rather than hidden score tables
- benchmark output must stay compatible with completion, assist, runtime, and MCP surfaces
- benchmark review must remain honest when no strong reference family is available for the current task or source mode

## Acceptance Criteria

Slice 11 is acceptable only if:

1. one standard public dataset shows parity or near parity against at least one explicit reference approach
2. one run that underperforms emits an honest gap report and a recommended next action instead of pretending success
3. benchmark posture becomes visible in `relaytic show` and downstream governed surfaces
4. the benchmark surface works for both direct CLI use and the Relaytic MCP contract

## Required Verification

Slice 11 should not be considered complete without targeted tests that cover at least:

- one classification benchmark run
- one regression benchmark run
- one run-summary surface showing benchmark parity data
- one completion/governor path that consumes benchmark artifacts
- one interoperability regression showing benchmark tools are exposed to external agents
