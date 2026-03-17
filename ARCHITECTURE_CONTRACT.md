# Relaytic Architecture Contract

This file freezes the load-bearing contracts that later slices must obey.

## Public Product Surface

- Product name: `Relaytic`
- Descriptor: `The Relay Inference Lab`
- Canonical package: `relaytic`
- Canonical CLI: `relaytic`
- Compatibility package: `corr2surrogate` for import fallback only

New docs, code, examples, and tests must target `relaytic`.

## Package Boundary

Current package rule:

- `src/relaytic/` is canonical
- `src/corr2surrogate/` is a temporary shim that forwards legacy imports

Later slices may remove the shim only after `MIGRATION_MAP.md` and `IMPLEMENTATION_STATUS.md` are updated.

## Control Documents

These files are required and must stay current:

- `ARCHITECTURE_CONTRACT.md`
- `IMPLEMENTATION_STATUS.md`
- `MIGRATION_MAP.md`
- `docs/build_slices/phase_00.md`
- `docs/build_slices/phase_01.md`
- `docs/build_slices/phase_02.md`
- `docs/build_slices/phase_03.md`

## Early Artifact Contract

The first slices must preserve these names:

- `manifest.json`
- `policy_resolved.yaml`
- `lab_mandate.json`
- `work_preferences.json`
- `run_brief.json`
- `data_origin.json`
- `domain_brief.json`
- `task_brief.json`
- `dataset_profile.json`
- `domain_memo.json`
- `objective_hypotheses.json`
- `focus_debate.json`
- `focus_profile.json`
- `optimization_profile.json`
- `feature_strategy_profile.json`
- `plan.json`
- `alternatives.json`
- `hypotheses.json`

## CLI Contract

The public CLI command is `relaytic`.

Minimum guaranteed surfaces at this stage:

- `relaytic --help`
- `relaytic manifest init`
- `relaytic policy resolve`
- `relaytic mandate init`
- `relaytic mandate show`
- `relaytic context init`
- `relaytic context show`
- `relaytic foundation init`
- `relaytic setup-local-llm`
- `relaytic run-agent-session`
- `relaytic run-agent1-analysis`
- `relaytic run-inference`
- `relaytic scan-git-safety`

## Security Contract

- `.env*`, secrets, certs, local private data, and local environments must remain ignored
- Repo-specific environment variables should use the `RELAYTIC_*` prefix
- Legacy `C2S_*` variables may be accepted only as compatibility fallbacks
- No raw secrets may be written into tracked docs, tests, or artifacts

## Migration Rule

Rename work and semantic changes should not be mixed casually. If a slice changes the public boundary, document:

- what moved
- what stays compatible
- what is intentionally broken
- when the shim is expected to disappear
