# Paper Track P25 - Evidence disclosure and immutable release finalization

Status: implemented

## Purpose

P25 closes the last release risks without changing any reported benchmark value. It makes three distinctions explicit and mechanically checked: a validation-only selection protocol is not the same as an untouched test holdout, a published reference value is context rather than local parity evidence, and a review-budget result requires the threshold and queue provenance that produced it.

## Scope

1. Record PaySim P4/P6 prior test exposure alongside the P6-A validation-only competitive selection contract. The record must block untouched-holdout wording while preserving the measured result.
2. Store validation-threshold transfer, comparator, tie rule, partition size, positive count, reviewed count, precision, recall, and realized review fraction for each reader-facing operating point.
3. Pin the RevClassifyDS reference to the versioned RevTrack paper PDF, Table 1 location, DOI, access date, and SHA-256. The paper may use it only as external context.
4. Emit machine-readable execution statuses and make `--require-full-rerun` reject a skipped benchmark execution.
5. Require a local Git tag resolving to HEAD for the exact out-of-tree paper build. The generated manuscript, PDF, source bundle, and release manifest must agree on the tag and full commit hash.
6. Replace public job-search or promotional wording with external technical-review language.

## Release Procedure

1. Run the paper regeneration and validation sequence from a clean checkout.
2. Commit the reviewed source revision.
3. Create an annotated release tag at that commit.
4. Run:

```powershell
py -3.11 -m relaytic.ui.cli release-safety paper-release-integrity --final --release-tag relaytic-aml-arxiv-v1 --format json
```

5. Review the PDF and source bundle under `dist/paper-release/<full-commit>/` before uploading them to arXiv.

## Boundaries

P25 does not claim a real-bank AML result, detector novelty, graph-neural superiority, RevClassifyDS parity, or an untouched PaySim holdout. It does not alter benchmark measurements or rerun PaySim’s previously exposed test partition merely to update prose metadata.

## Acceptance Criteria

- The manuscript and machine artifacts disclose the PaySim test-exposure history.
- Operating-point audits recompute reported queue, precision, and recall from recorded counts.
- The versioned RevTrack reference provenance is present and correct.
- A final build fails for a dirty worktree, absent tag, or tag not resolving to HEAD.
- The final release manifest contains PDF/source SHA-256 hashes, tag, and full commit.
- Public prose contains no job-search framing.
