# RELAYTIC_SLICING_PLAN.md

This file turns the Relaytic vision into bounded implementation slices.

## Global slice rules

Every slice must:
- touch as few subsystems as practical
- add or update tests
- preserve the deterministic floor
- avoid unnecessary renames
- update `IMPLEMENTATION_STATUS.md`
- update `MIGRATION_MAP.md` if boundaries move
- keep optional dependencies optional
- prefer mature OSS libraries behind explicit adapters when they strengthen deterministic validation, baselines, diagnostics, feature breadth, or benchmark parity
- prefer high-leverage optional adapters for uncertainty, monitoring, lineage, registries, and benchmark baselines when they strengthen the proof track faster than in-core reimplementation
- strengthen at least one frontier axis once the repo has a working route
- keep human and agent control surfaces aligned
- map every new intelligence claim to artifacts plus tests or benchmark hooks
- state what becomes newly autonomous, newly challengeable, and newly inspectable after the slice lands
- define the deterministic fallback for every optional dependency, model, or external library it introduces
- leave at least one golden-path case and one adversarial case stronger than before
- for post-11 host-facing or operator-facing slices, strengthen at least one protocol-conformance, flagship-demo, or human-supervision proof case
- if it introduces a new autonomous loop, make the loop budgeted, replayable, and explicitly stoppable
- leave the repository coherent after completion

## Slice execution contract

From Slice 08 onward, every slice should be specified and implemented in the same shape:

- **load-bearing improvement**
  what Relaytic can do after the slice that it could not do before
- **human surface**
  what a human operator can now see, ask for, or control
- **agent surface**
  what another agent can now drive or consume non-interactively
- **intelligence source**
  whether the slice gets smarter through deterministic priors, retrieval, bounded semantic tasks, optional model help, external adapters, or some combination
- **proof obligation**
  what test, adversarial case, benchmark hook, or demo must pass so the slice is believable
- **fallback rule**
  what happens when the new intelligence path, integration, or optional runtime is missing

If a proposed slice cannot be written in that shape, it is not sharp enough yet.

## Intelligence source rules

Relaytic should become more intelligent through explicit, inspectable mechanisms only.

Allowed intelligence sources:

- stronger deterministic priors
- stronger evidence extraction from current-run artifacts
- optional mature-library adapters behind stable contracts
- bounded local semantic tasks
- memory and analog retrieval
- optional policy-gated frontier amplification
- benchmark-validated dojo improvements

Disallowed intelligence claims:

- vague "the agent knows"
- hidden prompt magic without artifacts
- silent behavior changes from optional dependencies
- benchmark claims without separation between deterministic, local-LLM, frontier, and dojo modes

## Runtime and security translation rules

Relaytic should borrow strong runtime ideas from modern agent systems only where they improve structured-data work without weakening data security or local control.

Required translation rules:

- artifacts on local disk remain the canonical source of truth; any memory index, semantic cache, or retrieval structure is derived and disposable
- major run and inference flows must operate on immutable staged copies inside the run directory rather than the original source file
- semantic helpers and optional LLM paths are rowless by default; they should receive schema summaries, bounded evidence bundles, redacted notes, and sampled diagnostics unless policy explicitly grants richer access
- every specialist should have an explicit capability profile covering read scope, write scope, network allowance, and semantic-tool allowance
- side-effecting specialist work should be scoped to the current run directory unless the operator explicitly enables a broader boundary
- engine slots remain one-active-backend-per-slot so Relaytic stays adaptable without turning into plugin chaos
- hook points must be deterministic, local-first, and inspectable; read-only is the default and write-capable hooks require explicit policy
- append-only event traces should become the coordination spine for long runs, memory flushes, retries, and later UI/MCP synchronization
- no slice may introduce a remote-first memory, embedding, or orchestration dependency as the default path
- remote streaming, warehouse, lakehouse, and datalake connectors may arrive later only as explicit adapter tracks; the current public MVP supports local snapshot files plus bounded local stream/lakehouse materialization

## High-leverage external routines to consider

These are not mandatory core dependencies. They are pre-approved optional adapter candidates because they can accelerate frontier-grade capability without diluting Relaytic's judgment core.

- **MAPIE**
  use for conformal uncertainty, calibrated prediction intervals/sets, and abstention-aware lifecycle decisions
  strongest fit: Slice 08 and Slice 11
- **Evidently**
  use for drift, data-quality, and monitoring-oriented evidence views
  strongest fit: Slice 08 and later lifecycle/reporting work
- **MLflow registry/tracking**
  use for optional export of model versions, aliases, promotion ledgers, and artifact lineage
  strongest fit: Slice 08 and Slice 15
- **OpenTelemetry**
  use for traces, metrics, and structured observability around agent and run execution
  strongest fit: Slice 08 and Slice 15
- **OpenLineage**
  use for dataset/job/run lineage beyond Relaytic's internal artifact graph
  strongest fit: Slice 08 and Slice 15
- **FLAML**
  use as a strong reference AutoML baseline in benchmark and parity work
  strongest fit: Slice 11
- **Feast**
  use later for point-in-time feature retrieval and feature-serving alignment
  strongest fit: late lifecycle/serving work after Slice 08 and Slice 15
- **JEPA-family representation engines**
  use later for latent predictive representation learning over large unlabeled local tables, event histories, and streams
  strongest fit: late-stage research work after Slice 15, especially a future Slice 16 representation-engine track

Adapter rule:

- every external routine must stay behind an explicit Relaytic adapter
- every adapter must expose self-checks, version capture, and graceful fallback
- no optional library may become a hidden source of truth for mandate, policy, or final judgment
- no optional library should enter the guaranteed baseline unless the deterministic floor remains intact without it

## Frontier proof track

The slices are not only a feature order. They are also a proof order.

From Slice 05 onward, Relaytic should keep these cross-cutting proof tracks alive:

- **golden autonomous path**
  one stable dataset -> intent -> judged model run that proves the main loop still works
- **challenger path**
  one case where the first answer can be overturned or materially weakened by challenger pressure
- **agent-control path**
  one non-interactive JSON-first flow that another agent could drive end to end
- **governor path**
  one case where Relaytic explicitly decides whether to stop, continue, benchmark, or seek more evidence and the reason is inspectable
- **memory path**
  once Slice 09A lands, one case where analog retrieval materially changes route choice, challenger design, or completion reasoning with visible provenance
- **runtime path**
  once Slice 09B lands, one case where CLI and MCP agree because they consume the same evented run state with visible capability enforcement
- **closed-loop path**
  once Slice 09C lands, one case where Relaytic actually executes a second-pass challenger, recalibration, retrain, or replan action and either improves the result or stops honestly
- **research path**
  one case where a redacted run signature retrieves external methods or benchmark references, changes planning/evidence/autonomy design, and records explicit no-raw-row audit
- **benchmark path**
  formal benchmark parity is Slice 11, but benchmark harness stubs and reference logging should start earlier whenever route, evidence, or completion logic changes

If a later slice adds "smartness" without strengthening at least one of those proof tracks, it is not sharp enough.

- **outcome-learning path**
  once Slice 10 lands, one case where validated intervention or post-deployment outcome evidence changes a later policy or route recommendation with visible rollback support
- **control-contract path**
  once Slice 10C lands, one case where a human or external agent asks Relaytic to change course, Relaytic challenges the request, accepts/modifies/rejects it explicitly, and writes a replayable override decision instead of silently complying
- **causal-memory path**
  once Slice 10C lands, one case where intervention history, outcome history, or prior method outcomes materially change Relaytic's skepticism, next-step judgment, or takeover behavior beyond analog similarity alone
- **decision-lab path**
  once Slice 10A lands, one case where Relaytic chooses between more search, more data, recalibration, retraining, abstention, or operator review because it modeled the downstream decision environment explicitly
- **method-compiler path**
  once Slice 10A lands, one case where research, memory, or operator notes compile into an executable challenger, feature, split, or benchmark template rather than only a report
- **incumbent-challenge path**
  once Slice 11A lands, one case where a user or external agent imports an existing model, prediction set, scorecard, or ruleset as the incumbent and Relaytic honestly reports whether it can beat it under the same local split and metric contract
- **control-center path**
  once Slice 11C lands, one case where a new user can install Relaytic, launch one local control center, inspect run status, quality/budget posture, decision state, incumbent parity, current modes, capabilities, safe assist/control actions, and bounded stage reruns from one coherent surface instead of stitching together multiple commands
- **handbook path**
  once Slice 11E lands, one case where a new human or external agent can open mission control, discover the correct role-specific handbook immediately, and get pointed to the right next command without reading the repo tree
- **demo-onboarding path**
  once Slice 11F lands, one case where a new person who knows nothing about Relaytic can discover what it is, how to start, what the modes mean, what to do when stuck, and what the shortest useful demo flow is without repo literacy or hand-holding
- **adaptive-onboarding path**
  once Slice 11G lands, one case where a human pastes a dataset path or a messy data-plus-goal message into mission-control chat, Relaytic captures what matters, asks the next clarifying question naturally, and only creates the first run after deterministic confirmation
- **pulse path**
  once Slice 12A lands, one case where Relaytic wakes on a bounded schedule, notices something worth attention, writes explicit recommendations or watchlists, and either safely skips or queues one bounded follow-up without silently mutating core behavior
- **trace path**
  once Slice 12B lands, one case where a human or external agent can replay one run across specialist turns, tool calls, interventions, branch decisions, competing claim packets, and deterministic adjudication from one trace model instead of stitching multiple logs together
- **agent-security path**
  once Slice 12B lands, one case where Relaytic deliberately withstands or rejects a control-injection, tool-misuse, or unsafe branch-expansion request and records the defense or failure mode in an explicit evaluation artifact
- **protocol-conformance path**
  once Slice 12B lands, one case where CLI and MCP expose the same trace, adjudication winner, and defensive-control outcome from the same canonical run truth, and any mismatch becomes an explicit eval failure rather than silent drift
- **handoff-and-learnings path**
  once Slice 12C lands, one case where a completed run yields differentiated human and agent result reports, explicit next-run options, durable learnings that survive across runs, and a deliberate learnings reset that does not silently repopulate on the same refresh
- **workspace-continuity path**
  once Slice 12D lands, one workspace should carry at least two runs with visible lineage, one shared machine-stable result contract per run, governed learnings that can be invalidated or expired without deleting history, and an explicit next-run plan that chooses between same-data continuation, add-data continuation, or starting over
- **mission-control path**
  once Slice 15 lands, one case where a human or external agent can see branch structure, confidence, and change attribution without reading the entire artifact tree
- **flagship-demo path**
  once Slice 15 lands, at least three packaged demos with explicit scorecards should stay green:
  - unfamiliar dataset to useful governed decision
  - imported incumbent challenge under the same contract
  - skeptical override rejection or unsafe-request defense with replayable trace
- **human-supervision path**
  once Slice 15 lands, one first-time human and one external agent path should be able to complete onboarding, start useful work, inspect why Relaytic changed course, and recover when stuck without repo literacy

## Preferred post-MVP execution order

Stable slice numbering stays the same, but the preferred execution order after Slice 07 is:

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

Why:

- Slice 08 makes Relaytic operational over time instead of one-run-only
- Slice 08A makes Relaytic reachable from the most common agent hosts without collapsing into a vendor-specific shell
- Slice 08B makes host discovery and activation explicit, which is necessary for honest mass usage
- Slice 09A is the highest-leverage intelligence upgrade because it makes later agents smarter across runs and turns artifact memory into a first-class system
- Slice 09B gives Relaytic a local lab runtime with evented coordination, hook discipline, and capability-scoped specialists instead of relying on loose process glue
- Slice 09 improves bounded semantic and strategic lift without redefining the core, and becomes safer once runtime and capability profiles exist
- Slice 09C turns judged recommendations into bounded autonomous second-pass action so Relaytic can execute challenger expansion, recalibration, retraining, and re-planning rather than only recommending them
- Slice 09D lets Relaytic absorb external SOTA knowledge through redacted research queries, method-transfer artifacts, and benchmark-reference harvesting without exporting user data
- Slice 09E gives Relaytic a communicative control surface so humans and external agents can ask for explanations, jump back to any bounded stage, or let Relaytic take over safely
- Slice 09F makes the LLM layer explicit, routed, hardware-aware, and provable instead of leaving semantic help as an ambient feature
- Slice 11 gives honest proof before feedback or dojo behavior expands too far
- Slice 10 becomes safer after memory and benchmark doctrine exist
- Slice 10B makes quality gates, budget posture, and operating-profile assumptions explicit before deeper decision-world modeling and broader search begin leaning on them
- Slice 10C should now come before Slice 10A because Relaytic needs skeptical steering, intervention contracts, causal memory, and control-injection defenses before it expands decision authority again
- Slice 10A is the category-shift slice that turns Relaytic from a governed model/evaluation engine into a decision-and-discovery engine with compiled methods and data-acquisition reasoning
- Slice 11A turns Relaytic's benchmark and challenger story into something much more real for operators and recruiters by letting users attach an incumbent model and forcing Relaytic to beat it honestly
- Slice 11B is now implemented and gives Relaytic a real operator-facing control center plus a low-friction install/onboarding path before dojo and later frontier slices expand the lab
- Slice 11C is now implemented and makes that control center legible on first contact by surfacing modes, capabilities, safe next actions, bounded stage reruns, and starter questions even before a user has discovered the assist surface manually
- Slice 11D is now implemented and makes first contact far less confusing by adding guided onboarding, real terminal mission-control chat, explicit capability reasons, and a clearer dashboard-versus-chat split
- Slice 11E is now implemented and makes that onboarding surface explicit for both humans and external agents by surfacing role-specific handbooks directly from mission control, chat, and checked-in host notes
- Slice 11F is now implemented and makes the experience much more demo-ready by surfacing a guided walkthrough, explicit mode explanations, and stuck-recovery guidance directly from mission control, chat, and the handbook stack
- Slice 11G is now implemented and makes that first-contact UX much more forgiving by adding adaptive onboarding capture, visible chat session state, explicit analysis-first versus governed-run routing, lightweight local semantic rescue for messy human input, and full-install helper provisioning
- Slice 12A should come after dojo because periodic awareness, innovation watching, and bounded background follow-up are much safer once self-improvement stays quarantined and promotion rules already exist
- Slice 12B should come before Slice 13 and the later Slice 15 mission-control expansion because wider search and full trace-backed mission control both need one canonical trace substrate plus explicit agent/security evaluation before they are believable
- Slice 12B should also establish protocol conformance between CLI, MCP, and later richer UI surfaces instead of assuming those surfaces stay aligned
- Slice 12C should come before Slice 13 because Relaytic still needs a professional post-run handoff, explicit next-run steering, and durable learnings that survive across runs before deeper search and late demo packaging can feel complete
- Slice 12D should come before Slice 13 because Relaytic should become workspace-first before it becomes search-deeper; the result contract, governed learnings, workspace lineage, and explicit next-run plan need to exist before wider search can responsibly choose between same-data continuation, add-data continuation, or starting over
- Slice 13 should prove not only deeper search but explicit value-of-search decisions so the controller can justify widening, stopping, adding data, or moving to a new dataset
- Slice 13A should come immediately after Slice 13 because Relaytic now has enough operator-facing surface that release hygiene, artifact attestation, and packaging discipline must become a product-enforced gate instead of a best-effort repo habit
- Slice 13B should come after Slice 13A because Relaytic needs one visible event bus and one explicit permission model before daemon work, remote approvals, or richer supervision can be trusted
- Slice 13C should come after Slice 13B because background work, resumable sessions, and memory-maintenance queues must consume the same event and authority model instead of inventing a second runtime
- Slice 14 should come after Slice 13C because real-world feasibility is stronger once Relaytic can account for permission posture, waiting approvals, and long-running work instead of treating constraints as static annotations
- Slice 14A should come after Slice 14 because remote supervision is only credible once local feasibility, permission modes, and background resumability are already explicit
- Slice 15 should close the loop with flagship demo packs, release readiness, remote supervision visibility, and human-supervision evaluation rather than treating UI polish as sufficient proof
- Slice 16 is the optional late-stage representation-engine slice where Relaytic can evaluate JEPA-style latent predictive models for large unlabeled local corpora, event histories, and streams without promoting them into the authority path prematurely

