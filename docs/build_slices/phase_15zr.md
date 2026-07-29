# Slice 15Z-R - Paper benchmark and release freeze

## Status

Implemented.

## Intent

Slice 15Z-R freezes the public benchmark and release evidence after the AML productization track and before the Paper Track.

This release-readiness slice proves that Relaytic-AML can run relevant
benchmarks, reproduce the artifacts, and state public claims without overreach.

It is not the final arXiv release gate. Paper Track P0 through P13 must still clean public surfaces, freeze the paper thesis, run real benchmark rows, add strong baselines, generate reproducible paper tables, draft and lint the paper, and pass an external dry run before Academy work or public hard-performance claims resume.

## Load-Bearing Improvement

- Relaytic emits one paper/release benchmark pack that ties named benchmark families, exact commands, result tables, ablations, operational metrics, public-claim gates, and release-safety evidence into one reproducible bundle.

## Human Surface

- reviewers can run one documented benchmark sequence, inspect one paper result table, and see exactly which claims are allowed, blocked, or supporting-only.

## Agent Surface

- external agents can consume a stable release-freeze manifest and verify benchmark relevance, run completeness, public-claim posture, and reproducibility without scraping prose.

## Intelligence Source

- 15U baseline and ablation artifacts
- 15V graph loader and subgraph provenance artifacts
- 15W temporal and weak-label claim artifacts
- 15X environment scorecards
- 15Y paper benchmark runbook
- 15Z public-surface and cleanup reports
- benchmark truth gates, release-safety scans, demo bundles, and run summaries

## Fallback Rule

- if a public benchmark is unavailable, login-gated, licensing-unclear, too expensive for the local release profile, or not yet supported by the relevant loader, Relaytic records the reason and excludes it from hard claims instead of substituting a weaker benchmark silently.

## Required Outputs

- `paper_release_freeze_manifest.json`
- `aml_relevant_benchmark_catalog.json`
- `paper_benchmark_runbook.md`
- `paper_result_table.json`
- `paper_claim_boundary_report.json`
- `reproducibility_attestation.json`
- `release_attention_pack_manifest.json`

## Acceptance Criteria

1. The relevant benchmark catalog includes at least one transaction-fraud temporal track, one graph AML track, one subgraph or synthetic-bank-graph AML track, and one generic supporting structured-data track, each labeled as `dev`, `holdout`, `paper`, `proxy`, or `blocked`.
2. The paper result table includes model metrics, operational metrics, ablation posture, environment score, and public-claim status instead of reporting only AUROC or leaderboard-style scores.
3. Every public-facing claim in the release bundle is backed by a claim-boundary entry that cites the exact artifact path and explains whether the claim is hard, supporting-only, or blocked.
4. The reproducibility attestation records commands, dataset source posture, dependency/profile posture, host assumptions, runtime budget, and release-safety scan state.
5. A clean local rerun can regenerate the release-freeze manifest and either reproduce the reported table or emit a deterministic blocked-rerun reason.

## Required Verification

- relevant benchmark catalog schema test
- paper result table regression
- public-claim boundary regression
- reproducibility attestation regression
- release-freeze command smoke test

## Implementation Notes

- introduced `src/relaytic/release_safety/paper_freeze.py` for deterministic paper/release freeze pack generation
- added `relaytic release-safety paper-freeze` so a clean local rerun can regenerate the freeze artifacts or preserve deterministic blocked-claim reasons
- materialized the Slice 15Z-R freeze pack under `docs/reports/`
- froze hard AML performance claims as blocked until a true paper/holdout track has numeric evidence, passing environment scorecards, passing claim gates, and clean release safety
- added `tests/test_cli_slice15zr.py` coverage for catalog coverage, result-table shape, claim boundaries, reproducibility attestation, and command smoke
