# Slice 11D - Guided onboarding, live terminal mission-control chat, and capability explanations

## Load-bearing improvement

Slice 11D is where Relaytic stops assuming a new operator already understands the product shape.

The goal is to make first contact legible:

- explain what Relaytic is
- explain what it needs first
- explain why some capabilities are unavailable
- explain how the dashboard differs from terminal chat
- give users and external agents a real terminal question surface instead of forcing them to discover the right command by accident

## Human surface

- `relaytic mission-control show`
- `relaytic mission-control launch`
- `relaytic mission-control launch --interactive`
- `relaytic mission-control chat`
- clearer `relaytic assist chat`

## Agent surface

- the quick mission-control payload should expose enough onboarding truth for external agents to guide setup without scraping prose
- onboarding-first question starters should be visible through the same shared mission-control bundle
- assist and mission-control chat should preserve bounded-stage and skeptical-control language instead of collapsing into a permissive shell

## Intelligence source

- deterministic onboarding and capability explanations
- existing assist/control state
- existing host/interoperability inventory
- existing doctor/install state

Optional local semantic phrasing can still exist later, but Slice 11D should not require an LLM to feel understandable.

## Fallback rule

If no run exists:

- Relaytic must still explain what it is
- Relaytic must still explain the first steps
- Relaytic must still explain the dashboard-versus-chat split
- Relaytic must still explain capability reasons and activation hints

If a run exists:

- Relaytic must still preserve the same bounded stage rerun and skeptical-control rules already established in Slices 09E, 10C, and 11C

## Required behavior

1. Mission control must clearly explain that Relaytic is a local-first structured-data lab.
2. Mission control must clearly say that Relaytic needs data plus a goal before deeper run capabilities become meaningful.
3. Disabled or unavailable capabilities must show both:
   - why they are unavailable
   - what activates them
4. Mission control must clearly distinguish:
   - dashboard inspection
   - terminal chat
   - run creation
   - host integration
5. `relaytic mission-control chat` must answer onboarding questions directly.
6. `relaytic mission-control launch --interactive` must drop into terminal chat after the dashboard is materialized.
7. `relaytic assist chat` must expose clearer startup guidance and shortcut commands for capabilities, stages, next action, and takeover.

## Proof obligation

Slice 11D is acceptable only if:

1. one onboarding-only mission-control case exposes what Relaytic is, what it needs, first steps, live chat entry, and capability reasons
2. one onboarding chat case answers `what can you do?` or equivalent without requiring a run
3. one interactive launch case proves the dashboard and terminal chat can be entered through one flow
4. one existing-run assist-chat case proves the clearer shortcuts still preserve bounded-stage language and skeptical-control framing

## Required outputs

- clearer onboarding fields inside `onboarding_status.json`
- clearer capability reasons and activation hints inside `capability_manifest.json`
- `relaytic mission-control chat`
- `relaytic mission-control launch --interactive`
- clearer `relaytic assist chat`

## Tests

Slice 11D should not be considered complete without targeted tests that cover at least:

- one onboarding mission-control visibility case
- one onboarding terminal-chat case
- one interactive launch case
- one existing-run assist-chat clarity case
