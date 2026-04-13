# Contributing

## Development Setup

Fastest local bootstrap:

- Windows PowerShell: `.\scripts\bootstrap.ps1 -Profile full`
- macOS/Linux: `bash ./scripts/bootstrap.sh --profile full`

1. Create a virtual environment.
   - Windows: `py -3.11 -m venv .venv`
   - macOS/Linux: `python3 -m venv .venv`
2. Activate it and install the project.
   - `python -m pip install --upgrade pip`
   - `python -m pip install -e ".[dev,stats,viz]"`

## Quality Gate

Run these before a PR:

1. `python scripts/check_push_readiness.py --mode quick`
2. `python scripts/check_push_readiness.py --mode prepush`
3. `python -m relaytic.ui.cli scan-git-safety`
4. `relaytic --help`
5. `git status --short`

Use the full wall only when you touched MCP, runtime transport, network-backed dataset fetches, or host-facing interoperability:

1. `python scripts/check_push_readiness.py --mode full`

Use `python -m pytest -q` for the full local suite when you intentionally want the highest confidence wall or are preparing a broader release sweep.

Confirm that `data/private/`, `reports/`, `artifacts/`, `models/`, `.env*`, and `.venv/` are clean or ignored.

## Scope Rules

- Keep Relaytic public naming consistent across docs, config, package metadata, and CLI help.
- Keep deterministic analytics and modeling as the source of truth.
- Keep optional LLM behavior bounded to orchestration and semantic assistance.
- Do not commit secrets, machine-specific paths, private datasets, local environments, or generated credentials.
- Do not introduce new `corr2surrogate` branding into the repository.
- Track compatibility shims explicitly in `MIGRATION_MAP.md` and remove them deliberately.
- Do not deserialize untrusted `.pkl` or `.joblib` model files; imported incumbent models require explicit trust.

## PR Expectations

- Include tests for behavioral changes.
- Update `README.md`, `IMPLEMENTATION_STATUS.md`, and `MIGRATION_MAP.md` when public behavior changes.
- Preserve a professional product surface: concise, inspectable, and reproducible.
