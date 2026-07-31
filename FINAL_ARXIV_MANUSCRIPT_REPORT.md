# Final arXiv Manuscript Report

Date: 2026-07-31

Scope: final scientific, editorial, build, and presentation review of the Relaytic-AML manuscript and directly generated publication assets. No benchmark was rerun or changed. No commit, tag, push, rebase, or other Git-history operation was performed.

## Release Decision

The manuscript is ready for the author's final human read. The canonical PDF builds successfully, the paper-specific test suite passes, the arXiv source candidate validates, the bibliography is internally complete, and the rendered PDF has been inspected page by page. The exact-revision archival bundle cannot be produced until the author commits the final changes because final mode intentionally rejects a dirty worktree.

The unresolved Elliptic2 upstream-provenance limitation remains explicit. Elliptic2 is presented only as an external-artifact governance case. It is not presented as a reconstructed cohort, parity result, or numerical comparison with published RevClassifyDS performance.

## Final Abstract

> Anti-money laundering (AML) machine-learning experiments are difficult to audit when data residency, temporal validity, graph provenance, agent assistance, review capacity, and public reporting are managed separately. Relaytic-AML is a local-first evaluation lab in which capability-scoped agents and deterministic harnesses convert local runs into provenance-bearing measurements and evidence-bounded release decisions. The architecture is evaluated with temporal PaySim and Elliptic workflows, an external-artifact governance case, and deterministic failure, handoff, and release-gate fixtures. The selected PaySim and Elliptic test PR-AUC point estimates are 0.6388 and 0.6688. Each is reported together with its split, feature, budget, calibration, and test-exposure contract. Across the tested system fixtures, required metric provenance was preserved, raw records were excluded from rowless handoff, and all six injected unsupported-claim cases were blocked. Relaytic-AML contributes an auditable evaluation, governance, and reproducibility architecture for agent-assisted AML experimentation rather than a new detector or detector-superiority result.

## Final Conclusion

> Relaytic-AML demonstrates an artifact-centered approach to agent-assisted financial-crime machine-learning evaluation. The framework binds measurements to source posture, split contracts, feature and leakage policy, model budget, operating points, and test-exposure status, while separate claim gates control what can be released. In the evaluated temporal, graph, external-artifact, and deterministic fixture workflows, Relaytic-AML preserved the tested provenance requirements, produced raw-row-free handoff records, supported recovery from interrupted state, and blocked the injected unsupported claims. These results establish the behavior of the implemented evaluation and release-governance mechanisms, not detector superiority, privacy certification, or production effectiveness. Human and institutional studies remain necessary to assess their effect on expert decisions and operational outcomes.

## Substantive Changes

