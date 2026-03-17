# Slice 01 - Contracts and Scaffolding

## Goal

Add the minimum Relaytic package scaffolding required for a stable MVP build path.

## Expected Outputs

- installable package shell
- `relaytic --help`
- manifest helper
- policy loader stub

## Implemented In This Slice

- `src/relaytic/artifacts/manifests.py`
- `src/relaytic/policies/loader.py`
- `relaytic manifest init`
- `relaytic policy resolve`
- targeted tests for deterministic scaffolding and local stub LLM integration

## Done Criteria

- CLI help works without importing heavyweight runtime modules
- `manifest.json` can be created in a run directory
- `policy_resolved.yaml` can be materialized from a config source
- new scaffolding commands are covered by tests
