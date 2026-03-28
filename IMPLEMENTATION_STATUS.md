# Implementation Status

This document tracks the operational state of the repository. It is an implementation control file, not product marketing copy.

## Current Baseline

- completed slices: 00 through 12, plus Slice 10A decision-lab world modeling, method compilation, and data-acquisition reasoning, Slice 10B explicit quality-budget-profile contracts, Slice 10C behavioral control contracts with skeptical steering and causal intervention memory, Slice 11E role-specific handbook onboarding, Slice 11F demo-grade onboarding plus stuck recovery, and Slice 11G adaptive human onboarding with lightweight local semantic guidance
- next recommended slice: 12A, lab pulse, periodic awareness, and bounded proactive follow-up
- next trace-and-safety follow-on after 12A: 12B, first-class tracing, agent evaluation, and runtime security harnesses
- next scale-and-search follow-on after 12B: 13, search controller, accelerated execution, and distributed local experimentation
- current public package: `relaytic`
- current public CLI: `relaytic`

## Operational Capabilities

The repository currently supports:

- policy resolution and manifest writing
- mandate and context foundation artifacts
- free-form intake translation with provenance and semantic mapping
- autonomous proceed-with-assumptions behavior for non-critical intake ambiguity
- investigation artifacts from Scout, Scientist, and Focus Council
- Strategist planning artifacts with a real Builder handoff
- a first deterministic local data-to-model route via `relaytic plan run`
- richer first-route preprocessing with bounded categorical handling, missingness indicators, executed interaction features, and reusable preprocessing state at inference time
- broader bounded candidate search within the current Builder family set instead of one fixed-parameter training route
- calibrated classification outputs and uncertainty-bearing prediction summaries for the current regression and classification path
- a first human-friendly and agent-friendly MVP shell via `relaytic run`, `relaytic show`, `relaytic predict`, and `relaytic evidence`
- persisted `run_summary.json` plus `reports/summary.md` for concise run understanding
- copy-only data staging so major run and inference paths operate on immutable working copies under the run directory instead of the original source file
- explicit source inspection/materialization support for humans and agents via `relaytic source inspect` and `relaytic source materialize`
- challenger, ablation, audit, leaderboard, and decision-memo evidence around the first Builder route
- completion-governor judgment that fuses mandate, context, intake, investigation, planning, and evidence into a machine-actionable next step
- visible run-state and blocking-layer artifacts via `relaytic status` and `relaytic completion review`
- lifecycle-governor judgment that distinguishes keep, recalibrate, retrain, promote, and rollback actions from the same run surface
- run memory and analog retrieval with provenance-bearing analog candidates, route priors, challenger priors, reflection memory, and pre-close memory flush artifacts
- visible memory support inside planning, challenger design, completion review, lifecycle review, `relaytic run`, `relaytic show`, and explicit `relaytic memory` surfaces
- a shared local runtime gateway with append-only events, checkpoints, capability-scoped specialists, hook audit, and one coherent control path for CLI and MCP
- bounded semantic-task execution with backend discovery, health reporting, capability-aware context assembly, document grounding, counterposition/verifier debate artifacts, and explicit semantic uncertainty
- visible intelligence support inside completion, lifecycle, `relaytic run`, `relaytic show`, explicit `relaytic intelligence` surfaces, and the MCP contract
- bounded autonomous second-pass execution with challenger queues, recalibration/retrain requests, loop budgeting, and champion lineage updates
- visible autonomy support inside `relaytic run`, `relaytic show`, explicit `relaytic autonomy` surfaces, the runtime event stream, and the MCP contract
- privacy-safe external research retrieval from redacted run signatures with typed source inventory, method-transfer distillation, benchmark-reference capture, and explicit no-raw-row audit
- benchmark parity review against explicit reference approaches under the same split and metric contract
- feedback assimilation with explicit intake, validation, reversible effect reports, route-prior updates, decision-policy suggestions, and rollback-ready casebook artifacts
- later-run planning influence from accepted feedback through memory-scanned route-prior updates
- explicit quality contracts, quality-gate reports, budget contracts, budget-consumption reporting, and bounded operator/lab profiles via `relaytic profiles`
- skeptical behavioral control contracts via `relaytic control review` and `relaytic control show`, with typed intervention requests, explicit override decisions, replayable checkpoints, and causal steering memory
- assist turns that always challenge material steering requests before rerunning or taking over instead of silently complying
- cross-run intervention memory that can make later takeover and override behavior more skeptical when similar earlier requests proved harmful
- MCP-visible control inspection through `relaytic_show_control` and structured assist-turn control payloads
- explicit decision-lab review via `relaytic decision review` and `relaytic decision show`, with machine-readable decision-world models, controller policies, intervention-policy reports, value-of-more-data reasoning, source-graph/join-candidate analysis, and compiled challenger/feature/benchmark templates
- decision-lab outputs that now influence `relaytic run`, `relaytic show`, autonomy follow-up, runtime stage inference, and MCP-visible next-step reasoning instead of remaining a side report
- local data-fabric reasoning that can prefer nearby staged data or join candidates over broader search when the current run is under-specified
- method compilation that turns research, memory, and operator context into executable challenger families, compiled feature hypotheses, and benchmark-protocol change proposals
- visible research support inside completion, autonomy, `relaytic run`, `relaytic show`, explicit `relaytic research` surfaces, and the MCP contract
- visible benchmark support inside completion, `relaytic run`, `relaytic show`, explicit `relaytic benchmark` surfaces, assist, runtime, and the MCP contract
- imported incumbent challenge support through `relaytic benchmark run --incumbent-path ...`, including local model replay, ruleset/scorecard execution, prediction-file fallback with reduced claims, explicit incumbent parity reports, and beat-target contracts that autonomy can consume
- communicative assist surfaces via `relaytic assist show`, `relaytic assist turn`, and `relaytic assist chat` so humans and agents can ask for explanations, request stage navigation, or let Relaytic take over safely
- routed intelligence profiles, explicit local semantic baseline selection, backend capability matrices, verifier-specific artifacts, and semantic-proof reporting so the optional LLM layer is visible and measurable rather than implicit
- connection guidance that can recommend deterministic local-only use, lightweight local LLM setup, or local host connections for Claude, Codex/OpenAI, OpenClaw, and ChatGPT connector paths without making any of them mandatory
- one-line bootstrap via `python scripts/install_relaytic.py` plus install-health verification via `relaytic doctor`
- a thin but real mission-control surface via `relaytic mission-control show` and `relaytic mission-control launch`, with shared local truth for onboarding, review queue, operator cards, launch metadata, and demo-session state
- install-launch coupling so `python scripts/install_relaytic.py --launch-control-center` can verify the environment and land a user in the same local control-center flow without inventing a separate onboarding truth
- role-specific handbook discovery through mission control, mission-control chat, and checked-in host notes so the product can point humans to `docs/handbooks/relaytic_user_handbook.md` and external agents to `docs/handbooks/relaytic_agent_handbook.md` on first contact
- demo-grade onboarding through explicit guided demo flow, mode explanations, stuck-recovery guidance, and a recruiter-safe walkthrough surfaced directly from mission control, chat, and the handbook stack
- adaptive human onboarding with visible captured chat state, dataset-path detection, explicit objective-family routing for quick analysis-first versus full governed-run requests, objective capture, confirmation-before-run behavior, direct analysis-first handling for lightweight exploratory requests, and bounded local semantic extraction for messy first-contact human input
- full-profile bootstrap that now attempts to provision a lightweight CPU-safe onboarding model so mission-control chat can be more forgiving without changing deterministic run control
- explicit dojo review via `relaytic dojo review`, `relaytic dojo show`, and `relaytic dojo rollback`, with quarantined self-improvement proposals, benchmark/quality/control gates, promotion ledgers, rollback-ready state, and mission-control visibility
- host-neutral MCP interoperability via `relaytic interoperability serve-mcp` plus checked-in Claude, Codex/OpenAI, OpenClaw, and ChatGPT-facing wrapper surfaces
- machine-readable host activation/discovery state so Relaytic can say which hosts can call it immediately and which still require connector registration
- optional local-LLM advisory support without making local LLMs a hard requirement
- optional frontier-model use remains in-plan as a policy-gated amplifier rather than a baseline dependency
- deterministic expert-prior inference that converts task/domain evidence into archetype-aware metric, route, feature, and risk priors
- optional integration inventory via `relaytic integrations show` so humans and external agents can discover mature OSS capabilities without smearing them into the core contract
- wired integration adapters for Pandera intake validation, statsmodels residual diagnostics, imbalanced-learn rare-event challengers, and PyOD anomaly challengers with a default Windows runtime guard for the current unstable PyOD stack
- adapter compatibility self-checks via `relaytic integrations self-check` so upgrades can be verified without guessing
- current task-family support across the main path for regression, binary classification, multiclass classification, and fraud/anomaly-style rare-event detection
- current public ingestion support for `.csv`, `.tsv`, `.xlsx`, `.xls`, `.parquet`, `.pq`, `.feather`, `.json`, `.jsonl`, and `.ndjson`
- current local source-mode support for append-only stream files and local lakehouse-style sources through bounded materialization into immutable run-local snapshots
- remote streaming, warehouse, and cloud lakehouse connectors remain future adapter work
- public-dataset end-to-end regression, binary-classification, and multiclass-classification coverage using stable bundled open datasets in the test suite
- optional official-UCI domain-dataset coverage for concrete strength, telecom churn, credit default, and predictive maintenance through an explicit opt-in network-backed test suite

