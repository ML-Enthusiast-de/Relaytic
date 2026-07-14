# Relaytic-AML Paper

Start with [`relaytic_aml_arxiv_draft.pdf`](relaytic_aml_arxiv_draft.pdf). The generated Markdown manuscript is [`relaytic_aml_arxiv_draft.md`](relaytic_aml_arxiv_draft.md), and [`arxiv_src/`](arxiv_src/) contains the self-contained LaTeX candidate. The rest of this directory is the audit trail behind those reader-facing files.

Relaytic-AML is a systems and evaluation paper. Keeping the generator, bibliography, vector figures, and rowless evidence reports in the repository is therefore part of the reproducibility claim. Raw or licensed benchmark rows are not redistributed.

## Requirements

- Python 3.10 or 3.11; the release candidate is tested with Python 3.11.
- Install the full profile from the repository root with `py -3.11 -m pip install -e ".[full]"` on Windows or `python3 -m pip install -e ".[full]"` on macOS/Linux.
- A TeX installation providing `pdflatex` and `bibtex` to rebuild the PDF. MiKTeX and TeX Live are suitable.
- No benchmark data is needed to verify committed evidence, rerun deterministic fixtures, regenerate the manuscript, or rebuild the PDF.

## Reproduce And Verify

After installation, the public `relaytic` command is the same on Windows, macOS, and Linux. Run this verification sequence from the repository root. The platform-specific blocks in the root [`README.md`](../../README.md#relaytic-aml-paper-draft) add the LaTeX and PDF-copy steps.

```text
relaytic release-safety paper-invariants --format json
relaytic release-safety paper-external-score-proof --format json
relaytic release-safety paper-external-score-integration --format json
relaytic release-safety paper-tables --format json
relaytic release-safety paper-draft --format json
relaytic release-safety paper-release --format json
relaytic release-safety paper-narrative-polish --format json
relaytic release-safety paper-novelty-positioning --format json
relaytic release-safety paper-release-integrity --format json
relaytic release-safety paper-arxiv-source --format json
relaytic release-safety paper-final-preflight --format json
```

A successful source build reports:

- `release_candidate_ready_for_human_upload` in `../reports/paper_p24_release_manifest.json`;
- `ready_for_source_release_candidate` in `../reports/paper_arxiv_source_manifest.json`;
- `ready_for_author_review_not_tagged` in `../reports/paper_final_preflight_manifest.json`.

After the final changes are committed, pushed to the public remote, and `git status --short` is empty, build the upload artifacts from that exact revision:

```text
relaytic release-safety paper-release-integrity --final --format json
```

Final mode refuses a dirty worktree or a source commit absent from the public remote. It writes the PDF, arXiv source archive, source revision, and SHA-256 hashes under `dist/paper-release/<commit>/`. A release tag is optional. When supplied, it must exist locally and remotely and resolve to the same commit.

## Benchmark Data

Full model reruns require local source data:

- PaySim: `data/paper_benchmarks/paysim/PS_20174392719_1491204439457_log.csv`
- Elliptic: `data/paper_benchmarks/elliptic/`
- Elliptic2/RevTrack: external local directories supplied to the relevant CLI commands

The paper states which results are raw-data reruns, committed-artifact verification, deterministic fixture reruns, or external benchmark context. Dataset hashes, split contracts, seeds, and expected output artifacts are recorded in `../reports/`; detailed benchmark commands are in [`../paper_benchmark_runbook.md`](../paper_benchmark_runbook.md).

For citation, use the immutable source commit recorded in the final bundle or a separately verified release tag. The `main` branch may continue to evolve after submission. The root build-control files document development history but are not required to understand or evaluate the paper.
