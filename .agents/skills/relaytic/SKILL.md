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

## Read First

- If you are new to this repo, read `docs/handbooks/relaytic_agent_handbook.md` before using the CLI. It is the terse agent-oriented map of commands, artifacts, and supporting contracts.

## Core commands

- `relaytic run --data-path <data.csv> --text "<intent>"`
- `relaytic guide --format json`
- `relaytic guide --run-dir <run_dir> --format json`
- `relaytic guide ask --run-dir <run_dir> --message "<question>" --format json`
- `relaytic guide export-context --run-dir <run_dir> --audience external-llm --format json`
- `relaytic show --run-dir <run_dir> --format json`
- `relaytic status --run-dir <run_dir> --format json`
- `relaytic aml temporal --run-dir <run_dir> --format json`
- `relaytic aml environment --run-dir <run_dir> --format json`
- `relaytic assist show --run-dir <run_dir> --format json`
- `relaytic assist turn --run-dir <run_dir> --message "<message>" --format json`
- `relaytic predict --run-dir <run_dir> --data-path <new_data.csv> --format json`
- `relaytic doctor --expected-profile full --format json`

## Safety rules

- Keep Relaytic local-first by default.
- Do not expose `/mcp` publicly without trusted HTTPS and auth controls.
- Treat `workspace_state.json`, `result_contract.json`, and
  `next_run_plan.json` as the canonical continuity and post-run contracts.
  `run_summary.json`, handoff reports, mission control, and lifecycle reports
  are reader-specific views over the same local artifact state.
- Use `relaytic guide` first when the user or agent is unsure where the run is,
  which artifact matters, what action is safe, or what context can be handed
  to another LLM.
- Use the assist surface when a human or external agent needs explanations, stage navigation, or safe takeover rather than inventing ad hoc chat behavior.
