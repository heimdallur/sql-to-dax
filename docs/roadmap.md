# Roadmap

## Phase 1: Conservative Single-Table Translation

Status: active.

- projections
- filters
- grouping
- basic aggregations
- ordering
- limits
- metadata-based name mapping

## Phase 2: Stronger Diagnostics and Explainability

- structured diagnostics
- CLI explain mode
- docs links for unsupported constructs

## Phase 3: Measure-Aware Translation

Translate SQL aggregations to existing DAX measures when metadata declares them.

## Phase 4: Relationship-Aware Joins

Only support joins when semantic model metadata defines relationships. Do not infer business semantics from SQL syntax alone.

## Phase 5: Semantic Model Interop

Investigate import from TMDL, TOM, Tabular Editor exports, or Power BI project structures.
