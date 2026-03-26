# Slice 10A - Decision lab, method compiler, and data-acquisition reasoning

## Status

Implemented.

Intended package boundaries:

- `src/relaytic/decision/`
- `src/relaytic/compiler/`
- `src/relaytic/data_fabric/`

Intended artifacts:

- `decision_world_model.json`
- `controller_policy.json`
- `handoff_controller_report.json`
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

Public commands:

- `relaytic decision review`
- `relaytic decision show`

MCP-visible surfaces:

- `relaytic_review_decision`
- `relaytic_show_decision`

## Intent

Slice 10A is the category-shift slice.

This is where Relaytic stops acting like a system that only chooses and judges models and starts acting like a system that can reason about:

- what downstream action follows a prediction
- what false positives, false negatives, defer decisions, and delays cost
- who should act next and how much branch depth or reviewer involvement is justified
- whether more search, more data, or a different intervention policy is the best next move
- how research, memory, and operator context should become executable challenger and feature plans
- what nearby local data could reduce uncertainty more than widening search on the current snapshot

## Load-Bearing Improvement

- Relaytic should stop behaving like a system that only asks "which model wins?" and start behaving like a system that can ask "which action policy, which additional data, which controller choice, and which next experiment most improves the real downstream decision?"

## Human Surface

- humans should be able to inspect the assumed decision regime, action costs, defer/review options, controller posture, data-acquisition suggestions, and compiled method-transfer ideas behind Relaytic's next-step judgment

## Agent Surface

- external agents should be able to consume a machine-readable decision world model, controller policy, handoff-controller report, compiled challenger templates, compiled feature/data hypotheses, and value-of-more-data reasoning without parsing prose

## Intelligence Source

- current artifacts, benchmark results, validated feedback, run memory, privacy-safe research retrieval, runtime evidence, and bounded semantic synthesis

## Fallback Rule

- if action economics, nearby sources, or method references are missing, Relaytic should emit a provisional world model with explicit uncertainty and fall back to current benchmark/memory/planning behavior rather than inventing hidden certainty

## Required Behavior

- decision-world modeling must remain explicit, inspectable, and uncertainty-aware
- Slice 10A should consume the explicit quality and budget contracts from Slice 10B rather than inventing hidden search or stop defaults
- Slice 10A should also consume intervention contracts, override decisions, and causal memory from Slice 10C so downstream decision-world reasoning reflects how the lab is actually being steered
- Slice 10A must make controller logic explicit: who should act next, how much branch depth is justified, when to ask for review, and when to keep work local to one specialist must be written as artifacts rather than inferred from code flow
- compiled methods must remain proposals until local evidence tests them
- source-graph and join reasoning must stay local-first and copy-only
- Relaytic must be able to say when more data is more valuable than more search
- the slice must improve planning, autonomy, lifecycle, and benchmark design rather than living as a side report

## Proof Obligation

- Relaytic must prove that decision-world modeling changes at least one real judgment, that controller logic changes at least one acting path, and that compiled methods become executable proposals rather than narrative summaries

## Acceptance Criteria

Slice 10A is acceptable only if:

1. one case shows modeled action economics changing threshold, abstention, review, or next-step judgment
2. one case shows compiled research or memory becoming an executable challenger or feature template
3. one case shows Relaytic preferring additional local data or a join candidate over broader search
4. one case records explicit uncertainty because the decision environment is under-specified
5. one case shows Relaytic changing branch depth, reviewer involvement, or the next acting specialist because the controller logic said it mattered

## Implementation Notes

Slice 10A is now implemented as:

- `src/relaytic/decision/` for decision-world modeling, controller policy, handoff/intervention policy synthesis, and decision-usefulness reporting
- `src/relaytic/compiler/` for compiled challenger templates, compiled feature hypotheses, and compiled benchmark-protocol changes
- `src/relaytic/data_fabric/` for nearby local-source discovery, source-graph writing, join-candidate analysis, and acquisition planning

The current shipped flow is:

1. read the run's planning, research, memory, control, benchmark, profile, and autonomy context
2. write a provisional but explicit decision world model
3. inspect nearby local staged data and derive join or acquisition options without leaving the local boundary
4. compile executable challenger, feature, and benchmark ideas from current artifacts rather than leaving method transfer as narrative only
5. write controller and usefulness artifacts that can change the visible next-step recommendation in `relaytic show` and autonomy follow-up

## Required Verification

Slice 10A should not be considered complete without targeted tests that cover at least:

- one decision-policy ambiguity case
- one compiled challenger-template case
- one compiled feature-hypothesis case
- one value-of-more-data case
- one source-graph or join-candidate case
- one dynamic-handoff/controller case
