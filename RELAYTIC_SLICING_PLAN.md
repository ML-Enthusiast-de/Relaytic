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
  strongest fit: late-stage research work after the post-Slice-15 academy track, especially a future Slice 17 representation-engine track

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
- **paper-release benchmark path**
  later AML/paper claims must end in a release-freeze bundle that names relevant public benchmark families, records proxy or blocked status honestly, and ties every claim to reproducible artifacts
- **paper-competitiveness path**
  every publishable benchmark must separate smoke, baseline, competitive, and release budgets; weak first-pass rows are allowed as honest baselines or failure analysis only, never as headline model-quality evidence without budgeted SOTA-candidate reruns, leakage audits, split checks, HPO/search-budget accounting, adapter/version capture, and validation-only threshold selection before final test evaluation

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
- **academy-growth path**
  once Slices 16B through 16F land, one candidate capability should be visible from replay through shadow, arena decision, and final promotion or retirement without altering authoritative run truth before promotion

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
35. Slice 15A
36. Slice 15B
37. Slice 15C
38. Slice 15D
39. Slice 15E
40. Slice 15F
41. Slice 15G
42. Slice 15H
43. Slice 15I
44. Slice 15J
45. Slice 15K
46. Slice 15L
47. Slice 15M
48. Slice 15N
49. Slice 15O
50. Slice 15P
51. Slice 15Q
52. Slice 15R-A
53. Slice 15S
54. Slice 15T
55. Slice 15U
56. Slice 15V
56A. Slice 15V-A
57. Slice 15W
58. Slice 15X
59. Slice 15Y
60. Slice 15Z
60A. Slice 15Z-R
61. Paper Track P0 - freeze and commit the 15Z-R baseline
62. Paper Track P1 - legacy public-surface cleanup
63. Paper Track P2 - paper thesis and claim contract
64. Paper Track P3 - benchmark dataset registry and access manifest
65. Paper Track P4 - PaySim-style temporal benchmark runner
66. Paper Track P5 - Elliptic graph benchmark loader and provenance
67. Paper Track P6 - strong tabular baseline suite
67A. Paper Track P6-A - PaySim competitive rerun and publishability gate
68. Paper Track P7 - graph baseline suite
69. Paper Track P8 - AMLSim and Elliptic2 blocked-or-supported track
69A. Paper Track P8-A - Elliptic2 modern-benchmark recovery pilot
69B. Paper Track P8-B - Elliptic2 competitive and robustness suite
69C. Paper Track P8-C - modern subgraph reference parity and leakage-resistant cohort protocol
69D. Paper Track P8-D - paper thesis narrowing and alternative evidence decision
70. Paper Track P9 - operational AML evaluation layer
71. Paper Track P10 - reproducible paper table generator
72. Paper Track P11 - paper draft and figure pack
73. Paper Track P12 - external dry run and clean-clone proof
74. Paper Track P13 - claim-safe paper release and attention pack
74A. Paper Track P14 - final arXiv source bundle and clean release candidate
74B. Paper Track P15 - measured system-evaluation proof pack
75. Slice 16
76. Slice 16A
77. Slice 16B
78. Slice 16C
79. Slice 16D
80. Slice 16E
81. Slice 16F
82. Slice 17
83. Slice 18

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
- Slice 11A turns Relaytic's benchmark and challenger story into something much more real for operators and technical reviewers by letting users attach an incumbent model and forcing Relaytic to beat it honestly
- Slice 11B is now implemented and gives Relaytic a real operator-facing control center plus a low-friction install/onboarding path before dojo and later frontier slices expand the lab
- Slice 11C is now implemented and makes that control center legible on first contact by surfacing modes, capabilities, safe next actions, bounded stage reruns, and starter questions even before a user has discovered the assist surface manually
- Slice 11D is now implemented and makes first contact far less confusing by adding guided onboarding, real terminal mission-control chat, explicit capability reasons, and a clearer dashboard-versus-chat split
- Slice 11E is now implemented and makes that onboarding surface explicit for both humans and external agents by surfacing role-specific handbooks directly from mission control, chat, and checked-in host notes
- Slice 11F is now implemented and makes the experience much more demo-ready by surfacing a guided walkthrough, explicit mode explanations, and stuck-recovery guidance directly from mission control, chat, and the handbook stack
- Slice 11G is now implemented and makes that first-contact UX much more forgiving by adding adaptive onboarding capture, visible chat session state, explicit analysis-first versus governed-run routing, lightweight local semantic rescue for messy human input, and full-install helper provisioning
- Slice 12A should come after dojo because periodic awareness, innovation watching, and bounded background follow-up are much safer once self-improvement stays quarantined and promotion rules already exist
- Slice 12B should come before Slice 13 and the Slice 15 mission-control expansion because wider search and full trace-backed mission control both need one canonical trace substrate plus explicit agent/security evaluation before they are believable
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
- Slices 15A through 15F are the initial model-competitiveness track and are now shipped, but the benchmark rerun proved Relaytic still needs a second performance-recovery track before the academy begins
- Slice 15G is now implemented and freezes objective truth, split health, and benchmark-metric integrity so later performance work stops optimizing broken comparisons
- Slice 15H is now shipped because stronger family coverage only matters once Relaytic knows exactly what it is optimizing and how the benchmark is being judged
- Slice 15I is now implemented and gives Relaytic a staged search-budget doctrine, explicit probe/race/finalist/post-fit artifacts, and a clean separation between lean test budgets and real operator or benchmark budgets
- Slice 15J is now implemented and restores serious temporal work with event-preserving blocked splits, richer lag/delta/rolling/seasonal feature ladders, honest ordinary-versus-lagged baselines, and sequence shadow trials that stay non-live until they beat strong lagged baselines
- Slice 15K is now implemented and turns calibration strategy selection, threshold search, review-budget optimization, abstention posture, and operating-point explanations into first-class performance work on top of the corrected task, family, search, and temporal stack
- Slice 15L is now implemented and closes the pre-academy recovery track by turning benchmark trust, trace identity, protocol conformance, leakage posture, and public-claim safety into one explicit gate
- Slice 15M is now implemented and closes the competitiveness-gap bridge by widening multiclass and rare-event specialization, surfacing adapter activation explicitly, tightening temporal benchmark recovery, partitioning benchmark claims into dev versus holdout posture, and auditing benchmark generalization so the academy does not start from benchmark-shaped blind spots
- Slice 15N should land before the academy because Relaytic needs one hard AML thesis instead of reading like a generic structured-data system with no wedge
- Slice 15O should follow because AML is a graph, entity, and subgraph problem as much as a row-classification problem
- Slice 15P is now implemented and makes analyst-review burden, queue quality, and case-packet usefulness first-class AML outputs
- Slice 15Q is now implemented and makes stream posture, weak-label risk, delayed-outcome alignment, and recalibration triggers explicit instead of treating AML as a static supervised problem
- Slice 15R-A is now implemented and aligns the AML proof pack across targeted tests, benchmark CLI/show, run summary, assist, mission control, control docs, and public-claim gates
- Slice 15S is now implemented and makes the AML story obvious through one public-safe flagship demo bundle instead of expecting reviewers to infer value from many artifacts
- Slice 15T is now implemented and makes analyst-hour value, review-capacity tradeoffs, case-packet completeness, and operational overclaim guards first-class AML outputs
- Slice 15U is now implemented and deepens AML baselines and ablations so the system can prove which capabilities actually changed outcomes
- Slice 15V is now implemented and adds raw graph/subgraph ingestion, graph provenance, subgraph task manifests, graph claim scope, and public graph benchmark cataloging so public graph AML work no longer depends only on flattened snapshots
- Slice 15V-A is now implemented and gives beginners plus external agents one no-lost guidance layer, one safe context-pack export, and one always-available status explanation before Relaytic adds still more artifact families
- Slice 15W is now implemented and adds delayed-label, positive-unlabeled, threshold-drift, and time-window proof before production-shaped temporal claims expand
- Slice 15X is now implemented and reframes Relaytic runs as evaluation environments with scorecards for messy task detection, unsafe steering rejection, incumbent challenge, alert-queue optimization, drift recovery, public-safe claims, benchmark-environment readiness, and model/environment score separation
- Slice 15Y is now implemented and makes first contact demo-led with an AML thesis page, product story, paper benchmark runbook, README proof path, and handbook demo commands
- Slice 15Z is now implemented and adds module-split evidence, deterministic repo credibility reports, public-surface inventory, retained extraction boundaries, and benchmark cleanup debt before the paper freeze
- Slice 15Z-R is now implemented and freezes relevant benchmark/release evidence into a rerunnable pack with claim boundaries, reproducibility attestation, and hard-performance-claim blocking until real paper evidence exists
- Paper Track P0 through P15 now come before Academy work because the current freeze pack deliberately blocked hard AML and SOTA claims; Relaytic first cleaned public surfaces, ran relevant benchmark tracks, challenged weak first-pass rows with competitive leakage-safe budgets, generated real numeric evidence, drafted a claim-safe paper, proved a clean paper-smoke path, produced a claim-safe P13 paper release pack, produced a P14 arXiv-compatible source bundle, and then added P15 measured user/agent handoff evidence before expanding into capability evolution
- Paper Track P0 is now implemented and records the frozen 15Z-R baseline, verification commands, and hard-claim blocked posture before any paper benchmark implementation starts
- Paper Track P1 is now implemented and cleans the paper-facing public surface, records the retained compatibility boundary, and adds Relaytic aliases for legacy API/tool names
- Paper Track P2 is now implemented and freezes the claim-gated AML evaluation-environment thesis, research questions, contribution story, metric doctrine, related-work seed, and claim taxonomy before benchmark implementation starts
- Paper Track P3 is now implemented and freezes dataset source/access posture, license notes, local file expectations, hashes for present local fixtures, split contracts, blocked reasons, and no-auto-download policy before benchmark runners start
- Paper Track P4 is now implemented and runs the full PaySim-style chronological temporal benchmark with validation-only threshold selection, fixed test evaluation, review-budget/fixed-FPR metrics, supporting-only paper posture, and hard AML/SOTA performance claims still blocked
- Paper Track P5 is now implemented and inspects the raw Elliptic graph bundle, freezes graph provenance and temporal split artifacts, records unknown-label scope, allows only supporting loader/provenance wording, and keeps graph benchmark/SOTA claims blocked before numeric graph baselines run
- Paper Track P6 is now implemented and runs the full PaySim tabular baseline suite under a train-only leakage-safe feature contract with explicit adapter versions, budget tiers, fallback states, and a publishability gate that blocks headline promotion until P6-A
- Paper Track P6-A is now implemented and runs a competitive PaySim rerun with audited prior-step destination-history features, 14 recorded probe trials, five full-training finalists, validation-only calibration/threshold selection, and a supporting-only publishability pass for validation-selected Extra Trees (`test_pr_auc=0.638773`) while retaining hard-claim blockers before P7
- Slice 16 is the umbrella academy track and should not be treated as one undifferentiated implementation pass; it exists so post-AML capability evolution has one coherent contract
- Slice 16A should start the academy by freezing capability cards and registry truth before replay, hunt, or recruitment logic appears
- Slice 16B should come before any live academy authority because replay packs and shadow mode are the main trust boundary for future capability growth
- Slice 16C should come before hunt-heavy or roster-heavy work because promotion and quarantine logic must be deterministic before Relaytic starts scouting aggressively
- Slice 16D should come after 16C because hunt campaigns should feed the same replay, shadow, and arena pipeline rather than inventing a parallel innovation loop
- Slice 16E should come after the tool-focused academy slices because non-core specialist recruitment and retirement should reuse the same proof pipeline instead of becoming a second roster mechanism
- Slice 16F should close the academy track by turning candidate, shadow, hunt, and promotion truth into one human- and agent-usable surface
- Slice 17 should remain the optional late-stage representation-engine slice and should land after the academy track so Relaytic can first learn to evolve governed capabilities before it experiments with deeper latent representation engines
- Slice 18 should land last as a deliberate consolidation/remediation pass so Relaytic can remove temporary compatibility layers, misleading structure, oversized modules, and stale prototype language after the capability work is complete

## Current execution state

