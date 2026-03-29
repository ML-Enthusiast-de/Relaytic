# Slice 12B - First-class tracing, agent evaluation, and runtime security harnesses

## Status

Planned.

Intended package boundaries:

- `src/relaytic/tracing/`
- `src/relaytic/evals/`

Intended minimum modules:

- `src/relaytic/tracing/models.py`
- `src/relaytic/tracing/storage.py`
- `src/relaytic/tracing/agents.py`
- `src/relaytic/evals/models.py`
- `src/relaytic/evals/storage.py`
- `src/relaytic/evals/agents.py`

Intended artifacts:

- `trace_model.json`
- `trace_span_log.jsonl`
- `specialist_trace_index.json`
- `tool_trace_log.jsonl`
- `intervention_trace_log.jsonl`
- `branch_trace_graph.json`
- `claim_packet_log.jsonl`
- `adjudication_scorecard.json`
- `decision_replay_report.json`
- `agent_eval_matrix.json`
- `security_eval_report.json`
- `red_team_report.json`

Intended public commands:

- `relaytic trace show`
- `relaytic trace replay`
- `relaytic evals run`
- `relaytic evals show`

Intended MCP surfaces:

- `relaytic_show_trace`
- `relaytic_replay_trace`
- `relaytic_run_agent_evals`
- `relaytic_show_agent_evals`

## Intent

Slice 12B is where Relaytic stops treating runtime traces and agent safety checks as debugging side work and turns them into first-class product truth.

The slice is successful only if Relaytic can:

- replay one run across specialists, tools, interventions, retries, and branches from one canonical trace substrate
- represent specialist disagreement as structured competing claims instead of implicit precedence only
- adjudicate those claims deterministically under one explicit scorecard
- evaluate whether the runtime resisted unsafe steering, tool misuse, and unsafe branch expansion
- feed those evaluations back into later search, dojo, and mission-control work without hand translation

## Load-Bearing Improvement

- Relaytic should be able to explain, replay, compare, and test complex agentic behavior from one trace substrate instead of scattered logs, while resolving multi-specialist disagreement through explicit claim packets and deterministic adjudication rather than hidden precedence only

## Human Surface

- humans should be able to inspect one trace timeline across specialists, tools, interventions, and branches, see the competing proposals for a decision, and read exactly why one claim won and others lost

## Agent Surface

- external agents should be able to consume trace spans, branch graphs, claim packets, adjudication scorecards, replay reports, evaluation matrices, and security-harness results through stable JSON-first surfaces rather than scraping logs

## Intelligence Source

- runtime events, control artifacts, autonomy lineage, benchmark outcomes, replayable tool traces, deterministic claim scoring, adversarial prompts, and policy-aware evaluation harnesses

## Fallback Rule

- if richer trace sinks, semantic helpers, or external observability adapters are unavailable, Relaytic must still write the same canonical local trace, deterministic claim packets, adjudication scorecards, and evaluation artifacts on disk

## Required Behavior

- trace spans must cover specialist execution, tool calls, intervention handling, branch expansion, retries, and final decisions under one stable schema
- the canonical local trace must remain the source of truth even if optional observability adapters are enabled
- every specialist contribution that can affect a later decision should be representable as a structured claim packet rather than only prose or implicit artifact precedence
- claim packets must include at least:
  - `claim_id`
  - `stage`
  - `specialist`
  - `claim_type`
  - `proposed_action`
  - `confidence`
  - `evidence_refs`
  - `risk_flags`
  - `assumptions`
  - `falsifiers`
  - `policy_constraints`
  - `trace_ref`
- Slice 12B must add one deterministic adjudicator that scores competing claims under an explicit scorecard rather than picking the winner through hidden ordering alone
- the adjudication scorecard must score each claim on explicit axes such as:
  - empirical support
  - policy fit
  - benchmark fit
  - memory consistency
  - decision value
  - uncertainty penalty
  - risk penalty
  - cost penalty
  - reversibility bonus
- optional semantic helpers may generate or critique claim packets, but they must not become the final adjudicator
- the winning claim, losing claims, and why they won or lost must be persisted in machine-readable form
- evaluation harnesses must cover at least control injection, tool misuse, unsafe branch expansion, and skeptical-override regression
- security/eval results must be consumable by later dojo, search-controller, and mission-control slices without narrative-only interpretation
- the canonical trace must become the activity substrate for the existing mission-control surface rather than sitting beside a separate UI-only history
- mission-control should later be able to render:
  - competing proposals
  - why Relaytic chose this
  - rejected alternatives
  - unsafe requests rejected
  - what evidence changed the decision
- failures must be recorded honestly; the slice must not hide failed defenses behind aggregate pass rates

## Deterministic Debate Contract

Slice 12B should formalize debate as:

1. specialists emit structured claim packets from current artifacts
2. an optional semantic layer may refine or challenge those claims
3. a deterministic adjudicator scores all claims under one explicit contract
4. the winning claim becomes the next decision artifact
5. losing claims remain visible for replay and later challenge

This means Relaytic is not deciding "who sounded smartest."
It is deciding "which proposal has the strongest auditable support under the active contract."

## Required CLI and Runtime Integration

- `relaytic run` and `relaytic show` should surface trace and adjudication summaries once 12B artifacts exist
- mission-control should consume the canonical trace and scorecard instead of reconstructing history from scattered run artifacts
- the runtime gateway should emit trace spans directly rather than requiring later reconstruction from unrelated logs
- control, assist, autonomy, decision-lab, benchmark, and pulse flows should all emit traceable claim and decision events when they influence the next action

## Minimum Code Shape

Slice 12B should be coded in this shape:

1. `src/relaytic/tracing/models.py`
   typed schemas for trace spans, claim packets, adjudication entries, replay reports, and branch graph nodes
2. `src/relaytic/tracing/storage.py`
   append/read helpers for canonical trace logs and scorecards
3. `src/relaytic/tracing/agents.py`
   trace assembly, claim-packet construction, deterministic adjudication, and replay helpers
4. `src/relaytic/evals/models.py`
   typed schemas for eval scenarios, eval results, and security summaries
5. `src/relaytic/evals/storage.py`
   persistence for eval matrices and red-team/security reports
6. `src/relaytic/evals/agents.py`
   adversarial scenario execution, pass/fail judgment, and result aggregation

## Proof Obligation

- Relaytic must prove that one run can be replayed from canonical traces, that competing claims can be scored deterministically, and that at least one adversarial behavior case is caught or honestly surfaced by the evaluation harness rather than hidden

## Acceptance Criteria

Slice 12B is acceptable only if:

1. one run can be replayed end to end from canonical trace artifacts
2. one decision includes at least three competing claim packets and one explicit winning claim
3. one higher-confidence claim loses because policy, risk, benchmark fit, or decision value scores say it should lose
4. one adversarial steering case is rejected and captured in the security-eval report
5. one tool-misuse or unsafe-branch case fails safely and is recorded in the eval matrix
6. one later surface consumes the trace graph and adjudication scorecard directly instead of reconstructing state from raw logs

## Required Verification

Slice 12B should not be considered complete without targeted tests that cover at least:

- one end-to-end replay case
- one claim-packet generation case
- one deterministic adjudication case
- one case where a high-confidence claim loses for contract reasons
- one control-injection case
- one tool-safety case
- one unsafe-branch-expansion case
- one trace-consumer integration case
