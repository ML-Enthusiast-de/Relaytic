# RELAYTIC_TRANSFORMATION_PLAN_COMPLETE.md

# Relaytic Transformation Plan

## Branding and naming

### Product brand
**Relaytic**

### Product descriptor
**The Relay Inference Lab**

### Positioning line
**Relaytic is a local-first inference engineering system for structured data, built around specialist agents that investigate data, form competing hypotheses, run challenger science, preserve mandate-aware user intent, optionally ground themselves in expert context, optionally perform privacy-safe external method and benchmark retrieval from redacted run signatures, amplify their judgment when a powerful LLM is available, optionally use a minimum local LLM baseline when users want semantic help on-device, actively help users and external agents set up local LLMs when desired, debate what the run should optimize for, keep core subsystems replaceable, carry bounded evidence between specialists, and expose their judgment as reusable tools.**

### Naming strategy
Use a two-layer naming system throughout the repository and docs:

- **Brand:** Relaytic
- **Descriptor:** The Relay Inference Lab

### Documentation rule
All top-level docs should present the project as:

> **Relaytic — The Relay Inference Lab**

---

## Goal

Transform this repository from a “data -> surrogate model” framework into a **local-first inference engineering system** for structured data that:

- runs fully locally by default
- treats “local” broadly: personal computer, workstation, local server, local instance, or local cluster under the user’s control
- can be steered when the user wants control
- can act autonomously when the user prefers delegation
- treats every meaningful human or external-agent steering action as an inspectable intervention request that can be challenged, accepted, modified, deferred, rejected, checkpointed, and remembered rather than blindly obeyed
- can run as a bounded session or as an explicit long-running daemon/service when the user wants continuous operation
- can optionally run a bounded periodic lab pulse that inspects local state, watches for relevant innovations or stale evidence, and queues safe follow-up without silently changing core behavior
- uses a coordinated team of specialist agents rather than a single planner
- investigates unknown datasets before committing to modeling assumptions
- supports multiple modeling routes, not just one narrow pipeline
- can recommend additional data collection opportunities regardless of domain
- optimizes for robust inference, not merely leaderboard score
- preserves long-term lab values, work preferences, and run-specific intent through a mandate layer
- lets specialists disagree with the mandate when they find materially better ideas, while still obeying binding constraints
- can optionally use user-provided context, uploaded documents, and policy-gated external knowledge retrieval
- can optionally retrieve papers, benchmark references, and method writeups from the web using rowless, redacted, generalized run signatures rather than private data
- still works when no expert context is provided
- uses a deterministic expert-prior substrate so specialists can reason about common business and data archetypes before any LLM help is available
- can optionally exploit strong local or frontier LLMs for deeper interpretation, hypothesis generation, challenger design, and synthesis without making LLMs a hard dependency
- can optionally use a small quantized local LLM baseline for dataset-label understanding, note interpretation, and conversational UX on personal computers
- can detect stronger available local LLM capacity and suggest better intelligence modes when it would materially improve insight
- can actively guide users and external agents through local-LLM setup when they want semantic help but no configured local model is available
- supports macOS and Linux as first-class platforms, including Apple Silicon-aware defaults
- automatically inspects available local hardware and sets safe default budgets when the user provides no explicit limits
- supports new data arrival, regular retraining, champion/challenger management, recalibration, and rollback
- versions datasets, features, models, policies, mandates, and reports
- produces reproducible artifacts, reports, traces, and deployable outputs
- produces differentiated post-run reports for humans and external agents from the same canonical run truth
- learns from prior runs and uses memory to improve future planning
- preserves durable, resettable local learnings so the next run can inherit validated lessons without silently drifting
- preserves more than analog memory: intervention memory, outcome memory, method memory, and causal links between assumptions, actions, and later results
- exposes itself as a reusable tool surface for other agents
- remains deterministic, testable, auditable, and policy-governed
- treats external tools and systems pragmatically: use what is best for each purpose, integrate strong existing systems where useful, and keep challenging every apparent winner for a better outcome
- includes a focus-selection layer that debates whether a run should prioritize accuracy, business value, reliability, efficiency, interpretability, sustainability, or a multi-objective blend
- keeps major subsystems replaceable through explicit engine slots instead of hard-wiring every backend choice
- carries bounded evidence bundles between specialists instead of relying only on implicit shared state
- uses a local lab gateway and append-only event stream so CLI, MCP, UI, and automation share the same run-control truth
- treats on-disk artifacts as canonical truth and any memory index, semantic cache, or retrieval structure as a derived view
- gives each specialist an explicit capability profile instead of ambient full-data, full-tool access
- defaults semantic helpers and optional LLM paths to rowless, redacted, schema-bound context unless policy explicitly grants richer access
- treats external research retrieval the same way: rowless and redacted by default, never a backdoor for raw data leakage
- flushes durable reflection and memory summaries before retries, compaction, and final completion/lifecycle handoff
- includes operator onboarding, health, backup, restore, and diagnostics as first-class product features
- defines trust boundaries for every integration so external systems are useful but never unquestionable
- includes a small structured semantic-task primitive for safe, schema-bound semantic reasoning
- includes an explicit completion-decision layer so agents and operators can tell whether the system should stop, continue, recalibrate, retrain, promote, roll back, or collect more data
- makes current workflow stage visible in the UI and agent/tool surfaces so humans and external agents always know what step Relaytic is at
- can ingest validated user or agent feedback and use it to improve policy, route preferences, feature strategy, and lifecycle heuristics for similar future data
- can accept a user-supplied incumbent model, prediction set, scorecard, or ruleset as the current challenger target and try to beat it honestly under the same contract
- is benchmarked against strong reference datasets and strong standard approaches for each supported route and must reach that level without hardcoding solutions
- includes a guarded dojo mode where Relaytic can self-improve its strategies, search spaces, priors, and even propose new model architectures when strong data and strong reference systems are available
- uses whatever permissible local hardware it can access to execute as fast and efficiently as possible, from CPU laptops to local GPU workstations to local clusters

---

## Frontier sharpness doctrine

Relaytic is not frontier because it contains agents, many artifacts, or optional LLMs.

Relaytic is frontier only if it materially expands what a local inference system can:

- discover about an unfamiliar dataset
- justify with auditable evidence
- improve through challenger pressure
- control under real mandate and policy constraints
- expose as a reusable judgment surface for humans and other agents

The frontier thesis is therefore not "more orchestration."
It is:

- **problem-formulation search**, not just model-family search
- **evidence-pressure loops**, not just single-pass training
- **mandate-aware autonomous judgment**, not just score chasing
- **agent-usable decision surfaces**, not just human-readable reports
- **private world-knowledge import without private-data export**, not just local heuristics or naive web calls
- **validated self-improvement**, not just prompt churn or hidden heuristic drift

Any slice that does not strengthen at least one of those axes is polish, not frontier progress.

## World-class proof doctrine

Relaytic should not call itself world-class because it has many artifacts, many agents, or a polished shell.

The product becomes world-class only when it can repeatedly prove:

- **protocol conformance**
  CLI, MCP, mission control, and later richer UI or host shells must expose the same run truth, next action, trace posture, and adjudication outcome rather than drifting into surface-specific behavior
- **flagship demo proof**
  Relaytic should keep a small set of recruiter-safe and lab-safe flagship demos with explicit scorecards, not just ad hoc walkthroughs
- **human-supervision success**
  a first-time human should be able to start, recover, inspect why Relaytic changed course, and complete a useful run without repo literacy or hidden operator lore

Future slices that add autonomy, new host surfaces, or new operator-facing behavior should strengthen at least one of those proof tracks in addition to their local feature work.

## Anti-mediocrity guardrails

Relaytic must not degrade into:

- **planner theater**
  many agent names but one real decision path
- **artifact theater**
  more JSON without stronger judgment or controllability
- **benchmark theater**
  polished benchmark claims without hard reference comparisons and failure reports
- **LLM theater**
  vague semantic authority replacing deterministic evidence
- **paper theater**
  buzzword-heavy paper retrieval or SOTA name-dropping without redaction audits, method-transfer artifacts, contradiction handling, or local proof
- **UI theater**
  a polished shell over weak model-search and weak challenge loops

If a proposed feature mostly increases surface area without increasing search power, evidence quality, autonomy, operator leverage, or benchmark strength, it should be deprioritized.

## Proof obligations

Every ambitious Relaytic claim should be falsifiable and backed by at least one of:

- a deterministic artifact
- a regression or adversarial test
- a golden-path demo
- a benchmark or reference-comparison protocol
- an explicit failure report plus next-experiment recommendation when Relaytic loses
- for any external-research influence, a redaction audit plus explicit method-transfer or benchmark-reference artifact

By the time the product is mature, Relaytic should be able to show, not just claim, that:

- it can match strong standard baselines on ordinary structured-data tasks
- it can exceed them when mandate, reliability, lifecycle, or operator constraints matter
- it can be driven end to end by either a human or an external agent through stable tool surfaces
- it can explain why it continued, stopped, recalibrated, retrained, promoted, or rolled back
- it improves itself only through validated method changes rather than silent behavior drift

It should also be able to show, not just claim, that:

- CLI, MCP, mission control, and later richer UI shells stay semantically aligned on the same run truth
- at least three flagship demos still pass under current code and policy:
  - unfamiliar dataset to useful governed decision
  - imported incumbent challenge under the same contract
  - skeptical override rejection or unsafe-request defense with replayable trace
- first-contact human onboarding remains usable without repo literacy, including stuck recovery and explanation of why Relaytic took the next step

All major performance claims should always be separated into:

- deterministic floor
- local-LLM-amplified mode
- optional frontier-assisted mode
- dojo-improved mode

This separation is mandatory. Otherwise the repo will drift into confusing or inflated claims.

## Current leverage points

For the repository as it exists today, the next major leverage points are not "more agents" or "more reports."

They are:

- **behavioral contracts** that let humans and external agents steer Relaytic without turning Relaytic into a compliant shell
- **causal multi-layer memory** that preserves interventions, method outcomes, downstream consequences, and why previous guidance proved right or wrong
- a **first-class trace model** that records specialist turns, tool calls, intervention handling, branch expansion, and later decisions as one replayable execution truth rather than scattered logs
- **dynamic controller logic** that can change handoff depth, branch width, reviewer involvement, and challenge pressure based on observed uncertainty, budget, and downstream decision value
- a **decision-system world model** that understands what action follows prediction, what errors cost, which cases should defer to humans, and whether more search is actually worth it
- a **method compiler** that turns papers, benchmark references, memory, and operator notes into executable challenger templates, feature hypotheses, split/evaluation adjustments, and data-collection suggestions
- **imported incumbent challenge tracks** so Relaytic can beat real existing models instead of only generic baselines
- a **richer search controller** that chooses broader challenger ecology, HPO depth, calibration breadth, and abstention policy under explicit budgets rather than fixed narrow search
- **outcome learning**, not just run learning, so Relaytic improves from interventions taken, overrides, downstream results, and false-positive/false-negative consequences
- a **richer long-term memory stack** with episodic, intervention, outcome, and method memory plus explicit retention, compaction, pinning, and replay rules so specialists do not keep relearning the same lesson
- **agent evaluator and security harnesses** that continuously test override skepticism, tool-safety boundaries, branch-controller behavior, and prompt/result injection resistance rather than assuming the runtime is safe because it is local
- a **lab pulse** that can periodically inspect runtime state, benchmark debt, research freshness, and memory health, then queue bounded safe follow-up without unsupervised drift
- a **richer data-understanding fabric** that can reason about nearby sources, join candidates, entity histories, and what additional data would reduce uncertainty most
- a **mission-control surface** that shows branch structure, confidence map, intervention history, incumbent-versus-Relaytic state, what changed because of memory, intelligence, research, or feedback, and what Relaytic would do next
- a **protocol-conformance harness** that proves CLI, MCP, mission control, and later richer UI shells expose the same control truth rather than drifting by surface
- a **flagship demo pack** with explicit scorecards so Relaytic can be judged by repeatable proof cases rather than one-off founder narration
- a **human-supervision evaluation track** that measures first-run success, stuck recovery, explanation quality, and whether operators can tell what Relaytic expects next
- benchmark-separated proof that Relaytic is strongest when evidence, mandate, reliability, lifecycle constraints, and decision usefulness actually matter

These are the places where the project most needs to become stronger if it wants to look like the next big thing rather than a well-structured research product.

One additional long-range opportunity is a **representation engine** for large unlabeled local corpora, event histories, and time-aware streams. JEPA-style latent predictive models are promising here because they could strengthen analog retrieval, anomaly precursors, temporal state understanding, and data-acquisition reasoning without becoming the authority path for metrics, calibration, or lifecycle decisions.

## 1. Product definition

### New product identity
Relaytic becomes:

> A local-first inference engineering system for structured data, where multiple specialist agents independently inspect data, form and challenge hypotheses, run evidence-driven experiments, quantify reliability, recommend additional data, preserve mandate-aware user intent, optionally use grounded expert context, and produce reusable inference systems and artifacts.

### What Relaytic is not
Relaytic is **not**:
- a thin AutoML wrapper
- a generic “chat with your CSV” app
- a model zoo launcher
- a benchmark-only leaderboard generator

Relaytic is:
- an investigator of unknown structured datasets
- a builder of robust inference systems
- a generator of evidence, not just metrics
- a system with a persistent lab mandate, work-style memory, run-specific brief, and lifecycle-aware retraining logic
- a local tool that other agents can call when they need judgment about data, modeling, reliability, missing information, or context-grounded investigation

### Core principles

1. **Local-first always**
   - No remote model or API use unless explicitly enabled.

2. **Steerable autonomy**
   - Support three execution modes:
     - `manual`
     - `guided`
     - `autonomous`

3. **Policy-aware optimization**
   - Optimize not only for score, but also for:
     - privacy
     - latency
     - interpretability
     - robustness
     - uncertainty
     - compute budget
     - memory budget
     - artifact size
     - approval boundaries

4. **Workflow search, not just hyperparameter search**
   - The system should choose:
     - task route
     - split semantics
     - feature strategy
     - model family
     - calibration method
     - uncertainty method
     - abstention/defer policy
     - HPO strategy
     - search budget
     - stopping rule
     - data-collection recommendations

5. **Reproducibility by default**
   - Every decision, experiment, artifact, and result must be persisted.

6. **Specialist disagreement by design**
   - Multiple specialist agents should independently inspect the dataset, propose competing interpretations, challenge each other’s assumptions, and converge only after evidence is collected.
   - Challenger behavior is mandatory.

7. **Evidence over vibes**
   - Every major recommendation must be backed by:
     - experiments
     - ablations
     - uncertainty analysis
     - challenger results
     - explicit rationale

8. **Inference-first**
   - The goal is not merely to train a model.
   - The goal is to produce a robust inference system with clear reliability characteristics, operating boundaries, and failure modes.

9. **Memory and priors**
   - Planning should improve over time through retrieved priors, plan archetypes, remembered failure modes, and remembered mandate patterns.

10. **Optional knowledge grounding**
   - The system should support expert grounding through:
     - deterministic expert priors derived from dataset and context evidence
     - user-supplied domain context
     - uploaded documents
     - prior-run memory
     - optional external literature retrieval
   - When no expert context is provided, the system must still proceed using dataset evidence alone.
   - Every grounded claim must carry provenance.

11. **Portable local intelligence**
   - Relaytic should run well on macOS and Linux personal computers.
   - A minimum local LLM baseline may be offered as an optional on-device semantic helper.
   - The minimum local LLM baseline must remain optional, replaceable, and fully disableable.

12. **Intelligence-seeking behavior**
   - Relaytic should be maximally curious about opportunities to gain more useful intelligence.
   - If it detects that a stronger permissible local model or backend is available, it should suggest the upgrade when the expected benefit is meaningful.
   - These suggestions must remain advisory unless the user explicitly enables automatic switching.

13. **Intelligence amplification**
   - When a strong LLM is available, Relaytic should gain materially more semantic and strategic power.
   - LLMs should improve understanding, critique, planning, synthesis, and lifecycle judgment.
   - Deterministic execution, verification, and artifact generation must remain intact.

14. **Mandate-aware autonomy**
   - Autonomous execution must remain aware of:
     - long-term lab values
     - work-style preferences
     - run-specific intent

15. **Debate with obedience**
   - Agents must obey binding constraints.
   - Agents may challenge soft preferences when evidence suggests materially better alternatives.
   - Final outputs must show what the mandate preferred, what the evidence preferred, and what compromise was selected.

13. **Resource-aware by default**
   - If the user does not supply compute limits, the system must inspect available local hardware and derive conservative default budgets.
   - Plans must adapt to CPU count, RAM, storage pressure, and optional accelerator availability.
   - The default assumption should favor successful completion on personal computers over maximal search depth.

14. **Bounded by default, unbounded by explicit opt-in**
   - Default runs should be bounded and terminate cleanly.
   - Long-running or indefinite operation must be an explicit user choice.
   - Even in long-running mode, the system must checkpoint, summarize, and remain interruptible.

16. **Continuous usefulness**
   - The system must be useful not only for one-off runs but also for:
     - regular retraining
     - new-data evaluation
     - recalibration-only refreshes
     - champion/candidate comparison
     - rollback and promotion
     - feature and schema lifecycle management

