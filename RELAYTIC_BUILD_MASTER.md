# RELAYTIC_BUILD_MASTER.md

This is the build entrypoint for Codex.

## Read order

Codex should read these in order:

1. `RELAYTIC_VISION_MASTER.md`
2. `ARCHITECTURE_CONTRACT.md`
3. `IMPLEMENTATION_STATUS.md`
4. `MIGRATION_MAP.md`
5. `RELAYTIC_SLICING_PLAN.md`

`AGENTS.md` defines the standing repo rules and is assumed to have already been read before the slice-specific build docs.

## Core rule

Codex must **not** attempt the whole transformation in one pass.

Codex must:
- work one bounded slice at a time
- keep the repository coherent after every slice
- preserve the deterministic floor
- keep optional systems optional
- update tests and status docs after each slice
- keep external integrations optional
- avoid novelty theater
- keep a golden proof path alive while building
- keep artifacts stable and inspectable
- keep local artifacts as the canonical source of truth
- keep semantic and memory systems rowless by default unless policy grants richer access
- keep specialist capabilities explicit instead of relying on ambient full-repo/full-data access
- keep protocol surfaces semantically aligned and explicitly conformance-tested as the product grows
- keep flagship-demo and human-supervision proof tracks alive, not just technical internals

When mature external routines can strengthen a slice faster than in-core reinvention, prefer explicit optional adapters with self-checks and graceful fallback. Current high-leverage candidates are:

- MAPIE for conformal uncertainty
- Evidently for monitoring evidence
- MLflow registry/tracking export
- OpenTelemetry and OpenLineage for observability and lineage
- FLAML for reference benchmark parity
- Feast later for feature retrieval/serving alignment

## Frontier discipline

Relaytic should be treated as frontier work only when a slice strengthens at least one of these axes:

- search power
- evidence rigor
- autonomous judgment
- human and agent operability
- validated self-improvement

If a slice mainly adds surface area, prose, or orchestration without strengthening one of those axes, it is not sharp enough.

The remaining world-class proof tracks that later slices must make explicit are:

- protocol conformance across CLI, MCP, mission control, and any richer UI shell
- flagship demo scorecards that remain reproducible across releases
- human-supervision and onboarding-success evaluation for first-time users

## Current intended build order

Start with:
0. normalization and contract freeze
1. contracts and scaffolding
2. mandate and context foundation
3. focus council and investigation baseline
4. intake and translation layer
5. planning and first working route
5A. MVP access and operator surface
6. experimentation, challenger, audit, and reports
7. completion judgment and visible workflow state
8. lifecycle baseline
8A. interoperability and host adapters
8B. host activation and discovery
9A. run memory and analog retrieval
9B. local lab gateway, hook bus, and capability-scoped specialists
9. intelligence amplification and local-LLM setup assistance
9C. autonomous experimentation, executable lifecycle loops, and challenger portfolio expansion
9D. private research retrieval and method transfer
9E. communicative assist, guided navigation, and bounded takeover
9F. routed intelligence profiles, capability matrices, and semantic proof
10. feedback assimilation
10B. quality contracts, visible budgets, and operator/lab profiles
10C. behavioral contracts, skeptical steering, and causal memory
10A. decision lab, method compiler, and data-acquisition reasoning
11. benchmark parity and reference approaches
11A. imported incumbents and bring-your-own challenger baselines
11B. mission control MVP, onboarding, and one-command install
11C. mission-control clarity, capabilities, and guided stage navigation
11D. guided onboarding, live terminal mission-control chat, and capability explanations
11E. role-specific handbooks and handbook-aware onboarding
11F. demo-grade onboarding, mode education, and stuck recovery
11G. adaptive human onboarding and lightweight local semantic guidance
12. dojo mode and guarded self-improvement
12A. lab pulse, periodic awareness, and bounded proactive follow-up
12B. first-class tracing, agent evaluation, and runtime security harnesses
12C. differentiated result handoff and durable learnings
13. search controller, accelerated execution, and distributed local experimentation
14. real-world feasibility, domain constraints, and action boundaries
15. mission-control expansion, packaging, integrations, demos, and polish
16. representation engines, JEPA-style latent world models, and unlabeled local corpora

## Preferred post-MVP execution order

Stable numbering stays the same, but once Slice 07 is complete the preferred execution order is:

1. Slice 08
2. Slice 08A
3. Slice 08B
4. Slice 09A
5. Slice 09B
6. Slice 09
7. Slice 09C
8. Slice 09D
9. Slice 09E
10. Slice 09F
11. Slice 11
12. Slice 10
13. Slice 10B
14. Slice 10C
15. Slice 10A
16. Slice 11A
17. Slice 11B
18. Slice 11C
19. Slice 11D
20. Slice 11E
21. Slice 11F
22. Slice 11G
23. Slice 12
24. Slice 12A
25. Slice 12B
26. Slice 12C
27. Slice 12D
28. Slice 13
29. Slice 13A
30. Slice 13B
31. Slice 13C
32. Slice 14
33. Slice 14A
34. Slice 15
35. Slice 16

Reason:

- Slice 08 makes Relaytic lifecycle-capable
- Slice 08A makes Relaytic reachable from the most common local agent hosts while preserving one host-neutral tool contract
- Slice 08B makes host discovery and activation explicit instead of leaving platform reachability to guesswork
- Slice 09A is the highest-leverage intelligence upgrade because it turns artifact memory into reusable judgment
- Slice 09B gives Relaytic a true local lab runtime instead of loose process orchestration
- Slice 09 makes semantic and strategic amplification operational once capability-scoped context assembly exists
- Slice 09C turns judged recommendations into bounded autonomous second-pass execution and real challenger breadth
- Slice 09D lets Relaytic import method and benchmark knowledge through redacted external research while preserving the local-first security boundary
- Slice 09E makes Relaytic communicative and steerable for humans and agents without demoting the artifact graph into a chat shell
- Slice 09F makes the LLM layer explicit, routed, hardware-aware, and provable instead of merely available
- Slice 11 gives honest proof before feedback and dojo expansion
- Slice 10 lets Relaytic learn from what happened after predictions, not just from what happened inside one run
- Slice 10B makes quality gates, budget posture, and profile overlays explicit before decision-world modeling and broader search depend on them
- Slice 10C now lands the skeptical intervention layer, so Relaytic can expand decision authority next without becoming a compliant shell
- Slice 10A is now implemented and gives Relaytic an explicit decision lab, controller-policy layer, data-acquisition reasoning, and method compilation instead of leaving downstream action logic implicit
- Slice 11A makes Relaytic much easier to adopt and demo because it can take a real incumbent model from the operator and try to beat it honestly under the same contract
- Slice 11B is now implemented and gives Relaytic a real operator cockpit plus low-friction install/onboarding before dojo and later frontier slices expand the lab
- Slice 11C is now implemented and makes that cockpit legible on first contact by surfacing modes, capabilities, safe next actions, bounded stage reruns, and starter questions even before an operator discovers the assist surface manually
- Slice 11D is now implemented and makes first contact far less confusing by adding guided onboarding, a real terminal mission-control chat, explicit capability reasons, and a clearer dashboard-versus-chat split
- Slice 11E is now implemented and gives that onboarding surface explicit role-specific handbooks, handbook-aware chat/help affordances, and consistent agent host entry points instead of leaving orientation scattered across repo docs
- Slice 11F is now implemented and turns that onboarding surface into a better demo product by adding a guided walkthrough, explicit mode education, and stuck-recovery guidance directly inside mission control, terminal chat, and the handbook stack
- Slice 11G is now implemented and makes that first-contact flow much more human-tolerant by adding adaptive onboarding capture, visible onboarding session state, explicit analysis-first versus governed-run routing, lightweight local semantic rescue for messy input, and full-install local-helper provisioning
- Slice 12 is now implemented and gives Relaytic a guarded dojo layer with quarantined self-improvement proposals, benchmark/quality/control gates, promotion ledgers, rollback-ready state, architecture-proposal quarantine, and mission-control visibility
- Slice 12A should come after dojo because periodic awareness and bounded background follow-up are much safer once self-improvement already has quarantine and promotion rules
- Slice 12B should come before Slice 13 and the later Slice 15 mission-control expansion because Relaytic needs one canonical trace substrate, explicit competing-claim/adjudication contracts, and agent/security evaluation before wider search and full trace-explorer claims become credible
- Slice 12B should also establish protocol conformance between CLI, MCP, and later richer UI surfaces instead of assuming those surfaces stay aligned
- Slice 12C should come before Slice 13 because Relaytic needs differentiated post-run handoff, explicit next-run steering, and durable local learnings before deeper search and later demo packaging can feel complete to humans or external agents
- Slice 12D should come before Slice 13 because Relaytic should become workspace-first before it becomes search-deeper; the result contract, governed learnings, workspace lineage, and explicit next-run plan need to exist before wider search can decide responsibly between same-data continuation, add-data continuation, or starting over
- Slice 13 should prove not only deeper search but explicit value-of-search decisions, including when Relaytic refuses to keep searching and when the right answer is to add data or move to a new dataset instead of spending more search budget
- Slice 13A should come immediately after Slice 13 because Relaytic now has enough operator-facing surface that release hygiene, artifact attestation, and packaging discipline must become a product-enforced gate rather than a best-effort repo habit
- Slice 13B should come after Slice 13A because Relaytic needs one visible event bus and one explicit permission model before daemon work, remote approvals, or richer supervision can be trusted
- Slice 13C should come after Slice 13B because background work, resumable sessions, and memory-maintenance queues must consume the same event and authority model instead of inventing a second runtime
- Slice 14 should come after Slice 13C because real-world feasibility is stronger once Relaytic can account for permission posture, waiting approvals, and long-running work instead of treating constraints as static annotations
- Slice 14A should come after Slice 14 because remote supervision is only credible once local feasibility, permission modes, and background resumability are already explicit
- Slice 15 should close the proof loop with flagship demo packs, release readiness, remote supervision visibility, and human-supervision evaluation rather than treating UI polish as sufficient evidence
- Slice 16 is the optional late-stage representation-engine slice where Relaytic can evaluate JEPA-style latent predictive models for large unlabeled local corpora, event histories, and streams without promoting them into the authority path prematurely