1. Replaced the abstract with an architecture-centered summary that reports only the selected PaySim and Elliptic point estimates and the exact deterministic-fixture claim boundary.
2. Tightened the introduction around functional stages and capability-scoped roles. Defined rowless handoff at first use and aligned the research questions with the evaluated evidence.
3. Revised Related Work into a neutral comparison with adjacent evaluation, provenance, governance, and agent-reliability systems. Retained ResearchLoop, FactReview, and safety-gated MCP coverage without claiming category-wide priority.
4. Reworked Table 1 for compact, neutral scope descriptions and readable placement.
5. Removed OpenClaw, Claude, and Codex from manuscript text, figures, captions, tables, and public reproduction instructions. The architecture is described through functional integrations and external-agent handoff.
6. Rebuilt Figure 1 around source audit, experiment design, bounded execution, review, and release-governance stages.
7. Kept the evidence-cell and interpretation-gate distinction while moving the two complete JSON records to the appendix. The main body now presents the field-level contract without duplicating the appendix.
8. Removed every occurrence of the external value 0.9740 from the generated manuscript and arXiv source.
9. Centralized the three Elliptic2 count states in one Experimental Protocol paragraph. The Results section contains the local estimates and their admissibility limits without repeating the full reconciliation.
10. Removed Elliptic2 from Figure 4. The figure now separates within-task ranking metrics from review-queue operating-point metrics.
11. Revised the Elliptic2 table labels to use external-artifact context and explicitly state that upstream cohort equivalence is not established.
12. Renamed Table 4's information boundary to distinguish deliberately excluded fields from unavailable upstream information.
13. Limited the complete pinned-artifact SHA-256 to one manuscript occurrence while preserving exact hashes in repository manifests and provenance reports.
14. Tightened PaySim and Elliptic result interpretation without changing any reported metric, split, feature, calibration, selection, test-exposure, or queue-budget fact.
15. Replaced internal release jargon in deterministic evaluation with explicit reader-facing behavior. The result is reported as all 6/6 injected unsupported-claim cases blocked, without extending the result to semantic correctness, usability, privacy, or production validation.
16. Consolidated limitations while preserving all material constraints, including synthetic PaySim evidence, prior PaySim test exposure, validation-window reuse, the unisolated destination-history contribution, Elliptic feature posture, single-seed point estimates, unavailable prediction-level intervals, Elliptic2 provenance, deterministic-fixture scope, privacy limits, and local-data requirements.
17. Streamlined reproducibility around clean-clone fixtures, benchmark-data requirements, the pinned external artifact, and exact release-integrity behavior. Internal editorial commands are absent from the manuscript's minimal workflow and the primary README quickstart.
18. Replaced the AI-assistance disclosure with a concise responsibility statement that names no commercial product.
19. Replaced the conclusion with the requested mechanism-level summary and explicit scientific boundary.
20. Applied a controlled language pass to reduce product-manual phrasing, anthropomorphic role inventories, defensive repetition, promotional language, and inconsistent external-artifact terminology.
21. Regenerated Markdown, LaTeX, bibliography copies, vector figures, tables, manifests, PDF, review-candidate source ZIP, and release-integrity reports from canonical generator sources.
22. Updated regression tests for the new abstract, Figure 4 scope, vendor-neutral language, public command list, relocated JSON examples, citation invariants, and Elliptic2 provenance boundary.
23. Corrected the final typesetting defects: Table 2 now uses an italic note label, JSON listings wrap without visible continuation symbols, and `paper-final-preflight` remains unbroken. The single-author manuscript contains no first-person plural wording.

## Scientific and Citation Audit

- Citation keys used by manuscript: 33
- Bibliography entries: 33
- Missing citation keys: 0
- Unused bibliography entries: 0
- Duplicate bibliography keys: 0
- Unresolved LaTeX citations or references: 0
- FactReview author attribution: Xu et al.
- Full 64-character pinned-artifact hash occurrences in manuscript: 1
- `0.9740` occurrences in manuscript and generated arXiv source: 0
- Elliptic2 mentions in abstract: 0
- Elliptic2 metrics in Figure 4: 0
- Vendor-specific agent-product names in manuscript: 0
- Placeholders or evidence TODO markers in publication source: 0

Critical current references were checked against their recorded primary publication or arXiv metadata. The generated bibliography has no missing, unused, or duplicate entry. No new scientific result or bibliographic fact was inferred during this pass.

## Elliptic2 Provenance Status

The provenance gap is unresolved and has not been invented away. Relaytic consumes an already constructed RevTrack-format `data_df.pkl` artifact. The repository does not construct it and does not contain the upstream construction code or row-level mapping. The supplied partitions define only the local evaluation state. The manuscript therefore makes no reconstruction, cohort-equivalence, RevClassifyDS-parity, or published-performance-comparison claim.

The local artifact result remains secondary context for governance behavior. The external published score 0.9740 is absent from the paper, and the local Elliptic2 estimates are absent from both the abstract and the main numerical figure.

## Build and Validation Record

All commands were run from the repository root with Python 3.11 unless stated otherwise.

