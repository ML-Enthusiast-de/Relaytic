# Slice 14 - Real-world feasibility, domain constraints, and action boundaries

## Status

Planned.

Intended package boundaries:

- extend `src/relaytic/decision/`
- extend `src/relaytic/lifecycle/`
- extend `src/relaytic/assist/`
- extend `src/relaytic/workspace/`
- extend `src/relaytic/permissions/`

Intended artifacts:

- `trajectory_constraint_report.json`
- `feasible_region_map.json`
- `extrapolation_risk_report.json`
- `decision_constraint_report.json`
- `action_boundary_report.json`
- `deployability_assessment.json`
- `review_gate_state.json`
- `constraint_override_request.json`
- `counterfactual_region_report.json`

## Intent

Slice 14 is where Relaytic stops treating feasibility as a post-hoc warning and starts incorporating domain, policy, and action-boundary constraints directly into what it recommends.

This slice must continue obeying:

- `docs/specs/workspace_lifecycle.md`
- `docs/specs/result_contract_schema.md`
- `docs/specs/mission_control_flows.md`
- `docs/specs/test_and_proof_matrix.md`

## Load-Bearing Improvement

- Relaytic should be able to reason about whether a promising route or action is actually allowable, operable, and decision-useful under real domain constraints rather than treating feasibility as a post-hoc warning

## Human Surface

- humans should be able to inspect which physical, regulatory, queue, compliance, or action-boundary constraints changed Relaytic's recommendation

## Agent Surface

- external agents should be able to consume explicit feasibility and action-boundary artifacts without reading narrative reports

## Intelligence Source

- domain constraints, runtime evidence, decision-world models, source contracts, and optional domain-specific reference knowledge

## Fallback Rule

- when explicit domain constraints are missing, Relaytic should emit an under-specified feasibility posture and avoid overclaiming deployability

## Required Behavior

- physical, regulatory, and operational constraints must be explicit inputs to proposal generation, not cosmetic warnings after the fact
- Relaytic must distinguish promising, unproven, physically implausible, operationally infeasible, and policy-constrained proposals
- action-boundary reasoning must integrate with abstention, review, rollback, and data-acquisition suggestions rather than living in a separate report
- feasibility must consume permission modes and approval posture from Slice 13B so infeasible or regulated actions can be approval-gated instead of merely annotated
- feasibility must consume background and resumable job posture from Slice 13C so deferred work, waiting approvals, and long-running experiments remain aligned with real operational constraints
- feasibility must consume the current workspace result contract and next-run plan from Slice 12D so constraint reasoning can change whether Relaytic should continue on the same data, add data, or start over
- feasibility must be able to request an explicit constraint override through `constraint_override_request.json` rather than silently flattening domain conflicts into warnings
- feasibility and action-boundary changes must extend the mission-control surface introduced in Slice 11B and expanded through Slices 11C, 11D, 11E, 11F, and 11G so operator-facing recommendations stay legible as constraints sharpen

## Proof Obligation

- Relaytic must prove that feasibility constraints can materially change recommendations rather than appearing only as side warnings

## Acceptance Criteria

Slice 14 is acceptable only if:

1. one domain case suppresses physically implausible proposals
2. one feasibility constraint materially alters route or recommendation output
3. one operational or compliance constraint alters the decision policy or recommended next action
4. one case emits an explicit review gate or override request rather than only a warning
5. one case changes the workspace next-run posture because feasibility says search or continuation should stop

## Required Verification

Slice 14 should not be considered complete without targeted tests that cover at least:

- one physical-constraint case
- one compliance or operational-constraint case
- one abstention or review-boundary case
- one override-request or review-gate case
- one workspace-next-step change caused by feasibility
