# Security Baseline

Relaytic is developed under a strict local-first and no-leak posture.

## Do Not Commit

- `.env` files
- `.venv/` or any local environment directory
- API keys, bearer tokens, passwords, certificates, or private keys
- local machine paths tied to a specific user account
- private datasets
- generated artifacts that may embed sensitive data

## Required Checks

Before a PR:

1. Run `python -m relaytic.ui.cli scan-git-safety`
2. Inspect `git status --short`
3. Confirm ignored paths remain untracked

## Environment Variables

Use `RELAYTIC_*` variables for Relaytic-specific local overrides.

Legacy `C2S_*` variables are compatibility-only and should not be introduced in new docs or scripts.

## Artifact Hygiene

- Do not persist raw secrets into reports or artifacts
- Do not log auth headers
- Keep generated outputs in ignored directories unless a sanitized example is intentionally added

## Executable Model Files

- Treat `.pkl` and `.joblib` files as executable local code, not inert model blobs.
- Relaytic blocks imported incumbent model deserialization by default.
- Prefer prediction files or JSON rulesets when comparing across trust boundaries.
- Only use `--trust-incumbent-model` or `RELAYTIC_TRUST_LOCAL_MODELS=1` when you explicitly trust the file and the machine it runs on.