## Current execution state

- implemented baseline: Slice 00 through Slice 13, including Slice 09F routed intelligence, Slice 10 feedback assimilation/outcome learning, Slice 10B explicit quality-budget-profile contracts, Slice 10C skeptical behavioral control contracts, Slice 10A decision-lab world modeling, data-fabric reasoning, method compilation, Slice 11A imported-incumbent beat-target support, Slice 11B mission-control/onboarding/install surfaces, Slice 11C mission-control clarity surfaces, Slice 11D guided onboarding/chat surfaces, Slice 11E handbook-guided onboarding surfaces, Slice 11F demo-grade onboarding surfaces, Slice 11G adaptive human onboarding plus lightweight local semantic guidance, Slice 12 guarded dojo review, Slice 12A lab pulse, Slice 12B first-class tracing plus runtime evaluation, Slice 12C differentiated result handoff plus durable learnings, Slice 12D workspace-first continuity plus result contracts and explicit iteration planning, and Slice 13 search-controller depth plus execution-strategy selection
- next execution target: Slice 13A
- latest pulse slice: Slice 12A
- latest trace-and-safety follow-on: Slice 12B
- latest handoff-and-learnings follow-on: Slice 12D
- latest search-and-execution follow-on: Slice 13
- next release-and-packaging follow-on after Slice 13: Slice 13A
- next runtime-and-permission follow-on after Slice 13A: Slice 13B
- next background-and-resume follow-on after Slice 13B: Slice 13C
- next workspace-and-iteration follow-on after Slice 13C: Slice 14
- next remote-supervision follow-on after Slice 14: Slice 14A
- later mission-control expansion after Slice 14A: Slice 15
- late optional representation follow-on after Slice 15: Slice 16
- after Slice 13, every later slice that changes operator-visible behavior, major artifact families, install/dependency posture, or long-running runtime behavior must extend the same mission-control, onboarding, dojo-visibility, differentiated-handoff, durable-learnings, workspace-continuity, result-contract, iteration-planning, search-controller, release-safety, permission-mode, and background-job surfaces instead of treating UI as a separate late-polish track
- the canonical product-spec pack for Slice 12D and its follow-ons now lives under `docs/specs/` and should be treated as normative for future implementation, including [mission_control_contract.md](docs/specs/mission_control_contract.md), [handoff_result_migration.md](docs/specs/handoff_result_migration.md), [learnings_migration_contract.md](docs/specs/learnings_migration_contract.md), and [external_agent_continuation_contract.md](docs/specs/external_agent_continuation_contract.md) for already-shipped mission control, handoff, learnings, and external-agent continuation surfaces

## Slice 00 - Normalization and contract freeze

Goal:
- freeze public naming on Relaytic
- add missing build-control docs
- add the public `relaytic` package and CLI surface
- establish security and env-handling rules
- track the temporary legacy compatibility boundary explicitly

Required outputs:
- `ARCHITECTURE_CONTRACT.md`
- `IMPLEMENTATION_STATUS.md`
- `MIGRATION_MAP.md`
- `docs/build_slices/phase_00.md`
- `AGENTS.md`
- Relaytic-branded README and package metadata
- temporary `corr2surrogate` compatibility shim

## Slice 01 - Contracts and scaffolding

Goal:
- create package scaffold
- establish pyproject-based install
- add minimal CLI shell
- add artifact manifest helper
- add policy/config loading shell

Required outputs:
- installable package shell
- `relaytic --help`
- manifest helper
- policy loader stub

## Slice 02 - Mandate and context foundation

Goal:
- stable mandate objects
- stable context objects
- resolved config writing

Required outputs:
- `policy_resolved.yaml`
- `lab_mandate.json`
- `work_preferences.json`
- `run_brief.json`
- `data_origin.json`
- `domain_brief.json`
- `task_brief.json`

## Slice 03 - Focus Council and investigation baseline

Goal:
- Scout baseline
- Scientist baseline
- Focus Council baseline
- deterministic expert-prior substrate for common structured-data archetypes
- dataset profile
- domain memo
- objective artifacts

Required outputs:
- `dataset_profile.json`
- `domain_memo.json`
- `objective_hypotheses.json`
- `focus_debate.json`
- `focus_profile.json`
- `optimization_profile.json`
- `feature_strategy_profile.json`

## Slice 04 - Intake and translation layer

Goal:
- raw user and external-agent intake
- deterministic translation of free-form notes into mandate/context/run fields
- explicit task-type and domain-archetype hint extraction from free-form intake
- schema alignment between typed language and dataset columns
- optional local-LLM semantic help with bounded provenance
- optional clarification generation for later refinement, never as the default blocking path
- explicit autonomy mode and proceed-with-assumptions behavior when answers are absent
- normalized updates into the Slice 02 foundation

Required outputs:
- `intake_record.json`
- `autonomy_mode.json`
- `clarification_queue.json`
- `assumption_log.json`
- `context_interpretation.json`
- `context_constraints.json`
- `semantic_mapping.json`

## Slice 05 - Planning and first working route

Goal:
- Strategist baseline
- explicit Strategist -> Builder handoff
- one working deterministic tabular route
- metric selection
- split selection
- feature-strategy integration
- experiment-priority integration
- same-run planning plus model artifact execution

Required outputs:
- `plan.json`
- `alternatives.json`
- `hypotheses.json`
- `experiment_priority_report.json`
- `marginal_value_of_next_experiment.json`

Expected behavior:
- `relaytic plan create` must write a concrete Builder handoff, not just abstract route notes
- `relaytic plan run` must execute the first deterministic route in the same run directory
- planning must distinguish hard feature guardrails from soft heuristic risk signals so autonomous runs do not collapse when investigation heuristics are overly conservative

## Slice 05A - MVP access and operator surface

Goal:
- one obvious end-to-end entrypoint
- human-friendly summary surface
- stable agent-friendly summary artifact
- simple prediction surface for built runs
- preserve the specialist architecture underneath

Required outputs:
- `run_summary.json`
- `reports/summary.md`

Required behavior:
- `relaytic run` must orchestrate intake, investigation, planning, and the first execution route
- `relaytic show` must summarize a run even if the summary artifacts were not originally created
- `relaytic predict` must make inference discoverable without forcing users into the lower-level command surface
- the MVP shell must remain a thin access layer over the real Relaytic pipeline, not a replacement for it

## Slice 06 - Experimentation, challenger, audit, reports

Goal:
- treat the selected Builder route as a challengeable champion, not a silent winner
- add one real challenger branch
- add one bounded ablation suite
- add one provisional audit pass
- expose the outcome as clear human and agent surfaces
- keep the MVP one-command usable while preserving explicit specialist control

Required outputs:
- `experiment_registry.json`
- `challenger_report.json`
- `leaderboard.csv`
- `ablation_report.json`
- `audit_report.json`
- `belief_update.json`
- `reports/summary.md`
- `reports/technical_report.md`
- `reports/decision_memo.md`

Required behavior:
- `relaytic evidence run` must be able to attach Slice 06 evidence to an existing executed run or autonomously ensure the executed route exists first
- `relaytic run` must include Slice 06 evidence pressure by default so the MVP does not stop at the first built model
- the evidence layer must remain deterministic by default and only use local-LLM advisory help for bounded memo refinement
- the output must make the provisional recommendation visible to both humans and external agents

## Slice 07 - Completion judgment and visible workflow state

Goal:
- Completion Judge as Inference Governor
- stage tracking
- explicit blocking-layer diagnosis
- mandate-vs-evidence adjudication
- machine-actionable next-action queue
- clear done/continue outputs

Required outputs:
- `completion_decision.json`
- `run_state.json`
- `stage_timeline.json`
- `mandate_evidence_review.json`
- `blocking_analysis.json`
- `next_action_queue.json`

Required behavior:
- completion must consume mandate, context, intake, investigation, planning, and evidence artifacts together rather than only final metrics
- completion outputs must be machine-actionable, not narrative only
- the current stage and next recommended action must be visible in both human and agent surfaces
- completion should turn ambiguity into explicit confidence and blocking reasons rather than hidden state
- completion must explicitly diagnose whether the current bottleneck is route breadth, evidence insufficiency, unresolved semantic ambiguity, missing benchmark comparison, missing memory support, or operator/policy constraint
- completion must be able to say "continue experimentation because the challenger space is still too narrow" rather than treating every executed run as equally complete
- completion must standardize its primary action vocabulary rather than inventing per-run phrasing
- completion must expose whether mandate and evidence agree, conflict, or remain unresolved
- completion must leave an explicit handoff into Slice 09A or Slice 11 when the real limitation is missing memory support or missing benchmark context
- completion must remain deterministic by default, with optional local-LLM help limited to bounded explanation refinement

## Slice 08 - Lifecycle baseline

Goal:
- monitor vs recalibrate vs retrain baseline
- champion/candidate comparison
- promotion/rollback baseline
- explicit lifecycle state transitions instead of one-shot run conclusions
- evidence-backed distinction between performance drift, calibration drift, route failure, and candidate superiority

Required outputs:
- `retrain_decision.json`
- `promotion_decision.json`
- `rollback_decision.json`
- `champion_vs_candidate.json`

Required behavior:
- lifecycle decisions must be evidence-backed, reversible, and easy for an external agent to consume
- Relaytic must distinguish "keep current champion", "recalibrate", "retrain", "promote challenger", and "roll back" as separate actions, not one blended outcome
- lifecycle must use current evidence, completion state, and fresh-data behavior together rather than watching only one scalar metric
- lifecycle must tell the difference between "model still good", "calibration is stale", "data shifted but route may still hold", and "route choice is no longer strong enough"
- lifecycle must leave a clean handoff into monitoring and later feedback/memory slices rather than burying state inside one report
- optional uncertainty and monitoring adapters should be considered here first, especially MAPIE for conformal decision support and Evidently for richer drift/data-quality evidence
- optional registry and observability exports should be considered here second, especially MLflow for promotion ledgers and OpenTelemetry/OpenLineage for run observability and lineage

First implementation moves:

1. Add `src/relaytic/lifecycle/` models, storage, and decision agents.
2. Build champion/candidate loaders over existing run, evidence, and completion artifacts.
3. Implement a deterministic lifecycle governor with explicit action thresholds and reason codes.
4. Add optional adapter slots for conformal uncertainty, richer monitoring evidence, registry export, and observability export.
5. Add a minimal human/agent CLI surface for lifecycle review.
6. Add fresh-data and stale-data tests that force recalibrate, retrain, promote, and rollback branches.

Minimum proof:

- one case where recalibration is preferred over retraining
- one case where challenger promotion is preferred over keeping the champion
- one case where rollback is recommended because the current route is no longer trustworthy
- one non-interactive agent-driven lifecycle review flow

## Slice 08A - Interoperability and host adapters

Goal:
- host-neutral MCP server
- safe local-first stdio and streamable HTTP transports
- checked-in Claude, Codex/OpenAI, and OpenClaw host wrappers
- ChatGPT connector export guidance
- compatibility self-checks and compact transport-safe health tools

Required outputs:
- checked-in `.mcp.json`
- checked-in `.claude/agents/relaytic.md`
- checked-in `.agents/skills/relaytic/SKILL.md`
- checked-in `openclaw/skills/relaytic/SKILL.md`
- checked-in `connectors/chatgpt/README.md`
- exportable `relaytic_host_bundle_manifest.json`

Required behavior:
- Relaytic must expose a host-neutral MCP tool surface rather than separate ad hoc wrappers per platform
- stdio must remain the local-default transport for developer tools and project-scoped hosts
- streamable HTTP must be available for connector-style deployment surfaces
- interoperability must stay local-first and safe by default: local bind host only, no checked-in secrets, no machine-specific paths, no remote exposure by accident
- external hosts must be able to access at least the current MVP run/show/status/predict/lifecycle surfaces through the same stable MCP contract
- the checked-in host bundles must remain drift-checked against generated templates
- interoperability self-checks must validate both static bundle correctness and at least one live stdio MCP handshake/tool call
- Relaytic must provide one compact transport-safe server-health tool so hosts can verify availability without pulling large artifacts

First implementation moves:

1. Add `src/relaytic/interoperability/` for MCP serving, host-bundle generation, and compatibility self-checks.
2. Freeze one canonical Relaytic MCP tool contract over the current MVP and phase-level surfaces.
3. Add local stdio and streamable HTTP transports with safe local defaults.
4. Add checked-in Claude, Codex/OpenAI, OpenClaw, and ChatGPT-facing wrapper/guidance files.
5. Add live stdio and streamable HTTP tests plus one public-dataset end-to-end Relaytic run through the interoperability layer.

Minimum proof:

- one live stdio MCP handshake and tool call
- one live streamable HTTP handshake and tool call
- one public-dataset end-to-end Relaytic run through the MCP surface
- one host-bundle export flow with no machine-specific paths or secrets

Innovation hook:

- Relaytic should become reachable from major human and agent surfaces without flattening into one vendor, one shell, or one opaque remote service

## Slice 08B - Host activation and discovery

Goal:
- explicit host discovery state
- workspace-level auto-discovery where the host supports it
- clear machine-readable activation requirements
- honest distinction between repo-local reachability and remote connector registration

Required outputs:
- checked-in `skills/relaytic/SKILL.md`
- expanded machine-readable host readiness in `relaytic interoperability show`
- updated ChatGPT connector guidance with explicit non-auto-discovery language

Required behavior:
- Claude readiness must be shown as repo-local/project-local discovery plus one approval step
- Codex/OpenAI readiness must be shown as repo-local skill discovery
- OpenClaw readiness must be shown as workspace-local `skills/` discovery
- ChatGPT readiness must be shown as connector-registration-only, requiring a public HTTPS `/mcp` endpoint
- Relaytic should no longer imply that all hosts can discover it directly from the same files

First implementation moves:

1. Add activation/discovery fields to host-bundle metadata.
2. Add a checked-in workspace-level `skills/relaytic/SKILL.md` mirror for OpenClaw.
3. Expose `discoverable_now`, `requires_activation`, `requires_public_https`, and `next_step` in `relaytic interoperability show`.
4. Update docs so users and external agents can see the host truth immediately.

