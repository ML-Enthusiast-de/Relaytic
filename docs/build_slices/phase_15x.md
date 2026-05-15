# Slice 15X - AML evaluation-environment reframe

## Status

Planned.

## Intent

Slice 15X turns Relaytic runs into explicit evaluation environments for humans and external agents.

This slice should make the public proof story broader than model accuracy: Relaytic must be evaluated as a local investigation environment under realistic workflow pressure.

## Load-Bearing Improvement

- Relaytic scores environment tasks such as messy task detection, unsafe steering rejection, incumbent challenge, alert-queue optimization, drift recovery, and public-safe claim generation.
- Environment tasks must include benchmark relevance, artifact reproducibility, public-claim discipline, and analyst-review utility so that the later paper release cannot cherry-pick only model metrics.

## Human Surface

- operators see one environment scorecard explaining whether Relaytic behaved well under realistic workflow pressure.

## Agent Surface

- external agents can run or inspect environment tasks non-interactively.

## Intelligence Source

- trace and eval artifacts
- assist and control artifacts
- benchmark guards
- incumbent comparisons
- casework
- stream-risk posture
- public-claim gates

## Fallback Rule

- if an environment task cannot run, Relaytic reports it as incomplete instead of treating model success as environment success.

## Required Outputs

- `aml_eval_environment_manifest.json`
- `aml_environment_scorecard.json`
- `aml_workflow_task_matrix.json`
- `aml_environment_failure_report.json`
- `aml_benchmark_environment_scorecard.json`

## Acceptance Criteria

1. One environment scorecard includes both a model-quality task and a workflow-safety task.
2. One unsafe steering task remains rejected with trace-backed evidence.
3. Model score and environment score are reported separately.
4. One benchmark-environment scorecard checks whether the run is reproducible, claim-safe, and relevant to at least one named AML benchmark family.
5. One failure report shows a case where model success does not imply environment success.

## Required Verification

- environment scorecard tests
- unsafe steering environment regression
- CLI/MCP parity check for environment score
- benchmark-environment scorecard regression
