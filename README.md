# Relaytic - Local-First AML Evaluation Lab

**Flagship research edition:** `Relaytic-AML`

Relaytic is a local-first inference lab. The current public story is Relaytic-AML: an AML and financial-crime evaluation environment that turns datasets, operator intent, modeling work, review assumptions, and optional local semantic help into auditable artifacts.

The public product name, package, and CLI stay `Relaytic` / `relaytic` / `relaytic`. `Relaytic-AML` is the flagship product story and roadmap direction, not a package rename.

Relaytic-AML is not presented as a production AML detector or a leaderboard-winning model. It is an evidence environment: local data custody, specialist-agent roles, reproducible artifacts, review-queue context, redacted handoff, and claim gates before public or paper-facing statements.

## How To Read This Repository

This repository is larger than the AML paper. Relaytic is the general local-first inference lab and command-line interface. Relaytic-AML is the current flagship edition, chosen because anti-money-laundering work forces privacy, temporal validity, graph context, human review, and public-claim discipline into one demanding setting.

For a paper review, use this path:

- Start with this README for navigation and claim boundaries.
- Read `docs/paper/relaytic_aml_arxiv_draft.pdf` or `docs/paper/relaytic_aml_arxiv_draft.md` for the manuscript.
- Run the paper regeneration commands in the paper section below if you want to reproduce the reader-facing artifacts.
- Use `ARCHITECTURE.md`, `INTEROPERABILITY.md`, `RUNTIME.md`, and `PROJECT_LAYOUT.md` only when you want the broader Relaytic platform context.

Deep audit, after the first read:

- System-evaluation proof: `docs/reports/paper_system_task_eval.json`, `docs/reports/paper_system_behavior_eval.json`, `docs/reports/paper_agent_handoff_eval.json`, `docs/reports/paper_no_lost_user_eval.json`, and `docs/reports/paper_claim_gate_case_studies.json`.
- Metric provenance and claim posture: `docs/reports/paper_result_table_final.json`, `docs/reports/paper_metric_cell_audit.json`, and `docs/reports/paper_publishability_matrix.json`.
- Final polish/readiness checks: `docs/reports/paper_narrative_polish_manifest.json`, `docs/reports/paper_paysim_selection_story_review.json`, `docs/reports/paper_reader_guidance_audit.json`, `docs/reports/paper_visual_table_polish_audit.json`, `docs/reports/paper_final_preflight_manifest.json`, and `docs/reports/paper_final_release_changelog.md`.

The long build-control files, especially `RELAYTIC_SLICING_PLAN.md` and `IMPLEMENTATION_STATUS.md`, are development provenance. They explain how the repo got here, but they are not required reading for the paper.

## Start Here: Relaytic-AML Demo Path

For a first technical review, start with the public-safe AML review-queue demo instead of reading the roadmap first.

Windows PowerShell:

```powershell
.\scripts\bootstrap.ps1 -Profile full -LaunchControlCenter:$false
relaytic doctor --expected-profile full --format json
relaytic demo aml-review-queue --run-dir artifacts\relaytic_aml_demo --format json
relaytic mission-control launch --run-dir artifacts\relaytic_aml_demo
```

macOS/Linux:

```bash
bash ./scripts/bootstrap.sh --profile full --no-launch-control-center
relaytic doctor --expected-profile full --format json
relaytic demo aml-review-queue --run-dir artifacts/relaytic_aml_demo --format json
relaytic mission-control launch --run-dir artifacts/relaytic_aml_demo
```

After the demo bundle exists, inspect the proof path in this order:

```powershell
relaytic show --run-dir artifacts\relaytic_aml_demo --format json
relaytic aml environment --run-dir artifacts\relaytic_aml_demo --format json
relaytic aml temporal --run-dir artifacts\relaytic_aml_demo --format json
relaytic guide export-context --run-dir artifacts\relaytic_aml_demo --audience external-llm --format json
```

