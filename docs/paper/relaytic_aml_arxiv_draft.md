# Relaytic-AML: A Local-First Evaluation Lab for Financial-Crime ML

## Abstract

Financial-crime machine learning is usually judged by detector scores, but operational AML work depends on evidence a team can trust: data posture, temporal validity, graph provenance, review capacity, and claim discipline. Relaytic-AML is a local-first evaluation lab for that setting. It keeps the workspace as the source of truth, records data and modeling decisions as inspectable artifacts, and lets specialist agents help without making their prose the authority.

Relaytic began as a general local inference-engineering system. In this work it is sharpened into an AML-focused environment where a human or external agent can ask what is known, what is blocked, and what should happen next. The public evidence includes supporting PaySim synthetic temporal-fraud PR-AUC 0.638773, supporting Elliptic temporal graph-feature PR-AUC 0.668756, and Elliptic2 modern-context PR-AUC 0.94324 +/- 0.000882, below the recorded RevClassifyDS reference of 0.974. The contribution is not a detector-superiority claim. It is a reproducible architecture for keeping experiments, review assumptions, limitations, and public wording aligned.

## 1. Introduction

AML systems are operational decision systems. A useful model does not only rank transactions or entities. It has to respect time, explain why a case reached a review queue, preserve graph or entity provenance, and make clear what a result does not prove. This is especially hard in financial-crime work because the most realistic data is private, licensed, regulated, or operationally sensitive.

Relaytic was first built as a broader local inference lab for structured data. The AML edition is a deliberate narrowing of that idea. Instead of trying to be a generic benchmark runner, Relaytic-AML asks a more practical question: can a local machine or local server become a trustworthy evaluation lab where data, modeling work, agent assistance, review assumptions, and public claims stay connected?

The answer explored here is architectural. Relaytic-AML treats the local workspace as the authority. Models, tables, context packs, figures, and paper text are downstream of artifacts on disk. Agents are useful, but they act through bounded roles. A guide explains the current state. A scout checks data posture and leakage risk. A scientist challenges the modeling plan. A builder runs the experiment. A claim governor decides whether a result can be described publicly. The user is never expected to know which file to open first because Relaytic itself can explain the run state and export a compact context pack for another LLM or coding agent.

The benchmarks in this paper are deliberately modest in their role. They are stress tests for the environment. A score is valuable only if the reader can see the dataset boundary, split rule, budget, operating point, limitation, and claim boundary that produced it. This paper therefore presents Relaytic-AML as an evaluation lab first and a benchmark package second.

## 2. Contribution and Scope

This paper is a systems paper about local-first AML evaluation. Its first contribution is the Relaytic-AML architecture: a workspace-centered lab where artifacts, not chat transcripts, carry the truth of an experiment. The second contribution is a role model for agentic help that keeps guidance, scouting, scientific challenge, model building, and claim review separate. The third contribution is an evidence-cell contract that makes every reported number traceable to a dataset, split, command, artifact field, budget, operating point, and claim state. The fourth contribution is a claim discipline that keeps useful evidence from becoming stronger than it deserves to be.

This scope matters. Relaytic-AML does not claim hard AML superiority, production readiness, graph-neural superiority, or equivalence to RevClassify. It shows a working local evaluation environment that can run meaningful public evidence, expose where stronger claims remain blocked, and give both humans and agents a stable way to continue the work.

| Paper claim | Relaytic mechanism | Current evidence posture |
|---|---|---|
| Local state is auditable | Run directories, manifests, traces, metric cells, tables, and release reports live in the workspace | Demonstrated by the generated paper and source package |
| Agent help is bounded | Guide, scout, scientist, builder, and claim governor roles have separate jobs and artifacts | Architecture evidence; not yet a formal autonomy benchmark |
| Scores are traceable | Evidence cells bind every number to dataset, split, command, artifact field, budget, and claim state | Supporting PaySim, Elliptic, and Elliptic2-context rows |
| Public wording is governed | Claim linting, release manifests, and source-package audits fail closed | Hard and headline AML claims remain blocked |

