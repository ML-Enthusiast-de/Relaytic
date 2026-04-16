# Slice 15M - Competitive specialization and benchmark generalization guards

## Status

Planned.

Delivered package boundaries:

- extend `src/relaytic/modeling/`
- extend `src/relaytic/analytics/`
- extend `src/relaytic/search/`
- extend `src/relaytic/benchmark/`
- extend `src/relaytic/evals/`
- extend `src/relaytic/ui/`
- extend `tests/`

Intended artifacts:

- `family_specialization_matrix.json`
- `multiclass_search_profile.json`
- `rare_event_search_profile.json`
- `adapter_activation_report.json`
- `temporal_benchmark_recovery_report.json`
- `benchmark_pack_partition.json`
- `holdout_claim_policy.json`
- `benchmark_generalization_audit.json`

## Intent

Slice 15M should be the final competitiveness-focused bridge between the shipped performance-recovery track and the later academy work.

It exists because the latest benchmark rerun proved three things at once:

- Relaytic is stronger and more trustworthy than before
- multiclass and rare-event competitiveness are still not strong enough
- repeated reuse of the same representative benchmark pack creates a real risk of optimizing Relaytic around the visible dev suite instead of improving general modeling quality

This slice should attack both problems directly: better specialization where Relaytic is weak, and stricter benchmark-governance rules so we do not accidentally cheat by repeatedly training our architecture around the same public scorecards.

## Load-Bearing Improvement

- Relaytic should specialize family routing and search for multiclass and rare-event tasks, recover claim-safe temporal classification benchmarking, and separate dev-benchmark iteration from paper-facing holdout claims so stronger results are more likely to generalize

## Human Surface

- operators should be able to see whether a gain came from stronger general routing versus benchmark-pack tuning, whether optional families were actually available for this run, and whether a result came from a dev pack or a holdout/paper-safe pack

## Agent Surface

- external agents should be able to inspect family-specialization posture, adapter activation state, benchmark-pack partition, and benchmark-generalization audit artifacts through stable JSON-first surfaces

## Required Behavior

- multiclass tasks must race a broader finalist set than the current default tabular ladder
- rare-event tasks must use an explicit imbalance-aware search profile rather than inheriting generic classification defaults
- CatBoost, LightGBM, and XGBoost must report readiness and activation cleanly; if absent they must degrade explicitly, not silently
- temporal classification benchmarks must either materialize a valid comparison contract with healthy folds or fail closed for paper use
- lagged temporal feature generation on benchmark paths must stop using fragmented repeated column insertion as the normal implementation path
- Relaytic must partition benchmark packs into at least `dev` and `holdout` postures, and paper-facing claims must not be based only on the repeatedly inspected dev pack
- no route-selection, family-selection, or threshold logic may branch on benchmark dataset identity directly; the generalization audit must be able to prove that

## Acceptance Criteria

Slice 15M is acceptable only if:

1. one multiclass benchmark shows a broader family race than before and either a real metric gain or an honest explicit miss
2. one rare-event benchmark shows an explicit imbalance-aware search profile and better final posture than the generic profile
3. one temporal classification benchmark becomes claim-safe or is blocked only for legitimate remaining data/split reasons rather than missing benchmark contract fields
4. one benchmark run records which pack partition (`dev` or `holdout`) produced the claim
5. one audit artifact proves Relaytic did not branch on benchmark dataset identity

## Required Verification

- one multiclass specialization regression test
- one rare-event specialization regression test
- one temporal classification benchmark-recovery test
- one benchmark-pack partition / holdout-claim test
- one benchmark-generalization audit test
