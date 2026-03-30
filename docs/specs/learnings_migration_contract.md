# Learnings Migration Contract

## Purpose

This document freezes how the already-shipped Slice 12C learnings surfaces should evolve into the governed learnings model defined for Slice 12D and later slices.

The goal is to preserve continuity without preserving ambiguity.

## Current canonical Slice 12C artifacts

- `lab_memory/learnings_state.json`
- `lab_memory/learnings.md`
- `lab_learnings_snapshot.json`

## Future governed-learnings expectations

Later learnings should become:

- typed
- confidence-bearing
- invalidatable
- resettable
- optionally expirable
- scoped

The target behavior is defined in:

- `docs/specs/governed_learnings_schema.md`

This document defines how to get there without breaking current surfaces.

## Migration rule

After Slice 12D lands:

- `learnings_state.json` remains public
- `learnings.md` remains public
- `lab_learnings_snapshot.json` remains public

But:

- `learnings_state.json` should evolve to carry governed fields
- `learnings.md` should become a rendering of the structured governed state
- `lab_learnings_snapshot.json` should become a run-local view into the current governed state plus newly harvested learnings

## Required additive fields

Future `learnings_state.json` entries should add, at minimum:

- `source_type`
- `scope`
- `confidence`
- `status`
- `last_reaffirmed_at`
- `invalidated_at`
- `invalidation_reason`
- `expires_at`

Those fields should be added compatibly rather than through a disruptive rename.

## Backward compatibility behavior

If old learnings entries exist without the new governed fields:

- Relaytic should treat them as legacy entries
- missing fields should be populated conservatively
- legacy entries should not be discarded just because they predate the stronger schema

Recommended conservative defaults:

- `confidence`: `low`
- `status`: `tentative`
- `source_type`: `observed_runtime`

## Reset compatibility

Current reset behavior should continue to work, but future resets should become more explicit.

Later implementation should preserve support for:

- `relaytic learnings reset`
- `relaytic_reset_learnings`

while allowing stronger reset semantics under the hood.

## Influence rules

Until entries are governed explicitly:

- legacy learnings should have weaker planning influence than active governed entries
- invalidated or expired entries should not influence planning
- reset entries should remain visible for audit but not active for recommendation logic

## Anti-patterns

Later implementation must not:

- silently reinterpret old learnings as high-confidence governed truth
- delete historical learnings just because the schema improved
- let markdown become the only surviving source of learnings truth
