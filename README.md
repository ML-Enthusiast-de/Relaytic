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
- completion-governor judgment with visible run state and machine-actionable next actions
- lifecycle-governor judgment with explicit keep, recalibrate, retrain, promote, and rollback decisions
- concise run summaries for humans and stable summary artifacts for agents
- one-line bootstrap install plus post-install dependency verification
- host-neutral MCP interoperability with checked-in wrappers for Claude, Codex/OpenAI, OpenClaw, and ChatGPT-facing connector guidance
- explicit host activation/discovery state so Relaytic can say which tools can call it immediately and which still need connector registration
- optional local-LLM advisory paths that remain non-required
- deterministic expert-prior reasoning for common structured-data archetypes such as manufacturing quality, fraud risk, anomaly monitoring, churn, demand, and pricing
- end-to-end local routes for regression, binary classification, multiclass classification, and fraud/anomaly-style rare-event classification

The next load-bearing implementation step is Slice 09A: run memory and analog retrieval.

## Design Principles

- local-first by default
- deterministic at the core
- autonomous but steerable
- artifact-rich and auditable
- specialist-driven rather than single-planner
- security-conscious by default

## How The Agents Know Things

Relaytic's specialists do not rely on hidden domain pretraining as the main product mechanism.

They get their working knowledge from:

- the dataset and deterministic profiling outputs
- deterministic expert-prior libraries that map dataset/context evidence into domain archetypes and task priors
- mandate and context artifacts
- policy constraints
- persisted planning, execution, evidence, and completion artifacts
- optional uploaded notes or structured operator context
- optional local-LLM advisory help for bounded semantic interpretation and synthesis

That means the default product contract is still deterministic, local-first, and auditable. Local LLMs can improve interpretation and summaries, but they are not required for the core run loop.

Relaytic does not currently rely on hidden custom pretraining to make its specialists useful. The near-term path to stronger expertise is: better deterministic priors, better run memory, better reference-doc grounding, and optional local-LLM amplification for the semantically hard parts.

## Reuse Mature OSS

Relaytic should reuse strong open source libraries for mature primitives instead of rebuilding them in-core. The system should stay novel in judgment, autonomy, artifact design, and multi-stage decision-making, not in reimplementing standard baselines or validators.

Check the locally available optional stack with:

```bash
relaytic integrations show
relaytic integrations show --format json
relaytic integrations self-check
relaytic integrations self-check --format json
```

The current wired surfaces are:

- Pandera-backed intake schema validation
- statsmodels-backed regression residual diagnostics in evidence audit
- imbalanced-learn rare-event challenger support
- PyOD anomaly challenger support, runtime-guarded on Windows unless explicitly overridden
- scikit-learn-backed public dataset fixtures and compatibility checks

The current adoption policy is documented in `OPEN_SOURCE_STACK.md`.

## Frontier Models

Relaytic still keeps frontier models in the plan, but only as optional policy-gated amplifiers.

The default product path remains local-first and deterministic. Frontier or external high-end models may be used later for bounded reasoning, semantic interpretation, challenger design, synthesis, or route expansion when policy explicitly allows them. They are not the baseline dependency and they do not replace Relaytic's own artifact, policy, or judgment layers.

## Quick Start

Preferred one-line bootstrap:

```bash
python scripts/install_relaytic.py
```

That command installs the full local Relaytic stack in editable mode and immediately runs `relaytic doctor` to verify the environment.

Manual install:

```bash
python -m pip install --upgrade pip
python -m pip install -e ".[full]"
relaytic doctor --expected-profile full
```

Check the public CLI surface:

```bash
relaytic --help
python -m relaytic.ui.cli --help
```

Check the interoperability surface:

```bash
relaytic interoperability show
relaytic interoperability self-check --live
```

Run the repository leak scan before commits:

```bash
python -m relaytic.ui.cli scan-git-safety
```

## Interoperability

Relaytic can now be reached from common local agent hosts through a Relaytic-owned MCP layer instead of host-specific forks.

Inspect the current interoperability inventory:

```bash
relaytic interoperability show
relaytic interoperability show --format json
relaytic interoperability self-check
relaytic interoperability self-check --live --format json
```

Serve local MCP over stdio for subprocess-based hosts:

```bash
relaytic interoperability serve-mcp --transport stdio
```

Serve local MCP over loopback HTTP for connector-style clients:

```bash
relaytic interoperability serve-mcp --transport streamable-http --host 127.0.0.1 --port 8000 --mount-path /mcp
```

Export fresh host bundles into another directory:

```bash
relaytic interoperability export --host all --output-dir artifacts/interop_export --force
```

The checked-in host surfaces are:

- `.mcp.json` for Claude Code style project-local MCP
- `.claude/agents/relaytic.md` for Claude agent guidance
- `.agents/skills/relaytic/SKILL.md` for Codex/OpenAI skills
- `skills/relaytic/SKILL.md` for workspace-level OpenClaw discovery
- `openclaw/skills/relaytic/SKILL.md` for OpenClaw
- `connectors/chatgpt/README.md` for ChatGPT connector guidance

Current activation truth:

- Claude Code can discover Relaytic from this repository, then asks for one MCP approval
- Codex/OpenAI local skill environments can discover the checked-in Relaytic skill from this repository
- OpenClaw can discover Relaytic from the repository workspace through `skills/relaytic/SKILL.md`
- ChatGPT still requires a registered connector against a public HTTPS `/mcp` endpoint; repository files alone are not enough

See `INTEROPERABILITY.md` for the transport model, safety rules, and verification flow.

## Example Workflow

The primary MVP surface is now a single end-to-end run command:

```bash
relaytic run --data-path path/to/data.csv --text "Do everything on your own. Predict off-spec batches early. Do not use post-inspection columns. Laptop CPU only."
```

That command now carries the run through intake, investigation, planning, execution, challenger pressure, ablation checks, audit, and summary materialization.

Then inspect or reuse the run:

```bash
relaytic show --run-dir artifacts/run_your_dataset_...
relaytic status --run-dir artifacts/run_your_dataset_...
relaytic evidence show --run-dir artifacts/run_your_dataset_...
relaytic lifecycle show --run-dir artifacts/run_your_dataset_...
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
relaytic completion review --run-dir artifacts/run_demo
relaytic lifecycle review --run-dir artifacts/run_demo --data-path path/to/data.csv
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
- completion artifacts such as `completion_decision.json`, `run_state.json`, `stage_timeline.json`, `mandate_evidence_review.json`, `blocking_analysis.json`, and `next_action_queue.json`
- lifecycle artifacts such as `champion_vs_candidate.json`, `recalibration_decision.json`, `retrain_decision.json`, `promotion_decision.json`, and `rollback_decision.json`
- operator-facing reports such as `reports/technical_report.md` and `reports/decision_memo.md`
- a machine-readable `run_summary.json`
- a human-readable `reports/summary.md`

## Documentation Map

Public-facing technical docs:

- `ARCHITECTURE.md` for the system overview
- `INTEROPERABILITY.md` for MCP transports, host bundles, and safety rules
- `OPEN_SOURCE_STACK.md` for the mature-library adoption policy
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
python scripts/install_relaytic.py --skip-install --expected-profile core
python -m relaytic.ui.cli scan-git-safety
relaytic --help
```

## Compatibility Note

The public package and CLI are `relaytic`. Any remaining legacy import shims are compatibility-only and should not be used in new code, docs, or examples.
