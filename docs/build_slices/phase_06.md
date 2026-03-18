# Slice 06 - Evidence Pressure

## Intent

Slice 06 turns the first built route into a challengeable champion.

The slice is complete only if Relaytic can:

- execute one bounded challenger branch
- execute one bounded ablation suite
- run one provisional audit pass
- expose the resulting judgment to both humans and external agents

This slice is not just reporting polish. It is the first point where Relaytic demonstrates that it can question its own first answer and carry that disagreement forward as artifacts.

## Implemented Surface

Canonical package boundary:

- `src/relaytic/evidence/`

Public CLI additions:

- `relaytic evidence run`
- `relaytic evidence show`

MVP surface change:

- `relaytic run` now includes the evidence layer by default after planning and execution

## Required Artifacts

- `experiment_registry.json`
- `challenger_report.json`
- `ablation_report.json`
- `audit_report.json`
- `belief_update.json`
- `leaderboard.csv`
- `reports/technical_report.md`
- `reports/decision_memo.md`

## Behavioral Contract

- the selected Builder route is treated as a provisional champion, not a final answer
- the challenger branch must be real training work, not a synthetic placeholder
- ablations must be real retraining runs with bounded scope
- audit conclusions must combine deterministic evidence from challenger results, ablations, and inference diagnostics
- local-LLM advisory help may refine memo language or highlight next actions, but it must not replace the deterministic evidence floor
- `run_summary.json` and `reports/summary.md` must surface the provisional recommendation so the top-level MVP remains understandable

## Notes

- Slice 06 is the first layer that makes Relaytic feel like an evidence-driven lab instead of a disciplined single-route pipeline.
- Completion judgment is intentionally deferred to Slice 07. Slice 06 provides provisional recommendation and belief update, not the final lifecycle decision framework.
