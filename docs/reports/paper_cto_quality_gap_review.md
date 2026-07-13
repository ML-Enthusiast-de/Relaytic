# Relaytic-AML CTO / arXiv Quality Gap Review

Date: 2026-07-01

## Perspective

This review asks whether the current Relaytic-AML paper would read as a strong modern arXiv systems/evaluation paper to a senior ML leader at an AML-heavy company such as PayPal. The review does not change any detector claim. It checks whether the current story, evidence, and paper shape are likely to earn attention from strong technical readers.

arXiv does not provide an official "high-ranked paper" standard. The comparison here uses recent visible patterns from strong arXiv papers in adjacent areas: agent evaluation, ML research-agent reliability, and modern AML graph/detector work.

## External Comparison Signals

Recent agent-evaluation papers such as PaperBench, MLR-Bench, MLE-bench, RE-Bench, and FIRE-Bench are strong because they define a clear evaluation object, publish rubrics or tasks, include many tasks or attempts, compare systems or humans, and report failure modes rather than only success cases:

- PaperBench evaluates AI agents on replication of 20 ICML papers with 8,316 gradable tasks and human comparison: https://arxiv.org/abs/2504.01848
- MLR-Bench evaluates agents on 201 open-ended ML research tasks and highlights fabricated or invalid experimental results as a central reliability issue: https://arxiv.org/abs/2505.19955
- MLE-bench uses 75 Kaggle-style ML engineering competitions and compares to public human leaderboards: https://arxiv.org/abs/2410.07095
- RE-Bench uses realistic ML R&D environments and compares against human-expert attempts: https://arxiv.org/abs/2411.15114
- FIRE-Bench frames agents around rediscovery of scientific insights: https://arxiv.org/abs/2602.02905

Recent AML papers are strong for a different reason: they add harder benchmarks, real or realistic graph data, detector families, throughput claims, or industry-facing scale.

- TransXion introduces a high-fidelity AML benchmark with roughly 3 million transactions and 50,000 entities, richer profile-aware simulation, and broad detector evaluation: https://arxiv.org/abs/2604.17420
- BlazingAML presents a scalable multi-stage graph-mining system and reports large CPU/GPU speedups on IBM AML data: https://arxiv.org/abs/2604.12241
- LineMVGNN proposes a line-graph-assisted multi-view GNN and reports results on Ethereum plus an industry partner payment dataset: https://arxiv.org/abs/2603.23584
- Elliptic2 introduces a large subgraph AML dataset and modern subgraph framing: https://arxiv.org/abs/2404.19109

## Current Relaytic-AML Strengths

The current paper has a credible and useful systems thesis:

- local-first AML evaluation rather than hosted-data leakage by default
- specialist agents with deterministic artifact gates rather than chat-only memory
- evidence cells tying metrics to dataset, split, command, artifact, budget, leakage posture, and claim state
- claim gates that block detector-superiority wording unless evidence exists
- rowless handoff for external agents
- deterministic failure cases and governance ablations
- formal governance invariants mapped to generated evidence artifacts

This is enough for a serious independent arXiv systems paper. It does not by itself establish broad production AML validation.

## CTO Read

A PayPal-style AML ML CTO would probably find the architecture interesting, especially the local-first handoff and claim governance. The likely positive reaction is:

- "This could reduce experiment-governance chaos."
- "This could help teams use coding agents without leaking rows or overstating results."
- "The evidence-cell model is a useful bridge between research, model risk, and compliance review."

The likely skeptical reaction is:

- "Show me this around a realistic AML detector or score stream."
- "Show me it handles the shape of our work: entity graphs, alert queues, model versions, redaction, review capacity, and audit questions."
- "Show me a comparison against a normal experiment tracker plus a normal model-card/checklist workflow."
- "Show me what breaks when an agent tries to overclaim, touch private data, or use a test set."
- "Do not sell me PaySim as an AML breakthrough."

The current paper answers the overclaim/privacy/governance questions reasonably well. It does not yet answer the realistic-hosted-detector workflow question strongly enough.

## Quality Verdict

Current quality level:

- Good independent arXiv systems/evaluation paper: yes.
- Credible AML governance/evaluation-lab paper: yes.
- Top visible arXiv paper in the style of major agent-evaluation or AML benchmark papers: not yet.
- External technical-review signal: the paper would benefit from one more concrete enterprise-relevant demonstration.

The paper should not try to compete with TransXion, BlazingAML, LineMVGNN, or Elliptic2 as a detector or dataset paper. Its best route is to show that Relaytic-AML is the local-first governance substrate those kinds of detector workflows should run through.

## Missing Pieces Before "Top Paper" Positioning

1. Hosted detector or score-stream demonstration.
   Relaytic should ingest a realistic external detector score file or benchmark output, attach evidence cells, enforce leakage/redaction rules, route claims, and export rowless context. This can be done without claiming detector novelty.

2. Adjacent-systems comparison with observed behavior.
   The current comparison is conceptual. A stronger paper would run the same miniature AML experiment through Relaytic-style artifacts versus a tracker/checklist-only workflow and report concrete differences: missing provenance fields, claim-blocking behavior, rowless handoff fields, and recovery state.

3. CTO-grade operational story.
   The paper should more directly explain how a company would use Relaytic: experiment intake, local data posture, detector score attachment, analyst review budget, model-risk review, external-agent help, release claim gating, and audit handoff.

4. Stronger system-evaluation scale.
   The current deterministic fixtures are useful. For higher credibility, add more task variants or a small external-review rubric: what a reviewer can find, what an external agent receives, what is redacted, and which claims are blocked.

5. Cleaner "why now" framing.
   The strongest modern hook is not "AML benchmark result"; it is "agentic ML workflows are becoming capable enough to create scientific-looking outputs, so high-stakes local domains need artifact-backed claim governance."

## Recommended Next Stage

The next stage should not immediately chase a bigger detector score. It should choose and implement a hosted-detector workflow demonstration:

Preferred route: external score-file adapter.

Why: it is the cleanest proof that Relaytic-AML can wrap modern AML detectors without needing to claim detector novelty. The score file can be synthetic or public-benchmark-derived, but the paper claim must be about evidence routing, redaction, provenance, and claim gating.

Acceptance bar:

- score rows are never exposed in rowless handoff
- score artifact has hash, schema, dataset role, split role, metric policy, and allowed claim state
- paper can say Relaytic-AML hosted a detector-output workflow
- paper cannot say Relaytic-AML produced detector superiority
- release gates fail if the score artifact lacks split, metric, leakage, or claim-state metadata

If that route is blocked, skip the detector demo and move to P20 narrative/visual polish with the limitation stated clearly.
