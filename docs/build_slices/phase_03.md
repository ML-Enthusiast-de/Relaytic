# Slice 03 - Focus Council and Investigation Baseline

## Goal

Add the first Relaytic investigation layer before real planning and search.

## Implemented Baseline

- `src/relaytic/investigation/` provides typed artifact models, storage helpers, and the Slice 03 pipeline
- `ScoutAgent` performs deterministic dataset inspection and leakage-aware profiling
- `ScientistAgent` turns Scout evidence plus mandate/context into grounded route and task hypotheses
- `FocusCouncilAgent` resolves objective priorities deterministically with optional bounded local-LLM advisory nudges
- `relaytic investigate` ensures the Slice 02 foundation exists, runs the investigation pipeline, writes artifacts, and refreshes the manifest

## Expected Outputs

- `dataset_profile.json`
- `domain_memo.json`
- `objective_hypotheses.json`
- `focus_debate.json`
- `focus_profile.json`
- `optimization_profile.json`
- `feature_strategy_profile.json`