| Command | Result |
|---|---|
| `py -3.11 -m relaytic.ui.cli release-safety paper-release --format json` | PASS. Regenerated canonical paper assets and reports. |
| `py -3.11 -m relaytic.ui.cli release-safety paper-narrative-polish --format json` | PASS. Internal editorial audit only. It is not exposed in the public workflow. |
| `py -3.11 -m relaytic.ui.cli release-safety paper-novelty-positioning --format json` | PASS. Internal positioning audit only. It is not presented as scientific validation. |
| `py -3.11 -m relaytic.ui.cli release-safety paper-release-integrity --candidate --format json` | PASS. Built and validated the dirty-worktree review candidate. |
| `py -3.11 -m relaytic.ui.cli release-safety paper-arxiv-source --format json` | PASS. Regenerated and validated the arXiv source directory. |
| `pdflatex -interaction=nonstopmode -halt-on-error main.tex` in `docs/paper/arxiv_src` | PASS. First LaTeX pass. |
| `bibtex main` in `docs/paper/arxiv_src` | PASS. Bibliography generated. |
| `pdflatex -interaction=nonstopmode -halt-on-error main.tex` in `docs/paper/arxiv_src` | PASS. Cross-reference pass. |
| `pdflatex -interaction=nonstopmode -halt-on-error main.tex` in `docs/paper/arxiv_src` | PASS. Final LaTeX pass. |
| `py -3.11 -m relaytic.ui.cli release-safety paper-final-preflight --format json` | PASS. Status: `ready_for_author_review_not_tagged`. |
| `$files=@((Get-ChildItem -LiteralPath tests -Filter 'test_paper_track_p*.py' \| Sort-Object Name \| ForEach-Object {$_.FullName})); $files += (Resolve-Path tests/test_pre_arxiv_corrections.py).Path; py -3.11 -m pytest -q $files` | PASS. 146 tests passed in 75.71 seconds. |
| `py -3.11 -m pytest -m prepush -q` with a 120-second limit | INCOMPLETE. The broader repository suite exceeded the local time limit and emitted no failure before termination. |
| `py -3.11 -m pytest -m prepush -q` with a 600-second limit | INCOMPLETE. The broader repository suite again exceeded the local time limit and emitted no failure before termination. This is not part of the required paper-track acceptance suite. |
| `git diff --check` | PASS. No whitespace errors. Git reported only expected LF-to-CRLF working-copy notices. |
| `pdfinfo docs/paper/relaytic_aml_arxiv_draft.pdf` | PASS. Title, author, metadata, and 28-page count verified. |
| `pdffonts docs/paper/relaytic_aml_arxiv_draft.pdf` | PASS. Fonts embedded; no Type 3 fonts. |
| Complete manuscript and arXiv-source scans for prohibited values, vendor names, placeholders, unresolved references, and unsupported claim forms | PASS. |
| Page-by-page raster inspection of all 28 pages, with focused inspection of the abstract, Table 1, Figures 1-4, Tables 2-7, appendix examples, limitations, reproducibility, disclosure, conclusion, and bibliography | PASS. No clipping, overlap, unreadable figure text, or orphaned heading observed. |

The broader `prepush` marker spans substantially more than the requested paper track and did not complete within ten minutes on this machine. No failing test was observed in either attempt. The bounded paper suite, generation pipeline, source validation, LaTeX build, and final preflight all completed successfully.

## Publication Artifacts

- Canonical review PDF: `docs/paper/relaytic_aml_arxiv_draft.pdf`
- PDF page count: 28
- Canonical and review PDF SHA-256: `64C29FB23C2E3917AD0C817157E523EB7545E910DA146E69C7209AD811AFE47A`
- Review-candidate arXiv ZIP: `dist/paper-release/review-candidate/relaytic_aml_arxiv_source.zip`
- Review-candidate ZIP SHA-256: `4FB1D32663FCD8F79901ACC587A46E84E53E543713B399ACC9186E149D0E1DA3`
- Review-candidate ZIP size: 110,117 bytes
- ZIP members: `main.tex`, `references.bib`, and four vector PDF figures
- Remaining LaTeX overfull boxes: 0
- Remaining LaTeX underfull boxes: 0
- Remaining undefined citations or references: 0
- Remaining LaTeX or package warnings: 0

The review-candidate ZIP is intentionally not the immutable final-release bundle. After the author commits the accepted manuscript, `paper-release-integrity --final` must create a bundle whose embedded revision matches that commit.

## Exact Changed Files

The final worktree contains the following publication-related tracked modifications and untracked additions. Generated assets are included because they are part of the review surface.

