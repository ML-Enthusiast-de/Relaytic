# Relaytic Architecture Contract

This file freezes the load-bearing contracts that later slices must obey.

## Public Product Surface

- Product name: `Relaytic`
- Descriptor: `The Relay Inference Lab`
- Canonical package: `relaytic`
- Canonical CLI: `relaytic`
- Compatibility package: `corr2surrogate` for import fallback only

New docs, code, examples, and tests must target `relaytic`.

## Package Boundary

Current package rule:

- `src/relaytic/` is canonical
- `src/relaytic/intake/` owns Slice 04 intake translation and interpretation artifacts
- `src/relaytic/investigation/` owns Slice 03 specialist-agent investigation and focus artifacts
- `src/relaytic/planning/` owns Slice 05 Strategist planning, Builder handoff, and planning artifact persistence
- `src/relaytic/runs/` owns Slice 05A MVP-access summaries and human-readable run presentation
- `src/relaytic/evidence/` owns Slice 06 challenger, ablation, audit, leaderboard, and evidence-report artifacts
- `src/relaytic/completion/` owns Slice 07 completion-governor logic and artifact persistence
- `src/relaytic/lifecycle/` owns Slice 08 lifecycle-governor logic and artifact persistence
- `src/relaytic/memory/` owns Slice 09A analog retrieval, route priors, challenger priors, reflection memory, and memory artifact persistence
- `src/relaytic/runtime/` owns Slice 09B local gateway, append-only event stream, hook dispatch, checkpoints, and capability-profile enforcement
- `src/relaytic/intelligence/` owns Slice 09 and Slice 09F structured semantic tasks, semantic debate/verifier flows, backend discovery, routed intelligence profiles, and document-grounding orchestration
- `src/relaytic/autonomy/` owns Slice 09C bounded autonomy loops, executable lifecycle follow-up, challenger queues, and champion-lineage management
- `src/relaytic/benchmark/` owns Slice 11 reference-approach comparison, parity-gap reporting, and benchmark artifact persistence
- `src/relaytic/assist/` owns Slice 09E communicative assistance, stage-navigation planning, optional takeover coordination, and connection-guide persistence
- `src/relaytic/interoperability/` owns Slice 08A host-neutral MCP serving, host-bundle generation, and interoperability self-checks
- `src/relaytic/integrations/` owns optional third-party capability discovery and adapter-scoped inventory surfaces
- `src/corr2surrogate/` is a temporary shim that forwards legacy imports

Current canonical boundaries:

