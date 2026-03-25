# Slice 12A - Lab Pulse, periodic awareness, and bounded proactive follow-up

## Status

Planned.

Intended package boundary:

- `src/relaytic/pulse/`

Intended artifacts:

- `pulse_schedule.json`
- `pulse_run_report.json`
- `pulse_skip_report.json`
- `pulse_recommendations.json`
- `innovation_watch_report.json`
- `challenge_watchlist.json`
- `pulse_checkpoint.json`

## Intent

Slice 12A is where Relaytic stops being only on-demand and starts becoming periodically aware in a controlled way.

This slice is successful only if Relaytic can:

- wake up on an explicit bounded schedule
- inspect local runtime state, benchmark debt, memory health, research freshness, and stale challenge pressure
- decide whether to skip, recommend, or queue one bounded low-risk follow-up
- remain policy-gated, stoppable, and non-drifting

## Required Behavior

- pulse must support disabled, observe-only, propose-only, and bounded-execute modes
- pulse must leave explicit reports whether it skipped or acted
- pulse must not silently rewrite defaults, promote dojo outputs, or mutate core contracts
- pulse may only trigger bounded low-risk actions by default
- heavier actions must remain recommendations unless existing autonomy/control policy explicitly allows them
- innovation-watch behavior must stay rowless and redacted for any external retrieval
- pulse should use the runtime/event system rather than inventing a parallel scheduler truth
- later mission-control and assist surfaces should be able to expose pulse history directly

## Acceptance Criteria

Slice 12A is acceptable only if:

1. one pulse run explicitly skips because nothing useful is pending
2. one pulse run writes a challenge watchlist without taking unsafe action
3. one pulse run queues one bounded low-risk follow-up through explicit policy
4. one pulse run surfaces a new relevant method or benchmark lead through redacted innovation watch
5. one pulse run is visible to humans and external agents through the same artifact contract

## Required Verification

Slice 12A should not be considered complete without targeted tests that cover at least:

- one skip/throttle case
- one propose-only case
- one bounded-execute case
- one redacted innovation-watch case
- one stale-run or stale-benchmark watchlist case
- one CLI/MCP visibility-parity case
