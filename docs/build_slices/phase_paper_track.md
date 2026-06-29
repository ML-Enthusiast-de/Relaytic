# Paper Track P0-P15 - Relaytic-AML arXiv benchmark path

## Status

P0 through P16 implemented. A triggerable paper-strengthening follow-on lives in `docs/build_slices/phase_paper_strengthening.md`; if the user triggers Stage 2, Paper Track P17 is next, otherwise Slice 16A is the next academy target.

## Intent

Paper Track P0 through P16 is the mandatory path plus first strengthening stage between Slice 15Z-R and Slice 16A.

Slice 15Z-R froze a safe release pack, but it intentionally blocks hard AML and SOTA claims until real paper evidence exists. This track turns that frozen, honest state into a clean repo, relevant benchmark suite, reproducible result table, claim-linted draft, clean-clone dry run, claim-safe paper release pack, final arXiv source release candidate, and measured system-evaluation proof pack. The final upload still requires local PDF review, bibliography/source-policy confirmation, and clean tag-target proof.

The P17-P21 strengthening track is not part of the original mandatory bridge. It is a user-triggered follow-on for adding governance ablations, formal invariants, optional hosted-detector workflow evidence, visual polish, and final preflight before a stronger arXiv or systems/evaluation submission.

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
10. **P8 - AMLSim and Elliptic2 blocked-or-supported track** - implemented
   Decide whether synthetic-bank and subgraph AML tracks are runnable for the first paper or explicitly blocked with exact reasons.
11. **P8-A - Elliptic2 modern-benchmark recovery pilot** - implemented
   Acquire and audit official Elliptic2/RevTrack evidence outside git, freeze protocol discrepancies, and run a strictly exploratory modern-context pilot.
12. **P8-B - Elliptic2 competitive and robustness suite** - implemented
   Challenge the recovered pilot against RevClassify, repeated seeds, validation-only search, and a row-order-independent robustness split before paper promotion.
13. **P8-C - Modern subgraph reference parity and leakage-resistant cohort protocol** - implemented
    Close or explicitly reject the gap to modern RevClassify evidence, reconcile the official-core versus RevTrack-evaluable cohort boundary, and require a stronger identity-aware split before the performance story advances.
14. **P8-D - Paper thesis narrowing and alternative evidence decision** - implemented
    Decide whether to reprovision faithful modern-subgraph parity or narrow the paper around claim-gated AML evaluation with Elliptic2 as supporting context.
15. **P9 - Operational AML evaluation layer** - implemented
    Add review-budget, analyst-hour, false-positive reduction, case-packet completeness, and operational claim guards to paper rows.
16. **P10 - Reproducible paper table generator** - implemented
    Generate all paper tables from run artifacts, not hand-maintained numbers.
17. **P11 - Paper draft and figure pack** - implemented
    Draft the arXiv paper and generate figures from artifacts or clearly mark schematic figures.
18. **P12 - External dry run and clean-clone proof** - implemented
    Reproduce the install, paper-smoke benchmark, table generation, claim lint, and leak scan from a clean clone.
19. **P13 - arXiv release and attention pack** - implemented
    Release only after P10 through P12 pass; otherwise emit a release blocker and schedule repair.
20. **P14 - final arXiv source bundle and clean release candidate** - implemented
    Convert the claim-safe Markdown paper pack into a LaTeX source tree, convert figures into accepted arXiv graphic formats, audit citations and package hygiene, and leave upload blocked until human TeX/PDF inspection and clean release gates are complete.
21. **P15 - measured system-evaluation proof pack** - implemented
    Exercise guide onboarding, partial-run recovery, redacted external-agent handoff, local-LLM advisory boundaries, interoperability discovery, and paper claim gates before regenerating release artifacts.

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

P8 added:

- `docs/reports/amlsim_generation_manifest.json`
- `docs/reports/amlsim_typology_manifest.json`
- `docs/reports/elliptic2_subgraph_access_report.json`
- `docs/reports/subgraph_benchmark_blocker_report.json`
- `src/relaytic/release_safety/hard_graph_tracks.py`
- `relaytic release-safety hard-graph-tracks --format json`
- `tests/test_paper_track_p8.py`

P8 recorded both current hard graph tracks as blocked from performance claims. AMLSim remains a future reproducible synthetic typology/workflow proxy; it cannot replace real subgraph evidence. P8-A superseded Elliptic2's access-blocked state, P8-B tested the recovered path competitively, P8-C recorded the reference-parity/cohort blocker, and P8-D accepted thesis narrowing so P9 can proceed without treating Elliptic2 as a performance contribution.

