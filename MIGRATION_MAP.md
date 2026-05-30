# Migration Map

This file tracks explicit compatibility boundaries while the repository continues moving toward the final Relaytic product surface.

## Public Naming

- product name: `Relaytic`
- flagship frontier edition: `Relaytic-AML`
- public package: `relaytic`
- public CLI: `relaytic`

Legacy `Corr2Surrogate` naming exists only where compatibility is still being preserved deliberately.

## Compatibility Surface

Current temporary compatibility promises:

- legacy Python imports rooted at `corr2surrogate` continue through a narrow shim
- legacy `C2S_*` environment variables may still be accepted as fallbacks in some runtime paths

These are compatibility mechanisms, not active public product surfaces.

## Preferred Environment Variables

Use:

- `RELAYTIC_CONFIG_PATH`
- `RELAYTIC_PROVIDER`
- `RELAYTIC_PROFILE`
- `RELAYTIC_MODEL`
- `RELAYTIC_ENDPOINT`
- `RELAYTIC_API_KEY`

Avoid introducing new references to:

- `C2S_CONFIG_PATH`
- `C2S_PROVIDER`
- `C2S_PROFILE`
- `C2S_MODEL`
- `C2S_ENDPOINT`
- `C2S_API_KEY`

## Module Mapping

- `src/corr2surrogate/*` -> `src/relaytic/*`
- `corr2surrogate.ui.cli` -> `relaytic.ui.cli`
- `corr2surrogate.security.git_guard` -> `relaytic.security.git_guard`

## Boundary Additions By Slice

### Slice 03

- introduced the canonical package boundary `src/relaytic/investigation/`
- introduced the public command `relaytic investigate`
- tightened compatibility wrappers so repo-local forwarding is explicit rather than accidental

### Slice 04

- introduced the canonical package boundary `src/relaytic/intake/`
- introduced the public commands `relaytic intake interpret`, `relaytic intake show`, and `relaytic intake questions`
- expanded the artifact boundary to include autonomous intake artifacts such as `autonomy_mode.json`, `clarification_queue.json`, and `assumption_log.json`

### Slice 05

- introduced the canonical package boundary `src/relaytic/planning/`
- introduced the public commands `relaytic plan create`, `relaytic plan run`, and `relaytic plan show`
- expanded the artifact boundary to include `plan.json`, `alternatives.json`, `hypotheses.json`, `experiment_priority_report.json`, and `marginal_value_of_next_experiment.json`
- established the first supported Builder-handoff boundary from planning artifacts into a same-run deterministic model build
- preserved existing compatibility promises without expanding the legacy `corr2surrogate` surface

### Slice 05A

- introduced the canonical package boundary `src/relaytic/runs/`
- introduced the canonical package boundary `src/relaytic/ingestion/staging.py`
- expanded the canonical ingestion boundary with `src/relaytic/ingestion/sources.py`
- introduced the public commands `relaytic run`, `relaytic show`, and `relaytic predict`
- introduced the public commands `relaytic source inspect` and `relaytic source materialize`
- expanded the artifact boundary to include `run_summary.json`, `reports/summary.md`, `data_copy_manifest.json`, and staged `data_copies/`
- standardized nested manifest artifact paths to POSIX-style relative paths for more stable cross-platform agent consumption
- upgraded the MVP access shell so run and prediction paths operate on immutable staged copies without persisting original absolute source paths
- expanded the supported local source boundary to include snapshot files, append-only stream files, local dataset directories, and local DuckDB sources through immutable materialization

### Slice 06

- introduced the canonical package boundary `src/relaytic/evidence/`
- introduced the public commands `relaytic evidence run` and `relaytic evidence show`
- expanded the artifact boundary to include `experiment_registry.json`, `challenger_report.json`, `ablation_report.json`, `audit_report.json`, `belief_update.json`, `leaderboard.csv`, `reports/technical_report.md`, and `reports/decision_memo.md`
- upgraded the MVP access shell so `relaytic run` now drives the evidence layer by default while preserving lower-level specialist surfaces

### Slice 07

- introduced the canonical package boundary `src/relaytic/completion/`
- introduced the public commands `relaytic status` and `relaytic completion review`
- expanded the artifact boundary to include `completion_decision.json`, `run_state.json`, `stage_timeline.json`, `mandate_evidence_review.json`, `blocking_analysis.json`, and `next_action_queue.json`
- upgraded the MVP access shell so `relaytic run` and `relaytic show` now surface an explicit governed run state rather than stopping at provisional evidence only

### Slice 08

- introduced the canonical package boundary `src/relaytic/lifecycle/`
- introduced the public commands `relaytic lifecycle review` and `relaytic lifecycle show`
- expanded the artifact boundary to include `champion_vs_candidate.json`, `recalibration_decision.json`, `retrain_decision.json`, `promotion_decision.json`, and `rollback_decision.json`
- upgraded the MVP access shell so `relaytic run` and `relaytic show` now surface lifecycle posture by default instead of stopping at completion-only state

### Slice 08A

- introduced the canonical package boundary `src/relaytic/interoperability/`
- introduced the public commands `relaytic interoperability show`, `relaytic interoperability self-check`, `relaytic interoperability export`, and `relaytic interoperability serve-mcp`
- introduced checked-in host bundle surfaces at `.mcp.json`, `.claude/agents/relaytic.md`, `.agents/skills/relaytic/SKILL.md`, `openclaw/skills/relaytic/SKILL.md`, and `connectors/chatgpt/README.md`
- introduced a Relaytic-owned MCP tool contract so host wrappers stay thin and local-first rather than becoming new product centers

### Slice 08B

- expanded the existing interoperability boundary to include explicit host activation/discovery metadata
- introduced the checked-in workspace discovery mirror `skills/relaytic/SKILL.md` for OpenClaw-style hosts
- upgraded `relaytic interoperability show` so host readiness is explicit instead of implied

### Slice 15D

- expanded the existing benchmark boundary without creating a new package by adding paper-facing benchmark artifacts under `src/relaytic/benchmark/`
- introduced the public paper-benchmark artifact family:
  - `paper_benchmark_manifest.json`
  - `paper_benchmark_table.json`
  - `benchmark_ablation_matrix.json`
  - `rerun_variance_report.json`
  - `benchmark_claims_report.json`
- upgraded `relaytic benchmark run` and `relaytic benchmark show` so humans and external agents can inspect benchmark competitiveness claims, rerun variance, temporal benchmark posture, and benchmark-vs-deploy separation from one stable benchmark bundle

### Slice 15E

- expanded the existing runtime boundary under `src/relaytic/runtime/` with explicit dependency-graph, freshness-contract, recompute-plan, cache-index, and invalidation-report artifacts
- introduced the public command `relaytic runtime reuse`
- upgraded `relaytic benchmark run`, `relaytic completion review`, and trace replay materialization so they now consult one explicit freshness/recompute contract instead of relying on scattered file-exists checks

### Slice 15F

- expanded the existing research/compiler/decision/benchmark/search boundaries without creating a second model-lab stack by adding imported-architecture provenance, candidate-registry, shadow-trial, quarantine, and promotion-readiness artifacts
- introduced governed imported-architecture artifacts:
  - `method_import_report.json`
  - `architecture_candidate_registry.json`
  - `shadow_trial_manifest.json`
  - `shadow_trial_scorecard.json`
  - `candidate_quarantine.json`
  - `promotion_readiness_report.json`
- upgraded `relaytic decision review`, `relaytic benchmark run`, `relaytic benchmark show`, `relaytic show`, `relaytic assist turn`, and search review so research-imported model families can stay replay-first, prove themselves in shadow mode, and remain clearly quarantined or promotion-ready without silently becoming live defaults

### Slice 15G

- extended the existing `src/relaytic/analytics/`, `src/relaytic/planning/`, `src/relaytic/benchmark/`, `src/relaytic/runs/`, and `src/relaytic/assist/` boundaries rather than introducing a separate benchmark-governance package
- introduced artifact boundaries for `optimization_objective_contract.json`, `objective_alignment_report.json`, `split_diagnostics_report.json`, `temporal_fold_health.json`, `metric_materialization_audit.json`, and `benchmark_truth_precheck.json`
- upgraded planning, benchmark review, run summary, and assist explanation surfaces so one canonical objective contract, one split-health report, and one truth precheck decide whether a benchmark is safe to rank instead of letting metric drift or degenerate temporal folds pass silently

### Slice 15J

