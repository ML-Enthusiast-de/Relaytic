# External Agent Continuation Contract

## Purpose

This document freezes how external agents should continue work with Relaytic, both on the current shipped surfaces and after the future workspace-first continuity layer lands.

The goal is to keep agent integration explicit, machine-usable, and professional.

## Current agent continuity surfaces

External agents should currently rely on:

- `run_summary.json`
- `run_handoff.json`
- `next_run_options.json`
- `next_run_focus.json`
- `lab_memory/learnings_state.json`
- `relaytic show`
- `relaytic handoff show`
- `relaytic handoff focus`
- `relaytic learnings show`
- `relaytic learnings reset`
- corresponding MCP surfaces

## Future agent continuity surfaces

After Slice 12D lands, external agents should additionally rely on:

- `workspace_state.json`
- `workspace_lineage.json`
- `result_contract.json`
- `next_run_plan.json`
- governed learnings state

## Core rule

External agents should prefer machine-stable JSON or MCP surfaces over prose whenever those machine-stable surfaces exist.

Markdown is a human-friendly companion, not the only continuity source.

## Required agent tasks

An external agent should be able to:

- understand what Relaytic found
- understand what Relaytic recommends next
- continue the same investigation
- choose to add data
- choose to start over
- inspect learnings
- reset learnings deliberately

without scraping HTML or relying on repo-specific folklore.

## Post-run continuation contract

After a serious run, an external agent should be able to determine:

- the current best conclusion
- the recommended next move
- the unresolved items
- whether continuity should stay on the same data, add data, or move to a new dataset
- what learnings are currently active

## Transition rule for Slice 12D

When Slice 12D lands:

- current handoff and learnings commands remain supported
- agents may continue to use the old surfaces
- the new workspace and result-contract surfaces become preferred

External-agent compatibility should therefore be additive, not breaking.

## Agent-oriented mission control expectations

Mission control should provide external agents:

- a stable state summary
- action affordances
- capability posture
- current continuity posture
- handbook references when needed

## Anti-patterns

Later implementation must not:

- require external agents to scrape markdown for canonical next steps
- expose one continuation path in MCP and a different one in CLI
- hide reset or continuation behavior behind UI-only controls
- invent separate agent-only truth that disagrees with the human-facing result contract
