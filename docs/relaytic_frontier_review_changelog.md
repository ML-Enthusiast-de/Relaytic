# Relaytic Frontier Review Changelog

Date: 2026-05-06

Status: historical design review. Its recommendations were adopted into the
master plan and implemented through Slice 15Z-R. Paper Track P0-P27 is also
implemented. Use `IMPLEMENTATION_STATUS.md` for current status.

## Executive Verdict

Relaytic is more interesting after the Relaytic-AML pivot than it was as a broad structured-data automation system.

The review recommended moving beyond a generic "AutoML with agents" framing:

> Relaytic is an artifact-first evaluation and decision environment for high-stakes structured-data agents, instantiated as Relaytic-AML for fraud and financial-crime workflows where graph structure, temporal drift, weak labels, review budgets, and auditability matter.

At the time of review, that direction was technically credible but the public
proof path, benchmark evidence, and repository presentation were incomplete.
The subsequent `15R-A` through `15Z-R` and `P0` through `P27` work addressed
the documented release and paper gaps. The detector claim boundaries remain.

## State At Review Time

- The control docs say the repo is implemented through Slice 15Q and still points to Slice 15R as next.
- The latest commit says "Added up to (but not finished) 15R."
- The source already contains AML proof-pack code paths such as `aml_benchmark_manifest`, `aml_holdout_claim_report`, `aml_demo_scorecard`, `aml_public_claim_guard`, and `aml_failure_report`.
- The 15R slice doc still says `Planned`, and there is no obvious `tests/test_cli_slice15r.py`.
- The working tree was clean during this review, so the state appears committed but strategically inconsistent: some 15R implementation exists, while roadmap/status docs and targeted tests lag behind.

## Technical Differentiation At Review Time

Partially.

Promising parts:

- local-first, artifact-first execution is a real differentiator for sensitive data
- explicit traces, adjudication, protocol conformance, release-safety gates, and skeptical steering fit the frontier-evals mindset
- AML is a strong domain wedge because it combines graph reasoning, temporal drift, rare events, review economics, delayed labels, and auditability
- the product has a credible agent-facing contract rather than only a human-readable report layer
- the benchmark-truth and public-claim gates are exactly the right instinct

Open issues at the time:

- the repo still contains too much orchestration breadth relative to hard proof
- the public narrative is too long and diffuse for first contact
- the strongest technical contribution is not yet obvious in one sentence
- raw graph AML, subgraph tasks, production stream connectors, and real incumbent comparisons are still shallow or future-facing
- the modeling core may still look less novel than the artifact/control system around it
- huge modules such as `src/relaytic/ui/cli.py`, `src/relaytic/modeling/training.py`, `src/relaytic/mission_control/agents.py`, and `src/relaytic/benchmark/agents.py` make the repo look less mature than the architecture docs claim

## Public Positioning

The project should be framed around the problem it solves, not around the number of agents or slices in the repo.

Weak framing:

- "I built an AML AutoML tool."
- "I built many agents for fraud detection."
- "Relaytic can do many dataset tasks."

Strong framing:

- "I built a local-first eval environment for high-stakes structured-data agents, with reproducible traces, adversarial steering tests, benchmark gates, public-claim guards, and self-improvement quarantine."
- "I instantiated it in AML because fraud/financial-crime is a hard real-world domain with weak labels, graph/temporal structure, drift, and human review budgets."
- "The system produces runnable evidence, not just explanations: benchmark manifests, adjudication scorecards, case packets, drift triggers, review-budget operating points, failure reports, and cross-surface protocol checks."

The AML product is the concrete proving ground. The broader technical story is evals, environments, systems, and rigorous product-shaped ML.

## Biggest Credibility Risks

1. Too much roadmap, not enough runnable flagship proof.
2. Docs and status files lagging behind code.
3. No single small demo that makes the value obvious in under five minutes.
4. Benchmark story can still look benchmark-shaped unless holdouts, ablations, and failure reports are aggressively separated.
5. Current repo structure makes some mature claims feel less credible because core files are very large.
6. The AML story is not yet production-shaped enough: it needs incumbent comparison, analyst-hour value, false-positive reduction, delayed labels, graph expansion, and drift recovery in one coherent walkthrough.
7. The capability-academy and representation plans should remain deferred
   until the AML proof path is reproducible and release-ready.

## Recommended Implementation Changelog

### 15R-A. Finish The AML Proof Pack

- Mark Slice 15R as shipped only after docs, tests, CLI surfaces, run summary, assist, and mission control agree.
- Add `tests/test_cli_slice15r.py`.
- Prove PaySim-style and flattened Elliptic-style workloads both materialize the AML proof artifacts.
- Require cross-track coverage before broader AML claims are allowed.
- Make `aml_failure_report.json` useful when Relaytic loses, not just present.
- Update `IMPLEMENTATION_STATUS.md`, `MIGRATION_MAP.md`, `ARCHITECTURE_CONTRACT.md`, `README.md`, and `RELAYTIC_BUILD_MASTER.md`.

