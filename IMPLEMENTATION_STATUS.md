# Implementation Status

## Current Slice

- completed: Slice 02 - mandate and context foundation
- next recommended slice: Slice 03 - Focus Council and investigation baseline

## Completed

### Slice 00

- public package renamed to `relaytic`
- public CLI renamed to `relaytic`
- top-level docs rewritten to Relaytic branding
- architecture, status, migration, security, and repo agent docs added
- temporary `corr2surrogate` import compatibility boundary established
- security baseline made explicit

### Slice 01

- added `relaytic.artifacts.manifests` with manifest creation and writing helpers
- added `relaytic.policies.loader` with resolved-policy loading and YAML materialization
- added `relaytic manifest init`
- added `relaytic policy resolve`
- added targeted tests for manifest scaffolding, policy scaffolding, CLI shells, config precedence, and local stub LLM integration

### Slice 02

- added stable mandate models and artifact writers under `src/relaytic/mandate/`
- added stable context models and artifact writers under `src/relaytic/context/`
- normalized legacy config into a canonical resolved Relaytic policy shell
- added `relaytic mandate init`
- added `relaytic mandate show`
- added `relaytic context init`
- added `relaytic context show`
- added `relaytic foundation init`
- added tests for mandate/context objects, CLI flows, overwrite protection, policy reuse, and local-stub-LLM consumption of foundation artifacts

## Pending

- Slice 03 - Focus Council and investigation baseline

## Temporary Shims

- `src/corr2surrogate/__init__.py` compatibility import shim
- legacy `C2S_*` environment variable fallback support where still required

## Known Non-Final Areas

- the current runtime still reflects the legacy harness baseline internally
- the artifact contract is only partially implemented beyond manifest, policy, mandate, and context scaffolding
- README describes the product direction and current baseline, not the full end-state feature set

## Immediate Next Work

Build Slice 03:

- scout baseline
- scientist baseline
- focus council baseline
- dataset profile
- domain memo
- objective artifacts