Minimum proof:

- interoperability inventory shows correct readiness states for Claude, Codex/OpenAI, OpenClaw, and ChatGPT
- exported host bundles include the workspace-level OpenClaw skill path
- ChatGPT remains explicitly non-auto-discoverable from repo files alone

## Slice 09 - Intelligence amplification, doc grounding, and structured semantic tasks

Execution note:
- preferred after Slice 09A and Slice 09B even though the stable numbering stays at 09

Goal:
- intelligence modes
- local-LLM discovery
- setup guidance
- health checks
- structured semantic task primitive
- bounded doc grounding
- capability-aware context assembly
- semantic debate, counterposition, and verifier packets
- contradiction detection and semantic uncertainty reporting
- semantically stronger challenger and retraining rationale
- health-driven intelligence escalation

Required outputs:
- `intelligence_mode.json`
- `llm_backend_discovery.json`
- `llm_health_check.json`
- `llm_upgrade_suggestions.json`
- `semantic_task_request.json`
- `semantic_task_results.json`
- `intelligence_escalation.json`
- `context_assembly_report.json`
- `doc_grounding_report.json`
- `semantic_access_audit.json`
- `semantic_debate_report.json`
- `semantic_counterposition_pack.json`
- `semantic_uncertainty_report.json`

Required behavior:
- intelligence amplification must improve bounded semantic and strategic tasks without collapsing the deterministic floor
- stronger local models or doc-grounded semantic flows must amplify the expert-prior substrate rather than replace it
- Relaytic must always be able to state which judgments came from deterministic evidence and which were LLM-amplified
- the semantic task primitive must stay schema-bound, policy-bound, and artifact-backed
- semantic tasks must be JSON-only at the contract level, even when the backing model is more general
- context assembly for semantic work must be capability-aware and rowless by default
- document grounding must cite bounded local artifacts or explicitly supplied documents rather than inventing ambient expertise
- any semantic path that receives richer-than-summary access must leave an explicit access audit trail
- local/backend discovery and setup guidance must make the intelligence surface operable for humans and external agents, not just configurable in code
- optional frontier backends must plug into the same bounded semantic-task contract rather than opening an uncontrolled side channel
- semantically amplified internal discussions must produce explicit extracted facts, competing hypotheses, counterarguments, verifier findings, and uncertainty notes instead of vague advisory prose
- when ambiguity is material, Relaytic should be able to generate at least one counterposition and one verifier pass before it changes task framing, challenger direction, or retraining rationale
- semantic amplification should be able to improve challenger design, completion reasoning, and retrain-vs-recalibrate reasoning without ever becoming a silent source of truth

First implementation moves:

1. Freeze one canonical semantic-task request/response schema and JSON validation layer.
2. Implement backend discovery and health checks over the existing local-LLM setup path.
3. Add a capability-aware context assembler that can produce rowless summaries, bounded evidence packets, and explicitly granted richer views.
4. Route intake, investigation, planning, evidence, completion, and lifecycle advisory calls through the structured semantic-task primitive.
5. Add a bounded proposer/counterposition/verifier microflow for semantically difficult judgments.
6. Add bounded local document-grounding support over explicitly supplied notes, specs, or policies.
7. Add backend health and escalation artifacts that explain why Relaytic stayed deterministic or escalated.

Minimum proof:

- one case where semantic amplification materially improves schema or context interpretation
- one case where the same task degrades gracefully to deterministic behavior with no model available
- one case where the system explicitly records that a judgment was LLM-amplified and what evidence constrained it
- one case where doc grounding improves a judgment without exposing raw rows
- one case where a capability policy blocks over-broad context assembly and Relaytic still completes the task safely
- one case where semantic counterposition changes challenger design, retraining rationale, or target understanding in a visible and auditable way

Innovation hook:

- Relaytic should not become "call an LLM everywhere"
- it should become better at bounded semantic labor and semantically grounded expert deliberation while staying inspectable, local-first, challengeable, and data-minimized by default

## Slice 09A - Run memory and analog retrieval

Goal:
- run memory retrieval
- analog-case search
- route-prior recovery
- challenger-prior suggestions
- cross-run intelligence that improves future judgment without overriding current evidence

Required outputs:
- `memory_retrieval.json`
- `analog_run_candidates.json`
- `route_prior_context.json`
- `challenger_prior_suggestions.json`
- `reflection_memory.json`
- `memory_flush_report.json`

Required behavior:
- memory must be advisory, provenance-carrying, and challengeable by current-run evidence
- memory must treat on-disk Relaytic artifacts as canonical and any retrieval index as derived
- retrieved analogs must influence planning, challenger design, and completion reasoning without silently overriding the current dataset
- memory failures or low-confidence retrieval must degrade gracefully into deterministic no-memory behavior
- memory must be able to explain *why* an analog was retrieved: task family, schema pattern, risk shape, evidence pattern, route history, or lifecycle similarity
- memory influence must be visible as a counterfactual whenever practical: what Relaytic would have done without memory vs with memory
- memory retrieval should operate on summaries, priors, and artifact-derived signals rather than raw training rows whenever practical
- no remote embedding or hosted retrieval service should be part of the default memory path
- before completion/lifecycle finalization, Relaytic should be able to flush durable reflection memory and retrieval deltas back to disk

First implementation moves:

1. Add `src/relaytic/memory/` with run indexing, retrieval, reflection writeback, and prior-suggestion helpers.
2. Build a derived local index over run summaries, evidence artifacts, completion artifacts, lifecycle outcomes, and reflection notes.
3. Inject retrieved priors into planning, challenger design, and completion review behind explicit advisory boundaries.
4. Add a pre-close memory flush that writes durable reflections before the run is considered complete for the current mode.
5. Add tests where analog retrieval changes route choice or challenger choice and where weak retrieval is ignored.
6. Add one cross-run demo fixture that proves memory changes behavior with visible provenance.

Minimum proof:

- one case where memory materially changes the selected route or challenger design
- one case where the retrieved analog is overruled by current-run evidence
- one case where low-confidence retrieval cleanly falls back to no-memory behavior
- one case where reflection memory is flushed to disk before completion/lifecycle finalization

Innovation hook:

- this is the first slice where Relaytic should become meaningfully smarter across runs instead of only within a run

## Slice 09B - Local lab gateway, hook bus, and capability-scoped specialists

Goal:
- local lab gateway
- append-only run event stream
- deterministic hook bus
- capability-scoped specialists
- pre-close state flush and checkpointing
- one control plane for CLI, MCP, UI, and automation

Required outputs:
- `lab_event_stream.jsonl`
- `hook_execution_log.json`
- `run_checkpoint_manifest.json`
- `capability_profiles.json`
- `data_access_audit.json`
- `context_influence_report.json`

Required behavior:
- Relaytic must gain a local-first runtime control plane that owns run state transitions, event emission, and hook dispatch instead of scattering that logic across ad hoc entrypoints
- the event stream must be append-only, machine-readable, and rich enough to reconstruct stage transitions, retries, fallbacks, approvals, and major branch decisions
- hooks must default to read-only, local-only, and run-dir-scoped; any broader write scope must be explicit and auditable
- every specialist must declare a capability profile covering artifact read scope, artifact write scope, raw-row access, semantic access, and external-adapter access
- semantic helpers and optional LLM-backed specialists must consume rowless summaries by default unless policy explicitly grants richer context
- the gateway must be able to flush reflection memory and checkpoint state before compaction, retry, or final completion/lifecycle transitions
- the runtime layer must strengthen, not replace, the existing CLI and MCP contracts

First implementation moves:

1. Add `src/relaytic/runtime/` for event emission, checkpointing, hook dispatch, and capability-profile resolution.
2. Freeze the event schema for run-stage transitions, fallback events, hook calls, and capability overrides.
3. Add capability profiles for Scout, Scientist, Strategist, Builder, Challenger, Completion, Lifecycle, and semantic helpers.
4. Route `relaytic run` and the MCP server through the same runtime event path.
5. Add one deterministic read-only hook surface and one policy-gated write hook surface.
6. Add tests for capability enforcement, rowless semantic defaults, and pre-close flush behavior.

Minimum proof:

- one run where CLI and MCP views agree because they read the same evented run state
- one case where a specialist is denied over-broad access by its capability profile and Relaytic still proceeds safely
- one case where a read-only hook observes a state transition without changing outcome
- one case where checkpoint and flush behavior preserves reflection/memory state across retry or completion boundaries

Innovation hook:

- Relaytic should stop looking like a pipeline with agent labels and start behaving like a secure local inference lab runtime with explicit specialist capabilities and evented coordination

## Slice 09C - Autonomous experimentation, executable lifecycle loops, and challenger portfolio expansion

Goal:
- bounded autonomous second-pass execution
- executable recalibration, retraining, and re-planning loops
- multi-branch challenger portfolio instead of one narrow challenger
- explicit champion lineage and branch promotion history
- budgeted loop control with plateau-aware stopping

Required outputs:
- `autonomy_loop_state.json`
- `autonomy_round_report.json`
- `challenger_queue.json`
- `branch_outcome_matrix.json`
- `retrain_run_request.json`
- `recalibration_run_request.json`
- `champion_lineage.json`
- `loop_budget_report.json`

Required behavior:
- completion and lifecycle decisions with clear next steps must be able to trigger bounded follow-up execution rather than stopping at a report
- Relaytic must support at least one second-pass action chosen from challenger expansion, recalibration pass, retrain pass, or re-plan-with-counterposition
- challenger science must grow from one bounded challenger into a small portfolio when route narrowness or challenger pressure is detected
- every autonomous round must record why the branch was chosen, what budget it consumed, what changed, and whether the result improved the current champion
- champion status must become lineage-aware so promotions, holds, and rollbacks are visible as explicit branch history rather than implied by the latest artifact set
- bounded loops must stop on budget limit, repeated non-improvement, mandate/policy conflict, or confidence plateau rather than drifting into open-ended search
- deterministic fallback must remain available: when auto-execution is disabled, Relaytic still emits the same loop requests and branch recommendations as inspectable artifacts

First implementation moves:

1. Add `src/relaytic/autonomy/` for loop-state persistence, branch selection, round budgeting, and lineage updates.
2. Freeze a loop action taxonomy for `expand_challenger_portfolio`, `run_recalibration_pass`, `run_retrain_pass`, `replan_with_counterposition`, `hold_current_champion`, and `stop_after_plateau`.
3. Upgrade completion and lifecycle layers so they can emit executable branch requests instead of advisory next steps only.
4. Expand the evidence layer from one challenger branch to a small bounded challenger queue when route narrowness or challenger pressure is present.
5. Add champion-lineage tracking so every promotion, hold, retrain, recalibration, and rollback becomes part of one inspectable branch history.
6. Add tests and demos where Relaytic runs a second pass automatically and either improves the result or stops honestly.

Minimum proof:

- one case where `continue_experimentation` triggers a real second-pass branch automatically
- one case where recalibration is executed and judged better than a full retrain
- one case where retraining is executed and the old champion is either retained or replaced with explicit lineage
- one case where a challenger portfolio overturns the first apparent winner
- one case where the loop stops because of budget exhaustion or non-improvement plateau

Innovation hook:

- this is the slice where Relaytic stops being a judged single-pass system and becomes a bounded autonomous inference lab that can actually carry its own next step out

## Slice 09D - Private research retrieval, method transfer, and benchmark-aware domain intelligence

Status:
- implemented in the current baseline
- shipped package boundary: `src/relaytic/research/`
- shipped public commands: `relaytic research gather`, `relaytic research show`, and `relaytic research sources`
- shipped artifacts: `research_query_plan.json`, `research_source_inventory.json`, `research_brief.json`, `method_transfer_report.json`, `benchmark_reference_report.json`, and `external_research_audit.json`

Goal:
- privacy-safe external research retrieval
- rowless redacted query planning
- source-tiered paper and benchmark harvesting
- method-transfer suggestions for planning, challenger science, and evaluation
- benchmark-reference capture without raw data leakage

Required outputs:
- `research_query_plan.json`
- `research_source_inventory.json`
- `research_brief.json`
- `method_transfer_report.json`
- `benchmark_reference_report.json`
- `external_research_audit.json`

Required behavior:
- external research must be policy-gated and optional
- default research queries must be built from abstracted run signatures such as task family, domain archetype, class imbalance, metric regime, time structure, deployment constraints, and risk flags
- no raw rows, private identifiers, proprietary system names, machine paths, or full sensitive schema details may be sent to external research sources unless policy explicitly permits it
- retrieved sources must be labeled by type and trust tier such as paper, benchmark, library docs, reference repo, or operator-supplied reference
- research findings must become explicit hypotheses, challenger ideas, evaluation ideas, or benchmark references, never hidden authority inside prompt context
- Relaytic must be able to reject, down-rank, or ignore retrieved advice when local evidence contradicts it
- research retrieval must degrade cleanly to the current no-network behavior when disabled or unavailable

First implementation moves:

1. Add a redacted query planner that derives safe external research queries from current artifacts.
2. Add bounded source adapters for papers, benchmark references, and method summaries.
3. Distill results into local method-transfer and benchmark-reference artifacts rather than free-form notes.
4. Wire research outputs into planning, evidence, autonomy, and later Slice 11 benchmark design.
5. Add privacy, contradiction, and no-network fallback tests.

Minimum proof:

- one case where retrieved research changes challenger or evaluation design with visible provenance
- one case where Relaytic records a no-leak research audit for an external query
- one case where a retrieved suggestion is rejected because local evidence is stronger
- one case where the entire feature degrades cleanly when networked research is disabled

Innovation hook:

- this is the slice where Relaytic starts acting like a private automated research lab that can import world knowledge without exporting user knowledge

## Slice 09E - Communicative assist, guided navigation, and bounded takeover

Status:
- implemented in the current baseline
- shipped package boundary: `src/relaytic/assist/`
- shipped public commands: `relaytic assist show`, `relaytic assist turn`, and `relaytic assist chat`
- shipped artifacts: `assist_mode.json`, `assist_session_state.json`, `assistant_connection_guide.json`, and `assist_turn_log.jsonl`

Goal:
- communicative explanation for humans and agents
- jump-back navigation to any bounded stage
- bounded takeover when the user or agent stops or is unsure
- optional local semantic lift without making an LLM mandatory
- integrated guidance for local lightweight LLMs and local host connections

Required behavior:
- assist must explain current state from the artifact graph rather than inventing hidden state
- humans and external agents must share the same turn contract
- stage navigation must rerun the requested stage and refresh downstream artifacts so the run stays coherent
- takeover must remain bounded and policy-aware rather than open-ended
- assist must work deterministically even when no local LLM is configured
- connection guidance must remain honest about what is local, what is optional, and what requires host-specific activation

Minimum proof:

- one case where Relaytic explains current state and next action through the assist surface
- one case where Relaytic jumps back to a bounded stage and refreshes downstream artifacts coherently
- one case where a user or agent says “take over” and Relaytic executes the next safe step
- one case where assist exposes local LLM and host-connection guidance without requiring either path

## Slice 09F - Routed intelligence profiles, capability matrices, and semantic proof

