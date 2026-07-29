# Relaytic UI Frontier Review

Date: 2026-05-07

Status: historical design review. The AML investigation board, demo flow,
mission-control artifacts, and guidance surfaces described below have since
landed. A richer live browser server and several interactive views remain
planned. Use `IMPLEMENTATION_STATUS.md` for current status.

## Verdict

At the time of review, Relaytic had a useful artifact-backed control surface,
but the operator experience was still incomplete.

The current UI is artifact-rich and honest. It writes mission-control JSON artifacts plus a static local HTML report, and it exposes terminal chat for onboarding and guidance. That is a credible MVP control plane.

The next version should become an AML operating room: a local browser workspace where humans and external agents can inspect the same truth, understand why Relaytic believes something, compare alternatives, approve or reject actions, and continue work without reading raw JSON or memorizing CLI commands.

## What Exists Now

Current command surface:

- `relaytic mission-control show`
- `relaytic mission-control launch`
- `relaytic mission-control chat`

Current UI mode:

- static local HTML report
- terminal chat for interaction
- JSON-first artifacts for agents and MCP callers

Current mission-control artifacts include:

- `mission_control_state.json`
- `control_center_layout.json`
- `mode_overview.json`
- `capability_manifest.json`
- `action_affordances.json`
- `stage_navigator.json`
- `question_starters.json`
- `onboarding_chat_session_state.json`
- `branch_dag.json`
- `confidence_map.json`
- `change_attribution_report.json`
- `trace_explorer_state.json`
- `approval_timeline.json`
- `background_job_view.json`
- `permission_mode_card.json`
- `release_health_report.json`
- `demo_pack_manifest.json`
- `flagship_demo_scorecard.json`
- `human_factors_eval_report.json`
- `onboarding_success_report.json`
- `reports/mission_control.html`

Observed onboarding surface from `relaytic mission-control show --format json`:

- current stage: `onboarding`
- recommended action: `launch_or_run`
- next actor: `operator`
- launch ready: `true`
- doctor status: `ok`
- card count: `11`
- capability count: `14`
- action count: `13`
- question count: `14`
- demo ready count: `0`
- demo story count: `5`
- first-run success ready: `true`

This is a lot of useful truth. The weakness is not missing state. The weakness is that most of the state is still rendered as cards, lists, and command hints rather than as a deeply usable operating workflow.

## What The Current UI Shows Well

- Install and doctor posture.
- First-contact onboarding.
- Captured dataset path and objective from mission-control chat.
- Capability availability and activation hints.
- Action affordances.
- Stage navigation scope.
- Question starters.
- Demo readiness.
- Release safety posture.
- Trace, permission, background job, and approval placeholders.

## What It Does Not Yet Show Strongly Enough

- A clear AML-first workspace view.
- The active investigation object: entity, alert queue, typology, drift window, or benchmark track.
- The current belief and what would change it.
- Review-budget tradeoffs as a first-class visual object.
- Business-value metrics such as analyst-hours saved or false positives avoided.
- Side-by-side incumbent versus Relaytic comparison.
- Graph/subgraph evidence as an inspectable network or motif view.
- Timeline of drift, delayed labels, recalibration, and threshold changes.
- Human approval state as a true workflow, not just a report.
- Agent handoff state: which artifact an external agent should read next and which command it should run next.
- Live updates while a long run, daemon job, benchmark, or search loop is active.
- A compact public demo mode that hides construction scaffolding and shows the story cleanly.

## Product Direction

Mission Control should split into two related surfaces:

- **Operator Console**
  The human browser workspace for running and supervising Relaytic.

- **Agent Console**
  A terse, JSON-linked control surface for Claude Code, ChatGPT connectors, OpenClaw, Codex, and MCP clients.

Both should read the same artifacts. They should never invent separate truth.

## First-Contact UI Contract

For Slice 15Y, first-contact docs should describe four UI layers clearly:

- **Static fallback:** `relaytic mission-control launch` writes and opens a local static HTML report. This remains the dependable no-server view.
- **AML investigation board:** the flagship workflow view for the review queue, case packet, graph/typology evidence, drift posture, benchmark guard, public-claim guard, and AML environment scorecard.
- **Agent Console:** the command-first and JSON-linked surface for external agents that need `run_summary.json`, guide payloads, external context packs, and exact artifact paths.
- **Local live UI server:** a later local-only server direction for live updates, event subscription, trace replay, approvals, benchmark runs, and richer filtering. It must read canonical artifacts rather than becoming a second backend truth.