Current repo state:

- implemented through Slice 13B, with Slice 09F routed-intelligence hardening, Slice 10 feedback assimilation, Slice 10B explicit quality/budget/profile contracts, Slice 10C skeptical behavioral control, Slice 10A decision-lab modeling, Slice 11A imported-incumbent challenge support, Slice 11B mission-control/onboarding/install surfaces, Slice 11C mission-control clarity surfaces, Slice 11D guided onboarding/chat surfaces, Slice 11E handbook-driven onboarding surfaces, Slice 11F demo-grade onboarding surfaces, Slice 11G adaptive human onboarding plus lightweight local semantic guidance, Slice 12 guarded dojo review, Slice 12A lab pulse, Slice 12B first-class tracing plus runtime evaluation, Slice 12C differentiated result handoff plus durable learnings, Slice 12D workspace continuity plus result-contract/iteration planning, Slice 13 search-controller depth plus execution-strategy selection, Slice 13A release safety plus build attestation, and Slice 13B event bus plus visible permission modes now landed
- next execution target: Slice 13C
- latest landed pulse slice: Slice 12A
- latest trace-and-safety slice: Slice 12B
- latest handoff-and-learnings slice: Slice 12D
- latest search-and-execution slice: Slice 13
- latest release-and-packaging slice: Slice 13A
- latest runtime-and-permission slice: Slice 13B
- next background-and-resume follow-on after Slice 13B: Slice 13C
- next workspace-and-iteration follow-on after Slice 13C: Slice 14
- next remote-supervision follow-on after Slice 14: Slice 14A
- after Slice 13, every later slice that changes operator-visible behavior, install/dependency posture, or long-running runtime behavior must extend the same mission-control, onboarding, dojo-visibility, pulse-visibility, trace/eval visibility, differentiated handoff, durable-learnings, workspace-continuity, result-contract, iteration-planning, search-controller, release-safety, permission-mode, and background-job surfaces rather than leaving the UI stale until late polish
- the canonical future product-contract pack for that work now lives under `docs/specs/` and should be treated as normative during later implementation, including [mission_control_contract.md](docs/specs/mission_control_contract.md), [handoff_result_migration.md](docs/specs/handoff_result_migration.md), [learnings_migration_contract.md](docs/specs/learnings_migration_contract.md), and [external_agent_continuation_contract.md](docs/specs/external_agent_continuation_contract.md) for already-shipped mission control, handoff, learnings, and external-agent continuation surfaces

## MVP boundary

The first working Relaytic should include only the load-bearing core:

- package scaffold
- deterministic floor
- policy loading
- artifact manifest
- mandate objects
- context objects
- intake and translation layer for human/agent inputs
- non-blocking intake clarification with explicit assumption logging and autonomous proceed behavior
- Focus Council baseline
- Scout / Scientist / Strategist / Builder baseline
- a thin MVP-access shell for humans and external agents
- Completion Judge baseline that consumes the full artifact graph, not just terminal metrics
- one working tabular route
- one challenger path
- one bounded ablation suite
- one provisional audit plus decision memo
- one stable agent-control path
- standardized artifacts
- CLI surface
- tests
- one golden demo path

Do **not** try to implement:
- every backend
- every benchmark family
- every route
- every UI screen
- dojo architecture search
- full local cluster orchestration
- every optional integration

before the MVP is undeniable.

## Current leverage points

If the goal is to turn the current implementation into something that looks genuinely novel rather than merely well-structured, the next leverage points are:

- a workspace-first continuity layer that promotes Relaytic from run-first tooling into a governed multi-run investigation workspace
- machine-stable result contracts that tell humans and external agents what Relaytic currently believes, how strong the evidence is, what remains unresolved, what it recommends next, and what would change its mind
- governed learnings that keep source, confidence, reaffirmation state, invalidation history, and optional expiry explicit instead of letting memory drift
- an iteration planner that can choose same-data continuation, add-data continuation, or new-dataset restart before deeper search spends time and compute
- a canonical product-spec pack that freezes schemas, flows, and proof burden so later coding work can optimize for quality instead of improvising product behavior
- a decision-world model that understands action cost, review/defer options, and whether more search is actually the right next move
- explicit quality and budget contracts that tell humans and external agents what Relaytic currently means by "good enough" and "worth the search"
- bounded operator/lab profiles that shape review posture and budget posture without personalizing truth-bearing logic
- behavioral contracts that let humans and external agents steer Relaytic without turning Relaytic into a compliant shell
- causal memory that preserves interventions, method outcomes, and downstream consequences rather than only analog similarity
- a method compiler that turns research, memory, and operator context into executable challenger and feature templates
- imported-incumbent challenge paths so Relaytic can beat real existing systems instead of only abstract baselines
- trace-native mission-control surfaces that turn the shipped specialist/tool/intervention/branch trace model into a polished replay, branch, and change-attribution experience
- broader runtime agent/security harnesses that expand the shipped control-injection, tool-misuse, branch-safety, and skeptical-override checks into a larger proof pack before broader autonomy becomes default
- outcome learning rather than run-only learning
- a richer long-term memory stack with retention, compaction, pinning, and replay rules so later specialists inherit durable lessons instead of analog hints alone
- richer data-fabric reasoning that can suggest joins, entity histories, or additional data before wasting search budget
- a stronger search controller that widens or prunes branches, changes handoff depth, and allocates HPO effort based on expected decision value under budget
- a mission-control surface that makes branch structure, confidence, intervention history, traces, incumbent-versus-Relaytic state, and change attribution legible to humans and agents
- an optional representation engine that can learn from large unlabeled local corpora and improve retrieval, anomaly support, and temporal state understanding without replacing deterministic adjudication

Slices 07, 09A, 09B, 09C, 09D, 09F, and 11 are the major groundwork novelty unlocks.
Slices 10, 10B, 10C, and 10A are the current category-shift unlocks that turned Relaytic from a governed inference lab into a more explicit decision-and-discovery system with skeptical steering. Slice 11A added real incumbent pressure, Slice 11B completed the first adoption unlock because humans and external agents can now launch, inspect, and demo the system from one coherent control surface, and Slice 11C made that surface legible enough to act as a real MVP cockpit instead of only a technical dashboard.
Slice 16 is a long-range optional frontier bet, not a prerequisite for the core lab thesis.

## Source of truth precedence

If files disagree, use:
1. `ARCHITECTURE_CONTRACT.md`
2. `RELAYTIC_SLICING_PLAN.md`
3. `IMPLEMENTATION_STATUS.md`
4. `MIGRATION_MAP.md`
5. `RELAYTIC_VISION_MASTER.md`

## Immediate instruction to Codex

Read the vision, then the build docs, then execute one bounded slice only.
For future slices, follow the slice-execution contract in `RELAYTIC_SLICING_PLAN.md`: load-bearing improvement, human surface, agent surface, intelligence source, proof obligation, and fallback rule.