- extended the existing `src/relaytic/analytics/`, `src/relaytic/modeling/`, `src/relaytic/benchmark/`, `src/relaytic/runs/`, and `src/relaytic/ui/` boundaries rather than introducing a separate temporal runtime package
- introduced artifact boundaries for `temporal_structure_report.json`, `temporal_feature_ladder.json`, `rolling_cv_plan.json`, `temporal_split_guard_report.json`, `sequence_shadow_scorecard.json`, `temporal_baseline_ladder.json`, and `temporal_metric_contract.json`
- upgraded temporal splitters, lagged feature generation, benchmark review, run summary, and benchmark CLI surfaces so ordered temporal structure is explicit, blocked time splits preserve future events when possible, lagged baselines are compared honestly against ordinary baselines, temporal comparison metrics are alias-safe, and sequence candidates remain shadow-only until they beat strong lagged baselines

### Slice 15K

- extended the existing `src/relaytic/modeling/`, `src/relaytic/runs/`, `src/relaytic/assist/`, `src/relaytic/ui/`, and `src/relaytic/benchmark/` boundaries rather than introducing a separate post-processing or threshold-only package
- introduced artifact boundaries for `calibration_strategy_report.json`, `operating_point_contract.json`, `threshold_search_report.json`, `decision_cost_profile.json`, `review_budget_optimization_report.json`, and `abstention_policy_report.json`
- upgraded training, run summary, assist explanations, and benchmark CLI surfaces so calibration choice, threshold search, review-budget posture, and abstention posture are persisted from one canonical operating-point contract instead of being reconstructed differently per surface

### Slice 15L

- extended the existing `src/relaytic/benchmark/`, `src/relaytic/evals/`, `src/relaytic/runs/`, `src/relaytic/assist/`, `src/relaytic/mission_control/`, and `src/relaytic/ui/` boundaries rather than introducing a separate paper-claim or benchmark-governance package
- introduced artifact boundaries for `trace_identity_conformance.json`, `eval_surface_parity_report.json`, `benchmark_truth_audit.json`, `paper_claim_guard_report.json`, `benchmark_release_gate.json`, and `dataset_leakage_audit.json`
- upgraded benchmark review, eval review, run summary, assist explanations, mission-control cards, and benchmark/evals CLI surfaces so trace identity, surface parity, leakage posture, protocol conformance, and public-claim safety are decided from one canonical gate instead of drifting by surface

### Slice 15M

- extended the existing `src/relaytic/analytics/`, `src/relaytic/modeling/`, `src/relaytic/benchmark/`, `src/relaytic/runs/`, `src/relaytic/assist/`, and `src/relaytic/ui/` boundaries rather than introducing a separate specialization or benchmark-generalization package
- introduced artifact boundaries for `family_specialization_matrix.json`, `multiclass_search_profile.json`, `rare_event_search_profile.json`, `adapter_activation_report.json`, `temporal_benchmark_recovery_report.json`, `benchmark_pack_partition.json`, `holdout_claim_policy.json`, and `benchmark_generalization_audit.json`
- upgraded HPO budgeting, architecture routing, benchmark review, run summary, assist explanations, and benchmark CLI surfaces so multiclass and rare-event search posture, adapter activation, temporal benchmark recovery, dev-vs-holdout claim provenance, and benchmark-generalization posture come from one canonical audited path instead of ad hoc benchmark-specific logic

### Slice 15N

- extended the existing `src/relaytic/analytics/`, `src/relaytic/runs/`, `src/relaytic/assist/`, and `src/relaytic/ui/` boundaries instead of introducing a premature AML package before the domain contract was stable
- introduced artifact boundaries for `aml_domain_contract.json`, `aml_case_ontology.json`, `aml_review_budget_contract.json`, and `aml_claim_scope.json`
- upgraded canonical task contracts, run summary, assist explanations, and benchmark CLI surfaces so Relaytic-AML posture, review-budget semantics, and AML claim scope come from one deterministic contract instead of free-form prompt interpretation

### Slice 15O

- introduced the canonical package boundary `src/relaytic/aml/`
- introduced artifact boundaries for `entity_graph_profile.json`, `counterparty_network_report.json`, `typology_detection_report.json`, `subgraph_risk_report.json`, and `entity_case_expansion.json`
- upgraded planning, run-summary materialization, benchmark bundle payloads, and assist explanations so Relaytic-AML can persist and surface deterministic entity-graph evidence instead of staying row-only

### Slice 15P

- introduced the canonical package boundary `src/relaytic/casework/`
- introduced artifact boundaries for `alert_queue_policy.json`, `alert_queue_rankings.json`, `analyst_review_scorecard.json`, `case_packet.json`, and `review_capacity_sensitivity.json`
- upgraded planning, run-summary materialization, benchmark bundle payloads, and assist explanations so Relaytic-AML can rank review queues under explicit analyst budgets and surface one evidence-backed case packet instead of only graph structure or flat risk scores

### Slice 15Q

- introduced the canonical package boundary `src/relaytic/stream_risk/`
- introduced artifact boundaries for `stream_risk_posture.json`, `weak_label_posture.json`, `delayed_outcome_alignment.json`, `drift_recalibration_trigger.json`, and `rolling_alert_quality_report.json`
- upgraded planning, run-summary materialization, benchmark bundle payloads, and assist explanations so Relaytic-AML can expose weak-label risk, delayed-outcome posture, rolling alert pressure, and recalibration triggers from one deterministic stream-risk path instead of treating AML as a static supervised table

### Slice 15R-A

- extended the existing `src/relaytic/benchmark/`, `src/relaytic/runs/`, `src/relaytic/assist/`, `src/relaytic/mission_control/`, and `src/relaytic/ui/` boundaries rather than introducing a separate AML proof package
- introduced accepted AML proof-pack artifact boundaries for `aml_benchmark_manifest.json`, `aml_holdout_claim_report.json`, `aml_demo_scorecard.json`, `aml_public_claim_guard.json`, and `aml_failure_report.json`
- upgraded intake target parsing so canonical one-character AML labels such as Elliptic-style `y` can be selected explicitly instead of being displaced by graph endpoint columns
- upgraded benchmark CLI/show, run-summary, assist, and mission-control proof visibility so PaySim-style and flattened Elliptic-style workloads expose the same AML proof posture and cross-track claim gate

### Slice 15S

- extended `src/relaytic/aml/`, `src/relaytic/ui/`, and `src/relaytic/mission_control/` so the flagship AML demo is a composed product surface over existing casework, stream-risk, benchmark, and public-claim artifacts
- introduced accepted AML demo-bundle artifact boundaries for `aml_demo_bundle_manifest.json`, `aml_demo_business_metric_table.json`, `aml_demo_flow_report.md`, `aml_demo_artifact_index.json`, and mission-control `aml_investigation_board.json`
- introduced the public command `relaytic demo aml-review-queue`, including a synthetic public-safe fixture path when no dataset is supplied
- upgraded mission control so the AML review queue, top case packet, drift posture, benchmark/public-claim guard, and failure posture can be inspected as an investigation board instead of a raw artifact tour

### Slice 15T

- introduced `src/relaytic/aml/business_value.py` for AML business-value metrics, analyst-hour savings, review-capacity metrics, incumbent capacity tradeoffs, and the operational metric guard
- introduced the public command `relaytic aml business-value --run-dir <run_dir>` for rebuilding and inspecting guarded AML business-value artifacts
- introduced accepted AML business-value artifact boundaries for `aml_business_value_report.json`, `analyst_hour_savings_report.json`, `review_capacity_metric_report.json`, and `operational_metric_guard.json`
- upgraded benchmark, run-summary, assist, mission-control, and demo-bundle surfaces so model-score wins do not imply analyst-hour value unless the operational guard passes

### Slice 15U

- introduced `src/relaytic/aml/baselines.py` for AML baseline matrices, capability ablations, adapter fallback reports, contribution summaries, and benchmark relevance scorecards
- introduced the public command `relaytic aml baselines --run-dir <run_dir>` for rebuilding and inspecting 15U baseline and ablation artifacts
- introduced accepted AML baseline artifact boundaries for `aml_baseline_matrix.json`, `aml_ablation_matrix.json`, `aml_baseline_adapter_report.json`, `aml_capability_contribution_report.json`, and `aml_benchmark_relevance_scorecard.json`
- upgraded benchmark, run-summary, and demo-bundle surfaces so no-graph, no-temporal, no-review-budget, no-calibration, and no-typology-prior evidence is visible without turning proxy evidence into a hard AML benchmark claim

### Slice 15V

- introduced `src/relaytic/aml/graph_loader.py` for raw graph bundle, flattened graph snapshot, and subgraph-pack ingestion evidence
- introduced the public command `relaytic aml graph-loader --run-dir <run_dir>` for rebuilding and inspecting 15V graph-loader artifacts
- introduced accepted AML graph-loader artifact boundaries for `aml_graph_loader_manifest.json`, `aml_graph_provenance_report.json`, `aml_subgraph_task_manifest.json`, `aml_graph_claim_scope.json`, and `aml_public_graph_benchmark_catalog.json`
- upgraded benchmark, run-summary, mission-control, demo-bundle, and AML baseline surfaces so raw graph, flattened proxy, subgraph, and graph-SOTA claims are separated from loader/provenance evidence