The public demo should send a new reviewer to the static fallback and AML investigation board first. The Agent Console and future live server should be explained as operating surfaces over the same artifact graph, not as separate products.

## Proposed UI Architecture

### 1. Static HTML remains the fallback

Keep the current static report because it is simple, local-first, and robust.

It should remain the guaranteed fallback when no server is running.

### 2. Add a local live UI server

Add:

- `relaytic ui serve`
- `relaytic ui open`
- `relaytic ui status`

The live UI should run locally, read the artifact graph, subscribe to runtime events, and expose actions through the same permission/control contracts.

It should not become a separate backend truth.

### 3. Add a frontend app only after the contract is clear

A React or similar app is justified only when it gives:

- live run progress
- filters and drilldown
- graph views
- approval workflows
- comparison tables
- trace replay
- demo mode

Do not add a frontend just to repaint the current cards.

## What The Browser UI Should Show

### Top Bar

Always visible:

- workspace
- run
- stage
- mode
- next actor
- current recommended action
- confidence
- unresolved count
- permission mode
- local/remote/daemon status

### Primary Workspace

The primary view should change by state:

- no run: onboarding and data/objective capture
- active run: live run timeline and current decision
- completed run: result contract, next-run plan, and proof status
- AML run: AML investigation board
- demo run: public-safe demo narrative and proof pack

### AML Investigation Board

This should be the flagship screen.

Show:

- dataset family: PaySim-style, Elliptic-style, flattened graph, raw graph, subgraph pack
- target and task posture
- rare-event and weak-label posture
- review budget
- alert queue
- top case packet
- top entity or subgraph
- typology candidates
- drift and delayed-label posture
- threshold and calibration status
- benchmark and public-claim guard
- failure report

### Alert Queue View

Users need this more than another metrics panel.

Show:

- ranked alerts or entity cases
- expected review cost
- reason codes
- typology tags
- graph evidence
- model score
- uncertainty
- case completeness
- action recommendation

Actions:

- mark reviewed
- defer
- request more evidence
- compare threshold
- export case packet

For now, those actions can write local simulated review artifacts. They should not imply production integration.

### Case Packet View

Show one case like an analyst would need it:

- entity
- why this case
- connected counterparties
- suspicious path or motif
- transaction summary
- temporal pattern
- model/graph/typology evidence
- uncertainty
- missing evidence
- recommended next step

This is the screen that can make Relaytic-AML feel real.

### Benchmark And Claims View

Show:

- dev versus holdout partition
- PaySim-style coverage
- Elliptic-style coverage
- baseline matrix
- ablation matrix
- public-claim guard
- paper-claim guard
- failure report

The UI should make blocked claims feel professional, not disappointing.

### Business Value View

Show:

- precision at top-k
- recall at review capacity
- false-positive reduction at fixed recall
- analyst-hours saved
- alert-to-case quality
- threshold stability
- operational metric guard

This should sit beside model metrics, not below them.

### Incumbent Challenge View

Show side-by-side:

- incumbent
- Relaytic
- same split
- same threshold/review budget
- same metric contract
- where Relaytic wins
- where Relaytic loses
- whether the claim is allowed

Actions:

- import ruleset
- import prediction file
- import model
- run fair comparison
- inspect beat-target contract

### Trace Replay View

Show:

- specialist turns
- tool calls
- branch decisions
- intervention decisions
- competing claims
- winning claim
- adjudication score
- what changed because of memory, research, feedback, or user steering

The trace view should be a readable story, not a log dump.

### Agent Handoff View

Every run should show:

- canonical artifact to read first
- next command
- current MCP readiness
- host status for Claude Code, ChatGPT, OpenClaw, Codex
- safe action affordances
- blocked action reasons

This should make external agents feel like first-class operators.

## Features Users Will Want

- paste a dataset path into the browser
- drag and drop local CSV/Parquet/Excel/JSONL
- choose quick analysis versus governed run
- see "what is Relaytic doing now?"
- pause, resume, or stop long work
- approve, deny, or modify proposed actions
- ask "why this case?"
- ask "what would change your mind?"
- compare thresholds visually
- compare incumbent versus Relaytic fairly
- export a case packet
- export a public-safe proof bundle
- see exactly why a claim is blocked
- continue tomorrow without remembering commands