- `src/relaytic/research/` owns Slice 09D redacted external research retrieval, source inventory, method-transfer distillation, benchmark-reference harvesting, and research-audit persistence
- `src/relaytic/feedback/` owns Slice 10 validated feedback, outcome learning, reversible effect reporting, and rollback-ready casebook state
- `src/relaytic/profiles/` owns Slice 10B quality contracts, budget contracts, operator/lab profile overlays, and budget-consumption reporting
- `src/relaytic/control/` owns Slice 10C intervention contracts, skeptical override handling, control-injection auditing, recovery checkpoints, control-ledger persistence, and causal steering-memory artifacts
- `src/relaytic/decision/` owns Slice 10A decision-world models, intervention policy, decision usefulness, controller-policy writing, and value-of-more-data reasoning
- `src/relaytic/compiler/` owns Slice 10A method compilation, executable challenger templates, compiled feature hypotheses, and compiled benchmark protocols
- `src/relaytic/data_fabric/` owns Slice 10A source-graph reasoning, join-candidate analysis, entity-history understanding, and acquisition planning
- `src/relaytic/benchmark/`, `src/relaytic/evidence/`, and `src/relaytic/lifecycle/` now also own Slice 11A imported-incumbent evaluation, incumbent parity reporting, and beat-target contracts
- `src/relaytic/mission_control/` owns Slice 11B mission-control MVP state, onboarding/install-health state, review-queue state, launch metadata, static control-center rendering, Slice 11C clarity surfaces for modes/capabilities/actions/navigation/questions, Slice 11D guided onboarding plus live terminal mission-control chat surfaces, Slice 11E role-specific handbook discovery and handbook-aware onboarding surfaces, Slice 11F demo-grade onboarding, explicit mode education, stuck recovery, recruiter-safe walkthrough surfaces, Slice 11G adaptive human onboarding capture plus lightweight local semantic guidance surfaces, and Slice 15 branch DAG, confidence map, trace exploration, change-attribution, approval-timeline, background-job, release-health, demo-pack, and human-factors surfaces
- `src/relaytic/dojo/` owns Slice 12 guarded self-improvement controls, quarantined proposal bundles, validation results, promotion ledgers, rollback state, and architecture-proposal quarantine
- `src/relaytic/pulse/` owns Slice 12A periodic awareness scheduling, innovation-watch gathering, pulse recommendations, skip reporting, bounded pulse-run persistence, explicit memory-maintenance orchestration, and pulse-to-mission-control visibility surfaces
- `src/relaytic/tracing/` owns Slice 12B canonical trace schemas, specialist/tool/intervention/branch span persistence, claim-packet persistence, deterministic adjudication scorecards, replay reports, and replay/query surfaces
- `src/relaytic/evals/` owns Slice 12B agent-behavior evaluation, security harnesses, protocol-conformance checks, adversarial steering tests, runtime regression packs, scenario/result matrices, and Slice 15 human-supervision/onboarding evaluation reports
- `src/relaytic/handoff/` owns Slice 12C differentiated post-run handoff generation, next-run options, persisted next-run focus, and differentiated report rendering for humans and external agents
- `src/relaytic/learnings/` owns Slice 12C durable local learnings state, learnings markdown, per-run learnings snapshots, and workspace learnings reset behavior
- `src/relaytic/workspace/` owns Slice 12D workspace state, multi-run lineage, focus history, workspace memory policy, and workspace-backed continuity views
- `src/relaytic/iteration/` owns Slice 12D next-run planning, focus-decision records, data-expansion candidates, and workspace continuation decisions
- `src/relaytic/search/` owns Slice 13 search-controller plans, portfolio search traces, HPO campaign reports, bounded branch widening/pruning, execution-backend selection, checkpoint posture, and explicit value-of-search evaluation artifacts
- `src/relaytic/release_safety/` owns Slice 13A release-bundle scanning, workspace-only pre-release scans, artifact attestation, source-map and sensitive-string audits, distribution-manifest reporting, packaging-regression reporting, and doctor-visible release posture
- `src/relaytic/events/` owns Slice 13B typed runtime event schemas, subscription registries, hook registries, and projection-only event-delivery contracts on top of the canonical runtime event stream
- `src/relaytic/permissions/` owns Slice 13B visible permission modes, tool-permission matrices, approval-policy reporting, append-only permission-decision logs, and session capability contracts
- `src/relaytic/daemon/` owns Slice 13C bounded background-job orchestration, checkpoint-backed resumability, stale-job reporting, approval-aware execution, and memory-maintenance queues
- `src/relaytic/remote_control/` owns Slice 14A remote supervision sessions, approval queues, supervision handoff, remote-control audit, and transport reporting

Reserved future boundaries:

- `src/relaytic/analytics/`, `src/relaytic/planning/`, `src/relaytic/modeling/`, `src/relaytic/memory/`, `src/relaytic/runs/`, `src/relaytic/assist/`, `src/relaytic/ui/`, `src/relaytic/search/`, `src/relaytic/benchmark/`, `src/relaytic/research/`, `src/relaytic/compiler/`, `src/relaytic/decision/`, `src/relaytic/runtime/`, and `src/relaytic/workspace/` now absorb the shipped Slice 15A through Slice 15L task-contract, architecture-routing, bounded-HPO, paper-grade benchmark, freshness-aware artifact-reuse, replay/shadow-tested imported-model, objective/split/metric-truth, first-class family-stack, staged portfolio-search, temporal-engine, operating-point, and benchmark-truth-gate responsibilities; later work should keep strengthening those same boundaries and may introduce focused subpackages such as `src/relaytic/modeling/families/`, `src/relaytic/modeling/portfolio/`, or `src/relaytic/temporal/` only if they sharpen responsibility instead of forking a disconnected parallel stack
- `src/relaytic/capability_academy/` should own Slice 16 and Slices 16A through 16F capability registries, replay/shadow trials, arena promotion scorecards, hunt campaigns, provider feedback, non-core specialist recruitment or retirement, and academy-state rendering
- `src/relaytic/representation/` should own Slice 17 optional representation engines, latent-state reports, embedding indexes, and JEPA-style pretraining support
- Slice 18 should be a cross-cutting consolidation and remediation slice rather than a feature-expansion boundary; by default it should remove misleading or redundant packages, split oversized modules, and retire legacy surfaces instead of introducing a new permanent package

Later slices may remove the shim only after `MIGRATION_MAP.md` and `IMPLEMENTATION_STATUS.md` are updated.

## Control Documents

These files are required and must stay current:

- `ARCHITECTURE_CONTRACT.md`
- `IMPLEMENTATION_STATUS.md`
- `MIGRATION_MAP.md`
- `docs/build_slices/phase_00.md`
- `docs/build_slices/phase_01.md`
- `docs/build_slices/phase_02.md`
- `docs/build_slices/phase_03.md`
- `docs/build_slices/phase_04.md`
- `docs/build_slices/phase_05.md`
- `docs/build_slices/phase_05a.md`
- `docs/build_slices/phase_06.md`
- `docs/build_slices/phase_07.md`
- `docs/build_slices/phase_08.md`
- `docs/build_slices/phase_08a.md`
- `docs/build_slices/phase_08b.md`
- `docs/build_slices/phase_09.md`
- `docs/build_slices/phase_09a.md`
- `docs/build_slices/phase_09b.md`
- `docs/build_slices/phase_09c.md`
- `docs/build_slices/phase_09d.md`
- `docs/build_slices/phase_09e.md`
- `docs/build_slices/phase_09f.md`
- `docs/build_slices/phase_10.md`
- `docs/build_slices/phase_10b.md`
- `docs/build_slices/phase_10c.md`
- `docs/build_slices/phase_10a.md`
- `docs/build_slices/phase_11.md`
- `docs/build_slices/phase_11a.md`
- `docs/build_slices/phase_11b.md`
- `docs/build_slices/phase_11c.md`
- `docs/build_slices/phase_11d.md`
- `docs/build_slices/phase_11e.md`
- `docs/build_slices/phase_11f.md`
- `docs/build_slices/phase_11g.md`
- `docs/build_slices/phase_12.md`
- `docs/build_slices/phase_12a.md`
- `docs/build_slices/phase_12b.md`
- `docs/build_slices/phase_12c.md`
- `docs/build_slices/phase_12d.md`
- `docs/build_slices/phase_13.md`
- `docs/build_slices/phase_13a.md`
- `docs/build_slices/phase_13b.md`
- `docs/build_slices/phase_13c.md`
- `docs/build_slices/phase_14.md`
- `docs/build_slices/phase_14a.md`
- `docs/build_slices/phase_15.md`
- `docs/build_slices/phase_15a.md`
- `docs/build_slices/phase_15b.md`
- `docs/build_slices/phase_15c.md`
- `docs/build_slices/phase_15d.md`
- `docs/build_slices/phase_15e.md`
- `docs/build_slices/phase_15f.md`
- `docs/build_slices/phase_15g.md`
- `docs/build_slices/phase_15h.md`
- `docs/build_slices/phase_15i.md`
- `docs/build_slices/phase_15j.md`
- `docs/build_slices/phase_15k.md`
- `docs/build_slices/phase_15l.md`
- `docs/build_slices/phase_16.md`
- `docs/build_slices/phase_16a.md`
- `docs/build_slices/phase_16b.md`
- `docs/build_slices/phase_16c.md`
- `docs/build_slices/phase_16d.md`
- `docs/build_slices/phase_16e.md`
- `docs/build_slices/phase_16f.md`
- `docs/build_slices/phase_17.md`
- `docs/build_slices/phase_18.md`
- `docs/specs/workspace_lifecycle.md`
- `docs/specs/result_contract_schema.md`
- `docs/specs/governed_learnings_schema.md`
- `docs/specs/model_competitiveness_contract.md`
- `docs/specs/performance_recovery_contract.md`
- `docs/specs/temporal_benchmark_pack.md`
- `docs/specs/capability_academy_contract.md`
- `docs/specs/mission_control_contract.md`
- `docs/specs/handoff_result_migration.md`
- `docs/specs/learnings_migration_contract.md`
- `docs/specs/external_agent_continuation_contract.md`
- `docs/specs/mission_control_flows.md`
- `docs/specs/test_and_proof_matrix.md`
- `docs/specs/flagship_demo_pack.md`

The `docs/specs/` files are normative product-contract documents for future slices. If a later slice changes workspace continuity, result rendering, learnings behavior, mission-control flow, testing burden, or flagship demo expectations, those docs must be updated in the same change.

## Artifact Contract

The current slices must preserve these names:

- `manifest.json`
- `policy_resolved.yaml`
- `data_copy_manifest.json`
- `lab_mandate.json`
- `work_preferences.json`
- `run_brief.json`
- `data_origin.json`
- `domain_brief.json`
- `task_brief.json`
- `intake_record.json`
- `autonomy_mode.json`
- `clarification_queue.json`
- `assumption_log.json`
- `context_interpretation.json`
- `context_constraints.json`
- `semantic_mapping.json`
- `dataset_profile.json`
- `domain_memo.json`
- `objective_hypotheses.json`
- `focus_debate.json`
- `focus_profile.json`
- `optimization_profile.json`
- `feature_strategy_profile.json`
- `plan.json`
- `alternatives.json`
- `hypotheses.json`
- `experiment_priority_report.json`
- `marginal_value_of_next_experiment.json`
- `run_summary.json`
- `reports/summary.md`
- `experiment_registry.json`
- `challenger_report.json`
- `ablation_report.json`
- `audit_report.json`
- `belief_update.json`
- `leaderboard.csv`
- `reports/technical_report.md`
- `reports/decision_memo.md`
- `completion_decision.json`
- `run_state.json`
- `stage_timeline.json`
- `mandate_evidence_review.json`
- `blocking_analysis.json`
- `next_action_queue.json`
- `champion_vs_candidate.json`
- `recalibration_decision.json`
- `retrain_decision.json`
- `promotion_decision.json`
- `rollback_decision.json`
- `intelligence_mode.json`
- `llm_routing_plan.json`
- `local_llm_profile.json`
- `llm_backend_discovery.json`
- `llm_health_check.json`
- `llm_upgrade_suggestions.json`
- `semantic_task_request.json`
- `semantic_task_results.json`
- `intelligence_escalation.json`
- `verifier_report.json`
- `semantic_debate_report.json`
- `semantic_counterposition_pack.json`
- `semantic_uncertainty_report.json`
- `semantic_proof_report.json`
- `memory_retrieval.json`
- `analog_run_candidates.json`
- `route_prior_context.json`
- `challenger_prior_suggestions.json`
- `reflection_memory.json`
- `memory_flush_report.json`
- `semantic_access_audit.json`
- `lab_event_stream.jsonl`
- `hook_execution_log.json`
- `run_checkpoint_manifest.json`
- `capability_profiles.json`
- `data_access_audit.json`
- `context_influence_report.json`
- `autonomy_loop_state.json`
- `autonomy_round_report.json`
- `challenger_queue.json`
- `branch_outcome_matrix.json`
- `retrain_run_request.json`
- `recalibration_run_request.json`
- `champion_lineage.json`
- `loop_budget_report.json`
- `research_query_plan.json`
- `research_source_inventory.json`
- `research_brief.json`
- `method_transfer_report.json`
- `benchmark_reference_report.json`
- `external_research_audit.json`
- `feedback_intake.json`
- `feedback_validation.json`
- `feedback_effect_report.json`
- `feedback_casebook.json`
- `outcome_observation_report.json`
- `decision_policy_update_suggestions.json`
- `policy_update_suggestions.json`
- `route_prior_updates.json`
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
- `reference_approach_matrix.json`
- `benchmark_gap_report.json`
- `benchmark_parity_report.json`
- `external_challenger_manifest.json`
- `external_challenger_evaluation.json`
- `incumbent_parity_report.json`
- `beat_target_contract.json`
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
- `assist_mode.json`
- `assist_session_state.json`
- `assistant_connection_guide.json`
- `assist_turn_log.jsonl`
- `context_assembly_report.json`
- `doc_grounding_report.json`

Current mission-control artifact names:

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

Current dojo artifact names:

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

Current handoff and learnings artifact names:

- `run_handoff.json`
- `next_run_options.json`
- `next_run_focus.json`
- `reports/user_result_report.md`
- `reports/agent_result_report.md`
- `lab_learnings_snapshot.json`
- `learnings_state.json`
- `learnings.md`

These Slice 12C artifacts remain the current public per-run handoff and learnings surfaces. Slice 12D must build workspace-backed continuity on top of them rather than silently replacing or renaming them.

Current workspace and iteration artifact names:

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

Current task-contract artifact names:

- `task_profile_contract.json`
- `target_semantics_report.json`
- `metric_contract.json`
- `benchmark_mode_report.json`
- `deployment_readiness_report.json`
- `benchmark_vs_deploy_report.json`
- `dataset_semantics_audit.json`

Current architecture-routing artifact names:

- `architecture_registry.json`
- `architecture_router_report.json`
- `candidate_family_matrix.json`
- `architecture_fit_report.json`
- `family_capability_matrix.json`
- `architecture_ablation_report.json`

Current trace and eval artifact names:

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

Current search-controller artifact names:

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

Reserved future artifact names:
- `release_safety_scan.json`
- `distribution_manifest.json`
- `artifact_inventory.json`
- `artifact_attestation.json`
- `source_map_audit.json`
- `sensitive_string_audit.json`
- `release_bundle_report.json`
- `packaging_regression_report.json`
- `event_schema.json`
- `event_subscription_registry.json`
- `hook_registry.json`
- `hook_dispatch_report.json`
- `permission_mode.json`
- `tool_permission_matrix.json`
- `approval_policy_report.json`
- `permission_decision_log.jsonl`
- `session_capability_contract.json`
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
- `representation_engine_profile.json`
- `latent_state_report.json`
- `embedding_index_report.json`
- `representation_transfer_report.json`
- `representation_ood_report.json`
- `jepa_pretraining_report.json`