Status:
- implemented in the current baseline
- shipped package boundary: `src/relaytic/intelligence/`
- shipped artifacts: `llm_routing_plan.json`, `local_llm_profile.json`, `verifier_report.json`, and `semantic_proof_report.json`

Goal:
- first-class intelligence routing
- hardware-aware local baseline profile selection
- explicit backend capability matrices
- semantic proof instead of hand-wavy “agent intelligence”
- visible user and agent guidance for why Relaytic chose one semantic path

Required behavior:
- Relaytic must route semantic work through explicit canonical modes: `none`, `local_min`, `assist`, `amplify`, and `max_reasoning`
- routing must remain policy-bound, local-first by default, and compatible with the deterministic floor
- legacy or implementation-specific mode labels may exist internally, but Relaytic must always be able to explain the canonical requested, recommended, and selected mode
- Relaytic must resolve one local baseline profile explicitly when local semantic help is configured or recommended
- backend discovery must expose a capability matrix for JSON mode, context window, endpoint scope, and other bounded semantic-task-relevant capabilities
- verifier output must be written as its own artifact rather than remaining embedded only inside a broader debate packet
- semantic amplification must emit an explicit proof artifact showing whether it changed any bounded semantic outputs relative to the deterministic semantic baseline
- humans and external agents must be able to inspect routed mode, recommended mode, selected local profile, and semantic gain through the same CLI/MCP contract

First implementation moves:

1. Add canonical mode utilities and routing helpers under `src/relaytic/intelligence/`.
2. Add local baseline profile resolution over the existing runtime-policy profile stack.
3. Add explicit routing, verifier, and semantic-proof artifacts to the intelligence bundle and manifest.
4. Upgrade `relaytic intelligence show`, `relaytic show`, and the assist/runtime surfaces so routed semantic posture is visible.
5. Add targeted tests for legacy-mode normalization, profile routing, verifier deltas, and semantic-proof reporting.

Minimum proof:

- one case where a legacy configured mode is normalized into the canonical routing contract
- one case where a minimum local profile is resolved explicitly and surfaced to the user
- one case where the verifier artifact records a change relative to the deterministic semantic baseline
- one case where semantic amplification leaves a measurable proof artifact instead of an implicit “LLM used” flag
- one case where the run summary and intelligence surface expose the same routed mode and selected profile

Innovation hook:

- this is the slice where Relaytic stops saying “LLMs are optional” as philosophy only and starts proving exactly how bounded semantic intelligence is routed, constrained, and measured

## Slice 10 - Feedback assimilation, outcome learning, and reversible policy shaping

Goal:
- feedback intake
- validation
- outcome learning
- policy/prior update suggestions
- reversible feedback memory

Load-bearing improvement:

- Relaytic should stop learning only from run-internal artifacts and begin learning from what humans, operators, and downstream outcomes say actually happened after the run

Human surface:

- operators should be able to record whether Relaytic's target, route, threshold, abstention posture, lifecycle judgment, or report usefulness was right in practice

Agent surface:

- external agents should be able to submit feedback and outcome packets non-interactively, inspect whether Relaytic trusted them, and see what future-default suggestions changed

Intelligence source:

- validated human feedback, validated external-agent feedback, benchmark review, runtime failure evidence, and post-decision outcome observations

Fallback rule:

- if no validated feedback or outcome evidence exists, Relaytic should continue using current run memory, benchmark doctrine, and deterministic priors without hidden behavior drift

Required outputs:
- `feedback_intake.json`
- `feedback_validation.json`
- `feedback_effect_report.json`
- `feedback_casebook.json`
- `outcome_observation_report.json`
- `decision_policy_update_suggestions.json`
- `policy_update_suggestions.json`
- `route_prior_updates.json`

Required behavior:
- validated feedback may change future defaults, but no accepted feedback may silently rewrite behavior without an inspectable effect report
- adversarial or low-quality feedback should degrade trust, not quietly pollute priors
- feedback updates must remain distinct from run-memory retrieval so Relaytic can tell whether a prior came from historical evidence, accepted feedback, or both
- accepted feedback must remain reversible, attributable, and benchmark-aware
- no feedback-derived change should become a default promotion path without surviving the benchmark doctrine from Slice 11
- feedback must not silently change autonomous loop policy, challenger breadth, or retrain triggers without an explicit effect report and rollback path
- feedback must distinguish route-quality feedback, decision-policy feedback, data-quality feedback, and post-deployment outcome evidence instead of collapsing them into one bucket
- accepted feedback may suggest changes to thresholds, abstention/defer posture, review policy, and data-acquisition priorities, but those suggestions must remain explicit and attributable
- post-decision outcomes should be able to contradict an apparently strong offline route and force a later policy or route update suggestion

First implementation moves:

1. Add feedback intake, validation, and trust-scoring primitives.
2. Add explicit outcome-observation records for intervention results, operator overrides, abstention outcomes, and later labels.
3. Separate accepted feedback memory from passive run memory and from observed outcome memory.
4. Generate route-prior, policy-update, and decision-policy suggestions rather than mutating live behavior directly.
5. Add adversarial feedback tests, misleading outcome tests, and rollback tests.
6. Gate feedback promotions behind explicit effect reports.

Minimum proof:

- one accepted feedback case that improves a later decision path
- one rejected or downgraded feedback case that avoids polluting priors
- one rollback of a feedback-derived prior update
- one case where downstream outcome evidence changes a later policy or route recommendation

Innovation hook:

- Relaytic should learn from what happened after the prediction, not just from what the system believed during the run

## Slice 10B - Quality contracts, visible budgets, and operator/lab profiles

Goal:
- explicit good-enough contracts
- explicit budget contracts
- visible budget consumption
- bounded operator and lab profiles

Load-bearing improvement:

- Relaytic should stop relying on scattered hidden defaults for "good enough" and "how far to search" and instead write one inspectable quality/budget contract that humans and external agents can see before, during, and after the run.

Human surface:

- humans should be able to inspect and, when policy allows, override accepted quality gates, benchmark appetite, review posture, search/autonomy/runtime budget, and profile overlays from one coherent surface instead of inferring them from multiple artifacts

Agent surface:

- external agents should be able to consume one machine-readable quality contract, one machine-readable budget contract, and one bounded operator/lab profile surface rather than reverse-engineering Relaytic defaults from scattered summaries

Intelligence source:

- task type, domain archetype, current policy defaults, resolved hardware profile, benchmark posture, feedback casebook, mandate, work preferences, and current runtime/autonomy evidence

Fallback rule:

- if no explicit quality or budget inputs are provided, Relaytic must derive default contracts from task type, local hardware assumptions, and policy defaults, write them explicitly, and continue autonomously instead of keeping those defaults implicit

Required outputs:
- `quality_contract.json`
- `quality_gate_report.json`
- `budget_contract.json`
- `budget_consumption_report.json`
- `operator_profile.json`
- `lab_operating_profile.json`

Required behavior:
- Relaytic must materialize one explicit "good enough" contract covering task-appropriate metric gates, benchmark expectations, calibration/review posture, and current stop/continue semantics
- Relaytic must materialize one explicit budget contract covering runtime, autonomy loops, branch count, search posture, and hardware/execution assumptions
- the UI, CLI summaries, assist layer, and MCP surfaces must expose both contracts and current consumption state consistently
- operator and lab profiles may shape review strictness, benchmark appetite, explanation style, and budget posture, but they must not silently override deterministic metrics, model outcomes, or artifact truth
- if no operator/lab profile is provided, Relaytic must still run by deriving defaults from `lab_mandate.json`, `work_preferences.json`, task evidence, and local hardware assumptions
- completion, lifecycle, autonomy, benchmark, and later search-control logic must consume these contracts instead of inventing private defaults phase by phase
- budget reporting must distinguish configured limits from consumed resources and from merely assumed limits

First implementation moves:

1. Add explicit contract builders for quality gates and budgets over the current policy/task/hardware defaults.
2. Add one bounded operator-profile and one lab-operating-profile layer that can safely overlay review posture, benchmark appetite, and budget posture without touching deterministic truth.
3. Surface quality/budget contracts through `relaytic show`, `relaytic runtime show`, `relaytic autonomy show`, `relaytic assist show`, and MCP summaries.
4. Add run-scope override support so humans and agents can define quality/budget inputs without editing the repo-wide defaults.
5. Make completion, lifecycle, autonomy, and benchmark surfaces explain decisions in terms of the explicit contracts they consumed.
6. Prepare Slice 10C, Slice 10A, and Slice 13 to read these contracts instead of scattering their own hidden assumptions.

Minimum proof:

- one no-input run where Relaytic writes task-derived quality and budget contracts explicitly before major execution
- one case where a bounded operator or lab profile changes review posture or budget posture without changing deterministic artifact truth
- one surface where configured budget, consumed budget, and remaining budget are visible together
- one case where Relaytic explains continue/recalibrate/retrain/stop in terms of the explicit quality gate report rather than only prose
- one case where an external agent can read the same quality/budget/profile contract through JSON or MCP without scraping markdown

Innovation hook:

- this is the slice that turns Relaytic from "smart but partly implicit" into a serious lab instrument with visible standards, visible limits, and visible operating posture

Profile discipline:

- prefer lab-scoped and operator-scoped profiles over hidden per-user personalization
- profile overlays may tune explanation depth, benchmark appetite, review strictness, abstain/review preference, and budget posture
- profile overlays must not silently force model-family choices, falsify metrics, or bypass the deterministic floor

## Slice 10C - Behavioral contracts, skeptical steering, and causal memory

Status:
- implemented

Goal:
- intervention contracts
- skeptical human/agent steering
- control-injection defense
- recovery checkpoints
- causal, intervention, outcome, and method memory

Load-bearing improvement:

- Relaytic should stop treating human or external-agent steering as either blind authority or free-form chat. It should treat every material steering action as an intervention request that can be challenged, accepted, modified, deferred, rejected, checkpointed, and remembered causally.

Human surface:

- humans should be able to step in at any bounded point, ask Relaytic to revisit or override something, and see a clear accept/modify/reject explanation plus the recovery checkpoint and downstream consequences

Agent surface:

- external agents should be able to submit machine-readable intervention requests, inspect challenge/override outcomes, read intervention memory, and query why Relaytic did or did not comply without scraping prose

Intelligence source:

- explicit instruction hierarchy, policy and mandate rules, runtime capability profiles, validated feedback, outcome evidence, causal memory, bounded semantic critique, and deterministic recovery logic

Fallback rule:

- if causal memory or richer semantic critique is unavailable, Relaytic should still challenge interventions with deterministic instruction hierarchy, policy, and artifact evidence rather than silently trusting the request

Required outputs:
- `intervention_request.json`
- `intervention_contract.json`
- `control_challenge_report.json`
- `override_decision.json`
- `intervention_ledger.json`
- `recovery_checkpoint.json`
- `control_injection_audit.json`
- `causal_memory_index.json`
- `intervention_memory_log.json`
- `outcome_memory_graph.json`
- `method_memory_index.json`

Required behavior:
- every truth-bearing human or external-agent request must be classified as navigation, clarification, proposal, override, or policy-bypass attempt before Relaytic acts on it
- navigation and explanation requests should remain easy; truth-bearing override requests must trigger challenge-before-comply behavior
- Relaytic must use a stable authority hierarchy for intervention handling rather than treating all user, agent, tool, and web instructions as equal
- Relaytic must be able to accept, accept-with-modification, defer pending evidence, or reject an intervention request explicitly
- any accepted override that can materially change later artifacts must checkpoint recoverable pre-override state first
- Relaytic must remember which interventions later proved helpful, harmful, or neutral and use that memory to improve skepticism and next-step judgment
- assist, research, interoperability, and autonomy surfaces must audit control-injection attempts instead of only trusting current-turn intent classification
- causal memory must preserve objective links between assumptions, interventions, actions, outcomes, and corrections rather than relying only on similarity retrieval

First implementation moves:

1. Add a control-contract layer that normalizes human and external-agent interventions into typed requests.
2. Add deterministic instruction-hierarchy and policy checks before modeling-changing requests are accepted.
3. Add recovery checkpoints and override decisions so Relaytic can safely roll back accepted steering.
4. Extend memory with causal, intervention, outcome, and method indexes that link what happened to what worked.
5. Add adversarial tests for policy-bypass language, tool/output injection, and over-trusting external-agent requests.
6. Wire control decisions into assist, runtime, feedback, memory, and interoperability surfaces.

Minimum proof:

- one case where a user asks Relaytic to rerun or go back and Relaytic accepts safely with an explicit checkpoint
- one case where a user or external agent asks Relaytic to skip a required safeguard and Relaytic rejects it with a challenge report
- one case where a prior harmful override increases skepticism on a later similar request through causal memory
- one case where a trusted but under-specified request is accepted only with modification or explicit uncertainty

Innovation hook:

- this is the slice that turns Relaytic from a steerable lab into a skeptical collaborator that can be directed without becoming compliant theater

## Slice 10A - Decision lab, method compiler, and data-acquisition reasoning

Status:
- implemented

Goal:
- decision-system world modeling
- method compilation
- data-fabric reasoning
- value-of-more-data and value-of-more-search judgment

Load-bearing improvement:

- Relaytic should stop behaving like a system that only asks "which model wins?" and start behaving like a system that can ask "which action policy, which additional data, which controller choice, and which next experiment most improves the real downstream decision?"

Human surface:

- humans should be able to inspect the assumed decision regime, action costs, defer/review options, data-acquisition suggestions, and compiled method-transfer ideas behind Relaytic's next-step judgment

Agent surface:

- external agents should be able to consume a machine-readable decision world model, controller policy, handoff-controller report, compiled challenger templates, compiled feature/data hypotheses, and value-of-more-data reasoning without parsing prose

Intelligence source:

- current artifacts, benchmark results, validated feedback, run memory, privacy-safe research retrieval, runtime evidence, and bounded semantic synthesis

Fallback rule:

- if action economics, nearby sources, or method references are missing, Relaytic should emit a provisional world model with explicit uncertainty and fall back to current benchmark/memory/planning behavior rather than inventing hidden certainty

Required outputs:
- `decision_world_model.json`
- `controller_policy.json`
- `handoff_controller_report.json`
- `intervention_policy_report.json`
- `decision_usefulness_report.json`
- `value_of_more_data_report.json`
- `data_acquisition_plan.json`
- `source_graph.json`
- `join_candidate_report.json`
- `method_compiler_report.json`
- `compiled_challenger_templates.json`
- `compiled_feature_hypotheses.json`
- `compiled_benchmark_protocol.json`

Required behavior:
- Slice 10A must consume the explicit quality and budget contracts from Slice 10B rather than inventing new hidden defaults for search or stopping behavior
- Slice 10A must also consume intervention contracts, override decisions, and causal memory from Slice 10C so downstream decision-world modeling reflects how the lab is actually being steered
- Slice 10A must make dynamic controller logic explicit: who should act next, how much branch depth is justified, when to ask for review, and when to keep work local to one specialist must be written as artifacts rather than inferred from code flow
- Relaytic must model downstream action, false-positive and false-negative cost, review/defer options, delay, and operator-load constraints when enough evidence exists
- when decision economics are under-specified, Relaytic must emit a provisional world model and explicit uncertainty rather than pretending raw score is the only objective
- research, memory, and operator notes must be able to compile into executable challenger templates, feature hypotheses, split/evaluation changes, or benchmark-protocol updates instead of stopping at summaries
- Relaytic must be able to say when more data is more valuable than more search and what local data would reduce uncertainty most
- multi-source reasoning must stay local-first and copy-only; any additional data pull must still materialize into bounded immutable run-local snapshots
- compiled methods must remain proposals until planning, autonomy, evidence, and benchmark paths test them against local evidence

