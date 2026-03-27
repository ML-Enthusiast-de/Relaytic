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
- `memory_compaction_plan.json`
- `memory_compaction_report.json`
- `memory_pinning_index.json`

## Intent

Slice 12A is where Relaytic stops being only on-demand and starts becoming periodically aware in a controlled way.

This slice is successful only if Relaytic can:

- wake up on an explicit bounded schedule
- inspect local runtime state, benchmark debt, memory health, research freshness, and stale challenge pressure
- maintain a longer-lived memory stack through explicit retention, compaction, and pinning
- decide whether to skip, recommend, or queue one bounded low-risk follow-up
- remain policy-gated, stoppable, and non-drifting

## Load-Bearing Improvement

- Relaytic should be able to wake on a bounded schedule, inspect stale or weak local state, maintain longer-lived memory, and either recommend or queue safe bounded follow-up without silently drifting its core behavior

## Human Surface

- humans should be able to inspect the pulse schedule, pulse reasons, skipped versus executed pulse runs, innovation-watch findings, memory-maintenance actions, queued follow-ups, and why Relaytic did or did not act

## Agent Surface

- external agents should be able to read pulse recommendations, watchlists, skip reasons, memory-compaction reports, and queued follow-up actions as stable artifacts and optionally trigger the same pulse manually

## Intelligence Source

- runtime state, stage/event history, benchmark gaps, research memory, causal memory, dojo proposals, local source freshness, and policy-gated redacted innovation retrieval

## Fallback Rule

- if a richer pulse input is unavailable, Relaytic should record that it skipped or reduced the pulse rather than inventing urgency or silently doing nothing

## Required Behavior

- pulse must support disabled, observe-only, propose-only, and bounded-execute modes
- pulse must leave explicit reports whether it skipped or acted
- pulse must not silently rewrite defaults, promote dojo outputs, or mutate core contracts
- pulse may only trigger bounded low-risk actions by default
- memory maintenance must upgrade Relaytic from analog retrieval toward episodic, intervention, outcome, and method memory with explicit compaction and pinning rules
- heavier actions must remain recommendations unless existing autonomy/control policy explicitly allows them
- innovation-watch behavior must stay rowless and redacted for any external retrieval
- pulse should use the runtime/event system rather than inventing a parallel scheduler truth
- the mission-control surface introduced in Slice 11B and clarified in Slice 11C, together with later assist surfaces, should expose pulse history directly rather than leaving pulse state as a side artifact

## Proof Obligation

- Relaytic must prove it can remain alive without becoming noisy theater, and that memory maintenance changes later behavior only through explicit, auditable artifacts

## Acceptance Criteria

Slice 12A is acceptable only if:

1. one pulse run explicitly skips because nothing useful is pending
2. one pulse run writes a challenge watchlist without taking unsafe action
3. one pulse run queues one bounded low-risk follow-up through explicit policy
4. one pulse run surfaces a new relevant method or benchmark lead through redacted innovation watch
5. one pulse run is visible to humans and external agents through the same artifact contract
6. one pulse run compacts or pins memory in a way that changes later retrieval quality or avoids forgetting a previously harmful intervention

## Required Verification

Slice 12A should not be considered complete without targeted tests that cover at least:

- one skip/throttle case
- one propose-only case
- one bounded-execute case
- one redacted innovation-watch case
- one stale-run or stale-benchmark watchlist case
- one CLI/MCP visibility-parity case
- one memory-compaction or memory-pinning case
