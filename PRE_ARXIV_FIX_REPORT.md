# Relaytic-AML Pre-arXiv Correction Report

## Scope And Outcome

This pass resolved the remaining Elliptic2 manuscript blocker through an
evidence-aligned reduction of claim scope. It did not infer or reconstruct an
unknown upstream transformation. No benchmark value, dataset count, figure
metric, experimental result, or detector conclusion was changed.

The manuscript now presents the local Elliptic2 run only as non-comparable
context from a pinned external RevTrack-format artifact. The unresolved
upstream provenance is retained as a permanent limitation in
`docs/reports/elliptic2_cohort_provenance_limitation.md`. It is no longer a
manuscript release blocker because the paper makes no cohort-equivalence,
reference-reproduction, parity, or detector-superiority claim from that run.

## Scientific Boundary

Three count states are kept distinct:

- locally audited current Elliptic2 core: 121,810 subgraphs, 2,763 positives
- RevTrack paper: 121,810 subgraphs, 2,718 positives
- pinned external artifact: 110,902 rows, 2,578 positives

The pinned artifact supplies 88,738/2,054 training rows/positives,
11,059/252 validation rows/positives, and 11,105/272 test rows/positives. Its
`data_df.pkl` SHA-256 is
`2baa712b67382aeade8d5e72dd07ddbffb1029b359a048c80a2300a3e3abc220`.

The repository does not contain the upstream construction pipeline, a
row-level map to the current core, or exclusion reasons. The differences among
the three states therefore remain unexplained. The paper states this directly.

## Manuscript Corrections

1. The abstract reports the local Elliptic2 estimate of
   `0.9432 +/- 0.0009` only as pinned, non-comparable external-artifact
   context. It contains no external `0.9740` value.
2. Methods identify the artifact, full SHA-256, supplied `TRN`/`VAL`/`TST`
   labels, exact split counts, and unavailable upstream provenance.
3. Results state prior exposure to the supplied test split and describe the
   repeated estimate as neither blind nor untouched.
4. The published RevClassifyDS `0.9740` appears exactly once in the main text,
   directly cited to Song et al. (2024), and labeled external and
   non-comparable.
5. The external value was removed from the main evidence table and Figure 4.
   Neither surface implies a shared cohort, reproduction, parity, or
   leaderboard comparison.
6. Limitations and reproducibility distinguish clean-clone checks from the
   local artifact-dependent context run.
7. `ResearchLoop` and `Elliptic2` are protected from awkward LaTeX
   hyphenation. The resulting source compiles without underfull or overfull
   boxes.
8. Generated reports use repository-relative artifact references. A
   machine-local Windows path found during the safety scan was removed from
   the canonical generator and covered by a regression test.

## Citation And Source Audit

The generated bibliography contains 33 unique keys. All 33 are cited, with no
missing, unused, or duplicate keys. The authoritative and arXiv-source copies
are byte-identical with SHA-256
`173c41f2d54d31d73481e06a36484f2e9e14d08e4d45895f22ada462dc92be48`.

The extracted PDF contains one `0.9740` occurrence. It is in the sentence that
attributes the RevClassifyDS result to Table 1 of Song et al. (2024). The
abstract contains none. Citation generation resolves the corresponding
textual citation as `\citet{song2024revtrack}`.

The arXiv source contains no unresolved citation or reference, local machine
path, secret pattern, stale prototype name, or pending-evidence marker.

## Build And Validation

The canonical paper workflow completed with these final states:

- paper release: `ready_for_claim_safe_arxiv_release`
- narrative polish: `ready_for_final_pdf_preflight`
- novelty positioning: `ready_for_final_author_review`
- release integrity: `release_candidate_ready_for_human_upload`
- arXiv source: `ready_for_source_release_candidate`
- final PDF preflight: `ready_for_author_review_not_tagged`

The source was compiled with:

```text
pdflatex -interaction=nonstopmode -halt-on-error main.tex
bibtex main
pdflatex -interaction=nonstopmode -halt-on-error main.tex
pdflatex -interaction=nonstopmode -halt-on-error main.tex
```

The final PDF has 29 A4 pages. LaTeX and BibTeX report no undefined
references, undefined citations, package warnings, underfull boxes, or
overfull boxes. All fonts are embedded and subset, with no Type 3 fonts.
Metadata contains the paper title, Tobias Gehra as author, and the build date.

Validation results:

- complete paper and provenance test set: 145 passed
- push-readiness smoke group: 1 passed
- architecture and agent-assist group: 22 passed
- final source/PDF preflight: zero failed checks
- git safety scan: no leak patterns detected
- `git diff --check`: no content or whitespace errors

All 29 PDF pages were rendered and inspected. No clipped table text, figure
overlap, text outside boxes, orphan section heading, command overflow, or
unreadable figure label was found. Pages affected by the final proper-name
typesetting change were rendered and inspected again.

## Remaining Human Release Actions

No commit, tag, or push was created. The final reviewed source should be
committed by the author, rebuilt from that immutable revision, and checked
once more before arXiv upload. The permanent Elliptic2 provenance limitation
must remain with the release unless upstream construction and row-level
mapping evidence later becomes available.

MiKTeX emits an environment-level legacy-Windows deprecation notice on this
machine. It does not affect the LaTeX build or the generated PDF.

READY_FOR_HUMAN_REVIEW
