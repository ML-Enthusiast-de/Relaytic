---
name: relaytic
description: Use Relaytic for local-first structured-data investigation, model planning, execution, lifecycle review, and inference.
---

# Relaytic

Relaytic is the local inference-engineering system in this workspace.

## When to use

- The user wants to model a structured dataset.
- A previous Relaytic run needs to be inspected, challenged, reviewed, or used for prediction.
- A downstream agent needs stable JSON artifacts instead of ad hoc prose.

## Preferred execution order

1. If Relaytic MCP tools are available, call them directly.
2. Otherwise use the `relaytic` CLI.
3. Prefer `relaytic run` for the main path unless the user explicitly asks for lower-level phase control.

## Core commands

- `relaytic run --data-path <data.csv> --text "<intent>"`
- `relaytic show --run-dir <run_dir> --format json`
- `relaytic status --run-dir <run_dir> --format json`
- `relaytic predict --run-dir <run_dir> --data-path <new_data.csv> --format json`
- `relaytic doctor --expected-profile full --format json`

## Safety rules

- Keep Relaytic local-first by default.
- Do not expose `/mcp` publicly without trusted HTTPS and auth controls.
- Treat `run_summary.json`, `completion_decision.json`, and lifecycle artifacts as the machine-facing source of truth.
