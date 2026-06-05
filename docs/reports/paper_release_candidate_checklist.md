# Paper P14 Release-Candidate Checklist

- Source release-candidate ready: `True`
- arXiv upload ready now: `False`
- Source tree: `docs/paper/arxiv_src`
- Package audit: `pass`

## Automated gates

- [x] P13 claim-safe release manifest is ready.
- [x] P13 public wording lint passes and hard/headline claims remain blocked.
- [x] Markdown paper source is converted to top-level LaTeX source.
- [x] SVG figures are converted to PDF figures for the pdfLaTeX arXiv processor.
- [x] Generated LaTeX citations resolve against `references.bib`.
- [x] Source-package audit blocks local paths, secrets, legacy prototype wording, and unguarded hard claims.

## Human gates before upload or tag

- [ ] Replace placeholder author, affiliation, and contact metadata in `docs/paper/arxiv_src/main.tex`.
- [ ] Run `pdflatex`, `bibtex`, `pdflatex`, and `pdflatex` from `docs/paper/arxiv_src/`; inspect the generated PDF.
- [ ] Include generated bibliography output if the final arXiv upload uses BibTeX rather than an inline bibliography.
- [ ] Rerun `relaytic release-safety paper-arxiv-source --format json` after metadata edits.
- [ ] Rerun `relaytic scan-git-safety` from the tag target.
- [ ] Confirm `git status --short` is empty before creating `relaytic-aml-paper-p14-source-rc`.

## Claim boundary

The source package remains an evaluation-environment release candidate. It still must not claim hard AML superiority, SOTA or leaderboard-winning performance, RevClassify parity, graph-neural superiority, production readiness, or hard business value.
