# Slice 09D - Private research retrieval, method transfer, and benchmark-aware domain intelligence

## Status

Implemented in the current baseline.

Shipped surface:

- package boundary: `src/relaytic/research/`
- public commands: `relaytic research gather`, `relaytic research show`, and `relaytic research sources`
- current artifacts: `research_query_plan.json`, `research_source_inventory.json`, `research_brief.json`, `method_transfer_report.json`, `benchmark_reference_report.json`, and `external_research_audit.json`

## Intent

Slice 09D is where Relaytic stops relying only on private local evidence and starts importing external method knowledge safely.

This slice is successful only if Relaytic can:

- search papers, benchmark references, and method writeups from a redacted run signature
- convert that retrieval into explicit local hypotheses rather than hidden internet prompt context
- improve planning, challenger design, evaluation design, or benchmark setup without leaking user data
- remain fully usable when networked research is disabled

## Weaknesses It Must Close

Without this slice, Relaytic still has these weaknesses:

- it can reason deeply over local artifacts but cannot yet absorb broader method or benchmark knowledge on demand
- doc grounding is limited to uploaded or already-local material
- benchmark preparation is still too disconnected from literature and reference-method reality
- the system cannot yet act like a private automated research lab for unfamiliar domains

## Package Boundary

Slice 09D introduced:

- `src/relaytic/research/`

That package should own redacted query planning, source-tiered retrieval, local distillation, method-transfer reports, benchmark-reference reports, and research-audit persistence.

## Required Outputs

- `research_query_plan.json`
- `research_source_inventory.json`
- `research_brief.json`
- `method_transfer_report.json`
- `benchmark_reference_report.json`
- `external_research_audit.json`

## Required Behavior

- external research must be opt-in, policy-gated, and advisory
- default research queries must be rowless, redacted, and generalized from run artifacts rather than built from raw rows or private identifiers
- retrieved sources must be typed and tiered such as paper, benchmark reference, implementation docs, reference repo, or operator-supplied reference
- retrieved ideas must become explicit transfer candidates like route ideas, challenger ideas, metric/split ideas, benchmark references, or data-collection suggestions
- local evidence must be able to override retrieved advice explicitly
- every external-research operation must emit a machine-readable audit showing what left the machine, what was redacted, and what source classes were used

## Acceptance Criteria

Slice 09D is acceptable only if:

1. one domain-specific run changes challenger, route, or evaluation design because Relaytic retrieved external references safely
2. the audit proves no raw rows or private identifiers were exported in the default path
3. one retrieved suggestion is rejected because local evidence is stronger
4. the same workflow degrades cleanly when research retrieval is disabled or unavailable

## Required Verification

Slice 09D should not be considered complete without targeted tests that cover at least:

- one redacted research query plan generated from a run signature
- one source inventory and method-transfer distillation path
- one no-network fallback path
- one privacy regression test for raw-row and identifier leakage
