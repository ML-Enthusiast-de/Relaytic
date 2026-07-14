# Paper P15 System-Evaluation Proof Pack

- Status: `ready_for_system_evaluation_evidence`
- System pass rate: `1.0`
- Required task count: `22`
- Raw rows exposed: `False`
- Private paths exposed: `False`
- Next slice: `Slice 16A - capability registry and capability cards`

## Reader And Agent Task Evaluation

The reader-task suite checks `11`/`11` concrete navigation, provenance, privacy, and claim-boundary tasks.

| Task | Measured Signal | Source | Result |
| --- | --- | --- | --- |
| repo_navigation_separates_relaytic_from_aml_paper | readme_present=True; mentions_pdf=True | README.md | `pass` |
| cross_platform_reproduction_path_visible | windows_path=True; unix_path=True | README.md | `pass` |
| metric_cell_provenance_available | audit_status=pass; required_fields_present=14/14 | docs/reports/paper_metric_cell_audit.json | `pass` |
| paysim_baseline_and_competitive_budget_comparable | baseline=0.331345; competitive=0.638773; improved=True | docs/reports/paper_metric_cell_audit.json | `pass` |
| paysim_claim_boundary_machine_readable | supporting=True; hard=False; reasons=2 | docs/reports/paper_publishability_matrix.json | `pass` |
| elliptic2_supporting_context_and_firewall_visible | context_role=modern_context_only; firewall_status=blocked_supporting_only_thesis_narrowing_required | docs/reports/paper_publishability_matrix.json | `pass` |
| rowless_external_agent_handoff_recoverable | rowless=True; next_action=True; tools=True | docs/reports/paper_agent_handoff_eval.json | `pass` |
| partial_run_recovery_without_artifact_literacy | onboarding=True; partial=True; shortlist=True | docs/reports/paper_no_lost_user_eval.json | `pass` |
| claim_gate_fails_closed_for_public_interpretation | claim_cases_status=pass; go_no_go=True | docs/reports/paper_claim_gate_case_studies.json | `pass` |
| all_publishability_rows_block_hard_and_headline_claims | rows=5; all_blocked=True | docs/reports/paper_publishability_matrix.json | `pass` |
| result_row_links_metric_cells_and_source_artifacts | row_present=True; artifact_refs=4 | docs/reports/paper_result_table_final.json | `pass` |

## Aggregate Protocol Checks

| Track | Task | Measured Signal | Result |
| --- | --- | --- | --- |
| no_lost_user | onboarding_guide_available | state=onboarding; commands=4; questions=4 | `pass` |
| no_lost_user | partial_run_state_recovery | state=partial_run; missing=8; actions=6 | `pass` |
| no_lost_user | artifact_shortlist_points_to_canonical_state | artifact_count=1; includes_run_summary=True | `pass` |
| agent_handoff | server_tool_contract_available | tool_count=57; required_present=True | `pass` |
| agent_handoff | external_context_rowless_and_redacted | raw_rows=False; redactions=8; blocked_fields=6 | `pass` |
| agent_handoff | safe_next_action_exported | actions=6; starter_questions=6 | `pass` |
| agent_handoff | local_llm_option_is_advisory | llm_status=not_requested; llm_used=False | `pass` |
| claim_gate | p11_claim_lint_passed | status=pass; hard=False; headline=False | `pass` |
| claim_gate | p12_go_no_go_blocks_hard_and_headline_claims | status=go_for_p13_claim_safe_release_pack; blocked=5 | `pass` |
| claim_gate | p12_full_benchmark_rerun_scope_disclosed | fallback=True; withheld_commands=8 | `pass` |
| claim_gate | p12_reproduction_failures_clear | status=no_failures; unresolved=0 | `pass` |
| claim_gate | p13_public_wording_lint_passed | status=claim_safe_public_wording_allowed; lint=pass | `pass` |
| claim_gate | p14_source_bundle_requires_human_upload_gate | source_ready=True; upload_ready=False | `pass` |
| claim_gate | p13_release_manifest_claim_safe | status=ready_for_claim_safe_arxiv_release; release_allowed=True | `pass` |
| reader_task | repo_navigation_separates_relaytic_from_aml_paper | readme_present=True; mentions_pdf=True | `pass` |
| reader_task | cross_platform_reproduction_path_visible | windows_path=True; unix_path=True | `pass` |
| reader_task | metric_cell_provenance_available | audit_status=pass; required_fields_present=14/14 | `pass` |
| reader_task | paysim_baseline_and_competitive_budget_comparable | baseline=0.331345; competitive=0.638773; improved=True | `pass` |
| reader_task | paysim_claim_boundary_machine_readable | supporting=True; hard=False; reasons=2 | `pass` |
| reader_task | elliptic2_supporting_context_and_firewall_visible | context_role=modern_context_only; firewall_status=blocked_supporting_only_thesis_narrowing_required | `pass` |
| reader_task | rowless_external_agent_handoff_recoverable | rowless=True; next_action=True; tools=True | `pass` |
| reader_task | partial_run_recovery_without_artifact_literacy | onboarding=True; partial=True; shortlist=True | `pass` |
| reader_task | claim_gate_fails_closed_for_public_interpretation | claim_cases_status=pass; go_no_go=True | `pass` |
| reader_task | all_publishability_rows_block_hard_and_headline_claims | rows=5; all_blocked=True | `pass` |
| reader_task | result_row_links_metric_cells_and_source_artifacts | row_present=True; artifact_refs=4 | `pass` |
