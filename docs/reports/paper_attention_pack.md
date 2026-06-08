# Relaytic-AML Paper Attention Pack

Use this wording for public posts until a later benchmark gate unlocks stronger claims.

## One-Line Summary

Relaytic-AML is a local-first agentic evaluation environment for financial-crime ML where specialist roles, local artifacts, redacted context packs, evidence cells, and claim gates keep humans and external agents oriented without turning benchmark rows into unsupported claims.

## Short Abstract

The Relaytic-AML draft presents a local-first architecture for agent-assisted AML evaluation, not a detector superiority claim. The controlled workspace is the source of truth. Specialist roles inspect source posture, challenge modeling plans, execute bounded searches, explain current state, and govern public claims. Benchmarks exercise that architecture. The current draft includes supporting PaySim synthetic temporal-fraud test PR-AUC 0.638773 and supporting Elliptic temporal graph-feature test PR-AUC 0.668756, while blocking hard AML, headline, graph-neural, claimed-equivalence-to-RevClassify, and hard business-value claims.

## Public Post

I finished a first claim-safe Relaytic-AML paper draft. The core idea is local-first agentic evaluation: keep the workspace as the authority, give humans and agents clear roles, export redacted context instead of private rows, and make every metric traceable before anybody turns it into a claim. The draft foregrounds the Relaytic architecture, role boundaries, intended company and research uses, current frontier AML context, figures, an arXiv source candidate, and explicit limitations for PaySim, Elliptic, Elliptic2, and AMLSim-style tracks.

The benchmark rows are supporting evidence for that architecture, not the identity of the system. PaySim and Elliptic are supporting evidence only, Elliptic2 is modern context only, and stronger claims stay blocked until the gates earn them. That is the point: Relaytic-AML is being built as an auditable local evaluation environment where agents and humans can see what is proven, what is blocked, and what would need to happen next.

## What This Does Not Claim

- No hard real-world AML superiority claim.
- No SOTA or leaderboard-winner claim.
- No claimed equivalence to RevClassify and no Elliptic2 performance-contribution claim.
- No graph-neural superiority claim.
- No hard business-value or analyst-hour savings claim.

## Reviewer Commands

```powershell
relaytic release-safety paper-tables --format json
relaytic release-safety paper-draft --format json
relaytic release-safety paper-release --format json
relaytic release-safety paper-arxiv-source --format json
relaytic scan-git-safety
```

## Release Facts

- Paper draft: `docs/paper/relaytic_aml_arxiv_draft.md`
- arXiv source tree: `docs/paper/arxiv_src/`
- Public claims whitelist: `docs/reports/paper_public_claims_allowed.json`
