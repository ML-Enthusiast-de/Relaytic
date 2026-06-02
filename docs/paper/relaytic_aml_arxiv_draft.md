# Relaytic-AML: Claim-Gated Evaluation Environments for Temporal Graph Financial-Crime ML

P13 arXiv-ready draft. Add author metadata and institutional affiliation before submission.

## Abstract

Financial-crime machine learning is difficult to publish responsibly because the same number can mean very different things depending on temporal split discipline, graph provenance, review capacity, dataset realism, and public claim scope. Relaytic-AML is a local-first evaluation environment that treats those constraints as auditable first-class artifacts. It binds each paper metric cell to its dataset registry, split contract, command, artifact field, leakage posture, budget tier, and publishability gate, then lints the paper and public wording against those gates. In the current release pack, a competitive PaySim synthetic temporal-fraud row reports test PR-AUC 0.638773, and an Elliptic temporal graph-feature row reports test PR-AUC 0.668756; both are supporting evidence only. Elliptic2 subgraph evidence is retained as modern context only: the local repeated official-partition candidate reports PR-AUC 0.94324 +/- 0.000882, below the recorded RevClassifyDS reference of 0.974, and reference-parity plus cohort gates remain unresolved. The contribution is therefore not a detector superiority claim. It is a claim-gated, reproducible AML evaluation environment that makes benchmark evidence, operational review metrics, limitations, and public wording inspectable together.

## 1. Introduction

AML systems are operational decision systems, not just classifiers. Investigators need temporally valid predictions, graph or entity provenance, a calibrated review queue, and defensible statements about what the evidence does and does not prove. Public AML benchmarks make this harder because datasets vary across synthetic mobile-money simulation, transaction-level graph labels, and modern subgraph labels. A result that is useful on one track can be misleading if it is promoted as a broader real-world AML claim.

Relaytic-AML addresses this by turning the evaluation process itself into the object under test. The system records benchmark inputs, split rules, model-search budgets, leakage posture, operating points, review-budget estimates, figure provenance, and public-claim gates. The result is a paper package where the reader can inspect exactly why a row is allowed as supporting evidence and why stronger wording remains blocked.

The paper asks a systems question: can a local artifact-first evaluation environment make AML benchmark work more credible by preventing model scores, graph claims, operational claims, and public release text from drifting apart?

## 2. Contributions

This draft makes four contributions.

1. A claim-gated AML evaluation environment that stores benchmark and claim truth as deterministic local artifacts.
2. A reproducible table pipeline where every numeric paper cell cites dataset, split, command, run-directory reference, artifact field, budget tier, leakage posture, and claim state.
3. A release-safety layer that blocks public wording when clean-clone, claim-lint, leak-scan, or publishability gates fail.
4. A transparent first evidence pack over PaySim, Elliptic, and Elliptic2-context tracks that preserves limitations instead of converting proxy or blocked evidence into broader claims.

## 3. Related Work

PaySim is a synthetic mobile-money simulator designed to address the scarcity of legitimate public mobile-transaction datasets for fraud research [@lopezrojas2016paysim]. It is useful for temporal transaction-fraud workflow evaluation, but synthetic evidence cannot by itself establish hard real-bank AML performance.

The Elliptic Bitcoin dataset introduced a public transaction graph with more than 200K transaction nodes, 234K directed payment-flow edges, and 166 node features across 49 time steps [@weber2019elliptic]. That work also showed why graph evidence must be compared against strong simpler baselines rather than assumed superior.

Elliptic2 shifts the public AML benchmark center toward subgraph learning, with 121,810 labeled subgraphs inside a background graph of roughly 49M node clusters and 196M edge transactions [@bellei2024elliptic2]. RevTrack and RevClassify further argue that sender and receiver context around a subgraph can be a powerful and scalable signal [@song2024revtrack]. These works motivate Relaytic-AML's modern-context and limitation track, but they do not make the current Relaytic Elliptic2 row a performance contribution.

