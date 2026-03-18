# Migration Map

This file tracks explicit compatibility boundaries while the repository continues moving toward the final Relaytic product surface.

## Public Naming

- product name: `Relaytic`
- public package: `relaytic`
- public CLI: `relaytic`

Legacy `Corr2Surrogate` naming exists only where compatibility is still being preserved deliberately.

## Compatibility Surface

Current temporary compatibility promises:

- legacy Python imports rooted at `corr2surrogate` continue through a narrow shim
- legacy `C2S_*` environment variables may still be accepted as fallbacks in some runtime paths

These are compatibility mechanisms, not active public product surfaces.

## Preferred Environment Variables

Use:

- `RELAYTIC_CONFIG_PATH`
- `RELAYTIC_PROVIDER`
- `RELAYTIC_PROFILE`
- `RELAYTIC_MODEL`
- `RELAYTIC_ENDPOINT`
- `RELAYTIC_API_KEY`

Avoid introducing new references to:

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

## Boundary Additions By Slice

### Slice 03

- introduced the canonical package boundary `src/relaytic/investigation/`
- introduced the public command `relaytic investigate`
- tightened compatibility wrappers so repo-local forwarding is explicit rather than accidental

### Slice 04

- introduced the canonical package boundary `src/relaytic/intake/`
- introduced the public commands `relaytic intake interpret`, `relaytic intake show`, and `relaytic intake questions`
- expanded the artifact boundary to include autonomous intake artifacts such as `autonomy_mode.json`, `clarification_queue.json`, and `assumption_log.json`

### Slice 05

- introduced the canonical package boundary `src/relaytic/planning/`
- introduced the public commands `relaytic plan create`, `relaytic plan run`, and `relaytic plan show`
- expanded the artifact boundary to include `plan.json`, `alternatives.json`, `hypotheses.json`, `experiment_priority_report.json`, and `marginal_value_of_next_experiment.json`
- established the first supported Builder-handoff boundary from planning artifacts into a same-run deterministic model build
- preserved existing compatibility promises without expanding the legacy `corr2surrogate` surface

### Slice 05A

- introduced the canonical package boundary `src/relaytic/runs/`
- introduced the public commands `relaytic run`, `relaytic show`, and `relaytic predict`
- expanded the artifact boundary to include `run_summary.json` and `reports/summary.md`
- standardized nested manifest artifact paths to POSIX-style relative paths for more stable cross-platform agent consumption

### Slice 06

- introduced the canonical package boundary `src/relaytic/evidence/`
- introduced the public commands `relaytic evidence run` and `relaytic evidence show`
- expanded the artifact boundary to include `experiment_registry.json`, `challenger_report.json`, `ablation_report.json`, `audit_report.json`, `belief_update.json`, `leaderboard.csv`, `reports/technical_report.md`, and `reports/decision_memo.md`
- upgraded the MVP access shell so `relaytic run` now drives the evidence layer by default while preserving lower-level specialist surfaces

## Reserved Next Boundaries

These boundaries are frozen for the next major slices so implementation can proceed without reopening naming or ownership questions.

### Slice 07

- reserve the canonical package boundary `src/relaytic/completion/`
- reserve the future public commands `relaytic status` and `relaytic completion review`
- reserve the artifact boundary for `completion_decision.json`, `run_state.json`, `stage_timeline.json`, `mandate_evidence_review.json`, `blocking_analysis.json`, and `next_action_queue.json`

### Slice 09A

- reserve the canonical package boundary `src/relaytic/memory/`
- reserve the future public command `relaytic memory retrieve`
- reserve the artifact boundary for `memory_retrieval.json`, `analog_run_candidates.json`, `route_prior_context.json`, and `challenger_prior_suggestions.json`

## Removal Criteria

The remaining compatibility layer can be removed when all of the following are true:

1. tests no longer depend on `corr2surrogate` imports
2. docs and examples no longer mention legacy package paths except historical notes
3. runtime paths no longer require `C2S_*` fallbacks
4. the next stable slices no longer rely on compatibility forwarding
