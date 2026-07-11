# Relaytic-AML: A Local-First Agentic Evaluation Lab for Financial-Crime Machine Learning

## Abstract

Anti-money laundering (AML) machine-learning experiments are difficult to audit when data residency, temporal validity, graph provenance, agent assistance, review capacity, and public reporting are handled separately. Relaytic-AML is a local-first evaluation lab in which role-scoped agents work through deterministic harnesses to produce provenance-bearing result records and evidence-bounded claims. We exercise the architecture with temporal PaySim and Elliptic workflows, deterministic governance tests, and an Elliptic2 reference workflow. The selected PaySim and Elliptic test PR-AUC point estimates are 0.6388 and 0.6688; the separate Elliptic2 context estimate is 0.9432 $\pm$ 0.0009, alongside a published RevClassifyDS reference of 0.9740. These values arise from different datasets and task contracts and are not compared as a leaderboard. The contribution is an evaluation, governance, and reproducibility architecture, not a new detector or a detector-superiority result.

## 1. Introduction

AML modeling is a rare-event, high-stakes evaluation problem. The input may be a stream of mobile-money transfers, card events, account activity, wire messages, customer profiles, or blockchain transactions. Suspicion often appears as a temporal or network pattern: rapid movement of newly received funds, repeated transfers through related accounts, structured amounts, new counterparties receiving many payments, activity inconsistent with a customer profile, or cryptocurrency flows involving higher-risk services and jurisdictions. FATF and FFIEC material describes such pattern-oriented red flags in operational terms [@fatf2020virtualassets; @ffiecRedFlags].

Because AML suspicion is often pattern-based, an isolated model metric is easy to misread. A precision-recall area under the curve (PR-AUC) estimate or a precision-at-review-budget estimate becomes interpretable only when the evaluation record shows which data stayed local, which fields were available at decision time, how temporal or graph boundaries were split, whether model selection touched the test partition, and which review capacity was assumed. Precision-recall analysis is particularly informative for highly imbalanced tasks because it focuses on performance for the rare positive class [@saito2015precisionrecall]. Agent assistance raises the provenance burden: fluent explanations from large language models (LLMs) or coding agents can drift from the artifact record unless release decisions are tied to machine-checkable evidence.

Relaytic began as a general local-first inference-engineering lab. Relaytic-AML is the financial-crime edition used here to test whether that architecture can support governed AML experimentation. It is a set of cooperating agents and deterministic harnesses around a local artifact store. The guide helps a user or another agent understand where the run is. The scout checks source posture, schema, leakage risk, and split feasibility. The strategist turns the objective into a task contract. The scientist challenges baselines, ablations, and budget choices. The builder executes bounded runs. Reviewers reconstruct traces. Release governors lint claims, figures, tables, source packages, and public wording against the evidence record.

Relaytic-AML contributes a local-first evidence and release-governance layer for AML machine-learning experiments, not a new detector architecture. The benchmark rows matter because they exercise the architecture under temporal, graph, operating-point, and claim-governance pressure. The central question is whether a local evaluation lab can keep evidence, agent assistance, privacy boundaries, and publishable claims aligned while preserving the role of each result.

The work is organized around four research questions, each scoped to the workflows and deterministic fixtures evaluated here:

- **RQ1:** Can Relaytic-AML produce reproducible evidence cells for AML-style temporal and graph tasks?
- **RQ2:** Do the implemented gates block the tested leakage-prone and unsupported claims?
- **RQ3:** Can the local artifact record support rowless handoff to external agents while preserving provenance?
- **RQ4:** Do the benchmark workflows produce interpretable evidence under explicit split and budget contracts?

The paper makes three contributions. First, it presents a local-first evidence model for AML experiments that binds reported values to dataset, split, command, artifact, budget, leakage posture, and operating point. Local-first software keeps primary data and control on the user's device while still permitting deliberate collaboration [@kleppmann2019localfirst]. Second, Relaytic-AML implements deterministic release gates for tested leakage, reporting, and external-agent-handoff conditions. Third, the paper evaluates that architecture through PaySim and Elliptic workflows, a separately identified Elliptic2 context workflow, and deterministic fixtures for provenance, handoff, recovery, and claim governance.

## 2. Related Work

The AML benchmark landscape is moving toward larger, more realistic, and more graph-native settings. PaySim remains useful as a synthetic mobile-money fraud simulator for temporal proxy experiments [@lopezrojas2016paysim]. Elliptic introduced a public Bitcoin transaction graph with anonymized node features and temporal labels [@weber2019elliptic]. Elliptic2 and RevTrack/RevClassify shifted attention to suspicious subgraphs and richer blockchain context [@bellei2024elliptic2; @song2024revtrack]. Recent preprints such as TransXion, quasi-temporal graph extraction, and BlazingAML, together with published LineMVGNN and continual graph-learning work, treat AML increasingly as a dynamic graph and systems problem [@chen2026transxion; @poon2025linemvgnn; @tariq2026extraqt; @ye2026blazingaml; @deprez2025continualaml].

Detector papers such as TransXion, BlazingAML, LineMVGNN, and RevClassifyDS push the model frontier. Relaytic-AML sits one layer around that work: it asks how experiments should be governed when data is local or licensed, the task may be temporal or graph-based, analyst review capacity matters, and an agent-assisted workflow must still produce evidence that a skeptical reviewer can audit. The focus on governed local experimentation places Relaytic-AML near dataset documentation, model reporting, reproducibility practice, experiment tracking, and governance work [@gebru2021datasheets; @mitchell2019modelcards; @pineau2021reproducibility; @zaharia2018mlflow].

Experiment-tracking systems preserve runs and artifacts [@zaharia2018mlflow]; model cards describe trained models; datasheets describe data; reproducibility checklists improve reporting; and agent benchmarks evaluate agent behavior. Relaytic-AML handles a different responsibility: determining which public scientific claims a local AML evidence cell is allowed to support. The claim-governance responsibility is especially important when evidence comes from licensed files, proxy datasets, temporal graph tasks, or rowless handoff packets rather than from a single open leaderboard run.

