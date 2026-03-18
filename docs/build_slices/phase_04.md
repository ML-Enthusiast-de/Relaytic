# Slice 04 - Intake and Translation Layer

## Goal

Add a real intake layer between raw human or agent input and the normalized
Relaytic foundation artifacts.

## Implemented Baseline

- `src/relaytic/intake/` provides typed intake artifact models, storage helpers,
  deterministic interpretation, and optional bounded local-LLM assistance
- raw free-form notes can be captured with actor/channel provenance
- typed or templated input can be translated into mandate/context/run updates
- dataset-aware semantic mapping can align user phrases to candidate columns
- low-confidence cases emit optional clarification items, but Relaytic still
  continues with logged assumptions instead of waiting by default
- explicit autonomy mode tracks when the operator asked Relaytic to find out
  the details and proceed on its own
- `relaytic intake interpret` ensures the Slice 02 foundation exists, writes
  intake artifacts, updates normalized mandate/context bundles, and refreshes
  the manifest
- `relaytic intake show` prints the Slice 04 artifact bundle from a run directory
- `relaytic intake questions` prints the optional clarification queue together
  with the assumption log and autonomy state

## Outputs

- `intake_record.json`
- `autonomy_mode.json`
- `clarification_queue.json`
- `assumption_log.json`
- `context_interpretation.json`
- `context_constraints.json`
- `semantic_mapping.json`