The paper also follows broader ML documentation and reproducibility practice. Datasheets for Datasets and Model Cards argue for explicit dataset and model reporting [@gebru2021datasheets; @mitchell2019modelcards]. The NeurIPS reproducibility program highlights the need for code, data, and checklist discipline in ML research [@pineau2021reproducibility]. Recent work on ML research agents warns that coherent papers can still contain invalidated experiments, reinforcing the need for executable artifacts and claim gates [@chen2025mlrbench].

## 4. Relaytic-AML Evaluation Environment

Relaytic-AML is organized as a deterministic local evidence pipeline. Dataset registry artifacts define source and access posture. Split contracts define chronological, graph-snapshot, or subgraph partition rules. Benchmark runners produce model and operating-point artifacts. Paper-table generation consumes those artifacts and writes per-cell provenance. Draft generation and P13 release generation then lint wording against publishability gates.

The environment has three design rules.

1. Local artifacts are the source of truth. Narrative text is derived from artifacts, not the reverse.
2. Validation selects models, thresholds, and operating points before fixed test evaluation.
3. Blocked evidence stays visible as a limitation, because hiding failed or incomplete tracks makes the paper less scientific.

![Relaytic-AML claim-gated evidence flow](figures/figure_1_claim_gate_flow.svg)

*Relaytic-AML claim-gated evidence flow.* Role: `method_schematic_not_performance_evidence`.

![Supporting PR-AUC rows with claim posture](figures/figure_2_supporting_pr_auc.svg)

*Supporting PR-AUC rows with claim posture.* Role: `supporting_numeric_evidence_only`.

![Review-budget precision and recall](figures/figure_3_review_budget.svg)

*Review-budget precision and recall.* Role: `supporting_operational_evidence_only`.

![Publishability gate posture by track](figures/figure_4_publishability_matrix.svg)

*Publishability gate posture by track.* Role: `claim_gate_evidence`.

## 5. Benchmark Protocol

The current release pack separates smoke, baseline, competitive, and release budgets. Smoke checks prove that commands and artifacts exist. Baseline budgets establish conservative full-dataset evidence where possible. Competitive budgets use stronger features, candidate families, calibration, and validation-only operating-point selection. Release budgets freeze the paper transformation path and require clean-clone and leak-scan proof.

PaySim is treated as a synthetic temporal proxy. Elliptic is treated as temporal graph-feature supporting evidence. Elliptic2 is treated as modern subgraph context and limitation evidence, because the current local environment has not executed faithful RevClassify parity and the current-core to RevTrack-evaluable cohort boundary is not fully proven.

| Evidence row | Metric | Value | Claim posture | Provenance |
|---|---:|---:|---|---|
| PaySim baseline | test PR-AUC | 0.331345 | baseline-only | `paper-cell:paysim_p6_validation_selected_baseline.test_pr_auc` |
| PaySim competitive | test PR-AUC | 0.638773 | supporting-only synthetic temporal proxy | `paper-cell:paysim_p6a_competitive_selected.test_pr_auc` |
| PaySim competitive | precision at review budget | 0.703336 | supporting-only | `paper-cell:paysim_p6a_competitive_selected.precision_at_review_budget` |
| PaySim competitive | recall at review budget | 0.471584 | supporting-only | `paper-cell:paysim_p6a_competitive_selected.recall_at_review_budget` |
| Elliptic graph-feature | test PR-AUC | 0.668756 | supporting-only graph-feature evidence | `paper-cell:elliptic_p7_selected_graph_feature_baseline.test_pr_auc` |
| Elliptic graph-feature | precision at review budget | 1 | supporting-only | `paper-cell:elliptic_p7_selected_graph_feature_baseline.precision_at_review_budget` |
| Elliptic graph-feature | recall at review budget | 0.056604 | supporting-only | `paper-cell:elliptic_p7_selected_graph_feature_baseline.recall_at_review_budget` |
| Elliptic2 context | official-partition PR-AUC mean | 0.94324 | modern context only | `paper-cell:elliptic2_p8b_modern_context.official_partition_test_pr_auc_mean` |
| Elliptic2 context | official-partition PR-AUC std | 0.000882 | modern context only | `paper-cell:elliptic2_p8b_modern_context.official_partition_test_pr_auc_std` |
| RevClassifyDS reference | published PR-AUC | 0.974 | reference context, not parity | `paper-cell:elliptic2_p8b_modern_context.published_reference_pr_auc` |