A closely related newer line uses LLMs and agents for AML triage, graph-context reasoning, suspicious activity report (SAR) narrative support, compliance serving stacks, and runtime agent governance [@pirmorad2025amlgraphllm; @naik2025coinvestigator; @naik2026llmopsaml; @gaurav2025governanceaas; @kaptein2026runtimegovernance]. Those systems make agent assistance more capable, but they also make evidence boundaries more important. Relaytic-AML is not a SAR drafting system, not an LLM detector, and not a general-purpose agent-governance product. Its role is narrower: keep local AML evidence, rowless handoff, and public claims aligned.

**What is new.** Relaytic-AML is a governance substrate around detectors and agent-assisted workflows. It would be used to wrap detector outputs, LLM explanations, hosted score files, and paper tables with evidence cells, rowless handoff, and claim gates. A company would not use it as a detector replacement; it would use it to make the local evaluation record inspectable before a result becomes a benchmark row, a handoff packet, or a public claim. In short, Relaytic-AML is not a detector replacement. It is the local evidence layer around detectors and agents.

**Table 1. Adjacent systems comparison.**

| Family | Primary object | Relaytic-AML position | Boundary |
|---|---|---|---|
| Model cards and model reporting [@mitchell2019modelcards] | trained model and intended-use report | adds command-level metric provenance, release gating, and stronger-claim blocking around AML experiments | does not replace model reporting |
| Datasheets and dataset documentation [@gebru2021datasheets] | dataset creation, composition, collection, and recommended use | connects dataset posture to split contracts, leakage controls, benchmark rows, and admissible claims | does not replace source-dataset governance |
| ML reproducibility checklists [@pineau2021reproducibility] | reporting checklist and reproducibility discipline | turns checklist-like obligations into executable artifact-generation and release gates | does not claim full independent reproduction for licensed data |
| MLOps experiment tracking [@zaharia2018mlflow] | runs, metrics, parameters, artifacts, lineage, and model versions | focuses on local AML evidence, privacy posture, rowless handoff, and public scientific claim admissibility | is not a hosted tracker or production model registry |
| Agent benchmarks and research-agent evaluations [@chen2025mlrbench; @starace2025paperbench] | agent performance on research, coding, or skill-use tasks | uses agents inside a governed local evaluation lab and then tests whether their outputs stay artifact-attached | does not benchmark a general-purpose agent |
| AML detector and benchmark papers [@weber2019elliptic; @bellei2024elliptic2] | detector architecture, benchmark result, graph construction, or financial-crime dataset | provides the local evidence and claim-governance substrate that such detector studies can run through | governs detector evidence rather than introducing a graph-neural model |
| AML LLM graph reasoning and triage systems [@pirmorad2025amlgraphllm; @naik2026llmopsaml] | LLM reasoning, triage, serving, and evidence-rich prompts for AML workflows | keeps LLM or external-agent help downstream of rowless local evidence, artifact provenance, and claim gates | does not claim an LLM detector or AML LLM-serving stack |
| Agentic SAR and compliance narrative assistants [@naik2025coinvestigator] | human-in-the-loop SAR or compliance narrative drafting | governs the local experimental evidence and admissible claims that such narrative workflows should cite | does not generate or validate regulatory SAR submissions |
| Agent governance and runtime trust layers [@gaurav2025governanceaas; @kaptein2026runtimegovernance] | runtime policy, enforcement, logging, and trust | specializes governance to AML result provenance, rowless handoff, benchmark context, and public claims | not a general agent-governance platform |

Relaytic-AML does not replace dataset documentation, model cards, experiment trackers, or detector papers. The system ties those concerns together for local AML research: a model result is only reader-facing after its source posture, split, leakage policy, budget, artifact field, handoff posture, and claim boundary are visible.

Recent agent-evaluation work shows that language-model systems can produce persuasive research artifacts while still failing on reproduction, validation, or expert-level judgment [@chen2025mlrbench; @starace2025paperbench; @wijk2025rebench]. Skill- and tool-using agents make that opportunity larger and the governance problem sharper [@yang2026skillopt]. Relaytic-AML responds by making model scores, public claims, handoff packets, and paper assets downstream of local artifacts rather than downstream of a conversation transcript.

## 3. System Overview

Relaytic-AML is built around one authority rule: truth-bearing records live in the local workspace, not in the conversation. Raw data, licensed benchmark files, run summaries, traces, metric cells, model outputs, tables, figures, and release reports live on disk. Agents may explain, propose, and repair, but their proposals only become evidence when they are materialized as artifacts another human or agent can inspect.

![Relaytic-AML local-first architecture: local data and artifacts flow through role-scoped agents into evidence cells, interpretation gates, and paper/release/handoff surfaces.](figures/figure_1_claim_gate_flow.svg)

Figure 1 summarizes the local evidence loop. Dataset registries and split contracts enter the role-scoped agent runtime. Candidate runs write benchmark manifests, search traces, feature reports, and metric cells. Claim gates read those cells together with release audits and emit only the interpretations that the evidence supports. The same contract feeds the command-line interface, project skills, OpenClaw-style handoff, Claude/Codex skill files, and Model Context Protocol (MCP) adapters.

The external-agent path is rowless by default. Relaytic can export current state, next-action options, artifact shortlists, and safe commands for another model without sending raw transaction rows, secrets, or private local paths. A local LLM can optionally help phrase guidance, but the deterministic guide and evidence artifacts remain the source of truth. The separation between advisory help and local evidence matters for private AML work: outside intelligence may help navigate the run, but data residency and claim provenance stay local unless an operator deliberately changes policy.

## 4. Evidence Cell and Claim-Gate Design

An evidence cell is the unit that makes a paper number auditable. Rather than storing a bare metric value, it records the dataset, split, command, artifact field, model or feature budget, leakage posture, and operating point. Interpretation is deliberately stored in a separate gate output: the cell says what happened, and the gate says how that fact may be used.

![Evidence-cell schema: every reported number carries dataset, split, command, artifact, budget, leakage posture, operating point, metric, and value; interpretation is stored separately.](figures/figure_2_supporting_pr_auc.svg)

The table below uses compact publication aliases for readability; the full machine metric-cell identifiers are preserved in the metric-cell audit artifact and generated table comments. Keeping the factual metric record separate from the claim boundary is the central design choice.

