# Slice 10 - Feedback assimilation, outcome learning, and reversible policy shaping

## Status

Planned.

Intended package boundary:

- `src/relaytic/feedback/`

Intended artifacts:

- `feedback_intake.json`
- `feedback_validation.json`
- `feedback_effect_report.json`
- `feedback_casebook.json`
- `outcome_observation_report.json`
- `decision_policy_update_suggestions.json`
- `policy_update_suggestions.json`
- `route_prior_updates.json`

## Intent

Slice 10 is where Relaytic starts learning from what happened after the run, not just from what happened during the run.

This slice is successful only if Relaytic can:

- ingest feedback from humans, external agents, runtime failures, benchmark review, and downstream outcomes
- validate whether that feedback is trustworthy, reusable, and worth changing future behavior for
- keep accepted feedback reversible and attributable instead of silently mutating default behavior
- distinguish route-quality feedback from decision-policy feedback, data-quality feedback, and outcome evidence

## Required Behavior

- feedback must remain optional and never block the current deterministic floor
- accepted feedback must produce explicit effect reports instead of hidden behavior drift
- post-deployment outcomes must be allowed to contradict apparently good offline performance
- route, policy, and decision-policy updates must remain suggestions until later slices validate promotion
- accepted feedback must remain distinct from passive run-memory retrieval

## Acceptance Criteria

Slice 10 is acceptable only if:

1. one accepted feedback case improves a later recommendation or route suggestion
2. one rejected or downgraded feedback case avoids poisoning future priors
3. one rollback path removes a prior feedback-derived suggestion cleanly
4. one downstream-outcome case changes a later policy or route recommendation

## Required Verification

Slice 10 should not be considered complete without targeted tests that cover at least:

- one direct user-feedback path
- one external-agent feedback path
- one outcome-observation path
- one adversarial or low-quality feedback rejection path
- one rollback or prior-removal path
