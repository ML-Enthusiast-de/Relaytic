# Slice 05A

## Scope

Land the first truly usable Relaytic MVP shell:

- one-shot `relaytic run`
- concise `relaytic show`
- discoverable `relaytic predict`
- machine-readable run summary
- human-readable run report

## Landed

- `src/relaytic/runs/` with summary and report materialization helpers
- `relaytic run`
- `relaytic show`
- `relaytic predict`
- `run_summary.json`
- `reports/summary.md`

## Contract Notes

- this slice does not replace intake, investigation, or planning
- it is a thin orchestration and presentation layer over the real specialist pipeline
- summary artifacts are meant for both human comprehension and agent consumption
- manifest paths for nested artifacts are now normalized to POSIX-style relative paths

## Verification

- CLI access-surface tests
- summary bootstrapping tests for older run directories
- full regression suite
