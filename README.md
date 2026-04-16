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
- imported incumbent challenge support so Relaytic can reevaluate a trusted local model, ruleset/scorecard, or prediction file and issue an honest beat-target contract instead of only generic parity language
- validated feedback and outcome learning with explicit intake, trust scoring, reversible effect reports, route-prior updates, and rollback-ready casebook artifacts
- decision-lab review with explicit decision-world models, controller policies, value-of-more-data reasoning, local source-graph/join analysis, and compiled challenger/feature/benchmark templates
- communicative assist surfaces that explain what Relaytic is doing, let humans or external agents jump back to any bounded stage, and let Relaytic take over when the operator stops or is unsure
- concise run summaries for humans and stable summary artifacts for agents
- one-line Windows and macOS/Linux bootstrap wrappers plus post-install dependency verification
- a thin mission-control surface via `relaytic mission-control show` and `relaytic mission-control launch`, backed by shared run-summary, control, benchmark, decision, onboarding, and launch artifacts
- a clearer mission-control and assist surface that always exposes current modes, capabilities, safe next actions, bounded stage reruns, and starter questions instead of requiring users or external agents to guess the interaction model
- guided onboarding and live terminal mission-control chat through `relaytic mission-control chat` and `relaytic mission-control launch --interactive`, with explicit explanations of what Relaytic is, what it needs first, why capabilities need setup, and how the dashboard differs from terminal chat
- role-specific handbooks surfaced directly from mission control and chat, so human operators are pointed to a narrative `docs/handbooks/relaytic_user_handbook.md` while external agents and host wrappers are pointed to the command-first `docs/handbooks/relaytic_agent_handbook.md`
- demo-grade onboarding through an explicit walkthrough, clearer mode education, and stuck-recovery guidance surfaced directly from mission control, chat, and `docs/handbooks/relaytic_demo_walkthrough.md`
- adaptive human onboarding through mission-control chat, with visible captured onboarding state, direct dataset-path handling, explicit objective-family routing for quick analysis-first versus full governed-run requests, confirmation before the first run, and bounded local semantic extraction for messy first-contact messages
- optional install-to-launch onboarding through `.\scripts\bootstrap.ps1 -Profile full -LaunchControlCenter` on Windows, `bash ./scripts/bootstrap.sh --profile full --launch-control-center` on macOS/Linux, or `python scripts/install_relaytic.py --launch-control-center` when you already control the Python environment
- full-profile bootstrap now attempts to provision a lightweight CPU-safe local onboarding model so first-contact chat can recover messy human input without making LLMs part of the truth-bearing execution path
- differentiated post-run handoff through `relaytic handoff show` and `relaytic handoff focus`, with separate user and agent result reports, explicit next-run options, and persisted next-run focus
- durable local learnings through `relaytic learnings show` and `relaytic learnings reset`, with cross-run learnings markdown/JSON state, per-run learnings snapshots, and memory-visible workspace priors
- explicit workspace continuity through `relaytic workspace show` and `relaytic workspace continue`, with shared workspace state, lineage, focus history, workspace memory policy, machine-stable result contracts, confidence posture, belief-revision triggers, and an explicit next-run plan
- explicit search-controller review through `relaytic search review` and `relaytic search show`, with value-of-search scoring, widened versus pruned branch traces, bounded HPO depth, execution-profile selection, checkpoint posture, and proof that Relaytic can stop search when more search is low value
- guarded dojo review through `relaytic dojo review`, `relaytic dojo show`, and `relaytic dojo rollback`, with quarantined self-improvement proposals, benchmark/quality/control gates, promotion ledgers, rollback-ready state, and mission-control visibility
- explicit lab pulse review through `relaytic pulse review` and `relaytic pulse show`, with bounded skip reporting, rowless innovation watch, challenge watchlists, safe queued follow-up, memory compaction reports, and mission-control visibility
- first-class trace review through `relaytic trace show` and `relaytic trace replay`, with canonical specialist/tool/intervention/branch traces, deterministic claim scorecards, replayable decision reports, and direct runtime-span capture from the shared gateway
- agent/security evaluation through `relaytic evals run` and `relaytic evals show`, with protocol-conformance reports, host-surface matrices, adversarial steering coverage, and explicit open-finding reporting
- explicit event-bus review through `relaytic events show`, with a typed event schema, subscription registry, hook registry, dispatch projections, and one projection-only view over the canonical runtime stream
- explicit permission review through `relaytic permissions show`, `relaytic permissions check`, and `relaytic permissions decide`, with visible `review`, `plan`, `safe_execute`, and `bounded_autonomy` modes, a tool-permission matrix, an approval-policy report, an append-only decision log, and a machine-readable session capability contract
- explicit daemon review through `relaytic daemon review`, `relaytic daemon show`, `relaytic daemon run-job`, and `relaytic daemon resume-job`, with visible background-job registries, approval-aware execution, resumable checkpoints, stale-job reporting, search-resume plans, memory-maintenance queues, and workspace-coherent background continuity
- explicit artifact-reuse review through `relaytic runtime reuse`, with dependency graphs, freshness contracts, recompute plans, cache indexes, and invalidation reports that explain what Relaytic can safely reuse before it spends more compute
- a professional mission-control surface through `relaytic mission-control show` and `relaytic mission-control launch`, with branch DAGs, confidence posture, trace replay state, change attribution, approval timelines, background jobs, permission cards, release-health posture, demo-pack readiness, human-factors evaluation, and onboarding-success reporting
- host-neutral MCP interoperability with checked-in wrappers for Claude, Codex/OpenAI, OpenClaw, and ChatGPT-facing connector guidance
- explicit host activation/discovery state so Relaytic can say which tools can call it immediately and which still need connector registration
- optional local-LLM advisory paths that remain non-required
- deterministic expert-prior reasoning for common structured-data archetypes such as manufacturing quality, fraud risk, anomaly monitoring, churn, demand, and pricing
- end-to-end local routes for regression, binary classification, multiclass classification, and fraud/anomaly-style rare-event classification
- copy-only data handling that stages immutable working copies inside each run directory and avoids persisting original source paths

