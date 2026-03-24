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
- a deterministic local route from data to model inside one Relaytic run directory with richer categorical handling, executed missingness-aware feature engineering, bounded interaction features, and split-safe preprocessing reuse at inference time
- broader bounded candidate search within the current Builder family set instead of a single fixed-parameter route
- calibrated classification outputs and uncertainty-bearing regression/classification summaries in inference artifacts
- challenger, ablation, audit, and decision-memo evidence around the first built route
- completion-governor judgment with visible run state and machine-actionable next actions
- lifecycle-governor judgment with explicit keep, recalibrate, retrain, promote, and rollback decisions
- run memory and analog retrieval with visible analog provenance, route priors, challenger priors, and reflection-memory flushes
- a shared local runtime gateway with append-only events, capability-scoped specialists, checkpoints, hook audit, and one coherent control path for CLI and MCP
- structured semantic-task execution with capability-aware context assembly, document grounding, semantic debate/counterposition artifacts, and explicit uncertainty reporting
- routed semantic intelligence with explicit mode selection, local-profile resolution, verifier artifacts, and measurable semantic-proof reporting
- bounded autonomous follow-up loops with challenger queues, recalibration/retrain requests, loop budgets, and champion lineage tracking
- privacy-safe external research retrieval from redacted run signatures with typed source inventory, method-transfer reports, benchmark-reference capture, and explicit external-research audit
- benchmark parity and gap reporting against explicit reference approaches under the same split and metric contract
- validated feedback and outcome learning with explicit intake, trust scoring, reversible effect reports, route-prior updates, and rollback-ready casebook artifacts
- communicative assist surfaces that explain what Relaytic is doing, let humans or external agents jump back to any bounded stage, and let Relaytic take over when the operator stops or is unsure
- concise run summaries for humans and stable summary artifacts for agents
- one-line bootstrap install plus post-install dependency verification
- host-neutral MCP interoperability with checked-in wrappers for Claude, Codex/OpenAI, OpenClaw, and ChatGPT-facing connector guidance
- explicit host activation/discovery state so Relaytic can say which tools can call it immediately and which still need connector registration
- optional local-LLM advisory paths that remain non-required
- deterministic expert-prior reasoning for common structured-data archetypes such as manufacturing quality, fraud risk, anomaly monitoring, churn, demand, and pricing
- end-to-end local routes for regression, binary classification, multiclass classification, and fraud/anomaly-style rare-event classification
- copy-only data handling that stages immutable working copies inside each run directory and avoids persisting original source paths

Slice 10 is now implemented: Relaytic can ingest human, external-agent, runtime, benchmark, and downstream-outcome feedback; validate trustworthiness; emit explicit reversible effect reports; and keep rollback-ready casebook state instead of silently drifting. The next load-bearing implementation step is Slice 10B, where Relaytic makes quality gates, budget posture, and operator/lab profile overlays explicit before the deeper decision-lab work in Slice 10A.

The next frontier upgrades are:

- explicit quality contracts that tell humans and external agents what Relaytic currently means by "good enough"
- explicit budget contracts and budget-consumption reporting that make runtime/search/autonomy limits visible instead of implicit
- bounded operator/lab profiles that shape review posture, benchmark appetite, explanation style, and budget posture without personalizing truth-bearing logic
- decision-world modeling that distinguishes better score from better downstream action
- method compilation that turns research, memory, and operator context into executable challenger and feature plans
- local data-fabric reasoning that can suggest joins, entity histories, and additional local data before wasting search budget
- mission-control surfaces that show branch structure, confidence, and change attribution to humans and external agents
- an optional late-stage representation engine for large unlabeled local corpora, streams, and entity histories, with JEPA-style latent predictive models as one promising backend family

## Design Principles

- local-first by default
- deterministic at the core
- autonomous but steerable
- artifact-rich and auditable
- specialist-driven rather than single-planner
- security-conscious by default

## Current Data Formats

Relaytic's current public ingestion contract is file-snapshot based.

Supported input formats today:

- `.csv`
- `.tsv`
- `.xlsx`
- `.xls`
- `.parquet`
- `.pq`
- `.feather`
- `.json`
- `.jsonl`
- `.ndjson`

Current native local source modes:

- snapshot files in the formats above
- append-only local stream files materialized into bounded micro-batch snapshots
  Supported stream file formats: `.csv`, `.tsv`, `.jsonl`, `.ndjson`