17. **Agent interoperability**
   - The system should be usable directly by humans and consumable by other agents as a plugin/tool server.

18. **Showcaseability and operator experience**
   - Every major capability should have:
     - a polished local UI flow
     - a one-command demo path
     - README-first documentation
     - inspectable artifacts

---

18. **Replaceable subsystems**
   - Relaytic should not hard-wire every backend into the core.
   - Major capabilities should be exposed through explicit engine slots with stable contracts.
   - Swapping a backend must not change Relaytic’s judgment layer or artifact contracts.

19. **Bounded evidence handoffs**
   - Specialists should exchange bounded evidence bundles, not unlimited hidden context.
   - Every important handoff should carry:
     - structured summaries
     - selected evidence
     - provenance
     - confidence
     - size limits

20. **Operator-safe by design**
   - Onboarding, health checks, backup, restore, and diagnostics must be first-class features.
   - Relaytic should be easy to install, verify, recover, and move between machines.

21. **Trust boundaries everywhere**
   - Every integrated backend, route, or external result must be treated as challengeable.
   - External systems may be useful, but none are authoritative by default.
   - Relaytic must remain fail-closed for risky integrations and explicit about trust mode.

22. **Structured semantic tasks**
   - Relaytic should include a bounded semantic-task primitive for schema-constrained meaning extraction.
   - This should be the safest reusable way to exploit extra intelligence for small semantic jobs.

23. **Focus-aware optimization**
   - Relaytic must not assume that every task should optimize the same thing.
   - A focus-selection layer must debate whether the run should prioritize:
     - predictive accuracy
     - business value
     - reliability
     - efficiency
     - interpretability
     - sustainability
     - or a multi-objective blend
   - The resolved focus must directly shape metrics, thresholds, HPO depth, challenger strategy, and lifecycle decisions.

24. **Relentless search for the better answer**
   - Relaytic must never assume that the first strong result is the best final answer.
   - It should integrate strong external systems when they are useful, challenge their outputs when needed, and keep searching for a better justified outcome.
   - “Use what is best for each purpose, then challenge it” should be a core Relaytic value.

25. **Focus-shaped feature engineering**
   - The resolved focus profile must shape feature engineering proposals, not only metrics and tuning.
   - Focus should influence:
     - allowed feature families
     - discouraged feature families
     - feature-search aggressiveness
     - feature-selection bias
     - compute budget for feature generation
     - explanation emphasis in reports

26. **LLM-amplified focus reasoning**
   - The Focus Council must work deterministically by default.
   - When stronger intelligence is available, it may use LLM-assisted semantic reasoning to better infer which objectives should dominate.
   - This is especially valuable when domain notes, deployment context, or business stakes are ambiguous.

27. **Explicit completion judgment**
   - Relaytic must not leave “are we done yet?” implicit.
   - It should fuse evidence into an explicit completion decision that states whether the system should:
     - stop
     - continue search
     - collect more data
     - recalibrate
     - retrain
     - promote
     - rollback
     - reject deployment

28. **Visible workflow state**
   - Users and external agents must be able to see which step Relaytic is currently in.
   - Stage visibility must exist in:
     - UI
     - API/tool surfaces
     - logs/traces
     - periodic summaries for long-running mode

29. **Validated feedback assimilation**
   - Relaytic should learn from user feedback and external-agent feedback when that feedback is validated as useful.
   - Feedback must not be ingested blindly.
   - Validated feedback may update policy defaults, route priors, feature strategy priors, benchmark expectations, and lifecycle heuristics for similar future data.

30. **Benchmark parity without hardcoding**
   - For each supported route, Relaytic should be tested against strong general benchmark datasets and strong standard or gold-reference approaches.
   - Relaytic must aim to reach that level through general reasoning, search, and learned priors rather than hardcoding benchmark-specific answers.

31. **Guarded dojo self-improvement**
   - Relaytic may enter a dojo mode where it tries to improve its own strategies when strong data, strong reference models, or benchmark feedback are available.
   - Dojo improvements must remain quarantined until they prove themselves through benchmark and golden-case validation.
   - Self-improvement must update reusable priors and methods, not silently mutate trusted production behavior.

32. **Local-first, hardware-maximal execution**
   - “Local” should include the user’s laptop, workstation, local server, local instance, or local cluster under their control.
   - Relaytic should exploit available permissible hardware aggressively when doing so materially improves speed, breadth, or intelligence.
   - The planner should choose the fastest justified execution profile that remains within policy, trust, and budget boundaries.

33. **Accelerated and distributed awareness**
   - Relaytic should understand CPU, GPU, multi-GPU, and local-cluster execution contexts.
   - Device and scheduler availability should influence route choice, HPO depth, intelligence mode, and benchmark strategy.
   - Distributed execution must remain optional, inspectable, and artifact-rich.

## 2. Scope changes

### Keep and build on
Preserve these strengths:

- local-only runtime policy and explicit remote opt-in
- the current analyst/modeler flow as the seed of a broader agent system
- deterministic training and evaluation
- artifact and report generation
- current CLI surface where practical
- current tests and CI as the baseline quality bar

### Replace or expand

- replace the public two-agent framing with a multi-role specialist system
- make surrogate modeling one route among several
- replace ad hoc experimentation flow with:
  - an investigation phase
  - a mandate phase
  - a hypothesis phase
  - an experiment graph
  - a handoff graph
  - a run memory layer
  - a continuous-operations layer
- upgrade reports into full decision and evidence artifacts
- make uncertainty, calibration, robustness, drift, and abstention first-class outputs
- add independent profile generation, disagreement resolution, and challenger science
- add additional-data recommendation and value-of-information estimation
- add a mandate system with long-term, work-style, and run-specific memory
- add a judgment-oriented interoperability layer
- add learned-prior route selection and frontier backends
- add dataset/version/feature/model lifecycle management
- add retraining, recalibration, promotion, shadowing, and rollback flows

---

## 3. Innovation thesis

Relaytic should stand out because it combines eight ideas that most projects do not combine well:

### 3.1 Specialist disagreement before model search
At least two specialists independently inspect the data and argue about task framing, leakage, split semantics, and missing signal before the main search begins.

### 3.2 Challenger science, not just challenger models
The system must challenge not only the incumbent model, but also:
- the split strategy
- the route
- suspicious features
- temporal assumptions
- low-data robustness
- missingness sensitivity

### 3.3 Additional data planning as a first-class output
The system should say:
- what data is missing
- why it matters
- what collection plan is likely to reduce uncertainty most
- whether more data is better than more search

### 3.4 Memory-guided planning
The system should learn from prior runs by storing:
- dataset fingerprints
- winning plan archetypes
- failure archetypes
- challenger win patterns
- calibration/drift failure patterns

### 3.5 Mandate-aware autonomy
The system should preserve:
- long-term lab philosophy
- work preferences
- run-specific intent
while still allowing specialists to surface better ideas, challenge soft preferences, and show where evidence conflicts with stated preference.

### 3.6 Judgment tools for other agents
Relaytic should expose high-level tools like:
- `investigate_dataset`
- `challenge_incumbent_model`
- `generate_data_collection_plan`
- `produce_decision_memo`

### 3.7 Continuous evidence-driven operations
Relaytic should not stop at “best model found.”
It should decide whether to:
- score only
- recalibrate
- retrain
- shadow-test
- promote
- rollback
when new data arrives.

---


### 3.8 Intelligence-amplified but deterministic
Relaytic should become meaningfully stronger when a powerful LLM is available, especially in:
- dataset interpretation
- expert-context interpretation
- hypothesis generation
- challenger design
- final synthesis
- lifecycle judgment

But the system must still execute, verify, and enforce constraints deterministically.



## 3A. Ecosystem integration philosophy

Relaytic should not try to replace every strong system in the ecosystem.

Instead, Relaytic should:

- use strong external systems where they are best-in-class for a specific purpose
- integrate them as routes, backends, registries, or supporting infrastructure
- challenge their outputs through Relaytic’s own specialist process
- keep final judgment inside Relaytic’s evidence, mandate, lifecycle, and challenger framework

### Core philosophy

Relaytic does not assume that one system should own everything.

It should:
- use strong model-search systems as candidate generators when useful
- use strong registry/tracing systems as systems of record when useful
- use strong local-LLM serving systems when useful
- still challenge every apparent winner for leakage, fragility, realism, mandate fit, and lifecycle correctness

### Examples of the philosophy

- A strong AutoGluon run may become one candidate route, but Relaytic still challenges whether its winner is realistic and robust.
- A strong MLflow setup may become a registry/tracing backend, but Relaytic still decides whether a model should be promoted, recalibrated, retrained, or rolled back.
- A strong local LLM backend may improve semantic interpretation, but Relaytic still validates actions and keeps deterministic execution in control.

### Required value statement

Relaytic must explicitly adopt this value in docs and product copy:

> Use what is best for each purpose, then challenge it for a better outcome.

---



## 3A.1 Engine slots and replaceable subsystems

Relaytic should make backend choice explicit through **engine slots**.

This turns the value “use what is best for each purpose” into architecture.

### Core engine slots

Relaytic should define explicit slots for:

- **focus engine slot**
- **context engine slot**
- **memory engine slot**
- **representation engine slot**
- **candidate-generation slot**
- **registry backend slot**
- **intelligence backend slot**
- **lifecycle policy slot**
- **semantic-task engine slot**
- **document-grounding slot**
- **research retrieval slot**
- **hook policy slot**
- **capability policy slot**

### Rules for engine slots

- Each slot must have a stable contract.
- The slot interface must be narrower than the backend itself.
- Backends can be swapped without rewriting Relaytic’s judgment layer.
- Slot outputs must remain compatible with artifact contracts and handoff rules.
- One active backend should be resolved per slot at runtime.
- Hidden auto-loaded plugins are out of contract.

### Why this matters

Relaytic should remain:
- backend-agnostic where it is wise
- judgment-owning where it matters
- adaptable without turning into plugin chaos

### Required artifacts

- `engine_slots.json`
- `backend_capabilities.json`
- `slot_resolution.json`

---

## 3A.2 Local lab gateway, event stream, and hook bus

Relaytic should not coordinate long runs only through loose CLI glue and scattered function calls.

It should gain a **local lab gateway** that acts as the control plane for:

- run-state transitions
- append-only event emission
- hook dispatch
- checkpointing
- MCP, CLI, and later UI coherence

### Required gateway rules

- local-first by default
- no public exposure by default
- append-only machine-readable event stream
- idempotent handling for side-effecting run transitions where practical
- deterministic fallback when hooks are absent or rejected
- explicit policy around read-only vs write-capable hooks

### Required artifacts

- `lab_event_stream.jsonl`
- `hook_execution_log.json`
- `run_checkpoint_manifest.json`

### Why this matters

This is the runtime discipline that turns Relaytic from a pipeline with agent names into a real inference lab.

It also makes memory flush, retry behavior, specialist coordination, and external-agent control much safer.

---

## 3A.3 Capability-scoped specialists and data minimization

Relaytic specialists should not all see the same raw material by default.

Each specialist should have an explicit **capability profile** covering:

- artifact read scope
- artifact write scope
- raw-row access
- semantic-task access
- external-adapter access
- network allowance

### Default rule

Semantic helpers, optional LLM-backed specialists, and external semantic adapters should receive:

- rowless summaries
- bounded evidence bundles
- redacted notes
- schema and diagnostics

unless policy explicitly grants richer access.

### Required artifacts

- `capability_profiles.json`
- `data_access_audit.json`
- `context_influence_report.json`

### Required effect

Relaytic should become both smarter and safer:

- smarter because context assembly becomes deliberate
- safer because every broader access grant is visible and challengeable

---

## 3B. Focus Council and objective selection

Relaytic must include a **Focus Council** that debates what the run should optimize for.

The council should be dynamic rather than a fixed bureaucracy. Only the relevant lenses should activate for a given run.

### Core question

Before major planning and tuning, Relaytic should answer:

> What should matter most for this dataset, this task, this mandate, and this deployment setting?

### Dynamic lens roles

The Focus Council should support lenses such as:

#### Accuracy Lens
Advocates for:
- strongest predictive performance
- deeper HPO where justified
- broader search when likely to pay off

#### Value Lens
Advocates for:
- business value
- asymmetric error costs
- thresholding for actionability
- decision usefulness over abstract score

#### Reliability Lens
Advocates for:
- calibration
- uncertainty quality
- stability
- robustness
- abstention or defer strategies where needed

#### Efficiency Lens
Advocates for:
- lower latency
- lower memory
- lower serving cost
- lower retraining burden
- laptop-friendly and edge-friendly routes

#### Interpretability Lens
Advocates for:
- simpler models
- clearer feature stories
- stronger auditability
- better human defensibility

#### Sustainability Lens
Advocates for:
- lower energy / compute cost
- lower retraining frequency burden
- lighter serving footprint
- less wasteful search

### Dynamic activation rule

Not every lens should activate every run.

Activation should depend on:
- dataset structure
- inferred task type
- domain/context notes
- mandate
- deployment setting
- hardware profile
- lifecycle constraints

### Separation of responsibilities

- **Steward** represents what the user or lab wants.
- **Focus Council** represents what the problem itself appears to demand.
- **Strategist** turns the resolved focus into a concrete plan.
- **Synthesizer** resolves and explains conflicts when mandate and focus disagree.

### Required artifacts

- `objective_hypotheses.json`
- `focus_debate.json`
- `focus_profile.json`
- `optimization_profile.json`
- `objective_tradeoffs.json`
- `feature_strategy_profile.json`

### Required behaviors

- Focus Council must run before major planning in guided/autonomous modes.
- The council may conclude that one focus dominates or that a multi-objective blend is required.
- The resolved focus must shape:
  - metric selection
  - threshold objective
  - HPO policy
  - model-family bias
  - feature engineering proposals
  - feature-family bias
  - feature-search aggressiveness
  - feature-selection bias
  - calibration requirements
  - uncertainty requirements
  - serving constraints
  - lifecycle decision policy
- If mandate and focus disagree, the conflict must be surfaced explicitly.


### Focus Council intelligence use

The Focus Council must have two operating modes:

- **deterministic focus reasoning**
  - uses dataset profile
  - task type
  - mandate
  - deployment constraints
  - lifecycle constraints
  - heuristic objective rules

- **LLM-amplified focus reasoning**
  - optionally uses stronger semantic reasoning when available
  - interprets messy domain notes, business context, deployment context, and ambiguous objective language
  - helps infer whether value, reliability, efficiency, interpretability, sustainability, or a blend should dominate

The LLM-amplified mode must remain optional and advisory-to-structured.
The final focus profile must still be emitted as a structured artifact.

### Example outcomes

Examples of resolved focus profiles:
- primary = business_value, secondary = calibration, tertiary = latency
- primary = reliability, secondary = interpretability
- primary = efficiency, secondary = acceptable_accuracy
- primary = multi_objective(score, calibration, latency)

---


## 3C. Handoff evidence bundles

Relaytic specialists should not rely only on an implicit shared working directory or giant global context.

Instead, important cross-agent handoffs should use **bounded evidence bundles**.

### Purpose

Evidence bundles make multi-specialist reasoning:

- more inspectable
- more reproducible
- safer for long runs
- easier to export to other agents
- easier to debug

### What an evidence bundle contains

A bundle should include:

- handoff purpose
- selected evidence items
- structured summary
- provenance references
- confidence notes
- redactions if needed
- size and token limits

### Example uses

- Scout -> Focus Council:
  dataset interpretation packet

- Scientist -> Strategist:
  route and leakage hypothesis packet

- Challenger -> Auditor:
  challenger-failure or challenger-win packet

- Lifecycle Manager -> Synthesizer:
  promotion / rollback evidence packet

### Required artifacts

- `handoff_bundle_manifest.json`
- `evidence_bundle_<id>.json`

### Rules

- Bundles must stay bounded.
- Bundles must prefer selected evidence over raw dumps.
- Bundles must preserve provenance.
- Bundles may be exported for external-agent use.

---


## 3D. Completion decision and continuation judgment

Relaytic must include an explicit layer that decides whether the system is done or should continue.

This decision must be visible to:
- users
- external agents
- long-running operator workflows
- lifecycle logic

### Core question

After meaningful progress points, Relaytic should answer:

> Are we done for now, or is more action still justified?

### Why this matters

A professional system should not only optimize models.
It should know when:

- more search is no longer decision-relevant
- more data is likely more valuable than more tuning
- recalibration is enough
- full retraining is justified
- a candidate is strong enough to promote
- deployment should be rejected despite raw score

### Decision inputs

The completion layer should consume:

- score and robust-score trends
- challenger results
- ablation findings
- calibration and uncertainty status
- slice robustness
- drift and freshness status
- focus-profile satisfaction
- mandate satisfaction
- lifecycle constraints
- expected value of more search
- expected value of more data
- expected value of recalibration
- expected value of retraining

### Output states

The completion layer should output one of:

- `done_for_now`
- `continue_search`
- `collect_more_data`
- `recalibrate_only`
- `retrain_candidate`
- `promote_candidate`
- `rollback`
- `reject_deployment`

### Required artifact

- `completion_decision.json`

### Minimum fields

- status
- confidence
- reasons
- blocking_issues
- expected_value_of_more_search
- expected_value_of_more_data
- expected_value_of_recalibration
- expected_value_of_retraining
- next_recommended_action
- current_stage_reference

### Required behavior

