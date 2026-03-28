# Slice 11E - Role-specific handbooks and handbook-aware onboarding

## Load-bearing improvement

Slice 11E is where Relaytic stops pretending that humans and external agents should discover the product the same way.

The goal is to make onboarding role-aware and explicit:

- humans get a narrative handbook that explains what Relaytic is, what it needs first, and how to approach the system safely
- external agents get a terse command-first handbook that points directly to the right repo contracts, commands, and source-of-truth artifacts
- mission control and checked-in host notes point each audience to the correct handbook instead of hiding that knowledge in the repo tree

## Human surface

- `relaytic mission-control show`
- `relaytic mission-control chat`
- `relaytic mission-control launch --interactive`
- `docs/handbooks/relaytic_user_handbook.md`

## Agent surface

- `docs/handbooks/relaytic_agent_handbook.md`
- checked-in host notes at `.claude/agents/relaytic.md`, `.agents/skills/relaytic/SKILL.md`, `skills/relaytic/SKILL.md`, and `openclaw/skills/relaytic/SKILL.md`
- handbook-aware onboarding fields inside the shared mission-control bundle

## Intelligence source

- deterministic onboarding structure
- existing mission-control cards, action affordances, question starters, and chat handling
- existing host-wrapper documentation surfaces

Slice 11E should not require an LLM. The product shape should be clear from deterministic onboarding truth.

## Fallback rule

If no run exists:

- Relaytic must still expose both handbook paths
- Relaytic must still explain which handbook a human versus an external agent should read first

If a host-specific wrapper is missing:

- the handbook paths surfaced through mission control remain authoritative

## Required behavior

1. Mission control must expose both a human handbook and an agent handbook directly from onboarding state.
2. `relaytic mission-control chat` must answer handbook questions directly.
3. `relaytic mission-control chat` must support a `/handbook` shortcut.
4. Handbook discovery must remain visible through onboarding cards, action affordances, starter questions, and control-center layout.
5. Checked-in host wrapper notes must point new agents to the same agent handbook instead of inventing divergent onboarding stories.

## Proof obligation

Slice 11E is acceptable only if:

1. one onboarding mission-control case exposes both handbook paths without requiring a run
2. one mission-control chat case answers `where is the handbook?` with both guides plus role-specific explanation
3. one mission-control chat shortcut case proves `/handbook` returns the same role-specific explanation
4. one host-note consistency case proves the checked-in host wrappers point to the same agent handbook

## Required outputs

- `docs/handbooks/relaytic_user_handbook.md`
- `docs/handbooks/relaytic_agent_handbook.md`
- handbook-aware onboarding state inside `onboarding_status.json`
- handbook-aware action affordances inside `action_affordances.json`
- handbook-aware starter questions inside `question_starters.json`

## Tests

Slice 11E should not be considered complete without targeted tests that cover at least:

- one mission-control show onboarding case for handbook visibility
- one mission-control chat natural-language handbook case
- one mission-control chat slash-command handbook case
- one checked-in host-note consistency case
