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
- **decision-lab path**
  once Slice 10A lands, one case where Relaytic chooses between more search, more data, recalibration, retraining, abstention, or operator review because it modeled the downstream decision environment explicitly
- **method-compiler path**
  once Slice 10A lands, one case where research, memory, or operator notes compile into an executable challenger, feature, split, or benchmark template rather than only a report
- **mission-control path**
  once Slice 15 lands, one case where a human or external agent can see branch structure, confidence, and change attribution without reading the entire artifact tree

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
10. Slice 11
11. Slice 10
12. Slice 10A
13. Slice 12
14. Slice 13
15. Slice 14
16. Slice 15
17. Slice 16

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
- Slice 11 gives honest proof before feedback or dojo behavior expands too far
- Slice 10 becomes safer after memory and benchmark doctrine exist
- Slice 10A is the category-shift slice that turns Relaytic from a governed model/evaluation engine into a decision-and-discovery engine with compiled methods and data-acquisition reasoning
- Slice 16 is the optional late-stage representation-engine slice where Relaytic can evaluate JEPA-style latent predictive models for large unlabeled local corpora, event histories, and streams without promoting them into the authority path prematurely

## Current execution state

- implemented baseline: Slice 00 through Slice 11
- next execution target: Slice 10
- next proof follow-on after Slice 10: Slice 10A
- next adaptive follow-on after Slice 10A: Slice 12
- late optional representation follow-on after Slice 15: Slice 16

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

## Slice 10A - Decision lab, method compiler, and data-acquisition reasoning

Goal:
- decision-system world modeling
- method compilation
- data-fabric reasoning
- value-of-more-data and value-of-more-search judgment

Load-bearing improvement:

- Relaytic should stop behaving like a system that only asks "which model wins?" and start behaving like a system that can ask "which action policy, which additional data, and which next experiment most improves the real downstream decision?"

Human surface:

- humans should be able to inspect the assumed decision regime, action costs, defer/review options, data-acquisition suggestions, and compiled method-transfer ideas behind Relaytic's next-step judgment

Agent surface:

- external agents should be able to consume a machine-readable decision world model, compiled challenger templates, compiled feature/data hypotheses, and value-of-more-data reasoning without parsing prose

Intelligence source:

- current artifacts, benchmark results, validated feedback, run memory, privacy-safe research retrieval, runtime evidence, and bounded semantic synthesis

Fallback rule:

- if action economics, nearby sources, or method references are missing, Relaytic should emit a provisional world model with explicit uncertainty and fall back to current benchmark/memory/planning behavior rather than inventing hidden certainty

Required outputs:
- `decision_world_model.json`
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
5. Wire compiled outputs into planning, autonomy, lifecycle, assist, and benchmark surfaces.

Minimum proof:

- one case where modeled action economics changes threshold, abstention, review, or next-step judgment
- one case where compiled research or memory changes challenger or feature design through an explicit executable template
- one case where Relaytic recommends additional local data or a join candidate instead of wider search on the current snapshot
- one case where Relaytic records uncertainty because the downstream decision environment is under-specified

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

## Slice 12 - Dojo mode and guarded self-improvement

Goal:
- explicit dojo mode
- quarantined improvements
- method self-improvement
- experimental architecture proposals

Load-bearing improvement:

- Relaytic should improve not only route priors but also decision-world-model heuristics, method-compiler behavior, search-control policy, and data-acquisition reasoning under hard validation gates

Human surface:

- humans should be able to see which proposed self-improvements target route search, decision usefulness, data acquisition, or method compilation and why they were promoted or rejected

Agent surface:

- external agents should be able to consume dojo proposals, validation outcomes, and promotion/rollback state as explicit artifacts

Intelligence source:

- benchmark gaps, validated feedback, outcome evidence, prior failure cases, gold decision cases, and quarantined experimental proposals

Fallback rule:

- if dojo validation data or benchmark proof is unavailable, the current incumbent behavior remains authoritative and dojo outputs stay quarantined

Required outputs:
- `dojo_session.json`
- `dojo_hypotheses.json`
- `dojo_results.json`
- `dojo_promotions.json`
- `architecture_proposals.json`

