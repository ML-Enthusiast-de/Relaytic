# Slice 16D - Hunt campaigns, seeded exploration, and provider feedback

## Status

Planned.

Intended package boundaries:

- `src/relaytic/capability_academy/`
- extend `src/relaytic/daemon/`
- extend `src/relaytic/pulse/`
- extend `src/relaytic/search/`
- extend `src/relaytic/remote_control/`

Intended artifacts:

- `hunt_campaign_state.json`
- `hunt_target_selection.json`
- `hunt_candidate_log.jsonl`
- `hunt_outcome_report.json`
- `provider_feedback_report.json`
- `exploration_budget_report.json`
- `exploration_seed_log.jsonl`
- `exploration_policy_report.json`

## Intent

Slice 16D gives Relaytic bounded autonomous capability scouting.

## Load-Bearing Improvement

- Relaytic should be able to use idle daemon or pulse windows to scout benchmark gaps, sample candidates, run bounded hunt campaigns, and generate reusable provider feedback without silently mutating production behavior

## Human Surface

- humans should be able to see what Relaytic hunted for, what budget it spent, what it found, and why the hunt stopped

## Agent Surface

- external agents should be able to inspect hunt state, seeds, targets, and provider feedback through stable JSON-first surfaces and remote supervision

## Intelligence Source

- pulse watchlists, benchmark gaps, repeated workspace failures, imported incumbent deficits, seeded candidate sampling, and bounded daemon execution

## Fallback Rule

- when hunt mode is disabled, Relaytic must keep the same targets and candidate queues visible but must not run autonomous scouting work

## Required Behavior

- hunt mode must be budgeted, seeded, replayable, and stoppable
- hunt campaigns must target explicit gaps rather than arbitrary exploration
- failed hunts must still produce provider feedback
- remote supervision must be able to inspect and gate hunt campaigns through the same authority path

## Acceptance Criteria

Slice 16D is acceptable only if:

1. one hunt campaign runs from an explicit target gap to a queued candidate outcome
2. one hunt campaign exhausts its budget and stops honestly
3. one failed candidate still yields useful provider feedback
4. one seeded hunt can be replayed deterministically

## Required Verification

- one hunt-budget test
- one hunt-replay test
- one failed-candidate provider-feedback test
- one remote-supervision visibility test