- the completion decision must be updated at meaningful checkpoints
- the completion decision must be visible in UI, API, and reports
- long-running daemon mode must emit periodic completion updates
- completion reasoning must distinguish between:
  - offline experimentation
  - deployment readiness
  - live operational health

---


## 3E. Workflow stage tracking and run-state visibility

Relaytic must make the current workflow step visible at all times.

### Canonical stages

At minimum, Relaytic should track these stages:

- onboarding
- mandate_setup
- context_setup
- intelligence_setup
- focus_selection
- investigate
- hypothesize
- plan
- feature_strategy
- experiment
- challenge
- ablate
- audit
- completion_review
- lifecycle_review
- report
- serve
- monitor

### Required artifacts

- `run_state.json`
- `stage_timeline.json`

### Required behavior

- the current stage must be visible in the UI
- the current stage must be queryable through API/tool surfaces
- every stage transition must be logged
- daemon mode must expose both:
  - current live stage
  - most recent completed stage

### Why this matters

Users and external agents should never have to guess:
- what Relaytic is doing right now
- what it just finished
- what comes next
- whether the run is blocked or waiting on review

---


## 3F. Feedback assimilation and policy learning

Relaytic should improve when users or external agents provide useful feedback.

### Core question

When someone says:
- this target choice was wrong
- this dataset is actually business-critical
- these features are misleading
- this report was not actionable
- this lifecycle choice was too aggressive
- this benchmark expectation was unrealistic

Relaytic should ask:

> Is this feedback valuable, valid, and reusable for similar future runs?

### Feedback sources

Supported sources may include:

- direct user feedback
- operator review
- external-agent review
- benchmark review
- post-deployment outcome review
- intervention outcome review
- abstention/defer outcome review
- human-review queue outcome review
- action-cost review

### Validation rules

Feedback must not automatically become policy.

Relaytic should validate feedback by checking:
- provenance
- consistency with evidence
- whether the feedback is run-specific or reusable
- whether the feedback conflicts with mandate or policy
- whether the feedback improves later outcomes on similar cases
- whether the feedback concerns route quality, decision policy, data quality, or missing-data needs
- whether the claimed improvement survives comparison against downstream outcomes rather than only offline opinion

### Possible updates from validated feedback

Validated feedback may update:
- policy defaults
- focus heuristics
- feature-strategy priors
- route-selection priors
- challenger heuristics
- decision-policy priors
- abstention/defer heuristics
- data-collection priorities
- report templates
- lifecycle heuristics
- benchmark expectations for similar data regimes

### Required artifacts

- `feedback_intake.json`
- `feedback_validation.json`
- `feedback_effect_report.json`
- `policy_update_suggestions.json`
- `route_prior_updates.json`
- `feedback_casebook.json`
- `outcome_observation_report.json`
- `decision_policy_update_suggestions.json`

### Safety rule

Feedback-derived updates must remain inspectable, versioned, and reversible.

---

## 4. Target architecture

### Specialist roles

#### 4.1 Scout
Responsible for:
- independent dataset inspection
- schema inference
- hidden key detection
- leakage pattern discovery
- time/entity/group detection
- missingness profiling
- suspicious-column surfacing
- dataset weirdness logging
- using optional origin/schema/context documents when available

#### 4.2 Scientist
Responsible for:
- task framing
- route hypotheses
- target ambiguity resolution
- feature hypotheses
- split hypotheses
- additional-data hypotheses
- missing-signal hypotheses
- problem restatement in operational terms
- incorporating optional domain brief and reference documents into hypothesis generation
- using stronger LLM reasoning when available to generate higher-quality grounded hypotheses

#### 4.3 Focus Council
Responsible for:
- activating relevant objective lenses
- debating what the run should prioritize
- proposing focus hypotheses
- resolving whether the run should optimize for score, value, reliability, efficiency, interpretability, sustainability, or a blend
- producing a structured focus profile before major planning
- surfacing conflicts between problem demands and user/lab mandate

#### 4.4 Strategist
Responsible for:
- choosing routes under policy, mandate, and resolved focus profile
- selecting metrics
- selecting split strategies
- composing workflow plans
- assigning budget
- selecting search-controller behavior
- deciding whether more experimentation is worth it
- deciding whether success criteria are met
- deciding whether to tune, warm-start, recalibrate, retrain, or defer
- deciding when an external route or backend should be used for one part of the workflow
- adapting search and execution depth to detected hardware and active effort tier
- choosing whether CPU, GPU, multi-GPU, or local-cluster execution is justified
- translating the Focus Council output into an executable optimization strategy

#### 4.5 Builder
Responsible for:
- executing workflow candidates
- tracking trials
- respecting per-phase resource budgets
- early-stopping weak branches
- managing search budgets
- collecting metrics
- persisting artifacts
- running integrated external routes when chosen by the plan
- orchestrating device-aware and optionally distributed execution when available

#### 4.6 Challenger
Responsible for:
- beating the incumbent plan/model
- proposing alternative assumptions
- testing anti-leakage variants
- testing different split semantics
- testing reduced-feature and robustness variants
- surfacing whether the current winner is fragile
- using optional domain/context knowledge to attack unrealistic assumptions
- using stronger LLM reasoning when available to generate better alternate explanations and challenger experiments

#### 4.7 Ablation Judge
Responsible for:
- structured ablations
- fragility analysis
- identifying which assumptions actually drove performance
- separating robust gains from inflated gains
- generating belief updates from ablation evidence

#### 4.8 Auditor
Responsible for:
- calibration
- uncertainty
- slice analysis
- robustness checks
- drift and OOD checks
- repeatability validation
- abstention/defer policy evaluation
- model card generation
- risk report generation

#### 4.9 Steward
Responsible for:
- interpreting long-term lab mandate
- interpreting work preferences
- interpreting run-specific brief
- translating mandate into structured constraints and preferences
- translating free-form human or agent intent into mandate updates with confidence and provenance
- tracking alignment drift during autonomous execution
- participating in debates when evidence conflicts with mandate
- logging tradeoff decisions
- recommending mandate updates over time
- mediating how optional expert context should influence the run
- deciding how strong-LLM interpretations should be weighted against deterministic context parsing

#### 4.10 Memory Keeper
Responsible for:
- storing run fingerprints
- retrieving similar prior runs
- proposing plan archetypes
- remembering failure archetypes
- improving warm starts over time
- remembering mandate patterns and tradeoff history
- storing validated feedback and reusable policy/route priors

#### 4.11 Lifecycle Manager
Responsible for:
- detecting new-data events
- comparing dataset versions
- deciding whether scoring, recalibration, retraining, shadowing, or promotion should occur
- maintaining champion/candidate lineage
- triggering rollback when necessary

#### 4.12 Completion Judge
Responsible for:
- deciding whether the run is done for now or should continue
- fusing score trends, challenger results, ablations, calibration, uncertainty, drift, and focus satisfaction
- estimating the likely value of more search vs more data vs recalibration vs retraining
- emitting a structured completion decision at major checkpoints
- exposing completion state to users and external agents

#### 4.13 Synthesizer
Responsible for:
- comparing competing interpretations
- integrating evidence across specialists
- writing final recommendation rationale
- producing a machine-readable recommendation bundle
- deciding whether the answer is:
  - ship model
  - collect more data
  - continue search
  - reject deployment
  - recalibrate only
  - retrain
  - promote candidate
  - rollback champion

#### 4.14 Broker
Responsible for:
- exposing the system as local tools for external agents
- serving MCP-compatible tool interfaces
- exposing machine-readable capability manifests
- packaging runs for consumption by other systems
- clearly communicating which inputs are optional, which are advisory, and how provenance is handled
- exposing how Relaytic integrates with surrounding systems such as candidate generators, registries, and local-LLM backends

#### 4.15 Dojo Curator
Responsible for:
- managing dojo-mode experiments
- evaluating whether self-improvement hypotheses are valid
- keeping experimental improvements quarantined until validated
- promoting validated method updates into reusable priors and strategy improvements

---

## 5. Package structure

Refactor toward this structure:

```text
src/relaytic/
  agents/
    scout.py
    scientist.py
    focus_council.py
    strategist.py
    builder.py
    challenger.py
    ablation_judge.py
    auditor.py
    steward.py
    memory_keeper.py
    lifecycle_manager.py
    completion_judge.py
    synthesizer.py
    broker.py
    coordinator.py
    schemas.py
    policies.py
    mandates.py
    handoffs.py
    disagreements.py
  autonomy/
    controller.py
    stop_rules.py
    approval.py
    budgets.py
    success_criteria.py
    branch_promotion.py
  datasets/
    schema.py
    profiling.py
    quality.py
    leakage.py
    slicing.py
    time_semantics.py
    entity_detection.py
    target_semantics.py
    unknown_domain.py
    additional_data.py
    versioning.py
  planning/
    task_inference.py
    route_selection.py
    metric_selection.py
    split_selection.py
    focus_selection.py
    optimization_profiles.py
    feature_strategy_selection.py
    search_space.py
    workflow_graph.py
    hypotheses.py
    portfolio_warmstart.py
    pareto.py
    plan_archetypes.py
  experiments/
    registry.py
    tracker.py
    execution.py
    leaderboard.py
    replay.py
    multi_fidelity.py
    challenger_runs.py
    ablations.py
  execution/
    profiles.py
    devices.py
    gpu_policy.py
    distributed.py
    checkpoints.py
    scheduler.py
  hpo/
    backends.py
    constraints.py
    thresholds.py
    transfer.py
    budgets.py
  memory/
    fingerprints.py
    retrieval.py
    run_memory.py
    failure_memory.py
    priors.py
    mandate_memory.py
    feedback_memory.py
  mandate/
    lab_mandate.py
    work_preferences.py
    run_brief.py
    alignment.py
    tradeoffs.py
    updates.py
  context/
    data_origin.py
    domain_brief.py
    task_brief.py
    retrieval.py
    provenance.py
    source_registry.py
  intelligence/
    modes.py
    routing.py
    debate.py
    verifier.py
    reflection.py
    reasoning.py
    semantic_task.py
    backends.py
    local_baseline.py
    capability_profiles.py
    discovery.py
    health.py
    setup_guidance.py
  research/
    query_planner.py
    sources.py
    distillation.py
    transfer.py
    benchmark_refs.py
    audit.py
  decision/
    world_model.py
    action_policy.py
    usefulness.py
    value_of_more_data.py
    abstention_policy.py
  compiler/
    method_compiler.py
    challenger_templates.py
    feature_hypotheses.py
    split_eval_templates.py
    benchmark_protocols.py
  data_fabric/
    source_graph.py
    join_candidates.py
    entity_history.py
    acquisition_plan.py
    point_in_time_contracts.py
  features/
    tabular_basic.py
    tabular_interactions.py
    time_lags.py
    time_windows.py
    encoders.py
    selectors.py
    feature_hypotheses.py
    feature_strategy.py
    versioning.py
    point_in_time.py
    online_offline_checks.py
  modeling/
    families/
      linear.py
      tree.py
      ensemble.py
      baseline.py
      tabpfn_backend.py
    calibration.py
    uncertainty.py
    robustness.py
    abstention.py
    training.py
    inference.py
  registry/
    model_registry.py
    champion.py
    candidate.py
    promotion.py
    rollback.py
    shadow.py
  integrations/
    autogluon_route.py
    mlflow_backend.py
    local_llm_backends.py
    registry_exports.py
    trust.py
    slots.py
  lifecycle/
    freshness.py
    retraining.py
    recalibration.py
    schedules.py
    triggers.py
    decisions.py
    completion.py
    runtime_modes.py
    cycle_controller.py
  dojo/
    session.py
    hypotheses.py
    evaluation.py
    promotion.py
    architecture_search.py
  resources/
    detect.py
    profiles.py
    budgets.py
    watchdog.py
  evaluation/
    metrics.py
    diagnostics.py
    drift.py
    ood.py
    conformal.py
    stability.py
    calibration_plots.py
    conditional_coverage.py
    value_of_information.py
  interoperability/
    api_tools.py
    mcp_server.py
    capability_manifest.py
    tool_cards.py
    artifact_exports.py
    example_payloads.py
  workflows/
    relayspec.py
    runner.py
    validation.py
  observability/
    traces.py
    spans.py
    telemetry.py
    handoff_graph.py
    evidence_bundles.py
    run_state.py
    stage_timeline.py
  mission_control/
    branch_dag.py
    confidence_map.py
    change_attribution.py
    operator_panels.py
    agent_views.py
  artifacts/
    manifests.py
    model_card.py
    reports.py
    packaging.py
  serve/
    app.py
    schemas.py
    monitoring.py
    abstention.py
  ui/
    cli.py
    api.py
    streamlit_app.py
    mandate_forms.py
    context_forms.py
    lifecycle_views.py
    onboarding.py
    doctor.py
    backup_views.py
```

---

## 6. Execution modes

Supported values:

- `manual`
- `guided`
- `autonomous`

### Required CLI and API support
All major commands must accept:

```bash
--execution-mode manual|guided|autonomous
```

---


## 6A. Operation modes

Relaytic must support both bounded runs and explicit long-running operation.

### Supported operation modes

- `session`
- `daemon`

### `session`
Used for one-off investigation, search, reporting, and bounded retraining runs.

Characteristics:
- bounded by default
- hard stop rules active
- designed for laptops and interactive use
- produces a final decision bundle and exits

### `daemon`
Used for continuous monitoring, repeated scoring, scheduled retraining, drift checks, and champion/candidate management.

Characteristics:
- explicit opt-in only
- may continue indefinitely
- must checkpoint regularly
- must emit periodic summaries
- must remain interruptible
- must enforce per-cycle budgets even when the process itself is long-lived

### Required behavior

- if the user does not explicitly request indefinite operation, Relaytic must use `session`
- in `daemon` mode, each cycle must still be bounded even if the service runs forever
- the UI and CLI must explain the difference clearly

---


## 6B. Platform support and personal-computer compatibility

Relaytic must be usable on personal computers, especially laptops and desktop workstations.

### First-class platforms

Support first-class operation on:
- macOS
- Linux

Windows support may be added later, but macOS and Linux must be treated as primary targets.

### macOS requirements

Relaytic must support:
- Intel Mac
- Apple Silicon Mac

### Apple Silicon rules

- do not assume CUDA availability
- treat Metal or vendor-specific acceleration as optional
- fall back cleanly to CPU
- keep the base install usable without GPU-specific dependencies
- resource detection must recognize Apple Silicon hardware profiles

### Dependency discipline

To preserve laptop usability:
- the base install must avoid fragile native dependencies where possible
- heavy or platform-sensitive components must be isolated behind extras
- Docker must remain available as a fallback when native installs are inconvenient
- optional local LLM backends must declare platform support clearly

### Acceptance criteria

- a Mac user can install the base Python package and run a bounded session locally
- a Mac user can use Docker as a fallback path
- Apple Silicon is treated as a first-class machine profile in resource detection
- optional extras do not break the base install on common Mac setups

---


## 6C. Accelerated and distributed local execution

Relaytic must treat local execution as a spectrum, not only a laptop process.

### Local execution profiles

Relaytic should support profiles such as:

- `cpu_local`
- `gpu_local`
- `multi_gpu_local`
- `workstation_local`
- `local_server`
- `local_instance`
- `local_cluster_interactive`
- `local_cluster_batch`

These profiles remain **local-first** as long as the hardware is under the user’s control or within their explicitly approved environment.

### Core rule

If stronger permissible local hardware is available, Relaytic should be able to use it.

Examples:
- deeper search on a workstation
- stronger local reasoning model on a GPU box
- wider benchmark sweep on a local cluster
- distributed challenger branches on multiple devices
- larger feature search on a high-memory local instance

### Required behavior

Relaytic should:
- detect available devices and execution backends
- choose a suitable execution profile automatically when limits are unspecified
- let the user or external agent override execution profile explicitly
- decide whether GPU or distributed execution is actually worth the overhead
- fall back cleanly to smaller profiles when acceleration is not available

### Distributed execution rule

Distributed or scheduler-backed execution should remain:
- explicit
- policy-aware
- checkpointed
- traceable
- recoverable

### Required artifacts

- `execution_backend_profile.json`
- `device_allocation.json`
- `distributed_run_plan.json`
- `scheduler_job_map.json`
- `checkpoint_state.json`

---

## 7. Mandate system

Relaytic must maintain a mandate layer that represents what the lab cares about and how the current run should be conducted.

### Mandate layers

#### 7.1 Long-term lab mandate
Represents durable philosophy and global preferences.

#### 7.2 Work preferences
Represents semi-stable style and workflow preferences.

#### 7.3 Run brief
Represents specific run intent.

### Influence modes

Supported modes:

- `off`
- `advisory`
- `weighted`
- `binding`
- `constitutional`

### Meaning of modes

- `off`: no mandate influence beyond safety/policy.
- `advisory`: mandate is visible, but agents may ignore it with logged rationale.
- `weighted`: mandate materially influences ranking and recommendation, but can be overridden with evidence.
- `binding`: hard and high-priority mandate requirements must be followed.
- `constitutional`: the mandate defines governing principles for the run; agents may debate, but final decisions must stay within those boundaries.

### Required artifacts

- `lab_mandate.json`
- `work_preferences.json`
- `run_brief.json`
- `alignment_trace.json`
- `tradeoff_decisions.json`
- `mandate_update_suggestions.json`

