# Paper P17 Governance-Ablation Pack

- Status: `ready_for_governance_ablation_evidence`
- Full path safe: `True`
- Disabled fixture count: `5`
- Fixture scope: `deterministic system-level governance ablation over current paper evidence artifacts`
- Raw rows exposed: `False`
- Private paths exposed: `False`
- Next slice: `Paper Track P18 - governance invariants and adjacent-systems positioning`

## Governance Ablation Matrix

| Path | Disabled Machinery | Unsafe Claims | Leakage Inputs | Raw Fields | Missing Provenance | Publishable Tables | Recovery Actions | Result |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Full governance path | none | 0 | 0 | 0 | 0 | 3 | 6 | `safe` |
| No claim gate | public claim gate | 6 | 0 | 0 | 0 | 3 | 6 | `unsafe` |
| No leakage policy | PaySim feature leakage policy | 0 | 4 | 0 | 0 | 3 | 6 | `unsafe` |
| No rowless handoff redaction | external-agent redaction | 0 | 0 | 6 | 0 | 3 | 6 | `unsafe` |
| No evidence-cell required fields | metric-cell required-field gate | 0 | 0 | 0 | 13 | 3 | 6 | `unsafe` |
| No interrupted-run recovery guide | no-lost-user guide | 0 | 0 | 0 | 0 | 3 | 0 | `unsafe` |
