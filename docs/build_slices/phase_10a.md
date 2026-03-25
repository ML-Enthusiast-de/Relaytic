# Slice 10A - Decision lab, method compiler, and data-acquisition reasoning

## Status

Planned.

Intended package boundaries:

- `src/relaytic/decision/`
- `src/relaytic/compiler/`
- `src/relaytic/data_fabric/`

Intended artifacts:

- `decision_world_model.json`
- `intervention_policy_report.json`
- `decision_usefulness_report.json`
- `value_of_more_data_report.json`
- `data_acquisition_plan.json`
- `source_graph.json`
- `join_candidate_report.json`
- `method_compiler_report.json`
- `compiled_challenger_templates.json`
- `compiled_feature_hypotheses.json`
- `compiled_benchmark_protocol.json`

## Intent

Slice 10A is the category-shift slice.

This is where Relaytic stops acting like a system that only chooses and judges models and starts acting like a system that can reason about:

- what downstream action follows a prediction
- what false positives, false negatives, defer decisions, and delays cost
- whether more search, more data, or a different intervention policy is the best next move
- how research, memory, and operator context should become executable challenger and feature plans
- what nearby local data could reduce uncertainty more than widening search on the current snapshot

## Required Behavior

- decision-world modeling must remain explicit, inspectable, and uncertainty-aware
- Slice 10A should consume the explicit quality and budget contracts from Slice 10B rather than inventing hidden search or stop defaults
- Slice 10A should also consume intervention contracts, override decisions, and causal memory from Slice 10C so downstream decision-world reasoning reflects how the lab is actually being steered
- compiled methods must remain proposals until local evidence tests them
- source-graph and join reasoning must stay local-first and copy-only
- Relaytic must be able to say when more data is more valuable than more search
- the slice must improve planning, autonomy, lifecycle, and benchmark design rather than living as a side report

## Acceptance Criteria

Slice 10A is acceptable only if:

1. one case shows modeled action economics changing threshold, abstention, review, or next-step judgment
2. one case shows compiled research or memory becoming an executable challenger or feature template
3. one case shows Relaytic preferring additional local data or a join candidate over broader search
4. one case records explicit uncertainty because the decision environment is under-specified

## Required Verification

Slice 10A should not be considered complete without targeted tests that cover at least:

- one decision-policy ambiguity case
- one compiled challenger-template case
- one compiled feature-hypothesis case
- one value-of-more-data case
- one source-graph or join-candidate case