- implemented baseline: Slice 00 through Slice 15Z-R plus Paper Track P0 through P15. Latest named additions include Slice 15R-A AML proof-pack alignment, Slice 15S flagship AML demo-bundle packaging, Slice 15T guarded business-value and analyst-hour proof, Slice 15U strong AML baselines and capability ablations, Slice 15V raw graph/subgraph ingestion, Slice 15V-A no-lost guide/status/context-pack export, Slice 15W temporal weak-label claim gating, Slice 15X AML evaluation-environment scoring, Slice 15Y demo-first public documentation, Slice 15Z repo credibility cleanup, Slice 15Z-R paper/release freeze, Paper Track P0 baseline freeze, Paper Track P1 public-surface cleanup, Paper Track P2 thesis/claim contract, Paper Track P3 dataset registry, Paper Track P4 PaySim temporal benchmark, Paper Track P5 Elliptic graph provenance, Paper Track P6 strong tabular baseline suite, Paper Track P6-A competitive PaySim rerun, Paper Track P7 Elliptic graph baseline suite, Paper Track P8 hard graph-track decisions, Paper Track P8-A Elliptic2 modern recovery pilot, Paper Track P8-B competitive/robustness evidence, Paper Track P8-C reference-parity/cohort gate, Paper Track P8-D thesis narrowing, Paper Track P9 operational AML evaluation, Paper Track P10 reproducible paper table generation, Paper Track P11 claim-linted paper draft generation, Paper Track P12 external dry-run proof, Paper Track P13 claim-safe paper release pack, Paper Track P14 final arXiv source bundle, and Paper Track P15 measured system-evaluation proof pack.
- next execution target: Slice 16A
- latest pulse slice: Slice 12A
- latest trace-and-safety follow-on: Slice 12B
- latest handoff-and-learnings follow-on: Slice 12D
- latest search-and-execution follow-on: Slice 13
- latest release-and-packaging follow-on after Slice 13: Slice 13A
- latest runtime-and-permission slice: Slice 13B
- latest background-and-resume slice: Slice 13C
- latest mission-control-and-proof slice: Slice 15
- next planned paper follow-on: none before Slice 16A; P15 leaves only human author metadata, final PDF review, and clean tag-target confirmation before upload
- next planned academy follow-on: Slice 16A, after P15 closed the upload-source, release-candidate, and measured system-evaluation gaps
- late optional representation follow-on after the academy track: Slice 17
- final planned cleanup follow-on after Slice 17: Slice 18
- after Slice 13, every later slice that changes operator-visible behavior, major artifact families, install/dependency posture, or long-running runtime behavior must extend the same mission-control, onboarding, dojo-visibility, differentiated-handoff, durable-learnings, workspace-continuity, result-contract, iteration-planning, search-controller, release-safety, permission-mode, and background-job surfaces instead of treating UI as a separate late-polish track
- the canonical product-spec pack for Slice 12D, Slice 15, the model-competitiveness track, the performance-recovery track, the AML pivot track, and the academy follow-ons now lives under `docs/specs/` and should be treated as normative for future implementation, including [model_competitiveness_contract.md](docs/specs/model_competitiveness_contract.md), [performance_recovery_contract.md](docs/specs/performance_recovery_contract.md), [aml_frontier_contract.md](docs/specs/aml_frontier_contract.md), [capability_academy_contract.md](docs/specs/capability_academy_contract.md), [mission_control_contract.md](docs/specs/mission_control_contract.md), [handoff_result_migration.md](docs/specs/handoff_result_migration.md), [learnings_migration_contract.md](docs/specs/learnings_migration_contract.md), and [external_agent_continuation_contract.md](docs/specs/external_agent_continuation_contract.md) for already-shipped and future mission control, model competitiveness, performance recovery, AML, academy, handoff, learnings, and external-agent continuation surfaces

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
- public-safe first-contact experience

Load-bearing improvement:

- Relaytic should stop requiring first-time demo audiences to infer the product shape. Mission control, chat, and the handbook stack should explain the shortest useful demo flow, what each major surface is for, and what to do when the next step is unclear.

Human surface:

- humans should be able to open mission control and immediately find a demo flow, mode explanations, stuck guidance, and a public-safe walkthrough
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
- a separate demo walkthrough must exist for public-safe demos

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

Implemented.

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

## Slice 15A - Canonical task contract, rare-event taxonomy, and benchmark-vs-deploy separation

Goal:
- freeze one canonical task/problem contract early
- unify task typing across intake, planning, modeling, benchmark, and explanation
- separate benchmark competitiveness from deployment readiness

Required outputs:
- `task_profile_contract.json`
- `target_semantics_report.json`
- `metric_contract.json`
- `benchmark_mode_report.json`
- `deployment_readiness_report.json`
- `benchmark_vs_deploy_report.json`
- `dataset_semantics_audit.json`

Minimum proof:

- one labeled rare-event dataset remains supervised classification instead of drifting into anomaly detection
- one multiclass string-label dataset stays multiclass through planning, training, benchmark, and explanation surfaces
- one offline benchmark run is reported as competitive while deployment readiness remains conditional for separate reasons

## Slice 15B - Model registry expansion and adaptive architecture routing

Goal:
- expand the model registry beyond the narrow current family set
- choose architectures because they fit the task, not because they are already implemented
- keep sequence models gated behind real sequence evidence

Required outputs:
- `architecture_registry.json`
- `architecture_router_report.json`
- `candidate_family_matrix.json`
- `architecture_fit_report.json`
- `family_capability_matrix.json`
- `architecture_ablation_report.json`

Minimum proof:

- one mixed-type or categorical-heavy dataset prefers a categorical-aware family when available
- one multiclass dataset routes to a non-default family because the registry judged it a better fit
- one static table explicitly rejects sequence-family routing with an auditable explanation

## Slice 15C - Budgeted HPO, early stopping, and deeper portfolio loops

Goal:
- replace shallow fixed-variant search with explicit bounded HPO
- add real search spaces, early stopping, threshold tuning, and warm starts
- make deeper loops explicit instead of hidden in hard-coded variants

Required outputs:
- `hpo_budget_contract.json`
- `architecture_search_space.json`
- `trial_ledger.jsonl`
- `early_stopping_report.json`
- `search_loop_scorecard.json`
- `warm_start_transfer_report.json`
- `threshold_tuning_report.json`

Minimum proof:

- one family uses a real search space instead of a fixed three-variant sweep
- one search loop stops because of plateau or budget logic rather than arbitrary variant exhaustion
- one rerun can warm-start from prior family evidence

## Slice 15D - Paper-grade benchmark harness and benchmark rigor

Status:
- implemented

Goal:
- turn benchmark work into a reproducible paper-facing harness
- record rerun variance, ablations, and claim boundaries explicitly
- keep benchmark truth separate from deployability truth

Required outputs:
- `paper_benchmark_manifest.json`
- `paper_benchmark_table.json`
- `benchmark_ablation_matrix.json`
- `rerun_variance_report.json`
- `benchmark_claims_report.json`
- `benchmark_vs_deploy_report.json`

Minimum proof:

- one full benchmark table is renderable from artifacts without manual cleanup
- one rerun-variance report shows stability across repeated runs
- one benchmark claim report states clearly where Relaytic is below reference and why

## Slice 15E - Execution DAG, freshness contracts, and artifact reuse

Goal:
- make recompute scope explicit
- avoid heavy reruns when inputs did not change
- support deeper search and wider benchmark packs through reuse

Required outputs:
- `artifact_dependency_graph.json`
- `freshness_contract.json`
- `recompute_plan.json`
- `materialization_cache_index.json`
- `invalidation_report.json`

Minimum proof:

- one no-op review path reuses heavy upstream artifacts instead of rerunning them
- one changed input invalidates only the correct downstream slices
- one recompute plan is human- and agent-inspectable before execution

## Slice 15F - Research-imported architecture candidates and shadow trials

Goal:
- let Relaytic learn promising model families from publications, web research, and adapter discovery
- keep those families in replay and shadow mode until they prove themselves
- bridge into the later academy track without opening uncontrolled self-modification

Required outputs:
- `architecture_candidate_registry.json`
- `method_import_report.json`
- `shadow_trial_manifest.json`
- `shadow_trial_scorecard.json`
- `candidate_quarantine.json`
- `promotion_readiness_report.json`

Minimum proof:

- one externally sourced architecture remains shadow-only because proof is weak
- one externally sourced architecture becomes promotion-ready after replay and shadow evidence
- one explanation surface answers why a paper-inspired architecture was not yet used live

## Slice 15G - Objective contracts, split correctness, and metric-truth alignment

Goal:
- canonical optimization-objective contract
- split diagnostics and temporal fold health
- benchmark metric-materialization truth
- fail-closed benchmark prechecks

Required outputs:
- `optimization_objective_contract.json`
- `objective_alignment_report.json`
- `split_diagnostics_report.json`
- `temporal_fold_health.json`
- `metric_materialization_audit.json`
- `benchmark_truth_precheck.json`

Minimum proof:

- one benchmark run aligns family-selection, calibration, threshold, benchmark, and deployment objectives explicitly
- one temporal classification benchmark avoids zero-positive validation or test folds or is blocked explicitly
- one benchmark bundle fails closed because the claimed comparison metric is unavailable
- one explanation surface answers why Relaytic optimized one metric but reported another without contradiction

## Slice 15H - First-class competitive family stack

Goal:
- stronger first-class family coverage
- categorical-aware routing
- multiclass and rare-event specialization
- graceful optional-adapter activation

Required outputs:
- `family_registry_extension.json`
- `family_readiness_report.json`
- `family_eligibility_matrix.json`
- `family_probe_policy.json`
- `categorical_strategy_report.json`
- `family_specialization_report.json`

Minimum proof:

- one mixed-type benchmark considers a categorical-aware family before generic numeric boosting when the adapter is available
- one small-data classification case considers a small-data specialist family when available
- one multiclass benchmark gets a materially broader eligible family set than the current path
- one no-adapter environment still falls back cleanly to the deterministic floor

## Slice 15I - Portfolio search engine and serious budget doctrine

Goal:
- staged probe/race/finalist search
- serious search-budget doctrine
- multi-fidelity pruning
- explicit stop reasons

Required outputs:
- `search_budget_envelope.json`
- `probe_stage_report.json`
- `family_race_report.json`
- `finalist_search_plan.json`
- `multi_fidelity_pruning_report.json`
- `portfolio_search_scorecard.json`
- `search_stop_reason.json`

Minimum proof:

- one benchmark profile gives multiple materially different families non-trivial probe budgets before finalist selection
- one finalist receives deeper follow-up budget than losing families
- one low-budget profile still runs a staged search and reports which deeper work was skipped
- one test profile can shrink budgets without mutating default operator or benchmark profile contracts

## Slice 15J - Temporal engine and time-aware competitiveness

Goal:
- temporal structure detection
- rolling and grouped temporal evaluation
- strong lagged temporal baselines
- honest sequence shadow trials

Required outputs:
- `temporal_structure_report.json`
- `temporal_feature_ladder.json`
- `rolling_cv_plan.json`
- `temporal_split_guard_report.json`
- `sequence_shadow_scorecard.json`
- `temporal_baseline_ladder.json`
- `temporal_metric_contract.json`

Minimum proof:

- one occupancy-style temporal classification benchmark retains positives in validation and test or is blocked explicitly
- one temporal regression benchmark materializes its claimed comparison metric correctly
- one temporal dataset shows a lagged baseline beating a naive non-temporal baseline
- one sequence candidate is compared against a strong lagged baseline and remains shadow-only when it loses

## Slice 15K - Calibration, thresholds, and decision optimization

Goal:
- calibration strategy selection
- threshold search by objective family
- review-budget-aware operating points
- abstention-aware decision optimization

Required outputs:
- `calibration_strategy_report.json`
- `operating_point_contract.json`
- `threshold_search_report.json`
- `decision_cost_profile.json`
- `review_budget_optimization_report.json`
- `abstention_policy_report.json`

Minimum proof:

- one rare-event task improves decision posture through threshold or calibration choice without changing the winning family
- one calibration strategy wins for explicit evidence-based reasons
- one review-budget-aware operating point differs from the best raw-score threshold
- one explanation surface can answer why Relaytic chose this threshold and why not a rerun instead

## Slice 15L - Benchmark truth hardening and paper-claim gates

Goal:
- trace-identity conformance
- benchmark-truth audits
- public-claim safety gates
- paper-safe benchmark bundles

Required outputs:
- `trace_identity_conformance.json`
- `benchmark_truth_audit.json`
- `paper_claim_guard_report.json`
- `eval_surface_parity_report.json`
- `benchmark_release_gate.json`
- `dataset_leakage_audit.json`

Minimum proof:

- one trace-identity drift class is eliminated across CLI and MCP
- one benchmark bundle is blocked from paper-safe status because benchmark-truth or protocol gates fail
- one degenerate temporal benchmark is blocked explicitly rather than silently reported
- one clean benchmark bundle is marked safe to cite publicly

## Slice 15M - Competitive specialization and benchmark generalization guards

Goal:
- multiclass specialization
- rare-event specialization
- temporal classification benchmark recovery
- benchmark-pack partitioning
- anti-overfitting claim guards

Required outputs:
- `family_specialization_matrix.json`
- `multiclass_search_profile.json`
- `rare_event_search_profile.json`
- `adapter_activation_report.json`
- `temporal_benchmark_recovery_report.json`
- `benchmark_pack_partition.json`
- `holdout_claim_policy.json`
- `benchmark_generalization_audit.json`

Minimum proof:

- one multiclass task shows a broader family race than the current generic ladder and either improves honestly or stays an explicit miss
- one rare-event task uses an explicit imbalance-aware search profile rather than the generic classification profile
- one temporal classification benchmark becomes claim-safe or is blocked only for legitimate remaining fold/data reasons rather than missing contract fields
- one benchmark run records whether the result came from a `dev` or `holdout` pack
- one audit artifact proves Relaytic did not branch on benchmark dataset identity

## Slice 15N - AML domain contract and flagship pivot

Goal:
- freeze `Relaytic-AML` as the flagship frontier edition of Relaytic
- define one canonical AML domain contract, case ontology, and review-budget contract
- stop treating AML as only a generic rare-event classification variant

Required outputs:
- `aml_domain_contract.json`
- `aml_case_ontology.json`
- `aml_review_budget_contract.json`
- `aml_claim_scope.json`

## Slice 15O - Entity, graph, and typology reasoning

Goal:
- add entity- and graph-aware AML reasoning
- support typology templates and suspicious subgraph evidence
- let casework consume graph evidence instead of row scores only

Required outputs:
- `entity_graph_profile.json`
- `counterparty_network_report.json`
- `typology_detection_report.json`
- `subgraph_risk_report.json`
- `entity_case_expansion.json`

## Slice 15P - Analyst review optimization and casework

Goal:
- make analyst-review economics first-class
- rank alerts under explicit review budgets
- produce machine-readable case packets

Required outputs:
- `alert_queue_policy.json`
- `alert_queue_rankings.json`
- `analyst_review_scorecard.json`
- `case_packet.json`
- `review_capacity_sensitivity.json`

