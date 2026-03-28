# Slice 11F - Demo-grade onboarding, mode education, and stuck recovery

## Load-bearing improvement

Slice 11F is where Relaytic stops being merely understandable to builders and becomes much more legible to first-time demo audiences.

The goal is to make first contact demo-safe:

- explain the shortest useful demo flow
- explain what each major surface is for
- explain what to do when the user is stuck
- keep that guidance available inside mission control and chat instead of only in repo docs

## Human surface

- `relaytic mission-control show`
- `relaytic mission-control launch`
- `relaytic mission-control chat`
- `/demo`
- `/modes`
- `/stuck`
- `docs/handbooks/relaytic_user_handbook.md`
- `docs/handbooks/relaytic_demo_walkthrough.md`

## Agent surface

- mission-control onboarding payload with guided demo flow, mode explanations, and stuck guidance
- handbook stack that explains the product shape to host wrappers and external agents
- stable onboarding questions and action affordances that an agent can replay without improvising

## Intelligence source

- deterministic onboarding structure
- mission-control summary truth
- existing capability/action/question artifacts
- checked-in handbooks and walkthrough docs

Slice 11F should not require an LLM. The onboarding story should be strong even in a deterministic-only environment.

## Fallback rule

If no run exists:

- Relaytic must still explain what it is
- Relaytic must still explain the shortest useful demo flow
- Relaytic must still explain what the modes mean
- Relaytic must still explain what to do when stuck

If a run exists:

- the same demo, mode, and stuck guidance should remain available while preserving the bounded stage and skeptical-control contract

## Required behavior

1. Mission control must expose a guided demo flow directly from onboarding state.
2. Mission control must expose explicit mode explanations directly from onboarding state.
3. Mission control must expose explicit stuck-recovery guidance directly from onboarding state.
4. `relaytic mission-control chat` must support `/demo`, `/modes`, and `/stuck`.
5. Mission-control chat must answer the same questions through natural language, not only slash commands.
6. The human handbook must explain the main flow, what happens next, and what to do when stuck.
7. The agent handbook must explain the safe operating pattern, source-of-truth hierarchy, and what to do when stuck.
8. A separate demo walkthrough must exist for recruiter-safe or first-contact demos.

## Proof obligation

Slice 11F is acceptable only if:

1. one mission-control onboarding case exposes guided demo flow, mode explanations, and stuck guidance
2. one rendered mission-control case shows those sections in the human output
3. one mission-control chat case proves `/demo`, `/modes`, and `/stuck` work
4. one handbook-content case proves the user handbook, agent handbook, and demo walkthrough all cover demo flow and stuck recovery

## Required outputs

- guided demo flow inside `onboarding_status.json`
- mode explanations inside `onboarding_status.json`
- stuck guidance inside `onboarding_status.json`
- onboarding action affordances for demo and stuck recovery
- onboarding starter questions for demo flow, mode explanation, and stuck recovery
- `docs/handbooks/relaytic_demo_walkthrough.md`

## Tests

Slice 11F should not be considered complete without targeted tests that cover at least:

- one mission-control show onboarding case for demo-grade guidance
- one mission-control rendered-output case for the new sections
- one mission-control chat shortcut case for `/demo`, `/modes`, and `/stuck`
- one handbook-content case for user, agent, and walkthrough coverage
