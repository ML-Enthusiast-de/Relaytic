# Relaytic-AML: Claim-Gated Evaluation Environments for Temporal Graph Financial-Crime ML

Source-draft status: generated evidence draft used by the release pipeline. For reader-facing review, use `docs/paper/relaytic_aml_arxiv_draft.md`.

## Abstract

Financial-crime machine learning is often evaluated through isolated model scores, while the operational question involves temporal validity, graph provenance, review capacity, case evidence, and public claim discipline. Relaytic-AML is a local-first evaluation environment that binds each benchmark row to a dataset registry, split contract, command, artifact path, leakage posture, budget tier, and publishability gate. In the current evidence pack, PaySim synthetic temporal-fraud and Elliptic temporal graph results are supporting rows, not headline superiority claims. The PaySim competitive row reports test PR-AUC 0.6388 and the Elliptic graph-feature row reports test PR-AUC 0.6688; both are explicitly claim-guarded. Elliptic2 subgraph evidence is retained as modern context and limitation evidence only because reference-parity and cohort gates remain unresolved. The contribution is an auditable environment for claim-safe AML evaluation, not a detector-superiority claim.

## Introduction

AML and fraud detection systems are rare-event decision systems, not only classifiers. A model can look strong under a single metric while still being unusable if the split leaks future information, if graph evidence is flattened into an overbroad claim, if review capacity is ignored, or if paper text drifts beyond what the benchmark actually proves. Relaytic-AML treats those failure modes as first-class evaluation objects.

This source draft argues for a claim-gated evaluation environment. Each numeric cell in the result table is tied to a command, dataset, split, run-directory reference, artifact field, budget tier, leakage posture, and claim state. Public claims are allowed only when the evidence pack and publishability gates agree. The current package allows supporting evidence claims and blocks hard AML, headline performance, and hard business-value claims.

The paper therefore asks whether a local artifact system can make AML evaluation more credible by keeping model score, temporal correctness, graph provenance, operational review utility, and public claim boundaries inspectable together.

## Related Work

Relaytic-AML sits between AML benchmark papers, synthetic financial-crime data, modern tabular and graph baselines, and research reproducibility work. The related-work seed is intentionally artifact-backed so the paper can be refreshed without turning literature context into unsupported authority.

