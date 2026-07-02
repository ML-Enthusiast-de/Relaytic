# Paper P19-B Hosted-Score Reproducibility Card

This card regenerates the hosted external-score governance proof and the paper-facing case-study artifacts. It uses the repo-local rowless fixture by default and does not require PaySim, Elliptic, or Elliptic2 data.

Windows PowerShell:

```powershell
py -3.11 -m relaytic.ui.cli release-safety paper-external-score-proof --format json
py -3.11 -m relaytic.ui.cli release-safety paper-external-score-integration --format json
py -3.11 -m relaytic.ui.cli release-safety paper-release --format json
```

macOS/Linux:

```bash
python3 -m relaytic.ui.cli release-safety paper-external-score-proof --format json
python3 -m relaytic.ui.cli release-safety paper-external-score-integration --format json
python3 -m relaytic.ui.cli release-safety paper-release --format json
```

Expected outputs:

- `docs/reports/paper_external_score_case_study.json`
- `docs/reports/paper_external_score_paper_panel.json`
- `docs/reports/paper_external_score_claim_map.json`
- `docs/reports/paper_external_score_repro_card.md`
- `docs/reports/paper_external_score_integration_manifest.json`

Data and privacy boundary:

- The default fixture is rowless and contains no raw transactions, identifiers, secrets, licensed data, or private machine paths.
- Optional local score artifacts remain local. Relaytic records only schema fields, hash prefixes, metric policy, leakage posture, claim state, and redaction evidence.

Evidence identifiers:

- Evidence cell: `p19a.external_score.hosted_metadata_completeness`
- Dataset: `p19a_hosted_score_fixture`
- Split: `fixture_holdout`
- Schema hash prefix: `4b2b70a58b0c`
- Content hash prefix: `dac68c3801f5`
