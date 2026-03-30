# Result Contract Schema

## Purpose

This document defines the canonical machine-stable result contract that every serious Relaytic run should emit once Slice 12D lands.

Human and agent reports may render this contract differently, but they must not replace it as the authoritative post-run conclusion.

Compatibility for the already-shipped Slice 12C handoff surfaces is frozen separately in:

- `docs/specs/handoff_result_migration.md`

## Canonical artifact

- `result_contract.json`

Related supporting artifacts:

- `confidence_posture.json`
- `belief_revision_triggers.json`

## Required top-level fields

`result_contract.json` must include:

- `schema_version`
- `run_id`
- `workspace_id`
- `generated_at`
- `status`
- `objective_summary`
- `current_beliefs`
- `evidence_strength`
- `unresolved_items`
- `recommended_next_move`
- `why_this_move`
- `why_not_other_moves`
- `confidence_posture_ref`
- `belief_revision_triggers_ref`
- `source_artifacts`

## Status values

Required `status` enum:

- `provisional`
- `actionable`
- `blocked`
- `needs_review`
- `restart_recommended`

## Objective summary

`objective_summary` must contain:

- `task_type`
- `target_summary`
- `focus_profile`
- `decision_context`
- `active_constraints`

`task_type` should be one of:

- `classification`
- `regression`
- `ranking`
- `forecasting`
- `anomaly_detection`
- `data_analysis`
- `benchmark_challenge`
- `mixed`

## Current beliefs

`current_beliefs` must be a list of structured belief objects, not one free-form paragraph.

Each belief object must contain:

- `belief_id`
- `statement`
- `scope`
- `support_level`
- `supporting_evidence_refs`
- `counterevidence_refs`
- `applies_if`

Required `support_level` values:

- `weak`
- `moderate`
- `strong`
- `tentative`

## Evidence strength

`evidence_strength` must summarize:

- `overall_strength`
- `metric_posture`
- `benchmark_posture`
- `trace_posture`
- `data_posture`
- `risk_posture`

Required `overall_strength` values:

- `low`
- `medium`
- `high`

`metric_posture` should include:

- `primary_metric`
- `primary_value`
- `minimum_contract_met`
- `calibration_ok`
- `uncertainty_ok`

## Unresolved items

`unresolved_items` must be a list of structured blockers or open questions.

Each unresolved item must contain:

- `item_id`
- `statement`
- `severity`
- `kind`
- `resolution_hint`
- `blocking_next_moves`

Required `severity` values:

- `low`
- `medium`
- `high`

Required `kind` values:

- `data_gap`
- `evaluation_gap`
- `model_gap`
- `decision_gap`
- `policy_gap`
- `review_gap`
- `semantic_gap`

## Recommended next move

`recommended_next_move` must contain:

- `direction`
- `action`
- `confidence`
- `required_inputs`
- `estimated_cost_posture`
- `estimated_value_posture`

Required `direction` values:

- `same_data`
- `add_data`
- `new_dataset`

Recommended `action` values:

- `search_more`
- `recalibrate`
- `retrain`
- `benchmark_incumbent`
- `collect_more_data`
- `collect_better_labels`
- `pause_for_review`
- `start_fresh`

## Why this move

`why_this_move` must be a list of structured reasons.

Each reason must contain:

- `reason_type`
- `statement`
- `evidence_refs`

Required `reason_type` values:

- `evidence`
- `cost`
- `risk`
- `benchmark`
- `continuity`
- `operator_input`
- `memory`

## Why not other moves

`why_not_other_moves` must contain explicit assessments of at least:

- `same_data`
- `add_data`
- `new_dataset`

Each must include:

- `rejected`
- `reason`
- `reconsider_if`

## Confidence posture

`confidence_posture.json` must contain:

- `overall_confidence`
- `known_fragility`
- `abstention_readiness`
- `review_need`
- `confidence_explanation`

Required `overall_confidence` values:

- `low`
- `medium`
- `high`

Required `review_need` values:

- `none`
- `recommended`
- `required`

## Belief revision triggers

`belief_revision_triggers.json` must contain explicit conditions under which Relaytic should change its mind.

Each trigger must include:

- `trigger_id`
- `condition`
- `expected_effect`
- `priority`

Required `expected_effect` values:

- `weaken_current_belief`
- `strengthen_current_belief`
- `change_next_move`
- `require_restart`
- `require_review`

## Rendering rules

`reports/user_result_report.md` should optimize for:

- clarity
- narrative explanation
- recommended next action
- confidence and unresolved items
- what the user can do now

`reports/agent_result_report.md` should optimize for:

- terseness
- artifact references
- exact next-run actionability
- structured unresolved items
- command or surface hints

Neither rendering may introduce a belief or recommendation that is absent from `result_contract.json`.

## Backward compatibility

Before Slice 12D lands, Relaytic may still rely on the current Slice 12C handoff surfaces.

After Slice 12D lands:

- `run_handoff.json` may remain as a convenience artifact
- `result_contract.json` becomes the canonical post-run truth
- all report surfaces must be derivable from that contract