### Required behaviors

- the mandate can be enabled or disabled
- influence mode is visible and editable
- hard constraints must always be obeyed
- soft preferences may be challenged with evidence
- all major conflicts between evidence and mandate must be logged
- the final recommendation must state:
  - what the mandate preferred
  - what the evidence preferred
  - what compromise was chosen

---

## 8. Policy system

### Policy schema

```yaml
policy:
  locality:
    remote_allowed: false
    local_models_only: true
    allow_optional_remote_baselines: false
  autonomy:
    execution_mode: autonomous
    operation_mode: session
    allow_auto_run: true
    allow_indefinite_operation: false
    approval_required_for_expensive_runs: true
    approval_required_for_optional_backends: true
  compute:
    autodetect_hardware_if_unspecified: true
    machine_profile: auto
    default_effort_tier: standard
    max_wall_clock_minutes: 120
    max_trials: 200
    max_parallel_trials: 4
    max_memory_gb: 24
    multi_fidelity_enabled: true
    execution_profile: auto
    gpu_allowed: true
    distributed_local_allowed: true
    scheduler_allowed: true
    checkpoint_required_for_distributed_runs: true
  optimization:
    objective: best_robust_pareto_front
    primary_metric: auto
    secondary_metrics: [calibration, stability, latency]
    pareto_selection: true
    focus_council_enabled: true
    focus_profile: auto
  constraints:
    latency_ms_max: null
    interpretability: medium
    uncertainty_required: true
    reproducibility_required: true
    abstention_allowed: true
  safety:
    strict_leakage_checks: true
    strict_time_ordering: true
    reject_unstable_models: true
    require_disagreement_resolution: true
    require_challenger_science: true
  memory:
    enable_run_memory: true
    allow_prior_retrieval: true
    feedback_learning_enabled: true
  mandate:
    enabled: true
    influence_mode: weighted
    allow_agent_challenges: true
    require_disagreement_logging: true
    allow_soft_preference_override_with_evidence: true
  context:
    enabled: true
    external_retrieval_allowed: false
    allow_uploaded_docs: true
    require_provenance: true
    semantic_task_enabled: true
  intelligence:
    enabled: true
    intelligence_mode: none
    prefer_local_llm: true
    allow_frontier_llm: false
    allow_max_reasoning: false
    minimum_local_llm_enabled: false
    minimum_local_llm_profile: none
    enable_backend_discovery: true
    allow_upgrade_suggestions: true
    allow_automatic_local_upgrade: false
    require_schema_constrained_actions: true
    require_verifier_for_high_impact_decisions: true
  lifecycle:
    scheduled_retraining_enabled: true
    drift_triggered_retraining_enabled: true
    recalibration_only_allowed: true
    rollback_allowed: true
    champion_candidate_registry_enabled: true
    completion_judge_enabled: true
    stage_visibility_enabled: true
  dojo:
    enabled: false
    allow_method_self_improvement: true
    allow_architecture_proposals: true
    require_quarantine_before_promotion: true
  hpo:
    backend: optuna_or_flaml
    enable_multi_objective: true
    enable_threshold_tuning: true
    enable_transfer_from_prior_runs: true
  interoperability:
    enable_mcp_server: true
    expose_tool_contracts: true
    workflow_specs_enabled: true
  integrations:
    engine_slots_enabled: true
    trust_mode_default: advisory_only
    dry_run_for_side_effecting_backends: true
  reporting:
    create_model_card: true
    create_risk_report: true
    create_experiment_graph: true
    create_handoff_graph: true
    create_data_recommendations: true
    create_decision_memo: true
```

---


## 8A. Hardware detection and resource governance

Relaytic must be practical on personal computers by default.

### Hardware autodetection

If the user does not provide limits, Relaytic must inspect local hardware and derive conservative defaults from:

- CPU count
- available RAM
- free disk space
- optional accelerator availability
- operating-system limits when visible

### Derived assumptions

From detected hardware, the system must infer:

- machine profile:
  - `laptop_light`
  - `laptop_standard`
  - `workstation`
  - `server_like`
  - `gpu_workstation`
  - `local_cluster`
- safe parallelism
- safe RAM budget
- safe artifact budget
- safe search depth
- whether GPU acceleration is worthwhile
- whether distributed execution is worthwhile
- whether heavy optional backends should be discouraged

### Effort tiers

Support:
- `quick`
- `standard`
- `deep`

If nothing is specified:
- autodetect hardware
- choose `standard`
- scale budgets conservatively to the machine profile

### Watchdog behavior

The system must monitor:
- memory pressure
- CPU saturation
- artifact growth
- queue growth
- disk pressure

When pressure exceeds safe bounds, Relaytic must:
- reduce parallelism
- reduce challenger depth
- reduce HPO depth
- skip non-critical ablations
- checkpoint and stop if required

### Required artifacts

- `hardware_profile.json`
- `resource_assumptions.json`
- `budget_resolution.json`

---

## 9. Mandate disagreement protocol

### Rules
- Agents must obey hard constraints.
- Agents may challenge soft preferences when evidence suggests a materially better alternative.
- All challenges to mandate-aligned plans must be logged.
- Final recommendation must state:
  - what the mandate preferred
  - what the evidence preferred
  - what compromise was selected

---

## 10. Knowledge and context layer

Relaytic must support optional expert grounding without making it mandatory.

### Core rule

The system must work in both modes:

- **ungrounded mode**
  - no domain brief
  - no uploaded docs
  - no external retrieval
  - agents continue using dataset evidence, prior-run memory if allowed, and policy/mandate only

- **grounded mode**
  - user-supplied context and/or uploaded docs are available
  - optional private research retrieval may be enabled by policy
  - agents may use grounded evidence with provenance tracking

### Context layers

#### A. Data origin
Represents where the dataset came from and how it was produced.

#### B. Domain brief
Represents what the real-world system is, what the target means, what known caveats exist, and which columns are suspicious or forbidden.

#### C. Task brief
Represents what problem the user actually wants solved.

#### D. Reference documents
Represents uploaded PDFs, data dictionaries, schema docs, SOPs, papers, notes, and prior reports.

#### E. Private research retrieval
Represents policy-gated external retrieval for papers, benchmark docs, method cards, implementation references, and domain-specific references through redacted run signatures.

### Required artifacts

- `data_origin.json`
- `domain_brief.json`
- `task_brief.json`
- `context_sources.json`
- `provenance_map.json`
- `research_query_plan.json`
- `research_source_inventory.json`
- `research_brief.json`
- `method_transfer_report.json`
- `benchmark_reference_report.json`
- `external_research_audit.json`

### Trust and precedence rules

- user-provided hard constraints override external literature
- uploaded authoritative docs may be marked as binding or advisory
- literature is advisory unless the user explicitly says otherwise
- prior-run memory is advisory
- when sources conflict, the conflict must be surfaced explicitly
- retrieved methods must become explicit transfer hypotheses, not silent route overrides
- benchmark references must become explicit comparison plans, not automatic claims of parity

### Required behaviors

- the system must be able to continue when no context is provided
- the UI must let users provide context before or during a run
- external retrieval must be opt-in and policy-gated
- external research queries must default to redacted, rowless, generalized task/domain signatures
- no raw rows, private identifiers, machine paths, or proprietary system names may leave the machine unless policy explicitly grants richer disclosure
- every research-derived recommendation must say what was transferred: route idea, challenger idea, metric/split idea, benchmark reference, or data-collection suggestion
- every grounded recommendation must cite whether it came from:
  - raw data evidence
  - user-provided context
  - uploaded docs
  - prior-run memory
  - external literature

---


## 10A.1 Context interpretation and semantic grounding

Relaytic must be able to use expert context even when no LLM is available.

### Core rule

Expert context interpretation must support two paths:

- **deterministic interpretation path**
- **optional local-LLM interpretation path**

Structured context may be provided directly, but Relaytic must also support
free-form user or external-agent input that is translated into the same
foundation objects with provenance, confidence, optional clarification, and
explicit fallback assumptions before those objects are updated.

### Deterministic interpretation path

Without any LLM, the system should still extract useful structure from expert context using:

- structured forms
- field-level templates
- column-note mappings
- keyword and pattern extraction
- schema alignment
- document chunk retrieval with provenance
- deterministic confidence rules

This path must support:
- identifying likely target definitions
- identifying known leakage columns
- identifying forbidden features
- identifying operational constraints
- identifying deployment context
- identifying domain caveats

### Optional local-LLM interpretation path

When a capable local or frontier LLM is available, it may improve:

- semantic interpretation of free-form notes
- summarization of uploaded documents
- extraction of subtle domain caveats
- mapping between user language and modeling constraints
- generation of stronger grounded hypotheses

### Required rule

The local LLM is an enhancement, not a dependency.
If no local LLM exists, Relaytic must still proceed using deterministic parsing and provenance-aware retrieval.

### Required artifacts

- `context_interpretation.json`
- `context_constraints.json`
- `semantic_mapping.json`

---


## 10A.2 Intelligence amplification layer

Relaytic must be able to exploit stronger LLMs when available without becoming dependent on them.

### Core rule

Relaytic must support two lanes:

- **deterministic floor**
  - always available
  - no LLM required
  - sufficient for end-to-end operation

- **LLM-amplified ceiling**
  - optional
  - activated when a capable local or frontier LLM is available and allowed by policy
  - improves semantic understanding, critique, planning, and synthesis

### Intelligence modes

Support:

- `none`
- `local_min`
- `assist`
- `amplify`
- `max_reasoning`

### Meaning of modes

- `none`
  - deterministic only
  - no LLM involvement

- `local_min`
  - use a small quantized local LLM for dataset-label understanding, conversational UX, note interpretation, and light semantic extraction
  - intended for personal computers when users want on-device help without a stronger model

- `assist`
  - use LLMs for summarization, note interpretation, and context extraction
  - deterministic planning remains primary

- `amplify`
  - use LLMs for investigation, hypothesis generation, challenger design, and synthesis
  - deterministic validators still gate actions

- `max_reasoning`
  - use stronger LLM reasoning passes for investigation, critique, debate, reflection, and lifecycle decisions
  - intended for the most semantically difficult phases
  - still subject to hard budgets and deterministic verification

### Quality and budget contracts

Relaytic should not keep "good enough" and "worth the search" as hidden defaults.

It should materialize:

- one explicit quality contract
  - task-appropriate metric gates
  - benchmark appetite
  - review or abstain posture
  - calibration and uncertainty expectations
  - current stop/continue semantics

- one explicit budget contract
  - runtime budget
  - search and challenger budget
  - autonomy-loop budget
  - hardware and execution assumptions
  - configured versus derived limits

- bounded operator and lab profiles
  - may shape review strictness, benchmark appetite, explanation style, and budget posture
  - must not silently override deterministic metrics, model outcomes, or artifact truth

If no explicit inputs are given, Relaytic should derive these contracts from task evidence, local hardware assumptions, mandate/work preferences, and policy defaults, write them explicitly, and continue.


### Minimum local LLM baseline

Relaytic may offer an optional minimum on-device LLM baseline for users who want lightweight semantic help.

This baseline should be:

- good enough to power a communicative assist layer that can explain current state, guide a human or agent through the workflow, and make the UI feel alive without becoming the authoritative control plane
- optional rather than mandatory
- local-first by default
- cheap enough for regular laptop use

- optional
- replaceable
- disableable
- quantized and personal-computer friendly
- used only for semantic assistance, not as a mandatory control plane

### Intended uses of the minimum baseline

- interpreting dataset labels and column names
- helping users talk to the system locally
- extracting structure from short notes
- lightweight domain/context interpretation
- label/target candidate explanation

### Non-goals of the minimum baseline

The minimum local baseline should **not** be required for:
- model fitting
- metric computation
- lifecycle decisions
- artifact generation
- hard policy enforcement

### Baseline model guidance

The plan should support a configurable baseline local model slot with choices such as:

- `none`
- `small_4b_quantized`
- `small_7b_quantized`
- `custom_local_model`

Do not hardcode a single model into the architecture contract.
Instead, define:
- required capability level
- maximum expected resource footprint
- backend abstraction
- configuration interface

### Practical recommendation

For the architecture, assume:
- baseline local semantic helper: small 4B–8B quantized instruct model when available
- stronger local model: larger local instruct/reasoning model when available
- frontier model: optional external high-end reasoning model if policy allows, used as an amplifier or challenger backend rather than a hard dependency for the core run loop

The exact model name should remain configurable rather than baked into the core design.

Relaytic should also provide setup guidance and backend health checks for this slot rather than assuming it is already configured.

### Where LLM intelligence should help most

When available, strong LLMs should primarily improve:

- dataset understanding
- free-form expert context interpretation
- hypothesis generation
- challenger experiment design
- mandate/context conflict interpretation
- final synthesis
- recalibrate vs retrain vs defer judgment under ambiguity

### What must remain deterministic

Even in `max_reasoning` mode, these must remain deterministic:

- model fitting
- metric computation
- calibration math
- conformal math
- budget enforcement
- stop rules
- dataset and feature versioning
- registry promotion and rollback mechanics
- artifact writing and manifests

### Required patterns

#### Structured action generation
All LLM-produced actions must be schema-constrained and validated before execution.

#### Debate + verifier pattern
Important semantic decisions should support:
- proposer
- challenger
- verifier

#### Reflection memory
The system should store reflective lessons from:
- failed hypotheses
- fragile gains
- surprising ablations
- retraining mistakes
- mandate/evidence conflicts

### Required artifacts

- `intelligence_mode.json`
- `llm_routing_plan.json`
- `local_llm_profile.json`
- `debate_trace.json`
- `verifier_report.json`
- `semantic_proof_report.json`
- `reflection_memory.json`

### Required behavior

- if no capable LLM is available, Relaytic must continue with the deterministic floor
- if a strong LLM is available, Relaytic should use it at the most semantically valuable phases rather than everywhere
- available local hardware may influence which intelligence mode is recommended
- Relaytic must always be able to state the canonical requested mode, recommended mode, and selected routed mode even when legacy labels or older config values were used internally
- one explicit local baseline profile should be resolved when local semantic help is configured or recommended
- backend discovery should expose a bounded capability matrix relevant to schema-constrained semantic work
- the chosen intelligence mode must be visible in UI, CLI, API, and artifacts
- LLM outputs must never bypass deterministic safety, policy, or budget checks
- semantic amplification should leave an explicit proof artifact showing whether it changed bounded semantic outputs relative to a deterministic semantic baseline

---


## 10A.3 Local-LLM setup assistance and intelligence discovery

Relaytic must help users and external agents configure local intelligence when they want it.

### Core rule

If no local LLM is configured, Relaytic should still work.
But if semantic help would materially improve the run, Relaytic should be able to:

- explain that a local LLM is optional
- detect compatible local-LLM backends when possible
- guide the user through setup
- recommend an appropriate intelligence mode
- suggest stronger available local models when they would materially improve results

### Supported setup-assistance behaviors

Relaytic should support:

- backend discovery
- capability probing
- simple setup guidance
- health checks
- model-slot validation
- explicit opt-in upgrade suggestions

### Discovery targets

At minimum, the architecture should anticipate detection/support adapters for:

- Ollama-style local endpoints
- LM Studio-style local endpoints
- custom OpenAI-compatible local endpoints
- custom Anthropic-compatible local endpoints where relevant

### Required artifacts

- `llm_backend_discovery.json`
- `llm_setup_guide.json`
- `llm_health_check.json`
- `llm_upgrade_suggestions.json`

### Required behavior

- setup help must be visible in the UI
- setup help must be available through the API/tool surface
- users must be able to choose:
  - no local LLM
  - minimum local semantic helper
  - stronger local model
  - custom endpoint
- if Relaytic detects a stronger available local model/backend, it may recommend using it
- recommendations must explain:
  - why the stronger option helps
  - which phases benefit
  - expected resource cost
  - whether the recommendation is optional

### Safety rule

Relaytic must never silently switch to a stronger model without explicit user or caller permission unless a policy explicitly allows automatic upgrade within local-only boundaries.

---


## 10A.4 Structured semantic task primitive

Relaytic should expose a small, safe semantic primitive for bounded meaning-extraction tasks.

This is different from full agentic planning.

### Purpose

Use structured semantic tasks for things like:

- interpret these column labels
- extract likely constraints from these notes
- summarize target meaning into a schema
- list likely leakage hints from this domain brief
- explain why these target candidates differ

### Rules

- one semantic task should be narrow and bounded
- inputs should be explicit
- outputs must be schema-constrained
- no uncontrolled tool use inside the primitive
- results are challengeable and not automatically authoritative

### Why it belongs in Relaytic

This lets Relaytic exploit stronger intelligence safely for small semantic jobs without turning every workflow into an uncontrolled LLM loop.

### Required artifacts

- `semantic_task_request.json`
- `semantic_task_results.json`

### Example output fields

- task_type
- extracted_facts
- inferred_constraints
- uncertainty_notes
- confidence
- provenance

---


## 10A.5 Health-driven intelligence escalation

Relaytic should not use stronger intelligence blindly.

It should escalate intelligence when the expected value is high.

### Escalation triggers

Examples:
- ambiguous target semantics
- messy or cryptic labels
- conflicting context documents
- mandate vs focus conflict
- unstable lifecycle recommendation
- contradictory challenger evidence
- unusually high uncertainty in semantic extraction