First implementation moves:

1. Add a decision-world-model layer that fuses mandate, completion, lifecycle, benchmark, feedback, runtime, and outcome evidence.
2. Add a method compiler that turns research, memory, and operator context into challenger, feature, split, and benchmark templates.
3. Add a source-graph and join-candidate layer over local snapshots, staged copies, and permitted source contracts.
4. Add value-of-more-data and value-of-more-search reasoning that completion and autonomy can consume directly.
5. Add a controller-policy layer that can change handoff depth, reviewer involvement, and branch pressure under explicit reasoning.
6. Wire compiled outputs into planning, autonomy, lifecycle, assist, and benchmark surfaces.

Minimum proof:

- one case where modeled action economics changes threshold, abstention, review, or next-step judgment
- one case where compiled research or memory changes challenger or feature design through an explicit executable template
- one case where Relaytic recommends additional local data or a join candidate instead of wider search on the current snapshot
- one case where Relaytic records uncertainty because the downstream decision environment is under-specified
- one case where Relaytic changes branch depth, reviewer involvement, or the next acting specialist because the controller logic said it mattered

Innovation hook:

- this is the slice where Relaytic becomes a decision-and-discovery engine rather than only a governed model-and-evaluation engine

## Slice 11 - Benchmark parity and reference approaches

Status:
- implemented in the current baseline

Goal:
- benchmark doctrine
- reference-approach comparison
- honest parity reporting
- no-hardcoding discipline

Required outputs:
- `benchmark_gap_report.json`
- `reference_approach_matrix.json`
- `benchmark_parity_report.json`

Required behavior:
- benchmark results must separate deterministic-floor Relaytic, local-LLM-amplified Relaytic, bounded-loop Relaytic, and dojo-improved Relaytic
- benchmark suites must include both ordinary structured-data cases and operator-constrained or mandate-heavy cases
- benchmark failures must emit next-experiment recommendations, not just pass/fail summaries
- benchmark reporting must compare Relaytic against explicit reference approaches, not against vague internal expectations
- benchmark results must expose where Relaytic wins because of judgment, lifecycle handling, or constraints rather than raw score alone
- benchmark reports must state whether the gap came from first-pass route quality, challenger breadth, recalibration/retraining policy, or loop-control policy
- strong optional reference baselines should be used here where they increase honesty faster than in-core baseline rebuilding, especially FLAML for AutoML parity and MAPIE-backed uncertainty-aware comparisons where relevant

First implementation moves:

1. Freeze the benchmark schema and result taxonomy.
2. Build reference baselines with the current mature-library adapter stack plus optional FLAML where it materially strengthens parity claims.
3. Add ordinary public datasets plus constrained/operator-heavy cases that the raw-score baseline does not optimize for.
4. Add uncertainty-aware comparisons where abstention, calibration, or coverage matter.
5. Emit benchmark gap reports with next-experiment recommendations.
6. Keep deterministic, local-LLM, bounded-loop, frontier, and dojo modes separate in every report.

Minimum proof:

- one report showing parity or near-parity on a standard public task
- one report showing Relaytic advantage on a constrained or mandate-heavy task
- one failure case that emits an honest gap report and next experiment recommendations
- one report showing whether bounded-loop Relaytic materially improved over first-pass Relaytic on the same dataset

Innovation hook:

- this is the slice that turns architectural ambition into externally credible proof

## Slice 11A - Imported incumbents and bring-your-own challenger baselines

Status:
- implemented

Goal:
- imported incumbent evaluation
- bring-your-own-model challenge tracks
- beat-target contracts
- honest incumbent parity reporting

Load-bearing improvement:

- Relaytic should be able to treat an existing user or enterprise model as the incumbent to beat instead of assuming the current Relaytic run or a generic baseline is the only meaningful comparison target

Human surface:

- humans should be able to attach an incumbent model, scored prediction file, scorecard, or ruleset, inspect how Relaytic evaluated it locally, and see whether Relaytic truly beat it under the same contract

Agent surface:

- external agents should be able to register an incumbent challenger manifest, request reevaluation under current contracts, and consume parity/beat-target outcomes as stable artifacts

Intelligence source:

- local dataset evidence, explicit incumbent manifests, benchmark contracts, quality/budget contracts, decision-world models, and challenger science

Fallback rule:

- if the incumbent cannot be executed locally, Relaytic should fall back to prediction-file or metric-audit comparison mode and reduce its claims explicitly rather than pretending full parity

Required outputs:
- `external_challenger_manifest.json`
- `external_challenger_evaluation.json`
- `incumbent_parity_report.json`
- `beat_target_contract.json`

Required behavior:
- Relaytic must support at least three incumbent forms: local serialized model or adapter, scored prediction file, and explicit ruleset/scorecard wrapper
- imported incumbents must be evaluated under the same local split, metric, threshold, calibration, and decision contract where possible
- Relaytic must never blindly trust incumbent metrics supplied by the operator when local reevaluation is possible
- incumbent challenge results must be visible to evidence, benchmark, lifecycle, assist, and mission-control surfaces
- if the user says "beat this model," that should become an explicit contract rather than a vague note in the run brief
- Relaytic must be able to lose honestly and explain why the incumbent remained stronger

Shipped shape:

1. `relaytic benchmark run` now accepts `--incumbent-path`, `--incumbent-kind`, and `--incumbent-name`.
2. Relaytic supports three incumbent modes: local serialized model, explicit ruleset/scorecard, and prediction-file replay with reduced-claim fallback.
3. Benchmark persistence now includes incumbent manifests, incumbent evaluation, incumbent parity, and explicit beat-target contracts.
4. Run-summary, benchmark-show, assist-visible summary state, runtime manifests, and MCP benchmark surfaces now expose incumbent state explicitly.
5. Autonomy now consumes the beat-target contract so incumbent pressure can change follow-up behavior instead of staying a passive report.

Minimum proof:

- one case where Relaytic reevaluates a local incumbent model under the same split and metrics
- one case where Relaytic falls back to prediction-only incumbent comparison with reduced claims
- one case where Relaytic beats the incumbent and explains why
- one case where Relaytic fails to beat the incumbent and emits an honest next-step recommendation

Innovation hook:

- this is the slice that makes Relaytic look like a real adoption path inside serious labs and companies rather than a greenfield-only system

## Slice 11B - Mission control MVP, onboarding, and one-command install

Status:
- implemented

Goal:
- first real local control center
- low-friction install and onboarding
- one coherent operator cockpit
- UI parity with current CLI/MCP truth

Load-bearing improvement:

- Relaytic should expose one thin but real local control center and one low-friction install/onboarding path so humans and external agents can launch, monitor, steer, and demo the lab from one coherent surface instead of stitching together raw artifacts and shell commands

Human surface:

- humans should be able to install Relaytic, verify the environment, launch one local control center, attach a dataset and optional incumbent, inspect stage/timeline/next action, see quality and budget posture, and use assist/control actions without reading raw JSON files

Agent surface:

- external agents should be able to query the same mission-control state, launch metadata, onboarding posture, review queue, and action cards through stable JSON-first and MCP-accessible surfaces rather than relying on UI-only state

Intelligence source:

- canonical runtime state, run summary, benchmark/incumbent artifacts, quality and budget contracts, decision-lab outputs, control and assist state, doctor/install health, and later trace-backed enrichments

Fallback rule:

- if richer UI dependencies are unavailable, Relaytic must still expose the same control-center truth through CLI, MCP, and stable artifacts; if easy-install extras are unavailable, `python scripts/install_relaytic.py` plus `relaytic doctor` remains the canonical fallback

Required outputs:
- `mission_control_state.json`
- `review_queue_state.json`
- `control_center_layout.json`
- `onboarding_status.json`
- `install_experience_report.json`
- `launch_manifest.json`
- `demo_session_manifest.json`
- `ui_preferences.json`

Required behavior:
- Relaytic must provide one documented install path that ends in explicit environment verification and a clearly documented way to launch the local control center
- the control center must consume the same canonical runtime and artifact truth already used by CLI and MCP rather than inventing a separate UI-only state machine
- the first operator-facing surface must expose current stage, next recommended action, quality/budget posture, incumbent parity, decision-lab posture, and safe assist/control actions from one coherent view
- dataset selection, intent entry, and optional incumbent attachment should be possible from the same surface or a clearly linked first-run flow rather than through unrelated setup steps
- control-center actions must route through the existing assist and skeptical-control layers instead of bypassing them
- install/onboarding should make base versus full profiles, dependency health, recovery guidance, and host-integration hints explicit instead of leaving setup knowledge to repository archaeology
- later slices must extend the same mission-control and onboarding surfaces whenever they add new operator-visible behavior, new major artifact families, or new dependency expectations
- Slice 11B must remain thin: no duplicated business logic, no UI-only calculations, and no forked source of truth

First implementation moves:

1. Introduce `src/relaytic/mission_control/` as the canonical package for mission-control state, operator cards, onboarding state, launch metadata, and static control-center rendering.
2. Add `relaytic mission-control show` and `relaytic mission-control launch` so the same operator truth is available through CLI, artifact files, and MCP-accessible inspection.
3. Upgrade `scripts/install_relaytic.py`, packaging metadata, and doctor wiring so a fresh user can verify the environment and optionally land in the control center from one obvious path.
4. Add explicit install-health, onboarding, launch, review-queue, demo-session, and UI-preference artifacts so CLI, MCP, and UI render the same operator truth.
5. Ensure later slice docs and future code consume the same mission-control package instead of adding parallel UI shells.

Minimum proof:

- one fresh-install case that reaches explicit environment verification and a launchable local control center from one documented path
- one run that is monitored end to end from the control center without reading raw artifact files
- one imported-incumbent case that is visible in the control center with honest parity or beat-target state
- one assist or skeptical-control interaction that is visible in the same surface and changes operator understanding without bypassing guardrails

Innovation hook:

- this is the slice that turns Relaytic from an impressive CLI-first lab into something people can actually show, evaluate, and adopt without hiding the rigor under raw artifacts

## Slice 11C - Mission-control clarity, capabilities, and guided stage navigation

Status:
- implemented

Goal:
- explicit mode visibility
- explicit capability visibility
- explicit action affordances
- bounded stage navigation clarity
- starter-question visibility
- first-contact UX legibility for humans and external agents

Load-bearing improvement:

- Relaytic should make its control model legible on first contact so humans and external agents can immediately see what mode it is in, what it can do, what they can do next, what stage reruns are allowed, and what remains deliberately bounded, without guessing the shell vocabulary or reading raw artifacts

Human surface:

- humans should be able to open mission control or assist on a fresh run and immediately understand the current stage, current modes, next actor, current capabilities, safe next actions, bounded stage reruns, starter questions, and the fact that Relaytic challenges truth-bearing steering instead of obeying it blindly

Agent surface:

- external agents should be able to consume the same mode overview, capability manifest, action-affordance state, stage navigator, and starter-question state through stable JSON-first and MCP-accessible surfaces rather than reconstructing the interaction model from prose or prior turns

Intelligence source:

- shared run summary, assist controls, host inventory, backend discovery, benchmark/incumbent posture, decision-lab posture, skeptical-control posture, and doctor/install-health state

Fallback rule:

- if richer UI rendering or optional assist artifacts are missing, Relaytic must materialize the same clarity surface deterministically from the current canonical run state instead of hiding capabilities or assuming the operator already knows the workflow

Required outputs:
- `mode_overview.json`
- `capability_manifest.json`
- `action_affordances.json`
- `stage_navigator.json`
- `question_starters.json`

Required behavior:
- mission control must expose current autonomy mode, intelligence mode, routed mode, local profile, takeover availability, skeptical-control posture, and next actor as first-class state instead of leaving them implicit across other artifacts
- mission control and assist must expose what Relaytic can do now, what a human or external agent can do now, and what stage reruns are currently available without requiring a prior assist interaction
- stage navigation must be explicit that it is bounded stage rerun, not arbitrary checkpoint time travel
- starter questions must be visible so first-time users and external agents know how to ask for explanation, capabilities, incumbent reasoning, challenged-steering rationale, stage reruns, and safe takeover
- quick CLI and MCP mission-control surfaces must expose the high-signal counts and mode fields needed by external agents without forcing them to decode the full mission-control bundle first
- the clarity layer must remain thin and derived from the canonical run truth; it must not invent a separate UI-only interaction state machine

First implementation moves:

1. Extend `src/relaytic/mission_control/` with typed mode-overview, capability-manifest, action-affordance, stage-navigator, and starter-question artifacts.
2. Extend `src/relaytic/assist/` so assist state always carries available actions, stage targets, and suggested questions.
3. Make `relaytic mission-control show`, `relaytic mission-control launch`, `relaytic assist show`, and `relaytic assist turn` surface the same clarity state.
4. Materialize assist-derived clarity artifacts automatically from mission control when a fresh run has not yet touched the assist surface.
5. Keep the same clarity state visible through CLI, static HTML, and MCP-accessible mission-control inspection.

Minimum proof:

- one fresh-run case where mission control exposes modes, capabilities, actions, navigation scope, and starter questions even before `assist show` is called
- one assist case where `what can you do?` produces an explicit capabilities answer that mentions bounded questions, bounded stage reruns, safe takeover, and skeptical steering
- one CLI/MCP parity case where the quick mission-control surface exposes next actor, capability counts, question counts, and navigation scope consistently
- one bounded-navigation case where the operator can see that Relaytic supports rerunning named stages but not arbitrary checkpoint time travel

Innovation hook:

- this is the slice that turns the control center from a strong operator dashboard into something that feels immediately understandable, steerable, and demo-ready for first-time humans and external agents

## Slice 11E - Role-specific handbooks and handbook-aware onboarding

Status:
- implemented

Goal:
- role-specific handbooks
- handbook-aware onboarding
- handbook-aware terminal chat
- consistent host-facing agent entrypoints

Load-bearing improvement:

- Relaytic should stop assuming that one onboarding surface works equally well for first-time humans and external agents. The product should point each audience to the shortest correct guide directly from mission control, terminal chat, and checked-in host notes.

Human surface:

- human operators should be able to discover the narrative handbook directly from `relaytic mission-control show`, `relaytic mission-control chat`, and `relaytic mission-control launch --interactive`
- mission control should surface handbook cards, actions, and question starters instead of expecting the operator to browse the repo manually

Agent surface:

- external agents and host wrappers should be able to discover the command-first handbook from mission control and from the checked-in Claude, Codex/OpenAI, and OpenClaw host notes
- handbook discovery should be stable enough that another agent can learn the right repo contracts and CLI surfaces without guessing which markdown file matters first

Intelligence source:

- deterministic onboarding structure
- existing mission-control cards, action affordances, and question starters
- existing host-wrapper documentation surfaces

