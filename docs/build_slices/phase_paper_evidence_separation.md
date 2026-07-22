# Paper Track P26 - Evidence/gate separation and validation-subsplit disclosure

Status: implemented

## Goal

P26 corrects the final paper-release contract without changing benchmark values. It makes factual evidence cells structurally independent from interpretive claim gates, documents the nested validation subsets used for calibration and threshold selection, removes an unsupported public tag claim, and repairs the PaySim finalist tie wording at the precision shown in the paper.

## Required behavior

1. Evidence cells contain measurement provenance only. Interpretive fields such as `claim_state`, `admissible_use`, `publication_role`, `stronger_claim_status`, and `missing_evidence` are rejected.
2. Every reader-facing metric cell is referenced by a separate claim-gate record. Gate references to absent cells fail validation.
3. The hosted external-score fixture emits a factual invariant cell and a separate hosted-output gate.
4. PaySim and Elliptic validation partitions disclose the full selection surface and the nested calibration and threshold-selection subsets, including boundaries, counts, positives, and overlap policy.
5. The paper describes XGBoost and Random Forest as joint PaySim runners-up at four-decimal display precision while preserving the unrounded recorded values.
6. Public release text may name a tag only after local and remote verification. Otherwise it identifies an immutable public commit and does not emit a tag archive URL.

## Evidence boundary

P26 does not rerun detector selection, alter benchmark measurements, claim an untouched PaySim holdout, establish RevClassifyDS parity, or add a detector-superiority result.

## Minimum proof

- deterministic schema tests reject merged evidence/interpretation records
- validation-subsplit counts reconcile to the full validation partitions and operating-point denominators
- reader-facing tables and snippets consume separate gate records
- final PDF and source bundle identify one public immutable revision and pass visual, font, citation, and release preflight

## Implemented outputs

- metric schema: `relaytic.paper_metric_evidence_cell.v1`
- invariant schema: `relaytic.paper_invariant_evidence_cell.v1`
- interpretive schema: `relaytic.paper_claim_gate.v2`
- table-gate artifact: `docs/reports/paper_claim_gate_records.json`
- separation audit: `docs/reports/paper_p26_evidence_gate_separation_audit.json`
- validation-subsplit audit: `docs/reports/paper_p26_validation_subsplit_audit.json`
- release-reference audit: `docs/reports/paper_p26_release_reference_audit.json`
- deterministic regression coverage: `tests/test_paper_track_p26.py`
