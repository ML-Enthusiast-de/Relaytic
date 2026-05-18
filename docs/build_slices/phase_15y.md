# Slice 15Y - Demo-first documentation rewrite

## Status

Implemented.

## Intent

Slice 15Y makes first contact demo-led instead of roadmap-led.

This slice must also make the benchmark path legible: a technical reviewer should be able to run the flagship demo, then find the exact command and artifact path for the relevant benchmark pack.

## Load-Bearing Improvement

- a new reader can understand the AML path, run the demo, inspect the case packet, inspect benchmark/public-claim guards, and inspect trace/evals before learning the full slice history.
- first-contact docs should name which benchmark claims are demo-only, dev-benchmark, holdout-benchmark, or paper-ready.

## Human Surface

- README and handbooks point to one flagship AML path first.

## Agent Surface

- agent handbooks expose one command-first AML demo path and the proof artifacts to inspect.

## Intelligence Source

- documentation structure
- product-story artifacts
- proof links

## Fallback Rule

- if a demo artifact is not generated yet, docs say which slice generates it instead of pretending it exists.

## Required Outputs

- `docs/relaytic_ui_frontier_review.md`
- `docs/why_relaytic_aml.md`
- `docs/product_story.md`
- `docs/paper_benchmark_runbook.md`
- README flagship path rewrite
- handbook demo-path updates

## Acceptance Criteria

1. README names the next command for a new operator.
2. Docs link to AML proof artifacts without overstating support.
3. Slice history moves behind the demo-led first-contact story.
4. Mission-control docs distinguish the static fallback, AML investigation board, agent console, and later local live UI server.
5. The paper benchmark runbook names the public benchmark families, expected artifacts, blocked-claim conditions, and reproducibility command sequence.

## Required Verification

- docs link check for new AML story files
- handbook command-surface regression
- README proof-path review
- paper benchmark runbook review

## Implementation Notes

- Added `docs/why_relaytic_aml.md`, `docs/product_story.md`, and `docs/paper_benchmark_runbook.md`.
- Reworked the top of `README.md` around the public-safe AML demo command, proof artifacts, and claim-boundary labels before the slice history.
- Updated the user, agent, and demo handbooks with the flagship AML demo path and artifact checklist.
- Updated `docs/relaytic_ui_frontier_review.md` to distinguish the static fallback, AML investigation board, Agent Console, and future local live UI server.