## Features Agents Will Want

- stable run/workspace IDs
- canonical "read this first" artifact
- canonical "do this next" command
- action affordances with permission requirements
- machine-readable blocked reasons
- MCP tool parity status
- JSON schema versions
- artifact freshness status
- trace replay index
- event stream cursor
- benchmark/public-claim status
- clear distinction between human-facing explanation and agent-facing control truth

## Innovative Features Relaytic Should Add

### 1. Belief Delta Lens

Show what changed Relaytic's belief:

- new data
- graph evidence
- threshold tuning
- calibration
- benchmark result
- incumbent comparison
- user intervention
- memory/research influence

This is more interesting than a typical dashboard because it makes reasoning inspectable.

### 2. What Would Change My Mind Panel

For every important claim, show:

- current claim
- confidence
- supporting evidence
- contradicting evidence
- cheapest next evidence that could overturn it

This fits Relaytic's identity better than generic "insights."

### 3. Review Budget Simulator

Let users move review capacity and see:

- expected positives caught
- false positives
- analyst-hours
- threshold
- case completeness
- claim safety

This is central for AML.

### 4. Public Claim Firewall

A dedicated screen that says:

- safe to say
- not safe to say
- why blocked
- what proof would unlock it

This is unusual and valuable.

### 5. Shadow Candidate Review

Show shadow-only models and tools as non-authoritative:

- would have won
- would have lost
- blocked by safety
- blocked by transfer
- blocked by cost
- candidate next step

This prepares the UI for Academy without starting Academy too early.

### 6. Agent Copilot Rail

A side rail for external agents:

- current artifact contract
- next command
- expected output
- allowed actions
- forbidden actions
- stale artifact warnings

This makes Relaytic useful inside Claude Code, ChatGPT, OpenClaw, and Codex workflows.

### 7. Case Evidence Map

For AML, show entity and transaction evidence as a focused case map, not a generic graph hairball.

The UI should show the suspicious neighborhood around one entity, with typology badges and path explanations.

### 8. Run Replay Filmstrip

A compact replay:

- intake
- investigation
- planning
- training
- challenger
- benchmark
- casework
- drift
- decision

Each frame links to the exact artifact and trace span.

## Proposed UI Slices

### UI-A. Mission Control Information Architecture Upgrade

- reorganize static HTML around current state, next action, result contract, AML board, proof status, and agent handoff
- remove long lists from first viewport
- add compact sections with explicit empty states

### UI-B. AML Investigation Board

- render alert queue, top case packet, typology evidence, drift posture, and benchmark claim guard from existing artifacts
- this can start static before becoming live

### UI-C. Agent Console

- add a dedicated JSON/HTML-lite view for external agents
- show canonical artifacts, commands, action affordances, MCP status, and blocked reasons

### UI-D. Local Live UI Server

- add `relaytic ui serve`
- subscribe to local event stream
- refresh run progress, background jobs, approvals, and trace state

### UI-E. Action And Approval Workflow

- browser actions for approve/deny/modify, safe takeover, bounded stage rerun, resume job, and benchmark run
- every action writes through existing permission/control artifacts

### UI-F. Review Budget Simulator

- interactive review-capacity slider backed by existing threshold/search/casework artifacts
- output remains artifact-backed

### UI-G. Trace And Belief Delta Explorer

- render branch decisions, competing claims, adjudication, and belief deltas
- connect trace spans to artifacts and user-visible decisions

### UI-H. Demo Mode

- public-safe view for the flagship AML demo
- hide internal construction scaffolding
- show proof bundle, business metrics, case packet, and blocked claims

## Recommended Build Order

1. UI-A after Slice 15R-A, because proof-pack state must be visible immediately.
2. UI-B during Slice 15S, because the flagship demo needs an AML board.
3. UI-H during Slice 15S or 15Y, because demo mode is the first public UI story.
4. UI-F during Slice 15T, because business-value metrics should be visual.
5. UI-C and UI-G before Academy, because agents need a clean operating surface.
6. UI-D and UI-E after the static information architecture is correct, because live interaction should not be built on a confused layout.

## Hard Product Rule

Do not build a prettier dashboard over weak proof.

The UI should make Relaytic more useful by exposing decisions, tradeoffs, evidence, and next actions. If a panel does not help a human or external agent decide what to do next, it should not be on the main screen.
