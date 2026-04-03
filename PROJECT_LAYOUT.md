# Relaytic Project Layout

This document describes the current repository structure and ownership boundaries. It is descriptive, not normative.

## Primary Docs

Public-facing docs:

1. `README.md`
2. `ARCHITECTURE.md`
3. `INTEROPERABILITY.md`
4. `RUNTIME.md`
5. `OPEN_SOURCE_STACK.md`
6. `SECURITY.md`

Implementation control docs:

1. `ARCHITECTURE_CONTRACT.md`
2. `IMPLEMENTATION_STATUS.md`
3. `MIGRATION_MAP.md`
4. `RELAYTIC_BUILD_MASTER.md`
5. `RELAYTIC_SLICING_PLAN.md`

## Repository Shape

```text
Relaytic/
  .agents/
    skills/
      relaytic/
  .claude/
    agents/
  .mcp.json
  configs/
    default.yaml
  data/
  artifacts/
  connectors/
    chatgpt/
  openclaw/
    skills/
  reports/
  models/
  docs/
    build_slices/
    handbooks/
  skills/
    relaytic/
  scripts/
  src/
    relaytic/
      artifacts/
      context/
      ingestion/
      intake/
      investigation/
      mandate/
      evidence/
      benchmark/
      compiler/
      completion/
      control/
      dojo/
      events/
      lifecycle/
      data_fabric/
      decision/
      permissions/
      feedback/
      handoff/
      intelligence/
      iteration/
      profiles/
      learnings/
      memory/
      autonomy/
      release_safety/
      research/
      assist/
      interoperability/
      integrations/
      modeling/
      planning/
      policies/
      pulse/
      search/
      tracing/
      evals/
      runs/
      runtime/
      mission_control/
      workspace/
    corr2surrogate/  # compatibility shim only
  tests/
  README.md
  ARCHITECTURE.md
  INTEROPERABILITY.md
  SECURITY.md
  AGENTS.md
  ARCHITECTURE_CONTRACT.md
  IMPLEMENTATION_STATUS.md
  MIGRATION_MAP.md
  RELAYTIC_VISION_MASTER.md
  RELAYTIC_BUILD_MASTER.md
  RELAYTIC_SLICING_PLAN.md
```

## Package Ownership