## 3. Questions

The central question is whether an AML evaluation system can stay useful without becoming opaque. A trained reader can understand PR-AUC, temporal splits, graph features, and review budgets. That reader cannot know Relaytic's internal state unless the system makes it legible. The paper therefore asks whether Relaytic can keep the state of a run visible, whether external agents can receive enough structured context to help safely, and whether claim boundaries can stop a local result from being overstated.

| Question | What to inspect | Current answer |
|---|---|---|
| Can local artifacts remain the authority? | Source manifests, run summaries, metric cells, tables, and source-bundle reports | Yes for the current paper path |
| Can humans and agents avoid getting lost? | Guide, status, assist, mission-control, and redacted context-export surfaces | Supported by product surfaces; formal user/agent study remains future work |
| Can benchmark evidence stay useful without becoming marketing language? | Claim-boundary reports, public wording lint, and release gates | Yes: supporting rows are visible while stronger claims stay blocked |
| What would make the work stronger? | Future unlock conditions for holdout data, same-queue comparison, and faithful graph reference reproduction | Explicitly listed as future work rather than implied as solved |

## 4. Local-First Agent Architecture

Relaytic is designed around one control rule: the user's workspace is the authority. Raw and licensed data stay local by default. Run directories, manifests, traces, metric cells, model files, and paper assets form the durable record. Semantic caches, memory indexes, and LLM summaries are derived views. This is different from a remote-first agent that sends private rows to a hosted planner and later reconstructs provenance from a conversation.

The system is agentic, but the roles are concrete. They are small jobs with bounded permissions and visible outputs. A scout inspects source posture and split risk. A scientist challenges baselines and ablations. A builder executes a controlled run. A claim governor can reject wording even when the model score looks attractive. A guide explains the current state to a human or exports a redacted context pack to another model.

| Role | What it owns | Local-first boundary | Main artifacts |
|---|---|---|---|
| Operator and mandate owner | Sets goals, constraints, privacy posture, and stop/continue preferences. | Can keep all data on a controlled local machine, server, or cluster. | Mandate, policy, permission, and next-action artifacts. |
| Guide and assist layer | Answers where the run is, what artifacts matter, and which action is safe next. | Uses local artifacts first. Optional LLM help is advisory and redacted by default. | Guide payloads, assist turns, status, and context packs. |
| Scout and task-contract agents | Inspect source posture, target semantics, split validity, and leakage risk. | Work from staged local snapshots rather than mutating the original data source. | Dataset registry, source manifests, split contracts, and task reports. |
| Scientist and challenger agents | Propose baselines, ablations, shadow candidates, and failure explanations. | Candidate work is bounded by explicit budgets and local artifact permissions. | Experiment registry, scorecards, ablations, and shadow-trial reports. |
| Builder and search controller | Execute reproducible model/search plans and select thresholds on validation evidence. | Optional adapters are versioned and never become hidden sources of truth. | Run directories, model artifacts, search traces, and operating-point records. |
| Claim and release governors | Decide which evidence can be said publicly and which claims stay blocked. | Fail closed on leakage, missing provenance, unsafe wording, or dirty release state. | Metric cells, claim boundaries, public wording notes, and source-bundle audits. |
| External agents or LLMs | Consume exported context, propose repairs, or continue work through stable surfaces. | Receive rowless/redacted context unless policy explicitly grants richer access. | External context packs, handoff reports, and reproducible commands. |

Two design choices carry most of the system. First, important work produces a local artifact that another human or agent can inspect. Second, optional intelligence is subordinate to the artifact graph. A local LLM may help phrase guidance, and a frontier model may suggest repairs, but neither becomes the source of truth unless its proposal is converted into a reproducible local artifact.

![Local-first Relaytic agent architecture](figures/figure_1_claim_gate_flow.svg)