### Required behavior

When such ambiguity appears, Relaytic may recommend:

- enable a minimum local semantic helper
- use a stronger local model
- use a stronger allowed reasoning backend
- keep deterministic mode if the gain is unlikely to matter

### Required outputs

Any escalation suggestion must state:
- why stronger intelligence may help
- which phase would improve
- expected resource cost
- whether the suggestion is optional
- what happens if the user declines

### Required artifacts

- `intelligence_escalation.json`

---

## 10A.6 Semantic debate, verifier, and counterposition packets

Relaytic should use stronger semantic help for the hard parts of expert discussion, not as a vague all-purpose oracle.

### Purpose

When task framing, challenger direction, retrain-vs-recalibrate choice, or domain interpretation is materially ambiguous, Relaytic should be able to run a bounded semantic discussion that produces:

- one proposed interpretation
- one counterposition
- one verifier pass
- one explicit uncertainty report

### Rules

- the debate must stay schema-bound and artifact-backed
- the debate must operate on rowless or explicitly minimized context by default
- extracted facts, hypotheses, counterarguments, and verifier findings must be separate fields rather than one blended paragraph
- no semantic debate packet may silently override deterministic evidence
- debate packets should be allowed to influence challenger design, retraining rationale, and target interpretation only through explicit artifacts

### Required artifacts

- `semantic_debate_report.json`
- `semantic_counterposition_pack.json`
- `semantic_uncertainty_report.json`

### Why it belongs in Relaytic

This is how Relaytic makes its internal discussions feel like expert reasoning instead of a chain of thin heuristics or decorative agent labels.

---

## 11. Unknown-domain investigation

### Required artifact
- `domain_memo.json`

The system must infer task framing, target semantics, likely leakage, likely decision type, and what it is unsure about.

---

## 12. Independent data understanding

### Required artifacts

```text
independent_profiles/
  profile_a.json
  profile_b.json
  disagreement_report.json
  resolved_understanding.json
```

At least two specialists must independently inspect the dataset before major experiment search begins.

---

## 13. Planning system

### New artifacts
- `plan.json`
- `alternatives.json`
- `hypotheses.json`
- `rejected_routes.json`

### Planner requirements
Planner must produce:
- one primary plan
- at least two alternative plans
- at least one challenger plan
- at least one additional-data hypothesis when relevant
- at least one leakage hypothesis when relevant
- at least one split-validity hypothesis when relevant
- one learned-prior route when appropriate
- one classical search route when appropriate
- one hybrid route when appropriate
- one focus-aligned optimization profile
- a mandate alignment note for each major plan
- a focus alignment note for each major plan
- a lifecycle note for whether the output should be used for one-off analysis, deployment, recalibration, retraining, or shadowing

---

## 14. Run memory and meta-priors

### Required artifacts
- `memory_retrieval.json`
- `plan_archetype.json`
- `historical_analogs.json`
- `reflection_memory.json`
- `memory_flush_report.json`

### Required capabilities
- retrieve similar prior runs
- warm-start plan generation from archetypes
- retrieve similar failure modes
- propose prior-informed challenger plans
- compare current run against historical analogs
- retrieve similar mandate patterns and tradeoffs
- retrieve similar retraining and promotion decisions
- write durable reflection memory before retries, compaction, and final completion/lifecycle decisions
- keep any retrieval index derived from on-disk artifacts rather than authoritative on its own
- explain the counterfactual effect of memory whenever it changes route or challenger choice

---

## 15. Advanced search controller and HPO

### Required search features
- multi-fidelity pruning
- Successive Halving / ASHA-style branch pruning
- portfolio warm-starts
- branch promotion
- compute-aware scheduling
- per-branch stop criteria
- incumbent vs challenger tracking
- Pareto-front model selection across:
  - score
  - calibration
  - stability
  - latency
  - artifact size

### HPO requirements
- explicit HPO backend selection
- constrained multi-objective tuning
- threshold tuning separate from model hyperparameters when appropriate
- cross-run transfer of good configs
- family-specific tuning budgets
- ability to skip deep HPO when learned-prior routes dominate
- focus-aware HPO depth and objective shaping based on the Focus Council output

### Required artifacts
- `hpo_plan.json`
- `hpo_trace.json`
- `threshold_tuning_report.json`

---


## 15A. Device-aware planning and acceleration policy

Relaytic must make execution-backend choice part of planning.

### Core question

For a given run, Relaytic should ask:

> Which execution profile gives the best speed/quality tradeoff under current policy and available hardware?

### Planning implications

Execution profile should influence:
- candidate-family eligibility
- HPO depth
- number of challenger branches
- benchmark sweep breadth
- feature-search breadth
- intelligence mode recommendation
- checkpoint frequency
- distributed fan-out strategy

### Required behavior

- GPU should be used when its expected benefit exceeds overhead
- distributed execution should be used when the run is large enough to justify scheduling and collation overhead
- local cluster execution should favor checkpointable, artifact-rich job plans
- low-latency laptop runs should avoid pretending to be HPC jobs

### Required artifact

- `execution_strategy_report.json`

---

## 16A. Impact-per-effort experiment prioritization

Relaytic should not queue new experiments only because they are possible.

It should ask:

> Which next experiment is most likely to improve the final decision per unit effort?

### Core rule

Every proposed next experiment should be scored by expected marginal value relative to effort.

### Expected value dimensions

Potential value may include:
- improved final recommendation quality
- reduced uncertainty
- better challenger coverage
- better calibration confidence
- better lifecycle confidence
- better understanding of whether more data matters

### Effort dimensions

Effort should include:
- compute time
- memory and accelerator demand
- implementation or orchestration complexity
- artifact and storage growth
- data-collection burden
- operator burden

### Required artifacts

- `experiment_priority_report.json`
- `marginal_value_of_next_experiment.json`

### Required behavior

- Relaytic should rank next actions by expected value per effort
- the completion layer should use this ranking when deciding whether to continue or stop
- the UI should show why one next experiment outranks another

---

## 16. Autonomous experimentation loop

### New orchestration loop

```text
configure mandate -> configure optional context -> intake and translate user/agent inputs -> focus selection -> investigate -> resolve understanding -> hypothesize -> plan -> feature strategy -> execute batch -> challenge -> ablate -> audit -> completion review -> lifecycle review -> decide next step -> execute one bounded follow-up round when value remains -> rejudge champion lineage -> stop and report
```

### Required loop decisions
- `expand_search`
- `refine_promising_branch`
- `promote_branch`
- `queue_challenger_branch`
- `expand_challenger_portfolio`
- `run_ablation_suite`
- `calibrate_top_models`
- `execute_recalibration_pass`
- `execute_retrain_pass`
- `run_uncertainty_wrap`
- `run_robustness_checks`
- `launch_semantic_counterposition`
- `replan_with_counterposition`
- `run_high_effort_reasoning_pass`
- `request_more_data`
- `rejudge_champion_lineage`
- `stop_after_plateau`
- `stop_after_budget_limit`
- `emit_completion_decision`
- `stop_and_report`

### Loop discipline

- completion and lifecycle judgments should be executable when policy and budget allow, not merely descriptive
- every loop round must record why it was chosen, what budget it consumed, what changed, and whether the current champion survived
- challenger science should expand into a small portfolio when route narrowness or challenger pressure is detected
- autonomous loops must be bounded by explicit budgets, plateau rules, and policy boundaries
- if the next round is not expected to pay for itself, Relaytic should stop honestly rather than perform search theater

---

## 17. Experiment graph and handoff graph

### New artifacts
- `experiment_graph.json`
- `handoff_graph.json`
- `pareto_front.json`

---

## 18. Model family system

### Baseline family layer
- linear regression or ridge
- logistic regression
- simple decision tree
- majority or mean baseline
- last-value and seasonal naive for time series

### Standard family layer
- random forest
- extra trees
- gradient boosting
- histogram boosting where practical

### Learned-prior / frontier route layer
Optional extras may expose:
- TabPFN backend
- benchmark reference runners for AutoGluon
- benchmark reference runners for FLAML
- benchmark reference runners for auto-sklearn
- surrogate-specific libraries
- optional heavier local libraries

### Strategy rule
The Strategist must explicitly consider:
- classical search route
- learned-prior route
- hybrid route

when the dataset regime supports them.

---


## 18A. External systems integration

Relaytic should integrate strong surrounding systems where they are useful, without giving up Relaytic’s judgment layer.

### AutoGluon-style route integration

Relaytic may use AutoGluon-style systems as one candidate-generation or execution route.

Role inside Relaytic:
- candidate generator
- strong tabular baseline/portfolio route
- optional executor for broad family search

Rules:
- AutoGluon route is one route among others, not the whole product
- Challenger must still attack the AutoGluon winner
- Ablation Judge must still test whether the gain is fragile or inflated
- Synthesizer must still decide whether the AutoGluon result is the right final recommendation

### MLflow-style backend integration

Relaytic may use MLflow-style systems as optional infrastructure for:

- run lineage
- model registry
- champion/candidate aliases
- promotion history
- tracing exports

Rules:
- MLflow-style backend is an optional system of record, not Relaytic’s identity
- Relaytic still owns:
  - recommendation logic
  - recalibrate vs retrain vs promote vs rollback judgment
  - decision memo generation
  - mandate-aware tradeoff reasoning

### Local-LLM backend integration

Relaytic may use surrounding local-LLM serving systems as backend providers for intelligence modes.

Examples of role:
- local semantic helper
- stronger local reasoning backend
- backend discovery target
- health-check target

Rules:
- backend may be swapped
- intelligence layer stays backend-agnostic
- deterministic safeguards stay in Relaytic

### Required integration artifacts

- `integration_plan.json`
- `external_route_results.json`
- `registry_backend_config.json`
- `backend_export_report.json`

### Acceptance criteria

- external systems can be used where they are strongest
- Relaytic still owns final cross-route judgment
- any external result can be challenged, ablated, and overruled
- no integrated system is treated as unquestionable

---


## 18B. Trust boundaries, supply chain, and safe integration

Relaytic must be explicit about trust boundaries.

### Core rule

Every integration is useful but challengeable.

This includes:
- candidate-generation routes
- registry/tracing backends
- local-LLM backends
- semantic-task backends
- imported artifacts
- remote-compatible endpoints if policy allows them

### Required trust modes

Each integration should be labeled as one of:

- `trusted_local`
- `trusted_configured`
- `advisory_only`
- `quarantined`
- `disabled`

### Required protections

Relaytic should include:
- secrets redaction in logs and artifacts
- explicit backend allowlists
- dry-run for side-effecting operations where practical
- fail-closed defaults for risky remote or write-capable integrations
- provenance on imported results
- quarantine mode for uncertain adapters

### Why this matters

Relaytic should be bold in using strong systems but strict in what it trusts.

### Required artifacts

- `trust_boundary_report.json`
- `integration_trust_modes.json`
- `redaction_report.json`

---

## 19. Features system and feature lifecycle

Feature generation must become route-aware, policy-aware, hypothesis-aware, and lifecycle-safe.

### Required feature lifecycle capabilities
- feature versioning
- point-in-time correctness for training
- online/offline consistency checks
- feature availability checks at inference time
- schema compatibility checks across retrains

### Required artifacts
- `feature_manifest.json`
- `feature_version.json`
- `offline_online_consistency_report.json`

---


## 19A. Focus-shaped feature engineering

Feature engineering must be explicitly conditioned on the resolved focus profile.

### Core rule

Relaytic must not treat feature engineering as a generic prelude to modeling.
Feature proposals should reflect what the run is trying to optimize for.

### Examples

#### Accuracy-focused runs
May allow:
- richer interactions
- broader transforms
- deeper candidate feature search
- more aggressive engineered representations

#### Value-focused runs
Should prefer:
- action-linked features
- intervention-relevant features
- threshold-relevant signals
- features tied to business timing or business process leverage

#### Reliability-focused runs
Should prefer:
- stable features
- low-leakage features
- low-missingness-risk features
- features with cleaner slice behavior
- features that support better calibration

#### Efficiency-focused runs
Should prefer:
- cheap-to-compute features
- low-latency transforms
- smaller feature sets
- lighter materialization cost

#### Interpretability-focused runs
Should prefer:
- human-legible features
- simpler aggregates
- fewer opaque interactions
- easier feature narratives

#### Sustainability-focused runs
Should prefer:
- lower-compute transforms
- lower retraining burden
- lighter feature pipelines
- lower feature maintenance cost

### Required artifact

- `feature_strategy_profile.json`

### Minimum fields

- primary_focus
- allowed_feature_families
- discouraged_feature_families
- aggressiveness
- interpretability_bias
- stability_bias
- compute_bias
- rationale

### Required behavior

- the Focus Council and Strategist must jointly shape feature strategy
- the final plan must cite the feature strategy profile
- the feature strategy must influence both proposal and selection, not only reporting

---

## 19B. Physics-respecting trajectory and exploration policy

If Relaytic infers or is told that the data represents a physical system, it should respect physical plausibility in proposed next trajectories and experiments.

### Core rule

By default, Relaytic should remain within:
- known feasible regions
- trusted gradients
- valid operating envelopes
- known control ranges

### Exploration modes

Relaytic should distinguish:

- **interpolation**
  - stay inside observed/support regions

- **local controlled exploration**
  - move along nearby trusted gradients
  - bounded deviation from known trajectories

- **frontier extrapolation**
  - explicit opt-in
  - risk-labeled
  - used only when policy and user intent allow it

### Required behavior

Physics-aware constraints should influence:
- data-collection proposals
- active-learning proposals
- simulation sweeps
- feature engineering suggestions for trajectories
- dojo exploration on physical systems

### Required artifacts

- `trajectory_constraint_report.json`
- `feasible_region_map.json`
- `extrapolation_risk_report.json`

### Required rule

If a proposal leaves known feasible gradients, Relaytic must state:
- why
- what is assumed
- what the extrapolation risk is
- whether a safer local alternative exists

---

## 20. Evidence and ablation engine

### Required outputs
- `ablation_report.json`
- `belief_update.json`

### Required ablations
- leakage ablations
- suspicious-feature removal
- temporal split ablations
- reduced-data ablations
- missingness stress tests
- entity holdout ablations
- label-noise sensitivity
- feature-family ablations
- route ablations

---

## 21. Evaluation redesign

Must include:
- performance
- calibration
- stability
- robustness
- uncertainty
- abstention/defer
- operational metrics

---


## 21A. Evaluation layers and professional decision boundaries

Relaytic must distinguish clearly between three evaluation layers.

### A. Offline experimentation evaluation
Questions:
- Did the candidate perform well in training, validation, and backtesting?
- Did the challenger break the apparent winner?
- Are gains robust under ablation?

### B. Deployment-readiness evaluation
Questions:
- Is the candidate calibrated enough?
- Is uncertainty acceptable?
- Is the model robust enough for the intended setting?
- Is it aligned with focus and mandate?

### C. Live operational evaluation
Questions:
- Is the deployed system still healthy under current data?
- Has drift or freshness degradation appeared?
- Should we keep monitoring, recalibrate, retrain, promote, or roll back?

### Required behavior

The completion decision must say which layer is currently blocking progress, if any.

---

## 21B. Decision-system world model and action economics

Relaytic should not stop at "which model scored best."

It should model the downstream decision environment that the prediction is meant to serve.

### Core questions

- what action follows a positive, negative, or uncertain prediction
- what false positives, false negatives, abstentions, and delays cost
- whether human review exists and what queue or latency limits it has
- whether the best next move is more search, more data, recalibration, retraining, or a different operational policy
- whether the current label or target is only a proxy for the real decision objective

### Required behavior

- when explicit action economics are missing, Relaytic should infer a provisional decision regime and mark the uncertainty explicitly
- offline score improvements must not be treated as automatically valuable if they do not improve the downstream decision regime
- abstention, defer, and queue-aware choices must be treated as first-class decision outputs where relevant
- decision-policy reasoning must remain auditable and must not silently replace deterministic metric, calibration, or lifecycle mechanics

### Required artifacts

- `decision_world_model.json`
- `intervention_policy_report.json`
- `decision_usefulness_report.json`
- `value_of_more_data_report.json`

---

## 22. Uncertainty, calibration, and abstention

### New artifacts
- `uncertainty_report.json`
- `calibration_report.json`
- `abstention_report.json`

### Additional lifecycle requirement
The system must support a recalibration-only path when:
- the model family remains adequate
- drift is moderate
- a full retrain is not yet justified

### Required artifact
- `recalibration_decision.json`

---


## 22A. Benchmark parity, reference approaches, and non-hardcoded excellence

Relaytic must be judged against strong external reference points.

### Core rule

For every supported route, Relaytic should be benchmarked against:

- strong general benchmark datasets
- strong standard or gold-reference approaches
- sensible naive baselines
- strong ecosystem-integrated routes when available

### Why this matters

Relaytic should not only be elegant.
It should be credibly strong on real tasks.

### Benchmark doctrine

Relaytic must try to reach strong benchmark performance by using:
- general planning
- focus-aware optimization
- feature strategy
- challenger science
- learned priors
- dojo-mode improvements

It must **not** rely on:
- benchmark-specific hardcoded answers
- route logic that is secretly tuned to one dataset identity
- manually embedded solutions for named benchmark cases

### Required benchmark strata

