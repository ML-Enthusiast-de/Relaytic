# Relaytic Documentation

The root [`README.md`](../README.md) is the public entry point. This index
separates current product guidance from implementation history and generated
evidence.

## Reader Documentation

- [`why_relaytic_aml.md`](why_relaytic_aml.md) explains the Relaytic-AML use
  case and its claim boundaries.
- [`product_story.md`](product_story.md) maps the main product workflow.
- [`handbooks/relaytic_user_handbook.md`](handbooks/relaytic_user_handbook.md)
  is the operator guide.
- [`handbooks/relaytic_agent_handbook.md`](handbooks/relaytic_agent_handbook.md)
  is the external-agent guide.
- [`paper/README.md`](paper/README.md) identifies the manuscript, source
  package, and reproduction commands.

## Current Engineering Contracts

- [`../ARCHITECTURE_CONTRACT.md`](../ARCHITECTURE_CONTRACT.md) defines stable
  package and runtime boundaries.
- [`../IMPLEMENTATION_STATUS.md`](../IMPLEMENTATION_STATUS.md) records what is
  implemented now and what comes next.
- [`../MIGRATION_MAP.md`](../MIGRATION_MAP.md) records compatibility and
  ownership transitions.
- [`specs/`](specs/) contains current behavioral and artifact contracts.

## Historical Build Records

[`build_slices/`](build_slices/) contains the specifications used to implement
bounded slices. A slice file describes the intended state at that point in the
project. Its local "next" language is historical unless the current status
document says otherwise.

The dated frontier and UI reviews are retained as decision records. Their
status assessments describe the repository on the date shown, not the current
implementation.

## Generated Evidence

[`reports/`](reports/) contains deterministic reports and stage-scoped paper
evidence. These files are useful for audits and regeneration. They are not the
current roadmap. The current manuscript is identified in
[`paper/README.md`](paper/README.md).

