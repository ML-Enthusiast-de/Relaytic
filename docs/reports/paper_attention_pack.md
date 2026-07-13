# Relaytic-AML Paper Attention Pack

Use this wording for public posts until a later benchmark gate unlocks stronger claims.

## One-Line Summary

Relaytic-AML is a local-first agentic evaluation environment for financial-crime machine learning where specialist roles, local artifacts, redacted context packs, evidence cells, and claim gates keep humans and external agents oriented without turning benchmark rows into unsupported claims.

## Short Abstract

The Relaytic-AML draft presents a local-first architecture for agent-assisted anti-money-laundering (AML) evaluation, not a detector superiority claim. The controlled workspace is the source of truth. Specialist roles inspect source posture, challenge modeling plans, execute bounded searches, explain current state, and govern public claims. Benchmarks exercise that architecture. The current draft includes supporting PaySim synthetic temporal-fraud test precision-recall area under the curve (PR-AUC) 0.6388 and supporting Elliptic temporal graph-feature test PR-AUC 0.6688, while blocking hard AML, headline, graph-neural, claimed-equivalence-to-RevClassify, and hard business-value claims.

## Public Post

The Relaytic-AML paper presents a claim-bounded local evaluation architecture. The workspace remains authoritative, humans and agents have explicit roles, handoff exports redacted context rather than private rows, and each reported metric is traceable before it becomes a public claim. The draft covers architecture, role boundaries, research and operational use, current anti-money-laundering context, figures, reproducible source, and explicit benchmark limitations.

The benchmark rows are supporting evidence for that architecture, not the identity of the system. PaySim and Elliptic are supporting evidence only, Elliptic2 is modern context only, and stronger claims stay blocked until the gates earn them. The public story is that Relaytic-AML is an auditable local evaluation environment where agents and humans can see what is proven, what is blocked, and what would need to happen next.

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