When `relaytic plan run` executes the Builder handoff, the run directory must also contain:

- `model_params.json`
- `normalization_state.json` when normalization is enabled
- `model_state.json` or `<selected_model>_state.json`
- `checkpoints/ckpt_*.json`

When staged dataset copies exist, the run directory must also contain:

- `data_copies/`

## Data Handling Contract

Current public ingestion formats are:

- `.csv`
- `.tsv`
- `.xlsx`
- `.xls`
- `.parquet`
- `.pq`
- `.feather`
- `.json`
- `.jsonl`
- `.ndjson`

Current public local source modes are:

- snapshot files in the formats above
- append-only local stream files materialized into bounded run-local snapshots
- local lakehouse-style sources materialized into bounded run-local snapshots

The current public MVP must stage immutable working copies under `data_copies/` before major run and inference work.

Required behavior:

- `relaytic run` must operate on a staged primary copy rather than the original source file
- `relaytic predict` must operate on a staged inference copy rather than the original source file
- `relaytic source materialize` must create an immutable run-local snapshot rather than mutating the source
- Relaytic must not write back to the original source file during normal run or inference flows
- `data_copy_manifest.json` must record purpose, staged path, and integrity metadata for staged copies
- `data_copy_manifest.json` must not persist original absolute source paths

Remote streaming, warehouse, cloud lakehouse, and datalake connectors remain future adapter surfaces and are not part of the current guaranteed public contract.

## CLI Contract

The public CLI command is `relaytic`.

Minimum guaranteed surfaces at this stage:

- `relaytic --help`
- `relaytic manifest init`
- `relaytic policy resolve`
- `relaytic mandate init`
- `relaytic mandate show`
- `relaytic context init`
- `relaytic context show`
- `relaytic foundation init`
- `relaytic intake interpret`
- `relaytic intake show`
- `relaytic intake questions`
- `relaytic investigate`
- `relaytic plan create`
- `relaytic plan run`
- `relaytic plan show`
- `relaytic evidence run`
- `relaytic evidence show`
- `relaytic status`
- `relaytic completion review`
- `relaytic lifecycle review`
- `relaytic lifecycle show`
- `relaytic memory retrieve`
- `relaytic memory show`
- `relaytic runtime show`
- `relaytic runtime events`
- `relaytic intelligence run`
- `relaytic intelligence show`
- `relaytic research gather`
- `relaytic research show`
- `relaytic research sources`
- `relaytic benchmark run`
- `relaytic benchmark show`
- `relaytic assist show`
- `relaytic assist turn`
- `relaytic assist chat`
- `relaytic autonomy run`
- `relaytic autonomy show`
- `relaytic run`
- `relaytic show`
- `relaytic predict`
- `relaytic source inspect`
- `relaytic source materialize`
- `relaytic doctor`
- `relaytic interoperability show`
- `relaytic interoperability self-check`
- `relaytic interoperability export`
- `relaytic interoperability serve-mcp`
- `relaytic integrations show`
- `relaytic integrations self-check`
- `relaytic setup-local-llm`
- `relaytic run-agent-session`
- `relaytic run-agent1-analysis`
- `relaytic run-inference`
- `relaytic scan-git-safety`

## Slice 05 Planning Contract

- Strategist must consume foundation plus investigation artifacts, not raw prose alone
- planning must emit a concrete Builder handoff inside `plan.json`
- planning must distinguish hard feature guardrails from soft heuristic risk signals
- `relaytic plan run` must execute the first deterministic route inside the same run directory that holds planning artifacts
- local LLMs may add bounded planning advice, but the planning floor must remain deterministic

## Slice 05A Access Contract

- `relaytic run` must remain a thin orchestration shell over intake, investigation, planning, and evidence rather than replacing those layers
- `relaytic show` must be able to summarize older run directories by materializing `run_summary.json` on demand
- `relaytic predict` must expose the same deterministic inference capability as `run-inference` through a simpler run-dir-first surface
- `run_summary.json` must remain machine-readable and stable for agent consumption
- `reports/summary.md` must remain concise and readable for humans

## Slice 06 Evidence Contract

