# Relaytic-AML Paper Benchmark Runbook

This runbook defines the public benchmark path reviewers should expect before Relaytic-AML makes paper-facing claims.

The current public-safe AML review-queue demo is demo-only. Slice 15Z-R now emits the release-freeze pack, and P9 emits the operational metric pack. Hard AML performance and business-value claims remain blocked until true paper/holdout evidence, complete operational assumptions, passing environment scorecards, passing claim gates, and clean release safety all exist.

Generated freeze artifacts live under `docs/reports/`:

- `paper_release_freeze_manifest.json`
- `aml_relevant_benchmark_catalog.json`
- `paper_benchmark_runbook.md`
- `paper_result_table.json`
- `paper_claim_boundary_report.json`
- `reproducibility_attestation.json`
- `release_attention_pack_manifest.json`

Current paper-track baseline artifacts also live under `docs/reports/`:

- `paysim_benchmark_manifest.json`
- `elliptic_graph_loader_manifest.json`
- `paper_baseline_suite_manifest.json`
- `paper_tabular_baseline_table.json`
- `paper_benchmark_budget_contract.json`
- `paper_leakage_safe_feature_report.json`
- `paper_publishability_gate.json`
- `paysim_competitive_benchmark_manifest.json`
- `paysim_competitive_baseline_table.json`
- `paysim_competitive_search_trace.json`
- `paysim_leakage_safe_feature_report.json`
- `paysim_publishability_gate.json`
- `paper_graph_baseline_manifest.json`
- `paper_graph_feature_table.json`
- `paper_graph_model_shadow_scorecard.json`
- `paper_graph_baseline_fallback_report.json`
- `paper_graph_budget_contract.json`
- `paper_graph_competitive_search_trace.json`
- `paper_graph_publishability_gate.json`
- `amlsim_generation_manifest.json`
- `amlsim_typology_manifest.json`
- `elliptic2_subgraph_access_report.json`
- `subgraph_benchmark_blocker_report.json`
- `elliptic2_recovery_manifest.json`
- `elliptic2_schema_overlap_audit.json`
- `elliptic2_protocol_audit.json`
- `elliptic2_modern_reference_contract.json`
- `elliptic2_context_pilot_result.json`
- `elliptic2_recovery_gate.json`
- `elliptic2_competitive_budget_contract.json`
- `elliptic2_revclassify_reference_scorecard.json`
- `elliptic2_relaytic_candidate_search_trace.json`
- `elliptic2_repeated_seed_scorecard.json`
- `elliptic2_split_robustness_report.json`
- `elliptic2_publishability_gate.json`
- `elliptic2_neural_reference_parity_contract.json`
- `elliptic2_evaluable_cohort_reconciliation.json`
- `elliptic2_entity_disjoint_split_report.json`
- `elliptic2_neural_candidate_scorecard.json`
- `elliptic2_reference_parity_gate.json`
- `paper_p8d_thesis_decision.json`
- `paper_p8d_evidence_role_matrix.json`
- `paper_p8d_reprovisioning_decision.json`
- `paper_p8d_claim_rewrite_plan.json`
- `paper_operational_metric_table.json`
- `paper_review_budget_curve.json`
- `paper_case_packet_completeness_report.json`
- `paper_operational_claim_guard.json`
- `paper_result_table_final.json`
- `paper_table_provenance.json`
- `paper_reproduction_commands.md`
- `paper_metric_cell_audit.json`
- `paper_publishability_matrix.json`

## Benchmark Families

| Family | Current role | Claim status | Expected evidence |
| --- | --- | --- | --- |
| PaySim-style transaction fraud | Temporal transaction-fraud evidence | `dev` or `proxy` until holdout and claim gates pass | `aml_benchmark_manifest.json`, `aml_temporal_benchmark_claim_report.json`, `aml_time_window_scorecard.json`, `aml_environment_scorecard.json`, `paper_operational_metric_table.json` |
| Elliptic-style graph AML | Flattened and raw-graph AML evidence | `dev`, `proxy`, or `holdout` depending on source and graph-loader posture | `aml_graph_loader_manifest.json`, `aml_graph_provenance_report.json`, `aml_graph_claim_scope.json`, `aml_benchmark_relevance_scorecard.json`, `paper_review_budget_curve.json` |
| Elliptic2-style subgraph AML | Modern subgraph context and limitation evidence | supporting-only after P8-D thesis narrowing; no performance contribution, headline, SOTA, full-core, or reference-parity claim | `elliptic2_publishability_gate.json`, `elliptic2_reference_parity_gate.json`, `paper_p8d_thesis_decision.json`, `paper_result_table_final.json` |
| AMLSim-style synthetic bank graph | Synthetic bank-network evidence | `proxy` until reproducible generation and benchmark relevance are frozen | `aml_public_graph_benchmark_catalog.json`, `entity_graph_profile.json`, `subgraph_risk_report.json`, `case_packet.json` |
| Generic structured-data benchmark pack | Supporting breadth evidence | supporting-only, not the flagship AML claim | `paper_benchmark_manifest.json`, `paper_benchmark_table.json`, `benchmark_release_gate.json` |

