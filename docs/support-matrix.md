# Support Matrix

| SparkSQL construct | Status | DAX strategy | Test coverage | Notes |
|---|---:|---|---|---|
| `SELECT column FROM table` | Supported | `SELECTCOLUMNS` | `supported.toml` | Single-table only |
| Projection aliases | Supported | `SELECTCOLUMNS` label | API tests |  |
| `WHERE column = literal` | Supported | `FILTER` | `supported.toml` | Basic literals |
| `<>` / `!=` | Supported | `<>` | predicate tests |  |
| `<`, `<=`, `>`, `>=` | Supported | same operator | predicate tests |  |
| `IN (...)` | Supported | DAX `IN { ... }` | predicate tests | Literal lists only |
| `IS NULL` | Supported | `ISBLANK(column)` | predicate tests | DAX blank semantics apply |
| `IS NOT NULL` | Supported | `NOT ISBLANK(column)` | predicate tests | DAX blank semantics apply |
| `AND` / `OR` | Supported | Boolean DAX predicate | predicate tests | Parentheses emitted |
| `GROUP BY` | Supported | `SUMMARIZECOLUMNS` | `supported.toml` | Single table |
| `SUM`, `AVG`, `MIN`, `MAX` | Supported | same-name DAX aggregators | API tests | Column args only |
| `COUNT(*)` | Supported | `COUNTROWS(table)` | `supported.toml` | Single table |
| `ORDER BY` | Supported | DAX `ORDER BY` or `TOPN` | API tests | Alias references use `[alias]` |
| `LIMIT` | Supported | `TOPN` | API tests | Best with explicit `ORDER BY` |
| `JOIN` | Not supported | N/A | `unsupported.toml` | Needs relationship metadata |
| CTEs | Not supported | N/A | `unsupported.toml` | Future phase |
| Subqueries | Not supported | N/A | planned | Future phase |
| Window functions | Not supported | N/A | `unsupported.toml` | Not a v0.1 goal |
| `HAVING` | Not supported | N/A | `unsupported.toml` | Future filter-over-summary support |