- the evidence layer must treat the selected Builder route as a challengeable champion, not an unquestioned winner
- Slice 06 must produce one real challenger branch, one bounded ablation suite, one provisional audit, and one machine-readable belief update
- `relaytic evidence run` must be able to attach evidence to an already executed planning run or autonomously ensure planning execution exists first
- `relaytic evidence show` must expose a concise human memo and a stable JSON payload for external agents
- the evidence layer may use bounded local-LLM advisory help for memo refinement, but the challenger, ablation, and audit floor must remain deterministic

## Slice 07 Completion Contract

- the completion layer must consume mandate, context, intake, investigation, planning, and evidence artifacts together rather than mirroring only the last-stage recommendation
- Slice 07 must output a machine-actionable completion decision, a visible workflow state, a mandate-vs-evidence review, and an explicit blocking analysis
- completion must be able to diagnose whether the current weakness is route narrowness, evidence insufficiency, unresolved semantic ambiguity, missing benchmark context, missing memory support, or policy/operator constraint
- the completion layer must expose a stable next-action queue that humans and external agents can follow without reading long prose first
- completion must emit explicit handoffs when memory support or benchmark proof is the real limiting factor rather than pretending the current run is self-sufficient
- `completion_decision.json` must use a stable action vocabulary chosen from: `stop_for_now`, `continue_experimentation`, `review_challenger`, `collect_more_data`, `benchmark_needed`, `memory_support_needed`, `recalibration_candidate`, `retrain_candidate`
- `completion_decision.json` must at minimum expose: `action`, `confidence`, `current_stage`, `blocking_layer`, `mandate_alignment`, `evidence_state`, `complete_for_mode`, and `reason_codes`
- `next_action_queue.json` entries must be machine-actionable and include at minimum: `action`, `priority`, `reason_code`, `source_artifact`, and `blocking`
- completion may use bounded local-LLM help for explanation polish, but the completion decision itself must remain deterministic and auditable

## Slice 08 Lifecycle Contract

- lifecycle must consume current evidence, completion state, and fresh-data behavior together rather than only a single scalar score
- lifecycle must distinguish `keep_current_champion`, `promote_challenger`, `recalibrate`, `retrain`, and `rollback_required` as separate machine-readable outcomes
- `champion_vs_candidate.json` must expose the current champion, first challenger, fresh-data behavior, and adapter-slot visibility in one artifact
- `recalibration_decision.json`, `retrain_decision.json`, `promotion_decision.json`, and `rollback_decision.json` must each carry an explicit `action`, `confidence`, `reason_codes`, and `next_step`
- `relaytic lifecycle review` must be able to materialize Slice 08 from an already completed MVP run without requiring manual slice-by-slice rebuilding
- lifecycle may expose optional uncertainty, monitoring, registry, and observability adapter slots, but canonical lifecycle judgment must remain deterministic and auditable

## Slice 08A Interoperability Contract

- interoperability must expose a Relaytic-owned, host-neutral MCP tool contract instead of relying on vendor-specific wrappers as the source of truth
- the MCP surface must support `stdio` for local agent hosts and `streamable-http` for connector-style deployments
- the checked-in host bundles must remain secret-free, machine-path-free, and local-first by default
- `relaytic interoperability self-check` must verify bundle drift and be able to run a live local stdio smoke check
- the interoperability surface must include at least one compact health tool that is safe to call before larger run operations
- host adapters for Claude, Codex/OpenAI, OpenClaw, and ChatGPT-facing guidance must remain thin wrappers over the same Relaytic MCP/CLI contract
- public HTTPS exposure of `/mcp` is never the default; remote deployment guidance must require trusted TLS and authentication controls

## Slice 08B Host Activation Contract

- `relaytic interoperability show` must expose per-host discovery state, activation requirements, and the next step needed to make Relaytic callable from that host
- host readiness must distinguish repo-local auto-discovery, workspace-local auto-discovery, and remote connector registration instead of flattening them into a single "ready" label
- OpenClaw workspace discovery must be supported through a checked-in `skills/relaytic/SKILL.md` mirror inside the repository root
- ChatGPT-facing guidance must say explicitly that repository files are not auto-discovered and that a public HTTPS `/mcp` endpoint still must be registered as a connector
- activation metadata must remain machine-readable so other agents can decide whether Relaytic is callable now or still needs user setup

## Slice 09 Intelligence Contract

- intelligence amplification must use one canonical semantic-task contract rather than ad hoc prompt calls spread across subsystems
- semantic tasks must be JSON-only, schema-validated, policy-bound, and artifact-backed
- context assembly for semantic work must be capability-aware and rowless by default
- document grounding must rely on explicit local artifacts or operator-supplied documents rather than ambient hidden knowledge
- Relaytic must emit machine-readable reports showing what context was assembled, what documents were used, and whether richer-than-summary access was granted
- backend discovery, health, and escalation artifacts must explain why Relaytic stayed deterministic or escalated to stronger semantic help
- semantically amplified internal discussion must emit extracted facts, competing hypotheses, counterarguments, verifier findings, and uncertainty notes rather than free-form advisory prose
- semantically amplified challenger, completion, and retraining reasoning must go through the same bounded semantic-task contract instead of hidden model-specific prompt paths

