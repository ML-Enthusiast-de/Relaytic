# Implementation Status

This document tracks the operational state of the repository. It is an implementation control file, not product marketing copy.

## Current Baseline

- completed slices: 00 through 06
- next recommended slice: 07, completion judgment and visible workflow state
- next reserved follow-on after 07: 09A, run memory and analog retrieval
- current public package: `relaytic`
- current public CLI: `relaytic`

## Operational Capabilities

The repository currently supports:

- policy resolution and manifest writing
- mandate and context foundation artifacts
- free-form intake translation with provenance and semantic mapping
- autonomous proceed-with-assumptions behavior for non-critical intake ambiguity
- investigation artifacts from Scout, Scientist, and Focus Council
- Strategist planning artifacts with a real Builder handoff
- a first deterministic local data-to-model route via `relaytic plan run`
- a first human-friendly and agent-friendly MVP shell via `relaytic run`, `relaytic show`, `relaytic predict`, and `relaytic evidence`
- persisted `run_summary.json` plus `reports/summary.md` for concise run understanding
- challenger, ablation, audit, leaderboard, and decision-memo evidence around the first Builder route
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

### Slice 05

- added `src/relaytic/planning/` with typed planning artifacts, storage helpers, and optional local advisory
- implemented `StrategistAgent` to turn investigation outputs into a concrete Builder handoff
- added `plan.json`, `alternatives.json`, `hypotheses.json`, `experiment_priority_report.json`, and `marginal_value_of_next_experiment.json`
- added `relaytic plan create`, `relaytic plan run`, and `relaytic plan show`
- connected the first deterministic Builder execution route into the same Relaytic run directory
- made planning robust against over-aggressive heuristic exclusions by distinguishing hard guardrails from soft feature-risk signals
- added targeted planning, CLI, end-to-end inference, and local-stub-LLM tests

### Slice 05A

- added `src/relaytic/runs/` for MVP-access summaries and human-readable run reports
- added `relaytic run` as a one-shot intake -> investigate -> plan -> execute surface
- added `relaytic show` to materialize and render concise run summaries
- added `relaytic predict` as the accessible inference surface for built runs
- added `run_summary.json` and `reports/summary.md`
- standardized nested manifest artifact paths to POSIX-style relative paths for easier agent consumption
- added targeted MVP-access CLI tests

### Slice 06

- added `src/relaytic/evidence/` with typed challenger, ablation, audit, and belief-update artifacts plus storage helpers
- implemented a bounded challenger branch against the selected Builder route
- implemented bounded feature-drop ablations against the selected champion family
- implemented a provisional audit pass that combines challenger evidence, ablation evidence, and inference diagnostics
- added `experiment_registry.json`, `challenger_report.json`, `ablation_report.json`, `audit_report.json`, `belief_update.json`, `leaderboard.csv`, `reports/technical_report.md`, and `reports/decision_memo.md`
- added `relaytic evidence run` and `relaytic evidence show`
- upgraded `relaytic run` so the MVP flow now includes Slice 06 evidence pressure by default
- extended `run_summary.json` and `reports/summary.md` so humans and agents can see the provisional recommendation and evidence posture
- added targeted Slice 06 agent, CLI, and local-stub-LLM tests

## Compatibility Boundary

The remaining compatibility surface is intentionally narrow:

- `src/corr2surrogate/__init__.py` forwards legacy imports
- legacy `C2S_*` environment variable fallbacks may still be accepted where required

New code and docs must target `relaytic` and `RELAYTIC_*`.

## Known Gaps

The repository is not yet at the final product state. The main remaining gaps are:

- the current challenger layer is real but still narrow; it does not yet prove broad challenger science
- the current evidence layer does not yet fuse mandate, context, investigation, and evidence into a final machine-actionable governor decision
- completion judgment, lifecycle decisions, and memory-guided route improvement are still pending
- benchmark-separated proof of strength under constrained/operator-heavy settings is still pending
- some deeper runtime surfaces still retain compatibility-era internals while newer product layers are being built on top

## Immediate Next Work

Slice 07 should land:

- Completion Judge as Inference Governor
- visible workflow state for humans and external agents
- explicit mandate-vs-evidence review
- explicit blocking-layer diagnosis
- machine-actionable next-action queue
- explicit continue/stop/recalibrate/retrain/benchmark/collect-more-evidence style outputs

After Slice 07, the next high-leverage follow-on should include:

- Slice 09A run memory and analog retrieval
- Slice 11 benchmark-separated proof under constrained settings
