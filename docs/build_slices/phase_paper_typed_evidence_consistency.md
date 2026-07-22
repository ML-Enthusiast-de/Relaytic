# Paper Track P27 - Typed evidence and release-candidate consistency

Status: implemented

## Goal

P27 removes the remaining ambiguity between detector measurements and deterministic system checks. It also makes candidate and archival release states truthful without changing any benchmark value.

## Required behavior

1. Metric observations and system invariants use separate typed schemas over one common factual provenance base.
2. Invariant records cannot carry detector metric or value fields. Neither factual type can contain interpretation fields.
3. Required-field and missing-field fixture counts come from one generated schema contract.
4. PaySim P6 and P6-A are compared under the same dataset, temporal split, and metric while their distinct feature contracts remain visible.
5. The RevClassifyDS value is an external published reference with source-scorecard provenance, not a locally generated Relaytic result.
6. Candidate manuscripts claim no source revision. Final mode requires a clean commit and verifies generated surfaces plus TeX/PDF revision identity.

## Evidence boundary

P27 does not retrain a detector, alter benchmark numbers, establish RevClassifyDS parity, claim an untouched PaySim holdout, create a Git tag, push a commit, or upload to arXiv.

## Minimum proof

- negative schema tests reject untyped, incomplete, conflated, and interpretive factual records
- generated schema, metric audit, ablation, and missing-field fixture counts reconcile
- generated manuscript and SVG figures match their source generators
- candidate release reports no archival revision and all integrity checks pass
- final mode rejects a dirty worktree and verifies one full commit in source and PDF
