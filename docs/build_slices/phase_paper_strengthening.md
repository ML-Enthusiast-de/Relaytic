# Paper Track P16-P21 - Relaytic-AML paper-strengthening path

## Status

Stage 1 is implemented. P16 now produces deterministic failure-case evidence and the generated paper consumes it as a publication table. P17 is the next triggerable stage.

## Intent

This follow-on track moves Relaytic-AML from a credible independent arXiv systems paper toward a stronger ML systems/evaluation paper by adding measured evidence that the local-first agentic evaluation lab prevents concrete failures, improves auditability, and supports reproducible agent-assisted AML workflows.

The track preserves the current paper boundary:

- Relaytic-AML is a local-first evaluation and governance substrate for financial-crime ML.
- Detector benchmarks exercise the lab, but they do not define a new detector-SOTA claim.
- No result, figure, table, or public claim may be added without generated evidence.
- Hard real-bank AML superiority, RevClassifyDS parity, graph-neural detector novelty, production deployment, and analyst-impact claims remain blocked unless future evidence gates explicitly promote them.

## Trigger Map

Use these user-facing triggers to advance one bounded stage at a time:

| User trigger | Paper track slice | Scope |
|---|---|---|
| `start Stage 1` | P16 | Failure-case evaluation pack |
| `start Stage 2` | P17 | Governance machinery ablation pack |
| `start Stage 3` | P18 | Governance invariants and adjacent-systems positioning |
| `start Stage 4` | P19 | Hosted detector workflow demonstration, if selected |
| `start Stage 5` | P20 | PaySim selection-story cleanup and evaluation-narrative tightening |
| `start Stage 6` | P20 | Figure and table polish after the new evidence exists |
| `start Stage 7` | P21 | Final source/PDF preflight and release changelog |

Stage 4 requires a short decision before implementation: prefer an external-score adapter fixture unless the user explicitly chooses a lightweight graph-native fixture or RevClassifyDS-style scorecard adapter.

## Required Order

1. **Paper Track P16 - failure-case evaluation pack** - implemented
   Added deterministic failure fixtures and artifacts for leakage-column injection, test-set selection violation, over-strong claim attempts, rowless handoff redaction, and interrupted-run recovery. Generated a machine-readable report and a paper-ready failure-case table.

2. **Paper Track P17 - governance machinery ablation pack**
   Compare the full Relaytic-AML path against disabled-gate fixtures: no claim gate, no leakage policy, no rowless handoff redaction, and no evidence-cell required fields. Report unsupported claims released, leakage features allowed, raw fields exported, missing provenance fields, publishable tables generated, and recovery next actions available.

3. **Paper Track P18 - governance invariants and adjacent-systems positioning**
   Add formal release/governance invariants and connect them to P16/P17 checks. Add a compact related-work comparison against model cards, datasheets, reproducibility checklists, MLflow/W&B/DVC-style tracking, agent benchmarks, and AML detector papers.

4. **Paper Track P19 - hosted detector workflow demonstration**
   If feasible, demonstrate that Relaytic-AML can host a stronger detector workflow through an external score-file adapter, a lightweight graph-native fixture, or a RevClassifyDS-style external scorecard adapter. The claim is substrate hosting and evidence routing, not detector superiority.

5. **Paper Track P20 - paper narrative and visual polish**
   Clarify the PaySim model-selection story without inventing rationale, tighten evaluation wording around system behavior rather than detector PR-AUC, and polish Figures 1-4 plus dense tables after P16-P19 evidence is available.

6. **Paper Track P21 - final source/PDF preflight and changelog**
   Regenerate the paper PDF and arXiv source, run paper/source/static checks, inspect rendered pages, and produce a short changelog listing new tests, new artifacts, changed tables/figures, and claims intentionally not made.

## Non-Negotiable Gates

- No invented benchmark result, citation, artifact path, or observed signal.
- No detector-SOTA, real-bank superiority, RevClassifyDS parity, graph-neural novelty, production deployment, or hard analyst-impact claim.
- Every new paper claim must map to an evidence cell, failure-case artifact, ablation artifact, audit check, or limitation.
- Deterministic fixtures are allowed for system-evaluation evidence, but they must be labeled as system-level safety/audit fixtures rather than detector benchmarks.
- New tables and figures must be generated from artifacts or explicitly marked as schematic.
- Windows and macOS/Linux reproduction commands must remain copy-paste safe.
- The public paper/source scan must stay clean of TODO, FIXME, placeholder, unresolved, pending, dummy, and temp language.
- Stage work stops at the requested trigger unless the user explicitly asks to continue.

## Expected Evidence Artifacts

P16 and P17 introduce committed, machine-readable reports under `docs/reports/`. P16 writes `paper_failure_case_eval.json`, `paper_failure_case_table.json`, `paper_failure_case_manifest.json`, and `paper_failure_case_summary.md`. P17 should add the governance-ablation family.

- failure-case evaluation manifest and per-case reports
- governance ablation matrix
- evidence-cell required-field check report
- leakage-policy injected-risk report
- test-selection-violation gate report
- over-strong-claim routing report
- rowless handoff redaction report
- interrupted-run recovery report

## Stage 1 Acceptance

Stage 1 is complete when:

1. `relaytic release-safety paper-failure-eval` writes the P16 report family under `docs/reports/`.
2. The report covers leakage-column injection, test-set selection violation, over-strong claim attempts, rowless handoff redaction, and interrupted-run recovery.
3. P13 release generation fails closed if P16 evidence is missing.
4. The generated manuscript includes a publication-clean failure-case table and preserves the evaluation-lab claim boundary.
5. Focused P13-P16 tests and LaTeX/source audits pass without overfull table warnings.

## Stage 0 Acceptance (completed)

Stage 0 is complete when:

1. This planning file exists.
2. `RELAYTIC_BUILD_MASTER.md` and `RELAYTIC_SLICING_PLAN.md` reference P16-P21 as a triggerable paper-strengthening follow-on.
3. `IMPLEMENTATION_STATUS.md` recorded that the track was registered and that P16 was the next paper-strengthening slice at Stage 0 registration time.
4. A regression test asserts that the plan includes P16-P21, the required failure cases, the governance-ablation metrics, and the no-overclaim gates.
5. No paper generator, benchmark result, PDF, or arXiv source behavior changes in Stage 0.