Fallback rule:

- if no run exists, Relaytic must still expose both handbook paths and explain which one a human versus an external agent should read first
- if a host-specific wrapper is missing, the handbook paths surfaced through mission control remain authoritative

Required behavior:

- mission control must expose both a human handbook and an agent handbook directly from onboarding state
- mission-control chat must answer handbook questions directly and support a `/handbook` shortcut
- handbook discovery must remain visible through question starters, action affordances, and control-center layout
- checked-in host wrapper notes should point to the agent handbook so new agents do not drift into competing local onboarding stories

Required outputs:

- `docs/handbooks/relaytic_user_handbook.md`
- `docs/handbooks/relaytic_agent_handbook.md`
- handbook-aware onboarding fields inside `onboarding_status.json`
- handbook-aware action affordances inside `action_affordances.json`
- handbook-aware starter questions inside `question_starters.json`

Minimum proof:

- one onboarding mission-control case where both handbook paths are visible without a run
- one mission-control chat case where `where is the handbook?` returns both guides with role-specific explanation
- one mission-control chat shortcut case where `/handbook` returns the same role-specific explanation
- one checked-in host-note case where a new agent is pointed to the same agent handbook instead of a divergent local instruction path

Innovation hook:

- this is the slice that makes Relaytic feel like a product that knows how to onboard both humans and agents, instead of a repo that expects them to reverse-engineer the right markdown file

## Slice 11F - Demo-grade onboarding, mode education, and stuck recovery

Status:
- implemented

Goal:
- guided demo flow
- mode education
- stuck recovery
- recruiter-safe first-contact experience

Load-bearing improvement:

- Relaytic should stop requiring first-time demo audiences to infer the product shape. Mission control, chat, and the handbook stack should explain the shortest useful demo flow, what each major surface is for, and what to do when the next step is unclear.

Human surface:

- humans should be able to open mission control and immediately find a demo flow, mode explanations, stuck guidance, and a recruiter-safe walkthrough
- mission-control chat should support direct help through `/demo`, `/modes`, and `/stuck`

Agent surface:

- external agents should be able to consume guided demo flow, mode explanations, and stuck guidance directly from onboarding payloads
- the handbook stack should explain safe operating patterns and source-of-truth rules without forcing an agent to reverse-engineer the repo

Intelligence source:

- deterministic onboarding structure
- current mission-control, capability, and action truth
- handbook and walkthrough documents

Fallback rule:

- if no run exists, Relaytic must still explain the demo path, the modes, and stuck recovery
- if a run exists, the same guidance must remain available without weakening bounded stage and skeptical-control rules

Required behavior:

- mission control must expose guided demo flow directly from onboarding state
- mission control must expose explicit mode explanations directly from onboarding state
- mission control must expose explicit stuck guidance directly from onboarding state
- mission-control chat must support `/demo`, `/modes`, and `/stuck`
- the same guidance must also work through natural-language onboarding questions
- the user handbook must explain the main flow, what happens after a run starts, and what to do when stuck
- the agent handbook must explain the safe operating pattern, source-of-truth hierarchy, and what to do when stuck
- a separate demo walkthrough must exist for recruiter-safe demos

Required outputs:

- guided demo flow inside `onboarding_status.json`
- mode explanations inside `onboarding_status.json`
- stuck guidance inside `onboarding_status.json`
- onboarding action affordances for demo and stuck recovery
- onboarding starter questions for demo flow, mode explanation, and stuck recovery
- `docs/handbooks/relaytic_demo_walkthrough.md`

Minimum proof:

- one mission-control onboarding case where guided demo flow, mode explanations, and stuck guidance are visible
- one rendered mission-control case where those sections appear in the human-facing output
- one mission-control chat case where `/demo`, `/modes`, and `/stuck` work
- one handbook case where user, agent, and walkthrough docs all cover demo flow and stuck recovery

Innovation hook:

- this is the slice that makes Relaytic feel much less like a powerful internal tool and much more like something you can hand to a smart outsider without standing next to them

## Slice 11G - Adaptive human onboarding and lightweight local semantic guidance

Status:
- implemented

Goal:
- adaptive human onboarding
- visible onboarding session state
- analysis-first versus governed-run routing
- messy-input recovery
- lightweight local semantic help

Load-bearing improvement:

- Relaytic should stop assuming first-contact humans behave like disciplined CLI users. Mission-control chat should capture data paths, objectives, and run-start readiness across turns, distinguish quick analysis-first requests from full governed-run requests, rescue messy first messages when a lightweight local helper is available, and still keep validation and run creation deterministic.

Human surface:

- humans should be able to paste a dataset path directly into mission-control chat, describe the goal later, inspect captured state with `/state`, reset with `/reset`, and confirm before the first run starts
- humans should be able to ask for a quick analysis, top signals, or a correlation pass without being forced into the full governed run path
- the full one-line bootstrap should attempt to provision the lightweight onboarding helper automatically on the full profile

Agent surface:

- external agents should be able to read `onboarding_chat_session_state.json` and understand captured data path, captured objective, next expected input, semantic-backend status, and run-start readiness without scraping chat prose
- install payloads should explicitly report whether onboarding-local-LLM provisioning was requested and what happened

Intelligence source:

- deterministic path detection, file-existence validation, state persistence, and run creation
- bounded local semantic extraction for messy human onboarding input
- shared mission-control artifact truth

Fallback rule:

- if no local semantic backend is available, Relaytic must still accept direct path pastes, explicit objective messages, visible onboarding state, and explicit confirmation before run creation
- if a local semantic backend is available, it may help interpret messy human input but must not replace deterministic file validation, run creation, or control decisions

Required behavior:

- mission-control chat must capture a pasted dataset path and ask for the missing objective naturally
- mission-control chat must capture an objective without losing earlier onboarding state
- mission-control chat must support one messy first-turn case that combines a dataset hint and a goal
- mission-control chat must expose captured state through `/state`
- mission-control chat must support `/reset`
- mission-control chat must distinguish analysis-first requests from full governed-run requests and execute a direct exploratory pass when the lightweight path is enough
- configured onboarding run directories must respect policy defaults instead of hardcoded demo paths
- full-profile install bootstrap must attempt lightweight onboarding-helper setup by default
- canonical `policy:` configs and legacy top-level configs must both work for local semantic onboarding

Required outputs:

- `onboarding_chat_session_state.json`
- updated mission-control onboarding cards and rendered onboarding sections
- onboarding-state visibility for objective family plus direct-analysis summary/report path
- install payloads that include onboarding-local-LLM setup intent and result

Minimum proof:

- one mission-control chat case where Relaytic captures a dataset path and asks for the objective
- one mission-control chat case where Relaytic captures data plus objective and starts the first run after confirmation
- one mission-control chat case where Relaytic handles an analysis-first request without creating a full governed run
- one mission-control chat case where a lightweight local semantic helper rescues messy human wording
- one install-bootstrap case where onboarding-local-LLM setup is requested

Innovation hook:

- this is the slice that makes Relaytic feel less like a command grammar and more like a guided local product for real humans, while still keeping the authority path deterministic

## Slice 12 - Dojo mode and guarded self-improvement

Status:
- implemented

Goal:
- explicit dojo mode
- quarantined improvements
- method self-improvement
- experimental architecture proposals

Load-bearing improvement:

- Relaytic should improve not only route priors but also decision-world-model heuristics, method-compiler behavior, search-control policy, and data-acquisition reasoning under hard validation gates

Human surface:

- humans should be able to inspect dojo review state through `relaytic dojo review`, `relaytic dojo show`, mission-control cards, and run summaries, and see which proposed self-improvements target route search, decision usefulness, data acquisition, or method compilation and why they were promoted, rejected, quarantined, or rolled back

Agent surface:

- external agents should be able to consume dojo proposals, validation outcomes, promotion/rollback state, and architecture-proposal quarantine through explicit artifacts plus JSON-first/MCP-accessible dojo surfaces

Intelligence source:

- benchmark gaps, validated feedback, outcome evidence, prior failure cases, gold decision cases, and quarantined experimental proposals

Fallback rule:

- if dojo validation data or benchmark proof is unavailable, the current incumbent behavior remains authoritative, dojo outputs stay quarantined, and no authoritative runtime defaults are mutated silently

Required outputs:
- `dojo_session.json`
- `dojo_hypotheses.json`
- `dojo_results.json`
- `dojo_promotions.json`
- `architecture_proposals.json`

Required behavior:
- dojo outputs must remain quarantined until they beat the incumbent on benchmark validation and pass the visible quality-gate proxy used by the current implementation
- no dojo promotion may become default behavior without an explicit promotion artifact
- dojo must improve strategies, priors, challenger design, route search, decision-world-model heuristics, and method-compilation logic before it is allowed to touch deeper architecture proposals
- dojo must not weaken intervention contracts, override skepticism, or control-injection defenses without explicit regression evidence that those guarantees still hold
- every dojo promotion must preserve rollback, provenance, and benchmark comparability
- dojo proposals, promotions, rejections, and rollbacks must extend the mission-control surface introduced in Slice 11B and expanded through Slices 11C, 11D, 11E, 11F, and 11G instead of remaining CLI-only state
- early architecture proposals must remain explicitly quarantined and non-authoritative even when method-level proposals are promotable
- dojo review and rollback must be available through stable CLI surfaces before later pulse, trace, or search slices build on them

First implementation moves:

1. Add a quarantined dojo workspace and promotion ledger.
2. Restrict early dojo scope to strategy, challenger, and prior improvements.
3. Wire dojo outputs into benchmark and golden-case validation gates.
4. Add promotion, rejection, and rollback tests for dojo proposals.
5. Only after that, allow experimental architecture proposals.

Minimum proof:

- one dojo proposal that is rejected with clear reasons
- one dojo proposal that is promoted only after beating the incumbent on required validations
- one rollback of a previously promoted dojo artifact
- one architecture proposal that remains quarantined instead of being promoted by the early dojo path

Innovation hook:

- Relaytic should self-improve like a lab, not mutate like an unstable agent demo

## Slice 12A - Lab Pulse, periodic awareness, and bounded proactive follow-up

Status: implemented.

Goal:
- scheduled lab pulse
- bounded periodic awareness
- innovation watch
- challenge watchlists
- long-term memory maintenance
- safe background maintenance and queueing

Load-bearing improvement:

- Relaytic should be able to wake up on a bounded schedule, inspect its local artifact universe, detect stale runs, benchmark debt, new relevant methods, data freshness issues, or memory-maintenance needs, perform explicit memory retention and compaction work, and either recommend or queue safe bounded follow-up without silently drifting its core behavior

Human surface:

- humans should be able to inspect the pulse schedule, pulse reasons, skipped versus executed pulse runs, innovation-watch findings, queued follow-ups, and why Relaytic did or did not act

Agent surface:

- external agents should be able to read pulse recommendations, watchlists, skip reasons, and queued follow-up actions as stable artifacts and optionally trigger the same pulse manually

Intelligence source:

- runtime state, stage/event history, benchmark gaps, research memory, causal memory, dojo proposals, local source freshness, and policy-gated redacted innovation retrieval

Fallback rule:

- if a richer pulse input is unavailable, Relaytic should record that it skipped or reduced the pulse rather than inventing urgency or silently doing nothing

Required outputs:
- `pulse_schedule.json`
- `pulse_run_report.json`
- `pulse_skip_report.json`
- `pulse_recommendations.json`
- `innovation_watch_report.json`
- `challenge_watchlist.json`
- `pulse_checkpoint.json`
- `memory_compaction_plan.json`
- `memory_compaction_report.json`
- `memory_pinning_index.json`

Required behavior:

- the pulse must be policy-gated, explicitly scheduled, and stoppable
- pulse should distinguish observe-only, propose-only, and bounded-execute modes
- pulse must not silently mutate defaults, promote dojo outputs, or rewrite core contracts
- pulse may safely trigger only bounded low-risk work by default, such as memory compaction/flush, benchmark refresh recommendation, research gather recommendation, challenge queue refresh, or stale-run review queueing
- memory maintenance must upgrade Relaytic from analog retrieval toward a long-term memory stack by applying retention, compaction, pinning, and replay rules to episodic, intervention, outcome, and method memory artifacts
- heavier actions should require either existing autonomy/control contracts or remain as explicit recommendations
- innovation watch must stay rowless and redacted by default for any external retrieval
- pulse runs must leave explicit skip reasons when nothing useful was done, so the system does not look alive through empty churn
- mission-control and assist surfaces should later expose pulse history and next queued pulse actions directly

First implementation moves:

1. Add a pulse scheduler and pulse-run ledger over the local runtime/event system.
2. Add policy controls for disabled, observe-only, propose-only, and bounded-execute pulse modes.
3. Add innovation-watch gathering over research memory, benchmark gaps, and redacted external method retrieval.
4. Add challenge watchlists for stale champions, unclosed benchmark gaps, and untested incumbent beat-targets.
5. Add memory-maintenance and queue-refresh actions as the first bounded pulse actions.
6. Add skip-report and throttle logic so pulse avoids busy-loop theater.

Minimum proof:

- one case where pulse wakes, finds nothing worth doing, and records an explicit skip report
- one case where pulse notices stale or weak state and writes a challenge watchlist without taking unsafe action
- one case where pulse queues one bounded low-risk follow-up through explicit policy
- one case where innovation watch surfaces a new method or benchmark lead through redacted retrieval without leaking private data
- one case where pulse compacts or pins memory in a way that changes later retrieval quality or avoids forgetting a previously harmful intervention

Innovation hook:

- this is the slice that makes Relaytic feel like a living lab without turning it into an unsupervised drift engine

## Slice 12B - First-class tracing, agent evaluation, and runtime security harnesses

Status:
- Implemented.

Goal:
- one canonical trace model
- replayable specialist/tool/intervention/branch traces
- structured competing claim packets
- deterministic adjudication scorecards
- agent-behavior evaluation
- runtime security harnesses
- adversarial control and tool-safety testing

Load-bearing improvement:

- Relaytic should be able to explain, replay, compare, and test complex agentic behavior from one trace substrate instead of scattered logs, while resolving multi-specialist disagreement through explicit claim packets and deterministic adjudication rather than hidden precedence only

Human surface:

- humans should be able to inspect one trace timeline across specialists, tools, interventions, and branches, see competing proposals for a decision, and read exactly why one claim won and others lost

Agent surface:

- external agents should be able to consume trace spans, branch graphs, claim packets, adjudication scorecards, replay reports, evaluation matrices, and security-harness results through stable JSON-first surfaces rather than scraping logs

Intelligence source:

- runtime events, control artifacts, autonomy lineage, benchmark outcomes, replayable tool traces, deterministic claim scoring, adversarial prompts, and policy-aware evaluation harnesses

Fallback rule:

- if richer trace sinks, semantic helpers, or external observability adapters are unavailable, Relaytic must still write the same canonical local trace, deterministic claim packets, adjudication scorecards, and evaluation artifacts on disk

Required outputs:
- `trace_model.json`
- `trace_span_log.jsonl`
- `specialist_trace_index.json`
- `tool_trace_log.jsonl`
- `intervention_trace_log.jsonl`
- `branch_trace_graph.json`
- `claim_packet_log.jsonl`
- `adjudication_scorecard.json`
- `decision_replay_report.json`
- `agent_eval_matrix.json`
- `security_eval_report.json`
- `red_team_report.json`
- `protocol_conformance_report.json`
- `host_surface_matrix.json`

