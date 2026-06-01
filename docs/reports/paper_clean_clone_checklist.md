# Paper P12 Clean-Clone Checklist

Run these commands from a fresh clone before arXiv or public attention release.

## Install

```powershell
git clone <repo-url> Relaytic
cd Relaytic
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -e ".[full]"
.\.venv\Scripts\python.exe -m relaytic.ui.cli doctor --expected-profile full --format json
```

## Paper-Smoke Reproduction

```powershell
.\.venv\Scripts\python.exe -m relaytic.ui.cli release-safety paper-tables --format json
.\.venv\Scripts\python.exe -m relaytic.ui.cli release-safety paper-draft --format json
.\.venv\Scripts\python.exe -m relaytic.ui.cli release-safety paper-dry-run --run-isolated-install --format json
.\.venv\Scripts\python.exe -m relaytic.ui.cli scan-git-safety
```

## Pass Criteria

- `paper_clean_clone_install_report.json` status is `pass_clean_clone_ready`.
- `paper_external_dry_run_report.json` status is `pass_paper_smoke_reproduced_claim_linted`.
- `paper_reproduction_failure_report.json` status is `no_failures`.
- `paper_release_go_no_go.json` has `paper_can_continue_to_p13: true`.
- Public wording remains limited to the claim-safe evaluation-environment story.

## Heavy Reruns Outside P12 Smoke

- `python -m relaytic.ui.cli release-safety paysim-benchmark --format json`
- `python -m relaytic.ui.cli release-safety elliptic-graph --format json`
- `python -m relaytic.ui.cli release-safety tabular-baselines --budget-tier baseline --run-optional --format json`
- `python -m relaytic.ui.cli release-safety paysim-competitive --budget-tier competitive --run-optional --format json`
- `python -m relaytic.ui.cli release-safety graph-baselines --budget-tier competitive --run-optional --format json`
- `python -m relaytic.ui.cli release-safety elliptic2-recovery --core-data-dir <external-local-core-dir> --revtrack-dir <external-local-revtrack-dir> --prepare-selected-embeddings --run-pilot --hash-large-assets --format json`
- `python -m relaytic.ui.cli release-safety elliptic2-competitive --revtrack-dir <external-local-revtrack-dir> --budget-tier competitive --run-suite --format json`
- `python -m relaytic.ui.cli release-safety elliptic2-reference-parity --revtrack-dir <external-local-revtrack-dir> --run-neural --format json`

## Current Go/No-Go

- Release decision: `go_for_p13`
- P13 allowed: `True`
- Allowed release mode: `claim_safe_evaluation_environment_only`
