# Performance Recovery Contract

## Purpose

This document freezes the post-Slice-15F performance recovery and paper-competitiveness track that must land before Relaytic starts the academy work.

It exists because the initial model-competitiveness track improved semantics, routing breadth, HPO structure, benchmark surfaces, artifact reuse, and research-imported shadow trials, but it did not yet produce the level of raw modeling strength and paper-safe benchmark truth that Relaytic needs.

## Why this track exists

Recent benchmark comparison work exposed a clear pattern:

- architecture diversity improved
- task semantics improved
- raw performance gains were mixed rather than decisive
- multiclass performance is still not good enough
- temporal benchmarks are not yet paper-safe
- protocol/security eval drift can still invalidate paper claims

That means the next work must not be "more surface area" or "more autonomy."

It must be a direct attack on the modeling ceiling.

## Core thesis

Serious performance gains require six things in order:

1. correct objective and split contracts
2. a stronger first-class competitive family stack
3. staged portfolio search with serious budgets
4. a real temporal engine instead of shallow lag hacks
5. calibration and decision optimization as first-class work
6. benchmark-truth gates that block unsafe paper claims

If Relaytic skips any of those and simply adds more loops or more imported models, it will mostly spend more compute on the wrong families, the wrong objectives, or broken benchmark setups.

## Non-goals

This track must not:

- start the broader academy or generic capability-evolution work
- add more agent theater without stronger model outcomes
- make optional adapters mandatory
- promote sequence models because timestamps exist
- let benchmark wins silently become deployment approval
- let test-friendly loop budgets become production defaults

## Hard lessons that must become doctrine

### 1. Test budgets are not product budgets

Relaytic must separate:

- tiny deterministic test budgets
- local laptop demo budgets
- serious benchmark budgets
- full operator budgets

No future slice may inherit shallow search depth simply because tests need to run quickly.

Every competitive search layer must persist:

- the active profile
- the chosen budget envelope
- why the envelope was chosen
- what deeper search was not attempted

### 2. Objective coherence beats extra search

Relaytic must never optimize one metric, compare on another, threshold on a third, and explain a fourth without making that separation explicit.

Every competitive run must carry one canonical objective family that distinguishes:

- family-selection metric
- finalist-ranking metric
- calibration metric
- threshold or operating-point metric
- benchmark comparison metric
- deployment decision metric

### 3. Family competition comes before deep tuning

Relaytic should not spend most of its budget polishing one early winner from a heuristic ladder.

It must first:

- probe multiple eligible families cheaply
- eliminate weak fits honestly
- deepen only the surviving finalists

### 4. Temporal work needs first-class architecture, not fallback heuristics

Time-aware data is not a small variant of ordinary tabular data.

Relaytic must treat temporal work as a separate competitiveness track with:

- temporal structure detection
- temporal split health
- grouped rolling evaluation
- temporal feature ladders
- sequence candidates only after strong lagged baselines exist

### 5. Calibration and decision optimization are performance work

For rare-event, fraud, review-queue, and abstention-sensitive tasks, raw model fit is only part of the problem.

Relaytic must optimize:

- calibration quality
- threshold choice
- review load
- operating-point cost
- abstention posture

as part of competitiveness, not as polish.

### 6. Paper claims require benchmark-truth gates

Relaytic must not present a benchmark result as paper-safe if any of the following are true:

- protocol conformance is failing
- surface parity is drifting
- the claimed comparison metric is not materialized in the benchmark rows
- temporal splits are degenerate
- leakage checks are unresolved

## Required invariants

### Objective and split invariants

- every run must persist one explicit optimization-objective contract
- every benchmark row must expose the claimed comparison metric
- every temporal classification benchmark must either preserve positive events in validation and test or fail closed
- every task family must preserve its task contract through planning, training, benchmark review, assist, and summary surfaces

### Search invariants

- portfolio search must have distinct stages, not one flat loop
- finalist budgets must be deeper than probe budgets
- warm starts must be evidence-based, not silent bias
- stopping must always record a reason

### Family invariants

- first-class families must own their own training assumptions and search space
- optional adapter families must expose readiness, version, and graceful fallback
- multiclass and rare-event work must not inherit binary-default assumptions blindly

### Temporal invariants

- temporal feature generation must be vectorized enough to avoid repeated fragmented-frame construction as the normal path
- sequence candidates must remain replay-first or shadow-first until they beat strong lagged baselines honestly

### Benchmark truth invariants

- CLI, MCP, mission control, and benchmark bundles must agree on trace identity and adjudication winner
- benchmark tables must separate competitiveness from deployment posture
- paper-safe claims must be emitted only through an explicit gate artifact

## Required future artifacts

- `optimization_objective_contract.json`
- `objective_alignment_report.json`
- `split_diagnostics_report.json`
- `temporal_fold_health.json`
- `metric_materialization_audit.json`
- `family_readiness_report.json`
- `family_eligibility_matrix.json`
- `search_budget_envelope.json`
- `probe_stage_report.json`
- `family_race_report.json`
- `finalist_search_plan.json`
- `multi_fidelity_pruning_report.json`
- `portfolio_search_scorecard.json`
- `temporal_structure_report.json`
- `temporal_feature_ladder.json`
- `rolling_cv_plan.json`
- `temporal_split_guard_report.json`
- `sequence_shadow_scorecard.json`
- `calibration_strategy_report.json`
- `operating_point_contract.json`
- `threshold_search_report.json`
- `decision_cost_profile.json`
- `review_budget_optimization_report.json`
- `trace_identity_conformance.json`
- `benchmark_truth_audit.json`
- `paper_claim_guard_report.json`
- `benchmark_release_gate.json`

## Proof burden

This recovery track is only complete if Relaytic can prove all of the following:

1. one benchmark bundle shows aligned family-selection, calibration, threshold, benchmark, and deployment objectives
2. one temporal classification benchmark avoids zero-positive validation or test folds without manual intervention
3. one multiclass task gets a materially broader family race than the earlier boosted-tree-heavy path
4. one serious benchmark profile runs a clearly deeper finalist search than the test profile without code-path drift
5. one temporal dataset shows lagged tabular competitiveness over a naive non-temporal baseline
6. one temporal sequence candidate loses honestly and stays shadow-only
7. one rare-event task changes outcome quality through calibration or threshold optimization rather than family change alone
8. one benchmark bundle is explicitly blocked from paper-safe status because protocol or benchmark-truth gates fail
9. one clean benchmark bundle is marked safe to cite publicly

## Relationship to the academy track

The academy track must stay after this recovery track.

Reason:

- a weak modeling core will only let the academy discover and promote mediocrity faster
- capability growth is only worth it once Relaytic can trust its task contracts, family competition, search budgets, temporal evaluation, and benchmark-truth gates
