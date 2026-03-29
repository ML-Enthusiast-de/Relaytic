# Slice 15 - Mission-control expansion, packaging, integrations, demos, and polish

## Status

Planned.

Intended package boundaries:

- `src/relaytic/mission_control/`
- extend `src/relaytic/interoperability/`
- extend `src/relaytic/runtime/`

Intended artifacts:

- `mission_control_state.json`
- `branch_dag.json`
- `confidence_map.json`
- `change_attribution_report.json`
- `review_queue_state.json`
- `trace_explorer_state.json`
- `branch_replay_index.json`
- `demo_pack_manifest.json`
- `flagship_demo_scorecard.json`
- `human_factors_eval_report.json`
- `onboarding_success_report.json`

## Intent

Slice 15 is where Relaytic turns the thinner mission-control and onboarding surface from Slices 11B through 11G into a professional operating surface for humans and external agents.

The slice is successful only if Relaytic can:

- show current stage, branch structure, confidence, intervention history, and next action from one coherent surface
- expose the same mission-control truth through CLI, MCP, and any richer UI shell
- package that experience into demos, onboarding, doctor, backup/restore, and ecosystem integrations that feel like software rather than a research repo
- prove that first-time humans and external agents can actually succeed with that surface instead of only exposing it

## Load-Bearing Improvement

- Relaytic should expose a professional mission-control surface that lets humans and external agents navigate branch history, confidence, traces, interventions, and change attribution while the packaging and integration layer makes that surface survivable for real-world use

## Human Surface

- operators should be able to open one coherent mission-control view showing current stage, branch DAG, confidence map, trace timeline, intervention history, recommended next actions, and environment health

## Agent Surface

- external agents should be able to query the same mission-control state, branch structure, trace explorer state, and change attribution through stable JSON-first surfaces and MCP tools

## Intelligence Source

- canonical runtime events, trace artifacts, artifact graph, benchmark outcomes, feedback/outcome memory, and later ecosystem exports

## Fallback Rule

- if richer UI or ecosystem integrations are unavailable, Relaytic must still expose the same mission-control truth through CLI, MCP, and artifact files without degrading inspectability

## Required Behavior

- Slice 15 must consume the canonical trace model from Slice 12B rather than inventing a separate UI-only activity history
- Slice 15 must build on the mission-control MVP from Slices 11B through 11G rather than replacing it with a separate UI stack
- mission control must make branch, tool, intervention, and confidence state legible without requiring humans or external agents to read raw artifact trees
- CLI, MCP, and any richer UI shell must expose the same mission-control truth with only presentation differences
- packaged demos must include at least one skeptical-control case, one incumbent challenge case, and one trace-backed branch comparison
- packaged demos should become a maintained flagship demo pack with explicit scorecards instead of ad hoc walkthroughs
- Slice 15 must consume the protocol-conformance outputs from Slice 12B and fail loudly when richer UI shells drift from CLI/MCP truth
- Slice 15 must include human-supervision evaluation covering first-run success, stuck recovery, and explanation quality for first-time operators

## Proof Obligation

- Relaytic must prove that humans and external agents can understand why the system changed course without reading raw artifact trees, that mission control is driven by the same trace/runtime truth as the rest of the product, and that first-time users can actually complete meaningful work with the shipped onboarding surface

## Acceptance Criteria

Slice 15 is acceptable only if:

1. one mission-control view replays why Relaytic changed course across at least two branches
2. one agent-consumable mission-control export shows current stage, branch state, and recommended next action without missing trace context
3. one packaged demo shows what changed because of memory, research, feedback, and intervention handling from the same surface
4. one flagship demo pack includes at least:
   - unfamiliar dataset to useful governed decision
   - imported incumbent challenge
   - skeptical override rejection or unsafe-request defense
5. one human-factors or onboarding-success eval shows that a first-time operator can start, recover, and finish a useful flow without repo literacy

## Required Verification

Slice 15 should not be considered complete without targeted tests that cover at least:

- one CLI mission-control case
- one MCP mission-control case
- one trace-backed replay case
- one packaged demo health check
- one human-factors or onboarding-success case
