# Slice 15V - Raw graph and subgraph ingestion

## Status

Planned.

## Intent

Slice 15V moves Relaytic-AML beyond flattened graph snapshots for public AML graph workloads.

## Load-Bearing Improvement

- Relaytic-AML ingests Elliptic-style multi-file graph bundles and preserves node, edge, feature, time, and label provenance.

## Human Surface

- operators can see whether a graph workload was raw graph, flattened graph, or subgraph-packaged, and which claims that permits.

## Agent Surface

- external agents can consume graph-loader manifests and know which files, IDs, and transformations were used.

## Intelligence Source

- deterministic graph loaders
- graph provenance
- entity graph construction
- typology reasoning
- subgraph packaging

## Fallback Rule

- if raw graph files are incomplete, Relaytic falls back to flattened snapshot mode only when a valid flattened file is provided and downgrades graph claims.

## Required Outputs

- `aml_graph_loader_manifest.json`
- `aml_graph_provenance_report.json`
- `aml_subgraph_task_manifest.json`
- `aml_graph_claim_scope.json`

## Acceptance Criteria

1. One raw graph fixture loads into the existing graph/entity artifact path.
2. One incomplete graph bundle fails safely with a precise recovery instruction.
3. Flattened graph support remains compatible and honestly labeled.

## Required Verification

- raw graph loader unit tests
- incomplete bundle safety test
- flattened compatibility regression