The demo is meant to show the product shape: analyst queue, case packet, drift posture, benchmark/public-claim guards, business-value guard, baseline/ablation proof, and model-vs-environment separation. It is not by itself a paper-grade benchmark result.

## What To Inspect

The shortest proof tour is:

- `aml_demo_bundle_manifest.json` for the public-safe demo bundle.
- `case_packet.json`, `alert_queue_rankings.json`, and `analyst_review_scorecard.json` for analyst workflow value.
- `aml_business_value_report.json`, `review_capacity_metric_report.json`, and `operational_metric_guard.json` for guarded business-value claims.
- `aml_baseline_matrix.json`, `aml_ablation_matrix.json`, and `aml_benchmark_relevance_scorecard.json` for baseline and contribution evidence.
- `aml_temporal_benchmark_claim_report.json` and `aml_time_window_scorecard.json` for delayed-label, weak-label, and temporal claim posture.
- `aml_environment_scorecard.json`, `aml_workflow_task_matrix.json`, and `aml_benchmark_environment_scorecard.json` for whether Relaytic behaved well as an AML workflow environment, not only as a model scorer.
- `benchmark_release_gate.json`, `paper_claim_guard_report.json`, and `aml_public_claim_guard.json` for what can be claimed publicly.
- `trace_model.json`, `agent_eval_matrix.json`, `security_eval_report.json`, and `eval_surface_parity_report.json` when present for trace/eval posture.
- `docs/reports/public_surface_inventory.json`, `docs/reports/module_split_report.json`, and `docs/reports/benchmark_surface_cleanup_report.json` for the pre-Academy repo credibility audit before paper-freeze work.
- `docs/reports/paper_release_freeze_manifest.json`, `docs/reports/paper_result_table.json`, `docs/reports/paper_claim_boundary_report.json`, and `docs/reports/reproducibility_attestation.json` for the Slice 15Z-R paper/release freeze pack.

## Claim Boundaries

Use these labels when discussing results:

- **Demo-only:** the public-safe fixture proves the product workflow and artifact contract, not real-world AML superiority.
- **Dev-benchmark:** a benchmark run or proof pack on a visible/dev partition can guide engineering, but cannot support paper-grade claims by itself.
- **Holdout-benchmark:** a held-out benchmark partition can support stronger evidence if the claim guards, leakage audits, and benchmark-environment score pass.
- **Claim-safe paper-ready:** allowed only when the local evidence artifacts, public-claims report, table provenance, source package, and release-safety scan agree. This still does not imply hard AML or headline benchmark superiority.

More context:

- [Why Relaytic-AML](docs/why_relaytic_aml.md)
- [Product Story](docs/product_story.md)
- [Paper Benchmark Runbook](docs/paper_benchmark_runbook.md)
- [UI Frontier Review](docs/relaytic_ui_frontier_review.md)

## Relaytic-AML Paper Draft

The current paper draft presents Relaytic-AML as a local-first evaluation lab for financial-crime ML. It is an architecture and evidence-discipline paper, not a hard AML superiority result. Relaytic remains the general package and CLI. Relaytic-AML is the current flagship edition and the focus of the draft because AML makes privacy, temporal validity, graph context, human review, and claim discipline visible in one domain.

The repo includes the Markdown draft, a compiled PDF draft, an arXiv source candidate, references, figures, tables, and the underlying public evidence artifacts. The final source/PDF preflight is ready for author review, but public upload still needs final public tag selection, page-by-page human PDF inspection, and a clean tag-target confirmation.

Inspect:

- `docs/paper/relaytic_aml_arxiv_draft.md` for the claim-safe paper draft.
- `docs/paper/arxiv_src/` for the arXiv source bundle.
- `docs/paper/references.bib` for citable sources.
- `docs/paper/figures/` and `docs/paper/tables/` for generated visual/table assets.
- `docs/reports/paper_public_claims_allowed.json` for allowed and blocked public wording.
- `docs/reports/paper_attention_pack.md` for claim-safe public post text.
- `docs/reports/paper_final_preflight_manifest.json` and `docs/reports/paper_final_release_changelog.md` for the final source/PDF preflight state.

