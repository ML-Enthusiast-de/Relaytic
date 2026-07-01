# Paper Track P16-P21 - Relaytic-AML paper-strengthening path

## Status

Stage 4A is implemented. P16 produces deterministic failure-case evidence, P17 produces deterministic governance-ablation evidence, P18 produces formal governance-invariant plus adjacent-systems positioning evidence, and P19-A produces the external score-file governance proof pack. The P19 CTO/arXiv quality-gate review is present, and P19-B is now the next triggerable paper-facing integration stage after P19-A.

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
| `start Stage 4` | P19 | CTO/arXiv quality gate and hosted detector workflow demonstration, if selected |
| `start Stage 4A` | P19-A | External score-file adapter proof pack, if selected |
| `start Stage 4B` | P19-B | External score case-study and paper integration, if P19-A lands |
| `start Stage 5` | P20 | PaySim selection-story cleanup and evaluation-narrative tightening |
| `start Stage 6` | P20 | Figure and table polish after the new evidence exists |
| `start Stage 7` | P21 | Final source/PDF preflight and release changelog |

Stage 4 requires a short decision before implementation: prefer an external-score adapter fixture unless the user explicitly chooses a lightweight graph-native fixture or RevClassifyDS-style scorecard adapter. The quality-gate artifact for that decision is `docs/reports/paper_cto_quality_gap_review.md`.

## Required Order

1. **Paper Track P16 - failure-case evaluation pack** - implemented
   Added deterministic failure fixtures and artifacts for leakage-column injection, test-set selection violation, over-strong claim attempts, rowless handoff redaction, and interrupted-run recovery. Generated a machine-readable report and a paper-ready failure-case table.

2. **Paper Track P17 - governance machinery ablation pack** - implemented
   Compares the full Relaytic-AML path against deterministic disabled-component fixtures: no claim gate, no leakage policy, no rowless handoff redaction, no evidence-cell required fields, and no interrupted-run recovery guide. Reports unsupported claims released, leakage features allowed, raw fields exported, missing provenance fields, publishable tables generated, and recovery next actions available.

3. **Paper Track P18 - governance invariants and adjacent-systems positioning** - implemented
   Adds formal release/governance invariants and connects them to P16/P17 checks. Adds a compact related-work comparison against model cards, datasheets, reproducibility checklists, MLOps experiment tracking, agent benchmarks, and AML detector papers.

4. **Paper Track P19 - CTO/arXiv quality gate and hosted detector workflow demonstration**
   Use the CTO/arXiv quality review to choose whether to implement a hosted detector workflow. Preferred route: external score-file adapter. If feasible, demonstrate that Relaytic-AML can host a stronger detector workflow through an external score-file adapter, a lightweight graph-native fixture, or a RevClassifyDS-style external scorecard adapter. The claim is substrate hosting, evidence routing, redaction, and claim governance, not detector superiority.

5. **Paper Track P19-A - external score-file adapter proof pack** - implemented
   Implements the preferred P19 route. Ingests a rowless external detector-score artifact with schema, hash, dataset, split, metric, leakage, and claim-state metadata; emits evidence cells, a score manifest, a publishability gate, a handoff redaction report, a route decision, and a paper-safe summary. The claim remains hosted detector-output governance, not detector superiority.

6. **Paper Track P19-B - external score case-study and paper integration**
   Consume the P19-A artifact family and turn it into a reviewer-facing case study: what score artifact entered, what Relaytic checked, what it emitted, what was redacted, which claims were allowed, and which stronger claims stayed blocked. The paper should gain a compact case-study table or figure panel plus nearby interpretation, not a new detector-performance headline.

7. **Paper Track P20 - paper narrative and visual polish**
   Clarify the PaySim model-selection story without inventing rationale, tighten evaluation wording around system behavior rather than detector PR-AUC, and polish Figures 1-4 plus dense tables after P16-P19 evidence is available.

8. **Paper Track P21 - final source/PDF preflight and changelog**
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

P16 through P19-A introduce committed, machine-readable reports under `docs/reports/`. P16 writes `paper_failure_case_eval.json`, `paper_failure_case_table.json`, `paper_failure_case_manifest.json`, and `paper_failure_case_summary.md`. P17 writes `paper_governance_ablation_eval.json`, `paper_governance_ablation_matrix.json`, `paper_governance_ablation_manifest.json`, and `paper_governance_ablation_summary.md`. P18 writes `paper_governance_invariants.json`, `paper_adjacent_systems_comparison.json`, `paper_invariant_manifest.json`, and `paper_invariant_summary.md`. P19-A writes `paper_external_score_route_decision.json`, `paper_external_score_schema.json`, `paper_external_score_manifest.json`, `paper_external_score_evidence_cells.json`, `paper_external_score_claim_gate.json`, `paper_external_score_handoff_eval.json`, and `paper_external_score_summary.md`.

- failure-case evaluation manifest and per-case reports
- governance ablation matrix
- evidence-cell required-field check report
- leakage-policy injected-risk report
- test-selection-violation gate report
- over-strong-claim routing report
- rowless handoff redaction report
- interrupted-run recovery report
- governance-invariant proof map
- adjacent-systems positioning comparison
- CTO/arXiv quality-gap review
- hosted detector or score-workflow route decision
- `paper_external_score_route_decision.json`
- `paper_external_score_schema.json`
- `paper_external_score_manifest.json`
- `paper_external_score_evidence_cells.json`
- `paper_external_score_claim_gate.json`
- `paper_external_score_handoff_eval.json`
- `paper_external_score_summary.md`
- `paper_external_score_case_study.json`
- `paper_external_score_paper_panel.json`
- `paper_external_score_claim_map.json`
- `paper_external_score_repro_card.md`

