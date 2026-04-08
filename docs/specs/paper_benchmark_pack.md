# Paper Benchmark Pack

## Purpose

This document defines the first paper-grade benchmark and eval pack for Relaytic.

The pack is designed to answer two different questions:

- can Relaytic operate credibly across the main structured-data task families?
- can the same system story survive later paper writing, benchmark reporting, and ablation work?

This pack is intentionally separate from the default CI wall. It is optional, slower, and partly network-backed.

## Selection criteria

Datasets in this pack should be:

- public and easy to cite from a primary source
- strongly associated with structured/tabular ML work
- varied enough to cover different domains, class structures, and failure modes
- small or medium enough to remain realistic on a local machine
- free of login-gated download paths
- clear enough that a paper reader can understand why each one is present

The first version of the pack intentionally favors:

- UCI-hosted datasets for citable primary-source stability
- scikit-learn bundled datasets for deterministic local sanity checks
- mixed-type and imbalanced datasets, not just perfectly clean toy tables

## Scientific positioning

This pack is good enough for:

- a systems paper benchmark section
- an agent-for-tabular-data paper where the main claim is reliability, governance, continuity, or operator experience
- a paper that includes modeling competitiveness as one part of the story instead of claiming pure tabular SOTA

This pack is not enough by itself for:

- a strong claim that Relaytic is state of the art across tabular modeling
- a claim that Relaytic matches the strongest modern benchmark suites used in pure model papers

Reason:

- the current pack is public, citable, diverse, and reproducible
- but many datasets are still small to medium classical benchmarks rather than a broad modern benchmark suite
- it does not yet include a larger OpenML-style benchmark suite, a dedicated time-aware suite, or a stronger public fraud benchmark

So the correct scientific claim today is:

- the pack is legitimate and paper-acceptable
- it is strong enough for a credible first benchmark section
- it should later be expanded before making stronger modeling-dominance claims

The dedicated future time-aware benchmark track is specified separately in [temporal_benchmark_pack.md](temporal_benchmark_pack.md).

## Dataset matrix

### Regression

1. `sklearn_diabetes`
Source: scikit-learn `load_diabetes`
URL: https://scikit-learn.org/stable/modules/generated/sklearn.datasets.load_diabetes.html
Rows: `442`
Target: `disease_progression`
Why:
- classic small regression benchmark for repeatable local smoke checks
- common enough that paper readers immediately recognize it

2. `uci_concrete_strength`
Source: UCI Machine Learning Repository
URL: https://archive.ics.uci.edu/dataset/165/concrete+compressive+strength
Rows: `1030`
Target: `concrete_strength`
Why:
- nonlinear engineering regression benchmark with real tabular structure
- more paper-serious than a tiny toy example while still staying local-friendly

3. `uci_energy_efficiency`
Source: UCI Machine Learning Repository
URL: https://archive.ics.uci.edu/dataset/242/energy+efficiency
Rows: `768`
Target: `heating_load`
Why:
- strong structured regression benchmark with a different domain than concrete
- useful for later paper tables because it is small enough for repeated ablations

### Binary Classification

1. `sklearn_breast_cancer`
Source: scikit-learn `load_breast_cancer`
URL: https://scikit-learn.org/stable/modules/generated/sklearn.datasets.load_breast_cancer.html
Rows: `569`
Target: `diagnosis_flag`
Why:
- canonical medical binary classification benchmark
- strong deterministic baseline for end-to-end product verification

2. `uci_bank_marketing`
Source: UCI Machine Learning Repository
URL: https://archive.ics.uci.edu/dataset/222/bank+marketing
Rows: `6000` sampled stratified from the full dataset
Target: `term_deposit_flag`
Why:
- mixed-type tabular classification with operational business semantics
- more realistic preprocessing and routing pressure than toy binary datasets

3. `uci_statlog_german_credit`
Source: UCI Machine Learning Repository
URL: https://archive.ics.uci.edu/dataset/144/statlog+german+credit+data
Rows: `1000`
Target: `credit_risk_flag`
Why:
- classic credit-risk benchmark still used in structured-data comparisons
- valuable for papers because it mixes numeric and categorical evidence in a compact dataset

### Multiclass Classification

