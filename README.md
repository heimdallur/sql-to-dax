# sql-to-dax

`sql-to-dax` is a conservative Python translator for a documented subset of Databricks SparkSQL analytical queries into DAX query expressions.

It is designed for correctness over breadth. Unsupported SQL fails with stable diagnostic codes rather than emitting plausible but wrong DAX.

## Status

Alpha. The package currently targets single-table analytical query patterns. It is not a general SQL-to-DAX compiler.

## Supported in v0.1

- `SELECT column FROM table`
- `WHERE` with basic column/literal predicates
- `AND` / `OR`
- `GROUP BY`
- `SUM`, `AVG`, `MIN`, `MAX`, `COUNT(*)`
- `ORDER BY`
- `LIMIT`
- Optional metadata mapping for DAX table and column names

See [`docs/support-matrix.md`](docs/support-matrix.md) for details.

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
from sql_to_dax import translate

sql = """
SELECT region, SUM(revenue) AS total_revenue
FROM sales
WHERE year = 2026
GROUP BY region
ORDER BY total_revenue DESC
LIMIT 10
"""

print(translate(sql))
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

## Design Principles

- Prefer explicit refusal over incorrect output.
- Keep dependencies minimal and credible.
- Treat SQL parsing, logical normalization, and DAX emission as separate concerns.
- Make every supported construct executable through tests and golden cases.

## Development Quality Gates

```bash
python -m ruff check .
python -m mypy src
python -m pytest --cov=sql_to_dax --cov-report=term-missing
python -m build
```

## License

MIT. See [`LICENSE`](LICENSE).