Required behavior:

- Slice 12B must treat runtime traces as a first-class local source of truth for replay and comparison rather than a debug side channel
- trace spans must cover specialist execution, tool calls, intervention handling, branch expansion, retries, and final decisions under one stable schema
- every specialist contribution that can affect a later decision should be representable as a structured claim packet rather than only prose or implicit artifact precedence
- the claim packet contract should carry at least `claim_id`, `stage`, `specialist`, `claim_type`, `proposed_action`, `confidence`, `evidence_refs`, `risk_flags`, `assumptions`, `falsifiers`, `policy_constraints`, and `trace_ref`
- Slice 12B must add one deterministic adjudicator that scores competing claims under an explicit scorecard instead of deciding purely through hidden precedence
- the adjudication scorecard should score each claim on explicit axes such as empirical support, policy fit, benchmark fit, memory consistency, decision value, uncertainty penalty, risk penalty, cost penalty, and reversibility bonus
- optional semantic helpers may generate or critique claim packets, but they must not become the final adjudicator
- evaluation harnesses must cover at least control injection, tool misuse, unsafe branch expansion, and skeptical-override regression
- security/eval results must be consumable by later dojo, search-controller, and mission-control slices without hand translation
- any optional observability adapter must remain secondary to the canonical local trace artifacts
- mission-control should later consume the trace graph and adjudication scorecard directly so humans and agents can see competing proposals, rejected alternatives, and why Relaytic chose the winning claim

Minimum proof:

- one run replayed end to end from the canonical trace artifacts
- one decision with at least three competing claim packets and one explicit winning claim
- one higher-confidence claim that still loses because policy, risk, benchmark fit, or decision value says it should lose
- one adversarial steering case that is rejected and captured in the security-eval report
- one tool-misuse or unsafe-branch case that fails safely and is recorded in the eval matrix
- one CLI-versus-MCP conformance case that passes or records an explicit failure in `protocol_conformance_report.json`
- one case where mission control reads the trace graph, adjudication winner, or eval posture directly

## Slice 12C - Differentiated result handoff and durable learnings

### Status

Implemented.

### Load-bearing improvement

- Relaytic now ends a serious run with differentiated human and agent result reports, explicit next-run options, persisted next-run focus, and durable local learnings that can be reviewed or reset deliberately

### Human surface

- humans can now ask what Relaytic found, read a narrative result report, choose whether the next run should stay on the same data, add data, or start over, inspect what Relaytic learned from prior runs, and reset those learnings when they want a clean slate

### Agent surface

- external agents can now consume a terser agent handoff, persist next-run focus through stable JSON/MCP surfaces, inspect durable learnings, and reset workspace learnings without scraping markdown

### Intelligence source

- canonical run-summary truth, explicit handoff synthesis, and durable local learnings harvested from assumptions, feedback, benchmark outcomes, control incidents, next-run focus decisions, and open safety/eval lessons

### Fallback rule

- if differentiated handoff or durable learnings are unavailable, Relaytic must still preserve `run_summary.json` and `reports/summary.md` as the fallback truth while recording that the handoff or learnings layer is missing

### Required behavior

- the user report and agent report must be generated from the same canonical run summary, not from two separate hidden states
- Relaytic must expose explicit next-run choices for:
  - `same_data`
  - `add_data`
  - `new_dataset`
- next-run focus must be persisted and reviewable instead of living only in chat state
- durable learnings must be local-first, resettable, and surfaced through CLI, mission control, assist, and MCP
- mission-control chat should support natural turns like:
  - `what did you find?`
  - `use the same data next time but focus on recall`
  - `show learnings`
  - `reset the learnings`
- durable learnings should be visible to the memory layer as explicit workspace priors rather than remaining UI-only state

### Proof obligation

- Relaytic must prove that humans and agents receive differentiated but aligned post-run handoffs, that next-run steering is explicit and durable, and that workspace learnings survive across runs until deliberately reset

### Acceptance criteria

- one governed run writes both `reports/user_result_report.md` and `reports/agent_result_report.md` and they are meaningfully different
- one persisted next-run focus updates run-summary handoff state without forcing a rerun
- one durable learnings view shows both workspace learnings and current-run active learnings
- one reset case clears durable learnings and does not silently repopulate them on the same refresh
- one mission-control run-context chat case supports result-report review, next-run focus selection, learnings review, and learnings reset in a natural multi-turn flow
- one external-agent or MCP case uses the same handoff and learnings truth without scraping prose
- one memory case shows that durable learnings are visible as reusable priors

## Slice 12D - Workspace-first continuity, result contracts, and governed learnings

### Status

Planned.

### Load-bearing improvement

- Relaytic should stop treating the isolated run as the whole product and instead become a governed multi-run workspace that carries machine-stable result contracts, explicit continuity state, governed learnings, and next-run planning across runs

### Human surface

- humans should be able to finish a run, review one user-optimized result report, understand what Relaytic currently believes, see what remains unresolved, choose whether to continue on the same data, add data, or start over, and then continue from the same workspace without losing context

### Agent surface

- external agents should be able to consume one machine-stable result contract, workspace lineage, continuity state, governed learnings, and next-run plan without scraping narrative prose or inferring continuity from file layout alone

### Intelligence source

- canonical run truth from Slice 12C, trace and adjudication truth from Slice 12B, durable learnings, feedback/outcome memory, next-run focus decisions, and explicit workspace-level continuity policy

### Fallback rule

- if workspace state is unavailable, Relaytic must still preserve the current per-run handoff and learnings surfaces from Slice 12C while recording that workspace continuity is degraded rather than silently improvising continuity from filenames or directory guesses

### Required behavior

- every serious run should belong to a workspace once continuity exists; Relaytic must not rely on parent-directory heuristics as the primary continuity mechanism
- Slice 12C handoff artifacts remain public and valid, but they should become per-run snapshots that are mirrored into workspace-backed continuity rather than competing truth sources
- Relaytic must generate one machine-stable `result_contract.json` per serious run that states:
  - what Relaytic currently believes
  - how strong the evidence is
  - what remains unresolved
  - what Relaytic recommends next
  - what would change its mind
- `reports/user_result_report.md` and `reports/agent_result_report.md` must become differentiated renderings of `result_contract.json`, not separate reasoning products
- governed learnings must become typed records with explicit source, confidence, status, reaffirmation state, invalidation history, and optional expiry rather than free-form sticky memory
- Relaytic must maintain workspace lineage and focus history so later runs can explain how the current direction evolved
- Relaytic must emit one explicit `next_run_plan.json` that can choose between:
  - `same_data`
  - `add_data`
  - `new_dataset`
  and should also state the lower-level reason, such as more search, recalibration, retraining, incumbent comparison, or restart
- mission control, assist, and MCP must expose workspace continuity, result-contract posture, and next-run planning directly instead of only showing the current run
- memory retrieval should prefer explicit workspace state and governed learnings over loose analog assumptions when both are available
- existing `relaytic handoff *` and `relaytic learnings *` commands must remain supported as compatibility-preserving views over workspace-backed truth once Slice 12D lands

### Proof obligation

- Relaytic must prove that multi-run continuity is explicit, governed, and machine-usable rather than hidden in prose, path conventions, or operator memory

### Required outputs

- `workspace_state.json`
- `workspace_lineage.json`
- `workspace_focus_history.json`
- `workspace_memory_policy.json`
- `result_contract.json`
- `confidence_posture.json`
- `belief_revision_triggers.json`
- `next_run_plan.json`
- `focus_decision_record.json`
- `data_expansion_candidates.json`

### Acceptance criteria

Slice 12D is acceptable only if:

1. one workspace carries at least two runs with visible lineage and focus history
2. one run proves that the user report and agent report are differentiated renderings of the same `result_contract.json`
3. one next-run plan chooses `add_data` or `new_dataset` because the value contract says deeper search on the same data is low value
4. one governed-learning case invalidates or expires stale guidance without deleting its history
5. one mission-control or assist surface shows current belief, confidence posture, unresolved items, recommended next move, and belief-revision triggers from workspace-backed truth
6. one external-agent or MCP case continues a workspace using machine-stable workspace and next-run-plan artifacts rather than scraping markdown
7. one compatibility case proves that existing Slice 12C handoff and learnings commands still work on top of workspace-backed truth

### Required verification

Slice 12D should not be considered complete without targeted tests that cover at least:

- one multi-run workspace lineage case
- one result-contract rendering-parity case
- one governed-learning invalidation or expiry case
- one next-run planner case that chooses between same data, add data, and new dataset
- one mission-control or assist workspace-continuity case
- one external-agent or MCP workspace-continuation case
- one memory-integration case where workspace truth overrides weaker analog guesses

## Slice 13 - Search controller, accelerated execution, and distributed local experimentation

Goal:
- search-controller policy
- execution-profile detection
- device-aware planning
- CPU/GPU/local-cluster profile choice
- checkpointable distributed-plan baseline

Load-bearing improvement:

- Relaytic should be able to run wider challenger fields, deeper HPO, calibration branches, uncertainty/abstention experiments, and dynamic controller-adjusted branch depth under one explicit search controller instead of only static narrow search choices

Human surface:

- humans should be able to inspect why Relaytic widened or pruned search, which device profile it chose, and which branches were considered too expensive or too low value

Agent surface:

- external agents should be able to consume one search-controller plan, execution strategy, checkpoint state, scheduler map, HPO campaign report, and branch-pruning rationale without inferring hidden orchestration decisions

Intelligence source:

- budget-aware search policy, benchmark gaps, completion/autonomy value signals, hardware detection, and optional distributed execution adapters

Fallback rule:

- when acceleration or distributed execution is unavailable, Relaytic must still run the same search logic in a narrower local profile rather than changing the source of truth or losing replayability

Required outputs:
- `search_controller_plan.json`
- `portfolio_search_trace.json`
- `hpo_campaign_report.json`
- `search_decision_ledger.json`
- `execution_backend_profile.json`
- `device_allocation.json`
- `distributed_run_plan.json`
- `scheduler_job_map.json`
- `checkpoint_state.json`
- `execution_strategy_report.json`

Required behavior:

- execution acceleration must preserve provenance, checkpointing, and replayability
- Slice 13 must consume the explicit quality and budget contracts from Slice 10B instead of inventing separate hidden search limits
- Slice 13 must consume real runtime/control accounting and any beat-target contract from Slice 11A rather than relying only on estimated search effort or abstract parity goals
- Slice 13 should consume the canonical trace/eval artifacts from Slice 12B so branch expansion, pruning, and controller changes can be justified by replayable evidence rather than implicit heuristics
- search widening, pruning, HPO allocation, and device/backend choices must extend the mission-control surface introduced in Slice 11B and expanded through Slices 11C, 11D, 11E, 11F, and 11G so humans and external agents can see why search did or did not go deeper
- device-aware planning must change *how* Relaytic executes, not silently change *what* it believes
- distributed execution must remain resumable and safe for long local runs
- search expansion must remain budgeted and justified by expected decision value, not only by abstract score-chasing
- the search controller must be able to prune low-value branches early and widen high-value branches explicitly
- broader route families, calibration variants, uncertainty wraps, abstention policies, imported-incumbent beat-target branches, and deeper HPO campaigns should be eligible where their value is justified

Minimum proof:

- one same-plan run that succeeds across two execution profiles
- one interrupted distributed run that resumes from checkpoint
- one agent-consumable execution strategy report
- one case where the search controller rejects a low-value branch and expands a higher-value branch with explicit justification
- one case where the search controller widens or cuts HPO effort because the decision contract, beat-target pressure, or trace evidence says more search is or is not worth it

## Slice 13A - Release safety, build attestation, and packaging discipline

Goal:
- release-bundle scanning
- artifact attestation
- source-map and debug-artifact rejection
- sensitive-string and machine-path auditing
- packaging regression gates for demos and public builds

Load-bearing improvement:

- Relaytic should be able to prove that a built distribution contains only the intended product surface and does not leak machine paths, source maps, hidden debug files, or accidental sensitive strings

Human surface:

- humans should be able to inspect one release-safety report that says whether a build is safe to hand out and what must be fixed if it is not

Agent surface:

- external agents should be able to consume one release-safety bundle and fail a packaging workflow without scraping prose

Intelligence source:

- built distributions, docs bundles, host bundles, install surfaces, git-safety rules, and explicit release policy

Fallback rule:

- when a packaged artifact is unavailable, Relaytic should still run the same checks against the local workspace and mark the result as pre-release rather than silently skipping the gate

Required outputs:
- `release_safety_scan.json`
- `distribution_manifest.json`
- `artifact_inventory.json`
- `artifact_attestation.json`
- `source_map_audit.json`
- `sensitive_string_audit.json`
- `release_bundle_report.json`
- `packaging_regression_report.json`

Required behavior:

- Slice 13A must upgrade the existing git-safety posture into a real release-safety layer rather than a one-off repository scan
- release safety must scan built artifacts, host bundles, generated HTML, manifests, packaged docs, and install surfaces rather than only tracked source files
- release safety must explicitly detect machine paths, source maps, hidden internal URLs, oversized accidental payloads, obvious secret-like strings, and debug-only manifests
- release attestation must prove which files were intentionally included and which checks were run against them
- `relaytic doctor` and later mission-control packaging surfaces should consume the same release-safety posture

Minimum proof:

- one build with an injected machine path is rejected with an explicit reason
- one build with an injected source map or debug manifest is rejected with an explicit artifact path
- one clean build produces a complete attestation showing scanned files and passed checks
- one host-bundle or docs-bundle surface is included in the release-safety gate

## Slice 13B - Event bus, runtime hooks, and visible permission modes

Goal:
- typed runtime-event schemas
- event subscription registry
- hook registry and dispatch reporting
- visible permission modes
- tool-permission matrix and approval-policy reporting

Load-bearing improvement:

- Relaytic should expose one canonical event bus plus one explicit authority model so later daemon, remote-control, and richer mission-control work can subscribe to real runtime truth instead of reconstructing state from artifacts after the fact

Human surface:

- humans should be able to see the current permission mode, pending approvals, recent event timeline, and which tools or actions are allowed, approval-gated, or denied

Agent surface:

- external agents should be able to query one session capability contract, one permission-mode artifact, and one machine-readable event or hook registry without trial-and-error tool use

Intelligence source:

- the shared runtime gateway, control contracts, capability profiles, workspace continuity state, and explicit operator or agent policy overlays

Fallback rule:

- when subscriptions or richer hook handlers are unavailable, Relaytic must still emit the canonical event stream and permission decisions through stable artifacts rather than silently degrading into hidden local state

Required outputs:
- `event_schema.json`
- `event_subscription_registry.json`
- `hook_registry.json`
- `hook_dispatch_report.json`
- `permission_mode.json`
- `tool_permission_matrix.json`
- `approval_policy_report.json`
- `permission_decision_log.jsonl`
- `session_capability_contract.json`

Required behavior:

