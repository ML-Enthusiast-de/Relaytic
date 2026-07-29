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
9. Decision lab
   Decision specialists build an explicit downstream decision-world model, estimate whether more search or more local data is more valuable, derive controller posture, inspect nearby local sources and join candidates, and compile executable challenger, feature, and benchmark ideas before the final governor path commits to a next move.
10. Completion governor
   Completion specialists fuse the full artifact graph into a visible run state, mandate-evidence review, blocking-layer diagnosis, and machine-actionable next action.
11. Lifecycle
   Lifecycle specialists compare the current champion, challenger evidence, completion state, and fresh-data behavior to decide whether to keep, recalibrate, retrain, promote, or roll back.
12. Bounded autonomy
   Autonomy specialists can execute one budgeted follow-up round such as challenger expansion, recalibration, retraining, or re-plan follow-up while keeping lineage, branch outcomes, and stop rules visible.
13. Runtime gateway
   The local runtime owns append-only event emission, checkpoints, hook audit, and capability-scoped specialist visibility so CLI and MCP share one control plane.
14. Interoperability and host adapters
   Relaytic exposes the same run, workspace, guidance, AML, and lifecycle
   surfaces through a host-neutral MCP server plus thin host wrappers.
15. Workspace continuity and supervision
   Workspace state, result contracts, next-run plans, permission decisions,
   resumable jobs, approvals, and remote-supervision artifacts preserve one
   control truth across runs and interfaces.
16. Model and evaluation control
   Task contracts, architecture routing, bounded search, temporal evaluation,
   calibration, operating-point selection, leakage checks, and benchmark
   claim gates keep model selection separate from test evidence.
17. Relaytic-AML
   AML specialists materialize graph provenance, typology evidence, ranked
   review queues, case packets, delayed-label and drift posture, operational
   metrics, and public-claim limits.
18. Guidance and mission control
   Humans and external agents can inspect current state, relevant artifacts,
   available actions, safe continuation paths, and rowless context exports
   without reconstructing the run from raw files.
19. Release and paper evidence
   Build attestation, repository safety checks, evidence cells, claim gates,
   generated manuscript artifacts, and exact-revision checks connect public
   statements to reproducible local evidence.

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

The public runtime does not expose remote streaming, warehouse, or cloud
lakehouse connectors. Those remain explicit adapter tracks.

For safety, Relaytic stages immutable working copies inside the run directory before major run and inference operations. The source of truth for execution is therefore the staged copy under `data_copies/`, not the original file path.

## Core System Principles

- Deterministic floor: the system must remain useful without any LLM.
- Local-first execution: local runtime paths are the default expectation.
- Steerable autonomy: Relaytic should keep moving when non-critical ambiguity remains, while logging what it assumed.
- Artifact-first behavior: important decisions are written as inspectable artifacts, not hidden in transient agent state.
- Specialist decomposition: focused agents handle bounded responsibilities rather than collapsing everything into a single planner.

## Role Of Local And External Models

Local LLMs are optional advisory components, not a hard dependency for the product contract.

They can improve:

- free-form intake interpretation
- semantic mapping from human language to dataset schema
- bounded advisory support inside investigation specialists
- bounded advisory support inside planning and route selection
- bounded advisory support inside evidence review and memo refinement

Policy-gated external models may serve as optional reasoning or challenger
backends. They are used only when explicitly allowed and must enrich Relaytic's
artifact graph rather than replace the deterministic floor.

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

Relaytic can route common structured-data work such as regression, binary and
multiclass classification, fraud-style rare-event detection, anomaly
detection, and time-aware evaluation. Its specialists remain bounded software
roles rather than a substitute for domain experts. Optional semantic models,
reference documents, and redacted research retrieval can extend their context
without becoming authoritative.

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

The repository implements product slices `00` through `15Z-R`. The major
shipped layers are:

- local policy, mandate, context, intake, investigation, planning, execution,
  challenger, ablation, and audit paths
- completion and lifecycle governance, incumbent challenge, decision-world
  modeling, feedback assimilation, and bounded autonomous follow-up
- workspace continuity, governed learnings, result contracts, iteration plans,
  traces, protocol evaluation, permissions, resumable jobs, and supervision
- task, architecture, search, temporal, calibration, operating-point,
  benchmark-truth, leakage, and claim-scope contracts
- Relaytic-AML graph, typology, alert-queue, case-packet, stream-risk,
  delayed-label, business-value, benchmark, demo, and environment surfaces
- mission control, no-lost guidance, rowless external context export, MCP, and
  checked-in host integrations
- release safety, repository credibility checks, benchmark evidence, paper
  generation, and exact-revision release integrity

Paper Track `P0` through `P27` is implemented. Slice `16A`, capability cards
and registry truth, is the next planned product stage.

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
- `benchmark_reference_report.json`
- `external_research_audit.json`
- `reference_approach_matrix.json`
- `benchmark_gap_report.json`
- `benchmark_parity_report.json`
- `quality_contract.json`
- `quality_gate_report.json`
- `budget_contract.json`
- `budget_consumption_report.json`
- `operator_profile.json`
- `lab_operating_profile.json`
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

Later implemented layers add canonical artifacts including:

- `workspace_state.json`, `workspace_lineage.json`, `result_contract.json`,
  `confidence_posture.json`, and `next_run_plan.json`
- `canonical_trace.json`, `adjudication_scorecard.json`,
  `permission_mode.json`, and `background_job_state.json`
- `task_profile_contract.json`, `optimization_objective_contract.json`,
  `architecture_registry.json`, `search_strategy_report.json`,
  `temporal_metric_contract.json`, and `operating_point_contract.json`
- `entity_graph_profile.json`, `typology_detection_report.json`,
  `alert_queue_rankings.json`, `case_packet.json`,
  `delayed_outcome_alignment.json`, and `aml_public_claim_guard.json`
- `aml_benchmark_environment_scorecard.json`,
  `paper_metric_evidence_cells.json`, `paper_claim_gates.json`, and the
  exact-revision paper release manifests

When staged copies exist, the run directory also contains:

- `data_copies/`

## Current CLI Baseline

The public CLI command is `relaytic`.

Representative product-facing surfaces include:

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
- `relaytic profiles review`
- `relaytic profiles show`
- `relaytic assist show`
- `relaytic assist turn`
- `relaytic assist chat`
- `relaytic autonomy run`
- `relaytic autonomy show`
- `relaytic guide`
- `relaytic guide ask`
- `relaytic guide export-context`
- `relaytic workspace show`
- `relaytic workspace continue`
- `relaytic handoff show`
- `relaytic learnings show`
- `relaytic trace show`
- `relaytic permissions show`
- `relaytic daemon show`
- `relaytic mission-control launch`
- `relaytic aml baselines`
- `relaytic aml graph-loader`
- `relaytic aml temporal`
- `relaytic aml environment`
- `relaytic release-safety paper-final-preflight`
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

Run `relaytic --help` for the complete current command tree. Lower-level
phase commands remain supported for inspection, testing, and controlled
re-entry.

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
