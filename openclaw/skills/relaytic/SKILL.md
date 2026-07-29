---
name: relaytic
description: Local-first structured-data investigation, AML evaluation, modeling, evidence review, lifecycle decisions, and prediction through Relaytic.
---

# Relaytic

Use Relaytic when the task involves structured datasets, AML evaluation, model
generation, or review and continuation of an existing Relaytic workspace.

## Default workflow

1. Run `relaytic run --data-path <data.csv> --text "<intent>"`.
2. Inspect with `relaytic show --run-dir <run_dir>`.
3. Use `relaytic guide --run-dir <run_dir> --format json` when the next action
   or relevant artifact is unclear.
4. Use `relaytic status --run-dir <run_dir>` for the governed state.
5. Use `relaytic predict --run-dir <run_dir> --data-path <new_data.csv>` for inference.

## Read First

- Start with `docs/handbooks/relaytic_agent_handbook.md` when you are new to the Relaytic surface or need the shortest command-first operating guide.

## Notes

- Relaytic is autonomous by default and will proceed with explicit assumptions when non-critical answers are missing.
- Prefer Relaytic JSON outputs when passing results to other tools or agents.
- Treat `workspace_state.json`, `result_contract.json`, and
  `next_run_plan.json` as the canonical continuity and post-run contracts.
- Keep remote exposure behind trusted HTTPS/auth layers when using the MCP server outside local development.
