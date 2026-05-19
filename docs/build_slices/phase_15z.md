# Slice 15Z - Pre-Academy repo credibility cleanup

## Status

Implemented.

## Intent

Slice 15Z reduces credibility risk before Relaytic adds capability-academy surface area.

This slice should leave the repository clean enough that a benchmark reviewer can reproduce the AML path without reverse-engineering oversized modules, stale names, or hidden prototype-era assumptions.

## Load-Bearing Improvement

- the codebase looks easier to evaluate and maintain before it grows again.
- benchmark and release surfaces look intentional enough that the following paper-freeze slice can focus on evidence rather than repo archaeology.

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
- `benchmark_surface_cleanup_report.json`

## Acceptance Criteria

1. At least one oversized module is split without changing public behavior.
2. Public CLI and import-boundary smoke tests still pass.
3. Any retained oversized module has a documented extraction boundary.
4. Benchmark, demo, and public-claim commands are present in the public-surface inventory with no stale `corr2surrogate` expansion or prototype naming.
5. The benchmark-surface cleanup report lists any retained cleanup debt that could affect paper reproduction.

## Required Verification

- module-size audit
- import-boundary smoke test
- targeted public CLI regression
- benchmark surface inventory regression

## Implementation Notes

- extracted the `relaytic aml environment` execution helpers from the oversized CLI into `src/relaytic/ui/aml_environment.py` while preserving the public command surface
- added `src/relaytic/release_safety/repo_credibility.py` to build deterministic pre-Academy repo credibility reports
- materialized the required machine-readable reports under `docs/reports/`
- added Slice 15Z regression coverage for report presence, import-boundary smoke, public-surface inventory hygiene, module-split evidence, and retained benchmark cleanup debt
