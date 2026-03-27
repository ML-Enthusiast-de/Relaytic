# Slice 11C - Mission-control clarity, capabilities, and guided stage navigation

## Status

Implemented.

Shipped package boundaries:

- extend `src/relaytic/mission_control/`
- extend `src/relaytic/assist/`
- extend `src/relaytic/ui/`
- extend `src/relaytic/interoperability/`

Shipped artifacts:

- `mode_overview.json`
- `capability_manifest.json`
- `action_affordances.json`
- `stage_navigator.json`
- `question_starters.json`

## Intent

Slice 11C is where Relaytic stops assuming the operator already understands the lab and starts making the interaction model explicit on first contact.

The slice is successful only if Relaytic can:

- show the current modes, next actor, and skeptical-control posture without making the user infer them from multiple artifacts
- show what Relaytic can do now and what the human or external agent can do now
- show that stage navigation is bounded stage rerun rather than arbitrary checkpoint time travel
- provide starter questions so the system feels immediately explorable instead of shell-guessy

## Load-Bearing Improvement

- Relaytic should make its control model legible on first contact so humans and external agents can immediately see what mode it is in, what it can do, what they can do next, and what remains deliberately bounded

## Human Surface

- humans should be able to open mission control or assist on a fresh run and immediately understand current stage, current modes, next actor, safe next actions, bounded stage reruns, starter questions, and why Relaytic may challenge an override

## Agent Surface

- external agents should be able to read the same mode overview, capability manifest, action-affordance state, stage navigator, and starter-question state through JSON-first and MCP-accessible mission-control surfaces

## Intelligence Source

- shared run summary
- assist controls
- host inventory
- backend discovery
- benchmark/incumbent posture
- decision-lab posture
- skeptical-control posture
- doctor/install-health state

## Fallback Rule

- if richer UI rendering or previously materialized assist artifacts are missing, Relaytic must still derive the same clarity state from the canonical run truth instead of hiding capabilities or assuming prior interaction

## Required Behavior

- mission control must expose autonomy mode, intelligence mode, routed mode, local profile, takeover availability, skeptical-control posture, and next actor as first-class state
- mission control and assist must expose what Relaytic can do now, what the user or external agent can do now, and which bounded stage reruns are available
- stage navigation must explicitly say that Relaytic supports bounded stage reruns, not arbitrary checkpoint time travel
- starter questions must be visible so first-time users and external agents know how to ask for explanation, capabilities, challenged-steering rationale, stage reruns, and safe takeover
- quick CLI and MCP mission-control payloads must expose next actor, capability counts, action counts, question counts, and navigation scope without requiring the full bundle
- the clarity layer must remain derived from canonical run truth rather than becoming a UI-only interaction state machine

## Proof Obligation

- Relaytic must prove that a fresh run is already understandable and steerable before the operator learns the assist vocabulary by trial and error

## Acceptance Criteria

Slice 11C is acceptable only if:

1. one fresh-run mission-control case exposes modes, capabilities, actions, navigation scope, and starter questions before `assist show` is called
2. one assist case answers `what can you do?` with explicit mention of bounded questions, bounded stage reruns, safe takeover, and skeptical steering
3. one CLI and MCP parity case shows the same next actor, capability counts, and navigation scope
4. one bounded-navigation case clearly communicates that Relaytic can rerun named stages but cannot jump to an arbitrary checkpoint

## Required Verification

Slice 11C should not be considered complete without targeted tests that cover at least:

- one mission-control visibility case for modes/capabilities/actions/navigation/questions
- one assist capability-response case
- one fresh-run auto-materialization case for the clarity artifacts
- one CLI/MCP parity case for the quick mission-control surface

## Shipped Surface

The implemented surface now includes:

- mission-control artifacts for modes, capabilities, action affordances, stage navigation, and starter questions
- richer `relaytic mission-control show` and `relaytic mission-control launch` quick payloads
- richer `relaytic assist show` output with visible actions, stages, and starter questions
- a `what can you do?` assist path that explains how to interact with Relaytic safely
