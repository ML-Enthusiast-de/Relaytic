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
10. feedback assimilation
11. benchmark parity and reference approaches
12. dojo mode and guarded self-improvement
13. accelerated/distributed local execution
14. physics-aware exploration constraints
15. packaging, integrations, demos, and polish

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
10. Slice 11
11. Slice 10
12. Slice 12
13. Slice 13
14. Slice 14
15. Slice 15

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
- Slice 11 gives honest proof before feedback and dojo expansion

Current repo state:

- implemented through Slice 09E
- next execution target: Slice 11

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

- a real completion governor that can diagnose why Relaytic should continue, stop, benchmark, or seek more evidence
- memory-guided route and challenger improvement rather than one-run-local reasoning only
- semantically grounded expert deliberation rather than shallow internal discussion
- bounded autonomous second-pass execution for challenger expansion, recalibration, retraining, and re-planning
- privacy-safe research retrieval that turns SOTA papers and benchmark references into explicit local transfer hypotheses rather than hidden internet prompt context
- benchmark-separated proof that Relaytic is stronger under mandate, reliability, and lifecycle constraints rather than only on raw score

Slices 07, 09A, 09B, 09C, and 11 should be treated as the main novelty unlocks, not just as supporting features.
Slices 08 and 09 are the main operability and bounded-intelligence unlocks that make those novelty slices more believable.

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