## Stage 1 Acceptance

Stage 1 is complete when:

1. `relaytic release-safety paper-failure-eval` writes the P16 report family under `docs/reports/`.
2. The report covers leakage-column injection, test-set selection violation, over-strong claim attempts, rowless handoff redaction, and interrupted-run recovery.
3. P13 release generation fails closed if P16 evidence is missing.
4. The generated manuscript includes a publication-clean failure-case table and preserves the evaluation-lab claim boundary.
5. Focused P13-P16 tests and LaTeX/source audits pass without overfull table warnings.

## Stage 2 Acceptance

Stage 2 is complete when:

1. `relaytic release-safety paper-governance-ablation` writes the P17 report family under `docs/reports/`.
2. The report compares the full governance path with disabled fixtures for public-claim gating, leakage policy, rowless handoff redaction, metric-cell required fields, and interrupted-run recovery.
3. P13 release generation fails closed if P17 evidence is missing.
4. The generated manuscript includes a publication-clean governance-ablation table and states that the ablation is system/governance evidence, not detector performance evidence.
5. Focused P13-P17 tests and LaTeX/source audits pass without overfull table warnings.

## Stage 3 Acceptance

Stage 3 is complete when:

1. `relaytic release-safety paper-invariants` writes the P18 report family under `docs/reports/`.
2. The report records current invariants for metric-cell provenance, claim-strength monotonicity, leakage and selection firewalls, rowless handoff, interrupted-run recovery, benchmark role separation, and local-first release safety.
3. Every current invariant maps to at least one evidence artifact plus a failure, ablation, or limitation boundary.
4. The generated manuscript includes an adjacent-systems comparison and a governance-invariant evidence table without promoting detector-superiority claims.
5. Focused P13-P18 tests and LaTeX/source audits pass without overfull table warnings.

## Stage 4 Acceptance

Stage 4 is complete when:

1. `docs/reports/paper_cto_quality_gap_review.md` exists and compares Relaytic-AML against recent visible arXiv patterns in agent evaluation, ML research-agent reliability, and AML graph/detector papers.
2. The review states whether the current paper is a good independent systems/evaluation paper and whether it meets a top visible arXiv / AML CTO bar.
3. A route decision chooses one of: external score-file adapter, lightweight graph-native fixture, RevClassifyDS-style scorecard adapter, or skip P19 and move to P20.
4. If a hosted detector workflow is implemented, every score artifact must carry hash, schema, dataset role, split role, metric policy, leakage posture, and allowed claim state.
5. The generated paper may claim hosted detector-output governance only if the new artifact pack passes. It must not claim detector superiority, production AML readiness, graph-neural novelty, or RevClassifyDS parity.

## Stage 4A Acceptance (completed)

Stage 4A is complete when:

1. `relaytic release-safety paper-external-score-proof` writes the P19-A report family under `docs/reports/`.
2. The command fails closed when the score artifact or required metadata is absent.
3. The accepted score artifact records hash, schema, dataset role, split role, metric policy, leakage posture, and claim state.
4. The rowless handoff report redacts raw rows, entity identifiers, private paths, and unapproved score payload fields.
5. P13/P14 generation can only use bounded hosted-detector-output governance wording; detector superiority, production AML readiness, graph-neural novelty, and RevClassifyDS parity remain blocked.
6. Focused P13-P19A tests, source scans, and leak scans pass.

## Stage 4B Acceptance

Stage 4B is complete when:

1. `relaytic release-safety paper-external-score-integration` consumes the P19-A report family and writes the P19-B paper-integration artifacts under `docs/reports/`.
2. The generated manuscript includes one compact hosted-score case study or figure panel with interpretation near the evidence.
3. The case study shows the adapter input contract, schema/hash posture, metric policy, rowless redaction posture, allowed claim state, and blocked stronger claims.
4. The reproducibility card gives copy-paste-safe Windows and macOS/Linux commands for regenerating the P19-A/P19-B evidence without exposing raw rows, private paths, secrets, or licensed data.
5. The paper wording stays inside the hosted-detector-output governance boundary and does not promote detector superiority, graph-neural novelty, production AML readiness, RevClassifyDS parity, or real-bank validation.
6. Focused P13-P19B tests, source scans, paper static scans, and leak scans pass.

## Stage 0 Acceptance (completed)

Stage 0 is complete when:

1. This planning file exists.
2. `RELAYTIC_BUILD_MASTER.md` and `RELAYTIC_SLICING_PLAN.md` reference P16-P21 as a triggerable paper-strengthening follow-on.
3. `IMPLEMENTATION_STATUS.md` recorded that the track was registered and that P16 was the next paper-strengthening slice at Stage 0 registration time.
4. A regression test asserts that the plan includes P16-P21, the required failure cases, the governance-ablation metrics, and the no-overclaim gates.
5. No paper generator, benchmark result, PDF, or arXiv source behavior changes in Stage 0.
