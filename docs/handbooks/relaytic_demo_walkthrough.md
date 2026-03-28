# Relaytic Demo Walkthrough

## Goal

This walkthrough is the shortest reliable path for showing Relaytic to someone who has never seen it before.

Use it for:

- recruiter demos
- first-contact user demos
- internal onboarding
- agent-host demo sessions

## What You Need

- a working Relaytic install
- one local structured dataset
- a short goal in plain language

If you use the full install profile, Relaytic will also try to provision a lightweight local onboarding helper. That helper is meant to make first-contact chat more forgiving for humans; it does not replace deterministic run control.

Any small local CSV, TSV, Excel, Parquet, JSON, JSONL, or NDJSON file is enough for a first demo.

## The Five-Step Demo

### 1. Verify The Local Environment

```powershell
python scripts/install_relaytic.py --profile full --launch-control-center
```

What to say:

- Relaytic is local-first
- it checks its own install before touching data
- on the full profile it tries to provision a lightweight local onboarding helper for messy first-contact human input
- the environment health is part of the product surface

### 2. Start From Mission-Control Chat Or Create One Real Run

Human-first path:

```powershell
relaytic mission-control chat
```

Then paste:

- the dataset path
- the objective
- or both in one message

Relaytic should capture what it understands, ask for the missing piece, and confirm before it creates the run.

Direct CLI path:

```powershell
relaytic run --run-dir artifacts\demo --data-path <data.csv> --text "Describe the goal here." --format json
```

What to say:

- Relaytic needs data plus a goal
- it creates a governed run instead of a loose notebook session
- the run is the source of truth for later review

### 3. Open Mission Control

```powershell
relaytic mission-control launch --run-dir artifacts\demo
```

Or, if you want terminal-only:

```powershell
relaytic mission-control show --run-dir artifacts\demo
```

What to say:

- mission control is the main control center
- it shows current stage, next action, capabilities, queue state, and operator guidance
- the UI is driven by the same artifact truth as the CLI

### 4. Ask A Plain-Language Question

Use either:

```powershell
relaytic mission-control chat
```

or:

```powershell
relaytic assist turn --run-dir artifacts\demo --message "what can you do?" --format json
```

Good follow-up questions:

- `what can you do?`
- `why did you choose this route?`
- `what is the next action?`
- `go back to planning`

What to say:

- Relaytic explains itself
- Relaytic exposes bounded steering
- Relaytic does not pretend to be a blind chat shell

### 5. Show One Controlled Next Step

Pick one:

- inspect the next recommended action
- rerun one bounded stage
- attach an incumbent
- let Relaytic continue safely

Example:

```powershell
relaytic assist turn --run-dir artifacts\demo --message "go back to planning" --format json
```

What to say:

- Relaytic supports bounded control
- it can be influenced
- but it preserves explicit control and artifact truth

## If You Have An Existing Model

Use:

```powershell
relaytic benchmark run --run-dir artifacts\demo --data-path <data.csv> --incumbent-path <path> --incumbent-kind model
```

What to say:

- Relaytic can compare against an incumbent under the same contract
- it is not just benchmarking against abstract references

## If You Need To Explain Why This Is Different

Say this:

Relaytic is not just AutoML with agent names. It is a local-first structured-data lab with explicit artifacts, skeptical control, bounded autonomy, benchmark pressure, and a shared control surface for humans and external agents.

## What To Do If Something Feels Off During The Demo

1. run `relaytic doctor`
2. open mission-control chat
3. ask `i'm stuck, what should i do?`
4. inspect capability reasons before assuming something is broken
5. prefer one bounded step over many ad hoc commands

## Recommended Follow-Up Docs

- [relaytic_user_handbook.md](./relaytic_user_handbook.md)
- [relaytic_agent_handbook.md](./relaytic_agent_handbook.md)
- [README.md](../../README.md)