- Slice 13B must upgrade the existing `lab_event_stream.jsonl`, `hook_execution_log.json`, and `capability_profiles.json` rather than replacing them with a second incompatible runtime history
- event emission must cover session lifecycle, prompt submit, tool pre/post use, stage transitions, background-job lifecycle, workspace resume, compaction lifecycle, and approval requested/approved/denied
- permission modes must be explicit and user-visible, with at least `review`, `plan`, `safe_execute`, and `bounded_autonomy`
- mission control, CLI, MCP, and later remote surfaces must expose the same current mode and the same tool or action matrix
- denied and approval-gated actions must be replayable from one permission-decision log rather than scattered across unrelated artifacts

Minimum proof:

- one action allowed in `bounded_autonomy` is blocked or approval-gated in `review`
- one hook subscriber reacts to a runtime event without changing the canonical source of truth
- one CLI and one MCP surface report the same permission mode and pending-approval posture
- one denied or approval-gated action is replayable from the event and permission logs alone

## Slice 13C - Background daemon, resumable jobs, and memory maintenance

Goal:
- bounded daemon orchestration
- background-job registry and logs
- checkpoint-backed resumability
- explicit background approval queue
- memory-maintenance queue and stale-job reporting

Load-bearing improvement:

- Relaytic should be able to run bounded background work, resume interrupted jobs, and maintain workspace memory over time without becoming a hidden daemon that acts outside operator or agent visibility

Human surface:

- humans should be able to see active jobs, waiting jobs, resumed jobs, stale jobs, and memory-maintenance jobs from one mission-control surface

Agent surface:

- external agents should be able to query one background-job registry, one resume manifest, and one approval queue to understand what is running, what is paused, and what needs a decision

Intelligence source:

- event bus and permission modes from Slice 13B, pulse watchlists, search-controller outputs, workspace state, result contracts, and governed learnings or memory policy

Fallback rule:

- when background execution is disabled, Relaytic must still produce the same planned job manifests and resume plans so the work can be run interactively without changing truth or dropping state

Required outputs:
- `daemon_state.json`
- `background_job_registry.json`
- `background_job_log.jsonl`
- `background_checkpoint.json`
- `resume_session_manifest.json`
- `background_approval_queue.json`
- `memory_maintenance_queue.json`
- `memory_maintenance_report.json`
- `search_resume_plan.json`
- `stale_job_report.json`

Required behavior:

- Slice 13C must consume the event and permission substrate from Slice 13B instead of inventing a daemon-specific authority model
- background work must stay bounded, explicit, and stoppable; no hidden long-running activity is acceptable
- daemon-managed jobs must cover at least pulse follow-up, search-controller campaigns, memory compaction or reaffirmation maintenance, and long-running benchmark or challenger jobs when policy allows
- resumability must be based on explicit checkpoints and job manifests rather than process-local memory
- workspace resume should restore the current result contract, active jobs, pending approvals, and next-run posture coherently

Minimum proof:

- one long-running search or benchmark job resumes from checkpoint after interruption
- one memory-maintenance task runs in the background and leaves an explicit before/after report
- one background task is queued, approved, and started through the explicit approval path rather than silently running
- one stale or failed job is surfaced with a reason and recovery suggestion

## Slice 14 - Real-world feasibility, domain constraints, and action boundaries

Goal:
- physical-system detection hooks
- regulatory and operational constraint hooks
- feasible-region reporting
- extrapolation risk labeling
- physically and operationally bounded proposal generation

Load-bearing improvement:

- Relaytic should be able to reason about whether a promising route or action is actually allowable, operable, and decision-useful under real domain constraints rather than treating feasibility as a post-hoc warning

Human surface:

- humans should be able to inspect which physical, regulatory, queue, compliance, or action-boundary constraints changed Relaytic's recommendation

Agent surface:

- external agents should be able to consume explicit feasibility and action-boundary artifacts without reading narrative reports

Intelligence source:

- domain constraints, runtime evidence, decision-world models, source contracts, and optional domain-specific reference knowledge

Fallback rule:

- when explicit domain constraints are missing, Relaytic should emit an under-specified feasibility posture and avoid overclaiming deployability

Required outputs:
- `trajectory_constraint_report.json`
- `feasible_region_map.json`
- `extrapolation_risk_report.json`
- `decision_constraint_report.json`
- `action_boundary_report.json`
- `deployability_assessment.json`
- `review_gate_state.json`
- `constraint_override_request.json`
- `counterfactual_region_report.json`

Required behavior:

- physical, regulatory, and operational constraints must be explicit inputs to proposal generation, not cosmetic warnings after the fact
- Relaytic must distinguish "promising", "unproven", "physically implausible", "operationally infeasible", and "policy-constrained" proposals
- action-boundary reasoning must integrate with abstention, review, rollback, and data-acquisition suggestions rather than living in a separate report
- feasibility must consume permission modes and approval posture from Slice 13B so infeasible or regulated actions can be approval-gated instead of merely annotated
- feasibility must consume background and resumable job posture from Slice 13C so deferred work, waiting approvals, and long-running experiments remain aligned with real operational constraints
- feasibility must be able to emit an explicit constraint override request rather than silently flattening domain conflicts into warnings
- feasibility and action-boundary changes must extend the mission-control surface introduced in Slice 11B and expanded through Slices 11C, 11D, 11E, 11F, and 11G so operator-facing recommendations stay legible as constraints sharpen

Minimum proof:

- one domain case where physically implausible proposals are suppressed
- one case where feasibility constraints materially alter route or recommendation output
- one case where operational or compliance constraints alter the decision policy or recommended next action
- one case where Relaytic emits a review gate or override request instead of only a warning

## Slice 14A - Remote mission control, approvals, and supervision handoff

Goal:
- trusted remote-inspection surface
- approval and denial queue
- remote supervision handoff
- remote presence and freshness reporting
- remote-control audit and notification delivery

Load-bearing improvement:

- Relaytic should allow humans and external agents to supervise a workspace remotely through the same truth used locally, including approvals, denials, resume actions, and handoff between operators or agents

Human surface:

- humans should be able to inspect remote session status, pending approvals, supervision handoff state, and remote presence without guessing whether the remote surface is stale or authoritative

Agent surface:

- external agents should be able to read and act on approval queues, supervision handoffs, and remote workspace truth through stable JSON-first surfaces rather than screen-scraping a UI shell

Intelligence source:

- mission-control truth, event bus and permission modes from Slice 13B, daemon state from Slice 13C, workspace or result-contract state, and interoperability transport configuration

Fallback rule:

- when remote transport is disabled or unavailable, Relaytic must still preserve the same approval and supervision artifacts locally so the same decisions can be made through CLI or MCP without remote drift

Required outputs:
- `remote_session_manifest.json`
- `remote_transport_report.json`
- `approval_request_queue.json`
- `approval_decision_log.jsonl`
- `remote_operator_presence.json`
- `supervision_handoff.json`
- `notification_delivery_report.json`
- `remote_control_audit.json`

Required behavior:

- Slice 14A must remain local-first by default; remote access should be explicitly enabled and clearly marked
- remote mission control must be read-mostly unless an action is explicitly approval-scoped or policy-allowed
- approvals, denials, and handoffs must use the same permission and event substrate as local sessions rather than inventing remote-only authority logic
- remote session state must expose freshness and transport posture so operators and agents know whether they are looking at live or stale state
- mission control, CLI, MCP, and remote supervision must remain semantically aligned on result contract, active jobs, pending approvals, and next-run posture

Minimum proof:

- one remote approval or denial changes the same local workspace truth that CLI and MCP later read
- one supervision handoff transfers control cleanly between a human and an external agent
- one remote session shows freshness and transport status explicitly
- one locally disabled remote surface fails closed and leaves a clear audit trail

## Slice 15 - Mission-control expansion, packaging, integrations, demos, polish

Goal:
- mission-control surfaces
- package extras
- Docker path
- operator onboarding
- doctor/backup/restore
- ecosystem integrations
- remote connector adapters behind the same copy-only boundary
- polished demos
- README polish

Load-bearing improvement:

- Relaytic should expose a professional mission-control surface that lets humans and external agents navigate branch history, confidence, traces, interventions, and change attribution while the packaging and integration layer makes that surface survivable for real-world use

Human surface:

- operators should be able to open one coherent mission-control view showing current stage, branch DAG, confidence map, trace timeline, intervention history, recommended next actions, and environment health

Agent surface:

- external agents should be able to query the same mission-control state, branch structure, trace explorer state, and change attribution through stable JSON-first surfaces and MCP tools

Intelligence source:

- canonical runtime events, artifact graph, benchmark outcomes, feedback/outcome memory, and later ecosystem exports

Fallback rule:

- if richer UI or ecosystem integrations are unavailable, Relaytic must still expose the same mission-control truth through CLI, MCP, and artifact files without degrading inspectability

Required outputs:
- `mission_control_state.json`
- `branch_dag.json`
- `confidence_map.json`
- `change_attribution_report.json`
- `review_queue_state.json`
- `trace_explorer_state.json`
- `branch_replay_index.json`
- `approval_timeline.json`
- `background_job_view.json`
- `permission_mode_card.json`
- `release_health_report.json`
- one golden demo
- one Focus Council demo
- one completion/status demo
- one feedback-learning demo
- one benchmark-parity demo
- one dojo demo

Required behavior:

- Slice 15 must consume the canonical trace model from Slice 12B rather than inventing a separate UI-only activity history
- Slice 15 must build on the mission-control MVP from Slices 11B through 11G rather than replacing it with a separate UI stack
- Slice 15 must consume release-safety posture from Slice 13A so packaging and demo readiness are visible from the same operator surface
- Slice 15 must consume the event bus and explicit permission modes from Slice 13B rather than presenting stale or UI-only authority state
- Slice 15 must consume background-job and resume state from Slice 13C so long-running work is visible and controllable from the same mission-control truth
- Slice 15 must consume remote-approval and supervision-handoff state from Slice 14A instead of building a separate remote-only dashboard model
- mission control must make branch, tool, intervention, and confidence state legible without requiring humans or external agents to read raw artifact trees
- mission control must make current permission mode, active background jobs, pending approvals, remote-supervision posture, and release-health posture legible from the same top-level surface
- CLI, MCP, and any richer UI shell must expose the same mission-control truth with only presentation differences
- the packaged demos must include at least one skeptical-control case, one incumbent challenge case, and one trace-backed branch comparison

Minimum proof:

- one mission-control view that replays why Relaytic changed course across at least two branches
- one agent-consumable mission-control export that shows current stage, branch state, and recommended next action without missing trace context
- one packaged demo where humans can see what changed because of memory, research, feedback, and intervention handling from the same surface
- one accelerated execution demo
- one mission-control view that shows active background jobs, current permission mode, and pending approvals without drifting from CLI or MCP truth
- one release-health view that shows whether the current build or demo pack is safe to hand out publicly

Required behavior:

- polish must not erase inspectability or the specialist architecture
- mission control should expose intervention history, accepted/rejected overrides, active review queue items, causal-memory highlights, and incumbent-versus-Relaytic comparison state rather than only stage and branch cosmetics
- demos must prove substance, not only CLI cosmetics
- mission control must explain what changed because of memory, semantic intelligence, research, feedback, outcomes, and autonomous loops instead of flattening everything into one opaque story
- onboarding, backup, restore, doctor, and integrations should make Relaytic survivable for real operator use
- optional ecosystem exports should be made operable here only after their upstream slices are proven, especially registry export, observability export, and later feature-serving alignment
- remote connector adapters must never become direct modeling surfaces; they must materialize bounded immutable run-local snapshots before Relaytic touches the data
- remote connector adapters must stay read-only against the upstream system and must never mutate or write back to the source
- connector examples worth considering here are Kafka-style consumers, object-store Parquet readers, and warehouse query adapters, but all must preserve the local-first audit and copy-only contract

Minimum proof:

- one clean new-user path from install to judged run
- one external-agent path that uses the JSON surfaces only
- one recovery path that proves backup/restore or doctor behavior
- one mission-control path that shows branch structure, confidence, and change attribution for a non-trivial autonomous run
- one remote-source demo where Relaytic reads through a connector, materializes a bounded local snapshot, records explicit provenance, and still avoids persisting original absolute source paths

## Slice 16 - Representation engines, JEPA-style latent world models, and unlabeled local corpora

Goal:
- optional representation-engine slot
- JEPA-style latent predictive modeling
- unlabeled local corpora support
- temporal/entity-state embeddings for retrieval and anomaly support

Load-bearing improvement:

- Relaytic should be able to learn useful latent predictive structure from large unlabeled local data sources, especially streams, event histories, and time-aware entity trajectories, and use those representations to improve retrieval, anomaly/OOD signals, challenger design, and data-acquisition reasoning

Human surface:

- humans should be able to inspect when a representation engine was used, what corpora it was trained on, what downstream gains it provided, and where it was intentionally not trusted

Agent surface:

- external agents should be able to consume representation-engine profiles, latent-state summaries, and embedding-derived evidence through stable artifacts without treating them as hidden truth

Intelligence source:

- self-supervised latent predictive learning over local unlabeled data, with JEPA-family methods as one likely backend family

Fallback rule:

- if no representation engine is configured or validated, Relaytic must continue using deterministic features, current memory, current search, and current benchmark logic without behavioral drift

Required outputs:
- `representation_engine_profile.json`
- `latent_state_report.json`
- `embedding_index_report.json`
- `representation_transfer_report.json`
- `representation_ood_report.json`
- `jepa_pretraining_report.json`

Required behavior:

- representation learning must remain optional and must never become the authority path for metrics, calibration, budgets, stop rules, or lifecycle mechanics
- representation engines must be local-first and operate on staged or explicitly permitted local corpora, never on hidden remote data by default
- JEPA-style engines should be evaluated first where they are most plausible: time-aware structured data, event streams, entity histories, anomaly precursors, and analog retrieval
- representation-derived improvements must be benchmarked separately from the deterministic floor and from semantic-intelligence gains
- learned embeddings may influence retrieval, anomaly detection, challenger templates, or data-acquisition suggestions, but they must do so through explicit artifacts and ablations

First implementation moves:

1. Add an explicit `representation engine slot` with a no-engine deterministic fallback.
2. Add one bounded local latent-state adapter path for time-aware or event-history data.
3. Use learned representations first for analog retrieval, anomaly/OOD support, and challenger priors rather than for opaque end-to-end replacement of the Builder path.
4. Add benchmark strata that compare deterministic Relaytic against representation-augmented Relaytic on the same data contract.
5. Keep all representation influence visible in summary, mission-control, and benchmark artifacts.

Minimum proof:

- one case where representation-augmented retrieval materially improves analog relevance or challenger design
- one case where a latent predictive model improves anomaly or OOD support on a time-aware dataset
- one case where JEPA-style pretraining does not help and Relaytic reports that honestly
- one benchmark report separating deterministic-floor, representation-augmented, local-LLM, and bounded-loop modes

Innovation hook:

- this is the long-range slice where Relaytic can start absorbing frontier self-supervised world-model ideas without abandoning its deterministic judgment core

## First four slices to build before anything fancy

If you want the highest chance of success, only do these first:
- Slice 01
- Slice 02
- Slice 03
- Slice 04

Then stop, test, and review.

