# Migration Map

## Public Naming Migration

- old product name: `Corr2Surrogate`
- new product name: `Relaytic`
- old public package: `corr2surrogate`
- new public package: `relaytic`
- old public CLI: `corr2surrogate`
- new public CLI: `relaytic`

## Compatibility Boundary

Current compatibility promise:

- old Python imports rooted at `corr2surrogate` continue through a temporary shim
- new code and docs must import `relaytic`
- the old CLI command is no longer the public contract

## Environment Variable Migration

Preferred:

- `RELAYTIC_CONFIG_PATH`
- `RELAYTIC_PROVIDER`
- `RELAYTIC_PROFILE`
- `RELAYTIC_MODEL`
- `RELAYTIC_ENDPOINT`
- `RELAYTIC_API_KEY`

Compatibility-only legacy names may still be accepted temporarily:

- `C2S_CONFIG_PATH`
- `C2S_PROVIDER`
- `C2S_PROFILE`
- `C2S_MODEL`
- `C2S_ENDPOINT`
- `C2S_API_KEY`

## Module Mapping

- `src/corr2surrogate/*` -> `src/relaytic/*`
- `corr2surrogate.ui.cli` -> `relaytic.ui.cli`
- `corr2surrogate.security.git_guard` -> `relaytic.security.git_guard`

## Removal Plan

1. Keep the import shim until at least Slice 03 is stable.
2. Remove the shim only after tests and docs no longer depend on legacy imports.
3. Remove legacy `C2S_*` env fallbacks after the new Relaytic env contract is fully adopted.