## Planned High-Leverage Follow-Ons

The most important not-yet-implemented shifts after the current baseline are:

- a lab pulse that can periodically inspect local state, watch for new relevant methods or benchmark debt, and queue bounded safe follow-up without silent drift
- a first-class trace model across specialists, tools, interventions, and branches so Relaytic can replay and compare multi-stage behavior from one runtime truth
- runtime evaluator and security harnesses that test skeptical control, tool safety, branch-controller safety, and adversarial steering before broader autonomy is trusted
- richer long-term memory with retention, compaction, pinning, and replay rules so durable lessons survive beyond analog similarity
- stronger dynamic controller logic that decides who should act next, how deep to branch, and when review is worth it under explicit contracts
- stronger search/HPO/controller logic that widens, prunes, and allocates effort under explicit value and budget contracts
- mission-control surfaces that expose branch DAG, confidence, and change attribution to both humans and external agents
- an optional late-stage representation engine for large unlabeled local corpora, streams, and entity histories, with JEPA-style latent predictive learning as one candidate backend family

## Implemented Slices

### Slice 00

- locked public naming on `Relaytic`, `relaytic`, and `relaytic`
- established security, migration, and implementation control documents
- introduced the temporary `corr2surrogate` compatibility boundary

### Slice 01

- added manifest helpers under `src/relaytic/artifacts/`
- added canonical policy loading and resolved-policy writing under `src/relaytic/policies/`
- added `relaytic manifest init`
- added `relaytic policy resolve`
- added targeted scaffold and CLI tests