### Slice 15V-A

- introduced the canonical package boundary `src/relaytic/guide/` for no-lost guidance, safe action menus, artifact shortlists, optional local-LLM guide summaries, and redacted external-context exports
- introduced the public commands `relaytic guide`, `relaytic guide ask`, and `relaytic guide export-context`
- upgraded `relaytic status` so partial runs without completion-governor artifacts fall back to the guide instead of failing with an artifact-literacy error
- introduced accepted guide and external-context artifact boundaries for `guide_state.json`, `guide_action_menu.json`, `guide_artifact_shortlist.json`, `guide_question_starters.json`, `guide_local_llm_summary.json`, `external_llm_context_pack.json`, `external_llm_context_pack.md`, `external_llm_artifact_index.json`, and `external_llm_redaction_report.json`

### Slice 15W

- introduced `src/relaytic/aml/temporal.py` for AML delayed-label evaluation, positive-unlabeled posture, threshold-drift reporting, time-window scorecards, and temporal benchmark claim gating
- introduced the public command `relaytic aml temporal --run-dir <run_dir>` for rebuilding and inspecting 15W temporal weak-label artifacts
- introduced accepted AML temporal artifact boundaries for `aml_delayed_label_eval_report.json`, `aml_positive_unlabeled_posture.json`, `aml_threshold_drift_report.json`, `aml_time_window_scorecard.json`, and `aml_temporal_benchmark_claim_report.json`
- upgraded benchmark, run-summary, guide, and AML CLI surfaces so time-window evidence stays rowless, delayed-label and PU blockers are visible, sequence-native claims remain shadow-gated, and temporal public claims fail closed under missing delayed outcomes, zero-positive future folds, leakage, or unresolved threshold drift

### Slice 15X

- introduced `src/relaytic/aml/environment.py` for AML evaluation-environment scoring, workflow task matrices, benchmark-environment scorecards, and failure reporting
- introduced the public command `relaytic aml environment --run-dir <run_dir>` for rebuilding and inspecting model-vs-environment score separation without regenerating upstream evidence
- introduced accepted AML environment artifact boundaries for `aml_eval_environment_manifest.json`, `aml_environment_scorecard.json`, `aml_workflow_task_matrix.json`, `aml_environment_failure_report.json`, and `aml_benchmark_environment_scorecard.json`
- upgraded run-summary, guide, and AML CLI surfaces so unsafe steering rejection, benchmark-environment readiness, public-claim discipline, and model/environment disagreement are visible to humans and external agents

### Slice 15Y

- introduced the public documentation contract for the demo-first Relaytic-AML path through `docs/why_relaytic_aml.md`, `docs/product_story.md`, and `docs/paper_benchmark_runbook.md`
- upgraded `README.md`, `docs/handbooks/relaytic_user_handbook.md`, `docs/handbooks/relaytic_agent_handbook.md`, and `docs/handbooks/relaytic_demo_walkthrough.md` so first contact starts with `relaytic demo aml-review-queue` and the AML proof artifact checklist
- upgraded `docs/relaytic_ui_frontier_review.md` so mission-control docs distinguish the static fallback, AML investigation board, Agent Console, and later local live UI server
- no new code package boundary was introduced; Slice 15Y is a public documentation and proof-path boundary

### Slice 15Z

- introduced `src/relaytic/ui/aml_environment.py` as the focused UI helper boundary for `relaytic aml environment` execution, artifact summary shaping, and run-summary refresh behavior previously embedded in the oversized CLI module
- introduced `src/relaytic/release_safety/repo_credibility.py` for deterministic pre-Academy repo credibility reports
- introduced repo-level report artifacts under `docs/reports/`: `pre_academy_repo_audit.json`, `module_extraction_plan.json`, `public_surface_inventory.json`, `module_split_report.json`, and `benchmark_surface_cleanup_report.json`
- preserved the public `relaytic aml environment` command while documenting retained oversized modules and the next extraction boundaries
- future Slice 15Z-R paper-freeze work should consume the public-surface inventory and benchmark cleanup debt report rather than rediscovering repo credibility risks from scratch

### Slice 15Z-R

- introduced `src/relaytic/release_safety/paper_freeze.py` for deterministic paper/release freeze pack generation
- introduced the public command `relaytic release-safety paper-freeze` for regenerating the freeze pack locally
- introduced repo-level release-freeze artifacts under `docs/reports/`: `paper_release_freeze_manifest.json`, `aml_relevant_benchmark_catalog.json`, `paper_benchmark_runbook.md`, `paper_result_table.json`, `paper_claim_boundary_report.json`, `reproducibility_attestation.json`, and `release_attention_pack_manifest.json`
- froze PaySim-style, flattened Elliptic-style, subgraph/synthetic-bank graph, and generic supporting tracks with explicit `dev`, `proxy`, or `blocked` posture rather than hard public AML superiority claims
- future academy work should consume the release-freeze pack as the public-claim boundary before adding capability-growth surfaces

### Paper Track P4

- introduced `src/relaytic/release_safety/paysim_benchmark.py` under the existing release-safety boundary for deterministic PaySim temporal benchmark artifact generation
- introduced the public command `relaytic release-safety paysim-benchmark` for regenerating PaySim paper artifacts locally
- introduced paper-track benchmark artifacts under `docs/reports/`: `paysim_benchmark_manifest.json`, `paysim_temporal_split_report.json`, `paysim_operating_point_table.json`, and `paysim_paper_result_row.json`
- preserved supporting-only claim posture for PaySim-style proxy evidence and kept hard AML/SOTA performance claims blocked until later paper gates pass
- Paper Track P6 consumes the P3 dataset registry, P4 result-row contract, and P5 graph provenance before adding strong baseline suites; P6-A consumes the P6 budget and publishability gates, and P7 now adds claim-gated numeric graph evidence before P8 decides harder graph-track support

### Paper Track P5

- introduced `src/relaytic/release_safety/elliptic_graph.py` under the existing release-safety boundary for deterministic Elliptic graph provenance and temporal split artifact generation
- introduced the public command `relaytic release-safety elliptic-graph` for regenerating Elliptic graph paper artifacts locally
- introduced paper-track graph artifacts under `docs/reports/`: `elliptic_graph_loader_manifest.json`, `elliptic_graph_provenance_report.json`, `elliptic_temporal_split_report.json`, `elliptic_graph_claim_scope.json`, and `elliptic_paper_result_row.json`
- preserved supporting-only loader/provenance posture for Elliptic-style graph evidence and kept graph benchmark performance, graph SOTA, paper-primary, and hard AML claims blocked until later graph baselines and competitive paper gates pass

### Paper Track P6

- introduced `src/relaytic/release_safety/paper_baselines.py` under the existing release-safety boundary for deterministic tabular baseline suites, adapter/fallback reporting, explicit budget contracts, leakage-safe feature audits, and publishability gating
- introduced the public command `relaytic release-safety tabular-baselines` for regenerating P6 paper artifacts locally
- introduced paper-track baseline artifacts under `docs/reports/`: `paper_baseline_suite_manifest.json`, `paper_baseline_version_matrix.json`, `paper_tabular_baseline_table.json`, `paper_baseline_fallback_report.json`, `paper_benchmark_budget_contract.json`, `paper_competitive_search_trace.json`, `paper_leakage_safe_feature_report.json`, and `paper_publishability_gate.json`
- executed six full-data PaySim baseline families using the frozen chronological split, train-only feature state, and validation-only thresholds; preserved baseline-only posture and kept headline/hard claims blocked until P6-A

### Paper Track P6-A

- introduced `src/relaytic/release_safety/paysim_competitive.py` under the existing release-safety boundary for competitive PaySim search, prior-step destination-history features, validation-only calibration/threshold selection, and supporting-only publishability gating
- introduced the public command `relaytic release-safety paysim-competitive` for regenerating P6-A competitive artifacts locally
- introduced paper-track competitive artifacts under `docs/reports/`: `paysim_competitive_benchmark_manifest.json`, `paysim_competitive_budget_contract.json`, `paysim_competitive_search_trace.json`, `paysim_leakage_safe_feature_report.json`, `paysim_competitive_baseline_table.json`, and `paysim_publishability_gate.json`
- executed 14 full-data-compatible probe trials and five full-training finalists under the frozen chronological split; validation-selected Extra Trees reports fixed test PR-AUC `0.638773`, passes as a supporting-only PaySim table candidate, and keeps headline/hard claims blocked before P7 and release proof