- `src/relaytic/` is the canonical product package
- `src/relaytic/mandate/` owns mandate foundation objects and writers
- `src/relaytic/context/` owns context foundation objects and writers
- `src/relaytic/ingestion/` owns snapshot-file loading and immutable data-copy staging
- `src/relaytic/ingestion/sources.py` owns local source inspection plus stream/lakehouse materialization into immutable run-local snapshots
- `src/relaytic/intake/` owns intake translation and interpretation artifacts
- `src/relaytic/investigation/` owns investigation specialists and focus artifacts
- `src/relaytic/planning/` owns Strategist planning, Builder handoff, and planning artifact storage
- `src/relaytic/modeling/feature_pipeline.py` owns split-safe categorical handling, missingness indicators, bounded interaction features, and reusable preprocessing state
- `src/relaytic/modeling/calibration.py` owns bounded calibration and uncertainty helpers for the current Builder route
- `src/relaytic/evidence/` owns challenger, ablation, audit, leaderboard, and decision-memo artifacts
- `src/relaytic/benchmark/` owns reference-approach comparison, parity-gap reporting, and benchmark artifact storage
- `src/relaytic/completion/` owns the completion-governor layer, run-state artifacts, and status synthesis
- `src/relaytic/lifecycle/` owns champion/candidate comparison, recalibration, retraining, promotion, and rollback artifacts
- `src/relaytic/intelligence/` owns semantic-task execution, backend discovery, routed intelligence profiles, capability-aware context assembly, document grounding, counterposition packs, verifier/proof artifacts, and semantic uncertainty artifacts
- `src/relaytic/memory/` owns analog retrieval, route priors, challenger priors, reflection memory, and memory artifact persistence
- `src/relaytic/autonomy/` owns bounded second-pass execution, challenger queues, branch outcomes, loop budgets, retrain/recalibration requests, and champion lineage
- `src/relaytic/research/` owns redacted external research retrieval, method-transfer distillation, benchmark-reference harvesting, and research-audit persistence
- `src/relaytic/compiler/` owns method compilation, executable challenger templates, compiled feature hypotheses, and compiled benchmark protocols
- `src/relaytic/feedback/` owns validated feedback, outcome learning, reversible effect reporting, and rollback-ready casebook artifacts
- `src/relaytic/handoff/` owns differentiated post-run handoff generation, next-run options, persisted next-run focus, and differentiated report rendering
- `src/relaytic/decision/` owns decision-world models, controller policies, intervention-policy reports, decision-usefulness synthesis, and value-of-more-data reasoning
- `src/relaytic/learnings/` owns durable local learnings state, learnings markdown, per-run learnings snapshots, and workspace learnings reset behavior
- `src/relaytic/data_fabric/` owns source-graph reasoning, join-candidate analysis, entity-history understanding, and acquisition planning
- `src/relaytic/dojo/` owns guarded self-improvement review, quarantined proposal bundles, validation results, promotion ledgers, rollback state, and architecture-proposal quarantine
- `src/relaytic/pulse/` owns periodic awareness scheduling, innovation-watch gathering, pulse recommendations, skip reporting, bounded pulse-run persistence, and memory-maintenance orchestration
- `src/relaytic/assist/` owns communicative assistance, stage navigation, bounded takeover, and connection-guide persistence
- `src/relaytic/interoperability/` owns MCP serving, host-bundle generation, and interoperability self-checks
- `src/relaytic/integrations/` owns optional-library discovery, compatibility self-checks, and adapter-scoped capability inventory
- `src/relaytic/runs/` owns MVP-access summaries, run reports, and top-level run presentation helpers
- `src/relaytic/runtime/` owns the local lab gateway, append-only event stream, hook audit, checkpoints, and capability-profile enforcement
- `src/relaytic/mission_control/` owns mission-control state, onboarding/install-health state, review-queue state, launch metadata, demo-session state, and control-center rendering
- `src/relaytic/artifacts/` owns manifest helpers
- `src/relaytic/policies/` owns policy loading and resolved-policy writing
- `src/corr2surrogate/` exists only to preserve a narrow temporary compatibility boundary

## Operational Directories

- `configs/` stores checked-in defaults
- `.agents/`, `.claude/`, `openclaw/`, and `connectors/` store checked-in agent-host wrapper surfaces and guidance
- `skills/` stores workspace-local skill mirrors for hosts that auto-discover from the current repository
- `data/private/` is reserved for local private inputs and must remain ignored
- `artifacts/`, `reports/`, and `models/` contain generated outputs and must remain ignored except for sentinel files
- `docs/build_slices/` tracks bounded implementation slices
- `docs/handbooks/` stores the role-specific onboarding guides for human operators and external agents
- `scripts/` stores local bootstrap and support scripts such as `install_relaytic.py`
- `tests/` provides regression coverage for both product and compatibility boundaries

## Current Package Boundaries