For each major route, maintain:

- **naive baseline**
- **classical strong baseline**
- **ecosystem-integrated strong baseline**
- **Relaytic baseline**
- **Relaytic improved / dojo-enhanced variant**

### Required artifacts

- `benchmark_gap_report.json`
- `reference_approach_matrix.json`
- `benchmark_parity_report.json`
- `gold_standard_comparison.json`

### Required behavior

- benchmark results must separate:
  - zero-feedback Relaytic
  - feedback-improved Relaytic
  - dojo-improved Relaytic
- benchmark reports must say whether Relaytic matched, exceeded, or still trails strong reference approaches
- benchmark cases must include both gold-standard methods and gold-standard decision situations

---

## 23. Drift, OOD, monitoring, and observability

### Required artifacts
- `drift_report.json`
- `telemetry_summary.json`
- `fallback_events.json`

Every specialist action, handoff, disagreement, retry, fallback, approval gate, and branch decision must be traced.

---

## 24. Continuous data operations, retraining, and promotion

Relaytic must support continuous usefulness when new data arrives.

### Required lifecycle decisions
For new data or scheduled refreshes, the system must be able to decide between:
- score only
- monitor only
- recalibrate only
- partial refresh
- full retrain
- shadow candidate
- promote candidate
- rollback champion

### Required triggers
- schedule-based retraining
- drift-triggered retraining
- schema-change-triggered review
- freshness SLA breach
- champion degradation
- new-label availability

### Champion / candidate management
The system must maintain:
- current champion
- shadow candidate
- promoted candidate history
- rollback lineage

### Focus-aware lifecycle rule
Lifecycle choices must consider the resolved focus profile.
Examples:
- value-focused runs may prefer threshold recalibration before a full retrain
- reliability-focused runs may demand stronger calibration checks before promotion
- efficiency-focused runs may reject a heavier candidate even if score improves modestly

### Required artifacts
- `dataset_version.json`
- `schema_version.json`
- `retrain_decision.json`
- `promotion_decision.json`
- `rollback_decision.json`
- `champion_vs_candidate.json`
- `freshness_report.json`

### Acceptance criteria
- the system can compare incoming data against prior data versions
- retraining is not always the default; recalibration or defer may be chosen
- promotion decisions cite both technical evidence and mandate impact
- rollback path exists and is testable

---


## 24A. Data connectivity and live-data architecture

Relaytic must separate online/live paths from offline training paths.

### Supported ingestion modes

- **snapshot mode**
  - CSV
  - Parquet
  - local directories
  - DuckDB tables

- **table mode**
  - SQLite
  - DuckDB
  - Postgres
  - warehouse/lake snapshots

- **stream mode**
  - append-only event stream
  - queue / bus consumer
  - webhook-style event ingestion

### Architecture rule

Live data must not automatically trigger full autonomous search on every event.

Instead:
- live data feeds scoring, monitoring, freshness checks, schema checks, drift checks, and OOD checks
- offline windows or snapshots feed retraining, recalibration, challenger evaluation, and promotion decisions

### Required behaviors

- snapshot mode must be the default for personal-computer use
- table mode must support scheduled retraining from stable snapshots
- stream mode must support monitoring-first workflows
- stream inputs must be able to materialize bounded training snapshots for later retraining cycles
- the data layer should maintain a local source graph so Relaytic can reason about nearby snapshots, tables, event histories, and join candidates without mutating upstream systems
- Relaytic should be able to say when a missing signal is more likely to be solved by pulling or collecting additional local data than by widening search on the current snapshot
- entity-history and point-in-time reasoning should become explicit future inputs to route selection, challenger design, and decision usefulness

### Required artifacts

- `ingestion_mode.json`
- `data_source_contract.json`
- `training_snapshot_manifest.json`
- `source_graph.json`
- `join_candidate_report.json`
- `data_acquisition_plan.json`

---


## 24B. Dojo mode and guarded self-improvement

Relaytic may include a **dojo mode** for deliberate self-improvement.

Dojo mode is not normal operation.
It is an explicit mode where Relaytic tries to improve its own methods.

### Purpose

In dojo mode, Relaytic may try to improve:

- route-selection priors
- feature-strategy priors
- focus heuristics
- challenger heuristics
- completion heuristics
- lifecycle heuristics
- search-space design
- optional new model-family proposals
- optional new architecture proposals

### Inputs dojo mode may use

- strong benchmark datasets
- trusted internal datasets
- high-quality post-hoc labels
- strong reference models
- strong integrated ecosystem routes
- validated feedback
- prior failure cases
- gold decision cases

### Rules for dojo mode

- dojo mode must be explicit opt-in
- dojo outputs must remain quarantined until validated
- dojo improvements must be benchmarked before they affect default behavior
- dojo must produce reusable method updates, not hidden magic
- architecture proposals must be treated as experimental until they earn promotion

### Required outputs

- `dojo_session.json`
- `dojo_hypotheses.json`
- `dojo_results.json`
- `dojo_promotions.json`
- `architecture_proposals.json`

### Why this matters

Relaytic should be able to become better over time, not only by retraining models on new data, but by improving how it thinks and searches.

---

## 24C. Mission control and change attribution

Relaytic should expose a professional mission-control surface over its artifact graph and runtime state.

This is not cosmetic UI work.
It is the operator and agent surface for understanding why the lab took the path it took.
The thin version of this should arrive early as the first real control center, and later slices should deepen it rather than restarting the UI story from scratch.

### Mission-control questions

- which branches were explored and why
- what changed because memory was available
- what changed because semantic intelligence was enabled
- what changed because research retrieval was enabled
- what changed because feedback or outcomes altered priors
- which current uncertainty blocks progress most
- which next experiment is expected to pay off per unit effort

### Required behavior

- mission control must consume the same canonical runtime and artifact state as CLI, MCP, and reports
- the first usable mission-control/control-center surface should ship before later dojo/search/polish slices and then be extended by those later slices whenever operator-visible behavior changes
- branch structure and confidence views must remain inspectable and exportable for external agents
- change attribution must stay explicit instead of collapsing all improvements into a generic "Relaytic got smarter" story

### Required artifacts

- `mission_control_state.json`
- `branch_dag.json`
- `confidence_map.json`
- `change_attribution_report.json`

---

## 25. Artifacts contract

### New run directory layout

```text
artifacts/run_<timestamp>/
  manifest.json
  policy_resolved.yaml
  hardware_profile.json
  resource_assumptions.json
  budget_resolution.json
  execution_backend_profile.json
  device_allocation.json
  distributed_run_plan.json
  scheduler_job_map.json
  checkpoint_state.json
  execution_strategy_report.json
  lab_mandate.json
  work_preferences.json
  run_brief.json
  data_origin.json
  domain_brief.json
  task_brief.json
  context_sources.json
  provenance_map.json
  research_query_plan.json
  research_source_inventory.json
  research_brief.json
  method_transfer_report.json
  benchmark_reference_report.json
  external_research_audit.json
  semantic_task_request.json
  semantic_task_results.json
  intelligence_mode.json
  llm_routing_plan.json
  debate_trace.json
  verifier_report.json
  reflection_memory.json
  dataset_profile.json
  run_state.json
  stage_timeline.json
  completion_decision.json
  benchmark_gap_report.json
  reference_approach_matrix.json
  benchmark_parity_report.json
  gold_standard_comparison.json
  dataset_version.json
  schema_version.json
  freshness_report.json
  domain_memo.json
  independent_profiles/
    profile_a.json
    profile_b.json
    disagreement_report.json
    resolved_understanding.json
  memory_retrieval.json
  plan_archetype.json
  historical_analogs.json
  feedback_intake.json
  feedback_validation.json
  feedback_effect_report.json
  feedback_casebook.json
  outcome_observation_report.json
  decision_policy_update_suggestions.json
  policy_update_suggestions.json
  route_prior_updates.json
  decision_world_model.json
  intervention_policy_report.json
  decision_usefulness_report.json
  value_of_more_data_report.json
  source_graph.json
  join_candidate_report.json
  data_acquisition_plan.json
  method_compiler_report.json
  compiled_challenger_templates.json
  compiled_feature_hypotheses.json
  compiled_benchmark_protocol.json
  plan.json
  alternatives.json
  hypotheses.json
  objective_hypotheses.json
  focus_debate.json
  focus_profile.json
  optimization_profile.json
  objective_tradeoffs.json
  feature_strategy_profile.json
  trajectory_constraint_report.json
  feasible_region_map.json
  extrapolation_risk_report.json
  rejected_routes.json
  hpo_plan.json
  hpo_trace.json
  threshold_tuning_report.json
  experiment_priority_report.json
  marginal_value_of_next_experiment.json
  integration_plan.json
  external_route_results.json
  registry_backend_config.json
  backend_export_report.json
  handoff_bundle_manifest.json
  trust_boundary_report.json
  integration_trust_modes.json
  redaction_report.json
  workflow_spec.json
  workflow_run_report.json
  experiment_graph.json
  handoff_graph.json
  pareto_front.json
  leaderboard.csv
  ablation_report.json
  belief_update.json
  data_recommendations.json
  voi_report.json
  alignment_trace.json
  tradeoff_decisions.json
  mandate_update_suggestions.json
  recalibration_decision.json
  retrain_decision.json
  promotion_decision.json
  rollback_decision.json
  champion_vs_candidate.json
  mission_control_state.json
  branch_dag.json
  confidence_map.json
  change_attribution_report.json
  dojo_session.json
  dojo_hypotheses.json
  dojo_results.json
  dojo_promotions.json
  architecture_proposals.json
  best_model/
    model.pkl
    model_config.json
    feature_manifest.json
    feature_version.json
  challenger_models/
  reports/
    summary.md
    technical_report.md
    model_card.md
    risk_report.md
    decision_memo.md
    interoperability_report.md
    lifecycle_report.md
  diagnostics/
    health_report.json
    backup_manifest.json
    restore_report.json
    diagnostics_bundle_manifest.json
    calibration_report.json
    uncertainty_report.json
    abstention_report.json
    drift_report.json
    stability_report.json
    slice_report.json
    offline_online_consistency_report.json
  logs/
    agent_trace.jsonl
    telemetry_summary.json
    fallback_events.json
    execution.log
```

---

## 26. Reporting redesign

### Required reports
- `summary.md`
- `technical_report.md`
- `model_card.md`
- `risk_report.md`
- `decision_memo.md`
- `interoperability_report.md`
- `lifecycle_report.md`

The decision memo must explicitly show:
- what the mandate preferred
- what the Focus Council preferred
- what the evidence preferred
- what compromise was selected
- whether strong-LLM reasoning materially changed the recommendation

The lifecycle report must explicitly show:
- whether the recommendation is one-off, deployable, recalibration-only, retrain, promote, or rollback
- why that lifecycle decision was chosen
- how the resolved focus profile influenced that lifecycle decision
- whether the completion layer believes the system is done for now or should continue
- how the resolved focus profile influenced feature strategy

---

## 27. CLI redesign

### New primary CLI

```bash
relaytic run \
  --data-path data.csv \
  --target target \
  --execution-mode autonomous \
  --operation-mode session \
  --policy configs/policies/default.yaml \
  --goal best_robust_pareto_front
```

### Required subcommands

```bash
relaytic mandate init
relaytic mandate edit
relaytic mandate show
relaytic context init
relaytic context edit
relaytic context show
relaytic intelligence show
relaytic onboard
relaytic doctor
relaytic backup create
relaytic backup verify
relaytic restore
relaytic status
relaytic investigate
relaytic hypothesize
relaytic plan
relaytic experiment
relaytic challenge
relaytic ablate
relaytic audit
relaytic retrain
relaytic promote
relaytic rollback
relaytic report
relaytic serve
relaytic retrain
relaytic promote
relaytic rollback
relaytic replay
relaytic tool-server
relaytic status
```

---

## 28. API redesign

### Endpoints

- `POST /mandate/init`
- `POST /mandate/update`
- `GET /mandate`
- `POST /context/init`
- `POST /context/update`
- `GET /context`
- `GET /intelligence`
- `POST /intelligence/update`
- `POST /semantic-task`
- `POST /onboard`
- `GET /health`
- `POST /backup`
- `POST /restore`
- `GET /status`
- `GET /execution-profile`
- `POST /investigate`
- `POST /hypothesize`
- `POST /plan`
- `POST /run`
- `POST /challenge`
- `POST /ablate`
- `POST /audit`
- `POST /retrain`
- `POST /promote`
- `POST /rollback`
- `POST /report`
- `POST /predict`
- `POST /status`
- `POST /recommend-data`
- `GET /runs/{run_id}`
- `GET /runs/{run_id}/artifacts`
- `GET /health`

---

## 29. Agent interoperability layer

### Required exported capabilities

- `configure_mandate`
- `configure_context`
- `configure_intelligence_mode`
- `discover_local_llm_backends`
- `validate_local_llm_setup`
- `run_structured_semantic_task`
- `get_run_status`
- `get_execution_profile`
- `attach_reference_docs`
- `investigate_dataset`
- `propose_hypotheses`
- `generate_plan`
- `run_experiments`
- `run_challenger_branch`
- `run_ablation_suite`
- `audit_model`
- `compare_models`
- `recommend_additional_data`
- `generate_data_collection_plan`
- `produce_decision_memo`
- `produce_lifecycle_decision`
- `package_model`
- `summarize_run`
- `inspect_hardware_and_resolve_budgets`
- `materialize_training_snapshot`

### Current bounded implementation baseline

The current bounded implementation for this vision layer is Slice 08A.

It already provides:

- a Relaytic-owned MCP server boundary rather than vendor-specific wrappers as the source of truth
- local `stdio` serving for subprocess-based hosts
- local `streamable-http` serving for connector-style clients
- a compact health tool plus live local interoperability self-checks
- checked-in wrapper surfaces for Claude, Codex/OpenAI skills, OpenClaw, and ChatGPT connector guidance
- explicit host activation/discovery state so Relaytic can say which ecosystems can call it immediately and which still need connector registration

The current exported tool surface covers the implemented MVP and slice-level flows:

- `relaytic_server_info`
- `relaytic_run`
- `relaytic_show_run`
- `relaytic_get_status`
- `relaytic_predict`
- `relaytic_intake_interpret`
- `relaytic_investigate_dataset`
- `relaytic_generate_plan`
- `relaytic_run_evidence_review`
- `relaytic_review_completion`
- `relaytic_review_lifecycle`
- `relaytic_show_lifecycle`
- `relaytic_doctor`
- `relaytic_integrations_show`

Current safety posture:

- local-first by default
- checked-in host bundles must stay secret-free and machine-path-free
- public HTTPS exposure of `/mcp` is optional and must sit behind trusted TLS/auth controls
- host wrappers remain thin and must not become a second source of truth

Current activation truth:

- Claude can discover the project-local MCP and agent surfaces from the repository, then asks for one approval step
- Codex/OpenAI local skill environments can discover the checked-in repository skill surface
- OpenClaw-style workspace discovery can use `skills/relaytic/SKILL.md`
- ChatGPT still requires explicit connector registration against a public HTTPS `/mcp` endpoint

External agents must be able to provide mandate context, run briefs, data origin notes, domain briefs, and reference documents. They should also be told clearly in docs and tool cards:
- which inputs are optional
- which are advisory
- how provenance is handled
- how free-form notes are translated into structured artifacts
- when Relaytic will ask clarifying questions instead of guessing
- how retrain/promotion tools are expected to be used
- how session vs daemon mode works
- how live data should flow into monitoring vs retraining
- what intelligence modes exist and when strong LLM use is beneficial
- what the minimum local LLM baseline is for and how to disable it
- how to configure a local LLM backend
- how Relaytic discovers and health-checks local LLMs
- how external candidate-generation and registry backends fit into Relaytic
- which platform notes matter for macOS users

---


## 29A. Portable workflow specifications

Relaytic should support a portable workflow/program format for repeatable inference-engineering procedures.

Possible internal names:
- `RelaySpec`
- `RelayFlow`

### Purpose

Portable workflow specifications should let users and external agents define repeatable workflows for:

- investigation
- focus selection
- challenger review
- lifecycle review
- benchmark runs
- dataset triage

### Required properties

A workflow specification should be:
- human-readable
- machine-runnable
- versioned
- exportable
- inspectable
- bounded

### Why this matters

This makes Relaytic:
- easier to automate
- easier to reproduce
- easier to share
- easier to call from other agent systems

### Required artifacts

- `workflow_spec.json`
- `workflow_run_report.json`

---

## 30. UI and operator experience

### Mandatory initial flow

Before the first autonomous/guided run, the UI must present a setup flow where the user can:

- enable or disable the mandate system
- choose mandate influence mode
- fill in or edit long-term lab mandate
- fill in or edit work preferences
- fill in or edit run-specific brief
- optionally provide data origin notes
- optionally provide a domain brief
- optionally provide a task brief
- optionally upload reference documents
- choose whether external literature retrieval is allowed when policy permits it
- choose intelligence mode if strong LLMs are available
- choose whether to use no local LLM, a minimum local semantic helper, or a stronger available model
- launch local-LLM setup help if desired
- optionally review or override focus priorities if the user wants manual influence
- review what is binding vs advisory
- choose whether agents may challenge soft preferences
- see examples of how these settings affect the run

