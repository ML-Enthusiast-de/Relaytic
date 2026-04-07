# Relaytic User Handbook

## Who This Is For

This handbook is for a human operator who wants to understand what Relaytic is, how to start, how the product is meant to be used, and what to do when something is unclear.

If you are an external agent or host wrapper, start with [relaytic_agent_handbook.md](./relaytic_agent_handbook.md) instead.

## What Relaytic Is

Relaytic is a local-first structured-data research lab.

You point it to data, describe the goal in plain language, and Relaytic creates a governed run that can:

- investigate the dataset
- infer likely task structure and route choices
- build and review a model
- challenge itself
- compare against benchmarks and incumbents
- explain what it is doing
- keep the whole process auditable

Relaytic is not meant to be a vague chat shell. Its source of truth is the local artifact graph it writes during a run.

For first-contact UX, Relaytic can also use a lightweight local onboarding helper on the full install profile. That helper is there to understand messy human onboarding messages, not to replace deterministic run control.

## What Relaytic Needs First

Relaytic becomes meaningfully useful after you give it:

- a dataset or local source path
- a short goal in plain language

Good examples of goals:

- `Predict customer churn from this table.`
- `Classify diagnosis_flag from the measurement columns.`
- `Analyze this dataset first and give me the top 3 signals.`
- `Run a correlation analysis before we decide whether to model anything.`
- `Tell me if this existing model is good enough and try to beat it.`
- `Do everything on your own, but keep me informed.`

Relaytic now supports two clean onboarding directions:

- `analysis first`
  Use this when you want exploration, top signals, or a quick correlation-style pass without starting the full governed modeling flow yet.
- `governed run`
  Use this when you want Relaytic to build, challenge, benchmark, and judge a model or incumbent under the full artifact contract.

## The Fastest Start

Run these in order:

```powershell
.\scripts\bootstrap.ps1 -Profile full -LaunchControlCenter
relaytic doctor --expected-profile full --format json
relaytic mission-control chat
```

On macOS/Linux, use:

```bash
bash ./scripts/bootstrap.sh --profile full --launch-control-center
```

If you already know the dataset path and objective, you can still create the first run directly:

```powershell
relaytic run --run-dir artifacts\demo --data-path <data.csv> --text "Describe the goal here."
relaytic mission-control launch --run-dir artifacts\demo
```

If you want questions in the terminal instead of the dashboard:

```powershell
relaytic mission-control chat
```

## The Main Surfaces

### Mission Control

`relaytic mission-control show` or `relaytic mission-control launch`

Use this when you want the big picture:

- what Relaytic is doing now
- what stage the run is in
- what Relaytic thinks should happen next
- what capabilities are available
- what is blocked and why

### Mission Control Chat

`relaytic mission-control chat`

Use this when you want onboarding help or a plain-language explanation.

Good questions:

- `what is relaytic?`
- `how do i start?`
- `show me a demo flow`
- `what do the modes mean?`
- `i'm stuck, what should i do?`
- `why are some capabilities disabled?`

You can also paste things directly instead of phrasing them perfectly:

- a local dataset path
- a plain-language goal
- both in one messy sentence
- a quick-analysis request such as `analyze this data first` or `give me the top 3 signals`

Relaytic should capture what matters, show you what it understood, and ask for the next missing piece.

### Assist

`relaytic assist chat --run-dir <run_dir>`

Use this after a run exists when you want run-specific help:

- explanations of route choice
- bounded stage reruns
- safe takeover
- clearer understanding of the next action

### Show

`relaytic show --run-dir <run_dir>`

Use this when you want the current run summary truth in one place.

## The Main Flow

This is the intended operator flow:

1. Verify the install with `relaytic doctor`.
2. Point Relaytic at a real local dataset.
3. Give it a short goal.
4. Confirm what Relaytic captured if you started from mission-control chat.
5. Open mission control.
6. Inspect the current stage, next action, and capability state.
7. Ask Relaytic questions if anything is unclear.
8. Only then decide whether to let it continue, rerun a bounded stage, or attach an incumbent.

## How Mission-Control Chat Works

Mission-control chat is meant for humans first.

It should let you:

- paste a dataset path directly
- say the objective in plain language
- choose between a quick analysis-first pass and the full governed modeling path
- check what Relaytic has captured with `/state`
- clear the captured onboarding state with `/reset`
- confirm before it creates the first governed run

If the lightweight local onboarding helper is available, Relaytic should also recover gracefully from messy phrasing such as:

- `maybe use "C:\data\churn.csv" because I care about churn risk`
- `this file should predict malignant cases`
- `maybe compare this against our old model too`

## Quick Analysis First

If you are not ready to start a full governed run, mission-control chat should also handle lighter requests like:

- `analyze this data`
- `give me the top 3 signals`
- `run a correlation analysis`
- `explore this dataset first`

That path should produce a direct analysis-first result and then tell you how to switch into the full governed run path if you want modeling next.

