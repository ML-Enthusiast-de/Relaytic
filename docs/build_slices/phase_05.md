# Slice 05

## Scope

Land the first real Strategist-to-Builder bridge:

- planning artifacts
- explicit Builder handoff
- one deterministic local route from data to model
- same-run artifact persistence
- optional local planning advisory

## Landed

- `src/relaytic/planning/` with typed models, storage helpers, local advisory support, and Strategist orchestration
- `relaytic plan create`
- `relaytic plan run`
- `relaytic plan show`
- `plan.json`
- `alternatives.json`
- `hypotheses.json`
- `experiment_priority_report.json`
- `marginal_value_of_next_experiment.json`
- first deterministic Builder execution into the same Relaytic run directory

## Contract Notes

- planning consumes foundation plus investigation artifacts, not unstructured prose alone
- the Builder handoff is embedded in `plan.json`
- hard exclusions and soft heuristic feature-risk signals are treated differently
- local LLM advice is optional and bounded to structured planning suggestions

## Verification

- planning tests
- CLI Slice 05 tests
- end-to-end inference-from-run-dir coverage
- local stub LLM planning advisory tests
- adjacent Slice 03 and Slice 04 regression coverage