### Slice 02

- added stable mandate models and writers under `src/relaytic/mandate/`
- added stable context models and writers under `src/relaytic/context/`
- added `relaytic mandate init` and `relaytic mandate show`
- added `relaytic context init` and `relaytic context show`
- added `relaytic foundation init`
- added targeted foundation and CLI tests

### Slice 03

- added `src/relaytic/investigation/` with typed investigation artifacts and storage helpers
- implemented Scout for dataset profiling
- implemented Scientist for grounded domain and objective hypotheses
- implemented Focus Council for early objective resolution
- added deterministic expert-prior reasoning so Scientist and Focus Council can carry archetype-aware knowledge without requiring an LLM
- added `relaytic investigate`
- added targeted investigation, CLI, and local-stub-LLM tests

### Slice 04

- added `src/relaytic/intake/` with typed intake artifacts and storage helpers
- implemented `StewardAgent` for mandate, work-preference, and run-brief translation
- implemented `ContextInterpreterAgent` for data-origin, domain, and task translation
- added task-type and domain-archetype hint extraction from free-form intake so later specialists can receive stronger structured intent
- upgraded intake so explicit targets can resolve task-type hints from dataset evidence instead of relying only on generic language cues
- added `relaytic intake interpret`
- added `relaytic intake show`
- added `relaytic intake questions`
- added `autonomy_mode.json`, `clarification_queue.json`, and `assumption_log.json`
- made intake clarification optional by default and auditable through explicit assumptions
- added targeted intake, CLI, and local-stub-LLM tests

### Slice 05

- added `src/relaytic/planning/` with typed planning artifacts, storage helpers, and optional local advisory
- implemented `StrategistAgent` to turn investigation outputs into a concrete Builder handoff
- added `plan.json`, `alternatives.json`, `hypotheses.json`, `experiment_priority_report.json`, and `marginal_value_of_next_experiment.json`
- added `relaytic plan create`, `relaytic plan run`, and `relaytic plan show`
- connected the first deterministic Builder execution route into the same Relaytic run directory
- made planning robust against over-aggressive heuristic exclusions by distinguishing hard guardrails from soft feature-risk signals
- added targeted planning, CLI, end-to-end inference, and local-stub-LLM tests

### Slice 05A

