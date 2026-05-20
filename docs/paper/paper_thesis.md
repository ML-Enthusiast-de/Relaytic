# Relaytic-AML: Claim-Gated Evaluation Environments for Temporal Graph Financial-Crime ML

## Thesis

Relaytic-AML is a local-first, claim-gated evaluation environment for financial-crime ML. Its paper claim is not that a single model wins a leaderboard, but that AML evaluation becomes more credible when model metrics, temporal correctness, graph provenance, analyst-review utility, reproducibility, and public-claim boundaries are evaluated together.

## Primary Research Question

Can Relaytic-AML make temporal graph financial-crime evaluation more reproducible and less overclaimed by binding benchmark evidence, operational utility, and public claims to local artifacts?

## Research Questions

- **rq1_environment**: Can a local-first AML evaluation environment make model score, temporal correctness, graph provenance, analyst review utility, reproducibility, and public-claim safety inspectable together?
- **rq2_temporal_graph**: Can Relaytic-AML evaluate temporal transaction-fraud and graph AML workloads without collapsing proxy, flattened, raw-graph, and subgraph evidence into one overbroad claim?
- **rq3_operational**: Do review-budget, case-packet, and operational metrics change the interpretation of AML model quality compared with leaderboard-only metrics?
- **rq4_reproducibility**: Can the paper tables be regenerated from local artifacts with every metric cell tied to commands, datasets, splits, artifacts, and claim posture?

## Contributions

- **Claim-gated AML evaluation environment**: A local-first artifact system that keeps model metrics, temporal checks, graph provenance, operational utility, reproducibility, and public-claim boundaries in one inspectable contract.
- **Benchmark-track discipline for AML evidence**: A benchmark doctrine that separates PaySim-style proxy evidence, Elliptic-style graph evidence, Elliptic2-style subgraph evidence, AMLSim-style synthetic-bank evidence, and generic tabular breadth.
- **Operational AML metrics as first-class paper rows**: Review-budget, false-positive, analyst-capacity, and case-packet metrics are required alongside PR-AUC and precision-at-k before stronger AML claims are allowed.
- **Reproducible claim firewall**: Every public claim is tied to artifact paths and table provenance; unsupported SOTA and hard AML performance claims stay blocked until holdout evidence and gates pass.

## Benchmark Doctrine

- **paysim_temporal_transaction_fraud**: chronological split, rare-event metrics, threshold drift, review-budget metrics (supporting-only until holdout and paper gates pass).
- **elliptic_flattened_graph_aml**: graph provenance, raw-vs-flattened distinction, structural baseline comparison (supporting-only until raw graph, holdout, and claim-scope gates pass).
- **elliptic2_subgraph_aml**: subgraph AML relevance and future hard-track posture (blocked until access, loader, and claim-scope support are reproducible).
- **amlsim_synthetic_bank_graph**: seeded typology, synthetic-bank graph, and analyst-case workflow proof (blocked or proxy until generator and source manifest are frozen).
- **generic_structured_supporting_pack**: structured-data breadth context (supporting-only; cannot replace AML temporal, graph, or operational evidence).

## Claim Boundaries

- **claim_release_freeze_pack_exists**: `hard` - Relaytic-AML includes a local release-freeze pack that records benchmark relevance, reproducibility posture, and blocked claims.
- **claim_paysim_temporal_transaction_fraud**: `supporting-only` - PaySim-style evidence is a relevant proxy/dev workflow, not a hard real-world AML superiority result.
- **claim_elliptic_flattened_graph_aml**: `supporting-only` - Flattened Elliptic-style evidence is supporting proxy graph AML evidence until raw graph/holdout gates pass.
- **claim_sota_or_hard_aml_superiority**: `blocked` - Hard AML performance claims are blocked until a frozen holdout/paper track reports numeric evidence and all claim gates pass.
- **claim_generic_structured_supporting_pack**: `supporting-only` - Generic structured-data benchmark evidence is supporting breadth context and is not the flagship AML proof.
- **claim_subgraph_or_synthetic_bank_graph**: `blocked` - Subgraph and synthetic-bank graph tracks are cataloged and blocked until data access, loader support, and reproducible generation are frozen.

## Related-Work Seed

- **elliptic_bitcoin_aml_2019**: Anti-Money Laundering in Bitcoin: Experimenting with Graph Convolutional Networks for Financial Forensics - https://arxiv.org/abs/1908.02591
- **elliptic2_subgraph_2024**: The Shape of Money Laundering: Subgraph Representation Learning on the Blockchain with the Elliptic2 Dataset - https://arxiv.org/abs/2404.19109
- **amlsim_amlworld_neurips_2023**: Realistic Synthetic Financial Transactions for Anti-Money Laundering Models - https://research.ibm.com/publications/realistic-synthetic-financial-transactions-for-anti-money-laundering-models
- **paysim_2016**: PaySim: A financial mobile money simulator for fraud detection - https://www.diva-portal.org/smash/record.jsf?pid=diva2:1058442
- **tabpfn_nature_2025**: Accurate predictions on small data with a tabular foundation model - https://www.nature.com/articles/s41586-024-08328-6
- **dgraph_finance_graph_2022**: DGraph: A Large-Scale Financial Dataset for Graph Anomaly Detection - https://arxiv.org/abs/2207.03579
- **paperbench_2025**: PaperBench: Evaluating AI's Ability to Replicate AI Research - https://arxiv.org/abs/2504.01848
- **mlr_bench_2025**: MLR-Bench: Evaluating AI Agents on Open-Ended Machine Learning Research - https://arxiv.org/abs/2505.19955

## Non-Goals

- The paper must not claim global tabular SOTA.
- The paper must not claim hard AML superiority without numeric holdout evidence and passing gates.
- The paper must not treat synthetic, proxy, flattened, raw-graph, and subgraph evidence as interchangeable.

## Next Slice

Paper Track P3 must freeze dataset registry, access posture, split posture, hashes, and blocked reasons before any benchmark runner is treated as paper evidence.