## Slice 09C Autonomy Contract

- completion and lifecycle actions with clear reasons and available budget must be able to trigger bounded second-pass execution instead of stopping at reports only
- bounded autonomy must support challenger expansion, recalibration pass, retrain pass, and re-plan-with-counterposition as explicit loop actions
- every autonomous round must write loop state, budget consumption, branch choice, outcome, and updated champion lineage as inspectable artifacts
- autonomous loops must stop on budget exhaustion, repeated non-improvement, policy conflict, or confidence plateau rather than drifting into open-ended search
- challenger science must be able to grow from one challenger branch into a small bounded portfolio when route narrowness or challenger pressure is detected
- deterministic fallback must remain available: when autonomous execution is disabled, Relaytic still emits the same branch requests and loop recommendations as artifacts

## Slice 09D Research Contract

- external research retrieval must be policy-gated, optional, and non-authoritative
- the public surface centers on `relaytic research gather`, `relaytic research show`, and `relaytic research sources`
- research queries must default to redacted, rowless, generalized run signatures rather than raw rows, private identifiers, or proprietary schema details
- research outputs must distinguish source tier and source type such as paper, benchmark reference, library docs, reference repo, or operator-supplied document
- retrieved content must be distilled into explicit method-transfer and benchmark-reference artifacts rather than hidden prompt context
- planning, evidence, autonomy, and benchmark design may consume research artifacts, but local evidence remains the final arbiter of route changes
- every external research call must emit an audit artifact showing what was sent, what was redacted, what sources were used, and whether richer disclosure was policy-authorized
- deterministic fallback must remain available: if external research is disabled or unavailable, Relaytic still runs with current local artifacts, priors, memory, and semantic layers only

## Slice 09E Assist Contract

- communicative assist must remain deterministic-first, optional, and fully local by default
- the public surface centers on `relaytic assist show`, `relaytic assist turn`, and `relaytic assist chat`
- assist turns must work for both humans and external agents through the same structured contract
- assist must be able to explain current state, rerun from a bounded stage, and take over safely when policy allows
- assist must not require an LLM; local semantic lift is optional and should remain an enhancement rather than the control plane
- connection guidance must explain both lightweight local options and local host-connection options without implying any public exposure is required
- assist stage navigation must refresh downstream artifacts so the run remains coherent after a jump-back request
- every assist turn that changes state must be persisted in an explicit turn log rather than disappearing as ephemeral chat

## Slice 09F Routed Intelligence Contract

- Relaytic must expose the canonical semantic modes `none`, `local_min`, `assist`, `amplify`, and `max_reasoning` through explicit routing artifacts rather than leaving mode interpretation implicit
- routed intelligence must remain policy-bound, deterministic-safe, and local-first by default even when stronger semantic backends are available
- one local profile selection artifact must explain which baseline or stronger local profile was chosen or recommended and why
- backend discovery must expose a bounded capability matrix relevant to schema-constrained semantic work
- verifier output must be written as its own artifact so downstream layers can inspect verifier deltas without reparsing broader debate packets
- semantic amplification must emit a proof artifact that compares routed semantic outputs against a deterministic semantic baseline and states whether measurable bounded gain occurred
- `relaytic intelligence show`, `relaytic show`, and the MCP intelligence surface must all expose routed mode, recommended mode, selected local profile, and semantic proof posture consistently

## Slice 11 Benchmark Contract

- benchmark parity work must live behind one canonical `relaytic benchmark` surface rather than being scattered across reports only
- the public surface centers on `relaytic benchmark run` and `relaytic benchmark show`
- benchmark comparison must use the same split contract and primary-metric contract as the evaluated Relaytic route unless policy explicitly records a justified deviation
- the benchmark layer must persist a reference matrix, a gap report, and a parity report as explicit artifacts rather than hidden score tables
- benchmark output must distinguish ordinary parity, near parity, clear underperformance, and constrained/operator-aware advantage rather than collapsing all outcomes into pass/fail
- benchmark output must explain whether the observed gap is more attributable to route quality, challenger breadth, recalibration/calibration policy, uncertainty handling, or loop policy
- benchmark review must remain honest when a strong reference stack is unavailable; it may degrade to available deterministic references instead of inventing unsupported superiority claims
- optional stronger baselines such as FLAML or MAPIE-backed uncertainty comparisons may appear behind adapters, but deterministic scikit-learn reference comparisons remain the baseline floor

