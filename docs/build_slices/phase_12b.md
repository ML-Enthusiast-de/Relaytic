# Slice 12B - First-class tracing, agent evaluation, and runtime security harnesses

## Status

Planned.

Intended package boundaries:

- `src/relaytic/tracing/`
- `src/relaytic/evals/`

Intended artifacts:

- `trace_model.json`
- `trace_span_log.jsonl`
- `specialist_trace_index.json`
- `tool_trace_log.jsonl`
- `intervention_trace_log.jsonl`
- `branch_trace_graph.json`
- `agent_eval_matrix.json`
- `security_eval_report.json`
- `red_team_report.json`

## Intent

Slice 12B is where Relaytic stops treating runtime traces and agent safety checks as debugging side work and turns them into first-class product truth.

The slice is successful only if Relaytic can:

- replay one run across specialists, tools, interventions, retries, and branches from one canonical trace substrate
- evaluate whether the runtime resisted unsafe steering, tool misuse, and unsafe branch expansion
- feed those evaluations back into later search, dojo, and mission-control work without hand translation

## Load-Bearing Improvement

- Relaytic should be able to explain, replay, compare, and test complex agentic behavior from one trace substrate instead of scattered logs, while continuously evaluating whether the runtime resists unsafe steering, tool misuse, and branch-controller errors

## Human Surface

- humans should be able to inspect one trace timeline across specialists, tools, interventions, and branches, plus visible security/evaluation summaries that explain where Relaytic held the line or failed

## Agent Surface

- external agents should be able to consume trace spans, branch graphs, evaluation matrices, and security-harness results through stable JSON-first surfaces rather than scraping logs

## Intelligence Source

- runtime events, control artifacts, autonomy lineage, benchmark outcomes, replayable tool traces, adversarial prompts, and policy-aware evaluation harnesses

## Fallback Rule

- if richer trace sinks or external observability adapters are unavailable, Relaytic must still write the same canonical local trace and evaluation artifacts on disk

## Required Behavior

- trace spans must cover specialist execution, tool calls, intervention handling, branch expansion, retries, and final decisions under one stable schema
- the canonical local trace must remain the source of truth even if optional observability adapters are enabled
- evaluation harnesses must cover at least control injection, tool misuse, unsafe branch expansion, and skeptical-override regression
- security/eval results must be consumable by later dojo, search-controller, and mission-control slices without narrative-only interpretation
- the canonical trace must become the activity substrate for the existing mission-control surface rather than sitting beside a separate UI-only history
- failures must be recorded honestly; the slice must not hide failed defenses behind aggregate pass rates

## Proof Obligation

- Relaytic must prove that one run can be replayed from canonical traces and that at least one adversarial behavior case is caught or honestly surfaced by the evaluation harness rather than hidden

## Acceptance Criteria

Slice 12B is acceptable only if:

1. one run can be replayed end to end from canonical trace artifacts
2. one adversarial steering case is rejected and captured in the security-eval report
3. one tool-misuse or unsafe-branch case fails safely and is recorded in the eval matrix
4. one later surface consumes the trace graph directly instead of reconstructing state from raw logs

## Required Verification

Slice 12B should not be considered complete without targeted tests that cover at least:

- one end-to-end replay case
- one control-injection case
- one tool-safety case
- one unsafe-branch-expansion case
- one trace-consumer integration case
