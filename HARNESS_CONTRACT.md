# Relaytic Harness Baseline Contract

This file captures the current pre-transformation harness baseline that still exists inside the repository while Relaytic is being built out.

It is not the long-term architecture contract. For forward-looking implementation rules, use `ARCHITECTURE_CONTRACT.md`.

## Purpose

The baseline harness remains useful for:

- deterministic CLI smoke checks
- local LLM setup validation
- compatibility during the package rename
- regression coverage while larger Relaytic slices are implemented

## Current Baseline Modules

The baseline harness currently lives under:

- `src/relaytic/orchestration/workflow.py`
- `src/relaytic/orchestration/handoff_contract.py`
- `src/relaytic/agents/agent1_analyst.py`
- `src/relaytic/agents/agent2_modeler.py`
- `src/relaytic/analytics/`
- `src/relaytic/modeling/`
- `src/relaytic/persistence/`
- `src/relaytic/orchestration/tool_registry.py`
- `src/relaytic/orchestration/agent_loop.py`
- `src/relaytic/orchestration/runtime_policy.py`
- `src/relaytic/orchestration/default_tools.py`
- `src/relaytic/orchestration/harness_runner.py`

Prompt assets currently live under:

- `src/relaytic/agents/prompts/analyst_system.txt`
- `src/relaytic/agents/prompts/modeler_system.txt`

## Migration Rule

This harness is transitional. It should be used to preserve repo coherence while Relaytic slices replace it with:

- mandate-aware execution
- context-aware planning
- Focus Council outputs
- standardized run artifacts
- completion judgment
- lifecycle decisions

Any new work that touches the baseline harness should keep the public surface branded as Relaytic and should update `MIGRATION_MAP.md` if a compatibility promise changes.