Slices 10, 10B, 10C, 10A, 11A, 11B, 11C, 11D, 11E, 11F, 11G, 12, 12A, 12B, 12C, 12D, 13, 13A, 13B, 13C, 14, 14A, 15, 15A, 15B, 15C, 15D, 15E, 15F, 15G, 15H, 15I, 15J, 15K, and 15L are now implemented: Relaytic can ingest human, external-agent, runtime, benchmark, and downstream-outcome feedback; validate trustworthiness; emit explicit reversible effect reports; make quality gates and budget posture explicit; challenge human or external-agent steering through typed intervention contracts, override decisions, replayable checkpoints, and causal steering memory; turn the resulting run state into a visible decision-world model with controller policy, value-of-more-data reasoning, source-graph/join analysis, compiled challenger or feature hypotheses, and now explicit feasibility, deployability, action-boundary, and counterfactual reasoning; pressure the run against imported incumbent models, rulesets, and prediction files under the same local contract; surface the current operator truth through one coherent mission-control layer plus a one-command install-and-launch path; make that surface legible through explicit modes, capabilities, action affordances, bounded stage navigation, starter questions, guided onboarding, live terminal chat, role-specific handbooks for humans and agents, a recruiter-safe demo walkthrough, explicit stuck-recovery guidance, adaptive onboarding capture, a lightweight local semantic helper for messy first-contact human input, branch DAGs, confidence posture, trace replay state, change attribution, approval timelines, background jobs, release-health posture, demo-pack readiness, and onboarding-success reporting; end completed runs with differentiated human and agent result reports plus explicit next-run options; retain durable local learnings that can be inspected or reset deliberately; turn those per-run handoffs into a shared workspace continuity layer with lineage, machine-stable result contracts, confidence posture, belief-revision triggers, and explicit same-data/add-data/new-dataset iteration planning; run guarded dojo review with quarantined self-improvement proposals, benchmark/quality/control gates, promotion ledgers, and rollback-ready state; run a bounded lab pulse that can skip honestly, surface rowless innovation leads, queue one safe follow-up, and pin memory for later retrieval without silent drift; write canonical trace truth with deterministic competing-claim adjudication plus protocol-conformance and runtime-security evaluation artifacts that stay visible in mission control and MCP instead of living in debug logs; run an explicit search controller that scores the value of more search, widens or prunes bounded branches, selects HPO depth and execution strategy, and can recommend stopping search in favor of adding data or starting over; run a release-safety gate that scans built bundles or the tracked workspace, writes attestation artifacts, detects machine paths and source maps, and feeds release posture back into `relaytic doctor`; expose one canonical event bus plus one visible permission model so CLI, MCP, mission control, and later daemon or remote surfaces can subscribe to the same runtime truth and the same explicit authority contract; run a bounded background daemon layer that keeps search campaigns, memory maintenance, pulse follow-up, and resumable checkpoints visible, approval-aware, and auditable instead of burying long-running work in hidden sessions; explain why Relaytic did or did not choose a route, model, rerun, or continuation posture using the same local-first feasibility and workspace truth that drives the run; expose a read-mostly remote supervision layer so humans and external agents can inspect pending approvals, apply remote approval decisions, and hand off supervision without creating a second source of truth; create canonical task-profile, target-semantics, metric, and benchmark-vs-deploy artifacts so planning, benchmark review, run summary, and assist explain the same problem contract while temporal benchmark scaffolding exists in code and tests instead of only on the roadmap; route architecture choice through explicit registry, router, fit, ablation, readiness, eligibility, probe, and categorical-strategy artifacts while Relaytic can genuinely train histogram-gradient boosting, extra-trees, CatBoost, XGBoost, and LightGBM families as first-class candidates when they are available, keep TabPFN in the live small-data specialist set when the task fits, and fall back cleanly when adapters are absent; run bounded seeded HPO loops with warm starts and threshold tuning; emit paper-grade benchmark manifests, ranked tables, ablation matrices, rerun-variance reports, temporal benchmark posture, and explicit claim boundaries that separate competitiveness from deployment readiness; materialize dependency graphs, freshness contracts, recompute plans, cache indexes, and invalidation reports so Relaytic can reuse safe upstream artifacts instead of rerunning heavy review work reflexively; turn research-imported architecture ideas into governed candidates with provenance, shadow-trial scorecards, quarantine state, promotion-readiness reports, and human-readable `why not this imported family yet?` explanations; carry one canonical optimization-objective contract, split-diagnostics report, temporal-fold-health report, metric-materialization audit, and benchmark-truth precheck so Relaytic can block unsafe benchmark ranking instead of pretending broken evaluation conditions are trustworthy; run staged portfolio search with explicit probe, race, finalist, and post-fit budgets plus visible pruning reasons and stop reasons instead of one shallow evenly spread search loop; detect real ordered temporal structure, preserve future events across blocked temporal splits when possible, build richer lag/delta/rolling/seasonal feature ladders, compare honest ordinary-versus-lagged baselines, and keep sequence candidates shadow-only until they beat a strong lagged baseline; treat calibration strategy selection, threshold search, review-budget optimization, abstention posture, and operating-point explanations as first-class decision-quality work instead of thin post-processing; and now harden benchmark truth through trace-identity conformance, eval-surface parity, dataset-leakage audits, benchmark-truth audits, release-gate reporting, and explicit safe-to-cite-publicly claim posture.

