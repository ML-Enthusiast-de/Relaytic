# Why Relaytic-AML

Relaytic-AML is the flagship proof path for Relaytic: a local-first AML and financial-crime investigation system that treats the workflow around a model as part of the thing being evaluated.

The useful claim is not "we trained a fraud classifier." The useful claim is:

- Relaytic can inspect messy AML-style data locally.
- Relaytic can turn the run into auditable artifacts.
- Relaytic can rank alerts and produce a case packet under review-budget pressure.
- Relaytic can separate model score from analyst workflow value.
- Relaytic can keep weak-label, delayed-label, drift, graph, and public-claim limits visible.
- Relaytic can tell a human or an external agent what to inspect next without assuming repo literacy.

## The Fastest Honest Demo

Run the public-safe review-queue demo:

```powershell
relaytic demo aml-review-queue --run-dir artifacts\relaytic_aml_demo --format json
relaytic mission-control launch --run-dir artifacts\relaytic_aml_demo
```

Then inspect:

```powershell
relaytic show --run-dir artifacts\relaytic_aml_demo --format json
relaytic aml environment --run-dir artifacts\relaytic_aml_demo --format json
relaytic guide export-context --run-dir artifacts\relaytic_aml_demo --audience external-llm --format json
```

## Proof Artifacts

The demo and AML run surfaces should point reviewers to these rowless artifacts:

- `aml_demo_bundle_manifest.json`
- `aml_demo_business_metric_table.json`
- `aml_demo_artifact_index.json`
- `case_packet.json`
- `alert_queue_rankings.json`
- `analyst_review_scorecard.json`
- `aml_business_value_report.json`
- `operational_metric_guard.json`
- `aml_baseline_matrix.json`
- `aml_ablation_matrix.json`
- `aml_benchmark_relevance_scorecard.json`
- `aml_temporal_benchmark_claim_report.json`
- `aml_environment_scorecard.json`
- `aml_workflow_task_matrix.json`
- `aml_benchmark_environment_scorecard.json`
- `aml_public_claim_guard.json`
- `benchmark_release_gate.json`

## What This Does Not Claim Yet

The public-safe demo is demo-only. It can show the workflow and artifact contract, but it does not prove paper-grade AML benchmark superiority.

The implemented release-freeze and paper evidence packs require:

- named AML benchmark-family coverage
- a reproducible command sequence
- benchmark-truth and leakage gates
- operational business-value guard
- AML environment scorecard
- public claim-boundary report
- release-safety scan

Those gates agree for the current supporting claims. Publishing the reviewed
commit and submitting its exact-revision bundle remain human release actions.
