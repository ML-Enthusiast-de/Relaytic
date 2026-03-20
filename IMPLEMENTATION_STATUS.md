# Implementation Status

This document tracks the operational state of the repository. It is an implementation control file, not product marketing copy.

## Current Baseline

- completed slices: 00 through 09B
- next recommended slice: 09, structured semantic tasks, document grounding, and bounded intelligence amplification
- next high-leverage frontier follow-on: 09, structured semantic tasks, doc grounding, and semantically grounded expert deliberation
- next bounded-autonomy follow-on after 09: 09C, executable retraining/recalibration loops and challenger portfolio expansion
- current public package: `relaytic`
- current public CLI: `relaytic`

## Operational Capabilities

The repository currently supports:

- policy resolution and manifest writing
- mandate and context foundation artifacts
- free-form intake translation with provenance and semantic mapping
- autonomous proceed-with-assumptions behavior for non-critical intake ambiguity
- investigation artifacts from Scout, Scientist, and Focus Council
- Strategist planning artifacts with a real Builder handoff
- a first deterministic local data-to-model route via `relaytic plan run`
- a first human-friendly and agent-friendly MVP shell via `relaytic run`, `relaytic show`, `relaytic predict`, and `relaytic evidence`
- persisted `run_summary.json` plus `reports/summary.md` for concise run understanding
- challenger, ablation, audit, leaderboard, and decision-memo evidence around the first Builder route
- completion-governor judgment that fuses mandate, context, intake, investigation, planning, and evidence into a machine-actionable next step
- visible run-state and blocking-layer artifacts via `relaytic status` and `relaytic completion review`
- lifecycle-governor judgment that distinguishes keep, recalibrate, retrain, promote, and rollback actions from the same run surface
- run memory and analog retrieval with provenance-bearing analog candidates, route priors, challenger priors, reflection memory, and pre-close memory flush artifacts
- visible memory support inside planning, challenger design, completion review, lifecycle review, `relaytic run`, `relaytic show`, and explicit `relaytic memory` surfaces
- a shared local runtime gateway with append-only events, checkpoints, capability-scoped specialists, hook audit, and one coherent control path for CLI and MCP
- one-line bootstrap via `python scripts/install_relaytic.py` plus install-health verification via `relaytic doctor`
- host-neutral MCP interoperability via `relaytic interoperability serve-mcp` plus checked-in Claude, Codex/OpenAI, OpenClaw, and ChatGPT-facing wrapper surfaces
- machine-readable host activation/discovery state so Relaytic can say which hosts can call it immediately and which still require connector registration
- optional local-LLM advisory support without making local LLMs a hard requirement
- optional frontier-model use remains in-plan as a policy-gated amplifier rather than a baseline dependency
- deterministic expert-prior inference that converts task/domain evidence into archetype-aware metric, route, feature, and risk priors
- optional integration inventory via `relaytic integrations show` so humans and external agents can discover mature OSS capabilities without smearing them into the core contract
- wired integration adapters for Pandera intake validation, statsmodels residual diagnostics, imbalanced-learn rare-event challengers, and PyOD anomaly challengers with a default Windows runtime guard for the current unstable PyOD stack
- adapter compatibility self-checks via `relaytic integrations self-check` so upgrades can be verified without guessing
- current task-family support across the main path for regression, binary classification, multiclass classification, and fraud/anomaly-style rare-event detection
- public-dataset end-to-end regression, binary-classification, and multiclass-classification coverage using stable bundled open datasets in the test suite
- optional official-UCI domain-dataset coverage for concrete strength, telecom churn, credit default, and predictive maintenance through an explicit opt-in network-backed test suite

## Implemented Slices

### Slice 00

- locked public naming on `Relaytic`, `relaytic`, and `relaytic`
- established security, migration, and implementation control documents
- introduced the temporary `corr2surrogate` compatibility boundary

### Slice 01

