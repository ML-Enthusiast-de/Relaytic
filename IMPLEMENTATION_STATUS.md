# Implementation Status

This document tracks the operational state of the repository. It is an implementation control file, not product marketing copy.

## Current Baseline

- completed slices: 00 through 04
- next recommended slice: 05, planning and first working route
- current public package: `relaytic`
- current public CLI: `relaytic`

## Operational Capabilities

The repository currently supports:

- policy resolution and manifest writing
- mandate and context foundation artifacts
- free-form intake translation with provenance and semantic mapping
- autonomous proceed-with-assumptions behavior for non-critical intake ambiguity
- investigation artifacts from Scout, Scientist, and Focus Council
- optional local-LLM advisory support without making local LLMs a hard requirement

## Implemented Slices

### Slice 00

- locked public naming on `Relaytic`, `relaytic`, and `relaytic`
- established security, migration, and implementation control documents
- introduced the temporary `corr2surrogate` compatibility boundary

### Slice 01

- added manifest helpers under `src/relaytic/artifacts/`
- added canonical policy loading and resolved-policy writing under `src/relaytic/policies/`
- added `relaytic manifest init`
- added `relaytic policy resolve`
- added targeted scaffold and CLI tests

### Slice 02

- added stable mandate models and writers under `src/relaytic/mandate/`
- added stable context models and writers under `src/relaytic/context/`
- added `relaytic mandate init` and `relaytic mandate show`
- added `relaytic context init` and `relaytic context show`
- added `relaytic foundation init`
- added targeted foundation and CLI tests

### Slice 03

- added `src/relaytic/investigation/` with typed investigation artifacts and storage helpers
- implemented Scout for dataset profiling
- implemented Scientist for grounded domain and objective hypotheses
- implemented Focus Council for early objective resolution
- added `relaytic investigate`
- added targeted investigation, CLI, and local-stub-LLM tests

### Slice 04

- added `src/relaytic/intake/` with typed intake artifacts and storage helpers
- implemented `StewardAgent` for mandate, work-preference, and run-brief translation
- implemented `ContextInterpreterAgent` for data-origin, domain, and task translation
- added `relaytic intake interpret`
- added `relaytic intake show`
- added `relaytic intake questions`
- added `autonomy_mode.json`, `clarification_queue.json`, and `assumption_log.json`
- made intake clarification optional by default and auditable through explicit assumptions
- added targeted intake, CLI, and local-stub-LLM tests

## Compatibility Boundary

The remaining compatibility surface is intentionally narrow:

- `src/corr2surrogate/__init__.py` forwards legacy imports
- legacy `C2S_*` environment variable fallbacks may still be accepted where required

New code and docs must target `relaytic` and `RELAYTIC_*`.

## Known Gaps

The repository is not yet at the final product state. The main remaining gaps are:

- Slice 05 planning and the first deterministic data-to-model route are not yet implemented
- experimentation, challenger, reporting, completion judgment, and lifecycle slices are still pending
- some deeper runtime surfaces still retain compatibility-era internals while newer product layers are being built on top

## Immediate Next Work

Slice 05 should land:

- Strategist baseline
- `plan.json`
- `alternatives.json`
- `hypotheses.json`
- first deterministic tabular route
- metric and split selection
- feature-strategy integration
