# Paper Track P16-P23 - Relaytic-AML paper-strengthening path

## Status

Stage 9/9 is implemented. P16 produces deterministic failure-case evidence, P17 produces deterministic governance-ablation evidence, P18 produces formal governance-invariant plus adjacent-systems positioning evidence, P19-A produces the external score-file governance proof pack, P19-B turns that proof into a reader-facing hosted-score case study, P20 cleans the PaySim selection story plus reader-facing polish, P21 produces the final source/PDF preflight reports plus release changelog, P22 hardens author-review layout/readability over the final source/PDF bundle, and P23 hardens the paper's novelty and adjacent-systems distinction. Slice 16A remains the next academy implementation slice; final arXiv upload still requires author tag selection, human page review, and a clean tag target.

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
| `start Stage 8` | P22 | Author-review layout hardening and regression closure |
| `start Stage 9` | P23 | Novelty and adjacent-systems distinction hardening |

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

6. **Paper Track P19-B - external score case-study and paper integration** - implemented
   Consumes the P19-A artifact family and turns it into a reviewer-facing case study: what score artifact entered, what Relaytic checked, what it emitted, what was redacted, which claims were allowed, and which stronger claims stayed blocked. The paper gains a compact hosted-score case-study table plus nearby interpretation, not a new detector-performance headline.

7. **Paper Track P20 - paper narrative and visual polish** - implemented
   Clarify the PaySim model-selection story without inventing rationale, tighten evaluation wording around system behavior rather than detector PR-AUC, and polish Figures 1-4 plus dense tables after P16-P19 evidence is available.

8. **Paper Track P21 - final source/PDF preflight and changelog** - implemented
   Regenerate the paper PDF and arXiv source, run paper/source/static checks, inspect rendered pages, and produce a short changelog listing new tests, new artifacts, changed tables/figures, and claims intentionally not made.

9. **Paper Track P22 - author-review layout hardening and regression closure** - implemented
   Compress the main-body system-evaluation table, move dense audit detail to appendix captions, anchor figures, keep platform command labels with command blocks, refresh Figure 4 and rowless-handoff wording, regenerate the canonical Markdown/LaTeX/PDF bundle, and rerun final preflight without adding benchmark claims.

10. **Paper Track P23 - novelty and adjacent-systems distinction hardening** - implemented
    Makes the paper's novelty lane unmistakable before public submission without adding benchmark numbers or stronger detector claims. It clarifies that Relaytic-AML is not a detector replacement, not generic experiment tracking, not a model card or datasheet substitute, not a general agent benchmark, not an agent-governance trust layer, and not a SAR/narrative-writing assistant. Its distinct claim is a local-first AML evaluation-evidence governance layer around detectors and agents: evidence cells bind local runs to provenance, rowless handoff lets external agents inspect state without raw data, and claim gates decide which public or paper-facing interpretations are admissible.

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

P16 through P23 introduce committed, machine-readable reports under `docs/reports/`. P16 writes `paper_failure_case_eval.json`, `paper_failure_case_table.json`, `paper_failure_case_manifest.json`, and `paper_failure_case_summary.md`. P17 writes `paper_governance_ablation_eval.json`, `paper_governance_ablation_matrix.json`, `paper_governance_ablation_manifest.json`, and `paper_governance_ablation_summary.md`. P18 writes `paper_governance_invariants.json`, `paper_adjacent_systems_comparison.json`, `paper_invariant_manifest.json`, and `paper_invariant_summary.md`. P19-A writes `paper_external_score_route_decision.json`, `paper_external_score_schema.json`, `paper_external_score_manifest.json`, `paper_external_score_evidence_cells.json`, `paper_external_score_claim_gate.json`, `paper_external_score_handoff_eval.json`, and `paper_external_score_summary.md`. P19-B writes `paper_external_score_case_study.json`, `paper_external_score_paper_panel.json`, `paper_external_score_claim_map.json`, `paper_external_score_repro_card.md`, and `paper_external_score_integration_manifest.json`. P20 writes `paper_paysim_selection_story_review.json`, `paper_reader_guidance_audit.json`, `paper_visual_table_polish_audit.json`, `paper_narrative_polish_manifest.json`, and `paper_polish_readiness.md`. P21 writes `paper_final_pdf_preflight.json`, `paper_final_source_preflight.json`, `paper_final_preflight_manifest.json`, and `paper_final_release_changelog.md`. P22 refreshes the P20/P21 polish and preflight reports plus the canonical Markdown/LaTeX/PDF artifacts after layout-hardening generator changes; it does not add benchmark metrics or headline detector claims. P23 writes `paper_novelty_positioning_audit.json`, `paper_adjacent_systems_distinction_matrix.json`, `paper_novelty_positioning_manifest.json`, and `paper_novelty_positioning_summary.md`, and makes P14/P21 source preflight require those artifacts before final author review.

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
- `paper_external_score_integration_manifest.json`
- `paper_paysim_selection_story_review.json`
- `paper_reader_guidance_audit.json`
- `paper_visual_table_polish_audit.json`
- `paper_narrative_polish_manifest.json`
- `paper_polish_readiness.md`
- `paper_final_pdf_preflight.json`
- `paper_final_source_preflight.json`
- `paper_final_preflight_manifest.json`
- `paper_final_release_changelog.md`
- P22 refreshed `paper_visual_table_polish_audit.json`, `paper_final_pdf_preflight.json`, `paper_final_source_preflight.json`, `paper_final_preflight_manifest.json`, and the canonical Markdown/LaTeX/PDF bundle after layout-hardening generator changes
- P23 novelty/distinction artifacts: `paper_novelty_positioning_audit.json`, `paper_adjacent_systems_distinction_matrix.json`, `paper_novelty_positioning_manifest.json`, `paper_novelty_positioning_summary.md`, refreshed adjacent-systems comparison, and regenerated Markdown/LaTeX/PDF artifacts

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

