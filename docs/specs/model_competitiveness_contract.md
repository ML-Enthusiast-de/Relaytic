# Model Competitiveness Contract

## Purpose

This document freezes the product contract for the model-competitiveness track that follows Slice 15 and precedes the broader academy work.

The shipped Slice 15A through Slice 15F path established the first half of that track.

The remaining performance-recovery and paper-competitiveness hardening work is now specified in [performance_recovery_contract.md](performance_recovery_contract.md) and should land as Slice 15G through Slice 15L before the academy begins.

Relaytic should remain:

- local-first
- auditable
- bounded by explicit budgets
- deterministic at the control layer

But it should no longer behave like a system that mostly chooses among a narrow boosted-tree-centric family set with shallow fixed variants.

## Core thesis

Relaytic should become adaptive in how it chooses and tests model families.

That means:

- one canonical task contract must decide what kind of problem Relaytic is solving
- one architecture router must decide which model families are worth trying first
- one bounded HPO layer must decide how much tuning is worth spending
- one benchmark mode must separate scientific competitiveness from deployment readiness
- one shadow-trial path must allow promising externally sourced architectures to prove themselves before they become normal candidates

## Non-goals

This track must not:

- silently replace the deterministic floor with opaque AutoML
- make web or external model downloads mandatory
- route unproven research architectures directly into live authority
- treat benchmark wins as deployment approval
- assume all time-aware data should use sequence models

## Required invariants

### 1. Canonical task contract

Relaytic must create one canonical task/problem artifact early and consume it everywhere later.

That contract must make the following explicit:

- target column
- task type
- problem family
- positive class semantics when applicable
- class count
- time-awareness and sequence-awareness
- benchmark intent
- deployment intent
- metric family
- thresholding posture
- rarity posture

Later stages may enrich the contract, but they must not silently reinterpret it.

### 2. Architecture selection must be evidence-based

Relaytic must not default to boosted-tree families simply because they are already implemented.

Architecture routing must consider at least:

- row count
- feature count
- numeric vs categorical mix
- missingness pattern
- class cardinality
- class imbalance
- sequence structure
- latency and budget profile
- prior benchmark evidence
- workspace analog evidence

For temporal work, architecture routing must also consider:

- true ordered temporal structure versus incidental timestamps
- horizon length
- per-entity sequence depth
- cadence regularity
- whether lagged tabular baselines are already strong enough

### 3. HPO must be bounded and explicit

Training depth must be controlled by explicit contracts, not hidden loops.

Relaytic must persist:

- trial budget
- time budget
- search space
- early-stopping logic
- warm-start source
- per-trial outcomes
- reason for stopping

### 4. Benchmark truth and deployment truth must be separate

Offline benchmark competitiveness and real-world deployment readiness are different judgments.

Relaytic must persist both separately and must never let one overwrite the other.

### 5. Externally sourced architectures must go through shadow proof

Architectures discovered from publications, web research, or adapters must move through:

1. candidate registration
2. offline replay
3. shadow trial
4. promotion readiness review

They must not become default routing options merely because they were mentioned in research.

## Minimum family coverage after this track

By the end of the model-competitiveness track, Relaytic should have:

- a deterministic local linear family
- a deterministic local bagged-tree family
- a deterministic local boosted-tree family
- a stronger histogram-gradient-boosting family
- a stronger extra-trees or random-forest family
- a categorical-aware boosted family when the adapter is available
- a small-data specialized classifier when the adapter is available
- a real sequence family only when the task contract proves sequence structure is present

That sequence family may start as a shadow-only candidate before it is allowed into the standard router.

The current local surrogate families remain the fallback floor even when adapters are unavailable.

## Recommended adaptive architecture policy

Relaytic should prefer policies like these:

- small to medium tabular classification with moderate feature count:
  consider `tabpfn_classifier` when available, otherwise strong histogram or boosted-tree candidates
- mixed-type or categorical-heavy tabular data:
  consider `catboost` when available before generic numeric-only boosting
- large general tabular classification or regression:
  consider histogram-gradient boosting, LightGBM, or XGBoost style families when available
- sparse linear or mostly monotonic regimes:
  keep linear or elastic-net candidates active instead of forcing trees
- multiclass problems:
  widen family diversity and calibration review rather than reusing binary defaults
- labeled rare-event problems:
  treat them as supervised rare-event classification first, not anomaly detection by reflex
- unlabeled anomaly problems:
  route anomaly families only when supervision is genuinely absent
- time-aware ordered data:
  consider lagged tabular routes first and sequence models only when sequence evidence is strong enough

### Temporal doctrine

Relaytic should treat time-aware modeling as a ladder, not a reflex:

1. ordinary tabular baseline
2. lagged tabular baseline
3. stronger temporal-feature tree or boosting routes
4. sequence-native candidates in replay or shadow mode
5. promoted sequence-native routes only after proof

That means:

- `timestamp column` is not enough to justify LSTM or temporal-transformer routing
- sequence families should become live candidates only after a temporal benchmark pack exists and the shadow-trial path is operational

## Required future artifacts

- `task_profile_contract.json`
- `target_semantics_report.json`
- `metric_contract.json`
- `architecture_registry.json`
- `architecture_router_report.json`
- `architecture_search_space.json`
- `hpo_budget_contract.json`
- `trial_ledger.jsonl`
- `early_stopping_report.json`
- `warm_start_transfer_report.json`
- `benchmark_mode_report.json`
- `benchmark_vs_deploy_report.json`
- `paper_benchmark_table.json`
- `rerun_variance_report.json`
- `artifact_dependency_graph.json`
- `freshness_contract.json`
- `recompute_plan.json`
- `architecture_candidate_registry.json`
- `shadow_trial_scorecard.json`
- `candidate_quarantine.json`
- `promotion_readiness_report.json`

## Proof burden

This track is only complete if Relaytic can prove all of the following:

1. one labeled rare-event task is kept in supervised classification posture instead of drifting into anomaly routing
2. one multiclass task chooses a non-default family because the router judged it a better fit
3. one benchmark run produces a strong benchmark judgment while deployment readiness remains conditional for separate reasons
4. one HPO campaign stops for explicit budget or convergence reasons instead of fixed hard-coded variant exhaustion
5. one externally sourced architecture remains shadow-only because its proof is not yet good enough
6. one externally sourced architecture graduates into the candidate registry after replay and shadow evidence

For temporal work, this proof burden also includes:

7. one timestamped dataset where lagged tabular routes beat a naive non-temporal baseline
8. one timestamped dataset where a sequence family is tested and loses honestly
9. one timestamped dataset where a sequence family wins enough in replay or shadow mode to become promotion-ready

## Relationship to the academy track

This competitiveness track comes before the broader academy track.

Reason:

- Relaytic first needs a stronger task contract, stronger model router, stronger benchmark harness, and stronger shadow logic for model families
- only after that should it generalize those ideas into a full capability academy for tools and non-core specialists
