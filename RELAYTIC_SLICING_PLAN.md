# RELAYTIC_SLICING_PLAN.md

This file turns the Relaytic vision into bounded implementation slices.

## Global slice rules

Every slice must:
- touch as few subsystems as practical
- add or update tests
- preserve the deterministic floor
- avoid unnecessary renames
- update `IMPLEMENTATION_STATUS.md`
- update `MIGRATION_MAP.md` if boundaries move
- keep optional dependencies optional
- strengthen at least one frontier axis once the repo has a working route
- keep human and agent control surfaces aligned
- map every new intelligence claim to artifacts plus tests or benchmark hooks
- leave the repository coherent after completion

## Frontier proof track

The slices are not only a feature order. They are also a proof order.

From Slice 05 onward, Relaytic should keep these cross-cutting proof tracks alive:

- **golden autonomous path**
  one stable dataset -> intent -> judged model run that proves the main loop still works
- **challenger path**
  one case where the first answer can be overturned or materially weakened by challenger pressure
- **agent-control path**
  one non-interactive JSON-first flow that another agent could drive end to end
- **governor path**
  one case where Relaytic explicitly decides whether to stop, continue, benchmark, or seek more evidence and the reason is inspectable
- **memory path**
  once Slice 09A lands, one case where analog retrieval materially changes route choice, challenger design, or completion reasoning with visible provenance
- **benchmark path**
  formal benchmark parity is Slice 11, but benchmark harness stubs and reference logging should start earlier whenever route, evidence, or completion logic changes

If a later slice adds "smartness" without strengthening at least one of those proof tracks, it is not sharp enough.

## Slice 00 - Normalization and contract freeze

Goal:
- freeze public naming on Relaytic
- add missing build-control docs
- add the public `relaytic` package and CLI surface
- establish security and env-handling rules
- track the temporary legacy compatibility boundary explicitly

Required outputs:
- `ARCHITECTURE_CONTRACT.md`
- `IMPLEMENTATION_STATUS.md`
- `MIGRATION_MAP.md`
- `docs/build_slices/phase_00.md`
- `AGENTS.md`
- Relaytic-branded README and package metadata
- temporary `corr2surrogate` compatibility shim

## Slice 01 - Contracts and scaffolding

Goal:
- create package scaffold
- establish pyproject-based install
- add minimal CLI shell
- add artifact manifest helper
- add policy/config loading shell

Required outputs:
- installable package shell
- `relaytic --help`
- manifest helper
- policy loader stub

## Slice 02 - Mandate and context foundation

Goal:
- stable mandate objects
- stable context objects
- resolved config writing

Required outputs:
- `policy_resolved.yaml`
- `lab_mandate.json`
- `work_preferences.json`
- `run_brief.json`
- `data_origin.json`
- `domain_brief.json`
- `task_brief.json`

## Slice 03 - Focus Council and investigation baseline

Goal:
- Scout baseline
- Scientist baseline
- Focus Council baseline
- dataset profile
- domain memo
- objective artifacts

Required outputs:
- `dataset_profile.json`
- `domain_memo.json`
- `objective_hypotheses.json`
- `focus_debate.json`
- `focus_profile.json`
- `optimization_profile.json`
- `feature_strategy_profile.json`

## Slice 04 - Intake and translation layer

Goal:
- raw user and external-agent intake
- deterministic translation of free-form notes into mandate/context/run fields
- schema alignment between typed language and dataset columns
- optional local-LLM semantic help with bounded provenance
- optional clarification generation for later refinement, never as the default blocking path
- explicit autonomy mode and proceed-with-assumptions behavior when answers are absent
- normalized updates into the Slice 02 foundation

Required outputs:
- `intake_record.json`
- `autonomy_mode.json`
- `clarification_queue.json`
- `assumption_log.json`
- `context_interpretation.json`
- `context_constraints.json`
- `semantic_mapping.json`

## Slice 05 - Planning and first working route

Goal:
- Strategist baseline
- explicit Strategist -> Builder handoff
- one working deterministic tabular route
- metric selection
- split selection
- feature-strategy integration
- experiment-priority integration
- same-run planning plus model artifact execution

