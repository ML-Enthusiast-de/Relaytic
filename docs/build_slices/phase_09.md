# Slice 09 - Intelligence amplification, document grounding, and semantically grounded expert deliberation

## Status

Implemented in the current baseline.

Shipped surface:

- package boundary: `src/relaytic/intelligence/`
- public commands: `relaytic intelligence run` and `relaytic intelligence show`
- current artifacts: `intelligence_mode.json`, `llm_backend_discovery.json`, `llm_health_check.json`, `llm_upgrade_suggestions.json`, `semantic_task_request.json`, `semantic_task_results.json`, `intelligence_escalation.json`, `context_assembly_report.json`, `doc_grounding_report.json`, `semantic_access_audit.json`, `semantic_debate_report.json`, `semantic_counterposition_pack.json`, and `semantic_uncertainty_report.json`

## Intent

Slice 09 is where Relaytic stops treating semantic help as lightweight advisory polish and starts using it as a bounded expert-deliberation substrate.

This slice is successful only if Relaytic becomes better at:

- interpreting difficult labels, notes, and domain constraints
- generating counterpositions instead of one semantic guess
- verifying semantically difficult judgments before they affect route, challenger, or lifecycle logic
- grounding its semantic reasoning in explicit local documents or artifacts

## Weaknesses It Must Close

Without this slice, Relaytic still has these weaknesses:

- internal discussions are mostly deterministic artifact fusion, not semantically strong expert deliberation
- challenger design and retrain rationale remain under-informed when dataset or domain language is ambiguous
- local LLM help exists in places, but not yet through one canonical, inspectable semantic-task contract
- document grounding is still too weak for difficult domain-specific judgments

## Planned Package Boundary

Slice 09 should introduce:

- `src/relaytic/intelligence/`

That package should own semantic-task orchestration, bounded semantic debate/verifier flows, backend discovery, health checks, and document-grounding orchestration.

## Required Outputs

- `intelligence_mode.json`
- `llm_backend_discovery.json`
- `llm_health_check.json`
- `llm_upgrade_suggestions.json`
- `semantic_task_request.json`
- `semantic_task_results.json`
- `intelligence_escalation.json`
- `context_assembly_report.json`
- `doc_grounding_report.json`
- `semantic_access_audit.json`
- `semantic_debate_report.json`
- `semantic_counterposition_pack.json`
- `semantic_uncertainty_report.json`

## Required Behavior

- Relaytic must keep one canonical semantic-task contract
- semantic work must remain JSON-only, schema-bound, and policy-bound
- semantically amplified discussion must emit extracted facts, competing hypotheses, counterarguments, verifier findings, and uncertainty notes explicitly
- semantic context must be capability-aware and rowless by default
- any richer-than-summary access must be audited
- semantically amplified reasoning should be able to improve challenger design, target interpretation, and retrain-vs-recalibrate rationale without becoming a hidden authority

## Acceptance Criteria

Slice 09 is acceptable only if:

1. one semantically difficult judgment improves because Relaytic used proposer/counterposition/verifier packets
2. the same workflow degrades cleanly to deterministic behavior when no semantic backend is available
3. document grounding improves one judgment without exposing raw rows
4. a human and an external agent can both see what semantic evidence changed the outcome

## Required Verification

Slice 09 should not be considered complete without targeted tests that cover at least:

- one semantic counterposition that changes target or constraint interpretation
- one verifier pass that blocks a bad semantic conclusion
- one doc-grounded challenger or retrain rationale improvement
- one capability-policy denial that forces rowless fallback