The next frontier upgrades are:

The next recommended build is **Slice 15M**, because the current rerun proved Relaytic is stronger but still not done with competitiveness work: multiclass and rare-event specialization still need help, temporal classification benchmark recovery is not finished, and we should add explicit benchmark-generalization guards before the academy so we do not accidentally optimize Relaytic around one repeatedly inspected dev pack.

The initial model-competitiveness path through **Slice 15F** is now landed, and the first performance-recovery foundation slice is now landed too:

- Slice 15F research-imported architecture candidates with replay and shadow trials
- Slice 15G objective contracts, split correctness, and metric-truth alignment

The full required performance-recovery path is now landed:

- Slice 15L benchmark truth hardening and paper-claim gates

The broader **Relaytic Academy** then starts at **Slice 16A**, after Slice 15M closes the remaining specialization and benchmark-generalization gap rather than learning new capabilities on top of a still-limited performance ceiling.

After the academy track and the optional representation-engine bet, the roadmap now ends with **Slice 18**, a deliberate consolidation/remediation slice that removes legacy compatibility surfaces, misleading duplicate structure, oversized modules, and stale prototype residue so the finished repo reads like one intentional product rather than a long-lived construction site.

The normative product-contract pack that now governs the shipped workspace layer and its future follow-ons lives in [workspace_lifecycle.md](docs/specs/workspace_lifecycle.md), [result_contract_schema.md](docs/specs/result_contract_schema.md), [governed_learnings_schema.md](docs/specs/governed_learnings_schema.md), [model_competitiveness_contract.md](docs/specs/model_competitiveness_contract.md), [performance_recovery_contract.md](docs/specs/performance_recovery_contract.md), [temporal_benchmark_pack.md](docs/specs/temporal_benchmark_pack.md), [capability_academy_contract.md](docs/specs/capability_academy_contract.md), [mission_control_contract.md](docs/specs/mission_control_contract.md), [handoff_result_migration.md](docs/specs/handoff_result_migration.md), [learnings_migration_contract.md](docs/specs/learnings_migration_contract.md), [external_agent_continuation_contract.md](docs/specs/external_agent_continuation_contract.md), [mission_control_flows.md](docs/specs/mission_control_flows.md), [test_and_proof_matrix.md](docs/specs/test_and_proof_matrix.md), and [flagship_demo_pack.md](docs/specs/flagship_demo_pack.md).