- added manifest helpers under `src/relaytic/artifacts/`
- added canonical policy loading and resolved-policy writing under `src/relaytic/policies/`
- added `relaytic manifest init`
- added `relaytic policy resolve`
- added targeted scaffold and CLI tests

### Slice 02

- added stable mandate models and writers under `src/relaytic/mandate/`
- added stable context models and writers under `src/relaytic/context/`
- added `relaytic mandate init` and `relaytic mandate show`
- added `relaytic context init` and `relaytic context show`
- added `relaytic foundation init`
- added targeted foundation and CLI tests

### Slice 03

- added `src/relaytic/investigation/` with typed investigation artifacts and storage helpers
- implemented Scout for dataset profiling
- implemented Scientist for grounded domain and objective hypotheses
- implemented Focus Council for early objective resolution
- added deterministic expert-prior reasoning so Scientist and Focus Council can carry archetype-aware knowledge without requiring an LLM
- added `relaytic investigate`
- added targeted investigation, CLI, and local-stub-LLM tests

### Slice 04

- added `src/relaytic/intake/` with typed intake artifacts and storage helpers
- implemented `StewardAgent` for mandate, work-preference, and run-brief translation
- implemented `ContextInterpreterAgent` for data-origin, domain, and task translation
- added task-type and domain-archetype hint extraction from free-form intake so later specialists can receive stronger structured intent
- upgraded intake so explicit targets can resolve task-type hints from dataset evidence instead of relying only on generic language cues
- added `relaytic intake interpret`
- added `relaytic intake show`
- added `relaytic intake questions`
- added `autonomy_mode.json`, `clarification_queue.json`, and `assumption_log.json`
- made intake clarification optional by default and auditable through explicit assumptions
- added targeted intake, CLI, and local-stub-LLM tests

### Slice 05

- added `src/relaytic/planning/` with typed planning artifacts, storage helpers, and optional local advisory
- implemented `StrategistAgent` to turn investigation outputs into a concrete Builder handoff
- added `plan.json`, `alternatives.json`, `hypotheses.json`, `experiment_priority_report.json`, and `marginal_value_of_next_experiment.json`
- added `relaytic plan create`, `relaytic plan run`, and `relaytic plan show`
- connected the first deterministic Builder execution route into the same Relaytic run directory
- made planning robust against over-aggressive heuristic exclusions by distinguishing hard guardrails from soft feature-risk signals
- added targeted planning, CLI, end-to-end inference, and local-stub-LLM tests

### Slice 05A

- added `src/relaytic/runs/` for MVP-access summaries and human-readable run reports
- added `relaytic run` as a one-shot intake -> investigate -> plan -> execute surface
- added `relaytic show` to materialize and render concise run summaries
- added `relaytic predict` as the accessible inference surface for built runs
- added `run_summary.json` and `reports/summary.md`
- standardized nested manifest artifact paths to POSIX-style relative paths for easier agent consumption
- added targeted MVP-access CLI tests

### Slice 06

- added `src/relaytic/evidence/` with typed challenger, ablation, audit, and belief-update artifacts plus storage helpers
- implemented a bounded challenger branch against the selected Builder route
- implemented bounded feature-drop ablations against the selected champion family
- implemented a provisional audit pass that combines challenger evidence, ablation evidence, and inference diagnostics
- added `experiment_registry.json`, `challenger_report.json`, `ablation_report.json`, `audit_report.json`, `belief_update.json`, `leaderboard.csv`, `reports/technical_report.md`, and `reports/decision_memo.md`
- added `relaytic evidence run` and `relaytic evidence show`
- upgraded `relaytic run` so the MVP flow now includes Slice 06 evidence pressure by default
- extended `run_summary.json` and `reports/summary.md` so humans and agents can see the provisional recommendation and evidence posture
- added targeted Slice 06 agent, CLI, and local-stub-LLM tests

### Slice 07

