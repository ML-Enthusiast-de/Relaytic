# Slice 15O - Entity, graph, and typology reasoning

## Status

Planned.

## Intent

Slice 15O turns Relaytic-AML from row-only transaction scoring into a system that can reason about entities, communities, paths, and suspicious structures.

## Load-Bearing Improvement

- Relaytic-AML should be able to build entity and transaction graphs, score suspicious neighborhoods and candidate subgraphs, and preserve typology-level evidence instead of only row-level classifier outputs

## Human Surface

- operators should be able to inspect suspicious entities, expanded neighborhoods, typology hits, and why a case is structurally suspicious

## Agent Surface

- external agents should be able to query entity-graph profiles, typology hits, and subgraph risk reports without scraping prose

## Intelligence Source

- deterministic graph construction
- deterministic typology templates
- optional graph-learning adapters behind explicit contracts
- replay- and shadow-first treatment of heavier graph models

## Intended Artifacts

- `entity_graph_profile.json`
- `counterparty_network_report.json`
- `typology_detection_report.json`
- `subgraph_risk_report.json`
- `entity_case_expansion.json`

## Acceptance Criteria

1. one AML benchmark or demo task produces both row-level and graph-level evidence
2. one typology detector contributes to a case packet visibly
3. one heavier graph candidate can lose honestly to a simpler structural baseline

## Required Verification

- one graph-construction test
- one typology-detection regression test
- one case-packet graph-evidence test
