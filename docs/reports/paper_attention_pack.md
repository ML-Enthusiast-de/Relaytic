# Relaytic-AML P13 Attention Pack

Use only this wording for public posts until a later benchmark gate unlocks stronger claims.

## One-Line Summary

Relaytic-AML is a local-first, claim-gated evaluation environment for financial-crime ML that turns benchmark evidence into auditable tables, figures, limitations, and public-claim gates.

## Short Abstract

The P13 Relaytic-AML draft presents a claim-gated evaluation environment, not a detector superiority claim. The current pack reports supporting PaySim synthetic temporal-fraud test PR-AUC 0.638773 and supporting Elliptic temporal graph-feature test PR-AUC 0.668756, while blocking hard AML, headline, graph-neural, RevClassify parity, and hard business-value claims.

## Public Post

I finished the claim-safe Relaytic-AML paper package. The interesting part is not just the model scores; it is the release discipline around them. Every table cell is tied to a dataset, split, command, artifact field, budget tier, leakage posture, and claim state. The draft includes deterministic tables and figures, a clean-clone dry run, a public-claims whitelist, and explicit limitations for PaySim, Elliptic, Elliptic2, and AMLSim-style tracks.

The current release is intentionally careful: PaySim and Elliptic are supporting evidence only, Elliptic2 is modern context only, and stronger claims stay blocked until the benchmark gates earn them. That is the point. Relaytic-AML is being built as an auditable local evaluation environment where agents and humans can see what is proven, what is blocked, and what would need to happen next.

## What This Does Not Claim

- No hard real-world AML superiority claim.
- No SOTA or leaderboard-winner claim.
- No RevClassify parity or Elliptic2 performance-contribution claim.
- No graph-neural superiority claim.
- No hard business-value or analyst-hour savings claim.

## Reviewer Commands

```powershell
relaytic release-safety paper-tables --format json
relaytic release-safety paper-draft --format json
relaytic release-safety paper-dry-run --run-isolated-install --format json
relaytic release-safety paper-release --format json
relaytic scan-git-safety
```

## Release Facts

- Planned tag: `relaytic-aml-paper-p13-claim-safe`
- P12 dry-run status: `pass_paper_smoke_reproduced_claim_linted`
- Paper draft: `docs/paper/relaytic_aml_arxiv_draft.md`
- Public claims whitelist: `docs/reports/paper_public_claims_allowed.json`
- Release manifest: `docs/reports/paper_release_manifest.json`
