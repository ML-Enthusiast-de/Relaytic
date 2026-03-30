# Slice 12C - Differentiated result handoff and durable learnings

## Status

Implemented.

Canonical package boundaries:

- `src/relaytic/handoff/`
- `src/relaytic/learnings/`

Landed minimum modules:

- `src/relaytic/handoff/models.py`
- `src/relaytic/handoff/storage.py`
- `src/relaytic/handoff/agents.py`
- `src/relaytic/learnings/models.py`
- `src/relaytic/learnings/storage.py`
- `src/relaytic/learnings/agents.py`

Canonical artifacts:

- `run_handoff.json`
- `next_run_options.json`
- `next_run_focus.json`
- `reports/user_result_report.md`
- `reports/agent_result_report.md`
- `lab_learnings_snapshot.json`
- `lab_memory/learnings_state.json`
- `lab_memory/learnings.md`

Public commands:

- `relaytic handoff show`
- `relaytic handoff focus`
- `relaytic learnings show`
- `relaytic learnings reset`

MCP surfaces:

- `relaytic_show_handoff`
- `relaytic_set_next_run_focus`
- `relaytic_show_learnings`
- `relaytic_reset_learnings`

## Intent

Slice 12C is where Relaytic stops ending at one generic summary and starts closing the loop cleanly for both humans and external agents.

Landed implementation notes:

- Relaytic now materializes a differentiated user-facing result report and a terser agent-facing handoff from the same canonical run summary
- Relaytic now records explicit next-run options so the operator or an external agent can choose whether to stay on the same data, add data, or start over with a new dataset
- Relaytic now writes durable workspace learnings in markdown and JSON so the next run does not start from zero by accident
- mission control, assist, and interoperability now surface result handoff and durable learnings directly instead of leaving them as hidden side artifacts
- run-context mission-control chat can now answer `what did you find?`, save a next-run focus, show learnings, and reset learnings without dropping the user into a lower-level shell
- memory retrieval now reads the durable learnings state and carries workspace focus and recent lesson context into reflection and later reuse

The slice is successful only if Relaytic can:

- explain the same run differently to a human and an external agent without inventing two truths
- let a human or agent choose the next-run direction explicitly
- retain durable cross-run lessons in a local-first way
- let the operator reset those learnings deliberately
- expose the same handoff and learnings truth through CLI, mission control, assist, and MCP

## Load-Bearing Improvement

- Relaytic should be able to end every serious run with a differentiated human-and-agent handoff, a bounded next-run steering contract, and durable local learnings that can influence future work without turning into hidden drift

## Human Surface

- humans should be able to read a narrative result report, understand what Relaytic found, choose the next-run direction, inspect what Relaytic learned from prior runs, and reset those learnings if they want a clean slate

## Agent Surface

- external agents should be able to consume a terser result handoff, read machine-stable next-run options, persist the chosen next-run focus, inspect durable learnings, and reset workspace learnings through stable JSON-first and MCP-accessible surfaces

## Intelligence Source

- canonical run-summary truth, explicit handoff synthesis, durable local learnings harvested from assumptions, feedback, benchmark outcomes, control incidents, trace/eval posture, and operator-selected next-run focus

## Fallback Rule

- if differentiated report rendering or durable learnings are unavailable for a run, Relaytic must still preserve `run_summary.json` and `reports/summary.md` as the fallback truth while recording that handoff or learnings were not materialized

## Required Behavior

- the user report and the agent report must be generated from the same canonical run summary rather than from separate hidden state
- the user report should prioritize findings, risks, next moves, and operator-readable guidance
- the agent report should prioritize run state, winning action, artifact paths, next-run options, and reusable commands
- Relaytic must expose at least three next-run options:
  - `same_data`
  - `add_data`
  - `new_dataset`
- next-run focus selection must be explicit, persisted, and reviewable rather than hidden in chat state
- durable learnings must be local-first and resettable
- durable learnings must harvest at least:
  - assumptions
  - accepted feedback or outcome pressure
  - skeptical-control lessons
  - benchmark/incumbent outcomes
  - next-run focus decisions
  - open safety/eval lessons
- resetting learnings must clear the durable learnings state for the workspace and must not silently repopulate it on the same summary refresh
- mission control should show that a result handoff exists, that durable learnings exist, and what the current next-run focus is
- assist and mission-control chat should let humans say:
  - `what did you find?`
  - `use the same data next time but focus on recall`
  - `show learnings`
  - `reset the learnings`
- external-agent wrappers and MCP tools must expose the same handoff and learnings capabilities without scraping markdown
- memory retrieval should consume durable learnings as explicit workspace priors rather than ignoring them completely

## Proof Obligation

- Relaytic must prove that humans and agents receive differentiated but aligned post-run handoffs, that next-run steering is explicit and durable, and that learnings survive across runs until deliberately reset

## Acceptance Criteria

Slice 12C is acceptable only if:

1. one governed run writes both a user result report and an agent result report and they are meaningfully different
2. one CLI handoff review case exposes the same recommended next-run option that appears in the run summary
3. one next-run focus selection updates the persisted handoff state without forcing a rerun
4. one durable learnings view shows both workspace learnings and current-run active learnings
5. one learnings reset case clears the workspace state and does not silently repopulate on immediate summary refresh
6. one mission-control run-context chat case supports result-report review, next-run focus selection, learnings review, and learnings reset in a natural multi-turn flow
7. one external-agent or MCP case consumes the same handoff and learnings truth without scraping prose
8. one memory case shows that durable learnings are visible to the memory layer as reusable priors rather than remaining isolated UI state

## Required Verification

Slice 12C should not be considered complete without targeted tests that cover at least:

- one end-to-end governed run with differentiated user and agent reports
- one CLI handoff surface case
- one CLI next-run focus case
- one CLI durable learnings show/reset case
- one mission-control run-context chat case using natural phrasing
- one human-chaos detour case where the conversation stays coherent
- one external-agent wrapper case for handoff and learnings
- one memory integration case where durable learnings appear in the memory signature or reflection output
