# Paper P13 arXiv Submission Checklist

P13 permits only a claim-safe evaluation-environment release.

## Gate Checks

- [ ] `docs/reports/paper_metric_cell_audit.json` status is `pass`.
- [ ] `docs/reports/paper_claim_lint_report.json` status is `pass`.
- [ ] `docs/reports/paper_external_dry_run_report.json` status is `pass_paper_smoke_reproduced_claim_linted`.
- [ ] `docs/reports/paper_reproduction_failure_report.json` status is `no_failures`.
- [ ] `docs/reports/paper_public_claims_allowed.json` status is `claim_safe_public_wording_allowed`.
- [ ] `relaytic scan-git-safety` reports no findings after staging P13 files.

## Paper Package

- [ ] Regenerate `docs/paper/arxiv_src/` with `relaytic release-safety paper-arxiv-source --format json` after any final paper edit.
- [ ] Include `docs/paper/references.bib` and verify every in-text citation has a matching BibTeX key.
- [ ] Verify the converted PDF figures in `docs/paper/arxiv_src/figures/` are accepted by the selected arXiv processor.
- [ ] Keep the table values synchronized with `docs/paper/tables/table_manifest.json` and `docs/reports/paper_metric_cell_audit.json`.
- [ ] Fill in author name, affiliation, contact, and optional acknowledgements before upload.
- [ ] Confirm the AI-assistance disclosure is accurate before upload.

## Public Claim Discipline

- [ ] Public posts use `docs/reports/paper_attention_pack.md` wording only.
- [ ] Do not add hard anti-money-laundering, headline, SOTA, claimed-equivalence-to-RevClassify, graph-neural superiority, or hard business-value claims.
- [ ] Confirm public wording status is `claim_safe_public_wording_allowed`.

## Suggested arXiv Metadata

- Title: `Relaytic-AML: Claim-Gated Evaluation Environments for Temporal Graph Financial-Crime Machine Learning`
- Primary category: `cs.LG`
- Secondary categories: `q-fin.GN`, `cs.SI`, `cs.CY`
- Keywords: anti-money laundering, financial crime, graph machine learning, reproducibility, evaluation environments, claim gating

## Tag And Release

- [ ] Confirm `git status --short` is empty at the final tag target.
- [ ] Confirm the final tag target contains the release-pack artifacts generated from base commit `225a300f1c57f89c2f5a8f55ae4657ffcbbbab78`; rerun the manifest after final edits if the source evidence changes.
- [ ] Create tag after the final PDF/source matches the manifest: `git tag -a relaytic-aml-paper-p13-claim-safe -m "Relaytic-AML claim-safe paper release"`.
- [ ] Attach or link the paper PDF, release manifest, public claims JSON, and benchmark artifacts.

## Fallback

If any gate fails, do not submit. Keep `paper_release_manifest.json` as a release-blocker report and repair the failed gate first.
