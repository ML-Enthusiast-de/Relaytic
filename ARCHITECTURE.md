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
   Strategist turns investigation outputs into a concrete Builder handoff, and the first deterministic route executes into the same Relaytic run directory.
5. Evidence pressure
   Challenger, ablation, and audit specialists treat the first built route as a provisional champion, then write leaderboard, report, and belief-update artifacts for humans and external agents.
6. Completion governor
   Completion specialists fuse the full artifact graph into a visible run state, mandate-evidence review, blocking-layer diagnosis, and machine-actionable next action.

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
- optional uploaded notes or structured context when provided
- optional local-LLM advisory help for bounded semantic refinement

So the main intelligence path is artifact-grounded reasoning, not hidden pretrained authority. Local LLMs can improve interpretation and synthesis, but they do not replace the deterministic floor or the auditable evidence chain.

At the current baseline, that means Relaytic can already reason over and route common structured-data work such as regression, binary classification, multiclass classification, fraud-style rare-event detection, and anomaly-style detection. The specialist layer is still not equivalent to a fully pretrained PhD-level domain expert; the roadmap for that is stronger memory, reference-doc grounding, and optional intelligence amplification, not opaque magic.

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

The next planned layer is Slice 08: lifecycle baseline.

## Current Artifact Baseline

Relaytic already standardizes several load-bearing artifacts:

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
- `relaytic run`
- `relaytic show`
- `relaytic predict`
- `relaytic integrations show`
- `relaytic integrations self-check`

Additional runtime commands from earlier repository layers still exist while later slices replace deeper internal paths. Those commands are not the long-term architectural center of the product.

## Implementation Control Docs

For detailed slice planning and compatibility tracking, use:

1. `RELAYTIC_VISION_MASTER.md`
2. `RELAYTIC_BUILD_MASTER.md`
3. `ARCHITECTURE_CONTRACT.md`
4. `IMPLEMENTATION_STATUS.md`
5. `MIGRATION_MAP.md`
6. `RELAYTIC_SLICING_PLAN.md`

Those files are intentionally operational. This document is the concise architectural view.
