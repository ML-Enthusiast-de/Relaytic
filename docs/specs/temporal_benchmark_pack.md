# Temporal Benchmark Pack

## Purpose

This document defines the future time-aware benchmark pack for Relaytic.

It exists because Relaytic already has:

- timestamp detection
- blocked temporal splits
- lag-aware routes
- sensor diagnostics
- time-aware investigation logic

But it does not yet have:

- a dedicated temporal benchmark suite
- a paper-grade temporal evaluation story
- a serious sequence-model comparison path

## Current honest status

Relaytic has **time-aware architecture hooks**, but not yet a **time-aware benchmark program**.

That means:

- we did not lose temporal support completely
- we did deprioritize it in the benchmark and competitiveness story

This pack fixes that.

## Benchmark doctrine

Temporal evaluation should happen in two tiers.

### Tier 1. Timestamped tabular temporal benchmarks

These are the first datasets Relaytic should support because they match the current product shape best:

- tabular rows
- explicit timestamp or ordered structure
- lagged-feature routes are already a sensible baseline
- later sequence models can challenge them honestly

### Tier 2. Sequence-native benchmarks

These should come later, once Relaytic has real LSTM, TCN, or temporal-transformer candidate families.

These datasets are still valuable, but they should not be forced into the current lagged-tabular route family before the model registry is ready.

## Tier 1: recommended paper-grade timestamped tabular datasets

### 1. UCI Appliances Energy Prediction

Source:
- UCI Machine Learning Repository
- https://archive.ics.uci.edu/dataset/374/appliances+energy+prediction

Recommended task:
- regression / forecasting

Why it fits:
- explicit temporal order
- multivariate sensor-style inputs
- common forecasting use in papers and student/research baselines
- good bridge between ordinary tabular regression and richer time-aware modeling

Why Relaytic should use it:
- lagged tabular routes should be a credible first baseline here
- later LSTM or temporal-transformer candidates can challenge that baseline honestly

### 2. UCI Beijing Multi-Site Air Quality

Source:
- UCI Machine Learning Repository
- https://archive.ics.uci.edu/dataset/501/beijingmultisiteairqualitydata

Recommended task:
- regression / forecasting

Why it fits:
- real multivariate temporal environmental data
- strong paper-friendly forecasting benchmark semantics
- site-aware and temporally ordered, which is useful for later richer temporal reasoning

Why Relaytic should use it:
- tests whether Relaytic can reason about ordered sensor-style data instead of only static tables
- provides a more serious temporal benchmark than tiny toy forecasting sets

### 3. UCI Individual Household Electric Power Consumption

Source:
- UCI Machine Learning Repository
- https://archive.ics.uci.edu/dataset/235/individualhouseholdelectricpowerconsumption

Recommended task:
- regression / forecasting

Why it fits:
- classic household load forecasting benchmark
- long ordered series with realistic noise and missingness
- widely cited enough to be paper-legible

Why Relaytic should use it:
- strong fit for lagged regression and later deeper temporal architectures
- forces Relaytic to handle longer-horizon, higher-volume temporal data responsibly

### 4. NASA C-MAPSS

Source:
- NASA Prognostics Data Repository / NASA Open Data
- https://data.nasa.gov/dataset/simulating-degradation-data-for-prognostic-algorithm-development
- https://www.nasa.gov/intelligent-systems-division/discovery-and-systems-health/pcoe/pcoe-data-set-repository/

Recommended task:
- regression / remaining-useful-life style prediction

Why it fits:
- one of the most recognizable sequence-heavy prognostics benchmarks
- heavily used in predictive-maintenance literature
- strong case where sequence-aware models often matter

Why Relaytic should use it:
- gives Relaytic a serious industrial temporal benchmark
- becomes the clearest proving ground for when lagged tabular routes stop being enough

## Tier 2: later sequence-native expansion candidates

These are good later candidates once Relaytic has a real temporal model registry and shadow-test pipeline:

- Monash forecasting-repository style datasets
- ETT-style transformer forecasting datasets
- richer public multivariate sensor classification datasets
- stronger public prognostics suites beyond C-MAPSS

These should not be first because they increase implementation pressure before Relaytic has:

- a stronger task contract
- temporal model routing
- real temporal HPO
- shadow-tested sequence families

## Temporal model ladder

Relaytic should compare temporal approaches in this order:

1. non-temporal baseline
2. lagged tabular baseline
3. stronger tree/boosting routes with temporal features
4. sequence-native candidate families in replay or shadow mode
5. promoted sequence family only after benchmark proof

This matters because many timestamped tabular tasks are still best served by lagged gradient boosting or similar tabular routes.

Relaytic should not assume:

- `time column` -> `LSTM`

## Required future artifacts

- `temporal_benchmark_manifest.json`
- `temporal_route_comparison.json`
- `temporal_horizon_report.json`
- `sequence_candidate_registry.json`
- `sequence_shadow_scorecard.json`
- `temporal_generalization_report.json`

## Required future proof

The temporal track is only credible if Relaytic can prove:

1. one timestamped dataset where lagged tabular routes beat a naive non-temporal route
2. one timestamped dataset where a sequence family is tested and loses honestly to lagged tabular
3. one timestamped dataset where a sequence family wins enough in replay or shadow mode to become promotion-ready
4. one explanation flow that answers `why not use LSTM here?`
5. one explanation flow that answers `why did you choose a temporal model here?`

## Relationship to the model-competitiveness track

This temporal benchmark pack should be consumed by:

- Slice 15B for temporal architecture routing
- Slice 15C for temporal HPO depth and stop logic
- Slice 15D for paper-grade temporal benchmark reporting
- Slice 15F for research-imported temporal candidates such as LSTM, TCN, or temporal-transformer families in replay and shadow mode
