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

Relaytic's paper path now supports both local transaction snapshots and the raw three-file Elliptic graph bundle.

That means:

- PaySim-style CSV snapshots are in scope now
- flattened Elliptic-style graph snapshots are in scope now
- raw multi-file Elliptic bundles are in scope through provenance, temporal split, and P7 graph-baseline artifacts
- P8 initially recorded Elliptic2 as blocked, P8-A recovered its official labeled core plus pinned RevTrack modern-reference assets into a hash-audited pilot path, P8-B admits a supporting repeated-seed/context row only, P8-C blocks reference-parity/headline claims, and P8-D accepts thesis narrowing so Elliptic2 remains supporting context rather than a performance contribution
- P9 adds operational evidence under the P8-D boundary: review-budget rows, false-positive burden proxies, case-packet completeness state, and an operational claim guard. These are supporting paper metrics, not hard business-value claims while analyst assumptions, case packets, and same-queue baseline evidence remain incomplete
- P10 turns those artifacts into reproducible tables with per-cell provenance and a publishability matrix. Passing P10 means the paper can be drafted; it does not mean hard AML, SOTA, headline, or business-value claims are allowed
- P11 turns the P10 evidence into a claim-linted paper draft and deterministic figure pack. Passing P11 means the draft is internally consistent with the artifact contract; it still does not allow hard AML, SOTA, headline, RevClassify parity, graph-neural superiority, or hard business-value claims before P12/P13 gates
- P12 turns the P10/P11 evidence into an external dry-run proof. Passing P12 means the clean-clone checklist, optional isolated full-profile install probe, paper-smoke regeneration, leak scan, reproduction failure report, and go/no-go gate agree; it still allows only claim-safe evaluation-environment release language before P13
- P13 turns the P10-P12 evidence into a claim-safe arXiv release pack: final generated draft, citable references, generated tables, attention pack, checklist, release manifest, and allowed-public-claims report. Passing P13 allows only evaluation-environment public wording; hard AML, SOTA, headline, RevClassify parity, graph-neural superiority, production-ready, and hard business-value claims remain blocked
- P8 records AMLSim as blocked until a seeded generated bundle, generator revision, output hashes, generated-data license, and typology audit exist; once verified it remains synthetic `proxy` evidence only

Relaytic-AML must be honest about that boundary. Raw Elliptic support is now real, but it does not imply Elliptic2-scale subgraph support or graph-neural superiority.

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

Expected raw-bundle or flattened shape:

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

P8-A confirmed it as the highest-upside scientific breadth recovery, and P8-B records stable supporting evidence: official-partition repeated test `PR-AUC=0.943240 +/- 0.000882` and row-order-independent content-hash test `PR-AUC=0.929669 +/- 0.000538`. P8-C then blocks stronger claims: faithful RevClassify parity is not locally executable in the current environment, the RevTrack-evaluable cohort (`110902` rows) is not proven equivalent to the audited current official core (`121810` rows), and a strict entity-disjoint component split is degenerate because `110889/110902` rows share one identity component. P8-D accepts the first-paper narrowing: this track remains supporting context and limitation evidence only, while faithful parity reprovisioning stays a future extension. P9 keeps it out of operational performance contribution claims as well.

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
2. Elliptic raw graph provenance and graph-baseline runs work end to end through the current CLI
3. both workload families materialize AML contracts plus graph/case artifacts
4. benchmark doctrine for both is explicit and honest

## Adopted pre-Academy proof sequence

The benchmark pack is now part of a broader AML proof/productization sequence. The repository has followed this order before Academy work resumes:

1. **15R-A**: finished AML proof-pack alignment across tests, CLI, run summary, assist, mission control, docs, and claim gates.
2. **15S**: created the public-safe flagship AML demo bundle.
3. **15T**: added operational business-value metrics, analyst-hour proof, and guarded overclaim blocking.
4. **15U**: added strong AML baselines, ablations, adapter fallback reporting, contribution summaries, and benchmark relevance scorecards.
5. **15V**: added raw graph and subgraph ingestion.
6. **15W**: strengthened temporal and weak-label evaluation.
7. **15X**: added AML evaluation-environment scorecards.
8. **15Y**: rewrote first-contact docs around the flagship path and added the paper benchmark runbook.
9. **15Z**: cleaned repo credibility risks with module-split evidence, public-surface inventory, and retained benchmark cleanup debt.
10. **15Z-R**: froze the relevant benchmark and release evidence with a rerunnable paper-freeze command, claim boundaries, reproducibility attestation, and hard-performance-claim blocking.
11. **Paper Track P0-P13, with P8-C/P8-D inserted after P8-B**: completed the frozen but claim-blocked release pack into a paper-ready path: commit the baseline, clean public surfaces, freeze the paper thesis, register datasets, run PaySim-style and Elliptic-style evidence, add strong tabular and graph baselines, recover and challenge modern Elliptic2 evidence, explicitly narrow its neural-reference/cohort gap for the first paper, add guarded operational evidence, generate reproducible per-cell-provenance tables, draft and lint the paper, dry-run from a clean clone, and release to arXiv only if gates pass.

Benchmark success must stay separated from:

- schema compatibility
- operational business value
- environment behavior
- public-claim readiness
- paper-safe broader claims

## Paper-track relevance gate

The final pre-Academy paper track must not rely on one easy or repeatedly inspected dataset.

The relevant benchmark catalog should include:

- PaySim-style or equivalent transaction-fraud temporal evidence, treated as useful but synthetic/proxy unless stronger real public data is available
- Elliptic-style graph AML evidence, with flattened, raw-graph, and claim-scope status separated
- Elliptic2-style subgraph AML evidence when the loader and data-access posture are mature enough; otherwise a precise blocked reason
- AMLSim-style synthetic bank graph evidence when reproducible local generation is available
- the generic paper benchmark pack only as supporting structured-data evidence, not as the flagship AML proof

Public claims require the benchmark catalog, holdout/partition posture, operational business-value guard, benchmark truth gate, environment scorecard, release-safety scan, paper table provenance, claim lint, and external dry run to agree.