- added `src/relaytic/runs/` for MVP-access summaries and human-readable run reports
- added `relaytic run` as a one-shot intake -> investigate -> plan -> execute surface
- added `relaytic show` to materialize and render concise run summaries
- added `relaytic predict` as the accessible inference surface for built runs
- added `run_summary.json` and `reports/summary.md`
- standardized nested manifest artifact paths to POSIX-style relative paths for easier agent consumption
- added targeted MVP-access CLI tests

### Slice 06

- added `src/relaytic/evidence/` with typed challenger, ablation, audit, and belief-update artifacts plus storage helpers
- implemented a bounded challenger branch against the selected Builder route
- implemented bounded feature-drop ablations against the selected champion family
- implemented a provisional audit pass that combines challenger evidence, ablation evidence, and inference diagnostics
- added `experiment_registry.json`, `challenger_report.json`, `ablation_report.json`, `audit_report.json`, `belief_update.json`, `leaderboard.csv`, `reports/technical_report.md`, and `reports/decision_memo.md`
- added `relaytic evidence run` and `relaytic evidence show`
- upgraded `relaytic run` so the MVP flow now includes Slice 06 evidence pressure by default
- extended `run_summary.json` and `reports/summary.md` so humans and agents can see the provisional recommendation and evidence posture
- added targeted Slice 06 agent, CLI, and local-stub-LLM tests

### Slice 07

- added `src/relaytic/completion/` with typed completion-governor artifacts, storage helpers, and optional local advisory
- implemented a state tracker that records visible workflow stage and stage timeline
- implemented a mandate review layer that checks target alignment and constraint conflicts against the executed route
- implemented a completion governor that emits a stable action vocabulary, blocking-layer diagnosis, and machine-actionable next-action queue
- added `completion_decision.json`, `run_state.json`, `stage_timeline.json`, `mandate_evidence_review.json`, `blocking_analysis.json`, and `next_action_queue.json`
- added `relaytic status` and `relaytic completion review`
- upgraded `relaytic run` and `relaytic show` so the MVP flow now ends in an explicit governed state rather than a provisional evidence memo only
- tightened `--overwrite` behavior so reruns refresh targeted investigation, planning, evidence, and completion artifacts instead of mixing stale upstream state into later governed outputs
- added targeted Slice 07 agent, CLI, local-stub-LLM, and end-to-end tests

### Slice 08

- added `src/relaytic/lifecycle/` with typed lifecycle artifacts, storage helpers, and deterministic lifecycle review logic
- implemented champion-vs-candidate comparison that fuses evidence, completion state, and fresh-data behavior
- implemented distinct recalibration, retraining, promotion, and rollback decisions with machine-readable reason codes
- added `champion_vs_candidate.json`, `recalibration_decision.json`, `retrain_decision.json`, `promotion_decision.json`, and `rollback_decision.json`
- added `relaytic lifecycle review` and `relaytic lifecycle show`
- upgraded `relaytic run` and `relaytic show` so the MVP flow now includes lifecycle review by default
- extended `run_summary.json` and `reports/summary.md` so humans and agents can see lifecycle posture in the same surface
- added targeted Slice 08 agent, CLI, doctor, bootstrap, and public-dataset end-to-end tests

### Slice 08A

- added `src/relaytic/interoperability/` with a Relaytic-owned MCP server boundary, host-bundle generation, and interoperability self-checks
- implemented a host-neutral MCP tool contract over the current Relaytic MVP and phase-level surfaces
- added `relaytic interoperability show`, `relaytic interoperability self-check`, `relaytic interoperability export`, and `relaytic interoperability serve-mcp`
- added checked-in `.mcp.json`, `.claude/agents/relaytic.md`, `.agents/skills/relaytic/SKILL.md`, `openclaw/skills/relaytic/SKILL.md`, and `connectors/chatgpt/README.md`
- added transport-safe compact health tooling and live stdio/streamable HTTP smoke coverage
- added public-dataset end-to-end MCP coverage so Relaytic can be exercised through the interoperability surface rather than CLI only

### Slice 08B

- expanded host-bundle metadata with explicit discovery mode, activation requirements, HTTPS requirements, and next-step guidance
- added workspace-level `skills/relaytic/SKILL.md` so OpenClaw-style workspace discovery can work directly from this repository
- upgraded `relaytic interoperability show` so humans and agents can see which hosts are callable now versus which still need registration or approval
- tightened ChatGPT connector guidance so repository-local files are not mistaken for automatic ChatGPT availability

### Slice 09A