## Slice 15Q - Streaming drift, weak labels, and continual AML learning

Goal:
- support temporal AML posture under weak labels and delayed outcomes
- make drift-triggered recalibration and threshold updates explicit
- keep streaming evaluation audit-safe

Required outputs:
- `stream_risk_posture.json`
- `weak_label_posture.json`
- `delayed_outcome_alignment.json`
- `drift_recalibration_trigger.json`
- `rolling_alert_quality_report.json`

## Slice 15R - AML flagship benchmark, demo, and paper pack

Goal:
- turn the AML pivot into public-safe and paper-safe proof
- maintain one AML benchmark pack, one holdout claim policy, and one flagship demo pack
- force honest failure reporting on AML misses

Required outputs:
- `aml_benchmark_manifest.json`
- `aml_holdout_claim_report.json`
- `aml_demo_scorecard.json`
- `aml_public_claim_guard.json`
- `aml_failure_report.json`

## Slice 15R-A - Finish AML proof pack alignment

Goal:
- accepted as implemented
- keep docs, status files, CLI output, run summary, assist, mission control, tests, and public-claim gates aligned
- prevent future drift that would let Relaytic treat AML proof artifacts as shipped when the proof path is incomplete

Load-bearing improvement:

- Relaytic-AML should be able to rerun PaySim-style and flattened Elliptic-style workloads, materialize the proof pack, and explain which claims are allowed, blocked, or still supporting-only

Human surface:

- humans should see AML proof status, demo status, covered benchmark tracks, and primary remaining failure directly through benchmark and summary surfaces

Agent surface:

- external agents should be able to consume the same proof state from stable JSON fields without parsing markdown

Intelligence source:

- deterministic benchmark manifests, holdout claim policy, benchmark-generalization guards, demo scorecards, release gates, and explicit failure reports

Fallback rule:

- if cross-track coverage, holdout posture, or release gates are incomplete, Relaytic must block broader AML claims and emit a concrete next-step recommendation

Required outputs:
- `aml_benchmark_manifest.json`
- `aml_holdout_claim_report.json`
- `aml_demo_scorecard.json`
- `aml_public_claim_guard.json`
- `aml_failure_report.json`

Minimum proof:

- one PaySim-style workload regression
- one flattened Elliptic-style workload regression
- one cross-track claim-gating regression
- one assist or mission-control regression that surfaces the AML proof posture

## Slice 15S - Flagship AML demo pack

Goal:
- accepted as implemented
- keep Relaytic-AML immediately understandable through one public-safe demo bundle
- preserve the end-to-end story from data to review queue, case packet, operating point, drift posture, benchmark guard, and failure report

Load-bearing improvement:

- Relaytic should be able to create a `relaytic-aml-review-queue` demo bundle from fixture data with no repo archaeology

Human surface:

- humans should get one concise demo report with a run-flow diagram, business-metric table, top case packet, and safe claims

Agent surface:

- external agents should be able to inspect the demo manifest, artifact paths, proof status, and recommended next command from JSON

Intelligence source:

- existing AML graph, casework, stream-risk, benchmark, trace, release-gate, and public-claim artifacts

Fallback rule:

- if a richer HTML demo renderer is unavailable, Relaytic must still produce a markdown and JSON demo bundle

Required outputs:
- `aml_demo_bundle_manifest.json`
- `aml_demo_business_metric_table.json`
- `aml_demo_flow_report.md`
- `aml_demo_artifact_index.json`
- `aml_investigation_board.json`

Minimum proof:

- one command creates the demo bundle from fixture data
- the bundle links to the case packet, benchmark guard, public-claim guard, and failure report

## Slice 15T - Business-value metrics and analyst-hour proof

Goal:
- accepted as implemented
- make analyst capacity and business value first-class evaluation criteria
- separate model quality from operational usefulness

Load-bearing improvement:

- Relaytic-AML should report analyst-hours saved, false-positive reduction at fixed recall, recall at review capacity, precision at top-k, and case-packet completeness

Human surface:

- humans should see whether Relaytic improved the actual review queue, not only the predictive score

Agent surface:

- external agents should consume a stable business-value report and know when high AUROC is operationally weak

Intelligence source:

- review-budget contracts, threshold search, casework scorecards, operating-point contracts, and incumbent comparisons

Fallback rule:

- if analyst-hour assumptions are missing, Relaytic must use conservative defaults, label them as assumptions, and avoid hard business-value claims

Required outputs:
- `aml_business_value_report.json`
- `analyst_hour_savings_report.json`
- `review_capacity_metric_report.json`
- `operational_metric_guard.json`

Minimum proof:

- one regression where a model-score improvement fails the operational metric guard
- one incumbent comparison with analyst-capacity tradeoffs

## Slice 15U - Strong AML baselines and ablations

Goal:
- strengthen AML proof through explicit baselines and ablation science
- show what graph, temporal, calibration, threshold, and review-budget machinery contributed

Load-bearing improvement:

- Relaytic-AML should compare against rules, calibrated linear models, tree ensembles, optional boosted trees, lagged temporal baselines, structural graph baselines, and graph-shadow candidates under the same contract

Human surface:

- humans should see one AML ablation matrix that explains which capability mattered

Agent surface:

- external agents should inspect baseline availability, adapter versions, ablation outcomes, and blocked claims through stable artifacts

Intelligence source:

- existing model-family registry, optional adapter readiness, benchmark truth gates, temporal ladder, graph evidence, and casework metrics

Fallback rule:

- optional baselines may be unavailable, but Relaytic must record adapter absence and keep deterministic baselines alive

Required outputs:
- `aml_baseline_matrix.json`
- `aml_ablation_matrix.json`
- `aml_baseline_adapter_report.json`
- `aml_capability_contribution_report.json`
- `aml_benchmark_relevance_scorecard.json`

Minimum proof:

- one AML workload where at least three baseline families run or explicitly fall back
- one ablation that changes a public metric and is surfaced in the benchmark/demo report

Implemented in current baseline through `src/relaytic/aml/baselines.py` and `relaytic aml baselines`.

## Slice 15V - Raw graph and subgraph ingestion

Goal:
- move beyond flattened graph snapshots for AML workloads
- support public graph/subgraph datasets through explicit local loaders and provenance manifests

Load-bearing improvement:

- Relaytic-AML should ingest Elliptic-style multi-file graph bundles and preserve node, edge, feature, time, and label provenance

Human surface:

- humans should see whether a graph workload was raw graph, flattened graph, or subgraph-packaged, and which claims that permits

Agent surface:

- external agents should consume graph-loader manifests and know which files, IDs, and transformations were used

Intelligence source:

- deterministic graph loaders, graph provenance, entity graph construction, typology reasoning, and subgraph packaging

Fallback rule:

- if raw graph files are incomplete, Relaytic must fall back to flattened snapshot mode only when a valid flattened file is provided and must downgrade graph claims

Required outputs:
- `aml_graph_loader_manifest.json`
- `aml_graph_provenance_report.json`
- `aml_subgraph_task_manifest.json`
- `aml_graph_claim_scope.json`
- `aml_public_graph_benchmark_catalog.json`

Minimum proof:

- one raw graph fixture loads into the same graph/entity artifact path
- one incomplete graph bundle fails safely with a precise recovery instruction
- flattened graph compatibility remains labeled as proxy evidence
- the graph catalog separates raw Elliptic-style, flattened Elliptic-style, Elliptic2-style subgraph, and AMLSim-style graph support

## Slice 15V-A - No-lost guide and external context pack

Goal:
- make Relaytic self-orienting for inexperienced humans and external agents
- add one canonical guidance surface that answers what is happening, what is possible now, what is blocked, and how to proceed without requiring artifact literacy
- add a local, redacted context-pack export that a user can hand to an external LLM or agent

Load-bearing improvement:

- Relaytic should provide one safe front door for every product state: no run, onboarding capture, partial run, completed run, benchmark-ready run, blocked environment, stale artifacts, and multi-run workspace continuation
- the guide must synthesize mission control, run summary, assist, handoff, workspace, learnings, benchmark, release-health, and artifact-index truth into plain next actions
- `relaytic status` and guide-style status queries must degrade gracefully when completion artifacts are missing instead of making inexperienced users feel stuck

Human surface:

- humans should be able to run `relaytic guide` or `relaytic guide --run-dir <run_dir>` and immediately see:
  - where Relaytic is now
  - the single best next move
  - what is blocked and why
  - the safe actions available now, with exact commands
  - which reports matter and why
  - what not to claim yet
  - how to export a safe context pack for another LLM
- humans should also be able to ask plain questions through `relaytic guide ask --run-dir <run_dir> --message "<question>"` without knowing whether the answer lives in mission control, assist, handoff, workspace, or benchmark artifacts

Agent surface:

- external agents should consume one JSON-first guide payload instead of guessing which artifact or command to inspect first
- the agent payload must include `current_state`, `state_confidence`, `blocking_items`, `recommended_next_action`, `available_actions`, `safe_commands`, `artifact_shortlist`, `claim_boundaries`, `missing_evidence`, `external_context_pack`, and `starter_questions`
- safe commands must be generated from registered CLI affordances, not free-form prose

Intelligence source:

- deterministic artifact synthesis from mission control, run summary, result contract, handoff, workspace continuity, durable learnings, benchmark truth gates, release-health posture, and doctor output
- optional local LLM assistance may improve phrasing, summarize the deterministic guide bundle, and answer natural-language guide questions, but it must remain rowless/redacted by default and must cite deterministic guide fields rather than inventing commands or claims
- if a local LLM is not configured, the guide must still work fully through deterministic templates and should point to existing local-LLM setup guidance only when the user asks for richer conversational help

Fallback rule:

- if a run directory is missing, guide must fall back to onboarding and install guidance
- if completion, lifecycle, benchmark, or handoff artifacts are missing, guide must report which artifact family is absent and use the strongest available lower-level truth
- if a local LLM is unavailable, disabled, too slow, or fails, guide must emit the deterministic answer and record the local-LLM status without changing recommended actions
- if external context export would include raw rows, secrets, machine-private paths, or unsupported claim text, export must redact or block those fields and write a redaction report

Required outputs:
- `guide_state.json`
- `guide_action_menu.json`
- `guide_artifact_shortlist.json`
- `guide_question_starters.json`
- `guide_local_llm_summary.json`
- `external_llm_context_pack.json`
- `external_llm_context_pack.md`
- `external_llm_artifact_index.json`
- `external_llm_redaction_report.json`

Required commands:
- `relaytic guide`
- `relaytic guide --run-dir <run_dir>`
- `relaytic guide ask --run-dir <run_dir> --message "<question>"`
- `relaytic guide export-context --run-dir <run_dir> --audience external-llm --format json`

Minimum proof:

- no-run onboarding guide explains how to start without requiring repo knowledge
- partial-run guide does not fail when `completion_decision.json` is missing and explains what state it used instead
- completed-run guide points to the human report, agent handoff, result contract, next-run options, and workspace continuation command
- agent JSON guide lists only valid commands and stable artifact paths
- external context export contains no raw data rows and records any redactions
- local-LLM-assisted guide produces a friendlier explanation from the deterministic guide bundle while preserving the same recommended action and claim boundaries as deterministic mode
- local-LLM-unavailable guide falls back cleanly and explains that conversational help is optional

Implementation note:

- implemented in `src/relaytic/guide/` and exposed through `relaytic guide`, `relaytic guide ask`, `relaytic guide export-context`, and graceful `relaytic status` fallback for partial runs

## Slice 15W - Temporal and weak-label upgrade

Goal:
- improve production-shaped AML time and label handling
- make delayed labels, weak labels, threshold drift, and rolling windows explicit

Load-bearing improvement:

- Relaytic-AML should evaluate delayed-label windows, positive-unlabeled posture, threshold stability, and recalibration choices under ordered data

Human surface:

- humans should see whether Relaytic recommends retraining, recalibration, threshold reset, or more delayed-outcome observation

Agent surface:

- external agents should consume time-window scorecards and weak-label guards without reinterpreting raw rows

Intelligence source:

- temporal engine, stream-risk posture, weak-label posture, delayed-outcome alignment, rolling alert-quality reports, and threshold-search artifacts

Fallback rule:

- if timestamp or delayed-label evidence is missing, Relaytic must keep temporal claims blocked and emit required-data recommendations

Required outputs:
- `aml_delayed_label_eval_report.json`
- `aml_positive_unlabeled_posture.json`
- `aml_threshold_drift_report.json`
- `aml_time_window_scorecard.json`
- `aml_temporal_benchmark_claim_report.json`

Minimum proof:

- one ordered workload produces a threshold-drift decision
- one delayed-label scenario blocks overconfident public claims

Implementation:

- implemented in `src/relaytic/aml/temporal.py` and exposed through `relaytic aml temporal`, run summaries, benchmark surfaces, guide artifact shortlists, and temporal public-claim gates

## Slice 15X - AML evaluation-environment reframe

Status:
- implemented

Goal:
- turn Relaytic runs into explicit evaluation environments for humans and agents
- separate environment behavior from model-score behavior

Load-bearing improvement:

- Relaytic should score environment tasks such as messy task detection, unsafe steering rejection, incumbent challenge, alert-queue optimization, drift recovery, and public-safe claim generation

Human surface:

- humans should see one environment scorecard that explains whether Relaytic behaved well under realistic workflow pressure

Agent surface:

- external agents should be able to run or inspect environment tasks non-interactively

Intelligence source:

- trace/eval artifacts, assist/control artifacts, benchmark guards, incumbent comparisons, casework, stream-risk posture, and public-claim gates

