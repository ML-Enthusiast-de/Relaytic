# Slice 10B - Quality contracts, visible budgets, and operator/lab profiles

## Status

Implemented.

Intended package boundary:

- `src/relaytic/profiles/`

Intended artifacts:

- `quality_contract.json`
- `quality_gate_report.json`
- `budget_contract.json`
- `budget_consumption_report.json`
- `operator_profile.json`
- `lab_operating_profile.json`

Primary public surfaces:

- `relaytic profiles review`
- `relaytic profiles show`
- `relaytic show`
- `relaytic assist show`

## Intent

Slice 10B is where Relaytic stops hiding "good enough" and "worth the search" inside scattered defaults.

This slice is successful only if Relaytic can:

- materialize one explicit quality contract for the current run
- materialize one explicit budget contract for the current run
- show configured versus consumed budget clearly
- distinguish lab-scoped posture from operator-scoped posture without personalizing truth-bearing logic
- keep running autonomously when no inputs are provided by deriving contracts explicitly instead of leaving them implicit

## Required Behavior

- quality and budget contracts must be explicit, persisted, and inspectable
- operator and lab profiles may shape review strictness, benchmark appetite, explanation style, abstain/review preference, and budget posture
- operator and lab profiles must not silently override deterministic metrics, model outcomes, or artifact truth
- completion, lifecycle, autonomy, benchmark, later control-contract logic, and later search-control logic should consume the same contracts rather than inventing their own hidden defaults
- the same contract view must be visible through CLI, MCP, assist, and summary surfaces

## Acceptance Criteria

Slice 10B is acceptable only if:

1. one no-input run materializes explicit quality and budget contracts before major execution
2. one bounded operator or lab profile changes posture without changing deterministic artifact truth
3. one surface shows configured budget, consumed budget, and remaining budget together
4. one report explains continue, recalibrate, retrain, or stop in terms of the explicit quality contract
5. one external-agent path consumes the same contracts through JSON or MCP without scraping prose

## Verification

Implemented with targeted coverage for:

- task-derived default quality contracts
- operator-profile overlays that change posture without changing deterministic artifact truth
- lab-profile overlays that tighten benchmark/review posture
- budget-consumption reporting
- CLI and host-facing visibility through `relaytic show`, `relaytic profiles show`, assist surfaces, and the MCP-facing run-summary path

## Required Verification

Slice 10B should not be considered complete without targeted tests that cover at least:

- one task-derived default quality contract case
- one derived hardware-budget case
- one operator-profile overlay case
- one lab-profile overlay case
- one budget-consumption reporting case
- one CLI/MCP visibility-parity case