### Paper Track P7

- introduced `src/relaytic/release_safety/graph_baselines.py` under the existing release-safety boundary for temporal-safe Elliptic graph feature views, optional graph-model shadows, explicit graph budgets, and publishability gating
- introduced the public command `relaytic release-safety graph-baselines` for regenerating P7 graph baseline artifacts locally
- introduced paper-track graph baseline artifacts under `docs/reports/`: `paper_graph_baseline_manifest.json`, `paper_graph_feature_table.json`, `paper_graph_model_shadow_scorecard.json`, `paper_graph_baseline_fallback_report.json`, `paper_graph_budget_contract.json`, `paper_graph_competitive_search_trace.json`, and `paper_graph_publishability_gate.json`
- executed the full raw Elliptic bundle after verifying all edges are same-time-step observable; selected LightGBM on source-plus-structural features with test PR-AUC `0.668756` and recorded the modest paired source-only delta (`+0.004588`) without promoting the weaker GraphSAGE shadow or any headline/SOTA claim

### Paper Track P8

- introduced `src/relaytic/release_safety/hard_graph_tracks.py` under the existing release-safety boundary for AMLSim generation/typology verification and Elliptic2 acquisition, loader, split, resource, and license decisions
- introduced the public command `relaytic release-safety hard-graph-tracks` for regenerating P8 supported/proxy/blocked artifacts locally
- introduced paper-track hard-graph decision artifacts under `docs/reports/`: `amlsim_generation_manifest.json`, `amlsim_typology_manifest.json`, `elliptic2_subgraph_access_report.json`, and `subgraph_benchmark_blocker_report.json`
- recorded both current hard tracks as blocked: AMLSim lacks an audited generated proxy bundle, and Elliptic2 lacks local source plus official-loader, overlap/split, and resource proof; neither can be used for paper performance or SOTA claims

### Paper Track P8-A

- introduced `src/relaytic/release_safety/elliptic2_recovery.py` under the existing release-safety boundary for official Elliptic2 labeled-core audit, RevTrack/RevClassify source pinning, low-memory selected-embedding derivation, protocol-discrepancy reporting, and an exploratory context pilot
- introduced the public command `relaytic release-safety elliptic2-recovery` for regenerating P8-A artifacts against external local official sources without committing raw assets or revealing machine paths
- introduced paper-track modern graph recovery artifacts under `docs/reports/`: `elliptic2_recovery_manifest.json`, `elliptic2_schema_overlap_audit.json`, `elliptic2_protocol_audit.json`, `elliptic2_modern_reference_contract.json`, `elliptic2_context_pilot_result.json`, and `elliptic2_recovery_gate.json`
- recovered Elliptic2 from source-blocked to pilot-ready with official labeled-core audit and a strong context pilot (`test_pr_auc=0.935255`), while keeping public paper/SOTA claims blocked until P8-B performs competitive, repeated-seed, and split-robust proof

### Paper Track P8-B

- introduced `src/relaytic/release_safety/elliptic2_competitive.py` under the existing release-safety boundary for modern-reference comparison, validation-only pooled-context candidate search, repeated-seed scoring, content-hash split robustness, cohort-coverage auditing, and publishability gating
- introduced the public command `relaytic release-safety elliptic2-competitive` for regenerating P8-B artifacts from external local pinned RevTrack assets without committing raw data or machine paths
- introduced paper-track competitive subgraph artifacts under `docs/reports/`: `elliptic2_competitive_budget_contract.json`, `elliptic2_revclassify_reference_scorecard.json`, `elliptic2_relaytic_candidate_search_trace.json`, `elliptic2_repeated_seed_scorecard.json`, `elliptic2_split_robustness_report.json`, and `elliptic2_publishability_gate.json`
- promoted only a supporting modern-context row: pooled-moments LightGBM reports repeated official test `PR-AUC=0.943240 +/- 0.000882` and deterministic hash-split test `PR-AUC=0.929669 +/- 0.000538`, below reported `RevClassifyDS=0.974`; P8-C is required before P9

### Paper Track P8-C

- introduced `src/relaytic/release_safety/elliptic2_reference_parity.py` under the existing release-safety boundary for faithful RevClassify precondition auditing, current-core versus RevTrack-evaluable cohort reconciliation, strict entity-disjoint split feasibility, neural candidate scorecard blocking, and reference-parity gating
- introduced the public command `relaytic release-safety elliptic2-reference-parity` for regenerating P8-C artifacts from external local pinned RevTrack assets without committing raw data or machine paths
- introduced paper-track reference-parity artifacts under `docs/reports/`: `elliptic2_neural_reference_parity_contract.json`, `elliptic2_evaluable_cohort_reconciliation.json`, `elliptic2_entity_disjoint_split_report.json`, `elliptic2_neural_candidate_scorecard.json`, and `elliptic2_reference_parity_gate.json`
- recorded that P8-B remains supporting-only: faithful RevClassify parity is blocked by missing local dependencies/accelerator and absent distributed classification checkpoints, cohort equivalence to the current official core is not proven, and strict entity-disjoint splitting degenerates with `110889/110902` rows in the largest identity component; P8-D is required before P9

### Paper Track P8-D

- introduced `src/relaytic/release_safety/paper_thesis_decision.py` under the existing release-safety boundary for post-P8-C thesis narrowing, evidence-role freezing, reprovisioning decision, and claim-rewrite planning
- introduced the public command `relaytic release-safety paper-thesis-decision` for regenerating the P8-D paper strategy gate from committed P8-B/P8-C artifacts
- introduced paper-track thesis-decision artifacts under `docs/reports/`: `paper_p8d_thesis_decision.json`, `paper_p8d_evidence_role_matrix.json`, `paper_p8d_reprovisioning_decision.json`, and `paper_p8d_claim_rewrite_plan.json`
- accepted the narrowed first-paper thesis around claim-gated AML evaluation and operational evidence: P8-B remains supporting modern-context evidence only, P8-C remains a limitation and claim-firewall, Elliptic2 is not a performance contribution, and P9 is now unblocked

### Paper Track P9

- introduced `src/relaytic/release_safety/paper_operational_metrics.py` under the existing release-safety boundary for operational AML metric tables, review-budget curves, case-packet completeness reporting, and claim-guarded analyst-workflow evidence
- introduced the public command `relaytic release-safety paper-operational-metrics` for regenerating P9 artifacts from committed paper-track evidence, with optional run-specific casework context via `--run-dir`
- introduced paper-track operational metric artifacts under `docs/reports/`: `paper_operational_metric_table.json`, `paper_review_budget_curve.json`, `paper_case_packet_completeness_report.json`, and `paper_operational_claim_guard.json`
- materialized PaySim and Elliptic supporting review-budget rows with false-positive burden proxies while keeping hard business-value, headline operational, Elliptic2 performance-contribution, and SOTA claims blocked until case packets, explicit analyst assumptions, and same-queue baseline evidence are complete; P10 is now unblocked for reproducible table generation

### Paper Track P10

- introduced `src/relaytic/release_safety/paper_table_generator.py` under the existing release-safety boundary for reproducible paper result tables, metric-cell provenance, reproduction commands, audit reports, and publishability matrices
- introduced the public command `relaytic release-safety paper-tables` for regenerating P10 table artifacts from committed paper-track evidence
- introduced paper-track table artifacts under `docs/reports/`: `paper_result_table_final.json`, `paper_table_provenance.json`, `paper_reproduction_commands.md`, `paper_metric_cell_audit.json`, and `paper_publishability_matrix.json`
- generated claim-guarded supporting performance, operational, modern-context, and limitation tables where every numeric cell carries artifact, command, split, budget, leakage, run-directory, and claim-state provenance; P11 is now unblocked while headline, hard AML, SOTA, and business-value claims remain blocked

### AML Pivot Track

- the public product name remains `Relaytic`, but the flagship frontier story now becomes `Relaytic-AML`
- the AML productization and paper-freeze bridge is now landed through Slice 15Z-R; future capability-academy work starts from Slice 16A
- future AML boundaries should concentrate under `src/relaytic/benchmark/`, `src/relaytic/aml/`, `src/relaytic/casework/`, `src/relaytic/graph_fabric/`, `src/relaytic/stream_risk/`, and any focused future AML loader or release-freeze package rather than scattering domain logic across unrelated generic packages
- future public AML artifacts should remain additive and must not break the canonical `relaytic` package or CLI surface

### Slice 09A