Fallback rule:

- if an environment task cannot run, Relaytic must report it as incomplete rather than silently treating model success as environment success

Required outputs:
- `aml_eval_environment_manifest.json`
- `aml_environment_scorecard.json`
- `aml_workflow_task_matrix.json`
- `aml_environment_failure_report.json`
- `aml_benchmark_environment_scorecard.json`

Minimum proof:

- one environment scorecard includes both a model-quality task and a workflow-safety task
- one unsafe steering task remains rejected with trace-backed evidence
- implemented in `src/relaytic/aml/environment.py` and exposed through `relaytic aml environment`, run summaries, guide artifact shortlists, and benchmark-environment claim boundaries

## Slice 15Y - Demo-first documentation rewrite

Status:
- implemented

Goal:
- make first contact demo-led instead of roadmap-led
- keep slice history available without making it the main public story

Load-bearing improvement:

- a new reader should understand the AML path, run the demo, inspect the case packet, inspect benchmark/public-claim guards, and inspect trace/evals before learning the full slice history

Human surface:

- README and handbooks should point to one flagship path first

Agent surface:

- agent handbooks should expose one command-first AML demo path and the proof artifacts to inspect

Intelligence source:

- documentation structure, product-story artifacts, and proof links

Fallback rule:

- if a demo artifact is not generated yet, docs must say which slice generates it instead of pretending it exists

Required outputs:
- `docs/relaytic_ui_frontier_review.md`
- `docs/why_relaytic_aml.md`
- `docs/product_story.md`
- `docs/paper_benchmark_runbook.md`
- README flagship path rewrite
- handbook demo-path updates

Minimum proof:

- README names the next command for a new operator
- docs link to AML proof artifacts without overstating support
- implemented by moving the README first-contact path to `relaytic demo aml-review-queue`, adding the AML thesis/product-story/runbook docs, and documenting demo-only, dev-benchmark, holdout-benchmark, and paper-ready claim boundaries

## Slice 15Z - Pre-Academy repo credibility cleanup

Goal:
- reduce credibility risk before adding capability-academy surface area
- split oversized modules where extraction improves clarity
- remove or document misleading surfaces that make the repo feel accumulated

Load-bearing improvement:

- the codebase should look easier to evaluate and maintain before it grows again

Human surface:

- humans should see a cleaner package map and public-surface inventory

Agent surface:

- external agents should have a clearer import/module boundary map and fewer oversized entrypoints to reason about

Intelligence source:

- deterministic module-size audits, import-boundary checks, public-surface inventory, and targeted regression tests

Fallback rule:

- if a large module cannot be safely split in one pass, Relaytic must document the retained responsibility and the next extraction boundary

Required outputs:
- `pre_academy_repo_audit.json`
- `module_extraction_plan.json`
- `public_surface_inventory.json`
- `module_split_report.json`
- `benchmark_surface_cleanup_report.json`

Minimum proof:

- at least one oversized module is split without changing public behavior
- public CLI and import-boundary smoke tests still pass
- benchmark/demo/public-claim commands are inventoried without stale prototype language

Implemented by:

- extracting AML environment CLI execution helpers into `src/relaytic/ui/aml_environment.py`
- adding `src/relaytic/release_safety/repo_credibility.py`
- materializing `docs/reports/pre_academy_repo_audit.json`, `docs/reports/module_extraction_plan.json`, `docs/reports/public_surface_inventory.json`, `docs/reports/module_split_report.json`, and `docs/reports/benchmark_surface_cleanup_report.json`
- adding `tests/test_cli_slice15z.py` coverage for module split evidence, retained extraction boundaries, import-boundary smoke, and public-surface hygiene

## Slice 15Z-R - Paper benchmark and release freeze

Goal:
- freeze the public benchmark and release evidence after the AML productization track and before Academy work
- make paper/demo claims reproducible, relevant, and claim-gated before Academy work expands scope

Load-bearing improvement:

- Relaytic should emit one paper/release benchmark pack that ties named benchmark families, exact commands, result tables, ablations, operational metrics, public-claim gates, and release-safety evidence into one reproducible bundle

Human surface:

- humans should be able to run one documented benchmark sequence, inspect one paper result table, and see exactly which claims are allowed, blocked, or supporting-only

Agent surface:

- external agents should consume a stable release-freeze manifest and verify benchmark relevance, run completeness, public-claim posture, and reproducibility without scraping prose

Intelligence source:

- 15U through 15Z-R AML artifacts, benchmark truth gates, release-safety scans, demo bundles, and run summaries

Fallback rule:

- if a benchmark is unavailable, login-gated, licensing-unclear, too expensive for the local release profile, or not yet supported by the relevant loader, Relaytic must record the reason and exclude it from hard claims instead of substituting a weaker benchmark silently

Required outputs:
- `paper_release_freeze_manifest.json`
- `aml_relevant_benchmark_catalog.json`
- `paper_benchmark_runbook.md`
- `paper_result_table.json`
- `paper_claim_boundary_report.json`
- `reproducibility_attestation.json`
- `release_attention_pack_manifest.json`

Minimum proof:

- the benchmark catalog includes at least one transaction-fraud temporal track, one graph AML track, one subgraph or synthetic-bank-graph AML track, and one generic supporting structured-data track, each labeled as `dev`, `holdout`, `paper`, `proxy`, or `blocked`
- every public-facing claim cites the exact artifact path and is labeled hard, supporting-only, or blocked
- a clean local rerun regenerates the release-freeze manifest or emits a deterministic blocked-rerun reason

Implemented by:

- adding `src/relaytic/release_safety/paper_freeze.py`
- adding the public command `relaytic release-safety paper-freeze`
- materializing `docs/reports/paper_release_freeze_manifest.json`, `docs/reports/aml_relevant_benchmark_catalog.json`, `docs/reports/paper_benchmark_runbook.md`, `docs/reports/paper_result_table.json`, `docs/reports/paper_claim_boundary_report.json`, `docs/reports/reproducibility_attestation.json`, and `docs/reports/release_attention_pack_manifest.json`
- adding `tests/test_cli_slice15zr.py` coverage for catalog coverage, multidimensional result rows, claim boundaries, reproducibility attestation, and command rerun smoke

## Paper Track - Relaytic-AML arXiv benchmark path

Status:
- planned and mandatory before Slice 16A

Paper thesis:
- Relaytic-AML should be presented as a claim-gated local evaluation environment for temporal, graph, and operational financial-crime ML, not as a raw "we beat SOTA" leaderboard wrapper.
- The paper should argue that credible AML evaluation needs model metrics, temporal leakage checks, graph provenance, review-budget metrics, case-packet utility, reproducibility, and public-claim gates in one rerunnable local system.
- Hard performance claims remain blocked until Paper Track P10 through P12 generate numeric holdout evidence and the release-freeze, benchmark-environment, temporal, graph, and release-safety gates agree.

Target paper title:
- `Relaytic-AML: Claim-Gated Evaluation Environments for Temporal Graph Financial-Crime ML`

Target benchmark families:
- PaySim-style temporal transaction fraud for chronological split, review-budget, and operational queue proof
- Elliptic-style temporal graph AML for raw or flattened graph provenance, time-step stability, and structural-vs-model comparison
- Elliptic2-style subgraph AML for the hard modern subgraph track, treated as blocked until access, loader, and claim-scope proof are real
- AMLSim-style synthetic bank graph for seeded typology and analyst-case workflow proof, treated as synthetic/proxy unless stronger evidence is available
- generic structured-data benchmarks only as supporting breadth evidence, never as the flagship AML claim

Non-negotiable paper gates:
- public docs and CLI help must not expand stale `corr2surrogate`, prototype, toy, or unsupported SOTA language
- every table row must cite exact commands, dataset posture, split posture, artifacts, metric columns, runtime profile, and claim boundary
- no single proxy dataset can unlock a broader AML superiority claim
- optional baselines such as LightGBM, CatBoost, XGBoost, TabPFN, PyG, or graph-mining adapters must capture version and fallback state
- arXiv release is allowed only after a clean-clone dry run reproduces the paper table or emits deterministic blocked reasons

### Paper Track P0 - Freeze and commit the 15Z-R baseline

Goal:
- freeze the current 15Z-R paper-freeze state and make the repo safe to extend without losing the known-good baseline

Load-bearing improvement:
- Relaytic starts the paper track from a committed, tested, claim-blocked release state instead of layering paper work on a dirty tree

Human surface:
- humans can see one clean starting point, one verification transcript, and one explicit next paper slice

Agent surface:
- external agents can inspect the commit, test wall, freeze manifest, and next-slice pointer without guessing whether the current artifacts are provisional

Intelligence source:
- deterministic git status, test results, release-safety scan, and paper-freeze artifacts

Fallback rule:
- if the full prepush wall is too expensive, P0 may record a targeted wall plus the skipped full-wall reason, but it cannot allow hard claims

Required outputs:
- `paper_track_baseline_manifest.json`
- `paper_track_verification_report.json`
- updated `IMPLEMENTATION_STATUS.md`

Minimum proof:
- clean `git status` after commit or an explicit uncommitted-work ledger
- targeted paper-freeze and release-safety tests pass
- `relaytic release-safety paper-freeze --format json` still blocks hard claims honestly

Implemented by:
- adding `docs/reports/paper_track_baseline_manifest.json`
- adding `docs/reports/paper_track_verification_report.json`
- adding `tests/test_paper_track_p0.py`
- keeping hard AML/SOTA performance claims blocked and setting Paper Track P1 as the next implementation target

### Paper Track P1 - Legacy public-surface cleanup

Goal:
- make the repo read like current Relaytic-AML, not inherited `corr2surrogate` or generic surrogate-era scaffolding

Load-bearing improvement:
- public docs, CLI help, reports, and paper-facing artifacts become internally consistent enough for a reviewer to trust the project direction

Human surface:
- humans see Relaytic-AML naming, paper commands, and benchmark boundaries without stale prototype vocabulary

Agent surface:
- external agents get a machine-readable public-surface hygiene report and a stable compatibility-retention ledger

Intelligence source:
- deterministic text scans, import-boundary checks, CLI-help captures, public docs inventory, and compatibility retention rules

Fallback rule:
- legacy imports may remain only behind the explicit compatibility shim and must be hidden from new public surfaces

Required outputs:
- `paper_public_surface_hygiene_report.json`
- `legacy_compatibility_retention_report.json`
- `paper_repo_cleanup_scorecard.json`

Minimum proof:
- no stale public-surface language outside migration, compatibility, or history files
- old `surrogate` APIs have public Relaytic aliases where they affect paper or agent-facing flows
- tests prove compatibility remains narrow and new docs target `relaytic`

Implemented by:
- adding `src/relaytic/release_safety/paper_surface_hygiene.py`
- adding `docs/reports/paper_public_surface_hygiene_report.json`
- adding `docs/reports/legacy_compatibility_retention_report.json`
- adding `docs/reports/paper_repo_cleanup_scorecard.json`
- adding `train_model_candidates`, `rank_candidate_targets`, `train_incremental_linear_model`, and `resume_incremental_linear_model` aliases while retaining compatibility names
- cleaning README, CLI model-family help, and the modeler prompt so paper-facing surfaces no longer expose stale public-surface language
- adding `tests/test_paper_track_p1.py`

### Paper Track P2 - Paper thesis and claim contract

Goal:
- freeze the exact paper question, contribution story, allowed claims, blocked claims, and benchmark acceptance doctrine

Load-bearing improvement:
- Relaytic stops letting paper scope drift and gives every later benchmark slice one claim contract to satisfy

Human surface:
- humans can read one short thesis contract that says what the paper is about and what it refuses to claim

Agent surface:
- external agents can consume JSON claim contracts and reject paper text or benchmark rows that overreach

Intelligence source:
- current AML artifacts, external benchmark research notes, paper-freeze claim boundaries, and dataset availability evidence

Fallback rule:
- if a hot benchmark cannot be accessed or rerun locally, it becomes a named blocked or future track, not a substitute claim

Required outputs:
- `docs/paper/paper_thesis.md`
- `paper_thesis_contract.json`
- `paper_claim_taxonomy.json`
- `paper_related_work_seed.json`

Minimum proof:
- the paper title, research questions, contributions, metrics, and blocked claims are written before new benchmark implementation begins
- paper claim taxonomy agrees with `paper_claim_boundary_report.json`

Implemented by:
- adding `src/relaytic/release_safety/paper_thesis.py`
- adding `docs/paper/paper_thesis.md`
- adding `docs/reports/paper_thesis_contract.json`
- adding `docs/reports/paper_claim_taxonomy.json`
- adding `docs/reports/paper_related_work_seed.json`
- adding `tests/test_paper_track_p2.py`

P2 kept hard AML and SOTA performance claims blocked before Paper Track P3 froze dataset posture.

### Paper Track P3 - Benchmark dataset registry and access manifest

Goal:
- create one source-of-truth registry for all paper datasets, licenses, access methods, split posture, hashes, and blocked reasons

Load-bearing improvement:
- Relaytic can tell whether a benchmark is paper-ready, proxy-only, dev-only, or blocked before training anything

Human surface:
- humans see which datasets to fetch, where to place them, what license/access caveats apply, and which claims each can support

Agent surface:
- external agents can inspect dataset manifests and choose the next benchmark action without scraping markdown

Intelligence source:
- deterministic file inspection, source manifests, license/access notes, split-contract rules, and benchmark-family cataloging

Fallback rule:
- network-backed or login-gated datasets stay optional and blocked unless local source files and access posture are explicit

