# Relaytic Architecture Overview

Relaytic is a local-first system for structured-data inference work. It is meant to behave like an evidence-driven lab: capture intent, inspect the data, resolve focus, plan the work, execute routes, compare alternatives, and record why decisions were made.

This document is the public system overview. The implementation control documents remain in the repository for detailed build planning and slice tracking.

## Operating Model

Relaytic is organized as a staged artifact pipeline.

1. Policy and foundation
   Relaytic resolves policy, writes the run manifest, and establishes stable mandate and context artifacts.
2. Intake and translation
   Free-form user or agent input is translated into structured run context with provenance, semantic mapping, optional clarification, and explicit fallback assumptions.
3. Investigation
   Specialist agents inspect the dataset, generate grounded hypotheses, and resolve the initial modeling focus.
4. Planning and execution
   Strategist turns investigation outputs into a concrete Builder handoff, and the current Builder route executes with split-safe preprocessing, bounded categorical handling, missingness-aware features, bounded interaction features, calibration hooks, and reusable inference-time transforms inside the same Relaytic run directory.
5. Evidence pressure
   Challenger, ablation, and audit specialists treat the first built route as a provisional champion, then write leaderboard, report, and belief-update artifacts for humans and external agents.
6. Cross-run memory
   Relaytic retrieves prior analog runs from local artifacts, derives route and challenger priors, and flushes reflection memory back to disk without making memory silently authoritative.
7. Semantically grounded deliberation
   Intelligence specialists assemble capability-aware context, route bounded semantic work through explicit modes and local profiles, ground semantic work in local documents and artifacts, and emit counterposition/verifier outputs plus semantic-proof reports rather than one opaque semantic guess.
8. Research and benchmark parity
   Research specialists retrieve redacted external method knowledge, and the benchmark layer compares Relaytic against explicit reference approaches under the same split and metric contract so the run can be judged against something real.
9. Completion governor
   Completion specialists fuse the full artifact graph into a visible run state, mandate-evidence review, blocking-layer diagnosis, and machine-actionable next action.
10. Lifecycle
   Lifecycle specialists compare the current champion, challenger evidence, completion state, and fresh-data behavior to decide whether to keep, recalibrate, retrain, promote, or roll back.
11. Bounded autonomy
   Autonomy specialists can execute one budgeted follow-up round such as challenger expansion, recalibration, retraining, or re-plan follow-up while keeping lineage, branch outcomes, and stop rules visible.
12. Runtime gateway
   The local runtime owns append-only event emission, checkpoints, hook audit, and capability-scoped specialist visibility so CLI and MCP share one control plane.
13. Interoperability and host adapters
   Relaytic exposes the same MVP and slice-level surfaces through a host-neutral MCP server plus thin host wrappers for common agent ecosystems.

## Current Data Ingestion Boundary

Relaytic's current public ingestion surface is snapshot-file based.

Supported public input formats:

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

Supported local source modes:

- snapshot files in the formats above
- append-only local stream files materialized into bounded micro-batch snapshots
- local lakehouse-style sources materialized into bounded run-local snapshots

The current MVP does not yet expose remote streaming, warehouse, or cloud lakehouse connectors. Those remain future adapter tracks.

For safety, Relaytic stages immutable working copies inside the run directory before major run and inference operations. The source of truth for execution is therefore the staged copy under `data_copies/`, not the original file path.

## Core System Principles

- Deterministic floor: the system must remain useful without any LLM.
- Local-first execution: local runtime paths are the default expectation.
- Steerable autonomy: Relaytic should keep moving when non-critical ambiguity remains, while logging what it assumed.
- Artifact-first behavior: important decisions are written as inspectable artifacts, not hidden in transient agent state.
- Specialist decomposition: focused agents handle bounded responsibilities rather than collapsing everything into a single planner.

## Role Of Local And Frontier Models

Local LLMs are optional advisory components, not a hard dependency for the product contract.

They can improve:

