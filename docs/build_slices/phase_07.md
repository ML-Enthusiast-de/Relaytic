# Slice 07 - Completion Governor

## Intent

Slice 07 is not a cosmetic status layer.

It is the first point where Relaytic should become an explicit inference governor:

- consume the full artifact graph
- decide whether the run is actually complete
- identify the real blocking layer
- expose the next action in a form that a human or another agent can execute

If Slice 07 lands as a status dashboard without stronger judgment, it failed.

## Weaknesses It Must Close

The current repo still has these frontier-relevant weaknesses:

- challenger pressure is real but still narrow
- evidence is not yet fully fused with mandate, context, and investigation
- the MVP can build and challenge a route, but it cannot yet authoritatively say whether the run should continue, stop, benchmark, recalibrate, or seek more evidence
- memory and benchmark systems are not implemented yet, so Slice 07 must at least detect and name when those absences are the real limiting factor

Slice 07 must surface those weaknesses explicitly instead of hiding them.

## Required Outputs

- `completion_decision.json`
- `run_state.json`
- `stage_timeline.json`
- `mandate_evidence_review.json`
- `blocking_analysis.json`
- `next_action_queue.json`

## Required Inputs

Slice 07 must consume, at minimum:

- mandate artifacts
- context artifacts
- intake autonomy and assumption artifacts
- investigation and focus artifacts
- planning artifacts
- evidence artifacts from Slice 06

It must not operate on final metrics alone.

## Canonical Package Boundary

Slice 07 introduced:

- `src/relaytic/completion/`

That package should own completion-governor logic, artifact persistence, and top-level status synthesis.

## Required Behavior

- completion must emit a machine-actionable decision, not only a narrative explanation
- completion must state:
  - current stage
  - recommended action
  - confidence level
  - blocking layer
  - whether mandate and evidence agree or conflict
  - whether the run is complete enough for the current operating mode
- completion must be able to say:
  - `stop_for_now`
  - `continue_experimentation`
  - `review_challenger`
  - `collect_more_data`
  - `benchmark_needed`
  - `memory_support_needed`
  - `recalibration_candidate`
  - `retrain_candidate`
- `completion_decision.json` must at minimum expose:
  - `action`
  - `confidence`
  - `current_stage`
  - `blocking_layer`
  - `mandate_alignment`
  - `evidence_state`
  - `complete_for_mode`
  - `reason_codes`
- `next_action_queue.json` entries must at minimum expose:
  - `action`
  - `priority`
  - `reason_code`
  - `source_artifact`
  - `blocking`
- completion must keep the deterministic floor
- if the real limitation is missing memory support or missing benchmark context, completion must say so explicitly and hand off into Slice 09A or Slice 11 rather than pretending the run is self-sufficient
- optional local-LLM help may refine summaries, but must not decide the completion action

## Public CLI Surface

Slice 07 adds:

- `relaytic status`
- `relaytic completion review`

The top-level `relaytic show` output should also surface the current stage, blocking layer, and recommended action.

## Acceptance Criteria

Slice 07 is acceptable only if:

1. a human can run one command and see whether Relaytic believes it is done and why
2. an external agent can read one JSON artifact and know the next action without reading long prose
3. the completion layer can explicitly say when the current run is limited by narrow challenger breadth, missing benchmark context, or missing memory support
4. the result is auditable and deterministic

## Landed

- `src/relaytic/completion/` now owns the completion-governor logic and artifact persistence
- `relaytic run` now includes Slice 07 by default after the evidence stage
- `relaytic show` now surfaces the governed run state rather than evidence-only posture
- `relaytic status` and `relaytic completion review` now expose stable human and agent control surfaces

## Verification

- targeted Slice 07 agent tests
- targeted Slice 07 CLI tests
- targeted Slice 07 local-stub-LLM tests
- end-to-end `relaytic run` coverage through completion artifacts

## Required Verification

Slice 07 should not be considered complete without targeted tests that cover at least:

- a run that resolves to `continue_experimentation` because challenger breadth is still too narrow
- a run that resolves to `benchmark_needed`
- a run that resolves to `memory_support_needed`
- a run where mandate and evidence conflict
- CLI tests for `relaytic status` and `relaytic completion review`
