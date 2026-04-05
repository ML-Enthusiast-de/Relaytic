# Slice 16E - Non-core specialist recruitment and retirement

## Status

Planned.

Intended package boundaries:

- `src/relaytic/capability_academy/`
- extend `src/relaytic/search/`
- extend `src/relaytic/mission_control/`
- extend `src/relaytic/permissions/`

Intended artifacts:

- `specialist_candidate_queue.json`
- `recruitment_decision_report.json`
- `specialist_trial_report.json`
- `capability_retirement_report.json`
- `roster_change_log.jsonl`
- `core_agent_protection_report.json`

## Intent

Slice 16E gives Relaytic a governed way to add or remove non-core specialists.

## Load-Bearing Improvement

- Relaytic should be able to recruit useful specialist agents for recurring needs and retire underperforming non-core specialists without allowing uncontrolled roster drift or any deletion of core agents

## Human Surface

- humans should be able to inspect why a non-core specialist was recruited, why it was retired, and how that changed capability coverage

## Agent Surface

- external agents should be able to propose non-core specialists and inspect roster decisions through stable JSON-first surfaces

## Intelligence Source

- repeated workspace gaps, hunt outcomes, arena results, transfer evidence, and deterministic roster rules

## Fallback Rule

- when recruitment logic is disabled, Relaytic must preserve the existing roster and record proposals as candidate-only without changing execution routing

## Required Behavior

- core agents must remain non-deletable
- non-core specialists must require the same replay, shadow, and promotion proof as tools
- retirement must require explicit evidence, not just age or inactivity
- roster changes must remain rollbackable and auditable

## Acceptance Criteria

Slice 16E is acceptable only if:

1. one non-core specialist is recruited for a recurring capability gap
2. one underperforming non-core specialist is retired with explicit evidence
3. one attempt to retire a core agent is rejected and audited
4. one roster change alters available routing without changing authority rules

## Required Verification

- one specialist-recruitment test
- one specialist-retirement test
- one no-core-deletion guard
- one routing-update regression test
