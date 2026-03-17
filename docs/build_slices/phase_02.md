# Slice 02 - Mandate and Context Foundation

## Goal

Add stable mandate and context objects with resolved config writing.

## Expected Outputs

- `policy_resolved.yaml`
- `lab_mandate.json`
- `work_preferences.json`
- `run_brief.json`
- `data_origin.json`
- `domain_brief.json`
- `task_brief.json`

## Implemented In This Slice

- `src/relaytic/mandate/models.py`
- `src/relaytic/mandate/storage.py`
- `src/relaytic/context/models.py`
- `src/relaytic/context/storage.py`
- canonical policy normalization in `src/relaytic/policies/loader.py`
- `relaytic mandate init`
- `relaytic mandate show`
- `relaytic context init`
- `relaytic context show`
- `relaytic foundation init`

## Done Criteria

- mandate artifacts are written with stable schema versions
- context artifacts are written with stable schema versions
- `policy_resolved.yaml` uses a canonical Relaytic policy shape
- foundation commands update `manifest.json` automatically
- tests cover deterministic flows and local-stub-LLM consumption of the foundation artifacts
