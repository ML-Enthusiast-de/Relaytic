# Migration Map

This file tracks explicit compatibility boundaries while the repository continues moving toward the final Relaytic product surface.

## Public Naming

- product name: `Relaytic`
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

## Current Newly-Shipped Boundaries

- `src/relaytic/profiles/` for Slice 10B quality contracts, budget contracts, operator/lab profile overlays, and budget-consumption reporting
- `src/relaytic/control/` for Slice 10C intervention contracts, skeptical override handling, control-injection auditing, recovery checkpoints, and control-ledger persistence
- `src/relaytic/decision/` for Slice 10A decision-world models, intervention policy, value-of-more-data reasoning, and decision-usefulness synthesis
- `src/relaytic/compiler/` for Slice 10A method compilation, executable challenger templates, compiled feature hypotheses, and compiled benchmark protocols
- `src/relaytic/data_fabric/` for Slice 10A source-graph reasoning, join-candidate analysis, entity-history understanding, and acquisition planning
- `src/relaytic/benchmark/` for Slice 11A imported-incumbent evaluation, incumbent parity reporting, and beat-target contracts on top of Slice 11 reference comparisons
- `src/relaytic/mission_control/` for Slice 11B mission-control MVP state, onboarding/install-health state, review-queue state, launch metadata, demo-session state, static control-center rendering, Slice 11C clarity surfaces for modes/capabilities/actions/navigation/questions, Slice 11D live onboarding/chat behavior, Slice 11E handbook discovery surfaces, Slice 11F guided demo/mode-education/stuck-recovery surfaces, and Slice 11G adaptive onboarding/session-capture/lightweight-semantic-helper surfaces
- `src/relaytic/dojo/` for Slice 12 guarded self-improvement controls, quarantined proposal bundles, validation results, promotion ledgers, rollback-ready state, and architecture-proposal quarantine
- `docs/handbooks/` for Slice 11E role-specific human/operator and external-agent onboarding guides
- `docs/handbooks/relaytic_demo_walkthrough.md` for Slice 11F recruiter-safe demo sequencing and first-contact presentation

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

## Reserved Future Boundaries

The following boundaries are reserved for the next frontier slices so later implementation can stay sharp without widening the legacy compatibility surface ad hoc:

- `src/relaytic/mission_control/` for later Slice 15 branch DAG, confidence map, trace exploration, change attribution, and broader professional operator surfaces on top of the shipped Slice 11B mission-control foundation
- `src/relaytic/tracing/` for Slice 12B canonical trace schemas, specialist/tool/intervention/branch traces, claim-packet persistence, deterministic adjudication scorecards, replay reports, and replay/query surfaces
- `src/relaytic/evals/` for Slice 12B agent-behavior evaluation, security harnesses, adversarial steering tests, runtime regression packs, and scenario/result matrices
- `src/relaytic/representation/` for Slice 16 optional representation engines, latent-state reports, embedding indexes, and JEPA-style pretraining support

Reserved future artifact names:
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
- `hpo_campaign_report.json`
- `search_decision_ledger.json`
- `branch_dag.json`
- `confidence_map.json`
- `change_attribution_report.json`
- `trace_explorer_state.json`
- `branch_replay_index.json`
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