## 5. Current Frontier Context

The current AML frontier is not a single leaderboard. It is a set of pressure points: real graph scale, realistic entity behavior, temporal drift, operational throughput, and reliable agent-assisted research. Relaytic-AML is designed as infrastructure around those pressure points, not as a replacement for detector papers.

Recent agentic-ML work also treats external state, benchmark environments, and research validity as first-class objects. SkillOpt, for example, frames agent skills as trainable external state with validation-gated edits [@yang2026skillopt], while MLR-Bench evaluates whether agents can produce valid open-ended ML research rather than only fluent reports [@chen2025mlrbench]. Relaytic-AML follows the same broader style of making the environment and its evidence inspectable, but applies it to AML-specific data custody, review queues, and public-claim gates.

PaySim is a synthetic mobile-money simulator designed to address the scarcity of legitimate public mobile-transaction datasets for fraud research [@lopezrojas2016paysim]. It is useful for temporal transaction-fraud workflow evaluation, but synthetic evidence cannot by itself establish hard real-bank AML performance.

The Elliptic Bitcoin dataset introduced a public transaction graph with more than 200K transaction nodes, 234K directed payment-flow edges, and 166 node features across 49 time steps [@weber2019elliptic]. That work also showed why graph evidence must be compared against strong simpler baselines rather than assumed superior.

Elliptic2 shifts the public AML benchmark center toward subgraph learning, with 121,810 labeled subgraphs inside a background graph of roughly 49M node clusters and 196M edge transactions [@bellei2024elliptic2]. RevTrack and RevClassify further argue that sender and receiver context around a subgraph can be a powerful and scalable signal [@song2024revtrack]. These works motivate Relaytic-AML's modern-context and limitation track, but they do not make the current Relaytic Elliptic2 row a performance contribution.

Recent AML graph work raises the bar beyond the current Relaytic evidence rows. TransXion frames benchmark realism around profile-aware simulation, richer entity attributes, non-template illicit synthesis, and out-of-character behavior [@chen2026transxion]. LineMVGNN and ExSTraQt focus on directed money flow, edge-aware graph views, and quasi-temporal transaction representations [@poon2026linemvgnn] [@tariq2026extraqt]. BlazingAML treats throughput and multi-stage graph mining as a systems problem [@ye2026blazingaml]. Continual graph-learning reviews emphasize drift, adaptation, class imbalance, and changing laundering behavior [@deprez2025continualaml]. Relaytic-AML is complementary to these efforts. It does not claim detector parity with them. It tries to make dataset posture, split validity, budget, limitations, and public claims auditable.

The paper also follows broader ML documentation and reproducibility practice. Datasheets for Datasets and Model Cards argue for explicit dataset and model reporting [@gebru2021datasheets] [@mitchell2019modelcards]. The NeurIPS reproducibility program highlights the need for code, data, and checklist discipline in ML research [@pineau2021reproducibility]. Recent work on ML research agents warns that coherent papers can still contain invalidated experiments, which reinforces the need for executable artifacts and claim boundaries [@chen2025mlrbench].

## 6. Methodology: Evidence Cells, Gates, and Budgets

Relaytic-AML treats a metric as an evidence cell, not as a free-standing score. An evidence cell records the dataset identity, split contract, execution command, run or artifact reference, metric value, budget tier, leakage posture, operating-point rule, claim state, and limitation notes. A reported row is accepted only when those fields are present.

The claim gate is intentionally conservative. It can mark a row as supporting evidence, modern context, baseline-only evidence, or blocked evidence. In the current public version, no row is headline-eligible. This is not a weakness of the environment. It is the point of the environment. A strong-looking number is only useful if the system can also say what the number is allowed to mean.

The budget ladder separates quick engineering checks from serious evidence. Smoke runs test that commands and artifacts exist. Baseline runs establish conservative rows. Competitive runs add stronger feature families, validation-only threshold selection, calibration, and model search. Frozen reporting runs preserve the transformation from experiment to table, figure, and public claim. This prevents a weak first pass from being quietly promoted into a strong paper claim.

