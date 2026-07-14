# Table 1. Evidence Summary

| Evidence row | Metric | Value | Claim posture |
|---|---:|---:|---|
| PaySim baseline | test PR-AUC | 0.3313 | baseline-only |
| PaySim competitive | test PR-AUC | 0.6388 | supporting-only synthetic temporal proxy |
| PaySim competitive | precision at review budget | 0.7033 | supporting-only |
| PaySim competitive | recall at review budget | 0.4716 | supporting-only |
| Elliptic graph-feature | test PR-AUC | 0.6688 | supporting-only graph-feature evidence |
| Elliptic graph-feature | precision at review budget | 1.0000 | supporting-only |
| Elliptic graph-feature | recall at review budget | 0.0566 | supporting-only |
| Elliptic2 context | provided RevTrack TST PR-AUC mean | 0.9432 | modern context only |
| Elliptic2 context | provided RevTrack TST PR-AUC std | 0.0009 | modern context only |
| RevClassifyDS reference | published PR-AUC | 0.9740 | reference context, not parity |

<!-- evidence-cells: paper-cell:paysim_p6_validation_selected_baseline.test_pr_auc paper-cell:paysim_p6a_competitive_selected.test_pr_auc paper-cell:paysim_p6a_competitive_selected.precision_at_review_budget paper-cell:paysim_p6a_competitive_selected.recall_at_review_budget paper-cell:elliptic_p7_selected_graph_feature_baseline.test_pr_auc paper-cell:elliptic_p7_selected_graph_feature_baseline.precision_at_review_budget paper-cell:elliptic_p7_selected_graph_feature_baseline.recall_at_review_budget paper-cell:elliptic2_p8b_modern_context.official_partition_test_pr_auc_mean paper-cell:elliptic2_p8b_modern_context.official_partition_test_pr_auc_std paper-cell:elliptic2_p8b_modern_context.published_reference_pr_auc -->

Exact evidence-cell identifiers and artifact fields are stored in the evidence-cell audit artifact named in the reproducibility section. None of these rows is a headline or hard AML claim.