- added `src/relaytic/memory/` with typed memory controls, analog retrieval artifacts, provenance-bearing scoring, reflection writeback, and storage helpers
- added `relaytic memory retrieve` and `relaytic memory show`
- added `memory_retrieval.json`, `analog_run_candidates.json`, `route_prior_context.json`, `challenger_prior_suggestions.json`, `reflection_memory.json`, and `memory_flush_report.json`
- upgraded planning so analog priors can change candidate-family order with a visible counterfactual instead of silently mutating the route
- upgraded challenger selection so memory can bias challenger family choice when prior evidence supports it
- upgraded completion and lifecycle review so memory support is diagnosed explicitly and retrieved analogs become visible to both humans and external agents
- upgraded `relaytic run` and `relaytic show` so the MVP shell materializes memory artifacts automatically and surfaces the resulting memory delta in `run_summary.json`
- added targeted Slice 09A agent, CLI, and public-dataset end-to-end tests

### Slice 09B

- added `src/relaytic/runtime/` with typed runtime controls, capability profiles, append-only event storage, hook audit, checkpoint manifests, and context-influence persistence
- added `relaytic runtime show` and `relaytic runtime events`
- added `lab_event_stream.jsonl`, `hook_execution_log.json`, `run_checkpoint_manifest.json`, `capability_profiles.json`, `data_access_audit.json`, and `context_influence_report.json`
- upgraded intake, investigation, planning, evidence, memory, completion, and lifecycle orchestration so stage transitions flow through one shared local runtime instead of loose per-surface glue
- upgraded `relaytic show`, `run_summary.json`, and the MCP layer so humans and external agents can inspect runtime posture, event counts, denied accesses, and hook behavior directly
- added targeted Slice 09B runtime, CLI, MCP, and public-dataset end-to-end tests

### Slice 09

- added `src/relaytic/intelligence/` with typed semantic-task controls, backend discovery, health checks, document-grounding support, counterposition packaging, uncertainty reporting, and storage helpers
- added `relaytic intelligence run` and `relaytic intelligence show`
- added `intelligence_mode.json`, `llm_backend_discovery.json`, `llm_health_check.json`, `llm_upgrade_suggestions.json`, `semantic_task_request.json`, `semantic_task_results.json`, `intelligence_escalation.json`, `context_assembly_report.json`, `doc_grounding_report.json`, `semantic_access_audit.json`, `semantic_debate_report.json`, `semantic_counterposition_pack.json`, and `semantic_uncertainty_report.json`
- implemented one canonical JSON-first semantic-task contract with proposer/counterposition/verifier style outputs instead of scattered prompt calls
- made semantic work capability-aware and rowless by default while auditing richer-access requests explicitly
- upgraded completion and lifecycle so semantically difficult target, constraint, challenger, and retrain judgments can influence the governed outcome visibly
- upgraded `relaytic run`, `relaytic show`, and the MCP layer so intelligence posture is materialized automatically and remains inspectable for both humans and agents
- added targeted Slice 09 CLI, local-LLM, and regression tests

### Slice 09C

- added `src/relaytic/autonomy/` with typed loop-state artifacts, challenger queues, branch-outcome tracking, executable follow-up requests, champion lineage, and storage helpers
- added `relaytic autonomy run` and `relaytic autonomy show`
- added `autonomy_loop_state.json`, `autonomy_round_report.json`, `challenger_queue.json`, `branch_outcome_matrix.json`, `retrain_run_request.json`, `recalibration_run_request.json`, `champion_lineage.json`, and `loop_budget_report.json`
- implemented one bounded autonomous second pass that can expand challenger pressure, execute recalibration or retraining requests, and stop honestly on budget or plateau
- upgraded runtime, memory, intelligence, completion, lifecycle, `relaytic run`, `relaytic show`, and the MCP contract so autonomous follow-up is visible and replayable instead of hidden control flow
- preserved the deterministic fallback when autonomous execution is disabled or not justified by the judged state
- added targeted Slice 09C CLI, local-LLM, and regression tests

### Slice 09D

- added `src/relaytic/research/` with typed redacted-query planning, bounded source adapters, method-transfer distillation, benchmark-reference capture, and research-audit persistence
- added `relaytic research gather`, `relaytic research show`, and `relaytic research sources`
- added `research_query_plan.json`, `research_source_inventory.json`, `research_brief.json`, `method_transfer_report.json`, `benchmark_reference_report.json`, and `external_research_audit.json`
- wired research outputs into completion, autonomy, `relaytic run`, `relaytic show`, and MCP surfaces while preserving local evidence as the final arbiter
- added targeted Slice 09D research, CLI, and privacy-regression tests

