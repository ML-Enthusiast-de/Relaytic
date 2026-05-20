# Paper Track P0-P13 - Relaytic-AML arXiv benchmark path

## Status

P0 through P2 implemented. P3 through P13 planned.

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
4. **P3 - Benchmark dataset registry and access manifest**
   Record dataset sources, licenses, hashes, split posture, access blockers, and claim posture for each track.
5. **P4 - PaySim-style temporal benchmark runner**
   Produce a chronological temporal transaction-fraud result row with review-budget metrics and proxy/holdout posture.
6. **P5 - Elliptic graph benchmark loader and provenance**
   Produce raw or flattened Elliptic-style graph provenance, split proof, and graph claim scope.
7. **P6 - Strong tabular baseline suite**
   Compare deterministic baselines plus optional LightGBM, CatBoost, XGBoost, TabPFN-style, or other strong tabular adapters under one split contract.
8. **P7 - Graph baseline suite**
   Compare flattened tabular, structural graph-feature, and optional graph-model baselines without conflating their claims.
9. **P8 - AMLSim and Elliptic2 blocked-or-supported track**
   Decide whether synthetic-bank and subgraph AML tracks are runnable for the first paper or explicitly blocked with exact reasons.
10. **P9 - Operational AML evaluation layer**
    Add review-budget, analyst-hour, false-positive reduction, case-packet completeness, and operational claim guards to paper rows.
11. **P10 - Reproducible paper table generator**
    Generate all paper tables from run artifacts, not hand-maintained numbers.
12. **P11 - Paper draft and figure pack**
    Draft the arXiv paper and generate figures from artifacts or clearly mark schematic figures.
13. **P12 - External dry run and clean-clone proof**
    Reproduce the install, paper-smoke benchmark, table generation, claim lint, and leak scan from a clean clone.
14. **P13 - arXiv release and attention pack**
    Release only after P10 through P12 pass; otherwise emit a release blocker and schedule repair.

## Non-Negotiable Gates

- no hard AML or SOTA claim without numeric holdout evidence and passing paper gates
- no single proxy dataset unlocks a broader AML superiority claim
- every table cell cites dataset, split, command, run directory, artifact path, and claim posture
- every optional adapter captures version, eligibility, and fallback state
- blocked datasets are reported as blocked, not replaced silently by easier evidence
- arXiv release requires a clean-clone dry run or a documented release blocker

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

P2 freezes the paper story as a claim-gated AML evaluation environment, keeps SOTA and hard AML performance claims blocked, and records Paper Track P3 as the next paper implementation slice.

## Next Implementation Target

The next implementation target is **Paper Track P3**.

P3 should not add benchmark modeling behavior yet. It should freeze dataset sources, licenses, access posture, split contracts, local file expectations, hashes when available, and blocked reasons before any runner is treated as paper evidence.