### Screens
- mandate onboarding / setup
- context onboarding / setup
- mandate editor
- context editor
- intelligence mode panel
- local-LLM setup assistant
- local-LLM health/status panel
- focus council view
- focus profile editor
- feature strategy view
- run status board
- current stage panel
- hardware / execution backend panel
- cluster/distributed job panel
- onboarding wizard
- doctor / health view
- backup / restore view
- domain memo
- independent profile comparison
- hypothesis view
- plan view
- experiment progress
- challenger comparison
- ablation findings
- leaderboard
- audit view
- lifecycle view
- champion vs candidate view
- final report view
- serve / inference view
- tool-server status view

### Behavior
- user can change mandate settings at any time
- changes to mandate settings must be versioned and logged
- the UI must clearly explain the difference between:
  - lab mandate
  - work preferences
  - run brief
  - data origin / domain brief / task brief
  - influence modes
  - advisory context vs binding constraints
- the UI must show retraining, recalibration, promotion, and rollback decisions clearly
- the UI must explain that context is optional and the system can continue without it
- the UI must explain deterministic floor vs LLM-amplified ceiling
- the UI must explain what the minimum local LLM baseline does and does not do
- the UI must show when strong-LLM reasoning is active and on which phases
- the UI must show the current good-enough contract, including active metric gates, benchmark posture, review posture, and why Relaytic believes the run passed or failed it
- the UI must show configured budget, consumed budget, and remaining budget for runtime, autonomy, and search-related work, plus whether the current limits came from operator input, lab profile, or derived hardware defaults
- the UI must distinguish lab-operating profiles from operator profiles and explain that those overlays shape posture rather than artifact truth
- the UI must explain how to set up a local LLM backend
- the UI must surface detected local backends and upgrade suggestions when available
- the UI must explain what the Focus Council is doing and which objectives are currently prioritized
- the UI must explain how the current focus changes feature engineering proposals
- the UI must explain trust modes for integrations and why some results are advisory-only
- the UI must surface engine-slot choices when relevant
- the UI must always show the current workflow stage and whether the system believes it is done yet

### Acceptance criteria
- first-run UX includes mandate setup
- first-run UX includes optional context setup
- mandate editing is always accessible
- context editing is always accessible
- the user can toggle mandate on/off
- the user can change influence mode mid-session before a new run
- the user can change intelligence mode before a new run
- the user can switch the minimum local LLM baseline on, off, or to a custom configured local model before a new run
- the user can run local-LLM discovery and health checks before a new run
- the user can inspect and optionally override the resolved focus profile before a new run
- the UI explains how mandate settings affect autonomous behavior
- the UI explains what would need to improve for the system to continue versus stop
- the UI explains lifecycle decisions when new data arrives

---


## 30A. Operator onboarding, health, backup, restore, and diagnostics

Relaytic must feel operable, not just architecturally impressive.

### Required operator surfaces

Relaytic should support first-class operator commands and UI flows for:

- onboarding
- doctor / health
- status
- backup
- restore
- diagnostics bundle export

### Example command surfaces

Target commands should include:

```bash
relaytic onboard
relaytic doctor
relaytic status
relaytic backup create
relaytic backup verify
relaytic restore
relaytic demo
```

### Why this matters

A system this ambitious must be:
- easy to set up
- easy to validate
- easy to recover
- easy to move to another machine
- easy to diagnose when something breaks

### Required artifacts

- `health_report.json`
- `backup_manifest.json`
- `restore_report.json`
- `diagnostics_bundle_manifest.json`

### Required behavior

- onboarding should guide first-run setup
- health should validate package, backend, storage, and optional intelligence surfaces
- backup should include manifest and integrity checks
- restore should verify compatibility before applying

---


## 30B. Run Status Board and professional graph surfaces

Relaytic should expose a clear status board for operators and external agents.

### The status board should answer

- what stage are we in right now?
- what was the most recent completed stage?
- are we done for now?
- if not, why not?
- what is the next recommended action?

### Required visual surfaces

At minimum, Relaytic should provide:

#### Search progress graph
- best score over trials
- robust score over trials
- challenger wins and losses

#### Completion graph
- estimated upside from more search
- estimated upside from more data
- estimated upside from recalibration
- estimated upside from retraining

#### Promotion graph
- champion vs candidate across:
  - score
  - calibration
  - latency
  - fragility

#### Drift graph
- feature drift
- prediction drift
- missingness drift
- freshness trend

### Required behavior

- the status board must be visible in the UI
- the same state must be queryable by external agents through API/tool surfaces
- graphs should update at checkpoint boundaries, not just at run end

---

## 31. Demo, showcase, and adoption layer

### Required demos

- **Golden tabular demo**
  - includes mandate setup and full pipeline

- **Golden time-series demo**
  - includes challenger branch, ablation findings, uncertainty outputs, and retraining decision

- **Plugin / tool-server demo**
  - includes passing a run brief, mandate context, or optional domain brief/reference docs

- **Continuous-data demo**
  - shows new data arrival
  - dataset version comparison
  - recalibrate vs retrain vs promote decision
  - champion/candidate visualization

- **Intelligence amplification demo**
  - compares deterministic-only vs strong-LLM-assisted investigation on the same messy dataset
  - shows better hypothesis generation and synthesis without changing deterministic evaluation mechanics

- **Local-LLM setup demo**
  - shows Relaytic detecting a missing local LLM
  - guiding the user through optional setup
  - validating the backend
  - suggesting an upgrade when a stronger permissible local model is available

- **Integrated-route demo**
  - shows Relaytic using an external candidate-generation route
  - challenging the external winner
  - producing a better justified final recommendation

- **Focus Council demo**
  - shows the same dataset under different resolved focus profiles
  - demonstrates how value, reliability, or efficiency priorities change metric choice, thresholds, and final recommendation

- **Operator safety demo**
  - shows onboarding, health checks, backup verification, and restore validation

- **Completion and status-board demo**
  - shows stage-by-stage progress
  - displays whether Relaytic is done yet or should continue
  - demonstrates how completion decisions change after challenger and audit steps

- **Feedback-learning demo**
  - shows user or agent feedback being validated
  - demonstrates a later similar run changing policy or priors because the feedback proved reusable

- **Benchmark-parity demo**
  - compares Relaytic against strong reference approaches on a general benchmark case
  - shows whether Relaytic matched, exceeded, or still trails the reference approach

- **Dojo mode demo**
  - shows Relaytic trying to improve its own strategy on strong data
  - keeps improvements quarantined until validation

- **Accelerated local execution demo**
  - shows Relaytic selecting CPU vs GPU vs local-cluster-style execution appropriately
  - explains why the chosen execution profile is faster and still policy-aligned

- **Semantic task demo**
  - shows a bounded semantic job interpreting labels or domain notes with schema-constrained output

### Required showcase assets
- architecture diagram
- specialist handoff diagram
- mandate layer diagram
- knowledge/context layer diagram
- lifecycle / promotion diagram
- screenshot set or GIFs of the UI
- sample report bundle
- example artifact tree
- benchmark summary figure
- one “why the model was chosen” visual
- one “more data vs more search” visual
- one “mandate vs evidence” visual
- one “recalibrate vs retrain vs promote” visual
- one “deterministic vs LLM-amplified reasoning” visual
- one “local-LLM setup and upgrade suggestion” visual
- one “external route challenged by Relaytic” visual
- one “Focus Council changed the optimization plan” visual
- one “engine slot swapped, judgment stayed stable” visual
- one “operator onboarding / doctor / backup” visual
- one “are we done yet?” status-board visual
- one “validated feedback changed the next similar run” visual
- one “Relaytic vs reference approach” visual
- one “dojo improvement promoted after validation” visual
- one “execution profile chosen from available local hardware” visual

---

## 32. LLM and agent contract redesign

Each agent emits one structured action validated against Pydantic models.

Example action types include:
- `inspect_dataset`
- `flag_suspicious_column`
- `choose_route`
- `choose_split`
- `propose_hypothesis`
- `queue_experiments`
- `request_calibration`
- `request_uncertainty_wrap`
- `request_robustness_check`
- `request_additional_data`
- `challenge_incumbent`
- `run_ablation_suite`
- `argue_mandate_override`
- `request_recalibration_only`
- `request_retrain`
- `request_promotion`
- `request_rollback`
- `stop_with_recommendation`

The system must remain fully functional without any LLM.
When a strong LLM is available, Relaytic should route it to the semantically difficult phases rather than letting it replace deterministic execution.

---

## 33. Benchmark harness

### Required ablations
- no multi-agent disagreement vs multi-agent disagreement
- no challenger vs challenger enabled
- no mandate vs mandate enabled
- advisory vs weighted mandate
- no run memory vs run memory
- no ablation judge vs ablation judge
- ungrounded vs grounded context mode
- no transfer HPO vs transfer HPO
- recalibration-only vs full retrain when drift appears
- deterministic-only vs LLM-amplified mode on messy context tasks
- none vs minimum-local-LLM vs strong-LLM semantic interpretation quality
- raw external-route winner vs Relaytic-challenged final recommendation

---

## 34. Testing expansion

### Unit tests
- route inference
- split selection
- focus selection
- focus-shaped feature strategy selection
- completion decision logic
- run-state / stage tracking
- engine slot resolution
- policy resolution
- stop rules
- artifact manifests
- calibration utilities
- conformal utilities
- CQR utilities
- disagreement resolution
- handoff schemas
- run-memory retrieval
- value-of-information estimation
- mandate interpretation
- influence mode behavior
- context ingestion and provenance
- dataset versioning
- retraining decision logic
- promotion and rollback logic
- threshold tuning behavior
- hardware autodetection and budget resolution
- per-cycle watchdog behavior
- intelligence mode routing behavior
- verifier gating behavior
- minimum local LLM baseline routing behavior
- local-LLM backend discovery behavior
- local-LLM health-check behavior
- semantic-task schema behavior
- engine-slot resolution behavior
- trust-mode behavior
- macOS/Apple Silicon package smoke coverage where feasible

### Integration tests
- mandate setup -> context setup -> focus selection -> investigate
- investigate -> hypothesize
- hypothesize -> plan
- plan -> execute
- execute -> challenge
- challenge -> ablate
- ablate -> audit
- audit -> report
- retrain -> promote
- promote -> rollback
- tool-server capability exposure

### End-to-end tests
- one mandate-aware autonomous run
- one grounded run with uploaded context docs
- one ungrounded run with no context provided
- one lifecycle run with new data arrival
- one daemon-mode cycle sequence with per-cycle stopping
- one strong-LLM-assisted run with schema-constrained actions
- one minimum-local-LLM-assisted run on a label-heavy messy dataset
- one local-LLM setup-assistant flow
- one Focus Council-guided run with different objective outcomes
- one focus-shaped feature-strategy run comparing two objective profiles
- one semantic-task bounded run
- one onboarding/doctor/backup run
- one completion-decision run showing continue vs stop states

### Failure tests
- conflict between mandate and evidence
- conflicting context sources
- schema change on new data
- missing feature at inference time
- candidate promotion rejected by policy
- hardware budget fallback on low-resource machine profile
- invalid LLM action rejected by verifier
- minimum local LLM disabled path still works cleanly
- discovered backend rejected if health check fails
- focus profile conflicts with mandate and is surfaced correctly
- advisory-only integration result is surfaced but not blindly trusted
- stage visibility remains accurate across multi-step runs

### Regression tests
Golden artifact snapshots for:
- `alignment_trace.json`
- `decision_memo.md`
- `retrain_decision.json`
- `promotion_decision.json`

---

## 35. CI and repo health

Add:
- mandate-mode behavior test
- lifecycle decision behavior test
- promotion/rollback smoke test
- hardware profile resolution smoke test
- daemon-cycle watchdog smoke test
- intelligence-mode routing smoke test
- verifier smoke test
- macOS-friendly base install smoke test

---

## 36. Migration plan

### Phase 1
- policy schema
- execution modes
- mandate objects and influence modes
- optional context objects and provenance layer
- unknown-domain memo
- independent inspect and disagreement artifacts
- plan object
- experiment registry
- artifact contract
- compatibility shims

### Phase 2
- scout
- scientist
- strategist
- builder
- challenger
- ablation judge
- steward
- memory keeper
- lifecycle manager
- coordinator loop
- schema-validated actions

### Phase 3
- calibration
- conformal uncertainty
- CQR
- stability checks
- slice analysis
- drift report
- abstention outputs
- ablation engine
- value-of-information estimates
- alignment traces and tradeoff logging
- HPO backend layer
- threshold tuning
- intelligence amplification layer
- debate/verifier/reflection flows

### Phase 4
- unified CLI
- local API
- MCP/tool server
- Streamlit app
- mandate setup UX
- optional context setup UX
- local serve mode
- lifecycle screens

### Phase 5
- benchmark harness
- ablations
- optional frontier backends
- run memory priors
- retraining / promotion / rollback flows
- packaging and distribution surfaces
- docs rewrite
- end-to-end demos

---

## 37. Implementation rules for Codex

1. Do not remove local-first defaults.
2. Do not make remote APIs required.
3. Preserve existing commands where practical using compatibility wrappers.
4. Prefer additive refactors over destructive rewrites.
5. Keep deterministic behavior where already present.
6. Add tests with each major subsystem.
7. Persist every important decision as an artifact.
8. Do not introduce heavyweight dependencies into the core package unless behind optional extras.
9. Maintain clean separation between:
   - mandate
   - context
   - investigation
   - hypotheses
   - planning
   - execution
   - challenge
   - ablation
   - evaluation
   - lifecycle
   - reporting
   - memory
   - interoperability
10. The system must work without LLMs.
11. The system must support local LLM enhancement without becoming LLM-dependent.
12. Challenger behavior is required in autonomous mode.
13. Additional-data recommendation is required in guided/autonomous modes.
14. Every important handoff must be logged.
15. The system must generate evidence, not just metrics.
16. Judgment-oriented tools must be exposed for external agents.
17. Mandate behavior must be switchable and inspectable.
18. Context ingestion must remain optional.
19. Strong-LLM use must remain optional.
20. A minimum local LLM baseline may be offered but must remain optional and replaceable.
21. Relaytic should actively help users and external agents set up local LLM backends when requested.
22. The UI must make mandate options visible and editable from the start.
23. The UI must present optional context inputs from the start and explain that they are optional.
24. The UI must present intelligence modes clearly when capable LLMs are available.
25. Focus selection must be explicit, inspectable, and able to shape planning and tuning materially.
26. Continuous-data handling, retraining, recalibration, promotion, and rollback must be first-class.
27. Distribution must be Python-package-first, Docker-second, and optional-native-hotspot-only.
28. macOS and Linux must be treated as first-class targets.
29. Codex must implement the plan through bounded slices with explicit status and migration tracking.
30. External systems may be integrated where they are strongest, but Relaytic must keep final judgment and challenger authority.

### Required deliverables from Codex

- refactored package structure
- new policy system
- new execution mode system
- mandate system with influence modes
- optional context/knowledge layer with provenance
- intelligence amplification layer
- optional minimum local LLM baseline abstraction
- unknown-domain memo layer
- independent inspect/disagreement layer
- new plan object and planner
- hypothesis subsystem
- Focus Council and focus-profile subsystem
- experiment graph and handoff graph
- challenger subsystem
- ablation engine and belief-update engine
- run-memory subsystem
- HPO backend layer
- uncertainty, calibration, abstention, and CQR modules
- additional-data recommendation subsystem
- value-of-information subsystem
- alignment trace and tradeoff logging
- lifecycle subsystem for new-data handling
- champion/candidate registry and promotion flows
- standardized artifacts
- unified CLI
- local API and tool-server
- expanded tests
- rewritten README and docs
- branding integrated across README, CLI help text, UI copy, and demo assets
- one complete local demo path
- one polished tabular golden demo
- one polished time-series golden demo
- one external-agent integration demo path
- one continuous-data lifecycle demo
- one daemon-mode monitoring/retraining demo
- showcase screenshots/GIFs and demo assets

---

## 38. README rewrite requirements

The README must present the system as:

- local-first
- autonomous but steerable
- multi-specialist
- focus-aware
- mandate-aware
- hypothesis-driven
- evidence-driven
- inference-first
- memory-guided
- policy-aware
- lifecycle-aware
- intelligence-amplified when available
- artifact-rich
- consumable by other agents

### Required README sections

1. What Relaytic is
2. Why local-first
3. Why multiple specialists
4. Why mandate-aware autonomy matters
5. Why this is different from plain AutoML
6. Execution modes
7. Mandate setup and influence modes
8. Optional knowledge/context inputs
9. Supported routes
10. Hypothesis-driven workflow
11. Evidence and challenger science
12. Hardware-aware operation and effort tiers
13. Intelligence amplification modes
14. Minimum local LLM baseline
15. Local-LLM setup and backend discovery
16. Continuous retraining and promotion
17. Live-data architecture
18. Ecosystem integrations and philosophy
19. Focus Council and objective selection
20. Focus-shaped feature engineering
21. Engine slots and replaceable subsystems
22. Trust boundaries and safe integration
23. Golden demos
23. Example outputs
24. Artifact structure
25. Installation and packaging options
26. Policy examples
27. Tool-server / plugin usage
28. Benchmarks
29. Development and tests

### Required differentiator sentence

The README must contain a line close to:

