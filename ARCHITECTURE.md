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
   Later slices will add Strategist, the first deterministic end-to-end modeling route, challenger paths, and lifecycle decisions.

## Core System Principles

- Deterministic floor: the system must remain useful without any LLM.
- Local-first execution: local runtime paths are the default expectation.
- Steerable autonomy: Relaytic should keep moving when non-critical ambiguity remains, while logging what it assumed.
- Artifact-first behavior: important decisions are written as inspectable artifacts, not hidden in transient agent state.
- Specialist decomposition: focused agents handle bounded responsibilities rather than collapsing everything into a single planner.

## Role Of Local LLMs

Local LLMs are optional advisory components, not a hard dependency for the product contract.

They can improve:

- free-form intake interpretation
- semantic mapping from human language to dataset schema
- bounded advisory support inside investigation specialists

They must not replace:

- the deterministic intake floor
- policy enforcement
- artifact provenance
- the ability to continue autonomously without model availability

## Current Implemented Layers

The repository currently implements the following product layers:

- Slice 01: manifest and policy scaffolding
- Slice 02: mandate and context foundation
- Slice 03: investigation baseline with Scout, Scientist, and Focus Council
- Slice 04: intake and translation with autonomy, clarification, and assumption artifacts

The next planned layer is Slice 05: planning and the first deterministic route from data to model.

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
