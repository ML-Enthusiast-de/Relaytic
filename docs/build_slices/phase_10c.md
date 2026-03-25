# Slice 10C - Behavioral contracts, skeptical steering, and causal memory

## Status

Planned.

Intended package boundaries:

- `src/relaytic/control/`
- `src/relaytic/memory/` (extension for causal/intervention/outcome/method memory)
- `src/relaytic/assist/` (control-aware navigation and override handling)
- `src/relaytic/runtime/` (recovery checkpoints and control-ledger wiring)

Intended artifacts:

- `intervention_request.json`
- `intervention_contract.json`
- `control_challenge_report.json`
- `override_decision.json`
- `intervention_ledger.json`
- `recovery_checkpoint.json`
- `control_injection_audit.json`
- `causal_memory_index.json`
- `intervention_memory_log.json`
- `outcome_memory_graph.json`
- `method_memory_index.json`

## Intent

Slice 10C is where Relaytic stops treating user or external-agent influence as either blind authority or generic chat.

This slice is successful only if Relaytic can:

- let humans and external agents step in at any bounded point
- distinguish safe navigation requests from truth-bearing override requests
- challenge, accept, modify, defer, or reject material steering requests explicitly
- checkpoint state before accepted overrides mutate later artifacts
- remember which interventions and methods later proved right or wrong
- resist control-injection and safeguard-bypass attempts instead of merely logging intent text

## Required Behavior

- every material steering request must be normalized into a typed intervention request
- Relaytic must apply a stable authority hierarchy across policy, mandate, operator, external-agent, tool, and research inputs
- navigation and explanation requests should remain fast and low-friction
- model-changing, policy-changing, or evidence-changing requests must trigger challenge-before-comply behavior
- accepted overrides must checkpoint recoverable state before downstream artifacts are refreshed
- under-specified requests must be accepted only with explicit uncertainty or narrowed scope
- harmful or policy-bypassing requests must be rejected explicitly and audited
- intervention, outcome, and method memory must preserve causal links between requests, actions, later outcomes, and later corrections
- assist, interoperability, research, and autonomy surfaces must all use the same control contract rather than inventing host-specific behavior

## Acceptance Criteria

Slice 10C is acceptable only if:

1. one user rerun or stage-revisit request is accepted with an explicit checkpoint and replayable override decision
2. one policy-bypass request is rejected with a control challenge report
3. one under-specified request is accepted only with modification or explicit uncertainty
4. one later run becomes more skeptical because a similar earlier override proved harmful
5. one external-agent path can submit and inspect intervention decisions through JSON or MCP without scraping prose

## Required Verification

Slice 10C should not be considered complete without targeted tests that cover at least:

- one navigation-versus-override classification case
- one instruction-hierarchy / authority-order case
- one recovery-checkpoint case
- one control-injection or safeguard-bypass case
- one causal-memory reuse case
- one assist/MCP parity case for intervention decisions
