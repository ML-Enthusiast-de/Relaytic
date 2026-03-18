# Implementation Status

## Current Slice

- completed: Slice 04 - intake and translation layer
- next recommended slice: Slice 05 - planning and first working route

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

### Slice 03

- added `src/relaytic/investigation/` with typed Slice 03 artifact models, storage helpers, deterministic specialist agents, and optional local-LLM advisory integration
- implemented Scout as a deterministic dataset inspector that emits `dataset_profile.json`
- implemented Scientist as a grounded hypothesis generator that emits `domain_memo.json`
- implemented Focus Council as a structured objective resolver that emits `objective_hypotheses.json`, `focus_debate.json`, `focus_profile.json`, `optimization_profile.json`, and `feature_strategy_profile.json`
- added `relaytic investigate`
- made `relaytic investigate` ensure foundation artifacts exist before writing Slice 03 outputs
- added targeted tests for deterministic investigation, CLI artifact writing, overwrite protection, and local-stub-LLM advisory behavior
- tightened the dependency contract to `pandas>=2.0,<3.0` after `pandas 3.0.1` proved unstable in the current environment

### Slice 04

- added `src/relaytic/intake/` with typed intake artifact models, storage helpers, deterministic translation agents, and optional local-LLM advisory integration
- implemented `StewardAgent` to translate free-form user or agent input into mandate, work-preference, and run-brief updates
- implemented `ContextInterpreterAgent` to translate free-form input plus optional dataset schema into data-origin, domain-brief, and task-brief updates
- added `relaytic intake interpret`
- added `relaytic intake show`
- added `relaytic intake questions`
- made `relaytic intake interpret` ensure the Slice 02 foundation exists before writing Slice 04 artifacts and updating normalized foundation bundles
- added explicit `autonomy_mode.json`, `clarification_queue.json`, and `assumption_log.json` so unanswered non-critical questions become auditable assumptions instead of blockers
- made intake clarification optional by default and allowed explicit operator autonomy signals such as "do everything on your own" to suppress non-critical question noise while preserving the queue
- added targeted tests for deterministic intake translation, autonomous proceed-with-assumptions behavior, CLI artifact writing, overwrite protection, manifest preservation, and local-stub-LLM advisory behavior

## Pending

- Slice 05 - planning and first working route

## Temporary Shims

- `src/corr2surrogate/__init__.py` compatibility import shim
- legacy `C2S_*` environment variable fallback support where still required

## Known Non-Final Areas

- the current runtime still reflects the legacy harness baseline internally
- the artifact contract is only partially implemented beyond manifest, policy, mandate, context, intake, and investigation scaffolding
- README describes the product direction and current baseline, not the full end-state feature set

## Immediate Next Work

Build Slice 05:

- strategist baseline
- first working deterministic tabular route
- metric selection
- split selection
- feature-strategy integration
