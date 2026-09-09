# Support Matrix

| SparkSQL construct | Status | DAX strategy | Notes |
|---|---:|---|---|
| `SELECT column FROM table` | Supported | `SELECTCOLUMNS` | Single-table only |
| `WHERE column = literal` | Supported | `FILTER` | Basic literals |
| `AND` / `OR` | Supported | Boolean DAX predicate | Parentheses emitted |
| `GROUP BY` | Supported | `SUMMARIZECOLUMNS` | Single table |
| `SUM`, `AVG`, `MIN`, `MAX` | Supported | Same-name DAX aggregators | Column args only |
| `COUNT(*)` | Supported | `COUNTROWS(table)` | Single table |
| `ORDER BY` | Supported | DAX `ORDER BY` or `TOPN` | Alias references use `[alias]` |
| `LIMIT` | Supported | `TOPN` | Best with explicit `ORDER BY` |
| `JOIN` | Not supported | N/A | Needs relationship metadata |
| CTEs | Not supported | N/A | Future phase |
| Subqueries | Not supported | N/A | Future phase |
| Window functions | Not supported | N/A | Not a v0.1 goal |
| `HAVING` | Not supported | N/A | Future filter-over-summary support |
