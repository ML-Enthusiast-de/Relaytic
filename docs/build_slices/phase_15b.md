# Slice 15B - Model registry expansion and adaptive architecture routing

## Status

Shipped.

Delivered package boundaries:

- extend `src/relaytic/modeling/`
- extend `src/relaytic/planning/`
- extend `src/relaytic/search/`
- extend `src/relaytic/analytics/`
- extend `src/relaytic/research/`

Intended artifacts:

- `architecture_registry.json`
- `architecture_router_report.json`
- `candidate_family_matrix.json`
- `architecture_fit_report.json`
- `family_capability_matrix.json`
- `architecture_ablation_report.json`

## Intent

Slice 15B stops Relaytic from behaving like a `boosted_tree_for_everything` system.

It introduces a real architecture registry and an explicit router that selects model families based on task semantics, dataset structure, resource profile, and benchmark evidence.

## Load-Bearing Improvement

- Relaytic should widen beyond a narrow tree-centric default and choose model families because they fit the problem, not because they already exist

## Human Surface

- operators should be able to see which architectures were considered, why some were recommended first, why some were excluded, and whether an optional adapter family was unavailable or merely not selected

## Agent Surface

- external agents should be able to inspect the architecture registry, router reasoning, candidate order, and adapter availability through stable JSON-first artifacts

## Required Behavior

- Relaytic must keep the existing deterministic local surrogate families as the fallback floor
- Relaytic must add stronger tabular families beyond the current custom tree and logistic set
- the first expansion pass must include:
  - histogram-gradient-boosting regression and classification
  - extra-trees or random-forest regression and classification
  - stronger regularized linear routes where appropriate
  - optional categorical-native boosting through adapter slots such as CatBoost when installed
  - optional modern gradient-boosting adapters such as XGBoost or LightGBM when installed
  - optional small-data specialized classification adapters such as TabPFN when installed
- the router must consider:
  - row count
  - feature count
  - categorical ratio
  - missingness
  - class count
  - rarity
  - time-awareness
  - horizon structure
  - per-entity sequence depth
  - cadence regularity
  - benchmark evidence
  - workspace analog evidence
- sequence LSTM or other sequence families must not be used on ordinary static tables by default
- sequence families may only enter the candidate set when the task contract proves true ordered sequence structure and sufficient data support
- the first temporal comparison ladder should be:
  - ordinary tabular baseline
  - lagged tabular baseline
  - stronger temporal-feature tree/boosting routes
  - sequence-native candidates only after those baselines are in place

## Acceptance Criteria

Slice 15B is acceptable only if:

1. one categorical-heavy dataset prefers a categorical-aware family when the adapter is available
2. one multiclass dataset routes to a non-default family because the registry judged it a better fit
3. one small-to-medium classification dataset can prefer a small-data specialized adapter when available
4. one static table explicitly rejects sequence-family routing with an auditable explanation
5. one timestamped dataset produces an explicit temporal routing report showing why Relaytic stayed with lagged tabular or escalated to a sequence candidate

## Required Verification

- one registry-availability test
- one architecture-router test for multiclass data
- one static-table `why not LSTM?` explanation test
- one adapter-unavailable graceful-fallback test

## Shipped Notes

Slice 15B is now landed.

It ships:

- canonical architecture-routing artifacts from planning through run summary
- widened built-in trainable families for histogram-gradient boosting and extra-trees regression/classification
- optional CatBoost, XGBoost, LightGBM, and TabPFN adapter slots with graceful availability reporting
- shared planner, memory, inference, assist, and summary integration so architecture choice is inspectable instead of hidden inside Builder defaults
- explicit sequence-family shadow gating so static tables reject LSTM/transformer routing with an auditable explanation

## Verification Snapshot

Targeted slice verification passed:

- `tests/test_architecture_routing.py`
- `tests/test_model_training_candidates.py`
- `tests/test_planning_agents.py`
- `tests/test_assist_agents.py`
- `tests/test_cli_slice15b.py`

Direct slice wall result:

- `27 passed`

Broader adjacent validation also passed:

- `43 passed`
