# RELAYTIC_BUILD_MASTER.md

This is the build entrypoint for Codex.

## Read order

Codex should read these in order:

1. `RELAYTIC_VISION_MASTER.md`
2. `ARCHITECTURE_CONTRACT.md`
3. `IMPLEMENTATION_STATUS.md`
4. `MIGRATION_MAP.md`
5. `RELAYTIC_SLICING_PLAN.md`
6. `docs/specs/aml_frontier_contract.md`

`AGENTS.md` defines the standing repo rules and is assumed to have already been read before the slice-specific build docs.

Current strategic doctrine:

- Relaytic remains the public product and package
- Relaytic-AML is the flagship frontier direction for all pre-academy work from now on
- the Paper Track P0 through P23 is now completed as the mandatory pre-Academy paper path plus hosted-score proof, case-study integration, paper-polish, final source/PDF preflight, author-review layout-hardening, and novelty/distinction hardening; capability-academy slices may start from Slice 16A while final arXiv upload remains a human release action
- the detailed paper-strengthening plan remains in `docs/build_slices/phase_paper_strengthening.md` for audit history and P16-P23 evidence obligations
- paper benchmark work must separate smoke, baseline, competitive, and release budgets; weak first-pass numbers can be retained as honest baselines but must not become headline paper claims without leakage-safe competitive reruns, HPO/search-budget accounting, and publishability gates
- the paper-track execution brief lives at `docs/build_slices/phase_paper_track.md` and the normative slice contract lives in `RELAYTIC_SLICING_PLAN.md`

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
- relevant public benchmark and paper-release freezes that cannot be satisfied by one easy or proxy dataset
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
15A. canonical task contracts, rare-event taxonomy cleanup, and benchmark-vs-deploy separation
15B. model registry expansion and adaptive architecture routing
15C. budgeted HPO, early stopping, and deeper portfolio loops
15D. paper-grade benchmark harness and benchmark rigor
15E. execution DAG, freshness contracts, and artifact reuse
15F. research-imported architecture candidates with replay and shadow trials
15G. objective contracts, split correctness, and metric-truth alignment
15H. first-class competitive family stack
15I. portfolio search engine and serious budget doctrine
15J. temporal engine and time-aware competitiveness
15K. calibration, thresholds, and decision optimization
15L. benchmark truth hardening and paper-claim gates
15M. competitive specialization and benchmark generalization guards
15N. AML domain contract and flagship pivot
15O. entity, graph, and typology reasoning
15P. analyst review optimization and casework
15Q. streaming drift, weak labels, and continual AML learning
15R. AML flagship benchmark, demo, and paper pack
15R-A. finish the AML proof pack, tests, docs, and public-claim alignment
15S. flagship AML demo pack
15T. business-value metrics and analyst-hour proof
15U. strong AML baselines and ablations
15V. raw graph and subgraph ingestion
15V-A. no-lost guide and external context pack
15W. temporal and weak-label upgrade
15X. AML evaluation-environment reframe
15Y. demo-first documentation rewrite
15Z. pre-academy repo credibility cleanup
15Z-R. paper benchmark and release freeze
Paper P0. freeze and commit the 15Z-R baseline
Paper P1. legacy public-surface cleanup
Paper P2. paper thesis and claim contract
Paper P3. benchmark dataset registry and access manifest
Paper P4. PaySim-style temporal benchmark runner
Paper P5. Elliptic graph benchmark loader and provenance
Paper P6. strong tabular baseline suite
Paper P7. graph baseline suite
Paper P8. AMLSim and Elliptic2 blocked-or-supported track
Paper P8-A. Elliptic2 modern-benchmark recovery pilot
Paper P8-B. Elliptic2 competitive and robustness suite
Paper P8-C. modern subgraph reference parity and leakage-resistant cohort protocol
Paper P8-D. paper thesis narrowing and alternative evidence decision
Paper P9. operational AML evaluation layer
Paper P10. reproducible paper table generator
Paper P11. paper draft and figure pack
Paper P12. external dry run and clean-clone proof
Paper P13. arXiv release and attention pack
Paper P14. final arXiv source bundle and clean release candidate
Paper P15. measured system-evaluation proof pack
Paper P16. failure-case evaluation pack
Paper P17. governance machinery ablation pack
Paper P18. governance invariants and adjacent-systems positioning
Paper P19. CTO/arXiv quality gate and hosted detector workflow demonstration, if selected
Paper P19-A. external score-file adapter proof pack, if selected
Paper P19-B. external score case-study and paper integration, if selected
Paper P20. PaySim selection-story cleanup and paper visual/narrative polish
Paper P21. final source/PDF preflight and release changelog
Paper P22. author-review layout hardening and regression closure
Paper P23. novelty and adjacent-systems distinction hardening
16. Relaytic Academy umbrella track, governed capability evolution, and shadow-tested growth
16A. capability registry and capability cards
16B. offline replay packs and shadow mode
16C. arena evaluation and promotion scorecards
16D. hunt campaigns, seeded exploration, and provider feedback
16E. non-core specialist recruitment and retirement
16F. academy mission control and explainability surfaces
17. representation engines, JEPA-style latent world models, and unlabeled local corpora
18. endgame consolidation, legacy removal, and repo-quality hardening

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
61. Paper Track P0
62. Paper Track P1
63. Paper Track P2
64. Paper Track P3
65. Paper Track P4
66. Paper Track P5
67. Paper Track P6
67A. Paper Track P6-A
68. Paper Track P7
69. Paper Track P8
69A. Paper Track P8-A
69B. Paper Track P8-B
69C. Paper Track P8-C
69D. Paper Track P8-D
70. Paper Track P9
71. Paper Track P10
72. Paper Track P11
73. Paper Track P12
74. Paper Track P13
75. Paper Track P14
75A. Paper Track P15
75B. Paper Track P16
75C. Paper Track P17
75D. Paper Track P18
75E. Paper Track P19
75F-A. Paper Track P19-A
75F-B. Paper Track P19-B
75G. Paper Track P20
75H. Paper Track P21
75I. Paper Track P22
75J. Paper Track P23
76. Slice 16
77. Slice 16A
78. Slice 16B
79. Slice 16C
80. Slice 16D
81. Slice 16E
82. Slice 16F
83. Slice 17
84. Slice 18

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
- Slice 12B should come before Slice 13 and the Slice 15 mission-control expansion because Relaytic needs one canonical trace substrate, explicit competing-claim/adjudication contracts, and agent/security evaluation before wider search and full trace-explorer claims become credible
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
- Slices 15A through 15F are the initial model-competitiveness track and are now shipped, but the benchmark rerun proved Relaytic still needs a second performance-recovery track before the academy begins
- Slice 15G is now implemented and freezes objective truth, split health, and benchmark-metric integrity so later performance work stops optimizing broken comparisons
- Slice 15H is now shipped because stronger family coverage only matters once Relaytic knows exactly what it is optimizing and how the benchmark is being judged
- Slice 15I is now implemented and gives Relaytic a staged search-budget doctrine, explicit probe/race/finalist/post-fit artifacts, and a clean separation between lean test budgets and real operator or benchmark budgets
- Slice 15J is now implemented and restores serious temporal work with event-preserving blocked splits, richer lag/delta/rolling/seasonal feature ladders, honest ordinary-versus-lagged baselines, and sequence shadow trials that stay non-live until they beat strong lagged baselines
- Slice 15K is now implemented and turns calibration strategy selection, threshold search, review-budget optimization, abstention posture, and operating-point explanations into first-class performance work on top of the corrected task, family, search, and temporal stack
- Slice 15L is now implemented and closes the pre-academy recovery track by turning benchmark trust, trace identity, protocol conformance, leakage posture, and public-claim safety into one explicit gate
- Slice 15M is now implemented and closes the competitiveness-gap bridge by widening multiclass and rare-event specialization, surfacing adapter activation explicitly, tightening temporal benchmark recovery, partitioning benchmark claims into dev versus holdout posture, and auditing benchmark generalization so the academy does not start from benchmark-shaped blind spots
- Slice 15N should land before the academy because Relaytic needs one hard AML thesis and one explicit AML contract before it starts capability growth
- Slice 15O should come next because AML becomes interesting only when Relaytic can reason over entities, counterparties, typologies, and suspicious subgraphs rather than only rows
- Slice 15P is now implemented and makes analyst-review burden, queue order, and case usefulness first-class AML outputs instead of downstream reporting afterthoughts
- Slice 15Q is now implemented and makes stream posture, weak-label risk, delayed-outcome alignment, and recalibration triggers explicit instead of treating AML like a static supervised table
- Slice 15R-A is now implemented and aligns AML proof-pack docs, tests, CLI, run summary, assist, mission control, and public-claim gates across PaySim-style and flattened Elliptic-style workloads
- Slice 15S is now implemented and turns the AML proof pack into one public-safe flagship demo that a technical reviewer can run without reading the whole repository
- Slice 15T is now implemented and makes analyst-hour value, review-capacity tradeoffs, case-packet completeness, and operational overclaim guards first-class AML outputs
- Slice 15U is now implemented and deepens AML baselines and ablations so the proof story is about what graph, temporal, calibration, threshold, and review-budget machinery contributed
- Slice 15V is now implemented and adds raw graph/subgraph ingestion, graph provenance, graph claim scope, and public graph benchmark cataloging so Elliptic-style work stops being limited to flattened snapshots
- Slice 15V-A is now implemented and adds one no-lost guide, one safe external context pack, and one graceful status path before stronger temporal and benchmark work adds still more artifact families
- Slice 15W is now implemented and upgrades delayed labels, positive-unlabeled posture, threshold drift, and time-window evaluation before Relaytic-AML makes production-shaped temporal claims
- Slice 15X is now implemented and frames Relaytic runs as evaluation environments with model/environment score separation, workflow task matrices, unsafe steering rejection evidence, benchmark-environment scoring, and failure reports
- Slice 15Y is now implemented and moves first contact to the flagship AML demo path with proof artifacts, claim-boundary labels, handbooks, and a paper benchmark runbook before repo cleanup and release freezing
- Slice 15Z is now implemented and adds module-split evidence, repo credibility reports, public-surface inventory, retained extraction boundaries, and benchmark cleanup debt before paper-freeze work
- Slice 15Z-R is now implemented and freezes the relevant benchmark/release pack with catalog coverage, multidimensional result-table schema, explicit claim boundaries, reproducibility attestation, and blocked hard-performance claims until real holdout evidence exists
- Paper Track P0 through P23 now come before Academy work because Relaytic needed a clean repo surface, real numeric benchmark table, external dry run, claim-linted paper, claim-safe public release pack, arXiv-compatible source release candidate, measured user/agent handoff evidence, deterministic failure-case evidence, governance-ablation evidence, formal governance-invariant positioning, hosted-score governance proof, hosted-score case-study integration, PaySim/story/reader-guidance polish, final source/PDF preflight, author-review layout hardening, and explicit novelty/distinction positioning before capability evolution resumed.
- Paper Track P0 is now implemented and freezes the 15Z-R baseline into explicit baseline and verification reports; Paper Track P1 should clean the public surface next
- Paper Track P1 is now implemented and cleans paper-facing public surfaces, records retained compatibility boundaries, and adds Relaytic API/tool aliases
- Paper Track P2 is now implemented and freezes the claim-gated AML evaluation-environment thesis, research questions, contribution story, metric doctrine, related-work seed, and claim taxonomy
- Paper Track P3 is now implemented and freezes dataset source/access posture, license notes, local file expectations, hashes for present local fixtures, split contracts, blocked reasons, and no-auto-download policy
- Paper Track P4 is now implemented and runs the full PaySim-style chronological benchmark with validation-only threshold selection, fixed test evaluation, review-budget/fixed-FPR metrics, supporting-only paper posture, and hard AML/SOTA performance claims still blocked
- Paper Track P5 is now implemented and records raw Elliptic graph provenance, chronological graph split proof, unknown-label scope, claim-safe loader wording, and blocked graph performance/SOTA claims
- Paper Track P6 is now implemented and runs six full-data PaySim tabular baseline families under a train-only leakage-safe feature contract, records versions/fallbacks/budget tiers, selects Extra Trees on validation with test PR-AUC `0.331345`, and blocks headline claims until Paper Track P6-A
- Paper Track P6-A is now implemented and runs a competitive full-data PaySim rerun with prior-step destination-history features, 14 recorded probe trials, five full-training finalists, validation-only calibration/threshold selection, and validation-selected Extra Trees with test PR-AUC `0.638773`; it admits a supporting-only table candidate while keeping headline and hard AML claims blocked before P7
- Paper Track P7 is now implemented and runs the full raw Elliptic bundle under a same-time-step snapshot protocol; validation-selected LightGBM over source plus structural features reports test PR-AUC `0.668756` versus paired source-only `0.664168`, while a weaker PyG GraphSAGE shadow (`0.388907`) remains blocked from graph-neural claims
- Paper Track P8 is now implemented and emits explicit AMLSim/Elliptic2 track decisions: both are currently blocked from first-paper performance claims, with Elliptic2 identified as the highest-upside conditional recovery track and AMLSim reserved for reproducible synthetic proxy evidence
- Paper Track P8-A is now implemented and recovers the Elliptic2 modern path: official labeled-core audit passes over 121,810 subgraphs, RevTrack/RevClassify assets and low-memory embedding derivation are pinned, the original paper/code split discrepancy is recorded, and an exploratory context pilot reports test PR-AUC `0.935255` while remaining blocked from paper-table or SOTA claims until P8-B
- Paper Track P8-B is now implemented and tests that modern path honestly: the validation-selected pooled-moments candidate records repeated official test PR-AUC `0.943240 +/- 0.000882` and row-order-independent content-hash test PR-AUC `0.929669 +/- 0.000538`, while remaining below reported full-shot `RevClassifyDS=0.974` and exposing that the RevTrack-evaluable cohort covers only `110902/121810` audited current-core rows; P8-C has now confirmed this is supporting-only evidence
- Paper Track P8-C is now implemented and blocks modern-subgraph parity claims honestly: faithful RevClassify replay was explicitly requested but local preconditions are missing, the current-core to RevTrack-evaluable mapping is not proven, and a strict entity-disjoint component split is degenerate with `110889/110902` rows in one identity component; P8-D was required before P9
- Paper Track P8-D is now implemented and accepts the narrowed first-paper thesis: Relaytic-AML proceeds as a claim-gated AML evaluation-environment paper, P8-B is supporting modern-context evidence only, P8-C is a limitation and claim-firewall, Elliptic2 is not a performance contribution, and P9 is unblocked
- Paper Track P9 is now implemented and materializes operational AML evidence under the P8-D thesis boundary: PaySim and Elliptic supporting rows now include review-budget metrics, false-positive burden proxies, case-packet completeness state, and a claim guard that unblocks P10 while blocking hard business-value, headline operational, Elliptic2 performance-contribution, and SOTA claims
- Paper Track P10 is now implemented and generates reproducible paper tables from committed artifacts: every numeric metric cell has dataset, split, command, run-directory, artifact, claim-state, budget-tier, leakage-posture, and publishability-gate provenance, so P11 drafting is unblocked while hard/headline claims remain blocked
- Paper Track P11 is now implemented and generates the first claim-linted Relaytic-AML draft plus deterministic figures, limitations matrix, and claim-lint report from P10 evidence; P12 clean-clone proof is unblocked while hard AML, headline, SOTA, RevClassify parity, graph-neural superiority, and hard business-value claims remain blocked
- Paper Track P12 is now implemented and proves the external paper-smoke path with a clean-clone checklist, optional isolated full-profile install probe, P10/P11 regeneration checks, leak scan, failure report, and release go/no-go gate; P13 is unblocked only for claim-safe evaluation-environment release language while hard AML, headline, SOTA, RevClassify parity, graph-neural superiority, and hard business-value claims remain blocked
- Paper Track P13 is now implemented and produces the claim-safe arXiv release pack: final generated draft, citable references, paper tables, submission checklist, public attention pack, release manifest, and allowed-public-claims report. The release status is claim-safe evaluation-environment only; hard/headline performance claims stay blocked.
- Paper Track P14 is now implemented and produces the final arXiv source release candidate: deterministic LaTeX source, bibliography copy, converted PDF figures, citation and package audits, and a release-candidate checklist. Upload stays blocked until real author metadata, local TeX/PDF inspection, and clean tag-target proof exist.
- Paper Track P15 is now implemented and produces a measured system-evaluation proof pack: guide onboarding, partial-run recovery, rowless external-agent handoff, optional local-LLM advisory boundaries, MCP-style tool discovery, and paper claim gates are checked deterministically before P13/P14 release regeneration. The evidence is protocol-level only; it does not claim a human study, production deployment, or hard operational impact.
- Paper Track P16 is now implemented as the first strengthening stage: it adds concrete deterministic failure-case evaluation for leakage, test-selection, over-claim, handoff-redaction, and interrupted-run recovery guardrails.
- Paper Track P18 is now implemented as the third strengthening stage: it formalizes governance invariants, maps each invariant to evidence artifacts or stress cases, adds adjacent-systems positioning, and keeps the generated paper framed as an evaluation-lab/governance systems paper rather than a detector-superiority paper. Paper Track P19-A is now implemented as the hosted-score proof stage: it creates rowless external score-file governance artifacts, evidence cells, claim gates, and handoff-redaction evidence without promoting detector superiority. Paper Track P19-B is now implemented as the paper-integration stage: it turns the P19-A proof into a compact hosted-score case study, claim map, paper panel, and reproduction card. Paper Track P20 is now implemented as the PaySim/story/reader-guidance polish stage: it separates probe screening from full-finalist selection, audits reader guidance from paper to README, and makes P14 require the P20 audit before final preflight. Paper Track P21 is now implemented as the final source/PDF preflight and release changelog stage. Paper Track P22 is now implemented as the author-review layout hardening stage: it compresses main-body system evaluation, moves dense audit detail to appendix captions, anchors figures and command labels, refreshes Figure 4 and rowless-handoff wording, regenerates the canonical paper bundle, and keeps upload blocked on human release checks. Paper Track P23 is now implemented as the novelty/distinction hardening stage: it makes the "around detectors and agents" evaluation-evidence governance claim explicit without adding benchmark numbers and makes final source/PDF preflight require the P23 reports. The track is evidence-first and preserves all hard/headline detector-claim blockers.
- Slice 16 is the umbrella academy track and should not be treated as one undifferentiated implementation pass; it exists so later post-AML capability-evolution work has one coherent contract
- Slice 16A should start the academy by freezing capability cards and registry truth before replay, hunt, or recruitment logic appears
- Slice 16B should come before any live academy authority because replay packs and shadow mode are the main trust boundary for future capability growth
- Slice 16C should come before hunt-heavy or roster-heavy work because promotion and quarantine logic must be deterministic before Relaytic starts scouting aggressively
- Slice 16D should come after 16C because hunt campaigns should feed the same replay, shadow, and arena pipeline rather than inventing a parallel innovation loop
- Slice 16E should come after the tool-focused academy slices because non-core specialist recruitment and retirement should reuse the same proof pipeline instead of becoming a second roster mechanism
- Slice 16F should close the academy track by turning candidate, shadow, hunt, and promotion truth into one human- and agent-usable surface
- Slice 17 should remain the optional late-stage representation-engine slice and should land after the academy track so Relaytic can first learn to evolve governed capabilities before it experiments with deeper latent representation engines
- Slice 18 should land last as an explicit consolidation/remediation pass so Relaytic does not carry misleading legacy packages, stale compatibility shims, oversized modules, or prototype-era naming into its finished product state

