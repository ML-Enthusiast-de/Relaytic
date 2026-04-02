# Slice 13A - Release safety, build attestation, and packaging discipline

## Status

Implemented.

Intended package boundaries:

- `src/relaytic/release_safety/`
- extend `src/relaytic/runtime/`
- extend `src/relaytic/interoperability/`
- extend `scripts/`

Intended artifacts:

- `release_safety_scan.json`
- `distribution_manifest.json`
- `artifact_inventory.json`
- `artifact_attestation.json`
- `source_map_audit.json`
- `sensitive_string_audit.json`
- `release_bundle_report.json`
- `packaging_regression_report.json`

## Intent

Slice 13A is where Relaytic stops treating release hygiene as an ad hoc repo concern and turns it into a product contract.

This slice exists to prevent avoidable packaging leaks, hidden machine-path exposure, accidental debug artifacts, and distribution drift before Relaytic grows a larger remote, daemon, and approval surface.

This slice must continue obeying:

- `docs/specs/test_and_proof_matrix.md`
- `docs/specs/flagship_demo_pack.md`

## Load-Bearing Improvement

- Relaytic should be able to prove that a built distribution contains only the intended product surface and does not leak machine paths, debug files, source maps, hidden roadmap artifacts, or accidental sensitive strings

## Human Surface

- humans should be able to inspect one release-safety report that explains whether a build is safe to ship, what was scanned, what failed, and what must be fixed before a demo or public release

## Agent Surface

- external agents should be able to consume one machine-readable release-safety bundle and fail a release or packaging workflow without scraping prose or guessing what counts as a leak

## Intelligence Source

- built distributions, checked-in host bundles, packaging metadata, generated artifact inventories, git-safety rules, and explicit release policies

## Fallback Rule

- when a full packaged artifact is unavailable, Relaytic must still run the same release-safety checks against the local workspace and clearly mark the result as pre-release or workspace-only

## Required Behavior

- Slice 13A must upgrade the existing `scan-git-safety` posture into a real release-safety layer rather than leaving leak checks as a one-off repository utility
- release safety must scan built artifacts, checked-in host bundles, generated HTML, manifests, packaged docs, and install surfaces rather than only tracked source files
- release safety must explicitly detect:
  - machine paths
  - source maps
  - hidden internal URLs
  - oversized accidental payloads
  - obvious secret-like strings
  - debug-only manifests or roadmap-heavy internals that should not ship
- release attestation must prove which files were intentionally included in a build and which safety checks were run against them
- `relaytic doctor` and later richer mission-control packaging surfaces should consume release-safety posture rather than inventing separate health signals
- the release-safety layer must stay local-first by default and should never upload scanned bundle contents for remote analysis

## Proof Obligation

- Relaytic must prove that shipping safety is enforced by the product itself rather than by memory, convention, or last-minute manual review

## Acceptance Criteria

Slice 13A is acceptable only if:

1. one built distribution with an injected machine path is rejected with an explicit leak reason
2. one build with an injected source map or debug manifest is rejected with an explicit artifact path and reason
3. one clean build produces a complete attestation showing scanned files, passed checks, and the intended distribution contents
4. one host-bundle or docs surface is included in the release-safety scan so checked-in wrappers cannot bypass the packaging gate

## Required Verification

Slice 13A should not be considered complete without targeted tests that cover at least:

- one machine-path leak case
- one source-map or debug-file case
- one clean attested-build case
- one host-bundle or docs-bundle case
- one CLI-facing release-safety case
- one regression guard for accidental packaging drift