- `src/relaytic/research/` owns Slice 09D redacted external research retrieval, method-transfer distillation, benchmark-reference harvesting, and research-audit persistence
- `src/relaytic/assist/` owns Slice 09E communicative assistance, stage-navigation planning, takeover coordination, and connection-guide persistence
- `src/relaytic/benchmark/` owns Slice 11 reference comparison, parity-gap reporting, and benchmark artifact persistence
- `src/relaytic/benchmark/` also owns Slice 11A imported-incumbent evaluation, incumbent parity reporting, and beat-target contract persistence
- `src/relaytic/feedback/` owns Slice 10 validated feedback, outcome learning, reversible effect reporting, and rollback-ready casebook artifacts
- `src/relaytic/profiles/` owns Slice 10B quality contracts, budget contracts, operator/lab profile overlays, and budget-consumption reporting
- `src/relaytic/control/` owns Slice 10C intervention contracts, skeptical override handling, control-injection auditing, recovery checkpoints, and control-ledger persistence
- `src/relaytic/decision/` owns Slice 10A decision-world models, controller-policy writing, decision usefulness, and value-of-more-data reasoning
- `src/relaytic/compiler/` owns Slice 10A method compilation, executable challenger templates, compiled feature hypotheses, and compiled benchmark protocols
- `src/relaytic/data_fabric/` owns Slice 10A source-graph reasoning, join-candidate analysis, entity-history understanding, and acquisition planning
- `src/relaytic/mission_control/` owns Slice 11B mission-control MVP state, onboarding/install-health state, launch metadata, review-queue state, static control-center rendering, Slice 11C clarity artifacts for modes/capabilities/actions/navigation/questions, Slice 11D guided onboarding/live-chat behavior, Slice 11E handbook discovery/onboarding behavior, Slice 11F demo flow/mode education/stuck-recovery behavior, Slice 11G adaptive onboarding/session-capture/lightweight-local-semantic behavior, and the shared operator cockpit surface
- `src/relaytic/dojo/` owns Slice 12 guarded self-improvement controls, quarantined proposal bundles, validation results, promotion ledgers, rollback-ready state, and architecture-proposal quarantine
- `src/relaytic/pulse/` owns Slice 12A periodic awareness scheduling, innovation-watch gathering, pulse recommendations, skip reporting, bounded pulse-run persistence, memory-maintenance orchestration, and mission-control-visible pulse artifacts
- `src/relaytic/tracing/` owns Slice 12B canonical trace schemas, specialist/tool/intervention/branch trace persistence, claim-packet persistence, deterministic adjudication scorecards, replay reports, and replay/query surfaces
- `src/relaytic/evals/` owns Slice 12B agent-behavior evaluation, security harnesses, protocol-conformance checks, adversarial steering tests, runtime regression packs, scenario/result matrices, and later Slice 15 human-supervision/onboarding evaluation reports
- `src/relaytic/handoff/` owns Slice 12C differentiated post-run handoff generation, next-run options, persisted next-run focus, and differentiated report rendering for humans and external agents
- `src/relaytic/learnings/` owns Slice 12C durable local learnings state, learnings markdown, per-run learnings snapshots, workspace learnings reset behavior, and the learnings-to-memory handoff

Current workspace-first boundaries:

- `src/relaytic/workspace/` owns Slice 12D workspace state, multi-run lineage, focus history, workspace memory policy, and workspace-backed continuity views
- `src/relaytic/iteration/` owns Slice 12D next-run planning, focus-decision records, and data-expansion candidates
- `src/relaytic/search/` owns Slice 13 search-controller plans, portfolio search traces, HPO campaign reports, execution-backend selection, checkpoint posture, and explicit value-of-search artifacts
- `src/relaytic/release_safety/` owns Slice 13A release-bundle scanning, workspace-only pre-release scans, artifact attestation, source-map and sensitive-string audits, distribution-manifest capture, and packaging-regression reporting
- `src/relaytic/events/` owns Slice 13B typed runtime-event schemas, subscription registries, hook registries, and projection-only event-delivery contracts over the canonical runtime stream
- `src/relaytic/permissions/` owns Slice 13B visible permission modes, tool-permission matrices, approval-policy reporting, append-only permission-decision logs, and session capability contracts

Reserved future boundaries:

- `src/relaytic/daemon/` should own bounded background-job orchestration, resumable jobs, and memory-maintenance queues
- `src/relaytic/remote_control/` should own remote mission-control sessions, approval queues, supervision handoff, and remote-control audit
- `src/relaytic/representation/` should own optional representation engines, latent-state reports, embedding indexes, and JEPA-style pretraining support

Documentation boundaries:

- `docs/specs/` owns the canonical product-contract pack for workspace lifecycle, result-contract schema, governed learnings, mission-control behavior, compatibility migration, testing/proof burden, and flagship demos

## Naming Rule

All new public-facing work must use `Relaytic`, `relaytic`, and `relaytic`. Legacy names should appear only when documenting an explicit compatibility boundary.
