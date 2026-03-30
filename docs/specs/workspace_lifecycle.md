# Workspace Lifecycle Contract

## Purpose

This document defines how Relaytic should treat a workspace once Slice 12D lands.

The goal is to stop relying on implied continuity from directory structure, chat history, or operator memory. A workspace is the canonical continuity unit for multi-run investigations.

## Scope

This contract governs:

- workspace creation
- workspace identity
- run-to-workspace attachment
- continuation versus restart decisions
- focus history
- selective reset behavior
- compatibility with existing Slice 12C handoff and learnings surfaces

This contract does not define the field-level schema for result contracts or governed learnings. Those are covered in separate spec documents.

Compatibility and migration for already-shipped handoff and learnings surfaces are frozen separately in:

- `docs/specs/handoff_result_migration.md`
- `docs/specs/learnings_migration_contract.md`

## Canonical objects

Slice 12D should introduce these canonical workspace artifacts:

- `workspace_state.json`
- `workspace_lineage.json`
- `workspace_focus_history.json`
- `workspace_memory_policy.json`
- `next_run_plan.json`

These artifacts become the continuity truth for later slices.

## Workspace identity

Every workspace should have:

- a stable `workspace_id`
- a human-facing `workspace_label`
- a `created_at` timestamp
- an `updated_at` timestamp
- a `status`
- a `current_run_id`
- a `current_focus`
- a `continuity_mode`

Required `status` values:

- `active`
- `paused`
- `archived`
- `reset_pending`

Required `continuity_mode` values:

- `single_run`
- `same_data_continuation`
- `data_expansion`
- `new_dataset_restart`

## Creation rules

A workspace should be created when:

- a user or external agent explicitly starts a new investigation
- a serious governed run is started without an existing workspace
- a previous workspace is intentionally closed and a new investigation begins

A workspace should not be created for:

- lightweight ad hoc health checks
- isolated diagnostic commands
- read-only artifact inspection

## Run attachment rules

Each serious run should declare:

- `run_id`
- `workspace_id`
- `parent_run_id`
- `continuation_reason`
- `dataset_relation`

Required `dataset_relation` values:

- `same_primary_dataset`
- `same_dataset_with_more_rows`
- `same_dataset_with_more_columns`
- `new_dataset_same_problem`
- `new_dataset_new_problem`

Required `continuation_reason` values:

- `continue_same_data`
- `add_data`
- `start_over`
- `recalibration_refresh`
- `retrain_refresh`
- `benchmark_follow_on`
- `incumbent_follow_on`

## Same workspace versus new workspace

Relaytic should stay in the same workspace when:

- the user wants to continue the same underlying investigation
- the objective remains materially the same
- the new run is an iteration on the same decision problem
- the dataset is expanded but not conceptually replaced

Relaytic should recommend a new workspace when:

- the objective changes materially
- the dataset changes enough that prior continuity would confuse interpretation
- the user explicitly asks to start fresh
- the result contract says prior beliefs are no longer a useful framing

## Continuation planner outputs

`next_run_plan.json` must contain one top-level `recommended_direction` with exactly one of:

- `same_data`
- `add_data`
- `new_dataset`

It must also contain:

- `primary_reason`
- `secondary_actions`
- `confidence`
- `why_not_the_other_paths`
- `required_user_inputs`
- `belief_revision_dependency`

`secondary_actions` may include:

- `search_more`
- `recalibrate`
- `retrain`
- `benchmark_incumbent`
- `collect_labels`
- `add_features`
- `expand_entities`
- `pause_for_review`

## Focus history

`workspace_focus_history.json` should record:

- every accepted focus
- who or what chose it
- why it changed
- what evidence justified the change
- which later result contract superseded it

Focus history should be append-only. Resetting a workspace should not silently erase historical focus changes from lineage views.

## Reset behavior

Relaytic must support selective reset rather than one destructive “start over” action.

Required reset scopes:

- `learnings_only`
- `focus_only`
- `next_run_plan_only`
- `workspace_soft_reset`
- `workspace_archive_and_restart`

Required behavior:

- `learnings_only` removes active learnings from future use but preserves history
- `focus_only` clears the current active focus while preserving focus history
- `next_run_plan_only` clears pending continuation intent without deleting prior result contracts
- `workspace_soft_reset` clears active continuation state but preserves lineage and prior runs
- `workspace_archive_and_restart` marks the current workspace archived and creates a new workspace

Relaytic must not silently convert any of those into a full destructive reset.

## Compatibility rules

When Slice 12D lands:

- `relaytic handoff show` remains public
- `relaytic handoff focus` remains public
- `relaytic learnings show` remains public
- `relaytic learnings reset` remains public

Those commands should become compatibility-preserving views or actions over workspace-backed truth rather than being removed.

## Mission-control expectations

Mission control should surface:

- current workspace label
- current run
- prior run count
- current recommended direction
- focus history status
- learnings posture
- reset affordances

Humans should not need to infer workspace continuity by looking at directories.

## Agent expectations

External agents should be able to continue a workspace by reading:

- `workspace_state.json`
- `result_contract.json`
- `next_run_plan.json`
- governed learnings state

Agents should not be required to scrape markdown or compare multiple reports to discover the current continuity posture.
