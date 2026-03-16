# Relaytic Agent Notes

This repository is built incrementally. Read in this order before implementing a new slice:

1. `RELAYTIC_VISION_MASTER.md`
2. `RELAYTIC_BUILD_MASTER.md`
3. `ARCHITECTURE_CONTRACT.md`
4. `IMPLEMENTATION_STATUS.md`
5. `MIGRATION_MAP.md`
6. `RELAYTIC_SLICING_PLAN.md`

## Repo Rules

- Public name: `Relaytic`
- Public package: `relaytic`
- Public CLI: `relaytic`
- Legacy `corr2surrogate` references are compatibility-only and must not expand
- No `.env` files, local virtual environments, tokens, API keys, machine paths, or private data may be committed
- New work must update `IMPLEMENTATION_STATUS.md`
- Boundary changes must update `MIGRATION_MAP.md`
- Large changes must land in bounded slices, not repo-wide rewrites

## Product Standard

Every visible surface should read like professional software:

- consistent naming
- explicit contracts
- auditable behavior
- local-first defaults
- no secret leakage
- no stale prototype language in public docs