All values are generated from `docs/reports/paper_metric_cell_audit.json`; none is a headline or hard AML claim.


## 6. Results

The PaySim competitive row improves over the PaySim baseline inside the recorded synthetic temporal-fraud contract. The Elliptic graph-feature row is supporting graph evidence with modest structural lift, not graph-neural superiority. The Elliptic2 context row is strong enough to motivate future reprovisioning, but not enough to claim parity with the RevClassifyDS reference or to make an Elliptic2 performance contribution.

| Track | Supporting table | Headline claim | Hard claim | Gate status | Gate limitation notes |
|---|---:|---:|---:|---|---|
| paysim_temporal_transaction_fraud | yes | no | no | pass_supporting_only | paysim_is_supporting_proxy_not_real_bank_holdout, release_budget_and_clean_clone_proof_not_executed |
| elliptic_flattened_graph_aml | yes | no | no | pass_supporting_only | headline_graph_claim_requires_release_budget_and_repeated_seed_proof, graph_sota_claim_not_benchmarked, hard_aml_claim_requires_broader_holdout_and_operational_proof, graph_neural_shadow_candidate_not_promoted |
| elliptic2_subgraph_aml | yes | no | no | pass_supporting_modern_context_only | official_test_partition_was_exposed_during_p8a, entity_disjoint_generalization_not_yet_proven |
| elliptic2_subgraph_aml | yes | no | no | blocked_supporting_only_thesis_narrowing_required | full_core_row_mapping_not_proven, local_accelerator_not_available_for_faithful_revclassify_budget, official_revclassify_classification_checkpoints_not_distributed, official_revclassify_dependency_hydra-core_missing, official_revclassify_dependency_lightning_missing, official_revclassify_dependency_omegaconf_missing, +4 more |
| paper_operational_layer | yes | no | no | supporting_operational_metrics_ready_hard_claims_blocked | paper_benchmark_case_packets_missing, analyst_hour_assumption_defaulted, same_queue_incumbent_or_human_baseline_missing, operational_metrics_supporting_only_not_hard_claims, elliptic2_excluded_from_operational_performance_contribution_by_p8d |


## 7. Discussion

The practical value of Relaytic-AML is not that it replaces a compliance platform. Its value is that it can give risk, fraud, or AML teams a local evidence lab for unknown datasets, incumbent challenges, review-budget tradeoffs, leakage checks, and public-claim discipline. A company evaluating a new dataset can inspect whether the result is a model win, an environment win, a proxy-only result, or a blocked claim. That distinction is often what separates a useful internal experiment from an unsafe public or deployment claim.

For technical hiring or research review, the strongest story is the artifact discipline: Relaytic-AML demonstrates that an agentic evaluation system can be ambitious while still refusing claims it has not earned.

## 8. Limitations

- **LIM-01-paysim-proxy**: PaySim is synthetic mobile-money fraud evidence. It is useful for a temporal proxy workflow, but it is not real-bank AML superiority evidence. Required repair: Add a real financial-crime holdout or partner-approved private evaluation before making hard AML claims.
- **LIM-02-elliptic-supporting-graph**: The Elliptic row is a supporting temporal graph-feature result. It does not prove graph-neural or graph-SOTA superiority. Required repair: Run repeated-seed graph baselines and promote a graph-native candidate only if it beats strong feature baselines under the same split.
- **LIM-03-elliptic2-context-only**: Elliptic2 is retained as modern context and limitation evidence only; it is not a Relaytic performance contribution in this paper. Required repair: Reproduce a faithful RevClassify parity run or define a new leakage-resistant subgraph protocol with viable cohort proof.
- **LIM-04-operational-assumptions**: Operational review-budget rows are supporting estimates because aggregate case packets, same-queue incumbent comparisons, and analyst-hour assumptions are not fully frozen. Required repair: Freeze case-packet completeness and compare against the same review queue or an approved incumbent baseline.
- **LIM-05-clean-clone-smoke-scope**: P12 clean-clone and paper-smoke proof now passes for the generated paper path, including install-readiness checks, P10/P11 smoke regeneration, leak scan, and reproduction failure reporting. The remaining limitation is scope: heavy external-local benchmark reruns are documented but not rerun inside the P12 smoke proof. Required repair: run the heavy benchmark commands under a frozen release budget before promoting hard or headline benchmark claims.

