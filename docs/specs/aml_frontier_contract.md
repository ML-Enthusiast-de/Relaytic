# Relaytic-AML Frontier Contract

## Purpose

This document freezes the flagship domain pivot for Relaytic.

Relaytic remains the public product name, package, and CLI. The new flagship story is **Relaytic-AML**: the AML and financial-crime frontier edition of Relaytic.

The goal is to stop presenting Relaytic as a broad structured-data system with an unclear wedge and instead make it a serious local-first investigation system for high-stakes anti-money-laundering, fraud, and analyst-review workflows.

## Why this pivot exists

The repository now tells a credible story about:

- governed local execution
- strong artifact discipline
- human and agent operability
- benchmark rigor and benchmark-truth gates

But that is still not enough to make the project feel top-tier to a frontier lab, a payment-risk org, or an AML team.

The missing piece is a sharper thesis.

Relaytic becomes much more compelling when it is judged against a hard, high-value, domain-specific problem:

- graph- and entity-heavy risk
- extreme class imbalance
- temporal drift
- review-budget constraints
- false-positive pain
- explainability and auditability requirements

AML and adjacent payment-fraud work fit Relaytic's existing strengths better than a generic "all structured data" story.

## Flagship thesis

Relaytic-AML should be the local-first investigation and decision system for:

- transaction-monitoring model development
- alert triage and analyst-review optimization
- graph and subgraph money-laundering pattern detection
- typology-aware challenger design
- drift-aware recalibration and retraining
- benchmark-safe and regulator-safe evidence production

The system should be strongest when:

- rules, graph signals, temporal signals, and tabular features all matter
- review teams are overloaded
- labels are weak, delayed, or incomplete
- false positives are expensive
- human escalation remains necessary

## Hard problems Relaytic-AML must solve

### 1. Graph and subgraph reasoning

AML is not only row classification.

Relaytic-AML must reason about:

- entities
- counterparties
- communities
- multi-hop paths
- suspicious subgraphs
- typology motifs such as smurfing, layering, funnels, and peel chains

### 2. Analyst-budget optimization

A model that raises too many alerts is not a strong AML system.

Relaytic-AML must optimize under explicit review budgets:

- fixed analyst capacity
- precision at top-k
- recall at constrained review volume
- investigation time burden
- explainability for case handoff

### 3. Temporal and streaming drift

AML behavior changes.

Relaytic-AML must support:

- rolling evaluation
- event-preserving temporal splits
- concept drift detection
- threshold drift detection
- recalibration under shifting base rates

### 4. Weak labels and delayed ground truth

Relaytic-AML must not assume perfect supervised labels.

It needs explicit support for:

- positive-unlabeled posture
- delayed case outcomes
- noisy labels
- semi-supervised and self-supervised candidate paths
- shadow evaluation where full truth is unavailable

### 5. Human-review integration

Relaytic-AML is not done when it emits a probability.

It must support:

- case packets
- review queue prioritization
- reason codes
- evidence bundles
- "why this alert now?" explanations
- "what would reduce uncertainty?" recommendations

## What Relaytic-AML must not become

It must not become:

- a graph-paper zoo with weak product judgment
- a benchmark-only crypto demo
- an opaque fraud score service
- a streaming system that sacrifices auditability
- a benchmark-overfit system shaped around one public pack

## Required metrics and operating objectives

Relaytic-AML must evaluate more than AUROC.

Primary decision-facing metrics should include:

- precision at k
- recall at fixed review budget
- PR AUC
- false positives per analyst hour
- alert-to-case conversion quality
- threshold stability across time windows
- calibration under drift
- typology coverage
- explanation completeness for case handoff

Secondary modeling metrics can still include:

- log loss
- ROC AUC
- F1
- balanced accuracy

But those are not enough for the flagship story.

## Benchmark doctrine

Relaytic-AML should use a tiered benchmark doctrine.

### Dev pack

Used to shape implementation.

### Holdout pack

Used to test whether gains generalized beyond the repeatedly inspected dev suite.

### Paper pack

Used for public claims only after the other two are healthy.

The paper pack should eventually cover:

- transaction-level rare-event detection
- entity / account risk scoring
- graph / subgraph AML detection
- temporal drift and recalibration
- analyst-review queue optimization

## Canonical public datasets to target

