# TODO Evidence Before Public Submission

This file lists evidence items that are intentionally not fabricated in the paper draft.

## Required before arXiv upload

- `TODO_EVIDENCE[author_metadata]`: replace the draft author metadata in `docs/paper/arxiv_src/main.tex` with the author's final name, affiliation, contact, and acknowledgements/license text as appropriate.
- `TODO_EVIDENCE[human_pdf_review]`: perform a final human PDF inspection after metadata is filled, including title page, figures, captions, tables, citations, and page breaks.
- `TODO_EVIDENCE[clean_tag_target]`: rerun the paper-source commands from a clean intended tag target and confirm `git status --short` contains only intended release files.

## Required before stronger empirical claims

- `TODO_EVIDENCE[paysim_prior_history_isolated_test_pr_auc]`: add an isolated PaySim ablation that tests prior-step destination-history features without also changing the search budget, so the feature contribution can be separated from the final competitive search.
- `TODO_EVIDENCE[partner_or_real_holdout]`: add a legally approved real-bank, partner, or otherwise realistic holdout before making hard real-world AML performance claims.
- `TODO_EVIDENCE[elliptic_graph_native_release_budget]`: run graph-native candidate families under a release budget and compare them with the current strong feature baselines before making graph-model superiority claims.
- `TODO_EVIDENCE[revclassify_reference_protocol]`: reproduce the RevClassifyDS/Elliptic2 reference protocol faithfully, or define and publish a new leakage-resistant subgraph protocol, before making parity or superiority claims.
- `TODO_EVIDENCE[human_usability_study]`: run a controlled human or expert-reviewer study before claiming measured human usability or analyst productivity improvement.
- `TODO_EVIDENCE[same_queue_incumbent_eval]`: compare review-budget outputs against the same queue or an approved incumbent baseline before claiming hard business value or analyst-hour savings.
