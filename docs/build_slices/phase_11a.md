# Slice 11A - Imported incumbents and bring-your-own challenger baselines

## Status

Planned.

Intended package boundaries:

- extend `src/relaytic/benchmark/`
- extend `src/relaytic/evidence/`
- extend `src/relaytic/lifecycle/`
- extend `src/relaytic/runs/` and `src/relaytic/assist/` for visibility

Intended artifacts:

- `external_challenger_manifest.json`
- `external_challenger_evaluation.json`
- `incumbent_parity_report.json`
- `beat_target_contract.json`

## Intent

Slice 11A is where Relaytic stops assuming the only meaningful baseline is an internal reference approach or the previous Relaytic run.

This slice is successful only if Relaytic can:

- accept a real incumbent from the user or an external agent
- evaluate that incumbent locally under the same split and metric contract where possible
- fall back honestly when only predictions or partial metadata are available
- tell the operator whether Relaytic actually beat the incumbent and why
- use that incumbent as an explicit beat-target for later search, autonomy, and lifecycle reasoning

## Required Behavior

- Relaytic must support at least three incumbent forms:
  - local serialized model or adapter
  - scored prediction file
  - explicit ruleset or scorecard wrapper
- incumbent evaluation must use the same split, metric, threshold, calibration, and decision contract where possible
- incumbent metrics supplied by the operator must not be trusted blindly when local reevaluation is possible
- reduced-claim fallback must be explicit when Relaytic cannot execute the incumbent locally
- beat-target contracts must be visible to evidence, benchmark, lifecycle, assist, and later mission-control surfaces
- Relaytic must be able to lose honestly and emit a next-step recommendation when the incumbent remains stronger

## Acceptance Criteria

Slice 11A is acceptable only if:

1. one locally executable incumbent is reevaluated under the same contract as Relaytic
2. one prediction-only incumbent path falls back with reduced claims
3. one case shows Relaytic beating the incumbent with an explicit parity report
4. one case shows Relaytic losing honestly and recommending what to do next
5. one search or autonomy surface consumes an explicit beat-target contract rather than vague parity language

## Required Verification

Slice 11A should not be considered complete without targeted tests that cover at least:

- one local incumbent-model adapter case
- one prediction-file incumbent case
- one ruleset or scorecard case
- one win-against-incumbent case
- one loss-against-incumbent case
- one lifecycle or benchmark visibility-parity case
