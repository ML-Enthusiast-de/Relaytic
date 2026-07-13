# Paper P16 Failure-Case Evaluation Pack

- Status: `ready_for_failure_case_evidence`
- Case pass rate: `5`/`5`
- Fixture scope: `deterministic injected-risk audit over current paper evidence artifacts`
- Raw rows exposed: `False`
- Private paths exposed: `False`
- Next slice: `Paper Track P17 - governance machinery ablation pack`

## Injected Failure Cases

| Case | Injected Risk | Gate Or Check | Expected Behavior | Observed Result | Result |
| --- | --- | --- | --- | --- | --- |
| Leakage-column injection | PaySim balance fields are offered as candidate model inputs. | Leakage feature policy | Post-event balance fields stay out of allowed features. | offered=4; excluded=4; used=0; labels_for_features=False | `pass` |
| Test-set selection violation | A model-selection path tries to use test evidence before the finalist is fixed. | Validation-only selection policy | Only validation evidence may select, calibrate, or threshold the finalist. Prior P4/P6 test exposure must remain disclosed. | probe_surfaces=1 validation-only; test_used_for_selection=False; final_policy=one_competitive_finalist_evaluated_after_validation_only_selection_and_protocol_freeze; prior_test_exposure=True | `pass` |
| Over-strong claim attempt | Draft wording proposes real-bank superiority or RevClassifyDS parity. | Public claim gate | Unsupported headline and hard-performance claims remain blocked. | blocked_claims=6; hard_allowed=False; headline_allowed=False | `pass` |
| Rowless handoff redaction | An external-agent packet requests raw rows, private paths, or sensitive fields. | Context export redaction | The export contains state and next actions, not raw rows or private paths. | raw_rows=False; redactions=8; blocked_fields=6 | `pass` |
| Interrupted-run recovery | A user or agent resumes a partial run without knowing which artifact to inspect. | No-lost-user guide | The guide exposes current state, missing evidence, artifact shortlist, and next actions. | state=partial_run; missing=8; actions=6 | `pass` |
