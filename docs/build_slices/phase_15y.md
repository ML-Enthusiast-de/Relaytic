# Slice 15Y - Demo-first documentation rewrite

## Status

Planned.

## Intent

Slice 15Y makes first contact demo-led instead of roadmap-led.

## Load-Bearing Improvement

- a new reader can understand the AML path, run the demo, inspect the case packet, inspect benchmark/public-claim guards, and inspect trace/evals before learning the full slice history.

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
- README flagship path rewrite
- handbook demo-path updates

## Acceptance Criteria

1. README names the next command for a new operator.
2. Docs link to AML proof artifacts without overstating support.
3. Slice history moves behind the demo-led first-contact story.
4. Mission-control docs distinguish the static fallback, AML investigation board, agent console, and later local live UI server.

## Required Verification

- docs link check for new AML story files
- handbook command-surface regression
- README proof-path review
