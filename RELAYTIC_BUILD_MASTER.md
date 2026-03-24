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
10A. decision lab, method compiler, and data-acquisition reasoning
11. benchmark parity and reference approaches
12. dojo mode and guarded self-improvement
13. search controller, accelerated execution, and distributed local experimentation
14. real-world feasibility, domain constraints, and action boundaries
15. mission control, packaging, integrations, demos, and polish
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
13. Slice 10A
14. Slice 12
15. Slice 13
16. Slice 14
17. Slice 15
18. Slice 16

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
- Slice 10A is the category-shift slice where Relaytic begins modeling the downstream decision system, compiling methods into executable experiments, and reasoning about what additional data is worth pulling
- Slice 16 is the optional late-stage representation-engine slice where Relaytic can evaluate JEPA-style latent predictive models for large unlabeled local corpora, event histories, and streams without promoting them into the authority path prematurely

Current repo state:

- implemented through Slice 11, with Slice 09F routed-intelligence hardening and Slice 10 feedback assimilation now landed as well
- next execution target: Slice 10A
- next proof follow-on after Slice 10A: Slice 12

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

- a decision-world model that understands action cost, review/defer options, and whether more search is actually the right next move
- a method compiler that turns research, memory, and operator context into executable challenger and feature templates
- outcome learning rather than run-only learning
- richer data-fabric reasoning that can suggest joins, entity histories, or additional data before wasting search budget
- a stronger search controller that widens or prunes branches based on expected decision value under budget
- a mission-control surface that makes branch structure, confidence, and change attribution legible to humans and agents
- an optional representation engine that can learn from large unlabeled local corpora and improve retrieval, anomaly support, and temporal state understanding without replacing deterministic adjudication

Slices 07, 09A, 09B, 09C, 09D, 09F, and 11 are the major groundwork novelty unlocks.
Slices 10 and 10A are the next category-shift unlocks that can turn Relaytic from a governed inference lab into a genuine decision-and-discovery system.
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