**Table 2. Representative evidence cells.**

| ID | Dataset | Metric | Value | Split | Artifact | Evidence role |
|---|---|---|---|---|---|---|
| PS-PR | PaySim | test PR-AUC | 0.6388 | temporal test | PaySim run; manifest | bounded demonstration |
| PS-P@B | PaySim | precision at review budget | 0.7033 | temporal test | PaySim run; manifest | bounded demonstration |
| EL-PR | Elliptic | test PR-AUC | 0.6688 | graph-time test | graph run; feature table | graph-feature evidence |
| EL-P@B | Elliptic | precision at review budget | 1.0000 | graph-time test | graph run; feature table | graph-feature evidence |
| E2-PRm | Elliptic2 | official test PR-AUC mean | 0.9432 | official test | E2 run; scorecard | external reference/context |
| E2-ref | Elliptic2 | published reference PR-AUC | 0.9740 | reported ref. | E2 run; scorecard | external reference/context |

A representative record is compact enough to audit directly. The public table uses the alias `PS-PR`, while the underlying artifact keeps the longer machine identifier. The example shows the factual record that the claim gate later consumes; stronger interpretations are deliberately kept outside the cell.

```json
{
  "cell_id": "PS-PR",
  "dataset_id": "paysim_temporal_transaction_fraud",
  "split": "temporal test",
  "command": "paysim-competitive --budget-tier competitive",
  "artifact_ref": "paper_metric_cell_audit:test_pr_auc",
  "metric": "test_pr_auc", "value": 0.6388,
  "leakage_posture": "balance and raw IDs excluded",
  "claim_state": "bounded PaySim proxy; stronger claims need holdout"
}
```

```algorithm
Algorithm: Evidence-cell creation
Input: dataset registry D, split contract S, candidate budget B, run artifacts A
Output: evidence cell c with factual provenance
1. Freeze source posture, license posture, task target, and split contract.
2. Derive only features allowed by S and record excluded leakage fields.
3. Run baseline candidates under the declared baseline budget.
4. Run stronger candidates only within B and select on validation evidence.
5. Evaluate the selected row once on the fixed test surface.
6. Write c = dataset, split, command, artifact field, metric, value, budget, leakage posture, and operating point.
7. Hand c to the claim gate before it appears in tables, figures, or release text.
```

The claim gate is the second half of the design. Its job is conservative by construction: if the evidence cell is incomplete, if a split is leakage-prone, if a metric is only a proxy, or if a stronger interpretation needs a different dataset or study, the gate preserves the evidence and routes the stronger use to an evidence-needs record. The gate is implemented as a release mechanism, so it changes what the paper artifact pipeline and public release surfaces are allowed to say.

```algorithm
Algorithm: Claim-gate validation
Input: public claim q, evidence cells C, gates G, limitations L
Output: admissible wording and evidence-needs record
1. Resolve every evidence cell named by q and require dataset, split, command, artifact, budget, and leakage fields.
2. Compare the strength of q with source posture, split validity, metric scope, and benchmark role.
3. If q is exactly supported, emit the admissible wording and the evidence-cell identifiers.
4. If q is stronger than C and G permit, record the stronger-claim status and gate reason.
5. Attach the missing evidence needed to make q testable in future work.
6. Route current evidence to its admissible paper use and keep stronger uses out of headline wording.
```

![Claim routing summary: current cells map to admissible paper uses and to evidence needed for stronger future interpretations.](figures/figure_4_publishability_matrix.svg)

Figure 3 gives concrete routing behavior. A PaySim row becomes a temporal-proxy demonstration, an Elliptic row becomes graph-feature evidence with temporal provenance, and an Elliptic2 row becomes external benchmark context. The same records also specify what evidence would be needed before stronger future uses could be made.

## 5. Experimental Protocol

The experiments test Relaytic-AML as an evaluation lab. The datasets are separated by evidence role. PaySim is the main empirical demonstration because it is fully local and supports a controlled temporal proxy workflow. Elliptic tests temporal graph provenance and feature-view discipline. Elliptic2 tests whether the system can keep a modern external reference row visible without overstating its role.

Tables 3 and 4 record the population, split, and feature contracts needed to interpret the reported metrics. PR-AUC is the primary ranking score because the positive class is rare and analyst capacity is constrained. PaySim uses whole chronological simulator-step boundaries with no gap or embargo. Elliptic uses non-overlapping graph time-step windows. Elliptic2 uses the `TRN`, `VAL`, and `TST` labels supplied by the pinned RevTrack preprocessing artifact; it is reported separately as reference context.

**Table 3a. Dataset scale and exact split contracts.**

| Dataset | Unit / positive | Train | Validation | Test |
|---|---|---|---|---|
| PaySim | transactions / fraud events | 1-445: 6,010,937 / 5,007 | 446-594: 228,103 / 1,552 | 595-743: 123,580 / 1,654 |
| Elliptic | known-label nodes / illicit nodes | 1-29: 26,381 / 2,871 | 30-39: 8,999 / 1,038 | 40-49: 11,184 / 636 |
| Elliptic2 context | RevTrack rows / positives | TRN: 88,738 / 2,054 | VAL: 11,059 / 252 | TST: 11,105 / 272 |

Elliptic has 203,769 total nodes; unknown-label nodes are excluded from fitting and metrics. Elliptic2 distinguishes the audited core (121,810 subgraphs) from the RevTrack-evaluable cohort (110,902 rows).

**Table 3b. Feature, leakage, and metric policy.**

| Dataset | Split policy | Allowed information | Excluded information | Primary reporting |
|---|---|---|---|---|
| PaySim | whole chronological steps; no gap or embargo | row-local amount/type/time; prior-step destination history | mixed balance quartet, raw account IDs, simulator flag | PR-AUC; precision/recall at validation threshold |
| Elliptic | disjoint time windows; metrics on known labels | source features; same-snapshot structure; combined view | future snapshots; unknown labels as targets | PR-AUC; precision/recall at validation threshold |
| Elliptic2 context | provided RevTrack TRN/VAL/TST labels | pinned pooled subgraph summaries | full-core equivalence not established | repeated PR-AUC; contextual comparison only |

