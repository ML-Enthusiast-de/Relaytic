# Governed Learnings Schema

## Purpose

This document defines how durable learnings should behave once Slice 12D lands.

The goal is to preserve useful continuity without letting prior guesses, user preferences, or stale conditions silently become hidden truth.

## Canonical artifacts

- `learnings_state.json`
- `learnings.md`
- `lab_learnings_snapshot.json`

Future workspace-aware supporting artifacts:

- `workspace_memory_policy.json`

## Core rule

Every active learning must be:

- typed
- scoped
- confidence-bearing
- attributable
- reaffirmable
- invalidatable
- resettable
- optionally expirable

## Learning record schema

Each structured learning record should include:

- `learning_id`
- `statement`
- `source_type`
- `source_ref`
- `scope`
- `confidence`
- `status`
- `applies_to`
- `created_at`
- `last_reaffirmed_at`
- `invalidated_at`
- `invalidation_reason`
- `expires_at`
- `used_in_runs`

## Source types

Required `source_type` values:

- `observed_runtime`
- `user_feedback_validated`
- `external_agent_feedback_validated`
- `benchmark_outcome`
- `control_incident`
- `result_contract`
- `memory_compaction`
- `operator_override_review`

## Scope values

Required `scope` values:

- `workspace`
- `dataset_family`
- `objective_family`
- `route_family`
- `lab_global`

`lab_global` should be used rarely and only for strongly validated lessons.

## Confidence values

Required `confidence` values:

- `low`
- `medium`
- `high`

Low-confidence learnings may be surfaced as hints, but should not dominate planning over stronger evidence.

## Status values

Required `status` values:

- `active`
- `tentative`
- `invalidated`
- `expired`
- `reset`

Only `active` and `tentative` learnings may influence future planning.

## Applies-to object

`applies_to` should allow structured matching fields such as:

- `workspace_id`
- `dataset_signature`
- `objective_type`
- `target_name`
- `route_family`
- `benchmark_family`

The absence of a field should not imply universal applicability.

## Reaffirmation rules

A learning should be reaffirmed when later runs provide corroborating evidence.

Reaffirmation should update:

- `last_reaffirmed_at`
- `confidence`
- `used_in_runs`

Reaffirmation must not overwrite the original source attribution.

## Invalidation rules

Invalidation should be explicit and non-destructive.

An invalidated learning should keep:

- original statement
- original source
- invalidation timestamp
- invalidation reason
- invalidating artifact reference when available

Relaytic must prefer invalidation over silent disappearance when a formerly active learning stops being trustworthy.

## Expiry rules

Expiry should be used when a learning is time-sensitive or context-sensitive.

Examples:

- stale data-quality assumptions
- route preferences tied to an old schema
- benchmark lessons that no longer apply after policy or objective changes

Expiry must move a learning out of active influence without deleting history.

## Reset rules

Reset should operate on active influence, not historical existence.

Required reset behaviors:

- `soft_reset`: move active learnings to `reset` while preserving history
- `scope_reset`: reset learnings within one workspace or scope only
- `full_learning_reset`: clear active learnings across the current workspace and mark them reset

Relaytic must not silently repopulate reset learnings on the same refresh unless a new validating source is recorded.

## Markdown rendering

`learnings.md` should be a readable rendering of structured learnings, not the authoritative source itself.

It should separate:

- active learnings
- tentative learnings
- invalidated learnings
- expired learnings
- reset history

## Planning rules

Planning and memory retrieval should:

- prefer active learnings over tentative learnings
- prefer stronger direct workspace learnings over weaker analog hints
- ignore invalidated and expired learnings for recommendation logic
- preserve visibility of invalidated and expired learnings for audit and replay

## Testing expectations

Future tests should prove:

- active learnings influence later planning
- invalidated learnings stop influencing planning
- expired learnings stop influencing planning
- resets remove active influence without deleting history
- workspace-scoped learnings do not leak into unrelated workspaces without explicit justification
