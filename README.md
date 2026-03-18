# Relaytic - The Relay Inference Lab

Relaytic is a local-first inference engineering system for structured data. It turns datasets, operator intent, and optional local semantic help into auditable modeling decisions, structured artifacts, and reusable local tooling.

Relaytic is designed around a deterministic floor, specialist-agent reasoning, explicit policy and mandate handling, and artifact-first execution. The system should be able to continue autonomously when non-critical ambiguity remains, while still making its assumptions inspectable.

## Current Product Baseline

The repository already supports a working early product baseline:

- installable `relaytic` package and CLI
- one-shot `relaytic run` orchestration for a first usable MVP surface
- resolved policy writing and manifest creation
- mandate and context foundation artifacts
- free-form intake translation from human or external-agent input
- optional clarification queues with explicit fallback assumptions
- investigation specialists that profile datasets and resolve early modeling focus
- Strategist planning artifacts with a concrete Builder handoff
- a first deterministic local route from data to model inside one Relaytic run directory
- challenger, ablation, audit, and decision-memo evidence around the first built route
- concise run summaries for humans and stable summary artifacts for agents
- optional local-LLM advisory paths that remain non-required

The next load-bearing implementation step is Slice 07: completion judgment and visible workflow state.

## Design Principles

- local-first by default
- deterministic at the core
- autonomous but steerable
- artifact-rich and auditable
- specialist-driven rather than single-planner
- security-conscious by default

## Quick Start

Install the package in editable mode:

```bash
python -m pip install --upgrade pip
python -m pip install -e ".[dev,stats,viz]"
```

Check the public CLI surface:

```bash
relaytic --help
python -m relaytic.ui.cli --help
```

Run the repository leak scan before commits:

```bash
python -m relaytic.ui.cli scan-git-safety
```

## Example Workflow

The primary MVP surface is now a single end-to-end run command:

```bash
relaytic run --data-path path/to/data.csv --text "Do everything on your own. Predict off-spec batches early. Do not use post-inspection columns. Laptop CPU only."
```

That command now carries the run through intake, investigation, planning, execution, challenger pressure, ablation checks, audit, and summary materialization.

Then inspect or reuse the run:

```bash
relaytic show --run-dir artifacts/run_your_dataset_...
relaytic evidence show --run-dir artifacts/run_your_dataset_...
relaytic predict --run-dir artifacts/run_your_dataset_... --data-path path/to/data.csv
```

Advanced users and other agents can still use the explicit staged flow:

```bash
relaytic foundation init --run-dir artifacts/run_demo
relaytic intake interpret --run-dir artifacts/run_demo --data-path path/to/data.csv --text "Do everything on your own. Predict off-spec batches early. Do not use post-inspection columns. Laptop CPU only."
relaytic intake questions --run-dir artifacts/run_demo
relaytic investigate --run-dir artifacts/run_demo --data-path path/to/data.csv
relaytic plan create --run-dir artifacts/run_demo --data-path path/to/data.csv
relaytic plan run --run-dir artifacts/run_demo --data-path path/to/data.csv
relaytic evidence run --run-dir artifacts/run_demo --data-path path/to/data.csv
relaytic run-inference --run-dir artifacts/run_demo --data-path path/to/data.csv
```

That flow produces:

- resolved policy and manifest artifacts
- mandate and context foundation bundles
- intake provenance, semantic mappings, autonomy state, clarification queue, and assumption log
- investigation outputs such as dataset profile, domain memo, objective hypotheses, and focus artifacts
- planning outputs such as `plan.json`, route alternatives, hypotheses, and experiment priorities
- model artifacts such as `model_params.json`, model state, and local checkpoints
- evidence artifacts such as `experiment_registry.json`, `challenger_report.json`, `ablation_report.json`, `audit_report.json`, and `belief_update.json`
- operator-facing reports such as `reports/technical_report.md` and `reports/decision_memo.md`
- a machine-readable `run_summary.json`
- a human-readable `reports/summary.md`

## Documentation Map

Public-facing technical docs:

- `ARCHITECTURE.md` for the system overview
- `SECURITY.md` for security and repo hygiene rules
- `PROJECT_LAYOUT.md` for repository structure and ownership boundaries

Implementation control docs:

1. `RELAYTIC_VISION_MASTER.md`
2. `RELAYTIC_BUILD_MASTER.md`
3. `ARCHITECTURE_CONTRACT.md`
4. `IMPLEMENTATION_STATUS.md`
5. `MIGRATION_MAP.md`
6. `RELAYTIC_SLICING_PLAN.md`

The control docs exist to keep implementation rigorous and incremental. They are intentionally more operational than the public overview.

## Development

Run the test suite:

```bash
python -m pytest -q
```

If you touch packaging, CLI, or security surfaces, also run:

```bash
python -m relaytic.ui.cli scan-git-safety
relaytic --help
```

## Compatibility Note

The public package and CLI are `relaytic`. Any remaining legacy import shims are compatibility-only and should not be used in new code, docs, or examples.