Modeling effort is intentionally budgeted rather than open-ended. PaySim uses probes on a seeded train-only sample followed by five full-training finalists; selection, Platt calibration, and operating-threshold choice use validation data before one fixed test evaluation [@geurts2006extratrees; @chen2016xgboost; @platt1999probabilistic]. Elliptic compares source-provided anonymized features, Relaytic-derived same-step structural features, and their combination; the selected LightGBM configuration uses seed 42 [@ke2017lightgbm]. Elliptic2 uses pooled subgraph summaries with LightGBM seeds 11, 42, and 73 as a context workflow. The model-family and search-budget inventory is kept in the appendix.

PaySim contains a mixed balance quartet: `oldbalanceOrg` and `oldbalanceDest` describe pre-transaction balances, whereas `newbalanceOrig` and `newbalanceDest` describe post-transaction balances. Relaytic excludes all four conservatively because their availability and simulator consistency do not match the intended pre-decision contract. Raw account identifiers and simulator flags are also excluded as model inputs. Destination history is computed over the full chronological stream as cumulative activity from strictly earlier steps. It carries across train, validation, and test boundaries, but same-step events do not see one another and future steps cannot contribute. The destination identifier is used only as a grouping key, never as a model feature; amount thresholds are fitted on training data. The isolated contribution of this history family has not been tested and is not claimed.
For Elliptic, supervised fitting and metrics use only known labels. Unknown-label nodes may contribute their observable source features and same-step topology, but never targets or metric rows. Relaytic-derived structural features use edges whose endpoints occur in the same snapshot; no future snapshot contributes to an earlier node. The original anonymized node features remain a distinct feature view so the paper does not attribute source-provided information to Relaytic's graph summaries.

## 6. Results

**Table 4. PaySim modeling path.**

| Stage | Model/contract | Selection evidence | Final test evidence | Role |
|---|---|---|---|---|
| P4 reference | SGD logistic baseline | source-safe starting point | 0.2159 | reference row |
| P6 baseline | Extra Trees baseline | leakage-safe feature set | 0.3313 | baseline row |
| Probe screen | best small-sample probe: XGBoost | 26 allowed features; probe validation PR-AUC 0.5944 | no test evaluation | candidate screening |
| Full finalist selection | Extra Trees finalist | full-training validation PR-AUC 0.5687; selected before test | test still hidden | model selection |
| Final fixed test | Extra Trees with Platt calibration | validation-only calibration and threshold | 0.6388 | bounded demonstration |

PaySim is the most complete local modeling path in the current evidence pack. The earliest reference row had test PR-AUC 0.2159, and the later leakage-safe baseline reached 0.3313. A small-sample probe identified a promising XGBoost configuration, but fixed-test eligibility was determined only among the full-training finalists. Extra Trees had the highest full-training validation PR-AUC and was the sole competitive finalist evaluated on the fixed test, where it reached PR-AUC 0.6388 and ROC-AUC 0.9683. Raw and calibrated test PR-AUC are both 0.6388; Platt scaling therefore supports probability and threshold handling here, not a claimed ranking improvement. This is a single-seed point estimate on a synthetic temporal-fraud proxy under the stated feature and selection contract.

The PaySim operating point was chosen by taking the score at the requested top 0.5% rank on validation and applying that threshold unchanged to test. Test rows with scores equal to the threshold are included. Ties therefore produced a realized test queue of 1,109 of 123,580 transactions (0.8974%), with precision 0.7033 and recall 0.4716. This queue is more concentrated than the 1.3384% test prevalence, but it still misses more than half of the positive test events. The requested fraction and realized queue must therefore be read separately.

Elliptic is a different evidence contract. The validation-selected source-plus-structural LightGBM row has validation PR-AUC 0.9767 and later-window test PR-AUC 0.6688. The gap is consistent with temporal shift, validation-specific selection, or both, but the current artifacts do not identify a causal decomposition. The same validation-threshold procedure produced a realized test queue of 36 of 11,184 known-label nodes (0.3219%), with precision 1.0000 and recall 0.0566; the difference from the requested 0.5% again follows from applying a fixed threshold with ties rather than forcing a test-set rank. This seed-42 point estimate supports temporal graph provenance and operating-point reporting. It does not isolate a graph-detector advance, because source-provided anonymized features strongly influence the selected view.

Elliptic2 is modern benchmark context, not a detector contribution. The audited current core contains 121,810 subgraphs and 2,763 positives, whereas the pinned RevTrack-evaluable table contains 110,902 rows and 2,578 positives. The latter supplies `TRN`/`VAL`/`TST` partitions of 88,738/11,059/11,105 rows. The repeated context estimate is PR-AUC 0.9432 $\pm$ 0.0009; a separately defined content-hash partition gives mean PR-AUC 0.9297. The official test partition had already been inspected during an earlier recovery run, so the repeated value is confirmatory rather than an untouched-test estimate. The published RevClassifyDS PR-AUC 0.9740 is shown only as an external reference; cohort equivalence and parity are not established.

![Benchmark evidence by task contract: local ranking estimates, Elliptic2 external-reference context, and validation-threshold review queues are shown in separate panels.](figures/figure_3_review_budget.svg)

Figure 4 separates local ranking evidence, external reference context, and realized review queues. The panels use distinct task contracts and must not be read as a cross-dataset leaderboard. PR-AUC summarizes ranking within a dataset. Precision and recall describe the test rows selected by a validation-derived threshold, while the realized fractions show how ties and score distributions changed queue size.

## 7. Deterministic Artifact and Release-Gate Evaluation

The system claim is evaluated through deterministic reader and agent tasks. These checks ask whether a reviewer can navigate from the README to the paper evidence, trace PaySim metric provenance, compare baseline and competitive budgets, keep Elliptic2 as context rather than a contribution, export rowless state for an external agent, recover an interrupted run, and block over-strong public claims. The main paper reports the synthesis; the detailed failure cases, ablations, invariant map, hosted-score example, and handoff rows are preserved in the appendix and generated evidence artifacts.

**Table 5. Deterministic artifact and release-gate checks.**