Required outputs:
- `paper_dataset_registry.json`
- `paper_dataset_access_manifest.json`
- `paper_split_contracts.json`
- `paper_dataset_blockers.json`

Minimum proof:
- PaySim-style, Elliptic-style, Elliptic2-style, AMLSim-style, and generic support tracks all have source posture and claim posture
- missing datasets yield precise setup or blocked-reason artifacts

Implemented by:
- adding `src/relaytic/release_safety/paper_dataset_registry.py`
- adding `docs/reports/paper_dataset_registry.json`
- adding `docs/reports/paper_dataset_access_manifest.json`
- adding `docs/reports/paper_split_contracts.json`
- adding `docs/reports/paper_dataset_blockers.json`
- adding `tests/test_paper_track_p3.py`

P3 keeps hard AML and SOTA performance claims blocked, records local file hashes for repo-local support fixtures, blocks or gates missing/login-gated datasets with exact setup paths, and records Paper Track P4 as the next paper implementation slice.

### Paper Track P4 - PaySim-style temporal benchmark runner

Goal:
- turn the proxy temporal transaction-fraud track into a rerunnable benchmark path with real temporal and review-budget metrics

Load-bearing improvement:
- Relaytic can generate a paper table row for PaySim-style data without treating synthetic evidence as real-world AML superiority

Human surface:
- humans can run one command sequence and inspect PR-AUC, precision@k, recall@review_budget, fixed-FPR recall, and threshold drift

Agent surface:
- external agents can consume the PaySim result row, split proof, temporal scorecard, and public-claim status

Intelligence source:
- chronological split contracts, rare-event metrics, review-budget operating points, baseline adapters, and existing AML temporal artifacts

Fallback rule:
- if only fixture or synthetic/proxy data exists, results are allowed as proxy or dev evidence only

Required outputs:
- `paysim_benchmark_manifest.json`
- `paysim_temporal_split_report.json`
- `paysim_operating_point_table.json`
- `paysim_paper_result_row.json`

Minimum proof:
- one chronological PaySim-style run completes
- threshold tuning uses validation and reports fixed test behavior
- paper result row remains supporting-only unless holdout and claim gates pass

Implemented by:
- adding `src/relaytic/release_safety/paysim_benchmark.py`
- adding `docs/reports/paysim_benchmark_manifest.json`
- adding `docs/reports/paysim_temporal_split_report.json`
- adding `docs/reports/paysim_operating_point_table.json`
- adding `docs/reports/paysim_paper_result_row.json`
- adding `tests/test_paper_track_p4.py`
- adding `relaytic release-safety paysim-benchmark --format json`

P4 runs the full 6,362,620-row PaySim source through a chronological `step` split, selects thresholds only on validation data, applies those thresholds unchanged to test, and emits review-budget plus fixed-FPR metrics for paper-table generation. It keeps the result row supporting-only, leaves paper-primary and hard-performance claims blocked, and records Paper Track P5 as the next paper implementation slice.

### Paper Track P5 - Elliptic graph benchmark loader and provenance

Goal:
- make Elliptic-style graph AML evidence credible by separating raw graph, flattened graph, and unsupported subgraph claims

Load-bearing improvement:
- Relaytic can ingest or explicitly block raw Elliptic-style graph bundles with node, edge, feature, time, and label provenance

Human surface:
- humans can see exactly whether a run used raw graph evidence, flattened proxy evidence, or blocked graph support

Agent surface:
- external agents can consume graph provenance, loader manifests, and graph claim scope directly

Intelligence source:
- graph loader detection, provenance reports, temporal split checks, structural graph features, and current AML graph artifacts

Fallback rule:
- flattened graph snapshots remain valid proxy evidence but must not be described as raw graph or subgraph benchmark support

Required outputs:
- `elliptic_graph_loader_manifest.json`
- `elliptic_graph_provenance_report.json`
- `elliptic_temporal_split_report.json`
- `elliptic_graph_claim_scope.json`
- `elliptic_paper_result_row.json`

Minimum proof:
- one raw or flattened Elliptic-style track materializes graph provenance
- incomplete raw bundles produce precise recovery instructions
- graph claims are blocked unless loader, split, and claim-scope checks pass

Implemented by:
- adding `src/relaytic/release_safety/elliptic_graph.py`
- adding `docs/reports/elliptic_graph_loader_manifest.json`
- adding `docs/reports/elliptic_graph_provenance_report.json`
- adding `docs/reports/elliptic_temporal_split_report.json`
- adding `docs/reports/elliptic_graph_claim_scope.json`
- adding `docs/reports/elliptic_paper_result_row.json`
- adding `relaytic release-safety elliptic-graph --format json`
- adding `tests/test_paper_track_p5.py`

P5 inspects the local raw Elliptic graph bundle, records 203,769 nodes, 234,355 directed edges, 165 source feature values per node, 49 chronological time steps, unknown-label scope, and a train/validation/test split by `time_step`. It allows only supporting loader/provenance wording, keeps graph benchmark performance, graph SOTA, paper-primary, and hard AML claims blocked, and records Paper Track P6 as the next paper implementation slice.

### Paper Track P6 - Strong tabular baseline suite

Goal:
- upgrade the paper comparison set so Relaytic is judged against current strong tabular baselines, not only legacy local models

Load-bearing improvement:
- Relaytic can compare rules, calibrated linear models, tree ensembles, boosted trees, optional tabular foundation-model adapters, and budgeted SOTA-candidate tabular routines under the same split, leakage, metric, and threshold contract

Human surface:
- humans see which baselines ran at smoke, baseline, competitive, and release budgets; which fell back; what versions were used; what search budget was consumed; and where Relaytic won, lost, or remains non-competitive

Agent surface:
- external agents can consume baseline eligibility, budget tier, fallback, version, runtime, HPO/search trace, leakage posture, and metric rows without inferring adapter state

Intelligence source:
- mature optional adapters, deterministic fallback baselines, leakage-safe feature generation, train-only imbalance handling, calibration/threshold contracts, HPO/search-controller budgets, rerun variance where practical, and benchmark-truth gates

Fallback rule:
- optional libraries may strengthen evidence but cannot become required for the deterministic floor or hidden sources of truth; if competitive adapters are unavailable or underperform, the result is recorded as non-competitive or baseline-only rather than promoted into the headline paper table

Required outputs:
- `paper_baseline_suite_manifest.json`
- `paper_baseline_version_matrix.json`
- `paper_tabular_baseline_table.json`
- `paper_baseline_fallback_report.json`
- `paper_benchmark_budget_contract.json`
- `paper_competitive_search_trace.json`
- `paper_leakage_safe_feature_report.json`
- `paper_publishability_gate.json`

Minimum proof:
- at least three baseline families run on one AML benchmark or emit explicit fallback states
- optional adapters capture version and eligibility
- result rows share the same split and metric contract
- every reported benchmark row is labeled `smoke`, `baseline`, `competitive`, or `release`
- no weak first-pass result can enter the headline table unless the competitive budget either improves it or emits a documented non-competitive blocker

Implemented by:
- adding `src/relaytic/release_safety/paper_baselines.py`
- adding `docs/reports/paper_baseline_suite_manifest.json`
- adding `docs/reports/paper_baseline_version_matrix.json`
- adding `docs/reports/paper_tabular_baseline_table.json`
- adding `docs/reports/paper_baseline_fallback_report.json`
- adding `docs/reports/paper_benchmark_budget_contract.json`
- adding `docs/reports/paper_competitive_search_trace.json`
- adding `docs/reports/paper_leakage_safe_feature_report.json`
- adding `docs/reports/paper_publishability_gate.json`
- adding `relaytic release-safety tabular-baselines --budget-tier baseline --run-optional --format json`
- adding `tests/test_paper_track_p6.py`

P6 runs six baseline families on the full 6,362,620-row PaySim source: a deterministic rule floor, sklearn linear, histogram boosting, and Extra Trees families plus installed LightGBM and XGBoost adapters. Every row shares the chronological split contract and validation-only threshold policy; feature transforms are row-local or fit from training data only, with prohibited balance fields excluded. Extra Trees is selected using validation PR-AUC and records fixed test PR-AUC `0.331345`, improving the earlier conservative floor while remaining explicitly baseline-only. CatBoost and TabPFN are recorded as unavailable fallbacks, LightGBM's poor observed result remains visible, and all headline/hard claims remain blocked until P6-A executes the competitive budget.

### Paper Track P6-A - PaySim competitive rerun and publishability gate

Goal:
- rerun PaySim under a real paper-grade competitive budget before PaySim performance is used as more than a baseline/provenance row

Load-bearing improvement:
- Relaytic stops treating the P4 leakage-safe logistic row as sufficient performance evidence and instead challenges it with strong leakage-safe feature engineering, boosted/tree ensembles, calibration, and budgeted HPO

Human surface:
- humans see the PaySim smoke, baseline, competitive, and release-candidate rows side by side, with exact feature exclusions, search budget, adapter versions, validation-selected thresholds, and reasons any result is or is not publishable

Agent surface:
- external agents can inspect the PaySim competitive search trace, feature report, leakage audit, model-family table, operating-point table, and publishability gate without reading code or markdown

Intelligence source:
- P3 source/split contracts, P4 temporal benchmark artifacts, P6 strong tabular adapters, search-controller budget doctrine, leakage audits, validation-only threshold optimization, and review-budget operating points

Fallback rule:
- if strong adapters are unavailable, runtime budget is insufficient, or the best clean model remains weak, PaySim stays baseline-only or non-competitive and the paper must frame it as failure analysis or supporting proxy evidence, not a model-quality headline

Required outputs:
- `paysim_competitive_benchmark_manifest.json`
- `paysim_competitive_budget_contract.json`
- `paysim_competitive_search_trace.json`
- `paysim_leakage_safe_feature_report.json`
- `paysim_competitive_baseline_table.json`
- `paysim_publishability_gate.json`

Minimum proof:
- at least one deterministic baseline and at least three strong tabular families run or emit precise fallback states on the same chronological split
- HPO/search budget, candidate count, runtime, random seeds, adapter versions, and train-only imbalance handling are recorded
- all feature engineering is point-in-time or leakage-safe, with forbidden PaySim balance fields and invalid split methods blocked from paper claims
- thresholds and calibration are selected only on validation and applied unchanged to test
- the result is promoted to paper-table candidate only if the publishability gate passes; otherwise the weak or non-competitive result is explicitly reported as such

Implemented by:
- adding `src/relaytic/release_safety/paysim_competitive.py`
- adding `docs/reports/paysim_competitive_benchmark_manifest.json`
- adding `docs/reports/paysim_competitive_budget_contract.json`
- adding `docs/reports/paysim_competitive_search_trace.json`
- adding `docs/reports/paysim_leakage_safe_feature_report.json`
- adding `docs/reports/paysim_competitive_baseline_table.json`
- adding `docs/reports/paysim_publishability_gate.json`
- adding `relaytic release-safety paysim-competitive --budget-tier competitive --run-optional --format json`
- adding `tests/test_paper_track_p6a.py`

P6-A runs on the full 6,362,620-row PaySim source with balance fields excluded and `nameDest` used only as a grouping key for history aggregated strictly before each time step. It executes 14 probe trials on a declared 750,000-row train-only probe set, refits five family finalists on all 6,010,937 training rows, selects Extra Trees from validation PR-AUC `0.568725`, fits Platt calibration and thresholds on validation-only subwindows, and reports one fixed test evaluation with PR-AUC `0.638773` versus the P6 baseline `0.331345`. The publishability gate passes this as a supporting-only PaySim table candidate; headline, real-world AML, and SOTA claims remain blocked until graph evidence and release proof land.

### Paper Track P7 - Graph baseline suite

Goal:
- add graph-aware baselines while keeping structural graph features, graph neural models, and graph-mining approaches separated

Load-bearing improvement:
- Relaytic can compare flattened tabular features, deterministic structural graph features, and optional graph model candidates honestly under baseline and competitive graph budgets

Human surface:
- humans see whether graph evidence came from structural features, graph-shadow models, or raw graph neural baselines, and whether each row is baseline-only, competitive, blocked, or release-candidate

Agent surface:
- external agents can consume graph baseline rows, budget tiers, eligibility, fallback, version/runtime state, leakage/split posture, and claim posture from stable artifacts

Intelligence source:
- graph feature extraction, optional graph ML adapters, graph-shadow scorecards, graph HPO/search budgets, split/leakage audits, and current graph claim scope

Fallback rule:
- if PyG or a graph adapter is unavailable, structural graph baselines remain the supported floor and graph-neural claims stay blocked; if competitive graph models underperform clean baselines, the paper must report the loss rather than hide it

Required outputs:
- `paper_graph_baseline_manifest.json`
- `paper_graph_feature_table.json`
- `paper_graph_model_shadow_scorecard.json`
- `paper_graph_baseline_fallback_report.json`
- `paper_graph_budget_contract.json`
- `paper_graph_competitive_search_trace.json`
- `paper_graph_publishability_gate.json`

Minimum proof:
- one structural graph baseline runs on Elliptic-style evidence
- optional graph models either run shadow-only or record fallback
- graph model claims stay separate from graph environment claims
- graph rows are labeled baseline, competitive, blocked, or release-candidate
- headline graph claims are blocked unless the competitive graph budget and graph claim-scope gate pass

Implemented by:
- adding `src/relaytic/release_safety/graph_baselines.py`
- adding `docs/reports/paper_graph_baseline_manifest.json`
- adding `docs/reports/paper_graph_feature_table.json`
- adding `docs/reports/paper_graph_model_shadow_scorecard.json`
- adding `docs/reports/paper_graph_baseline_fallback_report.json`
- adding `docs/reports/paper_graph_budget_contract.json`
- adding `docs/reports/paper_graph_competitive_search_trace.json`
- adding `docs/reports/paper_graph_publishability_gate.json`
- adding `relaytic release-safety graph-baselines --budget-tier competitive --run-optional --format json`
- adding `tests/test_paper_track_p7.py`

