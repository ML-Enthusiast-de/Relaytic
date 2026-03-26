# Slice 11B - Mission control MVP, onboarding, and one-command install

## Status

Planned.

Intended package boundaries:

- `src/relaytic/mission_control/`
- extend `src/relaytic/ui/`
- extend `src/relaytic/runtime/`
- extend `src/relaytic/interoperability/`
- extend `scripts/`

Intended artifacts:

- `mission_control_state.json`
- `review_queue_state.json`
- `control_center_layout.json`
- `onboarding_status.json`
- `install_experience_report.json`
- `launch_manifest.json`
- `demo_session_manifest.json`
- `ui_preferences.json`

## Intent

Slice 11B is where Relaytic stops being primarily a CLI-and-artifact experience for operators and becomes a real local control center with a low-friction install and launch path.

The slice is successful only if Relaytic can:

- take a new user from install to verified local launch with one obvious path
- expose current run state, quality/budget posture, incumbent parity, decision-lab posture, and safe assist/control actions from one coherent local surface
- reuse the same runtime and artifact truth already exposed through CLI and MCP
- remain usable even when richer UI extras are unavailable

## Load-Bearing Improvement

- Relaytic should expose one coherent operator cockpit and one low-friction install/onboarding path so humans and external agents can launch, monitor, steer, and demo the lab without stitching together raw artifacts and shell commands

## Human Surface

- humans should be able to install Relaytic, verify the environment, launch one control center, attach a dataset and optional incumbent, inspect stage/timeline/next action, see quality and budget posture, and use assist/control actions without reading raw JSON files

## Agent Surface

- external agents should be able to query the same mission-control state, launch metadata, onboarding posture, review queue, and action cards through stable JSON-first and MCP-accessible surfaces rather than relying on UI-only state

## Intelligence Source

- canonical runtime state, run summaries, quality and budget contracts, benchmark/incumbent artifacts, decision-lab outputs, control and assist state, and doctor/install-health results

## Fallback Rule

- if richer UI dependencies are unavailable, Relaytic must still expose the same control-center truth through CLI, MCP, and stable artifacts; if easy-install extras are unavailable, `python scripts/install_relaytic.py` plus `relaytic doctor` remains the canonical fallback

## Required Behavior

- Relaytic must provide one documented install path that ends in explicit environment verification and a clearly documented way to launch the local control center
- the control center must consume the same canonical runtime and artifact truth already used by CLI and MCP rather than inventing a separate UI-only state machine
- the first operator-facing surface must expose current stage, next recommended action, quality/budget posture, incumbent parity, decision-lab posture, and safe assist/control actions from one coherent view
- dataset selection, intent entry, and optional incumbent attachment should be possible from the same surface or a clearly linked first-run flow rather than through unrelated setup steps
- control-center actions must route through the existing assist and skeptical-control layers instead of bypassing them
- install and onboarding should make base versus full profiles, dependency health, recovery guidance, and host-integration hints explicit instead of leaving setup knowledge to repository archaeology
- every later slice that changes operator-visible behavior, adds major artifact families, or changes dependency posture must extend the same mission-control and onboarding surfaces rather than leaving them stale until Slice 15
- Slice 11B must remain thin: no duplicated business logic, no UI-only calculations, and no forked source of truth

## Proof Obligation

- Relaytic must prove that a new user can install, verify, launch, and inspect one real run from one coherent local surface, and that humans and external agents see the same operator truth regardless of whether they come in through UI, CLI, or MCP

## Acceptance Criteria

Slice 11B is acceptable only if:

1. one fresh-install case reaches explicit environment verification and a launchable local control center from one documented path
2. one run can be monitored and explained from the control center without reading raw artifact files
3. one imported-incumbent case is visible in the control center with honest parity or beat-target state
4. one assist or skeptical-control interaction is visible in the same surface without bypassing guardrails
5. one CLI or MCP consumer sees the same operator truth the control center renders

## Required Verification

Slice 11B should not be considered complete without targeted tests that cover at least:

- one install-flow smoke test
- one control-center launch smoke test
- one run-summary parity case
- one incumbent/benchmark card case
- one assist/control interaction case
- one CLI/MCP/UI parity case
