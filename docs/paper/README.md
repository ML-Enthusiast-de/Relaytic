# Relaytic-AML Paper Artifacts

This directory contains the reader-facing Relaytic-AML paper draft and the reproducibility artifacts behind it. Start with the PDF or Markdown manuscript, then use this page only when you want to inspect or regenerate the evidence package.

## Start Here

- `relaytic_aml_arxiv_draft.pdf` is the review PDF.
- `relaytic_aml_arxiv_draft.md` is the canonical Markdown draft generated from the evidence pack.
- `arxiv_src/` is the source candidate used to build the PDF.
- `references.bib`, `figures/`, and `tables/` hold the paper bibliography and generated visual assets.

## Why The Build Pipeline Is Visible

Relaytic-AML is a systems paper about local, auditable evidence for anti-money-laundering evaluation. For that reason, the repository keeps the artifact-generation pipeline and JSON reports visible. They are not meant to be the first reading path; they are the audit trail that lets a reviewer check how tables, figures, claim boundaries, and preflight status were produced.

For public citation, use the final Git tag, GitHub Release, or archival snapshot selected at arXiv submission time. The `main` branch may continue to evolve after submission.

## Reproduce The Paper Assets

The root README contains copy-paste-safe Windows and macOS/Linux command blocks. The short path is:

```bash
python -m pip install -e ".[full]"
python -m relaytic.ui.cli release-safety paper-release --format json
python -m relaytic.ui.cli release-safety paper-arxiv-source --format json
python -m relaytic.ui.cli release-safety paper-final-preflight --format json
```

Full benchmark regeneration requires local access to the source datasets. Raw PaySim, Elliptic, and Elliptic2 files are not committed to this repository.

## Audit Trail

The main reports live under `../reports/`. They are useful after reading the paper, especially:

- `paper_release_manifest.json` for release-pack status.
- `paper_public_claims_allowed.json` for allowed and blocked public wording.
- `paper_metric_cell_audit.json` for metric provenance.
- `paper_final_preflight_manifest.json` for final source/PDF readiness.

The build-control files in the repository root record development history. They are useful for maintainers, but they are not required to understand or evaluate the paper.