- machine-stable result contracts with confidence posture and belief-revision triggers so humans, agents, CLI, MCP, and later richer UI shells can all read the same conclusion differently without drifting
- governed learnings with source, confidence, reaffirmation, invalidation, reset, and optional expiry semantics
- an iteration planner that can choose whether the next move should stay on the same data, add data, or start over before deeper search spends more compute
- an evented runtime and visible permission model so every later background, remote, or approval-based feature is built on one typed event bus and one explicit authority contract
- richer daemon orchestration that goes beyond the shipped Slice 13C background continuity layer into remote supervision, tighter feasibility coupling, and deeper long-horizon campaign control
- a stronger governed-learnings upgrade that migrates the shipped workspace learnings into typed, confidence-bearing, reaffirmable, invalidatable, and optionally expirable records
- richer long-term memory with retention, compaction, pinning, and replay rules so specialists do not repeatedly forget the same lesson
- a stronger search/HPO controller that goes beyond the shipped Slice 13 bounded search controller into deeper portfolio ecology, better stop-search proofs, and tighter daemon or resume integration
- a performance-recovery track that fixes objective drift, strengthens first-class family coverage, deepens portfolio search with serious budgets, restores temporal competitiveness, improves calibration and decision quality, and blocks unsafe benchmark claims before academy work begins
- richer remote transports, notification freshness, and connector-aware supervision flows on top of the shipped remote-supervision surface
- academy-aware operating surfaces that turn the shipped canonical trace and scorecards into polished replay, promotion, and change-attribution experiences
- broader protocol-conformance harnesses that prove CLI, MCP, mission control, and later richer UI shells stay aligned on the same run truth as the surface area grows
- packaging, release, and long-session regression packs that test the product the way a real frontier operator runtime gets used rather than only as a fast CLI
- flagship demo packs with explicit scorecards so Relaytic can be judged by repeatable proof cases rather than ad hoc walkthroughs
- human-supervision and onboarding-success evaluation so first-time operators can be shown to succeed without repo literacy
- deeper academy and remote-operating surfaces that build on the shipped Slice 15 control-center foundation to show capability growth, supervision history, and change attribution to humans and external agents
- a post-Slice-15 capability-academy track that can discover, shadow-test, promote, demote, and retire new tools and non-core specialists through replayable proof instead of ad hoc growth
- a later optional representation engine for large unlabeled local corpora, streams, and entity histories, with JEPA-style latent predictive models as one promising backend family

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

Windows PowerShell:

```powershell
.\scripts\bootstrap.ps1 -Profile full -LaunchControlCenter
```

macOS/Linux:

```bash
bash ./scripts/bootstrap.sh --profile full --launch-control-center
```

Those wrappers create or reuse a repo-local `.venv`, upgrade `pip`, install Relaytic in editable mode, run `relaytic doctor`, and on the full profile attempt to provision Relaytic's lightweight local onboarding helper for more forgiving first-contact chat.

If you already control the active Python interpreter, you can still call the installer directly:

```bash
python scripts/install_relaytic.py --profile full --launch-control-center
```

If you are new after install:

- human operators should start with `docs/handbooks/relaytic_user_handbook.md`
- external agents and host wrappers should start with `docs/handbooks/relaytic_agent_handbook.md`
- the shortest recruiter-safe demo path is in `docs/handbooks/relaytic_demo_walkthrough.md`
- mission control can point you to both through `relaytic mission-control show`, `relaytic mission-control chat`, or the `/handbook` chat shortcut

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
relaytic handoff show --run-dir path/to/existing_run
relaytic learnings show --run-dir path/to/existing_run
relaytic benchmark show --run-dir path/to/existing_run
relaytic decision show --run-dir path/to/existing_run
relaytic dojo show --run-dir path/to/existing_run
```

Run the repository leak scan before commits:

```bash
python -m relaytic.ui.cli scan-git-safety
```

Imported incumbent model files deserve one extra safety note:

- Relaytic blocks `.pkl` and `.joblib` incumbent model deserialization by default because those formats execute local pickle/joblib payloads.
- Prefer prediction files or JSON rulesets when sharing incumbents across trust boundaries.
- Only use `relaytic benchmark run --trust-incumbent-model ...` when you explicitly trust the local file.

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

The current one-run lab surface also includes explicit decision review:

```bash
relaytic decision review --run-dir path/to/existing_run
relaytic decision show --run-dir path/to/existing_run
relaytic dojo review --run-dir path/to/existing_run
relaytic dojo show --run-dir path/to/existing_run
```

Roll back one promoted dojo proposal explicitly:

```bash
relaytic dojo rollback --run-dir path/to/existing_run --proposal-id dojo_proposal_0001
```

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
relaytic profiles show --run-dir artifacts/run_your_dataset_...
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
relaytic benchmark run --run-dir artifacts/run_demo --data-path path/to/data.csv --incumbent-path path/to/legacy_model.pkl --incumbent-kind model --incumbent-name legacy_model
relaytic profiles review --run-dir artifacts/run_demo
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
relaytic profiles show --run-dir artifacts/run_demo
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
- profile and contract artifacts such as `quality_contract.json`, `quality_gate_report.json`, `budget_contract.json`, `budget_consumption_report.json`, `operator_profile.json`, and `lab_operating_profile.json`
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

Run the fast local smoke wall during normal development:

```bash
python scripts/check_push_readiness.py --mode quick
```

Run the broader local pre-push wall before you actually push:

```bash
python scripts/check_push_readiness.py --mode prepush
```

Use the full wall only when you touched MCP, runtime transport, network-backed dataset flows, or host-facing interoperability:

```bash
python scripts/check_push_readiness.py --mode full
```

Run the optional official-UCI domain dataset flows:

```bash
$env:RELAYTIC_ENABLE_NETWORK_DATASETS="1"
python -m pytest tests/test_domain_dataset_flows.py -q
```

Prepare the broader paper-grade benchmark and eval pack:

```bash
$env:RELAYTIC_ENABLE_PAPER_BENCHMARKS="1"
python -m pytest tests/test_paper_benchmark_pack.py -q
```

Dataset rationale and source links for that pack live in `docs/specs/paper_benchmark_pack.md`.

If you touch packaging, CLI, or security surfaces, also run:

```bash
python scripts/install_relaytic.py --skip-install --expected-profile core
python -m relaytic.ui.cli scan-git-safety
relaytic --help
```

## Compatibility Note

The public package and CLI are `relaytic`. Any remaining legacy import shims are compatibility-only and should not be used in new code, docs, or examples.
