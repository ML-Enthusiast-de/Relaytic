# Open Source Stack Strategy

Relaytic should not win by reimplementing mature commodity libraries. It should win on orchestration, judgment, autonomy, provenance, and evidence-backed decisions.

## Adoption Rule

Use mature external libraries when they improve:

- baseline strength
- diagnostics quality
- schema validation
- feature breadth
- monitoring depth
- benchmark parity

Do not let them replace:

- Relaytic artifact contracts
- mandate and policy handling
- completion judgment
- agent coordination
- run provenance

## Strong Near-Term Candidates

- `scikit-learn`
  Use for reference baselines, bundled public datasets, preprocessing, calibration, and metric parity checks.
- `imbalanced-learn`
  Use for rare-event challengers and imbalance-focused ablations.
- `statsmodels`
  Use for residual diagnostics, uncertainty checks, and classical sanity baselines.
- `pandera`
  Use for dataframe schema validation around intake, execution, and agent-facing payloads.
- `PyOD`
  Use for anomaly challengers when the native challenger space needs broader detector families.

## Targeted Later Candidates

- `featuretools`
  For relational and grouped-history feature synthesis.
- `tsfresh`
  For time-series feature extraction.
- `sktime`
  For forecasting and time-series benchmark parity.
- `river`
  For streaming, drift, and incremental-monitoring slices.
- `SHAP`
  For selective post-hoc explanation surfaces.
- `Evidently`
  For optional monitoring and reporting views.

## Integration Rules

- keep them behind explicit adapter boundaries
- keep dependencies optional unless a surface is part of the guaranteed baseline
- record library name and version when results influence artifacts
- treat third-party outputs as evidence inputs, not hidden sources of truth
- prefer offline-stable public datasets in tests over network-bound dataset fetches

## Discoverability

Relaytic exposes the current optional-integration inventory through:

```bash
relaytic integrations show
relaytic integrations show --format json
relaytic integrations self-check
relaytic integrations self-check --format json
```

That surface is meant for both humans and external agents.

## Wired Today

- `pandera`
  Wired into intake dataframe-contract validation and recorded in `intake_record.json`.
- `statsmodels`
  Wired into regression evidence audit for residual diagnostics and finding enrichment.
- `imbalanced-learn`
  Wired into rare-event challenger execution for fraud-style or imbalanced binary routes.
- `PyOD`
  Wired into anomaly challenger execution for anomaly-detection routes, with a default Windows runtime guard until the current PyOD/numba/llvmlite stack is stable enough to trust.
- `scikit-learn`
  Wired into public dataset test coverage and integration self-checks.

## Upgrade Safety

Every wired integration must:

- sit behind a dedicated adapter
- expose stable `status`, `compatible`, `version`, `notes`, and `details` fields
- degrade to `skipped`, `not_installed`, or `incompatible` instead of crashing the run
- be covered by `relaytic integrations self-check`