For an external reader, the important idea is simple: every number has a trail, and every claim has a boundary. The trail helps another person reproduce or challenge the result. The boundary says whether the result is a benchmark observation, an operational estimate, a limitation, or a claim that should not be made yet.

## 7. Evidence Operating Layer

The local-first architecture becomes concrete through an evidence operating layer. Relaytic-AML is not only a model runner. It coordinates source posture, task semantics, split discipline, model search, decision thresholds, review queues, artifacts, and claim boundaries.

| Layer | What Relaytic records | Why it matters |
|---|---|---|
| Source and task contracts | Dataset access, target semantics, benchmark posture, and split rules | A reader can see whether the task is valid before judging the score |
| Execution and search | Candidate families, budgets, calibration, thresholds, and selected runs | Model development becomes inspectable instead of anecdotal |
| AML domain layer | Entity graphs, typology posture, review queues, delayed labels, and case evidence | The model is tied to the analyst workflow it is supposed to support |
| Evidence ledger | Metric cells, tables, figures, limitations, and commands | Numbers are connected to the artifacts that produced them |
| Claim boundaries | Allowed claims, blocked claims, and future unlock conditions | The same result cannot quietly become marketing language |
| Handoff surfaces | Guide, status, assist, mission control, and redacted context export | Humans and external agents can continue work without guessing hidden state |

This operating layer is useful even when a detector claim is blocked. A blocked row is not thrown away. It becomes a structured research state with a reason, an artifact reference, and a repair path.

## 8. What Relaytic-AML Is For

The intended user is a person or team that has data, a risky modeling question, and a need to know whether the evidence is strong enough to act on. That includes a bank team comparing a new model against an incumbent queue, a fraud group exploring a new dataset, a researcher testing a benchmark protocol, or an external agent trying to continue a run without seeing private rows.

| Capability | Reader-facing meaning |
|---|---|
| Local-first privacy posture | Private or licensed data can stay outside the public repo while hashes, access posture, and evidence artifacts remain inspectable |
| Artifact-first reproducibility | Tables and figures are tied to local JSON and model artifacts rather than loose notes |
| Role-scoped agent help | A guide, scout, scientist, builder, and claim reviewer have different responsibilities |
| Budget-aware modeling | Quick checks, baseline evidence, competitive runs, and frozen reporting are kept separate |
| Operational evaluation | Review-budget precision, recall, false-positive burden, and case-packet completeness sit next to model metrics |
| External context export | Another LLM or coding agent can receive a redacted summary and reproducible commands |

This is why the project moved from a broad Relaytic system toward Relaytic-AML as the flagship story. The general architecture still matters, but AML gives it a sharper test. It forces the system to handle rare events, temporal splits, graph context, human review limits, privacy, and public-claim discipline at the same time.

Companies could use this kind of lab to challenge incumbent rules or models on the same review queue, evaluate whether a new dataset is worth deeper investment, audit whether a vendor comparison is fair, and prepare evidence packs for compliance or model-risk review. Researchers could use it to ask whether an AML result is supported, blocked, or mainly useful as a limitation.

## 9. Evaluation Environment

The current evaluation environment combines public benchmark evidence with local artifact discipline. Dataset registry artifacts define source and access posture. Split contracts define chronological, graph-snapshot, or subgraph partition rules. Benchmark runners produce model and operating-point artifacts. Tables and figures then read from those artifacts.

The current public evidence uses three tracks. PaySim is a synthetic temporal proxy. Elliptic is temporal graph-feature evidence. Elliptic2 is retained as modern subgraph context and limitation evidence because a faithful RevClassify reference-protocol reproduction has not yet been completed locally.

