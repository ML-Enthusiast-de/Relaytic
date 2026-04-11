# Slice 15E - Execution DAG, freshness contracts, and artifact reuse

## Status

Shipped.

Delivered package boundaries:

- extend `src/relaytic/runtime/`
- extend `src/relaytic/runs/`
- extend `src/relaytic/workspace/`
- extend `src/relaytic/search/`

Intended artifacts:

- `artifact_dependency_graph.json`
- `freshness_contract.json`
- `recompute_plan.json`
- `materialization_cache_index.json`
- `invalidation_report.json`

## Intent

Slice 15E turns Relaytic from an imperative stage runner into a more explicit dependency-driven system.

This matters because deeper search and broader benchmark packs become much more practical when Relaytic can reuse clean upstream materializations instead of rerunning heavy stages reflexively.

## Load-Bearing Improvement

- Relaytic should be able to tell exactly what must be recomputed, what can be reused, and why, so deeper loops do not feel wasteful or fragile

## Human Surface

- operators should be able to inspect why a rerun recomputed some stages, skipped others, and reused existing artifacts where safe

## Agent Surface

- external agents should be able to inspect dependency graphs, freshness contracts, and recompute plans before asking Relaytic to spend more compute

## Required Behavior

- every major artifact family must declare its upstream dependencies
- Relaytic must materialize one explicit dependency graph
- Relaytic must decide rerun scope from dependency and freshness contracts instead of imperative stage ordering alone
- benchmark review, completion review, and mission-control replay must avoid rerunning heavy upstream stages when inputs have not changed
- invalidation must be explicit, not implicit

## Acceptance Criteria

Slice 15E is acceptable only if:

1. one completion or benchmark review reuses heavy upstream artifacts instead of recomputing them
2. one changed input invalidates only the required downstream slices
3. one human or agent can inspect a recompute plan before rerunning
4. one benchmark shard completes faster because reuse is working as intended

## Required Verification

- one dependency-graph test
- one freshness-invalidation test
- one no-op review reuse test
- one recompute-plan explanation test