| Source | Role in this paper |
|---|---|
| [Anti-Money Laundering in Bitcoin: Experimenting with Graph Convolutional Networks for Financial Forensics](https://arxiv.org/abs/1908.02591) | Anchor for Elliptic-style temporal graph AML evidence and the need to compare graph methods against strong simpler baselines. |
| [The Shape of Money Laundering: Subgraph Representation Learning on the Blockchain with the Elliptic2 Dataset](https://arxiv.org/abs/2404.19109) | Justifies treating the hardest AML graph track as subgraph-centric and blocking claims until subgraph support is reproducible. |
| [Realistic Synthetic Financial Transactions for Anti-Money Laundering Models](https://research.ibm.com/publications/realistic-synthetic-financial-transactions-for-anti-money-laundering-models) | Supports a synthetic-bank graph track while keeping synthetic evidence separate from hard real-world AML superiority claims. |
| [PaySim: A financial mobile money simulator for fraud detection](https://www.diva-portal.org/smash/record.jsf?pid=diva2:1058442) | Supports the PaySim-style temporal transaction-fraud proxy track and its synthetic-source caveat. |
| [Accurate predictions on small data with a tabular foundation model](https://www.nature.com/articles/s41586-024-08328-6) | Motivates evaluating modern tabular baselines instead of comparing only against older local models. |
| [DGraph: A Large-Scale Financial Dataset for Graph Anomaly Detection](https://arxiv.org/abs/2207.03579) | Provides adjacent dynamic financial-graph benchmark pressure while staying separate from AML-specific claims until data access and task posture are frozen. |
| [PaperBench: Evaluating AI's Ability to Replicate AI Research](https://arxiv.org/abs/2504.01848) | Motivates machine-readable reproduction commands, table provenance, and claim linting. |
| [MLR-Bench: Evaluating AI Agents on Open-Ended Machine Learning Research](https://arxiv.org/abs/2505.19955) | Reinforces that research systems should expose executable evidence rather than narrative-only claims. |

## Method

Relaytic-AML is organized as a local evidence pipeline rather than a single model family. The pipeline records a dataset registry and split contracts, runs benchmark-specific evidence builders, materializes operational review-budget rows, generates paper tables from artifacts, and then lints draft claims against the claim taxonomy and publishability matrix.

The method has four claim-control rules:

1. Proxy, graph, subgraph, and synthetic-bank tracks keep separate claim boundaries.
2. Validation selects models, thresholds, and operating points before fixed test evaluation.
3. Numeric paper cells must cite machine-readable provenance rather than handwritten notes.
4. Blocked tracks stay visible as limitations instead of being replaced by easier evidence.

![Relaytic-AML local-first architecture: local data and artifacts flow through role-scoped agents into evidence cells, claim gates, and paper/release/handoff surfaces.](figures/figure_1_claim_gate_flow.svg)

![Evidence-cell schema: every reported number carries dataset, split, command, artifact, budget, leakage posture, operating point, metric, and claim state.](figures/figure_2_supporting_pr_auc.svg)

![Benchmark and review-budget evidence: PR-AUC is shown beside precision and recall at the bounded review queue instead of being interpreted alone.](figures/figure_3_review_budget.svg)

![Claim-gate examples: allowed claims, blocked promotions, and evidence needed before stronger public interpretations.](figures/figure_4_publishability_matrix.svg)

## Benchmarks

| Track | Role | Budget | Claim state | Gate |
|---|---|---|---|---|
| PaySim synthetic mobile-money transaction fraud | baseline_reference_appendix | baseline | baseline_only_not_headline | blocked |
| PaySim synthetic mobile-money transaction fraud | supporting_temporal_proxy_numeric_candidate | competitive | supporting-only | pass_supporting_only |
| Elliptic Bitcoin temporal graph | supporting_temporal_graph_numeric_candidate | competitive | supporting-only | pass_supporting_only |
| paysim_temporal_transaction_fraud | supporting_operational_proxy_only | operational_evaluation | supporting-only | supporting_operational_metrics_ready_hard_claims_blocked |
| elliptic_flattened_graph_aml | supporting_graph_operational_metric_only | operational_evaluation | supporting-only | supporting_operational_metrics_ready_hard_claims_blocked |
| Elliptic2 subgraph AML | supporting_modern_context_only | competitive_context | supporting_context_only_not_performance_contribution | pass_supporting_modern_context_only |
| Elliptic2 subgraph AML | limitation_and_claim_firewall | reference_parity_gate | blocked_claim_evidence | blocked_supporting_only_thesis_narrowing_required |
| AMLSim synthetic bank graph | blocked_pending_reproducible_generation | blocked | blocked_or_future_proxy | hard_tracks_blocked_with_p8d_thesis_narrowing_accepted |

## Results

The current result table is intentionally supporting-only. It is useful because it shows where Relaytic-AML can produce leakage-aware, operationally annotated evidence, and where it refuses to overclaim.

| Evidence row | Metric | Value | Claim posture | Provenance |
|---|---:|---:|---|---|
| PaySim baseline | test PR-AUC | 0.3313 | baseline-only | `paper-cell:paysim_p6_validation_selected_baseline.test_pr_auc` |
| PaySim competitive | test PR-AUC | 0.6388 | supporting-only | `paper-cell:paysim_p6a_competitive_selected.test_pr_auc` |
| PaySim competitive | precision at review budget | 0.7033 | supporting-only | `paper-cell:paysim_p6a_competitive_selected.precision_at_review_budget` |
| PaySim competitive | recall at review budget | 0.4716 | supporting-only | `paper-cell:paysim_p6a_competitive_selected.recall_at_review_budget` |
| Elliptic graph-feature | test PR-AUC | 0.6688 | supporting-only | `paper-cell:elliptic_p7_selected_graph_feature_baseline.test_pr_auc` |
| Elliptic graph-feature | precision at review budget | 1 | supporting-only | `paper-cell:elliptic_p7_selected_graph_feature_baseline.precision_at_review_budget` |
| Elliptic2 context | official-partition PR-AUC mean | 0.9432 | modern context only | `paper-cell:elliptic2_p8b_modern_context.official_partition_test_pr_auc_mean` |
| Elliptic2 context | published RevClassifyDS PR-AUC | 0.974 | reference context | `paper-cell:elliptic2_p8b_modern_context.published_reference_pr_auc` |

The PaySim competitive result improved over the PaySim baseline under the recorded temporal proxy contract, but PaySim remains synthetic. The Elliptic graph-feature result is credible supporting graph evidence, but it does not promote a graph-neural claim. The Elliptic2 context row shows a strong reproduced local candidate relative to many ordinary baselines, yet it remains below the recorded RevClassifyDS reference and cannot support a parity or headline detector claim in this source draft.

## Limitations

- **LIM-01-paysim-proxy**: PaySim is synthetic mobile-money fraud evidence. It is useful for a temporal proxy workflow, but it is not real-bank AML superiority evidence. Required repair: Add a real financial-crime holdout or partner-approved private evaluation before making hard AML claims.
- **LIM-02-elliptic-supporting-graph**: The Elliptic row is a supporting temporal graph-feature result. It does not prove graph-neural or graph benchmark superiority. Required repair: Run repeated-seed graph baselines and promote a graph-native candidate only if it beats strong feature baselines under the same split.
- **LIM-03-elliptic2-context-only**: Elliptic2 is retained as modern context and limitation evidence only; it is not a Relaytic performance contribution in this paper. Required repair: Reproduce the RevClassify reference setup faithfully or define a new leakage-resistant subgraph protocol with viable cohort proof.
- **LIM-04-operational-assumptions**: Operational review-budget rows are supporting estimates because aggregate case packets, same-queue incumbent comparisons, and analyst-hour assumptions are not fully frozen. Required repair: Freeze case-packet completeness and compare against the same review queue or an approved incumbent baseline.
- **LIM-05-clean-clone-pending**: The first draft is generated from committed evidence, but P12 must still prove clean-clone install, paper-smoke reproduction, leak scan, and claim lint. Required repair: Run Paper Track P12 from a clean clone and record the external dry-run report before arXiv release.

## Reproducibility Appendix

The draft, figures, tables, limitations matrix, and claim-lint report are generated from local artifacts. The core P10 command sequence is:

# Paper P10 Reproduction Commands

Run from the repository root. External-local dataset paths are intentionally placeholders when the source is not committed.

```powershell
relaytic release-safety paysim-benchmark --format json
relaytic release-safety elliptic-graph --format json
relaytic release-safety tabular-baselines --budget-tier baseline --run-optional --format json
relaytic release-safety paysim-competitive --budget-tier competitive --run-optional --format json
relaytic release-safety graph-baselines --budget-tier competitive --run-optional --format json
relaytic release-safety hard-graph-tracks --format json
relaytic release-safety elliptic2-recovery --core-data-dir <external-local-core-dir> --revtrack-dir <external-local-revtrack-dir> --prepare-selected-embeddings --run-pilot --hash-large-assets --format json
relaytic release-safety elliptic2-competitive --revtrack-dir <external-local-revtrack-dir> --budget-tier competitive --run-suite --format json
relaytic release-safety elliptic2-reference-parity --revtrack-dir <external-local-revtrack-dir> --run-neural --format json
relaytic release-safety paper-thesis-decision --format json
relaytic release-safety paper-operational-metrics --format json
relaytic release-safety paper-tables --format json
```

- Table status: `tables_generated_claim_guarded`
- Metric audit status: `pass`
- P9 dependency: `supporting_operational_metrics_ready_hard_claims_blocked`
- Paper may continue to P11: `True`

The P11 generation command is:

```powershell
relaytic release-safety paper-draft --format json
```

Important artifact references:

- `docs/reports/paper_result_table_final.json`
- `docs/reports/paper_table_provenance.json`
- `docs/reports/paper_metric_cell_audit.json`
- `docs/reports/paper_publishability_matrix.json`
- `docs/reports/paper_claim_lint_report.json`
- `docs/reports/paper_limitations_matrix.json`

Allowed non-blocked claim IDs in this draft: claim_release_freeze_pack_exists, claim_paysim_temporal_transaction_fraud, claim_elliptic_flattened_graph_aml, claim_generic_structured_supporting_pack.
Hard claims allowed by the P10/P11 gates: False.
Headline claims allowed by the P10/P11 gates: False.