### Slice 09E

- added `src/relaytic/assist/` with typed communicative-assist controls, session-state artifacts, connection guidance, and turn-log persistence
- added `relaytic assist show`, `relaytic assist turn`, and `relaytic assist chat`
- added `assist_mode.json`, `assist_session_state.json`, `assistant_connection_guide.json`, and `assist_turn_log.jsonl`
- implemented deterministic explanation, stage navigation, and bounded takeover over the current Relaytic artifact graph instead of a hidden chat-only shell

### Slice 10C

- added `src/relaytic/control/` with typed intervention contracts, skeptical challenge reports, override decisions, recovery checkpoints, control-injection audit, intervention ledgers, and causal steering-memory artifacts
- added `relaytic control review` and `relaytic control show`
- added `intervention_request.json`, `intervention_contract.json`, `control_challenge_report.json`, `override_decision.json`, `intervention_ledger.json`, `recovery_checkpoint.json`, `control_injection_audit.json`, `causal_memory_index.json`, `intervention_memory_log.json`, `outcome_memory_graph.json`, and `method_memory_index.json`
- upgraded `relaytic assist turn` so navigation stays easy, but takeover and other truth-bearing steering requests are challenged, checkpointed, accepted-with-modification, deferred, or rejected explicitly
- upgraded run summaries and MCP inspection so humans and external agents can see control posture and replayable override state without scraping prose
- added targeted Slice 10C agent, CLI, assist-regression, access-surface, and MCP tests
- integrated lightweight local-LLM guidance and local host-connection guidance without making semantic assist mandatory
- upgraded the MCP contract so external agents can use the same communicative assist surface non-interactively
- added targeted Slice 09E CLI and interoperability tests

### Slice 09F

- extended `src/relaytic/intelligence/` with canonical mode utilities, routed intelligence planning, and explicit local baseline profile resolution
- added `llm_routing_plan.json`, `local_llm_profile.json`, `verifier_report.json`, and `semantic_proof_report.json`
- upgraded `relaytic intelligence show`, `relaytic show`, and run-summary generation so routed mode, recommended mode, selected local profile, and semantic gain are visible to both humans and external agents
- turned legacy intelligence-mode labels into one canonical routing contract without making the semantic layer mandatory
- added targeted routed-intelligence unit tests plus expanded Slice 09 CLI coverage

### Slice 11

- added `src/relaytic/benchmark/` with typed reference-comparison controls, parity/gap artifacts, and storage helpers
- added `relaytic benchmark run` and `relaytic benchmark show`
- added `reference_approach_matrix.json`, `benchmark_gap_report.json`, and `benchmark_parity_report.json`
- upgraded the Builder path with richer categorical handling, missingness-aware executed features, bounded interaction features, calibration, and reusable preprocessing state
- upgraded inference so staged prediction runs can reuse preprocessing, expose calibration-aware classification outputs, and surface uncertainty-bearing summaries
- upgraded completion, runtime, assist, `relaytic run`, `relaytic show`, and the MCP contract so benchmark posture is visible instead of hidden in ad hoc evaluation notes
- added targeted Slice 11 CLI, modeling, inference, and public-dataset tests

### Slice 11A

- extended `src/relaytic/benchmark/` with imported-incumbent evaluation, incumbent parity reporting, and beat-target contracts
- extended `relaytic benchmark run` so operators and external agents can attach local models, prediction files, rulesets, or scorecards directly
- added `external_challenger_manifest.json`, `external_challenger_evaluation.json`, `incumbent_parity_report.json`, and `beat_target_contract.json`
- upgraded autonomy, run summaries, and MCP surfaces so explicit beat-target posture can change follow-up behavior instead of remaining benchmark-only metadata
- added targeted Slice 11A CLI and interoperability tests

### Slice 11B

- added `src/relaytic/mission_control/` with mission-control state, onboarding/install-health state, review-queue state, launch metadata, demo-session state, and control-center rendering helpers
- added `relaytic mission-control show` and `relaytic mission-control launch`
- added `mission_control_state.json`, `review_queue_state.json`, `control_center_layout.json`, `onboarding_status.json`, `install_experience_report.json`, `launch_manifest.json`, `demo_session_manifest.json`, `ui_preferences.json`, and `reports/mission_control.html`
- upgraded `scripts/install_relaytic.py` so install verification and local control-center launch share one documented onboarding path instead of separate setup surfaces
- added targeted Slice 11B CLI, interoperability, and doctor-adjacent verification

### Slice 11C