- local lakehouse-style sources materialized into bounded run-local snapshots
  Supported lakehouse sources: partitioned dataset directories and local DuckDB files

What is still not a first-class public ingestion surface:

- remote Kafka or message-bus consumers
- remote warehouse connectors
- remote cloud lakehouse tables

Relaytic stays local-first: even stream and lakehouse sources are first materialized into an immutable run-local snapshot before modeling.

## Data Safety

Relaytic should operate on copies of input data, not the original source files.

Current behavior:

- `relaytic run` stages immutable working copies under `data_copies/` inside the run directory
- `relaytic predict` stages separate inference copies under the same run directory
- `relaytic source inspect` explains how Relaytic will treat a source before touching it
- `relaytic source materialize` lets humans and agents explicitly stage a stream or lakehouse source into a run-local snapshot
- `data_copy_manifest.json` records staged-copy provenance, purpose, and hashes
- original absolute source paths are not persisted in the staged-data manifest
- Relaytic does not write back to the original dataset path during normal run or inference flows

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

Relaytic does not currently rely on hidden custom pretraining to make its specialists useful. The near-term path to stronger expertise is: better deterministic priors, better run memory, better reference-doc grounding, privacy-safe external research retrieval from redacted run signatures, stronger benchmark doctrine, validated feedback and outcome learning, explicit decision-world modeling, method compilation, richer data-fabric reasoning, and optional local-LLM amplification for the semantically hard parts.

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
relaytic runtime show --run-dir path/to/existing_run
relaytic memory show --run-dir path/to/existing_run
relaytic benchmark show --run-dir path/to/existing_run
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

That command now carries the run through intake, investigation, cross-run memory retrieval, planning, execution, challenger pressure, ablation checks, semantic debate, audit, privacy-safe research retrieval, benchmark comparison, completion, lifecycle review, bounded autonomous follow-up, and summary materialization.

You can also inspect or stage richer local sources first:

```bash
relaytic source inspect --source-path path/to/data.parquet
relaytic source inspect --source-path path/to/append_only_events.jsonl --source-type stream
relaytic source inspect --source-path path/to/local_lakehouse --source-type lakehouse
relaytic source materialize --source-path path/to/local_lakehouse --source-type lakehouse --run-dir artifacts/run_demo
```

Then inspect or reuse the run:

```bash
relaytic show --run-dir artifacts/run_your_dataset_...
relaytic runtime show --run-dir artifacts/run_your_dataset_...
relaytic runtime events --run-dir artifacts/run_your_dataset_...
relaytic memory show --run-dir artifacts/run_your_dataset_...
relaytic intelligence show --run-dir artifacts/run_your_dataset_...
relaytic research show --run-dir artifacts/run_your_dataset_...
relaytic research sources --run-dir artifacts/run_your_dataset_...
relaytic benchmark show --run-dir artifacts/run_your_dataset_...
relaytic assist show --run-dir artifacts/run_your_dataset_...
relaytic assist turn --run-dir artifacts/run_your_dataset_... --message "why did you choose this route?"
relaytic status --run-dir artifacts/run_your_dataset_...
relaytic evidence show --run-dir artifacts/run_your_dataset_...
relaytic lifecycle show --run-dir artifacts/run_your_dataset_...
relaytic autonomy show --run-dir artifacts/run_your_dataset_...
relaytic predict --run-dir artifacts/run_your_dataset_... --data-path path/to/data.csv
```

Advanced users and other agents can still use the explicit staged flow:

```bash
relaytic foundation init --run-dir artifacts/run_demo
relaytic intake interpret --run-dir artifacts/run_demo --data-path path/to/data.csv --text "Do everything on your own. Predict off-spec batches early. Do not use post-inspection columns. Laptop CPU only."
relaytic intake questions --run-dir artifacts/run_demo
relaytic investigate --run-dir artifacts/run_demo --data-path path/to/data.csv
relaytic memory retrieve --run-dir artifacts/run_demo --data-path path/to/data.csv
relaytic plan create --run-dir artifacts/run_demo --data-path path/to/data.csv
relaytic plan run --run-dir artifacts/run_demo --data-path path/to/data.csv
relaytic evidence run --run-dir artifacts/run_demo --data-path path/to/data.csv
relaytic intelligence run --run-dir artifacts/run_demo
relaytic research gather --run-dir artifacts/run_demo
relaytic benchmark run --run-dir artifacts/run_demo --data-path path/to/data.csv
relaytic completion review --run-dir artifacts/run_demo
relaytic lifecycle review --run-dir artifacts/run_demo --data-path path/to/data.csv
relaytic autonomy run --run-dir artifacts/run_demo --data-path path/to/data.csv
relaytic assist turn --run-dir artifacts/run_demo --message "go back to research"
relaytic runtime show --run-dir artifacts/run_demo
relaytic runtime events --run-dir artifacts/run_demo --limit 12
relaytic memory show --run-dir artifacts/run_demo
relaytic intelligence show --run-dir artifacts/run_demo
relaytic research show --run-dir artifacts/run_demo
relaytic benchmark show --run-dir artifacts/run_demo
relaytic autonomy show --run-dir artifacts/run_demo
relaytic run-inference --run-dir artifacts/run_demo --data-path path/to/data.csv
```

