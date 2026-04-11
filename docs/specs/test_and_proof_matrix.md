# Test And Proof Matrix

## Purpose

This document defines the minimum proof burden for future Relaytic work.

The goal is to prevent slices from landing with plausible artifacts but weak evidence.

## Global rule

Every future slice should add:

- targeted unit tests
- targeted CLI or MCP integration tests
- one realistic workflow test
- one regression guard for the most likely failure mode

## Required proof categories

### 1. Schema and contract proof

Future slices that introduce new canonical artifacts must test:

- schema completeness
- enum validity
- fallback behavior
- backward compatibility where promised

### 2. Human workflow proof

Human-facing slices must test:

- first-time use
- recovery after confusion
- continuation after a detour
- post-run next-step understanding

### 3. External-agent proof

Agent-facing slices must test:

- MCP or CLI parity
- machine-readable continuity
- command-hint usability
- no markdown scraping requirement for canonical actions

### 4. Chaos proof

Chaos-style tests should include:

- user pastes only a path
- user pastes a path and objective in one line
- user goes off topic and returns
- user asks for weather or small talk in between
- user changes objective midstream
- user asks to reset

### 5. Workspace proof

Workspace-aware slices must test:

- two-run continuity
- result-contract parity across reports
- governed learnings invalidation
- next-run plan transitions
- start-over versus continue correctness

### 6. Trace and adjudication proof

Trace-aware slices must test:

- canonical replay
- losing claim visibility
- contract-driven winner selection
- protocol-conformance parity across surfaces

### 7. Release-safety proof

Release- or packaging-facing slices must test:

- machine-path leak detection
- source-map or debug-artifact detection
- attested clean-build generation
- host-bundle and docs-bundle safety checks

### 8. Permission and supervision proof

Runtime-authority slices must test:

- visible permission-mode transitions
- allow versus approval-gated versus denied action behavior
- CLI, MCP, and later remote parity on authority state
- approval audit correctness

### 9. Background and resume proof

Daemon or long-session slices must test:

- checkpoint resume
- stale-job detection
- memory-maintenance queue behavior
- no hidden background activity outside the canonical job registry

### 10. Benchmark-pack proof

Paper-facing benchmark packs should test:

- coverage across the main Relaytic task families
- primary-source dataset traceability
- bundled versus network-backed separation
- representative benchmark plus eval materialization on a smaller heavy subset

## Required future shard groups

To reduce timeout risk, future CI should support at least:

- `mvp_human`
- `mvp_agent`
- `workspace_continuity`
- `trace_and_evals`
- `search_controller`
- `release_safety`
- `background_runtime`
- `remote_supervision`
- `mission_control`
- `paper_benchmark_pack`
- `performance_recovery`
- `temporal_benchmark_pack`
- `benchmark_truth`
- `capability_academy`

## Minimum pass expectation by slice family

### Slice 12D family

- schema tests
- workspace lineage tests
- result contract rendering-parity tests
- governed learnings invalidation/reset tests
- human continuation tests
- external-agent continuation tests

### Slice 13 family

- search value tests
- stop-search tests
- add-data or new-dataset recommendation tests
- checkpoint or profile tests
- agent-consumable strategy tests

### Slice 13A through 13C family

- release-safety leak tests
- artifact-attestation tests
- event and permission parity tests
- background-job resume tests
- memory-maintenance queue tests
- hidden-activity regression guards

### Slice 15 family

- human mission-control tests
- agent mission-control tests
- demo-pack health checks
- onboarding-success tests
- workspace replay tests

### Slice 15G through 15L family

- objective-alignment tests
- split-degeneracy and metric-materialization tests
- family-eligibility and adapter-fallback tests
- staged-search and budget-profile separation tests
- temporal split-health and lagged-baseline tests
- calibration and operating-point optimization tests
- protocol-conformance and paper-claim-gate tests
- no-toy-budget regression guards

### Slice 16 family

- capability-card schema tests
- replay-pack tests
- shadow-mode non-authority tests
- arena-promotion tests
- hunt-budget and seeded-replay tests
- non-core specialist recruitment and retirement tests
- no-core-deletion guards
- human and agent explanation tests for promoted or retired capabilities

### Slice 17 family

- representation-slot fallback tests
- representation-uplift benchmark tests
- no-gain honesty tests
- benchmark separation tests between deterministic and representation-augmented modes

## Release gate

For a slice to be considered recruiter-demo-ready, it should have:

- green targeted tests for the slice
- green human-chaos tests for impacted flows
- green external-agent tests for impacted surfaces
- no newly introduced warnings unless explicitly justified

## Demo gate

For a feature to be shown in a flagship demo, it should have:

- one stable proof case
- one failure-mode case
- one recovery or fallback case

If it cannot survive that bar, it should not be presented as a polished demo capability.
