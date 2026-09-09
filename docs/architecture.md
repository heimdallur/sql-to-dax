# Architecture

The translator has three layers.

## 1. Parser

`sql_to_dax.parser` uses `sqlglot` with the Databricks dialect by default. This avoids hand-rolled SQL parsing.

## 2. Logical Model

`sql_to_dax.logical` contains small dataclasses representing the supported query subset. This keeps the DAX emitter independent from `sqlglot` internals.

## 3. DAX Emitter

`sql_to_dax.dax` emits deterministic DAX strings from the logical model.

## Why This Shape

Direct string rewriting is not safe. SQL and DAX differ in filter context, row context, relationships, blanks, and aggregation semantics. A logical model creates a hard boundary where unsupported semantics can be rejected.