For a more communicative demo-friendly surface, use:

```bash
relaytic assist show --run-dir artifacts/run_demo
relaytic assist turn --run-dir artifacts/run_demo --message "connect claude or use a local llm"
relaytic assist turn --run-dir artifacts/run_demo --message "i'm not sure, take over"
relaytic assist chat --run-dir artifacts/run_demo
```

That flow produces:

- resolved policy and manifest artifacts
- mandate and context foundation bundles
- intake provenance, semantic mappings, autonomy state, clarification queue, and assumption log
- investigation outputs such as dataset profile, domain memo, objective hypotheses, and focus artifacts
- planning outputs such as `plan.json`, route alternatives, hypotheses, and experiment priorities
- model artifacts such as `model_params.json`, model state, and local checkpoints
- evidence artifacts such as `experiment_registry.json`, `challenger_report.json`, `ablation_report.json`, `audit_report.json`, and `belief_update.json`
- memory artifacts such as `memory_retrieval.json`, `analog_run_candidates.json`, `route_prior_context.json`, `challenger_prior_suggestions.json`, `reflection_memory.json`, and `memory_flush_report.json`
- runtime artifacts such as `lab_event_stream.jsonl`, `hook_execution_log.json`, `run_checkpoint_manifest.json`, `capability_profiles.json`, `data_access_audit.json`, and `context_influence_report.json`
- intelligence artifacts such as `intelligence_mode.json`, `llm_routing_plan.json`, `local_llm_profile.json`, `verifier_report.json`, `semantic_proof_report.json`, `semantic_task_results.json`, `context_assembly_report.json`, `doc_grounding_report.json`, `semantic_debate_report.json`, `semantic_counterposition_pack.json`, and `semantic_uncertainty_report.json`
- benchmark artifacts such as `reference_approach_matrix.json`, `benchmark_gap_report.json`, and `benchmark_parity_report.json`
- completion artifacts such as `completion_decision.json`, `run_state.json`, `stage_timeline.json`, `mandate_evidence_review.json`, `blocking_analysis.json`, and `next_action_queue.json`
- lifecycle artifacts such as `champion_vs_candidate.json`, `recalibration_decision.json`, `retrain_decision.json`, `promotion_decision.json`, and `rollback_decision.json`
- autonomy artifacts such as `autonomy_loop_state.json`, `autonomy_round_report.json`, `challenger_queue.json`, `branch_outcome_matrix.json`, `retrain_run_request.json`, `recalibration_run_request.json`, `champion_lineage.json`, and `loop_budget_report.json`
- operator-facing reports such as `reports/technical_report.md` and `reports/decision_memo.md`
- a machine-readable `run_summary.json`
- a human-readable `reports/summary.md`

## Documentation Map

Public-facing technical docs:

- `ARCHITECTURE.md` for the system overview
- `INTEROPERABILITY.md` for MCP transports, host bundles, and safety rules
- `RUNTIME.md` for the local gateway, event stream, checkpoints, and capability profiles
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

Run the optional official-UCI domain dataset flows:

```bash
$env:RELAYTIC_ENABLE_NETWORK_DATASETS="1"
python -m pytest tests/test_domain_dataset_flows.py -q
```

If you touch packaging, CLI, or security surfaces, also run:

```bash
python scripts/install_relaytic.py --skip-install --expected-profile core
python -m relaytic.ui.cli scan-git-safety
relaytic --help
```

## Compatibility Note

The public package and CLI are `relaytic`. Any remaining legacy import shims are compatibility-only and should not be used in new code, docs, or examples.
