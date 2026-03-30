# Flagship Demo Pack Contract

## Purpose

This document defines the recruiter-safe and lab-safe flagship demos Relaytic should maintain once the later mission-control slices land.

The goal is to make Relaytic impressive through repeatable proof, not narration.

## Demo 1: Unknown dataset to governed decision

### Story

A first-time operator points Relaytic at an unfamiliar structured dataset, states a reasonable objective, and Relaytic produces a governed result plus a clear next-step recommendation.

### Must prove

- strong onboarding
- clear objective handling
- professional result handoff
- explicit unresolved items
- a believable next-run recommendation

### Required proof artifacts

- result contract
- user report
- agent report
- mission-control view
- onboarding-success evidence

## Demo 2: Incumbent challenge

### Story

A user or external agent brings an incumbent model or prediction baseline. Relaytic evaluates it under the same contract and tries to beat it honestly.

### Must prove

- fair comparison
- explicit beat-target contract
- clear parity reasoning
- no benchmark theater

### Required proof artifacts

- incumbent parity report
- beat-target contract
- search value or continuation reasoning
- result contract

## Demo 3: Skeptical override rejection

### Story

A user or external agent tries to push Relaytic into an unsafe or weakly justified choice. Relaytic challenges the request, records why, and stays legible.

### Must prove

- skeptical control
- trace-backed explanation
- contract-driven refusal or modification
- professional operator experience under tension

### Required proof artifacts

- intervention request
- control challenge report
- override decision
- trace replay
- adjudication scorecard where relevant

## Demo 4: Multi-run workspace continuity

### Story

Relaytic finishes one run, carries the investigation into a second run, preserves governed learnings, and explicitly recommends whether to stay on the same data, add data, or start over.

### Must prove

- workspace lineage
- result-contract parity across reports
- governed learnings
- next-run planning
- no continuity theater

### Required proof artifacts

- workspace state
- workspace lineage
- result contracts for at least two runs
- next-run plan
- learnings state

## Demo scoring

Each demo should be judged at least on:

- clarity
- correctness
- continuity
- operator trust
- agent usability
- replayability

Those judgments should later feed `flagship_demo_scorecard.json`.
