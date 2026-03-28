# Slice 14 - Real-world feasibility, domain constraints, and action boundaries

## Status

Planned.

Intended package boundaries:

- extend `src/relaytic/decision/`
- extend `src/relaytic/lifecycle/`
- extend `src/relaytic/assist/`

Intended artifacts:

- `trajectory_constraint_report.json`
- `feasible_region_map.json`
- `extrapolation_risk_report.json`
- `decision_constraint_report.json`
- `action_boundary_report.json`

## Intent

Slice 14 is where Relaytic stops treating feasibility as a post-hoc warning and starts incorporating domain, policy, and action-boundary constraints directly into what it recommends.

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
- feasibility and action-boundary changes must extend the mission-control surface introduced in Slice 11B and expanded through Slices 11C, 11D, 11E, 11F, and 11G so operator-facing recommendations stay legible as constraints sharpen

## Proof Obligation

- Relaytic must prove that feasibility constraints can materially change recommendations rather than appearing only as side warnings

## Acceptance Criteria

Slice 14 is acceptable only if:

1. one domain case suppresses physically implausible proposals
2. one feasibility constraint materially alters route or recommendation output
3. one operational or compliance constraint alters the decision policy or recommended next action

## Required Verification

Slice 14 should not be considered complete without targeted tests that cover at least:

- one physical-constraint case
- one compliance or operational-constraint case
- one abstention or review-boundary case