- introduced the canonical package boundary `src/relaytic/memory/`
- introduced the public commands `relaytic memory retrieve` and `relaytic memory show`
- expanded the artifact boundary to include `memory_retrieval.json`, `analog_run_candidates.json`, `route_prior_context.json`, `challenger_prior_suggestions.json`, `reflection_memory.json`, and `memory_flush_report.json`
- upgraded planning, evidence, completion, lifecycle, `relaytic run`, and `relaytic show` so memory artifacts can influence current runs without widening the legacy compatibility surface

### Slice 09B

- introduced the canonical package boundary `src/relaytic/runtime/`
- introduced the public commands `relaytic runtime show` and `relaytic runtime events`
- expanded the artifact boundary to include `lab_event_stream.jsonl`, `hook_execution_log.json`, `run_checkpoint_manifest.json`, `capability_profiles.json`, `data_access_audit.json`, and `context_influence_report.json`
- upgraded CLI and MCP orchestration so stage transitions share one local runtime instead of parallel surface-specific state

### Slice 09

- introduced the canonical package boundary `src/relaytic/intelligence/`
- introduced the public commands `relaytic intelligence run` and `relaytic intelligence show`
- expanded the artifact boundary to include `intelligence_mode.json`, `llm_backend_discovery.json`, `llm_health_check.json`, `llm_upgrade_suggestions.json`, `semantic_task_request.json`, `semantic_task_results.json`, `intelligence_escalation.json`, `context_assembly_report.json`, `doc_grounding_report.json`, `semantic_access_audit.json`, `semantic_debate_report.json`, `semantic_counterposition_pack.json`, and `semantic_uncertainty_report.json`
- upgraded completion, lifecycle, `relaytic run`, `relaytic show`, and the MCP contract so bounded semantic deliberation is visible instead of hidden in advisory paths

### Slice 09C

- introduced the canonical package boundary `src/relaytic/autonomy/`
- introduced the public commands `relaytic autonomy run` and `relaytic autonomy show`
- expanded the artifact boundary to include `autonomy_loop_state.json`, `autonomy_round_report.json`, `challenger_queue.json`, `branch_outcome_matrix.json`, `retrain_run_request.json`, `recalibration_run_request.json`, `champion_lineage.json`, and `loop_budget_report.json`
- upgraded runtime, memory, intelligence, lifecycle, `relaytic run`, `relaytic show`, and the MCP contract so bounded autonomous follow-up is replayable and inspectable rather than implied by later artifacts

### Post-Slice 07 Cross-Cutting Additions

- introduced the canonical package boundary `src/relaytic/integrations/`
- introduced the public command `relaytic integrations show`
- introduced the public command `relaytic integrations self-check`
- introduced the public command `relaytic doctor`
- introduced the one-line bootstrap script `scripts/install_relaytic.py`
- wired adapter-scoped third-party surfaces for intake validation and evidence diagnostics/challengers without broadening the legacy compatibility surface
- kept third-party capabilities optional and adapter-scoped rather than broadening the core or legacy compatibility surface

## Recent Boundary Changes

### Slice 09D

- introduced the canonical package boundary `src/relaytic/research/`
- introduced artifact boundaries for `research_query_plan.json`, `research_source_inventory.json`, `research_brief.json`, `method_transfer_report.json`, `benchmark_reference_report.json`, and `external_research_audit.json`
- introduced public commands `relaytic research gather`, `relaytic research show`, and `relaytic research sources`
- wired research artifacts into completion, autonomy, run summary, and MCP service surfaces without widening the legacy compatibility boundary

### Slice 09E

- introduced the canonical package boundary `src/relaytic/assist/`
- introduced artifact boundaries for `assist_mode.json`, `assist_session_state.json`, `assistant_connection_guide.json`, and `assist_turn_log.jsonl`
- introduced public commands `relaytic assist show`, `relaytic assist turn`, and `relaytic assist chat`
- wired communicative assist into the CLI and MCP service surfaces without changing the deterministic core or widening the legacy compatibility boundary

### Slice 09F

- extended the existing intelligence boundary with routed-intelligence helpers at `src/relaytic/intelligence/modes.py`, `src/relaytic/intelligence/local_baseline.py`, and `src/relaytic/intelligence/routing.py`
- introduced artifact boundaries for `llm_routing_plan.json`, `local_llm_profile.json`, `verifier_report.json`, and `semantic_proof_report.json`
- upgraded the existing public commands `relaytic intelligence run` and `relaytic intelligence show` so routed mode, local profile, verifier posture, and semantic proof are visible without creating a separate compatibility surface

### Slice 11

- introduced the canonical package boundary `src/relaytic/benchmark/`
- introduced the canonical modeling boundaries `src/relaytic/modeling/feature_pipeline.py` and `src/relaytic/modeling/calibration.py`
- introduced artifact boundaries for `reference_approach_matrix.json`, `benchmark_gap_report.json`, and `benchmark_parity_report.json`
- introduced public commands `relaytic benchmark run` and `relaytic benchmark show`
- upgraded the Builder/runtime boundary so first-route execution now persists richer preprocessing, bounded categorical handling, executed feature transforms, calibration state, and uncertainty-bearing inference outputs without widening the legacy compatibility boundary
- wired benchmark artifacts into completion, run summary, assist, runtime, and MCP surfaces without turning benchmark tooling into a separate source of truth

### Slice 11A

- extended the existing benchmark boundary rather than introducing a separate incumbent package
- introduced artifact boundaries for `external_challenger_manifest.json`, `external_challenger_evaluation.json`, `incumbent_parity_report.json`, and `beat_target_contract.json`
- extended the public command `relaytic benchmark run` so operators and external agents can attach incumbent models, prediction files, or rulesets directly
- extended autonomy and run-summary surfaces so explicit beat-target contracts can change follow-up behavior instead of staying benchmark-only metadata

### Slice 11B

- introduced the canonical package boundary `src/relaytic/mission_control/`
- introduced artifact boundaries for `mission_control_state.json`, `review_queue_state.json`, `control_center_layout.json`, `onboarding_status.json`, `install_experience_report.json`, `launch_manifest.json`, `demo_session_manifest.json`, `ui_preferences.json`, and `reports/mission_control.html`
- introduced public commands `relaytic mission-control show` and `relaytic mission-control launch`
- upgraded `scripts/install_relaytic.py` so install verification and local control-center launch can share one documented onboarding path instead of splitting environment health and operator entry into separate flows
- introduced MCP-visible mission-control inspection through `relaytic_show_mission_control`

### Slice 11C

- extended the existing `src/relaytic/mission_control/` and `src/relaytic/assist/` boundaries instead of creating a separate UI-shell package
- introduced artifact boundaries for `mode_overview.json`, `capability_manifest.json`, `action_affordances.json`, `stage_navigator.json`, and `question_starters.json`
- upgraded the existing public commands `relaytic mission-control show`, `relaytic mission-control launch`, `relaytic assist show`, and `relaytic assist turn` so mission-control clarity is available through shared artifacts instead of UI-only state
- upgraded CLI and MCP mission-control quick payloads so next actor, current mode, capability counts, action counts, question counts, and stage-navigation scope remain visible without decoding the full bundle

### Slice 11D

- extended the existing `src/relaytic/mission_control/` boundary plus `src/relaytic/ui/cli.py` rather than introducing a separate onboarding shell
- introduced the public command `relaytic mission-control chat`
- extended the public command `relaytic mission-control launch` with `--interactive`
- upgraded the existing mission-control and assist chat surfaces so onboarding guidance, capability reasons, activation hints, and chat shortcuts are available from the same local product entrypoints

### Slice 11E

- extended the existing `src/relaytic/mission_control/` boundary and checked-in host wrapper notes instead of introducing a separate handbook runtime package
- introduced checked-in handbook surfaces at `docs/handbooks/relaytic_user_handbook.md` and `docs/handbooks/relaytic_agent_handbook.md`
- upgraded the existing public commands `relaytic mission-control show`, `relaytic mission-control chat`, and `relaytic mission-control launch` so role-specific handbook discovery is part of onboarding instead of hidden repo knowledge
- upgraded the checked-in Claude, Codex/OpenAI, and OpenClaw host notes so new agents are pointed to the same agent handbook before they start driving Relaytic

### Slice 15A

- extended the existing `src/relaytic/analytics/`, `src/relaytic/planning/`, `src/relaytic/benchmark/`, `src/relaytic/assist/`, and `src/relaytic/runs/` boundaries rather than introducing a separate task-governance package
- introduced artifact boundaries for `task_profile_contract.json`, `target_semantics_report.json`, `metric_contract.json`, `benchmark_mode_report.json`, `deployment_readiness_report.json`, `benchmark_vs_deploy_report.json`, and `dataset_semantics_audit.json`
- upgraded planning, benchmark review, run summary, and assist explanation surfaces so task semantics, metric choice, and benchmark-versus-deploy posture come from one canonical contract instead of being re-inferred later
- expanded the benchmark/test boundary to include timestamped temporal benchmark dataset writers and optional temporal benchmark-pack tests without changing the current public ingestion surface