Current repo state:

- implemented through Slice 15Z-R plus Paper Track P0 through P23, with Slice 15R-A AML proof-pack alignment, Slice 15S flagship AML demo-bundle packaging, Slice 15T guarded business-value and analyst-hour proof, Slice 15U AML baseline and ablation relevance proof, Slice 15V raw graph/subgraph ingestion, Slice 15V-A no-lost guide/status/context-pack export, Slice 15W temporal weak-label claim gating, Slice 15X AML evaluation-environment scoring, Slice 15Y demo-first public documentation, Slice 15Z repo credibility cleanup, Slice 15Z-R paper/release freeze, Paper Track P0 baseline freeze, Paper Track P1 public-surface cleanup, Paper Track P2 thesis/claim contract, Paper Track P3 dataset registry, Paper Track P4 PaySim temporal benchmark, Paper Track P5 Elliptic graph provenance, Paper Track P6 tabular baseline suite, Paper Track P6-A competitive PaySim gate, Paper Track P7 Elliptic graph baseline suite, Paper Track P8 hard-track decisions, Paper Track P8-A Elliptic2 modern recovery, Paper Track P8-B competitive/robustness evidence, Paper Track P8-C reference-parity/cohort gate, Paper Track P8-D thesis narrowing, Paper Track P9 operational AML evaluation, Paper Track P10 reproducible table generation, Paper Track P11 paper draft generation, Paper Track P12 external dry-run proof, Paper Track P13 claim-safe arXiv release pack, Paper Track P14 arXiv source release candidate, Paper Track P15 measured system-evaluation proof pack, Paper Track P16 failure-case evaluation pack, Paper Track P17 governance machinery ablation pack, Paper Track P18 governance-invariant positioning, Paper Track P19-A external score-file adapter proof pack, Paper Track P19-B hosted-score case-study integration, Paper Track P20 PaySim/story/reader-guidance polish, Paper Track P21 final source/PDF preflight, Paper Track P22 author-review layout hardening, and Paper Track P23 novelty and adjacent-systems distinction hardening now landed
- next execution target: Slice 16A capability registry and capability cards; final arXiv upload remains a human release action
- latest landed pulse slice: Slice 12A
- latest trace-and-safety slice: Slice 12B
- latest handoff-and-learnings slice: Slice 12D
- latest search-and-execution slice: Slice 13
- latest release-and-packaging slice: Slice 13A
- latest runtime-and-permission slice: Slice 13B
- latest background-and-resume slice: Slice 13C
- latest mission-control-and-proof slice: Slice 15
- next planned paper action: final human arXiv upload steps only: release tag, human PDF review, upload-package confirmation, and clean tag-target confirmation
- next planned academy follow-on: Slice 16A, after P23 closed the paper-positioning follow-on
- final planned cleanup follow-on after Slice 17: Slice 18
- after Slice 13, every later slice that changes operator-visible behavior, install/dependency posture, or long-running runtime behavior must extend the same mission-control, onboarding, dojo-visibility, pulse-visibility, trace/eval visibility, differentiated handoff, durable-learnings, workspace-continuity, result-contract, iteration-planning, search-controller, release-safety, permission-mode, and background-job surfaces rather than leaving the UI stale until late polish
- the canonical future product-contract pack for that work now lives under `docs/specs/` and should be treated as normative during later implementation, including [model_competitiveness_contract.md](docs/specs/model_competitiveness_contract.md), [performance_recovery_contract.md](docs/specs/performance_recovery_contract.md), [aml_frontier_contract.md](docs/specs/aml_frontier_contract.md), [aml_benchmark_pack.md](docs/specs/aml_benchmark_pack.md), [capability_academy_contract.md](docs/specs/capability_academy_contract.md), [mission_control_contract.md](docs/specs/mission_control_contract.md), [handoff_result_migration.md](docs/specs/handoff_result_migration.md), [learnings_migration_contract.md](docs/specs/learnings_migration_contract.md), and [external_agent_continuation_contract.md](docs/specs/external_agent_continuation_contract.md) for already-shipped and future mission control, model competitiveness, performance recovery, AML proof/productization, academy, handoff, learnings, and external-agent continuation surfaces
- mission-control and browser-facing work should also follow [relaytic_ui_frontier_review.md](docs/relaytic_ui_frontier_review.md): static HTML remains the fallback, but the product direction is an AML investigation board, agent console, belief-delta/claim-firewall views, review-budget simulation, trace replay, and eventually a local live UI server backed by canonical artifacts

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
- academy-aware operating surfaces that turn the shipped specialist/tool/intervention/branch trace model into polished replay, promotion, and change-attribution experiences
- broader runtime agent/security harnesses that expand the shipped control-injection, tool-misuse, branch-safety, and skeptical-override checks into a larger proof pack before broader autonomy becomes default
- outcome learning rather than run-only learning
- a richer long-term memory stack with retention, compaction, pinning, and replay rules so later specialists inherit durable lessons instead of analog hints alone
- richer data-fabric reasoning that can suggest joins, entity histories, or additional data before wasting search budget
- a stronger search controller that widens or prunes branches, changes handoff depth, and allocates HPO effort based on expected decision value under budget
- a performance-recovery track that turns Relaytic from a strong system wrapped around a still-limited family stack into a much more competitive modeling system with stronger objective contracts, broader first-class families, deeper portfolio search, temporal competitiveness, calibration and decision optimization, and explicit paper-claim gates
- academy-aware mission control that makes branch structure, confidence, intervention history, traces, incumbent-versus-Relaytic state, capability growth, and change attribution legible to humans and agents
- a governed capability-academy track that can scout, shadow-test, promote, demote, and retire tools or non-core specialists through deterministic proof instead of ad hoc growth
- an optional representation engine that can learn from large unlabeled local corpora and improve retrieval, anomaly support, and temporal state understanding without replacing deterministic adjudication

