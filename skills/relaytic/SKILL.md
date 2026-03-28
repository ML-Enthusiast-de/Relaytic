---
name: relaytic
description: Structured-data investigation, modeling, evidence review, lifecycle decisions, and prediction through Relaytic.
---

# Relaytic

Use Relaytic when the task involves structured datasets, model generation, or reviewing an existing Relaytic run.

## Default workflow

1. Run `relaytic run --data-path <data.csv> --text "<intent>"`.
2. Inspect with `relaytic show --run-dir <run_dir>`.
3. Use `relaytic status --run-dir <run_dir>` for the governed state.
4. Use `relaytic predict --run-dir <run_dir> --data-path <new_data.csv>` for inference.

## Read First

- Start with `docs/handbooks/relaytic_agent_handbook.md` when you are new to the Relaytic surface or need the shortest command-first operating guide.

## Notes

- Relaytic is autonomous by default and will proceed with explicit assumptions when non-critical answers are missing.
- Prefer Relaytic JSON outputs when passing results to other tools or agents.
- Keep remote exposure behind trusted HTTPS/auth layers when using the MCP server outside local development.