## What Happens After You Start A Run

After `relaytic run`, Relaytic typically:

1. interprets the goal and context
2. profiles and investigates the dataset
3. plans a route
4. builds and evaluates a model
5. challenges itself
6. reviews completion and lifecycle posture
7. surfaces the next bounded action in mission control

This means you usually do not need to guess the next step. Relaytic should show it.

## What To Read After A Run

Relaytic now writes two different post-run reports on purpose:

- `reports/user_result_report.md`
  Read this when you want the plain-language human result, the main findings, the main risks, and the best next moves.
- `reports/agent_result_report.md`
  This is the terser machine-facing version. You usually do not need it unless an external agent is helping you.

You can open the handoff directly with:

```powershell
relaytic handoff show --run-dir <run_dir>
```

If you want to tell Relaytic what the next run should focus on:

```powershell
relaytic handoff focus --run-dir <run_dir> --selection same_data --notes "focus on recall"
```

The available next-run directions are:

- `same_data`
  Stay on the same dataset and sharpen the focus
- `add_data`
  Bring in more local data before making a stronger claim
- `new_dataset`
  Start over with a different dataset or problem

## Durable Learnings

Relaytic now keeps a local durable learnings memory so the next run does not always start from zero.

That learnings layer can include:

- assumptions that mattered
- accepted feedback
- skeptical-control lessons
- benchmark or incumbent lessons
- next-run focus decisions
- open safety or evaluation issues

You can inspect it with:

```powershell
relaytic learnings show --run-dir <run_dir>
```

If you want a clean slate:

```powershell
relaytic learnings reset --run-dir <run_dir>
```

Mission-control chat should also understand plain requests like:

- `what did you find?`
- `use the same data next time but focus on recall`
- `show learnings`
- `reset the learnings`

## What The Modes Mean

Relaytic uses different surfaces for different jobs.

### Mission Control

The dashboard. Use it for state, overview, and visibility.

### Mission Control Chat

The onboarding and guidance chat. Use it when you want Relaytic to explain the system, the first steps, the demo flow, or what to do when you are stuck.

### Assist

The run-specific conversation surface. Use it when a run already exists and you want Relaytic to explain a concrete run, rerun one bounded stage, or continue safely.

### Agent Host

The integration layer for Claude, Codex, OpenClaw, and MCP-style clients. Use it when Relaytic is being driven from another tool rather than directly by you.

## Why Some Capabilities Are Disabled

A disabled capability usually means one of three things:

- Relaytic needs a run first
- Relaytic needs data first
- a host or backend still needs activation

Common examples:

- bounded stage reruns need an existing run
- safe takeover needs an existing run with enough state
- incumbent comparison needs a run before Relaytic can compare under the same contract
- some host integrations need explicit activation even though Relaytic itself is healthy

Mission control should show both:

- why the capability is not ready
- what activates it

If it does not, treat that as a UX problem, not your fault.

## What To Do When You Are Stuck

Use this order:

1. Run `relaytic doctor --expected-profile full --format json`
2. Ask `how do i start?` or `show me a demo flow` in mission-control chat
3. Read the capability reasons in mission control before assuming something is broken
4. Read this handbook or the demo walkthrough
5. If a run exists, ask `what can you do?` in assist or mission-control chat
6. If a run exists and you want Relaytic to continue, use safe takeover rather than guessing commands

If you are stuck because you have no data:

- export any small local table to CSV, TSV, Excel, Parquet, JSON, JSONL, or NDJSON
- then run Relaytic on that file

Relaytic cannot do meaningful modeling without data. That is expected.

## The Best First Demo

Use this five-step pattern:

1. Show `relaytic doctor`
2. Run `relaytic run` on a real local dataset
3. Open mission control
4. Ask `what can you do?`
5. Show the next action, capability reasons, and one bounded steering path

If you have a baseline model or prediction file:

6. attach it as an incumbent
7. let Relaytic explain whether it can beat it honestly

## If You Want A Longer Walkthrough

Use:

- [relaytic_demo_walkthrough.md](./relaytic_demo_walkthrough.md)

## Host Integrations

Relaytic can sit under:

- Claude
- Codex / OpenAI-style skill environments
- OpenClaw
- MCP-capable clients

Use:

```powershell
relaytic interoperability show
```

to see what is already discoverable locally and what still needs activation.

## Safe Steering

You can steer Relaytic, but Relaytic is intentionally skeptical about truth-bearing overrides.

That means:

- you can ask questions
- you can request bounded reruns
- you can let Relaytic continue
- but Relaytic may challenge, modify, or reject requests that would weaken the run or bypass guardrails

That is part of the design, not a bug.

## What To Read Next

- [relaytic_demo_walkthrough.md](./relaytic_demo_walkthrough.md)
- [README.md](../../README.md)
- [INTEROPERABILITY.md](../../INTEROPERABILITY.md)
