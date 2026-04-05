# Slice 16F - Academy mission control and explainability surfaces

## Status

Planned.

Intended package boundaries:

- `src/relaytic/mission_control/`
- extend `src/relaytic/capability_academy/`
- extend `src/relaytic/interoperability/`
- extend `src/relaytic/remote_control/`

Intended artifacts:

- `academy_state.json`
- `academy_registry_view.json`
- `academy_trial_dashboard.json`
- `academy_hunt_view.json`
- `academy_promotion_timeline.json`
- `academy_explanation_report.json`
- `academy_remote_approval_view.json`

## Intent

Slice 16F makes the academy legible to humans and external agents.

## Load-Bearing Improvement

- Relaytic should expose one professional academy surface that shows promoted capabilities, candidates in replay or shadow, hunt campaigns, roster changes, and promotion or retirement reasons from the same runtime truth

## Human Surface

- humans should be able to ask why a capability was promoted, blocked, or retired and get a trace-backed explanation without reading raw artifact trees

## Agent Surface

- external agents should be able to query the same academy state, candidate registry, trial posture, and promotion reasoning through stable JSON-first surfaces and MCP tools

## Intelligence Source

- capability cards, replay and shadow evidence, arena scorecards, provider feedback, roster change history, and remote-supervision state

## Fallback Rule

- if richer UI rendering is unavailable, Relaytic must still expose the same academy truth through CLI, MCP, and artifacts without degrading explainability

## Required Behavior

- academy mission control must consume academy truth rather than re-summarizing from prose
- explanation answers must cite the promotion or retirement evidence that actually drove the decision
- academy views must stay aligned across CLI, MCP, and remote supervision
- humans and external agents must be able to inspect current hunt posture and current promotion backlog from one coherent surface

## Acceptance Criteria

Slice 16F is acceptable only if:

1. one human can inspect promoted capabilities, shadow candidates, and hunt campaigns from one academy view
2. one agent can query the same academy state through MCP or JSON-first surfaces
3. one "why was this promoted?" explanation is trace-backed and specific
4. one remote supervisor can inspect academy promotion or hunt state without creating a second authority path

## Required Verification

- one CLI academy-view test
- one MCP academy-view test
- one explanation-quality test
- one remote-supervision parity test
