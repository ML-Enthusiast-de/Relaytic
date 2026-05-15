# AML Benchmark Pack

## Purpose

This document fixes the real-world benchmark doctrine for Relaytic-AML.

Relaytic-AML should be judged on workloads that look like production financial-crime and payment-risk work, not only on generic tabular benchmarks.

## Why this exists

Relaytic-AML is more credible when it can support the workload shapes that real fraud and AML teams actually use:

- PaySim-style temporal transaction fraud
- Elliptic-style temporal graph AML
- later, Elliptic2-style subgraph AML

Those workload families are closer to the user's existing fraud projects and to the kinds of problems a PayPal-style risk team would care about.

## Current public support boundary

Today Relaytic's public ingestion contract is still a local single-snapshot file.

That means:

- PaySim-style CSV snapshots are in scope now
- flattened Elliptic-style graph snapshots are in scope now
- raw multi-file graph bundles such as the full Elliptic triplet should be treated as a future dedicated loader path

Relaytic-AML must be honest about that boundary. It should not imply that raw graph bundles are first-class if it still expects a flattened local snapshot.

## Canonical workload tracks

### 1. PaySim-style temporal transaction fraud

Expected shape:

- `step`
- `type`
- `amount`
- `nameOrig`
- `nameDest`
- balance fields
- fraud label such as `isFraud`

What Relaytic-AML should prove here:

- chronological split discipline
- rare-event posture
- fixed-FPR-budget operating points
- review-budget-aware thresholding
- counterparty and shared-instrument reasoning

### 2. Elliptic-style temporal graph AML

Expected flattened shape:

- `src`
- `dst`
- `time_step`
- supervised label such as `y`
- local numeric features

What Relaytic-AML should prove here:

- temporal split discipline
- time-step stability reporting
- graph/entity/subgraph reasoning
- threshold tuning on validation, fixed on test
- honest comparison between structural baselines and heavier graph candidates

### 3. Later: Elliptic2-style subgraph AML

This is the harder public-proof track.

It should be used once Relaytic-AML can support subgraph-centric benchmark packaging and holdout-safe claim gates.

### 4. AMLSim-style synthetic bank-transaction graph

Expected shape:

- generated account, transaction, alert, SAR, and typology-pattern outputs
- account/entity graph edges
- configurable simulation steps and alert patterns

What Relaytic-AML should prove here:

- account/entity risk scoring
- typology-aware alert generation
- synthetic-bank graph provenance
- analyst-review queue optimization over known injected patterns
- clear labeling as synthetic benchmark evidence, not real-bank deployment proof

## Required evaluation posture

Relaytic-AML should not reduce AML evaluation to AUROC.

Priority metrics:

- `pr_auc`
- `precision_at_k`
- `recall_at_review_budget`
- recall / precision at fixed FPR budgets where appropriate
- threshold stability across time windows
- time-sliced quality by `time_step`

Useful secondary metrics:

- `log_loss`
- `roc_auc`
- calibration error

## Claim discipline

Relaytic-AML must separate:

- schema compatibility
- benchmark execution success
- competitiveness
- public-claim readiness

Supporting a PaySim-like or Elliptic-like dataset shape is not the same as winning on it.

## Near-term proof obligation

Before the AML flagship paper/demo pack is considered credible, Relaytic-AML should be able to show:

1. PaySim-like runs work end to end through the current CLI
2. Elliptic-like flattened graph runs work end to end through the current CLI
3. both workload families materialize AML contracts plus graph/case artifacts
4. benchmark doctrine for both is explicit and honest

## Adopted pre-Academy proof sequence

The benchmark pack is now part of a broader AML proof/productization sequence. The next implementation sessions must follow this order before Academy work resumes:

1. **15R-A**: finished AML proof-pack alignment across tests, CLI, run summary, assist, mission control, docs, and claim gates.
2. **15S**: created the public-safe flagship AML demo bundle.
3. **15T**: added operational business-value metrics, analyst-hour proof, and guarded overclaim blocking.
4. **15U**: add strong AML baselines and ablations.
5. **15V**: add raw graph and subgraph ingestion.
6. **15W**: strengthen temporal and weak-label evaluation.
7. **15X**: add AML evaluation-environment scorecards.
8. **15Y**: rewrite first-contact docs around the flagship path.
9. **15Z**: clean repo credibility risks before capability growth expands.
10. **15Z-R**: freeze the relevant benchmark and release evidence for paper/demo use.

Benchmark success must stay separated from:

- schema compatibility
- operational business value
- environment behavior
- public-claim readiness
- paper-safe broader claims

## Release-freeze relevance gate

The final pre-Academy paper/release freeze must not rely on one easy or repeatedly inspected dataset.

The relevant benchmark catalog should include:

- PaySim-style or equivalent transaction-fraud temporal evidence, treated as useful but synthetic/proxy unless stronger real public data is available
- Elliptic-style graph AML evidence, with flattened, raw-graph, and claim-scope status separated
- Elliptic2-style subgraph AML evidence when the loader and data-access posture are mature enough; otherwise a precise blocked reason
- AMLSim-style synthetic bank graph evidence when reproducible local generation is available
- the generic paper benchmark pack only as supporting structured-data evidence, not as the flagship AML proof

Public claims require the benchmark catalog, holdout/partition posture, operational business-value guard, benchmark truth gate, environment scorecard, and release-safety scan to agree.