Status labels:

- `dev`: useful for engineering, not final public evidence.
- `holdout`: held-out partition evidence, potentially stronger if claim gates pass.
- `paper`: paper-ready only after the release-freeze pack passes.
- `proxy`: relevant shape but not enough for a hard real-world AML claim.
- `blocked`: excluded from hard claims with a recorded reason.

## Minimum Command Sequence

Demo-only path:

```powershell
relaytic demo aml-review-queue --run-dir artifacts\relaytic_aml_demo --format json
relaytic show --run-dir artifacts\relaytic_aml_demo --format json
relaytic aml environment --run-dir artifacts\relaytic_aml_demo --format json
```

Benchmark path for a local AML dataset:

```powershell
relaytic run --run-dir artifacts\aml_benchmark_run --data-path <aml_dataset.csv> --text "Build an AML transaction-monitoring model and keep benchmark claims guarded." --format json
relaytic benchmark run --run-dir artifacts\aml_benchmark_run --data-path <aml_dataset.csv> --format json
relaytic aml baselines --run-dir artifacts\aml_benchmark_run --format json
relaytic aml temporal --run-dir artifacts\aml_benchmark_run --format json
relaytic aml environment --run-dir artifacts\aml_benchmark_run --format json
relaytic guide export-context --run-dir artifacts\aml_benchmark_run --audience external-llm --format json
```

Raw graph or subgraph path when graph files are available:

```powershell
relaytic aml graph-loader --run-dir artifacts\aml_benchmark_run --graph-path <graph_bundle_or_subgraph_pack> --format json
relaytic aml environment --run-dir artifacts\aml_benchmark_run --format json
```

Release hygiene before public use:

```powershell
relaytic release-safety paysim-benchmark --format json
relaytic release-safety elliptic-graph --format json
relaytic release-safety tabular-baselines --budget-tier baseline --run-optional --format json
relaytic release-safety paysim-competitive --budget-tier competitive --run-optional --format json
relaytic release-safety graph-baselines --budget-tier competitive --run-optional --format json
relaytic release-safety hard-graph-tracks --format json
relaytic release-safety elliptic2-recovery --core-data-dir <external-local-core-dir> --revtrack-dir <external-local-revtrack-dir> --prepare-selected-embeddings --run-pilot --hash-large-assets --format json
relaytic release-safety elliptic2-competitive --revtrack-dir <external-local-revtrack-dir> --budget-tier competitive --run-suite --format json
relaytic release-safety elliptic2-reference-parity --revtrack-dir <external-local-revtrack-dir> --run-neural --format json
relaytic release-safety paper-thesis-decision --format json
relaytic release-safety paper-operational-metrics --format json
relaytic release-safety paper-tables --format json
relaytic release-safety paper-freeze --format json
relaytic release-safety scan --format json
relaytic doctor --expected-profile full --format json
```

## Expected Artifacts

The release-freeze pack should cite these when available:

- `manifest.json`
- `run_summary.json`
- `data_copy_manifest.json`
- `benchmark_truth_precheck.json`
- `benchmark_release_gate.json`
- `paper_claim_guard_report.json`
- `aml_benchmark_manifest.json`
- `aml_holdout_claim_report.json`
- `aml_public_claim_guard.json`
- `aml_failure_report.json`
- `aml_business_value_report.json`
- `review_capacity_metric_report.json`
- `operational_metric_guard.json`
- `aml_baseline_matrix.json`
- `aml_ablation_matrix.json`
- `aml_benchmark_relevance_scorecard.json`
- `aml_graph_loader_manifest.json`
- `aml_graph_provenance_report.json`
- `aml_subgraph_task_manifest.json`
- `aml_graph_claim_scope.json`
- `aml_public_graph_benchmark_catalog.json`
- `aml_temporal_benchmark_claim_report.json`
- `aml_environment_scorecard.json`
- `aml_workflow_task_matrix.json`
- `aml_benchmark_environment_scorecard.json`
- `paysim_benchmark_manifest.json`
- `paysim_temporal_split_report.json`
- `elliptic_graph_loader_manifest.json`
- `elliptic_temporal_split_report.json`
- `paper_baseline_suite_manifest.json`
- `paper_tabular_baseline_table.json`
- `paper_baseline_version_matrix.json`
- `paper_leakage_safe_feature_report.json`
- `paper_publishability_gate.json`
- `paysim_competitive_benchmark_manifest.json`
- `paysim_competitive_budget_contract.json`
- `paysim_competitive_search_trace.json`
- `paysim_leakage_safe_feature_report.json`
- `paysim_competitive_baseline_table.json`
- `paysim_publishability_gate.json`
- `paper_graph_baseline_manifest.json`
- `paper_graph_feature_table.json`
- `paper_graph_model_shadow_scorecard.json`
- `paper_graph_baseline_fallback_report.json`
- `paper_graph_budget_contract.json`
- `paper_graph_competitive_search_trace.json`
- `paper_graph_publishability_gate.json`
- `amlsim_generation_manifest.json`
- `amlsim_typology_manifest.json`
- `elliptic2_subgraph_access_report.json`
- `subgraph_benchmark_blocker_report.json`
- `elliptic2_recovery_manifest.json`
- `elliptic2_schema_overlap_audit.json`
- `elliptic2_protocol_audit.json`
- `elliptic2_modern_reference_contract.json`
- `elliptic2_context_pilot_result.json`
- `elliptic2_recovery_gate.json`
- `elliptic2_competitive_budget_contract.json`
- `elliptic2_revclassify_reference_scorecard.json`
- `elliptic2_relaytic_candidate_search_trace.json`
- `elliptic2_repeated_seed_scorecard.json`
- `elliptic2_split_robustness_report.json`
- `elliptic2_publishability_gate.json`
- `elliptic2_neural_reference_parity_contract.json`
- `elliptic2_evaluable_cohort_reconciliation.json`
- `elliptic2_entity_disjoint_split_report.json`
- `elliptic2_neural_candidate_scorecard.json`
- `elliptic2_reference_parity_gate.json`
- `paper_p8d_thesis_decision.json`
- `paper_p8d_evidence_role_matrix.json`
- `paper_p8d_reprovisioning_decision.json`
- `paper_p8d_claim_rewrite_plan.json`
- `paper_operational_metric_table.json`
- `paper_review_budget_curve.json`
- `paper_case_packet_completeness_report.json`
- `paper_operational_claim_guard.json`
- `paper_result_table_final.json`
- `paper_table_provenance.json`
- `paper_reproduction_commands.md`
- `paper_metric_cell_audit.json`
- `paper_publishability_matrix.json`
- `release_safety_scan.json`