- added `src/relaytic/completion/` with typed completion-governor artifacts, storage helpers, and optional local advisory
- implemented a state tracker that records visible workflow stage and stage timeline
- implemented a mandate review layer that checks target alignment and constraint conflicts against the executed route
- implemented a completion governor that emits a stable action vocabulary, blocking-layer diagnosis, and machine-actionable next-action queue
- added `completion_decision.json`, `run_state.json`, `stage_timeline.json`, `mandate_evidence_review.json`, `blocking_analysis.json`, and `next_action_queue.json`
- added `relaytic status` and `relaytic completion review`
- upgraded `relaytic run` and `relaytic show` so the MVP flow now ends in an explicit governed state rather than a provisional evidence memo only
- tightened `--overwrite` behavior so reruns refresh targeted investigation, planning, evidence, and completion artifacts instead of mixing stale upstream state into later governed outputs
- added targeted Slice 07 agent, CLI, local-stub-LLM, and end-to-end tests

### Slice 08

- added `src/relaytic/lifecycle/` with typed lifecycle artifacts, storage helpers, and deterministic lifecycle review logic
- implemented champion-vs-candidate comparison that fuses evidence, completion state, and fresh-data behavior
- implemented distinct recalibration, retraining, promotion, and rollback decisions with machine-readable reason codes
- added `champion_vs_candidate.json`, `recalibration_decision.json`, `retrain_decision.json`, `promotion_decision.json`, and `rollback_decision.json`
- added `relaytic lifecycle review` and `relaytic lifecycle show`
- upgraded `relaytic run` and `relaytic show` so the MVP flow now includes lifecycle review by default
- extended `run_summary.json` and `reports/summary.md` so humans and agents can see lifecycle posture in the same surface
- added targeted Slice 08 agent, CLI, doctor, bootstrap, and public-dataset end-to-end tests

### Slice 08A

- added `src/relaytic/interoperability/` with a Relaytic-owned MCP server boundary, host-bundle generation, and interoperability self-checks
- implemented a host-neutral MCP tool contract over the current Relaytic MVP and phase-level surfaces
- added `relaytic interoperability show`, `relaytic interoperability self-check`, `relaytic interoperability export`, and `relaytic interoperability serve-mcp`
- added checked-in `.mcp.json`, `.claude/agents/relaytic.md`, `.agents/skills/relaytic/SKILL.md`, `openclaw/skills/relaytic/SKILL.md`, and `connectors/chatgpt/README.md`
- added transport-safe compact health tooling and live stdio/streamable HTTP smoke coverage
- added public-dataset end-to-end MCP coverage so Relaytic can be exercised through the interoperability surface rather than CLI only

### Slice 08B

- expanded host-bundle metadata with explicit discovery mode, activation requirements, HTTPS requirements, and next-step guidance
- added workspace-level `skills/relaytic/SKILL.md` so OpenClaw-style workspace discovery can work directly from this repository
- upgraded `relaytic interoperability show` so humans and agents can see which hosts are callable now versus which still need registration or approval
- tightened ChatGPT connector guidance so repository-local files are not mistaken for automatic ChatGPT availability

### Slice 09A

- added `src/relaytic/memory/` with typed memory controls, analog retrieval artifacts, provenance-bearing scoring, reflection writeback, and storage helpers
- added `relaytic memory retrieve` and `relaytic memory show`
- added `memory_retrieval.json`, `analog_run_candidates.json`, `route_prior_context.json`, `challenger_prior_suggestions.json`, `reflection_memory.json`, and `memory_flush_report.json`
- upgraded planning so analog priors can change candidate-family order with a visible counterfactual instead of silently mutating the route
- upgraded challenger selection so memory can bias challenger family choice when prior evidence supports it
- upgraded completion and lifecycle review so memory support is diagnosed explicitly and retrieved analogs become visible to both humans and external agents
- upgraded `relaytic run` and `relaytic show` so the MVP shell materializes memory artifacts automatically and surfaces the resulting memory delta in `run_summary.json`
- added targeted Slice 09A agent, CLI, and public-dataset end-to-end tests

### Slice 09B