P7 runs the full 203,769-node, 234,355-edge Elliptic source under a frozen batch-snapshot protocol after verifying that every source edge remains inside one `time_step`. It evaluates one validation-selected winner per declared feature view without using test outcomes for selection. LightGBM on source features plus 12 label-free same-step structural features is selected on validation (`PR-AUC=0.976654`) and reports fixed test `PR-AUC=0.668756`, versus paired source-feature-only test `PR-AUC=0.664168` (`+0.004588` descriptive structural lift). A PyG GraphSAGE candidate runs shadow-only and underperforms the selected baseline on test (`PR-AUC=0.388907`), so graph-neural, SOTA, headline, and hard AML claims remain blocked. Before P10 can present any graph-neural row as more than failure-analysis evidence, a repeated-seed recovery or explicit non-competitive finding is required.

### Paper Track P8 - AMLSim and Elliptic2 blocked-or-supported track

Goal:
- decide whether AMLSim-style synthetic bank graphs and Elliptic2-style subgraph AML can enter the first paper or must remain future work

Load-bearing improvement:
- Relaytic stops hand-waving about the hardest relevant tracks and records either runnable support or precise blockers

Human surface:
- humans know whether to spend time setting up AMLSim or Elliptic2 for this paper, and what each track can claim

Agent surface:
- external agents can consume supported, proxy, or blocked state with exact next actions

Intelligence source:
- dataset registry, graph loader, generator manifests, source availability, local resource checks, and claim contract rules

Fallback rule:
- if these tracks are blocked, the paper must mention them as limitations or future benchmarks, not silently replace them with easier evidence

Required outputs:
- `amlsim_generation_manifest.json`
- `amlsim_typology_manifest.json`
- `elliptic2_subgraph_access_report.json`
- `subgraph_benchmark_blocker_report.json`

Minimum proof:
- each track is labeled supported, proxy, or blocked
- blocked tracks include access, scale, loader, license, or claim-scope reasons
- no paper table implies support without a corresponding artifact

Implemented by:
- adding `src/relaytic/release_safety/hard_graph_tracks.py`
- adding `relaytic release-safety hard-graph-tracks --format json`
- adding `tests/test_paper_track_p8.py`
- adding `docs/reports/amlsim_generation_manifest.json`
- adding `docs/reports/amlsim_typology_manifest.json`
- adding `docs/reports/elliptic2_subgraph_access_report.json`
- adding `docs/reports/subgraph_benchmark_blocker_report.json`

P8 recorded both hard tracks as `blocked` in the then-current local state. AMLSim remains blocked pending a reproducible synthetic proxy audit. Elliptic2's access decision is now superseded by P8-A recovery evidence, P8-B supporting modern-context evidence, and P8-C reference-parity/cohort blockers; because the paper must be modern and honest, P9 does not proceed until P8-D accepts thesis narrowing or reprovisions the benchmark path.

### Paper Track P8-A - Elliptic2 modern-benchmark recovery pilot

Goal:
- remove the practical Elliptic2 access/execution block and determine whether a modern context-aware result is viable on this machine

Load-bearing improvement:
- Relaytic no longer treats the hardest relevant graph track as hypothetical; it verifies official source material, pins the modern RevTrack/RevClassify reference, audits protocol discrepancies, and runs one carefully bounded feasibility pilot

Required outputs:
- `elliptic2_recovery_manifest.json`
- `elliptic2_schema_overlap_audit.json`
- `elliptic2_protocol_audit.json`
- `elliptic2_modern_reference_contract.json`
- `elliptic2_context_pilot_result.json`
- `elliptic2_recovery_gate.json`

Minimum proof:
- official Elliptic2 labeled-subgraph core is hash-recorded and schema/overlap audited without committing raw source files
- official RevTrack assets and a CPU-bounded selected-embedding derivation are hash-recorded with a provenance sidecar
- the original Elliptic2 paper/code split discrepancy is visible and cannot be silently mistaken for a clean comparable protocol
- a pilot result is labelled exploratory and cannot become a paper row, headline, SOTA, or hard AML claim

Implemented by:
- adding `src/relaytic/release_safety/elliptic2_recovery.py`
- adding `relaytic release-safety elliptic2-recovery --core-data-dir <external-local-core-dir> --revtrack-dir <external-local-revtrack-dir> --prepare-selected-embeddings --run-pilot --hash-large-assets --format json`
- adding `tests/test_paper_track_p8a.py`
- adding all six P8-A reports under `docs/reports/`

P8-A downloads the public official labeled-subgraph core outside git, audits `121810` subgraphs (`2763` suspicious), `444521` node memberships, and `367137` in-subgraph edges with no detected membership overlap or cross-component edge. It pins RevTrack/RevClassify as the modern reference, records its official `TRN`/`VAL`/`TST` partition, and exposes the mismatch between the original Elliptic2 paper's stated random split and the public preprocessing code's insertion-order modulo split. On CPU-only local hardware, P8-A verifies a low-memory derivation from the official `49299864 x 43` raw embedding tensor to the `90745 x 43` used-node cache, then runs a predeclared LightGBM pilot over pooled official RevTrack embeddings. The structural-only view reports test `PR-AUC=0.027773`, while the context view reports validation `PR-AUC=0.952440` and fixed test `PR-AUC=0.935255`. This establishes feasibility, not publishability: P8-B remains mandatory.

### Paper Track P8-B - Elliptic2 competitive and robustness suite

Goal:
- turn the promising modern-context pilot into defensible paper evidence or explicitly reject it

Load-bearing improvement:
- Relaytic tests modern subgraph evidence against the actual frontier reference and against split fragility rather than accepting one attractive pilot row

Required outputs:
- `elliptic2_competitive_budget_contract.json`
- `elliptic2_revclassify_reference_scorecard.json`
- `elliptic2_relaytic_candidate_search_trace.json`
- `elliptic2_repeated_seed_scorecard.json`
- `elliptic2_split_robustness_report.json`
- `elliptic2_publishability_gate.json`

Minimum proof:
- run or rigorously document the official RevClassify BP/DS comparison path and its dependency/resource posture
- freeze a validation-only competitive budget for Relaytic candidates over official RevTrack context features
- report repeated-seed mean, dispersion, and failure cases for promoted candidates
- evaluate both the pinned official RevTrack partition and a predeclared deterministic robustness partition independent of row-order artifacts
- allow a paper row only when performance survives the gate; never imply end-to-end Relaytic superiority while consuming official RevTrack preprocessing unless that boundary is explicit

Fallback rule:
- if P8-B cannot promote the pilot, the paper must state that modern Elliptic2 execution was recovered but not sufficiently robust for a competitive claim; P9 and paper assembly remain blocked until that claim posture is accepted deliberately

Implemented by:
- adding `src/relaytic/release_safety/elliptic2_competitive.py`
- adding `relaytic release-safety elliptic2-competitive --revtrack-dir <external-local-revtrack-dir> --budget-tier competitive --run-suite --format json`
- adding `tests/test_paper_track_p8b.py`
- adding all six P8-B reports under `docs/reports/`

P8-B records the official paper's full-shot RevClassify comparison (`BP PR-AUC=0.972`, `DS PR-AUC=0.974`) and documents that the pinned public repository provides no classification checkpoint for local replay and describes single-V100 experiments. It discovers that the pinned RevTrack-evaluable table contains `110902` rows and `2578` positives versus the audited current official Elliptic2 core's `121810` rows and `2763` suspicious labels. A bounded validation-only CPU search selects pooled-moments LightGBM; repeated official-partition test performance is `PR-AUC=0.943240 +/- 0.000882`, and the predeclared row-order-independent content-hash test performance is `PR-AUC=0.929669 +/- 0.000538`. This is stable supporting evidence, not reference parity or an end-to-end Relaytic result. P8-C is required before P9 because the modern result remains below the published frontier reference, uses official preprocessing/embeddings, follows an already exposed official test split, and does not prove full-core or entity-disjoint generalization.

### Paper Track P8-C - Modern subgraph reference parity and leakage-resistant cohort protocol

Goal:
- make the modern-subgraph paper story genuinely competitive rather than stopping at a strong supporting baseline

Load-bearing improvement:
- Relaytic either reproduces or fairly challenges the RevClassify neural reference and replaces ambiguous cohort/split assumptions with explicit, harder generalization evidence

Required outputs:
- `elliptic2_neural_reference_parity_contract.json`
- `elliptic2_evaluable_cohort_reconciliation.json`
- `elliptic2_entity_disjoint_split_report.json`
- `elliptic2_neural_candidate_scorecard.json`
- `elliptic2_reference_parity_gate.json`

Minimum proof:
- implement or faithfully execute RevClassifyBP/DS-style neural candidates with exact dependency, accelerator, seed, early-stopping, and search-budget accounting
- reconcile why the pinned RevTrack table evaluates `110902` rows while the audited official core has `121810`, or narrow every claim permanently to the demonstrably mapped cohort
- run an entity-disjoint, connected-component-grouped, or comparably stringent predeclared split that cannot gain from sender/receiver identity recurrence across partitions
- compare repeated-seed neural candidate evidence against the reported `RevClassifyDS PR-AUC=0.974` boundary without selecting on an already observed official test partition
- keep P9 and headline modern-subgraph claims blocked unless the parity/cohort gate passes or the paper thesis is explicitly narrowed

Fallback rule:
- if local hardware cannot support faithful neural parity, P8-C must emit a resource-backed blocker and revise the paper to present the Elliptic2 result as stable supporting context evidence only, not as a performance contribution

Implemented by:
- adding `src/relaytic/release_safety/elliptic2_reference_parity.py`
- adding `relaytic release-safety elliptic2-reference-parity --revtrack-dir <external-local-revtrack-dir> --run-neural --format json`
- adding `tests/test_paper_track_p8c.py`
- adding all five P8-C reports under `docs/reports/`

P8-C requested faithful RevClassify parity execution and recorded the exact blocker set instead of turning the supporting P8-B row into an overclaim. The pinned RevTrack checkout contains the full-shot BP/DS configurations and 15 recommendation checkpoints, but no distributed RevClassify classification checkpoints; the local environment is CPU-only and lacks the official Lightning/Hydra/OmegaConf/TorchMetrics stack needed for faithful replay. Cohort reconciliation keeps every modern-subgraph claim narrowed to the pinned RevTrack-evaluable table (`110902` rows, `2578` positives) because the current audited official core has `121810` subgraphs and `2763` suspicious labels and the RevTrack table does not expose original component IDs. The strict component-grouped entity-disjoint audit is also not a meaningful evaluation split: the largest identity component contains `110889/110902` rows (`0.99988278`), leaving only 7 validation rows and 6 test rows under a zero-overlap component split. P8-C therefore blocks reference-parity, SOTA, full-core, entity-disjoint, hard AML, and end-to-end Relaytic claims; P8-B remains supporting modern-context evidence only. P8-D is now required before P9 to either reprovision a faithful benchmark environment/cohort protocol or narrow the paper thesis deliberately.

### Paper Track P8-D - Paper thesis narrowing and alternative evidence decision

Goal:
- decide the first paper's honest post-P8-C story before adding operational metrics or assembling tables

Load-bearing improvement:
- Relaytic records whether the paper will reprovision modern-subgraph parity or deliberately narrow to a claim-gated AML evaluation-environment thesis that uses Elliptic2 as supporting context only

Required outputs:
- `paper_p8d_thesis_decision.json`
- `paper_p8d_evidence_role_matrix.json`
- `paper_p8d_reprovisioning_decision.json`
- `paper_p8d_claim_rewrite_plan.json`

Minimum proof:
- consume P8-B and P8-C gates directly rather than prose summaries
- choose one explicit route: reprovision faithful RevClassify parity resources, or narrow the paper so P8-B is supporting context only
- update allowed/blocked claim language before P9 operational metrics can proceed
- preserve the option to return to modern-subgraph parity later without blocking the first paper indefinitely

Fallback rule:
- if no thesis route is accepted, P9 remains blocked and no reproducible paper table may include Elliptic2 as a performance contribution

Implemented by:
- adding `src/relaytic/release_safety/paper_thesis_decision.py`
- adding `relaytic release-safety paper-thesis-decision --format json`
- adding `tests/test_paper_track_p8d.py`
- adding `docs/reports/paper_p8d_thesis_decision.json`
- adding `docs/reports/paper_p8d_evidence_role_matrix.json`
- adding `docs/reports/paper_p8d_reprovisioning_decision.json`
- adding `docs/reports/paper_p8d_claim_rewrite_plan.json`
- updating `docs/reports/subgraph_benchmark_blocker_report.json` so P9 can proceed under the narrowed thesis

P8-D accepts the narrowed first-paper route instead of waiting for a GPU-backed faithful RevClassify reprovisioning pass. It consumes the P8-B and P8-C gates directly, records P8-B as supporting modern-context evidence only, treats P8-C as a claim-firewall and limitation, blocks Elliptic2 performance/SOTA/full-core/entity-disjoint claims, preserves a later reprovisioning extension, and unblocks P9 operational AML evaluation.

### Paper Track P9 - Operational AML evaluation layer

Goal:
- make analyst-review utility a primary evaluation axis rather than an after-the-fact product demo metric

Load-bearing improvement:
- Relaytic can evaluate AML systems by review capacity, false-positive reduction, case-packet completeness, and queue usefulness as well as model score