P8-A added:

- `docs/reports/elliptic2_recovery_manifest.json`
- `docs/reports/elliptic2_schema_overlap_audit.json`
- `docs/reports/elliptic2_protocol_audit.json`
- `docs/reports/elliptic2_modern_reference_contract.json`
- `docs/reports/elliptic2_context_pilot_result.json`
- `docs/reports/elliptic2_recovery_gate.json`
- `src/relaytic/release_safety/elliptic2_recovery.py`
- `relaytic release-safety elliptic2-recovery --core-data-dir <external-local-core-dir> --revtrack-dir <external-local-revtrack-dir> --prepare-selected-embeddings --run-pilot --hash-large-assets --format json`
- `tests/test_paper_track_p8a.py`

P8-A audits the official labeled Elliptic2 core over 121,810 subgraphs and pins the ICAIF 2024 RevTrack/RevClassify reference. It records a nontrivial comparability issue: the original paper states a random `80:10:10` split while its public preprocessor assigns subgraphs by insertion-order modulo. After deriving a CPU-bounded, hash-audited selected-node cache from official RevTrack embeddings, the predeclared context pilot reports test `PR-AUC=0.935255`, versus `0.027773` for structure-only role counts. This is promising modern evidence, not yet a publishable Relaytic result, because it consumes official RevTrack preprocessing and has not passed repeated-seed or alternate-split proof.

P8-B added:

- `docs/reports/elliptic2_competitive_budget_contract.json`
- `docs/reports/elliptic2_revclassify_reference_scorecard.json`
- `docs/reports/elliptic2_relaytic_candidate_search_trace.json`
- `docs/reports/elliptic2_repeated_seed_scorecard.json`
- `docs/reports/elliptic2_split_robustness_report.json`
- `docs/reports/elliptic2_publishability_gate.json`
- `src/relaytic/release_safety/elliptic2_competitive.py`
- `relaytic release-safety elliptic2-competitive --revtrack-dir <external-local-revtrack-dir> --budget-tier competitive --run-suite --format json`
- `tests/test_paper_track_p8b.py`

P8-B rigorously records the published full-shot reference (`RevClassifyBP PR-AUC=0.972`, `RevClassifyDS PR-AUC=0.974`) and documents that the pinned public repository does not distribute classification checkpoints and reports single-V100 training. It also discovers a material cohort boundary: the pinned RevTrack table evaluates 110,902 rows and 2,578 positives versus the audited current official core of 121,810 rows and 2,763 suspicious labels. Under a validation-only three-candidate CPU budget, pooled moments are selected and produce repeated official test `PR-AUC=0.943240 +/- 0.000882` and deterministic content-hash test `PR-AUC=0.929669 +/- 0.000538`. The hash partition passes row-order-independence, but the result remains below RevClassifyDS, consumes official preprocessing/embeddings, follows an already exposed official test partition, and does not prove entity-disjoint generalization. P8-B permits a supporting modern-context row only; P8-C now confirms it cannot become a central parity claim in the current environment.

P8-C added:

- `docs/reports/elliptic2_neural_reference_parity_contract.json`
- `docs/reports/elliptic2_evaluable_cohort_reconciliation.json`
- `docs/reports/elliptic2_entity_disjoint_split_report.json`
- `docs/reports/elliptic2_neural_candidate_scorecard.json`
- `docs/reports/elliptic2_reference_parity_gate.json`
- `src/relaytic/release_safety/elliptic2_reference_parity.py`
- `relaytic release-safety elliptic2-reference-parity --revtrack-dir <external-local-revtrack-dir> --run-neural --format json`
- `tests/test_paper_track_p8c.py`

P8-C requested faithful RevClassify parity execution and blocked it with exact evidence: the local environment is CPU-only, lacks the official Lightning/Hydra/OmegaConf/TorchMetrics stack, and the pinned repository does not distribute RevClassify classification checkpoints. It narrows every modern-subgraph claim to the RevTrack-evaluable table because current-core equivalence is not proven (`110902/121810` rows, `2578/2763` positives). Its strict entity-disjoint component split is degenerate: `110889/110902` rows collapse into the largest identity component, leaving only 7 validation rows and 6 test rows under a zero-overlap split. P8-C therefore keeps P8-B as supporting context only and blocked P9 until P8-D recorded the accepted thesis boundary.

P8-D added:

- `docs/reports/paper_p8d_thesis_decision.json`
- `docs/reports/paper_p8d_evidence_role_matrix.json`
- `docs/reports/paper_p8d_reprovisioning_decision.json`
- `docs/reports/paper_p8d_claim_rewrite_plan.json`
- `src/relaytic/release_safety/paper_thesis_decision.py`
- `relaytic release-safety paper-thesis-decision --format json`
- `tests/test_paper_track_p8d.py`

P8-D accepts the narrowed first-paper route: Relaytic-AML is framed as a claim-gated AML evaluation environment with operational evidence, not as a modern subgraph SOTA model paper. P8-B remains supporting modern-context evidence only, P8-C becomes the limitation and claim-firewall evidence, Elliptic2 is excluded from performance-contribution claims, and faithful RevClassify reprovisioning is preserved as a later extension instead of blocking P9.

P9 added:

- `docs/reports/paper_operational_metric_table.json`
- `docs/reports/paper_review_budget_curve.json`
- `docs/reports/paper_case_packet_completeness_report.json`
- `docs/reports/paper_operational_claim_guard.json`
- `src/relaytic/release_safety/paper_operational_metrics.py`
- `relaytic release-safety paper-operational-metrics --format json`
- `tests/test_paper_track_p9.py`

P9 materializes the operational layer promised by the narrowed thesis. PaySim and Elliptic supporting rows now include review-budget metrics, prevalence-matched false-positive burden proxies, analyst-hour assumptions, and artifact citations. Aggregate case packets are still missing, so the claim guard blocks hard business-value and headline operational claims while allowing P10 table generation to proceed.

P10 added:

- `docs/reports/paper_result_table_final.json`
- `docs/reports/paper_table_provenance.json`
- `docs/reports/paper_reproduction_commands.md`
- `docs/reports/paper_metric_cell_audit.json`
- `docs/reports/paper_publishability_matrix.json`
- `src/relaytic/release_safety/paper_table_generator.py`
- `relaytic release-safety paper-tables --format json`
- `tests/test_paper_track_p10.py`

P10 turns the paper-track evidence into reproducible supporting tables. Every numeric metric cell now carries dataset, split, command, run-directory, artifact, claim-state, budget-tier, leakage-posture, and publishability-gate provenance. The metric-cell audit passes and P11 is unblocked, but the publishability matrix keeps hard AML, headline, SOTA, and business-value claims blocked.

P11 added:

- `docs/paper/relaytic_aml_draft.md`
- `docs/paper/figures/figure_manifest.json`
- `docs/paper/figures/figure_1_claim_gate_flow.svg`
- `docs/paper/figures/figure_2_supporting_pr_auc.svg`
- `docs/paper/figures/figure_3_review_budget.svg`
- `docs/paper/figures/figure_4_publishability_matrix.svg`
- `docs/reports/paper_claim_lint_report.json`
- `docs/reports/paper_limitations_matrix.json`
- `src/relaytic/release_safety/paper_draft.py`
- `relaytic release-safety paper-draft --format json`
- `tests/test_paper_track_p11.py`

P11 renders the first Relaytic-AML draft directly from the P10 evidence pack. The draft contains abstract, introduction, related work, method, benchmarks, results, limitations, and reproducibility appendix sections; it cites audited `paper-cell:*` metric references; it names every generated limitation; and its claim lint passes. Hard AML, headline, SOTA, RevClassify parity, graph-neural superiority, and hard business-value claims remain blocked before P12.

P12 added:

- `docs/reports/paper_clean_clone_checklist.md`
- `docs/reports/paper_external_dry_run_report.json`
- `docs/reports/paper_clean_clone_install_report.json`
- `docs/reports/paper_reproduction_failure_report.json`
- `docs/reports/paper_release_go_no_go.json`
- `src/relaytic/release_safety/paper_dry_run.py`
- `relaytic release-safety paper-dry-run --run-isolated-install --format json`
- `tests/test_paper_track_p12.py`

P12 proves the external paper-smoke path. It documents the clean-clone install checklist, verifies the install contract, supports an optional temp isolated full-profile install probe, regenerates the P10 table pack and P11 draft pack, records leak-scan status, and emits a fail-closed go/no-go report. P13 is unblocked only in claim-safe evaluation-environment mode; hard AML, headline, SOTA, RevClassify parity, graph-neural superiority, and hard business-value claims remain blocked.

P13 added:

- `docs/reports/paper_release_manifest.json`
- `docs/reports/paper_arxiv_submission_checklist.md`
- `docs/reports/paper_attention_pack.md`
- `docs/reports/paper_public_claims_allowed.json`
- `docs/paper/relaytic_aml_arxiv_draft.md`
- `docs/paper/references.bib`
- `docs/paper/tables/table_manifest.json`
- `docs/paper/tables/table_1_evidence_summary.md`
- `docs/paper/tables/table_2_claim_gate_matrix.md`
- `docs/paper/tables/table_3_release_artifact_set.md`
- `src/relaytic/release_safety/paper_release.py`
- `relaytic release-safety paper-release --format json`
- `tests/test_paper_track_p13.py`

P13 produces the claim-safe Markdown draft, citable references, generated paper tables, release manifest, public attention pack, submission checklist, and allowed-public-claims report from the P10-P12 gated artifact set. It writes a release tag plan but does not create or push tags automatically. Public wording is allowed only in evaluation-environment mode; hard AML, headline, SOTA, RevClassify parity, graph-neural superiority, production-ready, and hard business-value claims remain blocked.

## Completed Source and System Evidence

### Paper Track P14 - final arXiv source bundle and clean release candidate

P14 converts the P13 Markdown draft into a deterministic arXiv-compatible source package without changing the claim contract. It produces LaTeX source, converted PDF figure files for the selected pdfLaTeX processor, author-metadata placeholders, a submission-package audit, and a release-candidate tag plan. A follow-up paper-excellence pass sharpened the paper around evidence cells, deterministic claim gates, explicit research questions, agentic ML reliability, and company-facing evaluation-lab utility. P14 remains blocked if any citation key is missing, any figure cannot be included by the chosen processor, or any public surface adds hard AML, headline, SOTA, RevClassify parity, graph-neural superiority, production-ready, or hard business-value claims.

P14 added:

- `docs/paper/arxiv_src/`
- `docs/reports/paper_arxiv_source_manifest.json`
- `docs/reports/paper_submission_package_audit.json`
- `docs/reports/paper_release_candidate_checklist.md`
- `src/relaytic/release_safety/paper_arxiv_source.py`
- `relaytic release-safety paper-arxiv-source --format json`
- `tests/test_paper_track_p14.py`

Implemented acceptance:

1. The arXiv source package contains a top-level TeX source, bibliography file, and converted PDF figures with case-matching file references.
2. A deterministic citation audit confirms every in-text citation has a BibTeX entry and no BibTeX entry used by the paper is malformed.
3. The submission package audit confirms no local machine paths, external private data paths, secrets, `.env` files, or virtual environments are referenced.
4. The final checklist records that `git status --short` is empty at the release-candidate tag target.
5. `paper_arxiv_source_manifest.json` marks source release-candidate status ready, keeps hard/headline claims blocked, and keeps `arxiv_upload_ready` false until human TeX/PDF inspection, source-policy, and clean release gates pass.

### Paper Track P15 - measured system-evaluation proof pack

P15 converts the paper's system-behavior claims into deterministic protocol evidence. It checks whether a new user or external agent can discover the current state through the guide surface, recover from a partial run, receive a rowless and redacted context pack, inspect available interoperability tools, understand optional local-LLM boundaries, and see which paper claims are allowed or blocked. The result strengthens the architecture and methodology sections without pretending that the project has run a human-subject study or production deployment.

P15 added:

- `src/relaytic/release_safety/paper_system_eval.py`
- `relaytic release-safety paper-system-eval --format json`
- `docs/reports/paper_system_behavior_eval.json`
- `docs/reports/paper_system_task_eval.json`
- `docs/reports/paper_agent_handoff_eval.json`
- `docs/reports/paper_no_lost_user_eval.json`
- `docs/reports/paper_claim_gate_case_studies.json`
- `docs/reports/paper_system_eval_manifest.json`
- `docs/reports/paper_system_eval_summary.md`
- `tests/test_paper_track_p15.py`

Implemented acceptance:

1. All required deterministic protocol checks pass in the committed report set, including the reader/agent task suite for repository navigation, metric provenance, claim-boundary recovery, partial-run recovery, and rowless handoff.
2. The pack fails closed when required P11/P12/P13 claim-gate inputs are absent.
3. The handoff evidence is rowless and redacted, and committed P15 reports avoid raw rows, secrets, and private local paths.
4. P13 consumes the P15 report before rendering reader-facing measured-system-evaluation text.
5. The current evidence remains protocol-level only; human-study, analyst-hour, production, hard AML, headline, and SOTA claims remain blocked.

Follow-on:

- `docs/build_slices/phase_paper_strengthening.md` records P16 as implemented and P17-P21 as the remaining optional paper-strengthening path. P17 should only start when the user triggers Stage 2.
