# Paper P18 Governance-Invariant Pack

- Status: `ready_for_governance_invariant_evidence`
- Invariant status: `pass`
- Adjacent-systems status: `pass`
- Current invariant count: `7`
- Adjacent family count: `9`
- Evidence-completeness check passed: `True`
- Next slice: `Paper Track P19 - hosted detector workflow demonstration, if selected`

## Governance Invariants

| Invariant | Enforcement | Evidence | Boundary |
| --- | --- | --- | --- |
| Metric-cell provenance | metric-cell audit plus required-field gate | all_numeric_cells_have_required_provenance; metric_cell_provenance_available | The invariant checks artifact completeness. It does not establish detector optimality. |
| Claim-strength monotonicity | claim lint, allowed-claims report, publishability matrix, and overclaim failure case | claim_safe_public_wording_allowed; hard_headline_claims_blocked | The gate is a deterministic release check; it is not an external peer review. |
| Leakage and selection firewall | feature policy report, split contract, failure fixtures, and leakage ablation | forbidden_balance_columns_used; test_set_selection_violation; test_exposure_contract | The current firewall is benchmark-specific; future datasets need their own leakage taxonomy. |
| Rowless external-agent handoff | handoff evaluator plus redaction failure case | external_context_rowless_and_redacted; rowless_external_agent_handoff_recoverable | The check evaluates deterministic redaction on fixtures. It is not a broad privacy certification. |
| Interrupted-run recoverability | no-lost-user guide and partial-run recovery fixtures | partial_run_state_recovery; partial_run_recovery_without_artifact_literacy | The check is deterministic; it does not measure human time-to-recovery. |
| Benchmark role separation | publishability matrix and allowed-claims report | supporting_table_allowed; elliptic2_supporting_context_and_firewall_visible | Rows with external or proxy roles cannot be treated as unified leaderboard evidence. |
| Local-first release safety | release go/no-go, claim lint, and public-claim whitelist | wording_lint; go_for_p13_claim_safe_release_pack | Licensed benchmark files are not redistributed; reproduction depends on local access. |

## Adjacent Systems

| Family | Primary object | Relaytic-AML position |
| --- | --- | --- |
| Model cards and model reporting | trained model and intended-use report | adds command-level metric provenance, release gating, and stronger-claim blocking around AML experiments |
| Datasheets and dataset documentation | dataset creation, composition, collection, and recommended use | connects dataset posture to split contracts, leakage controls, benchmark rows, and admissible claims |
| ML reproducibility checklists | reporting checklist and reproducibility discipline | turns checklist-like obligations into executable artifact-generation and release gates |
| MLOps experiment tracking | runs, metrics, parameters, artifacts, lineage, and model versions | focuses on local AML evidence, privacy posture, rowless handoff, and public scientific claim admissibility |
| Agent benchmarks and research-agent evaluations | agent performance on research, coding, or skill-use tasks | uses agents inside a governed local evaluation lab and then tests whether their outputs stay artifact-attached |
| AML detector and benchmark papers | detector architecture, benchmark result, graph construction, or financial-crime dataset | provides the local evidence and claim-governance substrate that such detector studies can run through |
| AML LLM graph reasoning and triage systems | LLM reasoning, triage, serving, and evidence-rich prompts for AML workflows | keeps LLM or external-agent help downstream of rowless local evidence, artifact provenance, and claim gates |
| Agentic SAR and compliance narrative assistants | human-in-the-loop SAR or compliance narrative drafting | governs the local experimental evidence and admissible claims that such narrative workflows should cite |
| Agent governance and runtime trust layers | runtime policies, enforcement, logging, trust scoring, and path-dependent agent governance | specializes governance to local AML evidence cells, rowless handoff, benchmark context, and paper/public claim admissibility |
