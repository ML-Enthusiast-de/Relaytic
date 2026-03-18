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
9. intelligence amplification and local-LLM setup assistance
9A. run memory and analog retrieval
10. feedback assimilation
11. benchmark parity and reference approaches
12. dojo mode and guarded self-improvement
13. accelerated/distributed local execution
14. physics-aware exploration constraints
15. packaging, integrations, demos, and polish

## Preferred post-MVP execution order

Stable numbering stays the same, but once Slice 07 is complete the preferred execution order is:

1. Slice 08
2. Slice 09A
3. Slice 09
4. Slice 11
5. Slice 10
6. Slice 12
7. Slice 13
8. Slice 14
9. Slice 15

Reason:

- Slice 08 makes Relaytic lifecycle-capable
- Slice 09A is the highest-leverage intelligence upgrade
- Slice 09 makes semantic and strategic amplification operational
- Slice 11 gives honest proof before feedback and dojo expansion

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
- benchmark-separated proof that Relaytic is stronger under mandate, reliability, and lifecycle constraints rather than only on raw score

Slices 07, 09A, and 11 should be treated as the main novelty unlocks, not just as supporting features.

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