Required outputs:
- `plan.json`
- `alternatives.json`
- `hypotheses.json`
- `experiment_priority_report.json`
- `marginal_value_of_next_experiment.json`

Expected behavior:
- `relaytic plan create` must write a concrete Builder handoff, not just abstract route notes
- `relaytic plan run` must execute the first deterministic route in the same run directory
- planning must distinguish hard feature guardrails from soft heuristic risk signals so autonomous runs do not collapse when investigation heuristics are overly conservative

## Slice 05A - MVP access and operator surface

Goal:
- one obvious end-to-end entrypoint
- human-friendly summary surface
- stable agent-friendly summary artifact
- simple prediction surface for built runs
- preserve the specialist architecture underneath

Required outputs:
- `run_summary.json`
- `reports/summary.md`

Required behavior:
- `relaytic run` must orchestrate intake, investigation, planning, and the first execution route
- `relaytic show` must summarize a run even if the summary artifacts were not originally created
- `relaytic predict` must make inference discoverable without forcing users into the lower-level command surface
- the MVP shell must remain a thin access layer over the real Relaytic pipeline, not a replacement for it

## Slice 06 - Experimentation, challenger, audit, reports

Goal:
- treat the selected Builder route as a challengeable champion, not a silent winner
- add one real challenger branch
- add one bounded ablation suite
- add one provisional audit pass
- expose the outcome as clear human and agent surfaces
- keep the MVP one-command usable while preserving explicit specialist control

Required outputs:
- `experiment_registry.json`
- `challenger_report.json`
- `leaderboard.csv`
- `ablation_report.json`
- `audit_report.json`
- `belief_update.json`
- `reports/summary.md`
- `reports/technical_report.md`
- `reports/decision_memo.md`

Required behavior:
- `relaytic evidence run` must be able to attach Slice 06 evidence to an existing executed run or autonomously ensure the executed route exists first
- `relaytic run` must include Slice 06 evidence pressure by default so the MVP does not stop at the first built model
- the evidence layer must remain deterministic by default and only use local-LLM advisory help for bounded memo refinement
- the output must make the provisional recommendation visible to both humans and external agents

## Slice 07 - Completion judgment and visible workflow state

Goal:
- Completion Judge as Inference Governor
- stage tracking
- explicit blocking-layer diagnosis
- mandate-vs-evidence adjudication
- machine-actionable next-action queue
- clear done/continue outputs

Required outputs:
- `completion_decision.json`
- `run_state.json`
- `stage_timeline.json`
- `mandate_evidence_review.json`
- `blocking_analysis.json`
- `next_action_queue.json`

Required behavior:
- completion must consume mandate, context, intake, investigation, planning, and evidence artifacts together rather than only final metrics
- completion outputs must be machine-actionable, not narrative only
- the current stage and next recommended action must be visible in both human and agent surfaces
- completion should turn ambiguity into explicit confidence and blocking reasons rather than hidden state
- completion must explicitly diagnose whether the current bottleneck is route breadth, evidence insufficiency, unresolved semantic ambiguity, missing benchmark comparison, missing memory support, or operator/policy constraint
- completion must be able to say "continue experimentation because the challenger space is still too narrow" rather than treating every executed run as equally complete
- completion must standardize its primary action vocabulary rather than inventing per-run phrasing
- completion must expose whether mandate and evidence agree, conflict, or remain unresolved
- completion must leave an explicit handoff into Slice 09A or Slice 11 when the real limitation is missing memory support or missing benchmark context
- completion must remain deterministic by default, with optional local-LLM help limited to bounded explanation refinement

## Slice 08 - Lifecycle baseline

Goal:
- monitor vs recalibrate vs retrain baseline
- champion/candidate comparison
- promotion/rollback baseline

Required outputs:
- `retrain_decision.json`
- `promotion_decision.json`
- `rollback_decision.json`
- `champion_vs_candidate.json`

Required behavior:
- lifecycle decisions must be evidence-backed, reversible, and easy for an external agent to consume
- Relaytic must distinguish "keep current champion", "recalibrate", "retrain", "promote challenger", and "roll back" as separate actions, not one blended outcome

## Slice 09 - Intelligence amplification and local-LLM assistance

Goal:
- intelligence modes
- local-LLM discovery
- setup guidance
- health checks
- structured semantic task primitive
- health-driven intelligence escalation

