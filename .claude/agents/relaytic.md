---
name: relaytic
description: Use Relaytic for local-first structured-data and AML investigation, model routing, governed workspace review, continuation, and inference.
---

# Relaytic

Use Relaytic for local-first structured-data modeling, review, and inference.

## Prefer this order

1. Use the project-local Relaytic MCP server when the `relaytic_*` tools are available.
2. Fall back to the `relaytic` CLI if MCP is unavailable.
3. Keep runs local-first and deterministic unless the user explicitly asks for stronger semantic help.

## Read First

- Start with `docs/handbooks/relaytic_agent_handbook.md` when you are new to the Relaytic surface or need the shortest command-first operating guide.

## Fast paths

- End-to-end: `relaytic run --data-path <data.csv> --text "Do everything on your own. Predict <target>."`
- Inspect: `relaytic show --run-dir <run_dir>`
- Guidance: `relaytic guide --run-dir <run_dir> --format json`
- Status: `relaytic status --run-dir <run_dir>`
- Workspace: `relaytic workspace show --run-dir <run_dir> --format json`
- Predict: `relaytic predict --run-dir <run_dir> --data-path <new_data.csv>`
- Lifecycle: `relaytic lifecycle show --run-dir <run_dir>`

## Guardrails

- Do not invent targets or forbidden columns when the dataset or artifacts can answer the question.
- Prefer Relaytic's structured artifacts over narrative summaries when handing results to other tools or agents.
- Treat `workspace_state.json`, `result_contract.json`, and
  `next_run_plan.json` as canonical continuity contracts.
- Keep secrets out of prompts, saved notes, and exported configs.
- For remote MCP exposure, require trusted HTTPS/auth infrastructure instead of exposing a local development server directly.
