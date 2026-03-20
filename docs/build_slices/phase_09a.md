# Slice 09A - Run Memory and Analog Retrieval

## Implementation Status

Implemented in the current baseline.

The current Slice 09A delivery includes:

- `src/relaytic/memory/` as the canonical run-memory package boundary
- `relaytic memory retrieve` and `relaytic memory show`
- automatic memory enrichment inside planning, challenger design, completion review, lifecycle review, `relaytic run`, and `relaytic show`
- disk-first memory artifacts with explicit provenance, route/challenger counterfactuals, and reflection-memory flushes

## Intent

Slice 09A is where Relaytic stops behaving like each run lives in isolation.

This slice is successful only if Relaytic can retrieve prior runs and analog cases in a way that:

- improves current route choice
- improves challenger design
- improves completion judgment
- writes durable reflection memory back to disk before the run closes
- remains auditable and challengeable by current-run evidence

Memory is not allowed to become hidden authority.
It must stay explicit, provenance-bearing, and bounded.

## Weaknesses It Must Close

Without a dedicated memory slice, Relaytic still has these frontier-relevant weaknesses:

- route choice is too local to the current run
- challenger design lacks historical analog pressure
- completion can detect missing memory support but cannot yet resolve it
- prior successful or failed patterns are not yet reusable in a structured, inspectable way

Slice 09A must close those weaknesses without introducing opaque behavior drift.

## Planned Package Boundary

Slice 09A should introduce:

- `src/relaytic/memory/`

That package should own retrieval, scoring, provenance capture, and memory artifact persistence.

## Required Outputs

- `memory_retrieval.json`
- `analog_run_candidates.json`
- `route_prior_context.json`
- `challenger_prior_suggestions.json`
- `reflection_memory.json`
- `memory_flush_report.json`

## Required Inputs

Slice 09A must consume, at minimum:

- current run summary artifacts
- planning artifacts
- evidence artifacts
- completion artifacts when available
- prior run manifests and selected comparable artifacts

## Required Behavior

- memory must remain advisory, never silently binding
- on-disk Relaytic artifacts remain the canonical truth; any retrieval index must be derived and disposable
- every retrieved analog must include provenance and a retrieval rationale
- `analog_run_candidates.json` entries must at minimum expose `run_id`, `similarity_score`, `relevance_reason`, and `provenance`
- planning, challenger, and completion layers must be able to cite exactly what changed because memory was available
- weak or low-confidence retrieval must degrade cleanly into no-memory behavior
- memory must be able to help both humans and external agents understand why a prior run was considered relevant
- memory retrieval must not bypass the deterministic floor
- memory retrieval should prefer summaries, priors, lifecycle outcomes, and reflections over raw-row persistence whenever practical
- before completion or lifecycle finalization, Relaytic should be able to flush reflection memory and retrieval deltas to disk

## Planned Surface

Slice 09A should add at least:

- `relaytic memory retrieve`
- memory-aware enrichment in `relaytic show`

Memory-aware planning, evidence, and completion may also consume the new artifacts automatically when present.

## Acceptance Criteria

Slice 09A is acceptable only if:

1. Relaytic can retrieve a small set of prior analog runs with explicit provenance
2. at least one current-run recommendation changes because a retrieved analog was available
3. a human can see why the analog was retrieved
4. an external agent can consume the retrieval output without reading prose first

## Required Verification

Slice 09A should not be considered complete without targeted tests that cover at least:

- retrieval of analog runs with explicit provenance
- graceful fallback when no credible analogs exist
- one case where planning changes because memory was available
- one case where completion changes because memory was available
- one case where reflection memory is flushed before the run is considered complete for the current mode
