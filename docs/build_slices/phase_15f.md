# Slice 15F - Research-imported architecture candidates and shadow trials

## Status

Planned.

Delivered package boundaries:

- extend `src/relaytic/research/`
- extend `src/relaytic/compiler/`
- extend `src/relaytic/benchmark/`
- extend `src/relaytic/search/`

Intended artifacts:

- `architecture_candidate_registry.json`
- `method_import_report.json`
- `shadow_trial_manifest.json`
- `shadow_trial_scorecard.json`
- `candidate_quarantine.json`
- `promotion_readiness_report.json`

## Intent

Slice 15F gives Relaytic a governed path for learning new model families from publications, web research, and adapter discovery without turning the core router into a chaotic self-modifying system.

This slice is model-family specific and deliberately narrower than the later full academy track.

## Load-Bearing Improvement

- Relaytic should be able to scout promising architectures from research, register them as candidates, and test them in replay or shadow mode before they gain routing authority

## Human Surface

- operators should be able to inspect where a candidate family came from, what evidence supports it, what benchmarks it was shadow-tested on, and why it is still quarantined or ready for promotion

## Agent Surface

- external agents should be able to propose model-family candidates, inspect shadow-trial outcomes, and consume promotion-readiness state through stable JSON artifacts

## Required Behavior

- research retrieval must be able to register model-family candidates with provenance
- the method compiler must be able to convert accepted research signals into candidate architecture cards
- candidate families must go through:
  - candidate registration
  - offline replay
  - shadow trial
  - promotion-readiness review
- candidate families must not become default router options without proof
- weak candidates must remain quarantined with explicit rejection reasons
- strong candidates may become `candidate_available` before the later academy track generalizes promotion logic to tools and non-core specialists
- temporal imported candidates such as LSTM, TCN, or temporal-transformer families must remain replay-first and shadow-first until the temporal benchmark pack proves they add value over lagged tabular baselines

## Acceptance Criteria

Slice 15F is acceptable only if:

1. one externally sourced architecture remains shadow-only because proof is weak
2. one externally sourced architecture is marked promotion-ready after replay and shadow evidence
3. one human explanation surface answers why a paper-inspired architecture was not yet used live
4. one agent surface can inspect candidate provenance and shadow scorecards without prose-only interpretation
5. one temporal imported candidate is compared against a lagged tabular baseline before any promotion-readiness claim is made

## Required Verification

- one research-to-candidate registry test
- one shadow-trial scorecard test
- one quarantine-path test
- one `why not this imported architecture?` explanation test
