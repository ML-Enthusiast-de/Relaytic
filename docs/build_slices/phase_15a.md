# Slice 15A - Canonical task contract, rare-event taxonomy, and benchmark-vs-deploy separation

## Status

Planned.

Slice 15A is the next recommended target.

Delivered package boundaries:

- extend `src/relaytic/analytics/`
- extend `src/relaytic/planning/`
- extend `src/relaytic/modeling/`
- extend `src/relaytic/benchmark/`
- extend `src/relaytic/decision/`
- extend `src/relaytic/runs/`

Intended artifacts:

- `task_profile_contract.json`
- `target_semantics_report.json`
- `metric_contract.json`
- `benchmark_mode_report.json`
- `deployment_readiness_report.json`
- `benchmark_vs_deploy_report.json`
- `dataset_semantics_audit.json`

## Intent

Slice 15A fixes the foundational semantic weakness exposed by benchmark work: Relaytic still allows task meaning to drift across intake, planning, training, benchmark review, and later explanation.

This slice creates one canonical problem contract and forces every later stage to consume it.

## Load-Bearing Improvement

- Relaytic should decide once what problem it is solving, what counts as success, and whether the current run is being judged for benchmark competitiveness, deployment readiness, or both

## Human Surface

- operators should be able to inspect one clear explanation of what task Relaytic believes it is solving, why it chose that interpretation, which metrics it will optimize, and whether the current posture is benchmark-facing or deployment-facing

## Agent Surface

- external agents should be able to consume the canonical task contract and the benchmark-vs-deploy split through stable JSON artifacts instead of inferring semantics from scattered later-stage reports

## Required Behavior

- Relaytic must create one canonical `task_profile_contract.json` before route selection
- later stages must consume that contract instead of silently re-inferring task type
- rare-event labeled tasks must distinguish supervised rare-event classification from true anomaly detection
- multiclass string labels must remain multiclass through all later stages
- benchmark review must not be downgraded solely because deployment-readiness logic says `hold_for_data_refresh`
- deployment readiness must still remain explicit and conservative when needed
- assist and mission control must answer `why this task type?` and `why not anomaly detection?` from the same contract

## Acceptance Criteria

Slice 15A is acceptable only if:

1. one labeled rare-event dataset is kept in supervised classification posture end to end
2. one multiclass string-label dataset stays multiclass through planning, training, benchmark, and explanation surfaces
3. one offline benchmark run can be reported as competitive while deployment readiness remains conditional for separate reasons
4. one explanation flow can answer why Relaytic chose the current task type and metric family without contradiction across CLI and MCP

## Required Verification

- one task-detection regression test for string multiclass labels
- one rare-event taxonomy test
- one benchmark-vs-deploy split test
- one assist explanation test for task semantics