- free-form intake interpretation
- semantic mapping from human language to dataset schema
- bounded advisory support inside investigation specialists
- bounded advisory support inside planning and route selection
- bounded advisory support inside evidence review and memo refinement

Policy-gated frontier models remain part of the long-term design as optional high-end reasoning or challenger backends. They should only be used when explicitly allowed, and they must enrich Relaytic's artifact graph rather than replace the deterministic floor.

They must not replace:

- the deterministic intake floor
- policy enforcement
- artifact provenance
- the ability to continue autonomously without model availability

## Where Agent Knowledge Comes From

Relaytic's specialists are not pretrained domain experts in the product-contract sense.

They get their working knowledge from:

- the dataset itself and deterministic profiling outputs
- deterministic expert-prior libraries that map artifact evidence into domain archetypes and task-specific priors
- structured mandate and context artifacts
- policy and safety constraints
- persisted evidence from planning, execution, challenger, audit, and completion stages
- fresh-data behavior and lifecycle review after completion
- optional uploaded notes or structured context when provided
- optional local-LLM advisory help for bounded semantic refinement

So the main intelligence path is artifact-grounded reasoning, not hidden pretrained authority. Local LLMs can improve interpretation and synthesis, but they do not replace the deterministic floor or the auditable evidence chain.

At the current baseline, that means Relaytic can already reason over and route common structured-data work such as regression, binary classification, multiclass classification, fraud-style rare-event detection, and anomaly-style detection. The specialist layer is still not equivalent to a fully pretrained PhD-level domain expert; the roadmap for that is stronger memory, reference-doc grounding, privacy-safe external research retrieval from redacted run signatures, and optional intelligence amplification, not opaque magic.

## Reuse Mature Libraries Through Adapters

Relaytic should not reinvent mature commodity tooling where the ecosystem is already strong.

The correct pattern is:

- use mature libraries for baselines, diagnostics, schema validation, feature extraction, drift signals, and benchmark parity
- keep those capabilities behind explicit adapter boundaries
- preserve Relaytic-native artifacts as the source of truth for policy, judgment, and provenance
- expose local availability to both humans and external agents through `relaytic integrations show`
- expose adapter compatibility through `relaytic integrations self-check`

The repository's current adoption policy lives in `OPEN_SOURCE_STACK.md`.

## Current Implemented Layers

The repository currently implements the following product layers:

- Slice 01: manifest and policy scaffolding
- Slice 02: mandate and context foundation
- Slice 03: investigation baseline with Scout, Scientist, and Focus Council
- Slice 04: intake and translation with autonomy, clarification, and assumption artifacts
- Slice 05: Strategist planning, Builder handoff, and the first deterministic route from data to model
- Slice 05A: MVP-access orchestration with `relaytic run`, `relaytic show`, `relaytic predict`, and persisted run summaries
- Slice 06: challenger, ablation, provisional audit, leaderboard, and decision-memo evidence around the first built route
- Slice 07: completion-governor judgment with visible run state, blocking analysis, mandate-evidence review, and next-action queue
- Slice 08: lifecycle-governor judgment with champion/candidate comparison and explicit keep, recalibrate, retrain, promote, and rollback actions
- Slice 08A: host-neutral MCP interoperability with checked-in Claude, Codex/OpenAI, OpenClaw, and ChatGPT-facing wrapper surfaces
- Slice 08B: host activation and discovery state with repo/workspace auto-discovery where the host permits it
- Slice 09A: run memory and analog retrieval with route priors, challenger priors, reflection memory, and pre-close memory flush artifacts
- Slice 09B: local runtime gateway with append-only event traces, capability profiles, hook audit, and shared CLI/MCP run-state coordination
- Slice 09: structured semantic tasks, document grounding, semantic debate/counterposition artifacts, and bounded intelligence amplification
- Slice 09F: routed intelligence profiles, backend capability matrices, verifier-specific artifacts, and semantic-proof reporting
- Slice 09C: bounded autonomous second-pass execution with challenger queues, executable recalibration/retrain requests, loop budgets, and champion lineage
- Slice 09D: privacy-safe external research retrieval with redacted query planning, typed source inventory, method-transfer distillation, benchmark-reference capture, and explicit no-leak audit
- Slice 09E: communicative assist surfaces with deterministic explanation, stage navigation, bounded takeover, optional local semantic lift, and host-connection guidance
- Slice 11: benchmark parity, explicit reference-approach comparison, and parity-gap reporting under the same split and metric contract

