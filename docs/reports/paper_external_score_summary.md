# Paper P19-A External Score-File Proof Pack

- Status: `ready_for_hosted_score_governance`
- Selected route: `external_score_file_adapter`
- Score artifact accepted: `True`
- Required metadata completeness: `1.0`
- Claim gate publishable: `True`
- Rowless handoff passed: `True`
- Next slice: `Paper Track P19-B - external score case-study and paper integration`

## Evidence Cells

| Cell | Dataset | Split | Metric | Value | Claim state |
| --- | --- | --- | --- | --- | --- |
| p19a.external_score.hosted_metadata_completeness | p19a_hosted_score_fixture | fixture_holdout | hosted_score_metadata_completeness | 1.0 | hosted_detector_output_governance_only |

## Claim Boundary

- Allowed wording: `hosted_detector_output_governance_only`
- Blocked stronger claims: `5`
- Redacted handoff fields: `16`

## Reproduction

- Windows: `py -3.11 -m relaytic.ui.cli release-safety paper-external-score-proof --format json`
- macOS/Linux: `python -m relaytic.ui.cli release-safety paper-external-score-proof --format json`
