# Slice 12D - Workspace-first continuity, result contracts, and governed learnings

## Status

Planned.

Intended package boundaries:

- `src/relaytic/workspace/`
- `src/relaytic/iteration/`
- extend `src/relaytic/handoff/`
- extend `src/relaytic/learnings/`
- extend `src/relaytic/mission_control/`
- extend `src/relaytic/memory/`

Intended artifacts:

- `workspace_state.json`
- `workspace_lineage.json`
- `workspace_focus_history.json`
- `workspace_memory_policy.json`
- `result_contract.json`
- `confidence_posture.json`
- `belief_revision_triggers.json`
- `next_run_plan.json`
- `focus_decision_record.json`
- `data_expansion_candidates.json`

## Intent

Slice 12D is where Relaytic stops treating the isolated run as the whole product and starts behaving like a governed multi-run workspace.

The slice is successful only if Relaytic can:

- preserve explicit continuity across at least two runs in one workspace
- express one machine-stable result contract per serious run
- keep durable learnings governed rather than sticky and silent
- decide whether the next move should stay on the same data, add data, or start over

This slice must follow these normative spec documents:

- `docs/specs/workspace_lifecycle.md`
- `docs/specs/result_contract_schema.md`
- `docs/specs/governed_learnings_schema.md`
- `docs/specs/mission_control_flows.md`
- `docs/specs/test_and_proof_matrix.md`
- `docs/specs/flagship_demo_pack.md`

## Load-Bearing Improvement

- Relaytic should become workspace-first before it becomes search-deeper, so later search, mission-control, and demo slices can build on explicit continuity, governed learnings, and machine-stable next-run planning instead of narrative memory

## Human Surface

- humans should be able to finish a run, read one user-optimized result report, understand what Relaytic currently believes, see what remains unresolved, choose whether to continue on the same data, add data, or start over, and continue from the same workspace without losing context

## Agent Surface

- external agents should be able to consume one machine-stable result contract, workspace lineage, focus history, governed learnings, and next-run plan without scraping markdown or inferring continuity from directory structure

## Intelligence Source

- canonical run truth from Slice 12C, trace and adjudication truth from Slice 12B, durable learnings, feedback and outcome memory, next-run focus decisions, and explicit workspace-level continuity policy

## Fallback Rule

- if workspace state is unavailable, Relaytic must still preserve the current Slice 12C handoff and learnings surfaces while recording that workspace continuity is degraded rather than silently reconstructing continuity from filenames or folder guesses

## Required behavior

- every serious run should belong to a workspace once continuity exists; Relaytic must not rely on parent-directory heuristics as the primary continuity mechanism
- Slice 12C handoff artifacts remain public and valid, but they should become per-run snapshots mirrored into workspace-backed continuity instead of competing truth sources
- Relaytic must generate one machine-stable `result_contract.json` per serious run that states:
  - what Relaytic currently believes
  - how strong the evidence is
  - what remains unresolved
  - what Relaytic recommends next
  - what would change its mind
- `reports/user_result_report.md` and `reports/agent_result_report.md` must become differentiated renderings of `result_contract.json`, not separate reasoning products
- governed learnings must become typed records with explicit source, confidence, status, reaffirmation state, invalidation history, and optional expiry rather than free-form sticky memory
- Relaytic must maintain workspace lineage and focus history so later runs can explain how the current direction evolved
- Relaytic must emit one explicit `next_run_plan.json` that can choose between:
  - `same_data`
  - `add_data`
  - `new_dataset`
  and should also state the lower-level reason, such as more search, recalibration, retraining, incumbent comparison, or restart
- mission control, assist, and MCP must expose workspace continuity, result-contract posture, and next-run planning directly instead of only showing the current run
- memory retrieval should prefer explicit workspace state and governed learnings over loose analog assumptions when both are available
- existing `relaytic handoff *` and `relaytic learnings *` commands must remain supported as compatibility-preserving views over workspace-backed truth once Slice 12D lands

## Proof obligation

- Relaytic must prove that multi-run continuity is explicit, governed, and machine-usable rather than hidden in prose, path conventions, or operator memory

## Acceptance criteria

Slice 12D is acceptable only if:

1. one workspace carries at least two runs with visible lineage and focus history
2. one run proves that the user report and agent report are differentiated renderings of the same `result_contract.json`
3. one next-run plan chooses `add_data` or `new_dataset` because the value contract says deeper search on the same data is low value
4. one governed-learning case invalidates or expires stale guidance without deleting its history
5. one mission-control or assist surface shows current belief, confidence posture, unresolved items, recommended next move, and belief-revision triggers from workspace-backed truth
6. one external-agent or MCP case continues a workspace using machine-stable workspace and next-run-plan artifacts rather than scraping markdown
7. one compatibility case proves that existing Slice 12C handoff and learnings commands still work on top of workspace-backed truth

## Required verification

Slice 12D should not be considered complete without targeted tests that cover at least:

- one multi-run workspace lineage case
- one result-contract rendering-parity case
- one governed-learning invalidation or expiry case
- one next-run planner case that chooses between same data, add data, and new dataset
- one mission-control or assist workspace-continuity case
- one external-agent or MCP workspace-continuation case
- one memory-integration case where workspace truth overrides weaker analog guesses
- all relevant proof categories from `docs/specs/test_and_proof_matrix.md`
