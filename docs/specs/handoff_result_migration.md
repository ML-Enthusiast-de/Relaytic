# Handoff And Result-Contract Migration

## Purpose

This document freezes how the already-shipped Slice 12C handoff surfaces should evolve once Slice 12D introduces canonical result contracts and workspace-backed continuity.

The goal is to preserve compatibility while making later product behavior much more explicit.

## Current canonical Slice 12C artifacts

- `run_handoff.json`
- `next_run_options.json`
- `next_run_focus.json`
- `reports/user_result_report.md`
- `reports/agent_result_report.md`

These are already shipped and should not be treated as disposable prototypes.

## Future canonical Slice 12D artifacts

- `result_contract.json`
- `confidence_posture.json`
- `belief_revision_triggers.json`
- `next_run_plan.json`
- `focus_decision_record.json`

## Migration rule

After Slice 12D lands:

- `result_contract.json` becomes the canonical machine-stable post-run truth
- the Slice 12C handoff artifacts remain public compatibility surfaces
- the Slice 12C handoff artifacts become views or projections derived from the canonical result contract and workspace continuity state

## Required mappings

### `run_handoff.json`

Future role:

- compatibility-preserving summary artifact

Expected source mapping:

- headline and summary derive from `result_contract.json`
- key findings derive from `current_beliefs`
- risks and open questions derive from `unresolved_items`
- recommended option derives from `recommended_next_move`

### `next_run_options.json`

Future role:

- compatibility-preserving option view

Expected source mapping:

- options derive from `next_run_plan.json`
- recommended option derives from `recommended_direction`
- why-not reasoning derives from `why_not_other_moves`

### `next_run_focus.json`

Future role:

- compatibility-preserving record of selected continuation focus

Expected source mapping:

- selected focus should align with `focus_decision_record.json`
- workspace-level active focus should align with `workspace_focus_history.json`

### `reports/user_result_report.md`

Future role:

- human-optimized rendering of the current result contract

Must emphasize:

- what Relaytic found
- how strong the evidence is
- what remains unresolved
- what the recommended next move is
- what the user can do next

### `reports/agent_result_report.md`

Future role:

- agent-optimized rendering of the current result contract

Must emphasize:

- current belief summary
- unresolved items
- recommended next move
- artifact references
- continuity hints

## Compatibility promises

When Slice 12D lands:

- existing commands must keep working
- existing MCP surfaces must keep working
- existing handoff artifacts may become projections, but should not silently disappear

Specifically:

- `relaytic handoff show` remains public
- `relaytic handoff focus` remains public
- `relaytic_show_handoff` remains public
- `relaytic_set_next_run_focus` remains public

## Anti-patterns

Later implementation must not:

- keep two conflicting post-run truths
- let reports diverge from the canonical result contract
- quietly remove handoff surfaces because a new artifact exists
- force old clients to scrape markdown when machine-stable artifacts exist