| Check | Failure condition | Mechanism | Observed result | Scope |
|---|---|---|---|---|
| Metric provenance | A reported number cannot be traced to source, split, command, or artifact. | Required evidence-cell fields and metric-cell audit. | 13/13 required fields present; metric audit passed. | Proves traceability, not detector optimality. |
| Budget comparability | Baseline and competitive rows are compared under different contracts. | Dataset, split doctrine, metric, and budget checks. | PaySim PR-AUC improved from 0.3313 to 0.6388 under the same contract. | Supports a bounded PaySim comparison, not SOTA. |
| Leakage and selection firewall | Post-event fields or test evidence influence the selected model. | Feature policy plus validation-only selection fixtures. | 4 forbidden balance fields excluded; no test-set selection; one fixed test finalist. | Benchmark-specific leakage taxonomy. |
| Claim-strength gating | Proxy or context rows become real-bank, parity, or headline claims. | Public wording lint, publishability matrix, and stronger-claim cases. | Six stronger-claim cases tested; hard and headline claims blocked. | Deterministic release gate, not peer review. |
| Rowless handoff | An external agent receives raw rows, credentials, or private paths. | Context-export redaction and handoff evaluator. | Rowless handoff preserved next action and allowed tools. | Fixture redaction proof, not a privacy certification. |
| Interrupted recovery | A user or agent cannot recover current state without artifact literacy. | No-lost-user guide and recovery artifact shortlist. | Recovery guide, partial-run state, and artifact shortlist were emitted. | Deterministic recovery check, not a human study. |
| Hosted-score wrapper | A third-party score file is mistaken for Relaytic detector novelty. | Schema/hash adapter, evidence cell, redaction report, and claim map. | 11 exported fields; 16 blocked fields; no raw rows exported | Hosted detector-output governance only. |

Across the tested fixtures, Relaytic-AML changes what the release pipeline may promote: a number with missing provenance, a prohibited feature path, a test-selected finalist, an unsafe handoff packet, or an over-strong claim produces a blocked record instead of reader-facing text. These are deterministic infrastructure checks. They are not human usability evidence, privacy certification, or production AML validation.

The hosted external-score fixture shows the intended integration point for stronger third-party detectors. A rowless detector-score artifact enters Relaytic with schema and content hashes, not raw rows. Relaytic emits one governance evidence cell, redacts unsafe handoff fields, and routes the result as hosted detector-output governance evidence. Future detector outputs can therefore pass through the same local release boundary without being mistaken for a new detector contribution.

## 8. Limitations and Threats to Validity

PaySim is synthetic. It is useful for controlled temporal fraud experiments, but it is not evidence of bank-scale AML superiority. The simulator has known simplifications, and the current result should be interpreted as a leakage-audited proxy result. The destination-history feature contract is present, but the isolated destination-history ablation is not in the current evidence pack, so no separate result is claimed for that feature family.

Public blockchain data is also not the same as bank AML. Elliptic provides a valuable temporal graph task, but unknown labels, anonymized features, and public-chain behavior limit direct operational interpretation. Elliptic2 is modern and highly relevant, but the current local evidence does not satisfy the stronger reference-parity conditions needed for a performance contribution against RevClassifyDS.

The PaySim and Elliptic detector rows are single-seed point estimates. Prediction-level scores are not part of the committed public evidence pack, so confidence intervals cannot be reconstructed faithfully from aggregate metrics. The deterministic system checks are also not a substitute for a human usability study. They test artifacts, redactions, gate decisions, and recovery surfaces, but do not measure analyst time, production incidents, organizational adoption, or investigation quality. Future work should add repeated runs or a predeclared rowless prediction artifact, private or partner-approved holdouts, same-queue incumbent comparisons, and graph-native families under the same evidence discipline.

The system is intentionally local-first, which creates a tradeoff. Privacy and provenance improve because raw rows stay local, but external reviewers cannot rerun licensed or private data without obtaining it themselves. The paper handles that by publishing commands, hashes where allowed, generated artifacts, and claim boundaries, but a fully independent reproduction of every heavy benchmark still depends on legal access to the source datasets.

## 9. Reproducibility

The repository is larger than this AML paper. Relaytic is the general local-first inference lab and public package; Relaytic-AML is the focused AML edition used here for the manuscript. A reader should start with the README and this paper. Development-control files record the build history, but they are not required to understand the paper claims. Public citation should use the final release tag or archival snapshot selected at submission time, because the main branch can continue to evolve after the paper is posted.

Repository: https://github.com/ML-Enthusiast-de/Relaytic. This checked-in PDF is a review build from a working tree with uncommitted changes. The final clean-release command injects and verifies the exact source revision.

The compact contract below separates what a clean clone can reproduce immediately from what requires local benchmark access. The README contains the full regeneration script; the paper keeps the main path short enough to try without reading the generated audit files first.

**Table 6. Reproduction modes and dependencies.**

| Mode | Command fragment | Output class | Requirement |
|---|---|---|---|
| Paper build | paper-release; paper-arxiv-source | Markdown, LaTeX, bibliography, and vector figures | clean clone; TeX required only for PDF compilation |
| Source validation | paper-final-preflight | citations, logs, fonts, links, metadata, and release gates | compiled PDF and local TeX tools |
| Deterministic fixtures | paper-invariants | provenance, claim, handoff, and recovery cases | repo-local fixtures; no benchmark data |
| Artifact verification | paper-release-integrity | metric/split agreement and evidence authority | committed rowless reports; no retraining |
| PaySim raw-data rerun | paysim-competitive --budget-tier competitive --run-optional | competitive model and operating-point artifacts | local PaySim CSV; sha256 prefix 16910f90577b |
| Elliptic raw-data rerun | graph-baselines --budget-tier competitive --run-optional | graph-feature and operating-point artifacts | local Elliptic bundle; sha256 prefix 93e2e7b2405c plus 2 files |
| Elliptic2 context rerun | elliptic2-competitive --run-optional | RevTrack-cohort context artifacts | local Elliptic2/RevTrack files; prior test exposure remains disclosed |

