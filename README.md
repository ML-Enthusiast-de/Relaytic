# Relaytic - The Relay Inference Lab

Relaytic is a local-first inference engineering system for structured data. It investigates datasets before it commits to modeling assumptions, preserves user intent through policy and mandate layers, interprets human and external-agent input into structured run context, keeps deterministic execution as the floor, proceeds autonomously when non-critical clarification goes unanswered, and exposes its judgment through inspectable artifacts and local tool surfaces.

This repository is in an active transformation from a legacy prototype into the Relaytic product. The public package, CLI, docs, and migration controls now use Relaytic naming. Remaining legacy internals are tracked explicitly and are being removed slice by slice.

## What Relaytic Is

Relaytic is not an AutoML wrapper. It is a local-first inference engineering system that investigates data, forms competing hypotheses, runs challenger science, quantifies uncertainty, preserves mandate-aware user intent, translates free-form human or agent input into structured operating context, recommends missing data, and exposes its judgment as reusable local tools.

The intended product is:

- local-first by default
- deterministic at the core
- autonomous but steerable
- multi-specialist rather than single-planner
- artifact-rich and auditable
- lifecycle-aware beyond one-off model fitting

## Repository State

The source of truth for the transformation is:

1. `RELAYTIC_VISION_MASTER.md`
2. `RELAYTIC_BUILD_MASTER.md`
3. `ARCHITECTURE_CONTRACT.md`
4. `IMPLEMENTATION_STATUS.md`
5. `MIGRATION_MAP.md`
6. `RELAYTIC_SLICING_PLAN.md`

Current normalization status:

- public package name: `relaytic`
- public CLI name: `relaytic`
- compatibility import shim: `corr2surrogate` (temporary)
- top-level build and migration docs: present
- security baseline: enforced through `.gitignore` and leak scan tooling

## Quick Start

Create an environment and install the editable package:

```bash
python -m pip install --upgrade pip
python -m pip install -e ".[dev,stats,viz]"
```

Smoke-check the public CLI:

```bash
relaytic --help
python -m relaytic.ui.cli --help
```

Run the repository leak scan before commits:

```bash
python -m relaytic.ui.cli scan-git-safety
```

## Current CLI Baseline

The current CLI surface is still the legacy harness baseline, now exposed through the Relaytic name while the larger architecture is being built out in slices.

Examples:

```bash
relaytic policy resolve --output artifacts/run_demo/policy_resolved.yaml
relaytic manifest init --run-dir artifacts/run_demo --entry policy_resolved.yaml
relaytic foundation init --run-dir artifacts/run_demo
relaytic intake interpret --run-dir artifacts/run_demo --text "Do everything on your own. Predict off-spec batches early. Do not use post-inspection columns. Laptop CPU only."
relaytic intake questions --run-dir artifacts/run_demo
relaytic investigate --run-dir artifacts/run_demo --data-path data/private/run1.csv
relaytic mandate init --run-dir artifacts/run_demo --objective best_robust_pareto_front
relaytic context init --run-dir artifacts/run_demo --problem-statement "Predict off-spec batches early."
relaytic setup-local-llm --provider llama_cpp
relaytic run-agent-session --agent analyst
relaytic run-agent1-analysis --data-path data/private/run1.csv
relaytic run-inference --run-dir artifacts/<run_dir> --data-path data/private/run1.csv
```

## Security Baseline

This repository treats security hygiene as non-negotiable:

- do not commit `.env` files, virtual environments, private datasets, generated reports, or local model artifacts
- do not commit API keys, tokens, passwords, certificates, or machine-specific paths
- do not persist raw secrets into artifacts or docs
- run `python -m relaytic.ui.cli scan-git-safety` before opening a PR

Relevant files:

- `SECURITY.md`
- `.gitignore`
- `src/relaytic/security/git_guard.py`

## Build Discipline

Relaytic is being built in bounded slices. Completed load-bearing slices are:

1. Slice 01 - contracts and scaffolding
2. Slice 02 - mandate and context foundation
3. Slice 03 - Focus Council and investigation baseline
4. Slice 04 - intake and translation layer

The next recommended build step is:

5. Slice 05 - planning and first working route

The completed normalization slice established:

- Relaytic naming across public surfaces
- migration control documents
- repo-local agent instructions
- a tracked compatibility boundary for the old package name
- a formal security baseline for envs, secrets, and local artifacts

## Current Layout

```text
src/relaytic/          Main runtime package and current implementation baseline
src/corr2surrogate/    Temporary compatibility import shim
src/relaytic/mandate/  Mandate foundation objects and writers
src/relaytic/context/  Context foundation objects and writers
src/relaytic/intake/   Slice 04 intake translation and interpretation artifacts
src/relaytic/investigation/ Slice 03 specialist agents and investigation artifacts
src/relaytic/policies/ Canonical resolved policy helpers
src/relaytic/artifacts/ Manifest helpers
configs/               Runtime configuration
docs/build_slices/     Incremental implementation slices
artifacts/             Generated run artifacts (ignored except sentinels)
reports/               Generated reports (ignored except sentinels)
tests/                 Automated regression coverage
```

## Professional Standard

The repo should read like a product, not a scratchpad. That means:

- one public name
- one public CLI
- explicit contracts
- explicit migration notes
- explicit assumptions when Relaytic proceeds autonomously
- no leaked secrets
- no checked-in local environments
- no ambiguous legacy branding in new work

## Development

Run tests:

```bash
python -m pytest -q
```

If you touch packaging, CLI, or security surfaces, also run:

```bash
python -m relaytic.ui.cli scan-git-safety
relaytic --help
```