The environment follows three design rules. Local artifacts are the source of truth. Validation selects models, thresholds, and operating points before fixed test evaluation. Blocked evidence stays visible because hiding failed or incomplete tracks makes both human and agent-assisted research less scientific.

## 10. Benchmark Protocol

The benchmark protocol is deliberately subordinate to the architecture. Its purpose is to check whether Relaytic can produce traceable evidence, respect split and leakage contracts, expose operational assumptions, and block unsupported claims. A single score does not define the value of the system.

The public rows separate baseline and competitive evidence. Competitive rows use stronger feature families, candidate search, calibration, and validation-only operating-point selection. The goal is not to pretend the current numbers are final. The goal is to make their scope visible.

The evidence summary below should be read as a claim-boundary table as much as a performance table. The numbers matter, but the posture column is what stops them from being overstated.

| Evidence row | Metric | Value | Claim posture |
|---|---:|---:|---|
| PaySim baseline | test PR-AUC | 0.331345 | baseline-only |
| PaySim competitive | test PR-AUC | 0.638773 | supporting-only synthetic temporal proxy |
| PaySim competitive | precision at review budget | 0.703336 | supporting-only |
| PaySim competitive | recall at review budget | 0.471584 | supporting-only |
| Elliptic graph-feature | test PR-AUC | 0.668756 | supporting-only graph-feature evidence |
| Elliptic graph-feature | precision at review budget | 1 | supporting-only |
| Elliptic graph-feature | recall at review budget | 0.056604 | supporting-only |
| Elliptic2 context | official-partition PR-AUC mean | 0.94324 | modern context only |
| Elliptic2 context | official-partition PR-AUC std | 0.000882 | modern context only |
| RevClassifyDS reference | published PR-AUC | 0.974 | reference context, not parity |

![Supporting PR-AUC rows with claim posture](figures/figure_2_supporting_pr_auc.svg)

![Review-budget precision and recall](figures/figure_3_review_budget.svg)

![Claim boundaries and future unlocks](figures/figure_4_publishability_matrix.svg)

## 11. Results

The PaySim competitive row improves over the PaySim baseline inside the synthetic temporal-fraud contract. The Elliptic graph-feature row is useful supporting graph evidence, but it is not a graph-neural superiority claim. The Elliptic2 context row is strong enough to justify more work, but not enough to claim parity with the RevClassifyDS reference or to make an Elliptic2 performance contribution.

The more important result is the behavior of the environment. Relaytic can carry a useful score and still refuse the stronger sentence. In financial-crime ML, that refusal is not cosmetic. It is part of scientific and operational honesty.

| Track | Current paper use | Blocked stronger claim | Evidence needed before promotion | Gate status |
|---|---|---|---|---|
| PaySim temporal proxy | supporting synthetic temporal-fraud evidence | real-bank AML superiority | partner or real holdout with frozen evaluation budget | supporting only |
| Elliptic graph-feature | supporting temporal graph-feature evidence | graph-neural or graph benchmark superiority | repeated graph evaluation budget against strong feature baselines | supporting only |
| Elliptic2 subgraph | modern subgraph context and limitation evidence | Elliptic2 performance contribution or reference-method match | faithful RevClassify reproduction or leakage-resistant subgraph protocol | context only |
| Operational review layer | supporting review-budget estimates | hard analyst-hour or business-value claim | complete case packets and same-queue incumbent comparison | supporting only |

## 12. Discussion

The practical value of Relaytic-AML is not that it replaces a compliance platform or wins one benchmark table. Its value is that it gives risk, fraud, or AML teams a local evidence lab for unknown datasets, incumbent challenges, review-budget tradeoffs, leakage checks, and claim discipline. A team evaluating a new dataset can inspect whether the result is a model win, an environment win, a proxy-only result, or a blocked claim.

For research teams and agentic ML workflows, the same structure is a guard against coherent but invalid experiments. External agents can read the structured artifacts, see blocked claims, and propose the next benchmark action without inferring hidden state from prose. The strongest story is the artifact discipline: Relaytic-AML demonstrates that an ambitious evaluation system can still refuse claims it has not earned.