### 15S. Flagship AML Demo Pack

- Build one golden demo named `relaytic-aml-review-queue`.
- Input: PaySim-style or local fraud CSV.
- Output: ranked alert queue, top entity case packet, review-budget operating point, drift posture, benchmark parity, public-claim guard, and failure report.
- Add one imported incumbent ruleset and show whether Relaytic beats it under the same split and budget.
- Add a public-safe HTML or markdown demo report with one diagram of the run flow and one table of business metrics.
- Acceptance test: one command creates the demo bundle from fixture data.

### 15T. Business-Value Metrics

- Add first-class `analyst_hours_saved`, `false_positive_reduction_at_fixed_recall`, `recall_at_review_capacity`, `precision_at_top_k`, and `case_packet_completeness`.
- Ensure benchmark and run summary separate ML metrics from operational metrics.
- Show the concrete tradeoff: "At 100 reviews, Relaytic catches X positives and avoids Y low-value alerts versus incumbent."
- Add tests where AUROC improves but review-budget utility worsens, and Relaytic refuses to overclaim.

### 15U. Strong AML Baselines And Ablations

- Add explicit baselines for:
  - ruleset incumbent
  - logistic regression / calibrated linear model
  - random forest / extra trees
  - histogram gradient boosting
  - XGBoost / LightGBM / CatBoost when installed
  - lagged temporal baseline
  - structural graph baseline
  - graph-shadow candidate
- Add ablations for:
  - no graph features
  - no temporal features
  - no review-budget optimization
  - no calibration
  - no typology priors
- Make the ablation matrix the public center of the paper/demo story.

### 15V. Raw Graph And Subgraph Ingestion

- Add a dedicated AML graph loader for Elliptic-style multi-file graph bundles.
- Keep flattened snapshots supported, but label them honestly as flattened.
- Add subgraph/task packaging for Elliptic2-style or AMLSim-derived public workloads when licensing is clean.
- Emit one graph loader manifest with node, edge, feature, time, and label provenance.

### 15W. Temporal And Weak-Label Upgrade

- Add delayed-label evaluation windows.
- Add positive-unlabeled posture for unlabeled or late-confirmed fraud.
- Add threshold drift tests across time windows.
- Add "would retrain, recalibrate, or change threshold" explanations tied to rolling evidence.
- Keep sequence-native models shadow-only until they beat strong lagged tabular baselines.

### 15X. Frontier-Evals Reframe

- Add an `eval_environments/` or equivalent docs/demo layer that describes Relaytic runs as evaluation environments.
- Define tasks such as:
  - detect task and target from messy operator request
  - reject unsafe steering
  - beat an incumbent under the same contract
  - optimize alert queue under review budget
  - recover under drift
  - produce public-safe claims
- Add environment scorecards separate from model scorecards.
- This is the bridge from AML product to broader evaluation-environment relevance.

### 15Y. Demo-First Documentation Rewrite

- Rewrite the first half of `README.md` around one flagship path:
  - install
  - run AML demo
  - inspect case packet
  - inspect benchmark/public-claim guard
  - inspect trace/evals
- Move the long slice history lower or into docs.
- Create `docs/why_relaytic_aml.md` with the crisp thesis.
- Create `docs/product_story.md` with positioning, architecture diagram, and proof links.

### 15Z. Repo Credibility Cleanup Before Academy

- Split the largest files before adding capability-academy work:
  - `src/relaytic/ui/cli.py`
  - `src/relaytic/modeling/training.py`
  - `src/relaytic/mission_control/agents.py`
  - `src/relaytic/benchmark/agents.py`
- Start with extraction, not redesign.
- Add a public surface inventory and import-boundary smoke test after the split.
- Keep Slice 18 as the final cleanup pass, but do not wait until Slice 18 to fix credibility-damaging module size.

## What To Pause

- Pause Slice 16 Academy until 15R/15S prove the AML wedge.
- Pause representation-engine work until there is a benchmark where representation learning is a justified response to a measured failure.
- Pause broad new integrations unless they directly strengthen the AML proof path.
- Pause more agent names. Add fewer, sharper proof loops.

## One-Sentence North Star

Relaytic-AML should become the local-first eval and decision environment for financial-crime AI: it turns messy transaction data into traceable model choices, review-budget-aware alert queues, graph-backed case evidence, drift-aware recalibration decisions, and public-safe proof reports that a skeptical engineer can rerun.

## External Signals Consulted

- public descriptions of evaluation environments, red-team testing, scalable
  evaluation systems, secure data infrastructure, and ML feature engineering
- public financial-fraud engineering material covering anomaly detection,
  scoring, false-decline control, and continuous monitoring

These sources informed the dated product review. They are not evidence for the
Relaytic-AML paper and are not part of the current related-work bibliography.