The first three rows below are available from a clean clone. Artifact verification checks committed evidence without retraining. A deterministic fixture rerun executes repo-local synthetic cases. A paper or source-bundle build regenerates publication assets. Raw-data benchmark reruns require local PaySim, Elliptic, or Elliptic2/RevTrack data. For benchmark commands, `--run-optional` requests optional model and data execution; it does not guarantee that unavailable dependencies or datasets were run, so the emitted status and blocked reasons must be checked.

Minimal public check:

```bash
python -m pip install -e ".[full]"
python -m relaytic.ui.cli release-safety paper-invariants --format json
python -m relaytic.ui.cli release-safety paper-release --format json
python -m relaytic.ui.cli release-safety paper-narrative-polish --format json
python -m relaytic.ui.cli release-safety paper-novelty-positioning --format json
python -m relaytic.ui.cli release-safety paper-release-integrity --format json
python -m relaytic.ui.cli release-safety paper-arxiv-source --format json
python -m relaytic.ui.cli release-safety paper-final-preflight --format json
```

Raw benchmark data is not committed. PaySim and Elliptic require local downloads and are referenced through registry artifacts, split reports, hashes, and command ledgers. Elliptic2 is used as benchmark context in this paper because the stronger reference-parity conditions are not satisfied locally. Clean clones can reproduce the paper artifact-build checks and repo-local public fixtures; full benchmark regeneration requires the locally licensed datasets named in the README.

## AI Assistance Disclosure

Large language model tools assisted with drafting, editing, repository inspection, consistency checks, and implementation work around the paper artifacts. They are not authors. The evidence cells, benchmark outputs, source code, figures, tables, limitations, and final interpretation remain the author's responsibility.

## Conclusion

Relaytic-AML shows how an agent-assisted AML evaluation lab can be built around local evidence rather than conversational memory. The system keeps data posture, temporal and graph split validity, leakage controls, model budgets, review-budget operating points, rowless handoff, and public claims inside one artifact record. The PaySim, Elliptic, and Elliptic2 rows are useful because they demonstrate that architecture under realistic forms of pressure, including rare events, graph provenance, modern benchmark context, and governed interpretation.

The evidence supports a bounded architectural conclusion: in the workflows and fixtures evaluated here, Relaytic-AML preserved metric provenance, exposed split and operating-point assumptions, produced rowless handoff records, recovered interrupted state, and blocked the tested unsupported claims. Whether those mechanisms improve expert decisions or production outcomes requires human and institutional evaluation. Relaytic-AML is a governance substrate for detector studies rather than a replacement for them.

## Appendix: Detailed Audit and Reproducibility Records

The appendix keeps the concrete audit evidence out of the main reading path while preserving it for reviewers who want to inspect the mechanics. The tables below summarize generated artifacts; the repository stores the corresponding JSON reports with full fields, hashes, and pass criteria.

**Appendix table. Model families and search budgets.**

| Track | Families | Features | Search budget | Evidence role |
|---|---|---|---|---|
| PaySim | tree and boosting candidates; Extra Trees selected | amount, type, time, shifted destination history | 14 probes; 5 finalists; seeds 42 | validation PR-AUC; one fixed test |
| Elliptic | tree/boosting baselines; LightGBM selected | source node features plus same-step graph statistics | 16 trials; seeds 42 | graph-feature evidence row |
| Elliptic2 | LightGBM context row | 348 pooled subgraph moments/counts | 3 repeated seeds: 11, 42, 73 | external reference row |

The model-search table records budget shape and evidence role. It is appendix material because it supports auditability without changing the paper's central architectural claim.

**Appendix table. Detailed failure-case fixtures.**

| Failure mode | Injected risk | Gate/check | Evidence | Expected behavior | Observed result |
|---|---|---|---|---|---|
| Leakage-column injection | PaySim balance fields are offered as candidate model inputs. | Leakage feature policy | PS-PR feature policy | Post-event balance fields stay out of allowed features. | 4 offered, 4 excluded, 0 used; labels not used as features |
| Test-set selection violation | A model-selection path tries to use test evidence before the finalist is fixed. | Validation-only selection policy | PS-PR search contract | Only validation evidence may select, calibrate, or threshold the finalist. | validation-only probes; no test selection; one finalist test |
| Over-strong claim attempt | Draft wording proposes real-bank superiority or RevClassifyDS parity. | Public claim gate | claim-gate report | Unsupported headline and hard-performance claims remain blocked. | 6 blocked claims; hard and headline claims blocked |
| Rowless handoff redaction | An external-agent packet requests raw rows, private paths, or sensitive fields. | Context export redaction | handoff redaction task | The export contains state and next actions, not raw rows or private paths. | raw rows excluded from export; 8 unsafe fields redacted; 6 blocked fields recorded |
| Interrupted-run recovery | A user or agent resumes a partial run without knowing which artifact to inspect. | No-lost-user guide | guide recovery task | The guide exposes current state, missing evidence, artifact shortlist, and next actions. | partial run recovered; 8 missing-evidence items recorded; 6 recovery actions exposed |

The failure-case fixtures exercise whether the release path refuses leakage features, test-set model selection, over-strong claims, unsafe handoff, and lost-run states. They do not add detector benchmark rows.

**Appendix table. Governance machinery ablation.**

| Path | Disabled machinery | Unsafe signal | Artifact integrity | Handoff / recovery | Interpretation |
|---|---|---|---|---|---|
| Full governance path | none | 0 unsupported claims, leakage inputs, or raw fields | 0 missing fields; 3 table groups | 6 recovery actions exposed | Claim gate, leakage policy, redaction, provenance, and recovery guide are all active. |
| No claim gate | public claim gate | 6 unsupported claims | 3 table groups unchanged | 6 recovery actions exposed | The claim gate is what keeps proxy evidence below hard AML, SOTA, RevClassifyDS parity, production, and business-value claims. |
| No leakage policy | PaySim feature leakage policy | 4 leakage inputs | 0 missing fields; 1 unsafe table path | 6 recovery actions exposed | The leakage policy prevents post-event simulator fields from becoming apparently strong evidence. |
| No rowless handoff redaction | external-agent redaction | 6 raw fields | 3 table groups unchanged | 6 raw fields; 6 recovery actions exposed | Rowless handoff is the privacy boundary that lets outside agents help without receiving raw data or local paths. |
| No evidence-cell required fields | metric-cell required-field gate | 13 missing provenance fields | 13 missing fields; 1 unsafe table path | 6 recovery actions exposed | Required fields are what connect a reader-facing number back to dataset, split, command, artifact, leakage, budget, and claim state. |
| No interrupted-run recovery guide | no-lost-user guide | 0 recovery actions | 3 table groups unchanged | 0 recovery actions exposed | The recovery guide is what keeps state navigation from depending on repo literacy. |