- extended `src/relaytic/mission_control/` and `src/relaytic/assist/` so a fresh mission-control surface now materializes explicit mode, capability, action-affordance, stage-navigation, and starter-question state instead of assuming assist artifacts already exist
- added `mode_overview.json`, `capability_manifest.json`, `action_affordances.json`, `stage_navigator.json`, and `question_starters.json`
- upgraded `relaytic mission-control show`, `relaytic mission-control launch`, `relaytic assist show`, and `relaytic assist turn` so humans and external agents can immediately see what Relaytic can do, how to steer it safely, what stages can be rerun, and that navigation is bounded rather than arbitrary checkpoint time travel
- upgraded the quick CLI/MCP mission-control payload so current mode, next actor, capability counts, action counts, question counts, and stage-navigation scope are visible without unpacking the full bundle
- added targeted Slice 11C mission-control, assist, and interoperability verification

### Slice 11D

- extended `src/relaytic/mission_control/` and `src/relaytic/ui/cli.py` so onboarding now explicitly explains what Relaytic is, what it needs first, how the dashboard differs from terminal chat, and why capabilities need setup instead of dumping a passive status board on first contact
- added `relaytic mission-control chat` plus `relaytic mission-control launch --interactive` so users and external agents can ask setup and capability questions directly from the terminal instead of discovering the assist vocabulary by accident
- upgraded mission-control HTML and markdown rendering with first steps, interaction modes, capability reasons, activation hints, and clearer live-chat entrypoints
- upgraded `relaytic assist chat` with clearer startup guidance plus `/capabilities`, `/stages`, `/next`, and `/takeover` shortcuts while keeping the existing bounded stage and skeptical-control contract intact
- added targeted Slice 11D CLI verification for onboarding, interactive launch, mission-control chat, and assist-chat clarity

### Slice 11E

- extended `src/relaytic/mission_control/` and `src/relaytic/ui/cli.py` so mission control can point humans and external agents to different guides instead of assuming the same onboarding shape fits both
- added `docs/handbooks/relaytic_user_handbook.md` and `docs/handbooks/relaytic_agent_handbook.md`
- upgraded onboarding cards, interaction modes, question starters, action affordances, control-center layout, and mission-control chat so handbook discovery is explicit and available through `/handbook` as well as natural onboarding questions
- upgraded `.claude/agents/relaytic.md`, `.agents/skills/relaytic/SKILL.md`, `skills/relaytic/SKILL.md`, and `openclaw/skills/relaytic/SKILL.md` so checked-in host notes point to the same agent handbook instead of drifting independently
- added targeted Slice 11E CLI verification for handbook discovery through mission control and mission-control chat

### Slice 11F

- extended `src/relaytic/mission_control/`, `src/relaytic/ui/cli.py`, and the handbook stack so Relaytic now exposes an explicit demo path, mode education, and stuck-recovery guidance instead of assuming first-time users can infer the right flow
- added `docs/handbooks/relaytic_demo_walkthrough.md`
- upgraded mission-control onboarding, action affordances, question starters, markdown/html rendering, and mission-control chat so users can ask for a demo flow, mode explanation, or stuck guidance directly through `/demo`, `/modes`, `/stuck`, and equivalent plain-language questions
- expanded the human and agent handbooks so they now explain the main flow, what happens after a run starts, what each surface is for, and what to do when something is unclear
- added targeted Slice 11F CLI and handbook verification for demo-grade onboarding, mode explanation, and stuck recovery

### Slice 11G

- extended `src/relaytic/mission_control/`, `src/relaytic/ui/cli.py`, `src/relaytic/intelligence/backends.py`, `src/relaytic/orchestration/local_llm_setup.py`, and `scripts/install_relaytic.py` so first-contact chat can capture messy human input, keep visible onboarding state, and use a lightweight local semantic helper without making semantic inference part of the authority path
- added `onboarding_chat_session_state.json` as a first-class mission-control artifact for captured dataset path, objective, next expected input, semantic-backend status, and run-start readiness
- upgraded mission-control chat so humans can paste a dataset path directly, provide the objective in a later turn, inspect captured state with `/state`, reset with `/reset`, and confirm before the first run is created
- expanded onboarding so Relaytic now distinguishes quick analysis-first requests from full governed-run requests and can execute lightweight direct analysis for top-signal, exploratory, and correlation-style objectives without forcing debate-heavy modeling
- hardened local semantic backend discovery and local-LLM setup so canonical `policy:` configs work in the same way as legacy top-level config files for onboarding use
- upgraded `python scripts/install_relaytic.py --profile full` so the one-line bootstrap now attempts to provision Relaytic's lightweight local onboarding helper by default
- added targeted Slice 11G onboarding and install verification for dataset-path capture, objective capture plus confirmation, messy-input semantic rescue, and one-line-installer onboarding-local-LLM setup