### Slice 15B

- extended the existing `src/relaytic/analytics/`, `src/relaytic/planning/`, `src/relaytic/modeling/`, `src/relaytic/memory/`, `src/relaytic/assist/`, and `src/relaytic/runs/` boundaries rather than introducing a separate architecture-selection package
- introduced artifact boundaries for `architecture_registry.json`, `architecture_router_report.json`, `candidate_family_matrix.json`, `architecture_fit_report.json`, `family_capability_matrix.json`, and `architecture_ablation_report.json`
- upgraded planning, memory-informed candidate ordering, run summary, and assist explanation surfaces so architecture choice is routed and auditable instead of hidden inside Builder defaults
- expanded the trainable-model boundary to include histogram-gradient boosting and extra-trees regression/classification families plus optional CatBoost, XGBoost, LightGBM, and TabPFN adapter slots when those libraries are installed

### Slice 15C

- extended the existing `src/relaytic/modeling/`, `src/relaytic/runs/`, `src/relaytic/assist/`, and `src/relaytic/ui/` boundaries rather than introducing a separate HPO orchestration package
- introduced artifact boundaries for `hpo_budget_contract.json`, `architecture_search_space.json`, `trial_ledger.jsonl`, `early_stopping_report.json`, `search_loop_scorecard.json`, `warm_start_transfer_report.json`, and `threshold_tuning_report.json`
- upgraded the deterministic floor from shallow fixed family variants to bounded seeded search loops with explicit plateau stopping, wall-clock budgeting, threshold tuning, and warm-start reuse
- upgraded run-summary, access-surface, and assist explanation surfaces so model-choice questions can cite HPO budgets, executed trials, stop reasons, and threshold policy instead of hand-waving over search behavior

### Slice 11F

- extended the existing `src/relaytic/mission_control/` boundary and `src/relaytic/ui/cli.py` rather than introducing a separate demo shell
- introduced the checked-in walkthrough surface at `docs/handbooks/relaytic_demo_walkthrough.md`
- extended the existing mission-control onboarding boundary so `onboarding_status.json`, `action_affordances.json`, `question_starters.json`, and rendered mission-control surfaces now include guided demo flow, explicit mode explanations, and stuck-recovery guidance
- upgraded the existing mission-control chat surface with `/demo`, `/modes`, and `/stuck` so first-contact users do not need repo knowledge to recover or continue

### Slice 11G

- extended the existing `src/relaytic/mission_control/`, `src/relaytic/ui/cli.py`, `src/relaytic/intelligence/backends.py`, and `scripts/install_relaytic.py` boundaries rather than introducing a separate onboarding-conversation product
- introduced the mission-control artifact boundary `onboarding_chat_session_state.json`
- upgraded the existing mission-control chat surface so it can capture dataset paths and objectives across turns, expose `/state` and `/reset`, and start the first run after explicit confirmation
- upgraded the existing bootstrap installer so the full profile attempts lightweight onboarding-local-LLM provisioning by default instead of leaving that setup as a hidden follow-up step

### Slice 12

- introduced the canonical package boundary `src/relaytic/dojo/`
- introduced artifact boundaries for `dojo_session.json`, `dojo_hypotheses.json`, `dojo_results.json`, `dojo_promotions.json`, and `architecture_proposals.json`
- introduced public commands `relaytic dojo review`, `relaytic dojo show`, and `relaytic dojo rollback`
- introduced MCP-visible dojo inspection and review through `relaytic_show_dojo` and `relaytic_review_dojo`
- upgraded run-summary and mission-control surfaces so dojo proposal state, validation outcomes, promotion counts, and rollback state remain visible instead of becoming CLI-only side state

### Slice 12A

- introduced the canonical package boundary `src/relaytic/pulse/`
- introduced artifact boundaries for `pulse_schedule.json`, `pulse_run_report.json`, `pulse_skip_report.json`, `pulse_recommendations.json`, `innovation_watch_report.json`, `challenge_watchlist.json`, `pulse_checkpoint.json`, `memory_compaction_plan.json`, `memory_compaction_report.json`, and `memory_pinning_index.json`
- introduced public commands `relaytic pulse review` and `relaytic pulse show`
- introduced MCP-visible pulse inspection and review through `relaytic_show_pulse` and `relaytic_review_pulse`
- upgraded memory retrieval, run-summary, mission-control, and manifest surfaces so bounded periodic awareness, rowless innovation watch, safe queued follow-up, and memory pinning remain visible instead of becoming sidecar scheduler state

### Slice 12B

- introduced the canonical package boundaries `src/relaytic/tracing/` and `src/relaytic/evals/`
- introduced artifact boundaries for `trace_model.json`, `trace_span_log.jsonl`, `specialist_trace_index.json`, `tool_trace_log.jsonl`, `intervention_trace_log.jsonl`, `branch_trace_graph.json`, `claim_packet_log.jsonl`, `adjudication_scorecard.json`, `decision_replay_report.json`, `agent_eval_matrix.json`, `security_eval_report.json`, `red_team_report.json`, `protocol_conformance_report.json`, and `host_surface_matrix.json`
- introduced public commands `relaytic trace show`, `relaytic trace replay`, `relaytic evals run`, and `relaytic evals show`
- introduced MCP-visible trace and eval surfaces through `relaytic_show_trace`, `relaytic_replay_trace`, `relaytic_run_agent_evals`, and `relaytic_show_agent_evals`
- upgraded the runtime gateway so stage transitions and runtime events emit canonical trace spans directly instead of relying only on later reconstruction
- upgraded run-summary and mission-control surfaces so trace truth, adjudication winners, protocol conformance, and open security findings remain visible instead of becoming debug-only output

### Slice 12C

- introduced the canonical package boundaries `src/relaytic/handoff/` and `src/relaytic/learnings/`
- introduced artifact boundaries for `run_handoff.json`, `next_run_options.json`, `next_run_focus.json`, `reports/user_result_report.md`, `reports/agent_result_report.md`, `lab_learnings_snapshot.json`, `learnings_state.json`, and `learnings.md`
- introduced public commands `relaytic handoff show`, `relaytic handoff focus`, `relaytic learnings show`, and `relaytic learnings reset`
- introduced MCP-visible handoff and learnings surfaces through `relaytic_show_handoff`, `relaytic_set_next_run_focus`, `relaytic_show_learnings`, and `relaytic_reset_learnings`
- upgraded run-summary, mission-control, assist, memory, manifest, and mission-control-chat surfaces so differentiated result handoff, next-run steering, and durable learnings remain visible instead of becoming side artifacts

### Slice 10

- introduced the canonical package boundary `src/relaytic/feedback/`
- introduced artifact boundaries for `feedback_intake.json`, `feedback_validation.json`, `feedback_effect_report.json`, `feedback_casebook.json`, `outcome_observation_report.json`, `decision_policy_update_suggestions.json`, `policy_update_suggestions.json`, and `route_prior_updates.json`
- introduced public commands `relaytic feedback add`, `relaytic feedback review`, `relaytic feedback show`, and `relaytic feedback rollback`
- wired feedback artifacts into memory and run-summary surfaces so accepted route-prior updates remain explicit rather than hidden state drift

### Slice 10C

- introduced the canonical package boundary `src/relaytic/control/`
- introduced artifact boundaries for `intervention_request.json`, `intervention_contract.json`, `control_challenge_report.json`, `override_decision.json`, `intervention_ledger.json`, `recovery_checkpoint.json`, `control_injection_audit.json`, `causal_memory_index.json`, `intervention_memory_log.json`, `outcome_memory_graph.json`, and `method_memory_index.json`
- introduced public commands `relaytic control review` and `relaytic control show`
- upgraded assist and MCP surfaces so steering requests are normalized, challenged, checkpointed, and replayable instead of being treated as blind authority

### Slice 10A

- introduced the canonical package boundaries `src/relaytic/decision/`, `src/relaytic/compiler/`, and `src/relaytic/data_fabric/`
- introduced artifact boundaries for `decision_world_model.json`, `controller_policy.json`, `handoff_controller_report.json`, `intervention_policy_report.json`, `decision_usefulness_report.json`, `value_of_more_data_report.json`, `data_acquisition_plan.json`, `source_graph.json`, `join_candidate_report.json`, `method_compiler_report.json`, `compiled_challenger_templates.json`, `compiled_feature_hypotheses.json`, and `compiled_benchmark_protocol.json`
- introduced public commands `relaytic decision review` and `relaytic decision show`
- introduced MCP-visible decision surfaces through `relaytic_review_decision` and `relaytic_show_decision`
- upgraded the run-summary, autonomy, runtime, assist, and MCP boundaries so decision-world reasoning can change next-step posture instead of remaining a detached report