## 9. Reproducibility

The P13 package is generated from P10-P12 artifacts. The clean-clone proof records install readiness, paper-smoke regeneration, claim lint, leak scan, and failure reporting. The final public wording is constrained by `docs/reports/paper_public_claims_allowed.json`.

| Artifact | Present | Role |
|---|---:|---|
| `docs/reports/paper_result_table_final.json` | yes | P10-P12 gate input |
| `docs/reports/paper_metric_cell_audit.json` | yes | P10-P12 gate input |
| `docs/reports/paper_publishability_matrix.json` | yes | P10-P12 gate input |
| `docs/reports/paper_claim_lint_report.json` | yes | P10-P12 gate input |
| `docs/reports/paper_external_dry_run_report.json` | yes | P10-P12 gate input |
| `docs/reports/paper_reproduction_failure_report.json` | yes | P10-P12 gate input |
| `docs/reports/paper_release_go_no_go.json` | yes | P10-P12 gate input |
| `docs/paper/relaytic_aml_draft.md` | yes | paper draft or figure input |
| `docs/paper/figures/figure_manifest.json` | yes | paper draft or figure input |
| `docs/paper/figures/figure_1_claim_gate_flow.svg` | yes | paper draft or figure input |
| `docs/paper/figures/figure_2_supporting_pr_auc.svg` | yes | paper draft or figure input |
| `docs/paper/figures/figure_3_review_budget.svg` | yes | paper draft or figure input |
| `docs/paper/figures/figure_4_publishability_matrix.svg` | yes | paper draft or figure input |


Core reproduction commands:

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

P13 release command:

```powershell
relaytic release-safety paper-release --format json
relaytic scan-git-safety
```

## 10. Conclusion

Relaytic-AML should be read as a claim-gated AML evaluation-environment paper. The current evidence pack is useful and publishable in that systems sense: it has real numeric supporting rows, modern benchmark context, deterministic figures, limitations, clean-clone proof, and public wording gates. The same evidence does not support a hard AML superiority, headline benchmark, graph-neural superiority, RevClassify parity, or hard business-value claim. That restraint is part of the contribution.

## References

- Lopez-Rojas, E. A., Elmir, A., and Axelsson, S. (2016). PaySim: A Financial Mobile Money Simulator for Fraud Detection. European Modeling and Simulation Symposium.
- Weber, M., Domeniconi, G., Chen, J., Weidele, D. K. I., Bellei, C., Robinson, T., and Leiserson, C. E. (2019). Anti-Money Laundering in Bitcoin. arXiv:1908.02591.
- Bellei, C., Xu, M., Phillips, R., Robinson, T., Weber, M., Kaler, T., Leiserson, C. E., Arvind, and Chen, J. (2024). The Shape of Money Laundering. arXiv:2404.19109.
- Song, K., Dhraief, M. A., Xu, M., Cai, L., Chen, X., Arvind, and Chen, J. (2024). Identifying Money Laundering Subgraphs on the Blockchain. ICAIF 2024.
- Gebru, T. et al. (2021). Datasheets for Datasets. Communications of the ACM.
- Mitchell, M. et al. (2019). Model Cards for Model Reporting. FAT* 2019.
- Pineau, J. et al. (2021). Improving Reproducibility in Machine Learning Research. JMLR.
- Chen, H. et al. (2025). MLR-Bench: Evaluating AI Agents on Open-Ended Machine Learning Research. arXiv:2505.19955.
