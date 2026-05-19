# Relaytic-AML Paper Freeze Runbook

This generated runbook is the Slice 15Z-R machine-aligned release-freeze runbook.
It records the relevant benchmark families, the allowed claim posture, and the commands reviewers should use before treating a result as public evidence.

## Track Status

| Track | Type | Label | Hard claim | Current evidence |
| --- | --- | --- | --- | --- |
| paysim_temporal_transaction_fraud | transaction_fraud_temporal | `proxy` | `False` | dev_fixture_and_cli_path_supported |
| elliptic_flattened_graph_aml | graph_aml | `proxy` | `False` | flattened_graph_and_graph_loader_paths_supported |
| elliptic2_subgraph_aml | subgraph_aml | `blocked` | `False` | blocked_until_loader_data_access_and_claim_scope_are_reproducible |
| amlsim_synthetic_bank_graph | synthetic_bank_graph_aml | `blocked` | `False` | blocked_until_reproducible_generation_and_source_manifest_exist |
| generic_structured_supporting_pack | generic_supporting_structured_data | `dev` | `False` | supported_as_non_flagship_breadth_evidence |

## Reproducibility Commands

### install_full_profile

```powershell
python -m pip install -e ".[full]"
```

Install the same full dependency profile used by CI.

### generate_release_freeze_pack

```powershell
relaytic release-safety paper-freeze --format json
```

Regenerate the machine-readable paper/release freeze artifacts.

### run_release_safety_scan

```powershell
relaytic release-safety scan --format json
```

Verify release-safety posture before public use.

### run_aml_demo_path

```powershell
relaytic demo aml-review-queue --run-dir artifacts/relaytic_aml_demo --format json
```

Regenerate the public-safe demo path that anchors the product story.

### run_aml_environment_gate

```powershell
relaytic aml environment --run-dir artifacts/relaytic_aml_demo --format json
```

Regenerate model/environment score separation and benchmark-environment posture.

## Claim Rule

Hard AML performance or SOTA claims remain blocked unless the catalog row is labeled `paper`, the result table has numeric holdout metrics, the environment scorecard passes, and release-safety is clean.
