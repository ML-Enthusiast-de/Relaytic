# Paper P14 Release Checklist

- Source package validation ready: `True`
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

## Human gates before upload or release

- [x] Author block and PDF metadata are present in `docs/paper/arxiv_src/main.tex`.
- [ ] Run `pdflatex`, `bibtex`, `pdflatex`, and `pdflatex` from `docs/paper/arxiv_src/`; inspect the generated PDF.
- [ ] Include generated bibliography output if the final arXiv upload uses BibTeX rather than an inline bibliography.
- [ ] Confirm the AI-assistance disclosure accurately describes any LLM drafting, editing, or code-review help.
- [ ] Rerun `relaytic release-safety paper-arxiv-source --format json` after any manual source edits.
- [ ] Rerun `relaytic scan-git-safety` from the final cited revision.
- [ ] Confirm `git status --short` is empty and the cited commit exists on the public remote.

## Claim boundary

The source package remains bounded to the evaluation-environment contribution. It must not claim hard AML superiority, SOTA or leaderboard-winning performance, claimed equivalence to RevClassify, graph-neural superiority, production readiness, or hard business value.
