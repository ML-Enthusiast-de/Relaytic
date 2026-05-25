# Paper Track P0-P13 - Relaytic-AML arXiv benchmark path

## Status

P0 through P7 implemented. P8 through P13 planned.

## Intent

Paper Track P0 through P13 is the mandatory path between Slice 15Z-R and Slice 16A.

Slice 15Z-R froze a safe release pack, but it intentionally blocks hard AML and SOTA claims until real paper evidence exists. This track turns that frozen, honest state into a clean repo, relevant benchmark suite, reproducible result table, claim-linted draft, clean-clone dry run, and arXiv-ready release.

## Paper Thesis

Relaytic-AML should be presented as a claim-gated local evaluation environment for temporal, graph, and operational financial-crime ML.

The paper should focus on the evaluation environment, not a leaderboard-only claim:

- model score
- temporal leakage and delayed-label posture
- graph provenance and subgraph support posture
- analyst review-budget utility
- case-packet completeness
- reproducible local artifacts
- public-claim gates

## Required Order

1. **P0 - Freeze and commit the 15Z-R baseline** - implemented
   Commit the current paper-freeze state, record verification, and block new benchmark work until the baseline is stable.
2. **P1 - Legacy public-surface cleanup** - implemented
   Remove stale `corr2surrogate`, prototype, toy, and unsupported SOTA language from public surfaces while retaining only explicit compatibility shims.
3. **P2 - Paper thesis and claim contract** - implemented
   Freeze the paper title, research questions, contribution story, allowed claims, blocked claims, and related-work seed.
4. **P3 - Benchmark dataset registry and access manifest** - implemented
   Record dataset sources, licenses, hashes, split posture, access blockers, and claim posture for each track.
5. **P4 - PaySim-style temporal benchmark runner** - implemented
   Produce a chronological temporal transaction-fraud result row with review-budget metrics and proxy/holdout posture.
6. **P5 - Elliptic graph benchmark loader and provenance** - implemented
   Produce raw or flattened Elliptic-style graph provenance, split proof, and graph claim scope.
7. **P6 - Strong tabular baseline suite** - implemented
   Compare deterministic baselines plus optional LightGBM, CatBoost, XGBoost, TabPFN-style, or other strong tabular adapters under one split contract and explicit budget ladder.
8. **P6-A - PaySim competitive rerun and publishability gate** - implemented
   Rerun PaySim under a paper-grade competitive budget before any PaySim metric can enter a headline table.
9. **P7 - Graph baseline suite** - implemented
   Compare flattened tabular, structural graph-feature, and optional graph-model baselines without conflating their claims.
10. **P8 - AMLSim and Elliptic2 blocked-or-supported track**
   Decide whether synthetic-bank and subgraph AML tracks are runnable for the first paper or explicitly blocked with exact reasons.
11. **P9 - Operational AML evaluation layer**
    Add review-budget, analyst-hour, false-positive reduction, case-packet completeness, and operational claim guards to paper rows.
12. **P10 - Reproducible paper table generator**
    Generate all paper tables from run artifacts, not hand-maintained numbers.
13. **P11 - Paper draft and figure pack**
    Draft the arXiv paper and generate figures from artifacts or clearly mark schematic figures.
14. **P12 - External dry run and clean-clone proof**
    Reproduce the install, paper-smoke benchmark, table generation, claim lint, and leak scan from a clean clone.
15. **P13 - arXiv release and attention pack**
    Release only after P10 through P12 pass; otherwise emit a release blocker and schedule repair.

## Non-Negotiable Gates

- no hard AML or SOTA claim without numeric holdout evidence and passing paper gates
- no single proxy dataset unlocks a broader AML superiority claim
- no first runnable benchmark row is allowed to become a final paper headline row without a competitive rerun under a declared paper budget
- every benchmark must report both a conservative baseline budget and a stronger competitive budget, or explain exactly why the stronger budget was blocked
- every competitive budget must include leakage audits, temporal/graph split checks, adapter/version capture, HPO/search-budget accounting, and validation-only threshold selection before test evaluation
- weak but honest results remain useful as baseline or failure-analysis rows, not as evidence of model quality or SOTA competitiveness
- every table cell cites dataset, split, command, run directory, artifact path, and claim posture
- every optional adapter captures version, eligibility, and fallback state
- blocked datasets are reported as blocked, not replaced silently by easier evidence
- arXiv release requires a clean-clone dry run or a documented release blocker

