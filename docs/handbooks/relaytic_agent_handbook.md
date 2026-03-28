# Relaytic Agent Handbook

## Goal

This handbook is the shortest safe path for an external agent or host wrapper that needs to operate Relaytic predictably and explain it to a human without inventing product behavior.

If you are a human operator, start with [relaytic_user_handbook.md](./relaytic_user_handbook.md).

## Read In This Order

1. `AGENTS.md`
2. `RELAYTIC_VISION_MASTER.md`
3. `RELAYTIC_BUILD_MASTER.md`
4. `ARCHITECTURE_CONTRACT.md`
5. `IMPLEMENTATION_STATUS.md`
6. `MIGRATION_MAP.md`
7. `RELAYTIC_SLICING_PLAN.md`

## Core Operating Rule

Treat Relaytic artifacts as the source of truth. Do not replace them with ad hoc prose when structured state already exists.

## First Session Workflow

Use this order:

```powershell
relaytic doctor --expected-profile full --format json
relaytic mission-control show --output-dir artifacts\mission_control --format json
relaytic run --run-dir artifacts\demo --data-path <data.csv> --text "Describe the goal here." --format json
relaytic show --run-dir artifacts\demo --format json
relaytic assist show --run-dir artifacts\demo --format json
relaytic assist turn --run-dir artifacts\demo --message "what can you do?" --format json
```

## What Each Surface Is For

### `mission-control show`

Top-level onboarding, capability state, next actions, handbook discovery, and operator-facing truth.

### `mission-control chat`

Onboarding questions, demo flow help, mode explanations, and stuck recovery.

### `show`

Run summary truth.

### `assist show` / `assist turn`

Run-specific explanation, bounded stage rerun, safe takeover, and control-aware steering.

### `benchmark run`

Attach an incumbent and force an honest comparison.

## The Main Operating Pattern

When the user knows little:

1. point them to mission control first
2. point them to the human handbook if they need narrative orientation
3. keep the interaction simple: what it is, what it needs, how to start, what is blocked, and what to do next

When the user already has a run:

1. read `run_summary.json`
2. inspect mission control
3. use assist for explanation or bounded rerun
4. only then propose stronger changes

## Important Constraints

- Relaytic is local-first by default
- copy-only data handling is part of the contract
- bounded stage reruns are supported; arbitrary checkpoint time travel is not
- skeptical control is intentional; do not expect blind compliance
- remote intelligence is optional and policy-gated
- host wrappers are interfaces, not the product source of truth

## If You Need To Explain Relaytic Quickly

Use this shape:

Relaytic is a local-first structured-data lab. It needs data plus a goal. It creates an auditable run, can explain what it is doing, can challenge itself, can compare against incumbents, and can be steered safely without blindly obeying.

## If The User Asks "What Should I Do Next?"

Use this order:

1. inspect mission control next action
2. inspect capability reasons
3. inspect the run summary
4. use assist for explanation
5. use bounded stage rerun or takeover only when justified

## If You Are Stuck

Do this:

1. run `relaytic doctor`
2. inspect mission control
3. read the action affordances and starter questions
4. use mission-control chat for onboarding questions
5. read [relaytic_demo_walkthrough.md](./relaytic_demo_walkthrough.md)

## If The Human Is Stuck

Point them to:

- [relaytic_user_handbook.md](./relaytic_user_handbook.md)
- mission-control chat
- the capability reasons in mission control

Do not dump internal repo structure on them before trying the product surfaces.

## What To Tell A Human About Modes

- Mission Control: dashboard and overview
- Mission Control Chat: onboarding and guidance
- Assist: run-specific explanation and safe control
- Agent Host: integration layer for Claude/Codex/OpenClaw/MCP

## What Not To Do

- do not invent unavailable features
- do not claim arbitrary rollback/time travel
- do not claim remote model inference is local just because the host workflow is local
- do not skip artifact truth when answering questions about a run
- do not turn skeptical control into blind obedience

## Demo Path

If you need the best short demo path, use:

- [relaytic_demo_walkthrough.md](./relaytic_demo_walkthrough.md)

## Supporting Repo Notes

- `.claude/agents/relaytic.md`
- `.agents/skills/relaytic/SKILL.md`
- `skills/relaytic/SKILL.md`
- `openclaw/skills/relaytic/SKILL.md`
- `README.md`