The governance ablation compares the full path with disabled-component fixtures. The detector scores do not change; what changes is which wording and handoff surfaces are allowed to leave the evidence pack.

**Appendix table. Governance invariants and evidence map.**

| Invariant | Mechanism | Evidence and stress signal | Boundary |
|---|---|---|---|
| Metric-cell provenance | metric-cell audit plus required-field gate | audit: pass; stress ablation: 13 provenance fields missing; release blocked | The invariant proves artifact completeness, not that the detector is optimal. |
| Claim-strength monotonicity | claim lint, allowed-claims report, publishability matrix, and overclaim failure case | claim lint: pass; stress overclaim stress: 6 unsupported claims blocked | The gate is a deterministic release check; it is not an external peer review. |
| Leakage and selection firewall | feature policy report, split contract, failure fixtures, and leakage ablation | leakage policy: 4 forbidden fields offered; 0 used; stress leakage stress: 4 leakage fields offered and excluded; 0 used | The current firewall is benchmark-specific; future datasets need their own leakage taxonomy. |
| Rowless external-agent handoff | handoff evaluator plus redaction failure case | handoff audit: raw rows excluded; 8 unsafe fields redacted; 6 fields blocked; stress redaction stress: 6 unsafe fields blocked; raw rows excluded | The check proves deterministic redaction on fixtures, not a broad privacy certification. |
| Interrupted-run recoverability | no-lost-user guide and partial-run recovery fixtures | recovery audit: partial run recovered; 8 missing items; 6 actions exposed; stress recovery stress: partial run recovered; 6 actions exposed | The check is deterministic; it does not measure human time-to-recovery. |
| Benchmark role separation | publishability matrix and allowed-claims report | role matrix: 5 supporting rows allowed; hard/headline claims blocked; stress claim stress: 6 public claims blocked | Rows with external or proxy roles cannot be treated as unified leaderboard evidence. |
| Local-first release safety | release go/no-go, claim lint, and public-claim whitelist | wording lint: pass; stress claim boundary: headline and hard performance claims blocked | Licensed benchmark files are not redistributed; reproduction depends on local access. |

The invariant map records release-time rules rather than prose preferences. Each invariant pairs a mechanism with an observed stress signal and an explicit boundary.

**Appendix table. Hosted external-score case study.**

| Component | Observed evidence | Evidence | Admissible interpretation |
|---|---|---|---|
| Adapter input | external-score adapter over a rowless fixture; schema hash 4b2b70a58b0c; content hash dac68c3801f5 | schema/hash report | The score artifact is described by schema and hash posture, not by raw rows. |
| Evidence emitted | 1 evidence cell; metadata-completeness metric; value 1.0000 | evidence-cell report | Relaytic records the governance metric as auditable evidence, not as detector novelty. |
| Rowless handoff | 11 exported fields; 16 blocked fields; no raw rows exported | handoff-redaction report | A downstream agent can inspect state without receiving rows, identifiers, paths, or secrets. |
| Claim state | hosted detector-output governance only; 5 stronger claims blocked | claim-gate report | The public use is hosted detector-output governance only. |

```json
{
  "cell_id": "p19a.external_score.hosted_metadata_completeness",
  "dataset_id": "p19a_hosted_score_fixture",
  "split": "fixture_holdout",
  "command": "relaytic release-safety paper-external-score-proof",
  "artifact_ref": "fixture:p19a_external_score_rowless_v1",
  "metric": "hosted_score_metadata_completeness",
  "value": 1.0,
  "leakage_posture": "rowless_no_training_or_label_data_exported",
  "claim_state": "hosted_detector_output_governance_only"
}
```

The hosted-score record is metadata governance only. It proves that a rowless score artifact can be wrapped by schema, hash, redaction, and claim-state records.

**Appendix table. Evidence routing examples.**

| Stronger future use | Current admissible use | Evidence needed |
|---|---|---|
| Real-bank deployment study | bounded PaySim temporal-proxy demonstration | Partner or bank-approved holdout, incumbent comparison, analyst-review protocol, and legal release gate. |
| Elliptic2 reference-method comparison | external RevClassifyDS reference marker plus local context row | Faithful reference execution, cohort reconciliation, resource budget, and repeated parity report. |
| Graph-native detector release | Elliptic temporal graph-feature evidence path | Graph-native release budget, neural baselines, repeated seeds, and graph-specific ablations. |

The blocked-claim rows show how stronger future uses are handled. The gate records current admissible use and the evidence needed before a stronger interpretation could be made.

**Appendix table. Rowless handoff and interrupted-run recovery examples.**

| Scenario | Input state | Exported fields | Redacted fields | Observed signal |
|---|---|---|---|---|
| External-agent handoff | partial run with available guide state | state summary, action options, starter questions, tool contract, artifact shortlist | raw transaction rows, credentials, private paths, raw source files | raw rows excluded from export; 8 unsafe fields redacted; 6 blocked fields recorded |
| Safe next action | external model asked what to do next | six next actions, six starter questions, command options | unredacted local paths and data rows | 6 next actions and 6 starter questions exposed |
| Interrupted-run recovery | operator returns to partial run without artifact literacy | current state, missing evidence count, canonical artifact shortlist, context-export command | raw benchmark data and private machine paths | partial run recovered; 8 missing-evidence items and 6 actions exposed |

The handoff and recovery rows give the practical external-agent story. A second model can receive state, commands, artifacts, and starter questions, while raw rows remain redacted and private paths stay withheld.

Appendix reproduction shortcut:

The full Windows and macOS/Linux regeneration script is kept in the README so the appendix remains readable. The essential local paper path is:

Windows PowerShell:

```powershell
py -3.11 -m pip install -e ".[full]"
py -3.11 -m relaytic.ui.cli release-safety paper-invariants --format json
py -3.11 -m relaytic.ui.cli release-safety paper-release --format json
py -3.11 -m relaytic.ui.cli release-safety paper-narrative-polish --format json
py -3.11 -m relaytic.ui.cli release-safety paper-novelty-positioning --format json
py -3.11 -m relaytic.ui.cli release-safety paper-release-integrity --format json
py -3.11 -m relaytic.ui.cli release-safety paper-arxiv-source --format json
py -3.11 -m pytest -m prepush -q
```

After compiling `docs/paper/arxiv_src/main.tex` and copying the PDF to the review draft, run `paper-final-preflight`. The README includes the exact compile/copy commands and the longer audit test matrix.

macOS/Linux:

```bash
python3 -m pip install -e ".[full]"
python3 -m relaytic.ui.cli release-safety paper-invariants --format json
python3 -m relaytic.ui.cli release-safety paper-release --format json
python3 -m relaytic.ui.cli release-safety paper-narrative-polish --format json
python3 -m relaytic.ui.cli release-safety paper-novelty-positioning --format json
python3 -m relaytic.ui.cli release-safety paper-release-integrity --format json
python3 -m relaytic.ui.cli release-safety paper-arxiv-source --format json
python3 -m pytest -m prepush -q
```

## References

- Lopez-Rojas, E. A., Elmir, A., and Axelsson, S. (2016). PaySim: A Financial Mobile Money Simulator for Fraud Detection. European Modeling and Simulation Symposium.
- Financial Action Task Force. (2020). Virtual Assets Red Flag Indicators of Money Laundering and Terrorist Financing. Accessed 2026-07-11.
- Federal Financial Institutions Examination Council. BSA/AML Examination Manual: Appendix F, Money Laundering and Terrorist Financing Red Flags. Accessed 2026-07-11.
- Weber, M., Domeniconi, G., Chen, J., Weidele, D. K. I., Bellei, C., Robinson, T., and Leiserson, C. E. (2019). Anti-Money Laundering in Bitcoin. arXiv:1908.02591.
- Bellei, C., Xu, M., Phillips, R., Robinson, T., Weber, M., Kaler, T., Leiserson, C. E., Arvind, and Chen, J. (2024). The Shape of Money Laundering. arXiv:2404.19109.
- Song, K., Dhraief, M. A., Xu, M., Cai, L., Chen, X., Arvind, and Chen, J. (2024). Identifying Money Laundering Subgraphs on the Blockchain. ICAIF 2024.
- Chen, K. et al. (2026). TransXion: A High-Fidelity Graph Benchmark for Realistic Anti-Money Laundering. arXiv:2604.17420.
- Poon, C.-H., Kwok, J. T. Y., Chow, C., and Choi, J.-H. (2025). LineMVGNN: Anti-Money Laundering with Line-Graph-Assisted Multi-View Graph Neural Networks. AI, 6(4), 69.
- Tariq, H., and Hassani, M. (2026). Extracting Money Laundering Transactions from Quasi-Temporal Graph Representation. arXiv:2604.02899.
- Ye, H., Laxman, A., Yuan, Y., Flautner, K., and Talati, N. (2026). BlazingAML: High-Throughput Anti-Money Laundering via Multi-Stage Graph Mining. arXiv:2604.12241.
- Deprez, B., Wei, W., Verbeke, W., Baesens, B., Mets, K., and Verdonck, T. (2025). Advances in Continual Graph Learning for Anti-Money Laundering Systems. arXiv:2503.24259.
- Pirmorad, E. (2025). Exploring the In-Context Learning Capabilities of LLMs for Money Laundering Detection in Financial Graphs. arXiv:2507.14785.
- Naik, P. V., Dintakurthi, N. K., Hu, Z., Wang, Y., and Qiu, R. (2025). Co-Investigator AI. arXiv:2509.08380.
- Naik, P. V., Dintakurthi, N., and Wang, Y. (2026). Rethinking LLMOps for Fraud and AML. arXiv:2605.11232.
- Pervez, H., Gaurav, S., Heikkonen, J., and Chaudhary, J. (2025). Governance-as-a-Service. arXiv:2508.18765.
- Kaptein, M., Khan, V.-J., and Podstavnychy, A. (2026). Runtime Governance for AI Agents. arXiv:2603.16586.
- Gebru, T. et al. (2021). Datasheets for Datasets. Communications of the ACM.
- Mitchell, M. et al. (2019). Model Cards for Model Reporting. FAT* 2019.
- Pineau, J. et al. (2021). Improving Reproducibility in Machine Learning Research. JMLR.
- Zaharia, M. et al. (2018). Accelerating the Machine Learning Lifecycle with MLflow. IEEE Data Engineering Bulletin.
- Chen, H. et al. (2025). MLR-Bench: Evaluating AI Agents on Open-Ended Machine Learning Research. arXiv:2505.19955.
- Starace, G. et al. (2025). PaperBench: Evaluating AI's Ability to Replicate AI Research. arXiv:2504.01848.
- Wijk, H. et al. (2025). RE-Bench: Evaluating Frontier AI R&D Capabilities of Language Model Agents against Human Experts. ICML 2025.
- Yang, Y. et al. (2026). SkillOpt: Executive Strategy for Self-Evolving Agent Skills. arXiv:2605.23904.
- Saito, T., and Rehmsmeier, M. (2015). The Precision-Recall Plot Is More Informative than the ROC Plot When Evaluating Binary Classifiers on Imbalanced Datasets. PLOS ONE.
- Kleppmann, M., Wiggins, A., van Hardenberg, P., and McGranaghan, M. (2019). Local-First Software. Onward! 2019.
- Geurts, P., Ernst, D., and Wehenkel, L. (2006). Extremely Randomized Trees. Machine Learning.
- Chen, T., and Guestrin, C. (2016). XGBoost. KDD 2016.
- Ke, G. et al. (2017). LightGBM. NeurIPS 2017.
- Platt, J. C. (1999). Probabilistic Outputs for Support Vector Machines. Advances in Large Margin Classifiers.