Regenerate:

Windows PowerShell:

```powershell
py -3.11 -m relaytic.ui.cli release-safety paper-system-eval --format json
py -3.11 -m relaytic.ui.cli release-safety paper-release --format json
py -3.11 -m relaytic.ui.cli release-safety paper-narrative-polish --format json
py -3.11 -m relaytic.ui.cli release-safety paper-arxiv-source --format json
Set-Location docs\paper\arxiv_src
pdflatex -interaction=nonstopmode -halt-on-error main.tex
bibtex main
pdflatex -interaction=nonstopmode -halt-on-error main.tex
pdflatex -interaction=nonstopmode -halt-on-error main.tex
Set-Location ..\..\..
Copy-Item -LiteralPath docs\paper\arxiv_src\main.pdf -Destination docs\paper\relaytic_aml_arxiv_draft.pdf -Force
py -3.11 -m relaytic.ui.cli release-safety paper-final-preflight --format json
py -3.11 -m pytest tests/test_paper_track_p15.py tests/test_paper_track_p20.py tests/test_paper_track_p21.py -q
```

macOS/Linux:

```bash
python3 -m relaytic.ui.cli release-safety paper-system-eval --format json
python3 -m relaytic.ui.cli release-safety paper-release --format json
python3 -m relaytic.ui.cli release-safety paper-narrative-polish --format json
python3 -m relaytic.ui.cli release-safety paper-arxiv-source --format json
cd docs/paper/arxiv_src
pdflatex -interaction=nonstopmode -halt-on-error main.tex
bibtex main
pdflatex -interaction=nonstopmode -halt-on-error main.tex
pdflatex -interaction=nonstopmode -halt-on-error main.tex
cd ../../..
cp docs/paper/arxiv_src/main.pdf docs/paper/relaytic_aml_arxiv_draft.pdf
python3 -m relaytic.ui.cli release-safety paper-final-preflight --format json
python3 -m pytest tests/test_paper_track_p15.py tests/test_paper_track_p20.py tests/test_paper_track_p21.py -q
```

Hard AML, headline, SOTA, RevClassify parity, graph-neural superiority, and hard business-value claims remain blocked until later gates explicitly allow them.

## Current Product Baseline

The repository already supports a working early product baseline. Treat the list below as a capability inventory for reviewers and contributors, not as a paper claim ladder or proof of deployment readiness:

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
- demo-grade onboarding through an explicit public-safe walkthrough, clearer mode education, and stuck-recovery guidance surfaced directly from mission control, chat, and `docs/handbooks/relaytic_demo_walkthrough.md`
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
- deterministic AML graph and casework surfaces that can turn structural risk into review-queue policy, ranked entity cases, analyst burden estimates, and one evidence-backed case packet
- deterministic AML stream-risk surfaces that can make weak-label risk, delayed confirmation, rolling alert pressure, and recalibration posture visible on ordered transaction streams
- AML proof-pack surfaces that align PaySim-style and flattened Elliptic-style workload evidence across benchmark CLI/show, run summary, assist, mission control, and public-claim gates
- AML business-value surfaces through `relaytic aml business-value`, with analyst-hour savings, false-positive reduction, review-capacity metrics, incumbent capacity tradeoffs, and an operational guard that blocks model-score overclaims
- AML baseline and ablation surfaces through `relaytic aml baselines`, with baseline matrices, optional-adapter fallback reporting, no-graph/no-temporal/no-review-budget/no-calibration/no-typology-prior ablations, and supported/proxy/blocked benchmark relevance scorecards
- AML temporal weak-label surfaces through `relaytic aml temporal`, with delayed-label evaluation, positive-unlabeled posture, threshold-drift reporting, rowless time-window scorecards, and temporal public-claim gates
- AML evaluation-environment surfaces through `relaytic aml environment`, with model-vs-environment score separation, workflow task matrices, unsafe-steering rejection evidence, benchmark-environment scoring, and failure reports
- a one-command Relaytic-AML review-queue demo bundle through `relaytic demo aml-review-queue`, with a flow report, business-metric table, artifact index, business-value guard, baseline/ablation proof, and mission-control investigation board
- pre-Academy repo credibility reports under `docs/reports/`, including module-size audit, public-surface inventory, module-split evidence, extraction boundaries, and benchmark cleanup debt before the paper/release freeze
- a paper/release freeze surface through `relaytic release-safety paper-freeze`, with relevant benchmark catalog, multidimensional result table, claim-boundary report, reproducibility attestation, and a safe attention-pack manifest that blocks hard AML performance claims until holdout evidence is frozen
- a claim-safe paper surface through `relaytic release-safety paper-release`, with Markdown draft, citable references, paper tables, public attention text, arXiv submission notes, and allowed-public-claims report
- a final paper-source surface through `relaytic release-safety paper-arxiv-source`, with deterministic LaTeX source, converted PDF figures, citation/figure audits, source-package scanning, and a release-candidate checklist
- copy-only data handling that stages immutable working copies inside each run directory and avoids persisting original source paths

