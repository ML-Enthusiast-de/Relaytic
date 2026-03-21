# Relaytic Project Layout

This document describes the current repository structure and ownership boundaries. It is descriptive, not normative.

## Primary Docs

Public-facing docs:

1. `README.md`
2. `ARCHITECTURE.md`
3. `INTEROPERABILITY.md`
4. `RUNTIME.md`
5. `OPEN_SOURCE_STACK.md`
6. `SECURITY.md`

Implementation control docs:

1. `ARCHITECTURE_CONTRACT.md`
2. `IMPLEMENTATION_STATUS.md`
3. `MIGRATION_MAP.md`
4. `RELAYTIC_BUILD_MASTER.md`
5. `RELAYTIC_SLICING_PLAN.md`

## Repository Shape

```text
Relaytic/
  .agents/
    skills/
      relaytic/
  .claude/
    agents/
  .mcp.json
  configs/
    default.yaml
  data/
  artifacts/
  connectors/
    chatgpt/
  openclaw/
    skills/
  reports/
  models/
  docs/
    build_slices/
  skills/
    relaytic/
  scripts/
  src/
    relaytic/
      artifacts/
      context/
      ingestion/
      intake/
      investigation/
      mandate/
      evidence/
      completion/
      lifecycle/
      intelligence/
      memory/
      autonomy/
      interoperability/
      integrations/
      planning/
      policies/
      runs/
      runtime/
    corr2surrogate/  # compatibility shim only
  tests/
  README.md
  ARCHITECTURE.md
  INTEROPERABILITY.md
  SECURITY.md
  AGENTS.md
  ARCHITECTURE_CONTRACT.md
  IMPLEMENTATION_STATUS.md
  MIGRATION_MAP.md
  RELAYTIC_VISION_MASTER.md
  RELAYTIC_BUILD_MASTER.md
  RELAYTIC_SLICING_PLAN.md
```

## Package Ownership

- `src/relaytic/` is the canonical product package
- `src/relaytic/mandate/` owns mandate foundation objects and writers
- `src/relaytic/context/` owns context foundation objects and writers
- `src/relaytic/ingestion/` owns snapshot-file loading and immutable data-copy staging
- `src/relaytic/ingestion/sources.py` owns local source inspection plus stream/lakehouse materialization into immutable run-local snapshots
- `src/relaytic/intake/` owns intake translation and interpretation artifacts
- `src/relaytic/investigation/` owns investigation specialists and focus artifacts
- `src/relaytic/planning/` owns Strategist planning, Builder handoff, and planning artifact storage
- `src/relaytic/evidence/` owns challenger, ablation, audit, leaderboard, and decision-memo artifacts
- `src/relaytic/completion/` owns the completion-governor layer, run-state artifacts, and status synthesis
- `src/relaytic/lifecycle/` owns champion/candidate comparison, recalibration, retraining, promotion, and rollback artifacts
- `src/relaytic/intelligence/` owns semantic-task execution, backend discovery, capability-aware context assembly, document grounding, counterposition packs, and semantic uncertainty artifacts
- `src/relaytic/memory/` owns analog retrieval, route priors, challenger priors, reflection memory, and memory artifact persistence
- `src/relaytic/autonomy/` owns bounded second-pass execution, challenger queues, branch outcomes, loop budgets, retrain/recalibration requests, and champion lineage
- `src/relaytic/interoperability/` owns MCP serving, host-bundle generation, and interoperability self-checks
- `src/relaytic/integrations/` owns optional-library discovery, compatibility self-checks, and adapter-scoped capability inventory
- `src/relaytic/runs/` owns MVP-access summaries, run reports, and top-level run presentation helpers
- `src/relaytic/runtime/` owns the local lab gateway, append-only event stream, hook audit, checkpoints, and capability-profile enforcement
- `src/relaytic/artifacts/` owns manifest helpers
- `src/relaytic/policies/` owns policy loading and resolved-policy writing
- `src/corr2surrogate/` exists only to preserve a narrow temporary compatibility boundary

## Operational Directories

- `configs/` stores checked-in defaults
- `.agents/`, `.claude/`, `openclaw/`, and `connectors/` store checked-in agent-host wrapper surfaces and guidance
- `skills/` stores workspace-local skill mirrors for hosts that auto-discover from the current repository
- `data/private/` is reserved for local private inputs and must remain ignored
- `artifacts/`, `reports/`, and `models/` contain generated outputs and must remain ignored except for sentinel files
- `docs/build_slices/` tracks bounded implementation slices
- `scripts/` stores local bootstrap and support scripts such as `install_relaytic.py`
- `tests/` provides regression coverage for both product and compatibility boundaries

## Current Package Boundaries

- `src/relaytic/research/` owns Slice 09D redacted external research retrieval, method-transfer distillation, benchmark-reference harvesting, and research-audit persistence
- `src/relaytic/assist/` owns Slice 09E communicative assistance, stage-navigation planning, takeover coordination, and connection-guide persistence

## Naming Rule

All new public-facing work must use `Relaytic`, `relaytic`, and `relaytic`. Legacy names should appear only when documenting an explicit compatibility boundary.
