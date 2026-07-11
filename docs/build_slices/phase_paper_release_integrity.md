# Paper Track P24 - Release integrity, protocol disclosure, and revision-locked arXiv candidate

Status: implemented; exact-revision final build awaits the reviewed clean commit

Trigger: `implement P24`

P24 is the final engineering slice before the human arXiv upload decision. It repairs factual, methodological, bibliographic, visual, and release-provenance defects that remain after P23. It must not change benchmark values silently, expand detector claims, or call the paper release-ready merely because LaTeX compiles.

## Why This Slice Exists

The current paper is a credible systems/evaluation draft, but the checked-in candidate is not yet a defensible release artifact. A repository inspection on 2026-07-10 found concrete blockers:

- the adjacent-systems table contains the literal truncation `paper/public claim a...`
- the generated paper records source commit `7874eef05de1`, while the inspected clean checkout was at `3687403a6ee22e7b0fedfa34af1b33c9ab2cda74`; that observed hash is diagnostic only and must not be hard-coded as the repair
- the paper date is June 2026 while bibliography access dates extend into July 2026
- reader-facing text still contains ASCII `+/-`, generic `rows/nodes`, `official-partition`, broad `System Evaluation`, and statistically stronger wording than single-seed evidence supports
- the PaySim balance quartet is incorrectly described in places as entirely post-event even though it contains pre-transaction and post-transaction balances
- the main protocol description omits exact split ranges, counts, history boundaries, unknown-label handling, and realized review-queue fractions that already exist in repository artifacts or code
- the selected Elliptic row records validation PR-AUC `0.976654` and later-window test PR-AUC `0.668756`, but the manuscript does not discuss that gap
- the review-budget implementation selects a validation threshold at the requested rank and applies `score >= threshold` to test, so ties are included and realized fractions can differ from the requested `0.005`
- the current selected PaySim queue is `1109/123580` (`0.008974`) and the selected Elliptic queue is `36/11184` (`0.003219`), despite the same nominal requested fraction
- Elliptic2 artifacts distinguish the audited current core (`121810` subgraphs) from the pinned RevTrack-evaluable cohort (`110902` rows), disclose prior official-test exposure, and report the content-hash robustness result; the manuscript currently compresses those distinctions too aggressively
- the named Governance-as-a-Service and Runtime Governance bibliography entries contain author metadata that conflicts with the cited official records named in the release brief
- no committed prediction-level PaySim or Elliptic score artifact is available for a methodologically auditable bootstrap, so confidence intervals require an explicit feasibility gate rather than being invented from aggregate metrics
- Figure 4 visually places heterogeneous dataset/task metrics on shared scales and can be read as a cross-dataset leaderboard

These findings are entry conditions for P24, not manuscript claims. P24 must re-read the authoritative artifacts at implementation time because the repository may change before the trigger is used.

## Goal

Produce one calm, professional Relaytic-AML arXiv candidate for which:

- factual descriptions match authoritative artifacts and primary sources
- the experimental protocol is understandable without opening JSON files
- every headline number is checked against a machine-readable evidence source
- single-seed and prior-exposure limits are visible
- citations support the exact nearby claims
- tables and figures cannot be mistaken for internal logs or a cross-dataset leaderboard
- the PDF and source bundle are built from and identify one exact clean Git revision
- final release checks fail closed on stale revisions, semantic truncation, metric drift, split drift, unsupported claims, and broken source metadata

## Claim Boundary

P24 preserves the P23 category claim: Relaytic-AML is a local-first agentic evaluation-lab, governance, and reproducibility architecture around financial-crime detectors and agent-assisted workflows. It is not a new detector, a graph-neural architecture contribution, a production AML validation, a privacy certification, a regulatory compliance product, or a RevClassifyDS-parity result.

No existing benchmark value may be changed unless the new value is read from an authoritative evidence artifact, the source artifact and field are recorded, all manuscript surfaces are regenerated, and the manuscript-to-artifact consistency audit passes. Formatting changes and newly disclosed existing values, such as the Elliptic validation score, are not new benchmark runs.

## Execution Order

P24 is one release-integrity slice with six ordered gates. Implementation must stop at the first failed evidence gate and report the missing or contradictory source instead of guessing.

### Gate 0 - Evidence authority and baseline freeze

Before editing prose, build a source-of-truth map for every paper-facing dataset fact, split field, feature policy, metric, queue count, evidence role, citation, and release identifier.

Required work:

- inventory the generated Markdown, LaTeX, figures, bibliography, paper tables, release scripts, preflight scripts, and all PaySim/Elliptic/Elliptic2 evidence inputs
- assign one authoritative artifact and exact field to every displayed metric and protocol value
- record supersession where older artifacts conflict with newer ones, especially the original P8 Elliptic2 access report versus P8-A through P8-D context evidence
- record the current Git revision and cleanliness as an observed build input, never as a source constant
- create a before-change manuscript-to-artifact comparison so P24 cannot silently alter numbers

