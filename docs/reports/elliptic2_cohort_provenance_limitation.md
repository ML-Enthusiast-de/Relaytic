# Elliptic2 Cohort Provenance Limitation

## Status

The underlying upstream-provenance gap remains unresolved. It is no longer
treated as a manuscript release blocker because the manuscript is restricted
to an explicitly non-comparable, pinned-artifact context claim.

The exact transformation from the published or current Elliptic2 labeled core
to the pinned RevTrack-evaluable table cannot be reconstructed from this
repository. No join, filter, deduplication, missing-value, or exclusion rule is
asserted without evidence.

## Verified Count States

Three distinct states are currently documented:

| State | Rows or subgraphs | Positive or suspicious cases | Evidence |
|---|---:|---:|---|
| Current audited Elliptic2 core | 121,810 | 2,763 | `docs/reports/elliptic2_schema_overlap_audit.json` |
| RevTrack paper cohort | 121,810 | 2,718 | Song et al. (2024), Section 5 and Table 1 context |
| Pinned RevTrack-evaluable table | 110,902 | 2,578 | `docs/reports/elliptic2_modern_reference_contract.json` |

The evaluable table has the following internally consistent split counts:

| Split | Rows | Positives |
|---|---:|---:|
| `TRN` | 88,738 | 2,054 |
| `VAL` | 11,059 | 252 |
| `TST` | 11,105 | 272 |
| Total | 110,902 | 2,578 |

The row total is `88,738 + 11,059 + 11,105 = 110,902`. The positive total is
`2,054 + 252 + 272 = 2,578`.

## Repository Evidence Reviewed

Source and execution code:

- `src/relaytic/release_safety/elliptic2_recovery.py`
- `src/relaytic/release_safety/elliptic2_competitive.py`
- `src/relaytic/release_safety/elliptic2_reference_parity.py`
- `src/relaytic/release_safety/hard_graph_tracks.py`
- `src/relaytic/release_safety/paper_release.py`
- `src/relaytic/release_safety/paper_release_integrity.py`
- `src/relaytic/release_safety/paper_table_generator.py`

Committed evidence and protocol records:

- `docs/reports/elliptic2_schema_overlap_audit.json`
- `docs/reports/elliptic2_modern_reference_contract.json`
- `docs/reports/elliptic2_protocol_audit.json`
- `docs/reports/elliptic2_context_pilot_result.json`
- `docs/reports/elliptic2_revclassify_reference_scorecard.json`
- `docs/reports/elliptic2_repeated_seed_scorecard.json`
- `docs/reports/elliptic2_split_robustness_report.json`
- `docs/reports/elliptic2_evaluable_cohort_reconciliation.json`
- `docs/reports/elliptic2_entity_disjoint_split_report.json`
- `docs/reports/elliptic2_reference_parity_gate.json`
- `docs/reports/paper_p24_artifact_conflict_audit.json`

Documentation, plans, and tests:

- `docs/paper_benchmark_runbook.md`
- `docs/specs/aml_benchmark_pack.md`
- `docs/build_slices/phase_paper_track.md`
- `RELAYTIC_BUILD_MASTER.md`
- `RELAYTIC_SLICING_PLAN.md`
- `IMPLEMENTATION_STATUS.md`
- `tests/test_paper_track_p8a.py`
- `tests/test_paper_track_p8b.py`
- `tests/test_paper_track_p8c.py`

The tracked and ignored repository trees were searched for the original
Elliptic2 CSV files, the pinned `data_df.pkl`, RevTrack preprocessing code,
component mappings, and row-exclusion manifests. None of those source assets is
present. Git history for commits `1a8d8b7`, `b21ae9f`, and `38b7c2f` contains
the Relaytic audit and evaluation code but not the upstream table-construction
pipeline.

## Earliest Untraceable Step

Relaytic receives the RevTrack table as an already constructed external
artifact named `data_df.pkl`. The recovery code verifies its SHA-256 value
`2baa712b67382aeade8d5e72dd07ddbffb1029b359a048c80a2300a3e3abc220`
and loads it with `pandas.read_pickle`. It does not construct that table.

The pinned table contains partition-local identifiers such as `TRN0` and does
not expose `ccId`, `component_id`, or another direct identifier from the
current Elliptic2 core. Consequently, the repository cannot identify which
10,908 current-core rows are absent, why 185 current-core positives are absent,
or how the 2,718-positive RevTrack paper label state relates to either local
state.

## Information Required To Resolve The Blocker

Resolution requires:

1. The exact Elliptic2 source release and checksums used to construct the pinned
   RevTrack table.
2. The RevTrack preprocessing implementation at commit
   `f2111c8a1bafd84ebaa5a04e5caca8f1f0ed7ac0`, including every join, filter,
   cycle-removal, missing-value, deduplication, and exclusion rule.
3. A stable mapping from each `data_df.pkl` row or `subg` value to the original
   Elliptic2 `ccId`.
4. A row-level exclusion audit grouped by reason.
5. The label snapshot or correction history that explains 2,718 suspicious
   cases in the RevTrack paper versus 2,763 in the audited current core.
6. A clean reconstruction that reproduces the pinned table hash and the
   110,902/2,578 totals from identified raw inputs.

Until those materials are available, the manuscript may describe the pinned
artifact as a distinct local evaluation state and may report its repeated
result only as non-comparable context. It must not explain the count difference
as preprocessing, claim a row-level relationship to the current core, or imply
cohort or reference-method equivalence.