Relaytic has a longer internal build history, but the public story is now simpler: Relaytic is the local-first inference lab, and Relaytic-AML is the flagship edition used to prove the architecture in a demanding domain. Detailed build history lives in `RELAYTIC_SLICING_PLAN.md` and `IMPLEMENTATION_STATUS.md`. The next product work is capability-card and academy-style hardening, while the paper work is human-facing: inspect the compiled PDF, confirm a clean tag target, and submit only claim-safe wording.

That ordering is deliberate. Relaytic is more useful when judged as a serious AML evaluation lab than as a generic capability-evolution project with no sharp domain wedge.

The normative product-contract pack that now governs the shipped workspace layer and its future follow-ons lives in [workspace_lifecycle.md](docs/specs/workspace_lifecycle.md), [result_contract_schema.md](docs/specs/result_contract_schema.md), [governed_learnings_schema.md](docs/specs/governed_learnings_schema.md), [model_competitiveness_contract.md](docs/specs/model_competitiveness_contract.md), [performance_recovery_contract.md](docs/specs/performance_recovery_contract.md), [temporal_benchmark_pack.md](docs/specs/temporal_benchmark_pack.md), [aml_frontier_contract.md](docs/specs/aml_frontier_contract.md), [aml_benchmark_pack.md](docs/specs/aml_benchmark_pack.md), [capability_academy_contract.md](docs/specs/capability_academy_contract.md), [mission_control_contract.md](docs/specs/mission_control_contract.md), [handoff_result_migration.md](docs/specs/handoff_result_migration.md), [learnings_migration_contract.md](docs/specs/learnings_migration_contract.md), [external_agent_continuation_contract.md](docs/specs/external_agent_continuation_contract.md), [mission_control_flows.md](docs/specs/mission_control_flows.md), [test_and_proof_matrix.md](docs/specs/test_and_proof_matrix.md), and [flagship_demo_pack.md](docs/specs/flagship_demo_pack.md).

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
- the shortest public-safe demo path is in `docs/handbooks/relaytic_demo_walkthrough.md`
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
- AML proof-pack artifacts such as `aml_benchmark_manifest.json`, `aml_holdout_claim_report.json`, `aml_demo_scorecard.json`, `aml_public_claim_guard.json`, and `aml_failure_report.json`
- AML demo-bundle artifacts such as `aml_demo_bundle_manifest.json`, `aml_demo_business_metric_table.json`, `aml_demo_flow_report.md`, `aml_demo_artifact_index.json`, and `aml_investigation_board.json`
- AML environment artifacts such as `aml_environment_scorecard.json`, `aml_workflow_task_matrix.json`, `aml_environment_failure_report.json`, and `aml_benchmark_environment_scorecard.json`
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