### Slice 12

- added `src/relaytic/dojo/` with typed guarded self-improvement controls, quarantined proposal bundles, validation results, promotion ledgers, rollback-ready state, and storage helpers
- added `relaytic dojo review`, `relaytic dojo show`, and `relaytic dojo rollback`
- added `dojo_session.json`, `dojo_hypotheses.json`, `dojo_results.json`, `dojo_promotions.json`, and `architecture_proposals.json`
- implemented deterministic guarded self-improvement against benchmark, visible quality-proxy, and skeptical-control gates
- kept early architecture proposals quarantined and non-authoritative even when method-level proposals are promotable
- extended run summary, mission-control, and MCP/service surfaces so dojo posture is visible instead of CLI-only side state
- added targeted Slice 12 agent, CLI, mission-control, interoperability, and doctor-adjacent verification

### Cross-Cutting Hardening

- added `src/relaytic/integrations/` as the canonical optional-library discovery boundary
- added `relaytic integrations show` for human and agent visibility into mature OSS capabilities
- added `relaytic integrations self-check` so wired adapters can be compatibility-checked after package changes
- wired Pandera into intake validation, statsmodels into evidence audit diagnostics, imbalanced-learn into rare-event challenger execution, and PyOD into anomaly challenger execution
- added `relaytic doctor` as the canonical runtime/install-health surface and a one-line bootstrap script at `scripts/install_relaytic.py`
- adopted bundled public datasets for stable end-to-end regression, binary-classification, and multiclass-classification tests without introducing network-bound CI behavior
- added an opt-in official-UCI domain-dataset suite so Relaytic can be exercised on domain-specific public data without making default CI depend on live network fetches
- sharpened `RELAYTIC_SLICING_PLAN.md` into a stricter future-slice execution contract with explicit intelligence sources, proof obligations, fallbacks, and a preferred post-MVP execution order
- folded explicit optional SOTA routine tracks into the slicing plan so future lifecycle, memory, benchmark, and polish slices know where MAPIE, Evidently, MLflow, OpenTelemetry, OpenLineage, FLAML, and later Feast fit
- sharpened the future architecture doctrine so upcoming slices are now expected to deliver disk-first artifact memory, rowless-by-default semantic work, capability-scoped specialists, deterministic hook points, and a local lab runtime rather than looser pipeline-style orchestration

## Compatibility Boundary

The remaining compatibility surface is intentionally narrow:

- `src/corr2surrogate/__init__.py` forwards legacy imports
- legacy `C2S_*` environment variable fallbacks may still be accepted where required

New code and docs must target `relaytic` and `RELAYTIC_*`.

## Known Gaps

The repository is not yet at the final product state. The main remaining gaps are:

- the current challenger layer is broader and now loop-capable, but it is still not a full challenger field or large search program
- autonomous second-pass behavior is real, but its budgeted loop set is still intentionally narrow rather than deeply adaptive
- run memory is now real, but longer-horizon feedback learning and richer analog indexing are still pending
- benchmark parity is now real, but broader constrained-superiority coverage and optional stronger reference stacks are still pending
- privacy-safe external research retrieval is now real, but it is still limited to bounded source adapters and shallow transfer logic rather than a mature domain-research stack
- communicative assist is now real, but it is still deterministic-first and intentionally bounded rather than a rich multi-agent conversational shell
- reference-doc grounding is now real but still shallow compared with a mature domain corpus strategy
- internal specialist discussion is now materially stronger and the routed semantic layer is now explicit, but it is still not equivalent to rich domain-specific expert systems or large benchmarked semantic stacks

## Immediate Next Work

With Slice 11G and Slice 12 now landed, the next high-leverage frontier follow-ons are:

- Slice 12A lab pulse, periodic awareness, and bounded proactive follow-up
- Slice 12B first-class tracing, agent evaluation, and runtime security harnesses
- Slice 13 search-controller depth, accelerated execution, and distributed local experimentation under explicit value and budget contracts
- richer long-term memory compaction, pinning, and replay rules that build on the shipped causal and dojo ledgers
- later Slice 15 remote connector adapters for Kafka-style streams, object-store Parquet, and warehouse reads, but only through read-only materialization into immutable run-local snapshots
