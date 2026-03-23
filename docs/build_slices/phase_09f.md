# Slice 09F - Routed Intelligence Profiles, Capability Matrices, and Semantic Proof

## Status

Implemented in the current baseline.

Shipped surface:

- package boundary: `src/relaytic/intelligence/`
- current artifacts: `llm_routing_plan.json`, `local_llm_profile.json`, `verifier_report.json`, and `semantic_proof_report.json`
- upgraded public commands: `relaytic intelligence run`, `relaytic intelligence show`, and `relaytic show`

## Intent

Slice 09F turns the LLM layer from an optional hidden enhancement into an explicit, bounded, inspectable semantic-routing system.

This slice is successful only if Relaytic can:

- normalize configured intelligence labels into canonical semantic modes
- explain which local profile or backend path it selected and why
- show what the verifier concluded as a standalone artifact
- prove whether semantic amplification changed any bounded semantic outputs relative to the deterministic semantic baseline

## Required Behavior

- routed intelligence must remain optional, local-first by default, and subordinate to deterministic execution and adjudication layers
- one canonical routing artifact must expose requested, recommended, and selected semantic modes
- one local profile artifact must expose the selected local semantic baseline when applicable
- backend capability reporting must stay bounded to features relevant for schema-constrained semantic tasks
- verifier results must be readable without reparsing the entire semantic debate packet
- semantic proof must record whether routed semantic work changed target interpretation, challenger direction, confidence, or other bounded semantic outputs

## Acceptance Criteria

Slice 09F is acceptable only if:

1. one deterministic run still produces explicit routing and local-profile artifacts without requiring an LLM
2. one local-LLM run produces a visible routed mode and selected profile
3. one verifier artifact records whether the selected semantic action changed relative to the deterministic baseline
4. one semantic-proof artifact records whether measurable bounded semantic gain was detected
5. `relaytic intelligence show` and `relaytic show` agree on routed mode and local profile

## Required Verification

Slice 09F should not be considered complete without targeted tests that cover at least:

- one legacy-mode normalization case
- one minimum-local-profile routing case
- one verifier delta case
- one semantic-proof case
- one CLI intelligence surface regression showing the new artifacts are materialized and visible