Human surface:
- humans can inspect top cases, review-budget tradeoffs, analyst-hour assumptions, and operational guardrails

Agent surface:
- external agents can consume operational metric rows and compare model wins against workflow value

Intelligence source:
- casework artifacts, operating-point contracts, review-capacity sensitivity, business-value reports, and public-claim guards

Fallback rule:
- if operational assumptions are missing, Relaytic records unknown or not claimable rather than inventing analyst-hour claims

Required outputs:
- `paper_operational_metric_table.json`
- `paper_review_budget_curve.json`
- `paper_case_packet_completeness_report.json`
- `paper_operational_claim_guard.json`

Minimum proof:
- at least one AML benchmark row includes review-budget metrics
- operational metrics cite assumptions and artifacts
- public claims fail closed when business-value assumptions are incomplete

Implemented by:
- adding `src/relaytic/release_safety/paper_operational_metrics.py`
- adding `relaytic release-safety paper-operational-metrics --format json`
- adding `tests/test_paper_track_p9.py`
- adding `docs/reports/paper_operational_metric_table.json`
- adding `docs/reports/paper_review_budget_curve.json`
- adding `docs/reports/paper_case_packet_completeness_report.json`
- adding `docs/reports/paper_operational_claim_guard.json`

P9 materializes supporting operational evidence for the narrowed first paper: PaySim and Elliptic rows now expose review-budget performance, prevalence-matched false-positive burden proxies, analyst-hour assumptions, and explicit artifact refs. Case-packet completeness is recorded as missing for aggregate benchmark rows, so hard business-value and headline operational claims remain blocked. The operational claim guard allows P10 to generate reproducible paper tables while keeping Elliptic2 out of performance-contribution claims.

### Paper Track P10 - Reproducible paper table generator

Goal:
- generate all paper tables from artifacts and rerunnable commands instead of hand-maintained numbers

Load-bearing improvement:
- Relaytic can produce a paper-ready result pack whose numbers, blockers, and claim labels are traceable to local runs

Human surface:
- humans can regenerate tables and see why any row is numeric, proxy-only, baseline-only, competitive, release-candidate, non-competitive, or blocked

Agent surface:
- external agents can inspect table provenance and verify that every metric cell has an artifact source, budget tier, leakage posture, and publishability-gate state

Intelligence source:
- paper dataset registry, benchmark result rows, baseline tables, competitive search traces, budget contracts, leakage audits, operational metrics, environment scorecards, and claim gates

Fallback rule:
- missing metrics become empty or blocked cells with reasons, never manually filled placeholders; baseline-only or weak first-pass metrics are excluded from headline tables unless the publishability gate explicitly promotes them

Required outputs:
- `paper_result_table_final.json`
- `paper_table_provenance.json`
- `paper_reproduction_commands.md`
- `paper_metric_cell_audit.json`
- `paper_publishability_matrix.json`

Minimum proof:
- one command regenerates the paper table pack from existing run artifacts
- every numeric cell cites dataset, split, command, run directory, artifact, and claim state
- every headline metric cites a competitive or release budget row, not only a smoke or baseline row
- hard claims remain blocked unless all required gates pass

Implemented by:
- adding `src/relaytic/release_safety/paper_table_generator.py`
- adding `relaytic release-safety paper-tables --format json`
- adding `tests/test_paper_track_p10.py`
- adding `docs/reports/paper_result_table_final.json`
- adding `docs/reports/paper_table_provenance.json`
- adding `docs/reports/paper_reproduction_commands.md`
- adding `docs/reports/paper_metric_cell_audit.json`
- adding `docs/reports/paper_publishability_matrix.json`

P10 generates the first reproducible paper table pack from committed artifacts instead of hand-maintained numbers. Supporting PaySim, Elliptic, operational, Elliptic2-context, and limitation rows are grouped into table roles, and every numeric cell has dataset, split, command, run-directory, artifact, claim-state, budget-tier, leakage-posture, and publishability-gate provenance. The metric-cell audit passes and permits P11 drafting, while headline, hard AML, SOTA, and business-value claims remain blocked.

### Paper Track P11 - Paper draft and figure pack

Goal:
- write the first paper draft and generate figures from the same evidence pack

Load-bearing improvement:
- Relaytic turns benchmark artifacts into a coherent arXiv-facing argument without drifting beyond the claim contract

Human surface:
- humans can read a paper draft, inspect figures, and see limitations before public release

Agent surface:
- external agents can lint paper claims against the contract and table provenance

Intelligence source:
- paper thesis contract, benchmark tables, operational metrics, related-work notes, figure generators, and claim taxonomy

Fallback rule:
- sections that depend on blocked benchmarks must be written as limitations or future work

Required outputs:
- `docs/paper/relaytic_aml_draft.md`
- `docs/paper/figures/`
- `paper_claim_lint_report.json`
- `paper_limitations_matrix.json`

Minimum proof:
- draft contains abstract, intro, related work, method, benchmarks, results, limitations, and reproducibility appendix
- claim lint passes against the claim contract
- figures are generated from artifacts or explicitly marked schematic

Implemented by:
- adding `src/relaytic/release_safety/paper_draft.py`
- adding `relaytic release-safety paper-draft --format json`
- adding `tests/test_paper_track_p11.py`
- adding `docs/paper/relaytic_aml_draft.md`
- adding `docs/paper/figures/figure_manifest.json`
- adding four deterministic SVG figures under `docs/paper/figures/`
- adding `docs/reports/paper_claim_lint_report.json`
- adding `docs/reports/paper_limitations_matrix.json`

P11 generates the first Relaytic-AML paper draft from the P10 table pack, not from hand-copied numbers. The draft contains the required paper sections, cites audited `paper-cell:*` metric references, renders artifact-backed or explicitly schematic figures, and names every generated limitation. The claim lint passes and permits P12 clean-clone proof, while hard AML, headline, SOTA, RevClassify parity, graph-neural superiority, and hard business-value claims remain blocked.

### Paper Track P12 - External dry run and clean-clone proof

Goal:
- prove that a fresh reviewer or external agent can reproduce the paper path without local tribal knowledge

Load-bearing improvement:
- Relaytic earns the right to call the paper reproducible by testing the repository as an outsider would use it

Human surface:
- humans get a clean-clone checklist and one clear pass/fail report before arXiv submission

Agent surface:
- external agents can run the dry-run checklist, inspect failures, and propose concrete repairs

Intelligence source:
- clean environment install checks, dataset registry, benchmark commands, release-safety scans, claim gates, and paper table regeneration

Fallback rule:
- if the full benchmark is too heavy, P12 must still reproduce a declared paper-smoke subset and record what remains non-reproduced

Required outputs:
- `paper_external_dry_run_report.json`
- `paper_clean_clone_install_report.json`
- `paper_reproduction_failure_report.json`
- `paper_release_go_no_go.json`

Minimum proof:
- clean clone installs with the documented profile
- paper-smoke benchmark subset regenerates expected artifacts
- leak scan and claim lint pass
- arXiv release is blocked on unresolved dry-run failures

P12 added:

- `src/relaytic/release_safety/paper_dry_run.py`
- `relaytic release-safety paper-dry-run --run-isolated-install --format json`
- `docs/reports/paper_clean_clone_checklist.md`
- `docs/reports/paper_external_dry_run_report.json`
- `docs/reports/paper_clean_clone_install_report.json`
- `docs/reports/paper_reproduction_failure_report.json`
- `docs/reports/paper_release_go_no_go.json`
- `tests/test_paper_track_p12.py`

P12 proves the external paper-smoke path without overclaiming full benchmark reruns. The dry-run pack documents a clean-clone checklist, verifies the install contract, optionally runs a temp isolated full-profile install probe, regenerates the P10 table pack and P11 draft pack, records release-safety leak-scan status, and writes a deterministic release go/no-go decision. P13 is unblocked only in claim-safe evaluation-environment mode; hard AML, headline, SOTA, RevClassify parity, graph-neural superiority, and hard business-value claims remain blocked.

### Paper Track P13 - arXiv release and attention pack

Goal:
- prepare the claim-safe paper, benchmark pack, tag plan, and public attention materials only after gates pass

Load-bearing improvement:
- Relaytic converts technical benchmark proof into a credible public artifact without overclaiming

Human surface:
- humans get a release checklist, paper draft, references, generated paper tables, README update, and concise public summary

Agent surface:
- external agents can verify release tag plan, paper version, benchmark artifacts, and allowed public wording

Intelligence source:
- final paper table, dry-run report, claim lint, release-safety scan, and attention-pack manifest

Fallback rule:
- if gates fail, P13 becomes a release-blocker report and schedules the next repair slice instead of publishing

Required outputs:
- `paper_release_manifest.json`
- `paper_arxiv_submission_checklist.md`
- `paper_attention_pack.md`
- `paper_public_claims_allowed.json`
- `docs/paper/relaytic_aml_arxiv_draft.md`
- `docs/paper/references.bib`
- `docs/paper/tables/table_manifest.json`
- `docs/paper/tables/table_1_evidence_summary.md`
- `docs/paper/tables/table_2_claim_gate_matrix.md`
- `docs/paper/tables/table_3_release_artifact_set.md`

Minimum proof:
- P10 through P12 pass
- release tag and paper draft cite the same artifact set
- README and public post text use only allowed wording
- no hard AML/SOTA claim appears without passing holdout, environment, claim, and reproducibility gates

P13 added:

- `src/relaytic/release_safety/paper_release.py`
- `relaytic release-safety paper-release --format json`
- `docs/reports/paper_release_manifest.json`
- `docs/reports/paper_arxiv_submission_checklist.md`
- `docs/reports/paper_attention_pack.md`
- `docs/reports/paper_public_claims_allowed.json`
- `docs/paper/relaytic_aml_arxiv_draft.md`
- `docs/paper/references.bib`
- `docs/paper/tables/table_manifest.json`
- `docs/paper/tables/table_1_evidence_summary.md`
- `docs/paper/tables/table_2_claim_gate_matrix.md`
- `docs/paper/tables/table_3_release_artifact_set.md`
- `tests/test_paper_track_p13.py`

P13 produces a claim-safe Markdown draft and attention pack from P10-P12 source artifacts. It writes a release tag plan but does not create or push tags automatically. The public wording lint passes only because hard AML, headline, SOTA, RevClassify parity, graph-neural superiority, production-ready, and hard business-value claims remain blocked. Paper Track P14 converted that pack into a source release candidate, and P15 now adds measured system-behavior evidence before release regeneration.

### Paper Track P14 - final arXiv source bundle and clean release candidate

Goal:

- turn the P13 Markdown draft pack into a final arXiv-compatible source bundle without changing the claim contract
- verify the paper as a professional release candidate from a clean clone and a clean tag target
- keep the public story focused on a claim-gated AML evaluation environment unless later benchmark gates unlock stronger language

Deliverables:

- `docs/paper/arxiv_src/`
- `docs/reports/paper_arxiv_source_manifest.json`
- `docs/reports/paper_submission_package_audit.json`
- `docs/reports/paper_release_candidate_checklist.md`
- `tests/test_paper_track_p14.py`

Acceptance:

1. The source bundle includes top-level TeX/PDF source, bibliography, and converted figures in formats accepted by the selected arXiv processor.
2. Citation and reference audits prove every in-text citation resolves and every paper-used BibTeX entry is valid enough for the chosen source format.
3. The package audit blocks local machine paths, external private data paths, secrets, `.env` files, virtual environments, stale prototype language, and unguarded hard claims.
4. A clean-clone smoke run regenerates P10-P13 artifacts and validates the P14 source package.
5. The release-candidate checklist requires an empty `git status --short` at the final tag target before upload.

Implemented status:

- implemented by `src/relaytic/release_safety/paper_arxiv_source.py`
- public command: `relaytic release-safety paper-arxiv-source --format json`
- generated source tree: `docs/paper/arxiv_src/main.tex`, `docs/paper/arxiv_src/references.bib`, and four converted PDF figures under `docs/paper/arxiv_src/figures/`
- generated audits: `paper_arxiv_source_manifest.json`, `paper_submission_package_audit.json`, and `paper_release_candidate_checklist.md`
- P14 source release-candidate status is ready; a paper-excellence pass sharpened the thesis around evidence cells, deterministic claim gates, explicit research questions, agentic ML reliability, and company-facing evaluation-lab utility. `arxiv_upload_ready` remains false until author metadata is replaced, local TeX/PDF compile is inspected, and the final tag target has empty `git status --short`

### Paper Track P15 - measured system-evaluation proof pack

Goal:

- turn Relaytic's guide, recovery, handoff, interoperability, and claim-gate behavior into measured deterministic evidence that can support the system sections of the paper
- make the paper stronger for technical readers by showing how user and external-agent orientation is tested, not only described

Load-bearing improvement:

- the paper can now claim that Relaytic gives humans and agents a safe way to ask what state the system is in, what artifacts matter, what can be handed to another model, and what claims are allowed, because those behaviors are exercised in a repeatable release-safety pack

Deliverables:

- `src/relaytic/release_safety/paper_system_eval.py`
- `relaytic release-safety paper-system-eval`
- `docs/reports/paper_system_behavior_eval.json`
- `docs/reports/paper_system_task_eval.json`
- `docs/reports/paper_agent_handoff_eval.json`
- `docs/reports/paper_no_lost_user_eval.json`
- `docs/reports/paper_claim_gate_case_studies.json`
- `docs/reports/paper_system_eval_manifest.json`
- `docs/reports/paper_system_eval_summary.md`
- P13 release gating that consumes P15 before rendering reader-facing system-evaluation text

Acceptance:

1. The pack evaluates no-lost onboarding, partial-run recovery, artifact shortlist quality, safe next actions, rowless external-agent handoff, optional local-LLM advisory boundaries, interoperability tool discovery, and claim-gate behavior.
2. Required checks fail closed if P11/P12/P13 claim-gate inputs are missing or stale.
3. Committed reports contain no raw dataset rows, no private local paths, no secrets, and no unsupported human-study, analyst-hour, production, or SOTA claims.
4. The paper draft/source/PDF include a concise measured-system-behavior section with interpretation near the evidence.
5. Tests cover the builder, CLI surface, fail-closed missing-input behavior, and committed artifact readiness.

Implemented status:

- implemented by `src/relaytic/release_safety/paper_system_eval.py`
- generated reports: `paper_system_behavior_eval.json`, `paper_system_task_eval.json`, `paper_agent_handoff_eval.json`, `paper_no_lost_user_eval.json`, `paper_claim_gate_case_studies.json`, `paper_system_eval_manifest.json`, and `paper_system_eval_summary.md`
- the current pack passes the required deterministic protocol and reader/agent task checks, covering navigation, metric provenance, partial-run recovery, rowless handoff, local-LLM advisory boundaries, and claim gates while remaining explicitly bounded to protocol evidence, not human-study or production-deployment evidence
- Slice 16A remains the next execution target

## Slice 16 - Relaytic Academy, governed capability evolution, and shadow-tested growth

Goal:
- governed capability registry
- replay and shadow validation
- arena promotion scorecards
- bounded hunt campaigns
- non-core specialist recruitment and retirement
- academy mission-control explainability

Load-bearing improvement:

- Relaytic should be able to discover, trial, promote, demote, and retire new tools and non-core specialist agents through a shadow-tested academy instead of relying only on fixed manually-coded capability growth

Human surface:

- humans should be able to inspect candidate capabilities, shadow-trial outcomes, promotion decisions, hunt campaigns, and retirement reasons from one coherent operator surface

Agent surface:

- external agents should be able to propose capabilities, run replay or shadow trials, inspect promotion scorecards, and consume academy state through stable JSON-first surfaces

Intelligence source:

- pulse watchlists, benchmark gaps, workspace memory, search-controller deficits, external-agent proposals, replay packs, shadow disagreements, and seeded exploration

Fallback rule:

- when the academy is disabled, Relaytic must continue using only the current promoted static capability set and must not silently trial or route candidate tools or non-core specialists

Required behavior:

- core agents must remain immutable from the academy's point of view
- tools and non-core specialists must move through explicit lifecycle states rather than appearing silently
- replay and shadow proof must exist before live authority
- hunt exploration must be seeded, budgeted, and replayable
- promotion, quarantine, and retirement decisions must be deterministic and audit-backed

Minimum proof:

- one candidate progresses from intake to shadow mode without changing production truth
- one candidate is promoted through explicit replay, shadow, and arena evidence
- one candidate is quarantined or retired despite promise because safety, transfer, or policy proof fails
- one seeded hunt campaign can be replayed exactly

This umbrella slice is delivered through Slices 16A through 16F below.

## Slice 16A - Capability registry and capability cards

Goal:
- capability registry
- capability cards
- core-agent protection
- non-core specialist registry

Load-bearing improvement:

- Relaytic should be able to represent candidate and promoted tools or specialists explicitly as typed capability cards with lifecycle, risk, owner, and proof posture

Human surface:

- humans should be able to inspect what a capability is, what permissions it needs, and whether it is candidate, promoted, quarantined, or retired

Agent surface:

- external agents should be able to submit candidates and inspect the same capability cards through stable JSON-first surfaces

Intelligence source:

- current workspace gaps, benchmark debt, pulse innovation watch, and external-agent proposals

Fallback rule:

- when the academy registry is unavailable, Relaytic must expose an explicit `academy_unavailable` posture rather than inferring candidate state

Required outputs:
- `capability_registry.json`
- `capability_card_log.jsonl`
- `capability_intake_record.json`
- `capability_risk_profile.json`
- `academy_policy_report.json`
- `core_agent_roster.json`
- `non_core_specialist_registry.json`

Minimum proof:

- one tool candidate can be registered with a full capability card
- one non-core specialist candidate can be registered without affecting the core roster
- one attempt to make a core agent removable is rejected explicitly

## Slice 16B - Offline replay packs and shadow mode

Goal:
- replay packs
- non-authoritative shadow mode
- disagreement capture
- counterfactual win reporting

Load-bearing improvement:

- Relaytic should be able to evaluate candidate tools or specialists on replayable runs and in live-like shadow mode without allowing them to alter production truth

Human surface:

- humans should be able to see whether a candidate would have helped, hurt, disagreed, or violated constraints before it gets live authority

Agent surface:

- external agents should be able to launch replay and shadow trials and inspect disagreement or counterfactual win reports through stable JSON-first surfaces

Intelligence source:

- historical runs, benchmark packs, trace spans, shadow disagreements, cost envelopes, and feasibility or permission outcomes

Fallback rule:

- when replay packs are unavailable, Relaytic must block promotion and keep the candidate in non-authoritative states

Required outputs:
- `offline_replay_scorecard.json`
- `replay_trace_index.json`
- `capability_failure_taxonomy.json`
- `shadow_trial_report.json`
- `shadow_disagreement_log.jsonl`
- `shadow_counterfactual_win_report.json`
- `shadow_budget_report.json`

Minimum proof:

- one replay pack produces a comparable scorecard
- one shadow run leaves authoritative output unchanged
- one candidate shows a measurable counterfactual win
- one weak candidate is blocked from advancing

## Slice 16C - Arena evaluation and promotion scorecards

Goal:
- deterministic arena comparison
- promotion and quarantine scorecards
- narrow live trial contracts
- rollback-ready promotion decisions

Load-bearing improvement:

- Relaytic should be able to compare candidates against incumbents through one deterministic arena and promote only when multi-axis evidence justifies the added complexity

Human surface:

- humans should be able to inspect why one candidate won, why another lost, and what evidence blocked promotion

Agent surface:

- external agents should be able to consume one ranking and one promotion decision report without prompt-only interpretation

Intelligence source:

- replay packs, shadow trials, cost and safety budgets, feasibility outcomes, transfer evidence, and deterministic scorecards

Fallback rule:

- when arena comparison cannot be run, Relaytic must quarantine the candidate and emit an incomplete-proof posture

Required outputs:
- `capability_arena_scorecard.json`
- `promotion_candidate_ranking.json`
- `arena_judge_report.json`
- `promotion_decision_report.json`
- `capability_registry_update.json`
- `trial_scope_contract.json`
- `trial_rollback_checkpoint.json`

Minimum proof:

- one candidate is promoted through an explicit arena win
- one metric-strong candidate still loses because safety, feasibility, or transfer evidence is worse
- one candidate enters a rollbackable narrow live trial
- one candidate is quarantined because proof is incomplete

## Slice 16D - Hunt campaigns, seeded exploration, and provider feedback

Goal:
- bounded hunt campaigns
- seeded exploration
- provider feedback
- daemon-backed scouting

Load-bearing improvement:

- Relaytic should be able to use idle daemon or pulse windows to scout benchmark gaps, sample candidates, run bounded hunt campaigns, and generate reusable provider feedback without silently mutating production behavior

Human surface:

- humans should be able to see what Relaytic hunted for, what budget it spent, what it found, and why the hunt stopped

Agent surface:

- external agents should be able to inspect hunt state, seeds, targets, and provider feedback through stable JSON-first surfaces and remote supervision

Intelligence source:

- pulse watchlists, benchmark gaps, repeated workspace failures, imported-incumbent deficits, seeded candidate sampling, and bounded daemon execution

Fallback rule:

- when hunt mode is disabled, Relaytic must keep the same targets and queues visible but must not run autonomous scouting

Required outputs:
- `hunt_campaign_state.json`
- `hunt_target_selection.json`
- `hunt_candidate_log.jsonl`
- `hunt_outcome_report.json`
- `provider_feedback_report.json`
- `exploration_budget_report.json`
- `exploration_seed_log.jsonl`
- `exploration_policy_report.json`

Minimum proof:

- one hunt campaign runs from an explicit target gap to a queued candidate outcome
- one hunt campaign exhausts its budget and stops honestly
- one failed candidate still yields useful provider feedback
- one seeded hunt is replayable

## Slice 16E - Non-core specialist recruitment and retirement

Goal:
- governed specialist recruitment
- governed specialist retirement
- core-agent protection
- roster change audit

Load-bearing improvement:

- Relaytic should be able to recruit useful non-core specialists for recurring needs and retire underperforming non-core specialists without allowing uncontrolled roster drift or any deletion of core agents

Human surface:

- humans should be able to inspect why a non-core specialist was recruited or retired and how that changed capability coverage

Agent surface:

- external agents should be able to propose non-core specialists and inspect roster decisions through stable JSON-first surfaces

Intelligence source:

- repeated workspace gaps, hunt outcomes, arena results, transfer evidence, and deterministic roster rules

Fallback rule:

- when recruitment logic is disabled, Relaytic must preserve the existing roster and record proposals as candidate-only

Required outputs:
- `specialist_candidate_queue.json`
- `recruitment_decision_report.json`
- `specialist_trial_report.json`
- `capability_retirement_report.json`
- `roster_change_log.jsonl`
- `core_agent_protection_report.json`

Minimum proof:

- one non-core specialist is recruited for a recurring gap
- one underperforming non-core specialist is retired with explicit evidence
- one attempt to retire a core agent is rejected and audited

## Slice 16F - Academy mission control and explainability surfaces

Goal:
- academy mission control
- academy explanation surfaces
- academy remote supervision views
- academy MCP exports

Load-bearing improvement:

- Relaytic should expose one professional academy surface that shows promoted capabilities, candidates in replay or shadow, hunt campaigns, roster changes, and promotion or retirement reasons from the same runtime truth

Human surface:

- humans should be able to ask why a capability was promoted, blocked, or retired and get a trace-backed explanation without reading raw artifact trees

Agent surface:

- external agents should be able to query the same academy state, candidate registry, trial posture, and promotion reasoning through stable JSON-first surfaces and MCP tools

Intelligence source:

- capability cards, replay and shadow evidence, arena scorecards, provider feedback, roster history, and remote-supervision state

Fallback rule:

- if richer academy UI rendering is unavailable, Relaytic must still expose the same academy truth through CLI, MCP, and artifacts

Required outputs:
- `academy_state.json`
- `academy_registry_view.json`
- `academy_trial_dashboard.json`
- `academy_hunt_view.json`
- `academy_promotion_timeline.json`
- `academy_explanation_report.json`
- `academy_remote_approval_view.json`

Minimum proof:

- one human can inspect promoted capabilities, shadow candidates, and hunt campaigns from one academy view
- one agent can query the same academy state through JSON-first or MCP surfaces
- one "why was this promoted?" explanation is trace-backed and specific
- one remote supervisor can inspect academy promotion or hunt state without creating a second authority path

## Slice 17 - Representation engines, JEPA-style latent world models, and unlabeled local corpora

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

## Slice 18 - Endgame consolidation, legacy removal, and repo-quality hardening

Goal:
- remove misleading legacy structure
- retire compatibility shims that are no longer justified
- split oversized modules and helper grab-bags
- leave the repo reading like one intentional product

Load-bearing improvement:

- Relaytic should finish the roadmap with one deliberate consolidation pass that removes temporary scaffolding, misleading folder structure, stale prototype language, dead code, and unjustified compatibility surfaces so the final repo is easier to trust, extend, and evaluate

Human surface:

- humans should see a cleaner, more coherent product surface with fewer duplicate concepts, fewer confusing entry points, and no stale legacy naming outside explicit historical notes

Agent surface:

- external agents should see one clear package map, one clear public CLI surface, fewer misleading wrappers, and more predictable artifact or module boundaries

Intelligence source:

- deterministic repo audits, public-surface inventory, import-graph review, dead-code checks, protocol-conformance checks, install-health checks, and explicit refactor scorecards rather than new modeling intelligence

Fallback rule:

- if a legacy surface still has active compatibility value, Relaytic must keep it temporarily but record the retention reason, owning slice, and removal condition explicitly instead of letting it drift indefinitely

Required outputs:
- `legacy_surface_audit.json`
- `compatibility_removal_report.json`
- `module_split_report.json`
- `public_surface_inventory.json`
- `dead_code_removal_report.json`
- `repo_cleanup_scorecard.json`

Required behavior:

- remove or rename misleading top-level structures that no longer represent the real architecture
- split oversized `agents.py` or similarly overloaded modules when the split improves clarity without inventing new abstraction theater
- eliminate stale prototype or compatibility language from public docs, CLI help, and host bundles unless the history is intentionally documented
- remove dead code, duplicate helpers, and thin wrappers that no longer carry real product value
- preserve working public surfaces intentionally; no cleanup rewrite is allowed to silently break supported CLI, artifact, or integration contracts
- finish with stronger tests, stronger docs, and a clearer repo map than before the slice started

Minimum proof:

- one explicit legacy or misleading package surface is removed or retired cleanly
- one oversized module is split into clearer bounded files with tests preserved
- one compatibility shim is either removed or given an explicit documented retention reason
- one full repo-wide proof wall passes, including install health, git safety, and the broad pytest wall

Final doctrine:

- Slice 18 is not optional polish. It is the bounded cleanup pass that turns a long-lived build sequence into a professional finished repository.

## First four slices to build before anything fancy

If you want the highest chance of success, only do these first:
- Slice 01
- Slice 02
- Slice 03
- Slice 04

Then stop, test, and review.