1. `sklearn_wine`
Source: scikit-learn `load_wine`
URL: https://scikit-learn.org/stable/modules/generated/sklearn.datasets.load_wine.html
Rows: `178`
Target: `wine_class`
Why:
- canonical multiclass smoke benchmark
- keeps the pack grounded and fast

2. `uci_dry_bean`
Source: UCI Machine Learning Repository
URL: https://archive.ics.uci.edu/dataset/602/dry+bean+dataset
Rows: `4000` sampled stratified from the full dataset
Target: `bean_class`
Why:
- stronger modern multiclass benchmark with seven classes
- useful paper dataset because it exposes weak route selection more clearly than Wine

3. `uci_dermatology`
Source: UCI Machine Learning Repository
URL: https://archive.ics.uci.edu/dataset/33/dermatology
Rows: `366`
Target: `dermatology_class`
Why:
- compact clinical multiclass benchmark with heterogeneous features
- complements Dry Bean with a medically flavored multiclass problem

### Rare-Event / Fraud-Like / Anomaly-Sensitive

1. `uci_credit_default`
Source: UCI Machine Learning Repository
URL: https://archive.ics.uci.edu/dataset/350/default+of+credit+card+clients
Rows: `5000` sampled stratified from the full dataset
Target: `default_flag`
Why:
- finance-oriented rare-event decisioning problem that is paper-friendly and public
- strong proxy for fraud-like or risk-sensitive classification without relying on gated downloads

2. `uci_iranian_churn`
Source: UCI Machine Learning Repository
URL: https://archive.ics.uci.edu/dataset/563/iranian+churn+dataset
Rows: `2500` sampled stratified from the full dataset
Target: `churn_flag`
Why:
- business retention risk task with skewed outcomes and operational relevance
- good complement to finance because it broadens the rare-event story

3. `uci_ai4i_machine_failure`
Source: UCI Machine Learning Repository
URL: https://archive.ics.uci.edu/dataset/601/ai4i+2020+predictive+maintenance+dataset
Rows: `3000` sampled stratified from the full dataset
Target: `machine_failure`
Why:
- industrial failure detection benchmark with low positive prevalence
- gives Relaytic a paper-grade rare-event benchmark outside finance and churn

## Prepared test surfaces

The prepared optional pytest surface is:

- `tests/test_paper_benchmark_pack.py`

It includes:

- a full dataset-matrix run test across all selected datasets
- a heavier representative subset that also materializes:
  - benchmark review
  - eval harness

Representative heavy subset:

- `uci_energy_efficiency`
- `uci_bank_marketing`
- `uci_dry_bean`
- `uci_credit_default`

Those four were chosen because they cover the four major task families with more paper-serious datasets than the tiny bundled smoke fixtures.

## How to run later

Windows PowerShell:

```powershell
$env:RELAYTIC_ENABLE_PAPER_BENCHMARKS="1"
python -m pytest tests/test_paper_benchmark_pack.py -q
```

macOS/Linux:

```bash
export RELAYTIC_ENABLE_PAPER_BENCHMARKS=1
python -m pytest tests/test_paper_benchmark_pack.py -q
```

Recommended shards:

- `python -m pytest tests/test_paper_benchmark_pack.py -k regression -q`
- `python -m pytest tests/test_paper_benchmark_pack.py -k binary_classification -q`
- `python -m pytest tests/test_paper_benchmark_pack.py -k multiclass_classification -q`
- `python -m pytest tests/test_paper_benchmark_pack.py -k rare_event -q`

## Why some obvious datasets are not in version one

Not every famous dataset belongs in the first paper pack.

Excluded from version one:

- Kaggle- or login-gated datasets, even if they are popular
- giant datasets that distort local runtime comparisons
- datasets with unclear reuse or citation posture
- datasets that are too toy-like to matter in a paper

Examples of plausible later additions:

- a public, ungated credit-card fraud benchmark if we decide the licensing and fetch path are stable enough
- a larger multiclass benchmark beyond Dry Bean
- a truly time-aware benchmark once we decide to make time-series evaluation part of the main paper thesis
- a broader OpenML-style benchmark expansion once we are ready for a more expensive paper-grade comparison suite