Required outputs:

- `docs/reports/paper_p24_evidence_authority.json`
- `docs/reports/paper_p24_baseline_metric_snapshot.json`
- `docs/reports/paper_p24_artifact_conflict_audit.json`

Stop condition:

- if two live artifacts disagree and no explicit supersession rule identifies the authority, block the affected paper row and surface the conflict

### Gate 1 - Factual and experimental-protocol correction

Repair the generated manuscript source and the generators that own it. Do not patch only the rendered PDF or generated LaTeX.

Required work:

- remove Table 1 truncation and keep its caption with the table without microscopic text
- describe PaySim as `6,362,620 transactions`, not `rows/nodes`
- describe Elliptic as transaction-graph nodes only where node terminology is correct
- distinguish the four PaySim balance fields as a mixed pre/post transaction quartet excluded conservatively for decision-time and simulator-consistency risk
- state exact PaySim train/validation/test step ranges, row counts, positive counts, boundary policy, history state behavior, and shifted destination-history construction from code and artifacts
- state exact Elliptic time ranges, known-label counts, illicit counts, unknown-label handling, graph-construction scope, and whether structural statistics are same-snapshot, cumulative, or another verified policy
- state the exact Elliptic2 partition source, RevTrack-evaluable cohort size, audited full-core size, train/validation/test sizes, prior test exposure, and content-hash robustness role
- disclose the Elliptic validation-to-test PR-AUC gap and limit causal interpretation to plausible temporal shift, validation-specific selection, or both unless a dedicated analysis exists
- define the review operating point as a validation-selected score threshold, explain `>=` tie inclusion, report requested and realized fractions and counts, and remove wording that implies identical fixed queue fractions
- explain Platt calibration as validation-only probability calibration that can affect threshold operating points but ordinarily does not improve rank-invariant PR-AUC unless score ordering changes
- rename `System Evaluation` to `Deterministic Artifact and Release-Gate Evaluation` or an equally precise bounded title
- update the paper date to the actual release month/date and make it consistent with access dates and PDF metadata

Required output:

- `docs/reports/paper_p24_protocol_disclosure_audit.json`

Stop condition:

- if history reset/cross-boundary behavior, Elliptic structural scope, or Elliptic2 partition provenance cannot be established from code plus artifacts, state the missing evidence in limitations and do not assert a policy

### Gate 2 - Bibliography, citation, statistical, and wording audit

Every citation and empirical qualifier must be checked against the claim it supports.

Required work:

- verify every bibliography entry, with special attention to 2025-2026 preprints, against an official arXiv record, DOI record, or publisher page
- correct Governance-as-a-Service, Runtime Governance for AI Agents, and Rethinking LLMOps for Fraud and AML author metadata, author order, title, year, identifiers, venue state, and URL from primary records
- add the canonical Saito-Rehmsmeier precision-recall citation, Kleppmann et al. local-first citation, and primary Extra Trees, XGBoost, LightGBM, and Platt-scaling citations at first substantive use
- replace the generic FinCEN landing-page support for any specific typology with a directly supporting advisory, or narrow the prose to the landing page's actual scope
- classify recent arXiv work as preprints unless formal publication is verified
- remove unused bibliography entries and fail on missing citation keys
- create a sentence-level claim-to-source audit for factual statements and paraphrases; direct quotations are not required and should remain rare
- replace unsupported `meaningful`, `significant`, `stable`, `robust`, `generalizes`, `superiority`, and equivalent language with numerical, contract-specific descriptions
- add a bootstrap confidence interval only if prediction-level test labels and scores can be regenerated or recovered into a hashed, rowless evidence artifact with a frozen bootstrap unit, sample count, confidence level, seed, and no-positive handling policy
- otherwise state explicitly that PaySim and Elliptic are single-seed point estimates; aggregate metrics must never be reverse-engineered into confidence intervals

Required outputs:

- `docs/reports/paper_p24_bibliography_verification.json`
- `docs/reports/paper_p24_claim_citation_map.json`
- `docs/reports/paper_p24_statistical_reporting_decision.json`

Stop condition:

- remove or narrow any factual statement whose nearby source cannot be verified to support it

### Gate 3 - Reproducibility, tables, figures, and layout

Required work:

- classify each reproduction command as raw-data benchmark rerun, artifact regeneration, artifact verification, deterministic fixture rerun, paper build, or source-bundle validation
- explain `--run-optional` precisely and never call artifact reuse or validation a benchmark rerun
- keep the paper's command path short and copy-paste safe on Windows PowerShell and macOS/Linux; retain detailed command matrices in the repository rather than a visually weak paper page
- use clickable repository links and proper LaTeX `\pm` notation throughout reader-facing surfaces
- shorten dense table cells while retaining exact evidence roles; use booktabs-style tables and prevent caption or heading orphans
- redesign Figure 4 as distinct task-contract panels: PaySim and Elliptic local evidence rows, a separate Elliptic2-versus-published-reference context panel, and a separate review-queue panel
- place `Values across datasets and task contracts are not directly comparable.` prominently inside Figure 4
- separate ranking metrics, operating-point metrics, local evidence, and external reference context visually and in the caption
- preserve vector output, embedded fonts, grayscale readability, and normal-zoom legibility
- inspect appendix tables for clipping and density without redesigning readable material unnecessarily
- improve page flow around reproducibility and conclusion without shrinking text or stranding headings

Required outputs:

- refreshed generated Markdown, LaTeX, bibliography, vector figures, source bundle, and canonical review PDF
- `docs/reports/paper_p24_visual_layout_audit.json`
- `docs/reports/paper_p24_reproduction_semantics.json`

Stop condition:

- any table truncation, caption orphan, clipped figure label, cross-dataset leaderboard reading, broken URL, or unreadable normal-zoom text blocks release

### Gate 4 - Semantic and manuscript-to-artifact release checks

Extend the release harness so the defects found in this review cannot recur silently.

Required checks:

- suspicious literal `...` endings inside generated table cells, without globally banning legitimate prose ellipses
- TODO, FIXME, placeholder, unresolved, pending-evidence, dummy, temp, `??`, malformed URL, empty caption, unresolved citation, and ASCII `+/-` markers on reader-facing surfaces
- stale or hard-coded source commit identifiers
- inconsistent paper, access, and PDF metadata dates
- prohibited universal or detector-superiority phrases
- exact metric agreement, with display-rounding tolerances, across abstract, results prose, tables, figures, appendix, and evidence cells
- PaySim PR-AUC, ROC-AUC, precision, recall, requested queue fraction, realized queue fraction, and reviewed count
- Elliptic validation PR-AUC, test PR-AUC, precision, recall, requested queue fraction, realized queue fraction, and reviewed count
- Elliptic2 official-partition mean and standard deviation, content-hash robustness value, cohort sizes, prior-exposure disclosure, and RevClassifyDS external reference
- exact split range/count/positive-count agreement and unknown-label/feature-policy agreement with machine-readable contracts
- validation-only selection, calibration, and threshold policy agreement with implementation
- source/PDF revision agreement, clean-build precondition, file hashes, embedded fonts, no Type 3 fonts, and clean LaTeX references/boxes

Required outputs:

- `docs/reports/paper_p24_metric_consistency_audit.json`
- `docs/reports/paper_p24_split_consistency_audit.json`
- `docs/reports/paper_p24_semantic_source_audit.json`
- `docs/reports/paper_p24_release_manifest.json`

### Gate 5 - Exact-revision release finalization

Avoid the self-referential commit problem: a committed PDF cannot contain the hash of the commit that includes that PDF without changing the hash again.

The required mechanism is an out-of-tree release build from a clean source revision:

1. Commit all source, generator, evidence, bibliography, and test changes.
2. Confirm `git status --short` is empty.
3. Resolve `git rev-parse HEAD` once and record the full SHA.
4. Build the final PDF, arXiv source bundle, and preflight reports into an ignored or temporary release directory keyed by that SHA.
5. Inject that SHA into the manuscript during the release build; do not edit a checked-in hash manually.
6. Verify every release artifact manifest names the same SHA and records SHA-256 hashes for the PDF, source bundle, bibliography, and figures.
7. If a dedicated tag is used, create or select it explicitly on that source revision and rebuild from the tag. Never claim a tag or archive that does not exist.
8. Attach or upload the out-of-tree artifacts associated with that exact revision. The checked-in review PDF may be refreshed for convenience, but it is not the authority for exact-revision attestation.

The release command must refuse to run in final mode on a dirty worktree. A non-final review build may remain available, but it must say `review build` and must not report `arxiv_upload_ready=true`.

Required outputs:

- `dist/paper-release/<full-or-short-sha>/relaytic_aml_arxiv.pdf`
- `dist/paper-release/<full-or-short-sha>/relaytic_aml_arxiv_source.tar.gz`
- `dist/paper-release/<full-or-short-sha>/release_revision_manifest.json`
- `dist/paper-release/<full-or-short-sha>/final_preflight.json`

The `dist/paper-release/` path must remain outside tracked source or be ignored. The final response must report the exact commit, whether the source tree was clean before the build, and hashes of the released artifacts.