## Blocked-Claim Conditions

Do not claim paper-ready AML superiority when any of these are true:

- `benchmark_truth_precheck.json` says ranking is unsafe.
- `benchmark_release_gate.json` blocks public citation.
- `paper_claim_guard_report.json` or `aml_public_claim_guard.json` contains blockers.
- `aml_benchmark_relevance_scorecard.json` labels the family `proxy` or `blocked`.
- `aml_temporal_benchmark_claim_report.json` blocks temporal claims because delayed labels, positive-unlabeled posture, leakage, or threshold drift are unresolved.
- `aml_environment_scorecard.json` reports `partial`, `fail`, or model/environment disagreement.
- `aml_benchmark_environment_scorecard.json` reports incomplete reproducibility, claim safety, or benchmark relevance.
- `paper_publishability_gate.json` blocks a headline performance claim because competitive or release-budget proof has not passed.
- `paysim_publishability_gate.json` does not admit even a supporting PaySim paper-table candidate, or is cited as permitting real-world/headline AML performance.
- `paper_graph_publishability_gate.json` is cited as permitting graph-neural, SOTA, headline, or hard AML claims; P7 currently admits only a supporting graph-feature row.
- `subgraph_benchmark_blocker_report.json` labels Elliptic2 or AMLSim `blocked` without a later recovery artifact; P8-A now supersedes Elliptic2's access blocker only to `modern_context_pilot_only`, while AMLSim remains blocked.
- `elliptic2_recovery_gate.json` is only `pass_pilot_only`; it must be read alongside the later P8-B gate and never cited by itself as permitting a paper result.
- `elliptic2_publishability_gate.json` permits only supporting modern-context wording: P8-B is stable under repeated seeds and a row-order-independent content-hash partition, but it remains below reported full-shot `RevClassifyDS PR-AUC=0.974`, consumes official RevTrack preprocessing/embeddings, does not prove full-core cohort equivalence, and does not establish entity-disjoint generalization.
- `elliptic2_reference_parity_gate.json` blocks reference-parity, SOTA, full-core, entity-disjoint, hard AML, and end-to-end Relaytic claims: P8-C requested faithful neural parity but local preconditions are missing, current-core mapping is not proven, and the strict component split is degenerate.
- `paper_p8d_thesis_decision.json` unblocks P9 only under the narrowed evaluation-environment thesis. It does not permit Elliptic2 as a primary performance contribution, modern-subgraph SOTA result, RevClassify parity result, or full-core/entity-disjoint claim.
- `paper_operational_claim_guard.json` unblocks P10 table generation only when supporting review-budget metrics exist. It does not permit hard business-value or headline operational claims while case packets, explicit nondefault analyst assumptions, or same-queue incumbent/human-baseline evidence are incomplete.
- `paper_publishability_matrix.json` reports hard or headline claims as blocked, or `paper_metric_cell_audit.json` contains metric provenance violations.
- The run used a public-safe fixture or synthetic/proxy source and has no holdout or release-freeze evidence.

## Reproducibility Record

For any paper-facing table, record:

- exact commands
- Relaytic version or commit
- Python version and install profile
- dataset family and source posture
- whether the dataset is demo, dev, holdout, paper, proxy, or blocked
- run directory
- runtime budget assumptions
- release-safety scan result
- claim-boundary artifact paths

Slice 15Z-R turned this runbook into machine-readable freeze artifacts. Treat `docs/reports/paper_claim_boundary_report.json` and `docs/reports/reproducibility_attestation.json` as the public-claim and rerun truth before publishing paper-facing language.
