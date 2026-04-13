# Slice 15H - First-class competitive family stack

## Status

Shipped.

Delivered package boundaries:

- extend `src/relaytic/modeling/`
- extend `src/relaytic/analytics/`
- extend `src/relaytic/planning/`
- extend `src/relaytic/benchmark/`
- extend `src/relaytic/assist/`
- extend `tests/`

Intended artifacts:

- `family_registry_extension.json`
- `family_readiness_report.json`
- `family_eligibility_matrix.json`
- `family_probe_policy.json`
- `categorical_strategy_report.json`
- `family_specialization_report.json`

## Intent

Slice 15H upgrades Relaytic from "broader than boosted trees" to a genuinely competitive family stack.

The goal is to make strong families first-class citizens with family-owned assumptions, search spaces, and eligibility logic instead of routing everything through one generic training path.

## Load-Bearing Improvement

- Relaytic should be able to choose from a serious tabular family set, including categorical-aware, multiclass-aware, rare-event-aware, and small-data-specialist routes, without pretending one generic boosted-tree stack is enough

## Human Surface

- operators should be able to inspect which families were eligible, which adapters were available, which categorical strategy Relaytic chose, and why a stronger family was or was not considered

## Agent Surface

- external agents should be able to inspect family eligibility, readiness, and specialization through stable JSON artifacts without scraping prose

## Required Behavior

- Relaytic must make strong linear, histogram-gradient, extra-trees/random-forest, and boosted-tree families first-class routing options
- optional CatBoost, LightGBM, XGBoost, and TabPFN-style adapters must expose readiness, version capture, and graceful fallback
- mixed-type and categorical-heavy data must be able to prefer categorical-aware families when available
- multiclass tasks must not inherit binary-default family logic
- labeled rare-event tasks must carry rare-event-specific family policies instead of generic classification defaults
- sequence-native families must remain out of the live standard router until Slice 15J proves real temporal structure and competitiveness

## Acceptance Criteria

Slice 15H is acceptable only if:

1. one mixed-type benchmark considers a categorical-aware family before generic numeric boosting when the adapter is available
2. one small-data classification case considers a small-data specialist family when available
3. one multiclass benchmark gets a materially broader eligible family set than the current path
4. one no-adapter environment still falls back cleanly to the deterministic floor without changing control truth

## Required Verification

- one family-eligibility matrix test
- one adapter-readiness and fallback test
- one multiclass family-widening test
- one assist explanation test for family eligibility