Slices 07, 09A, 09B, 09C, 09D, 09F, and 11 are the major groundwork novelty unlocks.
Slices 10, 10B, 10C, and 10A are the current category-shift unlocks that turned Relaytic from a governed inference lab into a more explicit decision-and-discovery system with skeptical steering. Slice 11A added real incumbent pressure, Slice 11B completed the first adoption unlock because humans and external agents can now launch, inspect, and demo the system from one coherent control surface, and Slice 11C made that surface legible enough to act as a real MVP cockpit instead of only a technical dashboard.
Slices 15A through 15M are now shipped as the initial model-competitiveness track plus the full performance-recovery and benchmark-generalization bridge. Slices 15N through 15Z-R are the shipped AML foundation, proof-pack alignment, flagship demo-bundle, guarded business-value track, baseline/ablation relevance track, raw graph/subgraph ingestion track, no-lost guide/context-pack track, temporal weak-label claim-gating track, evaluation-environment scoring track, demo-first documentation track, repo credibility cleanup, and paper/release freeze. Paper Track P0 through P23 are the completed mandatory pre-Academy arXiv path plus the implemented strengthening stages: clean the public surface, freeze the paper thesis, register datasets, run PaySim-style and Elliptic-style benchmarks, evaluate strong tabular and graph baselines, rerun PaySim under an explicit competitive paper budget, decide AMLSim/Elliptic2 support honestly, use P8-D's narrowed thesis so Elliptic2 remains supporting context rather than a performance contribution, add operational evidence, generate reproducible tables, draft the paper, dry-run from a clean clone, release only if claim gates pass, generate an arXiv-compatible source release candidate, measure guide/handoff/system-evaluation behavior, add deterministic failure-case evidence, add governance-ablation evidence, formalize governance invariants with adjacent-systems positioning, prove hosted external-score governance, integrate that proof as a reader-facing case study, polish the PaySim selection story plus reader-guidance path, produce the final source/PDF preflight plus release changelog, harden the author-review layout without adding benchmark claims, and make the paper's category claim explicit: Relaytic-AML is an evaluation-evidence governance layer around detectors and agents, not a detector, generic experiment tracker, model-card substitute, SAR-writing assistant, agent benchmark, or general agent-governance product. P9 added operational evidence, P10 generated reproducible claim-guarded tables, P11 generated a claim-linted draft and figure pack, P12 generated the external dry-run/go-no-go proof, P13 generated the claim-safe arXiv draft, reference pack, tables, attention pack, submission checklist, release manifest, and public-claim whitelist, P14 generated LaTeX source, PDF figures, citation/package audits, P15 generated the measured system-evaluation proof pack, P16 generated the failure-case evaluation pack, P17 generated the governance-ablation pack, P18 generated the governance-invariant and adjacent-systems reports, P19-A generated the external score-file proof pack, P19-B generated the hosted-score case-study integration pack, P20 generated the narrative/guidance/visual-table polish audit, P21 generated the final source/PDF preflight reports plus release changelog, P22 regenerated the canonical paper bundle after layout-hardening generator changes, and P23 generated the novelty-positioning audit and adjacent-systems distinction matrix. Slices 16A through 16F are the later governed capability-evolution track, Slice 17 remains the long-range optional representation-engine bet after the academy track, and Slice 18 is the planned endgame consolidation/remediation pass after all feature work.

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