Required behavior:
- dojo outputs must remain quarantined until they beat the incumbent on benchmark and golden-case validation
- no dojo promotion may become default behavior without an explicit promotion artifact
- dojo must improve strategies, priors, challenger design, route search, decision-world-model heuristics, and method-compilation logic before it is allowed to touch deeper architecture proposals
- every dojo promotion must preserve rollback, provenance, and benchmark comparability

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

Innovation hook:

- Relaytic should self-improve like a lab, not mutate like an unstable agent demo

## Slice 13 - Search controller, accelerated execution, and distributed local experimentation

Goal:
- search-controller policy
- execution-profile detection
- device-aware planning
- CPU/GPU/local-cluster profile choice
- checkpointable distributed-plan baseline

Load-bearing improvement:

- Relaytic should be able to run wider challenger fields, deeper HPO, calibration branches, and uncertainty/abstention experiments under one explicit search controller instead of only static narrow search choices

Human surface:

- humans should be able to inspect why Relaytic widened or pruned search, which device profile it chose, and which branches were considered too expensive or too low value

Agent surface:

- external agents should be able to consume one search-controller plan, execution strategy, checkpoint state, and scheduler map without inferring hidden orchestration decisions

Intelligence source:

- budget-aware search policy, benchmark gaps, completion/autonomy value signals, hardware detection, and optional distributed execution adapters

Fallback rule:

- when acceleration or distributed execution is unavailable, Relaytic must still run the same search logic in a narrower local profile rather than changing the source of truth or losing replayability

Required outputs:
- `search_controller_plan.json`
- `portfolio_search_trace.json`
- `execution_backend_profile.json`
- `device_allocation.json`
- `distributed_run_plan.json`
- `scheduler_job_map.json`
- `checkpoint_state.json`
- `execution_strategy_report.json`

Required behavior:

- execution acceleration must preserve provenance, checkpointing, and replayability
- device-aware planning must change *how* Relaytic executes, not silently change *what* it believes
- distributed execution must remain resumable and safe for long local runs
- search expansion must remain budgeted and justified by expected decision value, not only by abstract score-chasing
- the search controller must be able to prune low-value branches early and widen high-value branches explicitly
- broader route families, calibration variants, uncertainty wraps, and abstention policies should be eligible branches where their value is justified

Minimum proof:

- one same-plan run that succeeds across two execution profiles
- one interrupted distributed run that resumes from checkpoint
- one agent-consumable execution strategy report
- one case where the search controller rejects a low-value branch and expands a higher-value branch with explicit justification

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

Required behavior:

- physical, regulatory, and operational constraints must be explicit inputs to proposal generation, not cosmetic warnings after the fact
- Relaytic must distinguish "promising", "unproven", "physically implausible", "operationally infeasible", and "policy-constrained" proposals
- action-boundary reasoning must integrate with abstention, review, rollback, and data-acquisition suggestions rather than living in a separate report

Minimum proof:

- one domain case where physically implausible proposals are suppressed
- one case where feasibility constraints materially alter route or recommendation output
- one case where operational or compliance constraints alter the decision policy or recommended next action

## Slice 15 - Mission control, packaging, integrations, demos, polish

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

- Relaytic should expose a professional mission-control surface that lets humans and external agents navigate branch history, confidence, and change attribution while the packaging and integration layer makes that surface survivable for real-world use

Human surface:

- operators should be able to open one coherent mission-control view showing current stage, branch DAG, confidence map, change attribution, recommended next actions, and environment health

Agent surface:

- external agents should be able to query the same mission-control state, branch structure, and change attribution through stable JSON-first surfaces and MCP tools

Intelligence source:

- canonical runtime events, artifact graph, benchmark outcomes, feedback/outcome memory, and later ecosystem exports

Fallback rule:

- if richer UI or ecosystem integrations are unavailable, Relaytic must still expose the same mission-control truth through CLI, MCP, and artifact files without degrading inspectability

Required outputs:
- `mission_control_state.json`
- `branch_dag.json`
- `confidence_map.json`
- `change_attribution_report.json`
- one golden demo
- one Focus Council demo
- one completion/status demo
- one feedback-learning demo
- one benchmark-parity demo
- one dojo demo
- one accelerated execution demo

Required behavior:

- polish must not erase inspectability or the specialist architecture
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

