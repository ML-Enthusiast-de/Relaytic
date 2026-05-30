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
