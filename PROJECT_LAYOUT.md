# Relaytic Project Layout

This document describes the current repository shape during the Relaytic migration.

## Source Of Truth

For architecture decisions, use:

1. `ARCHITECTURE_CONTRACT.md`
2. `IMPLEMENTATION_STATUS.md`
3. `MIGRATION_MAP.md`
4. `RELAYTIC_BUILD_MASTER.md`
5. `RELAYTIC_SLICING_PLAN.md`

This file is descriptive, not normative.

## Current Layout

```text
Relaytic/
  configs/
    default.yaml
  data/
  artifacts/
  reports/
  models/
  docs/
    build_slices/
  src/
    relaytic/
      artifacts/
      context/
      mandate/
      policies/
    corr2surrogate/  # temporary compatibility shim
  tests/
  README.md
  SECURITY.md
  AGENTS.md
  ARCHITECTURE_CONTRACT.md
  IMPLEMENTATION_STATUS.md
  MIGRATION_MAP.md
  RELAYTIC_VISION_MASTER.md
  RELAYTIC_BUILD_MASTER.md
  RELAYTIC_SLICING_PLAN.md
```

## Package Boundary

- `src/relaytic/` is the canonical product package.
- `src/corr2surrogate/` exists only to keep old imports from crashing during migration.
- New work must target `relaytic`, not `corr2surrogate`.

## Operational Directories

- `configs/` stores checked-in defaults.
- `data/private/` is reserved for local private inputs and must stay ignored.
- `artifacts/`, `reports/`, and `models/` contain generated outputs and must stay ignored except for sentinel files.

## Documentation Standard

Top-level documents should present the repository as:

`Relaytic - The Relay Inference Lab`

They should avoid legacy branding unless they are explicitly describing a tracked compatibility shim or migration step.
