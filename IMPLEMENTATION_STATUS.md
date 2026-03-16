# Implementation Status

## Current Slice

- completed: Slice 00 - normalization and contract freeze
- next recommended slice: Slice 01 - contracts and scaffolding

## Completed

### Slice 00

- public package renamed to `relaytic`
- public CLI renamed to `relaytic`
- top-level docs rewritten to Relaytic branding
- architecture, status, migration, security, and repo agent docs added
- temporary `corr2surrogate` import compatibility boundary established
- security baseline made explicit

## Pending

- Slice 01 - contracts and scaffolding
- Slice 02 - mandate and context foundation
- Slice 03 - Focus Council and investigation baseline

## Temporary Shims

- `src/corr2surrogate/__init__.py` compatibility import shim
- legacy `C2S_*` environment variable fallback support where still required

## Known Non-Final Areas

- the current runtime still reflects the legacy harness baseline internally
- the artifact contract is only partially implemented
- README describes the product direction and current baseline, not the full end-state feature set

## Immediate Next Work

Build Slice 01:

- package scaffolding hardening
- manifest helper
- policy loader shell
- status-tracked CLI baseline
