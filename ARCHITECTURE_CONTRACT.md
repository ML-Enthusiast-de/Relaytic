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
- `src/relaytic/integrations/` owns optional third-party capability discovery and adapter-scoped inventory surfaces
- `src/corr2surrogate/` is a temporary shim that forwards legacy imports

Reserved next canonical boundaries:

- `src/relaytic/memory/` is reserved for Slice 09A analog retrieval, route priors, and challenger priors

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
- `docs/build_slices/phase_09a.md`

## Artifact Contract

The current slices must preserve these names:

- `manifest.json`
- `policy_resolved.yaml`
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
- `memory_retrieval.json`
- `analog_run_candidates.json`
- `route_prior_context.json`
- `challenger_prior_suggestions.json`

When `relaytic plan run` executes the Builder handoff, the run directory must also contain:

- `model_params.json`
- `normalization_state.json` when normalization is enabled
- `model_state.json` or `<selected_model>_state.json`
- `checkpoints/ckpt_*.json`

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
- `relaytic run`
- `relaytic show`
- `relaytic predict`
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

## Slice 09A Memory Contract

- run memory must be advisory and provenance-bearing rather than silently authoritative
- memory retrieval must surface analog candidates, route priors, and challenger priors as explicit artifacts
- memory-aware planning and completion must always be able to explain what changed because memory was available
- `analog_run_candidates.json` entries must include provenance and a comparable-score explanation rather than only a free-form note

## Security Contract

- `.env*`, secrets, certs, local private data, and local environments must remain ignored
- repo-specific environment variables should use the `RELAYTIC_*` prefix
- legacy `C2S_*` variables may be accepted only as compatibility fallbacks
- no raw secrets may be written into tracked docs, tests, or artifacts

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
