You are revising this paper into a professional arXiv-ready systems/ML paper. The goal is not cosmetic polishing. The goal is to make the paper credible to ML researchers, AML/financial-crime engineers, and frontier AI company reviewers.

Core positioning:
Relaytic-AML is a local-first, agent-assisted AML evaluation lab. Its contribution is not SOTA AML detection. Its contribution is an evidence architecture that binds data posture, temporal/graph split validity, leakage controls, model/search artifacts, review-budget operating points, and public claim boundaries into reproducible “evidence cells”.

Rewrite the paper around this thesis.

Tasks:

1. Restructure the paper into a conventional professional structure:
   - Abstract
   - 1 Introduction
   - 2 Related Work
   - 3 System Overview
   - 4 Evidence Cell and Claim-Gate Design
   - 5 Experimental Protocol
   - 6 Results
   - 7 System Evaluation
   - 8 Limitations and Threats to Validity
   - 9 Reproducibility
   - Conclusion

2. Merge or remove repetitive sections:
   - Merge “Contribution and Scope”, “Design Thesis”, and parts of “What Relaytic-AML Is For”.
   - Merge “Local-First Agent Architecture”, “Agent Runtime”, and “Evidence Operating Layer” into a sharper system-design section.
   - Keep “Future Work” short or fold it into Limitations.

3. Add a clear research-question block near the end of the introduction:
   RQ1: Can Relaytic-AML produce reproducible evidence cells for AML-style temporal and graph tasks?
   RQ2: Can it prevent leakage-prone or unsupported claims from being promoted?
   RQ3: Can the local-first artifact graph support rowless handoff to external agents while preserving provenance?
   RQ4: Do the benchmark rows demonstrate useful, bounded detector evidence under explicit split and budget contracts?

4. Add a contributions paragraph with exactly 3–4 concrete contributions:
   - A local-first artifact graph and role-scoped agent runtime for AML evaluation.
   - An evidence-cell schema tying each metric to dataset, split, command, artifact, budget, leakage posture, operating point, and claim state.
   - A release/claim-gating harness that converts artifacts into tables/figures/manuscript claims while blocking unsupported interpretations.
   - Public benchmark demonstrations on PaySim, Elliptic, and Elliptic2 context rows, with strict claim boundaries.

5. Add missing experimental detail. Do not fabricate results. If the repository contains the information, extract it. If not, add explicit TODO_EVIDENCE markers and create a list of missing evidence.
   Required tables:
   - Dataset/task table: dataset, task, number of samples/nodes/subgraphs, positive rate, split rule, train/val/test sizes, allowed features, forbidden/leakage features, metric.
   - Model/search table: model families, feature families, hyperparameter/search budget, calibration/threshold rule, random seeds.
   - Evidence-cell table: dataset, metric, value, split, command/artifact path, budget tier, leakage posture, claim state.
   - Ablation table for PaySim: baseline, leakage-safe features, prior-step destination history, competitive search, final model.
   - System-evaluation table: each deterministic check/task, artifact output, pass/fail, and which paper claim it supports.

6. Strengthen the Results section:
   - Results must not just repeat the table.
   - For each dataset, explain what was tested, what changed vs baseline, what the metric means, and what claim is allowed.
   - PaySim should be the main empirical demonstration.
   - Elliptic should be framed as graph-feature/provenance evidence.
   - Elliptic2 should be clearly framed as modern-context/limitation evidence, not a performance contribution.

7. Improve the abstract:
   Write a tighter abstract with four sentences:
   - Problem: AML ML results are hard to trust because privacy, temporal validity, graph provenance, leakage, review capacity, and claims are often disconnected.
   - Method: Relaytic-AML introduces a local-first artifact graph, role-scoped agents, evidence cells, and claim gates.
   - Evidence: summarize PaySim/Elliptic/Elliptic2 numbers with cautious wording.
   - Contribution: the paper contributes a reproducible evaluation-lab architecture, not a SOTA detector claim.

8. Improve figures:
   - Figure 1 should be the main architecture figure: Local data/artifacts → role-scoped agents → evidence cells → claim gates → paper/release/handoff.
   - Figure 2 should show the evidence-cell schema, not only bars.
   - Figure 3 should show benchmark PR-AUC and review-budget metrics.
   - Figure 4 should show claim-gate examples: allowed claim vs blocked claim vs evidence needed.
   Make all figures publication-style, not slide-style. Avoid tiny text.

9. Add a “Threats to Validity” subsection:
   Include:
   - synthetic PaySim limitation
   - public blockchain data not equal to bank AML
   - possible benchmark mismatch with RevClassify/Elliptic2
   - deterministic system checks are not the same as human usability studies
   - no production/analyst-hour validation
   - risk of overfitting to public benchmark protocols

10. Add professional polish:
   - Replace placeholder author/contact fields.
   - Use consistent terminology: evidence cell, claim gate, artifact graph, review budget.
   - Reduce repeated “this does not claim…” wording.
   - Ensure all claims are backed by artifacts, citations, or explicit limitations.
   - Do not invent stronger claims or missing results.
   - Generate a TODO_EVIDENCE.md file listing any missing values needed before arXiv submission.

11. After editing:
   - Build the PDF.
   - Render all pages.
   - Check for overfull boxes, tiny figure text, awkward page breaks, table overflow, placeholder text, and broken citations.
   - Report what was changed and what evidence remains missing before arXiv submission.