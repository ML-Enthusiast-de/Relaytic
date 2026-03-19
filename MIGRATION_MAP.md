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

### Slice 07

- introduced the canonical package boundary `src/relaytic/completion/`
- introduced the public commands `relaytic status` and `relaytic completion review`
- expanded the artifact boundary to include `completion_decision.json`, `run_state.json`, `stage_timeline.json`, `mandate_evidence_review.json`, `blocking_analysis.json`, and `next_action_queue.json`
- upgraded the MVP access shell so `relaytic run` and `relaytic show` now surface an explicit governed run state rather than stopping at provisional evidence only

### Slice 08

- introduced the canonical package boundary `src/relaytic/lifecycle/`
- introduced the public commands `relaytic lifecycle review` and `relaytic lifecycle show`
- expanded the artifact boundary to include `champion_vs_candidate.json`, `recalibration_decision.json`, `retrain_decision.json`, `promotion_decision.json`, and `rollback_decision.json`
- upgraded the MVP access shell so `relaytic run` and `relaytic show` now surface lifecycle posture by default instead of stopping at completion-only state

### Slice 08A

- introduced the canonical package boundary `src/relaytic/interoperability/`
- introduced the public commands `relaytic interoperability show`, `relaytic interoperability self-check`, `relaytic interoperability export`, and `relaytic interoperability serve-mcp`
- introduced checked-in host bundle surfaces at `.mcp.json`, `.claude/agents/relaytic.md`, `.agents/skills/relaytic/SKILL.md`, `openclaw/skills/relaytic/SKILL.md`, and `connectors/chatgpt/README.md`
- introduced a Relaytic-owned MCP tool contract so host wrappers stay thin and local-first rather than becoming new product centers

### Slice 08B

- expanded the existing interoperability boundary to include explicit host activation/discovery metadata
- introduced the checked-in workspace discovery mirror `skills/relaytic/SKILL.md` for OpenClaw-style hosts
- upgraded `relaytic interoperability show` so host readiness is explicit instead of implied

### Post-Slice 07 Cross-Cutting Additions

- introduced the canonical package boundary `src/relaytic/integrations/`
- introduced the public command `relaytic integrations show`
- introduced the public command `relaytic integrations self-check`
- introduced the public command `relaytic doctor`
- introduced the one-line bootstrap script `scripts/install_relaytic.py`
- wired adapter-scoped third-party surfaces for intake validation and evidence diagnostics/challengers without broadening the legacy compatibility surface
- kept third-party capabilities optional and adapter-scoped rather than broadening the core or legacy compatibility surface

## Reserved Next Boundaries

These boundaries are frozen for the next major slices so implementation can proceed without reopening naming or ownership questions.

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
