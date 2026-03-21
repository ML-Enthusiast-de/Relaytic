# Slice 09C - Autonomous experimentation, executable lifecycle loops, and challenger portfolio expansion

## Status

Implemented in the current baseline.

Shipped surface:

- package boundary: `src/relaytic/autonomy/`
- public commands: `relaytic autonomy run` and `relaytic autonomy show`
- current artifacts: `autonomy_loop_state.json`, `autonomy_round_report.json`, `challenger_queue.json`, `branch_outcome_matrix.json`, `retrain_run_request.json`, `recalibration_run_request.json`, `champion_lineage.json`, and `loop_budget_report.json`

## Intent

Slice 09C is where Relaytic stops only recommending the next move and starts carrying out a bounded second pass itself.

This slice is successful only if Relaytic can:

- execute one autonomous follow-up round after completion/lifecycle judgment
- expand challenger science beyond one narrow challenger
- run recalibration, retraining, or re-planning as explicit branch actions
- keep champion lineage and loop budgets fully inspectable

## Weaknesses It Must Close

Without this slice, Relaytic still has these weaknesses:

- completion and lifecycle artifacts are strong, but mostly descriptive
- `continue_experimentation`, `recalibrate`, and `retrain` usually stop at a recommendation
- challenger science is still too narrow to feel frontier-sharp
- there is no explicit champion-lineage history across second-pass branches

## Planned Package Boundary

Slice 09C should introduce:

- `src/relaytic/autonomy/`

That package should own loop-state persistence, branch budgeting, challenger queues, executable follow-up requests, and champion-lineage updates.

## Required Outputs

- `autonomy_loop_state.json`
- `autonomy_round_report.json`
- `challenger_queue.json`
- `branch_outcome_matrix.json`
- `retrain_run_request.json`
- `recalibration_run_request.json`
- `champion_lineage.json`
- `loop_budget_report.json`

## Required Behavior

- completion and lifecycle should be able to emit executable branch requests rather than advisory next steps only
- Relaytic must support at least one bounded second-pass action from challenger expansion, recalibration, retraining, or re-plan-with-counterposition
- challenger science must expand to a small bounded portfolio when route narrowness or challenger pressure is detected
- every autonomous round must record why it ran, what it cost, what changed, and whether the champion survived
- loops must stop on budget, repeated non-improvement, policy conflict, or confidence plateau
- deterministic fallback must remain available when auto-execution is disabled

## Acceptance Criteria

Slice 09C is acceptable only if:

1. one run automatically performs a second pass after `continue_experimentation`
2. one case executes recalibration instead of full retraining and keeps the stronger result
3. one case executes retraining and records clear champion lineage
4. one challenger portfolio overturns the first winner or proves the first winner robust
5. one loop stops honestly because more search is no longer worth it

## Required Verification

Slice 09C should not be considered complete without targeted tests that cover at least:

- automatic second-pass execution after completion/lifecycle judgment
- challenger portfolio expansion under route narrowness
- recalibration execution and comparison against retraining
- champion-lineage persistence across promotion and hold decisions
- stop-on-plateau and stop-on-budget behavior