The system is also valuable when results are not spectacular. A low or blocked row can still tell a team that a dataset is synthetic-only, that a split leaks future information, that a graph-native candidate failed to beat strong tabular features, that a review-queue claim lacks a same-queue incumbent, or that a paper sentence is stronger than the evidence permits. In high-risk financial-crime settings, those negative answers are productive outputs.

A company would not use Relaytic-AML because it magically knows AML. It would use it because the difficult parts of a model evaluation are forced into the open: what data was allowed to move, what split was used, what budget was spent, whether the threshold was chosen on validation evidence, what a reviewer would see, and which sentence the evidence still refuses to support.

## 13. Limitations

The current public evidence is not a deployment validation. PaySim is synthetic mobile-money evidence, so it cannot establish real-bank AML superiority. The Elliptic row is a temporal graph-feature result, not proof that a graph-neural model is better. Elliptic2 is modern context, not a Relaytic performance contribution, because faithful reference-protocol reproduction and cohort equivalence still need more work.

The operational evidence also remains early. The review-budget rows are useful for showing how Relaytic connects model output to analyst capacity, but they do not prove analyst-hour savings against an incumbent queue. A stronger version of this work should include complete case packets, a same-queue incumbent comparison, and a partner-approved or otherwise realistic holdout.

The paper therefore does not make a hard AML superiority claim. It argues that Relaytic-AML is a useful local evaluation environment and that the current benchmark rows are enough to demonstrate the architecture. They are not enough to end the detector question.

## 14. Future Work

The next step is to make the architecture harder to fool and the evidence more operationally realistic. Some work should test Relaytic itself: whether the guide, scout, scientist, builder, and claim reviewer agree about the same local run state, and whether an external LLM can use a redacted context pack to propose a useful repair without inventing unsupported claims. Other work should push the AML evidence: a partner-approved holdout, faithful Elliptic2 reference reproduction, stronger graph-native candidates, continual-learning experiments, and same-queue business-value comparisons.

The next strong paper version should evaluate the environment as directly as it evaluates detector rows. A first-time human, a local LLM, and an external coding agent should each be given the same run and asked to recover current state, identify the right artifacts, propose the next safe action, and avoid unsupported public claims. That would turn Relaytic's usability promise into a measurable benchmark rather than a narrative assertion.

| Direction | What would make the claim stronger |
|---|---|
| Role-level evaluation | Show that guide, scout, scientist, builder, and claim reviewer agree on the same run state |
| External-agent handoff | Measure whether redacted context packs let another model help without seeing private rows |
| Realistic AML holdout | Add partner-approved or otherwise realistic data with frozen access posture and repeated runs |
| Elliptic2 reproduction | Run a faithful RevClassify-style protocol or define a new leakage-resistant cohort |
| Operational proof | Compare against the same review queue or incumbent ruleset with complete case packets |
| Continual learning | Add drift, delayed labels, recalibration, and forgetting tests |

The longer-term goal is still broader than AML. Relaytic should become a general local evaluation laboratory for structured, temporal, and graph ML. AML is the current flagship because it forces the system to handle privacy, time, graph context, human review, and claim discipline together.

## 15. Reproducibility

The code, paper source, figures, tables, and public evidence artifacts are in the Relaytic repository. The public repo keeps raw private or licensed data out of version control. Where a benchmark requires local data, the command ledger describes the expected local paths and access posture.

A compact reproduction path for the public paper assets is:
```powershell
relaytic release-safety paper-tables --format json
relaytic release-safety paper-draft --format json
relaytic release-safety paper-release --format json
relaytic release-safety paper-arxiv-source --format json
relaytic scan-git-safety
```

