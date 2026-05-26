# Paper Benchmark Data

Raw paper benchmark files live here locally and are intentionally ignored by git.

Expected first-track layout:

- `paysim/PS_20174392719_1491204439457_log.csv`
- `elliptic/elliptic_txs_classes.csv`
- `elliptic/elliptic_txs_edgelist.csv`
- `elliptic/elliptic_txs_features.csv`

Optional hard-track layouts evaluated by Paper Track P8:

- `elliptic2/background_edges.csv`, `elliptic2/background_nodes.csv`, `elliptic2/connected_components.csv`, `elliptic2/edges.csv`, `elliptic2/nodes.csv`
- `amlsim/conf.json`, `amlsim/tx_log.csv`, `amlsim/alert_transactions.csv`, `amlsim/sar_accounts.csv`
- `amlsim/generator_commit.txt` and `amlsim/generated_dataset_manifest.json`

Run `relaytic release-safety hard-graph-tracks --format json` to record whether these tracks are usable, proxy-only, or blocked. Source presence alone does not make Elliptic2 a supported benchmark, and AMLSim remains synthetic proxy evidence even after reproducible generation.

Use `docs/reports/paper_dataset_access_manifest.json` for source URLs, license posture, and setup notes.