## Slice 09A Memory Contract

- run memory must be advisory and provenance-bearing rather than silently authoritative
- memory retrieval must surface analog candidates, route priors, and challenger priors as explicit artifacts
- memory-aware planning, evidence, completion, and lifecycle review must always be able to explain what changed because memory was available
- `analog_run_candidates.json` entries must include provenance and a comparable-score explanation rather than only a free-form note
- on-disk Relaytic artifacts remain the canonical memory truth; any retrieval index or embedding structure must be derived and disposable
- memory retrieval should prefer summaries, priors, reflections, and artifact-derived signals over raw-row persistence whenever practical
- Relaytic must be able to flush reflection memory and retrieval deltas to disk before completion or lifecycle finalization
- `relaytic memory retrieve` must be able to enrich an existing run directory without requiring the user to rebuild the entire run from scratch
- `relaytic memory show` and `relaytic show` must both expose the current memory delta in a machine-readable way

## Slice 09B Runtime Contract

- the runtime layer must provide one local-first control plane for run state transitions, event emission, and hook dispatch across CLI, MCP, and later UI surfaces
- `lab_event_stream.jsonl` must be append-only and rich enough to reconstruct stage transitions, retries, fallbacks, approvals, and major branch decisions
- hooks must default to read-only, local-only, and run-dir-scoped; broader write scope requires explicit policy and auditability
- every specialist must declare a capability profile covering artifact read scope, artifact write scope, raw-row access, semantic access, and external-adapter access
- semantic helpers and optional LLM-backed specialists must consume rowless summaries by default unless policy explicitly grants richer context
- the runtime must be able to checkpoint and flush state before retry, compaction, or final completion/lifecycle transitions
- future mission-control surfaces must consume the same runtime and artifact graph rather than building a separate UI-only state model
- future decision-world-model logic must stay advisory to planning, autonomy, completion, and lifecycle and must not silently replace deterministic metrics, calibration math, or artifact persistence
- future method-compilation logic must emit explicit compiled artifacts instead of hidden prompt context or silent route rewrites

## Slice 10B Quality/Budget/Profile Contract

- Relaytic must materialize one explicit quality contract and one explicit budget contract when run-scope inputs are absent instead of leaving those defaults implicit
- operator and lab profile overlays may shape review posture, benchmark appetite, explanation style, abstain/review preference, and budget posture, but they must not silently override deterministic metrics, model outcomes, or artifact truth
- quality/budget/profile surfaces must be visible through CLI, MCP, assist, and summary outputs instead of living only in config files
- quality-gate reporting must explain why Relaytic continued, recalibrated, retrained, asked for more data, or stopped in terms of the explicit contract it consumed
- later decision-world-model and search-controller slices must consume these contracts rather than inventing hidden thresholds or limits phase by phase

## Security Contract

- `.env*`, secrets, certs, local private data, and local environments must remain ignored
- repo-specific environment variables should use the `RELAYTIC_*` prefix
- legacy `C2S_*` variables may be accepted only as compatibility fallbacks
- no raw secrets may be written into tracked docs, tests, or artifacts
- checked-in host-bundle configs must not contain user-specific filesystem paths, tokens, or remote endpoints that are live by default
- semantic helpers, optional LLM paths, and external adapters must default to rowless or redacted context unless policy explicitly grants richer access
- local artifacts remain the canonical truth; memory indexes, semantic caches, and retrieval stores must be derived rather than authoritative
- one active backend per engine slot should be resolved explicitly; hidden plugin auto-loading is out of contract

## External Capability Contract

- mature third-party libraries may be adopted when they strengthen baselines, diagnostics, validation, feature breadth, monitoring, or benchmark parity
- those dependencies must remain behind explicit adapter boundaries instead of becoming hidden core requirements
- Relaytic artifacts remain the source of truth for policy, judgment, and provenance even when external libraries contribute evidence
- offline-stable public datasets are preferred in automated tests over network-bound dataset fetches

## Intake Autonomy Contract

- Slice 04 clarification must be optional by default
- unanswered non-critical intake questions must degrade confidence, not block the run
- Relaytic must log fallback assumptions explicitly when it proceeds without answers
- local LLMs may improve interpretation quality but must not be required for the deterministic intake floor

## Migration Rule

Rename work and semantic changes should not be mixed casually. If a slice changes the public boundary, document:

- what moved
- what stays compatible
- what is intentionally broken
- when the shim is expected to disappear
