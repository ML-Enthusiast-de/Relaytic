# Slice 13 - Search controller, accelerated execution, and distributed local experimentation

## Status

Planned.

Intended package boundaries:

- extend `src/relaytic/autonomy/`
- extend `src/relaytic/runtime/`
- extend `src/relaytic/modeling/`

Intended artifacts:

- `search_controller_plan.json`
- `portfolio_search_trace.json`
- `hpo_campaign_report.json`
- `search_decision_ledger.json`
- `execution_backend_profile.json`
- `device_allocation.json`
- `distributed_run_plan.json`
- `scheduler_job_map.json`
- `checkpoint_state.json`
- `execution_strategy_report.json`
- `search_value_report.json`
- `search_controller_eval_report.json`

## Intent

Slice 13 is where Relaytic stops running only narrow bounded search and starts managing broader search, deeper HPO, and execution strategy under one explicit controller.

The slice is successful only if Relaytic can:

- decide when more search is worth it under quality, budget, and beat-target pressure
- widen or prune branches explicitly
- allocate HPO depth under the same decision contract
- resume interrupted local or distributed execution without losing replayability

## Load-Bearing Improvement

- Relaytic should be able to run wider challenger fields, deeper HPO, calibration branches, uncertainty/abstention experiments, and dynamic controller-adjusted branch depth under one explicit search controller instead of only static narrow search choices

## Human Surface

- humans should be able to inspect why Relaytic widened or pruned search, how much HPO effort it allocated, which device profile it chose, and which branches were considered too expensive or too low value

## Agent Surface

- external agents should be able to consume one search-controller plan, execution strategy, checkpoint state, scheduler map, HPO campaign report, and branch-pruning rationale without inferring hidden orchestration decisions

## Intelligence Source

- budget-aware search policy, benchmark gaps, beat-target pressure, decision-world models, canonical trace/eval artifacts, hardware detection, and optional distributed execution adapters

## Fallback Rule

- when acceleration or distributed execution is unavailable, Relaytic must still run the same search logic in a narrower local profile rather than changing the source of truth or losing replayability

## Required Behavior

- Slice 13 must consume the explicit quality and budget contracts from Slice 10B instead of inventing separate hidden search limits
- Slice 13 must consume real runtime/control accounting and any beat-target contract from Slice 11A rather than relying only on estimated search effort
- Slice 13 should consume the canonical trace/eval artifacts from Slice 12B so branch expansion, pruning, and controller changes can be justified by replayable evidence rather than implicit heuristics
- search widening, pruning, HPO allocation, and device/backend choices must extend the mission-control surface introduced in Slice 11B and expanded through Slices 11C, 11D, 11E, 11F, and 11G so humans and external agents can see why search did or did not go deeper
- device-aware planning must change how Relaytic executes, not silently change what it believes
- distributed execution must remain resumable and safe for long local runs
- broader route families, calibration variants, uncertainty wraps, abstention policies, imported-incumbent beat-target branches, and deeper HPO campaigns should be eligible where their value is justified
- search decisions must produce explicit value-of-search evidence showing why Relaytic widened, pruned, or stopped rather than leaving deeper HPO to ambient availability
- Slice 13 should include at least one proof where Relaytic declines more search because the value contract says stop, not because hardware or adapters are missing

## Proof Obligation

- Relaytic must prove that wider search is allocated or denied for explicit decision reasons, not because deeper HPO happened to be available, and that those reasons remain legible to both humans and external agents

## Acceptance Criteria

Slice 13 is acceptable only if:

1. one same-plan run succeeds across two execution profiles
2. one interrupted distributed run resumes from checkpoint
3. one low-value branch is pruned while a higher-value branch is widened with explicit justification
4. one case widens or cuts HPO effort because the decision contract, beat-target pressure, or trace evidence says more search is or is not worth it
5. one case records explicit stop-search reasoning in `search_value_report.json` even though deeper HPO or broader branches were technically available

## Required Verification

Slice 13 should not be considered complete without targeted tests that cover at least:

- one multi-profile execution case
- one checkpoint-resume case
- one branch-pruning case
- one HPO-allocation case
- one explicit stop-search-value case
- one agent-consumable execution-strategy case
