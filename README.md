# sql-to-dax

`sql-to-dax` translates a documented subset of Databricks SparkSQL analytical queries into DAX query expressions.

The project favours correctness over breadth. Unsupported or semantically unsafe SQL fails with stable diagnostics rather than emitting plausible but wrong DAX.

## Status

Alpha. The package targets single-table analytical query patterns. It is not a general SQL-to-DAX compiler.

## Supported in v0.1

- `SELECT column FROM table`
- aliased projections
- `WHERE` with column/literal predicates
- `=`, `<>`, `<`, `<=`, `>`, `>=`, `IN`, `IS NULL`, `IS NOT NULL`
- `AND` / `OR` with deterministic parentheses
- `GROUP BY`
- `SUM`, `AVG`, `MIN`, `MAX`, `COUNT(*)`
- `ORDER BY`
- `LIMIT` via `TOPN`
- optional TOML metadata mapping for DAX table and column names

See [`docs/support-matrix.md`](docs/support-matrix.md).

## Install

```bash
pip install sql-to-dax
```

For local development:

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install -e '.[dev]'
```

## Python API

```python
from sql_to_dax import explain, translate

sql = """
SELECT region, SUM(revenue) AS total_revenue
FROM sales
WHERE year = 2026
GROUP BY region
ORDER BY total_revenue DESC
LIMIT 10
"""

print(translate(sql))
print(explain(sql).supported)
```

Output:

```dax
EVALUATE
TOPN(10, SUMMARIZECOLUMNS('sales'[region], FILTER('sales', 'sales'[year] = 2026), "total_revenue", SUM('sales'[revenue])), [total_revenue], DESC)
```

## CLI

```bash
sql-to-dax query.sql
sql-to-dax - < query.sql
python -m sql_to_dax query.sql
```

With metadata:

```bash
sql-to-dax query.sql --metadata examples/model.toml
```

## Metadata

Metadata maps source SQL identifiers to semantic-model DAX identifiers.

```toml
[tables.sales]
name = "Sales"

[tables.sales.columns]
region = "Region"
revenue = "Revenue"
```

## Documentation

- [Architecture](docs/architecture.md)
- [Support matrix](docs/support-matrix.md)
- [Examples](docs/examples.md)
- [Semantic model metadata](docs/semantic-model.md)
- [Roadmap](docs/roadmap.md)
- [Adding SQL constructs](docs/contributor-guide/adding-sql-constructs.md)

## Development Quality Gates

```bash
python -m ruff check .
python -m mypy src
python -m pytest --cov=sql_to_dax --cov-report=term-missing
python -m build
```

## Dependency Policy

Runtime dependency surface is deliberately small. `sqlglot` is used for SQL parsing. The CLI, metadata loader, and data model use the Python standard library.

## License

MIT. See [`LICENSE`](LICENSE).