- added `src/relaytic/runtime/` with typed runtime controls, capability profiles, append-only event storage, hook audit, checkpoint manifests, and context-influence persistence
- added `relaytic runtime show` and `relaytic runtime events`
- added `lab_event_stream.jsonl`, `hook_execution_log.json`, `run_checkpoint_manifest.json`, `capability_profiles.json`, `data_access_audit.json`, and `context_influence_report.json`
- upgraded intake, investigation, planning, evidence, memory, completion, and lifecycle orchestration so stage transitions flow through one shared local runtime instead of loose per-surface glue
- upgraded `relaytic show`, `run_summary.json`, and the MCP layer so humans and external agents can inspect runtime posture, event counts, denied accesses, and hook behavior directly
- added targeted Slice 09B runtime, CLI, MCP, and public-dataset end-to-end tests

### Cross-Cutting Hardening

- added `src/relaytic/integrations/` as the canonical optional-library discovery boundary
- added `relaytic integrations show` for human and agent visibility into mature OSS capabilities
- added `relaytic integrations self-check` so wired adapters can be compatibility-checked after package changes
- wired Pandera into intake validation, statsmodels into evidence audit diagnostics, imbalanced-learn into rare-event challenger execution, and PyOD into anomaly challenger execution
- added `relaytic doctor` as the canonical runtime/install-health surface and a one-line bootstrap script at `scripts/install_relaytic.py`
- adopted bundled public datasets for stable end-to-end regression, binary-classification, and multiclass-classification tests without introducing network-bound CI behavior
- added an opt-in official-UCI domain-dataset suite so Relaytic can be exercised on domain-specific public data without making default CI depend on live network fetches
- sharpened `RELAYTIC_SLICING_PLAN.md` into a stricter future-slice execution contract with explicit intelligence sources, proof obligations, fallbacks, and a preferred post-MVP execution order
- folded explicit optional SOTA routine tracks into the slicing plan so future lifecycle, memory, benchmark, and polish slices know where MAPIE, Evidently, MLflow, OpenTelemetry, OpenLineage, FLAML, and later Feast fit
- sharpened the future architecture doctrine so upcoming slices are now expected to deliver disk-first artifact memory, rowless-by-default semantic work, capability-scoped specialists, deterministic hook points, and a local lab runtime rather than looser pipeline-style orchestration

## Compatibility Boundary

The remaining compatibility surface is intentionally narrow:

- `src/corr2surrogate/__init__.py` forwards legacy imports
- legacy `C2S_*` environment variable fallbacks may still be accepted where required

New code and docs must target `relaytic` and `RELAYTIC_*`.

## Known Gaps

The repository is not yet at the final product state. The main remaining gaps are:

- the current challenger layer is real but still narrow; it does not yet prove broad challenger science
- completion and lifecycle now emit good next steps, but they still mostly stop at judgment rather than executing a bounded second pass automatically
- run memory is now real, but long-horizon feedback learning and richer analog indexing are still pending
- benchmark-separated proof of strength under constrained/operator-heavy settings is still pending
- the bounded semantic-task and document-grounding layer is still pending, so runtime capability control is ahead of runtime semantic intelligence
- internal specialist discussion is still more deterministic artifact fusion than semantically strong counterposition, verification, and contradiction handling

## Immediate Next Work

Slice 09 should land:

- one canonical semantic-task contract for bounded intelligence work
- capability-aware context assembly and document grounding
- explicit backend discovery, health, and escalation artifacts
- rowless-by-default semantic assistance that integrates cleanly with the runtime gateway
- semantically grounded proposer/counterposition/verifier microflows for difficult judgments
- explicit semantic uncertainty and counterposition artifacts so challenger and retrain reasoning become sharper rather than just better worded

After Slice 09, the next high-leverage frontier follow-ons should include:

- Slice 09 intelligence amplification and bounded semantic-task infrastructure
- Slice 09C autonomous second-pass execution, challenger portfolio expansion, and executable lifecycle loops
- Slice 11 benchmark-separated proof under constrained settings
