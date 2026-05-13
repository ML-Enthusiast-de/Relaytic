# Slice 15S - Flagship AML demo pack

## Status

Implemented.

## Intent

Slice 15S makes Relaytic-AML obvious through one public-safe demo bundle instead of expecting a reviewer to infer value from many independent artifacts.

## Load-Bearing Improvement

- Relaytic can create a `relaytic-aml-review-queue` demo bundle from fixture data with a review queue, case packet, operating point, drift posture, benchmark guard, public-claim guard, and failure report.
- Mission control can render that bundle as an AML investigation board instead of only a generic card list.

## Human Surface

- operators get one concise demo report with a run-flow diagram, business-metric table, top case packet, and safe claims.

## Agent Surface

- external agents can inspect the demo manifest, proof status, artifact paths, and recommended next command from JSON.

## Intelligence Source

- AML graph artifacts
- casework artifacts
- stream-risk artifacts
- benchmark truth gates
- public-claim guards
- trace and eval surfaces

## Fallback Rule

- if a richer HTML renderer is unavailable, Relaytic still writes markdown and JSON demo artifacts.

## Required Outputs

- `aml_demo_bundle_manifest.json`
- `aml_demo_business_metric_table.json`
- `aml_demo_flow_report.md`
- `aml_demo_artifact_index.json`
- `aml_investigation_board.json`
- mission-control AML investigation board section backed by existing artifacts

Implemented command:

- `relaytic demo aml-review-queue`

## Acceptance Criteria

1. One command creates the demo bundle from fixture data.
2. The bundle links to the case packet, benchmark guard, public-claim guard, and failure report.
3. The demo report separates model metrics from operational review-budget metrics.
4. Mission control shows the alert queue, top case packet, drift posture, and claim guard without requiring raw artifact reading.

## Required Verification

- one CLI demo-bundle test
- one artifact-index integrity test
- one public-safe claim guard regression