## Stage 4B Acceptance (completed)

Stage 4B is complete when:

1. `relaytic release-safety paper-external-score-integration` consumes the P19-A report family and writes the P19-B paper-integration artifacts under `docs/reports/`.
2. The generated manuscript includes one compact hosted-score case study or figure panel with interpretation near the evidence.
3. The case study shows the adapter input contract, schema/hash posture, metric policy, rowless redaction posture, allowed claim state, and blocked stronger claims.
4. The reproducibility card gives copy-paste-safe Windows and macOS/Linux commands for regenerating the P19-A/P19-B evidence without exposing raw rows, private paths, secrets, or licensed data.
5. The paper wording stays inside the hosted-detector-output governance boundary and does not promote detector superiority, graph-neural novelty, production AML readiness, RevClassifyDS parity, or real-bank validation.
6. Focused P13-P19B tests, source scans, paper static scans, and leak scans pass.

## Stage 5/6 Acceptance (completed)

Stage 5/6 is complete when:

1. `relaytic release-safety paper-narrative-polish` writes the P20 polish reports under `docs/reports/`.
2. The PaySim story separates small-sample probe screening from full-training finalist selection and does not invent a rationale for XGBoost versus Extra Trees beyond recorded validation evidence.
3. Every main result has nearby interpretation and the detector-superiority boundary remains intact.
4. The README and paper guide readers through the README, manuscript, and copy-paste-safe Windows plus macOS/Linux commands before optional deep JSON audit artifacts.
5. P14 source generation requires the P20 polish manifest before final PDF/source preflight.
6. Focused P13-P20 tests, source scans, paper static scans, and leak scans pass.

## Stage 7 Acceptance (completed)

Stage 7 is complete when:

1. `relaytic release-safety paper-final-preflight` writes the P21 final preflight reports and release changelog under `docs/reports/`.
2. Source preflight checks the public-marker scan, wrapped reproduction commands, numbered hosted-score case study, AI assistance disclosure naming, release identifier, P20 polish manifest, P14 source manifest, and source-package audit.
3. PDF preflight checks the compiled PDF, source/review PDF synchronization, LaTeX log, embedded fonts, and PDF metadata.
4. The final manifest reports `ready_for_author_review_not_tagged`, keeps `arxiv_upload_ready` false, and records the remaining human upload blockers.
5. Focused P13-P21 tests, LaTeX compile, font scan, static marker scan, and leak scan pass.

## Stage 8 Acceptance (completed)

Stage 8 is complete when:

1. The generated paper keeps a compact main-body system-evaluation table and moves dense audit details to appendix tables with real LaTeX captions.
2. Figures are anchored so result interpretation prose and captions do not separate awkwardly, and command-block platform labels cannot strand alone at the bottom of a page.
3. Figure 4 and rowless-handoff wording are reader-facing, with no generated-log fragments or private path exposure.
4. The canonical Markdown, LaTeX source, and PDF are regenerated from the generators rather than manually edited.
5. Final preflight reports `ready_for_author_review_not_tagged`, focused P13-P21 paper tests and strengthening-plan regression tests pass, the leak scan passes, fonts and metadata are clean, and rendered-page inspection covers figures, tables, appendix audit records, and command blocks.

## Stage 9 Acceptance (completed)

Stage 9 is complete when:

1. The generated manuscript has a concise "what is new" or equivalent distinction paragraph/table after related work that names the closest adjacent categories without sounding defensive.
2. The adjacent-systems comparison explicitly covers AML detector/benchmark papers, AML LLM triage systems, agentic SAR/compliance narrative systems, agent-governance/trust layers, MLOps experiment tracking, model cards, datasheets, reproducibility checklists, and agent-evaluation benchmarks.
3. The paper states that companies would use Relaytic-AML around detectors and agent-assisted workflows to govern local evidence, rowless handoff, benchmark context, and admissible claims; they would not use it as a detector replacement.
4. A compact distinction matrix records each adjacent system type, what it optimizes, what Relaytic-AML does not claim, and the distinct Relaytic-AML role.
5. The abstract, conclusion, and related-work framing preserve the exact claim boundary: local-first AML evaluation-evidence governance with artifact-backed evidence cells, rowless external-agent handoff, and deterministic claim gates.
6. New citations are added only for verified existing work. Candidate categories include AML LLM triage, agentic AML compliance narratives, and agent-governance/trust layers.
7. Regression checks fail if the manuscript loses the around-detectors framing, omits the AML LLM/agent-governance distinctions, or strengthens detector superiority, RevClassifyDS parity, production AML, hard business-value, or SOTA claims.
8. Regenerated Markdown, LaTeX, PDF, source/package preflight, focused paper tests, citation checks, and leak scan pass.

## Stage 0 Acceptance (completed)

Stage 0 is complete when:

1. This planning file exists.
2. `RELAYTIC_BUILD_MASTER.md` and `RELAYTIC_SLICING_PLAN.md` reference P16-P23 as the paper-strengthening follow-on, with P16-P23 implemented.
3. `IMPLEMENTATION_STATUS.md` records that P23 is implemented and that Slice 16A is the next engineering slice while public submission remains a human release action.
4. A regression test asserts that the plan includes P16-P23, the required failure cases, the governance-ablation metrics, the no-overclaim gates, and the P23 novelty/distinction acceptance criteria.
5. No paper generator, benchmark result, PDF, or arXiv source behavior changes in Stage 0.
