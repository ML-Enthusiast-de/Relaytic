# Slice 15Z - Pre-Academy repo credibility cleanup

## Status

Planned.

## Intent

Slice 15Z reduces credibility risk before Relaytic adds capability-academy surface area.

## Load-Bearing Improvement

- the codebase looks easier to evaluate and maintain before it grows again.

## Human Surface

- operators and reviewers see a cleaner package map and public-surface inventory.

## Agent Surface

- external agents get a clearer import/module boundary map and fewer oversized entrypoints to reason about.

## Intelligence Source

- deterministic module-size audits
- import-boundary checks
- public-surface inventory
- targeted regression tests

## Fallback Rule

- if a large module cannot be safely split in one pass, Relaytic documents the retained responsibility and the next extraction boundary.

## Required Outputs

- `pre_academy_repo_audit.json`
- `module_extraction_plan.json`
- `public_surface_inventory.json`
- `module_split_report.json`

## Acceptance Criteria

1. At least one oversized module is split without changing public behavior.
2. Public CLI and import-boundary smoke tests still pass.
3. Any retained oversized module has a documented extraction boundary.

## Required Verification

- module-size audit
- import-boundary smoke test
- targeted public CLI regression