The main reader-facing files are `docs/paper/relaytic_aml_arxiv_draft.md`, `docs/paper/relaytic_aml_arxiv_draft.pdf`, `docs/paper/arxiv_src/`, `docs/paper/figures/`, and `docs/paper/tables/`. The benchmark command ledger is `docs/reports/paper_reproduction_commands.md`. The README explains the current project shape: Relaytic remains the general package and CLI, while Relaytic-AML is the flagship AML edition used for this paper.

## 16. Author Use of AI Assistance

This manuscript was written and revised by the human author with assistance from LLM-based tools for drafting, editing, repository inspection, consistency checks, and formatting support. The author reviewed the text, code references, figures, tables, claims, and limitations, and remains responsible for the accuracy and interpretation of the work. The LLM tools are not listed as authors because they do not take responsibility for the manuscript or the underlying experiments.

## 17. Conclusion

Relaytic-AML should be read as a local-first AML evaluation-lab paper. The current work is valuable because it makes the operating idea concrete. Data stays locally governed. Specialist roles create inspectable artifacts. External agents receive structured context instead of hidden state. Claim boundaries prevent stronger wording than the evidence has earned. The same evidence does not support hard AML superiority, a headline benchmark claim, graph-neural superiority, claimed equivalence to RevClassify, or hard business value. That restraint is not a footnote. It is part of the contribution.

The right test for this version is therefore not whether it ends the AML detector race. It does not. The right test is whether the repository makes the current evidence easier to inspect, easier to challenge, and harder to oversell. That is the claim this paper is prepared to make.

## References

- Lopez-Rojas, E. A., Elmir, A., and Axelsson, S. (2016). PaySim: A Financial Mobile Money Simulator for Fraud Detection. European Modeling and Simulation Symposium.
- Weber, M., Domeniconi, G., Chen, J., Weidele, D. K. I., Bellei, C., Robinson, T., and Leiserson, C. E. (2019). Anti-Money Laundering in Bitcoin. arXiv:1908.02591.
- Bellei, C., Xu, M., Phillips, R., Robinson, T., Weber, M., Kaler, T., Leiserson, C. E., Arvind, and Chen, J. (2024). The Shape of Money Laundering. arXiv:2404.19109.
- Song, K., Dhraief, M. A., Xu, M., Cai, L., Chen, X., Arvind, and Chen, J. (2024). Identifying Money Laundering Subgraphs on the Blockchain. ICAIF 2024.
- Chen, K. et al. (2026). TransXion: A High-Fidelity Graph Benchmark for Realistic Anti-Money Laundering. arXiv:2604.17420.
- Poon, C.-H., Kwok, J., Chow, C., and Choi, J.-H. (2026). LineMVGNN: Anti-Money Laundering with Line-Graph-Assisted Multi-View Graph Neural Networks. arXiv:2603.23584.
- Tariq, H., and Hassani, M. (2026). Extracting Money Laundering Transactions from Quasi-Temporal Graph Representation. arXiv:2604.02899.
- Ye, H., Laxman, A., Yuan, Y., Flautner, K., and Talati, N. (2026). BlazingAML: High-Throughput Anti-Money Laundering via Multi-Stage Graph Mining. arXiv:2604.12241.
- Deprez, B., Wei, W., Verbeke, W., Baesens, B., Mets, K., and Verdonck, T. (2025). Advances in Continual Graph Learning for Anti-Money Laundering Systems. arXiv:2503.24259.
- Gebru, T. et al. (2021). Datasheets for Datasets. Communications of the ACM.
- Mitchell, M. et al. (2019). Model Cards for Model Reporting. FAT* 2019.
- Pineau, J. et al. (2021). Improving Reproducibility in Machine Learning Research. JMLR.
- Chen, H. et al. (2025). MLR-Bench: Evaluating AI Agents on Open-Ended Machine Learning Research. arXiv:2505.19955.
- Yang, Y. et al. (2026). SkillOpt: Executive Strategy for Self-Evolving Agent Skills. arXiv:2605.23904.