The next planned layer is Slice 10: feedback assimilation from operator interventions, runtime failures, and later-run evidence.

## Current Artifact Baseline

Relaytic already standardizes several load-bearing artifacts:

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
- `memory_retrieval.json`
- `analog_run_candidates.json`
- `route_prior_context.json`
- `challenger_prior_suggestions.json`
- `reflection_memory.json`
- `memory_flush_report.json`
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
- `context_assembly_report.json`
- `doc_grounding_report.json`
- `semantic_access_audit.json`
- `semantic_debate_report.json`
- `semantic_counterposition_pack.json`
- `semantic_uncertainty_report.json`
- `semantic_proof_report.json`
- `research_query_plan.json`
- `research_source_inventory.json`
- `research_brief.json`
- `method_transfer_report.json`
- `benchmark_reference_report.json`
- `external_research_audit.json`
- `reference_approach_matrix.json`
- `benchmark_gap_report.json`
- `benchmark_parity_report.json`
- `assist_mode.json`
- `assist_session_state.json`
- `assistant_connection_guide.json`
- `assist_turn_log.jsonl`
- `lab_event_stream.jsonl`
- `hook_execution_log.json`
- `run_checkpoint_manifest.json`
- `capability_profiles.json`
- `data_access_audit.json`
- `context_influence_report.json`
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
- `autonomy_loop_state.json`
- `autonomy_round_report.json`
- `challenger_queue.json`
- `branch_outcome_matrix.json`
- `retrain_run_request.json`
- `recalibration_run_request.json`
- `champion_lineage.json`
- `loop_budget_report.json`

When staged copies exist, the run directory also contains:

- `data_copies/`

## Current CLI Baseline

The public CLI command is `relaytic`.

The currently guaranteed product-facing surfaces include:

- `relaytic manifest init`
- `relaytic policy resolve`
- `relaytic foundation init`
- `relaytic mandate init`
- `relaytic context init`
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

Additional runtime commands from earlier repository layers still exist while later slices replace deeper internal paths. Those commands are not the long-term architectural center of the product.

## Interoperability Baseline

Relaytic now exposes a local-first interoperability layer on top of the same product contract.

- `stdio` MCP is the default path for local agent hosts that can spawn Relaytic as a subprocess
- `streamable-http` MCP is available for local connector-style clients on `127.0.0.1`
- checked-in host bundles exist for Claude, Codex/OpenAI skills, OpenClaw, and ChatGPT connector guidance
- the checked-in wrappers are intentionally thin and must not become a second source of truth
- `relaytic interoperability show` now makes host readiness explicit instead of pretending all hosts discover Relaytic the same way
- OpenClaw workspace discovery is supported through `skills/relaytic/SKILL.md`, while ChatGPT still requires explicit connector registration against a public HTTPS `/mcp` endpoint

See `INTEROPERABILITY.md` for concrete usage patterns and safety notes.
See `RUNTIME.md` for the local gateway, event stream, hook model, and capability-profile surface.

## Implementation Control Docs

For detailed slice planning and compatibility tracking, use:

1. `RELAYTIC_VISION_MASTER.md`
2. `RELAYTIC_BUILD_MASTER.md`
3. `ARCHITECTURE_CONTRACT.md`
4. `IMPLEMENTATION_STATUS.md`
5. `MIGRATION_MAP.md`
6. `RELAYTIC_SLICING_PLAN.md`

Those files are intentionally operational. This document is the concise architectural view.
