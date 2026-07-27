# Paper P23 Novelty And Adjacent-Systems Distinction

- Status: `blocked_pending_p23_repairs`
- Distinction matrix: `pass`
- Manuscript audit: `fail`
- Covered categories: `9`
- Next slice: `Paper Track P23 repair`

## Distinction Matrix

| Adjacent system | What it optimizes | Relaytic-AML role |
| --- | --- | --- |
| AML detector and benchmark papers | higher-performing detector architectures, graph features, datasets, and benchmark rows | wrap detector runs and outputs with local provenance, leakage posture, budget context, review-budget interpretation, and claim gates |
| AML LLM graph reasoning and triage systems | LLM reasoning over AML graph context, risk-factor extraction, serving throughput, and quality gates | keep LLM and external-agent assistance downstream of rowless local evidence cells and admissible-claim checks |
| Agentic SAR and compliance narrative assistants | human-in-the-loop SAR narrative generation, compliance validation, and investigator-facing writing support | make the experimental evidence and claim boundary that downstream narratives should cite auditable before writing begins |
| Agent governance and runtime trust layers | general runtime policy enforcement, trust scoring, path-dependent controls, and agent action logs | specialize governance to AML evidence cells, rowless handoff, benchmark-context routing, and public paper/release wording |
| MLOps experiment tracking | run history, artifacts, metrics, parameters, model versions, and lifecycle memory | add local AML-specific interpretation gates that decide which tracked results may become public scientific claims |
| Model cards and model reporting | model documentation, intended use, evaluation summaries, and caveats | materialize factual provenance and separate interpretation records that a defensible model report can cite |
| Datasheets and dataset documentation | dataset composition, collection process, stewardship, and recommended use | connect dataset posture to split contracts, leakage controls, benchmark rows, and admissible interpretations |
| ML reproducibility checklists | static reporting requirements that make ML results easier to reproduce | turn checklist obligations into executable local artifact generation, failure cases, and release preflight gates |
| Agent benchmarks and research-agent evaluations | measuring whether agents can complete research, coding, or tool-use tasks | use role-scoped agents inside an AML evaluation lab and test whether their outputs stay attached to evidence |

## Failed Checks

- `required_p23_inputs_present`: P23 requires the current manuscript, references, P18 adjacent comparison, P20 reader guidance, public-claim gate, and hosted-score claim map.
- `novelty_audit_passed`: P23 manuscript novelty and claim-boundary audit must pass.
