# Mission Control Contract

## Purpose

This document freezes the current mission-control contract shipped across Slices 11B through 11G so later slices can extend it without quietly redefining the operator experience.

The goal is to make the already-coded mission-control layer a stable foundation rather than a moving target.

## Scope

This contract governs:

- mission-control state artifacts
- onboarding and launch artifacts
- role-aware visibility expectations
- current chat and guidance affordances
- compatibility rules for later workspace and trace-native expansion

This document complements, but does not replace:

- `docs/specs/mission_control_flows.md`
- `docs/specs/workspace_lifecycle.md`

## Current canonical artifacts

The current mission-control contract should preserve these artifact families:

- `mission_control_state.json`
- `review_queue_state.json`
- `control_center_layout.json`
- `onboarding_status.json`
- `install_experience_report.json`
- `launch_manifest.json`
- `demo_session_manifest.json`
- `ui_preferences.json`
- `mode_overview.json`
- `capability_manifest.json`
- `action_affordances.json`
- `stage_navigator.json`
- `question_starters.json`
- `onboarding_chat_session_state.json`
- `reports/mission_control.html`

## Core rule

Mission control is not a side dashboard. It is a first-class operator surface built on the same truth already exposed through CLI, MCP, and canonical artifacts.

Later slices must extend that truth instead of inventing UI-only state.

## Always-visible contract

At minimum, the main mission-control surface should always make visible:

- current status
- current run when present
- current stage when present
- recommended action
- next actor
- review requirement
- core capability posture
- visible action affordances
- visible onboarding help when no run exists

If one of those is unavailable, mission control should say so explicitly rather than silently dropping the category.

## Human-facing expectations

For humans, mission control should make clear:

- what Relaytic is
- what it needs next
- what it can do right now
- what the human can do right now
- whether the current path is onboarding, analysis-first, or governed-run work

Humans should not need to read raw JSON to know the next useful action.

## Agent-facing expectations

For external agents, mission control should expose:

- stable JSON artifacts
- stable MCP-visible surfaces
- capability status
- action affordances
- question starters or handbook pointers
- current continuity posture once workspaces exist

External agents should not need to scrape the HTML mission-control report.

## Current chat contract

The current mission-control chat should remain bounded and explicit.

It should support:

- onboarding guidance
- capability explanation
- handbook access
- stuck recovery
- adaptive dataset/objective capture
- safe transitions into analysis-first or governed-run flows

It must not pretend to be an unconstrained general assistant when it is really a workflow conductor.

## Role-aware rendering rule

Mission control may render differently for humans and agents, but the following must remain aligned:

- current state
- current recommendation
- capability posture
- next-step options
- canonical artifact references

## Fallback behavior

If richer UI surfaces are unavailable:

- `mission_control_state.json` remains canonical
- CLI and MCP should still expose the same state categories
- onboarding/help should remain accessible through text-first surfaces

If no run exists:

- mission control should switch into an onboarding-first posture rather than showing an empty run shell

## Compatibility rules for later slices

Later slices, especially 12D and 15, must:

- extend the current mission-control contract rather than replacing it
- preserve the current artifacts unless an explicit migration contract says otherwise
- treat `mission_control_state.json` as current truth even when richer workspace and trace-native surfaces are added

Slice 15 may add:

- branch DAG
- confidence map
- trace explorer
- workspace continuity views

But it must not break the operator legibility already established in Slices 11B through 11G.
