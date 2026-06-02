# Table 1. Evidence Summary

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
