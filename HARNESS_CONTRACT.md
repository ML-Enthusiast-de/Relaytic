# Relaytic Legacy Harness Contract

This file documents the early two-role harness that remains in the repository
for compatibility and regression coverage. It is not the current Relaytic
agent architecture.

For the current specialist, runtime, workspace, AML, and release contracts, use
`ARCHITECTURE_CONTRACT.md` and `ARCHITECTURE.md`.

## Purpose

The retained harness remains useful for:

- deterministic CLI smoke checks
- local LLM setup validation
- compatibility across the completed package migration
- regression coverage for early orchestration paths

## Retained Modules

The retained harness lives under:

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

Retained prompt assets live under:

- `src/relaytic/agents/prompts/analyst_system.txt`
- `src/relaytic/agents/prompts/modeler_system.txt`

## Migration Rule

The main Relaytic pipeline has replaced this harness with:

- mandate-aware execution
- context-aware planning
- Focus Council outputs
- standardized run artifacts
- completion judgment
- lifecycle decisions

New product behavior must not expand this legacy harness. Changes should be
limited to compatibility, security, or regression maintenance and must update
`MIGRATION_MAP.md` if a compatibility promise changes.