### Gate 6 - Full validation and human review handoff

Run all paper-specific release commands, focused and broad tests proportional to the changed code, fresh LaTeX compilation, bibliography compilation, font inspection, hyperlink checks, leak scans, and page rendering.

Visually inspect every PDF page, with special attention to current pages 5-7, 11-13, 16-17, and the command appendix. Page numbers may shift after reflow, so inspection must also identify pages by table, figure, and section content.

The final machine state may become `release_candidate_ready_for_human_upload` only when all automated gates pass. The actual arXiv upload and public tag/release publication remain human-owned external actions.

## Expected Implementation Surface

P24 is expected to modify the owning source rather than generated output alone, including:

- `src/relaytic/release_safety/paper_release.py`
- `src/relaytic/release_safety/paper_draft.py`
- `src/relaytic/release_safety/paper_arxiv_source.py`
- `src/relaytic/release_safety/paper_final_preflight.py`
- benchmark/split helpers only where needed to expose already implemented policy accurately
- `docs/paper/references.bib`
- generated paper Markdown, LaTeX, vector figures, reports, and canonical review PDF
- paper-track tests and CI/static paper checks
- README reproduction guidance only where the paper points readers to it

P24 must not broaden package architecture, add a detector family, rerun model selection on test, create a release tag automatically, upload to arXiv, or clean unrelated repository history.

## Acceptance Criteria

P24 is complete only when all of the following are true:

1. Table 1 has no truncation and its caption remains attached to the table at normal font size.
2. PaySim balance, transaction-count, split, history-feature, and leakage wording matches code and authoritative artifacts.
3. Elliptic split, unknown-label, graph-scope, validation score, test score, and validation-test-gap wording is exact and bounded.
4. Elliptic2 partition/cohort terminology, prior exposure, robustness role, and `121810` versus `110902` distinction are explicit and source-backed.
5. Review-budget selection, threshold transfer, tie inclusion, queue counts, and realized fractions match implementation and evidence.
6. PaySim and Elliptic are identified as single-seed point estimates unless valid prediction-level bootstrap evidence is added.
7. Platt calibration wording does not attribute PR-AUC improvement to calibration without ranking-change evidence.
8. Deterministic fixture evaluation is not described as human usability, privacy certification, production validation, or universal prevention.
9. Reproduction commands accurately distinguish rerun, regeneration, validation, fixture, build, and optional-skip behavior.
10. All bibliography entries and nearby factual claims pass primary-source verification; the named incorrect author entries are corrected and canonical metric/local-first/model-method citations are present.
11. Figure 4 cannot reasonably be read as a cross-dataset leaderboard and contains the non-comparability sentence inside the figure.
12. Reader-facing `+/-`, `rows/nodes`, stale commit, wrong date, suspicious table ellipses, and unresolved markers are absent.
13. Every headline metric and split value matches one authoritative artifact within declared display-rounding tolerance.
14. No benchmark number changes silently; any changed displayed number has an artifact/field trace and appears in the final comparison report.
15. The PDF and arXiv source bundle are generated from one exact clean revision by the out-of-tree release path, and all release manifests agree on that SHA.
16. LaTeX and bibliography builds are clean; citations and references resolve; fonts are embedded; no Type 3 fonts, visible overfull boxes, clipping, orphaned headings/captions, or broken hyperlinks remain.
17. Git-safety and source-package scans find no private paths, secrets, raw licensed rows, or local-only data.
18. The conclusion and research questions map only to reported deterministic checks, evidence cells, benchmark roles, and stated limitations.
19. The final P24 manifest lists modified files, factual and citation corrections, methods clarifications, claim-boundary changes, layout changes, automated checks, commands, test results, unresolved facts, release artifact paths, exact source commit, and clean-build state.
20. `arxiv_upload_ready` stays false until an exact clean revision build passes and any intended public tag or archival snapshot actually exists.

## Fallback Rules

- Missing split or feature evidence: narrow the manuscript and record the gap; do not infer a policy.
- Missing prediction-level scores: report single-seed point estimates; do not fabricate uncertainty.
- Unverified citation: remove or narrow the claim; do not retain convenient metadata.
- Unavailable licensed data during clean-build validation: validate existing artifacts and label that path accurately; do not call it a benchmark rerun.
- Dirty release tree: block final mode and explain the files preventing attestation.
- Visual failure: repair the generator and regenerate; never edit the PDF by hand.
- Metric mismatch: block release even if the PDF compiles.

## Trigger Contract

`implement P24` authorizes the full ordered slice above. Implementation should provide progress at each gate and stop if an evidence authority conflict cannot be resolved. It does not authorize creating or pushing a Git tag, publishing a GitHub release, or uploading to arXiv; those remain explicit user actions after the release candidate is verified.