## Benchmark Ambition Doctrine

Every paper benchmark must run through a staged evidence ladder:

1. **Smoke budget**
   Tiny or fixture-backed run that proves the command, artifacts, and claim gates work. This is never paper performance evidence.
2. **Baseline budget**
   Full dataset where possible, conservative leakage-safe features, deterministic or low-cost models, and fixed split/metric contracts. This establishes the honest floor.
3. **Competitive budget**
   Full dataset, strong feature generation, strong tabular or graph baselines, train-only imbalance handling, calibration, threshold optimization on validation only, and budgeted HPO/search. This is the minimum candidate for a paper performance table.
4. **Release budget**
   Frozen configs, clean-clone reproduction, rerun variance where practical, exact version capture, and claim linting. This is required before arXiv or public attention materials.

If a benchmark looks weak after the baseline budget, Relaytic must treat that as a challenge signal: widen the candidate family, improve leakage-safe feature engineering, raise the search budget, or mark the track as non-competitive. It must not rationalize weak numbers into a headline claim.

## Implementation Notes

P0 added:

- `docs/reports/paper_track_baseline_manifest.json`
- `docs/reports/paper_track_verification_report.json`
- `tests/test_paper_track_p0.py`

P0 keeps hard AML and SOTA performance claims blocked and records Paper Track P1 as the next paper implementation slice.

P1 added:

- `docs/reports/paper_public_surface_hygiene_report.json`
- `docs/reports/legacy_compatibility_retention_report.json`
- `docs/reports/paper_repo_cleanup_scorecard.json`
- modern Relaytic aliases for old model-training and target-ranking API/tool names
- `tests/test_paper_track_p1.py`

P1 kept hard AML and SOTA performance claims blocked before P2 froze the paper thesis contract.

P2 added:

- `docs/paper/paper_thesis.md`
- `docs/reports/paper_thesis_contract.json`
- `docs/reports/paper_claim_taxonomy.json`
- `docs/reports/paper_related_work_seed.json`
- `src/relaytic/release_safety/paper_thesis.py`
- `tests/test_paper_track_p2.py`

P2 froze the paper story as a claim-gated AML evaluation environment and kept SOTA plus hard AML performance claims blocked before P3 froze dataset posture.

P3 added:

- `docs/reports/paper_dataset_registry.json`
- `docs/reports/paper_dataset_access_manifest.json`
- `docs/reports/paper_split_contracts.json`
- `docs/reports/paper_dataset_blockers.json`
- `src/relaytic/release_safety/paper_dataset_registry.py`
- `tests/test_paper_track_p3.py`

P3 freezes dataset source/access posture, license notes, local file expectations, hashes for present local fixtures, split contracts, blocked reasons, and no-auto-download policy. It keeps hard AML and SOTA performance claims blocked and records Paper Track P4 as the next paper implementation slice.

P4 added:

- `docs/reports/paysim_benchmark_manifest.json`
- `docs/reports/paysim_temporal_split_report.json`
- `docs/reports/paysim_operating_point_table.json`
- `docs/reports/paysim_paper_result_row.json`
- `src/relaytic/release_safety/paysim_benchmark.py`
- `relaytic release-safety paysim-benchmark --format json`
- `tests/test_paper_track_p4.py`

P4 runs the full 6,362,620-row PaySim source through a chronological `step` split, uses validation-only threshold selection, applies thresholds fixed to test, reports review-budget and fixed-FPR operating points, and keeps hard AML/SOTA performance claims blocked. The result is supporting proxy evidence for the paper path, not a primary real-world AML superiority claim.

P5 added:

- `docs/reports/elliptic_graph_loader_manifest.json`
- `docs/reports/elliptic_graph_provenance_report.json`
- `docs/reports/elliptic_temporal_split_report.json`
- `docs/reports/elliptic_graph_claim_scope.json`
- `docs/reports/elliptic_paper_result_row.json`
- `src/relaytic/release_safety/elliptic_graph.py`
- `relaytic release-safety elliptic-graph --format json`
- `tests/test_paper_track_p5.py`