> Relaytic is not an AutoML wrapper. It is a local-first inference engineering system that investigates data, forms competing hypotheses, runs challenger science, quantifies uncertainty, preserves mandate-aware user intent, can optionally ground itself in expert context, recommends missing data, and exposes its judgment as reusable tools for other agents.

### Required lifecycle sentence

The README must also contain a line close to:

> Relaytic does not stop at choosing a model; it decides whether new data should trigger monitoring, recalibration, retraining, promotion, or rollback.

> When a strong LLM is available, Relaytic uses it as a cognitive coprocessor for interpretation, critique, planning, and synthesis while keeping execution and verification deterministic.

> Relaytic should be installable as a lightweight Python package, runnable as a Dockerized local stack, and extensible through optional extras rather than a bloated default install.

> Relaytic may optionally use a small local quantized model as a semantic helper for labels, notes, and local conversational UX, but that helper must never be mandatory.

> Relaytic should help users and external agents discover, configure, validate, and optionally upgrade local LLM backends when doing so would materially improve intelligence.

> Relaytic should use what is best for each purpose, integrate strong surrounding systems when useful, and still challenge every apparent winner for a better outcome.

> Relaytic should explicitly debate what the run ought to optimize for instead of assuming every problem should maximize the same score.

> Relaytic should keep major subsystems replaceable, exchange bounded evidence between specialists, and remain operator-safe and trust-explicit as it integrates surrounding systems.

> Relaytic should make it obvious whether it is still searching, already done, blocked on data, or ready for recalibration, retraining, promotion, or rollback.

> Relaytic should accept useful feedback when it can validate it, hold itself to strong benchmark references without hardcoding solutions, and improve itself through a guarded dojo mode rather than hidden drift in behavior.

> Relaytic should use whatever permissible local hardware is available—from laptop CPU to local GPU workstation to local cluster—to execute as fast as possible without abandoning its local-first philosophy.

---


## 38A. Distribution, packaging, and adoption strategy

Relaytic must be easy to install, easy to try, and easy to integrate.
That means install and first-launch UX should be treated as a core product surface, not deferred until the final polish slice.

### Primary distribution strategy

The primary product surface should be a **Python package**.

Reasons:
- easiest adoption path for ML and agent users
- best integration with local notebooks, scripts, and tools
- easiest path for other agents to call Relaytic as a local dependency
- strongest fit for the current ML ecosystem

### Secondary distribution strategy

Relaytic must also provide a **Docker** path for:

- reproducible demos
- UI/API bundles
- CI
- users who do not want to manage Python environments
- known-good dependency packaging

### Performance strategy

Do **not** rewrite the system in another language.

Use:
- Python for the main product
- optional Rust/native extensions later only for clear hotspots

### Packaging requirements

Relaytic must ship with a `pyproject.toml`-first package layout.

Required package surfaces:

- base package: `relaytic`
- console entry point: `relaytic`
- optional extras:
  - `ui`
  - `serve`
  - `llm`
  - `bench`
  - `frontier`
  - `dev`

### Required install paths

#### Minimal install
```bash
pip install relaytic
```

#### Common install
```bash
pip install "relaytic[ui,serve]"
```

#### Power-user install
```bash
pip install "relaytic[llm,bench,frontier]"
```

#### Development install
```bash
uv sync --all-extras
uv run relaytic --help
```


### Platform packaging requirements

Distribution must explicitly support:
- macOS
- Linux

The packaging strategy must:
- keep the base package Mac-friendly
- isolate platform-sensitive dependencies behind extras
- document Apple Silicon notes where relevant
- make Docker a clear fallback for Mac users who do not want native dependency management

### Required Docker surfaces

- `Dockerfile` for reproducible local runtime
- `docker-compose.yml` for full local demo stack when needed
- versioned images for released demo environments
- one lightweight image for CLI/API
- one fuller image for UI/demo workflows if needed

### Repository packaging requirements

The repository must include:

- `pyproject.toml`
- console scripts/entry points
- optional dependency groups
- lockfile or reproducible environment spec
- minimal install instructions
- Docker instructions
- release packaging notes

### Release strategy

Relaytic should ship through:

- GitHub repo as source of truth
- versioned GitHub Releases
- Python package publishing
- versioned Docker images
- demo assets attached to releases where useful

### Acceptance criteria

- a user can install Relaytic from Python packaging without Docker
- a user can install Relaytic, verify the environment, and reach one coherent local control-center launch path without repository archaeology
- a user can run Relaytic through Docker without setting up Python locally
- extras keep the base install lightweight
- packaging choices do not make heavy optional dependencies mandatory
- the README clearly explains install paths, extras, and Docker options

---

## 39. Definition of done

The transformation is complete when all of the following are true:

1. A user can run one command locally on a CSV and get:
   - mandate setup
   - optional context setup
   - dataset profile
   - domain memo
   - independent specialist interpretations
   - hypotheses
   - plan
   - experiments
   - challenger comparison
   - ablation findings
   - leaderboard
   - calibrated and uncertainty-aware best model
   - additional-data recommendations
   - final report

2. The system supports:
   - manual
   - guided
   - autonomous

3. Every run produces:
   - `policy_resolved.yaml`
   - `lab_mandate.json`
   - `work_preferences.json`
   - `run_brief.json`
   - `dataset_profile.json`
   - `domain_memo.json`
   - independent profile artifacts
   - `plan.json`
   - `hypotheses.json`
   - `experiment_graph.json`
   - `handoff_graph.json`
   - `ablation_report.json`
   - `belief_update.json`
   - `alignment_trace.json`
   - `tradeoff_decisions.json`
   - `leaderboard.csv`
   - summary and technical reports
   - uncertainty, calibration, abstention, and drift artifacts
   - `data_recommendations.json`
   - `voi_report.json`

4. Continuous operation produces:
   - `dataset_version.json`
   - `schema_version.json`
   - `retrain_decision.json`
   - `promotion_decision.json`
   - `rollback_decision.json`
   - `champion_vs_candidate.json`

5. The system works fully offline by default.

6. Tests cover the new mandate, investigate, planner, builder, challenger, ablation judge, steward, lifecycle manager, and auditor flow.

7. Another local agent can invoke the system through a stable tool contract.

8. The UI forces the user to see and configure mandate options before the first guided/autonomous run.

9. The UI also presents optional context inputs before the first guided/autonomous run and explains that the system can continue without them.

10. If the user supplies no limits, Relaytic detects local hardware and resolves conservative budgets automatically.

11. The repository includes at least:
   - one polished tabular golden demo
   - one polished time-series golden demo
   - one external-agent / tool-server demo
   - one continuous-data lifecycle demo

---

## 40. First implementation sprint

### Sprint 1
- add policy schema
- add execution mode support
- add mandate objects and influence modes
- add optional context objects and provenance layer
- create unknown-domain memo
- create independent inspect outputs
- create `plan.json`
- create `hypotheses.json`
- create experiment registry
- refactor current analyst/modeler flow into `scout` + `scientist` + `strategist` + `builder`
- standardize artifact directory
- add compatibility shims
- update CLI with `mandate`, `context`, `investigate`, `hypothesize`, `plan`

### Sprint 2
- add experiment graph
- add handoff graph
- add challenger subsystem
- add ablation engine
- add steward
- add calibration
- add conformal uncertainty
- add CQR
- add stability checks
- add `summary.md`, `technical_report.md`, `model_card.md`, `risk_report.md`, `decision_memo.md`
- add `data_recommendations.json`
- add `voi_report.json`
- add `alignment_trace.json`
- add `tradeoff_decisions.json`

### Sprint 3
- add API
- add MCP/tool server
- add Streamlit app
- add mandate setup UX
- add optional context setup UX
- add serve mode and local monitoring
- add benchmark harness
- add optional frontier backends
- add run memory priors
- add HPO backend layer
- add lifecycle subsystem
- add hardware autodetection and watchdog layer
- add intelligence amplification layer
- add minimum local LLM baseline abstraction
- add Python packaging surfaces and extras
- add Docker surfaces
- add golden demos
- add showcase assets
- rewrite README for fast onboarding and live demo use
- integrate Relaytic branding across docs, UI, CLI, and demo assets

---


## 40A. Codex execution protocol and context-window-aware implementation

The transformation plan must be implementable by Codex incrementally.

Relaytic is too large for a safe one-shot rewrite. The implementation protocol must explicitly respect limited context windows and reduce integration risk.

### Core rule

Codex must **not** attempt to implement the whole plan in one pass.

Instead, Codex must work through bounded slices that:
- fit comfortably within context
- compile or at least type-check in isolation where possible
- preserve architecture contracts
- leave the repository in a consistent intermediate state

### Required implementation artifacts

Codex must create and maintain:

- `ARCHITECTURE_CONTRACT.md`
- `IMPLEMENTATION_STATUS.md`
- `MIGRATION_MAP.md`
- `docs/build_slices/`
- `docs/build_slices/phase_01.md`
- `docs/build_slices/phase_02.md`
- `docs/build_slices/phase_03.md`
- additional slice files as needed

### Meaning of these files

#### `ARCHITECTURE_CONTRACT.md`
Defines the stable contracts that later slices must obey:
- artifact names and locations
- core schemas
- policy object shape
- mandate object shape
- lifecycle decision object shape
- package/module boundaries
- CLI/API naming contracts

#### `IMPLEMENTATION_STATUS.md`
Tracks:
- completed slices
- pending slices
- known temporary shims
- known broken/non-final surfaces
- next recommended slice

#### `MIGRATION_MAP.md`
Maps:
- old modules to new modules
- old CLI commands to new CLI commands
- temporary compatibility wrappers
- removal plan for legacy shims

#### `docs/build_slices/*`
Each slice file must be self-contained and small enough for Codex to execute reliably.

A slice file should include:
- goal
- affected files
- contracts touched
- tests to add/update
- migration risks
- done criteria

### Required implementation slicing strategy

Codex must implement in this order:

#### Slice group 1: contracts and scaffolding
- package scaffolding
- architecture contract
- policy schema
- artifact manifest contract
- basic CLI shell
- compatibility wrappers

#### Slice group 2: mandate and context foundation
- mandate objects
- context objects
- provenance objects
- first-run UI forms
- resolved config writing

#### Slice group 3: intake and interpretation
- raw user/agent intake
- free-form mandate/context translation
- semantic mapping to dataset schema and artifact fields
- optional clarification-question generation plus proceed-with-assumptions behavior
- optional bounded local-LLM interpretation

#### Slice group 4: investigation and planning
- scout/scientist/strategist baseline
- dataset profile
- domain memo
- plan/hypothesis artifacts
- lightweight deterministic routes

#### Slice group 5: experimentation and evidence
- strategist translation of focus profile
- experiment registry
- challenger
- ablation engine
- audit outputs
- reports

#### Slice group 6: intelligence amplification
- intelligence modes
- minimum local LLM baseline abstraction
- backend discovery and setup guidance
- LLM routing
- debate/verifier/reflection
- schema-constrained action layer

#### Slice group 7: lifecycle operations
- dataset/schema versioning
- retrain/recalibrate/promotion/rollback decisions
- champion/candidate registry
- lifecycle reports

#### Slice group 8: distribution and polish
- packaging extras
- Docker surfaces
- macOS/Linux install notes
- integration adapters
- release assets
- README/demo polish
- tool-server examples

### Required slice constraints

Each Codex slice should:
- touch as few subsystems as practical
- avoid unnecessary renames
- preserve tests or add new ones
- update `IMPLEMENTATION_STATUS.md`
- update `MIGRATION_MAP.md` if boundaries move
- avoid introducing large temporary duplication unless justified

### Contract-first rule

Before implementing large subsystems, Codex should freeze and write the schema/contracts first.

Examples:
- `plan.json` schema before planner expansion
- `alignment_trace.json` schema before steward logic
- `retrain_decision.json` schema before lifecycle manager logic
- `intelligence_mode.json` schema before LLM routing logic

### Integration rule

At the end of each slice:
- repository must remain internally coherent
- compatibility shims must still work where promised
- artifact names must remain stable unless the migration docs are updated
- tests or smoke checks for the touched surface must exist

### Anti-patterns Codex must avoid

- full-repo big-bang rewrites
- changing package structure and semantics in the same slice without migration notes
- adding heavy optional dependencies into the base install
- introducing LLM dependencies into deterministic core paths
- silently changing artifact contracts without updating contract docs

### Acceptance criteria

- a future Codex run can resume from `IMPLEMENTATION_STATUS.md` without re-understanding the whole repo
- each slice is understandable independently
- the final system emerges from additive slices that fit together cleanly
- the architecture contract stays stable enough to prevent drift across slices

---

## 41. Codex prompt to paste

```text
Read RELAYTIC_TRANSFORMATION_PLAN_COMPLETE.md and implement it incrementally.

Constraints:
- Keep local-first defaults and existing runtime policy.
- Remote APIs must remain explicit opt-in only.
- The system must work without any LLM.
- Preserve existing functionality where possible through compatibility wrappers.
- Refactor incrementally, not as a destructive rewrite.
- Keep deterministic behavior where it already exists.
- Add tests for every new subsystem.
- Keep the core dependency-light.
- Put frontier backends behind optional extras.

Main goals:
1. Replace the public two-agent framing with a multi-specialist architecture:
   scout, scientist, strategist, builder, challenger, ablation_judge, auditor, steward, memory_keeper, lifecycle_manager, synthesizer, broker.
2. Add execution modes: manual, guided, autonomous.
3. Add mandate-aware autonomy with:
   - lab_mandate
   - work_preferences
   - run_brief
   - influence modes
   - alignment traces
   - tradeoff logging
4. Add an optional context/knowledge layer with:
   - data_origin
   - domain_brief
   - task_brief
   - reference document ingestion
   - provenance tracking
   - optional external retrieval gated by policy
   The system must still work when no context is provided.
5. Add a Focus Council that debates whether the run should prioritize accuracy, business value, reliability, efficiency, interpretability, sustainability, or a blend.
6. Add unknown-domain investigation and disagreement resolution before planning.
7. Add a policy-aware planning layer that chooses route, metric, split strategy, feature plan, candidate families, uncertainty plan, and stop criteria.
7. Generalize the system into routes:
   tabular_regression, tabular_classification, time_series_forecasting, time_aware_prediction, surrogate.
8. Add a hypothesis-driven autonomous loop:
   configure mandate -> configure optional context -> investigate -> resolve understanding -> hypothesize -> plan -> execute batch -> challenge -> ablate -> audit -> decide next step.
9. Add multi-fidelity search, branch promotion, challenger branches, Pareto-front selection, and explicit HPO backend support.
10. Add experiment graph and handoff graph artifacts.
11. Add run-memory priors and historical analog retrieval.
12. Add calibration, conformal uncertainty, CQR, abstention, robustness, slice analysis, drift reports, and value-of-information estimates.
13. Add additional-data recommendation as a first-class artifact.
14. Add structured ablation science and belief updates.
15. Add a lifecycle subsystem for:
   - new data arrival
   - scheduled retraining
   - recalibration-only decisions
   - promotion
   - rollback
   - champion/candidate tracking
16. Add hardware autodetection, conservative default budget resolution, effort tiers, watchdog behavior, and explicit session vs daemon operation modes.
17. Add an intelligence amplification layer with intelligence modes, debate/verifier/reflection flows, and strong-LLM routing for semantically difficult phases.
18. Add an optional minimum local LLM baseline abstraction for lightweight semantic help on personal computers.
19. Add local-LLM backend discovery, setup guidance, health checks, and upgrade suggestions.
20. Add external-system integrations where useful, including candidate-generation routes and optional registry/tracing backends, while keeping Relaytic’s final judgment layer intact.
21. Standardize artifacts and reports.
22. Add a unified CLI:
   mandate, context, investigate, hypothesize, plan, experiment, challenge, ablate, audit, retrain, promote, rollback, report, serve, replay, tool-server.
23. Add a real local API and a local MCP/tool server.
24. Add a local Streamlit operator UI.
25. The UI must show mandate options initially, require the user to configure them before the first guided/autonomous run, and let the user edit them later.
26. The UI must also show optional context inputs initially, explain that they are optional, and let the user edit them later.
27. The UI must show intelligence modes when capable LLMs are available and explain deterministic floor vs LLM-amplified ceiling.
28. The UI must show session vs daemon mode, detected hardware assumptions when limits are absent, and explain how live data feeds monitoring vs retraining.
29. The UI must show the current good-enough contract and why Relaytic believes the run passed or failed it.
30. The UI must show configured versus consumed search, runtime, and autonomy budget, plus whether current limits came from user input, lab profile, or hardware-derived defaults.
31. The UI must distinguish lab-operating profiles from operator profiles and state that those overlays shape posture rather than deterministic truth.
32. Add benchmark harness and ablations.
33. Rewrite README to match the new architecture.
34. Add Python-package-first distribution with:
   - pyproject-based packaging
   - console entry points
   - optional extras
   - lightweight base install
Add Docker-second distribution with:
   - Dockerfile
   - docker-compose where useful
   - demo-friendly reproducible local stack
Implement through bounded slices that maintain:
   - ARCHITECTURE_CONTRACT.md
   - IMPLEMENTATION_STATUS.md
   - MIGRATION_MAP.md
   - docs/build_slices/*
Integrate the Relaytic brand and the descriptor `The Relay Inference Lab` consistently across docs, CLI help, UI copy, tool-server descriptions, and demo assets.
```