## Latest Boundary Additions

- `src/relaytic/profiles/` for Slice 10B quality contracts, budget contracts, operator/lab profile overlays, and budget-consumption reporting
- `src/relaytic/control/` for Slice 10C intervention contracts, skeptical override handling, control-injection auditing, recovery checkpoints, and control-ledger persistence
- `src/relaytic/decision/` for Slice 10A decision-world models, intervention policy, value-of-more-data reasoning, and decision-usefulness synthesis
- `src/relaytic/compiler/` for Slice 10A method compilation, executable challenger templates, compiled feature hypotheses, and compiled benchmark protocols
- `src/relaytic/data_fabric/` for Slice 10A source-graph reasoning, join-candidate analysis, entity-history understanding, and acquisition planning
- `src/relaytic/benchmark/` for Slice 11A imported-incumbent evaluation, incumbent parity reporting, and beat-target contracts on top of Slice 11 reference comparisons
- `src/relaytic/mission_control/` for Slice 11B mission-control MVP state, onboarding/install-health state, review-queue state, launch metadata, demo-session state, static control-center rendering, Slice 11C clarity surfaces for modes/capabilities/actions/navigation/questions, Slice 11D live onboarding/chat behavior, Slice 11E handbook discovery surfaces, Slice 11F guided demo/mode-education/stuck-recovery surfaces, Slice 11G adaptive onboarding/session-capture/lightweight-semantic-helper surfaces, and Slice 15 branch-aware operator/proof surfaces
- `src/relaytic/dojo/` for Slice 12 guarded self-improvement controls, quarantined proposal bundles, validation results, promotion ledgers, rollback-ready state, and architecture-proposal quarantine
- `src/relaytic/pulse/` for Slice 12A periodic awareness scheduling, innovation-watch gathering, pulse recommendations, skip reporting, bounded pulse-run persistence, explicit memory-maintenance orchestration, and pulse-to-mission-control visibility surfaces
- `src/relaytic/tracing/` for Slice 12B canonical trace schemas, specialist/tool/intervention/branch traces, claim-packet persistence, deterministic adjudication scorecards, replay reports, and replay/query surfaces
- `src/relaytic/evals/` for Slice 12B agent-behavior evaluation, security harnesses, protocol-conformance checks, adversarial steering tests, runtime regression packs, scenario/result matrices, and Slice 15 human-supervision/onboarding evaluation reports
- `src/relaytic/handoff/` for Slice 12C differentiated post-run handoff generation, next-run options, persisted next-run focus, and differentiated report rendering for humans and external agents
- `src/relaytic/learnings/` for Slice 12C durable local learnings state, learnings markdown, per-run learnings snapshots, and workspace learnings reset behavior
- `docs/handbooks/` for Slice 11E role-specific human/operator and external-agent onboarding guides
- `docs/handbooks/relaytic_demo_walkthrough.md` for Slice 11F public-safe demo sequencing and first-contact presentation
- `docs/specs/` for normative product-contract docs covering workspace lifecycle, result-contract schema, governed learnings, mission-control behavior, compatibility migration, proof burden, and flagship demos

Shipped artifact names:

- `quality_contract.json`
- `quality_gate_report.json`
- `budget_contract.json`
- `budget_consumption_report.json`
- `operator_profile.json`
- `lab_operating_profile.json`
- `intervention_request.json`
- `intervention_contract.json`
- `control_challenge_report.json`
- `override_decision.json`
- `intervention_ledger.json`
- `recovery_checkpoint.json`
- `control_injection_audit.json`
- `causal_memory_index.json`
- `intervention_memory_log.json`
- `outcome_memory_graph.json`
- `method_memory_index.json`
- `decision_world_model.json`
- `controller_policy.json`
- `handoff_controller_report.json`
- `intervention_policy_report.json`
- `decision_usefulness_report.json`
- `value_of_more_data_report.json`
- `data_acquisition_plan.json`
- `source_graph.json`
- `join_candidate_report.json`
- `method_compiler_report.json`
- `compiled_challenger_templates.json`
- `compiled_feature_hypotheses.json`
- `compiled_benchmark_protocol.json`
- `external_challenger_manifest.json`
- `external_challenger_evaluation.json`
- `incumbent_parity_report.json`
- `beat_target_contract.json`
- `mission_control_state.json`
- `review_queue_state.json`
- `control_center_layout.json`
- `mode_overview.json`
- `capability_manifest.json`
- `action_affordances.json`
- `stage_navigator.json`
- `question_starters.json`
- `onboarding_status.json`
- `onboarding_chat_session_state.json`
- `install_experience_report.json`
- `launch_manifest.json`
- `demo_session_manifest.json`
- `ui_preferences.json`
- `reports/mission_control.html`
- `dojo_session.json`
- `dojo_hypotheses.json`
- `dojo_results.json`
- `dojo_promotions.json`
- `architecture_proposals.json`
- `pulse_schedule.json`
- `pulse_run_report.json`
- `pulse_skip_report.json`
- `pulse_recommendations.json`
- `innovation_watch_report.json`
- `challenge_watchlist.json`
- `pulse_checkpoint.json`
- `memory_compaction_plan.json`
- `memory_compaction_report.json`
- `memory_pinning_index.json`
- `run_handoff.json`
- `next_run_options.json`
- `next_run_focus.json`
- `reports/user_result_report.md`
- `reports/agent_result_report.md`
- `lab_learnings_snapshot.json`
- `learnings_state.json`
- `learnings.md`
- `trace_model.json`
- `trace_span_log.jsonl`
- `specialist_trace_index.json`
- `tool_trace_log.jsonl`
- `intervention_trace_log.jsonl`
- `branch_trace_graph.json`
- `claim_packet_log.jsonl`
- `adjudication_scorecard.json`
- `decision_replay_report.json`
- `agent_eval_matrix.json`
- `security_eval_report.json`
- `red_team_report.json`
- `protocol_conformance_report.json`
- `host_surface_matrix.json`

## Current Workspace Boundaries

- `src/relaytic/workspace/` now owns Slice 12D workspace state, multi-run lineage, focus history, workspace memory policy, and workspace-backed continuity views
- `src/relaytic/iteration/` now owns Slice 12D next-run planning, focus-decision records, and data-expansion candidates
- `src/relaytic/search/` now owns Slice 13 search-controller plans, portfolio search traces, HPO campaign reports, execution-strategy selection, explicit value-of-search artifacts, and Slice 15I staged search-budget envelopes, probe/race/finalist reports, pruning reports, scorecards, and stop-reason artifacts

Existing Slice 12C handoff and learnings commands remain part of the public compatibility surface. Under Slice 12D they now behave as compatibility-preserving views over workspace-backed truth rather than isolated per-run truth sources.

Current Slice 12D artifact names:
- `workspace_state.json`
- `workspace_lineage.json`
- `workspace_focus_history.json`
- `workspace_memory_policy.json`
- `result_contract.json`
- `confidence_posture.json`
- `belief_revision_triggers.json`
- `next_run_plan.json`
- `focus_decision_record.json`
- `data_expansion_candidates.json`
- `search_controller_plan.json`
- `portfolio_search_trace.json`
- `hpo_campaign_report.json`
- `search_decision_ledger.json`
- `execution_backend_profile.json`
- `device_allocation.json`
- `distributed_run_plan.json`
- `scheduler_job_map.json`
- `checkpoint_state.json`
- `execution_strategy_report.json`
- `search_value_report.json`
- `search_controller_eval_report.json`

## Current Newly-Shipped Boundaries

- `src/relaytic/events/` for Slice 13B typed runtime-event schemas, subscription registries, hook registries, and projection-only event-delivery contracts on top of the canonical runtime event stream
- `src/relaytic/permissions/` for Slice 13B visible permission modes, tool-permission matrices, approval-policy reporting, append-only permission-decision logs, and session capability contracts
- `src/relaytic/daemon/` for Slice 13C bounded background-job orchestration, checkpoint-backed resumability, stale-job reporting, approval-aware execution, and memory-maintenance queues
- `src/relaytic/remote_control/` for Slice 14A remote supervision sessions, approval queues, supervision handoff, remote-control audit, and transport reporting
- `src/relaytic/mission_control/` for Slice 15 branch DAGs, confidence posture, trace explorer state, change attribution, approval timelines, background-job views, permission cards, release-health posture, demo-pack manifests, flagship demo scorecards, and human-factors/onboarding-success reporting
- `src/relaytic/guide/` for Slice 15V-A no-lost guidance, safe action menus, artifact shortlists, optional local-LLM guide summaries, graceful partial-run status fallback support, and redacted external-context exports

