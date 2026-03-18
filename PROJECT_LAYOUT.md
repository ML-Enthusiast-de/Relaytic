# Relaytic Project Layout

This document describes the current repository structure and ownership boundaries. It is descriptive, not normative.

## Primary Docs

Public-facing docs:

1. `README.md`
2. `ARCHITECTURE.md`
3. `SECURITY.md`

Implementation control docs:

1. `ARCHITECTURE_CONTRACT.md`
2. `IMPLEMENTATION_STATUS.md`
3. `MIGRATION_MAP.md`
4. `RELAYTIC_BUILD_MASTER.md`
5. `RELAYTIC_SLICING_PLAN.md`

## Repository Shape

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
      intake/
      investigation/
      mandate/
      policies/
    corr2surrogate/  # compatibility shim only
  tests/
  README.md
  ARCHITECTURE.md
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
- `src/relaytic/intake/` owns intake translation and interpretation artifacts
- `src/relaytic/investigation/` owns investigation specialists and focus artifacts
- `src/relaytic/artifacts/` owns manifest helpers
- `src/relaytic/policies/` owns policy loading and resolved-policy writing
- `src/corr2surrogate/` exists only to preserve a narrow temporary compatibility boundary

## Operational Directories

- `configs/` stores checked-in defaults
- `data/private/` is reserved for local private inputs and must remain ignored
- `artifacts/`, `reports/`, and `models/` contain generated outputs and must remain ignored except for sentinel files
- `docs/build_slices/` tracks bounded implementation slices
- `tests/` provides regression coverage for both product and compatibility boundaries

## Naming Rule

All new public-facing work must use `Relaytic`, `relaytic`, and `relaytic`. Legacy names should appear only when documenting an explicit compatibility boundary.
