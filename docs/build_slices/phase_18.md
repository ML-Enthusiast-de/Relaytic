# Slice 18 - Endgame consolidation, legacy removal, and repo-quality hardening

## Status

Planned.

Delivered package boundaries:

- cross-cutting cleanup across existing `src/relaytic/`, `docs/`, tests, and host bundles
- no new permanent package boundary by default

Intended artifacts:

- `legacy_surface_audit.json`
- `compatibility_removal_report.json`
- `module_split_report.json`
- `public_surface_inventory.json`
- `dead_code_removal_report.json`
- `repo_cleanup_scorecard.json`

## Intent

Slice 18 is the final repository-quality pass after the capability roadmap is complete.

Its job is to remove misleading legacy structure, retire stale compatibility surfaces, split oversized modules that still reflect build-history accumulation, and leave the repo reading like one coherent professional product.

## Load-Bearing Improvement

- Relaytic should end the roadmap with a cleaner, more intentional architecture instead of carrying temporary scaffolding, misleading package names, stale docs, and prototype-era wrappers forever

## Human Surface

- humans should encounter one clear public package map, one coherent CLI/help story, consistent docs, and fewer confusing duplicate concepts

## Agent Surface

- external agents should be able to navigate the repo, import the right modules, and call the right public surfaces without tripping over obsolete wrappers or misleading folder names

## Required Behavior

- remove or explicitly retire misleading legacy structure once it no longer has compatibility value
- split oversized `agents.py` or similarly overloaded modules where the split materially improves clarity and ownership
- delete dead code, duplicate helpers, and stale prototype wrappers when they no longer serve a real product contract
- preserve supported public CLI, artifact, and integration contracts unless the migration docs explicitly authorize a breaking change
- clean public docs, handbook language, and host-bundle guidance so the final repo does not read like an archaeological dig through earlier slices
- leave explicit cleanup scorecards and audit artifacts so the repo-quality gains are inspectable rather than hand-waved

## Acceptance Criteria

Slice 18 is acceptable only if:

1. one misleading or legacy package surface is removed or retired cleanly
2. one oversized module is split into clearer bounded files without reducing test coverage
3. one compatibility shim is either removed or given an explicit documented retention reason
4. one repo-wide public-surface inventory shows fewer confusing entry points than before
5. the final repo passes the broad proof wall, not just narrow targeted tests

## Required Verification

- full repo-wide `pytest -q`
- `relaytic doctor --expected-profile full --format json`
- `python -m relaytic.ui.cli scan-git-safety`
- `git diff --check`
- one install/bootstrap sanity check on Windows and one on macOS/Linux