## Reserved Future Boundaries

The following boundaries are reserved for the next frontier slices so later implementation can stay sharp without widening the legacy compatibility surface ad hoc:

- `src/relaytic/modeling/families/`, if introduced during Slice 15H, for first-class family-owned trainers, search spaces, adapter shims, and specialization logic rather than one generic trainer path
- `src/relaytic/modeling/portfolio/`, if introduced during Slice 15I, for staged family probing, racing, finalist search, pruning, and budget-envelope logic
- `src/relaytic/temporal/`, if introduced after Slice 15J, for deeper temporal family ownership beyond the currently shipped temporal-engine surfaces in `src/relaytic/analytics/`, `src/relaytic/modeling/`, and `src/relaytic/benchmark/`
- `src/relaytic/benchmark/`, `src/relaytic/aml/`, `src/relaytic/graph_fabric/`, `src/relaytic/casework/`, `src/relaytic/stream_risk/`, and any focused future AML loader or release-freeze package for the remaining AML paper-freeze track in Slice 15Z-R
- `src/relaytic/capability_academy/` for Slice 16 and Slices 16A through 16F capability registries, replay/shadow trials, arena promotion scorecards, hunt campaigns, provider feedback, and non-core specialist recruitment or retirement after the AML pivot lands
- `src/relaytic/representation/` for Slice 17 optional representation engines, latent-state reports, embedding indexes, and JEPA-style pretraining support
- Slice 18 should avoid creating a new package boundary unless absolutely necessary; its job is to remove misleading, duplicated, or legacy boundaries, split oversized modules, retire compatibility shims when the removal criteria are met, and leave the public surface cleaner than before

Implemented release-safety artifact names:
- `release_safety_scan.json`
- `distribution_manifest.json`
- `artifact_inventory.json`
- `artifact_attestation.json`
- `source_map_audit.json`
- `sensitive_string_audit.json`
- `release_bundle_report.json`
- `packaging_regression_report.json`
- `paysim_benchmark_manifest.json`
- `paysim_temporal_split_report.json`
- `paysim_operating_point_table.json`
- `paysim_paper_result_row.json`
- `elliptic_graph_loader_manifest.json`
- `elliptic_graph_provenance_report.json`
- `elliptic_temporal_split_report.json`
- `elliptic_graph_claim_scope.json`
- `elliptic_paper_result_row.json`
- `paper_baseline_suite_manifest.json`
- `paper_baseline_version_matrix.json`
- `paper_tabular_baseline_table.json`
- `paper_baseline_fallback_report.json`
- `paper_benchmark_budget_contract.json`
- `paper_competitive_search_trace.json`
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

Implemented event-bus and permission artifact names:
- `event_schema.json`
- `event_subscription_registry.json`
- `hook_registry.json`
- `hook_dispatch_report.json`
- `permission_mode.json`
- `tool_permission_matrix.json`
- `approval_policy_report.json`
- `permission_decision_log.jsonl`
- `session_capability_contract.json`

Implemented daemon, feasibility, remote-supervision, and mission-control proof artifact names plus reserved later academy and representation names:
- `aml_demo_bundle_manifest.json`
- `aml_demo_business_metric_table.json`
- `aml_demo_flow_report.md`
- `aml_demo_artifact_index.json`
- `aml_investigation_board.json`
- `aml_business_value_report.json`
- `analyst_hour_savings_report.json`
- `review_capacity_metric_report.json`
- `operational_metric_guard.json`
- `aml_baseline_matrix.json`
- `aml_ablation_matrix.json`
- `aml_baseline_adapter_report.json`
- `aml_capability_contribution_report.json`
- `aml_benchmark_relevance_scorecard.json`
- `aml_graph_loader_manifest.json`
- `aml_graph_provenance_report.json`
- `aml_subgraph_task_manifest.json`
- `aml_graph_claim_scope.json`
- `aml_public_graph_benchmark_catalog.json`
- `aml_delayed_label_eval_report.json`
- `aml_positive_unlabeled_posture.json`
- `aml_threshold_drift_report.json`
- `aml_time_window_scorecard.json`
- `aml_temporal_benchmark_claim_report.json`
- `aml_eval_environment_manifest.json`
- `aml_environment_scorecard.json`
- `aml_workflow_task_matrix.json`
- `aml_environment_failure_report.json`
- `aml_benchmark_environment_scorecard.json`
- `pre_academy_repo_audit.json`
- `module_extraction_plan.json`
- `daemon_state.json`
- `background_job_registry.json`
- `background_job_log.jsonl`
- `background_checkpoint.json`
- `resume_session_manifest.json`
- `background_approval_queue.json`
- `memory_maintenance_queue.json`
- `memory_maintenance_report.json`
- `search_resume_plan.json`
- `stale_job_report.json`
- `deployability_assessment.json`
- `review_gate_state.json`
- `constraint_override_request.json`
- `counterfactual_region_report.json`
- `remote_session_manifest.json`
- `remote_transport_report.json`
- `approval_request_queue.json`
- `approval_decision_log.jsonl`
- `remote_operator_presence.json`
- `supervision_handoff.json`
- `notification_delivery_report.json`
- `remote_control_audit.json`
- `branch_dag.json`
- `confidence_map.json`
- `change_attribution_report.json`
- `trace_explorer_state.json`
- `branch_replay_index.json`
- `approval_timeline.json`
- `background_job_view.json`
- `permission_mode_card.json`
- `release_health_report.json`
- `demo_pack_manifest.json`
- `flagship_demo_scorecard.json`
- `human_factors_eval_report.json`
- `onboarding_success_report.json`
- `optimization_objective_contract.json`
- `objective_alignment_report.json`
- `split_diagnostics_report.json`
- `temporal_fold_health.json`
- `metric_materialization_audit.json`
- `benchmark_truth_precheck.json`
- `family_registry_extension.json`
- `family_readiness_report.json`
- `family_eligibility_matrix.json`
- `family_probe_policy.json`
- `categorical_strategy_report.json`
- `family_specialization_report.json`
- `search_budget_envelope.json`
- `probe_stage_report.json`
- `family_race_report.json`
- `finalist_search_plan.json`
- `multi_fidelity_pruning_report.json`
- `portfolio_search_scorecard.json`
- `search_stop_reason.json`
- `temporal_structure_report.json`
- `temporal_feature_ladder.json`
- `rolling_cv_plan.json`
- `temporal_split_guard_report.json`
- `sequence_shadow_scorecard.json`
- `temporal_baseline_ladder.json`
- `temporal_metric_contract.json`
- `calibration_strategy_report.json`
- `operating_point_contract.json`
- `threshold_search_report.json`
- `decision_cost_profile.json`
- `review_budget_optimization_report.json`
- `abstention_policy_report.json`
- `trace_identity_conformance.json`
- `benchmark_truth_audit.json`
- `paper_claim_guard_report.json`
- `eval_surface_parity_report.json`
- `benchmark_release_gate.json`
- `dataset_leakage_audit.json`
- `capability_registry.json`
- `capability_card_log.jsonl`
- `capability_intake_record.json`
- `capability_risk_profile.json`
- `offline_replay_scorecard.json`
- `shadow_trial_report.json`
- `shadow_disagreement_log.jsonl`
- `shadow_counterfactual_win_report.json`
- `capability_arena_scorecard.json`
- `promotion_candidate_ranking.json`
- `promotion_decision_report.json`
- `capability_registry_update.json`
- `hunt_campaign_state.json`
- `hunt_target_selection.json`
- `hunt_candidate_log.jsonl`
- `hunt_outcome_report.json`
- `provider_feedback_report.json`
- `exploration_budget_report.json`
- `exploration_seed_log.jsonl`
- `specialist_candidate_queue.json`
- `recruitment_decision_report.json`
- `specialist_trial_report.json`
- `capability_retirement_report.json`
- `roster_change_log.jsonl`
- `academy_state.json`
- `academy_registry_view.json`
- `academy_trial_dashboard.json`
- `academy_hunt_view.json`
- `academy_promotion_timeline.json`
- `academy_explanation_report.json`
- `representation_engine_profile.json`
- `latent_state_report.json`
- `embedding_index_report.json`
- `representation_transfer_report.json`
- `representation_ood_report.json`
- `jepa_pretraining_report.json`

## Removal Criteria

The remaining compatibility layer can be removed when all of the following are true:

1. tests no longer depend on `corr2surrogate` imports
2. docs and examples no longer mention legacy package paths except historical notes
3. runtime paths no longer require `C2S_*` fallbacks
4. the next stable slices no longer rely on compatibility forwarding
