# Capability Academy Contract

## Purpose

This document freezes the product contract for Relaytic's future capability-academy track.

The academy is the governed subsystem that lets Relaytic discover, trial, promote, demote, and retire new tools and non-core specialist agents without weakening authority, auditability, or rollback safety.

## Core doctrine

The academy must never behave like uncontrolled self-modification.

The academy must always be:

- local-first
- permission-aware
- trace-backed
- replayable
- promotion-gated
- rollbackable

## Core and non-core agents

Core agents are immutable from the academy's point of view.

The academy may:

- propose prompt or method changes for core agents through ordinary reviewed development
- let core agents sponsor or judge candidates

The academy may not:

- delete core agents
- silently replace core agents
- grant core agents hidden authority through academy shortcuts

The academy may recruit or retire only non-core specialists.

## Capability types

The academy must support at least:

- `tool`
- `specialist_agent`

Each capability must declare:

- `capability_id`
- `capability_type`
- `core_status`
- `provider_type`
- `status`
- `owner_role`
- `task_families`
- `domain_fit`
- `required_permissions`
- `risk_level`
- `cost_profile`
- `proof_state`

## Capability lifecycle

Capability state must be explicit.

Minimum lifecycle:

- `candidate`
- `offline_replay`
- `shadow`
- `trial`
- `promoted`
- `watchlist`
- `retired`
- `quarantined`

No capability may jump directly from `candidate` to `promoted`.

## Evaluation pipeline

Every capability candidate must pass through:

1. intake
2. offline replay
3. shadow mode
4. arena comparison
5. narrow live trial where applicable
6. promotion or quarantine decision
7. continuous online watch after promotion

## Shadow mode contract

Shadow mode is non-authoritative.

Shadow mode must:

- run against the same case as the authority path
- never alter the authoritative outcome
- record disagreements
- record counterfactual wins or losses
- record cost and latency
- record safety, permission, and feasibility conflicts

## Hunt mode contract

Hunt mode is bounded autonomous scouting.

Hunt mode may:

- target benchmark gaps
- target repeated workspace failures
- target imported-incumbent deficits
- sample candidates using seeded exploration

Hunt mode may not:

- modify promoted production behavior directly
- bypass permission mode
- run unbounded compute
- invent a second authority path

## Randomness contract

Randomness is allowed only for exploration.

Allowed:

- candidate sampling
- branch ordering
- hunt-pack selection

Not allowed:

- final authority decisions
- final promotion without deterministic scoring
- release or safety conclusions
- audit or provenance generation

Every exploration step must record:

- `seed`
- `sampler`
- `budget_limit`
- `selection_temperature`
- `replay_hash`

## Promotion contract

Promotion must be deterministic and scorecard-backed.

Promotion must consider:

- task-performance change
- cost impact
- latency impact
- safety and permission incidents
- feasibility consistency
- transfer quality
- explanation quality

One candidate must not self-certify its own promotion.

## Retirement contract

Retirement is allowed only for non-core specialists and candidate or promoted tools.

Retirement must be evidence-backed and auditable.

Valid retirement reasons include:

- repeated underperformance
- repeated safety or policy failures
- redundancy with stronger promoted capabilities
- poor transfer outside a narrow niche

## Provider feedback contract

The academy must produce feedback for both successful and failed candidates.

Provider feedback should include:

- measurable gains
- no-gain outcomes
- brittleness
- safety concerns
- transfer strength
- recommended next action

## Surfaces

The academy must eventually be visible through:

- CLI
- MCP
- mission control
- remote supervision

All surfaces must stay aligned on:

- current capability registry
- current candidate state
- current hunt state
- promotion and retirement truth

## Required artifacts

The future academy track must reserve these artifact families:

- `capability_registry.json`
- `capability_card_log.jsonl`
- `capability_intake_record.json`
- `capability_risk_profile.json`
- `offline_replay_scorecard.json`
- `shadow_trial_report.json`
- `shadow_disagreement_log.jsonl`
- `shadow_counterfactual_win_report.json`
- `capability_arena_scorecard.json`
- `promotion_candidate_ranking.json`
- `promotion_decision_report.json`
- `capability_registry_update.json`
- `hunt_campaign_state.json`
- `hunt_target_selection.json`
- `hunt_candidate_log.jsonl`
- `hunt_outcome_report.json`
- `provider_feedback_report.json`
- `exploration_budget_report.json`
- `exploration_seed_log.jsonl`
- `specialist_candidate_queue.json`
- `recruitment_decision_report.json`
- `specialist_trial_report.json`
- `capability_retirement_report.json`
- `roster_change_log.jsonl`
- `academy_state.json`
- `academy_registry_view.json`
- `academy_trial_dashboard.json`
- `academy_hunt_view.json`
- `academy_promotion_timeline.json`
- `academy_explanation_report.json`

## Proof burden

The academy is only credible if it can prove:

- shadow mode does not alter authority truth
- promotion is deterministic and replayable
- non-core specialists can be retired but core agents cannot
- hunt campaigns are budgeted and replayable
- failed candidates still produce reusable feedback
- humans and external agents can ask why a capability was promoted, blocked, or retired and receive a trace-backed answer