The exact pack can evolve, but the roadmap should be designed around public or reproducible tasks such as:

- PaySim-style temporal transaction fraud
- Elliptic transaction risk
- Elliptic2 subgraph AML tasks
- AMLSim-derived public tasks where licensing and reproducibility are acceptable
- public transaction-fraud datasets with temporal ordering
- graph-feature AML baselines and review-budget-oriented fraud tasks

Near-term practical rule:

- PaySim-style and flattened Elliptic-style snapshots should work now through the existing local file contract
- raw multi-file graph bundles and labeled subgraph packs now have dedicated loader/provenance artifacts, but public graph benchmark or SOTA claims remain blocked until benchmarked and claim-gated

Relaytic-AML must never silently optimize on dataset identity. Public claims require holdout verification and a benchmark-generalization audit.

## Required flagship demos

Relaytic-AML should eventually keep these four flagship demos green:

1. legacy alert engine challenge
2. overloaded review queue optimization
3. suspicious subgraph / entity expansion with explanation
4. drift-triggered recalibration or threshold reset without hidden behavior

## Pre-Academy implementation doctrine

Relaytic must not move into the capability Academy track merely because the first AML proof artifacts exist.

The AML proof path is accepted only after these slices are complete:

- **15R-A** finished the AML proof pack by aligning tests, CLI, run summary, assist, mission control, docs, and public-claim gates.
- **15S** built one public-safe flagship AML demo bundle around review-queue value and case evidence.
- **15T** added guarded business-value metrics such as analyst-hours saved, false-positive reduction at fixed recall, recall at review capacity, precision at top-k, case-packet completeness, and operational overclaim blocking.
- **15U** added strong AML baselines, capability ablations, adapter fallback reporting, contribution summaries, and benchmark relevance scorecards so graph, temporal, calibration, threshold, and review-budget contributions are measured.
- **15V** added raw graph and subgraph ingestion, graph provenance, graph claim scope, and public graph benchmark cataloging so public graph AML work is not limited to flattened snapshots.
- **15W** strengthens delayed-label, positive-unlabeled, threshold-drift, and time-window evaluation.
- **15X** frames Relaytic runs as evaluation environments with explicit workflow scorecards.
- **15Y** rewrites first-contact docs around the flagship AML path.
- **15Z** cleans credibility-damaging repo structure before broader capability growth resumes.
- **15Z-R** freezes the relevant benchmark and release evidence so public paper/demo claims are tied to reproducible artifacts instead of aspirational roadmap language.

If any of these slices discovers that Relaytic-AML loses, the correct output is a failure report and next experiment, not a broader claim.

## Required future artifacts

- `aml_domain_contract.json`
- `aml_case_ontology.json`
- `aml_review_budget_contract.json`
- `entity_graph_profile.json`
- `subgraph_risk_report.json`
- `typology_detection_report.json`
- `alert_queue_policy.json`
- `case_packet.json`
- `analyst_review_scorecard.json`
- `stream_risk_posture.json`
- `drift_recalibration_trigger.json`
- `weak_label_posture.json`
- `aml_benchmark_manifest.json`
- `aml_holdout_claim_report.json`
- `aml_demo_bundle_manifest.json`
- `aml_investigation_board.json`
- `aml_business_value_report.json`
- `aml_ablation_matrix.json`
- `aml_graph_loader_manifest.json`
- `aml_graph_provenance_report.json`
- `aml_subgraph_task_manifest.json`
- `aml_graph_claim_scope.json`
- `aml_public_graph_benchmark_catalog.json`
- `aml_delayed_label_eval_report.json`
- `aml_environment_scorecard.json`
- `aml_relevant_benchmark_catalog.json`
- `paper_release_freeze_manifest.json`
- `paper_benchmark_runbook.md`
- `paper_result_table.json`
- `paper_claim_boundary_report.json`
- `reproducibility_attestation.json`
- `release_attention_pack_manifest.json`

## Success criterion

Relaytic-AML is successful only if a strong technical reviewer can say:

- this is clearly built for a hard AML / fraud problem
- the architecture matches the problem
- the benchmark story is honest
- the review-budget and human-analyst economics are first-class
- the product is more than a general modeling shell with AML words pasted on top
- the paper/release benchmark pack covers relevant AML workload shapes and blocks claims when evidence is only synthetic, flattened, proxy, or incomplete