```text
IMPLEMENTATION_STATUS.md
README.md
docs/paper/README.md
docs/paper/arxiv_src/figures/figure_1_claim_gate_flow.pdf
docs/paper/arxiv_src/figures/figure_2_supporting_pr_auc.pdf
docs/paper/arxiv_src/figures/figure_3_review_budget.pdf
docs/paper/arxiv_src/figures/figure_4_publishability_matrix.pdf
docs/paper/arxiv_src/main.tex
docs/paper/arxiv_src/references.bib
docs/paper/figures/figure_1_claim_gate_flow.svg
docs/paper/figures/figure_3_review_budget.svg
docs/paper/figures/figure_4_publishability_matrix.svg
docs/paper/figures/figure_manifest.json
docs/paper/references.bib
docs/paper/relaytic_aml_arxiv_draft.md
docs/paper/relaytic_aml_arxiv_draft.pdf
docs/paper/relaytic_aml_draft.md
docs/paper/tables/table_1_evidence_summary.md
docs/paper/tables/table_manifest.json
docs/reports/elliptic2_competitive_budget_contract.json
docs/reports/elliptic2_publishability_gate.json
docs/reports/elliptic2_relaytic_candidate_search_trace.json
docs/reports/paper_arxiv_source_manifest.json
docs/reports/paper_arxiv_submission_checklist.md
docs/reports/paper_attention_pack.md
docs/reports/paper_claim_gate_records.json
docs/reports/paper_claim_lint_report.json
docs/reports/paper_final_pdf_preflight.json
docs/reports/paper_invariant_manifest.json
docs/reports/paper_limitations_matrix.json
docs/reports/paper_novelty_positioning_audit.json
docs/reports/paper_p24_artifact_conflict_audit.json
docs/reports/paper_p24_baseline_metric_snapshot.json
docs/reports/paper_p24_bibliography_verification.json
docs/reports/paper_p24_evidence_authority.json
docs/reports/paper_p24_metric_consistency_audit.json
docs/reports/paper_p24_protocol_disclosure_audit.json
docs/reports/paper_p24_reference_provenance_audit.json
docs/reports/paper_p24_release_manifest.json
docs/reports/paper_p24_reproduction_semantics.json
docs/reports/paper_p24_visual_layout_audit.json
docs/reports/paper_public_claims_allowed.json
docs/reports/paper_publishability_matrix.json
docs/reports/paper_release_manifest.json
docs/reports/paper_table_provenance.json
src/relaytic/release_safety/elliptic2_competitive.py
src/relaytic/release_safety/paper_arxiv_source.py
src/relaytic/release_safety/paper_draft.py
src/relaytic/release_safety/paper_narrative_polish.py
src/relaytic/release_safety/paper_novelty_positioning.py
src/relaytic/release_safety/paper_release.py
src/relaytic/release_safety/paper_release_integrity.py
src/relaytic/release_safety/paper_table_generator.py
tests/test_paper_track_p13.py
tests/test_paper_track_p14.py
tests/test_paper_track_p15.py
tests/test_paper_track_p20.py
tests/test_paper_track_p23.py
tests/test_paper_track_p24.py
tests/test_paper_track_p26.py
PRE_ARXIV_FIX_REPORT.md
docs/reports/elliptic2_cohort_provenance_limitation.md
tests/test_pre_arxiv_corrections.py
FINAL_ARXIV_MANUSCRIPT_REPORT.md
```

The ignored review-candidate bundle was also regenerated at `dist/paper-release/review-candidate/`.

## Required Human Actions

1. Read the canonical 28-page PDF once without source context, checking scientific meaning, author identity, and tone.
2. Review the complete Git diff, including generated reports and the permanent Elliptic2 provenance limitation.
3. Decide whether the two timed-out broad `prepush` runs warrant an overnight full-repository test before publication. The complete paper-specific suite already passes.
4. Commit the accepted source and generated publication assets.
5. With a clean worktree, run `py -3.11 -m relaytic.ui.cli release-safety paper-release-integrity --final --format json` to create the exact-revision bundle.
6. Inspect that bundle, push the commit, and rerun final integrity with `--verify-public`. Add a release tag only after it resolves locally and remotely to the same public commit.
7. Upload the exact validated source ZIP and matching PDF to arXiv. Treat arXiv as a preprint venue, not peer review.

READY_FOR_FINAL_HUMAN_READ