P5 inspects the local raw Elliptic graph bundle, records 203,769 nodes, 234,355 edges, 49 time steps, and a chronological train/validation/test split by `time_step`. It keeps unknown labels out of supervised metric scope, allows supporting loader/provenance wording only, and blocks graph performance, graph SOTA, paper-primary, and hard AML claims until P7 graph baselines run.

P6 added:

- `docs/reports/paper_baseline_suite_manifest.json`
- `docs/reports/paper_baseline_version_matrix.json`
- `docs/reports/paper_tabular_baseline_table.json`
- `docs/reports/paper_baseline_fallback_report.json`
- `docs/reports/paper_benchmark_budget_contract.json`
- `docs/reports/paper_competitive_search_trace.json`
- `docs/reports/paper_leakage_safe_feature_report.json`
- `docs/reports/paper_publishability_gate.json`
- `src/relaytic/release_safety/paper_baselines.py`
- `relaytic release-safety tabular-baselines --budget-tier baseline --run-optional --format json`
- `tests/test_paper_track_p6.py`

P6 runs six full-data PaySim baseline families with an explicit baseline budget, versions and fallback state, a shared chronological split, train-only feature fitting, and validation-only threshold selection. Extra Trees is selected on validation and reports fixed test PR-AUC `0.331345`; the suite records the improvement as clean baseline evidence only. Headline performance, paper-primary, and hard AML claims remain blocked until P6-A performs the declared competitive rerun and publishability decision.

P6-A added:

- `docs/reports/paysim_competitive_benchmark_manifest.json`
- `docs/reports/paysim_competitive_budget_contract.json`
- `docs/reports/paysim_competitive_search_trace.json`
- `docs/reports/paysim_leakage_safe_feature_report.json`
- `docs/reports/paysim_competitive_baseline_table.json`
- `docs/reports/paysim_publishability_gate.json`
- `src/relaytic/release_safety/paysim_competitive.py`
- `relaytic release-safety paysim-competitive --budget-tier competitive --run-optional --format json`
- `tests/test_paper_track_p6a.py`

P6-A runs the full PaySim source with balance fields excluded and destination histories derived strictly from prior steps. It records 14 probe trials and five full-training finalists, selects Extra Trees on validation PR-AUC `0.568725`, performs validation-only Platt calibration and operating-point selection, and reports fixed test PR-AUC `0.638773` versus the P6 baseline `0.331345`. Its gate admits a supporting-only PaySim paper-table candidate while continuing to block headline, hard AML, and SOTA language until graph and release proof pass.

P7 added:

- `docs/reports/paper_graph_baseline_manifest.json`
- `docs/reports/paper_graph_feature_table.json`
- `docs/reports/paper_graph_model_shadow_scorecard.json`
- `docs/reports/paper_graph_baseline_fallback_report.json`
- `docs/reports/paper_graph_budget_contract.json`
- `docs/reports/paper_graph_competitive_search_trace.json`
- `docs/reports/paper_graph_publishability_gate.json`
- `src/relaytic/release_safety/graph_baselines.py`
- `relaytic release-safety graph-baselines --budget-tier competitive --run-optional --format json`
- `tests/test_paper_track_p7.py`

P7 verifies that all raw Elliptic edges are same-time-step observable, runs a competitive paired feature-view evaluation without test-driven selection, and selects LightGBM over source features plus label-free structural snapshot features (`validation_pr_auc=0.976654`, `test_pr_auc=0.668756`). The paired source-feature-only row reports `test_pr_auc=0.664168`, so the measured structural lift is modest (`+0.004588`). PyG GraphSAGE runs shadow-only and reports weaker test `PR-AUC=0.388907`; it remains failure-analysis evidence until recovery and repeated-seed proof exist. The selected graph-feature row is supporting-only; graph-neural, SOTA, headline, paper-primary, and hard AML claims remain blocked.

## Next Implementation Target

The next implementation target is **Paper Track P8**.

P8 should decide whether AMLSim and Elliptic2 can enter the first paper with runnable, reproducible evidence or must remain explicit limitations. It must also preserve P7's finding that the current graph-neural shadow is not competitive rather than silently promoting it.
