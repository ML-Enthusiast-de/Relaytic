# Slice 15V - Raw graph and subgraph ingestion

## Status

Planned.

## Intent

Slice 15V moves Relaytic-AML beyond flattened graph snapshots for public AML graph workloads.

This slice is the point where Relaytic starts being credible on graph AML benchmarks instead of only graph-flavored tabular snapshots.

## Load-Bearing Improvement

- Relaytic-AML ingests Elliptic-style multi-file graph bundles and preserves node, edge, feature, time, and label provenance.
- Relaytic-AML can represent subgraph-centric benchmark tasks, including Elliptic2-style subgraph labels, without pretending that a flattened node table is equivalent to a raw graph or subgraph workload.

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
- `aml_public_graph_benchmark_catalog.json`

## Acceptance Criteria

1. One raw graph fixture loads into the existing graph/entity artifact path.
2. One incomplete graph bundle fails safely with a precise recovery instruction.
3. Flattened graph support remains compatible and honestly labeled.
4. The graph benchmark catalog distinguishes flattened Elliptic-style support, raw Elliptic-style support, Elliptic2-style subgraph support, and AMLSim-style synthetic bank graph support.
5. Claim scope blocks raw graph, subgraph, or graph-SOTA claims unless the corresponding loader/provenance path is active and benchmarked.

## Required Verification

- raw graph loader unit tests
- incomplete bundle safety test
- flattened compatibility regression
- graph benchmark catalog regression