Required outputs:
- `intelligence_mode.json`
- `llm_backend_discovery.json`
- `llm_health_check.json`
- `llm_upgrade_suggestions.json`
- `semantic_task_request.json`
- `semantic_task_results.json`
- `intelligence_escalation.json`

Required behavior:
- intelligence amplification must improve bounded semantic and strategic tasks without collapsing the deterministic floor
- Relaytic must always be able to state which judgments came from deterministic evidence and which were LLM-amplified

## Slice 09A - Run memory and analog retrieval

Goal:
- run memory retrieval
- analog-case search
- route-prior recovery
- challenger-prior suggestions

Required outputs:
- `memory_retrieval.json`
- `analog_run_candidates.json`
- `route_prior_context.json`
- `challenger_prior_suggestions.json`

Required behavior:
- memory must be advisory, provenance-carrying, and challengeable by current-run evidence
- retrieved analogs must influence planning, challenger design, and completion reasoning without silently overriding the current dataset
- memory failures or low-confidence retrieval must degrade gracefully into deterministic no-memory behavior

## Slice 10 - Feedback assimilation

Goal:
- feedback intake
- validation
- policy/prior update suggestions
- reversible feedback memory

Required outputs:
- `feedback_intake.json`
- `feedback_validation.json`
- `feedback_effect_report.json`
- `policy_update_suggestions.json`
- `route_prior_updates.json`

Required behavior:
- validated feedback may change future defaults, but no accepted feedback may silently rewrite behavior without an inspectable effect report
- adversarial or low-quality feedback should degrade trust, not quietly pollute priors
- feedback updates must remain distinct from run-memory retrieval so Relaytic can tell whether a prior came from historical evidence, accepted feedback, or both

## Slice 11 - Benchmark parity and reference approaches

Goal:
- benchmark doctrine
- reference-approach comparison
- honest parity reporting
- no-hardcoding discipline

Required outputs:
- `benchmark_gap_report.json`
- `reference_approach_matrix.json`
- `benchmark_parity_report.json`
- `gold_standard_comparison.json`

Required behavior:
- benchmark results must separate deterministic-floor Relaytic, local-LLM-amplified Relaytic, and dojo-improved Relaytic
- benchmark suites must include both ordinary structured-data cases and operator-constrained or mandate-heavy cases
- benchmark failures must emit next-experiment recommendations, not just pass/fail summaries

## Slice 12 - Dojo mode and guarded self-improvement

Goal:
- explicit dojo mode
- quarantined improvements
- method self-improvement
- experimental architecture proposals

Required outputs:
- `dojo_session.json`
- `dojo_hypotheses.json`
- `dojo_results.json`
- `dojo_promotions.json`
- `architecture_proposals.json`

Required behavior:
- dojo outputs must remain quarantined until they beat the incumbent on benchmark and golden-case validation
- no dojo promotion may become default behavior without an explicit promotion artifact

## Slice 13 - Accelerated and distributed local execution

Goal:
- execution-profile detection
- device-aware planning
- CPU/GPU/local-cluster profile choice
- checkpointable distributed-plan baseline

Required outputs:
- `execution_backend_profile.json`
- `device_allocation.json`
- `distributed_run_plan.json`
- `scheduler_job_map.json`
- `checkpoint_state.json`
- `execution_strategy_report.json`

## Slice 14 - Physics-aware exploration constraints

Goal:
- physical-system detection hooks
- feasible-region reporting
- extrapolation risk labeling
- physically bounded proposal generation

Required outputs:
- `trajectory_constraint_report.json`
- `feasible_region_map.json`
- `extrapolation_risk_report.json`

## Slice 15 - Packaging, integrations, demos, polish

Goal:
- package extras
- Docker path
- operator onboarding
- doctor/backup/restore
- ecosystem integrations
- polished demos
- README polish

Required outputs:
- one golden demo
- one Focus Council demo
- one completion/status demo
- one feedback-learning demo
- one benchmark-parity demo
- one dojo demo
- one accelerated execution demo

## First four slices to build before anything fancy

If you want the highest chance of success, only do these first:
- Slice 01
- Slice 02
- Slice 03
- Slice 04

Then stop, test, and review.

